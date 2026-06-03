/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - TREASURY SWEEP MANAGER [V56.2.0-PRODUCTION-LIQUIDITY]                                                                      ║
 * ║ [LIQUIDITY POLICY | BENCHMARK-AWARE YIELD ROUTING | APPROVAL GATES | SHA3 SWEEP PROOFS]                                               ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 56.2.0-PRODUCTION-LIQUIDITY | PRODUCTION READY | INSTITUTIONAL CASH CONTROL                                                  ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/services/TreasurySweepManager.js                                     ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                    ║
 * ║ • Wilson Khanyezi (CEO/Lead Architect) - Required treasury automation to become governed liquidity infrastructure, not hard-coded     ║
 * ║   yield theatre or blind cash movement.                                                                                                ║
 * ║ • AI Engineering (Codex) - ARCHITECTED: Added benchmark-aware policy, operating buffers, approval gates, bank variance controls,       ║
 * ║   source-silent execution safety, and SHA3-sealed treasury receipts.                                                                    ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 *
 * This is not an investment-advice engine and it does not fabricate banking execution.
 * It evaluates cash against operating buffers, statutory reserves, reconciliation risk and
 * benchmark freshness, then executes only through live treasury endpoints when all gates pass.
 */

import { sha3_512 } from 'js-sha3';
import api from './api';
import { broadcastTelemetry } from '../utils/telemetryHelper';

export const TREASURY_SWEEP_MANAGER_VERSION = 'V56.2.0-PRODUCTION-LIQUIDITY';

const LIVE_POLICY_CACHE_TTL_MS = 20 * 60 * 1000;
const LIVE_POLICY_BACKOFF_MS = 5 * 60 * 1000;
const RATE_DENOMINATOR = 10000;

const STATUS_ENDPOINTS = Object.freeze([
  tenantId => `/treasury/status/${tenantId}`,
  tenantId => `/finance/treasury/status/${tenantId}`,
  tenantId => `/billing/treasury/status/${tenantId}`
]);

const BALANCE_ENDPOINTS = Object.freeze([
  () => '/treasury/balances',
  () => '/finance/treasury/balances'
]);

const EXECUTION_ENDPOINTS = Object.freeze([
  tenantId => `/treasury/sweep/${tenantId}`,
  () => '/treasury/sweep/execute',
  () => '/finance/treasury/sweep/execute'
]);

const POLICY_ENDPOINTS = Object.freeze([
  () => '/treasury/policy/matrix',
  () => '/finance/treasury/policy/matrix',
  () => '/system/treasury/policy/matrix'
]);

const BENCHMARK_ENDPOINTS = Object.freeze([
  () => '/treasury/benchmarks/latest',
  () => '/finance/benchmarks/latest',
  () => '/system/rates/benchmarks'
]);

const CURRENCY_EXPONENTS = Object.freeze({
  BHD: 3,
  BIF: 0,
  CLP: 0,
  DJF: 0,
  GNF: 0,
  JOD: 3,
  JPY: 0,
  KRW: 0,
  KWD: 3,
  MGA: 0,
  OMR: 3,
  PYG: 0,
  RWF: 0,
  TND: 3,
  UGX: 0,
  VND: 0,
  VUV: 0,
  XAF: 0,
  XOF: 0,
  XPF: 0
});

