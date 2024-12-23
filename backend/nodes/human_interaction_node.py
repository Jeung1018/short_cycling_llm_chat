from typing import Literal
from langgraph.types import interrupt, Command
from models.state import State
from langgraph.graph import END, START, StateGraph, MessagesState


def human_interaction_node(state: State) -> Command[Literal["additional_question", END]]:
    """사용자 입력을 받아 추가 질문 여부를 결정하는 노드"""
    print('---ROUTE: HUMAN INTERACTION---')
    
    # 현재 답변을 사용자에게 보여주고 입력 받기
    user_input = interrupt(
        {
            "current_answer": state.get("answer", "No answer generated"),
            "question": "Would you like to ask an additional question? (yes/no)"
        }
    )
    
    # 사용자 입력에 따라 다음 노드 결정
    if isinstance(user_input, str) and user_input.lower() == "yes":
        return Command(goto="additional_question")
    return Command(goto=END) 