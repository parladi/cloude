"""
UBL-TR Fatura Ayıklayıcı - Flask Web Uygulaması
GİB e-Fatura ZIP dosyalarından fatura bilgilerini ayıklar.
"""

import os
import io
from flask import Flask, render_template, request, send_file, redirect, url_for, flash
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from ubl_parser import extract_from_zip_bytes, get_flat_invoice_data, get_all_line_items

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100 MB limit


@app.route('/', methods=['GET'])
def index():
    """Ana sayfa - ZIP yükleme formu."""
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload():
    """ZIP dosyasını yükle ve faturaları ayıkla."""
    if 'zipfile' not in request.files:
        flash('Lütfen bir ZIP dosyası seçin.', 'error')
        return redirect(url_for('index'))

    file = request.files['zipfile']
    if file.filename == '':
        flash('Dosya seçilmedi.', 'error')
        return redirect(url_for('index'))

    if not file.filename.lower().endswith('.zip'):
        flash('Lütfen .zip uzantılı bir dosya yükleyin.', 'error')
        return redirect(url_for('index'))

    zip_bytes = file.read()
    invoices, errors = extract_from_zip_bytes(zip_bytes, file.filename)

    if not invoices and errors:
        flash(f'Hiç fatura bulunamadı. {len(errors)} hata oluştu.', 'error')
        return render_template('results.html', invoices=[], errors=errors,
                               flat_data=[], line_items=[], filename=file.filename)

    flat_data = get_flat_invoice_data(invoices)
    line_items = get_all_line_items(invoices)

    return render_template('results.html',
                           invoices=invoices,
                           flat_data=flat_data,
                           line_items=line_items,
                           errors=errors,
                           filename=file.filename)


@app.route('/export', methods=['POST'])
def export_excel():
    """Faturaları Excel dosyasına aktarır."""
    if 'zipfile' not in request.files:
        flash('Excel oluşturmak için ZIP dosyası yükleyin.', 'error')
        return redirect(url_for('index'))

    file = request.files['zipfile']
    if file.filename == '' or not file.filename.lower().endswith('.zip'):
        flash('Geçerli bir ZIP dosyası yükleyin.', 'error')
        return redirect(url_for('index'))

    zip_bytes = file.read()
    invoices, errors = extract_from_zip_bytes(zip_bytes, file.filename)

    if not invoices:
        flash('İçe aktarılacak fatura bulunamadı.', 'error')
        return redirect(url_for('index'))

    wb = create_excel_workbook(invoices)

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)

    export_name = os.path.splitext(file.filename)[0] + '_faturalar.xlsx'
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=export_name
    )


def create_excel_workbook(invoices):
    """Fatura verilerinden Excel çalışma kitabı oluşturur."""
    wb = Workbook()

    # Stil tanımlamaları
    header_font = Font(bold=True, color='FFFFFF', size=11)
    header_fill = PatternFill(start_color='2F5496', end_color='2F5496', fill_type='solid')
    header_alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
    thin_border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )

    # --- Sayfa 1: Fatura Özeti ---
    ws1 = wb.active
    ws1.title = 'Fatura Özeti'

    flat_data = get_flat_invoice_data(invoices)
    if flat_data:
        # Tüm sütun başlıklarını topla
        all_keys = []
        for row in flat_data:
            for key in row.keys():
                if key not in all_keys:
                    all_keys.append(key)

        # Başlık satırı
        for col, key in enumerate(all_keys, 1):
            cell = ws1.cell(row=1, column=col, value=key)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = header_alignment
            cell.border = thin_border

        # Veri satırları
        for row_idx, row_data in enumerate(flat_data, 2):
            for col_idx, key in enumerate(all_keys, 1):
                cell = ws1.cell(row=row_idx, column=col_idx, value=row_data.get(key, ''))
                cell.border = thin_border
                cell.alignment = Alignment(wrap_text=True)

        # Sütun genişliklerini ayarla
        for col in range(1, len(all_keys) + 1):
            ws1.column_dimensions[ws1.cell(row=1, column=col).column_letter].width = 18

    # --- Sayfa 2: Fatura Kalemleri ---
    ws2 = wb.create_sheet('Fatura Kalemleri')

    line_items = get_all_line_items(invoices)
    if line_items:
        all_line_keys = []
        for row in line_items:
            for key in row.keys():
                if key not in all_line_keys:
                    all_line_keys.append(key)

        for col, key in enumerate(all_line_keys, 1):
            cell = ws2.cell(row=1, column=col, value=key)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = header_alignment
            cell.border = thin_border

        for row_idx, row_data in enumerate(line_items, 2):
            for col_idx, key in enumerate(all_line_keys, 1):
                cell = ws2.cell(row=row_idx, column=col_idx, value=row_data.get(key, ''))
                cell.border = thin_border

        for col in range(1, len(all_line_keys) + 1):
            ws2.column_dimensions[ws2.cell(row=1, column=col).column_letter].width = 16

    # --- Sayfa 3: Hatalar (varsa) ---
    # Bu sayfayı dışarıda oluşturuyoruz, hata yoksa eklenmez

    # Filtre ekle
    if flat_data:
        ws1.auto_filter.ref = ws1.dimensions
    if line_items:
        ws2.auto_filter.ref = ws2.dimensions

    # İlk satırı dondur
    ws1.freeze_panes = 'A2'
    ws2.freeze_panes = 'A2'

    return wb


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
