from typing import Dict
from models.state import State
from langchain.prompts import ChatPromptTemplate

def format_response_node(state: State) -> dict:
    """쿼리 분석 후 적절한 데이터를 선택하여 응답을 생성하는 노드"""
    print('---ROUTE: FORMAT RESPONSE---')
    
    print("\nCurrent State in format_response_node:")
    print(state)
    
    try:
        # 데이터 선택을 위한 LLM 프롬프트
        select_data_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a helpful assistant that analyzes user queries and selects appropriate data to respond.
            Available data in state:
            1. active_breakers: Contains information about circuit breakers, their usage, and cycles
            2. building_info: Contains general building information like ID, name, location, total panels/breakers
            3. building_hierarchy: Contains detailed building structure information including panels and breakers organization
            
            Select the most relevant data source(s) based on the user's query.
            Return your answer as a list of data source names, e.g., ["active_breakers", "building_info"]"""),
            ("user", "Here is the user's query: {query}")
        ])
        
        # 데이터 선택
        chain = select_data_prompt | state["llm"]
        
        print("\nLLM Information:")
        print(f"Model Name: {state['llm'].model_name}")
        print(f"Temperature: {state['llm'].temperature}")
        print(f"Model Config: {state['llm'].model_kwargs}")
        
        print("state[llm]: ", state["llm"])
        data_selection_response = chain.invoke({
            "query": state["query"]
        })
        
        print("\nSelected data sources:")
        print(data_selection_response)
        
        # 문자열에서 실제 데이터 소스 목록 추출
        import ast
        data_sources = ast.literal_eval(data_selection_response.content)
        
        # 선택된 데이터 수집
        selected_data = {}
        for source in data_sources:
            if source == "active_breakers" and "active_breakers" in state:
                selected_data["active_breakers"] = state["active_breakers"]
            elif source == "building_info" and "building_info" in state:
                selected_data["building_info"] = state["building_info"]
            elif source == "building_hierarchy" and "building_hierarchy" in state:
                selected_data["building_hierarchy"] = state["building_hierarchy"]
            
        print("\nData sent to LLM:")
        print(selected_data)
        
        # 응답 생성을 위한 LLM 프롬프트
        response_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a helpful assistant that explains building and breaker data. 
            Format the data in a natural, easy to understand way that directly answers the user's query.
            Include relevant numbers and details from the provided data."""),
            ("user", "Here is my query: {query}\n\nHere is the relevant data:\n{data}")
        ])
        
        # 응답 생성
        chain = response_prompt | state["llm"]
        response = chain.invoke({
            "query": state["query"],
            "data": selected_data
        })
        
        return {
            "answer": response.content,
            "chat_history": state.get("chat_history", []) + [response.content]
        }
        
    except Exception as e:
        print(f"Format response error: {str(e)}")
        return {
            "answer": f"Error formatting response: {str(e)}",
            "error": str(e)
        }