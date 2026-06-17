/** InitialStockForm — manual initial-stock (roll) entry (admin/manager only). */
import { X } from "lucide-react";

export default function InitialStockForm({ stockForm, setStockForm, products = [], warehouses = [], entities = [], submitting, onSubmit, onClose }) {
  return (
    <div className="rounded-xl border border-[#E5E5EA] bg-white p-3">
      <div className="flex items-center justify-between mb-2.5">
        <p className="text-[12px] font-bold">Tambah Stok Awal (Roll)</p>
        <button onClick={onClose} data-testid="close-stock-form"><X size={13} className="text-[#6B6B73]" /></button>
      </div>
      <div className="grid grid-cols-2 gap-2 sm:grid-cols-3">
        <div className="col-span-2 sm:col-span-1">
          <label className="block text-[10px] font-semibold text-[#6B6B73] mb-1">Produk *</label>
          <select value={stockForm.product_id} data-testid="stock-product-select" onChange={e => setStockForm({ ...stockForm, product_id: e.target.value })} className="field">
            <option value="">Pilih produk...</option>
            {products.map(p => <option key={p.id} value={p.id}>{p.sku} — {p.name}</option>)}
          </select>
        </div>
        <div>
          <label className="block text-[10px] font-semibold text-[#6B6B73] mb-1">Pemilik (Entitas) *</label>
          <select value={stockForm.owner_entity_id} data-testid="stock-owner-select" onChange={e => setStockForm({ ...stockForm, owner_entity_id: e.target.value })} className="field">
            <option value="">Pilih entitas...</option>
            {entities.map(en => <option key={en.id} value={en.id}>{en.short_name || en.legal_name}</option>)}
          </select>
        </div>
        <div>
          <label className="block text-[10px] font-semibold text-[#6B6B73] mb-1">Gudang *</label>
          <select value={stockForm.warehouse_id} data-testid="stock-warehouse-select" onChange={e => setStockForm({ ...stockForm, warehouse_id: e.target.value })} className="field">
            <option value="">Pilih gudang...</option>
            {warehouses.map(w => <option key={w.id} value={w.id}>{w.name}</option>)}
          </select>
        </div>
        <div>
          <label className="block text-[10px] font-semibold text-[#6B6B73] mb-1">Panjang (Qty) *</label>
          <input type="number" data-testid="stock-qty-input" value={stockForm.quantity} onChange={e => setStockForm({ ...stockForm, quantity: parseFloat(e.target.value) || 0 })} className="field tabular-nums" placeholder="0" />
        </div>
        <div>
          <label className="block text-[10px] font-semibold text-[#6B6B73] mb-1">Unit</label>
          <input type="text" value={stockForm.unit} onChange={e => setStockForm({ ...stockForm, unit: e.target.value })} className="field" placeholder="meter" />
        </div>
        <div>
          <label className="block text-[10px] font-semibold text-[#6B6B73] mb-1">Lot *</label>
          <input type="text" data-testid="stock-lot-input" value={stockForm.lot} onChange={e => setStockForm({ ...stockForm, lot: e.target.value })} className="field" placeholder="LOT-2026-001" />
        </div>
        <div>
          <label className="block text-[10px] font-semibold text-[#6B6B73] mb-1">Grade</label>
          <select value={stockForm.grade} data-testid="stock-grade-select" onChange={e => setStockForm({ ...stockForm, grade: e.target.value })} className="field">
            <option value="A">A</option>
            <option value="B">B</option>
            <option value="C">C</option>
            <option value="Reject">Reject</option>
          </select>
        </div>
        <div>
          <label className="block text-[10px] font-semibold text-[#6B6B73] mb-1">Roll No</label>
          <input type="text" value={stockForm.roll_no} onChange={e => setStockForm({ ...stockForm, roll_no: e.target.value })} className="field" placeholder="(auto)" />
        </div>
        <div>
          <label className="block text-[10px] font-semibold text-[#6B6B73] mb-1">Batch</label>
          <input type="text" value={stockForm.batch} onChange={e => setStockForm({ ...stockForm, batch: e.target.value })} className="field" />
        </div>
      </div>
      <div className="flex gap-2 mt-3">
        <button onClick={onSubmit} disabled={submitting} data-testid="submit-stock-button"
          className="flex-1 bg-[#34C759] hover:bg-[#28A745] text-white rounded-lg px-4 py-2 text-[12px] font-semibold disabled:opacity-50">
          Simpan Roll
        </button>
        <button onClick={onClose} className="secondary-button">Batal</button>
      </div>
    </div>
  );
}
