# Reference data services
from app.models.database_models.reference_data import ProcessType, ParameterType, Unit, ActivityBasis, City
from typing import List, Optional
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime

async def create_reference_item(collection_name: str, item_dict: dict, db: AsyncIOMotorDatabase) -> str:
    """Create a new reference data item with duplicate check"""
    # Check for case-insensitive duplicate
    existing = await db.database[collection_name].find_one({
        "name": {"$regex": f"^{item_dict['name']}$", "$options": "i"}
    })
    if existing:
        raise ValueError(f"Entry '{item_dict['name']}' already exists")
    
    item_dict['_id'] = str(ObjectId())
    item_dict['createdAt'] = datetime.utcnow().isoformat()
    item_dict['isActive'] = True
    result = await db.database[collection_name].insert_one(item_dict)
    return str(result.inserted_id)

async def get_reference_items(collection_name: str, db: AsyncIOMotorDatabase, active_only: bool = True) -> list:
    """Fetch all reference data items"""
    query = {"isActive": True} if active_only else {}
    items = []
    cursor = db.database[collection_name].find(query).sort("name", 1)
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        items.append(doc)
    return items

async def update_reference_item(collection_name: str, item_id: str, update_dict: dict, db: AsyncIOMotorDatabase) -> bool:
    """Update a reference data item"""
    # Check for case-insensitive duplicate (excluding self)
    if 'name' in update_dict:
        existing = await db.database[collection_name].find_one({
            "_id": {"$ne": item_id},
            "name": {"$regex": f"^{update_dict['name']}$", "$options": "i"}
        })
        if existing:
            raise ValueError(f"Entry '{update_dict['name']}' already exists")
    
    update_dict['updatedAt'] = datetime.utcnow().isoformat()
    result = await db.database[collection_name].update_one(
        {"_id": item_id},
        {"$set": update_dict}
    )
    return result.modified_count == 1

async def delete_reference_item(collection_name: str, item_id: str, db: AsyncIOMotorDatabase) -> bool:
    """Soft delete (mark as inactive) a reference data item"""
    result = await db.database[collection_name].update_one(
        {"_id": item_id},
        {"$set": {"isActive": False, "updatedAt": datetime.utcnow().isoformat()}}
    )
    return result.modified_count == 1

async def search_reference_items(collection_name: str, search_term: str, db: AsyncIOMotorDatabase) -> list:
    """Search reference data items by name"""
    items = []
    cursor = db.database[collection_name].find({
        "name": {"$regex": search_term, "$options": "i"},
        "isActive": True
    }).sort("name", 1).limit(20)
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        items.append(doc)
    return items
