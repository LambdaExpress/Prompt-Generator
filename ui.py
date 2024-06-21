import queue
import threading
import gradio as gr
from config import Config
from metainfo import SAVERULE, SPECIAL
from generate_prompt import get_prompt, convert_text_to_dict, save_prompt
from generate_image import generate_and_save_image
from wildcards import wildcard_match, dict_wildcard_match
from tqdm import tqdm

is_cancel = False
is_cancel_image = False
config_instance = Config()
prompt_count = 0
image_count = 0
global_loop_count = 0

def main():
    with gr.Blocks(theme=gr.themes.Soft()) as demo:
        with gr.Tab("Prompt Generator"):
            with gr.Row():
                with gr.Column(scale=4):
                    with gr.Row():
                        with gr.Column(scale=2):
                            rating = gr.Radio(
                                ["safe", "sensitive", "nsfw", "nsfw, explicit"],
                                value=config_instance.rating,
                                label="Rating",
                            )
                            special_tags = gr.Dropdown(
                                SPECIAL,
                                value=config_instance.special_tags,
                                label="Special tags",
                                multiselect=True,
                            )
                            characters = gr.Textbox(label="Characters (Wildcards)", value=config_instance.characters)
                            copyrights = gr.Textbox(label="Copyrights(Series) (Wildcards)", value=config_instance.copyrights_series)
                            artist = gr.Textbox(label="Artist (Wildcards)", value=config_instance.artist)
                            target = gr.Radio(
                                ["very_short", "short", "long", "very_long"],
                                value=config_instance.target_length,
                                label="Target length",
                            )
                            len_target = gr.Slider(
                                value=config_instance.len_target,
                                minimum=20,
                                maximum=80,
                                step=10,
                                label="Len target",
                            )
                        with gr.Column(scale=2):
                            general = gr.TextArea(label="Input your general tags (Wildcards)", lines=6, value=config_instance.general)
                            tag_black_list = gr.TextArea(
                                label="tag Black list (seperated by comma)", lines=5,
                                value=config_instance.tag_black_list
                            )
                            with gr.Row():
                                prompt_width = gr.Slider(
                                    value=config_instance.prompt_width,
                                    minimum=256,
                                    maximum=4096,
                                    step=32,
                                    label="Width",
                                )
                                prompt_height = gr.Slider(
                                    value=config_instance.prompt_height,
                                    minimum=256,
                                    maximum=4096,
                                    step=32,
                                    label="Height",
                                )
                                gr.Button("Exchange").click(
                                    lambda w, h : (h, w),
                                    inputs=[
                                        prompt_width,
                                        prompt_height,
                                    ],
                                    outputs=[
                                        prompt_width,
                                        prompt_height
                                    ]
                                )
                            with gr.Row():
                                temperature = gr.Slider(
                                    value=config_instance.temperature,
                                    minimum=0.1,
                                    maximum=2,
                                    step=0.05,
                                    label="Temperature",
                                )
                                escape_bracket = gr.Checkbox(
                                    value=config_instance.escape_bracket,
                                    label="Escape bracket",
                                )
                            model = gr.Dropdown(
                                list(config_instance.models.keys()),
                                value=list(config_instance.models.keys())[-1],
                                label="Model",
                            )
                    with gr.Row():
                        submit = gr.Button("Generate Pormpt")
                        generate_all = gr.Button("Generate Prompt and Image")
                    cancel = gr.Button("Cancel")
                with gr.Row():
                    with gr.Column(scale=5):
                        save_rule = gr.Dropdown(
                            SAVERULE,
                            value=config_instance.save_rule,
                            label="Save Rule",
                            multiselect=True,
                        )
                        loop_count = gr.Slider(
                            value=config_instance.loop_count,
                            minimum=1,
                            maximum=10000,
                            step=1,
                            label="Loop Count",
                        )
                        save_path = gr.Textbox(label="Save path", value=config_instance.save_path)
                        generate_image_format = gr.TextArea(
                            value=config_instance.generate_image_format,
                            label="Generate Image Format (Wildcards)", lines=14,
                            max_lines = 14,
                            placeholder='Example: <artist>, <general>, some words...',
                        )
                        count = gr.Markdown(every=5, value=monitor_counts)
                    save_settings = gr.Button("Save Settings")
        with gr.Tab("Image Generator"):
            with gr.Row():
                with gr.Column(scale=3):
                    with gr.Row():
                        pre_prompt = gr.TextArea(label="Input Pre-Prompt (Wildcards)", max_lines=7, value=config_instance.pre_prompt)
                        prompt_file_path = gr.TextArea(label="Input file path or prompt", max_lines=7, value=config_instance.prompt_file_path)
                    negative_prompt = gr.TextArea(
                        max_lines=7, 
                        label="Negative prompt (Wildcards)", 
                        value=config_instance.negative_prompt
                    )
                    with gr.Row():
                        width = gr.Slider(
                            value=config_instance.width,
                            minimum=256,
                            maximum=4096,
                            step=32,
                            label="Width",
                        )
                        height = gr.Slider(
                            value=config_instance.height,
                            minimum=256,
                            maximum=4096,
                            step=32,
                            label="Height",
                        )
                        exchange = gr.Button("Exchange")
                        exchange.click(
                            lambda w, h: (h, w),
                            inputs=[
                                width,
                                height,
                            ],
                            outputs=[
                                width,
                                height,
                            ]
                        )
                    count_per_prompt = gr.Slider(
                        value=config_instance.count_per_prompt,
                        minimum=1,
                        maximum=100,
                        step=1,
                        label='Count per prompt'
                    )
                    generate_image = gr.Button("Generate Image")
                    cancel_image = gr.Button("Cancel")
                with gr.Column(2):
                    n = gr.Markdown()
                    save_settings_image = gr.Button("Save Settings")
        generate_all.click(
            generate_prompt_and_image,
            inputs=[
                model,
                rating,
                artist,
                characters,
                copyrights,
                target,
                len_target,
                special_tags,
                general,
                width,
                height,
                tag_black_list,
                escape_bracket,
                temperature,
                loop_count,
                save_path,
                save_rule,
                negative_prompt,
                generate_image_format,
            ],
        )
        save_settings_image.click(
            _save_settings,
            inputs=[
                rating,
                artist,
                characters,
                copyrights,
                target,
                len_target,
                special_tags,
                general,
                width,
                height,
                tag_black_list,
                escape_bracket,
                temperature,
                loop_count,
                save_path,
                save_rule,
                negative_prompt,
                count_per_prompt,
                prompt_width,
                prompt_height,
                pre_prompt,
                prompt_file_path,
                generate_image_format,
            ],
        )
        cancel_image.click(
            _set_cancel_image
        )
        save_settings.click(
            _save_settings,
            inputs=[
                rating,
                artist,
                characters,
                copyrights,
                target,
                len_target,
                special_tags,
                general,
                width,
                height,
                tag_black_list,
                escape_bracket,
                temperature,
                loop_count,
                save_path,
                save_rule,
                negative_prompt,
                count_per_prompt,
                prompt_width,
                prompt_height,
                pre_prompt,
                prompt_file_path,
                generate_image_format,
            ],
        )
        generate_image.click(
            _generate_image,
            inputs=[
                prompt_file_path,
                negative_prompt,
                count_per_prompt,
                width,
                height,
                pre_prompt,
            ],
            outputs=[
                n,
            ]
        )
        cancel.click(
            set_cancel
        )
        submit.click(
            generate,
            inputs=[
                model,
                rating,
                artist,
                characters,
                copyrights,
                target,
                len_target,
                special_tags,
                general,
                prompt_width,
                prompt_height,
                tag_black_list,
                escape_bracket,
                temperature,
                loop_count,
                save_path,
                save_rule,
            ],
            outputs=[
                count
            ],
            show_progress=True,
        )
    demo.launch()
