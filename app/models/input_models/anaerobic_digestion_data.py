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



class AnaerobicDigestionResponse(BaseModel):
    """
    Pydantic model for anaerobic digestion emissions response.
    Includes both per-tonne (kgCO2e/ton waste digested) and total (kgCO2e) outputs.

    Per-tonne outputs (per ton waste digested):
        ch4_emissions: CH4 emissions (kgCO2e/ton)
        ch4_emissions_avoid: CH4 emissions avoided (kgCO2e/ton)
        co2_emissions: CO2 emissions (kgCO2e/ton)
        co2_emissions_avoid: CO2 emissions avoided (kgCO2e/ton)
        n2o_emissions: N2O emissions (kgCO2e/ton)
        n2o_emissions_avoid: N2O emissions avoided (kgCO2e/ton)
        bc_emissions: Black Carbon mass (kg/ton)
        bc_emissions_avoid: Black Carbon mass avoided (kg/ton)
        total_emissions: Total CO2eq (CH4+CO2+N2O) (kgCO2e/ton)
        total_emissions_avoid: Total CO2eq avoided (kgCO2e/ton)
        net_emissions: Net CO2eq (kgCO2e/ton)
        net_emissions_bc: Net BC mass (kg/ton)

    Total outputs (for all waste digested, in kgCO2e or kg):
        ch4_emissions_total: CH4 emissions (kgCO2e)
        ch4_emissions_avoid_total: CH4 emissions avoided (kgCO2e)
        co2_emissions_total: CO2 emissions (kgCO2e)
        co2_emissions_avoid_total: CO2 emissions avoided (kgCO2e)
        n2o_emissions_total: N2O emissions (kgCO2e)
        n2o_emissions_avoid_total: N2O emissions avoided (kgCO2e)
        bc_emissions_total: Black Carbon mass (kg)
        bc_emissions_avoid_total: Black Carbon mass avoided (kg)
        total_emissions_total: Total CO2eq (CH4+CO2+N2O) (kgCO2e)
        total_emissions_avoid_total: Total CO2eq avoided (kgCO2e)
        net_emissions_total: Net CO2eq (kgCO2e)
        net_emissions_bc_total: Net BC mass (kg)
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
