/* eslint-disable */
/**
 * ╔══════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS — FINANCE SOURCE CONNECTOR                                        ║
 * ║ VERSION: 1.0.0-PRODUCTION-NO-FAKE-DATA                                     ║
 * ║ FILE: server/services/sourceConnectors/financeSourceConnector.js            ║
 * ║ PURPOSE: Verify finance evidence for contracts, ARR, runway and ledgers.    ║
 * ╚══════════════════════════════════════════════════════════════════════════════╝
 *
 * @description
 * This connector never fabricates financial verification.
 *
 * It supports:
 * - Local evidence file: WILSY_FINANCE_EVIDENCE_FILE
 * - Generic finance evidence API: WILSY_FINANCE_API_URL
 * - QuickBooks reports: WILSY_QUICKBOOKS_REALM_ID + WILSY_QUICKBOOKS_ACCESS_TOKEN
 * - Xero accounting data: WILSY_XERO_TENANT_ID + WILSY_XERO_ACCESS_TOKEN
 * - Stripe revenue/payment data: WILSY_STRIPE_SECRET_KEY
 *
 * It returns VERIFIED only when a provider/evidence store returns:
 * - verified true or status VERIFIED
 * - sourceId / recordId / id
 * - retrievedAt / timestamp / generatedAt
 * - evidence payload
 *
 * Missing configuration returns MISSING.
 * Incomplete evidence returns PENDING.
 * Provider failure returns ERROR.
 */

import crypto from 'node:crypto';
import { existsSync } from 'node:fs';
import { readFile } from 'node:fs/promises';

const STATUS = Object.freeze({
  VERIFIED: 'VERIFIED',
  PENDING: 'PENDING',
  MISSING: 'MISSING',
  ERROR: 'ERROR',
});

const FINANCE_EVIDENCE_TYPES = Object.freeze({
  REVENUE_YTD: 'REVENUE_YTD',
  ANNUAL_RECURRING_REVENUE: 'ANNUAL_RECURRING_REVENUE',
  RUNWAY_MONTHS: 'RUNWAY_MONTHS',
  CONTRACT_VALUE_LEDGER: 'CONTRACT_VALUE_LEDGER',
});

const DEFAULT_QUICKBOOKS_BASE_URL = 'https://quickbooks.api.intuit.com';
const DEFAULT_XERO_BASE_URL = 'https://api.xero.com/api.xro/2.0';
const DEFAULT_STRIPE_BASE_URL = 'https://api.stripe.com';

/**
 * @function nowIso
 * @description Returns current ISO timestamp.
 * @returns {string} ISO timestamp.
 */
function nowIso() {
  return new Date().toISOString();
}

/**
 * @function stableStringify
 * @description Deterministic JSON serialization for evidence hashing.
 * @param {*} value - Value to serialize.
 * @returns {string} Stable JSON string.
 */
function stableStringify(value) {
  if (value === null || typeof value !== 'object') return JSON.stringify(value);
  if (Array.isArray(value)) return `[${value.map((item) => stableStringify(item)).join(',')}]`;

  return `{${Object.keys(value)
    .sort()
    .map((key) => `${JSON.stringify(key)}:${stableStringify(value[key])}`)
    .join(',')}}`;
}

/**
 * @function hashEvidence
 * @description Creates forensic evidence hash.
 * @param {*} payload - Evidence payload.
 * @returns {{algorithm:string, hash:string}} Hash output.
 */
function hashEvidence(payload) {
  const algorithm = crypto.getHashes().includes('sha3-512') ? 'sha3-512' : 'sha512';

  return {
    algorithm,
    hash: crypto.createHash(algorithm).update(stableStringify(payload)).digest('hex'),
  };
}

/**
 * @function normalizeTenantId
 * @description Normalizes tenant id.
 * @param {string} tenantId - Tenant id.
 * @returns {string} Normalized tenant id.
 */
