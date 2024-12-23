from typing import Dict, List
from langchain_openai import ChatOpenAI

from config import OPENAI_API_KEY, LLM_MODEL, LLM_TEMPERATURE
from ..utils.data_fetchers import fetch_building_hierarchy, fetch_active_breakers

class AnalysisChain:
    """데이터 분석을 수행하는 체인"""
    def __init__(self):
        self.llm = ChatOpenAI(
            model=LLM_MODEL,
            temperature=LLM_TEMPERATURE,
            openai_api_key=OPENAI_API_KEY
        )

    def analyze(self, query: str, validation_result: Dict, data: List[Dict], breaker_filter_result: Dict) -> Dict:
        try:
            print("\nDEBUG - Analysis Chain:")
            print("Validation result:", validation_result)
            print("Breaker filter result:", breaker_filter_result)
            
            # 필터 타입에 따라 다른 처리
            if breaker_filter_result.get("show_active_only"):
                print("Processing active breakers query...")
                active_breakers = fetch_active_breakers(data)
                formatted_result = self.format_hierarchy_results(active_breakers)
                return {
                    "result_type": "active_breakers",
                    "data": active_breakers,
                    "formatted_output": formatted_result
                }
            
            # 전체 hierarchy 처리
            print("Processing full hierarchy query...")
            building_id = "530"
            hierarchy = fetch_building_hierarchy(building_id)
            
            if "error" in hierarchy:
                return hierarchy
            
            formatted_result = self.format_hierarchy_results(hierarchy)
            return {
                "result_type": "hierarchy",
                "data": hierarchy,
                "formatted_output": formatted_result
            }
            
        except Exception as e:
            print(f"Analysis error: {str(e)}")
            return {"error": str(e)}

    @staticmethod
    def format_hierarchy_results(data: Dict) -> str:
        """계층 구조 결과 포맷팅"""
        output = []
        output.append(f"\nBuilding {data.get('building_id', '530')} Structure:")
        
        for panel in data.get("panels", []):
            output.append(f"\nPanel: {panel.get('panel_id', '')}")
            for breaker in panel.get("breakers", []):
                cycles = breaker.get("total_cycles", "N/A")
                output.append(f"  Breaker {breaker.get('breaker_id', '')}: {cycles} cycles")
        
        return "\n".join(output) 