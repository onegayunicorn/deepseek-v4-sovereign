# Gemma-3-12B Jailbreak — Quantization Table

All 26 variants cataloged (imatrix-weighted quants). Recommended default for
this hardware profile: **Q4_K_M** (7.3 GB).

| Variant | Type | Size (GB) | Quality | Notes |
| :--- | :--- | :---: | :--- | :--- |
| imatrix | imatrix | 0.1 | N/A | imatrix file — custom quantization generation |
| IQ1_S | IQ1_S | 2.95 | Lowest | "For the desperate" — 1-bit ultra-light |
| IQ1_M | IQ1_M | 3.16 | Very Low | "Mostly desperate" — 1-bit |
| IQ2_XXS | IQ2_XXS | 3.53 | Very Low | 2-bit extreme compression |
| IQ2_XS | IQ2_XS | 3.84 | Very Low | 2-bit extra-small |
| IQ2_S | IQ2_S | 4.02 | Low | 2-bit small |
| Q2_K_S | Q2_K_S | 4.45 | Low | 2-bit K — very low quality |
| IQ2_M | IQ2_M | 4.31 | Low | 2-bit medium |
| Q2_K | Q2_K | 4.77 | Low | IQ3_XXS likely better |
| IQ3_XXS | IQ3_XXS | 4.78 | Medium-Low | Lower quality 3-bit |
| IQ3_XS | IQ3_XS | 5.21 | Medium | 3-bit extra-small |
| IQ3_S | IQ3_S | 5.46 | Medium-High | Beats Q3_K* — recommended 3-bit |
| Q3_K_S | Q3_K_S | 5.46 | Medium | IQ3_XS likely better |
| IQ3_M | IQ3_M | 5.66 | High | 3-bit medium |
| Q3_K_M | Q3_K_M | 6.01 | High | IQ3_S likely better |
| Q3_K_L | Q3_K_L | 6.48 | High | IQ3_M likely better |
| IQ4_XS | IQ4_XS | 6.55 | Very High | Optimal — best balance |
| IQ4_NL | IQ4_NL | 6.89 | Very High | Prefer IQ4_XS |
| Q4_0 | Q4_0 | 6.91 | High | Fast, low quality |
| Q4_K_S | Q4_K_S | 6.94 | Very High | Optimal size/speed/quality |
| **Q4_K_M** | Q4_K_M | **7.30** | Very High | **Fast — RECOMMENDED ✅** |
| Q4_1 | Q4_1 | 7.56 | Very High | 4.1 variant |
| Q5_K_S | Q5_K_S | 8.23 | Excellent | 5-bit small — high fidelity |
| Q5_K_M | Q5_K_M | 8.45 | Excellent | 5-bit medium — high fidelity |
| Q6_K | Q6_K | 9.66 | Near-Lossless | Practically like FP16 |

## Hardware fit

| Property | Value |
| :--- | :--- |
| Recommended | Q4_K_M (7.3 GB) |
| Reason | Fits 8 GB RAM with 0.7 GB headroom |
| CPU | AMD Ryzen Threadripper Zen 9 5000 |
| RAM | 8 GB |
| Compute | 14.00 TFLOPS |

> Note: a 12B model at Q4_K_M in 8 GB RAM is at the practical edge —
> expect slow CPU token rates and OS swap pressure if other processes
> consume memory. See `docs/performance_tuning.md`.
