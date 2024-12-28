import sys
import os
from bson import ObjectId
import json

# 현재 파일의 디렉토리 경로를 찾습니다
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
backend_dir = os.path.join(project_root, 'backend')

# 두 경로 모두 Python 경로에 추가
sys.path.append(project_root)
sys.path.append(backend_dir)

import streamlit as st
from datetime import datetime
from backend.workflow import create_workflow 
from backend.config import OPENAI_API_KEY, LLM_MODEL, LLM_TEMPERATURE
from langchain_openai import ChatOpenAI
from backend.models.state import State
from utils.session_manager import (
    init_session_state,
    update_chat_history,
    update_session_state,
    clear_session_state
)

class MongoJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        return super().default(obj)

def format_chat_history(history):
    """
    채팅 기록을 문자열 리스트로 변환
    """
    formatted_history = []
    for item in history:
        formatted_history.extend([
            f"User: {item['query']}",
            f"Assistant: {item['answer']}"
        ])
    return formatted_history

def run_workflow(query: str, previous_docs=None, conversation_history=None):
    """
    워크플로우를 실행하고 결과를 반환하는 함수
    """
    # LLM 모델 초기화
    llm = ChatOpenAI(
        model_name=LLM_MODEL,
        temperature=LLM_TEMPERATURE,
        openai_api_key=OPENAI_API_KEY
    )
    
    # 워크플로우 생성
    workflow = create_workflow()
    
    # thread_id 설정
    thread_config = {"configurable": {"thread_id": "streamlit_session"}}
    
    # chat_history를 문자열 리스트로 변환
    formatted_history = format_chat_history(conversation_history) if conversation_history else []
    
    # previous_docs가 있다면 ObjectId를 문자열로 변환
    if previous_docs:
        previous_docs = json.loads(json.dumps(previous_docs, cls=MongoJSONEncoder))
    
    # 워크플로우 실행
    result = workflow.invoke(
        State(
            query=query, 
            llm=llm,
            previous_docs=previous_docs or [],
            chat_history=formatted_history
        ),
        config=thread_config
    )
    
    # 결과에서 필요한 정보 추출
    response = result.get("answer", "Sorry, I couldn't generate an answer.")
    
    # fetched_docs에서 ObjectId를 문자열로 변환
    fetched_docs = json.loads(json.dumps(result.get("fetched_gen_data", []), cls=MongoJSONEncoder))
    
    last_interaction = {
        "query": query,
        "answer": response,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    return response, fetched_docs, last_interaction

# Initialize session state
init_session_state()

# Streamlit UI
st.title("Interactive Anomalies Detection")
st.write("Interact with the LangGraph workflow by asking a question below.")

# Description of the Prototype
with st.expander("About This Prototype", expanded=False):
    st.markdown("""
    This app is designed to analyze **short cycling energy anomalies** for **Building 530** during the **month of October 2024**.

    #### What You Can Do:
    - **Ask Questions About Short Cycling**:
      - Examples:
        - "Is there any short cycling in Building 530?"
        - "Is there any short cycling in Building 530 on Oct 15th?"
        - "How many short cycles occurred on breaker 28722?"
    - **Get Summarized Insights**:
      - Total short cycles and recommendations for identified issues.
    - **Follow-Up Questions**:
      - Refine or expand your queries based on previous answers.

    #### Important Notes:
    - This app **only supports queries** about **Building 530** and **short cycling** for **October 2024**.
    - Unsupported queries will guide you back to the app's focus.

    Start exploring anomalies and trends with precise, contextualized insights!
    """)

# User query input
query = st.text_input("Enter your query:", placeholder="Type your question here...")

# Submit button
if st.button("Submit"):
    if query:
        try:
            with st.spinner("Processing your query..."):
                # Run workflow and get results
                response, fetched_docs, last_interaction = run_workflow(
                    query,
                    previous_docs=st.session_state.previous_docs,
                    conversation_history=st.session_state.history
                )

                # Update session state
                update_session_state(last_interaction, fetched_docs)
                update_chat_history(query, response)

                # Display answer
                st.success("Generated Answer:")
                st.write(response)

        except Exception as e:
            st.error(f"An error occurred: {e}")
    else:
        st.warning("Please enter a query.")

# Display chat history
st.subheader("Chat History:")
if st.session_state.history:
    for item in st.session_state.history:
        st.markdown(f"**[{item['timestamp']}] Q: {item['query']}**")
        st.markdown(f"A: {item['answer']}")
        st.markdown("---")
else:
    st.info("No chat history yet.")

# Clear History button
if st.button("Clear History"):
    clear_session_state()
    st.info("Chat history cleared.") 