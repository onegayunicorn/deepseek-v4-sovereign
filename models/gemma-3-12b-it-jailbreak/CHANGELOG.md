# Changelog — gemma-3-12b-it-jailbreak module

## v1.0.0 (2026-08-08)
- Initial monorepo integration into `deepseek-v4-sovereign`
- Model card, specs, and full 26-variant quantization table
- Hardware profile (AMD Threadripper Zen 9 5000 · 8 GB · 14 TFLOPS) with
  Q4_K_M recommended quant
- Inference runners: transformers, llama.cpp (server/CLI), ollama, docker,
  unsloth, lemonade + unified loader
- Defensive hooks: pre/post load validation, inference metrics with
  jailbreak-indicator detection, quantization-change instrumentation
- Tasks: download, hardware-optimized quant selection, benchmark, fine-tune
  scaffolding
- Triggers: on_model_load, on_inference_complete, on_quant_change
- Tests: import, quant-load, basic inference (mock), defensive detection,
  hardware fit
- CI: model-verify, download-quants cache, hf-sync, delete-hf-gguf
  (workflow_dispatch + explicit confirm)
- Registered in `models/registry.yaml`
