from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

# Import your  model
from .transportation_data import TransportationData
from .composting_data import CompostingData
from .anaerobic_digestion_data import AnaerobicDigestionData
from .recycling_data import RecyclingData
from .incineration_data import IncinerationData
from .landfill_data import LandfillData

class WasteComposition(BaseModel):
    food: float = Field(..., description="Percentage of food waste")
    garden: float = Field(..., description="Percentage of garden waste")
    plastic: float = Field(..., description="Percentage of plastic waste")
    paper: float = Field(..., description="Percentage of paper waste")
    textile: float = Field(..., description="Percentage of textile waste")
    leather_rubber: float = Field(..., description="Percentage of leather and rubber waste")
    glass: float = Field(..., description="Percentage of glass waste")
    metal: float = Field(..., description="Percentage of metal waste (aluminum + steel)")
    nappies: float = Field(..., description="Percentage of nappies/diapers")
    wood: float = Field(..., description="Percentage of wood waste")
    hazardous: float = Field(..., description="Percentage of hazardous waste")
    others: float = Field(..., description="Percentage of other waste types")

class WasteAllocation(BaseModel):
    composting: float = Field(..., description="Waste allocated for composting (tonnes/day)")
    anaerobic_digestion: float = Field(..., description="Waste allocated for anaerobic digestion (tonnes/day)")
    recycling: float = Field(..., description="Waste allocated for recycling (tonnes/day)")
    incineration: float = Field(..., description="Waste allocated for incineration (tonnes/day)")
    landfilling: float = Field(..., description="Waste allocated for landfilling (tonnes/day)")


# New nested general block
class GeneralBlock(BaseModel):
    city_name: str = Field(..., description="City name")
    date: str = Field(..., description="Date of waste data entry (YYYY-MM-DD)")
    total_waste_generation: float = Field(..., description="Total waste generation (tonnes/day)")
    formally_collected: float = Field(..., description="Formally collected waste (tonnes/day)")
    informally_collected: float = Field(..., description="Informally collected waste (tonnes/day)")
    uncollected: Optional[float] = Field(None, description="Uncollected waste (auto-calculated if not provided)")
    dry_waste_percentage: Optional[float] = Field(None, description="Dry waste percentage")
    mixed_waste_percentage: Optional[float] = Field(None, description="Mixed waste percentage")
    wet_waste_percentage: Optional[float] = Field(None, description="Wet waste percentage")
    selected_treatment_methods: List[str] = Field(
        ..., 
        description="List of selected waste treatment methods. Options: composting, anaerobic_digestion, recycling, incineration, landfilling"
    )
    waste_allocation: WasteAllocation = Field(..., description="Waste allocation for each category (tonnes/day)")
    waste_composition: WasteComposition = Field(..., description="Waste composition as percentage by weight")

class WasteData(BaseModel):
    submission_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique submission ID")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Submission timestamp")
    user_id: Optional[str] = Field(None, description="User ID (set from logged-in user)")
    scenario_name: str = Field(..., description="Scenario name or tag (e.g., Summer2024 Plan)")
    general: GeneralBlock = Field(..., description="General city and waste data block")
    transportation: Optional[TransportationData] = Field(None, description="Transportation data block")
    composting: Optional[CompostingData] = Field(None, description="Composting data block")
    anaerobic_digestion: Optional[AnaerobicDigestionData] = Field(None, description="Anaerobic Digestion data block")
    recycling: Optional[RecyclingData] = Field(None, description="Recycling data block")
    incineration: Optional[IncinerationData] = Field(None, description="Incineration data block")
    landfill: Optional[LandfillData] = Field(None, description="Landfill data block")
    transportation_emissions: Optional[Dict[str, Any]] = Field(
        None, description="Results of transportation emissions calculation"
    )
    composting_emissions: Optional[Dict[str, Any]] = Field(
        None, description="Results of composting emissions calculation"
    )
    anaerobic_digestion_emissions: Optional[Dict[str, Any]] = Field(
        None, description="Results of anaerobic digestion emissions calculation"
    )
    recycling_emissions: Optional[Dict[str, Any]] = Field(
        None, description="Results of recycling emissions calculation"
    )
    incineration_emissions: Optional[Dict[str, Any]] = Field(
        None, description="Results of incineration emissions calculation"
    )
    landfill_emissions: Optional[Dict[str, Any]] = Field(
        None, description="Results of landfill emissions calculation"
    )
