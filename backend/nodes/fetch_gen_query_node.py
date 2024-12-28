from pymongo import MongoClient
from models.state import State


def fetch_gen_query_node(state: State) -> State:
    """
    LLM이 생성한 MongoDB 쿼리를 실행하여 데이터를 조회하는 노드
    """
    print('---ROUTE: FETCH GEN QUERY NODE---')

    # MongoDB 클라이언트 설정
    mongo_uri = "mongodb://localhost:27017/"
    client = MongoClient(mongo_uri)
    db = client["verdigris"]

    # 생성된 MongoDB 쿼리 가져오기
    mongo_query = state.get("mongo_query", None)

    if not mongo_query:
        raise ValueError("MongoDB query is not available in state")

    print(f"Executing MongoDB Query: {mongo_query}")

    # MongoDB 쿼리 실행
    try:
        result = db["530_2024-10_monthly_report"].aggregate(mongo_query)
        result_list = list(result)

        print(f"Query Result: {result_list}")
        
        new_state = {
            **state,
            "fetched_gen_data": result_list
        }
        
        print(f"Updated State: {new_state}")  # 상태 업데이트 확인을 위한 로그 추가
        
        return new_state

    except Exception as e:
        print(f"Error executing MongoDB query: {str(e)}")
        return {
            **state,
            "fetched_gen_data": f"Error executing query: {str(e)}"
        }
