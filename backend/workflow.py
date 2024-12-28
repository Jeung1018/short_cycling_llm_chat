from typing import Any, Dict
from langgraph.graph import END, START, StateGraph, MessagesState
from langgraph.checkpoint.memory import MemorySaver
from backend.models.state import State
from nodes.check_data_required_node import check_data_required_node, check_data_required_rf
from nodes.data_router_node import data_router_node, data_router_rf
from nodes.breaker_filter_node import breaker_filter_node
from nodes.fetch_active_breakers_node import fetch_active_breakers_node
from nodes.format_response_node import format_response_node
from nodes.building_analysis_node import building_analysis_node
from nodes.hierarchy_analysis_node import hierarchy_analysis_node
from nodes.general_answer_node import general_answer_node
from nodes.additional_question_node import additional_question_node
from nodes.human_interaction_node import human_interaction_node
from nodes.mongo_gen_query_node import mongo_gen_query_node
from nodes.fetch_gen_query_node import fetch_gen_query_node
from nodes.answer_fetched_gen_data_node import answer_fetched_gen_data_node




from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel
from langchain_core.messages import HumanMessage
import operator

class QueryIntent(BaseModel):
    query_type: str
    is_active_only: bool
    detail_level: str

def create_workflow() -> Any:
    """전체 워크플로우를 생성하고 설정하는 함수"""
    # StateGraph 생성
    workflow = StateGraph(State)
    
    # Nodes
    workflow.add_node("check_data_required", check_data_required_node)
    workflow.add_node("data_router", data_router_node)
    workflow.add_node("breaker_filter", breaker_filter_node)
    workflow.add_node("fetch_active_breakers", fetch_active_breakers_node)
    workflow.add_node("building_analysis", building_analysis_node)


    workflow.add_node("mongo_gen_query", mongo_gen_query_node)
    workflow.add_node("fetch_gen_query", fetch_gen_query_node)
    workflow.add_node("answer_fetched_gen_data", answer_fetched_gen_data_node)



    workflow.add_node("format_response", format_response_node)
    workflow.add_node("human_interaction", human_interaction_node)
    workflow.add_node("additional_question", additional_question_node)
    workflow.add_node("hierarchy_analysis", hierarchy_analysis_node)
    workflow.add_node("general_answer", general_answer_node)
    
    # 시작점 설정
    workflow.set_entry_point("check_data_required")
    
    # 데이터 필요 여부 확인을 위한 라우팅
    workflow.add_conditional_edges(
        'check_data_required',
        check_data_required_rf,
        {
            'fetch_data': 'data_router',
            'general_answer': 'general_answer'
        }
    )
    
    # 데이터 타입에 따른 라우팅
    workflow.add_conditional_edges(
        'data_router',
        data_router_rf,
        {
            'breaker_filter': 'breaker_filter',
            'building_analysis': 'building_analysis',
            'hierarchy_analysis': 'hierarchy_analysis',
            'detail_analysis' : 'mongo_gen_query'
        }
    )

    workflow.add_edge("mongo_gen_query", "fetch_gen_query")
    workflow.add_edge("fetch_gen_query", "answer_fetched_gen_data")
    workflow.add_edge("answer_fetched_gen_data", "human_interaction")

    # 나머지 엣지 연결
    workflow.add_edge("breaker_filter", "fetch_active_breakers")
    workflow.add_edge("fetch_active_breakers", "format_response")
    workflow.add_edge("format_response", "human_interaction")
    workflow.add_edge("building_analysis", "format_response")
    workflow.add_edge("hierarchy_analysis", "format_response")
    workflow.add_edge("general_answer", "human_interaction")
    workflow.add_edge("additional_question", "check_data_required")

    
    # 체크포인터 추가
    checkpointer = MemorySaver()
    
    return workflow.compile(checkpointer=checkpointer)
