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
        # Extract new payload structure
        wc = getattr(request, 'waste_collection', {})
        ts = getattr(request, 'transfer_station', None)

        vehicle_type = wc.get('vehicle_type', '')
        vehicle_fuels = wc.get('fuel_consumption', {})
        fuel_types_transport = [k for k, v in vehicle_fuels.items() if v > 0]
        fuel_consumed_transport = [v for k, v in vehicle_fuels.items() if v > 0]

        waste_transfer_station = ts is not None
        waste_handled_at_station = ts['waste_handled_tpd'] if ts else 1
        electric_consumed = ts['electricity_kwh_per_day'] if ts else 0
        station_fuels = ts.get('fuel_consumption', {}) if ts else {}
        fuel_types_station = [k for k, v in station_fuels.items() if v > 0]
        fuel_consumed_station = [v for k, v in station_fuels.items() if v > 0]

        emissions_service = TransportationEmissions(
            waste_formal=request.waste_formal,
            fuel_types_transport=fuel_types_transport,
            fuel_consumed_transport=fuel_consumed_transport,
            vehicle_type=vehicle_type,
            waste_transfer_station=waste_transfer_station,
            fuel_types_station=fuel_types_station,
            fuel_consumed_station=fuel_consumed_station,
            electric_consumed=electric_consumed,
            waste_handled_at_station=waste_handled_at_station
        )

        emissions = emissions_service.overall_emissions()
        return TransportationResponse(**emissions)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
