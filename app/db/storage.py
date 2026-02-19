"""
SQLite depolama modülü.
Veritabanı şeması ve CRUD operasyonları.
"""
import sqlite3
import os
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

# Bağlantı; her çağrıda yeni oluşturuluyor (Streamlit thread-safe için)
def _conn(db_path: str) -> sqlite3.Connection:
    con = sqlite3.connect(db_path, check_same_thread=False)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA journal_mode=WAL")
    con.execute("PRAGMA synchronous=NORMAL")
    return con


# ─── ŞEMA OLUŞTURMA ──────────────────────────────────────────────────────────

SCHEMA = """
CREATE TABLE IF NOT EXISTS auth (
    user          TEXT PRIMARY KEY,
    password_hash TEXT NOT NULL,
    created_at    TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS meta (
    key   TEXT PRIMARY KEY,
    value TEXT
);

CREATE TABLE IF NOT EXISTS documents (
    doc_id           TEXT PRIMARY KEY,
    doc_type         TEXT,          -- DESPATCH / INVOICE
    doc_no           TEXT,
    issue_date       TEXT,
    ship_date        TEXT,
    sender_vkn       TEXT,
    receiver_vkn     TEXT,
    currency         TEXT,
    plate            TEXT,
    driver           TEXT,
    depot            TEXT,
    doc_total        REAL,
    has_embedded_pdf INTEGER DEFAULT 0,
    embedded_pdf_path TEXT,
    file_path        TEXT,
    file_hash        TEXT UNIQUE,
    created_at       TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS lines (
    line_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    doc_id       TEXT REFERENCES documents(doc_id),
    item_code    TEXT,
    item_name    TEXT,
    quantity     REAL,
    unit         TEXT,
    net          REAL,
    gross        REAL,
    lot_or_serial TEXT,
    line_amount  REAL
);

CREATE TABLE IF NOT EXISTS errors (
    err_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    file_path     TEXT,
    file_name     TEXT,
    file_hash     TEXT,
    error_message TEXT,
    created_at    TEXT DEFAULT (datetime('now'))
);

-- İndeksler
CREATE INDEX IF NOT EXISTS idx_doc_issue_date  ON documents(issue_date);
CREATE INDEX IF NOT EXISTS idx_doc_no          ON documents(doc_no);
CREATE INDEX IF NOT EXISTS idx_doc_sender      ON documents(sender_vkn);
CREATE INDEX IF NOT EXISTS idx_doc_receiver    ON documents(receiver_vkn);
CREATE INDEX IF NOT EXISTS idx_doc_total       ON documents(doc_total);
CREATE INDEX IF NOT EXISTS idx_line_code       ON lines(item_code);
CREATE INDEX IF NOT EXISTS idx_line_name       ON lines(item_name);
CREATE INDEX IF NOT EXISTS idx_line_doc        ON lines(doc_id);
"""


def init_db(db_path: str) -> None:
    """Veritabanını ve tabloları oluşturur."""
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    with _conn(db_path) as con:
        con.executescript(SCHEMA)


# ─── AUTH ────────────────────────────────────────────────────────────────────

def get_user(db_path: str, username: str) -> Optional[sqlite3.Row]:
    with _conn(db_path) as con:
        return con.execute(
            "SELECT * FROM auth WHERE user = ?", (username,)
        ).fetchone()


def create_user(db_path: str, username: str, password_hash: str) -> None:
    with _conn(db_path) as con:
        con.execute(
            "INSERT INTO auth(user, password_hash) VALUES(?,?)",
            (username, password_hash),
        )


def update_password(db_path: str, username: str, password_hash: str) -> None:
    with _conn(db_path) as con:
        con.execute(
            "UPDATE auth SET password_hash=? WHERE user=?",
            (password_hash, username),
        )


def user_exists(db_path: str) -> bool:
    with _conn(db_path) as con:
        row = con.execute("SELECT COUNT(*) FROM auth").fetchone()
        return row[0] > 0


# ─── META ────────────────────────────────────────────────────────────────────

def set_meta(db_path: str, key: str, value: str) -> None:
    with _conn(db_path) as con:
        con.execute(
            "INSERT OR REPLACE INTO meta(key, value) VALUES(?,?)", (key, value)
        )


def get_meta(db_path: str, key: str) -> Optional[str]:
    with _conn(db_path) as con:
        row = con.execute("SELECT value FROM meta WHERE key=?", (key,)).fetchone()
        return row[0] if row else None


# ─── HASH KONTROLÜ ───────────────────────────────────────────────────────────

