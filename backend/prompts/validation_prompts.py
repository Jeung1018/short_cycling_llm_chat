from langchain.prompts import PromptTemplate

VALIDATION_PROMPT = PromptTemplate(
    input_variables=["query"],
    template="""
    Analyze the following query about building data:
    Query: {query}

    Determine:
    1. If it specifically references Building 530
    2. If it relates to October 2024
    3. If it involves short cycling analysis
    4. The type of query (building/panel/breaker/date/hierarchy)

    Return a JSON with these exact fields:
    {{
        "is_building_530": boolean,
        "is_october_2024": boolean,
        "is_short_cycling": boolean,
        "query_type": "building" or "panel" or "breaker" or "date" or "hierarchy"
    }}
    """
) 