export const TREASURY_POLICY_MATRIX = Object.freeze({
  ZAR: {
    currency: 'ZAR',
    targetSleeve: 'ZAR_OPERATIONAL_LIQUIDITY_RESERVE',
    benchmarkCode: 'SARB_POLICY_RATE_ZARONIA',
    benchmarkSource: 'South African Reserve Bank current market rates and ZARONIA references',
    benchmarkSourceUrls: [
      'https://www.resbank.co.za/en/home/what-we-do/statistics/key-statistics/current-market-rates',
      'https://www.resbank.co.za/en/home/what-we-do/financial-markets/zaroniarate'
    ],
    operatingBuffer: 500000,
    minSweepAmount: 50000,
    autoApprovalLimit: 250000,
    maxSweepPercentOfBalance: 0.55,
    runwayDays: 45,
    settlementHorizonDays: 1,
    instrumentPreference: ['CALL_DEPOSIT', 'TREASURY_MM_FUND', 'SARB_LINKED_CASH'],
    staticPolicyBps: 625,
    sourceStatus: 'STATIC_POLICY_REQUIRES_LIVE_BENCHMARK'
  },
  USD: {
    currency: 'USD',
    targetSleeve: 'USD_TREASURY_BILL_LADDER',
    benchmarkCode: 'US_TREASURY_BILL',
    benchmarkSource: 'U.S. Department of the Treasury Daily Treasury Bill Rates',
    benchmarkSourceUrls: ['https://home.treasury.gov/resource-center/data-chart-center/interest-rates/TextView?type=daily_treasury_bill_rates'],
    operatingBuffer: 50000,
    minSweepAmount: 10000,
    autoApprovalLimit: 100000,
    maxSweepPercentOfBalance: 0.60,
    runwayDays: 45,
    settlementHorizonDays: 1,
    instrumentPreference: ['GOVERNMENT_MM_FUND', 'T_BILL_4W', 'T_BILL_13W'],
    staticPolicyBps: 430,
    sourceStatus: 'STATIC_POLICY_REQUIRES_LIVE_BENCHMARK'
  },
  EUR: {
    currency: 'EUR',
    targetSleeve: 'EUR_GOVERNMENT_LIQUIDITY_RESERVE',
    benchmarkCode: 'ECB_DEPOSIT_FACILITY',
    benchmarkSource: 'European Central Bank key interest rates',
    benchmarkSourceUrls: ['https://www.ecb.europa.eu/stats/policy_and_exchange_rates/key_ecb_interest_rates/html/index.en.html'],
    operatingBuffer: 45000,
    minSweepAmount: 10000,
    autoApprovalLimit: 90000,
    maxSweepPercentOfBalance: 0.55,
    runwayDays: 45,
    settlementHorizonDays: 1,
    instrumentPreference: ['GOVERNMENT_MM_FUND', 'OVERNIGHT_DEPOSIT', 'SHORT_DURATION_TBILL'],
    staticPolicyBps: 220,
    sourceStatus: 'STATIC_POLICY_REQUIRES_LIVE_BENCHMARK'
  },
  GBP: {
    currency: 'GBP',
    targetSleeve: 'GBP_STERLING_LIQUIDITY_RESERVE',
    benchmarkCode: 'BOE_BANK_RATE',
    benchmarkSource: 'Bank of England Bank Rate',
    benchmarkSourceUrls: ['https://www.bankofengland.co.uk/boeapps/database/Bank-Rate.asp'],
    operatingBuffer: 40000,
    minSweepAmount: 10000,
    autoApprovalLimit: 80000,
    maxSweepPercentOfBalance: 0.55,
    runwayDays: 45,
    settlementHorizonDays: 1,
    instrumentPreference: ['STERLING_MM_FUND', 'TREASURY_BILL', 'OVERNIGHT_DEPOSIT'],
    staticPolicyBps: 350,
    sourceStatus: 'STATIC_POLICY_REQUIRES_LIVE_BENCHMARK'
  }
});

/**
 * @function stableStringify
 * @description Serializes values with deterministic key ordering for repeatable proof hashes.
 * @param {unknown} value - Value to serialize.
 * @returns {string} Canonical JSON string.
 */
export const stableStringify = (value) => {
  if (typeof value === 'undefined') return 'null';
  if (value instanceof Date) return JSON.stringify(value.toISOString());
  if (value === null || typeof value !== 'object') return JSON.stringify(value);
  if (Array.isArray(value)) return `[${value.map(item => stableStringify(item)).join(',')}]`;
  return `{${Object.keys(value).sort().map(key => `${JSON.stringify(key)}:${stableStringify(value[key])}`).join(',')}}`;
};

/**
 * @function createTreasuryProofHash
 * @description Creates a SHA3-512 proof hash over a canonical treasury packet.
 * @param {Object} payload - Treasury payload.
 * @returns {string} Uppercase SHA3-512 digest.
 */
export const createTreasuryProofHash = (payload) => sha3_512(stableStringify(payload)).toUpperCase();

/**
 * @function normalizeCurrency
 * @description Normalizes a currency code for treasury policy lookup.
 * @param {string} value - Raw currency.
 * @returns {string} Uppercase currency code.
 */
export const normalizeCurrency = (value = 'ZAR') => String(value || 'ZAR').trim().toUpperCase().slice(0, 3) || 'ZAR';

