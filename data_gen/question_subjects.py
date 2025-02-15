import random
import sys
import os
import json
import re
current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print(current_dir)
sys.path.append(current_dir)
from attributes_tasks_domains import task_info
from utils import resume_from_generated

prompt_template = """Generate 10 subjects on domain: {domain}. These subjects are for the task: {task}. The task requires agent to {task_description}
The agent will leverage the user's attributes to answer the request related to the subject in a personalized way. The user's attributes includes:
age, income_level, profession, openness, conscientiousness, extraversion, agreeableness, neuroticism, residence(urban/rural),gender,health(healthy/minor_issue/disabled),hobby
---Important Note---
- Make your generated subject as diverse as possible. To cover as much as possible, with the greatest possible differences between categories.
- Subject should be applicable to all user attributes, and the subject should not include any hints about attributes.
- The length of the subject should be less than 5 words.
- Output your generated subjects in the format of:
Output subjects: 
- subject 1
- subject 2
- ...
---Example Subject---
Suppose you are asked to generate subject on domain: {example_domain},
Output subjects: 
{example_subjects}
---Your Generated Subject---
Now list your generated subject on domain: {domain}
Output subjects: """

def generate_responses(output_file, task, request_api, start_id=0, max_tokens=500):
    with open(output_file, "a", encoding='utf-8') as outfile:
        for i, domain in enumerate(task_info[task]["domains"]):
            idx = i
            if idx < start_id:
                continue
            task_description = task_info[task]["description"]
            example_domain = task_info[task]["example_domain"]
            example_subjects = task_info[task]["example_subjects"]
            prompt = prompt_template.format(domain=domain, task=task, task_description=task_description, example_domain=example_domain, example_subjects=example_subjects)
            output = request_api(prompt, max_tokens=max_tokens)
            output_dict = {"task": task, "task_index":i, "domain": domain, "output": output}
            json.dump(output_dict, outfile, ensure_ascii=False)
            outfile.write("\n")
            print(f"=============================={domain}==============================")
            print(prompt)
            print("                   Below is the generated subjects                   ")
            print(output)
    
if __name__ == "__main__":
    import argparse
    from model_api.gpt4 import request_gpt4o
    request_api = request_gpt4o
    parser = argparse.ArgumentParser(description="Generate responses using GPT-4.")
    parser.add_argument("--task", type=str, default="decision", help="Task type", choices=['recommend', 'rank', 'filter', 'predict', 'preference_infer', 'intention_infer', 'advice', 'decision', 'convince'])
    args = parser.parse_args()
    task = args.task
    output_file = f"testset/output/{task}/question/subjects.jsonl"
    start_id = resume_from_generated(output_file)
    # create path if not exist
    if not os.path.exists(os.path.dirname(output_file)):
        os.makedirs(os.path.dirname(output_file))
    generate_responses(output_file, task, request_api, start_id=start_id,max_tokens=500)