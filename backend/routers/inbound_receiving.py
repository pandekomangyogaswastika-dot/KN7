"""Inbound Receiving router: scan-based receiving with escalation."""
from typing import Any, Dict, List
from fastapi import APIRouter, HTTPException, Request
from pymongo import ReturnDocument
from db import db
from dependencies import require_permission, audit
from core_utils import new_id, now_iso, safe_doc, DEFAULT_ENTITY_ID
from schemas import POReceiveItem

router = APIRouter(prefix="/api")


@router.get("/inbound/tasks")
async def list_inbound_tasks(request: Request, status: str = None) -> List[Dict[str, Any]]:
    """List all inbound receiving tasks, optionally filtered by status."""
    await require_permission(request, "wms", "view")
    
    query = {"flow_type": "inbound", "source_type": "purchase_order"}
    if status:
        query["status"] = status
    
    tasks = await db.wms_tasks.find(query, {"_id": 0}).sort("created_at", -1).to_list(200)
    
    # Enrich with PO info
    po_ids = list(set(t.get("po_id") for t in tasks if t.get("po_id")))
    pos = {p["id"]: p for p in await db.purchase_orders.find({"id": {"$in": po_ids}}, {"_id": 0}).to_list(100)}
    
    for task in tasks:
        if task.get("po_id"):
            po = pos.get(task["po_id"], {})
            task["supplier_name"] = po.get("supplier_name", "")
    
    return tasks


@router.post("/inbound/tasks/{task_id}/scan-receive")
async def scan_receive_item(
    task_id: str,
    payload: POReceiveItem,
    request: Request
) -> Dict[str, Any]:
    """
    Scan and receive item for inbound task.
    
    Updates received_qty and tracks batch/lot/roll/bin.
    If received_qty reaches expected_qty, auto-advance to next stage.
    """
    actor = await require_permission(request, "wms", "update")
    
    task = safe_doc(await db.wms_tasks.find_one({"id": task_id}, {"_id": 0}))
    if not task:
        raise HTTPException(status_code=404, detail="Inbound task tidak ditemukan")
    
    if task.get("flow_type") != "inbound":
        raise HTTPException(status_code=400, detail="Task ini bukan inbound task")
    
    if task["status"] in ["completed", "cancelled"]:
        raise HTTPException(status_code=400, detail="Task sudah selesai atau dibatalkan")
    
    # Validate product match
    if payload.product_id != task["product_id"]:
        raise HTTPException(status_code=400, detail="Product ID tidak sesuai dengan task")
    
    # Update received qty
    new_received_qty = task.get("received_qty", 0.0) + payload.actual_qty
    expected_qty = task.get("expected_qty", 0.0)
    
    # Check if qty exceeds expected (should not happen, but validate)
    if new_received_qty > expected_qty:
        raise HTTPException(
            status_code=400,
            detail=f"Qty received ({new_received_qty}) melebihi expected ({expected_qty})"
        )
    
    # Log scan entry
    scan_entry = {
        "id": new_id("scan"),
        "scan_type": "receive",
        "actual_qty": payload.actual_qty,
        "batch": payload.batch,
        "lot": payload.lot,
        "roll_id": payload.roll_id,
        "bin_id": payload.bin_id,
        "actor": actor["name"],
        "timestamp": now_iso()
    }
    
    update_data = {
        "received_qty": new_received_qty,
        "batch": payload.batch or task.get("batch", ""),
        "lot": payload.lot or task.get("lot", ""),
        "roll_id": payload.roll_id or task.get("roll_id", ""),
        "bin_id": payload.bin_id or task.get("bin_id", ""),
        "updated_at": now_iso()
    }
    
    # If received qty matches expected, auto-advance to receiving status
    if task["status"] == "waiting_goods" and new_received_qty > 0:
        update_data["status"] = "receiving"
    
    # If fully received, mark as ready for QC
    if new_received_qty >= expected_qty:
        update_data["status"] = "qc_check"
        update_data["quantity"] = new_received_qty  # Set final quantity
    
    updated_task = await db.wms_tasks.find_one_and_update(
        {"id": task_id},
        {
            "$set": update_data,
            "$push": {"scan_log": scan_entry}
        },
        projection={"_id": 0},
        return_document=ReturnDocument.AFTER
    )
    
    await audit(actor["name"], "inbound_scan_receive", "wms_task", task_id, {
        "actual_qty": payload.actual_qty,
        "received_qty": new_received_qty,
        "expected_qty": expected_qty
    })
    
    return safe_doc(updated_task)


