"""SQL Editör blueprint — çalıştırma + arşivleme"""
import json
import logging

from flask import Blueprint, render_template, request

from config import CONFIG, get_databases, get_default_database
from core.archive import save_query
from core.sql_executor import execute_sql

logger = logging.getLogger(__name__)
bp = Blueprint("sql_editor", __name__, url_prefix="/sql")

MAX_DISPLAY_ROWS = CONFIG.get("arsiv", {}).get("max_display_rows", 1000)


def _json_default(value):
    """Datetime/Decimal vb. string'e düşür"""
    try:
        return str(value)
    except Exception:
        return None


@bp.route("/")
def index():
    selected = request.args.get("database") or get_default_database()
    rerun_id = request.args.get("rerun")
    rerun_sql = ""
    rerun_title = ""
    rerun_desc = ""

    if rerun_id:
        from core.archive import get_query
        try:
            q = get_query(int(rerun_id))
            if q:
                rerun_sql = q["sql"] or ""
                rerun_title = q["title"] or ""
                rerun_desc = q["description"] or ""
                selected = q["database"] or selected
        except (ValueError, TypeError):
            pass

    return render_template(
        "sql_editor.html",
        databases=get_databases(),
        selected_db=selected,
        rerun_sql=rerun_sql,
        rerun_title=rerun_title,
        rerun_desc=rerun_desc,
    )


@bp.route("/execute", methods=["POST"])
def execute():
    sql = (request.form.get("sql") or "").strip()
    database = (request.form.get("database") or "").strip()
    title = (request.form.get("title") or "").strip()
    description = (request.form.get("description") or "").strip()

    logger.info(f"SQL execute isteği: db={database}, başlık={title!r}")

    if not sql:
        return render_template(
            "partials/_sql_result.html",
            status="error",
            error="SQL boş olamaz",
        ), 400

    if not database:
        return render_template(
            "partials/_sql_result.html",
            status="error",
            error="Veritabanı seçilmedi",
        ), 400

    try:
        df, duration = execute_sql(database, sql, timeout=CONFIG["sql_server"].get("query_timeout", 600))
        total_rows = len(df)

        query_id = save_query(
            title=title or "Başlıksız",
            description=description,
            sql=sql,
            database=database,
            df=df,
            duration=duration,
            status="success",
        )

        display_df = df.head(MAX_DISPLAY_ROWS)
        truncated = total_rows > MAX_DISPLAY_ROWS

        rows_list = display_df.to_dicts()
        cols_list = [
            {"title": col, "field": col, "headerFilter": "input", "resizable": True}
            for col in display_df.columns
        ]

        return render_template(
            "partials/_sql_result.html",
            status="success",
            duration=duration,
            total_rows=total_rows,
            display_rows=len(display_df),
            truncated=truncated,
            query_id=query_id,
            rows_json=json.dumps(rows_list, default=_json_default, ensure_ascii=False),
            columns_json=json.dumps(cols_list, ensure_ascii=False),
        )

    except ValueError as e:
        logger.warning(f"Güvenlik reddi: {e}")
        return render_template(
            "partials/_sql_result.html",
            status="error",
            error=str(e),
        ), 400

    except Exception as e:
        logger.exception("SQL hatası")

        try:
            save_query(
                title=title or "Hatalı sorgu",
                description=description,
                sql=sql,
                database=database,
                df=None,
                duration=0,
                status="error",
                error_message=str(e),
            )
        except Exception:
            pass

        return render_template(
            "partials/_sql_result.html",
            status="error",
            error=str(e),
        ), 500
