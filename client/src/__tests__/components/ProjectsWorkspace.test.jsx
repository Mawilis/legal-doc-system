/**
 * TITLE: WILSY OS Projects workspace interaction certificate
 * VERSION: v2.35.0-EOS-CAPABILITY-PROJECTION-CERT
 * AUTHORITY: Client contract evidence only; Python EOS owns Projects authority.
 * EPITOME: Proves exact-scope list/detail/summary validation and the user-facing
 *          create, update, status-transition and archive readback sequence.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/__tests__/components/ProjectsWorkspace.test.jsx
 * COLLABORATION / OWNERSHIP: Vitest mocks the existing authenticated api.js transport; no database is contacted.
 * CERTIFICATION / UPDATE DATE: 2026-11-19.
 * COMPLIANCE: AGENTS.md; POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
 * SECURITY / PRIVACY POSTURE: Synthetic exact-scope fixtures only; no tokens,
 *          real identities, private comments or production credentials.
 * TENANT BOUNDARY: Exact tenant and project checks; no root fallback.
 * AUTHORITY BOUNDARY: Mock client assertions only; Python EOS owns IAM,
 *          task commands, decisions, evidence and immutable audit truth.
 * FINANCIAL AUTHORITY BOUNDARY: No financial execution or approval grants.
 * CHANGELOG: v2.35.0-EOS-CAPABILITY-PROJECTION-CERT supplies only
 *          synthetic exact-project capability records for existing work
 *          journeys; no test fixture grants actual update authority.
 * CHANGELOG: v2.34.1-CONTEXTUAL-MENU-REGRESSION-CERT adapts
 *          existing task edit/activity journeys to desktop menu roles.
 * CHANGELOG: v2.34.0-CAPABILITY-AWARE-MENU-CERT pins desktop menu
 *          keyboard/ARIA and separate Assign/Edit, ensuring explicitly
 *          forbidden action flags hide commands without invoking EOS.
 * CHANGELOG: v2.33.0-WORK-ROW-SELECTION-DENSITY-CERT proves
 *          selected rows toggle independently and page selection is visual
 *          only; work density switches without a server mutation.
 * CHANGELOG: v2.32.0-PENDING-WORK-TRANSITION-CERT verifies immediate
 *          pending feedback without premature task completion, then requires
 *          authoritative readback to clear the pending presentation.
 * CHANGELOG: v2.31.1-SOURCE-REASSIGN-NOOP-CERT proves an assigned
 *          contributor is actionable and an unchanged selection cannot
 *          issue a no-op task revision through EOS.
 * CHANGELOG: v2.31.0-ASSIGNMENT-FOCUS-CERT verifies A opens a compact
 *          current-project assignment picker without unrelated task fields,
 *          while task edits preserve their separate revisioned form.
 * CHANGELOG: v2.30.2-NO-OPAQUE-PROJECT-HEADER-CERT pins the removal
 *          of automatic hexadecimal project codes from the main list and
 *          selected-project header without changing authoritative IDs.
 * CHANGELOG: v2.30.1-COMMITTED-TEMPLATE-COPY-CERT asserts a confirmed
 *          201 activation uses the committed-pending-readback message, not
 *          the distinct ambiguous-save warning.
 * CHANGELOG: v2.30.0-FOCUSED-WORK-KEYBOARD-CERT proves J/K focus,
 *          A opens a bounded edit sheet, and no keyboard shortcut creates
 *          an unauthorized work transition or completion attestation.
 * CHANGELOG: v2.29.1-UNCERTAIN-TEMPLATE-OUTCOME-CERT proves an ambiguous
 *          activation response prompts a source-based list inspection, not
 *          a duplicate POST or a fabricated saved/failed claim.
 * CHANGELOG: v2.29.0-PROJECT-MY-WORK-FILTER-CERT verifies that current
 *          assignee filtering uses only the source-backed current project page,
 *          remains reversible and performs no unauthorized write.
 * CHANGELOG: v2.28.7-MOBILE-ACTION-SHEET-GESTURE-CERT pins a downward
 *          sheet dismissal without executing a mutation or leaving body
 *          scroll locked on a mobile viewport.
 * CHANGELOG: v2.28.6-POSTCOMMAND-REVISION-BROWSER-CERT waits for the
 *          committed revision before reading owner names, reacquires
 *          work rows after filters remount them, and scopes contextual
 *          actions to the current source row.
 * CHANGELOG: v2.28.6-POSTCOMMAND-REVISION-BROWSER-CERT validates source changes
 *          independently of collapsed optional visualizations, scopes
 *          contextual action selection, and preserves correct post-command
 *          disabled states after owner assignment.
 * CHANGELOG: v2.28.6-POSTCOMMAND-REVISION-BROWSER-CERT prevents invisible
 *          template form labels and opaque internal IDs in the verified
 *          industry creation experience at the current test head.
 * CHANGELOG: v2.28.6-POSTCOMMAND-REVISION-BROWSER-CERT certifies Arrow/Home/End
 *          navigation and focus return for the real responsive action
 *          presenter without adding fake lifecycle authority.
 * CHANGELOG: v2.28.6-POSTCOMMAND-REVISION-BROWSER-CERT awaits source-ready row actions after
 *          each command, opens contextual overflow rather than removed
 *          peer buttons, and exercises on-demand checklist/assignment state.
 * CHANGELOG: v2.28.1-KEYBOARD-WORK-DRAWER-CERT verifies
 *          keyboard Enter opens the exact source work drawer and Close
 *          returns focus without mutating persisted EOS task data.
 * CHANGELOG: v2.28.0-RESPONSIVE-WORK-ACTION-CERT asserts
 *          the status-derived primary action, Escape focus restoration,
 *          contextual blocking and explicit destructive cancel confirmation.
 * CHANGELOG: v2.27.3-VALID-TEMPLATE-READBACK-FIXTURE uses a
 *          real two-step work/milestone blueprint in the accepted-command
 *          delayed-list regression, matching strict catalogue validation.
 * CHANGELOG: v2.27.2-CONTEXTUAL-TASK-EDIT-CERT ensures
 *          modal task editing retains EOS revision readback and an
 *          accessible, discoverable save action.
 * CHANGELOG: v2.27.1-NO-FALSE-EMPTY-AFTER-COMMIT-CERT refuses
 *          to render an empty-tenant notice over EOS-confirmed persisted
 *          template materialisation pending list reconciliation.
 * CHANGELOG: v2.27.0-POSTCOMMIT-READBACK-SEPARATION-CERT guards against false
 *          template save failures after EOS committed an authoritative
 *          project but the independent list has not yet returned that item.
 * CHANGELOG: v2.26.1-COLLAPSED-PORTFOLIO-CERT verifies optional portfolio chart disclosure
 *          while the source-backed project table remains primary.
 * CHANGELOG: v2.26.0-PRIMARY-QUEUE-POSTCOMMIT-REGRESSION certifies read-first queue disclosures,
 *          direct Start/Complete controls, contextual secondary task actions,
 *          and separated accepted template activation versus readback failures.
 * CHANGELOG: v2.25.2-EXACT-STATUS-SOURCE-READBACK-CERT verifies
 *          the actual source-backed status control after transition,
 *          without depending on the portfolio toolbar removed from detail.
 * CHANGELOG: v2.25.1-TEMPLATE-RENAMED-DRAFT-CERT certifies
 *          the user-renamed project draft is passed verbatim into the
 *          independently authenticated template activation contract.
 * CHANGELOG: v2.25.0-COMPACT-SELECTED-PROJECT-CERT confirms the
 *          portfolio summary is displayed in list mode, while selected
 *          project views prioritize verified project work; a summary 503
 *          never hides the authorized list or detail on navigation.
 * CHANGELOG: v2.24.0-SEVEN-INDUSTRY-MATERIALIZATION-CLIENT-CERT verifies
 *          seven exact-scope source definitions, a selected business blueprint,
 *          one explicit activation, and independent project list/detail readback.
 * CHANGELOG: v2.23.0-ACTIVITY-FIRST-TEMPLATE-UI-CERT verifies that source activity precedes the
 *          optional editor in DOM, with contextual accessible note actions.
 * CHANGELOG: v2.22.0-CONTEXTUAL-NOTE-READBACK-CERT verifies compact read-first
 *          source notes, optional new-note composer and implicit CAS revision
 *          without exposing opaque audit identifiers in the note board.
 * CHANGELOG: v2.21.0-FOUR-SOURCE-ACTIVITY-CERT proves
 *          independently verified comment, lifecycle, decision and file
 *          events render chronologically, and links remain in exact-task
 *          approval and attachment workflows without new IAM.
 * CHANGELOG: v2.20.0-AUTHORITATIVE-TASK-ACTIVITY-CERT certifies
 *          source-verified task lifecycle events and comment activity appear
 *          newest-first, and the unified Activity & discussion navigation
 *          preserves separately authorized decisions and evidence links.
 * CHANGELOG: v2.19.0-TOP-LEVEL-DISCUSSIONS-CERT certifies
 *          the primary Discussions tab opens an EOS-verified task chooser
 *          without rendering the work dashboard, and selected task comments
 *          remain independently scoped to their canonical project/task.
 * CHANGELOG: v2.18.0-ONE-CLICK-DISCUSSION-CERT verifies
 *          Discuss exposes EOS source-backed comments immediately with the
 *          composer closed, and Write update opens the safe Markdown editor
 *          only on explicit request; retains original draft/readback checks.
 * CHANGELOG: v2.17.0-ON-DEMAND-COMMENT-HISTORY-CERT verifies
 *          comments remain collapsed initially, open on explicit request,
 *          and hide again without losing the independently verified source.
 * CHANGELOG: v2.16.1-ASSIGNMENT-OVERVIEW-CERT updates
 *          owner/department assignment readback assertions for the intentional
 *          source-honest Overview label; verifies the ID is retained in the
 *          title attribute and not exposed as primary display text.
 * CHANGELOG: v2.16.0-OVERVIEW-READABILITY-CERT verifies
 *          overview renders readable source-owned actor names and avoids
 *          publishing unverified department IDs as user-facing labels.
 * CHANGELOG: v2.15.0-PROJECT-SUMMARY-503-ISOLATION-CERT verifies
 *          the independently authorized project page remains operational
 *          when summary returns HTTP 503 before or after its list readback;
 *          foreign-tenant summary rejection remains fail-closed.
 * CHANGELOG: v2.14.0-SAFE-DISCUSSION-MARKDOWN-CERT verifies
 *          literal pasted Markdown renders in live comment preview, escaped
 *          untrusted HTML remains text, and history formats EOS-owned bodies
 *          without changing the stored comment or its authority.
 * CHANGELOG: v2.13.0-FOCUSED-ACTION-NAMED-MEMBER-CERT certifies
 *          focused discussion replacing the long work table and composer
 *          preceding comment history; verifies sourced participant names and
 *          unknown-name fallback without deriving identity from opaque IDs.
 * CHANGELOG: v2.12.1-PARENT-BOUND-CHECKLIST-CERT certifies
 *          Add checklist step selects the EOS-verified active parent before
 *          submitting the existing idempotent task create command.
 * CHANGELOG: v2.12.0-PERSISTED-TODO-CHECKLIST-CERT proves To-do checkboxes
 *          cannot assert Done optimistically, require conscious confirmation,
 *          and reflect the revisioned EOS transition only after fresh source
 *          readback; preserves existing tenant and command scope.
 * CHANGELOG: v2.11.0-LIFECYCLE-AUDIT-VISUAL-CERT proves status
 *          visualization changes only after EOS readback, actionable bar
 *          filters and newest-revision-first audit presentation.
 * CHANGELOG: v2.10.0-OPERATIONAL-WORK-QUEUE-CERT certifies distinct EOS subtask and
 *          milestone commands, active parent selection, and current-page queue
 *          search/filter over exact-scope verified task readbacks.
 * CHANGELOG: v2.9.0-INDEXED-OWNER-PAGINATION-CERT verifies owner-filtered EOS endpoint and source-bound count/pagination, never client-only filtering across 500+ projects.
 * CHANGELOG: v2.27.3-VALID-TEMPLATE-READBACK-FIXTURE certifies owner-only filtering against the authoritative current registry page, with no participant IAM fallback or fake total counts; independently keeps participant navigation for explicitly admitted principals.
 * CHANGELOG: v2.27.3-VALID-TEMPLATE-READBACK-FIXTURE certifies author-selected colour in note command, independently verified EOS readback and sticky-board presentation without project mutation.
 * CHANGELOG: v2.27.3-VALID-TEMPLATE-READBACK-FIXTURE verifies human creator, owner and audit actor display names are backed by the exact source identity, while preserving immutable command and event IDs.
 * CHANGELOG: v2.27.3-VALID-TEMPLATE-READBACK-FIXTURE shows tenant-bound human owner names while submitting immutable principal IDs, and denies fabricated or incomplete name projections without allowing assignment.
 * CHANGELOG: v2.27.3-VALID-TEMPLATE-READBACK-FIXTURE certifies selected-project task-first view, full-width workspace, separate overview, settings, notes and audit navigation without weakening source checks.
 * CHANGELOG: v2.27.3-VALID-TEMPLATE-READBACK-FIXTURE proves a
 *            Daily Attention participant-focused project opens the separately
 *            authorized Assigned Projects UI without owner-list side effects.
 * CHANGELOG: v2.27.3-VALID-TEMPLATE-READBACK-FIXTURE adds in-place task
 *            editing and updated revision readback without changing project
 *            Planned status, task graph or tenant authorization scope.
 * CHANGELOG: v2.27.3-VALID-TEMPLATE-READBACK-FIXTURE certifies task creation, verified
 *            EOS readback, revision-guarded transition and unmodified Planned
 *            project state in the existing authenticated client harness.
 * CHANGELOG: v2.27.3-VALID-TEMPLATE-READBACK-FIXTURE waits for the committed note row
 *            instead of a transient draft textarea with the same source text.
 * CHANGELOG: v2.27.3-VALID-TEMPLATE-READBACK-FIXTURE certifies source-backed project note
 *            creation/readback without modifying Planned status, propagating
 *            current principal/tenant scope or granting participant authority.
 * CHANGELOG: v2.27.3-VALID-TEMPLATE-READBACK-FIXTURE certifies server-side exact-tenant status filtering,
 *            one-page post-filter readback and no client-invented rows.
 * CHANGELOG: v2.27.3-VALID-TEMPLATE-READBACK-FIXTURE tests server-verified page metadata, source
 *            pagination beyond the first page, and denial of phantom next pages.
 * CHANGELOG: v2.27.3-VALID-TEMPLATE-READBACK-FIXTURE proves navigation
 *            beyond 100 same-tenant projects and source-verified status graph
 *            counts while retaining the existing lifecycle assertions.
 *            v1.6.3-RUNNER-PORTABLE-CSS-CERT resolves the source stylesheet
 *            from Vitest's project root rather than transformed import.meta.url;
 *            retains exact semantic label selectors and all assertions.
 *            v1.6.2-ACTUAL-ACCOUNTABILITY-STYLE-HOOK-CERT ensures the rendered
 *            project accountability form is actually targeted by the
 *            contrasting semantic stylesheet; protects against dead selectors.
 *            v1.6.1-EXPLICIT-ASSIGNMENT-SOURCE-STATE-CERT certifies user-visible current
 *            directory counts and fail-closed empty selectors without
 *            inventing principal, department or a completed assignment.
 *            v1.6.0-GOVERNED-ACCOUNTABILITY-CLIENT-CERT covers source-backed owner/department selection,
 *            independently authorized department creation and audited CAS
 *            assignment with fresh list and detail readback.
 * v1.5.0-SOURCE-VERIFIED-AUTO-CODE-CERT verifies
 *            one-click legacy project-code generation, revision guarding,
 *            independent EOS list/detail confirmation, and no duplicate action.
 * CHANGELOG: v1.4.0-NATIVE-CALENDAR-EXECUTION-CERT verifies
 *            visible Start and Target native calendar picker actions
 *            and ISO date-only values without premature EOS mutation.
 * CHANGELOG: v1.3.0-FLUID-PROJECT-DETAIL-PRESENTATION-CERT proves
 *            full-width list, selected detail layout, safe formatted scope
 *            in both collapsed and expanded modes, and sourced null values.
 * CHANGELOG: v1.2.0-STRATEGY-HANDOFF-SCOPE-CERT proves Strategy focus requires an
 *            authenticated exact-tenant list before detail readback and
 *            rejects absent IDs without issuing any project mutations.
 * CHANGELOG: v1.1.1-EXACT-SCOPE-CREATE-UPDATE-ARCHIVE-CERT covers full synthetic lifecycle and rejects stale or foreign envelopes; v1.0.1 covers create replay and denial.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
 * SECURITY / PRIVACY POSTURE: Synthetic test identities only; no credential or production data.
 * TENANT BOUNDARY: Tests assert selected tenant/principal envelopes and stale response isolation; not a live EOS isolation certificate.
 * AUTHORITY BOUNDARY: HTTP is mocked; no IAM or entitlement grant is made or proven.
 * FINANCIAL AUTHORITY BOUNDARY: No financial command is exercised.
 */
