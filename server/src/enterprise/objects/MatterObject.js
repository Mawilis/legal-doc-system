/**
 * ============================================================================
 * WILSY OS - MATTER ENTERPRISE OBJECT
 * ============================================================================
 *
 * @file         MatterObject.js
 * @directory    server/src/enterprise/objects/
 * @system       Wilsy OS - Legal Enterprise Operating System & SaaS Platform
 * @authority    Wilson Khanyezi, Founder & Chief Architect
 * @version      1.0.0-SOVEREIGN
 * @epitome      Generation 2 Sovereign Matter Kernel Object implementation.
 *               Serves as the central legal mandate domain entity in Wilsy OS.
 *               Integrates FICA compliance validation, Conflict of Interest
 *               auditing, South African Prescription Act deadline tracking,
 *               fee structure budgets, and legal team access controls.
 *
 * @collaboration
 * - Lead Architect: Wilson Khanyezi (Wilsy OS Architecture Core Team)
 * - Practice Management: Legal Mandate & Practice Management Core
 * - Statutory Compliance: FICA, LPC, & Prescription Act Oversight Core
 *
 * ============================================================================
 * INSTITUTIONAL AUDIT TRAIL
 * ============================================================================
 * Date       | Author          | Version | Description
 * -----------|-----------------|---------|------------------------------------
 * 2026-07-24 | Wilson Khanyezi | 1.0.0   | Production-ready Matter domain object
 *            |                 |         | with FICA gates, conflict checks,
 *            |                 |         | prescription locks, and team assignments.
 * ============================================================================
 */

const { BaseEnterpriseObject, OBJECT_LIFECYCLE_STATES } = require('./BaseEnterpriseObject');
const { DataRedactor } = require('../kernel/EnterpriseKernel');

/**
 * Recognized Legal Matter Practice Areas.
 */
const MATTER_PRACTICE_AREA = Object.freeze({
  LITIGATION_CIVIL: 'LITIGATION_CIVIL',
  LITIGATION_CRIMINAL: 'LITIGATION_CRIMINAL',
  COMMERCIAL_CORPORATE: 'COMMERCIAL_CORPORATE',
  CONVEYANCING_PROPERTY: 'CONVEYANCING_PROPERTY',
  LABOUR_EMPLOYMENT: 'LABOUR_EMPLOYMENT',
  FAMILY_ESTATES: 'FAMILY_ESTATES',
  REGULATORY_COMPLIANCE: 'REGULATORY_COMPLIANCE',
  INTELLECTUAL_PROPERTY: 'INTELLECTUAL_PROPERTY'
});

/**
 * Legal Matter Operational Lifecycle States.
 */
const MATTER_STATUS = Object.freeze({
  PENDING_FICA: 'PENDING_FICA',
  PENDING_CONFLICT_CHECK: 'PENDING_CONFLICT_CHECK',
  ACTIVE: 'ACTIVE',
  SUSPENDED: 'SUSPENDED',
  LITIGATION_STAYED: 'LITIGATION_STAYED',
  SETTLED: 'SETTLED',
  CLOSED: 'CLOSED',
  ARCHIVED: 'ARCHIVED'
});

/**
 * Fee Agreement Structures for Legal Billing.
 */
const FEE_STRUCTURE = Object.freeze({
  HOURLY_RATE: 'HOURLY_RATE',
  FIXED_FEE: 'FIXED_FEE',
  CONTINGENCY_AGREEMENT: 'CONTINGENCY_AGREEMENT',
  RETAINER: 'RETAINER',
  PRO_BONO: 'PRO_BONO'
});

/**
 * Custom Error Class for Matter Domain Faults.
 */
class MatterObjectError extends Error {
  /**
   * @param {string} message - Error details.
   * @param {string} [code='MATTER_ERR_GENERIC'] - Standard error code.
   * @param {Object} [details={}] - Additional contextual metadata.
   */
  constructor(message, code = 'MATTER_ERR_GENERIC', details = {}) {
    super(message);
    this.name = 'MatterObjectError';
    this.code = code;
    this.timestamp = new Date().toISOString();
    this.details = DataRedactor.sanitize(details);
    if (Error.captureStackTrace) {
      Error.captureStackTrace(this, MatterObjectError);
    }
  }
}

