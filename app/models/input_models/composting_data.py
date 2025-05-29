# models/input_models/composting_data.py

from pydantic import BaseModel, Field
from typing import Optional

class CompostingFuelConsumption(BaseModel):
    petrol: Optional[float] = Field(None, description="Petrol used in composting operations (L/day)")
    diesel: Optional[float] = Field(None, description="Diesel used in composting operations (L/day)")
    cng: Optional[float] = Field(None, description="CNG used in composting operations (L/day)")

class CompostingData(BaseModel):
    electricity_kwh_per_day: float = Field(..., description="Electricity used for composting operations (kWh/day)")
    fuel_consumption: Optional[CompostingFuelConsumption] = Field(None, description="Fuel used in composting operations")
    compost_production_kg_per_tonne: float = Field(..., description="Compost production in kg per tonne of waste")
    compost_usage_percent: float = Field(..., ge=0, le=100, description="Percentage of compost used for agri/gardening")
