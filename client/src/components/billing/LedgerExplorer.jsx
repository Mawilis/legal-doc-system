/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS – LEDGER EXPLORER [V4.5.0-CSV-EXPORT]                                                                              ║
 * ║ [FORENSIC SEALING | TELEMETRY | ANOMALY DETECTION | SOVEREIGNTY INDEX | CREATOR LINEAGE | DUAL-PIPELINE | POPIA AUDIT]              ║
 * ║ [PROMETHEUS METRICS INTEGRATION]                                                                                                      ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 4.5.0-CSV-EXPORT | PRODUCTION READY                                                                               ║
 * ║ EPITOME: Sovereign ledger analytics cockpit — full file structure preserved. Creator lineage, Sovereignty Index, forensic sealing,  ║
 * ║          dual platform/client pipeline isolation, and POPIA §19 audit-trail hygiene. Now integrates with Prometheus counters.        ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/components/billing/LedgerExplorer.jsx                               ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN‑OFF:                                                                                                ║
 * ║ • Wilson Khanyezi (CEO/Lead Architect) – Mandated creator lineage, Sovereignty Index, and Prometheus integration.                   ║
 * ║ • AI Engineering – V4.5.0: Added CSV export (wave 14) with `exportLedgerCsv` helper and toolbar button.                            ║
 * ║ • AI Engineering – V4.3.0: Added HTTP calls to /api/metrics/ledger to increment ledgerViewCount and ledgerExportCount.              ║
 * ║ • AI Engineering – V4.2.1: dual-pipeline platform endpoints first, platform field normalize, POPIA-minimised anomaly payloads.     ║
 * ║ • Compliance: POPIA §19 · GDPR §32 · SOC2 §CC7.2 · ISO 27001                                                                        ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 🔧 CHANGES (v4.5.0):                                                                                                                 ║
 * ║   1. Added `exportLedgerCsv(rows, filename)` helper to generate CSV blob and download.                                              ║
 * ║   2. Added `handleExportCsv` callback to export filtered invoices (respects current filters).                                      ║
 * ║   3. Added "CSV" button to the toolbar, disabled when no rows or loading.                                                          ║
 * ║   4. Preserved all existing features: SovereigntyIndex, anomalies, pickCreatedBy, ForensicDetailModal, charts, table.              ║
 * ║   5. No new metrics – CSV export is a client-side operational export and does not increment counters.                              ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { createPortal } from 'react-dom';
import { sha3_512 } from 'js-sha3';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend, AreaChart, Area,
} from 'recharts';
import {
  RefreshCw, Search, TrendingUp, PieChart as PieIcon, List,
  Shield, User, Hash, Building2, X, Download, Copy, CheckCircle, AlertTriangle,
  Gauge, Zap, Globe, Award,
} from 'lucide-react';
import hudStyles from './BillingHUD.module.css';
import { broadcastTelemetry } from '../../utils/telemetryHelper';

// ─── CONSTANTS ──────────────────────────────────────────────────────────────
const STATUS_COLORS = {
  paid: '#22c55e',
  pending: '#eab308',
  issued: '#d4af37',
  overdue: '#ef4444',
  cancelled: '#64748b',
  draft: '#38bdf8',
  unknown: '#94a3b8',
};

const STATUS_LABEL = {
  paid: 'Paid',
  pending: 'Pending',
  issued: 'Issued',
  overdue: 'Overdue',
  cancelled: 'Cancelled',
  draft: 'Draft',
  unknown: 'Unknown',
};

const NORMALIZED_STATUSES = Object.freeze({
  ISSUED: 'issued',
  issued: 'issued',
  OPEN: 'issued',
  open: 'issued',
  SENT: 'issued',
  POSTED: 'issued',
  PARTIALLY_PAID: 'pending',
  PAID: 'paid',
  paid: 'paid',
  OVERDUE: 'overdue',
  PAST_DUE: 'overdue',
  past_due: 'overdue',
  VOID: 'cancelled',
  VOIDED: 'cancelled',
  voided: 'cancelled',
  CANCELLED: 'cancelled',
  cancelled: 'cancelled',
  DRAFT: 'draft',
  DISPUTED: 'overdue',
  LEGAL_HOLD: 'overdue',
});

const PAGE_SIZE = 15;
const DEFAULT_FILTERS = {
  status: 'all',
  period: '30d',
  search: '',
};

// ─── HELPERS ─────────────────────────────────────────────────────────────────

