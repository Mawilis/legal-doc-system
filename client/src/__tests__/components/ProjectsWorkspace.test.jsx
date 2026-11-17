/**
 * TITLE: WILSY OS Projects workspace interaction certificate
 * VERSION: v1.1.1-EXACT-SCOPE-CREATE-UPDATE-ARCHIVE-CERT
 * AUTHORITY: Client contract evidence only; Python EOS owns Projects authority.
 * EPITOME: Proves exact-scope list/detail/summary validation and the user-facing
 *          create, update, status-transition and archive readback sequence.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/__tests__/components/ProjectsWorkspace.test.jsx
 * COLLABORATION / OWNERSHIP: Vitest mocks the existing authenticated api.js transport; no database is contacted.
 * CERTIFICATION / UPDATE DATE: 2026-11-16.
 * CHANGELOG: v1.1.1-EXACT-SCOPE-CREATE-UPDATE-ARCHIVE-CERT covers full synthetic lifecycle and rejects stale or foreign envelopes; v1.0.1 covers create replay and denial.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
 * SECURITY / PRIVACY POSTURE: Synthetic test identities only; no credential or production data.
 * TENANT BOUNDARY: Tests assert selected tenant/principal envelopes and stale response isolation; not a live EOS isolation certificate.
 * AUTHORITY BOUNDARY: HTTP is mocked; no IAM or entitlement grant is made or proven.
 * FINANCIAL AUTHORITY BOUNDARY: No financial command is exercised.
 */
import React from 'react';
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
 * VERSION: v1.1.1-EXACT-SCOPE-CREATE-UPDATE-ARCHIVE-CERT
 * AUTHORITY BOUNDARY: Synthetic client transport only; EOS remains authoritative.
 * TENANT POSTURE: Tests validate synthetic exact tenant/principal scope; live isolation is not claimed.
 * FAIL-CLOSED POSTURE: Uncertainty and denial cannot create client-side business truth.
 * FINANCIAL EXECUTION AUTHORITY: None; Kennel EOS exclusively.
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
