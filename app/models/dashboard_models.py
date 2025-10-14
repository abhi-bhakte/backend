from pydantic import BaseModel
from typing import Optional, Dict

class CitySummaryResponse(BaseModel):
    city_name: str
    start_date: str
    end_date: str
    formally_collected_cumulative: float
    informally_collected_cumulative: float
    uncollected_cumulative: float
    waste_diverted_cumulative: float
    ghg_emissions_cumulative: float
    dry_percent_cumulative: Optional[float]
    wet_percent_cumulative: Optional[float]
    mixed_percent_cumulative: Optional[float]
    composition_cumulative: Optional[Dict[str, float]]
    material_recovery_cumulative: Optional[Dict[str, float]]
