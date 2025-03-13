import google.generativeai as genai
from elia_api.config import config  # Assuming your config file is named config.py
import logging

logger = logging.getLogger(__name__)

# Function to initialize Gemini
def init_gemini():
    if not config.GOOGLE_API_KEY:
        raise RuntimeError("❌ GOOGLE_API_KEY is missing in config.")
    genai.configure(api_key=config.GOOGLE_API_KEY)
    logger.info("✅ Gemini API initialized.")
