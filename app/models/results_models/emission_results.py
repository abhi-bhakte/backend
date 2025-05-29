from pydantic import BaseModel
from typing import Optional
from .transportation import TransportationResponse

class WasteEmissionResult(BaseModel):
    transportation: Optional[TransportationResponse] = None
