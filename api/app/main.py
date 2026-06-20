from fastapi import FastAPI
from sqlalchemy import text
from app.routers.import_router import router as import_router
from app.core.database import engine
from app.api.v1.router import api_router

app = FastAPI(
    title="Oil Lab API",
    version="1.0.0"
)

app.include_router(
    api_router,
    prefix="/api"
)

app.include_router(import_router)

@app.get("/")
def root():
    return {
        "service": "oil-lab-api",
        "status": "running"
    }


@app.get("/health")
def health():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))

        return {
            "status": "healthy",
            "database": "connected"
        }

    except Exception as e:
        return {
            "status": "unhealthy",
            "database": str(e)
        }
