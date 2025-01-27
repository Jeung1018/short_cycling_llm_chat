from models.state import State
from langchain.prompts import ChatPromptTemplate
from backend.config import DATABASE_STRUCTURE, LLM_MODEL_VALIDATION, LLM_TEMPERATURE, OPENAI_API_KEY, MONGO_QUERY_MODEL
from langchain_openai import ChatOpenAI

def check_data_required_node(state: State) -> State:
    """
    LLM을 사용하여 쿼리를 분석하고 추가 데이터 조회 필요 여부를 판단하는 노드
    """
    print('---ROUTE: CHECK DATA REQUIRED---')

    state = {
        **state,
        "database_structure": DATABASE_STRUCTURE,
        "validate_query_model": ChatOpenAI(
        model_name=LLM_MODEL_VALIDATION,
        temperature=LLM_TEMPERATURE,
        openai_api_key=OPENAI_API_KEY
    ),
        "mongo_query_model": ChatOpenAI(
        model_name=MONGO_QUERY_MODEL,
        temperature=LLM_TEMPERATURE,
        openai_api_key=OPENAI_API_KEY
    )
    }

    # LLM 프롬프트 템플릿
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an assistant that analyzes user queries and current state data.
        Available data in state:
        - building_info: Contains building information (id, name, panels, dates)
        - building_hierarchy: Contains building's electrical hierarchy structure
        - fetched_gen_data: Contains detailed information about short cycling events, including timestamps, power levels, durations, and structured data for individual breakers and panels

        Determine if additional data retrieval is needed based on:
        1. The user's query and chat history
        2. Currently available data in state

        Return only 'true' if new data is needed, 'false' if existing state data is sufficient."""),
        ("user", """Chat History:\n{chat_history}\n\nQuery: {query}

        Current State Data:
        Building Info: {building_info}
        Building Hierarchy: {building_hierarchy}
        Fetched Data: {fetched_gen_data}

        Is additional data retrieval needed?""")
    ])

    # LLM 체인 실행
    chain = prompt | state["llm"]
    response = chain.invoke({
        "chat_history": state.get("chat_history", []),
        "query": state["query"],
        "building_info": state.get("building_info", {}),
        "building_hierarchy": state.get("building_hierarchy", {}),
        "fetched_gen_data": state.get("fetched_gen_data", {})
    })

    # LLM 응답을 boolean으로 변환
    needs_data = response.content.lower().strip() == 'true'

    print(f"Needs Data: {needs_data}")

    # chat_history 안전하게 처리
    chat_history = state.get("chat_history", [])
    add_human_query_to_chat_history = chat_history + [{"role": "You", "content": state["query"]}]


    return {
        **state,
        "needs_data": needs_data,
        "chat_history": add_human_query_to_chat_history
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