/**
 * @function getCurrencyExponent
 * @description Resolves the minor-unit exponent for a currency.
 * @param {string} currency - Currency code.
 * @returns {number} Currency exponent.
 */
export const getCurrencyExponent = (currency = 'ZAR') => CURRENCY_EXPONENTS[normalizeCurrency(currency)] ?? 2;

/**
 * @function toMinorUnits
 * @description Converts a display amount into integer minor units.
 * @param {number|string} value - Display amount.
 * @param {string} currency - Currency code.
 * @returns {number} Minor-unit integer.
 */
export const toMinorUnits = (value, currency = 'ZAR') => {
  const exponent = getCurrencyExponent(currency);
  const scale = 10 ** exponent;
  const numeric = Number(value || 0);
  return Number.isFinite(numeric) ? Math.round(numeric * scale) : 0;
};

/**
 * @function fromMinorUnits
 * @description Converts integer minor units into a decimal amount.
 * @param {number} minorUnits - Minor units.
 * @param {string} currency - Currency code.
 * @returns {number} Decimal amount.
 */
export const fromMinorUnits = (minorUnits, currency = 'ZAR') => {
  const exponent = getCurrencyExponent(currency);
  return Number((Number(minorUnits || 0) / (10 ** exponent)).toFixed(exponent));
};

/**
 * @function bpsToRate
 * @description Converts basis points into a decimal rate.
 * @param {number} bps - Basis points.
 * @returns {number} Decimal rate.
 */
export const bpsToRate = (bps = 0) => Number(bps || 0) / RATE_DENOMINATOR;

/**
 * @function normalizeApiPayload
 * @description Normalizes mixed Wilsy API envelopes.
 * @param {Object} response - Axios response or raw service payload.
 * @returns {Object|null} Normalized payload.
 */
const normalizeApiPayload = (response) => response?.data?.data || response?.data || response || null;

/**
 * @function clonePolicy
 * @description Creates a mutable policy copy for runtime enrichment.
 * @param {Object} policy - Treasury policy.
 * @returns {Object} Cloned policy.
 */
const clonePolicy = (policy) => JSON.parse(JSON.stringify(policy || {}));

/**
 * @function normalizePolicyPayload
 * @description Normalizes a backend treasury policy matrix into currency-keyed policies.
 * @param {Object|Array} payload - Raw policy payload.
 * @returns {Object} Normalized matrix.
 */
const normalizePolicyPayload = (payload) => {
  const raw = payload?.policies || payload?.matrix || payload?.data || payload;
  if (Array.isArray(raw)) {
    return raw.reduce((acc, item) => {
      const currency = normalizeCurrency(item.currency);
      acc[currency] = { ...item, currency };
      return acc;
    }, {});
  }
  if (!raw || typeof raw !== 'object') return {};
  return Object.entries(raw).reduce((acc, [currency, policy]) => {
    acc[normalizeCurrency(currency)] = { ...policy, currency: normalizeCurrency(currency) };
    return acc;
  }, {});
};

/**
 * @function normalizeBenchmarkPayload
 * @description Normalizes live benchmark data into a currency-keyed map.
 * @param {Object|Array} payload - Raw benchmark payload.
 * @returns {Object} Benchmark matrix.
 */
const normalizeBenchmarkPayload = (payload) => {
  const raw = payload?.benchmarks || payload?.rates || payload?.data || payload;
  if (Array.isArray(raw)) {
    return raw.reduce((acc, item) => {
      const currency = normalizeCurrency(item.currency);
      acc[currency] = {
        currency,
        benchmarkBps: Number(item.benchmarkBps ?? item.rateBps ?? Number(item.rate || 0) * RATE_DENOMINATOR),
        sourceStatus: item.sourceStatus || 'LIVE_BENCHMARK',
        source: item.source || item.benchmarkCode || item.name || 'LIVE_TREASURY_BENCHMARK',
        updatedAt: item.updatedAt || item.asOf || new Date().toISOString()
      };
      return acc;
    }, {});
  }
  if (!raw || typeof raw !== 'object') return {};
  return Object.entries(raw).reduce((acc, [currency, item]) => {
    const normalized = normalizeCurrency(currency);
    acc[normalized] = {
      currency: normalized,
      benchmarkBps: Number(item.benchmarkBps ?? item.rateBps ?? Number(item.rate || 0) * RATE_DENOMINATOR),
      sourceStatus: item.sourceStatus || 'LIVE_BENCHMARK',
      source: item.source || item.benchmarkCode || item.name || 'LIVE_TREASURY_BENCHMARK',
      updatedAt: item.updatedAt || item.asOf || new Date().toISOString()
    };
    return acc;
  }, {});
};

