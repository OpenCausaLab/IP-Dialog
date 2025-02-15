import random
import sys
import os
import json
import re
current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print(current_dir)
sys.path.append(current_dir)
from data_gen.attributes_tasks_domains import task_info, attribute_dict
from utils import resume_from_generated, load_items

def diaglogue_to_text(dialogue):
    return '\n'.join([f"{item['speaker']}: {item['content']}" for item in dialogue])

def gen_answer(item):
    task = item["task"]
    if task in ["decision", "predict"]:
        answer = item["GT"]["answer"]
    elif task in ["filter","preference_infer", "rank"]:
        answer = ", ".join(item["GT"]["answer"])
    elif task in ["risk_detect", "intention_infer", "advice"]:
        answer = ""
        for i, answer_item in enumerate(item["GT"]["answer"]):
            answer += f"{i+1}. {answer_item} "
    elif task in ["recommend", "convince"]:
        answer = item["GT"]["answer"]
    else:
        raise ValueError(f"Task {task} not found.")
    return answer

answer_note_for_questions = {
    "recommend": "",
    "rank": "",
    "filter": "\n- Make sure there is no more than 2 item left after filtering.",
    "predict": "\n- your Answer should include yes and no only.",
    "preference_infer": "\n- You can choose 1,2 or 3 options in your Answer. Make sure they best satisfy what the user prefers most.",
    "risk_detect": "\n- List the risks with numbers in your Answer.",
    "intention_infer": "\n- List the intentions with numbers in your Answer.",
    "advice": "\n- Respond to the user's request with actionable advice. Offer a specific method or step to address their problem rather than suggesting an object. List the advices with numbers in your Answer.",
    "decision": "\n- Your answer should be either yes or no.",
    "convince": ""
}

task_definition_no_attr = {
    "recommend": "recommend products for user",
    "rank": "rank a series of given items according to the user's potential level of interest.",
    "filter": "filter a given list of items user preferences, retaining suitable content and removing irrelevant items.",
    "predict": "predict whether a user will take a specific action or make a particular decision.",
    "preference_infer": "infer the type or characteristics of objects an individual prefers. This involves understanding their general preferences rather than identifying specific items they might like.",
    "risk_detect": "detect potential risks that a user with the given attributes may face.",
    "intention_infer": "infer the exact intentions of a user given an implicit user request.",
    "advice": "provide actionable advice to the user. Offer specific methods to address their problem.",
    "decision": "make a decision for a user on whether to perform an action or not.",
    "convince": "convince the user to perform an action or adopt a certain attitude."
}

ans_format = {
    "recommend": "- Answer: [recommendation1, recommendation2, ...]. (Your answer should be concise.)",
    "rank": "- Answer: [your ranked options], such as [A, B, C, D]",
    "filter": "- Answer: [your filtered options only], such as [A, B]",
    "predict": "- Answer: [yes or no]",
    "preference_infer": "- Answer: [your options only], such as [A, B]",
    "risk_detect": "- Answer: [1. risk1 2. risk2 3. ... ...]. (Your answer should be concise.)",
    "intention_infer": "- Answer: [1. intention1 2. intention2 3. ... ...]. (Your answer should be concise.)",
    "advice": "- Answer: [1. advice1 2. advice2 3. ... ...] (Your answer should be concise.)",
    "decision": "- Answer: [yes or no]",
    "convince": "- Answer: [..] (Your answer should be concise.)"
}

