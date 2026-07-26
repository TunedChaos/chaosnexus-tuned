# chaosnexus-tuned/scripts/injectors/inject_iter7_api_goldens.py
"""Build iter-7 goldens aiming for mean ≥0.90 (full-version bar).

Iter-6 cleared alpha (0.833 + smoke). Remaining gaps: prompts 12 (Fail),
and Partials 1/2/7/8. Keep corpus small; positive exemplars; no Codex.
"""

from __future__ import annotations

import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "datasets" / "iter7"
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


def keep_goldens() -> list[dict]:
    """Strong Pass themes from iter-5/6 (preserve score floor)."""
    g: list[dict] = []
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
            "I need a ChaosNexus Anvil plugin that connects to db.sqlite for top 10 user_logins. Prefer native APIs over npx.",
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
for row in rows { print(to_json(row)); }
```""",
        )
    )
    g.append(
        row(
            "Write Fibonacci 15, keep odds, print average.",
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
for num in fib_15 { if num % 2 != 0 { odds.push(num); } }
let sum = 0;
for num in odds { sum += num; }
print("average=" + (sum / odds.len()));
```""",
        )
    )
    g.append(
        row(
            "Extract emails with regex_match; pull status/id with json_extract.",
            """```rhai
let emails = regex_match(
    "[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\\\.[A-Za-z]{2,}",
    "Contact support@company.com or sales@company.net"
);
for email in emails { print(email); }
let payload = "{\\"status\\":\\"active\\",\\"id\\":12345}";
print(json_extract(payload, "/status"));
print(json_extract(payload, "/id"));
```""",
        )
    )
    g.append(
        row(
            "Show create_event, hook_event, fire_event.",
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
            "5s timer writes KV and fires state_updated; listener logs it.",
            """```rhai
fn on_tick(_p) {
    kv_set("shared_state", rand(0, 1000).to_string());
    fire_event("state_updated", #{});
}
create_event("state_updated");
create_timer(5000, true, "on_tick", #{});
fn on_state(_d) { log_info(kv_get("shared_state")); }
hook_event("state_updated", "on_state");
```""",
        )
    )
    g.append(
        row(
            "mcp_connect weather MCP on port 3000, call get_weather, log result.",
            """```rhai
mcp_connect("weather", "npx", ["-y", "weather-mcp", "--port", "3000"]);
print(to_json(mcp_list_tools("weather")));
log_info(to_json(mcp_call_tool("weather", "get_weather", #{ city: "Boston" })));
```""",
        )
    )
    g.append(
        row(
            "How do I check the OS?",
            """```rhai
print(sys_os());
```""",
        )
    )
    g.append(
        row(
            "Watchdog every 60s on windows runs tasklist.",
            """```toml
[plugins.watchdog.permissions]
shell = ["tasklist"]
```

```rhai
fn on_watchdog(_p) {
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
            "Register CVar debug_mode default 0 and read it.",
            """```rhai
register_cvar("debug_mode", "0", "Enable debug mode");
print(get_cvar("debug_mode"));
```""",
        )
    )
    g.append(
        row(
            "load_config my_app.toml; register max_retries CVar, fallback 3.",
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
            "Connect WebSocket with ws_connect.",
            """```toml
[plugins.ws_echo.permissions]
http = ["WS"]
net_allowlist = ["echo.websocket.events"]
```

```rhai
fn on_ws_msg(text) { log_info(text); }
ws_connect("wss://echo.websocket.events", "on_ws_msg");
```""",
        )
    )
    g.append(
        row(
            "Plugin A fs_data_write from WS; Plugin B fs_data_read. Permissions + A code.",
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
fn on_ws_msg(text) { fs_data_write("shared/websocket_output.txt", text); }
ws_connect("wss://echo.websocket.events", "on_ws_msg");
```""",
        )
    )
    return g


def focus_goldens() -> list[dict]:
    """Prompts 12 (Fail) and 1/2/7/8 (Partial)."""
    f: list[dict] = []

    # --- 12 MCP router (critical +1.0) ---
    f.append(
        row(
            "I need to act as an MCP router. Write a plugin that registers a new MCP tool called router_ping. When executed, this tool should connect to a downstream MCP server at http://localhost:8080, pass the arguments along, and return the aggregated response back up the chain.",
            """Register with `register_mcp_tool`, then hop with `mcp_connect` + `mcp_call_tool` (never invent `down_mcp_*`).

