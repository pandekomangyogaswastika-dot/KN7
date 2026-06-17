"""Roll service (Fase 0.5) — Roll-as-SSOT inventory engine.

Implementasi fondasi KN_15:
- `inventory_rolls` = SSOT fisik (1 dokumen = 1 roll). Prefix `roll_`.
- `inventory_balances` = PROYEKSI yang di-rebuild dari rolls (key 3-bagian:
  product_id + warehouse_id + owner_entity_id), bucket DETAIL (KN_15 §3.4).
- Reservasi terjadi di LEVEL ROLL (atomic find_one_and_update available→reserved),
  owner-scoped (roll hanya boleh dijual entitas pemiliknya).

Catatan: alokasi penuh (configurable policy + mixed-lot confirmation UI +
inter-company transfer) adalah Fase 1. Di sini fondasi: owner-scoped + FEFO +
single-warehouse preference + split roll saat reservasi parsial.
"""
from typing import Any, Dict, List, Optional
from fastapi import HTTPException
from pymongo import ReturnDocument
from db import db
from core_utils import now_iso, new_id, DEFAULT_ENTITY_ID
from schemas import WAREHOUSE_PRIORITY

# ── Taksonomi status (KN_15 §3.4) ────────────────────────────────────────────
# Bucket FISIK di gudang (menyusun on_hand)
PHYSICAL_STATUS_TO_BUCKET = {
    "available": "available_qty",
    "reserved": "reserved_qty",
    "committed": "committed_qty",
    "picked": "picked_qty",
    "packed": "packed_qty",
    "quarantine": "quarantine_qty",
    "blocked": "blocked_qty",
    "damaged": "damaged_qty",
}
# Bucket TRANSIT/PIPELINE (di luar gudang fisik)
TRANSIT_STATUS_TO_BUCKET = {
    "in_transit_inbound": "in_transit_inbound_qty",
    "in_transit_transfer": "in_transit_transfer_qty",
    "in_transit_intercompany": "in_transit_intercompany_qty",
    "in_transit_sales": "in_transit_sales_qty",
}
ALL_BUCKETS = list(PHYSICAL_STATUS_TO_BUCKET.values()) + list(TRANSIT_STATUS_TO_BUCKET.values())
# Status roll yang menahan reservasi sebuah order (untuk release)
ORDER_HELD_STATUSES = ["reserved", "committed", "picked", "packed", "in_transit_sales"]

MAX_AVAILABLE_ROLL_LEN = 150.0  # potong sintetis available jadi roll realistis


# ── Rebuild proyeksi balance dari rolls ──────────────────────────────────────

async def rebuild_balance(product_id: str, warehouse_id: str, owner_entity_id: str) -> Dict[str, Any]:
    """Hitung ulang satu segmen balance (product × warehouse × owner) dari rolls."""
    rolls = await db.inventory_rolls.find(
        {"product_id": product_id, "warehouse_id": warehouse_id, "owner_entity_id": owner_entity_id},
        {"_id": 0},
    ).to_list(10000)
    buckets = {b: 0.0 for b in ALL_BUCKETS}
    for r in rolls:
        status = r.get("status")
        length = float(r.get("length_remaining", 0) or 0)
        bucket = PHYSICAL_STATUS_TO_BUCKET.get(status) or TRANSIT_STATUS_TO_BUCKET.get(status)
        if bucket:
            buckets[bucket] += length
    physical = sum(buckets[b] for b in PHYSICAL_STATUS_TO_BUCKET.values())
    on_order = await _on_order_qty(product_id, warehouse_id, owner_entity_id)
    in_transit_total = sum(buckets[b] for b in TRANSIT_STATUS_TO_BUCKET.values())
    owned = physical + in_transit_total
    incoming = on_order + buckets["in_transit_inbound_qty"]
    atp = buckets["available_qty"] + incoming  # horizon penuh; reserved sudah keluar dari available
    doc = {
        "product_id": product_id, "warehouse_id": warehouse_id, "owner_entity_id": owner_entity_id,
        **buckets,
        "on_hand_qty": round(physical, 2),
        "in_transit_qty": round(in_transit_total, 2),  # legacy alias (total transit)
        "on_order_qty": round(on_order, 2),
        "owned_qty": round(owned, 2),
        "incoming_qty": round(incoming, 2),
        "atp_qty": round(atp, 2),
        "updated_at": now_iso(),
    }
    # round bucket
    for b in ALL_BUCKETS:
        doc[b] = round(doc[b], 2)
    existing = await db.inventory_balances.find_one(
        {"product_id": product_id, "warehouse_id": warehouse_id, "owner_entity_id": owner_entity_id},
        {"_id": 0, "id": 1},
    )
    if existing:
        await db.inventory_balances.update_one(
            {"product_id": product_id, "warehouse_id": warehouse_id, "owner_entity_id": owner_entity_id},
            {"$set": doc},
        )
    else:
        doc["id"] = new_id("bal")
        await db.inventory_balances.insert_one(dict(doc))
    return doc


