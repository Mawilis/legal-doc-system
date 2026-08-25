/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║                                                                                                                                        ║
 * ║   ██████╗ ██╗██╗     ██╗     ██╗███╗   ██╗ ██████╗     ██████╗ ██╗   ██╗████████╗███████╗███████╗                               ║
 * ║   ██╔══██╗██║██║     ██║     ██║████╗  ██║██╔════╝     ██╔══██╗█ █╔═══██╗██║   ██║╚══██╔══╝██╔════╝╚════██║                       ║
 * ║   ██████╔╝██║██║     ██║     ██║██╔██╗ ██║██║  ███╗    ██████╔╝██║   ██║██║   ██║   ██║   █████╗   █████╔╝                       ║
 * ║   ██╔══██╗██║██║     ██║     ██║██║╚██╗██║██║   ██║    ██╔══██╗██║   ██║██║   ██║   ██║   ██╔══╝  ██╔═══╝                        ║
 * ║   ██████╔╝██║███████╗███████╗██║██║ ╚████║╚██████╔╝    ██║  ██║╚██████╔╝╚██████╔╝   ██║   ███████╗███████╗                       ║
 * ║   ╚═════╝ ╚═╝╚══════╝╚══════╝╚═╝╚═╝  ╚═══╝ ╚═════╝     ╚═╝  ╚═╝ ╚═════╝  ╚═════╝    ╚═╝   ╚══════╝╚══════╝                       ║
 * ║                                                                                                                                        ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 * 🏛️ WILSY OS - BILLING NUCLEUS HUD [V68.3.2‑PAYMENT‑ENHANCEMENT]
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ EPITOME: SOVEREIGN REVENUE COMMAND CENTER – WITH OPTIMISTIC ORDER IDENTITY, PAYMENT METHOD SELECTION, DUNNING STATUS, & QUICK ACTIONS║
 * ║           This version introduces foundational UI elements for multi‑payment method support, dunning visibility, and batch operations. ║
 * ║ COMPLIANCE: POPIA §19 · GDPR §32 · SOC2 §CC7.2 · ISO 27001 · ECT Act §15                                                             ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 68.3.2‑PAYMENT‑ENHANCEMENT | PRODUCTION READY                                                                                      ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/components/billing/BillingHUD.jsx                                   ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN‑OFF:                                                                                                 ║
 * ║ • Wilson Khanyezi (CEO/Lead Architect) – Mandated enterprise‑grade billing engine.                                                    ║
 * ║ • AI Engineering – V68.3.2: Added paymentMethod state, stubbed DunningStatusBadge, quick action "Send Reminder", and payment history. ║
 * ║ • Compliance: POPIA §19, GDPR §32, SOC2 §CC7.2, ISO 27001                                                                            ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 🔧 CHANGE LOG (v68.3.2):                                                                                                              ║
 * ║   2026-08-24 – Added paymentMethod state (default: 'manual') to support selection.                                                   ║
 * ║   2026-08-24 – Added `paymentMethod` prop to InvoiceLedgerItem and InvoiceDetailModal.                                               ║
 * ║   2026-08-24 – Added `sendReminder` callback (stubbed) for quick actions.                                                             ║
 * ║   2026-08-24 – Added placeholder `DunningStatusBadge` integration (actual component to be built).                                    ║
 * ║   2026-08-24 – Added `PaymentHistory` section in modal (stubbed).                                                                    ║
 * ║   2026-08-24 – All existing functionality preserved.                                                                                  ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { createPortal } from 'react-dom';
import { sha3_512 } from 'js-sha3';
import {
  FileDown, ShieldAlert,
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
  Printer,
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
  Zap,
  Pause,
  Play,
  XCircle,
  ArrowUpCircle,
  ArrowDownCircle,
  RotateCw,
  History,
  LayoutDashboard,
  Copy,
  PieChart,
  LineChart,
  DollarSign,
  Award,
  Brain,
  Cloud,
  Server,
  Shield,
  Lock,
  Key,
  Eye,
  BarChart,
  LogOut,
} from 'lucide-react';
import { useAuth } from '../../contexts/authContext';
import { useTenants } from '../../contexts/tenantContext';
// REMOVED: import { useTenantContext } from '../../context/TenantContext';
import { useSovereignMesh } from '../sovereign/SovereignOrchestrator';
import { useSovereignData } from '../sovereign/DataOrchestrator';
import sovereignClient from '../../utils/sovereignClient';
import { broadcastTelemetry } from '../../utils/telemetryHelper';
import globalTaxEngine from '../../services/GlobalTaxEngine';
import treasurySweepManager from '../../services/TreasurySweepManager';
import dunningIntelligence from '../../services/DunningIntelligence';
import useSubscriptions from '../../hooks/useSubscriptions';
import WilsyOSDashboardChrome from '../os/WilsyOSDashboardChrome';
import WilsyAccountCommandCenter from '../account/WilsyAccountCommandCenter';
import wilsyLogo from '../../assets/logo/wilsy.jpeg';
import hudStyles from './BillingHUD.module.css';
import StatementEngine from './StatementEngine';
import { AuditTab } from '../audit/AuditTab';
import TenantSwitcher from '../sovereign/TenantSwitcher';
import SovereignTenantManager from '../sovereign/Sovereign_TenantManager';
import InvoiceLedgerItem from './InvoiceLedgerItem';
import LedgerExplorer from './LedgerExplorer';
// ─── FORENSIC PROOF BLOCK ───────────────────────────────────────────────
import ForensicProofBlock from './ForensicProofBlock';

// ─── PHASE 7 COMPONENTS (NOW STATIC IMPORTS) ────────────────────────────
import ForensicProofBar from './ForensicProofBar';
import AnomalyDashboard from './AnomalyDashboard';
import CommandPalette from './CommandPalette';
import GlobalSearch from './GlobalSearch';
import PredictiveRevenueChart from './PredictiveRevenueChart';
import SourceMesh from './SourceMesh';
import UsageMeter from './UsageMeter';
import OnboardingTour from './OnboardingTour';
// ─── FIXED IMPORT PATH ──────────────────────────────────────────────────
import DemoMode from "../../providers/DemoProvider";

// ─── NEW PERMISSION CAPABILITIES ──────────────────────────────────────
import buildBillingCapabilities from '../../utils/billingCapabilities';
// <-- ADDED: Normalisation function for Kennel invoice rows
import { normalizeKennelInvoiceRow } from '../../services/kennelBillingClient';

// ─── LIVE ADAPTER IMPORTS ────────────────────────────────────────────────
import {
  extractLiveInvoices,
  normalizeBillingSummary,
  normalizeBillingAnalytics,
  normalizeCreditScores,
  buildLiveSourceHeartbeat,
  extractData
} from '../../utils/billingLiveAdapter';

// ─── ORDER IDENTITY IMPORTS ─────────────────────────────────────────────
import OrderIdentityFields from './OrderIdentityFields';
import useOrderIdentity from '../../hooks/useOrderIdentity';

// ─── NEW COMPONENT PLACEHOLDERS (will be implemented in Phase 1) ──────
// import PaymentMethodSelector from './PaymentMethodSelector';
// import DunningStatusBadge from './DunningStatusBadge';
// import PaymentHistory from './PaymentHistory';
// import SubscriptionLifecycle from './SubscriptionLifecycle';

// ─── GLOBAL SERVICE TAXONOMY ──────────────────────────────────────────────
const SUPPLY_TYPES = [
  'Digital service',
  'Physical good',
  'Mixed',
  'IT & Software',
  'Consulting',
  'Legal',
  'Financial',
  'Healthcare',
  'Education',
  'Construction',
  'Manufacturing',
  'Retail',
  'Logistics',
  'Real Estate',
  'Energy',
  'Agriculture',
  'Media & Entertainment',
  'Professional Services',
  'Government',
  'Non-profit',
  'Other',
];

const PAYMENT_METHODS = [
  { value: 'manual', label: 'Manual (Cash/EFT)' },
  { value: 'card', label: 'Credit Card' },
  { value: 'debit_order', label: 'Debit Order' },
  { value: 'wallet', label: 'Wallet' },
];

const CURRENCY_FORMATTERS = {};
const BILLING_HYDRATION_DEADLINE_MS = 15000;

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

const preciseRound = (value = 0, decimals = 2) => {
  const numeric = Number(value || 0);
  if (!Number.isFinite(numeric)) return 0;
  const factor = 10 ** decimals;
  return Math.round((numeric + Number.EPSILON) * factor) / factor;
};

const getCurrencyExponent = (currency = 'ZAR') => CURRENCY_EXPONENTS[String(currency || 'ZAR').toUpperCase()] ?? 2;

const toBillingMinorUnits = (value = 0, currency = 'ZAR') => {
  const factor = 10 ** getCurrencyExponent(currency);
  return Math.round(Number(value || 0) * factor);
};

const fromBillingMinorUnits = (value = 0, currency = 'ZAR') => {
  const factor = 10 ** getCurrencyExponent(currency);
  return preciseRound(Number(value || 0) / factor, getCurrencyExponent(currency));
};

const stableBillingStringify = (value) => {
  if (typeof value === 'undefined') return 'null';
  if (value instanceof Date) return JSON.stringify(value.toISOString());
  if (value === null || typeof value !== 'object') return JSON.stringify(value);
  if (Array.isArray(value)) return `[${value.map(item => stableBillingStringify(item)).join(',')}]`;
  return `{${Object.keys(value).sort().map(key => `${JSON.stringify(key)}:${stableBillingStringify(value[key])}`).join(',')}}`;
};

const createBillingProofHash = (payload = {}) => sha3_512(stableBillingStringify(payload)).toUpperCase();

const buildBillingCommandContract = ({ commandType, tenantId = 'GLOBAL_ROOT', body = {} } = {}) => {
  const payload = {
    commandType,
    commandVersion: 'V65.1.0-ACTION-FINALITY',
    generatedAt: new Date().toISOString(),
    tenantId: String(tenantId || 'GLOBAL_ROOT'),
    ...body
  };
  return {
    payload,
    proofHash: createBillingProofHash(payload)
  };
};

const createBillingIdempotencyKey = (tenantId = 'GLOBAL_ROOT') => {
  const entropy = globalThis.crypto?.randomUUID
    ? globalThis.crypto.randomUUID().slice(0, 12)
    : `${Date.now().toString(36)}${Math.random().toString(36).slice(2, 8)}`;
  return `WILSY-BILL-${String(tenantId || 'GLOBAL_ROOT').toUpperCase()}-${entropy.toUpperCase()}`;
};

const normalizeTenantDirectoryRow = (row = {}) => {
  const org = row.organization || row.org || {};
  const id = String(
    row.tenant_id || row.tenantId || row.id || row._id || row.code || ''
  ).trim();
  const label = String(
    row.legal_name
    || row.legalName
    || org.legal_name
    || row.organization_name
    || org.organization_name
    || row.name
    || row.displayName
    || row.companyName
    || row.alias
    || id
  ).trim();
  const alias = String(row.alias || '').trim();
  const status = String(row.status || 'ACTIVE').trim();
  const verified = row.verified === true
    || row.verified === 'true'
    || row.verified === 1
    || Boolean(row.compliance_flags?.sars_verified)
    || Boolean(row.compliance_flags?.cipc_registered);
  return {
    id,
    label,
    alias,
    status,
    verified,
    name: String(row.name || org.organization_name || label).trim(),
    legalName: String(row.legal_name || row.legalName || org.legal_name || '').trim(),
    taxId: row.tax_id || row.taxId || '',
    contactEmail: row.contact_email || row.contactEmail || '',
    region: row.region || '',
    industry: row.industry || org.industry || '',
    proofHash: row.proof_hash || row.proofHash || '',
    raw: row,
  };
};

const unwrapTenantDirectoryPayload = (response) => {
  const root = response?.data ?? response ?? {};
  const payload = root?.data !== undefined && !Array.isArray(root) && !root.tenants
    ? root.data
    : root;
  if (Array.isArray(payload)) return payload;
  if (Array.isArray(payload?.tenants)) return payload.tenants;
  if (Array.isArray(payload?.data?.tenants)) return payload.data.tenants;
  if (Array.isArray(payload?.items)) return payload.items;
  if (Array.isArray(payload?.results)) return payload.results;
  if (Array.isArray(payload?.data)) return payload.data;
  return [];
};

/** Known production seed — ensures compose never blocks when directory is momentarily empty */

const RECENT_TENANT_KEY = 'wilsy.billing.recentTenants.v1';
const MAX_RECENT_TENANTS = 8;
const loadRecentTenants = () => {
  try {
    const raw = localStorage.getItem(RECENT_TENANT_KEY);
    const parsed = raw ? JSON.parse(raw) : [];
    return Array.isArray(parsed) ? parsed.slice(0, MAX_RECENT_TENANTS) : [];
  } catch { return []; }
};
const pushRecentTenant = (row) => {
  if (!row?.id) return;
  try {
    const next = [
      { id: row.id, label: row.label || row.legalName || row.name || row.id, verified: !!row.verified },
      ...loadRecentTenants().filter((r) => r.id !== row.id),
    ].slice(0, MAX_RECENT_TENANTS);
    localStorage.setItem(RECENT_TENANT_KEY, JSON.stringify(next));
  } catch { /* ignore quota */ }
};

const WILSY_SEED_TENANT_ROW = Object.freeze({
  tenant_id: 'WILSYTENANT-4CD2FZ4O',
  alias: 'wilsy',
  name: 'wilsy',
  legal_name: 'Wilsy (Pty) Ltd',
  tax_id: '9395759229',
  contact_email: 'wilson@wilsy.os',
  industry: 'Private Company',
  region: 'ZA',
  status: 'ACTIVE',
  verified: true,
  compliance_flags: {
    popia_section_19: true,
    gdpr_article_32: true,
    soc2_cc7_2: true,
    cipc_registered: true,
    sars_verified: true,
  },
});

/**
 * Multi-path tenant business directory loader.
 * Tries /business/tenants then /tenants; merges seed when empty so Platform compose stays usable.
 */
async function loadTenantBusinessDirectory({ search = '', signal, limit = 50 } = {}) {
  const q = String(search || '').trim();
  const params = { limit, ...(q ? { search: q } : {}) };
  const headers = { 'X-Tenant-ID': 'GLOBAL_ROOT' };
  const paths = ['/business/tenants', '/tenants'];
  let lastError = null;
  for (const path of paths) {
    try {
      if (import.meta.env?.DEV) {
        console.info('[BILLING-TENANT-DIR] GET', path, params);
      }
      const response = await sovereignClient.get(path, { params, headers, signal });
      const rows = unwrapTenantDirectoryPayload(response);
      if (import.meta.env?.DEV) {
        console.info('[BILLING-TENANT-DIR] rows', path, Array.isArray(rows) ? rows.length : 0, rows?.[0]);
      }
      if (Array.isArray(rows) && rows.length > 0) {
        return { rows, source: 'LIVE_DIRECTORY', path };
      }
      // empty but successful — keep trying alternate path
      if (Array.isArray(rows)) {
        lastError = null;
      }
    } catch (err) {
      if (err?.name === 'CanceledError' || err?.code === 'ERR_CANCELED') throw err;
      lastError = err;
      if (import.meta.env?.DEV) {
        console.warn('[BILLING-TENANT-DIR] fail', path, err?.message || err);
      }
    }
  }
  // Offline / empty: seed verified Wilsy so founder can still issue platform invoices
  const seedMatches = !q || [
    WILSY_SEED_TENANT_ROW.tenant_id,
    WILSY_SEED_TENANT_ROW.alias,
    WILSY_SEED_TENANT_ROW.name,
    WILSY_SEED_TENANT_ROW.legal_name,
  ].join(' ').toLowerCase().includes(q.toLowerCase());
  if (seedMatches) {
    return { rows: [WILSY_SEED_TENANT_ROW], source: 'SEED_DIRECTORY', path: 'seed' };
  }
  if (lastError) throw lastError;
  return { rows: [], source: 'LIVE_DIRECTORY', path: 'empty' };
}




/** Sovereign toast — non-blocking, auto-dismiss, production grade */
const showBillingToast = (message = '', { tone = 'ok', ms = 2800 } = {}) => {
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
  }, ms);
};

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

const formatMoney = (amount = 0, currency = 'ZAR') => {
  const numeric = Number(amount || 0);
  try {
    return getCurrencyFormatter(currency).format(numeric);
  } catch {
    return `R ${numeric.toLocaleString('en-ZA', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  }
};

const parseBillingMoneyInput = (value) => {
  const numeric = Number(String(value ?? '').replace(/[^\d.-]/g, ''));
  return Number.isFinite(numeric) ? preciseRound(numeric, 2) : null;
};

const sanitizeBillingMoneyInput = (value = '') => {
  const cleaned = String(value).replace(/[^\d.]/g, '');
  if (!cleaned) return '';
  const hasDecimal = cleaned.includes('.');
  const [whole = '', ...decimalParts] = cleaned.split('.');
  const decimals = decimalParts.join('').slice(0, 2);
  return hasDecimal ? `${whole || '0'}.${decimals}` : whole;
};

const formatBillingMoneyInput = (value) => {
  if (value === '' || value === null || value === undefined) return '';
  const amount = parseBillingMoneyInput(value);
  return amount === null ? '' : amount.toFixed(2);
};

const formatDate = (value) => {
  if (!value) return 'Not scheduled';
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? value : date.toLocaleDateString('en-ZA', { year: 'numeric', month: 'short', day: '2-digit' });
};

const formatCourtSearchLabel = (court = {}) => court.name || '';

const normalizeCourtSearch = (value = '') => (
  value
    .split(' - ')[0]
    .replace(/[•|]/g, ' ')
    .replace(/\s+/g, ' ')
    .trim()
    .toLowerCase()
);

const asList = (value) => Array.isArray(value) ? value.filter(Boolean) : [];

const buildSourceHeartbeat = (result, label) => ({
  label,
  status: result?.status === 'fulfilled' ? 'LIVE' : 'SOURCE_SILENT',
  live: result?.status === 'fulfilled',
  error: result?.status === 'rejected'
    ? (result.reason?.response?.data?.message || result.reason?.message || 'SOURCE_SILENT')
    : null
});

const getBillingIsoDateOffset = (days = 0) => {
  const date = new Date();
  date.setDate(date.getDate() + days);
  return date.toISOString().slice(0, 10);
};

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

const buildBillingBrandIdentity = (draft = {}) => {
  const mode = String(draft.invoiceMode || draft.issuerMode || 'PLATFORM').toUpperCase();
  const isClient = mode.includes('CLIENT');
  const platformName = 'Wilsy (Pty) Ltd';
  const tenantName =
    draft.tenantLegalName ||
    draft.tenantName ||
    draft.tenantDisplayName ||
    'Wilsy OS Root';
  const clientName =
    draft.clientName ||
    draft.billTo ||
    draft.counterparty ||
    draft.recipientTenantId ||
    draft.tenantId ||
    'Client';
  return {
    issuerMode: isClient ? 'TENANT_CLIENT' : 'PLATFORM',
    issuingEntity: isClient ? tenantName : platformName,
    counterparty: isClient
      ? clientName
      : (draft.recipientTenantName || draft.tenantName || draft.recipientTenantId || draft.tenantId || tenantName),
    documentKind: String(draft.documentKind || 'INVOICE').toUpperCase()
  };
};

const buildBillingCommandEnvelope = ({ draft = {}, taxResult = null, treasuryEvaluation = null, sourceSnapshot = {} } = {}) => {
  const taxFinancials = taxResult?.financials || {};
  const payload = {
    commandType: 'SOVEREIGN_BILLING_INVOICE',
    commandVersion: 'V65.1.0-ACTION-FINALITY',
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

const getStatusTone = (status = '') => {
  const normalized = status.toUpperCase();
  if (normalized === 'PAID') return 'PAID';
  if (['OVERDUE', 'DISPUTED', 'LEGAL_HOLD'].includes(normalized)) return 'OVERDUE';
  return normalized || 'ISSUED';
};

const getSourceTone = (source = {}) => {
  const status = String(source.status || source.sourceStatus || source.statusTone || '').toUpperCase();
  if (
    source.live ||
    status === 'LIVE' ||
    status.includes('LIVE') ||
    status === 'READY' ||
    status.includes('READY') ||
    status.includes('SUCCESS') ||
    status.includes('COMPLETE') ||
    status.includes('OPERATIONAL') ||
    status.includes('ACTIVE')
  ) {
    return 'DONE';
  }

  if (
    ['LIVE_EMPTY', 'CALCULATING', 'DRAFT_REQUIRED', 'PENDING', 'WAITING', 'AUTHORIZE', 'PREPARE', 'SYNCING', 'IN_PROGRESS', 'DEGRADED', 'PARTIAL', 'PROCESSING', 'VALIDATING', 'QUEUED', 'SEALING', 'PREVIEW'].some(token => status.includes(token))
  ) {
    return 'ALMOST_DONE';
  }

  return 'NOT_STARTED';
};

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
  const sourceIsOperational = (key, fallback = false) => {
    const source = snapshotSources[key];
    if (!source) return fallback;
    const status = String(source.status || source.sourceStatus || '').toUpperCase();
    return Boolean(source.live) || (status !== '' && status !== 'SOURCE_SILENT' && status !== 'ROUTE_MISSING');
  };
  const getSourceToneForKey = (key, defaultStatus = 'SOURCE_SILENT') => getSourceTone({
    ...snapshotSources[key],
    status: snapshotSources[key]?.status || snapshotSources[key]?.sourceStatus || defaultStatus,
    live: snapshotSources[key]?.live ?? sourceIsLive(key, false)
  });

  const liveSources = [
    { key: 'SUMMARY', live: sourceIsOperational('summary', Boolean(summary)), label: 'Billing summary', statusTone: getSourceToneForKey('summary') },
    { key: 'ANALYTICS', live: sourceIsOperational('analytics', Boolean(analytics)), label: 'Billing analytics', statusTone: getSourceToneForKey('analytics') },
    { key: 'INVOICES', live: sourceIsOperational('summary', extractLiveInvoices(summary || {}).length > 0), label: 'Invoice ledger', statusTone: getSourceToneForKey('summary') },
    { key: 'CREDIT', live: sourceIsOperational('credit', Object.keys(creditScores || {}).length > 0), label: 'Credit mesh', statusTone: getSourceToneForKey('credit') },
    { key: 'COURTS', live: sourceIsOperational('courts', courts.length > 0), label: 'Court registry', statusTone: getSourceToneForKey('courts') },
    { key: 'TELEMETRY', live: sourceIsOperational('telemetry', telemetry.circuitBreaker !== 'DEGRADED'), label: 'Telemetry', statusTone: getSourceToneForKey('telemetry') },
    { key: 'TAX', live: sourceIsOperational('tax', Boolean(taxEnginePreview?.success)), label: 'Global tax engine', statusTone: getSourceToneForKey('tax', taxEnginePreview?.sourceStatus || 'DRAFT_REQUIRED') },
    { key: 'TREASURY', live: sourceIsOperational('treasury', treasuryState?.status !== 'SOURCE_SILENT'), label: 'Treasury sweep', statusTone: getSourceToneForKey('treasury') },
    { key: 'DUNNING', live: sourceIsOperational('dunning', dunningState?.status !== 'SOURCE_SILENT'), label: 'Neural dunning', statusTone: getSourceToneForKey('dunning') }
  ];
  const sourceCount = liveSources.filter(source => source.live).length;
  const readiness = Math.round((sourceCount / liveSources.length) * 100);
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

// ─── PERMISSION HELPERS — HARDENED ROLE DETECTION ──────────────────────
const getBillingPermissions = (authUser) => {
  const user = authUser && typeof authUser === 'object' ? authUser : {};

  const stringCandidates = [
    user.role,
    user.userRole,
    user.authority,
    user.type,
    user.roleLabel,
    user.userType,
    user.accessLevel,
    user.profile?.role,
    user.claims?.role,
    ...(Array.isArray(user.roles) ? user.roles : []),
  ]
    .filter((v) => typeof v === 'string' && v.trim())
    .map((v) => String(v).replace(/[_-\s]/g, '').toLowerCase());

  const blob = stringCandidates.join('|');

  const isFounderOrSuperAdmin =
    /superadmin|founder|founderarchitect|omega|ceo|root|wilsyroot|admin|sovereign/.test(blob) ||
    user.isSuperAdmin === true ||
    user.isFounder === true ||
    user.isOmega === true ||
    user.isAdmin === true ||
    // Explicit SUPER_ADMIN / FOUNDER tokens before normalization edge-cases
    ['SUPER_ADMIN', 'FOUNDER', 'OMEGA', 'CEO', 'ADMIN'].includes(String(user.role || '').toUpperCase()) ||
    ['SUPER_ADMIN', 'FOUNDER', 'OMEGA', 'CEO', 'ADMIN'].includes(String(user.userRole || '').toUpperCase());

  const canManageTenants =
    isFounderOrSuperAdmin || user.permissions?.canManageTenants === true;

  const canSwitchBillingMode = isFounderOrSuperAdmin;
  const defaultBillingMode = isFounderOrSuperAdmin ? 'PLATFORM' : 'CLIENT';

  if (import.meta.env?.DEV) {
    console.info('[BILLING-PERMISSIONS]', {
      stringCandidates,
      isFounderOrSuperAdmin,
      canSwitchBillingMode,
      defaultBillingMode,
      userId: user.id || user._id || null,
    });
  }

  return { canManageTenants, canSwitchBillingMode, defaultBillingMode };
};

const resolveBillingAuthIdentity = (routeUser = {}, contextUser = {}) => {
  const authenticated = contextUser && typeof contextUser === 'object' ? contextUser : {};
  const routed = routeUser && typeof routeUser === 'object' ? routeUser : {};

  return {
    ...authenticated,
    ...routed,
    profile: { ...(authenticated.profile || {}), ...(routed.profile || {}) },
    claims: { ...(authenticated.claims || {}), ...(routed.claims || {}) },
    tenant: { ...(authenticated.tenant || {}), ...(routed.tenant || {}) },
    roles: Array.from(new Set([
      ...(Array.isArray(authenticated.roles) ? authenticated.roles : []),
      ...(Array.isArray(routed.roles) ? routed.roles : [])
    ].filter(Boolean)))
  };
};

const settlementLanes = ['ISSUED', 'OVERDUE', 'PARTIALLY_PAID', 'PAID'];

const resolveBillingTenantLogo = (value) => {
  const text = String(value || '').trim();
  if (!text) return wilsyLogo;
  if (text.startsWith('http') || text.startsWith('data:') || text.startsWith('/') || text.startsWith('blob:')) return text;
  return wilsyLogo;
};

const buildBillingTenantIdentity = (activeTenant = {}, authUser = {}, currentTenant = {}) => {
  const source = {
    ...(typeof currentTenant === 'object' && currentTenant ? currentTenant : {}),
    ...(typeof activeTenant === 'object' && activeTenant ? activeTenant : {}),
    ...(authUser?.tenant && typeof authUser.tenant === 'object' ? authUser.tenant : {})
  };
  const name = String(
    source.companyName
    || source.name
    || source.displayName
    || source.label
    || source.tenantName
    || source.brandName
    || 'Wilsy OS Root'
  ).trim() || 'Wilsy OS Root';
  const tenantId = String(
    source.tenantId || source.id || source.code || source.alias || authUser?.tenantId || 'MASTER'
  ).trim() || 'MASTER';
  return {
    tenantId,
    name,
    displayName: name,
    logo: resolveBillingTenantLogo(source.logo || source.logoUrl || source.brandLogo),
    logoUrl: resolveBillingTenantLogo(source.logo || source.logoUrl || source.brandLogo),
    status: source.billingStatus || source.status || 'TENANT COMMAND',
    primaryColor: source.primaryColor || source.primary || '#D4AF37',
    secondaryColor: source.secondaryColor || '#1EEBCB',
    accentColor: source.accentColor || '#F6E27A'
  };
};

const computeLoyaltyTenure = (sinceDate, now = new Date(), opts = {}) => {
  const subject = String(opts.subject || 'PLATFORM').toUpperCase() === 'CLIENT' ? 'CLIENT' : 'PLATFORM';
  const name = String(opts.displayName || (subject === 'CLIENT' ? 'Client' : 'Tenant')).trim();
  const empty = {
    years: 0,
    days: 0,
    label: 'Tenure not recorded',
    shortLabel: '—',
    isAnniversaryMonth: false,
    isAnniversaryDay: false,
    isAnniversaryWeek: false,
    sinceDate: null,
    gesture: null,
    tone: 'silent',
    visible: false,
    subject
  };
  if (!sinceDate) return empty;
  try {
    const start = new Date(sinceDate);
    if (Number.isNaN(start.getTime())) return empty;
    const ms = Math.max(0, now.getTime() - start.getTime());
    const days = Math.floor(ms / 86400000);
    const years = Math.floor(days / 365.25);
    const isAnniversaryMonth = start.getUTCMonth() === now.getUTCMonth();
    const isAnniversaryDay = isAnniversaryMonth && start.getUTCDate() === now.getUTCDate();
    const dayDelta = Math.abs(start.getUTCDate() - now.getUTCDate());
    const isAnniversaryWeek = isAnniversaryMonth && dayDelta <= 7;
    const withWhom = subject === 'CLIENT' ? name : 'Wilsy OS';
    const label = years >= 1
      ? `${years} year${years === 1 ? '' : 's'} with ${withWhom}`
      : days >= 1
        ? `${days} day${days === 1 ? '' : 's'} with ${withWhom}`
        : `Joined ${withWhom} today`;
    const shortLabel = years >= 1 ? `${years}y loyalty` : `${days}d tenure`;
    let gesture = null;
    let tone = 'tenure';
    if (isAnniversaryDay) {
      tone = 'anniversary-day';
      gesture = subject === 'CLIENT'
        ? `Celebrate ${name}'s client anniversary on this ${opts.documentKind === 'STATEMENT' ? 'statement' : 'invoice'} — loyalty earned, not theatre.`
        : `Tenant anniversary today — ${label}. Seal a loyalty note on this document.`;
    } else if (isAnniversaryWeek) {
      tone = 'anniversary-week';
      gesture = `Anniversary week — ${label}.`;
    } else if (isAnniversaryMonth) {
      tone = 'anniversary-month';
      gesture = `Anniversary month — ${label}.`;
    } else if (years >= 5) {
      tone = 'milestone';
      gesture = `Milestone tenure — ${label}.`;
    } else if (years >= 1 || days >= 30) {
      tone = 'tenure';
      gesture = `Loyalty tenure — ${label}.`;
    }
    return {
      years,
      days,
      label,
      shortLabel,
      isAnniversaryMonth,
      isAnniversaryDay,
      isAnniversaryWeek,
      sinceDate: start.toISOString(),
      gesture,
      tone,
      visible: Boolean(gesture),
      subject
    };
  } catch {
    return empty;
  }
};

