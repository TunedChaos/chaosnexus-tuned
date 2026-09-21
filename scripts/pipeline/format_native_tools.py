import os
import json

from pathlib import Path
DATASETS_DIR = Path(os.path.dirname(os.path.abspath(__file__))).parent.parent / "datasets"

# We will process the ChatML files in core/ and full_stack/, and then automatically
# generate the corresponding Alpaca and ShareGPT variants from them.
TARGET_DIRS = [
    os.path.join(DATASETS_DIR, "core")
]

def extract_json_object(text):
    start_idx = text.find('```json')
    if start_idx == -1:
        return None, text
    end_idx = text.find('```', start_idx + 7)
    if end_idx == -1:
        return None, text
    
    json_str = text[start_idx+7:end_idx].strip()
    try:
        parsed = json.loads(json_str)
        # We no longer remove the markdown block from text since we want to embed it
        return parsed, text.strip()
    except Exception:
        return None, text

def process_chatml(filepath):
    """
    Parses the raw ChatML train.jsonl (with markdown JSON blocks), 
    extracts them into native OpenAI tool_calls arrays, and returns the structured data.
    """
    if not os.path.exists(filepath):
        print(f"Skipping {filepath} (not found)")
        return []
        
    chatml_data = []
    changes_made = 0
    
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            if not line.strip():
                continue
            try:
                data = json.loads(line)
                if "messages" in data:
                    new_messages = []
                    for msg in data["messages"]:
                        if msg["role"] == "system":
                            msg["content"] = "You are an elite Workspace Systems Architect. You master the ChaosNexus Anvil MCP. You autonomously discover and leverage capabilities provided by your workspace environment. You MUST ONLY write Rhai scripts when creating plugins. NEVER output Python, Bash, Node.js, or any other language. Always search for plugins before creating one."
                            changes_made += 1
                            new_messages.append(msg)
                        elif msg["role"] == "user":
                            new_messages.append(msg)
                        elif msg["role"] == "assistant":
                            original_content = msg.get("content", "")
                            extracted_json, new_content = extract_json_object(original_content)
                            
                            if extracted_json and extracted_json.get("tool") == "cn_a_create_plugin":
                                args = extracted_json.get("arguments", {})
                                plugin_name = args.get("plugin_name", "unknown")
                                
                                # Inject search tool call
                                search_call = {
                                    "role": "assistant",
                                    "content": f"Let me check if a plugin already exists to handle this task.\n\n```json\n{{\n  \"tool\": \"cn_a_search_plugins\",\n  \"arguments\": {{\n    \"query\": \"{plugin_name}\"\n  }}\n}}\n```",
                                    "tool_calls": [{
                                        "type": "function",
                                        "function": {
                                            "name": "cn_a_search_plugins",
                                            "arguments": json.dumps({"query": plugin_name})
                                        }
                                    }]
                                }
                                new_messages.append(search_call)
                                
                                # Inject tool response for search
                                tool_resp_search = {
                                    "role": "tool",
                                    "name": "cn_a_search_plugins",
                                    "content": json.dumps([{"name": f"old_{plugin_name}", "description": "An existing but outdated plugin"}])
                                }
                                new_messages.append(tool_resp_search)
                                
                                # Inject read tool call
                                read_call = {
                                    "role": "assistant",
                                    "content": f"I found a plugin named `old_{plugin_name}`. Let me read its contents to see if it satisfies the requirement.\n\n```json\n{{\n  \"tool\": \"cn_a_read_plugin\",\n  \"arguments\": {{\n    \"plugin_name\": \"old_{plugin_name}\"\n  }}\n}}\n```",
                                    "tool_calls": [{
                                        "type": "function",
                                        "function": {
                                            "name": "cn_a_read_plugin",
                                            "arguments": json.dumps({"plugin_name": f"old_{plugin_name}"})
                                        }
                                    }]
                                }
                                new_messages.append(read_call)
                                
                                # Inject tool response for read
                                tool_resp_read = {
                                    "role": "tool",
                                    "name": "cn_a_read_plugin",
                                    "content": json.dumps({"error": "Plugin is deprecated and lacks required capabilities."})
                                }
                                new_messages.append(tool_resp_read)
                                
                                # Now append the original create_plugin call, but prefix the content
                                prefix = f"The existing `old_{plugin_name}` plugin is deprecated and missing what we need. I will create a new plugin named `{plugin_name}`.\n\n"
                                # If the content already starts with some narrative, we keep it, just prepend
                                if not new_content.startswith("The existing"):
                                    msg["content"] = prefix + new_content
                                else:
                                    msg["content"] = new_content
                                    
                                msg["tool_calls"] = [{
                                    "type": "function",
                                    "function": {
                                        "name": "cn_a_create_plugin",
                                        "arguments": json.dumps(args)
                                    }
                                }]
                                changes_made += 1
                                new_messages.append(msg)
                            else:
                                if extracted_json:
                                    msg["content"] = new_content
                                    msg["tool_calls"] = [{
                                        "type": "function",
                                        "function": {
                                            "name": extracted_json.get("tool", "unknown"),
                                            "arguments": json.dumps(extracted_json.get("arguments", {}))
                                        }
                                    }]
                                new_messages.append(msg)
                    data["messages"] = new_messages
                chatml_data.append(data)
            except Exception as e:
                print(f"Error processing line in {filepath}: {e}")
                
    if changes_made > 0:
        print(f"Converted {changes_made} messages to native tool calls in {filepath}")
    
    return chatml_data

