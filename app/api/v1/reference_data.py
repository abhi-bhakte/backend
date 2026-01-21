# API endpoints for reference data management
from fastapi import APIRouter, HTTPException, Depends
from app.models.database_models.reference_data import ProcessType, ParameterType, Unit, ActivityBasis, City
from app.services.reference_data_service import (
    create_reference_item, get_reference_items, update_reference_item,
    delete_reference_item, search_reference_items
)
from app.db.db import get_db
from app.utils.dependencies import get_current_user
from motor.motor_asyncio import AsyncIOMotorDatabase

router = APIRouter()

# Helper to check if user is superadmin
async def check_superadmin(current_user = Depends(get_current_user)):
    if current_user.get("role") != "superadmin":
        raise HTTPException(status_code=403, detail="Only superadmin can manage reference data")
    return current_user

# ===== PROCESS TYPES =====
@router.get("/reference-data/process-types", response_model=list)
async def get_process_types(database: AsyncIOMotorDatabase = Depends(get_db)):
    return await get_reference_items("process_types", database)

@router.post("/reference-data/process-types", response_model=dict)
async def add_process_type(
    item: ProcessType,
    database: AsyncIOMotorDatabase = Depends(get_db),
    current_user = Depends(check_superadmin)
):
    try:
        item_dict = item.dict()
        item_dict['createdBy'] = current_user.get('name', '')
        item_dict['updatedBy'] = current_user.get('name', '')
        item_id = await create_reference_item("process_types", item_dict, database)
        return {"id": item_id, "message": "Process type added successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/reference-data/process-types/{item_id}", response_model=dict)
async def update_process_type(
    item_id: str,
    item: ProcessType,
    database: AsyncIOMotorDatabase = Depends(get_db),
    current_user = Depends(check_superadmin)
):
    try:
        item_dict = item.dict()
        item_dict['updatedBy'] = current_user.get('name', '')
        success = await update_reference_item("process_types", item_id, item_dict, database)
        if not success:
            raise HTTPException(status_code=404, detail="Process type not found")
        return {"message": "Process type updated successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/reference-data/process-types/{item_id}", response_model=dict)
async def delete_process_type(
    item_id: str,
    database: AsyncIOMotorDatabase = Depends(get_db),
    current_user = Depends(check_superadmin)
):
    success = await delete_reference_item("process_types", item_id, database)
    if not success:
        raise HTTPException(status_code=404, detail="Process type not found")
    return {"message": "Process type deleted successfully"}

# ===== PARAMETER TYPES =====
@router.get("/reference-data/parameter-types", response_model=list)
async def get_parameter_types(database: AsyncIOMotorDatabase = Depends(get_db)):
    return await get_reference_items("parameter_types", database)

@router.post("/reference-data/parameter-types", response_model=dict)
async def add_parameter_type(
    item: ParameterType,
    database: AsyncIOMotorDatabase = Depends(get_db),
    current_user = Depends(check_superadmin)
):
    try:
        item_dict = item.dict()
        item_dict['createdBy'] = current_user.get('name', '')
        item_dict['updatedBy'] = current_user.get('name', '')
        item_id = await create_reference_item("parameter_types", item_dict, database)
        return {"id": item_id, "message": "Parameter type added successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/reference-data/parameter-types/{item_id}", response_model=dict)
async def update_parameter_type(
    item_id: str,
    item: ParameterType,
    database: AsyncIOMotorDatabase = Depends(get_db),
    current_user = Depends(check_superadmin)
):
    try:
        item_dict = item.dict()
        item_dict['updatedBy'] = current_user.get('name', '')
        success = await update_reference_item("parameter_types", item_id, item_dict, database)
        if not success:
            raise HTTPException(status_code=404, detail="Parameter type not found")
        return {"message": "Parameter type updated successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/reference-data/parameter-types/{item_id}", response_model=dict)
async def delete_parameter_type(
    item_id: str,
    database: AsyncIOMotorDatabase = Depends(get_db),
    current_user = Depends(check_superadmin)
):
    success = await delete_reference_item("parameter_types", item_id, database)
    if not success:
        raise HTTPException(status_code=404, detail="Parameter type not found")
    return {"message": "Parameter type deleted successfully"}

# ===== UNITS =====
@router.get("/reference-data/units", response_model=list)
async def get_units(database: AsyncIOMotorDatabase = Depends(get_db)):
    return await get_reference_items("units", database)

