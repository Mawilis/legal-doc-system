/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - SOVEREIGN CURRENCY INTELLIGENCE ENGINE [V4.0.0-BIBLICAL-PRODUCTION]                                                       ║
 * ║ [ISO CURRENCY REGISTRY | ZAR DEFAULT | FX GRAPH RESOLUTION | SARB/FICA SIGNALS | VaR | STRESS TESTS | ENV-OWNED RATE SOURCES]       ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 4.0.0-BIBLICAL-PRODUCTION | PRODUCTION READY | GLOBAL MULTI-CURRENCY OPERATING INTELLIGENCE                               ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/utils/currencyIntelligence.js                                            ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                    ║
 * ║ • Wilson Khanyezi (Founder/CEO) - Rejected prototype FX logic and mandated all-currency, South-African-first production algorithms. ║
 * ║ • AI Engineering (Codex) - ARCHITECTED: Rebuilt as ISO-wide currency registry, FX graph resolver, compliance scorer and risk engine. ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import crypto from 'crypto';
import https from 'https';
import path from 'path';
import { performance } from 'perf_hooks';
import { fileURLToPath } from 'url';
import dotenv from 'dotenv';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

dotenv.config({ path: path.resolve(__dirname, '../.env') });

const ENGINE_VERSION = 'V4.0.0-BIBLICAL-PRODUCTION';
const DEFAULT_LOCALE = 'en-ZA';
const DEFAULT_BASE_CURRENCY = 'ZAR';
const RATE_CACHE = new Map();

const FALLBACK_ISO_CURRENCY_CODES = Object.freeze([
  'AED', 'AFN', 'ALL', 'AMD', 'ANG', 'AOA', 'ARS', 'AUD', 'AWG', 'AZN',
  'BAM', 'BBD', 'BDT', 'BGN', 'BHD', 'BIF', 'BMD', 'BND', 'BOB', 'BOV',
  'BRL', 'BSD', 'BTN', 'BWP', 'BYN', 'BZD', 'CAD', 'CDF', 'CHE', 'CHF',
  'CHW', 'CLF', 'CLP', 'CNY', 'COP', 'COU', 'CRC', 'CUC', 'CUP', 'CVE',
  'CZK', 'DJF', 'DKK', 'DOP', 'DZD',
  'EGP', 'ERN', 'ETB', 'EUR', 'FJD', 'FKP', 'GBP', 'GEL', 'GHS', 'GIP',
  'GMD', 'GNF', 'GTQ', 'GYD', 'HKD', 'HNL', 'HRK', 'HTG', 'HUF', 'IDR',
  'ILS', 'INR', 'IQD', 'IRR', 'ISK', 'JMD', 'JOD', 'JPY', 'KES', 'KGS',
  'KHR', 'KMF', 'KPW', 'KRW', 'KWD', 'KYD', 'KZT', 'LAK', 'LBP', 'LKR',
  'LRD', 'LSL', 'LYD', 'MAD', 'MDL', 'MGA', 'MKD', 'MMK', 'MNT', 'MOP',
  'MRU', 'MUR', 'MVR', 'MWK', 'MXN', 'MXV', 'MYR', 'MZN', 'NAD', 'NGN', 'NIO',
  'NOK', 'NPR', 'NZD', 'OMR', 'PAB', 'PEN', 'PGK', 'PHP', 'PKR', 'PLN',
  'PYG', 'QAR', 'RON', 'RSD', 'RUB', 'RWF', 'SAR', 'SBD', 'SCR', 'SDG',
  'SEK', 'SGD', 'SHP', 'SLE', 'SLL', 'SOS', 'SRD', 'SSP', 'STN', 'SVC',
  'SYP', 'SZL', 'THB', 'TJS', 'TMT', 'TND', 'TOP', 'TRY', 'TTD', 'TWD',
  'TZS', 'UAH', 'UGX', 'USD', 'USN', 'UYI', 'UYU', 'UYW', 'UZS', 'VED',
  'VES', 'VND', 'VUV', 'WST', 'XAF', 'XAG', 'XAU', 'XBA', 'XBB', 'XBC',
  'XBD', 'XCD', 'XCG', 'XDR', 'XOF', 'XPD', 'XPF', 'XPT', 'XSU', 'XTS',
  'XUA', 'XXX', 'YER', 'ZAR', 'ZMW', 'ZWG', 'ZWL'
]);

const AFRICAN_CURRENCY_CODES = new Set([
  'AOA', 'BIF', 'BWP', 'CDF', 'CVE', 'DJF', 'DZD', 'EGP', 'ERN', 'ETB',
  'GHS', 'GMD', 'GNF', 'KES', 'KMF', 'LRD', 'LSL', 'LYD', 'MAD', 'MGA',
  'MRU', 'MUR', 'MWK', 'MZN', 'NAD', 'NGN', 'RWF', 'SCR', 'SDG', 'SHP',
  'SLE', 'SLL', 'SOS', 'SSP', 'STN', 'SZL', 'TND', 'TZS', 'UGX', 'XAF',
  'XOF', 'ZAR', 'ZMW', 'ZWG', 'ZWL'
]);

const MAJOR_RESERVE_CURRENCIES = new Set(['USD', 'EUR', 'GBP', 'JPY', 'CHF', 'CAD', 'AUD', 'NZD', 'CNY', 'SGD', 'HKD']);
const PEGGED_OR_MANAGED_CURRENCIES = new Set(['AED', 'BHD', 'DKK', 'HKD', 'JOD', 'KWD', 'OMR', 'PAB', 'QAR', 'SAR', 'XAF', 'XCD', 'XOF', 'XPF']);
const HEIGHTENED_DILIGENCE_CURRENCIES = new Set(['ARS', 'IRR', 'KPW', 'LBP', 'MMK', 'RUB', 'SDG', 'SSP', 'SYP', 'TRY', 'VES', 'YER', 'ZWG', 'ZWL']);
const NON_CASH_ISO_UNITS = new Set([
  'BOV', 'CHE', 'CHW', 'CLF', 'COU', 'MXV', 'USN', 'UYI', 'UYW', 'VED',
  'XAG', 'XAU', 'XBA', 'XBB', 'XBC', 'XBD', 'XDR', 'XPD', 'XPT', 'XSU',
  'XTS', 'XUA', 'XXX'
]);
const ISO_UNIT_EXPONENT_OVERRIDES = Object.freeze({
  CLF: 4,
  UYW: 4,
  XAG: 0,
  XAU: 0,
  XBA: 0,
  XBB: 0,
  XBC: 0,
  XBD: 0,
  XDR: 0,
  XPD: 0,
  XPT: 0,
  XSU: 0,
  XTS: 0,
  XUA: 0,
  XXX: 0
});

/**
 * @function readCurrencyEnv
 * @description Reads the first populated environment key from server/.env.
 * @param {Array<string>} keys - Candidate environment keys.
 * @param {string|number|boolean} fallback - Non-sensitive fallback.
 * @returns {string|number|boolean} Environment value or fallback.
 * @collaboration Keeps currency configuration deployment-owned instead of hardcoded into Wilsy OS source files.
 */
export function readCurrencyEnv(keys = [], fallback = '') {
  const foundKey = keys.find(key => process.env[key] !== undefined && process.env[key] !== '');
  return foundKey ? process.env[foundKey] : fallback;
}

/**
 * @function requireCurrencyEnv
 * @description Resolves a required environment value from server/.env.
 * @param {Array<string>} keys - Candidate environment keys.
 * @returns {string} Required environment value.
 * @collaboration Makes production currency security fail closed when key material is absent.
 */
export function requireCurrencyEnv(keys = []) {
  const value = readCurrencyEnv(keys, '');
  if (!value) throw new Error(`Missing required server/.env key: ${keys.join(' or ')}`);
  return String(value);
}

/**
 * @function readCurrencyNumberEnv
 * @description Reads a numeric environment value with a bounded fallback.
 * @param {Array<string>} keys - Candidate environment keys.
 * @param {number} fallback - Numeric fallback.
 * @returns {number} Parsed number.
 * @collaboration Keeps thresholds, cache TTLs and fee policy tunable without editing source.
 */
export function readCurrencyNumberEnv(keys = [], fallback = 0) {
  const value = Number(readCurrencyEnv(keys, fallback));
  return Number.isFinite(value) ? value : fallback;
}

/**
 * @function readCurrencyBooleanEnv
 * @description Reads a boolean environment value.
 * @param {Array<string>} keys - Candidate environment keys.
 * @param {boolean} fallback - Boolean fallback.
 * @returns {boolean} Parsed boolean.
 * @collaboration Allows production operators to toggle currency safeguards from server/.env.
 */
export function readCurrencyBooleanEnv(keys = [], fallback = false) {
  const value = String(readCurrencyEnv(keys, fallback ? 'true' : 'false')).toLowerCase();
  return ['1', 'true', 'yes', 'on'].includes(value);
}

/**
 * @function readCurrencyListEnv
 * @description Reads a comma-separated currency-code list from server/.env.
 * @param {string} key - Environment key.
 * @param {Array<string>} fallback - Fallback list.
 * @returns {Array<string>} Normalized currency codes.
 * @collaboration Lets Wilsy OS deployments restrict or extend currency scope without creating new modules.
 */
export function readCurrencyListEnv(key, fallback = []) {
  const value = process.env[key];
  if (!value) return fallback;
  return value.split(',').map(item => item.trim().toUpperCase()).filter(Boolean);
}

/**
 * @function preciseRound
 * @description Rounds numeric values through integer-safe precision.
 * @param {number|string} value - Numeric value.
 * @param {number} decimals - Decimal precision.
 * @returns {number} Rounded value.
 * @collaboration Keeps finance calculations deterministic instead of leaking JavaScript floating-point drift.
 */
