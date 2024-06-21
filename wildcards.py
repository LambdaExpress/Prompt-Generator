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
def wildcard_match(prompt : str, dir_path : str, general : str = None):
    pattern = re.compile(r'<(.*?)>')
    matches = re.findall(pattern, prompt)
    for match in matches:
        if match == 'general':
            if general == None:
                raise Exception('general must be specified')
            text = general
        else:
            with open(f'{os.path.join(dir_path, match)}.txt', 'r') as f:
                text = f.read().strip().split('\n')
            text = random.choice(text)
        prompt = prompt.replace(f'<{match}>', text)
    return prompt
def wildcards_match(prompts : List[str], dir_path : str, general : str = None):
    result = []
    for prompt in prompts:
        prompt = wildcard_match(prompt, dir_path, general)
        result.append(prompt)
    return result
if __name__ == '__main__':
    p = wildcard_match("1girl, <general>, <artist>, somewords", 'suzuran', 'wildcards')
    print(p)