"""Debug sayfası — log + sistem bilgisi"""
import logging
import os
import platform
import sys
from collections import deque

from flask import Blueprint, Response, render_template, request

from config import DATA_DIR, PROJECT_ROOT

logger = logging.getLogger(__name__)
bp = Blueprint("debug", __name__, url_prefix="/debug")


def _package_versions() -> dict:
    packages = ["flask", "pymssql", "polars", "duckdb", "waitress",
                "xlsxwriter", "tabulate", "yaml"]
    out = {}
    for p in packages:
        try:
            mod = __import__(p)
            ver = getattr(mod, "__version__", None) or "?"
        except ImportError:
            ver = "YOK"
        out[p] = ver
    return out


def _vendor_check() -> dict:
    vendor = PROJECT_ROOT / "versions" / "v1" / "static" / "vendor"
    items = {
        "Monaco loader": vendor / "monaco" / "min" / "vs" / "loader.js",
        "Monaco main": vendor / "monaco" / "min" / "vs" / "editor" / "editor.main.js",
        "Tabulator JS": vendor / "tabulator" / "tabulator.min.js",
        "Tabulator CSS": vendor / "tabulator" / "tabulator.min.css",
    }
    out = {}
    for name, path in items.items():
        if path.exists():
            out[name] = {"exists": True, "path": str(path.relative_to(PROJECT_ROOT)), "size": path.stat().st_size}
        else:
            out[name] = {"exists": False, "path": str(path.relative_to(PROJECT_ROOT)), "size": 0}
    return out


@bp.route("/")
def index():
    sys_info = {
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "cwd": os.getcwd(),
        "pid": os.getpid(),
        "executable": sys.executable,
    }

    return render_template(
        "debug.html",
        sys_info=sys_info,
        packages=_package_versions(),
        vendor_check=_vendor_check(),
    )


@bp.route("/log")
def log_tail():
    try:
        lines = int(request.args.get("lines", 300))
    except (ValueError, TypeError):
        lines = 300

    log_path = DATA_DIR / "logs" / "app.log"
    if not log_path.exists():
        return Response("(log dosyasi henuz olusturulmadi)", mimetype="text/plain; charset=utf-8")

    try:
        with open(log_path, "r", encoding="utf-8", errors="replace") as f:
            tail = deque(f, maxlen=lines)
        return Response("".join(tail), mimetype="text/plain; charset=utf-8")
    except Exception as e:
        return Response(f"Log okunamadi: {e}", mimetype="text/plain; charset=utf-8", status=500)
