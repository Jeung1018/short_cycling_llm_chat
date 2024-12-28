from models.state import State
from prompts.answer_fetched_gen_data_prompts import ANSWER_FETCHED_GEN_DATA_PROMPT

def answer_fetched_gen_data_node(state: State) -> State:
    """
    조회된 데이터를 기반으로 사용자의 질문에 답변하는 노드
    """
    print('---ROUTE: ANSWER FETCHED GEN DATA NODE---')

    # 필요한 데이터 확인
    fetched_gen_data = state.get("fetched_gen_data")
    if not fetched_gen_data:
        return {
            **state,
            "answer": "죄송합니다. 데이터를 찾을 수 없습니다.",
            "chat_history": state.get("chat_history", []) + ["죄송합니다. 데이터를 찾을 수 없습니다."]
        }

    # LLM 체인 실행
    chain = ANSWER_FETCHED_GEN_DATA_PROMPT | state["llm"]
    response = chain.invoke({
        "query": state["query"],
        "fetched_gen_data": str(fetched_gen_data),
        "chat_history": str(state.get("chat_history", []))
    })

    print(f"Generated Answer: {response.content}")

    # chat_history 업데이트
    current_chat_history = state.get("chat_history", [])
    updated_chat_history = current_chat_history + [
        f"User: {state['query']}",
        f"Assistant: {response.content}"
    ]

    return {
        **state,
        "answer": response.content,
        "chat_history": updated_chat_history
    } 