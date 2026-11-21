const API_URL = 'http://localhost:8000/chat/stream';

const form = document.getElementById('chat-form');
const input = document.getElementById('message-input');
const sendBtn = document.getElementById('send-btn');
const messagesEl = document.getElementById('messages-container');
const feedEl = document.getElementById('workflow-feed');
const badgeEl = document.getElementById('workflow-badge');

const WELCOME_HTML = messagesEl.innerHTML;
const EMPTY_HTML = feedEl.innerHTML;

// ---------- utilidades de UI ----------

function el(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}

function scrollToBottom(container) {
  container.scrollTop = container.scrollHeight;
}

function addMessage(role, text) {
  const wrapper = el('div', `message ${role}`);
  const bubble = el('div', 'bubble');
  bubble.textContent = text;
  wrapper.appendChild(bubble);
  messagesEl.appendChild(wrapper);
  scrollToBottom(messagesEl);
}

function setBadge(state, label) {
  badgeEl.className = `badge ${state}`;
  badgeEl.textContent = label;
}

function formatTime(ts) {
  const d = ts ? new Date(ts) : new Date();
  return d.toLocaleTimeString('pt-BR', { hour12: false });
}

/** Adiciona SEMPRE um novo item ao final da timeline (nunca atualiza um existente). */
function addWorkflowItem({ kind, icon, title, desc, detail, ts }) {
  if (feedEl.querySelector('.empty-state')) feedEl.innerHTML = '';

  const item = el('div', `wf-item ${kind}`);
  item.appendChild(el('div', 'wf-icon-col', icon));

  const content = el('div', 'wf-content');
  const header = el('div', 'wf-item-header');
  header.appendChild(el('span', 'wf-item-title', title));
  header.appendChild(el('span', 'wf-item-time', formatTime(ts)));
  content.appendChild(header);

  if (desc) content.appendChild(el('div', 'wf-item-desc', desc));
  if (detail) content.appendChild(el('div', 'wf-item-detail', detail));

  item.appendChild(content);
  feedEl.appendChild(item);
  scrollToBottom(feedEl.parentElement);
}

// ---------- tradução de eventos SSE em itens da timeline ----------

const NODE_KIND = {
  planner: 'planner',
  executor: 'executor',
  synthesis_node: 'synthesis',
  critic: 'critic',
  replanner: 'replan',
  recusa: 'failed',
};

const ERROR_KIND_LABEL = {
  timeout: 'tempo esgotado',
  permission: 'sem permissão',
  invalid_query: 'consulta inválida',
  syntax: 'erro de sintaxe/estrutura',
  no_documents: 'nenhum documento relevante',
  unknown: 'erro desconhecido',
};

function describeProgress(d) {
  const origem = d.action === 'SQL' ? 'SQL' : 'RAG';
  const tentativa = d.attempt ? ` (tentativa ${d.attempt})` : '';
  switch (d.stage) {
    case 'generate_sql':
      return { title: `Passo ${d.step_id} · Gerando consulta`, desc: `Agente SQL elaborando a consulta${tentativa}.` };
    case 'execute_sql':
      return d.ok
        ? { title: `Passo ${d.step_id} · Consulta executada`, desc: `${d.row_count} registro(s) retornado(s)${tentativa}.` }
        : { title: `Passo ${d.step_id} · Consulta falhou`, desc: `Motivo: ${ERROR_KIND_LABEL[d.error_kind] || d.error_kind}${tentativa}.` };
    case 'analyze_query':
      return { title: `Passo ${d.step_id} · Analisando pergunta`, desc: 'Agente RAG interpretando a busca.' };
    case 'retrieve':
      return { title: `Passo ${d.step_id} · Documentos recuperados`, desc: `${d.doc_count} documento(s) encontrado(s)${tentativa}.` };
    case 'grade':
      return { title: `Passo ${d.step_id} · Avaliando relevância`, desc: d.is_relevant ? 'Documentos considerados relevantes.' : 'Documentos insuficientes.' };
    case 'rewrite':
      return { title: `Passo ${d.step_id} · Reescrevendo busca`, desc: `Refazendo a busca com nova consulta${tentativa}.` };
    default:
      return { title: `Passo ${d.step_id} · ${origem}`, desc: d.stage };
  }
}

