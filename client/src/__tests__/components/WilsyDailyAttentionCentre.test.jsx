/**
 * TITLE: WILSY OS Daily Attention Centre Client Contract Tests
 * VERSION: v1.1.0-FLOATING-CALENDAR-ACTION-CONTRACT
 * AUTHORITY: WILSY OS Core Governance
 * EPITOME: Exercises tenant-bound source rendering, interactive work triage,
 *          source-owned navigation and fail-closed missing/invalid projections.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/__tests__/components/WilsyDailyAttentionCentre.test.jsx
 * COLLABORATION / OWNERSHIP: WilsyDailyAttentionCentre.jsx and EOS /my-work schema.
 * CERTIFICATION / UPDATE DATE: 2026-11-09
 * CHANGELOG: v1.1.0-FLOATING-CALENDAR-ACTION-CONTRACT verifies floating,
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
  summary: { active_count: 2, overdue_count: 1 },
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
  it('displays authorised business work, not fabricated unread notifications', async () => {
    renderCentre();
    expect(await screen.findByText('Review governed contract')).toBeTruthy();
    expect(screen.getByText('Follow up with customer')).toBeTruthy();
    expect(api.get).toHaveBeenCalledWith('/my-work', { forceNetworkRetry: true });
    expect(screen.getByLabelText(/active work items, not unread notifications/)).toBeTruthy();
    expect(screen.queryByText(/3 unread/)).toBeNull();
  });

  it('filters actionable work by overdue, priority, source and search', async () => {
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

  it('expands governed work detail and delegates all commands to My Work', async () => {
    const { onOpenWork } = renderCentre();
    fireEvent.click(await screen.findByRole('button', { name: /Review governed contract/ }));
    const dialog = screen.getByRole('dialog', { name: 'Daily attention centre' });
    expect(within(dialog).getByText(/Verify source evidence/)).toBeTruthy();
    fireEvent.click(within(dialog).getByRole('button', { name: 'Open in My Work' }));
    expect(onOpenWork).toHaveBeenCalledTimes(1);
    expect(api.get).toHaveBeenCalledTimes(1);
  });

  it('rejects foreign tenant, corrupt summary and fabricated permission authority', () => {
    expect(() => assertAttentionProjection({
      ...projection(), tenant_id: 'OTHER-TENANT',
    }, TENANT)).toThrow('ATTENTION_PROJECTION_INVALID');
    expect(() => assertAttentionProjection({
      ...projection(), summary: { active_count: 100, overdue_count: 1 },
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
    fireEvent.click(screen.getByRole('tab', { name: 'Work list' }));
    expect(screen.getByText('Follow up with customer')).toBeTruthy();
  });

  it('opens the existing HR workflow from a genuine empty queue', async () => {
    api.get.mockResolvedValueOnce({ data: {
      ...projection(), items: [], summary: { active_count: 0, overdue_count: 0 },
    } });
    const onOpenWorkforce = vi.fn();
    renderCentre({ onOpenWorkforce });
    await screen.findByText('No active work in authorised sources');
    fireEvent.click(screen.getByRole('button', { name: 'Open HR & workforce duties' }));
    expect(onOpenWorkforce).toHaveBeenCalledTimes(1);
  });

  it('never requests a tenant work queue for a system services workspace', async () => {
    renderCentre({ systemServicesWorkspace: true });
    expect(await screen.findByRole('alert')).toBeTruthy();
    expect(api.get).not.toHaveBeenCalled();
  });
});

/*
 * ARTIFACT: WilsyDailyAttentionCentre.test.jsx
 * VERSION: v1.1.0-FLOATING-CALENDAR-ACTION-CONTRACT
 * AUTHORITY BOUNDARY: Deterministic component test only.
 * TENANT POSTURE: Synthetic exact-tenant and foreign-tenant cases.
 * FAIL-CLOSED POSTURE: No simulated approvals or silent fallback.
 * FINANCIAL EXECUTION AUTHORITY: Kennel EOS only.
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
