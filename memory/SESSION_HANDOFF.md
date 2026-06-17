# SESSION HANDOFF
## Kain Nusantara Platform — State Transfer Antar Session

**Format:** Compact, max 2 halaman. Machine-readable. Update di AKHIR setiap session.
**Tujuan:** Agent baru bisa paham state sistem dalam < 5 menit tanpa baca semua docs.

---

## ⚡ QUICK STATE (Update setiap session)

```
Last Updated:    Session #021 (Sub-fase 1.6 — Backorder Lifecycle: opt-in backorder + perbaikan SSOT inbound GR + auto-fulfill)
Last Agent:      Neo (Emergent)
Source Repo:     https://github.com/pandekomangyogaswastika-dot/KN6 → di-copy ke /app (preserve .env)
Backend:         ✅ Running (port 8001) — +allow_partial (roll_service) +allow_backorder (sales_orders) +backorder_service.auto_fulfill; inbound GR kini buat roll (SSOT)
Frontend:        ✅ Running (port 3000) — CartPanel checkbox backorder; OrdersView stat/filter/status waiting_stock; OrderDetailPanel.jsx (split baru)
Database:        test_database @ mongodb://localhost:27017 (DB_NAME di .env; MONGO_URL TIDAK diubah)
Seed Status:     ✅ Re-seeded (seed_realistic.py) — 7 produk, 8 SO, 6 PO, 33 rolls/12 balances.
Gates (Guardrail): ✅ verify_data_integrity 86 PASS/0 FAIL clean-seed (88 pasca-mutasi backorder) — +L4-BO (INV-BO-1/2/3) ·
                 validate_compliance 57 PASS/0 FAIL/0 WARN (PO monster file sudah di-split sesi lalu; OrdersView di-split ke OrderDetailPanel) ·
                 frontend esbuild compile bersih · testing_agent_v3 iteration_9: backend 96% / frontend 100% / integrity 100% (0 bug)
Development:     ✅ Fase 1A/1B · 1.4 · 1.5 · 1.6 DONE.
                 BELUM: Sub-fase 1.7 (allocation policy R1/R2 configurable), mixed-lot confirmation UI, pegging/earmarking, HPP/unit_cost (Fase 4).
```

### Session #021 Notes (Sub-fase 1.6 — Backorder Lifecycle)
- Konteks: lanjut dari env existing; baseline diverifikasi HIJAU (compliance 57/0/0, integrity 85→86 setelah L4-BO ditambah). User setuju: opt-in backorder, perbaiki inbound GR (latent SSOT bug), mulai 1.6.1.
- **Temuan kritis & perbaikan:** `inbound_receiving.complete_inbound_receiving` SEBELUMNYA `$inc` langsung ke `inventory_balances` tanpa membuat roll → melanggar invarian Roll-as-SSOT (balance==Σrolls). Kini membuat `inventory_rolls` + `rebuild_balance` → invarian terjaga (terbukti 88 PASS pasca-GR).
- **Backend:** `roll_service.allocate_and_reserve_rolls(allow_partial)`; `sales_orders.create_order(allow_backorder)` + status `waiting_stock` + `backorders[]`; `services/backorder_service.auto_fulfill_backorders()` (FIFO, owner-scoped) dipanggil dari GR complete; cancel/release/expire menangani waiting_stock.
- **Invarian baru:** `verify_data_integrity.py` layer L4-BO (INV-BO-1 qty==reserved+backorder; INV-BO-2 status waiting_stock⟺Σbackorder>0; INV-BO-3 owner-scoped).
- **Frontend:** CartPanel `allow-backorder-checkbox` + `backorder-option-card`; OrdersView `orders-stat-backorder` + filter waiting_stock; `OrderDetailPanel.jsx` (di-split agar OrdersView<500 baris) banner `order-backorder-panel` + breakdown `order-item-backorder-{pid}`; `useAppActions.submitOrder` kirim `allow_backorder`.
- **Files:** backend roll_service.py, sales_orders.py, inbound_receiving.py, inventory_service.py, schemas.py, services/backorder_service.py (BARU); scripts/verify_data_integrity.py; frontend CartPanel.jsx, OrdersView.jsx, OrderDetailPanel.jsx (BARU), hooks/useAppActions.js, styles/components.css; tests/test_backorder_16.py (BARU); memory/test_credentials.md (diisi).
- GOTCHA: GR auto-fulfill memakai `PO.entity_id` sebagai owner roll; PO received_qty kini `$inc` (akumulatif). Backorder owner-scoped — auto-fulfill hanya untuk SO entitas yang sama (jaga D3).
- NEXT: Sub-fase 1.7 (allocation policy R1/R2 configurable). Butuh konfirmasi user.

### Session #021b Notes (Sub-fase 1.6.1 — Decouple Status & Approval-with-Backorder)
- Keputusan user: (1a) kerjakan sekarang · (2c) approval lanjut sekarang, shipment parsial fisik MENYUSUL · (3a) pisahkan `status` dari flag `has_backorder` · (4a) auto-commit ikut approval awal · (5a) hormati `shipment_policy`.
- **Backend:** `create_order` status `reserved` bila ada porsi reserved (walau backorder); `waiting_stock` hanya bila 0 reserved (pure backorder). `auto_fulfill_backorders` kini target SEMUA SO `has_backorder` lintas status; bila approved/confirmed → `set_order_rolls_status(committed)` (auto-commit, tanpa approval ulang); `waiting_stock`→`reserved` saat mulai ada reserved; status lain tak diubah. `_norm_backorder()` di GET sales-orders memastikan respons selalu punya `has_backorder`/`backorders` (fix contract drift order lama).
- **Invariant L4-BO direvisi:** `has_backorder ⟺ Σbackorder>0`; `waiting_stock ⟹ Σreserved≈0`.
- **Frontend:** stat Backorder dihitung dari `has_backorder` (lintas status); chip "Backorder" di list (`order-backorder-chip-{id}`) + header detail (`order-backorder-chip`).
- **Verifikasi:** testing_agent_v3 iteration_10 — BE 100% (14/14) · FE 100% · integrity 100% (88/0) · contract 100%. Self-test `tests/test_backorder_approval_161.py` 9/9. Semua gate seed_reset LULUS.
- GOTCHA: gate `verify_api_contract.py` (CHECK C) menolak FE membaca field yang tidak ada di respons BE untuk data lama — selalu pastikan field baru dinormalisasi di respons GET (`_norm_backorder`).
- **MENYUSUL:** pengiriman parsial FISIK terhadap backorder (Surat Jalan porsi reserved + multi-shipment) — belum, butuh konfirmasi user. NEXT utama: Sub-fase 1.7.

