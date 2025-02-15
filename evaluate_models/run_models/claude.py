import random
import sys
import os
import json
import re
current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(current_dir)
print(current_dir)
from utils import load_items, resume_from_generated
from tqdm import tqdm

def run_model(inputs, output_file, request_api, start_id=0, max_tokens=500):
    with open(output_file, 'a', encoding='utf-8') as outfile:
        for i, input in tqdm(enumerate(inputs)):
            idx = i
            if idx < start_id:
                continue
            output_data = input.copy()
            print("\n" + "="*50 + str(i) + "/"+str(len(inputs))+"="*50)
            prompt = input['instruction'] + input['input']
            model_answer = request_api(prompt, max_tokens=max_tokens)
            output_data['predict'] = model_answer
            json.dump(output_data, outfile, ensure_ascii=False)
            outfile.write('\n')
            outfile.flush()  # 确保数据立即写入文件
            print(f"Input: {prompt}")
            print(f"Output: {model_answer}")
            print("\n" + "="*50)
            assert type(model_answer) == str, model_answer
            assert "\"type\":\"error\"" not in model_answer, model_answer

if __name__ == "__main__":
    import argparse
    from model_api.claude import request_claude
    request_api = request_claude
    parser = argparse.ArgumentParser(description="Generate responses using claude.")
    parser.add_argument("--input_dir", type=str, default=None, help="input_dir")
    args = parser.parse_args()
    file_name = os.path.splitext(args.input_dir)[0]
    if "\\" in file_name:
        file_name = file_name.split("\\")[-1]
    output_dir = f"evaluate_models/output/{file_name}/claude.jsonl"
    inputs = load_items(args.input_dir)

    start_id = resume_from_generated(output_dir)
    run_model(inputs, output_dir, request_api, start_id=start_id, max_tokens=500)