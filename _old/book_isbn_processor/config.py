import os

from dotenv import load_dotenv

load_dotenv()

API_BASE_URL = os.getenv("API_BASE_URL", "https://dapi.kakao.com/v3/search/book")
API_KEY = os.getenv("KAKAO_API_KEY")

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "5432")),
    "database": os.getenv("DB_NAME", "book_db"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD"),
}

DEFAULT_CSV_FILE = os.getenv("DEFAULT_CSV_FILE", "isbn.csv")

LOG_LEVEL = os.getenv("LOG_LEVEL", "ERROR").upper()
LOG_FILE_PATH = os.getenv("LOG_FILE_PATH", "logs/book_isbn_processor.log")
