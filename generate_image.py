import base64
import os
import random
import time
import zipfile
import requests
from tqdm import tqdm
from datetime import datetime

def get_file_base64(path):
    with open(path, 'rb') as image_file:
        image_data = image_file.read()
        base64_encoded_data = base64.b64encode(image_data)
    return base64_encoded_data.decode('utf-8')
def get_api_token():
    with open('api_token.txt', 'r') as f:
        return f.read().split('\n')[0]
headers = {
    "Accept": "*/*",
    "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
    "Accept-Encoding": "gzip, deflate, br",
    "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0',
    "Authorization": f"Bearer {get_api_token()}",
    "Content-Type": "application/json",
    "Origin": "https://novelai.net",
    "Referer": "https://novelai.net/",
}
url = 'https://image.novelai.net/ai/generate-image'

def generate_and_save_image(prompts, negative_prompt, count_per_prompt, width, height):
    payload = {
        "input": None,
        "model": "nai-diffusion-3",
        "action": "generate",
        "parameters": {
            "params_version": 1,
            "width": width,
            "height": height,
            "scale": 5,
            "sampler": "k_euler",
            "steps": 28,
            "n_samples": 1,
            "ucPreset": 0,
            "qualityToggle": True,
            "sm": False,
            "sm_dyn": False,
            "dynamic_thresholding": False,
            "controlnet_strength": 1,
            "legacy": False,
            "add_original_image": True,
            "uncond_scale": 1,
            "cfg_rescale": 0,
            "noise_schedule": "native",
            "legacy_v3_extend": False,
            "seed": None,
            "negative_prompt": negative_prompt,
            "reference_image_multiple": [],
            "reference_information_extracted_multiple": [],
            "reference_strength_multiple": []
        }
    }
    for prompt in tqdm(prompts):
        for i in tqdm(range(count_per_prompt), leave=False):
            payload["parameters"]["seed"] = random.randint(0, 9999999999)
            payload["input"] = prompt
            try:
                response = requests.post(url, headers=headers, json=payload)
                with open('test.zip', 'wb') as f:
                    f.write(response.content)
                with zipfile.ZipFile('test.zip', 'r') as zip_ref:
                    zip_ref.extractall(f'image/')
                now = datetime.now()
                formatted_date_time = now.strftime("%Y%m%d_%H%M%S")
                os.rename('image/image_0.png', f'image/{formatted_date_time}.png')
                yield f'image/{formatted_date_time}.png'
            except Exception as e:
                print(e)

            finally:
                if os.path.exists('test.zip'):
                    os.remove("test.zip")