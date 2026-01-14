"""
Bheem DataViz Python SDK

Usage:
    from dataviz_client import DataVizClient
    
    client = DataVizClient(api_url="https://api.dataviz.bheemkodee.com")
    dashboards = client.dashboards.list()
"""

import httpx
from typing import Optional, Dict, Any, List

class DataVizClient:
    def __init__(self, api_url: str, api_key: Optional[str] = None):
        self.api_url = api_url.rstrip("/")
        self.api_key = api_key
        self._client = httpx.Client(
            base_url=f"{self.api_url}/api/v1",
            headers={"Authorization": f"Bearer {api_key}"} if api_key else {}
        )
        
        self.connections = ConnectionsAPI(self._client)
        self.datasets = DatasetsAPI(self._client)
        self.dashboards = DashboardsAPI(self._client)
        self.charts = ChartsAPI(self._client)
        self.queries = QueriesAPI(self._client)


class ConnectionsAPI:
    def __init__(self, client: httpx.Client):
        self._client = client
    
    def list(self) -> List[Dict]:
        return self._client.get("/connections").json()
    
    def create(self, data: Dict) -> Dict:
        return self._client.post("/connections", json=data).json()
    
    def get(self, connection_id: str) -> Dict:
        return self._client.get(f"/connections/{connection_id}").json()
    
    def test(self, connection_id: str) -> Dict:
        return self._client.post(f"/connections/{connection_id}/test").json()


class DatasetsAPI:
    def __init__(self, client: httpx.Client):
        self._client = client
    
    def list(self) -> List[Dict]:
        return self._client.get("/datasets").json()
    
    def create(self, data: Dict) -> Dict:
        return self._client.post("/datasets", json=data).json()
    
    def preview(self, dataset_id: str, limit: int = 100) -> Dict:
        return self._client.get(f"/datasets/{dataset_id}/preview", params={"limit": limit}).json()


class DashboardsAPI:
    def __init__(self, client: httpx.Client):
        self._client = client
    
    def list(self) -> List[Dict]:
        return self._client.get("/dashboards").json()
    
    def create(self, data: Dict) -> Dict:
        return self._client.post("/dashboards", json=data).json()
    
    def get(self, dashboard_id: str) -> Dict:
        return self._client.get(f"/dashboards/{dashboard_id}").json()
    
    def update(self, dashboard_id: str, data: Dict) -> Dict:
        return self._client.put(f"/dashboards/{dashboard_id}", json=data).json()


class ChartsAPI:
    def __init__(self, client: httpx.Client):
        self._client = client
    
    def list(self) -> List[Dict]:
        return self._client.get("/charts").json()
    
    def create(self, data: Dict) -> Dict:
        return self._client.post("/charts", json=data).json()
    
    def render(self, chart_id: str) -> Dict:
        return self._client.get(f"/charts/{chart_id}/render").json()


class QueriesAPI:
    def __init__(self, client: httpx.Client):
        self._client = client
    
    def execute(self, connection_id: str, sql: str, limit: int = 1000) -> Dict:
        return self._client.post("/queries/execute", json={
            "connection_id": connection_id,
            "sql": sql,
            "limit": limit
        }).json()