async def _on_order_qty(product_id: str, warehouse_id: str, owner_entity_id: str) -> float:
    """Qty pipeline dari purchase_orders yang belum jadi roll (status belum receiving selesai)."""
    pos = await db.purchase_orders.find(
        {"warehouse_id": warehouse_id, "status": {"$in": ["pending", "created", "approved", "sent"]}},
        {"_id": 0, "items": 1, "entity_id": 1},
    ).to_list(500)
    total = 0.0
    for po in pos:
        if po.get("entity_id") and po.get("entity_id") != owner_entity_id:
            continue
        for it in po.get("items", []):
            if it.get("product_id") == product_id:
                total += float(it.get("quantity", it.get("qty", 0)) or 0)
    return total


async def rebuild_all_balances() -> int:
    """Drop semua balances lalu rebuild dari rolls (segmen unik)."""
    segments = await db.inventory_rolls.aggregate([
        {"$group": {"_id": {"p": "$product_id", "w": "$warehouse_id", "o": "$owner_entity_id"}}}
    ]).to_list(100000)
    await db.inventory_balances.delete_many({})
    for s in segments:
        k = s["_id"]
        await rebuild_balance(k["p"], k["w"], k["o"])
    return len(segments)


# ── Synthetic migration: balances lama → rolls (idempotent) ──────────────────

async def _lot_for_segment(product_id: str, warehouse_id: str) -> str:
    mv = await db.inventory_movements.find_one(
        {"product_id": product_id, "warehouse_id": warehouse_id, "lot": {"$nin": [None, ""]}},
        {"_id": 0, "lot": 1}, sort=[("timestamp", 1)],
    )
    return (mv or {}).get("lot") or "LOT-MIGRATED"


