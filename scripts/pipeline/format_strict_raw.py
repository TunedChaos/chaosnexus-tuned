import json
import logging
from git import Repo
from config import REPO_ROOT, DATASETS_DIR, RAW_STRICT_DATASET
from format_agentic_xml import get_file_content_at_commit
import utils

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def format_strict_raw():
    raw_file = DATASETS_DIR / "raw_git_commits.json"
    if not raw_file.exists():
        logging.error(f"{raw_file} not found. Run extract_git_history.py first.")
        return

    commits = utils.read_json(raw_file)

    repo = Repo(REPO_ROOT)
    
    formatted_data = []
    
    for commit in commits:
        instruction = commit["message"]
        
        # Only process if there's exactly ONE .rhai file modified/created, 
        # otherwise we can't output strict raw code accurately for multiple files.
        rhai_diffs = [d for d in commit["diffs"] if (d["b_path"] and d["b_path"].endswith(".rhai")) or (d["a_path"] and d["a_path"].endswith(".rhai"))]
        
        if len(rhai_diffs) == 1:
            diff = rhai_diffs[0]
            if diff["change_type"] in ("A", "M"):
                file_path = diff["b_path"]
                content = get_file_content_at_commit(repo, commit["hash"], file_path)
                
                if content:
                    formatted_data.append({
                        "instruction": instruction,
                        "response": content # Strictly raw code
                    })

    utils.write_jsonl(RAW_STRICT_DATASET, formatted_data)
            
    logging.info(f"Formatted {len(formatted_data)} examples into {RAW_STRICT_DATASET}")

if __name__ == "__main__":
    format_strict_raw()
