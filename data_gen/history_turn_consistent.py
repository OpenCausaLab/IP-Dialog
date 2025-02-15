import random
import sys
import os
import json
import re
current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(current_dir)
print(current_dir)
from utils import load_items, resume_from_generated
from tqdm import tqdm

def get_generation_prompt(item, turn_id):
    dialogue = item[f"dialogue_t{turn_id}"]["dialogue"]
    attr_key, attr_value = item[f"dialogue_t{turn_id}"]["attr"]
    full_attr = item['GT']['related_attributes']
    prompt = f"""Examine the following dialogue:
{dialogue}

Is this dialogue consistent with the following user attribute(s)?
{str(full_attr)}
Consistency definition: The dialogue content does not contradict any of the listed user attribute(s).
answer yes or no only.
Answer (yes/no): 
"""
    return prompt

def generate_histories(inputs, output_file, turn_id, request_api, start_id=0, max_tokens=500):
    with open(output_file, 'a', encoding='utf-8') as outfile:
        for i, input in tqdm(enumerate(inputs)):
            idx = i
            if idx < start_id:
                continue

            output_data = input.copy()
            if input["generation_finished"] == "yes" or \
                (f"consistent_t{turn_id}" in input[f"dialogue_t{turn_id}"] and \
                 input[f"dialogue_t{turn_id}"][f"consistent_t{turn_id}"] == "yes"):
                pass
            else:
                print(f"\n################Processing set {idx}###################")
                prompt = get_generation_prompt(input, turn_id)
                model_answer = request_api(prompt, max_tokens=max_tokens)
                print("[Prompt]:", prompt)
                print("[Model Response]:", model_answer)
                output_data[f"dialogue_t{turn_id}"]["output"] = model_answer
            json.dump(output_data, outfile, ensure_ascii=False)
            outfile.write('\n')
            outfile.flush()

if __name__ == "__main__":
    import argparse
    from model_api.gpt4 import request_gpt4o
    request_api = request_gpt4o
    parser = argparse.ArgumentParser(description="Generate responses using GPT-4.")
    parser.add_argument("--task", type=str, default="decision", help="Task type", choices=['recommend', 'rank', 'filter', 'predict', 'preference_infer', 'intention_infer', 'risk_detect', 'advice', 'decision', 'convince', 'total_task','random_subset_1000'])
    parser.add_argument("--turn_id", type=int, required=True, help="Turn ID")
    parser.add_argument("--iter_id", type=int, required=True, help="Iteration ID")
    args = parser.parse_args()
    task = args.task

    input_dir = f"testset/output/{task}/history/turn_{args.turn_id}/dialogue_i-{args.iter_id}_examed_extracted.jsonl"
    output_dir = f"testset/output/{task}/history/turn_{args.turn_id}/dialogue_i-{args.iter_id}_consistent.jsonl"
    inputs = load_items(input_dir)

    start_id = resume_from_generated(output_dir)
    generate_histories(inputs, output_dir, args.turn_id, request_api, start_id=start_id, max_tokens=500)