
import logging
from fastapi import APIRouter, HTTPException, Depends, Body, status, Request
from app.models.input_models.waste_data import WasteData
from app.db.db import get_db
from bson import ObjectId
from app.utils.dependencies import get_current_user  # <-- import the dependency

router = APIRouter(prefix="/waste-data", tags=["Waste Data"])

COLLECTION_NAME = "waste_data"


@router.post("/", summary="Submit city waste data")
async def submit_waste_data(
    request: Request,
    db=Depends(get_db),
    current_user=Depends(get_current_user)
):
    try:
        payload = await request.json()
        logging.info(f"Incoming waste data payload: {payload}")
        data = WasteData(**payload)
    except Exception as e:
        logging.error(f"Validation or parsing error: {e}")
        return {"error": str(e), "payload": payload if 'payload' in locals() else None}
    data.user_id = str(current_user["_id"])
    result = await db[COLLECTION_NAME].insert_one(data.dict())
    return {"message": "Waste data submitted", "id": str(result.inserted_id)}

@router.get("/", summary="Get all city waste data")
async def get_all_waste_data(db=Depends(get_db), current_user=Depends(get_current_user)):
    # Determine allowed cities for user
    role = current_user.get("role")
    accessible_cities = current_user.get("accessibleCities", [])
    query = {}
    if role == "regular":
        query = {"scenario.city_name": {"$in": accessible_cities}}
    data_list = []
    async for data in db[COLLECTION_NAME].find(query):
        if "_id" in data:
            data["_id"] = str(data["_id"])
        data_list.append(data)
    return data_list

@router.get("/by-city", summary="Get data by city name")
async def get_data_by_city(city_name: str, db=Depends(get_db)):
    data = await db[COLLECTION_NAME].find_one({"city_name": city_name}, {"_id": 0})
    if not data:
        raise HTTPException(status_code=404, detail="City not found")
    return data

@router.get("/by-user")
async def get_by_user(user_id: str, db=Depends(get_db)):
    results = []
    async for doc in db[COLLECTION_NAME].find({"user_id": user_id}, {"_id": 0}):
        results.append(doc)
    return results

@router.get("/by-id")
async def get_by_submission(submission_id: str, db=Depends(get_db)):
    data = await db[COLLECTION_NAME].find_one({"submission_id": submission_id}, {"_id": 0})
    if not data:
        raise HTTPException(status_code=404, detail="Not found")
    return data

@router.get("/by-scenario")
async def get_by_scenario(scenario_name: str, db=Depends(get_db)):
    results = []
    async for doc in db[COLLECTION_NAME].find({"scenario_name": scenario_name}, {"_id": 0}):
        results.append(doc)
    return results

@router.get("/latest-by-scenario")
async def get_latest_by_scenario(scenario_name: str, db=Depends(get_db)):
    data = await db[COLLECTION_NAME].find_one(
        {"scenario_name": scenario_name},
        sort=[("timestamp", -1)],
        projection={"_id": 0}
    )
    if not data:
        raise HTTPException(status_code=404, detail="Not found")
    return data

@router.get("/latest", summary="Get the latest waste data instance")
async def get_latest(db=Depends(get_db)):
    data = await db[COLLECTION_NAME].find_one(
        {},
        sort=[("timestamp", -1)],
        projection={"_id": 0}
    )
    if not data:
        raise HTTPException(status_code=404, detail="Not found")
    return data

@router.patch("/{id}/", summary="Update waste data by MongoDB ObjectId")
async def update_waste_data(id: str, update: dict = Body(...), db=Depends(get_db)):
    result = await db[COLLECTION_NAME].update_one(
        {"_id": ObjectId(id)},
        {"$set": update}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Scenario not found")
    return {"message": "Waste data updated"}

@router.delete("/{id}", summary="Delete waste data by MongoDB ObjectId", status_code=status.HTTP_204_NO_CONTENT)
async def delete_waste_data(id: str, db=Depends(get_db)):
    result = await db[COLLECTION_NAME].delete_one({"_id": ObjectId(id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"message": "Waste data deleted"}

