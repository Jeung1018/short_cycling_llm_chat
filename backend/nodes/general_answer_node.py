from models.state import State
from langchain.prompts import ChatPromptTemplate

def general_answer_node(state: State) -> State:
    """
    LLM을 사용하여 일반적인 질문에 대한 답변을 생성하는 노드
    """
    print('---ROUTE: GENERAL ANSWER---')
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a helpful assistant for the T-Mobile Albuquerque CDC (ALBRNMFE) building management system.

        System Context:
        - This system manages power consumption data collected at 1-minute intervals for October 2024
        - The building contains multiple electrical panels, each housing multiple circuit breakers
        - Each breaker's power usage is monitored and analyzed for patterns and anomalies
        
        Available State Data:
        - building_info: Contains building details, panel information, and historical data
        - active_breakers: Lists currently active breakers and their status
        - building_hierarchy: Contains building's electrical hierarchy structure
        
        Instructions:
        1. Analyze the provided state data carefully
        2. Use specific numbers and details from the state data in your response
        3. If relevant information exists in the state data, prioritize using it
        4. Provide clear, specific, and data-driven responses
        
        Current state data:
        {state_data}
        
        Remember to reference actual values and information from the state data in your response."""),
        ("user", "{query}")
    ])
    
    # state 데이터 준비
    state_data = {
        "building_info": state.get("building_info", {}),
        "active_breakers": state.get("active_breakers", {}),
        "building_hierarchy": state.get("building_hierarchy", {})
    }
    
    # LLM 체인 실행
    chain = prompt | state["llm"]
    response = chain.invoke({
        "query": state["query"],
        "state_data": str(state_data)
    })
    
    return {
        **state,
        "answer": response.content
    } 