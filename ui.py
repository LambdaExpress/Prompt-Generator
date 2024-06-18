import gradio as gr
from config import Config
from metainfo import SAVERULE, SPECIAL
from generate_prompt import get_prompt, convert_text_to_dict, save_prompt
from tqdm import tqdm

is_cancel = False
config_instance = Config()

def main():
    with gr.Blocks(theme=gr.themes.Soft()) as demo:
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
                        characters = gr.Textbox(label="Characters", value=config_instance.characters)
                        copyrights = gr.Textbox(label="Copyrights(Series)", value=config_instance.copyrights_series)
                        artist = gr.Textbox(label="Artist", value=config_instance.artist)
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
                        general = gr.TextArea(label="Input your general tags", lines=6, value=config_instance.general)
                        black_list = gr.TextArea(
                            label="tag Black list (seperated by comma)", lines=5,
                            value=config_instance.tag_black_list
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
                submit = gr.Button("Submit")
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
                    formated_result = gr.TextArea(
                        label="Final output", lines=14, show_copy_button=True,
                        max_lines = 14,
                    )
                    count = gr.Markdown()
                save_settings = gr.Button("Save Settings")
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
                black_list,
                escape_bracket,
                temperature,
                loop_count,
                save_path,
                save_rule,
            ],
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
                width,
                height,
                black_list,
                escape_bracket,
                temperature,
                loop_count,
                save_path,
                save_rule,
            ],
            outputs=[
                formated_result,
                count
            ],
            show_progress=True,
        )
    demo.launch()
def _save_settings(rating, 
                   artist, 
                   characters, 
                   copyrights, 
                   target, 
                   len_target, 
                   special_tags, 
                   general, 
                   width, 
                   height, 
                   black_list, 
                   escape_bracket,
                   temperature,
                   loop_count,
                   save_path,
                   save_rule
                   ):
    config_instance.rating = rating
    config_instance.artist = artist
    config_instance.characters = characters
    config_instance.copyrights_series = copyrights
    config_instance.target_length = target
    config_instance.len_target = len_target
    config_instance.special_tags = special_tags
    config_instance.general = general
    config_instance.width = width
    config_instance.height = height
    config_instance.tag_black_list = black_list
    config_instance.escape_bracket = escape_bracket
    config_instance.temperature = temperature
    config_instance.loop_count = loop_count
    config_instance.save_path = save_path
    config_instance.save_rule = save_rule
    config_instance.save()

def set_cancel(state : bool = True):
    global is_cancel
    is_cancel = state
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
                black_list,
                escape_bracket,
                temperature,
                loop_count,
                save_path,
                save_rule,):
    try:
        text_model, tokenizer = config_instance.models[model]
        for i in tqdm(range(1, loop_count + 1)):
            if is_cancel:
                raise Exception('Cancellation Initiated by User')
            prompt = get_prompt(text_model, tokenizer, rating, artist, characters, copyrights, target, len_target, special_tags, general, width / height, black_list, escape_bracket, temperature)
            if is_cancel:
                raise Exception('Cancellation Initiated by User')
            prompt = convert_text_to_dict(prompt)
            if is_cancel:
                raise Exception('Cancellation Initiated by User')
            prompt = save_prompt(save_path, prompt, save_rule)
            if is_cancel:
                raise Exception('Cancellation Initiated by User')
            yield prompt, f'**Completed: {i} / {loop_count}**'
    except Exception as e:
        yield f'Error\nException: {e}', f'**Completed: {i} / {loop_count}**'
    finally:
        set_cancel(False)
    
if __name__ == '__main__':
    main()