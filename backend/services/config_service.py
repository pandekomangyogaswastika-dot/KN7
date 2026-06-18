"""Config service (Fase 1A) — Configuration Foundation.

Prinsip user: SEMUA CONFIGURABLE, TIDAK ADA HARDCODE.
- `system_settings`  (prefix set_)    : pengaturan global + override per-entitas
- `payment_terms`    (prefix pterm_)  : term pembayaran (tunai/kredit/DP/bertahap)
- `approval_rules`   (prefix aprule_) : matriks approval per dokumen/entitas/threshold

config_service menyediakan resolver "effective settings" (global di-override entitas),
kalkulasi pajak (PPN excluded/included), dan evaluasi approval.
"""
from typing import Any, Dict, List, Optional
from db import db
from core_utils import now_iso, new_id, DEFAULT_ENTITY_ID

GLOBAL_SCOPE = "global"

# Default global settings (seed sekali, lalu editable dari Admin → Pengaturan)
DEFAULT_GLOBAL_SETTINGS: Dict[str, Any] = {
    "tax": {
        "ppn_rate": 11.0,            # %
        "ppn_mode": "excluded",     # excluded = ditambah saat invoice | included
        "efaktur_enabled": True,    # PKP terbit Faktur Pajak
    },
    "finance": {
        "base_currency": "IDR",
        "fiscal_year_end_month": 12,
        "default_payment_term_code": "NET30",
    },
    "sales": {
        "quotation_enabled": False,
        "allow_partial_shipment": True,
        "allow_order_discount": True,
        "allow_item_discount": True,
    },
    "inventory": {
        "default_uom": "meter",
        "min_cut_qty": 0.5,
        "intercompany_transfer_required": True,  # KN_15 D-? — jual stok entitas lain wajib transfer
    },
    # Sub-fase 1.7 — Allocation Policy (KN_15 §6.0) — CONFIGURABLE + CLARITY
    "allocation": {
        "mode": "auto",                                            # auto | assisted | manual
        "priority_order": ["owner", "lot", "location", "roll_efficiency"],  # owner selalu HARD #1
        "lot_mode": "prefer_single",                               # prefer_single | strict_single | allow_mixed
        "lot_selection": "fefo",                                   # fefo | fifo | smallest_fit | largest_fit
        "location_pref": "single_warehouse",                       # single_warehouse | nearest_customer | fewest_splits
        "allow_intercompany": True,
        "allow_partial": True,
    },
}

DEFAULT_PAYMENT_TERMS: List[Dict[str, Any]] = [
    {"code": "CASH",  "name": "Tunai / POS",          "type": "cash",        "net_days": 0,  "dp_percent": 0,  "installment_count": 0, "sort": 1},
    {"code": "NET7",  "name": "Kredit NET 7 Hari",    "type": "credit",      "net_days": 7,  "dp_percent": 0,  "installment_count": 0, "sort": 2},
    {"code": "NET14", "name": "Kredit NET 14 Hari",   "type": "credit",      "net_days": 14, "dp_percent": 0,  "installment_count": 0, "sort": 3},
    {"code": "NET30", "name": "Kredit NET 30 Hari",   "type": "credit",      "net_days": 30, "dp_percent": 0,  "installment_count": 0, "sort": 4},
    {"code": "DP50",  "name": "DP 50% + Pelunasan",   "type": "dp",          "net_days": 14, "dp_percent": 50, "installment_count": 0, "sort": 5},
    {"code": "INST3", "name": "Bertahap 3x",          "type": "installment", "net_days": 30, "dp_percent": 0,  "installment_count": 3, "sort": 6},
]

DEFAULT_APPROVAL_RULES: List[Dict[str, Any]] = [
    {"doc_type": "sales_order",    "entity_id": "all", "min_amount": 0,         "max_amount": 50000000,  "required_role": "",        "sort": 1},
    {"doc_type": "sales_order",    "entity_id": "all", "min_amount": 50000000,  "max_amount": 200000000, "required_role": "manager", "sort": 2},
    {"doc_type": "sales_order",    "entity_id": "all", "min_amount": 200000000, "max_amount": None,       "required_role": "admin",   "sort": 3},
    {"doc_type": "discount",       "entity_id": "all", "min_amount": 0,         "max_amount": 10,         "required_role": "",        "sort": 1, "is_percent": True},
    {"doc_type": "discount",       "entity_id": "all", "min_amount": 10,        "max_amount": None,       "required_role": "manager", "sort": 2, "is_percent": True},
    {"doc_type": "purchase_order", "entity_id": "all", "min_amount": 0,         "max_amount": 100000000, "required_role": "",        "sort": 1},
    {"doc_type": "purchase_order", "entity_id": "all", "min_amount": 100000000, "max_amount": None,       "required_role": "manager", "sort": 2},
]


