from fastapi import APIRouter, HTTPException, status, Depends, Response, Body, Path
from datetime import datetime, timedelta
from pydantic import BaseModel, EmailStr, Field
from app.db.db import get_db
from app.utils.auth import (
    verify_password,
    create_access_token,
    hash_password  
)
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List
from bson import ObjectId
from fastapi.encoders import jsonable_encoder

router = APIRouter()

LOCK_WINDOW_MINUTES = 10
INITIAL_LOCK_THRESHOLD = 6
FOLLOWUP_LOCK_THRESHOLD = 3
LOCK_DURATIONS_MINUTES = [10, 20, 30, 60, 60]


async def _get_login_guard(db: AsyncIOMotorDatabase, email: str) -> dict:
    return await db["login_attempts"].find_one({"email": email})


async def _save_login_guard(db: AsyncIOMotorDatabase, email: str, guard: dict) -> None:
    await db["login_attempts"].update_one(
        {"email": email},
        {"$set": guard},
        upsert=True,
    )


def _lock_duration_for_stage(stage: int) -> int:
    index = max(0, min(stage - 1, len(LOCK_DURATIONS_MINUTES) - 1))
    return LOCK_DURATIONS_MINUTES[index]


# Request & Response Schemas
class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    message: str


class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str = Field(..., min_length=6)
    mobile: str
    city: str
    role: str  # superadmin, admin, regular
    permissions: list[str] = []  # modules from frontend
    accessibleCities: list[str] = []  # NEW: accessible cities from frontend


class RegisterResponse(BaseModel):
    message: str
    access_token: str
    token_type: str = "bearer"
    user_id: str


class UserOut(BaseModel):
    id: str
    name: str
    email: str
    mobile: str
    city: str
    role: str
    accessibleCities: list[str] = []  # NEW: accessible cities for user
    # Add other fields as needed, but exclude password/hash


class UserUpdateRequest(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    mobile: str | None = None
    city: str | None = None
    role: str | None = None
    accessibleCities: list[str] | None = None
    # Add other fields as needed


# 🔐 Login Endpoint
@router.post("/login", response_model=LoginResponse)
async def login_user(
    request: LoginRequest,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    email = request.email.lower()
    password = request.password

    guard = await _get_login_guard(db, email)
    now = datetime.utcnow()
    if guard and guard.get("locked_until") and guard["locked_until"] > now:
        retry_after = int((guard["locked_until"] - now).total_seconds())
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Account temporarily locked. Try again later.",
            headers={"Retry-After": str(max(retry_after, 1))},
        )

    user = await db["users"].find_one({"email": email})
    if not user:
        await _record_login_failure(db, email, now)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if not verify_password(password, user["hashed_password"]):
        await _record_login_failure(db, email, now)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password"
        )

    await db["login_attempts"].delete_one({"email": email})

    access_token = create_access_token(data={
        "sub": user["email"],
        "name": user["name"],
        "role": user.get("role", ""),
        "id": str(user["_id"]),
        "accessibleCities": user.get("accessibleCities", [])
    })
    return LoginResponse(
        access_token=access_token,
        message="Login successful"
    )


async def _record_login_failure(db: AsyncIOMotorDatabase, email: str, now: datetime) -> None:
    guard = await _get_login_guard(db, email) or {
        "email": email,
        "failed_count": 0,
        "window_start": now,
        "locked_until": None,
        "lock_stage": 0,
    }

    window_start = guard.get("window_start") or now
    if now - window_start > timedelta(minutes=LOCK_WINDOW_MINUTES):
        guard["failed_count"] = 0
        guard["window_start"] = now

    guard["failed_count"] = guard.get("failed_count", 0) + 1

    threshold = INITIAL_LOCK_THRESHOLD if guard.get("lock_stage", 0) == 0 else FOLLOWUP_LOCK_THRESHOLD
    if guard["failed_count"] >= threshold:
        guard["lock_stage"] = min(guard.get("lock_stage", 0) + 1, len(LOCK_DURATIONS_MINUTES))
        duration_minutes = _lock_duration_for_stage(guard["lock_stage"])
        guard["locked_until"] = now + timedelta(minutes=duration_minutes)
        guard["failed_count"] = 0
        guard["window_start"] = now

    await _save_login_guard(db, email, guard)


