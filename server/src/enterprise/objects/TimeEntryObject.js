/**
 * ============================================================================
 * WILSY OS - TIME ENTRY ENTERPRISE OBJECT
 * ============================================================================
 *
 * @file         TimeEntryObject.js
 * @directory    server/src/enterprise/objects/
 * @system       Wilsy OS - Legal Enterprise Operating System & SaaS Platform
 * @authority    Wilson Khanyezi, Founder & Chief Architect
 * @version      1.0.0-SOVEREIGN
 * @epitome      Generation 2 Sovereign Time Entry Kernel Object implementation.
 *               Serves as the practitioner time-tracking and billable labor ledger.
 *               Encapsulates unit calculations, partner approval gates, statutory
 *               fee scale linkages, and invoice lifecycle immutability locks.
 *
 * @collaboration
 * - Lead Architect: Wilson Khanyezi (Wilsy OS Architecture Core Team)
 * - Practice Management: Fee Earner Productivity & Time Recording Core
 * - Revenue Systems: Unbilled WIP & Invoice Generation Subsystem
 *
 * ============================================================================
 * INSTITUTIONAL AUDIT TRAIL
 * ============================================================================
 * Date       | Author          | Version | Description
 * -----------|-----------------|---------|------------------------------------
 * 2026-07-24 | Wilson Khanyezi | 1.0.0   | Production-ready Time Entry domain object
 *            |                 |         | with approval workflows, dynamic rate
 *            |                 |         | engines, and invoice status locks.
 * ============================================================================
 */

const { BaseEnterpriseObject, OBJECT_LIFECYCLE_STATES } = require('./BaseEnterpriseObject');
const { DataRedactor } = require('../kernel/EnterpriseKernel');

/**
 * Recognized Legal Activity Classifications.
 */
const TIME_ACTIVITY_TYPE = Object.freeze({
  COURT_APPEARANCE: 'COURT_APPEARANCE',
  DRAFTING_PLEADINGS: 'DRAFTING_PLEADINGS',
  CONSULTATION: 'CONSULTATION',
  RESEARCH: 'RESEARCH',
  ATTENDANCE_TELEPHONIC: 'ATTENDANCE_TELEPHONIC',
  DOCUMENT_REVIEW: 'DOCUMENT_REVIEW',
  TRAVEL: 'TRAVEL',
  ADMINISTRATIVE: 'ADMINISTRATIVE'
});

/**
 * Operational Billing Status for Time Entries.
 */
const TIME_ENTRY_STATUS = Object.freeze({
  UNBILLED: 'UNBILLED',
  APPROVED: 'APPROVED',
  INVOICED: 'INVOICED',
  WRITTEN_OFF: 'WRITTEN_OFF',
  NON_BILLABLE: 'NON_BILLABLE'
});

/**
 * Custom Error Class for Time Entry Domain Faults.
 */
class TimeEntryObjectError extends Error {
  /**
   * @param {string} message - Error details.
   * @param {string} [code='TIME_ERR_GENERIC'] - Standard error code.
   * @param {Object} [details={}] - Additional contextual metadata.
   */
  constructor(message, code = 'TIME_ERR_GENERIC', details = {}) {
    super(message);
    this.name = 'TimeEntryObjectError';
    this.code = code;
    this.timestamp = new Date().toISOString();
    this.details = DataRedactor.sanitize(details);
    if (Error.captureStackTrace) {
      Error.captureStackTrace(this, TimeEntryObjectError);
    }
  }
}

/**
 * Sovereign Time Entry Domain Object.
 * Encapsulates practitioner billable hours, fee tariffs, matter linkage, partner
 * review gates, and invoice attachment lifecycles in Wilsy OS.
 */
