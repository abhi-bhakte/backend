from pydantic import BaseModel
from typing import Optional

class ReferenceDataItem(BaseModel):
    """Base model for reference data items"""
    name: str
    description: Optional[str] = ""
    isActive: bool = True
    createdAt: Optional[str] = ""
    updatedAt: Optional[str] = ""
    createdBy: Optional[str] = ""
    updatedBy: Optional[str] = ""

class ProcessType(ReferenceDataItem):
    """Process Type reference data"""
    pass

class ParameterType(ReferenceDataItem):
    """Parameter Type reference data"""
    pass

class Unit(ReferenceDataItem):
    """Unit reference data"""
    symbol: Optional[str] = ""  # e.g., kg, ton, tons

class ActivityBasis(ReferenceDataItem):
    """Activity Basis reference data"""
    pass

class City(ReferenceDataItem):
    """City reference data for Regional coverage"""
    country: Optional[str] = ""
    region: Optional[str] = ""

class ReferenceDataResponse(BaseModel):
    """Response model for reference data"""
    id: str
    name: str
    symbol: Optional[str] = None
    description: Optional[str] = ""
    isActive: bool = True