@router.post("/inbound/tasks/{task_id}/escalate")
async def escalate_inbound_task(
    task_id: str,
    request: Request,
    reason: str = "Qty tidak sesuai dengan PO"
) -> Dict[str, Any]:
    """
    Escalate inbound task to manager due to qty mismatch or other issues.
    
    Manager can then adjust expected_qty or investigate issue.
    """
    actor = await require_permission(request, "wms", "update")
    
    task = safe_doc(await db.wms_tasks.find_one({"id": task_id}, {"_id": 0}))
    if not task:
        raise HTTPException(status_code=404, detail="Inbound task tidak ditemukan")
    
    escalation = {
        "escalated_by": actor["name"],
        "escalated_at": now_iso(),
        "reason": reason,
        "status": "pending_review",
        "resolved_by": None,
        "resolved_at": None,
        "resolution_notes": ""
    }
    
    updated_task = await db.wms_tasks.find_one_and_update(
        {"id": task_id},
        {
            "$set": {
                "escalation": escalation,
                "status": "escalated",
                "updated_at": now_iso()
            }
        },
        projection={"_id": 0},
        return_document=ReturnDocument.AFTER
    )
    
    await audit(actor["name"], "inbound_escalated", "wms_task", task_id, {
        "reason": reason,
        "received_qty": task.get("received_qty", 0),
        "expected_qty": task.get("expected_qty", 0)
    })
    
    return safe_doc(updated_task)


@router.post("/inbound/tasks/{task_id}/resolve-escalation")
async def resolve_escalation(
    task_id: str,
    request: Request,
    adjusted_qty: float = None,
    resolution_notes: str = ""
) -> Dict[str, Any]:
    """
    Resolve escalated inbound task (manager only).
    
    Manager can adjust expected_qty to match actual received qty.
    """
    actor = await require_permission(request, "wms", "approve")  # Manager permission
    
    task = safe_doc(await db.wms_tasks.find_one({"id": task_id}, {"_id": 0}))
    if not task:
        raise HTTPException(status_code=404, detail="Inbound task tidak ditemukan")
    
    if not task.get("escalation"):
        raise HTTPException(status_code=400, detail="Task tidak dalam status escalation")
    
    escalation = task["escalation"]
    escalation["status"] = "resolved"
    escalation["resolved_by"] = actor["name"]
    escalation["resolved_at"] = now_iso()
    escalation["resolution_notes"] = resolution_notes
    
    update_data = {
        "escalation": escalation,
        "status": "qc_check",  # Move to QC after resolution
        "updated_at": now_iso()
    }
    
    # If manager adjusts qty, update expected and final quantity
    if adjusted_qty is not None:
        update_data["expected_qty"] = adjusted_qty
        update_data["quantity"] = task.get("received_qty", 0.0)
    
    updated_task = await db.wms_tasks.find_one_and_update(
        {"id": task_id},
        {"$set": update_data},
        projection={"_id": 0},
        return_document=ReturnDocument.AFTER
    )
    
    await audit(actor["name"], "inbound_escalation_resolved", "wms_task", task_id, {
        "adjusted_qty": adjusted_qty,
        "resolution_notes": resolution_notes
    })
    
    return safe_doc(updated_task)


