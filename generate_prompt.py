import json
import os
from typing import Any, Dict, List
from contextlib import nullcontext
from random import shuffle
from tqdm import tqdm
import torch
from llama_cpp import Llama
from transformers import GenerationConfig, PreTrainedModel, PreTrainedTokenizerBase
from transformers import LlamaForCausalLM, LlamaTokenizer
os.environ["CUDA_PATH"] = r"C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.2"
os.environ["TRANSFORMERS_CACHE"] = f"{os.getcwd()}/.cache"

def generate(
    model : PreTrainedModel | Llama,
    tokenizer: PreTrainedTokenizerBase,
    prompt="",
    temperature=0.5,
    top_p=0.95,
    top_k=45,
    repetition_penalty=1.17,
    max_new_tokens=128,
    autocast_gen=lambda: torch.autocast("cpu", enabled=False),
    **kwargs,
):
    if isinstance(model, Llama):
        result = model.create_completion(
            prompt,
            temperature=temperature,
            top_p=top_p,
            top_k=top_k,
            max_tokens=max_new_tokens,
            repeat_penalty=repetition_penalty or 1,
        )
        return prompt + result["choices"][0]["text"]

    torch.cuda.empty_cache()
    inputs = tokenizer(prompt, return_tensors="pt")
    input_ids = inputs["input_ids"].to(next(model.parameters()).device)
    generation_config = GenerationConfig(
        temperature=temperature,
        top_p=top_p,
        top_k=top_k,
        repetition_penalty=repetition_penalty,
        do_sample=True,
        **kwargs,
    )
    with torch.no_grad(), autocast_gen():
        generation_output = model.generate(
            input_ids=input_ids,
            generation_config=generation_config,
            return_dict_in_generate=True,
            output_scores=True,
            max_new_tokens=max_new_tokens,
        )
    s = generation_output.sequences[0]
    output = tokenizer.decode(s)

    torch.cuda.empty_cache()
    return output


def tag_gen(
    text_model,
    tokenizer,
    prompt,
    prompt_tags,
    len_target,
    black_list,
    temperature=0.5,
    top_p=0.95,
    top_k=100,
    max_new_tokens=256,
    max_retry=5,
):
    prev_len = 0
    retry = max_retry
    llm_gen = ""

    while True:
        llm_gen = generate(
            model=text_model,
            tokenizer=tokenizer,
            prompt=prompt,
            temperature=temperature,
            top_p=top_p,
            top_k=top_k,
            repetition_penalty=None,
            max_new_tokens=max_new_tokens,
            stream_output=False,
            autocast_gen=lambda: (
                torch.autocast("cuda") if torch.cuda.is_available() else nullcontext()
            ),
            prompt_lookup_num_tokens=10,
            pad_token_id=tokenizer.eos_token_id,
            eos_token_id=tokenizer.eos_token_id,
        )
        llm_gen = llm_gen.replace("</s>", "").replace("<s>", "")
        extra = llm_gen.split("<|input_end|>")[-1].strip().strip(",")
        extra_tokens = list(
            set(
                [
                    tok.strip()
                    for tok in extra.split(",")
                    if tok.strip() not in black_list
                ]
            )
        )
        llm_gen = llm_gen.replace(extra, ", ".join(extra_tokens))

        yield llm_gen, extra_tokens

        if len(prompt_tags) + len(extra_tokens) < len_target:
            if len(extra_tokens) == prev_len and prev_len > 0:
                if retry < 0:
                    break
                retry -= 1
            shuffle(extra_tokens)
            retry = max_retry
            prev_len = len(extra_tokens)
            prompt = llm_gen.strip().replace("  <|", " <|")
        else:
            break
    yield llm_gen, extra_tokens

def get_prompt(    
    text_model: LlamaForCausalLM,
    tokenizer: LlamaTokenizer,
    rating: str = "",
    artist: str = "",
    characters: str = "",
    copyrights: str = "",
    target: str = "long",
    len_target : int = 40,
    special_tags: List[str] = ["1girl"],
    general: str = "",
    aspect_ratio: float = 0.0,
    blacklist: str = "",
    escape_bracket: bool = False,
    temperature: float = 1.35,):
    prompt = f"""
    rating: {rating or '<|empty|>'}
    artist: {artist.strip() or '<|empty|>'}
    characters: {characters.strip() or '<|empty|>'}
    copyrights: {copyrights.strip() or '<|empty|>'}
    aspect ratio: {f"{aspect_ratio:.1f}" or '<|empty|>'}
    target: {'<|' + target + '|>' if target else '<|long|>'}
    general: {", ".join(special_tags)}, {general.strip().strip(",")}<|input_end|>
    """.strip()
    prompt_tags = special_tags + general.strip().strip(",").split(",")
    black_list = set(
        [tag.strip().replace("_", " ") for tag in blacklist.strip().split(",")]
    )
    for llm_gen, extra_tokens in tag_gen(
        text_model,
        tokenizer,
        prompt,
        prompt_tags,
        len_target,
        black_list,
        temperature=temperature,
        top_p=0.95,
        top_k=100,
        max_new_tokens=256,
        max_retry=5):
        print(llm_gen)
    if escape_bracket:
        llm_gen = llm_gen.replace("[", "\\[").replace("]", "\\]").replace("(", "\\(").replace(")", "\\)")
    return llm_gen
def convert_text_to_dict(text : str):
    lines = [line.strip().replace('  <|empty|>', '') for line in text.split('\n')]
    data : Dict[str, str] = {}
    for line in lines:
        if ':' in line:
            key, value = line.split(':', 1)
            data[key.strip()] = value.strip()
        else:
            data['general'] = f"{data['general']}{line.strip()}"
    data['general'] = data['general'].replace('  <|input_end|>', '')
    return data

def save_prompt(path : str, prompt : Dict[str, str], save_rule : List[str]):
    if not os.path.exists(os.path.dirname(path)):
        os.mkdir(os.path.dirname(path))
    with open(path, 'a', encoding='utf-8') as f:
        rule = ''
        for i in save_rule:
            if prompt[i] != '':
                rule += f'{prompt[i]}, '
        rule = rule[:-2] + '\n'
        f.write(rule)