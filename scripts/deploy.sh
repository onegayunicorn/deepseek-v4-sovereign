#!/usr/bin/env bash
# SOVEREIGN — deploy orchestrator (local | docker | kubernetes)
# Usage: bash scripts/deploy.sh [local|docker|kubernetes]
set -euo pipefail
cd "$(dirname "$0")/.."

TARGET="${1:-docker}"

case "$TARGET" in
  local)
    bash scripts/start.sh
    ;;
  docker)
    docker compose -f docker/docker-compose.yml build
    docker compose -f docker/docker-compose.yml up -d
    echo "[deploy] docker stack up — http://localhost:8000"
    ;;
  kubernetes)
    kubectl apply -f kubernetes/configmap.yaml
    kubectl apply -f kubernetes/secrets.yaml
    kubectl apply -f kubernetes/deployment.yaml
    kubectl apply -f kubernetes/service.yaml
    kubectl apply -f kubernetes/ingress.yaml
    kubectl apply -f kubernetes/hpa.yaml
    echo "[deploy] kubernetes applied"
    ;;
  *) echo "unknown target: $TARGET (local|docker|kubernetes)" >&2; exit 2 ;;
esac