def hash_exists(db_path: str, file_hash: str) -> bool:
    """Bu hash daha önce işlendi mi?"""
    with _conn(db_path) as con:
        row = con.execute(
            "SELECT 1 FROM documents WHERE file_hash=? LIMIT 1", (file_hash,)
        ).fetchone()
        if row:
            return True
        row = con.execute(
            "SELECT 1 FROM errors WHERE file_hash=? LIMIT 1", (file_hash,)
        ).fetchone()
        return row is not None


# ─── BELGE KAYDETME ──────────────────────────────────────────────────────────

def insert_doc(db_path: str, doc: Dict[str, Any]) -> None:
    """Bir belgeyi documents tablosuna ekler."""
    with _conn(db_path) as con:
        con.execute(
            """INSERT OR REPLACE INTO documents
               (doc_id, doc_type, doc_no, issue_date, ship_date,
                sender_vkn, receiver_vkn, currency, plate, driver, depot,
                doc_total, has_embedded_pdf, embedded_pdf_path,
                file_path, file_hash)
               VALUES
               (:doc_id,:doc_type,:doc_no,:issue_date,:ship_date,
                :sender_vkn,:receiver_vkn,:currency,:plate,:driver,:depot,
                :doc_total,:has_embedded_pdf,:embedded_pdf_path,
                :file_path,:file_hash)""",
            doc,
        )


def insert_lines(db_path: str, lines: List[Dict[str, Any]]) -> None:
    """Belge kalemlerini toplu ekler."""
    with _conn(db_path) as con:
        con.executemany(
            """INSERT INTO lines
               (doc_id, item_code, item_name, quantity, unit,
                net, gross, lot_or_serial, line_amount)
               VALUES
               (:doc_id,:item_code,:item_name,:quantity,:unit,
                :net,:gross,:lot_or_serial,:line_amount)""",
            lines,
        )


def log_error(db_path: str, file_path: str, file_hash: str, error_message: str) -> None:
    file_name = os.path.basename(file_path.split("::")[-1])
    with _conn(db_path) as con:
        con.execute(
            """INSERT INTO errors(file_path, file_name, file_hash, error_message)
               VALUES(?,?,?,?)""",
            (file_path, file_name, file_hash, error_message),
        )


# ─── SORGULAMA ───────────────────────────────────────────────────────────────

def query_filtered(
    db_path: str,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    vkn: Optional[str] = None,
    doc_no: Optional[str] = None,
    item_code: Optional[str] = None,
    item_name: Optional[str] = None,
    depot: Optional[str] = None,
    currency: Optional[str] = None,
    plate: Optional[str] = None,
    driver: Optional[str] = None,
    total_min: Optional[float] = None,
    total_max: Optional[float] = None,
    doc_type: Optional[str] = None,
    limit: int = 5000,
    offset: int = 0,
) -> List[Dict]:
    """
    Filtrelenmiş sonuçları döner.
    Her satır bir line kaydına karşılık gelir (documents JOIN lines).
    """
    params: List[Any] = []
    where: List[str] = []

    if date_from:
        where.append("d.issue_date >= ?"); params.append(date_from)
    if date_to:
        where.append("d.issue_date <= ?"); params.append(date_to)
    if vkn:
        where.append("(d.sender_vkn LIKE ? OR d.receiver_vkn LIKE ?)")
        params += [f"%{vkn}%", f"%{vkn}%"]
    if doc_no:
        where.append("d.doc_no LIKE ?"); params.append(f"%{doc_no}%")
    if item_code:
        where.append("l.item_code LIKE ?"); params.append(f"%{item_code}%")
    if item_name:
        where.append("l.item_name LIKE ?"); params.append(f"%{item_name}%")
    if depot:
        where.append("d.depot LIKE ?"); params.append(f"%{depot}%")
    if currency:
        where.append("d.currency = ?"); params.append(currency)
    if plate:
        where.append("d.plate LIKE ?"); params.append(f"%{plate}%")
    if driver:
        where.append("d.driver LIKE ?"); params.append(f"%{driver}%")
    if total_min is not None:
        where.append("d.doc_total >= ?"); params.append(total_min)
    if total_max is not None:
        where.append("d.doc_total <= ?"); params.append(total_max)
    if doc_type:
        where.append("d.doc_type = ?"); params.append(doc_type)

    where_sql = ("WHERE " + " AND ".join(where)) if where else ""

    sql = f"""
        SELECT
            d.doc_type      AS DOC_TYPE,
            d.doc_no        AS DOC_NO,
            d.issue_date    AS ISSUE_DATE,
            d.ship_date     AS SHIP_DATE,
            d.sender_vkn    AS SENDER_VKN_TCKN,
            d.receiver_vkn  AS RECEIVER_VKN_TCKN,
            l.item_code     AS ITEM_CODE,
            l.item_name     AS ITEM_NAME,
            l.quantity      AS QUANTITY,
            l.unit          AS UNIT,
            l.net           AS NET,
            l.gross         AS GROSS,
            d.depot         AS DEPOT_OR_BRANCH,
            d.plate         AS PLATE,
            d.driver        AS DRIVER,
            l.lot_or_serial AS LOT_OR_SERIAL,
            d.currency      AS CURRENCY,
            d.doc_total     AS DOC_TOTAL,
            d.doc_id        AS DOC_ID,
            d.file_path     AS FILE_PATH,
            d.file_hash     AS HASH
        FROM documents d
        LEFT JOIN lines l ON l.doc_id = d.doc_id
        {where_sql}
        ORDER BY d.issue_date DESC, d.doc_no
        LIMIT ? OFFSET ?
    """
    params += [limit, offset]

    with _conn(db_path) as con:
        rows = con.execute(sql, params).fetchall()
        return [dict(r) for r in rows]


