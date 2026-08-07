# Universal Driver

**Role**: drivers · **Path**: `../universal-driver`

Multi-platform device driver monorepo (pnpm workspaces + Turborepo).

## Integration surface

| Surface | Purpose |
|---|---|
| `packages/` | Driver packages |
| `docs/` | Driver documentation |
| `turbo.json`, `pnpm-workspace.yaml` | Build orchestration |
| `tsconfig.json` | TypeScript config |

## Wiring into SOVEREIGN

- Source of cross-platform device driver patterns for the BCI module.
- `ogu-build/src/universal_driver` carries built driver artifacts.
- Distribution pipeline can publish driver packages to npm
  (`distribution/release_channels.yaml`).
