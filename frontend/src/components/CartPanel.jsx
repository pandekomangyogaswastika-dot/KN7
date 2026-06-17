import { useEffect, useState } from "react";
import { ShoppingBag, PackageCheck, XCircle, Receipt, ArrowLeftRight, AlertTriangle } from "lucide-react";
import { formatCurrency, formatQty } from "../utils/formatters";
import { computeOrderPreview } from "../utils/pricing";
import { modeMeta } from "../utils/fulfillment";

export function CartPanel({
  cart,
  setCart,
  selectedCustomer,
  selectedAddress,
  onSubmitOrder,
  onShowDetail,
  settings = {},
  paymentTerms = [],
  allocationLines = {},
  allocationLoading = false,
  transferRequests = {},
  onRequestTransfer,
  specialPrices = {},
}) {
  const [orderDiscount, setOrderDiscount] = useState(0);
  const [paymentTerm, setPaymentTerm] = useState("");
  const [allowBackorder, setAllowBackorder] = useState(false);

  const defaultTerm = settings?.finance?.default_payment_term_code || "";
  useEffect(() => {
    if (!paymentTerm && defaultTerm) setPaymentTerm(defaultTerm);
  }, [defaultTerm]); // eslint-disable-line react-hooks/exhaustive-deps

  // Sub-fase 1.6 — deteksi baris yang akan backorder (stok+incoming entitas kurang)
  const backorderQtyTotal = Object.values(allocationLines || {}).reduce(
    (sum, l) => sum + (Number(l?.breakdown?.backorder) || 0), 0
  );
  const hasBackorderLine = backorderQtyTotal > 0;

  const allowItemDiscount = settings?.sales?.allow_item_discount !== false;
  const allowOrderDiscount = settings?.sales?.allow_order_discount !== false;

  const updateQty = (productId, quantity) =>
    setCart(cart.map((item) =>
      item.product.id === productId ? { ...item, quantity: Number(quantity) || 0 } : item
    ));

  const updateDiscount = (productId, discount) =>
    setCart(cart.map((item) =>
      item.product.id === productId
        ? { ...item, discount_percent: Math.max(0, Math.min(100, Number(discount) || 0)) }
        : item
    ));

  const remove = (productId) =>
    setCart(cart.filter((item) => item.product.id !== productId));

  // Sub-fase 1.7 — harga khusus override harga normal untuk preview & display.
  const effectivePrice = (item) => {
    const sp = specialPrices[item.product.id];
    return sp && sp.has_special ? Number(sp.requested_price) : (item.product.price || 0);
  };
  const cartPriced = cart.map((item) => {
    const sp = specialPrices[item.product.id];
    return sp && sp.has_special
      ? { ...item, product: { ...item.product, price: Number(sp.requested_price) } }
      : item;
  });
  const hasSpecial = cart.some((i) => specialPrices[i.product.id]?.has_special);

  const p = computeOrderPreview(cartPriced, orderDiscount, settings);

  return (
    <section data-testid="cart-panel" className="section-card">
      <div className="section-head">
        <div className="flex items-center gap-2 min-w-0">
          <ShoppingBag data-testid="cart-panel-icon" size={14} className="text-[#0058CC]" />
          <span className="kicker">Draft Order</span>
          <h2>Reservasi 3 hari</h2>
        </div>
      </div>
      <div className="section-body">
        <div className="grid gap-2">
          {cart.length === 0 && (
            <p
              data-testid="empty-cart-message"
              className="rounded-md border border-dashed border-[#E5E5EA] bg-[#FAFBFC] p-3 text-[12px] text-[#6B6B73]"
            >
              Pilih produk dari grid POS untuk mulai membuat order.
            </p>
          )}
          {cart.map((item) => {
            const sp = specialPrices[item.product.id];
            const isSpecial = !!(sp && sp.has_special);
            const unitPrice = isSpecial ? Number(sp.requested_price) : (item.product.price || 0);
            const lineSubtotal = unitPrice * (item.quantity || 0);
            const dp = allowItemDiscount ? Number(item.discount_percent || 0) : 0;
            const lineTotal = lineSubtotal - (lineSubtotal * dp) / 100;
            return (
              <div
                data-testid={`cart-item-${item.product.id}`}
                key={item.product.id}
                className="rounded-md border border-[#EFF0F2] bg-[#FAFBFC] p-2.5"
              >
                <div className="flex items-start justify-between gap-2">
                  <div className="min-w-0">
                    <p
                      data-testid={`cart-item-sku-${item.product.id}`}
                      className="text-[10.5px] font-bold uppercase tracking-wide text-[#0058CC]"
                    >
                      {item.product.sku}
                    </p>
                    <p
                      data-testid={`cart-item-name-${item.product.id}`}
                      className="text-[12.5px] font-semibold truncate"
                    >
                      {item.product.name}
                    </p>
                    {isSpecial && (
                      <p
                        data-testid={`cart-item-special-${item.product.id}`}
                        className="mt-0.5 inline-flex items-center gap-1 rounded-full bg-[#F3E9FA] px-2 py-0.5 text-[9.5px] font-bold text-[#6B219A]"
                      >
                        Harga khusus {formatCurrency(unitPrice)}
                        <span className="font-normal text-[#8E8E93] line-through">{formatCurrency(sp.normal_price)}</span>
                      </p>
                    )}
                  </div>
                  <button
                    data-testid={`remove-cart-item-button-${item.product.id}`}
                    className="icon-button"
                    onClick={() => remove(item.product.id)}
                    aria-label="Remove item"
                  >
                    <XCircle size={14} />
                  </button>
                </div>
                <div className="mt-2 grid grid-cols-[1fr_56px] gap-2">
                  <div>
                    <label className="text-[9px] font-bold uppercase tracking-wide text-[#8E8E93]">Qty</label>
                    <input
                      data-testid={`cart-item-qty-input-${item.product.id}`}
                      className="field"
                      type="number"
                      min="1"
                      value={item.quantity}
                      onChange={(e) => updateQty(item.product.id, e.target.value)}
                    />
                  </div>
                  <div>
                    <label className="text-[9px] font-bold uppercase tracking-wide text-[#8E8E93]">Unit</label>
                    <div
                      data-testid={`cart-item-unit-${item.product.id}`}
                      className="grid h-[34px] place-items-center rounded-md bg-white border border-[#EFF0F2] text-[12px] font-semibold"
                    >
                      {item.product.base_unit}
                    </div>
                  </div>
                </div>
                {allowItemDiscount && (
                  <div className="mt-2 grid grid-cols-[64px_1fr] items-end gap-2">
                    <div>
                      <label className="text-[9px] font-bold uppercase tracking-wide text-[#8E8E93]">Disc %</label>
                      <input
                        data-testid={`cart-item-discount-input-${item.product.id}`}
                        className="field"
                        type="number"
                        min="0"
                        max="100"
                        value={item.discount_percent || 0}
                        onChange={(e) => updateDiscount(item.product.id, e.target.value)}
                      />
                    </div>
                    <div className="text-right">
                      <p className="text-[9px] font-bold uppercase tracking-wide text-[#8E8E93]">Subtotal</p>
                      <p className="text-[12px] font-semibold">
                        {formatCurrency(lineTotal)}
                        {dp > 0 && (
                          <span className="ml-1 text-[10px] text-[#8E8E93] line-through">{formatCurrency(lineSubtotal)}</span>
                        )}
                      </p>
                    </div>
                  </div>
                )}
                <FulfillmentInfo
                  line={allocationLines[item.product.id]}
                  loading={allocationLoading}
                  reqStatus={transferRequests[item.product.id]}
                  onRequestTransfer={onRequestTransfer}
                />
              </div>
            );
          })}
        </div>

        {/* Term pembayaran + diskon order (Fase 1B) */}
        {cart.length > 0 && (
          <div className="mt-3 grid gap-2 rounded-md border border-[#EFF0F2] bg-white p-2.5">
            <div>
              <label className="text-[9px] font-bold uppercase tracking-wide text-[#8E8E93]">Term Pembayaran</label>
              <select
                data-testid="payment-term-select"
                className="field"
                value={paymentTerm}
                onChange={(e) => setPaymentTerm(e.target.value)}
              >
                {paymentTerms.length === 0 && <option value="">Default</option>}
                {paymentTerms.map((t) => (
                  <option key={t.code} value={t.code}>{t.name}</option>
                ))}
              </select>
            </div>
            {allowOrderDiscount && (
              <div>
                <label className="text-[9px] font-bold uppercase tracking-wide text-[#8E8E93]">Diskon Order (%)</label>
                <input
                  data-testid="order-discount-input"
                  className="field"
                  type="number"
                  min="0"
                  max="100"
                  value={orderDiscount}
                  onChange={(e) => setOrderDiscount(Math.max(0, Math.min(100, Number(e.target.value) || 0)))}
                />
              </div>
            )}
          </div>
        )}

        {/* Ringkasan pricing (Fase 1B) */}
        {cart.length > 0 && (
          <button
            data-testid="cart-total-card"
            className="interactive-card mt-2 w-full rounded-md bg-black p-3 text-left text-white"
            onClick={() => onShowDetail({
              title: "Ringkasan Sales Order",
              body: "Harga ditangkap saat order dibuat. PPN & diskon mengikuti pengaturan (Admin -> Pengaturan) dan status PKP entitas.",
              facts: [
                { label: "Item", value: cart.length },
                { label: "Subtotal", value: formatCurrency(p.gross) },
                { label: "Diskon", value: formatCurrency(p.discountTotal) },
                { label: `PPN ${p.ppnRate || 0}%`, value: formatCurrency(p.ppn) },
                { label: "Grand Total", value: formatCurrency(p.grand) },
                { label: "Term", value: paymentTerm || "Default" },
              ],
              target: "sales",
              cta: "Kembali ke draft",
            })}
          >
            <div className="flex items-center gap-1.5">
              <Receipt size={12} className="text-white/70" />
              <p className="text-[10.5px] font-bold uppercase tracking-wide text-white/70">Ringkasan</p>
            </div>
            <div className="mt-1.5 space-y-1 text-[11.5px]">
              <Row label="Subtotal (bruto)" value={formatCurrency(p.gross)} />
              {p.discountTotal > 0 && <Row label="Diskon" value={`- ${formatCurrency(p.discountTotal)}`} />}
              {p.discountTotal > 0 && <Row label="Subtotal netto (DPP)" value={formatCurrency(p.net)} />}
              {p.ppn > 0 && <Row label={`PPN ${p.ppnRate}%`} value={formatCurrency(p.ppn)} />}
              {p.isPkp === false && <Row label="PPN" value="Non-PKP (0)" muted />}
            </div>
            <div className="mt-2 flex items-end justify-between border-t border-white/15 pt-2">
              <p className="text-[10.5px] font-bold uppercase tracking-wide text-white/70">Grand Total</p>
              <p data-testid="cart-grand-total" className="text-[18px] font-bold">{formatCurrency(p.grand)}</p>
            </div>
          </button>
        )}

        {/* Sub-fase 1.6 — opsi backorder bila stok entitas tak cukup */}
        {cart.length > 0 && hasBackorderLine && (
          <div
            data-testid="backorder-option-card"
            className="mt-2 rounded-md border border-[#F5C9A6] bg-[#FFF7EF] p-2.5"
          >
            <div className="flex items-start gap-2">
              <AlertTriangle size={14} className="mt-0.5 shrink-0 text-[#A8221A]" />
              <div className="min-w-0">
                <p className="text-[11.5px] font-semibold text-[#8C4A00]">
                  Stok entitas tidak cukup untuk {formatQty(backorderQtyTotal)} meter.
                </p>
                <label className="mt-1.5 flex cursor-pointer items-center gap-2">
                  <input
                    data-testid="allow-backorder-checkbox"
                    type="checkbox"
                    className="h-3.5 w-3.5 accent-[#0058CC]"
                    checked={allowBackorder}
                    onChange={(e) => setAllowBackorder(e.target.checked)}
                  />
                  <span className="text-[11.5px] font-medium text-[#1C1C1E]">
                    Izinkan backorder (reservasi stok tersedia sekarang, sisanya menunggu barang masuk)
                  </span>
                </label>
              </div>
            </div>
          </div>
        )}

        <button
          data-testid="submit-sales-order-button"
          className="primary-button mt-2 w-full"
          disabled={!selectedCustomer || !selectedAddress || cart.length === 0}
          onClick={() => onSubmitOrder({
            order_discount_percent: orderDiscount,
            payment_term_code: paymentTerm,
            allow_backorder: allowBackorder,
            special_prices: specialPrices,
          })}
        >
          <PackageCheck size={14} />
          {hasBackorderLine && allowBackorder ? "Buat Order + Backorder" : "Buat Sales Order & Reserve"}
        </button>
      </div>
    </section>
  );
}