def count_filtered(
    db_path: str,
    date_from=None, date_to=None, vkn=None, doc_no=None,
    item_code=None, item_name=None, depot=None, currency=None,
    plate=None, driver=None, total_min=None, total_max=None, doc_type=None,
) -> int:
    """Filtreli toplam satır sayısı."""
    params: List[Any] = []
    where: List[str] = []

    if date_from:
        where.append("d.issue_date >= ?"); params.append(date_from)
    if date_to:
        where.append("d.issue_date <= ?"); params.append(date_to)
    if vkn:
        where.append("(d.sender_vkn LIKE ? OR d.receiver_vkn LIKE ?)")
        params += [f"%{vkn}%", f"%{vkn}%"]
    if doc_no:
        where.append("d.doc_no LIKE ?"); params.append(f"%{doc_no}%")
    if item_code:
        where.append("l.item_code LIKE ?"); params.append(f"%{item_code}%")
    if item_name:
        where.append("l.item_name LIKE ?"); params.append(f"%{item_name}%")
    if depot:
        where.append("d.depot LIKE ?"); params.append(f"%{depot}%")
    if currency:
        where.append("d.currency = ?"); params.append(currency)
    if plate:
        where.append("d.plate LIKE ?"); params.append(f"%{plate}%")
    if driver:
        where.append("d.driver LIKE ?"); params.append(f"%{driver}%")
    if total_min is not None:
        where.append("d.doc_total >= ?"); params.append(total_min)
    if total_max is not None:
        where.append("d.doc_total <= ?"); params.append(total_max)
    if doc_type:
        where.append("d.doc_type = ?"); params.append(doc_type)

    where_sql = ("WHERE " + " AND ".join(where)) if where else ""
    sql = f"""
        SELECT COUNT(*) FROM documents d
        LEFT JOIN lines l ON l.doc_id = d.doc_id
        {where_sql}
    """
    with _conn(db_path) as con:
        row = con.execute(sql, params).fetchone()
        return row[0] if row else 0


def get_doc(db_path: str, doc_id: str) -> Optional[Dict]:
    with _conn(db_path) as con:
        row = con.execute(
            "SELECT * FROM documents WHERE doc_id=?", (doc_id,)
        ).fetchone()
        return dict(row) if row else None


def get_lines(db_path: str, doc_id: str) -> List[Dict]:
    with _conn(db_path) as con:
        rows = con.execute(
            "SELECT * FROM lines WHERE doc_id=? ORDER BY line_id", (doc_id,)
        ).fetchall()
        return [dict(r) for r in rows]


def get_errors(db_path: str) -> List[Dict]:
    with _conn(db_path) as con:
        rows = con.execute(
            "SELECT * FROM errors ORDER BY created_at DESC"
        ).fetchall()
        return [dict(r) for r in rows]


def clear_all(db_path: str) -> None:
    """Tüm indeksleme verilerini siler (auth ve meta hariç)."""
    with _conn(db_path) as con:
        con.executescript("""
            DELETE FROM lines;
            DELETE FROM documents;
            DELETE FROM errors;
        """)


def get_stats(db_path: str) -> Dict[str, int]:
    with _conn(db_path) as con:
        docs = con.execute("SELECT COUNT(*) FROM documents").fetchone()[0]
        lines = con.execute("SELECT COUNT(*) FROM lines").fetchone()[0]
        errs = con.execute("SELECT COUNT(*) FROM errors").fetchone()[0]
        return {"belgeler": docs, "kalemler": lines, "hatalar": errs}


def get_distinct_currencies(db_path: str) -> List[str]:
    with _conn(db_path) as con:
        rows = con.execute(
            "SELECT DISTINCT currency FROM documents WHERE currency != '' ORDER BY currency"
        ).fetchall()
        return [r[0] for r in rows]
