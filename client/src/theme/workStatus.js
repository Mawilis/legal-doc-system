/**
 * TITLE: WILSY OS Shared Source-Owned Work Status Semantics
 * VERSION: v1.1.0-HR01-HIGH-VISIBILITY-STATUS-PALETTE
 * AUTHORITY: WILSY OS client presentation only; EOS retains lifecycle truth.
 * EPITOME: One colour and accessible class vocabulary for Projects, People and
 *          subsequently My Work, Strategy, Calendar and Daily Attention.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/theme/workStatus.js
 * COLLABORATION / OWNERSHIP: ProjectWorkRow, ProjectTasksPanel and HrDashboard.
 * CERTIFICATION / UPDATE DATE: 2026-11-27
 * CHANGELOG: v1.1.0-HR01-HIGH-VISIBILITY-STATUS-PALETTE introduces visibly saturated, contrast-safe EOS status badges and project row lifecycle accents; no status mutation.
 * CHANGELOG: v1.0.3-M03-SECURITY-HEADER-SEAL includes mandatory sovereign security/privacy header metadata with no status behavior changes.
 * CHANGELOG: v1.0.2-M03-WHITESPACE-NORMALIZATION-FIX corrects human label whitespace normalization for task headers.
 * CHANGELOG: v1.0.1-M03-HUMAN-STATUS-LABEL-COMPATIBILITY resolves human-readable task status labels (e.g. In progress) to the same verified EOS semantic tone without changing lifecycle truth.
 * CHANGELOG: v1.0.0-M03-ENTERPRISE-WORK-COLOUR-SEMANTICS maps only verified
 *          statuses; unknown states remain neutral, never imply completion.
 * COMPLIANCE: AGENTS.md; WCAG 2.2 AA.
 * SECURITY / PRIVACY POSTURE: Source-state values only; no user PII, tokens, data persistence or browser storage.
 * TENANT BOUNDARY: Presentation-only, no tenant records or IAM.
 * AUTHORITY BOUNDARY: Visuals cannot authorize source actions.
 * FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution.
 */

export const WORK_STATUS = Object.freeze({
  TODO: 'TODO',
  IN_PROGRESS: 'IN_PROGRESS',
  BLOCKED: 'BLOCKED',
  DONE: 'DONE',
  CANCELLED: 'CANCELLED',
});

// Accessible light-surface semantics; design colours are never the sole
// meaning, and provisional transitions must retain their "pending" label.
const appearance = Object.freeze({
  neutral: Object.freeze({
    color: '#8792a2', chip: 'border-slate-600 bg-slate-600 text-white',
  }),
  active: Object.freeze({
    color: '#2563eb', chip: 'border-blue-700 bg-blue-700 text-white',
  }),
  success: Object.freeze({
    color: '#15803d', chip: 'border-emerald-700 bg-emerald-700 text-white',
  }),
  caution: Object.freeze({
    color: '#d49716', chip: 'border-amber-700 bg-amber-700 text-white',
  }),
  blocked: Object.freeze({
    color: '#be3640', chip: 'border-red-700 bg-red-700 text-white',
  }),
});

const tones = Object.freeze({
  TODO: 'neutral',
  DRAFT: 'neutral',
  PENDING_SOURCE: 'neutral',
  IN_PROGRESS: 'active',
  ACTIVE: 'active',
  APPLIED: 'active',
  SCREENING: 'active',
  INTERVIEW: 'active',
  SELECTED: 'active',
  SUBMITTED: 'caution',
  PENDING: 'caution',
  REVIEW_REQUIRED: 'caution',
  WAITING: 'caution',
  BLOCKED: 'blocked',
  REJECTED: 'blocked',
  DENIED: 'blocked',
  FAILED: 'blocked',
  DONE: 'success',
  COMPLETED: 'success',
  APPROVED: 'success',
  VERIFIED: 'success',
  CANCELLED: 'neutral',
  REVOKED: 'neutral',
  INACTIVE: 'neutral',
});

export function workStatusTone(status) {
  return typeof status === 'string'
    ? (tones[status.trim().toUpperCase().replace(/[\s-]+/g, '_')] || 'neutral')
    : 'neutral';
}

export function workStatusColor(status) {
  return appearance[workStatusTone(status)].color;
}

export function workStatusAccentClass(status) {
  return {
    neutral: 'border-l-slate-500',
    active: 'border-l-blue-600',
    success: 'border-l-emerald-700',
    caution: 'border-l-amber-600',
    blocked: 'border-l-red-700',
  }[workStatusTone(status)];
}

export function workStatusClasses(status) {
  return 'inline-flex items-center rounded-md border px-2 py-1 text-xs font-semibold '
    + appearance[workStatusTone(status)].chip;
}

// ARTIFACT: client/src/theme/workStatus.js
// VERSION: v1.1.0-HR01-HIGH-VISIBILITY-STATUS-PALETTE
// AUTHORITY BOUNDARY: No status writes or authorization inferred from colour.
// TENANT POSTURE: Presentation token contract only.
// FAIL-CLOSED POSTURE: Unknown statuses remain neutral.
// FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
// END OF WILSY OS SOVEREIGN ARTIFACT
