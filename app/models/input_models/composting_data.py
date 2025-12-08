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


# Output model for composting results 
class CompostingResponse(BaseModel):
    """
    Pydantic model for composting emissions response.
    Includes both per-tonne (kgCO2e/ton waste composted) and total (kgCO2e) outputs.

    Per-tonne outputs (per ton waste composted):
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

    Total outputs (for all waste composted, in kgCO2e or kg):
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