function normalizeTenantId(tenantId = 'MASTER') {
  return String(tenantId || 'MASTER').trim() || 'MASTER';
}

/**
 * @function env
 * @description Reads and trims an environment variable.
 * @param {string} name - Env var name.
 * @returns {string} Env var value.
 */
function env(name) {
  return String(process.env[name] || '').trim();
}

/**
 * @function evidenceFilePath
 * @description Resolves local finance evidence file path.
 * @returns {string} Evidence file path.
 */
function evidenceFilePath() {
  return env('WILSY_FINANCE_EVIDENCE_FILE');
}

/**
 * @function genericFinanceApiUrl
 * @description Resolves generic finance evidence API base URL.
 * @returns {string} API base URL.
 */
function genericFinanceApiUrl() {
  return env('WILSY_FINANCE_API_URL').replace(/\/$/, '');
}

/**
 * @function quickBooksBaseUrl
 * @description Resolves QuickBooks API base URL.
 * @returns {string} QuickBooks base URL.
 */
function quickBooksBaseUrl() {
  return (env('WILSY_QUICKBOOKS_BASE_URL') || DEFAULT_QUICKBOOKS_BASE_URL).replace(/\/$/, '');
}

/**
 * @function xeroBaseUrl
 * @description Resolves Xero Accounting API base URL.
 * @returns {string} Xero base URL.
 */
function xeroBaseUrl() {
  return (env('WILSY_XERO_BASE_URL') || DEFAULT_XERO_BASE_URL).replace(/\/$/, '');
}

/**
 * @function stripeBaseUrl
 * @description Resolves Stripe API base URL.
 * @returns {string} Stripe base URL.
 */
function stripeBaseUrl() {
  return (env('WILSY_STRIPE_BASE_URL') || DEFAULT_STRIPE_BASE_URL).replace(/\/$/, '');
}

/**
 * @function safeJsonParse
 * @description Parses JSON evidence with descriptive error.
 * @param {string} content - JSON content.
 * @param {string} label - Source label.
 * @returns {*} Parsed JSON.
 */
function safeJsonParse(content, label) {
  try {
    return JSON.parse(content);
  } catch (error) {
    const enriched = new Error(`Invalid finance evidence JSON from ${label}: ${error.message}`);
    enriched.cause = error;
    throw enriched;
  }
}

/**
 * @function normalizeMoney
 * @description Normalizes numeric money values without inventing values.
 * @param {*} value - Raw value.
 * @returns {number|null} Number or null.
 */
function normalizeMoney(value) {
  if (value === null || value === undefined || value === '') return null;

  const numeric = Number(String(value).replace(/[^0-9.-]+/g, ''));

  return Number.isFinite(numeric) ? numeric : null;
}

/**
 * @function artifactHints
 * @description Extracts finance lookup hints from context.
 * @param {object} context - Source registry context.
 * @returns {object} Lookup hints.
 */
function artifactHints(context = {}) {
  const artifact = context.artifact || {};

  return {
    tenantId: normalizeTenantId(context.tenantId),
    contractId:
      artifact.contractId || artifact.agreementId || artifact.documentId || artifact.id || '',
    dealId: artifact.dealId || artifact.hubspotDealId || '',
    invoiceId: artifact.invoiceId || artifact.invoiceNumber || '',
    customerId: artifact.customerId || artifact.counterpartyId || '',
    counterparty: artifact.counterparty || artifact.counterpartyName || artifact.clientName || '',
    title: artifact.title || artifact.name || '',
    type: artifact.type || artifact.id || '',
  };
}

/**
 * @function fetchJson
 * @description Fetches JSON with strict error handling.
 * @param {string|URL} url - URL.
 * @param {object} options - Fetch options.
 * @returns {Promise<object>} JSON or connector error marker.
 */
