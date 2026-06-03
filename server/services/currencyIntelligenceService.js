/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - ZAR-FIRST CURRENCY INTELLIGENCE SERVICE [V1.0.0-SARB-AWARE-FX]                                                            ║
 * ║ [SOUTH AFRICAN DEFAULT CURRENCY | LIVE FX SOURCE STATE | ZAR DISPLAY LAW | SARB THRESHOLD SIGNALS | NO FAKE RATE FALLBACKS]          ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 1.0.0-SARB-AWARE-FX | PRODUCTION READY | MULTI-TENANT CURRENCY CONVERSION READ MODEL                                       ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/services/currencyIntelligenceService.js                                 ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                    ║
 * ║ • Wilson Khanyezi (Founder/CEO) - Mandated Wilsy OS to be South Africa anchored, ZAR-first, and commercially useful across tenants.   ║
 * ║ • AI Engineering (Codex) - ARCHITECTED: Added source-aware live FX conversion without synthetic fallback rates or cross-tenant drift.  ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import crypto from 'node:crypto';

const DEFAULT_BASE_CURRENCY = 'ZAR';
const FX_SOURCE_URL = 'https://api.frankfurter.dev/v2';
const FX_CACHE_TTL_MS = Number(process.env.FX_CACHE_TTL_MS || 15 * 60 * 1000);
const SARB_INTERNAL_REVIEW_THRESHOLD_ZAR = Number(process.env.SARB_INTERNAL_REVIEW_THRESHOLD_ZAR || 1000000);
const fxCache = new Map();

/**
 * @constant {Array<string>}
 * @description Supported executive FX currencies for Wilsy OS operating dashboards.
 * @collaboration ZAR remains the sovereign default while the OS can serve cross-border tenants and prospects.
 */
export const SUPPORTED_EXECUTIVE_CURRENCIES = Object.freeze([
  'ZAR',
  'USD',
  'EUR',
  'GBP',
  'TZS',
  'KES',
  'NGN',
  'GHS',
  'BWP',
  'NAD',
  'MUR',
  'AED'
]);

/**
 * @function stableCurrencyStringify
 * @description Serializes FX packets with deterministic key ordering for repeatable proof hashes.
 * @param {unknown} value - Candidate value.
 * @returns {string} Canonical string.
 * @collaboration Currency conversion receipts must be replayable when exported into audit or board packs.
 */
const stableCurrencyStringify = (value) => {
  if (typeof value === 'undefined') return 'null';
  if (value instanceof Date) return JSON.stringify(value.toISOString());
  if (value === null || typeof value !== 'object') return JSON.stringify(value);
  if (Array.isArray(value)) return `[${value.map(item => stableCurrencyStringify(item)).join(',')}]`;
  return `{${Object.keys(value).sort().map(key => `${JSON.stringify(key)}:${stableCurrencyStringify(value[key])}`).join(',')}}`;
};

/**
 * @function createCurrencyProofHash
 * @description Creates a SHA3-512 proof hash for FX source envelopes.
 * @param {Object} payload - Payload to seal.
 * @returns {string} Uppercase digest.
 * @collaboration FX is money motion intelligence, so every answer needs a tamper-evident receipt.
 */
export const createCurrencyProofHash = (payload = {}) => crypto
  .createHash('sha3-512')
  .update(stableCurrencyStringify(payload))
  .digest('hex')
  .toUpperCase();

/**
 * @function normalizeCurrencyCode
 * @description Normalizes tenant currency inputs into ISO-like uppercase codes.
 * @param {string} value - Raw currency value.
 * @returns {string} Supported currency code.
 * @collaboration Operators may say "ZA", but Wilsy OS stores the correct ISO 4217 code, ZAR.
 */
export const normalizeCurrencyCode = (value = DEFAULT_BASE_CURRENCY) => {
  const code = String(value || DEFAULT_BASE_CURRENCY).trim().toUpperCase();
  if (code === 'ZA') return 'ZAR';
  return SUPPORTED_EXECUTIVE_CURRENCIES.includes(code) ? code : DEFAULT_BASE_CURRENCY;
};

/**
 * @function roundMoney
 * @description Rounds money to institutional two-decimal precision.
 * @param {number|string} value - Amount to round.
 * @returns {number|null} Rounded value or null when not numeric.
 * @collaboration Prevents JavaScript floating point noise from leaking into executive money decisions.
 */
export const roundMoney = (value = 0) => {
  const numeric = Number(value);
  if (!Number.isFinite(numeric)) return null;
  return Math.round((numeric + Number.EPSILON) * 100) / 100;
};

