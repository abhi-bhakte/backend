from pydantic import BaseModel, Field, validator
from typing import List


class AnaerobicDigestionRequest(BaseModel):
    """
    Pydantic model for anaerobic digestion emissions request.
    
    Attributes:
        waste_digested (float): Total waste anaerobically digested (tons).
        ad_energy_product (str): Type of product from anaerobic digestion (electricity, heat, biogas).
        fuel_replaced (str): Fossil fuel replaced if the recovered product is heat or biogas.
        compost_recovered (bool): Whether compost (solid digestate) is recovered from AD.
        percent_compost_use_agri_garden (float): Percentage of recovered compost used in agriculture/gardens.
        electricity_consumed (float): Electricity consumed during anaerobic digestion (kWh).
        fuel_types_operation (List[str]): Types of fuel used in anaerobic digestion operations.
        fuel_consumed_operation (List[float]): Fuel consumption in liters.
    """
    
    waste_digested: float = Field(..., gt=0, description="Total waste anaerobically digested (tons)")
    ad_energy_product: str = Field(..., description="Type of product from anaerobic digestion (electricity, heat, biogas)")
    fuel_replaced: str = Field(..., description="Fossil fuel replaced if the recovered product is heat or biogas")
    compost_recovered: bool = Field(..., description="Whether compost (solid digestate) is recovered from AD")
    percent_compost_use_agri_garden: float = Field(..., ge=0, le=100, description="Percentage of recovered compost used in agriculture/gardens")
    electricity_consumed: float = Field(..., ge=0, description="Electricity consumed during anaerobic digestion (kWh)")
    fuel_types_operation: List[str] = Field(..., description="Types of fuel used in anaerobic digestion operations")
    fuel_consumed_operation: List[float] = Field(..., description="Fuel consumption in liters")

    @validator("fuel_replaced")
    def validate_fuel_replaced(cls, value):
        if not value.strip():  # Ensure the value is not empty or whitespace
            raise ValueError("fuel_replaced cannot be empty")
        return value


class AnaerobicDigestionResponse(BaseModel):
    """
    Pydantic model for anaerobic digestion emissions response.
    
    Attributes:
        ch4_emissions (float): CH4 emissions from anaerobic digestion (kgCO2e/ton waste digested).
        ch4_emissions_avoid (float): CH4 emissions avoided due to anaerobic digestion (kgCO2e/ton waste digested).
        co2_emissions (float): CO2 emissions from anaerobic digestion (kgCO2e/ton waste digested).
        co2_emissions_avoid (float): CO2 emissions avoided due to anaerobic digestion (kgCO2e/ton waste digested).
        n2o_emissions (float): N2O emissions from anaerobic digestion (kgCO2e/ton waste digested).
        n2o_emissions_avoid (float): N2O emissions avoided due to anaerobic digestion (kgCO2e/ton waste digested).
        bc_emissions (float): Black Carbon emissions from anaerobic digestion (kgCO2e/ton waste digested).
        bc_emissions_avoid (float): Black Carbon emissions avoided due to anaerobic digestion (kgCO2e/ton waste digested).
        total_emissions (float): Total CO2-equivalent emissions from anaerobic digestion (kgCO2e/ton waste digested).
        total_emissions_avoid (float): Total CO2-equivalent emissions avoided due to anaerobic digestion (kgCO2e/ton waste digested).
        net_emissions (float): Net emissions from anaerobic digestion (kgCO2e/ton waste digested).
    """
    
    ch4_emissions: float  # CH4 emissions from anaerobic digestion (kgCO2e/ton waste digested)
    ch4_emissions_avoid: float  # CH4 emissions avoided due to anaerobic digestion (kgCO2e/ton waste digested)
    co2_emissions: float  # CO2 emissions from anaerobic digestion (kgCO2e/ton waste digested)
    co2_emissions_avoid: float  # CO2 emissions avoided due to anaerobic digestion (kgCO2e/ton waste digested)
    n2o_emissions: float  # N2O emissions from anaerobic digestion (kgCO2e/ton waste digested)
    n2o_emissions_avoid: float  # N2O emissions avoided due to anaerobic digestion (kgCO2e/ton waste digested)
    bc_emissions: float  # Black Carbon mass from AD operations (kg/ton waste digested)
    bc_emissions_avoid: float  # Black Carbon mass avoided (kg/ton waste digested)
    total_emissions: float  # Total CO2eq emissions from anaerobic digestion (kgCO2e/ton waste digested)
    total_emissions_avoid: float  # Total CO2eq emissions avoided due to anaerobic digestion (kgCO2e/ton waste digested)
    net_emissions: float  # Net GHG emissions (CO2e) excluding BC mass (kgCO2e/ton waste digested)
    net_emissions_bc: float  # Net BC mass (kg/ton waste digested)