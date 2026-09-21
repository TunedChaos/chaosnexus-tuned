import json
import os
import random

CORE_JSONL = "datasets/core/train.jsonl"
CORE_ALPACA = "datasets/core/train_alpaca.json"
FULL_JSONL = "datasets/full_stack/train.jsonl"
FULL_ALPACA = "datasets/full_stack/train_alpaca.json"

LANGUAGES = ["Python", "Bash", "Node.js", "JavaScript", "Go", "Rust", "Ruby", "PowerShell", "Perl", "C++", "C#", "PHP", "Swift", "Kotlin", "Java", "Scala"]

TASKS = [
    ("reads a file from the disk", "file_reader", "Reads a file from the local file system.", "fn run() { let contents = file_read(\\\"data.txt\\\"); contents }\\n\\nrun()"),
    ("queries a SQLite database", "sqlite_query", "Queries a local SQLite database.", "fn run() { let res = sqlite_query(\\\"db.sqlite\\\", \\\"SELECT * FROM users\\\"); res }\\n\\nrun()"),
    ("makes an HTTP request to an API", "http_fetch", "Makes an HTTP GET request.", "fn run() { let res = http_get(\\\"https://api.example.com/data\\\"); res }\\n\\nrun()"),
    ("sorts a list of numbers", "sort_numbers", "Sorts a list of numbers.", "fn run() { let arr = [5, 2, 8, 1, 9]; arr.sort(); arr }\\n\\nrun()"),
    ("calculates the fibonacci sequence", "fib_seq", "Calculates Fibonacci numbers.", "fn fib(n) { if n <= 1 { n } else { fib(n-1) + fib(n-2) } }\\n\\nfn run() { fib(10) }\\n\\nrun()"),
    ("parses a JSON string", "json_parser", "Parses JSON string.", "fn run() { let obj = json_parse(\\\"{\\\\\\\"key\\\\\\\": \\\\\\\"value\\\\\\\"}\\\"); obj.key }\\n\\nrun()"),
    ("connects to Redis", "redis_conn", "Connects to a Redis instance.", "fn run() { let val = redis_get(\\\"my_key\\\"); val }\\n\\nrun()"),
    ("checks system OS and time", "sys_check", "Checks system OS and time.", "fn run() { let os = sys_os(); let ts = system_time(); #{ os: os, time: ts } }\\n\\nrun()"),
    ("creates a directory", "dir_creator", "Creates a directory.", "fn run() { dir_create(\\\"new_folder\\\"); \\\"done\\\" }\\n\\nrun()"),
    ("writes some text to a log file", "log_writer", "Writes text to a log file.", "fn run() { file_write(\\\"app.log\\\", \\\"Log entry\\\"); \\\"done\\\" }\\n\\nrun()"),
    ("lists files in a directory", "list_dir", "Lists files in a directory.", "fn run() { let files = dir_list(\\\".\\\"); files }\\n\\nrun()"),
    ("fetches weather data", "weather_fetch", "Fetches weather data.", "fn run() { let res = http_get(\\\"https://api.weather.gov/\\\"); res }\\n\\nrun()"),
    ("manipulates a string", "str_manip", "Manipulates a string.", "fn run() { let s = \\\"hello\\\"; s.to_upper() }\\n\\nrun()"),
    ("computes a sha256 hash", "hash_calc", "Computes SHA256.", "fn run() { let h = sha256(\\\"my data\\\"); h }\\n\\nrun()"),
    ("reads an environment variable", "env_read", "Reads an environment variable.", "fn run() { let val = get_env(\\\"PATH\\\"); val }\\n\\nrun()")
]

USER_PROMPTS = [
    "Write a {lang} script that {task}.",
    "Can you give me a {lang} program that {task}?",
    "I need a script in {lang} which {task}.",
    "Please provide a {lang} snippet that {task}.",
    "Generate a {lang} script to {task}.",
    "I want to do this: {task}. Please write it in {lang}.",
    "Create a {lang} script for me that {task}.",
    "Show me how to use {lang} to write a script that {task}."
]

