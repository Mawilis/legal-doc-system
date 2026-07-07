/* eslint-disable */
const crypto = require('crypto');

const RULE_ENGINE_VERSION = 'wilsy-lead-category-engine-v1';

/**
 * @function normalizeLeadText
 * @description Normalizes Lead values for deterministic rule matching.
 * @collaboration Lead category engine, saved views, Wilsy AI answers, and audit-safe comparisons.
 * @param {*} value Candidate value.
 * @returns {string} Normalized value.
 */
function normalizeLeadText(value) {
  if (value === null || value === undefined) return '';
  if (Array.isArray(value)) return value.map(normalizeLeadText).filter(Boolean).join(' ');
  if (typeof value === 'object') {
    if (value.name) return normalizeLeadText(value.name);
    if (value.label) return normalizeLeadText(value.label);
    if (value.email) return normalizeLeadText(value.email);
    if (value.id) return normalizeLeadText(value.id);
    return JSON.stringify(value);
  }
  return String(value).trim();
}

/**
 * @function normalizeLeadToken
 * @description Converts a Lead value into lower-case searchable text.
 * @collaboration Criteria matching, category grouping, custom views, and backend run previews.
 * @param {*} value Candidate value.
 * @returns {string} Lower-case token.
 */
function normalizeLeadToken(value) {
  return normalizeLeadText(value).toLowerCase();
}

/**
 * @function getLeadFieldValue
 * @description Resolves known CRM Lead fields and nested fallback paths from a Lead record.
 * @collaboration Backend views, AI category explanations, and Lead evidence inspection.
 * @param {object} lead Lead record.
 * @param {string} field Field key.
 * @returns {*} Field value.
 */
function getLeadFieldValue(lead = {}, field = '') {
  const key = normalizeLeadToken(field);

  const knownFields = {
    owner: lead.ownerName || lead.owner || lead.assignedTo || lead.ownerEmail || lead.ownerId,
    ownername: lead.ownerName || lead.owner || lead.assignedTo,
    owneremail: lead.ownerEmail || lead.owner?.email,
    status: lead.status || lead.leadStatus || lead.stage,
    stage: lead.stage || lead.status,
    score: lead.score || lead.leadScore || lead.qualificationScore,
    company: lead.company || lead.companyName || lead.accountName,
    email: lead.email || lead.primaryEmail,
    phone: lead.phone || lead.mobile || lead.primaryPhone,
    source: lead.source || lead.sourceChannel || lead.campaign || lead.origin,
    campaign: lead.campaign || lead.campaignName,
    createdat: lead.createdAt,
    updatedat: lead.updatedAt,
    lastactivity: lead.lastActivityAt || lead.lastActivity || lead.updatedAt,
    verified: lead.verified || lead.isVerified || lead.verificationStatus,
    compliance: lead.complianceStatus || lead.consentStatus,
    consent: lead.consentStatus || lead.popiaConsent || lead.gdprConsent,
  };

  if (Object.prototype.hasOwnProperty.call(knownFields, key)) {
    return knownFields[key];
  }

  return String(field || '')
    .split('.')
    .reduce((current, part) => {
      if (!current || typeof current !== 'object') return undefined;
      return current[part];
    }, lead);
}

/**
 * @function hasLeadSourceEvidence
 * @description Checks whether a Lead carries source or provenance evidence.
 * @collaboration Source Gaps, evidence vault posture, import ledger, and Wilsy AI lead advice.
 * @param {object} lead Lead record.
 * @returns {boolean} Whether source evidence exists.
 */
function hasLeadSourceEvidence(lead = {}) {
  return Boolean(
    lead.source ||
    lead.sourceChannel ||
    lead.campaign ||
    lead.campaignId ||
    lead.importBatchId ||
    lead.connectorReceiptId ||
    lead.utmSource ||
    lead.referrer ||
    lead.origin ||
    lead.provenance ||
    lead.createdBy
  );
}

/**
 * @function hasLeadContactPath
 * @description Checks whether a Lead has a usable contact path.
 * @collaboration Verification gates, lead scoring, compliance posture, and owner actionability.
 * @param {object} lead Lead record.
 * @returns {boolean} Whether contact path exists.
 */
function hasLeadContactPath(lead = {}) {
  return Boolean(lead.email || lead.primaryEmail || lead.phone || lead.mobile || lead.primaryPhone);
}

/**
 * @function hasLeadOwner
 * @description Checks whether a Lead has an accountable owner.
 * @collaboration Owner assignment repair, WK owner display, action queues, and audit views.
 * @param {object} lead Lead record.
 * @returns {boolean} Whether owner exists.
 */
function hasLeadOwner(lead = {}) {
  return Boolean(
    lead.ownerName || lead.owner || lead.assignedTo || lead.ownerId || lead.ownerEmail
  );
}

/**
 * @function hasMeaningfulLeadActivity
 * @description Detects whether a Lead has meaningful post-create activity.
 * @collaboration Untouched Leads, owner SLA monitoring, pipeline health, and Wilsy AI advice.
 * @param {object} lead Lead record.
 * @returns {boolean} Whether activity exists.
 */
