/**
 * TITLE: WILSY OS Projects workspace interaction certificate
 * VERSION: v2.1.0-PROJECT-TASK-EXECUTION-READBACK-CERT
 * AUTHORITY: Client contract evidence only; Python EOS owns Projects authority.
 * EPITOME: Proves exact-scope list/detail/summary validation and the user-facing
 *          create, update, status-transition and archive readback sequence.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/__tests__/components/ProjectsWorkspace.test.jsx
 * COLLABORATION / OWNERSHIP: Vitest mocks the existing authenticated api.js transport; no database is contacted.
 * CERTIFICATION / UPDATE DATE: 2026-11-17.
 * CHANGELOG: v2.1.0-PROJECT-TASK-EXECUTION-READBACK-CERT certifies task creation, verified
 *            EOS readback, revision-guarded transition and unmodified Planned
 *            project state in the existing authenticated client harness.
 * CHANGELOG: v2.1.0-PROJECT-TASK-EXECUTION-READBACK-CERT waits for the committed note row
 *            instead of a transient draft textarea with the same source text.
 * CHANGELOG: v2.1.0-PROJECT-TASK-EXECUTION-READBACK-CERT certifies source-backed project note
 *            creation/readback without modifying Planned status, propagating
 *            current principal/tenant scope or granting participant authority.
 * CHANGELOG: v2.1.0-PROJECT-TASK-EXECUTION-READBACK-CERT certifies server-side exact-tenant status filtering,
 *            one-page post-filter readback and no client-invented rows.
 * CHANGELOG: v2.1.0-PROJECT-TASK-EXECUTION-READBACK-CERT tests server-verified page metadata, source
 *            pagination beyond the first page, and denial of phantom next pages.
 * CHANGELOG: v2.1.0-PROJECT-TASK-EXECUTION-READBACK-CERT proves navigation
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
import { act, cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

const api = vi.hoisted(() => ({ get: vi.fn(), post: vi.fn(), patch: vi.fn() }));
vi.mock('../../services/api.js', () => ({ default: api }));

import ProjectsWorkspace from '../../components/workspaces/ProjectsWorkspace.jsx';

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

beforeEach(() => {
  vi.clearAllMocks();
  let keySequence = 0;
  vi.stubGlobal('crypto', { randomUUID: vi.fn(() => `stable-project-key-${++keySequence}`) });
  api.get.mockImplementation(async (path) => {
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
  it('navigates 125 source-backed tenant projects without truncating to the first 100', async () => {
    const rows = Array.from({ length: 125 }, (_, index) => project({
      project_id: `prj-${(index + 1).toString(16).padStart(48, '0')}`,
      name: `Tenant project ${index + 1}`,
      code: `TEN-${index + 1}`,
    }));
    api.get.mockImplementation(async (path) => {
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
    api.get.mockImplementation(async (path) => {
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
    api.get.mockImplementation(async (path) => {
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

  it('creates and transitions source-backed project tasks without activating the project', async () => {
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
    api.get.mockImplementation(async path => {
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
    fireEvent.click(row.querySelector('button'));
    await waitFor(() => expect(row).toHaveTextContent('In progress'));
    expect(commands).toBe(2);
    expect(persisted.status).toBe('planned');
  });

  it('creates source-backed notes in selected project detail without changing Planned', async () => {
    const persisted = project();
    const noteId = `pnt-${'a'.repeat(48)}`;
    const approvedNote = {
      tenant_id: TENANT, project_id: PROJECT_ID, note_id: noteId,
      author_principal_id: PRINCIPAL, revision: 1,
      body: 'Project operating context', fingerprint: 'f'.repeat(128),
      created_at: '2026-11-18T06:30:00+00:00',
      updated_at: '2026-11-18T06:30:00+00:00',
      archived_at: null,
    };
    let notes = [];
    api.get.mockImplementation(async (path) => {
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
      expect(body).toEqual({ body: 'Project operating context' });
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
    expect(await screen.findByRole('region', { name: 'Project notes' })).toBeVisible();
    const input = screen.getByRole('textbox', { name: 'New project note' });
    fireEvent.change(input, { target: { value: 'Project operating context' } });
    fireEvent.click(screen.getByRole('button', { name: /Add note to EOS/ }));
    await waitFor(() => {
      expect(screen.getByRole('button', { name: 'Edit note' })).toBeVisible();
    });
    expect(screen.getByText('Project operating context', { selector: '.wp-notes-list p' })).toBeVisible();
    expect(api.post).toHaveBeenCalledTimes(1);
    expect(api.patch).not.toHaveBeenCalled();
    expect(persisted.status).toBe('planned');
    expect(screen.getByRole('button', { name: 'Edit note' })).toBeVisible();
  });

  it('opens a Strategy-handoff project only after EOS lists it for the selected scope', async () => {
    const persisted = project({ name: 'WILSY OS — Unified Operating Platform Foundation' });
    api.get.mockImplementation(async (path) => {
      if (path === '/projects') return { data: list([persisted]) };
      if (path === '/projects/summary') return { data: summary([persisted]) };
      if (path === `/projects/${PROJECT_ID}`) return { data: result(persisted) };
      throw new Error('Unexpected source route');
    });
    render(<ProjectsWorkspace tenantId={TENANT} principalId={PRINCIPAL}
      sessionScope="founder-project-handoff" focusProjectId={PROJECT_ID}/>);
    expect(await screen.findByRole('heading', { name: persisted.name })).toBeVisible();
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
    api.get.mockImplementation(async (path) => {
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
    expect(screen.getByText('Not recorded')).toBeVisible();
    expect(screen.getAllByText('Not assigned')).toHaveLength(2);
    expect(screen.getByText('Not scheduled')).toBeVisible();
    expect(screen.getByRole('heading', { name: 'Project objective' })).toBeVisible();
    expect(screen.queryByText('**Project objective**')).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: 'Read full project scope' }));
    expect(screen.getByRole('button', { name: 'Collapse project scope' })).toBeVisible();
    expect(screen.getAllByRole('heading', { name: 'Definition of done' }).length).toBeGreaterThan(0);
    expect(screen.getByLabelText('Project code')).toHaveValue('');
    fireEvent.click(screen.getByRole('button', { name: 'Close project details' }));
    expect(container.querySelector('.wp-body')).toHaveAttribute('data-layout', 'list');
  });

  it('exposes native calendar pickers and preserves exact source-backed date drafts', async () => {
    const current = project({ name: 'Scheduled milestone', target_date: null });
    api.get.mockImplementation(async path => {
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
    api.get.mockImplementation(async (path) => {
      if (path === '/projects') return { data: list([current]) };
      if (path === '/projects/summary') return { data: summary([current]) };
      if (path === `/projects/${PROJECT_ID}`) return { data: result(current) };
      if (path === '/projects/assignment-options') return { data: {
        schema: 'WILSY-PROJECT-ASSIGNMENT-OPTIONS/V1',
        tenant_id: TENANT,
        principals: [{ principal_id: ownerId, eligibility: 'VERIFIED_CURRENT' }],
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
    const ownerSelector = await screen.findByRole('combobox', { name: 'Eligible project owner' });
    fireEvent.change(ownerSelector, { target: { value: ownerId } });
    fireEvent.change(screen.getByRole('combobox', { name: 'Tenant department' }), {
      target: { value: departmentId },
    });
    fireEvent.click(screen.getByRole('button', { name: 'Save audited assignment' }));
    await waitFor(() => {
      expect(api.patch).toHaveBeenCalledTimes(1);
      expect(screen.getByText(ownerId)).toBeInTheDocument();
      expect(screen.getByText(departmentId)).toBeInTheDocument();
    });
    expect(current.status).toBe('planned');
    expect(api.get.mock.calls.filter(([path]) => path === `/projects/${PROJECT_ID}`).length).toBeGreaterThan(1);
  });

  it('does not offer assignment when current owner and department directories are empty', async () => {
    api.get.mockImplementation(async (path) => {
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
    api.get.mockImplementation(async path => {
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
    api.get.mockImplementation(async (path) => {
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
    expect(screen.getByText('PROJECT_CREATED')).toBeInTheDocument();
    expect(api.post).toHaveBeenCalledWith('/projects', expect.objectContaining({ name: 'Persisted roadmap' }), expect.objectContaining({
      headers: { 'X-Tenant-ID': TENANT, 'Idempotency-Key': 'stable-project-key-1' },
    }));

    fireEvent.change(screen.getByLabelText('Name'), { target: { value: 'Updated roadmap' } });
    fireEvent.click(screen.getByRole('button', { name: 'Save revision' }));
    await waitFor(() => expect(api.patch).toHaveBeenCalledTimes(1));
    await waitFor(() => expect(screen.getByRole('heading', { name: 'Updated roadmap' })).toBeInTheDocument());
    expect(api.patch.mock.calls[0][1].expected_revision).toBe(1);

    fireEvent.change(screen.getByLabelText('Project status'), { target: { value: 'active' } });
    await waitFor(() => expect(api.patch).toHaveBeenCalledTimes(2));
    await waitFor(() => expect(screen.getByLabelText('Project status').value).toBe('active'));
    expect(api.patch.mock.calls[1][1]).toMatchObject({ expected_revision: 2, status: 'active' });
    expect(screen.getByText('1 active · 1 total')).toBeInTheDocument();

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

  it('reuses the same create idempotency key after an uncertain outcome and requires list/detail readback', async () => {
    let listReads = 0;
    let present = false;
    api.get.mockImplementation(async (path) => {
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
    expect(screen.getByText('PROJECT_CREATED')).toBeInTheDocument();
  });

  it('rejects a foreign tenant summary instead of presenting it as verified empty', async () => {
    api.get.mockImplementation(async (path) => path === '/projects'
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
    api.get.mockImplementation(async (path, config = {}) => {
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
 * VERSION: v2.1.0-PROJECT-TASK-EXECUTION-READBACK-CERT
 * AUTHORITY BOUNDARY: Synthetic client transport only; EOS remains authoritative.
 * TENANT POSTURE: Tests validate synthetic exact tenant/principal scope; live isolation is not claimed.
 * FAIL-CLOSED POSTURE: Uncertainty and denial cannot create client-side business truth.
 * FINANCIAL EXECUTION AUTHORITY: None; Kennel EOS exclusively.
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
