# ENTITY REGISTRY — SSOT Map
## Kain Nusantara Platform

**WAJIB DIBACA SEBELUM MEMBUAT COLLECTION, SCHEMA, ATAU ENDPOINT BARU.**

File ini adalah satu-satunya sumber kebenaran untuk semua entitas bisnis.
Sebelum membuat apapun yang baru, tanya: **"Apakah ini sudah ada di sini?"**

**Update wajib setiap kali ada:**
- Collection baru ditambahkan
- Schema baru dibuat
- Endpoint baru untuk entitas yang sudah ada
- Component baru untuk entitas yang sudah ada

---

## 📋 QUICK LOOKUP TABLE

| Entitas | Collection | Router | Schema | Frontend Component |
|---|---|---|---|---|
| User | `users` | `routers/auth.py`, `routers/users.py` | `UserCreate` | `AdminView` (tab Users) |
| Session (Auth) | `sessions` | `routers/auth.py` | — | `LoginScreen` |
| Product | `products` | `routers/products.py` | `ProductPayload` | `ProductCard`, `AdminView` (tab Product) |
| Customer | `customers` | `routers/customers.py` | `CustomerCreate` | `CustomerPanel`, `AdminView` (tab Customer) |
| Warehouse | `warehouses` | `routers/warehouses.py` | `WarehousePayload` | `AdminView` (tab Warehouse) |
| UOM | `uoms` | `routers/uoms.py` | `UOMPayload` | `AdminView` (tab UOM) |
| Sales Order | `sales_orders` | `routers/sales_orders.py` | `SalesOrderCreate` | `SalesPortal`, `OrdersView`, `CartPanel` |
| Invoice | `invoices` | `routers/invoices.py` | `PaymentSimulationCreate` | `DocumentsView` |
| Inventory Balance | `inventory_balances` | `routers/inventory.py` | — | `InventoryStockView` |
| Inventory Roll *(IMPLEMENTED Fase 0.5)* | `inventory_rolls` | `routers/inventory.py`, `services/roll_service.py` | `RollPayload` | `InventoryStockView`, `SalesPortal` |
| Inventory Movement | `inventory_movements` | `routers/inventory.py` | — | `InventoryStockView` (tab Ledger) |
| WMS Task | `wms_tasks` | `routers/wms.py` | `WMSTaskCreate` | `ScannerTaskPanel` |
| Inbound Task | `wms_tasks` *(flow_type=inbound)* | `routers/inbound_receiving.py` | — | `InboundScanInterface` |
| Outbound Task | `wms_tasks` *(flow_type=outbound)* | `routers/outbound_picking.py` | — | `OutboundScanInterface` |
| Transfer | `warehouse_transfers` | `routers/transfers.py` | `TransferCreate` | `TransferManagement` |
| Cycle Count | `cycle_count_sessions` | `routers/cycle_count.py` | — | `CycleCount` |
| Purchase Order | `purchase_orders` | `routers/purchase_orders.py` | `PurchaseOrderCreate` | `PurchaseOrderManagement` |
| Document Template | `document_templates` | `routers/documents.py` | `TemplatePayload` | `DocumentsView`, `AdminView` (tab Templates) |
| Generated Document | `generated_documents` | `routers/documents.py` | `DocumentGenerate` | `DocumentsView` |
| Permission Settings | `permission_settings` | `routers/admin.py` | `PermissionUpdate` | `AdminView` (tab Permissions) |
| Audit Log | `audit_logs` | `routers/audit.py` | — | `AdminView` (tab Audit) |
| Onboarding | `user_onboarding` | `routers/onboarding.py` | — | `OnboardingPanel` |

---

## 🗂️ DETAIL ENTITAS

### users
```
Collection:  users
Routers:     routers/auth.py (login, me, logout)
             routers/users.py (CRUD)
Schema:      schemas.py → UserCreate, UserResponse
Component:   AdminView.jsx (tab Users), LoginScreen (CoreWidgets.jsx)
Key Fields:
  id          string   prefix "user_"
  name        string
  email       string   UNIQUE
  role        enum     admin | sales | manager | warehouse
  password_hash string  SHA256 hash (kain-nusantara::password)
  status      enum     active | inactive
  created_at  string   ISO 8601 UTC

⚠️ JANGAN BUAT: staff, karyawan, operator, employee (untuk user system)
⚠️ Auth: Bearer token via Authorization header (BUKAN cookie)
⚠️ Password: hash_password() dari core_utils.py — jangan pake bcrypt
```

### sessions
```
Collection:  sessions
Router:      routers/auth.py (auto-managed)
Key Fields:
  token       string   format: "sess_[hex12]"
  user_id     string   FK → users.id
  created_at  string

⚠️ JANGAN query sessions langsung dari router lain
⚠️ Gunakan current_user() dari dependencies.py
```

