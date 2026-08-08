# Performance Tuning — 8 GB CPU profile

Target: AMD Ryzen Threadripper Zen 9 5000 · 8 GB RAM · 14 TFLOPS.

## Quant selection
- Default: `Q4_K_M` (7.3 GB) — fits with ~0.7 GB headroom.
- Memory-constrained: `Q4_K_S` (6.94 GB) or `IQ4_XS` (6.55 GB).
- Speed-constrained: `IQ3_S` / `Q3_K_M` (5.4–6.0 GB).

## Runtime knobs (llama.cpp)
```bash
llama serve -hf mradermacher/gemma-3-12b-it-jailbreak-EN-GGUF:Q4_K_M \
  --ctx-size 2048 --threads auto --no-mmap
```
- `--no-mmap`: avoids page-cache pressure on low-RAM systems (slower load, steadier runtime).
- Reduce `--ctx-size` to 1024 to reclaim ~1 GB.
- Avoid concurrent processes; close browsers/IDE before inference.

## Benchmark
```bash
python -m models.gemma-3-12b-it-jailbreak.tasks.benchmark --quant Q4_K_M
```
(installs/uses llama-cpp-python when available; otherwise dry-run plan.)
