from langgraph.types import interrupt
from models.state import State

def additional_question_node(state: State) -> dict:
    """추가 질문을 받는 노드"""
    print('---ROUTE: ADDITIONAL QUESTION---')
    
    # 사용자로부터 추가 질문 받기
    new_question = interrupt(
        {
            "question": "What is your additional question?"
        }
    )
    
    # 새로운 질문으로 state 업데이트
    return {
        **state,
        "query": new_question,
        "current_input": new_question
    } 