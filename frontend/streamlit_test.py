import sys
import os
import json
from bson import ObjectId
import streamlit as st

# 현재 파일의 디렉토리 경로를 찾습니다
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
backend_dir = os.path.join(project_root, 'backend')

# 두 경로 모두 Python 경로에 추가
sys.path.append(project_root)
sys.path.append(backend_dir)

from backend.workflow import create_workflow
from backend.config import OPENAI_API_KEY, LLM_MODEL, LLM_TEMPERATURE
from langchain_openai import ChatOpenAI
from backend.models.state import State
from utils.session_manager import (
    init_session_state,
    update_chat_history,
    clear_session_state
)



# JSON encoder for ObjectId conversion
class MongoJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        return super().default(obj)

def convert_objectid(obj):
    """Recursively convert ObjectId instances in a structure to strings."""
    if isinstance(obj, ObjectId):
        return str(obj)
    elif isinstance(obj, dict):
        return {k: convert_objectid(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_objectid(i) for i in obj]
    return obj

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
            current_state,
            config=thread_config
        )
    
    # Store the interrupted state for next query
    st.session_state.current_state = state
    
    # Convert state to ensure no ObjectId remains
    state = convert_objectid(state)
    
    return state


# Initialize session state
init_session_state()

# Main UI
st.title("Test Workflow App")

# Input text box
query = st.text_input("Enter your query:")

# Button to test run workflow
if st.button("Test Run Workflow"):
    if query:
        try:
            with st.spinner("Processing your query..."):
                state = run_workflow(query)
                
                # Print raw state for debugging
                st.subheader("Raw State Data:")
                st.json(state)  # Show the raw state as JSON

                st.success("Generated Answer:")
                st.write(state.get("answer", "No answer generated"))

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
