from fastapi import APIRouter, HTTPException
from app.models.input_models.landfill_data import LandfillData, LandfillResponse
from app.services.landfill import LandfillEmissions

# Create a FastAPI router instance
router = APIRouter()


@router.post("/calculate", response_model=LandfillResponse)
def calculate_landfill_emissions(request: LandfillData):
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
        # Map new LandfillData model to LandfillEmissions arguments
        emissions_service = LandfillEmissions(
            waste_disposed=request.waste_disposed,
            waste_disposed_fired=(request.landfill_operation.waste_disposed_fired if request.landfill_operation and request.landfill_operation.waste_disposed_fired is not None else 0.0),
            landfill_type=(request.landfill_operation.landfill_type if request.landfill_operation and request.landfill_operation.landfill_type is not None else "uncategorized"),
            start_year=(request.landfill_operation.start_year if request.landfill_operation and request.landfill_operation.start_year is not None else 2000),
            end_year=(request.landfill_operation.end_year if request.landfill_operation and request.landfill_operation.end_year is not None else 2025),
            current_year=(request.landfill_operation.current_year if request.landfill_operation and request.landfill_operation.current_year is not None else 2025),
            annual_growth_rate=(request.landfill_operation.annual_growth_rate if request.landfill_operation and request.landfill_operation.annual_growth_rate is not None else 0.0),
            fossil_fuel_types=[k for k, v in request.fuel_consumption.dict().items() if v is not None and v > 0],
            fossil_fuel_consumed=[v for v in request.fuel_consumption.dict().values() if v is not None and v > 0],
            electricity_kwh_per_day=request.electricity_kwh_per_day,
            gas_collection_efficiency=(request.landfill_gas_recovery.gas_collection_efficiency if request.landfill_gas_recovery and request.landfill_gas_recovery.gas_collection_efficiency is not None else 0.0),
            gas_treatment_method=(request.landfill_gas_recovery.gas_treatment_method if request.landfill_gas_recovery and request.landfill_gas_recovery.gas_treatment_method is not None else None),
            lfg_utilization_efficiency=(request.landfill_gas_recovery.lfg_utilization_efficiency if request.landfill_gas_recovery and request.landfill_gas_recovery.lfg_utilization_efficiency is not None else 0.0),
            gas_recovery_start_year=(request.landfill_gas_recovery.gas_recovery_start_year if request.landfill_gas_recovery and request.landfill_gas_recovery.gas_recovery_start_year is not None else None),
            gas_recovery_end_year=(request.landfill_gas_recovery.gas_recovery_end_year if request.landfill_gas_recovery and request.landfill_gas_recovery.gas_recovery_end_year is not None else None),
            replaced_fossil_fuel_type=(request.landfill_gas_recovery.fossil_fuel_replaced if request.landfill_gas_recovery and request.landfill_gas_recovery.fossil_fuel_replaced is not None else None),
            mix_waste_composition=None,  # Add if you support this in the input
        )

        emissions = emissions_service.overall_emissions()
        return LandfillResponse(**emissions)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))