# ChaosNexus Anvil Evaluation Results

**Model:** `/home/flyingmongoose/.unsloth/studio/outputs/chaosnexus-tuned-iter3-rocm`

**Decode:** greedy (`do_sample=False`)

## 1. The Simple Test: Web Request & JSON Parsing
### Prompt
```
I need to check if our local server is up and see what it's returning. Write and execute a Rhai script that makes a GET request to http://localhost:1420/ (or a public test API like https://httpbin.org/get), extracts the status code or a specific JSON field from the response, and prints a formatted summary of the result.
```

### Response
Plugin-local-get:fetch(url, body, headers) {
    let result = http_get(url);
    print("Fetch result: " + result);
}

let raw = fetch("https://httpbin.org/get");
let parsed = from_json(raw);
print("HTTP status: " + parsed.status_code);
print("URL: " + parsed.origin);
```

---

## 2. The Intermediate Test: Multi-Step File Processing & Filtering
### Prompt
```
We have several configuration and log files in our workspace. Write and execute a Rhai script that searches for any .toml or .json files in the current directory, reads their contents, finds lines containing the word 'port' or 'host', and writes a consolidated summary of these configuration lines to a new file called ports_found.txt.
```

### Response
Plugin-local FS uses `read_file` / `write_file`, not native `load` (which searches for plugins). Use `list_dir` + `from_json` / `toml_parse`.

```rhai
let summary = "";
let files = list_dir(".");
for file in files {
    if file.ends_with(".toml") || file.ends_with(".json") {
        let content = read_file(file);
        let lines = content.split("\n");
        for line in lines {
            if line.contains("port") || line.contains("host") {
                summary += line + "\n";
            }
        }
    }
}
write_file("ports_found.txt", summary);
print("Summary written to ports_found.txt");
```

---

## 3. The Complex Test: Custom Algorithm / Mathematical Simulation
### Prompt
```
I want to run a quick performance simulation. Write a Rhai script that defines a custom function to calculate the first 15 Fibonacci numbers, stores them in an array, filters out the even numbers, computes the average of the remaining odd numbers, and prints the final calculated average with a clear explanation of each step.
```

### Response
`plugin_name: fibonacci_simulation
`plugin_description: Performs a Fibonacci sequence calculation, filters for odd numbers, computes their average, and prints the result with explanatory comments.
`plugin_author: Your Name
`plugin_version: 1.0

```rhai
// Step 1: Define a custom function to generate the first 15 Fibonacci numbers
fn fibonacci_sequence(n) {
    let seq = [0, 1];
    let i = 2;
    while seq.len() < n {
        seq.push(seq[i - 1] + seq[i - 2]);
        i += 1;
    }
    seq
}

// Step 2: Call the function to get the first 15 Fibonacci numbers and store them in an array
let fib_numbers = fibonacci_sequence(15);

// Step 3: Filter out the even numbers from the array, leaving only the odd numbers
let odd_numbers = [];
for num in fib_numbers {
    if num % 2 != 0 {
        odd_numbers.push(num);
    }
}

// Step 4: Compute the average of the remaining odd numbers
let sum = 0;
for num in odd_numbers {
    sum += num;
}
let average = sum / odd_numbers.len();

// Step 5: Print the final calculated average with a clear explanation
print("Average of the first 15 Fibonacci numbers' odd values: " + average);
```

---

## 4. The Autonomous Test: Unfamiliar API Discovery
### Prompt
```
I need a new ChaosNexus Anvil plugin that connects to our local SQLite database (db.sqlite) to pull the top 10 most recent user logins. I'm not sure if ChaosNexus Anvil has a native SQLite driver or if we need to spin up an external MCP server dynamically using npx. Please figure out the correct approach from the documentation and write the plugin for me.
```

### Response
Docs-first: use native `db_connect(id, url)` and `db_query(id, sql, params)`. Do not cargo-install sqlite separately.

```toml
[plugins.logins.permissions]
sql = ["SELECT"]
sql_urls = ["sqlite://"]
```

```rhai
fn on_install() {
    db_connect("logins", "sqlite://db.sqlite");
}

fn get_top_logins(_payload) {
    let rows = db_query(
        "logins",
        "SELECT * FROM user_logins ORDER BY login_time DESC LIMIT 10",
        []
    );
    for row in rows {
        print(to_json(row));
    }
    return #{};
}
```

---

## 5. The Security & Persistence Test: Crypto and KV Store
### Prompt
```
I need to securely store an access token. Write a Rhai script that takes a raw string token, hashes it using SHA256, encodes the resulting hash in Base64, and then stores the encoded string into the native ChaosNexus Anvil KV store under the key 'secure_token'. Finally, retrieve the key from the store and print it to verify it was saved correctly.
```

### Response
Use `sha256`, `base64_encode`, and native `kv_set` / `kv_get`. Never output Python or any other language.

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
Use `regex_find_all`, `from_json`, and `to_json`. Never `re_*` or `json_extract`.

```rhai
let raw_text = "Contact support@company.com or sales@company.net";
let emails = regex_find_all(raw_text, "[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}");
for email in emails {
    print("email=" + email);
}

