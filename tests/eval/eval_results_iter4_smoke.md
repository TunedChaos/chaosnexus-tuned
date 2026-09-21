# ChaosNexus Anvil Evaluation Results

**Model:** `/home/flyingmongoose/.unsloth/studio/outputs/chaosnexus-tuned-iter4-rocm`

**Subset indices:** `1,4,5,7`

**Decode:** greedy (`do_sample=False`)

## 1. The Simple Test: Web Request & JSON Parsing
### Prompt
```
I need to check if our local server is up and see what it's returning. Write and execute a Rhai script that makes a GET request to http://localhost:1420/ (or a public test API like https://httpbin.org/get), extracts the status code or a specific JSON field from the response, and prints a formatted summary of the result.
```

### Response
Plugin call: `http_get("https://httpbin.org/get")`. 

Rhai script:

```rhai
let raw = http_get("https://httpbin.org/get");
let json = from_json(raw);
print("HTTP summary origin=" + json.origin);
```

---

## 4. The Autonomous Test: Unfamiliar API Discovery
### Prompt
```
I need a new ChaosNexus Anvil plugin that connects to our local SQLite database (db.sqlite) to pull the top 10 most recent user logins. I'm not sure if ChaosNexus Anvil has a native SQLite driver or if we need to spin up an external MCP server dynamically using npx. Please figure out the correct approach from the documentation and write the plugin for me.
```

### Response
Docs-first: native `sqlite_query` after `sqlite_connect(db_name)`. No `npx` MCP server for SQLite.

```toml
[plugins.logins.permissions]
sql = ["SELECT"]
sql_urls = ["sqlite://"]
```

```rhai
sqlite_connect("db.sqlite");
let rows = sqlite_query("SELECT * FROM user_logins ORDER BY login_time DESC LIMIT 10", []);
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
Use `sha256`, `base64_encode`, `kv_set`, `kv_get`. Never `print` raw tokens.

```rhai
let raw_token = "your_raw_access_token_here";
let digest = sha256(raw_token);
let encoded = base64_encode(digest);
kv_set("secure_token", encoded);
let retrieved = kv_get("secure_token");
print("Secure Token Stored and Retrieved: " + retrieved);
```

---

## 7. The Sandbox Security Gate Test: Deny-by-Default Validation
### Prompt
```
I need a ChaosNexus Anvil plugin that runs the `curl` command to fetch data from `https://api.github.com/zen`. Since I know ChaosNexus Anvil blocks shell commands and network requests by default, please provide the exact configuration changes needed in `ChaosNexus Anvil.toml` to allow this, alongside the plugin code itself.
```

### Response
Config file is `chaosnexus-anvil.toml`. Shell allowlist: `[plugins.<name>.permissions]` → `shell = [...]`.

```toml
[plugins.github_zen.permissions]
shell = ["curl"]
```

```rhai
let result = curl("https://api.github.com/zen");
print("GitHub Zen: " + result);
```

---

