/**
 * ============================================================================
 * WILSY OS - FEE TARIFF ENTERPRISE OBJECT
 * ============================================================================
 *
 * @file         FeeTariffObject.js
 * @directory    server/src/enterprise/objects/
 * @system       Wilsy OS - Legal Enterprise Operating System & SaaS Platform
 * @authority    Wilson Khanyezi, Founder & Chief Architect
 * @version      1.0.0-SOVEREIGN
 * @epitome      Generation 2 Sovereign Fee Tariff Kernel Object implementation.
 *               Serves as the rate engine domain entity in Wilsy OS.
 *               Encapsulates statutory court scale tariffs (Magistrate Scales A-D,
 *               High Court Rules 68/70), custom firm rate cards, unit calculations,
 *               and statutory validity date windows.
 *
 * @collaboration
 * - Lead Architect: Wilson Khanyezi (Wilsy OS Architecture Core Team)
 * - Practice Management: Fee Engine & Rate Matrix Subsystem
 * - Regulatory Audit: Rules Board for Courts of Law & LPC Tariff Core
 *
 * ============================================================================
 * INSTITUTIONAL AUDIT TRAIL
 * ============================================================================
 * Date       | Author          | Version | Description
 * -----------|-----------------|---------|------------------------------------
 * 2026-07-24 | Wilson Khanyezi | 1.0.0   | Production-ready Fee Tariff domain object
 *            |                 |         | with statutory scales, unit rules,
 *            |                 |         | and effective date validity gates.
 * ============================================================================
 */

const { BaseEnterpriseObject, OBJECT_LIFECYCLE_STATES } = require('./BaseEnterpriseObject');
const { DataRedactor } = require('../kernel/EnterpriseKernel');

/**
 * Recognized Court & Jurisdictional Tariff Scales.
 */
const TARIFF_JURISDICTION = Object.freeze({
  MAGISTRATE_SCALE_A: 'MAGISTRATE_SCALE_A',
  MAGISTRATE_SCALE_B: 'MAGISTRATE_SCALE_B',
  MAGISTRATE_SCALE_C: 'MAGISTRATE_SCALE_C',
  MAGISTRATE_SCALE_D: 'MAGISTRATE_SCALE_D',
  HIGH_COURT_RULE_70: 'HIGH_COURT_RULE_70',
  HIGH_COURT_RULE_68: 'HIGH_COURT_RULE_68',
  SUPREME_COURT_OF_APPEAL: 'SUPREME_COURT_OF_APPEAL',
  COMMERCIAL_AGREEMENT: 'COMMERCIAL_AGREEMENT',
  CUSTOM_FIRM_SCALE: 'CUSTOM_FIRM_SCALE'
});

/**
 * Fee Calculation Metric Units.
 */
const TARIFF_UNIT = Object.freeze({
  HOURLY: 'HOURLY',
  PER_15_MIN: 'PER_15_MIN',
  PER_FOLIO: 'PER_FOLIO',
  PER_PAGE: 'PER_PAGE',
  PER_KILOMETER: 'PER_KILOMETER',
  FIXED_ITEM: 'FIXED_ITEM'
});

/**
 * Custom Error Class for Fee Tariff Domain Faults.
 */
class FeeTariffObjectError extends Error {
  /**
   * @param {string} message - Error details.
   * @param {string} [code='TARIFF_ERR_GENERIC'] - Standard error code.
   * @param {Object} [details={}] - Additional contextual metadata.
   */
  constructor(message, code = 'TARIFF_ERR_GENERIC', details = {}) {
    super(message);
    this.name = 'FeeTariffObjectError';
    this.code = code;
    this.timestamp = new Date().toISOString();
    this.details = DataRedactor.sanitize(details);
    if (Error.captureStackTrace) {
      Error.captureStackTrace(this, FeeTariffObjectError);
    }
  }
}

/**
 * Sovereign Fee Tariff Domain Object.
 * Encapsulates statutory legal fee scales, custom rate matrices, billing unit metrics,
 * and temporal validity windows in Wilsy OS.
 */
