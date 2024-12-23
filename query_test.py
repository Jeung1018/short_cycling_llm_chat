from backend.workflows.main_workflow import create_workflow
from langchain_openai import ChatOpenAI

def test_query(query: str):
    """단일 쿼리를 테스트하는 함수"""
    # 워크플로우 생성
    workflow = create_workflow()
    
    # 초기 상태 설정
    state = {
        "query": query,
        "chat_history": [],
        "current_input": "",
        "validation_result": {},
        "analysis_result": {},
        "llm": ChatOpenAI(temperature=0),
        "docs": [],
        "answer": "",
        "mongo_query": {},
        "building_id": "",
        "date": "",
        "date_type": "",
        "date_range": {},
        "terminate": False,
        "analysis_results": {},
        "recommendations": {},
        "breaker_filter_result": {},
        "query_intent": {}
    }
    
    # 워크플로우 실행
    config = {"configurable": {"thread_id": "test-1"}}
    result = workflow.invoke(state, config)
    
    return result

if __name__ == "__main__":
    # 단일 쿼리 테스트
    test_query("Show me all active breakers")
    
    # 나중에 테스트할 쿼리들
    """
    queries = [
        "Tell me about Building 530",
        "Show me Building 530's structure",
        "What's the weather like today?"
    ]
    """