/**
 * @function formatZarAmount
 * @description Formats a value in South African Rand using Wilson's requested Wilsy OS display style.
 * @param {number|string|null} value - Candidate amount.
 * @returns {string} ZAR value such as R100-00, or SOURCE_REQUIRED when absent.
 * @collaboration South African tenants should see Wilsy OS speak in their money first.
 */
export const formatZarAmount = (value = 0) => {
  const rounded = roundMoney(value);
  if (rounded === null) return 'SOURCE_REQUIRED';
  const [whole, cents = '00'] = Math.abs(rounded).toFixed(2).split('.');
  const sign = rounded < 0 ? '-' : '';
  return `${sign}R${Number(whole).toLocaleString('en-ZA')}-${cents}`;
};

/**
 * @function getFxCacheKey
 * @description Builds an in-memory cache key for live FX rates.
 * @param {string} baseCurrency - Base currency.
 * @param {string} quoteCurrency - Quote currency.
 * @returns {string} Cache key.
 * @collaboration Caching protects public FX sources and keeps dashboards fast without inventing rates.
 */
const getFxCacheKey = (baseCurrency, quoteCurrency) => `${baseCurrency}:${quoteCurrency}`;

/**
 * @function getCachedRate
 * @description Returns a still-fresh live rate from memory.
 * @param {string} baseCurrency - Base currency.
 * @param {string} quoteCurrency - Quote currency.
 * @returns {Object|null} Cached rate packet.
 * @collaboration Cached rates are only reused when they came from a live source and remain inside the declared TTL.
 */
const getCachedRate = (baseCurrency, quoteCurrency) => {
  const cached = fxCache.get(getFxCacheKey(baseCurrency, quoteCurrency));
  if (!cached) return null;
  if (Date.now() - cached.cachedAt > FX_CACHE_TTL_MS) return null;
  return cached;
};

/**
 * @function setCachedRate
 * @description Stores a live FX rate packet in memory.
 * @param {string} baseCurrency - Base currency.
 * @param {string} quoteCurrency - Quote currency.
 * @param {Object} packet - Rate packet.
 * @returns {Object} Stored packet.
 * @collaboration Memory cache is intentionally short-lived and source-labelled for audit honesty.
 */
const setCachedRate = (baseCurrency, quoteCurrency, packet = {}) => {
  const cached = {
    ...packet,
    cachedAt: Date.now()
  };
  fxCache.set(getFxCacheKey(baseCurrency, quoteCurrency), cached);
  return cached;
};

/**
 * @function fetchFrankfurterRate
 * @description Fetches a live currency pair rate from Frankfurter's public rates API.
 * @param {string} baseCurrency - Source currency.
 * @param {string} quoteCurrency - Target currency.
 * @returns {Promise<Object>} Live FX rate packet.
 * @collaboration Frankfurter is used because it exposes a no-key API with central-bank-backed daily exchange-rate data.
 */
const fetchFrankfurterRate = async (baseCurrency, quoteCurrency) => {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), Number(process.env.FX_SOURCE_TIMEOUT_MS || 5500));
  try {
    const response = await fetch(`${FX_SOURCE_URL}/rate/${baseCurrency}/${quoteCurrency}`, {
      signal: controller.signal,
      headers: {
        Accept: 'application/json'
      }
    });
    if (!response.ok) {
      const error = new Error(`FX source returned ${response.status}`);
      error.status = response.status;
      throw error;
    }
    const payload = await response.json();
    const rate = Number(payload.rate || payload.rates?.[quoteCurrency]);
    if (!Number.isFinite(rate) || rate <= 0) {
      throw new Error(`FX source did not return a usable ${baseCurrency}/${quoteCurrency} rate.`);
    }
    return {
      rate,
      baseCurrency,
      quoteCurrency,
      sourceStatus: 'FX_SOURCE_LIVE',
      source: 'frankfurter.dev',
      providerDate: payload.date || null,
      fetchedAt: new Date().toISOString()
    };
  } finally {
    clearTimeout(timeout);
  }
};

/**
 * @function getLiveFxRate
 * @description Resolves an FX pair from live source, same-currency identity, or declared cache.
 * @param {Object} params - Rate inputs.
 * @returns {Promise<Object>} Rate packet.
 * @collaboration Currency conversion must be usable, but never at the cost of fake rates.
 */
