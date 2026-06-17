import { XCircle, Clock3, Truck, CreditCard, PackageX, ShieldAlert, Send, FileText, AlertTriangle } from "lucide-react";
import { formatCurrency, formatQty } from "../../utils/formatters";
import { StatusPill } from "../../components/CoreWidgets";

const TIMELINE_STEPS = [
  { status: "waiting_approval", label: "Waiting Approval", icon: "⏳" },
  { status: "reserved", label: "Reserved (Approved)", icon: "✓" },
  { status: "approved", label: "Approved", icon: "✓" },
  { status: "confirmed", label: "Confirmed", icon: "✓" },
  { status: "dispatched", label: "Dispatched", icon: "🚚" },
  { status: "done", label: "Done", icon: "✅" },
];
const STATUS_ORDER = ["waiting_approval", "reserved", "approved", "confirmed", "dispatched", "done"];

export function OrderDetailPanel({
  order: sel,
  onApprove,
  onConfirm,
  onCancel,
  onPay,
  onGenerateDocument,
  onReleaseReservation,
  onSubmitForApproval,
  onClose,
}) {
  return (
    <aside data-testid="order-detail-panel" className="section-card self-start">
      <div className="section-head">
        <div className="min-w-0">
          <p className="text-[10px] font-bold uppercase tracking-wide text-[#0058CC]">{sel.number}</p>
          <div className="flex items-center gap-1.5 mt-0.5 flex-wrap">
            <StatusPill status={sel.status} />
            <StatusPill status={sel.payment_status} />
            {sel.has_backorder && (
              <span data-testid="order-backorder-chip" className="rounded bg-[#FFF1EA] px-1.5 py-0.5 text-[9px] font-bold uppercase tracking-wide text-[#B23B14]">
                Backorder
              </span>
            )}
          </div>
        </div>
        <button className="icon-button" onClick={onClose}>
          <XCircle size={14} />
        </button>
      </div>
      <div className="section-body space-y-3">
        <div>
          <p data-testid="order-customer-detail" className="text-[12px] font-semibold">{sel.customer_name}</p>
          <p className="text-[11px] text-[#6B6B73]">{sel.customer_city || sel.shipping_city || "—"} · Sales: {sel.sales_name || "—"}</p>
          {sel.reservation_expires_at && (
            <p data-testid="order-expiry-detail" className="mt-0.5 flex items-center gap-1 text-[10.5px] text-[#7A2CA0]">
              <Clock3 size={11} /> {new Date(sel.reservation_expires_at).toLocaleString("id-ID")}
            </p>
          )}
        </div>

        {/* Sub-fase 1.6 — banner backorder (waiting_stock) */}
        {sel.has_backorder && (sel.backorders || []).length > 0 && (
          <div data-testid="order-backorder-panel" className="rounded-md border border-[#F5C9A6] bg-[#FFF7EF] p-2.5">
            <div className="flex items-center gap-1.5 mb-1.5">
              <AlertTriangle size={13} className="text-[#B23B14]" />
              <p className="text-[10px] font-bold uppercase tracking-wide text-[#8C4A00]">Menunggu Stok (Backorder)</p>
            </div>
            <p className="text-[10.5px] text-[#8C4A00] mb-2">
              Sebagian item menunggu barang masuk. Akan otomatis ter-reservasi saat barang diterima (Goods Receipt).
            </p>
            <div className="space-y-1">
              {(sel.backorders || []).filter((b) => Number(b.backorder_qty) > 0).map((b) => (
                <div
                  key={b.id || b.product_id}
                  data-testid={`order-backorder-line-${b.product_id}`}
                  className="flex items-center justify-between rounded bg-white/70 px-2 py-1 text-[10.5px]"
                >
                  <span className="font-semibold text-[#1C1C1E] truncate">{b.product_name || b.sku}</span>
                  <span className="tabular-nums text-[#B23B14] font-bold shrink-0">{formatQty(b.backorder_qty)} menunggu</span>
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="rounded-md border border-[#EFF0F2] bg-[#FAFBFC] p-2.5">
          <p className="text-[10px] font-bold uppercase text-[#6B6B73] mb-2">Status Timeline</p>
          <div className="space-y-1.5">
            {TIMELINE_STEPS.map(({ status, label, icon }) => {
              const currentIdx = STATUS_ORDER.indexOf(sel.status);
              const stepIdx = STATUS_ORDER.indexOf(status);
              const isActive = stepIdx === currentIdx;
              const isPassed = stepIdx < currentIdx;
              const isCancelled = sel.status === "cancelled";
              return (
                <div key={status} className="flex items-center gap-2">
                  <div className={`w-5 h-5 rounded-full flex items-center justify-center text-[10px] flex-shrink-0 ${
                    isCancelled ? "bg-gray-200 text-gray-400" :
                    isActive ? "bg-[#007AFF] text-white font-bold" :
                    isPassed ? "bg-green-500 text-white" :
                    "bg-gray-200 text-gray-400"
                  }`}>
                    {isPassed || isActive ? icon : "○"}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className={`text-[11px] ${
                      isCancelled ? "text-gray-400" :
                      isActive ? "font-bold text-[#007AFF]" :
                      isPassed ? "text-green-700 font-semibold" :
                      "text-[#8E8E93]"
                    }`}>
                      {label}
                    </p>
                  </div>
                  {isActive && <span className="text-[9px] px-1.5 py-0.5 rounded bg-[#007AFF] text-white font-bold">CURRENT</span>}
                </div>
              );
            })}
            {sel.status === "cancelled" && (
              <div className="flex items-center gap-2 mt-2 pt-2 border-t border-[#EFF0F2]">
                <div className="w-5 h-5 rounded-full flex items-center justify-center text-[10px] flex-shrink-0 bg-red-500 text-white">✕</div>
                <p className="text-[11px] font-bold text-red-600">Order Cancelled</p>
              </div>
            )}
          </div>
        </div>

        <div className="rounded-md border border-[#EFF0F2] overflow-hidden">
          <div className="px-2.5 py-1.5 bg-[#FAFBFC] text-[10px] font-bold uppercase text-[#6B6B73] border-b border-[#EFF0F2]">Items</div>
          {(sel.items || []).map((item, idx) => (
            <div
              data-testid={`order-item-${sel.id}-${item.id || item.product_id || idx}`}
              key={item.id || item.product_id || idx}
              className="px-2.5 py-1.5 border-b border-[#EFF0F2] last:border-0"
            >
              <p className="text-[10.5px] font-bold text-[#0058CC]">{item.sku}</p>
              <div className="flex justify-between">
                <p className="text-[11px]">{item.product_name}</p>
                <p className="text-[11px] font-semibold">{formatQty(item.quantity)} {item.unit}</p>
              </div>
              {Number(item.backorder_qty) > 0 && (
                <div data-testid={`order-item-backorder-${item.product_id}`} className="mt-0.5 flex gap-3 text-[10px] tabular-nums">
                  <span className="font-semibold text-[#126E2C]">Reserved {formatQty(item.reserved_qty)}</span>
                  <span className="font-semibold text-[#B23B14]">Backorder {formatQty(item.backorder_qty)}</span>
                </div>
              )}
              <div className="flex justify-between text-[10.5px] text-[#6B6B73]">
                <span>
                  {formatCurrency(item.price)}/{item.unit}
                  {Number(item.discount_percent) > 0 && (
                    <span className="ml-1 text-[#FF9500] font-semibold">· disc {item.discount_percent}%</span>
                  )}
                </span>
                <span className="font-semibold text-[#3C3C43]">
                  {formatCurrency(item.line_total != null ? item.line_total : item.subtotal)}
                </span>
              </div>
            </div>
          ))}
        </div>

        {/* Ringkasan harga + pajak (Fase 1B) */}
        <div data-testid="order-pricing-breakdown" className="rounded-md border border-[#EFF0F2] bg-[#FAFBFC] p-2.5 space-y-1 text-[11.5px]">
          <p className="text-[10px] font-bold uppercase text-[#6B6B73] mb-1">Ringkasan Harga</p>
          <BreakRow label="Subtotal (bruto)" value={formatCurrency(sel.total_amount)} />
          {Number(sel.discount_total) > 0 && (
            <>
              <BreakRow label="Diskon" value={`− ${formatCurrency(sel.discount_total)}`} amber />
              <BreakRow label="Subtotal netto (DPP)" value={formatCurrency(sel.net_subtotal != null ? sel.net_subtotal : sel.total_amount)} />
            </>
          )}
          {Number(sel.ppn_amount) > 0 ? (
            <BreakRow label={`PPN ${sel.ppn_rate || 0}%`} value={formatCurrency(sel.ppn_amount)} />
          ) : (
            <BreakRow label="PPN" value={sel.is_pkp === false ? "Non-PKP (0)" : formatCurrency(0)} muted />
          )}
          <div className="flex items-center justify-between border-t border-[#E5E5EA] pt-1 mt-1">
            <span className="text-[10px] font-bold uppercase text-[#6B6B73]">Grand Total</span>
            <span data-testid="order-grand-total" className="text-[14px] font-bold text-[#007AFF]">
              {formatCurrency(sel.grand_total != null ? sel.grand_total : sel.total_amount)}
            </span>
          </div>
          {sel.payment_term_name && (
            <p className="text-[10.5px] text-[#6B6B73] pt-0.5">Term: <span className="font-semibold text-[#3C3C43]">{sel.payment_term_name}</span></p>
          )}
        </div>

        {/* Badge kebutuhan approval (Fase 1B) */}
        {sel.approval_required && sel.required_approval_role && ["reserved", "waiting_approval"].includes(sel.status) && (
          <div data-testid="order-approval-badge" className="flex items-center gap-2 rounded-md border border-[#FFE2B8] bg-[#FFF7EC] px-2.5 py-1.5 text-[11px] text-[#9A5B00]">
            <ShieldAlert size={13} />
            <span>Butuh approval role <b className="uppercase">{sel.required_approval_role}</b> (Rp {formatQty(sel.approval_amount || sel.grand_total)})</span>
          </div>
        )}

        <div className="flex flex-wrap gap-2">
          {sel.status === "reserved" && onSubmitForApproval && (
            <button data-testid={`submit-approval-button-${sel.id}`} className="primary-button" onClick={() => onSubmitForApproval(sel.id)}>
              <Send size={13} /> {sel.approval_required ? "Submit for Approval" : "Proses (Auto-Approve)"}
            </button>
          )}
          {sel.status === "waiting_approval" && (
            <button data-testid={`approve-order-button-${sel.id}`} className="primary-button" onClick={() => onApprove(sel.id)}>
              <FileText size={13} /> Approve{sel.required_approval_role ? ` (${sel.required_approval_role})` : ""}
            </button>
          )}
          {sel.status === "approved" && (
            <button data-testid={`confirm-order-button-${sel.id}`} className="primary-button" onClick={() => onConfirm(sel.id)}>
              <FileText size={13} /> Confirm
            </button>
          )}
          {sel.status === "confirmed" && sel.payment_status !== "paid" && (
            <button data-testid={`simulate-payment-button-${sel.id}`} className="secondary-button" onClick={() => onPay(sel.id)}>
              <CreditCard size={13} /> Simulate Payment
            </button>
          )}
          {["reserved", "waiting_approval", "approved", "waiting_stock"].includes(sel.status) && (
            <button data-testid={`release-reservation-button-${sel.id}`} className="secondary-button" onClick={() => onReleaseReservation(sel.id)}>
              <PackageX size={13} /> Release Reservation
            </button>
          )}
          {!["done", "cancelled"].includes(sel.status) && (
            <button data-testid={`cancel-order-button-${sel.id}`} className="secondary-button text-red-600" onClick={() => onCancel(sel.id)}>
              <XCircle size={13} /> Cancel
            </button>
          )}
          {["confirmed", "dispatched", "done"].includes(sel.status) && (
            <>
              <button data-testid={`generate-invoice-button-${sel.id}`} className="secondary-button" onClick={() => onGenerateDocument("invoice", sel.id)}>
                <FileText size={13} /> Invoice (PPN)
              </button>
              <button data-testid={`generate-sj-button-${sel.id}`} className="secondary-button" onClick={() => onGenerateDocument("surat_jalan", sel.id)}>
                <Truck size={13} /> Surat Jalan
              </button>
            </>
          )}
        </div>
      </div>
    </aside>
  );
}

function BreakRow({ label, value, amber = false, muted = false }) {
  return (
    <div className="flex items-center justify-between">
      <span className={muted ? "text-[#8E8E93]" : "text-[#6B6B73]"}>{label}</span>
      <span className={amber ? "font-semibold text-[#FF9500]" : muted ? "text-[#8E8E93]" : "font-semibold text-[#3C3C43]"}>{value}</span>
    </div>
  );
}