def monitor_counts():
    if image_count >= 0:
     return f"**Completed: {prompt_count} / {global_loop_count}\nImage = {image_count} / {global_loop_count}**"
    else:
        return f"**Completed: {prompt_count} / {global_loop_count}**"
def _set_cancel_image(state = True):
    global is_cancel_image
    is_cancel_image = state
def _generate_image(prompt_file_path : str, negative_prompt : str, count_per_prompt : int, width : int, height : int, pre_prompt : str):
    n = 1
    try:
        with open(prompt_file_path, 'r') as f:
            prompts = f.read().split('\n')
        if prompts[-1] == '':
            prompts = prompts[:-1]
    except:
        prompts = [prompt_file_path]
    pre_prompt = pre_prompt.strip()
    if pre_prompt.endswith(','):
        pre_prompt = pre_prompt[:-1]
    if pre_prompt != '':
        temp = [wildcard_match(pre_prompt, "wildcards", general) for general in prompts]
        prompts = temp
    try:
        for _ in generate_and_save_image(prompts, negative_prompt, count_per_prompt, width, height):
            if is_cancel_image:
                raise Exception('Cancellation Initiated by User') 
            yield f'**Completed: {n} / {len(count_per_prompt*prompts)}**'
            n += 1
    except Exception as e:
        yield f'Error\nException: {e}'
    finally:
        _set_cancel_image(False)

