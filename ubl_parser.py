"""
UBL-TR (GİB e-Fatura) XML Parser Modülü
ZIP içindeki UBL XML dosyalarını okur ve fatura bilgilerini ayıklar.
"""

import xml.etree.ElementTree as ET
import zipfile
import io
import os

# UBL-TR namespace tanımlamaları
NAMESPACES = {
    'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
    'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
    'inv': 'urn:oasis:names:specification:ubl:schema:xsd:Invoice-2',
    'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
    'ds': 'http://www.w3.org/2000/09/xmldsig#',
    'xades': 'http://uri.etsi.org/01903/v1.3.2#',
}


def safe_text(element, xpath, namespaces=None):
    """XML elementinden güvenli metin çıkarır, bulunamazsa boş string döner."""
    if namespaces is None:
        namespaces = NAMESPACES
    el = element.find(xpath, namespaces)
    return el.text.strip() if el is not None and el.text else ''


def parse_party(party_element):
    """Alıcı veya satıcı bilgilerini ayıklar."""
    if party_element is None:
        return {}

    party = party_element.find('cac:Party', NAMESPACES)
    if party is None:
        return {}

    info = {}

    # VKN / TCKN
    party_id = party.find('cac:PartyIdentification/cbc:ID', NAMESPACES)
    if party_id is not None:
        scheme = party_id.get('schemeID', '')
        info['VKN/TCKN'] = party_id.text.strip() if party_id.text else ''
        info['Kimlik Tipi'] = scheme

    # Şirket / Kişi adı
    party_name = safe_text(party, 'cac:PartyName/cbc:Name')
    info['Ad'] = party_name

    # Vergi dairesi
    tax_scheme = safe_text(party, 'cac:PartyTaxScheme/cac:TaxScheme/cbc:Name')
    info['Vergi Dairesi'] = tax_scheme

    # Adres bilgileri
    address = party.find('cac:PostalAddress', NAMESPACES)
    if address is not None:
        info['İl'] = safe_text(address, 'cbc:CityName')
        info['İlçe'] = safe_text(address, 'cbc:CitySubdivisionName')
        info['Sokak'] = safe_text(address, 'cbc:StreetName')
        info['Bina No'] = safe_text(address, 'cbc:BuildingNumber')
        info['Posta Kodu'] = safe_text(address, 'cbc:PostalZone')
        info['Ülke'] = safe_text(address, 'cac:Country/cbc:Name')

    # İletişim bilgileri
    contact = party.find('cac:Contact', NAMESPACES)
    if contact is not None:
        info['Telefon'] = safe_text(contact, 'cbc:Telephone')
        info['Fax'] = safe_text(contact, 'cbc:Telefax')
        info['E-posta'] = safe_text(contact, 'cbc:ElectronicMail')

    # Kişi bilgileri
    person = party.find('cac:Person', NAMESPACES)
    if person is not None:
        first = safe_text(person, 'cbc:FirstName')
        last = safe_text(person, 'cbc:FamilyName')
        info['Kişi Adı'] = f"{first} {last}".strip()

    return info


