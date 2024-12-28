import sys
import os
from bson import ObjectId
import json
import time

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
            f"Human: {item['query']}",
            f"Assistant: {item['answer']}"
        ])
    return formatted_history

def run_workflow(query: str, previous_docs=None, conversation_history=None):
    """
    워크플로우를 실행하고 state를 반환하는 함수
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
    
    # 워크플로우 실행
    state = workflow.invoke(
        State(
            query=query, 
            llm=llm,
            previous_docs=previous_docs or [],
            chat_history=conversation_history or []
        ),
        config=thread_config
    )
    
    return state  # state 전체를 반환

def handle_recommended_question(query_text: str):
    """추천 질문 클릭 핸들러"""
    st.session_state.query = query_text
    st.session_state.run_query = True

# Initialize session state
init_session_state()

# Main content area
st.title("Short Cycling Analysis Chat")

# Description of the Prototype
with st.expander("About This Prototype", expanded=False):
    st.markdown("""
    This app is designed to analyze **short cycling energy anomalies** for **Building 530** during the **month of October 2024**. For each question, the app retrieves relevant data from the database and uses an AI language model to provide detailed, data-driven answers.

    #### Getting Started:
    - **Start with Overview Questions**:
      - Examples:
        - "Give me an overview of short cycling in Building 530 for October 2024"
        - "What is the electrical hierarchy of Building 530?"
        - "Show me the the peak day's detail short cycling trends in Building 530"
    
    #### Deep Dive Analysis:
    - **Follow the Suggested Questions**:
      - Each answer comes with relevant follow-up questions
      - Questions are designed to guide you through:
        - Panel-level analysis
        - Breaker-specific patterns
        - Temporal trends
    
    #### Important Notes:
    - This app analyzes data for **Building 530** during **October 2024**
    - Focus on **short cycling anomalies** and their patterns
    - Use suggested follow-up questions to explore deeper insights

    Start with an overview and follow the suggested questions to explore detailed insights!
    """)

# Main query input
query = st.text_input("Enter your query:")

# Sidebar for chat history
with st.sidebar:
    st.markdown("## 💬 Chat History")
    
    # Clear History button
    if st.button("Clear History", key="clear_history"):
        clear_session_state()
        st.info("Chat history cleared.")
        
    # Display chat history
    if st.session_state.history:
        for item in reversed(st.session_state.history):
            with st.container():
                st.markdown(f"**[{item['timestamp']}]**")
                st.markdown(f"**Q:** {item['query']}")
                with st.expander("Show Answer", expanded=False):
                    st.markdown(item['answer'])
                st.markdown("---")
    else:
        st.info("No chat history yet.")

# Submit button
if st.button("Submit", key="submit"):
    if query:
        try:
            with st.spinner("Processing your query..."):
                formatted_history = format_chat_history(st.session_state.history)
                state = run_workflow(
                    query,
                    previous_docs=st.session_state.previous_docs,
                    conversation_history=formatted_history
                )

                # Display answer in main area
                st.success("Generated Answer:")
                st.write(state["answer"])

                # Update chat history and session state
                update_chat_history(query, state["answer"])
                update_session_state(state)

                # Display recommended questions at the bottom
                if "rec_questions" in state:
                    st.markdown("---")
                    st.subheader("💡 Suggested follow-up questions:")
                    for i, q in enumerate(state["rec_questions"], 1):
                        st.markdown(f"**{i}.** {q}")

        except Exception as e:
            st.error(f"An error occurred: {e}")
    else:
        st.warning("Please enter a query.")

# JavaScript to handle click events
st.markdown("""
<script>
window.addEventListener('message', function(e) {
    if (e.data.type === 'streamlit:setComponentValue') {
        // Set the query in session state
        const queryInput = window.parent.document.querySelector('input[type="text"]');
        if (queryInput) {
            queryInput.value = e.data.value;
            queryInput.dispatchEvent(new Event('input', { bubbles: true }));
        }
    }
});
</script>
""", unsafe_allow_html=True)

# Add custom CSS
st.markdown("""
<style>
.recommended-question:hover {
    background-color: #e1e4e8 !important;
}
</style>
""", unsafe_allow_html=True) 