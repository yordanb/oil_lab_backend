from pydantic import BaseModel


class ImportResponse(BaseModel):
    filename: str
    total_rows: int
    imported_rows: int
    failed_rows: int
