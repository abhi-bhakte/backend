"""
Service functions for CRUD operations on the emissions collection in MongoDB.
"""

from app.models.database_models.emission_database import Emission
from typing import List, Optional
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

async def create_emission(emission: Emission, db: AsyncIOMotorDatabase) -> str:
    """
    Insert a new emission record into the database.

    Args:
        emission (Emission): The emission data to insert.
        db (AsyncIOMotorDatabase): The database connection.

    Returns:
        str: The inserted document's ID as a string.
    """
    result = await db.emissions.insert_one(emission.dict())
    return str(result.inserted_id)

async def get_emissions(db: AsyncIOMotorDatabase) -> list:
    """
    Retrieve all emission records from the database.

    Args:
        db (AsyncIOMotorDatabase): The database connection.

    Returns:
        list: A list of emission documents.
    """
    emissions = []
    cursor = db.emissions.find({})
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])  # Convert ObjectId to string for JSON serialization
        emissions.append(doc)
    return emissions

async def get_emission_by_id(emission_id: str, db: AsyncIOMotorDatabase) -> Optional[dict]:
    """
    Retrieve a single emission record by its ID.

    Args:
        emission_id (str): The ID of the emission document.
        db (AsyncIOMotorDatabase): The database connection.

    Returns:
        Optional[dict]: The emission document if found, else None.
    """
    doc = await db.emissions.find_one({"_id": ObjectId(emission_id)})
    if doc:
        doc["_id"] = str(doc["_id"])
    return doc

async def update_emission(emission_id: str, emission: Emission, db: AsyncIOMotorDatabase) -> bool:
    """
    Update an existing emission record by its ID.

    Args:
        emission_id (str): The ID of the emission document to update.
        emission (Emission): The new emission data.
        db (AsyncIOMotorDatabase): The database connection.

    Returns:
        bool: True if the document was updated, False otherwise.
    """
    result = await db.emissions.update_one(
        {"_id": ObjectId(emission_id)},
        {"$set": emission.dict()}
    )
    return result.modified_count == 1

async def delete_emission(emission_id: str, db: AsyncIOMotorDatabase) -> bool:
    """
    Delete an emission record by its ID.

    Args:
        emission_id (str): The ID of the emission document to delete.
        db (AsyncIOMotorDatabase): The database connection.

    Returns:
        bool: True if the document was deleted, False otherwise.
    """
    result = await db.emissions.delete_one({"_id": ObjectId(emission_id)})
    return result.deleted_count == 1