/**
 * poUtils.jsx — shared helpers untuk PurchaseOrderManagement sub-komponen.
 */

export function getStatusBadge(status) {
  const statusMap = {
    waiting_approval: { label: "Waiting Approval", cls: "bg-amber-100 text-amber-700" },
    pending:          { label: "Pending",           cls: "bg-yellow-100 text-yellow-700" },
    receiving:        { label: "Receiving",         cls: "bg-blue-100 text-blue-700" },
    completed:        { label: "Completed",         cls: "bg-green-100 text-green-700" },
    partial:          { label: "Partial",           cls: "bg-orange-100 text-orange-700" },
    cancelled:        { label: "Cancelled",         cls: "bg-gray-200 text-gray-500" },
  };
  const b = statusMap[status] || { label: status, cls: "bg-gray-200 text-gray-700" };
  return (
    <span data-testid={`po-status-badge-${status}`} className={`rounded px-1.5 py-0.5 text-[10px] font-semibold ${b.cls}`}>
      {b.label}
    </span>
  );
}
