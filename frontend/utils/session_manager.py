import streamlit as st
from typing import Dict, Optional, List
from datetime import datetime
from bson import ObjectId
import json

class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        return super().default(obj)

def init_session_state():
    """
    세션 상태를 초기화하는 함수
    """
    if 'history' not in st.session_state:
        st.session_state.history = []
    
    if 'previous_docs' not in st.session_state:
        st.session_state.previous_docs = []

def update_chat_history(query: str, answer: str):
    """
    채팅 기록을 업데이트하는 함수
    """
    if 'history' not in st.session_state:
        st.session_state.history = []
    
    # 현재 시간 추가
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # ObjectId를 포함한 데이터를 안전하게 직렬화
    history_item = {
        'timestamp': timestamp,
        'query': query,
        'answer': answer
    }
    
    # JSON으로 직렬화 가능한 형태로 변환
    history_item = json.loads(
        json.dumps(history_item, cls=JSONEncoder)
    )
    
    st.session_state.history.append(history_item)

def update_session_state(state):
    """
    세션 상태를 업데이트하는 함수
    """
    if not hasattr(st.session_state, 'previous_docs'):
        st.session_state.previous_docs = []
    
    if not hasattr(st.session_state, 'history'):
        st.session_state.history = []
    
    if not hasattr(st.session_state, 'rec_questions'):
        st.session_state.rec_questions = []

    # 이전 문서 업데이트
    if "fetched_gen_data" in state:
        st.session_state.previous_docs = state["fetched_gen_data"]

    # 추천 질문 업데이트
    if "rec_questions" in state:
        st.session_state.rec_questions = state["rec_questions"]

def clear_session_state():
    """
    세션 상태를 초기화하는 함수
    """
    st.session_state.history = []
    st.session_state.previous_docs = [] 