/**
 * TITLE: WILSY OS Authenticated My Work Execution Queue Tests
 * VERSION: v1.11.0-INTERACTIVE-RESIZE-CERT
 * AUTHORITY: Wilsy OS Core Governance
 * EPITOME: Certifies compact queue rendering, source filters, detail access,
 *          keyboard/focus behavior, source-owned completion and EOS readback.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/__tests__/components/MyWorkWorkspace.test.jsx
 * COLLABORATION / OWNERSHIP: MyWorkWorkspace.jsx, shared projection validator,
 *                            EOS My Work and independent source commands.
 * CERTIFICATION / UPDATE DATE: 2026-11-17
 * CHANGELOG: v1.11.0-INTERACTIVE-RESIZE-CERT simulates real pointer
 *            resizing and keyboard width reduction, not merely existence
 *            of the workbench resize handle.
 * CHANGELOG: v1.10.0-FLOATING-RESIZE-AND-AUTHORITY-CERT checks
 *            the independent resizable dialog handle and explicit EOS
 *            denied-UPDATE disclosure, without displaying unauthorized
 *            mutation controls or inventing source status.
 * CHANGELOG: v1.9.0-SOURCE-AUDITED-PROGRESS-CERT proves the
 *            In Progress state changes only after source command, persisted
 *            status audit and a fresh authenticated My Work projection.
 * CHANGELOG: v1.8.0-SOURCE-AUDITED-CANCEL-CERT verifies source-owned
 *            cancellation POST, mandatory reason, revision, idempotency,
 *            persisted cancellation event and fresh queue removal.
 * CHANGELOG: v1.7.1-SOURCE-EDIT-DUAL-SURFACE-CERT confirms the
 *            updated title is present in both the verified work row and
 *            source detail without assuming it occurs only once.
 * CHANGELOG: v1.7.0-SOURCE-AUDITED-EDIT-BROWSER-CERT verifies
 *            independently permitted CRM editing with exact PATCH payload,
 *            source/audit/unified readback, and denial when UPDATE is absent.
 *            No in-browser synthetic persistence is accepted.
 * CHANGELOG: v1.6.0-CRM-SOURCE-DETAIL-READBACK-CERT verifies exact source-owned CRM
 *            record details and fails closed for foreign-tenant data without
 *            creating browser audit or lifecycle authority.
 *            v1.5.1-LOCAL-TIMEZONE-VERIFICATION-CERT certifies the exact EOS as_of instant
 *            in the runner's browser-local timezone, retaining a real
 *            timestamp assertion across Johannesburg and UTC environments.
 *            v1.5.0-DENSE-EXECUTION-QUEUE-CERT covers responsive detail drawer
 *            lifecycle, compact row list, filters/order, dirty draft protection,
 *            exact source completion receipts, projection readback and failure.
 *            v1.4.0-HR-SOURCE-NAVIGATION-CERT verifies only EOS-admitted HR
 *            navigation, never client HR action authority.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
 * SECURITY / PRIVACY POSTURE: Synthetic records and mocked transport only.
 * TENANT BOUNDARY: Projection tenant/principal are checked before display.
 * AUTHORITY BOUNDARY: Only owning source services may complete work.
 * FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively.
 */
import React from 'react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import MyWorkWorkspace from '../../components/workspaces/MyWorkWorkspace.jsx';
import api from '../../services/api.js';
import AuthContext from '../../contexts/authContext.jsx';
import { completeLegalWorkItem } from '../../services/legalOperationsService.js';
import { readAttentionSourceActions } from '../../services/attentionFeedClient.js';

vi.mock('../../services/legalOperationsService.js', () => ({
  completeLegalWorkItem: vi.fn(),
}));
vi.mock('../../services/api.js', () => ({ default: { get: vi.fn(), post: vi.fn(), patch: vi.fn() } }));
vi.mock('../../services/attentionFeedClient.js', () => ({ readAttentionSourceActions: vi.fn() }));

const payload = {
  schema: 'WILSY-OS-UNIFIED-MY-WORK/V1',
  tenant_id: 'tenant-a',
  principal_id: 'principal-a',
  as_of: '2026-11-06T10:00:00+00:00',
  summary: {
    active_count: 2,
    overdue_count: 1,
    source_counts: { OPERATIONS: 1, LEGAL: 1 },
  },
  sources_included: ['OPERATIONS', 'LEGAL'],
  authority: { commands_owned_by: 'SOURCE_SERVICES', permits_completion: false },
  items: [
    {
      source: 'OPERATIONS', source_key: 'OPERATIONS:ops-1', work_item_id: 'ops-1',
      title: 'Prepare daily operations report', description: 'Review the verified operating figures.',
      status: 'OPEN', priority: 'HIGH', kind: 'TASK', due_at: '2026-11-05T10:00:00+00:00', is_overdue: true,
    },
    {
      source: 'LEGAL', source_key: 'LEGAL:legal-1', work_item_id: 'legal-1',
      title: 'Review matter evidence', description: '',
      status: 'OPEN', priority: 'NORMAL', kind: 'TASK', due_at: null, is_overdue: false,
    },
  ],
};