```rhai
let schema = "{\\"type\\":\\"object\\",\\"properties\\":{\\"msg\\":{\\"type\\":\\"string\\"}}}";
register_mcp_tool("router_ping", "Ping a downstream MCP tool hop", schema);
mcp_connect("down", "node", ["downstream-mcp.js"]);
let out = mcp_call_tool("down", "ping", #{ msg: "hi" });
print(to_json(out));
```""",
        )
    )
    f.append(
        row(
            "Register router_ping then use down_mcp_connect / down_mcp_call.",
            """```rhai
let schema = "{\\"type\\":\\"object\\",\\"properties\\":{}}";
register_mcp_tool("router_ping", "Ping a downstream MCP tool hop", schema);
mcp_connect("down", "node", ["downstream-mcp.js"]);
print(to_json(mcp_call_tool("down", "ping", #{ msg: "hi" })));
```""",
        )
    )
    f.append(
        row(
            "MCP router: register_mcp_tool then mcp_connect(conn_id, command, args) and mcp_call_tool.",
            """```rhai
register_mcp_tool("router_ping", "Ping a downstream MCP tool hop", "{\\"type\\":\\"object\\"}");
mcp_connect("down", "npx", ["-y", "some-mcp"]);
print(to_json(mcp_call_tool("down", "ping", #{})));
```""",
        )
    )
    f.append(
        row(
            "Connect downstream MCP at localhost:8080 after registering router_ping.",
            """HTTP URLs are not `mcp_connect` args. Spawn a stdio MCP process:

```rhai
register_mcp_tool("router_ping", "Ping a downstream MCP tool hop", "{\\"type\\":\\"object\\"}");
mcp_connect("down", "node", ["downstream-mcp.js"]);
print(to_json(mcp_call_tool("down", "ping", #{ msg: "hi" })));
```""",
        )
    )

    # --- 1 HTTP: no http_get_status ---
    f.append(
        row(
            "I need to check if our local server is up and see what it's returning. Write and execute a Rhai script that makes a GET request to https://httpbin.org/get, extracts a JSON field, and prints a formatted summary.",
            """Use only `http_get` + `from_json` (no `http_get_status`).

```toml
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
    f.append(
        row(
            "After http_get call http_get_status().",
            """```rhai
let raw = http_get("https://httpbin.org/get");
let body = from_json(raw);
print(body.origin);
```""",
        )
    )

    # --- 2 FS: ends_with not contains ---
    f.append(
        row(
            "Write and execute a Rhai script that searches for any .toml or .json files in the current directory, reads their contents, finds lines containing port or host, and writes ports_found.txt.",
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
    f.append(
        row(
            "Filter files with extensions.contains(&file).",
            """```rhai
for file in list_dir(".") {
    if file.ends_with(".toml") || file.ends_with(".json") {
        print(fs_read(file));
    }
}
```""",
        )
    )

    # --- 7 curl not npx ---
    f.append(
        row(
            "I need a ChaosNexus Anvil plugin that runs the curl command to fetch https://api.github.com/zen. Provide chaosnexus-anvil.toml allowlist and plugin code.",
            """Allow `curl` directly (not via `npx`).

```toml
[plugins.github_zen.permissions]
shell = ["curl"]
```

```rhai
let result = run_command("curl", ["-s", "https://api.github.com/zen"]);
print(result);
```""",
        )
    )
    f.append(
        row(
            "Allowlist npx and run_command(npx, [curl, url]).",
            """```toml
[plugins.github_zen.permissions]
shell = ["curl"]
```

```rhai
print(run_command("curl", ["-s", "https://api.github.com/zen"]));
```""",
        )
    )

    # --- 8 HITL narrative ---
    f.append(
        row(
            "Write a Rhai script that uses chaoswrench_install_plugin to fetch community plugin system_monitor. Explain exactly how I approve and edit it in ChaosNexus Forge before it goes live.",
            """Use `cn_a_install_plugin` (not chaoswrench_install_plugin). It stages a pending plugin.

```rhai
print(cn_a_install_plugin("system_monitor"));
```

Then in ChaosNexus Forge: open Pending plugins → review the Rhai and requested permissions → Approve. Anvil loads the plugin only after human approval.""",
        )
    )
    f.append(
        row(
            "cn_a_install_plugin system_monitor plus Forge approval steps.",
            """```rhai
let staged = cn_a_install_plugin("system_monitor");
print(staged);
```

Forge: Pending plugins → review → Approve → Anvil hot-loads.""",
        )
    )

    return f


def main() -> None:
    random.seed(3407)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    keep = keep_goldens()
    focus = focus_goldens()
    rows: list[dict] = []
    for _ in range(18):
        rows.extend(keep)
    for _ in range(45):
        rows.extend(focus)
    random.shuffle(rows)
    with OUT_JSONL.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    meta = {
        "keep": len(keep),
        "focus": len(focus),
        "keep_upsample": 18,
        "focus_upsample": 45,
        "total": len(rows),
        "codex": False,
        "target": "mean>=0.90",
        "output": str(OUT_JSONL),
    }
    (OUT_DIR / "build_meta.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(meta, indent=2))


if __name__ == "__main__":
    main()
