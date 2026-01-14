from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class DashboardBase(BaseModel):
    name: str
    description: Optional[str] = None
    layout: Optional[List[Dict[str, Any]]] = None
    filters: Optional[Dict[str, Any]] = None

class DashboardCreate(DashboardBase):
    pass

class Dashboard(DashboardBase):
    id: str
    is_published: bool = False
    
    class Config:
        from_attributes = True
