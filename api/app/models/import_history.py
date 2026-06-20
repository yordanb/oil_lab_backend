from sqlalchemy import (
    Column,
    BigInteger,
    Integer,
    Text,
    TIMESTAMP,
    text
)

from sqlalchemy.orm import declarative_base

Base = declarative_base()


class ImportHistory(Base):
    __tablename__ = "import_history"
    __table_args__ = {"schema": "oil_lab"}

    id = Column(BigInteger, primary_key=True)
    filename = Column(Text, nullable=False)

    total_rows = Column(Integer, default=0)
    imported_rows = Column(Integer, default=0)
    failed_rows = Column(Integer, default=0)

    imported_at = Column(
        TIMESTAMP(timezone=True),
        server_default=text("now()")
    )