# ── Seed defaults (idempotent) ───────────────────────────────────────────────

async def seed_config_defaults() -> Dict[str, int]:
    created = {"settings": 0, "payment_terms": 0, "approval_rules": 0}
    if await db.system_settings.count_documents({"scope": GLOBAL_SCOPE}) == 0:
        await db.system_settings.insert_one({
            "id": new_id("set"), "scope": GLOBAL_SCOPE,
            **DEFAULT_GLOBAL_SETTINGS,
            "created_at": now_iso(), "updated_at": now_iso(),
        })
        created["settings"] = 1
    if await db.payment_terms.count_documents({}) == 0:
        await db.payment_terms.insert_many([
            {"id": new_id("pterm"), **t, "active": True,
             "created_at": now_iso(), "updated_at": now_iso()} for t in DEFAULT_PAYMENT_TERMS
        ])
        created["payment_terms"] = len(DEFAULT_PAYMENT_TERMS)
    if await db.approval_rules.count_documents({}) == 0:
        await db.approval_rules.insert_many([
            {"id": new_id("aprule"), "is_percent": r.get("is_percent", False), "active": True,
             "created_at": now_iso(), "updated_at": now_iso(),
             **{k: v for k, v in r.items() if k != "is_percent"}} for r in DEFAULT_APPROVAL_RULES
        ])
        created["approval_rules"] = len(DEFAULT_APPROVAL_RULES)
    return created


# ── Effective settings (global di-override per-entitas) ──────────────────────

def _deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    out = dict(base)
    for k, v in (override or {}).items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _deep_merge(out[k], v)
        else:
            out[k] = v
    return out


async def get_global_settings() -> Dict[str, Any]:
    doc = await db.system_settings.find_one({"scope": GLOBAL_SCOPE}, {"_id": 0})
    if not doc:
        await seed_config_defaults()
        doc = await db.system_settings.find_one({"scope": GLOBAL_SCOPE}, {"_id": 0})
    return doc or {"scope": GLOBAL_SCOPE, **DEFAULT_GLOBAL_SETTINGS}


async def get_effective_settings(entity_id: Optional[str] = None) -> Dict[str, Any]:
    base = await get_global_settings()
    sections = {k: v for k, v in base.items() if isinstance(v, dict)}
    if entity_id and entity_id != "all":
        override = await db.system_settings.find_one({"scope": entity_id}, {"_id": 0})
        if override:
            ov_sections = {k: v for k, v in override.items() if isinstance(v, dict)}
            sections = _deep_merge(sections, ov_sections)
        # entitas PKP/non-PKP mempengaruhi pajak efektif
        entity = await db.business_entities.find_one({"id": entity_id}, {"_id": 0})
        if entity:
            is_pkp = (entity.get("default_tax_mode") == "ppn")
            sections.setdefault("tax", {})
            sections["tax"] = dict(sections.get("tax", {}))
            sections["tax"]["is_pkp"] = is_pkp
            if not is_pkp:
                sections["tax"]["ppn_rate"] = 0.0
                sections["tax"]["efaktur_enabled"] = False
    else:
        sections.setdefault("tax", {})
        sections["tax"] = dict(sections.get("tax", {}))
        sections["tax"]["is_pkp"] = True
    return {"scope": entity_id or "all", **sections}


# ── Kalkulasi pajak (PPN) ────────────────────────────────────────────────────

