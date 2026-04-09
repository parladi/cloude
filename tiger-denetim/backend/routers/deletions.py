from fastapi import APIRouter, HTTPException, Query

from database import execute_query
from queries.sql_queries import (
    COMPUTER_DISTRIBUTION,
    DELETION_COUNTS,
    RECENT_ALL_DELETIONS,
    TABLE_QUERIES,
)

router = APIRouter()


def serialize_rows(rows):
    """datetime nesnelerini string'e cevir"""
    for row in rows:
        for key, val in row.items():
            if hasattr(val, "isoformat"):
                row[key] = val.isoformat()
    return rows


@router.get("/deletions/summary")
def deletion_summary():
    """18 yedek tablodaki toplam silme sayilari"""
    try:
        result = execute_query(DELETION_COUNTS)
        return {"tables": result["rows"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/deletions/recent")
def recent_deletions(limit: int = Query(default=20, le=200)):
    """Tum tablolardan son silmeler"""
    try:
        sql = RECENT_ALL_DELETIONS.format(limit=limit)
        result = execute_query(sql)
        return {
            "columns": result["columns"],
            "rows": serialize_rows(result["rows"]),
            "row_count": result["row_count"],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/deletions/by-computer")
def deletions_by_computer():
    """Bilgisayar bazli silme dagilimi"""
    try:
        result = execute_query(COMPUTER_DISTRIBUTION)
        return {
            "computers": serialize_rows(result["rows"]),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/deletions/{table_name}")
def deletion_detail(table_name: str, limit: int = Query(default=50, le=500)):
    """Secilen tablonun silme detaylari"""
    table_upper = table_name.upper()
    if table_upper not in TABLE_QUERIES:
        raise HTTPException(
            status_code=404,
            detail=f"Tablo bulunamadi: {table_name}. Gecerli tablolar: {', '.join(TABLE_QUERIES.keys())}",
        )
    try:
        sql = TABLE_QUERIES[table_upper].format(limit=limit)
        result = execute_query(sql)
        return {
            "table": table_upper,
            "columns": result["columns"],
            "rows": serialize_rows(result["rows"]),
            "row_count": result["row_count"],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