function Row({ label, value, muted = false }) {
  return (
    <div className="flex items-center justify-between">
      <span className={muted ? "text-white/50" : "text-white/80"}>{label}</span>
      <span className={muted ? "text-white/50" : "font-semibold"}>{value}</span>
    </div>
  );
}

function FulfillmentInfo({ line, loading, reqStatus, onRequestTransfer }) {
  if (!line) {
    if (loading) {
      return (
        <p className="mt-2 text-[10px] text-[#8E8E93]">Mengecek ketersediaan (ATP)…</p>
      );
    }
    return null;
  }
  const meta = modeMeta(line.primary_mode);
  const bo = line.breakdown?.backorder || 0;
  const ic = line.breakdown?.inter_company || 0;
  const source = (line.cross_entity || [])[0];
  return (
    <div
      data-testid={`cart-item-fulfillment-${line.product_id}`}
      className="mt-2 rounded-md border border-[#EFF0F2] bg-white p-2"
    >
      <div className="flex items-center justify-between gap-2">
        <span
          data-testid={`cart-item-mode-${line.product_id}`}
          data-mode={line.primary_mode}
          className={`status-pill ${meta.cls}`}
        >
          {line.primary_mode === "inter_company" && <ArrowLeftRight size={11} />}
          {meta.label}
        </span>
        <span className="text-[10px] text-[#6B6B73] tabular-nums">
          ATP <span className="font-bold text-[#1C1C1E]">{formatQty(line.own_atp)}</span>
        </span>
      </div>
      <div className="mt-1.5 flex flex-wrap gap-x-3 gap-y-0.5 text-[10px] text-[#6B6B73] tabular-nums">
        <span>Stok: <span className="font-semibold text-[#126E2C]">{formatQty(line.own_available)}</span></span>
        <span>Incoming: <span className="font-semibold text-[#8C4A00]">{formatQty(line.own_incoming)}</span></span>
        {ic > 0 && (
          <span>Inter-Co: <span className="font-semibold text-[#6B219A]">{formatQty(ic)}</span></span>
        )}
      </div>
      {bo > 0 && (
        <p className="mt-1 text-[10px] font-semibold text-[#A8221A] tabular-nums">
          Backorder {formatQty(bo)} {line.unit}
        </p>
      )}
      <p className="mt-1 text-[10px] leading-snug text-[#8E8E93]">{line.explanation}</p>
      {line.primary_mode === "inter_company" && ic > 0 && source && (
        <div className="mt-2">
          {reqStatus === "requested" ? (
            <p
              data-testid={`transfer-requested-${line.product_id}`}
              className="rounded-md bg-[#EEF4FF] px-2 py-1.5 text-[10px] font-semibold text-[#0058CC]"
            >
              ✓ Transfer diminta — menunggu approval {source.entity_name}
            </p>
          ) : (
            <button
              type="button"
              data-testid={`request-transfer-${line.product_id}`}
              disabled={reqStatus === "requesting" || !onRequestTransfer}
              onClick={() => onRequestTransfer && onRequestTransfer(line)}
              className="flex w-full items-center justify-center gap-1.5 rounded-md border border-[#C9B6E8] bg-[#F7F2FE] px-2 py-1.5 text-[10px] font-bold text-[#6B219A] transition hover:bg-[#F0E8FB] disabled:opacity-50"
            >
              <ArrowLeftRight size={12} />
              {reqStatus === "requesting"
                ? "Memproses…"
                : reqStatus === "error"
                ? "Gagal — coba lagi"
                : `Minta Transfer dari ${source.entity_name} (${formatQty(ic)} ${line.unit})`}
            </button>
          )}
        </div>
      )}
    </div>
  );
}
