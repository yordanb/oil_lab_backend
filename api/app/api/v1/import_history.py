from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.import_history import ImportHistory

router = APIRouter(
    prefix="/import/history",
    tags=["Import History"]
)

@router.get("")
def get_import_history(
    db: Session = Depends(get_db)
):

    rows = (
        db.execute(
            select(ImportHistory)
            .order_by(
                ImportHistory.imported_at.desc()
            )
        )
        .scalars()
        .all()
    )

    return rows


