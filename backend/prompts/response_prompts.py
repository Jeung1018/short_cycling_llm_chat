from langchain.prompts import PromptTemplate

ACTIVE_BREAKERS_RESPONSE_PROMPT = PromptTemplate(
    input_variables=["query", "active_breakers"],
    template="""
    Based on the user's query about active breakers:
    Query: {query}

    And the active breakers data:
    {active_breakers}

    Provide a clear and informative response that:
    1. Summarizes the number of active panels and breakers
    2. Highlights any notable patterns (e.g., panels with many active breakers)
    3. Answers the specific aspects of the user's query
    4. Suggests relevant follow-up questions if appropriate

    Format the response in a user-friendly way.
    """
)

HIERARCHY_RESPONSE_PROMPT = PromptTemplate(
    input_variables=["query", "hierarchy_data"],
    template="""
    Based on the user's query about building hierarchy:
    Query: {query}

    And the hierarchy data:
    {hierarchy_data}

    Provide a clear and structured response that:
    1. Shows the building's structure clearly
    2. Lists all panels and their associated breakers
    3. Mentions the option to see only active breakers if relevant
    4. Suggests useful follow-up queries

    Format the response in an easy-to-read way.
    """
) 