from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from sqlalchemy.orm import Session

from app.core.database import get_db

from app.services.sample_service import (
    get_samples,
    get_sample_by_id,
    get_samples_by_unit,
    get_samples_by_vessel,
    get_stats,
    get_units,
    get_filtered_samples
)

router = APIRouter(
    prefix="/samples",
    tags=["Samples"]
)

@router.get("")
def list_samples(
    page: int = 1,
    page_size: int = 100,
    db: Session = Depends(get_db)
):
    return get_samples(db, page, page_size)


@router.get("/stats")
def stats(
    vessel: str = None,
    unit: str = None,
    date_from: str = None,
    date_to: str = None,
    db: Session = Depends(get_db)
):
    return get_stats(db, vessel, unit, date_from, date_to)


@router.get("/units")
def units(
    vessel: str = None,
    db: Session = Depends(get_db)
):
    return get_units(db, vessel)


@router.get("/search")
def search_samples(
    page: int = 1,
    page_size: int = 50,
    vessel: str = None,
    unit: str = None,
    date_from: str = None,
    date_to: str = None,
    db: Session = Depends(get_db)
):
    return get_filtered_samples(db, page, page_size, vessel, unit, date_from, date_to)


@router.get("/unit/{unit_id}")
def samples_by_unit(
    unit_id: str,
    page: int = 1,
    page_size: int = 100,
    db: Session = Depends(get_db)
):
    return get_samples_by_unit(db, unit_id, page, page_size)


@router.get("/vessel/{vessel_id}")
def samples_by_vessel(
    vessel_id: str,
    page: int = 1,
    page_size: int = 100,
    db: Session = Depends(get_db)
):
    return get_samples_by_vessel(db, vessel_id, page, page_size)


@router.get("/{sample_id}")
def get_sample(
    sample_id: int,
    db: Session = Depends(get_db)
):
    row = get_sample_by_id(db, sample_id)
    if not row:
        raise HTTPException(status_code=404, detail="Sample not found")
    return row