"""
Kain Nusantara — Realistic Seed Data Script
Populates database with realistic historical data including:
- Purchase orders with completed receiving history
- Sales orders in various stages
- Inbound & outbound tasks (completed + in-progress)
- Inventory movements

Dapat dipakai sebagai:
1) Standalone CLI:   `python seed_realistic.py`
2) Imported module:  `from seed_realistic import seed_all; await seed_all(db_instance)`
"""

import asyncio
import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent / "backend"
sys.path.insert(0, str(ROOT_DIR))

from dotenv import load_dotenv
load_dotenv(ROOT_DIR / ".env")

from motor.motor_asyncio import AsyncIOMotorClient
from core_utils import hash_password, new_id, now_iso
from permissions_config import DEFAULT_PERMISSIONS
from datetime import datetime, timedelta, timezone
import random

# `db` is a module-level placeholder; it will be set by `init_with_db()`
# or by `main()` when running as a standalone script. Seed functions reference
# `db` by name at call-time, so replacing this value works correctly.
db = None


def init_with_db(db_instance):
    """Inject an external Motor DB instance (for use from FastAPI endpoint)."""
    global db
    db = db_instance


def ago(days=0, hours=0, minutes=0) -> str:
    """Return ISO string for a datetime in the past."""
    dt = datetime.now(timezone.utc) - timedelta(days=days, hours=hours, minutes=minutes)
    return dt.isoformat()


async def clear_collections():
    """Drop operational data — keep nothing (fresh realistic seed)."""
    cols = [
        "users", "uoms", "warehouses", "products", "customers",
        "inventory_balances", "inventory_movements", "inventory_rolls", "sales_orders",
        "wms_tasks", "purchase_orders", "document_templates",
        "permission_settings", "audit_logs", "onboarding_checklists",
        "cycle_counts", "transfers", "escalations",
        "business_entities", "notifications",
        "system_settings", "payment_terms", "approval_rules",
        "price_approvals",
    ]
    for col in cols:
        await db[col].delete_many({})
    print("✅ Cleared all collections")


async def seed_users():
    await db.users.insert_many([
        {
            "id": "user_admin_01", "name": "Budi Santoso", "email": "admin@kainnusantara.id",
            "role": "admin", "password_hash": hash_password("demo12345"), "status": "active",
            "created_at": ago(days=180)
        },
        {
            "id": "user_sales_01", "name": "Ayu Permatasari", "email": "sales@kainnusantara.id",
            "role": "sales", "password_hash": hash_password("demo12345"), "status": "active",
            "created_at": ago(days=180)
        },
        {
            "id": "user_manager_01", "name": "Dewi Rahayu", "email": "manager@kainnusantara.id",
            "role": "manager", "password_hash": hash_password("demo12345"), "status": "active",
            "created_at": ago(days=180)
        },
        {
            "id": "user_wh_01", "name": "Eko Prasetyo", "email": "warehouse@kainnusantara.id",
            "role": "warehouse", "password_hash": hash_password("demo12345"), "status": "active",
            "created_at": ago(days=180)
        },
        {
            "id": "user_wh_02", "name": "Fitri Handayani", "email": "warehouse2@kainnusantara.id",
            "role": "warehouse", "password_hash": hash_password("demo12345"), "status": "active",
            "created_at": ago(days=90)
        },
    ])
    print("✅ Users seeded")


async def seed_uoms():
    await db.uoms.insert_many([
        {"id": "uom_meter", "code": "MTR", "name": "Meter", "base_type": "length", "precision": 2, "status": "active", "created_at": ago(days=180)},
        {"id": "uom_yard", "code": "YRD", "name": "Yard", "base_type": "length", "precision": 2, "status": "active", "created_at": ago(days=180)},
        {"id": "uom_roll", "code": "RLL", "name": "Roll", "base_type": "volume", "precision": 0, "status": "active", "created_at": ago(days=180)},
        {"id": "uom_pcs", "code": "PCS", "name": "Pcs", "base_type": "count", "precision": 0, "status": "active", "created_at": ago(days=180)},
    ])
    print("✅ UOMs seeded")


async def seed_warehouses():
    await db.warehouses.insert_many([
        {
            "id": "wh_jakarta", "code": "WH-JKT", "name": "Gudang Jakarta Utara", "city": "Jakarta",
            "lat": -6.1751, "lng": 106.8650, "active": True, "created_at": ago(days=180),
            "zones": [{"id": "zone_jkt_a", "name": "Zone A", "racks": [
                {"id": "rack_jkt_a1", "name": "Rack A1", "bins": [
                    {"id": "bin_jkt_a1_01", "code": "A1-01", "capacity": 500},
                    {"id": "bin_jkt_a1_02", "code": "A1-02", "capacity": 500},
                    {"id": "bin_jkt_a1_03", "code": "A1-03", "capacity": 500},
                ]},
                {"id": "rack_jkt_a2", "name": "Rack A2", "bins": [
                    {"id": "bin_jkt_a2_01", "code": "A2-01", "capacity": 400},
                    {"id": "bin_jkt_a2_02", "code": "A2-02", "capacity": 400},
                ]},
            ]},
            {"id": "zone_jkt_b", "name": "Zone B", "racks": [
                {"id": "rack_jkt_b1", "name": "Rack B1", "bins": [
                    {"id": "bin_jkt_b1_01", "code": "B1-01", "capacity": 600},
                    {"id": "bin_jkt_b1_02", "code": "B1-02", "capacity": 600},
                ]}
            ]}]
        },
        {
            "id": "wh_bandung", "code": "WH-BDG", "name": "Gudang Bandung Kopo", "city": "Bandung",
            "lat": -6.9175, "lng": 107.6191, "active": True, "created_at": ago(days=180),
            "zones": [{"id": "zone_bdg_a", "name": "Zone A", "racks": [
                {"id": "rack_bdg_a1", "name": "Rack A1", "bins": [
                    {"id": "bin_bdg_a1_01", "code": "A1-01", "capacity": 600},
                    {"id": "bin_bdg_a1_02", "code": "A1-02", "capacity": 600},
                ]}
            ]}]
        },
        {
            "id": "wh_surabaya", "code": "WH-SBY", "name": "Gudang Surabaya Rungkut", "city": "Surabaya",
            "lat": -7.2504, "lng": 112.7688, "active": True, "created_at": ago(days=180),
            "zones": [{"id": "zone_sby_a", "name": "Zone A", "racks": [
                {"id": "rack_sby_a1", "name": "Rack A1", "bins": [
                    {"id": "bin_sby_a1_01", "code": "A1-01", "capacity": 400},
                    {"id": "bin_sby_a1_02", "code": "A1-02", "capacity": 400},
                ]}
            ]}]
        },
    ])
    print("✅ Warehouses seeded")


async def seed_products():
    products = [
        {
            "id": "prod_batik_mega", "sku": "BTK-MEGA-001",
            "name": "Batik Mega Mendung Premium", "category": "Batik", "variant": "Premium",
            "color": "Biru-Coklat", "motif": "Mega Mendung", "grade": "A",
            "supplier": "Cirebon Craft", "base_unit": "meter", "price": 185000,
            "image": "https://images.unsplash.com/photo-1761516659766-c092d4b1209d?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2MzR8MHwxfHNlYXJjaHw0fHxiYXRpayUyMGluZG9uZXNpYSUyMGZhYnJpYyUyMHRyYWRpdGlvbmFsJTIwdGV4dGlsZSUyMHBhdHRlcm58ZW58MHx8fHwxNzc4NjkyMDU3fDA&ixlib=rb-4.1.0&q=85",
            "status": "active", "uom_conversions": [], "batch_lot_rolls": [],
            "created_at": ago(days=180), "updated_at": ago(days=2)
        },
        {
            "id": "prod_tenun_ikat", "sku": "TNI-GRGD-001",
            "name": "Tenun Ikat Garuda Premium", "category": "Tenun", "variant": "Premium",
            "color": "Merah-Emas", "motif": "Garuda", "grade": "A",
            "supplier": "NTT Weaving Co", "base_unit": "meter", "price": 225000,
            "image": "https://images.unsplash.com/photo-1748141951488-9c9fb9603daf?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzV8MHwxfHNlYXJjaHwyfHx0ZW51biUyMGlrYXQlMjBpbmRvbmVzaWFuJTIwd292ZW4lMjB0ZXh0aWxlJTIwdHJhZGl0aW9uYWwlMjBmYWJyaWN8ZW58MHx8fHwxNzc4NjkyMDY1fDA&ixlib=rb-4.1.0&q=85",
            "status": "active", "uom_conversions": [], "batch_lot_rolls": [],
            "created_at": ago(days=175), "updated_at": ago(days=5)
        },
        {
            "id": "prod_lurik_classic", "sku": "LRK-CLSC-001",
            "name": "Lurik Klasik Solo", "category": "Lurik", "variant": "Klasik",
            "color": "Coklat-Putih", "motif": "Garis Vertikal", "grade": "A",
            "supplier": "Solo Weave", "base_unit": "meter", "price": 95000,
            "image": "https://images.unsplash.com/photo-1761516659491-bf9a672d64c1?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2MzR8MHwxfHNlYXJjaHwzfHxiYXRpayUyMGluZG9uZXNpYSUyMGZhYnJpYyUyMHRyYWRpdGlvbmFsJTIwdGV4dGlsZSUyMHBhdHRlcm58ZW58MHx8fHwxNzc4NjkyMDU3fDA&ixlib=rb-4.1.0&q=85",
            "status": "active", "uom_conversions": [], "batch_lot_rolls": [],
            "created_at": ago(days=170), "updated_at": ago(days=1)
        },
        {
            "id": "prod_songket_palembang", "sku": "SGK-PLB-001",
            "name": "Songket Palembang Benang Emas", "category": "Songket", "variant": "Premium",
            "color": "Emas-Hitam", "motif": "Bunga Cengkeh", "grade": "A+",
            "supplier": "Palembang Silk House", "base_unit": "meter", "price": 450000,
            "image": "https://images.unsplash.com/photo-1594100618558-978ea7266c0a?crop=entropy&cs=srgb&fm=jpg&ixid=M3w4NjA1NDh8MHwxfHNlYXJjaHwzfHxzb25na2V0JTIwZmFicmljJTIwZ29sZCUyMHRocmVhZCUyMGluZG9uZXNpYW4lMjBzaWxrJTIwdGV4dGlsZXxlbnwwfHx8fDE3Nzg2OTIwNjV8MA&ixlib=rb-4.1.0&q=85",
            "status": "active", "uom_conversions": [], "batch_lot_rolls": [],
            "created_at": ago(days=160), "updated_at": ago(days=3)
        },
        {
            "id": "prod_ulos_batak", "sku": "ULS-BTK-001",
            "name": "Ulos Batak Ragidup", "category": "Ulos", "variant": "Tradisional",
            "color": "Biru-Oranye", "motif": "Ragidup", "grade": "A",
            "supplier": "Toba Craft", "base_unit": "meter", "price": 320000,
            "image": "https://images.unsplash.com/photo-1749367288395-f874bb54bc8a?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzV8MHwxfHNlYXJjaHw0fHx0ZW51biUyMGlrYXQlMjBpbmRvbmVzaWFuJTIwd292ZW4lMjB0ZXh0aWxlJTIwdHJhZGl0aW9uYWwlMjBmYWJyaWN8ZW58MHx8fHwxNzc4NjkyMDY1fDA&ixlib=rb-4.1.0&q=85",
            "status": "active", "uom_conversions": [], "batch_lot_rolls": [],
            "created_at": ago(days=155), "updated_at": ago(days=7)
        },
        {
            "id": "prod_jumputan_palembang", "sku": "JMP-PLB-001",
            "name": "Jumputan Palembang Pelangi", "category": "Jumputan", "variant": "Standard",
            "color": "Multicolor", "motif": "Pelangi Jumputan", "grade": "B",
            "supplier": "Palembang Silk House", "base_unit": "meter", "price": 145000,
            "image": "https://images.unsplash.com/photo-1761515315375-1315503bb3ce?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2MzR8MHwxfHNlYXJjaHwyfHxiYXRpayUyMGluZG9uZXNpYSUyMGZhYnJpYyUyMHRyYWRpdGlvbmFsJTIwdGV4dGlsZSUyMHBhdHRlcm58ZW58MHx8fHwxNzc4NjkyMDU3fDA&ixlib=rb-4.1.0&q=85",
            "status": "active", "uom_conversions": [], "batch_lot_rolls": [],
            "created_at": ago(days=120), "updated_at": ago(days=10)
        },
        {
            "id": "prod_endek_bali", "sku": "ENK-BALI-001",
            "name": "Endek Bali Rangrang", "category": "Endek", "variant": "Premium",
            "color": "Merah-Coklat", "motif": "Rangrang", "grade": "A",
            "supplier": "Bali Weave Studio", "base_unit": "meter", "price": 280000,
            "image": "https://images.unsplash.com/photo-1749367288413-994ae375d2f6?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzV8MHwxfHNlYXJjaHwzfHx0ZW51biUyMGlrYXQlMjBpbmRvbmVzaWFuJTIwd292ZW4lMjB0ZXh0aWxlJTIwdHJhZGl0aW9uYWwlMjBmYWJyaWN8ZW58MHx8fHwxNzc4NjkyMDY1fDA&ixlib=rb-4.1.0&q=85",
            "status": "active", "uom_conversions": [], "batch_lot_rolls": [],
            "created_at": ago(days=100), "updated_at": ago(days=4)
        },
    ]
    await db.products.insert_many(products)
    print("✅ Products seeded (7 products)")