@router.post("/inbound/tasks/{task_id}/complete")
async def complete_inbound_receiving(task_id: str, request: Request) -> Dict[str, Any]:
    """
    Complete inbound receiving and update inventory.
    
    This moves task from qc_check → put_away → completed.
    Inventory is updated ONLY when status becomes 'completed'.
    """
    actor = await require_permission(request, "wms", "update")
    
    task = safe_doc(await db.wms_tasks.find_one({"id": task_id}, {"_id": 0}))
    if not task:
        raise HTTPException(status_code=404, detail="Inbound task tidak ditemukan")
    
    if task["status"] not in ["qc_check", "put_away"]:
        raise HTTPException(
            status_code=400,
            detail=f"Task harus dalam status qc_check atau put_away (current: {task['status']})"
        )
    
    # Check if qty is finalized
    final_qty = task.get("quantity", 0.0)
    if final_qty <= 0:
        # Fallback: if quantity wasn't explicitly set, use received_qty
        final_qty = task.get("received_qty", 0.0)
    if final_qty <= 0:
        raise HTTPException(status_code=400, detail="Quantity harus lebih dari 0 untuk complete")
    
    # Advance directly to "completed" status (single-click finish)
    # Operator presses Complete → task moves all the way to completed and inventory updates.
    next_stage = "completed"
    
    # If reaching completed, update inventory
    if next_stage == "completed":
        # Sub-fase 1.6 — Roll-as-SSOT: barang masuk WAJIB menjadi `inventory_rolls`
        # (BUKAN $inc langsung ke balance) agar invarian `balance == Σ rolls` tetap
        # utuh; lalu rebuild_balance + auto-fulfill backorder yang menunggu.
        from services.roll_service import rebuild_balance
        from services.backorder_service import auto_fulfill_backorders

        # Owner entity diturunkan dari PO (default entitas utama)
        owner_entity_id = DEFAULT_ENTITY_ID
        if task.get("po_id"):
            po_doc = await db.purchase_orders.find_one({"id": task["po_id"]}, {"_id": 0})
            owner_entity_id = (po_doc or {}).get("entity_id") or DEFAULT_ENTITY_ID

        lot = task.get("lot") or f"LOT-{task.get('po_number', task_id)}"
        roll_seq = await db.inventory_rolls.count_documents({}) + 1
        roll_doc = {
            "id": new_id("roll"),
            "product_id": task["product_id"],
            "owner_entity_id": owner_entity_id,
            "ownership_type": "internal",
            "consignor_ref": None,
            "warehouse_id": task["warehouse_id"],
            "bin_id": task.get("bin_id") or None,
            "lot": lot,
            "batch": task.get("batch") or (lot.replace("LOT", "BATCH") if lot else ""),
            "roll_no": f"RL-{roll_seq:05d}",
            "length_initial": round(final_qty, 2),
            "length_remaining": round(final_qty, 2),
            "unit": task.get("unit", "meter"),
            "grade": "A",
            "status": "available",
            "tracking_mode": "barcode",
            "earmarked_for": None,
            "location_type": "warehouse_bin",
            "reserved_ref": None,
            "unit_cost": None,
            "acquired": {"via": "inbound", "ref_id": task.get("po_id") or task_id, "date": now_iso()},
            "rfid_tag_id": task.get("roll_id") or None,
            "is_remnant": False,
            "created_at": now_iso(), "updated_at": now_iso(),
            "created_by": actor.get("id") or "system", "created_by_name": actor["name"],
        }
        await db.inventory_rolls.insert_one(dict(roll_doc))

        # Log movement (owner-scoped, link roll)
        await db.inventory_movements.insert_one({
            "id": new_id("mov"),
            "product_id": task["product_id"],
            "warehouse_id": task["warehouse_id"],
            "owner_entity_id": owner_entity_id,
            "movement_type": "inbound_receiving",
            "quantity": round(final_qty, 2),
            "unit": task.get("unit", "meter"),
            "batch": task.get("batch", ""),
            "lot": lot,
            "roll_id": roll_doc["id"],
            "source_document": f"PO_{task.get('po_number', '')}",
            "timestamp": now_iso()
        })

        # Update PO item received_qty (akumulatif) + status
        if task.get("po_id"):
            await db.purchase_orders.update_one(
                {
                    "id": task["po_id"],
                    "items.product_id": task["product_id"]
                },
                {
                    "$inc": {"items.$.received_qty": final_qty},
                    "$set": {
                        "status": "receiving",  # Or "completed" if all items done
                        "updated_at": now_iso()
                    }
                }
            )

        # Rebuild proyeksi balance segmen (jaga invarian balance == Σ rolls)
        await rebuild_balance(task["product_id"], task["warehouse_id"], owner_entity_id)

        # AUTO-FULFILL backorder untuk produk + entitas ini (FIFO)
        await auto_fulfill_backorders(task["product_id"], owner_entity_id)
    
    updated_task = await db.wms_tasks.find_one_and_update(
        {"id": task_id},
        {"$set": {"status": next_stage, "updated_at": now_iso()}},
        projection={"_id": 0},
        return_document=ReturnDocument.AFTER
    )
    
    await audit(actor["name"], "inbound_completed", "wms_task", task_id, {
        "final_qty": final_qty,
        "status": next_stage
    })
    
    return safe_doc(updated_task)


