import React, { useCallback, useState } from 'react';
import api from '../../services/api.js';

const fieldStyle = { width: '100%', minWidth: 0, padding: '0.65rem 0.75rem', border: '1px solid var(--border, #cbd5e1)', borderRadius: 8, background: 'var(--surface, #fff)', color: 'var(--text, #0f172a)' };
const panelStyle = { border: '1px solid var(--border, #dbe2ea)', borderRadius: 14, padding: 18, background: 'var(--surface, #fff)', minWidth: 0 };
const buttonStyle = { border: 0, borderRadius: 8, padding: '0.7rem 1rem', background: 'var(--primary, #173b67)', color: '#fff', fontWeight: 650, cursor: 'pointer' };
const newId = (prefix) => `${prefix}_${globalThis.crypto?.randomUUID?.() || `${Date.now()}_${Math.random().toString(16).slice(2)}`}`;
const money = (minor, currency = 'ZAR') => new Intl.NumberFormat('en-ZA', { style: 'currency', currency }).format(Number(minor || 0) / 100);

function Field({ label, value, onChange, type = 'text', ...props }) {
  return <label style={{ display: 'grid', gap: 6, fontSize: 13, fontWeight: 600 }}>
    {label}<input {...props} type={type} value={value} onChange={(event) => onChange(event.target.value)} style={fieldStyle} />
  </label>;
}

