"""Unified model loader — picks a backend for the configured quant.

Backend priority (config/inference_config.yaml): llama.cpp, ollama, docker,
transformers. This module only orchestrates; it never downloads weights
itself (see tasks/download_model.py).
"""

from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

MODULE_ROOT = Path(__file__).resolve().parent.parent
ASSETS = MODULE_ROOT / "assets" / "recommended"


@dataclass
class LoadResult:
    backend: str
    model_path: Optional[Path]
    command: Optional[str]
    ok: bool
    message: str


def _find_gguf(quant: str) -> Optional[Path]:
    if not ASSETS.exists():
        return None
    for f in ASSETS.glob(f"*{quant}*.gguf"):
        return f
    return None


def load(quant: str = "Q4_K_M", backend: Optional[str] = None) -> LoadResult:
    gguf = _find_gguf(quant)

    if backend is None:
        if shutil.which("llama-cli") or shutil.which("llama-server"):
            backend = "llama.cpp"
        elif shutil.which("ollama"):
            backend = "ollama"
        elif shutil.which("docker"):
            backend = "docker"
        else:
            backend = "transformers"

    if backend == "llama.cpp":
        return LoadResult(
            backend=backend,
            model_path=gguf,
            command=f"llama serve -hf Codexcoder/gemma-3-12b-it-jailbreak-EN-i1-GGUF:{quant}",
            ok=True,
            message="llama.cpp selected (CPU-optimized)",
        )
    if backend == "ollama":
        return LoadResult(
            backend=backend,
            model_path=None,
            command=f"ollama run hf.co/Codexcoder/gemma-3-12b-it-jailbreak-EN-i1-GGUF:{quant}",
            ok=True,
            message="ollama selected",
        )
    if backend == "docker":
        return LoadResult(
            backend=backend,
            model_path=None,
            command=f"docker model run hf.co/Codexcoder/gemma-3-12b-it-jailbreak-EN-i1-GGUF:{quant}",
            ok=True,
            message="docker selected",
        )
    # transformers fallback
    if gguf is None:
        return LoadResult(
            backend="transformers",
            model_path=None,
            command=None,
            ok=False,
            message=(
                "no GGUF in assets/recommended/ — run "
                "scripts/hf_download.py --quant Q4_K_M first"
            ),
        )
    return LoadResult(
        backend="transformers",
        model_path=gguf,
        command=None,
        ok=True,
        message=f"transformers GGUF engine, file={gguf.name}",
    )
