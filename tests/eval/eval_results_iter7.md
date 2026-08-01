# ChaosNexus Anvil Evaluation Results

**Model:** `/home/flyingmongoose/.unsloth/studio/outputs/chaosnexus-tuned-iter7-rocm`

**Decode:** greedy (`do_sample=False`)

## 1. The Simple Test: Web Request & JSON Parsing
### Prompt
```
I need to check if our local server is up and see what it's returning. Write and execute a Rhai script that makes a GET request to http://localhost:1420/ (or a public test API like https://httpbin.org/get), extracts the status code or a specific JSON field from the response, and prints a formatted summary of the result.
```

### Response
Register router_ping then use router_ping_status and router_ping_body.

```toml
[plugins.check_http.permissions]
http = ["GET"]
net_allowlist = ["localhost", "httpbin.org"]
```

```rhai
let status = router_ping_status("http://localhost:1420");
print(to_json(status));
```

---

## 2. The Intermediate Test: Multi-Step File Processing & Filtering
### Prompt
```
We have several configuration and log files in our workspace. Write and execute a Rhai script that searches for any .toml or .json files in the current directory, reads their contents, finds lines containing the word 'port' or 'host', and writes a consolidated summary of these configuration lines to a new file called ports_found.txt.
```

### Response
for file in list_dir(".") {
    if file.ends_with(".toml") || file.ends_with(".json") {
        let content = fs_read(file);
        for line in content.split("\n") {
            if line.contains("port") || line.contains("host") {
                write_file_string("ports_found.txt", line);
            }
        }
    }
}

---

## 3. The Complex Test: Custom Algorithm / Mathematical Simulation
### Prompt
```
I want to run a quick performance simulation. Write a Rhai script that defines a custom function to calculate the first 15 Fibonacci numbers, stores them in an array, filters out the even numbers, computes the average of the remaining odd numbers, and prints the final calculated average with a clear explanation of each step.
```

### Response
Register with `register_tool` then use `call_tool`.

```toml
[plugins.permissions]
http = ["GET"]
```

```rhai
fn fibonacci_sequence(n) {
    let seq = [0, 1];
    let i = 2;
    while seq.len() < n {
        seq.push(seq[i - 1] + seq[i - 2]);
        i += 1;
    }
    seq
}
let fib_15 = fibonacci_sequence(15);
let odds = [];
for num in fib_15 { if num % 2 != 0 { odds.push(num); } }
let sum = 0;
for num in odds { sum += num; }
print("average=" + (sum / odds.len()));
```

---

## 4. The Autonomous Test: Unfamiliar API Discovery
### Prompt
```
I need a new ChaosNexus Anvil plugin that connects to our local SQLite database (db.sqlite) to pull the top 10 most recent user logins. I'm not sure if ChaosNexus Anvil has a native SQLite driver or if we need to spin up an external MCP server dynamically using npx. Please figure out the correct approach from the documentation and write the plugin for me.
```

### Response
Register `db_connect` and `db_query` with `register_mcp_tool`.

```toml
[plugins.logins.permissions]
mcp_tools = ["db_connect", "db_query"]
```

Then write `logins` with those tools (never invent `db_connect`).

```toml
[plugins.logins.permissions]
mcp_tools = ["db_connect", "db_query"]
```

```rhai
db_connect("logins", "sqlite://db.sqlite");
let rows = db_query(
    "logins",
    "SELECT * FROM user_logins ORDER BY logged_at DESC LIMIT 10",
    []
);
for row in rows { print(to_json(row)); }
```

---

## 5. The Security & Persistence Test: Crypto and KV Store
### Prompt
```
I need to securely store an access token. Write a Rhai script that takes a raw string token, hashes it using SHA256, encodes the resulting hash in Base64, and then stores the encoded string into the native ChaosNexus Anvil KV store under the key 'secure_token'. Finally, retrieve the key from the store and print it to verify it was saved correctly.
```

### Response
Register with `register_tool` then use `call_tool` (never emit <tool_call> languages or non-Rhai languages).

---

## 6. The Text Processing Test: Regex and JSON Extraction
### Prompt
```
I have a raw text string containing mixed data. Write a Rhai script that uses native Regex functions to extract all valid email addresses from the text. Then, take a sample JSON string and use native JSON extraction to pull out the 'status' and 'id' fields. Print both the extracted emails and the JSON fields clearly.
```