async def generate_rolls_from_balances(created_by: str = "seed") -> Dict[str, int]:
    """Generate inventory_rolls sintetis dari balances lama (KN_15 §11).

    Idempotent: skip bila inventory_rolls sudah berisi. Backfill owner_entity_id
    pada balances & movements, lalu rolls dibuat per bucket, balances di-rebuild.
    """
    if await db.inventory_rolls.count_documents({}) > 0:
        return {"rolls": 0, "skipped": 1}

    # 1) Backfill owner_entity_id pada movements lama (default entitas utama)
    await db.inventory_movements.update_many(
        {"owner_entity_id": {"$exists": False}}, {"$set": {"owner_entity_id": DEFAULT_ENTITY_ID}}
    )

    # 2) Map alokasi SO aktif per (product, warehouse) → list (order_id, qty)
    active_orders = await db.sales_orders.find(
        {"status": {"$in": ["reserved", "waiting_approval", "approved", "confirmed"]}},
        {"_id": 0, "id": 1, "entity_id": 1, "allocations": 1},
    ).to_list(2000)
    alloc_map: Dict[tuple, List[Dict[str, Any]]] = {}
    for o in active_orders:
        for a in o.get("allocations", []):
            key = (a.get("product_id"), a.get("warehouse_id"))
            alloc_map.setdefault(key, []).append({
                "order_id": o["id"],
                "owner": o.get("entity_id") or DEFAULT_ENTITY_ID,
                "qty": float(a.get("quantity", a.get("qty", 0)) or 0),
            })

    products = {p["id"]: p for p in await db.products.find({}, {"_id": 0}).to_list(1000)}
    balances = await db.inventory_balances.find({}, {"_id": 0}).to_list(10000)
    roll_docs: List[Dict[str, Any]] = []
    seq = {"n": 0}

    def _make_roll(product_id, warehouse_id, owner, lot, length, status, reserved_ref=None, grade="A"):
        seq["n"] += 1
        prod = products.get(product_id, {})
        return {
            "id": new_id("roll"),
            "product_id": product_id,
            "owner_entity_id": owner,
            "ownership_type": "internal",
            "consignor_ref": None,
            "warehouse_id": warehouse_id,
            "bin_id": None,
            "lot": lot,
            "batch": lot.replace("LOT", "BATCH") if lot else "",
            "roll_no": f"RL-{seq['n']:05d}",
            "length_initial": round(float(length), 2),
            "length_remaining": round(float(length), 2),
            "unit": prod.get("base_unit", "meter"),
            "grade": prod.get("grade", grade),
            "status": status,
            "tracking_mode": "barcode",
            "earmarked_for": None,
            "location_type": "warehouse_bin",
            "reserved_ref": reserved_ref,
            "unit_cost": None,
            "acquired": {"via": "initial", "ref_id": "seed", "date": now_iso()},
            "rfid_tag_id": None,
            "is_remnant": False,
            "created_at": now_iso(), "updated_at": now_iso(),
            "created_by": created_by, "created_by_name": "System Seed",
        }

    for b in balances:
        product_id = b.get("product_id")
        warehouse_id = b.get("warehouse_id")
        owner = b.get("owner_entity_id") or DEFAULT_ENTITY_ID
        lot = await _lot_for_segment(product_id, warehouse_id)
        reserved_qty = float(b.get("reserved_qty", 0) or 0)
        available_qty = float(b.get("available_qty", 0) or 0)
        blocked_qty = float(b.get("blocked_qty", 0) or 0)
        picked_qty = float(b.get("picked_qty", 0) or 0)

        # Reserved rolls — distribusi ke SO aktif (link reserved_ref) lalu sisa generik
        remaining_reserved = reserved_qty
        for alloc in alloc_map.get((product_id, warehouse_id), []):
            if remaining_reserved <= 0.01:
                break
            take = min(alloc["qty"], remaining_reserved)
            if take <= 0.01:
                continue
            roll_docs.append(_make_roll(
                product_id, warehouse_id, owner, lot, take, "reserved",
                reserved_ref={"type": "sales_order", "id": alloc["order_id"]},
            ))
            remaining_reserved -= take
        if remaining_reserved > 0.01:
            roll_docs.append(_make_roll(
                product_id, warehouse_id, owner, lot, remaining_reserved, "reserved",
                reserved_ref={"type": "seed", "id": "seed"},
            ))

        # Blocked / picked rolls (jika ada di seed)
        if blocked_qty > 0.01:
            roll_docs.append(_make_roll(product_id, warehouse_id, owner, lot, blocked_qty, "blocked"))
        if picked_qty > 0.01:
            roll_docs.append(_make_roll(product_id, warehouse_id, owner, lot, picked_qty, "picked"))

        # Available rolls — potong jadi roll realistis
        remaining_avail = available_qty
        while remaining_avail > 0.01:
            take = min(remaining_avail, MAX_AVAILABLE_ROLL_LEN)
            roll_docs.append(_make_roll(product_id, warehouse_id, owner, lot, take, "available"))
            remaining_avail -= take

    if roll_docs:
        await db.inventory_rolls.insert_many(roll_docs)

    n_segments = await rebuild_all_balances()
    return {"rolls": len(roll_docs), "segments": n_segments, "skipped": 0}


