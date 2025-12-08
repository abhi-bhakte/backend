# models/input_models/landfill_data.py

from pydantic import BaseModel, Field
from typing import Optional


class FuelConsumption(BaseModel):
    petrol_l_per_day: Optional[float] = Field(None, description="Petrol used (L/day)")
    diesel_l_per_day: Optional[float] = Field(None, description="Diesel used (L/day)")
    cng_l_per_day: Optional[float] = Field(None, description="CNG used (L/day)")


class LandfillOperationInfo(BaseModel):
    landfill_type: Optional[str] = Field(None, description="Type of landfill or open dump practice")
    waste_disposed_fired: Optional[float] = Field(None, ge=0, le=100, description="Percentage of disposed waste that is open-burned")
    annual_growth_rate: Optional[float] = Field(None, ge=0, le=100, description="Estimated annual disposal growth")
    start_year: Optional[int] = Field(None, description="Starting year of waste disposal")
    end_year: Optional[int] = Field(None, description="End year of waste disposal")
    current_year: Optional[int] = Field(None, description="Current year of disposal")


class LandfillGasRecovery(BaseModel):
    gas_collection_efficiency: Optional[float] = Field(None, ge=0, le=100, description="Efficiency of landfill gas (LFG) collection (%)")
    gas_treatment_method: Optional[str] = Field(None, description="Treatment method for LFG (e.g., LPG used in boiler to produce heating)")
    lfg_utilization_efficiency: Optional[float] = Field(None, ge=0, le=100, description="LFG utilization efficiency (%)")
    fossil_fuel_replaced: Optional[str] = Field(None, description="Type of fossil fuel replaced by the recovered LFG")
    gas_recovery_start_year: Optional[int] = Field(None, description="Starting year of LFG recovery")
    gas_recovery_end_year: Optional[int] = Field(None, description="End year of LFG recovery")



class LandfillData(BaseModel):
    waste_disposed: float = Field(..., gt=0, description="Amount of waste disposed at the site (tons)")
    electricity_kwh_per_day: float = Field(..., ge=0, description="Electricity used for landfill operations (kWh/day)")
    fuel_consumption: FuelConsumption = Field(..., description="Fossil fuel consumption (L or kg per day)")
    landfill_operation: LandfillOperationInfo = Field(None, description="Details about landfill operation and disposal trends")
    landfill_gas_recovery: LandfillGasRecovery = Field(None, description="Landfill gas recovery details")


# Output model for landfill results
class LandfillResponse(BaseModel):
    """
    Pydantic model for landfill emissions response.
    Includes both per-tonne (kgCO2e/ton waste disposed) and total (kgCO2e) outputs.

    Per-tonne outputs (per ton waste disposed):
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

    Total outputs (for all waste disposed, in kgCO2e or kg):
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

    ch4_emissions: float  # CH₄ emissions from landfill (kgCO₂e/ton waste disposed)
    ch4_emissions_avoid: float  # CH₄ emissions avoided due to landfill gas recovery (kgCO₂e/ton waste disposed)
    co2_emissions: float  # CO₂ emissions from landfill (kgCO₂e/ton waste disposed)
    co2_emissions_avoid: float  # CO₂ emissions avoided due to landfill gas recovery (kgCO₂e/ton waste disposed)
    n2o_emissions: float  # N₂O emissions from landfill (kgCO₂e/ton waste disposed)
    n2o_emissions_avoid: float  # N₂O emissions avoided due to landfill gas recovery (kgCO₂e/ton waste disposed)
    bc_emissions: float  # Black Carbon emissions from landfill (kg/ton waste disposed)
    bc_emissions_avoid: float  # Black Carbon emissions avoided due to landfill gas recovery (kg/ton waste disposed)
    total_emissions: float  # Total CO₂-equivalent emissions from landfill (kgCO₂e/ton waste disposed)
    total_emissions_avoid: float  # Total CO₂-equivalent emissions avoided due to landfill gas recovery (kgCO₂e/ton waste disposed)
    net_emissions: float  # Net emissions from landfill (kgCO₂e/ton waste disposed)
    net_emissions_bc: float  # Net Black Carbon emissions (kg/ton waste disposed)

    ch4_emissions_total: float  # CH₄ emissions from landfill (kgCO₂e)
    ch4_emissions_avoid_total: float  # CH₄ emissions avoided due to landfill gas recovery (kgCO₂e)
    co2_emissions_total: float  # CO₂ emissions from landfill (kgCO₂e)
    co2_emissions_avoid_total: float  # CO₂ emissions avoided due to landfill gas recovery (kgCO₂e)
    n2o_emissions_total: float  # N₂O emissions from landfill (kgCO₂e)
    n2o_emissions_avoid_total: float  # N₂O emissions avoided due to landfill gas recovery (kgCO₂e)
    bc_emissions_total: float  # Black Carbon emissions from landfill (kg)
    bc_emissions_avoid_total: float  # Black Carbon emissions avoided due to landfill gas recovery (kg)
    total_emissions_total: float  # Total CO₂-equivalent emissions from landfill (kgCO₂e)
    total_emissions_avoid_total: float  # Total CO₂-equivalent emissions avoided due to landfill gas recovery (kgCO₂e)
    net_emissions_total: float  # Net emissions from landfill (kgCO₂e)
    net_emissions_bc_total: float  # Net Black Carbon emissions (kg)