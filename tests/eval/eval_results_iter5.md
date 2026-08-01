# ChaosNexus Anvil Evaluation Results

**Model:** `/home/flyingmongoose/.unsloth/studio/outputs/chaosnexus-tuned-iter5-rocm`

**Decode:** greedy (`do_sample=False`)

## 1. The Simple Test: Web Request & JSON Parsing
### Prompt
```
I need to check if our local server is up and see what it's returning. Write and execute a Rhai script that makes a GET request to http://localhost:1420/ (or a public test API like https://httpbin.org/get), extracts the status code or a specific JSON field from the response, and prints a formatted summary of the result.
```

### Response
```toml
[plugins.check_http.permissions]
http = ["GET"]
net_allowlist = ["http://localhost", "https://httpbin.org"]
```

```rhai
let raw = http_get("https://httpbin.org/get");
let body = from_json(raw);
print("status=" + body.status + ", origin=" + body.origin);
```

---

## 2. The Intermediate Test: Multi-Step File Processing & Filtering
### Prompt
```
We have several configuration and log files in our workspace. Write and execute a Rhai script that searches for any .toml or .json files in the current directory, reads their contents, finds lines containing the word 'port' or 'host', and writes a consolidated summary of these configuration lines to a new file called ports_found.txt.
```

### Response
```rhai
let summary = "";
let files = list_dir(".");
for file in files {
    if file.ends_with(".toml") || file.ends_with(".json") {
        let content = fs_read(file);
        for line in content.split("\n") {
            if line.contains("port") || line.contains("host") {
                summary += line + "\n";
            }
        }
    }
}
write_file_string("ports_found.txt", summary);
print("wrote ports_found.txt");
```

---

## 3. The Complex Test: Custom Algorithm / Mathematical Simulation
### Prompt
```
I want to run a quick performance simulation. Write a Rhai script that defines a custom function to calculate the first 15 Fibonacci numbers, stores them in an array, filters out the even numbers, computes the average of the remaining odd numbers, and prints the final calculated average with a clear explanation of each step.
```

### Response
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
for num in fib_15 {
    if num % 2 != 0 {
        odds.push(num);
    }
}
let sum = 0;
for num in odds {
    sum += num;
}
print("The average of the first 15 Fibonacci numbers' odd values is " + (sum / odds.len()) + ".");
```

---

## 4. The Autonomous Test: Unfamiliar API Discovery
### Prompt
```
I need a new ChaosNexus Anvil plugin that connects to our local SQLite database (db.sqlite) to pull the top 10 most recent user logins. I'm not sure if ChaosNexus Anvil has a native SQLite driver or if we need to spin up an external MCP server dynamically using npx. Please figure out the correct approach from the documentation and write the plugin for me.
```

### Response
```rhai
let db = sqlite_connect("sqlite://db.sqlite");
let rows = db.query(
    "SELECT * FROM user_logins ORDER BY login_time DESC LIMIT 10",
);
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
```rhai
let digest = sha256("raw_access_token_here");
let encoded = base64_encode(digest);
kv_set("secure_token", encoded);
print(kv_get("secure_token"));
```

---

## 6. The Text Processing Test: Regex and JSON Extraction
### Prompt
```
I have a raw text string containing mixed data. Write a Rhai script that uses native Regex functions to extract all valid email addresses from the text. Then, take a sample JSON string and use native JSON extraction to pull out the 'status' and 'id' fields. Print both the extracted emails and the JSON fields clearly.
```

### Response
```rhai
let text = "Contact support@company.com or sales@company.net for assistance.";
let emails = [];
let regex = regex("([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,})");
for match in regex_matches(text, regex) {
    emails.push(match);
}
print_list(emails);

let json = "{\"status\":\"active\",\"id\":12345}";
let parsed = from_json(json);
print_value("status", parsed["status"]);
print_value("id", parsed["id"]);
```

---

