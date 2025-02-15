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
from attributes_tasks_domains import attribute_dict

def extract(model_response, verbose=True, target_attr_key='Attributes'):
    # Define regex patterns
    regex_for_attrs = {"Related Attribute Values": r'Related Attribute Values:\s*\[(.*?)\]',
                       'Attribute Values': r'Attribute Values:\s*\[(.*?)\]',
                       'Full Attribute Values': r'Full Attribute Values:\s*\[(.*?)\]'}
    patterns = {
        'Attributes': r'Attributes:\s*\[(.*?)\]',
        'Analysis': r'Analysis:\s*\[(.*?)\]',
        'Answer': r'Answer:\s*\[(.*?)\]'
    }
    if target_attr_key != 'Attributes':
        patterns["Attributes"] = regex_for_attrs[target_attr_key]
    
    result = {}
    
    # Try to extract using the original format
    for key, pattern in patterns.items():
        match = re.search(pattern, model_response, re.DOTALL)
        if match:
            result[key] = match.group(1).strip()
    if 'Attributes' not in result:
        regex_for_attrs = {"Related Attribute Values": r'- \*\*Related Attribute Values\*\*:\s*\[(.*?)\]',
                        'Attribute Values': r'- \*\*Attribute Values\*\*:\s*\[(.*?)\]',
                        'Full Attribute Values': r'- \*\*Full Attribute Values\*\*:\s*\[(.*?)\]'}
        if target_attr_key == 'Attributes':
            analysis_pattern = r'- \*\*Attributes\*\*:\s*\[(.*?)\]'
        else:
            analysis_pattern = regex_for_attrs[target_attr_key]
        match = re.search(analysis_pattern, model_response, re.DOTALL)
        if match:
            result['Attributes'] = match.group(1).strip()

    if 'Attributes' not in result:
        regex_for_attrs = {"Related Attribute Values": r'"Related Attribute Values":\s*(\[[\s\S]*?\])',
                        'Attribute Values': r'"Attribute Values":\s*(\[[\s\S]*?\])',
                        'Full Attribute Values': r'"Full Attribute Values":\s*(\[[\s\S]*?\])',}
        if target_attr_key == 'Attributes':
            analysis_pattern = r'"Attributes":\s*(\[[\s\S]*?\])'
        else:
            analysis_pattern = regex_for_attrs[target_attr_key]
        match = re.search(analysis_pattern, model_response, re.DOTALL)
        if match:
            result['Attributes'] = match.group(1).strip()
    
    # If the original format didn't work for 'Analysis', try the new format
    if 'Analysis' not in result:
        analysis_pattern = r'Analysis:\s*(.*?)(?=\n-\s*(?:Answer|$))'
        match = re.search(analysis_pattern, model_response, re.DOTALL)
        if match:
            result['Analysis'] = match.group(1).strip()

    if 'Analysis' not in result:
        # print("test new pattern:", model_response)
        analysis_pattern = r'\*\*Analysis\*\*:?\s*([\s\S]*?)(?=\s*\n\s*- \*\*Answer\*\*)'
        match = re.search(analysis_pattern, model_response, re.DOTALL | re.IGNORECASE)
        if match:
            result['Analysis'] = match.group(1).strip()
        # print('\n',result['Analysis']) if 'Analysis' in result else print("no Analysis!!!!!!!!!!!")
            
    if 'Analysis' not in result:
        # print("test new pattern:", model_response)
        analysis_pattern = r'\*\*Analysis:\*\*\s*([\s\S]*?)(?=\s*\n\s*- \*\*Answer:\*\*)'
        match = re.search(analysis_pattern, model_response, re.DOTALL | re.IGNORECASE)
        if match:
            result['Analysis'] = match.group(1).strip()
        # print('\n',result['Analysis']) if 'Analysis' in result else print("no Analysis!!!!!!!!!!!")
            
    if 'Analysis' not in result:
        # print("test new pattern:", model_response)
        analysis_pattern = r'"Analysis":\s*\[([\s\S]*?)\]'
        match = re.search(analysis_pattern, model_response, re.DOTALL | re.IGNORECASE)
        if match:
            result['Analysis'] = match.group(1).strip()
        # print('\n',result['Analysis']) if 'Analysis' in result else print("no Analysis!!!!!!!!!!!")

    # If the original format didn't work for 'Answer', try the new format
    if 'Answer' not in result:
        answer_pattern = r'Answer:\s*\n((?:\s*\d+\..*(?:\n|$))+)'
        match = re.search(answer_pattern, model_response, re.DOTALL)
        if match:
            result['Answer'] = match.group(1).strip()

    if 'Answer' not in result:
        model_response += ']'
        answer_pattern = r'Answer:\s*\n((?:\s*\d+\..*(?:\n|$))+)'
        match = re.search(answer_pattern, model_response, re.DOTALL)
        if match:
            result['Answer'] = match.group(1).strip()

    if 'Answer' not in result:
        answer_pattern = r'Answer:\s*\[(.*?)\]'   
        match = re.search(answer_pattern, model_response, re.DOTALL)
        if match:
            result['Answer'] = match.group(1).strip()
    
    if 'Answer' not in result:
        # print("Test nuw pattern", model_response)
        answer_pattern = r'Answer:\s*([\s\S]*?)(?=\Z|\n-\s*[A-Z])'
        match = re.search(answer_pattern, model_response, re.DOTALL)
        if match:
            result['Answer'] = match.group(1).strip()
        # print('\n',result['Answer']) if 'Answer' in result else print("No Answer")
        # exit()
            
    if 'Answer' not in result:
        # print("Test nuw pattern", model_response)
        answer_pattern = r'- \*\*Answer\*\*:\s*([\s\S]*?)(?=\Z|\n-\s*\*\*)'
        match = re.search(answer_pattern, model_response, re.DOTALL)
        if match:
            result['Answer'] = match.group(1).strip()
        # print('\n',result['Answer']) if 'Answer' in result else print("No Answer")
        # exit()
            
    if 'Answer' not in result:
        # print("Test nuw pattern", model_response)
        answer_pattern = r'"Answer":\s*(\[[\s\S]*?\])'
        match = re.search(answer_pattern, model_response, re.DOTALL)
        if match:
            result['Answer'] = match.group(1).strip()
        # print('\n',result['Answer']) if 'Answer' in result else print("No Answer")
        # exit()

    # Check if all keys are present
    for key in patterns.keys():
        if key not in result and verbose:
            raise ValueError(f"Cannot extract content for {key}:\n {model_response}")
    
    return result
    