### products
```
Collection:  products
Router:      routers/products.py
Schema:      schemas.py → ProductPayload
Component:   ProductCard.jsx, AdminView.jsx (tab Product), SalesPortal.jsx
Key Fields:
  id          string   prefix "prod_"
  sku         string   UNIQUE — format: CAT-MOTIF-NNN (e.g. BTK-MEGA-001)
  name        string
  category    enum     Batik | Tenun | Lurik | Songket | Ulos | Jumputan | Endek
  variant     string
  color       string
  motif       string
  grade       enum     A | A+ | B | C
  supplier    string   (string only saat ini, bukan FK)
  base_unit   string   meter | yard | roll | pcs
  price       float    IDR per base_unit
  image       string   URL
  status      enum     active | inactive
  uom_conversions  list  [{from_unit, to_unit, factor}]
  batch_lot_rolls  list  [{batch, lot, roll_id}]
  --- METADATA SMART-SEARCH / AI-READY [PROPOSED KN_16 §8B.6] (disiapkan, diisi bertahap) ---
  description      text   deskripsi panjang (marketing/search)
  specifications   object {komposisi, lebar_cm, gramasi, perawatan, asal, ...} (key-value terstruktur)
  tags             list   [string]
  media            list   [{type: image|video, url}]  (multi-media; image lama tetap kompat)
  search_keywords  list   [string]  (untuk smart search)
  attributes       object {} facet/filter terstruktur
  ai_meta          object { embedding: [], recommender_tags: [], updated_at }  (KOSONG dulu — engine nanti)
  created_at  string
  updated_at  string

⚠️ SSOT TUNGGAL: Sales-view & Inventory-view = PROYEKSI dari products yang sama, BUKAN tabel terpisah
   (mis. GET /products?view=sales vs ?view=inventory). Cegah data ganda/konflik.
⚠️ JANGAN BUAT: items, goods, materials, kain, fabric, accessories, products_sales, products_inventory
⚠️ Stok ADA DI inventory_balances/inventory_rolls, BUKAN di products
```

### customers
```
Collection:  customers
Router:      routers/customers.py
Schema:      schemas.py → CustomerCreate, CustomerAddress
Component:   CustomerPanel.jsx, AdminView.jsx (tab Customer)
Key Fields:
  id          string   prefix "cust_"
  code        string   format: "CUST-NNNN"
  name        string
  pic_name    string   nama contact person
  phone       string
  email       string
  type        enum     Retailer | Wholesaler | Boutique
  city        string
  status      enum     active | inactive
  addresses   list     [{id, label, recipient_name, phone, city, address, is_primary}]
  npwp, credit_limit, sales_pic, entity_id   (sudah ada)
  --- CRM-LITE [PROPOSED KN_17] ---
  assigned_sales_id  string  FK users (salesperson pemilik) — WAJIB (kunci manajemen; sales kelola miliknya)
  segment            enum    Retail|Wholesale|Distributor|VIP  (KLASIFIKASI saja, BUKAN penentu harga)
  tags               list    [string]
  contacts           list    [{name, role, phone, email, is_primary}]
  lot_policy         enum    prefer_single|strict_single|allow_mixed (default prefer_single; KN_15)
  payment_profile    object  {allowed_methods:[kontan|tunai|tempo|dp|bertahap], default_method,
                              term_days, dp_percent, installment:{count,interval_days}}
  credit             object  {credit_limit, ar_outstanding(derived), overdue_amount(derived),
                              status: active|warning|blocked}
  customer_group_id  string? penghubung customer sama lintas-entitas (DISIAPKAN, default kosong) [KN_17 S38]
  status      enum     active | inactive | blocked
  created_by  string
  created_at  string

⚠️ scoped entity_id (customer terpisah per entitas; customer sama boleh lintas-entitas; kunci=assigned_sales_id)
⚠️ RBAC row-level: role=sales hanya lihat/kelola customer assigned_sales_id==dirinya (enforce backend)
⚠️ JANGAN BUAT: clients, buyers, pembeli, pelanggan_toko, crm_customers
```

### warehouses
```
Collection:  warehouses
Router:      routers/warehouses.py
Schema:      schemas.py → WarehousePayload
Component:   AdminView.jsx (tab Warehouse)
Key Fields:
  id          string   prefix "wh_" (contoh: wh_jakarta, wh_bandung)
  code        string   format: "WH-XXX"
  name        string
  city        string
  lat, lng    float    koordinat GPS
  active      bool
  zones       list     [{id, name, racks: [{id, name, bins: [{id, code, capacity}]}]}]
  created_at  string

⚠️ Hierarchy: Zone → Rack → Bin
⚠️ JANGAN BUAT: gudang, depot, storage_location sebagai collection terpisah
⚠️ Zone/Rack/Bin adalah EMBEDDED dalam warehouse document
```

