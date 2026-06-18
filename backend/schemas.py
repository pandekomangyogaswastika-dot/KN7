from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from core_utils import new_id


class CustomerAddress(BaseModel):
    id: str = Field(default_factory=lambda: new_id("addr"))
    label: str = "Alamat Utama"
    recipient_name: str
    phone: str = ""
    city: str
    address: str
    is_primary: bool = False


class CustomerCreate(BaseModel):
    name: str
    pic_name: str
    phone: str
    email: str = ""
    type: str = "Retail"
    city: str
    address: str
    npwp: str = ""
    credit_limit: float = 0
    sales_pic: str = ""
    entity_id: str = ""
    created_by: str = "Sales Demo"


class BusinessEntityCreate(BaseModel):
    """Entitas legal grup (Multi-Entity — Fase 0)."""
    legal_name: str
    short_name: str
    type: str = "PT"            # PT | CV
    npwp: str = ""
    address: str = ""
    city: str = ""
    default_tax_mode: str = "ppn"  # ppn | non_ppn
    doc_prefix: str = ""          # mis. KSC, KANDA — untuk nomor dokumen per entitas
    logo_url: str = ""


class LoginRequest(BaseModel):
    email: str
    password: str


class UserCreate(BaseModel):
    name: str
    email: str
    role: str
    password: str = "demo12345"


class GenericPatch(BaseModel):
    data: Dict[str, Any]


class ProductPayload(BaseModel):
    sku: str
    name: str
    category: str = "Kain"
    variant: str = "Regular"
    color: str = "Natural"
    motif: str = "Polos"
    grade: str = "A"
    supplier: str = "Internal"
    base_unit: str = "meter"
    price: float = 0
    harga_pokok: float = 0
    gramasi: float = 0
    image: str = "https://images.unsplash.com/photo-1774679817333-decf0d988dd5?crop=entropy&cs=srgb&fm=jpg&ixlib=rb-4.1.0&q=85"
    status: str = "active"
    uom_conversions: List[Dict[str, Any]] = []


class WarehousePayload(BaseModel):
    code: str
    name: str
    city: str
    bin_code: str = "A1-01"
    bin_capacity: float = 1000
    lat: Optional[float] = None
    lng: Optional[float] = None


class UOMPayload(BaseModel):
    code: str
    name: str
    base_type: str = "length"
    precision: int = 2


class TemplatePayload(BaseModel):
    document_type: str
    name: str
    header: str = "Kain Nusantara"
    footer: str = "Dokumen dibuat otomatis oleh sistem."
    columns: List[str] = []
    logo_url: str = ""
    paper_size: str = "A4"
    orientation: str = "portrait"
    margin_mm: int = 12
    signature_left: str = "Dibuat Oleh"
    signature_right: str = "Disetujui Oleh"
    section_order: List[str] = ["header", "customer", "items", "allocation", "signature", "footer"]


class PermissionUpdate(BaseModel):
    matrix: Dict[str, Dict[str, List[str]]]


class WMSTaskCreate(BaseModel):
    flow_type: str = "inbound"
    source_type: str = "supplier"
    product_id: str
    quantity: float
    unit: str = "meter"
    warehouse_id: str
    bin_id: str
    batch: str
    lot: str
    roll_id: str


class ScannerScan(BaseModel):
    scan_type: str
    scan_value: str
    actor: str = "Warehouse Demo"


class SalesOrderItemIn(BaseModel):
    product_id: str
    quantity: float
    unit: str
    discount_percent: float = 0          # Fase 1B — diskon per item (0–100%)
    price_approval_id: str = ""          # Sub-fase 1.7 — harga khusus disetujui (override harga)


class SalesOrderCreate(BaseModel):
    customer_id: str
    shipping_address_id: str
    items: List[SalesOrderItemIn]
    sales_name: str = "Ayu Marketing"
    shipment_policy: str = "allow_partial_shipment"
    entity_id: str = ""
    order_discount_percent: float = 0     # Fase 1B — diskon level order (0–100%)
    payment_term_code: str = ""           # Fase 1B — term pembayaran (kode)
    allow_backorder: bool = False         # Sub-fase 1.6 — izinkan reservasi parsial + backorder
    confirm_mixed_lot: bool = False       # Sub-fase 1.7/MixedLot — konfirmasi pemenuhan lintas-lot


class AllocationPreviewItem(BaseModel):
    product_id: str
    quantity: float
    unit: str = "meter"


class AllocationPreviewIn(BaseModel):
    """Preview pemenuhan/ATP per baris SEBELUM order dibuat (Sub-fase 1.4, READ-ONLY)."""
    items: List[AllocationPreviewItem]
    entity_id: str = ""          # entitas penjual; kosong → default/owner customer
    customer_id: str = ""        # opsional (konteks kota; tidak mengubah ATP)


class InterCompanyTransferItem(BaseModel):
    product_id: str
    quantity: float
    unit: str = "meter"


