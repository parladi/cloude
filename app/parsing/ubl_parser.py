"""
UBL TR1.2 XML Parser - e-İrsaliye (DespatchAdvice) ve e-Fatura (Invoice).
Namespace-aware parsing, hata toleranslı.
"""
import base64
import uuid
from typing import Any, Dict, List, Optional, Tuple

from lxml import etree

# ─── NAMESPACE HARİTASI ──────────────────────────────────────────────────────

NS = {
    "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
    "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
    "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
    "inv": "urn:oasis:names:specification:ubl:schema:xsd:Invoice-2",
    "des": "urn:oasis:names:specification:ubl:schema:xsd:DespatchAdvice-2",
}


def _t(el: Optional[etree._Element], xpath: str, default: str = "") -> str:
    """XPath ile güvenli metin çekme."""
    if el is None:
        return default
    found = el.xpath(xpath, namespaces=NS)
    if found:
        val = found[0]
        if hasattr(val, "text"):
            return (val.text or "").strip()
        return str(val).strip()
    return default


def _first(el: Optional[etree._Element], *xpaths: str) -> str:
    """Birden fazla XPath dene, ilk bulduğunu döndür."""
    for xp in xpaths:
        v = _t(el, xp)
        if v:
            return v
    return ""


def _safe_float(val: str) -> Optional[float]:
    try:
        return float(val.replace(",", ".")) if val else None
    except (ValueError, AttributeError):
        return None


# ─── VKN/TCKN ÇIKARMA ───────────────────────────────────────────────────────

def _extract_vkn(party_el: Optional[etree._Element]) -> str:
    """
    Önce schemeID=VKN/TCKN olan PartyIdentification/ID'yi ara,
    sonra herhangi bir PartyIdentification/ID.
    """
    if party_el is None:
        return ""
    # cac:Party içindeki tüm PartyIdentification/ID'leri listele
    ids = party_el.xpath(
        ".//cac:Party/cac:PartyIdentification/cbc:ID", namespaces=NS
    )
    # Önce VKN/TCKN schemeID olana bak
    for id_el in ids:
        scheme = id_el.get("schemeID", "").upper()
        if scheme in ("VKN", "TCKN", "VERGINO", "TAX"):
            return (id_el.text or "").strip()
    # Yoksa ilk bulduğu
    if ids:
        return (ids[0].text or "").strip()
    # Alternatif: cac:PartyTaxScheme/cbc:CompanyID
    comp = party_el.xpath(
        ".//cac:Party/cac:PartyTaxScheme/cbc:CompanyID", namespaces=NS
    )
    if comp:
        return (comp[0].text or "").strip()
    return ""


# ─── EMBEDDED PDF ────────────────────────────────────────────────────────────

def _extract_embedded_pdf(root: etree._Element) -> Optional[bytes]:
    """
    AdditionalDocumentReference/Attachment/EmbeddedDocumentBinaryObject
    içindeki PDF base64 verisini çözer.
    """
    refs = root.xpath(".//cac:AdditionalDocumentReference", namespaces=NS)
    for ref in refs:
        # DocumentTypeCode veya ID ile PDF kontrolü
        type_code = _t(ref, "cbc:DocumentTypeCode").upper()
        doc_type = _t(ref, "cbc:DocumentType").upper()
        embed = ref.xpath(
            ".//cac:Attachment/cbc:EmbeddedDocumentBinaryObject", namespaces=NS
        )
        if not embed:
            continue
        embed_el = embed[0]
        mime = embed_el.get("mimeCode", "").lower()
        # PDF mi?
        if "pdf" in mime or "pdf" in type_code or "pdf" in doc_type:
            raw = (embed_el.text or "").strip()
            if raw:
                try:
                    return base64.b64decode(raw)
                except Exception:
                    pass
        # mimeCode yoksa yine dene (ilk embed)
        if not mime:
            raw = (embed_el.text or "").strip()
            if raw:
                try:
                    decoded = base64.b64decode(raw)
                    if decoded[:4] == b"%PDF":
                        return decoded
                except Exception:
                    pass
    return None


