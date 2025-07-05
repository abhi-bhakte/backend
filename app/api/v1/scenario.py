from fastapi import APIRouter, HTTPException, Depends, Body
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from app.db.db import get_db
from app.utils.dependencies import get_current_user
from datetime import datetime

router = APIRouter(tags=["Scenario"])

COLLECTION_NAME = "waste_data"

class ScenarioSaveRequest(BaseModel):
    name: str = Field(..., description="Scenario name")
    scenario: Dict[str, Any] = Field(..., description="Scenario input data (from ghgPayload)")
    emissions: Dict[str, Any] = Field(..., description="Emissions output data (from emissionsBreakdown)")
    savedAt: Optional[str] = Field(None, description="ISO timestamp")

@router.post("/save", summary="Save scenario input and emissions output")
async def save_scenario(
    req: ScenarioSaveRequest = Body(...),
    db=Depends(get_db),
    current_user=Depends(get_current_user)
):
    doc = {
        "user_id": str(current_user["_id"]),
        "scenario_name": req.name,
        "scenario": req.scenario,
        "emissions": req.emissions,
        "saved_at": req.savedAt or datetime.utcnow().isoformat(),
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
    }
    # Debug print to confirm DB and collection
    result = await db[COLLECTION_NAME].insert_one(doc)
    return {"message": "Scenario saved", "id": str(result.inserted_id)}

@router.get("/by-user", summary="Get all scenarios for current user")
async def get_scenarios_by_user(
    db=Depends(get_db),
    current_user=Depends(get_current_user)
):
    results = []
    async for doc in db[COLLECTION_NAME].find({"user_id": str(current_user["_id"])}):
        doc["id"] = str(doc.pop("_id"))
        results.append(doc)
    return results
