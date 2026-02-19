"""
UBL-TR (GIB e-Irsaliye) DespatchAdvice XML Parser Modulu
Klasor veya ZIP icindeki UBL DespatchAdvice XML dosyalarini okur
ve irsaliye bilgilerini ayiklar.
"""

import xml.etree.ElementTree as ET
import zipfile
import io
import os
import glob

# UBL-TR DespatchAdvice namespace tanimlari
NAMESPACES = {
    'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
    'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
    'da': 'urn:oasis:names:specification:ubl:schema:xsd:DespatchAdvice-2',
    'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
    'ds': 'http://www.w3.org/2000/09/xmldsig#',
    'xades': 'http://uri.etsi.org/01903/v1.3.2#',
}


def safe_text(element, xpath, namespaces=None):
    """XML elementinden guvenli metin cikarir, bulunamazsa bos string doner."""
    if namespaces is None:
        namespaces = NAMESPACES
    el = element.find(xpath, namespaces)
    return el.text.strip() if el is not None and el.text else ''


def safe_attr(element, xpath, attr, namespaces=None):
    """XML elementinden guvenli attribute cikarir."""
    if namespaces is None:
        namespaces = NAMESPACES
    el = element.find(xpath, namespaces)
    if el is not None:
        return el.get(attr, '')
    return ''


def parse_party(party_element):
    """Taraf (tedarikci/musteri/tasiyici) bilgilerini ayiklar."""
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

    # Sirket / Kisi adi
    party_name = safe_text(party, 'cac:PartyName/cbc:Name')
    info['Ad'] = party_name

    # Vergi dairesi
    tax_scheme = safe_text(party, 'cac:PartyTaxScheme/cac:TaxScheme/cbc:Name')
    info['Vergi Dairesi'] = tax_scheme

    # Adres bilgileri
    address = party.find('cac:PostalAddress', NAMESPACES)
    if address is not None:
        info['Il'] = safe_text(address, 'cbc:CityName')
        info['Ilce'] = safe_text(address, 'cbc:CitySubdivisionName')
        info['Sokak'] = safe_text(address, 'cbc:StreetName')
        info['Bina No'] = safe_text(address, 'cbc:BuildingNumber')
        info['Posta Kodu'] = safe_text(address, 'cbc:PostalZone')
        info['Ulke'] = safe_text(address, 'cac:Country/cbc:Name')

    # Iletisim bilgileri
    contact = party.find('cac:Contact', NAMESPACES)
    if contact is not None:
        info['Telefon'] = safe_text(contact, 'cbc:Telephone')
        info['Fax'] = safe_text(contact, 'cbc:Telefax')
        info['E-posta'] = safe_text(contact, 'cbc:ElectronicMail')

    # Kisi bilgileri
    person = party.find('cac:Person', NAMESPACES)
    if person is not None:
        first = safe_text(person, 'cbc:FirstName')
        last = safe_text(person, 'cbc:FamilyName')
        info['Kisi Adi'] = f"{first} {last}".strip()

    return info


def parse_carrier(shipment_element):
    """Tasiyici (CarrierParty) bilgilerini ayiklar."""
    if shipment_element is None:
        return {}

    delivery = shipment_element.find('cac:Delivery', NAMESPACES)
    if delivery is None:
        return {}

    carrier_party = delivery.find('cac:CarrierParty', NAMESPACES)
    if carrier_party is None:
        return {}

    info = {}

    # Tasiyici kimlik
    party_id = carrier_party.find('cac:PartyIdentification/cbc:ID', NAMESPACES)
    if party_id is not None:
        scheme = party_id.get('schemeID', '')
        info['VKN/TCKN'] = party_id.text.strip() if party_id.text else ''
        info['Kimlik Tipi'] = scheme

    # Tasiyici adi
    info['Ad'] = safe_text(carrier_party, 'cac:PartyName/cbc:Name')

    # Surucu bilgisi
    person = carrier_party.find('cac:Person', NAMESPACES)
    if person is not None:
        first = safe_text(person, 'cbc:FirstName')
        last = safe_text(person, 'cbc:FamilyName')
        info['Surucu'] = f"{first} {last}".strip()

    return info


