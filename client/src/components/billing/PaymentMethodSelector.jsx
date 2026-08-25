/* eslint-disable */
/**
 * WILSY OS - PAYMENT METHOD SELECTOR [V1.0.0-LEDGER-TRUTH]
 * EPITOME: Captures only payment-routing metadata required to record a payment; sensitive card or bank credentials never enter BillingHUD.
 * BIBLICAL ANCHOR: Psalm 1:3 - "And he shall be like a tree planted by the rivers of water..."
 * ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/components/billing/PaymentMethodSelector.jsx
 * COLLABORATION & OWNERSHIP: Wilson Khanyezi (Founder/CEO) mandated tenant-safe billing controls; AI Engineering (Codex) implemented the metadata-only selector.
 */

import React, { useEffect, useMemo, useState } from 'react';

const METHODS = Object.freeze([
  { value: 'cash', backendValue: 'manual', label: 'Cash', field: 'receiptNumber', prompt: 'Receipt number' },
  { value: 'eft', backendValue: 'bank_transfer', label: 'EFT', field: 'reference', prompt: 'EFT reference' },
  { value: 'debit_order', backendValue: 'bank_transfer', label: 'Debit order', field: 'mandateReference', prompt: 'Mandate reference' },
  { value: 'credit_card', backendValue: 'card', label: 'Credit card', field: 'authorizationReference', prompt: 'Authorisation reference' },
  { value: 'wallet', backendValue: 'other', label: 'Wallet', field: 'walletReference', prompt: 'Wallet transaction reference' },
  { value: 'manual', backendValue: 'manual', label: 'Manual adjustment', field: 'reference', prompt: 'Internal reference' },
]);

/**
 * @function PaymentMethodSelector
 * @description Renders a payment method picker and returns a non-sensitive payment method object.
 * @param {{value?:object|string,onChange?:(value:object)=>void,disabled?:boolean}} props - Component props.
 * @returns {JSX.Element} Payment method fields.
 * @collaboration Keeps payment instruments out of browser state while preserving auditable references.
 */
const PaymentMethodSelector = ({ value = 'manual', onChange, disabled = false }) => {
  const initial = useMemo(() => (typeof value === 'object' && value ? value : { type: value }), [value]);
  const [method, setMethod] = useState(initial.selection || initial.type || 'manual');
  const [reference, setReference] = useState(initial.reference || '');
  const selected = METHODS.find((item) => item.value === method) || METHODS[5];

  useEffect(() => {
    setMethod(initial.selection || initial.type || 'manual');
    setReference(initial.reference || '');
  }, [initial]);

  /**
   * @function emit
   * @description Emits a normalized, metadata-only method payload.
   * @param {string} nextMethod - Selected payment method.
   * @param {string} nextReference - External or internal reference.
   * @returns {void}
   * @collaboration Gives the payment endpoint an auditable method without collecting credentials.
   */
  const emit = (nextMethod, nextReference) => {
    const choice = METHODS.find((item) => item.value === nextMethod) || METHODS[5];
    onChange?.({
      type: choice.backendValue,
      selection: choice.value,
      reference: String(nextReference || '').trim(),
    });
  };

  return (
    <div style={{ display: 'grid', gap: 8, minWidth: 190 }}>
      <label style={{ fontSize: '0.62rem', color: '#94a3b8', textTransform: 'uppercase' }}>
        Payment method
      </label>
      <select
        value={method}
        disabled={disabled}
        onChange={(event) => { const next = event.target.value; setMethod(next); emit(next, reference); }}
        style={{ padding: '8px 10px', background: '#0f172a', color: '#f8fafc', border: '1px solid rgba(255,255,255,0.12)', borderRadius: 6 }}
      >
        {METHODS.map((item) => <option key={item.value} value={item.value}>{item.label}</option>)}
      </select>
      <input
        value={reference}
        disabled={disabled}
        onChange={(event) => { const next = event.target.value; setReference(next); emit(method, next); }}
        placeholder={selected.prompt}
        aria-label={selected.prompt}
        style={{ padding: '8px 10px', background: '#0f172a', color: '#f8fafc', border: '1px solid rgba(255,255,255,0.12)', borderRadius: 6 }}
      />
      <small style={{ color: '#64748b', fontSize: '0.58rem' }}>Store a reference only; do not enter card, bank, or wallet credentials.</small>
    </div>
  );
};

export default PaymentMethodSelector;

/** POST-UPDATE TODO: Add provider-token support only after a PCI-scoped payment service is available. */