def get_prompt(item, prompt_type):
    # assert prompt_type in ["hq_basic", "q", "h"]
    # task = item["task"]
    # task_description = task_info[task]["description"]
    # example_request_and_response = task_info[task]["example_request_and_response"] if "example_request_and_response" in task_info[task] else ""
    # example_user_attribute_group = task_info[task]["example_user_attribute_group"] if "example_user_attribute_group" in task_info[task] else ""
    # answer_note = task_info[task]["answer_note"] if "answer_note" in task_info[task] else ""
    # additional_output = task_info[task]["additional_output"] if "additional_output" in task_info[task] else ""
    history = "\n".join(diaglogue_to_text(item["history"][i]) for i in range(len(item["history"])))
    task = item["task"]
    request = item["request"]
    if prompt_type == "hq_basic":
        prompt = f"""You are a helpful agent for the task: {task}. The task requires the agent to {task_definition_no_attr[task]}
You will leverage my history dialogue to respond to my request in a personalized way. My history dialogue is:

{history}

---Important Note---{answer_note_for_questions[task]}
- First, provide the reasoning process for your answer in Analysis: [..]. Then, present your formatted answer in Answer: [..].
- Output your response in the format below, do not omit the [] in your response:
Output: 
- Analysis: [..]
{ans_format[task]}

My Request: {request}
Output: """
    elif prompt_type == "hq_cot1":
        prompt = f"""You are a helpful agent for the task: {task}. The task requires the agent to {task_definition_no_attr[task]}
You will leverage my history dialogue and my inferred attributes to respond to my request in a personalized way. My history dialogue is:

{history}

You can infer my attributes from the user attribute group: {str(attribute_dict)}
---Important Note---{answer_note_for_questions[task]}
- First, infer my attribute value of ALL the attributes in the user attribute group in Full Attribute Values: [...]. Then, extract related attributes you will use to answer my request, put them in Related Attribute Values: [..]. Next, provide the reasoning process for your answer in Analysis: [..]. Finally, present your formatted answer in Answer: [..].
- You should extract the user attributes that are most relevant to the request. Use no more than 5 attributes. ALL the attributes values should be selected from the given user attribute group.
- Your reasoning should be concise and clear.
- Output your response in the format below, do not omit the [] in your response:
Output: 
- Full Attribute Values: [attribute1: value1, attribute2: value2, ..., attribute12: value12], such as [age: child, income_level: low_income, ..., hobby: sports]
- Related Attribute Values: [related_attribute1, related_attribute2, ...], such as [age: child, profession: student]
- Analysis: [..]
{ans_format[task]}

My Request: {request}
Output: """
    elif prompt_type == "hq_cot2":
        prompt = f"""You are a helpful agent for the task: {task}. The task requires the agent to {task_definition_no_attr[task]}
You will leverage my history dialogue and my inferred attributes to respond to my request in a personalized way. My history dialogue is:

{history}

You can infer my attributes from the user attribute group: {str(attribute_dict)}
---Important Note---{answer_note_for_questions[task]}
- First, identify what attribute keys are most related to answer my request in Attribute Key: [...]. Then, based on my history dialogue, infer attribute values of your identified attribute, write it in Attribute Values: [..]. Next, provide the reasoning process for your answer in Analysis: [..]. Finally, present your formatted answer in Answer: [..].
- You should select the user attributes that are most relevant to the request. Use no more than 5 attributes. The attributes should be selected from the given user attribute group.
- Your reasoning should be concise and clear.
- Output your response in the format below, do not omit the [] in your response:
Output: 
- Attribute Key: [attribute1, attribute2, ...], such as [age, profession]
- Attribute Values: [attribute1: value1, attribute2: value2, ...], such as [age: child, profession: student]
- Analysis: [..]
{ans_format[task]}

My Request: {request}
Output: """
    elif prompt_type == "hq_cot3":
        prompt = f"""You are a helpful agent for the task: {task}. The task requires the agent to {task_definition_no_attr[task]}
You will leverage my history dialogue and my inferred attributes to respond to my request in a personalized way. My history dialogue is:

{history}

You can infer my attributes from the user attribute group: {str(attribute_dict)}
---Important Note---{answer_note_for_questions[task]}
- First, infer my attribute value of ALL the attributes in the user attribute group in Full Attribute Values: [...]. Next, provide the reasoning process for your answer in Analysis: [..]. Finally, present your formatted answer in Answer: [..].
- ALL the attributes values should be selected from the given user attribute group.
- Your reasoning should be concise and clear.
- Output your response in the format below, do not omit the [] in your response:
Output: 
- Full Attribute Values: [attribute1: value1, attribute2: value2, ..., attribute12: value12], such as [age: child, income_level: low_income, ..., hobby: sports]
- Analysis: [..]
{ans_format[task]}

My Request: {request}
Output: """
    elif prompt_type == "hq_cot4":
        prompt = f"""You are a helpful agent for the task: {task}. The task requires the agent to {task_definition_no_attr[task]}
You will leverage my history dialogue and my inferred attributes to respond to my request in a personalized way. My history dialogue is:

{history}

You can infer my attributes from the user attribute group: {str(attribute_dict)}
---Important Note---{answer_note_for_questions[task]}
- First, based on my history dialogue and my request, infer related attributes you will use to answer my request in Attributes: [..]. Then, provide the reasoning process for your answer in Analysis: [..]. Finally, present your formatted answer in Answer: [..].
- You should select the user attributes that are most relevant to the request. Use no more than 5 attributes. The attributes should be selected from the given user attribute group.
- Your reasoning should be concise and clear.
- Output your response in the format below, do not omit the [] in your response:
Output: 
- Attributes: [attribute1: value1, attribute2: value2, ...], such as [age: child, profession: student]
- Analysis: [..]
{ans_format[task]}

My Request: {request}
Output: """
    else:
        raise ValueError(f"Prompt type {prompt_type} not found.")
    return prompt