### uoms
```
Collection:  uoms
Router:      routers/uoms.py
Schema:      schemas.py → UOMPayload
Component:   AdminView.jsx (tab UOM)
Default UOMs:
  uom_meter  → MTR (length, precision 2)
  uom_yard   → YRD (length, precision 2)
  uom_roll   → RLL (volume, precision 0)
  uom_pcs    → PCS (count, precision 0)
Key Fields:
  id, code, name, base_type (length|volume|weight|count), precision, status

⚠️ JANGAN BUAT: satuan, unit_ukur, measurement
```

### sales_orders
```
Collection:  sales_orders
Router:      routers/sales_orders.py
Schema:      schemas.py → SalesOrderCreate, SalesOrderItemIn
Component:   SalesPortal.jsx, OrdersView.jsx, CartPanel.jsx
Status Lifecycle:
  reserved → waiting_approval → approved → confirmed → dispatched → done
  (cancelled tersedia di setiap stage)
Key Fields:
  id          string   prefix "so_"
  number       string  format: "SO-NNNNN"  (FIELD = "number", BUKAN "order_number")
  customer_id  string  FK → customers.id
  customer_name string SNAPSHOT (denormalized)
  items        list    [{product_id, product_name, sku, quantity, unit, price, subtotal,
                          discount_percent, discount_amount, line_total}]
                        (FIELD item = "quantity" & "price"; BUKAN "qty"/"unit_price")
                        subtotal = price×quantity (GROSS, invarian); line_total = subtotal−discount_amount
  allocations  list    [{warehouse_id, warehouse_name, warehouse_city, product_id, quantity}]
                        SNAPSHOT fulfillment (top-level, dipakai render dokumen)
  status       enum    (lihat lifecycle di atas)
  total_amount float    = Σ items.subtotal (GROSS — invarian verify_data_integrity L4)
  # Fase 1B — breakdown diskon + PPN (field TERPISAH agar total_amount tetap GROSS):
  items_discount_total   float
  order_discount_percent float   order_discount_amount float   discount_total float
  net_subtotal float   = total_amount − discount_total (= DPP base)
  dpp float   ppn_rate float   ppn_mode enum(excluded|included)   is_pkp bool
  ppn_amount float   grand_total float  (= yang dibayar customer)
  payment_term_code string   payment_term_name string   payment_status enum(pending|paid_partial|paid)
  # Fase 1B — approval dinamis (dari approval_rules):
  approval_required bool   required_approval_role string|null   approval_amount float
  sales_name   string
  shipping_address_id string
  reservation_expires_at string  UTC ISO
  created_at, updated_at string

⚠️ JANGAN BUAT: orders, customer_orders, so_list, penjualan
⚠️ Stock reservation terjadi di inventory_balances SAAT order dibuat
⚠️ Dispatch flow: sales_orders.confirm → wms.outbound_from_order → outbound_picking.dispatch
⚠️ Fase 1B: pricing dihitung services/config_service.compute_order_pricing (PPN ikut PKP entitas);
   approval via evaluate_approval + role_satisfies. INVARIAN: total_amount & item.subtotal tetap GROSS.
```

### invoices
```
Collection:  invoices
Router:      routers/invoices.py
Schema:      schemas.py → PaymentSimulationCreate
Key Fields:
  id, number ("INV-NNNNN-NN"), order_id, order_number, customer_id, customer_name, entity_id,
  amount (= grand_total order), status (paid), method, created_by, created_at
  # Fase 1B — snapshot pajak untuk Faktur/Invoice:
  total_amount, discount_total, net_subtotal, dpp, ppn_rate, ppn_mode, ppn_amount, grand_total,
  payment_term_code, payment_term_name

⚠️ SIMULATED payment — belum real gateway
⚠️ amount default = order.grand_total (server-authoritative); jangan embed _id sub-dok (RC ObjectId)
⚠️ JANGAN BUAT: bills, tagihan, faktur sebagai collection terpisah
```

### inventory_balances
```
Collection:  inventory_balances
Router:      routers/inventory.py
Component:   InventoryStockView.jsx
Key Fields:
  id           string   prefix "bal_"
  product_id   string   FK → products.id
  warehouse_id string   FK → warehouses.id
  owner_entity_id string FK → business_entities.id   [IMPLEMENTED Fase 0.5 — kepemilikan, 3-key]
  on_hand_qty  float    total fisik (= Σ bucket fisik)
  available_qty / reserved_qty / committed_qty / picked_qty / packed_qty / quarantine_qty / blocked_qty / damaged_qty  float (bucket fisik)
  on_order_qty / in_transit_inbound_qty / in_transit_transfer_qty / in_transit_intercompany_qty / in_transit_sales_qty  float (pipeline/transit)
  owned_qty / incoming_qty / atp_qty  float (derived)
  in_transit_qty float  legacy alias (= Σ transit)
  updated_at   string

⚠️ UNIQUE per (product_id + warehouse_id + owner_entity_id)  [IMPLEMENTED Fase 0.5]
   Balance = PROYEKSI/cache yang diturunkan dari inventory_rolls (SSOT fisik) via roll_service.rebuild_balance().
   [KN_15 §3.4] Bucket DETAIL: fisik (available/reserved/committed/picked/packed/quarantine/blocked/damaged→on_hand)
   + transit (on_order/in_transit_*) + derived (owned/incoming/atp). Status: IMPLEMENTED Fase 0.5.
⚠️ JANGAN pindahkan stok dengan update langsung — selalu buat inventory_movements + rebuild_balance
⚠️ JANGAN BUAT: stock, stok, stock_levels, inventory_count, stock_units, rolls (lepas)
```