@router.post("/reference-data/units", response_model=dict)
async def add_unit(
    item: Unit,
    database: AsyncIOMotorDatabase = Depends(get_db),
    current_user = Depends(check_superadmin)
):
    try:
        item_dict = item.dict()
        item_dict['createdBy'] = current_user.get('name', '')
        item_dict['updatedBy'] = current_user.get('name', '')
        item_id = await create_reference_item("units", item_dict, database)
        return {"id": item_id, "message": "Unit added successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/reference-data/units/{item_id}", response_model=dict)
async def update_unit(
    item_id: str,
    item: Unit,
    database: AsyncIOMotorDatabase = Depends(get_db),
    current_user = Depends(check_superadmin)
):
    try:
        item_dict = item.dict()
        item_dict['updatedBy'] = current_user.get('name', '')
        success = await update_reference_item("units", item_id, item_dict, database)
        if not success:
            raise HTTPException(status_code=404, detail="Unit not found")
        return {"message": "Unit updated successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/reference-data/units/{item_id}", response_model=dict)
async def delete_unit(
    item_id: str,
    database: AsyncIOMotorDatabase = Depends(get_db),
    current_user = Depends(check_superadmin)
):
    success = await delete_reference_item("units", item_id, database)
    if not success:
        raise HTTPException(status_code=404, detail="Unit not found")
    return {"message": "Unit deleted successfully"}

# ===== ACTIVITY BASIS =====
@router.get("/reference-data/activity-basis", response_model=list)
async def get_activity_basis(database: AsyncIOMotorDatabase = Depends(get_db)):
    return await get_reference_items("activity_basis", database)

@router.post("/reference-data/activity-basis", response_model=dict)
async def add_activity_basis(
    item: ActivityBasis,
    database: AsyncIOMotorDatabase = Depends(get_db),
    current_user = Depends(check_superadmin)
):
    try:
        item_dict = item.dict()
        item_dict['createdBy'] = current_user.get('name', '')
        item_dict['updatedBy'] = current_user.get('name', '')
        item_id = await create_reference_item("activity_basis", item_dict, database)
        return {"id": item_id, "message": "Activity basis added successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/reference-data/activity-basis/{item_id}", response_model=dict)
async def update_activity_basis(
    item_id: str,
    item: ActivityBasis,
    database: AsyncIOMotorDatabase = Depends(get_db),
    current_user = Depends(check_superadmin)
):
    try:
        item_dict = item.dict()
        item_dict['updatedBy'] = current_user.get('name', '')
        success = await update_reference_item("activity_basis", item_id, item_dict, database)
        if not success:
            raise HTTPException(status_code=404, detail="Activity basis not found")
        return {"message": "Activity basis updated successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/reference-data/activity-basis/{item_id}", response_model=dict)
async def delete_activity_basis(
    item_id: str,
    database: AsyncIOMotorDatabase = Depends(get_db),
    current_user = Depends(check_superadmin)
):
    success = await delete_reference_item("activity_basis", item_id, database)
    if not success:
        raise HTTPException(status_code=404, detail="Activity basis not found")
    return {"message": "Activity basis deleted successfully"}

# ===== CITIES =====
@router.get("/reference-data/cities", response_model=list)
async def get_cities(database: AsyncIOMotorDatabase = Depends(get_db)):
    return await get_reference_items("cities", database)

@router.post("/reference-data/cities", response_model=dict)
async def add_city(
    item: City,
    database: AsyncIOMotorDatabase = Depends(get_db),
    current_user = Depends(check_superadmin)
):
    try:
        item_dict = item.dict()
        item_dict['createdBy'] = current_user.get('name', '')
        item_dict['updatedBy'] = current_user.get('name', '')
        item_id = await create_reference_item("cities", item_dict, database)
        return {"id": item_id, "message": "City added successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/reference-data/cities/{item_id}", response_model=dict)
async def update_city(
    item_id: str,
    item: City,
    database: AsyncIOMotorDatabase = Depends(get_db),
    current_user = Depends(check_superadmin)
):
    try:
        item_dict = item.dict()
        item_dict['updatedBy'] = current_user.get('name', '')
        success = await update_reference_item("cities", item_id, item_dict, database)
        if not success:
            raise HTTPException(status_code=404, detail="City not found")
        return {"message": "City updated successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/reference-data/cities/{item_id}", response_model=dict)
async def delete_city(
    item_id: str,
    database: AsyncIOMotorDatabase = Depends(get_db),
    current_user = Depends(check_superadmin)
):
    success = await delete_reference_item("cities", item_id, database)
    if not success:
        raise HTTPException(status_code=404, detail="City not found")
    return {"message": "City deleted successfully"}
