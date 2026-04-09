from fastapi import APIRouter, HTTPException

from database import execute_query
from queries.sql_queries import CHANGELOG_COMPARISON

router = APIRouter()


@router.get("/changelog")
def get_changelog():
    """320 ve 321 kaynak vs yedek karsilastirma"""
    try:
        result = execute_query(CHANGELOG_COMPARISON)
        rows = {r["tablo"]: r["sayi"] for r in result["rows"]}

        kaynak_320 = rows.get("320_KAYNAK", 0)
        yedek_320 = rows.get("320_YEDEK", 0)
        kaynak_321 = rows.get("321_KAYNAK", 0)
        yedek_321 = rows.get("321_YEDEK", 0)

        return {
            "firma_320": {
                "kaynak": kaynak_320,
                "yedek": yedek_320,
                "fark": kaynak_320 - yedek_320,
                "ok": kaynak_320 >= yedek_320,
            },
            "firma_321": {
                "kaynak": kaynak_321,
                "yedek": yedek_321,
                "fark": kaynak_321 - yedek_321,
                "ok": kaynak_321 >= yedek_321,
            },
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
