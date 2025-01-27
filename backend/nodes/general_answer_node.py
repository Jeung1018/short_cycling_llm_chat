from models.state import State
from prompts.general_answer_prompts import GENERAL_ANSWER_PROMPT

def general_answer_node(state: State) -> State:
    """
    LLM을 사용하여 일반적인 질문에 대한 답변을 생성하는 노드
    """
    print('---ROUTE: GENERAL ANSWER---')
    
    # LLM 체인 실행
    chain = GENERAL_ANSWER_PROMPT | state["llm"]
    response = chain.invoke({
        "query": state["query"],
        "state_data": str(state)  # 전체 state를 전달
    })

    print(f"LLM Response: {response.content}")
    
       # chat_history 안전하게 처리
    chat_history = state.get("chat_history", [])
    add_ai_answeer_to_chat_history = chat_history + [{"role": "FDD Copilot", "content": response.content}]

    return {
        **state,
        "answer": response.content,
        "chat_history": add_ai_answeer_to_chat_history
    }
