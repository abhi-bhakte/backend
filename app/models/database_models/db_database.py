# Renamed from emission_database.py to db_database.py
# ...existing code from emission_database.py...
from pydantic import BaseModel
from typing import Optional

class Db(BaseModel):
    city: str
    category: str
    subcategory: Optional[str]
    unit: str
    value: float
    sourceUrl: Optional[str] = ""
    dataQualityScore: Optional[str] = ""
    uncertaintyRange: Optional[str] = ""
    description: Optional[str] = ""
    updatedAt: Optional[str] = ""
    updatedBy: Optional[str] = ""
