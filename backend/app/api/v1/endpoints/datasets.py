from fastapi import APIRouter, HTTPException
from typing import List
from app.schemas.dataset import Dataset, DatasetCreate

router = APIRouter()

datasets_db = {}

@router.get("/", response_model=List[Dataset])
async def list_datasets():
    return list(datasets_db.values())

@router.post("/", response_model=Dataset)
async def create_dataset(dataset: DatasetCreate):
    ds_id = str(len(datasets_db) + 1)
    ds = Dataset(id=ds_id, **dataset.dict())
    datasets_db[ds_id] = ds
    return ds

@router.get("/{dataset_id}", response_model=Dataset)
async def get_dataset(dataset_id: str):
    if dataset_id not in datasets_db:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return datasets_db[dataset_id]

@router.get("/{dataset_id}/preview")
async def preview_dataset(dataset_id: str, limit: int = 100):
    if dataset_id not in datasets_db:
        raise HTTPException(status_code=404, detail="Dataset not found")
    # TODO: Execute query and return preview
    return {"columns": [], "rows": [], "total": 0}