# ─── DESPATCH ADVICE (e-İrsaliye) ────────────────────────────────────────────

def _parse_despatch(root: etree._Element, file_path: str, file_hash: str) -> Tuple[Dict, List[Dict], Optional[bytes]]:
    doc_id = str(uuid.uuid4())

    doc_no = _t(root, "cbc:ID")
    issue_date = _t(root, "cbc:IssueDate")

    # Sevk tarihi - çeşitli alanlar deneniyor
    ship_date = _first(
        root,
        ".//cac:DespatchLine/cac:Shipment/cbc:ShippingDate",
        ".//cac:Shipment/cbc:ShippingDate",
        ".//cac:Shipment/cac:ShipmentStage/cbc:TransportModeCode",  # fallback
        "cbc:ActualDeliveryDate",
        ".//cac:Delivery/cbc:ActualDeliveryDate",
        ".//cac:DespatchLine/cac:Delivery/cbc:ActualDeliveryDate",
    )

    # Gönderici
    sender_vkn = _extract_vkn(root.find(".//cac:DespatchSupplierParty", NS))
    if not sender_vkn:
        sender_vkn = _extract_vkn(root.find(".//cac:SellerSupplierParty", NS))

    # Alıcı
    receiver_vkn = _extract_vkn(root.find(".//cac:DeliveryCustomerParty", NS))
    if not receiver_vkn:
        receiver_vkn = _extract_vkn(root.find(".//cac:BuyerCustomerParty", NS))

    # Para birimi
    currency = _first(root, "cbc:DocumentCurrencyCode", "cbc:LineExtensionAmount/@currencyID")

    # Plaka
    plate = _first(
        root,
        ".//cac:Shipment/cac:TransportHandlingUnit/cac:TransportEquipment/cbc:ID",
        ".//cac:Shipment/cac:RoadTransport/cbc:LicensePlateID",
        ".//cac:RoadTransport/cbc:LicensePlateID",
    )

    # Sürücü
    driver = _first(
        root,
        ".//cac:Shipment/cac:ShipmentStage/cac:DriverPerson/cbc:FirstName",
        ".//cac:DriverPerson/cbc:FirstName",
        ".//cac:Shipment/cac:ShipmentStage/cac:DriverPerson/cac:IdentityDocumentReference/cbc:ID",
    )
    # Sürücü soyadını da ekle
    driver_last = _first(
        root,
        ".//cac:Shipment/cac:ShipmentStage/cac:DriverPerson/cbc:FamilyName",
        ".//cac:DriverPerson/cbc:FamilyName",
    )
    if driver and driver_last:
        driver = f"{driver} {driver_last}"

    # Depo/Şube
    depot = _first(
        root,
        ".//cac:DeliveryCustomerParty/cac:Party/cac:PartyName/cbc:Name",
        ".//cac:Delivery/cac:DeliveryLocation/cbc:Description",
        ".//cac:Delivery/cac:DeliveryLocation/cbc:Name",
    )

    # Embedded PDF
    pdf_bytes = _extract_embedded_pdf(root)

    # Kalemler
    lines_data: List[Dict] = []
    for line_el in root.xpath(".//cac:DespatchLine", namespaces=NS):
        qty_el = line_el.find("cbc:DeliveredQuantity", NS)
        quantity = (qty_el.text or "").strip() if qty_el is not None else ""
        unit = qty_el.get("unitCode", "") if qty_el is not None else ""

        item_el = line_el.find("cac:Item", NS)
        item_name = _t(item_el, "cbc:Name") if item_el is not None else ""

        # Ürün kodu: önce seller, sonra buyer, sonra standard
        item_code = _first(
            item_el,
            "cac:SellersItemIdentification/cbc:ID",
            "cac:BuyersItemIdentification/cbc:ID",
            "cac:StandardItemIdentification/cbc:ID",
            "cac:ManufacturersItemIdentification/cbc:ID",
        ) if item_el is not None else ""

        # Lot/Seri
        lot = _first(
            line_el,
            ".//cac:Item/cac:ItemInstance/cac:LotIdentification/cbc:LotNumberID",
            ".//cac:Item/cac:ItemInstance/cac:LotIdentification/cbc:ExpiryDate",
            ".//cac:Item/cac:ItemInstance/cbc:SerialID",
            ".//cac:ItemInstance/cac:LotIdentification/cbc:LotNumberID",
            ".//cac:ItemInstance/cbc:SerialID",
        )

        # Net/Brüt
        net = _first(line_el, "cbc:LineExtensionAmount", "cbc:Price")
        gross = _first(line_el, "cbc:TaxInclusiveLineExtensionAmount", "cbc:LineExtensionAmount")

        lines_data.append({
            "doc_id": doc_id,
            "item_code": item_code,
            "item_name": item_name,
            "quantity": _safe_float(quantity),
            "unit": unit,
            "net": _safe_float(net),
            "gross": _safe_float(gross),
            "lot_or_serial": lot,
            "line_amount": _safe_float(net),
        })

    # Belge toplamı (satır toplamları)
    doc_total = sum(
        l["line_amount"] for l in lines_data if l["line_amount"] is not None
    )

    doc = {
        "doc_id": doc_id,
        "doc_type": "DESPATCH",
        "doc_no": doc_no,
        "issue_date": issue_date,
        "ship_date": ship_date,
        "sender_vkn": sender_vkn,
        "receiver_vkn": receiver_vkn,
        "currency": currency,
        "plate": plate,
        "driver": driver,
        "depot": depot,
        "doc_total": doc_total,
        "has_embedded_pdf": 1 if pdf_bytes else 0,
        "embedded_pdf_path": None,
        "file_path": file_path,
        "file_hash": file_hash,
    }
    return doc, lines_data, pdf_bytes


