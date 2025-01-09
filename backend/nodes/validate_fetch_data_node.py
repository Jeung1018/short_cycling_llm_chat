from models.state import State
from bson import json_util
import tiktoken


def count_tokens(data) -> int:
    """JSON 데이터의 토큰 수를 계산하는 헬퍼 함수"""
    encoding = tiktoken.get_encoding("cl100k_base")
    json_string = json_util.dumps(data)
    return len(encoding.encode(json_string))


def validate_fetch_data_node(state: State) -> State:
    """
    fetch된 데이터의 크기를 검증하는 노드
    """
    print('---VALIDATING FETCHED DATA---')
    
    if "fetched_gen_data" not in state:
        print('No fetched data to validate')
        return state
        
    token_count = count_tokens(state["fetched_gen_data"])
    print(f'Fetched data contains {token_count} tokens')
    
    # token count가 100000 이상이면 original_mongo_query 저장
    if token_count >= 100000:
        return {
            **state,
            "token_count": token_count,
            "original_mongo_query": state.get("mongo_query", {})
        }
    
    return {
        **state,
        "token_count": token_count
    }


def validate_fetch_data_rf(state: State) -> str:
    """
    validate_fetch_data_node 이후의 라우팅을 결정하는 함수

    Args:
        state (State): 현재 그래프 상태

    Returns:
        str: 다음 노드 결정 ('narrow_down_mongo_query' 또는 'valid_fetch_data')
    """
    print('---FETCH DATA VALIDATION ROUTING---')
    
    # fetched_gen_data 존재 여부 먼저 확인
    if "fetched_gen_data" not in state:
        print('No fetched data found, narrowing down query')
        return "narrow_down_mongo_query"
    
    # token count 확인
    if state.get("token_count", 0) >= 100000:
        print(f'Token count ({state.get("token_count")}) exceeds limit, narrowing down query')
        state["original_mongo_query"] = state.get("mongo_query", {})
        print(f"Original mongo_query: {state.get('original_mongo_query', {})}")
        print(f"mongo_query: {state.get('mongo_query', {})}")
        return "narrow_down_mongo_query"
    
    if state.get("token_count", 0) <= 5:
        print(f'Token count ({state.get("token_count")}) too small, regen query')
        print(f'fetched_gen_data: {state.get("fetched_gen_data", {})}')
        state["invalid_query_reason"] = "Current mongo_query fetch no data, please check the user input and regenerate the mongo_query"
        return "regen_mongo_query"
    
        # MongoDB 쿼리 에러 체크
    if isinstance(state.get("fetched_gen_data"), str) and "Error executing MongoDB query" in state["fetched_gen_data"]:
        print('MongoDB query execution error detected')
        state["invalid_query_reason"] = state["fetched_gen_data"]
        return "regen_mongo_query"
    
    print(f'Data validation passed with {state.get("token_count", 0)} tokens')
    return "valid_fetch_data" 