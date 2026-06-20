import os
import re
import pandas as pd
import math

from sqlalchemy import MetaData, Table
from sqlalchemy.dialects.postgresql import insert

from app.core.database import engine
from app.models.import_history import ImportHistory


def normalize_column(name: str) -> str:
    name = str(name).strip().lower()
    name = re.sub(r"[^a-z0-9]+", "_", name)
    name = re.sub(r"_+", "_", name)
    return name.strip("_")


COLUMN_MAPPING = {
    "pqindex": "pq_index",
    "nfuel": "n_fuel",
    "no_xi_max": "n_oxi_max",
    "gradet_bn": "grade_tbn",
}


def _sanitize_record(record: dict) -> dict:
    """Replace float('nan'), inf, and string 'NaN' with None."""
    for k, v in record.items():
        if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
            record[k] = None
        elif isinstance(v, str) and v.strip().lower() == 'nan':
            record[k] = None
    return record


def import_excel(file_path: str, filename: str, db):
    metadata = MetaData()

    sample_results = Table(
        "sample_results",
        metadata,
        schema="oil_lab",
        autoload_with=engine
    )

    history = ImportHistory(
        filename=filename,
        total_rows=0,
        imported_rows=0,
        failed_rows=0
    )

    db.add(history)
    db.commit()
    db.refresh(history)

    try:

        df = pd.read_excel(
            file_path,
            header=3
        )

        # buang 2 kolom kosong pertama
        df = df.iloc[:, 2:]

        # normalize header
        df.columns = [
            normalize_column(col)
            for col in df.columns
        ]

        # special mapping
        df.rename(
            columns=COLUMN_MAPPING,
            inplace=True
        )

        total_rows = len(df)

        # datetime conversion
        for col in ["sample_date", "date_taken"]:
            if col in df.columns:
                df[col] = pd.to_datetime(
                    df[col],
                    errors="coerce",
                    utc=True
                )

        # NaN -> None
        df = df.where(
            pd.notnull(df),
            None
        )

        # filter hanya kolom yg ada di DB
        valid_columns = {
            c.name
            for c in sample_results.columns
        }

        keep_columns = [
            c
            for c in df.columns
            if c in valid_columns
        ]

        df = df[keep_columns]

        records = df.to_dict(
            orient="records"
        )

        # sanitize: float nan/string NaN -> None
        for record in records:
            _sanitize_record(record)

        if len(records) == 0:
            raise Exception(
                "No valid columns found"
            )

        stmt = insert(
            sample_results
        ).values(records)

        stmt = stmt.on_conflict_do_nothing(
            index_elements=[
                "lab_no",
                "sample_date"
            ]
        )

        result = db.execute(stmt)
        db.commit()

        imported_rows = (
            result.rowcount
            if result.rowcount is not None
            else 0
        )

        failed_rows = (
            total_rows - imported_rows
        )

        history.total_rows = total_rows
        history.imported_rows = imported_rows
        history.failed_rows = failed_rows

        db.commit()

        return {
            "filename": filename,
            "total_rows": total_rows,
            "imported_rows": imported_rows,
            "failed_rows": failed_rows
        }

    except Exception:

        db.rollback()

        history.failed_rows = history.total_rows
        db.commit()

        raise

    finally:

        if os.path.exists(file_path):
            os.remove(file_path)
