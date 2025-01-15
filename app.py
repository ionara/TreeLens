import google.generativeai as genai
from pathlib import Path
import gradio as gr
from dotenv import load_dotenv
import os
import logging
from PIL import Image

# Configure logging for debugging
logging.basicConfig(level=logging.DEBUG)

# Load environment variables from a .env file
load_dotenv()

# Configure the GenerativeAI API key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Set up the model configuration for text generation
generation_config = {
    "temperature": 0.4,
    "top_p": 1,
    "top_k": 32,
    "max_output_tokens": 4096,
}

# Define safety settings for content generation
safety_settings = [
    {"category": f"HARM_CATEGORY_{category}", "threshold": "BLOCK_MEDIUM_AND_ABOVE"}
    for category in ["HARASSMENT", "HATE_SPEECH", "SEXUALLY_EXPLICIT", "DANGEROUS_CONTENT"]
]

# Initialize the GenerativeModel with the specified configuration
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
    safety_settings=safety_settings,
)

# Convert image to JPEG format (if not already JPEG)
def convert_image_to_jpeg(file_path):
    try:
        img = Image.open(file_path)
        jpeg_path = file_path.rsplit(".", 1)[0] + ".jpg"
        img = img.convert("RGB")  # Ensure it's in RGB mode
        img.save(jpeg_path, format="JPEG")
        logging.debug(f"Image converted to JPEG: {jpeg_path}")
        return jpeg_path
    except Exception as e:
        logging.error(f"Error converting image to JPEG: {e}")
        raise e

# Function to read image data from a file path
def read_image_data(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    # Check MIME type of the file
    import mimetypes
    mime_type, _ = mimetypes.guess_type(file_path)
    if mime_type not in ["image/jpeg", "image/png"]:
        raise ValueError(f"Unsupported image type: {mime_type}")

    with open(file_path, "rb") as f:
        image_data = f.read()
    
    logging.debug(f"Image MIME type: {mime_type}, Size: {len(image_data)} bytes")
    
    return {"mime_type": mime_type, "data": image_data}

# Function to generate a response based on a prompt and an image
def generate_gemini_response(prompt, image_path):
    logging.debug(f"Generating response for {image_path}")
    image_data = read_image_data(image_path)
    try:
        response = model.generate_content([prompt, image_data])
        logging.debug(f"Model response: {response.text}")
        return response.text
    except Exception as e:
        logging.error(f"Error during response generation: {e}")
        raise e

# Initial input prompt for the plant pathologist
input_prompt = """
As a highly skilled plant pathologist, your expertise is indispensable in our pursuit of maintaining optimal plant health...
"""
# input_prompt = """
# Como um patologista de plantas altamente qualificado, sua experiência é indispensável em nossa busca para manter a saúde ótima das plantas...
# """
# Function to process uploaded files and generate a response
def process_uploaded_files(file):
    if not file:
        return None, "No file uploaded."
    # Save the uploaded file locally
    file_path = file.name

    # Convert the file to JPEG (if necessary)
    try:
        if not file_path.endswith(".jpg") and not file_path.endswith(".jpeg"):
            file_path = convert_image_to_jpeg(file_path)

        # Generate a response
        response = generate_gemini_response(input_prompt, file_path)
    except Exception as e:
        logging.error(f"Error during response generation: {e}")
        return file_path, f"Error: {e}"

    return file_path, response

# Password-protected Gradio interface
PASSWORD = "Newforest1!"  # Replace with your desired password

# Authentication function
def authenticate(password):
    if password == PASSWORD:
        return gr.update(visible=True), gr.update(value="Access Granted!")
    else:
        return gr.update(visible=False), gr.update(value="Access Denied: Incorrect Password.")

# Gradio interface setup
with gr.Blocks() as demo:
    # Password input and status row
    with gr.Row():
        password_input = gr.Textbox(label="Enter Password", type="password", interactive=True)
        auth_status = gr.Textbox(label="Authentication Status", interactive=False)

    # Main app (hidden by default)
    with gr.Column(visible=False) as main_app:
        image_input = gr.File(file_types=["image"], label="Upload an Image")
        file_output = gr.Textbox(label="File Path")
        response_output = gr.Textbox(label="Analysis Result")

        # File upload and processing
        image_input.change(
            process_uploaded_files,
            inputs=image_input,
            outputs=[file_output, response_output],
        )

    # Bind password submission to authentication
    password_input.submit(
        authenticate,
        inputs=password_input,
        outputs=[main_app, auth_status]
    )

# Launch the app
demo.launch(debug=True, share=True)
