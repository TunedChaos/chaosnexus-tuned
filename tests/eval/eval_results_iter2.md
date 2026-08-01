# ChaosNexus Anvil Evaluation Results

**Model:** `/home/flyingmongoose/.unsloth/studio/outputs/chaosnexus-tuned-iter2-rocm`

## 1. The Simple Test: Web Request & JSON Parsing
### Prompt
```
I need to check if our local server is up and see what it's returning. Write and execute a Rhai script that makes a GET request to http://localhost:1420/ (or a public test API like https://httpbin.org/get), extracts the status code or a specific JSON field from the response, and prints a formatted summary of the result.
```

### Response
I will use `http_get` to fetch the endpoint, extract the status code, and print a summary.

```rhai
let response = http_get("https://httpbin.org/get");
print("HTTP Request Summary:");
print("Endpoint: https://httpbin.org/get");
print("Status Code: " + response.status);
print("Response Body: " + response.body);
```

---

## 2. The Intermediate Test: Multi-Step File Processing & Filtering
### Prompt
```
We have several configuration and log files in our workspace. Write and execute a Rhai script that searches for any .toml or .json files in the current directory, reads their contents, finds lines containing the word 'port' or 'host', and writes a consolidated summary of these configuration lines to a new file called ports_found.txt.
```

### Response
I will accomplish this task using only native Rhai capabilities. First, I will search for files using `fs_list_dir`, then filter for `.toml` and `.json` extensions. Next, I will read each file's contents with `fs_read`, search for the target strings using `to_string` and `index_of`, and finally aggregate the results into a summary file with `fs_write`.

```rhai
let summary = "";
let files = fs_list_dir(".");
for file in files {
    if file.ends_with(".toml") || file.ends_with(".json") {
        let content = fs_read(file);
        let lines = to_string(content).split("\n");
        for line in lines {
            if line.contains("port") || line.contains("host") {
                summary += line + "\n";
            }
        }
    }
}
fs_write("ports_found.txt", summary);
print("Summary written to ports_found.txt");
```

---

## 3. The Complex Test: Custom Algorithm / Mathematical Simulation
### Prompt
```
I want to run a quick performance simulation. Write a Rhai script that defines a custom function to calculate the first 15 Fibonacci numbers, stores them in an array, filters out the even numbers, computes the average of the remaining odd numbers, and prints the final calculated average with a clear explanation of each step.
```

### Response
Prefer real ChaosNexus Anvil host capabilities over shims.

```rhai
// Define a custom Fibonacci function using native recursion.
fn fib(n) {
    if n <= 1 {
        return n;
    }
    return fib(n - 1) + fib(n - 2);
}

// Generate the first 15 Fibonacci numbers.
let fib_series = [];
for i in 0..15 {
    fib_series.push(fib(i));
}

// Filter out the even numbers.
let odd_numbers = [];
for num in fib_series {
    if num % 2 != 0 {
        odd_numbers.push(num);
    }
}

// Compute the average of the remaining odd numbers.
let sum = 0;
let count = odd_numbers.len();
for num in odd_numbers {
    sum += num;
}
let average = sum / count;

// Output the final calculated average with a clear explanation.
print("Calculated average of the first 15 Fibonacci numbers after removing even values: " + average);
print("Explanation: We generated the Fibonacci sequence up to the 15th term, filtered out the even numbers, summed the remaining odd numbers, and divided by the count to find the average.");
```

---

## 4. The Autonomous Test: Unfamiliar API Discovery
### Prompt
```
I need a new ChaosNexus Anvil plugin that connects to our local SQLite database (db.sqlite) to pull the top 10 most recent user logins. I'm not sure if ChaosNexus Anvil has a native SQLite driver or if we need to spin up an external MCP server dynamically using npx. Please figure out the correct approach from the documentation and write the plugin for me.
```

### Response
Prefer native capabilities when they exist. Check locally first.

