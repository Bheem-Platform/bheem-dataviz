from fastapi import APIRouter, HTTPException
from typing import List
from app.schemas.chart import Chart, ChartCreate

router = APIRouter()

charts_db = {}

@router.get("/", response_model=List[Chart])
async def list_charts():
    return list(charts_db.values())

@router.post("/", response_model=Chart)
async def create_chart(chart: ChartCreate):
    chart_id = str(len(charts_db) + 1)
    c = Chart(id=chart_id, **chart.dict())
    charts_db[chart_id] = c
    return c

@router.get("/{chart_id}", response_model=Chart)
async def get_chart(chart_id: str):
    if chart_id not in charts_db:
        raise HTTPException(status_code=404, detail="Chart not found")
    return charts_db[chart_id]

@router.get("/{chart_id}/render")
async def render_chart(chart_id: str):
    if chart_id not in charts_db:
        raise HTTPException(status_code=404, detail="Chart not found")
    # TODO: Execute query and return chart data
    return {"data": [], "config": {}}