def reextract_request(request):
    pattern = r'(?:request\s*\d+:\s*)?(.*?)\s*$'
    match = re.search(pattern, request, re.IGNORECASE | re.DOTALL)
    
    if match:
        extracted_request = match.group(1).strip()
        if extracted_request:
            return extracted_request
        else:
            raise ValueError("Extracted request content is empty")
    else:
        raise ValueError("Cannot extract valid request from input")

def extract_attributes(attributes_text, verbose=True):
    # 将输入字符串分割成键值对
    pairs = [pair.strip() for pair in attributes_text.split(',')]
    
    result = {}
    
    for pair in pairs:
        if ":" not in pair:
            if verbose:
                raise ValueError(f"Invalid key-value pair: {attributes_text}")
            else:
                continue
        if len(pair.split(':')) != 2:
            if verbose:
                raise ValueError(f"Invalid key-value pair, !=2: \n{attributes_text}\n{pair}")
            else:
                continue
        key, value = pair.split(':')
        key = key.strip()
        value = value.strip()
        
        # Check if key exists in attribute_dict
        if key not in attribute_dict and verbose:
            raise ValueError(f"Invalid attribute: {key}\nfrom {attributes_text}")
        
        # Check if value exists in corresponding list in attribute_dict 
        if verbose and value not in attribute_dict[key]:
            raise ValueError(f"Invalid value '{value}' for attribute '{key}'\nfrom {attributes_text}")
        
        # If validation passes, add key-value pair to result dictionary
        result[key] = value
    
    return result
