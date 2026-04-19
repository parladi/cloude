"""CSV / Excel / Markdown üretici"""
import io
import logging
from typing import Optional

import polars as pl
from tabulate import tabulate

from config import CONFIG

logger = logging.getLogger(__name__)


def to_csv_bytes(df: pl.DataFrame) -> bytes:
    """UTF-8 BOM ile CSV (Excel açılır)"""
    encoding = CONFIG["output"].get("csv_encoding", "utf-8-sig")
    buf = io.BytesIO()
    text = df.write_csv()
    if encoding.lower() == "utf-8-sig":
        buf.write(b"\xef\xbb\xbf")
    buf.write(text.encode("utf-8"))
    return buf.getvalue()


def to_xlsx_bytes(df: pl.DataFrame, sheet_name: str = "Sonuc") -> bytes:
    """XLSX — xlsxwriter motoru"""
    buf = io.BytesIO()
    df.write_excel(workbook=buf, worksheet=sheet_name)
    return buf.getvalue()


def to_markdown(df: pl.DataFrame, title: str = "", sql: str = "",
                database: str = "", duration: Optional[float] = None,
                max_rows: int = 1000) -> str:
    """Claude'a yapıştırmak için Markdown"""
    lines = []

    if title:
        lines.append(f"# {title}\n")

    meta = []
    if database:
        meta.append(f"**Veritabanı:** `{database}`")
    if duration is not None:
        meta.append(f"**Süre:** {duration:.2f} sn")
    meta.append(f"**Satır sayısı:** {len(df)}")
    if meta:
        lines.append(" · ".join(meta) + "\n")

    if sql:
        lines.append("## Sorgu\n")
        lines.append("```sql")
        lines.append(sql.strip())
        lines.append("```\n")

    lines.append("## Sonuç\n")

    display_df = df.head(max_rows) if len(df) > max_rows else df
    if len(df) > max_rows:
        lines.append(f"> İlk {max_rows} satır gösteriliyor (toplam {len(df)})\n")

    if len(display_df) == 0:
        lines.append("_(sonuç boş)_")
    else:
        rows = display_df.to_dicts()
        headers = list(display_df.columns)
        table_data = [[r.get(h, "") for h in headers] for r in rows]
        lines.append(tabulate(table_data, headers=headers, tablefmt="github"))

    return "\n".join(lines)
