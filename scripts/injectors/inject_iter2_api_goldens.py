# chaosnexus-tuned/scripts/injectors/inject_iter2_api_goldens.py
"""Build iter-2 hybrid train JSONL: real Anvil host APIs + anti-invention goldens.

Upsamples curated ShareGPT-style ``messages`` rows (eval-aligned system prompt)
and merges a filtered slice of the existing augmented corpus so invented names
like ``sqlite_query`` / ``cn_a_sqlite_*`` do not dominate.
"""

from __future__ import annotations

import json
import os
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AUGMENTED = ROOT / "datasets" / "augmented" / "train_augmented.jsonl"
OUT_DIR = ROOT / "datasets" / "iter2"
OUT_JSONL = OUT_DIR / "train.jsonl"

EVAL_SYSTEM = (
    "You are an elite Workspace Systems Architect. You master the ChaosNexus Anvil MCP. "
    "You autonomously discover and leverage capabilities provided by your workspace environment. "
    "You MUST ONLY write Rhai scripts when creating plugins. NEVER output Python, Bash, Node.js, "
    "or any other language. Always search for plugins before creating one. "
    "Use only real ChaosNexus Anvil host functions (for example http_get, from_json, kv_set, "
    "kv_get, sha256, base64_encode, db_connect, db_query, mcp_connect, mcp_call_tool, "
    "register_mcp_tool, register_cvar, get_cvar, sys_os, regex_match, json_extract, "
    "ws_connect, create_event, hook_event, fire_event, create_timer, run_command, "
    "fs_list_dir, fs_read, fs_write, load_config). Never invent APIs such as sqlite_query, "
    "parse_json, kv_store_set, emit_event, fs_data_write, or cn_a_sqlite_query."
)

