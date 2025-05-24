import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from datetime import datetime
import os
from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# MongoDB configuration
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = "gacalc"

client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]
users_collection = db["users"]
permissions_collection = db["permissions"]


async def hash_password(password: str) -> str:
      return pwd_context.hash(password)

async def create_user(email: str, name: str, password: str):
    existing = await users_collection.find_one({"email": email})
    if existing:
        print(f"User with email {email} already exists.")
        return existing["_id"]

    hashed_pw = await hash_password(password)
    user = {
        "email": email,
        "name": name,
        "password": hashed_pw,
        "created_at": datetime.utcnow()
    }
    result = await users_collection.insert_one(user)
    print(f" User created with ID: {result.inserted_id}")
    return result.inserted_id


async def assign_permissions(user_id: str, module_perms: dict):
    # Example module_perms = {"dashboard": ["read"], "database": ["read", "write"]}
    user_obj_id = ObjectId(user_id)

    await permissions_collection.update_one(
        {"user_id": user_obj_id},
        {"$set": {"all_permissions": module_perms}},
        upsert=True
    )
    print(f" Permissions assigned to user {user_id}: {module_perms}")


async def main():
    email = "admin@greenaadhaar.in"
    name = "Admin"
    password = "admin123"

    # Create user
    user_id = await create_user(email, name, password)

    # Assign permissions
    permissions = {
        "dashboard": ["read", "write"],
        "database": ["read"],
        "profile": ["read", "write"],
        "emissions": ["read", "write"],
    }
    await assign_permissions(user_id, permissions)

    print("User setup complete!")


if __name__ == "__main__":
    asyncio.run(main())