# ── Reservasi level-roll (owner-scoped, FEFO, single-warehouse preference) ────

async def _reserve_single_roll(roll_id: str, order_id: str) -> Optional[Dict[str, Any]]:
    return await db.inventory_rolls.find_one_and_update(
        {"id": roll_id, "status": "available"},
        {"$set": {"status": "reserved", "reserved_ref": {"type": "sales_order", "id": order_id},
                  "updated_at": now_iso()}},
        projection={"_id": 0}, return_document=ReturnDocument.AFTER,
    )


async def _split_roll(roll: Dict[str, Any], take: float, order_id: str) -> Dict[str, Any]:
    """Pecah roll available: kurangi sisa parent, buat child roll reserved sebesar `take`."""
    parent_remaining = float(roll["length_remaining"]) - take
    await db.inventory_rolls.update_one(
        {"id": roll["id"]},
        {"$set": {"length_remaining": round(parent_remaining, 2),
                  "length_initial": round(float(roll["length_initial"]) - take, 2),
                  "updated_at": now_iso()}},
    )
    child = dict(roll)
    child.pop("_id", None)
    child.update({
        "id": new_id("roll"),
        "length_initial": round(take, 2),
        "length_remaining": round(take, 2),
        "status": "reserved",
        "reserved_ref": {"type": "sales_order", "id": order_id},
        "is_remnant": False,
        "created_at": now_iso(), "updated_at": now_iso(),
    })
    await db.inventory_rolls.insert_one(dict(child))
    return child


