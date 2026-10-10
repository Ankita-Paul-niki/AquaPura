"""
Pydantic schemas for authentication endpoints.
"""

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    full_name: str  = Field(..., min_length=1, max_length=150)
    email:     EmailStr
    password:  str  = Field(..., min_length=8)


class LoginRequest(BaseModel):
    email:    EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type:   str = "bearer"


class UserResponse(BaseModel):
    id:        int
    full_name: str
    email:     str

    model_config = {"from_attributes": True}
