import requests
import json
import os
from dotenv import load_dotenv
import streamlit as st
import base64
import PyPDF2

load_dotenv()


api_key= st.secrets["OPENROUTER_API_KEY"]
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
            "Authorization": f"Bearer {api_key}",
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

    if 'choices' in data and len(data['choices']) > 0:
        extracted = data['choices'][0]['message']['content']
        return extracted
    else:
        st.error("API did not return valid data. Response:")
        st.write(data)
        extracted = "No data found"
        return extracted

    
    

# Streamlit UI
st.title("📄 PDF INVOICE EXTRACTOR")
file = st.file_uploader("Upload a PDF file", type='pdf')

if file is not None:
    # Show PDF in UI
    st.success(f"✅ PDF uploaded: {file.name}")
    st.download_button(
    label="📥 Download Uploaded PDF",
    data=file.getvalue(),
    file_name=file.name,
    mime="application/pdf"
    )


    if st.button("Extract Invoice Data"):
        pdf_text = pdf_to_text(file)
        with st.spinner("Extracting Invoice Data..."):
            extracted_json = extract_invoice_data(pdf_text)
        st.subheader("Extracted Data")
        st.json(extracted_json)
