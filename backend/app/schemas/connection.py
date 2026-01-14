from pydantic import BaseModel
from typing import Optional, Dict, Any

class ConnectionBase(BaseModel):
    name: str
    type: str  # postgresql, mysql, bigquery, etc.
    host: Optional[str] = None
    port: Optional[int] = None
    database: Optional[str] = None
    username: Optional[str] = None
    extra: Optional[Dict[str, Any]] = None

class ConnectionCreate(ConnectionBase):
    password: Optional[str] = None

class Connection(ConnectionBase):
    id: str
    status: str = "active"
    
    class Config:
        from_attributes = True
