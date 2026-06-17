import { useEffect, useMemo, useRef, useState } from "react";
import axios, { API } from "../../services/apiClient";
import {
  BadgePercent, RefreshCw, Search, Plus, Check, X, Send, Paperclip,
  Trash2, Eye, Clock3, CheckCircle2, XCircle, Pencil,
} from "lucide-react";
import { formatCurrency, formatQty } from "../../utils/formatters";

/**
 * Approval Harga Khusus (Sub-fase 1.7 — Special Price / Approval Harga).
 * Sales mengajukan harga nego per customer+product → upload bukti → manager/admin
 * approve/reject. Harga disetujui dipakai otomatis di POS (override harga normal).
 * Koleksi: price_approvals (pra_). Respons BE = bare object/array.
 */

const STATUS_META = {
  draft: { label: "Draft", icon: Pencil },
  pending: { label: "Menunggu", icon: Clock3 },
  approved: { label: "Disetujui", icon: CheckCircle2 },
  rejected: { label: "Ditolak", icon: XCircle },
};

const FILTERS = [
  { id: "all", label: "Semua" },
  { id: "pending", label: "Menunggu" },
  { id: "approved", label: "Disetujui" },
  { id: "rejected", label: "Ditolak" },
  { id: "draft", label: "Draft" },
];

const EMPTY_FORM = { customer_id: "", product_id: "", requested_price: "", min_quantity: "", valid_until: "", reason: "" };