async def compute_tax(subtotal: float, entity_id: Optional[str] = None) -> Dict[str, Any]:
    s = await get_effective_settings(entity_id)
    tax = s.get("tax", {})
    rate = float(tax.get("ppn_rate", 0) or 0)
    mode = tax.get("ppn_mode", "excluded")
    is_pkp = tax.get("is_pkp", True)
    subtotal = round(float(subtotal or 0), 2)
    if not is_pkp or rate <= 0:
        return {"ppn_rate": 0.0, "ppn_mode": mode, "is_pkp": is_pkp, "dpp": subtotal,
                "ppn_amount": 0.0, "grand_total": subtotal}
    if mode == "included":
        dpp = round(subtotal / (1 + rate / 100), 2)
        ppn = round(subtotal - dpp, 2)
        grand = subtotal
    else:  # excluded (default)
        dpp = subtotal
        ppn = round(subtotal * rate / 100, 2)
        grand = round(subtotal + ppn, 2)
    return {"ppn_rate": rate, "ppn_mode": mode, "is_pkp": is_pkp,
            "dpp": dpp, "ppn_amount": ppn, "grand_total": grand}


# ── Evaluasi approval (matriks configurable) ─────────────────────────────────

async def evaluate_approval(doc_type: str, amount: float, entity_id: Optional[str] = None) -> Dict[str, Any]:
    """Tentukan apakah dokumen butuh approval & role minimum, dari approval_rules.
    Rule entitas-spesifik diutamakan; fallback ke entity_id='all'. amount untuk
    doc_type='discount' adalah persen (is_percent)."""
    rules = await db.approval_rules.find(
        {"doc_type": doc_type, "active": True}, {"_id": 0}
    ).sort("sort", 1).to_list(200)
    scoped = [r for r in rules if r.get("entity_id") == entity_id] if entity_id else []
    pool = scoped if scoped else [r for r in rules if r.get("entity_id") in (None, "all")]
    amount = float(amount or 0)
    for r in pool:
        lo = float(r.get("min_amount", 0) or 0)
        hi = r.get("max_amount")
        hi = float(hi) if hi is not None else float("inf")
        if lo <= amount < hi or (amount == hi == float("inf")):
            role = r.get("required_role") or ""
            return {"requires_approval": bool(role), "required_role": role or None,
                    "rule_id": r.get("id"), "doc_type": doc_type}
    return {"requires_approval": False, "required_role": None, "rule_id": None, "doc_type": doc_type}


# ── Pricing engine (Fase 1B) — diskon + PPN, INVARIAN-SAFE ───────────────────
# PENTING (verify_data_integrity L4): item.subtotal = price×quantity (GROSS) dan
# order.total_amount = Σ subtotal (GROSS) HARUS dipertahankan. Diskon & pajak
# disimpan di FIELD TERPISAH (discount_amount/line_total/net_subtotal/dpp/ppn/
# grand_total) sehingga invarian akuntansi lama tetap valid.

def _clamp_pct(v: float) -> float:
    try:
        return max(0.0, min(100.0, float(v or 0)))
    except (TypeError, ValueError):
        return 0.0


