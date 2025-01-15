import gradio as gr

# Password for the app
PASSWORD = "Newforest1!"

# Function to authenticate users
def authenticate(password):
    if password == PASSWORD:
        return "Access Granted! Please reload the page to use the app."
    else:
        return "Access Denied: Incorrect Password."

# Main app logic
def simple_app(name):
    return f"Hello, {name}!"

# Password-protected Gradio interface
with gr.Blocks() as demo:
    with gr.Row():
        password_input = gr.Textbox(label="Enter Password", type="password")
        auth_output = gr.Textbox(label="Authentication Status", interactive=False)
        password_input.submit(authenticate, inputs=password_input, outputs=auth_output)

    # Main app interface shown after authentication
    with gr.Row(visible=False) as main_app:
        name_input = gr.Textbox(label="Enter your name")
        greet_output = gr.Textbox(label="Greeting")
        name_input.submit(simple_app, inputs=name_input, outputs=greet_output)

    # Logic to switch between password screen and app
    def switch_to_main(auth_message):
        return auth_message == "Access Granted! Please reload the page to use the app.", gr.update(visible=True)

    auth_output.change(switch_to_main, inputs=auth_output, outputs=main_app)

demo.launch(debug=True, share=True)
