/**
 * ============================================================================
 * WILSY OS - ENTERPRISE OBJECTS CENTRAL BARREL INDEX
 * ============================================================================
 *
 * @file         index.js
 * @directory    server/src/enterprise/objects/
 * @system       Wilsy OS - Legal Enterprise Operating System & SaaS Platform
 * @authority    Wilson Khanyezi, Founder & Chief Architect
 * @version      1.0.0-SOVEREIGN
 * @epitome      Generation 2 Sovereign Enterprise Objects Export Registry.
 *               Provides unified, consolidated imports for all domain entities,
 *               custom error models, enums, and state machines across Wilsy OS.
 *
 * @collaboration
 * - Lead Architect: Wilson Khanyezi (Wilsy OS Architecture Core Team)
 * - Domain Architecture: Enterprise Object Subsystem
 *
 * ============================================================================
 * INSTITUTIONAL AUDIT TRAIL
 * ============================================================================
 * Date       | Author          | Version | Description
 * -----------|-----------------|---------|------------------------------------
 * 2026-07-24 | Wilson Khanyezi | 1.0.0   | Master export registry unifying all
 *            |                 |         | enterprise domain entities.
 * ============================================================================
 */

const { BaseEnterpriseObject, BaseEnterpriseObjectError, OBJECT_LIFECYCLE_STATES } = require('./BaseEnterpriseObject');
const { CustomerObject, CustomerObjectError, CUSTOMER_TYPES, KYC_STATUS } = require('./CustomerObject');
const { MatterObject, MatterObjectError, MATTER_STATUS, PRACTICE_AREAS } = require('./MatterObject');
const { DocumentObject, DocumentObjectError, DOCUMENT_TYPES, DOCUMENT_STATUS } = require('./DocumentObject');
const { InvoiceObject, InvoiceObjectError, INVOICE_STATUS, TAX_RATES } = require('./InvoiceObject');
const { TrustAccountObject, TrustAccountObjectError, TRUST_ACCOUNT_STATUS, LPC_SECTION_86_CLASS } = require('./TrustAccountObject');
const { WorkflowTaskObject, WorkflowTaskObjectError, TASK_STATUS, TASK_PRIORITY } = require('./WorkflowTaskObject');
const { ComplianceRecordObject, ComplianceRecordObjectError, COMPLIANCE_TYPE, COMPLIANCE_STATUS } = require('./ComplianceRecordObject');
const { DisbursementObject, DisbursementObjectError, DISBURSEMENT_TYPE, DISBURSEMENT_STATUS } = require('./DisbursementObject');
const { FeeTariffObject, FeeTariffObjectError, TARIFF_JURISDICTION, TARIFF_UNIT } = require('./FeeTariffObject');
const { PaymentReceiptObject, PaymentReceiptObjectError, PAYMENT_ACCOUNT_TYPE, PAYMENT_CHANNEL, PAYMENT_STATUS } = require('./PaymentReceiptObject');
const { TimeEntryObject, TimeEntryObjectError, TIME_ACTIVITY_TYPE, TIME_ENTRY_STATUS } = require('./TimeEntryObject');
const { AuditLogObject, AuditLogObjectError, AUDIT_SEVERITY, AUDIT_ACTION } = require('./AuditLogObject');

module.exports = {
  // Base Enterprise Framework
  BaseEnterpriseObject,
  BaseEnterpriseObjectError,
  OBJECT_LIFECYCLE_STATES,

  // Domain Objects & Entities
  CustomerObject,
  CustomerObjectError,
  CUSTOMER_TYPES,
  KYC_STATUS,

  MatterObject,
  MatterObjectError,
  MATTER_STATUS,
  PRACTICE_AREAS,

  DocumentObject,
  DocumentObjectError,
  DOCUMENT_TYPES,
  DOCUMENT_STATUS,

  InvoiceObject,
  InvoiceObjectError,
  INVOICE_STATUS,
  TAX_RATES,

  TrustAccountObject,
  TrustAccountObjectError,
  TRUST_ACCOUNT_STATUS,
  LPC_SECTION_86_CLASS,

  WorkflowTaskObject,
  WorkflowTaskObjectError,
  TASK_STATUS,
  TASK_PRIORITY,

  ComplianceRecordObject,
  ComplianceRecordObjectError,
  COMPLIANCE_TYPE,
  COMPLIANCE_STATUS,

  DisbursementObject,
  DisbursementObjectError,
  DISBURSEMENT_TYPE,
  DISBURSEMENT_STATUS,

  FeeTariffObject,
  FeeTariffObjectError,
  TARIFF_JURISDICTION,
  TARIFF_UNIT,

  PaymentReceiptObject,
  PaymentReceiptObjectError,
  PAYMENT_ACCOUNT_TYPE,
  PAYMENT_CHANNEL,
  PAYMENT_STATUS,

  TimeEntryObject,
  TimeEntryObjectError,
  TIME_ACTIVITY_TYPE,
  TIME_ENTRY_STATUS,

  AuditLogObject,
  AuditLogObjectError,
  AUDIT_SEVERITY,
  AUDIT_ACTION
};
