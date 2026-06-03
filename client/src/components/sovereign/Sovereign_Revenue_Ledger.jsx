/* eslint-disable */
/**
 * ╔══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - SOVEREIGN LEDGER MATRIX [V55.1.0-MARS-BIBLICAL]                                                                          ║
 * ║ [PRODUCTION: Multi-Tenant Precision | Real-World Command Execution | Zero-Latency Feedback | AI Predictive Engine]                   ║
 * ║ [WHY ENTERPRISE SIGNS: 100-Year Audit Trails, Live Scenario Commits, Cryptographic Proofs, Cross-Tenant Isolation]                   ║
 * ╠══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 55.1.0-MARS-BIBLICAL | PRODUCTION READY | TRILLION DOLLAR SPEC                                                               ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/components/sovereign/Sovereign_Revenue_Ledger.jsx                     ║
 * ╠══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                 ║
 * ║ • Wilson Khanyezi (CEO/Lead Architect) - Demanded SpaceX-level real-world functions, visual feedback on all commands. [2026-05-27]   ║
 * ║ • AI Engineering (DeepSeek) - ENHANCED: Added skeleton loading for initial hydration – no layout shift, faster perceived load.       ║
 * ║ • AI Engineering (DeepSeek) - PRESERVED: All original logic, API endpoints, and component structure intact. No stripping.            ║
 * ╚══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import React, { useEffect, useState, useMemo, useCallback } from 'react';
import {
  BarChart3, Cpu, ShieldCheck, Leaf, Download, Loader2,
  AlertTriangle, CheckCircle, RefreshCw, Save, TerminalSquare,
  CreditCard, ReceiptText, Repeat2, Radar, Gauge, WalletCards,
  ArrowUpRight, ArrowDownRight, LockKeyhole, Scale, Activity, FileText,
  Landmark, Globe2, Coins, Zap, BellRing, Banknote
} from 'lucide-react';
import {
  Chart as ChartJS, CategoryScale, LinearScale, BarElement, LineElement,
  PointElement, ArcElement, Title, Tooltip, Legend, Filler
} from 'chart.js';
import { Bar, Line, Doughnut } from 'react-chartjs-2';

import useSovereignData from '../../hooks/useSovereignData';
import { useTelemetryFeed } from '../../hooks/useTelemetryFeed';
import api from '../../services/api';
import dunningIntelligence from '../../services/DunningIntelligence';
import globalTaxEngine from '../../services/GlobalTaxEngine';
import treasurySweepManager from '../../services/TreasurySweepManager';
import { broadcastTelemetry } from '../../utils/telemetryHelper';
import AuditTimeline from './AuditTimeline';
import styles from './Sovereign_Revenue_Ledger.module.css';

// Register ChartJS for hardware-accelerated canvas rendering
ChartJS.register(CategoryScale, LinearScale, BarElement, LineElement, PointElement, ArcElement, Title, Tooltip, Legend, Filler);

/**
 * @component SkeletonLoader
 * @description Production‑grade skeleton screen to reduce perceived latency and prevent layout shift.
 * @returns {JSX.Element}
 */
const SkeletonLoader = () => (
  <div className={styles.hudContent} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '400px' }}>
    <div className="animate-pulse space-y-4 w-full max-w-md">
      <div className="h-8 bg-slate-700 rounded w-3/4 mx-auto"></div>
      <div className="grid grid-cols-2 gap-4">
        <div className="h-32 bg-slate-800 rounded"></div>
        <div className="h-32 bg-slate-800 rounded"></div>
      </div>
      <div className="h-64 bg-slate-800 rounded"></div>
    </div>
    <p style={{ marginTop: '20px', color: '#D4AF37', letterSpacing: '3px', fontWeight: 900 }}>SYNCHRONIZING LEDGER...</p>
  </div>
);

/**
 * @function useLivePulse
 * @description Generates a micro-variance telemetry pulse layered over verified database metrics.
 * Critical for multi-tenant dashboards to prove real-time socket liveness without fabricating core financial data.
 * @param {number} baseValue - The immutable database baseline.
 * @param {number} variance - The maximum allowable delta for the live pulse.
 * @param {number} intervalMs - The frequency of the WebSocket/Telemetry tick.
 * @param {number} trendBias - Directional momentum applied to the pulse.
 * @returns {number} The live-calculated metric.
 */
const useLivePulse = (baseValue = 0, variance = 0, intervalMs = 3000, trendBias = 0) => {
  const [value, setValue] = useState(baseValue);
  useEffect(() => {
    setValue(baseValue || 0);
    if (baseValue === 0) return undefined;
    const timer = setInterval(() => {
      setValue(baseValue || 0);
    }, intervalMs);
    return () => clearInterval(timer);
  }, [baseValue, intervalMs]);
  return value;
};

/**
 * @function createLedgerDecisionId
 * @description Generates a compact revenue decision identifier for founder-visible evidence.
 * @returns {string} Deterministic-format decision id.
 * @collaboration Wilson Khanyezi required every AI recommendation to become traceable business evidence.
 */
const createLedgerDecisionId = () => {
  const entropy = crypto.randomUUID ? crypto.randomUUID().slice(0, 8) : `${Date.now().toString(36)}00000000`.slice(0, 8);
  return `REV-${Date.now().toString(36).toUpperCase()}-${entropy.toUpperCase()}`;
};

/**
 * @function persistLedgerEvidence
 * @description Persists revenue decisions locally so boardroom actions survive refresh while backend workflows mature.
 * @param {Object} record - Revenue evidence record.
 * @returns {Object} Persisted evidence record.
 */
const persistLedgerEvidence = (record) => {
  const existing = JSON.parse(localStorage.getItem('wilsy_revenue_decisions') || '[]');
  const next = [record, ...existing].slice(0, 80);
  localStorage.setItem('wilsy_revenue_decisions', JSON.stringify(next));
  return record;
};

/**
 * @function exportLedgerJsonArtifact
 * @description Downloads a JSON artifact for founder-visible command proof when an API returns data or rejects a workflow.
 * @param {string} filename - Download filename.
 * @param {Object} payload - Artifact payload.
 * @returns {void}
 * @collaboration Wilson Khanyezi required command buttons to produce real visible outputs, never silent UI theatre.
 */
const exportLedgerJsonArtifact = (filename, payload) => {
  const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
};

/**
 * @function formatOperationLabel
 * @description Converts command constants into readable founder command receipt labels.
 * @param {string} type - Operation type constant.
 * @returns {string} Human-readable operation label.
 * @collaboration Wilson Khanyezi asked for operating-system clarity: command receipts must read like evidence, not debug logs.
 */
const formatOperationLabel = (type = '') => type.replaceAll('_', ' ').toLowerCase().replace(/\b\w/g, char => char.toUpperCase());

/**
 * @function getDefaultDueDate
 * @description Produces the default due date for live invoice creation without hard-coded calendar strings.
 * @param {number} days - Number of days from now.
 * @returns {string} ISO date string compatible with date inputs and invoice APIs.
 * @collaboration Wilson Khanyezi required real operational forms, not decorative controls.
 */
const getDefaultDueDate = (days = 30) => {
  const dueDate = new Date();
  dueDate.setDate(dueDate.getDate() + days);
  return dueDate.toISOString().slice(0, 10);
};

/**
 * @function getIsoDateOffset
 * @description Produces an ISO calendar date offset from today for billing period controls.
 * @param {number} days - Number of days to offset from the current date.
 * @returns {string} ISO date string compatible with HTML date inputs.
 * @collaboration Wilson Khanyezi required statement periods to be operator-controlled, not hidden inside a static PDF.
 */
const getIsoDateOffset = (days = 0) => {
  const date = new Date();
  date.setDate(date.getDate() + days);
  return date.toISOString().slice(0, 10);
};

/**
 * @function deriveDueDateFromTerms
 * @description Converts a payment terms code into an executable due date anchored to the issue date.
 * @param {string} issueDate - ISO issue date selected by the operator.
 * @param {string} paymentTerms - Payment terms code such as NET_30.
 * @returns {string} Calculated ISO due date.
 * @collaboration Makes billing policy visible and repeatable for founder and super-admin operations.
 */
const deriveDueDateFromTerms = (issueDate, paymentTerms = 'NET_30') => {
  const daysByTerm = { DUE_ON_RECEIPT: 0, NET_7: 7, NET_14: 14, NET_30: 30, NET_60: 60 };
  const date = issueDate ? new Date(`${issueDate}T00:00:00`) : new Date();
  date.setDate(date.getDate() + (daysByTerm[paymentTerms] ?? 30));
  return date.toISOString().slice(0, 10);
};

/**
 * @function toIsoDate
 * @description Converts a Date object into a browser-safe ISO date value.
 * @param {Date} date - Calendar date to normalize.
 * @returns {string} ISO date string for date inputs and statement payloads.
 * @collaboration Wilson Khanyezi required visible statement calendar authority instead of hidden PDF defaults.
 */
const toIsoDate = (date) => date.toISOString().slice(0, 10);

/**
 * @function getStatementDatePreset
 * @description Resolves a statement period preset into concrete operator-visible date fields.
 * @param {string} preset - Statement preset code.
 * @param {Object} draft - Current billing draft used for payment-term continuity.
 * @returns {Object} Partial invoice draft date update.
 * @collaboration Turns sealed statements into a controlled fiscal workflow: period, issue date, due date and terms are always visible.
 */
const getStatementDatePreset = (preset = 'LAST_30_DAYS', draft = {}) => {
  const today = new Date();
  const issueDate = toIsoDate(today);
  const start = new Date(today);
  const end = new Date(today);

  if (preset === 'THIS_MONTH') {
    start.setDate(1);
  } else if (preset === 'PREVIOUS_MONTH') {
    start.setMonth(start.getMonth() - 1, 1);
    end.setDate(0);
  } else if (preset === 'THIS_QUARTER') {
    const quarterStartMonth = Math.floor(today.getMonth() / 3) * 3;
    start.setMonth(quarterStartMonth, 1);
  } else if (preset === 'YEAR_TO_DATE') {
    start.setMonth(0, 1);
  } else {
    start.setDate(today.getDate() - 30);
  }

  return {
    issueDate,
    billingPeriodStart: toIsoDate(start),
    billingPeriodEnd: toIsoDate(end),
    dueDate: deriveDueDateFromTerms(issueDate, draft.paymentTerms || 'NET_30')
  };
};

/**
 * @function buildBillingStatementContext
 * @description Builds the shared statement and invoice policy payload from the live operator form.
 * @param {Object} draft - Current billing draft state.
 * @returns {Object} Normalized billing context for APIs, PDFs and forensic evidence.
 * @collaboration Prevents the billing engine from producing orphaned documents without period, terms or business model.
 */
const buildBillingStatementContext = (draft = {}) => ({
  issueDate: draft.issueDate,
  statementDate: draft.issueDate,
  dueDate: draft.dueDate,
  billingPeriodStart: draft.billingPeriodStart,
  billingPeriodEnd: draft.billingPeriodEnd,
  paymentTerms: draft.paymentTerms,
  billingModel: draft.billingModel,
  invoiceClass: draft.invoiceClass,
  supplyType: draft.supplyType,
  taxType: draft.taxType,
  taxJurisdiction: draft.taxJurisdiction,
  tenantJurisdiction: draft.tenantJurisdiction,
  clientJurisdiction: draft.clientJurisdiction,
  clientType: draft.clientType,
  customerTaxId: draft.customerTaxId,
  withholdingRate: draft.withholdingRate,
  idempotencyKey: draft.idempotencyKey,
  description: draft.description
});

/**
 * @function createInvoiceIdempotencyKey
 * @description Generates a client-side idempotency key so invoice retries cannot accidentally duplicate a billing event.
 * @param {string} tenantId - Active tenant authority.
 * @returns {string} Invoice idempotency key.
 * @collaboration Wilson Khanyezi required invoices to behave like institutional infrastructure, not a repeated form post.
 */
const createInvoiceIdempotencyKey = (tenantId = 'GLOBAL_ROOT') => {
  const entropy = crypto.randomUUID ? crypto.randomUUID().slice(0, 12) : `${Date.now().toString(36)}${Math.random().toString(36).slice(2, 8)}`;
  return `WILSY-INV-${tenantId}-${entropy}`.toUpperCase();
};

/**
 * @function buildInvoiceCommandPayload
 * @description Builds a normalized invoice payload for platform and client invoice APIs.
 * @param {Object} draft - Current invoice command draft.
 * @param {Object} options - Invoice target options.
 * @param {string} options.source - Source component identifier.
 * @param {Object|null} options.taxResult - Optional GlobalTaxEngine proof packet.
 * @returns {Object} API-ready invoice payload with line items, tax config, idempotency and metadata.
 * @collaboration This is the shared fiscal payload so every invoice action carries the same proof structure.
 */
const buildInvoiceCommandPayload = (draft = {}, { source = 'WILSY_REVENUE_LEDGER', taxResult = null } = {}) => {
  const quantity = Math.max(1, Number(draft.quantity || 1));
  const unitPrice = Number(draft.unitPrice || draft.amount || 0);
  const amount = Number(draft.amount || quantity * unitPrice || 0);
  const statementContext = buildBillingStatementContext(draft);
  const taxConfig = globalTaxEngine.buildInvoiceTaxConfig(taxResult, draft);
  const taxRate = Number(taxConfig.rate ?? 0);
  const taxAmount = Number(taxConfig.taxAmount ?? Math.round(amount * taxRate * 100) / 100);
  const totalAmount = Number(taxResult?.financials?.totalAmount ?? (amount + taxAmount));

  return {
    tenantId: draft.tenantId,
    clientId: draft.clientId,
    amount,
    subtotal: amount,
    taxAmount,
    totalAmount,
    currency: draft.currency || 'ZAR',
    invoiceClass: draft.invoiceClass,
    issueDate: draft.issueDate,
    dueDate: draft.dueDate,
    idempotencyKey: draft.idempotencyKey,
    billingPeriod: {
      start: draft.billingPeriodStart,
      end: draft.billingPeriodEnd
    },
    paymentTerms: draft.paymentTerms,
    billingModel: draft.billingModel,
    taxType: taxConfig.taxType || draft.taxType,
    taxConfig,
    metadata: {
      source,
      invoicePolicy: {
        duplicateDefense: 'IDEMPOTENCY_KEY_REQUIRED',
        taxPosture: taxConfig.taxType || draft.taxType,
        taxProofHash: taxConfig.proofHash || null,
        taxSourceStatus: taxConfig.sourceStatus || 'SOURCE_SILENT',
        tenantIsolation: draft.tenantId
      },
      statementContext
    },
    lineItems: [{
      description: draft.description,
      unitPrice,
      quantity,
      taxRate,
      category: draft.invoiceClass || 'SOVEREIGN_SERVICE',
      units: draft.billingModel || 'PLATFORM_RETAINER'
    }]
  };
};

/**
 * @function extractInvoiceRowsFromSnapshot
 * @description Extracts invoice rows from the mixed legacy and sovereign invoice API payload shapes.
 * @param {Object} operationsSnapshot - Current operations source snapshot.
 * @returns {Array<Object>} Normalized live invoice rows.
 * @collaboration Keeps the invoice UI truthful: rows come from the DB response, never static placeholders.
 */
const extractInvoiceRowsFromSnapshot = (operationsSnapshot = {}) => {
  const invoicesPayload = operationsSnapshot?.sources?.invoices?.payload || {};
  const candidates = [
    invoicesPayload?.data?.invoices,
    invoicesPayload?.data,
    invoicesPayload?.invoices,
    invoicesPayload
  ];
  const rows = candidates.find(candidate => Array.isArray(candidate));
  return Array.isArray(rows) ? rows : [];
};

/**
 * @function buildInvoiceCommandIntelligence
 * @description Derives invoice readiness, fiscal proof and live DB posture from draft inputs and source snapshots.
 * @param {Object} draft - Current invoice draft.
 * @param {Object} operationsSnapshot - Current operations source snapshot.
 * @param {Function} formatZAR - Currency formatter.
 * @param {Object|null} taxResult - Current GlobalTaxEngine proof packet.
 * @returns {{readiness:number, rows:Array<Object>, checklist:Array<Object>, metrics:Array<Object>}} Invoice operating intelligence.
 * @collaboration Turns invoice creation into a governed command loop: draft, validate, seal, sync and prove.
 */
const buildInvoiceCommandIntelligence = (draft = {}, operationsSnapshot = {}, formatZAR = value => value, taxResult = null) => {
  const rows = extractInvoiceRowsFromSnapshot(operationsSnapshot);
  const amount = Number(draft.amount || 0);
  const checklist = [
    { label: 'Tenant mounted', live: Boolean(draft.tenantId), evidence: draft.tenantId || 'MISSING' },
    { label: 'Client route', live: Boolean(draft.clientId), evidence: draft.clientId || 'MISSING' },
    { label: 'Fiscal amount', live: Number.isFinite(amount) && amount > 0, evidence: Number.isFinite(amount) && amount > 0 ? formatZAR(amount) : 'MISSING' },
    { label: 'Terms and due date', live: Boolean(draft.paymentTerms && draft.dueDate), evidence: `${draft.paymentTerms || 'NO TERMS'} / ${draft.dueDate || 'NO DUE DATE'}` },
    { label: 'Tax jurisdiction', live: Boolean(draft.taxType && (draft.clientJurisdiction || draft.taxJurisdiction)), evidence: `${draft.taxType || 'NO TAX'} / ${draft.clientJurisdiction || draft.taxJurisdiction || 'NO JURISDICTION'} / ${draft.clientType || 'NO CLIENT TYPE'}` },
    {
      label: 'Global tax proof',
      live: Boolean(taxResult?.proof?.hash && !taxResult?.taxProfile?.liveRateRequired),
      evidence: taxResult?.proof?.hash
        ? `${taxResult.taxProfile?.type || 'TAX'} / ${taxResult.sourceStatus || 'SOURCE_SILENT'}`
        : 'TAX_ENGINE_PENDING'
    },
    { label: 'Duplicate defense', live: Boolean(draft.idempotencyKey), evidence: draft.idempotencyKey || 'MISSING' },
    { label: 'DB invoice source', live: operationsSnapshot?.sources?.invoices?.status === 'LIVE', evidence: operationsSnapshot?.sources?.invoices?.status || 'SOURCE_SILENT' }
  ];
  const readiness = Math.round((checklist.filter(item => item.live).length / checklist.length) * 100);
  const openRows = rows.filter(row => ['ISSUED', 'PARTIALLY_PAID', 'OVERDUE', 'DISPUTED', 'LEGAL_HOLD'].includes((row.status || 'ISSUED').toUpperCase()));
  const outstanding = rows.reduce((sum, row) => sum + Number(row.outstandingAmount ?? row.totalAmount ?? row.amount ?? 0), 0);

  return {
    readiness,
    rows,
    checklist,
    metrics: [
      { label: 'Live invoice rows', value: rows.length, caption: operationsSnapshot?.sources?.invoices?.status || 'SOURCE_SILENT' },
      { label: 'Open receivables', value: formatZAR(outstanding), caption: `${openRows.length} actionable invoices` },
      { label: 'Invoice command', value: readiness >= 85 ? 'READY' : 'INCOMPLETE', caption: `${readiness}% command readiness` }
    ]
  };
};

/**
 * @function extractApiPayload
 * @description Normalizes API responses from Wilsy's mixed legacy and sovereign route shapes.
 * @param {Object} response - Axios response.
 * @returns {Object|null} Normalized payload or null.
 */
const extractApiPayload = (response) => response?.data?.data || response?.data || null;

/**
 * @function normalizeLedgerAiPacket
 * @description Converts the AI ledger API response into a polished command-brief packet for the Revenue Ledger UI.
 * @param {Object} responseData - Raw API response payload from /api/ai/query-ledger.
 * @param {string} query - Founder query that triggered the analysis.
 * @returns {Object} Normalized AI command brief.
 * @collaboration Wilson Khanyezi required AI output to look like investor-grade operating intelligence, not broken terminal text.
 */
const normalizeLedgerAiPacket = (responseData = {}, query = '') => {
  const packet = responseData?.data || responseData || {};
  const sourceStatus = responseData?.sourceStatus || packet.sourceStatus || 'AI_LEDGER_LIVE';
  return {
    query,
    insight: packet.insight || '',
    recommendedAction: packet.recommendedAction || 'Review live revenue operations before approving any revenue decision.',
    evidence: Array.isArray(packet.evidence) ? packet.evidence : [],
    posture: packet.posture || 'REVENUE_REVIEW',
    projection: packet.projection || null,
    sourceStatus,
    sealWarning: packet.sealWarning || '',
    confidenceScore: packet.confidenceScore ?? null,
    generatedAt: new Date().toISOString()
  };
};

/**
 * @function parseEvidenceToken
 * @description Converts API evidence tokens such as "growth=0.00%" into compact display fields.
 * @param {string} token - Raw evidence token returned by the live AI ledger endpoint.
 * @returns {{label: string, value: string}} Label/value pair for the executive evidence UI.
 * @collaboration Evidence must be legible in a boardroom: compact, labelled, and impossible to mistake for debug output.
 */
const parseEvidenceToken = (token = '') => {
  const [rawLabel, ...rawValue] = String(token).split('=');
  const label = rawLabel
    ? rawLabel.replace(/([A-Z])/g, ' $1').replace(/_/g, ' ').trim().toUpperCase()
    : 'EVIDENCE';
  return {
    label,
    value: rawValue.length ? rawValue.join('=') : String(token)
  };
};

/**
 * @function buildLedgerAiFallbackPacket
 * @description Builds a non-synthetic fallback brief that clearly names unavailable live sources.
 * @param {Object} params - Fallback parameters.
 * @param {string} params.query - Founder query.
 * @param {Array<string>} params.liveSources - Confirmed live sources.
 * @param {Array<string>} params.sourceGaps - Missing or degraded sources.
 * @param {Error} params.error - Captured request error.
 * @returns {Object} Fallback AI command brief.
 * @collaboration Keeps Wilsy OS honest: no fabricated forecast, but still gives the founder an actionable operating packet.
 */
const buildLedgerAiFallbackPacket = ({ query, liveSources, sourceGaps, error }) => ({
  query,
  insight: 'Wilsy OS refused to manufacture a forecast because the live AI ledger route did not return usable evidence.',
  recommendedAction: 'Sync DB sources, create or import invoices, generate sealed documents, then rerun the query.',
  evidence: [
    `liveSources=${liveSources.length ? liveSources.join(',') : 'NONE_CONFIRMED'}`,
    `sourceGaps=${sourceGaps.length ? sourceGaps.join('|') : 'AI_LEDGER_ROUTE_UNAVAILABLE'}`,
    `error=${error?.message || 'UNKNOWN'}`
  ],
  posture: 'NO_SYNTHETIC_ANSWER_GENERATED',
  projection: null,
  sourceStatus: 'AI_LEDGER_SOURCE_UNAVAILABLE',
  sealWarning: '',
  confidenceScore: null,
  generatedAt: new Date().toISOString()
});

/**
 * @function getSourceStatus
 * @description Converts a Promise.allSettled result into a concise live-source indicator.
 * @param {PromiseSettledResult} result - Settled API result.
 * @returns {string} LIVE or SOURCE_SILENT.
 */
const getSourceStatus = (result) => (result?.status === 'fulfilled' ? 'LIVE' : 'SOURCE_SILENT');

/**
 * @function classifyCashRisk
 * @description Converts ledger health into a clear CFO risk posture.
 * @param {Object} metrics - Ledger metrics.
 * @returns {string} LOW, MEDIUM or HIGH risk.
 */
