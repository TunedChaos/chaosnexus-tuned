import json
import logging
from config import DATASETS_DIR
import utils

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def convert_file(input_file, output_file, system_prompt):
    if not input_file.exists():
        logging.warning(f"Input file {input_file} does not exist. Skipping.")
        return

    items = utils.read_jsonl(input_file)
    converted = []
    
    for item in items:
        conversations = []
        if system_prompt:
            conversations.append({
                "from": "system",
                "value": system_prompt
            })
        
        conversations.append({
            "from": "human",
            "value": item["instruction"]
        })
        conversations.append({
            "from": "gpt",
            "value": item["response"]
        })
        
        converted.append({
            "conversations": conversations
        })

    utils.write_json(output_file, converted)
        
    logging.info(f"Converted {len(converted)} examples to ShareGPT format at {output_file}")

def main():
    # Read system prompts from ChaosNexus Tuned_Training_Rules.md or hardcode them based on the rules we wrote
    sys_strict = (
        "You are ChaosNexus Tuned, the industrial automation brain of the Tuned Chaos ecosystem.\n"
        "Your sole purpose is to translate natural language intentions into raw, valid Rhai scripts executable by the ChaosNexus Anvil engine.\n"
        "CRITICAL DIRECTIVES:\n"
        "1. Output ONLY valid, executable Rhai code.\n"
        "2. Do NOT wrap code in markdown blocks (no ```rhai).\n"
        "3. Do NOT include conversational greetings, explanations, or post-script text.\n"
        "4. If a request lacks structural context, assume standard Unix file structures or state handling native to ChaosNexus Anvil."
    )

    sys_xml = (
        "You are ChaosNexus Tuned, the industrial automation brain of the Tuned Chaos ecosystem.\n"
        "Your purpose is to act as an agentic full-stack generator.\n"
        "CRITICAL DIRECTIVES:\n"
        "1. You must wrap all edits in strict XML blocks: <file path=\"FILE_PATH\" action=\"MODIFY|CREATE|DELETE\"> ... </file>\n"
        "2. Do NOT include conversational text. Only output the XML block.\n"
        "3. You may output multiple XML blocks consecutively if multiple files are affected."
    )

    sys_json = (
        "You are ChaosNexus Tuned, the industrial automation brain of the Tuned Chaos ecosystem.\n"
        "Your purpose is to act as an agentic full-stack generator using tool calls.\n"
        "CRITICAL DIRECTIVES:\n"
        "1. You must output a JSON object representing tool calls to edit_file.\n"
        "2. Format: {\"tool_calls\": [{\"name\": \"edit_file\", \"arguments\": {\"path\": \"FILE_PATH\", \"action\": \"MODIFY\", \"content\": \"...\"}}]}\n"
        "3. Do NOT include conversational text or markdown blocks. Only output valid JSON."
    )

    convert_file(
        DATASETS_DIR / "raw_strict.jsonl",
        DATASETS_DIR / "raw_strict_sharegpt.json",
        sys_strict
    )
    
    convert_file(
        DATASETS_DIR / "agentic_xml.jsonl",
        DATASETS_DIR / "agentic_xml_sharegpt.json",
        sys_xml
    )

    convert_file(
        DATASETS_DIR / "agentic_json.jsonl",
        DATASETS_DIR / "agentic_json_sharegpt.json",
        sys_json
    )

if __name__ == "__main__":
    main()