function handleWorkflowEvent(name, d) {
  const ts = d.ts;
  switch (name) {
    case 'start':
      setBadge('running', 'Em execução');
      addWorkflowItem({ kind: 'start', icon: '▶', title: 'Requisição recebida', desc: 'Iniciando o workflow.', ts });
      break;

    case 'node_start': {
      const extra = d.step_id ? ` — passo ${d.step_id} (${d.action})` : '';
      addWorkflowItem({ kind: NODE_KIND[d.node] || 'executor', icon: '⏳', title: d.label + extra, ts });
      break;
    }

    case 'node_end': {
      let desc = '';
      let detail = '';
      const s = d.summary || {};
      if (s.steps) {
        desc = s.out_of_scope ? 'Pergunta fora do escopo.' : `${s.steps.length} passo(s) planejado(s).`;
        detail = s.steps.map((st) => `${st.id}. ${st.action}`).join('  →  ');
      } else if (d.node === 'executor') {
        desc = `Concluídos: [${(s.completed_steps || []).join(', ')}] · Falhas: [${(s.failed_steps || []).join(', ')}]`;
      }
      addWorkflowItem({ kind: NODE_KIND[d.node] || 'executor', icon: '✔', title: `${d.label} — concluído`, desc, detail, ts });
      break;
    }

    case 'node_error':
      addWorkflowItem({ kind: 'failed', icon: '✖', title: `Erro em ${d.node}`, desc: d.message, ts });
      break;

    case 'step_progress': {
      const { title, desc } = describeProgress(d);
      addWorkflowItem({ kind: 'executor', icon: d.action === 'SQL' ? '🗄' : '📚', title, desc, ts });
      break;
    }

    case 'step_failed':
      addWorkflowItem({
        kind: 'failed', icon: '⚠',
        title: `Passo ${d.step_id} falhou (${d.action})`,
        desc: d.message,
        detail: `causa: ${ERROR_KIND_LABEL[d.error_kind] || d.error_kind}`,
        ts,
      });
      break;

    case 'replan':
      addWorkflowItem({
        kind: 'replan', icon: '🔄',
        title: `Replanejamento #${d.attempt}`,
        desc: d.origin === 'critic' ? 'Solicitado pelo critic.' : 'Motivado por falha na execução.',
        detail: d.reason,
        ts,
      });
      break;

    case 'critic':
      addWorkflowItem({
        kind: d.passed ? 'critic' : 'failed',
        icon: d.passed ? '✅' : '❌',
        title: d.passed ? 'Resposta aprovada' : 'Resposta reprovada',
        desc: d.passed ? 'A resposta é fundamentada e completa.' : 'O critic pediu ajustes.',
        detail: d.feedback || '',
        ts,
      });
      break;

    case 'limit_reached':
      addWorkflowItem({ kind: 'failed', icon: '⛔', title: 'Limite de tentativas atingido', desc: d.message, ts });
      break;

    case 'answer':
      addWorkflowItem({ kind: 'answer', icon: '💬', title: 'Resposta final pronta', ts });
      addMessage('assistant', d.answer);
      break;

    case 'error':
      setBadge('failed', 'Erro');
      addWorkflowItem({ kind: 'failed', icon: '✖', title: 'Erro no processamento', desc: d.message, ts });
      addMessage('assistant', `⚠️ ${d.message}`);
      break;

    case 'done':
      if (badgeEl.classList.contains('running')) setBadge('completed', 'Concluído');
      break;
  }
}

// ---------- parser de SSE sobre fetch ----------

function parseSSEBlock(block) {
  let event = 'message';
  const dataLines = [];
  for (const line of block.split('\n')) {
    if (line.startsWith('event:')) event = line.slice(6).trim();
    else if (line.startsWith('data:')) dataLines.push(line.slice(5).trim());
  }
  if (!dataLines.length) return null;
  try {
    return { event, data: JSON.parse(dataLines.join('\n')) };
  } catch {
    return null;
  }
}

async function streamChat(message) {
  const response = await fetch(API_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ input: message }),
  });
  if (!response.ok || !response.body) throw new Error(`HTTP ${response.status}`);

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true }).replace(/\r\n/g, '\n');

    let idx;
    while ((idx = buffer.indexOf('\n\n')) !== -1) {
      const parsed = parseSSEBlock(buffer.slice(0, idx));
      buffer = buffer.slice(idx + 2);
      if (parsed) handleWorkflowEvent(parsed.event, parsed.data);
    }
  }
}

// ---------- interações ----------

let busy = false;

async function sendMessage() {
  const text = input.value.trim();
  if (!text || busy) return;

  busy = true;
  sendBtn.disabled = true;
  input.value = '';
  input.style.height = 'auto';

  addMessage('user', text);
  feedEl.innerHTML = '';
  setBadge('running', 'Em execução');

  try {
    await streamChat(text);
  } catch (err) {
    setBadge('failed', 'Erro');
    addWorkflowItem({ kind: 'failed', icon: '✖', title: 'Falha de conexão', desc: err.message });
    addMessage('assistant', '⚠️ Não foi possível conectar ao backend.');
  } finally {
    busy = false;
    sendBtn.disabled = false;
    input.focus();
  }
}

form.addEventListener('submit', (e) => {
  e.preventDefault();
  sendMessage();
});

input.addEventListener('keydown', (e) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
});

input.addEventListener('input', () => {
  input.style.height = 'auto';
  input.style.height = `${Math.min(input.scrollHeight, 140)}px`;
});

document.getElementById('clear-chat-btn').addEventListener('click', () => {
  messagesEl.innerHTML = WELCOME_HTML;
});

document.getElementById('clear-workflow-btn').addEventListener('click', () => {
  feedEl.innerHTML = EMPTY_HTML;
  setBadge('idle', 'Aguardando');
});
