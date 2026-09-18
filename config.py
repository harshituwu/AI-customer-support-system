import os
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Project root
BASE_DIR = Path(__file__).resolve().parent.parent

# API key
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Gemini configuration
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "gemini-embedding-001")

# Directories
CHROMA_DIR = BASE_DIR / os.getenv("CHROMA_DIR", "chroma_db")
KNOWLEDGE_BASE_DIR = BASE_DIR / os.getenv(
    "KNOWLEDGE_BASE_DIR", "knowledge_base"
)
UPLOAD_DIR = BASE_DIR / os.getenv("UPLOAD_DIR", "uploads")

# RAG configuration
TOP_K = int(os.getenv("TOP_K", "4"))

# Chroma collection
COLLECTION_NAME = "customer_support_knowledge"

# Create required directories
CHROMA_DIR.mkdir(parents=True, exist_ok=True)
KNOWLEDGE_BASE_DIR.mkdir(parents=True, exist_ok=True)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def validate_config():
    """Check whether the required configuration exists."""
    if not GOOGLE_API_KEY:
        raise ValueError(
            "GOOGLE_API_KEY is missing. Add your Gemini API key to .env"
        )
