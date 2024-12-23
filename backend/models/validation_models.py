from typing import Dict
from pydantic import BaseModel, Field
from typing import Literal

class ValidationResult(BaseModel):
    """쿼리 검증 결과를 위한 모델"""
    is_building_530: bool = Field(description="Whether query references Building 530")
    is_october_2024: bool = Field(description="Whether query is within October 2024") 
    is_short_cycling: bool = Field(description="Whether query relates to short cycling")
    query_type: str = Field(description="Type of query (building/panel/breaker/date/hierarchy)")

class QueryInfo(BaseModel):
    """쿼리 정보를 구조화하는 모델"""
    building_id: str = Field(description="Building identifier")
    date_type: str = Field(description="Type of date query")
    date_info: Dict = Field(description="Date-related information")
    component_type: str = Field(description="Component type (panel/breaker)")
    component_id: str = Field(description="Component identifier")

class BreakerFilterType(BaseModel):
    """Breaker 필터링 타입을 정의하는 모델"""
    show_active_only: bool = Field(description="Whether to show only active breakers")
    hierarchy_level: str = Field(description="Level of hierarchy detail (all/active)")

class QueryIntent(BaseModel):
    """쿼리 의도를 분석하는 모델"""
    query_type: Literal["building", "breaker", "hierarchy"] = Field(
        description="Type of query (building/breaker/hierarchy)",
        json_schema_extra={"enum": ["building", "breaker", "hierarchy"]}
    )
    is_active_only: bool = Field(
        description="Whether query asks for active breakers only"
    )
    detail_level: Literal["summary", "detailed"] = Field(
        description="Level of detail requested",
        json_schema_extra={"enum": ["summary", "detailed"]}
    ) 