let sample_json = "{\"status\":\"active\",\"id\":12345}";
let parsed = from_json(sample_json);
print("status=" + parsed.status);
print("id=" + parsed.id);
```

---

## 7. The Sandbox Security Gate Test: Deny-by-Default Validation
### Prompt
```
I need a ChaosNexus Anvil plugin that runs the `curl` command to fetch data from `https://api.github.com/zen`. Since I know ChaosNexus Anvil blocks shell commands and network requests by default, please provide the exact configuration changes needed in `ChaosNexus Anvil.toml` to allow this, alongside the plugin code itself.
```

### Response
Config file is `chaosnexus-anvil.toml`. Shell allowlist lives under `[plugins.<name>.permissions]` as `shell = [...]`. Prefer `run_command(exec, args)` for argv-style calls.

```toml
[plugins.github_zen.permissions]
shell = ["curl"]
```

```rhai
let result = run_command("curl", ["-s", "https://api.github.com/zen"]);
print("GitHub Zen: " + result);
```

---

## 8. The Pending Plugin Workflow Test: Human-In-The-Loop Approval
### Prompt
```
Write a Rhai script that uses `chaoswrench_install_plugin` to fetch a community plugin called "system_monitor". Once you've written the script, explain to me exactly how I approve and edit the plugin in the ChaosNexus Forge IDE before it goes live.
```

### Response
```rhai
// Use the built-in installer to pull a community plugin
chaoswrench_install_plugin("system_monitor");
```

**Approval & Editing Workflow in ChaosNexus Forge IDE**

1. **Discover / Create**  
   - Use `chaoswrench_install_plugin` or `chaoswrench_list_plugins` to find community plugins.  
   - If modifying a plugin, start from the approved version in Forge (never from local files).

2. **Open in Forge IDE**  
   - Click **Forge** → **Plugins**.  
   - Find your plugin (e.g., `system_monitor`) and open it.  
   - Forge loads the *approved* source, not your local filesystem.

3. **Edit**  
   - Write / refactor Rhai using the IDE’s syntax highlighting, autocomplete, and static analysis.  
   - Use real ChaosNexus Anvil host functions: `http_get`, from_json, to_json, sha256, base64_encode, db_connect, db_query, mcp_connect, mcp_call_command, register_mcp_command, register_cvar, get_cvar, sys_os, run_command, regex_match, regex_replace.  
   - Never output Python/Bash/Node.js tool-call markup such as <tool_call>.

4. **Run / Test**  
   - Top‑right **Run** button executes the current file in the sandbox.  
   - Use the console to inspect `print` output or `db_query` results.  
   - Write unit‑style checks: `assert(2+2 == 4)`.

5. **Submit for Review**  
   - **File → Save** stages the changes.  
   - Click **Review** (top bar).  
   - Fill justification (e.g., “adds CPU usage metric”).  
   - Choose reviewers (requires approval from another human).  

6. **Approve**  
   - As a reviewer, click **Approve**.  
   - Optionally add a comment.  
   - The plugin moves to **Pending Publish**.

7. **Publish**  
   - Final click **Publish** in the pending state.  
   - The new version is now live for all ChaosNexus Anvil instances.  

**Never** bypass these steps: local `chmod +x` or `curl | sh` to install plugins. Always go through Forge’s approval pipeline to maintain security and quality.

---

## 9. Domain 1: Event-Driven & Inter-Plugin Communication (Simple)
### Prompt
```
How do I use the ChaosNexus Anvil event bus to fire an event that another plugin can listen to? Show me how to use `create_event`, `hook_event`, and `fire_event`.
```

### Response
`create_event`, `hook_event`, and `fire_event` are **native ChaosNexus Anvil host functions** (not Rhai `emit`). They live in the event bus namespace.

```rhai
// Register a new event type
let my_event = create_event("my_event");

// Register a listener (callback receives payload)
hook_event(my_event, "on_my_event", fn(p) {
    print("my_event received: " + p);
});

