import { useEffect, useState } from "react";
import { Plus, Package } from "lucide-react";
import axios from "../../services/apiClient";
import { formatCurrency } from "../../utils/formatters";
import { getStatusBadge } from "./po/poUtils";
import POCreateForm from "./po/POCreateForm";
import PODetailPanel from "./po/PODetailPanel";

/**
 * PurchaseOrderManagement
 *
 * Manage Purchase Orders untuk inbound receiving workflow.
 * Create PO → Auto-create inbound tasks → Staff scan & receive.
 *
 * Sub-komponen (colocated di po/):
 *   - POCreateForm    — form buat PO baru
 *   - PODetailPanel   — panel detail PO dipilih
 *   - poUtils         — getStatusBadge helper
 */
export default function PurchaseOrderManagement({ user, onApprovePO }) {
  const [pos, setPos] = useState([]);
  const [products, setProducts] = useState([]);
  const [warehouses, setWarehouses] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [selectedPO, setSelectedPO] = useState(null);

  const emptyForm = {
    supplier_name: "", supplier_contact: "", warehouse_id: "",
    items: [], expected_delivery_date: "", notes: "",
    created_by: user?.name || "Admin",
  };
  const [formData, setFormData] = useState(emptyForm);
  const [newItem, setNewItem] = useState({ product_id: "", quantity: 0, unit: "meter", price: 0 });

  useEffect(() => { fetchPOs(); fetchMasterData(); }, []); // eslint-disable-line

  const fetchPOs = async () => {
    setLoading(true);
    try {
      const res = await axios.get("/api/purchase-orders");
      setPos(res.data);
    } catch (e) {
      console.error("Error fetching POs:", e);
    } finally {
      setLoading(false);
    }
  };

  const fetchMasterData = async () => {
    try {
      const [pRes, wRes] = await Promise.all([
        axios.get("/api/products"),
        axios.get("/api/warehouses"),
      ]);
      setProducts(pRes.data);
      setWarehouses(wRes.data);
    } catch (e) {
      console.error("Error fetching master data:", e);
    }
  };

  const handleAddItem = () => {
    if (!newItem.product_id || newItem.quantity <= 0) {
      alert("Pilih produk dan masukkan qty valid"); return;
    }
    const product = products.find((p) => p.id === newItem.product_id);
    setFormData({
      ...formData,
      items: [...formData.items, {
        ...newItem,
        price: newItem.price > 0 ? newItem.price : product?.price || 0,
      }],
    });
    setNewItem({ product_id: "", quantity: 0, unit: "meter", price: 0 });
  };

  const handleRemoveItem = (index) => {
    setFormData({ ...formData, items: formData.items.filter((_, i) => i !== index) });
  };

  const handleCreatePO = async () => {
    if (!formData.supplier_name || !formData.warehouse_id) {
      alert("Supplier name dan warehouse wajib diisi"); return;
    }
    if (formData.items.length === 0) {
      alert("Tambahkan minimal 1 item"); return;
    }
    try {
      const res = await axios.post("/api/purchase-orders", formData);
      const po = res.data;
      if (po.approval_required) {
        alert(`Purchase Order ${po.po_number} dibuat. Butuh APPROVAL role '${po.required_approval_role}' sebelum inbound task dibuat.`);
      } else {
        alert(`Purchase Order ${po.po_number} dibuat & inbound tasks otomatis dibuat!`);
      }
      setShowCreateForm(false);
      setFormData(emptyForm);
      fetchPOs();
    } catch (e) {
      alert(e.response?.data?.detail || "Gagal membuat PO");
    }
  };

  const handleViewDetail = async (poId) => {
    try {
      const res = await axios.get(`/api/purchase-orders/${poId}`);
      setSelectedPO(res.data);
    } catch {
      alert("Gagal load PO detail");
    }
  };

  const handleCancelPO = async (poId) => {
    if (!window.confirm("Yakin ingin membatalkan PO ini?")) return;
    try {
      await axios.post(`/api/purchase-orders/${poId}/cancel`);
      alert("PO berhasil dibatalkan");
      fetchPOs();
      setSelectedPO(null);
    } catch (e) {
      alert(e.response?.data?.detail || "Gagal cancel PO");
    }
  };

  const handleApprovePO = async (poId) => {
    if (!onApprovePO) return;
    const result = await onApprovePO(poId);
    if (result) { await fetchPOs(); await handleViewDetail(poId); }
  };

  const handleCloseForm = () => {
    setShowCreateForm(false);
    setFormData(emptyForm);
  };

  return (
    <div data-testid="po-management-panel">
      {/* Top bar */}
      <div className="section-card mb-3">
        <div className="section-head">
          <div className="flex items-center gap-2 min-w-0">
            <span className="kicker">Purchasing</span>
            <h2 data-testid="panel-title">Purchase Orders</h2>
          </div>
          <button data-testid="create-po-button"
            onClick={() => setShowCreateForm(!showCreateForm)}
            className="primary-button">
            <Plus size={13} /> {showCreateForm ? "Tutup Form" : "Buat PO"}
          </button>
        </div>
      </div>

      {/* Create Form */}
      {showCreateForm && (
        <POCreateForm
          formData={formData} setFormData={setFormData}
          newItem={newItem} setNewItem={setNewItem}
          products={products} warehouses={warehouses}
          onSubmit={handleCreatePO} onCancel={handleCloseForm}
          onAddItem={handleAddItem} onRemoveItem={handleRemoveItem}
        />
      )}

      {/* Two-panel: PO table + detail */}
      <div className="grid gap-3 lg:grid-cols-[1fr_360px]">
        {/* PO Table */}
        <div className="section-card">
          <div className="overflow-hidden">
            <div className="grid grid-cols-[60px_1fr_120px_90px_60px] px-3 py-1.5 bg-[#FAFBFC] text-[10px] font-bold uppercase text-[#6B6B73] border-b border-[#EFF0F2]">
              <span>Nomor</span><span>Supplier</span><span>Gudang</span><span>Items</span><span>Status</span>
            </div>
            {loading ? (
              <div className="py-8 text-center text-[12px] text-[#6B6B73]">Loading...</div>
            ) : pos.length === 0 ? (
              <div className="py-10 text-center text-[12px] text-[#6B6B73]">
                <Package className="mx-auto mb-2 text-gray-300" size={28} />
                <p>Belum ada Purchase Order</p>
              </div>
            ) : (
              <div className="divide-y divide-[#EFF0F2] max-h-[560px] overflow-y-auto">
                {pos.map((po) => (
                  <div key={po.id} data-testid={`po-card-${po.id}`}
                    className={`grid grid-cols-[60px_1fr_120px_90px_60px] items-center px-3 py-2.5 cursor-pointer hover:bg-[#FAFBFC] transition-colors ${selectedPO?.id === po.id ? "bg-[#EFF4FF] border-l-2 border-[#007AFF]" : ""}`}
                    onClick={() => handleViewDetail(po.id)}>
                    <p data-testid={`po-number-${po.id}`} className="text-[12px] font-bold text-[#007AFF]">{po.po_number}</p>
                    <div className="min-w-0">
                      <p data-testid={`po-supplier-${po.id}`} className="text-[11.5px] font-semibold truncate">{po.supplier_name}</p>
                      <p className="text-[10.5px] text-[#6B6B73]">{formatCurrency(po.total_amount)}</p>
                    </div>
                    <p className="text-[11px] text-[#3C3C43] truncate">{po.warehouse_name}</p>
                    <p className="text-[11.5px] text-[#6B6B73]">{po.items?.length || 0} item</p>
                    {getStatusBadge(po.status)}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* PO Detail Panel */}
        <PODetailPanel
          po={selectedPO}
          onClose={() => setSelectedPO(null)}
          onApprove={handleApprovePO}
          onCancel={handleCancelPO}
        />
      </div>
    </div>
  );
}
