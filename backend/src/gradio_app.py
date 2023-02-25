import gradio as gr

from SearchGPTService import SearchGPTService


def query_and_get_answer(search_text):
    search_gpt_service = SearchGPTService()
    response_text, response_text_with_footnote, source_text, data_json = search_gpt_service.query_and_get_answer(search_text)
    return response_text, response_text_with_footnote, source_text


demo = gr.Interface(fn=query_and_get_answer,
                    inputs=gr.Textbox(placeholder="What is chatgpt"),
                    outputs=["text", "text", "text"])
demo.launch()
