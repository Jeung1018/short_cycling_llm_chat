import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# OpenAI 설정
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
LLM_MODEL = "gpt-4o-mini"
LLM_TEMPERATURE = 0.0

# MongoDB 설정
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
DB_NAME = os.getenv("DB_NAME", "verdigris")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "530_2024-10_monthly_report")

# 기타 설정
DEFAULT_BUILDING_ID = "530"
DEFAULT_MONTH = "October"
DEFAULT_YEAR = "2024"