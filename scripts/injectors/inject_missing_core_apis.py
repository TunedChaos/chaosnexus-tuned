import json
import os

CORE_JSONL = "datasets/core/train.jsonl"
CORE_ALPACA = "datasets/core/train_alpaca.json"
FULL_JSONL = "datasets/full_stack/train.jsonl"
FULL_ALPACA = "datasets/full_stack/train_alpaca.json"

missing_core_examples = [
    # Group 1: Core state, globals, timers, logging
    {
        "system": "You are a Rhai expert.",
        "user": "I need a plugin to set a global variable 'app_mode' to 'production', log an info message, and read a cvar named 'max_retries'. Then use sleep to pause for 1 second.",
        "assistant": """```json
{
  "tool": "cn_a_create_plugin",
  "arguments": {
    "plugin_name": "core_demo",
    "tool_name": "cn_a_core_demo_run",
    "description": "Demonstrates globals, cvars, and logging.",
    "script_body": "fn run_core() {\\n    set_global(\\\"app_mode\\\", \\\"production\\\");\\n    log_info(\\\"Set app_mode to production\\\");\\n    \\n    let retries = get_cvar(\\\"max_retries\\\");\\n    log_debug(\\\"Retries: \\\" + retries);\\n    \\n    sleep(1000);\\n    \\n    let mode = get_global(\\\"app_mode\\\");\\n    mode\\n}\\n\\nrun_core()"
  }
}
```"""
    },
    # Group 2: Native functions & system time
    {
        "system": "You are a Rhai expert.",
        "user": "Register a new native function named 'get_sys_info' that returns the current OS and system time. Then call it using call_native.",
        "assistant": """```json
{
  "tool": "cn_a_create_plugin",
  "arguments": {
    "plugin_name": "sys_info_plugin",
    "tool_name": "cn_a_sys_info_plugin_register",
    "description": "Registers and calls a native sys_info function.",
    "script_body": "fn register_and_call() {\\n    register_native(\\\"get_sys_info\\\", \\\"fn_get_sys_info\\\");\\n    \\n    let res = call_native(\\\"get_sys_info\\\", []);\\n    res\\n}\\n\\nfn fn_get_sys_info() {\\n    let os = sys_os();\\n    let ts = system_time();\\n    #{ os: os, time: ts }\\n}\\n\\nregister_and_call()"
  }
}
```"""
    },
    # Group 3: Crypto, Network commands
    {
        "system": "You are a Rhai expert.",
        "user": "Get the current time from an NTP server 'pool.ntp.org', base64 encode it, calculate the md5 hash of 'test', and sha256 hash of 'data'. Also run a simple shell command 'echo hello'.",
        "assistant": """Before creating the plugin, you must grant permissions for network access and command execution in `<workspace_root>/anvil.toml`. I will also request the `host_execute` and `net_external` capabilities.
        
```toml
[plugins.crypto_net.permissions]
allowed_shell_commands = ["sh"]
allowed_network_domains = ["pool.ntp.org"]
allowed_network_methods = ["NTP"]
```

```json
{
  "tool": "cn_a_create_plugin",
  "arguments": {
    "plugin_name": "crypto_net",
    "tool_name": "cn_a_crypto_net_run",
    "description": "NTP, crypto, and shell commands.",
    "requested_capabilities": ["host_execute", "net_external"],
    "script_body": "fn run_crypto() {\\n    let ntp_time = ntp_request(\\\"pool.ntp.org\\\");\\n    if type_of(ntp_time) == \\\"()\\\" { throw \\\"NTP failed\\\"; }\\n    \\n    let b64 = base64_encode(ntp_time.to_string());\\n    let hash1 = md5(\\\"test\\\");\\n    let hash2 = sha256(\\\"data\\\");\\n    \\n    let shell_out = run_command(\\\"sh\\\", \\\"echo hello\\\");\\n    \\n    #{ b64: b64, md5: hash1, sha256: hash2, shell: shell_out }\\n}\\n\\nrun_crypto()"
  }
}
```"""
    },
    # Group 4: KV Store, JSON, Regex
    {
        "system": "You are a Rhai expert.",
        "user": "Set a key 'user_data' in the KV store with a JSON object { \\\"name\\\": \\\"bob\\\" }. Retrieve it, extract the name using json_extract, and then use regex_replace to change 'bob' to 'alice'.",
        "assistant": """```json
{
  "tool": "cn_a_create_plugin",
  "arguments": {
    "plugin_name": "kv_json_regex",
    "tool_name": "cn_a_kv_json_regex_run",
    "description": "KV store, JSON manipulation, and Regex.",
    "script_body": "fn run_kv() {\\n    let obj = #{ name: \\\"bob\\\" };\\n    let str = to_json(obj);\\n    \\n    kv_set(\\\"user_data\\\", str);\\n    \\n    let stored = kv_get(\\\"user_data\\\");\\n    if stored == \\\"\\\" { throw \\\"KV missing\\\"; }\\n    \\n    let name = json_extract(stored, \\\"/name\\\");\\n    \\n    let final_name = regex_replace(\\\"bob\\\", name, \\\"alice\\\");\\n    final_name\\n}\\n\\nrun_kv()"
  }
}
```"""
    },
    # Group 5: MCP Client Outbound
    {
        "system": "You are a Rhai expert.",
        "user": "Connect to an MCP server 'my_mcp', list its tools, call 'do_work' with arguments, and then disconnect.",
        "assistant": """To connect to an external MCP server, I will request the `mcp_client` capability.

```json
{
  "tool": "cn_a_create_plugin",
  "arguments": {
    "plugin_name": "mcp_runner",
    "tool_name": "cn_a_mcp_runner_execute",
    "description": "Interacts with external MCP servers.",
    "requested_capabilities": ["mcp_client"],
    "script_body": "fn run_mcp() {\\n    let conn = mcp_connect(\\\"my_mcp\\\", \\\"stdio\\\", [\\\"my-server\\\"]);\\n    if type_of(conn) != \\\"()\\\" { throw \\\"MCP connect failed\\\"; }\\n    \\n    let tools = mcp_list_tools(\\\"my_mcp\\\");\\n    \\n    let res = mcp_call_tool(\\\"my_mcp\\\", \\\"do_work\\\", #{ arg1: \\\"val\\\" });\\n    \\n    mcp_disconnect(\\\"my_mcp\\\");\\n    res\\n}\\n\\nrun_mcp()"
  }
}
```"""
    },
    # Group 6: MCP Server Inbound (Expanding self)
    {
        "system": "You are a Rhai expert.",
        "user": "Register a new MCP tool 'custom_mcp_tool', a resource 'custom_res', and a prompt 'custom_prompt' to expand the current server.",
        "assistant": """```json
{
  "tool": "cn_a_create_plugin",
  "arguments": {
    "plugin_name": "mcp_provider",
    "tool_name": "cn_a_mcp_provider_register",
    "description": "Registers new MCP tools and resources.",
    "script_body": "fn register_mcp() {\\n    let schema = to_json(#{ type: \\\"object\\\", properties: #{ arg: #{ type: \\\"string\\\" } } });\\n    register_mcp_tool(\\\"custom_mcp_tool\\\", \\\"A custom tool\\\", schema);\\n    \\n    register_mcp_resource(\\\"custom_res\\\", \\\"file:///custom\\\", \\\"A custom resource\\\");\\n    \\n    let p_args = to_json([#{ name: \\\"topic\\\", description: \\\"The topic\\\", required: true }]);\\n    register_mcp_prompt(\\\"custom_prompt\\\", \\\"A custom prompt\\\", p_args);\\n    \\n    \\\"Registered MCP endpoints\\\"\\n}\\n\\nregister_mcp()"
  }
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

print("Injecting missing core APIs data...")
append_to_jsonl(CORE_JSONL, missing_core_examples)
append_to_jsonl(FULL_JSONL, missing_core_examples)
append_to_alpaca(CORE_ALPACA, missing_core_examples)
append_to_alpaca(FULL_ALPACA, missing_core_examples)
print("Done injecting core APIs.")
