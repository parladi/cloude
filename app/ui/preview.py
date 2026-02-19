"""
Belge onizleme paneli.
PDF gomuluyse iframe, degilse HTML template gosterir.
Ayrica kaynak XML icerigini gorsel olarak gosterir.
"""
import base64
import os
import zipfile
from typing import Any, Dict, List

import streamlit as st
import streamlit.components.v1 as components

from app.db import storage
from app.parsing.html_render import render_html


def show_preview(db_path: str, doc_id: str) -> None:
    """Secilen belgenin onizlemesini gosterir."""
    doc = storage.get_doc(db_path, doc_id)
    if not doc:
        st.warning("Belge bulunamadi.")
        return

    lines = storage.get_lines(db_path, doc_id)

    # Baslik bilgisi
    doc_type_label = "e-Irsaliye" if doc.get("doc_type") == "DESPATCH" else "e-Fatura"
    st.markdown(
        f"**{doc_type_label}** -- {doc.get('doc_no','')} "
        f"| {doc.get('issue_date','')} "
        f"| {doc.get('currency','')} {doc.get('doc_total') or 0:,.2f}"
    )

    # Sekmeli onizleme: Belge | XML Icerik
    tab_doc, tab_xml = st.tabs(["Belge Onizleme", "XML Icerik"])

    with tab_doc:
        pdf_path = doc.get("embedded_pdf_path")
        if pdf_path and os.path.isfile(pdf_path):
            _show_pdf_iframe(pdf_path)
        else:
            html_content = render_html(doc, lines)
            components.html(html_content, height=600, scrolling=True)

    with tab_xml:
        _show_xml_content(doc)


def _show_pdf_iframe(pdf_path: str) -> None:
    """PDF'yi base64 ile iframe icinde gosterir."""
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
            PDF goruntulenemiyor. <a href="data:application/pdf;base64,{b64}" download="belge.pdf">Indir</a>
        </iframe>
        """
        components.html(iframe_html, height=620)
    except Exception as e:
        st.error(f"PDF yuklenemedi: {e}")


def _show_xml_content(doc: Dict) -> None:
    """Kaynak XML dosyasinin icerigini gorsel olarak gosterir."""
    file_path = doc.get("file_path", "")
    if not file_path:
        st.info("Kaynak dosya yolu bulunamadi.")
        return

    xml_text = _read_xml_from_source(file_path)
    if xml_text is None:
        st.warning(f"XML dosyasi okunamadi: {file_path}")
        return

    # Formatli XML goster
    try:
        from lxml import etree
        parsed = etree.fromstring(xml_text.encode("utf-8") if isinstance(xml_text, str) else xml_text)
        formatted = etree.tostring(parsed, pretty_print=True, encoding="unicode", xml_declaration=True)
    except Exception:
        formatted = xml_text

    # Syntax-highlighted HTML olarak goster
    html_display = _xml_to_highlighted_html(formatted)
    components.html(html_display, height=600, scrolling=True)

    # Ham XML indirme butonu
    st.download_button(
        "XML Indir",
        data=formatted if isinstance(formatted, str) else formatted.decode("utf-8"),
        file_name=f"{doc.get('doc_no', 'belge')}.xml",
        mime="application/xml",
        use_container_width=True,
    )


def _read_xml_from_source(file_path: str) -> str | None:
    """
    Kaynak yolundan XML icerigini okur.
    ZIP icindeki dosyalar icin 'zip_path::entry_name' formatini destekler.
    """
    if "::" in file_path:
        # ZIP icindeki dosya
        parts = file_path.split("::", 1)
        zip_path = parts[0]
        entry_name = parts[1]
        try:
            with zipfile.ZipFile(zip_path, "r") as zf:
                xml_bytes = zf.read(entry_name)
                return xml_bytes.decode("utf-8", errors="replace")
        except Exception:
            return None
    else:
        # Dogrudan XML dosyasi
        try:
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                return f.read()
        except Exception:
            return None


def _xml_to_highlighted_html(xml_text: str) -> str:
    """XML metnini syntax-highlighted HTML'e cevirir."""
    import html as html_mod

    escaped = html_mod.escape(xml_text)

    # Basit syntax highlighting
    import re
    # Tag isimleri
    highlighted = re.sub(
        r'&lt;(/?)([a-zA-Z0-9_:\-]+)',
        r'&lt;\1<span style="color:#1565C0;font-weight:bold">\2</span>',
        escaped,
    )
    # Attribute isimleri
    highlighted = re.sub(
        r'(\s)([a-zA-Z0-9_:\-]+)(=)',
        r'\1<span style="color:#6A1B9A">\2</span>\3',
        highlighted,
    )
    # Attribute degerleri (&quot; icinde)
    highlighted = re.sub(
        r'(&quot;)(.*?)(&quot;)',
        r'\1<span style="color:#2E7D32">\2</span>\3',
        highlighted,
    )

    return f"""<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"></head>
<body style="margin:0; padding:12px; background:#FAFAFA; font-family:'Consolas','Monaco','Courier New',monospace; font-size:12px;">
<pre style="white-space:pre-wrap; word-wrap:break-word; line-height:1.5; margin:0; color:#333;">{highlighted}</pre>
</body>
</html>"""