export function preciseRound(value = 0, decimals = 2) {
  const numeric = Number(value);
  if (!Number.isFinite(numeric)) return 0;
  const factor = 10 ** decimals;
  return Math.round((numeric + Number.EPSILON) * factor) / factor;
}

/**
 * @function stableCurrencyStringify
 * @description Serializes currency packets with deterministic key ordering.
 * @param {unknown} value - Value to serialize.
 * @returns {string} Canonical JSON string.
 * @collaboration Currency proofs must be reproducible for audit replay and boardroom exports.
 */
export function stableCurrencyStringify(value) {
  if (typeof value === 'undefined') return 'null';
  if (value instanceof Date) return JSON.stringify(value.toISOString());
  if (value === null || typeof value !== 'object') return JSON.stringify(value);
  if (Array.isArray(value)) return `[${value.map(item => stableCurrencyStringify(item)).join(',')}]`;
  return `{${Object.keys(value).sort().map(key => `${JSON.stringify(key)}:${stableCurrencyStringify(value[key])}`).join(',')}}`;
}

/**
 * @function createCurrencyProofHash
 * @description Creates a SHA3-512 proof hash for currency intelligence packets.
 * @param {Object} payload - Payload to seal.
 * @returns {string} Uppercase SHA3-512 digest.
 * @collaboration Gives every FX calculation and risk packet court-ready reproducibility.
 */
export function createCurrencyProofHash(payload = {}) {
  return crypto.createHash('sha3-512').update(stableCurrencyStringify(payload)).digest('hex').toUpperCase();
}

/**
 * @function getRuntimeCurrencyCodes
 * @description Builds the supported currency universe from Node/ICU and ISO fallback units.
 * @returns {Array<string>} Sorted currency codes.
 * @collaboration Wilsy OS builds once and supports the runtime ISO currency universe, not a small prototype list.
 */
export function getRuntimeCurrencyCodes() {
  const runtimeCodes = typeof Intl.supportedValuesOf === 'function'
    ? Intl.supportedValuesOf('currency')
    : [];
  return [...new Set([...runtimeCodes, ...FALLBACK_ISO_CURRENCY_CODES])].sort();
}

const SUPPORTED_CURRENCY_CODES = Object.freeze(getRuntimeCurrencyCodes());
const SUPPORTED_CURRENCY_SET = new Set(SUPPORTED_CURRENCY_CODES);

/**
 * @function normalizeCurrencyCode
 * @description Normalizes a currency code into uppercase ISO-like format.
 * @param {string} currency - Candidate currency code.
 * @returns {string} Normalized currency code.
 * @collaboration Keeps tenant-entered currencies consistent across billing, treasury and executive intelligence.
 */
export function normalizeCurrencyCode(currency = DEFAULT_BASE_CURRENCY) {
  return String(currency || DEFAULT_BASE_CURRENCY).trim().toUpperCase();
}

/**
 * @function isSupportedCurrency
 * @description Determines whether Wilsy OS recognizes a currency code.
 * @param {string} currency - Currency code.
 * @returns {boolean} True when supported.
 * @collaboration Gives every module the same all-currency validation contract.
 */
export function isSupportedCurrency(currency = DEFAULT_BASE_CURRENCY) {
  return SUPPORTED_CURRENCY_SET.has(normalizeCurrencyCode(currency));
}

/**
 * @function assertSupportedCurrency
 * @description Validates and returns a supported currency code.
 * @param {string} currency - Currency code.
 * @returns {string} Supported currency code.
 * @throws {Error} When currency is unsupported.
 * @collaboration Fails currency commands early before money movement or reporting can drift.
 */
export function assertSupportedCurrency(currency = DEFAULT_BASE_CURRENCY) {
  const code = normalizeCurrencyCode(currency);
  if (!/^[A-Z]{3}$/.test(code) || !isSupportedCurrency(code)) {
    throw new Error(`Unsupported currency: ${currency}. Wilsy OS supports ${SUPPORTED_CURRENCY_CODES.length} ISO/runtime currencies.`);
  }
  return code;
}

/**
 * @function getCurrencyDisplayName
 * @description Resolves a human-readable currency name using Intl.DisplayNames.
 * @param {string} currency - Currency code.
 * @returns {string} Display name.
 * @collaboration Makes global tenant currency labels readable without maintaining a hand-written name table.
 */
export function getCurrencyDisplayName(currency = DEFAULT_BASE_CURRENCY) {
  const code = assertSupportedCurrency(currency);
  try {
    const displayNames = new Intl.DisplayNames([DEFAULT_LOCALE, 'en'], { type: 'currency' });
    return displayNames.of(code) || code;
  } catch {
    return code;
  }
}

/**
 * @function getCurrencyExponent
 * @description Resolves the ISO minor-unit exponent from Intl.NumberFormat.
 * @param {string} currency - Currency code.
 * @returns {number} Minor-unit exponent.
 * @collaboration Avoids maintaining brittle cent/yen/fils tables in source while supporting all runtime currencies.
 */
export function getCurrencyExponent(currency = DEFAULT_BASE_CURRENCY) {
  const code = assertSupportedCurrency(currency);
  if (Object.prototype.hasOwnProperty.call(ISO_UNIT_EXPONENT_OVERRIDES, code)) {
    return ISO_UNIT_EXPONENT_OVERRIDES[code];
  }
  try {
    return new Intl.NumberFormat(DEFAULT_LOCALE, { style: 'currency', currency: code })
      .resolvedOptions()
      .maximumFractionDigits;
  } catch {
    return 2;
  }
}

/**
 * @function toMinorUnits
 * @description Converts display money into integer minor units.
 * @param {number|string} value - Display amount.
 * @param {string} currency - Currency code.
 * @returns {number} Integer minor units.
 * @collaboration Gives Wilsy OS invoice and FX math deterministic integer foundations.
 */
export function toMinorUnits(value = 0, currency = DEFAULT_BASE_CURRENCY) {
  const exponent = getCurrencyExponent(currency);
  return Math.round(Number(value || 0) * (10 ** exponent));
}

/**
 * @function fromMinorUnits
 * @description Converts integer minor units into display money.
 * @param {number|string} value - Minor-unit value.
 * @param {string} currency - Currency code.
 * @returns {number} Display amount.
 * @collaboration Preserves deterministic money values while exposing normal business amounts.
 */
export function fromMinorUnits(value = 0, currency = DEFAULT_BASE_CURRENCY) {
  const exponent = getCurrencyExponent(currency);
  return preciseRound(Number(value || 0) / (10 ** exponent), exponent);
}

/**
 * @function formatWilsyMoney
 * @description Formats money with South-African-first display rules.
 * @param {number|string} amount - Amount.
 * @param {string} currency - Currency code.
 * @returns {string} Formatted amount.
 * @collaboration ZAR is Wilsy OS home currency and renders as R100-00 for unmistakable South African business use.
 */
export function formatWilsyMoney(amount = 0, currency = DEFAULT_BASE_CURRENCY) {
  const code = assertSupportedCurrency(currency);
  const numeric = Number(amount || 0);
  if (code === 'ZAR') {
    const exponent = getCurrencyExponent(code);
    const minor = Math.abs(toMinorUnits(numeric, code));
    const sign = numeric < 0 ? '-' : '';
    const centsFactor = 10 ** exponent;
    const whole = Math.floor(minor / centsFactor).toLocaleString('en-ZA');
    const fraction = exponent ? String(minor % centsFactor).padStart(exponent, '0') : '';
    return `${sign}R${whole}${fraction ? `-${fraction}` : ''}`;
  }
  const exponent = getCurrencyExponent(code);
  try {
    return new Intl.NumberFormat(DEFAULT_LOCALE, {
      style: 'currency',
      currency: code,
      minimumFractionDigits: exponent,
      maximumFractionDigits: exponent
    }).format(numeric);
  } catch {
    return `${code} ${numeric.toLocaleString('en-ZA', {
      minimumFractionDigits: exponent,
      maximumFractionDigits: exponent
    })}`;
  }
}

/**
 * @function getCurrencyProfile
 * @description Builds an operational currency profile for one currency.
 * @param {string} currency - Currency code.
 * @returns {Object} Currency profile.
 * @collaboration Gives dashboards and algorithms a single complete profile shape for all supported currencies.
 */
export function getCurrencyProfile(currency = DEFAULT_BASE_CURRENCY) {
  const code = assertSupportedCurrency(currency);
  return {
    code,
    name: getCurrencyDisplayName(code),
    exponent: getCurrencyExponent(code),
    africanCurrency: AFRICAN_CURRENCY_CODES.has(code),
    reserveCurrency: MAJOR_RESERVE_CURRENCIES.has(code),
    peggedOrManaged: PEGGED_OR_MANAGED_CURRENCIES.has(code),
    heightenedDiligence: HEIGHTENED_DILIGENCE_CURRENCIES.has(code),
    nonCashIsoUnit: NON_CASH_ISO_UNITS.has(code),
    liquidityTier: inferLiquidityTier(code),
    volatilityBaseline: inferCurrencyVolatility(code)
  };
}

/**
 * @function getSupportedCurrencies
 * @description Returns the full Wilsy OS currency registry.
 * @returns {Array<Object>} Currency profiles.
 * @collaboration Exposes all supported currencies to tenant onboarding, billing and treasury without creating new files.
 */
export function getSupportedCurrencies() {
  return SUPPORTED_CURRENCY_CODES.map(code => getCurrencyProfile(code));
}

