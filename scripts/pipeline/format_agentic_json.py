import json
import logging
from git import Repo
from config import REPO_ROOT, DATASETS_DIR, JSON_AGENTIC_DATASET
import utils

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def format_json_protocol():
    raw_file = DATASETS_DIR / "raw_git_commits.json"
    if not raw_file.exists():
        logging.error(f"{raw_file} not found. Run extract_git_history.py first.")
        return

    commits = utils.read_json(raw_file)

    repo = Repo(REPO_ROOT)
    
    formatted_data = []
    
    for commit in commits:
        instruction = commit["message"]
        
        # Build the JSON response representing tool calls
        tool_calls = []
        for diff in commit["diffs"]:
            from config import parse_diff_metadata
            action, file_path, is_valid = parse_diff_metadata(diff)
            
            if not is_valid:
                continue
            
            content = ""
            if action != "DELETE":
                try:
                    blob = repo.tree(commit["hash"]) / file_path
                    content = blob.data_stream.read().decode('utf-8', errors='replace')
                except KeyError:
                    content = ""
                
            tool_calls.append({
                "name": "edit_file",
                "arguments": {
                    "path": file_path,
                    "action": action,
                    "content": content
                }
            })
            
        if tool_calls:
            formatted_data.append({
                "instruction": instruction,
                "response": json.dumps({"tool_calls": tool_calls}, indent=2)
            })

    utils.write_jsonl(JSON_AGENTIC_DATASET, formatted_data)
            
    logging.info(f"Formatted {len(formatted_data)} examples into {JSON_AGENTIC_DATASET}")

if __name__ == "__main__":
    format_json_protocol()
