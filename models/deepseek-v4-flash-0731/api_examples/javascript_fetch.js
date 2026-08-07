/*
DeepSeek-V4-Flash-0731 — JavaScript / Fetch API Example
Endpoint: Hugging Face Inference Router
*/
const HF_TOKEN = process.env.HF_TOKEN;

async function queryDeepSeek(prompt) {
  const response = await fetch("https://router.huggingface.co/v1/chat/completions", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${HF_TOKEN}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      model: "deepseek-ai/DeepSeek-V4-Flash-0731:novita",
      messages: [{ role: "user", content: prompt }],
    }),
  });

  const data = await response.json();
  return data.choices[0].message;
}

// Usage
queryDeepSeek("Explain quantum computing").then(console.log);
