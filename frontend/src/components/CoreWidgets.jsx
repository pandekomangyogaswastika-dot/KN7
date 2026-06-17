import { Layers3, Menu, X, RefreshCw, LogOut, Sparkles } from "lucide-react";

export function StatusPill({ status, testId }) {
  return <span data-testid={testId} className={`status-pill status-${status}`}>{String(status || "-").replaceAll("_", " ")}</span>;
}

export function MetricCard({ icon: Icon, label, value, tone, testId, onClick, hint }) {
  return (
    <button type="button" data-testid={testId} className="metric-card" onClick={onClick}>
      <div className="metric-icon" style={{ background: tone }}>
        <Icon size={18} data-testid={`${testId}-icon`} />
      </div>
      <div className="metric-body">
        <span className="metric-label" data-testid={`${testId}-label`}>{label}</span>
        <span className="metric-value" data-testid={`${testId}-value`}>{value}</span>
        {hint && <span className="metric-hint" data-testid={`${testId}-hint`}>{hint}</span>}
      </div>
    </button>
  );
}

export function Sidebar({ items, activeId, onSelect, user, onLogout, open, onClose }) {
  const initials = (user?.name || user?.email || "?").slice(0, 2).toUpperCase();
  return (
    <>
      <div data-testid="sidebar-backdrop" className={`sidebar-backdrop ${open ? "open" : ""} no-print`} onClick={onClose} aria-hidden="true" />
      <aside data-testid="app-sidebar" className={`app-sidebar ${open ? "open" : ""} no-print`}>
        <div className="sidebar-brand">
          <div data-testid="brand-mark" className="sidebar-brand-mark"><Layers3 size={16} /></div>
          <div className="sidebar-brand-text">
            <span data-testid="app-brand" className="t1">Kain Nusantara</span>
            <span data-testid="app-subtitle" className="t2">Inventory · WMS · Sales</span>
          </div>
        </div>
        <nav data-testid="main-navigation" className="sidebar-nav" aria-label="Main">
          <span className="sidebar-nav-group-label">Workspace</span>
          {items.map((item) => {
            const Icon = item.icon;
            return (
              <button
                key={item.id}
                data-testid={`nav-${item.id}`}
                className={`sidebar-item ${activeId === item.id ? "active" : ""}`}
                onClick={() => { onSelect(item.id); onClose && onClose(); }}
                aria-current={activeId === item.id ? "page" : undefined}
              >
                <Icon size={16} />
                <span className="label">{item.label}</span>
              </button>
            );
          })}
        </nav>
        <div className="sidebar-footer">
          <div className="user-chip" data-testid="user-menu-button">
            <div className="avatar">{initials}</div>
            <div className="user-text">
              <span className="name">{user?.name || user?.email?.split("@")[0]}</span>
              <span className="role">{user?.role}</span>
            </div>
          </div>
          <button data-testid="logout-button" className="secondary-button" onClick={onLogout}><LogOut size={14} /> Logout</button>
        </div>
      </aside>
    </>
  );
}

export function TopBar({ title, kicker, onToggleSidebar, onSync, syncing, notice, onShowDetail, infoCta, entitySwitcher, notificationCenter }) {
  return (
    <header className="topbar no-print" role="banner">
      <button
        type="button"
        data-testid="sidebar-toggle-button"
        className="icon-button menu-toggle"
        onClick={onToggleSidebar}
        aria-label="Toggle navigation"
      >
        <Menu size={16} />
      </button>
      <div className="title-block">
        {kicker && <span className="kicker" data-testid="page-kicker">{kicker}</span>}
        <h1 data-testid="page-title" className="page-title">{title}</h1>
      </div>
      {entitySwitcher && <div className="topbar-entity">{entitySwitcher}</div>}
      {notice && (
        <div data-testid="system-notice" className="info-ribbon desktop-only">
          <Sparkles size={13} className="ribbon-icon" />
          <span data-testid="system-notice-text">{notice}</span>
          {infoCta && (
            <button data-testid="system-notice-cta" className="nav-button ribbon-cta" onClick={infoCta.onClick}>{infoCta.label}</button>
          )}
        </div>
      )}
      <div className="topbar-actions">
        {notificationCenter}
        <button data-testid="refresh-data-button" className="icon-button" onClick={onSync} aria-label="Sync data" title="Sync">
          <RefreshCw size={14} className={syncing ? "animate-spin" : ""} />
        </button>
      </div>
    </header>
  );
}

export function PageSection({ kicker, title, actions, children, testId }) {
  return (
    <section data-testid={testId} className="section-card">
      <div className="section-head">
        <div className="flex items-center min-w-0">
          {kicker && <span className="kicker">{kicker}</span>}
          {title && <h2 className="truncate">{title}</h2>}
        </div>
        {actions && <div className="flex flex-wrap gap-2 justify-end">{actions}</div>}
      </div>
      <div className="section-body">{children}</div>
    </section>
  );
}

// LoginScreen extracted to ./LoginScreen.jsx (KN_02 modularity); re-export for back-compat.
export { LoginScreen } from "./LoginScreen";

// Re-export close icon for backwards compat if needed
export { X as CloseIcon };
