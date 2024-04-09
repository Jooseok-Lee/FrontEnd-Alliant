import streamlit as st
from PIL import Image
import base64
import io
from streamlit_chat import message as st_message
from transformers import BlenderbotTokenizer
from transformers import BlenderbotForConditionalGeneration
import os
import fitz  # PyMuPDF
import re

st.markdown("""
    <style>
        .intrologo {
            position: absolute;
            top: -5px;
            left: -350px;
            width: 1200px;
            height: 750px;
            border: none; /* This removes the border */
        }
    </style>
""", unsafe_allow_html=True)

img = Image.open("C:\\Users\\Debrup Basu\\Downloads\\Group 253.png")
img = img.convert("RGB")
image_bytes = io.BytesIO()
img.save(image_bytes, format="JPEG")
image_base64 = base64.b64encode(image_bytes.getvalue()).decode()
# Create a container for the main content and logo
main_content_container = st.empty()
main_content_container.markdown(f'<img class="intrologo" src="data:image/jpg;base64,{image_base64}">', unsafe_allow_html=True)

@st.cache(hash_funcs={re.Pattern: lambda _: None})
def get_models():
    model_name = "facebook/blenderbot-400M-distill"
    tokenizer = BlenderbotTokenizer.from_pretrained(model_name)
    model = BlenderbotForConditionalGeneration.from_pretrained(model_name)
    return tokenizer, model

if "history" not in st.session_state:
    st.session_state.history = []

st.title("Ask Patrick, Your Friendly Underwriter from Georgia!")

def process_pdf(uploaded_file):
    pdf_text = ""
    try:
        # Save the uploaded file to a temporary location
        temp_file_path = os.path.join("C:\\Users\\Debrup Basu\\Downloads", uploaded_file.name)
        with open(temp_file_path, "wb") as temp_file:
            temp_file.write(uploaded_file.getvalue())

        # Open the saved PDF file
        pdf_document = fitz.open(temp_file_path)

        # Iterate over each page in the PDF
        for page_num in range(len(pdf_document)):
            page = pdf_document.load_page(page_num)
            pdf_text += page.get_text()

        # Close the PDF file
        pdf_document.close()

        # Remove the temporary file
        os.remove(temp_file_path)
    except Exception as e:
        st.error(f"Error processing PDF file: {e}")
    
    return pdf_text

def generate_answer():
    tokenizer, model = get_models()
    user_message = st.session_state.input_text
    pdf_text = st.session_state.pdf_text

    combined_message = user_message.strip() + " " + pdf_text.strip() if pdf_text else user_message.strip()

    inputs = tokenizer(combined_message, return_tensors="pt")
    result = model.generate(**inputs)
    message_bot = tokenizer.decode(result[0], skip_special_tokens=True)

    st.session_state.history.append({"message": user_message, "is_user": True})
    st.session_state.history.append({"message": message_bot, "is_user": False})

uploaded_file = st.file_uploader("Upload PDF file", type=['pdf'])

if uploaded_file is not None:
    # Process the PDF file here
    pdf_text = process_pdf(uploaded_file)  # You need to implement the process_pdf function
    st.session_state.pdf_text = pdf_text

st.text_input("", key="input_text", on_change=generate_answer)

for i, chat in enumerate(st.session_state.history):
    st_message(**chat, key=str(i)) #unpacking
