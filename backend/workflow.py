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


from nodes.mongo_query_gen_node import mongo_query_gen_node
from nodes.validate_fetch_data_node import validate_fetch_data_node, validate_fetch_data_rf
from nodes.validate_mongo_query_node import validate_mongo_query_node, validate_mongo_query_rf
from nodes.regen_mongo_query_node import regen_mongo_query_node, regen_mongo_query_rf
from nodes.narrow_down_mongo_query_node import narrow_down_mongo_query_node, narrow_down_mongo_query_rf

from nodes.fetch_gen_query_node import fetch_gen_query_node
from nodes.answer_fetched_gen_data_node import answer_fetched_gen_data_node
from nodes.generate_recommendations_node import generate_recommendations_node

from nodes.error_node import error_node

from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel
from langchain_core.messages import HumanMessage
import operator
import sys
import logging
from datetime import datetime

class QueryIntent(BaseModel):
    query_type: str
    is_active_only: bool
    detail_level: str

def create_workflow() -> Any:
    """전체 워크플로우를 생성하고 설정하는 함수"""
    # Configure both logging and stdout redirection
    log_filename = f'workflow_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
    
    # Configure logging
    logging.basicConfig(
        filename=log_filename,
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        encoding='utf-8'
    )

    # Redirect stdout to both console and file
    class TeeStream:
        def __init__(self, filename, stream):
            self.terminal = stream
            self.file = open(filename, 'a', encoding='utf-8')

        def write(self, message):
            self.terminal.write(message)
            self.file.write(message)
            self.file.flush()

        def flush(self):
            self.terminal.flush()
            self.file.flush()

    sys.stdout = TeeStream(log_filename, sys.stdout)
    
    # StateGraph 생성
    workflow = StateGraph(State)
    
    # Nodes
    workflow.add_node("check_data_required", check_data_required_node)
    workflow.add_node("data_router", data_router_node)
    workflow.add_node("breaker_filter", breaker_filter_node)
    workflow.add_node("fetch_active_breakers", fetch_active_breakers_node)
    workflow.add_node("building_analysis", building_analysis_node)


    workflow.add_node("mongo_query_gen", mongo_query_gen_node)
    workflow.add_node("validate_mongo_query", validate_mongo_query_node)
    workflow.add_node("regen_mongo_query", regen_mongo_query_node)

    workflow.add_node("narrow_down_mongo_query", narrow_down_mongo_query_node)

    workflow.add_node("error", error_node)

    workflow.add_node("fetch_gen_query", fetch_gen_query_node)
    workflow.add_node("validate_fetch_data", validate_fetch_data_node)
    workflow.add_node("answer_fetched_gen_data", answer_fetched_gen_data_node)

    workflow.add_node("format_response", format_response_node)

    workflow.add_node("generate_recommendations", generate_recommendations_node)
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
            'detail_analysis' : 'mongo_query_gen'
        }
    )

    workflow.add_edge("mongo_query_gen", "validate_mongo_query")

    workflow.add_conditional_edges(
            'validate_mongo_query',
            validate_mongo_query_rf,
            {
                'valid_mongo_query': 'fetch_gen_query',
                'regen_mongo_query': 'regen_mongo_query'
            }
    )

    workflow.add_edge("fetch_gen_query", "validate_fetch_data")
    workflow.add_conditional_edges(
            'validate_fetch_data',
            validate_fetch_data_rf,
            {
                'valid_fetch_data': 'answer_fetched_gen_data',
                'regen_mongo_query': 'regen_mongo_query',
                'narrow_down_mongo_query': 'narrow_down_mongo_query'
            }
    )

    workflow.add_conditional_edges(
            'narrow_down_mongo_query',
            narrow_down_mongo_query_rf,
            {
                'narrow_downed_success': 'validate_mongo_query',
                'error': 'error'
            }
    )



    workflow.add_conditional_edges(
            'regen_mongo_query',
            regen_mongo_query_rf,
            {
                'error': 'error',
                'regened_mongo_query': 'fetch_gen_query',
                'fetch_data': 'fetch_gen_query'
            }
    )

    workflow.add_edge("answer_fetched_gen_data", "generate_recommendations")
    workflow.add_edge("generate_recommendations", "human_interaction")

    workflow.add_edge("error", "human_interaction")

    # 나머지 엣지 연결
    workflow.add_edge("breaker_filter", "fetch_active_breakers")
    workflow.add_edge("fetch_active_breakers", "format_response")
    workflow.add_edge("format_response", "generate_recommendations")
    workflow.add_edge("generate_recommendations", "human_interaction")

    workflow.add_edge("building_analysis", "format_response")
    workflow.add_edge("hierarchy_analysis", "format_response")
    workflow.add_edge("general_answer", "generate_recommendations")
    workflow.add_edge("generate_recommendations", "human_interaction")
    
    workflow.add_edge("additional_question", "check_data_required")

    
    # 체크포인터 추가
    checkpointer = MemorySaver()
    
    return workflow.compile(checkpointer=checkpointer)