class TimeEntryObject extends BaseEnterpriseObject {
  /**
   * Constructs a TimeEntryObject.
   *
   * @param {Object} params
   * @param {string} params.id - Unique Time Entry Identifier (e.g. 'TME-2026-7012').
   * @param {string} params.tenantId - Sovereign Tenant ID.
   * @param {string} params.matterId - Associated Legal Matter ID.
   * @param {string} params.practitionerId - Fee Earner User ID (Partner, Associate, Candidate Attorney).
   * @param {string} [params.activityType='CONSULTATION'] - Activity category constant.
   * @param {string} params.narrative - Detail of legal service rendered for client statement.
   * @param {number} params.durationMinutes - Total time spent in minutes.
   * @param {number} params.hourlyRate - Applicable hourly rate in ZAR.
   * @param {string} [params.tariffId=null] - Optional FeeTariffObject reference.
   * @param {boolean} [params.isBillable=true] - Whether duration is chargeable to client.
   * @param {string} [params.createdById='SYSTEM'] - Operator recording time entry.
   */
  constructor({
    id,
    tenantId,
    matterId,
    practitionerId,
    activityType = TIME_ACTIVITY_TYPE.CONSULTATION,
    narrative,
    durationMinutes,
    hourlyRate,
    tariffId = null,
    isBillable = true,
    createdById = 'SYSTEM'
  }) {
    if (!matterId || typeof matterId !== 'string') {
      throw new TimeEntryObjectError('Associated matter ID is required', 'TIME_ERR_INVALID_MATTER');
    }

    if (!practitionerId || typeof practitionerId !== 'string') {
      throw new TimeEntryObjectError('Practitioner fee earner ID is required', 'TIME_ERR_INVALID_PRACTITIONER');
    }

    if (!narrative || typeof narrative !== 'string' || narrative.trim().length === 0) {
      throw new TimeEntryObjectError('Narrative explanation of legal service is required', 'TIME_ERR_INVALID_NARRATIVE');
    }

    const minutes = Number(durationMinutes);
    if (isNaN(minutes) || minutes <= 0) {
      throw new TimeEntryObjectError('Duration in minutes must be a positive integer', 'TIME_ERR_INVALID_DURATION');
    }

    const rate = Number(hourlyRate);
    if (isNaN(rate) || rate < 0) {
      throw new TimeEntryObjectError('Hourly rate must be a non-negative number', 'TIME_ERR_INVALID_RATE');
    }

    const normType = activityType.trim().toUpperCase();
    if (!Object.values(TIME_ACTIVITY_TYPE).includes(normType)) {
      throw new TimeEntryObjectError(`Invalid activity type [${activityType}]`, 'TIME_ERR_INVALID_ACTIVITY');
    }

    const initialBillable = Boolean(isBillable);
    const calculatedFee = initialBillable ? Number(((minutes / 60) * rate).toFixed(2)) : 0.0;
    const initialStatus = initialBillable ? TIME_ENTRY_STATUS.UNBILLED : TIME_ENTRY_STATUS.NON_BILLABLE;

    const initialAttributes = {
      matterId: matterId.trim(),
      practitionerId: practitionerId.trim(),
      activityType: normType,
      narrative: narrative.trim(),
      durationMinutes: Math.round(minutes),
      hourlyRate: Number(rate.toFixed(2)),
      tariffId: tariffId ? tariffId.trim() : null,
      isBillable: initialBillable,
      calculatedFee: calculatedFee,
      billingStatus: initialStatus,
      approvedByPartnerId: null,
      approvedAt: null,
      invoiceId: null,
      invoicedAt: null,
      writeOffReason: null
    };

    super({
      id,
      tenantId,
      domain: 'TIME_ENTRY',
      attributes: initialAttributes,
      schemaVersion: '1.0.0',
      status: OBJECT_LIFECYCLE_STATES.ACTIVE,
      createdById
    });
  }

  /**
   * Approves time entry by Senior Partner prior to invoicing.
   *
   * @param {string} partnerId - User ID of approving Partner.
   * @returns {Object} Revision state.
   */
  approveTimeEntry(partnerId) {
    if (!partnerId || typeof partnerId !== 'string') {
      throw new TimeEntryObjectError('Partner ID is required for approval', 'TIME_ERR_INVALID_APPROVER');
    }

    if (this.attributes.billingStatus !== TIME_ENTRY_STATUS.UNBILLED) {
      throw new TimeEntryObjectError(
        `Cannot approve time entry in status [${this.attributes.billingStatus}]`,
        'TIME_ERR_INVALID_APPROVAL_STATE'
      );
    }

    return this.updateAttributes(
      {
        billingStatus: TIME_ENTRY_STATUS.APPROVED,
        approvedByPartnerId: partnerId.trim(),
        approvedAt: new Date().toISOString()
      },
      partnerId
    );
  }

