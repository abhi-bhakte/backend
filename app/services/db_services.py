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

async def get_dbs(db: AsyncIOMotorDatabase, query: dict = None) -> list:
    dbs = []
    if query is None:
        query = {}
    cursor = db.database.find(query)
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
    from bson import ObjectId
    # Try ObjectId first
    try:
        obj_id = ObjectId(db_id)
        result = await db.database.update_one({"_id": obj_id}, {"$set": update_dict})
        if result.modified_count == 1:
            return True
    except Exception:
        pass
    # Try string _id
    result = await db.database.update_one({"_id": db_id}, {"$set": update_dict})
    return result.modified_count == 1

async def delete_db(db_id: str, db: AsyncIOMotorDatabase) -> bool:
    from bson import ObjectId
    try:
        obj_id = ObjectId(db_id)
        result = await db.database.delete_one({"_id": obj_id})
        if result.deleted_count == 1:
            return True
    except Exception:
        pass
    result = await db.database.delete_one({"_id": db_id})
    return result.deleted_count == 1
