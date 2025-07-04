from pydantic import BaseModel, Field
from typing import List, Optional


class LandfillRequest(BaseModel):
    """
    Pydantic model for landfill emissions request.

    Attributes:
        waste_disposed (float): Amount of waste disposed at the site (tons).
        waste_disposed_fired (float): Percentage of waste disposed via open burning (tons).
        landfill_type (str): Type of landfill (e.g., "landfill", "open dump").
        start_year (int): Starting year of waste disposal.
        end_year (int): End year of waste disposal.
        current_year (int): Current year of disposal.
        annual_growth_rate (float): Estimated growth of annual disposal at the landfill (%).
        fossil_fuel_types (List[str]): Types of fossil fuels used for operation activities.
        fossil_fuel_consumed (List[float]): Consumption of fossil fuels used for operation activities (liters).
        grid_electricity (float): Grid electricity used for operation activities (kWh).
        gas_collection_efficiency (float): Efficiency of gas collection (%).
        gas_treatment_method (Optional[str]): Treatment method of collected landfill gas.
        lfg_utilization_efficiency (float): LFG utilization efficiency (e.g., electricity production, flare efficiency).
        gas_recovery_start_year (Optional[int]): Starting year of gas recovery after commencing the landfill.
        gas_recovery_end_year (Optional[int]): Closing year of gas recovery project.
        replaced_fossil_fuel_type (Optional[str]): Type of fossil fuel replaced by recovered LFG.
    """

    waste_disposed: float = Field(..., gt=0, description="Amount of waste disposed at the site (tons)")
    waste_disposed_fired: float = Field(..., ge=0, description="Percentage of waste disposed via open burning (tons)")
    landfill_type: str = Field(..., description="Type of landfill (e.g., 'landfill', 'open dump')")
    start_year: int = Field(..., ge=1900, description="Starting year of waste disposal")
    end_year: int = Field(..., ge=1900, description="End year of waste disposal")
    current_year: int = Field(..., ge=1900, description="Current year of disposal")
    annual_growth_rate: float = Field(..., ge=0, description="Estimated growth of annual disposal at the landfill (%)")
    fossil_fuel_types: List[str] = Field(..., description="Types of fossil fuels used for operation activities")
    fossil_fuel_consumed: List[float] = Field(..., description="Consumption of fossil fuels used for operation activities (liters)")
    grid_electricity: float = Field(..., ge=0, description="Grid electricity used for operation activities (kWh)")
    gas_collection_efficiency: float = Field(..., ge=0, le=100, description="Efficiency of gas collection (%)")
    gas_treatment_method: Optional[str] = Field(None, description="Treatment method of collected landfill gas")
    lfg_utilization_efficiency: float = Field(..., ge=0, le=100, description="LFG utilization efficiency (%)")
    gas_recovery_start_year: Optional[int] = Field(None, ge=1900, description="Starting year of gas recovery after commencing the landfill")
    gas_recovery_end_year: Optional[int] = Field(None, ge=1900, description="Closing year of gas recovery project")
    replaced_fossil_fuel_type: Optional[str] = Field(None, description="Type of fossil fuel replaced by recovered LFG")


class LandfillResponse(BaseModel):
    """
    Pydantic model for landfill emissions response.

    Attributes:
        ch4_emissions (float): CH₄ emissions from landfill (kgCO₂e/ton waste disposed).
        ch4_emissions_avoid (float): CH₄ emissions avoided due to landfill gas recovery (kgCO₂e/ton waste disposed).
        co2_emissions (float): CO₂ emissions from landfill (kgCO₂e/ton waste disposed).
        co2_emissions_avoid (float): CO₂ emissions avoided due to landfill gas recovery (kgCO₂e/ton waste disposed).
        n2o_emissions (float): N₂O emissions from landfill (kgCO₂e/ton waste disposed).
        n2o_emissions_avoid (float): N₂O emissions avoided due to landfill gas recovery (kgCO₂e/ton waste disposed).
        bc_emissions (float): Black Carbon emissions from landfill (kgCO₂e/ton waste disposed).
        bc_emissions_avoid (float): Black Carbon emissions avoided due to landfill gas recovery (kgCO₂e/ton waste disposed).
        total_emissions (float): Total CO₂-equivalent emissions from landfill (kgCO₂e/ton waste disposed).
        total_emissions_avoid (float): Total CO₂-equivalent emissions avoided due to landfill gas recovery (kgCO₂e/ton waste disposed).
        net_emissions (float): Net emissions from landfill (kgCO₂e/ton waste disposed).
    """

    ch4_emissions: float  # CH₄ emissions from landfill (kgCO₂e/ton waste disposed)
    ch4_emissions_avoid: float  # CH₄ emissions avoided due to landfill gas recovery (kgCO₂e/ton waste disposed)
    co2_emissions: float  # CO₂ emissions from landfill (kgCO₂e/ton waste disposed)
    co2_emissions_avoid: float  # CO₂ emissions avoided due to landfill gas recovery (kgCO₂e/ton waste disposed)
    n2o_emissions: float  # N₂O emissions from landfill (kgCO₂e/ton waste disposed)
    n2o_emissions_avoid: float  # N₂O emissions avoided due to landfill gas recovery (kgCO₂e/ton waste disposed)
    bc_emissions: float  # Black Carbon emissions from landfill (kgCO₂e/ton waste disposed)
    bc_emissions_avoid: float  # Black Carbon emissions avoided due to landfill gas recovery (kgCO₂e/ton waste disposed)
    total_emissions: float  # Total CO₂-equivalent emissions from landfill (kgCO₂e/ton waste disposed)
    total_emissions_avoid: float  # Total CO₂-equivalent emissions avoided due to landfill gas recovery (kgCO₂e/ton waste disposed)
    net_emissions: float  # Net emissions from landfill (kgCO₂e/ton waste disposed)