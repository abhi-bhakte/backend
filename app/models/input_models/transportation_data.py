# models/input_models/transportation_data.py
from pydantic import BaseModel, Field
from typing import Optional

class TransportationFuelUse(BaseModel):
    petrol: Optional[float] = Field(0, description="Petrol used (L/day)")
    diesel: Optional[float] = Field(0, description="Diesel used (L/day)")
    cng: Optional[float] = Field(0, description="CNG used (kg/day)")
    ev: Optional[float] = Field(0, description="Electricity used (kWh/day)")

class TransferStationEnergyUse(BaseModel):
    waste_handled_tpd: float = Field(..., description="Waste handled at transfer station (tonnes/day)")
    electricity_kwh_per_day: float = Field(..., description="Electricity used (kWh/day)")
    fossil_fuels: TransportationFuelUse = Field(..., description="Fossil fuels used at transfer station")

class TransportationData(BaseModel):
    vehicle_type: str = Field(..., description="Vehicle type used")
    vehicle_fuels: TransportationFuelUse = Field(..., description="Fuel consumption for collection/transportation")
    transfer_station: Optional[TransferStationEnergyUse] = Field(
        None, description="Energy and fuel use at transfer station"
    )