/**
 * @class TreasurySweepManager
 * @description Evaluates and executes governed liquidity sweeps with proof hashes and execution gates.
 */
class TreasurySweepManager {
  /**
   * @constructor
   * @param {Object} config - Manager configuration.
   * @param {Object} [config.apiClient] - Axios-compatible client.
   * @param {Object} [config.policyMatrix] - Currency policy matrix.
   * @param {number} [config.cacheTtlMs] - Live policy cache TTL.
   */
  constructor(config = {}) {
    this.engineVersion = config.engineVersion || TREASURY_SWEEP_MANAGER_VERSION;
    this.apiClient = config.apiClient || api;
    this.policyMatrix = new Map(Object.entries(config.policyMatrix || TREASURY_POLICY_MATRIX).map(([currency, policy]) => [
      normalizeCurrency(currency),
      clonePolicy(policy)
    ]));
    this.benchmarkMatrix = new Map();
    this.cacheTtlMs = Number(config.cacheTtlMs || LIVE_POLICY_CACHE_TTL_MS);
    this.livePolicyBackoffUntil = 0;
    this.lastPolicySync = null;
    this.lastBenchmarkSync = null;
  }

  /**
   * @method createTraceId
   * @description Creates a treasury trace id for command and telemetry correlation.
   * @param {string} tenantId - Tenant id.
   * @param {string} currency - Currency code.
   * @returns {string} Trace id.
   */
  createTraceId(tenantId = 'GLOBAL_ROOT', currency = 'ZAR') {
    const cryptoSource = typeof crypto !== 'undefined' ? crypto : null;
    const entropy = cryptoSource?.randomUUID
      ? cryptoSource.randomUUID().slice(0, 12)
      : `${Date.now().toString(36)}${Math.random().toString(36).slice(2, 8)}`;
    return `SWP-${String(tenantId || 'GLOBAL_ROOT').toUpperCase()}-${normalizeCurrency(currency)}-${entropy.toUpperCase()}`;
  }

  /**
   * @method getPolicy
   * @description Resolves a treasury policy for a supported currency.
   * @param {string} currency - Currency code.
   * @returns {Object|null} Policy or null.
   */
  getPolicy(currency = 'ZAR') {
    const code = normalizeCurrency(currency);
    const policy = this.policyMatrix.get(code);
    if (!policy) return null;
    const benchmark = this.benchmarkMatrix.get(code);
    return {
      ...clonePolicy(policy),
      benchmarkBps: Number(benchmark?.benchmarkBps ?? policy.staticPolicyBps ?? 0),
      benchmarkSourceStatus: benchmark?.sourceStatus || policy.sourceStatus || 'STATIC_POLICY_REQUIRES_LIVE_BENCHMARK',
      benchmarkUpdatedAt: benchmark?.updatedAt || null,
      benchmarkSource: benchmark?.source || policy.benchmarkSource
    };
  }

