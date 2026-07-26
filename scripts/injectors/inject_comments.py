import json
import os
import re
import random

CORE_JSONL = "datasets/core/train.jsonl"
CORE_ALPACA = "datasets/core/train_alpaca.json"
CORE_EVAL_JSONL = "core/eval.jsonl"
CORE_EVAL_ALPACA = "core/eval_alpaca.json"

# Generic detailed narrative comment blocks for different languages/contexts
RHAI_COMMENTS = [
    """\n    // ==========================================
    // NARRATIVE EXPLANATION:
    // This function, {func_name}, encapsulates our logic to keep it clean and readable!
    // We always use early returns if a condition fails or if data is empty.
    // This makes the code much easier for non-technical users to follow.
    // ==========================================""",
    """\n    // ==========================================
    // {func_name} implementation details:
    // Notice how we structure the flow using guard clauses. By exiting early
    // when data is missing or invalid, we prevent deeply nested if-statements
    // and keep the core logic at the top level of the function block.
    // ==========================================""",
    """\n    // ==========================================
    // For {func_name}, we prioritize safety and DRY principles.
    // The explicit early returns are intentional; they act as assertions 
    // that our assumptions about the state hold true before proceeding.
    // ==========================================""",
    """\n    // ==========================================
    // Inside {func_name}, observe the flat hierarchy.
    // Instead of wrapping everything in a massive conditional block, we return 
    // immediately on failure. This is standard operating procedure for our Rhai scripts.
    // ==========================================""",
    """\n    // ==========================================
    // Executing {func_name} logic:
    // We ensure that we avoid global returns by scoping this logic into a function.
    // The early checks ensure that downstream operations only run on valid data.
    // =========================================="""
]

RUST_COMMENTS = [
    """\n// ==========================================
// NARRATIVE EXPLANATION:
// This Rust function, {func_name}, acts as the bridge between our backend and frontend.
// We use the #[tauri::command] macro so the frontend can easily call this.
// We keep the logic straightforward and readable!
// ==========================================\n""",
    """\n// ==========================================
// Command Binding: {func_name}
// We expose this directly to Tauri via the #[tauri::command] macro.
// Any data passed back and forth will be serialized automatically.
// ==========================================\n""",
    """\n// ==========================================
// IPC Handler: {func_name}
// This function bridges the gap between Svelte and Rust. It handles 
// incoming requests and gracefully manages Result returns for the frontend.
// ==========================================\n"""
]

SVELTE_SCRIPT_COMMENTS = [
    """\n    // ==========================================
    // NARRATIVE EXPLANATION:
    // Welcome to our Svelte Component! We use Svelte 5 runes (like $state)
    // to make our variables reactive. This means when the variable changes,
    // the user interface automatically updates for us!
    // ==========================================\n""",
    """\n    // ==========================================
    // Svelte 5 Component Logic:
    // Notice the use of modern runes for reactivity. This ensures that 
    // any state mutations automatically trigger fine-grained DOM updates
    // without needing complex lifecycle hooks.
    // ==========================================\n""",
    """\n    // ==========================================
    // Reactive State Management:
    // We declare our reactive state at the top of the script tag using $state().
    // By following Svelte 5 patterns, we keep the component logic 
    // clean, predictable, and highly performant.
    // ==========================================\n"""
]

SVELTE_HTML_COMMENTS = [
    """\n<!-- \n  NARRATIVE EXPLANATION:\n  This is the visual part of our component! We use standard HTML along with \n  Svelte's curly braces {} to display our data dynamically. It's designed \n  to be clean and very easy to read!\n-->\n""",
    """\n<!-- \n  Markup Section:\n  The DOM structure is rendered reactively. Any variables we defined \n  in the script block are automatically bound and interpolated here.\n-->\n""",
    """\n<!-- \n  Component Layout:\n  We leverage semantic HTML and keep our inline logic to an absolute \n  minimum, relying on the script block for heavy lifting.\n-->\n"""
]


