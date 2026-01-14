from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class QueryExecute(BaseModel):
    connection_id: str
    sql: str
    limit: Optional[int] = 1000

class QueryResult(BaseModel):
    columns: List[str]
    rows: List[Dict[str, Any]]
    total: int
    execution_time: float