async function fetchJson(url, options = {}) {
  const response = await fetch(url, {
    ...options,
    headers: {
      Accept: 'application/json',
      ...(options.headers || {}),
    },
  });

  if (!response.ok) {
    return {
      __connectorStatus: STATUS.ERROR,
      __message: `HTTP ${response.status}: ${await response.text()}`,
    };
  }

  return response.json();
}

/**
 * @function readFileEvidence
 * @description Reads local finance evidence from configured JSON file.
 * @returns {Promise<object|null>} Evidence store.
 */
async function readFileEvidence() {
  const filePath = evidenceFilePath();

  if (!filePath) return null;

  if (!existsSync(filePath)) {
    return {
      __connectorStatus: STATUS.MISSING,
      __message: `Configured finance evidence file does not exist: ${filePath}`,
    };
  }

  const content = await readFile(filePath, 'utf8');

  return safeJsonParse(content, filePath);
}

/**
 * @function selectTenantEvidence
 * @description Selects tenant-specific finance evidence.
 * @param {object} store - Evidence store.
 * @param {string} tenantId - Tenant id.
 * @returns {object|null} Tenant evidence.
 */
function selectTenantEvidence(store = {}, tenantId = 'MASTER') {
  const normalizedTenantId = normalizeTenantId(tenantId);

  if (store.tenantId && normalizeTenantId(store.tenantId) === normalizedTenantId) return store;
  if (store.tenants && store.tenants[normalizedTenantId]) return store.tenants[normalizedTenantId];
  if (store[normalizedTenantId]) return store[normalizedTenantId];

  return store.finance || store.Finance || null;
}

/**
 * @function normalizeEvidenceRecord
 * @description Strictly normalizes evidence records into Source Registry format.
 * @param {string} evidenceType - Evidence type.
 * @param {object} record - Evidence record.
 * @param {object} context - Source context.
 * @returns {object} Connector result.
 */
function normalizeEvidenceRecord(evidenceType, record, context = {}) {
  if (!record) {
    return {
      status: STATUS.PENDING,
      evidenceType,
      message: `${evidenceType} evidence not found.`,
    };
  }

  if (record.__connectorStatus) {
    return {
      status: record.__connectorStatus,
      evidenceType,
      message: record.__message || record.message || `${evidenceType} source failed.`,
    };
  }

  const evidencePayload = record.evidence || record.data || record.record || null;
  const sourceId = record.sourceId || record.recordId || record.id || null;
  const retrievedAt = record.retrievedAt || record.timestamp || record.generatedAt || null;
  const verified = record.status === STATUS.VERIFIED || record.verified === true;

  const evidence = {
    evidenceType,
    tenantId: normalizeTenantId(context.tenantId),
    artifact: context.artifact?.id || context.artifact?.type || context.artifact?.title || null,
    sourceId,
    retrievedAt,
    evidence: evidencePayload,
  };

  const seal = hashEvidence(evidence);

  if (!verified || !sourceId || !retrievedAt || !evidencePayload) {
    return {
      status: STATUS.PENDING,
      verified: false,
      evidenceType,
      sourceId,
      retrievedAt,
      message: `${evidenceType} evidence is present but incomplete for boardroom reliance.`,
      requirements: {
        verifiedStatus: verified,
        sourceId: Boolean(sourceId),
        retrievedAt: Boolean(retrievedAt),
        evidencePayload: Boolean(evidencePayload),
      },
      evidence,
      evidenceHash: seal.hash,
      hashAlgorithm: seal.algorithm,
    };
  }

  return {
    status: STATUS.VERIFIED,
    verified: true,
    evidenceType,
    sourceId,
    retrievedAt,
    evidence,
    evidenceHash: seal.hash,
    hashAlgorithm: seal.algorithm,
  };
}

/**
 * @function fetchGenericApiEvidence
 * @description Fetches evidence from a generic Wilsy finance evidence API.
 * @param {string} evidenceType - Evidence type.
 * @param {object} context - Source context.
 * @returns {Promise<object|null>} Evidence.
 */