  /**
   * @method evaluateLiquidity
   * @description Evaluates operating cash against buffer, reconciliation, approval and benchmark gates.
   * @param {Object} params - Evaluation inputs.
   * @param {string} params.tenantId - Tenant id.
   * @param {string} params.currency - Currency code.
   * @param {number|string} params.currentBalance - Operating account balance.
   * @param {number|string|null} [params.requestedAmount] - Optional requested sweep amount.
   * @param {string} [params.sourceStatus='SOURCE_SILENT'] - Balance source status.
   * @param {Object} [params.context] - Liquidity context.
   * @returns {Object} Sealed evaluation packet.
   */
  evaluateLiquidity({
    tenantId = 'GLOBAL_ROOT',
    currency = 'ZAR',
    currentBalance = 0,
    requestedAmount = null,
    sourceStatus = 'SOURCE_SILENT',
    context = {}
  } = {}) {
    const traceId = this.createTraceId(tenantId, currency);
    const code = normalizeCurrency(currency);
    const policy = this.getPolicy(code);
    const generatedAt = new Date().toISOString();

    if (!policy) {
      const packet = {
        success: false,
        status: 'UNSUPPORTED_CURRENCY',
        executionEligible: false,
        traceId,
        tenantId,
        currency: code,
        generatedAt,
        gates: [{ gate: 'SUPPORTED_CURRENCY', status: 'FAIL', detail: `${code} is not in the treasury policy matrix.` }],
        warning: 'Unsupported currency for governed treasury sweeps.'
      };
      return { ...packet, proof: { algorithm: 'SHA3-512', hash: createTreasuryProofHash(packet) } };
    }

    const balanceMinor = toMinorUnits(currentBalance, code);
    const requestedMinor = requestedAmount === null || typeof requestedAmount === 'undefined'
      ? null
      : Math.max(0, toMinorUnits(requestedAmount, code));
    const operatingBufferMinor = toMinorUnits(policy.operatingBuffer, code);
    const minSweepMinor = toMinorUnits(policy.minSweepAmount, code);
    const burnRateMinor = toMinorUnits(context.monthlyBurnRate || context.recognizedRunRate || 0, code);
    const runwayBufferMinor = Math.round((burnRateMinor / 30) * Number(policy.runwayDays || 45));
    const statutoryReserveMinor = toMinorUnits(
      Number(context.pendingPayments || 0)
        + Number(context.taxReserve || 0)
        + Number(context.payrollReserve || 0),
      code
    );
    const bankVarianceMinor = Math.abs(toMinorUnits(context.bankVariance || 0, code));
    const requiredBufferMinor = Math.max(
      operatingBufferMinor,
      runwayBufferMinor,
      statutoryReserveMinor + bankVarianceMinor
    );
    const rawAvailableMinor = Math.max(0, balanceMinor - requiredBufferMinor);
    const concentrationCapMinor = Math.floor(balanceMinor * Number(policy.maxSweepPercentOfBalance || 0.55));
    const policyCandidateMinor = Math.min(rawAvailableMinor, concentrationCapMinor);
    const candidateMinor = requestedMinor === null ? policyCandidateMinor : Math.min(policyCandidateMinor, requestedMinor);
    const projectedAnnualYieldMinor = Math.round(candidateMinor * bpsToRate(policy.benchmarkBps));
    const approvalRequired = candidateMinor > toMinorUnits(policy.autoApprovalLimit, code);
    const liveBenchmark = policy.benchmarkSourceStatus === 'LIVE_BENCHMARK';
    const sourceLive = ['LIVE', 'LIVE_TREASURY', 'BANK_API', 'LIVE_BANK'].includes(String(sourceStatus).toUpperCase());
    const varianceWithinTolerance = bankVarianceMinor <= Math.max(toMinorUnits(context.varianceTolerance || 100, code), Math.round(balanceMinor * 0.0025));

    const gates = [
      { gate: 'BALANCE_SOURCE', status: sourceLive ? 'PASS' : 'REVIEW', detail: sourceStatus },
      { gate: 'OPERATING_BUFFER', status: balanceMinor > requiredBufferMinor ? 'PASS' : 'FAIL', detail: `${fromMinorUnits(requiredBufferMinor, code)} ${code} required buffer` },
      { gate: 'MIN_SWEEP_AMOUNT', status: candidateMinor >= minSweepMinor ? 'PASS' : 'FAIL', detail: `${fromMinorUnits(minSweepMinor, code)} ${code} minimum` },
      { gate: 'BENCHMARK_FRESHNESS', status: liveBenchmark ? 'PASS' : 'REVIEW', detail: policy.benchmarkSourceStatus },
      { gate: 'BANK_RECONCILIATION', status: varianceWithinTolerance ? 'PASS' : 'REVIEW', detail: `${fromMinorUnits(bankVarianceMinor, code)} ${code} variance` },
      { gate: 'APPROVAL_LIMIT', status: approvalRequired ? 'REVIEW' : 'PASS', detail: `${fromMinorUnits(policy.autoApprovalLimit, code)} ${code} auto limit` }
    ];

    const failed = gates.some(gate => gate.status === 'FAIL');
    const review = gates.some(gate => gate.status === 'REVIEW');
    const status = failed
      ? 'NO_ACTION'
      : (review || approvalRequired ? 'REVIEW_REQUIRED' : 'READY_FOR_EXECUTION');
    const executionEligible = status === 'READY_FOR_EXECUTION';

    const packet = {
      success: true,
      traceId,
      tenantId,
      currency: code,
      generatedAt,
      status,
      executionEligible,
      approvalRequired,
      sourceStatus,
      policy: {
        targetSleeve: policy.targetSleeve,
        benchmarkCode: policy.benchmarkCode,
        benchmarkSource: policy.benchmarkSource,
        benchmarkBps: policy.benchmarkBps,
        benchmarkSourceStatus: policy.benchmarkSourceStatus,
        benchmarkSourceUrls: policy.benchmarkSourceUrls || [],
        instrumentPreference: policy.instrumentPreference || [],
        settlementHorizonDays: policy.settlementHorizonDays
      },
      liquidity: {
        currentBalance: fromMinorUnits(balanceMinor, code),
        operatingBuffer: fromMinorUnits(operatingBufferMinor, code),
        runwayBuffer: fromMinorUnits(runwayBufferMinor, code),
        statutoryReserve: fromMinorUnits(statutoryReserveMinor, code),
        requiredBuffer: fromMinorUnits(requiredBufferMinor, code),
        availableToSweep: fromMinorUnits(candidateMinor, code),
        projectedAnnualYield: fromMinorUnits(projectedAnnualYieldMinor, code),
        minorUnits: {
          currentBalance: balanceMinor,
          requiredBuffer: requiredBufferMinor,
          availableToSweep: candidateMinor,
          projectedAnnualYield: projectedAnnualYieldMinor
        }
      },
      gates,
      warnings: gates
        .filter(gate => gate.status !== 'PASS')
        .map(gate => `${gate.gate}: ${gate.detail}`)
    };

    return {
      ...packet,
      proof: {
        algorithm: 'SHA3-512',
        canonicalization: 'STABLE_JSON_KEY_SORT',
        hash: createTreasuryProofHash(packet),
        canonicalPayload: stableStringify(packet)
      }
    };
  }