def check_valid_opntions(options, task, answer_text):
    if task in ["decision", "predict"]:
        assert options in ["yes", "no"], options
    elif task in ["filter","preference_infer"]:
        valid_options = set('ABCDE12345abcde')
        valid_options.update({'i', 'ii', 'iii', 'iv', 'vi', 'I', 'II', 'III', 'IV', 'VI'})
        assert all(option in valid_options for option in options), f"Invalid options for tasks, {options}"
    elif task == "rank":
        if len(options) == 3:
            print(f"Warning: Answer for task '{task}' only has three options: {options}")
        else:
            # assert all(opt in options for opt in ["A", "B", "C", "D"]), f"Invalid options for rank task, {options}"
            assert all(((opt in options) or (opt.upper() in options) or (opt.lower() in options)) for opt in ["A", "B", "C", "D"]), f"Invalid options for rank task, {options}, \n{answer_text}"
    else:
        raise ValueError(f"Cannot check if options are valid for task '{task}'")
    
def extract_answer(answer_text, task, verbose=True):
    result_answer = None
    if task in ["decision", "predict"]:
        answer_text = answer_text.strip().lower()
        if "]" in answer_text:
            answer_text = answer_text.split("]")[0]
        if verbose:
            assert answer_text in ["yes", "no"], answer_text
        result_answer =  answer_text
    elif task in ["filter","preference_infer", "rank"]:
        # pattern = r'([A-E])(?:,\s*|\s*$)'
        pattern = r'\b([A-Ea-e]|i{1,3}|iv|vi|[1-5]|I{1,3}|IV|VI)(?:,\s*|\s*$)'
        options = re.findall(pattern, answer_text)
        # Check if all options are in A, B, C, D, E
        # valid_options = set('ABCDE')
        # if not all(option in valid_options for option in options):
        #     raise ValueError("Invalid option detected. Options must be A, B, C, D, or E.")
        if verbose:
            check_valid_opntions(options, task, answer_text)
        # if task == "rank":
        #     if len(options) == 3:
        #         print(f"Warning: Answer for task '{task}' only has three options: {answer_text}")
        #     elif verbose:
        #         assert all(opt in options for opt in ["A", "B", "C", "D"]), f"Invalid options for rank task, {answer_text}"
        if len(options) == 0:
            # pattern = r'([A-Z])\.\s*([^,]+)'
            pattern = r'([A-E1-5a-e]|i{1,3}|iv|vi)\.\s*([^,]+)'
            matches = re.findall(pattern, answer_text)
            options = [match[0] for match in matches]
        if len(answer_text) > 15 and verbose:
            print("Warning: Answer length greater than 15, potential issue, option:", options, answer_text)
        result_answer = options
    elif task in ["risk_detect", "intention_infer", "advice"]:
        pattern = r"\d+\.\s+(.*?)(?=\s+\d+\.|$)"
        matches = re.findall(pattern, answer_text)
        
        if not matches and verbose:
            raise ValueError("No numbered items found in the provided text.")
        
        result_answer = matches
    elif task in ["recommend", "convince"]:
        result_answer = answer_text.strip()
    else:
        raise ValueError("No numbered items found in the provided text.")
    
    if verbose:
       assert result_answer is not None, f"Extracted answer is None: {answer_text}"
       assert len(result_answer) > 0, f"Extracted answer is empty: {answer_text}"
    return result_answer

def invalid_request(request, task):
    pattern = r'^request \d+$'
    if bool(re.match(pattern, request, re.IGNORECASE)):
        return True
    elif len(request) < 10:
        print(f"Warning: Request '{request}' length is less than 10, from task '{task}'")
        return False
    return False