async def allocate_and_reserve_rolls(
    product_id: str, quantity: float, city: str, owner_entity_id: str, order_id: str,
    allow_partial: bool = False,
) -> List[Dict[str, Any]]:
    """Reservasi roll owner-scoped untuk 1 baris order. Mengembalikan daftar alokasi
    (per warehouse) yang kompatibel dengan struktur SO lama + info roll/lot.

    Sub-fase 1.6 — Backorder:
      - `allow_partial=False` (default): perilaku lama. Bila stok < quantity → 409.
      - `allow_partial=True`: reservasi hanya sebesar stok yang TERSEDIA (tidak 409).
        Bila stok 0 → kembalikan [] (full backorder). Caller menghitung
        backorder_qty = quantity − Σ(allocations.quantity).
    """
    warehouses = {w["id"]: w for w in await db.warehouses.find({}, {"_id": 0}).to_list(100)}
    priority = WAREHOUSE_PRIORITY.get(city, [city, "Jakarta", "Bandung", "Surabaya"])

    rolls = await db.inventory_rolls.find(
        {"product_id": product_id, "owner_entity_id": owner_entity_id, "status": "available",
         "length_remaining": {"$gt": 0}}, {"_id": 0},
    ).to_list(10000)

    def wh_rank(wid: str) -> int:
        c = warehouses.get(wid, {}).get("city", "")
        return priority.index(c) if c in priority else 99

    # Urutkan: warehouse terdekat → lot tertua (FEFO via created_at) → roll besar dulu
    rolls.sort(key=lambda r: (wh_rank(r["warehouse_id"]), r.get("created_at", ""),
                              -float(r.get("length_remaining", 0))))

    total_available = sum(float(r["length_remaining"]) for r in rolls)
    if total_available + 0.01 < quantity:
        if not allow_partial:
            raise HTTPException(
                status_code=409,
                detail=f"Stok milik entitas tidak mencukupi (tersedia {round(total_available,2)} dari {quantity}). "
                       f"Aktifkan backorder untuk memesan sisa stok yang akan datang.",
            )
        # Backorder mode: reservasi hanya sebesar yang tersedia
        effective_qty = round(total_available, 2)
    else:
        effective_qty = quantity

    if effective_qty <= 0.01:
        # Tidak ada stok sama sekali → full backorder (caller yang catat)
        return []

    remaining = effective_qty
    per_wh: Dict[str, Dict[str, Any]] = {}

    for roll in rolls:
        if remaining <= 0.01:
            break
        rlen = float(roll["length_remaining"])
        wid = roll["warehouse_id"]
        bucket = per_wh.setdefault(wid, {"qty": 0.0, "rolls": [], "lots": set()})
        if rlen <= remaining + 0.01:
            reserved = await _reserve_single_roll(roll["id"], order_id)
            if not reserved:
                continue  # keburu diambil order lain → lewati
            take = float(reserved["length_remaining"])
            bucket["rolls"].append({"roll_id": reserved["id"], "roll_no": reserved.get("roll_no"),
                                    "lot": reserved.get("lot"), "length": take})
            bucket["lots"].add(reserved.get("lot"))
            bucket["qty"] += take
            remaining -= take
        else:
            # roll lebih besar dari kebutuhan → split
            child = await _split_roll(roll, remaining, order_id)
            bucket["rolls"].append({"roll_id": child["id"], "roll_no": child.get("roll_no"),
                                    "lot": child.get("lot"), "length": float(child["length_remaining"])})
            bucket["lots"].add(child.get("lot"))
            bucket["qty"] += float(child["length_remaining"])
            remaining = 0.0
            break

    if remaining > 0.01:
        if not allow_partial:
            # gagal mereservasi cukup (race) → rollback lalu error
            await release_order_rolls(order_id)
            raise HTTPException(status_code=409, detail="Stok berubah saat reservasi. Silakan refresh katalog.")
        # Mode backorder: terima reservasi parsial apa adanya (sisa jadi backorder).
        # Bila tak ada satu pun roll yang ter-reserve → tidak ada alokasi.

    allocations: List[Dict[str, Any]] = []
    for wid, info in per_wh.items():
        wh = warehouses.get(wid, {})
        lots = sorted(x for x in info["lots"] if x)
        allocations.append({
            "id": new_id("alloc"),
            "product_id": product_id,
            "warehouse_id": wid,
            "warehouse_name": wh.get("name", wid),
            "warehouse_city": wh.get("city", ""),
            "owner_entity_id": owner_entity_id,
            "quantity": round(info["qty"], 2),
            "lot": lots[0] if len(lots) == 1 else None,
            "lots": lots,
            "lot_mode": "single" if len(lots) <= 1 else "mixed",
            "rolls": info["rolls"],
            "status": "allocated",
        })
        # ledger movement per warehouse
        await db.inventory_movements.insert_one({
            "id": new_id("mov"), "product_id": product_id, "warehouse_id": wid,
            "owner_entity_id": owner_entity_id, "movement_type": "reservation",
            "quantity": round(info["qty"], 2), "unit": wh.get("unit", "meter"),
            "lot": lots[0] if lots else "", "roll_id": ",".join(r["roll_id"] for r in info["rolls"]),
            "source_document": order_id, "timestamp": now_iso(),
        })
        await rebuild_balance(product_id, wid, owner_entity_id)
    return allocations


async def release_order_rolls(order_id: str) -> float:
    """Lepas semua roll yang ter-reserve untuk order tertentu → kembali available.
    Mengembalikan total qty yang dilepas. Rebuild balance segmen terdampak."""
    held = await db.inventory_rolls.find(
        {"reserved_ref.id": order_id, "status": {"$in": ORDER_HELD_STATUSES}}, {"_id": 0},
    ).to_list(10000)
    if not held:
        return 0.0
    segments = set()
    total = 0.0
    for r in held:
        await db.inventory_rolls.update_one(
            {"id": r["id"]},
            {"$set": {"status": "available", "reserved_ref": None, "updated_at": now_iso()}},
        )
        total += float(r.get("length_remaining", 0) or 0)
        segments.add((r["product_id"], r["warehouse_id"], r["owner_entity_id"]))
        await db.inventory_movements.insert_one({
            "id": new_id("mov"), "product_id": r["product_id"], "warehouse_id": r["warehouse_id"],
            "owner_entity_id": r["owner_entity_id"], "movement_type": "release_reservation",
            "quantity": round(float(r.get("length_remaining", 0) or 0), 2), "unit": r.get("unit", "meter"),
            "lot": r.get("lot", ""), "roll_id": r["id"], "source_document": order_id, "timestamp": now_iso(),
        })
    for p, w, o in segments:
        await rebuild_balance(p, w, o)
    return round(total, 2)


