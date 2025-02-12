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
            "llm": st.session_state.llm
        })
        state = st.session_state.workflow.invoke(
            initial_state,
            config=thread_config
        )
    else:
        # Resume from previous state with new query
        current_state = st.session_state.current_state
        current_state["query"] = query  # Update the query in the current state
        state = st.session_state.workflow.invoke(
            Command(resume=query),
            config=thread_config
        )
    
    # Store the updated state in session_state
    st.session_state.current_state = state
    
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
st.title("FDD Copilot Prototype")

with st.expander("About This Prototype", expanded=False):
    about_content = load_markdown_content('about.md')
    st.markdown(about_content)

query = st.text_area("Enter your query:", height=100)


# Query submission
if st.button("Submit", key="submit"):
    if query:
        try:
            with st.spinner("Asking FDD Copilot..."):
                # Process the query and get the updated state
                state = run_workflow(query)

                # Store the new state in session_state
                st.session_state.current_state = state

                st.success("Generated Answer:")
                st.write(state["answer"])

                # Display suggested follow-up questions if available
                if "rec_questions" in state:
                    st.markdown("---")
                    st.subheader("💡 Suggested follow-up questions:")
                    for i, q in enumerate(state["rec_questions"], 1):
                        st.markdown(f"**{i}.** {q}")

        except Exception as e:
            st.error(f"An error occurred: {e}")
    else:
        st.warning("Please enter a query.")


# Sidebar for chat history
with st.sidebar:
    st.markdown("## 💬 Chat History")

    # Clear history button
    if st.button("Clear History", key="clear_history"):
        clear_session_state()
        st.info("Chat history cleared.")     

    
    # Check if 'current_state' and 'chat_history' exist in session_state
    if 'current_state' in st.session_state and "chat_history" in st.session_state.current_state:
        chat_history = st.session_state.current_state["chat_history"]

        if chat_history:
            # Iterate over chat history in pairs (user_message, assistant_message)
            for user_message, assistant_message in zip(chat_history[::2], chat_history[1::2]):
                # Get the user's question
                user_content = user_message.get("content", "No content available")

                # Get the assistant's response
                assistant_content = assistant_message.get("content", "No response available")

                # Display the question
                st.markdown(f"**You: {user_content}**")

                # Display the answer inside an expander
                st.markdown("**FDD Copilot:**")
                with st.expander("Show Answer", expanded=False):
                    st.markdown(assistant_content)

                # Add a separator for readability
                st.markdown("---")
            
            # Handle case where there's an extra user question without a response
            if len(chat_history) % 2 != 0:
                last_question = chat_history[-1].get("content", "No content available")
                st.markdown(f"**You: {last_question}**")
                st.markdown("**FDD Copilot:** No response available.")

        else:
            st.info("No chat history yet.")
    else:
        st.info("No chat history available.")

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

