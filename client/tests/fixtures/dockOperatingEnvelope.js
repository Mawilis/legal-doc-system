/**
 * TITLE: WILSY OS Dock Synthetic Operating Fixture
 * VERSION: v1.0.0
 * AUTHORITY: Test fixtures only; no real IAM grant.
 * EPITOME: Share a complete closed-catalog response across independent client certificates.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/tests/fixtures/dockOperatingEnvelope.js
 * COLLABORATION / OWNERSHIP: Dock component and schema tests.
 * CERTIFICATION / UPDATE DATE: 2026-11-25
 * CHANGELOG: v1.0.0 introduces synthetic role-aware operating envelopes.
 * COMPLIANCE: AGENTS.md; synthetic nonpersonal records.
 * SECURITY / PRIVACY POSTURE: No real tokens, records or provider calls.
 * TENANT BOUNDARY: Synthetic exact tenant/principal pair only.
 * AUTHORITY BOUNDARY: Fixtures confer no source permission.
 * FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively.
 */
export const PROJECT = 'prj-' + 'a'.repeat(48);
export const TASK = 'ptk-' + 'b'.repeat(48);
export const TENANT = 'dock-tenant';
export const PERSON = 'dock-person';

/**
 * @description Build a fresh synthetic inert envelope for one task revision.
 * @collaboration Unit and component tests. @institutional Grants no real IAM or writes.
 */
export function dockEnvelope({ revision = 1, status = 'TODO', participant = false, mutate = true, attach = true } = {}) {
  const source = { project_id: PROJECT, task_id: TASK, revision, fingerprint: String(revision).repeat(128).slice(0, 128), participant_view: participant };
  const specs = [['DRAFT_PLAN', 'Draft alignment plan', 'DRAFT_PLAN', null],
    ['OPEN_TASK', 'Open full task', 'NAVIGATE_TASK', null],
    ['REVIEW_EVIDENCE', 'Review dependencies and evidence', 'REVIEW_EVIDENCE', null]];
  if (mutate && ['TODO', 'BLOCKED', 'IN_PROGRESS'].includes(status)) specs.push(status === 'IN_PROGRESS'
    ? ['COMPLETE_TASK', 'Complete task', 'PROJECT_TASK_TRANSITION', 'DONE']
    : ['START_TASK', status === 'BLOCKED' ? 'Resume work' : 'Start work', 'PROJECT_TASK_TRANSITION', 'IN_PROGRESS']);
  return { catalog: 'wilsy.dock.v1', tenant_id: TENANT, principal_id: PERSON,
    observed_at: '2026-11-25T12:00:00Z', source, model_invoked: false, financial_execution: false,
    components: [{ type: 'TaskBrief', id: 'brief', source, title: 'MW-T11 alignment',
      purpose: 'Align the Dock with authorized work.', status, owner: null, deadline: '2026-12-01',
      dependencies: [], established: 'Projects verified the current task and its revision.',
      blockers: [], next_action: 'Draft alignment plan', can_attach: attach },
    { type: 'ActionList', id: 'actions', actions: specs.map(([kind, outcome, operation, target], priority) => ({
      id: TASK + ':' + kind, component_id: 'actions', kind, source, outcome, priority,
      availability: 'AVAILABLE', verified_revision: revision,
      execution: { operation, target_status: target, requires_confirmation: operation === 'PROJECT_TASK_TRANSITION' },
      correlation_id: 'd'.repeat(128),
    })) }] };
}

// ARTIFACT: dockOperatingEnvelope.js
// VERSION: v1.0.0
// AUTHORITY BOUNDARY: synthetic test data only
// TENANT POSTURE: fixed synthetic exact scope
// FAIL-CLOSED POSTURE: no production source or identity used
// FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
// END OF WILSY OS SOVEREIGN ARTIFACT
