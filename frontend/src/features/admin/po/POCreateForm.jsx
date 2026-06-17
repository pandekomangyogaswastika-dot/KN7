import { Plus, XCircle } from "lucide-react";
import { formatCurrency } from "../../../utils/formatters";

/**
 * POCreateForm — form buat Purchase Order baru (collapsible).
 * Props: formData, setFormData, newItem, setNewItem,
 *        products, warehouses, onSubmit, onCancel, onAddItem, onRemoveItem
 */
export default function POCreateForm({
  formData, setFormData,
  newItem, setNewItem,
  products, warehouses,
  onSubmit, onCancel,
  onAddItem, onRemoveItem,
}) {
  return (
    <div data-testid="create-po-form" className="section-card mb-3">
      <div className="section-head">
        <h2 className="text-[13px] font-bold">Buat Purchase Order Baru</h2>
      </div>
      <div className="section-body space-y-3">
        {/* Header fields */}
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="block text-[10.5px] font-semibold text-[#6B6B73] mb-1">Supplier Name *</label>
            <input data-testid="supplier-name-input" type="text" value={formData.supplier_name}
              onChange={(e) => setFormData({ ...formData, supplier_name: e.target.value })}
              className="field" placeholder="PT Supplier Textile" />
          </div>
          <div>
            <label className="block text-[10.5px] font-semibold text-[#6B6B73] mb-1">Supplier Contact</label>
            <input data-testid="supplier-contact-input" type="text" value={formData.supplier_contact}
              onChange={(e) => setFormData({ ...formData, supplier_contact: e.target.value })}
              className="field" placeholder="081234567890" />
          </div>
          <div>
            <label className="block text-[10.5px] font-semibold text-[#6B6B73] mb-1">Warehouse *</label>
            <select data-testid="warehouse-select" value={formData.warehouse_id}
              onChange={(e) => setFormData({ ...formData, warehouse_id: e.target.value })}
              className="field">
              <option value="">Pilih Warehouse</option>
              {warehouses.map((wh) => (
                <option key={wh.id} value={wh.id}>{wh.name} ({wh.code})</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-[10.5px] font-semibold text-[#6B6B73] mb-1">Expected Delivery</label>
            <input data-testid="delivery-date-input" type="date" value={formData.expected_delivery_date}
              onChange={(e) => setFormData({ ...formData, expected_delivery_date: e.target.value })}
              className="field" />
          </div>
        </div>

        <div>
          <label className="block text-[10.5px] font-semibold text-[#6B6B73] mb-1">Notes</label>
          <textarea data-testid="po-notes-input" value={formData.notes}
            onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
            className="field" rows="2" placeholder="Catatan tambahan..." />
        </div>

        {/* Add Item row */}
        <div className="bg-[#FAFBFC] rounded-md border border-[#EFF0F2] p-2.5">
          <p className="text-[10.5px] font-bold uppercase text-[#6B6B73] mb-2">Tambah Item</p>
          <div className="grid grid-cols-[1fr_80px_60px_100px_auto] gap-2">
            <select data-testid="item-product-select" value={newItem.product_id}
              onChange={(e) => setNewItem({ ...newItem, product_id: e.target.value })}
              className="field">
              <option value="">Pilih Produk</option>
              {products.map((p) => (
                <option key={p.id} value={p.id}>{p.sku} - {p.name}</option>
              ))}
            </select>
            <input data-testid="item-qty-input" type="number" placeholder="Qty"
              value={newItem.quantity}
              onChange={(e) => setNewItem({ ...newItem, quantity: parseFloat(e.target.value) || 0 })}
              className="field" />
            <input data-testid="item-unit-input" type="text" placeholder="Unit"
              value={newItem.unit}
              onChange={(e) => setNewItem({ ...newItem, unit: e.target.value })}
              className="field" />
            <input data-testid="item-price-input" type="number" placeholder="Harga"
              value={newItem.price}
              onChange={(e) => setNewItem({ ...newItem, price: parseFloat(e.target.value) || 0 })}
              className="field" />
            <button data-testid="add-item-button" onClick={onAddItem}
              className="primary-button !px-3">
              <Plus size={13} />
            </button>
          </div>
        </div>

        {/* Items list */}
        {formData.items.length > 0 && (
          <div className="rounded-md border border-[#EFF0F2] overflow-hidden">
            <div className="grid grid-cols-[1fr_80px_80px_30px] px-2.5 py-1.5 bg-[#FAFBFC] text-[10px] font-bold uppercase text-[#6B6B73] border-b border-[#EFF0F2]">
              <span>Produk</span><span>Qty</span><span>Harga</span><span></span>
            </div>
            {formData.items.map((item, i) => {
              const p = products.find((pr) => pr.id === item.product_id);
              return (
                <div key={i} data-testid={`po-item-row-${i}`}
                  className="grid grid-cols-[1fr_80px_80px_30px] items-center px-2.5 py-1.5 border-b border-[#EFF0F2] last:border-0 text-[11.5px]">
                  <span className="truncate">{p?.sku} — {p?.name}</span>
                  <span className="font-semibold">{item.quantity} {item.unit}</span>
                  <span>{formatCurrency(item.price)}</span>
                  <button data-testid={`remove-item-${i}`} onClick={() => onRemoveItem(i)}
                    className="text-red-400 hover:text-red-600">
                    <XCircle size={13} />
                  </button>
                </div>
              );
            })}
          </div>
        )}

        <div className="flex gap-2">
          <button data-testid="submit-po-button" onClick={onSubmit}
            className="flex-1 primary-button justify-center">
            Buat PO & Auto-create Inbound Tasks
          </button>
          <button data-testid="cancel-form-button" onClick={onCancel}
            className="secondary-button">
            Batal
          </button>
        </div>
      </div>
    </div>
  );
}
