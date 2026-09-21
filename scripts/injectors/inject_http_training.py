import json
import os

# Example 1: http_get
user_prompt_1 = "Write a script that fetches the server status from https://httpbin.org/status/200 and prints the output. Remember it must use early returns and avoid global returns."
assistant_response_1 = """I will create a plugin to fetch the URL using the native `http_get` function. Because `http_get` requires network permissions, you must manually update `ChaosNexus Anvil.toml` before approving the plugin.

Please add the following to `ChaosNexus Anvil.toml`:
```toml
[plugins.fetch_status.permissions]
domain = "httpbin.org"
methods = ["GET"]
```

```json
{
  "tool": "cn_a_create_plugin",
  "arguments": {
    "plugin_name": "fetch_status",
    "tool_name": "cn_a_fetch_status_run",
    "description": "Fetches the server status from httpbin.",
    "script_body": "fn fetch_status() {\\n    let res = http_get(\\"https://httpbin.org/status/200\\");\\n    if type_of(res) == \\"()\\" {\\n        return \\"Failed to fetch\\";\\n    }\\n    print(res);\\n}\\n\\nfetch_status()"
  }
}
```
Please approve this plugin in ChaosNexus Forge."""

# Example 2: ws_connect
user_prompt_2 = "I need to connect to a websocket at wss://ws.postman-echo.com/raw and log the messages. Structure it safely with no global returns."
assistant_response_2 = """I will create a plugin that uses the native `ws_connect` function and a callback to log incoming messages. You must explicitly allow network access in your configuration first.

Please add this to `ChaosNexus Anvil.toml`:
```toml
[plugins.ws_logger.permissions]
domain = "ws.postman-echo.com"
methods = ["WS"]
```

```json
{
  "tool": "cn_a_create_plugin",
  "arguments": {
    "plugin_name": "ws_logger",
    "tool_name": "cn_a_ws_logger_run",
    "description": "Connects to a websocket and logs messages.",
    "script_body": "fn on_ws_message(msg) {\\n    print(\\"WS: \\" + msg);\\n}\\n\\nfn start_ws() {\\n    ws_connect(\\"wss://ws.postman-echo.com/raw\\", \\"on_ws_message\\");\\n    return \\"Connected\\";\\n}\\n\\nstart_ws()"
  }
}
```
Please approve this plugin in ChaosNexus Forge."""

def get_system_prompt(jsonl_path):
    return "You are an elite Workspace Systems Architect. You master the ChaosNexus Anvil MCP. You autonomously discover and leverage capabilities provided by your workspace environment."

def inject_jsonl(filepath):
    if not os.path.exists(filepath):
        print(f"Skipping {filepath}, does not exist.")
        return
        
    system_prompt = get_system_prompt(filepath)
    
    with open(filepath, 'a') as f:
        # Append Example 1
        obj1 = {
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt_1},
                {"role": "assistant", "content": assistant_response_1}
            ]
        }
        f.write(json.dumps(obj1) + '\n')
        
        # Append Example 2
        obj2 = {
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt_2},
                {"role": "assistant", "content": assistant_response_2}
            ]
        }
        f.write(json.dumps(obj2) + '\n')
    print(f"Injected JSONL examples into {filepath}")

def inject_alpaca(filepath):
    if not os.path.exists(filepath):
        print(f"Skipping {filepath}, does not exist.")
        return
        
    with open(filepath, 'r') as f:
        data = json.load(f)
        
    system_prompt = data[0]["instruction"] if len(data) > 0 else "System Prompt"
    
    data.append({
        "instruction": system_prompt,
        "input": user_prompt_1,
        "output": assistant_response_1
    })
    
    data.append({
        "instruction": system_prompt,
        "input": user_prompt_2,
        "output": assistant_response_2
    })
    
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"Injected Alpaca examples into {filepath}")

# Inject into core
inject_jsonl('datasets/core/train.jsonl')
inject_alpaca('datasets/core/train_alpaca.json')

# Inject into full_stack
inject_jsonl('datasets/full_stack/train.jsonl')
inject_alpaca('datasets/full_stack/train_alpaca.json')

print("Done injecting HTTP training data.")
