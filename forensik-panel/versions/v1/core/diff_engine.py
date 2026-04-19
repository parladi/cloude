"""İki arşiv sorgusunu DuckDB ile karşılaştır"""
import logging
from typing import Optional

import duckdb
import polars as pl

from core.archive import get_query, get_query_df

logger = logging.getLogger(__name__)


def compare_queries(
    left_id: int,
    right_id: int,
    key_columns: Optional[list[str]] = None,
) -> dict:
    """İki arşiv sorgusunu karşılaştır.

    Döndürür: {
        "left": meta dict,
        "right": meta dict,
        "common_columns": [...],
        "key_columns": [...],
        "only_in_left": pl.DataFrame,
        "only_in_right": pl.DataFrame,
        "changed": pl.DataFrame,
        "unchanged_count": int,
        "summary": dict,
    }
    """
    left = get_query(left_id)
    right = get_query(right_id)
    if not left or not right:
        raise ValueError("Arşiv kaydı bulunamadı")

    left_df = get_query_df(left_id)
    right_df = get_query_df(right_id)

    if left_df is None or right_df is None:
        raise ValueError("Sonuç dosyası yok (parquet kayıp)")

    common = [c for c in left_df.columns if c in right_df.columns]
    if not common:
        raise ValueError("Ortak kolon yok — karşılaştırılamaz")

    if not key_columns:
        key_columns = [common[0]]
    else:
        key_columns = [c for c in key_columns if c in common]
        if not key_columns:
            key_columns = [common[0]]

    value_columns = [c for c in common if c not in key_columns]

    left_slim = left_df.select(common)
    right_slim = right_df.select(common)

    # DuckDB register et
    conn = duckdb.connect(":memory:")
    try:
        conn.register("L", left_slim.to_pandas())
        conn.register("R", right_slim.to_pandas())

        key_clause = " AND ".join([f'L."{k}" = R."{k}"' for k in key_columns])
        key_select_l = ", ".join([f'L."{k}"' for k in key_columns])
        key_select_r = ", ".join([f'R."{k}"' for k in key_columns])

        only_left_sql = f"""
            SELECT L.* FROM L
            LEFT JOIN R ON {key_clause}
            WHERE {' AND '.join([f'R."{k}" IS NULL' for k in key_columns])}
        """
        only_right_sql = f"""
            SELECT R.* FROM R
            LEFT JOIN L ON {key_clause}
            WHERE {' AND '.join([f'L."{k}" IS NULL' for k in key_columns])}
        """

        only_in_left = pl.from_pandas(conn.execute(only_left_sql).fetch_df())
        only_in_right = pl.from_pandas(conn.execute(only_right_sql).fetch_df())

        # Değişenler
        if value_columns:
            change_conds = " OR ".join([
                f'COALESCE(CAST(L."{c}" AS VARCHAR), \'\') <> COALESCE(CAST(R."{c}" AS VARCHAR), \'\')'
                for c in value_columns
            ])
            changed_cols = ", ".join([f'L."{c}" AS "L_{c}", R."{c}" AS "R_{c}"' for c in value_columns])
            changed_sql = f"""
                SELECT {key_select_l}, {changed_cols}
                FROM L
                INNER JOIN R ON {key_clause}
                WHERE {change_conds}
            """
            changed = pl.from_pandas(conn.execute(changed_sql).fetch_df())
        else:
            changed = pl.DataFrame()

        matched_sql = f"""
            SELECT COUNT(*) FROM L INNER JOIN R ON {key_clause}
        """
        matched_count = conn.execute(matched_sql).fetchone()[0]
        unchanged_count = matched_count - len(changed)
    finally:
        conn.close()

    return {
        "left": left,
        "right": right,
        "common_columns": common,
        "key_columns": key_columns,
        "value_columns": value_columns,
        "only_in_left": only_in_left,
        "only_in_right": only_in_right,
        "changed": changed,
        "unchanged_count": unchanged_count,
        "summary": {
            "left_total": len(left_df),
            "right_total": len(right_df),
            "only_in_left": len(only_in_left),
            "only_in_right": len(only_in_right),
            "changed": len(changed),
            "unchanged": unchanged_count,
        },
    }
