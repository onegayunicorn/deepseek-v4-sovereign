# SOVEREIGN — Deployment Guide

## Option A — Local (development)

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m sovereign.main dashboard          # http://localhost:8000
```

## Option B — Docker

```bash
docker compose -f docker/docker-compose.yml up -d
# services: api (8000), optional redis/vector via compose profiles
```

## Option C — Kubernetes

```bash
kubectl apply -f kubernetes/configmap.yaml
kubectl apply -f kubernetes/secrets.yaml
kubectl apply -f kubernetes/deployment.yaml
kubectl apply -f kubernetes/service.yaml
kubectl apply -f kubernetes/ingress.yaml
kubectl apply -f kubernetes/hpa.yaml
```

## Option D — Desktop / Mobile (product distribution)

```bash
bash builds/apk/build_apk.sh                # Android APK
bash builds/exe/build_exe.sh                # Windows EXE (run on Windows)
bash distribution/release_pipeline.sh       # full release
```

## Environment

Copy `.env.example` → `.env` and set:

| Variable | Required | Notes |
|---|---|---|
| `HF_TOKEN` | optional | DeepSeek router inference / HF Spaces deploy |
| `JWT_SECRET` | production | API auth |
| `AES_KEY_B64` | production | keyring encryption (32-byte base64) |
| `GITHUB_TOKEN` | scout agent | Expanded Intelligence integration |

## Verification

```bash
curl -s localhost:8000/health
bash scripts/healthcheck.sh
python3 integrations/connector.py
```
