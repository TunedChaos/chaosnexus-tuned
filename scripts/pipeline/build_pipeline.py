import os
import subprocess
import shutil
from pathlib import Path

# Paths
ROOT_DIR = Path(os.path.dirname(os.path.abspath(__file__))).parent.parent.parent
TUNER_DIR = ROOT_DIR / "chaosnexus-tuned"
DATASETS_DIR = TUNER_DIR / "datasets"
CORE_DIR = DATASETS_DIR / "core"
SCRIPTS_DIR = TUNER_DIR / "scripts"

def run_script(script_name):
    script_path = SCRIPTS_DIR / script_name
    print(f"\n--- Running {script_name} ---")
    result = subprocess.run(["python", str(script_path)], cwd=str(TUNER_DIR))
    if result.returncode != 0:
        print(f"ERROR: {script_name} failed with code {result.returncode}")
        exit(1)

def main():
    print("=== ChaosNexus Tuned Pipeline Build ===")
    
    # 1. Clean out existing datasets
    print("\n--- Cleaning old datasets ---")
    if CORE_DIR.exists():
        for f in CORE_DIR.glob("*"):
            if f.is_file():
                f.unlink()
                print(f"Deleted {f}")
    else:
        CORE_DIR.mkdir(parents=True, exist_ok=True)
        
    full_stack_dir = DATASETS_DIR / "full_stack"
    if full_stack_dir.exists():
        for f in full_stack_dir.glob("*"):
            if f.is_file():
                f.unlink()
        full_stack_dir.rmdir()
        print("Deleted full_stack directory")
        
    # 2. Inject Edge Cases and Features
    # Since we are dropping full_stack, we run injectors that target core/train.jsonl
    run_script("injectors/inject_edge_cases.py")
    run_script("injectors/inject_final_capabilities_training.py")
    
    # Let's run all valid core injectors
    # run_script("injectors/inject_advanced_capabilities.py")
    # run_script("injectors/inject_missing_core_apis.py")
    # run_script("injectors/inject_refusals.py")
    # run_script("injectors/inject_http_training.py")
    
    # We explicitly skip inject_full_capabilities_training.py because that's full stack!
    
    # 3. Format Native Tools
    # This transforms 'fake' json tools into native OpenAI tool calls,
    # and generates the Alpaca and ShareGPT datasets natively from train.jsonl
    run_script("pipeline/format_native_tools.py")
    
    # 4. Inject Comments into generated code (works on both JSONL and Alpaca)
    run_script("injectors/inject_comments.py")
    
    print("\n=== Pipeline Build Complete ===")

if __name__ == "__main__":
    main()