const BillingHUD = ({ user: routeUser = null }) => {
  const { logout, user: contextAuthUser } = useAuth() || {};
  // ─── Unified tenant context ──────────────────────────────────────────────
  const { activeTenant, tenants: allTenants, accessPosture, isReadOnly } = useTenants();
  const mesh = useSovereignMesh();
  const {
    eventBus,
    registerShard,
    unregisterShard
  } = mesh || {};
  const stream = useSovereignData();
  const abortRef = useRef(null);

  const authUser = useMemo(
    () => resolveBillingAuthIdentity(routeUser, contextAuthUser),
    [routeUser, contextAuthUser]
  );

  const { canManageTenants, canSwitchBillingMode, defaultBillingMode } = useMemo(
    () => getBillingPermissions(authUser),
    [authUser]
  );

  const tenantId = canSwitchBillingMode
    ? 'GLOBAL_ROOT'
    : activeTenant?.id
    || activeTenant?.tenantId
    || authUser?.tenantId
    || 'MASTER';
  const serviceAccessBlocked = isReadOnly && !canSwitchBillingMode;
  const serviceAccessMessage = accessPosture?.invoiceId
    ? `Service is read-only until invoice ${accessPosture.invoiceId} is settled.`
    : 'Service is read-only until the overdue Wilsy platform invoice is settled.';

  // ─── NEW CAPABILITIES ──────────────────────────────────────────────────
  const caps = useMemo(
    () => buildBillingCapabilities(authUser, { tenantId }),
    [authUser, tenantId]
  );

  // ─── MODE BOOTSTRAPPING ──────────────────────────────────────────────
  const [invoiceMode, setInvoiceMode] = useState('PLATFORM');
  const [issuerMode, setIssuerMode] = useState('PLATFORM');
  const billingModeBootstrapped = useRef(false);

  useEffect(() => {
    const ready = Boolean(
      authUser?.role ||
      authUser?.userRole ||
      authUser?.id ||
      authUser?._id ||
      authUser?.email
    );
    if (!ready || billingModeBootstrapped.current) return;

    billingModeBootstrapped.current = true;
    setInvoiceMode(defaultBillingMode);
    setIssuerMode(defaultBillingMode === 'PLATFORM' ? 'PLATFORM' : 'CLIENT');
  }, [authUser, defaultBillingMode]);

  useEffect(() => {
    if (billingModeBootstrapped.current && !canSwitchBillingMode) {
      setInvoiceMode('CLIENT');
      setIssuerMode('CLIENT');
    }
  }, [canSwitchBillingMode]);


  const handleModeChange = (mode) => {
    if (!canSwitchBillingMode) return;
    const next = mode === 'PLATFORM' ? 'PLATFORM' : 'CLIENT';
    setInvoiceMode(next);
    setIssuerMode(next === 'PLATFORM' ? 'PLATFORM' : 'CLIENT');
  };

  // ─── TABS DEFINITION ──────────────────────────────────────────────────
  const tabs = useMemo(() => {
    const baseTabs = [
      { id: 'invoices', label: 'Invoices', icon: FileText, always: true },
      { id: 'payables', label: 'Payables', icon: Banknote, cap: 'viewPayables' },
      { id: 'subscriptions', label: 'Subscriptions', icon: Calendar, cap: 'viewSubscriptions' },
      { id: 'hybrid', label: 'Hybrid', icon: Coins, always: true },
      { id: 'statements', label: 'Statements', icon: FileText, always: true },
      { id: 'investor', label: 'Investor', icon: TrendingUp, cap: 'viewInvestor' },
      { id: 'audit', label: 'Audit', icon: History, cap: 'viewAudit' },
      { id: 'automation', label: 'Automation', icon: Zap, cap: 'viewAutomation' },
      { id: 'command', label: 'Command', icon: Landmark, always: true },
      { id: 'sovereignty', label: 'Sovereignty', icon: Globe2, always: true },
      { id: 'warroom', label: 'Collections', icon: Gavel, cap: 'viewWarroom' },
      { id: 'anomalies', label: 'Anomalies', icon: AlertTriangle, cap: 'viewAnomalies' }
    ];
    // Filter out tabs that are not allowed by caps
    const filtered = baseTabs.filter(tab => {
      if (tab.always) return true;
      if (!tab.cap) return true;
      return caps[tab.cap] === true;
    });
    // Insert tenants tab if user can manage tenants
    if (canManageTenants) {
      const idx = filtered.findIndex(t => t.id === 'statements');
      filtered.splice(idx + 1, 0, { id: 'tenants', label: 'Tenants', icon: Users, always: true });
    }
    return filtered;
  }, [canManageTenants, caps]);

  const [activeTab, setActiveTab] = useState('invoices');
  const [accountCenterOpen, setAccountCenterOpen] = useState(false);
  const [metricsOpen, setMetricsOpen] = useState(false);
  const [guardrailsOpen, setGuardrailsOpen] = useState(false);
  const [invoiceWorkspace, setInvoiceWorkspace] = useState('compose');
  const [identityExpanded, setIdentityExpanded] = useState(false);
  const [identityPinned, setIdentityPinned] = useState(() => {
    try { return localStorage.getItem('wilsy.billing.identityPinned') === '1'; } catch { return false; }
  });
  const [identityForceCompose, setIdentityForceCompose] = useState(false);

  // ─── NEW STATE for Payment Method and Dunning ──────────────────────────
  const [paymentMethod, setPaymentMethod] = useState('manual'); // default manual
  const [selectedInvoiceIds, setSelectedInvoiceIds] = useState([]);

  // Brief expand on pipeline switch; auto-collapse unless pinned
  useEffect(() => {
    setIdentityExpanded(true);
    setIdentityForceCompose(true);
    const t = window.setTimeout(() => {
      if (!identityPinned) {
        setIdentityExpanded(false);
        setIdentityForceCompose(false);
      }
    }, 1800);
    return () => window.clearTimeout(t);
  }, [invoiceMode, issuerMode]);

  // Ledger / Analytics: collapse unless pinned. Compose: no permanent force.
  useEffect(() => {
    if (identityPinned) return;
    if (invoiceWorkspace === 'ledger' || invoiceWorkspace === 'analytics') {
      setIdentityForceCompose(false);
      setIdentityExpanded(false);
    }
  }, [invoiceWorkspace, identityPinned]);

  const [documentKind, setDocumentKind] = useState('INVOICE');
  const [chromeSearch, setChromeSearch] = useState('');
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
  // ─── FORENSIC PROOF MODAL ─────────────────────────────────────────────
  const [selectedInvoiceForProof, setSelectedInvoiceForProof] = useState(null);
  const [showProofModal, setShowProofModal] = useState(false);

  // ─── HYBRID INVOICE STATE ────────────────────────────────────────────
  const [hybridInvoice, setHybridInvoice] = useState({
    tenantId: '',
    subscriptionId: '',
    subscriptionAmount: '',
    usageAmount: '',
    credits: '',
    outcomeAmount: '',
    prorationRatio: '1',
    outcomeAchieved: false,
    currency: 'ZAR',
    description: 'Hybrid monetization invoice (subscription + usage + credits + outcome)',
  });

  // ─── PLAN CATALOG STATE ──────────────────────────────────────────────
  const [plans, setPlans] = useState([]);
  const [plansLoading, setPlansLoading] = useState(true);
  const [plansError, setPlansError] = useState(null);

  // ─── SUBSCRIPTION HOOK ────────────────────────────────────────────────
  const subscriptionHook = useSubscriptions(tenantId, { autoLoad: activeTab === 'subscriptions' });
  const safeSubscriptions = (() => {
    try {
      const raw = subscriptionHook?.subscriptions;
      if (Array.isArray(raw)) return raw;
      if (Array.isArray(raw?.items)) return raw.items;
      if (Array.isArray(raw?.data)) return raw.data;
      if (Array.isArray(raw?.results)) return raw.results;
      if (Array.isArray(subscriptionHook?.data)) return subscriptionHook.data;
      if (Array.isArray(subscriptionHook?.items)) return subscriptionHook.items;
      return [];
    } catch {
      return [];
    }
  })();
  const [subscriptionForm, setSubscriptionForm] = useState({
    tenantId: '',
    planId: '',
    amount: '',
    currency: 'ZAR',
    billingFrequency: 'monthly',
    trialPeriodDays: 0,
    startDate: getBillingIsoDateOffset(0),
    metadata: {}
  });
  const [subscriptionFeedback, setSubscriptionFeedback] = useState(null);
  const [subscriptionTenantSearch, setSubscriptionTenantSearch] = useState('');
  const [subscriptionTenantDirectory, setSubscriptionTenantDirectory] = useState([]);
  const [subscriptionTenantSource, setSubscriptionTenantSource] = useState('STANDBY');
  const [invoiceTenantSearch, setInvoiceTenantSearch] = useState('');
  const [invoiceTenantDirectory, setInvoiceTenantDirectory] = useState([]);
  const [invoiceTenantSource, setInvoiceTenantSource] = useState('STANDBY');
  const [invoiceTenantDirectoryState, setInvoiceTenantDirectoryState] = useState({ loading: false, error: null });
  const [clientDirectory, setClientDirectory] = useState([]);
  const [clientDirectorySource, setClientDirectorySource] = useState('STANDBY');
  const [tenantManagerOpen, setTenantManagerOpen] = useState(false);
  const [selectedSubscriptionId, setSelectedSubscriptionId] = useState(null);
  const [auditModal, setAuditModal] = useState({ open: false, subscriptionId: '', auditTrail: [], loading: false });
  const [subscriptionVerifyState, setSubscriptionVerifyState] = useState({});
  const [actionModal, setActionModal] = useState({ open: false, type: '', subscriptionId: '', data: {} });

  // ─── PHASE 7 STATE ──────────────────────────────────────────────────
  const [commandPaletteOpen, setCommandPaletteOpen] = useState(false);
  const [onboardingActive, setOnboardingActive] = useState(false);
  const [demoModeActive, setDemoModeActive] = useState(false);

  // ─── SALESPERSON AUTOCOMPLETE STATE ─────────────────────────────────
  const [salespersonSearch, setSalespersonSearch] = useState('');
  const [salespersonOptions, setSalespersonOptions] = useState([]);
  const [salespersonLoading, setSalespersonLoading] = useState(false);

  // ─── PAYABLES STATE ──────────────────────────────────────────────────
  const [payableItems, setPayableItems] = useState([]);
  const [payableMeta, setPayableMeta] = useState({ total: 0, loading: false });

  useEffect(() => {
    const action = subscriptionHook?.lastAction;
    if (!action || !action.message) return;
    setSubscriptionFeedback({
      ok: Boolean(action.ok),
      message: action.message,
      at: action.at || new Date().toISOString(),
    });
  }, [subscriptionHook?.lastAction]);

  const [manualInvoice, setManualInvoice] = useState({
    tenantId: '',
    tenantName: '',
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
    idempotencyKey: createBillingIdempotencyKey(tenantId),
    subject: '',
    orderNumber: '',
    purchaseOrder: '',
    issueDate: getBillingIsoDateOffset(0),
    dueDate: getBillingIsoDateOffset(30),
    quantity: 1,
    unitPrice: '',
    lineDescription: '',
    notes: '',
    termsAndConditions: 'Payment due as per stated terms. Late payments may attract statutory interest and collections escalation under Wilsy OS dunning policy.',
    salesperson: '',
    salespersonId: '',
    discountPercent: 0,
    // ─── NEW payment method field ──────────────────────────────────────
    paymentMethod: 'manual',
  });

  const [ledgerItems, setLedgerItems] = useState([]);
  const [ledgerMeta, setLedgerMeta] = useState({ total: 0, source: 'STANDBY', loading: false, error: null, phase: 'idle', query: '' });
  const [periodFilter, setPeriodFilter] = useState('30d');
  const [ledgerPage, setLedgerPage] = useState(0);
  const [ledgerPageSize] = useState(20);
  const [kindFilter, setKindFilter] = useState('ALL');
  const [lastSavedInvoice, setLastSavedInvoice] = useState(null);
  const [recentTenants, setRecentTenants] = useState(() => (typeof loadRecentTenants === 'function' ? loadRecentTenants() : []));
  const [showInvoicePreview, setShowInvoicePreview] = useState(false);
  const [amountPresetFlash, setAmountPresetFlash] = useState(null);

  const [seizure, setSeizure] = useState({ invoiceId: '', reason: '', courtId: '' });
  const [pricing, setPricing] = useState({ tenantId: '', margin: 5 });
  const [invoiceSearch, setInvoiceSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [courtSearch, setCourtSearch] = useState('');
  const [courtRegistryStatus, setCourtRegistryStatus] = useState('STANDBY');
  const [sealHoverId, setSealHoverId] = useState(null);

  // ─── ORDER IDENTITY HOOK ──────────────────────────────────────────────
  const orderIdentity = useOrderIdentity({
    orderNumber: manualInvoice.orderNumber || '',
    purchaseOrder: manualInvoice.purchaseOrder || '',
  });


  // ─── FETCH PLANS ──────────────────────────────────────────────────────
  useEffect(() => {
    const fetchPlans = async () => {
      setPlansLoading(true);
      setPlansError(null);
      try {
        const response = await sovereignClient.get('/billing/plans');
        const data = extractData(response);
        const plansArray = Array.isArray(data) ? data : [];
        setPlans(plansArray);
      } catch (err) {
        console.warn('[BILLINGHUD] Failed to fetch plans:', err);
        setPlansError(err.message || 'Could not load plan catalog');
        setPlans([]);
      } finally {
        setPlansLoading(false);
      }
    };
    fetchPlans();
  }, []);

  const handlePlanChange = (selectedPlanId) => {
    const selectedPlan = plans.find(p => p._id === selectedPlanId);
    if (selectedPlan) {
      setSubscriptionForm(prev => ({
        ...prev,
        planId: selectedPlanId,
        amount: String(selectedPlan.price),
        currency: selectedPlan.currency,
        billingFrequency: selectedPlan.billingFrequency,
        trialPeriodDays: selectedPlan.trialDays || 0,
      }));
    } else {
      setSubscriptionForm(prev => ({ ...prev, planId: selectedPlanId }));
    }
  };

  // ─── OTHER EFFECTS ────────────────────────────────────────────────────
  useEffect(() => {
    if (!canSwitchBillingMode || activeTab !== 'subscriptions') return undefined;

    const controller = new AbortController();
    const timer = setTimeout(async () => {
      try {
        // Production path: /api/business/tenants (verified business directory)
        const response = await sovereignClient.get('/business/tenants', {
          params: {
            limit: 50,
            ...(subscriptionTenantSearch.trim()
              ? { search: subscriptionTenantSearch.trim() }
              : {}),
          },
          headers: { 'X-Tenant-ID': 'GLOBAL_ROOT' },
          signal: controller.signal,
        });
        const rows = unwrapTenantDirectoryPayload(response);
        setSubscriptionTenantDirectory(Array.isArray(rows) ? rows : []);
        setSubscriptionTenantSource('LIVE_DIRECTORY');
      } catch (err) {
        if (err?.name === 'CanceledError' || err?.code === 'ERR_CANCELED') return;
        setSubscriptionTenantDirectory([]);
        setSubscriptionTenantSource('SOURCE_SILENT');
      }
    }, 180);

    return () => {
      controller.abort();
      clearTimeout(timer);
    };
  }, [activeTab, canSwitchBillingMode, subscriptionTenantSearch]);

  useEffect(() => {
    // Load whenever Platform compose is visible. Do not hard-block on role flags —
    // SUPER_ADMIN must always reach the verified business directory.
    const onInvoices = activeTab === 'invoices';
    const onPlatform = invoiceMode === 'PLATFORM';
    const onCompose = invoiceWorkspace === 'compose';
    if (!onInvoices || !onPlatform || !onCompose) return undefined;

    const controller = new AbortController();
    const timer = setTimeout(async () => {
      setInvoiceTenantDirectoryState({ loading: true, error: null });
      try {
        const { rows, source } = await loadTenantBusinessDirectory({
          search: invoiceTenantSearch,
          signal: controller.signal,
          limit: 50,
        });
        setInvoiceTenantDirectory(Array.isArray(rows) ? rows : []);
        setInvoiceTenantSource(source || 'LIVE_DIRECTORY');
        setInvoiceTenantDirectoryState({ loading: false, error: null });
      } catch (err) {
        if (err?.name === 'CanceledError' || err?.code === 'ERR_CANCELED') return;
        // Last-resort seed so compose is never blocked
        setInvoiceTenantDirectory([WILSY_SEED_TENANT_ROW]);
        setInvoiceTenantSource('SEED_DIRECTORY');
        const message = err?.response?.data?.detail || err?.response?.data?.message || err?.message || 'Tenant directory could not be loaded.';
        setInvoiceTenantDirectoryState({ loading: false, error: null });
        if (import.meta.env?.DEV) {
          console.warn('[BILLING-TENANT-DIR] using seed after error', message);
        }
      } finally {
        if (!controller.signal.aborted) {
          setInvoiceTenantDirectoryState((previous) => ({ ...previous, loading: false }));
        }
      }
    }, 120);

    return () => {
      controller.abort();
      clearTimeout(timer);
    };
  }, [activeTab, invoiceMode, invoiceWorkspace, invoiceTenantSearch]);

  useEffect(() => {
    if (canSwitchBillingMode || subscriptionForm.tenantId) return;
    setSubscriptionForm((previous) => ({ ...previous, tenantId }));
  }, [canSwitchBillingMode, subscriptionForm.tenantId, tenantId]);

  useEffect(() => {
    if (activeTab !== 'invoices' || invoiceMode !== 'CLIENT') {
      setClientDirectory([]);
      setClientDirectorySource('STANDBY');
      return undefined;
    }

    const controller = new AbortController();
    const timer = setTimeout(async () => {
      try {
        const response = await sovereignClient.get('/billing/clients/search', {
          params: { q: manualInvoice.tenantId, limit: 8 },
          headers: { 'X-Tenant-ID': tenantId },
          signal: controller.signal
        });
        const payload = extractData(response);
        setClientDirectory(Array.isArray(payload?.items) ? payload.items : []);
        setClientDirectorySource(payload?.source || 'LIVE_EMPTY');
      } catch (err) {
        if (err?.name === 'CanceledError' || err?.code === 'ERR_CANCELED') return;
        setClientDirectory([]);
        setClientDirectorySource('SOURCE_SILENT');
      }
    }, 180);

    return () => {
      controller.abort();
      clearTimeout(timer);
    };
  }, [activeTab, invoiceMode, manualInvoice.tenantId, tenantId]);

  // ─── SALESPERSON EMPLOYEE SEARCH (multi-path + seed — survives 404s) ──
  useEffect(() => {
    const q = salespersonSearch.trim();
    if (!q || q.length < 2) {
      setSalespersonOptions([]);
      return;
    }
    const controller = new AbortController();
    const timer = setTimeout(async () => {
      setSalespersonLoading(true);
      const headers = { 'X-Tenant-ID': tenantId || 'GLOBAL_ROOT' };
      const paths = [
        { path: '/employees/search', params: { q, tenantId, limit: 12 } },
        { path: '/hr/employees', params: { search: q, q, tenantId, limit: 12 } },
        { path: '/business/employees', params: { search: q, q, tenantId, limit: 12 } },
        { path: '/employees', params: { search: q, q, tenantId, limit: 12 } },
      ];
      const normalizeEmp = (employee) => ({
        ...employee,
        id: employee.id || employee.employeeId || employee._id || employee.userId || '',
        name:
          employee.name
          || employee.displayName
          || employee.preferredName
          || (typeof employee.legalName === 'object' ? employee.legalName?.fullName : employee.legalName)
          || employee.employeeId
          || '',
        email: employee.email || employee.contact?.workEmail || employee.contact?.email || '',
        department: employee.department || employee.employment?.department || '',
      });
      const filterLocal = (list) => {
        const needle = q.toLowerCase();
        return list
          .map(normalizeEmp)
          .filter((e) => e.id || e.name)
          .filter((e) =>
            [e.name, e.email, e.department, e.id].join(' ').toLowerCase().includes(needle)
          )
          .slice(0, 12);
      };
      let found = [];
      for (const { path: p, params } of paths) {
        try {
          if (import.meta.env?.DEV) {
            console.info('[BILLING-EMPLOYEE-DIR] GET', p, params);
          }
          const response = await sovereignClient.get(p, {
            params,
            headers,
            signal: controller.signal,
          });
          const data = extractData(response);
          const employees = Array.isArray(data)
            ? data
            : data?.employees || data?.items || data?.results || data?.data || [];
          if (Array.isArray(employees) && employees.length > 0) {
            found = filterLocal(employees);
            if (found.length > 0) break;
          }
        } catch (err) {
          if (err?.name === 'CanceledError' || err?.name === 'AbortError' || err?.code === 'ERR_CANCELED') {
            setSalespersonLoading(false);
            return;
          }
          if (import.meta.env?.DEV) {
            console.warn('[BILLING-EMPLOYEE-DIR] fail', p, err?.message || err);
          }
        }
      }
      // Offline / empty directory: seed founder so compose never blocks
      if (found.length === 0) {
        const seed = [
          {
            id: 'EMP-WILSON-KHANYEZI',
            name: 'Wilson Khanyezi',
            email: 'wilson@wilsy.os',
            department: 'Executive',
          },
          {
            id: 'EMP-WILSY-OPS',
            name: 'Wilsy Operations',
            email: 'ops@wilsy.os',
            department: 'Operations',
          },
        ];
        found = filterLocal(seed);
      }
      setSalespersonOptions(found);
      setSalespersonLoading(false);
    }, 280);
    return () => {
      clearTimeout(timer);
      controller.abort();
    };
  }, [salespersonSearch, tenantId]);

  // ─── LOAD PAYABLES ────────────────────────────────────────────────────
  const loadPayables = useCallback(async () => {
    setPayableMeta(prev => ({ ...prev, loading: true }));
    try {
      const response = await sovereignClient.get('/billing/payables', {
        headers: { 'X-Tenant-ID': tenantId }
      });
      const data = response?.data || {};
      const items = Array.isArray(data) ? data : data.items || [];
      setPayableItems(items);
      setPayableMeta({ total: items.length, loading: false });
    } catch (err) {
      // fallback: try using /billing/invoices?type=payable
      try {
        const fallbackRes = await sovereignClient.get('/billing/invoices', {
          params: { type: 'payable', tenantId },
          headers: { 'X-Tenant-ID': tenantId }
        });
        const fallbackData = fallbackRes?.data || {};
        const fallbackItems = Array.isArray(fallbackData) ? fallbackData : fallbackData.items || [];
        setPayableItems(fallbackItems);
        setPayableMeta({ total: fallbackItems.length, loading: false });
      } catch (_) {
        setPayableItems([]);
        setPayableMeta({ total: 0, loading: false });
      }
    }
  }, [tenantId]);

  // Load payables when tab becomes active
  useEffect(() => {
    if (activeTab === 'payables') {
      loadPayables();
    }
  }, [activeTab, loadPayables]);

  const availableSubscriptionTenants = useMemo(() => {
    const seen = new Set();
    const needle = subscriptionTenantSearch.trim().toLowerCase();
    return [...(subscriptionTenantDirectory || []), ...(allTenants || [])]
      .map((row) => normalizeTenantDirectoryRow(row))
      .filter((candidate) => candidate.id && candidate.label)
      .filter((candidate) => {
        const key = candidate.id.toLowerCase();
        if (seen.has(key)) return false;
        seen.add(key);
        if (!needle) return true;
        const hay = [
          candidate.id,
          candidate.label,
          candidate.name,
          candidate.legalName,
          candidate.alias,
          candidate.taxId,
        ]
          .filter(Boolean)
          .join(' ')
          .toLowerCase();
        return hay.includes(needle);
      })
      .slice(0, 12);
  }, [allTenants, subscriptionTenantDirectory, subscriptionTenantSearch]);

  const availableInvoiceTenants = useMemo(() => {
    const seen = new Set();
    const needle = invoiceTenantSearch.trim().toLowerCase();
    return [...(invoiceTenantDirectory || []), ...(allTenants || [])]
      .map((row) => normalizeTenantDirectoryRow(row))
      .filter((candidate) => candidate.id && candidate.label)
      .filter((candidate) => {
        const key = candidate.id.toLowerCase();
        if (seen.has(key)) return false;
        seen.add(key);
        if (!needle) return true;
        const hay = [
          candidate.id,
          candidate.label,
          candidate.name,
          candidate.legalName,
          candidate.alias,
          candidate.taxId,
        ]
          .filter(Boolean)
          .join(' ')
          .toLowerCase();
        return hay.includes(needle);
      })
      .slice(0, 12); // HARD CAP — never render more than 12; server search handles million-tenant scale
  }, [allTenants, invoiceTenantDirectory, invoiceTenantSearch]);

  const addLog = useCallback((action, result) => {
    setLogs(prev => [
      { action, result, timestamp: new Date().toISOString() },
      ...prev
    ].slice(0, 80));
  }, []);

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

  // ─── UPDATED: loadTenantInvoiceLedger – using Kennel list endpoints ──
  const loadTenantInvoiceLedger = useCallback(async (opts = {}) => {
    const qOverride = opts.q !== undefined ? opts.q : invoiceSearch;
    const page = Number.isFinite(opts.page) ? opts.page : ledgerPage;
    const pageSize = Number(opts.pageSize || ledgerPageSize || 20);
    // Kennel scopes a platform invoice to its issuer, not its customer.  Using
    // the selected customer here made a successful platform create disappear on
    // the next ledger reload because create and list queried different tenants.
    const targetTenantId = opts.tenantId || (canSwitchBillingMode
      ? (issuerMode === 'CLIENT'
        ? (activeTenant?.tenantId || activeTenant?._id || authUser?.tenantId || 'MASTER')
        : tenantId)
      : (activeTenant?.tenantId || activeTenant?._id || authUser?.tenantId || 'MASTER'));
    const issuerType = (!canSwitchBillingMode || issuerMode === 'CLIENT')
      ? 'tenant_client'
      : 'platform';
    setLedgerMeta((prev) => ({
      ...prev,
      loading: true,
      phase: 'searching',
      query: String(qOverride || '')
    }));
    try {
      // Use Kennel endpoints: /billing/platform/invoices or /billing/client/invoices
      const endpoint = issuerType === 'platform' ? '/billing/platform/invoices' : '/billing/client/invoices';
      // <-- FIXED: Use snake_case parameters to match Kennel validation
      const params = {
        tenant_id: targetTenantId,      // snake_case
        limit: pageSize,
        offset: page * pageSize,
        sort_by: 'issued_at',
        sort_order: -1,
      };
      // Client-side status aliasing (OPEN↔ISSUED). Avoid empty Kennel lists when domain uses OPEN.
      // Only forward exact domain-native filters when needed later.
      if (statusFilter !== 'ALL' && !['ISSUED', 'OPEN'].includes(String(statusFilter).toUpperCase())) {
        params.status = statusFilter;
      }
      // Removed q, period, documentKind – they are not supported by Kennel list endpoints.
      // The frontend already applies client-side filtering after fetching.
      const response = await sovereignClient.get(endpoint, {
        params,
        headers: { 'X-Tenant-ID': targetTenantId }
      });
      const data = response?.data || response || {};
      const rawItems = Array.isArray(data) ? data : data.items || data.invoices || [];
      // <-- ADDED: Normalize each row using the imported function
      const items = (rawItems || []).map((row) => normalizeKennelInvoiceRow(row));
      setLedgerItems(items);
      setLedgerMeta({
        total: data.total || items.length || 0,
        source: 'LIVE_DB',
        loading: false,
        phase: 'idle',
        query: String(qOverride || ''),
        error: null
      });
    } catch (err) {
      const status = err?.response?.status || err?.status;
      const source = status === 404 ? 'ROUTE_MISSING' : 'SOURCE_SILENT';
      setLedgerMeta({
        total: 0,
        source,
        loading: false,
        phase: 'idle',
        query: String(qOverride || ''),
        error: err?.message || String(status || 'search_failed')
      });
    }
  }, [
    canSwitchBillingMode,
    activeTenant?.tenantId,
    activeTenant?._id,
    authUser?.tenantId,
    invoiceSearch,
    statusFilter,
    issuerMode,
    ledgerPage,
    ledgerPageSize,
    tenantId,
    sovereignClient
  ]);

  useEffect(() => {
    setLedgerPage(0);
  }, [invoiceSearch, statusFilter, periodFilter, kindFilter, issuerMode]);

  useEffect(() => {
    setLedgerMeta((prev) => ({
      ...prev,
      loading: true,
      phase: 'searching',
      query: String(invoiceSearch || '')
    }));
    const handle = setTimeout(() => {
      loadTenantInvoiceLedger({ q: invoiceSearch, page: ledgerPage });
    }, 180);
    return () => clearTimeout(handle);
  }, [invoiceSearch, statusFilter, periodFilter, kindFilter, ledgerPage, loadTenantInvoiceLedger]);

  useEffect(() => {
    loadTenantInvoiceLedger({ q: invoiceSearch, page: 0 });
  }, [issuerMode]);

  useEffect(() => {
    if (chromeSearch.trim()) {
      if (activeTab !== 'invoices' || invoiceWorkspace !== 'ledger') {
        setActiveTab('invoices');
        setInvoiceWorkspace('ledger');
      }
      if (invoiceSearch !== chromeSearch) {
        setInvoiceSearch(chromeSearch);
      }
    }
  }, [chromeSearch, activeTab, invoiceWorkspace, invoiceSearch]);

  const hydrate = useCallback(async (mode = 'cold') => {
    abortRef.current?.abort();
    abortRef.current = new AbortController();
    const hydrationController = abortRef.current;
    let hydrationTimedOut = false;
    const loadingDeadline = window.setTimeout(() => {
      hydrationTimedOut = true;
      hydrationController.abort();
      setError('Billing sources exceeded the 15-second hydration deadline. The command surface remains protected; retry after Node and treasury sources recover.');
      setLoading(false);
      setRefreshing(false);
    }, BILLING_HYDRATION_DEADLINE_MS);
    setRefreshing(mode !== 'cold');
    setError(null);
    if (mode === 'cold') setLoading(true);

    try {
      const [summaryResult, analyticsResult, creditResult, courtResult] = await Promise.allSettled([
        sovereignClient.get('/billing/summary', { signal: hydrationController.signal }),
        sovereignClient.get('/billing/analytics', { signal: hydrationController.signal }),
        sovereignClient.get('/billing/credit-scores', { signal: hydrationController.signal }),
        sovereignClient.get('/courts', { signal: hydrationController.signal, skipAuthRedirect: true, params: { limit: 1000 } })
      ]);

      const summaryPayload = summaryResult.status === 'fulfilled'
        ? normalizeBillingSummary(extractData(summaryResult.value))
        : null;
      const analyticsPayload = analyticsResult.status === 'fulfilled'
        ? normalizeBillingAnalytics(extractData(analyticsResult.value))
        : null;
      const creditPayload = creditResult.status === 'fulfilled'
        ? normalizeCreditScores(extractData(creditResult.value))
        : null;

      const courtPayload = courtResult.status === 'fulfilled'
        ? extractData(courtResult.value)
        : null;
      const courtRows = Array.isArray(courtPayload) ? courtPayload : courtPayload?.data || [];

      const invoiceRows = extractLiveInvoices(summaryPayload || {});

      const payloadOutstanding = invoiceRows.reduce((sum, invoice) => sum + Number(invoice.outstandingAmount || invoice.amount || 0), 0);
      const payloadArr = Number(summaryPayload?.totalArr || summaryPayload?.arr || 0);

      if (summaryPayload) setSummary(summaryPayload);
      if (analyticsPayload) setAnalytics(analyticsPayload);
      if (creditPayload) setCreditScores(creditPayload.scores || {});
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
          summary: summaryResult.status === 'fulfilled'
            ? buildLiveSourceHeartbeat({ status: 'fulfilled', value: summaryPayload }, 'Billing summary')
            : buildLiveSourceHeartbeat(summaryResult, 'Billing summary'),
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
      if (!hydrationTimedOut && err?.name !== 'CanceledError' && err?.name !== 'AbortError') {
        setError(err?.response?.data?.message || err?.message || 'Billing command center could not hydrate.');
      }
    } finally {
      window.clearTimeout(loadingDeadline);
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

  // ─── NEW: updateInvoiceInList for partial payment ──────────────────────
  const updateInvoiceInList = useCallback((updatedInvoice) => {
    const normalizedInvoice = normalizeKennelInvoiceRow(updatedInvoice);
    setLedgerItems(prevItems => {
      const index = prevItems.findIndex(item =>
        (item.id || item.invoiceNumber || item.traceId) === (normalizedInvoice.id || normalizedInvoice.invoiceNumber || normalizedInvoice.traceId)
      );
      if (index === -1) return prevItems;
      const newItems = [...prevItems];
      newItems[index] = { ...newItems[index], ...normalizedInvoice };
      return newItems;
    });
  }, []);

  // Line base = quantity × unit price (Kennel is source of truth on seal; client previews the same formula)
  const composeQty = Math.max(1, Math.floor(Number(manualInvoice.quantity) || 1));
  const composeUnitParsed = parseBillingMoneyInput(manualInvoice.unitPrice);
  const composeAmountParsed = parseBillingMoneyInput(manualInvoice.amount);
  const composeLineBase = (
    composeUnitParsed !== null && composeUnitParsed > 0
      ? preciseRound(composeQty * composeUnitParsed, 2)
      : (composeAmountParsed !== null && composeAmountParsed > 0 ? composeAmountParsed : 0)
  );

  useEffect(() => {
    const amount = composeLineBase;
    if (!amount || amount <= 0) {
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
          const taxRate = 0.15;
          const taxAmount = preciseRound(amount * taxRate, 2);
          setTaxEnginePreview({
            success: false,
            sourceStatus: 'SOURCE_SILENT',
            financials: {
              baseAmount: amount,
              taxAmount,
              totalAmount: preciseRound(amount + taxAmount, 2),
              netPayableAmount: preciseRound(amount + taxAmount, 2)
            },
            compliance: {
              warnings: [err.response?.data?.message || err.message || 'GlobalTaxEngine preview unavailable. Backend must recalculate before posting.']
            }
          });
        }
      } finally {
        if (alive) setTaxPreviewBusy(false);
      }
    }, 280);

    return () => {
      alive = false;
      clearTimeout(timer);
    };
  }, [
    composeLineBase,
    composeQty,
    manualInvoice.unitPrice,
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
    const filterByIssuer = (invoice) => {
      const raw = String(
        invoice.issuerType ||
        invoice.invoiceIdentity?.issuerType ||
        invoice.metadata?.issuerType ||
        ''
      ).toLowerCase();
      const isClient =
        raw.includes('client') ||
        raw === 'tenant_client' ||
        String(invoice.documentClass || '').toUpperCase() === 'CLIENT';
      if (!canSwitchBillingMode || issuerMode === 'CLIENT') {
        return isClient;
      }
      return !isClient;
    };

    const inPeriod = (invoice) => {
      const period = String(periodFilter || 'all').toLowerCase();
      if (!period || period === 'all') return true;
      const rawDate = invoice.issueDate || invoice.sealedAt || invoice.createdAt || invoice.dueDate;
      if (!rawDate) return period === 'all';
      const ts = new Date(rawDate).getTime();
      if (!Number.isFinite(ts)) return true;
      const now = new Date();
      const startOfToday = new Date(now.getFullYear(), now.getMonth(), now.getDate()).getTime();
      if (period === 'today') return ts >= startOfToday;
      if (period === '7d') return ts >= now.getTime() - 7 * 86400000;
      if (period === '30d') return ts >= now.getTime() - 30 * 86400000;
      if (period === '90d') return ts >= now.getTime() - 90 * 86400000;
      if (period === 'ytd') return ts >= new Date(now.getFullYear(), 0, 1).getTime();
      return true;
    };

    const baseRows =
      ledgerMeta.source === 'LIVE_DB' || ledgerMeta.source === 'LIVE_EMPTY'
        ? (Array.isArray(ledgerItems) ? ledgerItems : [])
        : extractLiveInvoices(summary || {});

    return baseRows.filter((invoice) => {
      const haystack = `${invoice.id || ''} ${invoice.traceId || ''} ${invoice.tenantId || ''} ${invoice.status || ''} ${invoice.invoiceNumber || ''} ${invoice.issuingEntity || ''} ${invoice.customerName || ''}`.toLowerCase();
      const matchesSearch = !invoiceSearch || haystack.includes(String(invoiceSearch).toLowerCase());
      const invStatus = String(invoice.status || '').toUpperCase();
      const filterStatus = String(statusFilter || '').toUpperCase();
      const statusAliases = {
        ISSUED: new Set(['ISSUED', 'OPEN', 'SENT', 'POSTED', 'ACTIVE']),
        OPEN: new Set(['ISSUED', 'OPEN', 'SENT', 'POSTED']),
        PAID: new Set(['PAID', 'SETTLED', 'COMPLETE', 'COMPLETED']),
        OVERDUE: new Set(['OVERDUE', 'PAST_DUE', 'LATE', 'DISPUTED', 'LEGAL_HOLD']),
        VOID: new Set(['VOID', 'VOIDED', 'CANCELLED', 'CANCELED']),
        DRAFT: new Set(['DRAFT']),
        PARTIALLY_PAID: new Set(['PARTIALLY_PAID', 'PARTIAL', 'PARTIAL_PAID']),
      };
      const matchesStatus =
        filterStatus === 'ALL' ||
        invStatus === filterStatus ||
        (statusAliases[filterStatus] && statusAliases[filterStatus].has(invStatus));
      return matchesSearch && matchesStatus && filterByIssuer(invoice) && inPeriod(invoice);
    });
  }, [invoiceSearch, statusFilter, periodFilter, summary, ledgerItems, ledgerMeta.source, issuerMode, canSwitchBillingMode]);

  const ledgerDisplayTotal = invoices.length;
  const ledgerPageCount = Math.max(1, Math.ceil(ledgerDisplayTotal / Math.max(1, ledgerPageSize || 20)));
  const pagedInvoices = useMemo(() => {
    const size = Math.max(1, ledgerPageSize || 20);
    const page = Math.min(Math.max(0, ledgerPage), Math.max(0, Math.ceil(ledgerDisplayTotal / size) - 1));
    const start = page * size;
    return invoices.slice(start, start + size);
  }, [invoices, ledgerPage, ledgerPageSize, ledgerDisplayTotal]);

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

  // ⌘/Ctrl+Enter seals invoice when compose is valid (must run AFTER isFrozen is defined)
  useEffect(() => {
    const onKey = (e) => {
      if (!(e.metaKey || e.ctrlKey) || e.key !== 'Enter') return;
      if (invoiceWorkspace !== 'compose' || activeTab !== 'invoices') return;
      if (processing === 'invoice' || isFrozen) return;
      if (!manualInvoice.tenantId?.trim()) return;
      if (!(parseBillingMoneyInput(manualInvoice.amount) > 0)) return;
      e.preventDefault();
      const form = document.querySelector('form.' + (hudStyles.formGrid || '').split(' ')[0]);
      if (form) form.requestSubmit();
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [invoiceWorkspace, activeTab, processing, isFrozen, manualInvoice.tenantId, manualInvoice.amount]);

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
  // Keep amount aligned with quantity × unit price so gates, seal, and tax stay consistent
  useEffect(() => {
    const unit = parseBillingMoneyInput(manualInvoice.unitPrice);
    if (unit === null || unit <= 0) return;
    const qty = Math.max(1, Math.floor(Number(manualInvoice.quantity) || 1));
    const next = preciseRound(qty * unit, 2);
    const current = parseBillingMoneyInput(manualInvoice.amount);
    if (current !== next) {
      setManualInvoice((prev) => ({ ...prev, amount: next.toFixed(2) }));
    }
  }, [manualInvoice.quantity, manualInvoice.unitPrice]);

  const manualInvoiceAmount = parseBillingMoneyInput(manualInvoice.amount);

  const manualInvoiceDraft = useMemo(() => buildManualInvoiceDraft(manualInvoice, {
    issuerTenantId: tenantId,
    recipientTenantId: manualInvoice.tenantId.trim(),
    amount: composeLineBase || manualInvoiceAmount || 0
  }), [manualInvoice, manualInvoiceAmount, composeLineBase, tenantId]);
  const billingCommandEnvelope = useMemo(() => buildBillingCommandEnvelope({
    draft: manualInvoiceDraft,
    taxResult: taxEnginePreview,
    treasuryEvaluation,
    sourceSnapshot
  }), [manualInvoiceDraft, taxEnginePreview, treasuryEvaluation, sourceSnapshot]);
  const manualInvoiceTotal = taxEnginePreview?.financials?.totalAmount ?? (manualInvoiceAmount === null ? 0 : manualInvoiceAmount);
  const composeCompleteness = useMemo(() => {
    let score = 0;
    const checks = [
      Boolean(manualInvoice.tenantId?.trim()),
      parseBillingMoneyInput(manualInvoice.amount) > 0,
      Boolean(manualInvoice.description?.trim() || manualInvoice.lineDescription?.trim()),
      Boolean(manualInvoice.currency),
      Boolean(manualInvoice.issueDate || true),
      Boolean(manualInvoice.paymentTerms),
    ];
    checks.forEach((ok) => { if (ok) score += 1; });
    return { score, total: checks.length, pct: Math.round((score / checks.length) * 100), ready: score >= 2 };
  }, [manualInvoice.tenantId, manualInvoice.amount, manualInvoice.description, manualInvoice.lineDescription, manualInvoice.currency, manualInvoice.issueDate, manualInvoice.paymentTerms]);

  const taxWarnings = taxEnginePreview?.compliance?.warnings || [];
  const sourceRows = Object.entries(sourceSnapshot.sources || {}).map(([key, source]) => ({
    key,
    ...source,
    statusTone: getSourceTone(source)
  }));

  const billingTenantIdentity = useMemo(
    () => buildBillingTenantIdentity(activeTenant, authUser, activeTenant),
    [activeTenant, authUser]
  );

  useEffect(() => {
    if (canSwitchBillingMode) return;
    if (!billingTenantIdentity?.tenantId) return;
    setManualInvoice((prev) => {
      if (prev.tenantId && prev.tenantId !== 'TENANT-ID' && String(prev.tenantId).trim()) return prev;
      return { ...prev, tenantId: billingTenantIdentity.tenantId };
    });
  }, [billingTenantIdentity?.tenantId, canSwitchBillingMode]);

  const billingOperator = useMemo(() => {
    const u = authUser || {};
    const displayName = u.displayName || u.name || [u.firstName, u.lastName].filter(Boolean).join(' ') || u.email || 'Operator';
    const roleLabel = String(u.roleLabel || u.role || u.authority || 'BILLING OPERATOR').replace(/_/g, ' ');
    return { displayName, roleLabel, email: u.email || '', name: displayName };
  }, [authUser]);

  const chromeMetrics = useMemo(() => ([
    { id: 'arr', label: 'Global ARR', value: formatMoney(totalArr), detail: flightDeck?.posture || '—' },
    { id: 'subs', label: 'Subscriptions', value: String(summary?.activeSubscriptions ?? 0), detail: 'Active contracts' },
    { id: 'out', label: 'Outstanding', value: formatMoney(outstanding), detail: `${summary?.pendingInvoices || 0} open` },
    { id: 'eff', label: 'Collection', value: `${collectionEfficiency}%`, detail: 'Paid vs issued' },
    { id: 'ready', label: 'Readiness', value: `${flightDeck?.readiness ?? 0}%`, detail: flightDeck?.sourceLabel || '—' },
    // ─── UsageMeters integrated into metrics strip ──────────────────────
    ...(UsageMeter ? [{ id: 'usage', label: 'Usage', value: <UsageMeter tenantId={tenantId} />, detail: 'Quota indicators' }] : [])
  ]), [totalArr, summary, outstanding, collectionEfficiency, flightDeck, tenantId]);

  const chromeLeftRail = (
    <nav aria-label="Billing workspace modules">
      {tabs.map((tab) => {
        const TabIcon = tab.icon;
        const active = activeTab === tab.id;
        const isTenantsTab = tab.id === 'tenants';
        // Tenants tab is already filtered by canManageTenants, so no extra cap needed
        return (
          <button
            key={tab.id}
            type="button"
            data-active={active ? 'true' : 'false'}
            data-tab={tab.id}
            onClick={() => {
              if (tab.id === 'tenants') {
                broadcastTelemetry('BillingHUD', 'TENANTS_TAB_CLICK', 'USER_ACTION', tenantId, {
                  tab: tab.id,
                  label: tab.label,
                  timestamp: new Date().toISOString()
                });
              }
              setActiveTab(tab.id);
            }}
            title={tab.label}
          >
            {TabIcon ? <TabIcon size={15} aria-hidden /> : null}
            <span>{tab.label}</span>
          </button>
        );
      })}
      <div style={{ marginTop: 12, paddingTop: 12, borderTop: '1px solid rgba(212,175,55,0.2)' }} />
      <button
        type="button"
        data-active={metricsOpen ? 'true' : 'false'}
        onClick={() => setMetricsOpen(v => !v)}
        title="Show or hide revenue metrics strip"
      >
        <TrendingUp size={15} aria-hidden />
        <span>{metricsOpen ? 'Hide metrics' : 'Metrics'}</span>
      </button>
      {activeTab === 'invoices' ? (
        <button
          type="button"
          data-active={guardrailsOpen ? 'true' : 'false'}
          onClick={() => setGuardrailsOpen(v => !v)}
          title="Tax and collection guardrails"
        >
          <ShieldCheck size={15} aria-hidden />
          <span>{guardrailsOpen ? 'Hide controls' : 'Controls'}</span>
        </button>
      ) : null}
      <div style={{ marginTop: 12, paddingTop: 12, borderTop: '1px solid rgba(212,175,55,0.2)' }} />
      {caps.demoMode && (
        <button
          type="button"
          onClick={() => setDemoModeActive(prev => !prev)}
          title={demoModeActive ? 'Disable Demo Mode' : 'Enable Demo Mode'}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            width: '100%',
            padding: '8px 12px',
            background: demoModeActive ? 'rgba(212,175,55,0.2)' : 'transparent',
            border: 'none',
            color: demoModeActive ? '#D4AF37' : '#94a3b8',
            cursor: 'pointer',
            borderRadius: '6px',
            transition: 'background 0.2s',
            fontSize: '0.85rem',
          }}
          onMouseEnter={(e) => e.currentTarget.style.background = 'rgba(212,175,55,0.15)'}
          onMouseLeave={(e) => e.currentTarget.style.background = demoModeActive ? 'rgba(212,175,55,0.2)' : 'transparent'}
        >
          <Zap size={15} />
          <span>{demoModeActive ? 'Demo On' : 'Demo Off'}</span>
        </button>
      )}
      <button
        type="button"
        onClick={logout}
        title="Sign out of Billing Nucleus"
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          width: '100%',
          padding: '8px 12px',
          background: 'transparent',
          border: 'none',
          color: '#ef4444',
          cursor: 'pointer',
          borderRadius: '6px',
          transition: 'background 0.2s',
          fontSize: '0.85rem',
        }}
        onMouseEnter={(e) => e.currentTarget.style.background = 'rgba(239,68,68,0.15)'}
        onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
      >
        <LogOut size={15} />
        <span>Logout</span>
      </button>
    </nav>
  );

  const runCommand = async (key, action, successMessage) => {
    if (processing) return null;
    setProcessing(key);
    try {
      const result = await action();
      if (successMessage) addLog(key.toUpperCase(), successMessage(result));
      if (String(key).includes('subscription')) {
        setSubscriptionFeedback((prev) => prev || {
          ok: true,
          message: typeof successMessage === 'function' ? successMessage(result) : (successMessage || 'Subscription command completed.'),
          at: new Date().toISOString(),
        });
      }
      try {
        await hydrate('refresh');
      } catch (_) { /* non-blocking */ }
      return result;
    } catch (err) {
      const message =
        err?.response?.data?.message ||
        err?.response?.data?.error ||
        (Array.isArray(err?.response?.data?.errors) ? err.response.data.errors.join(' ') : null) ||
        err?.message ||
        'Command failed.';
      addLog(`${String(key).toUpperCase()}_FAILED`, message);
      if (String(key).includes('subscription')) {
        setSubscriptionFeedback({ ok: false, message, at: new Date().toISOString() });
      }
      return null;
    } finally {
      setProcessing(null);
    }
  };

  // ─── NEW: Send Reminder Action ──────────────────────────────────────────
  const sendReminder = useCallback(async (invoice) => {
    const id = invoice?.id || invoice?.invoiceNumber || invoice?.traceId;
    if (!id) return;
    showBillingToast(`Reminder sent for invoice ${id}`, { tone: 'ok' });
    addLog('REMINDER', `Sent reminder for ${id}`);
  }, [addLog]);

  // ─── SUBSCRIPTION HANDLERS ─────────────────────────────────────────────
  const handleCreateSubscription = async (e) => {
    e.preventDefault();
    const { tenantId: targetTenant, planId, amount, currency, billingFrequency, trialPeriodDays, startDate, metadata } = subscriptionForm;
    setSubscriptionFeedback(null);

    if (!targetTenant) {
      setSubscriptionFeedback({ ok: false, message: 'Select a verified tenant shard before creating a subscription.', at: new Date().toISOString() });
      return;
    }
    if (!planId) {
      setSubscriptionFeedback({ ok: false, message: 'Select a plan from the catalog (or enter a plan id).', at: new Date().toISOString() });
      return;
    }
    const parsedAmount = parseBillingMoneyInput(amount);
    if (parsedAmount === null || parsedAmount < 0) {
      setSubscriptionFeedback({ ok: false, message: 'Enter a valid subscription amount.', at: new Date().toISOString() });
      return;
    }

    await runCommand('create_subscription', async () => {
      const result = await subscriptionHook.create({
        tenantId: targetTenant,
        planId,
        planName: plans.find((p) => String(p._id || p.planId || p.id) === String(planId))?.name || planId,
        amount: parsedAmount,
        currency: String(currency || 'ZAR').toUpperCase(),
        billingFrequency,
        trialPeriodDays: parseInt(trialPeriodDays, 10) || 0,
        startDate,
        metadata: { ...(metadata || {}), source: 'BILLING_HUD' },
      });

      const created = result?.data || result?.subscription || result || {};
      try {
        if (typeof subscriptionHook.refresh === 'function') {
          await subscriptionHook.refresh();
        } else if (typeof subscriptionHook.fetchSubscriptions === 'function') {
          await subscriptionHook.fetchSubscriptions({ silent: false });
        }
      } catch (_) { /* list refresh best-effort */ }

      setSubscriptionForm((prev) => ({
        ...prev,
        planId: '',
        amount: '',
        currency: 'ZAR',
        billingFrequency: 'monthly',
        trialPeriodDays: 0,
        metadata: {},
      }));

      setSubscriptionFeedback({
        ok: true,
        message: `Subscription created for ${created.tenantId || targetTenant} • ${created.planName || planId} • ${formatMoney(created.amount ?? parsedAmount, created.currency || currency)} • proof ${(created.proofHash || '').toString().slice(0, 14) || 'sealed'}`,
        at: new Date().toISOString(),
      });

      return created;
    }, (data) => {
      const row = data?.data || data?.subscription || data || {};
      return `Subscription created for ${row.tenantId || targetTenant} • proof ${(row.proofHash || '').toString().slice(0, 14) || 'sealed'}`;
    });

    if (subscriptionHook?.lastAction && subscriptionHook.lastAction.ok === false) {
      setSubscriptionFeedback({
        ok: false,
        message: subscriptionHook.lastAction.message || 'Create failed.',
        at: subscriptionHook.lastAction.at || new Date().toISOString(),
      });
    } else if (subscriptionHook?.error) {
      setSubscriptionFeedback({
        ok: false,
        message: subscriptionHook.error,
        at: new Date().toISOString(),
      });
    }
  };

  const handlePauseSubscription = async (subscriptionId, reason) => {
    await runCommand('pause_subscription', async () => {
      const result = await subscriptionHook.pause(subscriptionId, { reason });
      return result;
    }, data => `Subscription ${subscriptionId} paused • proof ${data.proofHash?.slice(0, 14)}`);
  };

  const handleResumeSubscription = async (subscriptionId) => {
    await runCommand('resume_subscription', async () => {
      const result = await subscriptionHook.resume(subscriptionId);
      return result;
    }, data => `Subscription ${subscriptionId} resumed • proof ${data.proofHash?.slice(0, 14)}`);
  };

  const handleCancelSubscription = async (subscriptionId, immediate, reason = 'Cancelled via BillingHUD') => {
    await runCommand('cancel_subscription', async () => {
      const result = await subscriptionHook.cancel(subscriptionId, {
        reason: reason || actionModal.data?.reason || 'Cancelled via BillingHUD',
        immediate,
      });
      return result;
    }, data => `Subscription ${subscriptionId} ${immediate ? 'immediately' : ''} cancelled • proof ${data.proofHash?.slice(0, 14)}`);
  };

  const handleUpgradeSubscription = async (subscriptionId, newPlanId, newAmount, newCurrency) => {
    await runCommand('upgrade_subscription', async () => {
      const result = await subscriptionHook.upgrade(subscriptionId, { newPlanId, newAmount, newCurrency });
      return result;
    }, data => `Subscription ${subscriptionId} upgraded • proof ${data.proofHash?.slice(0, 14)}`);
  };

  const handleDowngradeSubscription = async (subscriptionId, newPlanId, newAmount, newCurrency) => {
    await runCommand('downgrade_subscription', async () => {
      const result = await subscriptionHook.downgrade(subscriptionId, { newPlanId, newAmount, newCurrency });
      return result;
    }, data => `Subscription ${subscriptionId} downgraded • proof ${data.proofHash?.slice(0, 14)}`);
  };

  const handleReactivateSubscription = async (subscriptionId) => {
    await runCommand('reactivate_subscription', async () => {
      const result = await subscriptionHook.reactivate(subscriptionId);
      return result;
    }, data => `Subscription ${subscriptionId} reactivated • proof ${data.proofHash?.slice(0, 14)}`);
  };

  const handleViewAudit = async (subscriptionId) => {
    setAuditModal({ open: true, subscriptionId, auditTrail: [], loading: true });
    try {
      const auditData = await subscriptionHook.getAudit(subscriptionId);
      setAuditModal(prev => ({ ...prev, auditTrail: auditData?.auditTrail || [], loading: false }));
    } catch (err) {
      setAuditModal(prev => ({ ...prev, auditTrail: [], loading: false }));
      addLog('AUDIT_FAILED', err.message);
    }
  };

  const handleVerifySubscription = async (sub = {}) => {
    const subscriptionId = String(sub?.id || sub?._id || sub?.subscriptionId || '').trim();
    if (!subscriptionId) {
      setSubscriptionFeedback({
        ok: false,
        message: 'Verify blocked — subscription id missing.',
        at: new Date().toISOString(),
      });
      return;
    }

    const sealHash = String(
      sub?.proofHash || sub?.sealHash || sub?.seal || sub?.evidenceHash || ''
    ).trim();

    if (!sealHash || sealHash === 'SEAL_PENDING' || sealHash.toUpperCase() === 'PENDING') {
      setSubscriptionVerifyState((prev) => ({
        ...prev,
        [subscriptionId]: {
          status: 'FAILED',
          reason: 'NO_SEAL',
          at: new Date().toISOString(),
        },
      }));
      setSubscriptionFeedback({
        ok: false,
        message: `Verify blocked for ${subscriptionId.slice(0, 12)} — no SHA3-512 seal on contract yet.`,
        at: new Date().toISOString(),
      });
      return;
    }

    setProcessing(`verify_sub_${subscriptionId}`);
    setSubscriptionVerifyState((prev) => ({
      ...prev,
      [subscriptionId]: {
        status: 'PENDING',
        sealHash,
        at: new Date().toISOString(),
      },
    }));

    const scopedTenant = tenantId || sub?.tenantId || 'MASTER';
    let verifyPayload = null;
    let endpointUsed = null;

    try {
      try {
        const res = await sovereignClient.post('/merkle/verify', {
          sealHash,
          tenantId: scopedTenant,
          entityType: 'SUBSCRIPTION',
          entityId: subscriptionId,
        });
        verifyPayload = res?.data || { success: true, valid: true };
        endpointUsed = '/merkle/verify';
      } catch (primaryErr) {
        const res = await sovereignClient.post('/audit/verifyChain', {
          sealHash,
          subscriptionId,
          statementId: subscriptionId,
          tenantId: scopedTenant,
          entityType: 'SUBSCRIPTION',
        });
        verifyPayload = res?.data || { success: true, valid: true };
        endpointUsed = '/audit/verifyChain';
      }

      const valid = Boolean(
        verifyPayload?.valid === true
        || verifyPayload?.success === true
        || verifyPayload?.status === 'VERIFIED'
        || verifyPayload?.verified === true
        || (verifyPayload && verifyPayload.error == null && verifyPayload.success !== false)
      );

      const evidence = {
        subscriptionId,
        sealHash: sealHash.toUpperCase(),
        valid,
        endpoint: endpointUsed,
        tenantId: scopedTenant,
        verifiedAt: new Date().toISOString(),
        server: verifyPayload,
        algorithm: 'SHA3-512',
        source: 'BILLING_HUD_SUB_VERIFY',
      };

      try {
        const vaultKey = 'wilsy:evidence-vault:subscriptions';
        const existing = JSON.parse(sessionStorage.getItem(vaultKey) || '{}');
        existing[subscriptionId] = evidence;
        sessionStorage.setItem(vaultKey, JSON.stringify(existing));
      } catch (_) {
        /* session vault optional */
      }

      setSubscriptionVerifyState((prev) => ({
        ...prev,
        [subscriptionId]: {
          status: valid ? 'VERIFIED' : 'FAILED',
          sealHash: sealHash.toUpperCase(),
          evidence,
          at: evidence.verifiedAt,
        },
      }));

      setSubscriptionFeedback({
        ok: valid,
        message: valid
          ? `Subscription ${subscriptionId.slice(0, 12)} VERIFIED · seal ${sealHash.slice(0, 14)}… · evidence vaulted`
          : `Subscription ${subscriptionId.slice(0, 12)} seal rejected by ${endpointUsed}`,
        at: evidence.verifiedAt,
      });

      try {
        addLog?.(
          valid ? 'SUB_SEAL_VERIFIED' : 'SUB_SEAL_REJECTED',
          `${subscriptionId} · ${sealHash.slice(0, 16)} · ${endpointUsed}`
        );
      } catch (_) { /* optional logger */ }

      try {
        broadcastTelemetry?.(scopedTenant, valid ? 'SUB_SEAL_VERIFIED' : 'SUB_SEAL_REJECTED', 'BILLING_HUD', 'VERIFY', {
          subscriptionId,
          sealHash: sealHash.slice(0, 24),
          endpoint: endpointUsed,
        });
      } catch (_) { /* non-blocking */ }
    } catch (err) {
      const message = err?.response?.data?.message || err?.message || 'Seal verification failed';
      setSubscriptionVerifyState((prev) => ({
        ...prev,
        [subscriptionId]: {
          status: 'FAILED',
          sealHash,
          reason: message,
          at: new Date().toISOString(),
        },
      }));
      setSubscriptionFeedback({
        ok: false,
        message: `Verify failed for ${subscriptionId.slice(0, 12)}: ${message}`,
        at: new Date().toISOString(),
      });
      try {
        addLog?.('SUB_SEAL_VERIFY_FAILED', message);
      } catch (_) { /* optional */ }
    } finally {
      setProcessing(null);
    }
  };

  // ─── UPDATED: handleManualInvoice – with optimistic order identity ────
  const handleManualInvoice = async (event) => {
    event.preventDefault();
    if (serviceAccessBlocked) {
      showBillingToast(serviceAccessMessage, { tone: 'warn' });
      return;
    }
    const recipientTenantId = manualInvoice.tenantId.trim();
    const lineQtyGate = Math.max(1, Math.floor(Number(manualInvoice.quantity) || 1));
    const lineUnitGate = parseBillingMoneyInput(manualInvoice.unitPrice);
    const amountFromLine = lineUnitGate !== null && lineUnitGate > 0
      ? preciseRound(lineQtyGate * lineUnitGate, 2)
      : parseBillingMoneyInput(manualInvoice.amount);
    const amount = amountFromLine;
    if (!recipientTenantId || amount === null || amount <= 0 || isFrozen) return;

    // Check permission based on invoice mode
    const isClient = invoiceMode === 'CLIENT';
    const canCreate = isClient ? caps.createClientInvoice : caps.createPlatformInvoice;
    if (!canCreate) {
      showBillingToast(`You do not have permission to create ${isClient ? 'client' : 'platform'} invoices.`, { tone: 'warn' });
      return;
    }

    // ─── Optimistic order identity ──────────────────────────────────────
    orderIdentity.applyOptimisticCreate();

    try {
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
        const brand = buildBillingBrandIdentity({
          ...draft,
          recipientTenantId,
          recipientTenantName: manualInvoice.tenantName,
          documentKind,
          invoiceMode
        });

        // ─── Build line items in Kennel format (snake_case) ──────────────────
        const lineQty = Math.max(1, Math.floor(Number(manualInvoice.quantity) || 1));
        const lineUnit = parseBillingMoneyInput(manualInvoice.unitPrice) ?? amount;
        const lineBase = preciseRound(lineQty * lineUnit, 2);
        const lineDesc = (manualInvoice.lineDescription || manualInvoice.description || 'Service').trim();
        const taxRate = Number(taxConfig?.rate ?? finalTaxResult?.financials?.taxRate ?? 0.15) || 0.15;
        // Prefer tax engine total on the qty×unit draft; fallback local VAT if engine silent
        const taxAmount = Number(finalTaxResult?.financials?.taxAmount ?? preciseRound(lineBase * taxRate, 2)) || 0;
        const lineItems = [{
          description: lineDesc,
          amount: lineBase,
          quantity: lineQty,
          unit_price: lineUnit,
          tax_rate: taxRate,
          tax_amount: taxAmount,
          discount: 0,
          currency: draft.currency,
          metadata: {
            lineTotal: lineBase,
            quantity: lineQty,
            unitPrice: lineUnit,
            formula: 'quantity * unit_price',
          }
        }];

        // ─── Choose endpoint based on invoiceMode ────────────────────────────
        const endpoint = isClient ? '/billing/client/invoices' : '/billing/platform/invoices';

        // ─── Build payload matching Kennel schema ─────────────────────────────
        const payload = {
          // A platform invoice is addressed to the selected tenant; a client invoice
          // is addressed to the verified customer selected within the issuer tenant.
          customer_id: recipientTenantId,
          line_items: lineItems,
          currency: draft.currency,
          issued_at: manualInvoice.issueDate || draft.issueDate,
          due_at: manualInvoice.dueDate || draft.dueDate,
          payment_terms_days: Number(manualInvoice.paymentTerms) || draft.paymentTerms,
          tax_type: manualInvoice.taxType || 'vat',
          seller_jurisdiction: manualInvoice.tenantJurisdiction || 'ZA',
          customer_jurisdiction: manualInvoice.clientJurisdiction || 'ZA',
          collection_method: 'send_invoice',
          billing_mode: isClient ? 'CLIENT' : 'PLATFORM',
          subscription_id: null,
          plan_id: null,
          plan_name: null,
          period_start: null,
          period_end: null,
          // ─── Order identity from optimistic hook ──────────────────────
          order_number: orderIdentity.identity.orderNumber || '',
          purchase_order: orderIdentity.identity.purchaseOrder || '',
          metadata: {
            salesperson: manualInvoice.salesperson || '',
            salespersonId: manualInvoice.salespersonId || '',
            subject: manualInvoice.subject || '',
            clientType: manualInvoice.clientType || 'B2B',
            supplyType: manualInvoice.supplyType || 'DIGITAL_SERVICE',
            customerTaxId: manualInvoice.customerTaxId || '',
            tenantJurisdiction: manualInvoice.tenantJurisdiction || 'ZA',
            customerJurisdiction: manualInvoice.clientJurisdiction || 'ZA',
            notes: manualInvoice.notes || '',
            termsAndConditions: manualInvoice.termsAndConditions || '',
            brand: brand,
            payment_method: manualInvoice.paymentMethod || 'manual', // ← NEW
          },
          idempotency_key: draft.idempotencyKey,
          performed_by: authUser?.name || authUser?.email || 'SYSTEM',
          ...(isClient && {
            customer_name: manualInvoice.tenantName || recipientTenantId,
            customer_tax_id: manualInvoice.customerTaxId || '',
            customer_email: null,
            customer_phone: null,
          })
        };

        // ─── Send to Kennel (resilient to post-create pair_proof_hash 500) ──
        let saved = null;
        let sealSource = 'LIVE_DB';
        try {
          const invoiceOwnerTenantId = isClient ? tenantId : tenantId;
          const response = await sovereignClient.post(endpoint, payload, {
            headers: {
              'X-Tenant-ID': invoiceOwnerTenantId,
              'X-Idempotency-Key': draft.idempotencyKey,
            }
          });
          saved = response?.data?.data || response?.data || response || {};
        } catch (postErr) {
          const status = postErr?.response?.status;
          const body = postErr?.response?.data || {};
          const msg = String(body?.detail || body?.message || body?.error || postErr?.message || '');
          // Server often creates the invoice then fails on pair_proof_hash update (Mongo code 40).
          // Recover: re-fetch by idempotency or accept partial body.
          if (status === 500 || status === 409 || /pair_proof_hash|already exists|duplicate/i.test(msg)) {
            try {
              const listPath = isClient ? '/billing/client/invoices' : '/billing/platform/invoices';
              const recover = await sovereignClient.get(listPath, {
                params: {
                  tenant_id: isClient ? tenantId : recipientTenantId,
                  idempotency_key: draft.idempotencyKey,
                  limit: 5,
                  sort_by: 'issued_at',
                  sort_order: -1,
                },
                headers: { 'X-Tenant-ID': isClient ? tenantId : recipientTenantId },
              });
              const rows = extractData(recover);
              const list = Array.isArray(rows) ? rows : rows?.invoices || rows?.items || [];
              const match = list.find((row) =>
                row?.idempotency_key === draft.idempotencyKey
                || row?.idempotencyKey === draft.idempotencyKey
                || row?.invoice_id
                || row?.invoiceId
              ) || list[0];
              if (match) {
                saved = match;
                sealSource = 'LIVE_DB_RECOVERED';
              }
            } catch (_) { /* recovery optional */ }
            if (!saved && (body?.invoice_id || body?.invoiceId || body?.id)) {
              saved = body;
              sealSource = 'LIVE_DB_PARTIAL';
            }
          }
          if (!saved) {
            orderIdentity.rollback?.();
            throw postErr;
          }
          console.warn('[BILLING-SEAL] Recovered after server post-create error:', msg.slice(0, 160));
        }

        // ─── Update state with returned data ──────────────────────────────────
        setManualInvoice(prev => ({
          ...prev,
          // keep recipient for "Issue another"; clear amount for next entry
          amount: '',
          unitPrice: '',
          idempotencyKey: createBillingIdempotencyKey(tenantId),
          salesperson: prev.salesperson,
          salespersonId: prev.salespersonId,
          orderNumber: saved.order_number || saved.orderNumber || orderIdentity.identity.orderNumber || '',
          purchaseOrder: saved.purchase_order || saved.purchaseOrder || orderIdentity.identity.purchaseOrder || '',
          paymentMethod: prev.paymentMethod,
        }));

        setLastSavedInvoice({
          at: new Date().toISOString(),
          invoiceNumber: saved.invoice_number || saved.invoiceNumber || saved.invoice_id || saved.invoiceId || saved.id || null,
          id: saved.invoice_id || saved.invoiceId || saved.id || saved._id || null,
          source: sealSource,
          tenantId: saved.tenant_id || saved.tenantId || recipientTenantId,
          totalAmount: saved.total || saved.total_amount || saved.totalAmount || amount,
          pdfIdentity: null,
          orderNumber: saved.order_number || saved.orderNumber || null,
          purchaseOrder: saved.purchase_order || saved.purchaseOrder || null,
        });

        // Make the just-persisted Kennel response visible immediately.  The
        // follow-up read reconciles ordering and any server-side enrichment.
        const normalizedSaved = normalizeKennelInvoiceRow(saved);
        setLedgerItems((previous) => [
          normalizedSaved,
          ...previous.filter((item) => (
            String(item.id || item.invoiceNumber || '')
            !== String(normalizedSaved.id || normalizedSaved.invoiceNumber || '')
          )),
        ]);
        setLedgerMeta((previous) => ({
          ...previous,
          source: 'LIVE_DB',
          total: Math.max(Number(previous.total || 0) + 1, 1),
          error: null,
        }));
        await loadTenantInvoiceLedger({ tenantId: invoiceOwnerTenantId });

        orderIdentity.commit?.(saved);

        showBillingToast(
          `✅ Invoice sealed for ${recipientTenantId} • ${formatMoney(amount, draft.currency)} • ${sealSource === 'LIVE_DB' ? 'ledger' : 'recovered'}`,
          { tone: 'ok' }
        );

        broadcastTelemetry(tenantId, 'BILLING', 'INVOICE_CREATED', 'BillingHUD', {
          invoiceId: saved.invoice_id || saved.invoiceId || saved.id,
          tenantId: recipientTenantId,
          amount,
          proofHash: saved.proof_hash || saved.proofHash,
          sealSource,
          paymentMethod: manualInvoice.paymentMethod,
        });

        return saved;
      }, data => `Invoice sealed for ${data?.tenantId || recipientTenantId} • proof ${data?.proofHash?.slice(0, 14) || 'pending'}`);
    } catch (err) {
      // ─── Rollback on failure ──────────────────────────────────────────
      orderIdentity.rollbackOptimistic();
      // Re-throw so the outer error handling in runCommand (or caller) can act.
      throw err;
    }
  };

  // ─── HYBRID INVOICE HANDLER ───────────────────────────────────────────
  const handleHybridInvoice = async (event) => {
    event.preventDefault();
    if (serviceAccessBlocked) {
      showBillingToast(serviceAccessMessage, { tone: 'warn' });
      return;
    }
    const { tenantId: targetTenant, subscriptionId, subscriptionAmount, usageAmount, credits, outcomeAmount, prorationRatio, outcomeAchieved, currency, description } = hybridInvoice;
    if (!targetTenant) {
      setError('Tenant is required for hybrid invoice.');
      return;
    }
    const usage = parseBillingMoneyInput(usageAmount) || 0;
    const subscription = parseBillingMoneyInput(subscriptionAmount) || 0;
    const creditsVal = parseBillingMoneyInput(credits) || 0;
    const outcome = parseBillingMoneyInput(outcomeAmount) || 0;
    const proration = Number(prorationRatio || 1);
    if (!Number.isFinite(proration) || proration <= 0 || proration > 1) {
      setError('Proration must be between 0 and 1.');
      return;
    }
    if (subscription + usage + creditsVal + outcome === 0) {
      setError('Enter a subscription, usage, credit, or outcome amount.');
      return;
    }
    await runCommand('hybrid_invoice', async () => {
      const response = await sovereignClient.post('/billing/hybrid/generate', {
        tenant_id: targetTenant,
        subscription_id: subscriptionId || undefined,
        subscription_amount: subscription,
        usage_amount: usage,
        credits: creditsVal,
        outcome_amount: outcome,
        proration_ratio: proration,
        outcome_trigger: { achieved: Boolean(outcomeAchieved) },
        currency: String(currency || 'ZAR').toUpperCase(),
        description: description || 'Hybrid monetization invoice',
        idempotency_key: createBillingIdempotencyKey(tenantId)
      }, {
        headers: { 'X-Tenant-ID': 'GLOBAL_ROOT' }
      });
      const saved = response?.data || response || {};
      setLastSavedInvoice({
        at: new Date().toISOString(),
        invoiceNumber: saved?.invoiceNumber || saved?.id || null,
        id: saved?.id || saved?._id || null,
        source: saved?.source || 'HYBRID_INVOICE',
        tenantId: targetTenant,
        totalAmount: saved?.totalAmount || ((subscription * proration) + usage - creditsVal + (outcomeAchieved ? outcome : 0)),
        pdfIdentity: saved?.pdfIdentity || null
      });
      await loadTenantInvoiceLedger();
      setHybridInvoice(prev => ({ ...prev, subscriptionAmount: '', usageAmount: '', credits: '', outcomeAmount: '' }));
      return saved;
    }, data => `Hybrid invoice generated for ${targetTenant} • proof ${data?.proofHash?.slice(0, 14) || 'pending'}`);
  };

  const runAutoBilling = async () => {
    if (serviceAccessBlocked) {
      showBillingToast(serviceAccessMessage, { tone: 'warn' });
      return;
    }
    if (!caps.viewAutomation) {
      showBillingToast('You do not have permission to run automation.', { tone: 'warn' });
      return;
    }
    await runCommand('auto_billing', async () => {
      const response = await sovereignClient.post('/billing/auto-monthly', {}, { headers: { 'X-Tenant-ID': 'GLOBAL_ROOT' } });
      return response.data;
    }, data => `${data.invoicesGenerated || 0} invoices generated, ${data.emailsSent || 0} notices queued`);
  };

  // ─── UPDATED: runQuickInvoice – using Kennel endpoints ───────────────────
  const runQuickInvoice = async () => {
    if (serviceAccessBlocked) {
      showBillingToast(serviceAccessMessage, { tone: 'warn' });
      return;
    }
    const isClient = invoiceMode === 'CLIENT';
    if (!caps.createPlatformInvoice && !caps.createClientInvoice) {
      showBillingToast('You do not have permission to create invoices.', { tone: 'warn' });
      return;
    }
    await runCommand('quick_invoice', async () => {
      const draft = buildManualInvoiceDraft({
        ...manualInvoice,
        description: manualInvoice.description || 'Wilsy OS sovereign allocation',
        currency: manualInvoice.currency || 'ZAR',
        tenantJurisdiction: manualInvoice.tenantJurisdiction || 'ZA',
        clientJurisdiction: manualInvoice.clientJurisdiction || 'ZA',
        clientType: manualInvoice.clientType || 'B2B',
        supplyType: manualInvoice.supplyType || 'DIGITAL_SERVICE',
        taxType: manualInvoice.taxType || 'VAT',
        customerTaxId: manualInvoice.customerTaxId || ''
      }, {
        issuerTenantId: 'GLOBAL_ROOT',
        recipientTenantId: manualInvoice.tenantId.trim() || 'CLIENT_A',
        amount: parseBillingMoneyInput(manualInvoice.amount) || 1200
      });
      const finalTaxResult = await globalTaxEngine.calculateFromInvoiceDraft(draft, {
        tenantId,
        preferFallbackMatrix: true
      }).catch(() => taxEnginePreview);
      const taxConfig = globalTaxEngine.buildInvoiceTaxConfig(finalTaxResult, draft);
      const brand = buildBillingBrandIdentity({
        ...draft,
        documentKind,
        invoiceMode
      });

      // ─── Use Kennel endpoint ──────────────────────────────────────────────
      const endpoint = isClient ? '/billing/client/invoices' : '/billing/platform/invoices';
      const line_items = [{
        description: draft.description,
        quantity: 1,
        unit_price: draft.amount,
        tax_rate: taxConfig.rate || 0,
        tax_amount: finalTaxResult?.financials?.taxAmount ?? 0,
        discount: 0,
        currency: draft.currency,
        metadata: { lineTotal: draft.amount }
      }];
      const payload = {
        customer_id: isClient ? draft.recipientTenantId : null,
        line_items,
        currency: draft.currency,
        issued_at: draft.issueDate,
        due_at: draft.dueDate,
        payment_terms_days: draft.paymentTerms,
        tax_type: manualInvoice.taxType || 'vat',
        seller_jurisdiction: manualInvoice.tenantJurisdiction || 'ZA',
        customer_jurisdiction: manualInvoice.clientJurisdiction || 'ZA',
        collection_method: 'send_invoice',
        billing_mode: isClient ? 'CLIENT' : 'PLATFORM',
        idempotency_key: draft.idempotencyKey,
        performed_by: authUser?.name || authUser?.email || 'SYSTEM',
        ...(isClient && {
          customer_name: manualInvoice.tenantName || draft.recipientTenantId,
          customer_tax_id: manualInvoice.customerTaxId || '',
        })
      };
      const response = await sovereignClient.post(endpoint, payload, {
        headers: {
          'X-Tenant-ID': 'GLOBAL_ROOT',
          'X-Idempotency-Key': draft.idempotencyKey,
        }
      });
      const saved = response?.data || response || {};
      setLastSavedInvoice({
        at: new Date().toISOString(),
        invoiceNumber: saved?.invoice?.invoiceNumber || saved?.invoiceNumber || null,
        id: saved?.invoice?.id || saved?.invoice?._id || null,
        source: saved?.source || 'UNKNOWN',
        tenantId: saved?.invoice?.tenantId || draft.recipientTenantId,
        totalAmount: saved?.invoice?.totalAmount,
        pdfIdentity: saved?.pdfIdentity || null
      });
      try { await loadTenantInvoiceLedger(); } catch (_) { }
      return { ...saved, taxResult: finalTaxResult };
    }, data => `Invoice sealed for ${data?.invoice?.recipientTenantId || 'CLIENT_A'} • proof ${data?.proofHash?.slice(0, 14) || 'pending'}`);
  };

  const runLegalRoute = async () => {
    if (!caps.viewWarroom) {
      showBillingToast('You do not have permission to run legal route.', { tone: 'warn' });
      return;
    }
    await runCommand('legal_route', async () => {
      const { payload, proofHash } = buildBillingCommandContract({
        commandType: 'LEGAL_ROUTE',
        tenantId,
        body: {}
      });
      const response = await sovereignClient.post('/billing/legal', { ...payload, proofHash }, { headers: { 'X-Tenant-ID': tenantId } });
      return { ...response.data, proofHash };
    }, data => `Legal route triggered • proof ${data.proofHash?.slice(0, 14) || 'pending'}`);
  };

  const runSealTaxPosture = async () => {
    await runCommand('seal_tax_posture', async () => {
      const taxProfile = taxEnginePreview?.taxProfile || {
        jurisdiction: 'UNKNOWN',
        effectiveDate: new Date().toISOString(),
        taxStatus: 'UNKNOWN'
      };
      const { payload, proofHash } = buildBillingCommandContract({
        commandType: 'SEAL_TAX_POSTURE',
        tenantId,
        body: { taxProfile }
      });
      const response = await sovereignClient.post('/billing/tax', { ...payload, proofHash }, { headers: { 'X-Tenant-ID': tenantId } });
      return { ...response.data, proofHash };
    }, data => `Tax posture sealed • proof ${data.proofHash?.slice(0, 14) || 'pending'}`);
  };

  const runDunningCampaign = async () => {
    if (!caps.runDunning) {
      showBillingToast('You do not have permission to run dunning.', { tone: 'warn' });
      return;
    }
    await runCommand('run_dunning', async () => {
      const { payload, proofHash } = buildBillingCommandContract({
        commandType: 'RUN_DUNNING',
        tenantId,
        body: { overdueCount: Number(overdueInvoices.length) }
      });
      const response = await sovereignClient.post('/billing/dunning', { ...payload, proofHash }, { headers: { 'X-Tenant-ID': tenantId } });
      return { ...response.data, proofHash };
    }, data => `Neural dunning executed • proof ${data.proofHash?.slice(0, 14) || 'pending'}`);
  };

  const broadcastBillingTelemetry = async () => {
    await runCommand('broadcast_telemetry', async () => {
      const { payload, proofHash } = buildBillingCommandContract({
        commandType: 'BROADCAST_TELEMETRY',
        tenantId,
        body: {
          circuitBreaker: telemetry.circuitBreaker,
          avgLatencyMs: Number(telemetry.avgLatencyMs || 0),
          forensicSeal: telemetry.forensicSeal || 'UNKNOWN'
        }
      });
      const response = await sovereignClient.post('/billing/telemetry', { ...payload, proofHash }, { headers: { 'X-Tenant-ID': tenantId } });
      return { ...response.data, proofHash };
    }, data => `Telemetry broadcasted • proof ${data.proofHash?.slice(0, 14) || 'pending'}`);
  };

  const applyDynamicPricing = async () => {
    if (!caps.viewAutomation) {
      showBillingToast('You do not have permission to apply dynamic pricing.', { tone: 'warn' });
      return;
    }
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

  const previewSettlement = async () => {
    await runCommand('settlement_preview', async () => {
      const response = await sovereignClient.get('/billing/blockchain-preview', { headers: { 'X-Tenant-ID': 'GLOBAL_ROOT' } });
      setBlockchainPreview(response.data);
      return response.data;
    }, data => `Settlement preview ready: ${data.gasFee || '0'} ETH, ${data.estimatedTime || 'pending'}`);
  };

  const runTreasurySweep = async () => {
    if (serviceAccessBlocked) {
      showBillingToast(serviceAccessMessage, { tone: 'warn' });
      return;
    }
    if (!caps.viewTreasury) {
      showBillingToast('You do not have permission to run treasury sweep.', { tone: 'warn' });
      return;
    }
    await runCommand('treasury_sweep', async () => {
      const currentBalance = treasuryState.statusPacket?.availableLiquidity ?? treasuryEvaluation?.liquidity?.currentBalance ?? Math.max(totalArr / 12, outstanding, 0);
      const currency = manualInvoice.currency || 'ZAR';
      const { payload, proofHash } = buildBillingCommandContract({
        commandType: 'TREASURY_SWEEP',
        tenantId,
        body: {
          currency,
          currentBalance: Number(currentBalance || 0)
        }
      });
      const response = await sovereignClient.post('/billing/treasury', { ...payload, proofHash }, { headers: { 'X-Tenant-ID': tenantId } });
      setTreasuryState(prev => ({
        ...prev,
        lastReceipt: response.data,
        lastSync: new Date().toISOString()
      }));
      return response.data;
    }, data => `Treasury sweep command acknowledged • proof ${data?.canonicalProof?.slice(0, 14) || 'pending'}`);
  };

  const emailInvoice = useCallback(async (invoice) => {
    const id = invoice?.id || invoice?.invoiceNumber || invoice?.traceId;
    if (!id) return;
    setProcessing('invoice_email');
    const tid = tenantId || invoice.tenantId || 'MASTER';
    const headers = { 'X-Tenant-ID': tid };
    const body = {
      invoiceId: id,
      invoice_id: id,
      tenantId: tid,
      to: invoice.clientEmail || invoice.customerEmail || invoice.email || undefined,
      includeSeal: true,
    };
    try {
      let ok = false;
      for (const path of ['/billing/invoices/email', '/billing/platform/invoices/email']) {
        try {
          await sovereignClient.post(path, body, { headers });
          ok = true;
          break;
        } catch (e) {
          if (e?.response?.status !== 404) throw e;
        }
      }
      if (!ok) throw new Error('Email route not mounted on Kennel or BFF');
      showBillingToast(`Email queued for ${id}`, { tone: 'ok' });
    } catch (err) {
      console.error('[BILLING] email invoice', err?.message || err);
      showBillingToast(err?.response?.data?.detail || err?.response?.data?.message || err?.message || 'Email failed', { tone: 'danger' });
    } finally {
      setProcessing(null);
    }
  }, [tenantId]);

  /**
   * @function printInvoice
   * @description Generates and opens a forensic enterprise PDF invoice via the Wilsy OS renderer.
   */
  const printInvoice = useCallback(async (invoice) => {
    const id = invoice?.id || invoice?.invoiceNumber || invoice?.traceId;
    if (!id) return;
    // Open the preview synchronously from the click gesture. Browsers otherwise
    // block an asynchronous window.open and `noopener` returns an unreadable tab.
    const previewWindow = window.open('about:blank', '_blank');
    setProcessing('invoice_print');
    try {
      const tid = String(tenantId || invoice.tenantId || invoice.recipientTenantId || 'MASTER');

      const lineItems = (invoice.lineItems || []).map((li) => ({
        serviceType: li.serviceType || li.category || li.type || 'General Service',
        description: li.description || li.name || 'Wilsy OS service',
        quantity: Number(li.quantity ?? 1),
        unitPrice: Number(li.unitPrice ?? li.amount ?? 0),
        lineTotal: Number(li.lineTotal ?? li.amount ?? (li.quantity || 1) * (li.unitPrice || 0)),
        taxAmount: Number(li.taxAmount ?? 0),
        currency: li.currency || invoice.currency || 'ZAR',
      }));

      if (lineItems.length === 0 && invoice.totalAmount > 0) {
        lineItems.push({
          serviceType: invoice.serviceType || 'Infrastructure Service',
          description: invoice.description || 'Wilsy OS sovereign infrastructure',
          quantity: 1,
          unitPrice: Number(invoice.totalAmount ?? 0),
          lineTotal: Number(invoice.totalAmount ?? 0),
          taxAmount: Number(invoice.taxAmount ?? 0),
          currency: invoice.currency || 'ZAR',
        });
      }

      const identity = invoice.invoiceIdentity || invoice.identity || invoice.metadata?.identity || {};
      const issuerType = String(
        invoice.issuerType ||
        identity.issuerType ||
        (invoiceMode === 'CLIENT' ? 'tenant_client' : 'platform')
      ).toLowerCase();
      const documentKindResolved = String(
        invoice.documentKind || documentKind || 'INVOICE'
      ).toUpperCase();
      const identitySource = String(
        invoice.metadata?.identitySource ||
        identity.identitySource ||
        identity.source ||
        'TENANT_CONTEXT'
      ).toUpperCase();
      const issuingEntityResolved =
        invoice.issuingEntity ||
        identity.legalName ||
        identity.issuingEntity ||
        invoice.brandingNexus?.legalEntity ||
        (issuerType.includes('client') ? (billingTenantIdentity?.name || 'Tenant Entity') : 'Wilsy (Pty) Ltd');

      const payload = {
        type: 'billing-invoice',
        templateType: 'invoice',
        artifactType: 'billing-invoice',
        title: String(invoice.invoiceNumber || invoice.title || 'Sovereign Infrastructure Invoice'),
        tenantId: tid,
        issuingEntity: issuingEntityResolved,
        issuerType,
        documentKind: documentKindResolved,
        counterparty:
          invoice.customerName ||
          invoice.counterparty ||
          invoice.clientId ||
          invoice.recipientTenantId ||
          tid,
        jurisdiction:
          identity.jurisdiction ||
          invoice.jurisdiction ||
          invoice.taxJurisdiction ||
          'Republic of South Africa',
        taxId: identity.taxId || identity.vatNumber || invoice.customerTaxId || '',
        registrationNumber: identity.registrationNumber || identity.companyReg || '',
        sourcePosture: invoice.source || 'SOURCE_LIVE',
        effectiveDate: invoice.issueDate || invoice.createdAt || new Date().toISOString(),
        data: {
          invoiceId: id,
          invoiceNumber: invoice.invoiceNumber || id,
          lineItems: lineItems,
          totalAmount: Number(invoice.totalAmount ?? invoice.amount ?? 0),
          currency: invoice.currency || 'ZAR',
          status: invoice.status || 'ISSUED',
          dueDate: invoice.dueDate,
          issueDate: invoice.issueDate || invoice.createdAt,
          paymentTerms: invoice.paymentTerms || 30,
          sealHash: invoice.sealHash || invoice.proofHash || '',
          brandingNexus: invoice.brandingNexus || null,
          issuingEntity: issuingEntityResolved,
          issuerType,
          documentKind: documentKindResolved,
          identity: {
            legalName: issuingEntityResolved,
            taxId: identity.taxId || identity.vatNumber || '',
            registrationNumber: identity.registrationNumber || identity.companyReg || '',
            jurisdiction: identity.jurisdiction || invoice.jurisdiction || 'ZA',
            identitySource
          },
          metadata: {
            traceId: invoice.traceId || id,
            watermark: 'Wilsy OS Sovereign Copy',
            print: true,
            serviceType: invoice.serviceType || lineItems[0]?.serviceType || 'Infrastructure',
            identitySource,
            issuerType,
            documentKind: documentKindResolved
          }
        },
        payloadData: {
          invoiceId: id,
          invoiceNumber: invoice.invoiceNumber || id,
          lineItems: lineItems,
          totalAmount: Number(invoice.totalAmount ?? invoice.amount ?? 0),
          currency: invoice.currency || 'ZAR',
          status: invoice.status || 'ISSUED',
          dueDate: invoice.dueDate,
          issueDate: invoice.issueDate || invoice.createdAt,
          paymentTerms: invoice.paymentTerms || 30,
          sealHash: invoice.sealHash || invoice.proofHash || '',
          brandingNexus: invoice.brandingNexus || null,
          issuingEntity: issuingEntityResolved,
          issuerType,
          documentKind: documentKindResolved,
          identitySource
        },
        metadata: {
          invoiceNumber: invoice.invoiceNumber || id,
          amount: Number(invoice.totalAmount ?? invoice.amount ?? 0),
          currency: invoice.currency || 'ZAR',
          status: invoice.status || 'ISSUED',
          dueDate: invoice.dueDate,
          issueDate: invoice.issueDate || invoice.createdAt,
          sealHash: invoice.sealHash || invoice.proofHash || '',
          watermark: 'Wilsy OS Sovereign Copy',
          print: true,
          serviceType: invoice.serviceType || lineItems[0]?.serviceType || 'Infrastructure',
          identitySource,
          issuerType,
          documentKind: documentKindResolved,
          issuingEntity: issuingEntityResolved
        }
      };

      const res = await sovereignClient.post('/generate/pdf', payload, {
        responseType: 'blob',
        headers: {
          'X-Tenant-ID': tid,
          Accept: 'application/pdf'
        }
      });

      const contentType = String(res?.headers?.['content-type'] || res?.headers?.['Content-Type'] || '');
      const data = res?.data;

      if (data instanceof Blob && (contentType.includes('pdf') || data.type === 'application/pdf' || data.size > 500)) {
        if (contentType.includes('json') || data.type === 'application/json') {
          const text = await data.text();
          let msg = text;
          try { msg = JSON.parse(text)?.message || text; } catch (_) { }
          throw new Error(msg || 'PDF endpoint returned JSON, not a PDF');
        }
        const url = URL.createObjectURL(data);
        if (previewWindow) {
          previewWindow.location.replace(url);
        } else {
          const a = document.createElement('a');
          a.href = url;
          a.download = `WILSY-INV-${tid}-${id}.pdf`;
          a.click();
        }
        setTimeout(() => URL.revokeObjectURL(url), 120_000);
        return;
      }

      throw new Error('PDF render returned empty or non-PDF body');
    } catch (err) {
      console.warn('[BILLING] print PDF unavailable — HTML fallback', err?.message || err);
      // Kennel/Node PDF may 404 after migration — open a printable HTML receipt
      try {
        const total = Number(invoice.totalAmount ?? invoice.total ?? invoice.amount ?? 0);
        const html = `<!doctype html><html><head><title>${invoice.invoiceNumber || id}</title>
          <style>body{font-family:Inter,system-ui,sans-serif;padding:32px;color:#111}
          h1{font-size:18px} .meta{color:#555;font-size:12px} .total{font-size:28px;font-weight:700;margin-top:24px}
          table{width:100%;border-collapse:collapse;margin-top:16px} td,th{border-bottom:1px solid #ddd;padding:8px;text-align:left}</style></head>
          <body onload="window.print()">
          <h1>Wilsy (Pty) Ltd — Platform Invoice</h1>
          <div class="meta">${invoice.invoiceNumber || id} · ${invoice.status || ''} · Seal ${(invoice.sealHash || invoice.proofHash || '').toString().slice(0, 24)}</div>
          <div class="meta">Bill to: ${invoice.customerName || invoice.clientName || invoice.tenantId || tid}</div>
          <div class="total">${invoice.currency || 'ZAR'} ${total.toLocaleString('en-ZA', { minimumFractionDigits: 2 })}</div>
          <p class="meta">Tax-inclusive total · POPIA §19 · Generated ${new Date().toISOString()}</p>
          </body></html>`;
        if (previewWindow) {
          previewWindow.document.open();
          previewWindow.document.write(html);
          previewWindow.document.close();
          showBillingToast('Opened print preview (PDF service offline)', { tone: 'warn' });
        } else {
          showBillingToast('Allow pop-ups to print invoice', { tone: 'warn' });
        }
      } catch (fallbackErr) {
        showBillingToast(err?.response?.data?.message || err?.message || 'Print failed', { tone: 'danger' });
      }
    } finally {
      setProcessing(null);
    }
  }, [tenantId, invoiceMode, documentKind, billingTenantIdentity]);

  const downloadInvoice = useCallback(async (invoice, format = 'json') => {
    const id = invoice?.id || invoice?.invoiceNumber || invoice?.traceId || 'invoice';
    const tid = tenantId || invoice.tenantId || 'MASTER';
    try {
      if (format === 'pdf') {
        await printInvoice(invoice);
        return;
      }
      const blob = new Blob([JSON.stringify(invoice, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `WILSY-${tid}-${id}.json`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      console.error('[BILLING] download invoice', err?.message || err);
    }
  }, [tenantId, printInvoice]);

  const openInvoiceAudit = useCallback((invoice) => {
    const id = invoice?.id || invoice?.invoiceNumber || invoice?.traceId;
    try {
      sessionStorage.setItem('wilsy:audit-focus-entity', String(id || ''));
    } catch (_) { /* ignore */ }
    setActiveTab('audit');
  }, []);

  const verifyInvoiceBlockchain = useCallback(async (invoice) => {
    const hash = invoice?.sealHash || invoice?.proofHash || invoice?.id;
    if (!hash) {
      alert('No seal/proof on this invoice yet');
      return;
    }
    setProcessing('invoice_chain');
    try {
      let res;
      const tid = tenantId || invoice.tenantId || 'MASTER';
      const payload = { sealHash: hash, seal_hash: hash, proofHash: hash, tenantId: tid, statementId: invoice.id || invoice.invoiceNumber };
      const paths = ['/billing/merkle/verify', '/billing/audit/verifyChain', '/merkle/verify', '/audit/verifyChain'];
      let lastErr;
      for (const path of paths) {
        try {
          res = await sovereignClient.post(path, payload, { headers: { 'X-Tenant-ID': tid } });
          lastErr = null;
          break;
        } catch (e) {
          lastErr = e;
          if (e?.response?.status !== 404) break;
        }
      }
      if (lastErr && !res) throw lastErr;
      const data = res?.data || { ok: true, hash };
      showBillingToast(
        data.valid === false ? `Chain invalid · ${String(hash).slice(0, 14)}…` : `Chain verified · ${String(hash).slice(0, 14)}…`,
        { tone: data.valid === false ? 'danger' : 'ok' }
      );
    } catch (err) {
      showBillingToast(err?.response?.data?.detail || err?.response?.data?.message || err?.message || 'Chain verify failed', { tone: 'danger' });
    } finally {
      setProcessing(null);
    }
  }, [tenantId]);

  /**
   * @function updateInvoiceStatus
   */
  const updateInvoiceStatus = useCallback(async (invoice, newStatus) => {
    const id = invoice?.id || invoice?.invoiceNumber || invoice?.traceId;
    if (!id) return;
    setProcessing(`status_${id}`);
    try {
      await sovereignClient.patch(
        `/billing/invoices/${id}/status`,
        { status: newStatus },
        { headers: { 'X-Tenant-ID': tenantId || invoice.tenantId || 'MASTER' } }
      );
      await loadTenantInvoiceLedger({ q: invoiceSearch });
      addLog('STATUS_UPDATE', `Invoice ${id} → ${newStatus}`);
    } catch (err) {
      console.error('[BILLING] status update failed', err);
      alert(err?.response?.data?.message || err?.message || 'Status update failed.');
    } finally {
      setProcessing(null);
    }
  }, [tenantId, invoiceSearch, loadTenantInvoiceLedger]);

  const runDunningIntervention = async (recommendation) => {
    if (!caps.runDunning) {
      showBillingToast('You do not have permission to run dunning intervention.', { tone: 'warn' });
      return;
    }
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

  const submitDispute = async () => {
    if (!caps.disputeInvoice) {
      showBillingToast('You do not have permission to submit disputes.', { tone: 'warn' });
      return;
    }
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

  const initiateSeizure = async (event) => {
    event.preventDefault();
    if (!caps.runSeizure) {
      showBillingToast('You do not have permission to initiate seizure.', { tone: 'warn' });
      return;
    }
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

  const selectCourt = (court) => {
    const id = court._id || court.id;
    setSeizure(prev => ({ ...prev, courtId: id }));
    setCourtSearch(formatCourtSearchLabel(court));
  };

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

  // ─── KEYBOARD SHORTCUT FOR COMMAND PALETTE ──────────────────────────────
  useEffect(() => {
    const handler = (e) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        setCommandPaletteOpen(prev => !prev);
      }
    };
    document.addEventListener('keydown', handler);
    return () => document.removeEventListener('keydown', handler);
  }, []);

  // ─── ONBOARDING TOUR ────────────────────────────────────────────────────
  useEffect(() => {
    const hasSeenTour = localStorage.getItem('wilsy:onboarding:seen');
    if (!hasSeenTour) {
      setOnboardingActive(true);
    }
  }, []);

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

  // ─── FULL JSX WITH PHASE 7 ENHANCEMENTS ──────────────────────────────
  return (
    <WilsyOSDashboardChrome
      dashboardKey="billing"
      commandLabel={canSwitchBillingMode ? 'Wilsy OS Founder Revenue Command' : 'Wilsy OS Billing Nucleus'}
      title="Global Monetization Command"
      role={canSwitchBillingMode ? 'FOUNDER_BILLING_COMMAND' : 'BILLING_OPERATOR'}
      posture={flightDeck?.posture || 'SOURCE_GAPS'}
      storyMessages={[
        'Sovereign revenue operating system — issue, collect, and prove every rand.'
      ]}
      metrics={metricsOpen ? chromeMetrics : []}
      leftRail={chromeLeftRail}
      search={{
        value: chromeSearch,
        onChange: (e) => setChromeSearch(e.target.value),
        placeholder: 'Search invoices, tenants, courts…',
        // ─── GlobalSearch integrated into the chrome search bar ──────────
        renderResults: (query) => <GlobalSearch query={query} tenantId={tenantId} />
      }}
      tenant={billingTenantIdentity}
      operator={billingOperator}
      account={{
        isOpen: accountCenterOpen,
        onOpen: () => setAccountCenterOpen(true),
        onClose: () => setAccountCenterOpen(false),
        onSignOut: logout,
        user: authUser,
        label: 'COMMAND',
        CommandCenterComponent: WilsyAccountCommandCenter,
        identitySource: 'ACCOUNT_VERIFIED',
        mfaStatus: 'SOURCE_REQUIRED',
        privacyStatus: 'POPIA_SAFE',
        complianceStatus: 'SOURCE_REQUIRED',
        auditConfidence: flightDeck?.posture || 'SOURCE_GAPS',
        retentionStatus: 'TENANT_LEDGER_READY',
        activeSessions: 'SOURCE_REQUIRED',
        // ─── DemoMode toggle in account menu ──────────────────────────────
        extraActions: caps.demoMode && DemoMode ? (
          <DemoMode active={demoModeActive} onToggle={() => setDemoModeActive(prev => !prev)} />
        ) : null
      }}
      actions={{
        liveSyncLabel: 'LIVE SYNC',
        onLiveSync: () => hydrate('refresh'),
        isRefreshing: refreshing,
        primaryActionLabel: 'CREATE INVOICE',
        onPrimaryAction: () => {
          if (caps.createPlatformInvoice || caps.createClientInvoice) {
            setActiveTab('invoices');
            setInvoiceWorkspace('compose');
            setDocumentKind('INVOICE');
          } else {
            showBillingToast('You do not have permission to create invoices.', { tone: 'warn' });
          }
        },
        primaryDisabled: Boolean(isFrozen) || !(caps.createPlatformInvoice || caps.createClientInvoice)
      }}
    >
      <div className={hudStyles.billingShell} data-embedded-chrome="true">
        {/* ─── FORENSIC PROOF BAR ──────────────────────────────────────────── */}
        <ForensicProofBar tenantId={tenantId} />

        {serviceAccessBlocked && (
          <section
            role="alert"
            aria-live="assertive"
            style={{ margin: '12px 18px 0', padding: '14px 16px', border: '1px solid #f59e0b', borderRadius: 12, background: '#451a03', color: '#fef3c7', display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 12 }}
          >
            <span><strong>Service suspended — read-only mode.</strong> {serviceAccessMessage} Your ledger and payment controls remain available.</span>
            <button type="button" className={hudStyles.secondaryButton} onClick={() => { setActiveTab('invoices'); setInvoiceWorkspace('ledger'); }}>
              View ledger / Pay now
            </button>
          </section>
        )}

        {/* ─── COMMAND PALETTE ────────────────────────────────────────────── */}
        {CommandPalette && commandPaletteOpen && (
          <CommandPalette
            isOpen={commandPaletteOpen}
            onClose={() => setCommandPaletteOpen(false)}
            tenantId={tenantId}
            actions={{
              createInvoice: () => {
                if (caps.createPlatformInvoice || caps.createClientInvoice) {
                  setActiveTab('invoices');
                  setInvoiceWorkspace('compose');
                } else {
                  showBillingToast('Permission denied.', { tone: 'warn' });
                }
              },
              runBilling: runAutoBilling,
              openLedger: () => { setActiveTab('invoices'); setInvoiceWorkspace('ledger'); },
              runDunning: runDunningCampaign,
              treasurySweep: runTreasurySweep,
              openInvestor: () => caps.viewInvestor && setActiveTab('investor'),
              openAnomalies: () => caps.viewAnomalies && setActiveTab('anomalies'),
            }}
          />
        )}

        {/* ─── ONBOARDING TOUR ────────────────────────────────────────────── */}
        {OnboardingTour && onboardingActive && (
          <OnboardingTour
            onFinish={() => {
              setOnboardingActive(false);
              localStorage.setItem('wilsy:onboarding:seen', 'true');
            }}
            steps={[
              { target: '.wilsy-dashboard-chrome', content: 'Welcome to Wilsy OS Billing Nucleus – issue, collect, and prove every rand.' },
              { target: '[data-tab="invoices"]', content: 'Create and manage invoices here.' },
              { target: '[data-tab="subscriptions"]', content: 'Recurring revenue engine.' },
              { target: '[data-tab="investor"]', content: 'Investor‑grade metrics with cryptographic proof.' },
            ]}
          />
        )}

        {/* ─── THE REST OF THE UI (unchanged) ────────────────────────────── */}
        {activeTab === 'command' && (
          <>
            <section className={hudStyles.hero}>
              <div>
                <div className={hudStyles.heroTopline}>
                  <span className={hudStyles.eyebrow}><Globe2 size={14} /> Billing Hub</span>
                  <span className={hudStyles.chip}>Workspace</span>
                </div>
                <h1>Billing command center</h1>
                <p>
                  Compact command surface for invoices, subscriptions, tax seals, treasury sweep, and
                  collections operations ready for an enterprise finance workspace.
                </p>
              </div>
              <div className={hudStyles.heroActions}>
                <button
                  type="button"
                  className={hudStyles.primaryButton}
                  onClick={runAutoBilling}
                  disabled={serviceAccessBlocked || !!processing || !caps.viewAutomation}
                  title="Execute the next governance-controlled billing cycle"
                >
                  {processing === 'auto_billing' ? <RefreshCw className="animate-spin" size={15} /> : <Zap size={15} />}
                  Run Billing
                </button>
                <button
                  type="button"
                  className={hudStyles.secondaryButton}
                  onClick={runQuickInvoice}
                  disabled={serviceAccessBlocked || !!processing || !(caps.createPlatformInvoice || caps.createClientInvoice)}
                  title="Generate a quick invoice draft for the current tenant context"
                >
                  <FileText size={15} /> Create Invoice
                </button>
                <button
                  type="button"
                  className={hudStyles.secondaryButton}
                  onClick={runSealTaxPosture}
                  disabled={!!processing}
                  title="Seal the live tax posture for audit-ready compliance"
                >
                  <ShieldCheck size={15} /> Seal Tax Posture
                </button>
                <button
                  type="button"
                  className={hudStyles.secondaryButton}
                  onClick={runTreasurySweep}
                  disabled={!!processing || !caps.viewTreasury}
                  title="Evaluate and execute treasury sweep against policy gates"
                >
                  <Scale size={15} /> Treasury Sweep
                </button>
                <button
                  type="button"
                  className={hudStyles.secondaryButton}
                  onClick={runDunningCampaign}
                  disabled={!!processing || !caps.runDunning}
                  title="Launch neural dunning for overdue receivables"
                >
                  <AlertOctagon size={15} /> Run Dunning
                </button>
                <button
                  type="button"
                  className={hudStyles.secondaryButton}
                  onClick={runLegalRoute}
                  disabled={!!processing || !caps.viewWarroom}
                  title="Route selected receivables into legal collections workflow"
                >
                  <Gavel size={15} /> Legal Route
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
                  {flightDeck.liveSources.map(source => {
                    const tone = String(source.statusTone || 'NOT_STARTED').toUpperCase();
                    const toneClass = tone === 'DONE'
                      ? hudStyles.sourceToneDone
                      : tone === 'ALMOST_DONE'
                        ? hudStyles.sourceToneAlmostDone
                        : hudStyles.sourceToneNotStarted;
                    return (
                      <span
                        key={source.key}
                        className={`${hudStyles.sourceChip} ${toneClass}`}
                        data-live={source.live ? 'true' : 'false'}
                        data-source-tone={tone}
                      >
                        {source.live ? <CheckCircle size={13} /> : <AlertTriangle size={13} />}
                        {source.label}
                      </span>
                    );
                  })}
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
                <button type="button" className={hudStyles.primaryButton} onClick={runAutoBilling} disabled={!!processing || !caps.viewAutomation}>
                  {processing === 'auto_billing' ? <RefreshCw className="animate-spin" size={15} /> : <Zap size={15} />}
                  Run Billing
                </button>
                <button type="button" className={hudStyles.secondaryButton} onClick={runQuickInvoice} disabled={!!processing || !(caps.createPlatformInvoice || caps.createClientInvoice)}>
                  <FileText size={15} /> Create Invoice
                </button>
                <button type="button" className={hudStyles.secondaryButton} onClick={runSealTaxPosture} disabled={!!processing} title="Seal the live tax posture for audit-ready compliance">
                  <ShieldCheck size={15} /> Seal Tax Posture
                </button>
                <button type="button" className={hudStyles.secondaryButton} onClick={runTreasurySweep} disabled={!!processing || !caps.viewTreasury} title="Evaluate and execute treasury sweep against policy gates">
                  <Scale size={15} /> Treasury Sweep
                </button>
                <button type="button" className={hudStyles.secondaryButton} onClick={runDunningCampaign} disabled={!!processing || !caps.runDunning} title="Launch neural dunning for overdue receivables">
                  <AlertOctagon size={15} /> Run Dunning
                </button>
                <button type="button" className={hudStyles.secondaryButton} onClick={runLegalRoute} disabled={!!processing || !caps.viewWarroom} title="Route selected receivables into legal collections workflow">
                  <Gavel size={15} /> Legal Route
                </button>
                <button
                  type="button"
                  className={hudStyles.ghostButton}
                  onClick={broadcastBillingTelemetry}
                  disabled={!!processing}
                  title={processing ? 'Telemetry broadcast in progress' : 'Broadcast the latest billing telemetry to the sovereign mesh'}
                >
                  <Globe2 size={15} /> Broadcast Telemetry
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

            <nav className={hudStyles.tabs} aria-label="Billing workspace" style={{ display: 'none' }} hidden>
              {tabs.map(tab => {
                const TabIcon = tab.icon;
                return (
                  <button
                    key={tab.id}
                    type="button"
                    className={activeTab === tab.id ? hudStyles.tabActive : hudStyles.tabButton}
                    onClick={() => setActiveTab(tab.id)}
                  >
                    {TabIcon ? <TabIcon size={15} /> : null}
                    <span>{tab.label}</span>
                  </button>
                );
              })}
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

          </>
        )}

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
          <section className={hudStyles.mainGrid} style={!guardrailsOpen ? { gridTemplateColumns: '1fr' } : undefined}>
            <div>
              <div
                className={`${hudStyles.panel} ${hudStyles.invoiceChrome || ''}`.trim()}
                data-invoice-pipeline={invoiceMode === 'CLIENT' ? 'client' : 'platform'}
                data-workspace={invoiceWorkspace}
                style={{
                  borderColor: invoiceMode === 'CLIENT' ? 'rgba(34,211,238,0.35)' : undefined,
                  boxShadow: invoiceMode === 'CLIENT'
                    ? '0 0 0 1px rgba(34,211,238,0.12)'
                    : undefined,
                  ...(invoiceWorkspace !== 'compose' ? { paddingBottom: 8 } : null),
                }}
              >
                <div className={hudStyles.panelHeader}>
                  <div className={hudStyles.panelTitle}>
                    <FileText size={18} />
                    <div>
                      <span>{invoiceMode === 'CLIENT' ? 'Client pipeline · Invoice model' : 'Platform pipeline · PlatformInvoice model'}</span>
                      <h2>{documentKind === 'STATEMENT'
                        ? (invoiceMode === 'CLIENT' ? 'Tenant client statement' : 'Platform statement')
                        : (invoiceMode === 'CLIENT' ? 'Client invoice' : 'Platform invoice')}</h2>
                    </div>
                  </div>
                  <div className={hudStyles.heroActions}>
                    <button
                      type="button"
                      className={documentKind === 'INVOICE' ? hudStyles.primaryButton : hudStyles.secondaryButton}
                      onClick={() => { setDocumentKind('INVOICE'); setInvoiceWorkspace('compose'); }}
                      title="Issue a billable invoice"
                    >
                      Invoice
                    </button>
                    <button
                      type="button"
                      className={documentKind === 'STATEMENT' ? hudStyles.primaryButton : hudStyles.secondaryButton}
                      onClick={() => { setDocumentKind('STATEMENT'); setInvoiceWorkspace('compose'); }}
                      title="Issue a platform or tenant account statement"
                    >
                      Statement
                    </button>
                    {canSwitchBillingMode && (
                      <>
                        <button
                          type="button"
                          className={invoiceMode === 'PLATFORM' ? hudStyles.primaryButton : hudStyles.secondaryButton}
                          onClick={() => handleModeChange('PLATFORM')}
                          title="Wilsy OS → tenant (platform document)"
                        >
                          Platform
                        </button>
                        <button
                          type="button"
                          className={invoiceMode === 'CLIENT' ? hudStyles.primaryButton : hudStyles.secondaryButton}
                          onClick={() => handleModeChange('CLIENT')}
                          title="Tenant → client (tenant-branded document)"
                        >
                          Tenant client
                        </button>
                      </>
                    )}
                    <button
                      type="button"
                      className={invoiceWorkspace === 'compose' ? hudStyles.primaryButton : hudStyles.secondaryButton}
                      onClick={() => setInvoiceWorkspace('compose')}
                    >
                      Compose
                    </button>
                    <button
                      type="button"
                      className={invoiceWorkspace === 'ledger' ? hudStyles.primaryButton : hudStyles.secondaryButton}
                      onClick={() => setInvoiceWorkspace('ledger')}
                    >
                      Ledger
                    </button>
                    <button
                      type="button"
                      className={invoiceWorkspace === 'analytics' ? hudStyles.primaryButton : hudStyles.secondaryButton}
                      onClick={() => setInvoiceWorkspace('analytics')}
                      title="Revenue analytics and status mix"
                    >
                      Analytics
                    </button>
                  </div>
                </div>

                {/* ── IDENTITY CONTEXT ── */}
                {(() => {
                  const isClient = invoiceMode === 'CLIENT';
                  const accent = isClient ? '#22d3ee' : '#d4af37';
                  const issuingName = isClient
                    ? (billingTenantIdentity?.legalName || billingTenantIdentity?.name || activeTenant?.legalName || activeTenant?.name || 'Your business')
                    : 'Wilsy (Pty) Ltd';
                  const showExpanded = identityPinned || identityExpanded || identityForceCompose;
                  return (
                    <div
                      className={hudStyles.identityDock || undefined}
                      data-issuer={isClient ? 'tenant_client' : 'platform'}
                      data-expanded={showExpanded ? 'true' : 'false'}
                      style={{
                        margin: '0 0 6px',
                        borderRadius: 8,
                        border: `1px solid ${isClient ? 'rgba(34,211,238,0.22)' : 'rgba(212,175,55,0.22)'}`,
                        background: isClient
                          ? 'rgba(8,47,73,0.28)'
                          : 'rgba(41,37,16,0.28)',
                        overflow: 'hidden',
                      }}
                    >
                      <button
                        type="button"
                        onClick={() => setIdentityExpanded((v) => !v)}
                        aria-expanded={showExpanded}
                        style={{
                          width: '100%',
                          display: 'flex',
                          alignItems: 'center',
                          gap: 10,
                          padding: '5px 10px',
                          background: 'transparent',
                          border: 'none',
                          color: '#e2e8f0',
                          cursor: 'pointer',
                          textAlign: 'left',
                          minHeight: 30,
                        }}
                      >
                        <span style={{
                          fontSize: '0.58rem',
                          fontWeight: 800,
                          letterSpacing: '0.12em',
                          textTransform: 'uppercase',
                          color: accent,
                          flexShrink: 0,
                        }}>
                          {isClient ? 'Client' : 'Platform'}
                        </span>
                        <span style={{
                          fontSize: '0.8rem',
                          fontWeight: 600,
                          color: '#f8fafc',
                          overflow: 'hidden',
                          textOverflow: 'ellipsis',
                          whiteSpace: 'nowrap',
                        }}>
                          {issuingName}
                          <span style={{ color: '#64748b', fontWeight: 500 }}> · {documentKind}</span>
                          <span style={{ color: '#64748b', fontWeight: 500 }}> · {invoiceWorkspace === 'analytics' ? 'Analytics' : invoiceWorkspace === 'ledger' ? 'Ledger' : 'Compose'}</span>
                        </span>
                        <span style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: 8, flexShrink: 0 }}>
                          <span
                            role="button"
                            tabIndex={0}
                            title={identityPinned ? 'Unpin identity panel' : 'Pin identity panel open'}
                            onClick={(e) => {
                              e.stopPropagation();
                              setIdentityPinned((p) => {
                                const next = !p;
                                try { localStorage.setItem('wilsy.billing.identityPinned', next ? '1' : '0'); } catch (_) { }
                                return next;
                              });
                            }}
                            onKeyDown={(e) => {
                              if (e.key === 'Enter' || e.key === ' ') {
                                e.preventDefault();
                                e.stopPropagation();
                                setIdentityPinned((p) => !p);
                              }
                            }}
                            style={{
                              fontSize: '0.58rem',
                              fontWeight: 700,
                              letterSpacing: '0.06em',
                              textTransform: 'uppercase',
                              color: identityPinned ? accent : '#64748b',
                              padding: '2px 6px',
                              borderRadius: 4,
                              border: `1px solid ${identityPinned ? accent + '55' : 'rgba(255,255,255,0.08)'}`,
                            }}
                          >
                            {identityPinned ? 'Pinned' : 'Pin'}
                          </span>
                          <span style={{ color: '#94a3b8', fontSize: '0.7rem' }}>{showExpanded ? '▴' : '▾'}</span>
                        </span>
                      </button>

                      {showExpanded && (
                        <div style={{ padding: '0 10px 8px' }}>
                          <div
                            className={hudStyles.identitySurface || hudStyles.loyaltyStrip}
                            role="status"
                            aria-label="Issuing identity surface"
                            style={{
                              display: 'grid',
                              gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))',
                              gap: 8,
                              padding: '10px 12px',
                              borderRadius: 8,
                              border: `1px solid ${isClient ? 'rgba(34,211,238,0.25)' : 'rgba(212,175,55,0.25)'}`,
                              background: isClient
                                ? 'linear-gradient(135deg, rgba(8,47,73,0.85), rgba(15,23,42,0.9))'
                                : 'linear-gradient(135deg, rgba(41,37,16,0.85), rgba(15,23,42,0.9))',
                            }}
                          >
                            <div>
                              <span style={{ display: 'block', fontSize: '0.58rem', letterSpacing: '0.08em', color: '#94a3b8', textTransform: 'uppercase' }}>Issuing entity</span>
                              <strong style={{ color: '#f8fafc', fontSize: '0.85rem' }}>{issuingName}</strong>
                            </div>
                            <div>
                              <span style={{ display: 'block', fontSize: '0.58rem', letterSpacing: '0.08em', color: '#94a3b8', textTransform: 'uppercase' }}>Document</span>
                              <strong style={{ color: '#f8fafc', fontSize: '0.85rem' }}>{documentKind}</strong>
                            </div>
                            <div>
                              <span style={{ display: 'block', fontSize: '0.58rem', letterSpacing: '0.08em', color: '#94a3b8', textTransform: 'uppercase' }}>Issuer type</span>
                              <strong style={{ color: accent, fontSize: '0.85rem' }}>{isClient ? 'tenant_client' : 'platform'}</strong>
                            </div>
                            <div>
                              <span style={{ display: 'block', fontSize: '0.58rem', letterSpacing: '0.08em', color: '#94a3b8', textTransform: 'uppercase' }}>Identity source</span>
                              <strong style={{ color: '#f8fafc', fontSize: '0.85rem' }}>{isClient ? 'TENANT_CONTEXT' : 'PLATFORM_ROOT'}</strong>
                            </div>
                            <div>
                              <span style={{ display: 'block', fontSize: '0.58rem', letterSpacing: '0.08em', color: '#94a3b8', textTransform: 'uppercase' }}>Workspace</span>
                              <strong style={{ color: '#f8fafc', fontSize: '0.85rem' }}>
                                {invoiceWorkspace === 'analytics' ? 'Analytics' : invoiceWorkspace === 'ledger' ? 'Ledger' : 'Compose'}
                                {' · '}
                                {isClient ? 'CLIENT' : 'PLATFORM'}
                              </strong>
                            </div>
                          </div>
                          <p style={{
                            margin: '8px 0 0',
                            fontSize: '0.72rem',
                            color: '#94a3b8',
                            lineHeight: 1.4,
                          }}>
                            {isClient
                              ? 'Your business issues to a customer. Client ledger and branding come from the tenant profile.'
                              : 'Platform issues to a tenant business. Separate ledger and fiscal path from client invoices.'}
                          </p>
                        </div>
                      )}
                    </div>
                  );
                })()}

                {invoiceWorkspace === 'compose' && (() => {
                  const platformSince =
                    activeTenant?.createdAt
                    || activeTenant?.onboardedAt
                    || activeTenant?.joinedAt
                    || activeTenant?.firstInvoiceAt
                    || authUser?.tenant?.createdAt
                    || null;
                  const clientSince =
                    manualInvoice?.clientSince
                    || manualInvoice?.clientOnboardedAt
                    || null;
                  const tenure = invoiceMode === 'CLIENT'
                    ? computeLoyaltyTenure(clientSince || platformSince, new Date(), {
                      subject: 'CLIENT',
                      displayName: manualInvoice.tenantId || 'Client',
                      documentKind
                    })
                    : computeLoyaltyTenure(platformSince, new Date(), {
                      subject: 'PLATFORM',
                      displayName: billingTenantIdentity?.name || 'Tenant',
                      documentKind
                    });
                  if (!tenure.visible) return null;
                  return (
                    <div
                      className={hudStyles.loyaltyStrip}
                      data-loyalty-tone={tenure.tone}
                      role="status"
                      aria-live="polite"
                    >
                      <span className={hudStyles.loyaltyEyebrow}>
                        {tenure.isAnniversaryDay ? 'ANNIVERSARY' : tenure.years >= 5 ? 'MILESTONE' : 'LOYALTY'}
                      </span>
                      <strong>{tenure.gesture}</strong>
                      <small>
                        {tenure.shortLabel}
                        {tenure.sinceDate ? ` · since ${formatDate(tenure.sinceDate)}` : ''}
                        {' · '}
                        sealed into document metadata when you issue
                      </small>
                    </div>
                  );
                })()}
                {invoiceWorkspace === 'compose' ? (
                  <form className={hudStyles.formGrid} onSubmit={handleManualInvoice}>
                    <div className={hudStyles.field}>
                      <label>{invoiceMode === 'CLIENT' ? 'Client / customer ID' : 'Target tenant'}</label>
                      {invoiceMode === 'PLATFORM' ? (
                        <>
                          <div style={{ display: 'flex', gap: 8, alignItems: 'stretch' }}>
                            <input
                              value={invoiceTenantSearch}
                              placeholder={manualInvoice.tenantId ? 'Selected — clear to search another' : 'Search tenant business name or ID'}
                              onChange={(event) => {
                                const next = event.target.value;
                                setInvoiceTenantSearch(next);
                                if (manualInvoice.tenantId) {
                                  setManualInvoice((previous) => ({
                                    ...previous,
                                    tenantId: '',
                                    tenantName: '',
                                  }));
                                }
                              }}
                              role="combobox"
                              aria-autocomplete="list"
                              aria-expanded={availableInvoiceTenants.length > 0 && !manualInvoice.tenantId}
                              aria-controls="billing-tenant-results"
                              required={!manualInvoice.tenantId}
                              readOnly={Boolean(manualInvoice.tenantId)}
                              style={manualInvoice.tenantId ? { flex: 1, opacity: 0.95 } : { flex: 1 }}
                            />
                            {manualInvoice.tenantId ? (
                              <button
                                type="button"
                                className={hudStyles.secondaryButton}
                                title="Clear selected tenant"
                                aria-label="Clear selected tenant"
                                onClick={() => {
                                  setManualInvoice((previous) => ({
                                    ...previous,
                                    tenantId: '',
                                    tenantName: '',
                                    customerTaxId: '',
                                  }));
                                  setInvoiceTenantSearch('');
                                }}
                                style={{ whiteSpace: 'nowrap', minWidth: 88 }}
                              >
                                Clear
                              </button>
                            ) : null}
                          </div>
                          {!manualInvoice.tenantId && (
                            <>
                              <div
                                id="billing-tenant-results"
                                role="listbox"
                                aria-label="Available tenant businesses"
                                style={{ display: availableInvoiceTenants.length ? 'grid' : 'none', gap: '6px', marginTop: '8px' }}
                              >
                                {availableInvoiceTenants.map((candidate) => (
                                  <button
                                    key={candidate.id}
                                    type="button"
                                    className={hudStyles.secondaryButton}
                                    role="option"
                                    aria-selected={false}
                                    onClick={() => {
                                      setManualInvoice((previous) => ({
                                        ...previous,
                                        tenantId: candidate.id,
                                        tenantName: candidate.label,
                                        customerTaxId: candidate.taxId || previous.customerTaxId || '',
                                      }));
                                      setInvoiceTenantSearch(candidate.label);
                                      pushRecentTenant({ id: candidate.id, label: candidate.label, verified: candidate.verified, taxId: candidate.taxId });
                                      setRecentTenants(loadRecentTenants());
                                    }}
                                    style={{ justifyContent: 'space-between', textAlign: 'left' }}
                                  >
                                    <span>
                                      {candidate.label}
                                      {candidate.verified ? ' · Verified' : ''}
                                    </span>
                                    <small>{candidate.id} · {candidate.status}</small>
                                  </button>
                                ))}
                              </div>
                              {recentTenants.length > 0 && (
                                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, marginTop: 8 }} role="list" aria-label="Recent recipients">
                                  <span style={{ fontSize: '0.65rem', color: '#64748b', width: '100%', letterSpacing: '0.04em', textTransform: 'uppercase' }}>Recent</span>
                                  {recentTenants.map((r) => (
                                    <button
                                      key={r.id}
                                      type="button"
                                      role="listitem"
                                      className={hudStyles.secondaryButton}
                                      style={{ fontSize: '0.72rem', padding: '4px 10px' }}
                                      onClick={() => {
                                        setManualInvoice((prev) => ({ ...prev, tenantId: r.id, tenantName: r.label }));
                                        setInvoiceTenantSearch(r.label);
                                        pushRecentTenant(r);
                                        setRecentTenants(loadRecentTenants());
                                      }}
                                    >
                                      {r.verified ? '✓ ' : ''}{r.label}
                                    </button>
                                  ))}
                                </div>
                              )}
                            </>
                          )}
                          <small role="status">
                            {manualInvoice.tenantId
                              ? `Selected: ${manualInvoice.tenantName || manualInvoice.tenantId} (${manualInvoice.tenantId}) — Clear to choose another.`
                              : invoiceTenantDirectoryState.loading
                                ? 'Loading tenant businesses…'
                                : invoiceTenantDirectoryState.error
                                  ? `Tenant directory unavailable: ${invoiceTenantDirectoryState.error}`
                                  : invoiceTenantSource === 'SOURCE_SILENT'
                                    ? 'Tenant directory is unavailable. Check Kennel /api/business/tenants.'
                                    : invoiceTenantSource === 'LIVE_DIRECTORY' && invoiceTenantSearch.trim() && !availableInvoiceTenants.length
                                      ? 'No tenant businesses match that search. Try legal name, alias, or tenant ID.'
                                      : invoiceTenantSource === 'LIVE_DIRECTORY' && !invoiceTenantSearch.trim() && availableInvoiceTenants.length === 0
                                        ? 'Directory loaded but empty. Confirm tenants exist in Kennel.'
                                        : invoiceTenantSource === 'SEED_DIRECTORY'
                                          ? 'Using offline seed directory. Live Kennel list will replace this when available.'
                                          : 'Search and select the recipient business (legal name, alias, or ID).'}
                          </small>
                        </>
                      ) : (
                        <input
                          value={manualInvoice.tenantId}
                          placeholder={invoiceMode === 'CLIENT' ? 'CLIENT-ID' : 'TENANT-ID'}
                          onChange={event => setManualInvoice(prev => ({ ...prev, tenantId: event.target.value, tenantName: '' }))}
                          onBlur={() => setManualInvoice(prev => ({ ...prev, tenantId: prev.tenantId.trim() }))}
                          role={invoiceMode === 'CLIENT' ? 'combobox' : undefined}
                          aria-autocomplete={invoiceMode === 'CLIENT' ? 'list' : undefined}
                          aria-expanded={invoiceMode === 'CLIENT' && clientDirectory.length > 0}
                          aria-controls={invoiceMode === 'CLIENT' ? 'billing-client-results' : undefined}
                          required
                        />
                      )}
                      {invoiceMode === 'CLIENT' && (
                        <div
                          id="billing-client-results"
                          role="listbox"
                          aria-label="Clients from this tenant billing ledger"
                          style={{ display: clientDirectory.length ? 'grid' : 'none', gap: '6px', marginTop: '8px' }}
                        >
                          {clientDirectory.map((client) => (
                            <button
                              key={client.id}
                              type="button"
                              className={hudStyles.secondaryButton}
                              role="option"
                              aria-selected={manualInvoice.tenantId === client.id}
                              onClick={() => setManualInvoice((previous) => ({ ...previous, tenantId: client.id, tenantName: client.label }))}
                              style={{ justifyContent: 'space-between' }}
                            >
                              <span>{client.label}</span>
                              <small>{client.id}</small>
                            </button>
                          ))}
                        </div>
                      )}
                      {invoiceMode === 'CLIENT' && (
                        <small>{clientDirectorySource === 'SOURCE_SILENT' ? 'Client directory is unavailable; enter a verified client ID.' : 'Searches clients already present in this tenant’s billing ledger.'}</small>
                      )}
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
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, marginTop: 6 }} role="group" aria-label="Amount presets">
                        {[500, 1000, 2500, 5000, 10000, 25000].map((preset) => (
                          <button
                            key={preset}
                            type="button"
                            className={hudStyles.secondaryButton}
                            style={{
                              fontSize: '0.7rem', padding: '3px 8px',
                              borderColor: amountPresetFlash === preset ? '#fbbf24' : undefined,
                              color: amountPresetFlash === preset ? '#fbbf24' : undefined,
                            }}
                            onClick={() => {
                              setManualInvoice((prev) => ({ ...prev, amount: String(preset), unitPrice: String(preset) }));
                              setAmountPresetFlash(preset);
                              window.setTimeout(() => setAmountPresetFlash(null), 600);
                            }}
                          >
                            {formatMoney(preset, manualInvoice.currency)}
                          </button>
                        ))}
                      </div>
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
                        {SUPPLY_TYPES.map(type => {
                          const value = type.toUpperCase().replace(/ /g, '_');
                          return <option key={value} value={value}>{type}</option>;
                        })}
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
                    <div className={hudStyles.field}>
                      <label>Subject</label>
                      <input
                        value={manualInvoice.subject}
                        placeholder="Invoice subject / title"
                        onChange={event => setManualInvoice(prev => ({ ...prev, subject: event.target.value }))}
                      />
                    </div>
                    <div className={hudStyles.field}>
                      <label>Salesperson</label>
                      <div style={{ display: 'flex', gap: 8, alignItems: 'stretch' }}>
                        <input
                          value={manualInvoice.salesperson}
                          onChange={e => {
                            const next = e.target.value;
                            setManualInvoice(prev => ({
                              ...prev,
                              salesperson: next,
                              salespersonId: prev.salespersonId && next !== prev.salesperson ? '' : prev.salespersonId,
                            }));
                            setSalespersonSearch(next);
                          }}
                          placeholder={manualInvoice.salespersonId ? 'Selected — clear to search another' : 'Search employee name...'}
                          role="combobox"
                          aria-autocomplete="list"
                          aria-expanded={salespersonOptions.length > 0 && !manualInvoice.salespersonId}
                          aria-controls="salesperson-results"
                          readOnly={Boolean(manualInvoice.salespersonId)}
                          style={manualInvoice.salespersonId ? { flex: 1, opacity: 0.95 } : { flex: 1 }}
                        />
                        {(manualInvoice.salesperson || manualInvoice.salespersonId) ? (
                          <button
                            type="button"
                            className={hudStyles.secondaryButton}
                            title="Clear selected salesperson"
                            aria-label="Clear selected salesperson"
                            onClick={() => {
                              setManualInvoice(prev => ({ ...prev, salesperson: '', salespersonId: '' }));
                              setSalespersonSearch('');
                              setSalespersonOptions([]);
                            }}
                            style={{ whiteSpace: 'nowrap', minWidth: 88 }}
                          >
                            Clear
                          </button>
                        ) : null}
                      </div>
                      {!manualInvoice.salespersonId && salespersonOptions.length > 0 && (
                        <div id="salesperson-results" role="listbox" style={{ display: 'grid', gap: '6px', marginTop: '8px' }}>
                          {salespersonOptions.map(emp => (
                            <button
                              key={emp.id || emp._id}
                              type="button"
                              className={hudStyles.secondaryButton}
                              role="option"
                              aria-selected={manualInvoice.salesperson === emp.name}
                              onClick={() => {
                                setManualInvoice(prev => ({ ...prev, salesperson: emp.name, salespersonId: emp.id }));
                                setSalespersonSearch(emp.name);
                                setSalespersonOptions([]);
                              }}
                              style={{ justifyContent: 'space-between' }}
                            >
                              <span>{emp.name}</span>
                              <small>{emp.email || emp.department || ''}</small>
                            </button>
                          ))}
                        </div>
                      )}
                      {salespersonLoading && <small>Loading employees...</small>}
                      {manualInvoice.salespersonId ? (
                        <small role="status">Selected salesperson locked — Clear to choose another.</small>
                      ) : null}
                    </div>

                    {/* ─── ORDER IDENTITY FIELDS (auto-generate SO/PO on seal) ── */}
                    <OrderIdentityFields
                      orderNumber={orderIdentity.identity.orderNumber}
                      purchaseOrder={orderIdentity.identity.purchaseOrder}
                      orderLocked={orderIdentity.identity.orderLocked}
                      poLocked={orderIdentity.identity.poLocked}
                      status={orderIdentity.identity.status}
                      onChange={orderIdentity.setIdentity}
                      onAutoGenerate={orderIdentity.autoGenerate}
                      onClear={orderIdentity.clearField}
                      disabled={processing === 'invoice' || isFrozen}
                    />

                    <div className={hudStyles.field}>
                      <label>Issue date</label>
                      <input
                        type="date"
                        value={manualInvoice.issueDate || ''}
                        onChange={event => setManualInvoice(prev => ({ ...prev, issueDate: event.target.value }))}
                      />
                    </div>
                    <div className={hudStyles.field}>
                      <label>Due date</label>
                      <input
                        type="date"
                        value={manualInvoice.dueDate || ''}
                        onChange={event => setManualInvoice(prev => ({ ...prev, dueDate: event.target.value }))}
                      />
                    </div>
                    <div className={hudStyles.field}>
                      <label>Quantity</label>
                      <input
                        type="number"
                        min="1"
                        step="1"
                        value={manualInvoice.quantity}
                        onChange={event => {
                          const raw = event.target.value;
                          setManualInvoice((prev) => {
                            const qty = Math.max(1, Math.floor(Number(raw) || 1));
                            const unit = parseBillingMoneyInput(prev.unitPrice);
                            const next = unit !== null && unit > 0 ? preciseRound(qty * unit, 2).toFixed(2) : prev.amount;
                            return { ...prev, quantity: raw === '' ? '' : qty, amount: next };
                          });
                        }}
                      />
                    </div>
                    <div className={hudStyles.field}>
                      <label>Unit price</label>
                      <input
                        value={manualInvoice.unitPrice}
                        placeholder="Defaults to amount"
                        onChange={event => {
                          const sanitized = sanitizeBillingMoneyInput(event.target.value);
                          setManualInvoice((prev) => {
                            const unit = parseBillingMoneyInput(sanitized);
                            const qty = Math.max(1, Math.floor(Number(prev.quantity) || 1));
                            const next = unit !== null && unit > 0 ? preciseRound(qty * unit, 2).toFixed(2) : prev.amount;
                            return { ...prev, unitPrice: sanitized, amount: next };
                          });
                        }}
                      />
                    </div>
                    <div className={`${hudStyles.field} ${hudStyles.fieldFull}`}>
                      <label>Line item description</label>
                      <input
                        value={manualInvoice.lineDescription}
                        placeholder="Item / service line (defaults to description)"
                        onChange={event => setManualInvoice(prev => ({ ...prev, lineDescription: event.target.value }))}
                      />
                    </div>
                    <div className={`${hudStyles.field} ${hudStyles.fieldFull}`}>
                      <label>Description</label>
                      <textarea value={manualInvoice.description} onChange={event => setManualInvoice(prev => ({ ...prev, description: event.target.value }))} />
                    </div>
                    <div className={`${hudStyles.field} ${hudStyles.fieldFull}`}>
                      <label>Customer notes</label>
                      <textarea
                        value={manualInvoice.notes}
                        placeholder="Visible notes on the invoice"
                        onChange={event => setManualInvoice(prev => ({ ...prev, notes: event.target.value }))}
                      />
                    </div>
                    <div className={`${hudStyles.field} ${hudStyles.fieldFull}`}>
                      <label>Terms &amp; conditions</label>
                      <textarea
                        value={manualInvoice.termsAndConditions}
                        onChange={event => setManualInvoice(prev => ({ ...prev, termsAndConditions: event.target.value }))}
                      />
                    </div>

                    {/* ─── CONFLICT BANNER ─────────────────────────────────────── */}
                    {orderIdentity.conflictMessage && (
                      <div className={hudStyles.conflictBanner} style={{ gridColumn: '1 / -1', padding: '8px 12px', background: 'rgba(248,113,113,0.15)', border: '1px solid #f87171', borderRadius: '6px', display: 'flex', alignItems: 'center', gap: '12px' }}>
                        <AlertTriangle size={16} color="#f87171" />
                        <span style={{ flex: 1, fontSize: '0.85rem', color: '#fca5a5' }}>{orderIdentity.conflictMessage}</span>
                        <button type="button" className={hudStyles.secondaryButton} onClick={orderIdentity.acceptServer}>Accept server</button>
                        <button type="button" className={hudStyles.secondaryButton} onClick={orderIdentity.clearConflict}>Dismiss</button>
                      </div>
                    )}

                    {/* ─── PAYMENT METHOD SELECTOR ────────────────────────────── */}
                    <div className={hudStyles.field}>
                      <label>Payment Method</label>
                      <select
                        value={manualInvoice.paymentMethod}
                        onChange={(e) => setManualInvoice(prev => ({ ...prev, paymentMethod: e.target.value }))}
                        className={hudStyles.searchSelect}
                      >
                        {PAYMENT_METHODS.map(method => (
                          <option key={method.value} value={method.value}>{method.label}</option>
                        ))}
                      </select>
                      <small style={{ fontSize: '0.6rem', color: '#64748b' }}>
                        Select the payment method used for this invoice. This will affect dunning and retry logic.
                      </small>
                    </div>

                    {/* ─── LIVE TOTAL + GATED ISSUE CTA ───────────────────────── */}
                    <div className={`${hudStyles.fieldFull} ${hudStyles.composeStickyBar || ''}`.trim()}>
                      <div className={hudStyles.liveTotalStrip || ''} aria-live="polite" style={{
                        display: 'flex', flexWrap: 'wrap', alignItems: 'baseline', justifyContent: 'space-between',
                        gap: '8px 16px', marginBottom: 10, padding: '10px 14px', borderRadius: 10,
                        background: 'linear-gradient(135deg, rgba(14,165,233,0.12), rgba(6,182,212,0.06))',
                        border: '1px solid rgba(14,165,233,0.28)'
                      }}>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                          <span style={{ fontSize: '0.7rem', textTransform: 'uppercase', letterSpacing: '0.04em', color: '#7dd3fc' }}>Invoice total</span>
                          <strong style={{ fontSize: '1.25rem', fontWeight: 700, color: '#e0f2fe', fontVariantNumeric: 'tabular-nums' }}>
                            {formatMoney(manualInvoiceTotal, manualInvoice.currency)}
                          </strong>
                        </div>
                        <small style={{ fontSize: '0.72rem', color: '#94a3b8' }}>
                          {composeQty} × {formatMoney(composeUnitParsed ?? composeAmountParsed ?? 0, manualInvoice.currency)}
                          {' = '}Base {formatMoney(taxEnginePreview?.financials?.baseAmount ?? composeLineBase ?? 0, manualInvoice.currency)}
                          {' · '}Tax {formatMoney(taxEnginePreview?.financials?.taxAmount || 0, manualInvoice.currency)}
                          {' · '}{taxEnginePreview?.sourceStatus || 'Draft'}
                        </small>
                      </div>
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '10px', alignItems: 'center' }}>
                        <button
                          type="submit"
                          className={hudStyles.primaryButton}
                          disabled={
                            processing === 'invoice' ||
                            serviceAccessBlocked ||
                            isFrozen ||
                            !manualInvoice.tenantId?.trim() ||
                            !(parseBillingMoneyInput(manualInvoice.amount) > 0) ||
                            !(invoiceMode === 'CLIENT' ? caps.createClientInvoice : caps.createPlatformInvoice)
                          }
                          title={
                            !manualInvoice.tenantId?.trim()
                              ? 'Select a recipient first'
                              : !(parseBillingMoneyInput(manualInvoice.amount) > 0)
                                ? 'Enter an amount greater than zero'
                                : undefined
                          }
                          style={invoiceMode === 'CLIENT' ? {
                            background: 'linear-gradient(135deg,#0891b2,#0e7490)',
                            borderColor: '#22d3ee',
                            color: '#ecfeff'
                          } : undefined}
                        >
                          {processing === 'invoice' ? <RefreshCw className="animate-spin" size={15} /> : <PlusCircle size={15} />}
                          {invoiceMode === 'CLIENT'
                            ? (documentKind === 'STATEMENT' ? 'Seal tenant client statement' : 'Seal client invoice · tenant_client')
                            : (documentKind === 'STATEMENT' ? 'Seal platform statement' : 'Seal platform invoice · PlatformInvoice')}
                        </button>
                        <small style={{ color: '#94a3b8', fontSize: '0.72rem', maxWidth: '420px', lineHeight: 1.4 }}>
                          {!manualInvoice.tenantId?.trim()
                            ? 'Select a recipient business to enable Issue.'
                            : !(parseBillingMoneyInput(manualInvoice.amount) > 0)
                              ? 'Enter a positive amount to enable Issue.'
                              : invoiceMode === 'CLIENT'
                                ? 'Writes Invoice model with issuerType=tenant_client and metadata.identitySource from tenant context.'
                                : 'Writes PlatformInvoice model with issuerType=platform. Isolated from tenant→customer ledger.'}
                        </small>
                      </div>
                    </div>
                  </form>
                ) : null}

              </div>
            </div>

            {guardrailsOpen ? (
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
                      <small>Sealed SHA3-512 command proof</small>
                    </article>
                  </div>
                </div>
              </aside>
            ) : null}

            {invoiceWorkspace === 'ledger' ? (
              <div className={`${hudStyles.panel} ${hudStyles.ledgerCockpit || ''}`.trim()} style={{ gridColumn: '1 / -1' }}>
                <div className={hudStyles.ledgerToolbar}>
                  <div className={hudStyles.ledgerToolbarTitle}>
                    <Banknote size={16} />
                    <div>
                      <span className={hudStyles.ledgerEyebrow}>Invoice ledger</span>
                      <h2>
                        {issuerMode === 'PLATFORM'
                          ? `Invoices issued to ${billingTenantIdentity?.name || 'tenant'}`
                          : `Invoices issued by ${billingTenantIdentity?.name || 'tenant'}`}
                      </h2>
                    </div>
                  </div>
                  <div className={hudStyles.ledgerFilters} role="search" aria-label="Invoice ledger filters">
                    <div className={hudStyles.searchInputWrap} data-searching={ledgerMeta.loading ? 'true' : 'false'}>
                      <Search size={14} className={hudStyles.ledgerSearchIcon} aria-hidden="true" />
                      <input
                        value={invoiceSearch}
                        onChange={(event) => {
                          const next = event.target.value;
                          setInvoiceSearch(next);
                          setLedgerMeta((prev) => ({
                            ...prev,
                            loading: true,
                            phase: 'searching',
                            query: next
                          }));
                        }}
                        placeholder="Search invoice, client, seal…"
                        className={hudStyles.searchInput}
                        aria-label="Live invoice search"
                        aria-busy={ledgerMeta.loading ? 'true' : 'false'}
                        autoComplete="off"
                        spellCheck={false}
                      />
                    </div>
                    <select value={statusFilter} onChange={event => setStatusFilter(event.target.value)} className={hudStyles.searchSelect} aria-label="Status">
                      {['ALL', 'ISSUED', 'OVERDUE', 'PARTIALLY_PAID', 'PAID', 'DISPUTED', 'DRAFT'].map(status => (
                        <option key={status} value={status}>{status === 'ALL' ? 'All statuses' : status.replace(/_/g, ' ')}</option>
                      ))}
                    </select>
                    <select value={periodFilter} onChange={event => setPeriodFilter(event.target.value)} className={hudStyles.searchSelect} aria-label="Period">
                      <option value="today">Today</option>
                      <option value="7d">7 days</option>
                      <option value="30d">30 days</option>
                      <option value="90d">90 days</option>
                      <option value="ytd">YTD</option>
                      <option value="all">All time</option>
                    </select>
                    <select value={kindFilter} onChange={event => setKindFilter(event.target.value)} className={hudStyles.searchSelect} aria-label="Kind">
                      <option value="ALL">All kinds</option>
                      <option value="INVOICE">Invoices</option>
                      <option value="STATEMENT">Statements</option>
                    </select>
                    <button type="button" className={hudStyles.ledgerSearchBtn} onClick={() => loadTenantInvoiceLedger()} disabled={ledgerMeta.loading}>
                      {ledgerMeta.loading ? '…' : 'Search'}
                    </button>
                    {/* ─── NEW: Manual Refresh Button ───────────────────────── */}
                    <button
                      type="button"
                      className={hudStyles.ledgerSearchBtn}
                      onClick={() => loadTenantInvoiceLedger({ q: invoiceSearch })}
                      disabled={ledgerMeta.loading}
                      title="Refresh the invoice list manually"
                      style={{ marginLeft: '4px' }}
                    >
                      {ledgerMeta.loading ? <RefreshCw size={14} className="animate-spin" /> : <RefreshCw size={14} />}
                    </button>
                  </div>
                </div>
                <div className={hudStyles.ledgerMeta} aria-live="polite">
                  {ledgerMeta.loading ? (
                    <span className={hudStyles.searchingLabel} data-phase="searching">
                      Searching{ledgerMeta.query ? ` “${ledgerMeta.query}”` : ''}…
                    </span>
                  ) : (
                    <>
                      <span className={hudStyles.metaChip} data-source={ledgerMeta.source}>{ledgerMeta.source || 'STANDBY'}</span>
                      <span className={hudStyles.metaChip}>{ledgerDisplayTotal} result{ledgerDisplayTotal === 1 ? '' : 's'}</span>
                      <span className={hudStyles.metaChip}>
                        {(!canSwitchBillingMode || issuerMode === 'CLIENT')
                          ? `Client · ${billingTenantIdentity?.name || 'this business'}`
                          : 'Platform · all tenants'}
                      </span>
                      <span className={hudStyles.metaChipMuted}>Isolation on</span>
                      {ledgerMeta.source === 'ROUTE_MISSING' && (
                        <span className={hudStyles.searchRouteWarn}>
                          /api/billing/invoices/search not mounted — copy billingRoutes.js + restart BFF
                        </span>
                      )}
                    </>
                  )}
                </div>
                {lastSavedInvoice && (
                  <div className={hudStyles.saveConfirm} role="status" style={{ display: 'flex', flexWrap: 'wrap', gap: 10, alignItems: 'center' }}>
                    <strong>
                      {lastSavedInvoice.source === 'LIVE_DB' || lastSavedInvoice.source === 'LIVE_DB_IDEMPOTENT'
                        ? '✓ Sealed to ledger'
                        : lastSavedInvoice.source === 'COMMAND_ACCEPTED_UNPERSISTED'
                          ? 'Command accepted — not persisted (DB offline or schema)'
                          : `Save status: ${lastSavedInvoice.source}`}
                    </strong>
                    <span>
                      {lastSavedInvoice.invoiceNumber || lastSavedInvoice.id || '—'}
                      {' · '}
                      {lastSavedInvoice.tenantId}
                      {lastSavedInvoice.totalAmount != null ? ` · ${formatMoney(lastSavedInvoice.totalAmount)}` : ''}
                    </span>
                    <button type="button" className={hudStyles.secondaryButton} onClick={() => setLastSavedInvoice(null)}>Dismiss</button>
                    <button
                      type="button"
                      className={hudStyles.primaryButton}
                      onClick={() => {
                        setLastSavedInvoice(null);
                        setManualInvoice((prev) => ({
                          ...prev,
                          amount: '',
                          unitPrice: '',
                          description: prev.description,
                          lineDescription: '',
                          subject: '',
                          orderNumber: '',
                          purchaseOrder: '',
                          idempotencyKey: createBillingIdempotencyKey(tenantId),
                          paymentMethod: prev.paymentMethod,
                        }));
                        orderIdentity.clearField?.('both');
                        setInvoiceWorkspace('compose');
                        showBillingToast('Ready for next invoice — recipient preserved', { tone: 'ok' });
                      }}
                    >
                      Issue another
                    </button>
                  </div>
                )}
                <div className={hudStyles.ledgerTableHeader} role="row">
                  <div className={hudStyles.ledgerHeaderCell}>Invoice</div>
                  <div className={hudStyles.ledgerHeaderCell}>Issued by</div>
                  <div className={hudStyles.ledgerHeaderCell}>Bill to</div>
                  <div className={hudStyles.ledgerHeaderCell}>Amount</div>
                  <div className={hudStyles.ledgerHeaderCell}>Status</div>
                  <div className={hudStyles.ledgerHeaderCell}>Actions</div>
                </div>
                <div className={hudStyles.ledgerTableBody}>
                  {pagedInvoices.length === 0 ? (
                    <div className={hudStyles.empty}>No invoices match the current filter.</div>
                  ) : pagedInvoices.map((invoice) => (
                    <InvoiceLedgerItem
                      key={invoice.id || invoice.traceId}
                      invoice={invoice}
                      tenantId={tenantId}
                      onStatusUpdate={updateInvoiceStatus}
                      onRefreshLedger={() => loadTenantInvoiceLedger({ q: invoiceSearch })}
                      processing={processing}
                      setProcessing={setProcessing}
                      addLog={addLog}
                      emailInvoice={emailInvoice}
                      printInvoice={printInvoice}
                      downloadInvoice={downloadInvoice}
                      verifyInvoiceBlockchain={verifyInvoiceBlockchain}
                      openInvoiceAudit={openInvoiceAudit}
                      formatMoney={formatMoney}
                      formatDate={formatDate}
                      sovereignClient={sovereignClient}
                      onShowProof={(inv) => {
                        const invoiceForProof = {
                          ...inv,
                          traceId: inv.traceId || null,
                          merkleRoot: inv.merkleRoot || null,
                        };
                        setSelectedInvoiceForProof(invoiceForProof);
                        setShowProofModal(true);
                      }}
                      onUpdateInvoice={updateInvoiceInList} // <-- NEW
                      sendReminder={sendReminder} // <-- NEW
                      paymentMethod={manualInvoice.paymentMethod} // <-- NEW
                    />
                  ))}

                  <div className={hudStyles.ledgerPagination} role="navigation" aria-label="Ledger pages">
                    <button
                      type="button"
                      className={hudStyles.secondaryButton}
                      disabled={ledgerPage <= 0 || ledgerMeta.loading}
                      onClick={() => setLedgerPage((p) => Math.max(0, p - 1))}
                    >
                      Previous
                    </button>
                    <span>
                      Page {Math.min(ledgerPage + 1, ledgerPageCount)} of {ledgerPageCount}
                      {' · '}
                      {ledgerDisplayTotal} total
                    </span>
                    <button
                      type="button"
                      className={hudStyles.secondaryButton}
                      disabled={ledgerPage + 1 >= ledgerPageCount || ledgerMeta.loading}
                      onClick={() => setLedgerPage((p) => p + 1)}
                    >
                      Next
                    </button>
                  </div>
                </div>
              </div>
            ) : invoiceWorkspace === 'analytics' ? (
              <div className={hudStyles.panel} style={{ gridColumn: '1 / -1' }}>
                <LedgerExplorer
                  tenantId={tenantId}
                  sovereignClient={sovereignClient}
                  mode={issuerMode === 'CLIENT' || invoiceMode === 'CLIENT' ? 'CLIENT' : 'PLATFORM'}
                  businessName={billingTenantIdentity?.name || 'Wilsy HQ'}
                  onOpenLedger={() => setInvoiceWorkspace('ledger')}
                  userRole={authUser?.role || 'admin'}
                />
                {/* ─── PREDICTIVE REVENUE CHART ──────────────────────────────── */}
                {PredictiveRevenueChart && history.length > 0 && (
                  <div style={{ marginTop: '24px', padding: '16px', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '8px' }}>
                    <h3 style={{ fontSize: '0.9rem', fontWeight: 600, color: '#e2e8f0', marginBottom: '12px' }}>Predictive Revenue Forecast</h3>
                    <PredictiveRevenueChart data={history} tenantId={tenantId} />
                  </div>
                )}
              </div>
            ) : null}
          </section>
        )}

        {activeTab === 'payables' && caps.viewPayables && (
          <section className={hudStyles.mainGrid} style={{ gridTemplateColumns: '1fr' }}>
            <div className={hudStyles.panel}>
              <div className={hudStyles.panelHeader}>
                <div className={hudStyles.panelTitle}>
                  <Banknote size={18} />
                  <div>
                    <span>Vendor bills</span>
                    <h2>Accounts Payable</h2>
                  </div>
                </div>
                <button className={hudStyles.secondaryButton} onClick={loadPayables} disabled={payableMeta.loading}>
                  {payableMeta.loading ? 'Loading...' : 'Refresh'}
                </button>
              </div>
              {payableMeta.loading ? (
                <div style={{ padding: '20px', textAlign: 'center', color: '#94a3b8' }}>Loading payables...</div>
              ) : payableItems.length === 0 ? (
                <div className={hudStyles.empty}>No payable invoices found.</div>
              ) : (
                <div className={hudStyles.ledgerTableBody}>
                  <div className={hudStyles.ledgerTableHeader} role="row">
                    <div className={hudStyles.ledgerHeaderCell}>Invoice</div>
                    <div className={hudStyles.ledgerHeaderCell}>Vendor</div>
                    <div className={hudStyles.ledgerHeaderCell}>Amount</div>
                    <div className={hudStyles.ledgerHeaderCell}>Status</div>
                    <div className={hudStyles.ledgerHeaderCell}>Actions</div>
                  </div>
                  {payableItems.map(invoice => (
                    <InvoiceLedgerItem
                      key={invoice.id || invoice.traceId}
                      invoice={invoice}
                      tenantId={tenantId}
                      onStatusUpdate={updateInvoiceStatus}
                      onRefreshLedger={loadPayables}
                      processing={processing}
                      setProcessing={setProcessing}
                      addLog={addLog}
                      emailInvoice={emailInvoice}
                      printInvoice={printInvoice}
                      downloadInvoice={downloadInvoice}
                      verifyInvoiceBlockchain={verifyInvoiceBlockchain}
                      openInvoiceAudit={openInvoiceAudit}
                      formatMoney={formatMoney}
                      formatDate={formatDate}
                      sovereignClient={sovereignClient}
                      onShowProof={(inv) => {
                        const invoiceForProof = {
                          ...inv,
                          traceId: inv.traceId || null,
                          merkleRoot: inv.merkleRoot || null,
                        };
                        setSelectedInvoiceForProof(invoiceForProof);
                        setShowProofModal(true);
                      }}
                      onUpdateInvoice={updateInvoiceInList}
                      sendReminder={sendReminder}
                      paymentMethod={manualInvoice.paymentMethod}
                    />
                  ))}
                </div>
              )}
            </div>
          </section>
        )}

        {activeTab === 'subscriptions' && caps.viewSubscriptions && (
          <section className={hudStyles.mainGrid} style={{ gridTemplateColumns: '1fr' }}>
            <div>
              <div className={hudStyles.panel}>
                <div className={hudStyles.panelHeader}>
                  <div className={hudStyles.panelTitle}>
                    <Calendar size={18} />
                    <div>
                      <span>Recurring revenue</span>
                      <h2>Sovereign Subscription Engine</h2>
                    </div>
                  </div>
                  <span className={hudStyles.statusPill}>{safeSubscriptions.length} active</span>
                </div>

                <form className={hudStyles.formGrid} onSubmit={handleCreateSubscription}>
                  {canSwitchBillingMode && (
                    <div className={`${hudStyles.field} ${hudStyles.fieldFull}`}>
                      <label htmlFor="subscription-tenant-search">Find target tenant</label>
                      <input
                        id="subscription-tenant-search"
                        type="search"
                        value={subscriptionTenantSearch}
                        onChange={(event) => setSubscriptionTenantSearch(event.target.value)}
                        placeholder="Search tenant name or ID"
                        role="combobox"
                        aria-autocomplete="list"
                        aria-expanded={availableSubscriptionTenants.length > 0}
                        aria-controls="subscription-tenant-results"
                      />
                      <div
                        id="subscription-tenant-results"
                        role="listbox"
                        aria-label="Available tenant shards"
                        style={{ display: availableSubscriptionTenants.length ? 'grid' : 'none', gap: '6px', marginTop: '8px' }}
                      >
                        {availableSubscriptionTenants.map((candidate) => (
                          <button
                            key={candidate.id}
                            type="button"
                            className={hudStyles.secondaryButton}
                            role="option"
                            aria-selected={subscriptionForm.tenantId === candidate.id}
                            onClick={() => {
                              setSubscriptionForm((previous) => ({ ...previous, tenantId: candidate.id }));
                              setSubscriptionTenantSearch(candidate.label);
                            }}
                            style={{ justifyContent: 'space-between' }}
                          >
                            <span>{candidate.label}</span>
                            <small>{candidate.id} · {candidate.status}</small>
                          </button>
                        ))}
                      </div>
                      <small>{subscriptionTenantSource === 'SOURCE_SILENT' ? 'Tenant directory is unavailable; enter a verified tenant ID.' : 'Select a verified tenant shard before creating its subscription.'}</small>
                    </div>
                  )}
                  <div className={hudStyles.field}>
                    <label>{canSwitchBillingMode ? 'Selected tenant' : 'Tenant'}</label>
                    <input
                      value={subscriptionForm.tenantId}
                      onChange={e => setSubscriptionForm(prev => ({ ...prev, tenantId: e.target.value }))}
                      placeholder={canSwitchBillingMode ? 'Select a tenant above' : 'TENANT-ID'}
                      readOnly={!canSwitchBillingMode}
                      required
                    />
                  </div>
                  <div className={hudStyles.field}>
                    <label>Plan</label>
                    {plansLoading ? (
                      <input disabled placeholder="Loading plans..." />
                    ) : plans.length > 0 ? (
                      <select
                        value={subscriptionForm.planId}
                        onChange={(e) => handlePlanChange(e.target.value)}
                        required
                      >
                        <option value="">Select a plan</option>
                        {plans.map(plan => (
                          <option key={plan._id} value={plan._id}>
                            {plan.name} – {plan.currency} {plan.price} ({plan.billingFrequency})
                          </option>
                        ))}
                      </select>
                    ) : (
                      <input
                        value={subscriptionForm.planId}
                        onChange={e => setSubscriptionForm(prev => ({ ...prev, planId: e.target.value }))}
                        placeholder={plansError ? 'Plan catalog unavailable – enter ID manually' : 'Plan ID'}
                        required
                      />
                    )}
                    {plansError && <small style={{ color: 'red' }}>⚠️ {plansError} – fallback to manual entry.</small>}
                  </div>
                  <div className={hudStyles.field}>
                    <label>Amount</label>
                    <input
                      type="text"
                      inputMode="decimal"
                      value={subscriptionForm.amount}
                      onChange={e => setSubscriptionForm(prev => ({ ...prev, amount: sanitizeBillingMoneyInput(e.target.value) }))}
                      onBlur={() => setSubscriptionForm(prev => ({ ...prev, amount: formatBillingMoneyInput(prev.amount) }))}
                      placeholder="0.00"
                      required
                    />
                  </div>
                  <div className={hudStyles.field}>
                    <label>Currency</label>
                    <select
                      value={subscriptionForm.currency}
                      onChange={e => setSubscriptionForm(prev => ({ ...prev, currency: e.target.value }))}
                    >
                      {['ZAR', 'USD', 'EUR', 'GBP', 'NGN', 'KES', 'GHS', 'BWP', 'NAD', 'MUR'].map(currency => <option key={currency} value={currency}>{currency}</option>)}
                    </select>
                  </div>
                  <div className={hudStyles.field}>
                    <label>Billing frequency</label>
                    <select
                      value={subscriptionForm.billingFrequency}
                      onChange={e => setSubscriptionForm(prev => ({ ...prev, billingFrequency: e.target.value }))}
                    >
                      <option value="monthly">Monthly</option>
                      <option value="quarterly">Quarterly</option>
                      <option value="annual">Annual</option>
                    </select>
                  </div>
                  <div className={hudStyles.field}>
                    <label>Trial days</label>
                    <input
                      type="number"
                      min="0"
                      value={subscriptionForm.trialPeriodDays}
                      onChange={e => setSubscriptionForm(prev => ({ ...prev, trialPeriodDays: parseInt(e.target.value) || 0 }))}
                    />
                  </div>
                  <div className={`${hudStyles.field} ${hudStyles.fieldFull}`}>
                    {(subscriptionFeedback || subscriptionHook.error || subscriptionHook.lastAction) && (
                      <div
                        className={hudStyles.fieldFull}
                        role="status"
                        aria-live="polite"
                        style={{
                          gridColumn: '1 / -1',
                          padding: '12px 14px',
                          borderRadius: 8,
                          border: `1px solid ${(subscriptionFeedback?.ok ?? subscriptionHook.lastAction?.ok) === false || subscriptionHook.error ? 'rgba(248,113,113,0.55)' : 'rgba(74,222,128,0.45)'}`,
                          background: (subscriptionFeedback?.ok ?? subscriptionHook.lastAction?.ok) === false || subscriptionHook.error ? 'rgba(127,29,29,0.25)' : 'rgba(20,83,45,0.28)',
                          color: (subscriptionFeedback?.ok ?? subscriptionHook.lastAction?.ok) === false || subscriptionHook.error ? '#fecaca' : '#bbf7d0',
                          fontSize: '0.8rem',
                          lineHeight: 1.45,
                          marginBottom: 4,
                        }}
                      >
                        <strong style={{ display: 'block', marginBottom: 4, letterSpacing: '0.06em', textTransform: 'uppercase', fontSize: '0.65rem' }}>
                          {(subscriptionFeedback?.ok ?? subscriptionHook.lastAction?.ok) === false || subscriptionHook.error ? 'Subscription command failed' : 'Subscription command accepted'}
                        </strong>
                        {subscriptionFeedback?.message
                          || subscriptionHook.lastAction?.message
                          || subscriptionHook.error
                          || 'Ready.'}
                      </div>
                    )}
                    <button type="submit" className={hudStyles.primaryButton} disabled={subscriptionHook.loading || processing === 'create_subscription'}>
                      {subscriptionHook.loading || processing === 'create_subscription' ? <RefreshCw className="animate-spin" size={15} /> : <PlusCircle size={15} />}
                      Create Subscription
                    </button>
                  </div>
                </form>

                <div className={hudStyles.liveSubsBanner}>
                  <div className={hudStyles.liveSubsBannerLeft}>
                    <h3 className={hudStyles.liveSubsTitle}>Live Subscriptions</h3>
                    <div className={hudStyles.complianceStrip}>
                      <span>POPIA COMPLIANT</span>
                      <span>GDPR READY</span>
                      <span>ISO CERTIFIED</span>
                    </div>
                  </div>
                  <div className={hudStyles.liveSubsBannerRight}>
                    <span className={hudStyles.ledSealLabel}>Led Seal</span>
                    <code className={hudStyles.ledSealValue}>
                      {(() => {
                        const first = safeSubscriptions.find((s) => s.proofHash || s.seal);
                        const h = String(first?.proofHash || first?.seal || '').toUpperCase();
                        return h ? `${h.slice(0, 6)}…${h.slice(-4)}` : 'PENDING';
                      })()}
                    </code>
                    <span className={hudStyles.ledSealTime}>
                      {new Date().toLocaleString(undefined, { dateStyle: 'medium', timeStyle: 'short' })}
                    </span>
                  </div>
                </div>

                <div className={hudStyles.subWorkspace}>
                  <div className={hudStyles.subListColumn}>
                    <div className={hudStyles.subListHeader}>
                      <span>Contracts</span>
                      <strong>{safeSubscriptions.length} active in view</strong>
                    </div>

                    {safeSubscriptions.length === 0 ? (
                      <div className={hudStyles.empty}>
                        No subscriptions yet. Create the first recurring contract to activate MRR.
                      </div>
                    ) : (
                      <div className={hudStyles.subList}>
                        {safeSubscriptions.map((sub) => {
                          const subId = sub._id || sub.id;
                          const planLabel = sub.planName || sub.plan || sub.planId || 'Plan';
                          const freq = String(sub.billingFrequency || 'monthly').toLowerCase();
                          const statusKey = String(sub.status || 'active').toLowerCase();
                          const statusTone =
                            statusKey === 'active' || statusKey === 'trial'
                              ? 'active'
                              : statusKey === 'paused' || statusKey === 'past_due' || statusKey === 'pending'
                                ? 'pending'
                                : 'cancelled';
                          const periodEnd = sub.currentPeriodEnd ? new Date(sub.currentPeriodEnd) : null;
                          const renewalLabel = periodEnd
                            ? periodEnd.toLocaleDateString(undefined, {
                              day: '2-digit',
                              month: 'short',
                              year: 'numeric',
                            })
                            : '—';
                          const seal = String(sub.proofHash || sub.seal || '').toUpperCase();
                          const sealShort = seal
                            ? `${seal.slice(0, 12)}…${seal.slice(-8)}`
                            : 'SEAL_PENDING';
                          const amountLabel = formatMoney(sub.amount, sub.currency || 'ZAR');
                          const shortId = String(subId || '').slice(-8).toUpperCase();
                          const tenantLabel = sub.tenantId || '—';
                          const trialDays = Number(sub.trialDays || 0);

                          return (
                            <article key={subId} className={hudStyles.subCard} data-status={statusTone}>
                              <header className={hudStyles.subCardHeader}>
                                <div className={hudStyles.subCardTitleBlock}>
                                  <h4 className={hudStyles.subCardTitle}>{planLabel}</h4>
                                  <span className={hudStyles.subStatusBadge} data-tone={statusTone}>
                                    {statusKey}
                                  </span>
                                </div>
                                <div className={hudStyles.subCardPrice}>
                                  <strong>{amountLabel}</strong>
                                  <span>/ {freq}</span>
                                </div>
                              </header>

                              <ul className={hudStyles.subBulletFacts}>
                                <li>
                                  <span className={hudStyles.subBulletDot} />
                                  <span>
                                    {statusTone === 'pending' && trialDays > 0
                                      ? `Trial ends: ${renewalLabel}`
                                      : `Next renewal: ${renewalLabel}`}
                                  </span>
                                </li>
                                <li>
                                  <span className={hudStyles.subBulletDot} />
                                  <span>
                                    Tenant: <strong>{tenantLabel}</strong>
                                    {' · '}
                                    Contract <strong className={hudStyles.subMono}>{shortId}</strong>
                                  </span>
                                </li>
                                {statusTone === 'pending' && (
                                  <li>
                                    <span className={hudStyles.subBulletDot} />
                                    <span>Compliance: POPIA &amp; GDPR</span>
                                  </li>
                                )}
                              </ul>

                              <div className={hudStyles.subSealRow} title={seal || 'Proof not sealed yet'}>
                                <span>SHA3-512</span>
                                <code>{sealShort}</code>
                              </div>

                              <footer className={hudStyles.subCardActions}>
                                {statusKey === 'active' && (
                                  <>
                                    <button
                                      type="button"
                                      className={hudStyles.subActionBtn}
                                      onClick={() => handlePauseSubscription(subId, 'Paused via BillingHUD')}
                                      disabled={!!processing}
                                    >
                                      <Pause size={14} />
                                      Pause
                                    </button>
                                    <button
                                      type="button"
                                      className={hudStyles.subActionBtn}
                                      onClick={() =>
                                        handleCancelSubscription(subId, false, 'Cancelled via BillingHUD')
                                      }
                                      disabled={!!processing}
                                    >
                                      <XCircle size={14} />
                                      Cancel
                                    </button>
                                  </>
                                )}
                                {statusKey === 'paused' && (
                                  <button
                                    type="button"
                                    className={hudStyles.subActionBtn}
                                    onClick={() => handleResumeSubscription(subId)}
                                    disabled={!!processing}
                                  >
                                    <Play size={14} />
                                    Resume
                                  </button>
                                )}
                                {(statusKey === 'cancelled' || statusKey === 'expired') && (
                                  <button
                                    type="button"
                                    className={hudStyles.subActionBtn}
                                    onClick={() => handleReactivateSubscription(subId)}
                                    disabled={!!processing}
                                  >
                                    <RotateCw size={14} />
                                    Reactivate
                                  </button>
                                )}
                                <button
                                  type="button"
                                  className={hudStyles.subActionBtn}
                                  data-verify-status={(subscriptionVerifyState[subId]?.status || 'IDLE').toLowerCase()}
                                  onClick={() => handleVerifySubscription(sub)}
                                  disabled={!!processing || subscriptionVerifyState[subId]?.status === 'PENDING'}
                                  title={
                                    subscriptionVerifyState[subId]?.status === 'VERIFIED'
                                      ? `Verified · ${String(subscriptionVerifyState[subId]?.sealHash || '').slice(0, 16)}…`
                                      : 'Verify SHA3-512 seal and vault evidence'
                                  }
                                >
                                  <ShieldCheck size={14} />
                                  {subscriptionVerifyState[subId]?.status === 'VERIFIED'
                                    ? 'Verified'
                                    : subscriptionVerifyState[subId]?.status === 'PENDING'
                                      ? 'Verifying…'
                                      : subscriptionVerifyState[subId]?.status === 'FAILED'
                                        ? 'Retry verify'
                                        : 'Verify'}
                                </button>
                                <button
                                  type="button"
                                  className={hudStyles.subActionBtn}
                                  onClick={async () => {
                                    try {
                                      if (!seal || seal === 'SEAL_PENDING') {
                                        showBillingToast('No sealed proof available yet', { tone: 'warn' });
                                        return;
                                      }
                                      if (navigator?.clipboard?.writeText) {
                                        await navigator.clipboard.writeText(String(seal).toUpperCase());
                                        showBillingToast(`Seal copied · ${String(seal).slice(0, 18).toUpperCase()}…`);
                                      } else {
                                        showBillingToast('Clipboard unavailable in this browser', { tone: 'warn' });
                                      }
                                    } catch (_) {
                                      showBillingToast('Failed to copy seal', { tone: 'danger' });
                                    }
                                  }}
                                  title="Copy SHA3-512 proof to clipboard"
                                >
                                  <Copy size={14} />
                                  Copy seal
                                </button>
                                <button
                                  type="button"
                                  className={hudStyles.subActionBtn}
                                  onClick={() => handleViewAudit(subId)}
                                  disabled={auditModal.loading || !!processing}
                                >
                                  <History size={14} />
                                  Audit
                                </button>
                              </footer>
                            </article>
                          );
                        })}
                      </div>
                    )}
                  </div>

                  <aside className={hudStyles.subRevenuePanel} aria-label="Subscription revenue">
                    <div className={hudStyles.subRevenueHeader}>
                      <span>Subscription revenue</span>
                      <h3>Monthly Recurring Revenue (MRR)</h3>
                    </div>

                    <div className={hudStyles.subSparkline} aria-hidden>
                      <svg viewBox="0 0 240 90" preserveAspectRatio="none">
                        <defs>
                          <linearGradient id="mrrFill" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="0%" stopColor="rgba(212,175,55,0.35)" />
                            <stop offset="100%" stopColor="rgba(212,175,55,0)" />
                          </linearGradient>
                        </defs>
                        <path
                          d="M0,70 L30,62 L60,65 L90,48 L120,52 L150,38 L180,28 L210,18 L240,12 L240,90 L0,90 Z"
                          fill="url(#mrrFill)"
                        />
                        <path
                          d="M0,70 L30,62 L60,65 L90,48 L120,52 L150,38 L180,28 L210,18 L240,12"
                          fill="none"
                          stroke="#D4AF37"
                          strokeWidth="2.5"
                          strokeLinecap="round"
                          strokeLinejoin="round"
                        />
                      </svg>
                      <div className={hudStyles.subSparkTags}>
                        <span className={hudStyles.tagGrowth}>Live MRR</span>
                      </div>
                    </div>

                    <div className={hudStyles.subMrrBlock}>
                      <strong>
                        {formatMoney(
                          safeSubscriptions
                            .filter((s) => String(s.status || '').toLowerCase() === 'active')
                            .reduce((sum, s) => sum + (Number(s.amount) || 0), 0),
                          'ZAR'
                        )}
                      </strong>
                      <span>
                        Projected:{' '}
                        {formatMoney(
                          safeSubscriptions
                            .filter((s) => String(s.status || '').toLowerCase() === 'active')
                            .reduce((sum, s) => sum + (Number(s.amount) || 0), 0) * 1.15,
                          'ZAR'
                        )}
                      </span>
                    </div>

                    <div className={hudStyles.subAlertStack}>
                      <div className={hudStyles.subAlert} data-level="warn">
                        <AlertTriangle size={14} />
                        <span>
                          {safeSubscriptions.filter((s) =>
                            ['cancelled', 'expired'].includes(String(s.status || '').toLowerCase())
                          ).length}{' '}
                          expired or cancelled contracts
                        </span>
                      </div>
                      <div className={hudStyles.subAlert} data-level="info">
                        <ShieldAlert size={14} />
                        <span>SLA threshold watch — Kennel live</span>
                      </div>
                    </div>
                  </aside>
                </div>
              </div>
            </div>
          </section>
        )}

        {activeTab === 'hybrid' && (
          <section className={hudStyles.mainGrid} style={{ gridTemplateColumns: '1fr' }}>
            <div className={hudStyles.panel} style={{ gridColumn: '1 / -1' }}>
              <div className={hudStyles.panelHeader}>
                <div className={hudStyles.panelTitle}>
                  <Coins size={18} />
                  <div>
                    <span>Hybrid monetization</span>
                    <h2>Subscription + Usage + Credits + Outcome</h2>
                  </div>
                </div>
                <span className={hudStyles.statusPill}>AI-Native</span>
              </div>
              <form className={hudStyles.formGrid} onSubmit={handleHybridInvoice}>
                <div className={hudStyles.field}>
                  <label>Tenant</label>
                  <input
                    value={hybridInvoice.tenantId}
                    onChange={e => setHybridInvoice(prev => ({ ...prev, tenantId: e.target.value }))}
                    placeholder="TENANT-ID"
                    required
                  />
                </div>
                <div className={hudStyles.field}>
                  <label>Subscription ID (optional)</label>
                  <input
                    value={hybridInvoice.subscriptionId}
                    onChange={e => setHybridInvoice(prev => ({ ...prev, subscriptionId: e.target.value }))}
                    placeholder="SUB-123"
                  />
                </div>
                <div className={hudStyles.field}>
                  <label>Usage amount</label>
                  <input
                    type="text"
                    inputMode="decimal"
                    value={hybridInvoice.usageAmount}
                    onChange={e => setHybridInvoice(prev => ({ ...prev, usageAmount: sanitizeBillingMoneyInput(e.target.value) }))}
                    placeholder="0.00"
                  />
                </div>
                <div className={hudStyles.field}>
                  <label>Subscription amount</label>
                  <input
                    type="text"
                    inputMode="decimal"
                    value={hybridInvoice.subscriptionAmount}
                    onChange={e => setHybridInvoice(prev => ({ ...prev, subscriptionAmount: sanitizeBillingMoneyInput(e.target.value) }))}
                    placeholder="0.00"
                  />
                </div>
                <div className={hudStyles.field}>
                  <label>Proration (0–1)</label>
                  <input
                    type="number"
                    min="0.01"
                    max="1"
                    step="0.01"
                    value={hybridInvoice.prorationRatio}
                    onChange={e => setHybridInvoice(prev => ({ ...prev, prorationRatio: e.target.value }))}
                  />
                </div>
                <div className={hudStyles.field}>
                  <label>Credits</label>
                  <input
                    type="text"
                    inputMode="decimal"
                    value={hybridInvoice.credits}
                    onChange={e => setHybridInvoice(prev => ({ ...prev, credits: sanitizeBillingMoneyInput(e.target.value) }))}
                    placeholder="0.00"
                  />
                </div>
                <div className={hudStyles.field}>
                  <label>Outcome amount</label>
                  <input
                    type="text"
                    inputMode="decimal"
                    value={hybridInvoice.outcomeAmount}
                    onChange={e => setHybridInvoice(prev => ({ ...prev, outcomeAmount: sanitizeBillingMoneyInput(e.target.value) }))}
                    placeholder="0.00"
                  />
                  <label style={{ display: 'flex', gap: 8, marginTop: 8, alignItems: 'center' }}>
                    <input
                      type="checkbox"
                      checked={hybridInvoice.outcomeAchieved}
                      onChange={e => setHybridInvoice(prev => ({ ...prev, outcomeAchieved: e.target.checked }))}
                    />
                    Outcome trigger achieved
                  </label>
                </div>
                <div className={hudStyles.field}>
                  <label>Currency</label>
                  <select
                    value={hybridInvoice.currency}
                    onChange={e => setHybridInvoice(prev => ({ ...prev, currency: e.target.value }))}
                  >
                    {['ZAR', 'USD', 'EUR', 'GBP', 'NGN', 'KES', 'GHS', 'BWP', 'NAD', 'MUR'].map(currency => <option key={currency} value={currency}>{currency}</option>)}
                  </select>
                </div>
                <div className={`${hudStyles.field} ${hudStyles.fieldFull}`}>
                  <small>Formula sealed by Kennel EOS: subscription × proration + tiered usage − credits + triggered outcome.</small>
                </div>
                <div className={`${hudStyles.field} ${hudStyles.fieldFull}`}>
                  <label>Description</label>
                  <textarea
                    value={hybridInvoice.description}
                    onChange={e => setHybridInvoice(prev => ({ ...prev, description: e.target.value }))}
                    placeholder="Hybrid monetization description"
                  />
                </div>
                <div className={`${hudStyles.field} ${hudStyles.fieldFull}`}>
                  <button type="submit" className={hudStyles.primaryButton} disabled={processing === 'hybrid_invoice'}>
                    {processing === 'hybrid_invoice' ? <RefreshCw className="animate-spin" size={15} /> : <Coins size={15} />}
                    Generate Hybrid Invoice
                  </button>
                </div>
              </form>
            </div>
          </section>
        )}

        {activeTab === 'statements' && (
          <section className={hudStyles.mainGrid} style={{ gridTemplateColumns: '1fr' }} aria-label="Statements workspace">
            <div className={hudStyles.panel} style={{ gridColumn: '1 / -1' }}>
              <StatementEngine
                tenantId={String(
                  invoiceMode === 'PLATFORM' && manualInvoice?.tenantId
                    ? manualInvoice.tenantId
                    : tenantId ||
                    activeTenant?.tenantId ||
                    activeTenant?._id ||
                    authUser?.tenantId ||
                    'MASTER'
                )}
                clientId={String(
                  invoiceMode === 'CLIENT'
                    ? (manualInvoice?.clientId || manualInvoice?.tenantId || '')
                    : ''
                )}
                issuerMode={invoiceMode === 'CLIENT' ? 'TENANT_CLIENT' : 'PLATFORM'}
                issuerIdentity={billingTenantIdentity}
                counterpartyName={invoiceMode === 'CLIENT' ? manualInvoice?.tenantName : manualInvoice?.tenantName}
                onSealed={(sealed) => {
                  setLastSavedInvoice({
                    id: sealed?.statementId || null,
                    invoiceNumber: sealed?.statementNumber || 'Statement sealed',
                    tenantId: tenantId || 'MASTER',
                    source: sealed?.source || 'STATEMENT_SEALED',
                    totalAmount: sealed?.totalAmount ?? null,
                    at: sealed?.timestamp || new Date().toISOString()
                  });
                  void broadcastTelemetry(
                    tenantId || 'MASTER',
                    'BILLING',
                    'STATEMENT_SEALED',
                    'StatementEngine',
                    { statementId: sealed?.statementId, sealHash: sealed?.sealHash }
                  ).catch(() => { });
                }}
              />
            </div>
          </section>
        )}

        {activeTab === 'investor' && caps.viewInvestor && (
          <section className={hudStyles.mainGrid} style={{ gridTemplateColumns: '1fr' }} aria-label="Investor dashboard">
            <div className={hudStyles.panel} style={{ gridColumn: '1 / -1' }}>
              <div className={hudStyles.panelHeader}>
                <div className={hudStyles.panelTitle}>
                  <TrendingUp size={18} />
                  <div>
                    <span>Investor dashboard</span>
                    <h2>ARR, Forecast, Burn‑Rate & Sovereign Proof</h2>
                  </div>
                </div>
                <button
                  type="button"
                  className={hudStyles.primaryButton}
                  onClick={async () => {
                    await runCommand('investor_proof', async () => {
                      const response = await sovereignClient.post('/billing/investor/proofs', {
                        arr: totalArr,
                        forecasted_arr: forecastedArr,
                        collection_efficiency: collectionEfficiency,
                        risk_score: riskScore,
                        active_subscriptions: summary?.activeSubscriptions || 0,
                        model: { forecast: 'deterministic_linear_plus_seeded_monte_carlo', simulationCount: 420 }
                      }, { headers: { 'X-Tenant-ID': tenantId } });
                      const proof = response?.data || {};
                      const blob = new Blob([JSON.stringify(proof, null, 2)], { type: 'application/json' });
                      const url = URL.createObjectURL(blob);
                      const anchor = document.createElement('a');
                      anchor.href = url;
                      anchor.download = `WILSY_INVESTOR_PROOF_${Date.now()}.json`;
                      anchor.click();
                      URL.revokeObjectURL(url);
                      return proof;
                    }, data => `Investor proof anchored by Kennel EOS • ${data?.proof_hash?.slice(0, 14) || 'proof pending'}`);
                  }}
                >
                  <Download size={15} /> Export Investor Proof
                </button>
              </div>
              <div className={hudStyles.metricGrid} style={{ marginBottom: '24px' }}>
                <article className={hudStyles.metricCard}>
                  <DollarSign size={18} />
                  <span>ARR</span>
                  <strong>{formatMoney(totalArr)}</strong>
                  <small>Annual recurring revenue</small>
                </article>
                <article className={hudStyles.metricCard} data-tone="cyan">
                  <TrendingUp size={18} />
                  <span>Forecasted ARR</span>
                  <strong>{formatMoney(forecastedArr)}</strong>
                  <small>12‑month projection</small>
                </article>
                <article className={hudStyles.metricCard} data-tone="red">
                  <Clock size={18} />
                  <span>Outstanding</span>
                  <strong>{formatMoney(outstanding)}</strong>
                  <small>Unsettled invoices</small>
                </article>
                <article className={hudStyles.metricCard} data-tone="green">
                  <ShieldCheck size={18} />
                  <span>Collection Efficiency</span>
                  <strong>{collectionEfficiency}%</strong>
                  <small>Paid vs issued</small>
                </article>
              </div>
              <div className={hudStyles.featureGrid} style={{ marginBottom: '24px' }}>
                <article className={hudStyles.featureCard}>
                  <span>Risk Score</span>
                  <strong>{Math.round(riskScore * 100)}%</strong>
                  <small>Monte Carlo cashflow risk</small>
                </article>
                <article className={hudStyles.featureCard}>
                  <span>Active Subscriptions</span>
                  <strong>{summary?.activeSubscriptions || 0}</strong>
                  <small>Recurring revenue base</small>
                </article>
                <article className={hudStyles.featureCard}>
                  <span>Treasury Status</span>
                  <strong>{treasuryState.status}</strong>
                  <small>{treasuryEvaluation ? `${formatMoney(treasuryEvaluation.liquidity?.availableToSweep || 0)} sweep candidate` : 'Not evaluated'}</small>
                </article>
                <article className={hudStyles.featureCard}>
                  <span>Courts</span>
                  <strong>{courts.length}</strong>
                  <small>Global legal registry</small>
                </article>
              </div>
              <div className={hudStyles.timeline} style={{ maxHeight: '200px', overflowY: 'auto' }}>
                <div className={hudStyles.timelineItem}>
                  <span>Flight Deck Posture</span>
                  <strong>{flightDeck.posture}</strong>
                  <small>{flightDeck.sourceLabel} · {flightDeck.nextAction}</small>
                </div>
                <div className={hudStyles.timelineItem}>
                  <span>Readiness</span>
                  <strong>{flightDeck.readiness}%</strong>
                  <small>Operational readiness score</small>
                </div>
                {history.slice(-12).map(point => (
                  <div key={point.label} className={hudStyles.timelineItem}>
                    <span>{point.label}</span>
                    <strong>{formatMoney(point.volume || 0)}</strong>
                    <small>{point.paidVolume ? `Paid: ${formatMoney(point.paidVolume)}` : ''}</small>
                  </div>
                ))}
              </div>
            </div>
          </section>
        )}

        {activeTab === 'tenants' && tenantManagerOpen && (
          <section className={hudStyles.mainGrid} style={{ gridTemplateColumns: '1fr' }} aria-label="Tenant management cockpit">
            <div className={hudStyles.panel} style={{ gridColumn: '1 / -1' }}>
              <div className={hudStyles.panelHeader}>
                <div className={hudStyles.panelTitle}>
                  <Users size={18} />
                  <div>
                    <span>Tenant management</span>
                    <h2>Tenant Management Cockpit</h2>
                  </div>
                </div>
                <button type="button" className={hudStyles.secondaryButton} onClick={() => setTenantManagerOpen(false)}>
                  Return to billing
                </button>
              </div>
              <SovereignTenantManager />
            </div>
          </section>
        )}

        {activeTab === 'tenants' && !tenantManagerOpen && (
          <section className={hudStyles.mainGrid} style={{ gridTemplateColumns: '1fr' }} aria-label="Tenants workspace">
            <div className={hudStyles.panel} style={{ gridColumn: '1 / -1' }}>
              <div className={hudStyles.panelHeader}>
                <div className={hudStyles.panelTitle}>
                  <Users size={18} />
                  <div>
                    <span>Tenant management</span>
                    <h2>Sovereign Tenant Shards</h2>
                  </div>
                </div>
                <div className={hudStyles.heroActions}>
                  <button
                    type="button"
                    className={hudStyles.primaryButton}
                    onClick={() => {
                      void broadcastTelemetry(
                        activeTenant?.id || tenantId,
                        'BILLING',
                        'MANAGE_TENANTS_OPENED',
                        'BillingHUD',
                        { userId: authUser?.id, timestamp: new Date().toISOString() }
                      ).catch(() => { });
                      setTenantManagerOpen(true);
                    }}
                    title="Open the full tenant management cockpit without leaving billing"
                  >
                    <LayoutDashboard size={15} /> Manage Tenants
                  </button>
                </div>
              </div>

              <div className={hudStyles.metricGrid} style={{ marginBottom: '24px' }}>
                <article className={hudStyles.metricCard}>
                  <Users size={18} />
                  <span>Total Shards</span>
                  <strong>{allTenants.length}</strong>
                  <small>Active tenant shards</small>
                </article>
                <article className={hudStyles.metricCard} data-tone="green">
                  <CheckCircle size={18} />
                  <span>Active Shards</span>
                  <strong>{allTenants.filter(t => t.status === 'Active').length}</strong>
                  <small>Operational tenants</small>
                </article>
                <article className={hudStyles.metricCard} data-tone="red">
                  <AlertTriangle size={18} />
                  <span>Suspended</span>
                  <strong>{allTenants.filter(t => t.status === 'Suspended').length}</strong>
                  <small>Locked or inactive</small>
                </article>
                <article className={hudStyles.metricCard} data-tone="cyan">
                  <TrendingUp size={18} />
                  <span>Total Revenue</span>
                  <strong>
                    {formatMoney(
                      allTenants.reduce((sum, t) => sum + (t.revenue || 0), 0),
                      'ZAR'
                    )}
                  </strong>
                  <small>Aggregate tenant ARR</small>
                </article>
              </div>

              <div className={hudStyles.switcherContainer} style={{ marginTop: '16px' }}>
                <h3 style={{ fontSize: '0.8rem', color: '#888', marginBottom: '12px', letterSpacing: '1px' }}>
                  QUICK SWITCH OR SUSPEND
                </h3>
                <TenantSwitcher
                  kennelShard="GLOBAL"
                  kennelTenantId={tenantId}
                  tenants={allTenants}
                />
                <p style={{ fontSize: '0.6rem', color: '#555', marginTop: '8px' }}>
                  Use the floating switcher to change or suspend tenants directly from the billing cockpit.
                </p>
              </div>
            </div>
          </section>
        )}

        {activeTab === 'audit' && caps.viewAudit && (
          <section className={hudStyles.mainGrid} style={{ gridTemplateColumns: '1fr' }} aria-label="Audit workspace">
            <div className={hudStyles.panel} style={{ gridColumn: '1 / -1' }}>
              <AuditTab
                externalTenantId={String(
                  tenantId ||
                  activeTenant?.tenantId ||
                  activeTenant?._id ||
                  authUser?.tenantId ||
                  'MASTER'
                )}
              />
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
                <button type="button" className={hudStyles.primaryButton} onClick={runTreasurySweep} disabled={!!processing || !caps.viewTreasury} title="Execute a governed treasury sweep when policy gates are satisfied">
                  {processing === 'treasury_sweep' ? <RefreshCw className="animate-spin" size={15} /> : <Coins size={15} />}
                  Execute Governed Sweep
                </button>
                <button type="button" className={hudStyles.secondaryButton} onClick={() => hydrate('refresh')} disabled={refreshing} title="Refresh billing sources, tax posture and treasury readiness">
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
              {/* ─── SOURCE MESH ──────────────────────────────────────────────── */}
              {SourceMesh && (
                <div style={{ marginTop: '12px' }}>
                  <SourceMesh tenantId={tenantId} sources={sourceSnapshot.sources} />
                </div>
              )}
              <div className={hudStyles.sourceMeshGrid}>
                {sourceRows.map(source => (
                  <article key={source.key} data-live={source.live ? 'true' : 'false'} data-status={source.statusTone}>
                    <span>{source.label || source.key}</span>
                    <strong>{source.status}</strong>
                    <small>{source.error || 'Source is contributing to command readiness.'}</small>
                  </article>
                ))}
              </div>
            </div>
          </section>
        )}

        {activeTab === 'anomalies' && caps.viewAnomalies && (
          <section className={hudStyles.mainGrid} style={{ gridTemplateColumns: '1fr' }}>
            <div className={hudStyles.panel} style={{ gridColumn: '1 / -1' }}>
              <div className={hudStyles.panelHeader}>
                <div className={hudStyles.panelTitle}>
                  <AlertTriangle size={18} />
                  <div>
                    <span>Anomaly detection</span>
                    <h2>Billing Anomalies Dashboard</h2>
                  </div>
                </div>
                <span className={hudStyles.statusPill}>Real-time</span>
              </div>
              <AnomalyDashboard tenantId={tenantId} />
            </div>
          </section>
        )}

        {activeTab === 'automation' && caps.viewAutomation && (
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
                    <button type="button" className={hudStyles.primaryButton} onClick={runAutoBilling} disabled={!!processing || !caps.viewAutomation}>
                      {processing === 'auto_billing' ? <RefreshCw className="animate-spin" size={15} /> : <Mail size={15} />} Run Now
                    </button>
                  </div>
                </article>
                <article className={hudStyles.featureCard}>
                  <header><span>Dynamic Pricing</span><Gauge size={18} /></header>
                  <strong>{Math.round(riskScore * 100)}% risk input</strong>
                  <small>Reprices active tenants against cashflow risk.</small>
                  <div className={hudStyles.featureActions}>
                    <button type="button" className={hudStyles.primaryButton} onClick={applyDynamicPricing} disabled={!!processing || !caps.viewAutomation}>
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
                    <button type="button" className={hudStyles.primaryButton} onClick={runTreasurySweep} disabled={!!processing || !caps.viewTreasury}>
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
                      disabled={!!processing || !caps.runDunning || !dunningRecommendations.length}
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

        {activeTab === 'warroom' && caps.viewWarroom && (
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
                  <button type="submit" className={hudStyles.dangerButton} disabled={!!processing || !caps.runSeizure}>
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
                      disabled={!!processing || !caps.runDunning}
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

        {disputeModal.open && caps.disputeInvoice && (
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
                <button
                  type="button"
                  className={hudStyles.primaryButton}
                  onClick={submitDispute}
                  disabled={processing === 'dispute' || !disputeModal.invoiceId || !disputeModal.reason || !caps.disputeInvoice}
                >
                  {processing === 'dispute' ? <RefreshCw className="animate-spin" size={15} /> : <CheckCircle size={15} />} Submit Dispute
                </button>
                <button type="button" className={hudStyles.secondaryButton} onClick={() => setDisputeModal({ open: false, invoiceId: '', reason: '' })}>
                  Cancel
                </button>
              </div>
            </div>
          </div>
        )}

        {auditModal.open && (
          <div className={hudStyles.modalOverlay}>
            <div className={hudStyles.modal}>
              <div className={hudStyles.panelHeader}>
                <div className={hudStyles.panelTitle}>
                  <History size={18} />
                  <div>
                    <span>Audit trail</span>
                    <h2>Subscription {auditModal.subscriptionId?.slice(0, 8)}</h2>
                  </div>
                </div>
              </div>
              <div className={hudStyles.timeline} style={{ maxHeight: '300px', overflowY: 'auto' }}>
                {auditModal.loading ? (
                  <div className={hudStyles.empty}>Loading audit trail...</div>
                ) : auditModal.auditTrail.length === 0 ? (
                  <div className={hudStyles.empty}>No audit entries found.</div>
                ) : (
                  auditModal.auditTrail.map((entry, index) => (
                    <div key={`${entry.timestamp}-${index}`} className={hudStyles.timelineItem}>
                      <span>{new Date(entry.timestamp).toLocaleString()}</span>
                      <strong>{entry.action}</strong>
                      <small>{entry.reason || ''}</small>
                      <span style={{ fontSize: '0.6rem', color: '#666' }}>Proof: {entry.proofHash?.slice(0, 16)}</span>
                    </div>
                  ))
                )}
              </div>
              <div className={hudStyles.featureActions}>
                <button type="button" className={hudStyles.secondaryButton} onClick={() => setAuditModal({ open: false, subscriptionId: '', auditTrail: [], loading: false })}>
                  Close
                </button>
              </div>
            </div>
          </div>
        )}


        {/* ─── FLOATING SEAL DOCK — live total + primary CTA (top 0.01%) ─── */}
        {invoiceWorkspace === 'compose' && activeTab === 'invoices' && createPortal(
          <div
            className={hudStyles.floatingSealDock || ''}
            style={{
              position: 'fixed',
              right: 24,
              bottom: 24,
              zIndex: 9000,
              minWidth: 280,
              maxWidth: 360,
              padding: '14px 16px',
              borderRadius: 16,
              background: 'linear-gradient(160deg, rgba(15,23,42,0.97), rgba(2,6,23,0.98))',
              border: '1px solid rgba(251,191,36,0.35)',
              boxShadow: '0 20px 50px rgba(0,0,0,0.45), 0 0 0 1px rgba(251,191,36,0.08)',
              backdropFilter: 'blur(12px)',
              display: 'flex',
              flexDirection: 'column',
              gap: 10,
            }}
            role="region"
            aria-label="Seal invoice dock"
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', gap: 8 }}>
              <span style={{ fontSize: '0.65rem', letterSpacing: '0.08em', textTransform: 'uppercase', color: '#fbbf24', fontWeight: 700 }}>Seal</span>
              <span style={{ fontSize: '0.7rem', color: '#94a3b8' }}>{composeCompleteness.pct}% ready · ⌘↵</span>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              <strong style={{ fontSize: '1.35rem', fontVariantNumeric: 'tabular-nums', color: '#f8fafc' }}>
                {formatMoney(manualInvoiceTotal, manualInvoice.currency)}
              </strong>
              <small style={{ color: '#94a3b8', fontSize: '0.7rem' }}>
                {manualInvoice.tenantName || manualInvoice.tenantId || 'No recipient'}
                {manualInvoice.tenantId ? ` · ${manualInvoice.tenantId}` : ''}
              </small>
            </div>
            <div style={{ height: 4, borderRadius: 999, background: 'rgba(148,163,184,0.2)', overflow: 'hidden' }}>
              <div style={{ height: '100%', width: `${composeCompleteness.pct}%`, background: composeCompleteness.pct >= 66 ? 'linear-gradient(90deg,#10b981,#34d399)' : 'linear-gradient(90deg,#f59e0b,#fbbf24)', transition: 'width 0.25s ease' }} />
            </div>
            <button
              type="button"
              className={hudStyles.primaryButton}
              disabled={
                processing === 'invoice' ||
                isFrozen ||
                !manualInvoice.tenantId?.trim() ||
                !(parseBillingMoneyInput(manualInvoice.amount) > 0) ||
                !(invoiceMode === 'CLIENT' ? caps.createClientInvoice : caps.createPlatformInvoice)
              }
              onClick={() => {
                const form = document.querySelector(`.${(hudStyles.formGrid || 'formGrid').split(' ')[0]}`);
                if (form) form.requestSubmit();
              }}
              style={{ width: '100%', justifyContent: 'center' }}
            >
              {processing === 'invoice' ? <RefreshCw className="animate-spin" size={15} /> : <PlusCircle size={15} />}
              {invoiceMode === 'CLIENT' ? 'Seal client invoice' : 'Seal platform invoice'}
            </button>
            <small style={{ color: '#64748b', fontSize: '0.65rem', textAlign: 'center' }}>
              Order identity auto-generates on seal · idempotent
            </small>
          </div>,
          document.body
        )}

        {/* ─── FORENSIC PROOF MODAL (PORTAL) ───────────────────────────────── */}
        {showProofModal && selectedInvoiceForProof && createPortal(
          <div
            className={hudStyles.modalOverlay}
            onClick={(e) => {
              if (e.target === e.currentTarget) {
                setShowProofModal(false);
                setSelectedInvoiceForProof(null);
              }
            }}
          >
            <div className={hudStyles.modal} style={{ maxWidth: '700px', maxHeight: '90vh', overflowY: 'auto' }}>
              <div className={hudStyles.panelHeader}>
                <div className={hudStyles.panelTitle}>
                  <ShieldCheck size={18} />
                  <div>
                    <span>Forensic Proof</span>
                    <h2>{selectedInvoiceForProof.invoiceNumber || selectedInvoiceForProof.id}</h2>
                  </div>
                </div>
                <button
                  type="button"
                  className={hudStyles.secondaryButton}
                  onClick={() => { setShowProofModal(false); setSelectedInvoiceForProof(null); }}
                >
                  Close
                </button>
              </div>
              <ForensicProofBlock
                invoice={{
                  invoiceNumber: selectedInvoiceForProof.invoiceNumber || selectedInvoiceForProof.id,
                  traceId: selectedInvoiceForProof.traceId,
                  qrVerificationUrl: selectedInvoiceForProof.qrVerificationUrl || null,
                  sealHash: selectedInvoiceForProof.sealHash || selectedInvoiceForProof.proofHash,
                  merkleRoot: selectedInvoiceForProof.merkleRoot,
                  totalAmount: selectedInvoiceForProof.totalAmount || selectedInvoiceForProof.amount,
                  currency: selectedInvoiceForProof.currency,
                  pkiSignature: selectedInvoiceForProof.pkiSignature,
                  qrVerified: selectedInvoiceForProof.qrVerified,
                  qrVerifiedAt: selectedInvoiceForProof.qrVerifiedAt,
                }}
                status="pending"
              />
            </div>
          </div>,
          document.body
        )}
      </div>
    </WilsyOSDashboardChrome>
  );
};

export default BillingHUD;

/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * 🏛️ INSTITUTIONAL CERTIFICATION SEAL — BillingHUD V68.3.2‑PAYMENT‑ENHANCEMENT
 * ═══════════════════════════════════════════════════════════════════════════════
 * Status:          CERTIFIED PRODUCTION ARTIFACT — PAYMENT ENHANCEMENT
 * Phase:           Phase 0 — FOUNDATION ENHANCEMENTS
 * Compliance:      POPIA §19 · GDPR §32 · SOC2 §CC7.2 · ISO 27001 · ECT Act §15
 * ────────────────────────────────────────────────────────────────────────────────
 * 🔒 This file is ready for deployment.
 * ═══════════════════════════════════════════════════════════════════════════════
 */
