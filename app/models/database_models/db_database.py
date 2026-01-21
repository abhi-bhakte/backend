# Renamed from emission_database.py to db_database.py
# ...existing code from emission_database.py...
from pydantic import BaseModel
from typing import Optional, Literal

class Db(BaseModel):
    coverageLevel: Literal['Regional', 'National', 'Global']
    city: Optional[str] = ""  # Required only if coverageLevel is Regional
    processType: str  # Replaces category
    parameterType: str  # Replaces subcategory
    parameterName: str  # New field
    value: float
    unit: str
    activityBasis: str  # New field
    sourceUrl: Optional[str] = ""
    dataQualityScore: Optional[str] = ""
    uncertaintyRange: Optional[str] = ""
    description: Optional[str] = ""
    updatedAt: Optional[str] = ""
    updatedBy: Optional[str] = ""
    # Legacy fields for backward compatibility
    category: Optional[str] = ""
    subcategory: Optional[str] = ""
