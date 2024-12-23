from langchain.prompts import PromptTemplate

BREAKER_FILTER_PROMPT = PromptTemplate(
    input_variables=["query"],
    template="""
    Analyze the following query about building breakers:
    Query: {query}

    Determine:
    1. If the query specifically requests active breakers only
    2. What level of breaker hierarchy is requested

    Return a JSON with these fields:
    {{
        "show_active_only": boolean,
        "hierarchy_level": "all" or "active"
    }}
    """
)

QUERY_ROUTER_PROMPT = PromptTemplate(
    input_variables=["query"],
    template="""
    Analyze the following query about a building system:
    Query: {query}

    Determine the query intent and return a JSON with these exact fields:
    {{
        "query_type": "building" or "breaker" or "hierarchy",
        "is_active_only": boolean,
        "detail_level": "summary" or "detailed"
    }}

    Examples:
    1. "Show me Building 530's structure" -> hierarchy query
    2. "Show me active breakers" -> breaker query with active_only=true
    3. "Tell me about Building 530" -> building query
    """
) 