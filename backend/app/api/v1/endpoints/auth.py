from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer
from pydantic import BaseModel, EmailStr
from typing import Optional

from app.core.config import settings
from app.core.bheem_passport_client import get_passport_client
from app.core.security import get_current_user, verify_token, CurrentUser

router = APIRouter(prefix="/auth", tags=["Authentication"])
security = HTTPBearer()


# Request/Response Models
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    company_code: Optional[str] = None


class RegisterResponse(BaseModel):
    id: str
    username: str
    role: str
    message: str = "Registration successful"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    company_code: Optional[str] = None


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class RefreshTokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    access_token: str


class UserResponse(BaseModel):
    id: str
    email: str
    name: Optional[str] = None
    role: str
    status: str = "active"
    company_code: str
    company_name: Optional[str] = None


class AuthResponse(BaseModel):
    user: UserResponse
    access_token: str
    token_type: str = "bearer"


@router.post("/register", response_model=RegisterResponse)
async def register_user(payload: RegisterRequest):
    """
    Register a new user via BheemPassport.
    Frontend -> Backend -> BheemPassport
    """
    passport_client = get_passport_client()

    company_code = payload.company_code or settings.COMPANY_CODE

    result = await passport_client.register(
        email=payload.email,
        password=payload.password,
        company_code=company_code,
        role="Customer"
    )

    return RegisterResponse(
        id=result.get("id", ""),
        username=result.get("username", payload.email),
        role=result.get("role", "Customer"),
        message="Registration successful"
    )


@router.post("/login", response_model=LoginResponse)
async def login_user(payload: LoginRequest):
    """
    Login user via BheemPassport.
    Frontend -> Backend -> BheemPassport
    """
    passport_client = get_passport_client()

    company_code = payload.company_code or settings.COMPANY_CODE

    result = await passport_client.login(
        email=payload.email,
        password=payload.password,
        company_code=company_code
    )

    return LoginResponse(
        access_token=result.get("access_token", ""),
        refresh_token=result.get("refresh_token", ""),
        token_type="bearer"
    )


@router.post("/refresh", response_model=RefreshTokenResponse)
async def refresh_token(payload: RefreshTokenRequest):
    """
    Refresh an access token using a refresh token.
    """
    passport_client = get_passport_client()

    result = await passport_client.refresh_token(payload.refresh_token)

    return RefreshTokenResponse(
        access_token=result.get("access_token", ""),
        refresh_token=result.get("refresh_token", ""),
        token_type="bearer"
    )


@router.post("/sync", response_model=AuthResponse)
async def sync_user(payload: TokenPayload):
    """
    Sync user from BheemPassport after login.
    Verifies JWT and returns user data from token.
    No local database needed - user data comes from BheemPassport/ERP.
    """
    # Verify token locally using PyJWT
    token_data = verify_token(payload.access_token)

    # Build user response from token data
    user = UserResponse(
        id=token_data.user_id,
        email=token_data.email,
        name=token_data.name or token_data.email.split("@")[0],
        role=token_data.role or "user",
        status="active",
        company_code=token_data.company_code,
        company_name=token_data.company_name,
    )

    return AuthResponse(
        user=user,
        access_token=payload.access_token,
        token_type="bearer"
    )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: CurrentUser = Depends(get_current_user)):
    """
    Get current authenticated user.
    Uses local JWT verification - no call to Passport.
    """
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        name=current_user.name,
        role=current_user.role,
        status="active",
        company_code=current_user.company_code,
        company_name=current_user.company_name,
    )


@router.get("/config")
async def get_auth_config():
    """Get auth configuration for frontend"""
    return {
        "passport_url": settings.BHEEMPASSPORT_URL,
        "company_code": settings.COMPANY_CODE,
        "oauth_providers": ["google", "github"]
    }