class InterCompanyTransferCreate(BaseModel):
    """Sub-fase 1.5 — minta transfer kepemilikan antar-entitas (B→E) dari preview POS.
    EXTEND warehouse_transfers (transfer_kind=inter_entity)."""
    source_entity_id: str                       # B (pemilik stok)
    dest_entity_id: str                         # E (entitas penjual yang butuh)
    items: List[InterCompanyTransferItem]
    linked_order_id: Optional[str] = None       # SO pemicu (opsional)
    transfer_price: Optional[float] = None      # Fase 4 (nullable; tidak ada dampak akuntansi sekarang)
    notes: str = ""
    requested_by: str = ""


class PaymentSimulationCreate(BaseModel):
    amount: float = 0                    # Fase 1B — opsional; default = grand_total order
    method: str = "Transfer Simulasi"
    created_by: str = "Admin Demo"


class DocumentGenerate(BaseModel):
    document_type: str
    source_id: str
    actor: str = "Admin Demo"


class BarcodeGenerate(BaseModel):
    target_type: str
    target_id: str
    label_size: str = "80x50mm"


WAREHOUSE_PRIORITY = {
    "Jakarta": ["Jakarta", "Bandung", "Surabaya"],
    "Bandung": ["Bandung", "Jakarta", "Surabaya"],
    "Surabaya": ["Surabaya", "Bandung", "Jakarta"],
    "Denpasar": ["Surabaya", "Jakarta", "Bandung"],
}


# ─── Transfer Schemas ────────────────────────────────────────────────────────

class TransferItem(BaseModel):
    product_id: str
    qty: float
    unit: str = "meter"
    batch: str = ""
    lot: str = ""
    roll_id: str = ""


class TransferCreate(BaseModel):
    source_warehouse_id: str
    dest_warehouse_id: str
    items: List[TransferItem]
    notes: str = ""
    requested_by: str = "Warehouse User"


class TransferApprove(BaseModel):
    approved_by: str = "Manager"


class TransferReject(BaseModel):
    rejected_by: str = "Manager"
    reason: str = ""


class TransferStatusUpdate(BaseModel):
    status: str  # picking, staging, dispatched, completed
    updated_by: str = "Warehouse User"


# ─── Purchase Order Schemas ──────────────────────────────────────────────────

class POItemCreate(BaseModel):
    product_id: str
    quantity: float
    unit: str = "meter"
    price: float = 0.0


class PurchaseOrderCreate(BaseModel):
    supplier_name: str
    supplier_contact: str = ""
    warehouse_id: str
    items: List[POItemCreate]
    expected_delivery_date: str = ""
    notes: str = ""
    created_by: str = "Admin"
    entity_id: str = ""


class POReceiveItem(BaseModel):
    product_id: str
    actual_qty: float
    batch: str = ""
    lot: str = ""
    roll_id: str = ""
    bin_id: str = ""


# ─── Inventory Roll Schema (Fase 0.5 — Roll-as-SSOT, KN_15) ──────────────────

class RollPayload(BaseModel):
    product_id: str
    warehouse_id: str
    owner_entity_id: str = ""        # default = entitas utama bila kosong
    lot: str
    quantity: float                  # = length_initial = length_remaining awal
    unit: str = "meter"
    grade: str = "A"
    batch: str = ""
    roll_no: str = ""
    bin_id: str = ""
    tracking_mode: str = "barcode"   # rfid | barcode | document | manual
    ownership_type: str = "internal" # internal | supplier_consignment | reseller_consignment


# ─── Configuration Foundation Schemas (Fase 1A — semua configurable) ─────────

class SettingsUpdate(BaseModel):
    scope: str = "global"            # "global" | entity_id
    tax: Optional[Dict[str, Any]] = None
    finance: Optional[Dict[str, Any]] = None
    sales: Optional[Dict[str, Any]] = None
    inventory: Optional[Dict[str, Any]] = None
    allocation: Optional[Dict[str, Any]] = None   # Sub-fase 1.7 — allocation policy


class PaymentTermPayload(BaseModel):
    code: str
    name: str
    type: str = "credit"             # cash | credit | dp | installment
    net_days: int = 0
    dp_percent: float = 0
    installment_count: int = 0
    sort: int = 99
    active: bool = True


class ApprovalRulePayload(BaseModel):
    doc_type: str                    # sales_order | purchase_order | transfer | discount
    entity_id: str = "all"
    min_amount: float = 0
    max_amount: Optional[float] = None
    required_role: str = ""          # "" = tidak butuh approval
    is_percent: bool = False
    sort: int = 99
    active: bool = True



# ─── Price Approval Schemas (Sub-fase 1.7 — Special Price / Approval Harga) ───

class PriceApprovalCreate(BaseModel):
    customer_id: str
    product_id: str
    requested_price: float               # harga khusus yang diajukan (per unit)
    min_quantity: float = 0              # qty minimum agar harga berlaku
    valid_until: str = ""                # "YYYY-MM-DD" atau ISO; "" = tanpa kadaluarsa
    reason: str = ""
    entity_id: str = ""                  # kosong → resolve dari entitas customer
    submit_now: bool = False             # True → langsung status pending (skip draft)


class PriceApprovalDecision(BaseModel):
    decision_notes: str = ""