async def compute_order_pricing(
    raw_items: List[Dict[str, Any]],
    entity_id: Optional[str] = None,
    order_discount_percent: float = 0.0,
    settings: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Hitung breakdown harga order: gross subtotal, diskon item, diskon order,
    DPP, PPN, grand total. Menghormati toggle settings.sales.allow_*_discount &
    PKP/non-PKP entitas. `raw_items` = list {price, quantity, discount_percent?, ...}.

    Mengembalikan dict siap-simpan (items diperkaya + agregat). INVARIAN-SAFE:
      - item.subtotal = price × quantity   (GROSS, tak terpengaruh diskon)
      - total_amount  = Σ item.subtotal    (GROSS)
      - net_subtotal  = DPP base = total_amount − items_discount − order_discount
    """
    s = settings or await get_effective_settings(entity_id)
    sales_cfg = s.get("sales", {})
    allow_item = bool(sales_cfg.get("allow_item_discount", True))
    allow_order = bool(sales_cfg.get("allow_order_discount", True))

    priced_items: List[Dict[str, Any]] = []
    gross_total = 0.0
    items_discount_total = 0.0
    for it in raw_items:
        price = round(float(it.get("price", 0) or 0), 2)
        qty = float(it.get("quantity", 0) or 0)
        subtotal = round(price * qty, 2)                      # GROSS — invarian
        disc_pct = _clamp_pct(it.get("discount_percent", 0)) if allow_item else 0.0
        disc_amt = round(subtotal * disc_pct / 100.0, 2)
        line_total = round(subtotal - disc_amt, 2)
        enriched = dict(it)
        enriched.update({
            "price": price, "subtotal": subtotal,
            "discount_percent": disc_pct, "discount_amount": disc_amt,
            "line_total": line_total,
        })
        priced_items.append(enriched)
        gross_total += subtotal
        items_discount_total += disc_amt

    gross_total = round(gross_total, 2)
    items_discount_total = round(items_discount_total, 2)
    after_item = round(gross_total - items_discount_total, 2)
    order_disc_pct = _clamp_pct(order_discount_percent) if allow_order else 0.0
    order_disc_amt = round(after_item * order_disc_pct / 100.0, 2)
    net_subtotal = round(after_item - order_disc_amt, 2)      # = DPP base

    tax = await compute_tax(net_subtotal, entity_id)
    return {
        "items": priced_items,
        "total_amount": gross_total,                          # GROSS (invarian)
        "items_discount_total": items_discount_total,
        "order_discount_percent": order_disc_pct,
        "order_discount_amount": order_disc_amt,
        "discount_total": round(items_discount_total + order_disc_amt, 2),
        "net_subtotal": net_subtotal,
        "dpp": tax["dpp"],
        "ppn_rate": tax["ppn_rate"],
        "ppn_mode": tax["ppn_mode"],
        "is_pkp": tax["is_pkp"],
        "ppn_amount": tax["ppn_amount"],
        "grand_total": tax["grand_total"],
    }


def role_satisfies(actor_role: str, required_role: Optional[str]) -> bool:
    """Cek apakah role aktor memenuhi required_role dari matriks approval.
    Hirarki flat: admin(3) > manager(2) > sales/warehouse(1). required '' = tanpa
    approval (siapa pun yang boleh update). admin selalu lolos."""
    rank = {"sales": 1, "warehouse": 1, "manager": 2, "admin": 3}
    need = {"": 0, None: 0, "manager": 2, "admin": 3}.get(required_role or "", 2)
    return rank.get(actor_role, 0) >= need


# ── Allocation Policy resolver (Sub-fase 1.7, KN_15 §6.0) ────────────────────
# Hierarki override: order > customer > system-settings(default). OWNER selalu HARD #1.

VALID_ALLOC = {
    "mode": {"auto", "assisted", "manual"},
    "lot_mode": {"prefer_single", "strict_single", "allow_mixed"},
    "lot_selection": {"fefo", "fifo", "smallest_fit", "largest_fit"},
    "location_pref": {"single_warehouse", "nearest_customer", "fewest_splits"},
}


def _sanitize_alloc(policy: Dict[str, Any], base: Dict[str, Any]) -> Dict[str, Any]:
    """Pastikan nilai enum valid; jika tidak, pakai base/default."""
    out = dict(base)
    for k, v in (policy or {}).items():
        if k in VALID_ALLOC:
            out[k] = v if v in VALID_ALLOC[k] else base.get(k)
        elif k in ("allow_intercompany", "allow_partial"):
            out[k] = bool(v)
        elif k == "priority_order" and isinstance(v, list) and v:
            # owner selalu #1 (HARD)
            rest = [x for x in v if x in ("lot", "location", "roll_efficiency")]
            out[k] = ["owner"] + [x for x in rest if x != "owner"]
        elif k in out:
            out[k] = v
    return out


async def get_allocation_policy(
    entity_id: Optional[str] = None,
    customer: Optional[Dict[str, Any]] = None,
    order_overrides: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Effective allocation policy: system(global+entity) → customer.allocation_policy → order_overrides."""
    s = await get_effective_settings(entity_id)
    base = dict(DEFAULT_GLOBAL_SETTINGS["allocation"])
    base = _sanitize_alloc(s.get("allocation", {}) or {}, base)
    if customer and isinstance(customer.get("allocation_policy"), dict):
        base = _sanitize_alloc(customer["allocation_policy"], base)
    # Customer lot_policy (KN_15 R4) → peta ke lot_mode bila ada
    cust_lot_policy = (customer or {}).get("lot_policy")
    lot_policy_map = {"strict_single": "strict_single", "prefer_single": "prefer_single", "allow_mixed": "allow_mixed"}
    if cust_lot_policy in lot_policy_map:
        base["lot_mode"] = lot_policy_map[cust_lot_policy]
    if order_overrides:
        base = _sanitize_alloc(order_overrides, base)
    return base

