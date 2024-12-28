from typing import Dict
from models.state import State
from langchain.prompts import ChatPromptTemplate

def format_response_node(state: State) -> State:
    """
    쿼리 타입에 따라 적절한 응답을 생성하는 노드
    """
    print('---ROUTE: FORMAT RESPONSE---')

    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert data analyst for the T-Mobile Albuquerque CDC (ALBRNMFE) building management system.

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
        
        Current state data:
        {state_data}"""),
        ("user", "{query}")
    ])

    # 선택된 데이터 수집
    selected_data = {}
    if "building_info" in state:
        selected_data["building_info"] = state["building_info"]
    if "building_hierarchy" in state:
        selected_data["building_hierarchy"] = state["building_hierarchy"]
    if "fetched_gen_data" in state:
        selected_data["fetched_gen_data"] = state["fetched_gen_data"]

    # LLM 체인 실행
    chain = prompt | state["llm"]
    response = chain.invoke({
        "query": state["query"],
        "state_data": str(selected_data)
    })

    return {
        **state,
        "answer": response.content
    }