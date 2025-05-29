from fastapi import APIRouter, HTTPException
from app.models.results_models.anaerobic_digestion import AnaerobicDigestionRequest, AnaerobicDigestionResponse
from app.services.anaerobic_digestion import AnaerobicDigestionEmissions

# Create a FastAPI router instance
router = APIRouter()


@router.post("/calculate", response_model=AnaerobicDigestionResponse)
def calculate_anaerobic_digestion_emissions(request: AnaerobicDigestionRequest):
    """
    API endpoint to compute GHG emissions for anaerobic digestion.
    
    Args:
        request (AnaerobicDigestionRequest): Input data containing waste and energy usage details.
    
    Returns:
        AnaerobicDigestionResponse: Calculated emissions data.
    
    Raises:
        HTTPException: If an invalid input value is provided.
    """
    try:
        # Initialize the AnaerobicDigestionEmissions service with request parameters
        emissions_service = AnaerobicDigestionEmissions(
            waste_digested=request.waste_digested,
            ad_energy_product=request.ad_energy_product,
            fuel_replaced=request.fuel_replaced,
            compost_recovered=request.compost_recovered,
            percent_compost_use_agri_garden=request.percent_compost_use_agri_garden,
            electricity_consumed=request.electricity_consumed,
            fuel_types_operation=request.fuel_types_operation,
            fuel_consumed_operation=request.fuel_consumed_operation
        )

        # Compute overall emissions
        emissions = emissions_service.overall_emissions()

        # Return the computed emissions as a response
        return AnaerobicDigestionResponse(**emissions)

    except ValueError as e:
        # Handle invalid input values and return an HTTP 400 error
        raise HTTPException(status_code=400, detail=str(e))