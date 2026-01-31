"""
JWT Security utilities for local token verification.
Uses PyJWT for HS256 JWT verification without calling Passport on every request.
User data comes from BheemPassport/ERP - no local users table needed.
"""
import jwt
from datetime import datetime, timezone
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

from app.core.config import settings


# Security scheme for Bearer token
security = HTTPBearer(auto_error=False)


class CurrentUser(BaseModel):
    """User data extracted from JWT token. No local DB needed."""
    id: str
    email: str
    name: Optional[str] = None
    role: str = "user"
    company_code: str
    company_name: Optional[str] = None
    companies: list[str] = []

    class Config:
        from_attributes = True


class TokenData:
    """Extracted token data."""

    def __init__(
        self,
        user_id: str,
        email: str,
        company_code: str,
        exp: Optional[datetime] = None,
        name: Optional[str] = None,
        role: Optional[str] = None,
        company_name: Optional[str] = None,
        companies: list[str] = None,
    ):
        self.user_id = user_id
        self.email = email
        self.company_code = company_code
        self.exp = exp
        self.name = name
        self.role = role
        self.company_name = company_name
        self.companies = companies or []


def verify_token(token: str) -> TokenData:
    """
    Verify and decode a JWT token locally using PyJWT.

    Args:
        token: JWT access token string

    Returns:
        TokenData object with decoded claims

    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        # Decode the JWT with HS256 algorithm
        payload = jwt.decode(
            token,
            settings.BHEEM_JWT_SECRET,
            algorithms=["HS256"],
            options={"verify_exp": True}
        )

        # Extract user information from payload
        # Bheem Passport JWT structure: user_id, username, role, company_code, companies, exp
        user_id = payload.get("user_id") or payload.get("sub")
        email = payload.get("email") or payload.get("username")
        company_code = payload.get("company_code", settings.COMPANY_CODE)

        if not user_id or not email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing required claims",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Convert exp timestamp to datetime if present
        exp = None
        if "exp" in payload:
            exp = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)

        return TokenData(
            user_id=user_id,
            email=email,
            company_code=company_code,
            exp=exp,
            name=payload.get("name"),
            role=payload.get("role"),
            company_name=payload.get("company_name"),
            companies=payload.get("companies", []),
        )

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> CurrentUser:
    """
    FastAPI dependency to get the current authenticated user from JWT.

    User data comes from BheemPassport/ERP - no local database query needed.

    Args:
        credentials: HTTP Bearer credentials from Authorization header

    Returns:
        CurrentUser object with user data from token

    Raises:
        HTTPException: If no token provided or token is invalid
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify token locally and extract user data
    token_data = verify_token(credentials.credentials)

    return CurrentUser(
        id=token_data.user_id,
        email=token_data.email,
        name=token_data.name or token_data.email.split("@")[0],
        role=token_data.role or "user",
        company_code=token_data.company_code,
        company_name=token_data.company_name,
        companies=token_data.companies,
    )


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Optional[CurrentUser]:
    """
    Optional version of get_current_user that returns None if not authenticated.
    Useful for endpoints that work with or without authentication.
    """
    if not credentials:
        return None

    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None


def get_token_expiration(token: str) -> Optional[datetime]:
    """
    Get the expiration time from a JWT without full verification.
    Useful for checking if a token needs refresh.

    Args:
        token: JWT token string

    Returns:
        datetime of expiration or None if no expiration
    """
    try:
        # Decode without verification to get expiration
        payload = jwt.decode(
            token,
            options={"verify_signature": False, "verify_exp": False}
        )
        if "exp" in payload:
            return datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        return None
    except jwt.InvalidTokenError:
        return None
