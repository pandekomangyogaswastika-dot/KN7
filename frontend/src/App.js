import { useState } from "react";
import "./App.css";
import { LoginScreen, MetricCard, Sidebar, TopBar } from "./components/CoreWidgets";
import { formatQty } from "./utils/formatters";
import { SalesPortal } from "./features/sales/SalesPortal";
import PriceApprovals from "./features/sales/PriceApprovals";
import OrdersView from "./features/orders/OrdersView";
import OperationsView from "./features/wms/OperationsView";
import DocumentsView from "./features/documents/DocumentsView";
import AdminView from "./features/admin/AdminView";
import DetailDrawer from "./components/DetailDrawer";
import TourMenu from "./components/TourMenu";
import OnboardingPanel from "./components/OnboardingPanel";
import EntitySwitcher from "./components/EntitySwitcher";
import NotificationCenter from "./components/NotificationCenter";
import { PAGE_META, GUIDANCE_MAP, buildNavigation } from "./config/navigationConfig";
import { useAppActions } from "./hooks/useAppActions";
import ManagerDashboard from "./features/manager/ManagerDashboard";
import PurchaseOrderManagement from "./features/admin/PurchaseOrderManagement";
import InventoryStatusBoard from "./features/inventory/InventoryStatusBoard";
import InterCompanyTransfers from "./features/transfers/InterCompanyTransfers";
import EscalationManagement from "./features/manager/EscalationManagement";
import GuidedTour from "./components/GuidedTour";
import {
  Archive,
  Boxes,
  Building2,
  Clock3,
  PackageCheck,
  Sparkles,
  Warehouse,
} from "lucide-react";


