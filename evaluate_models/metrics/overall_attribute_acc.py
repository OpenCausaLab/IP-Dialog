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
import json
import re
import os
# from bert_score import BERTScorer
from nltk.translate import bleu_score, meteor_score
from nltk import word_tokenize
import nltk
from rouge_score import rouge_scorer

nltk.download('punkt')
nltk.download('wordnet')

def calculate_bleu_score(gt_analysis_and_answer, pred_analysis_and_answer, n_gram=1):
    refs = [word_tokenize(gt_analysis_and_answer)]
    cand = word_tokenize(pred_analysis_and_answer)
    
    score = bleu_score.sentence_bleu(refs, cand, weights=[1/n_gram]*n_gram)
    
    return score

def calculate_meteor_score(gt_analysis_and_answer, pred_analysis_and_answer):
    refs = [word_tokenize(gt_analysis_and_answer)]
    cand = word_tokenize(pred_analysis_and_answer)
    
    score = meteor_score.meteor_score(refs, cand)
    
    return score

def calculate_rouge_score(gt_analysis_and_answer, pred_analysis_and_answer):
    """Calculate ROUGE-1 and ROUGE-L score.

    Args:
        gt_analysis_and_answer (str): ground truth
        pred_analysis_and_answer (str): prediction

    Returns:
        tuple: ROUGE-1 score, ROUGE-L score
    """    
    
    scorer = rouge_scorer.RougeScorer(['rouge1', 'rougeL'], use_stemmer=True)
    
    scores = scorer.score(gt_analysis_and_answer, pred_analysis_and_answer)
    
    return scores['rouge1'].fmeasure, scores['rougeL'].fmeasure

def calculate_answer_f1_score(gt_set, pred_set):
    true_positives = len(gt_set & pred_set)
    false_positives = len(pred_set - gt_set)
    false_negatives = len(gt_set - pred_set)
    
    precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
    recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
    
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    
    return f1, precision, recall

def compute_attribute_metrics(gt_dict, predict_dict, task, gt_attrs):
    def f1_score(gt_set, pred_set):
        true_positives = len(gt_set & pred_set)
        false_positives = len(pred_set - gt_set)
        false_negatives = len(gt_set - pred_set)
        precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
        recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        return f1, precision, recall
    # attribute f1
    attribute_f1, attribute_precision, attribute_recall = f1_score(set(gt_attrs.keys()), set(predict_dict["related_attributes"].keys()))
    # value f1 and precision and recall
    predict_values = [key+":"+value for key, value in predict_dict["related_attributes"].items()]
    gt_values = [key+":"+value for key, value in gt_attrs.items()]
    value_f1, value_precision, value_recall = f1_score(set(gt_values), set(predict_values))
    # relative value acc
    relative_value_acc1 = round(value_precision / attribute_precision, 2) if attribute_precision > 0 else 0
    relative_value_acc2 = round(value_recall / attribute_recall, 2) if attribute_recall > 0 else 0
    assert relative_value_acc1 == relative_value_acc2, f"relative_value_acc1: {relative_value_acc1}, relative_value_acc2: {relative_value_acc2}"
    relative_value_acc = relative_value_acc1

    return {
        "attribute_f1": attribute_f1,
        "value_f1": value_f1,
        "relative_value_acc": relative_value_acc,
    }

def compute_metrics(gt_dict, predict_dict, task, gt_attrs):
    # attribute
    attribute_metrics = compute_attribute_metrics(gt_dict, predict_dict, task, gt_attrs)
    # accuracy
    if task in ["decision", "predict"]:
        answer_acc = 1 if gt_dict["answer"] == predict_dict["answer"] else 0
    elif task in ["filter","preference_infer"]:
        f1, precision, recall = calculate_answer_f1_score(set(gt_dict["answer"]), set(predict_dict["answer"]))
        # answer_acc = len(set(gt_dict["answer"]) & set(predict_dict["answer"]))/len(set(gt_dict["answer"]))
        answer_acc = f1
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
        # answer_acc = None
        # bleu, rouge, meteor
        pred_analysis_and_answer = f"{predict_dict['analysis']} {predict_dict['answer']}"
        gt_analysis_and_answer = f"{gt_dict['analysis']} {gt_dict['answer']}"
        # pred_analysis_and_answer = f"{predict_dict['analysis']}"
        # gt_analysis_and_answer = f"{gt_dict['analysis']}"
        # bleu_1_score = calculate_bleu_score(gt_analysis_and_answer, pred_analysis_and_answer, n_gram=1)
        # bleu_2_score = calculate_bleu_score(gt_analysis_and_answer, pred_analysis_and_answer, n_gram=2)
        meteor_score = calculate_meteor_score(gt_analysis_and_answer, pred_analysis_and_answer)
        # rouge_1_score, rouge_L_score = calculate_rouge_score(gt_analysis_and_answer, pred_analysis_and_answer)
        answer_acc = meteor_score
    else:
        raise ValueError(f"Task {task} not found.")
    
    return_dict = {"answer_acc": answer_acc}
    return_dict.update(attribute_metrics)

    return return_dict

