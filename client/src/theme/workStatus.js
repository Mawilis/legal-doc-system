/**
 * TITLE: WILSY OS Shared Source-Owned Work Status Semantics
 * VERSION: v1.0.1-M03-HUMAN-STATUS-LABEL-COMPATIBILITY
 * AUTHORITY: WILSY OS client presentation only; EOS retains lifecycle truth.
 * EPITOME: One colour and accessible class vocabulary for Projects, People and
 *          subsequently My Work, Strategy, Calendar and Daily Attention.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/theme/workStatus.js
 * COLLABORATION / OWNERSHIP: ProjectWorkRow, ProjectTasksPanel and HrDashboard.
 * CERTIFICATION / UPDATE DATE: 2026-11-27
 * CHANGELOG: v1.0.1-M03-HUMAN-STATUS-LABEL-COMPATIBILITY resolves human-readable task status labels (e.g. In progress) to the same verified EOS semantic tone without changing lifecycle truth.
 * CHANGELOG: v1.0.0-M03-ENTERPRISE-WORK-COLOUR-SEMANTICS maps only verified
 *          statuses; unknown states remain neutral, never imply completion.
 * COMPLIANCE: AGENTS.md; WCAG 2.2 AA.
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
    color: '#64748b', chip: 'border-slate-200 bg-slate-100 text-slate-800',
  }),
  active: Object.freeze({
    color: '#2563eb', chip: 'border-blue-200 bg-blue-50 text-blue-800',
  }),
  success: Object.freeze({
    color: '#15803d', chip: 'border-green-200 bg-green-50 text-green-900',
  }),
  caution: Object.freeze({
    color: '#b45309', chip: 'border-amber-300 bg-amber-50 text-amber-950',
  }),
  blocked: Object.freeze({
    color: '#b91c1c', chip: 'border-red-200 bg-red-50 text-red-900',
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
    ? (tones[status.trim().toUpperCase().replace(/[\\s-]+/g, '_')] || 'neutral')
    : 'neutral';
}

export function workStatusColor(status) {
  return appearance[workStatusTone(status)].color;
}

export function workStatusClasses(status) {
  return 'inline-flex items-center rounded-md border px-2 py-1 text-xs font-semibold '
    + appearance[workStatusTone(status)].chip;
}

// ARTIFACT: client/src/theme/workStatus.js
// VERSION: v1.0.1-M03-HUMAN-STATUS-LABEL-COMPATIBILITY
// AUTHORITY BOUNDARY: No status writes or authorization inferred from colour.
// TENANT POSTURE: Presentation token contract only.
// FAIL-CLOSED POSTURE: Unknown statuses remain neutral.
// FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
// END OF WILSY OS SOVEREIGN ARTIFACT