function hasMeaningfulLeadActivity(lead = {}) {
  const activityCount = Number(lead.activityCount || lead.activitiesCount || lead.touchCount || 0);
  return Boolean(
    activityCount > 0 ||
    lead.lastActivityAt ||
    lead.lastActivity ||
    lead.lastEmailAt ||
    lead.lastCallAt ||
    lead.lastMeetingAt ||
    lead.notesCount ||
    lead.tasksCount ||
    lead.statusChangedAt
  );
}

/**
 * @function hasFailedLeadGate
 * @description Detects hard failures that block a Lead from verified operating posture.
 * @collaboration Failed Gates, compliance status, duplicate control, source contradictions, and audit records.
 * @param {object} lead Lead record.
 * @returns {boolean} Whether a hard failure exists.
 */
function hasFailedLeadGate(lead = {}) {
  const status = normalizeLeadToken(
    lead.status || lead.stage || lead.verificationStatus || lead.complianceStatus
  );
  const failureSignals = [
    lead.failed === true,
    lead.gateFailed === true,
    lead.isDuplicate === true,
    lead.duplicateBlocked === true,
    lead.blocked === true,
    lead.disqualified === true,
    status.includes('failed'),
    status.includes('blocked'),
    status.includes('invalid'),
    status.includes('disqualified'),
    normalizeLeadToken(lead.emailValidationStatus).includes('invalid'),
    normalizeLeadToken(lead.phoneValidationStatus).includes('invalid'),
    normalizeLeadToken(lead.consentStatus).includes('failed'),
  ];

  return failureSignals.some(Boolean);
}

/**
 * @function resolveLeadScore
 * @description Resolves a numeric score from a Lead record.
 * @collaboration Priority Leads, average score, qualification posture, and AI scoring summaries.
 * @param {object} lead Lead record.
 * @returns {number} Lead score.
 */
function resolveLeadScore(lead = {}) {
  const rawScore = lead.score || lead.leadScore || lead.qualificationScore || lead.aiScore || 0;
  const score = Number(rawScore);
  return Number.isFinite(score) ? score : 0;
}

/**
 * @function isPriorityLead
 * @description Detects priority leads using score, urgency, value, and intent posture.
 * @collaboration Priority Leads category, revenue routing, owner action queue, and Wilsy AI recommendations.
 * @param {object} lead Lead record.
 * @returns {boolean} Whether Lead is priority.
 */
function isPriorityLead(lead = {}) {
  const score = resolveLeadScore(lead);
  const stage = normalizeLeadToken(lead.stage || lead.status);
  const value = Number(lead.estimatedValue || lead.dealValue || lead.pipelineValue || 0);
  return Boolean(
    score >= 85 ||
    value >= 50000 ||
    stage.includes('qualified') ||
    stage.includes('proposal') ||
    lead.priority === true ||
    normalizeLeadToken(lead.intent).includes('high')
  );
}

/**
 * @function isVerifiedLead
 * @description Checks whether a Lead passes required verification gates.
 * @collaboration Verified Leads category, source integrity, owner accountability, and compliance-ready records.
 * @param {object} lead Lead record.
 * @returns {boolean} Whether Lead is verified.
 */
function isVerifiedLead(lead = {}) {
  if (hasFailedLeadGate(lead)) return false;

  const verificationStatus = normalizeLeadToken(lead.verificationStatus || lead.status);
  const explicitVerified =
    lead.verified === true || lead.isVerified === true || verificationStatus.includes('verified');

  return Boolean(
    explicitVerified ||
    (hasLeadOwner(lead) && hasLeadContactPath(lead) && hasLeadSourceEvidence(lead))
  );
}

/**
 * @function isPendingReviewLead
 * @description Detects Leads that require review without hard failure.
 * @collaboration Pending Review, source repair, compliance queue, and owner accountability.
 * @param {object} lead Lead record.
 * @returns {boolean} Whether Lead is pending review.
 */
function isPendingReviewLead(lead = {}) {
  if (hasFailedLeadGate(lead)) return false;
  return (
    !isVerifiedLead(lead) ||
    !hasLeadOwner(lead) ||
    !hasLeadContactPath(lead) ||
    !hasLeadSourceEvidence(lead)
  );
}

/**
 * @function doesLeadMatchBuiltInCategory
 * @description Applies the versioned built-in Lead category algorithm.
 * @collaboration View Organizer, backend counts, saved views, audit logs, and Wilsy AI category answers.
 * @param {object} lead Lead record.
 * @param {string} categoryId Category id.
 * @returns {boolean} Whether Lead matches category.
 */
function doesLeadMatchBuiltInCategory(lead = {}, categoryId = 'ALL_LEADS') {
  const normalizedId = normalizeLeadToken(categoryId).replace(/[^a-z0-9]/g, '');

  if (normalizedId === 'all' || normalizedId === 'allleads') return true;
  if (normalizedId === 'priority' || normalizedId === 'priorityleads') return isPriorityLead(lead);
  if (normalizedId === 'verified' || normalizedId === 'verifiedleads') return isVerifiedLead(lead);
  if (normalizedId === 'pending' || normalizedId === 'pendingreview')
    return isPendingReviewLead(lead);
  if (normalizedId === 'sourcegaps') return !hasLeadSourceEvidence(lead);
  if (normalizedId === 'untouched') return !hasMeaningfulLeadActivity(lead);
  if (normalizedId === 'failed' || normalizedId === 'failedgates') return hasFailedLeadGate(lead);

  return true;
}

