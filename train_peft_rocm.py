# chaosnexus-tuned/train_peft_rocm.py
"""ROCm / non-Unsloth PEFT SFT trainer for ChaosNexus Tuned (iter-2+).

Unsloth rejects AMD GPUs; this launcher mirrors ChaosNexus_Tuned.yaml LoRA
ranks using transformers + peft + trl on a CUDA/ROCm-capable PyTorch.
"""

from __future__ import annotations

import argparse
import os
import sys

import torch
from datasets import load_dataset
from peft import LoraConfig, PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer
from trl import SFTConfig, SFTTrainer


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--base_model",
        default="unsloth/granite-4.1-8b",
        help="Base instruct checkpoint (same family as studio iter-1).",
    )
    parser.add_argument(
        "--adapter",
        default="",
        help="Optional existing PEFT adapter to continue-train (preserves prior floor).",
    )
    parser.add_argument("--dataset", default="datasets/iter8/train.jsonl")
    parser.add_argument(
        "--output_dir",
        default=os.path.expanduser(
            "~/.unsloth/studio/outputs/chaosnexus-tuned-iter8-rocm"
        ),
    )
    parser.add_argument("--max_seq_length", type=int, default=4096)
    parser.add_argument("--num_epochs", type=float, default=2.0)
    parser.add_argument("--batch_size", type=int, default=1)
    parser.add_argument("--grad_accum", type=int, default=16)
    parser.add_argument("--learning_rate", type=float, default=2e-4)
    parser.add_argument("--lora_r", type=int, default=32)
    parser.add_argument("--lora_alpha", type=int, default=64)
    parser.add_argument("--lora_dropout", type=float, default=0.05)
    parser.add_argument("--max_steps", type=int, default=-1)
    args = parser.parse_args()

    if not torch.cuda.is_available():
        print("CUDA/ROCm not available in this interpreter.", file=sys.stderr)
        sys.exit(1)

    dtype = torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16
    print(f"Device0={torch.cuda.get_device_name(0)} dtype={dtype}")
    print(f"Loading base {args.base_model}...")

    tokenizer = AutoTokenizer.from_pretrained(args.base_model, use_fast=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        args.base_model,
        dtype=dtype,
        device_map={"": 0},
    )
    model.config.use_cache = False

    # Continue from a prior adapter when polishing toward ≥0.90 so we do not
    # wipe a cleared smoke/mean floor with a fresh random LoRA init.
    peft_config = None
    if args.adapter:
        print(f"Continuing from adapter {args.adapter}...")
        model = PeftModel.from_pretrained(model, args.adapter, is_trainable=True)
    else:
        peft_config = LoraConfig(
            r=args.lora_r,
            lora_alpha=args.lora_alpha,
            lora_dropout=args.lora_dropout,
            bias="none",
            task_type="CAUSAL_LM",
            target_modules=[
                "q_proj",
                "k_proj",
                "v_proj",
                "o_proj",
                "gate_proj",
                "up_proj",
                "down_proj",
            ],
        )

    ds = load_dataset("json", data_files={"train": args.dataset}, split="train")

    def to_text(example: dict) -> dict:
        messages = example["messages"]
        text = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=False,
        )
        return {"text": text}

    ds = ds.map(to_text, remove_columns=ds.column_names)

    os.makedirs(args.output_dir, exist_ok=True)
    sft_kwargs = dict(
        output_dir=args.output_dir,
        per_device_train_batch_size=args.batch_size,
        gradient_accumulation_steps=args.grad_accum,
        learning_rate=args.learning_rate,
        num_train_epochs=args.num_epochs,
        logging_steps=1,
        save_steps=8,
        save_total_limit=3,
        bf16=dtype == torch.bfloat16,
        fp16=dtype == torch.float16,
        optim="adamw_torch",
        lr_scheduler_type="cosine",
        warmup_ratio=0.03,
        report_to=[],
        seed=3407,
        gradient_checkpointing=True,
        dataset_text_field="text",
        max_length=args.max_seq_length,
        packing=False,
    )
    if args.max_steps > 0:
        sft_kwargs["max_steps"] = args.max_steps

    training_args = SFTConfig(**sft_kwargs)

    trainer_kwargs = dict(
        model=model,
        args=training_args,
        train_dataset=ds,
        processing_class=tokenizer,
    )
    if peft_config is not None:
        trainer_kwargs["peft_config"] = peft_config
    trainer = SFTTrainer(**trainer_kwargs)

    print("Starting PEFT SFT...")
    trainer.train()
    print(f"Saving adapter to {args.output_dir}")
    trainer.model.save_pretrained(args.output_dir)
    tokenizer.save_pretrained(args.output_dir)
    print("Done.")


if __name__ == "__main__":
    main()
