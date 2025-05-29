# models/input_models/landfill_data.py

from pydantic import BaseModel, Field
from typing import Optional


class LandfillEnergyUse(BaseModel):
    electricity_kwh_per_day: Optional[float] = Field(None, description="Electricity used for landfill operations (kWh/day)")
    petrol_l_per_day: Optional[float] = Field(None, description="Petrol used (L/day)")
    diesel_l_per_day: Optional[float] = Field(None, description="Diesel used (L/day)")
    cng_l_per_day: Optional[float] = Field(None, description="CNG used (L/day)")


class LandfillOperationInfo(BaseModel):
    landfill_type: Optional[str] = Field(None, description="Type of landfill or open dump practice")
    open_burning_percent: Optional[float] = Field(None, ge=0, le=100, description="Percentage of disposed waste that is open-burned")
    disposal_growth_percent: Optional[float] = Field(None, ge=0, le=100, description="Estimated annual disposal growth")
    start_year: Optional[int] = Field(None, description="Starting year of waste disposal")
    end_year: Optional[int] = Field(None, description="End year of waste disposal")
    current_year: Optional[int] = Field(None, description="Current year of disposal")


class LandfillGasRecovery(BaseModel):
    gas_collection_efficiency_percent: Optional[float] = Field(None, ge=0, le=100, description="Efficiency of landfill gas (LFG) collection (%)")
    treatment_method: Optional[str] = Field(None, description="Treatment method for LFG (e.g., LPG used in boiler to produce heating)")
    utilization_efficiency_percent: Optional[float] = Field(None, ge=0, le=100, description="LFG utilization efficiency (%)")
    fossil_fuel_replaced: Optional[str] = Field(None, description="Type of fossil fuel replaced by the recovered LFG")
    gas_recovery_start_year: Optional[int] = Field(None, description="Starting year of LFG recovery")
    gas_recovery_end_year: Optional[int] = Field(None, description="End year of LFG recovery")



class LandfillData(BaseModel):
    energy_consumption: Optional[LandfillEnergyUse] = Field(None, description="Energy usage in landfill operations")
    operation_details: Optional[LandfillOperationInfo] = Field(None, description="Details about landfill operation and disposal trends")
    gas_recovery: Optional[LandfillGasRecovery] = Field(None, description="Landfill gas recovery details")
