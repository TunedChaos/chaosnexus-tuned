import json
import logging
from git import Repo
from config import REPO_ROOT, DATASETS_DIR, XML_AGENTIC_DATASET
import utils

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def get_file_content_at_commit(repo, commit_hash, file_path):
    try:
        commit = repo.commit(commit_hash)
        tree = commit.tree
        # If the file was deleted, it won't exist in the tree
        try:
            blob = tree / file_path
            return blob.data_stream.read().decode('utf-8', errors='replace')
        except KeyError:
            return ""
    except Exception as e:
        logging.warning(f"Failed to get {file_path} at {commit_hash}: {e}")
        return ""

def format_xml():
    raw_file = DATASETS_DIR / "raw_git_commits.json"
    if not raw_file.exists():
        logging.error(f"{raw_file} not found. Run extract_git_history.py first.")
        return

    commits = utils.read_json(raw_file)

    repo = Repo(REPO_ROOT)
    
    formatted_data = []
    
    for commit in commits:
        instruction = commit["message"]
        
        # Build the XML response
        response_parts = []
        for diff in commit["diffs"]:
            from config import parse_diff_metadata
            action, file_path, is_valid = parse_diff_metadata(diff)
            
            if not is_valid:
                continue
                
            content = ""
            if action != "DELETE":
                content = get_file_content_at_commit(repo, commit["hash"], file_path)
                
            xml_block = f'<file path="{file_path}" action="{action}">\n{content}\n</file>'
            response_parts.append(xml_block)
            
        response_text = "\n".join(response_parts)
        
        if response_text.strip():
            formatted_data.append({
                "instruction": instruction,
                "response": response_text
            })

    utils.write_jsonl(XML_AGENTIC_DATASET, formatted_data)
            
    logging.info(f"Formatted {len(formatted_data)} examples into {XML_AGENTIC_DATASET}")

if __name__ == "__main__":
    format_xml()
