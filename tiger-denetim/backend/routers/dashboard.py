from datetime import datetime

from fastapi import APIRouter, HTTPException

from database import execute_query
from queries.sql_queries import DELETION_COUNTS, RECENT_ALL_DELETIONS, TRIGGERS_STATUS

router = APIRouter()


@router.get("/health")
def health():
    """Backend ve SQL Server baglanti durumu"""
    try:
        result = execute_query("SELECT 1 AS ok")
        return {
            "status": "ok",
            "connected": True,
            "timestamp": datetime.now().isoformat(),
            "server": "192.168.0.9",
            "database": "TIGERDB",
        }
    except Exception as e:
        return {
            "status": "error",
            "connected": False,
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
        }


@router.get("/summary")
def summary():
    """Tum sayfalar icin ozet veriler"""
    try:
        # Trigger durumu
        triggers_result = execute_query(TRIGGERS_STATUS)
        trigger_rows = triggers_result["rows"]
        active_count = sum(1 for t in trigger_rows if t["durum"] == "AKTIF")
        disabled = [t["trigger_adi"] for t in trigger_rows if t["durum"] == "KAPALI"]

        # Silme sayilari
        deletions_result = execute_query(DELETION_COUNTS)
        deletion_rows = deletions_result["rows"]
        total_deletions = sum(r["sayi"] for r in deletion_rows)

        # Changelog - ayri try/catch ile
        changelog_data = {"firm320_ok": None, "firm321_ok": None}
        try:
            from queries.sql_queries import CHANGELOG_COMPARISON

            cl_result = execute_query(CHANGELOG_COMPARISON)
            cl_rows = {r["tablo"]: r["sayi"] for r in cl_result["rows"]}
            changelog_data["firm320_ok"] = cl_rows.get("320_KAYNAK", 0) >= cl_rows.get(
                "320_YEDEK", 0
            )
            changelog_data["firm321_ok"] = cl_rows.get("321_KAYNAK", 0) >= cl_rows.get(
                "321_YEDEK", 0
            )
        except Exception:
            pass

        # Job durumu
        jobs_data = {"active": 0, "total": 0, "last_run": None}
        try:
            from queries.sql_queries import JOBS_STATUS

            jobs_result = execute_query(JOBS_STATUS, database="msdb")
            job_rows = jobs_result["rows"]
            jobs_data["total"] = len(job_rows)
            jobs_data["active"] = sum(1 for j in job_rows if j["durum"] == "AKTIF")
            if job_rows:
                jobs_data["last_run"] = str(job_rows[0].get("tarih", ""))
        except Exception:
            pass

        return {
            "connected": True,
            "timestamp": datetime.now().isoformat(),
            "triggers": {
                "active": active_count,
                "total": len(trigger_rows),
                "disabled": disabled,
            },
            "deletions": {
                "total": total_deletions,
                "by_table": [
                    {"kategori": r["kategori"], "sayi": r["sayi"]}
                    for r in deletion_rows
                ],
            },
            "changelog": changelog_data,
            "jobs": jobs_data,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
