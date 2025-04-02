import os
from dotenv import load_dotenv

load_dotenv()  # Load .env variables

API_BASE_URL = os.getenv("API_BASE_URL")
print(API_BASE_URL)