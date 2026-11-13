/**
 * TITLE: WILSY OS Daily Attention Centre Client Contract Tests
 * VERSION: v1.6.0-EXECUTIVE-TRIAGE-INTENT-CERT
 * AUTHORITY: WILSY OS Core Governance
 * EPITOME: Exercises tenant-bound source rendering, EOS-reported coverage,
 *          interactive work triage, source-owned navigation and honest empty states.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/__tests__/components/WilsyDailyAttentionCentre.test.jsx
 * COLLABORATION / OWNERSHIP: WilsyDailyAttentionCentre.jsx and EOS /api/my-work schema.
 * CERTIFICATION / UPDATE DATE: 2026-11-09
 * CHANGELOG: v1.6.0-EXECUTIVE-TRIAGE-INTENT-CERT proves counts and
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
import WilsyDailyAttentionCentre, {
  assertAttentionProjection,
} from '../../components/chrome/WilsyDailyAttentionCentre.jsx';

vi.mock('../../services/api.js', () => ({
  default: { get: vi.fn() },
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
    fireEvent.click(within(dialog).getByRole('button', { name: 'Open in My Work' }));
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
      name: 'Act on Review governed contract in My Work',
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
 * VERSION: v1.6.0-EXECUTIVE-TRIAGE-INTENT-CERT
 * AUTHORITY BOUNDARY: Deterministic component test only.
 * TENANT POSTURE: Synthetic exact-tenant and foreign-tenant cases.
 * FAIL-CLOSED POSTURE: No simulated approvals or silent fallback.
 * FINANCIAL EXECUTION AUTHORITY: Kennel EOS only.
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
