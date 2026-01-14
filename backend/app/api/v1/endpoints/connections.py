from fastapi import APIRouter, HTTPException
from typing import List
from app.schemas.connection import Connection, ConnectionCreate

router = APIRouter()

# In-memory store (replace with database)
connections_db = {}

@router.get("/", response_model=List[Connection])
async def list_connections():
    return list(connections_db.values())

@router.post("/", response_model=Connection)
async def create_connection(connection: ConnectionCreate):
    conn_id = str(len(connections_db) + 1)
    conn = Connection(id=conn_id, **connection.dict())
    connections_db[conn_id] = conn
    return conn

@router.get("/{connection_id}", response_model=Connection)
async def get_connection(connection_id: str):
    if connection_id not in connections_db:
        raise HTTPException(status_code=404, detail="Connection not found")
    return connections_db[connection_id]

@router.delete("/{connection_id}")
async def delete_connection(connection_id: str):
    if connection_id not in connections_db:
        raise HTTPException(status_code=404, detail="Connection not found")
    del connections_db[connection_id]
    return {"status": "deleted"}

@router.post("/{connection_id}/test")
async def test_connection(connection_id: str):
    if connection_id not in connections_db:
        raise HTTPException(status_code=404, detail="Connection not found")
    # TODO: Implement actual connection test
    return {"status": "success", "message": "Connection test passed"}
