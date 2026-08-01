# ChaosNexus Anvil Evaluation Results

**Model:** `/home/flyingmongoose/.unsloth/studio/outputs/chaosnexus-tuned-iter7-rocm`

**Subset indices:** `1,4,5,7`

**Decode:** greedy (`do_sample=False`)

## 1. The Simple Test: Web Request & JSON Parsing
### Prompt
```
I need to check if our local server is up and see what it's returning. Write and execute a Rhai script that makes a GET request to http://localhost:1420/ (or a public test API like https://httpbin.org/get), extracts the status code or a specific JSON field from the response, and prints a formatted summary of the result.
```

### Response
Register router_ping then use router_ping_status() and router_ping_body().

```toml
[plugins.check_http.permissions]
http = ["GET"]
net_allowlist = ["localhost", "httpbin.org"]
```

```rhai
let status = router_ping_status("http://localhost:1420");
print(to_json(status));
let body = router_ping_body("http://localhost:1420");
print(body);
```

---

## 4. The Autonomous Test: Unfamiliar API Discovery
### Prompt
```
I need a new ChaosNexus Anvil plugin that connects to our local SQLite database (db.sqlite) to pull the top 10 most recent user logins. I'm not sure if ChaosNexus Anvil has a native SQLite driver or if we need to spin up an external MCP server dynamically using npx. Please figure out the correct approach from the documentation and write the plugin for me.
```

### Response
Register `db_connect` and `db_query` with `register_mcp_tool`.

```toml
[plugins.logins.permissions]
mcp_tools = ["db_connect", "db_query"]
```

Then write `logins` with those tools (never invent `db_connect_status`).

```toml
mcp_allowlist = ["logins"]
```

```rhai
db_connect("logins", "sqlite://db.sqlite");
print(to_json(db_query("logins", "SELECT * FROM user_logins ORDER BY logged_at DESC LIMIT 10")));
```

---

## 5. The Security & Persistence Test: Crypto and KV Store
### Prompt
```
I need to securely store an access token. Write a Rhai script that takes a raw string token, hashes it using SHA256, encodes the resulting hash in Base64, and then stores the encoded string into the native ChaosNexus Anvil KV store under the key 'secure_token'. Finally, retrieve the key from the store and print it to verify it was saved correctly.
```

### Response
Register with `register_tool` then use `call_tool` (never emit <tool_call> languages or non-Rhai languages).

---

## 7. The Sandbox Security Gate Test: Deny-by-Default Validation
### Prompt
```
I need a ChaosNexus Anvil plugin that runs the `curl` command to fetch data from `https://api.github.com/zen`. Since I know ChaosNexus Anvil blocks shell commands and network requests by default, please provide the exact configuration changes needed in `ChaosNexus Anvil.toml` to allow this, alongside the plugin code itself.
```

### Response
Allowing `curl` (or any shell command) directly is not recommended. Instead, use `mcp_connect` + `http_get` (if available) or `mcp_call` a stdlib HTTP tool. Here’s how:

1. **Enable `curl` (not advised).**  
   ```toml
   [plugins.github_zen.permissions]
   shell = ["curl"]
   ```

2. **Preferred: no `curl` permission.**  
   ```toml
   [plugins.github_zen]
   code = """
   fn on_ping(text) {
       if text == "zen" {
           let result = http_get("https://api.github.com/zen");
           print(to_json(result));
       }
   }
   """
   ```

Both fetch GitHub’s Zen; the second never touches the OS shell.

---

