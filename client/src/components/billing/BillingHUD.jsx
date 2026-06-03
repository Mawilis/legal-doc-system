/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - BILLING NUCLEUS HUD [V56.3.0-PRODUCTION-EPITOME]                                                                          ║
 * ║ [DETERMINISTIC INVOICE GOVERNANCE | GLOBAL TAX ROUTING | TREASURY SWEEP | NEURAL DUNNING | COURT REGISTRY WAR ROOM]                  ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 56.3.0-PRODUCTION-EPITOME | PRODUCTION READY | MULTI-TENANT SOVEREIGN SAAS BILLING COMMAND                                 ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/components/billing/BillingHUD.jsx                                    ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                    ║
 * ║ • Wilson Khanyezi (CEO/Lead Architect) - Required BillingHUD to become the nucleus of Wilsy OS revenue: sealed commands,              ║
 * ║   idempotency, global tax sovereignty, treasury motion, neural dunning and court-ready collections.                                    ║
 * ║ • AI Engineering (Codex) - ARCHITECTED: Integrated GlobalTaxEngine, TreasurySweepManager and DunningIntelligence into the HUD,         ║
 * ║   added deterministic command envelopes, source coverage scoring, proof hashes and production guardrails.                             ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { sha3_512 } from 'js-sha3';
import {
  AlertOctagon,
  AlertTriangle,
  BadgeCheck,
  Banknote,
  BarChart3,
  Calendar,
  CheckCircle,
  Clock,
  Coins,
  CopyCheck,
  Crosshair,
  Download,
  FileText,
  Gavel,
  Gauge,
  Globe2,
  Landmark,
  Mail,
  PlusCircle,
  RefreshCw,
  Scale,
  Search,
  ShieldCheck,
  Sparkles,
  Target,
  TrendingUp,
  Users,
  Zap
} from 'lucide-react';
import { useAuth } from '../../contexts/authContext';
import { useTenants } from '../../contexts/tenantContext';
import { useSovereignMesh } from '../sovereign/SovereignOrchestrator';
import { useSovereignData } from '../sovereign/DataOrchestrator';
import sovereignClient from '../../utils/sovereignClient';
import { broadcastTelemetry } from '../../utils/telemetryHelper';
import globalTaxEngine from '../../services/GlobalTaxEngine';
import treasurySweepManager from '../../services/TreasurySweepManager';
import dunningIntelligence from '../../services/DunningIntelligence';
import hudStyles from './BillingHUD.module.css';

const CURRENCY_FORMATTERS = {};

const CURRENCY_EXPONENTS = Object.freeze({
  BHD: 3,
  JOD: 3,
  KWD: 3,
  OMR: 3,
  TND: 3,
  CLP: 0,
  JPY: 0,
  KRW: 0,
  UGX: 0,
  VND: 0,
  XAF: 0,
  XOF: 0,
  ZAR: 2,
  USD: 2,
  EUR: 2,
  GBP: 2,
  NGN: 2,
  KES: 2,
  GHS: 2,
  BWP: 2,
  NAD: 2,
  MUR: 2
});

/**
 * @description Rounds money and ratios through integer-safe precision instead of naked floating-point math.
 * @param {number|string} value - Numeric value to round.
 * @param {number} decimals - Decimal precision.
 * @returns {number} Precisely rounded value.
 * @collaboration Wilson Khanyezi required BillingHUD calculations to behave like a finance system, not JavaScript theatre.
 */
const preciseRound = (value = 0, decimals = 2) => {
  const numeric = Number(value || 0);
  if (!Number.isFinite(numeric)) return 0;
  const factor = 10 ** decimals;
  return Math.round((numeric + Number.EPSILON) * factor) / factor;
};

/**
 * @description Resolves ISO currency minor-unit precision for deterministic invoice math.
 * @param {string} currency - ISO currency code.
 * @returns {number} Minor-unit exponent.
 * @collaboration Keeps cents, yen-style zero-decimal currencies, and high-precision currencies explicit.
 */
const getCurrencyExponent = (currency = 'ZAR') => CURRENCY_EXPONENTS[String(currency || 'ZAR').toUpperCase()] ?? 2;

/**
 * @description Converts display money into minor units so invoice line totals cannot drift.
 * @param {number|string} value - Display amount.
 * @param {string} currency - ISO currency code.
 * @returns {number} Integer minor units.
 * @collaboration Makes manual invoice entry compatible with institutional reconciliation.
 */
const toBillingMinorUnits = (value = 0, currency = 'ZAR') => {
  const factor = 10 ** getCurrencyExponent(currency);
  return Math.round(Number(value || 0) * factor);
};

/**
 * @description Converts minor-unit money back into display units.
 * @param {number|string} value - Minor-unit amount.
 * @param {string} currency - ISO currency code.
 * @returns {number} Display amount.
 * @collaboration Gives the HUD deterministic money values without leaking integer implementation details.
 */
const fromBillingMinorUnits = (value = 0, currency = 'ZAR') => {
  const factor = 10 ** getCurrencyExponent(currency);
  return preciseRound(Number(value || 0) / factor, getCurrencyExponent(currency));
};

/**
 * @description Serializes command packets with deterministic object-key order for repeatable proof hashes.
 * @param {unknown} value - Value to serialize.
 * @returns {string} Canonical JSON string.
 * @collaboration Billing receipts must survive reloads and replays with the same cryptographic answer.
 */
const stableBillingStringify = (value) => {
  if (typeof value === 'undefined') return 'null';
  if (value instanceof Date) return JSON.stringify(value.toISOString());
  if (value === null || typeof value !== 'object') return JSON.stringify(value);
  if (Array.isArray(value)) return `[${value.map(item => stableBillingStringify(item)).join(',')}]`;
  return `{${Object.keys(value).sort().map(key => `${JSON.stringify(key)}:${stableBillingStringify(value[key])}`).join(',')}}`;
};

/**
 * @description Creates a SHA3-512 proof hash for a billing command envelope.
 * @param {Object} payload - Command payload.
 * @returns {string} Uppercase SHA3-512 digest.
 * @collaboration Every BillingHUD action should produce proof, even before the backend receipt returns.
 */
const createBillingProofHash = (payload = {}) => sha3_512(stableBillingStringify(payload)).toUpperCase();

/**
 * @description Creates an idempotency key for duplicate-safe invoice commands.
 * @param {string} tenantId - Tenant or root authority issuing the command.
 * @returns {string} Idempotency key.
 * @collaboration Distributed billing must tolerate duplicate network packets without duplicating ledger state.
 */
const createBillingIdempotencyKey = (tenantId = 'GLOBAL_ROOT') => {
  const entropy = globalThis.crypto?.randomUUID
    ? globalThis.crypto.randomUUID().slice(0, 12)
    : `${Date.now().toString(36)}${Math.random().toString(36).slice(2, 8)}`;
  return `WILSY-BILL-${String(tenantId || 'GLOBAL_ROOT').toUpperCase()}-${entropy.toUpperCase()}`;
};

/**
 * @description Returns a cached currency formatter so billing values render consistently without re-allocating Intl objects.
 * @param {string} currency - ISO currency code to format.
 * @returns {Intl.NumberFormat} Formatter bound to the requested currency.
 * @collaboration Wilson Khanyezi requires money in Wilsy OS to feel institutional, not improvised.
 */
const getCurrencyFormatter = (currency = 'ZAR') => {
  if (!CURRENCY_FORMATTERS[currency]) {
    CURRENCY_FORMATTERS[currency] = new Intl.NumberFormat('en-ZA', {
      style: 'currency',
      currency,
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    });
  }
  return CURRENCY_FORMATTERS[currency];
};

/**
 * @description Formats a numeric amount as institutional money while preserving zero as a truthful live value.
 * @param {number|string} amount - Amount from billing APIs or operator input.
 * @param {string} currency - ISO currency code.
 * @returns {string} Localized monetary display value.
 * @collaboration Prevents vague values inside the billing cockpit and invoices.
 */
