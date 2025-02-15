import random
import sys
import os
import json
import re
current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print(current_dir)
sys.path.append(current_dir)
from attributes_tasks_domains import task_info
from utils import resume_from_generated, load_items

def extract(model_response):
    try:
        # Use regex to match lines starting with a dash, allowing spaces before and after the dash
        pattern = r'^\s*-\s*(.+?)\s*$'
        
        # Find all matches in the text
        matches = re.findall(pattern, model_response, re.MULTILINE)
        
        # Check if any matches were found
        if not matches:
            raise ValueError("No valid list items found in the input string.")
        
        # Check if any items are empty or too long (>50 chars)
        if any((item.strip() == '') or (len(item.strip())>50) for item in matches):
            raise ValueError("One or more items are empty after removing leading/trailing whitespace.")
        
        # Return the list items with whitespace removed
        return [item.strip() for item in matches]
    
    except Exception as e:
        raise RuntimeError(f"Extraction failed: {str(e)}")
    
def generate_responses(input_data, output_file):
    with open(output_file, "w", encoding='utf-8') as outfile:
        for i, input in enumerate(input_data):
            model_response = input["output"]
            subjects = extract(model_response)
            output_dict = input.copy()
            output_dict["subjects"] = subjects
            output_dict.pop("output")
            json.dump(output_dict, outfile, ensure_ascii=False)
            outfile.write("\n")
    
if __name__ == "__main__":
    for task in task_info:
        input_file = f"testset/output/{task}/question/subjects.jsonl"
        output_file = f"testset/output/{task}/question/subjects_extracted.jsonl"
        # if input file does not exist, skip
        if not os.path.exists(input_file):
            print(f"[Warning] The file '{input_file}' does not exist, skip.")
            continue
        if not os.path.exists(os.path.dirname(output_file)):
            os.makedirs(os.path.dirname(output_file))
        input_data = load_items(input_file)
        generate_responses(input_data, output_file)