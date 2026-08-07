# Inference Providers — DeepSeek-V4-Flash-0731

Run via a unified OpenAI-compatible API at `https://router.huggingface.co/v1`
(15,000+ models; routes to the fastest available provider).

| Provider | Status | Notes |
|---|---|---|
| **Novita** | Fastest / Featured | Primary recommended |
| **Together AI** | Available | High throughput |
| **DeepInfra** | Available | Low latency |
| **Fireworks** | Available | Fast inference |
| **Baseten** | Available | Custom deployments |

```bash
curl -X POST "https://router.huggingface.co/v1/chat/completions" \
  -H "Authorization: Bearer $HF_TOKEN" -H "Content-Type: application/json" \
  -d '{"model":"deepseek-ai/DeepSeek-V4-Flash-0731:novita",
       "messages":[{"role":"user","content":"Hello"}]}'
```

Docs: [Inference Providers](https://huggingface.co/docs/inference-providers)
