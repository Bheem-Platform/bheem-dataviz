from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    PROJECT_NAME: str = "Bheem DataViz"
    API_V1_STR: str = "/api/v1"
    
    DATABASE_URL: str = "postgresql://localhost/dataviz"
    REDIS_URL: str = "redis://localhost:6379"
    
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "https://dataviz.bheemkodee.com"]
    
    OPENAI_API_KEY: str = ""
    
    class Config:
        env_file = ".env"

settings = Settings()
