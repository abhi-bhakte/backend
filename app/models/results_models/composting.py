from pydantic import BaseModel, Field


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
        bc_emissions (float): Black Carbon mass from composting (kg/ton waste composted).
        bc_emissions_avoid (float): Black Carbon mass avoided due to composting (kg/ton waste composted).
        total_emissions (float): Total CO2-equivalent emissions (CH4+CO2+N2O only) (kgCO2e/ton waste composted).
        total_emissions_avoid (float): Total CO2-equivalent emissions avoided (CH4+CO2+N2O only) (kgCO2e/ton waste composted).
        net_emissions_bc (float): Net BC mass (kg/ton waste composted).
        """
    
    ch4_emissions: float  # CH4 emissions from composting (kgCO2e/ton waste composted)
    ch4_emissions_avoid: float  # CH4 emissions avoided due to composting (kgCO2e/ton waste composted)
    co2_emissions: float  # CO2 emissions from composting (kgCO2e/ton waste composted)
    co2_emissions_avoid: float  # CO2 emissions avoided due to composting (kgCO2e/ton waste composted)
    n2o_emissions: float  # N2O emissions from composting (kgCO2e/ton waste composted)
    n2o_emissions_avoid: float  # N2O emissions avoided due to composting (kgCO2e/ton waste composted)
    bc_emissions: float  # Black Carbon mass from composting (kg/ton waste composted)
    bc_emissions_avoid: float  # Black Carbon mass avoided (kg/ton waste composted)
    total_emissions: float  # Total CO2eq emissions (CH4+CO2+N2O) (kgCO2e/ton waste composted)
    total_emissions_avoid: float  # Total CO2eq avoided (CH4+CO2+N2O) (kgCO2e/ton waste composted)
    net_emissions: float  # Net CO2e emissions (CH4+CO2+N2O) (kgCO2e/ton waste composted)
    net_emissions_bc: float  # Net BC mass (kg/ton waste composted)