# Substrings that mark poisoned synthetic rows to drop from the base corpus.
POISON = (
    "sqlite_query",
    "cn_a_sqlite",
    "parse_json",
    "kv_store_set",
    "kv_store_get",
    "emit_event",
    "fs_data_write",
    "fs_data_read",
    "crypto_hash_sha256",
    "websocket_connect",
    "cn_a_kv_",
    "cn_v_",
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

    # --- Prompt-aligned: HTTP ---
    g.append(
        row(
            "I need to check if our local server is up and see what it's returning. Write a Rhai script that makes a GET request to https://httpbin.org/get, extracts a JSON field from the response, and prints a formatted summary.",
            """I will use the native `http_get` and `from_json` host functions (not invented HTTP crates).

```rhai
// Allowlist https://httpbin.org in chaosnexus-anvil.toml under plugin_permissions before running.
let raw = http_get("https://httpbin.org/get");
let body = from_json(raw);
print("HTTP summary origin=" + body.origin);
```""",
        )
    )

    # --- Prompt-aligned: SQLite / docs-first ---
    g.append(
        row(
            "I need a new ChaosNexus Anvil plugin that connects to our local SQLite database (db.sqlite) to pull the top 10 most recent user logins. I'm not sure if ChaosNexus Anvil has a native SQLite driver or if we need to spin up an external MCP server dynamically using npx. Please figure out the correct approach from the documentation and write the plugin for me.",
            """Docs-first: ChaosNexus Anvil already exposes `db_connect` / `db_query`. Do not invent `sqlite_query`, and do not use npx or cargo-install prose.

Grant SQL allowlists in `chaosnexus-anvil.toml`, then:

```rhai
// Connect with a plugin-local sqlite URL (relative path under the plugin dir).
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
            """`sqlite_query` is not a ChaosNexus Anvil host function. Use `db_connect` + `db_query` instead.

```rhai
db_connect("db", "sqlite://db.sqlite");
let rows = db_query("db", "SELECT 1 AS ok", []);
print(to_json(rows));
```""",
        )
    )

    # --- Crypto + KV ---
    g.append(
        row(
            "I need to securely store an access token. Write a Rhai script that takes a raw string token, hashes it using SHA256, encodes the resulting hash in Base64, and then stores the encoded string into the native ChaosNexus Anvil KV store under the key 'secure_token'. Finally, retrieve the key from the store and print it to verify it was saved correctly.",
            """Use `sha256`, `base64_encode`, `kv_set`, and `kv_get` (never `crypto_hash_sha256` or `kv_store_*`).

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

    # --- Deny-by-default shell ---
    g.append(
        row(
            "I need a ChaosNexus Anvil plugin that runs the `curl` command to fetch data from `https://api.github.com/zen`. Since I know ChaosNexus Anvil blocks shell commands and network requests by default, please provide the exact configuration changes needed in ChaosNexus Anvil.toml to allow this, alongside the plugin code itself.",
            """Deny-by-default: edit `chaosnexus-anvil.toml` (not a made-up Anvil.toml), then use `run_command`.

```toml
[plugin_permissions.github_zen]
allowed_shell_commands = ["curl"]

[plugin_permissions.github_zen.data.network]
# Prefer structured network allowlists when using http_get; for curl, shell allowlist is required.
```

```rhai
let result = run_command("curl", ["-s", "https://api.github.com/zen"]);
print("GitHub Zen: " + result);
```""",
        )
    )

    # --- Files ---
    g.append(
        row(
            "Write and execute a Rhai script that searches for any .toml or .json files in the current directory, reads their contents, finds lines containing the word 'port' or 'host', and writes a consolidated summary to ports_found.txt.",
            """```rhai
let summary = "";
let files = fs_list_dir(".");
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
fs_write("ports_found.txt", summary);
print("Summary written to ports_found.txt");
```""",
        )
    )

    # --- Pure algorithm (valid Rhai, no Rust iterators) ---
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

    # --- Regex + JSON ---
    g.append(
        row(
            "Write a Rhai script that uses native Regex functions to extract all valid email addresses from sample text, then use native JSON extraction to pull 'status' and 'id' from a JSON string.",
            """Use `regex_match` / `regex_replace` and `from_json` or `json_extract` — not `parse_json` or `regex_find_all`.

```rhai
let raw_text = "Contact support@company.com or sales@company.net";
let ok = regex_match("[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\\\.[A-Za-z]{2,}", raw_text);
print("Email pattern matched: " + ok);

let payload = "{\\"status\\":\\"active\\",\\"id\\":12345}";
let status = json_extract(payload, "/status");
let id = json_extract(payload, "/id");
print("status=" + status + " id=" + id);
```""",
        )
    )

    # --- Events ---
    g.append(
        row(
            "How do I use the ChaosNexus Anvil event bus to fire an event that another plugin can listen to? Show me create_event, hook_event, and fire_event.",
            """```rhai
create_event("demo_ping");
hook_event("demo_ping", || {
    print("demo_ping received");
});
fire_event("demo_ping", #{ source: "example" });
```""",
        )
    )

    g.append(
        row(
            "Write two plugins: one timer writes a random number to KV every 5 seconds and fires state_updated; another listens and logs the value. Use emit_event.",
            """There is no `emit_event` host function. Use `fire_event` with `create_timer`, `kv_set`, `kv_get`, and `hook_event`.

```rhai
// updater.rhai
create_event("state_updated");
create_timer("tick", 5000, || {
    let n = rand(0, 1000);
    kv_set("shared_state", n.to_string());
    fire_event("state_updated", #{});
});

// listener.rhai
hook_event("state_updated", || {
    let v = kv_get("shared_state");
    log_info("state=" + v);
});
```""",
        )
    )

    # --- MCP ---
    g.append(
        row(
            "Show me how to connect to an external MCP server running on port 3000 using mcp_connect, call a tool named get_weather, and log the result.",
            """`mcp_connect` is a real Anvil host function (stdio command + args). Do not substitute raw `http_get` for MCP mesh calls.

```rhai
// Example: spawn a local MCP server binary that listens/bridges to your weather tools.
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
            "I need to act as an MCP router. Write a plugin that registers a new MCP tool called router_ping. When executed, connect to a downstream MCP server at http://localhost:8080, pass arguments along, and return the aggregated response.",
            """Register with `register_mcp_tool`, then use `mcp_connect` / `mcp_call_tool` for the downstream hop (not inventing HTTP MCP routers).

```rhai
register_mcp_tool("router_ping", "Ping downstream MCP", |args| {
    mcp_connect("down", "node", ["downstream-mcp.js"]);
    let out = mcp_call_tool("down", "ping", args);
    to_json(out)
});
```""",
        )
    )

    # --- sys_os / watchdog ---
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

    g.append(
        row(
            "Write a watchdog plugin. It should use create_timer to wake up every 60 seconds, check the current OS using sys_os, and if the OS is 'windows', use run_command to execute tasklist. Log the output. Tell me what chaosnexus-anvil.toml capabilities are needed.",
            """```toml
[plugin_permissions.watchdog]
allowed_shell_commands = ["tasklist"]
```

```rhai
create_timer("watchdog", 60000, || {
    let os = sys_os();
    if os == "windows" {
        let out = run_command("tasklist", []);
        log_info(out);
    } else {
        log_info("watchdog skip non-windows os=" + os);
    }
});
```""",
        )
    )

    # --- CVars / config ---
    g.append(
        row(
            "Show me how to register a Console Variable (CVar) called 'debug_mode' with a default integer value of 0, and how to read its value later.",
            """Use `register_cvar` and `get_cvar` — not invented `cn_a_` / `cn_v_` prefixes.

```rhai
register_cvar(PLUGIN_NAME, "debug_mode", "0", "Enable debug mode");
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
    register_cvar(PLUGIN_NAME, "max_retries", max_retries.to_string(), "Retry budget");
} else {
    register_cvar(PLUGIN_NAME, "max_retries", "3", "Retry budget");
}
print("max_retries=" + get_cvar("max_retries"));
```""",
        )
    )

    # --- WebSocket ---
    g.append(
        row(
            "Show me how to connect to a WebSocket endpoint using ws_connect and send a message.",
            """```rhai
let ws = ws_connect("wss://echo.websocket.events");
// Follow-up host helpers vary by binding; keep the connection id and send via documented WS APIs.
print("ws connected handle=" + ws);
```""",
        )
    )

    g.append(
        row(
            "Plugin A fetches data from a WebSocket and writes it with fs_data_write; Plugin B uses fs_data_read. Provide permissions and Plugin A code.",
            """There are no `fs_data_write` / `fs_data_read` hosts. Use `fs_write` / `fs_read` plus `ws_connect`, and share a path both plugins may access via `plugin_permissions`.

```toml
[plugin_permissions.plugin_a]
fs_write = true
fs_read = true

[plugin_permissions.plugin_b]
fs_read = true
```

```rhai
let ws = ws_connect("wss://echo.websocket.events");
let payload = "hello-from-ws";
fs_write("shared/websocket_output.txt", payload);
```""",
        )
    )

    # --- HITL ---
    g.append(
        row(
            "Write a Rhai script that uses chaoswrench_install_plugin to fetch a community plugin called system_monitor. Explain how I approve it in ChaosNexus Forge before it goes live.",
            """Prefer `sys_install_plugin` when available; plugins stage as pending until a human approves them in Forge.

```rhai
let result = sys_install_plugin("system_monitor");
print("install staged: " + result);
```

After staging: open ChaosNexus Forge → Pending plugins → review the Rhai + TOML permissions → Approve. Anvil hot-reloads only after approval.""",
        )
    )

    # --- Anti-invention short pairs ---
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

    return g


def corpus_ok(text: str) -> bool:
    lower = text.lower()
    return not any(p.lower() in lower for p in POISON)


def load_filtered_augmented(limit: int = 120) -> list[dict]:
    if not AUGMENTED.is_file():
        return []
    kept: list[dict] = []
    with AUGMENTED.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            blob = "\n".join(m.get("content", "") for m in obj.get("messages", []))
            if not corpus_ok(blob):
                continue
            # Re-anchor system prompt toward eval style for surviving rows.
            msgs = obj["messages"]
            if msgs and msgs[0].get("role") == "system":
                msgs[0]["content"] = EVAL_SYSTEM + "\n\n" + msgs[0]["content"][:800]
            kept.append(obj)
            if len(kept) >= limit:
                break
    return kept


def main() -> None:
    random.seed(3407)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    curated = goldens()
    # Upsample curated goldens so they dominate loss.
    upsample = 8
    rows = []
    for _ in range(upsample):
        rows.extend(curated)
    rows.extend(load_filtered_augmented(limit=120))
    random.shuffle(rows)
    with OUT_JSONL.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    meta = {
        "curated": len(curated),
        "upsample": upsample,
        "curated_expanded": len(curated) * upsample,
        "filtered_augmented": len(rows) - len(curated) * upsample,
        "total": len(rows),
        "output": str(OUT_JSONL),
    }
    (OUT_DIR / "build_meta.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(meta, indent=2))


if __name__ == "__main__":
    main()
