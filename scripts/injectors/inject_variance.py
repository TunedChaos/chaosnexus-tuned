import os
import json
import glob
import random
import re

INITIAL_RESPONSES = [
    "I will create this plugin using `cn_a_create_plugin`.",
    "I will draft this plugin using the `cn_a_create_plugin` tool.",
    "Let me generate that plugin for you using `cn_a_create_plugin`.",
    "I'll use `cn_a_create_plugin` to create the requested script.",
    "I'm deploying the `cn_a_create_plugin` tool to fulfill your request.",
    "I can help with that. I'll execute `cn_a_create_plugin` now.",
    "Creating the plugin now via `cn_a_create_plugin`.",
]

FINAL_RESPONSES_TOML = [
    (
        "The plugin has been created and is pending approval. Please add the following configuration to your `chaosnexus-anvil.toml` file:\n```toml\n{toml_content}\n```\nAfter updating the configuration, please approve the plugin in ChaosNexus Forge.",
        "The plugin has been generated and is now locked in a pending state. You will need to add the following configuration block to your `chaosnexus-anvil.toml` file:\n```toml\n{toml_content}\n```\nOnce you've updated the file, you can approve the plugin in ChaosNexus Forge."
    ),
    (
        "The plugin has been created and is pending approval. Please add the following configuration to your `chaosnexus-anvil.toml` file:\n```toml\n{toml_content}\n```\nAfter updating the configuration, please approve the plugin in ChaosNexus Forge.",
        "I've created the script for you. Since it requires additional permissions, please append this config to your workspace's `chaosnexus-anvil.toml`:\n```toml\n{toml_content}\n```\nFinally, authorize the plugin within the ChaosNexus Forge interface."
    ),
    (
        "The plugin has been created and is pending approval. Please add the following configuration to your `chaosnexus-anvil.toml` file:\n```toml\n{toml_content}\n```\nAfter updating the configuration, please approve the plugin in ChaosNexus Forge.",
        "Your plugin is ready but awaits your approval. Please update your `chaosnexus-anvil.toml` with the required permissions:\n```toml\n{toml_content}\n```\nThen, proceed to ChaosNexus Forge to approve it."
    ),
    (
        "The plugin has been created and is pending approval. Please add the following configuration to your `chaosnexus-anvil.toml` file:\n```toml\n{toml_content}\n```\nAfter updating the configuration, please approve the plugin in ChaosNexus Forge.",
        "The Rhai script has been written successfully. Before you can run it, you must declare these permissions in your `chaosnexus-anvil.toml`:\n```toml\n{toml_content}\n```\nPlease review and approve the plugin in the ChaosNexus Forge IDE."
    )
]

FINAL_RESPONSES_NO_TOML = [
    "The plugin has been created and is pending approval. Please approve the plugin in ChaosNexus Forge.",
    "I've drafted the script. You'll need to authorize it in ChaosNexus Forge before it can run.",
    "The implementation is complete. It is currently locked pending your approval in the ChaosNexus Forge IDE.",
    "Check ChaosNexus Forge to review and approve the new plugin.",
    "The plugin was generated successfully. Please head over to ChaosNexus Forge to approve it.",
    "I've created the requested plugin. It's waiting for your approval in ChaosNexus Forge."
]

PROMPT_PREFIXES = [
    "", "", "", "", "", # 50% chance of no prefix
    "Hey, ",
    "Could you help me out? ",
    "I'm trying to build something. ",
    "Quick question: ",
    "I need some help with ChaosNexus Anvil. "
]

def vary_prompt(prompt):
    # Only add prefix if it doesn't already look heavily customized
    if random.random() < 0.3:
        prefix = random.choice(PROMPT_PREFIXES)
        if prefix:
            # lower case the first letter of prompt if we added a prefix that ends in space
            if prefix.endswith(" "):
                prompt = prompt[0].lower() + prompt[1:]
            prompt = prefix + prompt
    return prompt

