# app/db.py

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.config import settings
import asyncio

client: AsyncIOMotorClient = AsyncIOMotorClient(settings.MONGO_URL)

async def connect_to_mongodb():
    try:
        await client.server_info()  # Forces connection and raises error if fails
        print("✅ MongoDB connection established")
    except Exception as e:
        print("❌ MongoDB connection failed:", e)

def get_db() -> AsyncIOMotorDatabase:
    return client[settings.MONGO_DB_NAME]
