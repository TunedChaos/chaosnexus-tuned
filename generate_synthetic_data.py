import os
import json
import time
from google import genai
from google.genai import types
from tenacity import Retrying, stop_after_attempt, wait_exponential

# Ensure the virtual environment's google-genai is used
# Run this script using: .venv/bin/python generate_synthetic_data.py

def make_turn(role, content):
    return {"role": role, "content": content}

def make_sharegpt_turn(from_role, value):
    return {"from": from_role, "value": value}

def tool_call(name, args):
    return make_turn("assistant", json.dumps({"tool_calls": [{"name": name, "arguments": args}]}))

def tool_response(name, result):
    return make_turn("tool", json.dumps({"tool_name": name, "result": result}))

SYSTEM_PROMPT = """You are ChaosNexus Tuned, the industrial automation brain of the Tuned Chaos ecosystem.

# GLOBAL RULES
1. **NARRATIVE COMMENTING**: All generated code (whether Rhai scripts, Rust, or Svelte UI components) MUST include extremely thorough, non-technical friendly, narrative-style comments explaining the "why" and "how" behind the logic. This applies to all matrices (A, B, and C). The code should be easily understandable by a beginner.

# MATRIX C: AGENTIC JSON TOOL PROTOCOL (Unified / Tool-calling)
1. You must output a JSON object representing tool calls.
2. Format: `{"tool_calls": [{"name": "tool_name", "arguments": {"arg1": "val1"}}]}`
3. Do NOT include conversational text or markdown blocks. Only output valid JSON.
4. **DOCUMENTATION AUTONOMY**: If a task requires using an unfamiliar API or complex framework, you must autonomously figure it out by leaning on ChaosNexus Anvil (`cn_a_` tools). You should attempt to find local documentation first (e.g., querying available MCP servers or reading locally synced documentation via `cn_a_` tools). ChaosNexus Codex (`cn_c_`) may not always be available, so do not blindly assume it is there. If the user provides a link or reference (e.g., a documentation URL or a GitHub repo), you must STILL attempt to find and verify the documentation locally first. However, if it cannot be found locally, you are allowed to use that link to "drill down", clone the repository, or fetch the web documentation in order to dynamically increase the local knowledgebase within ChaosNexus Codex (since `cn_c` supports adding to itself on the fly) before committing any code changes.
"""

# Hardcoded seed scenarios for the prompt
SEED_EXAMPLES = """
Example 1:
User: "I need to check if our local server is up and see what it's returning. Write and execute a Rhai script that makes a GET request to http://localhost:1420/, extracts the status code, and prints a formatted summary."
Docs Search Needed: Yes (query: "http_get json")
Plugin Name: "check_server"
Script Body:
// We use the native HTTP client to perform a GET request
let response = http_get("http://localhost:1420/");
// We extract the status code and parse the JSON payload
print("Server Status: " + response.status);
let body = parse_json(response.body);
print("Response Data: " + body);

Example 2:
User: "We have several configuration and log files in our workspace. Write and execute a Rhai script that searches for any .toml or .json files in the current directory, reads their contents, finds lines containing the word 'port' or 'host', and writes a consolidated summary of these configuration lines to a new file called ports_found.txt."
Docs Search Needed: Yes (query: "fs_list_dir fs_read fs_write")
Plugin Name: "config_scanner"
Script Body:
// Scan directory for config files
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

Example 3:
User: "I need a ChaosNexus Anvil plugin that runs the `curl` command to fetch data from `https://api.github.com/zen`. Since I know ChaosNexus Anvil blocks shell commands and network requests by default, please provide the exact configuration changes needed in `ChaosNexus Anvil.toml` to allow this, alongside the plugin code itself."
Docs Search Needed: Yes (query: "run_command shell capabilities")
Plugin Name: "curl_github"
Custom TOML: 
[plugin_permissions.curl_github]
allowed_shell_commands = ["curl"]
Script Body:
// Shell command execution to fetch the zen text
let result = run_command("curl", ["-s", "https://api.github.com/zen"]);
print("GitHub Zen: " + result);
"""

GEMINI_PROMPT = """You are an expert AI data generation system. I need you to act as a "Teacher" model to generate synthetic training data for a smaller 8B parameter model.
The 8B model will act as "ChaosNexus Tuned", an industrial automation brain that uses Rhai scripts to interact with a system called ChaosNexus Anvil.

Your task is to generate 5 completely new, diverse, and complex scenarios that test the agent's ability to:
1. Identify if it needs to discover capabilities or search documentation first. Emphasize "figuring things out" by leaning on ChaosNexus Anvil (`cn_a_` tools). Ensure the agent attempts to find local sources of information first. If the user provides a URL or repository link, the agent MUST check locally first, but if the local search fails, the agent must drill down into that link (e.g. cloning a git repo or doing a web search) to "get" the external documentation and dynamically add it to Codex's knowledgebase on the fly (since Codex supports dynamic expansion). Ensure the agent still operates securely and sovereignly.
2. Write a Rhai script with HIGHLY descriptive narrative comments (Mandatory).
3. Optionally require a custom TOML permissions file (for things like shell commands or network requests).

For each scenario, output a raw JSON object within an array. The JSON schema must strictly be:
[
  {
    "prompt": "The user's initial request. Vary the tone (polite, demanding, vague).",
    "docs_search": "The query to search docs with, or null if simple enough.",
    "plugin_name": "A short snake_case name for the plugin",
    "script": "The full Rhai script containing narrative comments.",
    "toml": "The string contents of the TOML file if permissions are needed, else null."
  }
]

Here are 3 seed examples for inspiration:
""" + SEED_EXAMPLES + """

Generate 5 NEW scenarios. Focus on system automation, log parsing, SQLite interactions, HTTP requests, KV store, and data manipulation.
OUTPUT ONLY VALID JSON. Do not include markdown formatting like ```json.
"""