async def seed_customers():
    await db.customers.insert_many([
        {
            "id": "cust_toko_kain", "code": "CUST-0001", "name": "Toko Kain Sejahtera",
            "pic_name": "Pak Hendra", "phone": "081234567890", "email": "hendra@tokokain.id",
            "type": "Retailer", "city": "Jakarta", "status": "active",
            "created_by": "user_admin_01", "created_at": ago(days=170),
            "addresses": [{"id": "addr_001", "label": "Toko Utama", "recipient_name": "Pak Hendra",
                           "phone": "081234567890", "city": "Jakarta",
                           "address": "Jl. Mangga Besar Raya No. 45", "is_primary": True}]
        },
        {
            "id": "cust_butik_bali", "code": "CUST-0002", "name": "Butik Bali Indah",
            "pic_name": "Ibu Komang", "phone": "082345678901", "email": "komang@butikbali.id",
            "type": "Boutique", "city": "Denpasar", "status": "active",
            "created_by": "user_admin_01", "created_at": ago(days=165),
            "addresses": [{"id": "addr_002", "label": "Butik Seminyak", "recipient_name": "Ibu Komang",
                           "phone": "082345678901", "city": "Denpasar",
                           "address": "Jl. Seminyak No. 88", "is_primary": True}]
        },
        {
            "id": "cust_moda_surabaya", "code": "CUST-0003", "name": "Moda Surabaya Fashion",
            "pic_name": "Bapak Andi", "phone": "083456789012", "email": "andi@modasby.id",
            "type": "Wholesaler", "city": "Surabaya", "status": "active",
            "created_by": "user_admin_01", "created_at": ago(days=160),
            "addresses": [{"id": "addr_003", "label": "Gudang Pusat", "recipient_name": "Bapak Andi",
                           "phone": "083456789012", "city": "Surabaya",
                           "address": "Jl. Rungkut Industri No. 22", "is_primary": True}]
        },
        {
            "id": "cust_fashion_bandung", "code": "CUST-0004", "name": "Fashion Bandung Kencana",
            "pic_name": "Ibu Sari", "phone": "085678901234", "email": "sari@fashionbdg.id",
            "type": "Boutique", "city": "Bandung", "status": "active",
            "created_by": "user_admin_01", "created_at": ago(days=120),
            "addresses": [{"id": "addr_004", "label": "Toko Dago", "recipient_name": "Ibu Sari",
                           "phone": "085678901234", "city": "Bandung",
                           "address": "Jl. Dago No. 112, Bandung", "is_primary": True}]
        },
        {
            "id": "cust_textile_medan", "code": "CUST-0005", "name": "Tekstil Medan Jaya",
            "pic_name": "Pak Robert", "phone": "081345678905", "email": "robert@tekstilmedan.id",
            "type": "Wholesaler", "city": "Medan", "status": "active",
            "created_by": "user_admin_01", "created_at": ago(days=90),
            "addresses": [{"id": "addr_005", "label": "Gudang Utama", "recipient_name": "Pak Robert",
                           "phone": "081345678905", "city": "Medan",
                           "address": "Jl. Asia No. 78, Medan", "is_primary": True}]
        },
    ])
    print("✅ Customers seeded (5 customers)")


async def seed_inventory_initial():
    """Seed initial inventory balances before receiving history."""
    balances = [
        # Jakarta
        {"id": new_id("bal"), "product_id": "prod_batik_mega", "warehouse_id": "wh_jakarta",
         "on_hand_qty": 485, "reserved_qty": 50, "available_qty": 435, "blocked_qty": 0,
         "picked_qty": 0, "in_transit_qty": 0, "updated_at": ago(hours=2)},
        {"id": new_id("bal"), "product_id": "prod_tenun_ikat", "warehouse_id": "wh_jakarta",
         "on_hand_qty": 320, "reserved_qty": 30, "available_qty": 290, "blocked_qty": 0,
         "picked_qty": 0, "in_transit_qty": 0, "updated_at": ago(hours=3)},
        {"id": new_id("bal"), "product_id": "prod_songket_palembang", "warehouse_id": "wh_jakarta",
         "on_hand_qty": 155, "reserved_qty": 20, "available_qty": 135, "blocked_qty": 0,
         "picked_qty": 0, "in_transit_qty": 0, "updated_at": ago(hours=1)},
        {"id": new_id("bal"), "product_id": "prod_ulos_batak", "warehouse_id": "wh_jakarta",
         "on_hand_qty": 95, "reserved_qty": 0, "available_qty": 95, "blocked_qty": 0,
         "picked_qty": 0, "in_transit_qty": 0, "updated_at": ago(days=1)},
        {"id": new_id("bal"), "product_id": "prod_endek_bali", "warehouse_id": "wh_jakarta",
         "on_hand_qty": 180, "reserved_qty": 0, "available_qty": 180, "blocked_qty": 0,
         "picked_qty": 0, "in_transit_qty": 0, "updated_at": ago(days=2)},
        # Bandung
        {"id": new_id("bal"), "product_id": "prod_batik_mega", "warehouse_id": "wh_bandung",
         "on_hand_qty": 340, "reserved_qty": 20, "available_qty": 320, "blocked_qty": 0,
         "picked_qty": 0, "in_transit_qty": 0, "updated_at": ago(hours=5)},
        {"id": new_id("bal"), "product_id": "prod_lurik_classic", "warehouse_id": "wh_bandung",
         "on_hand_qty": 620, "reserved_qty": 40, "available_qty": 580, "blocked_qty": 0,
         "picked_qty": 0, "in_transit_qty": 0, "updated_at": ago(hours=6)},
        {"id": new_id("bal"), "product_id": "prod_jumputan_palembang", "warehouse_id": "wh_bandung",
         "on_hand_qty": 210, "reserved_qty": 0, "available_qty": 210, "blocked_qty": 0,
         "picked_qty": 0, "in_transit_qty": 0, "updated_at": ago(days=3)},
        # Surabaya
        {"id": new_id("bal"), "product_id": "prod_tenun_ikat", "warehouse_id": "wh_surabaya",
         "on_hand_qty": 245, "reserved_qty": 35, "available_qty": 210, "blocked_qty": 0,
         "picked_qty": 0, "in_transit_qty": 0, "updated_at": ago(hours=4)},
        {"id": new_id("bal"), "product_id": "prod_lurik_classic", "warehouse_id": "wh_surabaya",
         "on_hand_qty": 410, "reserved_qty": 25, "available_qty": 385, "blocked_qty": 0,
         "picked_qty": 0, "in_transit_qty": 0, "updated_at": ago(hours=8)},
        {"id": new_id("bal"), "product_id": "prod_ulos_batak", "warehouse_id": "wh_surabaya",
         "on_hand_qty": 140, "reserved_qty": 0, "available_qty": 140, "blocked_qty": 0,
         "picked_qty": 0, "in_transit_qty": 0, "updated_at": ago(days=2)},
        {"id": new_id("bal"), "product_id": "prod_endek_bali", "warehouse_id": "wh_surabaya",
         "on_hand_qty": 75, "reserved_qty": 0, "available_qty": 75, "blocked_qty": 0,
         "picked_qty": 0, "in_transit_qty": 0, "updated_at": ago(days=4)},
    ]
    await db.inventory_balances.insert_many(balances)
    print(f"✅ Inventory balances seeded ({len(balances)} records)")


