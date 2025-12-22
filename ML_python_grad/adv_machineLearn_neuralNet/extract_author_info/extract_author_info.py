"""
LLM-powered author lookup
"""

import json
import re

import pandas as pd
import PyPDF2
import openai # pip install openai


LLM_PROVIDER = "openai"
KEYS = {
    "openai": "<API_KEY>"
}

def extract_pdf_text(pdf_path):
    """Extract all text from PDF, each page as separate entry"""
    pages_of_text = []
    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        print(f"PDF has {len(pdf_reader.pages)} pages")
        pages_of_text = [page.extract_text() + "\n" for page in pdf_reader.pages]
    return pages_of_text

def call_llm(prompt, provider=LLM_PROVIDER):
    client = openai.OpenAI(api_key=KEYS[provider])
    response = client.responses.create(
        model="gpt-4.1",
        input = prompt
    )
    # Parse JSON into Python dict
    result = re.sub(r"```json|```", "", response.output_text).strip()
    try:
        result = json.loads(result)
    except json.JSONDecodeError as e:
        print("Error decoding JSON:", e)
        print("Response was:", result)
        result = []
    return result

def obtain_list_of_json(text):
    """Use LLM to extract structured info from search results"""
    
    prompt = f"""
        You are extracting contact information for the authors found in: {text}

        Obtain a list of JSON objects, one JSON per author, with the following fields:
        {{
            "paper": "paper name",
            "first name": "first name",
            "last name": "first name",
            "email": "email address",
            "university": "university name",
            "department": "department",
            "address": "physical address"
        }}

        If any field is not found, use null. Return ONLY list of valid JSON.
    """
    
    response = call_llm(prompt, provider=LLM_PROVIDER)
    return response


pdf_name = "References.pdf"

pages_of_text = extract_pdf_text(pdf_name)
list_of_json = []
for i, text in enumerate(pages_of_text):
    print(f"Processing page {i + 1}")
    list_of_json += obtain_list_of_json(text)
df = pd.DataFrame(list_of_json)
df.to_excel("extracted_author_info_full.xlsx", index=False)
print(f"Extracted info for {len(df)} authors")
print(df)
