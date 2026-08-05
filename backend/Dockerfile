# Multi-stage production Dockerfile for FinSight AI
# Stage 1: build stage (install build-time deps if needed)
FROM python:3.11-slim AS builder

ENV APP_HOME=/app
WORKDIR ${APP_HOME}

# Install build deps
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential \
       gcc \
       g++ \
       curl \
       ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install into a wheelhouse
COPY backend/requirements.txt ./
RUN python -m pip install --upgrade pip setuptools wheel \
    && pip download --no-deps --dest /wheels -r requirements.txt

# Stage 2: runtime
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    APP_HOME=/app \
    PORT=8501

WORKDIR ${APP_HOME}

# Install runtime dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       curl \
       ca-certificates \
       tini \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd --gid 1000 appuser \
    && useradd --uid 1000 --gid appuser --create-home --shell /bin/bash appuser

# Copy wheelhouse from builder and install
COPY --from=builder /wheels /wheels
RUN python -m pip install --no-cache-dir /wheels/* || true \
    && python -m pip install --upgrade pip setuptools wheel

# Copy application code and backend packages
COPY app.py ${APP_HOME}/app.py
COPY pages ${APP_HOME}/pages
COPY frontend ${APP_HOME}/frontend
COPY backend/config.py ${APP_HOME}/backend/config.py
COPY backend/app_health.py ${APP_HOME}/backend/app_health.py
COPY backend/utils ${APP_HOME}/backend/utils
COPY backend/start.sh ${APP_HOME}/backend/start.sh

# Ensure startup script is executable and data dirs are present
RUN chmod +x ${APP_HOME}/backend/start.sh \
    && mkdir -p ${APP_HOME}/data ${APP_HOME}/logs \
    && chown -R appuser:appuser ${APP_HOME}

# Switch to non-root
USER appuser

EXPOSE ${PORT}

ENV STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_SERVER_ENABLECORS=false \
    STREAMLIT_SERVER_PORT=${PORT} \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
    PYTHONPATH=${APP_HOME}

# Use tini as PID 1 to manage subprocesses
ENTRYPOINT ["/usr/bin/tini", "--"]

# Start script will run both uvicorn health server (localhost:8000) and streamlit (0.0.0.0:8501)
CMD ["bash", "backend/start.sh"]
