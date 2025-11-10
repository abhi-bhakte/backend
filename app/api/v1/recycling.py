from fastapi import APIRouter, HTTPException
from app.models.results_models.recycling import RecyclingRequest, RecyclingResponse
from app.services.recycling import RecyclingEmissions

# Create a FastAPI router instance
router = APIRouter()


@router.post("/calculate", response_model=RecyclingResponse)
def calculate_recycling_emissions(request: RecyclingRequest):
    """
    API endpoint to compute GHG emissions for recycling.

    Args:
        request (RecyclingRequest): Input data containing recycling and fuel usage details.

    Returns:
        RecyclingResponse: Calculated emissions data.

    Raises:
        HTTPException: If an invalid input value is provided.
    """
    try:
        # Initialize the RecyclingEmissions service with request parameters
        emissions_service = RecyclingEmissions(
            recycle_collected_formal=request.recycle_collected_formal,
            recycle_collected_informal=request.recycle_collected_informal,
            material_composition_formal=request.material_composition_formal,
            material_composition_informal=request.material_composition_informal,
            electricity_consumed=request.electricity_consumed,
            fuel_consumption=request.fuel_consumption,
            recyclability=request.recyclability
        )

        # Compute overall emissions
        emissions = emissions_service.overall_emissions()

        # Return the computed emissions as a response
        return RecyclingResponse(**emissions)

    except ValueError as e:
        # Handle invalid input values and return an HTTP 400 error
        raise HTTPException(status_code=400, detail=str(e))