# ─── INVOICE (e-Fatura) ──────────────────────────────────────────────────────

def _parse_invoice(root: etree._Element, file_path: str, file_hash: str) -> Tuple[Dict, List[Dict], Optional[bytes]]:
    doc_id = str(uuid.uuid4())

    doc_no = _t(root, "cbc:ID")
    issue_date = _t(root, "cbc:IssueDate")
    currency = _t(root, "cbc:DocumentCurrencyCode")

    # Sevk tarihi
    ship_date = _first(
        root,
        ".//cac:Delivery/cbc:ActualDeliveryDate",
        ".//cac:Shipment/cbc:ShippingDate",
        ".//cac:DespatchDocumentReference/cbc:IssueDate",
    )

    sender_vkn = _extract_vkn(root.find(".//cac:AccountingSupplierParty", NS))
    receiver_vkn = _extract_vkn(root.find(".//cac:AccountingCustomerParty", NS))

    # Plaka
    plate = _first(
        root,
        ".//cac:Delivery/cac:Shipment/cac:RoadTransport/cbc:LicensePlateID",
        ".//cac:RoadTransport/cbc:LicensePlateID",
        ".//cac:Shipment/cac:TransportHandlingUnit/cac:TransportEquipment/cbc:ID",
    )

    # Sürücü
    driver = _first(
        root,
        ".//cac:Delivery/cac:Shipment/cac:ShipmentStage/cac:DriverPerson/cbc:FirstName",
        ".//cac:ShipmentStage/cac:DriverPerson/cbc:FirstName",
    )
    driver_last = _first(
        root,
        ".//cac:Delivery/cac:Shipment/cac:ShipmentStage/cac:DriverPerson/cbc:FamilyName",
        ".//cac:ShipmentStage/cac:DriverPerson/cbc:FamilyName",
    )
    if driver and driver_last:
        driver = f"{driver} {driver_last}"

    # Depo/Şube
    depot = _first(
        root,
        ".//cac:Delivery/cac:DeliveryLocation/cbc:Description",
        ".//cac:Delivery/cac:DeliveryLocation/cbc:Name",
        ".//cac:AccountingCustomerParty/cac:Party/cac:PartyName/cbc:Name",
    )

    # Belge toplamı
    doc_total_str = _first(
        root,
        ".//cac:LegalMonetaryTotal/cbc:PayableAmount",
        ".//cac:LegalMonetaryTotal/cbc:TaxInclusiveAmount",
        ".//cac:LegalMonetaryTotal/cbc:TaxExclusiveAmount",
    )
    doc_total = _safe_float(doc_total_str) or 0.0

    # Embedded PDF
    pdf_bytes = _extract_embedded_pdf(root)

    # Kalemler
    lines_data: List[Dict] = []
    for line_el in root.xpath(".//cac:InvoiceLine", namespaces=NS):
        qty_el = line_el.find("cbc:InvoicedQuantity", NS)
        quantity = (qty_el.text or "").strip() if qty_el is not None else ""
        unit = qty_el.get("unitCode", "") if qty_el is not None else ""

        item_el = line_el.find("cac:Item", NS)
        item_name = _t(item_el, "cbc:Name") if item_el is not None else ""
        item_code = _first(
            item_el,
            "cac:SellersItemIdentification/cbc:ID",
            "cac:BuyersItemIdentification/cbc:ID",
            "cac:StandardItemIdentification/cbc:ID",
        ) if item_el is not None else ""

        # Lot/Seri
        lot = _first(
            line_el,
            ".//cac:Item/cac:ItemInstance/cac:LotIdentification/cbc:LotNumberID",
            ".//cac:Item/cac:ItemInstance/cbc:SerialID",
            ".//cac:ItemInstance/cbc:SerialID",
        )

        net_str = _t(line_el, "cbc:LineExtensionAmount")
        net = _safe_float(net_str)

        # KDV dahil (varsa)
        tax_incl = _first(
            line_el,
            ".//cac:TaxTotal/cbc:TaxAmount",
        )
        gross = None
        if net is not None and tax_incl:
            t = _safe_float(tax_incl)
            gross = (net + t) if t is not None else net
        else:
            gross = net

        lines_data.append({
            "doc_id": doc_id,
            "item_code": item_code,
            "item_name": item_name,
            "quantity": _safe_float(quantity),
            "unit": unit,
            "net": net,
            "gross": gross,
            "lot_or_serial": lot,
            "line_amount": net,
        })

    doc = {
        "doc_id": doc_id,
        "doc_type": "INVOICE",
        "doc_no": doc_no,
        "issue_date": issue_date,
        "ship_date": ship_date,
        "sender_vkn": sender_vkn,
        "receiver_vkn": receiver_vkn,
        "currency": currency,
        "plate": plate,
        "driver": driver,
        "depot": depot,
        "doc_total": doc_total,
        "has_embedded_pdf": 1 if pdf_bytes else 0,
        "embedded_pdf_path": None,
        "file_path": file_path,
        "file_hash": file_hash,
    }
    return doc, lines_data, pdf_bytes


# ─── ANA PARSE FONKSİYONU ────────────────────────────────────────────────────

def parse_xml(
    xml_bytes: bytes, file_path: str, file_hash: str
) -> Tuple[Optional[Dict], List[Dict], Optional[bytes], Optional[str]]:
    """
    XML'i parse eder.
    Returns: (doc_dict, lines_list, pdf_bytes_or_None, error_str_or_None)
    """
    try:
        root = etree.fromstring(xml_bytes)
    except Exception as e:
        return None, [], None, f"XML parse hatası: {e}"

    # Root tag'e göre tip belirle (namespace prefix'i kaldır)
    tag = root.tag
    local = tag.split("}")[-1] if "}" in tag else tag

    try:
        if local == "DespatchAdvice":
            doc, lines, pdf_bytes = _parse_despatch(root, file_path, file_hash)
        elif local == "Invoice":
            doc, lines, pdf_bytes = _parse_invoice(root, file_path, file_hash)
        else:
            return None, [], None, f"Tanımsız belge tipi: {local}"
    except Exception as e:
        return None, [], None, f"Parse hatası ({local}): {e}"

    return doc, lines, pdf_bytes, None