export default function PriceApprovals({ currentUser = {} }) {
  const role = (currentUser.role || "").toLowerCase();
  const canApprove = ["manager", "admin"].includes(role);

  const [rows, setRows] = useState([]);
  const [customers, setCustomers] = useState([]);
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [filter, setFilter] = useState("all");
  const [search, setSearch] = useState("");
  const [busyId, setBusyId] = useState("");

  // form (create / edit)
  const [showForm, setShowForm] = useState(false);
  const [editId, setEditId] = useState("");
  const [form, setForm] = useState(EMPTY_FORM);
  const [formErr, setFormErr] = useState("");

  // decision (approve/reject)
  const [decideFor, setDecideFor] = useState(""); // `${id}:${mode}`
  const [decisionNotes, setDecisionNotes] = useState("");

  const fileInputs = useRef({});

  const load = async () => {
    setLoading(true);
    setError("");
    try {
      const [pa, cu, pr] = await Promise.all([
        axios.get(`${API}/price-approvals`),
        axios.get(`${API}/customers`),
        axios.get(`${API}/products`),
      ]);
      setRows(Array.isArray(pa.data) ? pa.data : []);
      setCustomers(Array.isArray(cu.data) ? cu.data : []);
      setProducts(Array.isArray(pr.data) ? pr.data : []);
    } catch (e) {
      setError(e.response?.data?.detail || "Gagal memuat data approval harga.");
      setRows([]);
    } finally {
      setLoading(false);
    }
  };

  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(() => { load(); }, []);

  const selectedProduct = useMemo(
    () => products.find((p) => p.id === form.product_id),
    [products, form.product_id],
  );

  const resetForm = () => { setForm(EMPTY_FORM); setEditId(""); setShowForm(false); setFormErr(""); };

  const openCreate = () => { setForm(EMPTY_FORM); setEditId(""); setFormErr(""); setShowForm(true); };

  const openEdit = (r) => {
    setEditId(r.id);
    setForm({
      customer_id: r.customer_id, product_id: r.product_id,
      requested_price: String(r.requested_price ?? ""),
      min_quantity: String(r.min_quantity ?? ""),
      valid_until: (r.valid_until || "").slice(0, 10),
      reason: r.reason || "",
    });
    setFormErr("");
    setShowForm(true);
  };

  const submitForm = async (submitNow) => {
    setFormErr("");
    const price = parseFloat(form.requested_price);
    if (!form.customer_id || !form.product_id) { setFormErr("Pilih customer dan produk."); return; }
    if (!price || price <= 0) { setFormErr("Harga khusus harus lebih dari 0."); return; }
    setBusyId("form");
    try {
      if (editId) {
        await axios.patch(`${API}/price-approvals/${editId}`, {
          data: {
            requested_price: price,
            min_quantity: parseFloat(form.min_quantity) || 0,
            valid_until: form.valid_until || "",
            reason: form.reason || "",
          },
        });
      } else {
        await axios.post(`${API}/price-approvals`, {
          customer_id: form.customer_id,
          product_id: form.product_id,
          requested_price: price,
          min_quantity: parseFloat(form.min_quantity) || 0,
          valid_until: form.valid_until || "",
          reason: form.reason || "",
          submit_now: !!submitNow,
        });
      }
      resetForm();
      await load();
    } catch (e) {
      setFormErr(e.response?.data?.detail || "Gagal menyimpan pengajuan.");
    } finally {
      setBusyId("");
    }
  };

  const runAction = async (id, fn) => {
    setBusyId(id);
    setError("");
    try {
      await fn();
      setDecideFor(""); setDecisionNotes("");
      await load();
    } catch (e) {
      setError(e.response?.data?.detail || "Aksi gagal diproses.");
    } finally {
      setBusyId("");
    }
  };

  const submitApproval = (id) => runAction(id, () => axios.post(`${API}/price-approvals/${id}/submit`, {}));
  const approveApproval = (id, notes) => runAction(id, () => axios.post(`${API}/price-approvals/${id}/approve`, { decision_notes: notes }));
  const rejectApproval = (id, notes) => runAction(id, () => axios.post(`${API}/price-approvals/${id}/reject`, { decision_notes: notes }));

  const removeApproval = async (id) => {
    setBusyId(id);
    try {
      await axios.delete(`${API}/price-approvals/${id}`);
      await load();
    } catch (e) {
      setError(e.response?.data?.detail || "Gagal menghapus pengajuan.");
    } finally {
      setBusyId("");
    }
  };

  const uploadFile = async (id, file) => {
    if (!file) return;
    setBusyId(id);
    setError("");
    try {
      const fd = new FormData();
      fd.append("file", file);
      await axios.post(`${API}/price-approvals/${id}/attachments`, fd, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      await load();
    } catch (e) {
      setError(e.response?.data?.detail || "Gagal mengunggah bukti.");
    } finally {
      setBusyId("");
    }
  };

  const viewAttachment = async (id, att) => {
    try {
      const res = await axios.get(`${API}/price-approvals/${id}/attachments/${att.id}/download`, { responseType: "blob" });
      const url = URL.createObjectURL(res.data);
      window.open(url, "_blank", "noopener");
      setTimeout(() => URL.revokeObjectURL(url), 60000);
    } catch (e) {
      setError("Gagal membuka lampiran.");
    }
  };

  const deleteAttachment = async (id, attId) => {
    setBusyId(id);
    try {
      await axios.delete(`${API}/price-approvals/${id}/attachments/${attId}`);
      await load();
    } catch (e) {
      setError("Gagal menghapus lampiran.");
    } finally {
      setBusyId("");
    }
  };

  const isEditable = (r) => ["draft", "pending"].includes(r.status);

  const filtered = useMemo(() => rows.filter((r) => {
    if (filter !== "all" && r.status !== filter) return false;
    const hay = `${r.customer_name} ${r.product_name} ${r.sku}`.toLowerCase();
    return hay.includes(search.toLowerCase());
  }), [rows, filter, search]);

  const counts = useMemo(() => ({
    pending: rows.filter((r) => r.status === "pending").length,
  }), [rows]);

  return (
    <div data-testid="price-approvals-view" className="grid gap-4">
      <section className="section-card">
        <div className="section-head">
          <div className="flex items-center gap-2 min-w-0">
            <BadgePercent size={15} className="text-[#6B219A]" />
            <span className="kicker">Sales</span>
            <h2 data-testid="price-approvals-title">Approval Harga Khusus</h2>
          </div>
          <div className="flex items-center gap-2">
            <div className="flex items-center gap-2 rounded-md border border-[#E5E5EA] bg-white px-2 py-1.5 min-w-[180px]">
              <Search size={14} className="text-[#6B6B73]" />
              <input
                data-testid="price-approvals-search"
                className="w-full bg-transparent text-[13px] outline-none"
                placeholder="Cari customer / produk..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />
            </div>
            <button
              data-testid="price-approvals-new"
              className="flex items-center gap-1.5 rounded-md bg-[#6B219A] px-3 py-1.5 text-[12px] font-bold text-white transition hover:bg-[#581580]"
              onClick={openCreate}
            >
              <Plus size={14} /> Ajukan
            </button>
            <button data-testid="price-approvals-refresh" className="icon-button" onClick={load} aria-label="Muat ulang">
              <RefreshCw size={14} className={loading ? "animate-spin" : ""} />
            </button>
          </div>
        </div>
        <div className="flex flex-wrap items-center gap-2 px-4 py-2">
          {FILTERS.map((f) => (
            <button
              key={f.id}
              data-testid={`price-approvals-filter-${f.id}`}
              onClick={() => setFilter(f.id)}
              className={`rounded-full px-3 py-1 text-[11px] font-semibold transition ${
                filter === f.id ? "bg-[#1C1C1E] text-white" : "bg-[#F2F2F7] text-[#3C3C43] hover:bg-[#E5E5EA]"
              }`}
            >
              {f.label}
              {f.id === "pending" && counts.pending > 0 && (
                <span className="ml-1 rounded-full bg-[#FF9500] px-1.5 text-[9px] text-white">{counts.pending}</span>
              )}
            </button>
          ))}
        </div>
      </section>

      {/* Form ajukan / edit */}
      {showForm && (
        <section data-testid="price-approvals-form" className="section-card p-4">
          <div className="mb-3 flex items-center justify-between">
            <h3 className="text-[13px] font-bold text-[#1C1C1E]">{editId ? "Edit Pengajuan Harga" : "Ajukan Harga Khusus"}</h3>
            <button className="icon-button" onClick={resetForm} aria-label="Tutup"><X size={14} /></button>
          </div>
          <div className="grid gap-3 sm:grid-cols-2">
            <label className="grid gap-1 text-[11px] font-semibold text-[#6B6B73]">
              Customer
              <select
                data-testid="price-approvals-customer"
                className="field"
                disabled={!!editId}
                value={form.customer_id}
                onChange={(e) => setForm({ ...form, customer_id: e.target.value })}
              >
                <option value="">— Pilih Customer —</option>
                {customers.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
              </select>
            </label>
            <label className="grid gap-1 text-[11px] font-semibold text-[#6B6B73]">
              Produk
              <select
                data-testid="price-approvals-product"
                className="field"
                disabled={!!editId}
                value={form.product_id}
                onChange={(e) => setForm({ ...form, product_id: e.target.value })}
              >
                <option value="">— Pilih Produk —</option>
                {products.map((p) => <option key={p.id} value={p.id}>{p.name} ({p.sku})</option>)}
              </select>
            </label>
            <label className="grid gap-1 text-[11px] font-semibold text-[#6B6B73]">
              Harga Khusus / unit
              {selectedProduct && (
                <span className="text-[10px] font-normal text-[#8E8E93]">Harga normal: {formatCurrency(selectedProduct.price)}</span>
              )}
              <input
                data-testid="price-approvals-price"
                type="number" min="0" className="field tabular-nums"
                placeholder="cth: 150000"
                value={form.requested_price}
                onChange={(e) => setForm({ ...form, requested_price: e.target.value })}
              />
            </label>
            <label className="grid gap-1 text-[11px] font-semibold text-[#6B6B73]">
              Qty Minimum
              <input
                data-testid="price-approvals-minqty"
                type="number" min="0" className="field tabular-nums"
                placeholder="0"
                value={form.min_quantity}
                onChange={(e) => setForm({ ...form, min_quantity: e.target.value })}
              />
            </label>
            <label className="grid gap-1 text-[11px] font-semibold text-[#6B6B73]">
              Berlaku Sampai (opsional)
              <input
                data-testid="price-approvals-validuntil"
                type="date" className="field"
                value={form.valid_until}
                onChange={(e) => setForm({ ...form, valid_until: e.target.value })}
              />
            </label>
            <label className="grid gap-1 text-[11px] font-semibold text-[#6B6B73] sm:col-span-2">
              Alasan / Catatan
              <textarea
                data-testid="price-approvals-reason"
                className="field min-h-[56px] text-[12px]"
                placeholder="Konteks negosiasi harga…"
                value={form.reason}
                onChange={(e) => setForm({ ...form, reason: e.target.value })}
              />
            </label>
          </div>
          {formErr && <p data-testid="price-approvals-form-error" className="mt-2 text-[11px] font-semibold text-[#A8221A]">{formErr}</p>}
          <div className="mt-3 flex flex-wrap gap-2">
            <button
              data-testid="price-approvals-save"
              disabled={busyId === "form"}
              onClick={() => submitForm(false)}
              className="rounded-md border border-[#E5E5EA] px-4 py-1.5 text-[12px] font-semibold text-[#3C3C43] disabled:opacity-50"
            >
              {editId ? "Simpan Perubahan" : "Simpan sebagai Draft"}
            </button>
            {!editId && (
              <button
                data-testid="price-approvals-save-submit"
                disabled={busyId === "form"}
                onClick={() => submitForm(true)}
                className="flex items-center gap-1.5 rounded-md bg-[#6B219A] px-4 py-1.5 text-[12px] font-bold text-white disabled:opacity-50"
              >
                <Send size={13} /> Ajukan untuk Approval
              </button>
            )}
          </div>
        </section>
      )}

      {error && (
        <div data-testid="price-approvals-error" className="rounded-md border border-[#F3C7C2] bg-[#FDF1F0] p-3 text-[12px] text-[#A8221A]">
          {error}
        </div>
      )}

      <section className="grid gap-3">
        {loading && (
          <div data-testid="price-approvals-loading" className="section-card animate-pulse p-8 text-center text-[13px] text-[#6B6B73]">
            Memuat pengajuan…
          </div>
        )}
        {!loading && filtered.length === 0 && (
          <div data-testid="price-approvals-empty" className="section-card p-10 text-center text-[13px] text-[#6B6B73]">
            Belum ada pengajuan harga khusus.
          </div>
        )}
        {!loading && filtered.map((r) => {
          const meta = STATUS_META[r.status] || { label: r.status, icon: Clock3 };
          const StatusIcon = meta.icon;
          const editable = isEditable(r);
          const attachments = r.attachments || [];
          return (
            <article key={r.id} data-testid={`price-approvals-card-${r.id}`} className="section-card p-0 overflow-hidden">
              <div className="flex flex-wrap items-center justify-between gap-2 border-b border-[#EFF0F2] bg-[#FAFBFC] px-4 py-2.5">
                <div className="flex items-center gap-2 min-w-0">
                  <span className="truncate text-[12.5px] font-bold text-[#1C1C1E]">{r.customer_name}</span>
                  <span className="text-[#C7C7CC]">·</span>
                  <span className="text-[10px] font-bold uppercase text-[#0058CC]">{r.sku}</span>
                  <span className="truncate text-[12px] text-[#3C3C43]">{r.product_name}</span>
                </div>
                <span className={`status-pill status-${r.status}`} data-testid={`price-approvals-status-${r.id}`}>
                  <StatusIcon size={11} /> {meta.label}
                  {r.is_expired && <span className="ml-1 text-[9px] text-[#A8221A]">(kadaluarsa)</span>}
                </span>
              </div>

              <div className="grid gap-3 px-4 py-3 sm:grid-cols-[1fr_auto]">
                <div className="grid gap-1.5">
                  <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-[12.5px]">
                    <span className="text-[#8E8E93] line-through tabular-nums">{formatCurrency(r.normal_price)}</span>
                    <span className="font-bold text-[#6B219A] tabular-nums" data-testid={`price-approvals-price-${r.id}`}>{formatCurrency(r.requested_price)}</span>
                    <span className="rounded-full bg-[#F3E9FA] px-2 py-0.5 text-[10px] font-bold text-[#6B219A]">−{formatQty(r.discount_percent)}%</span>
                    {r.min_quantity > 0 && <span className="text-[11px] text-[#6B6B73]">min {formatQty(r.min_quantity)} {r.unit}</span>}
                  </div>
                  {r.reason && <p className="text-[11.5px] text-[#6B6B73]">{r.reason}</p>}
                  <div className="flex flex-wrap items-center gap-x-4 gap-y-0.5 text-[10.5px] text-[#8E8E93]">
                    <span>Pengaju: <span className="font-medium text-[#3C3C43]">{r.requested_by_name || "—"}</span></span>
                    {r.valid_until && <span>Berlaku s/d: <span className="font-medium text-[#3C3C43]">{(r.valid_until || "").slice(0, 10)}</span></span>}
                    {r.approved_by_name && <span>{r.status === "rejected" ? "Ditolak" : "Disetujui"}: <span className="font-medium text-[#3C3C43]">{r.approved_by_name}</span></span>}
                  </div>
                  {r.decision_notes && (
                    <p className={`text-[11px] ${r.status === "rejected" ? "text-[#A8221A]" : "text-[#126E2C]"}`}>Catatan: {r.decision_notes}</p>
                  )}

                  {/* Lampiran bukti */}
                  {attachments.length > 0 && (
                    <div className="mt-1 flex flex-wrap gap-2">
                      {attachments.map((att) => (
                        <span key={att.id} data-testid={`price-approvals-att-${att.id}`} className="flex items-center gap-1 rounded-md border border-[#E5E5EA] bg-white px-2 py-1 text-[10.5px] text-[#3C3C43]">
                          <Paperclip size={11} className="text-[#6B219A]" />
                          <button className="max-w-[140px] truncate hover:underline" onClick={() => viewAttachment(r.id, att)} data-testid={`price-approvals-att-view-${att.id}`}>
                            {att.original_filename}
                          </button>
                          <button onClick={() => viewAttachment(r.id, att)} aria-label="Lihat" className="text-[#0058CC]"><Eye size={11} /></button>
                          {editable && (
                            <button onClick={() => deleteAttachment(r.id, att.id)} aria-label="Hapus lampiran" className="text-[#A8221A]"><Trash2 size={11} /></button>
                          )}
                        </span>
                      ))}
                    </div>
                  )}
                </div>

                {/* Aksi */}
                <div className="flex flex-col items-stretch gap-1.5 sm:min-w-[180px]">
                  {editable && (
                    <>
                      <input
                        ref={(el) => (fileInputs.current[r.id] = el)}
                        type="file" accept="image/*,application/pdf" className="hidden"
                        data-testid={`price-approvals-file-${r.id}`}
                        onChange={(e) => { uploadFile(r.id, e.target.files?.[0]); e.target.value = ""; }}
                      />
                      <button
                        data-testid={`price-approvals-upload-${r.id}`}
                        disabled={busyId === r.id}
                        onClick={() => fileInputs.current[r.id]?.click()}
                        className="flex items-center justify-center gap-1.5 rounded-md border border-[#E5E5EA] px-3 py-1.5 text-[11.5px] font-semibold text-[#3C3C43] disabled:opacity-50"
                      >
                        <Paperclip size={13} /> Upload Bukti
                      </button>
                    </>
                  )}

                  {r.status === "draft" && (
                    <button
                      data-testid={`price-approvals-submit-${r.id}`}
                      disabled={busyId === r.id}
                      onClick={() => submitApproval(r.id)}
                      className="flex items-center justify-center gap-1.5 rounded-md bg-[#6B219A] px-3 py-1.5 text-[11.5px] font-bold text-white disabled:opacity-50"
                    >
                      <Send size={13} /> Submit
                    </button>
                  )}

                  {r.status === "pending" && canApprove && decideFor !== `${r.id}:reject` && (
                    <button
                      data-testid={`price-approvals-approve-${r.id}`}
                      disabled={busyId === r.id}
                      onClick={() => { setDecideFor(`${r.id}:approve`); setDecisionNotes(""); }}
                      className="flex items-center justify-center gap-1.5 rounded-md bg-[#126E2C] px-3 py-1.5 text-[11.5px] font-bold text-white disabled:opacity-50"
                    >
                      <Check size={13} /> Approve
                    </button>
                  )}
                  {r.status === "pending" && canApprove && decideFor !== `${r.id}:approve` && (
                    <button
                      data-testid={`price-approvals-reject-${r.id}`}
                      disabled={busyId === r.id}
                      onClick={() => { setDecideFor(`${r.id}:reject`); setDecisionNotes(""); }}
                      className="flex items-center justify-center gap-1.5 rounded-md border border-[#E5E5EA] px-3 py-1.5 text-[11.5px] font-semibold text-[#A8221A] disabled:opacity-50"
                    >
                      <X size={13} /> Tolak
                    </button>
                  )}

                  {editable && (
                    <div className="flex gap-1.5">
                      <button
                        data-testid={`price-approvals-edit-${r.id}`}
                        onClick={() => openEdit(r)}
                        className="flex flex-1 items-center justify-center gap-1 rounded-md border border-[#E5E5EA] px-2 py-1.5 text-[11px] font-semibold text-[#3C3C43]"
                      >
                        <Pencil size={12} /> Edit
                      </button>
                      <button
                        data-testid={`price-approvals-delete-${r.id}`}
                        disabled={busyId === r.id}
                        onClick={() => removeApproval(r.id)}
                        className="flex flex-1 items-center justify-center gap-1 rounded-md border border-[#E5E5EA] px-2 py-1.5 text-[11px] font-semibold text-[#A8221A] disabled:opacity-50"
                      >
                        <Trash2 size={12} /> Hapus
                      </button>
                    </div>
                  )}
                </div>
              </div>

              {/* Panel keputusan (notes) */}
              {decideFor.startsWith(`${r.id}:`) && (
                <div className="border-t border-[#EFF0F2] bg-[#FAFBFC] px-4 py-3">
                  <textarea
                    data-testid={`price-approvals-notes-${r.id}`}
                    className="field min-h-[52px] w-full text-[12px]"
                    placeholder={decideFor.endsWith("approve") ? "Catatan persetujuan (opsional)…" : "Alasan penolakan…"}
                    value={decisionNotes}
                    onChange={(e) => setDecisionNotes(e.target.value)}
                  />
                  <div className="mt-2 flex gap-2">
                    <button
                      data-testid={`price-approvals-confirm-${r.id}`}
                      disabled={busyId === r.id}
                      onClick={() => (decideFor.endsWith("approve") ? approveApproval(r.id, decisionNotes) : rejectApproval(r.id, decisionNotes))}
                      className={`flex items-center gap-1.5 rounded-md px-4 py-1.5 text-[12px] font-bold text-white disabled:opacity-50 ${decideFor.endsWith("approve") ? "bg-[#126E2C]" : "bg-[#A8221A]"}`}
                    >
                      {decideFor.endsWith("approve") ? <Check size={13} /> : <X size={13} />}
                      {busyId === r.id ? "Memproses…" : decideFor.endsWith("approve") ? "Konfirmasi Setujui" : "Konfirmasi Tolak"}
                    </button>
                    <button
                      onClick={() => { setDecideFor(""); setDecisionNotes(""); }}
                      className="rounded-md border border-[#E5E5EA] px-3 py-1.5 text-[12px] font-semibold text-[#3C3C43]"
                    >
                      Batal
                    </button>
                  </div>
                </div>
              )}
            </article>
          );
        })}
      </section>
    </div>
  );
}
