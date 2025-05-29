from pydantic import BaseModel, Field
from typing import List


class IncinerationRequest(BaseModel):
    """
    Pydantic model for incineration emissions request.

    Attributes:
        waste_incinerated (float): Amount of waste incinerated (tons/day).
        incineration_type (str): Type of incineration.
        fossil_fuel_types (List[str]): List of fossil fuel types used for operation activities.
        fossil_fuel_consumptions (List[float]): List of fossil fuel consumption values (liters/day).
        electricity_used (float): Electricity used for operation activities (kWh/day).
        energy_recovery_type (str): Type of energy recovered (e.g., heat, electricity).
        efficiency_electricity_recovery (float): Efficiency of electricity recovery.
        percentage_electricity_used_onsite (float): Percentage of electricity used onsite.
        efficiency_heat_recovery (float): Efficiency of heat recovery.
        percentage_heat_used_onsite (float): Percentage of recovered heat used onsite.
        fossil_fuel_replaced (List[str]): List of fossil fuel types replaced by recovered heat.
    """

    waste_incinerated: float = Field(..., gt=0, description="Amount of waste incinerated (tons/day)")
    incineration_type: str = Field(..., description="Type of incineration")
    fossil_fuel_types: List[str] = Field(..., description="List of fossil fuel types used for operation activities")
    fossil_fuel_consumptions: List[float] = Field(..., description="List of fossil fuel consumption values (liters/day)")
    electricity_used: float = Field(..., ge=0, description="Electricity used for operation activities (kWh/day)")
    energy_recovery_type: str = Field(..., description="Type of energy recovered (e.g., heat, electricity)")
    efficiency_electricity_recovery: float = Field(..., ge=0, le=100, description="Efficiency of electricity recovery")
    percentage_electricity_used_onsite: float = Field(..., ge=0, le=100, description="Percentage of electricity used onsite")
    efficiency_heat_recovery: float = Field(..., ge=0, le=100, description="Efficiency of heat recovery")
    percentage_heat_used_onsite: float = Field(..., ge=0, le=100, description="Percentage of recovered heat used onsite")
    fossil_fuel_replaced: List[str] = Field(..., description="List of fossil fuel types replaced by recovered heat")


class IncinerationResponse(BaseModel):
    """
    Pydantic model for incineration emissions response.

    Attributes:
        ch4_emissions (float): CH4 emissions from incineration (kgCO2e/ton waste incinerated).
        ch4_emissions_avoid (float): CH4 emissions avoided due to incineration (kgCO2e/ton waste incinerated).
        co2_emissions (float): CO2 emissions from incineration (kgCO2e/ton waste incinerated).
        co2_emissions_avoid (float): CO2 emissions avoided due to incineration (kgCO2e/ton waste incinerated).
        n2o_emissions (float): N2O emissions from incineration (kgCO2e/ton waste incinerated).
        n2o_emissions_avoid (float): N2O emissions avoided due to incineration (kgCO2e/ton waste incinerated).
        bc_emissions (float): Black Carbon emissions from incineration (kgCO2e/ton waste incinerated).
        bc_emissions_avoid (float): Black Carbon emissions avoided due to incineration (kgCO2e/ton waste incinerated).
        total_emissions (float): Total CO2-equivalent emissions from incineration (kgCO2e/ton waste incinerated).
        total_emissions_avoid (float): Total CO2-equivalent emissions avoided due to incineration (kgCO2e/ton waste incinerated).
        net_emissions (float): Net emissions from incineration (kgCO2e/ton waste incinerated).
    """

    ch4_emissions: float  # CH4 emissions from incineration (kgCO2e/ton waste incinerated)
    ch4_emissions_avoid: float  # CH4 emissions avoided due to incineration (kgCO2e/ton waste incinerated)
    co2_emissions: float  # CO2 emissions from incineration (kgCO2e/ton waste incinerated)
    co2_emissions_avoid: float  # CO2 emissions avoided due to incineration (kgCO2e/ton waste incinerated)
    n2o_emissions: float  # N2O emissions from incineration (kgCO2e/ton waste incinerated)
    n2o_emissions_avoid: float  # N2O emissions avoided due to incineration (kgCO2e/ton waste incinerated)
    bc_emissions: float  # Black Carbon emissions from incineration (kgCO2e/ton waste incinerated)
    bc_emissions_avoid: float  # Black Carbon emissions avoided due to incineration (kgCO2e/ton waste incinerated)
    total_emissions: float  # Total CO2eq emissions from incineration (kgCO2e/ton waste incinerated)
    total_emissions_avoid: float  # Total CO2eq emissions avoided due to incineration (kgCO2e/ton waste incinerated)
    net_emissions: float  # Net emissions from incineration (kgCO2e/ton waste incinerated)