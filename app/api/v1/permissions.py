from typing import List, Literal, Optional
from fastapi import APIRouter, Depends, HTTPException
from app.db.db import get_db
from app.models.permissions import PermissionModel, PyObjectId
from pydantic import BaseModel, Field
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

router = APIRouter()

ModuleNames = Literal["dashboard","database", "comparison", "guide", "ghg_emissions", "profile"]
PermissionType = Literal["read", "write", "update", "delete", "audit", "all"]

# --- Schemas ---
class SetPermissionRequest(BaseModel):
    user_id: str = Field(..., description="MongoDB ObjectId as string")
    module: ModuleNames
    permissions: List[PermissionType]

class PermissionResponse(BaseModel):
    user_id: str
    module: Optional[str] = None
    permissions: Optional[List[str]] = None
    all_permissions: Optional[dict] = None


# --- Set Permissions ---
@router.post("/permissions", response_model=PermissionResponse)
async def set_permissions(
    request: SetPermissionRequest,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    

    try:
        user_oid = ObjectId(request.user_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid user_id format")

    user = await db["users"].find_one({"_id": user_oid})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    await db["permissions"].update_one(
        {"user_id": user_oid},
        {"$set": {f"modules.{request.module}": request.permissions}},
        upsert=True
    )

    return PermissionResponse(
        user_id=request.user_id,
        module=request.module,
        permissions=request.permissions
    )


# --- Get Permissions ---
@router.get("/permissions", response_model=PermissionResponse)
async def get_permissions(
    user_id: str,
    module: Optional[str] = None,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    try:
        user_oid = ObjectId(user_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid user_id format")

    perm_doc = await db["permissions"].find_one({"user_id": user_oid})
    if not perm_doc:
        raise HTTPException(status_code=404, detail="Permissions not found")

    if module:
        perms = perm_doc.get("modules", {}).get(module, [])
        return PermissionResponse(user_id=user_id, module=module, permissions=perms)
    else:
        all_perms = perm_doc.get("modules", {})
        return PermissionResponse(user_id=user_id, all_permissions=all_perms)
