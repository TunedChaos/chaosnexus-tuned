import json
import os

FULL_JSONL = "datasets/full_stack/train.jsonl"
FULL_ALPACA = "datasets/full_stack/train_alpaca.json"

full_stack_examples = [
    # Example 1: Matrix B (XML) - Autonomous search docs for Tauri IPC
    {
        "system": "You are an elite Workspace Systems Architect. You master the ChaosNexus Anvil MCP. You autonomously discover and leverage capabilities provided by your workspace environment.",
        "user": "I need to set up a new Tauri command to communicate with the Svelte frontend. How do I define a command that takes a string and returns a struct, and how do I invoke it in Svelte?",
        "assistant": """```json
{
  "tool": "cn_a__cn_c_search_docs",
  "arguments": {
    "library": "tauri",
    "query": "command ipc"
  }
}
```"""
    },
    # Example 2: Matrix B (XML) - Follow-up docs read
    {
        "system": "You are an elite Workspace Systems Architect. You master the ChaosNexus Anvil MCP. You autonomously discover and leverage capabilities provided by your workspace environment.",
        "user": "The search returned `[\"commands.md\", \"ipc.md\"]`. Please read the commands documentation.",
        "assistant": """```json
{
  "tool": "cn_a__cn_c_read_doc_page",
  "arguments": {
    "library": "tauri",
    "page": "commands.md"
  }
}
```"""
    },
    # Example 3: Matrix B (XML) - Final edit
    {
        "system": "You are an elite Workspace Systems Architect. You master the ChaosNexus Anvil MCP. You autonomously discover and leverage capabilities provided by your workspace environment.",
        "user": "The documentation states you use `#[tauri::command]` in Rust and `invoke('cmd_name')` in frontend. Implement this for a 'greet' command.",
        "assistant": """<file path="src-tauri/src/main.rs" action="MODIFY">
#[tauri::command]
fn greet(name: &str) -> String {
    format!("Hello, {}!", name)
}
</file>
<file path="src/App.svelte" action="MODIFY">
<script>
    import { invoke } from '@tauri-apps/api/core';
    let name = '';
    let greeting = '';
    async function doGreet() {
        greeting = await invoke('greet', { name });
    }
</script>
</file>"""
    },
    # Example 4: Matrix C (JSON) - Autonomous search docs for Svelte 5 Runes
    {
        "system": "You are an elite Workspace Systems Architect. You master the ChaosNexus Anvil MCP. You autonomously discover and leverage capabilities provided by your workspace environment.",
        "user": "How do I define reactive state using the new Svelte 5 syntax? I need a counter.",
        "assistant": """```json
{
  "tool": "cn_a__cn_c_search_docs",
  "arguments": {
    "library": "svelte",
    "query": "runes state"
  }
}
```"""
    },
    # Example 5: Matrix C (JSON) - Final edit
    {
        "system": "You are an elite Workspace Systems Architect. You master the ChaosNexus Anvil MCP. You autonomously discover and leverage capabilities provided by your workspace environment.",
        "user": "The documentation shows you use `let count = $state(0);`. Implement a counter component.",
        "assistant": """```json
{
  "tool_calls": [
    {
      "name": "edit_file",
      "arguments": {
        "path": "src/Counter.svelte",
        "action": "CREATE",
        "content": "<script>\\n    let count = $state(0);\\n</script>\\n\\n<button onclick={() => count++}>Count: {count}</button>"
      }
    }
  ]
}
```"""
    }
]

def append_to_jsonl(filepath, examples):
    if not os.path.exists(filepath):
        print(f"Skipping {filepath} (does not exist)")
        return
    with open(filepath, 'a') as f:
        for ex in examples:
            if "system" in ex:
                line = {
                    "messages": [
                        {"role": "system", "content": ex["system"]},
                        {"role": "user", "content": ex["user"]},
                        {"role": "assistant", "content": ex["assistant"]}
                    ]
                }
                f.write(json.dumps(line) + "\n")

def append_to_alpaca(filepath, examples):
    if not os.path.exists(filepath):
        print(f"Skipping {filepath} (does not exist)")
        return
    with open(filepath, 'r') as f:
        data = json.load(f)
    for ex in examples:
        if "system" in ex:
            data.append({
                "instruction": ex["system"],
                "input": ex["user"],
                "output": ex["assistant"]
            })
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)

print("Injecting full stack documentation querying data...")
append_to_jsonl(FULL_JSONL, full_stack_examples)
append_to_alpaca(FULL_ALPACA, full_stack_examples)
print("Done.")
