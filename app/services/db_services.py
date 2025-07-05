# Renamed from emission_services.py to db_services.py
from app.models.database_models.db_database import Db
from typing import List, Optional
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

async def create_db(db_obj: Db, db: AsyncIOMotorDatabase) -> str:
    db_dict = db_obj.dict()
    if '_id' not in db_dict or not db_dict['_id']:
        db_dict['_id'] = str(ObjectId())
    result = await db.database.insert_one(db_dict)
    return str(result.inserted_id)

async def get_dbs(db: AsyncIOMotorDatabase) -> list:
    dbs = []
    cursor = db.database.find({})
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        dbs.append(doc)
    return dbs

async def get_db_by_id(db_id: str, db: AsyncIOMotorDatabase) -> Optional[dict]:
    doc = await db.database.find_one({"_id": ObjectId(db_id)})
    if doc:
        doc["_id"] = str(doc["_id"])
    return doc

async def update_db(db_id: str, db_obj: Db, db: AsyncIOMotorDatabase) -> bool:
    update_dict = db_obj.dict()
    # Remove id and _id fields if present
    update_dict.pop('id', None)
    update_dict.pop('_id', None)
    result = await db.database.update_one(
        {"_id": ObjectId(db_id)},
        {"$set": update_dict}
    )
    return result.modified_count == 1

async def delete_db(db_id: str, db: AsyncIOMotorDatabase) -> bool:
    result = await db.database.delete_one({"_id": ObjectId(db_id)})
    return result.deleted_count == 1
