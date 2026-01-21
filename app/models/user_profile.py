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
    food: float
    garden: float
    plastic: float
    paper: float
    textile: float
    rubber: float
    glass: float
    metal: float
    nappies: float
    wood: float
    hazardous: float
    others: float

class Transportation(BaseModel):
    vehicleType: str
    fuelsUsed: List[str]
    transferStationFuels: List[str] = Field(default_factory=list)

class TransportationData(BaseModel):
    enabled: bool = False
    vehicleType: str = ""
    fuelsUsed: List[str] = Field(default_factory=list)

class Composting(BaseModel):
    compostProduction: str
    compostUsed: str
    fuelsUsed: List[str]
    inputTransport: TransportationData = Field(default_factory=TransportationData)
    outputTransport: TransportationData = Field(default_factory=TransportationData)

class AnaerobicDigestion(BaseModel):
    energyProduct: str
    fossilFuelReplaced: str
    compostRecoveryOption: str
    compostRecoveryPercentage: str
    fuelsUsed: List[str]
    inputTransport: TransportationData = Field(default_factory=TransportationData)
    outputTransport: TransportationData = Field(default_factory=TransportationData)

class RecyclingFormal(BaseModel):
    paper: str
    plastic: str
    aluminum: str
    metal: str = Field(validation_alias='steel')
    glass: str

    class Config:
        populate_by_name = True  # Allow both 'metal' and 'steel'

class RecyclingInformal(BaseModel):
    paper: str
    plastic: str
    aluminum: str
    metal: str = Field(validation_alias='steel')
    glass: str

    class Config:
        populate_by_name = True  # Allow both 'metal' and 'steel'

class Recycling(BaseModel):
    formal: RecyclingFormal
    informal: RecyclingInformal
    inputTransport: TransportationData = Field(default_factory=TransportationData)
    outputTransport: TransportationData = Field(default_factory=TransportationData)
    energyInputs: Optional['EnergyInputs'] = None

class EnergyInput(BaseModel):
    petrol: bool = False
    diesel: bool = False
    cng: bool = False
    coal: bool = False
    petrolAmount: Optional[str] = ""
    dieselAmount: Optional[str] = ""
    cngAmount: Optional[str] = ""
    coalAmount: Optional[str] = ""
    electricityAmount: Optional[str] = ""
    recyclability: Optional[str] = ""

class EnergyInputs(BaseModel):
    paper: EnergyInput = Field(default_factory=EnergyInput)
    plastic: EnergyInput = Field(default_factory=EnergyInput)
    aluminum: EnergyInput = Field(default_factory=EnergyInput)
    metal: EnergyInput = Field(default_factory=EnergyInput, validation_alias='steel')
    glass: EnergyInput = Field(default_factory=EnergyInput)

    class Config:
        populate_by_name = True  # Allow both 'metal' and 'steel'

class Incineration(BaseModel):
    caloricValue: str
    incinerationTechnology: str
    energyRecoveryType: str
    electricityEfficiency: str
    electricityUsedOnsite: str
    heatEfficiency: str
    recoveredHeatUsed: str
    fossilFuelReplaced: str
    fuelsUsed: List[str] = Field(default_factory=list)
    inputTransport: TransportationData = Field(default_factory=TransportationData)
    outputTransport: TransportationData = Field(default_factory=TransportationData)

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
    fuelsUsed: List[str] = Field(default_factory=list)

class UserProfile(BaseModel):
    user_id: str
    cityData: CityData
    wasteComposition: WasteComposition
    transportation: Transportation
    composting: Composting
    anaerobicDigestion: AnaerobicDigestion
    recycling: Recycling
    incineration: Incineration
    landfill: Landfill
