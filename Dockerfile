# ── Stage 1: Builder ─────────────────────────────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /app

# Install build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies into a prefix so we can copy them cleanly
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ── Stage 2: Runtime ─────────────────────────────────────────────────────────
FROM python:3.11-slim AS runtime

WORKDIR /app

# Copy only the installed packages from builder (no build tools in final image)
COPY --from=builder /install /usr/local

# Copy application source
COPY . .

# Create data directory for SQLite and ensure it's writable
RUN mkdir -p /app/data && chmod 777 /app/data

# Expose FastAPI port
EXPOSE 8000

# Health check — hits the FastAPI docs endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD sh -c "curl -f http://localhost:\${PORT:-8000}/docs || exit 1"

# Run the FastAPI server (uses $PORT provided by Railway/Render/Cloud Run, defaults to 8000)
CMD ["sh", "-c", "uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 2"]
