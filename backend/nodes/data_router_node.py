from models.state import State
from langchain.prompts import ChatPromptTemplate


def data_router_node(state: State) -> State:
    """
    LLM을 사용하여 쿼리 타입을 분석하는 노드
    """
    print('---ROUTE: DATA ROUTER---')

    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an assistant that analyzes user queries to determine the type of data needed.

        Query Types:
        1. "hierarchy" - Questions about building electrical structure, related to breakers, panels, and circuits
        2. "building" - General questions about the building or its overall systems
        3. "detail" - Queries that require generating precise MongoDB commands to retrieve structured data, such as the short cycling details for individual breakers and panels, visualization URLs for breakers, or comprehensive information about specific short cycling events, including timestamps, power levels, and durations.
        
        Return ONLY ONE of these exact words: "hierarchy", "building", or "detail"."""),
        ("user", "Analyze this query and determine its type: {query}")
    ])

    # LLM 체인 실행
    chain = prompt | state["llm"]
    response = chain.invoke({
        "query": state["query"]
    })

    # 응답 정규화
    query_type = response.content.strip().lower()
    if query_type not in ["hierarchy", "building", "detail"]:
        query_type = "building"  # 기본값

    print(f"\nQuery: {state['query']}")
    print(f"Determined Type: {query_type}")

    return {
        **state,
        "query_type": query_type
    }


def data_router_rf(state: State) -> str:
    """
    data_router_node 이후의 라우팅을 결정하는 함수

    Args:
        state (State): 현재 그래프 상태

    Returns:
        str: 다음 노드 결정 ('building_analysis', 'hierarchy_analysis', 'detail_analysis')
    """
    print('---DATA TYPE ROUTING---')
    query_type = state["query_type"]

    if query_type == "hierarchy":
        print('---ROUTE: HIERARCHY ANALYSIS---')
        return "hierarchy_analysis"
    elif query_type == "detail":
        print('---ROUTE: DETAIL ANALYSIS---')
        return "detail_analysis"
    else:
        print('---ROUTE: BUILDING ANALYSIS---')
        return "building_analysis"
