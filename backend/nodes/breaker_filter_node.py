from typing import Dict
from models.state import State

def breaker_filter_node(state: State) -> dict:
    """차단기 필터링 조건을 설정하는 노드"""
    print('---ROUTE: BREAKER FILTER---')
    
    try:
        # MongoDB 쿼리를 위한 필터 설정
        filter_conditions = {
            "building_id": state.get("building_id", "530"),
            "total_cycles": {"$gt": 0}  # 기본적으로 total_cycles > 0 조건
        }
        
        # 쿼리 분석에 따른 추가 필터 조건 설정
        query = state.get("query", "").lower()
        if "high usage" in query:
            filter_conditions["total_cycles"] = {"$gt": 100}
        
        print("\nFilter Conditions:")
        print(filter_conditions)
        
        # breaker_filter_result로 키 이름 변경
        return {
            "breaker_filter_result": filter_conditions,
            "building_id": state.get("building_id", "530")
        }
        
    except Exception as e:
        print(f"Breaker filter error: {str(e)}")
        return {
            "breaker_filter_result": {"error": str(e)},
            "error": str(e)
        }