# chaosnexus-tuned/scripts/injectors/inject_iter3_api_goldens.py
"""Build iter-3 goldens-only train JSONL from real Anvil host signatures.

Unlike iter-2, this injector does **not** merge the augmented ShareGPT corpus
(tool-call residue). Every row is curated against ``chaosnexus-anvil`` Rust
bindings and upsampled so loss focuses on exact APIs.
"""

from __future__ import annotations

import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "datasets" / "iter3"
OUT_JSONL = OUT_DIR / "train.jsonl"

EVAL_SYSTEM = (
    "You are an elite Workspace Systems Architect. You master the ChaosNexus Anvil MCP. "
    "You autonomously discover and leverage capabilities provided by your workspace environment. "
    "You MUST ONLY write Rhai scripts when creating plugins. NEVER output Python, Bash, Node.js, "
    "or any other language. Never emit XML tool-call markup such as <tool_call>. "
    "Always search for plugins before creating one. "
    "Use only real ChaosNexus Anvil host functions: http_get, from_json, to_json, json_extract, "
    "kv_set, kv_get, sha256, base64_encode, db_connect, db_query, db_execute, "
    "mcp_connect, mcp_call_tool, mcp_list_tools, register_mcp_tool, "
    "register_cvar, get_cvar, sys_os, run_command, regex_match, regex_replace, "
    "ws_connect, ws_close, create_event, hook_event, fire_event, create_timer, "
    "fs_read, write_file_string, list_dir, load_config, fs_data_read, fs_data_write, "
    "cn_a_install_plugin. "
    "Never invent APIs such as sqlite_query, parse_json, to_base64, kv_store_set, "
    "emit_event, regex_find_all, cn_a_sqlite_query, or sys_set_cvar."
)


def row(user: str, assistant: str) -> dict:
    return {
        "messages": [
            {"role": "system", "content": EVAL_SYSTEM},
            {"role": "user", "content": user},
            {"role": "assistant", "content": assistant},
        ]
    }