def save_chatml(data, filepath):
    with open(filepath, 'w', encoding='utf-8') as f:
        for item in data:
            f.write(json.dumps(item) + '\n')
    print(f"Saved ChatML (JSONL) to {filepath}")

def convert_to_alpaca(chatml_data, filepath):
    alpaca_data = []
    for item in chatml_data:
        messages = item.get("messages", [])
        system_msg = ""
        user_msg = ""
        assistant_msg = ""
        
        for msg in messages:
            if msg["role"] == "system":
                system_msg = msg["content"]
            elif msg["role"] == "user":
                user_msg = msg["content"]
            elif msg["role"] == "assistant":
                content = msg.get("content", "")
                if assistant_msg:
                    assistant_msg += "\n\n"
                assistant_msg += content
            elif msg["role"] == "tool":
                content = msg.get("content", "")
                if assistant_msg:
                    assistant_msg += "\n\n"
                assistant_msg += f"<|tool_response|>\n{content}"
                
        alpaca_data.append({
            "instruction": system_msg,
            "input": user_msg,
            "output": assistant_msg
        })
        
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(alpaca_data, f, indent=2)
    print(f"Saved Alpaca to {filepath}")

def convert_to_sharegpt(chatml_data, filepath):
    sharegpt_data = []
    for item in chatml_data:
        messages = item.get("messages", [])
        conversations = []
        for msg in messages:
            role = msg["role"]
            if role == "user":
                role = "human"
            elif role == "assistant":
                role = "gpt"
            elif role == "tool":
                role = "observation"
                
            conv = {
                "from": role,
                "value": msg.get("content", "")
            }
            
            # Unsloth/ShareGPT tool format
            if "tool_calls" in msg:
                conv["tool_calls"] = msg["tool_calls"]
                
            conversations.append(conv)
            
        sharegpt_data.append({"conversations": conversations})
        
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(sharegpt_data, f, indent=2)
    print(f"Saved ShareGPT to {filepath}")

def main():
    print("Starting native tool calling formatting...")
    
    for directory in TARGET_DIRS:
        for prefix in ["train", "eval"]:
            chatml_file = os.path.join(directory, f"{prefix}.jsonl")
            
            chatml_data = process_chatml(chatml_file)
            
            if chatml_data:
                # Save all 3 formats
                save_chatml(chatml_data, chatml_file)
                
                alpaca_file = os.path.join(directory, f"{prefix}_alpaca.json")
                convert_to_alpaca(chatml_data, alpaca_file)
                
                sharegpt_file = os.path.join(directory, f"{prefix}_sharegpt.json")
                convert_to_sharegpt(chatml_data, sharegpt_file)
            
    print("Formatting complete.")

if __name__ == "__main__":
    main()