async def seed_inventory_movements_initial():
    """Initial stock movements."""
    movements = [
        # Jakarta initial stocks (3 months ago)
        {"id": new_id("mov"), "product_id": "prod_batik_mega", "warehouse_id": "wh_jakarta",
         "movement_type": "initial_stock", "quantity": 300, "unit": "meter",
         "batch": "BTK-2025-001", "lot": "LOT-001", "roll_id": "ROLL-001",
         "source_document": "INIT-001", "notes": "Initial stock", "created_by": "user_admin_01",
         "timestamp": ago(days=180)},
        {"id": new_id("mov"), "product_id": "prod_tenun_ikat", "warehouse_id": "wh_jakarta",
         "movement_type": "initial_stock", "quantity": 200, "unit": "meter",
         "batch": "TNI-2025-001", "lot": "LOT-001", "roll_id": "ROLL-002",
         "source_document": "INIT-001", "notes": "Initial stock", "created_by": "user_admin_01",
         "timestamp": ago(days=180)},
        {"id": new_id("mov"), "product_id": "prod_songket_palembang", "warehouse_id": "wh_jakarta",
         "movement_type": "initial_stock", "quantity": 80, "unit": "meter",
         "batch": "SGK-2025-001", "lot": "LOT-001", "roll_id": "ROLL-003",
         "source_document": "INIT-001", "notes": "Initial stock", "created_by": "user_admin_01",
         "timestamp": ago(days=180)},
        # Bandung initial stocks
        {"id": new_id("mov"), "product_id": "prod_batik_mega", "warehouse_id": "wh_bandung",
         "movement_type": "initial_stock", "quantity": 250, "unit": "meter",
         "batch": "BTK-2025-001", "lot": "LOT-002", "roll_id": "ROLL-010",
         "source_document": "INIT-001", "notes": "Initial stock", "created_by": "user_admin_01",
         "timestamp": ago(days=180)},
        {"id": new_id("mov"), "product_id": "prod_lurik_classic", "warehouse_id": "wh_bandung",
         "movement_type": "initial_stock", "quantity": 400, "unit": "meter",
         "batch": "LRK-2025-001", "lot": "LOT-001", "roll_id": "ROLL-011",
         "source_document": "INIT-001", "notes": "Initial stock", "created_by": "user_admin_01",
         "timestamp": ago(days=180)},
        # Surabaya initial stocks
        {"id": new_id("mov"), "product_id": "prod_tenun_ikat", "warehouse_id": "wh_surabaya",
         "movement_type": "initial_stock", "quantity": 150, "unit": "meter",
         "batch": "TNI-2025-001", "lot": "LOT-002", "roll_id": "ROLL-020",
         "source_document": "INIT-001", "notes": "Initial stock", "created_by": "user_admin_01",
         "timestamp": ago(days=180)},
        {"id": new_id("mov"), "product_id": "prod_lurik_classic", "warehouse_id": "wh_surabaya",
         "movement_type": "initial_stock", "quantity": 300, "unit": "meter",
         "batch": "LRK-2025-001", "lot": "LOT-002", "roll_id": "ROLL-021",
         "source_document": "INIT-001", "notes": "Initial stock", "created_by": "user_admin_01",
         "timestamp": ago(days=180)},
    ]
    await db.inventory_movements.insert_many(movements)
    print(f"✅ Initial inventory movements seeded ({len(movements)})")


