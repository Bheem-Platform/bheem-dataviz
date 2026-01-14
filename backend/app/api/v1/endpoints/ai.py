from fastapi import APIRouter
from app.schemas.ai import NLQueryRequest, NLQueryResponse, InsightsRequest

router = APIRouter()

@router.post("/nl-query", response_model=NLQueryResponse)
async def natural_language_query(request: NLQueryRequest):
    # TODO: Implement NL to SQL conversion using OpenAI
    return NLQueryResponse(
        sql="SELECT * FROM sales LIMIT 10",
        explanation="Showing first 10 rows from sales table",
        confidence=0.85
    )

@router.post("/insights")
async def get_insights(request: InsightsRequest):
    # TODO: Implement AI insights generation
    return {
        "insights": [
            {"type": "trend", "message": "Sales increased 23% this quarter"},
            {"type": "anomaly", "message": "Unusual spike in returns on Dec 15"}
        ]
    }

@router.post("/chat")
async def chat(message: dict):
    # TODO: Implement chat with context
    return {
        "response": "I can help you analyze your data. What would you like to know?",
        "suggestions": ["Show sales by region", "Compare this month vs last month"]
    }

@router.post("/suggest")
async def suggest_visualizations(chart_id: dict):
    return {
        "suggestions": [
            {"type": "bar", "reason": "Best for comparing categories"},
            {"type": "line", "reason": "Good for showing trends over time"}
        ]
    }