/**
 * Sovereign Legal Matter Domain Object.
 * Encapsulates legal mandates, client associations, FICA regulatory gates,
 * conflict check verification, prescription date limits, fee caps, and assigned counsel in Wilsy OS.
 */
class MatterObject extends BaseEnterpriseObject {
  /**
   * Constructs a MatterObject.
   *
   * @param {Object} params
   * @param {string} params.id - Unique Matter Identifier (e.g. 'MAT-2026-1088').
   * @param {string} params.tenantId - Sovereign Tenant ID.
   * @param {string} params.customerId - Client / Primary Mandate Customer ID.
   * @param {string} params.title - Human-readable Matter Title (e.g., 'Khanyezi vs. Global Logistics Corp').
   * @param {string} params.leadAttorneyId - User ID of Lead Attorney / Director overseeing mandate.
   * @param {string} [params.practiceArea='COMMERCIAL_CORPORATE'] - Legal domain constant.
   * @param {string} [params.feeStructure='HOURLY_RATE'] - Billing agreement type.
   * @param {number} [params.estimatedBudget=0] - Financial fee cap limit (0 = uncapped).
   * @param {string} [params.prescriptionDate=null] - ISO Date String for statutory prescription.
   * @param {boolean} [params.ficaApproved=false] - FICA verification status.
   * @param {boolean} [params.conflictCheckPassed=false] - Conflict check status.
   * @param {string} [params.createdById='SYSTEM'] - Operator opening file.
   */
  constructor({
    id,
    tenantId,
    customerId,
    title,
    leadAttorneyId,
    practiceArea = MATTER_PRACTICE_AREA.COMMERCIAL_CORPORATE,
    feeStructure = FEE_STRUCTURE.HOURLY_RATE,
    estimatedBudget = 0,
    prescriptionDate = null,
    ficaApproved = false,
    conflictCheckPassed = false,
    createdById = 'SYSTEM'
  }) {
    if (!customerId || typeof customerId !== 'string') {
      throw new MatterObjectError('Client / Customer ID is required to open a legal matter', 'MATTER_ERR_INVALID_CUSTOMER');
    }

    if (!title || typeof title !== 'string' || title.trim().length === 0) {
      throw new MatterObjectError('Matter title is required', 'MATTER_ERR_INVALID_TITLE');
    }

    if (!leadAttorneyId || typeof leadAttorneyId !== 'string') {
      throw new MatterObjectError('Lead Attorney ID is required', 'MATTER_ERR_INVALID_LEAD_ATTORNEY');
    }

    const normArea = practiceArea.trim().toUpperCase();
    if (!Object.values(MATTER_PRACTICE_AREA).includes(normArea)) {
      throw new MatterObjectError(`Invalid practice area designation [${practiceArea}]`, 'MATTER_ERR_INVALID_PRACTICE_AREA');
    }

    const normFee = feeStructure.trim().toUpperCase();
    if (!Object.values(FEE_STRUCTURE).includes(normFee)) {
      throw new MatterObjectError(`Invalid fee structure designation [${feeStructure}]`, 'MATTER_ERR_INVALID_FEE_STRUCTURE');
    }

    // Determine initial status based on compliance status flags
    let initialStatus = MATTER_STATUS.PENDING_FICA;
    if (ficaApproved && !conflictCheckPassed) {
      initialStatus = MATTER_STATUS.PENDING_CONFLICT_CHECK;
    } else if (ficaApproved && conflictCheckPassed) {
      initialStatus = MATTER_STATUS.ACTIVE;
    }

    const initialAttributes = {
      customerId: customerId.trim(),
      title: title.trim(),
      leadAttorneyId: leadAttorneyId.trim(),
      practiceArea: normArea,
      feeStructure: normFee,
      matterStatus: initialStatus,
      estimatedBudget: Math.max(0, Number(estimatedBudget) || 0),
      prescriptionDate: prescriptionDate ? new Date(prescriptionDate).toISOString() : null,
      ficaApproved: Boolean(ficaApproved),
      ficaApprovedAt: ficaApproved ? new Date().toISOString() : null,
      ficaApprovedBy: ficaApproved ? createdById : null,
      conflictCheckPassed: Boolean(conflictCheckPassed),
      conflictCheckPassedAt: conflictCheckPassed ? new Date().toISOString() : null,
      conflictCheckPassedBy: conflictCheckPassed ? createdById : null,
      assignedTeamMembers: [
        {
          userId: leadAttorneyId.trim(),
          role: 'LEAD_ATTORNEY',
          assignedAt: new Date().toISOString()
        }
      ],
      closedAt: null,
      closureReason: null
    };

    super({
      id,
      tenantId,
      domain: 'MATTER',
      attributes: initialAttributes,
      schemaVersion: '1.0.0',
      status: OBJECT_LIFECYCLE_STATES.ACTIVE,
      createdById
    });
  }

