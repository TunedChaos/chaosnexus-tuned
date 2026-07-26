# /home/flyingmongoose/Projects/TunedChaos/tuned-chaos/chaosnexus-tuned/train_granite.py
"""
ChaosNexus Tuned - Model Training Pipeline
Optimized for IBM Granite 8B / Qwen 7B LoRA fine-tuning using Unsloth on AMD ROCm (RX 7900 XTX 24GB VRAM).
"""

import os
import sys

# Crucial ROCm compatibility environment variables for AMD Radeon RX 7900 XTX (gfx1100)
os.environ["HSA_OVERRIDE_GFX_VERSION"] = "11.0.0"
os.environ["HIP_VISIBLE_DEVICES"] = "0"

import torch
# Monkey-patch missing torch.int1 for torchao under PyTorch 2.5.1 ROCm
torch.int1 = getattr(torch, "int1", torch.int8)

from unsloth import FastLanguageModel
from datasets import load_dataset
import trl.trainer.sft_trainer
from trl import SFTTrainer, SFTConfig
from transformers import TrainingArguments

# Patch SFTConfig in both trl and trl.trainer.sft_trainer modules
def make_patched_init(orig_init):
    def _patched(self, *args, **kwargs):
        kwargs.pop("push_to_hub_token", None)
        return orig_init(self, *args, **kwargs)
    return _patched

SFTConfig.__init__ = make_patched_init(SFTConfig.__init__)
trl.trainer.sft_trainer.SFTConfig.__init__ = make_patched_init(trl.trainer.sft_trainer.SFTConfig.__init__)

def main():
    print("=" * 70)
    print("  ChaosNexus Tuned - Unsloth Model Training Run")
    print("  Hardware Target: AMD Radeon RX 7900 XTX (24GB VRAM ROCm)")
    print("  CPU Target: AMD Ryzen 9 9950X3D (32 Threads)")
    print("=" * 70)

    # 1. Model Configuration
    max_seq_length = 4096
    dtype = None # Auto detection (Float16/Bfloat16 for ROCm)
    load_in_4bit = True # 4bit quantization to maximize VRAM efficiency

    model_name = "unsloth/Qwen2.5-7B-Instruct-bnb-4bit"
    print(f"\n[1/5] Loading base model '{model_name}'...")

    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name = model_name,
        max_seq_length = max_seq_length,
        dtype = dtype,
        load_in_4bit = load_in_4bit,
    )

    # 2. Add LoRA Adapters
    print("[2/5] Adding FastLanguageModel LoRA adapters...")
    model = FastLanguageModel.get_peft_model(
        model,
        r = 16,
        target_modules = [
            "q_proj", "k_proj", "v_proj", "o_proj",
            "gate_proj", "up_proj", "down_proj"
        ],
        lora_alpha = 16,
        lora_dropout = 0, # Optimized 0 dropout for Unsloth
        bias = "none",
        use_gradient_checkpointing = "unsloth", # 30% VRAM saving
        random_state = 3407,
    )

    # 3. Load & Format Dataset
    dataset_file = os.path.join(os.path.dirname(__file__), "datasets", "core", "train_sharegpt.json")
    print(f"[3/5] Loading dataset from '{dataset_file}'...")
    
    dataset = load_dataset("json", data_files=dataset_file, split="train")

    def format_prompts(examples):
        texts = []
        for conversations in examples["conversations"]:
            formatted_text = ""
            for message in conversations:
                role = message.get("from", "user")
                val = message.get("value", "")
                if role == "system":
                    formatted_text += f"<|im_start|>system\n{val}<|im_end|>\n"
                elif role in ["human", "user"]:
                    formatted_text += f"<|im_start|>user\n{val}<|im_end|>\n"
                elif role in ["gpt", "assistant"]:
                    formatted_text += f"<|im_start|>assistant\n{val}<|im_end|>\n"
            texts.append(formatted_text)
        return {"text": texts}

    formatted_dataset = dataset.map(format_prompts, batched=True)

    # 4. Configure Trainer using SFTConfig directly
    print("[4/5] Starting SFTTrainer execution...")
    training_args = SFTConfig(
        dataset_text_field = "text",
        max_seq_length = max_seq_length,
        per_device_train_batch_size = 2,
        gradient_accumulation_steps = 4,
        warmup_steps = 5,
        max_steps = 60, # Initial fine-tuning epoch run
        learning_rate = 2e-4,
        fp16 = not torch.cuda.is_bf16_supported(),
        bf16 = torch.cuda.is_bf16_supported(),
        logging_steps = 1,
        optim = "adamw_8bit",
        weight_decay = 0.01,
        lr_scheduler_type = "linear",
        seed = 3407,
        output_dir = "models/outputs",
        report_to = "none",
    )
    setattr(training_args, "push_to_hub_token", None)

    trainer = SFTTrainer(
        model = model,
        tokenizer = tokenizer,
        train_dataset = formatted_dataset,
        dataset_num_proc = 2,
        packing = False,
        args = training_args,
    )

    trainer_stats = trainer.train()
    print(f"\nTraining completed in {trainer_stats.metrics['train_runtime']:.2f} seconds!")

    # 5. Save Model & Merged LoRA Weights
    save_path = os.path.join(os.path.dirname(__file__), "models", "chaosnexus-tuned-7b-lora")
    print(f"\n[5/5] Saving fine-tuned model adapters to '{save_path}'...")
    model.save_pretrained(save_path)
    tokenizer.save_pretrained(save_path)

    print("\nSUCCESS: ChaosNexus Tuned fine-tuning run completed successfully!")

if __name__ == "__main__":
    main()
