import os
os.environ["CUDA_PATH"] = r"C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.2"
os.environ["TRANSFORMERS_CACHE"] = f"{os.getcwd()}/.cache"
from llama_cpp import LlamaTokenizer
import torch
from transformers import GenerationConfig, PreTrainedModel, PreTrainedTokenizerBase
from transformers import LlamaForCausalLM, LlamaTokenizer
os.environ["CUDA_PATH"] = r"C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.2"
os.environ["TRANSFORMERS_CACHE"] = f"{os.getcwd()}/.cache"
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

rating = Rating.nsfw_explicit
artist = r''
characters = 'plana_(blue_archive)'
copyrights_series = ''
target_length = TargetLength.long #这里是让LLM以为的输出长度
special_tags = ['1girl'] # n girls ... n boys ... n others ...
tags = 'masturbation, pussy, pussy juice'
width = 1024
height = 1024
tag_black_list = 'tag_black_list'
escape_bracket = False
temperature = 1.35
model = 'KBlueLeaf/DanTagGen-gamma'
len_target = 40 #这里影响的是实际输出长度
aspect_ratio = 0.0
loop_count = 3
save_path = 'prompt/test.txt'
save_rule = ["characters","artist","general"]
MODEL_PATHS = ["KBlueLeaf/DanTagGen-gamma"]
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
models = {
model_path: [
    LlamaForCausalLM.from_pretrained(
        model_path, attn_implementation="flash_attention_2"
    )
    .requires_grad_(False)
    .eval()
    .half()
    .to(DEVICE),
    LlamaTokenizer.from_pretrained(model_path),
]
for model_path in MODEL_PATHS
}