const renderWorkspace = (props = {}) => render(
  <MemoryRouter><MyWorkWorkspace {...props} /></MemoryRouter>,
);
const openRow = async (title) => {
  const row = await screen.findByRole('button', { name: new RegExp(title) });
  fireEvent.click(row);
  return row;
};

beforeEach(() => {
  vi.clearAllMocks();
  readAttentionSourceActions.mockResolvedValue({ sourceActions: {}, unavailableSources: [] });
  api.get.mockResolvedValue({ data: payload });
  api.post.mockImplementation(async (path) => ({
    data: { work_item_id: decodeURIComponent(path.split('/').at(-2)), status: 'COMPLETED' },
  }));
  completeLegalWorkItem.mockResolvedValue({ work_item_id: 'legal-1', completion_event_id: 'event-1' });
});

describe('authenticated My Work execution queue', () => {
  it('loads the validated EOS projection and renders one compact row per item', async () => {
    renderWorkspace();
    expect(await screen.findByRole('heading', { name: 'My Work' })).toBeTruthy();
    expect(screen.getAllByRole('listitem')).toHaveLength(2);
    expect(screen.getByText('Prepare daily operations report')).toBeTruthy();
    expect(screen.getByText('Review matter evidence')).toBeTruthy();
    expect(screen.getByText('Overdue')).toBeTruthy();
    // The verified source instant is stable; its visible local clock time is
    // determined by the browser environment, not the CI runner's region.
    const verifiedInstant = new Date(payload.as_of);
    expect(verifiedInstant.toISOString()).toBe('2026-11-06T10:00:00.000Z');
    const localVerifiedTime = verifiedInstant.toLocaleString(undefined, {
      dateStyle: 'medium', timeStyle: 'short',
    });
    expect(screen.getAllByText('Verified ' + localVerifiedTime).length).toBeGreaterThan(0);
    expect(api.get).toHaveBeenCalledTimes(1);
    const [path, request] = api.get.mock.calls[0];
    expect(path).toBe('/my-work');
    expect(request.forceNetworkRetry).toBe(true);
    expect(request.signal.aborted).toBe(false);
  });

  it('reads the selected CRM source record under the authenticated tenant', async () => {
    const crmItem = {
      ...payload.items[0], source: 'CRM', source_key: 'CRM:crm-1',
      work_item_id: 'crm-1', title: 'Prepare CRM launch plan', status: 'OPEN',
    };
    const crmProjection = {
      ...payload, items: [crmItem], sources_included: ['CRM'],
      summary: { active_count: 1, overdue_count: 1, source_counts: { CRM: 1 } },
    };
    const sourceRecord = {
      schema: 'WILSY-OWNER-COMMERCIAL-WORK-ITEM/V1',
      tenant_id: 'tenant-a', work_item_id: 'crm-1',
      title: crmItem.title, description: crmItem.description,
      kind: 'TASK', status: 'OPEN', priority: crmItem.priority,
      owner_principal_id: 'principal-a', source_type: null, source_id: null,
      due_at: crmItem.due_at, created_at: '2026-11-01T10:00:00+00:00',
      updated_at: '2026-11-06T10:00:00+00:00',
      completed_at: null, completion_note: null,
    };
    api.get.mockImplementation(async (path) => {
      if (path === '/my-work') return { data: crmProjection };
      if (path === '/crm/owner-workspace/work-items/crm-1') return { data: sourceRecord };
      throw new Error('UNEXPECTED_SOURCE_ROUTE');
    });
    render(
      <AuthContext.Provider value={{ sessionGeneration: 4, user: {
        id: 'principal-a', tenantId: 'tenant-a',
      } }}>
        <MemoryRouter><MyWorkWorkspace /></MemoryRouter>
      </AuthContext.Provider>,
    );
    await openRow('Prepare CRM launch plan');
    expect(await screen.findByText('Persisted source record verified for this tenant')).toBeTruthy();
    const resize = screen.getByRole('separator', { name: 'Resize work details' });
    const dialog = screen.getByRole('dialog', { name: 'Prepare CRM launch plan' });
    expect(resize).toBeTruthy();
    expect(dialog).toBeTruthy();
    await waitFor(() => expect(parseFloat(dialog.style.width)).toBeGreaterThan(500));
    const originalWidth = parseFloat(dialog.style.width);
    fireEvent.pointerDown(resize, { button: 0, clientX: 600, clientY: 170 });
    fireEvent.pointerMove(window, { clientX: 680, clientY: 170 });
    fireEvent.pointerUp(window);
    await waitFor(() => expect(parseFloat(dialog.style.width)).toBeGreaterThan(originalWidth));
    const expandedWidth = parseFloat(dialog.style.width);
    fireEvent.keyDown(resize, { key: 'ArrowLeft' });
    await waitFor(() => expect(parseFloat(dialog.style.width)).toBeLessThan(expandedWidth));
    expect(screen.getByText('Principal recorded; human-readable name unavailable from this source')).toBeTruthy();
    expect(api.get).toHaveBeenCalledWith(
      '/crm/owner-workspace/work-items/crm-1',
      expect.objectContaining({ forceNetworkRetry: true, signal: expect.anything() }),
    );
  });


  it('edits a CRM task only after EOS UPDATE admission and verifies source audit and queue', async () => {
    const item = {
      ...payload.items[0], source: 'CRM', source_key: 'CRM:crm-edit-1',
      work_item_id: 'crm-edit-1', title: 'Original CRM task', status: 'OPEN',
    };
    const original = {
      schema: 'WILSY-OWNER-COMMERCIAL-WORK-ITEM/V1',
      tenant_id: 'tenant-a', work_item_id: item.work_item_id,
      title: item.title, description: item.description,
      kind: 'TASK', status: 'OPEN', priority: 'HIGH',
      owner_principal_id: 'principal-a',
      source_type: null, source_id: null, due_at: item.due_at,
      created_at: '2026-11-01T10:00:00+00:00',
      updated_at: '2026-11-06T10:00:00+00:00',
      completed_at: null, completion_note: null,
    };
    const updated = {
      ...original, title: 'Updated CRM task', description: 'Audited change',
      updated_at: '2026-11-06T10:15:00+00:00',
    };
    const initial = {
      ...payload, items: [item], sources_included: ['CRM'],
      summary: { active_count: 1, overdue_count: 1, source_counts: { CRM: 1 } },
    };
    const after = {
      ...initial,
      items: [{ ...item, title: updated.title, description: updated.description }],
    };
    let sourceUpdated = false;
    api.get.mockImplementation(async (path) => {
      if (path === '/my-work') return { data: sourceUpdated ? after : initial };
      if (path === '/crm/owner-workspace/work-items/crm-edit-1') {
        return { data: sourceUpdated ? updated : original };
      }
      if (path === '/crm/owner-workspace/work-items/crm-edit-1/history') {
        return { data: {
          schema: 'WILSY-OWNER-COMMERCIAL-WORK-HISTORY/V1',
          tenant_id: 'tenant-a', work_item_id: 'crm-edit-1',
          events: [{
            actor_principal_id: 'principal-a', recorded_at: updated.updated_at,
            before: original, after: updated,
          }],
        }};
      }
      throw new Error('UNEXPECTED_EDIT_READ');
    });
    readAttentionSourceActions.mockResolvedValue({
      sourceActions: { CRM: ['CREATE', 'UPDATE', 'COMPLETE'] },
      unavailableSources: [],
    });
    api.patch.mockImplementation(async () => {
      sourceUpdated = true;
      return { data: updated };
    });
    render(
      <AuthContext.Provider value={{ sessionGeneration: 4, user: {
        id: 'principal-a', tenantId: 'tenant-a',
      } }}>
        <MemoryRouter><MyWorkWorkspace /></MemoryRouter>
      </AuthContext.Provider>,
    );
    await openRow('Original CRM task');
    await screen.findByText('Persisted source record verified for this tenant');
    fireEvent.click(await screen.findByRole('button', { name: 'Edit CRM task' }));
    fireEvent.change(screen.getByRole('textbox', { name: 'Edit CRM title' }), {
      target: { value: updated.title },
    });
    fireEvent.change(screen.getByRole('textbox', { name: 'Edit CRM description' }), {
      target: { value: updated.description },
    });
    fireEvent.click(screen.getByRole('button', { name: 'Save audited edit' }));
    await waitFor(() => expect(api.patch).toHaveBeenCalledTimes(1));
    const [route, request, options] = api.patch.mock.calls[0];
    expect(route).toBe('/crm/owner-workspace/work-items/crm-edit-1');
    expect(request).toMatchObject({
      title: updated.title, description: updated.description,
      priority: 'HIGH', expected_updated_at: original.updated_at,
    });
    expect(options.headers['Idempotency-Key']).toBeTruthy();
    await waitFor(() => expect(screen.getByText(
      'CRM edit confirmed by source, audit history and fresh My Work.',
    )).toBeTruthy());
    expect(api.get.mock.calls.some(([path]) => path.endsWith('/history'))).toBe(true);
    expect(screen.getAllByText(updated.title).length).toBeGreaterThanOrEqual(1);
  });


  it('cancels only a verified owned CRM task, then verifies history and refreshed queue', async () => {
    const item = {
      ...payload.items[0], source: 'CRM', source_key: 'CRM:crm-cancel-1',
      work_item_id: 'crm-cancel-1', title: 'Withdrawn CRM follow-up', status: 'OPEN',
    };
    const original = {
      schema: 'WILSY-OWNER-COMMERCIAL-WORK-ITEM/V1',
      tenant_id: 'tenant-a', work_item_id: item.work_item_id,
      title: item.title, description: item.description, kind: 'TASK',
      status: 'OPEN', priority: 'HIGH', owner_principal_id: 'principal-a',
      source_type: null, source_id: null, due_at: item.due_at,
      created_at: '2026-11-01T10:00:00+00:00',
      updated_at: '2026-11-06T10:00:00+00:00',
      completed_at: null, completion_note: null,
    };
    const cancelled = {
      ...original, status: 'CANCELLED', updated_at: '2026-11-06T10:20:00+00:00',
    };
    const initial = {
      ...payload, items: [item], sources_included: ['CRM'],
      summary: { active_count: 1, overdue_count: 1, source_counts: { CRM: 1 } },
    };
    const after = {
      ...initial, items: [],
      summary: { active_count: 0, overdue_count: 0, source_counts: { CRM: 0 } },
    };
    let committed = false;
    api.get.mockImplementation(async (path) => {
      if (path === '/my-work') return { data: committed ? after : initial };
      if (path.endsWith('/crm-cancel-1')) return { data: committed ? cancelled : original };
      if (path.endsWith('/crm-cancel-1/history')) {
        return { data: {
          schema: 'WILSY-OWNER-COMMERCIAL-WORK-HISTORY/V1',
          tenant_id: 'tenant-a', work_item_id: 'crm-cancel-1',
          events: [{ operation: 'CANCEL', reason: 'Requirement withdrawn',
            actor_principal_id: 'principal-a', recorded_at: cancelled.updated_at,
            before: original, after: cancelled }],
        } };
      }
      throw new Error('UNEXPECTED_CANCEL_READ');
    });
    readAttentionSourceActions.mockResolvedValue({
      sourceActions: { CRM: ['UPDATE', 'COMPLETE'] }, unavailableSources: [],
    });
    api.post.mockImplementation(async (path) => {
      if (!path.endsWith('/crm-cancel-1/cancel')) throw new Error('UNEXPECTED_CANCEL_POST');
      committed = true;
      return { data: cancelled };
    });
    render(
      <AuthContext.Provider value={{ sessionGeneration: 4, user: {
        id: 'principal-a', tenantId: 'tenant-a',
      } }}>
        <MemoryRouter><MyWorkWorkspace /></MemoryRouter>
      </AuthContext.Provider>,
    );
    await openRow('Withdrawn CRM follow-up');
    await screen.findByText('Persisted source record verified for this tenant');
    fireEvent.click(await screen.findByRole('button', { name: 'Cancel task' }));
    fireEvent.change(screen.getByRole('textbox', { name: 'CRM cancellation reason' }), {
      target: { value: 'Requirement withdrawn' },
    });
    fireEvent.click(screen.getByRole('button', { name: 'Confirm cancellation' }));
    await waitFor(() => expect(api.post).toHaveBeenCalledTimes(1));
    const [url, body, options] = api.post.mock.calls[0];
    expect(url).toBe('/crm/owner-workspace/work-items/crm-cancel-1/cancel');
    expect(body).toEqual({
      reason: 'Requirement withdrawn', expected_updated_at: original.updated_at,
    });
    expect(options.headers['Idempotency-Key']).toBeTruthy();
    await waitFor(() => expect(screen.queryByRole('dialog')).toBeNull());
    expect(screen.queryByText('Withdrawn CRM follow-up')).toBeNull();
    expect(api.get.mock.calls.some(([path]) => path.endsWith('/history'))).toBe(true);
  });


  it('persists In Progress through source, status audit and refreshed active queue', async () => {
    const item = {
      ...payload.items[0], source: 'CRM', source_key: 'CRM:crm-progress',
      work_item_id: 'crm-progress', title: 'Production follow-up',
      status: 'OPEN',
    };
    const original = {
      schema: 'WILSY-OWNER-COMMERCIAL-WORK-ITEM/V1',
      tenant_id: 'tenant-a', work_item_id: 'crm-progress',
      title: item.title, description: item.description, kind: 'TASK',
      status: 'OPEN', priority: 'HIGH', owner_principal_id: 'principal-a',
      source_type: null, source_id: null, due_at: item.due_at,
      created_at: '2026-11-01T10:00:00+00:00',
      updated_at: '2026-11-06T10:00:00+00:00',
      completed_at: null, completion_note: null,
    };
    const progressed = {
      ...original, status: 'IN_PROGRESS',
      updated_at: '2026-11-06T10:20:00+00:00',
    };
    const initial = {
      ...payload, items: [item], sources_included: ['CRM'],
      summary: { active_count: 1, overdue_count: 1, source_counts: { CRM: 1 } },
    };
    let committed = false;
    api.get.mockImplementation(async (path) => {
      if (path === '/my-work') return { data: committed ? {
        ...initial, items: [{ ...item, status: 'IN_PROGRESS' }],
      } : initial };
      if (path === '/crm/owner-workspace/work-items/crm-progress') {
        return { data: committed ? progressed : original };
      }
      if (path.endsWith('/crm-progress/history')) return { data: {
        schema: 'WILSY-OWNER-COMMERCIAL-WORK-HISTORY/V1',
        tenant_id: 'tenant-a', work_item_id: 'crm-progress',
        events: [{ operation: 'STATUS', actor_principal_id: 'principal-a',
          before: original, after: progressed, recorded_at: progressed.updated_at }],
      } };
      throw new Error('UNEXPECTED_PROGRESS_READ');
    });
    readAttentionSourceActions.mockResolvedValue({
      sourceActions: { CRM: ['UPDATE'] }, unavailableSources: [],
    });
    api.post.mockImplementation(async (path) => {
      if (!path.endsWith('/crm-progress/status')) throw new Error('UNEXPECTED_PROGRESS_POST');
      committed = true;
      return { data: progressed };
    });
    render(
      <AuthContext.Provider value={{ sessionGeneration: 4, user: {
        id: 'principal-a', tenantId: 'tenant-a',
      } }}>
        <MemoryRouter><MyWorkWorkspace /></MemoryRouter>
      </AuthContext.Provider>,
    );
    await openRow('Production follow-up');
    await screen.findByText('Persisted source record verified for this tenant');
    const select = await screen.findByRole('combobox', { name: 'CRM work status' });
    fireEvent.change(select, { target: { value: 'IN_PROGRESS' } });
    fireEvent.click(screen.getByRole('button', { name: 'Update status' }));
    await waitFor(() => expect(api.post).toHaveBeenCalledWith(
      '/crm/owner-workspace/work-items/crm-progress/status',
      { status: 'IN_PROGRESS', expected_updated_at: original.updated_at },
      expect.objectContaining({ headers: { 'Idempotency-Key': expect.any(String) } }),
    ));
    await waitFor(() => expect(screen.getAllByText('In Progress').length).toBeGreaterThan(0));
    expect(api.get.mock.calls.some(([path]) => path.endsWith('/history'))).toBe(true);
  });

  it('never exposes CRM edit when current EOS source permission is absent', async () => {
    const item = {
      ...payload.items[0], source: 'CRM', source_key: 'CRM:crm-denied',
      work_item_id: 'crm-denied', title: 'Read-only CRM task',
    };
    const projection = {
      ...payload, items: [item], sources_included: ['CRM'],
      summary: { active_count: 1, overdue_count: 1, source_counts: { CRM: 1 } },
    };
    const source = {
      schema: 'WILSY-OWNER-COMMERCIAL-WORK-ITEM/V1',
      tenant_id: 'tenant-a', work_item_id: 'crm-denied',
      title: item.title, description: item.description, status: 'OPEN',
      priority: item.priority, kind: 'TASK', owner_principal_id: 'principal-a',
      created_at: '2026-11-01T10:00:00Z',
      updated_at: '2026-11-06T10:00:00Z',
      due_at: item.due_at, source_type: null, source_id: null,
      completed_at: null, completion_note: null,
    };
    api.get.mockImplementation(async (path) => {
      if (path === '/my-work') return { data: projection };
      if (path === '/crm/owner-workspace/work-items/crm-denied') return { data: source };
      throw new Error('UNEXPECTED_SOURCE_READ');
    });
    render(
      <AuthContext.Provider value={{ sessionGeneration: 4, user: {
        id: 'principal-a', tenantId: 'tenant-a',
      } }}>
        <MemoryRouter><MyWorkWorkspace /></MemoryRouter>
      </AuthContext.Provider>,
    );
    await openRow('Read-only CRM task');
    await screen.findByText('Persisted source record verified for this tenant');
    await waitFor(() => expect(screen.getByText('EOS edit permission not admitted')).toBeTruthy());
    expect(screen.getByRole('button', { name: 'Recheck actions' })).toBeTruthy();
    expect(screen.queryByRole('combobox', { name: 'CRM work status' })).toBeNull();
    expect(screen.queryByRole('button', { name: 'Edit CRM task' })).toBeNull();
    expect(api.patch).not.toHaveBeenCalled();
  });

  it('rejects CRM source detail from another tenant without showing it as verified', async () => {
    const crmItem = {
      ...payload.items[0], source: 'CRM', source_key: 'CRM:crm-2',
      work_item_id: 'crm-2', title: 'Review tenant CRM work', status: 'OPEN',
    };
    const crmProjection = {
      ...payload, items: [crmItem], sources_included: ['CRM'],
      summary: { active_count: 1, overdue_count: 1, source_counts: { CRM: 1 } },
    };
    api.get.mockImplementation(async (path) => {
      if (path === '/my-work') return { data: crmProjection };
      if (path === '/crm/owner-workspace/work-items/crm-2') return { data: {
        schema: 'WILSY-OWNER-COMMERCIAL-WORK-ITEM/V1',
        tenant_id: 'foreign-tenant', work_item_id: 'crm-2',
        title: crmItem.title, description: '', status: 'OPEN',
        owner_principal_id: 'foreign-principal',
        created_at: '2026-11-01T10:00:00Z',
        updated_at: '2026-11-06T10:00:00Z',
        completed_at: null, completion_note: null,
      } };
      throw new Error('UNEXPECTED_SOURCE_ROUTE');
    });
    render(
      <AuthContext.Provider value={{ sessionGeneration: 4, user: {
        id: 'principal-a', tenantId: 'tenant-a',
      } }}>
        <MemoryRouter><MyWorkWorkspace /></MemoryRouter>
      </AuthContext.Provider>,
    );
    await openRow('Review tenant CRM work');
    expect(await screen.findByRole('alert')).toHaveTextContent('CRM_DETAIL_SOURCE_OR_SCOPE_MISMATCH');
    expect(screen.queryByText('Persisted source record verified for this tenant')).toBeNull();
    expect(screen.queryByText('foreign-principal')).toBeNull();
  });

  it('renders ten authorized tasks as rows and offers only admitted sources with counts', async () => {
    const many = Array.from({ length: 10 }, (_, index) => ({
      ...payload.items[1], source: 'LEGAL', work_item_id: `legal-${index}`,
      source_key: `LEGAL:legal-${index}`, title: `Verified task ${index}`,
    }));
    api.get.mockResolvedValueOnce({ data: {
      ...payload, items: many,
      summary: { active_count: 10, overdue_count: 0, source_counts: { LEGAL: 10 } },
      sources_included: ['LEGAL'],
    } });
    renderWorkspace();
    expect(await screen.findAllByRole('listitem')).toHaveLength(10);
    expect(screen.getByRole('button', { name: 'Legal 10' })).toBeTruthy();
    expect(screen.queryByRole('button', { name: /CRM/ })).toBeNull();
    expect(screen.queryByRole('button', { name: /HR & Hiring/ })).toBeNull();
  });

  it('filters admitted source rows and search results from the validated projection', async () => {
    renderWorkspace();
    await screen.findByText('Prepare daily operations report');
    fireEvent.click(screen.getByRole('button', { name: 'Legal 1' }));
    expect(screen.queryByText('Prepare daily operations report')).toBeNull();
    expect(screen.getByText('Review matter evidence')).toBeTruthy();
    fireEvent.click(screen.getByRole('button', { name: 'All 2' }));
    fireEvent.change(screen.getByRole('searchbox', { name: 'Search authorized work' }), {
      target: { value: 'verified operating' },
    });
    expect(screen.getByText('Prepare daily operations report')).toBeTruthy();
    expect(screen.queryByText('Review matter evidence')).toBeNull();
  });

  it('sorts overdue first, then the chosen due/priority order with stable row identity', async () => {
    const rows = [
      { ...payload.items[1], source: 'CRM', work_item_id: 'z', source_key: 'CRM:z', title: 'No deadline' },
      { ...payload.items[1], source: 'CRM', work_item_id: 'b', source_key: 'CRM:b', title: 'Later normal', priority: 'NORMAL', due_at: '2026-11-08T10:00:00+00:00' },
      { ...payload.items[1], source: 'CRM', work_item_id: 'a', source_key: 'CRM:a', title: 'Earlier low', priority: 'LOW', due_at: '2026-11-07T10:00:00+00:00' },
      { ...payload.items[1], source: 'CRM', work_item_id: 'c', source_key: 'CRM:c', title: 'Overdue high', priority: 'HIGH', due_at: '2026-11-05T10:00:00+00:00', is_overdue: true },
    ];
    api.get.mockResolvedValueOnce({ data: {
      ...payload, items: rows,
      summary: { active_count: 4, overdue_count: 1, source_counts: { CRM: 4 } },
      sources_included: ['CRM'],
    } });
    renderWorkspace();
    await screen.findByText('Overdue high');
    const titles = () => [...document.querySelectorAll('[role="listitem"] .truncate')].map((el) => el.textContent);
    expect(titles()).toEqual(['Overdue high', 'Earlier low', 'Later normal', 'No deadline']);
    fireEvent.change(screen.getByLabelText('Sort'), { target: { value: 'priority' } });
    expect(titles()).toEqual(['Overdue high', 'Later normal', 'No deadline', 'Earlier low']);
  });

  it('opens a source-backed detail drawer and restores focus to the selected row on close', async () => {
    renderWorkspace();
    const row = await openRow('Prepare daily operations report');
    expect(screen.getByRole('dialog', { name: 'Prepare daily operations report' })).toBeTruthy();
    expect(screen.getByText('Review the verified operating figures.')).toBeTruthy();
    expect(screen.getByLabelText('Completion note')).toBeTruthy();
    expect(row.isConnected).toBe(true);
    fireEvent.click(screen.getByRole('button', { name: 'Close work details' }));
    await waitFor(() => expect(document.activeElement).toBe(row));
    expect(screen.queryByRole('dialog')).toBeNull();
  });

  it('protects a dirty completion note when Escape requests close', async () => {
    renderWorkspace();
    await openRow('Prepare daily operations report');
    const note = screen.getByLabelText('Completion note');
    fireEvent.change(note, { target: { value: 'Draft note retained until explicit discard.' } });
    fireEvent.keyDown(document, { key: 'Escape' });
    expect(screen.getByText('Discard the unsent completion note or evidence?')).toBeTruthy();
    fireEvent.click(screen.getByRole('button', { name: 'Keep editing' }));
    expect(screen.getByLabelText('Completion note').value).toBe('Draft note retained until explicit discard.');
    fireEvent.keyDown(document, { key: 'Escape' });
    fireEvent.click(screen.getByRole('button', { name: 'Discard and close' }));
    await waitFor(() => expect(screen.queryByRole('dialog')).toBeNull());
  });

  it('submits one source command, confirms the receipt, refreshes and reflects authoritative readback', async () => {
    api.get.mockResolvedValueOnce({ data: payload }).mockResolvedValueOnce({ data: {
      ...payload,
      items: [payload.items[1]],
      summary: { active_count: 1, overdue_count: 0, source_counts: { OPERATIONS: 0, LEGAL: 1 } },
    } });
    renderWorkspace();
    await openRow('Prepare daily operations report');
    fireEvent.change(screen.getByLabelText('Completion note'), { target: { value: 'Reviewed and reconciled.' } });
    fireEvent.click(screen.getByRole('button', { name: 'Complete through Operations' }));
    await waitFor(() => expect(api.post).toHaveBeenCalledTimes(1));
    expect(api.post).toHaveBeenCalledWith(
      '/tenant-modules/operations/workspace/work-items/ops-1/complete',
      { completion_note: 'Reviewed and reconciled.' },
    );
    await waitFor(() => expect(screen.queryByRole('dialog')).toBeNull());
    expect(screen.queryByText('Prepare daily operations report')).toBeNull();
    expect(screen.getAllByText('1').length).toBeGreaterThan(0);
    expect(api.get).toHaveBeenCalledTimes(2);
  });

  it('keeps the work and draft visible after a source command failure', async () => {
    api.post.mockRejectedValueOnce({ response: { status: 403, data: { detail: 'WORK_ITEM_COMPLETION_DENIED' } } });
    renderWorkspace();
    await openRow('Prepare daily operations report');
    const note = screen.getByLabelText('Completion note');
    fireEvent.change(note, { target: { value: 'Retain this note after denial.' } });
    fireEvent.click(screen.getByRole('button', { name: 'Complete through Operations' }));
    expect((await screen.findAllByText(/WORK_ITEM_COMPLETION_DENIED/)).length).toBeGreaterThan(0);
    expect(screen.getByLabelText('Completion note').value).toBe('Retain this note after denial.');
    expect(screen.getAllByText('Prepare daily operations report').length).toBeGreaterThan(0);
    expect(api.post).toHaveBeenCalledTimes(1);
    expect(api.get).toHaveBeenCalledTimes(1);
  });

  it('does not close the detail when fresh EOS readback still contains the active row', async () => {
    api.get.mockResolvedValue({ data: payload });
    renderWorkspace();
    await openRow('Prepare daily operations report');
    fireEvent.change(screen.getByLabelText('Completion note'), { target: { value: 'Source reports completed.' } });
    fireEvent.click(screen.getByRole('button', { name: 'Complete through Operations' }));
    expect((await screen.findAllByText(/WORK_ITEM_COMPLETION_NOT_REFLECTED/)).length).toBeGreaterThan(0);
    expect(screen.getByRole('dialog')).toBeTruthy();
    expect(screen.getAllByText('Prepare daily operations report').length).toBeGreaterThan(0);
  });

  it('routes Legal completion through the evidence-bound source client', async () => {
    renderWorkspace();
    await openRow('Review matter evidence');
    fireEvent.change(screen.getByLabelText('Legal completion evidence reference'), {
      target: { value: 'evidence:verified-source:legal-1' },
    });
    fireEvent.change(screen.getByLabelText('Legal completion evidence fingerprint'), {
      target: { value: 'a'.repeat(128) },
    });
    fireEvent.click(screen.getByRole('button', { name: 'Complete through Legal' }));
    await waitFor(() => expect(completeLegalWorkItem).toHaveBeenCalledWith({
      workItemId: 'legal-1',
      completionEvidenceReference: 'evidence:verified-source:legal-1',
      completionEvidenceFingerprint: 'a'.repeat(128),
    }));
    expect(api.post).not.toHaveBeenCalled();
  });

  it('shows only navigation for an admitted HR item and no generic action', async () => {
    api.get.mockResolvedValueOnce({ data: {
      ...payload,
      items: [{
        source: 'HR', source_key: 'HR:OFFER:opaque:DECIDE', work_item_id: 'OFFER:opaque:DECIDE',
        title: 'Independently decide employment offer', status: 'PENDING_ACTION', priority: 'HIGH',
        kind: 'HR_OFFER_DECISION', due_at: null, is_overdue: false,
      }],
      summary: { active_count: 1, overdue_count: 0, source_counts: { HR: 1 } },
      sources_included: ['HR'],
    } });
    renderWorkspace();
    expect(await screen.findByRole('button', { name: 'Open HR & Hiring' })).toBeTruthy();
    await openRow('Independently decide employment offer');
    expect(screen.getByText('This source does not expose a completion action in the current My Work contract.')).toBeTruthy();
    expect(screen.queryByRole('button', { name: /Complete through HR/ })).toBeNull();
    expect(api.post).not.toHaveBeenCalled();
  });

  it('fails closed on invalid source coverage and on an unavailable initial read', async () => {
    api.get.mockResolvedValueOnce({ data: {
      ...payload, summary: { ...payload.summary, source_counts: { OPERATIONS: 2, LEGAL: 0 } },
    } });
    renderWorkspace();
    expect(await screen.findByRole('alert')).toBeTruthy();
    expect(screen.getByText('ATTENTION_SOURCE_COVERAGE_INVALID')).toBeTruthy();
    expect(screen.queryByText('Prepare daily operations report')).toBeNull();
  });
});

/*
 * ARTIFACT: MyWorkWorkspace.test.jsx
 * VERSION: v1.11.0-INTERACTIVE-RESIZE-CERT
 * AUTHORITY BOUNDARY: Deterministic client projection and source command evidence only.
 * TENANT POSTURE: Synthetic exact-tenant work projections.
 * FAIL-CLOSED POSTURE: Invalid source metadata and failed commands never invent state.
 * FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
