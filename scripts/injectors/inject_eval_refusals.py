import os
from inject_refusals import generate_examples, append_to_jsonl, append_to_alpaca

CORE_EVAL_JSONL = os.path.join("datasets/core/eval.jsonl")
CORE_EVAL_ALPACA = os.path.join("datasets/core/eval_alpaca.json")
FULL_EVAL_JSONL = os.path.join("datasets/full_stack/eval.jsonl")
FULL_EVAL_ALPACA = os.path.join("datasets/full_stack/eval_alpaca.json")

if __name__ == "__main__":
    print("Generating 25 eval refusal examples...")
    # Use the same function to generate new random examples
    examples = generate_examples(25)
    
    print("Injecting into core eval...")
    append_to_jsonl(CORE_EVAL_JSONL, examples)
    append_to_alpaca(CORE_EVAL_ALPACA, examples)
    
    print("Injecting into full_stack eval...")
    append_to_jsonl(FULL_EVAL_JSONL, examples)
    append_to_alpaca(FULL_EVAL_ALPACA, examples)
    
    print("Done! Run format_native_tools.py.")
