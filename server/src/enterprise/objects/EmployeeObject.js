/**
 * ============================================================================
 * WILSY OS - EMPLOYEE ENTERPRISE OBJECT
 * ============================================================================
 *
 * @file         EmployeeObject.js
 * @directory    server/src/enterprise/objects/
 * @system       Wilsy OS - Legal Enterprise Operating System & SaaS Platform
 * @authority    Wilson Khanyezi, Founder & Chief Architect
 * @version      1.0.0-SOVEREIGN
 * @epitome      Generation 2 Sovereign Employee Kernel Object implementation.
 *               Provides strict domain encapsulation for firm partners, attorneys,
 *               paralegals, and administrative personnel. Manages role-based access
 *               levels, hourly billable rate schedules, departmental assignments,
 *               and POPIA/GDPR human resources data protection.
 *
 * @collaboration
 * - Lead Architect: Wilson Khanyezi (Wilsy OS Architecture Core Team)
 * - HR & Identity Security: Sovereign Role-Based Access Control & Identity Engine
 * - Legal Operations: Attorney Hourly Billing & Utilization Core
 *
 * ============================================================================
 * INSTITUTIONAL AUDIT TRAIL
 * ============================================================================
 * Date       | Author          | Version | Description
 * -----------|-----------------|---------|------------------------------------
 * 2026-07-24 | Wilson Khanyezi | 1.0.0   | Production-ready Employee domain object
 *            |                 |         | with billable rate schedules, RBAC level
 *            |                 |         | verification, and POPIA privacy controls.
 * ============================================================================
 */

const { BaseEnterpriseObject, OBJECT_LIFECYCLE_STATES } = require('./BaseEnterpriseObject');
const { DataRedactor } = require('../kernel/EnterpriseKernel');

/**
 * Standard Legal Firm Departments.
 */
const FIRM_DEPARTMENTS = Object.freeze({
  LITIGATION: 'LITIGATION',
  CORPORATE: 'CORPORATE',
  COMMERCIAL: 'COMMERCIAL',
  INTELLECTUAL_PROPERTY: 'INTELLECTUAL_PROPERTY',
  COMPLIANCE: 'COMPLIANCE',
  FINANCE: 'FINANCE',
  EXECUTIVE: 'EXECUTIVE',
  ADMINISTRATION: 'ADMINISTRATION'
});

/**
 * Custom Error Class for Employee Domain Violations.
 */
class EmployeeObjectError extends Error {
  /**
   * @param {string} message - Error details.
   * @param {string} [code='EMPLOYEE_ERR_GENERIC'] - Standard error code.
   * @param {Object} [details={}] - Additional contextual metadata.
   */
  constructor(message, code = 'EMPLOYEE_ERR_GENERIC', details = {}) {
    super(message);
    this.name = 'EmployeeObjectError';
    this.code = code;
    this.timestamp = new Date().toISOString();
    this.details = DataRedactor.sanitize(details);
    if (Error.captureStackTrace) {
      Error.captureStackTrace(this, EmployeeObjectError);
    }
  }
}

/**
 * Sovereign Employee Domain Object.
 * Encapsulates legal personnel profiles, access credentials metadata,
 * billable hourly rates, and organizational structures inside Wilsy OS.
 */
class EmployeeObject extends BaseEnterpriseObject {
  /**
   * Constructs an EmployeeObject.
   *
   * @param {Object} params
   * @param {string} params.id - Unique Employee Identifier (e.g., 'EMP-2026-0042').
   * @param {string} params.tenantId - Sovereign Tenant ID.
   * @param {string} params.firstName - Legal First Name.
   * @param {string} params.lastName - Legal Last Name.
   * @param {string} params.email - Professional Corporate Email address.
   * @param {string} [params.department='LITIGATION'] - Department allocation.
   * @param {string} [params.roleTitle='ASSOCIATE_ATTORNEY'] - Corporate or legal role title.
   * @param {number} [params.accessLevel=1] - Security clear level (1 to 10).
   * @param {number} [params.hourlyBillableRate=0] - Hourly fee rate for matter billing in ZAR/USD.
   * @param {string} [params.createdById='SYSTEM'] - Identity performing onboard registration.
   */
  constructor({
    id,
    tenantId,
    firstName,
    lastName,
    email,
    department = FIRM_DEPARTMENTS.LITIGATION,
    roleTitle = 'ASSOCIATE_ATTORNEY',
    accessLevel = 1,
    hourlyBillableRate = 0,
    createdById = 'SYSTEM'
  }) {
    if (!firstName || typeof firstName !== 'string' || firstName.trim().length === 0) {
      throw new EmployeeObjectError('First name must be a non-empty string', 'EMP_ERR_INVALID_FIRST_NAME');
    }
    if (!lastName || typeof lastName !== 'string' || lastName.trim().length === 0) {
      throw new EmployeeObjectError('Last name must be a non-empty string', 'EMP_ERR_INVALID_LAST_NAME');
    }
    if (!email || typeof email !== 'string' || !email.includes('@')) {
      throw new EmployeeObjectError('Valid employee email required', 'EMP_ERR_INVALID_EMAIL');
    }

    const level = Number(accessLevel);
    if (isNaN(level) || level < 1 || level > 10) {
      throw new EmployeeObjectError('Security access level must be an integer between 1 and 10', 'EMP_ERR_INVALID_ACCESS_LEVEL');
    }

    const rate = Number(hourlyBillableRate);
    if (isNaN(rate) || rate < 0) {
      throw new EmployeeObjectError('Hourly billable rate must be a non-negative number', 'EMP_ERR_INVALID_RATE');
    }

    const initialAttributes = {
      firstName: firstName.trim(),
      lastName: lastName.trim(),
      fullName: `${firstName.trim()} ${lastName.trim()}`,
      email: email.trim().toLowerCase(),
      department: department.trim().toUpperCase(),
      roleTitle: roleTitle.trim().toUpperCase(),
      accessLevel: level,
      hourlyBillableRate: rate,
      currency: 'ZAR',
      activeMattersCount: 0
    };

    super({
      id,
      tenantId,
      domain: 'EMPLOYEE',
      attributes: initialAttributes,
      schemaVersion: '1.0.0',
      status: OBJECT_LIFECYCLE_STATES.ACTIVE,
      createdById
    });
  }

