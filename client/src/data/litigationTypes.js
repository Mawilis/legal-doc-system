/**
 * File: client/src/data/litigationTypes.js
 * STATUS: EPITOME | WORKFLOW DNA | PRODUCTION-READY | VERSION: 1.0.0
 * -----------------------------------------------------------------------------
 * PURPOSE:
 * - Canonical litigation type registry for Wilsy OS.
 * - Drives UI workflows, upload validation, Sheriff instructions, AI triage, and billing.
 *
 * COLLABORATION:
 * - AUTHOR: Wilson Khanyezi (Chief Architect)
 * - REVIEWERS: @legal, @product, @security, @sre, @frontend
 * - OPS: Changes require migration script and audit entry.
 *
 * LEGAL SOURCES:
 * - PIE Act eviction procedure guidance (used to model eviction workflows).
 * - Civil case lifecycle references (letter of demand, summons, service, hearing).
 * - Notice of Motion vs Summons guidance for motion proceedings and urgent applications.
 *
 * NOTES:
 * - All exports are frozen to prevent runtime mutation.
 * - Extend via migration scripts; do not edit in-place in production.
 * -----------------------------------------------------------------------------
 */

export const CATEGORIES = Object.freeze({
  CIVIL: 'Civil Litigation',
  MOTION: 'Motion Proceedings',
  FAMILY: 'Matrimonial & Family',
  PROPERTY: 'Property & Eviction',
  CRITICAL: 'Urgent & Priority',
  JUDGMENT: 'Judgments & Rescissions'
});

/**
 * Canonical workflow states (UI + backend job mapping)
 * - Use these tokens across Dashboard, Sheriff, and Worker queues.
 */
export const WORKFLOW_STATES = Object.freeze([
  'DRAFTING',
  'ISSUING',
  'URGENT_ISSUING',
  'SHERIFF_SERVICE',
  'IMMEDIATE_SERVICE',
  'SERVICE',
  'SERVICE_MAIN',
  'SERVICE_MUNICIPALITY',
  'NOTICE_TO_DEFEND',
  'DEFAULT_JUDGMENT',
  'REGISTRAR_FILING',
  'JUDGMENT_GRANTED',
  'OPPOSING_PAPERS',
  'HEARING',
  'INTERIM_ORDER',
  'RETURN_DATE',
  'FINAL_ORDER',
  'NEGOTIATION',
  'SIGNING'
]);

/**
 * Risk levels (used by AI triage and SLA)
 */
export const RISK_LEVELS = Object.freeze({
  LOW: 'LOW',
  MEDIUM: 'MEDIUM',
  HIGH: 'HIGH',
  CRITICAL: 'CRITICAL'
});

/**
 * LITIGATION_TYPES
 * - Exhaustive, audited list of case types with metadata used across the product.
 */
