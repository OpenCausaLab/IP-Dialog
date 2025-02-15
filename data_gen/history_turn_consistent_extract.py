import random
import sys
import os
import json
import re
current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(current_dir)
print(current_dir)
from utils import load_items, resume_from_generated

def extract_answer(input_text):
    input_text = input_text.lower()
    if input_text.startswith(("yes", "[answer]: yes", "answer (yes/no): yes", "answer (yes)", "answer: yes")):
        answer = "yes"
    elif ("yes" in input_text) and ("no" not in input_text):
        answer = "yes"
    elif input_text.startswith(("no", "[answer]: no", "answer (yes/no): no", "answer (no)", "answer: no")):
        answer = "no"
    elif ("no" in input_text) and ("yes" not in input_text):
        answer = "no"
    else:
        raise ValueError(f"Error: The answer should be 'yes' or 'no'. \n Answer: {input_text}")
    return answer

def generate_histories(inputs, output_file, turn_id, max_tokens=500):
    passed = 0
    remove_total_count = 0
    total = 0
    with open(output_file, 'w', encoding='utf-8') as outfile:
        for i, input in enumerate(inputs):

            output_data = input.copy()
            total += input["GT"]["count"] if "count" in input["GT"] else 1
            if input["generation_finished"] == "yes":
                passed += 1
                pass
                
            else:
                model_response = input[f"dialogue_t{turn_id}"]["output"]
                answer = extract_answer(model_response)
                output_data[f"dialogue_t{turn_id}"][f"consistent_t{turn_id}"] = answer
                output_data[f"dialogue_t{turn_id}"].pop("output")
                if answer == "yes":
                    passed += 1
                else:
                    output_data["remove"] = "yes"
                    remove_total_count += input["GT"]["count"] if "count" in input["GT"] else 1
                if input[f"dialogue_t{turn_id}"]["check_extracted"]["pass_exam"] == "no" and answer == "yes":
                    output_data["remove"] = "yes"
                    remove_total_count += input["GT"]["count"] if "count" in input["GT"] else 1
                    passed -= 1
            json.dump(output_data, outfile, ensure_ascii=False)
            outfile.write('\n')
            outfile.flush()
    print(f"Consistent: {passed}/{len(inputs)}", f"Removed Total: {remove_total_count}/{total}", "Removed: ", len(inputs)-passed)

if __name__ == "__main__":
    import argparse
    # from model_api.gpt4 import request_gpt4o
    # request_api = request_gpt4o
    parser = argparse.ArgumentParser(description="Generate responses using GPT-4.")
    parser.add_argument("--task", type=str, default="decision", help="Task type", choices=['recommend', 'rank', 'filter', 'predict', 'preference_infer', 'intention_infer', 'risk_detect', 'advice', 'decision', 'convince', 'total_task','random_subset_1000'])
    parser.add_argument("--turn_id", type=int, required=True, help="Turn ID")
    parser.add_argument("--iter_id", type=int, required=True, help="Iteration ID")
    args = parser.parse_args()
    task = args.task

    input_dir = f"testset/output/{task}/history/turn_{args.turn_id}/dialogue_i-{args.iter_id}_consistent.jsonl"
    output_dir = f"testset/output/{task}/history/turn_{args.turn_id}/dialogue_i-{args.iter_id}_consistent_extracted.jsonl"
    inputs = load_items(input_dir)

    # start_id = resume_from_generated(output_dir)
    generate_histories(inputs, output_dir, args.turn_id, max_tokens=500)