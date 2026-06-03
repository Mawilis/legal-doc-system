/* eslint-disable */

const tryParseJson = (value) => {
  if (typeof value !== 'string') return value;
  const trimmed = value.trim();
  if (!trimmed || !/^[\[{]/.test(trimmed)) return value;
  try {
    return JSON.parse(trimmed);
  } catch {
    return value;
  }
};

const toArray = (value) => {
  const parsed = tryParseJson(value);
  if (Array.isArray(parsed)) return parsed;
  if (parsed && typeof parsed === 'object') return [parsed];
  if (typeof parsed === 'string' && parsed.trim()) return [{ description: parsed }];
  return [];
};

export const toMoneyNumber = (value, fallback = 0) => {
  if (value === null || value === undefined || value === '') return fallback;
  const numeric = Number(String(value).replace(/[^\d.-]/g, ''));
  return Number.isFinite(numeric) ? numeric : fallback;
};

export const formatMoney = (value, currency = 'ZAR') => {
  const amount = toMoneyNumber(value);
  return `${currency} ${amount.toLocaleString('en-ZA', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })}`;
};

export const normalizeInvoiceLineItems = (payload = {}) => {
  const source = payload.lineItems ?? payload.items ?? payload.services ?? payload.description ?? [];
  const rows = toArray(source);

  return rows.map((row, index) => {
    const item = typeof row === 'string' ? { description: row } : (row || {});
    const quantity = Math.max(toMoneyNumber(item.quantity ?? item.qty ?? 1, 1), 0);
    const unitPrice = toMoneyNumber(
      item.unitPrice ?? item.price ?? item.rate ?? item.amount ?? item.value ?? item.lineTotal,
      0
    );
    const lineTotal = toMoneyNumber(
      item.lineTotal ?? item.total ?? item.amount,
      quantity * unitPrice
    );

    const rawTaxRate = toMoneyNumber(item.taxRate ?? payload.taxRate ?? 0.15, 0.15);

    return {
      description: String(item.description ?? item.name ?? item.service ?? item.title ?? `Line item ${index + 1}`).trim(),
      quantity: quantity || 1,
      unitPrice,
      price: unitPrice,
      amount: lineTotal,
      lineTotal,
      taxRate: rawTaxRate > 1 ? rawTaxRate / 100 : rawTaxRate,
      category: item.category,
      units: item.units,
    };
  }).filter(item => item.description || item.lineTotal);
};

export const deriveInvoiceTotals = (payload = {}, lineItems = normalizeInvoiceLineItems(payload)) => {
  const subtotal = payload.subtotal !== undefined
    ? toMoneyNumber(payload.subtotal)
    : lineItems.reduce((sum, item) => sum + item.lineTotal, 0);
  const taxRate = toMoneyNumber(payload.taxRate ?? payload.vatRate ?? 15);
  const normalizedTaxRate = taxRate > 1 ? taxRate / 100 : taxRate;
  const explicitTotal = payload.totalAmount ?? payload.total ?? payload.amount;
  const totalAmount = explicitTotal !== undefined
    ? toMoneyNumber(explicitTotal)
    : subtotal + (subtotal * normalizedTaxRate);
  const taxAmount = payload.taxAmount !== undefined
    ? toMoneyNumber(payload.taxAmount)
    : Math.max(0, totalAmount - subtotal);

  return {
    subtotal,
    taxRate: normalizedTaxRate,
    taxAmount,
    totalAmount,
  };
};

export const normalizeStatementTransactions = (payload = {}) => {
  const rows = toArray(payload.transactions ?? payload.items ?? payload.lineItems ?? []);
  return rows.map((row, index) => {
    const tx = typeof row === 'string' ? { description: row } : (row || {});
    return {
      date: tx.date ?? tx.transactionDate ?? tx.createdAt ?? new Date().toISOString().slice(0, 10),
      description: String(tx.description ?? tx.memo ?? tx.reference ?? `Transaction ${index + 1}`).trim(),
      debit: toMoneyNumber(tx.debit ?? tx.charge ?? 0),
      credit: toMoneyNumber(tx.credit ?? tx.payment ?? 0),
      balance: tx.balance !== undefined ? toMoneyNumber(tx.balance) : undefined,
    };
  }).filter(tx => tx.description || tx.debit || tx.credit);
};
