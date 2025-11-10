from fastapi import APIRouter, HTTPException
from typing import List
from app.models.results_models.composting import CompostingResponse
from app.models.input_models.composting_data import CompostingData
from app.services.composting import CompostingEmissions

# Create a FastAPI router instance
router = APIRouter()


@router.post("/calculate", response_model=CompostingResponse)
def calculate_composting_emissions(request: CompostingData):
    """
    API endpoint to compute GHG emissions for composting.
    
    Args:
        request (CompostingData): Input data containing waste and fuel usage details.
    
    Returns:
        CompostingResponse: Calculated emissions data.
    
    Raises:
        HTTPException: If an invalid input value is provided.
    """
    try:
        # Map compact k/v fuel map to arrays expected by the service
        fuel_types: List[str] = []
        fuel_amounts: List[float] = []
        if request.fuel_consumption:
            for key in ["petrol", "diesel", "cng"]:
                val = getattr(request.fuel_consumption, key, None)
                if val is not None and val > 0:
                    fuel_types.append(key)
                    fuel_amounts.append(float(val))

        emissions_service = CompostingEmissions(
            waste_composted=request.waste_composted,
            percent_compost_use_agri_garden=request.compost_usage_percent,
            compost_prod_potential=request.compost_production_kg_per_tonne,
            electricity_consumed=request.electricity_kwh_per_day,
            fuel_types_operation=fuel_types,
            fuel_consumed_operation=fuel_amounts,
        )

        # Compute overall emissions
        emissions = emissions_service.overall_emissions()

        # Return the computed emissions as a response
        return CompostingResponse(**emissions)

    except ValueError as e:
        # Handle invalid input values and return an HTTP 400 error
        raise HTTPException(status_code=400, detail=str(e))
