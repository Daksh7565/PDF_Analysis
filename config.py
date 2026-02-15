import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    CHROMA_PERSIST_DIR = "./data/chroma_db"
    LOG_DIR = "./data/logs"
    UPLOAD_DIR = "./data/uploads"
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200
    MAX_WORKERS = 4
    DEFAULT_MODEL = "gemini-flash-latest"
    TEMPERATURE = 0.3
    
    @classmethod
    def ensure_dirs(cls):
        for dir_path in [cls.CHROMA_PERSIST_DIR, cls.LOG_DIR, cls.UPLOAD_DIR]:
            os.makedirs(dir_path, exist_ok=True)

Config.ensure_dirs()