def parse_invoice_lines(root):
    """Fatura kalemlerini ayıklar."""
    lines = []
    for line_el in root.findall('cac:InvoiceLine', NAMESPACES):
        line = {}
        line['Kalem No'] = safe_text(line_el, 'cbc:ID')
        line['Miktar'] = safe_text(line_el, 'cbc:InvoicedQuantity')

        qty_el = line_el.find('cbc:InvoicedQuantity', NAMESPACES)
        if qty_el is not None:
            line['Birim'] = qty_el.get('unitCode', '')

        line['Kalem Tutarı'] = safe_text(line_el, 'cbc:LineExtensionAmount')

        # Kalem KDV bilgisi
        tax_total = line_el.find('cac:TaxTotal', NAMESPACES)
        if tax_total is not None:
            line['Kalem KDV Tutarı'] = safe_text(tax_total, 'cbc:TaxAmount')
            tax_subtotal = tax_total.find('cac:TaxSubtotal', NAMESPACES)
            if tax_subtotal is not None:
                line['KDV Oranı (%)'] = safe_text(tax_subtotal, 'cbc:Percent')
                line['KDV Matrah'] = safe_text(tax_subtotal, 'cbc:TaxableAmount')

        # İndirim
        allowance = line_el.find('cac:AllowanceCharge', NAMESPACES)
        if allowance is not None:
            line['İndirim Tutarı'] = safe_text(allowance, 'cbc:Amount')
            line['İndirim Oranı (%)'] = safe_text(allowance, 'cbc:MultiplierFactorNumeric')

        # Ürün bilgileri
        item = line_el.find('cac:Item', NAMESPACES)
        if item is not None:
            line['Ürün Adı'] = safe_text(item, 'cbc:Name')
            line['Açıklama'] = safe_text(item, 'cbc:Description')

            seller_id = item.find('cac:SellersItemIdentification/cbc:ID', NAMESPACES)
            if seller_id is not None:
                line['Satıcı Ürün Kodu'] = seller_id.text.strip() if seller_id.text else ''

        # Birim fiyat
        price = line_el.find('cac:Price', NAMESPACES)
        if price is not None:
            line['Birim Fiyat'] = safe_text(price, 'cbc:PriceAmount')

        lines.append(line)

    return lines


def parse_tax_totals(root):
    """Vergi toplamlarını ayıklar."""
    taxes = []
    for tax_total in root.findall('cac:TaxTotal', NAMESPACES):
        total_amount = safe_text(tax_total, 'cbc:TaxAmount')
        for subtotal in tax_total.findall('cac:TaxSubtotal', NAMESPACES):
            tax = {}
            tax['Vergi Matrahı'] = safe_text(subtotal, 'cbc:TaxableAmount')
            tax['Vergi Tutarı'] = safe_text(subtotal, 'cbc:TaxAmount')
            tax['Vergi Oranı (%)'] = safe_text(subtotal, 'cbc:Percent')
            tax_cat = subtotal.find('cac:TaxCategory/cac:TaxScheme', NAMESPACES)
            if tax_cat is not None:
                tax['Vergi Türü'] = safe_text(tax_cat, 'cbc:Name')
                tax['Vergi Kodu'] = safe_text(tax_cat, 'cbc:TaxTypeCode')
            taxes.append(tax)
    return taxes


def parse_monetary_totals(root):
    """Parasal toplamları ayıklar."""
    totals = {}
    monetary = root.find('cac:LegalMonetaryTotal', NAMESPACES)
    if monetary is not None:
        totals['Satır Toplamı'] = safe_text(monetary, 'cbc:LineExtensionAmount')
        totals['Vergiler Dahil Toplam'] = safe_text(monetary, 'cbc:TaxInclusiveAmount')
        totals['Vergiler Hariç Toplam'] = safe_text(monetary, 'cbc:TaxExclusiveAmount')
        totals['İndirim Toplamı'] = safe_text(monetary, 'cbc:AllowanceTotalAmount')
        totals['Ödenecek Tutar'] = safe_text(monetary, 'cbc:PayableAmount')
        totals['Yuvarlama'] = safe_text(monetary, 'cbc:PayableRoundingAmount')
    return totals


