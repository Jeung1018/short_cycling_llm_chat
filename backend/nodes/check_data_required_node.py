from models.state import State
from langchain.prompts import ChatPromptTemplate

def check_data_required_node(state: State) -> State:
    """
    LLM을 사용하여 쿼리를 분석하고 추가 데이터 조회 필요 여부를 판단하는 노드
    """
    print('---ROUTE: CHECK DATA REQUIRED---')
    
    # LLM 프롬프트 템플릿
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an assistant that analyzes user queries and current state data.
        Available data in state:
        - building_info: Contains building information (id, name, panels, dates)
        - active_breakers: Contains active breaker information
        - building_hierarchy: Contains building's electrical hierarchy structure
        
        Determine if additional data retrieval is needed based on:
        1. The user's query
        2. Currently available data in state
        
        Return only 'true' if new data is needed, 'false' if existing state data is sufficient."""),
        ("user", """Query: {query}
        
        Current State Data:
        Building Info: {building_info}
        Active Breakers: {active_breakers}
        building_hierarchy: {building_hierarchy}
        
        Is additional data retrieval needed?""")
    ])
    
    # LLM 체인 실행
    chain = prompt | state["llm"]
    response = chain.invoke({
        "query": state["query"],
        "building_info": state.get("building_info", {}),
        "active_breakers": state.get("active_breakers", {}),
        "building_hierarchy": state.get("building_hierarchy", {})
    })
    
    # LLM 응답을 boolean으로 변환
    needs_data = response.content.lower().strip() == 'true'
    
    print(f"\nQuery: {state['query']}")
    print(f"Needs Data: {needs_data}")
    
    return {
        **state,
        "needs_data": needs_data
    }

def check_data_required_rf(state: State) -> str:
    """
    check_data_required_node 이후의 라우팅을 결정하는 함수

    Args:
        state (State): 현재 그래프 상태

    Returns:
        str: 다음 노드 결정 ('fetch_data' 또는 'general_answer')
    """
    print('---QUERY TYPE DECISION---')
    
    # state의 needs_data가 bool 타입인지 확인하고 처리
    needs_data = state.get("needs_data", False)
    if isinstance(needs_data, bool):
        if needs_data:
            print('---DECISION: NEEDS DATA FETCH---')
            return 'fetch_data'
        else:
            print('---DECISION: GENERAL ANSWER---')
            return 'general_answer'
    else:
        # needs_data가 bool이 아닌 경우 기본값으로 general_answer 반환
        print('---DECISION: GENERAL ANSWER (default)---')
        return 'general_answer'