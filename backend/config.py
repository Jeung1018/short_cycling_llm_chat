import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

#Langsmith 설정
LANGCHAIN_API_KEY= os.getenv("LANGCHAIN_API_KEY")
LANGSMITH_PROJECT=os.getenv("LANGSMITH_PROJECT")

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

DATABASE_STRUCTURE = """
    {
        building_id: "530",
        month: "2024-10",
        dates: [
            {
                date: "2024-10-01",
                total_cycles: Number,
                total_short_cycles: Number,
                panels: [
                    {
                        panel_id: String,
                        panel_name: String,
                        total_cycles: Number,
                        total_short_cycles: Number,
                        breakers: [
                            {
                                breaker_id: String,
                                breaker_name: String,
                                total_cycles: Number,
                                total_short_cycles: Number,
                                short_cycles: [
                                    {
                                        Breaker ID: String,
                                        Cycle Type: String,
                                        Base Timestamp: String,
                                        Previous Peak Timestamp: String,
                                        Next Peak Timestamp: String,
                                        "Off Duration (min)": Number,
                                        "On Duration (min)": Number,
                                        "Total Duration (min)": Number,
                                        Base Power: Number,
                                        Previous Peak Power: Number,
                                        Next Peak Power: Number
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        ]
    }
    """