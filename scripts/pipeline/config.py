import os
from pathlib import Path

# Paths
CHAOSTUNER_DIR = Path(os.path.dirname(os.path.abspath(__file__))).parent.parent
REPO_ROOT = CHAOSTUNER_DIR.parent

DATASETS_DIR = CHAOSTUNER_DIR / "datasets"
DATASETS_DIR.mkdir(exist_ok=True)

# Datasets
XML_AGENTIC_DATASET = DATASETS_DIR / "agentic_xml.jsonl"
JSON_AGENTIC_DATASET = DATASETS_DIR / "agentic_json.jsonl"
RAW_STRICT_DATASET = DATASETS_DIR / "raw_strict.jsonl"
SYNTHETIC_PROMPTS_DUMP = DATASETS_DIR / "synthetic_prompts_dump.json"

# Settings
GIT_BRANCH = "main" # Change if needing to extract from a different branch
MAX_COMMITS_TO_PROCESS = 1000

def ensure_dirs():
    DATASETS_DIR.mkdir(exist_ok=True)

ensure_dirs()

def parse_diff_metadata(diff):
    action = "MODIFY"
    if diff["change_type"] == "A":
        action = "CREATE"
    elif diff["change_type"] == "D":
        action = "DELETE"
        
    file_path = diff["b_path"] if diff["b_path"] else diff["a_path"]
    
    is_valid = True
    if any(file_path.endswith(ext) for ext in [".lock", "lock.yaml", "lock.json", ".png", ".jpg", ".svg", ".ico", ".wasm"]):
        is_valid = False
    elif any(dir_name in file_path.split('/') for dir_name in ["node_modules", "target", "dist", ".svelte-kit"]):
        is_valid = False
        
    return action, file_path, is_valid
