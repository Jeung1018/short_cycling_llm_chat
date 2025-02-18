from models.state import State
from prompts.answer_with_fetched_data_prompts import ANSWER_WITH_FETCHED_DATA_PROMPT

def answer_w_fetched_data_node(state: State) -> State:
    """
    조회된 데이터를 기반으로 사용자의 질문에 답변하는 노드
    """
    print('---ROUTE: ANSWER WITH FETCHED DATA NODE---')

    # 필요한 데이터 확인
    fetched_data = state.get("fetched_data")
    if not fetched_data:
        return {
            **state,
            "answer": "Sorry, no data found. Please try asking a different question about Building 530's short cycling events in October 2024. We are continuously improving our AI to better understand and find relevant data for your queries.",
            "chat_history": state.get("chat_history", []) + ["Sorry, no data found. Please try asking a different question about Building 530's short cycling events in October 2024. We are continuously improving our AI to better understand and find relevant data for your queries."]
        }

    # LLM 체인 실행
    chain = ANSWER_WITH_FETCHED_DATA_PROMPT | state["llm"]
    response = chain.invoke({
        "query": state["query"],
        "fetched_data": str(fetched_data),
        "chat_history": str(state.get("chat_history", []))
    })

    print(f"Generated Answer: {response.content}")

    # chat_history 업데이트
    current_chat_history = state.get("chat_history", [])
    print(f"current_chat_history: {current_chat_history}")
    updated_chat_history = current_chat_history + [
        {"role": "Fdd Copilot", "content": response.content}
    ]

    print("State contents:", dict(state))  # vars(state) 대신 dict(state) 사용
    
    return {
        **state,
        "answer": response.content,
        "chat_history": updated_chat_history
    } 