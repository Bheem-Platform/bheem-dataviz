# Backend v1.1 - Added login/register via BheemPassport proxy
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.api import api_router
from app.core.config import settings
from app.database import get_engine, Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create database tables
    try:
        engine = get_engine()
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("Database tables created successfully")
    except Exception as e:
        print(f"Warning: Could not connect to database: {e}")
        print("App will start but database features won't work")
    yield
    # Shutdown: cleanup if needed
    pass


app = FastAPI(
    title="Bheem DataViz API",
    description="AI-Powered Business Intelligence & Data Visualization",
    version="0.1.0",
    openapi_url="/api/v1/openapi.json",
    lifespan=lifespan,
    redirect_slashes=False  # Avoid 307 redirects that break HTTPS->HTTP
)

# Hardcoded CORS origins to ensure frontend access
CORS_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:3008",
    "http://localhost:5173",
    "https://dataviz.bheemkodee.com",
    "https://dataviz-staging.bheemkodee.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    return {
        "name": "Bheem DataViz API",
        "version": "1.3.0",
        "description": "AI-Powered BI Platform with BheemPassport Auth",
        "docs": "/docs",
        "health": "/health",
        "api": "/api/v1"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "bheem-dataviz"}
