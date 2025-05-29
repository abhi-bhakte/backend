from fastapi import APIRouter, HTTPException
from app.models.results_models.landfill import LandfillRequest, LandfillResponse
from app.services.landfill import LandfillEmissions

# Create a FastAPI router instance
router = APIRouter()


@router.post("/calculate", response_model=LandfillResponse)
def calculate_landfill_emissions(request: LandfillRequest):
    """
    API endpoint to compute GHG emissions for landfill operations.
    
    Args:
        request (LandfillRequest): Input data containing landfill and fuel usage details.
    
    Returns:
        LandfillResponse: Calculated emissions data.
    
    Raises:
        HTTPException: If an invalid input value is provided.
    """
    try:
        # Initialize the LandfillEmissions service with request parameters
        emissions_service = LandfillEmissions(
            waste_disposed=request.waste_disposed,
            waste_disposed_fired=request.waste_disposed_fired,
            landfill_type=request.landfill_type,
            start_year=request.start_year,
            end_year=request.end_year,
            current_year=request.current_year,
            annual_growth_rate=request.annual_growth_rate,
            fossil_fuel_type=request.fossil_fuel_type,
            fossil_fuel_consumption=request.fossil_fuel_consumption,
            grid_electricity=request.grid_electricity,
            gas_collection_efficiency=request.gas_collection_efficiency,
            gas_treatment_method=request.gas_treatment_method,
            lfg_utilization_efficiency=request.lfg_utilization_efficiency,
            gas_recovery_start_year=request.gas_recovery_start_year,
            gas_recovery_end_year=request.gas_recovery_end_year,
            replaced_fossil_fuel_type=request.replaced_fossil_fuel_type,
        )

        # Compute overall emissions
        emissions = emissions_service.overall_emissions()

        # Return the computed emissions as a response
        return LandfillResponse(**emissions)

    except ValueError as e:
        # Handle invalid input values and return an HTTP 400 error
        raise HTTPException(status_code=400, detail=str(e))