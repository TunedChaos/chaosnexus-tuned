import json
import logging
from config import DATASETS_DIR
import utils

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def convert_to_alpaca(input_file, output_file):
    if not input_file.exists():
        logging.warning(f"Input file {input_file} does not exist. Skipping.")
        return

    items = utils.read_jsonl(input_file)
    converted = []
    for item in items:
        converted.append({
            "instruction": item["instruction"],
            "input": "",
            "output": item["response"]
        })

    utils.write_json(output_file, converted)
        
    logging.info(f"Converted {len(converted)} examples to Alpaca format at {output_file}")

def main():
    convert_to_alpaca(
        DATASETS_DIR / "raw_strict.jsonl",
        DATASETS_DIR / "raw_strict_alpaca.json"
    )
    
    convert_to_alpaca(
        DATASETS_DIR / "agentic_xml.jsonl",
        DATASETS_DIR / "agentic_xml_alpaca.json"
    )

    convert_to_alpaca(
        DATASETS_DIR / "agentic_json.jsonl",
        DATASETS_DIR / "agentic_json_alpaca.json"
    )

if __name__ == "__main__":
    main()
