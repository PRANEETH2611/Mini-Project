import google.generativeai as genai
import sys
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

try:
    with open("models_list.txt", "w") as f:
        if not API_KEY:
            raise ValueError("GOOGLE_API_KEY is missing. Set it in .env")
        genai.configure(api_key=API_KEY)
        f.write("--- START MODEL LIST ---\n")
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                f.write(f"{m.name}\n")
        f.write("--- END MODEL LIST ---\n")
except Exception as e:
    with open("models_list.txt", "w") as f:
        f.write(f"Error: {e}")
