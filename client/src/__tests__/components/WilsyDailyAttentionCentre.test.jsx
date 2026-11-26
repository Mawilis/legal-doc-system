/**
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
 * SECURITY / PRIVACY POSTURE: No credentials or personal information exposed by this metadata repair.
 * TENANT BOUNDARY: Exact tenant scope, membership and entitlements remain server-governed.
 * AUTHORITY BOUNDARY: No new IAM, admission, session or business execution authority is created.
 * FINANCIAL AUTHORITY BOUNDARY: No financial execution; Kennel EOS remains exclusive.
 * TITLE: WILSY OS Daily Attention Centre Client Contract Tests
 * VERSION: v1.11.0-EDGE-RESIZE-FOCUSED-CERT
 * AUTHORITY: WILSY OS Core Governance
 * EPITOME: Exercises tenant-bound source rendering, EOS-reported coverage,
 *          interactive work triage, source-owned navigation and honest empty states.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/__tests__/components/WilsyDailyAttentionCentre.test.jsx
 * COLLABORATION / OWNERSHIP: WilsyDailyAttentionCentre.jsx and EOS /api/my-work schema.
 * CERTIFICATION / UPDATE DATE: 2026-11-16
 * CHANGELOG: v1.11.0-EDGE-RESIZE-FOCUSED-CERT verifies
 *          the accessible edge resize controls and transient dimension
 *          changes independently from the float/dock move command.
 * CHANGELOG: v1.10.0-ACCEPTED-RECEIPT-RECONCILIATION-CERT proves explicit rejection preservation and accepted-but-unverified readback recovery without issuing a second command.
 *            v1.9.0-COMPLETION-READBACK-GATE-CERT proves source receipt, fresh exact-scope reads, projection removal and stale-readback preservation.
 *            v1.8.0-SINGLE-SOURCE-ROW-PRESENTATION-CERT proves an active work
 *            record is not duplicated in the default list by the optional
 *            ranked briefing. Source conflict reconciliation remains intact.
 *            v1.7.0-SOURCE-CONFLICT-RECONCILIATION proves an authenticated
 *            source-create conflict preserves the draft and triggers exact-scope
 *            projection/feed revalidation without claiming persistence.
 *            v1.6.0-EXECUTIVE-TRIAGE-INTENT-CERT proves counts and
 *            source-verified next-action handoff in selected urgency queues.
 *            v1.5.0-OPERATIONAL-ATTENTION-COMMAND-HANDOFF proves
 *            source-filter feedback, visible one-click source-owned commands,
 *            and Operations management from a genuinely empty EOS queue.
 *            v1.4.0-VERIFIED-ZERO-ATTENTION-ACCESSIBILITY certifies
 *            explicit EOS-verified zero work versus unavailable work count
 *            in the accessible bell label; zero never generates an unread
 *            badge. The projection remains source-owned and read-only.
 *            v1.3.0-EOS-SOURCE-COVERAGE verifies filters use only included
 *            sources and distinguishes admitted-empty from no-source coverage.
 *            v1.2.0-EXPLICIT-CALENDAR-CLOSE-CONTRACT asserts visible Close calendar action
 *            and two-stage Escape: calendar first and entire panel second.
 *            v1.1.0-FLOATING-CALENDAR-ACTION-CONTRACT verifies floating,
 *            accessible keyboard movement, calendar, and HR work entry.
 *            v1.0.0-DAILY-ATTENTION-CONTRACT covers authoritative rendering,
 *            overdue/search/source filters, expanded work, retry and denied scope.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
 * SECURITY / PRIVACY POSTURE: Synthetic tenant and work data; no real identities.
 * TENANT BOUNDARY: Foreign tenant and injected item identity are rejected.
 * AUTHORITY BOUNDARY: The client never acknowledges, completes or approves work.
 * FINANCIAL AUTHORITY BOUNDARY: Kennel EOS only.
 */
import React from 'react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { fireEvent, render, screen, waitFor, within } from '@testing-library/react';
import api from '../../services/api.js';
import AuthContext from '../../contexts/authContext.jsx';
import WilsyDailyAttentionCentre, {
  assertAttentionProjection,
} from '../../components/chrome/WilsyDailyAttentionCentre.jsx';

vi.mock('../../services/api.js', () => ({
  default: { get: vi.fn(), post: vi.fn() },
}));

const TENANT = 'WILSYTENANT-TEST-A';

