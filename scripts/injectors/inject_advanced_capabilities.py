import json
import os

CORE_JSONL = "datasets/core/train.jsonl"
CORE_ALPACA = "datasets/core/train_alpaca.json"
FULL_JSONL = "datasets/full_stack/train.jsonl"
FULL_ALPACA = "datasets/full_stack/train_alpaca.json"

advanced_examples = [
    # Domain 1: Event-Driven & Inter-Plugin Communication (Simple)
    {
        "system": "You are a Rhai expert.",
        "user": "How do I use the ChaosNexus Anvil event bus to fire an event that another plugin can listen to? Show me how to use `create_event`, `hook_event`, and `fire_event`.",
        "assistant": """To use the ChaosNexus Anvil event bus, you need to first request the `events` capability. Then you can use `create_event` to initialize an event channel, `hook_event` to attach a callback, and `fire_event` to trigger it.

```json
{
  "tool": "cn_a_create_plugin",
  "arguments": {
    "plugin_name": "event_demo",
    "tool_name": "cn_a_event_demo_run",
    "description": "Demonstrates the event bus.",
    "requested_capabilities": ["events"],
    "script_body": "fn my_callback(payload) {\\n    print(\\\"Received: \\\" + payload);\\n}\\n\\nfn run() {\\n    create_event(\\\"my_custom_event\\\");\\n    hook_event(\\\"my_custom_event\\\", \\\"my_callback\\\");\\n    fire_event(\\\"my_custom_event\\\", \\\"Hello from the event bus!\\\");\\n    \\\"Event fired successfully.\\\"\\n}"
  }
}
```"""
    },
    # Domain 1: Event-Driven & Inter-Plugin Communication (Complex)
    {
        "system": "You are a Rhai expert.",
        "user": "We need a decentralized state manager. Write two plugins: the first plugin runs on a timer and writes a random number to the global KV store every 5 seconds, firing an event called 'state_updated'. The second plugin listens to 'state_updated', reads the new value from the global KV store, and logs it.",
        "assistant": """I will create two plugins. The first (`state_publisher`) will use `create_timer`, `set_global`, and `fire_event`. The second (`state_subscriber`) will use `hook_event`, `get_global`, and `log_info`. Both plugins need the `events` and `global_kv` capabilities.

Here is the first plugin:
```json
{
  "tool": "cn_a_create_plugin",
  "arguments": {
    "plugin_name": "state_publisher",
    "tool_name": "cn_a_state_publisher_start",
    "description": "Publishes random state updates every 5 seconds.",
    "requested_capabilities": ["events", "global_kv"],
    "script_body": "fn tick() {\\n    let val = 42; // Using static for demo\\n    set_global(\\\"shared_state\\\", val);\\n    fire_event(\\\"state_updated\\\", val);\\n}\\n\\nfn start() {\\n    create_event(\\\"state_updated\\\");\\n    create_timer(5000, \\\"tick\\\", true);\\n    \\\"Publisher started.\\\"\\n}"
  }
}
```

Here is the second plugin:
```json
{
  "tool": "cn_a_create_plugin",
  "arguments": {
    "plugin_name": "state_subscriber",
    "tool_name": "cn_a_state_subscriber_start",
    "description": "Listens for state updates.",
    "requested_capabilities": ["events", "global_kv"],
    "script_body": "fn on_update(payload) {\\n    let current = get_global(\\\"shared_state\\\");\\n    log_info(\\\"State updated to: \\\" + current);\\n}\\n\\nfn start() {\\n    hook_event(\\\"state_updated\\\", \\\"on_update\\\");\\n    \\\"Subscriber started.\\\"\\n}"
  }
}
```"""
    },
    # Domain 2: MCP Mesh Federation (Simple)
    {
        "system": "You are a Rhai expert.",
        "user": "Show me how to connect to an external MCP server running on port 3000 using `mcp_connect`, call a tool named `get_weather`, and log the result.",
        "assistant": """To connect to an external MCP server, you must request the `mcp_client` capability. You can then use `mcp_connect` to establish a connection, and `mcp_call_tool` to execute a remote tool. You must also allow the connection in `chaosnexus-anvil.toml`.

Please add this to `<workspace_root>/anvil.toml`:
```toml
[plugins.weather_caller.permissions]
allowed_network_domains = ["localhost:3000"]
```

```json
{
  "tool": "cn_a_create_plugin",
  "arguments": {
    "plugin_name": "weather_caller",
    "tool_name": "cn_a_weather_caller_run",
    "description": "Calls an external MCP weather tool.",
    "requested_capabilities": ["mcp_client"],
    "script_body": "fn run() {\\n    mcp_connect(\\\"weather_srv\\\", \\\"http://localhost:3000\\\");\\n    let args = #{ location: \\\"San Francisco\\\" };\\n    let res = mcp_call_tool(\\\"weather_srv\\\", \\\"get_weather\\\", args);\\n    log_info(\\\"Weather: \\\" + res);\\n    res\\n}"
  }
}
```"""
    },
    # Domain 2: MCP Mesh Federation (Complex)
    {
        "system": "You are a Rhai expert.",
        "user": "I need to act as an MCP router. Write a plugin that registers a new MCP tool called `router_ping`. When executed, this tool should connect to a downstream MCP server at `http://localhost:8080`, pass the arguments along, and return the aggregated response back up the chain.",
        "assistant": """To act as an MCP router, we will request both `mcp_server` (implicitly via tool registration) and `mcp_client` capabilities. The plugin will expose a tool that internally uses `mcp_connect` and `mcp_call_tool`.

Please add this to `<workspace_root>/anvil.toml`:
```toml
[plugins.mcp_router.permissions]
allowed_network_domains = ["localhost:8080"]
```

```json
{
  "tool": "cn_a_create_plugin",
  "arguments": {
    "plugin_name": "mcp_router",
    "tool_name": "router_ping",
    "description": "Routes ping requests to a downstream server.",
    "requested_capabilities": ["mcp_client"],
    "script_body": "fn execute(args) {\\n    mcp_connect(\\\"downstream\\\", \\\"http://localhost:8080\\\");\\n    let res = mcp_call_tool(\\\"downstream\\\", \\\"ping\\\", args);\\n    let aggregated = #{ router_status: \\\"ok\\\", downstream: res };\\n    to_json(aggregated)\\n}"
  }
}
```"""
    },
    # Domain 3: System Diagnostics & Monitoring (Simple)
    {
        "system": "You are a Rhai expert.",
        "user": "How do I check the operating system that ChaosNexus Anvil is currently running on?",
        "assistant": """You can use the `sys_os` native function to get the current operating system. This function does not require any special capabilities.

```json
{
  "tool": "cn_a_create_plugin",
  "arguments": {
    "plugin_name": "os_checker",
    "tool_name": "cn_a_os_checker_run",
    "description": "Checks the current OS.",
    "script_body": "fn run() {\\n    let os = sys_os();\\n    print(\\\"Running on: \\\" + os);\\n    os\\n}"
  }
}
```"""
    },
    # Domain 3: System Diagnostics & Monitoring (Complex)
    {
        "system": "You are a Rhai expert.",
        "user": "Write a watchdog plugin. It should use `create_timer` to wake up every 60 seconds, check the current OS using `sys_os`, and if the OS is 'windows', use `run_command` to execute `tasklist`. Log the output if successful, or log an error if it fails. Make sure to tell me what `chaosnexus-anvil.toml` capabilities are needed.",
        "assistant": """This requires the `shell` capability to execute system commands, and we must explicitly allow the `tasklist` command in the `chaosnexus-anvil.toml` file.

Please add the following to your `<workspace_root>/anvil.toml`:
```toml
[plugins.watchdog.permissions]
allowed_shell = ["tasklist"]
```

Here is the plugin code:
```json
{
  "tool": "cn_a_create_plugin",
  "arguments": {
    "plugin_name": "watchdog",
    "tool_name": "cn_a_watchdog_start",
    "description": "Periodically monitors windows processes.",
    "requested_capabilities": ["shell"],
    "script_body": "fn check_tasks() {\\n    if sys_os() == \\\"windows\\\" {\\n        try {\\n            let out = run_command(\\\"cmd\\\", \\\"tasklist\\\");\\n            log_info(\\\"Tasklist: \\\" + out);\\n        } catch(err) {\\n            log_error(\\\"Failed to run tasklist: \\\" + err);\\n        }\\n    }\\n}\\n\\nfn start() {\\n    create_timer(60000, \\\"check_tasks\\\", true);\\n    \\\"Watchdog started.\\\"\\n}"
  }
}
```"""
    },
    # Domain 4: Configuration & Feature Flags (Simple)
    {
        "system": "You are a Rhai expert.",
        "user": "Show me how to register a Console Variable (CVar) called 'debug_mode' with a default integer value of 0, and how to read its value later.",
        "assistant": """You can register global Console Variables (CVars) using `register_cvar` and read them using `get_cvar`. CVars are strings, so you will need to parse the integer if you want to use it mathematically. No special capabilities are required for CVars.

```json
{
  "tool": "cn_a_create_plugin",
  "arguments": {
    "plugin_name": "cvar_demo",
    "tool_name": "cn_a_cvar_demo_run",
    "description": "Demonstrates CVars.",
    "script_body": "fn run() {\\n    register_cvar(\\\"debug_mode\\\", \\\"0\\\");\\n    \\n    let mode_str = get_cvar(\\\"debug_mode\\\");\\n    let mode = parse_int(mode_str);\\n    \\n    if mode > 0 {\\n        print(\\\"Debug mode is ON\\\");\\n    } else {\\n        print(\\\"Debug mode is OFF\\\");\\n    }\\n    mode_str\\n}"
  }
}
```"""
    },
    # Domain 4: Configuration & Feature Flags (Complex)
    {
        "system": "You are a Rhai expert.",
        "user": "We have a custom configuration file called `my_app.toml` in the workspace. Write a plugin that uses `load_config` to read this file. If the file parses successfully, extract the 'max_retries' field and register it as a CVar. If it fails, fallback to registering the CVar with a value of 3.",
        "assistant": """I can achieve this by catching the error from `load_config` within a try-catch block. The `load_config` function parses a local file into a Rhai object map. No special capabilities are needed for `load_config`.

```json
{
  "tool": "cn_a_create_plugin",
  "arguments": {
    "plugin_name": "config_loader",
    "tool_name": "cn_a_config_loader_init",
    "description": "Loads a toml config and registers a CVar.",
    "script_body": "fn init() {\\n    let retries = \\\"3\\\";\\n    try {\\n        let conf = load_config(\\\"my_app.toml\\\");\\n        if \\\"max_retries\\\" in conf {\\n            retries = conf.max_retries.to_string();\\n        }\\n    } catch(err) {\\n        log_warn(\\\"Could not load my_app.toml, using defaults. Error: \\\" + err);\\n    }\\n    \\n    register_cvar(\\\"max_retries\\\", retries);\\n    \\\"Max retries set to: \\\" + retries\\n}"
  }
}
```"""
    },
    # Domain 5: Advanced I/O (Simple)
    {
        "system": "You are a Rhai expert.",
        "user": "Show me how to connect to a WebSocket endpoint using `ws_connect` and send a message.",
        "assistant": """To use WebSockets, you must request the `network` capability and allow the domain in `chaosnexus-anvil.toml`. You provide `ws_connect` with the URL and the name of a callback function to handle incoming messages. To send, you use `ws_send`.

Please add this to `<workspace_root>/anvil.toml`:
```toml
[plugins.ws_demo.permissions]
allowed_network_domains = ["echo.websocket.events"]
```

```json
{
  "tool": "cn_a_create_plugin",
  "arguments": {
    "plugin_name": "ws_demo",
    "tool_name": "cn_a_ws_demo_run",
    "description": "Connects to a WebSocket.",
    "requested_capabilities": ["network"],
    "script_body": "fn on_message(msg) {\\n    print(\\\"WS Received: \\\" + msg);\\n}\\n\\nfn run() {\\n    ws_connect(\\\"wss://echo.websocket.events\\\", \\\"on_message\\\");\\n    ws_send(\\\"wss://echo.websocket.events\\\", \\\"Hello server!\\\");\\n    \\\"Connected and sent.\\\"\\n}"
  }
}
```"""
    },
    # Domain 5: Advanced I/O (Complex)
    {
        "system": "You are a Rhai expert.",
        "user": "I need to orchestrate data between two plugins. Plugin A fetches data from a WebSocket and writes it to a shared file using `fs_data_write`. Plugin B needs to use `fs_data_read` to read that file. Please provide the exact permissions needed for Plugin A and B to share filesystem access, and the code for Plugin A.",
        "assistant": """To share data via the filesystem, both plugins must request the `fs_shared_data` and `fs_cross_plugin` capabilities. Plugin A will also need the `network` capability for the WebSocket connection.

Please add this to `<workspace_root>/anvil.toml`:
```toml
[plugins.plugin_a.permissions]
allowed_network_domains = ["echo.websocket.events"]
```

Here is the code for Plugin A:
```json
{
  "tool": "cn_a_create_plugin",
  "arguments": {
    "plugin_name": "plugin_a",
    "tool_name": "cn_a_plugin_a_start",
    "description": "Writes WebSocket data to shared fs.",
    "requested_capabilities": ["network", "fs_shared_data", "fs_cross_plugin"],
    "script_body": "fn on_msg(msg) {\\n    fs_data_write(\\\"shared_stream.txt\\\", msg);\\n}\\n\\nfn start() {\\n    ws_connect(\\\"wss://echo.websocket.events\\\", \\\"on_msg\\\");\\n    ws_send(\\\"wss://echo.websocket.events\\\", \\\"Trigger stream\\\");\\n    \\\"Plugin A started.\\\"\\n}"
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

if __name__ == "__main__":
    print("Injecting advanced capabilities data...")
    append_to_jsonl(CORE_JSONL, advanced_examples)
    append_to_jsonl(FULL_JSONL, advanced_examples)
    append_to_alpaca(CORE_ALPACA, advanced_examples)
    append_to_alpaca(FULL_ALPACA, advanced_examples)
    print("Done.")