  /**
   * @method getTreasuryStatus
   * @description Fetches live treasury status/balances from available backend endpoints.
   * @param {string} tenantId - Tenant id.
   * @returns {Promise<Object>} Treasury status packet.
   */
  async getTreasuryStatus(tenantId = 'GLOBAL_ROOT') {
    for (const endpointFactory of STATUS_ENDPOINTS) {
      try {
        const response = await this.apiClient.get(endpointFactory(tenantId), { params: { tenantId } });
        const payload = normalizeApiPayload(response) || {};
        return {
          success: true,
          status: payload.status || 'LIVE',
          sourceStatus: payload.sourceStatus || 'LIVE_TREASURY',
          tenantId,
          balances: payload.balances || payload.accounts || {},
          sweeps: payload.sweeps || payload.recentSweeps || [],
          availableLiquidity: Number(payload.availableLiquidity || payload.liquidity || 0),
          raw: payload
        };
      } catch {
        continue;
      }
    }

    for (const endpointFactory of BALANCE_ENDPOINTS) {
      try {
        const response = await this.apiClient.get(endpointFactory(), { params: { tenantId } });
        const payload = normalizeApiPayload(response) || {};
        return {
          success: true,
          status: 'LIVE',
          sourceStatus: 'LIVE_TREASURY',
          tenantId,
          balances: payload.balances || payload.accounts || payload || {},
          sweeps: [],
          availableLiquidity: Number(payload.availableLiquidity || payload.liquidity || 0),
          raw: payload
        };
      } catch {
        continue;
      }
    }

    return {
      success: false,
      status: 'SOURCE_SILENT',
      sourceStatus: 'SOURCE_SILENT',
      tenantId,
      balances: {},
      sweeps: [],
      availableLiquidity: 0,
      warning: 'No treasury status or bank-balance endpoint responded.'
    };
  }

  /**
   * @method syncBenchmarks
   * @description Refreshes benchmark rates from backend benchmark services when available.
   * @returns {Promise<Object>} Benchmark sync status.
   */
  async syncBenchmarks() {
    if (Date.now() < this.livePolicyBackoffUntil) {
      return { success: false, status: 'LIVE_POLICY_BACKOFF', count: this.benchmarkMatrix.size };
    }

    for (const endpointFactory of BENCHMARK_ENDPOINTS) {
      try {
        const response = await this.apiClient.get(endpointFactory());
        const benchmarks = normalizeBenchmarkPayload(normalizeApiPayload(response));
        const entries = Object.entries(benchmarks);
        if (entries.length) {
          entries.forEach(([currency, benchmark]) => this.benchmarkMatrix.set(normalizeCurrency(currency), benchmark));
          this.lastBenchmarkSync = new Date().toISOString();
          return { success: true, status: 'LIVE_BENCHMARKS_SYNCED', count: this.benchmarkMatrix.size, lastBenchmarkSync: this.lastBenchmarkSync };
        }
      } catch {
        continue;
      }
    }

    this.livePolicyBackoffUntil = Date.now() + LIVE_POLICY_BACKOFF_MS;
    return { success: false, status: 'BENCHMARK_SOURCE_SILENT', count: this.benchmarkMatrix.size };
  }