/**
 * @function resolveCurrencyEncryptionKey
 * @description Resolves AES-256-GCM encryption material from server/.env.
 * @returns {Buffer} Encryption key buffer.
 * @collaboration Currency evidence encryption must use stable env-owned keys, never generated runtime secrets.
 */
export function resolveCurrencyEncryptionKey() {
  const key = requireCurrencyEnv(['ENCRYPTION_KEY', 'FINANCIAL_ENCRYPTION_KEY']);
  if (/^[a-f0-9]{64}$/i.test(key)) return Buffer.from(key, 'hex');
  const base64 = Buffer.from(key, 'base64');
  if (base64.length === 32) return base64;
  throw new Error('Currency encryption key must be 32 bytes as 64 hex characters or base64.');
}

const CURRENCY_CONSTANTS = Object.freeze({
  ENGINE_VERSION,
  DEFAULT_CURRENCY: normalizeCurrencyCode(readCurrencyEnv(['DEFAULT_CURRENCY', 'BASE_CURRENCY'], DEFAULT_BASE_CURRENCY)),
  BASE_CURRENCY: normalizeCurrencyCode(readCurrencyEnv(['BASE_CURRENCY', 'DEFAULT_CURRENCY'], DEFAULT_BASE_CURRENCY)),
  CACHE_TTL_SECONDS: readCurrencyNumberEnv(['FOREX_CACHE_TTL', 'CURRENCY_CACHE_TTL_SECONDS', 'CACHE_TTL_DEFAULT'], 300),
  REQUEST_TIMEOUT_MS: readCurrencyNumberEnv(['FOREX_REQUEST_TIMEOUT_MS', 'API_TIMEOUT_MS'], 8000),
  SARB_THRESHOLD_ZAR: readCurrencyNumberEnv(['SARB_REPORTING_THRESHOLD', 'FICA_THRESHOLD'], 1000000),
  FICA_THRESHOLD_ZAR: readCurrencyNumberEnv(['FICA_THRESHOLD', 'SARB_REPORTING_THRESHOLD'], 1000000),
  REPORTING_THRESHOLD_ZAR: readCurrencyNumberEnv(['CURRENCY_REPORTING_THRESHOLD_ZAR', 'BREACH_REPORTING_THRESHOLD'], 50000),
  SUPPORTED_CURRENCIES: SUPPORTED_CURRENCY_CODES,
  OPEN_EXCHANGE_RATES_APP_ID: String(readCurrencyEnv(['OPENEXCHANGERATES_APP_ID', 'OPEN_EXCHANGE_RATES_APP_ID'], '')),
  STRICT_SOURCE_MODE: readCurrencyBooleanEnv(['CURRENCY_STRICT_SOURCE_MODE', 'STRICT_CURRENCY_SOURCE_MODE'], false),
  DEFAULT_FEE_BPS: readCurrencyNumberEnv(['CURRENCY_CONVERSION_FEE_BPS', 'FX_CONVERSION_FEE_BPS'], 100),
  AFRICAN_FEE_MULTIPLIER: readCurrencyNumberEnv(['AFRICAN_CURRENCY_FEE_MULTIPLIER'], 1.35),
  MIN_FEE_ZAR: readCurrencyNumberEnv(['CURRENCY_MIN_FEE_ZAR'], 10),
  MAX_FEE_ZAR: readCurrencyNumberEnv(['CURRENCY_MAX_FEE_ZAR'], 1000)
});

/**
 * @function quantumEncryptData
 * @description Encrypts sensitive currency intelligence packets with AES-256-GCM.
 * @param {unknown} data - Payload to encrypt.
 * @returns {{encrypted:string,iv:string,tag:string,algorithm:string,keySource:string}|null} Encrypted packet.
 * @collaboration Protects FX snapshots and risk reports when they are exported or stored.
 */
export function quantumEncryptData(data) {
  try {
    const iv = crypto.randomBytes(16);
    const cipher = crypto.createCipheriv('aes-256-gcm', resolveCurrencyEncryptionKey(), iv);
    const encrypted = Buffer.concat([cipher.update(JSON.stringify(data), 'utf8'), cipher.final()]);
    const tag = cipher.getAuthTag();
    return {
      encrypted: encrypted.toString('hex'),
      iv: iv.toString('hex'),
      tag: tag.toString('hex'),
      algorithm: 'AES-256-GCM',
      keySource: 'server/.env'
    };
  } catch (error) {
    console.error('[CURRENCY-ENCRYPTION-FRACTURE]', error.message);
    return null;
  }
}

/**
 * @function quantumDecryptData
 * @description Decrypts AES-256-GCM currency intelligence packets.
 * @param {{encrypted:string,iv:string,tag:string}} encryptedData - Encrypted packet.
 * @returns {Object|null} Decrypted payload.
 * @collaboration Gives treasury, audit and board exports a reversible encrypted evidence path.
 */
export function quantumDecryptData(encryptedData) {
  try {
    const decipher = crypto.createDecipheriv(
      'aes-256-gcm',
      resolveCurrencyEncryptionKey(),
      Buffer.from(encryptedData.iv, 'hex')
    );
    decipher.setAuthTag(Buffer.from(encryptedData.tag, 'hex'));
    const decrypted = Buffer.concat([
      decipher.update(Buffer.from(encryptedData.encrypted, 'hex')),
      decipher.final()
    ]);
    return JSON.parse(decrypted.toString('utf8'));
  } catch (error) {
    console.error('[CURRENCY-DECRYPTION-FRACTURE]', error.message);
    return null;
  }
}

/**
 * @function buildCacheKey
 * @description Builds a deterministic cache key for an FX request.
 * @param {string} baseCurrency - Base currency.
 * @param {Array<string>} targetCurrencies - Target currencies.
 * @returns {string} Cache key.
 * @collaboration Keeps live rate calls efficient without mixing tenant currency requests.
 */
export function buildCacheKey(baseCurrency, targetCurrencies = []) {
  return `${normalizeCurrencyCode(baseCurrency)}:${targetCurrencies.map(normalizeCurrencyCode).sort().join(',')}`;
}

/**
 * @function getCachedRates
 * @description Reads a non-expired FX snapshot from the in-memory cache.
 * @param {string} cacheKey - Cache key.
 * @returns {Object|null} Cached snapshot or null.
 * @collaboration Prevents unnecessary provider calls while preserving source freshness.
 */
export function getCachedRates(cacheKey) {
  const cached = RATE_CACHE.get(cacheKey);
  if (!cached) return null;
  const ageMs = Date.now() - cached.cachedAt;
  if (ageMs > CURRENCY_CONSTANTS.CACHE_TTL_SECONDS * 1000) {
    RATE_CACHE.delete(cacheKey);
    return null;
  }
  return {
    ...cached.snapshot,
    cache: {
      hit: true,
      ageMs,
      ttlSeconds: CURRENCY_CONSTANTS.CACHE_TTL_SECONDS
    }
  };
}

/**
 * @function setCachedRates
 * @description Stores an FX snapshot in cache.
 * @param {string} cacheKey - Cache key.
 * @param {Object} snapshot - FX snapshot.
 * @returns {void}
 * @collaboration Gives repeated dashboard reads fast, deterministic rate evidence.
 */
export function setCachedRates(cacheKey, snapshot) {
  RATE_CACHE.set(cacheKey, { cachedAt: Date.now(), snapshot });
}

/**
 * @function fetchJson
 * @description Fetches JSON from a configured HTTPS endpoint.
 * @param {URL|string} url - URL to fetch.
 * @param {number} timeoutMs - Request timeout.
 * @returns {Promise<Object>} Parsed JSON.
 * @collaboration Isolates outbound provider calls and keeps secret-bearing URLs out of logs.
 */
export function fetchJson(url, timeoutMs = CURRENCY_CONSTANTS.REQUEST_TIMEOUT_MS) {
  return new Promise((resolve, reject) => {
    const request = https.get(url, { timeout: timeoutMs }, response => {
      let data = '';
      response.on('data', chunk => {
        data += chunk;
      });
      response.on('end', () => {
        if (response.statusCode < 200 || response.statusCode >= 300) {
          reject(new Error(`Provider HTTP ${response.statusCode}`));
          return;
        }
        try {
          resolve(JSON.parse(data));
        } catch (error) {
          reject(new Error(`Provider JSON parse failed: ${error.message}`));
        }
      });
    });
    request.on('timeout', () => {
      request.destroy(new Error(`Provider timeout after ${timeoutMs}ms`));
    });
    request.on('error', reject);
  });
}

/**
 * @function createRateEdge
 * @description Creates a validated FX graph edge.
 * @param {string} fromCurrency - Source currency.
 * @param {string} toCurrency - Target currency.
 * @param {number} rate - Exchange rate.
 * @param {Object} metadata - Source metadata.
 * @returns {Object|null} Rate edge or null when invalid.
 * @collaboration Turns every rate source into one common graph primitive.
 */
export function createRateEdge(fromCurrency, toCurrency, rate, metadata = {}) {
  const from = assertSupportedCurrency(fromCurrency);
  const to = assertSupportedCurrency(toCurrency);
  const numericRate = Number(rate);
  if (!Number.isFinite(numericRate) || numericRate <= 0) return null;
  return {
    from,
    to,
    rate: numericRate,
    source: metadata.source || 'UNKNOWN',
    sourceStatus: metadata.sourceStatus || 'LIVE',
    confidence: Math.max(0.05, Math.min(1, Number(metadata.confidence ?? 0.75))),
    observedAt: metadata.observedAt || new Date().toISOString(),
    latencyMs: metadata.latencyMs || 0
  };
}

