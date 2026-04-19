"""Karşılaştırma blueprint"""
import json
import logging

from flask import Blueprint, render_template, request

from core.archive import list_all_queries
from core.diff_engine import compare_queries

logger = logging.getLogger(__name__)
bp = Blueprint("diff", __name__, url_prefix="/diff")

MAX_PREVIEW_ROWS = 500


def _json_default(value):
    try:
        return str(value)
    except Exception:
        return None


@bp.route("/")
def index():
    left = request.args.get("left", "").strip()
    right = request.args.get("right", "").strip()
    key = request.args.get("key", "").strip()

    filters = {"left": left, "right": right, "key": key}
    queries = list_all_queries()

    result = None
    error = None
    only_left_json = "[]"
    only_right_json = "[]"
    changed_json = "[]"

    if left and right:
        try:
            key_cols = [k.strip() for k in key.split(",") if k.strip()] if key else None
            result = compare_queries(int(left), int(right), key_columns=key_cols)

            only_left_json = json.dumps(
                result["only_in_left"].head(MAX_PREVIEW_ROWS).to_dicts(),
                default=_json_default, ensure_ascii=False,
            )
            only_right_json = json.dumps(
                result["only_in_right"].head(MAX_PREVIEW_ROWS).to_dicts(),
                default=_json_default, ensure_ascii=False,
            )
            changed_json = json.dumps(
                result["changed"].head(MAX_PREVIEW_ROWS).to_dicts(),
                default=_json_default, ensure_ascii=False,
            )
        except ValueError as e:
            error = str(e)
        except Exception as e:
            logger.exception("diff hatasi")
            error = str(e)

    return render_template(
        "diff.html",
        queries=queries,
        filters=filters,
        result=result,
        error=error,
        only_in_left_json=only_left_json,
        only_in_right_json=only_right_json,
        changed_json=changed_json,
    )