def inject_comments_into_assistant(content):
    # Strip old static comments to ensure idempotency
    content = content.replace("\\n    // ==========================================\\n    // NARRATIVE EXPLANATION:\\n    // This function encapsulates our logic to keep it clean and readable!\\n    // We always use early returns if a condition fails or if data is empty.\\n    // This makes the code much easier for non-technical users to follow.\\n    // ==========================================", "")
    content = content.replace("\\n// ==========================================\\n// NARRATIVE EXPLANATION:\\n// This Rust function acts as the bridge between our backend and frontend.\\n// We use the #[tauri::command] macro so the frontend can easily call this.\\n// We keep the logic straightforward and readable!\\n// ==========================================\\n", "")
    content = content.replace("\\n    // ==========================================\\n    // NARRATIVE EXPLANATION:\\n    // Welcome to our Svelte Component! We use Svelte 5 runes (like $state)\\n    // to make our variables reactive. This means when the variable changes,\\n    // the user interface automatically updates for us!\\n    // ==========================================\\n", "")
    content = content.replace("\\n<!-- \\n  NARRATIVE EXPLANATION:\\n  This is the visual part of our component! We use standard HTML along with \\n  Svelte's curly braces {} to display our data dynamically. It's designed \\n  to be clean and very easy to read!\\n-->\\n", "")
    
    # Strip dynamic comments to reset state
    content = re.sub(r'\\n    // ==========================================\\n    // (?:NARRATIVE EXPLANATION|.*?implementation details|For .*? we prioritize safety|Inside .*? observe the flat hierarchy|Executing .*? logic).*?// ==========================================', '', content, flags=re.DOTALL)
    content = re.sub(r'\\n// ==========================================\\n// (?:NARRATIVE EXPLANATION|Command Binding|IPC Handler).*?// ==========================================\\n', '', content, flags=re.DOTALL)
    content = re.sub(r'\\n    // ==========================================\\n    // (?:NARRATIVE EXPLANATION|Svelte 5 Component Logic|Reactive State Management).*?// ==========================================\\n', '', content, flags=re.DOTALL)
    content = re.sub(r'\\n<!-- \\n  (?:NARRATIVE EXPLANATION|Markup Section|Component Layout).*?-->\\n', '', content, flags=re.DOTALL)

    # If the content is an XML format (Matrix B)
    if "<file path=" in content:
        # Inject Rust comments
        def rust_repl(match):
            func_decl = match.group(1)
            func_name = func_decl.split("fn ")[1].split("(")[0].strip()
            comment = random.choice(RUST_COMMENTS).format(func_name=func_name)
            return func_decl + comment.replace('\\n', '\n')
            
        content = re.sub(r'(#\[tauri::command\]\nfn [^\{]+\{)', rust_repl, content)
        
        # Inject Svelte JS comments
        content = re.sub(r'(<script>)', lambda m: m.group(1) + random.choice(SVELTE_SCRIPT_COMMENTS).replace('\\n', '\n'), content)
        # Inject Svelte HTML comments
        content = re.sub(r'(</script>\n)', lambda m: m.group(1) + random.choice(SVELTE_HTML_COMMENTS).replace('\\n', '\n'), content)
        return content

    # If the content contains a json block (Matrix A or C)
    if "```json" in content:
        # Try to parse the json inside the block
        match = re.search(r'```json\n(.*?)\n```', content, re.DOTALL)
        if match:
            json_str = match.group(1)
            try:
                data = json.loads(json_str)
                modified = False
                
                # Check for Rhai plugins
                if data.get("tool") == "cn_a_create_plugin":
                    if "script_body" in data.get("arguments", {}):
                        script_body = data["arguments"]["script_body"]
                        # Inject after function declarations
                        def rhai_repl(match):
                            func_decl = match.group(1)
                            # Extract function name from "fn process_batch_0() {"
                            func_name = func_decl.replace("fn ", "").split("(")[0].strip()
                            comment = random.choice(RHAI_COMMENTS).format(func_name=func_name)
                            return func_decl + comment
                            
                        new_script_body = re.sub(r'(fn [^\{]+\{)', rhai_repl, script_body)
                        data["arguments"]["script_body"] = new_script_body
                        modified = True
                
                # Check for Svelte components via edit_file
                if "tool_calls" in data:
                    for call in data["tool_calls"]:
                        if call.get("name") == "edit_file" and "content" in call.get("arguments", {}):
                            file_content = call["arguments"]["content"]
                            if "<script>" in file_content:
                                file_content = re.sub(r'(<script>)', lambda m: m.group(1) + random.choice(SVELTE_SCRIPT_COMMENTS), file_content)
                                file_content = re.sub(r'(</script>\\n)', lambda m: m.group(1) + random.choice(SVELTE_HTML_COMMENTS), file_content)
                                call["arguments"]["content"] = file_content
                                modified = True

                if modified:
                    new_json_str = json.dumps(data, indent=2)
                    content = content.replace(json_str, new_json_str)
            except Exception as e:
                print("Failed to parse inner JSON:", e)
    
    return content

def process_jsonl(filepath):
    if not os.path.exists(filepath):
        print(f"Skipping {filepath} (does not exist)")
        return
        
    updated_lines = []
    modified_count = 0
    with open(filepath, 'r') as f:
        for line in f:
            obj = json.loads(line)
            # Find assistant message
            for msg in obj.get("messages", []):
                if msg["role"] == "assistant":
                    old_content = msg["content"]
                    new_content = inject_comments_into_assistant(old_content)
                    if old_content != new_content:
                        msg["content"] = new_content
                        modified_count += 1
            updated_lines.append(obj)
            
    with open(filepath, 'w') as f:
        for obj in updated_lines:
            f.write(json.dumps(obj) + '\n')
            
    print(f"Processed {filepath}: Modified {modified_count} examples.")

def process_alpaca(filepath):
    if not os.path.exists(filepath):
        print(f"Skipping {filepath} (does not exist)")
        return
        
    with open(filepath, 'r') as f:
        data = json.load(f)
        
    modified_count = 0
    for ex in data:
        old_content = ex["output"]
        new_content = inject_comments_into_assistant(old_content)
        if old_content != new_content:
            ex["output"] = new_content
            modified_count += 1
            
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)
        
    print(f"Processed {filepath}: Modified {modified_count} examples.")

def main():
    print("Processing Training Datasets...")
    process_jsonl(CORE_JSONL)
    process_alpaca(CORE_ALPACA)
    print("\nProcessing Evaluation Datasets...")
    process_jsonl(CORE_EVAL_JSONL)
    process_alpaca(CORE_EVAL_ALPACA)
    
    print("\nDone injecting comments into all datasets.")
    print("Done.")

if __name__ == "__main__":
    main()
