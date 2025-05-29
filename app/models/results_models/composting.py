from pydantic import BaseModel, Field
from typing import List


class CompostingRequest(BaseModel):
    """
    Pydantic model for composting emissions request.
    
    Attributes:
        waste_composted (float): Total waste composted (tons).
        percent_compost_use_agri_garden (float): Percentage of compost used in agriculture/gardens.
        compost_prod_potential (float): Compost production potential (tons).
        electricity_consumed (float): Electricity consumed during composting (kWh).
        fuel_types_operation (List[str]): Types of fuel used in composting operations.
        fuel_consumed_operation (List[float]): Fuel consumption in liters.
    """
    
    waste_composted: float = Field(..., gt=0, description="Total waste composted (tons)")
    percent_compost_use_agri_garden: float = Field(..., ge=0, le=100, description="Percentage of compost used in agriculture/gardens")
    compost_prod_potential: float = Field(..., ge=0, description="Compost production potential (tons)")
    electricity_consumed: float = Field(..., ge=0, description="Electricity consumed during composting (kWh)")
    fuel_types_operation: List[str] = Field(..., description="Types of fuel used in composting operations")
    fuel_consumed_operation: List[float] = Field(..., description="Fuel consumption in liters")


class CompostingResponse(BaseModel):
    """
    Pydantic model for composting emissions response.
    
    Attributes:
        ch4_emissions (float): CH4 emissions from composting (kgCO2e/ton waste composted).
        ch4_emissions_avoid (float): CH4 emissions avoided due to composting (kgCO2e/ton waste composted).
        co2_emissions (float): CO2 emissions from composting (kgCO2e/ton waste composted).
        co2_emissions_avoid (float): CO2 emissions avoided due to composting (kgCO2e/ton waste composted).
        n2o_emissions (float): N2O emissions from composting (kgCO2e/ton waste composted).
        n2o_emissions_avoid (float): N2O emissions avoided due to composting (kgCO2e/ton waste composted).
        bc_emissions (float): Black Carbon emissions from composting (kgCO2e/ton waste composted).
        bc_emissions_avoid (float): Black Carbon emissions avoided due to composting (kgCO2e/ton waste composted).
        total_emissions (float): Total CO2-equivalent emissions from composting (kgCO2e/ton waste composted).
        total_emissions_avoid (float): Total CO2-equivalent emissions avoided due to composting (kgCO2e/ton waste composted).
    """
    
    ch4_emissions: float  # CH4 emissions from composting (kgCO2e/ton waste composted)
    ch4_emissions_avoid: float  # CH4 emissions avoided due to composting (kgCO2e/ton waste composted)
    co2_emissions: float  # CO2 emissions from composting (kgCO2e/ton waste composted)
    co2_emissions_avoid: float  # CO2 emissions avoided due to composting (kgCO2e/ton waste composted)
    n2o_emissions: float  # N2O emissions from composting (kgCO2e/ton waste composted)
    n2o_emissions_avoid: float  # N2O emissions avoided due to composting (kgCO2e/ton waste composted)
    bc_emissions: float  # Black Carbon emissions from composting (kgCO2e/ton waste composted)
    bc_emissions_avoid: float  # Black Carbon emissions avoided due to composting (kgCO2e/ton waste composted)
    total_emissions: float  # Total CO2eq emissions from composting (kgCO2e/ton waste composted)
    total_emissions_avoid: float  # Total CO2eq emissions avoided due to composting (kgCO2e/ton waste composted)
    net_emissions: float  # Net emissions from composting (kgCO2e/ton waste composted)