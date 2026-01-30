from fastapi import APIRouter
from app.api.v1.endpoints import connections, datasets, dashboards, charts, queries, ai, auth, transforms, semantic_models, kpi, quickcharts

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(connections.router, prefix="/connections", tags=["connections"])
api_router.include_router(datasets.router, prefix="/datasets", tags=["datasets"])
api_router.include_router(dashboards.router, prefix="/dashboards", tags=["dashboards"])
api_router.include_router(charts.router, prefix="/charts", tags=["charts"])
api_router.include_router(queries.router, prefix="/queries", tags=["queries"])
api_router.include_router(ai.router, prefix="/ai", tags=["ai"])
api_router.include_router(transforms.router, prefix="/transforms", tags=["transforms"])
api_router.include_router(semantic_models.router, prefix="/models", tags=["models"])
api_router.include_router(kpi.router, prefix="/kpi", tags=["kpi"])
api_router.include_router(quickcharts.router, prefix="/quickcharts", tags=["quickcharts"])
