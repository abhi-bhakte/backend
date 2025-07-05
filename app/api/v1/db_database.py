# Renamed from emissions_database.py to db_database.py
from fastapi import APIRouter, HTTPException, Depends
from app.models.database_models.db_database import Db
from app.services.db_services import (
    create_db, get_dbs, get_db_by_id,
    update_db, delete_db
)
from app.db.db import get_db
from motor.motor_asyncio import AsyncIOMotorDatabase

router = APIRouter()

@router.post("/dbs/", response_model=dict)
async def add_db(db: Db, database: AsyncIOMotorDatabase = Depends(get_db)):
    db_id = await create_db(db, database)
    return {"id": db_id, "message": "DB data added successfully"}

@router.get("/dbs/", response_model=list)
async def fetch_dbs(database: AsyncIOMotorDatabase = Depends(get_db)):
    return await get_dbs(database)

@router.get("/dbs/{db_id}", response_model=dict)
async def fetch_db(db_id: str, database: AsyncIOMotorDatabase = Depends(get_db)):
    doc = await get_db_by_id(db_id, database)
    if not doc:
        raise HTTPException(status_code=404, detail="DB not found")
    return doc

@router.put("/dbs/{db_id}", response_model=dict)
async def update_db_api(db_id: str, db: Db, database: AsyncIOMotorDatabase = Depends(get_db)):
    updated = await update_db(db_id, db, database)
    if not updated:
        raise HTTPException(status_code=404, detail="DB not found or not updated")
    return {"message": "DB updated successfully"}

@router.delete("/dbs/{db_id}", response_model=dict)
async def delete_db_api(db_id: str, database: AsyncIOMotorDatabase = Depends(get_db)):
    deleted = await delete_db(db_id, database)
    if not deleted:
        raise HTTPException(status_code=404, detail="DB not found or not deleted")
    return {"message": "DB deleted successfully"}