/**
 * @function doesCriterionMatchLead
 * @description Applies one saved view criterion to a Lead.
 * @collaboration Custom views, backend preview, CRUD persistence, and Wilsy AI explainability.
 * @param {object} lead Lead record.
 * @param {object} criterion Criterion.
 * @returns {boolean} Whether criterion matches.
 */
function doesCriterionMatchLead(lead = {}, criterion = {}) {
  const fieldValue = getLeadFieldValue(lead, criterion.field);
  const left = normalizeLeadToken(fieldValue);
  const right = normalizeLeadToken(criterion.value);
  const operator = normalizeLeadToken(criterion.operator || 'contains');
  const numericLeft = Number(fieldValue);
  const numericRight = Number(criterion.value);

  if (operator === 'contains') return left.includes(right);
  if (operator === 'notcontains') return !left.includes(right);
  if (operator === 'equals' || operator === 'is') return left === right;
  if (operator === 'notequals' || operator === 'isnot') return left !== right;
  if (operator === 'startswith') return left.startsWith(right);
  if (operator === 'endswith') return left.endsWith(right);
  if (operator === 'exists' || operator === 'isnotempty') return Boolean(left);
  if (operator === 'missing' || operator === 'isempty') return !left;
  if (operator === 'greaterthan')
    return (
      Number.isFinite(numericLeft) && Number.isFinite(numericRight) && numericLeft > numericRight
    );
  if (operator === 'lessthan')
    return (
      Number.isFinite(numericLeft) && Number.isFinite(numericRight) && numericLeft < numericRight
    );

  return left.includes(right);
}

/**
 * @function doesLeadMatchCustomCriteria
 * @description Applies all saved custom view criteria to a Lead.
 * @collaboration Custom View Builder, backend run, preview, audit hash, and Wilsy AI view answers.
 * @param {object} lead Lead record.
 * @param {Array<object>} criteria Criteria list.
 * @returns {boolean} Whether Lead matches all criteria.
 */
function doesLeadMatchCustomCriteria(lead = {}, criteria = []) {
  const safeCriteria = Array.isArray(criteria) ? criteria.filter(Boolean) : [];
  if (!safeCriteria.length) return true;
  return safeCriteria.every((criterion) => doesCriterionMatchLead(lead, criterion));
}

/**
 * @function buildCriteriaHash
 * @description Creates a deterministic hash for criteria and audit comparison.
 * @collaboration Audit receipts, query explainability, saved view versioning, and AI traceability.
 * @param {Array<object>} criteria Criteria list.
 * @returns {string} Criteria hash.
 */
function buildCriteriaHash(criteria = []) {
  const safeCriteria = Array.isArray(criteria) ? criteria : [];
  return crypto.createHash('sha256').update(JSON.stringify(safeCriteria)).digest('hex');
}

/**
 * @function buildLeadCategorySummary
 * @description Builds live counts for the built-in Lead Organizer categories.
 * @collaboration CRM Leads Organizer, backend category engine, Wilsy AI, audit counts, and owner views.
 * @param {Array<object>} leads Lead records.
 * @returns {object} Category summary.
 */
function buildLeadCategorySummary(leads = []) {
  const safeLeads = Array.isArray(leads) ? leads : [];
  const categories = [
    ['ALL_LEADS', 'All Leads'],
    ['PRIORITY_LEADS', 'Priority Leads'],
    ['VERIFIED_LEADS', 'Verified Leads'],
    ['PENDING_REVIEW', 'Pending Review'],
    ['SOURCE_GAPS', 'Source Gaps'],
    ['UNTOUCHED', 'Untouched'],
    ['FAILED_GATES', 'Failed Gates'],
  ];

  return {
    ruleEngineVersion: RULE_ENGINE_VERSION,
    total: safeLeads.length,
    categories: categories.map(([id, label]) => ({
      id,
      label,
      count: safeLeads.filter((lead) => doesLeadMatchBuiltInCategory(lead, id)).length,
      total: safeLeads.length,
    })),
  };
}

module.exports = {
  RULE_ENGINE_VERSION,
  buildCriteriaHash,
  buildLeadCategorySummary,
  doesCriterionMatchLead,
  doesLeadMatchBuiltInCategory,
  doesLeadMatchCustomCriteria,
  getLeadFieldValue,
  hasFailedLeadGate,
  hasLeadContactPath,
  hasLeadOwner,
  hasLeadSourceEvidence,
  hasMeaningfulLeadActivity,
  isPendingReviewLead,
  isPriorityLead,
  isVerifiedLead,
  normalizeLeadText,
  normalizeLeadToken,
  resolveLeadScore,
};
