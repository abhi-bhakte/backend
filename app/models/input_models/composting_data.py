from pydantic import BaseModel, Field
from typing import Optional


class FuelConsumption(BaseModel):
    petrol: Optional[float] = Field(None, description="Petrol used in operations (L/day)")
    diesel: Optional[float] = Field(None, description="Diesel used in operations (L/day)")
    cng: Optional[float] = Field(None, description="CNG used in operations (L/day)")


class CompostingData(BaseModel):
    """Compact composting input aligned with frontend payload."""

    waste_composted: float = Field(..., gt=0, description="Total waste composted (tons)")
    compost_production_kg_per_tonne: float = Field(..., ge=0, description="Compost production potential (kg per ton waste)")
    compost_usage_percent: float = Field(..., ge=0, le=100, description="Percent of compost used in agri/gardens")

    electricity_kwh_per_day: float = Field(..., ge=0, description="Electricity consumed (kWh/day)")
    fuel_consumption: Optional[FuelConsumption] = Field(None, description="Operational fuel consumption (L/day)")