async def seed_purchase_orders():
    """Seed realistic POs with completed inbound receiving history."""

    # PO-00001 — Completed 45 days ago (Batik Mega Mendung from Cirebon Craft → Jakarta)
    po1_id = "po_001"
    task1a_id = new_id("wms")
    task1b_id = new_id("wms")
    await db.purchase_orders.insert_one({
        "id": po1_id, "po_number": "PO-00001",
        "supplier_name": "Cirebon Craft", "supplier_contact": "Pak Wahyu | 081234500001",
        "warehouse_id": "wh_jakarta",
        "status": "completed",
        "items": [
            {"product_id": "prod_batik_mega", "sku": "BTK-MEGA-001",
             "product_name": "Batik Mega Mendung Premium",
             "quantity": 150.0, "received_qty": 150.0, "unit": "meter", "price": 165000,
             "status": "completed", "inbound_task_id": task1a_id},
            {"product_id": "prod_songket_palembang", "sku": "SGK-PLB-001",
             "product_name": "Songket Palembang Benang Emas",
             "quantity": 60.0, "received_qty": 60.0, "unit": "meter", "price": 420000,
             "status": "completed", "inbound_task_id": task1b_id},
        ],
        "expected_delivery_date": ago(days=46),
        "notes": "Pengiriman pertama batch 2025 Q1",
        "created_by": "Budi Santoso", "created_at": ago(days=50),
        "completed_at": ago(days=44),
    })
    # WMS tasks for PO-00001
    await db.wms_tasks.insert_many([
        {
            "id": task1a_id, "flow_type": "inbound", "source_type": "purchase_order", "task_subtype": "receiving",
            "po_id": po1_id, "po_number": "PO-00001",
            "product_id": "prod_batik_mega", "sku": "BTK-MEGA-001",
            "product_name": "Batik Mega Mendung Premium",
            "warehouse_id": "wh_jakarta", "warehouse_name": "Gudang Jakarta Utara",
            "expected_qty": 150.0, "received_qty": 150.0, "quantity": 150.0,
            "unit": "meter", "status": "completed",
            "supplier_name": "Cirebon Craft",
            "bin_id": "A1-01", "batch": "BTK-2025-003", "lot": "LOT-003",
            "scan_log": [
                {"scan_time": ago(days=45, hours=2), "scanned_by": "Eko Prasetyo",
                 "actual_qty": 75.0, "batch": "BTK-2025-003", "lot": "LOT-003",
                 "roll_id": "ROLL-031", "bin_id": "A1-01"},
                {"scan_time": ago(days=45, hours=1), "scanned_by": "Eko Prasetyo",
                 "actual_qty": 75.0, "batch": "BTK-2025-003", "lot": "LOT-003",
                 "roll_id": "ROLL-032", "bin_id": "A1-01"},
            ],
            "escalation": None,
            "created_at": ago(days=50), "updated_at": ago(days=44),
            "completed_at": ago(days=44),
        },
        {
            "id": task1b_id, "flow_type": "inbound", "source_type": "purchase_order", "task_subtype": "receiving",
            "po_id": po1_id, "po_number": "PO-00001",
            "product_id": "prod_songket_palembang", "sku": "SGK-PLB-001",
            "product_name": "Songket Palembang Benang Emas",
            "warehouse_id": "wh_jakarta", "warehouse_name": "Gudang Jakarta Utara",
            "expected_qty": 60.0, "received_qty": 60.0, "quantity": 60.0,
            "unit": "meter", "status": "completed",
            "supplier_name": "Cirebon Craft",
            "bin_id": "A2-01", "batch": "SGK-2025-002", "lot": "LOT-002",
            "scan_log": [
                {"scan_time": ago(days=45, hours=1, minutes=30), "scanned_by": "Eko Prasetyo",
                 "actual_qty": 60.0, "batch": "SGK-2025-002", "lot": "LOT-002",
                 "roll_id": "ROLL-033", "bin_id": "A2-01"},
            ],
            "escalation": None,
            "created_at": ago(days=50), "updated_at": ago(days=44),
            "completed_at": ago(days=44),
        },
    ])
    # Inventory movements from PO-00001 receiving
    await db.inventory_movements.insert_many([
        {"id": new_id("mov"), "product_id": "prod_batik_mega", "warehouse_id": "wh_jakarta",
         "movement_type": "inbound_receiving", "quantity": 150.0, "unit": "meter",
         "batch": "BTK-2025-003", "lot": "LOT-003", "roll_id": "ROLL-031/032",
         "source_document": "PO-00001", "notes": "Receiving completed by Eko Prasetyo",
         "created_by": "user_wh_01", "timestamp": ago(days=44)},
        {"id": new_id("mov"), "product_id": "prod_songket_palembang", "warehouse_id": "wh_jakarta",
         "movement_type": "inbound_receiving", "quantity": 60.0, "unit": "meter",
         "batch": "SGK-2025-002", "lot": "LOT-002", "roll_id": "ROLL-033",
         "source_document": "PO-00001", "notes": "Receiving completed by Eko Prasetyo",
         "created_by": "user_wh_01", "timestamp": ago(days=44)},
    ])

    # PO-00002 — Completed 30 days ago (Tenun Ikat & Lurik from NTT/Solo → Bandung + Surabaya)
    po2_id = "po_002"
    task2a_id = new_id("wms")
    task2b_id = new_id("wms")
    await db.purchase_orders.insert_one({
        "id": po2_id, "po_number": "PO-00002",
        "supplier_name": "NTT Weaving Co", "supplier_contact": "Ibu Agnes | 082345600002",
        "warehouse_id": "wh_surabaya",
        "status": "completed",
        "items": [
            {"product_id": "prod_tenun_ikat", "sku": "TNI-GRGD-001",
             "product_name": "Tenun Ikat Garuda Premium",
             "quantity": 100.0, "received_qty": 100.0, "unit": "meter", "price": 200000,
             "status": "completed", "inbound_task_id": task2a_id},
            {"product_id": "prod_ulos_batak", "sku": "ULS-BTK-001",
             "product_name": "Ulos Batak Ragidup",
             "quantity": 80.0, "received_qty": 80.0, "unit": "meter", "price": 295000,
             "status": "completed", "inbound_task_id": task2b_id},
        ],
        "expected_delivery_date": ago(days=31),
        "notes": "Pengiriman batch 2025 Q1 - NTT Collection",
        "created_by": "Budi Santoso", "created_at": ago(days=35),
        "completed_at": ago(days=29),
    })
    await db.wms_tasks.insert_many([
        {
            "id": task2a_id, "flow_type": "inbound", "source_type": "purchase_order", "task_subtype": "receiving",
            "po_id": po2_id, "po_number": "PO-00002",
            "product_id": "prod_tenun_ikat", "sku": "TNI-GRGD-001",
            "product_name": "Tenun Ikat Garuda Premium",
            "warehouse_id": "wh_surabaya", "warehouse_name": "Gudang Surabaya Rungkut",
            "expected_qty": 100.0, "received_qty": 100.0, "quantity": 100.0,
            "unit": "meter", "status": "completed",
            "supplier_name": "NTT Weaving Co",
            "bin_id": "A1-01", "batch": "TNI-2025-002", "lot": "LOT-002",
            "scan_log": [
                {"scan_time": ago(days=30, hours=3), "scanned_by": "Eko Prasetyo",
                 "actual_qty": 50.0, "batch": "TNI-2025-002", "lot": "LOT-002",
                 "roll_id": "ROLL-041", "bin_id": "A1-01"},
                {"scan_time": ago(days=30, hours=2), "scanned_by": "Eko Prasetyo",
                 "actual_qty": 50.0, "batch": "TNI-2025-002", "lot": "LOT-002",
                 "roll_id": "ROLL-042", "bin_id": "A1-01"},
            ],
            "escalation": None,
            "created_at": ago(days=35), "updated_at": ago(days=29),
            "completed_at": ago(days=29),
        },
        {
            "id": task2b_id, "flow_type": "inbound", "source_type": "purchase_order", "task_subtype": "receiving",
            "po_id": po2_id, "po_number": "PO-00002",
            "product_id": "prod_ulos_batak", "sku": "ULS-BTK-001",
            "product_name": "Ulos Batak Ragidup",
            "warehouse_id": "wh_surabaya", "warehouse_name": "Gudang Surabaya Rungkut",
            "expected_qty": 80.0, "received_qty": 80.0, "quantity": 80.0,
            "unit": "meter", "status": "completed",
            "supplier_name": "NTT Weaving Co",
            "bin_id": "A1-02", "batch": "ULS-2025-001", "lot": "LOT-001",
            "scan_log": [
                {"scan_time": ago(days=30, hours=1, minutes=30), "scanned_by": "Fitri Handayani",
                 "actual_qty": 80.0, "batch": "ULS-2025-001", "lot": "LOT-001",
                 "roll_id": "ROLL-043", "bin_id": "A1-02"},
            ],
            "escalation": None,
            "created_at": ago(days=35), "updated_at": ago(days=29),
            "completed_at": ago(days=29),
        },
    ])
    await db.inventory_movements.insert_many([
        {"id": new_id("mov"), "product_id": "prod_tenun_ikat", "warehouse_id": "wh_surabaya",
         "movement_type": "inbound_receiving", "quantity": 100.0, "unit": "meter",
         "batch": "TNI-2025-002", "lot": "LOT-002", "roll_id": "ROLL-041/042",
         "source_document": "PO-00002", "notes": "Receiving completed by Eko Prasetyo",
         "created_by": "user_wh_01", "timestamp": ago(days=29)},
        {"id": new_id("mov"), "product_id": "prod_ulos_batak", "warehouse_id": "wh_surabaya",
         "movement_type": "inbound_receiving", "quantity": 80.0, "unit": "meter",
         "batch": "ULS-2025-001", "lot": "LOT-001", "roll_id": "ROLL-043",
         "source_document": "PO-00002", "notes": "Receiving completed by Fitri Handayani",
         "created_by": "user_wh_02", "timestamp": ago(days=29)},
    ])

    # PO-00003 — Completed 15 days ago (Lurik & Endek → Bandung, with escalation history)
    po3_id = "po_003"
    task3a_id = new_id("wms")
    task3b_id = new_id("wms")
    await db.purchase_orders.insert_one({
        "id": po3_id, "po_number": "PO-00003",
        "supplier_name": "Solo Weave", "supplier_contact": "Pak Joko | 085012300003",
        "warehouse_id": "wh_bandung",
        "status": "completed",
        "items": [
            {"product_id": "prod_lurik_classic", "sku": "LRK-CLSC-001",
             "product_name": "Lurik Klasik Solo",
             "quantity": 200.0, "received_qty": 180.0, "unit": "meter", "price": 88000,
             "status": "completed", "inbound_task_id": task3a_id,
             "escalation_note": "Supplier kirim 180m, bukan 200m. Manager adjust qty."},
            {"product_id": "prod_endek_bali", "sku": "ENK-BALI-001",
             "product_name": "Endek Bali Rangrang",
             "quantity": 100.0, "received_qty": 100.0, "unit": "meter", "price": 255000,
             "status": "completed", "inbound_task_id": task3b_id},
        ],
        "expected_delivery_date": ago(days=16),
        "notes": "Batch 2025 Q1 - Lurik & Endek Bali",
        "created_by": "Budi Santoso", "created_at": ago(days=20),
        "completed_at": ago(days=14),
    })
    await db.wms_tasks.insert_many([
        {
            "id": task3a_id, "flow_type": "inbound", "source_type": "purchase_order", "task_subtype": "receiving",
            "po_id": po3_id, "po_number": "PO-00003",
            "product_id": "prod_lurik_classic", "sku": "LRK-CLSC-001",
            "product_name": "Lurik Klasik Solo",
            "warehouse_id": "wh_bandung", "warehouse_name": "Gudang Bandung Kopo",
            "expected_qty": 180.0, "received_qty": 180.0, "quantity": 180.0,
            "unit": "meter", "status": "completed",
            "supplier_name": "Solo Weave",
            "bin_id": "A1-01", "batch": "LRK-2025-002", "lot": "LOT-002",
            "scan_log": [
                {"scan_time": ago(days=15, hours=4), "scanned_by": "Fitri Handayani",
                 "actual_qty": 90.0, "batch": "LRK-2025-002", "lot": "LOT-002",
                 "roll_id": "ROLL-051", "bin_id": "A1-01"},
                {"scan_time": ago(days=15, hours=3, minutes=30), "scanned_by": "Fitri Handayani",
                 "actual_qty": 90.0, "batch": "LRK-2025-002", "lot": "LOT-002",
                 "roll_id": "ROLL-052", "bin_id": "A1-01"},
            ],
            "escalation": {
                "escalated_at": ago(days=15, hours=5),
                "escalated_by": "Fitri Handayani",
                "reason": "Supplier hanya mengirim 180m dari 200m yang dipesan. Fisik sudah dihitung ulang.",
                "status": "resolved",
                "resolved_at": ago(days=15, hours=2),
                "resolved_by": "Dewi Rahayu",
                "resolution_notes": "Dikonfirmasi supplier kekurangan material. Adjust expected qty ke 180m dan proceed complete.",
                "adjusted_qty": 180.0,
            },
            "created_at": ago(days=20), "updated_at": ago(days=14),
            "completed_at": ago(days=14),
        },
        {
            "id": task3b_id, "flow_type": "inbound", "source_type": "purchase_order", "task_subtype": "receiving",
            "po_id": po3_id, "po_number": "PO-00003",
            "product_id": "prod_endek_bali", "sku": "ENK-BALI-001",
            "product_name": "Endek Bali Rangrang",
            "warehouse_id": "wh_bandung", "warehouse_name": "Gudang Bandung Kopo",
            "expected_qty": 100.0, "received_qty": 100.0, "quantity": 100.0,
            "unit": "meter", "status": "completed",
            "supplier_name": "Solo Weave",
            "bin_id": "A1-02", "batch": "ENK-2025-001", "lot": "LOT-001",
            "scan_log": [
                {"scan_time": ago(days=15, hours=2, minutes=45), "scanned_by": "Fitri Handayani",
                 "actual_qty": 100.0, "batch": "ENK-2025-001", "lot": "LOT-001",
                 "roll_id": "ROLL-053", "bin_id": "A1-02"},
            ],
            "escalation": None,
            "created_at": ago(days=20), "updated_at": ago(days=14),
            "completed_at": ago(days=14),
        },
    ])
    await db.inventory_movements.insert_many([
        {"id": new_id("mov"), "product_id": "prod_lurik_classic", "warehouse_id": "wh_bandung",
         "movement_type": "inbound_receiving", "quantity": 180.0, "unit": "meter",
         "batch": "LRK-2025-002", "lot": "LOT-002", "roll_id": "ROLL-051/052",
         "source_document": "PO-00003", "notes": "Receiving completed (escalated & resolved) by Fitri Handayani",
         "created_by": "user_wh_02", "timestamp": ago(days=14)},
        {"id": new_id("mov"), "product_id": "prod_endek_bali", "warehouse_id": "wh_bandung",
         "movement_type": "inbound_receiving", "quantity": 100.0, "unit": "meter",
         "batch": "ENK-2025-001", "lot": "LOT-001", "roll_id": "ROLL-053",
         "source_document": "PO-00003", "notes": "Receiving completed by Fitri Handayani",
         "created_by": "user_wh_02", "timestamp": ago(days=14)},
    ])

    # PO-00004 — Currently in receiving (started 3 days ago, partially scanned)
    po4_id = "po_004"
    task4a_id = new_id("wms")
    task4b_id = new_id("wms")
    await db.purchase_orders.insert_one({
        "id": po4_id, "po_number": "PO-00004",
        "supplier_name": "Palembang Silk House", "supplier_contact": "Ibu Ratna | 081278900004",
        "warehouse_id": "wh_jakarta",
        "status": "receiving",
        "items": [
            {"product_id": "prod_songket_palembang", "sku": "SGK-PLB-001",
             "product_name": "Songket Palembang Benang Emas",
             "quantity": 75.0, "received_qty": 40.0, "unit": "meter", "price": 430000,
             "status": "receiving", "inbound_task_id": task4a_id},
            {"product_id": "prod_jumputan_palembang", "sku": "JMP-PLB-001",
             "product_name": "Jumputan Palembang Pelangi",
             "quantity": 120.0, "received_qty": 0.0, "unit": "meter", "price": 130000,
             "status": "waiting_goods", "inbound_task_id": task4b_id},
        ],
        "expected_delivery_date": ago(days=2),
        "notes": "Batch 2025 Q2 - Palembang Collection. Pengiriman dalam 2 tahap.",
        "created_by": "Budi Santoso", "created_at": ago(days=7),
    })
    await db.wms_tasks.insert_many([
        {
            "id": task4a_id, "flow_type": "inbound", "source_type": "purchase_order", "task_subtype": "receiving",
            "po_id": po4_id, "po_number": "PO-00004",
            "product_id": "prod_songket_palembang", "sku": "SGK-PLB-001",
            "product_name": "Songket Palembang Benang Emas",
            "warehouse_id": "wh_jakarta", "warehouse_name": "Gudang Jakarta Utara",
            "expected_qty": 75.0, "received_qty": 40.0, "quantity": 0.0,
            "unit": "meter", "status": "receiving",
            "supplier_name": "Palembang Silk House",
            "bin_id": "B1-01", "batch": "SGK-2025-003", "lot": "LOT-003",
            "scan_log": [
                {"scan_time": ago(days=3, hours=2), "scanned_by": "Eko Prasetyo",
                 "actual_qty": 40.0, "batch": "SGK-2025-003", "lot": "LOT-003",
                 "roll_id": "ROLL-061", "bin_id": "B1-01"},
            ],
            "escalation": None,
            "created_at": ago(days=7), "updated_at": ago(days=3),
        },
        {
            "id": task4b_id, "flow_type": "inbound", "source_type": "purchase_order", "task_subtype": "receiving",
            "po_id": po4_id, "po_number": "PO-00004",
            "product_id": "prod_jumputan_palembang", "sku": "JMP-PLB-001",
            "product_name": "Jumputan Palembang Pelangi",
            "warehouse_id": "wh_jakarta", "warehouse_name": "Gudang Jakarta Utara",
            "expected_qty": 120.0, "received_qty": 0.0, "quantity": 0.0,
            "unit": "meter", "status": "waiting_goods",
            "supplier_name": "Palembang Silk House",
            "scan_log": [],
            "escalation": None,
            "created_at": ago(days=7), "updated_at": ago(days=7),
        },
    ])

    # PO-00005 — Pending (just created today, awaiting delivery — task siap untuk demo)
    po5_id = "po_005"
    task5a_id = new_id("wms")
    await db.purchase_orders.insert_one({
        "id": po5_id, "po_number": "PO-00005",
        "supplier_name": "Toba Craft", "supplier_contact": "Pak Maruli | 081156700005",
        "warehouse_id": "wh_surabaya",
        "status": "receiving",
        "items": [
            {"product_id": "prod_ulos_batak", "sku": "ULS-BTK-001",
             "product_name": "Ulos Batak Ragidup",
             "quantity": 100.0, "received_qty": 0.0, "unit": "meter", "price": 305000,
             "status": "receiving", "inbound_task_id": task5a_id},
        ],
        "expected_delivery_date": ago(hours=-12),
        "notes": "Restock Ulos untuk permintaan pernikahan adat Batak. Barang sudah sampai.",
        "created_by": "Budi Santoso", "created_at": ago(hours=18),
    })
    await db.wms_tasks.insert_one({
        "id": task5a_id, "flow_type": "inbound", "source_type": "purchase_order", "task_subtype": "receiving",
        "po_id": po5_id, "po_number": "PO-00005",
        "product_id": "prod_ulos_batak", "sku": "ULS-BTK-001",
        "product_name": "Ulos Batak Ragidup",
        "warehouse_id": "wh_surabaya", "warehouse_name": "Gudang Surabaya Rungkut",
        "expected_qty": 100.0, "received_qty": 0.0, "quantity": 0.0,
        "unit": "meter", "status": "created",
        "supplier_name": "Toba Craft",
        "scan_log": [],
        "escalation": None,
        "created_at": ago(hours=18), "updated_at": ago(hours=2),
    })

    # PO-00006 — Newly created with fresh receiving task (status: created, ready for demo)
    po6_id = "po_006"
    task6a_id = new_id("wms")
    await db.purchase_orders.insert_one({
        "id": po6_id, "po_number": "PO-00006",
        "supplier_name": "Bali Weave Studio", "supplier_contact": "Pak Gede | 081256700006",
        "warehouse_id": "wh_jakarta",
        "status": "receiving",
        "items": [
            {"product_id": "prod_endek_bali", "sku": "ENK-BALI-001",
             "product_name": "Endek Bali Rangrang",
             "quantity": 80.0, "received_qty": 0.0, "unit": "meter", "price": 270000,
             "status": "receiving", "inbound_task_id": task6a_id},
        ],
        "expected_delivery_date": ago(hours=-2),
        "notes": "Restock Endek Bali untuk koleksi musim semi. Barang baru tiba di gudang.",
        "created_by": "Budi Santoso", "created_at": ago(hours=8),
    })
    await db.wms_tasks.insert_one({
        "id": task6a_id, "flow_type": "inbound", "source_type": "purchase_order", "task_subtype": "receiving",
        "po_id": po6_id, "po_number": "PO-00006",
        "product_id": "prod_endek_bali", "sku": "ENK-BALI-001",
        "product_name": "Endek Bali Rangrang",
        "warehouse_id": "wh_jakarta", "warehouse_name": "Gudang Jakarta Utara",
        "expected_qty": 80.0, "received_qty": 0.0, "quantity": 0.0,
        "unit": "meter", "status": "created",
        "supplier_name": "Bali Weave Studio",
        "scan_log": [],
        "escalation": None,
        "created_at": ago(hours=8), "updated_at": ago(hours=1),
    })

    print("✅ Purchase Orders seeded (PO-00001 to PO-00006 with inbound tasks)")


