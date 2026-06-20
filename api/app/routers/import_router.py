import os
import uuid

from fastapi import (
    APIRouter,
    UploadFile,
    File,
    Depends,
    HTTPException
)

from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.excel_import import import_excel

router = APIRouter(
    prefix="/api/import",
    tags=["Import"]
)


@router.post("/xlsx")
async def upload_xlsx(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    if not file.filename.endswith(
        (".xlsx", ".xls")
    ):
        raise HTTPException(
            status_code=400,
            detail="Invalid file type"
        )

    temp_file = (
        f"/tmp/{uuid.uuid4()}.xlsx"
    )

    with open(temp_file, "wb") as buffer:
        buffer.write(
            await file.read()
        )

    return import_excel(
        temp_file,
        file.filename,
        db
    )
