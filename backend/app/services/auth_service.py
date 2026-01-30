"""
Authentication service for user management.
Uses local JWT verification instead of calling Passport on every request.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException

from app.core.config import settings
from app.core.security import verify_token, TokenData
from app.models.user import User, UserStatus, UserRole


class AuthService:

    @staticmethod
    def verify_token_locally(access_token: str) -> TokenData:
        """
        Verify token locally using PyJWT.
        This replaces the previous verify_passport_token that called Passport /me.

        Args:
            access_token: JWT access token

        Returns:
            TokenData with user information from the JWT

        Raises:
            HTTPException: If token is invalid or expired
        """
        return verify_token(access_token)

    @staticmethod
    async def verify_passport_token(access_token: str) -> dict:
        """
        Verify token and return user info as a dict.
        Maintained for backward compatibility with existing code.
        Now uses local JWT verification instead of calling Passport.

        Args:
            access_token: JWT access token

        Returns:
            Dict with user_id, email, name, company_code, etc.
        """
        token_data = verify_token(access_token)

        return {
            "user_id": token_data.user_id,
            "email": token_data.email,
            "name": token_data.name,
            "company_code": token_data.company_code,
            "company_name": token_data.company_name,
            "role": token_data.role,
        }

    @staticmethod
    async def get_or_create_user(db: AsyncSession, passport_user: dict) -> User:
        """
        Get existing user or create new one from BheemPassport data.
        Called after OAuth login to sync user data locally.

        Args:
            db: Database session
            passport_user: Dict with user_id, email, name, company_code, etc.

        Returns:
            User model instance
        """
        # Check if user already exists by passport_user_id
        stmt = select(User).where(User.passport_user_id == passport_user["user_id"])
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()

        if user:
            # Update user info if changed
            user.name = passport_user.get("name", user.name)
            user.email = passport_user.get("email", user.email)
            if passport_user.get("company_code"):
                user.company_code = passport_user["company_code"]
            if passport_user.get("company_name"):
                user.company_name = passport_user["company_name"]
            await db.commit()
            await db.refresh(user)
            return user

        # Create new user
        new_user = User(
            passport_user_id=passport_user["user_id"],
            name=passport_user.get("name", "Unknown"),
            email=passport_user["email"],
            role=UserRole.USER,
            status=UserStatus.ACTIVE,
            company_code=passport_user.get("company_code", settings.COMPANY_CODE),
            company_name=passport_user.get("company_name")
        )

        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)

        return new_user

    @staticmethod
    async def get_user_by_passport_id(db: AsyncSession, passport_user_id: str) -> User | None:
        """
        Get user by BheemPassport user ID.

        Args:
            db: Database session
            passport_user_id: Passport user ID

        Returns:
            User model instance or None
        """
        stmt = select(User).where(User.passport_user_id == passport_user_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
        """
        Get user by email address.

        Args:
            db: Database session
            email: User's email address

        Returns:
            User model instance or None
        """
        stmt = select(User).where(User.email == email)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
