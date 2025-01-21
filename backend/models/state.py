from typing import TypedDict, List, Dict, Any, Optional

class State(TypedDict):
    """Conversation state model with structured output"""
    query: str
    chat_history: List[Any]
    current_input: Optional[str]
    validation_result: Optional[Dict[str, Any]]
    analysis_result: Optional[Dict[str, Any]]
    llm: Any
    docs: List[Any]
    answer: str
    mongo_query: Dict[str, Any]
    building_id: str
    date: str
    date_type: str
    date_range: Dict[str, Any]
    terminate: bool
    analysis_results: Dict[str, Any]
    recommendations: Dict[str, Any]
    breaker_filter_result: Dict[str, Any]
    query_intent: Dict[str, Any]
    active_breakers: Dict[str, Any]
    building_info: Dict[str, Any]
    needs_data: bool
    building_hierarchy: Dict[str, Any]
    mongo_query: str
    fetched_gen_data: List[Dict[str, Any]]
    rec_questions: List[Dict[str, Any]]
    token_count: int
    validation_errors: str
    validation_query: str
    narrowed_mongo_query: str
    invalid_query_reason: str
    database_structure: Dict[str, Any]
    query_narrowed_count: int
    query_regen_count: int
    original_mongo_query: str
    data_truncated: bool
    validate_query_model: Any
    mongo_query_model: Any


