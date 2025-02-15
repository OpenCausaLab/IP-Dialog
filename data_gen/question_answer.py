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

prompt_template = """You are a helpful agent for the task: {task}. The task requires agent to {task_description}
You will leverage the user's attributes to respond to the request in a personalized way. The user request you need to respond to is: {request}
---Important Note---
- First, list the user attributes you will use to answer the request in Attributes: [..]. Then, provide the reasoning process for your answer in Analysis: [..]. Finally, present your formatted answer in Answer: [..].
- You should select the user attributes that are most relevant to the request. Use no more than 5 attributes. The attributes should be selected from the given user attribute group.
- Your reasoning should be concise and clear.
- {answer_note}
- Output your response in the format below, do not omit the [] in your response:
Output: 
- Attributes: [..].
- Analysis: [..].
- Answer: [..].
{additional_output}
---Example---
User Attribute Group: {example_user_attribute_group}
{example_request_and_response}
---Your Response---
User Attribute Group: {user_attribute_group}
User: {request}
Output: """

def generate_responses(input_data, output_file, task, request_api, start_id=0, max_tokens=500):
    task_description = task_info[task]["description"]
    example_request_and_response = task_info[task]["example_request_and_response"] if "example_request_and_response" in task_info[task] else ""
    example_user_attribute_group = task_info[task]["example_user_attribute_group"] if "example_user_attribute_group" in task_info[task] else ""
    answer_note = task_info[task]["answer_note"] if "answer_note" in task_info[task] else ""
    additional_output = task_info[task]["additional_output"] if "additional_output" in task_info[task] else ""
    count = 0
    with open(output_file, "a", encoding='utf-8') as outfile:
        for i, request_item in enumerate(input_data):
            requests = request_item["requests"]
            user_attribute_group = request_item["user_attr_group"]
            for j, request in enumerate(requests):
                if count < start_id:
                    count += 1
                    continue
                count += 1
                prompt = prompt_template.format(task=task, task_description=task_description, request=request, example_user_attribute_group=example_user_attribute_group, example_request_and_response=example_request_and_response,
                user_attribute_group=user_attribute_group,
                answer_note=answer_note,
                additional_output=additional_output)
                output = request_api(prompt, max_tokens=max_tokens)
                output_dict = {"task": task, 
                               "task_index":request_item["task_index"], 
                               "domain_index":request_item["domain_index"], 
                               "subject_index": request_item["subject_index"],
                               "request_index": j,
                               "domain": request_item["domain"], 
                               "subject": request_item["subject"], 
                               "user_attr_group": user_attribute_group,
                               "request": request,
                               "output": output}
                json.dump(output_dict, outfile, ensure_ascii=False)
                outfile.write("\n")
                print(f"\n\n=========================={i}-{j}==============================")
                print(prompt)
                print("[-------------------------------Below is the generated answers--------------------------------]")
                print(output)

if __name__ == "__main__":
    import argparse
    from model_api.gpt4 import request_gpt4o
    request_api = request_gpt4o
    parser = argparse.ArgumentParser(description="Generate responses using GPT-4.")
    parser.add_argument("--task", type=str, default="decision", help="Task type", choices=['recommend', 'rank', 'filter', 'predict', 'preference_infer', 'intention_infer', 'risk_detect', 'advice', 'decision', 'convince'])
    args = parser.parse_args()
    task = args.task
    input_file = f"testset/output/{task}/question/user_request_extracted.jsonl"
    output_file = f"testset/output/{task}/question/GT.jsonl"
    start_id = resume_from_generated(output_file)
    # create path if not exist
    if not os.path.exists(os.path.dirname(output_file)):
        os.makedirs(os.path.dirname(output_file))
    input_data = load_items(input_file)
    generate_responses(input_data, output_file, task, request_api, start_id=start_id, max_tokens=500)