async def seed_sales_orders():
    """Seed realistic Sales Orders in various stages."""

    # SO-0001 — Dispatched 40 days ago (completed flow)
    so1_id = "so_001"
    ob1a_id = new_id("wms")
    await db.sales_orders.insert_one({
        "id": so1_id, "number": "SO-0001",
        "customer_id": "cust_toko_kain", "customer_name": "Toko Kain Sejahtera",
        "customer_city": "Jakarta",
        "shipping_address": {"city": "Jakarta", "address": "Jl. Mangga Besar Raya No. 45",
                              "recipient_name": "Pak Hendra", "phone": "081234567890"},
        "items": [
            {"product_id": "prod_batik_mega", "sku": "BTK-MEGA-001",
             "product_name": "Batik Mega Mendung Premium", "quantity": 30.0, "unit": "meter",
             "price": 185000, "subtotal": 5550000,
             "warehouse_id": "wh_jakarta", "warehouse_name": "Gudang Jakarta Utara"},
            {"product_id": "prod_tenun_ikat", "sku": "TNI-GRGD-001",
             "product_name": "Tenun Ikat Garuda Premium", "quantity": 20.0, "unit": "meter",
             "price": 225000, "subtotal": 4500000,
             "warehouse_id": "wh_jakarta", "warehouse_name": "Gudang Jakarta Utara"},
        ],
        "total_amount": 10050000, "tax": 0, "grand_total": 10050000,
        "status": "dispatched",
        "payment_status": "paid",
        "allocations": [
            {"warehouse_id": "wh_jakarta", "warehouse_name": "Gudang Jakarta Utara",
             "product_id": "prod_batik_mega", "quantity": 30.0},
            {"warehouse_id": "wh_jakarta", "warehouse_name": "Gudang Jakarta Utara",
             "product_id": "prod_tenun_ikat", "quantity": 20.0},
        ],
        "created_by": "user_sales_01", "created_at": ago(days=45),
        "approved_at": ago(days=44), "approved_by": "user_manager_01",
        "confirmed_at": ago(days=43), "confirmed_by": "user_manager_01",
        "dispatched_at": ago(days=40),
        "notes": "Order reguler bulanan - Toko Kain Sejahtera",
    })
    await db.wms_tasks.insert_one({
        "id": ob1a_id, "flow_type": "outbound", "source_type": "sales_order", "task_subtype": "picking",
        "order_id": so1_id, "order_number": "SO-0001",
        "customer_name": "Toko Kain Sejahtera",
        "product_id": "prod_batik_mega", "sku": "BTK-MEGA-001",
        "product_name": "Batik Mega Mendung Premium",
        "warehouse_id": "wh_jakarta", "warehouse_name": "Gudang Jakarta Utara",
        "quantity": 30.0, "picked_qty": 30.0, "unit": "meter",
        "status": "dispatched",
        "batch": "BTK-2025-001", "lot": "LOT-001",
        "scan_log": [
            {"scan_time": ago(days=41, hours=3), "scanned_by": "Eko Prasetyo",
             "actual_qty": 30.0, "batch": "BTK-2025-001", "lot": "LOT-001",
             "roll_id": "ROLL-001", "bin_id": "A1-01"},
        ],
        "escalation": None,
        "created_at": ago(days=43), "updated_at": ago(days=40),
        "dispatched_at": ago(days=40),
    })
    await db.inventory_movements.insert_many([
        {"id": new_id("mov"), "product_id": "prod_batik_mega", "warehouse_id": "wh_jakarta",
         "movement_type": "outbound_dispatch", "quantity": -30.0, "unit": "meter",
         "batch": "BTK-2025-001", "lot": "LOT-001", "roll_id": "ROLL-001",
         "source_document": "SO-0001", "notes": "Dispatch ke Toko Kain Sejahtera",
         "created_by": "user_wh_01", "timestamp": ago(days=40)},
        {"id": new_id("mov"), "product_id": "prod_tenun_ikat", "warehouse_id": "wh_jakarta",
         "movement_type": "outbound_dispatch", "quantity": -20.0, "unit": "meter",
         "batch": "TNI-2025-001", "lot": "LOT-001", "roll_id": "ROLL-003",
         "source_document": "SO-0001", "notes": "Dispatch ke Toko Kain Sejahtera",
         "created_by": "user_wh_01", "timestamp": ago(days=40)},
    ])

    # SO-0002 — Dispatched 25 days ago, multi-warehouse split
    so2_id = "so_002"
    ob2a_id = new_id("wms")
    ob2b_id = new_id("wms")
    await db.sales_orders.insert_one({
        "id": so2_id, "number": "SO-0002",
        "customer_id": "cust_moda_surabaya", "customer_name": "Moda Surabaya Fashion",
        "customer_city": "Surabaya",
        "shipping_address": {"city": "Surabaya", "address": "Jl. Rungkut Industri No. 22",
                              "recipient_name": "Bapak Andi", "phone": "083456789012"},
        "items": [
            {"product_id": "prod_lurik_classic", "sku": "LRK-CLSC-001",
             "product_name": "Lurik Klasik Solo", "quantity": 100.0, "unit": "meter",
             "price": 95000, "subtotal": 9500000},
        ],
        "total_amount": 9500000, "tax": 0, "grand_total": 9500000,
        "status": "dispatched",
        "payment_status": "paid",
        "allocations": [
            {"warehouse_id": "wh_bandung", "warehouse_name": "Gudang Bandung Kopo",
             "product_id": "prod_lurik_classic", "quantity": 60.0},
            {"warehouse_id": "wh_surabaya", "warehouse_name": "Gudang Surabaya Rungkut",
             "product_id": "prod_lurik_classic", "quantity": 40.0},
        ],
        "created_by": "user_sales_01", "created_at": ago(days=30),
        "approved_at": ago(days=29), "approved_by": "user_manager_01",
        "confirmed_at": ago(days=28), "confirmed_by": "user_manager_01",
        "dispatched_at": ago(days=25),
        "notes": "Order grosir - Lurik split dari 2 gudang",
    })
    await db.wms_tasks.insert_many([
        {
            "id": ob2a_id, "flow_type": "outbound", "source_type": "sales_order", "task_subtype": "picking",
            "order_id": so2_id, "order_number": "SO-0002",
            "customer_name": "Moda Surabaya Fashion",
            "product_id": "prod_lurik_classic", "sku": "LRK-CLSC-001",
            "product_name": "Lurik Klasik Solo",
            "warehouse_id": "wh_bandung", "warehouse_name": "Gudang Bandung Kopo",
            "quantity": 60.0, "picked_qty": 60.0, "unit": "meter",
            "status": "dispatched",
            "batch": "LRK-2025-001", "lot": "LOT-001",
            "scan_log": [
                {"scan_time": ago(days=26, hours=4), "scanned_by": "Fitri Handayani",
                 "actual_qty": 60.0, "batch": "LRK-2025-001", "lot": "LOT-001",
                 "roll_id": "ROLL-011", "bin_id": "A1-01"},
            ],
            "escalation": None,
            "created_at": ago(days=28), "updated_at": ago(days=25),
            "dispatched_at": ago(days=25),
        },
        {
            "id": ob2b_id, "flow_type": "outbound", "source_type": "sales_order", "task_subtype": "picking",
            "order_id": so2_id, "order_number": "SO-0002",
            "customer_name": "Moda Surabaya Fashion",
            "product_id": "prod_lurik_classic", "sku": "LRK-CLSC-001",
            "product_name": "Lurik Klasik Solo",
            "warehouse_id": "wh_surabaya", "warehouse_name": "Gudang Surabaya Rungkut",
            "quantity": 40.0, "picked_qty": 40.0, "unit": "meter",
            "status": "dispatched",
            "batch": "LRK-2025-001", "lot": "LOT-002",
            "scan_log": [
                {"scan_time": ago(days=26, hours=2), "scanned_by": "Eko Prasetyo",
                 "actual_qty": 40.0, "batch": "LRK-2025-001", "lot": "LOT-002",
                 "roll_id": "ROLL-021", "bin_id": "A1-01"},
            ],
            "escalation": None,
            "created_at": ago(days=28), "updated_at": ago(days=25),
            "dispatched_at": ago(days=25),
        },
    ])
    await db.inventory_movements.insert_many([
        {"id": new_id("mov"), "product_id": "prod_lurik_classic", "warehouse_id": "wh_bandung",
         "movement_type": "outbound_dispatch", "quantity": -60.0, "unit": "meter",
         "batch": "LRK-2025-001", "lot": "LOT-001", "roll_id": "ROLL-011",
         "source_document": "SO-0002", "notes": "Dispatch (split) ke Moda Surabaya Fashion",
         "created_by": "user_wh_02", "timestamp": ago(days=25)},
        {"id": new_id("mov"), "product_id": "prod_lurik_classic", "warehouse_id": "wh_surabaya",
         "movement_type": "outbound_dispatch", "quantity": -40.0, "unit": "meter",
         "batch": "LRK-2025-001", "lot": "LOT-002", "roll_id": "ROLL-021",
         "source_document": "SO-0002", "notes": "Dispatch (split) ke Moda Surabaya Fashion",
         "created_by": "user_wh_01", "timestamp": ago(days=25)},
    ])

    # SO-0003 — Dispatched 12 days ago (Songket + Ulos, with escalation resolved)
    so3_id = "so_003"
    ob3a_id = new_id("wms")
    ob3b_id = new_id("wms")
    await db.sales_orders.insert_one({
        "id": so3_id, "number": "SO-0003",
        "customer_id": "cust_butik_bali", "customer_name": "Butik Bali Indah",
        "customer_city": "Denpasar",
        "shipping_address": {"city": "Denpasar", "address": "Jl. Seminyak No. 88",
                              "recipient_name": "Ibu Komang", "phone": "082345678901"},
        "items": [
            {"product_id": "prod_songket_palembang", "sku": "SGK-PLB-001",
             "product_name": "Songket Palembang Benang Emas", "quantity": 25.0, "unit": "meter",
             "price": 450000, "subtotal": 11250000,
             "warehouse_id": "wh_jakarta", "warehouse_name": "Gudang Jakarta Utara"},
            {"product_id": "prod_endek_bali", "sku": "ENK-BALI-001",
             "product_name": "Endek Bali Rangrang", "quantity": 40.0, "unit": "meter",
             "price": 280000, "subtotal": 11200000,
             "warehouse_id": "wh_jakarta", "warehouse_name": "Gudang Jakarta Utara"},
        ],
        "total_amount": 22450000, "tax": 0, "grand_total": 22450000,
        "status": "dispatched",
        "payment_status": "pending",
        "allocations": [
            {"warehouse_id": "wh_jakarta", "warehouse_name": "Gudang Jakarta Utara",
             "product_id": "prod_songket_palembang", "quantity": 25.0},
            {"warehouse_id": "wh_jakarta", "warehouse_name": "Gudang Jakarta Utara",
             "product_id": "prod_endek_bali", "quantity": 40.0},
        ],
        "created_by": "user_sales_01", "created_at": ago(days=18),
        "approved_at": ago(days=17), "approved_by": "user_manager_01",
        "confirmed_at": ago(days=16), "confirmed_by": "user_manager_01",
        "dispatched_at": ago(days=12),
        "notes": "Premium order untuk koleksi butik Bali",
    })
    await db.wms_tasks.insert_many([
        {
            "id": ob3a_id, "flow_type": "outbound", "source_type": "sales_order", "task_subtype": "picking",
            "order_id": so3_id, "order_number": "SO-0003",
            "customer_name": "Butik Bali Indah",
            "product_id": "prod_songket_palembang", "sku": "SGK-PLB-001",
            "product_name": "Songket Palembang Benang Emas",
            "warehouse_id": "wh_jakarta", "warehouse_name": "Gudang Jakarta Utara",
            "quantity": 25.0, "picked_qty": 22.0, "unit": "meter",
            "status": "dispatched",
            "batch": "SGK-2025-001", "lot": "LOT-001",
            "scan_log": [
                {"scan_time": ago(days=13, hours=3), "scanned_by": "Eko Prasetyo",
                 "actual_qty": 22.0, "batch": "SGK-2025-001", "lot": "LOT-001",
                 "roll_id": "ROLL-003", "bin_id": "A2-01"},
            ],
            "escalation": {
                "escalated_at": ago(days=13, hours=4),
                "escalated_by": "Eko Prasetyo",
                "reason": "Fisik di rak hanya 22m, sistem menunjukkan 25m. Kemungkinan selisih dari pemakaian sebelumnya.",
                "status": "resolved",
                "resolved_at": ago(days=13, hours=1),
                "resolved_by": "Dewi Rahayu",
                "resolution_notes": "Disetujui kirim 22m, balance 3m dikoreksi. Customer konfirmasi OK.",
                "adjusted_qty": 22.0,
            },
            "created_at": ago(days=16), "updated_at": ago(days=12),
            "dispatched_at": ago(days=12),
        },
        {
            "id": ob3b_id, "flow_type": "outbound", "source_type": "sales_order", "task_subtype": "picking",
            "order_id": so3_id, "order_number": "SO-0003",
            "customer_name": "Butik Bali Indah",
            "product_id": "prod_endek_bali", "sku": "ENK-BALI-001",
            "product_name": "Endek Bali Rangrang",
            "warehouse_id": "wh_jakarta", "warehouse_name": "Gudang Jakarta Utara",
            "quantity": 40.0, "picked_qty": 40.0, "unit": "meter",
            "status": "dispatched",
            "batch": "ENK-2025-001", "lot": "LOT-001",
            "scan_log": [
                {"scan_time": ago(days=13, hours=2), "scanned_by": "Eko Prasetyo",
                 "actual_qty": 40.0, "batch": "ENK-2025-001", "lot": "LOT-001",
                 "roll_id": "ROLL-053", "bin_id": "A2-01"},
            ],
            "escalation": None,
            "created_at": ago(days=16), "updated_at": ago(days=12),
            "dispatched_at": ago(days=12),
        },
    ])
    await db.inventory_movements.insert_many([
        {"id": new_id("mov"), "product_id": "prod_songket_palembang", "warehouse_id": "wh_jakarta",
         "movement_type": "outbound_dispatch", "quantity": -22.0, "unit": "meter",
         "batch": "SGK-2025-001", "lot": "LOT-001",
         "source_document": "SO-0003", "notes": "Dispatch ke Butik Bali Indah (adjusted after escalation)",
         "created_by": "user_wh_01", "timestamp": ago(days=12)},
        {"id": new_id("mov"), "product_id": "prod_endek_bali", "warehouse_id": "wh_jakarta",
         "movement_type": "outbound_dispatch", "quantity": -40.0, "unit": "meter",
         "batch": "ENK-2025-001", "lot": "LOT-001",
         "source_document": "SO-0003", "notes": "Dispatch ke Butik Bali Indah",
         "created_by": "user_wh_01", "timestamp": ago(days=12)},
    ])

    # SO-0004 — Currently in picking (outbound tasks in progress)
    so4_id = "so_004"
    ob4a_id = new_id("wms")
    ob4b_id = new_id("wms")
    await db.sales_orders.insert_one({
        "id": so4_id, "number": "SO-0004",
        "customer_id": "cust_fashion_bandung", "customer_name": "Fashion Bandung Kencana",
        "customer_city": "Bandung",
        "shipping_address": {"city": "Bandung", "address": "Jl. Dago No. 112, Bandung",
                              "recipient_name": "Ibu Sari", "phone": "085678901234"},
        "items": [
            {"product_id": "prod_batik_mega", "sku": "BTK-MEGA-001",
             "product_name": "Batik Mega Mendung Premium", "quantity": 50.0, "unit": "meter",
             "price": 185000, "subtotal": 9250000},
        ],
        "total_amount": 9250000, "tax": 0, "grand_total": 9250000,
        "status": "confirmed",
        "payment_status": "pending",
        "allocations": [
            {"warehouse_id": "wh_jakarta", "warehouse_name": "Gudang Jakarta Utara",
             "product_id": "prod_batik_mega", "quantity": 50.0},
        ],
        "created_by": "user_sales_01", "created_at": ago(days=5),
        "approved_at": ago(days=4), "approved_by": "user_manager_01",
        "confirmed_at": ago(days=3), "confirmed_by": "user_manager_01",
        "notes": "Urgent order - fashion show upcoming",
    })
    await db.wms_tasks.insert_many([
        {
            "id": ob4a_id, "flow_type": "outbound", "source_type": "sales_order", "task_subtype": "picking",
            "order_id": so4_id, "order_number": "SO-0004",
            "customer_name": "Fashion Bandung Kencana",
            "product_id": "prod_batik_mega", "sku": "BTK-MEGA-001",
            "product_name": "Batik Mega Mendung Premium",
            "warehouse_id": "wh_jakarta", "warehouse_name": "Gudang Jakarta Utara",
            "quantity": 50.0, "picked_qty": 30.0, "unit": "meter",
            "status": "picking",
            "scan_log": [
                {"scan_time": ago(days=2, hours=5), "scanned_by": "Eko Prasetyo",
                 "actual_qty": 30.0, "batch": "BTK-2025-003", "lot": "LOT-003",
                 "roll_id": "ROLL-032", "bin_id": "A1-01"},
            ],
            "escalation": None,
            "created_at": ago(days=3), "updated_at": ago(days=2),
        },
    ])

    # SO-0005 — Approved, awaiting confirmation
    so5_id = "so_005"
    await db.sales_orders.insert_one({
        "id": so5_id, "number": "SO-0005",
        "customer_id": "cust_textile_medan", "customer_name": "Tekstil Medan Jaya",
        "customer_city": "Medan",
        "shipping_address": {"city": "Medan", "address": "Jl. Asia No. 78, Medan",
                              "recipient_name": "Pak Robert", "phone": "081345678905"},
        "items": [
            {"product_id": "prod_tenun_ikat", "sku": "TNI-GRGD-001",
             "product_name": "Tenun Ikat Garuda Premium", "quantity": 50.0, "unit": "meter",
             "price": 225000, "subtotal": 11250000,
             "warehouse_id": "wh_surabaya", "warehouse_name": "Gudang Surabaya Rungkut"},
            {"product_id": "prod_ulos_batak", "sku": "ULS-BTK-001",
             "product_name": "Ulos Batak Ragidup", "quantity": 30.0, "unit": "meter",
             "price": 320000, "subtotal": 9600000,
             "warehouse_id": "wh_surabaya", "warehouse_name": "Gudang Surabaya Rungkut"},
        ],
        "total_amount": 20850000, "tax": 0, "grand_total": 20850000,
        "status": "approved",
        "payment_status": "pending",
        "allocations": [
            {"warehouse_id": "wh_surabaya", "warehouse_name": "Gudang Surabaya Rungkut",
             "product_id": "prod_tenun_ikat", "quantity": 50.0},
            {"warehouse_id": "wh_surabaya", "warehouse_name": "Gudang Surabaya Rungkut",
             "product_id": "prod_ulos_batak", "quantity": 30.0},
        ],
        "created_by": "user_sales_01", "created_at": ago(days=2),
        "approved_at": ago(hours=10), "approved_by": "user_manager_01",
        "notes": "Order besar - Tekstil Medan, perlu konfirmasi segera",
    })

    # SO-0006 — Reserved (just submitted, masih bisa di-cancel/release reservation)
    so6_id = "so_006"
    await db.sales_orders.insert_one({
        "id": so6_id, "number": "SO-0006",
        "customer_id": "cust_toko_kain", "customer_name": "Toko Kain Sejahtera",
        "customer_city": "Jakarta",
        "shipping_address": {"city": "Jakarta", "address": "Jl. Mangga Besar Raya No. 45",
                              "recipient_name": "Pak Hendra", "phone": "081234567890"},
        "items": [
            {"product_id": "prod_lurik_classic", "sku": "LRK-CLSC-001",
             "product_name": "Lurik Klasik Solo", "quantity": 40.0, "unit": "meter",
             "price": 95000, "subtotal": 3800000,
             "warehouse_id": "wh_bandung", "warehouse_name": "Gudang Bandung Kopo"},
            {"product_id": "prod_songket_palembang", "sku": "SGK-PLB-001",
             "product_name": "Songket Palembang Benang Emas", "quantity": 10.0, "unit": "meter",
             "price": 450000, "subtotal": 4500000,
             "warehouse_id": "wh_jakarta", "warehouse_name": "Gudang Jakarta Utara"},
        ],
        "total_amount": 8300000, "tax": 0, "grand_total": 8300000,
        "status": "reserved",
        "payment_status": "pending",
        "reservation_expires_at": (datetime.now(timezone.utc) + timedelta(days=2, hours=18)).isoformat(),
        "allocations": [
            {"warehouse_id": "wh_bandung", "warehouse_name": "Gudang Bandung Kopo",
             "product_id": "prod_lurik_classic", "quantity": 40.0},
            {"warehouse_id": "wh_jakarta", "warehouse_name": "Gudang Jakarta Utara",
             "product_id": "prod_songket_palembang", "quantity": 10.0},
        ],
        "created_by": "user_sales_01", "created_at": ago(hours=2),
        "notes": "Repeat order dari Pak Hendra - Toko Kain Sejahtera (reserved otomatis, demo release reservation)",
    })

    # SO-0007 — Waiting Approval (target tour 'Approve Order')
    so7_id = "so_007"
    await db.sales_orders.insert_one({
        "id": so7_id, "number": "SO-0007",
        "customer_id": "cust_fashion_bandung", "customer_name": "Fashion Bandung Kencana",
        "customer_city": "Bandung",
        "shipping_address": {"city": "Bandung", "address": "Jl. Dago No. 112, Bandung",
                              "recipient_name": "Ibu Sari", "phone": "085678901234"},
        "items": [
            {"product_id": "prod_endek_bali", "sku": "ENK-BALI-001",
             "product_name": "Endek Bali Rangrang", "quantity": 25.0, "unit": "meter",
             "price": 280000, "subtotal": 7000000,
             "warehouse_id": "wh_jakarta", "warehouse_name": "Gudang Jakarta Utara"},
            {"product_id": "prod_jumputan_palembang", "sku": "JMP-PLB-001",
             "product_name": "Jumputan Palembang Pelangi", "quantity": 60.0, "unit": "meter",
             "price": 145000, "subtotal": 8700000,
             "warehouse_id": "wh_bandung", "warehouse_name": "Gudang Bandung Kopo"},
        ],
        "total_amount": 15700000, "tax": 0, "grand_total": 15700000,
        "status": "waiting_approval",
        "payment_status": "pending",
        "reservation_expires_at": (datetime.now(timezone.utc) + timedelta(days=2, hours=22)).isoformat(),
        "allocations": [
            {"warehouse_id": "wh_jakarta", "warehouse_name": "Gudang Jakarta Utara",
             "product_id": "prod_endek_bali", "quantity": 25.0},
            {"warehouse_id": "wh_bandung", "warehouse_name": "Gudang Bandung Kopo",
             "product_id": "prod_jumputan_palembang", "quantity": 60.0},
        ],
        "created_by": "user_sales_01", "created_at": ago(hours=1),
        "notes": "Order baru untuk koleksi musim semi - butuh approval manager",
    })

    # SO-0008 — Reserved + multi-product (target untuk demo release reservation)
    so8_id = "so_008"
    await db.sales_orders.insert_one({
        "id": so8_id, "number": "SO-0008",
        "customer_id": "cust_butik_bali", "customer_name": "Butik Bali Indah",
        "customer_city": "Denpasar",
        "shipping_address": {"city": "Denpasar", "address": "Jl. Seminyak No. 88",
                              "recipient_name": "Ibu Komang", "phone": "082345678901"},
        "items": [
            {"product_id": "prod_batik_mega", "sku": "BTK-MEGA-001",
             "product_name": "Batik Mega Mendung Premium", "quantity": 15.0, "unit": "meter",
             "price": 185000, "subtotal": 2775000,
             "warehouse_id": "wh_jakarta", "warehouse_name": "Gudang Jakarta Utara"},
        ],
        "total_amount": 2775000, "tax": 0, "grand_total": 2775000,
        "status": "reserved",
        "payment_status": "pending",
        "reservation_expires_at": (datetime.now(timezone.utc) + timedelta(days=1, hours=12)).isoformat(),
        "allocations": [
            {"warehouse_id": "wh_jakarta", "warehouse_name": "Gudang Jakarta Utara",
             "product_id": "prod_batik_mega", "quantity": 15.0},
        ],
        "created_by": "user_sales_01", "created_at": ago(hours=8),
        "notes": "Reservasi sample untuk koleksi butik - akan dikonfirmasi",
    })

    # ===== Extra OUTBOUND tasks (status: created) untuk demo tour Process Outbound =====
    # Task 1 — SO-0005 outbound (status created, fresh ready to pick)
    ob5a_id = new_id("wms")
    ob5b_id = new_id("wms")
    await db.wms_tasks.insert_many([
        {
            "id": ob5a_id, "flow_type": "outbound", "source_type": "sales_order", "task_subtype": "picking",
            "order_id": so5_id, "order_number": "SO-0005",
            "customer_name": "Tekstil Medan Jaya",
            "product_id": "prod_tenun_ikat", "sku": "TNI-GRGD-001",
            "product_name": "Tenun Ikat Garuda Premium",
            "warehouse_id": "wh_surabaya", "warehouse_name": "Gudang Surabaya Rungkut",
            "quantity": 50.0, "picked_qty": 0.0, "unit": "meter",
            "status": "created",
            "scan_log": [], "escalation": None,
            "created_at": ago(hours=10), "updated_at": ago(hours=10),
        },
        {
            "id": ob5b_id, "flow_type": "outbound", "source_type": "sales_order", "task_subtype": "picking",
            "order_id": so5_id, "order_number": "SO-0005",
            "customer_name": "Tekstil Medan Jaya",
            "product_id": "prod_ulos_batak", "sku": "ULS-BTK-001",
            "product_name": "Ulos Batak Ragidup",
            "warehouse_id": "wh_surabaya", "warehouse_name": "Gudang Surabaya Rungkut",
            "quantity": 30.0, "picked_qty": 0.0, "unit": "meter",
            "status": "created",
            "scan_log": [], "escalation": None,
            "created_at": ago(hours=10), "updated_at": ago(hours=10),
        },
    ])

    print("✅ Sales Orders seeded (SO-0001 to SO-0008 with outbound tasks)")


