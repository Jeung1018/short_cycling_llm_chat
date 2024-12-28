from typing import Dict
from models.state import State
from backend.utils.mongodb import fetch_data_from_mongodb
from config import DB_NAME, COLLECTION_NAME, DEFAULT_BUILDING_ID

def fetch_active_breakers_node(state: State) -> dict:
    """필터 조건에 따라 MongoDB에서 차단기 데이터를 가져오는 노드"""
    print('---ROUTE: FETCH ACTIVE BREAKERS---')
    
    print("\nCurrent State in fetch_active_breakers_node:")
    print(state)
    
    try:
        # breaker_filter_result 직접 사용
        filter_conditions = state["breaker_filter_result"]
        
        print("\nFilter Conditions from State:")
        print(filter_conditions)
        
        if "error" in filter_conditions:
            return {
                "active_breakers": {"error": filter_conditions["error"]},
                "error": filter_conditions["error"]
            }
            
        # MongoDB 쿼리 구성
        min_cycles = filter_conditions.get("total_cycles", {}).get("$gt", 0)
        query = {
            "building_id": filter_conditions.get("building_id"),
            "dates.panels.breakers.total_cycles": {"$gt": min_cycles}
        }
        
        # MongoDB 쿼리 출력
        print("\nMongoDB Query:")
        print(query)
        
        # MongoDB에서 데이터 가져오기
        docs = fetch_data_from_mongodb(query)
        
        # 결과 데이터 구성
        active_breakers = {
            "building_id": filter_conditions.get("building_id", DEFAULT_BUILDING_ID),
            "panels": []
        }
        
        for doc in docs:
            building_name = doc.get("building_name", "")
            active_breakers["building_name"] = building_name
            
            for date in doc.get("dates", []):
                for panel in date.get("panels", []):
                    panel_info = {
                        "panel_id": panel["panel_id"],
                        "panel_name": panel.get("panel_name", ""),
                        "breakers": []
                    }
                    
                    for breaker in panel.get("breakers", []):
                        total_cycles = breaker.get("total_cycles", 0)
                        if total_cycles > min_cycles:
                            panel_info["breakers"].append({
                                "breaker_id": breaker["breaker_id"],
                                "breaker_name": breaker.get("breaker_name", ""),
                                "total_cycles": total_cycles,
                                "total_short_cycles": breaker.get("total_short_cycles", 0)
                            })
                    
                    if panel_info["breakers"]:
                        active_breakers["panels"].append(panel_info)
        
        # active_breakers 출력
        print("\nActive Breakers Result:")
        print(active_breakers)
        
        # State에 결과 저장
        state["active_breakers"] = active_breakers
        return {
            "active_breakers": active_breakers,
            "error": None
        }
        
    except Exception as e:
        print(f"Fetch active breakers error: {str(e)}")
        state["active_breakers"] = {"error": str(e)}
        return {
            "active_breakers": {"error": str(e)},
            "error": str(e)
        }