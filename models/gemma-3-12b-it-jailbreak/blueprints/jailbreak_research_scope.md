# Jailbreak Research Scope — gemma-3-12b-it-jailbreak

Purpose of this module's instrumentation, stated explicitly:

## In scope (defensive / audit)
- **Detection**: flag prompts containing jailbreak-indicator phrases for
  audit logging (`hooks/on_inference.py`, `triggers/on_inference_complete.yaml`).
- **Measurement**: benchmark quant variants for throughput/latency/fidelity
  (`tasks/benchmark.py`).
- **Red-team harness**: evaluate refusal/alignment behavior of the model under
  controlled, authorized conditions.
- **Hardware fit**: select the best quant for the target machine.

## Out of scope (this repository)
- Generation of evasion prompts or "prompt templates" designed to bypass
  safety filters (no `prompts.yaml` shipped).
- Deployment of the uncensored model to public-facing endpoints without
  access control and audit.
- Any use that violates the Google Gemma Terms of Use or applicable law.

## Guardrails
- All inference flows pass through the audit hook; indicator hits are logged
  to the `security` channel.
- Weights are downloaded at runtime; the repo never redistributes them.