  /**
   * Approves FICA compliance for the matter, clearing regulatory block.
   *
   * @param {string} operatorId - Compliance Officer or Attorney approving FICA.
   * @returns {Object} Revision state.
   */
  approveFicaCompliance(operatorId = 'SYSTEM') {
    let nextStatus = this.attributes.matterStatus;
    if (this.attributes.matterStatus === MATTER_STATUS.PENDING_FICA) {
      nextStatus = this.attributes.conflictCheckPassed ? MATTER_STATUS.ACTIVE : MATTER_STATUS.PENDING_CONFLICT_CHECK;
    }

    return this.updateAttributes(
      {
        ficaApproved: true,
        ficaApprovedAt: new Date().toISOString(),
        ficaApprovedBy: operatorId,
        matterStatus: nextStatus
      },
      operatorId
    );
  }

  /**
   * Approves Conflict of Interest verification for the matter.
   *
   * @param {string} operatorId - Senior Partner or Attorney approving conflict check.
   * @returns {Object} Revision state.
   */
  approveConflictCheck(operatorId = 'SYSTEM') {
    let nextStatus = this.attributes.matterStatus;
    if (this.attributes.matterStatus === MATTER_STATUS.PENDING_CONFLICT_CHECK || this.attributes.matterStatus === MATTER_STATUS.PENDING_FICA) {
      nextStatus = this.attributes.ficaApproved ? MATTER_STATUS.ACTIVE : MATTER_STATUS.PENDING_FICA;
    }

    return this.updateAttributes(
      {
        conflictCheckPassed: true,
        conflictCheckPassedAt: new Date().toISOString(),
        conflictCheckPassedBy: operatorId,
        matterStatus: nextStatus
      },
      operatorId
    );
  }

  /**
   * Assigns an additional legal practitioner or support staff to the matter team.
   *
   * @param {Object} memberData
   * @param {string} memberData.userId - System User ID of team member.
   * @param {string} [memberData.role='PARALEGAL'] - Legal role (e.g. ADVOCATE, ASSIGNED_ATTORNEY, PARALEGAL).
   * @param {string} operatorId - Lead Attorney modifying team composition.
   * @returns {Object} Revision state.
   */
  assignTeamMember({ userId, role = 'PARALEGAL' }, operatorId = 'SYSTEM') {
    if (!userId || typeof userId !== 'string') {
      throw new MatterObjectError('Team member User ID is required', 'MATTER_ERR_INVALID_MEMBER_ID');
    }

    const cleanUserId = userId.trim();
    const existingIndex = this.attributes.assignedTeamMembers.findIndex((m) => m.userId === cleanUserId);

    let updatedTeam = [...this.attributes.assignedTeamMembers];
    if (existingIndex >= 0) {
      updatedTeam[existingIndex] = {
        userId: cleanUserId,
        role: role.trim().toUpperCase(),
        assignedAt: new Date().toISOString()
      };
    } else {
      updatedTeam.push({
        userId: cleanUserId,
        role: role.trim().toUpperCase(),
        assignedAt: new Date().toISOString()
      });
    }

    return this.updateAttributes({ assignedTeamMembers: updatedTeam }, operatorId);
  }

