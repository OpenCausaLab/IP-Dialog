import random
import sys
import os
import json
import re
current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(current_dir)
print(current_dir)
from utils import load_items, resume_from_generated

def extract_dialogue(text):
    # First check if "Modified Dialogue:" marker exists
    modified_dialogue_match = re.search(r'Modified Dialogue:\s*(.*)', text, re.DOTALL)
    if modified_dialogue_match:
        print("!!!!")
        # If exists, only process the part after "Modified Dialogue:"
        text = modified_dialogue_match.group(1)
    
    # Use regex to match User and AI dialogues, supporting multiple rounds
    if '\n' in text:
        pattern = r'(User|AI):\s*(.*?)(?=\n(?:User|AI):|\Z)'
    else:
        pattern = r'(User|AI):\s*(.*?)(?=(?:User|AI):|$)'
    matches = re.findall(pattern, text, re.DOTALL)
    
    # Format matching results into a list, each element is a dictionary
    dialogue = []
    expected_speaker = "User"
    
    for speaker, content in matches:
        assert len(content.strip()) > 1, f"Empty content: {content}"
        assert len(content.strip()) < 500, f"Content too long: {content}"
        if speaker != expected_speaker:
            raise ValueError(f"Unexpected speaker: {speaker},\n{content}\n, {text}")
        
        dialogue.append({
            'speaker': speaker,
            'content': content.strip()
        })
        
        # Switch to the next expected speaker
        expected_speaker = "AI" if expected_speaker == "User" else "User"
    assert len(dialogue) > 1, f"len not enough{text}"
    assert text.strip()[-len(dialogue[-1]['content']):] == dialogue[-1]['content'], f"{text}"
    assert len(dialogue) == 2, f"num of dialogue not 2, text:\n{text}"
    return dialogue

def diaglogue_to_text(dialogue):
    return '\n'.join([f"{item['speaker']}: {item['content']}" for item in dialogue])

def generate_histories(inputs, output_file, turn_id):
    with open(output_file, 'w', encoding='utf-8') as outfile:
        for i, input in enumerate(inputs):
            output_data = input.copy()
            if input["generation_finished"] == "yes" or input[f"dialogue_t{turn_id}"]["check_extracted"]["pass_exam"] == "yes":
                pass
            else:
                model_response = input[f"dialogue_t{turn_id}"]["output"]
                dialogue = diaglogue_to_text(extract_dialogue(model_response))
                output_data[f"dialogue_t{turn_id}"]["dialogue"] = dialogue
                output_data[f"dialogue_t{turn_id}"].pop("output")
            json.dump(output_data, outfile, ensure_ascii=False)
            outfile.write('\n')
            outfile.flush()  # Ensure data is written to file immediately

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Generate responses using GPT-4.")
    parser.add_argument("--task", type=str, default="decision", help="Task type", choices=['recommend', 'rank', 'filter', 'predict', 'preference_infer', 'intention_infer', 'risk_detect', 'advice', 'decision', 'convince','total_task','random_subset_1000'])
    parser.add_argument("--turn_id", type=int, required=True, help="Turn ID")
    parser.add_argument("--iter_id", type=int, required=True, help="Iteration ID")
    args = parser.parse_args()
    task = args.task

    input_dir = f"testset/output/{task}/history/turn_{args.turn_id}/dialogue_i-{args.iter_id}.jsonl"
    output_dir = f"testset/output/{task}/history/turn_{args.turn_id}/dialogue_i-{args.iter_id}_extracted.jsonl"
    inputs = load_items(input_dir)
    generate_histories(inputs, output_dir, args.turn_id)