export const getLiveFxRate = async ({ baseCurrency = DEFAULT_BASE_CURRENCY, quoteCurrency = 'USD' } = {}) => {
  const base = normalizeCurrencyCode(baseCurrency);
  const quote = normalizeCurrencyCode(quoteCurrency);
  if (base === quote) {
    return {
      rate: 1,
      baseCurrency: base,
      quoteCurrency: quote,
      sourceStatus: 'FX_IDENTITY_RATE',
      source: 'wilsy-os',
      providerDate: new Date().toISOString().slice(0, 10),
      fetchedAt: new Date().toISOString()
    };
  }

  const cached = getCachedRate(base, quote);
  if (cached) {
    return {
      ...cached,
      sourceStatus: 'FX_SOURCE_CACHE'
    };
  }

  try {
    const live = await fetchFrankfurterRate(base, quote);
    return setCachedRate(base, quote, live);
  } catch (error) {
    return {
      rate: null,
      baseCurrency: base,
      quoteCurrency: quote,
      sourceStatus: 'FX_SOURCE_SILENT',
      source: 'frankfurter.dev',
      fetchedAt: new Date().toISOString(),
      error: error.message
    };
  }
};

/**
 * @function buildSarbReviewSignal
 * @description Builds an internal South African FX review signal for large ZAR-based conversions.
 * @param {Object} params - Review inputs.
 * @returns {Object} Review packet.
 * @collaboration This is not legal advice; it gives executives a conservative operating-control warning before large FX motion.
 */
export const buildSarbReviewSignal = ({ amount = 0, fromCurrency = DEFAULT_BASE_CURRENCY, toCurrency = 'USD', rate = null } = {}) => {
  const from = normalizeCurrencyCode(fromCurrency);
  const to = normalizeCurrencyCode(toCurrency);
  const numericAmount = Number(amount || 0);
  const zarExposure = from === 'ZAR'
    ? numericAmount
    : to === 'ZAR' && rate
      ? numericAmount * Number(rate)
      : null;
  const reviewRequired = Number(zarExposure || 0) >= SARB_INTERNAL_REVIEW_THRESHOLD_ZAR;
  return {
    status: reviewRequired ? 'INTERNAL_FX_REVIEW_REQUIRED' : 'STANDARD_FX_MONITORING',
    thresholdZar: SARB_INTERNAL_REVIEW_THRESHOLD_ZAR,
    zarExposure: zarExposure === null ? null : roundMoney(zarExposure),
    fromCurrency: from,
    toCurrency: to,
    note: reviewRequired
      ? 'Large ZAR exposure should be reviewed before external payment or treasury movement.'
      : 'Conversion is below the internal ZAR review threshold.'
  };
};

/**
 * @function convertCurrency
 * @description Converts money using a source-labelled FX rate and returns display-ready ZAR values.
 * @param {Object} params - Conversion inputs.
 * @returns {Promise<Object>} Conversion packet.
 * @collaboration Lets a tenant view ZAR, USD, TZS and other operating currencies without hiding source gaps.
 */
export const convertCurrency = async ({
  amount = 0,
  fromCurrency = DEFAULT_BASE_CURRENCY,
  toCurrency = 'USD',
  tenantId = 'GLOBAL_ROOT'
} = {}) => {
  const numericAmount = Number(amount || 0);
  const baseCurrency = normalizeCurrencyCode(fromCurrency);
  const quoteCurrency = normalizeCurrencyCode(toCurrency);
  const ratePacket = await getLiveFxRate({ baseCurrency, quoteCurrency });
  const convertedAmount = ratePacket.rate ? roundMoney(numericAmount * Number(ratePacket.rate)) : null;
  const packet = {
    success: Boolean(ratePacket.rate),
    tenantId,
    sourceStatus: ratePacket.sourceStatus,
    source: ratePacket.source,
    amount: roundMoney(numericAmount),
    fromCurrency: baseCurrency,
    toCurrency: quoteCurrency,
    convertedAmount,
    rate: ratePacket.rate,
    providerDate: ratePacket.providerDate || null,
    fetchedAt: ratePacket.fetchedAt,
    display: {
      source: baseCurrency === 'ZAR' ? formatZarAmount(numericAmount) : `${baseCurrency} ${roundMoney(numericAmount)?.toLocaleString('en-ZA')}`,
      converted: convertedAmount === null
        ? 'FX_SOURCE_REQUIRED'
        : quoteCurrency === 'ZAR'
          ? formatZarAmount(convertedAmount)
          : `${quoteCurrency} ${convertedAmount.toLocaleString('en-ZA', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
    },
    sarbReview: buildSarbReviewSignal({
      amount: numericAmount,
      fromCurrency: baseCurrency,
      toCurrency: quoteCurrency,
      rate: ratePacket.rate
    })
  };
  return {
    ...packet,
    proofHash: createCurrencyProofHash(packet)
  };
};

export default {
  SUPPORTED_EXECUTIVE_CURRENCIES,
  normalizeCurrencyCode,
  roundMoney,
  formatZarAmount,
  getLiveFxRate,
  buildSarbReviewSignal,
  convertCurrency,
  createCurrencyProofHash
};