@router.get("/inbound/po/{po_id}/receiving-goods-document")
async def generate_receiving_goods_document(po_id: str, request: Request):
    """
    Generate Receiving Goods document (like surat jalan) for completed PO.
    
    Shows all received items with batch/lot/qty details.
    """
    from datetime import datetime, timezone
    
    await require_permission(request, "wms", "view")
    
    po = safe_doc(await db.purchase_orders.find_one({"id": po_id}, {"_id": 0}))
    if not po:
        raise HTTPException(status_code=404, detail="Purchase Order tidak ditemukan")
    
    # Get all completed inbound tasks for this PO
    tasks = await db.wms_tasks.find({
        "po_id": po_id,
        "status": "completed"
    }, {"_id": 0}).to_list(100)
    
    if not tasks:
        raise HTTPException(status_code=400, detail="Belum ada inbound task yang completed untuk PO ini")
    
    # Build items table
    items_rows = ""
    for task in tasks:
        items_rows += f"""
        <tr>
            <td>{task.get('sku', '')}</td>
            <td>{task.get('product_name', '')}</td>
            <td>{task.get('quantity', 0.0)}</td>
            <td>{task.get('unit', '')}</td>
            <td>{task.get('batch', '-')}</td>
            <td>{task.get('lot', '-')}</td>
            <td>{task.get('bin_id', '-')}</td>
        </tr>
        """
    
    html = f"""
    <html>
    <head>
        <title>Surat Penerimaan Barang - {po['po_number']}</title>
        <style>
            @page {{size: A4 portrait; margin: 12mm}}
            body {{font-family: Arial, sans-serif; padding: 0; color: #111}}
            .header {{display: flex; justify-content: space-between; border-bottom: 2px solid #111; padding-bottom: 16px; margin-bottom: 20px}}
            h1 {{margin: 0; font-size: 24px}}
            h2 {{margin: 10px 0; font-size: 18px}}
            table {{width: 100%; border-collapse: collapse; margin-top: 18px}}
            td, th {{border: 1px solid #ddd; padding: 10px; text-align: left}}
            th {{background: #f5f5f5; font-weight: bold}}
            .info-section {{margin: 20px 0}}
            .signature {{display: flex; justify-content: space-between; margin-top: 60px}}
            .signature div {{text-align: center}}
            footer {{margin-top: 40px; border-top: 1px solid #ddd; padding-top: 12px; color: #555; font-size: 12px}}
        </style>
    </head>
    <body>
        <div class="header">
            <div>
                <h1>Kain Nusantara</h1>
                <p style="color: #555; margin: 5px 0">Enterprise Textile Warehouse</p>
            </div>
            <div style="text-align: right">
                <h2>SURAT PENERIMAAN BARANG</h2>
                <p style="margin: 5px 0"><strong>{po['po_number']}</strong></p>
                <p style="margin: 5px 0">{datetime.now(timezone.utc).strftime('%d %b %Y')}</p>
            </div>
        </div>
        
        <div class="info-section">
            <h3>Informasi PO</h3>
            <p><strong>Supplier:</strong> {po['supplier_name']}</p>
            <p><strong>Kontak:</strong> {po.get('supplier_contact', '-')}</p>
            <p><strong>Gudang Tujuan:</strong> {po.get('warehouse_name', '-')} ({po.get('warehouse_city', '')})</p>
            <p><strong>Tanggal Expected:</strong> {po.get('expected_delivery_date', '-')}</p>
        </div>
        
        <h3>Barang yang Diterima</h3>
        <table>
            <thead>
                <tr>
                    <th>SKU</th>
                    <th>Nama Produk</th>
                    <th>Qty Diterima</th>
                    <th>Unit</th>
                    <th>Batch</th>
                    <th>Lot</th>
                    <th>Bin Location</th>
                </tr>
            </thead>
            <tbody>
                {items_rows}
            </tbody>
        </table>
        
        <div class="signature">
            <div>
                <p>Diterima Oleh</p>
                <br/><br/>
                <p><strong>_________________</strong></p>
                <p>Warehouse Staff</p>
            </div>
            <div>
                <p>Disetujui Oleh</p>
                <br/><br/>
                <p><strong>_________________</strong></p>
                <p>Warehouse Manager</p>
            </div>
        </div>
        
        <footer>
            <p>Dokumen ini dibuat secara otomatis oleh sistem Kain Nusantara WMS.</p>
            <p>Barang diterima dalam kondisi baik dan sesuai dengan spesifikasi PO.</p>
        </footer>
    </body>
    </html>
    """
    
    from fastapi.responses import HTMLResponse
    return HTMLResponse(content=html)