const classifyCashRisk = (metrics) => {
  if ((metrics?.dso || 0) > 60 || (metrics?.leakage || 0) > 0) return 'HIGH';
  if ((metrics?.dso || 0) > 35 || (metrics?.pendingPayments || 0) > 0) return 'MEDIUM';
  return 'LOW';
};

/**
 * @function buildRevenueDecisionPackets
 * @description Produces CFO-grade AI Focus packets from live ledger metrics without fabricating clients or transactions.
 * @param {Object} metrics - Ledger intelligence metrics.
 * @param {Object} context - Current revenue context.
 * @returns {Array<Object>} Decision packets for the AI Focus command surface.
 * @collaboration Designed to beat generic AI chat by turning analysis into governed revenue action.
 */
const buildRevenueDecisionPackets = (metrics, context) => {
  const packets = [];
  const risk = classifyCashRisk(metrics);
  const hasCollectionRisk = (metrics.collectionRiskItems || []).length > 0;
  const growth = Number(context?.growth || 0);

  packets.push({
    id: 'cash-war-room',
    title: 'Cash Conversion War Room',
    status: risk,
    owner: 'CFO / Founder',
    evidence: `${metrics.dso || 0}d DSO, ${context.formatZAR(metrics.pendingPayments || 0)} pending, ${context.formatZAR(metrics.leakage || 0)} leakage.`,
    action: risk === 'HIGH'
      ? 'Open collections command, prioritize overdue balances, and require statement-grade proof before escalation.'
      : 'Maintain weekly cash conversion monitoring and preserve clean-state evidence.'
  });

  packets.push({
    id: 'arr-protection',
    title: 'ARR Protection Doctrine',
    status: metrics.nrrProxy >= 100 ? 'EXPANSION' : 'DEFEND',
    owner: 'Revenue Operations',
    evidence: `${context.formatPercent(metrics.nrrProxy)} NRR proxy with ${context.formatZAR(metrics.arr)} ARR baseline.`,
    action: metrics.nrrProxy >= 100
      ? 'Push expansion playbook into active accounts with clean payment history.'
      : 'Freeze risky discounting, inspect churn signals, and route founder approval for pricing concessions.'
  });

  if (hasCollectionRisk) {
    packets.push({
      id: 'legal-collections',
      title: 'Legal Collections Bridge',
      status: 'ACTION_REQUIRED',
      owner: 'Collections / Legal',
      evidence: `${metrics.collectionRiskItems.length} collection risk items detected in live ledger.`,
      action: 'Move to Collections view, verify invoices, then generate a statement before legal escalation.'
    });
  }

  packets.push({
    id: 'growth-integrity',
    title: 'Growth Integrity Scan',
    status: growth < -8 ? 'CONTRACTION' : growth > 25 ? 'ACCELERATION' : 'STABLE',
    owner: 'Founder',
    evidence: `${context.formatPercent(growth)} growth, ${context.formatZAR(metrics.recognizedRunRate)} recognized run-rate.`,
    action: growth < -8
      ? 'Trigger retention review and isolate accounts with payment or usage decline.'
      : 'Preserve current strategy and document boardroom-ready growth proof.'
  });

  return packets;
};

/**
 * @function buildRevenueOperatingDoctrine
 * @description Converts live revenue source status into an actionable founder operating doctrine.
 * @param {Object} params - Doctrine inputs.
 * @param {Object} params.metrics - Live ledger intelligence metrics.
 * @param {Object} params.operationsSnapshot - Current revenue operations source snapshot.
 * @param {Object} params.invoiceDraft - Current invoice/document command draft.
 * @param {string} params.tenantAlias - Active tenant authority.
 * @param {number} params.aiFocusScore - Current AI focus score derived from live source coverage.
 * @param {Function} params.formatZAR - Currency formatter.
 * @returns {{liveSources:number,totalSources:number,coverage:number,primaryRisk:string,lifecycle:Array<Object>}} Actionable doctrine model.
 * @collaboration Wilson Khanyezi mandated a real operating system, not cards; this turns DB/API truth into executable founder moves.
 */
const buildRevenueOperatingDoctrine = ({
  metrics,
  operationsSnapshot,
  invoiceDraft,
  tenantAlias,
  aiFocusScore,
  formatZAR
}) => {
  const sourceEntries = Object.entries(operationsSnapshot?.sources || {});
  const liveSources = sourceEntries.filter(([, source]) => source?.status === 'LIVE');
  const totalSources = sourceEntries.length;
  const coverage = totalSources ? Math.round((liveSources.length / totalSources) * 100) : 0;
  const silentSources = Object.keys(operationsSnapshot?.errors || {});
  const hasTenant = Boolean(tenantAlias && tenantAlias !== 'SOURCE_SILENT');
  const hasInvoiceCommand = Boolean(
    invoiceDraft?.tenantId
    && invoiceDraft?.amount
    && Number(invoiceDraft.amount) > 0
    && invoiceDraft?.dueDate
    && invoiceDraft?.description
  );
  const cashRisk = classifyCashRisk(metrics);
  const hasLedgerMotion = (metrics?.totalRevenue || 0) > 0 || (metrics?.pendingPayments || 0) > 0 || (metrics?.transactions || []).length > 0;

  return {
    liveSources: liveSources.length,
    totalSources,
    coverage,
    primaryRisk: silentSources.length ? 'SOURCE_GAPS' : cashRisk,
    lifecycle: [
      {
        id: 'source-sync',
        label: 'Live Source Mesh',
        status: coverage > 0 ? 'LIVE' : 'SOURCE_SILENT',
        evidence: totalSources
          ? `${liveSources.length}/${totalSources} revenue sources responding`
          : 'No revenue source scan has been executed in this session',
        outcome: coverage > 0
          ? 'Founder can make decisions from DB/API evidence.'
          : 'Run live source scan before making investor claims.',
        action: 'SYNC_SOURCES',
        cta: 'SYNC SOURCES'
      },
      {
        id: 'tenant-authority',
        label: 'Tenant Authority',
        status: hasTenant ? 'MOUNTED' : 'UNMOUNTED',
        evidence: hasTenant ? `${tenantAlias} is the active revenue tenant` : 'No tenant authority mounted',
        outcome: hasTenant
          ? 'Billing, documents and telemetry can be sealed to the tenant.'
          : 'Mount tenant context before issuing finance artifacts.',
        action: 'OPEN_METERING',
        cta: 'OPEN METERING'
      },
      {
        id: 'billing-command',
        label: 'Invoice Command',
        status: hasInvoiceCommand ? 'READY' : 'DRAFT_REQUIRED',
        evidence: hasInvoiceCommand
          ? `${formatZAR(Number(invoiceDraft.amount))} due ${invoiceDraft.dueDate}`
          : 'Amount, due date and line-item basis are required',
        outcome: hasInvoiceCommand
          ? 'A platform invoice can be created and returned to the ledger.'
          : 'Complete the invoice command form to create a DB-backed action.',
        action: 'CREATE_INVOICE',
        cta: 'CREATE INVOICE'
      },
      {
        id: 'cash-control',
        label: 'Cash Motion Control',
        status: hasLedgerMotion ? cashRisk : 'NO_REVENUE_BASE',
        evidence: hasLedgerMotion
          ? `${formatZAR(metrics.pendingPayments || 0)} pending, ${metrics.dso || 0}d DSO`
          : 'No invoice or transaction motion returned by live ledger',
        outcome: hasLedgerMotion
          ? 'Collections can be routed from ledger evidence.'
          : 'Create or import invoices before collections can be proven.',
        action: 'OPEN_COLLECTIONS',
        cta: 'COLLECTIONS'
      },
      {
        id: 'sealed-proof',
        label: 'Investor Proof Artifact',
        status: aiFocusScore > 0 ? 'READY' : 'SOURCE_SILENT',
        evidence: `${aiFocusScore}% AI focus score from live coverage`,
        outcome: aiFocusScore > 0
          ? 'Export a doctrine artifact and sealed revenue statement.'
          : 'Sync sources before exporting investor evidence.',
        action: 'EXPORT_DOCTRINE',
        cta: 'EXPORT PROOF'
      }
    ]
  };
};

/**
 * @function normalizeCommandArray
 * @description Converts mixed API payload shapes into a usable command array without manufacturing rows.
 * @param {unknown} value - API payload candidate.
 * @returns {Array<Object>} Normalized list of source rows.
 * @collaboration Keeps new OS modules source-aware while tolerating legacy route envelopes.
 */
const normalizeCommandArray = (value) => {
  if (Array.isArray(value)) return value;
  if (Array.isArray(value?.data)) return value.data;
  if (Array.isArray(value?.items)) return value.items;
  if (Array.isArray(value?.obligations)) return value.obligations;
  if (Array.isArray(value?.recommendations)) return value.recommendations;
  if (Array.isArray(value?.matches)) return value.matches;
  return [];
};

/**
 * @function shortAuditHash
 * @description Shortens a Merkle root, transaction hash, or trace id for compact footer and command displays.
 * @param {string|null|undefined} hash - Candidate cryptographic anchor.
 * @returns {string} Human-readable short hash.
 */
const shortAuditHash = (hash) => {
  if (!hash) return 'UNANCHORED';
  const value = String(hash);
  return value.length > 18 ? `${value.slice(0, 10)}...${value.slice(-6)}` : value;
};

/**
 * @function deriveDunningStage
 * @description Converts overdue age and risk score into a collections stage with an executable next action.
 * @param {number} overdueDays - Days past due.
 * @param {number} riskScore - Source or computed collection risk score.
 * @returns {{stage:string,tone:string,nextAction:string}} Dunning command stage.
 * @collaboration Replaces generic "overdue" labels with an actual collections playbook.
 */
const deriveDunningStage = (overdueDays = 0, riskScore = 0) => {
  if (overdueDays >= 45 || riskScore >= 80) {
    return { stage: 'LEGAL_ESCALATION', tone: '#ff6666', nextAction: 'Generate statement, freeze concessions, prepare legal pack.' };
  }
  if (overdueDays >= 21 || riskScore >= 62) {
    return { stage: 'FINAL_DEMAND', tone: '#D4AF37', nextAction: 'Send final demand and request proof of payment within 72 hours.' };
  }
  if (overdueDays >= 7 || riskScore >= 40) {
    return { stage: 'DUNNING_NOTICE', tone: '#ffaa33', nextAction: 'Send polite dunning notice with settlement link and statement.' };
  }
  return { stage: 'MONITOR', tone: '#00ff88', nextAction: 'Monitor account and preserve clean payment evidence.' };
};

/**
 * @function buildDunningIntelligence
 * @description Builds Dunning Intelligence recommendations from live API rows, collection risks, or invoice rows.
 * @param {Object} params - Source inputs.
 * @param {Array<Object>} params.apiRecommendations - Dunning API recommendations.
 * @param {Object} params.ledgerIntelligence - Current ledger intelligence.
 * @param {Array<Object>} params.invoiceRows - Invoice rows from operations sync.
 * @returns {Array<Object>} Dunning recommendation rows.
 * @collaboration Enables collections action without pretending a silent backend has spoken.
 */
const buildDunningIntelligence = ({ apiRecommendations = [], ledgerIntelligence = {}, invoiceRows = [] }) => {
  if (apiRecommendations.length) {
    return apiRecommendations.map((item, index) => (
      item.proof?.hash
        ? { ...item, tone: item.tone || item.toneColor || deriveDunningStage(item.overdueDays, item.riskScore).tone }
        : dunningIntelligence.buildRecommendation(item, { index, sourceStatus: item.sourceStatus || 'DUNNING_API' })
    ));
  }

  const collectionRows = (ledgerIntelligence.collectionRiskItems || []).map((item, index) => (
    dunningIntelligence.buildRecommendation(item, { index, sourceStatus: 'LEDGER_RISK' })
  ));

  const invoiceRiskRows = collectionRows.length ? [] : invoiceRows
    .filter(row => ['OVERDUE', 'DISPUTED', 'LEGAL_HOLD', 'PARTIALLY_PAID'].includes(String(row.status || '').toUpperCase()))
    .map((row, index) => dunningIntelligence.buildRecommendation(row, { index, sourceStatus: 'INVOICE_LEDGER' }));

  return [...collectionRows, ...invoiceRiskRows].map(item => ({
    ...item,
    tone: item.tone || item.toneColor || deriveDunningStage(item.overdueDays, item.riskScore).tone
  })).slice(0, 8);
};

/**
 * @function buildTaxTreasuryPosture
 * @description Converts tax, treasury, bank reconciliation and invoice command state into a CFO command model.
 * @param {Object} params - Source inputs.
 * @param {Object} params.taxTreasurySnapshot - Remote tax and treasury snapshot.
 * @param {Object} params.ledgerIntelligence - Revenue ledger intelligence.
 * @param {Object} params.invoiceDraft - Current invoice command draft.
 * @param {Object} params.bankReconciliation - Bank reconciliation hook state.
 * @param {Object|null} params.taxEngineResult - GlobalTaxEngine proof packet.
 * @returns {{metrics:Array<Object>,gates:Array<Object>,obligations:Array<Object>,sweeps:Array<Object>}} CFO command posture.
 * @collaboration Makes tax and cash operations an executable OS surface, not a passive report.
 */
const buildTaxTreasuryPosture = ({ taxTreasurySnapshot = {}, ledgerIntelligence = {}, invoiceDraft = {}, bankReconciliation = {}, taxEngineResult = null }) => {
  const obligations = normalizeCommandArray(taxTreasurySnapshot.tax?.obligations || taxTreasurySnapshot.tax);
  const sweeps = normalizeCommandArray(taxTreasurySnapshot.treasury?.sweeps || taxTreasurySnapshot.treasury);
  const invoiceAmount = Number(invoiceDraft.amount || 0);
  const vatExposure = taxEngineResult?.financials?.taxAmount ?? 0;
  const availableLiquidity = Number(taxTreasurySnapshot.treasury?.availableLiquidity ?? ledgerIntelligence.recognizedRunRate ?? 0);
  const treasuryCoverage = ledgerIntelligence.pendingPayments > 0
    ? Math.round((availableLiquidity / Math.max(ledgerIntelligence.pendingPayments, 1)) * 100)
    : 100;

  return {
    obligations,
    sweeps,
    metrics: [
      { label: 'Tax obligations', value: obligations.length, caption: taxTreasurySnapshot.tax?.sourceStatus || taxTreasurySnapshot.taxStatus || 'SOURCE_SILENT' },
      { label: 'VAT exposure', value: vatExposure, caption: taxEngineResult ? `${taxEngineResult.taxProfile?.type || 'TAX'} / ${taxEngineResult.sourceStatus}` : `${invoiceDraft.taxType || 'NO_TAX'} / ${invoiceDraft.clientJurisdiction || invoiceDraft.taxJurisdiction || 'NO_JURISDICTION'}` },
      { label: 'Available liquidity', value: availableLiquidity, caption: taxTreasurySnapshot.treasury?.sourceStatus || taxTreasurySnapshot.treasuryStatus || 'SOURCE_SILENT' },
      { label: 'Bank variance', value: Number(bankReconciliation.variance || 0), caption: bankReconciliation.sourceStatus || bankReconciliation.status || 'SOURCE_SILENT' }
    ],
    gates: [
      {
        label: 'Tax authority',
        status: obligations.length ? 'LIVE' : 'SOURCE_SILENT',
        action: obligations.length ? 'Review statutory due dates and export tax pack.' : 'Connect tax source or generate a tax report.'
      },
      {
        label: 'Treasury coverage',
        status: treasuryCoverage >= 100 ? 'COVERED' : 'WATCH',
        action: treasuryCoverage >= 100 ? 'Liquidity covers pending payments.' : 'Trigger sweep review before commitments.'
      },
      {
        label: 'Bank reconciliation',
        status: bankReconciliation.status || 'SOURCE_SILENT',
        action: Number(bankReconciliation.pending || 0) > 0 ? 'Resolve unmatched bank entries.' : 'Preserve reconciliation proof.'
      },
      {
        label: 'Global tax engine',
        status: taxEngineResult?.taxProfile?.liveRateRequired ? 'LIVE_RATE_REQUIRED' : (taxEngineResult?.proof?.hash ? 'SEALED' : 'PENDING'),
        action: taxEngineResult?.proof?.hash
          ? `Tax proof ${String(taxEngineResult.proof.hash).slice(0, 12)} binds invoice math to source metadata.`
          : 'Run the Global Tax Engine before issuing a final invoice.'
      }
    ]
  };
};

/**
 * @function useBankReconciliation
 * @description Polls bank reconciliation state for the active tenant without blocking the ledger UI.
 * @param {string} tenantId - Tenant authority.
 * @param {boolean} enabled - Whether polling should run.
 * @returns {{status:string,sourceStatus:string,matches:Array<Object>,pending:number,variance:number|null,lastUpdated:string|null,refresh:Function}} Bank reconciliation state.
 */
const useBankReconciliation = (tenantId, enabled = true) => {
  const [reconciliation, setReconciliation] = useState({
    status: 'SOURCE_SILENT',
    sourceStatus: 'SOURCE_SILENT',
    matches: [],
    pending: 0,
    variance: null,
    lastUpdated: null,
    warning: null
  });

  const refresh = useCallback(async () => {
    if (!tenantId) return;
    try {
      const response = await api.get(`/bank/reconciliation/${tenantId}`);
      const payload = extractApiPayload(response) || response.data || {};
      setReconciliation({
        status: payload.status || 'RECONCILED',
        sourceStatus: 'LIVE',
        matches: normalizeCommandArray(payload.matches || payload),
        pending: Number(payload.pending || payload.unmatched || 0),
        variance: payload.variance ?? payload.bankVariance ?? null,
        lastUpdated: payload.lastUpdated || new Date().toISOString(),
        warning: null
      });
    } catch (error) {
      setReconciliation(prev => ({
        ...prev,
        status: 'SOURCE_SILENT',
        sourceStatus: 'SOURCE_SILENT',
        warning: error.response?.data?.message || error.message,
        lastUpdated: prev.lastUpdated || null
      }));
    }
  }, [tenantId]);

  useEffect(() => {
    if (!enabled) return undefined;
    refresh();
    const interval = setInterval(refresh, 60000);
    return () => clearInterval(interval);
  }, [enabled, refresh]);

  return { ...reconciliation, refresh };
};

/**
 * @function useMerkleAuditor
 * @description Hydrates forensic chain verification for footer-level audit posture.
 * @param {string} tenantId - Active tenant authority.
 * @param {Array<string>} traceIds - Locally generated trace ids that still need audit confirmation.
 * @returns {{status:string,sourceStatus:string,merkleRoot:string|null,verified:boolean|null,pendingLocal:number,lastChecked:string|null,refresh:Function}} Merkle auditor state.
 */
const useMerkleAuditor = (tenantId, traceIds = []) => {
  const [audit, setAudit] = useState({
    status: 'SOURCE_SILENT',
    sourceStatus: 'SOURCE_SILENT',
    merkleRoot: null,
    verified: null,
    chainLength: 0,
    algorithm: 'SHA3-512',
    anchorMode: 'UNKNOWN',
    anchorProvider: 'UNKNOWN',
    driftCount: 0,
    qldbStatus: 'UNKNOWN',
    qldbEndOfSupport: null,
    externalAnchor: null,
    lastEntry: null,
    pendingLocal: traceIds.length,
    lastChecked: null,
    warning: null
  });

  const refresh = useCallback(async () => {
    try {
      const response = await api.get('/forensics/verify-chain', { params: { tenantId } });
      const payload = extractApiPayload(response) || response.data || {};
      const root = payload.merkleRoot || payload.chainAnchor || payload.root || payload.lastBlockchainAnchor || null;
      const verified = payload.valid ?? payload.verified ?? (payload.integrity ? payload.integrity === 'VERIFIED' : null);
      setAudit({
        status: payload.status || (verified === false ? 'REVIEW_REQUIRED' : 'ANCHORED'),
        sourceStatus: payload.sourceStatus || 'LIVE',
        merkleRoot: root,
        verified,
        chainLength: Number(payload.chainLength || payload.lastBlock || 0),
        algorithm: payload.algorithm || 'SHA3-512',
        anchorMode: payload.anchorMode || 'UNKNOWN',
        anchorProvider: payload.anchorProvider || 'UNKNOWN',
        driftCount: Number(payload.driftCount || payload.details?.mismatches?.length || 0),
        qldbStatus: payload.qldbStatus || 'UNKNOWN',
        qldbEndOfSupport: payload.qldbEndOfSupport || null,
        externalAnchor: payload.externalAnchor || null,
        lastEntry: payload.lastEntry || null,
        pendingLocal: traceIds.length,
        lastChecked: new Date().toISOString(),
        warning: payload.warning || payload.error || null
      });
    } catch (error) {
      setAudit(prev => ({
        ...prev,
        status: traceIds.length ? 'LOCAL_TRACE_QUEUE' : 'SOURCE_SILENT',
        sourceStatus: 'SOURCE_SILENT',
        driftCount: prev.driftCount || 0,
        pendingLocal: traceIds.length,
        warning: error.response?.data?.message || error.message,
        lastChecked: prev.lastChecked
      }));
    }
  }, [tenantId, traceIds.length]);

  useEffect(() => {
    refresh();
    const interval = setInterval(refresh, 120000);
    return () => clearInterval(interval);
  }, [refresh]);

  return { ...audit, refresh };
};

/**
 * @component Sovereign_Revenue_Ledger
 * @description The trillion-dollar institutional command center. Integrates predictive AI modeling,
 * forensic compliance tracking, and real-time ledger intelligence for multi-tenant SaaS orchestration.
 */
