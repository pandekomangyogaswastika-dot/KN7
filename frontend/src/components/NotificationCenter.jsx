import { Bell, Check, CheckCheck, RefreshCw, AlertTriangle, Info, X } from "lucide-react";
import { useState, useRef, useEffect } from "react";

const SEVERITY_ICON = { warning: AlertTriangle, critical: AlertTriangle, info: Info };

function timeAgo(iso) {
  if (!iso) return "";
  const diff = (Date.now() - new Date(iso).getTime()) / 1000;
  if (diff < 60) return "baru saja";
  if (diff < 3600) return `${Math.floor(diff / 60)} mnt lalu`;
  if (diff < 86400) return `${Math.floor(diff / 3600)} jam lalu`;
  return `${Math.floor(diff / 86400)} hari lalu`;
}

/**
 * Notification Center (Fase 0) — bell + dropdown daftar notifikasi in-app.
 * Sumber data REAL: stok menipis & reservasi mendekati kedaluwarsa.
 */
export default function NotificationCenter({
  notifications = [], unreadCount = 0, canGenerate = false,
  onMarkRead, onMarkAll, onGenerate, onNavigate,
}) {
  const [open, setOpen] = useState(false);
  const ref = useRef(null);

  useEffect(() => {
    const onClick = (e) => { if (ref.current && !ref.current.contains(e.target)) setOpen(false); };
    document.addEventListener("mousedown", onClick);
    return () => document.removeEventListener("mousedown", onClick);
  }, []);

  return (
    <div className="notif-center" ref={ref}>
      <button
        type="button"
        data-testid="notif-bell"
        className="icon-button notif-bell"
        onClick={() => setOpen((v) => !v)}
        aria-label="Notifikasi"
        title="Notifikasi"
      >
        <Bell size={15} />
        {unreadCount > 0 && (
          <span data-testid="notif-badge" className="notif-badge">{unreadCount > 99 ? "99+" : unreadCount}</span>
        )}
      </button>
      {open && (
        <div className="notif-panel" data-testid="notif-panel">
          <div className="notif-panel-head">
            <span className="notif-panel-title">Notifikasi</span>
            <div className="flex items-center gap-1">
              {canGenerate && (
                <button data-testid="notif-generate-button" className="notif-mini-button" title="Pindai event sistem" onClick={() => onGenerate?.()}>
                  <RefreshCw size={12} /> Scan
                </button>
              )}
              <button data-testid="notif-mark-all-button" className="notif-mini-button" title="Tandai semua dibaca" onClick={() => onMarkAll?.()}>
                <CheckCheck size={12} /> Semua
              </button>
              <button className="icon-button" aria-label="Tutup" onClick={() => setOpen(false)}><X size={14} /></button>
            </div>
          </div>
          <div className="notif-list" data-testid="notif-list">
            {notifications.length === 0 && (
              <div data-testid="notif-empty" className="notif-empty">Tidak ada notifikasi. Sistem dalam kondisi baik.</div>
            )}
            {notifications.map((n) => {
              const Icon = SEVERITY_ICON[n.severity] || Info;
              return (
                <div
                  key={n.id}
                  data-testid={`notif-item-${n.id}`}
                  className={`notif-item sev-${n.severity || "info"} ${n.read ? "read" : "unread"}`}
                  role="button"
                  tabIndex={0}
                  onClick={() => { if (!n.read) onMarkRead?.(n.id); if (n.link) onNavigate?.(n.link); setOpen(false); }}
                >
                  <div className="notif-item-icon"><Icon size={15} /></div>
                  <div className="notif-item-body">
                    <div className="notif-item-title">{n.title}</div>
                    <div className="notif-item-text">{n.body}</div>
                    <div className="notif-item-time">{timeAgo(n.created_at)}</div>
                  </div>
                  {!n.read && (
                    <button
                      data-testid={`notif-read-${n.id}`}
                      className="notif-read-dot"
                      title="Tandai dibaca"
                      onClick={(e) => { e.stopPropagation(); onMarkRead?.(n.id); }}
                    >
                      <Check size={12} />
                    </button>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
