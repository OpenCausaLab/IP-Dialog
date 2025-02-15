import random
import sys
import os
import json
import re
current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(current_dir)
print(current_dir)
from utils import load_items, resume_from_generated
from data_gen.question_answer_extract import extract, extract_answer, extract_attributes
from tqdm import tqdm
from scipy.stats import kendalltau
global success
success = 0
def extract_scores(text, file_dir, pred):
    bracket_content = re.findall(r'\[(.*?)\]', text)
    
    scores = {}
    for content in bracket_content:
        if 'Total' in content:
            total = re.search(r'Total:\s*(\d+)', content)
            if total:
                scores['Total'] = int(total.group(1))
        else:
            items = re.findall(r'([^,]+):\s*(\d+)', content)
            scores.update({item.strip(): int(score) for item, score in items})
    if 'Total' not in scores:
        print(f"Error: {file_dir}, {pred}")
    if len(scores) != 5:
        print(f"Error: {file_dir}, {pred}")
    
    return scores

def eval(inputs, file_dir):
        result_scores = {}
        assert len(inputs) == 100, f"Error: {len(inputs)}\n"
        for i, input in enumerate(inputs):
            task = input["task"]
            eval_str = input["gpt4o_eval"]
            scores = extract_scores(eval_str, file_dir, input["predict"])
            if task not in result_scores:
                result_scores[task] = {}
            for key, value in scores.items():
                if key not in result_scores[task]:
                    result_scores[task][key] = 0.
                result_scores[task][key] += value
        for task in result_scores:
            for key in result_scores[task]:
                result_scores[task][key] /= 10
        
        return result_scores

if __name__ == "__main__":
    import argparse
    from model_api.gpt4 import request_gpt4o
    request_api = request_gpt4o
    models = ["gpto1_mini", "gpt4o", "claude", "llama3-1", "qwen", "llama3_1_70b"]
    datasets = ["alpaca_hq_basic_1000", "alpaca_hq_cot1_1000", "alpaca_hq_cot2_1000", "alpaca_hq_cot3_1000", "alpaca_hq_cot4_1000"]
    parser = argparse.ArgumentParser(description="Generate responses using GPT-4.")
    gts = load_items("benchmark/filtered_data_test_1000.jsonl")
    output_dir = "evaluate_models/output_metrics/gpt4o_eval_new.json"
    results_dict = {}
    for file_name in datasets:
        prompt_type = file_name[len("alpaca_"):-len("_1000")]
        results_dict[file_name] = {}
        for model in models:
            input_dir = os.path.join(f"evaluate_models/output_metrics/gpt4o_eval_new/{file_name}", f"{model}.jsonl")
            # if path exists, load
            if not os.path.exists(input_dir):
                print(f"File not found: {input_dir}")
                continue
            inputs = load_items(input_dir)
            if len(inputs) != 100:
                print(f"Not 50 file: {input_dir}")
            #     continue
            # print(input_dir)
            output_dict = eval(inputs, input_dir)
            # print("success")
            results_dict[file_name][model] = output_dict
    
    # save
    with open(output_dir, 'w', encoding='utf-8') as outfile:
        json.dump(results_dict, outfile, ensure_ascii=False)