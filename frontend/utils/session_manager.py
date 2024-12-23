import streamlit as st
from typing import Dict, Optional, List
from datetime import datetime

def init_session_state():
    """Initialize session state variables"""
    if "history" not in st.session_state:
        st.session_state["history"] = []
    if "previous_docs" not in st.session_state:
        st.session_state["previous_docs"] = None

def update_chat_history(query: str, response: str):
    """Update chat history with new query and response"""
    st.session_state["history"].append({
        "query": query,
        "answer": response,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

def update_session_state(last_interaction: Dict, fetched_docs: Optional[List] = None):
    """Update session state with latest interaction and documents"""
    st.session_state.last_query = last_interaction.get("last_query")
    st.session_state.last_answer = last_interaction.get("last_answer")
    
    if fetched_docs:
        st.session_state.previous_docs = fetched_docs

def clear_session_state():
    """Clear all session state data"""
    st.session_state.history = []
    st.session_state.previous_docs = None 