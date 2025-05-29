"""
API router for Emission database endpoints in the GHG Accounting API.

This module defines the HTTP endpoints for CRUD operations on emission records.
"""

from fastapi import APIRouter, HTTPException
from app.models.database_models.emission_database import Emission
from app.services.emission_services import (
    create_emission, get_emissions, get_emission_by_id,
    update_emission, delete_emission
)

router = APIRouter()


@router.post("/emissions/", response_model=dict)
async def add_emission(emission: Emission):
    """
    Create a new emission record.

    Args:
        emission (Emission): The emission data to insert.

    Returns:
        dict: The inserted document's ID and a success message.
    """
    emission_id = await create_emission(emission)
    return {"id": emission_id, "message": "Emission data added successfully"}


@router.get("/emissions/", response_model=list)
async def fetch_emissions():
    """
    Retrieve all emission records.

    Returns:
        list: A list of emission documents.
    """
    return await get_emissions()


@router.get("/emissions/{emission_id}", response_model=dict)
async def fetch_emission(emission_id: str):
    """
    Retrieve a single emission record by its ID.

    Args:
        emission_id (str): The ID of the emission document.

    Returns:
        dict: The emission document if found.

    Raises:
        HTTPException: If the emission is not found.
    """
    doc = await get_emission_by_id(emission_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Emission not found")
    return doc


@router.put("/emissions/{emission_id}", response_model=dict)
async def update_emission_api(emission_id: str, emission: Emission):
    """
    Update an existing emission record by its ID.

    Args:
        emission_id (str): The ID of the emission document to update.
        emission (Emission): The new emission data.

    Returns:
        dict: Success message if updated.

    Raises:
        HTTPException: If the emission is not found or not updated.
    """
    updated = await update_emission(emission_id, emission)
    if not updated:
        raise HTTPException(status_code=404, detail="Emission not found or not updated")
    return {"message": "Emission updated successfully"}


@router.delete("/emissions/{emission_id}", response_model=dict)
async def delete_emission_api(emission_id: str):
    """
    Delete an emission record by its ID.

    Args:
        emission_id (str): The ID of the emission document to delete.

    Returns:
        dict: Success message if deleted.

    Raises:
        HTTPException: If the emission is not found or not deleted.
    """
    deleted = await delete_emission(emission_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Emission not found or not deleted")
    return {"message": "Emission deleted successfully"}