async def seed_document_templates():
    await db.document_templates.insert_many([
        {
            "id": "tmpl_sj_default", "document_type": "surat_jalan", "name": "Template SJ Standard",
            "header": "KAIN NUSANTARA — Enterprise Textile Warehouse",
            "footer": "Barang diterima dalam kondisi baik. Tanda tangan sebagai bukti penerimaan.",
            "columns": ["sku", "name", "qty", "unit", "batch", "lot"],
            "logo_url": "", "paper_size": "A4", "orientation": "portrait", "margin_mm": 12,
            "signature_left": "Disiapkan Oleh", "signature_right": "Diterima Oleh",
            "section_order": ["header", "customer", "items", "allocation", "signature", "footer"],
            "status": "active", "created_by": "seed", "created_at": ago(days=180)
        },
        {
            "id": "tmpl_inv_default", "document_type": "invoice", "name": "Template Invoice Standard",
            "header": "KAIN NUSANTARA — Invoice",
            "footer": "Pembayaran dalam 30 hari. Terima kasih atas kepercayaan Anda.",
            "columns": ["sku", "name", "qty", "unit", "price", "subtotal"],
            "logo_url": "", "paper_size": "A4", "orientation": "portrait", "margin_mm": 12,
            "signature_left": "Dibuat Oleh", "signature_right": "Disetujui Oleh",
            "section_order": ["header", "customer", "items", "signature", "footer"],
            "status": "active", "created_by": "seed", "created_at": ago(days=180)
        },
    ])
    print("✅ Document templates seeded")


