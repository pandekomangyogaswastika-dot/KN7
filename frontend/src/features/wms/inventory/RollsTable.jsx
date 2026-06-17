/** RollsTable — daftar roll fisik (Roll-as-SSOT, Fase 0.5). */
import { Layers } from "lucide-react";
import { formatQty, RollStatusBadge } from "./inventoryConstants";

export default function RollsTable({ loading, rolls = [] }) {
  return (
    <div className="bg-white rounded-xl border border-[#EFF0F2] overflow-hidden" data-testid="rolls-table">
      <div className="overflow-x-auto">
        <table className="w-full text-[11.5px]">
          <thead>
            <tr className="bg-[#FAFBFC] border-b border-[#EFF0F2]">
              <th className="text-left px-3 py-2 text-[10px] font-bold uppercase tracking-wide text-[#6B6B73]">Roll No</th>
              <th className="text-left px-3 py-2 text-[10px] font-bold uppercase tracking-wide text-[#6B6B73]">Produk</th>
              <th className="text-left px-3 py-2 text-[10px] font-bold uppercase tracking-wide text-[#6B6B73]">Pemilik</th>
              <th className="text-left px-3 py-2 text-[10px] font-bold uppercase tracking-wide text-[#6B6B73]">Gudang</th>
              <th className="text-left px-3 py-2 text-[10px] font-bold uppercase tracking-wide text-[#6B6B73]">Lot</th>
              <th className="text-center px-3 py-2 text-[10px] font-bold uppercase tracking-wide text-[#6B6B73]">Grade</th>
              <th className="text-right px-3 py-2 text-[10px] font-bold uppercase tracking-wide text-[#6B6B73]">Panjang</th>
              <th className="px-3 py-2 text-[10px] font-bold uppercase tracking-wide text-[#6B6B73]">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[#EFF0F2]">
            {loading && (
              <tr><td colSpan={8} className="text-center py-8 text-[12px] text-[#6B6B73]">Loading...</td></tr>
            )}
            {!loading && rolls.length === 0 && (
              <tr>
                <td colSpan={8} className="text-center py-10">
                  <Layers size={28} className="mx-auto mb-2 text-gray-300" />
                  <p className="text-[12px] text-[#6B6B73]">Tidak ada roll</p>
                </td>
              </tr>
            )}
            {rolls.map((r) => (
              <tr key={r.id} data-testid={`roll-row-${r.id}`} className="hover:bg-[#FAFBFC] transition-colors">
                <td className="px-3 py-2 font-bold text-[#007AFF] tabular-nums">{r.roll_no}</td>
                <td className="px-3 py-2">
                  <p className="font-medium">{r.product_name}</p>
                  <p className="text-[10px] text-[#8E8E93]">{r.sku}</p>
                </td>
                <td className="px-3 py-2">
                  <span className="inline-flex items-center rounded-md bg-[#EEF2FF] px-1.5 py-0.5 text-[10px] font-semibold text-[#4338CA]">
                    {r.owner_entity_name}
                  </span>
                </td>
                <td className="px-3 py-2">
                  <p className="font-medium">{r.warehouse_name}</p>
                  <p className="text-[10px] text-[#8E8E93]">{r.warehouse_city}</p>
                </td>
                <td className="px-3 py-2 font-mono text-[10.5px] text-[#3C3C43]">{r.lot}</td>
                <td className="px-3 py-2 text-center font-semibold">{r.grade || "-"}</td>
                <td className="px-3 py-2 text-right font-bold tabular-nums">
                  {formatQty(r.length_remaining)} <span className="text-[9px] text-[#8E8E93]">{r.unit}</span>
                </td>
                <td className="px-3 py-2"><RollStatusBadge status={r.status} /></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