### inventory_rolls  [IMPLEMENTED Fase 0.5 — koleksi baru, SSOT fisik]
```
Collection:  inventory_rolls            Prefix: roll_
Router:      routers/inventory.py (atau routers/rolls.py saat coding)
Component:   InventoryStockView.jsx (+ stock-breakdown matrix), SalesPortal (visibilitas)
Status:      DRAFT / PROPOSED (belum ada di DB/kode). Lihat KN_15.
Key Fields:
  id               string   prefix "roll_"  (1 dokumen = 1 roll fisik)
  product_id       string   FK → products.id  (katalog SHARED)
  owner_entity_id  string   FK → business_entities.id  (KEPEMILIKAN — wajib utk internal)
  ownership_type   enum     internal | supplier_consignment | reseller_consignment
                            (DEFAULT internal; konsinyasi DISIAPKAN, default OFF — KN_16 G1)
  consignor_ref    object?  {type: supplier|customer, id, name}  (bila konsinyasi)
  warehouse_id     string   FK → warehouses.id  (LOKASI gudang — netral)
  bin_id           string   lokasi detail (Zone→Rack→[Level]→Bin)
  lot              string   dye-lot (WAJIB) — penentu warna
  batch            string   batch produksi/pembelian
  roll_no          string   nomor/serial roll fisik (label)
  length_initial   float    panjang awal aktual (catch weight)
  length_remaining float    sisa panjang (0 ≤ x ≤ length_initial)
  unit             string   base unit (meter|yard|...)
  grade            enum     A | A+ | B | C
  status           enum     on_order|in_transit_inbound|receiving|quarantine|available|reserved|
                            committed|picked|packed|cross_dock|in_transit_sales|sold|
                            in_transit_transfer|in_transit_intercompany|blocked|damaged|returned|scrapped
  tracking_mode    enum     rfid | barcode | document | manual   (stok visible TANPA RFID — KN_15 §7B)
  earmarked_for    object?  {type: sales_order|special_order, id}  (pegging supply↔demand)
  location_type    enum     warehouse_bin|transit_in|transit_out|cross_dock|drop_ship|transit_transfer
  reserved_ref     object   {type: sales_order|transfer, id}
  unit_cost        float?   HPP per unit (NULLABLE — diisi Fase 4)
  acquired         object   {via: po|transfer|initial|adjustment|return, ref_id, date}
  rfid_tag_id      string?  FK → rfid_tags (Fase 5)
  is_remnant       bool     true bila roll = sisa potongan (BS)
  created_at, updated_at, created_by, created_by_name

⚠️ SSOT fisik stok. inventory_balances = PROYEKSI yang di-rebuild dari sini.
⚠️ Reservasi terjadi di LEVEL ROLL (atomic find_one_and_update status available→reserved).
⚠️ Penjualan owner-scoped: roll hanya boleh dijual entitas pemiliknya (owner_entity_id == SO.entity_id).
⚠️ JANGAN BUAT: stock_units, rolls (lepas), stock — gunakan inventory_rolls (namespace inventory_*).
```

### inventory_movements
```
Collection:  inventory_movements
Router:      routers/inventory.py
Component:   InventoryStockView.jsx (tab Ledger)
Movement Types:
  initial_stock | inbound_receiving | outbound_dispatch |
  transfer_out | transfer_in | cycle_count_adjustment | reservation | release_reservation
  [PROPOSED KN_15] + ownership_transfer_out | ownership_transfer_in (inter-company, owner berubah)
  [PROPOSED KN_15] + remnant_created | quarantine_in | quarantine_out | scrap
Key Fields:
  id, product_id, warehouse_id, movement_type, quantity, unit,
  batch, lot, roll_id, source_document, timestamp
  [PROPOSED KN_15] + owner_entity_id (wajib), roll_id (FK inventory_rolls),
                     from_owner_entity_id & to_owner_entity_id (utk ownership_transfer)

⚠️ APPEND-ONLY — tidak pernah update/delete movement yang sudah ada
⚠️ JANGAN BUAT: stock_history, gerakan_stok, stock_log
```

