# ── Stage 1: Frontend Build ────────────────────────────────────────────────────
FROM node:20-alpine AS frontend-build
WORKDIR /frontend

COPY frontend/package*.json ./
RUN npm ci --prefer-offline

COPY frontend/ ./
RUN npm run build


# ── Stage 2: Backend Build + FAISS Index ──────────────────────────────────────
FROM python:3.11-slim AS backend-build
WORKDIR /app

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install production deps from pyproject.toml without installing the package itself.
# Python 3.11 includes tomllib as stdlib — no extra tooling needed.
COPY backend/pyproject.toml ./
RUN python3 -c "\
import tomllib; \
deps = tomllib.load(open('pyproject.toml', 'rb'))['project']['dependencies']; \
open('requirements.txt', 'w').write('\n'.join(deps))" && \
    pip install --no-cache-dir -r requirements.txt

# Copy backend source and knowledge base
COPY backend/app/ ./app/
COPY backend/data/ ./data/

# Bake FAISS index into image at build time — eliminates cold-start embedding delay
RUN python -m app.rag.index_builder

# Copy React build from Stage 1 → served as static files by FastAPI
COPY --from=frontend-build /frontend/dist ./app/static/


# ── Stage 3: Runtime ──────────────────────────────────────────────────────────
FROM python:3.11-slim AS runtime
WORKDIR /app

# Minimal attack surface: non-root user
RUN useradd --create-home --no-log-init --shell /bin/bash appuser

COPY --from=backend-build /opt/venv /opt/venv
COPY --from=backend-build /app /app

RUN chown -R appuser:appuser /app
USER appuser

ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

EXPOSE 8080

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080", \
     "--workers", "1", "--log-level", "warning"]