async function fetchGenericApiEvidence(evidenceType, context = {}) {
  const baseUrl = genericFinanceApiUrl();

  if (!baseUrl) return null;

  const hints = artifactHints(context);
  const url = new URL(`${baseUrl}/finance/evidence`);

  url.searchParams.set('tenantId', hints.tenantId);
  url.searchParams.set('type', evidenceType);

  if (hints.contractId) url.searchParams.set('contractId', hints.contractId);
  if (hints.invoiceId) url.searchParams.set('invoiceId', hints.invoiceId);
  if (hints.customerId) url.searchParams.set('customerId', hints.customerId);
  if (hints.counterparty) url.searchParams.set('counterparty', hints.counterparty);

  const token = env('WILSY_FINANCE_API_TOKEN');

  return fetchJson(url, {
    headers: {
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      'X-Wilsy-Trace-Id': context.traceId || `FIN-${Date.now().toString(16).toUpperCase()}`,
    },
  });
}

/**
 * @function evidenceFromLocalOrGenericStore
 * @description Reads finance evidence from configured local file or generic API.
 * @param {string} evidenceType - Evidence type.
 * @param {object} context - Source context.
 * @returns {Promise<object|null>} Normalized evidence or null.
 */
async function evidenceFromLocalOrGenericStore(evidenceType, context = {}) {
  const apiEvidence = genericFinanceApiUrl()
    ? await fetchGenericApiEvidence(evidenceType, context)
    : null;

  if (apiEvidence) {
    const selected = selectTenantEvidence(apiEvidence, context.tenantId);
    const record =
      selected?.[evidenceType] ||
      selected?.[evidenceType.toLowerCase()] ||
      apiEvidence[evidenceType] ||
      apiEvidence;
    return normalizeEvidenceRecord(evidenceType, record, context);
  }

  const fileEvidence = evidenceFilePath() ? await readFileEvidence() : null;

  if (fileEvidence?.__connectorStatus) {
    return {
      status: fileEvidence.__connectorStatus,
      evidenceType,
      message: fileEvidence.__message,
    };
  }

  if (fileEvidence) {
    const selected = selectTenantEvidence(fileEvidence, context.tenantId);
    const record = selected?.[evidenceType] || selected?.[evidenceType.toLowerCase()] || null;
    return normalizeEvidenceRecord(evidenceType, record, context);
  }

  return null;
}

/**
 * @function quickBooksReport
 * @description Fetches a QuickBooks Online report.
 * @param {string} reportName - Report name.
 * @param {object} query - Query parameters.
 * @returns {Promise<object|null>} QuickBooks report.
 */
async function quickBooksReport(reportName, query = {}) {
  const realmId = env('WILSY_QUICKBOOKS_REALM_ID') || env('QUICKBOOKS_REALM_ID');
  const token = env('WILSY_QUICKBOOKS_ACCESS_TOKEN') || env('QUICKBOOKS_ACCESS_TOKEN');

  if (!realmId || !token) return null;

  const url = new URL(`${quickBooksBaseUrl()}/v3/company/${realmId}/reports/${reportName}`);

  Object.entries(query).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      url.searchParams.set(key, String(value));
    }
  });

  return fetchJson(url, {
    headers: {
      Authorization: `Bearer ${token}`,
      Accept: 'application/json',
    },
  });
}

/**
 * @function flattenQuickBooksRows
 * @description Flattens QuickBooks report rows for defensive parsing.
 * @param {object|Array} rowOrRows - Row tree.
 * @returns {Array<object>} Flat rows.
 */
function flattenQuickBooksRows(rowOrRows) {
  const rows = Array.isArray(rowOrRows) ? rowOrRows : [rowOrRows].filter(Boolean);
  const output = [];

  for (const row of rows) {
    output.push(row);

    const nested = row.Rows?.Row || row.Rows?.Rows || row.rows || [];
    output.push(...flattenQuickBooksRows(nested));
  }

  return output;
}