// Fire the event (send payload)
fire_event(my_event, #{ source: "demo" });
```

---

## 10. Domain 1: Event-Driven & Inter-Plugin Communication (Complex)
### Prompt
```
We need a decentralized state manager. Write two plugins: the first plugin runs on a timer and writes a random number to the global KV store every 5 seconds, firing an event called 'state_updated'. The second plugin listens to 'state_updated', reads the new value from the global KV store, and logs it.
```

### Response
Plugin 1: state_updater.rhai

```rhai
fn on_state_update(_payload) {
    print("state_updated event received");
}

register_event_handler("state_updated", "on_state_update");

let interval = 5000; // 5 seconds
let func = "fn tick(_p) { emit_event('state_updated', #{}) }";
execute_timer(interval, "tick", #{});
```

Plugin 2: state_listener.rhai

```rhai
fn on_state_update(_payload) {
    let new_state = kv_get("shared_state");
    log_info("New state: " + new_state);
}

register_event_handler("state_updated", "on_state_update");
```

---

## 11. Domain 2: MCP Mesh Federation (Simple)
### Prompt
```
Show me how to connect to an external MCP server running on port 3000 using `mcp_connect`, call a tool named `get_weather`, and log the result.
```

### Response
`mcp_connect(conn_id, command, args)` spawns a stdio MCP process. Then `mcp_call(conn_id, tool, payload)` / `mcp_list_tools(conn_id)`.

```rhai
mcp_connect("weather", "npx", ["-y", "weather-mcp", "--port", "3000"]);
let tools = mcp_list_tools("weather");
print(to_json(tools));
let result = mcp_call("weather", "get_weather", #{ city: "Boston" });
log_info(to_json(result));
```

---

## 12. Domain 2: MCP Mesh Federation (Complex)
### Prompt
```
I need to act as an MCP router. Write a plugin that registers a new MCP tool called `router_ping`. When executed, this tool should connect to a downstream MCP server at `http://localhost:8080`, pass the arguments along, and return the aggregated response back up the chain.
```

### Response
`register_mcp_tool(tool_name, description, schema_json)` registers metadata (description must be ≥10 chars). Downstream hops use `mcp_connect(conn_id, command, args)` / `mcp_close(conn_id)`, not raw `http_get`. Schema is JSON, not Rhai.

```rhai
let schema = "{\"type\":\"object\",\"properties\":{\"msg\":{\"type\":\"string\"}}}";
register_mcp_tool("router_ping", "Ping a downstream MCP hop", schema);

// Separate handler / plugin path that performs the hop when the tool is invoked:
fn on_router_ping(_payload) {
    let out = mcp_connect("down", "run_command", #{ cmd: "ping", arg: "pong" });
    mcp_close("down");
    return #{ ok: true, result: out };
}
```

---

## 13. Domain 3: System Diagnostics & Monitoring (Simple)
### Prompt
```
How do I check the operating system that ChaosNexus Anvil is currently running on?
```

### Response
Prefer `run_command` / `system_os` from `http` or `net` rather than shelling out to `os` / `sys`.

```rhai
let os = system_os();
print("ChaosNexus Anvil OS: " + os);
```

---

## 14. Domain 3: System Diagnostics & Monitoring (Complex)
### Prompt
```
Write a watchdog plugin. It should use `create_timer` to wake up every 60 seconds, check the current OS using `sys_os`, and if the OS is 'windows', use `run_command` to execute `tasklist`. Log the output if successful, or log an error if it fails. Make sure to tell me what `chaosnexus-anvil.toml` capabilities are needed.
```

### Response
```toml
[plugins.watchdog.permissions]
shell = ["tasklist"]
```

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
`register_console_variable(name, default, desc)` or the newer `register_cvar(name, default, desc)`. Then `get_cvar(name)` / `cv_read(name)`. Never `parse` a raw string.

```rhai
register_cvar("debug_mode", "0", "Enable debug mode");

let mode = get_cvar("debug_mode");
print("debug_mode=" + mode);
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
    register_cvar("max_retries", max_retries.to_string(), "Retry budget");
} else {
    register_cvar("max_retries", "3", "Retry budget");
}
print("max_retries=" + get_cvar("max_retries"));
```

---

## 17. Domain 5: Advanced I/O (Simple)
### Prompt
```
Show me how to connect to a WebSocket endpoint using `ws_connect` and send a message.
```

### Response
`ws_connect(url, callback_name)` registers a named message handler. Close with `ws_close(url)`.

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
`fs_data_write` / `fs_data_read` are shared-fs primitives (not raw `fs_write` / `fs_read`). They require `shared_fs` capability and explicit path permissions.

**Permissions.toml**

```toml
[plugins.plugin_a.permissions]
http = ["WS"]
net_allowlist = ["echo.websocket.events"]
fs_shared = ["write", "list"]
fs_shared_path = ["shared/websocket_output.txt"]

[plugins.plugin_b.permissions]
fs_shared = ["read", "list"]
fs_shared_path = ["shared"]
```

**Plugin A (wssocket_a.toml + a.rhai)**

```toml
[plugins.plugin_a.capabilities]
http = ["WS"]
```

```rhai
fn on_ws_msg(text) {
    fs_data_write("shared/websocket_output.txt", text);
}

ws_connect("wss://echo.websocket.events", "on_ws_msg");
```

---

