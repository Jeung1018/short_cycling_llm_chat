from typing import Dict
from models.state import State
from backend.utils.mongodb import fetch_data_from_mongodb

def analyze_building_level(data: Dict) -> Dict:
    """빌딩 레벨 분석"""
    try:
        # MongoDB에서 building 데이터 가져오기
        building_id = data.get("building_id", "530")
        query = {"building_id": building_id}
        
        print("\nMongoDB Query for Building Info:")
        print(query)
        
        # MongoDB에서 building 문서 가져오기
        building_doc = fetch_data_from_mongodb(query)
        
        if not building_doc:
            raise Exception(f"Building {building_id} not found")
            
        # 첫 번째 문서 사용
        building = building_doc[0]
        
        # 날짜별 정보와 해당 날짜의 패널 정보를 함께 추출
        dates_info = []
        for date in building.get("dates", []):
            # total_cycles가 0이 아닌 패널만 필터링
            active_panels = [{
                "panel_id": panel.get("panel_id"),
                "panel_name": panel.get("panel_name"),
                "total_cycles": panel.get("total_cycles", 0),
                "total_short_cycles": panel.get("total_short_cycles", 0)
            } for panel in date.get("panels", [])
            if panel.get("total_cycles", 0) > 0]

            dates_info.append({
                "date": date.get("date"),
                "total_cycles": date.get("total_cycles", 0),
                "total_short_cycles": date.get("total_short_cycles", 0),
                "panels": active_panels
            })
        
        # building_info 구성
        building_info = {
            "building_id": building.get("building_id"),
            "building_name": building.get("building_name"),
            "building_total_cycles": building.get("total_cycles"),
            "building_total_short_cycles": building.get("total_short_cycles"),
            "month": building.get("month"),
            "dates": dates_info  # 각 날짜별 정보와 패널 정보 포함
        }
        
        print("\nBuilding Info Retrieved:")
        print(building_info)
        
        return {
            "analysis_results": {
                "building_id": building_id,
                "analysis_type": "building_level",
                "findings": f"Building analysis for {building_info['building_name']} completed",
                "details": {
                    "total_panels": len(dates_info),
                    "total_dates": len(dates_info),
                    "latest_date": dates_info[-1] if dates_info else None,
                    "panel_count": len(dates_info)
                }
            },
            "building_info": building_info
        }
        
    except Exception as e:
        print(f"Error in analyze_building_level: {str(e)}")
        return {
            "analysis_results": {"error": str(e)},
            "building_info": {"error": str(e)}
        }

def building_analysis_node(state: State) -> State:
    """Building 분석을 수행하는 노드"""
    print("\nDEBUG - Building Analysis Node:")
    try:
        result = analyze_building_level(state)
        formatted_answer = f"Building {result['building_info']['building_name']} data retrieved"
        
        return {
            **state,
            "building_info": result["building_info"],  # building_info만 state에 저장
            "answer": formatted_answer
        }
    except Exception as e:
        print(f"Building analysis error: {str(e)}")
        return {
            **state,
            "building_info": {"error": str(e)},
            "answer": f"Error during building analysis: {str(e)}"
        }