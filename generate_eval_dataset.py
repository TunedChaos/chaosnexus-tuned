import os
import json
import re
from google import genai
from google.genai import types
from tenacity import Retrying, stop_after_attempt, wait_exponential

def make_turn(role, content):
    return {"role": role, "content": content}

def make_sharegpt_turn(from_role, value):
    return {"from": from_role, "value": value}

def tool_call(name, args):
    return make_turn("assistant", json.dumps({"tool_calls": [{"name": name, "arguments": args}]}))

def tool_response(name, result):
    return make_turn("tool", json.dumps({"tool_name": name, "result": result}))

SYSTEM_PROMPT = """You are ChaosNexus Tuned, the industrial automation brain of the Tuned Chaos ecosystem.

# GLOBAL RULES
1. **NARRATIVE COMMENTING**: All generated code (whether Rhai scripts, Rust, or Svelte UI components) MUST include extremely thorough, non-technical friendly, narrative-style comments explaining the "why" and "how" behind the logic. This applies to all matrices (A, B, and C). The code should be easily understandable by a beginner.

# MATRIX C: AGENTIC JSON TOOL PROTOCOL (Unified / Tool-calling)
1. You must output a JSON object representing tool calls.
2. Format: `{"tool_calls": [{"name": "tool_name", "arguments": {"arg1": "val1"}}]}`
3. Do NOT include conversational text or markdown blocks. Only output valid JSON.
4. **DOCUMENTATION AUTONOMY**: If a task requires using an unfamiliar API or complex framework, you must autonomously figure it out by leaning on ChaosNexus Anvil (`cn_a_` tools). You should attempt to find local documentation first (e.g., querying available MCP servers or reading locally synced documentation via `cn_a_` tools). ChaosNexus Codex (`cn_c_`) may not always be available, so do not blindly assume it is there. If the user provides a link or reference (e.g., a documentation URL or a GitHub repo), you must STILL attempt to find and verify the documentation locally first. However, if it cannot be found locally, you are allowed to use that link to "drill down", clone the repository, or fetch the web documentation in order to dynamically increase the local knowledgebase within ChaosNexus Codex (since `cn_c` supports adding to itself on the fly) before committing any code changes.
"""

def build_conversation(scenario):
    messages = [make_turn("system", SYSTEM_PROMPT)]
    messages.append(make_turn("user", scenario["prompt"]))
    
    if scenario.get("docs_search"):
        messages.append(tool_call("cn_a__cn_c_search_docs", {"query": scenario["docs_search"]}))
        messages.append(tool_response("cn_a__cn_c_search_docs", "Found relevant documentation for: " + scenario["docs_search"]))
        
    args = {
        "plugin_name": scenario["plugin_name"],
        "tool_name": f"{scenario['plugin_name']}_tool",
        "description": "Generated plugin.",
        "script_body": scenario["script"]
    }
    if scenario.get("toml"):
        args["custom_toml"] = scenario["toml"]
        
    messages.append(tool_call("cn_a_create_plugin", args))
    
    messages.append(tool_response("cn_a_create_plugin", f"PENDING human approval in ChaosNexus Forge.\\n\\nStaged quarantined plugin at .pending/{scenario['plugin_name']}.rhai"))
    messages.append(make_turn("assistant", "I have created the plugin and it is now in a pending state. Please review and approve it inside the ChaosNexus Forge IDE. Once you approve it, let me know."))
    
    messages.append(make_turn("user", "Approved."))
    messages.append(tool_call("cn_a_reload_plugins", {}))
    messages.append(tool_response("cn_a_reload_plugins", "Plugins reloaded successfully."))
    messages.append(make_turn("assistant", "The plugins have been hot-reloaded successfully. Your new tool is now active and ready to be used."))
    
    sharegpt_conv = []
    for msg in messages:
        if msg["role"] == "system":
            sharegpt_conv.append(make_sharegpt_turn("system", msg["content"]))
        elif msg["role"] == "user":
            sharegpt_conv.append(make_sharegpt_turn("human", msg["content"]))
        elif msg["role"] == "assistant":
            sharegpt_conv.append(make_sharegpt_turn("gpt", msg["content"]))
        elif msg["role"] == "tool":
            sharegpt_conv.append(make_sharegpt_turn("tool", msg["content"]))

    return {"messages": messages}, {"conversations": sharegpt_conv}