## 7. The Sandbox Security Gate Test: Deny-by-Default Validation
### Prompt
```
I need a ChaosNexus Anvil plugin that runs the `curl` command to fetch data from `https://api.github.com/zen`. Since I know ChaosNexus Anvil blocks shell commands and network requests by default, please provide the exact configuration changes needed in `ChaosNexus Anvil.toml` to allow this, alongside the plugin code itself.
```

### Response
```toml
[plugins.github_zen.permissions]
shell = ["curl"]
net_allowlist = ["api.github.com"]
```

```rhai
fn github_zen() {
    let result = run_command("curl", ["-s", "https://api.github.com/zen"]);
    print(result);
}
```

---

## 8. The Pending Plugin Workflow Test: Human-In-The-Loop Approval
### Prompt
```
Write a Rhai script that uses `chaoswrench_install_plugin` to fetch a community plugin called "system_monitor". Once you've written the script, explain to me exactly how I approve and edit the plugin in the ChaosNexus Forge IDE before it goes live.
```

### Response
```rhai
let schema = "{\"type\":\"object\",\"properties\":{\"cpu\":{\"type\":\"number\"},\"memory\":{\"type\":\"number\"}}}";
print(chaoswrench_install_plugin("system_monitor", "Monitors CPU and memory usage", schema));
```

---

## 9. Domain 1: Event-Driven & Inter-Plugin Communication (Simple)
### Prompt
```
How do I use the ChaosNexus Anvil event bus to fire an event that another plugin can listen to? Show me how to use `create_event`, `hook_event`, and `fire_event`.
```

### Response
```rhai
fn on_demo_ping(data) {
    print(to_json(data));
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
```rhai
// updater.rhai
fn on_tick(_payload) {
    kv_set("shared_state", rand(0, 1000).to_string());
    fire_event("state_updated", #{});
}
create_event("state_updated");
create_timer(5000, true, "on_tick", #{});

// logger.rhai
fn on_state(_data) {
    log_info(kv_get("shared_state"));
}
hook_event("state_updated", "on_state");
```

---

## 11. Domain 2: MCP Mesh Federation (Simple)
### Prompt
```
Show me how to connect to an external MCP server running on port 3000 using `mcp_connect`, call a tool named `get_weather`, and log the result.
```

### Response
```rhai
mcp_connect("weather", "npx", ["-y", "weather-mcp", "--port", "3000"]);
print(to_json(mcp_list_tools("weather")));
log_info(to_json(mcp_call_tool("weather", "get_weather", #{ city: "Boston" })));
```

---

## 12. Domain 2: MCP Mesh Federation (Complex)
### Prompt
```
I need to act as an MCP router. Write a plugin that registers a new MCP tool called `router_ping`. When executed, this tool should connect to a downstream MCP server at `http://localhost:8080`, pass the arguments along, and return the aggregated response back up the chain.
```

### Response
```rhai
let schema = "{\"type\":\"object\",\"properties\":{\"msg\":{\"type\":\"string\"}}}";
register_mcp_tool("router_ping", "Ping a downstream MCP tool hop", schema);
mcp_connect("down", "node", ["downstream-mcp.js"]);
print(to_json(mcp_call_tool("down", "ping", #{ msg: "hi" })));
```

---

## 13. Domain 3: System Diagnostics & Monitoring (Simple)
### Prompt
```
How do I check the operating system that ChaosNexus Anvil is currently running on?
```

### Response
```rhai
print(sys_os());
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
    if sys_os() == "windows" {
        let out = run_command("tasklist", []);
        if out.is_ok() {
            log_info(out.unwrap());
        } else {
            log_error("failed to run tasklist");
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
```rhai
register_cvar("debug_mode", "0", "Enable debug mode");
print(get_cvar("debug_mode"));
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
    register_cvar("max_retries", config.max_retries.to_string(), "Retry budget");
} else {
    register_cvar("max_retries", "3", "Retry budget");
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
```rhai
let out = ws_connect("wss://echo.websocket.events");
if out.is_ok() {
    print(to_json(out.ok()));
} else {
    print(to_json(out.err()));
}
ws_send(out, "Hello, WebSocket!");
```

---

## 18. Domain 5: Advanced I/O (Complex)
### Prompt
```
I need to orchestrate data between two plugins. Plugin A fetches data from a WebSocket and writes it to a shared file using `fs_data_write`. Plugin B needs to use `fs_data_read` to read that file. Please provide the exact permissions needed for Plugin A and B to share filesystem access, and the code for Plugin A.
```

### Response
```toml
[plugins.plugin_a]
granted_capabilities = ["fs_shared_data", "net_ws"]

[plugins.plugin_a.permissions]
http = ["WS"]
net_allowlist = ["echo.websocket.events"]

[plugins.plugin_b]
granted_capabilities = ["fs_shared_data"]
```

```rhai
fn on_ws_msg(text) {
    fs_data_write("shared/websocket_output.txt", text);
}
ws_connect("wss://echo.websocket.events", "on_ws_msg");
```

---

