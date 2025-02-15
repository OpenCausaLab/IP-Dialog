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
user_attr_groups_file = "random_attribute_group.jsonl"
user_attrs = load_items(user_attr_groups_file)
user_attr_count = 0
def get_user_attr(user_attr_group):
    global user_attr_count
    user_attr = user_attr_group[user_attr_count]
    user_attr_count += 1
    assert user_attr_count < len(user_attr_group)
    return user_attr

def reextract_request(request):
    # Pattern to match optional "request N:" prefix and capture the main content
    pattern = r'(?:request\s*\d+:\s*)?(.*?)\s*$'
    match = re.search(pattern, request, re.IGNORECASE | re.DOTALL)
    
    if match:
        extracted_request = match.group(1).strip()
        if extracted_request:
            return extracted_request
        else:
            raise ValueError("Extracted request content is empty")
    else:
        raise ValueError("Could not extract valid request from input")
    
def extract(model_response):
    # Pattern to match both formats:
    # 1. Lines starting with "- " followed by any text up to the end of the line or start of [
    # 2. Ignore any content within [ ]
    pattern = r"^-\s*(.*?)(?=\s*\[|$)"
    
    requests = re.findall(pattern, model_response, re.MULTILINE)
    
    if len(requests) not in  [3, 4]:
        raise ValueError(f"Expected 3 or 4 user requests, but found {len(requests)}. Model Response is:\n{model_response}")
    
    # Clean and check each request
    cleaned_requests = []
    for i, request in enumerate(requests, 1):
        cleaned = request.strip()
        if not cleaned:
            raise ValueError(f"Request {i} is empty after cleaning.")
        if re.search(r'\b(answer)\b', cleaned, re.IGNORECASE):
            raise ValueError(f"Request {i} contains invalid keywords ('answer'). {request}\n {model_response}")
        cleaned = reextract_request(cleaned)
        cleaned_requests.append(cleaned)
    
    return cleaned_requests
    
def generate_responses(input_data, output_file):
    with open(output_file, "w", encoding='utf-8') as outfile:
        for i, input in enumerate(input_data):
            model_response = input["output"]
            requests = extract(model_response)
            output_dict = input.copy()
            output_dict["requests"] = requests
            output_dict.pop("output")
            json.dump(output_dict, outfile, ensure_ascii=False)
            outfile.write("\n")

def generate_responses_for_risk_detect(output_file, number):
    with open(output_file, "w", encoding='utf-8') as outfile:
        for i in range(number):
            user_attr_group = get_user_attr(user_attrs)
            output_dict = {"task": "risk_detect", "task_index": i, "domain_index": -1, "subject_index": -1,
                           "domain": None, "subject": None, 
                           "user_attr_group": user_attr_group,
                           "requests":["What risks do you think I might face?"]}
            json.dump(output_dict, outfile, ensure_ascii=False)
            outfile.write("\n")
        
if __name__ == "__main__":
    for task in task_info:
        input_file = f"testset/output/{task}/question/user_request.jsonl"
        output_file = f"testset/output/{task}/question/user_request_extracted.jsonl"
        # if input file does not exist, skip
        if not os.path.exists(os.path.dirname(output_file)):
            os.makedirs(os.path.dirname(output_file))
        if task == "risk_detect":
            number = 1500
            generate_responses_for_risk_detect(output_file, number)
            continue
        if not os.path.exists(input_file):
            print(f"[Warning] The file '{input_file}' does not exist, skip.")
            continue
        input_data = load_items(input_file)
        generate_responses(input_data, output_file)