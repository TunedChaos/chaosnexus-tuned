# chaosnexus-tuned/scripts/injectors/inject_iter5_api_goldens.py
"""Build iter-5 goldens-only train JSONL: small, positive-exemplar dense.

Iter-4 collapsed from oversized anti-invention upsampling. This pass keeps
~25 short gold scripts, mild upsample (~500-800 rows), and only a few brief
corrections - no long ban-lists in assistant turns. Codex still deferred.
"""

from __future__ import annotations

import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "datasets" / "iter5"
OUT_JSONL = OUT_DIR / "train.jsonl"

# Keep the system prompt short so training does not memorize ban-lists.
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


def goldens() -> list[dict]:
    g: list[dict] = []

    # 1 HTTP
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

    # 2 FS
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

    # 3 Fibonacci (restore Pass)
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
    if num % 2 != 0 {
        odds.push(num);
    }
}
let sum = 0;
for num in odds {
    sum += num;
}
print("average=" + (sum / odds.len()));
```""",
        )
    )

    # 4 SQLite (critical smoke)
    g.append(
        row(
            "I need a ChaosNexus Anvil plugin that connects to db.sqlite and pulls the top 10 recent user logins. Prefer native Anvil APIs over npx MCP.",
            """Use `db_connect` and `db_query`.

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
            "Query sqlite with sqlite_query('db.sqlite', 'SELECT 1').",
            """Use `db_connect` + `db_query` instead.

```rhai
db_connect("db", "sqlite://db.sqlite");
print(to_json(db_query("db", "SELECT 1 AS ok", [])));
```""",
        )
    )

    # 5 Crypto KV
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

    # 6 Regex + JSON
    g.append(
        row(
            "Extract emails with native regex, then pull status and id from a JSON string.",
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

    # 7 curl allowlist
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

    # 8 HITL
    g.append(
        row(
            "Use chaoswrench_install_plugin to fetch system_monitor, then explain Forge approval.",
            """Use `cn_a_install_plugin`, then Approve in Forge Pending plugins.

```rhai
print(cn_a_install_plugin("system_monitor"));
```""",
        )
    )

    # 9 Events
    g.append(
        row(
            "Show create_event, hook_event, and fire_event.",
            """```rhai
fn on_demo_ping(data) {
    print(to_json(data));
}
create_event("demo_ping");
hook_event("demo_ping", "on_demo_ping");
fire_event("demo_ping", #{ source: "example" });
```""",
        )
    )

    # 10 Timer + KV + events
    g.append(
        row(
            "Two plugins: a 5s timer writes a random number to KV and fires state_updated; a listener logs the value.",
            """```rhai
// updater.rhai
fn on_tick(_payload) {
    kv_set("shared_state", rand(0, 1000).to_string());
    fire_event("state_updated", #{});
}
create_event("state_updated");
create_timer(5000, true, "on_tick", #{});

// listener.rhai
fn on_state(_data) {
    log_info(kv_get("shared_state"));
}
hook_event("state_updated", "on_state");
```""",
        )
    )

    # 11 MCP client
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

    # 12 MCP router
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

    # 13 sys_os
    g.append(
        row(
            "How do I check the OS ChaosNexus Anvil is running on?",
            """```rhai
print(sys_os());
```""",
        )
    )

    # 14 Watchdog
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

    # 15 CVars
    g.append(
        row(
            "Register CVar debug_mode default 0 and read it later.",
            """```rhai
register_cvar("debug_mode", "0", "Enable debug mode");
print(get_cvar("debug_mode"));
```""",
        )
    )

    # 16 load_config + CVar
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

    # 17 WS
    g.append(
        row(
            "Connect to a WebSocket with ws_connect.",
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

    # 18 fs_data shared
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

    # Brief corrections only (few)
    g.append(
        row(
            "Use to_base64 and kv_store_set.",
            """```rhai
kv_set("k", base64_encode(sha256("x")));
print(kv_get("k"));
```""",
        )
    )
    g.append(
        row(
            "Call system_os() please.",
            """```rhai
print(sys_os());
```""",
        )
    )
    g.append(
        row(
            "After mcp_connect use mcp_call not mcp_call_tool.",
            """```rhai
let out = mcp_call_tool("weather", "get_weather", #{ city: "Boston" });
print(to_json(out));
```""",
        )
    )
    g.append(
        row(
            "Use emit_event and execute_timer.",
            """```rhai
fn tick(_p) {
    fire_event("heartbeat", #{});
}
create_event("heartbeat");
create_timer(1000, true, "tick", #{});
```""",
        )
    )
    g.append(
        row(
            "Use read_file / write_file for ports_found.txt.",
            """```rhai
write_file_string("ports_found.txt", fs_read("config.toml"));
```""",
        )
    )
    g.append(
        row(
            "Register with con_var_set and con_var_get.",
            """```rhai
register_cvar("debug_mode", "0", "Enable debug mode");
print(get_cvar("debug_mode"));
```""",
        )
    )

    return g


def main() -> None:
    random.seed(3407)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    curated = goldens()
    # Mild upsample: ~24 * 28 ≈ 672 rows (inside 500-800 target band).
    upsample = 28
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
        "codex": False,
        "output": str(OUT_JSONL),
        "notes": "iter-5 small positive goldens; avoid ban-list mode collapse",
    }
    (OUT_DIR / "build_meta.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(meta, indent=2))


if __name__ == "__main__":
    main()
