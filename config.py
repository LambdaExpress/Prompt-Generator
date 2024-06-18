import json
import os
from typing import List
os.environ["CUDA_PATH"] = r"C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.2"
os.environ["TRANSFORMERS_CACHE"] = f"{os.getcwd()}/.cache"
from llama_cpp import LlamaTokenizer
import torch
from transformers import GenerationConfig, PreTrainedModel, PreTrainedTokenizerBase
from transformers import LlamaForCausalLM, LlamaTokenizer
class Rating:
    safe = 'safe'
    sensitive = 'sensitive'
    nsfw = 'nsfw'
    nsfw_explicit = 'nsfw, explicit'
    
class TargetLength:
    very_short = 'very_short'
    short = 'short'
    long = 'long'
    very_long = 'very_long'
class Config:
    _instance = None

    rating : str = Rating.safe
    artist : str = ''
    characters : str = ''
    copyrights_series : str = ''
    target_length : str = TargetLength.long             #这里是让LLM以为的输出长度
    special_tags : List[str] = ['1girl']        # n girls ... n boys ... n others ...
    width : int = 1024
    height : int = 1024
    tag_black_list : str = ''
    escape_bracket : bool = False
    temperature : float = 1.35
    model : str = 'KBlueLeaf/DanTagGen-gamma'
    len_target : int = 40                #这里影响的是实际输出长度
    loop_count : int = 1
    save_path : str = 'prompt/prompt.txt'
    save_rule : List[str] = ['characters', 'artist', 'general']
    general : str = ''
    negative_prompt : str = ''
    count_per_prompt : int = 1
    prompt_width : int = 1024
    prompt_height : int = 1024
    pre_prompt : str = ''


    model_paths : List[str] = ["KBlueLeaf/DanTagGen-gamma"]
    DEVICE : str = "cuda" if torch.cuda.is_available() else "cpu"
    models = {
    model_path: [
        LlamaForCausalLM.from_pretrained(
            model_path, attn_implementation="flash_attention_2"
        )
        .requires_grad_(False)
        .eval()
        .half()
        .to("cuda" if torch.cuda.is_available() else "cpu"),
        LlamaTokenizer.from_pretrained(model_path),
    ]
    for model_path in model_paths
    }
    def save(self):
        config_dict = {
            'rating': self.rating,
            'artist': self.artist,
            'characters': self.characters,
            'copyrights_series': self.copyrights_series,
            'general': self.general,
            'target_length': self.target_length,
            'special_tags': self.special_tags,
            'width': self.width,
            'height': self.height,
            'tag_black_list': self.tag_black_list,
            'escape_bracket': self.escape_bracket,
            'temperature': self.temperature,
            'model': self.model,
            'len_target': self.len_target,
            'loop_count': self.loop_count,
            'save_path': self.save_path,
            'save_rule': self.save_rule,
            'model_paths' : self.model_paths,
            'negative_prompt' : self.negative_prompt,
            'count_per_prompt' : self.count_per_prompt,
            'prompt_width' : self.prompt_width,
            'prompt_height' : self.prompt_height,
            'pre_prompt' : self.pre_prompt,
        }
        with open('config.json', 'w') as f:
            json.dump(config_dict, f)
    def load(self):
        with open('config.json', 'r') as f:
            config_dict = json.load(f)
        for key, value in config_dict.items():
            setattr(self, key, value)
    def __init__(self):
        try:
            self.load()
        except FileNotFoundError:
            pass
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Config, cls).__new__(cls, *args, **kwargs)
        return cls._instance