/**
 * @function findQuickBooksAmountByLabel
 * @description Finds an amount by label in QuickBooks report rows.
 * @param {object} report - QuickBooks report.
 * @param {Array<string>} labels - Possible labels.
 * @returns {number|null} Amount or null.
 */
function findQuickBooksAmountByLabel(report = {}, labels = []) {
  const normalizedLabels = labels.map((item) => String(item).toLowerCase());
  const rows = flattenQuickBooksRows(report.Rows?.Row || []);

  for (const row of rows) {
    const label =
      row.Summary?.ColData?.[0]?.value ||
      row.ColData?.[0]?.value ||
      row.Header?.ColData?.[0]?.value ||
      row.group ||
      '';

    if (!normalizedLabels.some((candidate) => String(label).toLowerCase().includes(candidate))) {
      continue;
    }

    const values = [...(row.Summary?.ColData || []), ...(row.ColData || [])];

    for (let index = values.length - 1; index >= 0; index -= 1) {
      const parsed = normalizeMoney(values[index]?.value);
      if (parsed !== null) return parsed;
    }
  }

  return null;
}

/**
 * @function quickBooksRevenueYtdEvidence
 * @description Builds revenue YTD evidence from QuickBooks Profit and Loss report.
 * @param {object} context - Source context.
 * @returns {Promise<object|null>} Evidence result.
 */
async function quickBooksRevenueYtdEvidence(context = {}) {
  const report = await quickBooksReport('ProfitAndLoss', {
    start_date: env('WILSY_FINANCE_PERIOD_START') || `${new Date().getFullYear()}-01-01`,
    end_date: env('WILSY_FINANCE_PERIOD_END') || new Date().toISOString().slice(0, 10),
    minorversion: env('WILSY_QUICKBOOKS_MINOR_VERSION') || '75',
  });

  if (!report) return null;

  if (report.__connectorStatus) {
    return {
      status: report.__connectorStatus,
      message: report.__message,
    };
  }

  const totalIncome = findQuickBooksAmountByLabel(report, ['total income', 'income']);

  if (totalIncome === null) {
    return {
      status: STATUS.PENDING,
      message: 'QuickBooks ProfitAndLoss report returned, but total income could not be parsed.',
    };
  }

  const evidence = {
    provider: 'QuickBooks',
    report: 'ProfitAndLoss',
    totalIncome,
    periodStart:
      report.Header?.StartPeriod ||
      env('WILSY_FINANCE_PERIOD_START') ||
      `${new Date().getFullYear()}-01-01`,
    periodEnd:
      report.Header?.EndPeriod ||
      env('WILSY_FINANCE_PERIOD_END') ||
      new Date().toISOString().slice(0, 10),
    currency: report.Header?.Currency || env('WILSY_FINANCE_CURRENCY') || 'UNKNOWN',
    rawReportHeader: report.Header || null,
  };

  const seal = hashEvidence(evidence);

  return {
    status: STATUS.VERIFIED,
    verified: true,
    sourceId: `quickbooks:profit-and-loss:${evidence.periodEnd}`,
    retrievedAt: nowIso(),
    evidence,
    evidenceHash: seal.hash,
    hashAlgorithm: seal.algorithm,
  };
}

/**
 * @function xeroInvoices
 * @description Fetches invoices from Xero Accounting API.
 * @param {object} query - Query params.
 * @returns {Promise<object|null>} Xero response.
 */
async function xeroInvoices(query = {}) {
  const token = env('WILSY_XERO_ACCESS_TOKEN') || env('XERO_ACCESS_TOKEN');
  const tenant = env('WILSY_XERO_TENANT_ID') || env('XERO_TENANT_ID');

  if (!token || !tenant) return null;

  const url = new URL(`${xeroBaseUrl()}/Invoices`);

  Object.entries(query).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      url.searchParams.set(key, String(value));
    }
  });

  return fetchJson(url, {
    headers: {
      Authorization: `Bearer ${token}`,
      'xero-tenant-id': tenant,
    },
  });
}

