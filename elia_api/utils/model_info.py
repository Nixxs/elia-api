import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables from .env file
load_dotenv()

# Get the API key from the environment
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Check if API key is loaded
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY is missing from environment variables!")

# Configure the generative AI client
genai.configure(api_key=GOOGLE_API_KEY)

# Function to list available models
def list_gemini_models():
    try:
        models = genai.list_models()
        model_list = []
        for m in models:
            model_list.append({
                "model_id": m.name,
                "description": m.description,
                "input_token_limit": m.input_token_limit,
                "output_token_limit": m.output_token_limit,
                "supported_generation_methods": m.supported_generation_methods
            })
        return model_list
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    available_models = list_gemini_models()
    for model in available_models:
        print(f"- Model ID: {model['model_id']}")
        print(f"  Description: {model['description']}")
        print(f"  Input Token Limit: {model['input_token_limit']}")
        print(f"  Output Token Limit: {model['output_token_limit']}")
        print(f"  Supported Generation Methods: {model['supported_generation_methods']}")
        print("------")