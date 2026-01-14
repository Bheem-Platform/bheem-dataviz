from pydantic import BaseModel
from typing import Optional

class NLQueryRequest(BaseModel):
    question: str
    dataset_id: Optional[str] = None
    context: Optional[str] = None

class NLQueryResponse(BaseModel):
    sql: str
    explanation: str
    confidence: float

class InsightsRequest(BaseModel):
    dataset_id: str
