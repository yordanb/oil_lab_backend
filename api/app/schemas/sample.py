from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class SampleResponse(BaseModel):
    id: int

    sample_date: datetime | None
    unit_id: str | None
    vesselid1: str | None

    lab_no: str | None
    compartment: str | None

    oil_brand: str | None
    oil_grade: str | None

    nfe: float | None
    ncu: float | None
    nal: float | None
    ncr: float | None

    nwater: float | None
    nfuel: float | None
    ntbn: float | None
    ntan: float | None

    class Config:
        from_attributes = True