def build_conversation(scenario):
    messages = [make_turn("system", SYSTEM_PROMPT)]
    messages.append(make_turn("user", scenario["prompt"]))
    
    # Discovery Phase
    if scenario.get("docs_search"):
        messages.append(tool_call("cn_a__cn_c_search_docs", {"query": scenario["docs_search"]}))
        messages.append(tool_response("cn_a__cn_c_search_docs", "Found relevant documentation for: " + scenario["docs_search"]))
        
    # Creation Phase
    args = {
        "plugin_name": scenario["plugin_name"],
        "tool_name": f"{scenario['plugin_name']}_tool",
        "description": "Generated plugin.",
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
    
    # Generate ShareGPT
    sharegpt_conv = []
    for msg in messages:
        if msg["role"] == "system":
            sharegpt_conv.append(make_sharegpt_turn("system", msg["content"]))
        elif msg["role"] == "user":
            sharegpt_conv.append(make_sharegpt_turn("human", msg["content"]))
        elif msg["role"] == "assistant":
            sharegpt_conv.append(make_sharegpt_turn("gpt", msg["content"]))
        elif msg["role"] == "tool":
            sharegpt_conv.append(make_sharegpt_turn("tool", msg["content"]))

    return {"messages": messages}, {"conversations": sharegpt_conv}

def main():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable not set.")
        return

    client = genai.Client()
    
    train_data = []
    sharegpt_data = []
    alpaca_data = []

    print("Generating synthetic scenarios using gemini-3.1-pro-preview...")
    import random
    topics = [
        "file system manipulation and log parsing",
        "HTTP requests and API integrations",
        "SQLite database querying and data migration",
        "KV store operations and caching",
        "mathematical algorithms and data transformations",
        "system monitoring and shell command execution",
        "network diagnostics and ping/traceroute",
        "cryptography, hashing, and encoding",
        "date/time manipulation and scheduling logic",
        "text processing, regex, and string extraction",
        "JSON/TOML configuration parsing and generation",
        "Rhai BigInt mathematical calculations",
        "Scientific libraries in Rhai for advanced computing"
    ]
    
    total_batches = 100
    
    for i in range(total_batches):
        current_topic = random.choice(topics)
        print(f"Batch {i+1}/{total_batches} (Topic: {current_topic})...")
        
        dynamic_prompt = GEMINI_PROMPT + f"\nFor this specific batch, heavily bias the scenarios towards: {current_topic}."
        
        try:
            for attempt in Retrying(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=2, max=10)):
                with attempt:
                    response = client.models.generate_content(
                        model='gemini-3.1-pro-preview',
                        contents=dynamic_prompt,
                        config=types.GenerateContentConfig(
                            temperature=0.9, # Higher temp for diversity
                        )
                    )
                    
                    raw_text = response.text.strip()
                    if raw_text.startswith("```json"):
                        raw_text = raw_text[7:]
                    if raw_text.endswith("```"):
                        raw_text = raw_text[:-3]
                        
                    scenarios = json.loads(raw_text)
                    
                    for sc in scenarios:
                        chatml, sharegpt = build_conversation(sc)
                        train_data.append(chatml)
                        sharegpt_data.append(sharegpt)
                        
                        alpaca_data.append({
                            "instruction": sc["prompt"],
                            "input": "",
                            "output": json.dumps({"tool_calls": [{"name": "cn_a_create_plugin", "arguments": {"plugin_name": sc["plugin_name"], "script_body": sc["script"]}}]})
                        })
                    
                    time.sleep(2) # Prevent rate limiting
        except Exception as e:
            print(f"Failed to generate batch {i+1} after multiple retries: {e}")

    # Append to existing files if they exist
    os.makedirs("datasets/augmented", exist_ok=True)
    
    with open("datasets/augmented/train_augmented.jsonl", "w") as f:
        for item in train_data:
            f.write(json.dumps(item) + "\n")
            
    with open("datasets/augmented/train_sharegpt_augmented.json", "w") as f:
        json.dump(sharegpt_data, f, indent=2)
        
    with open("datasets/augmented/train_alpaca_augmented.json", "w") as f:
        json.dump(alpaca_data, f, indent=2)

    print(f"Success! Generated {len(train_data)} new augmented scenarios.")

if __name__ == "__main__":
    main()