### system_settings  [Fase 1A IMPLEMENTED — Configuration Foundation]
```
Collection:  system_settings          Prefix: set_
Router:      routers/settings.py       Service: services/config_service.py
Component:   SettingsPanel.jsx (Admin → Pengaturan)
Key Fields:
  id, scope ("global" | entity_id),
  tax       {ppn_rate, ppn_mode(excluded|included), efaktur_enabled, is_pkp(derived)}
  finance   {base_currency, fiscal_year_end_month, default_payment_term_code}
  sales     {quotation_enabled, allow_partial_shipment, allow_order_discount, allow_item_discount}
  inventory {default_uom, min_cut_qty, intercompany_transfer_required}
  created_at, updated_at

⚠️ Effective settings = global di-override per-entitas (config_service.get_effective_settings).
⚠️ SEMUA configurable — JANGAN hardcode PPN/term/currency di kode.
⚠️ JANGAN BUAT: settings, config, configuration (lepas) — gunakan system_settings.
```

### payment_terms  [Fase 1A IMPLEMENTED]
```
Collection:  payment_terms             Prefix: pterm_
Router:      routers/settings.py
Component:   SettingsPanel.jsx (tab Term Pembayaran)
Key Fields:
  id, code (UNIQUE), name, type (cash|credit|dp|installment),
  net_days, dp_percent, installment_count, sort, active, created_at, updated_at

⚠️ JANGAN BUAT: terms, payment_term (singular) — gunakan payment_terms.
```

### approval_rules  [Fase 1A IMPLEMENTED]
```
Collection:  approval_rules            Prefix: aprule_
Router:      routers/settings.py       Service: config_service.evaluate_approval()
Component:   SettingsPanel.jsx (tab Matriks Approval)
Key Fields:
  id, doc_type (sales_order|purchase_order|transfer|discount), entity_id ("all"|entity_id),
  min_amount, max_amount (null = tak terhingga), required_role ("" = tanpa approval),
  is_percent (utk discount), sort, active, created_at, updated_at

⚠️ Matriks CONFIGURABLE menyesuaikan flow. Rule entitas-spesifik diutamakan, fallback "all".
⚠️ JANGAN BUAT: approval_matrix, approvals (lepas) — gunakan approval_rules.
```

### price_approvals  [Sub-fase 1.7 IMPLEMENTED — Special Price / Approval Harga]
```
Collection:  price_approvals           Prefix: pra_
Router:      routers/price_approvals.py
Service:     services/storage_service.py (upload bukti — Emergent Object Storage)
Component:   features/sales/PriceApprovals.jsx
Consumed by: routers/sales_orders.py (get_effective_special_price → override harga item)
Key Fields:
  id, entity_id, customer_id, customer_name, product_id, sku, product_name,
  normal_price (snapshot harga produk), requested_price (harga khusus/unit),
  min_quantity, unit, reason, valid_from, valid_until ("" = tanpa kadaluarsa),
  status (draft|pending|approved|rejected), attachments[] (bukti),
  requested_by, requested_by_name, approved_by, approved_by_name,
  decision_notes, decided_at, created_at, updated_at
Attachment item:
  id (att_), storage_path, original_filename, content_type, size,
  uploaded_by, uploaded_at, is_deleted (soft-delete; storage tak punya delete API)
Status flow:  draft → pending → approved | rejected
RBAC:
  sales   → create/update/delete pengajuan SENDIRI (row-level)
  manager → approve/reject; admin → semua
Konsumsi SO:
  item.price_approval_id valid (approved, berlaku, qty ≥ min_quantity) → price = requested_price.
  INVARIAN tetap: item.subtotal = price × quantity.

⚠️ Special Price = price_approvals (BUKAN koleksi 'special_prices'/'price_lists' lepas).
⚠️ JANGAN BUAT: special_prices, nego_harga, price_overrides — gunakan price_approvals.
```


### wms_tasks
```
Collection:  wms_tasks
Routers:     routers/wms.py (generic CRUD)
             routers/inbound_receiving.py (inbound-specific ops)
             routers/outbound_picking.py (outbound-specific ops)
Schema:      schemas.py → WMSTaskCreate, ScannerScan
Components:  ScannerTaskPanel.jsx (generic)
             InboundScanInterface.jsx (inbound)
             OutboundScanInterface.jsx (outbound)
flow_type:   inbound | outbound
Status Inbound:
  waiting_goods → receiving → qc_check → completed | escalated
Status Outbound:
  created → picking → packing → staging → dispatched | escalated
Key Fields:
  id, flow_type, source_type, product_id, product_name, sku,
  quantity, unit, warehouse_id, bin_id, batch, lot, roll_id,
  status, scanned_items: [{scan_value, scan_type, timestamp, actor}],
  source_document (PO id atau SO id), escalation_info, created_at

⚠️ SATU collection untuk inbound DAN outbound — dibedakan oleh flow_type
⚠️ JANGAN BUAT: inbound_tasks, outbound_tasks, receiving_tasks sebagai collection terpisah
```

