from fastapi import APIRouter

from app.api.v1.samples import router as sample_router
from app.api.v1.import_history import router as import_router

api_router = APIRouter()

api_router.include_router(sample_router)
api_router.include_router(import_router)