def gen_attr_key_text(attrbutes):
    attr_text = ", ".join([f"{key}" for key in attrbutes])
    return attr_text

def get_full_answer(item, prompt_type):
    if prompt_type == "hq_basic":
        answer = f'''- Analysis: [{item['GT']['analysis']}]
- Answer: [{gen_answer(item)}]'''
    elif prompt_type == "hq_cot1":
        answer = f'''- Full Attribute Values: [No Support]
- Related Attribute Values: [{gen_attr_text(item['GT']['related_attributes'])}]
- Analysis: [{item['GT']['analysis']}]
- Answer: [{gen_answer(item)}]'''
    elif prompt_type == "hq_cot2":
        answer = f'''- Attribute Key: [{gen_attr_key_text(item['GT']['related_attributes'])}]
- Attribute Values: [{gen_attr_text(item['GT']['related_attributes'])}]
- Analysis: [{item['GT']['analysis']}]
- Answer: [{gen_answer(item)}]'''
    elif prompt_type == "hq_cot3":
        answer = f'''- Full Attribute Values: [No Support]
- Analysis: [{item['GT']['analysis']}]
- Answer: [{gen_answer(item)}]'''
    elif prompt_type == "hq_cot4":
        answer = f'''- Attributes: [{gen_attr_text(item['GT']['related_attributes'])}]
- Analysis: [{item['GT']['analysis']}]
- Answer: [{gen_answer(item)}]'''
    else:
        raise ValueError(f"Prompt type {prompt_type} not found.")
    return answer

def gen_attr_text(attrbutes):
    attr_text = ", ".join([f"{key}: {value}" for key, value in attrbutes.items()])
    return attr_text
    
def generate_responses(full_items, output_file, prompt_type):
    tasks = []
    with open(output_file, "w", encoding='utf-8') as outfile:
        for i, input in enumerate(full_items):
            assert prompt_type in ["hq_basic", "hq_cot1", "hq_cot2", "hq_cot3", "hq_cot4", "q", "h"]
            input_str = get_prompt(input, prompt_type)
            output_str = get_full_answer(input, prompt_type)
            output_dict = {
                "index": input["index"],
                "task": input["task"],
                "instruction": "",
                "input": input_str,
                "output": output_str
            }
            if input["task"] not in tasks:
                tasks.append(input["task"])
                print(f"=================================={input['task']}==================================")
                print(f"[Input]: {input_str}")
                print("------------------------------------------------------------------------------------")
                print(f"[Output]: {output_str}")
            json.dump(output_dict, outfile, ensure_ascii=False)
            outfile.write("\n")
    
if __name__ == "__main__":
    input_file = "benchmark/train_data_10790.jsonl"
    prompt_type = "hq_basic" # ["hq_basic", "hq_cot4", "hq_cot2", "hq_cot1", "q", "h"]
    for prompt_type in [ "hq_cot4",]:
        output_file = f"benchmark/train_alpaca_{prompt_type}_10790.jsonl"
        if not os.path.exists(os.path.dirname(output_file)):
            os.makedirs(os.path.dirname(output_file))
        input_data = load_items(input_file)
        generate_responses(input_data, output_file, prompt_type)