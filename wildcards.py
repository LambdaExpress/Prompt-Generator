import re
import os
import random
from typing import Dict, List
def dict_wildcard_match(prompt : str, prompt_dict : Dict[str, str]):
    pattern = re.compile(r'<<(.*?)>>')
    matches = re.findall(pattern, prompt)
    for match in matches:
        text = prompt_dict[match]
        prompt = prompt.replace(f'<<{match}>>', text)
    return prompt
def wildcard_match(prompt : str, dir_path : str):
    pattern = re.compile(r'<(.*?)>')
    matches = re.findall(pattern, prompt)
    for match in matches:
        with open(f'{os.path.join(dir_path, match)}.txt', 'r') as f:
            text = f.read().strip().split('\n')
        text = random.choice(text)
        prompt = prompt.replace(f'<{match}>', text)
    return prompt
if __name__ == '__main__':
    p = wildcard_match("1girl, <general>, <artist>, somewords", 'suzuran', 'wildcards')
    print(p)