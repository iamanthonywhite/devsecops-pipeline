# ─────────────────────────────────────────────────────────────
# DevSecOps Demo — Dockerfile
# Multi-stage build: keeps the final image lean and secure
# ─────────────────────────────────────────────────────────────

# Stage 1: Build dependencies
FROM python:3.11-slim AS builder

WORKDIR /build

COPY app/requirements.txt .

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt --target=/build/deps


# Stage 2: Runtime image
FROM python:3.11-slim AS runtime

# Security: run as non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /build/deps /usr/local/lib/python3.11/site-packages/

# Copy application code
COPY app/ .

# Switch to non-root user
USER appuser

EXPOSE 8000

# Secrets injected at runtime via environment variables (from Vault)
# Never hardcode DB_PASSWORD or API_KEY here
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
