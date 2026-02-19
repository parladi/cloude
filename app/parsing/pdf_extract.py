"""
Gömülü PDF verisini diske kaydeder.
"""
import os


def save_pdf(pdf_bytes: bytes, cache_dir: str, doc_id: str) -> str:
    """
    PDF byte'larını cache/pdfs/{doc_id}.pdf olarak kaydeder.
    Dosya yolunu döner.
    """
    pdf_dir = os.path.join(cache_dir, "pdfs")
    os.makedirs(pdf_dir, exist_ok=True)
    path = os.path.join(pdf_dir, f"{doc_id}.pdf")
    with open(path, "wb") as f:
        f.write(pdf_bytes)
    return path
