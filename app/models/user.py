from pydantic import BaseModel, Field, EmailStr, validator
from typing import List, Optional


class UserCreateRequest(BaseModel):
    """
    Pydantic model for **user-registration** requests.

    Attributes:
        email (EmailStr): User e-mail address (stored in lowercase).
        password (str): User password (≥ 8 characters recommended).
        full_name (str, optional): User’s full name.
        roles (List[str], optional): One or more roles (e.g. `admin`, `editor`).
    """

    email: EmailStr = Field(
        ...,
        description="User e-mail address (case-insensitive; converted to lowercase)",
        examples=["user@example.com"],
    )
    password: str = Field(
        ...,
        min_length=8,
        description="Plain-text password (min 8 chars; will be hashed server-side)",
    )
    name: Optional[str] = Field(
        None, description="Name of the user"
    )
    roles: List[str] = Field(
        default_factory=list,
        description="List of roles assigned to the user",
        examples=[["admin", "auditor"]],
    )

    # Always store / compare the e-mail in lowercase
    @validator("email")
    def _lowercase_email(cls, v: str) -> str:  # noqa: N805
        return v.lower()


class UserLoginRequest(BaseModel):
    """
    Pydantic model for **login** requests.

    Attributes:
        email (EmailStr): User e-mail (lower-cased before comparison).
        password (str): User password.
    """

    email: EmailStr = Field(
        ...,
        description="User e-mail address (case-insensitive; converted to lowercase)",
        examples=["USER@Example.COM"],
    )
    password: str = Field(..., description="User password")

    @validator("email")
    def _lowercase_email(cls, v: str) -> str:  # noqa: N805
        return v.lower()


class UserResponse(BaseModel):
    """
    Pydantic model for **user** responses.

    Attributes:
        id (int): Unique user ID.
        email (EmailStr): User e-mail (always lowercase).
        name (str | None): User’s full name.
        roles (List[str]): Roles granted to the user.
        accessibleCities (List[str]): Cities this user can access.
    """

    id: int
    email: EmailStr
    name: Optional[str] = None
    roles: List[str] = Field(default_factory=list)
    accessibleCities: List[str] = Field(default_factory=list)


class LoginResponse(BaseModel):
    """
    Pydantic model for **successful login** responses.

    Attributes:
        access_token (str): JWT access token for authenticated requests.
        token_type (str): Typically `"bearer"`.
        message (str): Human-readable confirmation.
    """

    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field("bearer", description="Token type (always 'bearer')")
    message: str = Field("Login successful", description="Status message")
