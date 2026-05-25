import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://meetmind_user:meetmind_password@db:5432/meetmind_db"
)

AI_API_KEY = os.getenv("AI_API_KEY")

AI_API_BASE = os.getenv(
    "AI_API_BASE",
    "https://api.groq.com/openai/v1"
)

AI_MODEL = os.getenv(
    "AI_MODEL",
    "openai/gpt-oss-120b"
)

APP_NAME = "MeetMind AI"
APP_VERSION = "0.1.0"

DEBUG = os.getenv("DEBUG", "True") == "True"

CORS_ORIGINS = [
    "http://localhost:8501",
    "http://frontend:8501"
]

API_HOST = os.getenv("API_HOST", "0.0.0.0")

API_PORT = int(os.getenv("API_PORT", 8000))