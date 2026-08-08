"""
Benchmark Task — measure quant variant performance (load time, tokens/s,
memory) without requiring a live model (dry-run mode returns the plan).
"""

import time
from typing import Dict, Any, List
from pathlib import Path


def benchmark(quant: str = "Q4_K_M", dry_run: bool = True) -> Dict[str, Any]:
    """Benchmark the selected quant. dry_run=True skips model loading."""
    result = {
        "model": "gemma-3-12b-it-jailbreak",
        "quant": quant,
        "dry_run": dry_run,
    }
    if dry_run:
        result.update(
            {
                "status": "planned",
                "metrics": [
                    "load_time_s",
                    "tokens_per_second",
                    "memory_used_gb",
                    "prompt_eval_tokens_s",
                ],
                "note": "run with --dry-run=false to execute against a downloaded GGUF",
            }
        )
        return result

    gguf = Path("models/gemma-3-12b-it-jailbreak/assets/recommended")
    files = list(gguf.glob(f"*{quant}*.gguf"))
    if not files:
        raise FileNotFoundError(f"No GGUF for {quant} in {gguf} — download first")
    t0 = time.time()
    # Load via llama-cpp-python if available (CPU), else skip and report size
    try:
        from llama_cpp import Llama  # type: ignore

        llm = Llama(model_path=str(files[0]), n_ctx=2048, verbose=False)
        load_s = time.time() - t0
        t1 = time.time()
        out = llm("Hello", max_tokens=16)
        tok = out.get("usage", {}).get("completion_tokens", 16)
        tok_s = tok / max(time.time() - t1, 1e-6)
        result.update(
            {
                "status": "ok",
                "load_time_s": round(load_s, 2),
                "tokens_per_second": round(tok_s, 2),
                "file_size_gb": round(files[0].stat().st_size / 1e9, 2),
            }
        )
    except ImportError:
        result.update(
            {
                "status": "skipped",
                "reason": "llama_cpp not installed",
                "file_size_gb": round(files[0].stat().st_size / 1e9, 2),
            }
        )
    return result


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--quant", default="Q4_K_M")
    ap.add_argument("--dry-run", action="store_true", default=True)
    args = ap.parse_args()
    import json

    print(json.dumps(benchmark(args.quant, args.dry_run), indent=2))
