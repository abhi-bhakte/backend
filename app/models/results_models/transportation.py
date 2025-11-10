from pydantic import BaseModel, Field
from typing import List


class TransportationRequest(BaseModel):
    """
    Pydantic model for transportation emissions request.
    
    Attributes:
        waste_formal (float): Waste collected from the formal sector (tons).
        fuel_types_transport (List[str]): Fuel types used in transport.
        fuel_consumed_transport (List[float]): Fuel consumption values.
        vehicle_type (str): Type of vehicle used.
        waste_transfer_station (bool): Indicates if a transfer station is used.
        waste_handled_at_station (float): Waste handled at the station (tons).
        fuel_types_station (List[str]): Fuel types used at the transfer station.
        fuel_consumed_station (List[float]): Fuel consumption values at the station.
        electric_consumed (float): Electricity consumed at the station (kWh).
    """

    waste_formal: float = Field(..., gt=0, description="Waste collected from formal sector (tons)")
    waste_collection: dict = Field(..., description="Waste collection data including vehicle type and fuel consumption")
    transfer_station: dict = Field(..., description="Transfer station data including fuel and electricity consumption")


class TransportationResponse(BaseModel):
    """
    Pydantic model for transportation emissions response.
    
    Attributes:
        ch4_emissions (float): CH4 emissions per ton of waste (kg/ton).
        co2_emissions (float): CO2 emissions per ton of waste (kg/ton).
        n2o_emissions (float): N2O emissions per ton of waste (kg/ton).
        bc_emissions (float): Black Carbon (BC) emissions per ton of waste (kg/ton, mass only).
        total_emissions (float): Total CO2-equivalent emissions per ton of waste (kg/ton, excludes BC).
        net_emissions_bc (float): Net BC mass (kg/ton).
    """

    ch4_emissions: float  # CH4 per ton of waste (kgCO2e/ton)
    co2_emissions: float  # CO2 per ton of waste (kgCO2e/ton)
    n2o_emissions: float  # N2O per ton of waste (kgCO2e/ton)
    bc_emissions: float   # Black Carbon per ton of waste (kg/ton, mass only)
    total_emissions: float  # Total CO2eq per ton of waste (kgCO2e/ton, excludes BC)
    total_emissions_avoid: float  # Total CO2eq avoided (kgCO2e/ton)
    net_emissions: float  # Net emissions (kgCO2e/ton, excludes BC)
    net_emissions_bc: float  # Net BC mass (kg/ton)
