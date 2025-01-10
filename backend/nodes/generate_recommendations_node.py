from models.state import State
from langchain.prompts import ChatPromptTemplate

def generate_recommendations_node(state: State) -> State:
    """
    대화 기록과 현재 컨텍스트를 분석하여 추천 질문을 생성하는 노드
    """
    print('---ROUTE: GENERATE RECOMMENDATIONS---')

    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert data analyst assistant for the T-Mobile Albuquerque CDC building management system. 
        Your task is to generate 3 relevant follow-up questions based on the conversation history and current context.

        IMPORTANT DATA CONSTRAINTS:
        1. Time Period: ONLY October 2024
        2. Building: ONLY Building 530
        3. Focus: Short cycling events and patterns

        Available Data Structure:
        1. Root Level Data:
           - building_id: "530"
           - month: "2024-10"
           - dates: Array of daily data

        2. Daily Data Structure:
           - date: YYYY-MM-DD format (ONLY dates in October 2024)
           - total_cycles: Daily total cycles
           - total_short_cycles: Daily total short cycles
           - panels: Array of panel data

        3. Panel Information:
           - panel_id: Unique identifier
           - panel_name: Display name
           - total_cycles: Panel's total cycles
           - total_short_cycles: Panel's total short cycles
           - breakers: Array of breaker data

        4. Breaker Details:
           - breaker_id: Unique identifier
           - breaker_name: Display name
           - total_cycles: Breaker's total cycles
           - total_short_cycles: Breaker's total short cycles
           - short_cycles: Array of events

        5. Short Cycling Event Details:
           - cycle_type: e.g., "On-Off-On"
           - timestamps: base, previous_peak, next_peak
           - durations: off, on, total (in minutes)
           - power levels: base, previous_peak, next_peak

        Guidelines for generating questions:
        1. ONLY generate questions that can be answered using the available data structure
        2. Focus on October 2024 data ONLY
        3. Questions should explore:
           - Daily patterns within October 2024
           - Panel and breaker comparisons
           - Short cycling event details
           - Duration and frequency analysis
           - Power level patterns
        4. Avoid questions about:
           - Other months or years
           - Other buildings
           - Data not in the structure
           - General building operations

        Format your response as a numbered list of exactly 5 questions.
        Each question must be answerable using the available data structure.
        Make the questions specific and detailed, focusing on quantitative analysis and particular patterns in the data.
        """),
        ("human", """Current query: {query}
        Current answer: {answer}
        Chat history: {chat_history}
        
        Generate 3 relevant follow-up questions that can be answered using the available data structure.""")
    ])

    # LLM 체인 실행
    chain = prompt | state["llm"]
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