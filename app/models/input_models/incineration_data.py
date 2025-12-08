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


# Output model for incineration results
class IncinerationResponse(BaseModel):
    """
    Pydantic model for incineration emissions response.
    Includes both per-tonne (kgCO2e/ton waste incinerated) and total (kgCO2e) outputs.

    Per-tonne outputs (per ton waste incinerated):
        ch4_emissions: CH4 emissions (kgCO2e/ton)
        ch4_emissions_avoid: CH4 emissions avoided (kgCO2e/ton)
        co2_emissions: CO2 emissions (kgCO2e/ton)
        co2_emissions_avoid: CO2 emissions avoided (kgCO2e/ton)
        n2o_emissions: N2O emissions (kgCO2e/ton)
        n2o_emissions_avoid: N2O emissions avoided (kgCO2e/ton)
        bc_emissions: Black Carbon mass (kg/ton)
        bc_emissions_avoid: Black Carbon mass avoided (kg/ton)
        total_emissions: Total CO2eq (CH4+CO2+N2O) (kgCO2e/ton)
        total_emissions_avoid: Total CO2eq avoided (kgCO2e/ton)
        net_emissions: Net CO2eq (kgCO2e/ton)
        net_emissions_bc: Net BC mass (kg/ton)

    Total outputs (for all waste incinerated, in kgCO2e or kg):
        ch4_emissions_total: CH4 emissions (kgCO2e)
        ch4_emissions_avoid_total: CH4 emissions avoided (kgCO2e)
        co2_emissions_total: CO2 emissions (kgCO2e)
        co2_emissions_avoid_total: CO2 emissions avoided (kgCO2e)
        n2o_emissions_total: N2O emissions (kgCO2e)
        n2o_emissions_avoid_total: N2O emissions avoided (kgCO2e)
        bc_emissions_total: Black Carbon mass (kg)
        bc_emissions_avoid_total: Black Carbon mass avoided (kg)
        total_emissions_total: Total CO2eq (CH4+CO2+N2O) (kgCO2e)
        total_emissions_avoid_total: Total CO2eq avoided (kgCO2e)
        net_emissions_total: Net CO2eq (kgCO2e)
        net_emissions_bc_total: Net BC mass (kg)
    """

    ch4_emissions: float
    ch4_emissions_avoid: float
    co2_emissions: float
    co2_emissions_avoid: float
    n2o_emissions: float
    n2o_emissions_avoid: float
    bc_emissions: float
    bc_emissions_avoid: float
    total_emissions: float
    total_emissions_avoid: float
    net_emissions: float
    net_emissions_bc: float

    ch4_emissions_total: float
    ch4_emissions_avoid_total: float
    co2_emissions_total: float
    co2_emissions_avoid_total: float
    n2o_emissions_total: float
    n2o_emissions_avoid_total: float
    bc_emissions_total: float
    bc_emissions_avoid_total: float
    total_emissions_total: float
    total_emissions_avoid_total: float
    net_emissions_total: float
    net_emissions_bc_total: float

