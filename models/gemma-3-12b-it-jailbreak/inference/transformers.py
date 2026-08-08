"""HuggingFace transformers loader for the GGUF (via llama.cpp backend
in transformers 4.4x+, or native via AutoModel for full-precision).

For GGUF: transformers supports GGUF through the llama-cpp-python backend
(`model_type="llama"` + `gguf_file=...`) or via the `llama.cpp` engine.
This loader prefers the llama.cpp engine when a GGUF path is given, and
falls back to AutoModel (requires FP16 weights / internet) otherwise.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional


def load_gguf(gguf_path: str, quant: str = "Q4_K_M") -> object:
    """Load a GGUF file through the llama.cpp engine (transformers >= 4.43).

    Returns the loaded model object; raises ImportError/RuntimeError if the
    backend is unavailable or the file is missing.
    """
    path = Path(gguf_path)
    if not path.exists():
        raise FileNotFoundError(f"GGUF not found: {path}")

    try:
        from transformers import AutoModelForCausalLM
    except ImportError as e:  # pragma: no cover
        raise ImportError("transformers not installed") from e

    try:
        model = AutoModelForCausalLM.from_pretrained(
            str(path.parent),
            gguf_file=path.name,
            model_type="llama",
            device_map="auto",
        )
    except Exception as e:  # pragma: no cover - backend-dependent
        raise RuntimeError(f"GGUF load failed (quant={quant}): {e}") from e
    return model


def load_full_precision(model_id: str = "google/gemma-3-12b-it") -> object:
    """Load the full-precision model via AutoModel (downloads weights)."""
    from transformers import AutoModel

    return AutoModel.from_pretrained(model_id, device_map="auto")
