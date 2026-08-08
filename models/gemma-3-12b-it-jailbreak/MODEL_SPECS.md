# Gemma-3-12B Jailbreak — Model Specifications

## Architecture
- **Base Model:** google/gemma-3-12b-pt
- **Instruction Tuned:** google/gemma-3-12b-it
- **Jailbreak:** alexwirrell/gemma-3-12b-it-jailbreak-EN
- **Quantized:** Codexcoder/gemma-3-12b-it-jailbreak-EN-i1-GGUF
- **Format:** GGUF (imatrix-weighted quants)

## Parameters
| Parameter | Value |
|-----------|-------|
| **Total Parameters** | 12B |
| **Architecture** | gemma3 |
| **Context Length** | 8192 tokens |
| **Format** | GGUF |
| **Type** | Uncensored · Jailbreak |
| **License** | Gemma (Google) |
| **Language** | English |
| **Vision** | Capable |

## Model Tree

```
google/gemma-3-12b-pt
↓ (fine-tune)
google/gemma-3-12b-it
↓ (jailbreak fine-tune)
alexwirrell/gemma-3-12b-it-jailbreak-EN
↓ (quantization)
Codexcoder/gemma-3-12b-it-jailbreak-EN-i1-GGUF
↓ (mirror)
mradermacher/gemma-3-12b-it-jailbreak-EN-GGUF
```

## Use Cases
- 🛡️ Red-teaming / security research
- 🔓 Alignment-vulnerability testing
- 🧪 Overfit-attack research
- 💬 Conversational AI
- 👁️ Vision-capable applications

## Tags
- transformers · gguf · english · uncensored
- jailbreak · red-teaming · safety · security-research
- overfit-attack · gemma-3 · alignment-vulnerability
- imatrix · conversational

## Provenance
- Downloads (last month): 283
- Updated: 2026-06-28
- Collection: "Ai" — 5 items · Owner: Codexcoder
