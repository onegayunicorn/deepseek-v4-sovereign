#!/bin/bash
# DeepSeek-V4-Flash-0731 — cURL Example
# Endpoint: Hugging Face Inference Router → Novita
set -euo pipefail

curl -X POST "https://router.huggingface.co/v1/chat/completions" \
  -H "Authorization: Bearer $HF_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "deepseek-ai/DeepSeek-V4-Flash-0731:novita",
    "messages": [{"role": "user", "content": "What is the capital of France?"}]
  }'
