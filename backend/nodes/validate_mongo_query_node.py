from models.state import State
from prompts.validate_mongo_query_prompts import VALIDATE_MONGO_QUERY_PROMPT
from bson import json_util
import json

def validate_mongo_query_node(state: State) -> State:
    """
    Node for validating MongoDB query format
    If inappropriate format or syntax is found, forwards to regenerate_mongo_query_node
    """
    print('---ROUTE: VALIDATE MONGO QUERY FORMAT---')

    # Execute LLM chain
    chain = VALIDATE_MONGO_QUERY_PROMPT | state["llm"]
    query_str = json_util.dumps(state["mongo_query"], indent=2)
    
    response = chain.invoke({
        "mongo_query": query_str,
        "invalid_query_reason": state.get("invalid_query_reason", "")
    })

    try:
        # Parse validation result
        validation_result = json.loads(response.content.strip())
        print("Parsed validation result:", validation_result)  # 파싱된 결과 출력

        # validation 결과를 개별적으로 state에 저장
        state["mongo_query_validation"] = validation_result.get("mongo_query_validation", False)
        state["invalid_query_reason"] = validation_result.get("invalid_query_reason", "")
        
        # 결과 로깅
        if state["mongo_query_validation"]:
            print("Query validation successful")
        else:
            print(f"Query validation failed. Reason: {state['invalid_query_reason']}")
        
        return state

    except Exception as e:
        error_message = f"Query format validation failed: {str(e)}"
        print(error_message)
        raise ValueError(error_message)


def validate_mongo_query_rf(state: State) -> str:
    """
    Routing function after validate_mongo_query_node
    """
    print('---MONGO QUERY VALIDATION ROUTING---')

    validation_result = state.get("mongo_query_validation", False)
    if validation_result:
        print("Query format validation successful")
        return "valid_mongo_query"
    
    print(f"Query format validation failed: {state.get('invalid_query_reason', 'Unknown reason')}")
    return "regen_mongo_query"