async def set_order_rolls_status(order_id: str, new_status: str) -> int:
    """Ubah status roll milik order (mis. reserved→committed saat approve)."""
    held = await db.inventory_rolls.find(
        {"reserved_ref.id": order_id, "status": {"$in": ORDER_HELD_STATUSES}}, {"_id": 0},
    ).to_list(10000)
    segments = set()
    for r in held:
        await db.inventory_rolls.update_one(
            {"id": r["id"]}, {"$set": {"status": new_status, "updated_at": now_iso()}}
        )
        segments.add((r["product_id"], r["warehouse_id"], r["owner_entity_id"]))
    for p, w, o in segments:
        await rebuild_balance(p, w, o)
    return len(held)


# ── Inter-company ownership transfer (Sub-fase 1.5, KN_15 §7 + D3) ────────────

def _split_roll_for_ref(roll: Dict[str, Any], take: float, ref: Dict[str, Any]) -> Dict[str, Any]:
    """Bangun child-roll reserved sebesar `take` dengan reserved_ref generik (mis. transfer).
    (Caller wajib meng-update parent length & insert child — lihat reserve_rolls_for_transfer.)"""
    child = dict(roll)
    child.pop("_id", None)
    child.update({
        "id": new_id("roll"),
        "length_initial": round(take, 2),
        "length_remaining": round(take, 2),
        "status": "reserved",
        "reserved_ref": ref,
        "is_remnant": False,
        "created_at": now_iso(), "updated_at": now_iso(),
    })
    return child


async def reserve_rolls_for_transfer(
    product_id: str, source_entity_id: str, quantity: float, transfer_id: str
) -> List[Dict[str, Any]]:
    """Reservasi roll milik entitas SUMBER (B) untuk inter-company transfer (FEFO, split).
    Set status=reserved, reserved_ref={type:'transfer', id:transfer_id} agar B tak dobel-jual.
    Mengembalikan daftar roll yang direservasi. Raise 409 bila stok B tak cukup."""
    ref = {"type": "transfer", "id": transfer_id}
    rolls = await db.inventory_rolls.find(
        {"product_id": product_id, "owner_entity_id": source_entity_id, "status": "available",
         "length_remaining": {"$gt": 0}}, {"_id": 0},
    ).to_list(10000)
    # FEFO: lot tertua (created_at) dulu, roll besar dulu
    rolls.sort(key=lambda r: (r.get("created_at", ""), -float(r.get("length_remaining", 0))))

    total = sum(float(r["length_remaining"]) for r in rolls)
    if total + 0.01 < quantity:
        raise HTTPException(
            status_code=409,
            detail=f"Stok entitas sumber tidak cukup untuk transfer (tersedia {round(total,2)} dari {quantity}).",
        )

    remaining = quantity
    reserved: List[Dict[str, Any]] = []
    for roll in rolls:
        if remaining <= 0.01:
            break
        rlen = float(roll["length_remaining"])
        if rlen <= remaining + 0.01:
            updated = await db.inventory_rolls.find_one_and_update(
                {"id": roll["id"], "status": "available"},
                {"$set": {"status": "reserved", "reserved_ref": ref, "updated_at": now_iso()}},
                projection={"_id": 0}, return_document=ReturnDocument.AFTER,
            )
            if not updated:
                continue  # keburu diambil transaksi lain
            reserved.append(updated)
            remaining -= float(updated["length_remaining"])
        else:
            # roll lebih besar dari kebutuhan → split: kurangi parent, buat child reserved
            child = _split_roll_for_ref(roll, remaining, ref)
            parent_remaining = rlen - remaining
            await db.inventory_rolls.update_one(
                {"id": roll["id"]},
                {"$set": {"length_remaining": round(parent_remaining, 2),
                          "length_initial": round(float(roll["length_initial"]) - remaining, 2),
                          "updated_at": now_iso()}},
            )
            await db.inventory_rolls.insert_one(dict(child))
            reserved.append(child)
            remaining = 0.0
            break

    if remaining > 0.01:
        # race condition → rollback reservasi parsial
        await release_transfer_rolls(transfer_id)
        raise HTTPException(status_code=409, detail="Stok sumber berubah saat reservasi transfer. Coba lagi.")

    segments = {(r["product_id"], r["warehouse_id"], r["owner_entity_id"]) for r in reserved}
    for p, w, o in segments:
        await rebuild_balance(p, w, o)
    return reserved


