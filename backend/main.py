from workflow import create_workflow
from models.state import State
from langchain_openai import ChatOpenAI
from config import OPENAI_API_KEY, LLM_MODEL, LLM_TEMPERATURE
from langgraph.types import interrupt, Command


def test_query(query: str) -> None:
    """테스트 쿼리 실행"""
    print("\n" + "="*50)
    print(f"Processing Query: {query}")
    print("="*50)
    
    # LLM 모델 초기화
    llm = ChatOpenAI(
        model_name=LLM_MODEL,
        temperature=LLM_TEMPERATURE,
        openai_api_key=OPENAI_API_KEY
    )    
    # 워크플로우 생성
    workflow = create_workflow()
      
    # thread_id 설정
    thread_config = {"configurable": {"thread_id": "test_session"}}
    
    # 첫 번째 실행 - human interaction interrupt까지
    result = workflow.invoke(State(query=query, llm=llm), config=thread_config)
    print("\nCurrent Answer:")
    print(result.get("answer", "No answer generated"))
    
    # 사용자 입력 받기 (yes/no)
    user_input = input("\nWould you like to ask an additional question? (yes/no)\n")
    
    # 두 번째 실행 - additional question interrupt까지
    result = workflow.invoke(Command(resume=user_input), config=thread_config)
    print("\nCurrent Answer:")
    print(result.get("answer", "No answer generated"))
    
    # 추가 질문 받기
    if user_input.lower() == 'yes':
        additional_question = input("\nWhat is your additional question?\n")
        result = workflow.invoke(Command(resume=additional_question), config=thread_config)
        print("\nFinal Answer:")
        print(result.get("answer", "No answer generated"))

    # 사용자 입력 받기 (yes/no)
    user_input = input("\nWould you like to ask an additional question? (yes/no)\n")

    # 세 번째 실행 - additional question interrupt까지
    result = workflow.invoke(Command(resume=user_input), config=thread_config)
    print("\nCurrent Answer:")
    print(result.get("answer", "No answer generated"))

    # 추가 질문 받기
    if user_input.lower() == 'yes':
        additional_question = input("\nWhat is your additional question?\n")
        result = workflow.invoke(Command(resume=additional_question), config=thread_config)
        print("\nFinal Answer:")
        print(result.get("answer", "No answer generated"))


if __name__ == "__main__":
    # 단일 쿼리 테스트
    test_query("Tell me about Building 530's short cycling trend")
    
    # 나중에 테스트할 쿼리들
    """
    queries = [
        "Show me all active breakers"
        "Tell me about Building 530",
        "Show me Building 530's structure",
        "What's the weather like today?"
    ]
    """ 