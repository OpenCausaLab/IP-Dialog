# Example for command of history generation
Here's a command example for history generation process of our dataset.
```
# step 0
    # step 0 - iter 0
    python data_gen\history_turn.py --task total_task --turn_id 0 
    python data_gen\history_turn_extract.py --task total_task --turn_id 0 --iter_id 0
    python data_gen\history_turn_exam.py --task total_task --turn_id 0 --iter_id 0 
    python data_gen\history_turn_exam_extract.py --task total_task --turn_id 0 --iter_id 0 
    # step 0 - iter 1 (improve)
    python data_gen\history_turn_improve.py --task total_task --turn_id 0 --iter_id 1
    python data_gen\history_turn_extract.py --task total_task --turn_id 0 --iter_id 1
    python data_gen\history_turn_exam.py --task total_task --turn_id 0 --iter_id 1
    python data_gen\history_turn_exam_extract.py --task total_task --turn_id 0 --iter_id 1
    # step 0 - iter 2 (improve)
    ...
    # step 0 - iter 3 (improve)
    ...
    # step 0 - iter 4 (regen)
    python data_gen\history_turn_regen.py --task total_task --turn_id 0 --iter_id 4
    python data_gen\history_turn_extract.py --task total_task --turn_id 0 --iter_id 4
    python data_gen\history_turn_exam.py --task total_task --turn_id 0 --iter_id 4
    python data_gen\history_turn_exam_extract.py --task total_task --turn_id 0 --iter_id 4
    # step 0 - iter 5 (improve)
    ...
    ...
    # consistency check
    python data_gen\history_turn_consistent.py --task total_task --turn_id 0 --iter_id 30
    python data_gen\history_turn_consistent_extract.py --task total_task --turn_id 0 --iter_id 30

# step 1
    python data_gen\history_turn.py --task total_task --turn_id 1 --input_dir data_gen\output\total_task\history\turn_0\dialogue_i-30_consistent_extracted.jsonl
    ...
```