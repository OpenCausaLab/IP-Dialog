import random
import sys
import os
import json
import re
current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(current_dir)
print(current_dir)
from utils import load_items, resume_from_generated

def get_generation_prompt(item, turn_id):
    assert turn_id >= 0 and turn_id != None
    attr_key, attr_value = list(item['GT']['related_attributes'].items())[turn_id]
    dialogue = item[f"dialogue_t{turn_id}"]["dialogue"]
    prompt = f"""Given the following dialogue:
{dialogue}

Modify this dialogue to make the user message implicitly reflect the following user attribute:

{attr_key}: {attr_value}

Guidelines:
1. Do not explicitly mention the user attribute.
2. The user message should implicitly reflect the given attribute, allowing it to be inferred from the context.
3. Maintain a natural, single-round dialogue between a user and an AI assistant.

Format the modified dialogue strictly as follows:

User: [Brief user message that implicitly reflects the given attribute]
AI: [Brief AI response that naturally respond to the user's message without referencing the user's attributes]
"""
    return prompt

def generate_histories(inputs, output_file, turn_id, request_api, start_id=0, max_tokens=500):
    with open(output_file, 'a', encoding='utf-8') as outfile:
        for i, input in enumerate(inputs):
            idx = i
            if idx < start_id:
                continue
            output_data = input.copy()
            if  input["generation_finished"] == "yes" or input[f"dialogue_t{turn_id}"]["check_extracted"]["pass_exam"] == "yes":
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

    input_dir = f"testset/output/{task}/history/turn_{args.turn_id}/dialogue_i-{args.iter_id-1}_examed_extracted.jsonl"
    output_dir = f"testset/output/{task}/history/turn_{args.turn_id}/dialogue_i-{args.iter_id}.jsonl"
    inputs = load_items(input_dir)

    start_id = resume_from_generated(output_dir)
    generate_histories(inputs, output_dir, args.turn_id, request_api, start_id=start_id, max_tokens=500)