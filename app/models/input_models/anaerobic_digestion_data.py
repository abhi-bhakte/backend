# models/input_models/anaerobic_digestion_data.py

from pydantic import BaseModel, Field
from typing import Optional

class ADFuelConsumption(BaseModel):
    petrol: Optional[float] = Field(None, description="Petrol used for AD operations (L/day)")
    diesel: Optional[float] = Field(None, description="Diesel used for AD operations (L/day)")
    cng: Optional[float] = Field(None, description="CNG used for AD operations (L/day)")

class ADEnergyProduction(BaseModel):
    ad_energy_product: Optional[str] = Field(None,description="Product from AD: 'electricity', 'heat', or 'biogas'" )
    fuel_replaced: Optional[str] = Field(None,description="Fossil fuel replaced when energy product displaces conventional fuel")
    compost_recovered: bool = Field(False, description="Is compost recovered from AD?")
    compost_recovery_percent: Optional[float] = Field(None,ge=0,le=100,description="Percentage of compost recovered (0-100%)")

class AnaerobicDigestionData(BaseModel):
    waste_digested: float = Field(..., gt=0, description="Total waste anaerobically digested (tons)")
    electricity_kwh_per_day: float = Field(..., description="Electricity used for AD operations (kWh/day)")
    fuel_consumption: Optional[ADFuelConsumption] = Field(None, description="Fuel used in AD operations")
    energy_and_compost: ADEnergyProduction = Field(..., description="Biogas energy use and compost recovery data")
