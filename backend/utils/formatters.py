from typing import Dict, List

def format_date_range(date_type: str, date_info: Dict) -> str:
    """날짜 범위를 포맷팅하는 함수"""
    if date_type == "single":
        return date_info.get("date", "")
    elif date_type == "range":
        start = date_info.get("start", "")
        end = date_info.get("end", "")
        return f"{start} to {end}"
    elif date_type == "month":
        return date_info.get("month", "")
    return ""

def format_breaker_data(breaker_data: Dict) -> str:
    """Breaker 데이터를 보기 좋게 포맷팅하는 함수"""
    output = []
    output.append(f"Breaker ID: {breaker_data.get('breaker_id', 'N/A')}")
    output.append(f"Total Cycles: {breaker_data.get('total_cycles', 'N/A')}")
    
    if 'short_cycles' in breaker_data:
        output.append(f"Short Cycles: {breaker_data['short_cycles']}")
    
    return "\n".join(output)

def format_panel_data(panel_data: Dict) -> str:
    """Panel 데이터를 보기 좋게 포맷팅하는 함수"""
    output = []
    output.append(f"\nPanel: {panel_data.get('panel_id', 'N/A')}")
    
    for breaker in panel_data.get('breakers', []):
        output.append("  " + format_breaker_data(breaker))
    
    return "\n".join(output)

def save_results(results: Dict, query: str) -> None:
    """결과를 파일로 저장하는 함수"""
    try:
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"results_{timestamp}.txt"
        
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"Query: {query}\n\n")
            f.write("Results:\n")
            f.write(str(results))
            
        print(f"\nResults saved to {filename}")
    except Exception as e:
        print(f"Error saving results: {str(e)}") 