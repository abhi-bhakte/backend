from fastapi import APIRouter, HTTPException
from app.models.results_models.transportation import TransportationRequest, TransportationResponse
from app.services.transportation import TransportationEmissions

# Create a FastAPI router instance
router = APIRouter()


@router.post("/calculate", response_model=TransportationResponse)
def calculate_transportation_emissions(request: TransportationRequest):
    """
    API endpoint to compute GHG emissions for transportation.
    
    Args:
        request (TransportationRequest): Input data containing waste and fuel usage details.
    
    Returns:
        TransportationResponse: Calculated emissions data.
    
    Raises:
        HTTPException: If an invalid input value is provided.
    """
    try:
        # Initialize the TransportationEmissions service with request parameters
        emissions_service = TransportationEmissions(
            waste_formal=request.waste_formal,
            fuel_types_transport=request.fuel_types_transport,
            fuel_consumed_transport=request.fuel_consumed_transport,
            vehicle_type=request.vehicle_type,
            waste_transfer_station=request.waste_transfer_station,
            fuel_types_station=request.fuel_types_station,
            fuel_consumed_station=request.fuel_consumed_station,
            electric_consumed=request.electric_consumed,
            waste_handled_at_station=request.waste_handled_at_station
        )

        # Compute overall emissions
        emissions = emissions_service.overall_emissions()

        # Return the computed emissions as a response
        return TransportationResponse(**emissions)

    except ValueError as e:
        # Handle invalid input values and return an HTTP 400 error
        raise HTTPException(status_code=400, detail=str(e))