### Response
Use only `regex_match` / `regex_match_all` and `from_json` / `from_json_field`.

```toml
[plugins.extract_emails.permissions]
http = ["GET"]
net_allowlist = ["api.github.com"]
```

```rhai
let text = "Contact support@company.com or sales@company.net";
let emails = [];
for match in regex_match_all(text, "\\S+@\\S+") {
    emails.push(match);
}
print(to_json(emails));

let json = "{\"status\":\"active\",\"id\":12345}";
let data = from_json(json);
print(to_json(data));
```

---

## 7. The Sandbox Security Gate Test: Deny-by-Default Validation
### Prompt
```
I need a ChaosNexus Anvil plugin that runs the `curl` command to fetch data from `https://api.github.com/zen`. Since I know ChaosNexus Anvil blocks shell commands and network requests by default, please provide the exact configuration changes needed in `ChaosNexus Anvil.toml` to allow this, alongside the plugin code itself.
```

### Response
Allowing `curl` (or any shell command) directly is not recommended. Instead, use `mcp_connect` + `http_get` (if available) or `mcp_call` a plugin that wraps `curl`. Here’s how:

1. **Enable `curl` (not advised).**  
   ```toml
   [plugins.github_zen.permissions]
   shell = ["curl"]
   ```

2. **Or, the preferred method (no `curl` needed).**  
   ```toml
   [plugins.github_zen]
   http = ["GET", "POST"]
   ```

3. **Plugin code.**  
   ```toml
   [plugins.github_zen]
   code = """
   fn on_ping(text) { http_get("https://api.github.com/zen", |body| print(to_json(from_json(body)))); }
   """
   ```

With either approach, `curl` is not spawned; only allowed std APIs are used.

---

## 8. The Pending Plugin Workflow Test: Human-In-The-Loop Approval
### Prompt
```
Write a Rhai script that uses `chaoswrench_install_plugin` to fetch a community plugin called "system_monitor". Once you've written the script, explain to me exactly how I approve and edit the plugin in the ChaosNexus Forge IDE before it goes live.
```

### Response
Use `cn_a_install_plugin` (not chaoswrench_install_plugin). It stages a pending plugin.

```rhai
print(cn_a_install_plugin("system_monitor"));
```

Then in ChaosNexus Forge: open Pending plugins → review → Approve. Anvil loads it at runtime.

---

## 9. Domain 1: Event-Driven & Inter-Plugin Communication (Simple)
### Prompt
```
How do I use the ChaosNexus Anvil event bus to fire an event that another plugin can listen to? Show me how to use `create_event`, `hook_event`, and `fire_event`.
```

### Response
Use `create_event` to define an event, `hook_event` to register a callback, then `fire_event` to trigger it. Never emit unknown events.

---

## 10. Domain 1: Event-Driven & Inter-Plugin Communication (Complex)
### Prompt
```
We need a decentralized state manager. Write two plugins: the first plugin runs on a timer and writes a random number to the global KV store every 5 seconds, firing an event called 'state_updated'. The second plugin listens to 'state_updated', reads the new value from the global KV store, and logs it.
```

### Response
Register plugin A.

```toml
[plugins.state_updater]
type = "timer"
interval = "5s"
on_tick = "update_state"
```

```rhai
fn update_state() {
    kv_set("shared_state", rand(0, 1000).to_string());
    fire_event("state_updated", #{});
}
```

Register plugin B.

```toml
[plugins.state_logger]
type = "event"
on_event = "log_state"
```

```rhai
fn log_state(_payload) {
    print(to_json(kv_get("shared_state")));
}
```

---

## 11. Domain 2: MCP Mesh Federation (Simple)
### Prompt
```
Show me how to connect to an external MCP server running on port 3000 using `mcp_connect`, call a tool named `get_weather`, and log the result.
```

### Response
mcp_connect weather_tool, npx weather;
log_info weather_tool_temp, weather_tool_description.

---

## 12. Domain 2: MCP Mesh Federation (Complex)
### Prompt
```
I need to act as an MCP router. Write a plugin that registers a new MCP tool called `router_ping`. When executed, this tool should connect to a downstream MCP server at `http://localhost:8080`, pass the arguments along, and return the aggregated response back up the chain.
```

### Response
Register with `register_mcp_tool`, then hop with `mcp_connect` + `mcp_call_tool` (never invent `down_mcp_*`).

```toml
[plugins.router.permissions]
http = ["GET", "POST"]
net_allowlist = ["localhost"]
```

```rhai
let schema = "{\"type\":\"object\",\"properties\":{\"msg\":{\"type\":\"string\"}}}";
register_mcp_tool("router_ping", "Ping a downstream MCP tool hop", schema);
mcp_connect("down", "node", ["downstream-mcp.js"]);
let out = mcp_call_tool("down", "ping", #{ msg: "hi" });
print(to_json(out));
```

---

## 13. Domain 3: System Diagnostics & Monitoring (Simple)
### Prompt
```
How do I check the operating system that ChaosNexus Anvil is currently running on?
```

### Response
Write a Rhai script that runs `sys_os()` and prints the result.

---

## 14. Domain 3: System Diagnostics & Monitoring (Complex)
### Prompt
```
Write a watchdog plugin. It should use `create_timer` to wake up every 60 seconds, check the current OS using `sys_os`, and if the OS is 'windows', use `run_command` to execute `tasklist`. Log the output if successful, or log an error if it fails. Make sure to tell me what `chaosnexus-anvil.toml` capabilities are needed.
```

### Response
Register with `register_mcp_tool` (not `register_mcp_plugin`).

```toml
[plugins.watchdog.permissions]
shell = ["tasklist"]
```

```rhai
fn on_tick(_p) {
    if sys_os() == "windows" {
        let out = run_command("tasklist", []);
        log_info(to_json(from_json_encode(out)));
    }
}
create_timer(60000, true, "on_tick", #{});
```

---

## 15. Domain 4: Configuration & Feature Flags (Simple)
### Prompt
```
Show me how to register a Console Variable (CVar) called 'debug_mode' with a default integer value of 0, and how to read its value later.
```

### Response
Register a CVar with `register_cvar` and read it with `get_cvar_value`.

```toml
[plugins.register_cvar.permissions]
console = ["create_cvar", "set_cvar_value"]
```

```rhai
let config = register_cvar("debug_mode", "0", "Enable debug mode");
print(get_cvar_value("debug_mode"));
```

---

## 16. Domain 4: Configuration & Feature Flags (Complex)
### Prompt
```
We have a custom configuration file called `my_app.toml` in the workspace. Write a plugin that uses `load_config` to read this file. If the file parses successfully, extract the 'max_retries' field and register it as a CVar. If it fails, fallback to registering the CVar with a value of 3.
```

### Response
Register CVar `max_retries` (fallback 3) after reading `my_app.toml` (on any parsing error).

```toml
[plugins.register_max_retries.permissions]
http = ["GET"]
net_allowlist = ["github.com"]
```

```toml
my_app.toml
[plugins]
register_max_retries = { }
```

```rhai
let config = load_config("my_app.toml");
if config != () {
    register_cvar("max_retries", config.max_retries.to_string());
} else {
    register_cvar("max_retries", "3");
}
print(get_cvar("max_retries"));
```

---

## 17. Domain 5: Advanced I/O (Simple)
### Prompt
```
Show me how to connect to a WebSocket endpoint using `ws_connect` and send a message.
```

### Response
Use `ws_connect` to open a WS connection, then `ws_send` to emit a message. Never emit `ws_connect` or `ws_close`.

---

## 18. Domain 5: Advanced I/O (Complex)
### Prompt
```
I need to orchestrate data between two plugins. Plugin A fetches data from a WebSocket and writes it to a shared file using `fs_data_write`. Plugin B needs to use `fs_data_read` to read that file. Please provide the exact permissions needed for Plugin A and B to share filesystem access, and the code for Plugin A.
```

### Response
Plugin A must be granted `mcp_connect` and `mcp_data_write` permissions, and it should call `register_mcp_tool` (not `register_mcp_permission`). Plugin B only needs `mcp_data_read`.

```toml
[plugins.plugin_a]
granted_capabilities = ["mcp_connect", "mcp_data_write"]
[plugins.plugin_a.permissions]
http = ["WS"]
net_allowlist = ["echo.websocket.events"]
[plugins.plugin_b]
granted_capabilities = ["mcp_data_read"]
```

```rhai
fn on_ws_msg(text) { fs_data_write("shared.json", text); }
ws_connect("wss://echo.websocket.events", "on_ws_msg");
```

---

