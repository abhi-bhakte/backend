from fastapi import APIRouter, HTTPException
from app.models.results_models.incineration import IncinerationRequest, IncinerationResponse
from app.services.incineration import IncinerationEmissions

# Create a FastAPI router instance
router = APIRouter()


@router.post("/calculate", response_model=IncinerationResponse)
def calculate_incineration_emissions(request: IncinerationRequest):
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
        # Initialize the IncinerationEmissions service with request parameters
        emissions_service = IncinerationEmissions(
            waste_incinerated=request.waste_incinerated,
            incineration_type=request.incineration_type,
            fossil_fuel_types=request.fossil_fuel_types,
            fossil_fuel_consumptions=request.fossil_fuel_consumptions,
            electricity_used=request.electricity_used,
            energy_recovery_type=request.energy_recovery_type,
            efficiency_electricity_recovery=request.efficiency_electricity_recovery,
            percentage_electricity_used_onsite=request.percentage_electricity_used_onsite,
            efficiency_heat_recovery=request.efficiency_heat_recovery,
            percentage_heat_used_onsite=request.percentage_heat_used_onsite,
            fossil_fuel_replaced=request.fossil_fuel_replaced,
        )

        # Compute overall emissions
        emissions = emissions_service.overall_emissions()

        # Return the computed emissions as a response
        return IncinerationResponse(**emissions)

    except ValueError as e:
        # Handle invalid input values and return an HTTP 400 error
        raise HTTPException(status_code=400, detail=str(e))