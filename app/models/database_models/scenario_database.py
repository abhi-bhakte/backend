from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class ScenarioModel(BaseModel):
    scenario_name: str = Field(..., description="Name of the scenario for future reference")
    data: Dict[str, Any] = Field(..., description="All scenario data as a dict")
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
