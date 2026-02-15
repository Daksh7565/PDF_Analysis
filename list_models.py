import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("Error: GOOGLE_API_KEY not found in .env")
else:
    genai.configure(api_key=api_key)
    try:
        with open("models_list.txt", "w") as f:
            f.write("All available models:\n")
            for m in genai.list_models():
                f.write(f" - {m.name} ({m.supported_generation_methods})\n")
        print("Model list written to models_list.txt")
    except Exception as e:
        print(f"Error listing models: {e}")
