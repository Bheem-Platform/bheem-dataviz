"""
Bheem Passport HTTP Client for authentication operations.
Singleton pattern for efficient connection reuse.
"""
import httpx
from typing import Optional, Dict, Any
from fastapi import HTTPException

from app.core.config import settings


class BheemPassportClient:
    """HTTP client for Bheem Passport authentication service."""

    _instance: Optional["BheemPassportClient"] = None
    _client: Optional[httpx.AsyncClient] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @property
    def base_url(self) -> str:
        return settings.BHEEMPASSPORT_URL

    @property
    def company_code(self) -> str:
        return settings.COMPANY_CODE

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create the HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(30.0),
                headers={
                    "Content-Type": "application/json",
                    "X-Company-Code": self.company_code,
                }
            )
        return self._client

    async def close(self):
        """Close the HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None

    async def login(self, email: str, password: str, company_code: Optional[str] = None) -> Dict[str, Any]:
        """
        Authenticate user with Bheem Passport.

        Args:
            email: User's email address
            password: User's password
            company_code: Optional company code override

        Returns:
            Dict containing access_token, refresh_token, and token_type
        """
        client = await self._get_client()

        form_data = {
            "username": email,
            "password": password,
            "company_code": company_code or self.company_code,
        }

        try:
            response = await client.post(
                f"{self.base_url}/login",
                data=form_data,
                headers={
                    "Content-Type": "application/x-www-form-urlencoded",
                    "X-Company-Code": company_code or self.company_code,
                }
            )

            if response.status_code == 401:
                raise HTTPException(status_code=401, detail="Invalid credentials")
            elif response.status_code == 403:
                raise HTTPException(status_code=403, detail="Account is inactive or banned")
            elif response.status_code != 200:
                error_detail = response.json().get("detail", response.text)
                raise HTTPException(status_code=response.status_code, detail=f"Authentication failed: {error_detail}")

            return response.json()

        except httpx.RequestError as e:
            raise HTTPException(
                status_code=503,
                detail=f"Cannot connect to authentication service: {str(e)}"
            )

    async def register(
        self,
        email: str,
        password: str,
        company_code: Optional[str] = None,
        role: str = "Customer"
    ) -> Dict[str, Any]:
        """
        Register a new user with Bheem Passport.

        Args:
            email: User's email address
            password: User's password
            company_code: Optional company code override
            role: User role (default: Customer)

        Returns:
            Dict containing user registration details
        """
        client = await self._get_client()

        register_data = {
            "username": email,
            "password": password,
            "role": role,
            "company_code": company_code or self.company_code,
        }

        try:
            response = await client.post(
                f"{self.base_url}/register",
                json=register_data,
                headers={"X-Company-Code": company_code or self.company_code}
            )

            if response.status_code == 400:
                error_detail = response.json().get("detail", "Registration failed")
                raise HTTPException(status_code=400, detail=error_detail)
            elif response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Registration failed: {response.text}"
                )

            return response.json()

        except httpx.RequestError as e:
            raise HTTPException(
                status_code=503,
                detail=f"Cannot connect to authentication service: {str(e)}"
            )

    async def validate_token(self, access_token: str) -> Dict[str, Any]:
        """
        Validate a token with Bheem Passport.

        Args:
            access_token: JWT access token

        Returns:
            Dict containing user information if token is valid
        """
        client = await self._get_client()

        try:
            response = await client.get(
                f"{self.base_url}/me",
                headers={"Authorization": f"Bearer {access_token}"}
            )

            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                raise HTTPException(status_code=401, detail="Invalid or expired token")
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail="Token validation failed"
                )

        except httpx.RequestError as e:
            raise HTTPException(
                status_code=503,
                detail=f"Cannot connect to authentication service: {str(e)}"
            )

    async def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """
        Refresh an access token using a refresh token.

        Args:
            refresh_token: JWT refresh token

        Returns:
            Dict containing new access_token and refresh_token
        """
        client = await self._get_client()

        try:
            response = await client.post(
                f"{self.base_url}/refresh",
                json={"refresh_token": refresh_token},
                headers={"X-Company-Code": self.company_code}
            )

            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                raise HTTPException(status_code=401, detail="Invalid or expired refresh token")
            else:
                error_detail = response.json().get("detail", "Token refresh failed")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=error_detail
                )

        except httpx.RequestError as e:
            raise HTTPException(
                status_code=503,
                detail=f"Cannot connect to authentication service: {str(e)}"
            )

    async def get_current_user(self, access_token: str) -> Dict[str, Any]:
        """
        Get current user information from Bheem Passport.
        Alias for validate_token for semantic clarity.

        Args:
            access_token: JWT access token

        Returns:
            Dict containing user information
        """
        return await self.validate_token(access_token)

    async def get_companies(self) -> list:
        """
        Get list of available companies.

        Returns:
            List of company objects
        """
        client = await self._get_client()

        try:
            response = await client.get(f"{self.base_url}/companies")

            if response.status_code == 200:
                return response.json()
            else:
                return []

        except httpx.RequestError:
            return []


# Singleton accessor
_passport_client: Optional[BheemPassportClient] = None


def get_passport_client() -> BheemPassportClient:
    """Get the singleton Bheem Passport client instance."""
    global _passport_client
    if _passport_client is None:
        _passport_client = BheemPassportClient()
    return _passport_client