function formatCurrency(amount, currency = 'ZAR') {
  try {
    return new Intl.NumberFormat('en-ZA', {
      style: 'currency',
      currency: currency || 'ZAR',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(Number(amount) || 0);
  } catch {
    return `R ${Number(amount || 0).toLocaleString('en-ZA', { minimumFractionDigits: 2 })}`;
  }
}

function formatInvoiceDate(value) {
  if (value == null || Number.isNaN(new Date(value).getTime())) return '—';
  return new Intl.DateTimeFormat('en-ZA', {
    day: '2-digit', month: 'short', year: 'numeric',
  }).format(new Date(value));
}

function formatDateTime(value) {
  if (value == null || Number.isNaN(new Date(value).getTime())) return '—';
  return new Intl.DateTimeFormat('en-ZA', {
    day: '2-digit', month: 'short', year: 'numeric',
    hour: '2-digit', minute: '2-digit',
  }).format(new Date(value));
}

/**
 * Generate SHA3‑512 proof hash for an audit payload.
 */
function generateSeal(payload) {
  const data = JSON.stringify(payload, Object.keys(payload).sort());
  return sha3_512(data).toUpperCase();
}

/**
 * Generate an evidence package for an invoice.
 * @param {Object} invoice – normalized invoice.
 * @param {string} action – 'VIEW' or 'EXPORT'.
 * @param {Object} extra – additional metadata.
 * @returns {Object} sealed evidence package.
 */
function generateEvidencePackage(invoice, action = 'VIEW', extra = {}) {
  const payload = {
    invoiceId: invoice.id,
    invoiceNumber: invoice.invoiceNumber,
    tenantId: invoice.tenantId || 'MASTER',
    action,
    status: invoice.status,
    amount: invoice.totalAmount,
    currency: invoice.currency,
    issuerType: invoice.issuerType,
    identitySource: invoice.identitySource,
    createdBy: invoice.createdBy,
    traceId: invoice.traceId,
    sealHash: invoice.sealHash,
    timestamp: new Date().toISOString(),
    ...extra,
  };
  const proofHash = generateSeal(payload);
  return { ...payload, proofHash };
}

/**
 * Enhanced extractor for creator metadata.
 * Searches every conceivable field, including nested objects and arrays.
 * Returns { createdBy, createdById, createdByEmail, createdByRole, createdAt, sealedAt, createdBySystem? }.
 */
function pickCreatedBy(invoice = {}) {
  // Helper to safely traverse nested paths.
  const getDeep = (obj, path) => {
    if (!obj || typeof obj !== 'object') return null;
    const parts = path.split('.');
    let current = obj;
    for (const part of parts) {
      if (current == null || typeof current !== 'object') return null;
      current = current[part];
    }
    return current;
  };

  const deepFind = (obj, keyPattern, depth = 0) => {
    if (!obj || typeof obj !== 'object' || depth > 10) return null;
    for (const [k, v] of Object.entries(obj)) {
      if (k.toLowerCase().includes(keyPattern.toLowerCase())) {
        if (typeof v === 'string' && v.trim()) return v;
        if (v && typeof v === 'object') {
          if (v.name && typeof v.name === 'string') return v.name;
          if (v.fullName && typeof v.fullName === 'string') return v.fullName;
          if (v.displayName && typeof v.displayName === 'string') return v.displayName;
          if (v.id && typeof v.id === 'string') return v.id;
          if (v.email && typeof v.email === 'string') return v.email;
          const firstString = Object.values(v).find((val) => typeof val === 'string' && val.trim());
          if (firstString) return firstString;
        }
      }
      if (v && typeof v === 'object') {
        const nested = deepFind(v, keyPattern, depth + 1);
        if (nested) return nested;
      }
    }
    return null;
  };

  const asPerson = (val) => {
    if (!val) return null;
    if (typeof val === 'string' && val.trim()) {
      return { name: val.trim() };
    }
    if (typeof val === 'object' && !Array.isArray(val)) {
      const name =
        val.name || val.fullName || val.displayName || val.username || val.userName || val.email || null;
      return {
        name: name ? String(name).trim() : null,
        id: val.id || val.userId || val._id || val.uid || null,
        email: val.email || val.userEmail || null,
        role: val.role || val.userRole || val.roles?.[0] || null,
      };
    }
    return null;
  };

  // Priority ordered sources for platform + client invoices
  const personCandidates = [];
  const pushPerson = (raw) => {
    const p = asPerson(raw);
    if (p && (p.name || p.id || p.email)) personCandidates.push(p);
  };

  // 1) Explicit top-level creator stamps (post V7.4 / V34 backend)
  pushPerson(invoice.createdBy);
  pushPerson({
    name: invoice.createdByName,
    id: invoice.createdById || invoice.createdByUserId,
    email: invoice.createdByEmail,
    role: invoice.createdByRole,
  });
  pushPerson(invoice.issuedBy);
  pushPerson(invoice.operator);
  pushPerson(invoice.actor);
  pushPerson(invoice.author);
  pushPerson(invoice.performer);
  pushPerson(invoice.user);

  // 2) Nested identity / metadata bags (platform often stores here)
  const bags = [
    invoice.metadata,
    invoice.invoiceIdentity,
    invoice.brandingNexus,
    invoice.audit,
    invoice.provenance,
    invoice.createdByUser,
  ].filter(Boolean);
  for (const bag of bags) {
    pushPerson(bag.createdBy);
    pushPerson(bag.actor);
    pushPerson(bag.operator);
    pushPerson(bag.user);
    pushPerson(bag.issuer);
    if (bag.createdByName || bag.createdById || bag.createdByEmail) {
      pushPerson({
        name: bag.createdByName,
        id: bag.createdById,
        email: bag.createdByEmail,
        role: bag.createdByRole,
      });
    }
  }

  // 3) auditTrail / forensicChain — prefer CREATE / ISSUE / GENESIS entries
  const trails = []
    .concat(Array.isArray(invoice.auditTrail) ? invoice.auditTrail : [])
    .concat(Array.isArray(invoice.forensicChain) ? invoice.forensicChain : [])
    .concat(Array.isArray(invoice.auditLog) ? invoice.auditLog : []);

  const createLike = trails.filter((e) => {
    const a = String(e?.action || e?.event || e?.type || '').toUpperCase();
    return /CREATE|ISSUE|GENESIS|STAMP|SEAL|ONBOARD/.test(a);
  });
  const orderedTrail = createLike.length ? createLike.concat(trails) : trails;
  for (const entry of orderedTrail) {
    if (!entry || typeof entry !== 'object') continue;
    pushPerson(entry.performer);
    pushPerson(entry.actor);
    pushPerson(entry.user);
    pushPerson(entry.createdBy);
    pushPerson({
      name: entry.userName || entry.performerName || entry.actorName,
      id: entry.userId || entry.actorId || entry.performerId,
      email: entry.email || entry.userEmail,
      role: entry.role || entry.userRole,
    });
  }

  // 4) Recursive last-resort name search
  if (!personCandidates.length) {
    for (const key of ['creator', 'author', 'operator', 'actor', 'performer']) {
      const found = deepFind(invoice, key);
      if (found) pushPerson(found);
    }
  }

  // Choose best person
  const best =
    personCandidates.find((p) => p.name && p.name !== 'System' && p.name !== '—') ||
    personCandidates.find((p) => p.email) ||
    personCandidates.find((p) => p.id) ||
    personCandidates[0] ||
    null;

  let name = best?.name || '—';
  let userId = best?.id ? String(best.id) : '—';
  let email = best?.email ? String(best.email) : '—';
  let role = best?.role ? String(best.role) : '—';

  // Platform root honest fallback when no stamp exists on legacy docs
  const pipelineHint = String(
    invoice.issuerType || invoice.invoiceIdentity?.issuerType || invoice.metadata?.issuerType || ''
  ).toLowerCase();
  const isPlatformish =
    pipelineHint.includes('platform') ||
    pipelineHint.includes('root') ||
    String(invoice.identitySource || '').toUpperCase().includes('PLATFORM');

  if (name === '—' && isPlatformish) {
    name = 'Platform system';
    if (role === '—') role = 'SYSTEM';
  }

  const createdAt =
    getDeep(invoice, 'createdAt') ||
    getDeep(invoice, 'issueDate') ||
    getDeep(invoice, 'issuedAt') ||
    getDeep(invoice, 'issued') ||
    getDeep(invoice, 'metadata.createdAt') ||
    null;

  let sealedAt =
    getDeep(invoice, 'sealedAt') ||
    getDeep(invoice, 'metadata.sealedAt') ||
    getDeep(invoice, 'issuedAt') ||
    null;

  // If sealed hash exists but sealedAt missing, use createdAt as seal timestamp proxy
  const sealHash =
    invoice.sealHash || invoice.proofHash || invoice.merkleRoot || invoice.metadata?.sealHash || '';
  if (!sealedAt && sealHash && createdAt) sealedAt = createdAt;

  const isSystem =
    name === 'System' ||
    name === 'Platform system' ||
    getDeep(invoice, 'system') === true ||
    getDeep(invoice, 'generatedBy') === 'system';

  return {
    createdBy: name,
    createdById: userId,
    createdByEmail: email,
    createdByRole: role,
    createdAt: createdAt ? new Date(createdAt) : null,
    sealedAt: sealedAt ? new Date(sealedAt) : null,
    createdBySystem: isSystem,
  };
}

function classifyIssuer(invoice = {}) {
  const raw = String(
    invoice.issuerType ||
    invoice.invoiceIdentity?.issuerType ||
    invoice.metadata?.issuerType ||
    invoice.issuerMode ||
    invoice.billingMode ||
    ''
  ).toLowerCase().trim();

  const docClass = String(invoice.documentClass || invoice.metadata?.documentClass || '').toUpperCase();
  const modelHint = String(invoice.model || invoice._model || invoice.collection || '').toLowerCase();

  if (raw.includes('platform') || raw === 'root' || raw === 'platform_root' || modelHint.includes('platform')) {
    return 'platform';
  }
  if (raw.includes('client') || raw === 'tenant_client' || docClass === 'CLIENT') {
    return 'client';
  }
  return 'platform';
}

function normalizeInvoice(invoice = {}) {
  const rawStatus = String(invoice.status || invoice.invoiceStatus || 'DRAFT').toUpperCase();
  const pipeline = classifyIssuer(invoice);
  const creator = pickCreatedBy(invoice);

  return {
    ...invoice,
    id: invoice.id || invoice._id || invoice.invoiceId || invoice.invoiceNumber,
    invoiceNumber: invoice.invoiceNumber || invoice.number || invoice.id || invoice._id || '—',
    clientName:
      invoice.clientName ||
      invoice.customerName ||
      invoice.recipientName ||
      invoice.counterparty ||
      invoice.businessName ||
      invoice.recipientTenantId ||
      '',
    issuingEntity:
      invoice.issuingEntity ||
      invoice.sellerName ||
      invoice.invoiceIdentity?.legalName ||
      invoice.brandingNexus?.legalEntity ||
      (pipeline === 'platform' ? 'Wilsy (Pty) Ltd' : '—'),
    totalAmount: (() => {
      const lines = invoice.line_items || invoice.lineItems || [];
      const lineSum = Array.isArray(lines)
        ? lines.reduce((s, li) => s + Number(li.amount ?? li.line_total ?? (Number(li.quantity || 1) * Number(li.unit_price ?? li.unitPrice ?? 0)) ?? 0), 0)
        : 0;
      const raw = Number(invoice.total_amount ?? invoice.totalAmount ?? invoice.total ?? invoice.amount ?? 0);
      return (raw > 0 ? raw : lineSum) || 0;
    })(),
    outstandingAmount: Number(
      invoice.outstandingAmount ?? invoice.balanceDue ?? invoice.amountDue ??
      ((String(rawStatus) === 'PAID') ? 0 : (invoice.totalAmount ?? invoice.amount ?? 0))
    ) || 0,
    currency: invoice.currency || 'ZAR',
    status: (() => {
      const mapped = NORMALIZED_STATUSES[rawStatus] || String(rawStatus).toLowerCase();
      if (mapped === 'open' || rawStatus === 'OPEN') return 'issued';
      return mapped;
    })(),
    rawStatus,
    issueDate: invoice.issueDate || invoice.issuedAt || invoice.issued || invoice.createdAt || invoice.sealedAt || null,
    dueDate: invoice.dueDate || invoice.dueAt || invoice.due || null,
    sealedAt: invoice.sealedAt || invoice.issuedAt || invoice.metadata?.sealedAt || null,
    createdAt: invoice.createdAt || invoice.issueDate || null,
    issuerType: pipeline === 'client' ? 'tenant_client' : 'platform',
    pipeline,
    identitySource:
      invoice.metadata?.identitySource ||
      invoice.invoiceIdentity?.identitySource ||
      invoice.identitySource ||
      (pipeline === 'client' ? 'TENANT_CONTEXT' : 'PLATFORM_ROOT'),
    sealHash: invoice.sealHash || invoice.proofHash || invoice.merkleRoot || invoice.metadata?.sealHash || '',
    traceId: invoice.traceId || invoice.forensicTraceId || invoice.metadata?.traceId || '',
    ...creator,
    tenantId: invoice.tenantId || invoice.recipientTenantId || '',
    jurisdiction: invoice.jurisdiction || invoice.metadata?.jurisdiction || 'ZA',
  };
}

function daysPastDue(invoice) {
  if (!invoice.dueDate) return 0;
  const due = new Date(invoice.dueDate).getTime();
  if (!Number.isFinite(due)) return 0;
  if (invoice.status === 'paid' || invoice.status === 'cancelled') return 0;
  const diff = Date.now() - due;
  return diff > 0 ? Math.floor(diff / 86400000) : 0;
}

function calculateLedgerAnalytics(invoiceList = []) {
  const statusMap = {};
  const monthlyMap = {};
  let totalVolume = 0;
  let paidVolume = 0;
  let outstanding = 0;
  const aging = { current: 0, d1_30: 0, d31_60: 0, d61_90: 0, d90p: 0 };

  invoiceList.forEach((invoice) => {
    const status = invoice.status || 'unknown';
    statusMap[status] = (statusMap[status] || 0) + 1;
    const amount = Number(invoice.totalAmount || 0);
    totalVolume += amount;
    if (status === 'paid') paidVolume += amount;
    else if (status !== 'cancelled') {
      const open = Number(invoice.outstandingAmount || amount);
      outstanding += open;
      const d = daysPastDue(invoice);
      if (d <= 0) aging.current += open;
      else if (d <= 30) aging.d1_30 += open;
      else if (d <= 60) aging.d31_60 += open;
      else if (d <= 90) aging.d61_90 += open;
      else aging.d90p += open;
    }

    const issueDate = invoice.issueDate ? new Date(invoice.issueDate) : null;
    if (issueDate && !Number.isNaN(issueDate.getTime())) {
      const monthKey = issueDate.toISOString().slice(0, 7);
      monthlyMap[monthKey] = (monthlyMap[monthKey] || 0) + amount;
    }
  });

  return {
    statusCounts: Object.entries(statusMap).map(([name, value]) => ({
      name,
      label: STATUS_LABEL[name] || name,
      value,
    })),
    monthlyTotals: Object.entries(monthlyMap)
      .map(([month, total]) => ({ month, total }))
      .sort((a, b) => a.month.localeCompare(b.month)),
    aging: [
      { bucket: 'Current', total: aging.current },
      { bucket: '1–30d', total: aging.d1_30 },
      { bucket: '31–60d', total: aging.d31_60 },
      { bucket: '61–90d', total: aging.d61_90 },
      { bucket: '90d+', total: aging.d90p },
    ],
    totalVolume,
    paidVolume,
    outstanding,
    count: invoiceList.length,
  };
}

function inPeriod(invoice, period) {
  const p = String(period || 'all').toLowerCase();
  if (!p || p === 'all') return true;
  const raw = invoice.issueDate;
  if (!raw) return false;
  const ts = new Date(raw).getTime();
  if (!Number.isFinite(ts)) return false;
  const now = new Date();
  const startOfToday = new Date(now.getFullYear(), now.getMonth(), now.getDate()).getTime();
  if (p === 'today') return ts >= startOfToday;
  if (p === '7d') return ts >= now.getTime() - 7 * 86400000;
  if (p === '30d') return ts >= now.getTime() - 30 * 86400000;
  if (p === '90d') return ts >= now.getTime() - 90 * 86400000;
  if (p === 'ytd') return ts >= new Date(now.getFullYear(), 0, 1).getTime();
  return true;
}

const chartTooltipStyle = {
  backgroundColor: 'rgba(15,23,42,0.96)',
  border: '1px solid rgba(212,175,55,0.4)',
  borderRadius: 10,
  color: '#e2e8f0',
  fontSize: 12,
  boxShadow: '0 12px 40px rgba(0,0,0,0.45)',
  padding: '10px 12px',
};

// ─── DETECT ANOMALIES (top-level function) ─────────────────────────────────

function detectAnomalies(invoices) {
  // POPIA §19 / GDPR §32: anomaly payloads carry operational identifiers only —
  // no personal email/name dumps in telemetry surfaces.
  const anomalies = [];
  const seenNumbers = new Map();

  for (const inv of invoices) {
    const number = inv.invoiceNumber;
    if (number && number !== '—') {
      if (seenNumbers.has(number)) {
        anomalies.push({
          type: 'DUPLICATE_INVOICE_NUMBER',
          severity: 'WARNING',
          invoiceId: inv.id,
          invoiceNumber: number,
          duplicateOf: seenNumbers.get(number),
          description: `Duplicate invoice number ${number}`,
          complianceTag: 'POPIA_MINIMAL',
        });
      } else {
        seenNumbers.set(number, inv.id);
      }
    }

    if (inv.status === 'overdue') {
      const days = daysPastDue(inv);
      if (days > 90) {
        anomalies.push({
          type: 'EXTREME_OVERDUE',
          severity: 'CRITICAL',
          invoiceId: inv.id,
          invoiceNumber: inv.invoiceNumber,
          daysOverdue: days,
          description: `Invoice overdue ${days} days`,
          complianceTag: 'POPIA_MINIMAL',
        });
      }
    }

    // Missing forensic seal on issued commercial document
    if (inv.status !== 'draft' && inv.status !== 'cancelled' && !(inv.sealHash && String(inv.sealHash).length > 8)) {
      anomalies.push({
        type: 'SEAL_MISSING',
        severity: 'WARNING',
        invoiceId: inv.id,
        invoiceNumber: inv.invoiceNumber,
        description: 'Issued invoice lacks cryptographic seal',
        complianceTag: 'SOC2_INTEGRITY',
      });
    }
  }

  const total = invoices.length;
  const overdue = invoices.filter(i => i.status === 'overdue').length;
  if (total > 0 && overdue / total > 0.3) {
    anomalies.push({
      type: 'OVERDUE_SPIKE',
      severity: 'WARNING',
      description: `Overdue rate ${Math.round(overdue / total * 100)}% exceeds 30% threshold`,
      total,
      overdue,
      complianceTag: 'POPIA_MINIMAL',
    });
  }

  return anomalies;
}

// ─── SOVEREIGNTY INDEX COMPONENT ──────────────────────────────────────────

function SovereigntyIndex({ invoices }) {
  const total = invoices.length;
  if (total === 0) return null;

  const withSeal = invoices.filter(inv => inv.sealHash && inv.sealHash.length > 0).length;
  const withIdentity = invoices.filter(inv => inv.identitySource && inv.identitySource !== '—').length;
  const complianceScore = Math.round(((withSeal / total) * 0.5 + (withIdentity / total) * 0.5) * 100);

  const overdue = invoices.filter(inv => inv.status === 'overdue').length;
  const dso = overdue > 0 ? (overdue / total) * 90 : 0;
  const collectionScore = Math.max(0, Math.min(100, 100 - (dso / 90) * 100));

  const jurisdictions = invoices.map(inv => inv.jurisdiction || 'ZA');
  const jurisCounts = {};
  jurisdictions.forEach(j => { jurisCounts[j] = (jurisCounts[j] || 0) + 1; });
  const totalJuris = Object.keys(jurisCounts).length;
  let shannon = 0;
  for (const j in jurisCounts) {
    const p = jurisCounts[j] / total;
    shannon -= p * Math.log(p);
  }
  const maxShannon = Math.log(totalJuris || 1);
  const jurisdictionScore = totalJuris > 1 ? Math.round((shannon / maxShannon) * 100) : totalJuris === 1 ? 50 : 0;

  const automated = invoices.filter(inv => inv.traceId && inv.traceId.length > 0).length;
  const automationScore = Math.round((automated / total) * 100);

  const index = Math.round(
    0.40 * complianceScore +
    0.30 * collectionScore +
    0.20 * jurisdictionScore +
    0.10 * automationScore
  );

  const grade = index >= 80 ? 'Sovereign' : index >= 60 ? 'Institutional' : 'Operational Risk';

  return (
    <div style={{
      padding: '16px 18px',
      borderRadius: 12,
      border: '1px solid rgba(212,175,55,0.25)',
      background: 'linear-gradient(135deg, rgba(15,23,42,0.6), rgba(0,0,0,0.4))',
      marginBottom: 16,
      display: 'grid',
      gridTemplateColumns: '1fr 1fr 1fr',
      gap: 16,
    }}>
      <div style={{ textAlign: 'center' }}>
        <div style={{ fontSize: '0.6rem', color: '#94a3b8', letterSpacing: '0.12em', textTransform: 'uppercase' }}>
          Sovereignty Index
        </div>
        <div style={{
          width: 100,
          height: 100,
          borderRadius: '50%',
          background: `conic-gradient(
            ${index >= 80 ? '#d4af37' : index >= 60 ? '#94a3b8' : '#ef4444'} ${index * 3.6}deg,
            rgba(255,255,255,0.05) 0deg
          )`,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          margin: '6px auto 0',
          boxShadow: '0 0 20px rgba(212,175,55,0.2)',
        }}>
          <div style={{
            width: 80,
            height: 80,
            borderRadius: '50%',
            background: '#0b0b0f',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
          }}>
            <span style={{ fontSize: '1.5rem', fontWeight: 800, color: '#f0d78c' }}>{index}</span>
            <span style={{ fontSize: '0.5rem', color: '#94a3b8', textTransform: 'uppercase' }}>{grade}</span>
          </div>
        </div>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
        <div style={{ fontSize: '0.6rem', color: '#94a3b8', letterSpacing: '0.1em', marginBottom: 6, textTransform: 'uppercase' }}>
          Component breakdown
        </div>
        {[
          { label: 'Compliance', score: complianceScore, weight: 40, color: '#d4af37' },
          { label: 'Collection', score: collectionScore, weight: 30, color: '#22d3ee' },
          { label: 'Jurisdiction', score: jurisdictionScore, weight: 20, color: '#8b5cf6' },
          { label: 'Automation', score: automationScore, weight: 10, color: '#64748b' },
        ].map((c) => (
          <div key={c.label} style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 4 }}>
            <span style={{ width: 90, fontSize: '0.6rem', color: '#cbd5e1', textTransform: 'uppercase' }}>{c.label}</span>
            <div style={{ flex: 1, height: 4, background: 'rgba(255,255,255,0.08)', borderRadius: 2 }}>
              <div style={{ width: `${c.score}%`, height: '100%', background: c.color, borderRadius: 2 }} />
            </div>
            <span style={{ fontSize: '0.6rem', color: '#f1f5f9', width: 32, textAlign: 'right' }}>{c.score}%</span>
          </div>
        ))}
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'flex-end' }}>
        <div style={{
          padding: '4px 12px',
          borderRadius: 999,
          background: index >= 80 ? 'rgba(212,175,55,0.2)' : index >= 60 ? 'rgba(148,163,184,0.2)' : 'rgba(239,68,68,0.2)',
          border: `1px solid ${index >= 80 ? '#d4af37' : index >= 60 ? '#94a3b8' : '#ef4444'}44`,
          color: index >= 80 ? '#f0d78c' : index >= 60 ? '#cbd5e1' : '#fca5a5',
          fontSize: '0.65rem',
          fontWeight: 700,
          letterSpacing: '0.06em',
          textTransform: 'uppercase',
        }}>
          {grade}
        </div>
        <div style={{ marginTop: 8, fontSize: '0.55rem', color: '#64748b', textAlign: 'right' }}>
          {index >= 80 ? '✅ Sovereign grade' : index >= 60 ? '⚡ Institutional grade' : '⚠️ Operational risk'}
        </div>
      </div>
    </div>
  );
}

