# chaosnexus-tuned/scripts/run_evals.py
"""Run ChaosNexus Anvil golden-prompt evals against a local LoRA or full checkpoint."""

import json
import os
import re

import torch

try:
    from unsloth import FastLanguageModel
    HAS_UNSLOTH = True
except (ImportError, NotImplementedError):
    HAS_UNSLOTH = False

from transformers import AutoModelForCausalLM, AutoTokenizer

QUESTIONS_FILE = "tests/Questions.md"
OUTPUT_FILE = "tests/eval_results.md"
MAX_SEQ_LENGTH = 4096


def _remap_lora_keys(state: dict, model) -> dict:
    """Align PEFT key layouts (``lora_A.weight`` vs ``lora_A.default.weight``)."""
    model_keys = {n for n, _ in model.named_parameters()}
    remapped = {}
    for key, value in state.items():
        if key in model_keys:
            remapped[key] = value
            continue
        alt = key
        if ".lora_A.weight" in key or ".lora_B.weight" in key:
            alt = key.replace(".lora_A.weight", ".lora_A.default.weight").replace(
                ".lora_B.weight", ".lora_B.default.weight"
            )
        elif ".lora_A.default.weight" in key or ".lora_B.default.weight" in key:
            alt = key.replace(".lora_A.default.weight", ".lora_A.weight").replace(
                ".lora_B.default.weight", ".lora_B.weight"
            )
        remapped[alt if alt in model_keys else key] = value
    return remapped


def load_peft_adapter(adapter_dir: str):
    """Load a PEFT LoRA on GPU without Unsloth (ROCm / non-NVIDIA path).

    PeftModel.from_pretrained can leave adapter tensors at init on some Unsloth
    exports; we always overlay adapter_model.safetensors via load_state_dict.
    """
    from peft import PeftModel
    from safetensors.torch import load_file

    config_path = os.path.join(adapter_dir, "adapter_config.json")
    with open(config_path, "r", encoding="utf-8") as f:
        adapter_config = json.load(f)
    base_model_path = adapter_config.get("base_model_name_or_path")
    if not base_model_path:
        raise SystemExit(f"adapter_config.json missing base_model_name_or_path: {config_path}")

    if not torch.cuda.is_available():
        raise SystemExit(
            "CUDA/ROCm not available in this Python env. "
            "Use a ROCm PyTorch venv (e.g. Unsloth studio) or NVIDIA Unsloth."
        )

    dtype = torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16
    print(f"Loading base model {base_model_path} (dtype={dtype}, device 0)...")
    base_model = AutoModelForCausalLM.from_pretrained(
        base_model_path,
        dtype=dtype,
        device_map={"": 0},
    )
    print(f"Loading PEFT adapter scaffold {adapter_dir}...")
    model = PeftModel.from_pretrained(base_model, adapter_dir)
    weights_path = os.path.join(adapter_dir, "adapter_model.safetensors")
    if not os.path.isfile(weights_path):
        raise SystemExit(f"Missing adapter weights: {weights_path}")
    print(f"Overlaying adapter weights from {weights_path}...")
    state = _remap_lora_keys(load_file(weights_path), model)
    missing, unexpected = model.load_state_dict(state, strict=False)
    unexpected_lora = [k for k in unexpected if "lora_" in k]
    if unexpected_lora:
        raise SystemExit(f"Unexpected LoRA keys after overlay: {unexpected_lora[:5]}")
    # Sanity: trained LoRA-B should not be entirely zero.
    lora_b = [p for n, p in model.named_parameters() if "lora_B" in n]
    if lora_b and all(float(p.detach().abs().sum()) == 0.0 for p in lora_b):
        raise SystemExit("LoRA-B tensors are all zero after overlay; adapter did not load.")
    tokenizer = AutoTokenizer.from_pretrained(base_model_path)
    return model, tokenizer

