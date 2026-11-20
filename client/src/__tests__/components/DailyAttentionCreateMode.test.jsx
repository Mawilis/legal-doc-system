/**
 * TITLE: WILSY OS Daily Attention create-mode regression certificate
 * VERSION: v1.3.0-EXACT-CRM-INITIAL-STATUS-CERT
 * AUTHORITY: Client interaction evidence only; EOS source services own work state.
 * EPITOME: Certifies the focused Create mode, keyboard/focus return, failed-form
 *          retention, exact source-command arguments, and projection-only display.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/__tests__/components/DailyAttentionCreateMode.test.jsx
 * COLLABORATION / OWNERSHIP: Vitest and Testing Library; EOS command clients and source registries remain authoritative.
 * CERTIFICATION / UPDATE DATE: 2026-11-20
 * CHANGELOG: v1.3.0-EXACT-CRM-INITIAL-STATUS-CERT pins the existing canonical
 *            CRM OPEN initial status and exact supported command field set.
 * CHANGELOG: v1.2.0-COMPACT-LIST-AND-SORT-CERT proves the compact single-row
 *            filter controls and deterministic supported sort modes while
 *            retaining the exclusive Create workflow.
 *            v1.1.0-SUBMIT-VALIDATION-CERT proves title validation,
 *            removal of the duplicate CREATE badge, and inline safe source-field errors.
 *            v1.0.0-EXCLUSIVE-CREATE-MODE-ACCEPTANCE covers LIST/CREATE mode
 *            separation, form focus, cancel/Escape, source-supported command
 *            fields, no optimistic record insertion, and validated list readback.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
 * SECURITY / PRIVACY POSTURE: Synthetic test records only; no credentials or HTTP requests.
 * TENANT BOUNDARY: All fixture items use one isolated synthetic tenant/principal.
 * AUTHORITY BOUNDARY: Create callbacks are test doubles; source commands remain EOS-owned.
 * FINANCIAL AUTHORITY BOUNDARY: No approval, payment, or settlement operation is exercised.
 */
import React from 'react';
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';
import DailyAttentionWorkspace from '../../components/attention/DailyAttentionWorkspace.jsx';

afterEach(() => {
  cleanup();
  vi.restoreAllMocks();
});

const TENANT = 'daily-attention-create-tenant';
const PRINCIPAL = 'daily-attention-create-principal';

function feed(items = []) {
  return {
    schema: 'WILSY-OS-ATTENTION-FEED/V1',
    tenantId: TENANT,
    principalId: PRINCIPAL,
    syncedAt: '2026-11-15T10:00:00+00:00',
    view: 'active',
    items,
    counts: {
      active: items.length,
      overdue: items.filter((item) => item.isOverdue).length,
      dueToday: 0,
      highPriority: items.filter((item) => ['HIGH', 'CRITICAL'].includes(item.priority)).length,
    },
    sources: [{ moduleId: 'CRM', state: items.length ? 'ok' : 'empty', count: items.length }],
    coverage: {
      admittedSources: ['CRM'],
      notRepresentedSources: ['LEGAL', 'OPERATIONS', 'INTELLIGENCE', 'FINANCE', 'PEOPLE'],
      completeEnterpriseCoverage: false,
    },
    filteredTotal: items.length,
    nextCursor: null,
    authority: { commandsOwnedBy: 'SOURCE_SERVICES', attentionCommandsEnabled: false },
  };
}

function crmWork(workItemId, title) {
  return {
    id: `CRM:${workItemId}`,
    tenantId: TENANT,
    sourceModule: 'CRM',
    sourceType: 'TASK',
    sourceRecordId: workItemId,
    title,
    summary: 'Persisted owner-commercial CRM work',
    priority: 'HIGH',
    urgencyScore: 80,
    whyRanked: 'High source priority',
    dueAt: '2026-11-16T12:00:00+00:00',
    slaBreachAt: null,
    assigneeId: PRINCIPAL,
    requesterId: PRINCIPAL,
    status: 'OPEN',
    actionHints: ['OPEN'],
    deepLink: '/my-work',
    authzScope: 'SOURCE_SERVICE_ONLY',
    updatedAt: '2026-11-15T10:00:00+00:00',
    isOverdue: false,
  };
}

function props(overrides = {}) {
  return {
    feed: feed(),
    calendarItems: [],
    filter: 'ALL',
    setFilter: vi.fn(),
    source: 'ALL',
    setSource: vi.fn(),
    query: '',
    setQuery: vi.fn(),
    onRefresh: vi.fn(),
    onOpenWork: vi.fn(),
    onOpenOperations: vi.fn(),
    onOpenWorkforce: vi.fn(),
    onLoadMore: vi.fn(),
    loadingMore: false,
    pageError: '',
    authorisedActions: { CRM: ['CREATE', 'COMPLETE'] },
    onCreateWork: vi.fn().mockResolvedValue(true),
    ...overrides,
  };
}