  /**
   * @method syncPolicyMatrix
   * @description Refreshes treasury sweep policies from backend policy services while preserving static policy.
   * @returns {Promise<Object>} Policy sync status.
   */
  async syncPolicyMatrix() {
    if (Date.now() < this.livePolicyBackoffUntil) {
      return { success: false, status: 'LIVE_POLICY_BACKOFF', count: this.policyMatrix.size };
    }

    for (const endpointFactory of POLICY_ENDPOINTS) {
      try {
        const response = await this.apiClient.get(endpointFactory());
        const matrix = normalizePolicyPayload(normalizeApiPayload(response));
        const entries = Object.entries(matrix);
        if (entries.length) {
          entries.forEach(([currency, policy]) => this.policyMatrix.set(normalizeCurrency(currency), { ...this.getPolicy(currency), ...policy }));
          this.lastPolicySync = new Date().toISOString();
          return { success: true, status: 'LIVE_POLICY_SYNCED', count: this.policyMatrix.size, lastPolicySync: this.lastPolicySync };
        }
      } catch {
        continue;
      }
    }

    this.livePolicyBackoffUntil = Date.now() + LIVE_POLICY_BACKOFF_MS;
    return { success: false, status: 'POLICY_SOURCE_SILENT_FALLBACK_PRESERVED', count: this.policyMatrix.size };
  }

  /**
   * @method executeSweep
   * @description Executes a governed treasury sweep only after evaluation gates pass.
   * @param {Object} params - Execution params.
   * @param {string} params.tenantId - Tenant id.
   * @param {string} params.currency - Currency code.
   * @param {number|string} [params.currentBalance] - Operating balance.
   * @param {number|string|null} [params.requestedAmount] - Requested sweep amount.
   * @param {Object} [params.context] - Liquidity context.
   * @param {Object} [params.approval] - Approval evidence.
   * @param {boolean} [params.dryRun=false] - Whether to avoid backend execution.
   * @returns {Promise<Object>} Execution or review receipt.
   */
  async executeSweep({
    tenantId = 'GLOBAL_ROOT',
    currency = 'ZAR',
    currentBalance = null,
    requestedAmount = null,
    context = {},
    approval = {},
    dryRun = false
  } = {}) {
    const status = currentBalance === null
      ? await this.getTreasuryStatus(tenantId)
      : { sourceStatus: context.sourceStatus || 'LEDGER_CONTEXT', availableLiquidity: Number(currentBalance || 0), balances: { [normalizeCurrency(currency)]: currentBalance } };
    const code = normalizeCurrency(currency);
    const balance = currentBalance ?? status.balances?.[code] ?? status.availableLiquidity ?? 0;
    const evaluation = this.evaluateLiquidity({
      tenantId,
      currency: code,
      currentBalance: balance,
      requestedAmount,
      sourceStatus: status.sourceStatus,
      context
    });

    if (!evaluation.executionEligible || dryRun) {
      const receipt = {
        success: true,
        status: dryRun ? 'DRY_RUN' : evaluation.status,
        executionStatus: dryRun ? 'SIMULATED_ONLY' : 'NO_EXECUTION',
        tenantId,
        currency: code,
        evaluation,
        message: dryRun
          ? 'Dry run completed. No funds moved.'
          : 'Treasury sweep held by policy gates. No funds moved.'
      };
      return {
        ...receipt,
        proof: {
          algorithm: 'SHA3-512',
          hash: createTreasuryProofHash(receipt)
        }
      };
    }

    const payload = {
      traceId: evaluation.traceId,
      tenantId,
      currency: code,
      amount: evaluation.liquidity.availableToSweep,
      amountMinor: evaluation.liquidity.minorUnits.availableToSweep,
      sourceAccount: context.sourceAccount || 'OPERATING_CORE',
      destinationSleeve: evaluation.policy.targetSleeve,
      instrumentPreference: evaluation.policy.instrumentPreference,
      approval,
      evaluationProofHash: evaluation.proof.hash,
      engineVersion: this.engineVersion,
      requestedAt: new Date().toISOString()
    };

    for (const endpointFactory of EXECUTION_ENDPOINTS) {
      try {
        const response = await this.apiClient.post(endpointFactory(tenantId), payload);
        const responsePayload = normalizeApiPayload(response) || {};
        const receipt = {
          success: true,
          status: responsePayload.status || 'EXECUTED',
          executionStatus: 'EXECUTED',
          tenantId,
          currency: code,
          evaluation,
          receipt: responsePayload.receipt || responsePayload,
          payload
        };
        await Promise.resolve(broadcastTelemetry(tenantId, 'TREASURY_SWEEP', 'EXECUTED', 'TreasurySweepManager', {
          traceId: evaluation.traceId,
          currency: code,
          amount: payload.amount,
          proofHash: evaluation.proof.hash
        })).catch(() => {});
        return { ...receipt, proof: { algorithm: 'SHA3-512', hash: createTreasuryProofHash(receipt) } };
      } catch {
        continue;
      }
    }

    const rejected = {
      success: false,
      status: 'EXECUTION_ENDPOINT_SOURCE_SILENT',
      executionStatus: 'NO_EXECUTION',
      tenantId,
      currency: code,
      evaluation,
      payload,
      message: 'Policy gates passed, but no treasury execution endpoint accepted the command.'
    };
    await Promise.resolve(broadcastTelemetry(tenantId, 'TREASURY_SWEEP', 'EXECUTION_SOURCE_SILENT', 'TreasurySweepManager', {
      traceId: evaluation.traceId,
      currency: code,
      amount: payload.amount
    })).catch(() => {});
    return { ...rejected, proof: { algorithm: 'SHA3-512', hash: createTreasuryProofHash(rejected) } };
  }

