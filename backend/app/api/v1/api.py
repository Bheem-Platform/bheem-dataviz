from fastapi import APIRouter
from app.api.v1.endpoints import connections, datasets, dashboards, charts, queries, ai

api_router = APIRouter()

api_router.include_router(connections.router, prefix="/connections", tags=["connections"])
api_router.include_router(datasets.router, prefix="/datasets", tags=["datasets"])
api_router.include_router(dashboards.router, prefix="/dashboards", tags=["dashboards"])
api_router.include_router(charts.router, prefix="/charts", tags=["charts"])
api_router.include_router(queries.router, prefix="/queries", tags=["queries"])
api_router.include_router(ai.router, prefix="/ai", tags=["ai"])