export default function POSWorkspace() {
  const [locationId, setLocationId] = useState('');
  const [saleId, setSaleId] = useState('');
  const [currency, setCurrency] = useState('ZAR');
  const [productId, setProductId] = useState('');
  const [sku, setSku] = useState('');
  const [description, setDescription] = useState('');
  const [quantity, setQuantity] = useState('1');
  const [unitPrice, setUnitPrice] = useState('');
  const [tax, setTax] = useState('0');
  const [discount, setDiscount] = useState('0');
  const [sale, setSale] = useState(null);
  const [tenderType, setTenderType] = useState('CARD');
  const [tenderAmount, setTenderAmount] = useState('');
  const [tenderEvidenceId, setTenderEvidenceId] = useState('');
  const [cashReceived, setCashReceived] = useState('');
  const [returnSku, setReturnSku] = useState('');
  const [returnQuantity, setReturnQuantity] = useState('1');
  const [returnReason, setReturnReason] = useState('');
  const [refundAmount, setRefundAmount] = useState('');
  const [refundIntentId, setRefundIntentId] = useState('');
  const [refundBasis, setRefundBasis] = useState('');
  const [busy, setBusy] = useState(false);
  const [notice, setNotice] = useState({ kind: 'info', text: 'Select a location assigned to your authenticated account. The server verifies that assignment on every operation.' });

  const request = useCallback(async (method, path, body, commandKey) => {
    const key = commandKey || newId('poscmd');
    const response = method === 'get'
      ? await api.get(path)
      : await api.post(path, body, { headers: { 'Idempotency-Key': key } });
    return response.data;
  }, []);

  const run = useCallback(async (operation) => {
    if (!locationId.trim()) {
      setNotice({ kind: 'error', text: 'Enter a location ID. It is only a selector; EOS must independently verify your active assignment.' });
      return;
    }
    setBusy(true);
    try {
      const result = await operation();
      if (result?.sale) setSale(result);
      else if (result?.tenant_id && result?.sale_id) setSale({ sale: result, commercial_evidence: [] });
      setNotice({ kind: 'success', text: result?.execution_truth ? 'Kennel EOS returned execution evidence. This is not settlement or paid-state confirmation.' : 'Command accepted and durably recorded by EOS. POS does not assert financial execution or settlement.' });
    } catch (error) {
      const code = error?.response?.data?.detail || error?.message || 'POS_COMMAND_UNAVAILABLE';
      setNotice({ kind: 'error', text: String(code) });
    } finally {
      setBusy(false);
    }
  }, [locationId]);

  const base = `/pos/locations/${encodeURIComponent(locationId.trim())}`;
  const currentSale = sale?.sale;
  const lineTotal = Math.max(0, Number(quantity) * Number(unitPrice) - Number(discount) + Number(tax));

  return <section style={{ display: 'grid', gap: 18, padding: 'clamp(16px, 2.5vw, 28px)', maxWidth: 1440, margin: '0 auto' }}>
    <header style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'end', justifyContent: 'space-between', gap: 16 }}>
      <div>
        <p style={{ margin: 0, fontSize: 12, letterSpacing: '0.12em', fontWeight: 750, opacity: .65 }}>BUSINESS OPERATIONS / POS</p>
        <h1 style={{ margin: '6px 0', fontSize: 'clamp(24px, 3vw, 34px)' }}>Point of Sale</h1>
        <p style={{ margin: 0, opacity: .72 }}>Sales, tender evidence, returns and refund intent — with Kennel EOS retaining financial execution.</p>
      </div>
      <div style={{ width: 'min(100%, 320px)' }}>
        <Field label="Location ID" value={locationId} onChange={setLocationId} placeholder="Enter your assigned store/location" />
        <small style={{ display: 'block', marginTop: 5, opacity: .65 }}>Location input is never treated as access authority.</small>
      </div>
    </header>

    <div role="status" aria-live="polite" style={{ borderRadius: 10, padding: 12, border: '1px solid var(--border, #dbe2ea)', background: notice.kind === 'error' ? 'var(--danger-soft, #fff1f2)' : 'var(--surface-muted, #f8fafc)' }}>
      <strong>{notice.kind === 'error' ? 'Action blocked' : notice.kind === 'success' ? 'Recorded' : 'Workspace guidance'}</strong>
      <span style={{ marginLeft: 8 }}>{notice.text}</span>
    </div>

    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(min(100%, 320px), 1fr))', gap: 16 }}>
      <section style={panelStyle}>
        <h2 style={{ marginTop: 0 }}>Create a sale</h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, minmax(0, 1fr))', gap: 10 }}>
          <Field label="Sale reference" value={saleId} onChange={setSaleId} placeholder="e.g. SALE-10042" />
          <label style={{ display: 'grid', gap: 6, fontSize: 13, fontWeight: 600 }}>Currency<select value={currency} onChange={(e) => setCurrency(e.target.value)} style={fieldStyle}><option>ZAR</option><option>USD</option><option>EUR</option><option>GBP</option></select></label>
          <Field label="Product ID" value={productId} onChange={setProductId} />
          <Field label="SKU" value={sku} onChange={setSku} />
          <div style={{ gridColumn: '1 / -1' }}><Field label="Description" value={description} onChange={setDescription} /></div>
          <Field label="Quantity" type="number" min="1" value={quantity} onChange={setQuantity} />
          <Field label="Unit price (minor units)" type="number" min="0" value={unitPrice} onChange={setUnitPrice} />
          <Field label="Discount (minor units)" type="number" min="0" value={discount} onChange={setDiscount} />
          <Field label="Tax (minor units)" type="number" min="0" value={tax} onChange={setTax} />
        </div>
        <p style={{ fontWeight: 700 }}>Commercial total: {money(lineTotal, currency)}</p>
        <button type="button" disabled={busy} style={buttonStyle} onClick={() => run(async () => {
          const id = saleId.trim() || newId('sale');
          setSaleId(id);
          const created = await request('post', `${base}/sales`, { sale_id: id, currency, lines: [{ product_id: productId, sku, description, quantity: Number(quantity), unit_price_minor: Number(unitPrice), discount_minor: Number(discount), tax_minor: Number(tax), currency }] }, `sale:${id}`);
          return { sale: created, commercial_evidence: [] };
        })}>Create and record sale</button>
      </section>

      <section style={panelStyle}>
        <h2 style={{ marginTop: 0 }}>Retrieve a sale</h2>
        <Field label="Sale reference" value={saleId} onChange={setSaleId} placeholder="Enter an existing sale reference" />
        <button type="button" disabled={busy || !saleId.trim()} style={{ ...buttonStyle, marginTop: 12 }} onClick={() => run(() => request('get', `${base}/sales/${encodeURIComponent(saleId.trim())}`))}>Load sale and evidence</button>
        {currentSale ? <div style={{ marginTop: 18, borderTop: '1px solid var(--border, #dbe2ea)', paddingTop: 12 }}>
          <strong>{currentSale.sale_id}</strong><p style={{ margin: '6px 0' }}>{money(currentSale.total_minor, currentSale.currency)} · {currentSale.status}</p>
          <ul>{(currentSale.lines || []).map((line, index) => <li key={line.sku + index}>{line.description} · {line.quantity} × {money(line.unit_price_minor, line.currency)}</li>)}</ul>
          <p style={{ fontSize: 12, opacity: .65 }}>Financial state: not asserted by POS</p>
          <strong>Commercial evidence ({sale?.commercial_evidence?.length || 0})</strong>
          <ul>{(sale?.commercial_evidence || []).map((item) => <li key={item.evidence_id}>{item.evidence_type} · {item.evidence_id} · {item.recorded_by_principal_id}</li>)}</ul>
        </div> : null}
      </section>

      <section style={panelStyle}>
        <h2 style={{ marginTop: 0 }}>Record tender intent</h2>
        <Field label="Sale reference" value={saleId} onChange={setSaleId} />
        <label style={{ display: 'grid', gap: 6, fontSize: 13, fontWeight: 600 }}>Tender type<select value={tenderType} onChange={(e) => setTenderType(e.target.value)} style={fieldStyle}>{['CARD', 'BANK', 'WALLET', 'VOUCHER', 'STORE_CREDIT', 'CASH'].map((item) => <option key={item}>{item}</option>)}</select></label>
        <Field label="Amount (minor units)" type="number" min="1" value={tenderAmount} onChange={setTenderAmount} />
        <button type="button" disabled={busy || !saleId.trim() || Number(tenderAmount) <= 0} style={{ ...buttonStyle, marginTop: 12 }} onClick={() => run(() => { const id = tenderEvidenceId || newId('tender'); setTenderEvidenceId(id); return request('post', `${base}/sales/${encodeURIComponent(saleId.trim())}/tenders`, { tender_type: tenderType, amount_minor: Number(tenderAmount), evidence_id: id }, `tender:${id}`); })}>Record tender intent</button>
        {tenderEvidenceId && ['CARD', 'BANK', 'WALLET'].includes(tenderType) ? <button type="button" disabled={busy} style={{ ...buttonStyle, marginTop: 8, background: 'var(--success, #176b45)' }} onClick={() => run(() => request('post', `${base}/sales/${encodeURIComponent(saleId.trim())}/tenders/${encodeURIComponent(tenderEvidenceId)}/execute`, undefined, `execute-tender:${tenderEvidenceId}`))}>Authorize and send to Kennel EOS</button> : null}
        <p style={{ fontSize: 12, opacity: .65 }}>This records a request only. It does not mark the sale paid or settled.</p>
      </section>

      <section style={panelStyle}>
        <h2 style={{ marginTop: 0 }}>Record cash received</h2>
        <Field label="Sale reference" value={saleId} onChange={setSaleId} />
        <Field label="Cash received (minor units)" type="number" min="1" value={cashReceived} onChange={setCashReceived} />
        <button type="button" disabled={busy || !saleId.trim() || Number(cashReceived) <= 0} style={{ ...buttonStyle, marginTop: 12 }} onClick={() => run(() => request('post', `${base}/sales/${encodeURIComponent(saleId.trim())}/cash-tenders`, { cash_received_minor: Number(cashReceived), evidence_id: newId('cash') }))}>Record cash evidence</button>
      </section>

      <section style={panelStyle}>
        <h2 style={{ marginTop: 0 }}>Create a return intent</h2>
        <Field label="Sale reference" value={saleId} onChange={setSaleId} />
        <Field label="SKU" value={returnSku} onChange={setReturnSku} />
        <Field label="Quantity" type="number" min="1" value={returnQuantity} onChange={setReturnQuantity} />
        <Field label="Reason" value={returnReason} onChange={setReturnReason} />
        <button type="button" disabled={busy || !saleId.trim() || !returnSku.trim() || !returnReason.trim()} style={{ ...buttonStyle, marginTop: 12 }} onClick={() => run(() => request('post', `${base}/sales/${encodeURIComponent(saleId.trim())}/returns`, { sku: returnSku, quantity: Number(returnQuantity), reason: returnReason, return_id: newId('return') }))}>Record return intent</button>
      </section>

      <section style={panelStyle}>
        <h2 style={{ marginTop: 0 }}>Create a refund intent</h2>
        <Field label="Sale reference" value={saleId} onChange={setSaleId} />
        <Field label="Amount (minor units)" type="number" min="1" value={refundAmount} onChange={setRefundAmount} />
        <Field label="Basis" value={refundBasis} onChange={setRefundBasis} />
        <button type="button" disabled={busy || !saleId.trim() || Number(refundAmount) <= 0 || !refundBasis.trim()} style={{ ...buttonStyle, marginTop: 12 }} onClick={() => run(() => { const id = refundIntentId || newId('refund'); setRefundIntentId(id); return request('post', `${base}/sales/${encodeURIComponent(saleId.trim())}/refund-intents`, { amount_minor: Number(refundAmount), basis: refundBasis, refund_intent_id: id }, `refund:${id}`); })}>Record refund intent</button>
        {refundIntentId ? <button type="button" disabled={busy} style={{ ...buttonStyle, marginTop: 8, background: 'var(--success, #176b45)' }} onClick={() => run(() => request('post', `${base}/sales/${encodeURIComponent(saleId.trim())}/refund-intents/${encodeURIComponent(refundIntentId)}/execute`, undefined, `execute-refund:${refundIntentId}`))}>Authorize and send refund to Kennel EOS</button> : null}
        <p style={{ fontSize: 12, opacity: .65 }}>Refund execution and settlement remain with Kennel EOS.</p>
      </section>
    </div>
  </section>;
}
