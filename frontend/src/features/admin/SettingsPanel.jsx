/**
 * SettingsPanel — Configuration Foundation (Fase 1A).
 * Mengelola pengaturan global (pajak/keuangan/penjualan/inventory),
 * Term Pembayaran (CRUD), dan Matriks Approval (CRUD). Semua CONFIGURABLE.
 */
import { useEffect, useState } from "react";
import { Save, Plus, Trash2, Receipt, Wallet, CreditCard, ShieldCheck, Boxes, RefreshCw } from "lucide-react";
import axios from "../../services/apiClient";

const SUBTABS = [
  ["umum", "Umum", Receipt],
  ["terms", "Term Pembayaran", CreditCard],
  ["approval", "Matriks Approval", ShieldCheck],
];

const DOC_TYPES = [
  ["sales_order", "Sales Order"],
  ["purchase_order", "Purchase Order"],
  ["discount", "Diskon (%)"],
  ["transfer", "Transfer Gudang"],
];

const fmtRp = (v) => "Rp " + Number(v || 0).toLocaleString("id-ID");

export default function SettingsPanel({ entities = [] }) {
  const [sub, setSub] = useState("umum");
  const [settings, setSettings] = useState(null);
  const [terms, setTerms] = useState([]);
  const [rules, setRules] = useState([]);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [msg, setMsg] = useState("");

  const fetchAll = async () => {
    setLoading(true);
    try {
      const [s, t, r] = await Promise.all([
        axios.get("/api/settings"),
        axios.get("/api/payment-terms"),
        axios.get("/api/approval-rules"),
      ]);
      setSettings(s.data);
      setTerms(t.data);
      setRules(r.data);
    } catch (e) { console.error(e); }
    finally { setLoading(false); }
  };
  useEffect(() => { fetchAll(); }, []);

  const flash = (m) => { setMsg(m); setTimeout(() => setMsg(""), 2500); };

  const setSection = (sec, key, val) =>
    setSettings((p) => ({ ...p, [sec]: { ...(p?.[sec] || {}), [key]: val } }));

  const saveSettings = async () => {
    setSaving(true);
    try {
      await axios.put("/api/settings", {
        scope: "global",
        tax: settings.tax, finance: settings.finance,
        sales: settings.sales, inventory: settings.inventory,
      });
      flash("Pengaturan tersimpan");
    } catch (e) { alert(e.response?.data?.detail || "Gagal simpan"); }
    finally { setSaving(false); }
  };

  // ── Payment terms CRUD ──
  const [newTerm, setNewTerm] = useState({ code: "", name: "", type: "credit", net_days: 0, dp_percent: 0, installment_count: 0 });
  const addTerm = async () => {
    if (!newTerm.code || !newTerm.name) return alert("Kode & nama wajib diisi");
    try {
      await axios.post("/api/payment-terms", { ...newTerm, sort: terms.length + 1, active: true });
      setNewTerm({ code: "", name: "", type: "credit", net_days: 0, dp_percent: 0, installment_count: 0 });
      fetchAll(); flash("Term ditambahkan");
    } catch (e) { alert(e.response?.data?.detail || "Gagal"); }
  };
  const toggleTerm = async (t) => {
    await axios.patch(`/api/payment-terms/${t.id}`, { data: { active: !t.active } });
    fetchAll();
  };

  // ── Approval rules CRUD ──
  const [newRule, setNewRule] = useState({ doc_type: "sales_order", entity_id: "all", min_amount: 0, max_amount: "", required_role: "manager", is_percent: false });
  const addRule = async () => {
    try {
      await axios.post("/api/approval-rules", {
        ...newRule,
        max_amount: newRule.max_amount === "" ? null : Number(newRule.max_amount),
        is_percent: newRule.doc_type === "discount",
        sort: rules.filter((r) => r.doc_type === newRule.doc_type).length + 1,
        active: true,
      });
      setNewRule({ doc_type: "sales_order", entity_id: "all", min_amount: 0, max_amount: "", required_role: "manager", is_percent: false });
      fetchAll(); flash("Rule ditambahkan");
    } catch (e) { alert(e.response?.data?.detail || "Gagal"); }
  };
  const delRule = async (id) => {
    if (!window.confirm("Hapus rule ini?")) return;
    await axios.delete(`/api/approval-rules/${id}`);
    fetchAll();
  };

  if (loading || !settings) {
    return <div data-testid="settings-panel" className="section-card"><div className="section-body text-[12px] text-[#6B6B73]">Memuat pengaturan…</div></div>;
  }

  const tax = settings.tax || {}, fin = settings.finance || {}, sal = settings.sales || {}, inv = settings.inventory || {};

  return (
    <div data-testid="settings-panel" className="flex flex-col gap-3">
      {/* Sub-tab bar */}
      <div className="flex flex-wrap items-center gap-1.5">
        {SUBTABS.map(([id, label, Icon]) => (
          <button key={id} data-testid={`settings-subtab-${id}`} onClick={() => setSub(id)}
            className={`flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-[12px] font-semibold transition-all ${sub === id ? "bg-[#007AFF] text-white" : "bg-white border border-[#E5E5EA] text-[#6B6B73] hover:border-[#007AFF]"}`}>
            <Icon size={13} /> {label}
          </button>
        ))}
        <button onClick={fetchAll} className="ml-auto p-1.5 rounded-lg border border-[#E5E5EA] text-[#6B6B73] hover:bg-[#FAFBFC]"><RefreshCw size={13} /></button>
        {msg && <span data-testid="settings-flash" className="text-[12px] font-semibold text-[#34C759]">{msg}</span>}
      </div>

      {/* ── UMUM ── */}
      {sub === "umum" && (
        <div className="grid gap-3 md:grid-cols-2">
          {/* Pajak & Faktur */}
          <div className="section-card">
            <div className="section-head"><div className="flex items-center gap-2"><Receipt size={15} className="text-[#007AFF]" /><h2>Pajak & Faktur</h2></div></div>
            <div className="section-body grid gap-2.5">
              <Field label="Tarif PPN (%)">
                <input type="number" data-testid="settings-ppn-rate" className="field tabular-nums" value={tax.ppn_rate ?? 11}
                  onChange={(e) => setSection("tax", "ppn_rate", parseFloat(e.target.value) || 0)} />
              </Field>
              <Field label="Mode PPN">
                <select data-testid="settings-ppn-mode" className="field" value={tax.ppn_mode || "excluded"}
                  onChange={(e) => setSection("tax", "ppn_mode", e.target.value)}>
                  <option value="excluded">Excluded — ditambah saat invoice</option>
                  <option value="included">Included — sudah termasuk di harga</option>
                </select>
              </Field>
              <Toggle label="e-Faktur diaktifkan (PKP)" testid="settings-efaktur"
                checked={!!tax.efaktur_enabled} onChange={(v) => setSection("tax", "efaktur_enabled", v)} />
              <p className="text-[10.5px] text-[#8E8E93]">Entitas non-PKP otomatis PPN 0% & tanpa e-Faktur (mengikuti master entitas).</p>
            </div>
          </div>

          {/* Keuangan */}
          <div className="section-card">
            <div className="section-head"><div className="flex items-center gap-2"><Wallet size={15} className="text-[#007AFF]" /><h2>Keuangan</h2></div></div>
            <div className="section-body grid gap-2.5">
              <Field label="Mata Uang Dasar">
                <input data-testid="settings-currency" className="field" value={fin.base_currency || "IDR"}
                  onChange={(e) => setSection("finance", "base_currency", e.target.value)} />
              </Field>
              <Field label="Bulan Tutup Buku Fiskal">
                <select data-testid="settings-fiscal-month" className="field" value={fin.fiscal_year_end_month || 12}
                  onChange={(e) => setSection("finance", "fiscal_year_end_month", parseInt(e.target.value))}>
                  {["Jan","Feb","Mar","Apr","Mei","Jun","Jul","Agu","Sep","Okt","Nov","Des"].map((m, i) => <option key={i} value={i + 1}>{m}</option>)}
                </select>
              </Field>
              <Field label="Term Pembayaran Default">
                <select data-testid="settings-default-term" className="field" value={fin.default_payment_term_code || ""}
                  onChange={(e) => setSection("finance", "default_payment_term_code", e.target.value)}>
                  {terms.map((t) => <option key={t.id} value={t.code}>{t.name}</option>)}
                </select>
              </Field>
            </div>
          </div>

          {/* Penjualan */}
          <div className="section-card">
            <div className="section-head"><div className="flex items-center gap-2"><CreditCard size={15} className="text-[#007AFF]" /><h2>Penjualan</h2></div></div>
            <div className="section-body grid gap-2">
              <Toggle label="Aktifkan tahap Quotation" testid="settings-quotation" checked={!!sal.quotation_enabled} onChange={(v) => setSection("sales", "quotation_enabled", v)} />
              <Toggle label="Izinkan partial shipment" testid="settings-partial" checked={!!sal.allow_partial_shipment} onChange={(v) => setSection("sales", "allow_partial_shipment", v)} />
              <Toggle label="Izinkan diskon per-order" testid="settings-order-disc" checked={!!sal.allow_order_discount} onChange={(v) => setSection("sales", "allow_order_discount", v)} />
              <Toggle label="Izinkan diskon per-item" testid="settings-item-disc" checked={!!sal.allow_item_discount} onChange={(v) => setSection("sales", "allow_item_discount", v)} />
            </div>
          </div>

          {/* Inventory */}
          <div className="section-card">
            <div className="section-head"><div className="flex items-center gap-2"><Boxes size={15} className="text-[#007AFF]" /><h2>Inventory</h2></div></div>
            <div className="section-body grid gap-2.5">
              <Field label="UOM Default"><input data-testid="settings-default-uom" className="field" value={inv.default_uom || "meter"} onChange={(e) => setSection("inventory", "default_uom", e.target.value)} /></Field>
              <Field label="Minimum Potong (qty)"><input type="number" data-testid="settings-mincut" className="field tabular-nums" value={inv.min_cut_qty ?? 0.5} onChange={(e) => setSection("inventory", "min_cut_qty", parseFloat(e.target.value) || 0)} /></Field>
              <Toggle label="Transfer antar-entitas wajib sebelum jual stok entitas lain" testid="settings-ic-transfer" checked={!!inv.intercompany_transfer_required} onChange={(v) => setSection("inventory", "intercompany_transfer_required", v)} />
            </div>
          </div>

          <div className="md:col-span-2">
            <button data-testid="settings-save-button" onClick={saveSettings} disabled={saving} className="primary-button"><Save size={14} /> {saving ? "Menyimpan…" : "Simpan Pengaturan"}</button>
          </div>
        </div>
      )}

      {/* ── TERM PEMBAYARAN ── */}
      {sub === "terms" && (
        <div className="section-card">
          <div className="section-head"><div className="flex items-center gap-2"><CreditCard size={15} className="text-[#007AFF]" /><h2>Term Pembayaran</h2></div></div>
          <div className="section-body">
            <div className="grid gap-2 sm:grid-cols-6 mb-3 rounded-md border border-[#EFF0F2] bg-[#FAFBFC] p-2.5">
              <input data-testid="newterm-code" className="field" placeholder="Kode" value={newTerm.code} onChange={(e) => setNewTerm({ ...newTerm, code: e.target.value.toUpperCase() })} />
              <input data-testid="newterm-name" className="field sm:col-span-2" placeholder="Nama term" value={newTerm.name} onChange={(e) => setNewTerm({ ...newTerm, name: e.target.value })} />
              <select data-testid="newterm-type" className="field" value={newTerm.type} onChange={(e) => setNewTerm({ ...newTerm, type: e.target.value })}>
                <option value="cash">Tunai</option><option value="credit">Kredit</option><option value="dp">DP</option><option value="installment">Bertahap</option>
              </select>
              <input type="number" data-testid="newterm-netdays" className="field tabular-nums" placeholder="NET hari" value={newTerm.net_days} onChange={(e) => setNewTerm({ ...newTerm, net_days: parseInt(e.target.value) || 0 })} />
              <button data-testid="newterm-add" onClick={addTerm} className="primary-button"><Plus size={13} /> Tambah</button>
            </div>
            <div className="overflow-x-auto rounded-md border border-[#EFF0F2]">
              <table className="w-full text-[11.5px]">
                <thead><tr className="bg-[#FAFBFC] text-[10px] uppercase text-[#6B6B73]">
                  <th className="text-left px-3 py-2">Kode</th><th className="text-left px-3 py-2">Nama</th><th className="text-left px-3 py-2">Tipe</th><th className="text-right px-3 py-2">NET</th><th className="text-right px-3 py-2">DP%</th><th className="px-3 py-2">Status</th><th></th>
                </tr></thead>
                <tbody className="divide-y divide-[#EFF0F2]">
                  {terms.map((t) => (
                    <tr key={t.id} data-testid={`term-row-${t.id}`} className={t.active ? "" : "opacity-50"}>
                      <td className="px-3 py-2 font-bold text-[#007AFF]">{t.code}</td>
                      <td className="px-3 py-2">{t.name}</td>
                      <td className="px-3 py-2 capitalize">{t.type}</td>
                      <td className="px-3 py-2 text-right tabular-nums">{t.net_days}h</td>
                      <td className="px-3 py-2 text-right tabular-nums">{t.dp_percent}%</td>
                      <td className="px-3 py-2 text-center"><span className={`rounded px-1.5 py-0.5 text-[10px] font-semibold ${t.active ? "bg-green-100 text-green-700" : "bg-gray-100 text-gray-500"}`}>{t.active ? "Aktif" : "Nonaktif"}</span></td>
                      <td className="px-3 py-2 text-right"><button data-testid={`term-toggle-${t.id}`} onClick={() => toggleTerm(t)} className="secondary-button text-[11px]">{t.active ? "Nonaktifkan" : "Aktifkan"}</button></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* ── MATRIKS APPROVAL ── */}
      {sub === "approval" && (
        <div className="section-card">
          <div className="section-head"><div className="flex items-center gap-2"><ShieldCheck size={15} className="text-[#007AFF]" /><h2>Matriks Approval</h2></div></div>
          <div className="section-body">
            <div className="grid gap-2 sm:grid-cols-7 mb-3 rounded-md border border-[#EFF0F2] bg-[#FAFBFC] p-2.5">
              <select data-testid="newrule-doctype" className="field sm:col-span-2" value={newRule.doc_type} onChange={(e) => setNewRule({ ...newRule, doc_type: e.target.value })}>
                {DOC_TYPES.map(([v, l]) => <option key={v} value={v}>{l}</option>)}
              </select>
              <select data-testid="newrule-entity" className="field" value={newRule.entity_id} onChange={(e) => setNewRule({ ...newRule, entity_id: e.target.value })}>
                <option value="all">Semua Entitas</option>
                {entities.map((en) => <option key={en.id} value={en.id}>{en.short_name || en.legal_name}</option>)}
              </select>
              <input type="number" data-testid="newrule-min" className="field tabular-nums" placeholder="Min" value={newRule.min_amount} onChange={(e) => setNewRule({ ...newRule, min_amount: parseFloat(e.target.value) || 0 })} />
              <input type="number" data-testid="newrule-max" className="field tabular-nums" placeholder="Max (kosong=∞)" value={newRule.max_amount} onChange={(e) => setNewRule({ ...newRule, max_amount: e.target.value })} />
              <select data-testid="newrule-role" className="field" value={newRule.required_role} onChange={(e) => setNewRule({ ...newRule, required_role: e.target.value })}>
                <option value="">Tanpa approval</option><option value="manager">Manager</option><option value="admin">Admin</option>
              </select>
              <button data-testid="newrule-add" onClick={addRule} className="primary-button"><Plus size={13} /> Tambah</button>
            </div>
            {DOC_TYPES.map(([dt, dl]) => {
              const group = rules.filter((r) => r.doc_type === dt);
              if (group.length === 0) return null;
              return (
                <div key={dt} className="mb-3">
                  <p className="text-[11px] font-bold uppercase tracking-wide text-[#6B6B73] mb-1">{dl}</p>
                  <div className="overflow-x-auto rounded-md border border-[#EFF0F2]">
                    <table className="w-full text-[11.5px]">
                      <thead><tr className="bg-[#FAFBFC] text-[10px] uppercase text-[#6B6B73]">
                        <th className="text-left px-3 py-2">Entitas</th><th className="text-right px-3 py-2">Min</th><th className="text-right px-3 py-2">Max</th><th className="px-3 py-2">Butuh Approval</th><th></th>
                      </tr></thead>
                      <tbody className="divide-y divide-[#EFF0F2]">
                        {group.map((r) => (
                          <tr key={r.id} data-testid={`rule-row-${r.id}`}>
                            <td className="px-3 py-2">{r.entity_id === "all" ? "Semua" : (entities.find((e) => e.id === r.entity_id)?.short_name || r.entity_id)}</td>
                            <td className="px-3 py-2 text-right tabular-nums">{r.is_percent ? `${r.min_amount}%` : fmtRp(r.min_amount)}</td>
                            <td className="px-3 py-2 text-right tabular-nums">{r.max_amount == null ? "∞" : (r.is_percent ? `${r.max_amount}%` : fmtRp(r.max_amount))}</td>
                            <td className="px-3 py-2 text-center">{r.required_role ? <span className="rounded px-1.5 py-0.5 text-[10px] font-semibold bg-orange-100 text-orange-700 capitalize">{r.required_role}</span> : <span className="text-[#8E8E93]">—</span>}</td>
                            <td className="px-3 py-2 text-right"><button data-testid={`rule-del-${r.id}`} onClick={() => delRule(r.id)} className="danger-button text-[11px]"><Trash2 size={12} /></button></td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}

function Field({ label, children }) {
  return (
    <label className="block">
      <span className="block text-[10.5px] font-semibold text-[#6B6B73] mb-1">{label}</span>
      {children}
    </label>
  );
}

function Toggle({ label, checked, onChange, testid }) {
  return (
    <button type="button" data-testid={testid} onClick={() => onChange(!checked)}
      className="flex items-center justify-between gap-3 rounded-md border border-[#EFF0F2] px-2.5 py-2 text-left hover:bg-[#FAFBFC]">
      <span className="text-[11.5px] font-medium">{label}</span>
      <span className={`relative h-5 w-9 shrink-0 rounded-full transition-colors ${checked ? "bg-[#34C759]" : "bg-[#D1D1D6]"}`}>
        <span className={`absolute top-0.5 h-4 w-4 rounded-full bg-white shadow transition-all ${checked ? "left-[18px]" : "left-0.5"}`} />
      </span>
    </button>
  );
}
