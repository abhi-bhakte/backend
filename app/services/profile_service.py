from app.models.user_profile import UserProfile
from app.db.db import get_db
from typing import Optional

COLLECTION_NAME = "user_profiles"

async def save_profile(profile: UserProfile, db):
    result = await db[COLLECTION_NAME].update_one(
        {"user_id": profile.user_id},
        {"$set": profile.dict()},
        upsert=True
    )
    return result

async def get_profile(user_id: str, db) -> Optional[UserProfile]:
    data = await db[COLLECTION_NAME].find_one({"user_id": user_id})
    if data:
        return UserProfile(**data)
    return None
