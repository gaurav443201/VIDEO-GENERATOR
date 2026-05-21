import os
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "sk_7f2a4f4a3b6d92c23e73923da684c56d60d1664136c3dcb8")