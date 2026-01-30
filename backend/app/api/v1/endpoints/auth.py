from fastapi import APIRouter, Depends, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.database import get_db
from app.schemas.user import AuthResponse, UserResponse, TokenPayload, RegisterRequest, RegisterResponse, LoginRequest, LoginResponse
from app.services.auth_service import AuthService
from app.core.config import settings
from app.core.bheem_passport_client import get_passport_client
from app.core.security import get_current_user, verify_token
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["Authentication"])
security = HTTPBearer()


class RefreshTokenRequest(BaseModel):
    """Request body for token refresh."""
    refresh_token: str


class RefreshTokenResponse(BaseModel):
    """Response body for token refresh."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


@router.post("/register", response_model=RegisterResponse)
async def register_user(payload: RegisterRequest):
    """
    Register a new user via BheemPassport.
    Frontend -> Backend -> BheemPassport
    """
    passport_client = get_passport_client()

    # Use company_code from payload or default to settings
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

    # Use company_code from payload or default to settings (BHM010)
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
async def sync_user(
    payload: TokenPayload,
    db: AsyncSession = Depends(get_db)
):
    """
    Sync user from BheemPassport after OAuth login.
    Frontend calls this after receiving token from BheemPassport callback.
    Uses local JWT verification instead of calling Passport /me.
    """
    # Verify token locally using PyJWT
    token_data = verify_token(payload.access_token)

    # Build passport user dict from token data
    passport_user = {
        "user_id": token_data.user_id,
        "email": token_data.email,
        "name": token_data.name,
        "company_code": token_data.company_code,
        "company_name": token_data.company_name,
    }

    # Get or create local user
    local_user = await AuthService.get_or_create_user(db, passport_user)

    return AuthResponse(
        user=UserResponse.model_validate(local_user),
        access_token=payload.access_token
    )


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: User = Depends(get_current_user)
):
    """
    Get current authenticated user.
    Uses local JWT verification - no call to Passport.
    """
    return UserResponse.model_validate(current_user)


@router.get("/config")
async def get_auth_config():
    """Get auth configuration for frontend"""
    return {
        "passport_url": settings.BHEEMPASSPORT_URL,
        "company_code": settings.COMPANY_CODE,
        "oauth_providers": ["google", "github"]
    }