function openCreate() {
  fireEvent.click(screen.getByRole('button', { name: 'Create work' }));
}

describe('Daily Attention LIST and CREATE modes', () => {
  it('opens a prominent form and removes list controls, metrics, source evidence, and footer', async () => {
    render(<DailyAttentionWorkspace {...props({ feed: feed([crmWork('crm-existing', 'Existing CRM work')]) })}/>);

    openCreate();

    const workspace = document.querySelector('[data-attention-production-ui="true"]');
    expect(workspace).toHaveAttribute('data-attention-mode', 'CREATE');
    expect(screen.getByRole('form', { name: 'Create source work' })).toBeInTheDocument();
    expect(screen.queryByText('Create', { exact: true })).not.toBeInTheDocument();
    expect(screen.queryByRole('combobox', { name: 'Filter daily attention' })).not.toBeInTheDocument();
    expect(screen.queryByRole('group', { name: 'Severity of loaded work' })).not.toBeInTheDocument();
    expect(screen.queryByRole('searchbox', { name: 'Search authorised work' })).not.toBeInTheDocument();
    expect(screen.queryByRole('group', { name: 'Verified current-source workload' })).not.toBeInTheDocument();
    expect(screen.queryByText(/loaded · .*matching in last verified view/)).not.toBeInTheDocument();
    await waitFor(() => expect(screen.getByPlaceholderText('What needs to be done?')).toHaveFocus());
  });

  it('cancel and Escape return to LIST and restore focus to the opener', async () => {
    const { rerender } = render(<DailyAttentionWorkspace {...props()}/>);
    const trigger = screen.getByRole('button', { name: 'Create work' });
    fireEvent.click(trigger);
    fireEvent.click(screen.getByRole('button', { name: 'Cancel' }));

    await waitFor(() => expect(screen.getByRole('button', { name: 'Create work' })).toHaveFocus());
    expect(document.querySelector('[data-attention-mode="LIST"]')).toBeInTheDocument();
    expect(screen.getByRole('combobox', { name: 'Filter daily attention' })).toBeInTheDocument();

    fireEvent.click(screen.getByRole('button', { name: 'Create work' }));
    fireEvent.keyDown(screen.getByPlaceholderText('What needs to be done?'), { key: 'Escape' });
    await waitFor(() => expect(screen.getByRole('button', { name: 'Create work' })).toHaveFocus());
    expect(document.querySelector('[data-attention-mode="LIST"]')).toBeInTheDocument();
  });

  it('submits only CRM-supported fields once and shows work only after projection readback', async () => {
    const create = vi.fn().mockResolvedValue(true);
    const initial = props({ onCreateWork: create });
    const { rerender } = render(<DailyAttentionWorkspace {...initial}/>);
    openCreate();
    fireEvent.change(screen.getByPlaceholderText('What needs to be done?'), {
      target: { value: 'Call supplier about updated delivery date' },
    });
    fireEvent.change(screen.getByPlaceholderText('Outcome, owner context or instructions'), {
      target: { value: 'Confirm the revised delivery window with the supplier.' },
    });
    fireEvent.change(screen.getByRole('combobox', { name: 'Priority' }), {
      target: { value: 'HIGH' },
    });
    fireEvent.change(screen.getByLabelText('Deadline (optional)'), {
      target: { value: '2026-11-16T14:30' },
    });
    fireEvent.click(screen.getByRole('button', { name: 'Submit task to EOS' }));

    await waitFor(() => expect(create).toHaveBeenCalledTimes(1));
    const [source, command, idempotencyKey] = create.mock.calls[0];
    expect(source).toBe('CRM');
    expect(command).toMatchObject({
      title: 'Call supplier about updated delivery date',
      description: 'Confirm the revised delivery window with the supplier.',
      priority: 'HIGH',
    });
    expect(command.due_at).toEqual(expect.any(String));
    expect(command.initial_status).toBe('OPEN');
    expect(Object.keys(command).sort()).toEqual(['description', 'due_at', 'initial_status', 'priority', 'title']);
    expect(idempotencyKey).toMatch(/^[0-9a-f-]{36}$/i);
    expect(document.querySelector('[data-attention-mode="LIST"]')).toBeInTheDocument();
    expect(screen.queryByRole('button', { name: 'Inspect Call supplier about updated delivery date' })).not.toBeInTheDocument();

    rerender(<DailyAttentionWorkspace {...initial} feed={feed([
      crmWork('owk_persisted-owner-work', 'Call supplier about updated delivery date'),
    ])}/>);
    expect(await screen.findByRole('button', {
      name: 'Inspect Call supplier about updated delivery date',
    })).toBeInTheDocument();
    expect(screen.getByLabelText('Verified current-source workload')).toHaveTextContent('Active1');
    fireEvent.change(screen.getByRole('combobox', { name: 'Filter daily attention' }), {
      target: { value: 'HIGH' },
    });
    expect(initial.setFilter).toHaveBeenCalledWith('HIGH');
  });

  it('sorts only validated fields with a deterministic source-record tie break', () => {
    const items = [
      { ...crmWork('task-b', 'Task 10'), priority: 'LOW', urgencyScore: 20,
        dueAt: '2026-11-17T10:00:00+00:00' },
      { ...crmWork('task-a', 'Task 2'), priority: 'CRITICAL', urgencyScore: 90,
        dueAt: '2026-11-16T10:00:00+00:00' },
      { ...crmWork('task-c', 'Task 1'), priority: 'NORMAL', urgencyScore: 40,
        dueAt: null },
    ];
    render(<DailyAttentionWorkspace {...props({ feed: feed(items) })}/>);
    const inspectNames = () => screen.getAllByRole('button', { name: /^Inspect / })
      .map((button) => button.getAttribute('aria-label'));
    const sort = screen.getByRole('combobox', { name: 'Sort attention work' });

    fireEvent.change(sort, { target: { value: 'TITLE' } });
    expect(inspectNames()).toEqual([
      'Inspect Task 1', 'Inspect Task 2', 'Inspect Task 10',
    ]);
    fireEvent.change(sort, { target: { value: 'DUE_ASC' } });
    expect(inspectNames()).toEqual([
      'Inspect Task 2', 'Inspect Task 10', 'Inspect Task 1',
    ]);
    fireEvent.change(sort, { target: { value: 'PRIORITY_DESC' } });
    expect(inspectNames()).toEqual([
      'Inspect Task 2', 'Inspect Task 1', 'Inspect Task 10',
    ]);
    expect(screen.queryByRole('option', { name: /Recently (created|updated)/ })).not.toBeInTheDocument();
  });


  it('shows title validation and safe source field errors beside the controls', async () => {
    const create = vi.fn().mockResolvedValue(false);
    const view = render(<DailyAttentionWorkspace {...props({ onCreateWork: create })}/>);
    openCreate();
    const title = screen.getByPlaceholderText('What needs to be done?');
    fireEvent.click(screen.getByRole('button', { name: 'Submit task to EOS' }));
    expect(title).toHaveAttribute('aria-invalid', 'true');
    expect(screen.getByText('Enter a work title.')).toBeInTheDocument();
    expect(create).not.toHaveBeenCalled();
    fireEvent.change(title, { target: { value: 'x' } });

    view.rerender(<DailyAttentionWorkspace {...props({
      creationError: 'EOS rejected: title (string_too_short).',
      onCreateWork: create,
    })}/>);
    expect(title).toHaveAttribute('aria-invalid', 'true');
    expect(screen.getByText('Enter a valid title.')).toBeInTheDocument();
    expect(screen.getByText('EOS rejected: title (string_too_short).', { exact: true })).toBeInTheDocument();
  });

  it('retains form values after a rejected command and does not insert a work item', async () => {
    const create = vi.fn().mockResolvedValue(false);
    render(<DailyAttentionWorkspace {...props({
      onCreateWork: create,
      creationError: 'EOS denied this task creation.',
    })}/>);
    openCreate();
    const title = screen.getByPlaceholderText('What needs to be done?');
    const description = screen.getByPlaceholderText('Outcome, owner context or instructions');
    fireEvent.change(title, { target: { value: 'Denied CRM request' } });
    fireEvent.change(description, { target: { value: 'Retain this explanation for correction.' } });
    fireEvent.click(screen.getByRole('button', { name: 'Submit task to EOS' }));

    await waitFor(() => expect(create).toHaveBeenCalledTimes(1));
    expect(document.querySelector('[data-attention-mode="CREATE"]')).toBeInTheDocument();
    expect(title).toHaveValue('Denied CRM request');
    expect(description).toHaveValue('Retain this explanation for correction.');
    expect(screen.getByRole('alert')).toHaveTextContent('EOS denied this task creation.');
    expect(screen.queryByRole('button', { name: 'Inspect Denied CRM request' })).not.toBeInTheDocument();
  });
});

/*
 * ARTIFACT: WILSY OS Daily Attention create-mode regression certificate
 * VERSION: v1.3.0-EXACT-CRM-INITIAL-STATUS-CERT
 * AUTHORITY BOUNDARY: Client interaction evidence only; EOS owns persisted work.
 * TENANT POSTURE: Synthetic tenant only; no cross-tenant data is used.
 * FAIL-CLOSED POSTURE: Invalid and failed commands never add client-created records.
 * FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively; no execution occurs here.
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
