import json
import os
import re

SYSTEM_PROMPT = """You are ChaosNexus Tuned, the industrial automation brain of the Tuned Chaos ecosystem.

# GLOBAL RULES
1. **NARRATIVE COMMENTING**: All generated code (whether Rhai scripts, Rust, or Svelte UI components) MUST include extremely thorough, non-technical friendly, narrative-style comments explaining the "why" and "how" behind the logic. This applies to all matrices (A, B, and C). The code should be easily understandable by a beginner.

# MATRIX C: AGENTIC JSON TOOL PROTOCOL (Unified / Tool-calling)
1. You must output a JSON object representing tool calls.
2. Format: `{"tool_calls": [{"name": "tool_name", "arguments": {"arg1": "val1"}}]}`
3. Do NOT include conversational text or markdown blocks. Only output valid JSON.
4. **DOCUMENTATION AUTONOMY**: If a task requires using an unfamiliar API or complex UI framework behavior (e.g. Svelte 5 runes, Tauri IPC, Axum, SeaORM), you MUST autonomously emit an independent JSON tool call (e.g. `{"tool_calls": [{"name": "cn_c_search_docs", ...}]}`) before committing any changes.
"""

def make_turn(role, content):
    return {"role": role, "content": content}

def make_sharegpt_turn(from_role, value):
    return {"from": from_role, "value": value}

def tool_call(name, args):
    return make_turn("assistant", json.dumps({"tool_calls": [{"name": name, "arguments": args}]}))

def tool_response(name, result):
    # Depending on format, tool responses might be formatted differently, but standard ChatML can just be user/tool role.
    return make_turn("tool", json.dumps({"tool_name": name, "result": result}))

# The 18 Scenarios hardcoded for perfection.
scenarios = [
    {
        "id": 1,
        "title": "The Simple Test: Web Request & JSON Parsing",
        "prompt": "I need to check if our local server is up and see what it's returning. Write and execute a Rhai script that makes a GET request to http://localhost:1420/ (or a public test API like https://httpbin.org/get), extracts the status code or a specific JSON field from the response, and prints a formatted summary of the result.",
        "plugin_name": "check_server",
        "script": """// We use the native HTTP client to perform a GET request
let response = http_get("http://localhost:1420/");
// We extract the status code and parse the JSON payload
print("Server Status: " + response.status);
let body = parse_json(response.body);
print("Response Data: " + body);
""",
        "docs_search": "http_get json"
    },
    {
        "id": 2,
        "title": "The Intermediate Test: Multi-Step File Processing & Filtering",
        "prompt": "We have several configuration and log files in our workspace. Write and execute a Rhai script that searches for any .toml or .json files in the current directory, reads their contents, finds lines containing the word 'port' or 'host', and writes a consolidated summary of these configuration lines to a new file called ports_found.txt.",
        "plugin_name": "config_scanner",
        "script": """// Scan directory for config files
let files = fs_list_dir(".");
let summary = "";
for file in files {
    if file.ends_with(".toml") || file.ends_with(".json") {
        let content = fs_read(file);
        let lines = content.split("\\n");
        for line in lines {
            if line.contains("port") || line.contains("host") {
                summary += file + ": " + line + "\\n";
            }
        }
    }
}
// Write the aggregated summary to the target file
fs_write("ports_found.txt", summary);
""",
        "docs_search": "fs_list_dir fs_read fs_write"
    },
    {
        "id": 3,
        "title": "The Complex Test: Custom Algorithm / Mathematical Simulation",
        "prompt": "I want to run a quick performance simulation. Write a Rhai script that defines a custom function to calculate the first 15 Fibonacci numbers, stores them in an array, filters out the even numbers, computes the average of the remaining odd numbers, and prints the final calculated average with a clear explanation of each step.",
        "plugin_name": "fib_sim",
        "script": """// Calculate the first 15 fibonacci numbers
fn calculate_fib(n) {
    if n <= 1 { return n; }
    return calculate_fib(n - 1) + calculate_fib(n - 2);
}
let fibs = [];
for i in 0..15 { fibs.push(calculate_fib(i)); }
// Filter even and compute average of odds
let sum = 0;
let count = 0;
for num in fibs {
    if num % 2 != 0 {
        sum += num;
        count += 1;
    }
}
print("Average of odds: " + (sum / count));
""",
        "docs_search": None
    },
    {
        "id": 4,
        "title": "The Autonomous Test: Unfamiliar API Discovery",
        "prompt": "I need a new ChaosNexus Anvil plugin that connects to our local SQLite database (db.sqlite) to pull the top 10 most recent user logins. I'm not sure if ChaosNexus Anvil has a native SQLite driver or if we need to spin up an external MCP server dynamically using npx. Please figure out the correct approach from the documentation and write the plugin for me.",
        "plugin_name": "sqlite_logins",
        "script": """// Use the native db_execute tool to query the local SQLite database
let rows = db_query("sqlite://db.sqlite", "SELECT * FROM logins ORDER BY date DESC LIMIT 10");
print("Top Logins: " + rows);
""",
        "docs_search": "sqlite database db_query db_execute"
    },
    {
        "id": 5,
        "title": "The Security & Persistence Test: Crypto and KV Store",
        "prompt": "I need to securely store an access token. Write a Rhai script that takes a raw string token, hashes it using SHA256, encodes the resulting hash in Base64, and then stores the encoded string into the native ChaosNexus Anvil KV store under the key 'secure_token'. Finally, retrieve the key from the store and print it to verify it was saved correctly.",
        "plugin_name": "secure_kv",
        "script": """// Hash the token using SHA256 and encode it in Base64
let hash = hash_sha256("my_secret_token");
let encoded = base64_encode(hash);
// Store the encoded hash in the global KV store
kv_set("secure_token", encoded);
// Retrieve and print to verify
let retrieved = kv_get("secure_token");
print("Retrieved Token Hash: " + retrieved);
""",
        "docs_search": "crypto sha256 base64 kv_set kv_get"
    },
    {
        "id": 7,
        "title": "The Sandbox Security Gate Test: Deny-by-Default Validation",
        "prompt": "I need a ChaosNexus Anvil plugin that runs the `curl` command to fetch data from `https://api.github.com/zen`. Since I know ChaosNexus Anvil blocks shell commands and network requests by default, please provide the exact configuration changes needed in `ChaosNexus Anvil.toml` to allow this, alongside the plugin code itself.",
        "plugin_name": "curl_github",
        "script": """// Shell command execution to fetch the zen text
let result = run_command("curl", ["-s", "https://api.github.com/zen"]);
print("GitHub Zen: " + result);
""",
        "docs_search": "run_command shell capabilities",
        "toml": """[plugin_permissions.curl_github]
allowed_shell_commands = ["curl"]
"""
    },
    {
        "id": 8,
        "title": "The Pending Plugin Workflow Test: Human-In-The-Loop Approval",
        "prompt": "Write a Rhai script that uses `cn_a_install_plugin` to fetch a community plugin called \"system_monitor\". Once you've written the script, explain to me exactly how I approve and edit the plugin in the ChaosNexus Forge IDE before it goes live.",
        "plugin_name": "install_sysmon",
        "script": """// Call the native installation routine to fetch the plugin
cn_a_install_plugin("system_monitor");
""",
        "docs_search": "cn_a_install_plugin"
    }
]

