/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - CLIENT CURRENCY INTELLIGENCE SERVICE [V1.0.0-ZAR-FIRST-FX]                                                                 ║
 * ║ [SOUTH AFRICAN MONEY DISPLAY | LIVE FX CLIENT | SOURCE-SILENT CONVERSION | EXECUTIVE ZAR OPERATING LENS]                             ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 1.0.0-ZAR-FIRST-FX | PRODUCTION READY | REUSABLE CLIENT MONEY INTELLIGENCE                                                   ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/services/CurrencyIntelligenceService.js                              ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                    ║
 * ║ • Wilson Khanyezi (Founder/CEO) - Required Wilsy OS to be ZAR-first and productive for real businesses in South Africa and beyond.    ║
 * ║ • AI Engineering (Codex) - ARCHITECTED: Centralized Rand formatting and source-aware FX reads for dashboards and billing surfaces.     ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import { sha3_512 } from 'js-sha3';
import sovereignClient from '../utils/sovereignClient';

export const DEFAULT_OPERATING_CURRENCY = 'ZAR';

export const EXECUTIVE_CURRENCIES = Object.freeze([
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
 * @function stableCurrencyClientStringify
 * @description Serializes client FX payloads with stable key order for proof hashes.
 * @param {unknown} value - Candidate value.
 * @returns {string} Canonical string.
 * @collaboration Client-side currency packets need the same replay discipline as backend FX receipts.
 */
const stableCurrencyClientStringify = (value) => {
  if (typeof value === 'undefined') return 'null';
  if (value instanceof Date) return JSON.stringify(value.toISOString());
  if (value === null || typeof value !== 'object') return JSON.stringify(value);
  if (Array.isArray(value)) return `[${value.map(item => stableCurrencyClientStringify(item)).join(',')}]`;
  return `{${Object.keys(value).sort().map(key => `${JSON.stringify(key)}:${stableCurrencyClientStringify(value[key])}`).join(',')}}`;
};

/**
 * @function createCurrencyClientProof
 * @description Creates a SHA3-512 proof for frontend currency packets.
 * @param {Object} payload - Payload to seal.
 * @returns {string} Uppercase digest.
 * @collaboration Gives executives proof continuity even when an FX source is silent.
 */
export const createCurrencyClientProof = (payload = {}) => sha3_512(stableCurrencyClientStringify(payload)).toUpperCase();

/**
 * @function normalizeCurrency
 * @description Normalizes display or user-entered currency codes to supported operating codes.
 * @param {string} value - Raw currency value.
 * @returns {string} Supported currency code.
 * @collaboration Operators may type ZA; Wilsy OS stores and sends the correct ISO code, ZAR.
 */
export const normalizeCurrency = (value = DEFAULT_OPERATING_CURRENCY) => {
  const code = String(value || DEFAULT_OPERATING_CURRENCY).trim().toUpperCase();
  if (code === 'ZA') return 'ZAR';
  return EXECUTIVE_CURRENCIES.includes(code) ? code : DEFAULT_OPERATING_CURRENCY;
};

/**
 * @function roundMoney
 * @description Rounds a money value for display without hiding missing sources.
 * @param {number|string|null} value - Candidate value.
 * @returns {number|null} Rounded amount or null.
 * @collaboration Prevents null source values from becoming fake zeros.
 */
export const roundMoney = (value) => {
  if (value === null || value === undefined || value === '') return null;
  const numeric = Number(value);
  if (!Number.isFinite(numeric)) return null;
  return Math.round((numeric + Number.EPSILON) * 100) / 100;
};

/**
 * @function formatZarMoney
 * @description Formats South African Rand in the Wilsy OS local finance style.
 * @param {number|string|null} value - Amount.
 * @returns {string} Rand value such as R100-00.
 * @collaboration South African operating currency should feel native, not imported from a generic SaaS template.
 */
export const formatZarMoney = (value) => {
  const rounded = roundMoney(value);
  if (rounded === null) return 'SOURCE_REQUIRED';
  const [whole, cents = '00'] = Math.abs(rounded).toFixed(2).split('.');
  const sign = rounded < 0 ? '-' : '';
  return `${sign}R${Number(whole).toLocaleString('en-ZA')}-${cents}`;
};

/**
 * @function formatOperatingMoney
 * @description Formats money according to currency while keeping ZAR as the default operating lens.
 * @param {number|string|null} value - Amount.
 * @param {string} currency - Currency code.
 * @returns {string} Display amount.
 * @collaboration One formatter keeps billing, executive and AI monetisation surfaces aligned.
 */
export const formatOperatingMoney = (value, currency = DEFAULT_OPERATING_CURRENCY) => {
  const code = normalizeCurrency(currency);
  const rounded = roundMoney(value);
  if (rounded === null) return 'SOURCE_REQUIRED';
  if (code === 'ZAR') return formatZarMoney(rounded);
  return `${code} ${rounded.toLocaleString('en-ZA', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
};

/**
 * @function convertCurrency
 * @description Requests a protected backend FX conversion.
 * @param {Object} params - Conversion inputs.
 * @returns {Promise<Object>} Conversion packet.
 * @collaboration FX must travel through sovereignClient so tenant isolation and auth headers remain intact.
 */
export const convertCurrency = async ({
  tenantId = 'GLOBAL_ROOT',
  amount = 0,
  fromCurrency = DEFAULT_OPERATING_CURRENCY,
  toCurrency = 'USD'
} = {}) => {
  try {
    const response = await sovereignClient.get('/finance/currency/convert', {
      headers: { 'X-Tenant-ID': tenantId },
      params: {
        tenantId,
        amount,
        from: normalizeCurrency(fromCurrency),
        to: normalizeCurrency(toCurrency)
      },
      disableSourceBackoff: true
    });
    return response?.data?.data || response?.data || {};
  } catch (error) {
    const packet = {
      success: false,
      tenantId,
      sourceStatus: 'FX_CLIENT_SOURCE_SILENT',
      amount: roundMoney(amount),
      fromCurrency: normalizeCurrency(fromCurrency),
      toCurrency: normalizeCurrency(toCurrency),
      error: error.response?.data?.message || error.message || 'FX conversion unavailable.'
    };
    return {
      ...packet,
      proofHash: createCurrencyClientProof(packet)
    };
  }
};

/**
 * @function syncCurrencyWatchlist
 * @description Loads a ZAR-based FX watchlist for the executive dashboard.
 * @param {Object} params - Watchlist inputs.
 * @returns {Promise<Object>} Watchlist packet.
 * @collaboration Gives South African executives a practical cross-border lens without stale static rates.
 */
export const syncCurrencyWatchlist = async ({
  tenantId = 'GLOBAL_ROOT',
  baseCurrency = DEFAULT_OPERATING_CURRENCY,
  targets = ['USD', 'EUR', 'GBP', 'TZS', 'KES']
} = {}) => {
  try {
    const response = await sovereignClient.get('/finance/currency/rates', {
      headers: { 'X-Tenant-ID': tenantId },
      params: {
        tenantId,
        base: normalizeCurrency(baseCurrency),
        targets: targets.map(normalizeCurrency).join(',')
      },
      disableSourceBackoff: true
    });
    return response?.data?.data || response?.data || {};
  } catch (error) {
    const packet = {
      success: false,
      tenantId,
      baseCurrency: normalizeCurrency(baseCurrency),
      sourceStatus: 'FX_WATCHLIST_CLIENT_SOURCE_SILENT',
      rates: [],
      error: error.response?.data?.message || error.message || 'FX watchlist unavailable.'
    };
    return {
      ...packet,
      proofHash: createCurrencyClientProof(packet)
    };
  }
};

export default {
  DEFAULT_OPERATING_CURRENCY,
  EXECUTIVE_CURRENCIES,
  createCurrencyClientProof,
  normalizeCurrency,
  roundMoney,
  formatZarMoney,
  formatOperatingMoney,
  convertCurrency,
  syncCurrencyWatchlist
};
