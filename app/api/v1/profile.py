
from fastapi import APIRouter, HTTPException, Depends
from app.db.db import get_db
from app.models.user_profile import UserProfile
from bson import ObjectId
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/profile-data", tags=["Profile"])
COLLECTION_NAME = "user_profiles"

@router.post("/", summary="Create or update user profile")
async def create_or_update_profile(profile: UserProfile, db=Depends(get_db), current_user=Depends(get_current_user)):
    profile.user_id = str(current_user["_id"])
    result = await db[COLLECTION_NAME].update_one(
        {"user_id": profile.user_id},
        {
            "$set": profile.dict(),
            "$unset": {"energyInputs": ""}  # Remove old top-level energyInputs
        },
        upsert=True
    )
    # Fetch the profile to get the MongoDB _id
    saved_profile = await db[COLLECTION_NAME].find_one({"user_id": profile.user_id})
    return {"message": "Profile saved", "user_id": profile.user_id, "profile_id": str(saved_profile["_id"]) if saved_profile and "_id" in saved_profile else None}

@router.get("/", summary="Get current user profile")
async def get_profile(db=Depends(get_db), current_user=Depends(get_current_user)):
    user_id = str(current_user["_id"])
    profile = await db[COLLECTION_NAME].find_one({"user_id": user_id})
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    profile["profile_id"] = str(profile["_id"])
    profile.pop("_id", None)
    return profile

@router.get("/by-user/{user_id}", summary="Get profile by user ID")
async def get_profile_by_user(user_id: str, db=Depends(get_db)):
    profile = await db[COLLECTION_NAME].find_one({"user_id": user_id})
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    profile["profile_id"] = str(profile["_id"])
    profile.pop("_id", None)
    return profile

# New endpoint: GET /latest for frontend fetch
@router.get("/latest", summary="Get latest profile for current user")
async def get_latest_profile(db=Depends(get_db), current_user=Depends(get_current_user)):
    user_id = str(current_user["_id"])
    profile = await db[COLLECTION_NAME].find_one({"user_id": user_id})
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    profile["profile_id"] = str(profile["_id"])
    profile.pop("_id", None)
    return profile

# New endpoint: PATCH /{profileId} for frontend update
@router.patch("/{profile_id}", summary="Update profile by profile ID")
async def update_profile_by_id(profile_id: str, profile: UserProfile, db=Depends(get_db), current_user=Depends(get_current_user)):
    user_id = str(current_user["_id"])
    result = await db[COLLECTION_NAME].update_one(
        {"_id": ObjectId(profile_id), "user_id": user_id},
        {
            "$set": profile.dict(),
            "$unset": {"energyInputs": ""}  # Remove old top-level energyInputs
        }
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Profile not found or not authorized")
    updated_profile = await db[COLLECTION_NAME].find_one({"_id": ObjectId(profile_id)})
    updated_profile["profile_id"] = str(updated_profile["_id"])
    updated_profile.pop("_id", None)
    return updated_profile
