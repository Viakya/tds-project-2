import os
from dotenv import load_dotenv

load_dotenv()

SECRET = os.getenv("SECRET")
BASE_URL = os.getenv("BASE_URL")
MODEL = os.getenv("MODEL")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
