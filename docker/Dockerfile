# SOVEREIGN — production image
FROM python:3.11-slim AS base

ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY pyproject.toml ./
COPY src ./src
RUN pip install --no-cache-dir -e .

COPY config ./config
COPY agents triggers tasks actions modules routines operations webhooks jobs ./definitions/
COPY models ./models
COPY buckets ./buckets
COPY hardware ./hardware
COPY integrations ./integrations

RUN mkdir -p data/state data/memory data/artifacts logs/audits

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD curl -sf http://localhost:8000/health || exit 1

ENTRYPOINT ["python", "-m", "sovereign.main", "dashboard"]