def parse_shipment(root):
    """Sevkiyat bilgilerini ayiklar."""
    shipment = root.find('cac:Shipment', NAMESPACES)
    if shipment is None:
        return {}

    info = {}
    info['Sevkiyat ID'] = safe_text(shipment, 'cbc:ID')

    # Teslimat bilgileri
    delivery = shipment.find('cac:Delivery', NAMESPACES)
    if delivery is not None:
        # Gercek sevk tarihi/saati
        despatch = delivery.find('cac:Despatch', NAMESPACES)
        if despatch is not None:
            info['Sevk Tarihi'] = safe_text(despatch, 'cbc:ActualDespatchDate')
            info['Sevk Saati'] = safe_text(despatch, 'cbc:ActualDespatchTime')

        # Teslimat adresi
        del_address = delivery.find('cac:DeliveryAddress', NAMESPACES)
        if del_address is not None:
            info['Teslimat Il'] = safe_text(del_address, 'cbc:CityName')
            info['Teslimat Ilce'] = safe_text(del_address, 'cbc:CitySubdivisionName')
            info['Teslimat Sokak'] = safe_text(del_address, 'cbc:StreetName')
            info['Teslimat Bina No'] = safe_text(del_address, 'cbc:BuildingNumber')
            info['Teslimat Ulke'] = safe_text(del_address, 'cac:Country/cbc:Name')

    # Arac bilgileri (ShipmentStage)
    shipment_stage = shipment.find('cac:ShipmentStage', NAMESPACES)
    if shipment_stage is not None:
        transport_means = shipment_stage.find('cac:TransportMeans', NAMESPACES)
        if transport_means is not None:
            road = transport_means.find('cac:RoadTransport', NAMESPACES)
            if road is not None:
                info['Plaka'] = safe_text(road, 'cbc:LicensePlateID')

    # Dorse bilgisi (TransportHandlingUnit > TransportEquipment)
    thu = shipment.find('cac:TransportHandlingUnit', NAMESPACES)
    if thu is not None:
        te = thu.find('cac:TransportEquipment', NAMESPACES)
        if te is not None:
            info['Dorse Plaka'] = safe_text(te, 'cbc:ID')

    return info


def parse_despatch_lines(root):
    """Irsaliye kalemlerini ayiklar."""
    lines = []
    for line_el in root.findall('cac:DespatchLine', NAMESPACES):
        line = {}
        line['Kalem No'] = safe_text(line_el, 'cbc:ID')

        # Not
        note = safe_text(line_el, 'cbc:Note')
        if note:
            line['Not'] = note

        # Teslim edilen miktar
        qty_el = line_el.find('cbc:DeliveredQuantity', NAMESPACES)
        if qty_el is not None:
            line['Miktar'] = qty_el.text.strip() if qty_el.text else ''
            line['Birim'] = qty_el.get('unitCode', '')

        # Urun bilgileri
        item = line_el.find('cac:Item', NAMESPACES)
        if item is not None:
            line['Urun Adi'] = safe_text(item, 'cbc:Name')

            seller_id = item.find('cac:SellersItemIdentification/cbc:ID', NAMESPACES)
            if seller_id is not None:
                line['Satici Urun Kodu'] = seller_id.text.strip() if seller_id.text else ''

        # Siparis satir referansi
        order_ref = line_el.find('cac:OrderLineReference/cac:OrderReference/cbc:ID', NAMESPACES)
        if order_ref is not None:
            line['Siparis Ref'] = order_ref.text.strip() if order_ref.text else ''

        lines.append(line)

    return lines


def parse_single_despatch(xml_content, filename=''):
    """Tek bir UBL-TR DespatchAdvice XML dosyasini ayiklar."""
    try:
        root = ET.fromstring(xml_content)
    except ET.ParseError as e:
        return {'hata': f'XML parse hatasi: {str(e)}', 'dosya': filename}

    irsaliye = {}
    irsaliye['Dosya Adi'] = filename

    # Temel irsaliye bilgileri
    irsaliye['Irsaliye No'] = safe_text(root, 'cbc:ID')
    irsaliye['UUID'] = safe_text(root, 'cbc:UUID')
    irsaliye['Duzenleme Tarihi'] = safe_text(root, 'cbc:IssueDate')
    irsaliye['Duzenleme Saati'] = safe_text(root, 'cbc:IssueTime')
    irsaliye['Irsaliye Tipi'] = safe_text(root, 'cbc:DespatchAdviceTypeCode')
    irsaliye['Profil ID'] = safe_text(root, 'cbc:ProfileID')

    # Notlar
    notes = []
    for note in root.findall('cbc:Note', NAMESPACES):
        if note.text:
            notes.append(note.text.strip())
    irsaliye['Notlar'] = ' | '.join(notes)

    # Ek dokuman referanslari
    additional_docs = []
    for doc in root.findall('cac:AdditionalDocumentReference', NAMESPACES):
        doc_id = safe_text(doc, 'cbc:ID')
        doc_type = safe_text(doc, 'cbc:DocumentTypeCode')
        doc_type_text = safe_text(doc, 'cbc:DocumentType')
        label = doc_type_text or doc_type
        if doc_id:
            additional_docs.append(f"{doc_id} ({label})" if label else doc_id)
    irsaliye['Ek Dokuman Ref'] = ', '.join(additional_docs)

    # Tedarikci (Gonderen) bilgileri
    supplier = parse_party(root.find('cac:DespatchSupplierParty', NAMESPACES))
    for key, value in supplier.items():
        irsaliye[f'Gonderen {key}'] = value

    # Musteri (Alici) bilgileri
    customer = parse_party(root.find('cac:DeliveryCustomerParty', NAMESPACES))
    for key, value in customer.items():
        irsaliye[f'Alici {key}'] = value

    # Sevkiyat bilgileri
    shipment_info = parse_shipment(root)
    for key, value in shipment_info.items():
        irsaliye[key] = value

    # Tasiyici bilgileri
    shipment = root.find('cac:Shipment', NAMESPACES)
    carrier_info = parse_carrier(shipment)
    for key, value in carrier_info.items():
        irsaliye[f'Tasiyici {key}'] = value

    # Irsaliye kalemleri
    irsaliye['_kalemler'] = parse_despatch_lines(root)

    return irsaliye


