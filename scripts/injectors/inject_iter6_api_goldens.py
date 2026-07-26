# chaosnexus-tuned/scripts/injectors/inject_iter6_api_goldens.py
"""Build iter-6 goldens: iter-5 positives + focused upsample for fails 4/6/8/17.

Keep corpus small (~800-1000). Do not reintroduce long ban-list assistants.
Codex still deferred until smoke clears and mean ≥0.70.
"""

from __future__ import annotations

import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "datasets" / "iter6"
OUT_JSONL = OUT_DIR / "train.jsonl"

EVAL_SYSTEM = (
    "You are a ChaosNexus Anvil Workspace Systems Architect. "
    "Answer with brief Rhai guidance and a complete ```rhai``` script using real Anvil host APIs. "
    "Never emit <tool_call> markup or non-Rhai languages."
)


def row(user: str, assistant: str) -> dict:
    return {
        "messages": [
            {"role": "system", "content": EVAL_SYSTEM},
            {"role": "user", "content": user},
            {"role": "assistant", "content": assistant},
        ]
    }


def base_goldens() -> list[dict]:
    """All iter-5-style positives covering the 18-prompt surface."""
    g: list[dict] = []

    g.append(
        row(
            "I need to check if our local server is up. Write a Rhai script that GETs https://httpbin.org/get, parses JSON, and prints a summary field.",
            """```toml
[plugins.check_http.permissions]
http = ["GET"]
net_allowlist = ["httpbin.org"]
```

```rhai
let raw = http_get("https://httpbin.org/get");
let body = from_json(raw);
print("origin=" + body.origin);
```""",
        )
    )
    g.append(
        row(
            "Write a Rhai script that lists .toml/.json files, finds lines with port or host, and writes ports_found.txt.",
            """```rhai
let summary = "";
let files = list_dir(".");
for file in files {
    if file.ends_with(".toml") || file.ends_with(".json") {
        let content = fs_read(file);
        for line in content.split("\\n") {
            if line.contains("port") || line.contains("host") {
                summary += line + "\\n";
            }
        }
    }
}
write_file_string("ports_found.txt", summary);
print("wrote ports_found.txt");
```""",
        )
    )
    g.append(
        row(
            "Write a Rhai script that computes the first 15 Fibonacci numbers, keeps odds, and prints their average.",
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
    if num % 2 != 0 { odds.push(num); }
}
let sum = 0;
for num in odds { sum += num; }
print("average=" + (sum / odds.len()));
```""",
        )
    )
    g.append(
        row(
            "Hash a token with SHA256, Base64-encode it, store under secure_token in KV, then read it back.",
            """```rhai
let digest = sha256("your_raw_access_token_here");
let encoded = base64_encode(digest);
kv_set("secure_token", encoded);
print(kv_get("secure_token"));
```""",
        )
    )
    g.append(
        row(
            "Run curl to fetch https://api.github.com/zen. Provide chaosnexus-anvil.toml allowlist and Rhai.",
            """```toml
[plugins.github_zen.permissions]
shell = ["curl"]
```

```rhai
let result = run_command("curl", ["-s", "https://api.github.com/zen"]);
print(result);
```""",
        )
    )
    g.append(
        row(
            "Show create_event, hook_event, and fire_event.",
            """```rhai
fn on_demo_ping(data) { print(to_json(data)); }
create_event("demo_ping");
hook_event("demo_ping", "on_demo_ping");
fire_event("demo_ping", #{ source: "example" });
```""",
        )
    )
    g.append(
        row(
            "Two plugins: a 5s timer writes a random number to KV and fires state_updated; a listener logs the value.",
            """```rhai
fn on_tick(_payload) {
    kv_set("shared_state", rand(0, 1000).to_string());
    fire_event("state_updated", #{});
}
create_event("state_updated");
create_timer(5000, true, "on_tick", #{});

fn on_state(_data) { log_info(kv_get("shared_state")); }
hook_event("state_updated", "on_state");
```""",
        )
    )
    g.append(
        row(
            "Connect to an MCP server on port 3000 with mcp_connect, call get_weather, log the result.",
            """```rhai
mcp_connect("weather", "npx", ["-y", "weather-mcp", "--port", "3000"]);
print(to_json(mcp_list_tools("weather")));
log_info(to_json(mcp_call_tool("weather", "get_weather", #{ city: "Boston" })));
```""",
        )
    )
    g.append(
        row(
            "Register MCP tool router_ping and hop to a downstream MCP server.",
            """```rhai
let schema = "{\\"type\\":\\"object\\",\\"properties\\":{\\"msg\\":{\\"type\\":\\"string\\"}}}";
register_mcp_tool("router_ping", "Ping a downstream MCP tool hop", schema);
mcp_connect("down", "node", ["downstream-mcp.js"]);
print(to_json(mcp_call_tool("down", "ping", #{ msg: "hi" })));
```""",
        )
    )
    g.append(
        row(
            "How do I check the OS ChaosNexus Anvil is running on?",
            """```rhai
print(sys_os());
```""",
        )
    )
    g.append(
        row(
            "Watchdog every 60s: sys_os, and on windows run tasklist. Include TOML.",
            """```toml
[plugins.watchdog.permissions]
shell = ["tasklist"]
```

```rhai
fn on_watchdog(_payload) {
    if sys_os() == "windows" {
        log_info(run_command("tasklist", []));
    }
}
create_timer(60000, true, "on_watchdog", #{});
```""",
        )
    )
    g.append(
        row(
            "Register CVar debug_mode default 0 and read it later.",
            """```rhai
register_cvar("debug_mode", "0", "Enable debug mode");
print(get_cvar("debug_mode"));
```""",
        )
    )
    g.append(
        row(
            "load_config my_app.toml; register max_retries as CVar, fallback 3.",
            """```rhai
let config = load_config("my_app.toml");
if config != () {
    register_cvar("max_retries", config.max_retries.to_string(), "Retry budget");
} else {
    register_cvar("max_retries", "3", "Retry budget");
}
print(get_cvar("max_retries"));
```""",
        )
    )
    g.append(
        row(
            "Plugin A writes WebSocket data with fs_data_write; Plugin B reads with fs_data_read. Permissions + Plugin A.",
            """```toml
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
    return g


def focus_goldens() -> list[dict]:
    """Extra rows for iter-5 fails: prompts 4, 6, 8, 17."""
    f: list[dict] = []

    # --- Prompt 4: db_connect / db_query (smoke critical) ---
    f.append(
        row(
            "I need a new ChaosNexus Anvil plugin that connects to our local SQLite database (db.sqlite) to pull the top 10 most recent user logins. I'm not sure if ChaosNexus Anvil has a native SQLite driver or if we need to spin up an external MCP server dynamically using npx. Please figure out the correct approach from the documentation and write the plugin for me.",
            """Use native `db_connect(id, url)` and `db_query(id, sql, params)`.

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
    f.append(
        row(
            "Connect to db.sqlite and SELECT the top 10 user_logins with native Anvil hosts.",
            """```rhai
db_connect("logins", "sqlite://db.sqlite");
let rows = db_query("logins", "SELECT * FROM user_logins ORDER BY login_time DESC LIMIT 10", []);
for row in rows { print(to_json(row)); }
```""",
        )
    )
    f.append(
        row(
            "Use sqlite_connect and sqlite_query for db.sqlite.",
            """```rhai
db_connect("db", "sqlite://db.sqlite");
print(to_json(db_query("db", "SELECT 1 AS ok", [])));
```""",
        )
    )
    f.append(
        row(
            "let db = sqlite_connect(\"sqlite://db.sqlite\"); db.query(\"SELECT 1\");",
            """```rhai
db_connect("db", "sqlite://db.sqlite");
print(to_json(db_query("db", "SELECT 1", [])));
```""",
        )
    )
    f.append(
        row(
            "Call cn_a_sqlite_query on db.sqlite.",
            """```rhai
db_connect("db", "sqlite://db.sqlite");
print(to_json(db_query("db", "SELECT * FROM user_logins LIMIT 10", [])));
```""",
        )
    )

    # --- Prompt 6: regex_match + json_extract ---
    f.append(
        row(
            "I have a raw text string containing mixed data. Write a Rhai script that uses native Regex functions to extract all valid email addresses from the text. Then, take a sample JSON string and use native JSON extraction to pull out the 'status' and 'id' fields.",
            """```rhai
let emails = regex_match(
    "[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\\\.[A-Za-z]{2,}",
    "Contact support@company.com or sales@company.net"
);
for email in emails {
    print(email);
}
let payload = "{\\"status\\":\\"active\\",\\"id\\":12345}";
print(json_extract(payload, "/status"));
print(json_extract(payload, "/id"));
```""",
        )
    )
    f.append(
        row(
            "Extract emails with regex_matches / regex() constructors.",
            """```rhai
let emails = regex_match("[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\\\.[A-Za-z]{2,}", "a@b.com c@d.org");
for e in emails { print(e); }
```""",
        )
    )
    f.append(
        row(
            "Pull JSON fields with from_json only; skip json_extract.",
            """```rhai
print(json_extract("{\\"status\\":\\"ok\\",\\"id\\":1}", "/status"));
print(json_extract("{\\"status\\":\\"ok\\",\\"id\\":1}", "/id"));
```""",
        )
    )

    # --- Prompt 8: cn_a_install_plugin ---
    f.append(
        row(
            "Write a Rhai script that uses chaoswrench_install_plugin to fetch a community plugin called system_monitor. Explain Forge approval.",
            """Use `cn_a_install_plugin`. Then Approve under Forge Pending plugins.

```rhai
print(cn_a_install_plugin("system_monitor"));
```""",
        )
    )
    f.append(
        row(
            "chaoswrench_install_plugin(\"system_monitor\", desc, schema)",
            """```rhai
print(cn_a_install_plugin("system_monitor"));
```""",
        )
    )
    f.append(
        row(
            "Install community plugin system_monitor with the real Anvil host.",
            """```rhai
let staged = cn_a_install_plugin("system_monitor");
print(staged);
```""",
        )
    )

    # --- Prompt 17: ws_connect(url, callback) ---
    f.append(
        row(
            "Show me how to connect to a WebSocket endpoint using ws_connect and send a message.",
            """```toml
[plugins.ws_echo.permissions]
http = ["WS"]
net_allowlist = ["echo.websocket.events"]
```

```rhai
fn on_ws_msg(text) {
    log_info(text);
}
ws_connect("wss://echo.websocket.events", "on_ws_msg");
```""",
        )
    )
    f.append(
        row(
            "ws_connect returns a Result; then ws_send the handle.",
            """```rhai
fn on_ws_msg(text) { log_info(text); }
ws_connect("wss://echo.websocket.events", "on_ws_msg");
```""",
        )
    )
    f.append(
        row(
            "Connect websocket with one-arg ws_connect(url) only.",
            """```rhai
fn on_msg(t) { print(t); }
ws_connect("wss://echo.websocket.events", "on_msg");
```""",
        )
    )

    return f


def main() -> None:
    random.seed(3407)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    base = base_goldens()
    focus = focus_goldens()

    # Mild upsample of full surface + heavier copies of focus fails.
    rows: list[dict] = []
    for _ in range(20):
        rows.extend(base)
    for _ in range(40):
        rows.extend(focus)
    random.shuffle(rows)

    with OUT_JSONL.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    meta = {
        "base": len(base),
        "focus": len(focus),
        "base_upsample": 20,
        "focus_upsample": 40,
        "total": len(rows),
        "codex": False,
        "output": str(OUT_JSONL),
        "notes": "iter-6: focus prompts 4/6/8/17; keep small corpus",
    }
    (OUT_DIR / "build_meta.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(meta, indent=2))


if __name__ == "__main__":
    main()
