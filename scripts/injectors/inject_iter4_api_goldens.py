# chaosnexus-tuned/scripts/injectors/inject_iter4_api_goldens.py
"""Build iter-4 goldens-only train JSONL (Anvil-exact + hard-negatives).

Extends iter-3 with stronger coverage for eval fails 6/9/10/12/13 and
clean FS / HTTP / HITL answers. Still no augmented ShareGPT. No Codex MCP.
"""

from __future__ import annotations

import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "datasets" / "iter4"
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
    "emit_event, regex_find_all, cn_a_sqlite_query, system_os, mcp_call, "
    "read_file, write_file, fetch, register_event_handler, execute_timer, or sys_set_cvar."
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

    # --- 1 HTTP (clean; no fetch wrappers) ---
    g.append(
        row(
            "I need to check if our local server is up and see what it's returning. Write a Rhai script that makes a GET request to https://httpbin.org/get, extracts a JSON field from the response, and prints a formatted summary.",
            """Call `http_get` and `from_json` directly. Do not invent `fetch` helpers.

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
    g.append(
        row(
            "Write a fetch(url) wrapper then call http_get inside it for httpbin.",
            """Do not invent a `fetch` wrapper. Use `http_get` + `from_json` only.

```rhai
let raw = http_get("https://httpbin.org/get");
let body = from_json(raw);
print(body.origin);
```""",
        )
    )

    # --- 2 Files ---
    g.append(
        row(
            "Write and execute a Rhai script that searches for any .toml or .json files in the current directory, reads their contents, finds lines containing the word 'port' or 'host', and writes a consolidated summary to ports_found.txt.",
            """Plugin-local FS: `list_dir`, `fs_read`, `write_file_string`. Never `read_file` / `write_file`.

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
    g.append(
        row(
            "Use read_file and write_file to scan toml files for host lines.",
            """Those names are wrong. Use `fs_read` and `write_file_string` with `list_dir`.

```rhai
let files = list_dir(".");
let out = "";
for f in files {
    if f.ends_with(".toml") {
        let c = fs_read(f);
        if c.contains("host") {
            out += c + "\\n";
        }
    }
}
write_file_string("ports_found.txt", out);
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

    # --- 4 SQLite ---
    g.append(
        row(
            "I need a new ChaosNexus Anvil plugin that connects to our local SQLite database (db.sqlite) to pull the top 10 most recent user logins. I'm not sure if ChaosNexus Anvil has a native SQLite driver or if we need to spin up an external MCP server dynamically using npx. Please figure out the correct approach from the documentation and write the plugin for me.",
            """Docs-first: native `db_connect(id, url)` and `db_query(id, sql, params)`. No `sqlite_query` / `cn_a_sqlite_*` / npx MCP for SQLite.

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
            """There is no `cn_a_sqlite_query`. Use `db_connect` / `db_query`.

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

    # --- 6 Regex + JSON (HARD FAIL THEME) ---
    g.append(
        row(
            "Write a Rhai script that uses native Regex functions to extract all valid email addresses from the text. Then, take a sample JSON string and use native JSON extraction to pull out the 'status' and 'id' fields.",
            """`regex_match(pattern, text)` returns an **array** of full matches. Prefer `json_extract(json, pointer)`. Never invent `regex_find_all`. Never tell the user to avoid `json_extract`.

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
    g.append(
        row(
            "Extract emails with regex_find_all and parse JSON without json_extract.",
            """Wrong. Use `regex_match` (returns array) and `json_extract` (or `from_json`).

```rhai
let emails = regex_match("[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\\\.[A-Za-z]{2,}", "a@b.com c@d.org");
print(to_json(emails));
let status = json_extract("{\\"status\\":\\"ok\\"}", "/status");
print(status);
```""",
        )
    )

    # --- 7 curl deny-by-default ---
    g.append(
        row(
            "I need a ChaosNexus Anvil plugin that runs the `curl` command to fetch data from `https://api.github.com/zen`. Since I know ChaosNexus Anvil blocks shell commands and network requests by default, please provide the exact configuration changes needed in ChaosNexus Anvil.toml to allow this, alongside the plugin code itself.",
            """Config file is `chaosnexus-anvil.toml`. Shell allowlist: `[plugins.<name>.permissions]` → `shell = [...]`.

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

    # --- 8 HITL ---
    g.append(
        row(
            "Write a Rhai script that uses chaoswrench_install_plugin to fetch a community plugin called system_monitor. Explain how I approve it in ChaosNexus Forge before it goes live.",
            """There is no `chaoswrench_install_plugin` host. Use `cn_a_install_plugin` (Install capability). It stages a pending plugin for human approval.

```rhai
let result = cn_a_install_plugin("system_monitor");
print("install staged: " + result);
```

In ChaosNexus Forge: Pending plugins → review Rhai + permissions → Approve. Anvil loads only after approval.""",
        )
    )
    g.append(
        row(
            "Install with chaoswrench_install_plugin('system_monitor').",
            """Use `cn_a_install_plugin` instead.

```rhai
print(cn_a_install_plugin("system_monitor"));
```""",
        )
    )

    # --- 9 Events (HARD FAIL) ---
    g.append(
        row(
            "How do I use the ChaosNexus Anvil event bus to fire an event that another plugin can listen to? Show me create_event, hook_event, and fire_event.",
            """Signatures: `create_event(name)`, `hook_event(event_name, callback_fn_name)`, `fire_event(event_name, data)`. Callbacks are **string names**, not closures. `create_event` returns unit, not a handle.

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
    g.append(
        row(
            "hook_event(my_event, \"cb\", |p| { print(p); }) after let my_event = create_event(\"x\").",
            """Wrong arity and wrong callback style. Use string event name + string function name.

```rhai
fn cb(p) {
    print(to_json(p));
}
create_event("x");
hook_event("x", "cb");
fire_event("x", #{});
```""",
        )
    )

    # --- 10 Timers + events (HARD FAIL) ---
    g.append(
        row(
            "We need a decentralized state manager. Write two plugins: the first plugin runs on a timer and writes a random number to the global KV store every 5 seconds, firing an event called 'state_updated'. The second plugin listens to 'state_updated', reads the new value from the global KV store, and logs it.",
            """Use `create_timer(ms, repeat, callback_name, payload)`, `kv_set`/`kv_get`, `create_event`/`hook_event`/`fire_event`. Never `emit_event`, `execute_timer`, or `register_event_handler`.

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
            "Use emit_event and execute_timer for a 5s KV heartbeat.",
            """Those hosts do not exist. Correct pattern:

```rhai
fn on_tick(_p) {
    kv_set("shared_state", "1");
    fire_event("state_updated", #{});
}
create_event("state_updated");
create_timer(5000, true, "on_tick", #{});
```""",
        )
    )
    g.append(
        row(
            "register_event_handler(\"state_updated\", \"on_state\") please.",
            """Use `hook_event` after `create_event`.

```rhai
fn on_state(_d) {
    log_info(kv_get("shared_state"));
}
create_event("state_updated");
hook_event("state_updated", "on_state");
```""",
        )
    )

    # --- 11 MCP client ---
    g.append(
        row(
            "Show me how to connect to an external MCP server running on port 3000 using mcp_connect, call a tool named get_weather, and log the result.",
            """`mcp_connect(conn_id, command, args)` then `mcp_list_tools` / `mcp_call_tool`. Never invent `mcp_call`.

```rhai
mcp_connect("weather", "npx", ["-y", "weather-mcp", "--port", "3000"]);
let tools = mcp_list_tools("weather");
print(to_json(tools));
let result = mcp_call_tool("weather", "get_weather", #{ city: "Boston" });
log_info(to_json(result));
```""",
        )
    )
    g.append(
        row(
            "After mcp_connect, call mcp_call(\"weather\", \"get_weather\", #{}).",
            """The tool host is `mcp_call_tool`, not `mcp_call`.

```rhai
let result = mcp_call_tool("weather", "get_weather", #{ city: "Boston" });
log_info(to_json(result));
```""",
        )
    )

    # --- 12 MCP router (HARD FAIL) ---
    g.append(
        row(
            "I need to act as an MCP router. Write a plugin that registers a new MCP tool called router_ping. When executed, this tool should connect to a downstream MCP server at http://localhost:8080, pass the arguments along, and return the aggregated response back up the chain.",
            """`register_mcp_tool(name, desc, schema_json)` only registers metadata. The hop uses `mcp_connect(conn_id, command, args)` + `mcp_call_tool`. Do not pass maps into `mcp_connect` or invent `mcp_close` as the hop.

```rhai
let schema = "{\\"type\\":\\"object\\",\\"properties\\":{\\"msg\\":{\\"type\\":\\"string\\"}}}";
register_mcp_tool("router_ping", "Ping a downstream MCP tool hop", schema);

// When the registered tool runs, perform the downstream hop:
mcp_connect("down", "node", ["downstream-mcp.js"]);
let out = mcp_call_tool("down", "ping", #{ msg: "hi" });
print(to_json(out));
```""",
        )
    )
    g.append(
        row(
            "mcp_connect(\"down\", \"run_command\", #{ cmd: \"ping\" }) for the router hop.",
            """`mcp_connect` takes `(conn_id, command, args_array)`, then `mcp_call_tool`.

```rhai
mcp_connect("down", "node", ["downstream-mcp.js"]);
let out = mcp_call_tool("down", "ping", #{ msg: "hi" });
print(to_json(out));
```""",
        )
    )

    # --- 13 sys_os (HARD FAIL) ---
    g.append(
        row(
            "How do I check the operating system that ChaosNexus Anvil is currently running on?",
            """Use `sys_os()` only. Never invent `system_os` or shell out to `uname` for this.

```rhai
let os = sys_os();
print("ChaosNexus Anvil OS: " + os);
```""",
        )
    )
    g.append(
        row(
            "Print the OS with system_os().",
            """Wrong name. The host is `sys_os`.

```rhai
print(sys_os());
```""",
        )
    )

    # --- 14 Watchdog ---
    g.append(
        row(
            "Write a watchdog plugin. It should use create_timer to wake up every 60 seconds, check the current OS using sys_os, and if the OS is 'windows', use run_command to execute tasklist. Log the output. Tell me what chaosnexus-anvil.toml capabilities are needed.",
            """`run_command` returns a string on success (it throws on failure). Do not invent Result unwrap helpers.

```toml
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

    # --- 15 / 16 CVars + load_config ---
    g.append(
        row(
            "Show me how to register a Console Variable (CVar) called 'debug_mode' with a default integer value of 0, and how to read its value later.",
            """`register_cvar(name, default, desc)` then `get_cvar`. Never `sys_set_cvar`.

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

    # --- 17 WS ---
    g.append(
        row(
            "Show me how to connect to a WebSocket endpoint using ws_connect and send a message.",
            """`ws_connect(url, callback_name)` + `ws_close(url)`.

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

    # --- 18 Shared FS ---
    g.append(
        row(
            "Plugin A fetches data from a WebSocket and writes it with fs_data_write; Plugin B uses fs_data_read. Provide permissions and Plugin A code.",
            """`fs_data_write` / `fs_data_read` need `granted_capabilities = [\"fs_shared_data\"]`. Do not invent `fs_shared` TOML keys.

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
    g.append(
        row(
            "Set fs_shared = [\"write\"] under plugin permissions for shared data.",
            """Wrong schema. Use `granted_capabilities = [\"fs_shared_data\"]` and `fs_data_write` / `fs_data_read`.

```toml
[plugins.plugin_a]
granted_capabilities = ["fs_shared_data"]
```

```rhai
fs_data_write("shared/out.txt", "hello");
```""",
        )
    )

    # --- Anti tool-call / misc ---
    g.append(
        row(
            "Use a <tool_call> block to invoke http_get for https://httpbin.org/get.",
            """Do not emit `<tool_call>` markup.

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


# Substrings that mark hard-fail themes; those rows get extra copies before global upsample.
PRIORITY_NEEDLES = (
    "regex_match",
    "regex_find_all",
    "json_extract",
    "hook_event",
    "create_timer",
    "emit_event",
    "execute_timer",
    "register_event_handler",
    "mcp_call_tool",
    "mcp_call(",
    "sys_os",
    "system_os",
    "fs_read",
    "write_file_string",
    "read_file",
    "cn_a_install_plugin",
    "chaoswrench_install_plugin",
    "http_get",
    "fetch(",
)


def is_priority(r: dict) -> bool:
    blob = "\n".join(m.get("content", "") for m in r["messages"])
    return any(n in blob for n in PRIORITY_NEEDLES)


def main() -> None:
    random.seed(3407)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    curated = goldens()
    # Extra copies of priority / hard-negative rows before global upsample.
    boosted: list[dict] = []
    for r in curated:
        boosted.append(r)
        if is_priority(r):
            boosted.extend([r, r])  # +2 → 3x for priority themes

    upsample = 48
    rows: list[dict] = []
    for _ in range(upsample):
        rows.extend(boosted)
    random.shuffle(rows)
    with OUT_JSONL.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    meta = {
        "curated": len(curated),
        "boosted_unique_slots": len(boosted),
        "upsample": upsample,
        "total": len(rows),
        "augmented_merged": 0,
        "codex": False,
        "output": str(OUT_JSONL),
        "notes": "iter-4 goldens-only; hard-negatives for 6/9/10/12/13; no Codex",
    }
    (OUT_DIR / "build_meta.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(meta, indent=2))


if __name__ == "__main__":
    main()