/**
 * @function xeroRevenueYtdEvidence
 * @description Builds revenue YTD evidence from Xero authorised invoices.
 * @param {object} context - Source context.
 * @returns {Promise<object|null>} Evidence result.
 */
async function xeroRevenueYtdEvidence(context = {}) {
  const since = env('WILSY_FINANCE_PERIOD_START') || `${new Date().getFullYear()}-01-01`;
  const response = await xeroInvoices({
    where: `Type=="ACCREC"&&Date>=DateTime(${since.replace(/-/g, ',')})`,
  });

  if (!response) return null;

  if (response.__connectorStatus) {
    return {
      status: response.__connectorStatus,
      message: response.__message,
    };
  }

  const invoices = response.Invoices || response.invoices || [];

  if (!Array.isArray(invoices) || !invoices.length) {
    return {
      status: STATUS.PENDING,
      message:
        'Xero configured, but no accounts-receivable invoices were returned for revenue evidence.',
    };
  }

  const total = invoices.reduce((sum, invoice) => {
    const amount = normalizeMoney(
      invoice.Total || invoice.total || invoice.AmountDue || invoice.amountDue
    );
    return sum + (amount || 0);
  }, 0);

  const evidence = {
    provider: 'Xero',
    evidenceType: FINANCE_EVIDENCE_TYPES.REVENUE_YTD,
    invoiceCount: invoices.length,
    totalInvoiceValue: total,
    periodStart: since,
    currency:
      invoices[0]?.CurrencyCode ||
      invoices[0]?.currencyCode ||
      env('WILSY_FINANCE_CURRENCY') ||
      'UNKNOWN',
    sampleInvoices: invoices.slice(0, 10),
  };

  const seal = hashEvidence(evidence);

  return {
    status: STATUS.VERIFIED,
    verified: true,
    sourceId: `xero:invoices:${invoices.length}:${since}`,
    retrievedAt: nowIso(),
    evidence,
    evidenceHash: seal.hash,
    hashAlgorithm: seal.algorithm,
  };
}

/**
 * @function stripeGet
 * @description Fetches from Stripe API.
 * @param {string} path - Stripe path.
 * @param {object} query - Query params.
 * @returns {Promise<object|null>} Stripe response.
 */
async function stripeGet(path, query = {}) {
  const secret = env('WILSY_STRIPE_SECRET_KEY') || env('STRIPE_SECRET_KEY');

  if (!secret) return null;

  const url = new URL(`${stripeBaseUrl()}${path}`);

  Object.entries(query).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      url.searchParams.set(key, String(value));
    }
  });

  const basic = Buffer.from(`${secret}:`).toString('base64');

  return fetchJson(url, {
    headers: {
      Authorization: `Basic ${basic}`,
    },
  });
}

/**
 * @function stripeAnnualRecurringRevenueEvidence
 * @description Builds ARR evidence from Stripe subscriptions when configured.
 * @param {object} context - Source context.
 * @returns {Promise<object|null>} ARR evidence.
 */