const projection = () => ({
  schema: 'WILSY-OS-UNIFIED-MY-WORK/V1',
  tenant_id: TENANT,
  principal_id: 'WILSYPRINCIPAL-TEST',
  as_of: '2026-11-09T06:00:00+00:00',
  items: [
    {
      source: 'LEGAL',
      source_key: 'LEGAL:LEGAL-1',
      work_item_id: 'LEGAL-1',
      title: 'Review governed contract',
      description: 'Verify source evidence before approving the next action.',
      priority: 'HIGH',
      status: 'OPEN',
      kind: 'TASK',
      due_at: '2026-11-08T06:00:00+00:00',
      is_overdue: true,
    },
    {
      source: 'CRM',
      source_key: 'CRM:CRM-2',
      work_item_id: 'CRM-2',
      title: 'Follow up with customer',
      priority: 'NORMAL',
      status: 'OPEN',
      kind: 'TASK',
      due_at: null,
      is_overdue: false,
    },
  ],
  summary: {
    active_count: 2,
    overdue_count: 1,
    source_counts: { LEGAL: 1, CRM: 1 },
  },
  sources_included: ['LEGAL', 'CRM'],
  authority: { commands_owned_by: 'SOURCE_SERVICES', permits_completion: false },
});

const attentionFeedFor = (payload) => {
  const items = payload.items.map((item) => ({
    id: item.source_key,
    tenantId: payload.tenant_id,
    sourceModule: item.source,
    sourceType: item.kind,
    sourceRecordId: item.work_item_id,
    title: item.title,
    summary: item.description || '',
    priority: item.priority,
    urgencyScore: item.is_overdue ? 90 : 40,
    whyRanked: 'Source priority',
    dueAt: item.due_at,
    slaBreachAt: null,
    assigneeId: payload.principal_id,
    requesterId: payload.principal_id,
    status: item.status,
    actionHints: ['OPEN'],
    deepLink: '/my-work',
    authzScope: 'SOURCE_SERVICE_ONLY',
    updatedAt: payload.as_of,
    isOverdue: item.is_overdue,
  }));
  const included = payload.sources_included;
  return {
    schema: 'WILSY-OS-ATTENTION-FEED/V1', tenantId: payload.tenant_id,
    principalId: payload.principal_id, syncedAt: payload.as_of, view: 'active', items,
    counts: {
      active: payload.summary.active_count, overdue: payload.summary.overdue_count,
      dueToday: 0,
      highPriority: items.filter((item) => ['HIGH', 'CRITICAL'].includes(item.priority)).length,
    },
    sources: included.map((moduleId) => ({
      moduleId, state: payload.summary.source_counts[moduleId] === 0 ? 'empty' : 'ok',
      count: payload.summary.source_counts[moduleId],
    })),
    coverage: {
      admittedSources: included,
      notRepresentedSources: ['OPERATIONS', 'INTELLIGENCE', 'FINANCE', 'PEOPLE'],
      completeEnterpriseCoverage: false,
    },
    filteredTotal: items.length, nextCursor: null,
    authority: { commandsOwnedBy: 'SOURCE_SERVICES', attentionCommandsEnabled: false },
  };
};

const authenticatedFounderTestSession = {
  isAuthenticated: true, authStage: 'AUTHENTICATED', token: 'synthetic-test-session',
  sessionGeneration: 1,
  user: {
    id: 'WILSYPRINCIPAL-TEST', tenantId: TENANT, role: 'OWNER',
    workspaceId: 'TEST-WORKSPACE', businessRole: 'owner',
    membershipRevision: 1, businessRoleRevision: 1,
  },
};

const renderCentre = (props = {}) => {
  const callbacks = {
    onToggle: vi.fn(),
    onClose: vi.fn(),
    onOpenWork: vi.fn(),
  };
  render(<WilsyDailyAttentionCentre
    tenantId={TENANT}
    open
    activeCount={2}
    {...callbacks}
    {...props}
  />);
  return callbacks;
};

beforeEach(() => {
  vi.clearAllMocks();
  api.get.mockResolvedValue({ data: projection() });
});

