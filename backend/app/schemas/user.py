from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from uuid import UUID


class UserBase(BaseModel):
    email: EmailStr
    name: str


class UserCreate(UserBase):
    passport_user_id: str
    company_code: str
    company_name: Optional[str] = None


class UserResponse(UserBase):
    id: UUID
    role: str
    status: str
    company_code: str
    company_name: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class AuthResponse(BaseModel):
    user: UserResponse
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    access_token: str


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    company_code: Optional[str] = None  # Defaults to BHM010 in auth endpoint


class RegisterResponse(BaseModel):
    id: str
    username: str
    role: str
    message: str = "Registration successful"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    company_code: Optional[str] = None  # Defaults to BHM010 in auth endpoint


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
