import json
import os

CORE_JSONL = "datasets/core/train.jsonl"
CORE_ALPACA = "datasets/core/train_alpaca.json"

final_examples = [
    # Example 1: File System (Cross-Plugin)
    {
        "system": "You are a Rhai expert.",
        "user": "I need to read a log file from another plugin (log_manager), parse out all the WARNING lines using regex, and then write them back to my plugin's shared data folder as warnings.txt.",
        "assistant": """I can accomplish this using the `fs_read`, `regex_match`, and `fs_data_write` functions. I will request the `fs_cross_plugin` and `fs_shared_data` capabilities when creating the plugin.

```json
{
  "tool": "cn_a_create_plugin",
  "arguments": {
    "plugin_name": "log_parser",
    "tool_name": "cn_a_log_parser_extract_warnings",
    "description": "Extracts warnings from log_manager's files and saves them to local shared data.",
    "requested_capabilities": ["fs_cross_plugin", "fs_shared_data"],
    "script_body": "fn extract_warnings() {\\n    let content = fs_read(\\\"../log_manager/logs.txt\\\");\\n    if type_of(content) != \\\"String\\\" {\\n        throw \\\"Failed to read log file.\\\";\\n    }\\n    \\n    let lines = content.split(\\\"\\\\n\\\");\\n    let warnings = [];\\n    for line in lines {\\n        if regex_match(\\\"^WARNING:\\\", line) {\\n            warnings.push(line);\\n        }\\n    }\\n    \\n    let output = warnings.join(\\\"\\\\n\\\");\\n    let write_res = fs_data_write(\\\"warnings.txt\\\", output);\\n    if type_of(write_res) != \\\"()\\\" {\\n        throw \\\"Failed to write warnings.txt\\\";\\n    }\\n    \\\"Successfully extracted \\\" + warnings.len() + \\\" warnings.\\\"\\n}"
  }
}
```"""
    },
    # Example 2: DB Query / Execute
    {
        "system": "You are a Rhai expert.",
        "user": "I need to connect to my PostgreSQL database (postgres://user:pass@localhost/db), insert a new record for a user named 'Alice', and then select all users to return them as JSON.",
        "assistant": """I can do this using the `db_connect`, `db_execute`, and `db_query` APIs. First, I will request the `db_external` capability. You will also need to allow external database access for this plugin in `<workspace_root>/anvil.toml`.

Please add the following configuration:
```toml
[plugins.my_plugin.permissions]
allowed_database_urls = ["postgres://user:pass@localhost/db"]
allowed_database_ops = ["C", "R"]
```

```json
{
  "tool": "cn_a_create_plugin",
  "arguments": {
    "plugin_name": "my_plugin",
    "tool_name": "cn_a_my_plugin_manage_users",
    "description": "Inserts and retrieves users from Postgres.",
    "requested_capabilities": ["db_external"],
    "script_body": "fn manage_users() {\\n    let conn_res = db_connect(\\\"pg_main\\\", \\\"postgres://user:pass@localhost/db\\\");\\n    if type_of(conn_res) != \\\"()\\\" { throw \\\"DB Connection failed\\\"; }\\n    \\n    let exec_res = db_execute(\\\"pg_main\\\", \\\"INSERT INTO users (name) VALUES ($1)\\\", [\\\"Alice\\\"]);\\n    if type_of(exec_res) != \\\"i64\\\" { throw \\\"Execute failed\\\"; }\\n    \\n    let rows = db_query(\\\"pg_main\\\", \\\"SELECT * FROM users\\\", []);\\n    to_json(rows)\\n}"
  }
}
```"""
    },
    # Example 3: Config, Env, Time, and Complex Rhai features (maps)
    {
        "system": "You are a Rhai expert.",
        "user": "I want to load our TOML config from 'settings.toml', fetch the 'API_KEY' environment variable, and then return a map containing the current system time and the config keys.",
        "assistant": """I will use `load_config`, `get_env`, and `system_time`. I will construct a standard Rhai object map to return the consolidated data. Since we are reading a local plugin file, no special capabilities are required other than the default sandbox access.

```json
{
  "tool": "cn_a_create_plugin",
  "arguments": {
    "plugin_name": "config_reader",
    "tool_name": "cn_a_config_reader_get_info",
    "description": "Reads config and env vars and returns them with a timestamp.",
    "script_body": "fn get_info() {\\n    let conf = load_config(\\\"settings.toml\\\");\\n    if type_of(conf) != \\\"map\\\" { throw \\\"Failed to load config\\\"; }\\n    \\n    let key = get_env(\\\"API_KEY\\\");\\n    let now = system_time();\\n    \\n    let result = #{};\\n    result.timestamp = now;\\n    result.has_api_key = key != \\\"\\\";\\n    result.config_keys = conf.keys();\\n    \\n    result\\n}"
  }
}
```"""
    },
    # Example 4: Autonomous Documentation Fetching
    {
        "system": "You are a Rhai expert.",
        "user": "I forgot how to use the 'notify' library in Rust to watch for file changes. Can you look it up for me?",
        "assistant": """```json
{
  "tool": "cn_a__cn_c_search_docs",
  "arguments": {
    "library": "notify",
    "query": ".*"
  }
}
```"""
    },
    # Example 5: Follow-up to autonomous documentation fetching
    {
        "system": "You are a Rhai expert.",
        "user": "The search returned `[\"tutorial.md\", \"advanced.md\"]`. Please read the tutorial.",
        "assistant": """```json
{
  "tool": "cn_a__cn_c_read_doc_page",
  "arguments": {
    "library": "notify",
    "page": "tutorial.md"
  }
}
```"""
    }
]

def append_to_jsonl(filepath, examples):
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

print("Injecting final capabilities data...")
append_to_jsonl(CORE_JSONL, final_examples)
print("Done.")