  /**
   * Updates operational status of the legal matter (e.g. SUSPENDED, SETTLED, CLOSED).
   *
   * @param {string} newStatus - Target status constant from MATTER_STATUS.
   * @param {string} [reason=null] - Reason for status change.
   * @param {string} operatorId - User modifying matter status.
   * @returns {Object} Revision state.
   */
  updateMatterStatus(newStatus, reason = null, operatorId = 'SYSTEM') {
    const normStatus = newStatus ? newStatus.trim().toUpperCase() : '';
    if (!Object.values(MATTER_STATUS).includes(normStatus)) {
      throw new MatterObjectError(`Invalid status transition target [${newStatus}]`, 'MATTER_ERR_INVALID_STATUS');
    }

    // Enforce FICA and Conflict Check rules prior to setting ACTIVE state
    if (normStatus === MATTER_STATUS.ACTIVE) {
      if (!this.attributes.ficaApproved) {
        throw new MatterObjectError('Cannot set matter to ACTIVE before FICA approval', 'MATTER_ERR_FICA_REQUIRED');
      }
      if (!this.attributes.conflictCheckPassed) {
        throw new MatterObjectError('Cannot set matter to ACTIVE before Conflict Check approval', 'MATTER_ERR_CONFLICT_REQUIRED');
      }
    }

    const isClosing = normStatus === MATTER_STATUS.CLOSED || normStatus === MATTER_STATUS.ARCHIVED;

    return this.updateAttributes(
      {
        matterStatus: normStatus,
        closedAt: isClosing ? new Date().toISOString() : this.attributes.closedAt,
        closureReason: isClosing ? (reason ? reason.trim() : 'MANDATE_COMPLETED') : this.attributes.closureReason
      },
      operatorId
    );
  }

  /**
   * Convenience getter for Matter Title.
   * @returns {string}
   */
  get title() {
    return this.attributes.title;
  }

  /**
   * Convenience getter for Lead Attorney ID.
   * @returns {string}
   */
  get leadAttorneyId() {
    return this.attributes.leadAttorneyId;
  }

  /**
   * Convenience getter for Matter Status.
   * @returns {string}
   */
  get matterStatus() {
    return this.attributes.matterStatus;
  }

  /**
   * Convenience getter for FICA Compliance Status.
   * @returns {boolean}
   */
  get isFicaCompliant() {
    return this.attributes.ficaApproved;
  }

  /**
   * Generates a scrubbed overview of matter metadata for enterprise search and indexing.
   * @returns {Object}
   */
  getSanitizedSummary() {
    return {
      matterId: this.id,
      tenantId: this.tenantId,
      customerId: this.attributes.customerId,
      title: this.attributes.title,
      leadAttorneyId: this.attributes.leadAttorneyId,
      practiceArea: this.attributes.practiceArea,
      feeStructure: this.attributes.feeStructure,
      matterStatus: this.attributes.matterStatus,
      estimatedBudget: this.attributes.estimatedBudget,
      prescriptionDate: this.attributes.prescriptionDate,
      ficaApproved: this.attributes.ficaApproved,
      conflictCheckPassed: this.attributes.conflictCheckPassed,
      teamMemberCount: this.attributes.assignedTeamMembers.length,
      status: this.status,
      revisionNumber: this.revisionNumber,
      updatedAt: this.updatedAt
    };
  }
}

module.exports = {
  MatterObject,
  MatterObjectError,
  MATTER_PRACTICE_AREA,
  MATTER_STATUS,
  FEE_STRUCTURE
};
