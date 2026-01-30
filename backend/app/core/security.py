"""
JWT Security utilities for local token verification.
Uses PyJWT for HS256 JWT verification without calling Passport on every request.
"""
import jwt
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.database import get_db
from app.models.user import User


# Security scheme for Bearer token
security = HTTPBearer(auto_error=False)


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
    ):
        self.user_id = user_id
        self.email = email
        self.company_code = company_code
        self.exp = exp
        self.name = name
        self.role = role
        self.company_name = company_name


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
        # Bheem Passport JWT structure: user_id, email, company_code, exp, name, role
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
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    FastAPI dependency to get the current authenticated user.

    Extracts and verifies the JWT token from the Authorization header,
    then retrieves or creates the corresponding local user.

    Args:
        credentials: HTTP Bearer credentials from Authorization header
        db: Database session

    Returns:
        User object for the authenticated user

    Raises:
        HTTPException: If no token provided or token is invalid
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify token locally
    token_data = verify_token(credentials.credentials)

    # Look up local user by passport_user_id
    result = await db.execute(
        select(User).where(User.passport_user_id == token_data.user_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        # User not found locally - they need to sync first via /auth/sync
        # However, for better UX, we can auto-create the user here
        from app.models.user import UserRole, UserStatus

        user = User(
            passport_user_id=token_data.user_id,
            name=token_data.name or "Unknown",
            email=token_data.email,
            role=UserRole.USER,
            status=UserStatus.ACTIVE,
            company_code=token_data.company_code,
            company_name=token_data.company_name,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

    return user


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """
    Optional version of get_current_user that returns None if not authenticated.
    Useful for endpoints that work with or without authentication.
    """
    if not credentials:
        return None

    try:
        return await get_current_user(credentials, db)
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