// ─── MAIN COMPONENT ─────────────────────────────────────────────────────────

const LedgerExplorer = ({
  tenantId,
  sovereignClient: clientProp,
  mode = 'PLATFORM',
  businessName = 'Business',
  onOpenLedger,
  userRole = 'admin',
}) => {
  const [invoices, setInvoices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedInvoice, setSelectedInvoice] = useState(null);
  const [filters, setFilters] = useState(DEFAULT_FILTERS);
  const [isDetailOpen, setIsDetailOpen] = useState(false);
  const [page, setPage] = useState(0);
  const [isolationMeta, setIsolationMeta] = useState({ requested: '', applied: 0, dropped: 0 });
  const [anomalies, setAnomalies] = useState([]);
  const [traceId] = useState(() => `LEDGER-${Date.now().toString(16)}-${Math.random().toString(36).slice(2, 6)}`);

  const isClientMode = String(mode).toUpperCase() === 'CLIENT';
  const kennelShard = 'EOS_PRIMARY';

  // ─── Telemetry via broadcastTelemetry ────────────────────────────────────
  const incrementCounter = useCallback((counterName, labels = {}) => {
    broadcastTelemetry(
      tenantId || 'GLOBAL',
      'LEDGER',
      counterName,
      'LedgerExplorer',
      { ...labels, traceId }
    );
  }, [tenantId, traceId]);

  // ─── Prometheus metrics via HTTP POST ────────────────────────────────────
  const incrementMetric = useCallback((action, invoiceId = '') => {
    // Non‑blocking; swallow errors
    const payload = {
      action, // 'view' or 'export'
      tenantId: tenantId || 'GLOBAL',
      mode: isClientMode ? 'CLIENT' : 'PLATFORM',
      invoiceId,
      timestamp: new Date().toISOString(),
    };
    fetch('/api/metrics/ledger', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    }).catch(() => {}); // Ignore failures – metrics are not critical for UX
  }, [tenantId, isClientMode]);

  // ─── Fetch Invoices ──────────────────────────────────────────────────────
  const fetchInvoices = useCallback(async () => {
    setLoading(true);
    setError(null);
    const startTime = performance.now();
    try {
      let client = clientProp;
      if (!client) {
        try {
          const mod = await import('../../utils/sovereignClient');
          client = mod.default || mod.sovereignClient;
        } catch {
          client = null;
        }
      }
      if (!client?.get) throw new Error('Billing service is not available');

      const issuerType = isClientMode ? 'tenant_client' : 'platform';
      let rows = [];
      let usedEndpoint = '';

      const headers = {
        'X-Tenant-ID': String(tenantId || ''),
        'X-Invoice-Pipeline': issuerType,
        'X-Issuer-Type': issuerType,
        'X-Kennel-Shard': kennelShard,
        'X-Kennel-Role': userRole || 'admin',
        'X-Trace-ID': traceId,
      };

      const extractRows = (payload) => {
        const data = payload?.data || payload || {};
        if (Array.isArray(data.items)) return data.items;
        if (Array.isArray(data.data)) return data.data;
        if (Array.isArray(data.invoices)) return data.invoices;
        if (Array.isArray(data.results)) return data.results;
        if (Array.isArray(data)) return data;
        return [];
      };

      const tryGet = async (path) => {
        const response = await client.get(path, { headers });
        const extracted = extractRows(response?.data ?? response);
        if (extracted.length || response) {
          usedEndpoint = path.split('?')[0];
          return extracted;
        }
        return [];
      };

      const tid = encodeURIComponent(String(tenantId || ''));
      const candidates = isClientMode
        ? [
          `/billing/invoices/search?tenantId=${tid}&issuerType=tenant_client&limit=500&offset=0`,
          `/invoices?tenantId=${tid}&limit=500`,
          `/billing/invoices?tenantId=${tid}&limit=500`,
        ]
        : [
          `/platform/invoices?tenantId=${tid}&limit=100`,
          `/billing/platform/invoices?tenantId=${tid}&limit=100`,
          `/billing/invoices/search?tenantId=${tid}&issuerType=platform&limit=500&offset=0`,
          `/invoices?tenantId=${tid}&limit=500`,
        ];

      for (const path of candidates) {
        try {
          const got = await tryGet(path);
          if (got.length > 0) {
            rows = got;
            break;
          }
          if (!rows.length && usedEndpoint) {
            rows = got;
          }
        } catch {
          /* try next endpoint */
        }
      }

      if (!usedEndpoint) usedEndpoint = candidates[0].split('?')[0];

      const normalized = rows.map(normalizeInvoice).filter((inv) => inv.id);
      const gated = normalized.filter((inv) =>
        isClientMode ? inv.pipeline === 'client' : inv.pipeline === 'platform'
      );
      setIsolationMeta({
        requested: issuerType,
        applied: gated.length,
        dropped: normalized.length - gated.length,
        endpoint: usedEndpoint,
      });
      setInvoices(gated);

      const detected = detectAnomalies(gated);
      setAnomalies(detected);

      const latency = performance.now() - startTime;
      incrementCounter('ledgerViewCount', {
        mode: isClientMode ? 'CLIENT' : 'PLATFORM',
        tenantId: String(tenantId || 'GLOBAL'),
        count: gated.length,
        latency: Math.round(latency),
      });

      setPage(0);
    } catch (err) {
      setError(err?.response?.data?.message || err?.message || 'Unable to load analytics.');
      setInvoices([]);
    } finally {
      setLoading(false);
    }
  }, [clientProp, tenantId, isClientMode, userRole, traceId, kennelShard, incrementCounter]);

  useEffect(() => { fetchInvoices(); }, [fetchInvoices]);
  useEffect(() => { setPage(0); }, [filters.status, filters.period, filters.search, mode]);

  // ─── Filtered Invoices ───────────────────────────────────────────────────
  const filteredInvoices = useMemo(() => {
    let result = invoices.filter((inv) =>
      isClientMode ? inv.pipeline === 'client' : inv.pipeline === 'platform'
    );
    if (filters.status !== 'all') {
      result = result.filter((inv) => inv.status === filters.status);
    }
    result = result.filter((inv) => inPeriod(inv, filters.period));
    if (filters.search.trim()) {
      const term = filters.search.trim().toLowerCase();
      result = result.filter(
        (inv) =>
          String(inv.invoiceNumber || '').toLowerCase().includes(term) ||
          String(inv.clientName || '').toLowerCase().includes(term) ||
          String(inv.issuingEntity || '').toLowerCase().includes(term) ||
          String(inv.createdBy || '').toLowerCase().includes(term) ||
          String(inv.traceId || '').toLowerCase().includes(term)
      );
    }
    result.sort((a, b) => {
      const dateA = a.issueDate ? new Date(a.issueDate).getTime() : 0;
      const dateB = b.issueDate ? new Date(b.issueDate).getTime() : 0;
      return dateB - dateA;
    });
    return result;
  }, [invoices, filters, isClientMode]);

  const analytics = useMemo(() => calculateLedgerAnalytics(filteredInvoices), [filteredInvoices]);
  const pageCount = Math.max(1, Math.ceil(filteredInvoices.length / PAGE_SIZE));
  const safePage = Math.min(page, pageCount - 1);
  const paged = filteredInvoices.slice(safePage * PAGE_SIZE, safePage * PAGE_SIZE + PAGE_SIZE);
  const accent = isClientMode ? '#22d3ee' : '#d4af37';

  const handleFilterChange = (e) => {
    const { name, value } = e.target;
    setFilters((prev) => ({ ...prev, [name]: value }));
  };

  // ─── Handlers ────────────────────────────────────────────────────────────
  const handleViewInvoice = useCallback((invoice) => {
    const evidence = generateEvidencePackage(invoice, 'VIEW', { traceId });
    setSelectedInvoice(invoice);
    setIsDetailOpen(true);

    // Increment Prometheus counter
    incrementMetric('view', invoice.id);

    // Broadcast telemetry (existing)
    incrementCounter('ledgerViewCount', {
      mode: isClientMode ? 'CLIENT' : 'PLATFORM',
      tenantId: String(tenantId || 'GLOBAL'),
      invoiceId: invoice.id,
    });
    console.info('[LEDGER] Evidence package:', evidence);
  }, [isClientMode, tenantId, incrementCounter, incrementMetric, traceId]);

  const handleExportCsv = useCallback(() => {
    try {
      exportLedgerCsv(filteredInvoices || [], `wilsy-ledger-${Date.now()}.csv`);
      showBillingToast(`Exported ${(filteredInvoices || []).length} rows`, 'ok');
    } catch (err) {
      showBillingToast(err?.message || 'CSV export failed', 'danger');
    }
  }, [filteredInvoices]);

  const handleExportEvidence = useCallback((invoice) => {
    const evidence = generateEvidencePackage(invoice, 'EXPORT', { traceId });
    const blob = new Blob([JSON.stringify(evidence, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `WILSY_EVIDENCE_${invoice.invoiceNumber}_${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);

    // Increment Prometheus counter
    incrementMetric('export', invoice.id);

    // Broadcast telemetry (existing)
    incrementCounter('ledgerExportCount', {
      mode: isClientMode ? 'CLIENT' : 'PLATFORM',
      tenantId: String(tenantId || 'GLOBAL'),
      invoiceId: invoice.id,
    });
    showBillingToast('Evidence package exported', 'ok');
  }, [isClientMode, tenantId, incrementCounter, incrementMetric, traceId]);

  const hasAnomalies = anomalies.length > 0;

  return (
    <div className={hudStyles.ledgerCockpit || undefined} style={{ gridColumn: '1 / -1', marginTop: 0, paddingTop: 0 }}>
      {/* ─── Header ─────────────────────────────────────────────────────────── */}
      <div className={hudStyles.ledgerToolbar}>
        <div className={hudStyles.ledgerToolbarTitle}>
          <TrendingUp size={16} style={{ color: accent }} />
          <div>
            <span className={hudStyles.ledgerEyebrow}>Revenue analytics</span>
            <h2>
              {isClientMode ? `Client invoices · ${businessName}` : `Platform invoices · ${businessName}`}
            </h2>
          </div>
        </div>
        <div className={hudStyles.ledgerFilters} role="search">
          <div className={hudStyles.searchInputWrap}>
            <Search size={14} className={hudStyles.ledgerSearchIcon} aria-hidden />
            <input
              name="search"
              value={filters.search}
              onChange={handleFilterChange}
              placeholder="Invoice, client, creator, seal…"
              className={hudStyles.searchInput}
              aria-label="Search analytics"
            />
          </div>
          <select name="status" value={filters.status} onChange={handleFilterChange} className={hudStyles.searchSelect} aria-label="Status">
            <option value="all">All statuses</option>
            <option value="issued">Issued</option>
            <option value="paid">Paid</option>
            <option value="pending">Partially paid</option>
            <option value="overdue">Overdue</option>
            <option value="draft">Draft</option>
            <option value="cancelled">Cancelled</option>
          </select>
          <select name="period" value={filters.period} onChange={handleFilterChange} className={hudStyles.searchSelect} aria-label="Period">
            <option value="today">Today</option>
            <option value="7d">7 days</option>
            <option value="30d">30 days</option>
            <option value="90d">90 days</option>
            <option value="ytd">YTD</option>
            <option value="all">All time</option>
          </select>
          <button type="button" className={hudStyles.ledgerSearchBtn} onClick={fetchInvoices} disabled={loading}>
            {loading ? '…' : 'Refresh'}
          </button>
          <button type="button" className={hudStyles.ledgerSearchBtn} onClick={handleExportCsv} disabled={loading || !(filteredInvoices || []).length} title="Export filtered rows as CSV">
            CSV
          </button>
          {typeof onOpenLedger === 'function' && (
            <button
              type="button"
              className={hudStyles.ledgerSearchBtn}
              onClick={onOpenLedger}
              style={{ borderColor: 'rgba(255,255,255,0.15)', color: '#cbd5e1' }}
            >
              Open ledger
            </button>
          )}
        </div>
      </div>

      {/* ─── Meta Strip ───────────────────────────────────────────────────── */}
      <div className={hudStyles.ledgerMeta}>
        <span className={hudStyles.metaChip} data-source={error ? 'SOURCE_SILENT' : 'LIVE_DB'}>
          {error ? 'ERROR' : 'LIVE'}
        </span>
        <span className={hudStyles.metaChip}>{analytics.count} invoices</span>
        <span className={hudStyles.metaChip}>{formatCurrency(analytics.totalVolume)}</span>
        <span className={hudStyles.metaChip} style={{ borderColor: `${accent}55`, color: accent }}>
          {isClientMode ? 'CLIENT ONLY' : 'PLATFORM ONLY'}
        </span>
        {isolationMeta.dropped > 0 && (
          <span className={hudStyles.metaChipMuted}>
            Filtered out {isolationMeta.dropped} cross-pipeline rows
          </span>
        )}
        <span className={hudStyles.metaChipMuted}>Isolation enforced</span>
        {hasAnomalies && (
          <span className={hudStyles.metaChip} style={{ borderColor: '#ef444455', color: '#f87171' }}>
            <AlertTriangle size={12} style={{ marginRight: 4 }} />
            {anomalies.length} anomalies detected
          </span>
        )}
      </div>

      {/* ─── Sovereignty Index ────────────────────────────────────────────── */}
      {!loading && invoices.length > 0 && <SovereigntyIndex invoices={invoices} />}

      {/* ─── Error State ──────────────────────────────────────────────────── */}
      {error && (
        <div role="alert" style={alertStyle}>
          <strong style={{ display: 'block', marginBottom: 4 }}>Analytics unavailable</strong>
          {error}
          <button type="button" onClick={fetchInvoices} style={retryStyle}>Retry</button>
        </div>
      )}

      {/* ─── Anomaly Banner ───────────────────────────────────────────────── */}
      {hasAnomalies && (
        <div style={{
          marginBottom: 12,
          padding: '10px 14px',
          borderRadius: 8,
          border: '1px solid rgba(248,113,113,0.3)',
          background: 'rgba(127,29,29,0.15)',
          color: '#fca5a5',
          fontSize: '0.78rem',
          display: 'flex',
          alignItems: 'center',
          gap: 8,
          flexWrap: 'wrap',
        }}>
          <AlertTriangle size={14} />
          <strong>Anomalies detected:</strong>
          {anomalies.map((a, i) => (
            <span key={i} style={{ background: 'rgba(0,0,0,0.25)', padding: '2px 8px', borderRadius: 4 }}>
              {a.description}
              {a.invoiceNumber && ` (${a.invoiceNumber})`}
            </span>
          ))}
        </div>
      )}

      {/* ─── KPI Cards ────────────────────────────────────────────────────── */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: 10, marginBottom: 14 }}>
        {[
          { label: 'Volume', value: formatCurrency(analytics.totalVolume) },
          { label: 'Collected', value: formatCurrency(analytics.paidVolume) },
          { label: 'Outstanding', value: formatCurrency(analytics.outstanding) },
          {
            label: 'Collection rate',
            value: analytics.totalVolume > 0
              ? `${Math.round((analytics.paidVolume / analytics.totalVolume) * 100)}%`
              : '—',
          },
        ].map((kpi) => (
          <div key={kpi.label} style={{ ...kpiCard, borderColor: `${accent}33` }}>
            <div style={kpiLabel}>{kpi.label}</div>
            <div style={kpiValue}>{kpi.value}</div>
          </div>
        ))}
      </div>

      {/* ─── Charts ────────────────────────────────────────────────────────── */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 12, marginBottom: 16 }}>
        <ChartCard title="Monthly volume" icon={<TrendingUp size={14} style={{ color: accent }} />} loading={loading}>
          {analytics.monthlyTotals.length > 0 ? (
            <ResponsiveContainer width="100%" height={210}>
              <AreaChart data={analytics.monthlyTotals} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
                <defs>
                  <linearGradient id="volGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor={accent} stopOpacity={0.45} />
                    <stop offset="100%" stopColor={accent} stopOpacity={0.02} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" vertical={false} />
                <XAxis dataKey="month" tick={{ fontSize: 11, fill: '#94a3b8' }} axisLine={false} tickLine={false} />
                <YAxis
                  tick={{ fontSize: 11, fill: '#94a3b8' }}
                  axisLine={false}
                  tickLine={false}
                  tickFormatter={(v) => (v >= 1000 ? `R${Math.round(v / 1000)}k` : `R${v}`)}
                  width={48}
                />
                <Tooltip
                  contentStyle={chartTooltipStyle}
                  formatter={(v) => [formatCurrency(v), 'Volume']}
                  labelStyle={{ color: '#94a3b8', marginBottom: 4 }}
                />
                <Area type="monotone" dataKey="total" stroke={accent} strokeWidth={2.5} fill="url(#volGrad)" />
              </AreaChart>
            </ResponsiveContainer>
          ) : (
            <EmptyChart />
          )}
        </ChartCard>

        <ChartCard title="Status mix" icon={<PieIcon size={14} style={{ color: accent }} />} loading={loading}>
          {analytics.statusCounts.length > 0 ? (
            <ResponsiveContainer width="100%" height={210}>
              <PieChart>
                <Pie
                  data={analytics.statusCounts}
                  dataKey="value"
                  nameKey="label"
                  cx="50%"
                  cy="46%"
                  innerRadius={52}
                  outerRadius={78}
                  paddingAngle={3}
                  stroke="rgba(0,0,0,0.4)"
                  strokeWidth={1}
                >
                  {analytics.statusCounts.map((entry, i) => (
                    <Cell key={i} fill={STATUS_COLORS[entry.name] || STATUS_COLORS.unknown} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={chartTooltipStyle}
                  formatter={(v, n) => [`${v} invoices`, String(n)]}
                />
                <Legend
                  verticalAlign="bottom"
                  height={28}
                  iconType="circle"
                  formatter={(value) => <span style={{ color: '#cbd5e1', fontSize: 11 }}>{value}</span>}
                />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <EmptyChart />
          )}
        </ChartCard>

        <ChartCard title="AR aging" icon={<Shield size={14} style={{ color: accent }} />} loading={loading}>
          {analytics.outstanding > 0 || analytics.aging.some((b) => b.total > 0) ? (
            <ResponsiveContainer width="100%" height={210}>
              <BarChart data={analytics.aging} margin={{ top: 8, right: 8, left: 0, bottom: 0 }} barCategoryGap="28%">
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" vertical={false} />
                <XAxis dataKey="bucket" tick={{ fontSize: 11, fill: '#94a3b8' }} axisLine={false} tickLine={false} />
                <YAxis
                  tick={{ fontSize: 11, fill: '#94a3b8' }}
                  axisLine={false}
                  tickLine={false}
                  tickFormatter={(v) => (v >= 1000 ? `R${Math.round(v / 1000)}k` : `R${v}`)}
                  width={48}
                />
                <Tooltip contentStyle={chartTooltipStyle} formatter={(v) => [formatCurrency(v), 'Open AR']} />
                <Bar dataKey="total" radius={[6, 6, 0, 0]} maxBarSize={42}>
                  {analytics.aging.map((entry, i) => (
                    <Cell
                      key={i}
                      fill={
                        entry.bucket === 'Current' ? '#22c55e'
                          : entry.bucket === '1–30d' ? '#eab308'
                            : entry.bucket === '31–60d' ? '#f59e0b'
                              : entry.bucket === '61–90d' ? '#f97316'
                                : '#ef4444'
                      }
                    />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <EmptyChart label="No open receivables" />
          )}
        </ChartCard>
      </div>

      {/* ─── Table ─────────────────────────────────────────────────────────── */}
      <div style={tableShell}>
        <div style={tableHead}>
          <List size={14} style={{ color: accent }} />
          <span style={{ fontSize: '0.72rem', fontWeight: 700, color: '#e2e8f0' }}>
            {isClientMode ? 'Client pipeline rows' : 'Platform pipeline rows'}
          </span>
          <span style={{ marginLeft: 'auto', fontSize: '0.65rem', color: '#64748b' }}>
            {filteredInvoices.length} total · page {safePage + 1}/{pageCount}
          </span>
        </div>

        {loading ? (
          <div style={{ padding: 40, textAlign: 'center', color: '#64748b' }}>Loading…</div>
        ) : paged.length === 0 ? (
          <div style={{ padding: 32, textAlign: 'center', color: '#64748b', fontSize: '0.85rem' }}>
            {isClientMode
              ? 'No client invoices in this pipeline. Issue a client invoice to populate analytics.'
              : 'No platform invoices in this pipeline for the current filters.'}
          </div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.8rem' }}>
              <thead>
                <tr style={{ color: '#d4af37', textTransform: 'uppercase', fontSize: '0.58rem', letterSpacing: '0.1em' }}>
                  <th style={thStyle}>Invoice</th>
                  <th style={thStyle}>Bill to</th>
                  <th style={thStyle}>Created by</th>
                  <th style={thStyle}>Issued</th>
                  <th style={{ ...thStyle, textAlign: 'right' }}>Amount</th>
                  <th style={thStyle}>Status</th>
                  <th style={{ ...thStyle, textAlign: 'right' }}> </th>
                </tr>
              </thead>
              <tbody>
                {paged.map((invoice) => {
                  const isAnomaly = anomalies.some(a => a.invoiceId === invoice.id);
                  return (
                    <tr key={invoice.id} style={{ borderTop: '1px solid rgba(255,255,255,0.04)', background: isAnomaly ? 'rgba(127,29,29,0.08)' : 'transparent' }}>
                      <td style={tdStyle}>
                        <span title={invoice.invoiceNumber} style={monoEllipsis}>{invoice.invoiceNumber}</span>
                        {isAnomaly && <AlertTriangle size={10} color="#f87171" style={{ marginLeft: 4 }} />}
                      </td>
                      <td style={{ ...tdStyle, color: '#cbd5e1' }}>{invoice.clientName || '—'}</td>
                      <td style={{ ...tdStyle, color: '#94a3b8' }}>
                        <span style={{ color: '#e2e8f0', fontWeight: 600 }}>{invoice.createdBy}</span>
                      </td>
                      <td style={{ ...tdStyle, color: '#94a3b8' }}>{formatInvoiceDate(invoice.issueDate)}</td>
                      <td style={{ ...tdStyle, textAlign: 'right', fontFamily: 'ui-monospace, monospace', color: '#f0d78c', fontWeight: 700 }}>
                        {formatCurrency(invoice.totalAmount, invoice.currency)}
                      </td>
                      <td style={tdStyle}>
                        <span style={{
                          display: 'inline-block', padding: '2px 8px', borderRadius: 999,
                          fontSize: '0.62rem', fontWeight: 800, textTransform: 'uppercase',
                          color: STATUS_COLORS[invoice.status] || '#94a3b8',
                          background: `${STATUS_COLORS[invoice.status] || '#94a3b8'}22`,
                          border: `1px solid ${(STATUS_COLORS[invoice.status] || '#94a3b8')}44`,
                        }}>
                          {STATUS_LABEL[invoice.status] || invoice.status}
                        </span>
                      </td>
                      <td style={{ ...tdStyle, textAlign: 'right' }}>
                        <button
                          type="button"
                          onClick={() => handleViewInvoice(invoice)}
                          style={{
                            background: 'transparent', border: 'none', color: accent,
                            fontWeight: 700, fontSize: '0.72rem', cursor: 'pointer',
                            textTransform: 'uppercase', letterSpacing: '0.04em',
                            marginRight: 8,
                          }}
                        >
                          View
                        </button>
                        <button
                          type="button"
                          onClick={() => handleExportEvidence(invoice)}
                          style={{
                            background: 'transparent', border: 'none', color: '#94a3b8',
                            fontWeight: 700, fontSize: '0.72rem', cursor: 'pointer',
                            textTransform: 'uppercase', letterSpacing: '0.04em',
                          }}
                          title="Export evidence package"
                        >
                          <Download size={12} />
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}

        <div className={hudStyles.ledgerPagination} style={{ padding: '10px 14px' }}>
          <button type="button" className={hudStyles.secondaryButton} disabled={safePage <= 0 || loading} onClick={() => setPage((p) => Math.max(0, p - 1))}>
            Previous
          </button>
          <span>Page {safePage + 1} of {pageCount} · {filteredInvoices.length} total</span>
          <button type="button" className={hudStyles.secondaryButton} disabled={safePage + 1 >= pageCount || loading} onClick={() => setPage((p) => p + 1)}>
            Next
          </button>
        </div>
      </div>

      {/* ─── Forensic Detail Modal ───────────────────────────────────────── */}
      {isDetailOpen && selectedInvoice && createPortal(
        <ForensicDetailModal
          invoice={selectedInvoice}
          accent={accent}
          isClientMode={isClientMode}
          onClose={() => setIsDetailOpen(false)}
          onExport={handleExportEvidence}
        />,
        document.body
      )}
    </div>
  );
};

// ─── FORENSIC DETAIL MODAL ──────────────────────────────────────────────────

function ForensicDetailModal({ invoice, accent, isClientMode, onClose, onExport }) {
  const seal = invoice.sealHash ? String(invoice.sealHash) : '';
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    const prev = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
    const onKey = (e) => { if (e.key === 'Escape') onClose(); };
    window.addEventListener('keydown', onKey);
    return () => {
      document.body.style.overflow = prev;
      window.removeEventListener('keydown', onKey);
    };
  }, [onClose]);

  const handleCopySeal = useCallback(async () => {
    if (!seal) return;
    try {
      await navigator.clipboard.writeText(seal.toUpperCase());
      setCopied(true);
      setTimeout(() => setCopied(false), 3000);
    } catch {
      // fallback
    }
  }, [seal]);

  const handleExport = useCallback(() => {
    if (typeof onExport === 'function') {
      onExport(invoice);
    }
  }, [onExport, invoice]);

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-label="Invoice forensic detail"
      onClick={(e) => e.target === e.currentTarget && onClose()}
      style={{
        position: 'fixed',
        inset: 0,
        zIndex: 2147483000,
        background: 'rgba(0,0,0,0.82)',
        backdropFilter: 'blur(6px)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: 'max(24px, env(safe-area-inset-top)) 16px 24px',
      }}
    >
      <div
        style={{
          width: '100%',
          maxWidth: 580,
          maxHeight: 'min(88vh, 900px)',
          overflowY: 'auto',
          borderRadius: 16,
          border: `1px solid ${accent}66`,
          background: 'linear-gradient(165deg, #0b0b0f 0%, #12121c 55%, #0f172a 100%)',
          padding: '20px 22px 18px',
          color: '#e2e8f0',
          boxShadow: '0 28px 80px rgba(0,0,0,0.65)',
          position: 'relative',
        }}
      >
        <div style={{
          position: 'sticky', top: 0, zIndex: 2,
          display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start',
          gap: 12, marginBottom: 16, paddingBottom: 12,
          background: 'linear-gradient(180deg, #0b0b0f 70%, transparent)',
          borderBottom: '1px solid rgba(255,255,255,0.06)',
        }}>
          <div style={{ minWidth: 0 }}>
            <div style={{ fontSize: '0.58rem', color: accent, letterSpacing: '0.14em', textTransform: 'uppercase', fontWeight: 800 }}>
              {isClientMode ? 'Client invoice' : 'Platform invoice'} · forensic detail
            </div>
            <h3 style={{
              margin: '6px 0 0', color: '#f8fafc', fontSize: '0.95rem',
              fontFamily: 'ui-monospace, SFMono-Regular, Menlo, monospace',
              wordBreak: 'break-all', lineHeight: 1.35,
            }}>
              {invoice.invoiceNumber}
            </h3>
          </div>
          <button type="button" onClick={onClose} style={closeBtnStyle} aria-label="Close">
            <X size={16} />
          </button>
        </div>

        <Section title="Commercial" accent={accent}>
          <Grid2>
            <Field label="Bill to" value={invoice.clientName || '—'} />
            <Field label="Status" value={String(invoice.rawStatus || invoice.status).replace(/_/g, ' ')} />
            <Field label="Issued" value={formatInvoiceDate(invoice.issueDate)} />
            <Field label="Due" value={formatInvoiceDate(invoice.dueDate)} />
            <Field label="Amount" value={formatCurrency(invoice.totalAmount, invoice.currency)} emphasize />
            <Field label="Outstanding" value={formatCurrency(invoice.outstandingAmount, invoice.currency)} />
          </Grid2>
        </Section>

        <Section title="Created by" accent={accent} icon={<User size={12} />}>
          <Grid2>
            <Field label="Operator" value={invoice.createdBy && invoice.createdBy !== '—' ? invoice.createdBy : (isClientMode ? 'Tenant operator' : 'Platform system')} />
            <Field label="Role" value={invoice.createdByRole && invoice.createdByRole !== '—' ? invoice.createdByRole : (invoice.createdBySystem ? 'SYSTEM' : '—')} />
            <Field label="User ID" value={invoice.createdById && invoice.createdById !== '—' ? invoice.createdById : '—'} mono />
            <Field label="Email" value={invoice.createdByEmail && invoice.createdByEmail !== '—' ? invoice.createdByEmail : '—'} />
            <Field label="Created at" value={invoice.createdAt ? formatDateTime(invoice.createdAt) : '—'} />
            <Field label="Sealed at" value={invoice.sealedAt ? formatDateTime(invoice.sealedAt) : (invoice.sealHash ? formatDateTime(invoice.createdAt) : '—')} />
          </Grid2>
          {(!invoice.createdById || invoice.createdById === '—') && (
            <div style={{ marginTop: 8, fontSize: '0.62rem', color: '#94a3b8', lineHeight: 1.4 }}>
              Lineage not stamped on this document. New invoices created after backend creator fields deploy will show operator, role, user id, and email.
            </div>
          )}
        </Section>

        <Section title="Identity & pipeline" accent={accent} icon={<Building2 size={12} />}>
          <Grid2>
            <Field label="Issuing entity" value={invoice.issuingEntity || (isClientMode ? '—' : 'Wilsy (Pty) Ltd')} />
            <Field label="Pipeline" value={isClientMode ? 'Client (tenant_client)' : 'Platform'} />
            <Field label="Identity source" value={String(invoice.identitySource || '—').replace(/_/g, ' ')} />
            <Field label="Tenant" value={invoice.tenantId || '—'} mono />
          </Grid2>
        </Section>

        <Section title="Forensic seal" accent={accent} icon={<Hash size={12} />}>
          <Field label="Trace ID" value={invoice.traceId || '—'} mono />
          <div style={{ marginTop: 10 }}>
            <div style={labelStyle}>Seal / proof hash</div>
            <div style={{
              marginTop: 4, padding: '10px 12px', borderRadius: 8,
              background: 'rgba(0,0,0,0.4)', border: `1px solid ${accent}40`,
              fontFamily: 'ui-monospace, monospace', fontSize: '0.65rem',
              wordBreak: 'break-all', color: '#cbd5e1', lineHeight: 1.5,
              display: 'flex', justifyContent: 'space-between', alignItems: 'center',
            }}>
              <span>{seal ? seal.toUpperCase() : 'Seal pending'}</span>
              {seal && (
                <button
                  type="button"
                  onClick={handleCopySeal}
                  style={{ background: 'none', border: 'none', color: accent, cursor: 'pointer', padding: '4px' }}
                  title="Copy seal"
                >
                  {copied ? <CheckCircle size={14} color="#4ade80" /> : <Copy size={14} />}
                </button>
              )}
            </div>
          </div>
        </Section>

        <div style={{ marginTop: 16, display: 'flex', justifyContent: 'flex-end', gap: 8 }}>
          <button type="button" className={hudStyles.secondaryButton} onClick={handleExport}>
            <Download size={14} /> Export evidence
          </button>
          <button type="button" className={hudStyles.secondaryButton} onClick={onClose}>Close</button>
        </div>
      </div>
    </div>
  );
}

// ─── SUB‑COMPONENTS ─────────────────────────────────────────────────────────

function Section({ title, children, accent, icon }) {
  return (
    <div style={{ marginBottom: 14, paddingBottom: 12, borderBottom: '1px solid rgba(255,255,255,0.06)' }}>
      <div style={{
        display: 'flex', alignItems: 'center', gap: 6, marginBottom: 10,
        color: accent, fontSize: '0.62rem', fontWeight: 800, letterSpacing: '0.12em', textTransform: 'uppercase',
      }}>
        {icon}{title}
      </div>
      {children}
    </div>
  );
}

function Grid2({ children }) {
  return (
    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, fontSize: '0.84rem' }}>
      {children}
    </div>
  );
}

function Field({ label, value, mono, emphasize }) {
  return (
    <div style={emphasize ? { gridColumn: '1 / -1' } : undefined}>
      <div style={labelStyle}>{label}</div>
      <div style={{
        color: emphasize ? '#f0d78c' : '#f1f5f9',
        fontWeight: emphasize ? 700 : 500,
        fontSize: emphasize ? '1.3rem' : undefined,
        fontFamily: mono || emphasize ? 'ui-monospace, SFMono-Regular, Menlo, monospace' : undefined,
        wordBreak: 'break-word',
      }}>
        {value}
      </div>
    </div>
  );
}

function ChartCard({ title, icon, loading, children }) {
  return (
    <div style={{
      padding: '14px 14px 10px', borderRadius: 12,
      border: '1px solid rgba(212,175,55,0.16)',
      background: 'linear-gradient(180deg, rgba(15,23,42,0.55), rgba(0,0,0,0.35))',
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
        {icon}
        <span style={{ fontSize: '0.75rem', fontWeight: 700, color: '#e2e8f0', letterSpacing: '0.02em' }}>{title}</span>
      </div>
      {loading ? (
        <div style={{ height: 210, display: 'grid', placeItems: 'center', color: '#64748b' }}>
          <RefreshCw size={20} className={hudStyles.spin} />
        </div>
      ) : children}
    </div>
  );
}

function EmptyChart({ label = 'No data in this period' }) {
  return (
    <p style={{ color: '#64748b', fontSize: '0.8rem', padding: '56px 0', textAlign: 'center', margin: 0 }}>
      {label}
    </p>
  );
}

// ─── TOAST HELPER ────────────────────────────────────────────────────────────
function showBillingToast(message = '', tone = 'ok') {
  if (typeof document === 'undefined') return;
  const existing = document.getElementById('wilsy-billing-toast');
  if (existing) existing.remove();
  const toast = document.createElement('div');
  toast.id = 'wilsy-billing-toast';
  const bg = tone === 'danger'
    ? 'linear-gradient(135deg,#7f1d1d,#991b1b)'
    : tone === 'warn'
      ? 'linear-gradient(135deg,#78350f,#b45309)'
      : 'linear-gradient(135deg,#14532d,#166534)';
  toast.style.cssText = `
    position: fixed; z-index: 99999; right: 24px; bottom: 24px;
    max-width: 420px; padding: 14px 18px; border-radius: 12px;
    background: ${bg}; color: #f8fafc; font: 600 13px/1.4 Inter, system-ui, sans-serif;
    box-shadow: 0 12px 40px rgba(0,0,0,0.35); border: 1px solid rgba(255,255,255,0.12);
    opacity: 1; transition: opacity 0.45s ease;
  `;
  toast.textContent = String(message || '');
  document.body.appendChild(toast);
  window.setTimeout(() => {
    toast.style.opacity = '0';
    window.setTimeout(() => toast.remove(), 500);
  }, 2800);
}

// ─── STYLES ──────────────────────────────────────────────────────────────────

const labelStyle = {
  fontSize: '0.58rem', letterSpacing: '0.1em', textTransform: 'uppercase',
  color: '#64748b', marginBottom: 3, fontWeight: 700,
};
const thStyle = { textAlign: 'left', padding: '10px 14px', fontWeight: 800 };
const tdStyle = { padding: '10px 14px', verticalAlign: 'middle' };
const monoEllipsis = {
  fontFamily: 'ui-monospace, monospace', fontWeight: 600, color: '#f1f5f9',
  display: 'block', maxWidth: 200, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap',
};
const kpiCard = { padding: '12px 14px', borderRadius: 10, border: '1px solid', background: 'rgba(15,23,42,0.65)' };
const kpiLabel = { fontSize: '0.58rem', letterSpacing: '0.12em', textTransform: 'uppercase', color: '#94a3b8', marginBottom: 4 };
const kpiValue = { fontSize: '1.05rem', fontWeight: 700, color: '#f8fafc', fontFamily: 'ui-monospace, monospace' };
const tableShell = { borderRadius: 12, border: '1px solid rgba(212,175,55,0.15)', overflow: 'hidden', background: 'rgba(0,0,0,0.2)' };
const tableHead = { display: 'flex', alignItems: 'center', gap: 8, padding: '10px 14px', borderBottom: '1px solid rgba(212,175,55,0.12)' };
const alertStyle = { marginBottom: 12, padding: '12px 14px', borderRadius: 10, border: '1px solid rgba(248,113,113,0.35)', background: 'rgba(127,29,29,0.2)', color: '#fecaca', fontSize: '0.82rem' };
const retryStyle = { marginLeft: 12, background: 'transparent', border: 'none', color: '#fca5a5', textDecoration: 'underline', cursor: 'pointer' };
const closeBtnStyle = {
  background: 'rgba(255,255,255,0.06)', border: '1px solid rgba(255,255,255,0.12)',
  borderRadius: 8, color: '#94a3b8', width: 34, height: 34, cursor: 'pointer',
  display: 'inline-flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0,
};

/**
 * Export filtered ledger rows as CSV (wave 14).
 * @param {Array} rows – normalized invoices
 * @param {string} [filename]
 */
function exportLedgerCsv(rows = [], filename = 'wilsy-ledger-export.csv') {
  const cols = ['invoiceNumber', 'clientName', 'status', 'totalAmount', 'currency', 'issueDate', 'dueDate', 'tenantId', 'orderNumber', 'purchaseOrder', 'sealHash'];
  const esc = (v) => {
    const s = v == null ? '' : String(v);
    if (/[",\n]/.test(s)) return `"${s.replace(/"/g, '""')}"`;
    return s;
  };
  const header = cols.join(',');
  const lines = (Array.isArray(rows) ? rows : []).map((r) => cols.map((c) => esc(r[c])).join(','));
  const blob = new Blob([[header, ...lines].join('\n')], { type: 'text/csv;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

export default LedgerExplorer;

/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * 🏛️ INSTITUTIONAL CERTIFICATION SEAL — LedgerExplorer V4.5.0-CSV-EXPORT
 * ═══════════════════════════════════════════════════════════════════════════════
 * Status:          PRODUCTION READY — structure preserved · dual-pipeline · POPIA
 * Metrics:         Calls /api/metrics/ledger to increment Prometheus counters.
 * Preserved:       SovereigntyIndex · detectAnomalies · pickCreatedBy · Forensic modal
 *                  telemetry · charts · table · pagination · evidence export
 * Compliance:      POPIA §19 · GDPR §32 · SOC2 §CC7.2 · ISO 27001
 * Deploy:
 *   cp artifacts/client/src/components/billing/LedgerExplorer.jsx \
 *      /Users/wilsonkhanyezi/legal-doc-system/client/src/components/billing/LedgerExplorer.jsx
 * ═══════════════════════════════════════════════════════════════════════════════
 */