def extract_prompts(filepath):
    with open(filepath, 'r') as f:
        content = f.read()
    
    prompts = []
    # Match headers starting with # followed by a number
    sections = re.split(r'\n# \d+\.\s+', '\n' + content)[1:]
    
    for section in sections:
        # Extract title (first line)
        lines = section.split('\n')
        title = lines[0].strip()
        
        # Check if there is a ``` block
        code_block_match = re.search(r'```(.*?)```', section, re.DOTALL)
        if code_block_match:
            prompt_text = code_block_match.group(1).strip()
        else:
            # If no code block, just take the rest of the text after some cleanup
            text_lines = [ln for ln in lines[1:] if ln.strip() and not ln.startswith('##')]
            prompt_text = "\n".join(text_lines).strip()
            
        if prompt_text:
            prompts.append((title, prompt_text))
            
    return prompts

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str, default="lora_model", help="Path to local trained model or HF hub")
    parser.add_argument("--max_tokens", type=int, default=1024, help="Max new tokens to generate")
    parser.add_argument(
        "--indices",
        type=str,
        default="",
        help="Comma-separated 1-based prompt indices to run (e.g. 1,4,5,7). Empty = all.",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=OUTPUT_FILE,
        help="Markdown output path relative to cwd (default tests/eval_results.md)",
    )
    parser.add_argument(
        "--greedy",
        action="store_true",
        help="Decode with do_sample=False for stable scoring (iter-3+).",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.3,
        help="Sampling temperature when --greedy is not set (default 0.3).",
    )
    args = parser.parse_args()

    print(f"Extracting prompts from {QUESTIONS_FILE}...")
    prompts = extract_prompts(QUESTIONS_FILE)
    print(f"Found {len(prompts)} prompts.")

    if args.indices.strip():
        selected = []
        for part in args.indices.split(","):
            idx = int(part.strip())
            if idx < 1 or idx > len(prompts):
                raise SystemExit(f"--indices out of range: {idx} (1..{len(prompts)})")
            selected.append((idx, prompts[idx - 1]))
        print(f"Smoke/subset: running indices {[i for i, _ in selected]}")
    else:
        selected = list(enumerate(prompts, start=1))

    print(f"Loading model {args.model}...")

    config_path = os.path.join(args.model, "adapter_config.json")
    if HAS_UNSLOTH and not os.path.exists(config_path):
        model, tokenizer = FastLanguageModel.from_pretrained(
            model_name=args.model,
            max_seq_length=MAX_SEQ_LENGTH,
            dtype=None,
            load_in_4bit=True,
        )
        FastLanguageModel.for_inference(model)
    elif os.path.exists(config_path):
        # Prefer PEFT+safetensors overlay so Unsloth studio adapters work on ROCm.
        model, tokenizer = load_peft_adapter(args.model)
    else:
        model = AutoModelForCausalLM.from_pretrained(args.model, device_map={"": 0})
        tokenizer = AutoTokenizer.from_pretrained(args.model)

    results = []

    system_prompt = "You are an elite Workspace Systems Architect. You master the ChaosNexus Anvil MCP. You autonomously discover and leverage capabilities provided by your workspace environment. You MUST ONLY write Rhai scripts when creating plugins. NEVER output Python, Bash, Node.js, or any other language. Always search for plugins before creating one."

    for idx, (title, prompt_text) in selected:
        print(f"Evaluating [{idx}/{len(prompts)}]: {title}")

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt_text}
        ]

        inputs = tokenizer.apply_chat_template(
            messages,
            tokenize = True,
            add_generation_prompt = True,
            return_tensors = "pt",
            return_dict = True,
        ).to(model.device)

        gen_kwargs = dict(
            max_new_tokens=args.max_tokens,
            use_cache=True,
        )
        if args.greedy:
            gen_kwargs["do_sample"] = False
        else:
            gen_kwargs["do_sample"] = True
            gen_kwargs["temperature"] = args.temperature
            gen_kwargs["top_p"] = 0.9
        outputs = model.generate(**inputs, **gen_kwargs)
        response = tokenizer.batch_decode(outputs[:, inputs['input_ids'].shape[1]:], skip_special_tokens=True)[0]

        results.append({
            "index": idx,
            "title": title,
            "prompt": prompt_text,
            "response": response
        })

    out_path = args.output
    print(f"Saving results to {out_path}...")
    with open(out_path, 'w') as f:
        f.write("# ChaosNexus Anvil Evaluation Results\n\n")
        f.write(f"**Model:** `{args.model}`\n\n")
        if args.indices.strip():
            f.write(f"**Subset indices:** `{args.indices}`\n\n")
        if args.greedy:
            f.write("**Decode:** greedy (`do_sample=False`)\n\n")
        for res in results:
            f.write(f"## {res['index']}. {res['title']}\n")
            f.write("### Prompt\n")
            f.write(f"```\n{res['prompt']}\n```\n\n")
            f.write("### Response\n")
            f.write(f"{res['response']}\n\n")
            f.write("---\n\n")

if __name__ == "__main__":
    main()
