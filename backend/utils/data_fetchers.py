from typing import Dict, List

def fetch_building_hierarchy() -> Dict:
    """
    Fetches the building hierarchy data from the database
    Returns:
        Dict: A dictionary containing the building hierarchy
    """
    # TODO: Implement actual database fetching
    # This is a mock implementation
    return {
        "buildings": [
            {
                "name": "Building A",
                "floors": ["Floor 1", "Floor 2"],
                "rooms": ["Room 101", "Room 102"]
            }
        ]
    }

def fetch_active_breakers() -> List[Dict]:
    """
    Fetches the active breakers data from the database
    Returns:
        List[Dict]: A list of active breakers with their details
    """
    # TODO: Implement actual database fetching
    # This is a mock implementation
    return [
        {
            "id": "breaker_1",
            "location": "Building A - Floor 1",
            "status": "active"
        }
    ] 