const formatMoney = (amount = 0, currency = 'ZAR') => {
  const numeric = Number(amount || 0);
  try {
    return getCurrencyFormatter(currency).format(numeric);
  } catch {
    return `R ${numeric.toLocaleString('en-ZA', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  }
};

/**
 * @description Converts operator-entered invoice money into a rounded two-decimal number.
 * @param {string|number} value - Raw invoice amount from the command input.
 * @returns {number|null} Parsed money value or null when the input cannot become money.
 * @collaboration Wilson Khanyezi required invoice commands to behave like an institutional finance cockpit, not a raw browser number field.
 */
const parseBillingMoneyInput = (value) => {
  const numeric = Number(String(value ?? '').replace(/[^\d.-]/g, ''));
  return Number.isFinite(numeric) ? preciseRound(numeric, 2) : null;
};

/**
 * @description Sanitizes live invoice amount typing while preserving a decimal point during entry.
 * @param {string} value - Raw input value.
 * @returns {string} Money-safe value with at most two decimal places.
 * @collaboration Keeps the operator fast while preventing malformed values from reaching the billing API.
 */
const sanitizeBillingMoneyInput = (value = '') => {
  const cleaned = String(value).replace(/[^\d.]/g, '');
  if (!cleaned) return '';
  const hasDecimal = cleaned.includes('.');
  const [whole = '', ...decimalParts] = cleaned.split('.');
  const decimals = decimalParts.join('').slice(0, 2);
  return hasDecimal ? `${whole || '0'}.${decimals}` : whole;
};

/**
 * @description Formats an invoice amount field into fixed cents when the operator leaves the input.
 * @param {string|number} value - Current invoice amount field value.
 * @returns {string} Two-decimal money text or empty string when no value exists.
 * @collaboration Eliminates the unacceptable manual cent-zero burden from invoice creation.
 */
const formatBillingMoneyInput = (value) => {
  if (value === '' || value === null || value === undefined) return '';
  const amount = parseBillingMoneyInput(value);
  return amount === null ? '' : amount.toFixed(2);
};

/**
 * @description Formats an API date for the legal billing command surface.
 * @param {string|Date} value - Date-like value from an invoice, subscription or command.
 * @returns {string} Human-readable date or a declared unscheduled state.
 * @collaboration Keeps invoice timing explicit for founder and super-admin review.
 */
const formatDate = (value) => {
  if (!value) return 'Not scheduled';
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? value : date.toLocaleDateString('en-ZA', { year: 'numeric', month: 'short', day: '2-digit' });
};

/**
 * @description Builds the searchable label used by the court escalation picker.
 * @param {Object} court - Court registry row.
 * @returns {string} Court label shown in the picker.
 * @collaboration Court routing must be searchable and human-readable, not a dead dropdown.
 */
const formatCourtSearchLabel = (court = {}) => court.name || '';

/**
 * @description Normalizes court search text so jurisdiction, bloc and court-type searches behave predictably.
 * @param {string} value - Raw user search value.
 * @returns {string} Normalized searchable text.
 * @collaboration Enables the global legal registry workflow to behave like an operating system command, not a form.
 */
const normalizeCourtSearch = (value = '') => (
  value
    .split(' - ')[0]
    .replace(/[•|]/g, ' ')
    .replace(/\s+/g, ' ')
    .trim()
    .toLowerCase()
);

/**
 * @description Converts optional API arrays into clean lists.
 * @param {unknown} value - Candidate list from a live API payload.
 * @returns {Array} Non-empty list values.
 * @collaboration Keeps billing and court intelligence honest when fields are absent.
 */
const asList = (value) => Array.isArray(value) ? value.filter(Boolean) : [];

/**
 * @description Converts a settled API request into a source heartbeat row.
 * @param {PromiseSettledResult} result - Settled request result.
 * @param {string} label - Human label for the source.
 * @returns {{label:string,status:string,live:boolean,error:string|null}} Source heartbeat row.
 * @collaboration The founder should see exactly which billing sources are live and which refused to answer.
 */
const buildSourceHeartbeat = (result, label) => ({
  label,
  status: result?.status === 'fulfilled' ? 'LIVE' : 'SOURCE_SILENT',
  live: result?.status === 'fulfilled',
  error: result?.status === 'rejected'
    ? (result.reason?.response?.data?.message || result.reason?.message || 'SOURCE_SILENT')
    : null
});

/**
 * @description Produces a browser-safe ISO date offset from today.
 * @param {number} days - Days to offset from the current date.
 * @returns {string} ISO date string.
 * @collaboration Invoice issue and due dates must be generated from current time, never hard-coded.
 */
const getBillingIsoDateOffset = (days = 0) => {
  const date = new Date();
  date.setDate(date.getDate() + days);
  return date.toISOString().slice(0, 10);
};

/**
 * @description Extracts invoice rows from the mixed BillingHUD summary shapes.
 * @param {Object} summary - Billing summary payload.
 * @returns {Array<Object>} Invoice rows.
 * @collaboration Keeps the invoice ledger honest across legacy and sovereign endpoint envelopes.
 */
const extractBillingInvoices = (summary = {}) => {
  const candidates = [
    summary?.recentInvoices,
    summary?.invoices,
    summary?.data?.recentInvoices,
    summary?.data?.invoices
  ];
  const rows = candidates.find(Array.isArray);
  return Array.isArray(rows) ? rows : [];
};

/**
 * @description Builds the normalized invoice draft consumed by GlobalTaxEngine and the billing API.
 * @param {Object} manualInvoice - Operator invoice state.
 * @param {Object} params - Runtime context.
 * @param {string} params.issuerTenantId - Tenant issuing the command.
 * @param {string} params.recipientTenantId - Tenant receiving the invoice.
 * @param {number} params.amount - Net amount before tax.
 * @returns {Object} Normalized invoice draft.
 * @collaboration One invoice command should have one canonical fiscal shape across preview, API post and audit export.
 */
const buildManualInvoiceDraft = (manualInvoice = {}, { issuerTenantId = 'GLOBAL_ROOT', recipientTenantId = '', amount = 0 } = {}) => {
  const currency = String(manualInvoice.currency || 'ZAR').toUpperCase();
  const amountMinor = toBillingMinorUnits(amount, currency);
  const normalizedAmount = fromBillingMinorUnits(amountMinor, currency);
  const paymentTerms = Number(manualInvoice.paymentTerms || 30);
  const issueDate = manualInvoice.issueDate || getBillingIsoDateOffset(0);
  const dueDate = manualInvoice.dueDate || getBillingIsoDateOffset(paymentTerms);

  return {
    tenantId: recipientTenantId || manualInvoice.tenantId || issuerTenantId,
    issuerTenantId,
    recipientTenantId: recipientTenantId || manualInvoice.tenantId || '',
    clientId: recipientTenantId || manualInvoice.tenantId || 'UNRESOLVED_TENANT',
    amount: normalizedAmount,
    unitPrice: normalizedAmount,
    quantity: 1,
    currency,
    description: manualInvoice.description || 'WILSY OS sovereign infrastructure allocation',
    issueDate,
    dueDate,
    paymentTerms,
    billingPeriodStart: manualInvoice.billingPeriodStart || issueDate,
    billingPeriodEnd: manualInvoice.billingPeriodEnd || dueDate,
    invoiceClass: manualInvoice.invoiceClass || 'SOVEREIGN_INFRASTRUCTURE',
    billingModel: manualInvoice.supplyType || 'DIGITAL_SERVICE',
    supplyType: manualInvoice.supplyType || 'DIGITAL_SERVICE',
    taxType: manualInvoice.taxType || 'VAT',
    taxJurisdiction: manualInvoice.clientJurisdiction || 'ZA',
    tenantJurisdiction: manualInvoice.tenantJurisdiction || 'ZA',
    clientJurisdiction: manualInvoice.clientJurisdiction || 'ZA',
    clientType: manualInvoice.clientType || 'B2B',
    customerTaxId: manualInvoice.customerTaxId || '',
    idempotencyKey: manualInvoice.idempotencyKey || createBillingIdempotencyKey(issuerTenantId),
    minorUnits: {
      amount: amountMinor
    }
  };
};

/**
 * @description Builds a sealed Billing Nucleus command envelope for API submission and local receipts.
 * @param {Object} params - Envelope inputs.
 * @param {Object} params.draft - Normalized invoice draft.
 * @param {Object|null} params.taxResult - Tax engine result.
 * @param {Object|null} params.treasuryEvaluation - Treasury sweep evaluation.
 * @param {Object} params.sourceSnapshot - Source heartbeat snapshot.
 * @returns {Object} Command envelope with proof hash.
 * @collaboration Every BillingHUD invoice command becomes replayable business evidence before it leaves the browser.
 */
const buildBillingCommandEnvelope = ({ draft = {}, taxResult = null, treasuryEvaluation = null, sourceSnapshot = {} } = {}) => {
  const taxFinancials = taxResult?.financials || {};
  const payload = {
    commandType: 'SOVEREIGN_BILLING_INVOICE',
    commandVersion: 'V56.3.0-PRODUCTION-EPITOME',
    generatedAt: new Date().toISOString(),
    tenantId: draft.tenantId,
    issuerTenantId: draft.issuerTenantId,
    recipientTenantId: draft.recipientTenantId,
    idempotencyKey: draft.idempotencyKey,
    invoice: {
      amount: draft.amount,
      currency: draft.currency,
      description: draft.description,
      issueDate: draft.issueDate,
      dueDate: draft.dueDate,
      paymentTerms: draft.paymentTerms,
      invoiceClass: draft.invoiceClass,
      supplyType: draft.supplyType
    },
    tax: {
      traceId: taxResult?.traceId || null,
      proofHash: taxResult?.proof?.hash || null,
      sourceStatus: taxResult?.sourceStatus || 'SOURCE_SILENT',
      baseAmount: taxFinancials.baseAmount ?? draft.amount,
      taxAmount: taxFinancials.taxAmount ?? 0,
      totalAmount: taxFinancials.totalAmount ?? draft.amount,
      netPayableAmount: taxFinancials.netPayableAmount ?? taxFinancials.totalAmount ?? draft.amount,
      warnings: taxResult?.compliance?.warnings || []
    },
    treasury: {
      traceId: treasuryEvaluation?.traceId || null,
      status: treasuryEvaluation?.status || 'NOT_EVALUATED',
      availableToSweep: treasuryEvaluation?.liquidity?.availableToSweep || 0,
      proofHash: treasuryEvaluation?.proof?.hash || null
    },
    sources: sourceSnapshot?.sources || {}
  };

  return {
    ...payload,
    proof: {
      algorithm: 'SHA3-512',
      canonicalization: 'STABLE_JSON_KEY_SORT',
      hash: createBillingProofHash(payload),
      canonicalPayload: stableBillingStringify(payload)
    }
  };
};

/**
 * @description Builds the liquidity context used to evaluate treasury sweep readiness from billing state.
 * @param {Object} params - Revenue and receivable metrics.
 * @param {number} params.outstanding - Open receivable amount.
 * @param {number} params.totalArr - ARR amount.
 * @param {Object|null} params.taxResult - Tax engine result.
 * @returns {Object} Treasury evaluation context.
 * @collaboration Treasury automation must reserve tax and receivables before treating idle cash as deployable.
 */
const buildTreasuryContext = ({ outstanding = 0, totalArr = 0, taxResult = null } = {}) => ({
  pendingPayments: preciseRound(outstanding),
  recognizedRunRate: preciseRound(Number(totalArr || 0) / 12),
  monthlyBurnRate: preciseRound(Math.max(Number(totalArr || 0) / 18, Number(outstanding || 0) / 2, 10000)),
  taxReserve: preciseRound(taxResult?.financials?.taxAmount || 0),
  payrollReserve: 0,
  bankVariance: 0,
  varianceTolerance: 100,
  sourceAccount: 'BILLING_OPERATING_CORE'
});

/**
 * @description Forecasts ARR from live billing history using deterministic linear trend analysis.
 * @param {Array<Object>} history - Billing volume history from the API.
 * @returns {number} Annualized trend forecast.
 * @collaboration Replaces theatre with ledger-derived forecasting.
 */
const forecastARR = (history = []) => {
  const usable = history.filter(point => Number(point.volume || point.paidVolume || 0) > 0);
  if (usable.length < 2) return 0;
  const n = usable.length;
  const sumX = usable.reduce((sum, _, index) => sum + index, 0);
  const sumY = usable.reduce((sum, point) => sum + Number(point.volume || point.paidVolume || 0), 0);
  const sumXY = usable.reduce((sum, point, index) => sum + (index * Number(point.volume || point.paidVolume || 0)), 0);
  const sumXX = usable.reduce((sum, _, index) => sum + (index * index), 0);
  const slope = (n * sumXY - sumX * sumY) / Math.max(1, (n * sumXX - sumX * sumX));
  const intercept = (sumY - slope * sumX) / n;
  return Math.max(0, (intercept + slope * n) * 12);
};

/**
 * @description Creates a deterministic pseudo-random generator for replayable Monte Carlo simulations.
 * @param {number} seed - Integer seed.
 * @returns {Function} Generator returning a number from 0 to 1.
 * @collaboration Forecast risk should be stochastic enough to model volatility and deterministic enough to audit.
 */
const createSeededRandom = (seed = 1) => {
  let state = seed >>> 0;
  return () => {
    state += 0x6D2B79F5;
    let value = state;
    value = Math.imul(value ^ (value >>> 15), value | 1);
    value ^= value + Math.imul(value ^ (value >>> 7), value | 61);
    return ((value ^ (value >>> 14)) >>> 0) / 4294967296;
  };
};

/**
 * @description Computes cashflow risk from live billing history using deterministic Monte Carlo sampling.
 * @param {Array<Object>} history - Billing history from the API.
 * @param {number} threshold - Minimum healthy monthly inflow threshold.
 * @returns {number} Risk ratio from 0 to 1.
 * @collaboration Billing risk must model volatility while remaining reproducible in investor demos and audit trails.
 */
const monteCarloRisk = (history = [], threshold = 10000) => {
  const inflows = history.map(point => Number(point.paidVolume || point.volume || 0)).filter(value => value > 0);
  if (inflows.length < 3) return 0.32;
  const mean = inflows.reduce((sum, value) => sum + value, 0) / inflows.length;
  const variance = inflows.reduce((sum, value) => sum + Math.pow(value - mean, 2), 0) / inflows.length;
  const deviation = Math.sqrt(variance);
  const seed = inflows.reduce((sum, value, index) => sum + Math.round(value * (index + 1)), 97);
  const random = createSeededRandom(seed);
  const simulations = 420;
  let shortfalls = 0;

  for (let index = 0; index < simulations; index += 1) {
    const u1 = Math.max(random(), 0.000001);
    const u2 = random();
    const gaussian = Math.sqrt(-2 * Math.log(u1)) * Math.cos(2 * Math.PI * u2);
    const projectedMonthlyInflow = Math.max(0, mean + gaussian * deviation);
    if (projectedMonthlyInflow < threshold) shortfalls += 1;
  }

  const shortfallRatio = shortfalls / simulations;
  const overdueDrag = inflows.slice(-3).filter(value => value < threshold).length / 3;
  return preciseRound(Math.min(1, (shortfallRatio * 0.72) + (overdueDrag * 0.28)), 2);
};

/**
 * @description Maps invoice status into the visual tone used across settlement lanes.
 * @param {string} status - Invoice status from the billing ledger.
 * @returns {string} Normalized tone.
 * @collaboration Ensures invoices and disputes tell a consistent operational story.
 */
const getStatusTone = (status = '') => {
  const normalized = status.toUpperCase();
  if (normalized === 'PAID') return 'PAID';
  if (['OVERDUE', 'DISPUTED', 'LEGAL_HOLD'].includes(normalized)) return 'OVERDUE';
  return normalized || 'ISSUED';
};

/**
 * @description Derives a billing command doctrine from live API values.
 * @param {Object} params - Live billing metrics and command context.
 * @returns {Object} Readiness, source coverage and next action for the billing flight deck.
 * @collaboration Converts the Billing HUD from passive cards into a founder operating loop.
 */
const buildBillingFlightDeck = ({
  summary,
  analytics,
  invoices,
  creditScores,
  courts,
  logs,
  telemetry,
  taxEnginePreview,
  treasuryState,
  dunningState,
  sourceSnapshot,
  collectionEfficiency,
  riskScore,
  outstanding,
  totalArr,
  overdueInvoices
}) => {
  const snapshotSources = sourceSnapshot?.sources || {};
  const sourceIsLive = (key, fallback = false) => snapshotSources[key]?.live ?? fallback;
  const liveSources = [
    { key: 'SUMMARY', live: sourceIsLive('summary', Boolean(summary)), label: 'Billing summary' },
    { key: 'ANALYTICS', live: sourceIsLive('analytics', Boolean(analytics)), label: 'Billing analytics' },
    { key: 'INVOICES', live: sourceIsLive('summary', false) || extractBillingInvoices(summary || {}).length > 0, label: 'Invoice ledger' },
    { key: 'CREDIT', live: sourceIsLive('credit', Object.keys(creditScores || {}).length > 0), label: 'Credit mesh' },
    { key: 'COURTS', live: sourceIsLive('courts', courts.length > 0), label: 'Court registry' },
    { key: 'TELEMETRY', live: sourceIsLive('telemetry', telemetry.circuitBreaker !== 'DEGRADED'), label: 'Telemetry' },
    { key: 'TAX', live: Boolean(taxEnginePreview?.success), label: 'Global tax engine' },
    { key: 'TREASURY', live: treasuryState?.status !== 'SOURCE_SILENT', label: 'Treasury sweep' },
    { key: 'DUNNING', live: dunningState?.status !== 'SOURCE_SILENT', label: 'Neural dunning' }
  ];
  const sourceCount = liveSources.filter(source => source.live).length;
  const treasuryReady = treasuryState?.evaluation?.status === 'READY_FOR_EXECUTION' ? 1 : treasuryState?.evaluation ? 0.55 : 0;
  const dunningReady = (dunningState?.recommendations || []).some(item => item.gateStatus === 'READY') ? 1 : dunningState?.recommendations?.length ? 0.7 : 0;
  const taxReady = taxEnginePreview?.success && !taxEnginePreview?.taxProfile?.liveRateRequired ? 1 : taxEnginePreview?.success ? 0.65 : 0;
  const readiness = Math.round((
    (sourceCount / liveSources.length) * 32
    + Math.min(1, collectionEfficiency / 100) * 18
    + (riskScore < 0.45 ? 14 : riskScore < 0.7 ? 7 : 0)
    + (courts.length ? 8 : 0)
    + (logs.length ? 8 : 0)
    + (taxReady * 7)
    + (treasuryReady * 7)
    + (dunningReady * 6)
  ));
  const nextAction = overdueInvoices.length
    ? 'Run neural dunning, then route blocked or high-risk receivables into court registry escalation.'
    : outstanding > 0
      ? 'Review dunning gates and treasury reserve before investor proof export.'
      : taxEnginePreview?.taxProfile?.liveRateRequired
        ? 'Connect live tax rate source before sealing cross-border invoices.'
        : totalArr > 0
          ? 'Run monthly billing, evaluate treasury sweep, and export investor proof.'
          : 'Create the first idempotent sovereign invoice to activate revenue motion.';

  return {
    sourceCount,
    totalSources: liveSources.length,
    liveSources,
    readiness: Math.min(100, readiness),
    nextAction,
    posture: readiness >= 84 ? 'NUCLEUS_READY' : readiness >= 62 ? 'COMMANDABLE' : 'SOURCE_GAPS',
    sourceLabel: `${sourceCount}/${liveSources.length} live sources`
  };
};

const tabs = [
  { id: 'command', label: 'Command', icon: Landmark },
  { id: 'invoices', label: 'Invoices', icon: FileText },
  { id: 'sovereignty', label: 'Sovereignty', icon: Globe2 },
  { id: 'automation', label: 'Automation', icon: Zap },
  { id: 'warroom', label: 'War Room', icon: Gavel }
];

const settlementLanes = ['ISSUED', 'OVERDUE', 'PARTIALLY_PAID', 'PAID'];

const BillingHUD = () => {
  const { logout } = useAuth();
  const { activeTenant } = useTenants();
  const mesh = useSovereignMesh();
  const {
    eventBus,
    registerShard,
    unregisterShard
  } = mesh || {};
  const stream = useSovereignData();
  const tenantId = activeTenant?.id || activeTenant?.tenantId || 'GLOBAL_ROOT';
  const abortRef = useRef(null);

  const [activeTab, setActiveTab] = useState('command');
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [processing, setProcessing] = useState(null);
  const [error, setError] = useState(null);
  const [summary, setSummary] = useState(null);
  const [analytics, setAnalytics] = useState(null);
  const [creditScores, setCreditScores] = useState({});
  const [telemetry, setTelemetry] = useState({ circuitBreaker: 'CLOSED', avgLatencyMs: 0, forensicSeal: 'VERIFIED' });
  const [courts, setCourts] = useState([]);
  const [logs, setLogs] = useState([]);
  const [sourceSnapshot, setSourceSnapshot] = useState({ lastSync: null, sources: {} });
  const [taxEnginePreview, setTaxEnginePreview] = useState(null);
  const [taxPreviewBusy, setTaxPreviewBusy] = useState(false);
  const [treasuryState, setTreasuryState] = useState({
    status: 'SOURCE_SILENT',
    statusPacket: null,
    evaluation: null,
    lastReceipt: null,
    lastSync: null
  });
  const [dunningState, setDunningState] = useState({
    status: 'SOURCE_SILENT',
    recommendations: [],
    lastReceipt: null,
    lastSync: null,
    error: null
  });
  const [blockchainPreview, setBlockchainPreview] = useState(null);
  const [pricingResult, setPricingResult] = useState(null);
  const [competitiveResult, setCompetitiveResult] = useState(null);
  const [seizureResult, setSeizureResult] = useState(null);
  const [disputeModal, setDisputeModal] = useState({ open: false, invoiceId: '', reason: '' });

  const [manualInvoice, setManualInvoice] = useState({
    tenantId: '',
    amount: '',
    description: 'WILSY OS sovereign infrastructure allocation',
    currency: 'ZAR',
    paymentTerms: 30,
    tenantJurisdiction: 'ZA',
    clientJurisdiction: 'ZA',
    clientType: 'B2B',
    customerTaxId: '',
    supplyType: 'DIGITAL_SERVICE',
    taxType: 'VAT',
    idempotencyKey: createBillingIdempotencyKey(tenantId)
  });

  const [seizure, setSeizure] = useState({ invoiceId: '', reason: '', courtId: '' });
  const [pricing, setPricing] = useState({ tenantId: '', margin: 5 });
  const [invoiceSearch, setInvoiceSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [courtSearch, setCourtSearch] = useState('');
  const [courtRegistryStatus, setCourtRegistryStatus] = useState('STANDBY');

  /**
   * @description Adds a bounded command receipt to the local forensic activity stream.
   * @param {string} action - Command or failure label.
   * @param {string} result - Human-readable command outcome.
   * @returns {void}
   * @collaboration Billing operators need receipts for every action, even before server-side audit export.
   */
  const addLog = useCallback((action, result) => {
    setLogs(prev => [
      { action, result, timestamp: new Date().toISOString() },
      ...prev
    ].slice(0, 80));
  }, []);

  /**
   * @description Extracts API payloads from Wilsy OS response envelopes.
   * @param {Object} response - Axios response.
   * @returns {Object|Array} Extracted payload.
   * @collaboration Normalizes live billing endpoints without pretending missing data exists.
   */
  const extractData = (response) => response?.data?.data || response?.data || {};

  /**
   * @description Hydrates telemetry state for the active billing tenant.
   * @returns {Promise<void>} Resolves after telemetry is applied or marked degraded.
   * @collaboration Keeps billing command decisions aware of source health.
   */
  const fetchTelemetry = useCallback(async () => {
    try {
      const response = await sovereignClient.get(`/telemetry/${tenantId}/stats`);
      const payload = extractData(response);
      const nextTelemetry = {
        circuitBreaker: payload.circuitBreaker || payload.metrics?.circuitBreaker || 'CLOSED',
        avgLatencyMs: payload.avgLatencyMs || payload.metrics?.latency || 0,
        forensicSeal: payload.forensicSeal || 'VERIFIED'
      };
      setTelemetry(prev => ({
        ...prev,
        ...nextTelemetry
      }));
      return { status: 'LIVE', payload: nextTelemetry };
    } catch {
      setTelemetry(prev => ({ ...prev, circuitBreaker: 'DEGRADED' }));
      return { status: 'SOURCE_SILENT', payload: { circuitBreaker: 'DEGRADED' } };
    }
  }, [tenantId]);

  /**
   * @description Loads the billing cockpit from live summary, analytics, credit, court and telemetry APIs.
   * @param {string} mode - Hydration mode, either cold or refresh.
   * @returns {Promise<void>} Resolves after all live sources settle.
   * @collaboration The Billing HUD must declare source gaps instead of filling them with theatre.
   */
  const hydrate = useCallback(async (mode = 'cold') => {
    abortRef.current?.abort();
    abortRef.current = new AbortController();
    setRefreshing(mode !== 'cold');
    setError(null);
    if (mode === 'cold') setLoading(true);

    try {
      const [summaryResult, analyticsResult, creditResult, courtResult] = await Promise.allSettled([
        sovereignClient.get('/billing/summary', { signal: abortRef.current.signal }),
        sovereignClient.get('/billing/analytics', { signal: abortRef.current.signal }),
        sovereignClient.get('/billing/credit-scores', { signal: abortRef.current.signal }),
        sovereignClient.get('/courts', { signal: abortRef.current.signal, skipAuthRedirect: true, params: { limit: 1000 } })
      ]);

      const summaryPayload = summaryResult.status === 'fulfilled' ? extractData(summaryResult.value) : null;
      const analyticsPayload = analyticsResult.status === 'fulfilled' ? extractData(analyticsResult.value) : null;
      const creditPayload = creditResult.status === 'fulfilled' ? extractData(creditResult.value) : null;
      const courtPayload = courtResult.status === 'fulfilled' ? extractData(courtResult.value) : null;
      const courtRows = Array.isArray(courtPayload) ? courtPayload : courtPayload?.data || [];
      const invoiceRows = extractBillingInvoices(summaryPayload || {});
      const payloadOutstanding = invoiceRows.reduce((sum, invoice) => sum + Number(invoice.outstandingAmount || invoice.amount || 0), 0);
      const payloadArr = Number(summaryPayload?.totalArr || summaryPayload?.arr || 0);

      if (summaryPayload) setSummary(summaryPayload);
      if (analyticsPayload) setAnalytics(analyticsPayload);
      if (creditPayload) setCreditScores(creditPayload?.scores || creditResult.value.data?.scores || {});
      if (courtResult.status === 'fulfilled') {
        setCourts(courtRows);
        setCourtRegistryStatus(courtRows.length ? 'GLOBAL_REGISTRY_ONLINE' : 'REGISTRY_EMPTY');
        if (courtRows[0]?._id) {
          setSeizure(prev => (prev.courtId ? prev : { ...prev, courtId: courtRows[0]._id }));
          setCourtSearch(prev => prev || formatCourtSearchLabel(courtRows[0]));
        }
      }

      const [treasuryStatusResult, dunningResult, benchmarkResult, policyResult] = await Promise.allSettled([
        treasurySweepManager.getTreasuryStatus(tenantId),
        dunningIntelligence.getDunningRecommendations(tenantId, {
          invoiceRows,
          collectionRiskRows: summaryPayload?.collectionRiskItems || [],
          preferLedgerFallback: true
        }),
        treasurySweepManager.syncBenchmarks(),
        treasurySweepManager.syncPolicyMatrix()
      ]);
      const telemetryResult = await fetchTelemetry();

      if (treasuryStatusResult.status === 'fulfilled') {
        const statusPacket = treasuryStatusResult.value;
        const currentBalance = Number(statusPacket.availableLiquidity || statusPacket.balances?.ZAR || payloadOutstanding || Math.max(payloadArr / 12, 0));
        const evaluation = treasurySweepManager.evaluateLiquidity({
          tenantId,
          currency: 'ZAR',
          currentBalance,
          sourceStatus: statusPacket.sourceStatus,
          context: buildTreasuryContext({ outstanding: payloadOutstanding, totalArr: payloadArr })
        });
        setTreasuryState(prev => ({
          ...prev,
          status: statusPacket.status || evaluation.status,
          statusPacket,
          evaluation,
          lastSync: new Date().toISOString()
        }));
      } else {
        setTreasuryState(prev => ({
          ...prev,
          status: 'SOURCE_SILENT',
          statusPacket: null,
          evaluation: null,
          lastSync: new Date().toISOString()
        }));
      }

      if (dunningResult.status === 'fulfilled') {
        setDunningState(prev => ({
          ...prev,
          status: dunningResult.value.status,
          recommendations: dunningResult.value.recommendations || [],
          lastSync: new Date().toISOString(),
          error: dunningResult.value.warning || null
        }));
      } else {
        setDunningState(prev => ({
          ...prev,
          status: 'SOURCE_SILENT',
          recommendations: [],
          lastSync: new Date().toISOString(),
          error: dunningResult.reason?.message || 'DUNNING_SOURCE_SILENT'
        }));
      }

      setSourceSnapshot({
        lastSync: new Date().toISOString(),
        sources: {
          summary: buildSourceHeartbeat(summaryResult, 'Billing summary'),
          analytics: buildSourceHeartbeat(analyticsResult, 'Billing analytics'),
          credit: buildSourceHeartbeat(creditResult, 'Credit scores'),
          courts: buildSourceHeartbeat(courtResult, 'Court registry'),
          telemetry: {
            label: 'Telemetry',
            status: telemetryResult.status,
            live: telemetryResult.status === 'LIVE',
            error: telemetryResult.status === 'LIVE' ? null : 'TELEMETRY_SOURCE_SILENT'
          },
          treasury: {
            label: 'Treasury sweep',
            status: treasuryStatusResult.status === 'fulfilled' ? treasuryStatusResult.value.status : 'SOURCE_SILENT',
            live: treasuryStatusResult.status === 'fulfilled' && treasuryStatusResult.value.status !== 'SOURCE_SILENT',
            error: treasuryStatusResult.status === 'rejected' ? treasuryStatusResult.reason?.message : null
          },
          dunning: {
            label: 'Neural dunning',
            status: dunningResult.status === 'fulfilled' ? dunningResult.value.status : 'SOURCE_SILENT',
            live: dunningResult.status === 'fulfilled' && dunningResult.value.status !== 'SOURCE_SILENT',
            error: dunningResult.status === 'rejected' ? dunningResult.reason?.message : null
          },
          treasuryBenchmarks: {
            label: 'Treasury benchmarks',
            status: benchmarkResult.status === 'fulfilled' ? benchmarkResult.value.status : 'SOURCE_SILENT',
            live: benchmarkResult.status === 'fulfilled' && benchmarkResult.value.success,
            error: benchmarkResult.status === 'rejected' ? benchmarkResult.reason?.message : null
          },
          treasuryPolicy: {
            label: 'Treasury policy',
            status: policyResult.status === 'fulfilled' ? policyResult.value.status : 'SOURCE_SILENT',
            live: policyResult.status === 'fulfilled' && policyResult.value.success,
            error: policyResult.status === 'rejected' ? policyResult.reason?.message : null
          }
        }
      });

      eventBus?.dispatchEvent?.(new CustomEvent('wilsy_action', {
        detail: { action: 'BILLING_HUD_HYDRATED', payload: { tenantId } }
      }));
      broadcastTelemetry(tenantId, 'BILLING', 'HUD_HYDRATED', 'BillingHUD');
    } catch (err) {
      if (err.name !== 'CanceledError' && err.name !== 'AbortError') {
        setError(err.response?.data?.message || err.message || 'Billing command center could not hydrate.');
      }
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [eventBus, fetchTelemetry, tenantId]);

  useEffect(() => {
    registerShard?.(tenantId);
    hydrate('cold');
    const telemetryTimer = setInterval(fetchTelemetry, 60000);
    return () => {
      abortRef.current?.abort();
      clearInterval(telemetryTimer);
      unregisterShard?.(tenantId);
    };
  }, [fetchTelemetry, hydrate, registerShard, tenantId, unregisterShard]);

  useEffect(() => {
    if (stream?.revenue && Object.keys(stream.revenue).length > 0) {
      setSummary(prev => ({ ...(prev || {}), ...stream.revenue }));
    }
  }, [stream?.revenue]);

  useEffect(() => {
    setManualInvoice(prev => ({
      ...prev,
      idempotencyKey: prev.idempotencyKey || createBillingIdempotencyKey(tenantId)
    }));
  }, [tenantId]);

  useEffect(() => {
    const amount = parseBillingMoneyInput(manualInvoice.amount);
    if (amount === null || amount <= 0) {
      setTaxEnginePreview(null);
      setTaxPreviewBusy(false);
      return undefined;
    }

    let alive = true;
    const timer = setTimeout(async () => {
      setTaxPreviewBusy(true);
      try {
        const draft = buildManualInvoiceDraft(manualInvoice, {
          issuerTenantId: tenantId,
          recipientTenantId: manualInvoice.tenantId.trim() || tenantId,
          amount
        });
        const result = await globalTaxEngine.calculateFromInvoiceDraft(draft, {
          tenantId,
          preferFallbackMatrix: true
        });
        if (alive) setTaxEnginePreview(result);
      } catch (err) {
        if (alive) {
          setTaxEnginePreview({
            success: false,
            sourceStatus: 'SOURCE_SILENT',
            financials: {
              baseAmount: amount,
              taxAmount: 0,
              totalAmount: amount,
              netPayableAmount: amount
            },
            compliance: {
              warnings: [err.response?.data?.message || err.message || 'GlobalTaxEngine preview unavailable. Backend must recalculate before posting.']
            }
          });
        }
      } finally {
        if (alive) setTaxPreviewBusy(false);
      }
    }, 350);

    return () => {
      alive = false;
      clearTimeout(timer);
    };
  }, [
    manualInvoice.amount,
    manualInvoice.currency,
    manualInvoice.customerTaxId,
    manualInvoice.clientJurisdiction,
    manualInvoice.clientType,
    manualInvoice.supplyType,
    manualInvoice.taxType,
    manualInvoice.tenantId,
    manualInvoice.tenantJurisdiction,
    tenantId
  ]);

  useEffect(() => {
    setSourceSnapshot(prev => ({
      ...prev,
      sources: {
        ...(prev.sources || {}),
        tax: {
          label: 'Global tax engine',
          status: taxEnginePreview?.sourceStatus || (taxPreviewBusy ? 'CALCULATING' : 'DRAFT_REQUIRED'),
          live: Boolean(taxEnginePreview?.success),
          error: taxEnginePreview?.success ? null : taxEnginePreview?.compliance?.warnings?.[0] || null
        }
      }
    }));
  }, [taxEnginePreview, taxPreviewBusy]);

  const invoices = useMemo(() => {
    const rows = extractBillingInvoices(summary || {});
    return rows.filter(invoice => {
      const haystack = `${invoice.id || ''} ${invoice.traceId || ''} ${invoice.tenantId || ''} ${invoice.status || ''}`.toLowerCase();
      const matchesSearch = !invoiceSearch || haystack.includes(invoiceSearch.toLowerCase());
      const matchesStatus = statusFilter === 'ALL' || (invoice.status || '').toUpperCase() === statusFilter;
      return matchesSearch && matchesStatus;
    });
  }, [invoiceSearch, statusFilter, summary]);

  const history = summary?.history || [];
  const totalArr = Number(summary?.totalArr || 0);
  const forecastedArr = forecastARR(history) || Number(analytics?.forecast || 0) * 12;
  const outstanding = invoices.reduce((sum, invoice) => sum + Number(invoice.outstandingAmount || invoice.amount || 0), 0);
  const paidVolume = history.reduce((sum, point) => sum + Number(point.paidVolume || 0), 0);
  const issuedVolume = history.reduce((sum, point) => sum + Number(point.volume || 0), 0);
  const collectionEfficiency = issuedVolume > 0 ? Math.round((paidVolume / issuedVolume) * 100) : 100;
  const riskScore = monteCarloRisk(history, 10000);
  const overdueInvoices = useMemo(() => (
    invoices.filter(invoice => ['OVERDUE', 'DISPUTED', 'LEGAL_HOLD'].includes((invoice.status || '').toUpperCase()))
  ), [invoices]);
  const dunningRecommendations = useMemo(() => (
    dunningState.recommendations.length
      ? dunningState.recommendations
      : overdueInvoices.map((invoice, index) => dunningIntelligence.buildRecommendation(invoice, {
        tenantId,
        index,
        sourceStatus: 'INVOICE_LEDGER'
      }))
  ), [dunningState.recommendations, overdueInvoices, tenantId]);
  const treasuryEvaluation = treasuryState.evaluation;
  const maxVolume = Math.max(...history.map(point => Number(point.volume || 0)), 1);
  const isFrozen = activeTenant?.billingStatus === 'FROZEN_AWAITING_SETTLEMENT';
  const selectedCourt = courts.find(court => (court._id || court.id) === seizure.courtId);
  const flightDeck = useMemo(() => buildBillingFlightDeck({
    summary,
    analytics,
    invoices,
    creditScores,
    courts,
    logs,
    telemetry,
    taxEnginePreview,
    treasuryState,
    dunningState: { ...dunningState, recommendations: dunningRecommendations },
    sourceSnapshot,
    collectionEfficiency,
    riskScore,
    outstanding,
    totalArr,
    overdueInvoices
  }), [
    summary,
    analytics,
    invoices,
    creditScores,
    courts,
    logs,
    telemetry,
    taxEnginePreview,
    treasuryState,
    dunningState,
    dunningRecommendations,
    sourceSnapshot,
    collectionEfficiency,
    riskScore,
    outstanding,
    totalArr,
    overdueInvoices
  ]);
  const courtSearchResults = useMemo(() => {
    const needle = normalizeCourtSearch(courtSearch);
    const ranked = courts.filter(court => {
      if (!needle) return true;
      return [
        court.name,
        court.jurisdiction,
        court.type,
        court.location,
        court.economicBloc,
        court.courtLevel,
        court.globalTier,
        court.sourceAuthority,
        asList(court.matterTypes).join(' '),
        asList(court.filingChannels).join(' '),
        asList(court.enforcementRoutes).join(' ')
      ].filter(Boolean).join(' ').toLowerCase().includes(needle);
    });
    const selected = courts.find(court => (court._id || court.id) === seizure.courtId);
    const merged = selected && !ranked.some(court => (court._id || court.id) === (selected._id || selected.id))
      ? [selected, ...ranked]
      : ranked;
    return merged.slice(0, 8);
  }, [courtSearch, courts, seizure.courtId]);
  const manualInvoiceAmount = parseBillingMoneyInput(manualInvoice.amount);
  const manualInvoiceDraft = useMemo(() => buildManualInvoiceDraft(manualInvoice, {
    issuerTenantId: tenantId,
    recipientTenantId: manualInvoice.tenantId.trim(),
    amount: manualInvoiceAmount || 0
  }), [manualInvoice, manualInvoiceAmount, tenantId]);
  const billingCommandEnvelope = useMemo(() => buildBillingCommandEnvelope({
    draft: manualInvoiceDraft,
    taxResult: taxEnginePreview,
    treasuryEvaluation,
    sourceSnapshot
  }), [manualInvoiceDraft, taxEnginePreview, treasuryEvaluation, sourceSnapshot]);
  const manualInvoiceTotal = taxEnginePreview?.financials?.totalAmount ?? (manualInvoiceAmount === null ? 0 : manualInvoiceAmount);
  const taxWarnings = taxEnginePreview?.compliance?.warnings || [];
  const sourceRows = Object.entries(sourceSnapshot.sources || {}).map(([key, source]) => ({ key, ...source }));

  /**
   * @description Executes a billing command with busy-state protection, logging and post-command hydration.
   * @param {string} key - Command identifier used by the cockpit.
   * @param {Function} action - Async API action.
   * @param {Function} successMessage - Formatter for the command receipt.
   * @returns {Promise<unknown|null>} Command result or null when the command fails.
   * @collaboration Makes every billing button produce an auditable command receipt instead of silent UI motion.
   */
  const runCommand = async (key, action, successMessage) => {
    if (processing) return;
    setProcessing(key);
    try {
      const result = await action();
      if (successMessage) addLog(key.toUpperCase(), successMessage(result));
      await hydrate('refresh');
      return result;
    } catch (err) {
      const message = err.response?.data?.message || err.message || 'Command failed.';
      addLog(`${key.toUpperCase()}_FAILED`, message);
      return null;
    } finally {
      setProcessing(null);
    }
  };

  /**
   * @description Creates a sovereign platform invoice through the live billing API.
   * @param {SubmitEvent} event - Form submission event.
   * @returns {Promise<void>} Resolves after invoice creation and ledger refresh.
   * @collaboration Turns billing from a display into a money-motion command.
   */
  const handleManualInvoice = async (event) => {
    event.preventDefault();
    const recipientTenantId = manualInvoice.tenantId.trim();
    const amount = parseBillingMoneyInput(manualInvoice.amount);
    if (!recipientTenantId || amount === null || amount <= 0 || isFrozen) return;
    await runCommand('invoice', async () => {
      const draft = buildManualInvoiceDraft(manualInvoice, {
        issuerTenantId: tenantId,
        recipientTenantId,
        amount
      });
      const finalTaxResult = await globalTaxEngine.calculateFromInvoiceDraft(draft, {
        tenantId,
        preferFallbackMatrix: true
      })
        .catch(() => taxEnginePreview);
      const taxConfig = globalTaxEngine.buildInvoiceTaxConfig(finalTaxResult, draft);
      const commandEnvelope = buildBillingCommandEnvelope({
        draft,
        taxResult: finalTaxResult,
        treasuryEvaluation,
        sourceSnapshot
      });
      const response = await sovereignClient.post('/billing/invoice/generate', {
        idempotencyKey: draft.idempotencyKey,
        tenantId: recipientTenantId,
        amount: draft.amount,
        baseAmount: finalTaxResult?.financials?.baseAmount ?? draft.amount,
        taxAmount: finalTaxResult?.financials?.taxAmount ?? 0,
        totalAmount: finalTaxResult?.financials?.totalAmount ?? draft.amount,
        netPayableAmount: finalTaxResult?.financials?.netPayableAmount ?? finalTaxResult?.financials?.totalAmount ?? draft.amount,
        currency: draft.currency,
        paymentTerms: draft.paymentTerms,
        issueDate: draft.issueDate,
        dueDate: draft.dueDate,
        invoiceClass: draft.invoiceClass,
        billingModel: draft.billingModel,
        taxConfig,
        metadata: {
          billingNucleus: {
            commandVersion: commandEnvelope.commandVersion,
            commandProofHash: commandEnvelope.proof.hash,
            taxProofHash: finalTaxResult?.proof?.hash || null,
            treasuryProofHash: treasuryEvaluation?.proof?.hash || null,
            sourceCoverage: flightDeck.sourceLabel,
            readiness: flightDeck.readiness
          },
          sourceSnapshot: commandEnvelope.sources
        },
        lineItems: [{
          description: draft.description,
          quantity: 1,
          unitPrice: draft.amount,
          lineTotal: draft.amount,
          taxAmount: finalTaxResult?.financials?.taxAmount ?? 0,
          taxRate: taxConfig.rate || 0,
          category: 'PLATFORM_INFRASTRUCTURE',
          units: draft.supplyType
        }]
      }, {
        headers: {
          'X-Tenant-ID': 'GLOBAL_ROOT',
          'X-Idempotency-Key': draft.idempotencyKey,
          'X-Wilsy-Billing-Proof': commandEnvelope.proof.hash
        }
      });
      setManualInvoice(prev => ({
        ...prev,
        tenantId: '',
        amount: '',
        idempotencyKey: createBillingIdempotencyKey(tenantId)
      }));
      return { ...response.data, billingCommandEnvelope: commandEnvelope, taxResult: finalTaxResult };
    }, data => `Invoice sealed for ${data?.invoice?.recipientTenantId || recipientTenantId} • proof ${data?.billingCommandEnvelope?.proof?.hash?.slice(0, 14) || 'pending'}`);
  };

  /**
   * @description Runs the backend monthly billing sweep for active tenant subscriptions.
   * @returns {Promise<void>} Resolves after the billing sweep completes.
   * @collaboration Lets the founder execute recurring revenue operations from the cockpit.
   */
  const runAutoBilling = async () => {
    await runCommand('auto_billing', async () => {
      const response = await sovereignClient.post('/billing/auto-monthly', {}, { headers: { 'X-Tenant-ID': 'GLOBAL_ROOT' } });
      return response.data;
    }, data => `${data.invoicesGenerated || 0} invoices generated, ${data.emailsSent || 0} notices queued`);
  };

  /**
   * @description Reprices active tenants using live ARR, subscription count and deterministic risk.
   * @returns {Promise<void>} Resolves after pricing guardrails are applied.
   * @collaboration Pricing must adapt from evidence instead of static packages.
   */
  const applyDynamicPricing = async () => {
    await runCommand('dynamic_pricing', async () => {
      const basePrice = Math.max(1000, Math.round((totalArr || 12000) / Math.max(1, Number(summary?.activeSubscriptions || 1)) / 12));
      const riskAdjusted = riskScore > 0.7 ? basePrice * 1.15 : riskScore < 0.3 ? basePrice * 0.95 : basePrice;
      const response = await sovereignClient.post('/billing/apply-dynamic-pricing', {
        newPrice: Math.round(riskAdjusted),
        risk: riskScore
      }, { headers: { 'X-Tenant-ID': 'GLOBAL_ROOT' } });
      setPricingResult(response.data?.prices || {});
      return response.data;
    }, data => `${Object.keys(data.prices || {}).length} tenant prices recalibrated`);
  };

  /**
   * @description Requests a settlement preview from the billing backend.
   * @returns {Promise<void>} Resolves after settlement readiness is loaded.
   * @collaboration Gives finance operators a pre-flight settlement check before moving money.
   */
  const previewSettlement = async () => {
    await runCommand('settlement_preview', async () => {
      const response = await sovereignClient.get('/billing/blockchain-preview', { headers: { 'X-Tenant-ID': 'GLOBAL_ROOT' } });
      setBlockchainPreview(response.data);
      return response.data;
    }, data => `Settlement preview ready: ${data.gasFee || '0'} ETH, ${data.estimatedTime || 'pending'}`);
  };

  /**
   * @description Executes or simulates a governed treasury sweep through TreasurySweepManager.
   * @returns {Promise<void>} Resolves after sweep receipt is recorded.
   * @collaboration Idle capital is treated as an operational inefficiency, but no funds move unless policy gates pass.
   */
  const runTreasurySweep = async () => {
    await runCommand('treasury_sweep', async () => {
      const context = buildTreasuryContext({ outstanding, totalArr, taxResult: taxEnginePreview });
      const receipt = await treasurySweepManager.executeSweep({
        tenantId,
        currency: manualInvoice.currency || 'ZAR',
        currentBalance: treasuryState.statusPacket?.availableLiquidity ?? treasuryEvaluation?.liquidity?.currentBalance ?? Math.max(totalArr / 12, outstanding, 0),
        context,
        approval: {
          requestedBy: 'BillingHUD',
          readiness: flightDeck.readiness,
          sourceCoverage: flightDeck.sourceLabel
        }
      });
      setTreasuryState(prev => ({
        ...prev,
        status: receipt.status,
        evaluation: receipt.evaluation || prev.evaluation,
        lastReceipt: receipt,
        lastSync: new Date().toISOString()
      }));
      return receipt;
    }, receipt => `${receipt.executionStatus || receipt.status} • ${receipt.evaluation?.liquidity?.availableToSweep || 0} ${receipt.currency || manualInvoice.currency}`);
  };

  /**
   * @description Executes a neural dunning recommendation through DunningIntelligence.
   * @param {Object} recommendation - Dunning recommendation selected by the operator.
   * @returns {Promise<void>} Resolves after receipt is preserved.
   * @collaboration Collections become staged, consent-aware and court-ready instead of one-size-fits-all email blasts.
   */
  const runDunningIntervention = async (recommendation) => {
    await runCommand('dunning_intervention', async () => {
      const receipt = await dunningIntelligence.executeIntervention({ tenantId, recommendation });
      setDunningState(prev => ({
        ...prev,
        lastReceipt: receipt,
        recommendations: prev.recommendations.map(item => (
          item.traceId === recommendation.traceId ? { ...item, lastReceiptStatus: receipt.status } : item
        ))
      }));
      return receipt;
    }, receipt => `${recommendation.client || recommendation.clientId} • ${receipt.dispatchStatus || receipt.status}`);
  };

  /**
   * @description Submits a billing dispute with evidence context.
   * @returns {Promise<void>} Resolves after the dispute mediator records the case.
   * @collaboration Keeps billing conflict handling inside Wilsy OS instead of external spreadsheets.
   */
  const submitDispute = async () => {
    if (!disputeModal.invoiceId || !disputeModal.reason) return;
    await runCommand('dispute', async () => {
      const response = await sovereignClient.post('/billing/dispute', {
        invoiceId: disputeModal.invoiceId,
        reason: disputeModal.reason
      }, { headers: { 'X-Tenant-ID': 'GLOBAL_ROOT' } });
      setDisputeModal({ open: false, invoiceId: '', reason: '' });
      return response.data;
    }, data => data.resolution || 'Dispute registered');
  };

  /**
   * @description Sends an overdue invoice into the court-aware seizure workflow.
   * @param {SubmitEvent} event - Form submission event.
   * @returns {Promise<void>} Resolves after the legal collections command is sealed.
   * @collaboration Links revenue recovery to the global court registry with forensic precision.
   */
  const initiateSeizure = async (event) => {
    event.preventDefault();
    if (!seizure.invoiceId || !seizure.reason || !seizure.courtId) return;
    await runCommand('seizure', async () => {
      const response = await sovereignClient.post('/billing/warroom/seizure', {
        invoiceId: seizure.invoiceId,
        reason: seizure.reason,
        courtId: seizure.courtId,
        tenantId
      }, { headers: { 'X-Tenant-ID': tenantId } });
      setSeizureResult(response.data);
      return response.data;
    }, data => `Court ref ${data.courtRef || 'pending'} sealed`);
  };

  /**
   * @description Seeds or syncs the court registry used by billing legal escalation.
   * @returns {Promise<void>} Resolves after the court registry is refreshed.
   * @collaboration Court-aware billing is a Wilsy OS differentiator, not an optional dropdown.
   */
  const seedCourtRegistry = async () => {
    await runCommand('court_registry_seed', async () => {
      const response = await sovereignClient.post('/courts/seed', {}, { headers: { 'X-Tenant-ID': tenantId } });
      const rows = response.data?.data || [];
      setCourts(rows);
      setCourtRegistryStatus('GLOBAL_REGISTRY_SEEDED');
      if (rows[0]?._id) {
        setSeizure(prev => ({ ...prev, courtId: prev.courtId || rows[0]._id }));
        setCourtSearch(prev => prev || formatCourtSearchLabel(rows[0]));
      }
      return response.data;
    }, data => `${data.count || 0} courts anchored into registry`);
  };

  /**
   * @description Selects a court from the searchable global registry.
   * @param {Object} court - Court registry record.
   * @returns {void}
   * @collaboration Makes legal routing deliberate and visible to the operator.
   */
  const selectCourt = (court) => {
    const id = court._id || court.id;
    setSeizure(prev => ({ ...prev, courtId: id }));
    setCourtSearch(formatCourtSearchLabel(court));
  };

  /**
   * @description Applies competitive pricing pressure to a target tenant.
   * @param {SubmitEvent} event - Form submission event.
   * @returns {Promise<void>} Resolves after pricing adjustment is sealed.
   * @collaboration Enables market-capture actions from live billing context.
   */
  const activateCompetitivePricing = async (event) => {
    event.preventDefault();
    if (!pricing.tenantId) return;
    await runCommand('competitive_pricing', async () => {
      const response = await sovereignClient.post('/billing/warroom/competitive-pricing', {
        tenantId: pricing.tenantId,
        undercutMarginPercent: Number(pricing.margin || 5)
      }, { headers: { 'X-Tenant-ID': tenantId } });
      setCompetitiveResult(response.data);
      return response.data;
    }, data => `${pricing.tenantId} price moved to ${formatMoney(data.newPrice || 0)}`);
  };

  /**
   * @description Exports the currently visible invoice ledger to CSV.
   * @returns {void}
   * @collaboration Gives the boardroom a portable billing artifact without hiding source limits.
   */
  const exportToCSV = () => {
    if (!invoices.length) return;
    const headers = ['Invoice', 'Tenant', 'Amount', 'Outstanding', 'Status', 'Due Date', 'Seal'];
    const rows = invoices.map(invoice => [
      invoice.id || invoice.traceId || '',
      invoice.tenantId || '',
      invoice.amount || 0,
      invoice.outstandingAmount || 0,
      invoice.status || '',
      invoice.dueDate || '',
      invoice.sealHash || ''
    ]);
    const csv = [headers, ...rows].map(row => row.map(cell => `"${String(cell).replace(/"/g, '""')}"`).join(',')).join('\n');
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `wilsy_billing_command_${Date.now()}.csv`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
    addLog('EXPORT', `${invoices.length} billing rows exported`);
  };

  if (loading) {
    return (
      <div className={hudStyles.loading}>
        <div className={hudStyles.loadingInner}>
          <RefreshCw className="animate-spin" size={28} />
          <h2>Hydrating sovereign billing command</h2>
          <p>Reading subscriptions, invoices, credit scores, courts, telemetry and settlement rails.</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={hudStyles.error}>
        <div className={hudStyles.errorInner}>
          <AlertOctagon size={36} />
          <h2>Billing command offline</h2>
          <p>{error}</p>
          <div className={hudStyles.featureActions}>
            <button type="button" className={hudStyles.primaryButton} onClick={() => hydrate('cold')}>
              <RefreshCw size={15} /> Retry
            </button>
            <button type="button" className={hudStyles.secondaryButton} onClick={logout}>
              Re-authenticate
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={hudStyles.billingShell}>
      <section className={hudStyles.hero}>
        <div>
          <span className={hudStyles.eyebrow}><Globe2 size={15} /> Wilsy OS Billing Nucleus</span>
          <h1>Global Monetization Command</h1>
          <p>
            One source-aware command surface for idempotent invoices, ARR, global tax routing,
            treasury motion, neural dunning, disputes and court-ready legal collections.
          </p>
        </div>
        <div className={hudStyles.heroActions}>
          <button type="button" className={hudStyles.secondaryButton} onClick={exportToCSV}>
            <Download size={15} /> Export
          </button>
          <button type="button" className={hudStyles.secondaryButton} onClick={() => hydrate('refresh')} disabled={refreshing}>
            <RefreshCw size={15} className={refreshing ? 'animate-spin' : ''} /> Refresh
          </button>
          <button type="button" className={hudStyles.primaryButton} onClick={() => setActiveTab('invoices')}>
            <PlusCircle size={15} /> Invoice
          </button>
        </div>
      </section>

      {isFrozen && (
        <div className={hudStyles.alertBanner}>
          <AlertTriangle size={18} />
          Current tenant is frozen pending settlement. Manual invoice actions are locked for this shard.
        </div>
      )}

      <section className={hudStyles.statusStrip}>
        <article className={hudStyles.statusCard}>
          <span>Mesh</span>
          <strong>{mesh?.meshHealth || 'STANDBY'}</strong>
          <small>{mesh?.activeShards || 0} active shards, sync {stream?.syncStatus || 'idle'}</small>
        </article>
        <article className={hudStyles.statusCard}>
          <span>Telemetry</span>
          <strong>{telemetry.circuitBreaker}</strong>
          <small>{telemetry.avgLatencyMs || 0} ms average latency</small>
        </article>
        <article className={hudStyles.statusCard}>
          <span>Jurisdictions</span>
          <strong>{courts.length}</strong>
          <small>Courts available for escalation workflow</small>
        </article>
        <article className={hudStyles.statusCard}>
          <span>Seal</span>
          <strong>{telemetry.forensicSeal}</strong>
          <small>Evidence-ready ledger events</small>
        </article>
        <article className={hudStyles.statusCard}>
          <span>Tax</span>
          <strong>{taxPreviewBusy ? 'CALCULATING' : taxEnginePreview?.sourceStatus || 'DRAFT_REQUIRED'}</strong>
          <small>{taxEnginePreview?.proof?.hash ? `Proof ${taxEnginePreview.proof.hash.slice(0, 14)}` : 'Draft an invoice to seal tax posture'}</small>
        </article>
        <article className={hudStyles.statusCard}>
          <span>Treasury</span>
          <strong>{treasuryEvaluation?.status || treasuryState.status}</strong>
          <small>{treasuryEvaluation ? `${formatMoney(treasuryEvaluation.liquidity?.availableToSweep || 0, treasuryEvaluation.currency)} sweep candidate` : 'Treasury source not evaluated'}</small>
        </article>
        <article className={hudStyles.statusCard}>
          <span>Dunning</span>
          <strong>{dunningState.status}</strong>
          <small>{dunningRecommendations.length} governed recommendations</small>
        </article>
      </section>

      <section className={hudStyles.flightDeck} aria-label="Billing operating flight deck">
        <div className={hudStyles.flightNarrative}>
          <span><Gauge size={15} /> Billing Flight Deck</span>
          <h2>{flightDeck.posture.replace('_', ' ')}</h2>
          <p>{flightDeck.nextAction}</p>
          <div className={hudStyles.flightSourceRail}>
            {flightDeck.liveSources.map(source => (
              <span key={source.key} data-live={source.live ? 'true' : 'false'}>
                {source.live ? <CheckCircle size={13} /> : <AlertTriangle size={13} />}
                {source.label}
              </span>
            ))}
          </div>
        </div>
        <div className={hudStyles.flightReadiness}>
          <span>Operational Readiness</span>
          <strong>{flightDeck.readiness}%</strong>
          <small>{flightDeck.sourceLabel}</small>
          <div className={hudStyles.readinessBar} aria-hidden="true">
            <i style={{ width: `${flightDeck.readiness}%` }} />
          </div>
        </div>
        <div className={hudStyles.flightActions}>
          <button type="button" onClick={() => setActiveTab('invoices')}>
            <FileText size={15} /> Create Invoice
          </button>
          <button type="button" onClick={runAutoBilling} disabled={!!processing}>
            {processing === 'auto_billing' ? <RefreshCw className="animate-spin" size={15} /> : <Zap size={15} />}
            Run Billing
          </button>
          <button type="button" onClick={() => setActiveTab('warroom')}>
            <Gavel size={15} /> Legal Route
          </button>
        </div>
      </section>

      <section className={hudStyles.nucleusGrid} aria-label="Billing nucleus source proof">
        <article className={hudStyles.nucleusCard}>
          <header><span>Deterministic Governance</span><CopyCheck size={18} /></header>
          <strong>{manualInvoice.idempotencyKey}</strong>
          <small>Current invoice command proof {billingCommandEnvelope.proof.hash.slice(0, 16)}.</small>
        </article>
        <article className={hudStyles.nucleusCard}>
          <header><span>Cross-Border Tax</span><Globe2 size={18} /></header>
          <strong>{taxEnginePreview?.taxProfile?.type || manualInvoice.taxType}</strong>
          <small>{taxWarnings[0] || taxEnginePreview?.compliance?.invoiceNote || 'Global tax posture will seal when amount is entered.'}</small>
        </article>
        <article className={hudStyles.nucleusCard}>
          <header><span>Treasury Sweep</span><Landmark size={18} /></header>
          <strong>{treasuryEvaluation?.executionEligible ? 'READY' : treasuryEvaluation?.status || 'SOURCE_SILENT'}</strong>
          <small>{treasuryEvaluation?.warnings?.[0] || treasuryState.statusPacket?.warning || 'Operating buffer and benchmark gates are enforced.'}</small>
        </article>
        <article className={hudStyles.nucleusCard}>
          <header><span>Forensic Collections</span><Gavel size={18} /></header>
          <strong>{dunningRecommendations.filter(item => item.gateStatus === 'READY').length} READY</strong>
          <small>{dunningState.error || 'Dunning recommendations include consent, quiet-hour, dispute and legal-hold gates.'}</small>
        </article>
      </section>

      <nav className={hudStyles.tabs} aria-label="Billing workspace">
        {tabs.map(tab => (
          <button
            key={tab.id}
            type="button"
            className={activeTab === tab.id ? hudStyles.tabActive : hudStyles.tabButton}
            onClick={() => setActiveTab(tab.id)}
          >
            <tab.icon size={15} /> {tab.label}
          </button>
        ))}
      </nav>

      <section className={hudStyles.metricGrid}>
        <article className={hudStyles.metricCard}>
          <TrendingUp size={18} />
          <span>Global ARR</span>
          <strong>{formatMoney(totalArr)}</strong>
          <small>{summary?.mrrGrowth || 0}% monthly movement</small>
        </article>
        <article className={hudStyles.metricCard} data-tone="cyan">
          <Users size={18} />
          <span>Active Subscriptions</span>
          <strong>{summary?.activeSubscriptions || 0}</strong>
          <small>Live billable tenant contracts</small>
        </article>
        <article className={hudStyles.metricCard} data-tone="red">
          <Clock size={18} />
          <span>Outstanding</span>
          <strong>{formatMoney(outstanding)}</strong>
          <small>{summary?.pendingInvoices || 0} unsettled invoices</small>
        </article>
        <article className={hudStyles.metricCard} data-tone="green">
          <ShieldCheck size={18} />
          <span>Collection Efficiency</span>
          <strong>{collectionEfficiency}%</strong>
          <small>Paid volume against issued volume</small>
        </article>
      </section>

      {activeTab === 'command' && (
        <section className={hudStyles.mainGrid}>
          <div>
            <div className={hudStyles.panel}>
              <div className={hudStyles.panelHeader}>
                <div className={hudStyles.panelTitle}>
                  <BarChart3 size={18} />
                  <div>
                    <span>Revenue trajectory</span>
                    <h2>12 Month Billing Pulse</h2>
                  </div>
                </div>
                <strong>{formatMoney(forecastedArr || 0)} forecast ARR</strong>
              </div>
              <div className={hudStyles.chartGrid}>
                {history.map(point => (
                  <div
                    key={point.label}
                    className={hudStyles.bar}
                    style={{ height: `${Math.max(8, (Number(point.volume || 0) / maxVolume) * 160)}px` }}
                    title={`${point.label}: ${formatMoney(point.volume || 0)}`}
                  >
                    <span>{point.label?.slice(5) || '--'}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className={hudStyles.panel}>
              <div className={hudStyles.panelHeader}>
                <div className={hudStyles.panelTitle}>
                  <Target size={18} />
                  <div>
                    <span>Receivables operating board</span>
                    <h2>Settlement Lanes</h2>
                  </div>
                </div>
                <span className={hudStyles.statusPill}>{overdueInvoices.length} escalatable</span>
              </div>
              <div className={hudStyles.board}>
                {settlementLanes.map(lane => {
                  const laneItems = (summary?.recentInvoices || []).filter(invoice => (invoice.status || 'ISSUED').toUpperCase() === lane);
                  return (
                    <div key={lane} className={hudStyles.lane}>
                      <header><span>{lane.replace('_', ' ')}</span><strong>{laneItems.length}</strong></header>
                      {laneItems.length === 0 ? (
                        <div className={hudStyles.empty}>No invoices in lane.</div>
                      ) : laneItems.slice(0, 4).map(invoice => (
                        <article key={invoice.id || invoice.traceId} className={hudStyles.laneCard}>
                          <strong>{invoice.id || invoice.traceId}</strong>
                          <span>{invoice.tenantId || 'Unknown tenant'}</span>
                          <small>{formatMoney(invoice.outstandingAmount || invoice.amount || 0, invoice.currency)}</small>
                        </article>
                      ))}
                    </div>
                  );
                })}
              </div>
            </div>
          </div>

          <aside>
            <div className={hudStyles.panel}>
              <div className={hudStyles.panelHeader}>
                <div className={hudStyles.panelTitle}>
                  <Gauge size={18} />
                  <div>
                    <span>Risk engine</span>
                    <h3>Deterministic Cashflow Guard</h3>
                  </div>
                </div>
              </div>
              <div className={hudStyles.featureGrid}>
                <article className={hudStyles.featureCard}>
                  <span>Ledger Risk</span>
                  <strong>{Math.round(riskScore * 100)}%</strong>
                  <small>Derived from live inflow trend, variance and recent shortfall. No random simulation.</small>
                </article>
                <article className={hudStyles.featureCard}>
                  <span>Overdue Pressure</span>
                  <strong>{overdueInvoices.length}</strong>
                  <small>Invoices ready for legal or dunning actions</small>
                </article>
                <article className={hudStyles.featureCard}>
                  <span>Source Coverage</span>
                  <strong>{flightDeck.sourceLabel}</strong>
                  <small>Billing command readiness follows the sources currently mounted into the cockpit.</small>
                </article>
              </div>
            </div>

            <div className={hudStyles.panel}>
              <div className={hudStyles.panelHeader}>
                <div className={hudStyles.panelTitle}>
                  <Sparkles size={18} />
                  <div>
                    <span>Evidence stream</span>
                    <h3>Forensic Activity</h3>
                  </div>
                </div>
              </div>
              <div className={hudStyles.timeline}>
                {logs.length === 0 ? (
                  <div className={hudStyles.empty}>No billing commands executed this session.</div>
                ) : logs.map((log, index) => (
                  <div key={`${log.timestamp}-${index}`} className={hudStyles.timelineItem}>
                    <span>{new Date(log.timestamp).toLocaleTimeString()}</span>
                    <strong>{log.action}</strong>
                    <small>{log.result}</small>
                  </div>
                ))}
              </div>
            </div>
          </aside>
        </section>
      )}

      {activeTab === 'invoices' && (
        <section className={hudStyles.mainGrid}>
          <div>
            <div className={hudStyles.panel}>
              <div className={hudStyles.panelHeader}>
                <div className={hudStyles.panelTitle}>
                  <FileText size={18} />
                  <div>
                    <span>Invoice command</span>
                    <h2>Sovereign Infrastructure Invoice</h2>
                  </div>
                </div>
              </div>
              <form className={hudStyles.formGrid} onSubmit={handleManualInvoice}>
                <div className={hudStyles.field}>
                  <label>Target tenant</label>
                  <input
                    value={manualInvoice.tenantId}
                    onChange={event => setManualInvoice(prev => ({ ...prev, tenantId: event.target.value }))}
                    onBlur={() => setManualInvoice(prev => ({ ...prev, tenantId: prev.tenantId.trim() }))}
                    placeholder="TENANT-ID"
                    required
                  />
                </div>
                <div className={hudStyles.field}>
                  <label>Amount</label>
                  <input
                    type="text"
                    inputMode="decimal"
                    value={manualInvoice.amount}
                    onChange={event => setManualInvoice(prev => ({ ...prev, amount: sanitizeBillingMoneyInput(event.target.value) }))}
                    onBlur={() => setManualInvoice(prev => ({ ...prev, amount: formatBillingMoneyInput(prev.amount) }))}
                    placeholder="0.00"
                    required
                  />
                  <small className={hudStyles.moneyHint}>
                    Invoice total: {formatMoney(manualInvoiceTotal, manualInvoice.currency)}
                  </small>
                </div>
                <div className={hudStyles.field}>
                  <label>Currency</label>
                  <select value={manualInvoice.currency} onChange={event => setManualInvoice(prev => ({ ...prev, currency: event.target.value }))}>
                    {['ZAR', 'USD', 'EUR', 'GBP', 'NGN', 'KES', 'GHS', 'BWP', 'NAD', 'MUR'].map(currency => <option key={currency} value={currency}>{currency}</option>)}
                  </select>
                </div>
                <div className={hudStyles.field}>
                  <label>Payment terms</label>
                  <select value={manualInvoice.paymentTerms} onChange={event => setManualInvoice(prev => ({ ...prev, paymentTerms: event.target.value }))}>
                    {[7, 14, 30, 45, 60].map(days => <option key={days} value={days}>{days} days</option>)}
                  </select>
                </div>
                <div className={hudStyles.field}>
                  <label>Seller jurisdiction</label>
                  <select value={manualInvoice.tenantJurisdiction} onChange={event => setManualInvoice(prev => ({ ...prev, tenantJurisdiction: event.target.value }))}>
                    {['ZA', 'US', 'GB', 'EU', 'NG', 'KE', 'GH', 'BW', 'NA', 'MU', 'SG', 'AU', 'AE'].map(code => <option key={code} value={code}>{code}</option>)}
                  </select>
                </div>
                <div className={hudStyles.field}>
                  <label>Customer jurisdiction</label>
                  <select value={manualInvoice.clientJurisdiction} onChange={event => setManualInvoice(prev => ({ ...prev, clientJurisdiction: event.target.value }))}>
                    {['ZA', 'US', 'GB', 'EU', 'NG', 'KE', 'GH', 'BW', 'NA', 'MU', 'SG', 'AU', 'AE'].map(code => <option key={code} value={code}>{code}</option>)}
                  </select>
                </div>
                <div className={hudStyles.field}>
                  <label>Client type</label>
                  <select value={manualInvoice.clientType} onChange={event => setManualInvoice(prev => ({ ...prev, clientType: event.target.value }))}>
                    <option value="B2B">B2B</option>
                    <option value="B2C">B2C</option>
                  </select>
                </div>
                <div className={hudStyles.field}>
                  <label>Supply type</label>
                  <select value={manualInvoice.supplyType} onChange={event => setManualInvoice(prev => ({ ...prev, supplyType: event.target.value }))}>
                    <option value="DIGITAL_SERVICE">Digital service</option>
                    <option value="SAAS">SaaS subscription</option>
                    <option value="USAGE_BASED">Usage based</option>
                    <option value="PLATFORM_RETAINER">Platform retainer</option>
                    <option value="INSTITUTIONAL_SERVICE">Institutional service</option>
                  </select>
                </div>
                <div className={hudStyles.field}>
                  <label>Tax type</label>
                  <select value={manualInvoice.taxType} onChange={event => setManualInvoice(prev => ({ ...prev, taxType: event.target.value }))}>
                    <option value="VAT">VAT</option>
                    <option value="GST">GST</option>
                    <option value="SALES_TAX">Sales tax</option>
                    <option value="VAT_ZERO">VAT zero-rated</option>
                    <option value="VAT_EXEMPT">VAT exempt</option>
                    <option value="NO_TAX">No tax</option>
                  </select>
                </div>
                <div className={hudStyles.field}>
                  <label>Customer tax ID</label>
                  <input
                    value={manualInvoice.customerTaxId}
                    onChange={event => setManualInvoice(prev => ({ ...prev, customerTaxId: event.target.value }))}
                    placeholder="VAT/GST/TIN evidence"
                  />
                </div>
                <div className={`${hudStyles.field} ${hudStyles.fieldFull}`}>
                  <label>Idempotency key</label>
                  <div className={hudStyles.inlineCommand}>
                    <input
                      value={manualInvoice.idempotencyKey}
                      onChange={event => setManualInvoice(prev => ({ ...prev, idempotencyKey: event.target.value }))}
                    />
                    <button type="button" className={hudStyles.secondaryButton} onClick={() => setManualInvoice(prev => ({ ...prev, idempotencyKey: createBillingIdempotencyKey(tenantId) }))}>
                      <RefreshCw size={14} /> Rotate
                    </button>
                  </div>
                </div>
                <div className={`${hudStyles.field} ${hudStyles.fieldFull}`}>
                  <label>Description</label>
                  <textarea value={manualInvoice.description} onChange={event => setManualInvoice(prev => ({ ...prev, description: event.target.value }))} />
                </div>
                <div className={hudStyles.fieldFull}>
                  <button type="submit" className={hudStyles.primaryButton} disabled={processing === 'invoice' || isFrozen}>
                    {processing === 'invoice' ? <RefreshCw className="animate-spin" size={15} /> : <PlusCircle size={15} />}
                    Seal Invoice
                  </button>
                </div>
              </form>
            </div>
          </div>

          <aside>
            <div className={hudStyles.panel}>
              <div className={hudStyles.panelHeader}>
                <div className={hudStyles.panelTitle}>
                  <ShieldCheck size={18} />
                  <div>
                    <span>Controls</span>
                    <h3>Tax and Collection Guardrails</h3>
                  </div>
                </div>
              </div>
              <div className={hudStyles.featureGrid}>
                <article className={hudStyles.featureCard}>
                  <span>Tax proof</span>
                  <strong>{taxPreviewBusy ? 'Calculating' : taxEnginePreview?.sourceStatus || 'Draft required'}</strong>
                  <small>{taxEnginePreview?.proof?.hash ? `SHA3 ${taxEnginePreview.proof.hash.slice(0, 22)}` : taxWarnings[0] || 'Enter an amount to calculate VAT/GST/sales-tax posture.'}</small>
                </article>
                <article className={hudStyles.featureCard}>
                  <span>Idempotency</span>
                  <strong>{manualInvoice.idempotencyKey.slice(0, 18)}</strong>
                  <small>Duplicate-defense key is sent as X-Idempotency-Key and sealed into the command proof.</small>
                </article>
                <article className={hudStyles.featureCard}>
                  <span>Total payable</span>
                  <strong>{formatMoney(manualInvoiceTotal, manualInvoice.currency)}</strong>
                  <small>Base {formatMoney(taxEnginePreview?.financials?.baseAmount ?? manualInvoiceAmount ?? 0, manualInvoice.currency)} • tax {formatMoney(taxEnginePreview?.financials?.taxAmount || 0, manualInvoice.currency)}</small>
                </article>
                <article className={hudStyles.featureCard}>
                  <span>Command proof</span>
                  <strong>{billingCommandEnvelope.proof.hash.slice(0, 18)}</strong>
                  <small>{billingCommandEnvelope.commandVersion}</small>
                </article>
              </div>
            </div>
          </aside>

          <div className={hudStyles.panel} style={{ gridColumn: '1 / -1' }}>
            <div className={hudStyles.panelHeader}>
              <div className={hudStyles.panelTitle}>
                <Banknote size={18} />
                <div>
                  <span>Invoice ledger</span>
                  <h2>Recent Sovereign Invoices</h2>
                </div>
              </div>
              <div className={hudStyles.heroActions}>
                <input value={invoiceSearch} onChange={event => setInvoiceSearch(event.target.value)} placeholder="Search tenant or invoice" className={hudStyles.secondaryButton} />
                <select value={statusFilter} onChange={event => setStatusFilter(event.target.value)} className={hudStyles.secondaryButton}>
                  {['ALL', 'ISSUED', 'OVERDUE', 'PARTIALLY_PAID', 'PAID', 'DISPUTED'].map(status => <option key={status} value={status}>{status}</option>)}
                </select>
              </div>
            </div>
            <div className={hudStyles.invoiceList}>
              {invoices.length === 0 ? (
                <div className={hudStyles.empty}>No invoices match the current filter.</div>
              ) : invoices.map(invoice => (
                <article key={invoice.id || invoice.traceId} className={hudStyles.invoiceRow}>
                  <div>
                    <strong>{invoice.id || invoice.traceId}</strong>
                    <small>{invoice.traceId}</small>
                  </div>
                  <div>
                    <span>{invoice.tenantId || 'Unknown tenant'}</span>
                    <small>Due {formatDate(invoice.dueDate)}</small>
                  </div>
                  <strong>{formatMoney(invoice.amount || 0, invoice.currency)}</strong>
                  <span>{formatMoney(invoice.outstandingAmount || 0, invoice.currency)}</span>
                  <div className={hudStyles.featureActions}>
                    <span className={hudStyles.statusPill} data-status={getStatusTone(invoice.status)}>{invoice.status || 'ISSUED'}</span>
                    <button type="button" className={hudStyles.ghostButton} onClick={() => setDisputeModal({ open: true, invoiceId: invoice.id || invoice.traceId, reason: '' })}>
                      <Scale size={13} />
                    </button>
                  </div>
                </article>
              ))}
            </div>
          </div>
        </section>
      )}

      {activeTab === 'sovereignty' && (
        <section className={hudStyles.splitGrid}>
          <div className={hudStyles.panel}>
            <div className={hudStyles.panelHeader}>
              <div className={hudStyles.panelTitle}>
                <Globe2 size={18} />
                <div>
                  <span>Cross-border sovereignty</span>
                  <h2>Global Tax Routing</h2>
                </div>
              </div>
              <span className={hudStyles.statusPill}>{taxEnginePreview?.sourceStatus || 'DRAFT_REQUIRED'}</span>
            </div>
            <div className={hudStyles.sovereigntyGrid}>
              <article>
                <span>Rule</span>
                <strong>{taxEnginePreview?.jurisdictionData?.rule || 'Awaiting invoice draft'}</strong>
                <small>{taxEnginePreview?.jurisdictionData?.crossBorder ? 'Cross-border posture active' : 'Domestic or not yet classified'}</small>
              </article>
              <article>
                <span>Taxing jurisdiction</span>
                <strong>{taxEnginePreview?.jurisdictionData?.taxingJurisdiction || manualInvoice.clientJurisdiction}</strong>
                <small>{taxEnginePreview?.taxProfile?.authority || 'Live or fallback statutory authority required'}</small>
              </article>
              <article>
                <span>Effective rate</span>
                <strong>{preciseRound((taxEnginePreview?.taxProfile?.effectiveRate || 0) * 100, 2)}%</strong>
                <small>{taxEnginePreview?.taxProfile?.reverseChargeApplied ? 'Reverse charge applied' : 'Tax calculated where source permits'}</small>
              </article>
              <article>
                <span>Tax amount</span>
                <strong>{formatMoney(taxEnginePreview?.financials?.taxAmount || 0, manualInvoice.currency)}</strong>
                <small>Total payable {formatMoney(manualInvoiceTotal, manualInvoice.currency)}</small>
              </article>
            </div>
            <div className={hudStyles.warningStack}>
              {(taxWarnings.length ? taxWarnings : ['GlobalTaxEngine will refuse to invent a tax rate when no statutory source is available.']).map(item => (
                <span key={item}><AlertTriangle size={13} /> {item}</span>
              ))}
            </div>
          </div>

          <div className={hudStyles.panel}>
            <div className={hudStyles.panelHeader}>
              <div className={hudStyles.panelTitle}>
                <Landmark size={18} />
                <div>
                  <span>Treasury sweep</span>
                  <h2>Idle Capital Control</h2>
                </div>
              </div>
              <span className={hudStyles.statusPill}>{treasuryEvaluation?.status || treasuryState.status}</span>
            </div>
            <div className={hudStyles.sovereigntyGrid}>
              <article>
                <span>Available</span>
                <strong>{formatMoney(treasuryEvaluation?.liquidity?.availableToSweep || 0, treasuryEvaluation?.currency || manualInvoice.currency)}</strong>
                <small>Policy-cleared sweep candidate</small>
              </article>
              <article>
                <span>Required buffer</span>
                <strong>{formatMoney(treasuryEvaluation?.liquidity?.requiredBuffer || 0, treasuryEvaluation?.currency || manualInvoice.currency)}</strong>
                <small>Operating, runway, tax and variance reserve</small>
              </article>
              <article>
                <span>Target sleeve</span>
                <strong>{treasuryEvaluation?.policy?.targetSleeve || 'POLICY_PENDING'}</strong>
                <small>{treasuryEvaluation?.policy?.benchmarkCode || 'Benchmark source required'}</small>
              </article>
              <article>
                <span>Proof</span>
                <strong>{treasuryEvaluation?.proof?.hash?.slice(0, 18) || 'NO_PROOF'}</strong>
                <small>{treasuryState.lastReceipt?.executionStatus || 'No sweep command yet'}</small>
              </article>
            </div>
            <div className={hudStyles.featureActions}>
              <button type="button" className={hudStyles.primaryButton} onClick={runTreasurySweep} disabled={!!processing}>
                {processing === 'treasury_sweep' ? <RefreshCw className="animate-spin" size={15} /> : <Coins size={15} />}
                Execute Governed Sweep
              </button>
              <button type="button" className={hudStyles.secondaryButton} onClick={() => hydrate('refresh')} disabled={refreshing}>
                <RefreshCw size={15} className={refreshing ? 'animate-spin' : ''} /> Resync Sources
              </button>
            </div>
            <div className={hudStyles.warningStack}>
              {(treasuryEvaluation?.warnings?.length ? treasuryEvaluation.warnings : ['Sweep execution is blocked unless balance, buffer, benchmark and approval gates pass.']).map(item => (
                <span key={item}><ShieldCheck size={13} /> {item}</span>
              ))}
            </div>
          </div>

          <div className={hudStyles.panel} style={{ gridColumn: '1 / -1' }}>
            <div className={hudStyles.panelHeader}>
              <div className={hudStyles.panelTitle}>
                <BadgeCheck size={18} />
                <div>
                  <span>Live source mesh</span>
                  <h2>Billing Nucleus Heartbeat</h2>
                </div>
              </div>
              <strong>{flightDeck.sourceLabel}</strong>
            </div>
            <div className={hudStyles.sourceMeshGrid}>
              {sourceRows.map(source => (
                <article key={source.key} data-live={source.live ? 'true' : 'false'}>
                  <span>{source.label || source.key}</span>
                  <strong>{source.status}</strong>
                  <small>{source.error || 'Source is contributing to command readiness.'}</small>
                </article>
              ))}
            </div>
          </div>
        </section>
      )}

      {activeTab === 'automation' && (
        <section className={hudStyles.splitGrid}>
          <div className={hudStyles.panel}>
            <div className={hudStyles.panelHeader}>
              <div className={hudStyles.panelTitle}>
                <Calendar size={18} />
                <div>
                  <span>Autonomous revenue ops</span>
                  <h2>Billing Automation</h2>
                </div>
              </div>
            </div>
            <div className={hudStyles.featureGrid}>
              <article className={hudStyles.featureCard}>
                <header><span>Monthly Billing</span><Mail size={18} /></header>
                <strong>Generate and notify</strong>
                <small>Runs the server-side monthly billing controller for active subscriptions.</small>
                <div className={hudStyles.featureActions}>
                  <button type="button" className={hudStyles.primaryButton} onClick={runAutoBilling} disabled={!!processing}>
                    {processing === 'auto_billing' ? <RefreshCw className="animate-spin" size={15} /> : <Mail size={15} />} Run Now
                  </button>
                </div>
              </article>
              <article className={hudStyles.featureCard}>
                <header><span>Dynamic Pricing</span><Gauge size={18} /></header>
                <strong>{Math.round(riskScore * 100)}% risk input</strong>
                <small>Reprices active tenants against cashflow risk.</small>
                <div className={hudStyles.featureActions}>
                  <button type="button" className={hudStyles.primaryButton} onClick={applyDynamicPricing} disabled={!!processing}>
                    {processing === 'dynamic_pricing' ? <RefreshCw className="animate-spin" size={15} /> : <BarChart3 size={15} />} Reprice
                  </button>
                </div>
              </article>
              <article className={hudStyles.featureCard}>
                <header><span>Settlement Preview</span><Coins size={18} /></header>
                <strong>{blockchainPreview?.gasFee ? `${blockchainPreview.gasFee} ETH` : 'Ready'}</strong>
                <small>{blockchainPreview?.estimatedTime || 'Preview future settlement timing and network cost.'}</small>
                <div className={hudStyles.featureActions}>
                  <button type="button" className={hudStyles.secondaryButton} onClick={previewSettlement} disabled={!!processing}>
                    {processing === 'settlement_preview' ? <RefreshCw className="animate-spin" size={15} /> : <CopyCheck size={15} />} Simulate
                  </button>
                </div>
              </article>
              <article className={hudStyles.featureCard}>
                <header><span>Treasury Sweep</span><Landmark size={18} /></header>
                <strong>{treasuryEvaluation?.status || treasuryState.status}</strong>
                <small>{treasuryEvaluation ? `${formatMoney(treasuryEvaluation.liquidity?.availableToSweep || 0, treasuryEvaluation.currency)} policy candidate` : 'Evaluate idle capital against operating buffers.'}</small>
                <div className={hudStyles.featureActions}>
                  <button type="button" className={hudStyles.primaryButton} onClick={runTreasurySweep} disabled={!!processing}>
                    {processing === 'treasury_sweep' ? <RefreshCw className="animate-spin" size={15} /> : <Coins size={15} />} Sweep
                  </button>
                </div>
              </article>
              <article className={hudStyles.featureCard}>
                <header><span>Dunning Ladder</span><AlertTriangle size={18} /></header>
                <strong>{dunningRecommendations.length} targets</strong>
                <small>{dunningRecommendations.filter(item => item.gateStatus === 'READY').length} ready, {dunningRecommendations.filter(item => item.gateStatus !== 'READY').length} held by compliance gates.</small>
                <div className={hudStyles.featureActions}>
                  <button
                    type="button"
                    className={hudStyles.secondaryButton}
                    onClick={() => dunningRecommendations[0] && runDunningIntervention(dunningRecommendations[0])}
                    disabled={!!processing || !dunningRecommendations.length}
                  >
                    {processing === 'dunning_intervention' ? <RefreshCw className="animate-spin" size={15} /> : <AlertTriangle size={15} />} Run Top Gate
                  </button>
                </div>
              </article>
            </div>
          </div>

          <div className={hudStyles.panel}>
            <div className={hudStyles.panelHeader}>
              <div className={hudStyles.panelTitle}>
                <BadgeCheck size={18} />
                <div>
                  <span>Tenant credit</span>
                  <h2>Risk and Pricing Matrix</h2>
                </div>
              </div>
            </div>
            <div className={hudStyles.timeline}>
              {Object.keys(creditScores).length === 0 ? (
                <div className={hudStyles.empty}>No tenant credit scores returned yet.</div>
              ) : Object.entries(creditScores).slice(0, 12).map(([tenant, score]) => (
                <div key={tenant} className={hudStyles.timelineItem}>
                  <span>{tenant}</span>
                  <strong>{score}/100 credit health</strong>
                  <small>{score >= 75 ? 'Eligible for annual prepay incentive' : score >= 50 ? 'Monitor payment behavior' : 'Route to collections vigilance'}</small>
                </div>
              ))}
              {pricingResult && (
                <div className={hudStyles.timelineItem}>
                  <span>PRICING RESULT</span>
                  <strong>{Object.keys(pricingResult).length} subscriptions updated</strong>
                  <small>{Object.entries(pricingResult).slice(0, 3).map(([tenant, price]) => `${tenant}: ${formatMoney(price)}`).join(' | ')}</small>
                </div>
              )}
            </div>
          </div>
        </section>
      )}

      {activeTab === 'warroom' && (
        <section className={hudStyles.splitGrid}>
          <div className={hudStyles.panel}>
            <div className={hudStyles.panelHeader}>
              <div className={hudStyles.panelTitle}>
                <Gavel size={18} />
                <div>
                  <span>Legal collections</span>
                  <h2>Receivables Seizure Workflow</h2>
                </div>
              </div>
            </div>
            <form className={hudStyles.formGrid} onSubmit={initiateSeizure}>
              <div className={hudStyles.field}>
                <label>Invoice ID</label>
                <input value={seizure.invoiceId} onChange={event => setSeizure(prev => ({ ...prev, invoiceId: event.target.value }))} placeholder="INV-..." required />
              </div>
              <div className={`${hudStyles.field} ${hudStyles.fieldFull}`}>
                <label>Court</label>
                <div className={hudStyles.courtPicker}>
                  <div className={hudStyles.courtSearchBox}>
                    <Search size={15} />
                    <input
                      value={courtSearch}
                      onChange={event => {
                        setCourtSearch(event.target.value);
                        setSeizure(prev => ({ ...prev, courtId: '' }));
                      }}
                      placeholder="Search court, country, bloc or court type"
                      required={!seizure.courtId}
                    />
                  </div>
                  <div className={hudStyles.courtResults}>
                    {courts.length === 0 ? (
                      <button type="button" className={hudStyles.courtSeedButton} onClick={seedCourtRegistry} disabled={!!processing}>
                        <Globe2 size={14} /> Seed Global Court Registry
                      </button>
                    ) : courtSearchResults.length === 0 ? (
                      <div className={hudStyles.courtNoResults}>
                        <strong>No court matched this query.</strong>
                        <span>Try jurisdiction code, court type, city, bloc, or sync the registry.</span>
                      </div>
                    ) : courtSearchResults.map(court => (
                      <button
                        key={court._id || court.id || court.name}
                        type="button"
                        className={(court._id || court.id) === seizure.courtId ? hudStyles.courtOptionActive : hudStyles.courtOption}
                        onClick={() => selectCourt(court)}
                      >
                        <strong>{court.name}</strong>
                        <span>{court.jurisdiction || 'GLOBAL'} • {court.type || 'Court'} • {court.location || court.economicBloc || 'Registry'}</span>
                      </button>
                    ))}
                  </div>
                  <div className={hudStyles.courtRegistryMeta}>
                    <span>{courtRegistryStatus}</span>
                    <strong>{courts.length} courts</strong>
                    {selectedCourt && <small>{selectedCourt.jurisdiction || 'GLOBAL'} • {selectedCourt.economicBloc || selectedCourt.courtLevel || 'verified jurisdiction'} • {selectedCourt.sourceAuthority || 'public registry'}</small>}
                    <button type="button" onClick={seedCourtRegistry} disabled={!!processing}>
                      {processing === 'court_registry_seed' ? <RefreshCw className="animate-spin" size={13} /> : <Globe2 size={13} />}
                      Sync registry
                    </button>
                  </div>
                  {selectedCourt && (
                    <div className={hudStyles.courtIntel}>
                      <div>
                        <span>Routing score</span>
                        <strong>{selectedCourt.routingScore || 80}/100</strong>
                      </div>
                      <div>
                        <span>Matters</span>
                        <strong>{asList(selectedCourt.matterTypes).slice(0, 3).join(' / ') || selectedCourt.type || 'legal routing'}</strong>
                      </div>
                      <div>
                        <span>Filing</span>
                        <strong>{asList(selectedCourt.filingChannels).slice(0, 2).join(' / ') || 'registry filing'}</strong>
                      </div>
                      <div>
                        <span>Enforcement</span>
                        <strong>{asList(selectedCourt.enforcementRoutes).slice(0, 2).join(' / ') || 'writ or attachment'}</strong>
                      </div>
                      <div className={hudStyles.courtIntelFull}>
                        <span>Appeal path</span>
                        <strong>{asList(selectedCourt.appealPath).join(' -> ') || 'superior review -> apex review'}</strong>
                      </div>
                    </div>
                  )}
                </div>
              </div>
              <div className={`${hudStyles.field} ${hudStyles.fieldFull}`}>
                <label>Reason</label>
                <textarea value={seizure.reason} onChange={event => setSeizure(prev => ({ ...prev, reason: event.target.value }))} placeholder="Non-payment, final notice sent, client ledger verified..." required />
              </div>
              <div className={hudStyles.fieldFull}>
                <button type="submit" className={hudStyles.dangerButton} disabled={!!processing}>
                  {processing === 'seizure' ? <RefreshCw className="animate-spin" size={15} /> : <Gavel size={15} />} Lodge Seizure
                </button>
              </div>
            </form>
            {seizureResult && (
              <div className={hudStyles.timelineItem}>
                <span>COURT REF</span>
                <strong>{seizureResult.courtRef}</strong>
                <small>{seizureResult.sealHash}</small>
              </div>
            )}
          </div>

          <div className={hudStyles.panel}>
            <div className={hudStyles.panelHeader}>
              <div className={hudStyles.panelTitle}>
                <Crosshair size={18} />
                <div>
                  <span>Market capture</span>
                  <h2>Competitive Pricing Control</h2>
                </div>
              </div>
            </div>
            <form className={hudStyles.formGrid} onSubmit={activateCompetitivePricing}>
              <div className={hudStyles.field}>
                <label>Tenant ID</label>
                <input value={pricing.tenantId} onChange={event => setPricing(prev => ({ ...prev, tenantId: event.target.value }))} placeholder="TENANT-ID" required />
              </div>
              <div className={hudStyles.field}>
                <label>Undercut margin</label>
                <input type="number" min="1" max="20" value={pricing.margin} onChange={event => setPricing(prev => ({ ...prev, margin: event.target.value }))} />
              </div>
              <div className={hudStyles.fieldFull}>
                <button type="submit" className={hudStyles.primaryButton} disabled={!!processing}>
                  {processing === 'competitive_pricing' ? <RefreshCw className="animate-spin" size={15} /> : <Crosshair size={15} />} Reprice Tenant
                </button>
              </div>
            </form>
            {competitiveResult && (
              <div className={hudStyles.timelineItem}>
                <span>{competitiveResult.competitorRef}</span>
                <strong>{formatMoney(competitiveResult.oldPrice || 0)} to {formatMoney(competitiveResult.newPrice || 0)}</strong>
                <small>Price movement sealed for audit review.</small>
              </div>
            )}
          </div>

          <div className={hudStyles.panel} style={{ gridColumn: '1 / -1' }}>
            <div className={hudStyles.panelHeader}>
              <div className={hudStyles.panelTitle}>
                <AlertTriangle size={18} />
                <div>
                  <span>Neural dunning</span>
                  <h2>Forensic Collections Ladder</h2>
                </div>
              </div>
              <span className={hudStyles.statusPill}>{dunningState.status}</span>
            </div>
            <div className={hudStyles.dunningGrid}>
              {dunningRecommendations.length === 0 ? (
                <div className={hudStyles.empty}>No dunning candidates. Overdue invoices or a live dunning source will activate this rail.</div>
              ) : dunningRecommendations.slice(0, 8).map(recommendation => (
                <article key={recommendation.traceId || recommendation.id} data-status={recommendation.gateStatus}>
                  <div>
                    <span>{recommendation.stage} • {recommendation.channel}</span>
                    <strong>{recommendation.client || recommendation.clientId}</strong>
                    <p>{recommendation.nextAction}</p>
                    <small>{recommendation.complianceWarnings?.[0] || `Proof ${recommendation.proof?.hash?.slice(0, 18)}`}</small>
                  </div>
                  <button
                    type="button"
                    className={recommendation.gateStatus === 'READY' ? hudStyles.primaryButton : hudStyles.secondaryButton}
                    onClick={() => runDunningIntervention(recommendation)}
                    disabled={!!processing}
                  >
                    {processing === 'dunning_intervention' ? <RefreshCw className="animate-spin" size={14} /> : <Zap size={14} />}
                    {recommendation.gateStatus === 'READY' ? 'Dispatch' : 'Record Hold'}
                  </button>
                </article>
              ))}
            </div>
          </div>
        </section>
      )}

      {disputeModal.open && (
        <div className={hudStyles.modalOverlay}>
          <div className={hudStyles.modal}>
            <div className={hudStyles.panelHeader}>
              <div className={hudStyles.panelTitle}>
                <Scale size={18} />
                <div>
                  <span>Dispute mediator</span>
                  <h2>{disputeModal.invoiceId}</h2>
                </div>
              </div>
            </div>
            <div className={`${hudStyles.field} ${hudStyles.fieldFull}`}>
              <label>Reason</label>
              <textarea value={disputeModal.reason} onChange={event => setDisputeModal(prev => ({ ...prev, reason: event.target.value }))} placeholder="State the dispute reason and evidence..." />
            </div>
            <div className={hudStyles.featureActions}>
              <button type="button" className={hudStyles.primaryButton} onClick={submitDispute} disabled={processing === 'dispute'}>
                {processing === 'dispute' ? <RefreshCw className="animate-spin" size={15} /> : <CheckCircle size={15} />} Submit
              </button>
              <button type="button" className={hudStyles.secondaryButton} onClick={() => setDisputeModal({ open: false, invoiceId: '', reason: '' })}>
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default BillingHUD;