GEMINI_PROMPT = """You are an expert AI data generation system. I need you to act as a "Teacher" model to generate synthetic training data for a smaller 8B parameter model.
The 8B model will act as "ChaosNexus Tuned", an industrial automation brain that uses Rhai scripts to interact with a system called ChaosNexus Anvil.

Your task is to generate the PERFECT "Golden" scenario for the following exact user prompt.
You must output a raw JSON object within an array (length 1). The JSON schema must strictly be:
[
  {
    "prompt": "The exact user prompt provided below.",
    "docs_search": "The query to search docs with, or null if simple enough. Ensure the agent attempts to find local sources of information first.",
    "plugin_name": "A short snake_case name for the plugin",
    "script": "The full Rhai script containing highly descriptive narrative comments.",
    "toml": "The string contents of the TOML file if permissions are needed, else null."
  }
]

USER PROMPT TO RESPOND TO:
{prompt_text}

OUTPUT ONLY VALID JSON. Do not include markdown formatting like ```json.
"""

def extract_prompts(filepath):
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Split by headings
    sections = re.split(r'(?:^|\n)# \d+\.\s+', content)
    prompts = []
    for section in sections[1:]: # Skip preamble if any
        # If there's a ``` block, extract it
        code_blocks = re.findall(r'```(.*?)```', section, re.DOTALL)
        if code_blocks:
            prompt = code_blocks[0].strip()
        else:
            # Otherwise grab the text after the heading line
            lines = section.strip().split('\n')
            if len(lines) > 1:
                prompt = '\n'.join(lines[1:]).strip()
            else:
                prompt = lines[0].strip()
        
        # Clean up Markdown headings inside
        prompt = re.sub(r'^## Prompt:\s*', '', prompt).strip()
        if prompt:
            prompts.append(prompt)
    return prompts

def main():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable not set.")
        return

    client = genai.Client()
    
    train_data = []
    sharegpt_data = []
    alpaca_data = []

    questions_path = "chaosnexus-tuned/tests/eval/Questions.md"
    prompts = extract_prompts(questions_path)
    
    print(f"Extracted {len(prompts)} questions from {questions_path}.")
    
    for i, p_text in enumerate(prompts):
        print(f"Generating Golden Eval for Question {i+1}/{len(prompts)}...")
        
        dynamic_prompt = GEMINI_PROMPT.replace("{prompt_text}", p_text)
        
        try:
            for attempt in Retrying(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=2, max=10)):
                with attempt:
                    response = client.models.generate_content(
                        model='gemini-3.1-pro-preview',
                        contents=dynamic_prompt,
                        config=types.GenerateContentConfig(
                            temperature=0.2, # Lower temp for consistent golden answers
                        )
                    )
                    
                    raw_text = response.text.strip()
                    if raw_text.startswith("```json"):
                        raw_text = raw_text[7:]
                    if raw_text.endswith("```"):
                        raw_text = raw_text[:-3]
                        
                    scenarios = json.loads(raw_text)
                    
                    for sc in scenarios:
                        chatml, sharegpt = build_conversation(sc)
                        train_data.append(chatml)
                        sharegpt_data.append(sharegpt)
                        
                        alpaca_data.append({
                            "instruction": sc["prompt"],
                            "input": "",
                            "output": json.dumps({"tool_calls": [{"name": "cn_a_create_plugin", "arguments": {"plugin_name": sc["plugin_name"], "script_body": sc["script"]}}]})
                        })
        except Exception as e:
            print(f"Failed to generate eval for question {i+1} after multiple retries: {e}")

    os.makedirs("datasets/eval", exist_ok=True)
    
    with open("datasets/eval/eval_augmented.jsonl", "w") as f:
        for item in train_data:
            f.write(json.dumps(item) + "\n")
            
    with open("datasets/eval/eval_sharegpt_augmented.json", "w") as f:
        json.dump(sharegpt_data, f, indent=2)
        
    with open("datasets/eval/eval_alpaca_augmented.json", "w") as f:
        json.dump(alpaca_data, f, indent=2)

    print(f"Success! Generated {len(train_data)} golden evaluation scenarios.")

if __name__ == "__main__":
    main()
