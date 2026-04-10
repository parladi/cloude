from fastapi import APIRouter, HTTPException, Query
from database import execute_query
from queries.sql_queries import COMPUTER_DISTRIBUTION, DELETION_COUNTS, RECENT_ALL_DELETIONS, TABLE_QUERIES

router = APIRouter()


def serialize_rows(rows):
    for row in rows:
        for key, val in row.items():
            if hasattr(val, "isoformat"):
                row[key] = val.isoformat()
    return rows


@router.get("/deletions/summary")
def deletion_summary():
    try:
        return {"tables": execute_query(DELETION_COUNTS)["rows"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/deletions/recent")
def recent_deletions(limit: int = Query(default=20, le=200)):
    try:
        r = execute_query(RECENT_ALL_DELETIONS.format(limit=limit))
        return {"columns": r["columns"], "rows": serialize_rows(r["rows"]), "row_count": r["row_count"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/deletions/by-computer")
def deletions_by_computer():
    try:
        return {"computers": serialize_rows(execute_query(COMPUTER_DISTRIBUTION)["rows"])}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/deletions/{table_name}")
def deletion_detail(table_name: str, limit: int = Query(default=50, le=500)):
    t = table_name.upper()
    if t not in TABLE_QUERIES:
        raise HTTPException(status_code=404, detail=f"Tablo bulunamadi: {table_name}")
    try:
        r = execute_query(TABLE_QUERIES[t].format(limit=limit))
        return {"table": t, "columns": r["columns"], "rows": serialize_rows(r["rows"]), "row_count": r["row_count"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
