from pydantic import BaseModel, Field
from typing import Dict, List


class RecyclingRequest(BaseModel):
    """
    Pydantic model for recycling emissions request.

    Attributes:
        recycle_collected_formal (float): Total recyclable collected by the formal sector (tons).
        recycle_collected_informal (float): Total recyclable collected by the informal sector (tons).
        material_composition_formal (Dict[str, float]): Composition (%) of materials collected by the formal sector.
        material_composition_informal (Dict[str, float]): Composition (%) of materials collected by the informal sector.
        electricity_consumed (Dict[str, float]): Electricity consumed during recycling for each material (kWh).
        fuel_types_operation (Dict[str, List[str]]): Types of fuel used in recycling operations for each material.
        fuel_consumed_operation (Dict[str, List[float]]): Fuel consumption in liters for each material.
        recyclability (Dict[str, float]): Recyclability of materials (percentage).
    """
    recycle_collected_formal: float = Field(..., gt=0, description="Total recyclable collected by the formal sector (tons)")
    recycle_collected_informal: float = Field(..., ge=0, description="Total recyclable collected by the informal sector (tons)")
    material_composition_formal: Dict[str, float] = Field(..., description="Composition (%) of materials collected by the formal sector")
    material_composition_informal: Dict[str, float] = Field(..., description="Composition (%) of materials collected by the informal sector")
    electricity_consumed: Dict[str, float] = Field(..., description="Electricity consumed during recycling for each material (kWh)")
    fuel_types_operation: Dict[str, List[str]] = Field(..., description="Types of fuel used in recycling operations for each material")
    fuel_consumed_operation: Dict[str, List[float]] = Field(..., description="Fuel consumption in liters for each material")
    recyclability: Dict[str, float] = Field(..., description="Recyclability of materials (percentage)")


class RecyclingResponse(BaseModel):
    """
    Pydantic model for recycling emissions response.

    Attributes:
        ch4_emissions (float): CH4 emissions from recycling (kgCO2e/ton waste recycled).
        ch4_emissions_avoid (float): CH4 emissions avoided due to recycling (kgCO2e/ton waste recycled).
        co2_emissions (float): CO2 emissions from recycling (kgCO2e/ton waste recycled).
        co2_emissions_avoid (float): CO2 emissions avoided due to recycling (kgCO2e/ton waste recycled).
        n2o_emissions (float): N2O emissions from recycling (kgCO2e/ton waste recycled).
        n2o_emissions_avoid (float): N2O emissions avoided due to recycling (kgCO2e/ton waste recycled).
        bc_emissions (float): Black Carbon emissions from recycling (kgCO2e/ton waste recycled).
        bc_emissions_avoid (float): Black Carbon emissions avoided due to recycling (kgCO2e/ton waste recycled).
        total_emissions (float): Total CO2-equivalent emissions from recycling (kgCO2e/ton waste recycled).
        total_emissions_avoid (float): Total CO2-equivalent emissions avoided due to recycling (kgCO2e/ton waste recycled).
        net_emissions (float): Net emissions from recycling (kgCO2e/ton waste recycled).
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