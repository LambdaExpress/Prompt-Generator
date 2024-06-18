
import gradio as gr
import config
from metainfo import SAVERULE, SPECIAL
from generate_prompt import get_prompt, convert_text_to_dict, save_prompt
from tqdm import tqdm

is_cancel = False

def main():
    with gr.Blocks(theme=gr.themes.Soft()) as demo:
        with gr.Row():
            with gr.Column(scale=4):
                with gr.Row():
                    with gr.Column(scale=2):
                        rating = gr.Radio(
                            ["safe", "sensitive", "nsfw", "nsfw, explicit"],
                            value=config.rating,
                            label="Rating",
                        )
                        special_tags = gr.Dropdown(
                            SPECIAL,
                            value=config.special_tags,
                            label="Special tags",
                            multiselect=True,
                        )
                        characters = gr.Textbox(label="Characters", value=config.characters)
                        copyrights = gr.Textbox(label="Copyrights(Series)", value=config.copyrights_series)
                        artist = gr.Textbox(label="Artist", value=config.artist)
                        target = gr.Radio(
                            ["very_short", "short", "long", "very_long"],
                            value=config.target_length,
                            label="Target length",
                        )
                        len_target = gr.Slider(
                            value=config.len_target,
                            minimum=20,
                            maximum=80,
                            step=10,
                            label="Len target",
                        )
                    with gr.Column(scale=2):
                        general = gr.TextArea(label="Input your general tags", lines=6)
                        black_list = gr.TextArea(
                            label="tag Black list (seperated by comma)", lines=5
                        )
                        with gr.Row():
                            width = gr.Slider(
                                value=config.width,
                                minimum=256,
                                maximum=4096,
                                step=32,
                                label="Width",
                            )
                            height = gr.Slider(
                                value=config.height,
                                minimum=256,
                                maximum=4096,
                                step=32,
                                label="Height",
                            )
                        with gr.Row():
                            temperature = gr.Slider(
                                value=config.temperature,
                                minimum=0.1,
                                maximum=2,
                                step=0.05,
                                label="Temperature",
                            )
                            escape_bracket = gr.Checkbox(
                                value=config.escape_bracket,
                                label="Escape bracket",
                            )
                        model = gr.Dropdown(
                            list(config.models.keys()),
                            value=list(config.models.keys())[-1],
                            label="Model",
                        )
                submit = gr.Button("Submit")
                cancel = gr.Button("Cancel")
            with gr.Row():
                with gr.Column(scale=3):
                    save_rule = gr.Dropdown(
                        SAVERULE,
                        value=config.save_rule,
                        label="Save Rule",
                        multiselect=True,
                    )
                    loop_count = gr.Slider(
                        value=config.loop_count,
                        minimum=1,
                        maximum=10000,
                        step=1,
                        label="Loop Count",
                    )
                    save_path = gr.Textbox(label="Save path", value=config.save_path)
                    formated_result = gr.TextArea(
                        label="Final output", lines=14, show_copy_button=True
                    )
                    progress_rate = gr.Markdown()
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
                progress_rate
            ],
            show_progress=True,
        )
    demo.launch()
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
        text_model, tokenizer = config.models[model]
        for i in tqdm(range(loop_count)):
            if is_cancel:
                raise Exception('Cancellation Initiated by User')
            prompt = get_prompt(text_model, tokenizer, rating, artist, characters, copyrights, target, len_target, special_tags, general, width / height, black_list, escape_bracket, temperature)
            if is_cancel:
                raise Exception('Cancellation Initiated by User')
            prompt = convert_text_to_dict(prompt)
            if is_cancel:
                raise Exception('Cancellation Initiated by User')
            save_prompt(save_path, prompt, save_rule)
            if is_cancel:
                raise Exception('Cancellation Initiated by User')
            yield prompt, str(i)
    except Exception as e:
        yield f'Error\nException: {e}', str(i)
    finally:
        set_cancel(False)
    
if __name__ == '__main__':
    main()