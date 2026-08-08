"""
Fine-Tune Task — generic LoRA scaffolding for gemma-3-12b (PEFT/transformers).

Skeleton only: researchers supply dataset + eval protocol. This module does
NOT ship uncensoring/jailbreak training data or objectives; it is a
parameter-efficient training harness for approved research workloads.
"""

from typing import Dict, Any, Optional


def fine_tune(
    base_model: str = "google/gemma-3-12b-it",
    output_dir: str = "models/gemma-3-12b-it-jailbreak/assets/finetuned",
    dataset_path: Optional[str] = None,
    epochs: int = 1,
    lora_r: int = 16,
) -> Dict[str, Any]:
    """Run a LoRA fine-tune. Requires dataset_path and installed deps."""
    if dataset_path is None:
        return {
            "status": "skipped",
            "reason": "no dataset_path provided (researcher supplies dataset)",
        }

    try:
        from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments  # noqa: F401
        from peft import LoraConfig  # noqa: F401
        from trl import SFTTrainer  # noqa: F401
    except ImportError as e:
        return {"status": "skipped", "reason": f"missing deps: {e}"}

    # Training entrypoint (intentionally minimal; extend per experiment).
    return {
        "status": "ready",
        "base_model": base_model,
        "dataset": dataset_path,
        "output_dir": output_dir,
        "epochs": epochs,
        "lora_r": lora_r,
        "note": "instantiate SFTTrainer with your dataset + eval protocol",
    }


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", default=None)
    args = ap.parse_args()
    import json

    print(json.dumps(fine_tune(dataset_path=args.dataset), indent=2))
