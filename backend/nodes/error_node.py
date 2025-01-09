from models.state import State

def error_node(state: State) -> State:
    """
    Node for handling query generation errors and providing user feedback
    """
    print('---ROUTE: ERROR HANDLING---')
    
    error_message = """Sorry, I failed to retrieve the data.
Could you please rephrase your question?"""
    
    return {
        **state,
        "error_message": error_message,
        "status": "error"
    } 