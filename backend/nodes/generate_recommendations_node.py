from models.state import State
from prompts.gen_rec_prompts import GEN_REC_PROMPT

def generate_recommendations_node(state: State) -> State:
    """
    대화 기록과 현재 컨텍스트를 분석하여 추천 질문을 생성하는 노드
    """
    print('---ROUTE: GENERATE RECOMMENDATIONS---')

    # LLM 체인 실행
    chain = GEN_REC_PROMPT | state["mongo_query_model"]
    response = chain.invoke({
        "query": state.get("query"),
        "answer": state.get("answer", ""),
        "chat_history": state.get("chat_history", [])  # 기본값으로 빈 리스트 사용
    })

    # 응답을 리스트로 파싱
    rec_questions = [
        q.strip().split(". ", 1)[1] if ". " in q.strip() else q.strip()
        for q in response.content.strip().split("\n")
        if q.strip()
    ][:3]  # 3개 질문만 사용

    return {
        **state,
        "rec_questions": rec_questions
    } 