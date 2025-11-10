# models/input_models/recycling_data.py

from pydantic import BaseModel, Field
from typing import Optional



# New RecyclingData model matching the API payload (RecyclingRequest)
from typing import Dict

class RecyclingData(BaseModel):
    recycle_collected_formal: float = Field(..., gt=0, description="Total recyclable collected by the formal sector (tons)")
    recycle_collected_informal: float = Field(..., ge=0, description="Total recyclable collected by the informal sector (tons)")
    material_composition_formal: Dict[str, float] = Field(..., description="Composition (%) of materials collected by the formal sector")
    material_composition_informal: Dict[str, float] = Field(..., description="Composition (%) of materials collected by the informal sector")
    electricity_consumed: Dict[str, float] = Field(..., description="Electricity consumed during recycling for each material (kWh)")
    fuel_consumption: Dict[str, Dict[str, float]] = Field(..., description="Fuel consumption for each material and fuel type (liters)")
    recyclability: Dict[str, float] = Field(..., description="Recyclability of materials (percentage)")
