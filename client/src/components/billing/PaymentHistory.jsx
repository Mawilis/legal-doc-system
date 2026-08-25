/* eslint-disable */
/**
 * WILSY OS - PAYMENT HISTORY [V1.0.0-LEDGER-TRUTH]
 * EPITOME: Shows payment attempts supplied by the ledger, including the newest in-session result, without inventing persisted events.
 * BIBLICAL ANCHOR: Psalm 1:3 - "And he shall be like a tree planted by the rivers of water..."
 * ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/components/billing/PaymentHistory.jsx
 * COLLABORATION & OWNERSHIP: Wilson Khanyezi (Founder/CEO) mandated auditable payment visibility; AI Engineering (Codex) implemented it.
 */

import React, { useMemo, useState } from 'react';

/**
 * @function PaymentHistory
 * @description Renders an expandable list of normalized payment attempts.
 * @param {{payments?:Array,formatMoney?:(amount:number,currency?:string)=>string,currency?:string}} props - Payment data and formatter.
 * @returns {JSX.Element} Payment history accordion.
 * @collaboration Makes missing history explicit instead of displaying sample transactions.
 */
const PaymentHistory = ({ payments = [], formatMoney = (amount) => String(amount), currency = 'ZAR' }) => {
  const [open, setOpen] = useState(false);
  const rows = useMemo(() => (Array.isArray(payments) ? payments : []).map((item) => ({
    id: item.payment_id || item.paymentId || item.id || item.external_reference || item.externalReference || `${item.created_at || item.createdAt || ''}-${item.amount || ''}`,
    at: item.created_at || item.createdAt || item.timestamp || item.paid_at || item.paidAt,
    amount: item.amount || 0,
    method: item.method || item.payment_method || item.paymentMethod || 'manual',
    status: item.status || 'recorded',
    reference: item.external_reference || item.externalReference || item.reference || '—',
  })), [payments]);
  return (
    <section style={{ borderTop: '1px solid rgba(255,255,255,0.08)', paddingTop: 12, marginTop: 14 }}>
      <button type="button" onClick={() => setOpen((current) => !current)} aria-expanded={open} style={{ background: 'none', border: 'none', color: '#e2e8f0', padding: 0, cursor: 'pointer', fontWeight: 700 }}>
        Payment history ({rows.length}) {open ? '▴' : '▾'}
      </button>
      {open && (rows.length ? <div style={{ display: 'grid', gap: 7, marginTop: 10 }}>{rows.map((row) => <div key={row.id} style={{ display: 'grid', gridTemplateColumns: '1fr auto', gap: 10, padding: '8px 10px', background: 'rgba(15,23,42,0.72)', borderRadius: 7, fontSize: '0.72rem' }}><span><strong>{formatMoney(row.amount, currency)}</strong> · {String(row.method).replace(/_/g, ' ')} · {row.status}<br /><small style={{ color: '#94a3b8' }}>{row.reference}</small></span><time style={{ color: '#94a3b8' }}>{row.at ? new Date(row.at).toLocaleString('en-ZA') : 'Time unavailable'}</time></div>)}</div> : <p style={{ color: '#94a3b8', fontSize: '0.72rem', margin: '9px 0 0' }}>No payment attempts have been supplied by the ledger.</p>)}
    </section>
  );
};

export default PaymentHistory;

/** POST-UPDATE TODO: Replace in-invoice history with a paginated ledger endpoint when payment volumes require it. */