# 🔐 Register Endpoint
@router.post("/register", response_model=RegisterResponse)
async def register_user(
    request: RegisterRequest,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    email = request.email.lower()

    # Check if user already exists
    existing_user = await db["users"].find_one({"email": email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Hash the password
    hashed_pw = hash_password(request.password)

    user_data = {
        "email": email,
        "name": request.name,
        "hashed_password": hashed_pw,
        "mobile": request.mobile,
        "city": request.city,
        "role": request.role,
        "accessibleCities": request.accessibleCities,  # NEW
    }

    # Insert the user
    result = await db["users"].insert_one(user_data)
    user_id = str(result.inserted_id)

    # Assign permissions from frontend (all permissions for each selected module)
    modules = getattr(request, "permissions", None)
    default_permissions = ["read", "write", "update", "delete", "audit", "all"]
    if modules:
        await db["permissions"].update_one(
            {"user_id": result.inserted_id},
            {"$set": {f"modules.{m}": default_permissions for m in modules}},
            upsert=True
        )

    # Generate JWT token
    access_token = create_access_token(data={"sub": email, "id": user_id, "role": request.role})

    return RegisterResponse(
        message="User registered successfully",
        access_token=access_token,
        user_id=user_id
    )


@router.get("/users", response_model=List[UserOut])
async def list_users(db: AsyncIOMotorDatabase = Depends(get_db)):
    """
    Returns a list of all registered users (excluding sensitive info).
    """
    users = []
    async for user in db["users"].find():
        users.append(UserOut(
            id=str(user["_id"]),
            name=user.get("name", ""),
            email=user.get("email", ""),
            mobile=user.get("mobile", ""),
            city=user.get("city", ""),
            role=user.get("role", ""),
            accessibleCities=user.get("accessibleCities", []),  # NEW
        ))
    return users


@router.get("/users/{user_id}", response_model=UserOut)
async def get_user(user_id: str = Path(...), db: AsyncIOMotorDatabase = Depends(get_db)):
    """
    Get a single user's info by user_id (for frontend dashboard restriction).
    """
    try:
        oid = ObjectId(user_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid user_id format")
    user = await db["users"].find_one({"_id": oid})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserOut(
        id=str(user["_id"]),
        name=user.get("name", ""),
        email=user.get("email", ""),
        mobile=user.get("mobile", ""),
        city=user.get("city", ""),
        role=user.get("role", ""),
        accessibleCities=user.get("accessibleCities", []),
    )


@router.delete("/users/{user_id}")
async def delete_user(user_id: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    """
    Delete a user and their permissions by user_id.
    """
    try:
        oid = ObjectId(user_id)
    except Exception:
        return Response(status_code=400, content="Invalid user_id format")
    result = await db["users"].delete_one({"_id": oid})
    await db["permissions"].delete_one({"user_id": oid})
    if result.deleted_count == 0:
        return Response(status_code=404, content="User not found")
    return {"message": "User deleted successfully"}


@router.post("/users/{user_id}/reset_password")
async def admin_reset_password(
    user_id: str,
    new_password: str = Body(..., embed=True),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Allows an admin to reset a user's password by user_id.
    """
    try:
        oid = ObjectId(user_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid user_id format")
    hashed_pw = hash_password(new_password)
    result = await db["users"].update_one({"_id": oid}, {"$set": {"hashed_password": hashed_pw}})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "Password reset successfully"}


@router.patch("/users/{user_id}")
async def update_user(
    user_id: str,
    update: UserUpdateRequest = Body(...),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Update user fields (including accessibleCities) by user_id.
    """
    try:
        oid = ObjectId(user_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid user_id format")
    update_data = {k: v for k, v in update.dict(exclude_unset=True).items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")
    result = await db["users"].update_one({"_id": oid}, {"$set": update_data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User updated successfully"}
