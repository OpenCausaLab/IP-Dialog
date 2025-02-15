import json
import os
import random   

# load items from json or jsonl file
def load_items(file_path:str):
    if file_path.endswith('.jsonl'):
        questions = []
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                questions.append(json.loads(line))
    elif file_path.endswith('.json'):
        with open(file_path, 'r', encoding='utf-8') as file:
            questions = json.load(file)
    else:
        raise ValueError
    return questions

# load on random item
def load_one_random_item(file_path:str):
    res = None
    if file_path.endswith('.jsonl'):
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            res = json.loads(random.choice(lines))
    elif file_path.endswith('.json'):
        with open(file_path, 'r', encoding='utf-8') as file:
            res = random.choice(json.load(file))
    else:   
        raise ValueError
    return res


def resume_from_generated(output_file):
    output_dir = os.path.dirname(output_file)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    if os.path.exists(output_file):
        file_data = load_items(output_file)
        current_num = len(file_data)
        print(f'[Info] The file "{output_file}" already exists, and the current number of questions is {current_num}.')
    else:
        current_num = 0
        file_data = []
    return current_num

def check_file_eror(input_dir):
    def validate_json(file_path):
       with open(file_path, 'r', encoding='utf-8') as f:
           for i, line in enumerate(f, 1):
               try:
                   json.loads(line)
               except json.JSONDecodeError as e:
                   print(f"Error in line {i}: {e}")
                   print(f"Problematic content: {line[:50]}...")  # 打印前50个字符
    validate_json(input_dir)

if __name__ == "__main__":
    # input_dir = "E:\OneDrive\\AHE\\Projects\\PersonaLLM\\datasets\\bench\\evaluate_models\\output\\alpaca_hq_cot2_1000\\claude.jsonl"
    # check_file_eror(input_dir)
    import math
    def calculate_random_accuracy(total_options: int, correct_answers: int) -> float:
        """
        Calculate the random accuracy when selecting correct_answers from total_options.
        
        Args:
            total_options (int): Total number of available options (a)
            correct_answers (int): Number of correct answers to be selected (b)
        
        Returns:
            float: The random accuracy as a probability (between 0 and 1)
        
        Example:
            >>> calculate_random_accuracy(4, 2)
            0.16666666666666666  # 1/6
            >>> calculate_random_accuracy(5, 3)
            0.1  # 1/10
        """
        # Calculate combinations: C(a,b) = a!/(b!(a-b)!)
        combinations = math.comb(total_options, correct_answers)
        
        # Random accuracy is 1/combinations
        return 1 / combinations
    
    input_dir = "E:\OneDrive\\AHE\\Projects\\PersonaLLM\\datasets\\bench\\benchmark\\filtered_data_test_1000.jsonl"
    len_dict = {}
    len_task_dict = {"filter":0, "preference_infer":0}
    inputs = load_items(input_dir)
    for i, input in enumerate(inputs):
        if input["task"] == "rank":
            len_answer = len(input["GT"]["answer"])
            if len_answer not in len_dict.keys():
                len_dict[len_answer] = 0
            len_dict[len_answer] += 1
        if input["task"] == "filter":
            len_answer = len(input["GT"]["answer"])
            len_task_dict["filter"] += calculate_random_accuracy(5, len_answer)
        if input["task"] == "preference_infer":
            len_answer = len(input["GT"]["answer"])
            len_task_dict["preference_infer"] += calculate_random_accuracy(4, len_answer)
    print(len_task_dict)