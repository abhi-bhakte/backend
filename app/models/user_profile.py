from pydantic import BaseModel, Field
from typing import Optional, List

class CityData(BaseModel):
    cityName: str
    population: str
    area: str
    wards: str
    wasteGeneration: str
    treatmentMethods: List[str]

class WasteComposition(BaseModel):
    foodWaste: float
    gardenWaste: float
    plastic: float
    paper: float
    textile: float
    leatherRubber: float
    glass: float
    metal: float
    nappies: float
    wood: float
    hazardous: float
    others: float

class Transportation(BaseModel):
    vehicleType: str
    fuelsUsed: List[str]

class Composting(BaseModel):
    compostProduction: str
    compostUsed: str
    fuelsUsed: List[str]

class AnaerobicDigestion(BaseModel):
    energyProduct: str
    fossilFuelReplaced: str
    compostRecoveryOption: str
    compostRecoveryPercentage: str
    fuelsUsed: List[str]

class RecyclingFormal(BaseModel):
    paperCardboard: str
    plastic: str
    aluminum: str
    steel: str
    glass: str

class RecyclingInformal(BaseModel):
    paperCardboard: str
    plastic: str
    aluminum: str
    steel: str
    glass: str

class Recycling(BaseModel):
    formal: RecyclingFormal
    informal: RecyclingInformal

class EnergyInput(BaseModel):
    petrol: bool
    diesel: bool
    cng: bool
    coal: bool

class EnergyInputs(BaseModel):
    paper: EnergyInput
    plastic: EnergyInput
    aluminum: EnergyInput
    steel: EnergyInput
    glass: EnergyInput

class Incineration(BaseModel):
    caloricValue: str
    incinerationTechnology: str
    energyRecoveryType: str
    electricityEfficiency: str
    electricityUsedOnsite: str
    heatEfficiency: str
    recoveredHeatUsed: str
    fossilFuelReplaced: str

class Landfill(BaseModel):
    landfillType: str
    wasteOpenBurned: str
    annualDisposalGrowth: str
    disposalStartYear: str
    disposalEndYear: str
    disposalCurrentYear: str
    gasCollectionEfficiency: str
    treatmentMethod: str
    lfgUtilizationEfficiency: str
    gasRecoveryStartYear: str
    gasRecoveryEndYear: str

class UserProfile(BaseModel):
    user_id: str
    cityData: CityData
    wasteComposition: WasteComposition
    transportation: Transportation
    composting: Composting
    anaerobicDigestion: AnaerobicDigestion
    recycling: Recycling
    energyInputs: EnergyInputs
    incineration: Incineration
    landfill: Landfill