### Session #020 Notes (Sub-fase 1.5 — Inter-Company Transfer Flow)
- Konteks: import repo KN6 ke env baru → rsync preserve .env → install deps (reportlab, openpyxl) → yarn install → seed_realistic → gates HIJAU baseline.
- Review & mapping: dibaca KN_00, KN_01, PRD.md, plan.md, SESSION_HANDOFF.md, ENGINEERING_GUARDRAILS.md, ENTITY_REGISTRY.md, CODEBASE_MAP.md, KN_14–KN_16, iteration_8.json. Temuan: Sub-fase 1.5 SUDAH DIIMPLEMENTASIKAN di repo KN6 tapi dokumen belum di-update.
- Sub-fase 1.5 yang sudah ada di kode (terverifikasi):
  - Backend: `routers/transfers.py` — `POST /api/transfers/inter-company` (buat transfer_kind inter_entity, roll-reserve sumber); `POST /api/transfers/{id}/approve` (pindah kepemilikan B→E, rebuild_balance, status completed); `POST /api/transfers/{id}/reject` (lepas reservasi, status rejected); `DELETE /api/transfers/{id}` (cancel + lepas reservasi).
  - Frontend: `features/transfers/InterCompanyTransfers.jsx` (265 baris) — list + approve + reject; `SalesPortal.jsx handleRequestTransfer` → call POST inter-company; `CartPanel.jsx` — tombol "Minta Transfer dari {entity}" + badge "diminta"; `navigationConfig.js` route `interco-transfers`; `App.js` render.
- Test coverage sub-fase 1.5: `test_reports/iteration_8.json` — backend **36/36 (100%)**, frontend code review 100%. Skenario: KSC→Kanda + ownership movement + stock conservation + preview mode changes.
- Tindakan session ini: rsync repo, install deps, seed, verifikasi gates baseline, baca semua docs, verifikasi implementasi sub-fase 1.5, **update dokumentasi** (plan.md + SESSION_HANDOFF.md).
- Gates verifikasi session ini: verify_contract OK · data_integrity **85/0/0** · validate_compliance **56/0/2 WARN** (pre-existing PurchaseOrderManagement warning) · health_check **22 PASS/0 FAIL** (3 WARN info normal) · audit_endpoint_sweep **0×5xx**.
- GOTCHA #13 (BARU): Inter-company transfer flow SUDAH MUTASI (bukan informasional). create_order TETAP owner-scoped (409 bila stok sendiri kurang); inter-company transfer TERPISAH dari create_order — user harus klik "Minta Transfer" di CartPanel DULU, tunggu approval, baru buat SO setelah stok dialihkan. Ini by design (S3 KN_15 §7).
- LANGKAH BERIKUT (kandidat sub-fase berikutnya): backorder lifecycle (status waiting_stock + auto-fulfill saat GR), allocation policy R1/R2 configurable, mixed-lot confirmation UI. Butuh konfirmasi user.


