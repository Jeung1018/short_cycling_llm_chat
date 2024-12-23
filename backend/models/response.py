from typing import List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

class BreakerResponse(BaseModel):
    """Structured breaker analysis response"""
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "building_id": "530",
                    "active_breakers": [
                        {
                            "breaker_id": "B1",
                            "panel_id": "P1",
                            "total_cycles": 150
                        }
                    ],
                    "total_count": 1
                }
            ]
        }
    )

    building_id: str = Field(description="Building identifier")
    active_breakers: List[Dict[str, Any]] = Field(
        description="List of active breakers with their details",
        default_factory=list
    )
    total_count: int = Field(description="Total number of active breakers")

class BuildingResponse(BaseModel):
    """Structured building analysis response"""
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "building_id": "530",
                    "status": "operational",
                    "total_panels": 5,
                    "total_breakers": 20
                }
            ]
        }
    )

    building_id: str = Field(description="Building identifier")
    status: str = Field(description="Overall building status")
    total_panels: int = Field(description="Total number of panels")
    total_breakers: int = Field(description="Total number of breakers") 