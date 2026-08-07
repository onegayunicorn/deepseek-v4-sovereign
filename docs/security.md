# SOVEREIGN — Security Model

Sovereignty = you can prove what happened, and nothing leaves without your
say-so.

## Layers

| Layer | Mechanism | Location |
|---|---|---|
| At rest | AES-256-GCM (PBKDF2-derived or base64 key) | `security/encryption.py` |
| Keys | file/env/vault keyring; encrypted at rest | `security/keyring.py` |
| AuthN | JWT HS256 (stdlib impl) or OAuth2 | `security/authentication.py` |
| AuthZ | RBAC roles + tool permissions | `governance/permissions.py` |
| Policy | declarative policy engine (no-leak, tool allow-lists) | `governance/policies.py` |
| Execution | sandboxed shell (allow-list + rlimits), code interpreter import-block | `security/sandbox.py`, `tools/builtin/` |
| Audit | tamper-evident hash-chained JSONL | `governance/audit_logger.py` |
| Transit | TLS/mTLS config helper | `security/ssl.py` |
| Secrets | redaction in logs (api_key/token/password/...) | `utils/logging.py` |

## Threats & mitigations

| Threat | Mitigation |
|---|---|
| Prompt injection via tools | Tool allow-lists + policy engine + ethics guardrails |
| Secret exfiltration | api_client allow-list, log redaction, sandbox network rules |
| Tampered audit trail | prev_hash chaining; detect by recomputing hashes |
| Tool abuse | RBAC tool permissions; shell command allow/block lists |
| Model data leakage | no_external_egress policy; sovereign defaults (local only) |

## Hardening checklist

- [ ] Set `JWT_SECRET` (≥32 chars) and `AES_KEY_B64` (32-byte key) in `.env`
- [ ] Enable `AuthMiddleware` in `api/middleware.py` for non-local deployments
- [ ] Wire TLS (`security/ssl.py`) behind nginx or uvicorn ssl options
- [ ] Configure webhook HMAC secrets per source (`webhooks/`)
- [ ] Run `scripts/healthcheck.sh` + compliance endpoint in CI
- [ ] Rotate keys via keyring (`security/keyring.py`)

## Secrets

Never commit `.env` or `data/state/keyring.json`. Use the keyring or a Vault
backend (extension point in `security/secrets.py`).
