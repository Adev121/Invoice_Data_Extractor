import requests
import json
import os
from dotenv import load_dotenv
import streamlit as st
import base64
import PyPDF2

load_dotenv()

# Function to extract text from PDF
def pdf_to_text(uploaded_file):
    pdf_reader = PyPDF2.PdfReader(uploaded_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() or ""
    return text

# Function to call OpenRouter API
def extract_invoice_data(pdf_text):
    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
            "Content-Type": "application/json"
        },
        data=json.dumps({
            "model": "deepseek/deepseek-chat-v3.1:free",  # You can change model
            "messages": [
                {
                    "role": "user",
                    "content": f"Extract all necessary invoice information from this text return in key value format :\n\n{pdf_text}"
                }
            ]
        })
    )

    data = response.json()
    extracted = data['choices'][0]['message']['content']
    return extracted if extracted else "No data found"

# Streamlit UI
st.title("📄 PDF INVOICE EXTRACTOR")
file = st.file_uploader("Upload a PDF file", type='pdf')

if file is not None:
    # Show PDF in UI
    base64_pdf = base64.b64encode(file.getvalue()).decode('utf-8')
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="1000"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

    if st.button("Extract Invoice Data"):
        pdf_text = pdf_to_text(file)
        with st.spinner("Extracting Invoice Data..."):
            extracted_json = extract_invoice_data(pdf_text)
        st.subheader("Extracted Data")
        st.json(extracted_json)
