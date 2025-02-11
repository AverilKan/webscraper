import json
import pandas as pd
import re

def clean_llm_output(raw_text):
    """Extracts JSON data from LLM output, removes non-JSON content, and converts to a usable format."""
    
    # Step 1: Extract JSON content from text
    json_match = re.search(r'```json\n(.*?)\n```', raw_text, re.DOTALL)
    
    if json_match:
        json_data = json_match.group(1)  # Extract only the JSON part
    else:
        json_data = raw_text  # If no explicit JSON block, try parsing full text

    try:
        structured_data = json.loads(json_data)  # Convert text to JSON
    except json.JSONDecodeError:
        print("Error: Failed to parse JSON. Cleaning raw output.")
        structured_data = fix_malformed_json(json_data)  # Attempt to fix

    return structured_data

def fix_malformed_json(text):
    """Attempts to fix common JSON errors in LLM output."""
    try:
        text = text.replace("\n", "").replace("\t", "").strip()
        return json.loads(text)
    except json.JSONDecodeError:
        print("Critical Error: Cannot fix JSON automatically.")
        return {}

def format_and_validate(data):
    """Ensures consistent formatting, converts to DataFrame, and cleans data."""
    
    if "extracted_data" in data:
        extracted_list = data["extracted_data"]
    else:
        extracted_list = data  # Assume top-level JSON is already structured

    df = pd.DataFrame(extracted_list)

    # Step 2: Standardize Key Names
    standard_keys = {
        "Price": "Price (£)",
        "Bedrooms": "Bedrooms",
        "Bathrooms": "Bathrooms",
        "Address": "Address",
        "Type": "Property Type",
        "Parking Spaces": "Parking",
        "Layout": "House Layout",
        "Nearest Amenities": "Nearby Places"
    }
    
    df.rename(columns=standard_keys, inplace=True)

    # Step 3: Ensure Proper Data Types
    df["Price (£)"] = df["Price (£)"].replace(r"[^\d]", "", regex=True).astype(float)
    df["Bedrooms"] = df["Bedrooms"].astype(int)
    df["Bathrooms"] = df["Bathrooms"].astype(int)

    # Step 4: Fill Missing Values with "Unknown"
    df.fillna("Unknown", inplace=True)

    return df

def save_to_csv(df, filename="property_data.csv"):
    """Saves cleaned DataFrame to CSV."""
    df.to_csv(filename, index=False)
    print(f"✅ Data saved to {filename}")

# 🔥 Example Usage: Apply Full Pipeline
raw_llm_output = """ YOUR_LLM_OUTPUT_HERE """  # Replace with actual LLM output

# Process and format extracted data
structured_data = clean_llm_output(raw_llm_output)
df = format_and_validate(structured_data)
save_to_csv(df)
