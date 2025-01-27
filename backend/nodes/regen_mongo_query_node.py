from models.state import State
from prompts.regen_mongo_query_prompts import REGEN_MONGO_QUERY_PROMPT
from bson import json_util
import json

def regen_mongo_query_node(state: State) -> State:
    """
    Node for regenerating MongoDB query when validation fails
    Attempts to fix formatting issues and syntax errors
    """
    print('---ROUTE: MONGO QUERY REGENERATION---')

    # 현재 시도 횟수 계산
    query_regen_count = state.get("query_regen_count", 0) + 1
    print(f'Query regeneration attempt #{query_regen_count}')

    # Execute LLM chain
    chain = REGEN_MONGO_QUERY_PROMPT | state["llm"]
    response = chain.invoke({
        "mongo_query": json_util.dumps(state["mongo_query"], indent=2),
        "query": state.get("query", ""),
        "invalid_query_reason": state.get("invalid_query_reason", "Unknown validation error"),
        "database_structure": state.get("database_structure", {})
    })

    try:
        # 디버깅을 위한 원본 응답 출력
        print("Original Response:", response.content)
        
        # 응답 정리
        content = response.content.strip()
        
        # 코드 블록 제거
        if "```" in content:
            parts = content.split("```")
            if len(parts) >= 3:  # 올바른 코드 블록 형식인 경우
                content = parts[1]  # 첫 번째와 마지막 ``` 사이의 내용
                if content.startswith("json"):
                    content = content[4:].strip()  # "json" 태그 제거
        
        # 디버깅을 위한 정리된 응답 출력
        print("Cleaned Response:", content)
        
        if not content:
            raise ValueError("Empty response from LLM")
            
        # Parse regenerated query
        new_query = json.loads(content)
        
        print("Query regenerated successfully")
        return {
            **state,
            "mongo_query": new_query,
            "query_regen_count": query_regen_count
        }

    except Exception as e:
        error_message = f"Query regeneration failed: {str(e)}\nResponse content: {response.content}"
        print(error_message)
        raise ValueError(error_message)


def regen_mongo_query_rf(state: State) -> str:
    """
    Routing function after regen_mongo_query_node

    Args:
        state (State): Current graph state

    Returns:
        str: Next node decision ('validate_mongo_query' or 'error')
    """
    print('---MONGO QUERY REGENERATION ROUTING---')
    
    # Check if we've tried regenerating too many times
    if state.get("query_regen_count", 0) >= 2:
        print("Maximum regeneration attempts reached")
        state["mongo_query"] = state.get("original_mongo_query", {})
        print(f"Original mongo_query: {state.get('original_mongo_query', {})}")
        return "fetch_data"
    
    # Route back to validation
    print("Routing to validation")
    return "validate_mongo_query"