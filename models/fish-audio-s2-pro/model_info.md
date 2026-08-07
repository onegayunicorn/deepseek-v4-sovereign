# Fish Audio S2-Pro — Text-to-Speech Model

**Model ID**: `fishaudio/s2-pro`
**Collection**: [Fish Audio S2](https://huggingface.co/fishaudio/fish-audio-s2)
**Type**: Text-to-Speech (TTS)
**Size**: 5B parameters
**Downloads**: 383k+
**Likes**: 1.2k
**Author**: fishaudio
**Parent collections**: Fish Audio S1, Fish Speech

## Description

High-fidelity text-to-speech synthesis supporting natural voice generation,
multi-speaker capabilities, and prosody control. Used by SOVEREIGN for the
voice pipeline (ring + buds) and content audio.

## Quick start

```python
from transformers import AutoProcessor, AutoModel

processor = AutoProcessor.from_pretrained("fishaudio/s2-pro")
model = AutoModel.from_pretrained("fishaudio/s2-pro")
```

See `tts_client.py` in this directory for the sovereign integration wrapper.

## Hardware requirements

- GPU: 24GB+ VRAM (FP16), 16GB+ (INT8 quantized)
- RAM: 64GB+ system memory
