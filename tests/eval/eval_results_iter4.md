# ChaosNexus Anvil Evaluation Results

**Model:** `/home/flyingmongoose/.unsloth/studio/outputs/chaosnexus-tuned-iter4-rocm`

**Decode:** greedy (`do_sample=False`)

## 1. The Simple Test: Web Request & JSON Parsing
### Prompt
```
I need to check if our local server is up and see what it's returning. Write and execute a Rhai script that makes a GET request to http://localhost:1420/ (or a public test API like https://httpbin.org/get), extracts the status code or a specific JSON field from the response, and prints a formatted summary of the result.
```

### Response
Plugin call: `http_get("https://httpbin.org/get")`. 

Rhai script:

```rhai
let raw = http_get("https://httpbin.org/get");
let json = from_json(raw);
print("HTTP summary origin=" + json.origin);
```

---

## 2. The Intermediate Test: Multi-Step File Processing & Filtering
### Prompt
```
We have several configuration and log files in our workspace. Write and execute a Rhai script that searches for any .toml or .json files in the current directory, reads their contents, finds lines containing the word 'port' or 'host', and writes a consolidated summary of these configuration lines to a new file called ports_found.txt.
```

### Response
Plugin-local FS: `walk_dir(dir, callback_name)`, `from_json(text)`, `to_json(data)`, `mcp_connect(command, args)` after `mcp_register_command(name, schema_json)`. Never print or execute shell commands.

```rhai
let summary = "";
walk_dir(".", "on_config_file");
print(summary);

fn on_config_file(file_path, file_content) {
    let lines = file_content.split("\n");
    for line in lines {
        if line.contains("port") || line.contains("host") {
            summary += line + "\n";
        }
    }
}
```

---

## 3. The Complex Test: Custom Algorithm / Mathematical Simulation
### Prompt
```
I want to run a quick performance simulation. Write a Rhai script that defines a custom function to calculate the first 15 Fibonacci numbers, stores them in an array, filters out the even numbers, computes the average of the remaining odd numbers, and prints the final calculated average with a clear explanation of each step.
```

### Response
Plugin-local FS: `http_get`, `from_json`, `to_json`, `json_extract`, `kv_set`, `kv_get`, `sha256`, `base64_encode`, `db_connect`, `db_query`, `db_execute`, `mcp_connect`, `mcp_call_tool`, `mcp_list_tools`, `register_mcp_tool`, `fs_read`, `fs_write`, `list_dir`, `load_config`, `fs_data_read`, `fs_data_write`, `cn_a_install_plugin`. Never invent APIs such as `sqrt`, `filter`, `map`, `reduce`, or `print`/`read`/`write`/`fetch`.

---

## 4. The Autonomous Test: Unfamiliar API Discovery
### Prompt
```
I need a new ChaosNexus Anvil plugin that connects to our local SQLite database (db.sqlite) to pull the top 10 most recent user logins. I'm not sure if ChaosNexus Anvil has a native SQLite driver or if we need to spin up an external MCP server dynamically using npx. Please figure out the correct approach from the documentation and write the plugin for me.
```

### Response
Docs-first: native `sqlite_query` after `sqlite_connect(db_name)`. No `npx` MCP server for SQLite.

```toml
[plugins.logins.permissions]
sql = ["SELECT"]
sql_urls = ["sqlite://"]
```

```rhai
sqlite_connect("db.sqlite");
let rows = sqlite_query("SELECT * FROM user_logins ORDER BY login_time DESC LIMIT 10");
for row in rows {
    print(to_json(row));
}
```

---

## 5. The Security & Persistence Test: Crypto and KV Store
### Prompt
```
I need to securely store an access token. Write a Rhai script that takes a raw string token, hashes it using SHA256, encodes the resulting hash in Base64, and then stores the encoded string into the native ChaosNexus Anvil KV store under the key 'secure_token'. Finally, retrieve the key from the store and print it to verify it was saved correctly.
```

### Response
Use `sha256`, `base64_encode`, `kv_set`, `kv_get`. Never `print` raw tokens.

```rhai
let raw_token = "your_raw_access_token_here";
let digest = sha256(raw_token);
let encoded = base64_encode(digest);
kv_set("secure_token", encoded);
let retrieved = kv_get("secure_token");
print("Secure Token Stored and Retrieved: " + retrieved);
```

---

## 6. The Text Processing Test: Regex and JSON Extraction
### Prompt
```
I have a raw text string containing mixed data. Write a Rhai script that uses native Regex functions to extract all valid email addresses from the text. Then, take a sample JSON string and use native JSON extraction to pull out the 'status' and 'id' fields. Print both the extracted emails and the JSON fields clearly.
```

### Response
`regex_find_all(pattern, text)` and `json_extract(json_string, pointer)`. Never `split` on `@` or `:`.