def parse_single_invoice(xml_content, filename=''):
    """Tek bir UBL-TR XML faturasını ayıklar."""
    try:
        root = ET.fromstring(xml_content)
    except ET.ParseError as e:
        return {'hata': f'XML parse hatası: {str(e)}', 'dosya': filename}

    # Namespace prefix'ini kaldır (farklı namespace kullanımlarına uyum)
    tag = root.tag
    if '}' in tag:
        ns = tag.split('}')[0] + '}'
        if ns != '{urn:oasis:names:specification:ubl:schema:xsd:Invoice-2}':
            # Farklı namespace ise güncelle
            pass

    invoice = {}
    invoice['Dosya Adı'] = filename

    # Temel fatura bilgileri
    invoice['Fatura No'] = safe_text(root, 'cbc:ID')
    invoice['UUID'] = safe_text(root, 'cbc:UUID')
    invoice['Fatura Tarihi'] = safe_text(root, 'cbc:IssueDate')
    invoice['Fatura Saati'] = safe_text(root, 'cbc:IssueTime')
    invoice['Fatura Tipi'] = safe_text(root, 'cbc:InvoiceTypeCode')
    invoice['Para Birimi'] = safe_text(root, 'cbc:DocumentCurrencyCode')
    invoice['Profil ID'] = safe_text(root, 'cbc:ProfileID')
    invoice['Özelleştirme ID'] = safe_text(root, 'cbc:CustomizationID')
    invoice['Kopya Göstergesi'] = safe_text(root, 'cbc:CopyIndicator')
    invoice['Satır Sayısı'] = safe_text(root, 'cbc:LineCountNumeric')

    # Notlar
    notes = []
    for note in root.findall('cbc:Note', NAMESPACES):
        if note.text:
            notes.append(note.text.strip())
    invoice['Notlar'] = ' | '.join(notes)

    # Fatura dönemi
    inv_period = root.find('cac:InvoicePeriod', NAMESPACES)
    if inv_period is not None:
        invoice['Dönem Başlangıç'] = safe_text(inv_period, 'cbc:StartDate')
        invoice['Dönem Bitiş'] = safe_text(inv_period, 'cbc:EndDate')

    # Sipariş referansı
    invoice['Sipariş No'] = safe_text(root, 'cac:OrderReference/cbc:ID')

    # İrsaliye referansları
    despatch_refs = []
    for ref in root.findall('cac:DespatchDocumentReference', NAMESPACES):
        despatch_refs.append(safe_text(ref, 'cbc:ID'))
    invoice['İrsaliye Referansları'] = ', '.join(despatch_refs)

    # Ek doküman referansları
    additional_docs = []
    for doc in root.findall('cac:AdditionalDocumentReference', NAMESPACES):
        doc_id = safe_text(doc, 'cbc:ID')
        doc_type = safe_text(doc, 'cbc:DocumentTypeCode')
        if doc_id:
            additional_docs.append(f"{doc_id} ({doc_type})" if doc_type else doc_id)
    invoice['Ek Doküman Referansları'] = ', '.join(additional_docs)

    # Satıcı bilgileri
    supplier = parse_party(root.find('cac:AccountingSupplierParty', NAMESPACES))
    for key, value in supplier.items():
        invoice[f'Satıcı {key}'] = value

    # Alıcı bilgileri
    customer = parse_party(root.find('cac:AccountingCustomerParty', NAMESPACES))
    for key, value in customer.items():
        invoice[f'Alıcı {key}'] = value

    # Ödeme bilgileri
    payment_means = root.find('cac:PaymentMeans', NAMESPACES)
    if payment_means is not None:
        invoice['Ödeme Şekli Kodu'] = safe_text(payment_means, 'cbc:PaymentMeansCode')
        invoice['Ödeme Kanalı'] = safe_text(payment_means, 'cbc:PaymentChannelCode')
        invoice['Vade Tarihi'] = safe_text(payment_means, 'cbc:PaymentDueDate')
        invoice['Ödeme Notu'] = safe_text(payment_means, 'cbc:InstructionNote')

        # Banka bilgileri
        fin_account = payment_means.find('cac:PayeeFinancialAccount', NAMESPACES)
        if fin_account is not None:
            invoice['Banka Hesap No'] = safe_text(fin_account, 'cbc:ID')
            invoice['Şube Adı'] = safe_text(fin_account, 'cac:FinancialInstitutionBranch/cbc:Name')

    # Ödeme koşulları
    payment_terms = root.find('cac:PaymentTerms', NAMESPACES)
    if payment_terms is not None:
        invoice['Ödeme Koşulu'] = safe_text(payment_terms, 'cbc:Note')
        invoice['Ödeme Ceza Oranı'] = safe_text(payment_terms, 'cbc:PenaltySurchargePercent')

    # Vergi toplamları
    tax_totals = parse_tax_totals(root)
    if tax_totals:
        for i, tax in enumerate(tax_totals, 1):
            for key, value in tax.items():
                invoice[f'Vergi {i} - {key}'] = value

    # Toplam KDV tutarı
    tax_total_el = root.find('cac:TaxTotal/cbc:TaxAmount', NAMESPACES)
    if tax_total_el is not None:
        invoice['Toplam KDV Tutarı'] = tax_total_el.text.strip() if tax_total_el.text else ''

    # Tevkifat bilgisi
    withholding = root.find('cac:WithholdingTaxTotal', NAMESPACES)
    if withholding is not None:
        invoice['Tevkifat Tutarı'] = safe_text(withholding, 'cbc:TaxAmount')

    # Parasal toplamlar
    monetary_totals = parse_monetary_totals(root)
    for key, value in monetary_totals.items():
        invoice[key] = value

    # Fatura kalemleri
    invoice['_kalemler'] = parse_invoice_lines(root)

    return invoice


