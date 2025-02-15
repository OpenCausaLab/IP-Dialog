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
input_token = 0
prompt_template = """You are a request-generation engine. Your mission is to generate 3 requests on subject: {domain}-{subject}. These requests are for the task: {task}. The task requires an agent to {task_description}
The agent will leverage the user's attributes to answer the request in a personalized way. 
---Important Note---
- You should generate requests in a first-person tone.
- Make your generated requests type as diverse as possible. Avoid generating similar requests.
- Do not mention words such as best fit my unique profile, or any other hints about attributes.
- {task_specific_note}
- Output your generated requests in the format of:
Output requests: 
- request 1 [Answer: ...]
- request 2 [Answer: ...]
- ...
---Example Requests---
Suppose you are asked to generate request on subject: {example_domain}-{example_subject},
User Attributes: {example_user_attribute_group}
Output requests: 
{example_requests}
---Your Generated Requests---
Now list your generated requests on subject: {domain}-{subject}
User Attributes:
{user_attribute_group}
Output requests: """

user_attr_count = 0
def get_user_attr(user_attr_group):
    global user_attr_count
    user_attr = user_attr_group[user_attr_count]
    user_attr_count += 1
    assert user_attr_count < len(user_attr_group)
    return user_attr


def generate_responses(input_data, output_file, task, request_api, start_id=0, max_tokens=500):
    task_description = task_info[task]["description"]
    example_domain = task_info[task]["example_domain"]
    example_subject = task_info[task]["example_subject"]
    example_requests = task_info[task]["example_requests"]
    example_user_attribute_group = task_info[task]["example_user_attribute_group"] if "example_user_attribute_group" in task_info[task] else ""
    count = 0
    with open(output_file, "a", encoding='utf-8') as outfile:
        for i, domain_item in enumerate(input_data):
            domain = domain_item["domain"]
            for j, subject in enumerate(domain_item["subjects"]):
                for k in range(3):
                    idx = count
                    if idx < start_id:
                        count += 1
                        continue
                    count += 1
                    user_attr_group = get_user_attr(user_attrs)
                    if task_info[task]["mention_attr"]:
                        user_attr_group_str = user_attr_group
                    else:
                        user_attr_group_str = "age, income_level, profession, openness, conscientiousness, extraversion, agreeableness, neuroticism, residence(urban/rural),gender,health(healthy/minor_issue/disabled),hobby"
                    if "task_specific_note" in task_info[task] and task_info[task]["task_specific_note"]:
                        task_specific_note = task_info[task]["task_specific_note"]
                    else:
                        task_specific_note = ""
                    prompt = prompt_template.format(domain=domain, subject=subject, task=task, task_description=task_description, example_domain=example_domain, example_subject=example_subject, example_requests=example_requests,
                    user_attribute_group=user_attr_group_str,
                    task_specific_note=task_specific_note,
                    example_user_attribute_group=example_user_attribute_group)
                    output = request_api(prompt, max_tokens=max_tokens)
                    output_dict = {"task": task, "task_index":i, "domain_index":j, "subject_index": k, "domain": domain, "subject": subject, "user_attr_group": user_attr_group, "output": output}
                    json.dump(output_dict, outfile, ensure_ascii=False)
                    outfile.write("\n")
                    print(f"\n\n=========================={i}-{domain}, {j}-{subject}, No.{k}==============================")
                    print(prompt)
                    print("[-------------------------------Below is the generated requests--------------------------------]")
                    print(output)

if __name__ == "__main__":
    import argparse
    from model_api.gpt4 import request_gpt4o
    request_api = request_gpt4o
    parser = argparse.ArgumentParser(description="Generate responses using GPT-4.")
    parser.add_argument("--task", type=str, default="decision", help="Task type", choices=['recommend', 'rank', 'filter', 'predict', 'preference_infer', 'intention_infer', 'advice', 'decision', 'convince'])
    args = parser.parse_args()
    task = args.task
    input_file = f"testset/output/{task}/question/subjects_extracted.jsonl"
    output_file = f"testset/output/{task}/question/user_request.jsonl"
    start_id = resume_from_generated(output_file)
    # create path if not exist
    if not os.path.exists(os.path.dirname(output_file)):
        os.makedirs(os.path.dirname(output_file))
    input_data = load_items(input_file)
    generate_responses(input_data, output_file, task, request_api, start_id=start_id, max_tokens=500)