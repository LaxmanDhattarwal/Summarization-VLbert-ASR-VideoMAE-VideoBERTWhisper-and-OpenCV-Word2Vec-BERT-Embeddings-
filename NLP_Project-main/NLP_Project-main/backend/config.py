import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
UPLOAD_DIR = DATA_DIR / "uploads"
FIGURE_DIR = DATA_DIR / "figures"

MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50 MB
ALLOWED_EXTENSIONS = {".pdf"}

DEFAULT_MODELS = {
    "summarizer": os.getenv("SUMMARIZER_MODEL", "facebook/bart-large-cnn"),
    "qa": os.getenv("QA_MODEL", "deepset/roberta-base-squad2"),
    "image_captioner": os.getenv("IMAGE_CAPTION_MODEL", "nlpconnect/vit-gpt2-image-captioning"),
    "embedding": os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"),
}

CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
