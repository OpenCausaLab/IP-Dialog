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
from evaluate_models.get_eval_format import ans_format
    
def compute_metrics(gt_dict, predict_dict, task, gt_attrs=None):
    # attribute
    gt_attrs = gt_dict["related_attributes"] if gt_attrs is None else gt_attrs
    attribute_correct_part = set(gt_attrs.keys()) & set(predict_dict["related_attributes"].keys())
    total_attr_num = len(gt_attrs)
    predict_values = set(predict_dict["related_attributes"].values())
    gt_values = set(gt_attrs.values())
    value_correct_part = predict_values & gt_values
    attribute_item_acc = len(attribute_correct_part) / total_attr_num
    value_item_acc = len(value_correct_part) / total_attr_num
    attribute_item_hit_rate = len(attribute_correct_part) / len(predict_dict["related_attributes"]) if len(predict_dict["related_attributes"]) > 0 else 0
    value_item_hit_rate = len(value_correct_part) / len(predict_values) if len(predict_values) > 0 else 0
    # accuracy
    if task in ["decision", "predict"]:
        answer_acc = 1 if gt_dict["answer"] == predict_dict["answer"] else 0
    elif task in ["filter","preference_infer"]:
        answer_acc = len(set(gt_dict["answer"]) & set(predict_dict["answer"]))/len(set(gt_dict["answer"]))
    elif task in ["rank"]:
        gt_list = [ord(x) for x in gt_dict["answer"]]
        predict_list = [ord(x) for x in predict_dict["answer"]]
        # answer_acc = 1 if gt_dict["answer"] == predict_dict["answer"] else 0
        if len(gt_list) != len(predict_list):
            answer_acc = 0
        else:
            tau, _ = kendalltau(gt_list, predict_list)
            answer_acc = (tau + 1) / 2
    elif task in ["risk_detect", "intention_infer", "advice", "recommend", "convince"]:
        answer_acc = 0
    else:
        raise ValueError(f"Task {task} not found.")
    
    return {
        "attribute_acc": attribute_item_acc,
        "value_acc": value_item_acc,
        "attribute_hit_rate": attribute_item_hit_rate,
        "value_hit_rate": value_item_hit_rate,
        "answer_acc": answer_acc
    }
def print_task_metrics(metrics_result, metrics_result_tasks):
    print("Overall Metrics:", metrics_result)
    print("Task Metrics:")
    for task, metrics in metrics_result_tasks.items():
        print(f"Task: {task}", metrics)
def diaglogue_to_text(dialogue):
    return '\n'.join([f"{item['speaker']}: {item['content']}" for item in dialogue])

def get_gpt4o_eval_prompt(gt, predict):
    task = gt["task"]
    predict_answer = extract_answer(predict["Answer"], task, verbose=False)
    gt_attrs = gt["GT"]["related_attributes"]
    predict_analysis = predict["Analysis"]
    gt_attrs = gt["GT"]["related_attributes"]
    predict_analysis = predict["Analysis"]
    prompt = f'''Suppose you are a user with the following attributes: {gt_attrs}. Your request is: {gt['request']}. Now evaluate the following analysis and answers to your request:
Agent Analysis: {predict_analysis}
Agent Answer: {predict_answer}

Evaluation Standard:
Conciseness (0-1 points): Answers should be concise and to the point.
Personalization (0-4 points): Does the analysis and answer specifically address the user's request and attributes?
Analysis Quality (0-4 points): Is the analysis logical, coherent, and well-reasoned? Here's an example of a good analysis: {gt['GT']['analysis']}. 
Answer Accuracy (0-5 points): Does the answer correctly address the request? Ground Truth Answer: {gt['GT']['answer']}.
Total Score: Sum of all categories (0-14 points)

Output your score in the following format:
[Conciseness: score, Personalization: score, Analysis Quality: score, Answer Accuracy: score]
[Total: score]
For example:
[Conciseness: 1, Personalization: 4, Analysis Quality: 4, Answer Accuracy: 5]
[Total: 14]

Your Output:
'''
    return prompt

