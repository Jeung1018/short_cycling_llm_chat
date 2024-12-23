from typing import Dict
from pymongo import MongoClient
from config import MONGODB_URI
from models.state import State

# MongoDB setup
mongo_client = MongoClient(MONGODB_URI)
db = mongo_client["verdigris"]
collection = db["530_2024-10_monthly_report"]

def fetch_building_hierarchy(building_id: str) -> Dict:
    """Building의 hierarchy 정보만 가져오는 함수"""
    try:
        # 필요한 필드만 projection으로 지정
        projection = {
            "building_id": 1,
            "building_name": 1,
            "dates.panels.panel_id": 1,
            "dates.panels.panel_name": 1,
            "dates.panels.breakers.breaker_id": 1,
            "dates.panels.breakers.breaker_name": 1
        }
        
        query = {
            "building_id": building_id
        }
        
        doc = collection.find_one(query, projection)
        
        if not doc:
            return {"error": f"No hierarchy found for building {building_id}"}
            
        # hierarchy 구조
        hierarchy = {
            "building_id": doc["building_id"],
            "building_name": doc.get("building_name", ""),
            "total_panels": 0,
            "total_breakers": 0,
            "panels": []
        }
        
        # 첫 번째 날짜의 패널 정보만 사용
        if doc.get("dates") and len(doc["dates"]) > 0:
            for panel in doc["dates"][0].get("panels", []):
                breakers = [
                    {
                        "breaker_id": breaker["breaker_id"],
                        "breaker_name": breaker.get("breaker_name", "")
                    }
                    for breaker in panel.get("breakers", [])
                ]
                
                panel_info = {
                    "panel_id": panel["panel_id"],
                    "panel_name": panel.get("panel_name", ""),
                    "breaker_count": len(breakers),
                    "breakers": breakers
                }
                hierarchy["panels"].append(panel_info)
                
            # 전체 통계 계산
            hierarchy["total_panels"] = len(hierarchy["panels"])
            hierarchy["total_breakers"] = sum(panel["breaker_count"] for panel in hierarchy["panels"])
        
        return hierarchy
        
    except Exception as e:
        print(f"Error fetching hierarchy: {str(e)}")
        return {"error": str(e)}

def format_hierarchy_results(hierarchy: Dict) -> str:
    """Hierarchy 정보를 보기 좋게 포맷팅"""
    output = []
    
    output.append(f"\n=== {hierarchy['building_name']} (Building {hierarchy['building_id']}) Structure ===")
    output.append(f"\nTotal Panels: {hierarchy['total_panels']}")
    output.append(f"Total Breakers: {hierarchy['total_breakers']}")
    
    output.append("\nPanels and Breakers:")
    for panel in hierarchy["panels"]:
        output.append(f"\n📊 Panel {panel['panel_id']}: {panel['panel_name']}")
        output.append(f"   Total Breakers: {panel['breaker_count']}")
        for breaker in panel["breakers"]:
            output.append(f"   ⚡ Breaker {breaker['breaker_id']}: {breaker['breaker_name']}")
    
    return "\n".join(output)

def hierarchy_analysis_node(state: State) -> State:
    """Hierarchy 분석을 수행하는 노드"""
    print("\nDEBUG - Hierarchy Analysis Node:")
    try:
        building_id = state.get("building_id", "530")
        hierarchy = fetch_building_hierarchy(building_id)
        
        if "error" in hierarchy:
            return {
                **state,
                "building_hierarchy": {"error": hierarchy["error"]},
                "answer": f"Error analyzing hierarchy: {hierarchy['error']}"
            }
            
        formatted_result = format_hierarchy_results(hierarchy)
        
        return {
            **state,
            "building_hierarchy": hierarchy,  # hierarchy 데이터를 state에 저장
            "answer": formatted_result
        }
        
    except Exception as e:
        print(f"Hierarchy analysis error: {str(e)}")
        return {
            **state,
            "building_hierarchy": {"error": str(e)},
            "answer": f"Error during hierarchy analysis: {str(e)}"
        }