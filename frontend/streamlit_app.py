import sys
import os
from bson import ObjectId
import json
from datetime import datetime

# 현재 파일의 디렉토리 경로를 찾습니다
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
backend_dir = os.path.join(project_root, 'backend')

# 두 경로 모두 Python 경로에 추가
sys.path.append(project_root)
sys.path.append(backend_dir)

import streamlit as st
from backend.workflow import create_workflow
from backend.config import OPENAI_API_KEY, LLM_MODEL, LLM_TEMPERATURE
from langchain_openai import ChatOpenAI
from langgraph.types import interrupt, Command
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

def convert_objectid(obj):
    """
    Recursively convert ObjectId instances in a structure to strings.
    """
    if isinstance(obj, ObjectId):
        return str(obj)
    elif isinstance(obj, dict):
        return {k: convert_objectid(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_objectid(i) for i in obj]
    return obj

def format_chat_history(history):
    """
    Format chat history into a string list for conversation context.
    """
    formatted_history = []
    for item in history:
        formatted_history.extend([
            f"Human: {item['query']}",
            f"Assistant: {item['answer']}"
        ])
    return formatted_history

def run_workflow(query: str) -> State:
    """
    Executes the workflow and returns the state.
    """
    # Initialize the LLM model if not exists in session state
    if 'llm' not in st.session_state:
        st.session_state.llm = ChatOpenAI(
            model_name=LLM_MODEL,
            temperature=LLM_TEMPERATURE,
            openai_api_key=OPENAI_API_KEY
        )
    
    # Create workflow if not exists in session state
    if 'workflow' not in st.session_state:
        st.session_state.workflow = create_workflow()
    
    # Configure thread_id
    thread_config = {"configurable": {"thread_id": "streamlit_session"}}
    
    if 'current_state' not in st.session_state:
        # First query - initialize new state
        initial_state = State({
            "query": query,
            "llm": st.session_state.llm,
            "chat_history": st.session_state.history if 'history' in st.session_state else []  # 기존 히스토리 전달
        })
        state = st.session_state.workflow.invoke(
            initial_state,
            config=thread_config
        )
    else:
        # Resume from previous state with new query
        current_state = st.session_state.current_state
        current_state["query"] = query  # Update the query in the current state
        current_state["chat_history"] = st.session_state.history if 'history' in st.session_state else []  # 기존 히스토리 전달
        state = st.session_state.workflow.invoke(
            Command(resume=query),
            config=thread_config
        )
    
    # Store the interrupted state for next query
    st.session_state.current_state = state
    
    # Convert state to ensure no ObjectId remains
    state = convert_objectid(state)
    
    return state

def handle_recommended_question(query_text: str):
    """Handles recommended question clicks."""
    st.session_state.query = query_text
    st.session_state.run_query = True

def load_markdown_content(filename):
    """Load markdown content from a file."""
    file_path = os.path.join(current_dir, 'texts', filename)
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        print(f"Error loading markdown file: {e}")
        return "Error loading content."

# Initialize session state
init_session_state()

# Main content area
st.title("Short Cycling Analysis Chat")

with st.expander("About This Prototype", expanded=False):
    about_content = load_markdown_content('about.md')
    st.markdown(about_content)

query = st.text_input("Enter your query:")

# Sidebar for chat history
with st.sidebar:
    st.markdown("## 💬 Chat History")
    
    if st.button("Clear History", key="clear_history"):
        clear_session_state()
        st.info("Chat history cleared.")
        
    if st.session_state.history:
        for item in reversed(st.session_state.history):
            with st.container():
                # Add error handling for missing keys
                timestamp = item.get('timestamp', 'No timestamp')
                query = item.get('query', 'No query available')
                answer = item.get('answer', 'No answer available')
                
                st.markdown(f"**[{timestamp}]**")
                st.markdown(f"**Q:** {query}")
                with st.expander("Show Answer", expanded=False):
                    st.markdown(answer)
                st.markdown("---")
    else:
        st.info("No chat history yet.")

if st.button("Submit", key="submit"):
    if query:
        try:
            with st.spinner("Processing your query..."):
                state = run_workflow(query)

                st.success("Generated Answer:")
                st.write(state["answer"])

                # Use the imported update_chat_history function
                update_chat_history(query=query, answer=state["answer"])

                if "rec_questions" in state:
                    st.markdown("---")
                    st.subheader("💡 Suggested follow-up questions:")
                    for i, q in enumerate(state["rec_questions"], 1):
                        st.markdown(f"**{i}.** {q}")

        except Exception as e:
            print(f"Full error details: {str(e)}")
            st.error(f"An error occurred: {e}")
    else:
        st.warning("Please enter a query.")

st.markdown("""
<script>
window.addEventListener('message', function(e) {
    if (e.data.type === 'streamlit:setComponentValue') {
        const queryInput = window.parent.document.querySelector('input[type="text"]');
        if (queryInput) {
            queryInput.value = e.data.value;
            queryInput.dispatchEvent(new Event('input', { bubbles: true }));
        }
    }
});
</script>
""", unsafe_allow_html=True)

st.markdown("""
<style>
.recommended-question:hover {
    background-color: #e1e4e8 !important;
}
</style>
""", unsafe_allow_html=True)
