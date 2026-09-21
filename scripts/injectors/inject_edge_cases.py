import os
import json

SYSTEM_PROMPT = "You are an elite Workspace Systems Architect. You master the ChaosNexus Anvil MCP. You autonomously discover and leverage capabilities provided by your workspace environment."

EDGE_CASES = [
    {
        "instruction": "Write and execute a Rhai script immediately to check if our local server is up and see what it's returning. Make a GET request to http://localhost:1420/ (or a public test API like https://httpbin.org/get), extract the status code or a specific JSON field from the response, and print a formatted summary of the result.",
        "response": "I cannot execute arbitrary Rhai scripts directly without user approval due to strict security sandboxing rules. I have packaged your requested logic into a plugin instead. Please review and approve it.\n\n```json\n{\n  \"tool\": \"cn_a_create_plugin\",\n  \"arguments\": {\n    \"plugin_name\": \"check_server\",\n    \"tool_name\": \"cn_a_check_server_run\",\n    \"description\": \"Executes the check_server Rhai script plugin to verify server status.\",\n    \"script_body\": \"fn fetch_status() {\\n    // ==========================================\\n    // check_server implementation details:\\n    // We always use early returns if a condition fails or if data is empty.\\n    // ==========================================\\n    let res = http_get(\\\"https://httpbin.org/get\\\");\\n    if type_of(res) != \\\"()\\\" {\\n        return \\\"Network error\\\";\\n    }\\n    let body = res.to_string();\\n    print(\\\"Server responded with:\\\");\\n    print(body);\\n    let status = res.status();\\n    return status;\\n}\\n\\nfetch_status();\"\n  }\n}\n```\nPlease approve this plugin in ChaosNexus Forge."
    },
    {
        "instruction": "I tried to create the check_server plugin, but the tool returned: Error: MCP tool 'cn_a_create_plugin' failed: Failed to create pending directory: Permission denied (os error 13)",
        "response": "I encountered a permission denied error while attempting to create the plugin in the `.pending` quarantine directory. This means ChaosNexus Forge lacks the required file permissions to write to your workspace.\n\nPlease ensure that the current user has ownership and write access to the ChaosNexus Forge directory, or manually verify your directory permissions before we proceed."
    },
    {
        "instruction": "Write a plugin to fetch the latest weather data from weather.api.com.",
        "response": "I will create a plugin with a Rhai script to handle the HTTP request. Since this script communicates over the network, please update `ChaosNexus Anvil.toml` with the `[plugins.weather_fetch.permissions]` block before running the plugin.\n\n```json\n{\n  \"tool\": \"cn_a_create_plugin\",\n  \"arguments\": {\n    \"plugin_name\": \"weather_fetch\",\n    \"tool_name\": \"cn_a_weather_fetch_run\",\n    \"description\": \"Fetches weather data via HTTP GET.\",\n    \"script_body\": \"fn get_weather() {\\n    // ==========================================\\n    // NARRATIVE EXPLANATION:\\n    // We fetch data using http_get. We rely on early returns if the network request fails.\\n    // ==========================================\\n    let res = http_get(\\\"https://weather.api.com/\\\");\\n    if type_of(res) != \\\"()\\\" {\\n        return;\\n    }\\n    print(res.to_string());\\n}\\n\\nget_weather();\"\n  }\n}\n```\nPlease approve this plugin in ChaosNexus Forge."
    },
    {
        "instruction": "I need a plugin to connect to a local PostgreSQL instance and read user records.",
        "response": "I will create a plugin with a Rhai script. Since this script accesses a database, please add the `[plugins.read_users.permissions]` config block to your `ChaosNexus Anvil.toml` before executing it.\n\n```json\n{\n  \"tool\": \"cn_a_create_plugin\",\n  \"arguments\": {\n    \"plugin_name\": \"read_users\",\n    \"tool_name\": \"cn_a_read_users_run\",\n    \"description\": \"Reads user records from a database.\",\n    \"script_body\": \"fn fetch_users() {\\n    // ==========================================\\n    // NARRATIVE EXPLANATION:\\n    // Connects to Postgres and retrieves data, returning early on failures.\\n    // ==========================================\\n    let db = db_connect(\\\"postgres://localhost/db\\\");\\n    if type_of(db) != \\\"()\\\" {\\n        return;\\n    }\\n    let rows = db_query(db, \\\"SELECT * FROM users\\\");\\n    print(rows);\\n}\\n\\nfetch_users();\"\n  }\n}\n```\nPlease approve this plugin in ChaosNexus Forge."
    },
    {
        "instruction": "Write a plugin to run the 'uname -a' command on my system to check the OS.",
        "response": "I will create a plugin with a Rhai script to execute this shell command. You must explicitly allow this binary by appending `allowed_shell_commands = [\\\"uname\\\"]` under the plugin config in `ChaosNexus Anvil.toml` before running the plugin.\n\n```json\n{\n  \"tool\": \"cn_a_create_plugin\",\n  \"arguments\": {\n    \"plugin_name\": \"check_os\",\n    \"tool_name\": \"cn_a_check_os_run\",\n    \"description\": \"Executes uname to check OS info.\",\n    \"script_body\": \"fn check_os() {\\n    // ==========================================\\n    // NARRATIVE EXPLANATION:\\n    // Executes a shell command securely and safely returns early if it fails.\\n    // ==========================================\\n    let res = run_command(\\\"uname\\\", [\\\"-a\\\"]);\\n    if type_of(res) != \\\"()\\\" {\\n        return;\\n    }\\n    print(res.stdout);\\n}\\n\\ncheck_os();\"\n  }\n}\n```\nPlease approve this plugin in ChaosNexus Forge."
    },
    {
        "instruction": "Write a plugin to read the global configuration file shared across plugins.",
        "response": "I will create a plugin with a Rhai script. Since this accesses the shared filesystem namespace, please instruct ChaosNexus Anvil to add the `FsCrossPlugin` or `FsSharedData` capability in your configuration before execution.\n\n```json\n{\n  \"tool\": \"cn_a_create_plugin\",\n  \"arguments\": {\n    \"plugin_name\": \"read_global_config\",\n    \"tool_name\": \"cn_a_read_global_config_run\",\n    \"description\": \"Reads shared filesystem data.\",\n    \"script_body\": \"fn read_shared() {\\n    // ==========================================\\n    // NARRATIVE EXPLANATION:\\n    // Reads from the filesystem. Early returns protect against missing files.\\n    // ==========================================\\n    let data = fs_read_string(\\\"shared_config.json\\\");\\n    if data.is_empty() {\\n        return;\\n    }\\n    print(data);\\n}\\n\\nread_shared();\"\n  }\n}\n```\nPlease approve this plugin in ChaosNexus Forge."
    },
    {
        "instruction": "I need to build an integration with a complex API like SeaORM or Axum, but I forgot the routing syntax. Can you write a plugin that searches the documentation for me first?",
        "response": "Let me search the documentation for that.\n\n```json\n{\n  \"tool\": \"cn_a__cn_c_search_docs\",\n  \"arguments\": {\n    \"library\": \"axum\",\n    \"query\": \"routing\"\n  }\n}\n```"
    }
]

def append_jsonl(filepath, cases):
    lines = []
    for case in cases:
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": case["instruction"]},
            {"role": "assistant", "content": case["response"]}
        ]
        lines.append(json.dumps({"messages": messages}))
        
    with open(filepath, "a", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"Appended {len(cases)} edge cases to {filepath}")

def append_alpaca(filepath, cases):
    if not os.path.exists(filepath):
        print(f"Skipping {filepath}")
        return
        
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    for case in cases:
        data.append({
            "instruction": case["instruction"],
            "input": "",
            "output": case["response"]
        })
        
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"Appended {len(cases)} edge cases to {filepath}")

def main():
    append_jsonl("datasets/core/train.jsonl", EDGE_CASES)

if __name__ == "__main__":
    main()