def extract_from_zip(zip_path):
    """ZIP dosyasından UBL XML faturalarını ayıklar."""
    invoices = []
    errors = []

    try:
        with zipfile.ZipFile(zip_path, 'r') as zf:
            for name in zf.namelist():
                # Sadece XML dosyalarını işle
                if name.lower().endswith('.xml'):
                    try:
                        xml_content = zf.read(name)
                        invoice = parse_single_invoice(xml_content, filename=name)
                        if 'hata' in invoice:
                            errors.append(invoice)
                        else:
                            invoices.append(invoice)
                    except Exception as e:
                        errors.append({'dosya': name, 'hata': str(e)})
    except zipfile.BadZipFile:
        errors.append({'dosya': zip_path, 'hata': 'Geçersiz ZIP dosyası'})
    except Exception as e:
        errors.append({'dosya': zip_path, 'hata': str(e)})

    return invoices, errors


def extract_from_zip_bytes(zip_bytes, zip_filename='upload.zip'):
    """Bellek içi ZIP verisinden UBL XML faturalarını ayıklar."""
    invoices = []
    errors = []

    try:
        with zipfile.ZipFile(io.BytesIO(zip_bytes), 'r') as zf:
            for name in zf.namelist():
                if name.lower().endswith('.xml'):
                    try:
                        xml_content = zf.read(name)
                        invoice = parse_single_invoice(xml_content, filename=name)
                        if 'hata' in invoice:
                            errors.append(invoice)
                        else:
                            invoices.append(invoice)
                    except Exception as e:
                        errors.append({'dosya': name, 'hata': str(e)})
    except zipfile.BadZipFile:
        errors.append({'dosya': zip_filename, 'hata': 'Geçersiz ZIP dosyası'})
    except Exception as e:
        errors.append({'dosya': zip_filename, 'hata': str(e)})

    return invoices, errors


def get_flat_invoice_data(invoices):
    """Faturaları düz tablo formatına çevirir (kalemler hariç ana bilgiler)."""
    flat_data = []
    for inv in invoices:
        row = {k: v for k, v in inv.items() if k != '_kalemler'}
        flat_data.append(row)
    return flat_data


def get_all_line_items(invoices):
    """Tüm faturaların kalemlerini tek listede toplar."""
    all_lines = []
    for inv in invoices:
        fatura_no = inv.get('Fatura No', '')
        fatura_tarihi = inv.get('Fatura Tarihi', '')
        for line in inv.get('_kalemler', []):
            row = {'Fatura No': fatura_no, 'Fatura Tarihi': fatura_tarihi}
            row.update(line)
            all_lines.append(row)
    return all_lines
