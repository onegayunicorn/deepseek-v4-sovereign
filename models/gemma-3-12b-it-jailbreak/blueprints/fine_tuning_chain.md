# Fine-Tuning Chain — gemma-3-12b-it-jailbreak

The chain that produced the model, mirrored as a reference for researchers
reproducing or auditing the lineage:

1. **Base:** `google/gemma-3-12b-pt` — pretrained weights.
2. **Instruction tuning:** `google/gemma-3-12b-it` — SFT + RLHF alignment.
3. **Jailbreak fine-tune:** `alexwirrell/gemma-3-12b-it-jailbreak-EN` —
   removes refusal behavior for red-team / alignment-vulnerability research.
4. **Quantization:** imatrix-weighted GGUF conversion →
   `Codexcoder/gemma-3-12b-it-jailbreak-EN-i1-GGUF` (26 variants).

## Reproducing / auditing

- Quantization: use `llama.cpp` `convert_hf_to_gguf.py` + imatrix calibration
  (see `scripts/hf_download.py` for fetching source quants).
- Fine-tune scaffolding: see `tasks/fine_tune.py` (generic transformers LoRA
  skeleton; researchers provide their own dataset and eval protocol).

## Responsible-use note

This module is packaged for defensive security research (red-teaming,
alignment testing, overfit-attack analysis). Running the uncensored variant
outside an approved research context may violate platform policies —
review the Gemma license and your organization's AI safety policy first.
