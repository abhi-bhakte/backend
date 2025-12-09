from pydantic import BaseModel
from typing import Optional, Dict, List

class DailyStat(BaseModel):
    date: str
    collected: float
    emissions: float


class SankeyTransfer(BaseModel):
    source: str
    target: str
    value: float

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
    daily_stats: Optional[List[DailyStat]]
    compostingGWP: Optional[float]
    anaerobicDigestionGWP: Optional[float]
    recyclingGWP: Optional[float]
    landfillGWP: Optional[float]
    incinerationGWP: Optional[float]
    pyrolysisGWP: Optional[float]
    transfers: Optional[List[SankeyTransfer]]
