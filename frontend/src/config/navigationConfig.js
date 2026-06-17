import {
  AlertTriangle,
  ArrowLeftRight,
  BadgePercent,
  Boxes,
  ClipboardList,
  FileText,
  Layers3,
  Printer,
  Settings,
  ShoppingBag,
  Warehouse,
} from "lucide-react";

/**
 * Page metadata shown on the TopBar per active view.
 * Edit here to update kicker/title across the app (SSOT).
 */
export const PAGE_META = {
  admin:       { kicker: "Admin Workspace",  title: "Master Data & Audit" },
  sales:       { kicker: "Sales Workspace",  title: "Katalog POS & Reservation" },
  "price-approvals": { kicker: "Sales Workspace", title: "Approval Harga Khusus" },
  orders:      { kicker: "Order Control",    title: "Dashboard · Approval · Invoice · Receipt" },
  purchasing:  { kicker: "Purchasing",       title: "Purchase Order & Receiving" },
  operations:  { kicker: "Warehouse",        title: "Stok · Inbound · Outbound · Transfer" },
  "inventory-board": { kicker: "Inventory",  title: "Status Board · ATP & Fulfillment Modes" },
  "interco-transfers": { kicker: "Inventory", title: "Transfer Antar-Entitas (Inter-Company)" },
  escalations: { kicker: "Escalation",       title: "Eskalasi Inbound & Outbound" },
  documents:   { kicker: "Documents",        title: "Print Center & Labels" },
};

/**
 * Smart guidance CTA shown next to TopBar.
 */
export const GUIDANCE_MAP = {
  admin:       { label: "Audit",       target: "admin" },
  sales:       { label: "Cari Produk", target: "sales" },
  orders:      { label: "Review",      target: "orders" },
  purchasing:  { label: "Buat PO",     target: "purchasing" },
  operations:  { label: "WMS",         target: "operations" },
  "inventory-board": { label: "Cek ATP", target: "inventory-board" },
  "interco-transfers": { label: "Approve", target: "interco-transfers" },
  escalations: { label: "Resolve",     target: "escalations" },
  documents:   { label: "Print",       target: "documents" },
};

/**
 * Role-based menu visibility (allowlist per role).
 * - sales:     hanya akses pos / orders / documents
 * - warehouse: hanya akses operations / escalations / documents
 * - manager:   akses laporan, orders, purchasing, operations, escalations, documents
 * - admin:     akses semua menu (dengan tambahan admin & reports yang khusus role admin/manager)
 */
const ROLE_MENU_ALLOWLIST = {
  sales:     ["sales", "price-approvals", "inventory-board", "orders", "documents"],
  warehouse: ["operations", "inventory-board", "interco-transfers", "escalations", "documents"],
  manager:   ["reports", "price-approvals", "orders", "purchasing", "operations", "inventory-board", "interco-transfers", "escalations", "documents"],
};

/**
 * Build the navigation array for a given user role.
 * Returns array of { id, label, icon } items, already filtered for the role.
 */
export function buildNavigation(userRole) {
  const items = [
    ...(userRole === "admin" ? [{ id: "admin", label: "Admin", icon: Settings }] : []),
    ...(["admin", "manager"].includes(userRole) ? [{ id: "reports", label: "Dashboard", icon: Layers3 }] : []),
    { id: "sales",       label: "Sales POS",  icon: ShoppingBag },
    { id: "price-approvals", label: "Approval Harga", icon: BadgePercent },
    { id: "orders",      label: "Orders",     icon: FileText },
    { id: "purchasing",  label: "Purchasing", icon: ClipboardList },
    { id: "operations",  label: "WMS",        icon: Warehouse },
    { id: "inventory-board", label: "Status Stok", icon: Boxes },
    { id: "interco-transfers", label: "Transfer Antar-Entitas", icon: ArrowLeftRight },
    { id: "escalations", label: "Eskalasi",   icon: AlertTriangle },
    { id: "documents",   label: "Print Center", icon: Printer },
  ];
  const allowlist = ROLE_MENU_ALLOWLIST[userRole];
  if (!allowlist) return items; // admin & unknown roles → see everything
  return items.filter((item) => allowlist.includes(item.id));
}

/**
 * Default landing view per role after login.
 */
export function defaultViewForRole(role) {
  if (role === "admin")     return "admin";
  if (role === "warehouse") return "operations";
  if (role === "manager")   return "reports";
  return "sales";
}
