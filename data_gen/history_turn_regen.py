import random
import sys
import os
import json
import re
current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(current_dir)
print(current_dir)
from utils import load_items, resume_from_generated

def concat_dialogues(input, turn_id):
    dialogues = ""
    for i in range(turn_id):
        if f"model_history_t{i}"=="":
            continue
        dialogues += input[f"dialogue_t{i}"]["dialogue"] + "\n"
    return dialogues

def get_generation_prompt(item, turn_id):
    assert turn_id >= 0 and turn_id != None
    attr_key, attr_value = list(item['GT']['related_attributes'].items())[turn_id]
    if turn_id == 0:
        prompt = f"""Generate a single-round dialogue between a user and AI to implicitly reflect the following user attribute:

{attr_key}: {attr_value}

Guidelines:
1. Do not explicitly mention the user attributes.
2. The generated dialogue should implicitly reflect the user's attribute, allowing it to be inferred from the context.
3. Ensure the dialogue remains natural, as if between a user and an AI assistant.

Format the dialogue strictly as follows:

User: [Brief user message that implicitly reflects the given attribute]
AI: [Brief AI response that naturally respond to the user's message without referencing the user's attributes]
"""
        return prompt
    else:
        previous_dialogue = concat_dialogues(item, turn_id)
        prompt = f"""Based on the following dialogue:

{previous_dialogue}
Continue the dialogue for one more round. The continued single-round dialogue should be between a user and AI to implicitly reflect the following user attribute:

{attr_key}: {attr_value}

Guidelines:
1. Do not explicitly mention the user attributes.
2. The generated dialogue should implicitly reflect the user's attribute, allowing it to be inferred from the context.
3. Ensure the dialogue remains natural, as if between a user and an AI assistant.

Format the dialogue strictly as follows:

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
            if input["generation_finished"] == "yes" or input[f"dialogue_t{turn_id}"]["check_extracted"]["pass_exam"] == "yes":
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
    parser.add_argument("--task", type=str, default="decision", help="Task type", choices=['recommend', 'rank', 'filter', 'predict', 'preference_infer', 'intention_infer', 'risk_detect', 'advice', 'decision', 'convince','total_task','random_subset_1000'])
    parser.add_argument("--turn_id", type=int, required=True, help="Turn ID")
    parser.add_argument("--iter_id", type=int, required=True, help="Iteration ID")
    args = parser.parse_args()
    task = args.task

    input_dir = f"testset/output/{task}/history/turn_{args.turn_id}/dialogue_i-{args.iter_id-1}_examed_extracted.jsonl"
    output_dir = f"testset/output/{task}/history/turn_{args.turn_id}/dialogue_i-{args.iter_id}.jsonl"
    inputs = load_items(input_dir)

    start_id = resume_from_generated(output_dir)
    generate_histories(inputs, output_dir, args.turn_id, request_api, start_id=start_id, max_tokens=500)