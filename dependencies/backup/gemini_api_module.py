import os
import google.generativeai as genai
import json
import logging

# Configure logging
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

# Load configuration from config.json
try:
    with open("config.json", "r") as f:
        config = json.load(f)
    api_key = config.get("gemini_api_key")
    gemini_model_name = config.get("gemini_model")
except FileNotFoundError:
    logging.error("Error: config.json not found. Please make sure the file is created.")
    api_key = None
    gemini_model_name = None
except json.JSONDecodeError:
    logging.error("Error: config.json is not a valid JSON file.")
    api_key = None
    gemini_model_name = None
except Exception as e:
    logging.error(f"An unexpected error occurred while loading the config: {e}")
    api_key = None
    gemini_model_name = None

# Check if the api key was loaded correctly
if not api_key:
    print("Error: Gemini API key not found in config.json")
    exit(1)

if not gemini_model_name:
    print("Error: Gemini model not found in config.json")
    exit(1)

genai.configure(api_key=api_key)

# Function to generate text with Gemini
def generate_text(prompt):
    try:
        model = genai.GenerativeModel(gemini_model_name)
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        logging.error(f"Error generating text: {e}")
        return None

if __name__ == '__main__':
    prompt = "Write a very short sentence."
    response_text = generate_text(prompt)

    if response_text:
         print(f"Response: {response_text}")
    else:
        print("Error: No response received from Gemini API")