  /**
   * Links time entry to an issued tax invoice, freezing further edits.
   *
   * @param {string} invoiceId - Target Invoice ID.
   * @param {string} operatorId - Billing clerk or partner linking time.
   * @returns {Object} Revision state.
   */
  linkToInvoice(invoiceId, operatorId = 'SYSTEM') {
    if (
      this.attributes.billingStatus !== TIME_ENTRY_STATUS.UNBILLED &&
      this.attributes.billingStatus !== TIME_ENTRY_STATUS.APPROVED
    ) {
      throw new TimeEntryObjectError(
        `Cannot attach time entry in status [${this.attributes.billingStatus}] to invoice`,
        'TIME_ERR_LOCKED_STATUS'
      );
    }

    if (!invoiceId || typeof invoiceId !== 'string') {
      throw new TimeEntryObjectError('Valid target invoice ID is required', 'TIME_ERR_INVALID_INVOICE');
    }

    return this.updateAttributes(
      {
        billingStatus: TIME_ENTRY_STATUS.INVOICED,
        invoiceId: invoiceId.trim(),
        invoicedAt: new Date().toISOString()
      },
      operatorId
    );
  }

  /**
   * Writes off billable time in the event of fee reductions or billing disputes.
   *
   * @param {string} reason - Justification narrative for write-off.
   * @param {string} partnerId - Authorizing Senior Partner identity.
   * @returns {Object} Revision state.
   */
  writeOff(reason, partnerId = 'SYSTEM') {
    if (!reason || typeof reason !== 'string' || reason.trim().length === 0) {
      throw new TimeEntryObjectError('Write-off justification reason is required', 'TIME_ERR_REASON_REQUIRED');
    }

    if (this.attributes.billingStatus === TIME_ENTRY_STATUS.INVOICED) {
      throw new TimeEntryObjectError('Cannot write off a time entry that has already been invoiced', 'TIME_ERR_INVOICED_WRITE_OFF_PROHIBITED');
    }

    return this.updateAttributes(
      {
        billingStatus: TIME_ENTRY_STATUS.WRITTEN_OFF,
        writeOffReason: reason.trim()
      },
      partnerId
    );
  }

  /**
   * Convenience getter for Duration in Minutes.
   * @returns {number}
   */
  get durationMinutes() {
    return this.attributes.durationMinutes;
  }

  /**
   * Convenience getter for Calculated Fee.
   * @returns {number}
   */
  get calculatedFee() {
    return this.attributes.calculatedFee;
  }

  /**
   * Convenience getter for Billing Status.
   * @returns {string}
   */
  get billingStatus() {
    return this.attributes.billingStatus;
  }

  /**
   * Generates a scrubbed overview of time entry metadata for billing reports.
   * @returns {Object}
   */
  getSanitizedSummary() {
    return {
      timeEntryId: this.id,
      tenantId: this.tenantId,
      matterId: this.attributes.matterId,
      practitionerId: this.attributes.practitionerId,
      activityType: this.attributes.activityType,
      narrative: this.attributes.narrative,
      durationMinutes: this.attributes.durationMinutes,
      hourlyRate: this.attributes.hourlyRate,
      calculatedFee: this.attributes.calculatedFee,
      isBillable: this.attributes.isBillable,
      billingStatus: this.attributes.billingStatus,
      approvedByPartnerId: this.attributes.approvedByPartnerId,
      invoiceId: this.attributes.invoiceId,
      status: this.status,
      revisionNumber: this.revisionNumber,
      updatedAt: this.updatedAt
    };
  }
}

module.exports = {
  TimeEntryObject,
  TimeEntryObjectError,
  TIME_ACTIVITY_TYPE,
  TIME_ENTRY_STATUS
};
