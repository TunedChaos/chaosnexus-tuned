# chaosnexus-tuned/train_unsloth.py
"""
Unsloth LoRA/QLoRA Fine-Tuning Launcher for ChaosNexus Tuned.
Fine-tunes IBM Granite 4.1-8B-Instruct on native Rhai tool synthesis and capability authorization datasets.
"""

import os
import sys
import torch

def run_training():
    print("==================================================")
    print("  ChaosNexus Tuned: Unsloth Fine-Tuning Launcher  ")
    print("==================================================")
    
    try:
        from unsloth import FastLanguageModel
        from trl import SFTTrainer
        from transformers import TrainingArguments
        from datasets import load_dataset
    except ImportError as e:
        print(f"\n[!] Unsloth or dependencies missing: {e}")
        print("    To run fine-tuning, install unsloth via:")
        print("    pip install unsloth trl transformers torch xformers")
        print("    dataset files are generated and ready in datasets/core/")
        return

    max_seq_length = 8192
    dtype = None # Auto detection (Float16 / Bfloat16)
    load_in_4bit = True # 4bit quantization for <6GB VRAM footprint

    model_name = "ibm-granite/granite-4.1-8b-instruct"
    dataset_path = "datasets/core/train.jsonl"
    output_dir = "models/chaosnexus-granite-8b"

    print(f"\n[1/4] Loading base model: {model_name} (4-bit QLoRA)...")
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name = model_name,
        max_seq_length = max_seq_length,
        dtype = dtype,
        load_in_4bit = load_in_4bit,
    )

    print("\n[2/4] Applying LoRA target adapters (r=32, alpha=64)...")
    model = FastLanguageModel.get_peft_model(
        model,
        r = 32,
        target_modules = ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
        lora_alpha = 64,
        lora_dropout = 0.05,
        bias = "none",
        use_gradient_checkpointing = "unsloth",
        random_state = 3407,
    )

    print(f"\n[3/4] Loading training dataset from {dataset_path}...")
    dataset = load_dataset("json", data_files={"train": dataset_path}, split="train")

    trainer = SFTTrainer(
        model = model,
        tokenizer = tokenizer,
        train_dataset = dataset,
        dataset_text_field = "messages",
        max_seq_length = max_seq_length,
        dataset_num_proc = 2,
        packing = False,
        args = TrainingArguments(
            per_device_train_batch_size = 2,
            gradient_accumulation_steps = 8,
            warmup_steps = 10,
            max_steps = 60,
            learning_rate = 2e-4,
            fp16 = not torch.cuda.is_bf16_supported(),
            bf16 = torch.cuda.is_bf16_supported(),
            logging_steps = 1,
            optim = "adamw_8bit",
            weight_decay = 0.01,
            lr_scheduler_type = "linear",
            seed = 3407,
            output_dir = output_dir,
        ),
    )

    print("\n[4/4] Starting Unsloth SFT training run...")
    trainer.train()

    print(f"\n[✓] Training complete! Saving merged GGUF quantized model to {output_dir}_gguf...")
    model.save_pretrained_gguf(output_dir + "_gguf", tokenizer, quantization_method="q4_k_m")
    print("\n[✓] Model export finished successfully!")

if __name__ == "__main__":
    run_training()
