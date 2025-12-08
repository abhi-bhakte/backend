from fastapi import APIRouter, HTTPException
from app.models.input_models.transportation_data import TransportationData, TransportationResponse
from app.services.transportation import TransportationEmissions

# Create a FastAPI router instance
router = APIRouter()


@router.post("/calculate", response_model=TransportationResponse)
def calculate_transportation_emissions(request: TransportationData):
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
        # ---------- Input extraction ----------
        wc = request.waste_collection
        ts = request.transfer_station

        # Waste collection
        vehicle_type = wc.vehicle_type if hasattr(wc, 'vehicle_type') else (wc.get('vehicle_type', '') if isinstance(wc, dict) else '')
        waste_formal_val = wc.waste_formal if hasattr(wc, 'waste_formal') else (wc.get('waste_formal', 0) if isinstance(wc, dict) else 0)
        wc_fuels = wc.fuel_consumption.dict() if hasattr(wc, 'fuel_consumption') and hasattr(wc.fuel_consumption, 'dict') else (wc.get('fuel_consumption', {}) if isinstance(wc, dict) else {})
        fuel_types_transport = [k for k, v in wc_fuels.items() if v and v > 0]
        fuel_consumed_transport = [float(v) for k, v in wc_fuels.items() if v and v > 0]

        # Transfer station
        waste_transfer_station = ts is not None
        waste_handled_at_station = (ts.waste_handled_tpd if hasattr(ts, 'waste_handled_tpd') else (ts.get('waste_handled_tpd', 0) if isinstance(ts, dict) else 0))
        electric_consumed = (ts.electricity_kwh_per_day if hasattr(ts, 'electricity_kwh_per_day') else (ts.get('electricity_kwh_per_day', 0) if isinstance(ts, dict) else 0))
        ts_fuels = ts.fuel_consumption.dict() if (ts is not None and hasattr(ts, 'fuel_consumption') and hasattr(ts.fuel_consumption, 'dict')) else (ts.get('fuel_consumption', {}) if isinstance(ts, dict) else {})
        fuel_types_station = [k for k, v in ts_fuels.items() if v and v > 0]
        fuel_consumed_station = [float(v) for k, v in ts_fuels.items() if v and v > 0]

        emissions_service = TransportationEmissions(
            waste_formal=waste_formal_val,
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