  /**
   * @method runAutonomousSweepCycle
   * @description Evaluates all supported currency balances and executes only policy-cleared sweeps.
   * @param {string} tenantId - Tenant id.
   * @param {Object} [options] - Cycle options.
   * @param {boolean} [options.autoExecute=false] - Whether to execute eligible sweeps.
   * @returns {Promise<Object>} Cycle result.
   */
  async runAutonomousSweepCycle(tenantId = 'GLOBAL_ROOT', options = {}) {
    const status = await this.getTreasuryStatus(tenantId);
    const evaluations = [];
    const receipts = [];

    for (const currency of this.policyMatrix.keys()) {
      const balance = status.balances?.[currency] ?? (currency === 'ZAR' ? status.availableLiquidity : 0);
      const evaluation = this.evaluateLiquidity({
        tenantId,
        currency,
        currentBalance: balance,
        sourceStatus: status.sourceStatus,
        context: options.context || {}
      });
      evaluations.push(evaluation);

      if (options.autoExecute && evaluation.executionEligible) {
        receipts.push(await this.executeSweep({
          tenantId,
          currency,
          currentBalance: balance,
          context: { ...(options.context || {}), sourceStatus: status.sourceStatus },
          approval: options.approval || {}
        }));
      }
    }

    return {
      success: true,
      tenantId,
      status: receipts.length ? 'SWEEPS_EXECUTED' : 'EVALUATED',
      sourceStatus: status.sourceStatus,
      evaluations,
      receipts,
      generatedAt: new Date().toISOString()
    };
  }

  /**
   * @method getMatrixSnapshot
   * @description Returns the current policy and benchmark posture for exports.
   * @returns {Object} Treasury policy snapshot.
   */
  getMatrixSnapshot() {
    return {
      engineVersion: this.engineVersion,
      policyCount: this.policyMatrix.size,
      benchmarkCount: this.benchmarkMatrix.size,
      lastPolicySync: this.lastPolicySync,
      lastBenchmarkSync: this.lastBenchmarkSync,
      liveBackoffActive: Date.now() < this.livePolicyBackoffUntil,
      currencies: Array.from(this.policyMatrix.keys()).sort()
    };
  }
}

const treasurySweepManager = new TreasurySweepManager();

export { TreasurySweepManager };
export default treasurySweepManager;
