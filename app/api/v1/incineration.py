from fastapi import APIRouter, HTTPException

from app.models.input_models.incineration_data import IncinerationData
from app.models.results_models.incineration import IncinerationResponse
from app.services.incineration import IncinerationEmissions

# Create a FastAPI router instance
router = APIRouter()


@router.post("/calculate", response_model=IncinerationResponse)
def calculate_incineration_emissions(request: IncinerationData):
    """
    API endpoint to compute GHG emissions for incineration.

    Args:
        request (IncinerationRequest): Input data containing waste and fuel usage details.

    Returns:
        IncinerationResponse: Calculated emissions data.

    Raises:
        HTTPException: If an invalid input value is provided.
    """
    try:

        # Extract mixed_waste_composition from incinerator_info
        inc_info = request.incinerator_info.dict() if hasattr(request.incinerator_info, 'dict') else request.incinerator_info
        mixed_comp = inc_info.get('mixed_waste_composition', {})
        emissions_service = IncinerationEmissions(
            waste_incinerated=request.waste_incinerated,
            electricity_kwh_per_day=request.electricity_kwh_per_day,
            fuel_consumption=request.fuel_consumption.dict() if hasattr(request.fuel_consumption, 'dict') else request.fuel_consumption,
            incinerator_info=inc_info,
            energy_recovery=request.energy_recovery.dict() if hasattr(request.energy_recovery, 'dict') else request.energy_recovery,
            mixed_waste_composition=mixed_comp,
        )

        # Compute overall emissions
        emissions = emissions_service.overall_emissions()

        # Return the computed emissions as a response
        return IncinerationResponse(**emissions)

    except ValueError as e:
        # Handle invalid input values and return an HTTP 400 error
        raise HTTPException(status_code=400, detail=str(e))