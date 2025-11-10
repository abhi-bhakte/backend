# models/input_models/incineration_data.py

from pydantic import BaseModel, Field
from typing import Optional
from typing import Dict, List


# Section for fuel consumption
class FuelConsumption(BaseModel):
    petrol: Optional[float] = Field(None, description="Petrol used (L/day)")
    diesel: Optional[float] = Field(None, description="Diesel used (L/day)")
    cng: Optional[float] = Field(None, description="CNG used (L/day)")


# Section for mixed waste composition
class MixedWasteComposition(BaseModel):
    food: float = Field(..., description="Food waste (%)")
    garden: float = Field(..., description="Garden waste (%)")
    plastics: float = Field(..., description="Plastics (%)")
    paper: float = Field(..., description="Paper (%)")
    textile: float = Field(..., description="Textile (%)")
    rubber: float = Field(..., description="Leather/rubber (%)")
    glass: float = Field(..., description="Glass (%)")
    metal: float = Field(..., description="Metal (aluminium + steel) (%)")
    nappies_diapers: float = Field(..., description="Nappies (disposable diapers) (%)")
    wood: float = Field(..., description="Wood (%)")
    others: float = Field(..., description="Others (%)")

# Section for incinerator info
class IncineratorInfo(BaseModel):
    calorific_value_mj_per_kg: Optional[float] = Field(None, description="Calorific value (LHV) of waste in MJ/kg")
    incineration_type: Optional[str] = Field(None, description="Type of incineration technology")
    mixed_waste_composition: 'MixedWasteComposition' = Field(..., description="Percentage composition of each waste type in the incinerated waste")

# Section for energy recovery
class EnergyRecovery(BaseModel):
    energy_recovery_type: Optional[str] = Field(None, description="Type of energy recovered (e.g., heat, electricity, both)")
    electricity_recovery_efficiency: Optional[float] = Field(None, ge=0, le=100, description="Efficiency of electricity recovery (%)")
    electricity_used_onsite_percent: Optional[float] = Field(None, ge=0, le=100, description="Percentage of electricity used onsite (%)")
    heat_recovery_efficiency: Optional[float] = Field(None, ge=0, le=100, description="Efficiency of heat recovery (%)")
    recovered_heat_usage_percent: Optional[float] = Field(None, ge=0, le=100, description="Percentage of recovered heat used (%)")
    fossil_fuel_replaced: Optional[list] = Field(None, description="List of fossil fuel types replaced by recovered heat")





class IncinerationData(BaseModel):
    waste_incinerated: float = Field(..., gt=0, description="Amount of waste incinerated (tons/day)")
    electricity_kwh_per_day: float = Field(..., ge=0, description="Electricity used for incineration (kWh/day)")
    fuel_consumption: FuelConsumption = Field(..., description="Fossil fuel consumption (L or kg per day)")
    incinerator_info: IncineratorInfo = Field(..., description="Incinerator technology and waste info")
    energy_recovery: EnergyRecovery = Field(..., description="Energy recovery details from incineration")