### warehouse_transfers
```
Collection:  warehouse_transfers
Router:      routers/transfers.py
Schema:      schemas.py → TransferCreate, TransferApprove, TransferReject
Component:   TransferManagement.jsx
Status Lifecycle:
  draft → waiting_approval → approved → picking → staging → dispatched → received | rejected
Key Fields:
  id, transfer_number, source_warehouse_id, dest_warehouse_id,
  items: [{product_id, product_name, qty, unit, batch, lot, roll_id}],
  status, requested_by, approved_by, notes, created_at, updated_at
  [PROPOSED KN_15] + transfer_kind (intra_entity | inter_entity),
                     source_entity_id, dest_entity_id, transfer_price?, linked_order_id?

⚠️ [PROPOSED KN_15] Inter-company (beda entitas) = EXTEND koleksi ini (transfer_kind=inter_entity),
   BUKAN koleksi baru. Memicu ownership_transfer movement + (Fase 4) AR/AP antar entitas. Lihat KN_15 §7.
⚠️ JANGAN BUAT: transfers, stock_transfer, pemindahan_barang, inter_entity_transfers
```

### cycle_count_sessions
```
Collection:  cycle_count_sessions
Router:      routers/cycle_count.py
Component:   CycleCount.jsx
Status Lifecycle:
  draft → in_progress → submitted → approved | rejected
Key Fields:
  id, session_number, warehouse_id, status,
  items: [{id, product_id, expected_qty, actual_qty, variance, status}],
  submitted_by, approved_by, created_at

⚠️ Approval generate inventory_movements (cycle_count_adjustment)
⚠️ JANGAN BUAT: stock_count, physical_count, stock_opname
```

### purchase_orders
```
Collection:  purchase_orders
Router:      routers/purchase_orders.py
Schema:      schemas.py → PurchaseOrderCreate, POItemCreate, POReceiveItem
Component:   PurchaseOrderManagement.jsx
Status Lifecycle:
  [waiting_approval →] pending → receiving → completed | partial | cancelled
  (waiting_approval hanya jika total_amount memicu approval_rules; lihat Fase 1B)
Key Fields:
  id, po_number (format: PO-NNNNN), supplier_name, supplier_contact,
  warehouse_id, items: [{product_id, quantity, unit, price, subtotal, received_qty}],
  status, expected_delivery_date, notes, created_by, created_at, total_amount
  # Fase 1B — approval dinamis:
  approval_required bool   required_approval_role string|null
  approval_status enum(not_required|pending|approved)   approval_amount float   approved_by string

⚠️ Supplier adalah STRING saat ini — belum ada supplier master collection
⚠️ PO tanpa approval → langsung buat wms_tasks (inbound). PO butuh approval → wms_tasks
   dibuat HANYA setelah /purchase-orders/{id}/approve (role_satisfies dari approval_rules).
⚠️ JANGAN BUAT: po, pembelian, supplier_orders, procurement
```

### document_templates
```
Collection:  document_templates
Router:      routers/documents.py
Schema:      schemas.py → TemplatePayload
Component:   DocumentsView.jsx, AdminView.jsx (tab Templates)
document_type: surat_jalan | invoice
Key Fields:
  id, document_type, name, header, footer, columns, logo_url,
  paper_size, orientation, margin_mm, signature_left, signature_right,
  section_order, status, created_by, created_at

⚠️ JANGAN BUAT: templates, print_templates, doc_config
```

### generated_documents
```
Collection:  generated_documents
Router:      routers/documents.py
Schema:      schemas.py → DocumentGenerate
Key Fields:
  id, document_type, source_id (order_id atau po_id),
  html_content, generated_by, generated_at

⚠️ Dokumen disimpan sebagai HTML string untuk print
```

### permission_settings
```
Collection:  permission_settings
Router:      routers/admin.py
Schema:      schemas.py → PermissionUpdate
Component:   AdminView.jsx (tab Permissions)
Struktur:    {id: "default", matrix: {role: {module: [actions]}}}

⚠️ Hanya ADA 1 document dengan id="default"
⚠️ Fallback: DEFAULT_PERMISSIONS dari permissions_config.py
```

### audit_logs
```
Collection:  audit_logs
Router:      routers/audit.py (read-only list)
Ditulis:     dependencies.py → audit() helper
Component:   AdminView.jsx (tab Audit)
Key Fields:
  id, actor (user name), role, action, entity_type, entity_id,
  before, after, reason, timestamp

⚠️ APPEND-ONLY — tidak pernah update atau delete
⚠️ Gunakan audit() helper dari dependencies.py, BUKAN insert langsung
```

### user_onboarding
```
Collection:  user_onboarding
Router:      routers/onboarding.py
Component:   OnboardingPanel.jsx
Key Fields:
  id (= user_id), tasks: [{id, title, completed, completed_at}]

⚠️ Satu document per user
```

---

<!-- Discovery module (koleksi discovery_sessions/answers/attachments) dihapus 2026-06-17 — fitur assessment online-form. -->



---

## 🚨 FORBIDDEN — NAMA YANG PERNAH MENYEBABKAN DUPLIKAT