/**
 * @function addRateEdge
 * @description Adds a direct and reciprocal edge to the FX graph.
 * @param {Map<string,Array<Object>>} graph - FX graph.
 * @param {Object} edge - Rate edge.
 * @returns {void}
 * @collaboration Ensures every declared rate can power inverse and cross-currency calculations.
 */
export function addRateEdge(graph, edge) {
  if (!edge) return;
  if (!graph.has(edge.from)) graph.set(edge.from, []);
  graph.get(edge.from).push(edge);
  if (!graph.has(edge.to)) graph.set(edge.to, []);
  graph.get(edge.to).push({
    ...edge,
    from: edge.to,
    to: edge.from,
    rate: 1 / edge.rate,
    source: `${edge.source}:RECIPROCAL`,
    confidence: Math.max(0.05, edge.confidence * 0.98)
  });
}

/**
 * @function buildRateGraph
 * @description Builds an FX graph from rate edges.
 * @param {Array<Object>} edges - Rate edges.
 * @returns {Map<string,Array<Object>>} FX graph.
 * @collaboration Gives Wilsy OS graph-based conversion instead of one-hop prototype conversion.
 */
export function buildRateGraph(edges = []) {
  const graph = new Map();
  edges.forEach(edge => addRateEdge(graph, edge));
  return graph;
}

/**
 * @function resolveRatePath
 * @description Resolves the highest-confidence conversion path between two currencies.
 * @param {Map<string,Array<Object>>} graph - FX graph.
 * @param {string} fromCurrency - Source currency.
 * @param {string} toCurrency - Target currency.
 * @returns {Object|null} Resolved path packet.
 * @collaboration Enables ZAR-cross, USD-cross and provider/env hybrid conversions without hardcoded pair logic.
 */
export function resolveRatePath(graph, fromCurrency, toCurrency) {
  const from = assertSupportedCurrency(fromCurrency);
  const to = assertSupportedCurrency(toCurrency);
  if (from === to) {
    return { rate: 1, confidence: 1, path: [from], sources: ['IDENTITY'], hops: [] };
  }

  const queue = [{ currency: from, rate: 1, confidence: 1, path: [from], hops: [], cost: 0 }];
  const bestCost = new Map([[from, 0]]);

  while (queue.length) {
    queue.sort((left, right) => left.cost - right.cost);
    const current = queue.shift();
    if (current.currency === to) {
      return {
        rate: current.rate,
        confidence: preciseRound(current.confidence, 4),
        path: current.path,
        sources: [...new Set(current.hops.map(edge => edge.source))],
        hops: current.hops
      };
    }

    const edges = graph.get(current.currency) || [];
    edges.forEach(edge => {
      if (current.path.includes(edge.to)) return;
      const nextConfidence = current.confidence * edge.confidence;
      const nextCost = current.cost + 1 + (1 - edge.confidence);
      if (bestCost.has(edge.to) && bestCost.get(edge.to) <= nextCost) return;
      bestCost.set(edge.to, nextCost);
      queue.push({
        currency: edge.to,
        rate: current.rate * edge.rate,
        confidence: nextConfidence,
        path: [...current.path, edge.to],
        hops: [...current.hops, edge],
        cost: nextCost
      });
    });
  }

  return null;
}

/**
 * @function readDeclaredFxEdges
 * @description Reads every BASE_TO_TARGET FX rate declared in server/.env.
 * @returns {Array<Object>} Env-backed rate edges.
 * @collaboration Supports all configured currency pairs without embedding a single fake rate in source code.
 */
export function readDeclaredFxEdges() {
  const edges = [];
  Object.entries(process.env).forEach(([key, value]) => {
    const match = key.match(/^([A-Z]{3})_TO_([A-Z]{3})$/);
    if (!match) return;
    const [, from, to] = match;
    if (!isSupportedCurrency(from) || !isSupportedCurrency(to)) return;
    const edge = createRateEdge(from, to, Number(value), {
      source: 'server/.env',
      sourceStatus: 'ENV_DECLARED',
      confidence: 0.72
    });
    if (edge) edges.push(edge);
  });
  return edges;
}

/**
 * @function fetchFromOpenExchangeRates
 * @description Fetches provider rates from OpenExchangeRates when server/.env has an app id.
 * @param {string} requestedBaseCurrency - Requested base currency.
 * @param {Array<string>} targetCurrencies - Target currencies.
 * @returns {Promise<Array<Object>>} Provider rate edges.
 * @collaboration Isolates third-party FX dependency behind one adapter and never logs provider keys.
 */
export async function fetchFromOpenExchangeRates(requestedBaseCurrency = DEFAULT_BASE_CURRENCY, targetCurrencies = []) {
  const appId = CURRENCY_CONSTANTS.OPEN_EXCHANGE_RATES_APP_ID;
  if (!appId) return [];

  const startedAt = performance.now();
  const symbols = [...new Set([requestedBaseCurrency, ...targetCurrencies, CURRENCY_CONSTANTS.BASE_CURRENCY, 'USD'])]
    .map(assertSupportedCurrency)
    .join(',');
  const url = new URL('https://openexchangerates.org/api/latest.json');
  url.searchParams.set('app_id', appId);
  url.searchParams.set('symbols', symbols);

  const payload = await fetchJson(url);
  const providerBase = assertSupportedCurrency(payload.base || 'USD');
  const observedAt = payload.timestamp
    ? new Date(Number(payload.timestamp) * 1000).toISOString()
    : new Date().toISOString();
  const latencyMs = preciseRound(performance.now() - startedAt, 2);
  const edges = [];

  Object.entries(payload.rates || {}).forEach(([currency, rate]) => {
    if (!isSupportedCurrency(currency)) return;
    const edge = createRateEdge(providerBase, currency, Number(rate), {
      source: 'openexchangerates.org',
      sourceStatus: 'LIVE_PROVIDER',
      confidence: 0.92,
      observedAt,
      latencyMs
    });
    if (edge) edges.push(edge);
  });

  return edges;
}

/**
 * @function collectRateEdges
 * @description Collects FX graph edges from env and configured live providers.
 * @param {string} baseCurrency - Base currency.
 * @param {Array<string>} targetCurrencies - Target currencies.
 * @returns {Promise<{edges:Array,sources:Array}>} Edge collection packet.
 * @collaboration Makes source coverage explicit so dashboards can distinguish live rates from env-declared rates.
 */
export async function collectRateEdges(baseCurrency, targetCurrencies = []) {
  const envEdges = readDeclaredFxEdges();
  const sources = [{
    name: 'server/.env',
    status: envEdges.length ? 'ENV_DECLARED' : 'NO_ENV_RATES',
    edgeCount: envEdges.length
  }];
  const providerEdges = [];

  try {
    const openExchangeEdges = await fetchFromOpenExchangeRates(baseCurrency, targetCurrencies);
    providerEdges.push(...openExchangeEdges);
    sources.push({
      name: 'openexchangerates.org',
      status: openExchangeEdges.length ? 'LIVE_PROVIDER' : 'NOT_CONFIGURED',
      edgeCount: openExchangeEdges.length
    });
  } catch (error) {
    sources.push({
      name: 'openexchangerates.org',
      status: 'SOURCE_SILENT',
      edgeCount: 0,
      error: error.message
    });
  }

  return {
    edges: [...providerEdges, ...envEdges],
    sources
  };
}

/**
 * @function resolveTargetCurrencies
 * @description Resolves target currencies for an FX request.
 * @param {Array<string>} targetCurrencies - Requested targets.
 * @param {string} baseCurrency - Base currency.
 * @returns {Array<string>} Target currency codes.
 * @collaboration Supports all-currency requests while avoiding duplicate base currency rows.
 */
export function resolveTargetCurrencies(targetCurrencies = [], baseCurrency = DEFAULT_BASE_CURRENCY) {
  const base = assertSupportedCurrency(baseCurrency);
  const targets = targetCurrencies.length
    ? targetCurrencies
    : SUPPORTED_CURRENCY_CODES;
  return [...new Set(targets.map(assertSupportedCurrency))].filter(code => code !== base);
}

/**
 * @function fetchExchangeRates
 * @description Fetches and resolves exchange rates through live/env source graphing.
 * @param {string} baseCurrency - Base currency.
 * @param {Array<string>} targetCurrencies - Target currencies; empty means all supported currencies.
 * @param {Object} options - Runtime options.
 * @returns {Promise<Object>} FX snapshot.
 * @collaboration Replaces prototype one-hop conversion with all-currency graph intelligence and honest source gaps.
 */
export async function fetchExchangeRates(baseCurrency = DEFAULT_BASE_CURRENCY, targetCurrencies = [], options = {}) {
  const base = assertSupportedCurrency(baseCurrency);
  const targets = resolveTargetCurrencies(targetCurrencies, base);
  const cacheKey = buildCacheKey(base, targets);
  if (options.useCache !== false) {
    const cached = getCachedRates(cacheKey);
    if (cached) return cached;
  }

  const { edges, sources } = await collectRateEdges(base, targets);
  const graph = buildRateGraph(edges);
  const rates = { [base]: 1 };
  const paths = {};
  const missingRates = [];

  targets.forEach(target => {
    const pathResult = resolveRatePath(graph, base, target);
    if (!pathResult) {
      missingRates.push(`${base}_TO_${target}`);
      return;
    }
    rates[target] = preciseRound(pathResult.rate, 8);
    paths[target] = {
      path: pathResult.path,
      sources: pathResult.sources,
      confidence: pathResult.confidence
    };
  });

  const coverage = targets.length ? preciseRound(((targets.length - missingRates.length) / targets.length) * 100, 2) : 100;
  const sourceStatus = missingRates.length === 0
    ? 'ALL_RATES_RESOLVED'
    : Object.keys(rates).length > 1
      ? 'PARTIAL_RATE_COVERAGE'
      : 'SOURCE_REQUIRED';
  const snapshot = {
    success: missingRates.length === 0 || !CURRENCY_CONSTANTS.STRICT_SOURCE_MODE,
    engineVersion: ENGINE_VERSION,
    base,
    rates,
    paths,
    missingRates,
    coverage,
    sourceStatus,
    sourceCount: sources.filter(source => source.edgeCount > 0).length,
    sources,
    supportedCurrencyCount: SUPPORTED_CURRENCY_CODES.length,
    generatedAt: new Date().toISOString()
  };
  snapshot.proof = {
    algorithm: 'SHA3-512',
    hash: createCurrencyProofHash({
      base: snapshot.base,
      rates: snapshot.rates,
      missingRates: snapshot.missingRates,
      generatedAt: snapshot.generatedAt,
      engineVersion: snapshot.engineVersion
    })
  };
  snapshot.encrypted = quantumEncryptData({ rates, paths, sources });
  setCachedRates(cacheKey, snapshot);
  return snapshot;
}