# We will generate the 7 core scenarios here to ensure quality. The remaining can be extrapolated by the model later.

def generate_conversation(scenario):
    messages = [make_turn("system", SYSTEM_PROMPT)]
    messages.append(make_turn("user", scenario["prompt"]))
    
    # Discovery Phase
    if scenario.get("docs_search"):
        messages.append(tool_call("cn_c_search_docs", {"query": scenario["docs_search"]}))
        messages.append(tool_response("cn_c_search_docs", "Found relevant documentation for: " + scenario["docs_search"]))
        
    # Creation Phase
    args = {
        "plugin_name": scenario["plugin_name"],
        "tool_name": f"{scenario['plugin_name']}_tool",
        "description": scenario["title"],
        "script_body": scenario["script"]
    }
    if scenario.get("toml"):
        args["custom_toml"] = scenario["toml"]
        
    messages.append(tool_call("cn_a_create_plugin", args))
    
    # Wait for User Approval
    messages.append(tool_response("cn_a_create_plugin", f"PENDING human approval in ChaosNexus Forge.\\n\\nStaged quarantined plugin at .pending/{scenario['plugin_name']}.rhai"))
    
    messages.append(make_turn("assistant", "I have created the plugin and it is now in a pending state. Please review and approve it inside the ChaosNexus Forge IDE. Once you approve it, let me know."))
    
    # Execution / Hot Reload
    messages.append(make_turn("user", "Approved."))
    messages.append(tool_call("cn_a_reload_plugins", {}))
    messages.append(tool_response("cn_a_reload_plugins", "Plugins reloaded successfully."))
    messages.append(make_turn("assistant", "The plugins have been hot-reloaded successfully. Your new tool is now active and ready to be used."))
    
    # Generate equivalent ShareGPT conversation
    sharegpt_conv = []
    for msg in messages:
        if msg["role"] == "system":
            sharegpt_conv.append(make_sharegpt_turn("system", msg["content"]))
        elif msg["role"] == "user":
            sharegpt_conv.append(make_sharegpt_turn("human", msg["content"]))
        elif msg["role"] == "assistant":
            sharegpt_conv.append(make_sharegpt_turn("gpt", msg["content"]))
        elif msg["role"] == "tool":
            # Map tool responses to human or keep as tool if framework supports it. 
            # We'll map to 'tool' for completeness, though many frameworks accept 'observation' or just stringify it.
            sharegpt_conv.append(make_sharegpt_turn("tool", msg["content"]))

    return {"messages": messages, "sharegpt": {"conversations": sharegpt_conv}}

def main():
    os.makedirs("datasets/core", exist_ok=True)
    
    train_data = []
    alpaca_data = []
    sharegpt_data = []
    
    for sc in scenarios:
        result = generate_conversation(sc)
        train_data.append({"messages": result["messages"]})
        sharegpt_data.append(result["sharegpt"])
        
        # Alpaca approximation
        alpaca = {
            "instruction": sc["prompt"],
            "input": "",
            "output": json.dumps({"tool_calls": [{"name": "cn_a_create_plugin", "arguments": {"plugin_name": sc["plugin_name"], "script_body": sc["script"]}}]})
        }
        alpaca_data.append(alpaca)
        
    with open("datasets/core/train.jsonl", "w") as f:
        for item in train_data:
            f.write(json.dumps(item) + "\n")
            
    with open("datasets/core/train_alpaca.json", "w") as f:
        json.dump(alpaca_data, f, indent=2)
        
    with open("datasets/core/train_sharegpt.json", "w") as f:
        json.dump(sharegpt_data, f, indent=2)
        
    print("Successfully generated datasets/core/train.jsonl, datasets/core/train_alpaca.json, and datasets/core/train_sharegpt.json")

if __name__ == "__main__":
    main()
