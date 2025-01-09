from models.state import State
from backend.prompts.mongo_query_gen_prompts import MONGO_GEN_QUERY_PROMPT
import ast

def mongo_query_gen_node(state: State) -> State:
    """
    MongoDB 에서 데이터를 조회하기 위해 쿼리를 생성하는 노드
    """
    print('---ROUTE: MONGO QUERY GENERATION---')

    # LLM 체인 실행
    chain = MONGO_GEN_QUERY_PROMPT | state["llm"]
    response = chain.invoke({
        "query": state["query"],
        "chat_history": str(state.get("chat_history", []))  # chat_history 추가 및 기본값 설정
    })

    print(f"Raw LLM Response: {response.content}")  # 디버깅을 위해 추가

    # 문자열을 Python 객체로 변환
    try:
        # 응답에서 불필요한 공백과 줄바꿈 제거
        cleaned_response = response.content.strip()
        mongo_query = ast.literal_eval(cleaned_response)
        
        if not isinstance(mongo_query, list):
            error = f"Query is not a list, got type: {type(mongo_query)}"
            print(error)
            return {
                **state,
                "mongo_query": mongo_query,
                "mongo_query_error": error
            }
            
        if len(mongo_query) == 0:
            error = "Query list is empty"
            print(error)
            return {
                **state,
                "mongo_query": mongo_query,
                "mongo_query_error": error
            }
            
    except Exception as e:
        error = f"Error parsing MongoDB query: {e}"
        print(error)
        return {
            **state,
            "mongo_query": response.content,
            "mongo_query_error": error
        }

    print(f"Parsed MongoDB Query: {mongo_query}")

    return {
        **state,
        "mongo_query": mongo_query
    }