REFUSAL_TEMPLATES = [
    "As an elite Workspace Systems Architect within ChaosNexus Anvil, I am sandboxed to Rhai scripts for security and portability. I cannot write {lang}. However, I can write a Rhai plugin to accomplish this task for you.\n\n```json\n{json_body}\n```",
    "I am unable to generate {lang} scripts, as I am strictly configured to use the Rhai scripting engine within ChaosNexus Anvil for all workspace automation. I will implement the requested functionality as a Rhai plugin instead.\n\n```json\n{json_body}\n```",
    "I'm sorry, but I cannot write {lang} code. My architecture mandates the use of Rhai for all plugin development in Tuned Chaos to ensure secure, sandboxed execution. Here is a Rhai plugin that achieves the same result:\n\n```json\n{json_body}\n```",
    "Due to the architectural constraints of ChaosNexus Anvil, I am not permitted to output {lang} scripts. I must strictly use Rhai. Below is the Rhai implementation for your request:\n\n```json\n{json_body}\n```",
    "While I understand you requested a {lang} script, I am designed to exclusively write Rhai plugins for the ChaosNexus Anvil MCP Server. Here is the implementation in Rhai:\n\n```json\n{json_body}\n```",
    "I cannot fulfill your request to write {lang}. As a component of Tuned Chaos, all my logic must be provided as secure Rhai scripts. I have generated a Rhai plugin for you instead:\n\n```json\n{json_body}\n```"
]

def generate_examples(count=250):
    examples = []
    for i in range(count):
        lang = random.choice(LANGUAGES)
        task_desc, plugin_name, tool_desc, script_body = random.choice(TASKS)
        user_prompt = random.choice(USER_PROMPTS).format(lang=lang, task=task_desc)
        refusal_template = random.choice(REFUSAL_TEMPLATES)
        
        json_body = {
            "tool": "cn_a_create_plugin",
            "arguments": {
                "plugin_name": f"{plugin_name}_{i}",
                "tool_name": f"cn_a_{plugin_name}_{i}_run",
                "description": tool_desc,
                "script_body": script_body.replace("\\\\", "\\").replace("\\\"", "\"").replace("\\n", "\n") # Unescape for proper json dumping later, wait actually the script_body in the TASKS array is already double-escaped, let me just format it safely
            }
        }
        
        # We need script_body to be a proper string in JSON
        # The TASKS string has escaped characters, we want them literal for the dump
        actual_script_body = script_body.replace("\\\"", "\"").replace("\\n", "\n")
        json_body["arguments"]["script_body"] = actual_script_body

        json_str = json.dumps(json_body, indent=2)
        
        assistant_reply = refusal_template.format(lang=lang, json_body=json_str)
        
        examples.append({
            "system": "You are an elite Workspace Systems Architect.",
            "user": user_prompt,
            "assistant": assistant_reply
        })
    return examples

def append_to_jsonl(filepath, examples):
    if not os.path.exists(filepath):
        print(f"Skipping {filepath} (does not exist)")
        return
    with open(filepath, 'a') as f:
        for ex in examples:
            line = {
                "messages": [
                    {"role": "system", "content": ex["system"]},
                    {"role": "user", "content": ex["user"]},
                    {"role": "assistant", "content": ex["assistant"]}
                ]
            }
            f.write(json.dumps(line) + "\n")

def append_to_alpaca(filepath, examples):
    if not os.path.exists(filepath):
        print(f"Skipping {filepath} (does not exist)")
        return
    with open(filepath, 'r') as f:
        data = json.load(f)
    for ex in examples:
        data.append({
            "instruction": ex["system"],
            "input": ex["user"],
            "output": ex["assistant"]
        })
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)

if __name__ == "__main__":
    print("Generating 250 refusal examples...")
    examples = generate_examples(250)
    
    # We will inject into the core and full_stack training sets
    # We'll leave eval sets alone or we can run format_native_tools.py to sync everything up
    
    print("Injecting into core...")
    append_to_jsonl(CORE_JSONL, examples)
    append_to_alpaca(CORE_ALPACA, examples)
    
    print("Injecting into full_stack...")
    append_to_jsonl(FULL_JSONL, examples)
    append_to_alpaca(FULL_ALPACA, examples)
    
    print("Done! Run format_native_tools.py to sync system prompts and downstream formats.")