describe('WILSY daily attention centre', () => {
  it('reconciles an authenticated CRM create conflict and preserves the draft', async () => {
    const currentProjection = projection();
    const principalId = currentProjection.principal_id;
    const sourceItems = currentProjection.items.map((item) => ({
      id: item.source_key,
      tenantId: TENANT,
      sourceModule: item.source,
      sourceType: item.kind,
      sourceRecordId: item.work_item_id,
      title: item.title,
      summary: item.description || '',
      priority: item.priority,
      urgencyScore: item.is_overdue ? 90 : 40,
      whyRanked: 'Source priority',
      dueAt: item.due_at,
      slaBreachAt: null,
      assigneeId: principalId,
      requesterId: principalId,
      status: item.status,
      actionHints: ['OPEN'],
      deepLink: '/my-work',
      authzScope: 'SOURCE_SERVICE_ONLY',
      updatedAt: currentProjection.as_of,
      isOverdue: item.is_overdue,
    }));
    const sourceFeed = {
      schema: 'WILSY-OS-ATTENTION-FEED/V1',
      tenantId: TENANT,
      principalId,
      syncedAt: currentProjection.as_of,
      view: 'active',
      items: sourceItems,
      counts: {
        active: sourceItems.length,
        overdue: sourceItems.filter((item) => item.isOverdue).length,
        dueToday: 0,
        highPriority: sourceItems.filter((item) => ['HIGH', 'CRITICAL'].includes(item.priority)).length,
      },
      sources: ['LEGAL', 'CRM'].map((moduleId) => ({
        moduleId,
        state: 'ok',
        count: sourceItems.filter((item) => item.sourceModule === moduleId).length,
      })),
      coverage: {
        admittedSources: ['LEGAL', 'CRM'],
        notRepresentedSources: ['OPERATIONS', 'INTELLIGENCE', 'FINANCE', 'PEOPLE'],
        completeEnterpriseCoverage: false,
      },
      filteredTotal: sourceItems.length,
      nextCursor: null,
      authority: { commandsOwnedBy: 'SOURCE_SERVICES', attentionCommandsEnabled: false },
    };
    api.get.mockImplementation(async (path) => {
      if (path === '/my-work') return { data: currentProjection };
      if (path === '/attention/feed') return { data: sourceFeed };
      if (path === '/attention/actions/crm') return { data: {
        schema: 'WILSY-OS-ATTENTION-ACTION-AVAILABILITY/V1',
        tenantId: TENANT,
        principalId,
        authority: 'SOURCE_COMMAND_ENDPOINTS_REAUTHORIZE',
        sourceActions: { CRM: ['CREATE', 'COMPLETE'] },
      } };
      throw new Error('Unexpected test read route');
    });
    const conflict = Object.assign(new Error('conflict'), { response: { status: 409 } });
    api.post.mockRejectedValueOnce(conflict);
    const authValue = {
      isAuthenticated: true,
      authStage: 'AUTHENTICATED',
      token: 'synthetic-test-session',
      sessionGeneration: 1,
      user: {
        id: principalId,
        tenantId: TENANT,
        role: 'OWNER',
        workspaceId: 'TEST-WORKSPACE',
        businessRole: 'owner',
        membershipRevision: 1,
        businessRoleRevision: 1,
      },
    };

    render(<AuthContext.Provider value={authValue}>
      <WilsyDailyAttentionCentre tenantId={TENANT} open activeCount={2}
        onToggle={vi.fn()} onClose={vi.fn()} onOpenWork={vi.fn()}/>
    </AuthContext.Provider>);

    expect(await screen.findAllByText('Follow up with customer')).toHaveLength(1);
    fireEvent.click(screen.getByRole('button', { name: 'Create work' }));
    const title = screen.getByPlaceholderText('What needs to be done?');
    fireEvent.change(title, { target: { value: 'Retain this task after conflict' } });
    fireEvent.click(screen.getByRole('button', { name: 'Submit task to EOS' }));

    await waitFor(() => expect(api.post).toHaveBeenCalledTimes(1));
    expect(api.post).toHaveBeenCalledWith('/crm/owner-workspace/work-items', expect.objectContaining({
      title: 'Retain this task after conflict',
      kind: 'TASK',
    }), expect.objectContaining({ headers: { 'Idempotency-Key': expect.any(String) } }));
    expect(await screen.findByText('This work intent conflicts with existing source evidence.')).toBeInTheDocument();
    expect(title).toHaveValue('Retain this task after conflict');
    await waitFor(() => expect(api.get.mock.calls.filter(([path]) => path === '/my-work').length)
      .toBeGreaterThanOrEqual(2));
    expect(document.querySelector('[data-attention-mode="CREATE"]')).toBeInTheDocument();
  });
  it('confirms CRM completion only after fresh unified and attention readbacks remove the item', async () => {
    const active = projection();
    const fresh = {
      ...active,
      items: [active.items[0]],
      summary: { active_count: 1, overdue_count: 1, source_counts: { LEGAL: 1, CRM: 0 } },
    };
    let completionPersisted = false;
    api.get.mockImplementation(async (path) => {
      if (path === '/my-work') return { data: completionPersisted ? fresh : active };
      if (path === '/attention/feed') return {
        data: attentionFeedFor(completionPersisted ? fresh : active),
      };
      if (path === '/attention/actions/crm') return { data: {
        schema: 'WILSY-OS-ATTENTION-ACTION-AVAILABILITY/V1',
        tenantId: TENANT, principalId: 'WILSYPRINCIPAL-TEST',
        authority: 'SOURCE_COMMAND_ENDPOINTS_REAUTHORIZE',
        sourceActions: { CRM: ['COMPLETE'] },
      } };
      throw new Error('Unexpected test read route');
    });
    api.post.mockImplementation(async () => {
      completionPersisted = true;
      return { data: { work_item_id: 'CRM-2', tenant_id: TENANT, status: 'COMPLETED' } };
    });
    render(<AuthContext.Provider value={authenticatedFounderTestSession}>
      <WilsyDailyAttentionCentre tenantId={TENANT} open activeCount={2}
        onToggle={vi.fn()} onClose={vi.fn()} onOpenWork={vi.fn()}/>
    </AuthContext.Provider>);
    await screen.findByText('Follow up with customer');
    fireEvent.click(screen.getByRole('button', { name: 'Complete Follow up with customer' }));
    const evidence = screen.getByPlaceholderText('Record what was completed and the evidence for this decision');
    await waitFor(() => expect(evidence).toHaveFocus());
    fireEvent.change(evidence, { target: { value: 'Customer follow-up completed and recorded' } });
    fireEvent.click(screen.getByRole('button', { name: 'Confirm completion' }));
    await waitFor(() => expect(api.post).toHaveBeenCalledTimes(1));
    expect(api.post).toHaveBeenCalledWith(
      '/crm/owner-workspace/work-items/CRM-2/complete',
      { completion_note: 'Customer follow-up completed and recorded' },
    );
    await waitFor(() => expect(api.get.mock.calls.filter(([path]) => path === '/my-work').length)
      .toBeGreaterThanOrEqual(2));
    await waitFor(() => expect(api.get.mock.calls.filter(([path]) => path === '/attention/feed').length)
      .toBeGreaterThanOrEqual(2));
    await waitFor(() => expect(screen.queryByRole('button', {
      name: 'Complete Follow up with customer',
    })).toBeNull());
  });

  it('retains a valid EOS receipt after failed readback and reconciles without a second command', async () => {
    const active = projection();
    const fresh = {
      ...active,
      items: [active.items[0]],
      summary: { active_count: 1, overdue_count: 1, source_counts: { LEGAL: 1, CRM: 0 } },
    };
    let failFirstPostRead = true;
    let completionPersisted = false;
    api.get.mockImplementation(async (path) => {
      if (path === '/my-work') {
        if (api.post.mock.calls.length > 0 && failFirstPostRead) {
          throw new Error('disposable readback unavailable');
        }
        return { data: completionPersisted ? fresh : active };
      }
      if (path === '/attention/feed') {
        return { data: attentionFeedFor(completionPersisted ? fresh : active) };
      }
      if (path === '/attention/actions/crm') return { data: {
        schema: 'WILSY-OS-ATTENTION-ACTION-AVAILABILITY/V1',
        tenantId: TENANT, principalId: 'WILSYPRINCIPAL-TEST',
        authority: 'SOURCE_COMMAND_ENDPOINTS_REAUTHORIZE',
        sourceActions: { CRM: ['COMPLETE'] },
      } };
      throw new Error('Unexpected test read route');
    });
    api.post.mockResolvedValue({ data: {
      work_item_id: 'CRM-2', tenant_id: TENANT, status: 'COMPLETED',
      completion_note: 'Evidence retained after accepted completion',
    } });
    render(<AuthContext.Provider value={authenticatedFounderTestSession}>
      <WilsyDailyAttentionCentre tenantId={TENANT} open activeCount={2}
        onToggle={vi.fn()} onClose={vi.fn()} onOpenWork={vi.fn()}/>
    </AuthContext.Provider>);
    await screen.findByText('Follow up with customer');
    fireEvent.click(screen.getByRole('button', { name: 'Complete Follow up with customer' }));
    const evidence = screen.getByPlaceholderText('Record what was completed and the evidence for this decision');
    fireEvent.change(evidence, { target: { value: 'Evidence retained after accepted completion' } });
    fireEvent.click(screen.getByRole('button', { name: 'Confirm completion' }));
    expect(await screen.findByText(/EOS accepted completion.*fresh authorized readback could not be verified/)).toBeTruthy();
    const retainedEvidence = screen.getByPlaceholderText('Record what was completed and the evidence for this decision');
    expect(retainedEvidence).toHaveValue('Evidence retained after accepted completion');
    expect(retainedEvidence).toHaveAttribute('readonly');
    expect(screen.getByRole('button', { name: 'Awaiting source readback' })).toBeDisabled();
    expect(api.post).toHaveBeenCalledTimes(1);

    failFirstPostRead = false;
    fireEvent.click(screen.getByRole('button', { name: 'Refresh' }));
    expect(await screen.findByRole('button', { name: 'Reconcile completion' })).toBeEnabled();
    completionPersisted = true;
    fireEvent.click(screen.getByRole('button', { name: 'Reconcile completion' }));
    expect(await screen.findByText('Completion confirmed by EOS and a fresh authorized work readback.')).toBeTruthy();
    expect(api.post).toHaveBeenCalledTimes(1);
    expect(api.get.mock.calls.filter(([path]) => path === '/my-work').length).toBeGreaterThanOrEqual(4);
    expect(api.get.mock.calls.filter(([path]) => path === '/attention/feed').length).toBeGreaterThanOrEqual(4);
    expect(screen.queryByRole('button', { name: 'Complete Follow up with customer' })).toBeNull();
  });

  it('preserves CRM work and reports the actual EOS validation rejection', async () => {
    const active = projection();
    api.get.mockImplementation(async (path) => {
      if (path === '/my-work') return { data: active };
      if (path === '/attention/feed') return { data: attentionFeedFor(active) };
      if (path === '/attention/actions/crm') return { data: {
        schema: 'WILSY-OS-ATTENTION-ACTION-AVAILABILITY/V1',
        tenantId: TENANT, principalId: 'WILSYPRINCIPAL-TEST',
        authority: 'SOURCE_COMMAND_ENDPOINTS_REAUTHORIZE',
        sourceActions: { CRM: ['COMPLETE'] },
      } };
      throw new Error('Unexpected test read route');
    });
    api.post.mockRejectedValue(Object.assign(new Error('rejected'), {
      response: { status: 422, data: { detail: 'COMPLETION_NOTE_INVALID' } },
    }));
    render(<AuthContext.Provider value={authenticatedFounderTestSession}>
      <WilsyDailyAttentionCentre tenantId={TENANT} open activeCount={2}
        onToggle={vi.fn()} onClose={vi.fn()} onOpenWork={vi.fn()}/>
    </AuthContext.Provider>);
    await screen.findByText('Follow up with customer');
    fireEvent.click(screen.getByRole('button', { name: 'Complete Follow up with customer' }));
    const evidence = screen.getByPlaceholderText('Record what was completed and the evidence for this decision');
    fireEvent.change(evidence, { target: { value: 'Retain rejected evidence' } });
    fireEvent.click(screen.getByRole('button', { name: 'Confirm completion' }));
    expect(await screen.findByText('EOS rejected completion evidence (COMPLETION_NOTE_INVALID).')).toBeTruthy();
    expect(screen.getByPlaceholderText('Record what was completed and the evidence for this decision'))
      .toHaveValue('Retain rejected evidence');
    expect(screen.getByRole('button', { name: 'Confirm completion' })).toBeTruthy();
    expect(screen.queryByRole('button', { name: 'Reconcile completion' })).toBeNull();
    expect(api.post).toHaveBeenCalledTimes(1);
  });

  it('displays EOS-authorised work, not fabricated unread notifications', async () => {
    renderCentre();
    expect(await screen.findByText('Review governed contract')).toBeTruthy();
    expect(screen.getByText('Follow up with customer')).toBeTruthy();
    expect(api.get).toHaveBeenCalledWith('/my-work', { forceNetworkRetry: true });
    expect(screen.getByLabelText(/active work items, not unread notifications/)).toBeTruthy();
    expect(screen.queryByText(/3 unread/)).toBeNull();
  });

  it('announces verified zero work distinctly from an unavailable count', async () => {
    const empty = projection();
    empty.items = [];
    empty.summary = {
      active_count: 0, overdue_count: 0,
      source_counts: { LEGAL: 0, CRM: 0 },
    };
    api.get.mockResolvedValueOnce({ data: empty });
    renderCentre({ activeCount: 0 });
    const bell = screen.getByRole('button', { name: 'Open daily attention: 0 active work items' });
    expect(bell).toBeInTheDocument();
    expect(screen.queryByLabelText('0 active work items, not unread notifications')).toBeNull();
    expect(await screen.findByText('No active work in the included sources')).toBeInTheDocument();
    expect(bell).toHaveAttribute('aria-label', 'Open daily attention: 0 active work items');
  });

  it('does not invent a verified zero when no count has been read', () => {
    renderCentre({ open: false, activeCount: null });
    expect(screen.getByRole('button', { name: 'Open daily attention' }))
      .toHaveAttribute('aria-label', 'Open daily attention');
    expect(api.get).not.toHaveBeenCalled();
  });

  it('offers source filters only for sources included by EOS', async () => {
    renderCentre();
    await screen.findByText('Follow up with customer');
    const filter = screen.getByRole('combobox', { name: 'Filter work by source' });
    expect(Array.from(filter.options).map((option) => option.value))
      .toEqual(['ALL', 'LEGAL', 'CRM']);
    expect(within(filter).queryByRole('option', { name: 'Operations' })).toBeNull();
    expect(within(filter).queryByRole('option', { name: 'Intelligence' })).toBeNull();
  });

  it('filters actionable work by overdue, priority, included source and search', async () => {
    renderCentre();
    await screen.findByText('Follow up with customer');
    fireEvent.click(screen.getByRole('button', { name: 'Overdue' }));
    expect(screen.getByText('Review governed contract')).toBeTruthy();
    expect(screen.queryByText('Follow up with customer')).toBeNull();
    fireEvent.click(screen.getByRole('button', { name: 'All work' }));
    fireEvent.change(screen.getByRole('combobox', { name: 'Filter work by source' }), {
      target: { value: 'CRM' },
    });
    expect(screen.getByText('Follow up with customer')).toBeTruthy();
    expect(screen.queryByText('Review governed contract')).toBeNull();
    fireEvent.change(screen.getByRole('combobox', { name: 'Filter work by source' }), {
      target: { value: 'ALL' },
    });
    fireEvent.change(screen.getByRole('searchbox', { name: 'Search authorised work' }), {
      target: { value: 'contract' },
    });
    expect(screen.getByText('Review governed contract')).toBeTruthy();
    expect(screen.queryByText('Follow up with customer')).toBeNull();
  });

  it('explains executive triage and opens the next EOS-owned action', async () => {
    const { onOpenWork } = renderCentre();
    await screen.findByText('Follow up with customer');
    expect(screen.getByRole('group', {name: 'Filter daily attention'})).toBeTruthy();
    expect(screen.getByText('All work: 2 to review')).toBeTruthy();
    expect(screen.getByText(/Next: Review governed contract/)).toBeTruthy();
    fireEvent.click(screen.getByRole('button', {name: 'Overdue'}));
    expect(screen.getByText('Overdue: 1 to review')).toBeTruthy();
    expect(screen.getByText(/Address missed deadlines/)).toBeTruthy();
    fireEvent.click(screen.getByRole('button', {name: 'Work next: Review governed contract'}));
    expect(onOpenWork).toHaveBeenCalledWith(expect.objectContaining({
      source_key: 'LEGAL:LEGAL-1',
    }));
  });

  it('shows an actionable recovery intent when no work matches priority', async () => {
    renderCentre();
    await screen.findByText('Follow up with customer');
    fireEvent.click(screen.getByRole('button', {name: 'Due today'}));
    expect(screen.getByText('Due today: 0 to review')).toBeTruthy();
    expect(screen.getByText(/No matching work in the current selection/)).toBeTruthy();
    expect(screen.queryByRole('button', {name: /^Work next:/})).toBeNull();
    fireEvent.click(screen.getByRole('button', {name: 'Clear filters'}));
    expect(screen.getByText('All work: 2 to review')).toBeTruthy();
  });

  it('expands governed work detail and delegates all commands to My Work', async () => {
    const { onOpenWork } = renderCentre();
    fireEvent.click(await screen.findByRole('button', { name: 'Review governed contract', exact: true }));
    const dialog = screen.getByRole('dialog', { name: 'Daily attention centre' });
    expect(within(dialog).getByText(/Verify source evidence/)).toBeTruthy();
    fireEvent.click(within(dialog).getByRole('button', { name: 'Open authorized task' }));
    expect(onOpenWork).toHaveBeenCalledTimes(1);
    expect(api.get).toHaveBeenCalledTimes(1);
  });

  it('rejects foreign tenant, corrupt summary and fabricated permission authority', () => {
    expect(() => assertAttentionProjection({
      ...projection(), tenant_id: 'OTHER-TENANT',
    }, TENANT)).toThrow('MY_WORK_SCOPE_MISMATCH');
    expect(() => assertAttentionProjection({
      ...projection(), summary: { ...projection().summary, active_count: 100 },
    }, TENANT)).toThrow('ATTENTION_PROJECTION_INVALID');
    expect(() => assertAttentionProjection({
      ...projection(), authority: { commands_owned_by: 'SOURCE_SERVICES', permits_completion: true },
    }, TENANT)).toThrow('ATTENTION_PROJECTION_INVALID');
    const corrupted = projection();
    corrupted.items[0].tenant_id = 'OTHER-TENANT';
    expect(() => assertAttentionProjection(corrupted, TENANT)).toThrow('ATTENTION_ITEM_INVALID');
  });

  it('does not silently represent denial or an unavailable source as an empty queue', async () => {
    api.get.mockRejectedValueOnce(new Error('source unavailable'));
    renderCentre();
    expect(await screen.findByRole('alert')).toBeTruthy();
    expect(screen.getByText(/No cached or invented work is shown/)).toBeTruthy();
    fireEvent.click(screen.getByRole('button', { name: 'Retry authorised read' }));
    expect(await screen.findByText('Review governed contract')).toBeTruthy();
    await waitFor(() => expect(api.get).toHaveBeenCalledTimes(2));
  });

  it('floats and docks the panel with accessible keyboard repositioning', async () => {
    renderCentre();
    await screen.findByText('Review governed contract');
    fireEvent.click(screen.getByRole('button', { name: 'Float daily attention panel' }));
    const panel = screen.getByRole('dialog', { name: 'Daily attention centre' });
    expect(panel.getAttribute('data-floating')).toBe('true');
    const before = Number.parseFloat(panel.style.left);
    fireEvent.keyDown(screen.getByRole('button', {
      name: 'Move daily attention panel with pointer or arrow keys',
    }), { key: 'ArrowRight' });
    expect(Number.parseFloat(panel.style.left)).toBeGreaterThanOrEqual(before);
    fireEvent.click(screen.getByRole('button', { name: 'Dock daily attention panel' }));
    expect(panel.getAttribute('data-floating')).toBe('false');
  });

  it('resizes daily attention through accessible edge controls', async () => {
    renderCentre();
    await screen.findByText('Review governed contract');
    const panel = screen.getByRole('dialog', { name: 'Daily attention centre' });
    fireEvent.keyDown(screen.getByRole('separator', {
      name: 'Resize daily attention right edge',
    }), { key: 'ArrowRight' });
    expect(Number.parseFloat(panel.style.width)).toBeGreaterThan(0);
    fireEvent.keyDown(screen.getByRole('separator', {
      name: 'Resize daily attention bottom edge',
    }), { key: 'ArrowDown' });
    expect(Number.parseFloat(panel.style.height)).toBeGreaterThan(0);
    expect(screen.getByRole('separator', {
      name: 'Resize daily attention top edge',
    })).toBeTruthy();
  });

  it('turns the footer calendar into an actionable EOS deadline view', async () => {
    renderCentre();
    await screen.findByText('Review governed contract');
    fireEvent.click(screen.getByRole('button', { name: 'Open work deadline calendar' }));
    expect(screen.getByRole('group', { name: 'Choose work deadline date' })).toBeTruthy();
    expect(screen.getByRole('tab', { name: 'Calendar' }).getAttribute('aria-selected')).toBe('true');
    fireEvent.click(screen.getByRole('button', { name: 'Close calendar and return to work list' }));
    expect(screen.queryByRole('group', { name: 'Choose work deadline date' })).toBeNull();
    expect(screen.getByText('Follow up with customer')).toBeTruthy();
    expect(screen.queryByRole('button', { name: 'Close calendar and return to work list' })).toBeNull();
  });

  it('Escape dismisses the calendar before the entire attention panel', async () => {
    const { onClose } = renderCentre();
    await screen.findByText('Review governed contract');
    fireEvent.click(screen.getByRole('button', { name: 'Open work deadline calendar' }));
    expect(screen.getByRole('button', { name: 'Close calendar and return to work list' })).toBeTruthy();
    fireEvent.keyDown(document, { key: 'Escape' });
    expect(screen.getByRole('tab', { name: 'Work list' }).getAttribute('aria-selected')).toBe('true');
    expect(onClose).not.toHaveBeenCalled();
    fireEvent.keyDown(document, { key: 'Escape' });
    expect(onClose).toHaveBeenCalledTimes(1);
  });

  it('distinguishes an admitted empty queue from no source projection', async () => {
    api.get.mockResolvedValueOnce({ data: {
      ...projection(),
      items: [],
      summary: { active_count: 0, overdue_count: 0, source_counts: { LEGAL: 0, CRM: 0 } },
    } });
    const onOpenWorkforce = vi.fn();
    renderCentre({ onOpenWorkforce });
    expect(await screen.findByText('No active work in the included sources')).toBeTruthy();
    expect(screen.getByText('EOS returned no active work from Legal, CRM.')).toBeTruthy();
    expect(screen.queryByRole('button', { name: 'Open HR & workforce duties' })).toBeNull();
    expect(onOpenWorkforce).not.toHaveBeenCalled();
  });

  it('does not claim an empty queue when EOS included no work source', async () => {
    api.get.mockResolvedValueOnce({ data: {
      ...projection(),
      items: [],
      summary: { active_count: 0, overdue_count: 0, source_counts: {} },
      sources_included: [],
    } });
    renderCentre();
    expect(await screen.findByText('No work source was included in this session')).toBeTruthy();
    expect(screen.getByText(/not evidence that every business queue is empty/)).toBeTruthy();
  });

  it('makes every authorised task actionable without a hidden expansion', async () => {
    const { onOpenWork } = renderCentre();
    await screen.findByText('Review governed contract');
    fireEvent.click(screen.getByRole('button', {
      name: 'Open task Review governed contract',
    }));
    expect(onOpenWork).toHaveBeenCalledWith(expect.objectContaining({
      source_key: 'LEGAL:LEGAL-1',
    }));
    expect(api.get).toHaveBeenCalledTimes(1);
  });

  it('opens real Operations work management for an admitted empty queue', async () => {
    const empty = projection();
    empty.items = [];
    empty.sources_included = ['OPERATIONS'];
    empty.summary = {
      active_count: 0, overdue_count: 0, source_counts: { OPERATIONS: 0 },
    };
    api.get.mockResolvedValueOnce({ data: empty });
    const onOpenOperations = vi.fn();
    renderCentre({ onOpenOperations, activeCount: 0 });
    expect(await screen.findByText('No active work in the included sources')).toBeTruthy();
    fireEvent.change(screen.getByRole('combobox', { name: 'Filter work by source' }), {
      target: { value: 'OPERATIONS' },
    });
    expect(screen.getByText(/EOS has no active work in the admitted sources.*Showing Operations/)).toBeTruthy();
    fireEvent.click(screen.getByRole('button', {
      name: /Create or manage Operations work/,
    }));
    expect(onOpenOperations).toHaveBeenCalledTimes(1);
    expect(api.get).toHaveBeenCalledTimes(1);
  });

  it('never presents an Operations management action without EOS Operations coverage', async () => {
    const onOpenOperations = vi.fn();
    renderCentre({ onOpenOperations });
    await screen.findByText('Review governed contract');
    expect(screen.queryByRole('button', { name: 'Manage Operations' })).toBeNull();
    expect(screen.queryByRole('button', { name: /Create or manage Operations work/ })).toBeNull();
  });

  it('never requests a tenant work queue for a system services workspace', async () => {
    renderCentre({ systemServicesWorkspace: true });
    expect(await screen.findByRole('alert')).toBeTruthy();
    expect(api.get).not.toHaveBeenCalled();
  });
});

/*
 * ARTIFACT: WilsyDailyAttentionCentre.test.jsx
 * VERSION: v1.11.0-EDGE-RESIZE-FOCUSED-CERT
 * AUTHORITY BOUNDARY: Deterministic component test only.
 * TENANT POSTURE: Synthetic exact-tenant and foreign-tenant cases.
 * FAIL-CLOSED POSTURE: No simulated approvals or silent fallback.
 * FINANCIAL EXECUTION AUTHORITY: Kennel EOS only.
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