async def seed_permissions():
    if await db.permission_settings.count_documents({}) == 0:
        await db.permission_settings.insert_one(
            {"id": "default", "matrix": DEFAULT_PERMISSIONS, "updated_at": ago(days=30)}
        )
    print("✅ Permissions seeded")


async def seed_audit_logs():
    """Seed some realistic audit log entries."""
    logs = [
        {"id": new_id("audit"), "user_id": "user_admin_01", "user_name": "Budi Santoso",
         "action": "CREATE", "resource": "purchase_order", "resource_id": "po_001",
         "details": {"po_number": "PO-00001", "supplier": "Cirebon Craft"},
         "timestamp": ago(days=50)},
        {"id": new_id("audit"), "user_id": "user_wh_01", "user_name": "Eko Prasetyo",
         "action": "COMPLETE", "resource": "inbound_task", "resource_id": "completed",
         "details": {"po_number": "PO-00001", "product": "Batik Mega Mendung Premium", "quantity": 150},
         "timestamp": ago(days=44)},
        {"id": new_id("audit"), "user_id": "user_sales_01", "user_name": "Ayu Permatasari",
         "action": "CREATE", "resource": "sales_order", "resource_id": "so_001",
         "details": {"order_number": "SO-0001", "customer": "Toko Kain Sejahtera", "total": 10050000},
         "timestamp": ago(days=45)},
        {"id": new_id("audit"), "user_id": "user_manager_01", "user_name": "Dewi Rahayu",
         "action": "APPROVE", "resource": "sales_order", "resource_id": "so_001",
         "details": {"order_number": "SO-0001"},
         "timestamp": ago(days=44)},
        {"id": new_id("audit"), "user_id": "user_wh_02", "user_name": "Fitri Handayani",
         "action": "ESCALATE", "resource": "inbound_task", "resource_id": "escalated",
         "details": {"po_number": "PO-00003", "reason": "Qty kurang dari supplier"},
         "timestamp": ago(days=15, hours=5)},
        {"id": new_id("audit"), "user_id": "user_manager_01", "user_name": "Dewi Rahayu",
         "action": "RESOLVE_ESCALATION", "resource": "inbound_task", "resource_id": "resolved",
         "details": {"po_number": "PO-00003", "adjusted_qty": 180},
         "timestamp": ago(days=15, hours=2)},
    ]
    await db.audit_logs.insert_many(logs)
    print(f"✅ Audit logs seeded ({len(logs)} entries)")


async def backfill_order_snapshots():
    """Snapshot-completeness (kontrak FE↔BE): pastikan setiap sales_order punya
    `sales_name` (dari user pembuat) & `shipping_city` (dari customer/alamat).
    create_order menghasilkan field ini; seed harus mengikuti kontrak yang sama
    agar OrdersView tidak menampilkan label kosong (cegah RC-2/G1 drift)."""
    users_map = {u["id"]: u["name"]
                 for u in await db.users.find({}, {"_id": 0, "id": 1, "name": 1}).to_list(100)}
    patched = 0
    for o in await db.sales_orders.find({}, {"_id": 0}).to_list(500):
        upd = {}
        if not o.get("sales_name"):
            upd["sales_name"] = users_map.get(o.get("created_by"), "Sales")
        if not o.get("shipping_city"):
            upd["shipping_city"] = (
                o.get("customer_city")
                or (o.get("shipping_address") or {}).get("city")
                or "-"
            )
        if upd:
            await db.sales_orders.update_one({"id": o["id"]}, {"$set": upd})
            patched += 1
    print(f"✅ Order snapshots backfilled (sales_name/shipping_city) → {patched} order")