/**
 * @function calculateConversionFeeProfile
 * @description Calculates conversion fees and explains the applied policy.
 * @param {number} amount - Source amount.
 * @param {string} fromCurrency - Source currency.
 * @param {string} toCurrency - Target currency.
 * @param {Object} options - Fee options.
 * @returns {Object} Fee profile.
 * @collaboration Turns fees into transparent tenant-facing economics rather than hidden arithmetic.
 */
export function calculateConversionFeeProfile(amount, fromCurrency, toCurrency, options = {}) {
  const from = assertSupportedCurrency(fromCurrency);
  const to = assertSupportedCurrency(toCurrency);
  if (from === to) {
    return {
      feeAmount: 0,
      feeBps: 0,
      riskMultiplier: 1,
      sourceCurrency: from,
      targetCurrency: to,
      policy: 'IDENTICAL_CURRENCY_NO_FX_FEE'
    };
  }
  const baseBps = Number(options.feeBps ?? CURRENCY_CONSTANTS.DEFAULT_FEE_BPS);
  const riskMultiplier = AFRICAN_CURRENCY_CODES.has(from) || AFRICAN_CURRENCY_CODES.has(to)
    ? CURRENCY_CONSTANTS.AFRICAN_FEE_MULTIPLIER
    : 1;
  const rawFee = Number(amount || 0) * (baseBps / 10000) * riskMultiplier;
  const feeAmount = Math.max(CURRENCY_CONSTANTS.MIN_FEE_ZAR, Math.min(rawFee, CURRENCY_CONSTANTS.MAX_FEE_ZAR));
  return {
    feeAmount: preciseRound(feeAmount, getCurrencyExponent(from)),
    feeBps: baseBps,
    riskMultiplier,
    sourceCurrency: from,
    targetCurrency: to,
    policy: 'ENV_CONFIGURED_BPS_WITH_AFRICAN_RISK_MULTIPLIER'
  };
}

/**
 * @function calculateConversionFees
 * @description Returns the numeric fee amount for backward compatibility.
 * @param {number} amount - Source amount.
 * @param {string} fromCurrency - Source currency.
 * @param {string} toCurrency - Target currency.
 * @returns {number} Fee amount.
 * @collaboration Keeps legacy callers working while the richer fee profile exists for production modules.
 */
export function calculateConversionFees(amount, fromCurrency, toCurrency) {
  return calculateConversionFeeProfile(amount, fromCurrency, toCurrency).feeAmount;
}

/**
 * @function checkSARBCompliance
 * @description Builds a South-African-first compliance signal for a currency transaction.
 * @param {number} amount - Source amount.
 * @param {string} fromCurrency - Source currency.
 * @param {string} toCurrency - Target currency.
 * @param {Object} context - Optional contextual values.
 * @returns {Object} Compliance signal.
 * @collaboration Gives Wilsy OS a conservative compliance posture before cross-border or high-value money movement.
 */
export function checkSARBCompliance(amount, fromCurrency, toCurrency, context = {}) {
  const from = assertSupportedCurrency(fromCurrency);
  const to = assertSupportedCurrency(toCurrency);
  const amountInZar = Number(context.amountInZar ?? (from === 'ZAR' ? amount : 0));
  const crossBorder = Boolean(context.crossBorder ?? (from !== to));
  const foreignCurrencyExposure = from !== 'ZAR' || to !== 'ZAR';
  const flags = [];

  if (crossBorder) flags.push('CROSS_BORDER_CURRENCY_MOVEMENT');
  if (foreignCurrencyExposure) flags.push('FOREIGN_CURRENCY_EXPOSURE');
  if (amountInZar && amountInZar >= CURRENCY_CONSTANTS.SARB_THRESHOLD_ZAR) flags.push('SARB_REVIEW_REQUIRED');
  if (amountInZar && amountInZar >= CURRENCY_CONSTANTS.FICA_THRESHOLD_ZAR) flags.push('FICA_ENHANCED_DUE_DILIGENCE');
  if (amountInZar && amountInZar >= CURRENCY_CONSTANTS.REPORTING_THRESHOLD_ZAR) flags.push('INTERNAL_REPORTING_REQUIRED');
  if (HEIGHTENED_DILIGENCE_CURRENCIES.has(from) || HEIGHTENED_DILIGENCE_CURRENCIES.has(to)) flags.push('HEIGHTENED_CURRENCY_DILIGENCE');
  if (NON_CASH_ISO_UNITS.has(from) || NON_CASH_ISO_UNITS.has(to)) flags.push('NON_CASH_ISO_UNIT_REVIEW');

  return {
    jurisdiction: 'ZA',
    regulation: 'SARB Exchange Control / FICA internal review signal',
    amount,
    amountInZar: amountInZar ? preciseRound(amountInZar, 2) : null,
    fromCurrency: from,
    toCurrency: to,
    crossBorder,
    foreignCurrencyExposure,
    requiresApproval: flags.includes('SARB_REVIEW_REQUIRED') || flags.includes('HEIGHTENED_CURRENCY_DILIGENCE'),
    reportingRequired: flags.includes('INTERNAL_REPORTING_REQUIRED'),
    flags,
    status: flags.length ? 'REVIEW_REQUIRED' : 'AUTO_CLEARED',
    threshold: {
      sarbZar: CURRENCY_CONSTANTS.SARB_THRESHOLD_ZAR,
      ficaZar: CURRENCY_CONSTANTS.FICA_THRESHOLD_ZAR,
      reportingZar: CURRENCY_CONSTANTS.REPORTING_THRESHOLD_ZAR
    }
  };
}

/**
 * @function convertCurrency
 * @description Converts an amount between any supported currencies using FX graph resolution.
 * @param {number|string} amount - Amount to convert.
 * @param {string} fromCurrency - Source currency.
 * @param {string} toCurrency - Target currency.
 * @param {Object} options - Runtime options.
 * @returns {Promise<Object>} Conversion packet.
 * @collaboration Gives tenants real money conversion with proof, source coverage, fees and South African compliance context.
 */
export async function convertCurrency(amount, fromCurrency, toCurrency, options = {}) {
  const numericAmount = Number(amount);
  if (!Number.isFinite(numericAmount) || numericAmount <= 0) throw new Error('Amount must be a positive number.');

  const from = assertSupportedCurrency(fromCurrency);
  const to = assertSupportedCurrency(toCurrency);
  if (from === to) {
    const feeProfile = calculateConversionFeeProfile(numericAmount, from, to, options);
    const compliance = checkSARBCompliance(numericAmount, from, to, {
      amountInZar: options.amountInZar ?? (from === 'ZAR' ? numericAmount : null),
      crossBorder: options.crossBorder
    });
    const payload = {
      success: true,
      engineVersion: ENGINE_VERSION,
      original: {
        amount: preciseRound(numericAmount, getCurrencyExponent(from)),
        formatted: formatWilsyMoney(numericAmount, from),
        currency: from,
        minorUnits: toMinorUnits(numericAmount, from)
      },
      converted: {
        grossAmount: preciseRound(numericAmount, getCurrencyExponent(to)),
        netAmount: preciseRound(numericAmount, getCurrencyExponent(to)),
        formatted: formatWilsyMoney(numericAmount, to),
        currency: to,
        minorUnits: toMinorUnits(numericAmount, to)
      },
      zarReference: {
        amount: compliance.amountInZar,
        formatted: compliance.amountInZar ? formatWilsyMoney(compliance.amountInZar, 'ZAR') : null
      },
      rate: 1,
      fee: {
        ...feeProfile,
        targetFeeAmount: 0,
        targetFeeFormatted: formatWilsyMoney(0, to)
      },
      compliance,
      source: {
        sourceStatus: 'IDENTICAL_CURRENCY_NO_FX_REQUIRED',
        coverage: 100,
        path: [from],
        proofHash: createCurrencyProofHash({ from, to, amount: numericAmount, sourceStatus: 'IDENTICAL_CURRENCY_NO_FX_REQUIRED' })
      },
      generatedAt: new Date().toISOString()
    };
    return {
      ...payload,
      proof: {
        algorithm: 'SHA3-512',
        hash: createCurrencyProofHash(payload)
      }
    };
  }
  const targets = [...new Set([to, 'ZAR'])].filter(code => code !== from);
  const snapshot = await fetchExchangeRates(from, targets, options);
  const targetRate = to === from ? 1 : snapshot.rates[to];
  if (!targetRate) throw new Error(`Exchange rate not available for ${from} to ${to}. Missing: ${(snapshot.missingRates || []).join(', ')}`);

  const zarRate = from === 'ZAR' ? 1 : snapshot.rates.ZAR;
  const amountInZar = zarRate ? numericAmount * zarRate : null;
  const feeProfile = calculateConversionFeeProfile(numericAmount, from, to, options);
  const feeInTarget = feeProfile.feeAmount * targetRate;
  const grossTargetAmount = numericAmount * targetRate;
  const netTargetAmount = Math.max(0, grossTargetAmount - feeInTarget);
  const compliance = checkSARBCompliance(numericAmount, from, to, { amountInZar });

  const result = {
    success: true,
    engineVersion: ENGINE_VERSION,
    original: {
      amount: preciseRound(numericAmount, getCurrencyExponent(from)),
      formatted: formatWilsyMoney(numericAmount, from),
      currency: from,
      minorUnits: toMinorUnits(numericAmount, from)
    },
    converted: {
      grossAmount: preciseRound(grossTargetAmount, getCurrencyExponent(to)),
      netAmount: preciseRound(netTargetAmount, getCurrencyExponent(to)),
      formatted: formatWilsyMoney(netTargetAmount, to),
      currency: to,
      minorUnits: toMinorUnits(netTargetAmount, to)
    },
    zarReference: amountInZar
      ? {
          amount: preciseRound(amountInZar, 2),
          formatted: formatWilsyMoney(amountInZar, 'ZAR')
        }
      : null,
    rate: preciseRound(targetRate, 8),
    fee: {
      ...feeProfile,
      targetFeeAmount: preciseRound(feeInTarget, getCurrencyExponent(to)),
      targetFeeFormatted: formatWilsyMoney(feeInTarget, to)
    },
    compliance,
    source: {
      sourceStatus: snapshot.sourceStatus,
      coverage: snapshot.coverage,
      path: snapshot.paths[to] || null,
      proofHash: snapshot.proof?.hash
    },
    generatedAt: new Date().toISOString()
  };
  result.proof = {
    algorithm: 'SHA3-512',
    hash: createCurrencyProofHash(result)
  };
  return result;
}

