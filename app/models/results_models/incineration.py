from pydantic import BaseModel, Field
from typing import List





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
    bc_emissions: float  # Black Carbon emissions from incineration (kg/ton waste incinerated)
    bc_emissions_avoid: float  # Black Carbon emissions avoided due to incineration (kg/ton waste incinerated)
    total_emissions: float  # Total CO2eq emissions from incineration (kgCO2e/ton waste incinerated)
    total_emissions_avoid: float  # Total CO2eq emissions avoided due to incineration (kgCO2e/ton waste incinerated)
    net_emissions: float  # Net emissions from incineration (kgCO2e/ton waste incinerated)
    net_emissions_bc: float  # Net Black Carbon emissions from incineration (kg/ton waste incinerated)