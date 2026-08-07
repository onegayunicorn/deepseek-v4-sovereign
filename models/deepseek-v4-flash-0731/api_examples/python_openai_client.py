"""
DeepSeek-V4-Flash-0731 — OpenAI-Compatible API Example
Endpoint: Hugging Face Inference Router (Novita/Together/DeepInfra/...)
"""
import os

from openai import OpenAI

# Initialize client — fully OpenAI-compatible
client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=os.environ["HF_TOKEN"],  # Your Hugging Face token
)

# Chat completion
completion = client.chat.completions.create(
    model="deepseek-ai/DeepSeek-V4-Flash-0731:novita",
    messages=[{"role": "user", "content": "What is the capital of France?"}],
    stream=False,  # Set True for streaming responses
)

print(completion.choices[0].message)
