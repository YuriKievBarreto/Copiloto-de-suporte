# Estágio 1: Builder
FROM python:3.13-slim AS builder

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/

COPY pyproject.toml uv.lock ./

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --compile-bytecode

# Estágio 2: Runtime Final
FROM python:3.13-slim

WORKDIR /app

ENV PATH="/app/.venv/bin:$PATH"

COPY --from=builder /app/.venv /app/.venv
COPY app ./app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
