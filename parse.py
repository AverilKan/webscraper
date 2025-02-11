'parse.py: A module to parse the DOM content and extract specific information with LLM.'

import json
import pandas as pd
import re
import logging
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Initialize LLM
llm = OllamaLLM(model="deepseek-r1:7b")

### **🔹 LLM-Powered Extraction**
def extract_structure_from_text(raw_text):
    """
    Uses LLM to dynamically extract structured information and auto-detect relevant fields.
    Works for any dataset: real estate, products, job listings, etc.
    """

    prompt_template = (
        "You are an expert data extractor. Analyze the following text and infer structured attributes dynamically. "
        "Detect the relevant fields based on the content type (e.g., real estate listings, job postings, e-commerce products). "
        "Extract all useful information in JSON format. Do NOT include explanations.\n\n"
        "**Raw Extracted Text:**\n"
        "{raw_text}\n\n"
        "**Expected JSON Output Format:**\n"
        "```json\n"
        "{{\n"
        '  "data": [\n'
        "    {{ extracted_information }}\n"
        "  ]\n"
        "}}\n"
        "```"
    )

    prompt = ChatPromptTemplate.from_template(prompt_template)
    chain = prompt | llm

    logging.info("🔍 Sending extracted text to LLM for structured parsing...")
    response = chain.invoke({"raw_text": raw_text})

    # 🔥 DEBUG: Print full LLM response before processing
    print("\n🔥 RAW LLM OUTPUT 🔥\n", response, "\n🔥 END OF OUTPUT 🔥\n")

    return clean_llm_output(response)

### **🔹 Extract JSON from LLM Output**
def clean_llm_output(raw_text):
    """
    Extracts valid JSON from the LLM response, removing hallucinations.
    """

    # Extract JSON block from response
    json_match = re.search(r'```json\n(.*?)\n```', raw_text, re.DOTALL)

    if json_match:
        json_data = json_match.group(1)  # Extract JSON block
    else:
        json_data = raw_text  # Assume the full text is JSON

    try:
        structured_data = json.loads(json_data)  # Convert text to JSON
        return structured_data
    except json.JSONDecodeError:
        logging.warning("⚠️ JSON parsing failed, attempting to fix formatting...")
        return fix_malformed_json(json_data)

def fix_malformed_json(text):
    """
    Attempts to fix common JSON errors in LLM output.
    """
    try:
        text = text.replace("\n", "").replace("\t", "").strip()
        return json.loads(text)
    except json.JSONDecodeError:
        logging.error("🚨 Critical Error: Cannot fix JSON automatically.")
        return {}

### **🔹 Fix & Standardize Extracted Data (Dynamically)**
def format_and_validate(data):
    """
    Cleans extracted data, ensures correct types, and dynamically handles different structures.
    """

    if "data" in data:
        extracted_list = data["data"]
    else:
        extracted_list = data  # Assume top-level JSON is structured

    df = pd.DataFrame(extracted_list)

    # 🔹 Convert list values into readable strings
    for col in df.columns:
        df[col] = df[col].apply(lambda x: ", ".join(map(str, x)) if isinstance(x, list) else x)

    # 🔹 Detect and convert numeric fields (NO HARDCODED COLUMN NAMES)
    for col in df.columns:
        if df[col].dtype == 'object':  # If column contains text
            cleaned_col = df[col].astype(str).str.replace(r"[^\d.]", "", regex=True)
            if cleaned_col.str.isnumeric().all():
                df[col] = pd.to_numeric(cleaned_col, errors="coerce").fillna(0)

    # 🔹 Remove Columns that are only "Unknown"
    df.replace("Unknown", pd.NA, inplace=True)  # Convert "Unknown" to NaN
    df.dropna(axis=1, how="all", inplace=True)  # Drop columns where all values are NaN

    df.fillna("Unknown", inplace=True)  # Restore missing values
    return df

### **🔹 Save to CSV/JSON**
def save_to_csv(df, filename="extracted_data.csv"):
    """Saves structured data to CSV."""
    df.to_csv(filename, index=False)
    logging.info(f"✅ Data saved to {filename}")

def save_to_json(df, filename="extracted_data.json"):
    """Saves structured data to JSON."""
    df.to_json(filename, orient="records", indent=4)
    logging.info(f"✅ Data saved to {filename}")

### **🔹 Main Parsing Function**
def parse(dom_chunks):
    """
    Parses extracted website data, detects attributes dynamically, cleans, and saves as CSV/JSON.
    """
    logging.info("🔄 Processing extracted website content...")

    structured_data = extract_structure_from_text(" ".join(dom_chunks))  # Merge all chunks
    df = format_and_validate(structured_data)

    # Save Data
    save_to_csv(df)
    save_to_json(df)

    return df