def _save_settings(*args):
    keys = [
        'rating',
        'artist',
        'characters',
        'copyrights',
        'target',
        'len_target',
        'special_tags',
        'general',
        'width',
        'height',
        'tag_black_list',
        'escape_bracket',
        'temperature',
        'loop_count',
        'save_path',
        'save_rule',
        'negative_prompt',
        'count_per_prompt',
        'prompt_width',
        'prompt_height',
        'pre_prompt',
        'prompt_file_path',
        'generate_image_format',
    ]
    kwargs = dict(zip(keys, args))
    for key, value in kwargs.items():
        setattr(config_instance, key, value)
    config_instance.save()

def set_cancel(state : bool = True):
    global is_cancel
    is_cancel = state
def check_cancellation():
    global is_cancel
    if is_cancel:
        raise Exception('Operation cancelled by user')
def generate_prompt_and_image(model,
             rating,
             artist,
             characters,
             copyrights,
             target,
             len_target,
             special_tags,
             general,
             width,
             height,
             tag_black_list,
             escape_bracket,
             temperature,
             loop_count,
             save_path,
             save_rule,
             negative_prompt,
             generate_image_format):
    prompt_queue = queue.Queue()
    global global_loop_count, prompt_count, image_count
    global_loop_count = loop_count
    prompt_count = image_count = 0
    def producer(model, rating, artist, characters, copyrights, target, len_target, special_tags, general, width, height, tag_black_list, escape_bracket, temperature, loop_count, save_path, save_rule):
        try:
            text_model, tokenizer = config_instance.models[model]
            for i in range(1, loop_count + 1):
                check_cancellation()

                artist = wildcard_match(artist, 'wildcards')
                characters = wildcard_match(characters, 'wildcards')
                copyrights = wildcard_match(copyrights, 'wildcards')
                general = wildcard_match(general, 'wildcards')

                prompt = get_prompt(text_model, tokenizer, rating, artist, characters, copyrights, target, len_target, special_tags, general, width / height, tag_black_list, escape_bracket, temperature)
                prompt_dict = convert_text_to_dict(prompt)
                prompt = save_prompt(save_path, prompt_dict, save_rule)
                prompt_queue.put((prompt, prompt_dict))
                global prompt_count, image_count
                prompt_count = prompt_count + 1
            raise Exception("Mission Completed")
        except Exception as e:
            prompt_queue.put(e)
    def consumer(width, height, negative_prompt, generate_image_format):
        while True:
            item = prompt_queue.get()
            if item is None:
                break
            try:
                prompt, prompt_dict = item
                negative_prompt = wildcard_match(negative_prompt, "wildcards")
                generate_image_format = dict_wildcard_match(generate_image_format, prompt_dict)
                check_cancellation()
                if isinstance(prompt, Exception):
                    raise prompt
                for path in _generate_image(prompt, negative_prompt, 1, width, height, generate_image_format):
                    pass
                global image_count, prompt_count
                image_count = image_count + 1
            except Exception as e:
                raise Exception(f'Error\nException: {e}')
            finally:
                prompt_queue.task_done()
    producer_thread = threading.Thread(target=producer, args=(model, rating, artist, characters, copyrights, target, len_target, special_tags, general, width, height, tag_black_list, escape_bracket, temperature, loop_count, save_path, save_rule))
    consumer_thread = threading.Thread(target=consumer, args=(width, height, negative_prompt, generate_image_format))
    
    producer_thread.start()
    consumer_thread.start()

    prompt_queue.join()
    consumer_thread.join()
    prompt_count = image_count = 0
def generate(model,
             rating,
             artist,
             characters,
             copyrights,
             target,
             len_target,
             special_tags,
             general,
             width,
             height,
             tag_black_list,
             escape_bracket,
             temperature,
             loop_count,
             save_path,
             save_rule,):
    global image_count
    image_count = -1
    try:
        text_model, tokenizer = config_instance.models[model]
        for i in tqdm(range(1, loop_count + 1)):
            check_cancellation()
            prompt = get_prompt(text_model, tokenizer, rating, artist, characters, copyrights, target, len_target, special_tags, general, width / height, tag_black_list, escape_bracket, temperature)
            
            check_cancellation()
            prompt = convert_text_to_dict(prompt)
            check_cancellation()
            prompt = save_prompt(save_path, prompt, save_rule)
            yield f'**Completed: {i} / {loop_count}**'
    except Exception as e:
        yield f'**Completed: {i} / {loop_count}**'
    finally:
        set_cancel(False)
    
if __name__ == '__main__':
    main()