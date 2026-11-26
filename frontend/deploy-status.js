/*
 * Lógica pura (sem DOM) da página de espera: transforma a resposta da API do
 * GitHub Actions em fases, progresso e estado da página.
 *
 * CONTRATO com .github/workflows/deploy.yml: STEP_TO_PHASE usa os NOMES EXATOS
 * dos steps do workflow. Se um step for renomeado lá, atualize o mapa aqui
 * (um step desconhecido não quebra a página, só aparece com o nome cru).
 */
(function (root, factory) {
  const api = factory();
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else root.DeployStatus = api;
})(typeof self !== 'undefined' ? self : this, function () {
  'use strict';

  const TEST_JOB_NAME = 'Run Unit Tests';
  const FAIL = ['failure', 'cancelled', 'timed_out', 'startup_failure'];
  const STALE_MS = 30 * 60 * 1000; // run mais velho que isso não conta como "recente"
  const GRACE_MS = 5 * 60 * 1000; // tempo para o gateway responder após o deploy concluir

  // Steps do runner que não dizem nada ao visitante.
  const INFRA_STEPS = new Set([
    'Set up job',
    'Complete job',
    'Checkout repository',
    'Summary',
  ]);

  const STEP_TO_PHASE = {
    'Configure AWS credentials': 'aws',
    'Validate ECS configuration': 'aws',
    'Login to Amazon ECR': 'build',
    'Build & Push Image to ECR': 'build',
    'Stop Previous ECS Tasks': 'task',
    'Start ECS Fargate Task': 'task',
    'Wait for Task & Extract Public IP': 'network',
    'Update API Gateway Target': 'gateway',
    'External Smoke Test': 'verify',
  };

  // weight = segundos estimados por fase no deploy via ECS Fargate
  const PHASES = [
    { id: 'tests', label: 'Testes automatizados', weight: 15 },
    { id: 'aws', label: 'Autenticando na AWS', weight: 5 },
    { id: 'build', label: 'Construindo e publicando imagem no ECR', weight: 55 },
    { id: 'task', label: 'Iniciando container no ECS Fargate', weight: 10 },
    { id: 'network', label: 'Aguardando container e obtendo IP público', weight: 25 },
    { id: 'gateway', label: 'Conectando o API Gateway', weight: 3 },
    { id: 'verify', label: 'Verificação final de saúde', weight: 15 },
  ];

  function isInfraStep(name) {
    return INFRA_STEPS.has(name) || name.startsWith('Post ');
  }

  function phaseForStep(jobName, stepName) {
    if (isInfraStep(stepName)) return null;
    if (jobName === TEST_JOB_NAME) return 'tests';
    return STEP_TO_PHASE[stepName] || null;
  }

  function phaseStatus(steps) {
    if (!steps.length) return 'pending';
    if (steps.some((s) => FAIL.includes(s.conclusion))) return 'failed';
    if (steps.every((s) => s.conclusion === 'skipped')) return 'skipped';
    if (steps.every((s) => s.status === 'completed' && (s.conclusion === 'success' || s.conclusion === 'skipped'))) {
      return 'done';
    }
    if (steps.some((s) => s.status === 'in_progress' || s.status === 'completed')) return 'running';
    return 'pending';
  }

  function buildPhases(jobs) {
    const byPhase = {};
    for (const job of jobs || []) {
      if (job.name === TEST_JOB_NAME && job.conclusion === 'skipped' && !(job.steps && job.steps.length)) {
        (byPhase.tests ||= []).push({ status: 'completed', conclusion: 'skipped' });
        continue;
      }
      for (const step of job.steps || []) {
        const id = phaseForStep(job.name, step.name);
        if (!id) continue;
        (byPhase[id] ||= []).push(step);
      }
    }
    return PHASES.map((p) => ({ ...p, status: phaseStatus(byPhase[p.id] || []) }));
  }

  // Fase concluída conta o peso inteiro, em execução conta metade. Fases puladas ficam fora
  // do denominador. Teto de 99: 100% só quando o /health responde.
  function computeProgress(phases) {
    const active = phases.filter((p) => p.status !== 'skipped');
    const total = active.reduce((n, p) => n + p.weight, 0);
    if (total === 0) return 0;
    let done = 0;
    for (const p of active) {
      if (p.status === 'done') done += p.weight;
      else if (p.status === 'running') done += p.weight / 2;
    }
    return Math.min(99, Math.floor((done / total) * 100));
  }

  function describeCurrent(jobs, phases) {
    const running = phases.find((p) => p.status === 'running');
    if (running) return running.label;
    for (const job of jobs || []) {
      for (const s of job.steps || []) {
        if (s.status === 'in_progress' && !isInfraStep(s.name)) return s.name;
      }
    }
    return null;
  }

  // O run da listagem pode estar defasado; os jobs são mais frescos.
  function deriveRun(run, jobs) {
    if (!run || !jobs || !jobs.length) return run;
    const bad = jobs.find((j) => j.status === 'completed' && FAIL.includes(j.conclusion));
    const allDone = jobs.every((j) => j.status === 'completed');
    if (bad || allDone) {
      const times = jobs.map((j) => Date.parse(j.completed_at)).filter(Number.isFinite);
      const finished = times.length ? new Date(Math.max(...times)).toISOString() : run.updated_at;
      return { ...run, status: 'completed', conclusion: bad ? bad.conclusion : 'success', updated_at: finished };
    }
    const started = jobs.some((j) => j.status === 'in_progress');
    return { ...run, status: started ? 'in_progress' : run.status };
  }

  function isDeployRun(run) {
    return /deploy\.yml$/.test((run && run.path) || '');
  }

  // Runs vêm do mais novo para o mais antigo; só importam deploy e destroy.
  function pickRelevantRun(runs) {
    return (runs || []).find((r) => /(deploy|destroy)\.yml$/.test(r.path || '')) || null;
  }

  // run: undefined = ainda não consultado, null = nenhum run relevante.
  function resolveState({ health, run, now, degraded }) {
    if (health) return 'READY';
    if (degraded) return 'DEGRADED';
    if (run === undefined) return 'CHECKING';
    if (run === null || !isDeployRun(run)) return 'IDLE';

    if (run.status !== 'completed') {
      return now - Date.parse(run.created_at) < STALE_MS ? 'DEPLOYING' : 'IDLE';
    }
    const age = now - Date.parse(run.updated_at || run.created_at);
    if (FAIL.includes(run.conclusion)) return age < STALE_MS ? 'FAILED' : 'IDLE';
    if (run.conclusion === 'success') return age < GRACE_MS ? 'PROPAGATING' : 'IDLE';
    return 'IDLE';
  }

  function parseRateLimit(getHeader) {
    const remaining = Number(getHeader('x-ratelimit-remaining'));
    const reset = Number(getHeader('x-ratelimit-reset'));
    return {
      remaining: Number.isFinite(remaining) && getHeader('x-ratelimit-remaining') !== null ? remaining : null,
      resetAt: Number.isFinite(reset) && reset > 0 ? reset * 1000 : null,
    };
  }

  return {
    PHASES,
    STEP_TO_PHASE,
    buildPhases,
    computeProgress,
    describeCurrent,
    deriveRun,
    isDeployRun,
    pickRelevantRun,
    resolveState,
    parseRateLimit,
  };
});
