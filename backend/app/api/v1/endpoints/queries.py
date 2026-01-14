from fastapi import APIRouter, HTTPException
from app.schemas.query import QueryExecute, QueryResult

router = APIRouter()

saved_queries = {}

@router.post("/execute", response_model=QueryResult)
async def execute_query(query: QueryExecute):
    # TODO: Implement actual query execution
    return QueryResult(
        columns=["id", "name", "value"],
        rows=[
            {"id": 1, "name": "Sample", "value": 100}
        ],
        total=1,
        execution_time=0.05
    )

@router.post("/preview", response_model=QueryResult)
async def preview_query(query: QueryExecute):
    # Same as execute but with LIMIT
    return await execute_query(query)

@router.get("/saved")
async def list_saved_queries():
    return list(saved_queries.values())

@router.post("/saved")
async def save_query(query: QueryExecute):
    query_id = str(len(saved_queries) + 1)
    saved_queries[query_id] = {"id": query_id, **query.dict()}
    return saved_queries[query_id]
