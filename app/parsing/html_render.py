"""
PDF olmayan belgeler için HTML önizleme şablonu üretir.
"""
from typing import Any, Dict, List


def render_html(doc: Dict[str, Any], lines: List[Dict[str, Any]]) -> str:
    """Belge ve kalemlerden okunabilir HTML üretir."""
    doc_type_label = "e-İrsaliye" if doc.get("doc_type") == "DESPATCH" else "e-Fatura"
    color = "#1565C0" if doc.get("doc_type") == "DESPATCH" else "#2E7D32"

    lines_html = ""
    for i, ln in enumerate(lines, 1):
        qty = ln.get("quantity") or ""
        net = ln.get("net")
        gross = ln.get("gross")
        lines_html += f"""
        <tr>
            <td>{i}</td>
            <td><b>{ln.get('item_code','')}</b></td>
            <td>{ln.get('item_name','')}</td>
            <td style="text-align:right">{qty} {ln.get('unit','')}</td>
            <td style="text-align:right">{f'{net:,.2f}' if net is not None else ''}</td>
            <td style="text-align:right">{f'{gross:,.2f}' if gross is not None else ''}</td>
            <td>{ln.get('lot_or_serial','')}</td>
        </tr>"""

    plate_row = f"<tr><td><b>Plaka</b></td><td>{doc.get('plate','')}</td></tr>" if doc.get("plate") else ""
    driver_row = f"<tr><td><b>Sürücü</b></td><td>{doc.get('driver','')}</td></tr>" if doc.get("driver") else ""
    depot_row = f"<tr><td><b>Depo/Şube</b></td><td>{doc.get('depot','')}</td></tr>" if doc.get("depot") else ""
    ship_row = f"<tr><td><b>Sevk Tarihi</b></td><td>{doc.get('ship_date','')}</td></tr>" if doc.get("ship_date") else ""

    total = doc.get("doc_total") or 0
    currency = doc.get("currency") or ""

    return f"""<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="UTF-8">
<style>
  body {{ font-family: 'Segoe UI', Arial, sans-serif; font-size: 13px; margin: 0; padding: 12px; background: #fafafa; }}
  .header {{ background: {color}; color: white; padding: 12px 16px; border-radius: 6px; margin-bottom: 14px; }}
  .header h2 {{ margin: 0 0 4px 0; font-size: 16px; }}
  .header p {{ margin: 0; font-size: 12px; opacity: 0.85; }}
  .info-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 14px; }}
  .info-box {{ background: white; border: 1px solid #ddd; border-radius: 4px; padding: 10px; }}
  .info-box table {{ width: 100%; border-collapse: collapse; font-size: 12px; }}
  .info-box td {{ padding: 3px 6px; }}
  .info-box td:first-child {{ color: #555; width: 45%; }}
  h3 {{ font-size: 13px; color: {color}; border-bottom: 2px solid {color}; padding-bottom: 4px; margin: 14px 0 8px; }}
  table.lines {{ width: 100%; border-collapse: collapse; font-size: 12px; background: white; }}
  table.lines th {{ background: {color}; color: white; padding: 6px 8px; text-align: left; }}
  table.lines td {{ padding: 5px 8px; border-bottom: 1px solid #eee; }}
  table.lines tr:hover td {{ background: #f0f4ff; }}
  .total-box {{ text-align: right; margin-top: 10px; font-size: 14px; font-weight: bold; color: {color}; }}
</style>
</head>
<body>
<div class="header">
  <h2>{doc_type_label} Önizleme</h2>
  <p>Belge No: {doc.get('doc_no','')} &nbsp;|&nbsp; Tarih: {doc.get('issue_date','')}</p>
</div>

<div class="info-grid">
  <div class="info-box">
    <table>
      <tr><td><b>Gönderici VKN</b></td><td>{doc.get('sender_vkn','')}</td></tr>
      <tr><td><b>Alıcı VKN</b></td><td>{doc.get('receiver_vkn','')}</td></tr>
      <tr><td><b>Para Birimi</b></td><td>{currency}</td></tr>
      {ship_row}
    </table>
  </div>
  <div class="info-box">
    <table>
      {plate_row}
      {driver_row}
      {depot_row}
      <tr><td><b>Belge Tipi</b></td><td>{doc_type_label}</td></tr>
    </table>
  </div>
</div>

<h3>Kalemler ({len(lines)} adet)</h3>
<table class="lines">
  <thead>
    <tr>
      <th>#</th><th>Kod</th><th>Ürün/Hizmet</th>
      <th>Miktar</th><th>Net Tutar</th><th>Brüt Tutar</th><th>Lot/Seri</th>
    </tr>
  </thead>
  <tbody>
    {lines_html}
  </tbody>
</table>
<div class="total-box">Belge Toplamı: {total:,.2f} {currency}</div>
</body>
</html>"""
