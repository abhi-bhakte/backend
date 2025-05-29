# models/input_models/recycling_data.py

from pydantic import BaseModel, Field
from typing import Optional


class MaterialCollectionData(BaseModel):
    paper_cardboard: Optional[float] = Field(None, ge=0, le=100, description="Percentage of paper & cardboard collected")
    plastic: Optional[float] = Field(None, ge=0, le=100, description="Percentage of plastic collected")
    aluminum: Optional[float] = Field(None, ge=0, le=100, description="Percentage of aluminum collected")
    metal_steel: Optional[float] = Field(None, ge=0, le=100, description="Percentage of metal/steel collected")
    glass: Optional[float] = Field(None, ge=0, le=100, description="Percentage of glass collected")


class MaterialEnergyData(BaseModel):
    electricity_kwh_per_tonne: Optional[float] = Field(None, description="Electricity used for recycling (kWh/tonne)")
    petrol_l_per_day: Optional[float] = Field(None, description="Petrol used (L/day)")
    diesel_l_per_day: Optional[float] = Field(None, description="Diesel used (L/day)")
    cng_l_per_day: Optional[float] = Field(None, description="CNG used (L/day)")
    recyclability_percent: Optional[float] = Field(None, ge=0, le=100, description="Recyclability (%)")


class RecyclingEnergyConsumption(BaseModel):
    paper_cardboard: Optional[MaterialEnergyData]
    plastic: Optional[MaterialEnergyData]
    aluminum: Optional[MaterialEnergyData]
    metal_steel: Optional[MaterialEnergyData]
    glass: Optional[MaterialEnergyData]


class RecyclingData(BaseModel):
    formal_sector: Optional[MaterialCollectionData] = Field(None, description="Recyclables collected by the formal sector")
    informal_sector: Optional[MaterialCollectionData] = Field(None, description="Recyclables collected by the informal sector")
    energy_consumption: Optional[RecyclingEnergyConsumption] = Field(None, description="Energy use and recyclability for each material")
