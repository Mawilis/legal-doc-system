/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - GLOBAL TAX ENGINE [V56.2.0-PRODUCTION-NEXUS]                                                                               ║
 * ║ [SOURCE-ATTRIBUTED VAT/GST | CROSS-BORDER POSTURE | INTEGER MONEY MATH | SHA3 TAX PROOFS]                                             ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 56.2.0-PRODUCTION-NEXUS | PRODUCTION READY | INSTITUTIONAL TAX FINALITY                                                      ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/services/GlobalTaxEngine.js                                          ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                    ║
 * ║ • Wilson Khanyezi (CEO/Lead Architect) - Required global tax logic to move beyond prototype VAT fields into invoice-grade proof,       ║
 * ║   source attribution, cross-border posture, and visible statutory warnings.                                                            ║
 * ║ • AI Engineering (Codex) - ARCHITECTED: Replaced unsafe static tax shortcuts with researched fallback rates, live-rate sync paths,     ║
 * ║   reverse-charge review gates, integer minor-unit math, and SHA3-sealed tax packets.                                                   ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 *
 * This service is intentionally strict: it will not invent a tax rate for a jurisdiction it cannot prove
 * from the live rate service or the researched fallback matrix. Unknown destinations return SOURCE_SILENT
 * / LIVE_RATE_REQUIRED warnings instead of quiet 0% theatre.
 */

import { sha3_512 } from 'js-sha3';
import api from './api';
import { broadcastTelemetry } from '../utils/telemetryHelper';

export const GLOBAL_TAX_ENGINE_VERSION = 'V56.2.0-PRODUCTION-NEXUS';

const LIVE_RATE_CACHE_TTL_MS = 30 * 60 * 1000;
const LIVE_SYNC_BACKOFF_MS = 5 * 60 * 1000;
const DEFAULT_TAX_POINT_DATE = '2026-06-02';
const RATE_DENOMINATOR = 10000;

const TAX_RATE_ENDPOINTS = Object.freeze([
  '/finance/tax-rates/latest',
  '/tax/rates/latest',
  '/billing/tax-rates/latest',
  '/system/tax-rates/latest'
]);

const TAX_MATRIX_ENDPOINTS = Object.freeze([
  '/finance/tax-rates/matrix',
  '/tax/rates/matrix',
  '/system/tax-rates/matrix'
]);

const EU_COUNTRY_CODES = new Set([
  'AT', 'BE', 'BG', 'HR', 'CY', 'CZ', 'DK', 'EE', 'FI', 'FR', 'DE', 'GR',
  'HU', 'IE', 'IT', 'LV', 'LT', 'LU', 'MT', 'NL', 'PL', 'PT', 'RO', 'SK',
  'SI', 'ES', 'SE'
]);

const DIGITAL_SUPPLY_TYPES = new Set([
  'AI_SERVICE',
  'API_USAGE',
  'CLOUD_SERVICE',
  'DIGITAL_SERVICE',
  'HYBRID_SOVEREIGN',
  'PLATFORM_RETAINER',
  'SAAS',
  'SEAT_BASED',
  'SUBSCRIPTION',
  'USAGE_BASED'
]);