def vary_jsonl(filepath):
    print(f"Injecting variance into JSONL: {filepath}")
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    new_lines = []
    for line in lines:
        if not line.strip():
            continue
        data = json.loads(line)
        
        for msg in data.get('messages', []):
            if msg.get('role') == 'user':
                msg['content'] = vary_prompt(msg['content'])
            elif msg.get('role') == 'assistant' and 'tool_calls' in msg:
                if msg.get('content') == "I will create this plugin using `cn_a_create_plugin`.":
                    msg['content'] = random.choice(INITIAL_RESPONSES)
            elif msg.get('role') == 'assistant' and not msg.get('tool_calls'):
                content = msg.get('content', '')
                if content == "The plugin has been created and is pending approval. Please approve the plugin in ChaosNexus Forge.":
                    msg['content'] = random.choice(FINAL_RESPONSES_NO_TOML)
                else:
                    # check if it matches the TOML template
                    toml_match = re.search(r'```toml\n(.*?)```', content, re.DOTALL)
                    if toml_match and "After updating the configuration, please approve the plugin in ChaosNexus Forge." in content:
                        toml_content = toml_match.group(1)
                        _, new_template = random.choice(FINAL_RESPONSES_TOML)
                        msg['content'] = new_template.replace("{toml_content}", toml_content)
                        
        new_lines.append(json.dumps(data))
        
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_lines) + '\n')

def vary_sharegpt(filepath):
    print(f"Injecting variance into ShareGPT: {filepath}")
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    for item in data:
        for msg in item.get('conversations', []):
            if msg.get('from') == 'human':
                msg['value'] = vary_prompt(msg['value'])
            elif msg.get('from') == 'gpt' and 'tool_calls' in msg:
                if msg.get('value') == "I will create this plugin using `cn_a_create_plugin`.":
                    msg['value'] = random.choice(INITIAL_RESPONSES)
            elif msg.get('from') == 'gpt' and not msg.get('tool_calls'):
                content = msg.get('value', '')
                if content == "The plugin has been created and is pending approval. Please approve the plugin in ChaosNexus Forge.":
                    msg['value'] = random.choice(FINAL_RESPONSES_NO_TOML)
                else:
                    toml_match = re.search(r'```toml\n(.*?)```', content, re.DOTALL)
                    if toml_match and "After updating the configuration, please approve the plugin in ChaosNexus Forge." in content:
                        toml_content = toml_match.group(1)
                        _, new_template = random.choice(FINAL_RESPONSES_TOML)
                        msg['value'] = new_template.replace("{toml_content}", toml_content)
                        
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

def vary_alpaca(filepath):
    print(f"Injecting variance into Alpaca: {filepath}")
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    for item in data:
        item['instruction'] = vary_prompt(item.get('instruction', ''))
        
        output = item.get('output', '')
        
        # Replace initial
        output = output.replace(
            "I will create this plugin using `cn_a_create_plugin`.\n\n",
            random.choice(INITIAL_RESPONSES) + "\n\n"
        )
        
        # Replace final no-toml
        output = output.replace(
            "The plugin has been created and is pending approval. Please approve the plugin in ChaosNexus Forge.",
            random.choice(FINAL_RESPONSES_NO_TOML)
        )
        
        # Replace final toml
        toml_match = re.search(r'```toml\n(.*?)```\nAfter updating the configuration, please approve the plugin in ChaosNexus Forge\.', output, re.DOTALL)
        if toml_match:
            toml_content = toml_match.group(1)
            old_str = f"The plugin has been created and is pending approval. Please add the following configuration to your `chaosnexus-anvil.toml` file:\n```toml\n{toml_content}```\nAfter updating the configuration, please approve the plugin in ChaosNexus Forge."
            _, new_template = random.choice(FINAL_RESPONSES_TOML)
            new_str = new_template.replace("{toml_content}", toml_content)
            output = output.replace(old_str, new_str)
            
        item['output'] = output
            
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

def main():
    base_dirs = ['chaosnexus-tuned/core', 'chaosnexus-tuned/full_stack']
    for d in base_dirs:
        for jsonl_file in glob.glob(os.path.join(d, '*.jsonl')):
            vary_jsonl(jsonl_file)
            
        for alpaca_file in glob.glob(os.path.join(d, '*alpaca*.json')):
            vary_alpaca(alpaca_file)
            
        for sharegpt_file in glob.glob(os.path.join(d, '*sharegpt*.json')):
            vary_sharegpt(sharegpt_file)

if __name__ == '__main__':
    main()
