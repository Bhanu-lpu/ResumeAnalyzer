
from dotenv import load_dotenv
import os

load_dotenv()  # loads variables from .env

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