function App() {
  const [activeView, setActiveView] = useState("sales");
  const [data, setData] = useState({ products: [], customers: [], orders: [], warehouses: [], metrics: {} });
  const [movements, setMovements] = useState([]);
  const [templates, setTemplates] = useState([]);
  const [users, setUsers] = useState([]);
  const [uoms, setUoms] = useState([]);
  const [tasks, setTasks] = useState([]);
  const [onboarding, setOnboarding] = useState(null);
  const [showOnboarding, setShowOnboarding] = useState(false);
  const [permissions, setPermissions] = useState({ matrix: {}, actions: [] });
  const [auditLogs, setAuditLogs] = useState([]);
  const [auditFilters, setAuditFilters] = useState({ actor: "", module: "", action: "", date_from: "", date_to: "" });
  
  // Guided Tour state
  const [activeTour, setActiveTour] = useState(null);
  const [showTourMenu, setShowTourMenu] = useState(false);
  const [previewHtml, setPreviewHtml] = useState("");
  const [activeDetail, setActiveDetail] = useState(null);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [user, setUser] = useState(() => JSON.parse(localStorage.getItem("kn_user") || "null"));
  const [token, setToken] = useState(() => localStorage.getItem("kn_token") || "");
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [breakdown, setBreakdown] = useState(null);
  const [cart, setCart] = useState([]);
  const [selectedCustomer, setSelectedCustomer] = useState(null);
  const [selectedAddress, setSelectedAddress] = useState("");
  const [search, setSearch] = useState("");
  const [notice, setNotice] = useState("Sistem siap. Stok reservation dikunci 3 hari.");
  const [lastDocument, setLastDocument] = useState(null);
  const [lastLabel, setLastLabel] = useState(null);
  const [loading, setLoading] = useState(false);

  // Multi-Entity + Notification Center (Fase 0)
  const [entities, setEntities] = useState([]);
  const [selectedEntity, setSelectedEntity] = useState(() => localStorage.getItem("kn_entity") || "all");
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);

  // Configuration Foundation (Fase 1A) consumed by Sales/Orders (Fase 1B)
  const [settings, setSettings] = useState({});
  const [paymentTerms, setPaymentTerms] = useState([]);

  const onSelectEntity = (id) => {
    setSelectedEntity(id);
    localStorage.setItem("kn_entity", id);
  };

  // All async actions + side-effects live in this hook (SSOT for business logic).
  const actions = useAppActions({
    // values
    user, token, auditFilters, selectedCustomer, selectedAddress, cart, data, selectedEntity,
    // setters
    setUser, setToken, setActiveView, setNotice, setOnboarding, setShowOnboarding,
    setData, setTemplates, setUoms, setMovements, setTasks, setUsers, setPermissions, setAuditLogs,
    setSelectedCustomer, setSelectedAddress, setSelectedProduct, setBreakdown,
    setCart, setLastDocument, setLastLabel, setPreviewHtml,
    setActiveDetail, setLoading, setEntities, setNotifications, setUnreadCount,
    setSettings, setPaymentTerms,
  });
  const {
    login, logout, showMetricDetail, loadAll,
    inspectProduct, addToCart, createCustomer, submitOrder, mutateOrder,
    payInvoice, releaseReservation, generateDocument, generateLabel,
    approvePurchaseOrder,
    adminCreate, adminPatch, adminDelete, importMaster, exportMaster,
    updatePermissions, seedDemo, previewTemplate, refreshAudit,
    createInboundTask, createOutboundTasks, scanTask, advanceTask,
    markNotificationRead, markAllNotificationsRead, generateNotifications,
  } = actions;

  const nav = buildNavigation(user?.role);

  if (!user) return <LoginScreen onLogin={login} notice={notice} />;

  const pageMeta = PAGE_META[activeView] || { kicker: "Workspace", title: "Kain Nusantara" };
  const guidance = GUIDANCE_MAP[activeView];

  return (
    <div className={`app-shell layout-grid`}>
      <a className="skip-link" href="#main-content">Skip to content</a>
      <Sidebar
        items={nav}
        activeId={activeView}
        onSelect={setActiveView}
        user={user}
        onLogout={logout}
        open={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
      />
      <div className="app-main">
        <TopBar
          title={pageMeta.title}
          kicker={pageMeta.kicker}
          onToggleSidebar={() => setSidebarOpen((v) => !v)}
          onSync={loadAll}
          syncing={loading}
          notice={notice}
          infoCta={guidance ? { label: guidance.label, onClick: () => setActiveView(guidance.target) } : null}
          entitySwitcher={<EntitySwitcher entities={entities} value={selectedEntity} onChange={onSelectEntity} />}
          notificationCenter={
            <NotificationCenter
              notifications={notifications}
              unreadCount={unreadCount}
              canGenerate={["admin", "manager"].includes(user?.role)}
              onMarkRead={markNotificationRead}
              onMarkAll={markAllNotificationsRead}
              onGenerate={generateNotifications}
              onNavigate={(target) => setActiveView(target)}
            />
          }
        />
        <main id="main-content" className="mx-auto w-full max-w-[1600px] px-4 py-4 md:px-5 md:py-5">
          <section data-testid="metrics-row" className="grid gap-3 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5 no-print">
            <MetricCard testId="metric-products" icon={Archive} label="Produk Aktif" value={data.metrics?.products || 0} tone="rgba(0,122,255,.12)" hint="Buka katalog" onClick={() => showMetricDetail("products")} />
            <MetricCard testId="metric-available" icon={Boxes} label="Available Qty" value={formatQty(data.metrics?.available_qty)} tone="rgba(52,199,89,.14)" hint="Lihat stok" onClick={() => showMetricDetail("available")} />
            <MetricCard testId="metric-reserved" icon={Clock3} label="Reserved Qty" value={formatQty(data.metrics?.reserved_qty)} tone="rgba(175,82,222,.14)" hint="Buka orders" onClick={() => showMetricDetail("reserved")} />
            <MetricCard testId="metric-orders" icon={PackageCheck} label="Active Orders" value={data.metrics?.active_orders || 0} tone="rgba(255,149,0,.14)" hint="Control room" onClick={() => showMetricDetail("orders")} />
            <MetricCard testId="metric-warehouses" icon={Building2} label="Gudang" value={data.metrics?.warehouses || 0} tone="rgba(60,60,67,.10)" hint="Buka WMS" onClick={() => showMetricDetail("warehouses")} />
          </section>

          <div className="md:hidden mt-3">
            <div data-testid="system-notice-mobile" className="info-ribbon">
              <Sparkles size={13} className="ribbon-icon" />
              <span>{notice}</span>
            </div>
          </div>

          <DetailDrawer detail={activeDetail} onClose={() => setActiveDetail(null)} onNavigate={(target) => { setActiveView(target); setActiveDetail(null); }} />

          {/* Onboarding Checklist Panel */}
          {showOnboarding && (
            <OnboardingPanel
              onboarding={onboarding}
              onDismiss={() => setShowOnboarding(false)}
              onUpdate={setOnboarding}
            />
          )}

          <div className="mt-4 md:mt-5">
            {activeView === "admin" && <AdminView data={data} loading={loading} users={users} uoms={uoms} templates={templates} entities={entities} permissions={permissions} previewHtml={previewHtml} auditLogs={auditLogs} auditFilters={auditFilters} setAuditFilters={setAuditFilters} onAdminCreate={adminCreate} onAdminPatch={adminPatch} onAdminDelete={adminDelete} onImportMaster={importMaster} onExportMaster={exportMaster} onUpdatePermissions={updatePermissions} onPreviewTemplate={previewTemplate} onRefreshAudit={refreshAudit} onShowDetail={setActiveDetail} onSeedDemo={seedDemo} />}
            {activeView === "reports" && <ManagerDashboard token={token} />}
            {activeView === "sales" && <SalesPortal data={data} loading={loading} selectedProduct={selectedProduct} breakdown={breakdown} onInspect={inspectProduct} onAdd={addToCart} cart={cart} setCart={setCart} selectedCustomer={selectedCustomer} setSelectedCustomer={setSelectedCustomer} selectedAddress={selectedAddress} setSelectedAddress={setSelectedAddress} onCreateCustomer={createCustomer} onSubmitOrder={submitOrder} search={search} setSearch={setSearch} onShowDetail={setActiveDetail} settings={settings} paymentTerms={paymentTerms} selectedEntity={selectedEntity} />}
            {activeView === "inventory-board" && <InventoryStatusBoard selectedEntity={selectedEntity} entities={entities} />}
            {activeView === "price-approvals" && <PriceApprovals currentUser={user} />}
            {activeView === "interco-transfers" && <InterCompanyTransfers currentUser={user} />}
            {activeView === "orders" && <OrdersView orders={data.orders || []} loading={loading} user={user} onShowDetail={setActiveDetail} onSubmitForApproval={(id) => mutateOrder(`/sales-orders/${id}/submit-for-approval`, (order) => order.status === "approved" ? `${order.number} auto-approved (di bawah threshold).` : `${order.number} dikirim untuk approval (butuh ${order.required_approval_role || "approver"}).`)} onApprove={(id) => mutateOrder(`/sales-orders/${id}/approve`, (order) => `${order.number} approved.`)} onConfirm={(id) => mutateOrder(`/sales-orders/${id}/confirm`, (order) => `${order.number} confirmed.`)} onCancel={(id) => mutateOrder(`/sales-orders/${id}/cancel`, (order) => `${order.number} dibatalkan, stok unlock.`)} onPay={payInvoice} onGenerateDocument={generateDocument} onReleaseReservation={releaseReservation} />}
            {activeView === "purchasing" && <PurchaseOrderManagement user={user} onApprovePO={approvePurchaseOrder} />}
            {activeView === "operations" && <OperationsView data={data} movements={movements} tasks={tasks} entities={entities} selectedEntity={selectedEntity} onGenerateLabel={generateLabel} onCreateInboundTask={createInboundTask} onCreateOutboundTasks={createOutboundTasks} onScanTask={scanTask} onAdvanceTask={advanceTask} onShowDetail={setActiveDetail} token={token} user={user} />}
            {activeView === "escalations" && <EscalationManagement user={user} />}
            {activeView === "documents" && <DocumentsView templates={templates} loading={loading} lastDocument={lastDocument} lastLabel={lastLabel} onGenerateLabel={generateLabel} products={data.products || []} />}
          </div>
        </main>
      </div>
      
      {/* Guided Tour Component */}
      {activeTour && (
        <GuidedTour
          isActive={true}
          onClose={() => setActiveTour(null)}
          steps={activeTour.steps}
          tourId={activeTour.id}
          onComplete={() => {
            setActiveTour(null);
          }}
        />
      )}
      
      {/* Floating Help Button */}
      <TourMenu
        userRole={user?.role}
        showMenu={showTourMenu}
        onToggleMenu={() => setShowTourMenu(!showTourMenu)}
        onSelectTour={(tour) => {
          setActiveTour(tour);
          setShowTourMenu(false);
        }}
      />
    </div>
  );
}

export default App;