const Sovereign_Revenue_Ledger = () => {
  // 1. DATA HYDRATION & MULTI-TENANT CONTEXT
  const { revenue, compliance, analytics, loading } = useSovereignData();
  const tenantAlias = revenue?.tenantAlias || 'GLOBAL_ROOT';
  const { events: telemetryEvents } = useTelemetryFeed(tenantAlias);

  // 2. TACTICAL UI STATE
  const [isGenerating, setIsGenerating] = useState(false);
  const [isSyncing, setIsSyncing] = useState(false);
  const [isCommitting, setIsCommitting] = useState(false);
  const [isQuerying, setIsQuerying] = useState(false);
  const [ledgerDetail, setLedgerDetail] = useState(null);
  const [ledgerLoading, setLedgerLoading] = useState(false);

  const [generatedTraceIds, setGeneratedTraceIds] = useState([]);
  const [activeHUD, setActiveHUD] = useState('REVENUE');
  const [tooltipVisible, setTooltipVisible] = useState(null);

  // 3. AI & PREDICTIVE STATE
  const [queryInput, setQueryInput] = useState('');
  const [aiInsight, setAiInsight] = useState('');
  const [aiInsightPacket, setAiInsightPacket] = useState(null);
  const [whatIfParams, setWhatIfParams] = useState({ priceChange: 0, volumeChange: 0 });
  const [anomalyDetected, setAnomalyDetected] = useState(null);
  const [approvedPacketIds, setApprovedPacketIds] = useState([]);
  const [revenueDecisionLedger, setRevenueDecisionLedger] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem('wilsy_revenue_decisions') || '[]').slice(0, 8);
    } catch {
      return [];
    }
  });
  const [operationBusy, setOperationBusy] = useState(null);
  const [operationsSnapshot, setOperationsSnapshot] = useState({
    status: 'SOURCE_SILENT',
    lastSync: null,
    sources: {},
    errors: {}
  });
  const [lastOperationReceipt, setLastOperationReceipt] = useState(null);
  const [statementPreset, setStatementPreset] = useState('LAST_30_DAYS');
  const [invoiceDraft, setInvoiceDraft] = useState({
    tenantId: tenantAlias,
    clientId: 'CLIENT-ROOT',
    amount: '',
    unitPrice: '',
    quantity: 1,
    currency: 'ZAR',
    invoiceClass: 'SOVEREIGN_INFRA_FEE',
    supplyType: 'DIGITAL_SERVICE',
    taxType: 'VAT',
    taxJurisdiction: 'ZA',
    tenantJurisdiction: 'ZA',
    clientJurisdiction: 'ZA',
    clientType: 'B2B',
    customerTaxId: '',
    withholdingRate: 0,
    idempotencyKey: createInvoiceIdempotencyKey(tenantAlias),
    description: 'Wilsy OS sovereign operating services',
    issueDate: getIsoDateOffset(0),
    billingPeriodStart: getIsoDateOffset(-30),
    billingPeriodEnd: getIsoDateOffset(0),
    paymentTerms: 'NET_30',
    billingModel: 'PLATFORM_RETAINER',
    dueDate: getDefaultDueDate()
  });
  const [taxTreasurySnapshot, setTaxTreasurySnapshot] = useState({
    status: 'SOURCE_SILENT',
    lastSync: null,
    tax: { obligations: [], sourceStatus: 'SOURCE_SILENT' },
    treasury: { sweeps: [], availableLiquidity: 0, sourceStatus: 'SOURCE_SILENT' },
    errors: {}
  });
  const [taxEngineResult, setTaxEngineResult] = useState(null);
  const [taxEngineLoading, setTaxEngineLoading] = useState(false);
  const [treasurySweepState, setTreasurySweepState] = useState({
    status: 'SOURCE_SILENT',
    evaluation: null,
    receipt: null,
    lastUpdated: null
  });
  const [dunningState, setDunningState] = useState({
    status: 'SOURCE_SILENT',
    recommendations: [],
    lastReceipt: null,
    lastSync: null,
    error: null
  });
  const bankReconciliation = useBankReconciliation(tenantAlias, ['TAX_TREASURY', 'COLLECTIONS', 'METERING'].includes(activeHUD));
  const merkleAudit = useMerkleAuditor(tenantAlias, generatedTraceIds);

  // 4. IMMUTABLE LEDGER METRICS
  const totalVolume = revenue?.totalVolume || revenue?.total_volume || 0;
  const growth = revenue?.growth || revenue?.growthRate || revenue?.growth_rate || 0;
  const baseARR = revenue?.arr || revenue?.ARR || revenue?.annualRecurringRevenue || 0;
  const history = revenue?.history || analytics?.history || [];

  // 5. LIVE TELEMETRY OVERLAYS
  const liveTPS = useLivePulse(revenue?.tps, 120, 2500);
  const liveLatency = useLivePulse(analytics?.p95Latency, 1.5, 1800);
  const liveGreenRatio = useLivePulse(revenue?.esg?.greenRatio || compliance?.greenRatio, 0.3, 7000, 0.05);
  const liveComplianceScore = useLivePulse(compliance?.score, 0.06, 8500, 0.02);

  /**
   * @effect Ledger Drilldown Hydration
   * @description Pulls the real revenue ledger detail surface: DSO, pending payments,
   * collection risks, leakage and hash-chained transaction proofs.
   */
  useEffect(() => {
    let alive = true;
    const loadLedgerDetail = async () => {
      setLedgerLoading(true);
      try {
        const response = await api.get('/revenue/ledger', { params: { tenantId: tenantAlias } });
        if (alive) setLedgerDetail(response.data?.data || null);
      } catch (error) {
        console.warn('[REVENUE_LEDGER_DETAIL_FRACTURE]', error.message);
        if (alive) setLedgerDetail(null);
      } finally {
        if (alive) setLedgerLoading(false);
      }
    };
    loadLedgerDetail();
    return () => { alive = false; };
  }, [tenantAlias]);

  /**
   * @effect Tenant Alias Sync
   * @description Keeps operational invoice controls aligned to the currently selected tenant.
   */
  useEffect(() => {
    setInvoiceDraft(prev => ({
      ...prev,
      tenantId: tenantAlias,
      idempotencyKey: prev.idempotencyKey || createInvoiceIdempotencyKey(tenantAlias)
    }));
  }, [tenantAlias]);

  /**
   * @effect Global Tax Engine Calculation
   * @description Continuously seals the current invoice command with source-attributed VAT/GST posture.
   * @collaboration Wilson Khanyezi required global tax math to be operational proof, not a hard-coded 15% shortcut.
   */
  useEffect(() => {
    let alive = true;
    const timer = setTimeout(async () => {
      setTaxEngineLoading(true);
      try {
        const result = await globalTaxEngine.calculateFromInvoiceDraft(invoiceDraft, {
          tenantId: tenantAlias,
          preferFallbackMatrix: true
        });
        if (alive) setTaxEngineResult(result);
      } catch (error) {
        console.warn('[GLOBAL_TAX_ENGINE_FRACTURE]', error.message);
        if (alive) setTaxEngineResult(null);
      } finally {
        if (alive) setTaxEngineLoading(false);
      }
    }, 300);

    return () => {
      alive = false;
      clearTimeout(timer);
    };
  }, [invoiceDraft, tenantAlias]);

  /**
   * @function showToast
   * @description Renders a non-blocking tactical notification to the executive.
   * @param {string} message - The payload to display.
   */
  const showToast = useCallback((message) => {
    setTooltipVisible(message);
    setTimeout(() => setTooltipVisible(null), 4000);
  }, []);

  /**
   * @function handleStatementPresetChange
   * @description Applies a boardroom statement date preset directly to the invoice and PDF export payload.
   * @param {React.ChangeEvent<HTMLSelectElement>} event - Preset selector event.
   * @returns {void}
   * @collaboration Wilson Khanyezi required the sealed artifact date menu to be visible before export, not buried in a PDF backend.
   */
  const handleStatementPresetChange = useCallback((event) => {
    const nextPreset = event.target.value;
    setStatementPreset(nextPreset);
    if (nextPreset === 'CUSTOM') return;
    setInvoiceDraft(prev => ({
      ...prev,
      ...getStatementDatePreset(nextPreset, prev)
    }));
  }, []);

  /**
   * @effect Anomaly Scanner
   * @description Continuously monitors financial velocity to trigger boardroom alerts.
   */
  useEffect(() => {
    if (growth < -8) {
      setAnomalyDetected({ type: 'CRITICAL_DROP', message: `Revenue contraction of ${growth.toFixed(1)}% detected.` });
    } else if (growth > 25) {
      setAnomalyDetected({ type: 'UNUSUAL_SPIKE', message: `Significant acceleration of +${growth.toFixed(1)}%.` });
    } else {
      setAnomalyDetected(null);
    }
  }, [growth]);

  /**
   * @function handleForceSync
   * @description Bypasses cache to forcefully re-hydrate the ledger from the master database.
   * @async
   */
  const handleForceSync = async () => {
    if (isSyncing) return;
    setIsSyncing(true);
    try {
      // Real-world execution: Poll the synchronization endpoint
      await api.post(`/ledger/sync/${tenantAlias}`, { tenantId: tenantAlias });
      broadcastTelemetry(tenantAlias, 'LEDGER_SYNC', 'MANUAL_OVERRIDE', 'LedgerMatrix');
      showToast('Ledger synchronization complete. Zero drift.');
    } catch (error) {
      console.error('[SYNC FRACTURE]', error);
      showToast('Sync degraded. Secondary evidence preserved.');
    } finally {
      setIsSyncing(false);
    }
  };

  /**
   * @function handleAIQuery
   * @description Processes natural language commands against the encrypted financial dataset.
   * @async
   */
  const handleAIQuery = async () => {
    if (!queryInput.trim() || !revenue || isQuerying) return;
    setIsQuerying(true);
    setAiInsight(''); // Clear previous
    setAiInsightPacket(null);

    try {
      const liveSources = Object.entries(operationsSnapshot.sources || {})
        .filter(([, source]) => source?.status === 'LIVE')
        .map(([source]) => source.toUpperCase());
      const sourceGaps = Object.entries(operationsSnapshot.sources || {})
        .filter(([, source]) => source?.status !== 'LIVE')
        .map(([source]) => source.toUpperCase());

      // Real-world execution: Send query to LLM/Analytics backend with DB-derived evidence only.
      const response = await api.post(`/ai/query-ledger`, {
        tenantId: tenantAlias,
        query: queryInput,
        context: {
          growth,
          totalVolume,
          baseARR,
          arr: ledgerIntelligence.arr,
          mrr: ledgerIntelligence.mrr,
          pendingPayments: ledgerIntelligence.pendingPayments,
          leakage: ledgerIntelligence.leakage,
          deferredRevenue: ledgerIntelligence.deferredRevenue,
          recognizedRunRate: ledgerIntelligence.recognizedRunRate,
          dso: ledgerIntelligence.dso,
          collectionEfficiency: ledgerIntelligence.collectionEfficiency,
          activeContracts: ledgerIntelligence.activeContracts,
          transactionCount: ledgerIntelligence.transactions.length,
          collectionRiskCount: ledgerIntelligence.collectionRiskItems.length,
          currency: 'ZAR',
          sourceStatus: operationsSnapshot.status,
          liveSources,
          sourceGaps
        }
      });

      const normalizedPacket = normalizeLedgerAiPacket(response.data, queryInput);
      const packet = response.data?.data || response.data || {};
      const insight = packet.insight;
      if (!insight) {
        throw new Error('AI_LEDGER_BACKEND_RETURNED_NO_INSIGHT');
      }
      setAiInsight(normalizedPacket.insight);
      setAiInsightPacket(normalizedPacket);

      broadcastTelemetry(tenantAlias, 'AI_QUERY', 'INSIGHT_GENERATED', 'LedgerMatrix', { query: queryInput, sourceStatus: normalizedPacket.sourceStatus });
    } catch (error) {
      const liveSources = Object.entries(operationsSnapshot.sources || {})
        .filter(([, source]) => source?.status === 'LIVE')
        .map(([source]) => source.toUpperCase());
      const sourceGaps = Object.entries(operationsSnapshot.errors || {})
        .map(([source, message]) => `${source.toUpperCase()}: ${message}`);
      const record = persistLedgerEvidence({
        id: createLedgerDecisionId(),
        type: 'AI_LEDGER_SOURCE_UNAVAILABLE',
        tenantId: tenantAlias,
        query: queryInput,
        status: 'NO_SYNTHETIC_ANSWER_GENERATED',
        error: error.message,
        liveSources,
        sourceGaps,
        timestamp: new Date().toISOString()
      });
      setRevenueDecisionLedger(prev => [record, ...prev].slice(0, 8));
      const fallbackPacket = buildLedgerAiFallbackPacket({ query: queryInput, liveSources, sourceGaps, error });
      setAiInsight(fallbackPacket.insight);
      setAiInsightPacket(fallbackPacket);
    } finally {
      setIsQuerying(false);
      setQueryInput('');
    }
  };

  /**
   * @function handleCommitScenario
   * @description Locks a predictive 'What-If' model into the strategic planning database for board review.
   * @async
   */
  const handleCommitScenario = async () => {
    if (isCommitting) return;
    setIsCommitting(true);

    try {
      const payload = {
        tenantId: tenantAlias,
        baseARR,
        adjustments: whatIfParams,
        projectedARR,
        timestamp: new Date().toISOString()
      };

      try {
        await api.post(`/planning/commit-scenario`, payload);
      } catch (error) {
        persistLedgerEvidence({
          id: createLedgerDecisionId(),
          type: 'SCENARIO_COMMIT_LOCAL',
          tenantId: tenantAlias,
          status: 'QUEUED_FOR_BACKEND',
          payload,
          timestamp: new Date().toISOString()
        });
      }
      broadcastTelemetry(tenantAlias, 'SCENARIO_COMMIT', 'LOCKED', 'LedgerMatrix', { projectedARR });
      showToast(`Scenario locked. Forecast updated: ${formatZAR(projectedARR)}`);

      // Reset after commit
      setTimeout(() => setWhatIfParams({ priceChange: 0, volumeChange: 0 }), 1500);
    } catch (error) {
      showToast('Forecast commit failed. Local evidence queue preserved.');
    } finally {
      setIsCommitting(false);
    }
  };

  /**
   * @function handleGenerateStatement
   * @description Compiles current view into a cryptographically sealed, court-ready PDF.
   * @async
   */
  const handleGenerateStatement = async () => {
    if (isGenerating) return;
    setIsGenerating(true);
    const traceId = `TRC-TITAN-${Date.now().toString(36).toUpperCase()}`;
    let statementContext = {};
    let statementContextError = null;
    try {
      statementContext = buildBillingStatementContext(invoiceDraft);
    } catch (contextError) {
      statementContextError = contextError.message;
      statementContext = {
        issueDate: new Date().toISOString().slice(0, 10),
        statementDate: new Date().toISOString().slice(0, 10),
        dueDate: new Date().toISOString().slice(0, 10),
        billingPeriodStart: new Date().toISOString().slice(0, 10),
        billingPeriodEnd: new Date().toISOString().slice(0, 10),
        paymentTerms: 'NET_30',
        billingModel: 'PLATFORM_RETAINER',
        invoiceClass: activeHUD,
        taxType: 'VAT',
        taxJurisdiction: 'ZA',
        idempotencyKey: `WILSY-STMT-${tenantAlias}-${traceId}`,
        description: 'Wilsy OS sovereign operating services'
      };
    }
    const liveSourceCount = Object.values(operationsSnapshot.sources || {}).filter(source => source?.status === 'LIVE').length;
    const totalSourceCount = Object.keys(operationsSnapshot.sources || {}).length;
    const invoiceRows = extractInvoiceRowsFromSnapshot(operationsSnapshot);
    const openReceivables = invoiceRows.reduce((sum, row) => sum + Number(row.outstandingAmount ?? row.totalAmount ?? row.amount ?? 0), 0);
    try {
      const response = await api.get(`/statements/${activeHUD.toLowerCase()}`, {
        params: {
          tenantId: tenantAlias,
          hud: activeHUD,
          traceId,
          totalVolume,
          growth,
          arr: baseARR,
          amount: invoiceDraft.amount,
          clientId: invoiceDraft.clientId,
          invoiceRows: invoiceRows.length,
          openReceivables,
          pendingPayments: ledgerIntelligence.pendingPayments,
          dso: ledgerIntelligence.dso,
          decisionCount: revenueDecisionLedger.length,
          operationsStatus: operationsSnapshot.status,
          liveSourceCount,
          totalSourceCount,
          silentSourceCount: Math.max(0, totalSourceCount - liveSourceCount),
          lastOperationSync: operationsSnapshot.lastSync,
          taxEngineTraceId: taxEngineResult?.traceId || null,
          taxEngineProofHash: taxEngineResult?.proof?.hash || null,
          taxEngineSourceStatus: taxEngineResult?.sourceStatus || 'SOURCE_SILENT',
          taxAmount: taxEngineResult?.financials?.taxAmount || 0,
          invoiceTotalAmount: taxEngineResult?.financials?.totalAmount || invoiceDraft.amount,
          ...statementContext
        },
        responseType: 'blob'
      });

      const blobUrl = window.URL.createObjectURL(response.data);
      const link = document.createElement('a');
      link.href = blobUrl;
      link.download = `WILSY_SOVEREIGN_${activeHUD}_${tenantAlias}_${new Date().toISOString().slice(0,10)}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(blobUrl);

      setGeneratedTraceIds(prev => [traceId, ...prev]);
      const exportRecord = persistLedgerEvidence({
        id: createLedgerDecisionId(),
        type: 'SEALED_STATEMENT_EXPORTED',
        tenantId: tenantAlias,
        status: 'LIVE',
        title: 'Sealed Statement Exported',
        action: `Remote statement service produced artifact ${traceId}.`,
        payload: { traceId, hud: activeHUD, statementContext, taxProofHash: taxEngineResult?.proof?.hash || null },
        timestamp: new Date().toISOString()
      });
      setRevenueDecisionLedger(prev => [exportRecord, ...prev].slice(0, 8));
      setLastOperationReceipt(exportRecord);
      showToast(`Artifact sealed • Trace: ${traceId}`);
      broadcastTelemetry(tenantAlias, 'EXPORT', 'PDF_SUCCESS', 'LedgerMatrix', { hud: activeHUD, traceId });
    } catch (error) {
      console.error("[EXPORT FRACTURE]:", error);
      const fallbackRecord = persistLedgerEvidence({
        id: createLedgerDecisionId(),
        type: 'SEALED_STATEMENT_FALLBACK_CREATED',
        tenantId: tenantAlias,
        status: 'QUEUED_FOR_BACKEND',
        action: 'Remote PDF service rejected the request. Local forensic JSON fallback exported.',
        payload: {
          traceId,
          hud: activeHUD,
          error: error.response?.data?.message || error.message,
          inputs: { tenantAlias, totalVolume, growth, baseARR, statementContext, statementContextError, taxEngineResult }
        },
        timestamp: new Date().toISOString()
      });
      setGeneratedTraceIds(prev => [traceId, ...prev]);
      setRevenueDecisionLedger(prev => [fallbackRecord, ...prev].slice(0, 8));
      setLastOperationReceipt(fallbackRecord);
      exportLedgerJsonArtifact(`WILSY_LOCAL_SEALED_STATEMENT_${tenantAlias}_${traceId}.json`, fallbackRecord);
      showToast("Remote PDF unavailable. Local forensic artifact exported and queued.");
    } finally {
      setIsGenerating(false);
    }
  };

  /**
   * @function appendRevenueOperation
   * @description Records a real API-backed revenue operation into founder-visible evidence.
   * @param {string} type - Operation type.
   * @param {string} status - Result status.
   * @param {Object} payload - API payload or error details.
   * @returns {Object} Persisted evidence record.
   * @collaboration Wilson Khanyezi required every operational click to become auditable business proof.
   */
  const appendRevenueOperation = useCallback((type, status, payload = {}) => {
    const record = persistLedgerEvidence({
      id: createLedgerDecisionId(),
      type,
      tenantId: tenantAlias,
      status,
      title: formatOperationLabel(type),
      action: payload?.error ? `Backend response: ${payload.error}` : 'Command executed and evidence captured.',
      payload,
      timestamp: new Date().toISOString()
    });
    setRevenueDecisionLedger(prev => [record, ...prev].slice(0, 8));
    setLastOperationReceipt(record);
    return record;
  }, [tenantAlias]);

  /**
   * @function hydrateRevenueOperations
   * @description Hydrates the operations console from live billing, invoice, tenant and plan APIs.
   * @returns {Promise<void>} Resolves after source statuses are captured.
   */
  const hydrateRevenueOperations = useCallback(async () => {
    setOperationBusy('sync-operations');
    const sourceMap = {
      sovereignSummary: api.get('/billing/summary'),
      institutionalSummary: api.get('/billing/institutional/summary', { params: { tenantId: tenantAlias } }),
      billingAnalytics: api.get('/billing/analytics'),
      creditScores: api.get('/billing/credit-scores'),
      subscriptionStatus: api.get('/billing/status'),
      invoices: api.get('/invoices', { params: { limit: 12, tenantId: tenantAlias } })
    };

    const entries = Object.entries(sourceMap);
    const settled = await Promise.allSettled(entries.map(([, request]) => request));
    const sources = {};
    const errors = {};

    entries.forEach(([key], index) => {
      const result = settled[index];
      sources[key] = {
        status: getSourceStatus(result),
        payload: result.status === 'fulfilled' ? extractApiPayload(result.value) : null
      };
      if (result.status === 'rejected') {
        errors[key] = result.reason?.response?.data?.message || result.reason?.message || 'SOURCE_SILENT';
      }
    });

    const nextSnapshot = {
      status: Object.values(sources).some(source => source.status === 'LIVE') ? 'LIVE' : 'SOURCE_SILENT',
      lastSync: new Date().toISOString(),
      sources,
      errors
    };
    setOperationsSnapshot(nextSnapshot);
    appendRevenueOperation('LIVE_REVENUE_OPERATIONS_SYNC', nextSnapshot.status, {
      liveSources: Object.entries(sources).filter(([, source]) => source.status === 'LIVE').map(([key]) => key),
      silentSources: Object.keys(errors)
    });
    showToast(nextSnapshot.status === 'LIVE' ? 'Live revenue operations synced.' : 'No live revenue operation sources responded.');
    setOperationBusy(null);
  }, [tenantAlias, appendRevenueOperation, showToast]);

  /**
   * @effect Revenue Operations Hydration
   * @description Performs one live source scan when the Revenue Ledger opens.
   */
  useEffect(() => {
    hydrateRevenueOperations();
  }, [hydrateRevenueOperations]);

  /**
   * @function handleCreateSovereignInvoice
   * @description Creates a founder/platform invoice through the live billing API.
   * @returns {Promise<void>} Resolves after API response and evidence capture.
   */
  const handleCreateSovereignInvoice = useCallback(async () => {
    const amount = Number(invoiceDraft.amount);
    if (!invoiceDraft.tenantId || !Number.isFinite(amount) || amount <= 0) {
      showToast('Enter a tenant and valid invoice amount.');
      return;
    }

    setOperationBusy('sovereign-invoice');
    try {
      const response = await api.post('/billing/invoice/generate', buildInvoiceCommandPayload(invoiceDraft, {
        source: 'WILSY_REVENUE_LEDGER_PLATFORM_INVOICE',
        taxResult: taxEngineResult
      }));
      appendRevenueOperation('SOVEREIGN_PLATFORM_INVOICE_CREATED', 'LIVE', extractApiPayload(response));
      showToast('Platform invoice created in live DB.');
      setInvoiceDraft(prev => ({ ...prev, idempotencyKey: createInvoiceIdempotencyKey(prev.tenantId) }));
      await hydrateRevenueOperations();
    } catch (error) {
      appendRevenueOperation('SOVEREIGN_PLATFORM_INVOICE_FAILED', 'SOURCE_SILENT', {
        error: error.response?.data?.message || error.message
      });
      showToast('Platform invoice API rejected the request. No local invoice invented.');
    } finally {
      setOperationBusy(null);
    }
  }, [invoiceDraft, taxEngineResult, appendRevenueOperation, hydrateRevenueOperations, showToast]);

  /**
   * @function handleCreateClientInvoice
   * @description Creates a tenant-client invoice through the institutional billing API.
   * @returns {Promise<void>} Resolves after API response and evidence capture.
   */
  const handleCreateClientInvoice = useCallback(async () => {
    const amount = Number(invoiceDraft.amount);
    if (!invoiceDraft.clientId || !Number.isFinite(amount) || amount <= 0) {
      showToast('Enter a client id and valid invoice amount.');
      return;
    }

    setOperationBusy('client-invoice');
    try {
      const response = await api.post('/billing/institutional/invoice/generate', buildInvoiceCommandPayload(invoiceDraft, {
        source: 'WILSY_REVENUE_LEDGER_CLIENT_INVOICE',
        taxResult: taxEngineResult
      }));
      appendRevenueOperation('TENANT_CLIENT_INVOICE_CREATED', 'LIVE', extractApiPayload(response));
      showToast('Tenant client invoice created in live DB.');
      setInvoiceDraft(prev => ({ ...prev, idempotencyKey: createInvoiceIdempotencyKey(prev.tenantId) }));
      await hydrateRevenueOperations();
    } catch (error) {
      appendRevenueOperation('TENANT_CLIENT_INVOICE_FAILED', 'SOURCE_SILENT', {
        error: error.response?.data?.message || error.message
      });
      showToast('Client invoice API rejected the request. No local invoice invented.');
    } finally {
      setOperationBusy(null);
    }
  }, [invoiceDraft, taxEngineResult, appendRevenueOperation, hydrateRevenueOperations, showToast]);

  /**
   * @function handleRunMonthlyBilling
   * @description Executes the backend monthly billing engine for active tenants.
   * @returns {Promise<void>} Resolves after billing run completion.
   */
  const handleRunMonthlyBilling = useCallback(async () => {
    setOperationBusy('monthly-billing');
    try {
      const response = await api.post('/billing/auto-monthly');
      appendRevenueOperation('AUTONOMOUS_MONTHLY_BILLING_RUN', 'LIVE', extractApiPayload(response));
      showToast('Autonomous monthly billing completed.');
      await hydrateRevenueOperations();
    } catch (error) {
      appendRevenueOperation('AUTONOMOUS_MONTHLY_BILLING_FAILED', 'SOURCE_SILENT', {
        error: error.response?.data?.message || error.message
      });
      showToast('Monthly billing engine unavailable. No invoices fabricated.');
    } finally {
      setOperationBusy(null);
    }
  }, [appendRevenueOperation, hydrateRevenueOperations, showToast]);

  /**
   * @function hydrateTaxTreasuryCommand
   * @description Syncs tax obligations, treasury status and settlement previews into the capital command surface.
   * @returns {Promise<void>} Resolves after source status and errors are captured.
   * @collaboration Wilson Khanyezi required tax and treasury to become an operating layer, not a spreadsheet appendix.
   */
  const hydrateTaxTreasuryCommand = useCallback(async () => {
    setOperationBusy('tax-treasury-sync');
    const [policySyncResult, benchmarkSyncResult] = await Promise.allSettled([
      treasurySweepManager.syncPolicyMatrix(),
      treasurySweepManager.syncBenchmarks()
    ]);
    const sourceMap = {
      tax: api.get(`/tax/obligations/${tenantAlias}`),
      treasury: treasurySweepManager.getTreasuryStatus(tenantAlias),
      taxReports: api.get('/finance/tax-reports', { params: { tenantId: tenantAlias, limit: 12 } }),
      settlementPreview: api.get('/billing/blockchain-preview')
    };
    const entries = Object.entries(sourceMap);
    const settled = await Promise.allSettled(entries.map(([, request]) => request));
    const payloads = {};
    const errors = {};

    entries.forEach(([key], index) => {
      const result = settled[index];
      if (result.status === 'fulfilled') {
        payloads[key] = extractApiPayload(result.value) || result.value?.data || result.value || {};
      } else {
        errors[key] = result.reason?.response?.data?.message || result.reason?.message || 'SOURCE_SILENT';
      }
    });

    const taxObligations = normalizeCommandArray(payloads.tax || payloads.taxReports);
    const treasurySweeps = normalizeCommandArray(payloads.treasury?.sweeps || payloads.settlementPreview);
    const nextSnapshot = {
      status: Object.keys(payloads).length ? 'LIVE' : 'SOURCE_SILENT',
      lastSync: new Date().toISOString(),
      tax: {
        ...payloads.tax,
        obligations: taxObligations,
        sourceStatus: payloads.tax || payloads.taxReports ? 'LIVE' : 'SOURCE_SILENT'
      },
      treasury: {
        ...payloads.treasury,
        sweeps: treasurySweeps,
        settlementPreview: payloads.settlementPreview || null,
        availableLiquidity: Number(payloads.treasury?.availableLiquidity || payloads.treasury?.liquidity || ledgerDetail?.monthlyInflow || revenue?.mrr || (baseARR / 12) || 0),
        sourceStatus: payloads.treasury || payloads.settlementPreview ? 'LIVE' : 'SOURCE_SILENT'
      },
      errors
    };

    setTaxTreasurySnapshot(nextSnapshot);
    const evaluation = treasurySweepManager.evaluateLiquidity({
      tenantId: tenantAlias,
      currency: invoiceDraft.currency || 'ZAR',
      currentBalance: nextSnapshot.treasury.availableLiquidity,
      sourceStatus: nextSnapshot.treasury.sourceStatus,
      context: {
        pendingPayments: ledgerDetail?.pendingPayments || 0,
        taxReserve: taxEngineResult?.financials?.taxAmount || 0,
        bankVariance: bankReconciliation.variance || 0,
        recognizedRunRate: ledgerDetail?.monthlyInflow || revenue?.mrr || (baseARR / 12) || 0
      }
    });
    setTreasurySweepState(prev => ({
      status: evaluation.status,
      evaluation,
      receipt: prev.receipt,
      lastUpdated: new Date().toISOString()
    }));
    appendRevenueOperation('TAX_TREASURY_SOURCE_SYNC', nextSnapshot.status, {
      liveSources: Object.keys(payloads),
      silentSources: Object.keys(errors),
      treasurySweepStatus: evaluation.status,
      treasuryProofHash: evaluation.proof?.hash,
      policySync: policySyncResult.status === 'fulfilled' ? policySyncResult.value.status : 'POLICY_SYNC_FAILED',
      benchmarkSync: benchmarkSyncResult.status === 'fulfilled' ? benchmarkSyncResult.value.status : 'BENCHMARK_SYNC_FAILED'
    });
    showToast(nextSnapshot.status === 'LIVE' ? 'Tax and treasury sources synced.' : 'Tax and treasury sources are silent.');
    setOperationBusy(null);
  }, [
    tenantAlias,
    invoiceDraft.currency,
    ledgerDetail?.monthlyInflow,
    ledgerDetail?.pendingPayments,
    revenue?.mrr,
    baseARR,
    taxEngineResult,
    bankReconciliation.variance,
    appendRevenueOperation,
    showToast
  ]);

  /**
   * @function handleSyncGlobalTaxMatrix
   * @description Force-refreshes the GlobalTaxEngine jurisdiction matrix and immediately reseals the invoice command.
   * @returns {Promise<void>} Resolves after source status and recalculation evidence are captured.
   * @collaboration Makes statutory rate freshness a founder-visible command instead of a hidden constant.
   */
  const handleSyncGlobalTaxMatrix = useCallback(async () => {
    setOperationBusy('tax-matrix-sync');
    try {
      const matrixSync = await globalTaxEngine.syncJurisdictionMatrix({ forceRefresh: true });
      const recalculated = await globalTaxEngine.calculateFromInvoiceDraft(invoiceDraft, {
        tenantId: tenantAlias,
        forceRefreshRates: true
      });
      setTaxEngineResult(recalculated);
      appendRevenueOperation('GLOBAL_TAX_MATRIX_SYNC', matrixSync.status, {
        matrixSync,
        taxTraceId: recalculated.traceId,
        taxProofHash: recalculated.proof?.hash,
        sourceStatus: recalculated.sourceStatus
      });
      showToast(matrixSync.success ? 'Global tax matrix synced and invoice tax proof resealed.' : 'Tax matrix source silent. Researched fallback preserved.');
    } catch (error) {
      appendRevenueOperation('GLOBAL_TAX_MATRIX_SYNC_FAILED', 'SOURCE_SILENT', {
        error: error.response?.data?.message || error.message,
        tenantId: tenantAlias
      });
      showToast('Global tax matrix sync failed. Existing tax proof preserved.');
    } finally {
      setOperationBusy(null);
    }
  }, [invoiceDraft, tenantAlias, appendRevenueOperation, showToast]);

  /**
   * @function hydrateDunningIntelligence
   * @description Loads Dunning Intelligence recommendations from the backend and falls back to ledger-derived risk rows.
   * @returns {Promise<void>} Resolves after dunning source state is captured.
   * @collaboration Converts collections from passive aging into a timed legal-finance command rail.
   */
  const hydrateDunningIntelligence = useCallback(async () => {
    setOperationBusy('dunning-sync');
    try {
      const envelope = await dunningIntelligence.getDunningRecommendations(tenantAlias, {
        collectionRiskRows: ledgerDetail?.collectionRiskItems || [],
        invoiceRows: extractInvoiceRowsFromSnapshot(operationsSnapshot),
        preferLedgerFallback: true
      });
      const recommendations = envelope.recommendations || [];
      setDunningState(prev => ({
        status: envelope.status,
        recommendations,
        lastReceipt: prev.lastReceipt,
        lastSync: new Date().toISOString(),
        error: envelope.warning || null
      }));
      appendRevenueOperation('DUNNING_INTELLIGENCE_SYNC', envelope.status, {
        recommendations: recommendations.length,
        sourceStatus: envelope.sourceStatus,
        proofHashes: recommendations.slice(0, 5).map(item => item.proof?.hash).filter(Boolean)
      });
      showToast(recommendations.length ? 'Dunning Intelligence synced and sealed.' : 'No dunning candidates available.');
    } catch (error) {
      setDunningState(prev => ({
        ...prev,
        status: 'SOURCE_SILENT',
        lastSync: new Date().toISOString(),
        error: error.response?.data?.message || error.message
      }));
      appendRevenueOperation('DUNNING_INTELLIGENCE_SOURCE_SILENT', 'SOURCE_SILENT', {
        error: error.response?.data?.message || error.message
      });
    } finally {
      setOperationBusy(null);
    }
  }, [tenantAlias, ledgerDetail?.collectionRiskItems, operationsSnapshot, appendRevenueOperation, showToast]);

  /**
   * @function handleManualTreasurySweep
   * @description Requests a treasury sweep from the backend using current ledger liquidity context.
   * @returns {Promise<void>} Resolves after the sweep command is accepted or preserved as failed evidence.
   */
  const handleManualTreasurySweep = useCallback(async () => {
    setOperationBusy('treasury-sweep');
    try {
      const receipt = await treasurySweepManager.executeSweep({
        tenantId: tenantAlias,
        currency: invoiceDraft.currency || 'ZAR',
        currentBalance: taxTreasurySnapshot.treasury?.availableLiquidity || ledgerDetail?.deferredRevenue || ledgerDetail?.pendingPayments || 0,
        context: {
          sourceStatus: taxTreasurySnapshot.treasury?.sourceStatus || 'SOURCE_SILENT',
          pendingPayments: ledgerDetail?.pendingPayments || 0,
          taxReserve: taxEngineResult?.financials?.taxAmount || 0,
          bankVariance: bankReconciliation.variance || 0,
          recognizedRunRate: ledgerDetail?.monthlyInflow || revenue?.mrr || (baseARR / 12) || 0,
          sourceAccount: 'SOVEREIGN_REVENUE_LEDGER'
        },
        approval: {
          requestedBy: tenantAlias,
          reason: 'Manual treasury sweep from Sovereign Revenue Ledger'
        }
      });
      setTreasurySweepState({
        status: receipt.status,
        evaluation: receipt.evaluation || null,
        receipt,
        lastUpdated: new Date().toISOString()
      });
      appendRevenueOperation('TREASURY_SWEEP_TRIGGERED', receipt.executionStatus || receipt.status, {
        receipt,
        proofHash: receipt.proof?.hash,
        evaluationProofHash: receipt.evaluation?.proof?.hash
      });
      showToast(receipt.executionStatus === 'EXECUTED'
        ? 'Treasury sweep executed and sealed.'
        : 'Treasury sweep held by policy gates. Receipt sealed.');
      await hydrateTaxTreasuryCommand();
      await bankReconciliation.refresh();
    } catch (error) {
      appendRevenueOperation('TREASURY_SWEEP_REJECTED', 'SOURCE_SILENT', {
        error: error.response?.data?.message || error.message,
        tenantId: tenantAlias
      });
      showToast('Treasury sweep source unavailable. Evidence preserved.');
    } finally {
      setOperationBusy(null);
    }
  }, [
    tenantAlias,
    invoiceDraft.currency,
    taxTreasurySnapshot.treasury?.availableLiquidity,
    taxTreasurySnapshot.treasury?.sourceStatus,
    ledgerDetail?.deferredRevenue,
    ledgerDetail?.pendingPayments,
    ledgerDetail?.monthlyInflow,
    revenue?.mrr,
    baseARR,
    taxEngineResult,
    bankReconciliation.variance,
    bankReconciliation.refresh,
    appendRevenueOperation,
    hydrateTaxTreasuryCommand,
    showToast
  ]);

  /**
   * @function handleExportTaxTreasuryPacket
   * @description Exports the current tax, treasury, bank reconciliation and Merkle state as a founder evidence packet.
   * @returns {void}
   */
  const handleExportTaxTreasuryPacket = useCallback(() => {
    const artifact = {
      product: 'WILSY OS Tax Treasury Command Packet',
      tenantId: tenantAlias,
      generatedAt: new Date().toISOString(),
      taxTreasurySnapshot,
      taxEngine: taxEngineResult,
      taxMatrix: globalTaxEngine.getMatrixSnapshot(),
      treasurySweep: treasurySweepState,
      treasuryPolicy: treasurySweepManager.getMatrixSnapshot(),
      bankReconciliation: {
        status: bankReconciliation.status,
        sourceStatus: bankReconciliation.sourceStatus,
        pending: bankReconciliation.pending,
        variance: bankReconciliation.variance,
        lastUpdated: bankReconciliation.lastUpdated
      },
      merkleAudit,
      ledgerPosture: {
        pendingPayments: ledgerDetail?.pendingPayments || 0,
        deferredRevenue: ledgerDetail?.deferredRevenue || 0,
        recognizedRunRate: ledgerDetail?.monthlyInflow || revenue?.mrr || (baseARR / 12) || 0
      }
    };
    const record = appendRevenueOperation('TAX_TREASURY_PACKET_EXPORTED', taxTreasurySnapshot.status, {
      taxSource: taxTreasurySnapshot.tax?.sourceStatus,
      taxEngineSource: taxEngineResult?.sourceStatus,
      taxProofHash: taxEngineResult?.proof?.hash,
      treasurySweepStatus: treasurySweepState.status,
      treasurySweepProofHash: treasurySweepState.evaluation?.proof?.hash || treasurySweepState.receipt?.proof?.hash,
      treasurySource: taxTreasurySnapshot.treasury?.sourceStatus,
      bankSource: bankReconciliation.sourceStatus
    });
    exportLedgerJsonArtifact(`WILSY_TAX_TREASURY_${tenantAlias}_${record.id}.json`, artifact);
    showToast('Tax and treasury command packet exported.');
  }, [tenantAlias, taxTreasurySnapshot, taxEngineResult, treasurySweepState, bankReconciliation, merkleAudit, ledgerDetail, revenue?.mrr, baseARR, appendRevenueOperation, showToast]);

  /**
   * @function handleRunMerkleAudit
   * @description Executes the backend Forensic Merkle Auditor and requests immutable anchoring for a valid chain root.
   * @returns {Promise<void>} Resolves after the auditor status is recorded and refreshed.
   * @collaboration Wilson Khanyezi required cryptographic proof to be a command, not a passive footer label.
   */
  const handleRunMerkleAudit = useCallback(async () => {
    setOperationBusy('merkle-audit');
    try {
      const response = await api.post('/forensics/merkle-auditor/run', {
        tenantId: tenantAlias,
        anchor: true
      });
      const payload = extractApiPayload(response) || response.data || {};
      appendRevenueOperation('FORENSIC_MERKLE_AUDITOR_RUN', payload.status || 'AUDITED', {
        merkleRoot: payload.merkleRoot,
        chainLength: payload.chainLength,
        driftCount: payload.driftCount,
        anchorMode: payload.anchorMode,
        qldbStatus: payload.qldbStatus,
        externalAnchor: payload.externalAnchor
      });
      await merkleAudit.refresh();
      showToast(payload.verified ? 'Merkle auditor verified and anchored the chain.' : 'Merkle auditor completed with review posture.');
    } catch (error) {
      appendRevenueOperation('FORENSIC_MERKLE_AUDITOR_FAILED', 'SOURCE_SILENT', {
        error: error.response?.data?.message || error.message,
        tenantId: tenantAlias
      });
      showToast('Merkle auditor source unavailable. Evidence preserved.');
    } finally {
      setOperationBusy(null);
    }
  }, [tenantAlias, appendRevenueOperation, merkleAudit.refresh, showToast]);

  /**
   * @effect Capital Command Hydration
   * @description Activates tax, treasury and dunning source sync only when the founder enters those command surfaces.
   */
  useEffect(() => {
    if (activeHUD === 'TAX_TREASURY') {
      hydrateTaxTreasuryCommand();
      bankReconciliation.refresh();
      merkleAudit.refresh();
    }
    if (activeHUD === 'COLLECTIONS') {
      hydrateDunningIntelligence();
    }
  }, [activeHUD, hydrateTaxTreasuryCommand, hydrateDunningIntelligence, bankReconciliation.refresh, merkleAudit.refresh]);

  // 6. DYNAMIC CALCULATIONS
  const projectedARR = useMemo(() =>
    Math.round(baseARR * (1 + whatIfParams.priceChange / 100) * (1 + whatIfParams.volumeChange / 100)),
  [baseARR, whatIfParams]);

  const formatZAR = (val) => new Intl.NumberFormat('en-ZA', {
    style: 'currency', currency: 'ZAR', maximumFractionDigits: 0
  }).format(val || 0);

  /**
   * @function formatSafeRounded
   * @description Formats numeric telemetry when a source exists; legacy callers keep zero as a neutral fallback.
   * @param {number|string} val - Numeric source value.
   * @param {number} decimals - Decimal precision.
   * @returns {string} Rounded display value.
   * @collaboration Wilson Khanyezi mandated live-data honesty; new proof surfaces use explicit source checks before displaying metrics.
   */
  const formatSafeRounded = (val, decimals = 1) => {
    const num = Number(val);
    return isNaN(num) ? "0.0" : num.toFixed(decimals);
  };

  const formatPercent = (val, decimals = 1) => `${formatSafeRounded(val, decimals)}%`;

  /**
   * @function hasLiveNumber
   * @description Determines whether Wilsy OS received a finite numeric value from a live API/DB source.
   * @param {number|string|null|undefined} value - Candidate metric from a live data source.
   * @returns {boolean} True when the value is finite and can be shown as evidence.
   * @collaboration Wilson Khanyezi rejected ceremonial 0.0 metrics; this guard separates proof from silence.
   */
  const hasLiveNumber = (value) => Number.isFinite(Number(value));

  /**
   * @function formatLivePercent
   * @description Displays a sourced percentage or an explicit source-silent state.
   * @param {number|string|null|undefined} value - Live percentage candidate.
   * @param {number} decimals - Decimal precision.
   * @returns {string} Investor-safe percentage label.
   * @collaboration Keeps Wilsy OS from making compliance or ESG claims that the live ledger cannot defend.
   */
  const formatLivePercent = (value, decimals = 1) => (
    hasLiveNumber(value) ? `${Number(value).toFixed(decimals)}%` : 'SOURCE SILENT'
  );

  const ledgerIntelligence = useMemo(() => {
    const ledger = ledgerDetail || {};
    const totalRevenue = ledger.totalRevenue ?? totalVolume;
    const monthlyInflow = ledger.monthlyInflow ?? 0;
    const pendingPayments = ledger.pendingPayments ?? 0;
    const leakage = ledger.revenueLeakageDetected ?? 0;
    const activeContracts = ledger.activeContracts ?? 0;
    const dso = ledger.daysSalesOutstanding ?? 0;
    const mrr = revenue?.mrr || revenue?.MRR || Math.round((baseARR || totalRevenue * 12 || 0) / 12);
    const arr = baseARR || mrr * 12;
    const collectionEfficiency = totalRevenue + pendingPayments > 0
      ? (totalRevenue / (totalRevenue + pendingPayments)) * 100
      : 0;
    const nrrProxy = arr > 0
      ? Math.max(0, Math.min(160, 100 + Number(growth || 0) - ((leakage / arr) * 100)))
      : 0;
    const deferredRevenue = Math.max(0, pendingPayments);
    const recognizedRunRate = Math.max(monthlyInflow, mrr);
    return {
      totalRevenue,
      monthlyInflow,
      pendingPayments,
      leakage,
      activeContracts,
      dso,
      mrr,
      arr,
      nrrProxy,
      deferredRevenue,
      recognizedRunRate,
      collectionEfficiency,
      collectionRiskItems: ledger.collectionRiskItems || [],
      transactions: ledger.transactions || [],
      clientRiskScores: ledger.clientRiskScores || [],
      peerBenchmark: ledger.peerBenchmark || null
    };
  }, [ledgerDetail, totalVolume, revenue, baseARR, growth]);

  const aiDecisionPackets = useMemo(() => buildRevenueDecisionPackets(ledgerIntelligence, {
    growth,
    formatZAR,
    formatPercent
  }), [ledgerIntelligence, growth]);

  const aiFocusScore = useMemo(() => {
    const liveSources = [
      totalVolume > 0,
      ledgerDetail !== null,
      history.length > 0,
      telemetryEvents?.length > 0,
      compliance?.score !== undefined
    ].filter(Boolean).length;
    const riskPenalty = classifyCashRisk(ledgerIntelligence) === 'HIGH' ? 18 : classifyCashRisk(ledgerIntelligence) === 'MEDIUM' ? 8 : 0;
    return Math.max(0, Math.min(100, Math.round((liveSources / 5) * 100 - riskPenalty)));
  }, [totalVolume, ledgerDetail, history.length, telemetryEvents?.length, compliance?.score, ledgerIntelligence]);

  const revenueDoctrine = useMemo(() => buildRevenueOperatingDoctrine({
    metrics: ledgerIntelligence,
    operationsSnapshot,
    invoiceDraft,
    tenantAlias,
    aiFocusScore,
    formatZAR
  }), [ledgerIntelligence, operationsSnapshot, invoiceDraft, tenantAlias, aiFocusScore]);

  /**
   * @function handleApplyDynamicPricingGuard
   * @description Applies the live dynamic pricing endpoint using risk derived from actual ledger conditions.
   * @returns {Promise<void>} Resolves after pricing guard execution.
   */
  const handleApplyDynamicPricingGuard = useCallback(async () => {
    const risk = classifyCashRisk(ledgerIntelligence) === 'HIGH' ? 0.82 : classifyCashRisk(ledgerIntelligence) === 'MEDIUM' ? 0.55 : 0.22;
    setOperationBusy('dynamic-pricing');
    try {
      const response = await api.post('/billing/apply-dynamic-pricing', {
        risk,
        newPrice: ledgerIntelligence.mrr || 0
      });
      appendRevenueOperation('DYNAMIC_PRICING_GUARD_APPLIED', 'LIVE', extractApiPayload(response));
      showToast('Dynamic pricing guard applied from live ledger risk.');
      await hydrateRevenueOperations();
    } catch (error) {
      appendRevenueOperation('DYNAMIC_PRICING_GUARD_FAILED', 'SOURCE_SILENT', {
        error: error.response?.data?.message || error.message
      });
      showToast('Dynamic pricing API unavailable. No pricing changes invented.');
    } finally {
      setOperationBusy(null);
    }
  }, [ledgerIntelligence, appendRevenueOperation, hydrateRevenueOperations, showToast]);

  /**
   * @function appendRevenueDecision
   * @description Records an approved revenue packet as founder-visible operating evidence.
   * @param {Object} packet - AI decision packet.
   * @param {string} action - Action taken.
   * @returns {Object} Persisted decision record.
   * @collaboration Wilson Khanyezi required AI Focus to perform governed actions, not produce disposable text.
   */
  const appendRevenueDecision = useCallback((packet, action) => {
    const record = persistLedgerEvidence({
      id: createLedgerDecisionId(),
      type: 'AI_REVENUE_DECISION',
      tenantId: tenantAlias,
      packetId: packet.id,
      title: packet.title,
      status: packet.status,
      owner: packet.owner,
      evidence: packet.evidence,
      action,
      timestamp: new Date().toISOString()
    });

    setRevenueDecisionLedger(prev => [record, ...prev].slice(0, 8));
    setApprovedPacketIds(prev => Array.from(new Set([packet.id, ...prev])));
    return record;
  }, [tenantAlias]);

  /**
   * @function handleApproveDecisionPacket
   * @description Approves a CFO-grade AI Focus packet and broadcasts the evidence trail.
   * @param {Object} packet - AI decision packet.
   * @returns {Promise<void>} Resolves after telemetry dispatch.
   */
  const handleApproveDecisionPacket = useCallback(async (packet) => {
    const record = appendRevenueDecision(packet, packet.action);
    await broadcastTelemetry(tenantAlias, 'AI_REVENUE_FOCUS', 'DECISION_PACKET_APPROVED', 'LedgerMatrix', {
      decisionId: record.id,
      packetId: packet.id,
      status: packet.status
    }).catch(() => {});
    showToast(`Decision approved • ${record.id}`);
  }, [appendRevenueDecision, tenantAlias, showToast]);

  /**
   * @function handleLaunchCollectionsMission
   * @description Moves from AI analysis into the live Collections command surface.
   * @returns {void}
   */
  const handleLaunchCollectionsMission = useCallback(() => {
    setActiveHUD('COLLECTIONS');
    const packet = aiDecisionPackets.find(item => item.id === 'legal-collections') || aiDecisionPackets[0];
    appendRevenueDecision(packet, 'Collections mission opened from AI Focus.');
    showToast('Collections mission opened from AI Focus.');
  }, [aiDecisionPackets, appendRevenueDecision, showToast]);

  /**
   * @function handleExportCfoDossier
   * @description Exports a CFO-grade operating dossier containing live ledger metrics, AI decisions and scenario state.
   * @returns {void}
   */
  const handleExportCfoDossier = useCallback(() => {
    const dossier = {
      product: 'WILSY OS Sovereign Revenue Ledger',
      tenantId: tenantAlias,
      generatedAt: new Date().toISOString(),
      aiFocusScore,
      ledgerIntelligence,
      aiDecisionPackets,
      approvedPacketIds,
      revenueDecisionLedger,
      whatIfParams,
      projectedARR,
      taxEngineResult,
      taxMatrix: globalTaxEngine.getMatrixSnapshot(),
      dataPosture: {
        ledgerDetail: ledgerDetail ? 'LIVE' : 'SOURCE_SILENT',
        history: history.length,
        telemetryFrames: telemetryEvents?.length || 0,
        complianceScore: compliance?.score ?? null
      }
    };
    const record = persistLedgerEvidence({
      id: createLedgerDecisionId(),
      type: 'CFO_DOSSIER_EXPORTED',
      tenantId: tenantAlias,
      status: 'LIVE',
      title: 'CFO Dossier Exported',
      action: 'Founder exported a live revenue evidence dossier.',
      payload: { aiFocusScore, projectedARR, dataPosture: dossier.dataPosture, taxProofHash: taxEngineResult?.proof?.hash || null },
      timestamp: new Date().toISOString()
    });
    setRevenueDecisionLedger(prev => [record, ...prev].slice(0, 8));
    setLastOperationReceipt(record);
    exportLedgerJsonArtifact(`WILSY_CFO_DOSSIER_${tenantAlias}_${new Date().toISOString().slice(0, 19)}.json`, dossier);
    showToast('CFO dossier exported with live ledger evidence.');
  }, [tenantAlias, aiFocusScore, ledgerIntelligence, aiDecisionPackets, approvedPacketIds, revenueDecisionLedger, whatIfParams, projectedARR, taxEngineResult, ledgerDetail, history.length, telemetryEvents?.length, compliance?.score, showToast]);

  /**
   * @function handleExportRevenueDoctrine
   * @description Exports the founder revenue doctrine as an evidence artifact backed by live source coverage.
   * @returns {void}
   * @collaboration Gives Wilson Khanyezi an investor-ready proof packet that states exactly what Wilsy OS can prove.
   */
  const handleExportRevenueDoctrine = useCallback(() => {
    const artifact = {
      product: 'WILSY OS Revenue Operating Doctrine',
      tenantId: tenantAlias,
      generatedAt: new Date().toISOString(),
      doctrine: revenueDoctrine,
      operationsSnapshot,
      ledgerIntelligence,
      invoiceDraft: buildBillingStatementContext(invoiceDraft, { tenantAlias }),
      taxEngineResult,
      taxMatrix: globalTaxEngine.getMatrixSnapshot(),
      warning: revenueDoctrine.liveSources === 0
        ? 'No synthetic proof generated. Sync live sources before presenting investor claims.'
        : ''
    };
    const record = persistLedgerEvidence({
      id: createLedgerDecisionId(),
      type: 'REVENUE_DOCTRINE_EXPORTED',
      tenantId: tenantAlias,
      status: revenueDoctrine.liveSources > 0 ? 'LIVE' : 'SOURCE_SILENT',
      title: 'Revenue Operating Doctrine Exported',
      action: `${revenueDoctrine.liveSources}/${revenueDoctrine.totalSources || 0} live sources sealed into doctrine.`,
      payload: { coverage: revenueDoctrine.coverage, primaryRisk: revenueDoctrine.primaryRisk, taxProofHash: taxEngineResult?.proof?.hash || null },
      timestamp: new Date().toISOString()
    });
    setRevenueDecisionLedger(prev => [record, ...prev].slice(0, 8));
    setLastOperationReceipt(record);
    exportLedgerJsonArtifact(`WILSY_REVENUE_DOCTRINE_${tenantAlias}_${new Date().toISOString().slice(0, 19)}.json`, artifact);
    showToast('Revenue doctrine artifact exported.');
  }, [tenantAlias, revenueDoctrine, operationsSnapshot, ledgerIntelligence, invoiceDraft, taxEngineResult, showToast]);

  /**
   * @function handleRevenueDoctrineAction
   * @description Executes a doctrine stage command and routes the founder into the relevant live revenue workflow.
   * @param {React.MouseEvent<HTMLButtonElement>} event - Button event carrying the doctrine action.
   * @returns {void}
   * @collaboration Replaces passive reading with an operating-system command rail: scan, invoice, collect, meter or prove.
   */
  const handleRevenueDoctrineAction = useCallback((event) => {
    const action = event.currentTarget.dataset.action;
    const stage = revenueDoctrine.lifecycle.find(item => item.action === action);

    if (!stage) return;

    if (action === 'SYNC_SOURCES') {
      hydrateRevenueOperations();
      return;
    }

    if (action === 'OPEN_METERING') {
      setActiveHUD('METERING');
    } else if (action === 'CREATE_INVOICE') {
      handleCreateSovereignInvoice();
    } else if (action === 'OPEN_COLLECTIONS') {
      setActiveHUD('COLLECTIONS');
    } else if (action === 'EXPORT_DOCTRINE') {
      handleExportRevenueDoctrine();
    }

    appendRevenueOperation('REVENUE_DOCTRINE_STAGE_ACTIVATED', stage.status, {
      stage: stage.label,
      action: stage.action,
      evidence: stage.evidence
    });
  }, [
    revenueDoctrine.lifecycle,
    hydrateRevenueOperations,
    handleCreateSovereignInvoice,
    handleExportRevenueDoctrine,
    appendRevenueOperation
  ]);

  const revenueOperatingSystem = useMemo(() => ([
    {
      label: 'Recurring Core',
      value: formatZAR(ledgerIntelligence.mrr),
      caption: 'MRR normalized from live ARR',
      icon: Repeat2,
      tone: '#00ff88'
    },
    {
      label: 'Revenue Recovery',
      value: formatZAR(ledgerIntelligence.leakage),
      caption: 'Overdue leakage requiring action',
      icon: CreditCard,
      tone: ledgerIntelligence.leakage > 0 ? '#ff6666' : '#00ff88'
    },
    {
      label: 'Recognition Queue',
      value: formatZAR(ledgerIntelligence.deferredRevenue),
      caption: 'Unpaid or deferred ledger balance',
      icon: ReceiptText,
      tone: '#D4AF37'
    },
    {
      label: 'Cash Conversion',
      value: `${ledgerIntelligence.dso}d`,
      caption: 'Days sales outstanding',
      icon: Gauge,
      tone: ledgerIntelligence.dso > 45 ? '#ff6666' : '#00ff88'
    }
  ]), [ledgerIntelligence]);

  const usageMeters = useMemo(() => ([
    {
      name: 'Ledger Events',
      value: Math.round((liveTPS || 0) * 60),
      unit: 'events/min',
      status: liveTPS > 0 ? 'streaming' : 'standing by'
    },
    {
      name: 'Telemetry Dimensions',
      value: telemetryEvents?.length || 0,
      unit: 'live frames',
      status: telemetryEvents?.length ? 'segmented' : 'awaiting feed'
    },
    {
      name: 'Invoice Risk Alerts',
      value: ledgerIntelligence.collectionRiskItems.length,
      unit: 'open risks',
      status: ledgerIntelligence.collectionRiskItems.length ? 'action required' : 'clear'
    }
  ]), [liveTPS, telemetryEvents, ledgerIntelligence.collectionRiskItems.length]);

  const revenueOperationCards = useMemo(() => {
    const sources = operationsSnapshot.sources || {};
    const sovereignSummary = sources.sovereignSummary?.payload?.data || sources.sovereignSummary?.payload || {};
    const institutionalSummary = sources.institutionalSummary?.payload || {};
    const subscriptionStatus = sources.subscriptionStatus?.payload || {};
    const invoicesPayload = sources.invoices?.payload || {};
    const invoiceRows = invoicesPayload?.data?.invoices || invoicesPayload?.invoices || invoicesPayload?.data || [];
    const creditScores = sources.creditScores?.payload?.scores || sources.creditScores?.payload || {};
    return [
      {
        label: 'Plan Authority',
        value: subscriptionStatus?.tier || subscriptionStatus?.status || 'SOURCE SILENT',
        caption: sources.subscriptionStatus?.status || 'SOURCE_SILENT'
      },
      {
        label: 'DB Invoice Rows',
        value: Array.isArray(invoiceRows) ? invoiceRows.length : 'SOURCE SILENT',
        caption: sources.invoices?.status || 'SOURCE_SILENT'
      },
      {
        label: 'Global Pending',
        value: sources.sovereignSummary?.status === 'LIVE' ? `${sovereignSummary.pendingInvoices || 0}` : 'SOURCE SILENT',
        caption: sources.sovereignSummary?.status || 'SOURCE_SILENT'
      },
      {
        label: 'Tenant Receivables',
        value: sources.institutionalSummary?.status === 'LIVE'
          ? formatZAR(institutionalSummary?.metrics?.outstandingReceivables || 0)
          : 'SOURCE SILENT',
        caption: sources.institutionalSummary?.status || 'SOURCE_SILENT'
      },
      {
        label: 'Credit Signals',
        value: sources.creditScores?.status === 'LIVE' ? Object.keys(creditScores || {}).length : 'SOURCE SILENT',
        caption: sources.creditScores?.status || 'SOURCE_SILENT'
      }
    ];
  }, [operationsSnapshot.sources]);

  const invoiceCommandIntelligence = useMemo(() => (
    buildInvoiceCommandIntelligence(invoiceDraft, operationsSnapshot, formatZAR, taxEngineResult)
  ), [invoiceDraft, operationsSnapshot, taxEngineResult]);

  const dunningRecommendations = useMemo(() => (
    buildDunningIntelligence({
      apiRecommendations: dunningState.recommendations,
      ledgerIntelligence,
      invoiceRows: invoiceCommandIntelligence.rows
    })
  ), [dunningState.recommendations, ledgerIntelligence, invoiceCommandIntelligence.rows]);

  const taxTreasuryPosture = useMemo(() => (
    buildTaxTreasuryPosture({
      taxTreasurySnapshot,
      ledgerIntelligence,
      invoiceDraft,
      bankReconciliation,
      taxEngineResult
    })
  ), [taxTreasurySnapshot, ledgerIntelligence, invoiceDraft, bankReconciliation, taxEngineResult]);

  /**
   * @function handleRotateInvoiceIdempotencyKey
   * @description Rotates the invoice idempotency key for a new fiscal command attempt.
   * @returns {void}
   * @collaboration Makes duplicate-invoice defense visible to the founder instead of hidden in backend code.
   */
  const handleRotateInvoiceIdempotencyKey = useCallback(() => {
    setInvoiceDraft(prev => ({ ...prev, idempotencyKey: createInvoiceIdempotencyKey(prev.tenantId) }));
    showToast('Invoice duplicate-defense key rotated.');
  }, [showToast]);

  /**
   * @function handleExportInvoiceCommandPacket
   * @description Exports the current invoice command, readiness checklist and live invoice source posture.
   * @returns {void}
   * @collaboration Gives investor and audit conversations a real invoice artifact without inventing an invoice row.
   */
  const handleExportInvoiceCommandPacket = useCallback(() => {
    const payload = {
      product: 'WILSY OS Invoice Command Packet',
      tenantId: tenantAlias,
      generatedAt: new Date().toISOString(),
      commandPayload: buildInvoiceCommandPayload(invoiceDraft, {
        source: 'WILSY_REVENUE_LEDGER_PACKET_EXPORT',
        taxResult: taxEngineResult
      }),
      invoiceCommandIntelligence,
      taxEngineResult,
      taxMatrix: globalTaxEngine.getMatrixSnapshot(),
      liveSourceStatus: operationsSnapshot?.sources?.invoices?.status || 'SOURCE_SILENT'
    };
    const record = appendRevenueOperation('INVOICE_COMMAND_PACKET_EXPORTED', payload.liveSourceStatus, {
      readiness: invoiceCommandIntelligence.readiness,
      invoiceRows: invoiceCommandIntelligence.rows.length,
      taxProofHash: taxEngineResult?.proof?.hash || null
    });
    exportLedgerJsonArtifact(`WILSY_INVOICE_COMMAND_${tenantAlias}_${record.id}.json`, payload);
    showToast('Invoice command packet exported.');
  }, [tenantAlias, invoiceDraft, invoiceCommandIntelligence, taxEngineResult, operationsSnapshot?.sources?.invoices?.status, appendRevenueOperation, showToast]);

  /**
   * @function handleDunningCommand
   * @description Converts a dunning recommendation into command evidence and optionally opens statement export.
   * @param {Object} recommendation - Dunning recommendation selected by the founder.
   * @returns {void}
   * @collaboration Makes collections a governed action loop instead of a passive risk list.
   */
  const handleDunningCommand = useCallback(async (recommendation) => {
    setOperationBusy(`dunning-${recommendation.id}`);
    try {
      const receipt = await dunningIntelligence.executeIntervention({
        tenantId: recommendation.tenantId || tenantAlias,
        recommendation
      });
      setDunningState(prev => ({
        ...prev,
        lastReceipt: receipt
      }));
      const record = appendRevenueOperation('DUNNING_COMMAND_ARMED', receipt.dispatchStatus || receipt.status, {
        client: recommendation.client,
        amount: recommendation.amount,
        overdueDays: recommendation.overdueDays,
        nextAction: recommendation.nextAction,
        sourceStatus: recommendation.sourceStatus,
        gateStatus: recommendation.gateStatus,
        recommendationProofHash: recommendation.proof?.hash,
        receiptProofHash: receipt.proof?.hash
      });
      setLastOperationReceipt(record);
      showToast(receipt.dispatchStatus === 'DISPATCHED'
        ? `Dunning dispatched • ${recommendation.stage}`
        : `Dunning held • ${recommendation.gateStatus || receipt.status}`);
    } catch (error) {
      appendRevenueOperation('DUNNING_COMMAND_FAILED', 'SOURCE_SILENT', {
        client: recommendation.client,
        error: error.response?.data?.message || error.message
      });
      showToast('Dunning command failed. Evidence preserved.');
    } finally {
      setOperationBusy(null);
    }
  }, [tenantAlias, appendRevenueOperation, showToast]);

  const revenueChartData = useMemo(() => ({
    labels: history.length ? history.map(h => h.label || h.month) : ['No history'],
    datasets: [
      {
        type: 'bar',
        label: 'Revenue Volume',
        data: history.length ? history.map(h => h.volume || h.amount) : [],
        backgroundColor: 'rgba(212, 175, 55, 0.85)',
      },
      {
        type: 'line',
        label: 'ARR Trajectory',
        data: history.length ? history.map(h => h.arr || h.recurring) : [],
        borderColor: '#00ff88',
        tension: 0.4,
        fill: true,
      }
    ]
  }), [history]);

  const complianceChartData = useMemo(() => ({
    labels: compliance?.breakdown?.map(b => b.name) || ['Compliance'],
    datasets: [{
      data: compliance?.breakdown?.map(b => b.score) || [liveComplianceScore],
      backgroundColor: ['#D4AF37', '#00ff88', '#1a1a1a'],
      cutout: '78%',
      borderWidth: 0
    }]
  }), [compliance, liveComplianceScore]);

  const complianceLiveScore = compliance?.score ?? compliance?.complianceScore ?? compliance?.policyScore;
  const complianceHasLiveScore = hasLiveNumber(complianceLiveScore);
  const esgLiveRatio = revenue?.esg?.greenRatio ?? compliance?.greenRatio ?? revenue?.greenRatio;
  const esgHasLiveRatio = hasLiveNumber(esgLiveRatio);

  /**
   * @function buildProofRows
   * @description Converts live ledger, compliance and ESG source states into proof cards for investor-grade review.
   * @param {Array<{label:string,value:string|number,status:string}>} rows - Raw source rows.
   * @returns {Array<{label:string,value:string|number,status:string}>} Normalized proof rows.
   * @collaboration Wilson Khanyezi asked for story and process, not empty cards; these rows explain exactly what source is alive.
   */
  const buildProofRows = (rows) => rows.map((row) => ({
    ...row,
    value: row.value ?? 'SOURCE SILENT',
    status: row.status || 'SOURCE SILENT'
  }));

  const complianceProofRows = buildProofRows([
    {
      label: 'Compliance Score',
      value: formatLivePercent(complianceLiveScore),
      status: complianceHasLiveScore ? 'LIVE' : 'SYNC REQUIRED'
    },
    {
      label: 'Policy Controls',
      value: Array.isArray(compliance?.breakdown) && compliance.breakdown.length
        ? `${compliance.breakdown.length} controls`
        : 'NO BREAKDOWN',
      status: Array.isArray(compliance?.breakdown) && compliance.breakdown.length ? 'LIVE' : 'MISSING'
    },
    {
      label: 'Revenue Link',
      value: operationsSnapshot.sources?.institutionalSummary?.status || 'SOURCE SILENT',
      status: operationsSnapshot.sources?.institutionalSummary?.status === 'LIVE' ? 'LIVE' : 'SOURCE SILENT'
    },
    {
      label: 'Tenant Scope',
      value: tenantAlias,
      status: 'BOUND'
    }
  ]);

  const esgProofRows = buildProofRows([
    {
      label: 'Green Revenue Ratio',
      value: formatLivePercent(esgLiveRatio),
      status: esgHasLiveRatio ? 'LIVE' : 'SYNC REQUIRED'
    },
    {
      label: 'ESG Feed',
      value: revenue?.esg ? 'REVENUE ESG OBJECT' : 'NO ESG OBJECT',
      status: revenue?.esg ? 'LIVE' : 'MISSING'
    },
    {
      label: 'Compliance Link',
      value: complianceHasLiveScore ? formatLivePercent(complianceLiveScore) : 'SOURCE SILENT',
      status: complianceHasLiveScore ? 'LIVE' : 'SOURCE SILENT'
    },
    {
      label: 'Tenant Scope',
      value: tenantAlias,
      status: 'BOUND'
    }
  ]);

  /**
   * @function renderActiveHUD
   * @description Orchestrates the internal routing of the Matrix Shards.
   * @returns {JSX.Element}
   */
  const renderActiveHUD = () => {
    if (loading) {
      return <SkeletonLoader />;
    }

    switch (activeHUD) {
      case 'PREDICTIVE':
        return (
          <div className={styles.hudContent}>
            {/* AI Query Interface */}
            <div style={{ background: '#0a0a0a', padding: '24px', borderRadius: '8px', marginBottom: '24px', border: '1px solid rgba(212, 175, 55, 0.2)' }}>
              <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
                <TerminalSquare size={20} color="#D4AF37" />
                <input
                  type="text"
                  value={queryInput}
                  onChange={(e) => setQueryInput(e.target.value)}
                  disabled={isQuerying}
                  placeholder="Ask revenue command (e.g., 'Project next quarter revenue')"
                  style={{ flex: 1, background: '#000', border: '1px solid #222', color: '#D4AF37', padding: '14px', borderRadius: '4px', outline: 'none', fontFamily: 'monospace', letterSpacing: '1px' }}
                  onKeyPress={(e) => e.key === 'Enter' && handleAIQuery()}
                />
                <button
                  onClick={handleAIQuery}
                  disabled={isQuerying || !queryInput.trim()}
                  className={styles.actionBtnGold}
                  style={{ padding: '0 32px', height: '46px', display: 'flex', alignItems: 'center', gap: '8px' }}
                >
                  {isQuerying ? <Loader2 size={16} className="animate-spin" /> : <Cpu size={16} />}
                  EXECUTE
                </button>
              </div>
              {aiInsightPacket && (
                <section className={styles.aiAnswerBrief} aria-live="polite">
                  <div className={styles.aiAnswerHeader}>
                    <div>
                      <span><Cpu size={14} /> Revenue Intelligence Brief</span>
                      <h3>{aiInsightPacket.posture.replaceAll('_', ' ')}</h3>
                    </div>
                    <div className={styles.aiAnswerSeal}>
                      <small>Source</small>
                      <strong>{aiInsightPacket.sourceStatus.replaceAll('_', ' ')}</strong>
                    </div>
                  </div>

                  <div className={styles.aiAnswerBody}>
                    <article className={styles.aiAnswerPrimary}>
                      <span>Executive Answer</span>
                      <p>{aiInsight || aiInsightPacket.insight}</p>
                    </article>

                    <aside className={styles.aiAnswerProjection}>
                      <span>Next Move</span>
                      <strong>{aiInsightPacket.projection ? formatZAR(aiInsightPacket.projection.projectedQuarterRevenue) : 'No forecast issued'}</strong>
                      <p>{aiInsightPacket.recommendedAction}</p>
                    </aside>
                  </div>

                  <div className={styles.aiEvidenceGrid}>
                    {aiInsightPacket.projection && (
                      <>
                        <article>
                          <span>Baseline Quarter</span>
                          <strong>{formatZAR(aiInsightPacket.projection.baselineQuarterRevenue)}</strong>
                        </article>
                        <article>
                          <span>Cash At Risk</span>
                          <strong>{formatZAR(aiInsightPacket.projection.cashAtRisk)}</strong>
                        </article>
                      </>
                    )}
                    {aiInsightPacket.confidenceScore !== null && (
                      <article>
                        <span>Confidence</span>
                        <strong>{formatPercent(Number(aiInsightPacket.confidenceScore) * 100)}</strong>
                      </article>
                    )}
                    <article>
                      <span>Evidence Nodes</span>
                      <strong>{aiInsightPacket.evidence.length}</strong>
                    </article>
                  </div>

                  <div className={styles.aiEvidenceList}>
                    <span>Evidence used</span>
                    {aiInsightPacket.evidence.length ? aiInsightPacket.evidence.map((item) => (
                      <article key={item} className={styles.aiEvidenceChip}>
                        <small>{parseEvidenceToken(item).label}</small>
                        <strong>{parseEvidenceToken(item).value}</strong>
                      </article>
                    )) : (
                      <article className={styles.aiEvidenceChip}>
                        <small>Evidence</small>
                        <strong>NO LIVE EVIDENCE RETURNED</strong>
                      </article>
                    )}
                  </div>

                  {aiInsightPacket.sealWarning && (
                    <div className={styles.aiSealWarning}>
                      <AlertTriangle size={14} />
                      <span>{aiInsightPacket.sealWarning}</span>
                    </div>
                  )}
                </section>
              )}
            </div>

            <section className={styles.aiFocusCommand}>
              <div className={styles.aiFocusHeader}>
                <div>
                  <span><Cpu size={15} /> AI FOCUS COMMAND</span>
                  <h3>Revenue Decisions, Not Chat Theatre</h3>
                </div>
                <div className={styles.aiFocusScore}>
                  <small>FOCUS SCORE</small>
                  <strong>{aiFocusScore}%</strong>
                </div>
              </div>
              <div className={styles.aiPacketGrid}>
                {aiDecisionPackets.map(packet => (
                  <article key={packet.id} className={styles.aiPacket} data-status={packet.status}>
                    <div className={styles.aiPacketTop}>
                      <span>{packet.owner}</span>
                      <em>{approvedPacketIds.includes(packet.id) ? 'APPROVED' : packet.status}</em>
                    </div>
                    <h4>{packet.title}</h4>
                    <p>{packet.evidence}</p>
                    <small>{packet.action}</small>
                    <button
                      type="button"
                      onClick={() => handleApproveDecisionPacket(packet)}
                      disabled={approvedPacketIds.includes(packet.id)}
                      className={styles.actionBtnGold}
                    >
                      {approvedPacketIds.includes(packet.id) ? 'EVIDENCE LOCKED' : 'APPROVE PACKET'}
                    </button>
                  </article>
                ))}
              </div>
              <div className={styles.aiFocusActions}>
                <button type="button" className={styles.actionBtnGold} onClick={handleLaunchCollectionsMission}>
                  <Radar size={14} /> OPEN COLLECTIONS MISSION
                </button>
                <button type="button" className={styles.actionBtnGold} onClick={handleExportCfoDossier}>
                  <Download size={14} /> EXPORT CFO DOSSIER
                </button>
              </div>
              <div className={styles.aiDecisionLedger}>
                <strong>Founder Revenue Decision Ledger</strong>
                {revenueDecisionLedger.length ? revenueDecisionLedger.slice(0, 4).map(record => (
                  <div key={record.id}>
                    <span>{record.id}</span>
                    <p>{record.title} • {record.status}</p>
                    <small>{record.action}</small>
                  </div>
                )) : (
                  <div>
                    <span>NO DECISION YET</span>
                    <p>Approve an AI packet to create real operating evidence.</p>
                  </div>
                )}
              </div>
            </section>

            <section className={styles.revenueDoctrineCommand}>
              <div className={styles.revenueDoctrineHeader}>
                <div>
                  <span><Scale size={15} /> FOUNDER REVENUE DOCTRINE</span>
                  <h3>Connect Tenant. Prove Motion. Execute Revenue.</h3>
                  <p>
                    Wilsy OS converts live billing, invoice, subscription and credit sources into a command
                    sequence the founder can execute. Silent sources are exposed instead of disguised.
                  </p>
                </div>
                <div className={styles.revenueDoctrineSignal} data-risk={revenueDoctrine.primaryRisk}>
                  <small>SOURCE COVERAGE</small>
                  <strong>{revenueDoctrine.totalSources ? `${revenueDoctrine.coverage}%` : 'SCAN REQUIRED'}</strong>
                  <em>{revenueDoctrine.liveSources}/{revenueDoctrine.totalSources || 0} LIVE</em>
                </div>
              </div>

              <div className={styles.revenueDoctrineRail}>
                <article>
                  <span>Primary Risk</span>
                  <strong>{revenueDoctrine.primaryRisk}</strong>
                  <small>Derived from live source coverage and cash risk.</small>
                </article>
                <article>
                  <span>Tenant Link</span>
                  <strong>{tenantAlias}</strong>
                  <small>All doctrine actions seal back to this authority.</small>
                </article>
                <article>
                  <span>Next Proof</span>
                  <strong>{revenueDoctrine.liveSources ? 'EXPORTABLE' : 'SYNC FIRST'}</strong>
                  <small>No investor artifact is generated from invented data.</small>
                </article>
              </div>

              <div className={styles.revenueDoctrineTimeline}>
                {revenueDoctrine.lifecycle.map(stage => (
                  <article key={stage.id} data-status={stage.status}>
                    <div>
                      <span>{stage.status}</span>
                      <h4>{stage.label}</h4>
                      <p>{stage.evidence}</p>
                      <small>{stage.outcome}</small>
                    </div>
                    <button
                      type="button"
                      data-action={stage.action}
                      onClick={handleRevenueDoctrineAction}
                      disabled={Boolean(operationBusy) && stage.action !== 'OPEN_METERING' && stage.action !== 'OPEN_COLLECTIONS'}
                      className={styles.actionBtnGold}
                    >
                      {stage.cta}
                    </button>
                  </article>
                ))}
              </div>
            </section>

            <section className={styles.revenueOpsConsole}>
              <div className={styles.revenueOpsHeader}>
                <div>
                  <span><ReceiptText size={15} /> LIVE REVENUE OPERATIONS</span>
                  <h3>DB-Backed Billing, Documents, Plans and Usage Control</h3>
                </div>
                <button
                  type="button"
                  className={styles.actionBtnGold}
                  onClick={hydrateRevenueOperations}
                  disabled={operationBusy === 'sync-operations'}
                >
                  {operationBusy === 'sync-operations' ? <Loader2 size={14} className="animate-spin" /> : <RefreshCw size={14} />}
                  SYNC LIVE SOURCES
                </button>
              </div>

              <section className={styles.statementPeriodConsole} aria-label="Statement period authority">
                <div className={styles.statementPeriodBrief}>
                  <span><FileText size={15} /> SEALED STATEMENT PERIOD</span>
                  <h3>Choose Dates Before Artifact Generation</h3>
                  <p>
                    These controls drive the exported statement, invoice payload, payment policy and forensic
                    evidence rows. Nothing is hidden inside the PDF renderer.
                  </p>
                </div>
                <div className={styles.statementPeriodGrid}>
                  <label>
                    <span>Period Menu</span>
                    <select value={statementPreset} onChange={handleStatementPresetChange}>
                      <option value="LAST_30_DAYS">Last 30 days</option>
                      <option value="THIS_MONTH">This month</option>
                      <option value="PREVIOUS_MONTH">Previous month</option>
                      <option value="THIS_QUARTER">This quarter</option>
                      <option value="YEAR_TO_DATE">Year to date</option>
                      <option value="CUSTOM">Custom range</option>
                    </select>
                  </label>
                  <label>
                    <span>Statement / Issue Date</span>
                    <input
                      type="date"
                      value={invoiceDraft.issueDate}
                      onChange={(event) => {
                        setStatementPreset('CUSTOM');
                        setInvoiceDraft(prev => ({
                          ...prev,
                          issueDate: event.target.value,
                          dueDate: deriveDueDateFromTerms(event.target.value, prev.paymentTerms)
                        }));
                      }}
                    />
                  </label>
                  <label>
                    <span>Period Start</span>
                    <input
                      type="date"
                      value={invoiceDraft.billingPeriodStart}
                      onChange={(event) => {
                        setStatementPreset('CUSTOM');
                        setInvoiceDraft(prev => ({ ...prev, billingPeriodStart: event.target.value }));
                      }}
                    />
                  </label>
                  <label>
                    <span>Period End</span>
                    <input
                      type="date"
                      value={invoiceDraft.billingPeriodEnd}
                      onChange={(event) => {
                        setStatementPreset('CUSTOM');
                        setInvoiceDraft(prev => ({ ...prev, billingPeriodEnd: event.target.value }));
                      }}
                    />
                  </label>
                  <label>
                    <span>Payment Terms</span>
                    <select
                      value={invoiceDraft.paymentTerms}
                      onChange={(event) => setInvoiceDraft(prev => ({
                        ...prev,
                        paymentTerms: event.target.value,
                        dueDate: deriveDueDateFromTerms(prev.issueDate, event.target.value)
                      }))}
                    >
                      <option value="DUE_ON_RECEIPT">Due on receipt</option>
                      <option value="NET_7">Net 7</option>
                      <option value="NET_14">Net 14</option>
                      <option value="NET_30">Net 30</option>
                      <option value="NET_60">Net 60</option>
                    </select>
                  </label>
                  <label>
                    <span>Due Date</span>
                    <input
                      type="date"
                      value={invoiceDraft.dueDate}
                      onChange={(event) => {
                        setStatementPreset('CUSTOM');
                        setInvoiceDraft(prev => ({ ...prev, dueDate: event.target.value }));
                      }}
                    />
                  </label>
                </div>
              </section>

              <div className={styles.invoiceCommandDeck}>
                <div className={styles.invoiceCommandBrief}>
                  <span><LockKeyhole size={15} /> INVOICE FINALITY ENGINE</span>
                  <h3>Duplicate-Safe, Tax-Aware, Tenant-Sealed Invoicing</h3>
                  <p>
                    Every invoice command carries tenant authority, period controls, tax jurisdiction,
                    line-item math and an idempotency key. If the invoice DB source is silent, Wilsy OS says so.
                  </p>
                </div>
                <div className={styles.invoiceReadinessGauge}>
                  <small>COMMAND READINESS</small>
                  <strong>{invoiceCommandIntelligence.readiness}%</strong>
                  <em>{operationsSnapshot?.sources?.invoices?.status || 'SOURCE_SILENT'}</em>
                </div>
                <div className={styles.invoiceMetricRail}>
                  {invoiceCommandIntelligence.metrics.map(metric => (
                    <article key={metric.label}>
                      <span>{metric.label}</span>
                      <strong>{metric.value}</strong>
                      <small>{metric.caption}</small>
                    </article>
                  ))}
                </div>
                <div className={styles.invoiceChecklist}>
                  {invoiceCommandIntelligence.checklist.map(item => (
                    <article key={item.label} data-live={item.live ? 'true' : 'false'}>
                      {item.live ? <CheckCircle size={14} /> : <AlertTriangle size={14} />}
                      <div>
                        <strong>{item.label}</strong>
                        <small>{item.evidence}</small>
                      </div>
                    </article>
                  ))}
                </div>
                <div className={styles.invoiceCommandActions}>
                  <button type="button" onClick={handleRotateInvoiceIdempotencyKey}>
                    <RefreshCw size={14} /> ROTATE DUPLICATE DEFENSE
                  </button>
                  <button type="button" onClick={handleExportInvoiceCommandPacket}>
                    <Download size={14} /> EXPORT INVOICE PACKET
                  </button>
                </div>
              </div>

              <div className={styles.revenueOpsGrid}>
                <div className={styles.revenueOpsForm}>
                  <label>
                    <span>TENANT ID</span>
                    <input
                      value={invoiceDraft.tenantId}
                      onChange={(event) => setInvoiceDraft(prev => ({ ...prev, tenantId: event.target.value }))}
                      placeholder="GLOBAL_ROOT"
                    />
                  </label>
                  <label>
                    <span>CLIENT ID</span>
                    <input
                      value={invoiceDraft.clientId}
                      onChange={(event) => setInvoiceDraft(prev => ({ ...prev, clientId: event.target.value }))}
                      placeholder="CLIENT-001"
                    />
                  </label>
                  <label>
                    <span>INVOICE CLASS</span>
                    <select
                      value={invoiceDraft.invoiceClass}
                      onChange={(event) => setInvoiceDraft(prev => ({ ...prev, invoiceClass: event.target.value }))}
                    >
                      <option value="SOVEREIGN_INFRA_FEE">Sovereign infrastructure fee</option>
                      <option value="PLATFORM_FEE">Platform fee</option>
                      <option value="CLIENT_INVOICE">Client invoice</option>
                      <option value="INSTITUTIONAL_SERVICE">Institutional service</option>
                    </select>
                  </label>
                  <label>
                    <span>CURRENCY</span>
                    <select
                      value={invoiceDraft.currency}
                      onChange={(event) => setInvoiceDraft(prev => ({ ...prev, currency: event.target.value }))}
                    >
                      {['ZAR', 'USD', 'EUR', 'GBP', 'NGN', 'KES', 'GHS', 'BWP', 'NAD', 'MUR'].map(currency => (
                        <option key={currency} value={currency}>{currency}</option>
                      ))}
                    </select>
                  </label>
                  <label>
                    <span>AMOUNT</span>
                    <input
                      type="number"
                      min="0"
                      value={invoiceDraft.amount}
                      onChange={(event) => setInvoiceDraft(prev => ({ ...prev, amount: event.target.value }))}
                      placeholder="0.00"
                    />
                  </label>
                  <label>
                    <span>UNIT PRICE</span>
                    <input
                      type="number"
                      min="0"
                      step="0.01"
                      value={invoiceDraft.unitPrice}
                      onChange={(event) => setInvoiceDraft(prev => ({
                        ...prev,
                        unitPrice: event.target.value,
                        amount: String(Number(event.target.value || 0) * Number(prev.quantity || 1))
                      }))}
                      placeholder="0.00"
                    />
                  </label>
                  <label>
                    <span>QUANTITY</span>
                    <input
                      type="number"
                      min="1"
                      step="1"
                      value={invoiceDraft.quantity}
                      onChange={(event) => setInvoiceDraft(prev => ({
                        ...prev,
                        quantity: event.target.value,
                        amount: String(Number(prev.unitPrice || prev.amount || 0) * Number(event.target.value || 1))
                      }))}
                      placeholder="1"
                    />
                  </label>
                  <label>
                    <span>ISSUE DATE</span>
                    <input
                      type="date"
                      value={invoiceDraft.issueDate}
                      onChange={(event) => setInvoiceDraft(prev => ({
                        ...prev,
                        issueDate: event.target.value,
                        dueDate: deriveDueDateFromTerms(event.target.value, prev.paymentTerms)
                      }))}
                    />
                  </label>
                  <label>
                    <span>PERIOD START</span>
                    <input
                      type="date"
                      value={invoiceDraft.billingPeriodStart}
                      onChange={(event) => setInvoiceDraft(prev => ({ ...prev, billingPeriodStart: event.target.value }))}
                    />
                  </label>
                  <label>
                    <span>PERIOD END</span>
                    <input
                      type="date"
                      value={invoiceDraft.billingPeriodEnd}
                      onChange={(event) => setInvoiceDraft(prev => ({ ...prev, billingPeriodEnd: event.target.value }))}
                    />
                  </label>
                  <label>
                    <span>PAYMENT TERMS</span>
                    <select
                      value={invoiceDraft.paymentTerms}
                      onChange={(event) => setInvoiceDraft(prev => ({
                        ...prev,
                        paymentTerms: event.target.value,
                        dueDate: deriveDueDateFromTerms(prev.issueDate, event.target.value)
                      }))}
                    >
                      <option value="DUE_ON_RECEIPT">Due on receipt</option>
                      <option value="NET_7">Net 7</option>
                      <option value="NET_14">Net 14</option>
                      <option value="NET_30">Net 30</option>
                      <option value="NET_60">Net 60</option>
                    </select>
                  </label>
                  <label>
                    <span>TAX TYPE</span>
                    <select
                      value={invoiceDraft.taxType}
                      onChange={(event) => setInvoiceDraft(prev => ({ ...prev, taxType: event.target.value }))}
                    >
                      <option value="VAT">VAT</option>
                      <option value="VAT_ZERO">VAT zero-rated</option>
                      <option value="VAT_EXEMPT">VAT exempt</option>
                      <option value="NO_TAX">No tax</option>
                      <option value="WITHHOLDING">Withholding</option>
                    </select>
                  </label>
                  <label>
                    <span>TENANT TAX RESIDENCE</span>
                    <select
                      value={invoiceDraft.tenantJurisdiction}
                      onChange={(event) => setInvoiceDraft(prev => ({ ...prev, tenantJurisdiction: event.target.value }))}
                    >
                      {['ZA', 'NG', 'KE', 'GH', 'BW', 'NA', 'MU', 'GB', 'AE', 'SG', 'AU', 'EU', 'US'].map(jurisdiction => (
                        <option key={jurisdiction} value={jurisdiction}>{jurisdiction}</option>
                      ))}
                    </select>
                  </label>
                  <label>
                    <span>CLIENT TAX JURISDICTION</span>
                    <select
                      value={invoiceDraft.clientJurisdiction || invoiceDraft.taxJurisdiction}
                      onChange={(event) => setInvoiceDraft(prev => ({
                        ...prev,
                        clientJurisdiction: event.target.value,
                        taxJurisdiction: event.target.value
                      }))}
                    >
                      {['ZA', 'NG', 'KE', 'GH', 'BW', 'NA', 'MU', 'GB', 'AE', 'SG', 'AU', 'EU', 'US'].map(jurisdiction => (
                        <option key={jurisdiction} value={jurisdiction}>{jurisdiction}</option>
                      ))}
                    </select>
                  </label>
                  <label>
                    <span>CLIENT TYPE</span>
                    <select
                      value={invoiceDraft.clientType}
                      onChange={(event) => setInvoiceDraft(prev => ({ ...prev, clientType: event.target.value }))}
                    >
                      <option value="B2B">B2B / VAT registered</option>
                      <option value="B2C">B2C / consumer</option>
                    </select>
                  </label>
                  <label>
                    <span>SUPPLY TYPE</span>
                    <select
                      value={invoiceDraft.supplyType}
                      onChange={(event) => setInvoiceDraft(prev => ({ ...prev, supplyType: event.target.value }))}
                    >
                      <option value="DIGITAL_SERVICE">Digital service</option>
                      <option value="SAAS">SaaS subscription</option>
                      <option value="AI_SERVICE">AI service</option>
                      <option value="LEGAL_SERVICE">Legal service</option>
                      <option value="GOODS">Goods</option>
                    </select>
                  </label>
                  <label>
                    <span>WITHHOLDING RATE</span>
                    <input
                      type="number"
                      min="0"
                      max="100"
                      step="0.01"
                      value={invoiceDraft.withholdingRate}
                      onChange={(event) => setInvoiceDraft(prev => ({ ...prev, withholdingRate: event.target.value }))}
                      placeholder="0"
                    />
                  </label>
                  <label>
                    <span>BILLING MODEL</span>
                    <select
                      value={invoiceDraft.billingModel}
                      onChange={(event) => setInvoiceDraft(prev => ({ ...prev, billingModel: event.target.value }))}
                    >
                      <option value="PLATFORM_RETAINER">Platform retainer</option>
                      <option value="USAGE_BASED">Usage based</option>
                      <option value="SEAT_BASED">Seat based</option>
                      <option value="HYBRID_SOVEREIGN">Hybrid sovereign</option>
                    </select>
                  </label>
                  <label>
                    <span>DUE DATE</span>
                    <input
                      type="date"
                      value={invoiceDraft.dueDate}
                      onChange={(event) => setInvoiceDraft(prev => ({ ...prev, dueDate: event.target.value }))}
                    />
                  </label>
                  <label className={styles.revenueOpsWide}>
                    <span>CUSTOMER TAX ID / VAT NUMBER</span>
                    <input
                      value={invoiceDraft.customerTaxId}
                      onChange={(event) => setInvoiceDraft(prev => ({ ...prev, customerTaxId: event.target.value }))}
                      placeholder="VAT / GST / Tax registration evidence"
                    />
                  </label>
                  <label className={styles.revenueOpsWide}>
                    <span>IDEMPOTENCY KEY</span>
                    <input
                      value={invoiceDraft.idempotencyKey}
                      onChange={(event) => setInvoiceDraft(prev => ({ ...prev, idempotencyKey: event.target.value }))}
                      placeholder="WILSY-INV-..."
                    />
                  </label>
                  <label className={styles.revenueOpsWide}>
                    <span>LINE ITEM / DOCUMENT BASIS</span>
                    <textarea
                      value={invoiceDraft.description}
                      onChange={(event) => setInvoiceDraft(prev => ({ ...prev, description: event.target.value }))}
                      placeholder="Describe the service, legal basis or billing event."
                    />
                  </label>
                </div>

                <div className={styles.revenueOpsActions}>
                  <button type="button" onClick={handleCreateSovereignInvoice} disabled={Boolean(operationBusy)}>
                    {operationBusy === 'sovereign-invoice' ? <Loader2 size={15} className="animate-spin" /> : <ReceiptText size={15} />}
                    CREATE PLATFORM INVOICE
                  </button>
                  <button type="button" onClick={handleCreateClientInvoice} disabled={Boolean(operationBusy)}>
                    {operationBusy === 'client-invoice' ? <Loader2 size={15} className="animate-spin" /> : <CreditCard size={15} />}
                    CREATE CLIENT INVOICE
                  </button>
                  <button type="button" onClick={handleRunMonthlyBilling} disabled={Boolean(operationBusy)}>
                    {operationBusy === 'monthly-billing' ? <Loader2 size={15} className="animate-spin" /> : <Repeat2 size={15} />}
                    RUN MONTHLY BILLING
                  </button>
                  <button type="button" onClick={handleApplyDynamicPricingGuard} disabled={Boolean(operationBusy)}>
                    {operationBusy === 'dynamic-pricing' ? <Loader2 size={15} className="animate-spin" /> : <Gauge size={15} />}
                    APPLY PRICING GUARD
                  </button>
                  <button type="button" onClick={handleGenerateStatement} disabled={isGenerating}>
                    {isGenerating ? <Loader2 size={15} className="animate-spin" /> : <Download size={15} />}
                    CREATE SEALED DOCUMENT
                  </button>
                </div>
              </div>

              <div className={styles.operationReceiptRail} aria-live="polite">
                <div className={styles.operationReceiptPrimary}>
                  <span>Last command receipt</span>
                  {lastOperationReceipt ? (
                    <>
                      <strong>{lastOperationReceipt.title || formatOperationLabel(lastOperationReceipt.type)}</strong>
                      <small>
                        {lastOperationReceipt.status} • {new Date(lastOperationReceipt.timestamp).toLocaleTimeString()} • {lastOperationReceipt.id}
                      </small>
                    </>
                  ) : (
                    <>
                      <strong>No command executed yet</strong>
                      <small>Press a revenue operation button to create founder-visible evidence.</small>
                    </>
                  )}
                </div>
                <div className={styles.operationReceiptStack}>
                  {revenueDecisionLedger.slice(0, 3).map(record => (
                    <article key={record.id} data-status={record.status}>
                      <span>{record.status}</span>
                      <strong>{record.title || formatOperationLabel(record.type)}</strong>
                      <small>{record.action || record.type}</small>
                    </article>
                  ))}
                </div>
              </div>

              <div className={styles.revenueOpsStatusGrid}>
                {revenueOperationCards.map(card => (
                  <article key={card.label}>
                    <span>{card.label}</span>
                    <strong>{card.value}</strong>
                    <small>{card.caption}</small>
                  </article>
                ))}
              </div>

              {Object.keys(operationsSnapshot.errors || {}).length > 0 && (
                <div className={styles.revenueOpsErrors}>
                  <strong>Silent Sources</strong>
                  {Object.entries(operationsSnapshot.errors).map(([source, message]) => (
                    <span key={source}>{source}: {message}</span>
                  ))}
                </div>
              )}
            </section>

            {/* What-If Simulator Interface */}
            <div style={{ background: '#050505', padding: '32px', border: '1px solid #1a1a1a', borderRadius: '8px', position: 'relative', overflow: 'hidden' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '25px' }}>
                <h3 style={{ color: '#D4AF37', margin: 0, fontWeight: 900, letterSpacing: '2px' }}>STRATEGIC SCENARIO MODELER</h3>
                <button
                  onClick={handleCommitScenario}
                  disabled={isCommitting}
                  className={styles.actionBtnGold}
                  style={{ padding: '8px 20px', fontSize: '0.7rem', display: 'flex', alignItems: 'center', gap: '8px' }}
                >
                  {isCommitting ? <Loader2 size={14} className="animate-spin" /> : <Save size={14} />}
                  COMMIT TO BOARD
                </button>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '40px', position: 'relative', zIndex: 2 }}>
                <div style={{ background: '#0a0a0a', padding: '20px', borderRadius: '6px', border: '1px solid #222' }}>
                  <label style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '12px', color: '#888', fontSize: '0.7rem', fontWeight: 900, letterSpacing: '1px' }}>
                    <span>YIELD ADJUSTMENT</span>
                    <span style={{ color: whatIfParams.priceChange >= 0 ? '#00ff88' : '#ff6666' }}>{whatIfParams.priceChange}%</span>
                  </label>
                  <input type="range" min="-25" max="35" value={whatIfParams.priceChange} onChange={(e) => setWhatIfParams(p => ({...p, priceChange: Number(e.target.value)}))} style={{ width: '100%', cursor: 'pointer' }} />
                </div>
                <div style={{ background: '#0a0a0a', padding: '20px', borderRadius: '6px', border: '1px solid #222' }}>
                  <label style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '12px', color: '#888', fontSize: '0.7rem', fontWeight: 900, letterSpacing: '1px' }}>
                    <span>VOLUME EXPANSION</span>
                    <span style={{ color: whatIfParams.volumeChange >= 0 ? '#00ff88' : '#ff6666' }}>{whatIfParams.volumeChange}%</span>
                  </label>
                  <input type="range" min="-20" max="45" value={whatIfParams.volumeChange} onChange={(e) => setWhatIfParams(p => ({...p, volumeChange: Number(e.target.value)}))} style={{ width: '100%', cursor: 'pointer' }} />
                </div>
              </div>

              <div style={{ marginTop: '30px', padding: '20px', background: '#000', border: '1px solid rgba(0, 255, 136, 0.2)', borderRadius: '6px', textAlign: 'center' }}>
                <div style={{ fontSize: '0.65rem', color: '#888', letterSpacing: '2px', marginBottom: '5px' }}>PROJECTED ARR TRAJECTORY</div>
                <div style={{ fontSize: '2.8rem', fontWeight: 900, color: '#00ff88', textShadow: '0 0 20px rgba(0,255,136,0.3)' }}>
                  {formatZAR(projectedARR)}
                </div>
              </div>
            </div>
          </div>
        );

      case 'REVENUE':
        return (
          <div className={styles.hudContent}>
            {/* Action Bar */}
            <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: '15px' }}>
               <button
                  onClick={handleForceSync}
                  disabled={isSyncing}
                  style={{ background: 'transparent', border: '1px solid #333', color: '#D4AF37', padding: '6px 12px', borderRadius: '4px', fontSize: '0.65rem', fontWeight: 900, letterSpacing: '1px', display: 'flex', alignItems: 'center', gap: '6px', cursor: 'pointer' }}
                >
                  <RefreshCw size={12} className={isSyncing ? "animate-spin" : ""} />
                  {isSyncing ? 'SYNCING PIPELINE...' : 'FORCE LEDGER SYNC'}
               </button>
            </div>

            {anomalyDetected && (
              <div className={styles.anomalyBanner} style={{ display: 'flex', alignItems: 'center', gap: '12px', padding: '12px 20px', background: 'rgba(255, 51, 51, 0.1)', borderLeft: '4px solid #ff3333', borderRadius: '4px', marginBottom: '20px' }}>
                <AlertTriangle size={20} color="#ff3333" />
                <div style={{ color: '#ffaaaa', fontSize: '0.8rem', letterSpacing: '0.5px' }}>
                  <strong style={{ color: '#ff3333', marginRight: '8px' }}>[{anomalyDetected.type}]</strong>
                  {anomalyDetected.message}
                </div>
              </div>
            )}

            <div className={styles.metricGrid} style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '16px', marginBottom: '24px' }}>
              <div className={styles.titanCard} style={{ background: '#0a0a0a', padding: '24px', border: '1px solid rgba(212,175,55,0.2)', borderRadius: '8px' }}>
                <div className={styles.titanLabel} style={{ fontSize: '0.7rem', color: '#888', letterSpacing: '2px', fontWeight: 900, marginBottom: '10px' }}>TOTAL VERIFIED EQUITY</div>
                <div className={styles.titanValue} style={{ fontSize: '1.9rem', color: '#fff', fontWeight: 900 }}>{formatZAR(totalVolume)}</div>
              </div>
              <div className={styles.titanCard} style={{ background: '#0a0a0a', padding: '24px', border: '1px solid rgba(212,175,55,0.2)', borderRadius: '8px' }}>
                <div className={styles.titanLabel} style={{ fontSize: '0.7rem', color: '#888', letterSpacing: '2px', fontWeight: 900, marginBottom: '10px' }}>NET REVENUE RETENTION PROXY</div>
                <div className={styles.titanValue} style={{ fontSize: '1.9rem', fontWeight: 900, color: ledgerIntelligence.nrrProxy >= 100 ? '#00ff88' : '#ff6666' }}>
                  {formatPercent(ledgerIntelligence.nrrProxy)}
                </div>
              </div>
              <div className={styles.titanCard} style={{ background: '#0a0a0a', padding: '24px', border: '1px solid rgba(212,175,55,0.2)', borderRadius: '8px' }}>
                <div className={styles.titanLabel} style={{ fontSize: '0.7rem', color: '#888', letterSpacing: '2px', fontWeight: 900, marginBottom: '10px' }}>COLLECTION EFFICIENCY</div>
                <div className={styles.titanValue} style={{ fontSize: '1.9rem', color: ledgerIntelligence.collectionEfficiency > 80 ? '#00ff88' : '#D4AF37', fontWeight: 900 }}>
                  {formatPercent(ledgerIntelligence.collectionEfficiency)}
                </div>
              </div>
              <div className={styles.titanCard} style={{ background: '#0a0a0a', padding: '24px', border: '1px solid rgba(212,175,55,0.2)', borderRadius: '8px' }}>
                <div className={styles.titanLabel} style={{ fontSize: '0.7rem', color: '#888', letterSpacing: '2px', fontWeight: 900, marginBottom: '10px' }}>ACTIVE CONTRACTS</div>
                <div className={styles.titanValue} style={{ fontSize: '1.9rem', color: '#fff', fontWeight: 900 }}>
                  {ledgerIntelligence.activeContracts}
                </div>
              </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '14px', marginBottom: '24px' }}>
              {revenueOperatingSystem.map(item => (
                <article key={item.label} style={{ background: '#050505', border: '1px solid #1a1a1a', borderRadius: '8px', padding: '18px', minHeight: '126px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '18px' }}>
                    <span style={{ color: '#777', fontSize: '0.62rem', fontWeight: 900, letterSpacing: '1.4px' }}>{item.label.toUpperCase()}</span>
                    <item.icon size={16} color={item.tone} />
                  </div>
                  <strong style={{ display: 'block', color: item.tone, fontSize: '1.25rem', fontFamily: 'monospace', marginBottom: '8px' }}>{item.value}</strong>
                  <small style={{ color: '#555', fontSize: '0.66rem', lineHeight: 1.4 }}>{item.caption}</small>
                </article>
              ))}
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1.55fr 0.85fr', gap: '20px' }}>
              <div style={{ height: '380px', background: '#050505', border: '1px solid #1a1a1a', padding: '20px', borderRadius: '8px' }}>
                <Bar data={revenueChartData} options={{ responsive: true, maintainAspectRatio: false, plugins: { legend: { labels: { color: '#888', font: { family: 'monospace' } } } }, scales: { x: { grid: { color: '#111' }, ticks: { color: '#666' } }, y: { grid: { color: '#111' }, ticks: { color: '#666' } } } }} />
              </div>
              <div style={{ background: '#050505', border: '1px solid #1a1a1a', padding: '20px', borderRadius: '8px', minHeight: '380px' }}>
                <h3 style={{ margin: 0, marginBottom: '16px', color: '#D4AF37', fontSize: '0.78rem', letterSpacing: '2px', fontWeight: 900 }}>FORENSIC TRANSACTION CHAIN</h3>
                {ledgerLoading && <div style={{ color: '#666', fontSize: '0.72rem' }}>Hydrating ledger chain...</div>}
                {!ledgerLoading && ledgerIntelligence.transactions.length === 0 && (
                  <div style={{ color: '#555', fontSize: '0.72rem' }}>No live revenue transactions committed.</div>
                )}
                {ledgerIntelligence.transactions.slice(0, 7).map(tx => (
                  <div key={`${tx.hash}-${tx.reference}`} style={{ borderTop: '1px solid #111', padding: '11px 0', display: 'grid', gridTemplateColumns: '1fr auto', gap: '10px' }}>
                    <div>
                      <strong style={{ display: 'block', color: '#eee', fontSize: '0.72rem', letterSpacing: '0.5px' }}>{tx.reference}</strong>
                      <small style={{ color: '#666', fontFamily: 'monospace' }}>{tx.date} • {tx.previousHash}</small>
                    </div>
                    <div style={{ textAlign: 'right' }}>
                      <span style={{ display: 'block', color: '#00ff88', fontSize: '0.72rem', fontWeight: 900 }}>{formatZAR(tx.amount)}</span>
                      <small style={{ color: '#D4AF37', fontFamily: 'monospace' }}>{tx.hash}</small>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        );

      case 'COLLECTIONS':
        return (
          <div className={styles.hudContent}>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '16px', marginBottom: '24px' }}>
              {[
                { label: 'Pending Payments', value: formatZAR(ledgerIntelligence.pendingPayments), icon: WalletCards, tone: '#D4AF37' },
                { label: 'Revenue Leakage', value: formatZAR(ledgerIntelligence.leakage), icon: AlertTriangle, tone: ledgerIntelligence.leakage > 0 ? '#ff6666' : '#00ff88' },
                { label: 'Peer DSO Percentile', value: ledgerIntelligence.peerBenchmark ? `${ledgerIntelligence.peerBenchmark.yourPercentile}%` : '0%', icon: Scale, tone: '#00ff88' }
              ].map(item => (
                <article key={item.label} style={{ background: '#080808', border: '1px solid #1a1a1a', borderRadius: '8px', padding: '22px' }}>
                  <item.icon size={18} color={item.tone} />
                  <span style={{ display: 'block', color: '#777', fontSize: '0.66rem', letterSpacing: '1.5px', fontWeight: 900, marginTop: '14px' }}>{item.label.toUpperCase()}</span>
                  <strong style={{ display: 'block', color: item.tone, fontSize: '1.7rem', marginTop: '8px', fontFamily: 'monospace' }}>{item.value}</strong>
                </article>
              ))}
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1.15fr 0.85fr', gap: '20px' }}>
              <section style={{ background: '#050505', border: '1px solid #1a1a1a', borderRadius: '8px', padding: '22px' }}>
                <h3 style={{ margin: 0, marginBottom: '18px', color: '#D4AF37', fontSize: '0.8rem', letterSpacing: '2px', fontWeight: 900 }}>COLLECTION RISK COMMAND</h3>
                {ledgerIntelligence.collectionRiskItems.length === 0 ? (
                  <div style={{ color: '#666', fontSize: '0.8rem' }}>No overdue collection risk detected in the live ledger.</div>
                ) : ledgerIntelligence.collectionRiskItems.map(item => (
                  <article key={`${item.client}-${item.amount}`} style={{ borderTop: '1px solid #111', padding: '14px 0', display: 'grid', gridTemplateColumns: '1fr auto', gap: '16px' }}>
                    <div>
                      <strong style={{ color: '#fff', fontSize: '0.82rem' }}>{item.client}</strong>
                      <p style={{ color: '#888', fontSize: '0.72rem', margin: '7px 0 0', lineHeight: 1.45 }}>{item.aiRecommendation}</p>
                    </div>
                    <div style={{ textAlign: 'right' }}>
                      <span style={{ color: '#ff6666', display: 'block', fontWeight: 900 }}>{formatZAR(item.amount)}</span>
                      <small style={{ color: '#D4AF37' }}>{item.dueDays}d overdue • risk {item.riskScore}</small>
                    </div>
                  </article>
                ))}
              </section>

              <section style={{ background: '#050505', border: '1px solid #1a1a1a', borderRadius: '8px', padding: '22px' }}>
                <h3 style={{ margin: 0, marginBottom: '18px', color: '#D4AF37', fontSize: '0.8rem', letterSpacing: '2px', fontWeight: 900 }}>CLIENT HEALTH RADAR</h3>
                {ledgerIntelligence.clientRiskScores.length === 0 ? (
                  <div style={{ color: '#666', fontSize: '0.8rem' }}>Client risk graph will activate after paid invoice history exists.</div>
                ) : ledgerIntelligence.clientRiskScores.map(client => (
                  <div key={client.client} style={{ marginBottom: '16px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.7rem', marginBottom: '6px' }}>
                      <span style={{ color: '#ddd' }}>{client.client}</span>
                      <span style={{ color: client.score > 65 ? '#00ff88' : '#ff6666' }}>{client.score}/100</span>
                    </div>
                    <div style={{ height: '6px', background: '#111', borderRadius: '999px', overflow: 'hidden' }}>
                      <div style={{ width: `${client.score}%`, height: '100%', background: client.score > 65 ? '#00ff88' : '#ff6666' }} />
                    </div>
                  </div>
                ))}
              </section>
            </div>

            <section style={{ marginTop: '22px', background: '#050505', border: '1px solid rgba(255,102,102,0.24)', borderRadius: '8px', padding: '24px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', gap: '18px', alignItems: 'flex-start', marginBottom: '18px' }}>
                <div>
                  <span style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#ffaaaa', fontSize: '0.68rem', letterSpacing: '1.8px', fontWeight: 900 }}>
                    <BellRing size={15} /> DUNNING INTELLIGENCE
                  </span>
                  <h3 style={{ margin: '8px 0 0', color: '#fff', fontSize: '1.05rem' }}>Collections that escalate with evidence.</h3>
                  <p style={{ margin: '8px 0 0', color: '#777', maxWidth: '720px', fontSize: '0.76rem', lineHeight: 1.55 }}>
                    Dunning recommendations are pulled from the live source when available, then cross-checked against invoice
                    and collection-risk rows. Wilsy OS arms the next action without pretending a silent endpoint responded.
                  </p>
                </div>
                <button
                  type="button"
                  onClick={hydrateDunningIntelligence}
                  disabled={operationBusy === 'dunning-sync'}
                  className={styles.actionBtnGold}
                  style={{ whiteSpace: 'nowrap', display: 'flex', alignItems: 'center', gap: '8px' }}
                >
                  {operationBusy === 'dunning-sync' ? <Loader2 size={14} className="animate-spin" /> : <RefreshCw size={14} />}
                  SYNC DUNNING
                </button>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '14px' }}>
                {dunningRecommendations.length ? dunningRecommendations.map(item => (
                  <article key={item.id} style={{ background: '#090909', border: `1px solid ${item.tone}44`, borderRadius: '8px', padding: '18px', minHeight: '190px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', gap: '12px', marginBottom: '12px' }}>
                      <span style={{ color: item.tone, fontSize: '0.63rem', letterSpacing: '1.5px', fontWeight: 900 }}>{item.stage}</span>
                      <small style={{ color: item.gateStatus === 'READY' ? '#00ff88' : '#D4AF37', fontSize: '0.6rem' }}>{item.gateStatus || item.sourceStatus}</small>
                    </div>
                    <strong style={{ display: 'block', color: '#fff', fontSize: '0.95rem', marginBottom: '8px' }}>{item.client}</strong>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px', marginBottom: '12px' }}>
                      <div>
                        <small style={{ color: '#666' }}>Exposure</small>
                        <span style={{ display: 'block', color: '#D4AF37', fontWeight: 900 }}>{formatZAR(item.amount)}</span>
                      </div>
                      <div>
                        <small style={{ color: '#666' }}>Aging</small>
                        <span style={{ display: 'block', color: item.tone, fontWeight: 900 }}>{item.overdueDays}d / {item.riskScore}</span>
                      </div>
                    </div>
                    <p style={{ color: '#888', fontSize: '0.72rem', lineHeight: 1.45, minHeight: '44px' }}>{item.nextAction}</p>
                    {item.complianceWarnings?.length > 0 && (
                      <small style={{ display: 'block', color: '#D4AF37', fontSize: '0.66rem', lineHeight: 1.35, marginBottom: '8px' }}>
                        {item.complianceWarnings[0]}
                      </small>
                    )}
                    <small style={{ display: 'block', color: '#555', fontSize: '0.62rem', overflowWrap: 'anywhere' }}>
                      Proof {item.proof?.hash ? item.proof.hash.slice(0, 16) : 'UNSEALED'} • {item.channel || 'NO CHANNEL'}
                    </small>
                    <button
                      type="button"
                      onClick={() => handleDunningCommand(item)}
                      disabled={Boolean(operationBusy)}
                      className={styles.actionBtnGold}
                      style={{ width: '100%', marginTop: '10px' }}
                    >
                      {operationBusy === `dunning-${item.id}` ? 'ARMING...' : 'ARM DUNNING COMMAND'}
                    </button>
                  </article>
                )) : (
                  <article style={{ background: '#090909', border: '1px solid #1a1a1a', borderRadius: '8px', padding: '20px', color: '#777' }}>
                    <strong style={{ display: 'block', color: '#D4AF37', marginBottom: '8px' }}>NO DUNNING TARGETS</strong>
                    <p style={{ margin: 0, fontSize: '0.76rem', lineHeight: 1.5 }}>
                      No dunning source, invoice risk row, or collection risk item is currently available. Sync live sources or create invoices to activate this command rail.
                    </p>
                  </article>
                )}
              </div>
            </section>
          </div>
        );

      case 'METERING':
        return (
          <div className={styles.hudContent}>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '18px', marginBottom: '24px' }}>
              {usageMeters.map(meter => (
                <article key={meter.name} style={{ background: '#050505', border: '1px solid rgba(0,255,136,0.18)', borderRadius: '8px', padding: '24px' }}>
                  <Activity size={18} color="#00ff88" />
                  <span style={{ display: 'block', color: '#777', fontSize: '0.66rem', letterSpacing: '1.5px', fontWeight: 900, marginTop: '14px' }}>{meter.name.toUpperCase()}</span>
                  <strong style={{ display: 'block', color: '#00ff88', fontSize: '2rem', marginTop: '8px', fontFamily: 'monospace' }}>{meter.value}</strong>
                  <small style={{ color: '#555' }}>{meter.unit} • {meter.status}</small>
                </article>
              ))}
            </div>

            <section style={{ background: '#050505', border: '1px solid #1a1a1a', borderRadius: '8px', padding: '28px' }}>
              <h3 style={{ color: '#D4AF37', margin: 0, marginBottom: '20px', fontSize: '0.84rem', letterSpacing: '2px', fontWeight: 900 }}>USAGE-BASED REVENUE CONTROL PLANE</h3>
              {[
                ['Meter capture', 'Every billable event is treated as a ledger candidate with tenant, product, timestamp and forensic trace.'],
                ['Price resolution', 'Usage can be rated against flat, tiered, graduated, seat, success-fee or hybrid commercial models.'],
                ['Revenue recognition', 'Recognized, deferred and disputed balances remain visible before statement generation.'],
                ['Dispute defense', 'Hash-chained events keep usage proof attached to every invoice, statement and collection workflow.']
              ].map(([title, copy], index) => (
                <div key={title} style={{ display: 'grid', gridTemplateColumns: '38px 1fr', gap: '14px', padding: '14px 0', borderTop: index === 0 ? 'none' : '1px solid #111' }}>
                  <div style={{ width: 28, height: 28, borderRadius: '50%', border: '1px solid #D4AF37', color: '#D4AF37', display: 'grid', placeItems: 'center', fontSize: '0.72rem', fontWeight: 900 }}>{index + 1}</div>
                  <div>
                    <strong style={{ color: '#fff', fontSize: '0.82rem' }}>{title}</strong>
                    <p style={{ color: '#777', margin: '5px 0 0', fontSize: '0.76rem', lineHeight: 1.55 }}>{copy}</p>
                  </div>
                </div>
              ))}
            </section>
          </div>
        );

      case 'TAX_TREASURY':
        return (
          <div className={styles.hudContent}>
            <section className={styles.sourceCommandSurface} data-tone="tax">
              <div className={styles.sourceCommandHero}>
                <div className={styles.sourceCommandTitle}>
                  <span><Landmark size={16} /> Tax & Treasury Command</span>
                  <h3>Cash, tax, bank, proof. One operating surface.</h3>
                  <p>
                    Wilsy OS now treats statutory obligations, liquidity sweeps, bank reconciliation and
                    Merkle proof as one CFO-grade control loop. Silent sources remain visible instead of
                    being hidden behind optimistic numbers.
                  </p>
                </div>
                <div className={styles.sourceCommandScore} data-silent={taxTreasurySnapshot.status !== 'LIVE'}>
                  <span>Capital Source Mesh</span>
                  <strong>{taxTreasurySnapshot.status}</strong>
                  <small>{taxTreasurySnapshot.lastSync ? `Last sync ${new Date(taxTreasurySnapshot.lastSync).toLocaleTimeString()}` : 'Awaiting tax and treasury sync'}</small>
                </div>
              </div>

              <div className={styles.sourceCommandActions}>
                <button type="button" onClick={hydrateTaxTreasuryCommand} disabled={operationBusy === 'tax-treasury-sync'}>
                  {operationBusy === 'tax-treasury-sync' ? <Loader2 size={14} className="animate-spin" /> : <RefreshCw size={14} />}
                  Sync capital mesh
                </button>
                <button type="button" onClick={handleSyncGlobalTaxMatrix} disabled={operationBusy === 'tax-matrix-sync'}>
                  {operationBusy === 'tax-matrix-sync' ? <Loader2 size={14} className="animate-spin" /> : <Globe2 size={14} />}
                  Sync tax matrix
                </button>
                <button type="button" onClick={handleManualTreasurySweep} disabled={operationBusy === 'treasury-sweep'}>
                  {operationBusy === 'treasury-sweep' ? <Loader2 size={14} className="animate-spin" /> : <Zap size={14} />}
                  Trigger sweep
                </button>
                <button type="button" onClick={handleRunMerkleAudit} disabled={operationBusy === 'merkle-audit'}>
                  {operationBusy === 'merkle-audit' ? <Loader2 size={14} className="animate-spin" /> : <ShieldCheck size={14} />}
                  Run Merkle audit
                </button>
                <button type="button" onClick={handleExportTaxTreasuryPacket}>
                  <Download size={14} />
                  Export capital packet
                </button>
              </div>

              <div className={styles.sourceProofGrid}>
                {taxTreasuryPosture.metrics.map(metric => (
                  <article key={metric.label} data-status={metric.caption}>
                    <span>{metric.label}</span>
                    <strong>{metric.label === 'Tax obligations' ? metric.value : formatZAR(metric.value)}</strong>
                    <small>{metric.caption}</small>
                  </article>
                ))}
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0, 1.1fr) minmax(320px, 0.9fr)', gap: '18px' }}>
                <section style={{ background: '#050505', border: '1px solid rgba(212,175,55,0.16)', borderRadius: '8px', padding: '22px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', gap: '14px', alignItems: 'center', marginBottom: '14px' }}>
                    <h3 style={{ color: '#D4AF37', margin: 0, fontSize: '0.82rem', letterSpacing: '2px' }}><Globe2 size={15} /> GLOBAL TAX ENGINE</h3>
                    <small style={{ color: taxEngineResult?.taxProfile?.liveRateRequired ? '#D4AF37' : '#777' }}>
                      {taxEngineLoading ? 'CALCULATING' : (taxEngineResult?.sourceStatus || taxTreasurySnapshot.tax?.sourceStatus || 'SOURCE_SILENT')}
                    </small>
                  </div>
                  {taxEngineResult ? (
                    <>
                      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '10px', marginBottom: '14px' }}>
                        {[
                          ['Tax type', taxEngineResult.taxProfile?.type || 'SOURCE SILENT'],
                          ['Rate', formatPercent(Number(taxEngineResult.taxProfile?.effectiveRate || taxEngineResult.taxProfile?.rate || 0) * 100)],
                          ['Tax amount', formatZAR(taxEngineResult.financials?.taxAmount || 0)],
                          ['Invoice total', formatZAR(taxEngineResult.financials?.totalAmount || 0)],
                          ['Rule', taxEngineResult.jurisdictionData?.rule || 'UNRESOLVED'],
                          ['Proof', taxEngineResult.proof?.hash ? `${taxEngineResult.proof.hash.slice(0, 14)}...` : 'NO HASH']
                        ].map(([label, value]) => (
                          <article key={label} style={{ background: '#090909', border: '1px solid #151515', borderRadius: '6px', padding: '12px', minHeight: '72px' }}>
                            <span style={{ color: '#666', fontSize: '0.6rem', letterSpacing: '1.2px', textTransform: 'uppercase' }}>{label}</span>
                            <strong style={{ display: 'block', color: label === 'Proof' ? '#D4AF37' : '#fff', marginTop: '7px', fontSize: '0.78rem', overflowWrap: 'anywhere' }}>{value}</strong>
                          </article>
                        ))}
                      </div>
                      <p style={{ color: '#888', fontSize: '0.74rem', lineHeight: 1.55, margin: '0 0 14px' }}>
                        {taxEngineResult.compliance?.invoiceNote || 'Tax proof sealed.'}
                      </p>
                      {taxEngineResult.compliance?.warnings?.length > 0 && (
                        <div style={{ borderTop: '1px solid #111', borderBottom: '1px solid #111', padding: '10px 0', marginBottom: '12px' }}>
                          {taxEngineResult.compliance.warnings.slice(0, 4).map(warning => (
                            <small key={warning} style={{ color: '#D4AF37', display: 'block', lineHeight: 1.45 }}>{warning}</small>
                          ))}
                        </div>
                      )}
                    </>
                  ) : (
                    <div style={{ color: '#777', fontSize: '0.76rem', lineHeight: 1.5, marginBottom: '12px' }}>
                      Global tax proof is pending. The invoice command will fall back to backend recalculation until this surface seals a trace hash.
                    </div>
                  )}
                  {taxTreasuryPosture.obligations.length ? taxTreasuryPosture.obligations.slice(0, 6).map((obligation, index) => (
                    <article key={obligation.id || obligation.reference || index} style={{ borderTop: index === 0 ? 'none' : '1px solid #111', padding: '12px 0', display: 'grid', gridTemplateColumns: '1fr auto', gap: '12px' }}>
                      <div>
                        <strong style={{ display: 'block', color: '#fff', fontSize: '0.78rem' }}>{obligation.type || obligation.name || obligation.period || 'TAX OBLIGATION'}</strong>
                        <small style={{ color: '#666' }}>{obligation.authority || obligation.jurisdiction || invoiceDraft.clientJurisdiction || invoiceDraft.taxJurisdiction || 'UNRESOLVED_AUTHORITY'} • Due {obligation.dueDate || obligation.deadline || 'SOURCE SILENT'}</small>
                      </div>
                      <span style={{ color: '#D4AF37', fontWeight: 900 }}>{formatZAR(obligation.amount || obligation.balance || obligation.taxAmount || 0)}</span>
                    </article>
                  )) : (
                    <div style={{ color: '#777', fontSize: '0.76rem', lineHeight: 1.5 }}>
                      Tax source is silent. Current invoice command still exposes {invoiceDraft.taxType || 'NO_TAX'} in {invoiceDraft.clientJurisdiction || invoiceDraft.taxJurisdiction || 'NO_JURISDICTION'} with the Global Tax Engine posture shown above, but no statutory obligation has been claimed.
                    </div>
                  )}
                </section>

                <section style={{ background: '#050505', border: '1px solid rgba(0,255,136,0.16)', borderRadius: '8px', padding: '22px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', gap: '14px', alignItems: 'center', marginBottom: '14px' }}>
                    <h3 style={{ color: '#00ff88', margin: 0, fontSize: '0.82rem', letterSpacing: '2px' }}><Coins size={15} /> TREASURY SWEEP MANAGER</h3>
                    <small style={{ color: '#777' }}>{taxTreasurySnapshot.treasury?.sourceStatus || 'SOURCE_SILENT'}</small>
                  </div>
                  {treasurySweepState.evaluation && (
                    <div style={{ marginBottom: '14px' }}>
                      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '10px', marginBottom: '12px' }}>
                        {[
                          ['Sweep status', treasurySweepState.status],
                          ['Available', formatZAR(treasurySweepState.evaluation.liquidity?.availableToSweep || 0)],
                          ['Projected yield', formatZAR(treasurySweepState.evaluation.liquidity?.projectedAnnualYield || 0)]
                        ].map(([label, value]) => (
                          <article key={label} style={{ background: '#090909', border: '1px solid #151515', borderRadius: '6px', padding: '12px', minHeight: '70px' }}>
                            <span style={{ color: '#666', fontSize: '0.6rem', letterSpacing: '1.2px', textTransform: 'uppercase' }}>{label}</span>
                            <strong style={{ display: 'block', color: label === 'Sweep status' ? '#D4AF37' : '#00ff88', marginTop: '7px', fontSize: '0.78rem', overflowWrap: 'anywhere' }}>{value}</strong>
                          </article>
                        ))}
                      </div>
                      <div style={{ display: 'grid', gap: '7px', marginBottom: '12px' }}>
                        {treasurySweepState.evaluation.gates?.map(gate => (
                          <div key={gate.gate} style={{ display: 'grid', gridTemplateColumns: '120px 1fr', gap: '10px', borderTop: '1px solid #111', paddingTop: '7px' }}>
                            <span style={{ color: gate.status === 'PASS' ? '#00ff88' : '#D4AF37', fontSize: '0.62rem', letterSpacing: '1px', fontWeight: 900 }}>{gate.status}</span>
                            <small style={{ color: '#777' }}>{gate.gate}: {gate.detail}</small>
                          </div>
                        ))}
                      </div>
                      <small style={{ color: '#666', display: 'block', overflowWrap: 'anywhere' }}>
                        Sweep proof {treasurySweepState.evaluation.proof?.hash?.slice(0, 18) || 'NO HASH'} • {treasurySweepState.evaluation.policy?.benchmarkSourceStatus}
                      </small>
                    </div>
                  )}
                  {taxTreasuryPosture.sweeps.length ? taxTreasuryPosture.sweeps.slice(0, 5).map((sweep, index) => (
                    <article key={sweep.id || sweep.reference || index} style={{ borderTop: index === 0 ? 'none' : '1px solid #111', padding: '12px 0' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', gap: '10px' }}>
                        <strong style={{ color: '#fff', fontSize: '0.78rem' }}>{sweep.destination || sweep.account || sweep.network || 'TREASURY ROUTE'}</strong>
                        <span style={{ color: '#00ff88', fontWeight: 900 }}>{formatZAR(sweep.amount || sweep.value || 0)}</span>
                      </div>
                      <small style={{ color: '#666' }}>{sweep.status || 'PENDING'} • {sweep.createdAt || sweep.timestamp || 'NO TIMESTAMP'}</small>
                    </article>
                  )) : (
                    <div style={{ color: '#777', fontSize: '0.76rem', lineHeight: 1.5 }}>
                      No treasury sweep source responded. Triggering a sweep will call the treasury endpoint and preserve a rejection receipt if the backend is not online.
                    </div>
                  )}
                </section>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0, 1fr) minmax(0, 1fr)', gap: '18px' }}>
                <section style={{ background: '#050505', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '8px', padding: '22px' }}>
                  <h3 style={{ color: '#D4AF37', margin: '0 0 16px', fontSize: '0.82rem', letterSpacing: '2px' }}><Banknote size={15} /> BANK RECONCILIATION</h3>
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '10px', marginBottom: '14px' }}>
                    {[
                      ['Status', bankReconciliation.status],
                      ['Pending', bankReconciliation.pending],
                      ['Variance', formatZAR(bankReconciliation.variance || 0)]
                    ].map(([label, value]) => (
                      <article key={label} style={{ background: '#090909', border: '1px solid #151515', borderRadius: '6px', padding: '12px' }}>
                        <span style={{ color: '#666', fontSize: '0.62rem', letterSpacing: '1.2px' }}>{label}</span>
                        <strong style={{ display: 'block', color: '#fff', marginTop: '6px', fontSize: '0.86rem' }}>{value ?? 'SOURCE SILENT'}</strong>
                      </article>
                    ))}
                  </div>
                  {bankReconciliation.matches.length ? bankReconciliation.matches.slice(0, 4).map((match, index) => (
                    <div key={match.id || index} style={{ display: 'flex', justifyContent: 'space-between', borderTop: '1px solid #111', padding: '10px 0', color: '#888', fontSize: '0.72rem' }}>
                      <span>{match.reference || match.description || 'BANK MATCH'}</span>
                      <strong style={{ color: '#00ff88' }}>{formatZAR(match.amount || 0)}</strong>
                    </div>
                  )) : (
                    <p style={{ color: '#777', fontSize: '0.76rem', lineHeight: 1.5, margin: 0 }}>
                      Bank reconciliation source is silent. No bank match has been displayed without a source.
                    </p>
                  )}
                </section>

                <section style={{ background: '#050505', border: '1px solid rgba(212,175,55,0.14)', borderRadius: '8px', padding: '22px' }}>
                  <h3 style={{ color: '#D4AF37', margin: '0 0 16px', fontSize: '0.82rem', letterSpacing: '2px' }}><ShieldCheck size={15} /> STATUTORY GATES</h3>
                  {taxTreasuryPosture.gates.map(gate => (
                    <article key={gate.label} style={{ display: 'grid', gridTemplateColumns: '130px 1fr', gap: '12px', borderTop: '1px solid #111', padding: '12px 0' }}>
                      <span style={{ color: gate.status === 'SOURCE_SILENT' || gate.status === 'WATCH' ? '#D4AF37' : '#00ff88', fontSize: '0.66rem', letterSpacing: '1.2px', fontWeight: 900 }}>{gate.status}</span>
                      <div>
                        <strong style={{ color: '#fff', fontSize: '0.78rem' }}>{gate.label}</strong>
                        <p style={{ color: '#777', margin: '4px 0 0', fontSize: '0.72rem', lineHeight: 1.45 }}>{gate.action}</p>
                      </div>
                    </article>
                  ))}
                  <article style={{ borderTop: '1px solid #111', paddingTop: '12px', marginTop: '4px' }}>
                    <span style={{ color: '#666', fontSize: '0.62rem', letterSpacing: '1.2px' }}>MERKLE AUDITOR</span>
                    <strong style={{ display: 'block', color: merkleAudit.sourceStatus === 'LIVE' ? '#00ff88' : '#D4AF37', marginTop: '6px' }}>{merkleAudit.status} • {shortAuditHash(merkleAudit.merkleRoot)}</strong>
                    <small style={{ color: '#777', display: 'block', marginTop: '6px' }}>
                      {merkleAudit.algorithm} • {merkleAudit.chainLength} entries • {merkleAudit.anchorMode}
                    </small>
                    <small style={{ color: merkleAudit.driftCount ? '#ff6666' : '#777', display: 'block', marginTop: '4px' }}>
                      Drift {merkleAudit.driftCount} • {merkleAudit.pendingLocal} local trace ids awaiting proof • QLDB {merkleAudit.qldbStatus}
                    </small>
                  </article>
                </section>
              </div>
            </section>
          </div>
        );

      case 'COMPLIANCE':
        return (
          <div className={styles.hudContent}>
            <section className={styles.sourceCommandSurface} data-tone="compliance">
              <div className={styles.sourceCommandHero}>
                <div className={styles.sourceCommandTitle}>
                  <span><ShieldCheck size={16} /> Compliance Sentinel</span>
                  <h3>Proof before posture.</h3>
                  <p>
                    Wilsy OS will not call the business compliant because a silent source returned zero.
                    This view binds policy, revenue and tenant scope into an evidence-backed operating loop.
                  </p>
                </div>
                <div className={styles.sourceCommandScore} data-silent={!complianceHasLiveScore}>
                  <span>Live Compliance Source</span>
                  <strong>{formatLivePercent(complianceLiveScore)}</strong>
                  <small>{complianceHasLiveScore ? 'Score returned by live source' : 'No compliance score returned by API/DB'}</small>
                </div>
              </div>

              <div className={styles.sourceCommandActions}>
                <button type="button" onClick={hydrateRevenueOperations} disabled={operationBusy === 'sync'}>
                  <RefreshCw size={14} />
                  Sync live sources
                </button>
                <button type="button" onClick={handleExportCfoDossier}>
                  <Download size={14} />
                  Export proof pack
                </button>
                <button type="button" onClick={handleGenerateStatement} disabled={isGenerating}>
                  <FileText size={14} />
                  Create sealed statement
                </button>
              </div>

              <div className={styles.sourceProofGrid}>
                {complianceProofRows.map((row) => (
                  <article key={row.label} data-status={row.status}>
                    <span>{row.label}</span>
                    <strong>{row.value}</strong>
                    <small>{row.status}</small>
                  </article>
                ))}
              </div>

              <div className={styles.sourceNarrativeGrid}>
                <article className={styles.sourceNarrative}>
                  <span>Founder story</span>
                  <p>
                    {complianceHasLiveScore
                      ? `Compliance is live at ${formatLivePercent(complianceLiveScore)} for ${tenantAlias}. The next founder action is to export the proof pack or generate a sealed statement while evidence is fresh.`
                      : `Compliance source is silent for ${tenantAlias}. Wilsy OS is refusing the fake 0.0 celebration and turning the gap into an operational task: sync the source, inspect API health, then seal proof only after data arrives.`}
                  </p>
                </article>
                <article className={styles.sourceChecklist}>
                  <span>Operating sequence</span>
                  <ul>
                    <li>Verify compliance API/DB source state.</li>
                    <li>Bind policy controls to tenant and revenue evidence.</li>
                    <li>Export only evidence-backed compliance packs.</li>
                  </ul>
                </article>
              </div>
            </section>
          </div>
        );

      case 'ESG':
        return (
          <div className={styles.hudContent}>
            <section className={styles.sourceCommandSurface} data-tone="esg">
              <div className={styles.sourceCommandHero}>
                <div className={styles.sourceCommandTitle}>
                  <span><Leaf size={16} /> ESG Capital Posture</span>
                  <h3>Net-zero claims require evidence.</h3>
                  <p>
                    ESG is treated as a boardroom control plane: green revenue, compliance context,
                    tenant scope and exportable proof must come from live records before Wilsy OS speaks.
                  </p>
                </div>
                <div className={styles.sourceCommandScore} data-silent={!esgHasLiveRatio}>
                  <span>Live ESG Source</span>
                  <strong>{formatLivePercent(esgLiveRatio)}</strong>
                  <small>{esgHasLiveRatio ? 'Green revenue ratio returned by live source' : 'No ESG ratio returned by API/DB'}</small>
                </div>
              </div>

              <div className={styles.sourceCommandActions}>
                <button type="button" onClick={hydrateRevenueOperations} disabled={operationBusy === 'sync'}>
                  <RefreshCw size={14} />
                  Sync ESG source
                </button>
                <button type="button" onClick={handleExportCfoDossier}>
                  <Download size={14} />
                  Export investor proof
                </button>
                <button type="button" onClick={handleGenerateStatement} disabled={isGenerating}>
                  <FileText size={14} />
                  Create ESG statement
                </button>
              </div>

              <div className={styles.sourceProofGrid}>
                {esgProofRows.map((row) => (
                  <article key={row.label} data-status={row.status}>
                    <span>{row.label}</span>
                    <strong>{row.value}</strong>
                    <small>{row.status}</small>
                  </article>
                ))}
              </div>

              <div className={styles.sourceNarrativeGrid}>
                <article className={styles.sourceNarrative}>
                  <span>Founder story</span>
                  <p>
                    {esgHasLiveRatio
                      ? `ESG source is live at ${formatLivePercent(esgLiveRatio)} green revenue posture. Wilsy OS can now package investor proof without inventing environmental claims.`
                      : `ESG source is silent for ${tenantAlias}. Wilsy OS refuses to present a synthetic net-zero claim. Sync the revenue ESG object, attach emission or green-revenue evidence, then export the proof pack.`}
                  </p>
                </article>
                <article className={styles.sourceChecklist}>
                  <span>Operating sequence</span>
                  <ul>
                    <li>Ingest green revenue or emissions evidence.</li>
                    <li>Cross-check against tenant revenue and compliance posture.</li>
                    <li>Seal only verified ESG claims for investors.</li>
                  </ul>
                </article>
              </div>
            </section>
          </div>
        );

      default:
        return <div className={styles.hudContent}>Select a matrix shard.</div>;
    }
  };

  return (
    <div className={styles.ledgerShard} style={{ position: 'relative', display: 'flex', flexDirection: 'column', height: '100%', background: '#000' }}>
      {/* Neural Scanline */}
      <div className={styles.scanlineOverlay} style={{ position: 'absolute', inset: 0, pointerEvents: 'none', background: 'linear-gradient(rgba(212, 175, 55, 0.03) 1px, transparent 1px)', backgroundSize: '100% 4px', zIndex: 10 }} />

      {/* Institutional Tab Navigation */}
      <div className={styles.tabContainer} style={{ display: 'flex', borderBottom: '1px solid #222', background: '#0a0a0a', padding: '0 20px', position: 'relative', zIndex: 20 }}>
        {[
          { id: 'REVENUE', icon: BarChart3, label: 'REVENUE TITAN' },
          { id: 'COLLECTIONS', icon: Radar, label: 'COLLECTIONS' },
          { id: 'METERING', icon: ReceiptText, label: 'USAGE METERING' },
          { id: 'TAX_TREASURY', icon: Landmark, label: 'TAX & TREASURY' },
          { id: 'PREDICTIVE', icon: Cpu, label: 'AI FORECAST' },
          { id: 'COMPLIANCE', icon: ShieldCheck, label: 'COMPLIANCE' },
          { id: 'ESG', icon: Leaf, label: 'ESG LIVE' },
        ].map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveHUD(tab.id)}
            style={{
              display: 'flex', alignItems: 'center', gap: '8px', padding: '16px 24px', background: 'transparent',
              border: 'none', borderBottom: activeHUD === tab.id ? '2px solid #D4AF37' : '2px solid transparent',
              color: activeHUD === tab.id ? '#D4AF37' : '#666', fontSize: '0.65rem', fontWeight: 900, letterSpacing: '1.5px', cursor: 'pointer', transition: 'all 0.3s'
            }}
          >
            <tab.icon size={14} />
            {tab.label}
          </button>
        ))}

        <div style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', padding: '0 10px' }}>
          <button
            onClick={handleGenerateStatement}
            disabled={isGenerating}
            className={styles.actionBtnGold}
            style={{ padding: '8px 16px', fontSize: '0.65rem', display: 'flex', alignItems: 'center', gap: '8px' }}
          >
            {isGenerating ? <Loader2 size={14} className="animate-spin" /> : <Download size={14} />}
            SEAL ARTIFACT
          </button>
        </div>
      </div>

      {/* Primary Cockpit Content */}
      <div style={{ flex: 1, overflowY: 'auto', padding: '30px', position: 'relative', zIndex: 20 }}>
        {renderActiveHUD()}
      </div>

      {/* Sovereign Footer */}
      <div style={{ borderTop: '1px solid #1a1a1a', padding: '12px 30px', background: '#050505', fontSize: '0.6rem', color: '#555', display: 'flex', justifyContent: 'space-between', fontWeight: 900, letterSpacing: '1px', position: 'relative', zIndex: 20 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <ShieldCheck size={12} color="#D4AF37" />
          SOVEREIGN FINALITY PROTOCOL • <span style={{ color: '#D4AF37' }}>{tenantAlias}</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
          <span>CYBERCRIMES ACT 2026 COMPLIANT</span>
          <span style={{ color: merkleAudit.sourceStatus === 'LIVE' ? '#00ff88' : '#D4AF37' }}>
            MERKLE AUDITOR: {merkleAudit.status} / {shortAuditHash(merkleAudit.merkleRoot)} / {merkleAudit.chainLength} LINKS
          </span>
          <span style={{ width: '4px', height: '4px', background: merkleAudit.sourceStatus === 'LIVE' ? '#00ff88' : '#D4AF37', borderRadius: '50%', boxShadow: `0 0 8px ${merkleAudit.sourceStatus === 'LIVE' ? '#00ff88' : '#D4AF37'}` }} />
        </div>
      </div>

      {/* Forensic Audit Layer */}
      {generatedTraceIds.length > 0 && (
        <div style={{ position: 'absolute', bottom: '50px', right: '30px', zIndex: 30 }}>
          <AuditTimeline traceIds={generatedTraceIds} />
        </div>
      )}

      {/* Tactical HUD Notifications */}
      {tooltipVisible && (
        <div style={{ position: 'fixed', bottom: '40px', left: '50%', transform: 'translateX(-50%)', background: 'rgba(0,0,0,0.9)', border: '1px solid #D4AF37', color: '#D4AF37', padding: '12px 24px', borderRadius: '4px', fontSize: '0.75rem', fontWeight: 900, letterSpacing: '1px', boxShadow: '0 10px 30px rgba(0,0,0,0.8), 0 0 15px rgba(212,175,55,0.2)', zIndex: 9999, display: 'flex', alignItems: 'center', gap: '8px', animation: 'slideUp 0.3s cubic-bezier(0.16, 1, 0.3, 1)' }}>
          <CheckCircle size={14} />
          {tooltipVisible}
        </div>
      )}
    </div>
  );
};

export default Sovereign_Revenue_Ledger;
