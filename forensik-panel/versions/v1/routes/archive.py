"""Arşiv blueprint — listeleme, detay, indirme, silme, tekrar çalıştırma"""
import json
import logging
import re
from datetime import datetime

from flask import (Blueprint, Response, abort, flash, jsonify, redirect,
                   render_template, request, url_for)

from config import CONFIG, get_databases
from core.archive import (delete_query, get_query, get_query_df,
                          list_all_queries)
from core.export import to_csv_bytes, to_markdown, to_xlsx_bytes

logger = logging.getLogger(__name__)
bp = Blueprint("archive", __name__, url_prefix="/archive")

MAX_DISPLAY_ROWS = CONFIG.get("arsiv", {}).get("max_display_rows", 1000)


def _json_default(value):
    try:
        return str(value)
    except Exception:
        return None


def _safe_filename(s: str) -> str:
    s = (s or "sorgu").strip()
    s = re.sub(r"[^A-Za-z0-9._-]+", "_", s)
    return s[:80] or "sorgu"


@bp.route("/")
def index():
    filters = {
        "q": request.args.get("q", ""),
        "database": request.args.get("database", ""),
        "date_from": request.args.get("date_from", ""),
        "date_to": request.args.get("date_to", ""),
    }

    queries = list_all_queries(
        search=filters["q"],
        database=filters["database"],
        date_from=filters["date_from"],
        date_to=filters["date_to"],
    )

    return render_template(
        "archive.html",
        queries=queries,
        filters=filters,
        databases=get_databases(),
    )


@bp.route("/<int:query_id>")
def detail(query_id):
    query = get_query(query_id)
    if not query:
        abort(404)

    rows_json = "[]"
    columns_json = "[]"
    has_data = False
    truncated = False
    display_rows = 0

    if query["status"] == "success":
        df = get_query_df(query_id)
        if df is not None and len(df) > 0:
            has_data = True
            display_df = df.head(MAX_DISPLAY_ROWS)
            truncated = len(df) > MAX_DISPLAY_ROWS
            display_rows = len(display_df)

            rows_list = display_df.to_dicts()
            cols_list = [
                {"title": col, "field": col, "headerFilter": "input", "resizable": True}
                for col in display_df.columns
            ]
            rows_json = json.dumps(rows_list, default=_json_default, ensure_ascii=False)
            columns_json = json.dumps(cols_list, ensure_ascii=False)

    return render_template(
        "archive_detail.html",
        query=query,
        has_data=has_data,
        truncated=truncated,
        display_rows=display_rows,
        rows_json=rows_json,
        columns_json=columns_json,
    )


@bp.route("/<int:query_id>/download")
def download(query_id):
    fmt = (request.args.get("format") or "csv").lower()
    query = get_query(query_id)
    if not query:
        abort(404)

    df = get_query_df(query_id)
    if df is None:
        abort(404, "Parquet bulunamadı")

    base = _safe_filename(f"q{query_id:06d}_{query['title']}")
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    if fmt == "csv":
        data = to_csv_bytes(df)
        return Response(
            data,
            mimetype="text/csv; charset=utf-8",
            headers={
                "Content-Disposition": f"attachment; filename={base}_{stamp}.csv",
            },
        )

    if fmt == "xlsx":
        data = to_xlsx_bytes(df)
        return Response(
            data,
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f"attachment; filename={base}_{stamp}.xlsx",
            },
        )

    if fmt == "md":
        text = to_markdown(
            df,
            title=query["title"],
            sql=query["sql"],
            database=query["database"],
            duration=query["duration_sec"],
        )
        return Response(
            text,
            mimetype="text/markdown; charset=utf-8",
            headers={
                "Content-Disposition": f"attachment; filename={base}_{stamp}.md",
            },
        )

    abort(400, "Bilinmeyen format")


@bp.route("/<int:query_id>/rerun")
def rerun(query_id):
    query = get_query(query_id)
    if not query:
        abort(404)
    # SQL editörüne push — query param ile
    return redirect(
        url_for("sql_editor.index", database=query["database"], rerun=query_id)
    )


@bp.route("/<int:query_id>/delete", methods=["POST"])
def delete(query_id):
    ok = delete_query(query_id)
    if not ok:
        flash("Kayıt bulunamadı")
        return redirect(url_for("archive.index"))
    flash(f"Kayıt #{query_id} silindi")
    return redirect(url_for("archive.index"))


@bp.route("/<int:query_id>/sql")
def get_sql(query_id):
    """Tekrar çalıştırma için SQL'i JSON olarak döndür"""
    query = get_query(query_id)
    if not query:
        return jsonify({"error": "not found"}), 404
    return jsonify({
        "id": query["id"],
        "sql": query["sql"],
        "database": query["database"],
        "title": query["title"],
        "description": query["description"],
    })
