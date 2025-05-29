"""
Pydantic schema for Emission data used in the GHG Accounting API.

This schema defines the structure and types for emission records,
which are used for both request validation and response formatting
when interacting with the emissions database endpoints.
"""

from pydantic import BaseModel
from typing import Optional

class Emission(BaseModel):
    """
    Pydantic model for a single emission database record.

    Attributes:
        city (str): Name of the city related to the emission data.
        category (str): Category of the emission (e.g., Waste Composition, Treatment Methods).
        treatmentMethod (str): Method used for waste treatment (e.g., Composting, Incineration).
        constantType (Optional[str]): Type of constant or factor (e.g., Emission Factor).
        unit (str): Unit of measurement for the emission value (e.g., kg CO2e/ton).
        value (float): Numeric value representing the emission.
        sourceUrl (Optional[str]): Reference URL for the data source.
        dataQualityScore (Optional[str]): Score or description of data quality.
        uncertaintyRange (Optional[str]): Uncertainty range for the emission value.
        description (Optional[str]): Additional description or notes.
        updatedAt (Optional[str]): Timestamp or date when the record was last updated.
        updatedBy (Optional[str]): Name or ID of the user who last updated the record.
    """
    city: str  # Name of the city
    category: str  # Emission category
    treatmentMethod: str  # Waste treatment method
    constantType: Optional[str]  # Type of constant or factor
    unit: str  # Unit of measurement
    value: float  # Emission value
    sourceUrl: Optional[str] = ""  # Reference URL for data source
    dataQualityScore: Optional[str] = ""  # Data quality score or description
    uncertaintyRange: Optional[str] = ""  # Uncertainty range
    description: Optional[str] = ""  # Additional notes or description
    updatedAt: Optional[str] = ""  # Last updated timestamp
    updatedBy: Optional[str] = ""  # User who last updated