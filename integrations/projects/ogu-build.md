# OGU Builds (TURMO + Universal Driver)

**Role**: builds · **Path**: `../ogu-build`

Prebuilt artifacts: TURMO (display driver suite with .exe/.dll) and
universal driver builds.

## Integration surface

| Surface | Purpose |
|---|---|
| `src/turmo/TURMO/` | TURMO binaries + date/time/data modules |
| `src/universal_driver/` | Universal driver build |

## Wiring into SOVEREIGN

- Reference artifacts for the distribution pipeline's binary channels.
- `builds/` pipelines mirror the same signing/checksum discipline.