/**
 * @function normalizeExposureRows
 * @description Normalizes mixed exposure rows into currency/amount pairs.
 * @param {Array<Object>} rows - Exposure rows.
 * @returns {Array<Object>} Normalized rows.
 * @collaboration Allows billing, treasury and executive modules to feed the same risk engine without shape rewrites.
 */
export function normalizeExposureRows(rows = []) {
  if (!Array.isArray(rows)) return [];
  return rows
    .map(row => {
      const currency = normalizeCurrencyCode(row.currency || row._id || row.code || row.isoCode);
      const amount = Number(row.total ?? row.amount ?? row.value ?? row.exposure ?? 0);
      return {
        ...row,
        currency,
        amount: Number.isFinite(amount) ? Math.max(0, amount) : 0
      };
    })
    .filter(row => row.amount > 0 && isSupportedCurrency(row.currency));
}

/**
 * @function getDominantCurrency
 * @description Determines the dominant currency exposure.
 * @param {Array<Object>} currencyBreakdown - Exposure rows.
 * @returns {Object} Dominant currency packet.
 * @collaboration Gives executives immediate concentration awareness without pretending missing exposure exists.
 */
export function getDominantCurrency(currencyBreakdown = []) {
  const rows = normalizeExposureRows(currencyBreakdown);
  const total = rows.reduce((sum, row) => sum + row.amount, 0);
  if (!total) {
    return {
      currency: CURRENCY_CONSTANTS.DEFAULT_CURRENCY,
      percentage: 0,
      risk: 'NO_EXPOSURE',
      amount: 0,
      total: 0
    };
  }
  const dominant = rows.reduce((winner, row) => (row.amount > winner.amount ? row : winner), rows[0]);
  const percentage = (dominant.amount / total) * 100;
  return {
    currency: dominant.currency,
    profile: getCurrencyProfile(dominant.currency),
    percentage: preciseRound(percentage, 2),
    amount: preciseRound(dominant.amount, getCurrencyExponent(dominant.currency)),
    total: preciseRound(total, 2),
    risk: percentage >= 80 ? 'HIGH_CONCENTRATION' : percentage >= 55 ? 'MEDIUM_CONCENTRATION' : 'DIVERSIFIED'
  };
}

/**
 * @function calculateHHI
 * @description Calculates Herfindahl-Hirschman concentration index for currency exposure.
 * @param {Array<Object>} rows - Normalized exposure rows.
 * @returns {number} HHI score.
 * @collaboration Quantifies concentration risk with a defensible institutional metric.
 */
export function calculateHHI(rows = []) {
  const total = rows.reduce((sum, row) => sum + row.amount, 0);
  if (!total) return 0;
  return preciseRound(rows.reduce((sum, row) => {
    const share = row.amount / total;
    return sum + ((share * 100) ** 2);
  }, 0), 2);
}

/**
 * @function calculateEntropyIndex
 * @description Calculates a normalized diversification entropy index.
 * @param {Array<Object>} rows - Normalized exposure rows.
 * @returns {number} Diversification score from 0 to 1.
 * @collaboration Adds a portfolio-quality view beyond simple dominant-currency cards.
 */
export function calculateEntropyIndex(rows = []) {
  const total = rows.reduce((sum, row) => sum + row.amount, 0);
  if (!total || rows.length <= 1) return 0;
  const entropy = rows.reduce((sum, row) => {
    const share = row.amount / total;
    return share > 0 ? sum - (share * Math.log(share)) : sum;
  }, 0);
  return preciseRound(entropy / Math.log(rows.length), 4);
}

/**
 * @function inferLiquidityTier
 * @description Infers operational liquidity tier for a currency.
 * @param {string} currency - Currency code.
 * @returns {string} Liquidity tier.
 * @collaboration Gives risk and fee algorithms an explainable currency liquidity primitive.
 */
export function inferLiquidityTier(currency = DEFAULT_BASE_CURRENCY) {
  const code = assertSupportedCurrency(currency);
  if (MAJOR_RESERVE_CURRENCIES.has(code)) return 'GLOBAL_RESERVE';
  if (PEGGED_OR_MANAGED_CURRENCIES.has(code)) return 'MANAGED_LIQUIDITY';
  if (AFRICAN_CURRENCY_CODES.has(code)) return 'AFRICAN_MARKET';
  if (HEIGHTENED_DILIGENCE_CURRENCIES.has(code)) return 'HEIGHTENED_DILIGENCE';
  if (NON_CASH_ISO_UNITS.has(code)) return 'NON_CASH_ISO_UNIT';
  return 'STANDARD_MARKET';
}

/**
 * @function inferCurrencyVolatility
 * @description Infers a baseline annualized volatility for currency risk scoring.
 * @param {string} currency - Currency code.
 * @returns {number} Volatility baseline.
 * @collaboration Provides a documented baseline when live historical volatility is not supplied by a market-data source.
 */
export function inferCurrencyVolatility(currency = DEFAULT_BASE_CURRENCY) {
  const code = assertSupportedCurrency(currency);
  if (code === 'ZAR') return 0.14;
  if (MAJOR_RESERVE_CURRENCIES.has(code)) return 0.055;
  if (PEGGED_OR_MANAGED_CURRENCIES.has(code)) return 0.035;
  if (HEIGHTENED_DILIGENCE_CURRENCIES.has(code)) return 0.32;
  if (AFRICAN_CURRENCY_CODES.has(code)) return 0.18;
  if (NON_CASH_ISO_UNITS.has(code)) return 0.22;
  return 0.11;
}

/**
 * @function calculateAverageVolatility
 * @description Calculates weighted portfolio volatility from exposure rows.
 * @param {Array<Object>} breakdown - Exposure rows.
 * @returns {number} Weighted volatility.
 * @collaboration Makes VaR and stress testing responsive to actual tenant currency composition.
 */
export function calculateAverageVolatility(breakdown = []) {
  const rows = normalizeExposureRows(breakdown);
  const total = rows.reduce((sum, row) => sum + row.amount, 0);
  if (!total) return 0;
  return preciseRound(rows.reduce((sum, row) => (
    sum + ((row.amount / total) * inferCurrencyVolatility(row.currency))
  ), 0), 4);
}

/**
 * @function inverseNormalCdf
 * @description Approximates inverse normal CDF for VaR z-score calculations.
 * @param {number} probability - Probability value.
 * @returns {number} Z-score.
 * @collaboration Avoids dependency bloat while giving risk algorithms confidence-level flexibility.
 */
export function inverseNormalCdf(probability = 0.95) {
  const p = Math.min(0.999, Math.max(0.001, Number(probability)));
  const a1 = -39.6968302866538;
  const a2 = 220.946098424521;
  const a3 = -275.928510446969;
  const a4 = 138.357751867269;
  const a5 = -30.6647980661472;
  const a6 = 2.50662827745924;
  const b1 = -54.4760987982241;
  const b2 = 161.585836858041;
  const b3 = -155.698979859887;
  const b4 = 66.8013118877197;
  const b5 = -13.2806815528857;
  const c1 = -0.00778489400243029;
  const c2 = -0.322396458041136;
  const c3 = -2.40075827716184;
  const c4 = -2.54973253934373;
  const c5 = 4.37466414146497;
  const c6 = 2.93816398269878;
  const d1 = 0.00778469570904146;
  const d2 = 0.32246712907004;
  const d3 = 2.445134137143;
  const d4 = 3.75440866190742;
  const plow = 0.02425;
  const phigh = 1 - plow;

  if (p < plow) {
    const q = Math.sqrt(-2 * Math.log(p));
    return (((((c1 * q + c2) * q + c3) * q + c4) * q + c5) * q + c6) /
      ((((d1 * q + d2) * q + d3) * q + d4) * q + 1);
  }
  if (p <= phigh) {
    const q = p - 0.5;
    const r = q * q;
    return (((((a1 * r + a2) * r + a3) * r + a4) * r + a5) * r + a6) * q /
      (((((b1 * r + b2) * r + b3) * r + b4) * r + b5) * r + 1);
  }
  const q = Math.sqrt(-2 * Math.log(1 - p));
  return -(((((c1 * q + c2) * q + c3) * q + c4) * q + c5) * q + c6) /
    ((((d1 * q + d2) * q + d3) * q + d4) * q + 1);
}

