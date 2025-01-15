import gradio as gr

def simple_app(name):
    return f"Hello, {name}!"
demo = gr.Interface(fn=simple_app, inputs="text", outputs="text")
demo.launch(debug=True, share=True)
