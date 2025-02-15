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
from history_turn_extract import extract_dialogue
    
def process_histort(history_item):
    history_id = history_item["id"]
    history_count = history_item["GT"]["count"]
    dialogues = []
    attr_len = len(history_item["GT"]["related_attributes"])
    for i in range(attr_len):
        dialogue = history_item[f"dialogue_t{i}"]["dialogue"]
        dialogue_extracted = extract_dialogue(dialogue)
        dialogues.append(dialogue_extracted)
    return history_id, history_count, dialogues

def is_success_history(history_item):
    assert history_item["generation_finished"] == "yes"
    if "remove" not in history_item:
        attr_len = len(history_item["GT"]["related_attributes"])
        assert f"dialogue_t{attr_len-1}" in history_item, f"\"id\": {history_item['id']}\n{history_item['GT']['related_attributes']}\n{history_item}"
        assert f"dialogue_t{attr_len}" not in history_item
    if "remove" in history_item:
        return False
    else:
        return True
    
if __name__ == "__main__":
    output_file = f"testset/output/total_task/History_Question.jsonl"
    input_history = "testset/output/total_task/history/turn_7/dialogue_i-0.jsonl"
    # history item dict
    history_attr_dict = {}
    histories = load_items(input_history)
    for history in histories:
        history_attr = history["GT"]["related_attributes"]
        history_attr_as_set = tuple(sorted(history_attr.items()))
        history_attr_dict[history_attr_as_set] = history

    total_items = []
    # total_items_not_removed = []
    for task in task_info:
        input_file = f"testset/output/{task}/question/GT_extracted.jsonl"
        input_data = load_items(input_file)
        for i, input in enumerate(input_data):
            attr = input["GT"]["related_attributes"]
            attr_as_set = tuple(sorted(attr.items()))
            history_item = history_attr_dict[attr_as_set]
            assert history_item is not None
            assert tuple(sorted(history_item["GT"]["related_attributes"].items())) == tuple(sorted(attr.items()))
            if is_success_history(history_item):
                history_id, history_count, dialogues = process_histort(history_item)
                output = {"id": len(total_items)}
                output.update(input)
                output["history_id"] = history_id
                output["history_count"] = history_count
                output["history"] = dialogues
                total_items.append(output)
            # total_items_not_removed.append(output)
    print(len(total_items))

    with open(output_file, "w", encoding='utf-8') as outfile:
        for item in total_items:
            json.dump(item, outfile, ensure_ascii=False)
            outfile.write("\n")

    # distribution
    task_dict = {}
    for item in total_items:
        task = item["task"]
        domain = item["domain"]
        subject_index = item["subject_index"]
        request_index = item["request_index"]
        assert domain is not None or task == "risk_detect"
        assert subject_index is not -1 or task == "risk_detect"
        assert request_index is not -1
        if task == "risk_detect":
            domain = "risk_detect"
            subject_index = "risk_detect"
        subject = domain + str(subject_index)
        request = domain + str(subject_index) + str(request_index)
        if task not in task_dict:
            task_dict[task] = {"domain": [], "subject": [], "request": [], "count": 0}
        if domain not in task_dict[task]["domain"]:
            task_dict[task]["domain"].append(domain)
        if subject not in task_dict[task]["subject"]:
            task_dict[task]["subject"].append(subject)
        if request not in task_dict[task]["request"]:
            task_dict[task]["request"].append(request)
        task_dict[task]["count"] += 1

    for task in task_dict:
        print(f"Task: {task}, Domain: {len(task_dict[task]['domain'])}, Subject: {len(task_dict[task]['request'])}, Request: {task_dict[task]['count']}")

    # print(len(total_items_not_removed))
    # task_not_removed_dict = {}
    # for item in total_items_not_removed:
    #     task = item["task"]
    #     domain = item["domain"]
    #     subject_index = item["subject_index"]
    #     request = item["request_index"]
    #     assert domain is not None or task == "risk_detect"
    #     assert subject_index is not -1 or task == "risk_detect"
    #     if task == "risk_detect":
    #         domain = "risk_detect"
    #         subject_index = "risk_detect"
    #     subject = domain + str(subject_index)
    #     if task not in task_not_removed_dict:
    #         task_not_removed_dict[task] = {"domain": [], "subject": []}
    #     if domain not in task_not_removed_dict[task]["domain"]:
    #         task_not_removed_dict[task]["domain"].append(domain)
    #     if subject not in task_not_removed_dict[task]["subject"]:
    #         task_not_removed_dict[task]["subject"].append(subject)
        