import numpy as np
import pandas as pd
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
import openai
import textwrap
from transformers import BartTokenizer, BartForConditionalGeneration

from AMU_module import embedding as ed
from AMU_module import semantic_search as ss
from AMU_module import llm_generation as lg
from AMU_module import summarize as su

os.environ['KMP_DUPLICATE_LIB_OK']='True' # Handling Error #15: Initializing libomp.dylib, but found libiomp5.dylib already initialized.

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

img = Image.open("./img/Group 253.png")
img = img.convert("RGB")
image_bytes = io.BytesIO()
img.save(image_bytes, format="JPEG")
image_base64 = base64.b64encode(image_bytes.getvalue()).decode()
# Create a container for the main content and logo
main_content_container = st.empty()
main_content_container.markdown(f'<img class="intrologo" src="data:image/jpg;base64,{image_base64}">', unsafe_allow_html=True)

# OpenAI API Key
api_key = st.secrets["OPENAI_API_KEY"] # stored in .streamlit/secrets.toml

# Setting parameters
engine = "amu-gpt35-turbo-instruct"
temperature = 1
max_tokens = 200
top_p = 0.5
frequency_penalty = 0.1
presence_penalty = 0.1
best_of = 1
batch_size = 10
params = (temperature, max_tokens, top_p, frequency_penalty, presence_penalty, best_of, batch_size)

# Max context window
max_context_window = 3500

system_msg = '''
                You are an email generator for a title insurance attorney. 
                Please craft a response to the incoming email by drawing inspiration from past inquiries and replies. 
                Ensure the reply addresses the concerns raised in the incoming email without repeating the questions. 
                Focus on providing relevant information based on past interactions to maintain coherence and avoid generating irrelevant content.
            '''

#@st.cache(hash_funcs={re.Pattern: lambda _: None})
@st.cache_resource
def get_models():
    model_name = "facebook/blenderbot-400M-distill"
    tokenizer = BlenderbotTokenizer.from_pretrained(model_name)
    model = BlenderbotForConditionalGeneration.from_pretrained(model_name)
    return tokenizer, model

if "history" not in st.session_state:
    st.session_state.history = []

if "pdf_text" not in st.session_state:
    st.session_state.pdf_text = ""

if "subject_text" not in st.session_state:
    st.session_state.subject_text = ""

st.title("Ask Patrick, Your Friendly Underwriter from Georgia!")

def process_pdf(uploaded_file):
    pdf_text = ""
    try:
        # Save the uploaded file to a temporary location
        temp_file_path = os.path.join("./", uploaded_file.name)
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
    # Get text
    body_text = st.session_state.input_text.strip()
    pdf_text = st.session_state.pdf_text.strip()
    subject_text = st.session_state.subject_text.strip()
    
    # Set default value if a given text is empty
    body_text = "No Bodys" if len(body_text)==0 or body_text is None else body_text
    pdf_text = "No Attachments" if len(pdf_text)==0 or pdf_text is None else pdf_text
    subject_text = "No Subjects" if len(subject_text)==0 or subject_text is None else subject_text

    print(len(pdf_text))

    if len(pdf_text)>max_context_window: # If the length of pdf is too long
        print('Summarize pdf')
        print('Before: ' + str(len(pdf_text)))
        pdf_text = su.summarize(pdf_text)
        print('After: ' + str(len(pdf_text)))


    # Trasform text into its embedding representation
    body_emb = ed.embedding(body_text, api_key)
    pdf_emb = ed.embedding(pdf_text, api_key)
    subject_emb = ed.embedding(subject_text, api_key)

    # Retrieve similar email idxes
    sim_idx, sim_subject, sim_body, sim_attachment, sim_response = ss.semantic_search_module('data/embedding_results_v3.csv', subject_emb, body_emb, pdf_emb, K=1)
    
    # LLM generation
    incoming_email = (subject_text, body_text, pdf_text)
    augmented_example = (sim_subject, sim_body, sim_attachment, sim_response)
    llm_result = lg.LLM_generation(engine, params, incoming_email, augmented_example, system_msg, api_key)

    st.session_state.history.append({"message": llm_result, "is_user": False})

uploaded_file = st.file_uploader("Upload PDF file", type=['pdf'])

if uploaded_file is not None:
    # Process the PDF file here
    pdf_text = process_pdf(uploaded_file)  # You need to implement the process_pdf function
    st.session_state.pdf_text = pdf_text

st.text_input("Enter the subject of your message here", max_chars=100, key="subject_text")
st.text_area("Enter your message body here", height=200, key="input_text", on_change=generate_answer)

for i, chat in enumerate(st.session_state.history):
    st_message(**chat, key=str(i)) #unpacking
