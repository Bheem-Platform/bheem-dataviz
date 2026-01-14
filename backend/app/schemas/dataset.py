from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class DatasetBase(BaseModel):
    name: str
    connection_id: str
    sql_query: Optional[str] = None
    table_name: Optional[str] = None
    columns: Optional[List[Dict[str, Any]]] = None

class DatasetCreate(DatasetBase):
    pass

class Dataset(DatasetBase):
    id: str
    row_count: Optional[int] = None
    
    class Config:
        from_attributes = True