def extract_from_folder(folder_path):
    """Klasordeki tum XML dosyalarini okur ve irsaliyeleri ayiklar."""
    irsaliyeler = []
    errors = []

    xml_files = glob.glob(os.path.join(folder_path, '*.xml'))
    xml_files += glob.glob(os.path.join(folder_path, '**', '*.xml'), recursive=True)
    # Tekrarlari kaldir
    xml_files = list(set(xml_files))
    xml_files.sort()

    for xml_path in xml_files:
        try:
            with open(xml_path, 'rb') as f:
                xml_content = f.read()
            result = parse_single_despatch(xml_content, filename=os.path.basename(xml_path))
            if 'hata' in result:
                errors.append(result)
            else:
                irsaliyeler.append(result)
        except Exception as e:
            errors.append({'dosya': os.path.basename(xml_path), 'hata': str(e)})

    return irsaliyeler, errors


def extract_from_zip(zip_path):
    """ZIP dosyasindan UBL DespatchAdvice XML dosyalarini ayiklar."""
    irsaliyeler = []
    errors = []

    try:
        with zipfile.ZipFile(zip_path, 'r') as zf:
            for name in zf.namelist():
                if name.lower().endswith('.xml'):
                    try:
                        xml_content = zf.read(name)
                        result = parse_single_despatch(xml_content, filename=name)
                        if 'hata' in result:
                            errors.append(result)
                        else:
                            irsaliyeler.append(result)
                    except Exception as e:
                        errors.append({'dosya': name, 'hata': str(e)})
    except zipfile.BadZipFile:
        errors.append({'dosya': zip_path, 'hata': 'Gecersiz ZIP dosyasi'})
    except Exception as e:
        errors.append({'dosya': zip_path, 'hata': str(e)})

    return irsaliyeler, errors


def extract_from_zip_bytes(zip_bytes, zip_filename='upload.zip'):
    """Bellek ici ZIP verisinden UBL DespatchAdvice XML dosyalarini ayiklar."""
    irsaliyeler = []
    errors = []

    try:
        with zipfile.ZipFile(io.BytesIO(zip_bytes), 'r') as zf:
            for name in zf.namelist():
                if name.lower().endswith('.xml'):
                    try:
                        xml_content = zf.read(name)
                        result = parse_single_despatch(xml_content, filename=name)
                        if 'hata' in result:
                            errors.append(result)
                        else:
                            irsaliyeler.append(result)
                    except Exception as e:
                        errors.append({'dosya': name, 'hata': str(e)})
    except zipfile.BadZipFile:
        errors.append({'dosya': zip_filename, 'hata': 'Gecersiz ZIP dosyasi'})
    except Exception as e:
        errors.append({'dosya': zip_filename, 'hata': str(e)})

    return irsaliyeler, errors


def extract_from_xml_bytes_list(xml_files_data):
    """Birden fazla XML dosyasinin byte verisinden irsaliyeleri ayiklar.
    xml_files_data: [(filename, bytes), ...] listesi
    """
    irsaliyeler = []
    errors = []

    for filename, xml_content in xml_files_data:
        try:
            result = parse_single_despatch(xml_content, filename=filename)
            if 'hata' in result:
                errors.append(result)
            else:
                irsaliyeler.append(result)
        except Exception as e:
            errors.append({'dosya': filename, 'hata': str(e)})

    return irsaliyeler, errors


def get_flat_irsaliye_data(irsaliyeler):
    """Irsaliyeleri duz tablo formatina cevirir (kalemler haric ana bilgiler)."""
    flat_data = []
    for irs in irsaliyeler:
        row = {k: v for k, v in irs.items() if k != '_kalemler'}
        flat_data.append(row)
    return flat_data


def get_all_despatch_lines(irsaliyeler):
    """Tum irsaliyelerin kalemlerini tek listede toplar."""
    all_lines = []
    for irs in irsaliyeler:
        irsaliye_no = irs.get('Irsaliye No', '')
        irsaliye_tarihi = irs.get('Duzenleme Tarihi', '')
        gonderen = irs.get('Gonderen Ad', '')
        alici = irs.get('Alici Ad', '')
        for line in irs.get('_kalemler', []):
            row = {
                'Irsaliye No': irsaliye_no,
                'Tarih': irsaliye_tarihi,
                'Gonderen': gonderen,
                'Alici': alici,
            }
            row.update(line)
            all_lines.append(row)
    return all_lines
