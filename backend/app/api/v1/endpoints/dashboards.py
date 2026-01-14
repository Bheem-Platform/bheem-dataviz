from fastapi import APIRouter, HTTPException
from typing import List
from app.schemas.dashboard import Dashboard, DashboardCreate

router = APIRouter()

dashboards_db = {}

@router.get("/", response_model=List[Dashboard])
async def list_dashboards():
    return list(dashboards_db.values())

@router.post("/", response_model=Dashboard)
async def create_dashboard(dashboard: DashboardCreate):
    db_id = str(len(dashboards_db) + 1)
    db = Dashboard(id=db_id, **dashboard.dict())
    dashboards_db[db_id] = db
    return db

@router.get("/{dashboard_id}", response_model=Dashboard)
async def get_dashboard(dashboard_id: str):
    if dashboard_id not in dashboards_db:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    return dashboards_db[dashboard_id]

@router.put("/{dashboard_id}", response_model=Dashboard)
async def update_dashboard(dashboard_id: str, dashboard: DashboardCreate):
    if dashboard_id not in dashboards_db:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    db = Dashboard(id=dashboard_id, **dashboard.dict())
    dashboards_db[dashboard_id] = db
    return db

@router.delete("/{dashboard_id}")
async def delete_dashboard(dashboard_id: str):
    if dashboard_id not in dashboards_db:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    del dashboards_db[dashboard_id]
    return {"status": "deleted"}
