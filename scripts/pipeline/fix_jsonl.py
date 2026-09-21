import json

def fix_jsonl(filepath):
    with open(filepath, 'r') as f:
        content = f.read()

    # Split concatenated objects
    fixed_content = content.replace('}\\n{"messages"', '}\n{"messages"')
    
    # Remove trailing literal \n if it exists
    if fixed_content.endswith('\\n'):
        fixed_content = fixed_content[:-2] + '\n'

    # Remove trailing literal \n followed by real \n
    if fixed_content.endswith('\\n\n'):
        fixed_content = fixed_content[:-3] + '\n'

    with open(filepath, 'w') as f:
        f.write(fixed_content)

    # Verify
    try:
        with open(filepath, 'r') as f:
            lines = f.readlines()
            for i, line in enumerate(lines):
                if line.strip():
                    json.loads(line)
        print(f"Successfully fixed {filepath}")
    except Exception as e:
        print(f"Error verifying {filepath}: {e} on line {i}")

fix_jsonl('core/train.jsonl')
