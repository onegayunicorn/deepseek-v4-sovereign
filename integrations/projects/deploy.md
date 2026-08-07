# Deploy (Infra)

**Role**: infra · **Path**: `../deploy`

Infrastructure for the OGU stack: Docker, nginx, systemd service.

## Integration surface

| Surface | Purpose |
|---|---|
| `Dockerfile` / `Dockerfile.kaleidoscope` | Container images |
| `docker-compose.yml` | Compose stack |
| `nginx.conf` | Reverse proxy config |
| `qlb.service` | systemd unit |
| `entrypoint.sh` | Container entrypoint |

## Wiring into SOVEREIGN

- SOVEREIGN's `docker/` stack mirrors this layout with sovereign services.
- `operations/deploy.yaml` supports docker / k8s / local deployment.
