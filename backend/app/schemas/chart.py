from pydantic import BaseModel
from typing import Optional, Dict, Any

class ChartBase(BaseModel):
    name: str
    type: str  # bar, line, pie, etc.
    dataset_id: str
    config: Optional[Dict[str, Any]] = None
    dimensions: Optional[list] = None
    metrics: Optional[list] = None

class ChartCreate(ChartBase):
    pass

class Chart(ChartBase):
    id: str
    
    class Config:
        from_attributes = True