Jangan pernah buat collection atau schema dengan nama berikut
(karena sudah ada atau sudah pernah jadi sumber duplikat):

```
❌ items           → gunakan products
❌ goods           → gunakan products
❌ materials       → gunakan products
❌ accessories     → gunakan products
❌ kain            → gunakan products
❌ stock           → gunakan inventory_balances
❌ stok            → gunakan inventory_balances
❌ stock_levels    → gunakan inventory_balances
❌ orders          → gunakan sales_orders
❌ customer_orders → gunakan sales_orders
❌ penjualan       → gunakan sales_orders
❌ inbound_tasks   → gunakan wms_tasks (flow_type=inbound)
❌ outbound_tasks  → gunakan wms_tasks (flow_type=outbound)
❌ receiving_tasks → gunakan wms_tasks (flow_type=inbound)
❌ transfers       → gunakan warehouse_transfers
❌ stock_transfer  → gunakan warehouse_transfers
❌ po              → gunakan purchase_orders
❌ pembelian       → gunakan purchase_orders
❌ bills           → gunakan invoices
❌ tagihan         → gunakan invoices
❌ templates       → gunakan document_templates
❌ staff           → gunakan users
❌ operator        → gunakan users
❌ gudang          → gunakan warehouses
❌ depot           → gunakan warehouses
```

---

## 📐 BASE SCHEMA TEMPLATE

Setiap document baru WAJIB punya field-field ini:
```python
{
    "id":           new_id("prefix"),   # dari core_utils.new_id()
    "created_at":   now_iso(),           # dari core_utils.now_iso()
    "updated_at":   now_iso(),
    "created_by":   user["id"],          # dari token auth
    "created_by_name": user["name"],    # snapshot
    # ... business fields
}
```

Prefix ID yang sudah digunakan:
```
user_   → users
sess_   → sessions
prod_   → products
cust_   → customers
wh_     → warehouses
uom_    → uoms
so_     → sales_orders
bal_    → inventory_balances
roll_   → inventory_rolls            [Fase 0.5 IMPLEMENTED]
mov_    → inventory_movements
wms_    → wms_tasks
trf_    → warehouse_transfers
cc_     → cycle_count_sessions
po_     → purchase_orders
tmpl_   → document_templates
doc_    → generated_documents
inv_    → invoices
audit_  → audit_logs
addr_   → customer addresses (embedded)
ent_    → business_entities         [Fase 0 IMPLEMENTED]
ntf_    → notifications             [Fase 0 IMPLEMENTED]
set_    → system_settings           [Fase 1A IMPLEMENTED]
pterm_  → payment_terms             [Fase 1A IMPLEMENTED]
aprule_ → approval_rules            [Fase 1A IMPLEMENTED]
```
> Prefix PLANNED (lihat bagian PLANNED ENTITIES): `pra_` price_approvals (= "special price"),
> `sord_` special_orders, `bank_` bank_accounts, `cpl_` customer_price_lists, `sret_` sales_returns, `fkt_` tax_invoices.

---

## 🆕 PLANNED ENTITIES (IA KN_14 — belum diimplementasi)

> **Sumber:** `KN_14_INFORMATION_ARCHITECTURE.md`. Entitas berikut **direncanakan**
> per fase roadmap. Didaftarkan di sini lebih dulu (Navigation-First + SSOT) agar
> tidak terjadi duplikat/drift saat coding. Status: **[PLANNED]** — belum ada di DB/kode.
> Saat diimplementasi: pindahkan ke bagian DETAIL di atas + daftarkan ke `verify_contract.py`.

### Lapis Fundamental — Multi-Entity  (✅ IMPLEMENTED Fase 0)
```
Collection: business_entities            Prefix: ent_    Fase 0  [IMPLEMENTED]
  id, legal_name, short_name, type(PT|CV), npwp, address, city,
  default_tax_mode(ppn|non_ppn), doc_prefix, logo_url, status, created_at, updated_at
⚠️ entity_id (FK) ditambahkan ke koleksi TRANSAKSI (scoped): sales_orders, invoices,
   tax_invoices, purchase_orders, cash_transactions, journal_entries, bank_accounts,
   tax_records, fiscal_periods, price_approvals, sales_returns, special_orders.
   Master SHARED (products, warehouses, uoms, document_templates) TIDAK wajib entity_id.
   customers & suppliers = default scoped (opsi shared). JANGAN buat: tenant, company.
```

### Platform  (✅ `notifications` IMPLEMENTED Fase 0)
```
Collection: notifications    Prefix: ntf_    Fase 0  [IMPLEMENTED]
  id, entity_id, recipient_role|recipient_user, type, title, body,
  link(navigation_target), severity(info|warning|critical), ref, read, read_at, created_at
⚠️ JANGAN buat: notif, alerts (gunakan notifications)
```

