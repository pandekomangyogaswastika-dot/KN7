import { useState, useEffect } from "react";
import { Users, UserPlus } from "lucide-react";

export function CustomerPanel({ 
  customers, 
  selectedCustomer, 
  setSelectedCustomer, 
  selectedAddress, 
  setSelectedAddress, 
  onCreateCustomer, 
  onShowDetail 
}) {
  const [form, setForm] = useState({ 
    name: "", 
    pic_name: "", 
    phone: "", 
    city: "Jakarta", 
    address: "" 
  });
  
  const addresses = selectedCustomer?.addresses || [];
  
  useEffect(() => {
    if (selectedCustomer && !selectedAddress) {
      setSelectedAddress(selectedCustomer.addresses?.[0]?.id || "");
    }
  }, [selectedCustomer, selectedAddress, setSelectedAddress]);
  
  return (
    <section data-testid="customer-panel" className="section-card">
      <div className="section-head">
        <div className="flex items-center gap-2 min-w-0">
          <Users data-testid="customer-panel-icon" size={14} className="text-[#0058CC]" />
          <span className="kicker">Master Customer</span>
          <h2>Customer aktif</h2>
        </div>
      </div>
      <div className="section-body">
        {/* Customer Dropdown */}
        <div data-testid="customer-select" className="mb-3">
          <label className="block text-[10px] font-bold uppercase tracking-wide text-[#6B6B73] mb-1.5">
            Pilih Customer
          </label>
          <select 
            className="field w-full"
            value={selectedCustomer?.id || ""}
            onChange={(e) => {
              const customer = customers.find(c => c.id === e.target.value);
              setSelectedCustomer(customer);
            }}
          >
            <option value="">-- Pilih customer dari master --</option>
            {customers.map((customer) => (
              <option key={customer.id} value={customer.id}>
                {customer.name} — {customer.city}
              </option>
            ))}
          </select>
        </div>
        
        {selectedCustomer && (
          <div className="rounded-md border border-[#EFF0F2] bg-[#FAFBFC] p-2.5">
            <button 
              data-testid="selected-customer-info" 
              className="interactive-card w-full rounded-md bg-white p-2 text-left border border-[#EFF0F2]" 
              onClick={() => onShowDetail({ 
                title: selectedCustomer.name, 
                body: "Customer aktif untuk sales order ini. Pilih alamat pengiriman yang tepat agar Surat Jalan jelas.", 
                facts: [
                  { label: "PIC", value: selectedCustomer.pic_name }, 
                  { label: "Phone", value: selectedCustomer.phone }, 
                  { label: "Alamat", value: addresses.length }
                ], 
                target: "sales", 
                cta: "Lanjut order" 
              })}
            >
              <p data-testid="selected-customer-name" className="text-[12.5px] font-semibold">
                {selectedCustomer.name}
              </p>
              <p data-testid="selected-customer-contact" className="text-[11px] text-[#3C3C43]">
                {selectedCustomer.pic_name} • {selectedCustomer.phone}
              </p>
            </button>
            {addresses.length > 0 && (
              <div data-testid="shipping-address-select" className="mt-2">
                <label className="block text-[10px] font-bold uppercase tracking-wide text-[#6B6B73] mb-1">
                  Alamat Pengiriman
                </label>
                <select
                  className="field w-full"
                  value={selectedAddress || ""}
                  onChange={(e) => setSelectedAddress(e.target.value)}
                >
                  <option value="">-- Pilih alamat --</option>
                  {addresses.map((address) => (
                    <option key={address.id} value={address.id}>
                      {address.label} — {address.city}
                    </option>
                  ))}
                </select>
              </div>
            )}
          </div>
        )}
        <div className="mt-3 rounded-md border border-[#EFF0F2] bg-[#FAFBFC] p-2.5">
          <p className="mb-2 text-[10.5px] font-bold uppercase tracking-wide text-[#6B6B73]">
            Customer baru langsung aktif
          </p>
          <div className="grid gap-2">
            <input 
              data-testid="new-customer-name-input" 
              className="field" 
              placeholder="Nama customer" 
              value={form.name} 
              onChange={(e) => setForm({ ...form, name: e.target.value })} 
            />
            <input 
              data-testid="new-customer-pic-input" 
              className="field" 
              placeholder="Nama PIC" 
              value={form.pic_name} 
              onChange={(e) => setForm({ ...form, pic_name: e.target.value })} 
            />
            <input 
              data-testid="new-customer-phone-input" 
              className="field" 
              placeholder="No. WhatsApp" 
              value={form.phone} 
              onChange={(e) => setForm({ ...form, phone: e.target.value })} 
            />
            <div className="grid gap-2 sm:grid-cols-2">
              <input 
                data-testid="new-customer-city-input" 
                className="field" 
                placeholder="Kota" 
                value={form.city} 
                onChange={(e) => setForm({ ...form, city: e.target.value })} 
              />
              <input 
                data-testid="new-customer-address-input" 
                className="field" 
                placeholder="Alamat" 
                value={form.address} 
                onChange={(e) => setForm({ ...form, address: e.target.value })} 
              />
            </div>
            <button 
              data-testid="create-customer-button" 
              className="secondary-button" 
              onClick={() => onCreateCustomer(form)}
            >
              <UserPlus size={14} /> Buat Customer
            </button>
          </div>
        </div>
      </div>
    </section>
  );
}
