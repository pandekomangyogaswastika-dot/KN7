import { FileText, CheckCircle, XCircle, AlertCircle } from "lucide-react";
import { formatCurrency } from "../../../utils/formatters";
import { getStatusBadge } from "./poUtils";

/**
 * PODetailPanel — panel kanan detail PO yang dipilih.
 * Props: po, onClose, onApprove, onCancel
 */
export default function PODetailPanel({ po, onClose, onApprove, onCancel }) {
  if (!po) {
    return (
      <div className="section-card flex items-center justify-center min-h-[200px] border-dashed">
        <div className="text-center p-6">
          <FileText size={28} className="mx-auto mb-2 text-gray-300" />
          <p className="text-[12px] text-[#6B6B73]">Pilih PO untuk lihat detail</p>
        </div>
      </div>
    );
  }

  return (
    <div className="section-card self-start">
      <div className="section-head">
        <div className="min-w-0">
          <p className="text-[10px] font-bold uppercase text-[#0058CC]">{po.po_number}</p>
          <div className="mt-0.5">{getStatusBadge(po.status)}</div>
        </div>
        <button className="icon-button" onClick={onClose}><XCircle size={14} /></button>
      </div>

      <div className="section-body space-y-3">
        {/* Supplier + Gudang */}
        <div className="grid grid-cols-2 gap-2 text-[11.5px]">
          <div className="rounded-md border border-[#EFF0F2] bg-[#FAFBFC] p-2">
            <p className="text-[10px] text-[#6B6B73] uppercase font-semibold mb-0.5">Supplier</p>
            <p className="font-semibold">{po.supplier_name}</p>
            <p className="text-[10.5px] text-[#6B6B73]">{po.supplier_contact}</p>
          </div>
          <div className="rounded-md border border-[#EFF0F2] bg-[#FAFBFC] p-2">
            <p className="text-[10px] text-[#6B6B73] uppercase font-semibold mb-0.5">Gudang</p>
            <p className="font-semibold">{po.warehouse_name}</p>
            <p className="text-[10.5px] text-[#6B6B73]">{po.warehouse_city}</p>
          </div>
        </div>

        {/* Items */}
        <div className="rounded-md border border-[#EFF0F2] overflow-hidden">
          <div className="px-2.5 py-1.5 bg-[#FAFBFC] text-[10px] font-bold uppercase text-[#6B6B73] border-b border-[#EFF0F2]">
            Items ({po.items?.length || 0})
          </div>
          {po.items?.map((item, i) => (
            <div key={i} className="px-2.5 py-1.5 border-b border-[#EFF0F2] last:border-0 text-[11px]">
              <div className="flex justify-between">
                <p className="font-semibold truncate">{item.sku}</p>
                <p className="font-bold">{formatCurrency(item.subtotal || 0)}</p>
              </div>
              <p className="text-[10.5px] text-[#6B6B73]">
                Expected: {item.quantity} {item.unit} · Rcv: {item.received_qty || 0}
              </p>
            </div>
          ))}
        </div>

        {/* Inbound Tasks */}
        {po.inbound_tasks?.length > 0 && (
          <div className="rounded-md border border-[#EFF0F2] overflow-hidden">
            <div className="px-2.5 py-1.5 bg-[#FAFBFC] text-[10px] font-bold uppercase text-[#6B6B73] border-b border-[#EFF0F2]">
              Inbound Tasks
            </div>
            {po.inbound_tasks.map((task) => (
              <div key={task.id} className="flex items-center justify-between px-2.5 py-1.5 border-b border-[#EFF0F2] last:border-0">
                <div>
                  <p className="text-[11.5px] font-semibold">{task.sku}</p>
                  <p className="text-[10.5px] text-[#6B6B73]">Rcv: {task.received_qty || 0}/{task.expected_qty}</p>
                </div>
                {getStatusBadge(task.status)}
              </div>
            ))}
          </div>
        )}

        {/* Total + approval badge */}
        <div className="flex items-center justify-between rounded-md border border-[#EFF0F2] bg-[#FAFBFC] p-2 text-[11.5px]">
          <span className="text-[10px] font-bold uppercase text-[#6B6B73]">Total PO</span>
          <span className="text-[13px] font-bold text-[#007AFF]">{formatCurrency(po.total_amount)}</span>
        </div>
        {po.status === "waiting_approval" && po.required_approval_role && (
          <div data-testid="po-approval-badge"
            className="flex items-center gap-2 rounded-md border border-[#FFE2B8] bg-[#FFF7EC] px-2.5 py-1.5 text-[11px] text-[#9A5B00]">
            <AlertCircle size={13} />
            <span>Butuh approval role <b className="uppercase">{po.required_approval_role}</b> sebelum inbound task dibuat.</span>
          </div>
        )}

        {/* Actions */}
        <div className="flex flex-col gap-1.5">
          {po.status === "waiting_approval" && (
            <button data-testid="approve-po-button" onClick={() => onApprove(po.id)}
              className="primary-button justify-center">
              <CheckCircle size={13} /> Approve PO
            </button>
          )}
          {po.status === "completed" && (
            <button data-testid="view-receiving-goods-doc"
              onClick={() => window.open(`/api/inbound/po/${po.id}/receiving-goods-document`, "_blank")}
              className="primary-button justify-center">
              <FileText size={13} /> Receiving Goods Document
            </button>
          )}
          {["waiting_approval", "pending", "receiving"].includes(po.status) && (
            <button data-testid="cancel-po-button" onClick={() => onCancel(po.id)}
              className="danger-button justify-center">
              Cancel PO
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