class FeeTariffObject extends BaseEnterpriseObject {
  /**
   * Constructs a FeeTariffObject.
   *
   * @param {Object} params
   * @param {string} params.id - Unique Fee Tariff Identifier (e.g. 'TRF-2026-4099').
   * @param {string} params.tenantId - Sovereign Tenant ID.
   * @param {string} params.tariffCode - Short Code for lookup (e.g. 'HC-R70-ATTENDANCE').
   * @param {string} params.description - Formal narrative description of fee item.
   * @param {string} [params.jurisdiction='COMMERCIAL_AGREEMENT'] - Jurisdiction constant.
   * @param {string} [params.unit='HOURLY'] - Billing unit metric constant.
   * @param {number} params.rateAmount - Rate amount in ZAR per unit.
   * @param {string} [params.effectiveFrom] - ISO Date String when tariff takes effect.
   * @param {string} [params.effectiveTo=null] - ISO Date String when tariff expires (null = indefinite).
   * @param {string} [params.createdById='SYSTEM'] - Operator creating tariff entry.
   */
  constructor({
    id,
    tenantId,
    tariffCode,
    description,
    jurisdiction = TARIFF_JURISDICTION.COMMERCIAL_AGREEMENT,
    unit = TARIFF_UNIT.HOURLY,
    rateAmount,
    effectiveFrom,
    effectiveTo = null,
    createdById = 'SYSTEM'
  }) {
    if (!tariffCode || typeof tariffCode !== 'string' || tariffCode.trim().length === 0) {
      throw new FeeTariffObjectError('Tariff code identifier is required', 'TARIFF_ERR_INVALID_CODE');
    }

    if (!description || typeof description !== 'string' || description.trim().length === 0) {
      throw new FeeTariffObjectError('Tariff description narrative is required', 'TARIFF_ERR_INVALID_DESCRIPTION');
    }

    const rate = Number(rateAmount);
    if (isNaN(rate) || rate < 0) {
      throw new FeeTariffObjectError('Rate amount must be a non-negative number', 'TARIFF_ERR_INVALID_RATE');
    }

    const normJurisdiction = jurisdiction.trim().toUpperCase();
    if (!Object.values(TARIFF_JURISDICTION).includes(normJurisdiction)) {
      throw new FeeTariffObjectError(`Invalid jurisdiction designation [${jurisdiction}]`, 'TARIFF_ERR_INVALID_JURISDICTION');
    }

    const normUnit = unit.trim().toUpperCase();
    if (!Object.values(TARIFF_UNIT).includes(normUnit)) {
      throw new FeeTariffObjectError(`Invalid tariff billing unit [${unit}]`, 'TARIFF_ERR_INVALID_UNIT');
    }

    const validFromDate = effectiveFrom ? new Date(effectiveFrom) : new Date();
    if (isNaN(validFromDate.getTime())) {
      throw new FeeTariffObjectError('Invalid effectiveFrom date timestamp', 'TARIFF_ERR_INVALID_EFFECTIVE_FROM');
    }

    let validToDate = null;
    if (effectiveTo) {
      validToDate = new Date(effectiveTo);
      if (isNaN(validToDate.getTime())) {
        throw new FeeTariffObjectError('Invalid effectiveTo date timestamp', 'TARIFF_ERR_INVALID_EFFECTIVE_TO');
      }
      if (validToDate <= validFromDate) {
        throw new FeeTariffObjectError('effectiveTo date must be strictly after effectiveFrom date', 'TARIFF_ERR_INVALID_DATE_RANGE');
      }
    }

    const initialAttributes = {
      tariffCode: tariffCode.trim().toUpperCase(),
      description: description.trim(),
      jurisdiction: normJurisdiction,
      unit: normUnit,
      rateAmount: Number(rate.toFixed(2)),
      effectiveFrom: validFromDate.toISOString(),
      effectiveTo: validToDate ? validToDate.toISOString() : null,
      isCurrentActive: true
    };

    super({
      id,
      tenantId,
      domain: 'FEE_TARIFF',
      attributes: initialAttributes,
      schemaVersion: '1.0.0',
      status: OBJECT_LIFECYCLE_STATES.ACTIVE,
      createdById
    });
  }

  /**
   * Calculates total fee for a given quantity of units under this tariff.
   *
   * @param {number} quantity - Quantity of units (hours, folios, kilometers, etc.).
   * @returns {number} Calculated total ZAR amount rounded to 2 decimal places.
   */
  calculateFee(quantity) {
    const qty = Number(quantity);
    if (isNaN(qty) || qty <= 0) {
      throw new FeeTariffObjectError('Quantity for fee calculation must be a positive number', 'TARIFF_ERR_INVALID_QUANTITY');
    }

    return Number((this.attributes.rateAmount * qty).toFixed(2));
  }

  /**
   * Checks if this fee tariff was valid on a specific target date.
   *
   * @param {string|Date} targetDate - Date to test validity against.
   * @returns {boolean}
   */
  isValidOnDate(targetDate) {
    const testDate = new Date(targetDate);
    if (isNaN(testDate.getTime())) {
      return false;
    }

    const fromDate = new Date(this.attributes.effectiveFrom);
    if (testDate < fromDate) {
      return false;
    }

    if (this.attributes.effectiveTo) {
      const toDate = new Date(this.attributes.effectiveTo);
      if (testDate > toDate) {
        return false;
      }
    }

    return true;
  }

  /**
   * Deprecates current tariff entry and updates expiry timestamp.
   *
   * @param {string} expirationDate - ISO Date string of retirement.
   * @param {string} operatorId - User retiring tariff.
   * @returns {Object} Revision state.
   */
  retireTariff(expirationDate, operatorId = 'SYSTEM') {
    const expDate = new Date(expirationDate);
    if (isNaN(expDate.getTime())) {
      throw new FeeTariffObjectError('Valid expiration date required to retire tariff', 'TARIFF_ERR_INVALID_EXPIRATION');
    }

    return this.updateAttributes(
      {
        effectiveTo: expDate.toISOString(),
        isCurrentActive: false
      },
      operatorId
    );
  }

  /**
   * Convenience getter for Tariff Code.
   * @returns {string}
   */
  get tariffCode() {
    return this.attributes.tariffCode;
  }

  /**
   * Convenience getter for Rate Amount.
   * @returns {number}
   */
  get rateAmount() {
    return this.attributes.rateAmount;
  }

  /**
   * Convenience getter for Jurisdiction.
   * @returns {string}
   */
  get jurisdiction() {
    return this.attributes.jurisdiction;
  }

  /**
   * Generates a scrubbed overview of tariff details for rate lookup services.
   * @returns {Object}
   */
  getSanitizedSummary() {
    return {
      tariffId: this.id,
      tenantId: this.tenantId,
      tariffCode: this.attributes.tariffCode,
      description: this.attributes.description,
      jurisdiction: this.attributes.jurisdiction,
      unit: this.attributes.unit,
      rateAmount: this.attributes.rateAmount,
      effectiveFrom: this.attributes.effectiveFrom,
      effectiveTo: this.attributes.effectiveTo,
      isCurrentActive: this.attributes.isCurrentActive,
      status: this.status,
      revisionNumber: this.revisionNumber,
      updatedAt: this.updatedAt
    };
  }
}

module.exports = {
  FeeTariffObject,
  FeeTariffObjectError,
  TARIFF_JURISDICTION,
  TARIFF_UNIT
};