- Konteks awal: user salah copy repo (DA48) → dikoreksi ke **KN6**. Repo di-rsync ke /app (preserve .env/node_modules), +reportlab 4.5.1/openpyxl 3.1.5, seed_realistic, baseline gate diverifikasi hijau SEBELUM coding. Catatan: konteks "Sub-fase 1.4 / preview-allocation / Inventory Status Board" yang dilaporkan agent sebelumnya TERBUKTI nyata di KN6 (roll_service, CartPanel, KN_16) — bukan halusinasi.
- Governance: I1–I6 (KN_16) sudah RESOLVED (S#016) → coding Fase 1 Sales UNBLOCKED. Pilihan user: (1) selesaikan penuh; (2.c) ATP ikut logika existing (available+incoming); (3.b) board termasuk indikator inter-company; (4.a) ikut pola UI POS.
- Backend (ADDITIVE, READ-ONLY — tidak mengubah engine reservasi):
  - `services/fulfillment_service.py` (BARU): `build_supply_index` (gabung inventory_balances available/reserved/on_hand/in_transit_inbound + open-PO on_order=qty−received) → `classify_lines` (waterfall: from_stock→from_incoming→inter_company→backorder, severity-based primary_mode) + `status_board` (per produk × entitas × gudang + indikator inter-company). ATP = available + incoming.
  - `routers/sales_orders.py`: +`POST /api/sales-orders/preview-allocation` (require order:view, READ-ONLY). `schemas.py`: +`AllocationPreviewIn`.
  - `routers/inventory.py`: +`GET /api/inventory/status-board?product_id&owner_entity_id` (require product:view).
  - Penting: ATP `incoming` dihitung dari OPEN_PO_STATUSES = {waiting_approval, pending, created, approved, sent, receiving} − received_qty. Ini melengkapi roll_service.rebuild_balance yang sebelumnya 0 (status 'receiving' tak terhitung). balance.incoming_qty TIDAK diubah (gate-safe); ATP feature dihitung fresh di service (konsisten internal).
- Frontend (ikut pola UI existing):
  - `components/CartPanel.jsx`: +`FulfillmentInfo` (badge mode + ATP/Stok/Incoming/Inter-Co + backorder + penjelasan) per item. `features/sales/SalesPortal.jsx`: fetch preview-allocation (debounce 350ms) saat cart/entitas/customer berubah; entity = selectedEntity (atau customer.entity_id). `utils/fulfillment.js`: SSOT meta mode. `styles/components.css`: +pill `.fmode-*`.
  - `features/inventory/InventoryStatusBoard.jsx` (BARU): tabel per produk (on_hand/available/reserved/incoming/ATP) + expand per entitas & gudang + metrik ringkas + search + refresh. `App.js` + `navigationConfig.js`: menu "Status Stok" (id `inventory-board`, allowlist sales/manager/warehouse + admin).
- Verifikasi: POC `tests/poc_atp_fulfillment.py` 5/5 (4 mode + ATP konsistensi). testing_agent: **backend 21/21 (100%)**, **frontend 17/18 (95%)** — 1 isu LOW = selector entity switcher salah (BUKAN bug; diverifikasi manual mode inter_company tampil "Antar-Entitas" saat entitas Kanda). Gate: data_integrity 85/0, health 22/0, api_contract 0 err, sweep 0×5xx, ux_audit 0 ERROR.
- GOTCHA #12 (BARU): preview-allocation & status-board READ-ONLY (klasifikasi/visibilitas saja). create_order TETAP owner-scoped & masih 409 bila stok sendiri kurang (inter-company/backorder belum jadi flow MUTASI). Mode 'inter_company'/'backorder' baru INFORMASIONAL di POS — eksekusinya butuh sub-fase berikut.
- LANGKAH BERIKUT (kandidat sub-fase 1.5+): inter-company TRANSFER FLOW nyata (buat transfer antar-entitas dari preview), backorder lifecycle (status waiting_stock + auto-fulfill saat GR), allocation policy R1/R2 configurable, mixed-lot confirmation UI. Butuh konfirmasi user untuk perubahan yang MEMUTASI stok/membuat dokumen transfer.

### Session #018 Notes (Fase 1B — Configuration Consumption)
- Konteks: Fase 1A (config foundation) sudah ada tapi engine (compute_tax/evaluate_approval/effective_settings) BELUM dikonsumsi alur nyata. Session ini menyambungkannya.
- Backend:
  - `services/config_service.py`: +`compute_order_pricing()` (diskon item/order + PPN, INVARIAN-SAFE: subtotal & total_amount tetap GROSS), +`role_satisfies()` (hirarki role utk approval dinamis).
  - `schemas.py`: SalesOrderItemIn +`discount_percent`; SalesOrderCreate +`order_discount_percent`,+`payment_term_code`; PaymentSimulationCreate.amount → opsional.
  - `routers/sales_orders.py`: create_order pakai compute_order_pricing + simpan breakdown PPN/diskon + term + approval meta. submit-for-approval = evaluasi matriks (auto-approve bila di bawah threshold, else waiting_approval). approve = role_satisfies (dinamis, ganti role hardcode). list_orders +safe_doc (defensif).
  - `routers/invoices.py`: simulate-payment pakai grand_total order + snapshot pajak di invoice. FIX BUG: `insert_one(dict(invoice))` agar ObjectId tak ter-embed di order.payments (RC: latent ObjectId serialize 500).
  - `routers/purchase_orders.py`: PO create evaluasi approval; bila perlu → status waiting_approval & wms_tasks DITUNDA; +`/purchase-orders/{id}/approve` (role_satisfies) lalu buat inbound tasks. Helper `_create_inbound_tasks_for_po`.
  - `services/inventory_service.py`: render_order_html +blok ringkasan pajak (Subtotal/Diskon/DPP/PPN/Grand Total + Term) utk dokumen invoice.
- Frontend: utils/pricing.js (preview client = cermin backend); CartPanel (diskon per-item & order, pilih term, ringkasan PPN live); OrdersView (breakdown harga, badge approval, tombol Submit-for-Approval/Approve/Confirm dinamis, Invoice PPN); PurchaseOrderManagement (badge + tombol Approve PO, status waiting_approval); useAppActions (load settings+payment_terms, submitOrder kirim diskon+term, approvePurchaseOrder); App.js threading.
- Gate baru: verify_data_integrity INV-DB3 (net_subtotal==total−diskon; PPN==dpp×rate; grand==net+ppn; line_total==subtotal−diskon; 0≤disc%≤100). Seed `backfill_order_pricing()` agar 8 SO seed konsisten (PPN ikut PKP entitas) + approval meta → 0 FE↔BE drift.
- Verifikasi: curl E2E (order diskon 10%+5% → grand 1.755.742,5; PKP vs non-PKP; approval SO sales→403/manager→approved; small→auto-approve; PO 129jt→waiting→approve→tasks; invoice grand_total). Gate semua hijau (86/0/0). Screenshot POS: grand total client == backend.
- Tech-debt: PurchaseOrderManagement.jsx 455 baris (90% limit) — kandidat split. native select payment-term (+1 W2 warn, konsisten baseline).
- Status: Fase 1B DONE. Backlog Critical PRD #2 (diskon) & #3 (PPN 11%) selesai. MENUNGGU ARAHAN USER.

### Session #017 Notes (RE-IMPORT KN6 ke env baru + Setup + Review/Mapping)
- Sumber repo: https://github.com/pandekomangyogaswastika-dot/KN6 → di-copy ke /app via rsync (exclude: .git, .env, node_modules, __pycache__, *.pyc, build, .emergent). MONGO_URL & REACT_APP_BACKEND_URL TIDAK diubah; DB_NAME=test_database, CORS_ORIGINS=*. .env di-backup ke /tmp sebelum rsync & diverifikasi utuh setelahnya.
- Dependency: +reportlab 4.5.1 +openpyxl 3.1.5 (di-install ke venv; sudah tercantum di requirements.txt). Frontend `yarn install` OK (52s, hanya peer-dep warnings). litellm wheel di requirements TIDAK dipakai app → di-skip.
- Dibaca: KN_00, KN_01, README, docs/README, PRD, plan.md, CODEBASE_MAP, ENTITY_REGISTRY, ENGINEERING_GUARDRAILS, SESSION_HANDOFF, server.py, requirements.txt, package.json, LoginScreen.jsx, navigationConfig testids.
- Verified: import server.py bersih (148 routes), health "Kain Nusantara API aktif", openapi 115 API paths, login admin OK (Bearer sess_ token).
- Seed realistic OK: 5 user, 7 produk, 5 customer, 3 gudang, 6 PO, 8 SO, 10 inbound + 8 outbound task, 12 balances, 19 movements, 33 rolls (12 segmen), config defaults (settings 1/payment_terms 6/approval_rules 7), 6 audit, 2 entities, 1 notif.
- GATES HIJAU: verify_contract OK · validate_compliance **57/0/0** · verify_data_integrity **82/0/0** (+L4-ROLL, +config) · verify_api_contract 0 ERROR/0 WARN (148 route unik · 33 FE path cocok · field-check OrdersView/InventoryStockView) · health_check 21 PASS/0 FAIL (3 WARN info) · audit_endpoint_sweep 0×5xx (422 settings compute-tax/evaluate-approval + 404 transfer not-found = expected) · ux_audit 0 ERROR/20 WARN (W2 native select baseline) · find_dead_services 9/9 used.
- ADVISORY (non-blocking): check_nav_map 27 issue — validator masih cari data-testid statik padahal nav dibangun dinamis via config/navigationConfig.js (sama seperti #015, perlu update validator, bukan bug app). audit_collection_drift "MISSING" = koleksi kosong (mis. warehouse_transfers belum ada record di seed), normal.
- Screenshot + DOM assert verified: Login "Kain Nusantara Control Center" detach setelah login; Admin dashboard KPI **produk 7 · available 3.055 · reserved 220 · active_orders 8 · gudang 3** (cocok invarian gate). Entity Switcher "Semua Entitas" + Notification badge (1) + 8 menu sidebar + tab Admin (Entities/Product/Customer/Warehouse/UOM/Pengaturan/Templates/Permissions/Audit/Users) tampil. 7 produk ter-list.
- Catatan state: KN6 sudah mengandung **Fase 0 (Multi-Entity + Notifications)**, **Fase 0.5 (Roll-as-SSOT Inventory Ownership)**, dan **Fase 1A (Configuration Foundation: system_settings/payment_terms/approval_rules + SettingsPanel)** — semua IMPLEMENTED & gate hijau.
- Status: baseline KN6 stabil & ter-mapping di env baru. **NO CODING** (review & mapping dulu sesuai permintaan). MENUNGGU ARAHAN USER untuk fitur/fase berikutnya.

### Session #016 Notes (RE-IMPORT KN6 ke env baru + Setup + Review/Mapping)
- Sumber repo: https://github.com/pandekomangyogaswastika-dot/KN6 → di-copy ke /app via rsync (exclude: .git, .env, node_modules, __pycache__, build, .emergent). MONGO_URL & REACT_APP_BACKEND_URL TIDAK diubah; DB_NAME=test_database, CORS_ORIGINS=*.
- Dependency: backend core deps SUDAH ADA di base image; +reportlab 4.5.1 +openpyxl 3.1.5 (di-install untuk discovery PDF/export). `litellm` di requirements.txt KONFLIK (ResolutionImpossible) tapi TIDAK dipakai app → di-skip. Frontend `yarn install` OK (51s, hanya peer-dep warnings).
- Dibaca: KN_00, KN_01, README, docs/README, PRD, SESSION_HANDOFF, CODEBASE_MAP, ENTITY_REGISTRY, plan.md, server.py, db.py, requirements.txt, package.json.
- Verified: backend health "Kain Nusantara API aktif", 106 API paths (openapi), login admin OK (Bearer sess_ token), import server.py bersih.
- Seed realistic OK (seed_realistic.py): 5 user, 7 produk, 5 customer, 3 gudang, 6 PO, 8 SO, 10 inbound + 8 outbound task, 12 balances, 19 movements, 6→11 audit, 2 entities, 1 notif. DB live = 16 collection.
- GATES HIJAU: verify_contract OK · verify_data_integrity 64/0/0 · health_check 21 PASS/0 FAIL (3 WARN info) · audit_endpoint_sweep 0×5xx (400/404 expected: doc POST tanpa data + transfer not-found) · verify_api_contract 0 ERROR/0 WARN (31 FE path cocok) · ux_audit 0 ERROR/20 WARN (W2 native select baseline) · validate_compliance 56/0/0.
- Screenshot verified: Login "Kain Nusantara Control Center" + Admin dashboard (KPI: produk 7, available 3.055, reserved 220, active_orders 8, gudang 3) cocok dengan invarian gate. Entity Switcher "Semua Entitas" + Notification badge (1) tampil.
- Status: baseline KN6 stabil & ter-mapping di env baru.

**ADDENDUM Session #016 — FASE 0.5 ENABLER (Roll-as-SSOT) DIIMPLEMENTASIKAN (user approve "ya fase 0.5"):**
- Baru: `backend/services/roll_service.py` (rebuild_balance, generate_rolls_from_balances [idempotent §11], allocate_and_reserve_rolls [owner-scoped+FEFO+split], release_order_rolls, set_order_rolls_status).
- `inventory_rolls` (prefix roll_) = SSOT fisik; `inventory_balances` = proyeksi 3-key (product+warehouse+owner_entity_id) + bucket detail. Reservasi SO pindah ke LEVEL ROLL & owner-scoped (D3). approve→committed, cancel/release→available.
- Endpoint baru/ubah: GET /api/inventory/rolls; balances owner-aware; POST initial-stock→buat roll (RollPayload); products stock-breakdown +ownership_matrix +rolls.
- FE: WMS Stok kolom Pemilik + banner; tab Rolls (RollsTable.jsx); InitialStockForm +Pemilik/Lot/Grade; ProductDetail Ownership Matrix; filter owner via Entity Switcher (axios params, bukan string concat — supaya verify_api_contract lolos).
- Seed: server.py lifespan +backfill_inventory_owner +ensure_inventory_rolls; seed_realistic.py clear+generate (33 rolls / 12 segmen). available 3055 / reserved 220 / on_hand 3275 TERJAGA.
- Gates: data_integrity **72/0/0** (+L4-ROLL), verify_contract OK (inventory_rolls kanonik), compliance PASS, FE↔BE OK, ux_audit 0 ERROR. POC tests/poc_roll_reservation.py **18/18**. testing_agent: backend 19/20 (1 "bug" = /api/dashboard/summary 404 → SALAH EKSPEKTASI, endpoint benar /api/dashboard); FE diverifikasi via screenshot (owner col, Rolls tab, Ownership Matrix).
- ENTITY_REGISTRY + plan.md di-update (PROPOSED→IMPLEMENTED).
- GOTCHA #11 (BARU): JANGAN update stok via $inc langsung. Mutasi roll (status/length) → SELALU panggil roll_service.rebuild_balance(product,warehouse,owner). Reservasi/lepas SO via allocate_and_reserve_rolls/release_order_rolls (owner = SO.entity_id). balances = proyeksi, BUKAN sumber kebenaran.
- LANGKAH BERIKUT (Fase 1 Sales): butuh jawaban Info-Needed I1–I6 (KN_16) untuk inter-company transfer flow, allocation policy configurable, mixed-lot UI, ATP. NO CODING Fase 1 sebelum I1–I6 dijawab.

### Session #015 Notes (RE-IMPORT KN5 ke env baru + Setup + Review/Mapping)
- Sumber repo: https://github.com/pandekomangyogaswastika-dot/KN5 → di-copy ke /app via rsync --delete (preserve: .git, .env, node_modules, __pycache__). MONGO_URL & REACT_APP_BACKEND_URL TIDAK diubah; DB_NAME=test_database, CORS_ORIGINS=*.
- Dependency: backend +reportlab 4.5.1 +openpyxl 3.1.5 (di-install ke /root/.venv; sudah ada di requirements.txt). Frontend `yarn install` OK (warnings peer-dep normal). litellm/emergentintegrations TIDAK dipakai app.
- Dibaca: KN_00, KN_01, README, docs/README, PRD, CODEBASE_MAP, ENTITY_REGISTRY, plan.md, SESSION_HANDOFF, server.py, db.py.
- Verified: backend health "Kain Nusantara API aktif", 106 API paths (openapi), login admin OK (Bearer sess_ token), /auth/me OK.
- Seed realistic OK (seed_realistic.py): 5 user, 7 produk, 5 customer, 3 gudang, 6 PO, 8 SO, 10 inbound + 8 outbound task, 12 balances, 19 movements, 6→12 audit, 2 entities, 1 notif. DB live = 16 collection.
- GATES HIJAU: verify_contract OK · verify_data_integrity 64/0/0 · health_check 21 PASS/0 FAIL (3 WARN info) · audit_endpoint_sweep 0×5xx (39 OK / 5 EMPTY / 9 4xx auth) · verify_api_contract 0 ERROR/0 WARN · ux_audit 0 ERROR/20 WARN · validate_compliance 56/0/0.
- ADVISORY (non-blocking): check_nav_map 27 issue — validator masih cari data-testid statik (nav-home/nav-pos/wms-tab-*) padahal nav kini dibangun dinamis via config/navigationConfig.js. Perlu update validator (bukan bug app).
- Screenshot verified: Login "Kain Nusantara Control Center" + Admin dashboard (KPI: produk 7, available 3055, reserved 220, active_orders 8, gudang 3) cocok dengan invarian gate. Entity Switcher "Semua Entitas" + Notification badge (1) tampil.
- Status: baseline KN5 stabil & ter-mapping di env baru. NO CODING (sesuai permintaan: review & mapping dulu). MENUNGGU ARAHAN USER untuk fitur/fase berikutnya.
- 🧩 **Keputusan arsitektur (Session #015) — Multi-Entity Inventory Ownership (Roll-as-SSOT):** user setuju kepemilikan stok per-entitas di **level roll** (gudang netral), Opsi 2 (roll-as-SSOT penuh), inter-company transfer WAJIB, HPP nanti Fase 4. Tambahan: visibilitas Sales (gudang+owner+lot), integritas lot (single vs mixed bila qty>lot tunggal), flow shortage→transfer dipermudah. **Dokumen baru `docs/KN_15_INVENTORY_OWNERSHIP_LOT.md`** (deep dive + 28 edge case + sub-decision S1–S8). Sinkron: KN_14 (§6.1/§7/§9.1/§13/§14), ENTITY_REGISTRY (inventory_rolls + revisi balances/movements/transfers + prefix roll_), TECH_DECISIONS (ADR-008), plan.md (Fase 0.5). Status DRAFT — **NO CODING**, sub-decision S1–S8 menunggu konfirmasi sebelum lock final.
- 🧩 **Lanjutan keputusan (Session #015):** S1–S16 RESOLVED — allocation policy CONFIGURABLE+CLARITY, mixed-lot=Sales, ownership pindah saat approval/dispatch, extend warehouse_transfers + split roll, status waiting_intercompany, managing_entity_id Fase 4, **taksonomi inventory detail** (bucket fisik+transit+pipeline+derived; in_transit_inbound/sales/transfer/intercompany; cross_dock/drop_ship), ATP configurable, committed dipisah, retur manual, **mode sumber/pemenuhan** (from_stock/from_incoming/buy_to_order/special_order/cross_dock/drop_ship/inter_company), **tracking multi-modal** (rfid|barcode|document|manual → stok visible TANPA RFID), cross-dock no-scan, drop-ship SJ oleh kita, buy-to-order batal→fallback stok. **Dokumen baru `docs/KN_16_END_TO_END_PROCESS_FLOWS.md`** (flow Sales/Procurement/WMS-RFID + Blindspot Register G1–G25 + Info-Needed Register I1–I15). KN_15 kini v1.3. **NO CODING.** Menunggu user menjawab Info-Needed (I1–I6 fondasional) sebelum lock final & mulai Fase 0.5.

### Session #014 Notes (Import KN5 + Setup + Review/Mapping)
- Sumber repo: https://github.com/pandekomangyogaswastika-dot/KN5 → di-copy ke /app (preserve .env: MONGO_URL & REACT_APP_BACKEND_URL TIDAK diubah; DB_NAME=test_database).
- Dependency: backend +reportlab 4.5.1 +openpyxl 3.1.5 (di-install; requirements.txt di-sync). Frontend yarn install OK.
- Dibaca: KN_00, KN_01, KN_13, PRD, CODEBASE_MAP, ENTITY_REGISTRY, plan.md, SESSION_HANDOFF, CLEANUP_ANALYSIS, FRONTEND_MENU_ANALYSIS, ENGINEERING_GUARDRAILS.
- Verified: backend health "Kain Nusantara API aktif", 99 API paths, login admin OK (Bearer sess_ token).
- Seed realistic OK. GATES HIJAU: seed_reset (contract+api_contract+integrity 64/0/0), health_check 21/0, endpoint_sweep 0×5xx, ux_audit 0 ERROR/19 WARN, validate_compliance 54/0/0.
- Screenshot verified: login + Admin dashboard (KPI: produk 7, available 3055, reserved 220, active_orders 8, gudang 3) cocok dengan invarian gate.
- IA BLUEPRINT dibuat (atas arahan user "fokus IA dulu"): `docs/KN_14_INFORMATION_ARCHITECTURE.md` (4-lapis IA, 8 domain, target grouped-nav 6 fase, ER target + multi-entity layer, tax/notif, prefix ID & nama terlarang, governance) + update `KN_13` (Target Grouped Navigation IA) + `ENTITY_REGISTRY` (Planned Entities per fase). NO CODING.
- Validasi guardrail temuan: `employees` = alias TERLARANG→users → koleksi HRD pakai `hr_employees`; `stock_classifications`→`inventory_classifications` (konsisten namespace). Semua nama planned divalidasi vs verify_contract.py (contract OK).
- Status: baseline KN5 stabil & ter-mapping; IA blueprint v1 selesai.
- ✅ FASE 0 (Enabler) IMPLEMENTED & TESTED: Multi-Entity (business_entities ent_ksc/ent_kanda + entity_id scoped di sales_orders/invoices/purchase_orders/customers; master products/warehouses/uoms SHARED) + Entity Switcher (TopBar global, persist localStorage) + Notification Center (notifications, generator REAL: low_stock/reservation_expiring/order_approval/order_split, dedupe by ref) + field master (customer npwp/credit_limit/sales_pic, product harga_pokok/gramasi) + Admin "Entities" tab.
- Gates HIJAU pasca Fase 0: contract+api_contract+integrity 64/0/0, compliance 56/0/0, ux 0 ERROR, sweep 0×5xx. testing_agent: backend 39/39, frontend 100%, 0 bug.
- File baru: backend routers/entities.py, routers/notifications.py, services/notification_service.py; frontend components/EntitySwitcher.jsx, components/NotificationCenter.jsx, styles/fase0.css. Gate scripts diupdate (registrasi koleksi). NB: /app/backend_test_fase0.py = artefak test (boleh dipindah ke tests/).
- NEXT: Fase 1 (Sales) atau lanjut sesuai arahan user.

### Session #009 Notes (Import & Mapping)
- Sumber repo: https://github.com/pandekomangyogaswastika-dot/KN3 → di-copy ke /app (preserve .env).
- Dibaca: KN_00–KN_13, PRD, SESSION_HANDOFF, CODEBASE_MAP, ENTITY_REGISTRY, plan.md.
- Inkonsistensi doc ditemukan: PRD.md tulis "JWT + Bcrypt", padahal implementasi nyata =
  Bearer session token (sess_) + SHA256 hash_password (lihat ENTITY_REGISTRY/handoff). Actual code menang.
- Verified working: login (admin/sales/manager/warehouse), dashboard, master data, Discovery 14 domain.

### Session #010 Notes (EXECUTABLE GUARDRAILS — adaptasi torado60 → KN3)
Tujuan user: jadikan guardrails torado60 sebagai STANDAR PROSES executable untuk KN3,
gabung jadi satu fondasi, kembangkan lebih jauh (cegah blindspot/bug/techdebt).

**Gate executable baru (di /app/scripts/, semua bisa GAGAL exit≠0 — sudah diuji FAIL & PASS):**
- verify_contract.py        — nama koleksi kanonik vs TERLARANG; deteksi db.x DAN db["x"].
- verify_data_integrity.py  — Concept registry + invarian lintas-endpoint (di DB clean-seed).
- health_check.py           — sweep endpoint kritis (cek ISI).  → 21 PASS / 0 FAIL.
- audit_endpoint_sweep.py   — sweep SEMUA 49 GET /api.          → 0 5xx (setelah fix).
- ux_audit.py               — baseline UX executable (--strict).→ 15 ERROR/20 WARN = backlog.
- audit_collection_drift.py, find_dead_services.py, seed_reset.sh ([GATE] otomatis).

**Dokumen baru/diupdate:**
- memory/ENGINEERING_GUARDRAILS.md (RC-1..RC-15 + checklist 3-gate + DoD + eskalasi).
- docs/UX_USABILITY_STANDARD.md (developed further; di-enforce ux_audit.py).
- docs/KN_00 + scripts/README.md (rujukan gate). ENTITY_REGISTRY diperbaiki (number/price/allocations).

**BUG NYATA ditemukan gate & DIPERBAIKI (bukti gate bekerja):**
1. RC-2: seed_realistic.py pakai field `qty` (bukan `quantity`) di items+allocations SO
   → OrdersView blank qty + total_reserved_qty stats salah. FIX: "qty"→"quantity" (28 occ).
2. RC-6 + render rapuh: render_order_html 500 (KeyError 'warehouse_city' + akses key langsung)
   → /api/documents/preview & surat-jalan crash. FIX: render defensif (.get + fallback, guard customer None).
   Verified: preview so_001/so_007 → HTTP 200; sweep 0 5xx.

Status: SEMUA gate hijau (contract 0, integrity 60/0, health 0 fail, sweep 0 5xx). DB clean-seed.
Next: lanjut development fitur KN3 DENGAN menjalankan gate ini tiap akhir task (MENUNGGU ARAHAN fitur).

### Session #011 Notes (DEEP-DIVE round 2 — sempurnakan guardrails, tutup celah)
User minta deep-dive lebih dalam + sempurnakan guardrails karena masih ada celah → bug.
Metode: AUDIT guardrail v1 sendiri (meniru B1-B8 case-study) → temukan 9 celah (G1-G9).

**Gate BARU + enhancement:**
- `verify_api_contract.py` (NEW): Check A duplicate-route, Check B FE-call→route-exist,
  Check C FE-field⊆BE-response. Sempat false-positive (dua makna `${API}`, method fetch di
  arg-opsi, `${params}`) → DIPERBAIKI agar akurat (gate berisik = diabaikan).
- `verify_data_integrity.py` +L0 self-check (gate vs ENTITY_REGISTRY), +L5 number-series,
  +INV-5 active_orders, fix G5 WARN-swallow (exception invarian → FAIL bukan WARN).
- `seed_reset.sh` kini 4 gate (tambah api_contract).

**BUG NYATA round-2 ditemukan & DIPERBAIKI (yang LOLOS dari gate v1):**
1. G2: duplicate `GET /sales-orders` → filter status/customer_id MATI. FIX: hapus duplikat.
2. G9/RC-7: dashboard active_orders dihitung dari window 20 order. FIX: count_documents penuh.
3. G7/RC-6: barcode label & render order pakai akses key langsung → 500. FIX: defensif .get().
4. G1: OrdersView baca shipping_city/sales_name/reservation_expires_at/item.id yang BE tak
   produksi → label kosong/"Invalid Date". FIX: seed backfill + create_order snapshot + FE resilient.
5. G4: discovery_attachments tak ada di ENTITY_REGISTRY → ditambahkan (L0 yang menemukan).
6. G8/RC-5: penomoran count-based (rentan). Dibuat VISIBLE via L5 (deteksi duplikat nomor).

**Status round-2:** seed_reset.sh 4 gate LULUS exit 0 (integrity PASS 64/0, api_contract 0 ERROR,
contract 0, sweep 0 5xx). FE order detail terverifikasi (kota+sales tampil, no Invalid Date).
Semua gate baru DIBUKTIKAN bisa FAIL saat disuntik (L0 discovery_attachments, L5 duplikat nomor,
Check A duplicate route, Check C field drift).

---

## 📁 FILE YANG DISENTUH SESSION INI

```
[COPIED FROM REPO]
backend/
  server.py, db.py, core_utils.py, schemas.py,
  dependencies.py, permissions_config.py
  routers/ (22 files)
  services/ (3 files)

frontend/src/
  App.js, App.css, index.css
  components/ (11 files)
  features/ (15 files)
  config/, data/, hooks/, services/, utils/

docs/
  KN_00 through KN_13 (13 files)

memory/
  PRD.md, SESSION_LOG.md, TECH_DECISIONS.md

scripts/
  validate_compliance.py, check_nav_map.py

[CREATED NEW - Session #004]
  ENTITY_REGISTRY.md        ← NEW - SSOT untuk semua entitas
  CODEBASE_MAP.md           ← NEW - Quick reference semua file
  memory/SESSION_HANDOFF.md ← NEW - File ini

[COMPLETED - Session #005]
  scripts/validate_compliance.py  ← UPGRADED - 15 checks (monster files, naming, tech debt, imports)
  scripts/load_context.sh   ← VERIFIED & WORKING - instant context loader dengan DB state
  seed_realistic.py         ← DIJALANKAN (data sudah ada di DB)
```

---

## ⚠️ KNOWN GOTCHAS — BACA SEBELUM CODING

```
1. AUTH: Bearer token via Authorization header
   BUKAN cookie. dependencies.py → current_user() ambil dari header.
   Format header: "Authorization: Bearer sess_abc123"

2. PASSWORD HASH: pakai hash_password() dari core_utils.py
   BUKAN bcrypt. Format: SHA256("kain-nusantara::" + password)

3. WMS TASKS: wms_tasks adalah SATU collection untuk inbound DAN outbound
   Dibedakan oleh field flow_type: "inbound" | "outbound"
   JANGAN buat collection inbound_tasks atau outbound_tasks

4. INVENTORY: Stok ADA di inventory_balances, BUKAN di products
   Satu record per (product_id + warehouse_id) — UNIQUE constraint
   Update stok = SELALU buat inventory_movements dulu, lalu update balance

5. SAFE_DOC: Selalu wrap hasil MongoDB query dengan safe_doc()
   dari core_utils.py sebelum return ke client
   Ini handle ObjectId, datetime serialization

6. SEED DATA: Ada 2 seed mechanisms:
   a. server.py lifespan → seed minimal (users, uoms, warehouses, products awal)
   b. seed_realistic.py → seed lengkap dengan realistic data
   Jika DB kosong dan backend restart → seed minimal jalan otomatis

7. DB_NAME: "kain_nusantara" (bukan "test_database")
   Diset di /app/backend/.env

8. CORS: Backend set CORS_ORIGINS="*" di .env (development only)

9. ROUTER PREFIX: Semua endpoint harus prefix /api/
   Backend binding: 0.0.0.0:8001
   Frontend env: REACT_APP_BACKEND_URL sudah include base URL

10. SNAPSHOT PATTERN: Saat order dibuat, simpan customer_name di order document
    JANGAN hanya simpan customer_id lalu lookup saat display
    Ini cegah data rusak jika customer di-rename nanti
```

---

## 🚦 STATUS FITUR SAAT INI

```
✅ COMPLETED & WORKING:
  - Auth (login, logout, role-based access)
  - Master Data CRUD (Products, Customers, Warehouses, UOMs, Users)
  - Sales POS + Order Creation
  - Order Management & Approval workflow
  - WMS: Inventory, Inbound, Outbound, Transfer, Cycle Count
  - Purchase Orders
  - Invoicing (simulated)
  - Documents & Print Center
  - Reporting & Analytics (6 types)
  - Escalation Management
  - Audit Trail
  - Guided Tour (7 tours)
  - Permission Matrix
  - CSV Import/Export
  - Label Printer
  - Context Preservation System (load_context.sh + validate_compliance.py)
  - Multi-Entity (Fase 0): business_entities, entity_id scoped, Entity Switcher, Notification Center
  - Roll-as-SSOT Inventory Ownership (Fase 0.5): inventory_rolls, owner-scoped reservasi, FEFO allocation
  - Configuration Foundation (Fase 1A): system_settings, payment_terms, approval_rules, SettingsPanel
  - Configuration Consumption (Fase 1B): PPN otomatis, diskon per-item/order, approval dinamis
  - ATP & Fulfillment Modes (Sub-fase 1.4): preview-allocation READ-ONLY, Inventory Status Board
  - Inter-Company Transfer Flow (Sub-fase 1.5): POST /transfers/inter-company, approve (ownership B→E), reject/cancel + CartPanel button + InterCompanyTransfers page

⚠️ PARTIAL / KNOWN GAPS:
  - Payment: SIMULATED only (no real gateway)
  - Supplier: string field only (no supplier master collection)
  - Real-time: POLLING only (no WebSocket/Redis yet)
  - RFID: Architecture docs ada, implementasi belum
  - Finance Module: Belum ada (GL, AP/AR)
  - HR Module: Belum ada
  - Multi-tenancy: tenant_id placeholder ada, logic belum

🔴 BACKLOG CRITICAL (dari PRD):
  1. Auto-reservation expiry job (cron)
  2. ~~Discount field per item di POS~~ ✅ DONE (Fase 1B)
  3. ~~Tax 11% PPN configurable~~ ✅ DONE (Fase 1B)
  4. Redis + WebSocket real-time
  5. Supplier Master sebagai entitas

🔧 TECHNICAL DEBT (Detected by validate_compliance.py):
  - TransferManagement.jsx: 548 baris (melebihi limit 500) — perlu split
  - InventoryStockView.jsx: 503 baris (melebihi limit 500) — perlu split
  - Duplicate endpoint GET /sales-orders di sales_orders.py — perlu cleanup
```

---

## 📊 DATABASE STATE (Setelah Seed)

```
users:                5 records (admin, sales, manager, warehouse x2)
products:             7 records (Batik, Tenun, Lurik, Songket, Ulos, dll)
customers:            5 records
warehouses:           3 records (Jakarta, Bandung, Surabaya)
uoms:                 4 records (MTR, YRD, RLL, PCS)
inventory_balances:   12 records
inventory_movements:  19 records
sales_orders:         8 records
purchase_orders:      6 records
wms_tasks:            18 records
invoices:             generated dari orders
audit_logs:           6+ records
```

---

## 🎯 NEXT RECOMMENDED TASKS (Dari PRD Backlog)

Urutan prioritas berdasarkan impact bisnis:

```
P0 (Context Maintenance - SETIAP SESSION):
  → Jalankan: bash /app/scripts/load_context.sh (untuk load state)
  → Sebelum mark DONE: python3 /app/scripts/validate_compliance.py
  → Update SESSION_HANDOFF.md di akhir session

P1 (Critical - lakukan duluan):
  → Implement Redis + stock locking yang benar
  → WebSocket untuk real-time stock di Sales POS
  → Auto-reservation expiry cron job

P2 (High - Q3 2026):
  → Discount field di POS per item
  → PPN 11% configurable
  → Supplier Master collection + form
  → Notification system (in-app)
  → Fix technical debt: refactor monster files (TransferManagement, InventoryStockView)

P3 (Medium):
  → Finance module (GL, AP/AR)
  → HR module
  → Multi-tenancy (anak perusahaan)
  → RFID edge agent implementation
  → Backorder lifecycle (waiting_stock + auto-fulfill saat GR) — Sub-fase 1.6
  → Allocation policy R1/R2 configurable — Sub-fase 1.7
  → Mixed-lot confirmation UI — Sub-fase 1.8
```

---

## 🛑 JANGAN LAKUKAN SEBELUM TANYA USER

```
- Drop collection yang sudah ada data (users, sales_orders, dll)
- Rename API endpoint yang sudah ada (breaking change)
- Ubah auth flow (Bearer token)
- Tambah Python/JS dependency baru tanpa konfirmasi
- Ubah struktur MongoDB schema yang sudah ada data
- Tambah menu/navigasi baru di luar KN_13
```

---

**Template untuk Update:**
Isi ulang bagian "QUICK STATE", "FILE YANG DISENTUH", dan update STATUS FITUR
di akhir setiap session. Section KNOWN GOTCHAS dan JANGAN LAKUKAN hanya
ditambah jika ada temuan baru — jangan dihapus yang sudah ada.
