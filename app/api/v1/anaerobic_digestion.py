from fastapi import APIRouter, HTTPException
from typing import List
from app.models.input_models.anaerobic_digestion_data import (
    AnaerobicDigestionData,
)
from app.models.results_models.anaerobic_digestion import (
    AnaerobicDigestionResponse,
)
from app.services.anaerobic_digestion import AnaerobicDigestionEmissions

# Create a FastAPI router instance
router = APIRouter()


@router.post("/calculate", response_model=AnaerobicDigestionResponse)
def calculate_anaerobic_digestion_emissions(request: AnaerobicDigestionData):
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
        # Initialize the AnaerobicDigestionEmissions service with compact request parameters
        fuel_types_operation: List[str] = []
        fuel_consumed_operation: List[float] = []
        if request.fuel_consumption:
            for fuel_key in ["petrol", "diesel", "cng"]:
                amount = getattr(request.fuel_consumption, fuel_key, None)
                if amount is not None and amount > 0:
                    fuel_types_operation.append(fuel_key)
                    fuel_consumed_operation.append(float(amount))

        emissions_service = AnaerobicDigestionEmissions(
            waste_digested=request.waste_digested,
            ad_energy_product=request.energy_and_compost.ad_energy_product or "",
            fuel_replaced=request.energy_and_compost.fuel_replaced or "",
            compost_recovered=bool(request.energy_and_compost.compost_recovered),
            percent_compost_use_agri_garden=float(request.energy_and_compost.compost_recovery_percent or 0),
            electricity_consumed=float(request.electricity_kwh_per_day),
            fuel_types_operation=fuel_types_operation,
            fuel_consumed_operation=fuel_consumed_operation,
        )

        # Compute overall emissions
        emissions = emissions_service.overall_emissions()

        # Return the computed emissions as a response
        return AnaerobicDigestionResponse(**emissions)

    except ValueError as e:
        # Handle invalid input values and return an HTTP 400 error
        raise HTTPException(status_code=400, detail=str(e))