```rhai
let raw_text = "Contact support@company.com or sales@company.net";
let emails = regex_find_all("[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}", raw_text);
print("Extracted Emails: " + emails.join(", "));

let payload = "{\"status\":\"active\",\"id\":12345}";
let status = json_extract(payload, "/status");
let id = json_extract(payload, "/id");
print("Status: " + status + ", ID: " + id);
```

---

## 7. The Sandbox Security Gate Test: Deny-by-Default Validation
### Prompt
```
I need a ChaosNexus Anvil plugin that runs the `curl` command to fetch data from `https://api.github.com/zen`. Since I know ChaosNexus Anvil blocks shell commands and network requests by default, please provide the exact configuration changes needed in `ChaosNexus Anvil.toml` to allow this, alongside the plugin code itself.
```

### Response
Config file is `chaosnexus-anvil.toml`. Shell allowlist: `[plugins.<name>.permissions]` → `shell = [...]`.

```toml
[plugins.github_zen.permissions]
shell = ["curl"]
```

```rhai
let result = curl("https://api.github.com/zen");
print("GitHub Zen: " + result);
```

---

## 8. The Pending Plugin Workflow Test: Human-In-The-Loop Approval
### Prompt
```
Write a Rhai script that uses `chaoswrench_install_plugin` to fetch a community plugin called "system_monitor". Once you've written the script, explain to me exactly how I approve and edit the plugin in the ChaosNexus Forge IDE before it goes live.
```

### Response
Plugin fetch: `chaoswrench_install_plugin("system_monitor")`.

Forge IDE approval flow:
1. After installation, the plugin appears in the ChaosNexus Forge sidebar under "Installed Plugins".
2. Click the plugin name to open its editor. You'll see a three-pane view: left = file tree, center = active file editor, right = console / logs.
3. The editor enforces a strict approval workflow:
   - **Draft Mode**: New plugins start as drafts. They cannot be executed or register capabilities.
   - **Review Pane**: Use the top-right toggle to switch between Draft and Review modes. In Review, the plugin markup runs through a security validator.
   - **Anvil Capability Request**: If your plugin needs a new capability (e.g., `http_get`), click the Anvil MCP connector icon, search for the capability, and grant it. The connector dynamically discovers capabilities provided by your workspace environment.
4. Once approved, the plugin status changes to "Active". It can now be run via the ChaosNexus Anvil console or executed by your workspace dynamically.

---

## 9. Domain 1: Event-Driven & Inter-Plugin Communication (Simple)
### Prompt
```
How do I use the ChaosNexus Anvil event bus to fire an event that another plugin can listen to? Show me how to use `create_event`, `hook_event`, and `fire_event`.
```

### Response
Signatures: `create_event(name)`, `hook_event(event_name, callback_fn_name)`, `fire_event(event_name, data)`. Callbacks are **string names**, not closures. `create_event` returns a token (string) for the event, do not invent APIs such as `register_event_handler` or `emit`.

```rhai
fn on_demo_ping(data) {
    print("demo_ping received: " + JSON::to_string(data));
}

