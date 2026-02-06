import google.generativeai as genai
import sys

API_KEY = "AIzaSyC6MI7Z9rG_8kTMgk12-1_FH6TlOLrqp6s"

try:
    with open("models_list.txt", "w") as f:
        genai.configure(api_key=API_KEY)
        f.write("--- START MODEL LIST ---\n")
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                f.write(f"{m.name}\n")
        f.write("--- END MODEL LIST ---\n")
except Exception as e:
    with open("models_list.txt", "w") as f:
        f.write(f"Error: {e}")
