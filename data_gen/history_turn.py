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
        for i, input in tqdm(enumerate(inputs)):
            idx = i
            if idx < start_id:
                continue
            output_data = input.copy()
            if (len(input['GT']['related_attributes']) < turn_id+1) or ("remove" in input and input["remove"] == "yes"):
                output_data["generation_finished"] = "yes"
            else:
                output_data["generation_finished"] = "no"
                print(f"\n################Processing set {idx}###################")
                prompt = get_generation_prompt(input, turn_id)
                model_answer = request_api(prompt, max_tokens=max_tokens)
                print("[Prompt]:", prompt)
                print("[Model Response]:", model_answer)
                output_data[f"dialogue_t{turn_id}"] = {"attr": list(input['GT']['related_attributes'].items())[turn_id],
                            "output": model_answer,
                            "check_extracted": {"round": -1, "pass_exam": "no"}
                        }
            json.dump(output_data, outfile, ensure_ascii=False)
            outfile.write('\n')
            outfile.flush()
            # print("\n" + "="*50)

if __name__ == "__main__":
    import argparse
    from model_api.gpt4 import request_gpt4o
    request_api = request_gpt4o
    parser = argparse.ArgumentParser(description="Generate responses using GPT-4.")
    parser.add_argument("--task", type=str, default="decision", help="Task type", choices=['recommend', 'rank', 'filter', 'predict', 'preference_infer', 'intention_infer', 'risk_detect', 'advice', 'decision', 'convince','total_task','random_subset_1000'])
    parser.add_argument("--turn_id", type=int, required=True, help="Turn ID")
    parser.add_argument("--input_dir", type=str, default=None, help="input_dir")
    args = parser.parse_args()
    task = args.task

    if args.turn_id == 0:
        input_dir = f"testset/output/total_task/GT_attr.jsonl"
        assert args.input_dir is None or args.input_dir == input_dir
    else:
        assert args.input_dir is not None
        input_dir = args.input_dir
        assert input_dir.startswith(f"testset/output/{task}/history/turn_{args.turn_id-1}/dialogue_i-"), f"testset/output/{task}/history/turn_{args.turn_id-1}/dialogue_i-"
    output_dir = f"testset/output/{task}/history/turn_{args.turn_id}/dialogue_i-0.jsonl"
    inputs = load_items(input_dir)

    start_id = resume_from_generated(output_dir)
    generate_histories(inputs, output_dir, args.turn_id, request_api, start_id=start_id, max_tokens=500)