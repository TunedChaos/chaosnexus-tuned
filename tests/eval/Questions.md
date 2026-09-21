# 1. The Simple Test: Web Request & JSON Parsing
This tests basic syntax, string manipulation, and the HTTP/fetch API if exposed to Rhai.

## Prompt:
```
I need to check if our local server is up and see what it's returning. Write and execute a Rhai script that makes a GET request to http://localhost:1420/ (or a public test API like https://httpbin.org/get), extracts the status code or a specific JSON field from the response, and prints a formatted summary of the result.
```

# 2. The Intermediate Test: Multi-Step File Processing & Filtering
This tests the model's ability to handle loops, conditional logic, and custom native functions for file I/O.

## Prompt:
```
We have several configuration and log files in our workspace. Write and execute a Rhai script that searches for any .toml or .json files in the current directory, reads their contents, finds lines containing the word 'port' or 'host', and writes a consolidated summary of these configuration lines to a new file called ports_found.txt.
```

# 3. The Complex Test: Custom Algorithm / Mathematical Simulation
This tests the model's ability to implement pure algorithmic logic, custom functions, and mathematical capabilities inside Rhai's strictly sandboxed environment without relying on external system libraries.

## Prompt:
```
I want to run a quick performance simulation. Write a Rhai script that defines a custom function to calculate the first 15 Fibonacci numbers, stores them in an array, filters out the even numbers, computes the average of the remaining odd numbers, and prints the final calculated average with a clear explanation of each step.
```
# 4. The Autonomous Test: Unfamiliar API Discovery
We specifically trained the model that when faced with an unknown API or an external library requirement (like spinning up SQLite via npx), it should output a single JSON tool call to search the docs first, rather than immediately guessing the code. A successful test here is the model stopping, searching the docs, and then writing the plugin in a subsequent turn.

```
I need a new ChaosNexus Anvil plugin that connects to our local SQLite database (db.sqlite) to pull the top 10 most recent user logins. I'm not sure if ChaosNexus Anvil has a native SQLite driver or if we need to spin up an external MCP server dynamically using npx. Please figure out the correct approach from the documentation and write the plugin for me.
```

# 5. The Security & Persistence Test: Crypto and KV Store
This tests the model's ability to utilize the newly injected native cryptographic algorithms and global state persistence.

## Prompt:
```
I need to securely store an access token. Write a Rhai script that takes a raw string token, hashes it using SHA256, encodes the resulting hash in Base64, and then stores the encoded string into the native ChaosNexus Anvil KV store under the key 'secure_token'. Finally, retrieve the key from the store and print it to verify it was saved correctly.
```

# 6. The Text Processing Test: Regex and JSON Extraction
This tests the model's ability to handle complex text parsing and data extraction natively using the new capabilities.

## Prompt:
```
I have a raw text string containing mixed data. Write a Rhai script that uses native Regex functions to extract all valid email addresses from the text. Then, take a sample JSON string and use native JSON extraction to pull out the 'status' and 'id' fields. Print both the extracted emails and the JSON fields clearly.
```

# 7. The Sandbox Security Gate Test: Deny-by-Default Validation
This tests if the model respects the "Deny-all" configuration by explicitly requesting allowances via the appropriate TOML files when proposing HTTP or shell operations.

## Prompt:
```
I need a ChaosNexus Anvil plugin that runs the `curl` command to fetch data from `https://api.github.com/zen`. Since I know ChaosNexus Anvil blocks shell commands and network requests by default, please provide the exact configuration changes needed in `ChaosNexus Anvil.toml` to allow this, alongside the plugin code itself.
```

# 8. The Pending Plugin Workflow Test: Human-In-The-Loop Approval
This tests if the model correctly handles the `chaoswrench_install_plugin` command and understands that it must wait for the user to approve the plugin in the UI.

## Prompt:
```
Write a Rhai script that uses `chaoswrench_install_plugin` to fetch a community plugin called "system_monitor". Once you've written the script, explain to me exactly how I approve and edit the plugin in the ChaosNexus Forge IDE before it goes live.
```

# 9. Domain 1: Event-Driven & Inter-Plugin Communication (Simple)
How do I use the ChaosNexus Anvil event bus to fire an event that another plugin can listen to? Show me how to use `create_event`, `hook_event`, and `fire_event`.

# 10. Domain 1: Event-Driven & Inter-Plugin Communication (Complex)
We need a decentralized state manager. Write two plugins: the first plugin runs on a timer and writes a random number to the global KV store every 5 seconds, firing an event called 'state_updated'. The second plugin listens to 'state_updated', reads the new value from the global KV store, and logs it.

# 11. Domain 2: MCP Mesh Federation (Simple)
Show me how to connect to an external MCP server running on port 3000 using `mcp_connect`, call a tool named `get_weather`, and log the result.

# 12. Domain 2: MCP Mesh Federation (Complex)
I need to act as an MCP router. Write a plugin that registers a new MCP tool called `router_ping`. When executed, this tool should connect to a downstream MCP server at `http://localhost:8080`, pass the arguments along, and return the aggregated response back up the chain.

# 13. Domain 3: System Diagnostics & Monitoring (Simple)
How do I check the operating system that ChaosNexus Anvil is currently running on?

# 14. Domain 3: System Diagnostics & Monitoring (Complex)
Write a watchdog plugin. It should use `create_timer` to wake up every 60 seconds, check the current OS using `sys_os`, and if the OS is 'windows', use `run_command` to execute `tasklist`. Log the output if successful, or log an error if it fails. Make sure to tell me what `chaosnexus-anvil.toml` capabilities are needed.

# 15. Domain 4: Configuration & Feature Flags (Simple)
Show me how to register a Console Variable (CVar) called 'debug_mode' with a default integer value of 0, and how to read its value later.

# 16. Domain 4: Configuration & Feature Flags (Complex)
We have a custom configuration file called `my_app.toml` in the workspace. Write a plugin that uses `load_config` to read this file. If the file parses successfully, extract the 'max_retries' field and register it as a CVar. If it fails, fallback to registering the CVar with a value of 3.

# 17. Domain 5: Advanced I/O (Simple)
Show me how to connect to a WebSocket endpoint using `ws_connect` and send a message.

# 18. Domain 5: Advanced I/O (Complex)
I need to orchestrate data between two plugins. Plugin A fetches data from a WebSocket and writes it to a shared file using `fs_data_write`. Plugin B needs to use `fs_data_read` to read that file. Please provide the exact permissions needed for Plugin A and B to share filesystem access, and the code for Plugin A.
