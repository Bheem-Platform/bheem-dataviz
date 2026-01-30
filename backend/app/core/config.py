from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    PROJECT_NAME: str = "Bheem DataViz"
    API_V1_STR: str = "/api/v1"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8008

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://localhost/dataviz"
    REDIS_URL: str = "redis://localhost:6379"

    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"

    # CORS - can be JSON array or comma-separated string
    CORS_ORIGINS: str = '["http://localhost:5173","http://localhost:3000","http://localhost:3008","https://dataviz.bheemkodee.com","https://dataviz-staging.bheemkodee.com"]'

    def get_cors_origins(self) -> List[str]:
        """Parse CORS origins from JSON or comma-separated string."""
        origins_str = self.CORS_ORIGINS
        if origins_str.startswith("["):
            import json
            return json.loads(origins_str)
        return [origin.strip() for origin in origins_str.split(",") if origin.strip()]

    # BheemPassport
    BHEEMPASSPORT_URL: str = "http://localhost:8003/api/v1/auth"
    BHEEMPASSPORT_SECRET: str = "bheem-platform-secret-key-change-in-production"
    BHEEM_JWT_SECRET: str = "erp-staging-super-secret-jwt-token-with-at-least-32-characters-long"
    COMPANY_CODE: str = "BHM010"

    # Frontend URL (for redirects)
    FRONTEND_URL: str = "http://localhost:5173"

    # OpenAI
    OPENAI_API_KEY: str = ""

settings = Settings()