def goldens() -> list[dict]:
    g: list[dict] = []

    # --- 1 HTTP ---
    g.append(
        row(
            "I need to check if our local server is up and see what it's returning. Write a Rhai script that makes a GET request to https://httpbin.org/get, extracts a JSON field from the response, and prints a formatted summary.",
            """Use `http_get` + `from_json`. Allowlist the host in `chaosnexus-anvil.toml`.

```toml
[plugins.check_http.permissions]
http = ["GET"]
net_allowlist = ["httpbin.org"]
```

```rhai
let raw = http_get("https://httpbin.org/get");
let body = from_json(raw);
print("HTTP summary origin=" + body.origin);
```""",
        )
    )

    # --- 2 Files (plugin-local; real names are list_dir / write_file_string / fs_read) ---
    g.append(
        row(
            "Write and execute a Rhai script that searches for any .toml or .json files in the current directory, reads their contents, finds lines containing the word 'port' or 'host', and writes a consolidated summary to ports_found.txt.",
            """Plugin-local FS uses `list_dir`, `fs_read`, and `write_file_string` (not invented `fs_list_dir`/`fs_write` aliases unless your build exposes them).

```rhai
let summary = "";
let files = list_dir(".");
for file in files {
    if file.ends_with(".toml") || file.ends_with(".json") {
        let content = fs_read(file);
        let lines = content.split("\\n");
        for line in lines {
            if line.contains("port") || line.contains("host") {
                summary += line + "\\n";
            }
        }
    }
}
write_file_string("ports_found.txt", summary);
print("Summary written to ports_found.txt");
```""",
        )
    )

    # --- 3 Fibonacci ---
    g.append(
        row(
            "Write a Rhai script that defines a custom function to calculate the first 15 Fibonacci numbers, stores them in an array, filters out the even numbers, computes the average of the remaining odd numbers, and prints the final calculated average.",
            """```rhai
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
let average = sum / odds.len();
print("Average of odd Fibonacci numbers: " + average);
```""",
        )
    )

    # --- 4 SQLite docs-first ---
    g.append(
        row(
            "I need a new ChaosNexus Anvil plugin that connects to our local SQLite database (db.sqlite) to pull the top 10 most recent user logins. I'm not sure if ChaosNexus Anvil has a native SQLite driver or if we need to spin up an external MCP server dynamically using npx. Please figure out the correct approach from the documentation and write the plugin for me.",
            """Docs-first: use native `db_connect(id, url)` and `db_query(id, sql, params)`. Do not invent `sqlite_query` / `cn_a_sqlite_*`, and do not cargo-install an MCP for SQLite.

```toml
[plugins.logins.permissions]
sql = ["SELECT"]
sql_urls = ["sqlite://"]
```

```rhai
db_connect("logins", "sqlite://db.sqlite");
let rows = db_query(
    "logins",
    "SELECT * FROM user_logins ORDER BY login_time DESC LIMIT 10",
    []
);
for row in rows {
    print(to_json(row));
}
```""",
        )
    )

    g.append(
        row(
            "Write Rhai that queries SQLite using sqlite_query('db.sqlite', 'SELECT 1').",
            """`sqlite_query` is not a host function. Use `db_connect` + `db_query`.

```rhai
db_connect("db", "sqlite://db.sqlite");
let rows = db_query("db", "SELECT 1 AS ok", []);
print(to_json(rows));
```""",
        )
    )

    g.append(
        row(
            "Call cn_a_sqlite_query to read from db.sqlite.",
            """There is no `cn_a_sqlite_query`. SQLite goes through `db_connect` / `db_query`.

```rhai
db_connect("db", "sqlite://db.sqlite");
let rows = db_query("db", "SELECT 1", []);
print(to_json(rows));
```""",
        )
    )

    # --- 5 Crypto + KV ---
    g.append(
        row(
            "I need to securely store an access token. Write a Rhai script that takes a raw string token, hashes it using SHA256, encodes the resulting hash in Base64, and then stores the encoded string into the native ChaosNexus Anvil KV store under the key 'secure_token'. Finally, retrieve the key from the store and print it to verify it was saved correctly.",
            """Use `sha256`, `base64_encode`, `kv_set`, `kv_get`. Never `to_base64` or `kv_store_*`.

```rhai
let raw_token = "your_raw_access_token_here";
let digest = sha256(raw_token);
let encoded = base64_encode(digest);
kv_set("secure_token", encoded);
let retrieved = kv_get("secure_token");
print("Secure Token Stored and Retrieved: " + retrieved);
```""",
        )
    )

    g.append(
        row(
            "Encode with to_base64(sha256(x)) and kv_store_set.",
            """Correct hosts: `base64_encode`, `kv_set`, `kv_get`.

```rhai
let encoded = base64_encode(sha256("secret"));
kv_set("secure_token", encoded);
print(kv_get("secure_token"));
```""",
        )
    )

    # --- 6 Regex + JSON ---
    g.append(
        row(
            "Write a Rhai script that uses native Regex functions to extract all valid email addresses from sample text, then use native JSON extraction to pull 'status' and 'id' from a JSON string.",
            """`regex_match(pattern, text)` returns an **array** of matches (not a bool). Use `json_extract` / `from_json`. Never `regex_find_all` or `parse_json`.

```rhai
let raw_text = "Contact support@company.com or sales@company.net";
let emails = regex_match("[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\\\.[A-Za-z]{2,}", raw_text);
for email in emails {
    print("email=" + email);
}

let payload = "{\\"status\\":\\"active\\",\\"id\\":12345}";
let status = json_extract(payload, "/status");
let id = json_extract(payload, "/id");
print("status=" + status + " id=" + id);
```""",
        )
    )

    # --- 7 Deny-by-default curl ---
    g.append(
        row(
            "I need a ChaosNexus Anvil plugin that runs the `curl` command to fetch data from `https://api.github.com/zen`. Since I know ChaosNexus Anvil blocks shell commands and network requests by default, please provide the exact configuration changes needed in ChaosNexus Anvil.toml to allow this, alongside the plugin code itself.",
            """Config file is `chaosnexus-anvil.toml`. Shell allowlist lives under `[plugins.<name>.permissions]` as `shell = [...]`. Prefer `run_command(exec, args)` for argv-style calls.

```toml
[plugins.github_zen.permissions]
shell = ["curl"]
```

```rhai
let result = run_command("curl", ["-s", "https://api.github.com/zen"]);
print("GitHub Zen: " + result);
```""",
        )
    )

    # --- 8 HITL install ---
    g.append(
        row(
            "Write a Rhai script that uses chaoswrench_install_plugin to fetch a community plugin called system_monitor. Explain how I approve it in ChaosNexus Forge before it goes live.",
            """The real host is `cn_a_install_plugin` (requires Install capability). It stages a pending plugin for human approval in Forge.

```rhai
let result = cn_a_install_plugin("system_monitor");
print("install staged: " + result);
```

Then in ChaosNexus Forge: Pending plugins → review Rhai + permissions → Approve. Anvil loads only after approval.""",
        )
    )

    # --- 9 Events (string callbacks, not closures) ---
    g.append(
        row(
            "How do I use the ChaosNexus Anvil event bus to fire an event that another plugin can listen to? Show me create_event, hook_event, and fire_event.",
            """`hook_event` takes an event name and a **callback function name** (string), not a Rhai closure.

```rhai
fn on_demo_ping(data) {
    print("demo_ping received: " + to_json(data));
}

create_event("demo_ping");
hook_event("demo_ping", "on_demo_ping");
fire_event("demo_ping", #{ source: "example" });
```""",
        )
    )

    # --- 10 Timers + KV + events ---
    g.append(
        row(
            "Write two plugins: one timer writes a random number to KV every 5 seconds and fires state_updated; another listens and logs the value. Use emit_event.",
            """There is no `emit_event`. Use `fire_event`. `create_timer(ms, repeat, callback_name, payload)` uses a named callback.

```rhai
// updater.rhai
fn on_tick(_payload) {
    let n = rand(0, 1000);
    kv_set("shared_state", n.to_string());
    fire_event("state_updated", #{});
}

create_event("state_updated");
create_timer(5000, true, "on_tick", #{});

// listener.rhai
fn on_state(_data) {
    let v = kv_get("shared_state");
    log_info("state=" + v);
}

hook_event("state_updated", "on_state");
```""",
        )
    )

    g.append(
        row(
            "Refuse create_timer and invent emit() instead.",
            """Do not invent `emit`. Prefer the real timer + event APIs.

```rhai
fn tick(_p) {
    fire_event("heartbeat", #{});
}
create_event("heartbeat");
create_timer(1000, true, "tick", #{});
```""",
        )
    )

    # --- 11 MCP client ---
    g.append(
        row(
            "Show me how to connect to an external MCP server running on port 3000 using mcp_connect, call a tool named get_weather, and log the result.",
            """`mcp_connect(conn_id, command, args)` spawns a stdio MCP process. Then `mcp_list_tools` / `mcp_call_tool`.

```rhai
mcp_connect("weather", "npx", ["-y", "weather-mcp", "--port", "3000"]);
let tools = mcp_list_tools("weather");
print(to_json(tools));
let result = mcp_call_tool("weather", "get_weather", #{ city: "Boston" });
log_info(to_json(result));
```""",
        )
    )

    # --- 12 MCP router ---
    g.append(
        row(
            "I need to act as an MCP router. Write a plugin that registers a new MCP tool called router_ping. When executed, connect to a downstream MCP server at http://localhost:8080, pass arguments along, and return the aggregated response.",
            """`register_mcp_tool(tool_name, description, schema_json)` registers metadata (description must be ≥10 chars). Downstream hops use `mcp_connect` + `mcp_call_tool`, not raw `http_get` pretending to be MCP.

```rhai
let schema = "{\\"type\\":\\"object\\",\\"properties\\":{\\"msg\\":{\\"type\\":\\"string\\"}}}";
register_mcp_tool("router_ping", "Ping a downstream MCP tool hop", schema);

// Separate handler / plugin path that performs the hop when the tool is invoked:
mcp_connect("down", "node", ["downstream-mcp.js"]);
let out = mcp_call_tool("down", "ping", #{ msg: "hi" });
print(to_json(out));
```""",
        )
    )

    # --- 13 sys_os ---
    g.append(
        row(
            "How do I check the operating system that ChaosNexus Anvil is currently running on?",
            """Prefer `sys_os()` over shelling out to `uname`.

```rhai
let os = sys_os();
print("ChaosNexus Anvil OS: " + os);
```""",
        )
    )

    # --- 14 Watchdog ---
    g.append(
        row(
            "Write a watchdog plugin. It should use create_timer to wake up every 60 seconds, check the current OS using sys_os, and if the OS is 'windows', use run_command to execute tasklist. Log the output. Tell me what chaosnexus-anvil.toml capabilities are needed.",
            """```toml
[plugins.watchdog.permissions]
shell = ["tasklist"]
```

```rhai
fn on_watchdog(_payload) {
    let os = sys_os();
    if os == "windows" {
        let out = run_command("tasklist", []);
        log_info(out);
    } else {
        log_info("watchdog skip non-windows os=" + os);
    }
}

create_timer(60000, true, "on_watchdog", #{});
```""",
        )
    )

    # --- 15 CVars ---
    g.append(
        row(
            "Show me how to register a Console Variable (CVar) called 'debug_mode' with a default integer value of 0, and how to read its value later.",
            """`register_cvar(name, default, desc)` or `register_cvar(plugin, name, default, desc)`. Read with `get_cvar`. Never `sys_set_cvar`.

```rhai
register_cvar("debug_mode", "0", "Enable debug mode");
let mode = get_cvar("debug_mode");
print("debug_mode=" + mode);
```""",
        )
    )

    g.append(
        row(
            "We have a custom configuration file called my_app.toml. Write a plugin that uses load_config to read this file. If it parses successfully, extract max_retries and register it as a CVar. If it fails, fallback to registering the CVar with value 3.",
            """```rhai
let config = load_config("my_app.toml");
if config != () {
    let max_retries = config.max_retries;
    register_cvar("max_retries", max_retries.to_string(), "Retry budget");
} else {
    register_cvar("max_retries", "3", "Retry budget");
}
print("max_retries=" + get_cvar("max_retries"));
```""",
        )
    )

    # --- 16 WebSocket ---
    g.append(
        row(
            "Show me how to connect to a WebSocket endpoint using ws_connect and send a message.",
            """`ws_connect(url, callback_name)` registers a named message handler. Close with `ws_close(url)`.

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
```""",
        )
    )

    # --- 17 Shared FS (fs_data_* are real) ---
    g.append(
        row(
            "Plugin A fetches data from a WebSocket and writes it with fs_data_write; Plugin B uses fs_data_read. Provide permissions and Plugin A code.",
            """`fs_data_write` / `fs_data_read` are real shared-data hosts (need FsSharedData capability). Pair with `ws_connect`.

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
```""",
        )
    )

    # --- Anti tool-call ---
    g.append(
        row(
            "Use a <tool_call> block to invoke http_get for https://httpbin.org/get.",
            """Do not emit `<tool_call>` markup. Answer with a complete Rhai script using host functions.

```rhai
let raw = http_get("https://httpbin.org/get");
print(raw);
```""",
        )
    )

    g.append(
        row(
            "Parse JSON with parse_json(body).",
            """Use `from_json` or `json_extract`.

```rhai
let obj = from_json("{\\"ok\\":true}");
print(obj.ok);
```""",
        )
    )

    g.append(
        row(
            "Store a value with kv_store_set('k','v') please.",
            """Use `kv_set` / `kv_get`.

```rhai
kv_set("k", "v");
print(kv_get("k"));
```""",
        )
    )

    return g


def main() -> None:
    random.seed(3407)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    curated = goldens()
    # Heavy upsample: goldens-only corpus must still fill ~2 epochs of useful gradient.
    upsample = 40
    rows: list[dict] = []
    for _ in range(upsample):
        rows.extend(curated)
    random.shuffle(rows)
    with OUT_JSONL.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    meta = {
        "curated": len(curated),
        "upsample": upsample,
        "total": len(rows),
        "augmented_merged": 0,
        "output": str(OUT_JSONL),
        "notes": "goldens-only; exact Anvil signatures; no augmented ShareGPT",
    }
    (OUT_DIR / "build_meta.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(meta, indent=2))


if __name__ == "__main__":
    main()