def print_task_metrics(metrics_result, metrics_result_tasks):
    print("Overall Metrics:", metrics_result)
    print("Task Metrics:")
    for task, metrics in metrics_result_tasks.items():
        print(f"Task: {task}", metrics)

def eval(inputs, gts, prompt_type, model_name=None):
        prompt_to_attr_key = {
            "hq_basic": "Attributes",
            "hq_cot1": "Related Attribute Values",
            "hq_cot2": "Attribute Values",  
            "hq_cot3": "Full Attribute Values",
            "hq_cot4": "Attributes"
        }
        metrics_result = {}
        metrics_result_tasks = {}
        for i, input in enumerate(inputs):
            GT = gts[i]["GT"]
            task = gts[i]["task"]
            model_response = input["predict"]
            # extract predict
            predict = extract(model_response, verbose=False, target_attr_key=prompt_to_attr_key[prompt_type])
            for key in ["Attributes", "Answer", "Analysis"]:
                if key not in predict:
                    predict[key] = ""
            predict_attributes = extract_attributes(predict["Attributes"], verbose=False)
            predict_answer = extract_answer(predict["Answer"], task, verbose=False)
            predict_analysis = predict["Analysis"]
            predict_dict = {
                "related_attributes": predict_attributes,
                "analysis": predict_analysis,
                "answer": predict_answer
            }
            # metrics
            # metrics = compute_attribute_metrics(GT, predict_dict, task, GT["related_attributes"])
            metrics = compute_metrics(GT, predict_dict, task=task, gt_attrs=GT["related_attributes"]) # TODO: attr 修改在这里
            # if model == "qwen" and task == "predict":
            #     print(metrics['answer_acc'], predict_dict["answer"], GT["answer"])

            # to task dict
            if task not in metrics_result_tasks:
                metrics_result_tasks[task] = {}
            for key, value in metrics.items():
                if key not in metrics_result_tasks[task]:
                    metrics_result_tasks[task][key] = 0.
                metrics_result_tasks[task][key] += value

        for task in metrics_result_tasks:
            for key in metrics_result_tasks[task]:
                metrics_result_tasks[task][key]
                metrics_result_tasks[task][key] = round(metrics_result_tasks[task][key], 2)

        return metrics_result_tasks

if __name__ == "__main__":
    import argparse
    from model_api.gpt4 import request_gpt4o
    request_api = request_gpt4o
    models = ["gpto1_mini", "gpt4o", "claude", "qwen", "llama3-1", "llama3_1_70b", "llama3-1_trained_remove_rec_fil_de", "llama3-1_trained_remove_bi", "llama3-1_trained"]
    datasets = ["alpaca_hq_basic_1000", "alpaca_hq_cot1_1000", "alpaca_hq_cot2_1000", "alpaca_hq_cot3_1000", "alpaca_hq_cot4_1000"]
    parser = argparse.ArgumentParser(description="Generate responses using GPT-4.")
    # parser.add_argument("--input_dir", type=str, default=None, help="input_dir")
    parser.add_argument("--gt_dir", type=str, default="benchmark/filtered_data_test_1000.jsonl", help="gt_dir")
    args = parser.parse_args()
    gt_dir = args.gt_dir
    gts = load_items(gt_dir) if gt_dir is not None else None
    output_dir = "evaluate_models/output_metrics/all_datasets_all_models_metrics.json"
    results_dict = {}
    for file_name in datasets:
        prompt_type = file_name[len("alpaca_"):-len("_1000")]
        results_dict[file_name] = {}
        for model in tqdm(models):
            input_dir = os.path.join(f"evaluate_models/output/{file_name}", f"{model}.jsonl")
            # if path exists, load
            if not os.path.exists(input_dir):
                print(f"File not found: {input_dir}")
                continue
            inputs = load_items(input_dir)
            if len(inputs) != 1000:
                print("Warning! file not 1000", input_dir)
            output_dict = eval(inputs, gts, prompt_type=prompt_type, model_name=model)
            results_dict[file_name][model] = output_dict
    
    # save
    with open(output_dir, 'w', encoding='utf-8') as outfile:
        json.dump(results_dict, outfile, ensure_ascii=False)