const ZERO_TAX_OVERRIDES = new Set([
  'NO_TAX',
  'VAT_EXEMPT',
  'VAT_ZERO',
  'ZERO_RATED'
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

/**
 * @function deepFreeze
 * @description Recursively freezes nested matrix entries so frontend code cannot mutate statutory fallback data.
 * @param {Object|Array} value - Object or array to freeze.
 * @returns {Object|Array} Frozen value.
 */
const deepFreeze = (value) => {
  if (!value || typeof value !== 'object' || Object.isFrozen(value)) return value;
  Object.values(value).forEach(child => deepFreeze(child));
  return Object.freeze(value);
};

export const SOVEREIGN_TAX_MATRIX = deepFreeze({
  ZA: {
    jurisdiction: 'ZA',
    taxType: 'VAT',
    name: 'South African Value-Added Tax',
    authority: 'South African Revenue Service',
    rate: 0.15,
    standardRate: 0.15,
    sourceStatus: 'OFFICIAL_STATIC_2026_RESEARCHED',
    lastVerifiedAt: DEFAULT_TAX_POINT_DATE,
    sourceUrls: [
      'https://www.gov.za/services/services-organisations/tax/vat/register-vat',
      'https://www.sars.gov.za/businesses-and-employers/my-business-and-tax/vat-connect-issue-19-june-2025/'
    ],
    invoiceNote: 'South African standard VAT applied where the supply is taxable and no exemption or zero-rating evidence is present.'
  },
  NG: {
    jurisdiction: 'NG',
    taxType: 'VAT',
    name: 'Nigerian Value-Added Tax',
    authority: 'Nigeria Revenue Service / legacy FIRS guidance',
    rate: 0.075,
    standardRate: 0.075,
    sourceStatus: 'OFFICIAL_STATIC_REQUIRES_NRS_RECONFIRMATION',
    lastVerifiedAt: DEFAULT_TAX_POINT_DATE,
    sourceUrls: [
      'https://old.firs.gov.ng/wp-content/uploads/2020/10/VAT-FORM-20-02-20.pdf',
      'https://old.firs.gov.ng/wp-content/uploads/2021/06/CLARIFICATION-ON-THE-IMPLEMENTATION-OF-THE-VALUE-ADDED-TAX-VAT-ACT.pdf'
    ],
    invoiceNote: 'Nigeria VAT fallback uses the 7.5% return-form and FIRS clarification evidence; reconnect live NRS matrix before high-value statutory filing.'
  },
  KE: {
    jurisdiction: 'KE',
    taxType: 'VAT',
    name: 'Kenyan Value-Added Tax',
    authority: 'Kenya Revenue Authority',
    rate: 0.16,
    standardRate: 0.16,
    sourceStatus: 'OFFICIAL_STATIC_2026_RESEARCHED',
    lastVerifiedAt: DEFAULT_TAX_POINT_DATE,
    sourceUrls: ['https://kra.go.ke/individual/filing-paying/types-of-taxes/value-added-tax'],
    invoiceNote: 'Kenya general VAT rate applied to taxable supplies unless zero-rated or exempt evidence is attached.'
  },
  GH: {
    jurisdiction: 'GH',
    taxType: 'VAT_PLUS_LEVIES',
    name: 'Ghana VAT with statutory levy stack',
    authority: 'Ghana Revenue Authority',
    rate: 0.20,
    standardRate: 0.15,
    levies: [
      { code: 'NHIL', name: 'National Health Insurance Levy', rate: 0.025 },
      { code: 'GETFUND', name: 'Ghana Education Trust Fund Levy', rate: 0.025 }
    ],
    sourceStatus: 'OFFICIAL_STATIC_2026_RESEARCHED',
    lastVerifiedAt: DEFAULT_TAX_POINT_DATE,
    sourceUrls: ['https://gra.gov.gh/domestic-tax/tax-types/vat/'],
    invoiceNote: 'Ghana fallback separates 15% VAT from the 2.5% NHIL and 2.5% GETFund levy stack for invoice proof.'
  },
  BW: {
    jurisdiction: 'BW',
    taxType: 'VAT',
    name: 'Botswana Value-Added Tax',
    authority: 'Botswana Unified Revenue Service',
    rate: 0.14,
    standardRate: 0.14,
    sourceStatus: 'GOV_PORTAL_STATIC_REQUIRES_BURS_CONFIRMATION',
    lastVerifiedAt: DEFAULT_TAX_POINT_DATE,
    sourceUrls: ['https://www.doingbusiness.co.bw/registering-for-vat'],
    invoiceNote: 'Botswana fallback is 14%; live BURS-connected rate service should confirm before statutory filing.'
  },
  NA: {
    jurisdiction: 'NA',
    taxType: 'VAT',
    name: 'Namibian Value-Added Tax',
    authority: 'Namibia Revenue Agency',
    rate: 0.15,
    standardRate: 0.15,
    sourceStatus: 'SECONDARY_STATIC_REQUIRES_NAMRA_CONFIRMATION',
    lastVerifiedAt: DEFAULT_TAX_POINT_DATE,
    sourceUrls: ['https://www.namra.org.na/'],
    invoiceNote: 'Namibia fallback uses 15% with a live NamRA source required before final statutory filing.'
  },
  MU: {
    jurisdiction: 'MU',
    taxType: 'VAT',
    name: 'Mauritian Value-Added Tax',
    authority: 'Mauritius Revenue Authority',
    rate: 0.15,
    standardRate: 0.15,
    sourceStatus: 'OFFICIAL_STATIC_2026_RESEARCHED',
    lastVerifiedAt: DEFAULT_TAX_POINT_DATE,
    sourceUrls: ['https://mra.mu/index.php/taxes-duties/26-vat'],
    invoiceNote: 'Mauritius VAT fallback is 15% for taxable supplies unless an exemption or zero-rate basis is attached.'
  },
  GB: {
    jurisdiction: 'GB',
    taxType: 'VAT',
    name: 'United Kingdom Value-Added Tax',
    authority: 'HM Revenue & Customs',
    rate: 0.20,
    standardRate: 0.20,
    sourceStatus: 'OFFICIAL_STATIC_2026_RESEARCHED',
    lastVerifiedAt: DEFAULT_TAX_POINT_DATE,
    sourceUrls: ['https://www.gov.uk/vat-rates'],
    invoiceNote: 'UK standard VAT applied to taxable supplies unless reduced, zero-rated or exempt treatment is proven.'
  },
  AE: {
    jurisdiction: 'AE',
    taxType: 'VAT',
    name: 'United Arab Emirates Value-Added Tax',
    authority: 'UAE Federal Tax Authority',
    rate: 0.05,
    standardRate: 0.05,
    sourceStatus: 'OFFICIAL_STATIC_2026_RESEARCHED',
    lastVerifiedAt: DEFAULT_TAX_POINT_DATE,
    sourceUrls: [
      'https://u.ae/en/information-and-services/finance-and-investment/taxation/vat/valueaddedtaxvat',
      'https://tax.gov.ae/en/search/genericcontent/what.is.a.taxable.supply.aspx'
    ],
    invoiceNote: 'UAE VAT fallback is 5% for taxable supplies unless a 0% or exempt rule is evidenced.'
  },
  SG: {
    jurisdiction: 'SG',
    taxType: 'GST',
    name: 'Singapore Goods and Services Tax',
    authority: 'Inland Revenue Authority of Singapore',
    rate: 0.09,
    standardRate: 0.09,
    sourceStatus: 'OFFICIAL_STATIC_2026_RESEARCHED',
    lastVerifiedAt: DEFAULT_TAX_POINT_DATE,
    sourceUrls: ['https://www.iras.gov.sg/taxes/goods-services-tax-%28gst%29/charging-gst-%28output-tax%29/when-to-charge-goods-and-services-tax-%28gst%29'],
    invoiceNote: 'Singapore GST fallback is 9% for local taxable supplies unless the supply is exported, international, or exempt.'
  },
  AU: {
    jurisdiction: 'AU',
    taxType: 'GST',
    name: 'Australian Goods and Services Tax',
    authority: 'Australian Taxation Office',
    rate: 0.10,
    standardRate: 0.10,
    sourceStatus: 'OFFICIAL_STATIC_2026_RESEARCHED',
    lastVerifiedAt: DEFAULT_TAX_POINT_DATE,
    sourceUrls: [
      'https://business.gov.au/registrations/register-for-taxes/register-for-goods-and-services-tax-gst',
      'https://www.ato.gov.au/about-ato/research-and-statistics/in-detail/tax-gap/a-h-tax-gaps/goods-and-services-tax-gap/overview'
    ],
    invoiceNote: 'Australian GST fallback is 10% for most taxable supplies sold or consumed in Australia.'
  }
});

/**
 * @function stableStringify
 * @description Serializes data with deterministic key order for repeatable SHA3 proof generation.
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
 * @function createTaxProofHash
 * @description Creates a SHA3-512 proof hash over the canonical tax calculation payload.
 * @param {Object} payload - Calculation payload to seal.
 * @returns {string} Uppercase SHA3-512 digest.
 */
export const createTaxProofHash = (payload) => sha3_512(stableStringify(payload)).toUpperCase();

/**
 * @function normalizeJurisdictionCode
 * @description Normalizes country aliases into ISO 3166-1 alpha-2 tax jurisdiction codes.
 * @param {string} value - Raw jurisdiction input.
 * @param {string} fallback - Fallback jurisdiction.
 * @returns {string} Normalized jurisdiction code.
 */
export const normalizeJurisdictionCode = (value, fallback = 'ZA') => {
  const raw = String(value || fallback || 'ZA').trim().toUpperCase();
  if (!raw) return 'ZA';
  if (raw === 'UK') return 'GB';
  if (raw === 'UAE') return 'AE';
  if (raw === 'EU' || raw === 'EUROPEAN_UNION') return 'EU_DEFAULT';
  const sanitized = raw.replace(/[^A-Z]/g, '');
  return sanitized.length > 2 ? sanitized.slice(0, 2) : sanitized;
};

/**
 * @function normalizeCurrency
 * @description Normalizes currency codes for minor-unit conversion.
 * @param {string} value - Raw currency input.
 * @returns {string} ISO-like uppercase currency code.
 */
export const normalizeCurrency = (value = 'ZAR') => String(value || 'ZAR').trim().toUpperCase().slice(0, 3) || 'ZAR';

/**
 * @function normalizeClientType
 * @description Normalizes customer type to a controlled B2B/B2C value.
 * @param {string} value - Raw customer type.
 * @returns {string} B2B or B2C.
 */
export const normalizeClientType = (value = 'B2B') => (String(value).toUpperCase() === 'B2C' ? 'B2C' : 'B2B');

/**
 * @function normalizeSupplyType
 * @description Converts invoice classes and billing models into a controlled supply type.
 * @param {string} value - Raw supply type.
 * @returns {string} Normalized supply type.
 */
export const normalizeSupplyType = (value = 'DIGITAL_SERVICE') => (
  String(value || 'DIGITAL_SERVICE').trim().toUpperCase().replace(/[^A-Z0-9_]/g, '_') || 'DIGITAL_SERVICE'
);

/**
 * @function normalizeRate
 * @description Normalizes fractional or percentage-style rates into a decimal fraction.
 * @param {number|string|null|undefined} value - Rate input, e.g. 0.15 or 15.
 * @param {number|null} fallback - Fallback rate when the input is invalid.
 * @returns {number|null} Decimal rate.
 */
export const normalizeRate = (value, fallback = 0) => {
  const rate = Number(value);
  if (!Number.isFinite(rate)) return fallback;
  if (rate > 1 && rate <= 100) return rate / 100;
  return rate;
};

/**
 * @function getCurrencyExponent
 * @description Resolves the number of decimal places used by a currency for minor-unit math.
 * @param {string} currency - Currency code.
 * @returns {number} Currency exponent.
 */
export const getCurrencyExponent = (currency = 'ZAR') => CURRENCY_EXPONENTS[normalizeCurrency(currency)] ?? 2;

/**
 * @function toMinorUnits
 * @description Converts a display amount into integer minor units with decimal-string rounding.
 * @param {number|string} value - Display amount.
 * @param {string} currency - Currency code.
 * @returns {number} Minor-unit integer.
 */
export const toMinorUnits = (value, currency = 'ZAR') => {
  const exponent = getCurrencyExponent(currency);
  const scale = 10 ** exponent;

  if (typeof value === 'number' && Number.isFinite(value)) {
    return Math.round(value * scale);
  }

  const raw = String(value ?? '0').trim().replace(/,/g, '');
  if (!raw) return 0;
  const sign = raw.startsWith('-') ? -1 : 1;
  const sanitized = raw.replace(/^[+-]/, '');
  const [wholeRaw = '0', fractionRaw = ''] = sanitized.split('.');
  const whole = Number(wholeRaw.replace(/[^\d]/g, '') || 0);
  const fractionDigits = fractionRaw.replace(/[^\d]/g, '');

  if (exponent === 0) {
    const roundedWhole = whole + (Number(fractionDigits[0] || 0) >= 5 ? 1 : 0);
    return sign * roundedWhole;
  }

  const padded = fractionDigits.padEnd(exponent + 1, '0');
  const keptMinor = Number(padded.slice(0, exponent) || 0);
  const roundingUnit = Number(padded[exponent] || 0) >= 5 ? 1 : 0;
  return sign * ((whole * scale) + keptMinor + roundingUnit);
};

/**
 * @function fromMinorUnits
 * @description Converts integer minor units into a decimal display amount.
 * @param {number} minorUnits - Minor-unit integer.
 * @param {string} currency - Currency code.
 * @returns {number} Display amount.
 */
export const fromMinorUnits = (minorUnits, currency = 'ZAR') => {
  const exponent = getCurrencyExponent(currency);
  const scale = 10 ** exponent;
  return Number((Number(minorUnits || 0) / scale).toFixed(exponent));
};

/**
 * @function multiplyMinorUnitsByRate
 * @description Applies a decimal tax rate to minor units using basis-point rounding.
 * @param {number} minorUnits - Base amount in minor units.
 * @param {number|string} rate - Decimal or percentage-style rate.
 * @returns {number} Rounded tax amount in minor units.
 */
export const multiplyMinorUnitsByRate = (minorUnits, rate) => {
  const basisPoints = Math.round(Number(normalizeRate(rate, 0)) * RATE_DENOMINATOR);
  return Math.round((Number(minorUnits || 0) * basisPoints) / RATE_DENOMINATOR);
};

/**
 * @function extractApiPayload
 * @description Normalizes mixed Wilsy API response envelopes.
 * @param {Object} response - Axios response.
 * @returns {Object|null} Response payload.
 */
const extractApiPayload = (response) => response?.data?.data || response?.data || null;

/**
 * @function cloneProfile
 * @description Creates a defensive copy of a tax profile before it is enriched for a calculation.
 * @param {Object} profile - Rate profile.
 * @returns {Object} Cloned profile.
 */
const cloneProfile = (profile = {}) => JSON.parse(JSON.stringify(profile || {}));

/**
 * @function hasTaxIdentityEvidence
 * @description Determines whether the invoice has enough customer tax identity evidence for reverse-charge posture.
 * @param {Object} params - Evidence inputs.
 * @param {string} params.customerTaxId - Customer VAT/GST/tax id.
 * @param {Array<string|Object>} params.evidence - Additional evidence records.
 * @returns {boolean} True when identity evidence exists.
 */
const hasTaxIdentityEvidence = ({ customerTaxId, evidence = [] } = {}) => (
  Boolean(String(customerTaxId || '').trim())
  || (Array.isArray(evidence) && evidence.some(item => String(item?.type || item || '').toUpperCase().includes('TAX')))
);

/**
 * @function shouldDestinationTaxDigitalSupply
 * @description Determines whether a cross-border consumer supply should be treated as destination-taxed.
 * @param {string} supplyType - Normalized supply type.
 * @returns {boolean} True when digital destination-tax posture should apply.
 */
const shouldDestinationTaxDigitalSupply = (supplyType) => DIGITAL_SUPPLY_TYPES.has(normalizeSupplyType(supplyType));

/**
 * @function buildSourceSilentProfile
 * @description Builds an honest no-rate profile for jurisdictions absent from live and fallback sources.
 * @param {string} jurisdiction - Jurisdiction code.
 * @returns {Object} Source-silent profile.
 */
const buildSourceSilentProfile = (jurisdiction) => ({
  jurisdiction,
  taxType: 'SOURCE_SILENT',
  name: `${jurisdiction} tax rate unavailable`,
  authority: 'UNRESOLVED_TAX_AUTHORITY',
  rate: null,
  standardRate: null,
  sourceStatus: jurisdiction === 'EU_DEFAULT' || EU_COUNTRY_CODES.has(jurisdiction) ? 'LIVE_RATE_REQUIRED' : 'SOURCE_SILENT',
  lastVerifiedAt: null,
  sourceUrls: jurisdiction === 'EU_DEFAULT' || EU_COUNTRY_CODES.has(jurisdiction)
    ? ['https://europa.eu/youreurope/business/taxation/vat/vat-rules-rates/index_en.htm']
    : [],
  warnings: [
    jurisdiction === 'EU_DEFAULT' || EU_COUNTRY_CODES.has(jurisdiction)
      ? 'EU VAT rates vary by member state. Configure a live rate service or jurisdiction matrix before charging B2C EU VAT.'
      : `No live or fallback tax rate exists for ${jurisdiction}.`
  ],
  invoiceNote: 'Tax rate unavailable. Invoice should remain in review until a statutory rate source is connected.'
});

/**
 * @function buildRateComponents
 * @description Expands a tax profile into taxable components, including statutory levy stacks.
 * @param {Object} profile - Tax profile.
 * @returns {Array<Object>} Tax components.
 */
const buildRateComponents = (profile = {}) => {
  const components = [];
  const baseRate = normalizeRate(profile.standardRate ?? profile.rate, null);

  if (baseRate !== null && baseRate > 0) {
    components.push({
      code: profile.taxType || 'TAX',
      name: profile.name || profile.taxType || 'Tax',
      rate: baseRate
    });
  }

  (profile.levies || []).forEach(levy => {
    const levyRate = normalizeRate(levy.rate, null);
    if (levyRate !== null && levyRate > 0) {
      components.push({
        code: levy.code || levy.name || 'LEVY',
        name: levy.name || levy.code || 'Statutory levy',
        rate: levyRate
      });
    }
  });

  return components;
};

/**
 * @function normalizeLiveProfile
 * @description Converts a backend tax-rate row into the GlobalTaxEngine profile shape.
 * @param {Object} rawProfile - Raw live profile.
 * @param {string} requestedJurisdiction - Requested jurisdiction code.
 * @returns {Object|null} Normalized profile.
 */
const normalizeLiveProfile = (rawProfile, requestedJurisdiction) => {
  const raw = rawProfile?.profile || rawProfile?.taxProfile || rawProfile?.rateProfile || rawProfile;
  if (!raw || typeof raw !== 'object') return null;

  const jurisdiction = normalizeJurisdictionCode(raw.jurisdiction || raw.countryCode || raw.country || requestedJurisdiction);
  const baseRate = normalizeRate(raw.standardRate ?? raw.rate ?? raw.vatRate ?? raw.gstRate, null);
  const levies = Array.isArray(raw.levies)
    ? raw.levies.map(levy => ({ ...levy, rate: normalizeRate(levy.rate, 0) }))
    : [];
  const effectiveRate = normalizeRate(raw.effectiveRate, null)
    ?? (baseRate !== null ? baseRate + levies.reduce((sum, levy) => sum + Number(levy.rate || 0), 0) : null);

  if (effectiveRate === null && !levies.length) return null;

  return {
    jurisdiction,
    taxType: raw.taxType || raw.type || 'VAT',
    name: raw.name || `${jurisdiction} live tax profile`,
    authority: raw.authority || raw.sourceAuthority || 'LIVE_TAX_RATE_SERVICE',
    rate: effectiveRate,
    standardRate: baseRate ?? effectiveRate,
    levies,
    sourceStatus: raw.sourceStatus || 'LIVE_RATE_SERVICE',
    lastVerifiedAt: raw.lastVerifiedAt || raw.updatedAt || new Date().toISOString(),
    sourceUrls: Array.isArray(raw.sourceUrls) ? raw.sourceUrls : [],
    invoiceNote: raw.invoiceNote || 'Live tax-rate service supplied this invoice tax profile.',
    warnings: Array.isArray(raw.warnings) ? raw.warnings : []
  };
};

/**
 * @function normalizeMatrixPayload
 * @description Converts a backend matrix payload into keyed jurisdiction profiles.
 * @param {Object|Array} payload - Raw matrix payload.
 * @returns {Object} Normalized matrix object.
 */
const normalizeMatrixPayload = (payload) => {
  const raw = payload?.matrix || payload?.rates || payload?.jurisdictions || payload;
  if (Array.isArray(raw)) {
    return raw.reduce((acc, row) => {
      const profile = normalizeLiveProfile(row, row?.jurisdiction || row?.countryCode);
      if (profile?.jurisdiction) acc[profile.jurisdiction] = profile;
      return acc;
    }, {});
  }

  if (!raw || typeof raw !== 'object') return {};

  return Object.entries(raw).reduce((acc, [key, value]) => {
    const profile = normalizeLiveProfile({ jurisdiction: key, ...value }, key);
    if (profile?.jurisdiction) acc[profile.jurisdiction] = profile;
    return acc;
  }, {});
};

/**
 * @class GlobalTaxEngine
 * @description Computes source-attributed VAT/GST/sales-tax posture with cryptographic proof and safe degradation.
 */
class GlobalTaxEngine {
  /**
   * @constructor
   * @param {Object} config - Engine configuration.
   * @param {Object} [config.apiClient] - Axios-compatible client.
   * @param {number} [config.cacheTtlMs] - Live rate cache TTL.
   * @param {Object} [config.staticMatrix] - Static fallback tax matrix.
   */
  constructor(config = {}) {
    this.engineVersion = config.engineVersion || GLOBAL_TAX_ENGINE_VERSION;
    this.apiClient = config.apiClient || api;
    this.cacheTtlMs = Number(config.cacheTtlMs || LIVE_RATE_CACHE_TTL_MS);
    this.staticMatrix = new Map(Object.entries(config.staticMatrix || SOVEREIGN_TAX_MATRIX));
    this.liveRateCache = new Map();
    this.liveBackoffUntil = 0;
    this.lastMatrixSync = null;
  }

  /**
   * @method createTraceId
   * @description Creates a compact tax trace id for invoice and telemetry correlation.
   * @returns {string} Trace id.
   */
  createTraceId() {
    const cryptoSource = typeof crypto !== 'undefined' ? crypto : null;
    const entropy = cryptoSource?.randomUUID
      ? cryptoSource.randomUUID().slice(0, 12)
      : `${Date.now().toString(36)}${Math.random().toString(36).slice(2, 8)}`;
    return `TAX-${Date.now().toString(36).toUpperCase()}-${entropy.toUpperCase()}`;
  }

  /**
   * @method getFallbackProfile
   * @description Returns a researched fallback rate profile or a source-silent profile.
   * @param {string} jurisdiction - Jurisdiction code.
   * @returns {Object} Tax profile.
   */
  getFallbackProfile(jurisdiction) {
    const code = normalizeJurisdictionCode(jurisdiction);
    if (this.staticMatrix.has(code)) {
      return cloneProfile({ ...this.staticMatrix.get(code), fallbackUsed: true });
    }
    return buildSourceSilentProfile(code);
  }

  /**
   * @method fetchLiveProfile
   * @description Attempts to resolve a jurisdiction from backend/live tax-rate endpoints.
   * @param {string} jurisdiction - Jurisdiction code.
   * @param {Object} options - Live lookup options.
   * @param {string} [options.taxPointDate] - Tax-point date.
   * @param {boolean} [options.preferFallbackMatrix=false] - Skip optional live probes and use researched fallback matrix first.
   * @returns {Promise<Object|null>} Live profile or null.
   */
  async fetchLiveProfile(jurisdiction, options = {}) {
    if (options.preferFallbackMatrix || options.suppressLiveProbe) return null;
    if (Date.now() < this.liveBackoffUntil && !options.forceRefresh) return null;

    for (const endpoint of TAX_RATE_ENDPOINTS) {
      try {
        const response = await this.apiClient.get(endpoint, {
          params: {
            jurisdiction,
            date: options.taxPointDate || new Date().toISOString().slice(0, 10),
            supplyType: options.supplyType,
            clientType: options.clientType
          }
        });
        const profile = normalizeLiveProfile(extractApiPayload(response), jurisdiction);
        if (profile) return profile;
      } catch (error) {
        if (error.response?.status === 503 || error.isSourceBackoff) {
          this.liveBackoffUntil = Date.now() + LIVE_SYNC_BACKOFF_MS;
          return null;
        }
        continue;
      }
    }

    this.liveBackoffUntil = Date.now() + LIVE_SYNC_BACKOFF_MS;
    return null;
  }

  /**
   * @method getJurisdictionRate
   * @description Resolves a jurisdiction rate from cache, live backend, or researched fallback matrix.
   * @param {string} countryCode - ISO country code.
   * @param {Object} options - Resolution options.
   * @param {boolean} [options.forceRefresh=false] - Whether to bypass cache.
   * @param {boolean} [options.preferFallbackMatrix=false] - Whether to avoid live endpoint probing for optional previews.
   * @returns {Promise<Object>} Tax profile.
   */
  async getJurisdictionRate(countryCode, options = {}) {
    const jurisdiction = normalizeJurisdictionCode(countryCode);
    const cacheKey = `${jurisdiction}:${options.taxPointDate || 'CURRENT'}:${options.supplyType || 'ANY'}:${options.clientType || 'ANY'}`;
    const cached = this.liveRateCache.get(cacheKey);

    if (!options.forceRefresh && cached && cached.expiresAt > Date.now()) {
      return cloneProfile({ ...cached.profile, cacheStatus: 'LIVE_CACHE_HIT' });
    }

    const liveProfile = await this.fetchLiveProfile(jurisdiction, options);
    if (liveProfile) {
      this.liveRateCache.set(cacheKey, {
        profile: liveProfile,
        expiresAt: Date.now() + this.cacheTtlMs
      });
      return cloneProfile(liveProfile);
    }

    return this.getFallbackProfile(jurisdiction);
  }

  /**
   * @method determineTaxPosture
   * @description Determines cross-border, reverse-charge, and destination-tax rules from invoice coordinates.
   * @param {Object} params - Posture inputs.
   * @param {string} params.tenantJurisdiction - Seller/tenant jurisdiction.
   * @param {string} params.clientJurisdiction - Customer jurisdiction.
   * @param {string} params.clientType - B2B or B2C.
   * @param {string} params.supplyType - Supply type.
   * @param {string} params.customerTaxId - Customer tax id.
   * @param {Array<string|Object>} params.evidence - Supporting evidence.
   * @returns {Object} Tax posture.
   */
  determineTaxPosture({
    tenantJurisdiction,
    clientJurisdiction,
    clientType,
    supplyType,
    customerTaxId,
    evidence = []
  }) {
    const tenant = normalizeJurisdictionCode(tenantJurisdiction);
    const client = normalizeJurisdictionCode(clientJurisdiction, tenant);
    const normalizedClientType = normalizeClientType(clientType);
    const normalizedSupplyType = normalizeSupplyType(supplyType);
    const crossBorder = tenant !== client;
    const customerTaxEvidence = hasTaxIdentityEvidence({ customerTaxId, evidence });
    const warnings = [];
    const evidenceRequired = [];
    let rule = 'DOMESTIC_SUPPLY';
    let taxingJurisdiction = tenant;
    let reverseChargeApplied = false;
    let reverseChargeReviewRequired = false;

    if (crossBorder && normalizedClientType === 'B2B') {
      rule = customerTaxEvidence ? 'B2B_REVERSE_CHARGE_CANDIDATE' : 'B2B_TAX_ID_REQUIRED';
      taxingJurisdiction = client;
      evidenceRequired.push('CUSTOMER_TAX_ID_OR_EXEMPTION_CERTIFICATE');
      if (customerTaxEvidence) {
        reverseChargeApplied = true;
      } else {
        reverseChargeReviewRequired = true;
        warnings.push('Cross-border B2B invoice has no customer tax id evidence. Reverse charge is not applied automatically.');
      }
    } else if (crossBorder && shouldDestinationTaxDigitalSupply(normalizedSupplyType)) {
      rule = 'DESTINATION_DIGITAL_CONSUMER_SUPPLY';
      taxingJurisdiction = client;
      evidenceRequired.push('CUSTOMER_LOCATION_EVIDENCE');
      warnings.push('Cross-border digital B2C supply uses destination jurisdiction and may require non-resident registration thresholds or OSS/IOSS review.');
    } else if (crossBorder) {
      rule = 'CROSS_BORDER_DESTINATION_REVIEW';
      taxingJurisdiction = client;
      evidenceRequired.push('CUSTOMS_OR_PLACE_OF_SUPPLY_REVIEW');
      warnings.push('Cross-border non-digital supply requires place-of-supply/import review before statutory filing.');
    }

    return {
      tenant,
      client,
      clientType: normalizedClientType,
      supplyType: normalizedSupplyType,
      crossBorder,
      taxingJurisdiction,
      rule,
      reverseChargeApplied,
      reverseChargeReviewRequired,
      customerTaxEvidence,
      evidenceRequired,
      warnings
    };
  }

  /**
   * @method buildEffectiveProfile
   * @description Applies zero/exempt overrides and reverse-charge posture to a jurisdiction profile.
   * @param {Object} params - Effective profile inputs.
   * @param {Object} params.profile - Jurisdiction profile.
   * @param {Object} params.posture - Tax posture.
   * @param {string|null} params.taxTypeOverride - Operator tax type override.
   * @returns {Object} Effective tax profile.
   */
  buildEffectiveProfile({ profile, posture, taxTypeOverride }) {
    const override = taxTypeOverride ? String(taxTypeOverride).toUpperCase() : null;
    const warnings = [...(profile.warnings || []), ...(posture.warnings || [])];

    if (override && ZERO_TAX_OVERRIDES.has(override)) {
      warnings.push(`${override} override applied. Attach statutory exemption, zero-rating, or no-tax evidence before filing.`);
      return {
        ...profile,
        taxType: override,
        name: `Policy override: ${override}`,
        rate: 0,
        standardRate: 0,
        levies: [],
        sourceStatus: 'OPERATOR_OVERRIDE_REQUIRES_EVIDENCE',
        isZeroRated: true,
        overrideApplied: true,
        reverseChargeApplied: false,
        liveRateRequired: false,
        warnings,
        invoiceNote: `${override} applied by operator policy. Evidence is required for audit.`
      };
    }

    if (posture.reverseChargeApplied) {
      return {
        ...profile,
        taxType: 'REVERSE_CHARGE',
        name: 'Reverse charge / customer self-accounting',
        rate: 0,
        standardRate: 0,
        levies: [],
        sourceStatus: profile.sourceStatus || 'REVERSE_CHARGE',
        isZeroRated: true,
        overrideApplied: false,
        reverseChargeApplied: true,
        liveRateRequired: false,
        warnings,
        invoiceNote: 'Reverse charge applied because cross-border B2B customer tax identity evidence is present. Customer accounts for VAT/GST where required.'
      };
    }

    const components = buildRateComponents(profile);
    const effectiveRate = components.reduce((sum, item) => sum + Number(item.rate || 0), 0);
    const liveRateRequired = profile.rate === null || profile.sourceStatus === 'LIVE_RATE_REQUIRED' || (!components.length && profile.sourceStatus === 'SOURCE_SILENT');

    if (liveRateRequired) {
      warnings.push('No chargeable tax amount was computed because the jurisdiction needs a live statutory rate source.');
    }

    return {
      ...profile,
      rate: liveRateRequired ? 0 : effectiveRate,
      effectiveRate: liveRateRequired ? 0 : effectiveRate,
      components,
      isZeroRated: effectiveRate === 0,
      overrideApplied: false,
      reverseChargeApplied: false,
      liveRateRequired,
      warnings
    };
  }

  /**
   * @method calculate
   * @description Calculates tax, withholding, source posture, and a SHA3 proof packet for an invoice amount.
   * @param {Object} params - Calculation parameters.
   * @param {number|string} params.amount - Net invoice amount before tax.
   * @param {string} [params.currency='ZAR'] - Currency code.
   * @param {string} [params.tenantJurisdiction='ZA'] - Seller/tenant jurisdiction.
   * @param {string} [params.clientJurisdiction='ZA'] - Customer jurisdiction.
   * @param {string} [params.clientType='B2B'] - B2B or B2C.
   * @param {string} [params.supplyType='DIGITAL_SERVICE'] - Supply type.
   * @param {string} [params.customerTaxId] - Customer VAT/GST/tax id.
   * @param {Array<string|Object>} [params.evidence=[]] - Supporting tax evidence.
   * @param {string|null} [params.taxTypeOverride=null] - Optional zero/exempt/no-tax override.
   * @param {number|string} [params.withholdingRate=0] - Withholding rate as decimal or percentage.
   * @param {string} [params.tenantId='GLOBAL_ROOT'] - Tenant for telemetry.
   * @param {string} [params.issueDate] - Invoice issue date.
   * @param {boolean} [params.forceRefreshRates=false] - Whether to force live-rate refresh.
   * @param {boolean} [params.preferFallbackMatrix=false] - Whether to use researched matrix before optional live probes.
   * @param {boolean} [params.suppressLiveProbe=false] - Whether to suppress optional live tax endpoint probes.
   * @returns {Promise<Object>} Sealed tax calculation packet.
   */
  async calculate(params = {}) {
    const traceId = this.createTraceId();
    const generatedAt = new Date().toISOString();
    const currency = normalizeCurrency(params.currency || 'ZAR');
    const amountMinor = toMinorUnits(params.amount ?? 0, currency);

    if (!Number.isFinite(amountMinor) || amountMinor < 0) {
      throw new Error(`[GLOBAL_TAX_ENGINE] Invalid non-negative invoice amount required. Trace: ${traceId}`);
    }

    try {
      const posture = this.determineTaxPosture({
        tenantJurisdiction: params.tenantJurisdiction || 'ZA',
        clientJurisdiction: params.clientJurisdiction || params.tenantJurisdiction || 'ZA',
        clientType: params.clientType || 'B2B',
        supplyType: params.supplyType || 'DIGITAL_SERVICE',
        customerTaxId: params.customerTaxId,
        evidence: params.evidence || []
      });

      const profile = await this.getJurisdictionRate(posture.taxingJurisdiction, {
        forceRefresh: Boolean(params.forceRefreshRates),
        preferFallbackMatrix: Boolean(params.preferFallbackMatrix),
        suppressLiveProbe: Boolean(params.suppressLiveProbe),
        taxPointDate: params.issueDate || generatedAt.slice(0, 10),
        supplyType: posture.supplyType,
        clientType: posture.clientType
      });

      const effectiveProfile = this.buildEffectiveProfile({
        profile,
        posture,
        taxTypeOverride: params.taxTypeOverride
      });

      const components = effectiveProfile.liveRateRequired
        ? []
        : (effectiveProfile.components || buildRateComponents(effectiveProfile));
      const componentAmounts = components.map(component => ({
        ...component,
        amountMinor: multiplyMinorUnitsByRate(amountMinor, component.rate),
        amount: fromMinorUnits(multiplyMinorUnitsByRate(amountMinor, component.rate), currency)
      }));
      const taxAmountMinor = componentAmounts.reduce((sum, component) => sum + Number(component.amountMinor || 0), 0);
      const totalAmountMinor = amountMinor + taxAmountMinor;
      const withholdingRate = normalizeRate(params.withholdingRate, 0);
      const validWithholdingRate = withholdingRate > 0 && withholdingRate < 1 ? withholdingRate : 0;
      const withholdingAmountMinor = multiplyMinorUnitsByRate(amountMinor, validWithholdingRate);
      const netPayableMinor = Math.max(0, totalAmountMinor - withholdingAmountMinor);
      const warnings = [...new Set([
        ...(effectiveProfile.warnings || []),
        ...(validWithholdingRate !== withholdingRate ? ['Invalid withholding rate ignored.'] : [])
      ])];
      const evidenceRequired = [...new Set([
        ...(posture.evidenceRequired || []),
        ...(effectiveProfile.overrideApplied ? ['STATUTORY_OVERRIDE_EVIDENCE'] : [])
      ])];
      const sourceUrls = [...new Set(effectiveProfile.sourceUrls || [])];

      const proofPayload = {
        traceId,
        engineVersion: this.engineVersion,
        generatedAt,
        input: {
          amount: fromMinorUnits(amountMinor, currency),
          currency,
          tenantJurisdiction: posture.tenant,
          clientJurisdiction: posture.client,
          clientType: posture.clientType,
          supplyType: posture.supplyType,
          taxTypeOverride: params.taxTypeOverride || null,
          withholdingRate: validWithholdingRate
        },
        jurisdictionData: {
          tenant: posture.tenant,
          client: posture.client,
          crossBorder: posture.crossBorder,
          taxingJurisdiction: posture.taxingJurisdiction,
          rule: posture.rule,
          customerTaxEvidence: posture.customerTaxEvidence
        },
        taxProfile: {
          type: effectiveProfile.taxType,
          name: effectiveProfile.name,
          authority: effectiveProfile.authority,
          rate: Number(effectiveProfile.rate || 0),
          effectiveRate: Number(effectiveProfile.effectiveRate ?? effectiveProfile.rate ?? 0),
          sourceStatus: effectiveProfile.sourceStatus,
          reverseChargeApplied: Boolean(effectiveProfile.reverseChargeApplied),
          reverseChargeReviewRequired: Boolean(posture.reverseChargeReviewRequired),
          overrideApplied: Boolean(effectiveProfile.overrideApplied),
          liveRateRequired: Boolean(effectiveProfile.liveRateRequired),
          components: componentAmounts.map(component => ({
            code: component.code,
            name: component.name,
            rate: component.rate,
            amount: component.amount
          }))
        },
        financials: {
          currency,
          baseAmount: fromMinorUnits(amountMinor, currency),
          taxAmount: fromMinorUnits(taxAmountMinor, currency),
          withholdingAmount: fromMinorUnits(withholdingAmountMinor, currency),
          totalAmount: fromMinorUnits(totalAmountMinor, currency),
          netPayableAmount: fromMinorUnits(netPayableMinor, currency),
          minorUnits: {
            baseAmount: amountMinor,
            taxAmount: taxAmountMinor,
            withholdingAmount: withholdingAmountMinor,
            totalAmount: totalAmountMinor,
            netPayableAmount: netPayableMinor
          }
        },
        compliance: {
          invoiceNote: effectiveProfile.invoiceNote,
          taxPointDate: params.issueDate || generatedAt.slice(0, 10),
          sourceUrls,
          evidenceRequired,
          warnings
        }
      };

      const proofHash = createTaxProofHash(proofPayload);
      const result = {
        success: true,
        ...proofPayload,
        sourceStatus: effectiveProfile.sourceStatus || profile.sourceStatus || 'SOURCE_SILENT',
        proof: {
          algorithm: 'SHA3-512',
          canonicalization: 'STABLE_JSON_KEY_SORT',
          hash: proofHash,
          canonicalPayload: stableStringify(proofPayload)
        }
      };

      await Promise.resolve(broadcastTelemetry(
        params.tenantId || 'GLOBAL_ROOT',
        'GLOBAL_TAX_ENGINE',
        result.taxProfile.liveRateRequired ? 'LIVE_RATE_REQUIRED' : 'TAX_CALCULATION_SEALED',
        'GlobalTaxEngine',
        {
          traceId,
          jurisdiction: posture.taxingJurisdiction,
          taxType: result.taxProfile.type,
          taxAmount: result.financials.taxAmount,
          proofHash
        }
      )).catch(() => {});

      return result;
    } catch (error) {
      await Promise.resolve(broadcastTelemetry(
        params.tenantId || 'GLOBAL_ROOT',
        'GLOBAL_TAX_ENGINE',
        'TAX_CALCULATION_FAILED',
        'GlobalTaxEngine',
        { traceId, error: error.message }
      )).catch(() => {});
      throw error;
    }
  }

  /**
   * @method calculateFromInvoiceDraft
   * @description Builds a tax calculation from the Revenue Ledger invoice draft shape.
   * @param {Object} draft - Invoice draft.
   * @param {Object} options - Calculation options.
   * @param {boolean} [options.preferFallbackMatrix=false] - Whether to use researched fallback rates before live probes.
   * @param {boolean} [options.suppressLiveProbe=false] - Whether to suppress optional live tax endpoint probes.
   * @returns {Promise<Object>} Sealed tax calculation packet.
   */
  calculateFromInvoiceDraft(draft = {}, options = {}) {
    const quantity = Math.max(1, Number(draft.quantity || 1));
    const unitPrice = Number(draft.unitPrice || draft.amount || 0);
    const amount = Number(draft.amount || (quantity * unitPrice) || 0);
    const invoiceTaxType = String(draft.taxType || 'VAT').toUpperCase();
    const taxTypeOverride = ['VAT', 'GST', 'SALES_TAX', 'VAT_PLUS_LEVIES', 'WITHHOLDING'].includes(invoiceTaxType)
      ? null
      : invoiceTaxType;

    return this.calculate({
      amount,
      currency: draft.currency || 'ZAR',
      tenantJurisdiction: draft.tenantJurisdiction || draft.sellerJurisdiction || options.tenantJurisdiction || 'ZA',
      clientJurisdiction: draft.clientJurisdiction || draft.taxJurisdiction || options.clientJurisdiction || 'ZA',
      clientType: draft.clientType || options.clientType || 'B2B',
      customerTaxId: draft.customerTaxId || draft.clientTaxId || draft.vatNumber || options.customerTaxId,
      supplyType: draft.supplyType || draft.billingModel || draft.invoiceClass || 'DIGITAL_SERVICE',
      evidence: draft.taxEvidence || draft.evidence || [],
      taxTypeOverride,
      withholdingRate: draft.withholdingRate || 0,
      tenantId: draft.tenantId || options.tenantId || 'GLOBAL_ROOT',
      issueDate: draft.issueDate,
      forceRefreshRates: Boolean(options.forceRefreshRates),
      preferFallbackMatrix: Boolean(options.preferFallbackMatrix),
      suppressLiveProbe: Boolean(options.suppressLiveProbe)
    });
  }

  /**
   * @method buildInvoiceTaxConfig
   * @description Converts a sealed tax packet into the invoice API taxConfig shape.
   * @param {Object|null} taxResult - Tax calculation result.
   * @param {Object} draft - Invoice draft fallback.
   * @returns {Object} Invoice tax config.
   */
  buildInvoiceTaxConfig(taxResult = null, draft = {}) {
    if (!taxResult) {
      return {
        jurisdiction: draft.taxJurisdiction || 'ZA',
        rate: 0,
        calculationServiceVersion: `${this.engineVersion}-UNAVAILABLE`,
        sourceStatus: 'SOURCE_SILENT',
        requiresBackendRecalculation: true,
        warnings: ['GlobalTaxEngine calculation was unavailable; backend must recalculate before final posting.']
      };
    }

    return {
      jurisdiction: taxResult.jurisdictionData.taxingJurisdiction,
      originJurisdiction: taxResult.jurisdictionData.tenant,
      customerJurisdiction: taxResult.jurisdictionData.client,
      taxType: taxResult.taxProfile.type,
      rate: taxResult.taxProfile.effectiveRate,
      components: taxResult.taxProfile.components,
      taxAmount: taxResult.financials.taxAmount,
      withholdingAmount: taxResult.financials.withholdingAmount,
      netPayableAmount: taxResult.financials.netPayableAmount,
      calculationServiceVersion: this.engineVersion,
      traceId: taxResult.traceId,
      proofHash: taxResult.proof.hash,
      proofAlgorithm: taxResult.proof.algorithm,
      sourceStatus: taxResult.sourceStatus,
      reverseChargeApplied: taxResult.taxProfile.reverseChargeApplied,
      reverseChargeReviewRequired: taxResult.taxProfile.reverseChargeReviewRequired,
      liveRateRequired: taxResult.taxProfile.liveRateRequired,
      invoiceNote: taxResult.compliance.invoiceNote,
      evidenceRequired: taxResult.compliance.evidenceRequired,
      sourceUrls: taxResult.compliance.sourceUrls,
      warnings: taxResult.compliance.warnings,
      metadata: {
        rule: taxResult.jurisdictionData.rule,
        taxPointDate: taxResult.compliance.taxPointDate,
        canonicalProof: taxResult.proof.canonicalization
      }
    };
  }

  /**
   * @method syncJurisdictionMatrix
   * @description Force-refreshes the in-memory matrix from backend rate services while preserving researched fallbacks.
   * @param {Object} options - Sync options.
   * @param {boolean} [options.forceRefresh=false] - Whether to bypass backoff.
   * @returns {Promise<Object>} Sync result.
   */
  async syncJurisdictionMatrix(options = {}) {
    if (Date.now() < this.liveBackoffUntil && !options.forceRefresh) {
      return {
        success: false,
        status: 'LIVE_SYNC_BACKOFF',
        count: this.staticMatrix.size,
        lastMatrixSync: this.lastMatrixSync
      };
    }

    for (const endpoint of TAX_MATRIX_ENDPOINTS) {
      try {
        const response = await this.apiClient.get(endpoint, { params: { forceRefresh: Boolean(options.forceRefresh) } });
        const matrix = normalizeMatrixPayload(extractApiPayload(response));
        const entries = Object.entries(matrix);
        if (entries.length) {
          entries.forEach(([code, profile]) => this.staticMatrix.set(code, profile));
          this.lastMatrixSync = new Date().toISOString();
          await Promise.resolve(broadcastTelemetry('GLOBAL_ROOT', 'GLOBAL_TAX_ENGINE', 'TAX_MATRIX_SYNCED', 'GlobalTaxEngine', {
            endpoint,
            count: this.staticMatrix.size
          })).catch(() => {});
          return {
            success: true,
            status: 'LIVE_MATRIX_SYNCED',
            endpoint,
            count: this.staticMatrix.size,
            lastMatrixSync: this.lastMatrixSync
          };
        }
      } catch (error) {
        continue;
      }
    }

    this.liveBackoffUntil = Date.now() + LIVE_SYNC_BACKOFF_MS;
    await Promise.resolve(broadcastTelemetry('GLOBAL_ROOT', 'GLOBAL_TAX_ENGINE', 'TAX_MATRIX_SOURCE_SILENT', 'GlobalTaxEngine', {
      count: this.staticMatrix.size
    })).catch(() => {});
    return {
      success: false,
      status: 'SOURCE_SILENT_FALLBACK_PRESERVED',
      count: this.staticMatrix.size,
      lastMatrixSync: this.lastMatrixSync
    };
  }

  /**
   * @method getMatrixSnapshot
   * @description Returns the current fallback/live matrix posture for diagnostics and exports.
   * @returns {Object} Matrix snapshot.
   */
  getMatrixSnapshot() {
    return {
      engineVersion: this.engineVersion,
      count: this.staticMatrix.size,
      lastMatrixSync: this.lastMatrixSync,
      liveBackoffActive: Date.now() < this.liveBackoffUntil,
      jurisdictions: Array.from(this.staticMatrix.keys()).sort()
    };
  }
}

const globalTaxEngine = new GlobalTaxEngine();

export { GlobalTaxEngine };
export default globalTaxEngine;