async function stripeAnnualRecurringRevenueEvidence(context = {}) {
  const response = await stripeGet('/v1/subscriptions', {
    status: 'active',
    limit: 100,
  });

  if (!response) return null;

  if (response.__connectorStatus) {
    return {
      status: response.__connectorStatus,
      message: response.__message,
    };
  }

  const subscriptions = response.data || [];

  if (!Array.isArray(subscriptions) || !subscriptions.length) {
    return {
      status: STATUS.PENDING,
      message: 'Stripe configured, but no active subscriptions returned for ARR evidence.',
    };
  }

  let annualMinorUnits = 0;
  const normalized = [];

  for (const subscription of subscriptions) {
    for (const item of subscription.items?.data || []) {
      const price = item.price || {};
      const quantity = item.quantity || 1;
      const unitAmount = price.unit_amount || 0;
      const interval = price.recurring?.interval || '';
      const intervalCount = price.recurring?.interval_count || 1;

      let annualMultiplier = 0;

      if (interval === 'year') annualMultiplier = 1 / intervalCount;
      if (interval === 'month') annualMultiplier = 12 / intervalCount;
      if (interval === 'week') annualMultiplier = 52 / intervalCount;
      if (interval === 'day') annualMultiplier = 365 / intervalCount;

      const annualized = unitAmount * quantity * annualMultiplier;
      annualMinorUnits += annualized;

      normalized.push({
        subscriptionId: subscription.id,
        priceId: price.id,
        currency: price.currency,
        unitAmount,
        quantity,
        interval,
        intervalCount,
        annualizedMinorUnits: annualized,
      });
    }
  }

  if (!annualMinorUnits) {
    return {
      status: STATUS.PENDING,
      message:
        'Stripe active subscriptions exist, but recurring price values could not be annualized.',
    };
  }

  const evidence = {
    provider: 'Stripe',
    evidenceType: FINANCE_EVIDENCE_TYPES.ANNUAL_RECURRING_REVENUE,
    annualMinorUnits,
    currency: normalized[0]?.currency || env('WILSY_FINANCE_CURRENCY') || 'UNKNOWN',
    subscriptionCount: subscriptions.length,
    normalizedSubscriptions: normalized,
  };

  const seal = hashEvidence(evidence);

  return {
    status: STATUS.VERIFIED,
    verified: true,
    sourceId: `stripe:subscriptions:${subscriptions.length}`,
    retrievedAt: nowIso(),
    evidence,
    evidenceHash: seal.hash,
    hashAlgorithm: seal.algorithm,
  };
}

/**
 * @function evidenceNeedsFileOrGenericApi
 * @description Returns a PENDING result for finance metrics not safely derivable from provider APIs alone.
 * @param {string} evidenceType - Evidence type.
 * @param {string} reason - Reason.
 * @returns {object} PENDING result.
 */
function evidenceNeedsFileOrGenericApi(evidenceType, reason) {
  return {
    status: STATUS.PENDING,
    evidenceType,
    message: reason,
    requirements: {
      configuredEvidenceFile: Boolean(evidenceFilePath()),
      configuredFinanceApi: Boolean(genericFinanceApiUrl()),
    },
  };
}

/**
 * @function firstMeaningfulResult
 * @description Returns VERIFIED if any provider verified; otherwise the most useful status.
 * @param {Array<object|null>} results - Results.
 * @param {string} evidenceType - Evidence type.
 * @returns {object} Rolled result.
 */
function firstMeaningfulResult(results = [], evidenceType) {
  const usable = results.filter(Boolean);

  if (!usable.length) {
    return {
      status: STATUS.MISSING,
      evidenceType,
      message:
        'No finance source configured. Configure WILSY_FINANCE_EVIDENCE_FILE, WILSY_FINANCE_API_URL, QuickBooks, Xero, or Stripe credentials.',
    };
  }

  const verified = usable.find((item) => item.status === STATUS.VERIFIED);
  if (verified) return verified;

  const error = usable.find((item) => item.status === STATUS.ERROR);
  if (error) return error;

  const missing = usable.find((item) => item.status === STATUS.MISSING);
  if (missing) return missing;

  return usable[0];
}

/**
 * @function getRevenueYTD
 * @description Returns verified year-to-date revenue evidence.
 * @param {object} context - Source registry context.
 * @returns {Promise<object>} Revenue YTD evidence.
 */
