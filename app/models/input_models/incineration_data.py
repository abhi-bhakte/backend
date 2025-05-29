# models/input_models/incineration_data.py

from pydantic import BaseModel, Field
from typing import Optional


class IncineratorInfo(BaseModel):
    calorific_value_mj_per_kg: Optional[float] = Field(None, description="Calorific value (LHV) of waste in MJ/kg")
    incineration_technology: Optional[str] = Field(None, description="Type of incineration technology")


class IncinerationEnergyUse(BaseModel):
    electricity_kwh_per_day: Optional[float] = Field(None, description="Electricity used for incineration operations (kWh/day)")
    petrol_l_per_day: Optional[float] = Field(None, description="Petrol used (L/day)")
    diesel_l_per_day: Optional[float] = Field(None, description="Diesel used (L/day)")
    cng_l_per_day: Optional[float] = Field(None, description="CNG used (L/day)")


class EnergyRecoveryData(BaseModel):
    energy_recovery_type: Optional[str] = Field(None, description="Type of energy recovered")
    electricity_recovery_efficiency: Optional[float] = Field(None, ge=0, le=100, description="Efficiency of electricity recovery (%)")
    electricity_used_onsite_percent: Optional[float] = Field(None, ge=0, le=100, description="Percentage of electricity used onsite (%)")
    heat_recovery_efficiency: Optional[float] = Field(None, ge=0, le=100, description="Efficiency of heat recovery (%)")
    recovered_heat_usage_percent: Optional[float] = Field(None, ge=0, le=100, description="Percentage of recovered heat used (%)")
    fossil_fuel_replaced: Optional[str] = Field(None, description="Fossil fuel replaced by recovered heat")


class IncinerationData(BaseModel):
    incinerator_info: Optional[IncineratorInfo] = Field(None, description="Basic incinerator and waste details")
    energy_consumption: Optional[IncinerationEnergyUse] = Field(None, description="Energy used for incineration")
    energy_recovery: Optional[EnergyRecoveryData] = Field(None, description="Recovered energy details from incineration")