### Sales (Fase 1)
```
customer_price_lists   Prefix: cpl_   — harga khusus per customer/kategori/produk + periode [DEPRIORITAS: harga manual/nego]
price_approvals        Prefix: pra_   — special price (negosiasi harga + upload bukti + approval Finance/Admin)
sales_returns          Prefix: sret_  — retur/tukar/Barang Sisa (BS) cacat + dampak stok
special_orders         Prefix: sord_  — Special Order (SKU belum ada → MD + Purchasing) + estimasi
tax_invoices           Prefix: fkt_   — Faktur Pajak (nomor, DPP, PPN, status) per entitas
sales_targets          Prefix: starg_ — target sales per salesperson per periode (penjualan/pencairan/customer baru) [KN_17]
sales_incentives       Prefix: sinc_  — komisi/bonus per sales per periode (basis sales|pencairan|tiered) [KN_17]
campaigns              Prefix: camp_  — product focus / campaign + target per sales (advanced) [KN_17]
collection_followups   Prefix: cfu_   — jejak follow-up penagihan jatuh tempo [KN_17 S39]
credit_overrides       Prefix: cro_   — bypass blokir kredit via approval Finance + bukti (case-by-case) [KN_17 S37]
⚠️ KPI salesperson = DERIVED (dari sales_orders/invoices/payments/customers), BUKAN koleksi.
⚠️ JANGAN buat: discounts, faktur, returns_generic, salespersons (pakai users role=sales), leads/crm_* (fase lanjut)
```

### Procurement (Fase 3)
```
suppliers          Prefix: sup_    — master pemasok (nama, npwp, kontak, jenis barang, entity_id?)
bom_printing       Prefix: bom_    — BOM benang + bahan printing per produk/order
cash_transactions  Prefix: cash_   — kas kecil per entitas + kas besar gabungan
⚠️ purchase_orders.supplier_name (string) → refactor jadi FK suppliers.id
⚠️ Approval pembelian = workflow state + attachment pada purchase_orders (bukan koleksi baru)
⚠️ JANGAN buat: vendor, procurement, kas (pakai suppliers/cash_transactions)
```

### Finance (Fase 4)
```
chart_of_accounts  Prefix: coa_    — COA fleksibel (Aktiva/Hutang/Modal/Pendapatan/Beban)
journal_entries    Prefix: je_     — jurnal/GL double-entry (auto-posting dari invoice/kas)
bank_accounts      Prefix: bank_   — rekening per entitas (MULTI-rekening/entitas), entity_id,
                                    bank_name, account_no, account_name, branch,
                                    designation(ppn|non_ppn|both), is_active, is_default
                                    ⚠️ SO + destination_bank_account_id (dipilih saat buat SO; KN_16 §8B.3).
                                       Invoice PPN→akun ppn/both; non-PPN→non_ppn/both.
tax_records        Prefix: tax_    — rekap PPN/PPH (export Coretax = fase lanjut)
fiscal_periods     Prefix: fper_   — periode + closing (28/30/31) + lock
⚠️ AR aging/Outstanding = DERIVED dari invoices + credit_limit; denda 1–3% pada invoices
⚠️ JANGAN buat: ledger, accounts, gl (pakai journal_entries/chart_of_accounts/bank_accounts)
```

### Warehouse & RFID (Fase 5)
```
inventory_classifications Prefix: icls_ — klasifikasi fast/slow/dead (>3 bln) + analitik tren
warehouse_locations   Prefix: loc_  — master lokasi RFID hierarki (Zone→Rack→Level→Bin)
rfid_tags             Prefix: tag_  — registrasi tag ↔ item/lot/roll
rfid_devices          Prefix: dev_  — printer/reader/handheld/gate/server
rfid_events           Prefix: evt_  — log scan/gate (green/red) + alarm → notifications
⚠️ warehouses: tambah level "Level" (Zone→Rack→Level→Bin) — enhancement embedded
⚠️ JANGAN buat: rfid (terlalu generik), locations, tags_generic
```

### HRD (Fase 2)
```
hr_employees       Prefix: emp_    — data karyawan, jabatan, divisi, entity_id
attendance_records Prefix: att_    — absensi (import fingerprint CSV/API), telat, durasi
kpi_records        Prefix: kpi_    — KPI design (jumlah & kualitas desain)
design_gallery     Prefix: dsg_    — gallery motif kain + AI Gemini auto-tag (Emergent LLM key)
⚠️ employees/employee/staff/karyawan = TERLARANG (alias→users di verify_contract.py).
   Domain HRD WAJIB pakai 'hr_employees' (karyawan ≠ user login/auth).
```

---

**Versi:** 1.1  
**Dibuat:** 28 Mei 2026 · **Update IA:** 15 Jun 2026 (planned entities KN_14)  
**Update wajib:** Setiap kali ada entitas baru ditambahkan  
**IA induk:** `KN_14_INFORMATION_ARCHITECTURE.md` (SSOT triangle: KN_14 ⇄ KN_13 ⇄ ENTITY_REGISTRY)