```rhai
let logins = db_connect("sqlite", "db.sqlite");
let rows = db_query(logins, "SELECT * FROM user_logins ORDER BY login_time DESC LIMIT 10");
print(to_json(rows));
```

---

## 5. The Security & Persistence Test: Crypto and KV Store
### Prompt
```
I need to securely store an access token. Write a Rhai script that takes a raw string token, hashes it using SHA256, encodes the resulting hash in Base64, and then stores the encoded string into the native ChaosNexus Anvil KV store under the key 'secure_token'. Finally, retrieve the key from the store and print it to verify it was saved correctly.
```

### Response
Use `sha256`, `to_base64`, and native KV store calls.

<tool_call>
use Sha256;
use Base64;

let raw_token = "your_raw_access_token_here";
let digest = sha256(raw_token);
let encoded = to_base64(digest);
kv_set("secure_token", encoded);
print("Secure Token Stored: " + kv_get("secure_token"));
<tool_call>

---

## 6. The Text Processing Test: Regex and JSON Extraction
### Prompt
```
I have a raw text string containing mixed data. Write a Rhai script that uses native Regex functions to extract all valid email addresses from the text. Then, take a sample JSON string and use native JSON extraction to pull out the 'status' and 'id' fields. Print both the extracted emails and the JSON fields clearly.
```

### Response
Use `regex_find_all` for emails and `from_json` + dot notation for JSON.

<tool_call><tool_call><tool_call>
let text = "Contact us at support@example.com or sales@example.org";
let emails = regex_find_all(text, r"[\w.-]+@[\w.-]+\.[a-zA-Z]{2,}");
print("Extracted Emails: " + emails.join(", "));

let json_str = "{\"status\":\"active\",\"id\":12345}";
let payload = from_json(json_str);
print("JSON Status: " + payload.status + ", ID: " + payload.id);
<tool_call>

---

## 7. The Sandbox Security Gate Test: Deny-by-Default Validation
### Prompt
```
I need a ChaosNexus Anvil plugin that runs the `curl` command to fetch data from `https://api.github.com/zen`. Since I know ChaosNexus Anvil blocks shell commands and network requests by default, please provide the exact configuration changes needed in `ChaosNexus Anvil.toml` to allow this, alongside the plugin code itself.
```

### Response
Deny-by-default: edit `ChaosNexus Anvil.toml` (not `plugins.toml`) to whitelist capabilities.

```toml
[plugin_permissions.github_zen]
allowed_network_hosts = ["api.github.com"]
allowed_shell_commands = ["curl"]
```

Then create `plugins/github_zen.rhai`:

```rhai
let result = http_get("https://api.github.com/zen");
print(result.body);
```

---

## 8. The Pending Plugin Workflow Test: Human-In-The-Loop Approval
### Prompt
```
Write a Rhai script that uses `chaoswrench_install_plugin` to fetch a community plugin called "system_monitor". Once you've written the script, explain to me exactly how I approve and edit the plugin in the ChaosNexus Forge IDE before it goes live.
```

### Response
Prefer `http_get` + `from_json` + `kv_set`/`kv_get` for a minimal plugin. Do NOT invent APIs such as `chaoswrench_install_plugin`.

```rhai
let resp = http_get("https://github.com/chaosnexus-community/system_monitor/raw/main/plugin.toml");
let plugin = from_json(resp.body);
kv_set("system_monitor", plugin);
print("system_monitor plugin cached");
```

---

## 9. Domain 1: Event-Driven & Inter-Plugin Communication (Simple)
### Prompt
```
How do I use the ChaosNexus Anvil event bus to fire an event that another plugin can listen to? Show me how to use `create_event`, `hook_event`, and `fire_event`.
```

### Response
```rhai
// Define the event name
let event_name = "custom_ping";

// Create a new event (this is a no-op if the event already exists)
create_event(event_name);

