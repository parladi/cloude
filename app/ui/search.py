"""
Arama/Filtre sekmesi.
Sol: filtre paneli, Orta: sonuç tablosu, Sağ: önizleme paneli.
"""
import io
from datetime import date, timedelta
from typing import Any, Dict, List, Optional

import pandas as pd
import streamlit as st

from app.db import storage
from app.ui.preview import show_preview

EXCEL_ROW_LIMIT = 1_048_576
PAGE_SIZE = 200  # Sayfa başına gösterilecek satır


def show_search(db_path: str) -> None:
    st.header("Arama / Filtre")

    # ── FİLTRE PANELİ ─────────────────────────────────────────────────────
    with st.expander("Filtreler", expanded=True):
        fc1, fc2, fc3, fc4 = st.columns(4)

        with fc1:
            date_from = st.date_input(
                "Tarih Başlangıç",
                value=date.today() - timedelta(days=365),
                key="f_date_from",
            )
            date_to = st.date_input("Tarih Bitiş", value=date.today(), key="f_date_to")

        with fc2:
            doc_type = st.selectbox(
                "Belge Tipi",
                options=["", "DESPATCH", "INVOICE"],
                format_func=lambda x: {"": "Tümü", "DESPATCH": "e-İrsaliye", "INVOICE": "e-Fatura"}.get(x, x),
                key="f_doc_type",
            )
            currencies = [""] + storage.get_distinct_currencies(db_path)
            currency = st.selectbox("Para Birimi", options=currencies, key="f_currency")

        with fc3:
            vkn = st.text_input("VKN/TCKN (gönderici veya alıcı)", key="f_vkn")
            doc_no = st.text_input("Belge No", key="f_doc_no")

        with fc4:
            item_code = st.text_input("Malzeme Kodu", key="f_item_code")
            item_name = st.text_input("Malzeme Adı", key="f_item_name")

        fc5, fc6, fc7 = st.columns(3)
        with fc5:
            depot = st.text_input("Depo/Şube", key="f_depot")
        with fc6:
            plate = st.text_input("Plaka", key="f_plate")
            driver = st.text_input("Sürücü", key="f_driver")
        with fc7:
            total_min = st.number_input("Min Tutar", value=0.0, step=100.0, key="f_total_min")
            total_max = st.number_input("Max Tutar", value=0.0, step=100.0, key="f_total_max",
                                        help="0 girilirse üst limit uygulanmaz.")

        search_btn = st.button("Ara", type="primary")
        clear_btn = st.button("Filtreleri Temizle")

    if clear_btn:
        for key in ["f_date_from", "f_date_to", "f_doc_type", "f_currency",
                    "f_vkn", "f_doc_no", "f_item_code", "f_item_name",
                    "f_depot", "f_plate", "f_driver", "f_total_min", "f_total_max",
                    "search_results", "search_total"]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

    # ── ARAMA YÜRÜT ───────────────────────────────────────────────────────
    if search_btn:
        st.session_state["search_page"] = 0
        _run_search(db_path, date_from, date_to, doc_type, currency, vkn, doc_no,
                    item_code, item_name, depot, plate, driver, total_min, total_max)

    # ── SONUÇ TABLOSU + PREVIEW ───────────────────────────────────────────
    if "search_results" not in st.session_state:
        st.info("Filtre uygulayıp 'Ara' butonuna tıklayın.")
        return

    results: List[Dict] = st.session_state["search_results"]
    total: int = st.session_state.get("search_total", len(results))

    if not results:
        st.warning("Sonuç bulunamadı.")
        return

    st.caption(f"**{total:,}** satır bulundu (gösterilen: {len(results):,})")

    # Sayfalama
    page = st.session_state.get("search_page", 0)
    col_prev, col_info, col_next = st.columns([1, 2, 1])
    total_pages = max(1, (len(results) + PAGE_SIZE - 1) // PAGE_SIZE)
    with col_prev:
        if st.button("◀ Önceki") and page > 0:
            st.session_state["search_page"] = page - 1
            st.rerun()
    with col_info:
        st.caption(f"Sayfa {page+1} / {total_pages}")
    with col_next:
        if st.button("Sonraki ▶") and page < total_pages - 1:
            st.session_state["search_page"] = page + 1
            st.rerun()

    start = page * PAGE_SIZE
    end = start + PAGE_SIZE
    page_data = results[start:end]

    # ── İKİ KOLON: TABLO | PREVIEW ────────────────────────────────────────
    tbl_col, prev_col = st.columns([3, 2])

    with tbl_col:
        # Gösterim için DOC_ID ve FILE_PATH gizle
        display_cols = [
            "DOC_TYPE", "DOC_NO", "ISSUE_DATE", "SHIP_DATE",
            "SENDER_VKN_TCKN", "RECEIVER_VKN_TCKN",
            "ITEM_CODE", "ITEM_NAME", "QUANTITY", "UNIT",
            "NET", "GROSS", "DEPOT_OR_BRANCH", "PLATE", "DRIVER",
            "LOT_OR_SERIAL", "CURRENCY", "DOC_TOTAL",
        ]
        df_display = pd.DataFrame(page_data)
        existing_cols = [c for c in display_cols if c in df_display.columns]
        df_display = df_display[existing_cols]

        # Sayısal formatlama
        for num_col in ["NET", "GROSS", "DOC_TOTAL", "QUANTITY"]:
            if num_col in df_display.columns:
                df_display[num_col] = pd.to_numeric(df_display[num_col], errors="coerce")

        event = st.dataframe(
            df_display,
            use_container_width=True,
            height=420,
            on_select="rerun",
            selection_mode="single-row",
            key="result_table",
        )

        selected_rows = event.selection.get("rows", []) if event.selection else []

        # Export butonu
        _export_section(db_path, results, total)

    with prev_col:
        if selected_rows:
            selected_idx = start + selected_rows[0]
            if selected_idx < len(results):
                selected_doc_id = results[selected_idx].get("DOC_ID", "")
                if selected_doc_id:
                    st.subheader("Belge Önizleme")
                    show_preview(db_path, selected_doc_id)
        else:
            st.info("Soldan bir satır seçerek belgeyi önizleyin.")


# ─── ARAMA FONKSİYONU ─────────────────────────────────────────────────────────

def _run_search(
    db_path: str,
    date_from, date_to, doc_type, currency, vkn, doc_no,
    item_code, item_name, depot, plate, driver, total_min, total_max,
) -> None:
    kwargs = dict(
        date_from=str(date_from) if date_from else None,
        date_to=str(date_to) if date_to else None,
        doc_type=doc_type or None,
        currency=currency or None,
        vkn=vkn.strip() or None,
        doc_no=doc_no.strip() or None,
        item_code=item_code.strip() or None,
        item_name=item_name.strip() or None,
        depot=depot.strip() or None,
        plate=plate.strip() or None,
        driver=driver.strip() or None,
        total_min=total_min if total_min > 0 else None,
        total_max=total_max if total_max > 0 else None,
    )

    total = storage.count_filtered(db_path, **kwargs)
    results = storage.query_filtered(db_path, limit=5000, offset=0, **kwargs)

    st.session_state["search_results"] = results
    st.session_state["search_total"] = total


# ─── EXPORT ───────────────────────────────────────────────────────────────────

def _export_section(db_path: str, results: List[Dict], total: int) -> None:
    from datetime import datetime

    ts = datetime.now().strftime("%Y%m%d_%H%M")

    st.markdown("---")
    st.subheader("Disa Aktar")

    # Gosterim sutunlari (FILE_PATH, HASH, DOC_ID gizli)
    export_cols = [
        "DOC_TYPE", "DOC_NO", "ISSUE_DATE", "SHIP_DATE",
        "SENDER_VKN_TCKN", "RECEIVER_VKN_TCKN",
        "ITEM_CODE", "ITEM_NAME", "QUANTITY", "UNIT",
        "NET", "GROSS", "DEPOT_OR_BRANCH", "PLATE", "DRIVER",
        "LOT_OR_SERIAL", "CURRENCY", "DOC_TOTAL",
    ]

    df_export = pd.DataFrame(results)
    existing = [c for c in export_cols if c in df_export.columns]
    df_export = df_export[existing]

    ec1, ec2 = st.columns(2)

    with ec1:
        csv_data = df_export.to_csv(index=False, encoding="utf-8-sig")
        st.download_button(
            "CSV Indir (.csv)",
            data=csv_data.encode("utf-8-sig"),
            file_name=f"export_{ts}.csv",
            mime="text/csv",
            use_container_width=True,
            type="primary",
        )

    with ec2:
        if total > EXCEL_ROW_LIMIT:
            st.warning(f"Satir sayisi ({total:,}) Excel limitini ({EXCEL_ROW_LIMIT:,}) asiyor. CSV kullanin.")
        else:
            excel_buf = io.BytesIO()
            with pd.ExcelWriter(excel_buf, engine="openpyxl") as writer:
                df_export.to_excel(writer, index=False, sheet_name="Sonuclar")
            excel_buf.seek(0)
            st.download_button(
                "Excel Indir (.xlsx)",
                data=excel_buf.getvalue(),
                file_name=f"export_{ts}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
                type="primary",
            )

    st.caption(f"Toplam {len(results):,} satir disa aktarilacak.")
