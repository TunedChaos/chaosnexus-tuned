import os
import json
import logging
import requests
from config import DATASETS_DIR, SYNTHETIC_PROMPTS_DUMP

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def build_prompts():
    raw_file = DATASETS_DIR / "raw_git_commits.json"
    if not raw_file.exists():
        logging.error(f"{raw_file} not found. Run extract_git_history.py first.")
        return []

    with open(raw_file, "r", encoding="utf-8") as f:
        commits = json.load(f)

    prompts = []
    
    # We want to ask the LLM to rewrite the git diffs into high-quality instructions.
    for commit in commits:
        if not commit["diffs"]:
            continue
            
        system_prompt = (
            "You are an expert AI assistant. I will provide you with a git commit message and a set of file diffs. "
            "Your task is to reverse-engineer this into a highly detailed, step-by-step user instruction as if a "
            "developer were asking you to write this code from scratch. Output ONLY the instruction text."
        )
        
        user_prompt = f"Commit Message: {commit['message']}\n\nDiffs:\n"
        for diff in commit["diffs"]:
            user_prompt += f"File: {diff.get('b_path', diff.get('a_path'))}\n{diff['diff'][:1000]}...\n\n"
            
        prompts.append({
            "hash": commit["hash"],
            "system_prompt": system_prompt,
            "user_prompt": user_prompt
        })
        
    return prompts

def dump_prompts(prompts):
    with open(SYNTHETIC_PROMPTS_DUMP, "w", encoding="utf-8") as f:
        json.dump(prompts, f, indent=2)
    logging.info(f"Dumped {len(prompts)} synthetic generation prompts to {SYNTHETIC_PROMPTS_DUMP}")

def execute_prompts(prompts):
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        logging.error("GEMINI_API_KEY environment variable not set. Falling back to dump mode.")
        dump_prompts(prompts)
        return

    logging.info("Executing prompts against Gemini API... (This may take a while and cost money)")
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro-latest:generateContent?key={api_key}"
    
    results = []
    
    # Just do the first 5 for safety to avoid blowing through quota accidentally
    for idx, prompt in enumerate(prompts[:5]):
        logging.info(f"Processing {idx+1}/5...")
        payload = {
            "contents": [{
                "parts": [{"text": f"{prompt['system_prompt']}\n\n{prompt['user_prompt']}"}]
            }]
        }
        
        try:
            resp = requests.post(url, json=payload)
            resp.raise_for_status()
            data = resp.json()
            
            try:
                synthetic_instruction = data["candidates"][0]["content"]["parts"][0]["text"]
            except (KeyError, IndexError):
                synthetic_instruction = "ERROR_PARSING_RESPONSE"
                
            results.append({
                "original_hash": prompt["hash"],
                "synthetic_instruction": synthetic_instruction
            })
        except Exception as e:
            logging.error(f"API Error: {e}")
            
    out_file = DATASETS_DIR / "synthetic_instructions_results.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    logging.info(f"Saved {len(results)} API results to {out_file}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--execute", action="store_true", help="Execute against Gemini API instead of dumping to JSON")
    args = parser.parse_args()
    
    prompts = build_prompts()
    if args.execute:
        execute_prompts(prompts)
    else:
        dump_prompts(prompts)