async def seed_entities_and_backfill():
    """Multi-Entity (Fase 0): seed entitas legal + tag entity_id ke data transaksi.

    Distribusi realistis: ~70% ke PT Kain Suka Cita, ~30% ke CV Kanda Suka,
    agar Entity Switcher punya data untuk difilter. Lalu generate notifikasi
    dari kondisi REAL (stok menipis / reservasi mendekati kedaluwarsa).
    """
    await db.business_entities.insert_many([
        {"id": "ent_ksc", "legal_name": "PT Kain Suka Cita", "short_name": "KSC",
         "type": "PT", "npwp": "01.234.567.8-901.000",
         "address": "Jl. Soekarno Hatta No. 100", "city": "Bandung",
         "default_tax_mode": "ppn", "doc_prefix": "KSC", "logo_url": "",
         "status": "active", "created_by": "seed", "created_at": now_iso(), "updated_at": now_iso()},
        {"id": "ent_kanda", "legal_name": "CV Kanda Suka", "short_name": "Kanda",
         "type": "CV", "npwp": "02.345.678.9-012.000",
         "address": "Jl. Mangga Dua Raya No. 22", "city": "Jakarta",
         "default_tax_mode": "non_ppn", "doc_prefix": "KANDA", "logo_url": "",
         "status": "active", "created_by": "seed", "created_at": now_iso(), "updated_at": now_iso()},
    ])
    tagged = 0
    for col in ["sales_orders", "purchase_orders", "customers", "invoices"]:
        docs = await db[col].find({}, {"_id": 0, "id": 1}).to_list(2000)
        for d in docs:
            ent = "ent_kanda" if random.random() < 0.3 else "ent_ksc"
            await db[col].update_one({"id": d["id"]}, {"$set": {"entity_id": ent}})
            tagged += 1
    # Notifikasi awal dari data nyata
    try:
        from services.notification_service import generate_system_notifications
        created = await generate_system_notifications()
    except Exception as e:  # pragma: no cover
        created = 0
        print(f"  (notif generate skipped: {e})")
    print(f"✅ Entities seeded (2) · entity_id tagged → {tagged} dok · {created} notifikasi")


async def backfill_order_pricing():
    """Fase 1B — hitung ulang breakdown harga (diskon item/order + PPN) untuk tiap
    sales_order memakai engine YANG SAMA dengan create_order, agar seed tidak drift
    dari aplikasi (PPN mengikuti PKP/non-PKP entitas; invarian total_amount tetap GROSS)."""
    from services.config_service import compute_order_pricing, evaluate_approval
    gs = await db.system_settings.find_one({"scope": "global"}, {"_id": 0}) or {}
    default_term = (gs.get("finance", {}) or {}).get("default_payment_term_code", "NET30")
    terms = {t["code"]: t for t in await db.payment_terms.find({}, {"_id": 0}).to_list(50)}
    patched = 0
    for o in await db.sales_orders.find({}, {"_id": 0}).to_list(500):
        raw_items = [{
            "product_id": it.get("product_id"), "sku": it.get("sku"),
            "product_name": it.get("product_name"), "quantity": it.get("quantity", 0),
            "unit": it.get("unit", "meter"), "price": it.get("price", 0),
            "discount_percent": it.get("discount_percent", 0) or 0,
        } for it in o.get("items", [])]
        pricing = await compute_order_pricing(
            raw_items, o.get("entity_id"), o.get("order_discount_percent", 0) or 0)
        term_code = o.get("payment_term_code") or default_term
        appr = await evaluate_approval("sales_order", pricing["grand_total"], o.get("entity_id"))
        await db.sales_orders.update_one({"id": o["id"]}, {"$set": {
            "items": pricing["items"], "total_amount": pricing["total_amount"],
            "items_discount_total": pricing["items_discount_total"],
            "order_discount_percent": pricing["order_discount_percent"],
            "order_discount_amount": pricing["order_discount_amount"],
            "discount_total": pricing["discount_total"],
            "net_subtotal": pricing["net_subtotal"], "dpp": pricing["dpp"],
            "ppn_rate": pricing["ppn_rate"], "ppn_mode": pricing["ppn_mode"],
            "is_pkp": pricing["is_pkp"], "ppn_amount": pricing["ppn_amount"],
            "grand_total": pricing["grand_total"],
            "payment_term_code": term_code,
            "payment_term_name": (terms.get(term_code) or {}).get("name", term_code),
            "approval_required": appr["requires_approval"],
            "required_approval_role": appr["required_role"],
            "approval_amount": pricing["grand_total"],
        }})
        patched += 1
    print(f"✅ Order pricing backfilled (diskon+PPN+approval, engine create_order) → {patched} order")


async def seed_price_approvals():
    """Sub-fase 1.7 — contoh special price (1 approved + 1 pending), idempotent."""
    if await db.price_approvals.count_documents({}) > 0:
        return 0
    custs = await db.customers.find({"status": "active"}, {"_id": 0}).sort("created_at", 1).to_list(5)
    prods = await db.products.find({"status": "active"}, {"_id": 0}).sort("created_at", 1).to_list(5)
    if not custs or not prods:
        return 0
    sales_user = await db.users.find_one({"role": "sales"}, {"_id": 0}) or {}
    mgr = await db.users.find_one({"role": "manager"}, {"_id": 0}) or {}
    future = (datetime.now(timezone.utc) + timedelta(days=120)).date().isoformat() + "T23:59:59+00:00"
    c0, p0 = custs[0], prods[0]
    c1 = custs[1] if len(custs) > 1 else custs[0]
    p1 = prods[1] if len(prods) > 1 else prods[0]
    docs = [
        {
            "id": new_id("pra"), "entity_id": c0.get("entity_id") or "ent_ksc",
            "customer_id": c0["id"], "customer_name": c0.get("name", ""),
            "product_id": p0["id"], "sku": p0.get("sku", ""), "product_name": p0.get("name", ""),
            "normal_price": round(float(p0.get("price", 0) or 0), 2),
            "requested_price": round(float(p0.get("price", 0) or 0) * 0.85, 2),
            "min_quantity": 20, "unit": p0.get("base_unit", "meter"),
            "reason": "Repeat order volume besar — nego harga grosir",
            "valid_from": now_iso(), "valid_until": future,
            "status": "approved", "attachments": [],
            "requested_by": sales_user.get("id"), "requested_by_name": sales_user.get("name", "Sales"),
            "approved_by": mgr.get("id"), "approved_by_name": mgr.get("name", "Manager"),
            "decision_notes": "Disetujui untuk pelanggan loyal", "decided_at": now_iso(),
            "created_at": now_iso(), "updated_at": now_iso(),
        },
        {
            "id": new_id("pra"), "entity_id": c1.get("entity_id") or "ent_ksc",
            "customer_id": c1["id"], "customer_name": c1.get("name", ""),
            "product_id": p1["id"], "sku": p1.get("sku", ""), "product_name": p1.get("name", ""),
            "normal_price": round(float(p1.get("price", 0) or 0), 2),
            "requested_price": round(float(p1.get("price", 0) or 0) * 0.90, 2),
            "min_quantity": 10, "unit": p1.get("base_unit", "meter"),
            "reason": "Permintaan diskon promo pameran",
            "valid_from": now_iso(), "valid_until": "",
            "status": "pending", "attachments": [],
            "requested_by": sales_user.get("id"), "requested_by_name": sales_user.get("name", "Sales"),
            "approved_by": None, "approved_by_name": None,
            "decision_notes": "", "decided_at": None,
            "created_at": now_iso(), "updated_at": now_iso(),
        },
    ]
    await db.price_approvals.insert_many(docs)
    print(f"✅ Price approvals seeded ({len(docs)})")
    return len(docs)



async def seed_all(db_instance=None):
    """
    Run the complete seed pipeline. Can be called from an external module
    (e.g. FastAPI endpoint) by passing a Motor DB instance.

    Returns a summary dict with counts of inserted records.
    """
    if db_instance is not None:
        init_with_db(db_instance)
    if db is None:
        raise RuntimeError(
            "Seed pipeline requires a DB instance. "
            "Either call init_with_db(db) first or pass db_instance to seed_all()."
        )

    print("\n🚀 Starting Kain Nusantara Realistic Seed...\n")
    await clear_collections()
    await seed_users()
    await seed_uoms()
    await seed_warehouses()
    await seed_products()
    await seed_customers()
    await seed_inventory_initial()
    await seed_inventory_movements_initial()
    await seed_purchase_orders()
    await seed_sales_orders()
    await backfill_order_snapshots()
    await seed_document_templates()
    await seed_permissions()
    await seed_audit_logs()
    await seed_entities_and_backfill()
    # Fase 0.5 — Roll-as-SSOT: backfill owner + generate rolls + rebuild balances
    await db.inventory_balances.update_many(
        {"owner_entity_id": {"$exists": False}}, {"$set": {"owner_entity_id": "ent_ksc"}}
    )
    await db.inventory_movements.update_many(
        {"owner_entity_id": {"$exists": False}}, {"$set": {"owner_entity_id": "ent_ksc"}}
    )
    from services.roll_service import generate_rolls_from_balances
    roll_result = await generate_rolls_from_balances(created_by="seed")
    print(f"✅ Inventory rolls generated ({roll_result.get('rolls', 0)} rolls · {roll_result.get('segments', 0)} segmen)")
    # Fase 1A — Configuration Foundation defaults
    from services.config_service import seed_config_defaults
    cfg = await seed_config_defaults()
    print(f"✅ Config defaults seeded (settings {cfg.get('settings',0)} · payment_terms {cfg.get('payment_terms',0)} · approval_rules {cfg.get('approval_rules',0)})")
    # Sub-fase 1.7 — Special Price / Approval Harga (contoh)
    await seed_price_approvals()
    # Fase 1B — backfill pricing (diskon+PPN) agar seed konsisten dgn create_order
    await backfill_order_pricing()
    print("\n✅ All realistic seed data inserted successfully!")

    # Compute summary counts
    summary = {
        "users": await db.users.count_documents({}),
        "products": await db.products.count_documents({}),
        "customers": await db.customers.count_documents({}),
        "warehouses": await db.warehouses.count_documents({}),
        "purchase_orders": await db.purchase_orders.count_documents({}),
        "sales_orders": await db.sales_orders.count_documents({}),
        "inbound_tasks": await db.wms_tasks.count_documents({"flow_type": "inbound"}),
        "outbound_tasks": await db.wms_tasks.count_documents({"flow_type": "outbound"}),
        "inventory_balances": await db.inventory_balances.count_documents({}),
        "inventory_movements": await db.inventory_movements.count_documents({}),
        "inventory_rolls": await db.inventory_rolls.count_documents({}),
        "audit_logs": await db.audit_logs.count_documents({}),
        "price_approvals": await db.price_approvals.count_documents({}),
    }
    return summary


async def main():
    """Standalone CLI entry point — creates its own DB connection."""
    mongo_url = os.environ["MONGO_URL"]
    client = AsyncIOMotorClient(mongo_url)
    db_instance = client[os.environ["DB_NAME"]]
    summary = await seed_all(db_instance)
    client.close()
    print("\n📋 Summary:")
    print(f"  - {summary['users']} Users (admin, sales, manager, warehouse×2)")
    print(f"  - {summary['products']} Products (Batik, Tenun, Lurik, Songket, Ulos, Jumputan, Endek)")
    print(f"  - {summary['customers']} Customers")
    print(f"  - {summary['warehouses']} Warehouses (Jakarta, Bandung, Surabaya)")
    print(f"  - {summary['purchase_orders']} Purchase Orders (PO-00001 → PO-00006)")
    print(f"  - {summary['sales_orders']} Sales Orders (SO-0001 → SO-0008)")
    print(f"  - {summary['inbound_tasks']} Inbound tasks · {summary['outbound_tasks']} Outbound tasks")
    print(f"  - {summary['inventory_balances']} inventory balances · {summary['inventory_movements']} movements")
    print(f"  - {summary['inventory_rolls']} inventory rolls (Roll-as-SSOT)")
    print(f"  - {summary['audit_logs']} audit logs")


if __name__ == "__main__":
    asyncio.run(main())