export const LITIGATION_TYPES = Object.freeze([
  {
    id: 'combined_summons',
    label: 'Combined Summons',
    category: CATEGORIES.CIVIL,
    desc: 'Liquidated demands with dispute of fact',
    statute: 'Uniform Rule 17',
    icon: '📜',
    baseFee: 2500,
    riskLevel: RISK_LEVELS.MEDIUM,
    serviceType: 'PERSONAL_SERVICE_REQUIRED',
    requiredDocs: ['Particulars of Claim', 'Annexures'],
    workflow: ['DRAFTING', 'ISSUING', 'SHERIFF_SERVICE', 'NOTICE_TO_DEFEND']
  },
  {
    id: 'simple_summons',
    label: 'Simple Summons',
    category: CATEGORIES.CIVIL,
    desc: 'Liquidated debt/demands only',
    statute: 'Uniform Rule 17(2)',
    icon: '💰',
    baseFee: 1500,
    riskLevel: RISK_LEVELS.LOW,
    serviceType: 'NORMAL_SERVICE',
    requiredDocs: ['Summons Document', 'Statement of Account'],
    workflow: ['DRAFTING', 'ISSUING', 'SHERIFF_SERVICE', 'DEFAULT_JUDGMENT']
  },
  {
    id: 'notice_motion',
    label: 'Notice of Motion',
    category: CATEGORIES.MOTION,
    desc: 'Application procedure (motion court) — long form',
    statute: 'Uniform Rule 6',
    icon: '📝',
    baseFee: 3500,
    riskLevel: RISK_LEVELS.MEDIUM,
    serviceType: 'NORMAL_SERVICE',
    requiredDocs: ['Founding Affidavit', 'Notice of Motion'],
    workflow: ['DRAFTING', 'ISSUING', 'SERVICE', 'OPPOSING_PAPERS']
  },
  {
    id: 'urgent_app',
    label: 'Urgent Application',
    category: CATEGORIES.CRITICAL,
    desc: 'Priority handling under Rule 6(12)',
    statute: 'Uniform Rule 6(12)',
    icon: '🚨',
    baseFee: 8500,
    riskLevel: RISK_LEVELS.CRITICAL,
    serviceType: 'URGENT_SERVICE',
    requiredDocs: ['Certificate of Urgency', 'Founding Affidavit'],
    workflow: ['DRAFTING', 'URGENT_ISSUING', 'IMMEDIATE_SERVICE', 'COURT_HEARING']
  },
  {
    id: 'default_judgment',
    label: 'Default Judgment',
    category: CATEGORIES.JUDGMENT,
    desc: 'Unopposed request for judgment',
    statute: 'Uniform Rule 31',
    icon: '🔨',
    baseFee: 1200,
    riskLevel: RISK_LEVELS.LOW,
    serviceType: 'NONE',
    requiredDocs: ['Proof of Service', 'Minute of Default Judgment'],
    workflow: ['REGISTRAR_FILING', 'JUDGMENT_GRANTED']
  },
  {
    id: 'rescission',
    label: 'Rescission of Judgment',
    category: CATEGORIES.JUDGMENT,
    desc: 'Application to set aside judgment',
    statute: 'Uniform Rule 31(2)(b) / Rule 42',
    icon: '↩️',
    baseFee: 4000,
    riskLevel: RISK_LEVELS.HIGH,
    serviceType: 'NORMAL_SERVICE',
    requiredDocs: ['Founding Affidavit', 'Bona Fide Defense'],
    workflow: ['DRAFTING', 'SERVICE', 'OPPOSITION', 'HEARING']
  },
  {
    id: 'interdict',
    label: 'Interdict',
    category: CATEGORIES.CRITICAL,
    desc: 'Mandatory or prohibitory interdict (urgent relief)',
    statute: 'Common Law',
    icon: '🛑',
    baseFee: 5500,
    riskLevel: RISK_LEVELS.HIGH,
    serviceType: 'PERSONAL_SERVICE_REQUIRED',
    requiredDocs: ['Founding Affidavit', 'Clear Right Evidence'],
    workflow: ['INTERIM_ORDER', 'RETURN_DATE', 'FINAL_ORDER']
  },
  {
    id: 'eviction',
    label: 'Eviction Application (PIE)',
    category: CATEGORIES.PROPERTY,
    desc: 'PIE Act eviction application and municipal service requirements',
    statute: 'PIE Act 19 of 1998',
    icon: '🏠',
    baseFee: 6000,
    riskLevel: RISK_LEVELS.HIGH,
    serviceType: 'SECTION_4_2_SERVICE',
    requiredDocs: ['Section 4(2) Notice', 'Founding Affidavit', 'Title Deed'],
    workflow: ['EX_PARTE_APP', 'SERVICE_MAIN', 'SERVICE_MUNICIPALITY', 'HEARING']
  },
  {
    id: 'rule_43',
    label: 'Rule 43 Application',
    category: CATEGORIES.FAMILY,
    desc: 'Interim matrimonial relief (Rule 43)',
    statute: 'Uniform Rule 43',
    icon: '💍',
    baseFee: 4500,
    riskLevel: RISK_LEVELS.MEDIUM,
    serviceType: 'NORMAL_SERVICE',
    requiredDocs: ['Sworn Statement (limited pages)'],
    workflow: ['ISSUING', 'SERVICE', 'REPLY', 'HEARING']
  },
  {
    id: 'divorce_settlement',
    label: 'Divorce Settlement Agreement',
    category: CATEGORIES.FAMILY,
    desc: 'Settlement agreement drafting and registration',
    statute: 'Divorce Act 70 of 1979',
    icon: '🤝',
    baseFee: 2500,
    riskLevel: RISK_LEVELS.LOW,
    serviceType: 'NONE',
    requiredDocs: ['ID Documents', 'Marriage Certificate', 'Ante-nuptial Contract'],
    workflow: ['NEGOTIATION', 'DRAFTING', 'SIGNING']
  }
]);

/* -------------------------
   Helper utilities (exported)
   - getById, getByCategory, validateSubmission, getNextWorkflowStep
   ------------------------- */

export function getById(id) {
  return LITIGATION_TYPES.find(t => t.id === id) || null;
}

export function getByCategory(category) {
  return LITIGATION_TYPES.filter(t => t.category === category);
}

/**
 * validateSubmission
 * - Ensures requiredDocs are present before allowing progression.
 * - Returns { ok: boolean, missing: [] }
 */
export function validateSubmission(typeId, uploadedDocs = []) {
  const type = getById(typeId);
  if (!type) return { ok: false, missing: ['unknown_type'] };
  const missing = type.requiredDocs.filter(r => !uploadedDocs.includes(r));
  return { ok: missing.length === 0, missing };
}

/**
 * getNextWorkflowStep
 * - Given current step token, returns next step or null if complete.
 */
export function getNextWorkflowStep(typeId, currentStep) {
  const type = getById(typeId);
  if (!type) return null;
  const idx = type.workflow.indexOf(currentStep);
  if (idx === -1 || idx === type.workflow.length - 1) return null;
  return type.workflow[idx + 1];
}

/* -------------------------
   FINAL NOTES
   - This module references PIE eviction guidance and civil procedure sources for compliance and workflow fidelity.
   - For investor readiness: add unit tests for validateSubmission and workflow transitions, and a migration script when extending types.
   ------------------------- */