def gpt4o_eval(inputs, gts, output_dir, request_api, start_id, test=False, itern=10):
    with open(output_dir, 'a', encoding='utf-8') as outfile:
        metrics_result = {}
        metrics_result_tasks = {}
        for i, input in tqdm(enumerate(inputs)):
            idx = i
            if idx < start_id*itern:
                continue
            if idx % itern != 0:
                continue
            gt = gts[i]
            task = gt["task"]
            # assert ("index" in input) or (f"Answer: [{gt['GT']['answer']}]"[-5:] == input['label'][-5:]), input['label'][-5:] + '\n' + f"Answer: [{gt['GT']['answer']}]"
            assert ("index" not in input) or (gt["index"] == input["index"])
            assert len(set(gt["GT"]["answer"])) > 0, f"GT answer is empty: {gt['GT']['analysis']}"
            model_response = input["predict"]
            predict = extract(model_response, verbose=False)
            if test:
                if "Answer" not in predict:
                    print("Warning:", f"Answer not found in predict: {model_response}")
            # assert "Answer" in predict, f"Answer not found in predict: {model_response}"
            for key in ["Answer", "Analysis"]:
                if key not in predict:
                    predict[key] = ""
                    print("Warning:", f"{key} not found in predict: {model_response}")
            predict_answer = extract_answer(predict["Answer"], task, verbose=False)
            user_history = "\n".join(diaglogue_to_text(gt["history"][i]) for i in range(len(gt["history"])))
            gt_attrs = gt["GT"]["related_attributes"]
            # predict_attributes = extract_attributes(predict["Attributes"], verbose=False)
            predict_analysis = predict["Analysis"]

            #########get prompt and eval
            prompt = get_gpt4o_eval_prompt(gt, predict)
            if not test:
                print(f"############################{i}#########################")
                output = request_api(prompt, max_tokens=500)
                print(prompt)
                print(output)
            
                ########get prompt and eval
                output_dict = input.copy()
                output_dict.update({
                    "index": gt["index"],
                    "task": task,
                    "predict_extracted": {"analysis": predict_analysis,
                                        "answer": predict_answer
                                        },
                    "gpt4o_eval": output
                })
                json.dump(output_dict, outfile, ensure_ascii=False)
                outfile.write('\n')
                outfile.flush()

if __name__ == "__main__":
    import argparse

    models = ["gpto1_mini", "gpt4o", "claude", "qwen", "llama3-1", "llama3_1_70b"]
    parser = argparse.ArgumentParser(description="Generate responses using GPT-4.")
    parser.add_argument("--input_dir", type=str, default=None, help="input_dir")
    parser.add_argument("--gt_dir", type=str, default="benchmark/filtered_data_test_1000.jsonl", help="gt_dir")
    parser.add_argument("--GT_key", type=str, default="GT", help="GT key")
    parser.add_argument("--attr_key", type=str, default=None, help="attribute key")
    parser.add_argument("--test", action="store_true", help="test")
    parser.add_argument("--api_index", type=int)


            # GT_key = "GT_gpt4o_2" # GT or "GT_gpt4o_2"
        # attr_key = None  # None or "duplicate_attrs"
    args = parser.parse_args()
    # if args.api_index == 0:
    from model_api.gpt4 import request_gpt4o
    request_api = request_gpt4o
    # elif args.api_index == 1:
    #     from model_api.gpt4_term import request_gpt4o_term
    #     request_api = request_gpt4o_term
    # elif args.api_index == 2:
    #     from model_api.gpt4_term2 import request_gpt4o_term
    #     request_api = request_gpt4o_term
    # elif args.api_index == 3:
    #     from model_api.gpt4_term3 import request_gpt4o_term
    #     request_api = request_gpt4o_term
    # else:
    #     raise ValueError(f"api_index {args.api_index} not found.")

    input_dir = args.input_dir
    if "/" in input_dir and args.gt_dir == "benchmark\\filtered_data_test_1000.jsonl":
        gt_dir = "benchmark/filtered_data_test_1000.jsonl"
    else:
        gt_dir = args.gt_dir
    file_name = os.path.splitext(args.input_dir)[0]
    if "\\" in file_name:
        file_name = file_name.split("\\")[-1]
    elif "/" in file_name:
        file_name = file_name.split("/")[-1]
    assert file_name in models, f"Model {file_name} not found in {models}" # TODO: extract ensure
    file_half_path = input_dir.split("output")[-1][1:]
    assert file_half_path.startswith("alpaca"), f"Invalid input_dir: {file_half_path}"
    
    print(file_half_path)
    if "\\" in input_dir:
        output_dir = os.path.join("evaluate_models\\output_metrics\\gpt4o_eval_new\\", file_half_path)
    elif "/" in input_dir:
        output_dir = os.path.join("evaluate_models/output_metrics/gpt4o_eval_new/", file_half_path)
    print(output_dir)
    inputs = load_items(input_dir)
    assert len(inputs) == 1000
    assert gt_dir is not None, f"GT not found: {gt_dir}"
    gts = load_items(gt_dir)
    start_id = resume_from_generated(output_dir)
    gpt4o_eval(inputs, gts, output_dir, request_api, start_id=start_id,test=args.test, itern=10)