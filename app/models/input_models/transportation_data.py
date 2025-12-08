# models/input_models/transportation_data.py
from pydantic import BaseModel, Field
from typing import Optional, List

class FuelConsumption(BaseModel):
    petrol: Optional[float] = Field(0, description="Petrol used (L/day)")
    diesel: Optional[float] = Field(0, description="Diesel used (L/day)")
    cng: Optional[float] = Field(0, description="CNG used (kg/day)")
    ev: Optional[float] = Field(0, description="Electricity used (kWh/day)")

class WasteCollectionEnergyUse(BaseModel):
    waste_formal: float = Field(..., ge=0, description="Waste collected from formal sector (tons)")
    vehicle_type: str = Field(..., description="Type of collection vehicle")
    fuel_consumption: FuelConsumption = Field(..., description="Fuel consumption during collection")

class TransferStationEnergyUse(BaseModel):
    waste_handled_tpd: float = Field(..., description="Waste handled at transfer station (tonnes/day)")
    electricity_kwh_per_day: float = Field(..., description="Electricity used (kWh/day)")
    fuel_consumption: FuelConsumption = Field(..., description="Fuel consumption at transfer station")

class TransportationData(BaseModel):
    waste_collection: WasteCollectionEnergyUse = Field(..., description="Waste collection data including vehicle type and fuel consumption")
    transfer_station: Optional[TransferStationEnergyUse | dict] = Field(
        None, description="Energy and fuel use at transfer station"
    )


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

    # Per-ton outputs (kgCO2e per ton; BC is kg per ton)
    ch4_emissions: float
    co2_emissions: float
    n2o_emissions: float
    bc_emissions: float
    total_emissions: float
    total_emissions_avoid: float
    net_emissions: float
    net_emissions_bc: float

    # Absolute totals (kgCO2e or kg for BC)
    ch4_emissions_total: float
    co2_emissions_total: float
    n2o_emissions_total: float
    bc_emissions_total: float
    total_emissions_total: float
    total_emissions_avoid_total: float
    net_emissions_total: float
    net_emissions_bc_total: float

