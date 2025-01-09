from pymongo import MongoClient
from models.state import State
from bson import ObjectId

import tiktoken
import json

def convert_objectid(data):
    """
    Recursively convert ObjectId instances to strings in a MongoDB query result.
    """
    if isinstance(data, ObjectId):
        return str(data)
    elif isinstance(data, dict):
        return {k: convert_objectid(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_objectid(i) for i in data]
    return data


def count_tokens(text: str, model: str = "gpt-3.5-turbo") -> int:
    """
    주어진 텍스트의 토큰 수를 계산합니다.

    Args:
        text (str): 토큰 수를 계산할 텍스트
        model (str): 사용할 모델 이름 (기본값: "gpt-3.5-turbo")

    Returns:
        int: 토큰 수
    """
    try:
        encoding = tiktoken.encoding_for_model(model)
        if isinstance(text, (list, dict)):
            # Convert complex objects to string
            text = json.dumps(text, default=str)
        return len(encoding.encode(text))
    except Exception as e:
        print(f"Token counting error: {str(e)}")
        return 0

def truncate_data_by_tokens(data, max_tokens=90000):
    """토큰 수에 따라 데이터를 잘라내는 헬퍼 함수"""
    if not data:
        return data
        
    truncated_data = []
    current_tokens = 0
    
    for item in data:
        item_tokens = count_tokens(item)
        if current_tokens + item_tokens > max_tokens:
            break
        truncated_data.append(item)
        current_tokens += item_tokens
    
    return truncated_data

def fetch_gen_query_node(state: State) -> State:
    """
    LLM이 생성한 MongoDB 쿼리를 실행하여 데이터를 조회하는 노드
    """
    print('---ROUTE: FETCH GEN QUERY NODE---')

    # MongoDB 클라이언트 설정
    mongo_uri = "mongodb://localhost:27017/"
    client = MongoClient(mongo_uri)
    db = client["verdigris"]

    # 먼저 쿼리를 가져옴
    mongo_query = state.get("mongo_query", None)

    # 조건 체크 후 original_mongo_query로 교체
    if (state.get("query_regen_count", 0) >= 2 or 
        state.get("query_narrowed_count", 0) >= 2):
        mongo_query = state.get("original_mongo_query")
        print(f"Using original query")

    if not mongo_query:
        raise ValueError("MongoDB query is not available in state")

    # print(f"Executing MongoDB Query: {mongo_query}")

    # MongoDB 쿼리 실행
    try:
        # mongo_query가 리스트가 아닌 경우 리스트로 변환
        pipeline = [mongo_query] if not isinstance(mongo_query, list) else mongo_query
        result = db["530_2024-10_monthly_report"].aggregate(pipeline)
        # Convert MongoDB results to a serializable format
        result_list = [convert_objectid(doc) for doc in list(result)]

        # regen_count나 narrow_count가 2 이상인 경우 데이터 제한
        if (state.get("query_regen_count", 0) >= 2 or 
            state.get("query_narrowed_count", 0) >= 2):
            print("Limiting result data to 90000 tokens due to multiple query attempts")
            result_list = truncate_data_by_tokens(result_list, max_tokens=90000)
        
        # 결과 데이터의 토큰 수 계산
        token_count = count_tokens(result_list)
        print(f"fetched data contains approximately {token_count} tokens")
        
        return {
            **state,
            "fetched_gen_data": result_list,
            "query_token_count": token_count,
            "data_truncated": len(result_list) < len(list(result))  # 데이터가 잘렸는지 여부 저장
        }
        
    except Exception as e:
        print(f"Error executing MongoDB query: {str(e)}")
        return {
            **state,
            "fetched_gen_data": f"Error executing query: {str(e)}"
        }