import React from 'react';
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { within, act, cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

const api = vi.hoisted(() => ({ get: vi.fn(), post: vi.fn(), patch: vi.fn() }));
vi.mock('../../services/api.js', () => ({ default: api }));

import ProjectsWorkspace from '../../components/workspaces/ProjectsWorkspace.jsx';
import ProjectWorkRowActions from '../../components/workspaces/ProjectWorkRowActions.jsx';

const TENANT = 'projects-cert-tenant';
const PRINCIPAL = 'projects-cert-principal';
const PROJECT_ID = `prj-${'a'.repeat(48)}`;
const project = (overrides = {}) => ({
  project_id: PROJECT_ID,
  tenant_id: TENANT,
  name: 'Persisted roadmap',
  code: 'ROADMAP',
  summary: 'Source-confirmed project',
  status: 'planned',
  created_by_principal_id: PRINCIPAL,
  revision: 1,
  created_at: '2026-11-16T12:00:00+00:00',
  updated_at: '2026-11-16T12:00:00+00:00',
  archived_at: null,
  target_date: null,
  ...overrides,
});
const event = (type, revision, tenantId = TENANT, projectId = PROJECT_ID) => ({
  tenant_id: tenantId,
  event_id: `evt-${type}-${revision}`,
  project_id: projectId,
  event_type: type,
  actor_principal_id: PRINCIPAL,
  revision,
  occurred_at: `2026-11-16T12:0${Math.min(revision, 9)}:00+00:00`,
});
const result = (value, events = [event('PROJECT_CREATED', value.revision)]) => ({
  schema: 'WILSY-PROJECT-RESULT/V1',
  tenant_id: value.tenant_id,
  principal_id: PRINCIPAL,
  project: value,
  events,
  actor_profiles: Object.fromEntries(
    [...new Set([value.created_by_principal_id, value.owner_principal_id,
      ...events.map(entry => entry.actor_principal_id)].filter(Boolean))]
      .map(id => [id, {
        first_name: id === PRINCIPAL ? 'Verified' : 'Assigned',
        last_name: id === PRINCIPAL ? 'Creator' : 'Owner',
      }]),
  ),
  authority: { source: 'PYTHON_EOS_PROJECT_REGISTRY', financial_execution: false },
});
const list = (items, tenantId = TENANT, principalId = PRINCIPAL) => ({
  schema: 'WILSY-PROJECT-LIST/V1', tenant_id: tenantId, principal_id: principalId, items,
  limit: 100, offset: 0,
});
const summary = (items, tenantId = TENANT, principalId = PRINCIPAL) => {
  const counts = { total: items.length, active: 0, planned: 0, on_hold: 0, done: 0, cancelled: 0 };
  for (const item of items) if (!item.archived_at) counts[item.status] += 1;
  return { schema: 'WILSY-PROJECT-SUMMARY/V1', tenant_id: tenantId, principal_id: principalId, counts };
};

// Synthetic EOS permission fixture: never a real grant or authenticated claim.
const mockProjectGet = handler => api.get.mockImplementation((path, ...args) => {
  if (typeof path === 'string' && path.endsWith('/task-action-capabilities')) {
    const id = path.split('/')[2];
    return Promise.resolve({ data: {
      schema: 'WILSY-PROJECT-TASK-ACTION-CAPABILITIES/V1',
      tenant_id: TENANT, principal_id: PRINCIPAL, project_id: id,
      can_start: true, can_complete: true, can_block: true,
      can_cancel: true, can_assign: true, can_edit: true,
    } });
  }
  return handler(path, ...args);
});

beforeEach(() => {
  vi.clearAllMocks();
  let keySequence = 0;
  vi.stubGlobal('crypto', { randomUUID: vi.fn(() => `stable-project-key-${++keySequence}`) });
  mockProjectGet(async (path) => {
    if (path === '/projects') return { data: list([]) };
    if (path === '/projects/summary') return { data: summary([]) };
    throw new Error(`Unexpected project GET ${path}`);
  });
});

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

describe('ProjectsWorkspace source-backed lifecycle', () => {

  it('renders one primary work action and a keyboard-dismissable contextual action sheet', () => {
    const onTransition = vi.fn();
    const onComplete = vi.fn();
    const onEdit = vi.fn();
    const onAttachments = vi.fn();
    const onApprovals = vi.fn();
    const onActivity = vi.fn();
    const item = { task_id: 'ptk-' + 'c'.repeat(48),
      title: 'Validate deliverable', status: 'TODO' };
    const handlers = { item, busy: false, onTransition, onComplete,
      onEdit, onAttachments, onApprovals, onActivity };
    const view = render(<ProjectWorkRowActions {...handlers}/>);
    expect(screen.getByRole('button', { name: 'Start: Validate deliverable' })).toBeVisible();
    expect(screen.queryByRole('menuitem', { name: 'Mark blocked' })).not.toBeInTheDocument();
    const trigger = screen.getByRole('button', { name: 'More actions for Validate deliverable' });
    fireEvent.click(trigger);
    const actionDialog = screen.getByRole('menu', { name: 'Actions for Validate deliverable' });
    expect(actionDialog).toBeVisible();
    expect(screen.getByRole('menuitem', { name: 'Mark blocked' })).toHaveFocus();
    fireEvent.keyDown(actionDialog, { key: 'ArrowDown' });
    expect(screen.getByRole('menuitem', { name: 'Assign' })).toHaveFocus();
    fireEvent.keyDown(actionDialog, { key: 'End' });
    expect(screen.getByRole('button', { name: 'Close actions' })).toHaveFocus();
    fireEvent.keyDown(actionDialog, { key: 'Home' });
    expect(screen.getByRole('menuitem', { name: 'Mark blocked' })).toHaveFocus();
    fireEvent.keyDown(window, { key: 'Escape' });
    expect(screen.queryByRole('menu', { name: 'Actions for Validate deliverable' })).not.toBeInTheDocument();
    expect(trigger).toHaveFocus();
    fireEvent.click(trigger);
    fireEvent.click(screen.getByRole('menuitem', { name: 'Mark blocked' }));
    expect(onTransition).toHaveBeenCalledWith(item, 'BLOCKED');
    expect(screen.queryByRole('menu', { name: 'Actions for Validate deliverable' })).not.toBeInTheDocument();
    view.rerender(<ProjectWorkRowActions {...handlers}
      item={{ ...item, status: 'IN_PROGRESS' }}/>);
    fireEvent.click(screen.getByRole('button', { name: 'Complete: Validate deliverable' }));
    expect(onComplete).toHaveBeenCalledWith({ ...item, status: 'IN_PROGRESS' });
    fireEvent.click(trigger);
    fireEvent.click(screen.getByRole('menuitem', { name: 'Cancel work' }));
    expect(onTransition).toHaveBeenCalledTimes(1);
    fireEvent.click(screen.getByRole('button', { name: 'Confirm cancellation' }));
    expect(onTransition).toHaveBeenCalledWith({ ...item, status: 'IN_PROGRESS' }, 'CANCELLED');
    expect(onComplete).toHaveBeenCalledTimes(1);
  });



  it('hides actions explicitly disallowed by the caller without changing authority', () => {
    const item = { task_id: 'ptk-' + 'f'.repeat(48),
      title: 'Read-only work', status: 'IN_PROGRESS' };
    const onTransition = vi.fn();
    render(<ProjectWorkRowActions item={item} busy={false}
      onTransition={onTransition} onComplete={vi.fn()} onEdit={vi.fn()}
      onAttachments={vi.fn()} onActivity={vi.fn()} onApprovals={vi.fn()}
      canStart={false} canComplete={false} canBlock={false}
      canCancel={false} canAssign={false} canEdit={false}
      canAttachments={false} canApprovals={false}/>);
    expect(screen.queryByRole('button', { name: 'Complete: Read-only work' }))
      .not.toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: 'More actions for Read-only work' }));
    const menu = screen.getByRole('menu', { name: 'Actions for Read-only work' });
    expect(within(menu).getByRole('menuitem', { name: 'Activity & discussion' }))
      .toBeVisible();
    expect(within(menu).queryByRole('menuitem', { name: 'Mark blocked' }))
      .not.toBeInTheDocument();
    expect(within(menu).queryByRole('menuitem', { name: 'Cancel work' }))
      .not.toBeInTheDocument();
    expect(within(menu).queryByRole('menuitem', { name: 'Edit' }))
      .not.toBeInTheDocument();
    expect(onTransition).not.toHaveBeenCalled();
  });

  it('dismisses the mobile work actions sheet without mutating work', () => {
    vi.stubGlobal('innerWidth', 390);
    const onTransition = vi.fn();
    const item = { task_id: 'ptk-' + 'd'.repeat(48),
      title: 'Mobile decision', status: 'IN_PROGRESS' };
    render(<ProjectWorkRowActions item={item} busy={false} onTransition={onTransition}
      onComplete={vi.fn()} onEdit={vi.fn()} onAttachments={vi.fn()}
      onApprovals={vi.fn()} onActivity={vi.fn()}/>);
    const trigger = screen.getByRole('button', { name: 'More actions for Mobile decision' });
    fireEvent.click(trigger);
    const dialog = screen.getByRole('dialog', { name: 'Actions for Mobile decision' });
    expect(dialog).toBeVisible();
    expect(document.body.style.overflow).toBe('hidden');
    const grabber = dialog.querySelector('.touch-pan-y');
    expect(grabber).not.toBeNull();
    fireEvent.touchStart(grabber, { touches: [{ clientY: 80 }] });
    fireEvent.touchEnd(grabber, { changedTouches: [{ clientY: 185 }] });
    expect(screen.queryByRole('dialog', { name: 'Actions for Mobile decision' }))
      .not.toBeInTheDocument();
    expect(trigger).toHaveFocus();
    expect(document.body.style.overflow).not.toBe('hidden');
    expect(onTransition).not.toHaveBeenCalled();
  });

  it('filters current-page project work to the exact current assignee without a write', async () => {
    const source = project();
    const base = {
      schema: 'wilsy.project.task.v1', tenant_id: TENANT, project_id: PROJECT_ID,
      kind: 'TASK', parent_task_id: null, description: '', status: 'TODO',
      due_date: null, depends_on: [], revision: 1, fingerprint: 'a'.repeat(128),
      created_by_principal_id: PRINCIPAL, updated_by_principal_id: PRINCIPAL,
      created_at: '2026-11-19T09:00:00+00:00',
      updated_at: '2026-11-19T09:00:00+00:00',
    };
    const mine = { ...base, task_id: 'ptk-' + 'a'.repeat(48),
      title: 'My accountable delivery', assignee_principal_id: PRINCIPAL };
    const someoneElse = { ...base, task_id: 'ptk-' + 'b'.repeat(48),
      title: 'Other contributor delivery', assignee_principal_id: 'other-principal' };
    mockProjectGet(async path => {
      if (path === '/projects') return { data: list([source]) };
      if (path === '/projects/summary') return { data: summary([source]) };
      if (path === `/projects/${PROJECT_ID}`) return { data: result(source) };
      if (path === `/projects/${PROJECT_ID}/tasks?limit=50&offset=0`) return {
        data: { schema: 'WILSY-PROJECT-TASK-LIST/V1', tenant_id: TENANT,
          principal_id: PRINCIPAL, project_id: PROJECT_ID, items: [mine, someoneElse],
          limit: 50, offset: 0, has_more: false, next_offset: null },
      };
      if (path === `/projects/${PROJECT_ID}/participants?limit=100&offset=0`) return {
        data: { schema: 'WILSY-PROJECT-PARTICIPANT-LIST/V1', tenant_id: TENANT,
          principal_id: PRINCIPAL, project_id: PROJECT_ID, items: [],
          limit: 100, offset: 0, has_more: false, next_offset: null },
      };
      throw new Error('Unexpected read in current-assignee certificate ' + path);
    });
    render(<ProjectsWorkspace tenantId={TENANT} principalId={PRINCIPAL}
      sessionScope="project-my-work-page-cert"/>);
    fireEvent.click(await screen.findByRole('button', { name: /View project Persisted roadmap/ }));
    const work = await screen.findByRole('region', { name: 'Verified project tasks' });
    const rows = [...work.querySelectorAll('tbody tr[data-task-id]')];
    expect(rows).toHaveLength(2);
    rows[0].focus();
    fireEvent.keyDown(rows[0], { key: 'j' });
    expect(rows[1]).toHaveFocus();
    fireEvent.keyDown(rows[1], { key: 'k' });
    expect(rows[0]).toHaveFocus();
    fireEvent.keyDown(rows[0], { key: 'c' });
    expect(screen.queryByRole('dialog', { name: 'Confirm verified task completion' }))
      .not.toBeInTheDocument();
    fireEvent.keyDown(rows[0], { key: 'a' });
    expect(screen.getByRole('dialog', { name: 'Assign work' })).toBeVisible();
    expect(screen.getByRole('combobox', { name: 'Reassign task' })).toBeVisible();
    expect(screen.queryByRole('textbox', { name: 'Edit task title' })).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: 'Cancel edit' }));
    fireEvent.click(screen.getByRole('button', { name: 'Reassign: My accountable delivery' }));
    expect(screen.getByRole('dialog', { name: 'Assign work' })).toBeVisible();
    expect(screen.getByRole('button', { name: 'Save assignment' })).toBeDisabled();
    fireEvent.click(screen.getByRole('button', { name: 'Cancel edit' }));
    expect(within(work).getByText('My accountable delivery')).toBeVisible();
    expect(within(work).getByText('Other contributor delivery')).toBeVisible();
    fireEvent.click(screen.getByRole('checkbox', { name: 'Select My accountable delivery' }));
    expect(screen.getByText(/1 work item selected on this verified page/)).toBeVisible();
    fireEvent.change(screen.getByRole('combobox', { name: 'Work row density' }), {
      target: { value: 'compact' },
    });
    expect(work.querySelector('tr[data-task-id]')).toHaveClass('h-11');
    fireEvent.click(screen.getByRole('checkbox', { name: 'Select all visible work' }));
    expect(screen.getByRole('checkbox', { name: 'Select Other contributor delivery' })).toBeChecked();
    expect(screen.getByText(/2 work items selected on this verified page/)).toBeVisible();
    fireEvent.click(screen.getByRole('checkbox', { name: 'Select all visible work' }));
    expect(screen.getByRole('checkbox', { name: 'Select My accountable delivery' })).not.toBeChecked();
    fireEvent.change(screen.getByRole('combobox', { name: 'Work row density' }), {
      target: { value: 'comfortable' },
    });
    expect(work.querySelector('tr[data-task-id]')).toHaveClass('h-14');
    fireEvent.click(screen.getByRole('button', { name: 'My work on this page' }));
    expect(within(work).getByText('My accountable delivery')).toBeVisible();
    expect(within(work).queryByText('Other contributor delivery')).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: 'All work on this page' }));
    expect(within(work).getByText('Other contributor delivery')).toBeVisible();
    expect(api.post).not.toHaveBeenCalled();
    expect(api.patch).not.toHaveBeenCalled();
  });

  it('filters authorized owned projects without calling participant IAM or changing records', async () => {
    const owned = project({
      project_id: PROJECT_ID, name: 'Owned platform programme',
      owner_principal_id: PRINCIPAL, status: 'active',
    });
    const another = project({
      project_id: 'prj-' + 'b'.repeat(48), name: 'Another team project',
      owner_principal_id: 'another-principal', code: 'OTHER',
    });
    mockProjectGet(async path => {
      if (path === '/projects') return { data: list([owned, another]) };
      if (path === '/projects?limit=100&offset=0&owned_by_me=true') {
        return { data: list([owned]) };
      }
      if (path === '/projects/summary') return { data: summary([owned, another]) };
      throw new Error('Owner filter requested an unapproved source: ' + path);
    });
    render(<ProjectsWorkspace tenantId={TENANT} principalId={PRINCIPAL}
      sessionScope="explicit-owner-responsibility"/>);
    expect(await screen.findByText('2 shown · 2 verified')).toBeVisible();
    expect(screen.getByText('Owned platform programme')).toBeVisible();
    expect(screen.getByText('Another team project')).toBeVisible();
    fireEvent.click(screen.getByRole('button', { name: 'My owned projects' }));
    expect(await screen.findByText(/1 shown · 1 verified · EOS owner-filtered page/)).toBeVisible();
    expect(screen.getByText('Owned platform programme')).toBeVisible();
    expect(screen.queryByText('Another team project')).not.toBeInTheDocument();
    expect(api.get.mock.calls.some(([path]) =>
      path === '/projects?limit=100&offset=0&owned_by_me=true')).toBe(true);
    expect(api.get.mock.calls.some(([path]) => path.includes('/my-projects'))).toBe(false);
    expect(api.post).not.toHaveBeenCalled();
    expect(api.patch).not.toHaveBeenCalled();
    fireEvent.click(screen.getByRole('button', { name: 'My owned projects' }));
    expect(await screen.findByText('Another team project')).toBeVisible();
  });


  it('opens participant-focused project execution without owner registry reads', async () => {
    mockProjectGet(async path => {
      if (path === '/projects/my-projects?limit=50&offset=0') return { data: {
        schema: 'WILSY-PROJECT-MY-PROJECTS/V1',
        tenant_id: TENANT, principal_id: PRINCIPAL,
        items: [], limit: 50, offset: 0, has_more: false, next_offset: null,
      } };
      throw new Error('Unexpected owner-only project read: ' + path);
    });
    render(<ProjectsWorkspace tenantId={TENANT} principalId={PRINCIPAL}
      sessionScope="participant-attention-focus"
      focusAssignedProjectId={PROJECT_ID}/>);
    expect(await screen.findByRole('heading', { name: 'My assigned projects' })).toBeVisible();
    await waitFor(() => expect(api.get).toHaveBeenCalledWith(
      '/projects/my-projects?limit=50&offset=0',
      expect.any(Object),
    ));
    expect(api.get.mock.calls.some(([path]) => path === '/projects' || path === '/projects/summary')).toBe(false);
  });


  it('navigates 125 source-backed tenant projects without truncating to the first 100', async () => {
    const rows = Array.from({ length: 125 }, (_, index) => project({
      project_id: `prj-${(index + 1).toString(16).padStart(48, '0')}`,
      name: `Tenant project ${index + 1}`,
      code: `TEN-${index + 1}`,
    }));
    mockProjectGet(async (path) => {
      if (path === '/projects') return { data: { ...list(rows.slice(0, 100)), has_more: true, next_offset: 100 } };
      if (path === '/projects?limit=100&offset=100') return {
        data: { ...list(rows.slice(100)), limit: 100, offset: 100, has_more: false, next_offset: null },
      };
      if (path === '/projects/summary') return { data: summary(rows) };
      throw new Error(`Unexpected project GET ${path}`);
    });
    render(<ProjectsWorkspace tenantId={TENANT} principalId={PRINCIPAL}
      sessionScope="tenant-paging-cert" />);
    expect(await screen.findByText('100 shown · 100 verified')).toBeVisible();
    expect(screen.getByText(/Portfolio breakdown ·/)).toBeVisible();
    fireEvent.click(screen.getByText(/Portfolio breakdown ·/));
    expect(screen.getByRole('region', { name: 'Verified project status distribution' })).toBeVisible();
    expect(screen.getByRole('img', { name: 'Planned: 125 of 125 projects' })).toBeVisible();
    fireEvent.click(screen.getByRole('button', { name: 'Next' }));
    expect(await screen.findByText('25 shown · 25 verified')).toBeVisible();
    expect(screen.getByRole('button', { name: 'Previous' })).toBeEnabled();
    expect(screen.getByRole('button', { name: 'Next' })).toBeDisabled();
    expect(screen.getByRole('button', { name: /Tenant project 125/ })).toBeVisible();
    expect(api.get.mock.calls.some(([path]) => path === '/projects?limit=100&offset=100')).toBe(true);
  });

  it('does not invent a next page when exactly 100 projects exist', async () => {
    const rows = Array.from({ length: 100 }, (_, index) => project({
      project_id: `prj-${(index + 1).toString(16).padStart(48, '0')}`,
      name: `Exact-page project ${index + 1}`,
    }));
    mockProjectGet(async (path) => {
      if (path === '/projects') return {
        data: { ...list(rows), has_more: false, next_offset: null },
      };
      if (path === '/projects/summary') return { data: summary(rows) };
      throw new Error(`Unexpected project GET ${path}`);
    });
    render(<ProjectsWorkspace tenantId={TENANT} principalId={PRINCIPAL}
      sessionScope="exact-page-boundary-cert" />);
    expect(await screen.findByText('100 shown · 100 verified')).toBeVisible();
    expect(screen.queryByRole('button', { name: 'Next' })).not.toBeInTheDocument();
    expect(api.get.mock.calls.some(([path]) => path.includes('offset=100'))).toBe(false);
  });

  it('filters project status across the tenant at EOS before paging', async () => {
    const planned = project({ name: 'Unfiltered planned project' });
    const active = project({
      project_id: `prj-${'b'.repeat(48)}`,
      name: 'Verified active project',
      status: 'active',
    });
    mockProjectGet(async (path) => {
      if (path === '/projects') return {
        data: { ...list([planned, active]), has_more: false, next_offset: null },
      };
      if (path === '/projects?limit=100&offset=0&project_status=active') return {
        data: { ...list([active]), has_more: false, next_offset: null },
      };
      if (path === '/projects/summary') return { data: summary([planned, active]) };
      throw new Error(`Unexpected project GET ${path}`);
    });
    render(<ProjectsWorkspace tenantId={TENANT} principalId={PRINCIPAL}
      sessionScope="tenant-status-filter-cert" />);
    expect(await screen.findByText('2 shown · 2 verified')).toBeVisible();
    fireEvent.change(screen.getByRole('combobox', { name: 'Filter by status' }), {
      target: { value: 'active' },
    });
    expect(await screen.findByText('1 shown · 1 verified')).toBeVisible();
    expect(screen.getByRole('button', { name: /Verified active project/ })).toBeVisible();
    expect(screen.queryByRole('button', { name: /Unfiltered planned project/ })).not.toBeInTheDocument();
    expect(api.get.mock.calls.some(([path]) => path === '/projects?limit=100&offset=0&project_status=active')).toBe(true);
  });

  it('creates, transitions and edits source-backed project tasks without activating the project', async () => {
    const persisted = project();
    const taskId = `ptk-${'b'.repeat(48)}`;
    const originalTask = {
      schema: 'wilsy.project.task.v1', tenant_id: TENANT,
      project_id: PROJECT_ID, task_id: taskId, kind: 'TASK',
      parent_task_id: null, title: 'Build milestone execution', description: '',
      status: 'TODO', assignee_principal_id: null, due_date: null,
      depends_on: [], created_by_principal_id: PRINCIPAL,
      updated_by_principal_id: PRINCIPAL,
      created_at: '2026-11-18T06:00:00+00:00',
      updated_at: '2026-11-18T06:00:00+00:00',
      revision: 1, fingerprint: 'a'.repeat(128),
    };
    let work = [];
    let commands = 0;
    mockProjectGet(async path => {
      if (path === '/projects') return { data: list([persisted]) };
      if (path === '/projects/summary') return { data: summary([persisted]) };
      if (path === `/projects/${PROJECT_ID}`) return { data: result(persisted) };
      if (path === `/projects/${PROJECT_ID}/tasks?limit=50&offset=0`) return {
        data: {
          schema: 'WILSY-PROJECT-TASK-LIST/V1', tenant_id: TENANT,
          principal_id: PRINCIPAL, project_id: PROJECT_ID,
          limit: 50, offset: 0, items: work, has_more: false, next_offset: null,
        },
      };
      if (path === `/projects/${PROJECT_ID}/participants?limit=100&offset=0`) return {
        data: {
          schema: 'WILSY-PROJECT-PARTICIPANT-LIST/V1', tenant_id: TENANT,
          principal_id: PRINCIPAL, project_id: PROJECT_ID,
          limit: 100, offset: 0, items: [], has_more: false, next_offset: null,
        },
      };
      throw new Error('Unexpected source GET ' + path);
    });
    api.post.mockImplementation(async (path, body, options) => {
      expect(options.headers['X-Tenant-ID']).toBe(TENANT);
      expect(options.headers['Idempotency-Key']).toBeTruthy();
      commands += 1;
      if (commands === 1) {
        expect(path).toBe(`/projects/${PROJECT_ID}/tasks`);
        expect(body).toEqual({
          kind: 'TASK', title: 'Build milestone execution',
          description: '', due_date: null, assignee_principal_id: null,
          parent_task_id: null, depends_on: [],
        });
        work = [originalTask];
      } else {
        expect(path).toBe(`/projects/${PROJECT_ID}/tasks/${taskId}/transition`);
        expect(body).toEqual({ expected_revision: 1, status: 'IN_PROGRESS' });
        work = [{
          ...originalTask, status: 'IN_PROGRESS', revision: 2,
          fingerprint: 'b'.repeat(128),
        }];
      }
      return { data: {
        schema: 'WILSY-PROJECT-TASK-RESULT/V1',
        tenant_id: TENANT, principal_id: PRINCIPAL,
        project_id: PROJECT_ID, task: work[0],
      } };
    });
    api.patch.mockImplementationOnce(async (path, body, options) => {
      expect(path).toBe(`/projects/${PROJECT_ID}/tasks/${taskId}`);
      expect(options.headers['X-Tenant-ID']).toBe(TENANT);
      expect(options.headers['Idempotency-Key']).toBeTruthy();
      expect(body).toEqual({
        expected_revision: 2, title: 'Updated task handoff',
        description: '', due_date: null, assignee_principal_id: null,
      });
      work = [{
        ...work[0], title: 'Updated task handoff', revision: 3,
        fingerprint: 'c'.repeat(128),
      }];
      return { data: {
        schema: 'WILSY-PROJECT-TASK-RESULT/V1',
        tenant_id: TENANT, principal_id: PRINCIPAL,
        project_id: PROJECT_ID, task: work[0],
      } };
    });
    render(<ProjectsWorkspace tenantId={TENANT} principalId={PRINCIPAL}
      sessionScope="task-source-readback-cert" />);
    fireEvent.click(await screen.findByRole('button', { name: /View project Persisted roadmap/ }));
    const panel = await screen.findByRole('region', { name: 'Project work execution' });
    expect(panel).toBeVisible();
    fireEvent.click(await screen.findByRole('button', { name: 'Create task' }));
    fireEvent.change(screen.getByPlaceholderText('Deliverable and action'), {
      target: { value: 'Build milestone execution' },
    });
    fireEvent.click(screen.getByRole('button', { name: 'Save work to EOS' }));
    await waitFor(() => expect(screen.getByText('Build milestone execution', {
      selector: '.wp-project-tasks tbody td span',
    })).toBeVisible());
    const row = screen.getByText('Build milestone execution', {
      selector: '.wp-project-tasks tbody td span',
    }).closest('tr');
    expect(row).toHaveAttribute('data-task-id', taskId);
    row.focus();
    fireEvent.keyDown(row, { key: 'Enter' });
    expect(screen.getByRole('dialog', { name: 'Work details: Build milestone execution' }))
      .toBeVisible();
    fireEvent.click(screen.getByRole('button', { name: 'Close work details' }));
    expect(row).toHaveFocus();

    fireEvent.click(screen.getByText(/View lifecycle breakdown · 1 work items on this page/));
    expect(screen.getByText('Work lifecycle · current page')).toBeVisible();
    expect(screen.getByRole('button', { name: /Filter work to To do: 1 of 1 verified on page/ })).toBeVisible();
    const startWork = within(row).getByRole('button', { name: 'Start: Build milestone execution' });
    await waitFor(() => expect(startWork).toBeEnabled());
    fireEvent.click(startWork);
    await waitFor(() => expect(
      screen.getByRole('row', { name: /Build milestone execution/ }),
    ).toHaveTextContent('In progress'));
    const lifecycle = document.querySelector('[aria-label="Verified task lifecycle chart"]');
    if (!lifecycle.open) fireEvent.click(lifecycle.querySelector('summary'));
    expect(screen.getByRole('button', { name: /Filter work to In progress: 1 of 1 verified on page/ })).toBeVisible();
    fireEvent.click(screen.getByRole('button', { name: /Filter work to To do: 0 of 1 verified on page/ }));
    expect(screen.getByText(/No work items on this verified page match/)).toBeVisible();
    fireEvent.click(screen.getByRole('button', { name: /Filter work to To do: 0 of 1 verified on page/ }));
    expect(screen.getByText('Build milestone execution', {
      selector: '.wp-project-tasks tbody td span',
    })).toBeVisible();
    expect(commands).toBe(2);
    const reconciledRow = screen.getByRole('row', { name: /Build milestone execution/ });
    const actionTrigger = within(reconciledRow).getByRole('button', {
      name: 'More actions for Build milestone execution',
    });
    await waitFor(() => expect(actionTrigger).toBeEnabled());
    fireEvent.click(actionTrigger);
    fireEvent.click(within(screen.getByRole('menu', {
       name: 'Actions for Build milestone execution',
     })).getByRole('menuitem', { name: 'Edit' }));
    fireEvent.change(screen.getByRole('textbox', { name: 'Edit task title' }), {
      target: { value: 'Updated task handoff' },
    });
    fireEvent.click(screen.getByRole('button', { name: 'Save changes to EOS' }));
    await waitFor(() => expect(screen.getByText('Updated task handoff', {
      selector: '.wp-project-tasks tbody td span',
    })).toBeVisible());
    expect(api.patch).toHaveBeenCalledTimes(1);
    expect(persisted.status).toBe('planned');
  });

  it('ticks a persisted To-do checkbox only after confirmed EOS transition and fresh readback', async () => {
    const persisted = project();
    const taskId = 'ptk-' + 'e'.repeat(48);
    const activeTask = {
      schema: 'wilsy.project.task.v1', tenant_id: TENANT, project_id: PROJECT_ID,
      task_id: taskId, kind: 'TASK', parent_task_id: null,
      title: 'Evidence-backed operational acceptance', description: '',
      status: 'IN_PROGRESS', assignee_principal_id: null, due_date: null,
      depends_on: [], created_by_principal_id: PRINCIPAL,
      updated_by_principal_id: PRINCIPAL, revision: 2,
      created_at: '2026-11-18T06:00:00+00:00',
      updated_at: '2026-11-18T06:00:00+00:00', fingerprint: 'a'.repeat(128),
    };
    const completedTask = {
      ...activeTask, status: 'DONE', revision: 3, fingerprint: 'b'.repeat(128),
    };
    let readCount = 0;
    let releaseReadback;
    const pendingReadback = new Promise(resolve => { releaseReadback = resolve; });
    const taskList = item => ({ data: {
      schema: 'WILSY-PROJECT-TASK-LIST/V1', tenant_id: TENANT,
      principal_id: PRINCIPAL, project_id: PROJECT_ID,
      limit: 50, offset: 0, items: [item], has_more: false, next_offset: null,
    } });
    mockProjectGet(async path => {
      if (path === '/projects') return { data: list([persisted]) };
      if (path === '/projects/summary') return { data: summary([persisted]) };
      if (path === `/projects/${PROJECT_ID}`) return { data: result(persisted) };
      if (path === `/projects/${PROJECT_ID}/tasks?limit=50&offset=0`) {
        readCount += 1;
        return readCount === 1 ? taskList(activeTask) : pendingReadback;
      }
      if (path === `/projects/${PROJECT_ID}/participants?limit=100&offset=0`) return { data: {
        schema: 'WILSY-PROJECT-PARTICIPANT-LIST/V1', tenant_id: TENANT,
        principal_id: PRINCIPAL, project_id: PROJECT_ID,
        limit: 100, offset: 0, items: [], has_more: false, next_offset: null,
      } };
      throw new Error('Unexpected project read ' + path);
    });
    api.post.mockImplementationOnce(async (path, body, options) => {
      expect(path).toBe(`/projects/${PROJECT_ID}/tasks/${taskId}/transition`);
      expect(body).toEqual({ expected_revision: 2, status: 'DONE' });
      expect(options.headers['X-Tenant-ID']).toBe(TENANT);
      expect(options.headers['Idempotency-Key']).toBeTruthy();
      return { data: {
        schema: 'WILSY-PROJECT-TASK-RESULT/V1',
        tenant_id: TENANT, principal_id: PRINCIPAL,
        project_id: PROJECT_ID, task: completedTask,
      } };
    });
    render(<ProjectsWorkspace tenantId={TENANT} principalId={PRINCIPAL}
      sessionScope="source-checklist-readback-cert"/>);
    fireEvent.click(await screen.findByRole('button', { name: /View project Persisted roadmap/ }));
    fireEvent.click(await screen.findByText(/Checklist mode · 0\/1 completed/));
    const checkbox = await screen.findByRole('checkbox', {
      name: 'Mark completed: Evidence-backed operational acceptance',
    });
    expect(checkbox).not.toBeChecked();
    expect(screen.getByText('To-do checklist · current verified page')).toBeVisible();
    fireEvent.click(checkbox);
    expect(screen.getByRole('dialog', { name: 'Confirm verified task completion' })).toBeVisible();
    expect(api.post).not.toHaveBeenCalled();
    const confirm = screen.getByRole('button', { name: 'Confirm Done in EOS' });
    expect(confirm).toBeDisabled();
    fireEvent.click(screen.getByRole('checkbox', {
      name: /I reviewed this task's acceptance and supporting evidence/,
    }));
    expect(confirm).toBeEnabled();
    fireEvent.click(confirm);
    await waitFor(() => expect(api.post).toHaveBeenCalledTimes(1));
    await waitFor(() => expect(readCount).toBe(2));
    expect(checkbox).not.toBeChecked();
    expect(screen.getByText('Updating to Done…')).toBeVisible();
    await act(async () => { releaseReadback(taskList(completedTask)); });
    await waitFor(() => expect(screen.queryByText('Updating to Done…')).not.toBeInTheDocument());
    expect(await screen.findByRole('checkbox', {
      name: 'Mark completed: Evidence-backed operational acceptance',
    })).toBeChecked();
    const checklist = document.querySelector('[aria-label="EOS verified To-do checklist"]');
    if (!checklist.open) fireEvent.click(checklist.querySelector('summary'));
    expect(screen.getByText('1 of 1 completed')).toBeVisible();
    expect(screen.queryByRole('group', { name: 'Confirm verified task completion' }))
      .not.toBeInTheDocument();
  });

  it('opens project Discussions from top navigation and reads the selected milestone without work dashboard', async () => {
    const persisted = project();
    const taskId = 'ptk-' + 'f'.repeat(48);
    const entry = {
      schema: 'wilsy.project.task.v1', tenant_id: TENANT, project_id: PROJECT_ID,
      task_id: taskId, kind: 'TASK', parent_task_id: null,
      title: 'Current project delivery', description: '',
      status: 'TODO', assignee_principal_id: null, due_date: null,
      depends_on: [], created_by_principal_id: PRINCIPAL,
      updated_by_principal_id: PRINCIPAL, revision: 1,
      created_at: '2026-11-18T06:00:00+00:00',
      updated_at: '2026-11-18T06:00:00+00:00', fingerprint: 'a'.repeat(128),
    };
    mockProjectGet(async path => {
      if (path === '/projects') return { data: list([persisted]) };
      if (path === '/projects/summary') return { data: summary([persisted]) };
      if (path === `/projects/${PROJECT_ID}`) return { data: result(persisted) };
      if (path === `/projects/${PROJECT_ID}/tasks?limit=50&offset=0`) return { data: {
        schema: 'WILSY-PROJECT-TASK-LIST/V1', tenant_id: TENANT,
        principal_id: PRINCIPAL, project_id: PROJECT_ID,
        items: [entry], limit: 50, offset: 0, has_more: false, next_offset: null,
      } };
      if (path === `/projects/${PROJECT_ID}/participants?limit=100&offset=0`) return { data: {
        schema: 'WILSY-PROJECT-PARTICIPANT-LIST/V1', tenant_id: TENANT,
        principal_id: PRINCIPAL, project_id: PROJECT_ID,
        items: [], limit: 100, offset: 0, has_more: false, next_offset: null,
      } };
      if (path === `/projects/${PROJECT_ID}/tasks/${taskId}/comments?limit=50&offset=0`) return { data: {
        schema: 'WILSY-PROJECT-COMMENT-LIST/V1', tenant_id: TENANT,
        principal_id: PRINCIPAL, project_id: PROJECT_ID, task_id: taskId,
        items: [{
          schema: 'wilsy.project.comment.v1', tenant_id: TENANT,
          project_id: PROJECT_ID, task_id: taskId, comment_id: 'pcm-' + 'a'.repeat(48),
          author_principal_id: PRINCIPAL, body: '**Recent progress**',
          mentions: [], fingerprint: 'b'.repeat(128),
          created_at: '2026-11-19T09:00:00+00:00',
        }], limit: 50, offset: 0, has_more: false, next_offset: null,
      } };
      if (path === `/projects/${PROJECT_ID}/tasks/${taskId}/events?limit=50&offset=0`) return { data: {
        schema: 'WILSY-PROJECT-TASK-EVENT-LIST/V1', tenant_id: TENANT,
        principal_id: PRINCIPAL, project_id: PROJECT_ID, task_id: taskId,
        items: [{
          schema: 'wilsy.project.task.event.v1', tenant_id: TENANT,
          project_id: PROJECT_ID, task_id: taskId, revision: 1,
          event_type: 'PROJECT_TASK_CREATED', actor_principal_id: PRINCIPAL,
          status_after: 'TODO', occurred_at: '2026-11-18T06:00:00+00:00',
        }], limit: 50, offset: 0, has_more: false, next_offset: null,
      } };
      if (path === `/projects/${PROJECT_ID}/tasks/${taskId}/approvals?limit=50&offset=0`) return { data: {
        schema: 'WILSY-PROJECT-APPROVAL-LIST/V1', tenant_id: TENANT,
        principal_id: PRINCIPAL, project_id: PROJECT_ID, task_id: taskId,
        items: [{
          schema: 'wilsy.project.approval.v1', tenant_id: TENANT,
          project_id: PROJECT_ID, task_id: taskId, approval_id: 'par-' + 'c'.repeat(48),
          requester_principal_id: PRINCIPAL, reviewer_principal_id: 'reviewer-a',
          rationale: 'Approve delivery evidence', status: 'APPROVED',
          requested_at: '2026-11-19T08:00:00+00:00',
          decided_at: '2026-11-19T10:00:00+00:00',
          decision_rationale: 'Reviewed and accepted', revision: 2,
          fingerprint: 'c'.repeat(128),
        }], limit: 50, offset: 0, has_more: false, next_offset: null,
      } };
      if (path === `/projects/${PROJECT_ID}/tasks/${taskId}/attachments?limit=50&offset=0`) return { data: {
        schema: 'WILSY-PROJECT-ATTACHMENT-LIST/V1', tenant_id: TENANT,
        principal_id: PRINCIPAL, project_id: PROJECT_ID, task_id: taskId,
        items: [{
          schema: 'wilsy.project.attachment.v1', tenant_id: TENANT,
          project_id: PROJECT_ID, task_id: taskId, attachment_id: 'pat-' + 'd'.repeat(48),
          filename: 'evidence.pdf', uploader_principal_id: PRINCIPAL,
          media_type: 'application/pdf', size_bytes: 1200,
          content_sha3_512: 'a'.repeat(128), fingerprint: 'd'.repeat(128),
          state: 'QUARANTINED', revision: 1,
          scan_clearance_fingerprint: 'f'.repeat(128),
          created_at: '2026-11-19T11:00:00+00:00',
          scan_clearance_status: 'SCAN_CLEAN_VERIFIED',
        }], limit: 50, offset: 0, has_more: false, next_offset: null,
      } };
      throw new Error('Unexpected project GET ' + path);
    });
    render(<ProjectsWorkspace tenantId={TENANT} principalId={PRINCIPAL}
      sessionScope="top-level-discussions-cert"/>);
    fireEvent.click(await screen.findByRole('button', { name: /View project Persisted roadmap/ }));
    fireEvent.click(within(screen.getByRole('navigation', { name: 'Project workspace views' }))
      .getByRole('button', { name: 'Activity & discussion' }));
    expect(await screen.findByRole('region', { name: 'Project discussions workspace' })).toBeVisible();
    expect(screen.queryByRole('region', { name: 'Verified task lifecycle chart' })).not.toBeInTheDocument();
    expect(screen.queryByRole('region', { name: 'EOS verified To-do checklist' })).not.toBeInTheDocument();
    const options = await screen.findByRole('list', { name: 'Verified discussion work items' });
    fireEvent.click(within(options).getByRole('button', { name: /Current project delivery/ }));
    expect(await screen.findByRole('region', { name: 'Activity & discussion' })).toBeVisible();
    expect(screen.getByRole('button', { name: 'Write update' })).toHaveAttribute('aria-expanded', 'false');
    expect(document.querySelector('[aria-label="Verified task activity history"]')).toBeVisible();
    expect(await screen.findByText('Work created')).toBeVisible();
    expect(await screen.findByText('Evidence attached')).toBeVisible();
    expect(screen.getByText('Recent progress')).toBeVisible();
    const history = document.querySelector('[aria-label="Verified task activity history"]');
    await waitFor(() => expect(history.querySelectorAll('li')).toHaveLength(5));
    const entries = [...history.querySelectorAll('li')];
    expect(entries.map(item => item.textContent)).toEqual([
      expect.stringContaining('Evidence attached'),
      expect.stringContaining('Decision · approved'),
      expect.stringContaining('Recent progress'),
      expect.stringContaining('Approval requested'),
      expect.stringContaining('Work created'),
    ]);
    expect(screen.getAllByRole('button', { name: 'Open governed decision' })).toHaveLength(2);
    expect(screen.getByRole('button', { name: 'Open governed attachment' })).toBeVisible();
    expect(screen.getByText(/revision 1/)).toBeVisible();
    fireEvent.click(screen.getByRole('button', { name: 'All discussions' }));
    expect(await screen.findByRole('list', { name: 'Verified discussion work items' })).toBeVisible();
  });

  it('opens a focused EOS task discussion with composer before the history and restores the queue', async () => {
    const persisted = project();
    const taskId = 'ptk-' + 'f'.repeat(48);
    const entry = {
      schema: 'wilsy.project.task.v1', tenant_id: TENANT, project_id: PROJECT_ID,
      task_id: taskId, kind: 'TASK', parent_task_id: null,
      title: 'Current project delivery', description: '',
      status: 'TODO', assignee_principal_id: null, due_date: null,
      depends_on: [], created_by_principal_id: PRINCIPAL,
      updated_by_principal_id: PRINCIPAL, revision: 1,
      created_at: '2026-11-18T06:00:00+00:00',
      updated_at: '2026-11-18T06:00:00+00:00', fingerprint: 'a'.repeat(128),
    };
    mockProjectGet(async path => {
      if (path === '/projects') return { data: list([persisted]) };
      if (path === '/projects/summary') return { data: summary([persisted]) };
      if (path === `/projects/${PROJECT_ID}`) return { data: result(persisted) };
      if (path === `/projects/${PROJECT_ID}/tasks?limit=50&offset=0`) return { data: {
        schema: 'WILSY-PROJECT-TASK-LIST/V1', tenant_id: TENANT,
        principal_id: PRINCIPAL, project_id: PROJECT_ID,
        items: [entry], limit: 50, offset: 0, has_more: false, next_offset: null,
      } };
      if (path === `/projects/${PROJECT_ID}/participants?limit=100&offset=0`) return { data: {
        schema: 'WILSY-PROJECT-PARTICIPANT-LIST/V1', tenant_id: TENANT,
        principal_id: PRINCIPAL, project_id: PROJECT_ID,
        items: [], limit: 100, offset: 0, has_more: false, next_offset: null,
      } };
      if (path === `/projects/${PROJECT_ID}/tasks/${taskId}/comments?limit=50&offset=0`) return { data: {
        schema: 'WILSY-PROJECT-COMMENT-LIST/V1', tenant_id: TENANT,
        principal_id: PRINCIPAL, project_id: PROJECT_ID, task_id: taskId,
        items: [], limit: 50, offset: 0, has_more: false, next_offset: null,
      } };
      throw new Error('Unexpected project GET ' + path);
    });
    render(<ProjectsWorkspace tenantId={TENANT} principalId={PRINCIPAL}
      sessionScope="focused-discussion-cert"/>);
    fireEvent.click(await screen.findByRole('button', { name: /View project Persisted roadmap/ }));
    await screen.findByText('Current project delivery', { selector: '.wp-project-tasks tbody td span' });
    fireEvent.click(within(screen.getByRole('row', { name: /Current project delivery/ }))
      .getByRole('button', { name: /More actions for Current project delivery/ }));
    fireEvent.click(within(screen.getByRole('menu', {
       name: 'Actions for Current project delivery',
     })).getByRole('menuitem', { name: 'Activity & discussion' }));
    expect(await screen.findByRole('region', { name: 'Activity & discussion' })).toBeVisible();
    expect(screen.getByRole('button', { name: 'Back to work queue' })).toBeVisible();
    expect(screen.queryByRole('region', { name: 'Verified project tasks' })).not.toBeInTheDocument();
    expect(screen.queryByRole('region', { name: 'Verified task lifecycle chart' })).not.toBeInTheDocument();
    const discussion = screen.getByRole('region', { name: 'Activity & discussion' });
    expect(screen.getByRole('button', { name: 'Write update' }))
      .toHaveAttribute('aria-expanded', 'false');
    expect(discussion.querySelector('[aria-label="Verified task activity history"]'))
      .toBeInTheDocument();
    expect(discussion.querySelector('textarea[aria-label="New task comment"]'))
      .not.toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: 'Write update' }));
    expect(screen.getByRole('button', { name: 'Close editor' }))
      .toHaveAttribute('aria-expanded', 'true');
    expect(discussion.querySelector('textarea[aria-label="New task comment"]')).toBeVisible();
    const draft = '**Development progress — 19 November 2026**\\n\\n- Source readback verified\\n- Pending mobile acceptance\\n\\n<script>alert(1)</script>'.replaceAll('\\n','\n');
    fireEvent.change(screen.getByRole('textbox', { name: 'New task comment' }), {
      target: { value: draft },
    });
    const preview = screen.getByRole('region', { name: 'Live formatted comment preview' });
    expect(preview.querySelector('strong')).toHaveTextContent('Development progress — 19 November 2026');
    expect(preview.querySelectorAll('li')).toHaveLength(2);
    expect(preview).toHaveTextContent('<script>alert(1)</script>');
    expect(preview.querySelector('script')).not.toBeInTheDocument();
    expect(screen.getByRole('textbox', { name: 'New task comment' })).toHaveValue(draft);
    expect(discussion.querySelector('textarea').compareDocumentPosition(
      discussion.querySelector('[aria-label="Verified task activity history"] ul'),
    ) & Node.DOCUMENT_POSITION_PRECEDING).toBeTruthy();
    fireEvent.click(screen.getByRole('button', { name: 'Close editor' }));
    expect(discussion.querySelector('textarea')).not.toBeInTheDocument();
    expect(discussion.querySelector('[aria-label="Verified task activity history"]'))
      .toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: 'Back to work queue' }));
    expect(screen.getByRole('region', { name: 'Verified project tasks' })).toBeVisible();
  });

  it('labels eligible exact-tenant participants using sourced names, not opaque IDs', async () => {
    const persisted = project();
    const memberId = 'employee-' + 'b'.repeat(24);
    const namelessId = 'employee-' + 'c'.repeat(24);
    mockProjectGet(async path => {
      if (path === '/projects') return { data: list([persisted]) };
      if (path === '/projects/summary') return { data: summary([persisted]) };
      if (path === `/projects/${PROJECT_ID}`) return { data: result(persisted) };
      if (path === `/projects/${PROJECT_ID}/participants?limit=50&offset=0`) return { data: {
        schema: 'WILSY-PROJECT-PARTICIPANT-LIST/V1', tenant_id: TENANT,
        principal_id: PRINCIPAL, project_id: PROJECT_ID,
        items: [], limit: 50, offset: 0, has_more: false, next_offset: null,
      } };
      if (path === `/projects/${PROJECT_ID}/participant-options?limit=50&offset=0`) return { data: {
        schema: 'WILSY-PROJECT-PARTICIPANT-OPTIONS/V1', tenant_id: TENANT,
        principal_id: PRINCIPAL, project_id: PROJECT_ID,
        items: [
          { principal_id: memberId, first_name: 'Alex', last_name: 'Mokoena' },
          { principal_id: namelessId, first_name: null, last_name: null },
        ], limit: 50, offset: 0, has_more: false, next_offset: null,
      } };
      throw new Error('Unexpected GET ' + path);
    });
    render(<ProjectsWorkspace tenantId={TENANT} principalId={PRINCIPAL}
      sessionScope="verified-member-names-cert"/>);
    fireEvent.click(await screen.findByRole('button', { name: /View project Persisted roadmap/ }));
    fireEvent.click(screen.getByRole('button', { name: 'People' }));
    const option = await screen.findByRole('option', { name: 'Alex Mokoena' });
    expect(option).toHaveValue(memberId);
    expect(screen.getByRole('option', { name: 'Verified member — name unavailable' }))
      .toHaveValue(namelessId);
    fireEvent.change(screen.getByRole('combobox', { name: 'Eligible participant' }),
      { target: { value: memberId } });
    expect(screen.getByText('Source principal: ' + memberId)).toBeVisible();
  });

  it('operates real task, subtask and milestone commands from the verified work queue', async () => {
    const persisted = project();
    const parentId = 'ptk-' + 'b'.repeat(48);
    const childId = 'ptk-' + 'c'.repeat(48);
    const milestoneId = 'ptk-' + 'd'.repeat(48);
    const base = {
      schema: 'wilsy.project.task.v1', tenant_id: TENANT, project_id: PROJECT_ID,
      description: '', status: 'TODO', assignee_principal_id: null, due_date: null,
      depends_on: [], created_by_principal_id: PRINCIPAL, updated_by_principal_id: PRINCIPAL,
      created_at: '2026-11-18T06:00:00+00:00', updated_at: '2026-11-18T06:00:00+00:00',
      revision: 1, fingerprint: 'a'.repeat(128),
    };
    const parent = { ...base, task_id: parentId, kind: 'TASK',
      parent_task_id: null, title: 'Main delivery' };
    const child = { ...base, task_id: childId, kind: 'TASK',
      parent_task_id: parentId, title: 'Draft deliverable' };
    const milestone = { ...base, task_id: milestoneId, kind: 'MILESTONE',
      parent_task_id: null, title: 'Sign-off checkpoint' };
    let rows = [parent];
    mockProjectGet(async path => {
      if (path === '/projects') return { data: list([persisted]) };
      if (path === '/projects/summary') return { data: summary([persisted]) };
      if (path === `/projects/${PROJECT_ID}`) return { data: result(persisted) };
      if (path === `/projects/${PROJECT_ID}/tasks?limit=50&offset=0`) return { data: {
        schema: 'WILSY-PROJECT-TASK-LIST/V1', tenant_id: TENANT,
        principal_id: PRINCIPAL, project_id: PROJECT_ID, limit: 50, offset: 0,
        items: rows, has_more: false, next_offset: null,
      } };
      if (path === `/projects/${PROJECT_ID}/participants?limit=100&offset=0`) return { data: {
        schema: 'WILSY-PROJECT-PARTICIPANT-LIST/V1', tenant_id: TENANT,
        principal_id: PRINCIPAL, project_id: PROJECT_ID, limit: 100, offset: 0,
        items: [], has_more: false, next_offset: null,
      } };
      throw new Error('Unexpected GET ' + path);
    });
    api.post.mockImplementation(async (path, body, options) => {
      expect(path).toBe(`/projects/${PROJECT_ID}/tasks`);
      expect(options.headers['X-Tenant-ID']).toBe(TENANT);
      expect(options.headers['Idempotency-Key']).toBeTruthy();
      if (body.kind === 'TASK') {
        expect(body).toMatchObject({ title: 'Draft deliverable',
          parent_task_id: parentId, kind: 'TASK' });
        rows = [parent, child];
      } else {
        expect(body).toMatchObject({ title: 'Sign-off checkpoint',
          parent_task_id: null, kind: 'MILESTONE' });
        rows = [parent, child, milestone];
      }
      return { data: { schema: 'WILSY-PROJECT-TASK-RESULT/V1',
        tenant_id: TENANT, principal_id: PRINCIPAL, project_id: PROJECT_ID,
        task: body.kind === 'TASK' ? child : milestone } };
    });
    render(<ProjectsWorkspace tenantId={TENANT} principalId={PRINCIPAL}
      sessionScope="operational-work-queue-cert"/>);
    fireEvent.click(await screen.findByRole('button', { name: /View project Persisted roadmap/ }));
    await screen.findByRole('region', { name: 'Project work execution' });
    expect(await screen.findByText('Main delivery', {
      selector: '.wp-project-tasks tbody td span',
    })).toBeVisible();
    fireEvent.click(await screen.findByText(/Checklist mode ·/));
    fireEvent.click(screen.getByRole('button', { name: 'Add checklist step to Main delivery' }));
    expect(screen.getByRole('combobox', { name: 'Work type' })).toHaveValue('SUBTASK');
    expect(screen.getByRole('combobox', { name: 'Parent task' })).toHaveValue(parentId);
    expect(screen.getByRole('button', { name: 'Save work to EOS' })).toBeDisabled();
    fireEvent.change(screen.getByPlaceholderText('Deliverable and action'), {
      target: { value: 'Draft deliverable' },
    });
    fireEvent.click(screen.getByRole('button', { name: 'Save work to EOS' }));
    await waitFor(() => expect(screen.getByRole('row', { name: /Draft deliverable/ })).toBeVisible());
    fireEvent.change(screen.getByRole('combobox', { name: 'Filter work type' }), {
      target: { value: 'SUBTASK' },
    });
    expect(screen.getByText(/1 shown \/ 2 verified on page 1\./)).toBeVisible();
    expect(screen.queryByText('Main delivery', {
      selector: '.wp-project-tasks tbody td span',
    })).not.toBeInTheDocument();
    fireEvent.change(screen.getByRole('combobox', { name: 'Filter work type' }), {
      target: { value: 'ALL' },
    });
    fireEvent.click(screen.getByRole('button', { name: 'Create task' }));
    fireEvent.change(screen.getByRole('combobox', { name: 'Work type' }), {
      target: { value: 'MILESTONE' },
    });
    fireEvent.change(screen.getByPlaceholderText('Deliverable and action'), {
      target: { value: 'Sign-off checkpoint' },
    });
    fireEvent.click(screen.getByRole('button', { name: 'Save work to EOS' }));
    await waitFor(() => expect(screen.getByText('Sign-off checkpoint', {
      selector: '.wp-project-tasks tbody td span',
    })).toBeVisible());
    expect(api.post).toHaveBeenCalledTimes(2);
    expect(persisted.status).toBe('planned');
  });

  it('keeps automatic hexadecimal IDs out of the operating project list and header', async () => {
    const generated = 'PRJ-' + 'A'.repeat(16);
    const source = project({ name: 'Human-readable delivery', code: generated });
    mockProjectGet(async path => {
      if (path === '/projects') return { data: list([source]) };
      if (path === '/projects/summary') return { data: summary([source]) };
      if (path === `/projects/${PROJECT_ID}`) return { data: result(source) };
      throw new Error('Unexpected source in project identity presentation test: ' + path);
    });
    render(<ProjectsWorkspace tenantId={TENANT} principalId={PRINCIPAL}
      sessionScope="no-opaque-operating-identity-cert"/>);
    expect(await screen.findByRole('button', {
      name: /View project Human-readable delivery/,
    })).toBeVisible();
    expect(screen.getByText('Automatically assigned')).toBeVisible();
    expect(screen.queryByText(generated)).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: /View project Human-readable delivery/ }));
    expect(await screen.findByText('Code assigned')).toBeVisible();
    expect(screen.queryByText(generated)).not.toBeInTheDocument();
  });

  it('materialises one selected verified industry template only after EOS confirms the project', async () => {
    const persisted = project({ name: 'Legal litigation delivery' });
    const steps = [
      { id: 'first', kind: 'TASK', title: 'Open matter', role: 'project_lead',
        day: 5, acceptance: 'Source document accepted', depends_on: [] },
      { id: 'gate', kind: 'MILESTONE', title: 'Matter readiness', role: 'sponsor',
        day: 10, acceptance: 'Acceptance recorded', depends_on: ['first'] },
    ];
    const industries = ['Legal', 'Construction', 'Football', 'Imports',
      'Software', 'Healthcare', 'General business'];
    const catalogue = industries.map((industry, index) => ({
      slug: index === 0 ? 'legal-litigation' : 'template-' + index,
      industry, title: industry + ' delivery', revision: 1, steps,
    }));
    let activated = false;
    mockProjectGet(async path => {
      if (path === '/projects') return { data: list(activated ? [persisted] : []) };
      if (path === '/projects/summary') return { data: summary(activated ? [persisted] : []) };
      if (path === '/projects/templates') return { data: {
        schema: 'WILSY-PROJECT-TEMPLATE-CATALOGUE/V1',
        tenant_id: TENANT, principal_id: PRINCIPAL,
        ownership: 'PLATFORM_STARTERS', items: catalogue,
      } };
      if (path === `/projects/${PROJECT_ID}`) return { data: result(persisted) };
      throw new Error('Unexpected template source ' + path);
    });
    api.post.mockImplementation(async (path, body, options) => {
      expect(path).toBe('/projects/templates/legal-litigation/activate');
      expect(body).toEqual({
        name: 'Legal litigation delivery', template_revision: 1,
        start_date: '2026-11-19',
      });
      expect(options.headers['X-Tenant-ID']).toBe(TENANT);
      expect(options.headers['Idempotency-Key']).toBeTruthy();
      activated = true;
      return { data: {
        schema: 'WILSY-PROJECT-TEMPLATE-ACTIVATION/V1',
        tenant_id: TENANT, principal_id: PRINCIPAL,
        template_slug: 'legal-litigation', template_revision: 1,
        project: persisted,
        items: [
          { template_step_id: 'first', kind: 'TASK', task_id: 'ptk-' + 'a'.repeat(48) },
          { template_step_id: 'gate', kind: 'MILESTONE', task_id: 'ptk-' + 'b'.repeat(48) },
        ],
        authority: {
          iam_grants: false, auto_assignments: false, financial_execution: false,
        },
      } };
    });
    render(<ProjectsWorkspace tenantId={TENANT} principalId={PRINCIPAL}
      sessionScope="industry-template-cert" />);
    fireEvent.click(await screen.findByRole('button', { name: 'Create project' }));
    fireEvent.click(screen.getByRole('button', { name: 'Browse industry templates' }));
    const choices = await screen.findByRole('listbox', { name: 'Verified industry templates' });
    expect(within(choices).getAllByRole('option')).toHaveLength(7);
    fireEvent.click(within(choices).getByRole('option', { name: /Legal/ }));
    expect(screen.getByText('Matter readiness')).toBeVisible();
    const sheet = readFileSync(resolve(process.cwd(), 'src/components/workspaces/ProjectsWorkspace.css'), 'utf8');
    expect(sheet).toContain('[aria-label="Industry project templates"] form :is(label, legend)');
    expect(sheet).toContain('-webkit-text-fill-color: #193451 !important;');
    expect(screen.queryByText(PROJECT_ID)).not.toBeInTheDocument();
    fireEvent.change(screen.getByLabelText('Project name'), {
      target: { value: 'Legal litigation delivery' },
    });
    fireEvent.change(document.querySelector('input[type="date"]'), {
      target: { value: '2026-11-19' },
    });
    fireEvent.click(screen.getByRole('button', { name: 'Create project and work in EOS' }));
    await waitFor(() => expect(api.post).toHaveBeenCalledTimes(1));
    expect(await screen.findByRole('button', { name: 'Back to projects table' })).toBeVisible();
    expect(persisted.status).toBe('planned');
  });

  it('recovers an ambiguous template response in the list without a duplicate write', async () => {
    const persisted = project({ name: 'Recovered legal delivery' });
    const steps = [
      { id: 'scope', kind: 'TASK', title: 'Review scope', role: 'project_lead',
        day: 1, acceptance: 'Scope verified', depends_on: [] },
      { id: 'gate', kind: 'MILESTONE', title: 'Matter gate', role: 'sponsor',
        day: 3, acceptance: 'Approved evidence', depends_on: ['scope'] },
    ];
    const industries = ['Legal', 'Construction', 'Football', 'Imports',
      'Software', 'Healthcare', 'General business'];
    let committed = false;
    mockProjectGet(async path => {
      if (path === '/projects') return { data: list(committed ? [persisted] : []) };
      if (path === '/projects/summary') return { data: summary(committed ? [persisted] : []) };
      if (path === '/projects/templates') return { data: {
        schema: 'WILSY-PROJECT-TEMPLATE-CATALOGUE/V1', tenant_id: TENANT,
        principal_id: PRINCIPAL, ownership: 'PLATFORM_STARTERS',
        items: industries.map((industry, index) => ({
          slug: index === 0 ? 'legal-litigation' : 'template-' + index,
          industry, title: industry + ' delivery', revision: 1, steps,
        })),
      } };
      throw new Error('Unexpected activation recovery read: ' + path);
    });
    api.post.mockImplementationOnce(async (path, body, options) => {
      expect(path).toBe('/projects/templates/legal-litigation/activate');
      expect(options.headers['Idempotency-Key']).toBeTruthy();
      expect(body.start_date).toBe('2026-11-19');
      committed = true;
      throw Object.assign(new Error('Response unavailable after commit'),
        { response: { status: 503 } });
    });
    render(<ProjectsWorkspace tenantId={TENANT} principalId={PRINCIPAL}
      sessionScope="ambiguous-template-outcome-cert"/>);
    fireEvent.click(await screen.findByRole('button', { name: 'Create project' }));
    fireEvent.click(screen.getByRole('button', { name: 'Browse industry templates' }));
    const picker = await screen.findByRole('listbox', { name: 'Verified industry templates' });
    fireEvent.click(within(picker).getByRole('option', { name: /Legal/ }));
    fireEvent.change(screen.getByLabelText('Project name'), {
      target: { value: 'Recovered legal delivery' },
    });
    fireEvent.change(screen.getByLabelText('Start date date'), {
      target: { value: '2026-11-19' },
    });
    fireEvent.click(screen.getByRole('button', { name: 'Create project and work in EOS' }));
    expect(await screen.findByText(/Save outcome not confirmed/)).toBeVisible();
    expect(screen.getByRole('button', { name: 'Refresh matching projects' })).toBeVisible();
    expect(screen.queryByRole('button', { name: 'Create project and work in EOS' }))
      .not.toBeInTheDocument();
    expect(await screen.findByRole('button', { name: /View project Recovered legal delivery/ }))
      .toBeVisible();
    expect(api.post).toHaveBeenCalledTimes(1);
  });

  it('retains committed EOS template activation when immediate list readback is unavailable', async () => {
    const persisted = project({ name: 'Software implementation' });
    const step = { id: 'scope', kind: 'TASK', title: 'Scope release',
      role: 'project_lead', day: 7, acceptance: 'Approved scope',
      depends_on: [] };
    const milestone = { id: 'gate', kind: 'MILESTONE', title: 'Release readiness',
      role: 'project_sponsor', day: 21, acceptance: 'Certified release',
      depends_on: ['scope'] };
    const industries = ['Legal', 'Construction', 'Football', 'Imports',
      'Software', 'Healthcare', 'General business'];
    mockProjectGet(async path => {
      if (path === '/projects' || path.startsWith('/projects?')) return { data: list([]) };
      if (path === '/projects/summary') return { data: summary([]) };
      if (path === '/projects/templates') return { data: {
        schema: 'WILSY-PROJECT-TEMPLATE-CATALOGUE/V1',
        tenant_id: TENANT, principal_id: PRINCIPAL,
        ownership: 'PLATFORM_STARTERS',
        items: industries.map((industry, i) => ({
          slug: industry === 'Software' ? 'software-release' : 'starter-' + i,
          industry, title: industry + ' implementation', revision: 1, steps: [step, milestone],
        })),
      } };
      throw new Error('Unexpected independent read ' + path);
    });
    api.post.mockResolvedValue({ data: {
      schema: 'WILSY-PROJECT-TEMPLATE-ACTIVATION/V1',
      tenant_id: TENANT, principal_id: PRINCIPAL,
      template_slug: 'software-release', template_revision: 1,
      project: persisted,
      items: [
        { template_step_id: 'scope', kind: 'TASK', task_id: 'ptk-' + 'a'.repeat(48) },
        { template_step_id: 'gate', kind: 'MILESTONE', task_id: 'ptk-' + 'b'.repeat(48) },
      ],
      authority: { iam_grants: false, auto_assignments: false,
        financial_execution: false },
    } });
    render(<ProjectsWorkspace tenantId={TENANT} principalId={PRINCIPAL}
      sessionScope="template-accepted-readback-delay-cert"/>);
    fireEvent.click(await screen.findByRole('button', { name: 'Create project' }));
    fireEvent.click(screen.getByRole('button', { name: 'Browse industry templates' }));
    const choices = await screen.findByRole('listbox', { name: 'Verified industry templates' });
    fireEvent.click(within(choices).getByRole('option', { name: /Software/ }));
    expect(screen.queryByRole('listbox', { name: 'Verified industry templates' })).not.toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Change template' })).toBeVisible();
    fireEvent.change(screen.getByLabelText('Start date date'), {
      target: { value: '2026-11-19' },
    });
    fireEvent.click(screen.getByRole('button', { name: 'Create project and work in EOS' }));
    expect(await screen.findByText(/Project and work saved. Current project details are being verified/)).toBeVisible();
    expect(screen.queryByText(/Save outcome not confirmed/)).not.toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Verify project' })).toBeVisible();
    expect(screen.queryByText(/EOS has not verified template activation/)).not.toBeInTheDocument();
    expect(api.post).toHaveBeenCalledTimes(1);
    expect(screen.queryByText('No projects in this tenant')).not.toBeInTheDocument();
    expect(screen.getByText(/A committed project is awaiting refreshed list visibility/))
      .toBeVisible();
  });

  it('creates source-backed notes in selected project detail without changing Planned', async () => {
    const persisted = project();
    const noteId = `pnt-${'a'.repeat(48)}`;
    const approvedNote = {
      tenant_id: TENANT, project_id: PROJECT_ID, note_id: noteId,
      author_principal_id: PRINCIPAL, revision: 1,
      body: 'Project operating context', colour: 'mint', fingerprint: 'f'.repeat(128),
      created_at: '2026-11-18T06:30:00+00:00',
      updated_at: '2026-11-18T06:30:00+00:00',
      archived_at: null,
    };
    let notes = [];
    mockProjectGet(async (path) => {
      if (path === '/projects') return { data: list([persisted]) };
      if (path === '/projects/summary') return { data: summary([persisted]) };
      if (path === `/projects/${PROJECT_ID}`) return { data: result(persisted) };
      if (path === `/projects/${PROJECT_ID}/notes?limit=50&offset=0`) return {
        data: {
          schema: 'WILSY-PROJECT-NOTE-LIST/V1',
          tenant_id: TENANT, principal_id: PRINCIPAL, project_id: PROJECT_ID,
          items: notes, limit: 50, offset: 0, has_more: false, next_offset: null,
        },
      };
      throw new Error(`Unexpected source read ${path}`);
    });
    api.post.mockImplementation(async (path, body, options) => {
      expect(path).toBe(`/projects/${PROJECT_ID}/notes`);
      expect(options.headers['X-Tenant-ID']).toBe(TENANT);
      expect(options.headers['Idempotency-Key']).toBeTruthy();
      expect(body).toEqual({ body: 'Project operating context', colour: 'mint' });
      notes = [approvedNote];
      return { data: {
        schema: 'WILSY-PROJECT-NOTE-RESULT/V1',
        tenant_id: TENANT, principal_id: PRINCIPAL, project_id: PROJECT_ID,
        note: approvedNote, events: [],
      } };
    });
    render(<ProjectsWorkspace tenantId={TENANT} principalId={PRINCIPAL}
      sessionScope="notes-client-certificate" />);
    fireEvent.click(await screen.findByRole('button', { name: /Persisted roadmap/ }));
    fireEvent.click(screen.getByRole('button', { name: 'Notes', exact: true }));
    expect(await screen.findByRole('region', { name: 'Project notes' })).toBeVisible();
    expect(screen.queryByRole('textbox', { name: 'New project note' })).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: 'New note' }));
    const input = screen.getByRole('textbox', { name: 'New project note' });
    fireEvent.change(input, { target: { value: 'Project operating context' } });
    fireEvent.click(screen.getByRole('button', { name: 'Mint sticky-note colour' }));
    expect(screen.getByRole('button', { name: 'Mint sticky-note colour' }))
      .toHaveAttribute('aria-pressed', 'true');
    fireEvent.click(screen.getByRole('button', { name: 'Save note' }));
    await waitFor(() => {
      expect(screen.getByRole('button', { name: 'Edit project note' })).toBeVisible();
    });
    expect(screen.getByText('Project operating context', { selector: '.wp-notes-list p' })).toBeVisible();
    expect(screen.getByRole('list', { name: 'Project sticky notes board' })).toBeVisible();
    expect(screen.getByText('Your note')).toBeVisible();
    expect(within(screen.getByRole('list', { name: 'Project sticky notes board' }))
      .queryByText('Revision 1')).not.toBeInTheDocument();
    expect(screen.queryByRole('textbox', { name: 'New project note' })).not.toBeInTheDocument();
    expect(api.post).toHaveBeenCalledTimes(1);
    expect(api.patch).not.toHaveBeenCalled();
    expect(persisted.status).toBe('planned');
    expect(screen.getByRole('button', { name: 'Edit project note' })).toBeVisible();
  });

  it('opens a Strategy-handoff project only after EOS lists it for the selected scope', async () => {
    const persisted = project({ name: 'WILSY OS — Unified Operating Platform Foundation' });
    mockProjectGet(async (path) => {
      if (path === '/projects') return { data: list([persisted]) };
      if (path === '/projects/summary') return { data: summary([persisted]) };
      if (path === `/projects/${PROJECT_ID}`) return { data: result(persisted) };
      throw new Error('Unexpected source route');
    });
    render(<ProjectsWorkspace tenantId={TENANT} principalId={PRINCIPAL}
      sessionScope="founder-project-handoff" focusProjectId={PROJECT_ID}/>);
    expect(await screen.findByRole('heading', { name: persisted.name })).toBeVisible();
    fireEvent.click(screen.getByRole('button', { name: 'Audit history' }));
    expect(screen.getByRole('heading', { name: 'Audit events' })).toBeVisible();
    expect(api.get.mock.calls.some(([path]) => path === `/projects/${PROJECT_ID}`)).toBe(true);
    expect(api.patch).not.toHaveBeenCalled();
    expect(api.post).not.toHaveBeenCalled();
  });

  it('refuses Strategy-handoff details when the authorized list omits that project', async () => {
    render(<ProjectsWorkspace tenantId={TENANT} principalId={PRINCIPAL}
      sessionScope="absent-project-handoff" focusProjectId={PROJECT_ID}/>);
    expect(await screen.findByText('No projects in this tenant')).toBeVisible();
    expect(api.get.mock.calls.some(([path]) => path === `/projects/${PROJECT_ID}`)).toBe(false);
  });

  it('uses full-width list until selection and renders governed EOS fields and Markdown accessibly', async () => {
    const source = project({
      code: null, owner_principal_id: null, department_id: null, target_date: null,
      summary: 'Strategy reference (descriptive only).\\n**Project objective**\\nDeliver a real platform.\\n**Scope of execution**\\n1. **Unified identity:** Secure access.\\n**Definition of done**\\nConfirmed EOS result. '.repeat(4),
    });
    mockProjectGet(async (path) => {
      if (path === '/projects') return { data: list([source]) };
      if (path === '/projects/summary') return { data: summary([source]) };
      if (path === `/projects/${PROJECT_ID}`) return { data: result(source) };
      throw new Error('Unexpected project route');
    });
    const { container } = render(<ProjectsWorkspace tenantId={TENANT} principalId={PRINCIPAL} sessionScope="layout-cert"/>);
    await screen.findByText('1 shown · 1 verified');
    expect(container.querySelector('.wp-body')).toHaveAttribute('data-layout', 'list');
    fireEvent.click(screen.getByRole('button', { name: /Persisted roadmap/ }));
    expect(await screen.findByRole('heading', { name: 'Persisted roadmap' })).toBeVisible();
    expect(container.querySelector('.wp-body')).toHaveAttribute('data-layout', 'detail');
    fireEvent.click(screen.getByRole('button', { name: 'Overview', exact: true }));
    expect(screen.getByText('Not recorded')).toBeVisible();
    expect(screen.getAllByText('Not assigned')).toHaveLength(2);
    expect(screen.getByText('Not scheduled')).toBeVisible();
    expect(screen.getByRole('heading', { name: 'Project objective' })).toBeVisible();
    expect(screen.queryByText('**Project objective**')).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: 'Read full project scope' }));
    expect(screen.getByRole('button', { name: 'Collapse project scope' })).toBeVisible();
    expect(screen.getAllByRole('heading', { name: 'Definition of done' }).length).toBeGreaterThan(0);
    fireEvent.click(screen.getByRole('button', { name: 'Manage project' }));
    expect(screen.getByLabelText('Project code')).toHaveValue('');
    fireEvent.click(screen.getByRole('button', { name: 'Back to projects table' }));
    expect(container.querySelector('.wp-body')).toHaveAttribute('data-layout', 'list');
  });

  it('exposes native calendar pickers and preserves exact source-backed date drafts', async () => {
    const current = project({ name: 'Scheduled milestone', target_date: null });
    mockProjectGet(async path => {
      if (path === '/projects') return { data: list([current]) };
      if (path === '/projects/summary') return { data: summary([current]) };
      if (path === `/projects/${PROJECT_ID}`) return { data: result(current) };
      throw new Error('Unexpected EOS read');
    });
    const pickerSpy = vi.fn();
    const originalShowPicker = HTMLInputElement.prototype.showPicker;
    HTMLInputElement.prototype.showPicker = pickerSpy;
    try {
      const { container } = render(<ProjectsWorkspace tenantId={TENANT}
        principalId={PRINCIPAL} sessionScope="date-picker-cert"/>);
      await screen.findByText('1 shown · 1 verified');
      fireEvent.click(screen.getByRole('button', { name: /Scheduled milestone/ }));
      await screen.findByRole('heading', { name: 'Scheduled milestone' });
      expect(container.querySelector('.wp-body')).toHaveAttribute('data-layout', 'detail');
      fireEvent.click(screen.getByRole('button', { name: 'Manage project' }));
      const start = screen.getByLabelText('Start date');
      const target = screen.getByLabelText('Target date');
      expect(start).toHaveAttribute('type', 'date');
      expect(target).toHaveAttribute('type', 'date');
      fireEvent.click(screen.getByRole('button', { name: 'Choose start date' }));
      fireEvent.click(screen.getByRole('button', { name: 'Choose target date' }));
      expect(pickerSpy).toHaveBeenCalledTimes(2);
      fireEvent.change(start, { target: { value: '2026-11-18' } });
      fireEvent.change(target, { target: { value: '2026-12-15' } });
      expect(start).toHaveValue('2026-11-18');
      expect(target).toHaveValue('2026-12-15');
      expect(api.patch).not.toHaveBeenCalled();
    } finally {
      if (originalShowPicker) HTMLInputElement.prototype.showPicker = originalShowPicker;
      else delete HTMLInputElement.prototype.showPicker;
    }
  });

  it('selects verified owner and department through EOS and confirms audited assignment readback', async () => {
    const ownerId = 'verified-owner';
    const departmentId = 'dept-' + 'b'.repeat(32);
    let current = project({ owner_principal_id: null, department_id: null });
    mockProjectGet(async (path) => {
      if (path === '/projects') return { data: list([current]) };
      if (path === '/projects/summary') return { data: summary([current]) };
      if (path === `/projects/${PROJECT_ID}`) return { data: result(current) };
      if (path === '/projects/assignment-options') return { data: {
        schema: 'WILSY-PROJECT-ASSIGNMENT-OPTIONS/V1',
        tenant_id: TENANT,
        principals: [{
          principal_id: ownerId, eligibility: 'VERIFIED_CURRENT',
          first_name: 'Verified', last_name: 'Owner',
        }],
        departments: [{ department_id: departmentId, name: 'Platform Engineering', status: 'ACTIVE', revision: 1 }],
      } };
      throw new Error('Unexpected project GET ' + path);
    });
    api.patch.mockImplementation(async (path, body) => {
      expect(path).toBe(`/projects/${PROJECT_ID}/assignment`);
      expect(body).toEqual({
        expected_revision: 1, owner_principal_id: ownerId, department_id: departmentId,
      });
      current = project({
        owner_principal_id: ownerId, department_id: departmentId, revision: 2,
      });
      return { data: result(current, [event('PROJECT_CREATED', 1), event('PROJECT_UPDATED', 2)]) };
    });

    render(<ProjectsWorkspace tenantId={TENANT} principalId={PRINCIPAL} sessionScope="owner-assignment" />);
    fireEvent.click(await screen.findByRole('button', { name: /Persisted roadmap/ }));
    fireEvent.click(screen.getByRole('button', { name: 'Manage project' }));
    const ownerSelector = await screen.findByRole('combobox', { name: 'Eligible project owner' });
    expect(screen.getByRole('option', { name: 'Verified Owner' })).toHaveValue(ownerId);
    expect(screen.queryByRole('option', { name: ownerId })).not.toBeInTheDocument();
    fireEvent.change(ownerSelector, { target: { value: ownerId } });
    fireEvent.change(screen.getByRole('combobox', { name: 'Tenant department' }), {
      target: { value: departmentId },
    });
    fireEvent.click(screen.getByRole('button', { name: 'Save audited assignment' }));
    await waitFor(() => expect(api.patch).toHaveBeenCalledTimes(1));
    // Wait for the revisioned EOS list/detail readback, not only the PATCH call.
    await waitFor(() => expect(screen.getByText('Revision 2')).toBeInTheDocument());
    fireEvent.click(screen.getByRole('button', { name: 'Overview', exact: true }));
    await waitFor(() => {
      expect(screen.getByText('Assigned Owner')).toBeInTheDocument();
      expect(screen.getByText('Verified Creator')).toBeInTheDocument();
      expect(screen.getByText('Assigned · name not yet verified')).toHaveAttribute(
        'title', departmentId,
      );
      expect(screen.queryByText(departmentId)).not.toBeInTheDocument();
    });
    expect(current.status).toBe('planned');
    expect(api.get.mock.calls.filter(([path]) => path === `/projects/${PROJECT_ID}`).length).toBeGreaterThan(1);
  });

  it('does not offer assignment when current owner and department directories are empty', async () => {
    mockProjectGet(async (path) => {
      if (path === '/projects') return { data: list([project()]) };
      if (path === '/projects/summary') return { data: summary([project()]) };
      if (path === `/projects/${PROJECT_ID}`) return { data: result(project()) };
      if (path === '/projects/assignment-options') return { data: {
        schema: 'WILSY-PROJECT-ASSIGNMENT-OPTIONS/V1',
        tenant_id: TENANT, principals: [], departments: [],
      } };
      throw new Error('Unexpected project GET ' + path);
    });
    render(<ProjectsWorkspace tenantId={TENANT} principalId={PRINCIPAL} sessionScope="empty-authorities" />);
    fireEvent.click(await screen.findByRole('button', { name: /Persisted roadmap/ }));
    fireEvent.click(screen.getByRole('button', { name: 'Manage project' }));
    await waitFor(() => expect(screen.getByRole('button', { name: 'Save audited assignment' })).toBeDisabled());
    expect(screen.getByText('EOS verified 0 eligible project owners and 0 active tenant departments.')).toBeInTheDocument();
    const accountability = screen.getByRole('region', { name: 'Project accountability' });
    expect(accountability).toHaveClass('wp-accountability');
    const css = readFileSync(resolve(process.cwd(), 'src/components/workspaces/ProjectsWorkspace.css'), 'utf8');
    expect(css).toMatch(/\.wilsy-projects \.wp-detail \.wp-accountability form label\s*\{[^}]*color:\s*#203a5e\s*!important;/);
    expect(css).toMatch(/\.wilsy-projects \.wp-detail \.wp-accountability form label\s*\{[^}]*text-transform:\s*none\s*!important;/);
    expect(screen.getByRole('combobox', { name: 'Eligible project owner' })).toBeDisabled();
    expect(screen.getByRole('combobox', { name: 'Tenant department' })).toBeDisabled();
    expect(screen.getByText(/No eligible project owner has been verified/)).toBeInTheDocument();
    expect(screen.getByText(/No active canonical tenant department is recorded/)).toBeInTheDocument();
    expect(api.patch).not.toHaveBeenCalled();
  });

  it('generates a code for an existing legacy project and verifies EOS list/detail readback', async () => {
    let persisted = project({ code: null });
    const generated = 'PRJ-' + PROJECT_ID.slice(-16).toUpperCase();
    mockProjectGet(async path => {
      if (path === '/projects') return { data: list([persisted]) };
      if (path === '/projects/summary') return { data: summary([persisted]) };
      if (path === `/projects/${PROJECT_ID}`) return { data: result(persisted) };
      throw new Error('Unexpected EOS GET');
    });
    api.patch.mockImplementation(async (path, body) => {
      expect(path).toBe(`/projects/${PROJECT_ID}`);
      expect(body).toEqual({ expected_revision: 1, code: generated });
      persisted = project({ ...persisted, code: generated, revision: 2 });
      return { data: result(persisted) };
    });
    render(<ProjectsWorkspace tenantId={TENANT} principalId={PRINCIPAL}
      sessionScope="code-generation-cert"/>);
    await screen.findByText('1 shown · 1 verified');
    fireEvent.click(screen.getByRole('button', { name: /Persisted roadmap/ }));
    fireEvent.click(screen.getByRole('button', { name: 'Overview', exact: true }));
    expect(await screen.findByText('Not recorded')).toBeVisible();
    fireEvent.click(screen.getByRole('button', { name: 'Generate and save code' }));
    await waitFor(() => expect(api.patch).toHaveBeenCalledTimes(1));
    await waitFor(() => expect(screen.getAllByText(generated).length).toBeGreaterThan(0));
    expect(screen.getByText('2')).toBeVisible();
    expect(api.get.mock.calls.filter(([path]) => path === '/projects').length).toBeGreaterThan(1);
    expect(api.get.mock.calls.filter(([path]) => path === `/projects/${PROJECT_ID}`).length).toBeGreaterThan(1);
    expect(screen.queryByRole('button', { name: 'Generate and save code' })).not.toBeInTheDocument();
  });

  it('creates, reads, updates, changes status, archives and reads back through EOS routes', async () => {
    let current = null;
    let events = [];
    mockProjectGet(async (path) => {
      if (path === '/projects') return { data: list(current && !current.archived_at ? [current] : []) };
      if (path === '/projects/summary') return { data: summary(current && !current.archived_at ? [current] : []) };
      if (path === `/projects/${PROJECT_ID}` && current && !current.archived_at) return { data: result(current, events) };
      throw new Error(`Unexpected project GET ${path}`);
    });
    api.post.mockImplementation(async (path, body) => {
      if (path === '/projects') {
        current = project({ name: body.name, summary: body.summary || '', code: body.code || '' });
        events = [event('PROJECT_CREATED', current.revision)];
        return { data: result(current, events) };
      }
      if (path === `/projects/${PROJECT_ID}/archive`) {
        current = project({ ...current, archived_at: '2026-11-16T12:10:00+00:00', revision: current.revision + 1, updated_at: '2026-11-16T12:10:00+00:00' });
        events = [...events, event('PROJECT_ARCHIVED', current.revision)];
        return { data: result(current, events) };
      }
      throw new Error(`Unexpected project POST ${path}`);
    });
    api.patch.mockImplementation(async (path, body) => {
      if (path !== `/projects/${PROJECT_ID}` || body.expected_revision !== current.revision) {
        throw Object.assign(new Error('revision conflict'), { response: { status: 409 } });
      }
      current = project({ ...current, ...body, revision: current.revision + 1, updated_at: '2026-11-16T12:09:00+00:00' });
      events = [...events, event(body.status ? 'PROJECT_STATUS_TRANSITION' : 'PROJECT_UPDATED', current.revision)];
      return { data: result(current, events) };
    });

    render(<ProjectsWorkspace tenantId={TENANT} principalId={PRINCIPAL} sessionScope="owner-session-1"/>);
    expect(await screen.findByText('No projects in this tenant')).toBeInTheDocument();
    expect(screen.getByText('0 active · 0 total')).toBeInTheDocument();

    fireEvent.click(screen.getByRole('button', { name: 'Create project' }));
    fireEvent.change(screen.getByLabelText('Project name'), { target: { value: 'Persisted roadmap' } });
    fireEvent.change(screen.getByLabelText(/Summary/), { target: { value: 'Source-confirmed project' } });
    fireEvent.click(screen.getByRole('button', { name: 'Save project to EOS' }));
    expect(await screen.findByRole('heading', { name: 'Persisted roadmap' })).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: 'Audit history' }));
    expect(screen.getByText('PROJECT_CREATED')).toBeInTheDocument();
    expect(screen.getByText(/By Verified Creator · revision/)).toBeInTheDocument();
    expect(api.post).toHaveBeenCalledWith('/projects', expect.objectContaining({ name: 'Persisted roadmap' }), expect.objectContaining({
      headers: { 'X-Tenant-ID': TENANT, 'Idempotency-Key': 'stable-project-key-1' },
    }));

    fireEvent.click(screen.getByRole('button', { name: 'Manage project' }));
    fireEvent.change(screen.getByLabelText('Name'), { target: { value: 'Updated roadmap' } });
    fireEvent.click(screen.getByRole('button', { name: 'Save revision' }));
    await waitFor(() => expect(api.patch).toHaveBeenCalledTimes(1));
    await waitFor(() => expect(screen.getByRole('heading', { name: 'Updated roadmap' })).toBeInTheDocument());
    expect(api.patch.mock.calls[0][1].expected_revision).toBe(1);

    fireEvent.change(screen.getByLabelText('Project status'), { target: { value: 'active' } });
    await waitFor(() => expect(api.patch).toHaveBeenCalledTimes(2));
    await waitFor(() => expect(screen.getByLabelText('Project status').value).toBe('active'));
    expect(api.patch.mock.calls[1][1]).toMatchObject({ expected_revision: 2, status: 'active' });
    expect(screen.getByLabelText('Project status')).toHaveValue('active');
    expect(api.get).toHaveBeenCalledWith('/projects/summary', expect.anything());

    fireEvent.click(screen.getByRole('button', { name: 'Archive' }));
    expect(await screen.findByText('No projects in this tenant')).toBeInTheDocument();
    expect(screen.getByText('0 active · 0 total')).toBeInTheDocument();
    expect(api.post).toHaveBeenLastCalledWith(`/projects/${PROJECT_ID}/archive`, { expected_revision: 3 }, expect.objectContaining({
      headers: { 'X-Tenant-ID': TENANT, 'Idempotency-Key': 'stable-project-key-4' },
    }));
    expect(events.map((entry) => entry.event_type)).toEqual([
      'PROJECT_CREATED', 'PROJECT_UPDATED', 'PROJECT_STATUS_TRANSITION', 'PROJECT_ARCHIVED',
    ]);
  });

  it('orders verified project audit events by revision without changing EOS evidence', async () => {
    const current = project({ revision: 4, status: 'active' });
    const evidence = [
      event('PROJECT_CREATED', 1), event('PROJECT_UPDATED', 3),
      event('PROJECT_STATUS_TRANSITION', 4), event('PROJECT_UPDATED', 2),
    ];
    mockProjectGet(async path => {
      if (path === '/projects') return { data: list([current]) };
      if (path === '/projects/summary') return { data: summary([current]) };
      if (path === `/projects/${PROJECT_ID}`) return { data: result(current, evidence) };
      throw new Error('Unexpected project GET ' + path);
    });
    render(<ProjectsWorkspace tenantId={TENANT} principalId={PRINCIPAL}
      sessionScope="audit-visual-newest-first-cert"/>);
    fireEvent.click(await screen.findByRole('button', { name: /View project Persisted roadmap/ }));
    fireEvent.click(screen.getByRole('button', { name: 'Audit history' }));
    const audit = await screen.findByRole('region', { name: 'Project audit timeline' });
    const entries = [...audit.querySelectorAll('[data-audit-revision]')];
    expect(entries.map(element => Number(element.getAttribute('data-audit-revision'))))
      .toEqual([4, 3, 2, 1]);
    expect(entries[0]).toHaveTextContent('PROJECT_STATUS_TRANSITION');
    expect(entries[0]).toHaveTextContent('Latest returned event');
    expect(entries[3]).toHaveTextContent('PROJECT_CREATED');
    expect(evidence.map(item => item.revision)).toEqual([1, 3, 4, 2]);
  });

  it('reuses the same create idempotency key after an uncertain outcome and requires list/detail readback', async () => {
    let listReads = 0;
    let present = false;
    mockProjectGet(async (path) => {
      if (path === '/projects') {
        listReads += 1;
        return { data: list(present && listReads >= 3 ? [project()] : []) };
      }
      if (path === '/projects/summary') return { data: summary(present && listReads >= 3 ? [project()] : []) };
      if (path === `/projects/${PROJECT_ID}` && present) return { data: result(project()) };
      throw new Error(`Unexpected project GET ${path}`);
    });
    api.post
      .mockRejectedValueOnce(new Error('network outcome unknown'))
      .mockImplementationOnce(async () => { present = true; return { data: result(project()) }; });

    render(<ProjectsWorkspace tenantId={TENANT} principalId={PRINCIPAL} sessionScope="session-generation-1"/>);
    await waitFor(() => expect(screen.getByText('No projects in this tenant')).toBeInTheDocument());
    fireEvent.click(screen.getByRole('button', { name: 'Create project' }));
    fireEvent.change(screen.getByLabelText('Project name'), { target: { value: 'Persisted roadmap' } });
    fireEvent.click(screen.getByRole('button', { name: 'Save project to EOS' }));
    await waitFor(() => expect(api.post).toHaveBeenCalledTimes(1));
    await waitFor(() => expect(screen.getByRole('alert')).toHaveTextContent(/could not confirm/i));
    fireEvent.click(screen.getByRole('button', { name: 'Save project to EOS' }));
    await waitFor(() => expect(api.post).toHaveBeenCalledTimes(2));
    expect(api.post.mock.calls[0][2].headers['Idempotency-Key'])
      .toBe(api.post.mock.calls[1][2].headers['Idempotency-Key']);
    expect(await screen.findByRole('heading', { name: 'Persisted roadmap' })).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: 'Audit history' }));
    expect(screen.getByText('PROJECT_CREATED')).toBeInTheDocument();
    expect(screen.getByText(/By Verified Creator · revision/)).toBeInTheDocument();
  });

  it('keeps an independently verified project accessible when summary returns HTTP 503', async () => {
    const persisted = project();
    mockProjectGet(async path => {
      if (path === '/projects') return { data: list([persisted]) };
      if (path === '/projects/summary') throw Object.assign(new Error('temporary summary outage'), {
        response: { status: 503 },
      });
      if (path === `/projects/${PROJECT_ID}`) return { data: result(persisted) };
      throw new Error('Unexpected GET ' + path);
    });
    render(<ProjectsWorkspace tenantId={TENANT} principalId={PRINCIPAL}
      sessionScope="summary-503-isolated-cert"/>);
    const projectRow = await screen.findByRole('button', { name: /View project Persisted roadmap/ });
    expect(screen.getByText('Counts unavailable')).toBeVisible();
    fireEvent.click(projectRow);
    expect(await screen.findByRole('heading', { name: 'Persisted roadmap' })).toBeVisible();
    expect(screen.queryByText(/latest EOS read failed/i)).not.toBeInTheDocument();
  });

  it('does not invalidate a rendered authorized project when a delayed summary returns 503', async () => {
    const persisted = project();
    let rejectSummary;
    const delayed = new Promise((resolve, reject) => { rejectSummary = reject; });
    mockProjectGet(async path => {
      if (path === '/projects') return { data: list([persisted]) };
      if (path === '/projects/summary') return delayed;
      if (path === `/projects/${PROJECT_ID}`) return { data: result(persisted) };
      throw new Error('Unexpected GET ' + path);
    });
    render(<ProjectsWorkspace tenantId={TENANT} principalId={PRINCIPAL}
      sessionScope="summary-late-503-isolated-cert"/>);
    fireEvent.click(await screen.findByRole('button', { name: /View project Persisted roadmap/ }));
    expect(await screen.findByRole('heading', { name: 'Persisted roadmap' })).toBeVisible();
    await act(async () => {
      rejectSummary(Object.assign(new Error('summary unavailable'), { response: { status: 503 } }));
      await Promise.resolve();
    });
    expect(screen.getByRole('heading', { name: 'Persisted roadmap' })).toBeVisible();
    expect(screen.queryByText('Counts unavailable')).not.toBeInTheDocument();
    expect(screen.queryByText(/latest EOS read failed/i)).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: 'Back to projects table' }));
    expect(await screen.findByText('Counts unavailable')).toBeVisible();
    expect(await screen.findByRole('button', { name: /View project Persisted roadmap/ })).toBeVisible();
  });

  it('shows source-honest department and readable audit labels in project overview', async () => {
    const current = project({ department_id: 'dept-' + 'a'.repeat(32) });
    mockProjectGet(async path => {
      if (path === '/projects') return { data: list([current]) };
      if (path === '/projects/summary') return { data: summary([current]) };
      if (path === `/projects/${PROJECT_ID}`) return { data: result(current) };
      throw new Error('Unexpected GET ' + path);
    });
    render(<ProjectsWorkspace tenantId={TENANT} principalId={PRINCIPAL}
      sessionScope="readable-overview-cert"/>);
    fireEvent.click(await screen.findByRole('button', { name: /View project Persisted roadmap/ }));
    fireEvent.click(screen.getByRole('button', { name: 'Overview' }));
    expect(await screen.findByText('Assigned · name not yet verified')).toHaveAttribute(
      'title', current.department_id,
    );
    expect(screen.getByText('Audited creator')).toHaveClass('text-slate-800');
    expect(screen.queryByText(current.department_id)).not.toBeInTheDocument();
  });

  it('rejects a foreign tenant summary instead of presenting it as verified empty', async () => {
    mockProjectGet(async (path) => path === '/projects'
      ? { data: list([]) }
      : { data: summary([], 'another-tenant') });
    render(<ProjectsWorkspace tenantId={TENANT} principalId={PRINCIPAL} sessionScope="foreign-response-test"/>);
    expect(await screen.findByRole('alert')).toHaveTextContent(/source is unavailable/i);
    expect(screen.queryByText('No projects in this tenant')).not.toBeInTheDocument();
    expect(screen.queryByText('0 active · 0 total')).not.toBeInTheDocument();
  });

  it('renders authorization denial without presenting an empty project state', async () => {
    api.get.mockRejectedValue(Object.assign(new Error('denied'), {
      response: { status: 403, data: { detail: 'UNEXPECTED_SERVER_TEXT' } },
    }));
    render(<ProjectsWorkspace tenantId={TENANT} principalId={PRINCIPAL} sessionScope="denied-session"/>);
    await waitFor(() => expect(screen.getByRole('alert')).toHaveTextContent(/EOS denied Projects access/i));
    expect(screen.queryByText('No projects in this tenant')).not.toBeInTheDocument();
    expect(screen.queryByText(/0 active/)).not.toBeInTheDocument();
  });

  it('keeps late list results from a prior tenant/principal/capacity scope out of the new workspace', async () => {
    let resolvePriorList;
    let listCalls = 0;
    const priorList = new Promise((resolve) => { resolvePriorList = resolve; });
    mockProjectGet(async (path, config = {}) => {
      if (path === '/projects') {
        listCalls += 1;
        if (listCalls === 1) return priorList;
        const nextTenantProject = project({ project_id: `prj-${'b'.repeat(48)}`, tenant_id: 'projects-cert-tenant-b', name: 'Tenant B record' });
        return { data: list([nextTenantProject], 'projects-cert-tenant-b', 'projects-cert-principal-b') };
      }
      const tenant = config.headers?.['X-Tenant-ID'];
      const principal = tenant === 'projects-cert-tenant-b' ? 'projects-cert-principal-b' : PRINCIPAL;
      const items = tenant === 'projects-cert-tenant-b' ? [project({ project_id: `prj-${'b'.repeat(48)}`, tenant_id: tenant, name: 'Tenant B record' })] : [];
      return { data: summary(items, tenant, principal) };
    });
    const { rerender } = render(<ProjectsWorkspace tenantId={TENANT} principalId={PRINCIPAL} sessionScope="capacity-owner"/>);
    await waitFor(() => expect(listCalls).toBe(1));
    rerender(<ProjectsWorkspace tenantId="projects-cert-tenant-b" principalId="projects-cert-principal-b" sessionScope="capacity-manager"/>);
    expect(await screen.findByText('Tenant B record')).toBeInTheDocument();
    await act(async () => { resolvePriorList({ data: list([project({ name: 'Stale tenant A item' })]) }); });
    expect(screen.queryByText('Stale tenant A item')).not.toBeInTheDocument();
  });
});

/*
 * ARTIFACT: WILSY OS Projects workspace interaction certificate
 * VERSION: v2.35.0-EOS-CAPABILITY-PROJECTION-CERT
 * AUTHORITY BOUNDARY: Synthetic client transport only; EOS remains authoritative.
 * TENANT POSTURE: Tests validate synthetic exact tenant/principal scope; live isolation is not claimed.
 * FAIL-CLOSED POSTURE: Uncertainty and denial cannot create client-side business truth.
 * FINANCIAL EXECUTION AUTHORITY: None; Kennel EOS exclusively.
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
