from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, EmailStr, Field
from app.db.db import get_db
from app.utils.auth import (
    verify_password,
    create_access_token,
    hash_password  
)
from motor.motor_asyncio import AsyncIOMotorDatabase

router = APIRouter()


# Request & Response Schemas
class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    message: str


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    is_admin: bool = False


class RegisterResponse(BaseModel):
    message: str
    access_token: str
    token_type: str = "bearer"


# 🔐 Login Endpoint
@router.post("/login", response_model=LoginResponse)
async def login_user(
    request: LoginRequest,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    email = request.email.lower()
    password = request.password

    user = await db["users"].find_one({"email": email})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if not verify_password(password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password"
        )

    access_token = create_access_token(data={"sub": user["email"], "name" : user["name"], "isAdmin" : user["is_admin"], "id" : str(user["_id"])})
    return LoginResponse(
        access_token=access_token,
        message="Login successful"
    )


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
        "is_admin": request.is_admin
    }

    # Insert the user
    await db["users"].insert_one(user_data)

    # Generate JWT token
    access_token = create_access_token(data={"sub": email})

    return RegisterResponse(
        message="User registered successfully",
        access_token=access_token
    )