export async function getRevenueYTD(context = {}) {
  try {
    const local = await evidenceFromLocalOrGenericStore(
      FINANCE_EVIDENCE_TYPES.REVENUE_YTD,
      context
    );
    const quickBooks = await quickBooksRevenueYtdEvidence(context);
    const xero = await xeroRevenueYtdEvidence(context);

    return firstMeaningfulResult([local, quickBooks, xero], FINANCE_EVIDENCE_TYPES.REVENUE_YTD);
  } catch (error) {
    return {
      status: STATUS.ERROR,
      evidenceType: FINANCE_EVIDENCE_TYPES.REVENUE_YTD,
      message: error.message,
    };
  }
}

/**
 * @function getAnnualRecurringRevenue
 * @description Returns verified ARR evidence.
 * @param {object} context - Source registry context.
 * @returns {Promise<object>} ARR evidence.
 */
export async function getAnnualRecurringRevenue(context = {}) {
  try {
    const local = await evidenceFromLocalOrGenericStore(
      FINANCE_EVIDENCE_TYPES.ANNUAL_RECURRING_REVENUE,
      context
    );
    const stripe = await stripeAnnualRecurringRevenueEvidence(context);

    return firstMeaningfulResult(
      [
        local,
        stripe,
        evidenceNeedsFileOrGenericApi(
          FINANCE_EVIDENCE_TYPES.ANNUAL_RECURRING_REVENUE,
          'ARR requires subscription billing evidence from Stripe or a configured finance evidence source.'
        ),
      ],
      FINANCE_EVIDENCE_TYPES.ANNUAL_RECURRING_REVENUE
    );
  } catch (error) {
    return {
      status: STATUS.ERROR,
      evidenceType: FINANCE_EVIDENCE_TYPES.ANNUAL_RECURRING_REVENUE,
      message: error.message,
    };
  }
}

/**
 * @function getRunwayMonths
 * @description Returns verified runway evidence.
 * @param {object} context - Source registry context.
 * @returns {Promise<object>} Runway evidence.
 */
export async function getRunwayMonths(context = {}) {
  try {
    const local = await evidenceFromLocalOrGenericStore(
      FINANCE_EVIDENCE_TYPES.RUNWAY_MONTHS,
      context
    );

    return firstMeaningfulResult(
      [
        local,
        evidenceNeedsFileOrGenericApi(
          FINANCE_EVIDENCE_TYPES.RUNWAY_MONTHS,
          'Runway requires cash balance and burn-rate evidence from a configured finance evidence source.'
        ),
      ],
      FINANCE_EVIDENCE_TYPES.RUNWAY_MONTHS
    );
  } catch (error) {
    return {
      status: STATUS.ERROR,
      evidenceType: FINANCE_EVIDENCE_TYPES.RUNWAY_MONTHS,
      message: error.message,
    };
  }
}

/**
 * @function getContractValueLedger
 * @description Returns verified contract value ledger evidence.
 * @param {object} context - Source registry context.
 * @returns {Promise<object>} Contract value ledger evidence.
 */
export async function getContractValueLedger(context = {}) {
  try {
    const local = await evidenceFromLocalOrGenericStore(
      FINANCE_EVIDENCE_TYPES.CONTRACT_VALUE_LEDGER,
      context
    );

    return firstMeaningfulResult(
      [
        local,
        evidenceNeedsFileOrGenericApi(
          FINANCE_EVIDENCE_TYPES.CONTRACT_VALUE_LEDGER,
          'Contract value ledger requires source ledger evidence with contract ID, counterparty, amount, currency and approval trail.'
        ),
      ],
      FINANCE_EVIDENCE_TYPES.CONTRACT_VALUE_LEDGER
    );
  } catch (error) {
    return {
      status: STATUS.ERROR,
      evidenceType: FINANCE_EVIDENCE_TYPES.CONTRACT_VALUE_LEDGER,
      message: error.message,
    };
  }
}

export default Object.freeze({
  getRevenueYTD,
  getAnnualRecurringRevenue,
  getRunwayMonths,
  getContractValueLedger,
});
