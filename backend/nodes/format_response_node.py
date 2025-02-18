from typing import Dict
from models.state import State
from langchain.prompts import ChatPromptTemplate

def format_response_node(state: State) -> State:
    """
    쿼리 타입에 따라 적절한 응답을 생성하는 노드
    """
    print('---ROUTE: FORMAT RESPONSE---')
    print(state)

    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert data analyst for the building management system of "building 530".

        Available Data Types:
        1. Building Information:
           - General building details and overview
           - Basic building statistics and information
           
        2. Building Hierarchy:
           - Building 530's electrical structure
           - Panel and breaker organization
           - Relationships between panels and breakers
           
        3. Detailed Analysis:
           - Fetched data analysis for specific time periods
           - Event patterns and frequencies
           - Time-series data analysis
           - Comparative analysis between different periods
           - Identification of significant patterns or anomalies

        Guidelines:
        - Focus on providing clear, actionable insights
        - Use specific numbers and data points when available
        - Explain the significance of any patterns or trends
        - Maintain a professional and informative tone
        
        refer to the following retrieved data type:
        {query_type}),
        and selected data:
        {selected_data}"""),
        ("user", "{query}")
    ])

    # 선택된 데이터 수집
    selected_data = {}
    if state["query_type"] == "building":
        selected_data = state["building_info"]
    elif state["query_type"] == "hierarchy":
        selected_data = state["building_hierarchy"]
    elif state["query_type"] == "detail":
        selected_data = state["fetched_gen_data"]

    # LLM 체인 실행
    chain = prompt | state["llm"]
    response = chain.invoke({
        "query": state["query"],
        "query_type": state["query_type"],
        "selected_data": selected_data
    })

    # chat_history 안전하게 처리
    chat_history = state.get("chat_history", [])
    add_ai_answer_to_chat_history = chat_history + [{"role": "FDD Copilot", "content": response.content}]

    return {
        **state,
        "answer": response.content,
        "chat_history": add_ai_answer_to_chat_history
    }