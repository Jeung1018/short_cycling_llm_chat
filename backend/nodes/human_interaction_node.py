from typing import Literal
from langgraph.types import interrupt, Command, Send
from models.state import State
from langgraph.graph import END, START, StateGraph, MessagesState


def human_interaction_node(state: State) -> Command[Literal["additional_question", END]]:
    """사용자 입력을 받아 추가 질문 여부를 결정하는 노드"""
    print('---ROUTE: HUMAN INTERACTION---')
    
    # 현재 대화 기록 가져오기
    chat_history = state.get("chat_history", [])
    current_answer = state.get("answer", "No answer generated")
    
    # 현재 답변을 대화 기록에 추가
    if current_answer:
        chat_history = chat_history + [{"role": "FDD Copilot", "content": current_answer}]
    
    # print("Before interrupt - Current state:", state)
    
    # interrupt를 통해 워크플로우를 일시 중단하고 Streamlit으로부터의 입력을 기다림
    query = interrupt(
        {
            "current_answer": current_answer,  # Streamlit UI에 표시할 현재 답변
        }
    )
    
    print("After interrupt - Received query:", query)
    print("After interrupt - Query type:", type(query))
    
    # Streamlit에서 resume=query로 전달된 값이 여기서 처리됨
    if isinstance(query, str) and query.strip():
        updated_chat_history = chat_history + [{"role": "You", "content": query}]
        print(f"Query: {query}")
        print(f"Updated chat history after user input: {updated_chat_history}")
        
        return Command(
            goto="check_data_required",
            update={
                #"chat_history": updated_chat_history,
                "query": query
            }
        )
    return Command(goto=END) 