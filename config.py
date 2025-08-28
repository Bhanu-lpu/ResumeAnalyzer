from dotenv import load_dotenv
import os

load_dotenv(dotenv_path="backend/.env")  # path relative to app.py
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