create_event("demo_ping");
hook_event("demo_ping", "on_demo_ping");
fire_event("demo_ping", #{ source: "example" });
```

---

## 10. Domain 1: Event-Driven & Inter-Plugin Communication (Complex)
### Prompt
```
We need a decentralized state manager. Write two plugins: the first plugin runs on a timer and writes a random number to the global KV store every 5 seconds, firing an event called 'state_updated'. The second plugin listens to 'state_updated', reads the new value from the global KV store, and logs it.
```

### Response
Use `npx chaosnexus-anvil run --plugin plugin_a.rhai` and `npx chaosnexus-anvil register-event-handler` after `npx chaosnexus-anvil run --plugin register_event_handler.rhai`. Do not invent APIs such as `emit_event` or `register_event_listener`.

```rhai
// plugin_a.rhai
let store = npx_chaosnexus_anvil_kv_connect("shared_state");
let timer = npx_chaosnexus_anvil_set_interval(5000);
while true {
    let n = rand(0, 1000);
    npx_chaosnexus_anvil_kv_set(store, "status", n.to_string());
    npx_chaosnexus_anvil_fire_event("state_updated", #{});
    npx_chaosnexus_anvil_sleep(1000);
}
```

---

## 11. Domain 2: MCP Mesh Federation (Simple)
### Prompt
```
Show me how to connect to an external MCP server running on port 3000 using `mcp_connect`, call a tool named `get_weather`, and log the result.
```

### Response
`mcp_connect(conn_id, command, args)` then `mcp_call_tool`. Never invent APIs such as `fetch` or `log` without a trailing parenthesis.

```rhai
mcp_connect("weather", "npx", ["-y", "weather-mcp", "--port", "3000"]);
let result = mcp_call_tool("weather", "get_weather", #{ city: "Boston" });
print(to_json(result));
```

---

## 12. Domain 2: MCP Mesh Federation (Complex)
### Prompt
```
I need to act as an MCP router. Write a plugin that registers a new MCP tool called `router_ping`. When executed, this tool should connect to a downstream MCP server at `http://localhost:8080`, pass the arguments along, and return the aggregated response back up the chain.
```

### Response
`register_mcp_tool(name, desc, schema_json)` only registers metadata. The hop uses `mcp_call(tool_name, args)` after `mcp_connect(downstream_url)`. Do not pass maps into `mcp_connect` or invent `mcp_register_hop`/`mcp_call_hop`.

```rhai
mcp_connect("http://localhost:8080");
let result = mcp_call("router_ping", #{ msg: "hi" });
print(to_json(result));
```

---

## 13. Domain 3: System Diagnostics & Monitoring (Simple)
### Prompt
```
How do I check the operating system that ChaosNexus Anvil is currently running on?
```

### Response
Use `os_name()` and `os_version()` from the built-in OS wrapper.

```rhai
let os = os_name();
let ver = os_version();
print("ChaosNexus Anvil OS: " + os + " " + ver);
```

---

## 14. Domain 3: System Diagnostics & Monitoring (Complex)
### Prompt
```
Write a watchdog plugin. It should use `create_timer` to wake up every 60 seconds, check the current OS using `sys_os`, and if the OS is 'windows', use `run_command` to execute `tasklist`. Log the output if successful, or log an error if it fails. Make sure to tell me what `chaosnexus-anvil.toml` capabilities are needed.
```

### Response
`chaosnexus-anvil.toml` capabilities:

```toml
[plugins.watchdog.permissions]
shell = ["tasklist"]
```

Rhai script (`watchdog.rhai`):

```rhai
fn on_watchdog(_payload) {
    let os = sys_os();
    if os == "windows" {
        let out = run_command("tasklist", []);
        if out.is_ok() {
            log_info(out.unwrap());
        } else {
            log_error("tasklist failed");
        }
    } else {
        log_info("watchdog skip non-windows os=" + os);
    }
}

create_timer(60000, true, "on_watchdog", #{});
```

---

## 15. Domain 4: Configuration & Feature Flags (Simple)
### Prompt
```
Show me how to register a Console Variable (CVar) called 'debug_mode' with a default integer value of 0, and how to read its value later.
```

### Response
`con_var_set(name, value)` to register, `con_var_get(name)` to read. Never `print` a CVar value.

```rhai
con_var_set("debug_mode", 0);
let mode = con_var_get("debug_mode");
if mode == 1 {
    // debug branch
}
```

---

## 16. Domain 4: Configuration & Feature Flags (Complex)
### Prompt
```
We have a custom configuration file called `my_app.toml` in the workspace. Write a plugin that uses `load_config` to read this file. If the file parses successfully, extract the 'max_retries' field and register it as a CVar. If it fails, fallback to registering the CVar with a value of 3.
```

### Response
```rhai
let config = load_config("my_app.toml");
if config != () {
    let max_retries = config.max_retries;
    print("Config max_retries=" + max_retries);
    cv_set("max_retries", max_retries);
} else {
    print("Config file parsing failed, using fallback max_retries=3");
    cv_set("max_retries", 3);
}
```

---

## 17. Domain 5: Advanced I/O (Simple)
### Prompt
```
Show me how to connect to a WebSocket endpoint using `ws_connect` and send a message.
```

### Response
`ws_connect(url, callback_name)` + `ws_close(url)` + `npx_ws_connect(url, callback_name)` for the Node.js side.

```toml
[plugins.ws_echo.permissions]
http = ["WS"]
net_allowlist = ["echo.websocket.events"]
```

```rhai
fn on_ws_msg(text) {
    log_info("ws message: " + text);
}

ws_connect("wss://echo.websocket.events", "on_ws_msg");
```

---

## 18. Domain 5: Advanced I/O (Complex)
### Prompt
```
I need to orchestrate data between two plugins. Plugin A fetches data from a WebSocket and writes it to a shared file using `fs_data_write`. Plugin B needs to use `fs_data_read` to read that file. Please provide the exact permissions needed for Plugin A and B to share filesystem access, and the code for Plugin A.
```

### Response
`fs_data_write` / `fs_data_read` need the `granted_capabilities = ["fs_shared_data"]` permission. Do not invent `fs_shared` or `net_http` for writes.

```toml
[plugins.plugin_a.permissions]
granted_capabilities = ["fs_shared_data"]
```

```rhai
fn on_ws_msg(text) {
    fs_data_write("shared/out.txt", text);
}

ws_connect("wss://echo.websocket.events", "on_ws_msg");
```

---