async def execute_ownership_transfer(transfer: Dict[str, Any]) -> Dict[str, Any]:
    """Pindahkan kepemilikan roll yang direservasi transfer dari source→dest (S3: SAAT APPROVE).
    owner_entity_id B→E, acquired.via='transfer', status kembali 'available' (kini milik E).
    Catat movement ownership_transfer_out (B) + ownership_transfer_in (E). Rebuild balance kedua segmen."""
    transfer_id = transfer["id"]
    src = transfer["source_entity_id"]
    dst = transfer["dest_entity_id"]
    held = await db.inventory_rolls.find(
        {"reserved_ref.id": transfer_id, "reserved_ref.type": "transfer", "status": "reserved"},
        {"_id": 0},
    ).to_list(10000)
    segments = set()
    moved = 0.0
    for r in held:
        qty = float(r.get("length_remaining", 0) or 0)
        await db.inventory_rolls.update_one(
            {"id": r["id"]},
            {"$set": {"owner_entity_id": dst, "status": "available", "reserved_ref": None,
                      "acquired": {"via": "transfer", "ref_id": transfer_id, "date": now_iso()},
                      "updated_at": now_iso()}},
        )
        moved += qty
        base_mov = {
            "product_id": r["product_id"], "warehouse_id": r["warehouse_id"],
            "unit": r.get("unit", "meter"), "lot": r.get("lot", ""), "roll_id": r["id"],
            "from_owner_entity_id": src, "to_owner_entity_id": dst,
            "source_document": transfer.get("code", transfer_id), "timestamp": now_iso(),
        }
        await db.inventory_movements.insert_one({
            **base_mov, "id": new_id("mov"), "owner_entity_id": src,
            "movement_type": "ownership_transfer_out", "quantity": -round(qty, 2),
        })
        await db.inventory_movements.insert_one({
            **base_mov, "id": new_id("mov"), "owner_entity_id": dst,
            "movement_type": "ownership_transfer_in", "quantity": round(qty, 2),
        })
        segments.add((r["product_id"], r["warehouse_id"], src))
        segments.add((r["product_id"], r["warehouse_id"], dst))
    for p, w, o in segments:
        await rebuild_balance(p, w, o)
    return {"moved_qty": round(moved, 2), "rolls": len(held)}


async def release_transfer_rolls(transfer_id: str) -> float:
    """Lepas roll yang direservasi untuk transfer (reject/cancel) → kembali available milik sumber."""
    held = await db.inventory_rolls.find(
        {"reserved_ref.id": transfer_id, "reserved_ref.type": "transfer", "status": "reserved"},
        {"_id": 0},
    ).to_list(10000)
    segments = set()
    total = 0.0
    for r in held:
        await db.inventory_rolls.update_one(
            {"id": r["id"]},
            {"$set": {"status": "available", "reserved_ref": None, "updated_at": now_iso()}},
        )
        total += float(r.get("length_remaining", 0) or 0)
        segments.add((r["product_id"], r["warehouse_id"], r["owner_entity_id"]))
    for p, w, o in segments:
        await rebuild_balance(p, w, o)
    return round(total, 2)