/**
 * @function calculateValueAtRisk
 * @description Calculates currency Value-at-Risk from exposure and volatility.
 * @param {Array<Object>} breakdown - Exposure rows.
 * @param {number|null} totalExposure - Optional total exposure override.
 * @param {number} confidence - Confidence level.
 * @returns {Object} VaR packet.
 * @collaboration Gives executives a quantitative loss-at-risk signal instead of decorative risk language.
 */
export function calculateValueAtRisk(breakdown = [], totalExposure = null, confidence = 0.95) {
  const rows = normalizeExposureRows(breakdown);
  const exposure = Number(totalExposure ?? rows.reduce((sum, row) => sum + row.amount, 0));
  if (!rows.length || !exposure) return { valueAtRisk: 0, confidence, status: 'NO_EXPOSURE' };
  const volatility = calculateAverageVolatility(rows);
  const zScore = inverseNormalCdf(confidence);
  const valueAtRisk = exposure * volatility * zScore;
  return {
    valueAtRisk: preciseRound(valueAtRisk, 2),
    formattedZar: formatWilsyMoney(valueAtRisk, 'ZAR'),
    confidence,
    zScore: preciseRound(zScore, 4),
    volatility,
    totalExposure: preciseRound(exposure, 2),
    interpretation: getVaRInterpretation(valueAtRisk, exposure)
  };
}

/**
 * @function getVaRInterpretation
 * @description Maps VaR ratio into an operational risk label.
 * @param {number} varAmount - Value-at-Risk amount.
 * @param {number} totalExposure - Total exposure amount.
 * @returns {string} Risk interpretation.
 * @collaboration Converts risk math into a stable operator decision label.
 */
export function getVaRInterpretation(varAmount, totalExposure) {
  const ratio = totalExposure ? (varAmount / totalExposure) : 0;
  if (ratio >= 0.28) return 'EXTREME_RISK';
  if (ratio >= 0.18) return 'HIGH_RISK';
  if (ratio >= 0.1) return 'MEDIUM_RISK';
  if (ratio > 0) return 'LOW_RISK';
  return 'NO_RISK';
}

/**
 * @function calculateStressScenarios
 * @description Calculates deterministic FX stress scenarios for a portfolio.
 * @param {Array<Object>} breakdown - Exposure rows.
 * @returns {Array<Object>} Stress scenario results.
 * @collaboration Gives daily executive and treasury workflows realistic downside cases without random theatre.
 */
export function calculateStressScenarios(breakdown = []) {
  const rows = normalizeExposureRows(breakdown);
  const total = rows.reduce((sum, row) => sum + row.amount, 0);
  const africanShare = total ? rows.filter(row => AFRICAN_CURRENCY_CODES.has(row.currency)).reduce((sum, row) => sum + row.amount, 0) / total : 0;
  const reserveShare = total ? rows.filter(row => MAJOR_RESERVE_CURRENCIES.has(row.currency)).reduce((sum, row) => sum + row.amount, 0) / total : 0;
  const highRiskShare = total ? rows.filter(row => HEIGHTENED_DILIGENCE_CURRENCIES.has(row.currency)).reduce((sum, row) => sum + row.amount, 0) / total : 0;
  return [
    {
      id: 'ZAR_DEPRECIATION_15',
      label: 'ZAR 15% depreciation shock',
      impactAmount: preciseRound(total * africanShare * 0.15, 2),
      severity: africanShare > 0.55 ? 'HIGH' : 'MEDIUM'
    },
    {
      id: 'USD_LIQUIDITY_SQUEEZE',
      label: 'USD liquidity squeeze',
      impactAmount: preciseRound(total * Math.max(0, 1 - reserveShare) * 0.09, 2),
      severity: reserveShare < 0.25 ? 'HIGH' : 'LOW'
    },
    {
      id: 'HEIGHTENED_DILIGENCE_FREEZE',
      label: 'High-risk currency settlement freeze',
      impactAmount: preciseRound(total * highRiskShare * 0.35, 2),
      severity: highRiskShare > 0.1 ? 'CRITICAL' : 'LOW'
    }
  ];
}

/**
 * @function generateRiskRecommendations
 * @description Generates action recommendations from currency risk metrics.
 * @param {Object|string} riskInput - Risk packet or risk label.
 * @param {number} concentration - Dominant concentration percentage.
 * @param {number} currencyCount - Number of currencies.
 * @returns {Array<Object>} Recommendation rows.
 * @collaboration Turns Wilsy OS currency intelligence into productive daily executive action.
 */
export function generateRiskRecommendations(riskInput, concentration = 0, currencyCount = 0) {
  const riskLevel = typeof riskInput === 'string' ? riskInput : riskInput?.overallRisk;
  const recommendations = [];

  if (concentration >= 80) {
    recommendations.push({
      priority: 'HIGH',
      action: 'Reduce dominant currency concentration',
      detail: `Dominant exposure is ${preciseRound(concentration, 1)}%. Build a hedge or rebalance settlement terms.`
    });
  }
  if (currencyCount < 3) {
    recommendations.push({
      priority: 'MEDIUM',
      action: 'Add settlement optionality',
      detail: 'Enable at least three operating currencies for suppliers, clients or treasury reserves.'
    });
  }
  if (['HIGH', 'CRITICAL', 'EXTREME'].includes(riskLevel)) {
    recommendations.push({
      priority: 'HIGH',
      action: 'Trigger treasury hedge review',
      detail: 'Review forward cover, natural hedges and ZAR cash buffers before new cross-border commitments.'
    });
  }
  if (!recommendations.length) {
    recommendations.push({
      priority: 'LOW',
      action: 'Maintain monitored currency posture',
      detail: 'Currency portfolio is within current risk appetite; continue daily rate surveillance.'
    });
  }
  return recommendations;
}

/**
 * @function calculateCurrencyRisk
 * @description Calculates full portfolio currency risk with concentration, entropy, VaR and stress scenarios.
 * @param {Array<Object>} currencyBreakdown - Exposure rows.
 * @returns {Object} Currency risk packet.
 * @collaboration Replaces decorative cards with an auditable decision engine for real tenant money exposure.
 */
export function calculateCurrencyRisk(currencyBreakdown = []) {
  const rows = normalizeExposureRows(currencyBreakdown);
  const totalExposure = rows.reduce((sum, row) => sum + row.amount, 0);
  if (!totalExposure) {
    return {
      overallRisk: 'NO_EXPOSURE',
      riskScore: 0,
      totalExposure: 0,
      currencyCount: 0,
      recommendations: generateRiskRecommendations('NO_EXPOSURE', 0, 0)
    };
  }

  const dominant = getDominantCurrency(rows);
  const hhi = calculateHHI(rows);
  const entropy = calculateEntropyIndex(rows);
  const volatility = calculateAverageVolatility(rows);
  const highRiskShare = rows.filter(row => HEIGHTENED_DILIGENCE_CURRENCIES.has(row.currency)).reduce((sum, row) => sum + row.amount, 0) / totalExposure;
  const nonCashShare = rows.filter(row => NON_CASH_ISO_UNITS.has(row.currency)).reduce((sum, row) => sum + row.amount, 0) / totalExposure;
  const concentrationScore = Math.min(40, dominant.percentage * 0.4);
  const hhiScore = Math.min(20, hhi / 500);
  const volatilityScore = Math.min(22, volatility * 100);
  const diligenceScore = Math.min(14, highRiskShare * 100);
  const nonCashScore = Math.min(4, nonCashShare * 40);
  const diversificationCredit = entropy * 12;
  const riskScore = Math.max(0, Math.min(100, concentrationScore + hhiScore + volatilityScore + diligenceScore + nonCashScore - diversificationCredit));
  const overallRisk = riskScore >= 78 ? 'CRITICAL' : riskScore >= 58 ? 'HIGH' : riskScore >= 34 ? 'MEDIUM' : 'LOW';
  const varAnalysis = calculateValueAtRisk(rows, totalExposure, 0.95);
  const stressScenarios = calculateStressScenarios(rows);

  return {
    overallRisk,
    riskScore: preciseRound(riskScore, 2),
    totalExposure: preciseRound(totalExposure, 2),
    formattedExposure: formatWilsyMoney(totalExposure, CURRENCY_CONSTANTS.BASE_CURRENCY),
    currencyCount: rows.length,
    dominantCurrency: dominant,
    hhi,
    entropy,
    weightedVolatility: volatility,
    highRiskShare: preciseRound(highRiskShare, 4),
    nonCashShare: preciseRound(nonCashShare, 4),
    varAnalysis,
    stressScenarios,
    recommendations: generateRiskRecommendations(overallRisk, dominant.percentage, rows.length),
    proof: {
      algorithm: 'SHA3-512',
      hash: createCurrencyProofHash({ rows, totalExposure, overallRisk, riskScore })
    }
  };
}