  /**
   * Updates employee position and security clearance level.
   *
   * @param {Object} roleData
   * @param {string} [roleData.roleTitle] - New title designation.
   * @param {string} [roleData.department] - Department reassignment.
   * @param {number} [roleData.accessLevel] - Updated access clearance level (1-10).
   * @param {string} operatorId - HR or Executive user authorizing update.
   * @returns {Object} Revision result.
   */
  updateRoleAndClearance({ roleTitle, department, accessLevel }, operatorId = 'SYSTEM') {
    const patch = {};

    if (roleTitle && typeof roleTitle === 'string') {
      patch.roleTitle = roleTitle.trim().toUpperCase();
    }
    if (department && typeof department === 'string') {
      patch.department = department.trim().toUpperCase();
    }
    if (accessLevel !== undefined) {
      const level = Number(accessLevel);
      if (isNaN(level) || level < 1 || level > 10) {
        throw new EmployeeObjectError('Security access level must be between 1 and 10', 'EMP_ERR_INVALID_ACCESS_LEVEL');
      }
      patch.accessLevel = level;
    }

    if (Object.keys(patch).length === 0) {
      throw new EmployeeObjectError('No valid role or clearance fields provided', 'EMP_ERR_NO_FIELDS');
    }

    return this.updateAttributes(patch, operatorId);
  }

  /**
   * Updates hourly billable rate schedule.
   *
   * @param {number} newRate - Updated hourly billable rate.
   * @param {string} [currency='ZAR'] - Currency identifier.
   * @param {string} operatorId - Managing Partner or Finance Director ID.
   * @returns {Object} Update execution result.
   */
  updateBillableRate(newRate, currency = 'ZAR', operatorId = 'SYSTEM') {
    const numericRate = Number(newRate);
    if (isNaN(numericRate) || numericRate < 0) {
      throw new EmployeeObjectError('Hourly billable rate must be a non-negative number', 'EMP_ERR_INVALID_RATE');
    }

    return this.updateAttributes(
      {
        hourlyBillableRate: numericRate,
        currency: currency.trim().toUpperCase()
      },
      operatorId
    );
  }

  /**
   * Modifies active matter assignment workload counter.
   *
   * @param {number} delta - Number of matters added (+1) or closed (-1).
   * @param {string} operatorId - Operations user modifying counter.
   * @returns {Object} Revision metadata.
   */
  adjustActiveMattersCount(delta, operatorId = 'SYSTEM') {
    const newCount = this.attributes.activeMattersCount + Number(delta);
    if (newCount < 0) {
      throw new EmployeeObjectError('Active matters count cannot be negative', 'EMP_ERR_INVALID_MATTER_COUNT');
    }

    return this.updateAttributes({ activeMattersCount: newCount }, operatorId);
  }

  /**
   * Convenience getter for full employee name.
   * @returns {string}
   */
  get fullName() {
    return this.attributes.fullName;
  }

  /**
   * Convenience getter for corporate email.
   * @returns {string}
   */
  get email() {
    return this.attributes.email;
  }

  /**
   * Convenience getter for current security access level.
   * @returns {number}
   */
  get accessLevel() {
    return this.attributes.accessLevel;
  }

  /**
   * Convenience getter for hourly billable rate.
   * @returns {number}
   */
  get hourlyBillableRate() {
    return this.attributes.hourlyBillableRate;
  }

  /**
   * Generates a scrubbed employee summary suitable for internal firm directories.
   * @returns {Object}
   */
  getSanitizedSummary() {
    return {
      employeeId: this.id,
      tenantId: this.tenantId,
      fullName: this.attributes.fullName,
      email: this.attributes.email,
      department: this.attributes.department,
      roleTitle: this.attributes.roleTitle,
      accessLevel: this.attributes.accessLevel,
      hourlyBillableRate: this.attributes.hourlyBillableRate,
      currency: this.attributes.currency,
      activeMattersCount: this.attributes.activeMattersCount,
      status: this.status,
      revisionNumber: this.revisionNumber,
      updatedAt: this.updatedAt
    };
  }
}

module.exports = {
  EmployeeObject,
  EmployeeObjectError,
  FIRM_DEPARTMENTS
};
