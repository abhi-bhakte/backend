from fastapi import APIRouter, HTTPException
from app.models.composting import CompostingRequest, CompostingResponse
from app.services.composting import CompostingEmissions

# Create a FastAPI router instance
router = APIRouter()


@router.post("/calculate", response_model=CompostingResponse)
def calculate_composting_emissions(request: CompostingRequest):
    """
    API endpoint to compute GHG emissions for composting.
    
    Args:
        request (CompostingRequest): Input data containing waste and fuel usage details.
    
    Returns:
        CompostingResponse: Calculated emissions data.
    
    Raises:
        HTTPException: If an invalid input value is provided.
    """
    try:
        # Initialize the CompostingEmissions service with request parameters
        emissions_service = CompostingEmissions(
            waste_composted=request.waste_composted,
            percent_compost_use_agri_garden=request.percent_compost_use_agri_garden,
            compost_prod_potential=request.compost_prod_potential,
            electricity_consumed=request.electricity_consumed,
            fuel_types_operation=request.fuel_types_operation,
            fuel_consumed_operation=request.fuel_consumed_operation
        )

        # Compute overall emissions
        emissions = emissions_service.overall_emissions()

        # Return the computed emissions as a response
        return CompostingResponse(**emissions)

    except ValueError as e:
        # Handle invalid input values and return an HTTP 400 error
        raise HTTPException(status_code=400, detail=str(e))
