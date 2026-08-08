# Deployment — gemma-3-12b-it-jailbreak

## Local (CPU, recommended quant Q4_K_M)

```bash
# 1. download weights
python scripts/hf_download.py --quant Q4_K_M

# 2. validate before load
python -c "import sys; sys.path.insert(0,'.'); from hooks.pre_load import pre_load_hook; print(pre_load_hook({'model_path':'models/gemma-3-12b-it-jailbreak/assets/recommended/'}))"

# 3. serve
bash models/gemma-3-12b-it-jailbreak/inference/llama_cpp_server.sh
```

## Container

```bash
docker model run hf.co/Codexcoder/gemma-3-12b-it-jailbreak-EN-i1-GGUF:Q4_K_M
```

## Security note

This is an uncensored variant. Public endpoints MUST be access-controlled
and behind the audit hooks (triggers/on_inference_complete.yaml logs
indicator hits to the security channel).
