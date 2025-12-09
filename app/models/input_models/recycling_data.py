# models/input_models/recycling_data.py

from pydantic import BaseModel, Field
from typing import Dict

class RecyclingData(BaseModel):
    recycle_collected_formal: float = Field(..., gt=0, description="Total recyclable collected by the formal sector (tons)")
    recycle_collected_informal: float = Field(..., ge=0, description="Total recyclable collected by the informal sector (tons)")
    material_composition_formal: Dict[str, float] = Field(..., description="Composition (%) of materials collected by the formal sector")
    material_composition_informal: Dict[str, float] = Field(..., description="Composition (%) of materials collected by the informal sector")
    electricity_consumed: Dict[str, float] = Field(..., description="Electricity consumed during recycling for each material (kWh)")
    fuel_consumption: Dict[str, Dict[str, float]] = Field(..., description="Fuel consumption for each material and fuel type (liters)")
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
        bc_emissions (float): Black Carbon emissions from recycling (kg/ton waste recycled, NOT CO2e).
        bc_emissions_avoid (float): Black Carbon emissions avoided due to recycling (kg/ton waste recycled, NOT CO2e).
        total_emissions (float): Total CO2-equivalent emissions from recycling (kgCO2e/ton waste recycled).
        total_emissions_avoid (float): Total CO2-equivalent emissions avoided due to recycling (kgCO2e/ton waste recycled).
        net_emissions (float): Net emissions from recycling (kgCO2e/ton waste recycled).
        net_emissions_bc (float): Net Black Carbon emissions (kg/ton waste recycled, NOT CO2e).
        ch4_emissions_total (float): Total CH4 emissions from recycling (kgCO2e).
        ch4_emissions_avoid_total (float): Total CH4 emissions avoided due to recycling (kgCO2e).
        co2_emissions_total (float): Total CO2 emissions from recycling (kgCO2e).
        co2_emissions_avoid_total (float): Total CO2 emissions avoided due to recycling (kgCO2e).
        n2o_emissions_total (float): Total N2O emissions from recycling (kgCO2e).
        n2o_emissions_avoid_total (float): Total N2O emissions avoided due to recycling (kgCO2e).
        bc_emissions_total (float): Total Black Carbon emissions from recycling (kg, NOT CO2e).
        bc_emissions_avoid_total (float): Total Black Carbon emissions avoided due to recycling (kg, NOT CO2e).
        total_emissions_total (float): Combined total CO2-equivalent emissions from recycling (kgCO2e).
        total_emissions_avoid_total (float): Combined total CO2-equivalent emissions avoided (kgCO2e).
        net_emissions_total (float): Net total emissions after avoidance (kgCO2e).
        net_emissions_bc_total (float): Net total Black Carbon emissions (kg, NOT CO2e).
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