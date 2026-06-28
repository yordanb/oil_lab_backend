from sqlalchemy import text
import math
from datetime import datetime

def sanitize_value(value):

    if isinstance(value, float):

        if math.isnan(value):
            return None

        if math.isinf(value):
            return None

    if isinstance(value, datetime):
        return value.isoformat()

    return value


def row_to_dict(row):

    return {
        key: sanitize_value(value)
        for key, value in row._mapping.items()
    }

def get_samples(
    db,
    page: int,
    page_size: int
):
    offset = (page - 1) * page_size

    total = db.execute(
        text("""
            SELECT COUNT(*)
            FROM oil_lab.sample_results
        """)
    ).scalar()

    rows = db.execute(
        text("""
            SELECT *
            FROM oil_lab.sample_results
            ORDER BY sample_date DESC
            LIMIT :limit
            OFFSET :offset
        """),
        {
            "limit": page_size,
            "offset": offset
        }
    )

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [
            #dict(row._mapping)
            row_to_dict(row)
            for row in rows
        ]
    }


def get_sample_by_id(
    db,
    sample_id: int
):
    row = db.execute(
        text("""
            SELECT *
            FROM oil_lab.sample_results
            WHERE id = :id
        """),
        {"id": sample_id}
    ).first()

    if not row:
        return None

    return row_to_dict(row)


def get_samples_by_unit(
    db,
    unit_id: str,
    page: int,
    page_size: int
):
    offset = (page - 1) * page_size

    total = db.execute(
        text("""
            SELECT COUNT(*)
            FROM oil_lab.sample_results
            WHERE unit_id = :unit_id
        """),
        {"unit_id": unit_id}
    ).scalar()

    rows = db.execute(
        text("""
            SELECT *
            FROM oil_lab.sample_results
            WHERE unit_id = :unit_id
            ORDER BY sample_date DESC
            LIMIT :limit
            OFFSET :offset
        """),
        {
            "unit_id": unit_id,
            "limit": page_size,
            "offset": offset
        }
    )

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [
            row_to_dict(row)
            for row in rows
        ]
    }


def get_samples_by_vessel(
    db,
    vesselid: str,
    page: int,
    page_size: int
):
    offset = (page - 1) * page_size

    total = db.execute(
        text("""
            SELECT COUNT(*)
            FROM oil_lab.sample_results
            WHERE vesselid = :vesselid
        """),
        {"vesselid": vesselid}
    ).scalar()

    rows = db.execute(
        text("""
            SELECT *
            FROM oil_lab.sample_results
            WHERE vesselid = :vesselid
            ORDER BY sample_date DESC
            LIMIT :limit
            OFFSET :offset
        """),
        {
            "vesselid": vesselid,
            "limit": page_size,
            "offset": offset
        }
    )

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [
            row_to_dict(row)
            for row in rows
        ]
    }

def get_stats(
    db,
    vessel: str = None,
    unit: str = None,
    date_from: str = None,
    date_to: str = None
):
    wheres = []
    if vessel:
        wheres.append(f"LOWER(vesselid) LIKE '%' || LOWER(:vessel) || '%'")
    if unit:
        wheres.append("LOWER(unit_id) = LOWER(:unit)")
    if date_from:
        wheres.append("sample_date >= :date_from")
    if date_to:
        wheres.append("sample_date <= :date_to")

    where_clause = ('WHERE ' + ' AND '.join(wheres)) if wheres else ''

    params = {}
    if vessel: params['vessel'] = vessel
    if unit: params['unit'] = unit
    if date_from: params['date_from'] = date_from
    if date_to: params['date_to'] = date_to

    row = db.execute(
        text(f"""
            SELECT COUNT(*) as total,
                   COUNT(DISTINCT unit_id) as units,
                   COUNT(DISTINCT model) as models
            FROM oil_lab.sample_results
            {where_clause}
        """),
        params
    ).first()

    filtered = db.execute(
        text(f"""
            SELECT COUNT(*)
            FROM oil_lab.sample_results
            {where_clause}
        """),
        params
    ).scalar()

    # Date range
    range_row = db.execute(
        text(f"""
            SELECT MIN(sample_date), MAX(sample_date)
            FROM oil_lab.sample_results
            {where_clause}
        """),
        params
    ).first()

    return {
        "total": row[0],
        "units": row[1],
        "models": row[2],
        "filtered": filtered,
        "data_old": range_row[0].isoformat() if range_row[0] else None,
        "data_new": range_row[1].isoformat() if range_row[1] else None
    }


def get_units(
    db,
    vessel: str = None
):
    q = "SELECT DISTINCT unit_id FROM oil_lab.sample_results WHERE unit_id IS NOT NULL AND unit_id != ''"
    params = {}
    if vessel:
        q += " AND LOWER(vesselid) LIKE '%' || LOWER(:vessel) || '%'"
        params['vessel'] = vessel
    q += " ORDER BY unit_id"

    rows = db.execute(text(q), params)
    return [r[0] for r in rows]


def get_filtered_samples(
    db,
    page: int,
    page_size: int,
    vessel: str = None,
    unit: str = None,
    date_from: str = None,
    date_to: str = None
):
    offset = (page - 1) * page_size
    wheres = []
    params = {}
    
    if vessel:
        wheres.append("LOWER(vesselid) LIKE '%' || LOWER(:vessel) || '%'")
        params['vessel'] = vessel
    if unit:
        wheres.append("LOWER(unit_id) = LOWER(:unit)")
        params['unit'] = unit
    if date_from:
        wheres.append("sample_date >= :date_from")
        params['date_from'] = date_from
    if date_to:
        wheres.append("sample_date <= :date_to")
        params['date_to'] = date_to

    where_clause = ('WHERE ' + ' AND '.join(wheres)) if wheres else ''
    params['limit'] = page_size
    params['offset'] = offset

    total = db.execute(
        text(f"SELECT COUNT(*) FROM oil_lab.sample_results {where_clause}"),
        {k:v for k,v in params.items() if k not in ('limit','offset')}
    ).scalar()

    rows = db.execute(
        text(f"""
            SELECT vesselid, unit_id, sample_date, unit_time, unit_time_oils,
                   al, cr, cu, fe, pb, si, na, water,
                   visc, oxi, fuel, tbn, nitr, soot, condition,
                   grade_si, grade_fe, grade_cu, grade_al, grade_c, grade_pb, grade_na,
                   grade_visc, grade_fuel, grade_soot, grade_oxi, grade_nitr, grade_water, grade_tbn

            FROM oil_lab.sample_results
            {where_clause}
            ORDER BY sample_date DESC NULLS LAST
            LIMIT :limit OFFSET :offset
        """),
        params
    )

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [row_to_dict(row) for row in rows]
    }
