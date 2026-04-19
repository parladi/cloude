"""Panel (ana sayfa)"""
import logging

from flask import Blueprint, render_template

from core.archive import count_queries, list_recent_queries
from core.db import test_connection

logger = logging.getLogger(__name__)
bp = Blueprint("dashboard", __name__)


@bp.route("/")
def index():
    try:
        conn_test = test_connection()
    except Exception as e:
        logger.exception("test_connection çağrısı başarısız")
        conn_test = {"status": "error", "error": str(e)}

    try:
        count = count_queries()
    except Exception:
        logger.exception("count_queries başarısız")
        count = 0

    try:
        recent = list_recent_queries(limit=10)
    except Exception:
        logger.exception("list_recent_queries başarısız")
        recent = []

    return render_template(
        "dashboard.html",
        connection_ok=(conn_test.get("status") == "ok"),
        connection_error=conn_test.get("error", ""),
        archive_count=count,
        recent_queries=recent,
    )
