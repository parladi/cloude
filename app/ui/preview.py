"""
Belge önizleme paneli.
PDF gömülüyse iframe, değilse HTML template gösterir.
"""
import base64
import os
from typing import Any, Dict, List

import streamlit as st
import streamlit.components.v1 as components

from app.db import storage
from app.parsing.html_render import render_html


def show_preview(db_path: str, doc_id: str) -> None:
    """Seçilen belgenin önizlemesini gösterir."""
    doc = storage.get_doc(db_path, doc_id)
    if not doc:
        st.warning("Belge bulunamadı.")
        return

    lines = storage.get_lines(db_path, doc_id)

    # Başlık bilgisi
    doc_type_label = "e-İrsaliye" if doc.get("doc_type") == "DESPATCH" else "e-Fatura"
    st.markdown(
        f"**{doc_type_label}** — {doc.get('doc_no','')} "
        f"| {doc.get('issue_date','')} "
        f"| {doc.get('currency','')} {doc.get('doc_total') or 0:,.2f}"
    )

    pdf_path = doc.get("embedded_pdf_path")

    if pdf_path and os.path.isfile(pdf_path):
        # PDF iframe
        _show_pdf_iframe(pdf_path)
    else:
        # HTML template
        html_content = render_html(doc, lines)
        components.html(html_content, height=600, scrolling=True)


def _show_pdf_iframe(pdf_path: str) -> None:
    """PDF'yi base64 ile iframe içinde gösterir."""
    try:
        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()
        b64 = base64.b64encode(pdf_bytes).decode("utf-8")
        iframe_html = f"""
        <iframe
            src="data:application/pdf;base64,{b64}"
            width="100%"
            height="600px"
            style="border: 1px solid #ccc; border-radius: 4px;">
            PDF görüntülenemiyor. <a href="data:application/pdf;base64,{b64}" download="belge.pdf">İndir</a>
        </iframe>
        """
        components.html(iframe_html, height=620)
    except Exception as e:
        st.error(f"PDF yüklenemedi: {e}")