def generate_responses(input_data, output_file):
    analysis_dict = {"attribute_len":{"min":100, "max":0, "avg": 0},
                     "attribute_distribution":{},
                     "attribute_value_distribution":{},
                     "answer_distribution":{},
                     "analysis_len":{"min":100, "max":0, "avg": 0}}
    invalid_num = 0
    count = 0
    with open(output_file, "w", encoding='utf-8') as outfile:
        for i, input in enumerate(input_data):
            model_response = input["output"]
            request = input["request"]
            if invalid_request(request, task):
                invalid_num += 1
                continue
            GT = extract(model_response)
            attributes = extract_attributes(GT["Attributes"])
            output_dict = {"index": count,
                           "task": input["task"], 
                           "task_index": input["task_index"], 
                           "domain_index": input["domain_index"], 
                           "subject_index": input["subject_index"],
                           "request_index": input["request_index"],
                           "domain": input["domain"], 
                           "user_attr_group": input["user_attr_group"],
                           "request": reextract_request(input["request"]),
                           "GT": {"related_attributes": attributes,
                                            "analysis": GT["Analysis"],
                                            "answer": extract_answer(GT["Answer"], input["task"])}}
            
            analysis_dict["attribute_len"]["min"] = min(analysis_dict["attribute_len"]["min"], len(attributes))
            analysis_dict["attribute_len"]["max"] = max(analysis_dict["attribute_len"]["max"], len(attributes))
            analysis_dict["attribute_len"]["avg"] += len(attributes)
            analysis_dict["analysis_len"]["min"] = min(analysis_dict["analysis_len"]["min"], len(GT["Analysis"]))
            analysis_dict["analysis_len"]["max"] = max(analysis_dict["analysis_len"]["max"], len(GT["Analysis"]))
            analysis_dict["analysis_len"]["avg"] += len(GT["Analysis"])

            for key in attributes:
                if key not in analysis_dict["attribute_distribution"]:
                    analysis_dict["attribute_distribution"][key] = 0
                analysis_dict["attribute_distribution"][key] += 1

            analysis_dict["attribute_distribution"] = dict(sorted(analysis_dict["attribute_distribution"].items(), key=lambda x: x[1], reverse=True))

            if input["task"] in ["decision", "predict"]:
                if output_dict["GT"]["answer"] not in analysis_dict["answer_distribution"]:
                    analysis_dict["answer_distribution"][output_dict["GT"]["answer"]] = 0
                analysis_dict["answer_distribution"][output_dict["GT"]["answer"]] += 1
            elif input["task"] in ["filter"]:
                for option in output_dict["GT"]["answer"]:
                    if option not in analysis_dict["answer_distribution"]:
                        analysis_dict["answer_distribution"][option] = 0
                    analysis_dict["answer_distribution"][option] += 1

            json.dump(output_dict, outfile, ensure_ascii=False)
            outfile.write("\n")
            count += 1
        analysis_dict["attribute_len"]["avg"] /= len(input_data)
        analysis_dict["analysis_len"]["avg"] /= len(input_data)
        analysis_dict["attribute_len"]["avg"] = round(analysis_dict["attribute_len"]["avg"], 2)
        analysis_dict["analysis_len"]["avg"] = round(analysis_dict["analysis_len"]["avg"], 2)
        print(f"\nTask: {input['task']}, analysis_dict: {analysis_dict}")
        print(f"Total: {len(input_data)}, invalid: {invalid_num}, valid: {count}")
    
if __name__ == "__main__":
    for task in task_info:
        print("Run answer extract on task: ", task)
        input_file = f"testset/output/{task}/question/GT.jsonl"
        output_file = f"testset/output/{task}/question/GT_extracted.jsonl"
        # if input file does not exist, skip
        if not os.path.exists(input_file):
            print(f"[Warning] The file '{input_file}' does not exist, skip.")
            continue
        if not os.path.exists(os.path.dirname(output_file)):
            os.makedirs(os.path.dirname(output_file))
        input_data = load_items(input_file)
        generate_responses(input_data, output_file)