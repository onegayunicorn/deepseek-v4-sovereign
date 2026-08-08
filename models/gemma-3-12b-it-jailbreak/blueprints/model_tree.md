# Model Tree — gemma-3-12b-it-jailbreak

```
google/gemma-3-12b-pt                     (base pretrained)
    ↳ google/gemma-3-12b-it               (instruction tuned)
        ↳ alexwirrell/gemma-3-12b-it-jailbreak-EN   (jailbreak fine-tune)
            ↳ Codexcoder/gemma-3-12b-it-jailbreak-EN-i1-GGUF  ✅ (imatrix quants)
                ↳ mradermacher/gemma-3-12b-it-jailbreak-EN-GGUF (static quant mirror)
```

- Base: google/gemma-3-12b-pt — pretrained 12B, 8192 ctx, vision-capable.
- Instruct: google/gemma-3-12b-it — instruction-tuned variant.
- Jailbreak: alexwirrell/gemma-3-12b-it-jailbreak-EN — alignment-vulnerability
  research fine-tune.
- Quantized: Codexcoder/gemma-3-12b-it-jailbreak-EN-i1-GGUF — imatrix-weighted
  GGUF, 26 variants (see QUANTIZATION_TABLE.md).
- Mirror: mradermacher/gemma-3-12b-it-jailbreak-EN-GGUF — static quants backup.
