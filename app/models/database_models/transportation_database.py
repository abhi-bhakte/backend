# /backend/app/models/transportation.py
from pydantic import BaseModel
from typing import Optional

class TransportationInput(BaseModel):
    vehicle_id: str
    fuel_type: str
    distance_km: float
    fuel_efficiency: Optional[float]

class TransportationOutput(BaseModel):
    emissions_kg_co2e: float