/**
 * @function validateCurrencyTransaction
 * @description Validates a currency transaction command.
 * @param {Object} transaction - Candidate transaction.
 * @returns {{valid:boolean,errors:Array<string>,warnings:Array<string>,validatedAt:string,compliance:Object|null}} Validation packet.
 * @collaboration Protects tenants from malformed FX commands before billing or treasury receives them.
 */
export function validateCurrencyTransaction(transaction = {}) {
  const errors = [];
  const warnings = [];
  const amount = Number(transaction.amount);
  const fromCurrency = normalizeCurrencyCode(transaction.fromCurrency || transaction.currency || CURRENCY_CONSTANTS.BASE_CURRENCY);
  const toCurrency = normalizeCurrencyCode(transaction.toCurrency || CURRENCY_CONSTANTS.BASE_CURRENCY);

  if (!Number.isFinite(amount) || amount <= 0) errors.push('AMOUNT_MUST_BE_POSITIVE');
  if (!isSupportedCurrency(fromCurrency)) errors.push(`UNSUPPORTED_SOURCE_CURRENCY:${fromCurrency}`);
  if (!isSupportedCurrency(toCurrency)) errors.push(`UNSUPPORTED_TARGET_CURRENCY:${toCurrency}`);
  if (!transaction.tenantId) warnings.push('TENANT_ID_RECOMMENDED_FOR_AUDIT');
  if (!transaction.purpose) warnings.push('TRANSACTION_PURPOSE_RECOMMENDED');
  if (HEIGHTENED_DILIGENCE_CURRENCIES.has(fromCurrency) || HEIGHTENED_DILIGENCE_CURRENCIES.has(toCurrency)) warnings.push('HEIGHTENED_DILIGENCE_CURRENCY');
  if (NON_CASH_ISO_UNITS.has(fromCurrency) || NON_CASH_ISO_UNITS.has(toCurrency)) warnings.push('NON_CASH_ISO_UNIT_REVIEW');

  const compliance = errors.length ? null : checkSARBCompliance(amount, fromCurrency, toCurrency, transaction);
  return {
    valid: errors.length === 0,
    errors,
    warnings,
    compliance,
    validatedAt: new Date().toISOString()
  };
}

/**
 * @function generateCurrencyReport
 * @description Generates a sealed currency intelligence report.
 * @param {Array<Object>} breakdown - Exposure rows.
 * @param {string} period - Reporting period.
 * @returns {Object} Currency report packet.
 * @collaboration Gives executives, treasury and auditors one complete currency evidence artifact.
 */
export function generateCurrencyReport(breakdown = [], period = 'MONTHLY') {
  const rows = normalizeExposureRows(breakdown);
  const totalExposure = rows.reduce((sum, row) => sum + row.amount, 0);
  const riskAnalysis = calculateCurrencyRisk(rows);
  const payload = {
    reportId: `CUR-${Date.now().toString(36).toUpperCase()}`,
    engineVersion: ENGINE_VERSION,
    period,
    generatedAt: new Date().toISOString(),
    baseCurrency: CURRENCY_CONSTANTS.BASE_CURRENCY,
    supportedCurrencyCount: SUPPORTED_CURRENCY_CODES.length,
    summary: {
      totalExposure: preciseRound(totalExposure, 2),
      formattedExposure: formatWilsyMoney(totalExposure, CURRENCY_CONSTANTS.BASE_CURRENCY),
      currencyCount: rows.length,
      dominantCurrency: getDominantCurrency(rows)
    },
    riskAnalysis,
    currencyProfiles: rows.map(row => ({
      currency: row.currency,
      amount: row.amount,
      profile: getCurrencyProfile(row.currency)
    })),
    compliance: {
      jurisdiction: 'ZA',
      sarbThresholdZar: CURRENCY_CONSTANTS.SARB_THRESHOLD_ZAR,
      reportingRequired: totalExposure >= CURRENCY_CONSTANTS.REPORTING_THRESHOLD_ZAR,
      sourcePolicy: 'NO_FAKE_FX_RATES'
    }
  };
  return {
    ...payload,
    proof: {
      algorithm: 'SHA3-512',
      hash: createCurrencyProofHash(payload)
    },
    encrypted: quantumEncryptData(payload)
  };
}

/**
 * @function validateEnvironment
 * @description Validates production-critical currency environment configuration.
 * @returns {Object} Environment validation packet.
 * @collaboration Makes FX source readiness visible without exposing secret values.
 */
export function validateEnvironment() {
  const required = ['ENCRYPTION_KEY'];
  const warnings = [];
  const errors = [];
  required.forEach(key => {
    if (!process.env[key]) errors.push(`MISSING_${key}`);
  });
  if (!CURRENCY_CONSTANTS.OPEN_EXCHANGE_RATES_APP_ID) warnings.push('OPEN_EXCHANGE_RATES_PROVIDER_NOT_CONFIGURED');
  if (readDeclaredFxEdges().length === 0) warnings.push('NO_ENV_DECLARED_FX_RATES');
  return {
    valid: errors.length === 0,
    errors,
    warnings,
    baseCurrency: CURRENCY_CONSTANTS.BASE_CURRENCY,
    supportedCurrencyCount: SUPPORTED_CURRENCY_CODES.length,
    engineVersion: ENGINE_VERSION
  };
}

/**
 * @function selfTest
 * @description Runs a deterministic self-test of registry, encryption, FX graph and risk algorithms.
 * @returns {Promise<Object>} Self-test report.
 * @collaboration Gives maintainers proof that the production currency engine is operational after edits.
 */
export async function selfTest() {
  const tests = [];
  /**
   * @function pushTest
   * @description Appends a deterministic self-test outcome to the currency-engine proof report.
   * @param {string} name - Test label.
   * @param {boolean} passed - Whether the invariant passed.
   * @param {string|null} detail - Optional forensic detail for failures or source counts.
   * @returns {number} Updated test collection length.
   * @collaboration Keeps the self-test report explicit so Wilson can trust currency edits before production rollout.
   */
  const pushTest = (name, passed, detail = null) => tests.push({ name, passed, detail });

  try {
    pushTest('ISO runtime registry', SUPPORTED_CURRENCY_CODES.length >= 160 && isSupportedCurrency('ZAR') && isSupportedCurrency('TZS'), `${SUPPORTED_CURRENCY_CODES.length} currencies`);
  } catch (error) {
    pushTest('ISO runtime registry', false, error.message);
  }

  try {
    const encrypted = quantumEncryptData({ amount: 100, currency: 'ZAR' });
    const decrypted = quantumDecryptData(encrypted);
    pushTest('AES-GCM encryption', decrypted?.currency === 'ZAR');
  } catch (error) {
    pushTest('AES-GCM encryption', false, error.message);
  }

  try {
    const graph = buildRateGraph([
      createRateEdge('ZAR', 'USD', 0.05, { source: 'SELF_TEST', confidence: 1 }),
      createRateEdge('USD', 'TZS', 2600, { source: 'SELF_TEST', confidence: 1 })
    ]);
    const pathResult = resolveRatePath(graph, 'ZAR', 'TZS');
    pushTest('FX graph cross-rate', preciseRound(pathResult?.rate, 2) === 130);
  } catch (error) {
    pushTest('FX graph cross-rate', false, error.message);
  }

  try {
    const risk = calculateCurrencyRisk([{ currency: 'ZAR', amount: 100000 }, { currency: 'TZS', amount: 25000 }, { currency: 'USD', amount: 50000 }]);
    pushTest('Risk engine', Boolean(risk.overallRisk && risk.varAnalysis && risk.stressScenarios?.length));
  } catch (error) {
    pushTest('Risk engine', false, error.message);
  }

  const passed = tests.filter(test => test.passed).length;
  return {
    timestamp: new Date().toISOString(),
    engineVersion: ENGINE_VERSION,
    tests,
    summary: {
      passed,
      total: tests.length,
      percentage: preciseRound((passed / tests.length) * 100, 2)
    },
    status: passed === tests.length ? 'PASS' : 'WARN'
  };
}

export {
  CURRENCY_CONSTANTS
};

export default {
  ENGINE_VERSION,
  CURRENCY_CONSTANTS,
  readCurrencyEnv,
  requireCurrencyEnv,
  readCurrencyNumberEnv,
  readCurrencyBooleanEnv,
  readCurrencyListEnv,
  preciseRound,
  stableCurrencyStringify,
  createCurrencyProofHash,
  getRuntimeCurrencyCodes,
  normalizeCurrencyCode,
  isSupportedCurrency,
  assertSupportedCurrency,
  getCurrencyDisplayName,
  getCurrencyExponent,
  toMinorUnits,
  fromMinorUnits,
  formatWilsyMoney,
  getCurrencyProfile,
  getSupportedCurrencies,
  resolveCurrencyEncryptionKey,
  quantumEncryptData,
  quantumDecryptData,
  buildCacheKey,
  getCachedRates,
  setCachedRates,
  fetchJson,
  createRateEdge,
  addRateEdge,
  buildRateGraph,
  resolveRatePath,
  readDeclaredFxEdges,
  fetchFromOpenExchangeRates,
  collectRateEdges,
  resolveTargetCurrencies,
  fetchExchangeRates,
  calculateConversionFeeProfile,
  calculateConversionFees,
  checkSARBCompliance,
  convertCurrency,
  normalizeExposureRows,
  getDominantCurrency,
  calculateHHI,
  calculateEntropyIndex,
  inferLiquidityTier,
  inferCurrencyVolatility,
  calculateAverageVolatility,
  inverseNormalCdf,
  calculateValueAtRisk,
  getVaRInterpretation,
  calculateStressScenarios,
  generateRiskRecommendations,
  calculateCurrencyRisk,
  validateCurrencyTransaction,
  generateCurrencyReport,
  validateEnvironment,
  selfTest
};