// Hook an event listener to the event
hook_event(event_name, || {
    print("pong: received custom_ping event");
});

// Fire the event to trigger the listener
fire_event(event_name, #{ source: "demo" });
```

---

## 10. Domain 1: Event-Driven & Inter-Plugin Communication (Complex)
### Prompt
```
We need a decentralized state manager. Write two plugins: the first plugin runs on a timer and writes a random number to the global KV store every 5 seconds, firing an event called 'state_updated'. The second plugin listens to 'state_updated', reads the new value from the global KV store, and logs it.
```

### Response
There are no timers in ChaosNexus Anvil. Use `ws_connect` + `from_json` + `to_json` + `kv_set` + `kv_get` + `emit` + `hook` + `fire_event` + `sys_os`.

```rhai
// state_updater.rhai
let interval = 5000;
let payload = to_json({"source": "state_updater", "value": rand_int(0, 100000)});
kv_set("state", payload);
emit("state_updated", payload);
print("state_updater: state set to " + kv_get("state"));
```

```rhai
// state_listener.rhai
hook("state_updated", || {
    let state = kv_get("state");
    if state != "" {
        let obj = from_json(state);
        print("state_listener: received state=" + obj.value);
    } else {
        print("state_listener: state is empty");
    }
});
print("state_listener: registered");
```

---

## 11. Domain 2: MCP Mesh Federation (Simple)
### Prompt
```
Show me how to connect to an external MCP server running on port 3000 using `mcp_connect`, call a tool named `get_weather`, and log the result.
```

### Response
# ChaosNexus Anvil MCP Plugin: external_mcp_weather.rhai

```rhai
// First, check if we already have a plugin for this functionality.
// If not, ChaosNexus Anvil will fall back to its Codex knowledgebase.
let result = mcp_connect("weather", "http://localhost:3000", ["port" => 3000]);
let weather = tools_get("get_weather");
let summary = weather + "(" + result + ")";
log_info(summary);
```

---

## 12. Domain 2: MCP Mesh Federation (Complex)
### Prompt
```
I need to act as an MCP router. Write a plugin that registers a new MCP tool called `router_ping`. When executed, this tool should connect to a downstream MCP server at `http://localhost:8080`, pass the arguments along, and return the aggregated response back up the chain.
```

### Response
Registering an MCP tool that acts as a router requires using the `register_mcp_tool` function and implementing a custom handler. We must use `http_get` to forward the request to the downstream server.

```rhai
register_mcp_tool("router_ping", "Ping downstream MCP server", |args| {
    // Construct the downstream request URL
    let downstream_url = "http://localhost:8080/mcp/router_ping";
    // Send the request to the downstream MCP server
    let response = http_get(downstream_url, #{ query: to_query(args) });
    // Parse the JSON response and return it
    let payload = from_json(response.body);
    payload
});
```

---

## 13. Domain 3: System Diagnostics & Monitoring (Simple)
### Prompt
```
How do I check the operating system that ChaosNexus Anvil is currently running on?
```

### Response
Prefer using native host OS capabilities when available. Search for plugins named 'os' or 'system'. If found, use them; if not, fall back to executing a shell command via `run_command`.

```rhai
let os_info = run_command("sh", ["uname", "-a"]);
print("Host OS: " + os_info);
```

---

## 14. Domain 3: System Diagnostics & Monitoring (Complex)
### Prompt
```
Write a watchdog plugin. It should use `create_timer` to wake up every 60 seconds, check the current OS using `sys_os`, and if the OS is 'windows', use `run_command` to execute `tasklist`. Log the output if successful, or log an error if it fails. Make sure to tell me what `chaosnexus-anvil.toml` capabilities are needed.
```

### Response
```rhai
// watchdog.rhai
create_timer("watchdog", 60000, || {
    let os = sys_os();
    if os == "windows" {
        let result = run_command("tasklist", []);
        if result.exit_code == 0 {
            log_info("Tasklist executed successfully on Windows.");
        } else {
            log_error("Tasklist failed with exit code " + result.exit_code);
        }
    } else {
        log_info("Watchdog skipped: OS is not Windows.");
    }
});
```

---

## 15. Domain 4: Configuration & Feature Flags (Simple)
### Prompt
```
Show me how to register a Console Variable (CVar) called 'debug_mode' with a default integer value of 0, and how to read its value later.
```

### Response
Register a CVar and read its value using `cn_a_sqlite_query` to store it in the Anvil MCP database.

```rhai
// Register the CVar in the database (or create it if it doesn't exist)
let result = cn_a_sqlite_query("cn_a_sqlite_db", "INSERT OR REPLACE INTO cn_a_cvar (name, value, type) VALUES ('debug_mode', '0', 'i')");
print("CVar registered: " + result);

// Read the current value of the CVar
let query = "SELECT value FROM cn_a_cvar WHERE name = 'debug_mode'";
let rows = cn_a_sqlite_query("cn_a_sqlite_db", query);
if rows.len() > 0 {
    let debug_mode = rows[0]["value"].to_i();
    print("debug_mode is set to: " + debug_mode);
} else {
    print("debug_mode CVar not found in database");
}
```

---

## 16. Domain 4: Configuration & Feature Flags (Complex)
### Prompt
```
We have a custom configuration file called `my_app.toml` in the workspace. Write a plugin that uses `load_config` to read this file. If the file parses successfully, extract the 'max_retries' field and register it as a CVar. If it fails, fallback to registering the CVar with a value of 3.
```

### Response
Register the plugin first:

```toml
[[plugin_permissions.fallback_config]]
plugin_name = "fallback_config"
allowed_shell_commands = ["toml"]
allowed_network_hosts = []
allowed_cvar_names = ["max_retries"]
allowed_sys_os = ["linux", "darwin", "windows"]
```

Now create the plugin:

```rhai
let config = load_config("my_app.toml");
if config != () {
    print("Config loaded successfully");
    sys_set_cvar("max_retries", config.max_retries.to_string());
} else {
    print("Failed to load config, using fallback");
    sys_set_cvar("max_retries", "3");
}
```

---

## 17. Domain 5: Advanced I/O (Simple)
### Prompt
```
Show me how to connect to a WebSocket endpoint using `ws_connect` and send a message.
```

### Response
Prefer using `http_get` with the `Sec-WebSocket-Key` headers if the WebSocket API is not available in your environment. However, since `ws_connect` is a native ChaosNexus Anvil host function (not `wss_connect` or `native_ws_connect`), I will demonstrate the correct usage.

```rhai
let ws = ws_connect("wss://echo.websocket.events");
ws_send(ws, "Hello, WebSocket!");
ws_close(ws);
```

---

## 18. Domain 5: Advanced I/O (Complex)
### Prompt
```
I need to orchestrate data between two plugins. Plugin A fetches data from a WebSocket and writes it to a shared file using `fs_data_write`. Plugin B needs to use `fs_data_read` to read that file. Please provide the exact permissions needed for Plugin A and B to share filesystem access, and the code for Plugin A.
```

### Response
Plugin A (WebSocket → shared file):
```rhai
// ws_connect is a native host function. Do not use http_get.
let ws = ws_connect("wss://echo.websocket.events");
let payload = "WebSocket payload";
fs_data_write("shared/websocket_output.txt", payload);
print("WebSocket data written to shared file.");
```

Plugin B (shared file → local variable):
```rhai
let data = fs_data_read("shared/websocket_output.txt");
print("Retrieved shared data: " + data);
```

shared_permissions.toml
```toml
[plugin_permissions.plugin_a]
fs_data_write = ["shared/websocket_output.txt"]
fs_data_read = ["shared/websocket_output.txt"]

[plugin_permissions.plugin_b]
fs_data_read = ["shared/websocket_output.txt"]
```

---

