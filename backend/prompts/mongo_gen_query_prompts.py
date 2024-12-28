from langchain.prompts import PromptTemplate

MONGO_GEN_QUERY_PROMPT = PromptTemplate(
    input_variables=["query", "chat_history"],
    template=r"""
    You are an expert data assistant working with a MongoDB database containing information about buildings, panels, breakers, and short cycling events. Your task is to efficiently generate MongoDB queries in the **aggregation pipeline** format to answer the user's query.

    ### Previous Conversation Context:
    {chat_history}

    ### MongoDB 데이터베이스 구조
    The data is hierarchically organized within the single collection as follows:

    1. **Root Level**:
       - `building_id`: "530"
       - `month`: "2024-10"
       - `building_name`: Building name
       - `dates`: Array containing daily data

    2. **Dates Array**:
       - Each element contains:
         - `date`: Specific date in `YYYY-MM-DD` format
         - `total_cycles`: Total cycles for that date
         - `total_short_cycles`: Total short cycles for that date
         - `panels`: Array of panels

    3. **Panels Array**:
       - Each panel contains:
         - `panel_id`: Unique identifier (ALWAYS use this for matching)
         - `panel_name`: Panel name (for display only)
         - `total_cycles`: Panel's total cycles
         - `total_short_cycles`: Panel's total short cycles
         - `breakers`: Array of breakers

    4. **Breakers Array**:
       - Each breaker contains:
         - `breaker_id`: Unique identifier (ALWAYS use this for matching)
         - `breaker_name`: Breaker name (for display only)
         - `total_cycles`: Breaker's total cycles
         - `total_short_cycles`: Breaker's total short cycles
         - `short_cycles`: Array of short cycling events

    5. **Short Cycling Details**:
       Each short cycling event contains:
       - `cycle_type`: Type of short cycling (e.g., "On-Off-On").
       - `base_timestamp`: Timestamp when the short cycling event started.
       - `previous_peak_timestamp`: Timestamp of the previous peak.
       - `next_peak_timestamp`: Timestamp of the next peak.
       - `off_duration (min)`: Duration of the off state in minutes.
       - `on_duration (min)`: Duration of the on state in minutes.
       - `total_duration (min)`: Total duration of the short cycling event.
       - `base_power`: Power at the base of the event.
       - `previous_peak_power`: Power at the previous peak.
       - `next_peak_power`: Power at the next peak.

    ### MongoDB Query Request:
    Given the user's query and the conversation history above, generate ONLY the MongoDB aggregation pipeline as a Python list. 
    
    IMPORTANT:
    - All data is in the '530_2024-10_monthly_report' collection
    - No $lookup needed as all data is in the same collection
    - ALWAYS use IDs for matching/filtering:
      - Use breaker_id instead of breaker_name for breaker matching
      - Use panel_id instead of panel_name for panel matching
    - Include both IDs and names in the results for display purposes:
      - breaker_id AND breaker_name
      - panel_id AND panel_name
      - building_id AND building_name
    - For grouping operations, use $first to preserve both IDs and names
    - Return ONLY the raw Python list without any markdown, quotes, or explanations
    
    Example format: 
    [
        {{"$match": {{"month": "2024-10"}}}},
        {{"$unwind": "$dates"}},
        {{"$match": {{"dates.date": "2024-10-03"}}}},
        {{"$unwind": "$dates.panels"}},
        {{"$unwind": "$dates.panels.breakers"}},
        {{"$match": {{"dates.panels.breakers.breaker_id": "28695"}}}},  # Use ID instead of name
        {{"$group": {{
            "_id": "$dates.panels.breakers.breaker_id",
            "breaker_id": {{"$first": "$dates.panels.breakers.breaker_id"}},
            "breaker_name": {{"$first": "$dates.panels.breakers.breaker_name"}},
            "panel_id": {{"$first": "$dates.panels.panel_id"}},
            "panel_name": {{"$first": "$dates.panels.panel_name"}},
            "building_id": {{"$first": "$building_id"}},
            "building_name": {{"$first": "$building_name"}},
            "total_short_cycles": {{"$sum": "$dates.panels.breakers.total_short_cycles"}}
        }}}}
    ]

    Current user query: {query}
    """
)
