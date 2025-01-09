from models.state import State
from prompts.narrow_down_mongo_query_prompts import NARROW_DOWN_MONGO_QUERY_PROMPT
from bson import json_util
import json


def narrow_down_mongo_query_node(state: State) -> State:
    """
    LLM을 사용하여 MongoDB 쿼리를 더 효율적으로 좁히는 노드
    """
    print('---NARROWING DOWN MONGO QUERY WITH LLM---')

    print(f"Original mongo_query: {state.get('original_mongo_query', {})}")


    # 현재 시도 횟수 계산
    narrow_down_count = state.get("query_narrowed_count", 0) + 1
    print(f'Narrow down attempt #{narrow_down_count}')

    # Execute LLM chain
    chain = NARROW_DOWN_MONGO_QUERY_PROMPT | state["llm"]
    response = chain.invoke({
        "query": state.get("query", ""),
        "current_query": json_util.dumps(state.get("mongo_query", {}), indent=2),
        "database_structure": state.get("database_structure", {}),
        "token_count": state.get("token_count", 0)
    })

    try:
        # 디버깅을 위한 원본 응답 출력
        print("Original Response:", response.content)
        
        # 응답 정리
        content = response.content.strip()
        
        # JSON 추출 개선
        def extract_json(text: str) -> str:
            """코드 블록에서 JSON 추출 및 정리"""
            if "```" in text:
                # 코드 블록 추출
                parts = text.split("```")
                for part in parts:
                    cleaned = part.strip()
                    if cleaned.startswith(('json', '{')):
                        # json 태그 제거
                        return cleaned.replace('json', '', 1).strip()
            return text.strip()

        # 응답 정리
        content = extract_json(content)
        print("Cleaned Response:", content)
        
        if not content:
            raise ValueError("Empty response from LLM")
            
        # JSON 파싱 시도
        try:
            result = json.loads(content)
        except json.JSONDecodeError:
            # JSON 형식 교정 시도
            content = content.replace("'", '"')  # 작은따옴표를 큰따옴표로 변경
            content = content.replace('\n', '')  # 줄바꿈 제거
            result = json.loads(content)
        
        # 필수 필드 검증
        if "narrowed_mongo_query" not in result:
            raise ValueError("Missing 'narrowed_mongo_query' in LLM response")
            
        # MongoDB 쿼리 구조 검증
        modified_query = result["narrowed_mongo_query"]
        if not isinstance(modified_query, list):
            raise ValueError("narrowed_mongo_query must be a list of pipeline stages")
            
        print('Successfully generated new narrowed query')
        print(f'Reasoning: {result.get("reasoning", "No reasoning provided")}')
        print(f"Original mongo_query: {state.get('original_mongo_query', {})}")

        
        return {
            **state,
            "mongo_query": modified_query,
            "query_narrowed": True,
            "query_narrowed_count": narrow_down_count,
            "narrow_down_reasoning": result.get("reasoning")
        }

    except json.JSONDecodeError as e:
        error_message = f"JSON parsing error: {str(e)}\nCleaned content: {content}"
        print(error_message)
        raise ValueError(error_message)
    except Exception as e:
        error_message = f"Error in narrow down query: {str(e)}\nResponse content: {response.content}"
        print(error_message)
        raise ValueError(error_message)


def narrow_down_mongo_query_rf(state: State) -> str:
    """
    narrow_down_mongo_query_node 이후의 라우팅을 결정하는 함수

    Args:
        state (State): 현재 그래프 상태

    Returns:
        str: 다음 노드 결정 ('fetch_data' 또는 'error')
    """
    print('---NARROW DOWN QUERY ROUTING---')
    
    if state.get("query_narrowed_count", 0) >= 2:
        print("Maximum query narrowing attempts reached, use the original query")
        state["mongo_query"] = state.get("original_mongo_query", {})
        state["query_narrowed_count"] = 0
        return "narrow_downed_success"
    
    print("narrow_downed_success")
    return "narrow_downed_success" 