/**
 * TITLE: WILSY OS Headquarters Daily Brief Client Contract Tests
 * VERSION: v1.2.0-SHARED-PROJECTION-CONTRACT
 * AUTHORITY: Wilsy OS Core Governance
 * EPITOME: Certifies shared source-metadata validation, exact tenant projection,
 *          truthful empty states, and item-specific read-only navigation.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/__tests__/components/WilsyHeadquartersDailyBrief.test.jsx
 * COLLABORATION / OWNERSHIP: WilsyHeadquartersDailyBrief.jsx, the shared client
 *                            projection contract, and EOS /api/my-work.
 * CERTIFICATION / UPDATE DATE: 2026-11-09
 * CHANGELOG: v1.2.0-SHARED-PROJECTION-CONTRACT verifies selected item context
 *            reaches the callback and Headquarters uses the canonical EOS source
 *            coverage validator.
 *            v1.1.0-AUTHORISED-SOURCE-COVERAGE verifies that source options
 *            follow the exact EOS source set, source counts reconcile to rows,
 *            and no included source is distinct from a verified empty queue.
 *            v1.0.0-DAILY-BRIEF-CLIENT-CERTIFICATE covered source projection,
 *            invalid tenant, failed read, retry and action navigation.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
 * SECURITY / PRIVACY POSTURE: Synthetic source data only; no live service access.
 * TENANT BOUNDARY: Tests exact matching tenant with foreign-scope rejection.
 * AUTHORITY BOUNDARY: Client may only navigate, not complete work.
 * FINANCIAL AUTHORITY BOUNDARY: Kennel EOS only.
 */
import React from 'react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { fireEvent, render, screen, waitFor, within } from '@testing-library/react';
import api from '../../services/api.js';
import WilsyHeadquartersDailyBrief from '../../components/workspaces/WilsyHeadquartersDailyBrief.jsx';

vi.mock('../../services/api.js', () => ({
  default: { get: vi.fn() },
}));

const TENANT = 'TENANT-DAILY-TEST';
const valid = () => ({
  schema: 'WILSY-OS-UNIFIED-MY-WORK/V1',
  tenant_id: TENANT,
  principal_id: 'PRINCIPAL-DAILY-TEST',
  as_of: '2026-11-09T10:00:00+00:00',
  items: [
    {
      source: 'OPERATIONS', source_key: 'OPERATIONS:SHIP-1',
      work_item_id: 'SHIP-1', title: 'Clear dispatch backlog',
      status: 'OPEN', priority: 'HIGH',
      due_at: '2026-11-08T10:00:00+00:00', is_overdue: true,
    },
    {
      source: 'CRM', source_key: 'CRM:FOLLOW-2',
      work_item_id: 'FOLLOW-2', title: 'Follow up on renewal',
      status: 'OPEN', priority: 'NORMAL',
      due_at: null, is_overdue: false,
    },
  ],
  summary: {
    active_count: 2,
    overdue_count: 1,
    source_counts: { OPERATIONS: 1, CRM: 1 },
  },
  sources_included: ['OPERATIONS', 'CRM'],
  authority: { commands_owned_by: 'SOURCE_SERVICES', permits_completion: false },
});

beforeEach(() => {
  vi.clearAllMocks();
  api.get.mockResolvedValue({ data: valid() });
});

describe('Headquarters daily execution', () => {
  it('renders source-backed work and offers only sources included by EOS', async () => {
    const onOpenWork = vi.fn();
    render(<WilsyHeadquartersDailyBrief tenantId={TENANT} onOpenWork={onOpenWork}/>);
    const section = screen.getByRole('region', { name: 'Headquarters daily execution' });
    expect(await within(section).findByText('Clear dispatch backlog')).toBeTruthy();
    expect(within(section).getByText('Follow up on renewal')).toBeTruthy();
    expect(within(section).getByText(/Included: Operations, CRM/)).toBeTruthy();
    expect(api.get).toHaveBeenCalledWith('/my-work', { forceNetworkRetry: true });

    const sourceFilter = within(section).getByRole('combobox', {
      name: 'Filter headquarters by source',
    });
    expect(Array.from(sourceFilter.options).map((option) => option.value)).toEqual([
      'ALL', 'OPERATIONS', 'CRM',
    ]);
    expect(within(section).queryByRole('option', { name: 'Legal' })).toBeNull();
    expect(within(section).queryByRole('option', { name: 'Intelligence' })).toBeNull();

    fireEvent.click(within(section).getByRole('button', {
      name: 'Open authorised work action for Clear dispatch backlog',
    }));
    expect(onOpenWork).toHaveBeenCalledTimes(1);
    expect(onOpenWork).toHaveBeenCalledWith(expect.objectContaining({
      source: 'OPERATIONS',
      source_key: 'OPERATIONS:SHIP-1',
      work_item_id: 'SHIP-1',
    }));
  });

  it('filters overdue work and searches within included sources', async () => {
    render(<WilsyHeadquartersDailyBrief tenantId={TENANT} onOpenWork={vi.fn()}/>);
    await screen.findByText('Clear dispatch backlog');
    fireEvent.click(screen.getByRole('button', { name: 'Overdue' }));
    expect(screen.queryByText('Follow up on renewal')).toBeNull();
    fireEvent.click(screen.getByRole('button', { name: 'All work' }));
    fireEvent.change(screen.getByRole('searchbox', { name: 'Search headquarters work' }), {
      target: { value: 'renewal' },
    });
    expect(screen.getByText('Follow up on renewal')).toBeTruthy();
    expect(screen.queryByText('Clear dispatch backlog')).toBeNull();
  });

  it('distinguishes an empty included queue from no source projection', async () => {
    api.get.mockResolvedValueOnce({ data: {
      ...valid(),
      items: [],
      summary: {
        active_count: 0,
        overdue_count: 0,
        source_counts: { OPERATIONS: 0, CRM: 0 },
      },
    } });
    const { unmount } = render(
      <WilsyHeadquartersDailyBrief tenantId={TENANT} onOpenWork={vi.fn()}/>,
    );
    expect(await screen.findByText('No active work in the included sources')).toBeTruthy();
    expect(screen.getByText('EOS returned no active work from Operations, CRM.')).toBeTruthy();
    unmount();

    api.get.mockResolvedValueOnce({ data: {
      ...valid(),
      items: [],
      summary: { active_count: 0, overdue_count: 0, source_counts: {} },
      sources_included: [],
    } });
    render(<WilsyHeadquartersDailyBrief tenantId={TENANT} onOpenWork={vi.fn()}/>);
    expect(await screen.findByText('No work source was included in this session')).toBeTruthy();
    expect(screen.getByText(/not evidence that every business queue is empty/)).toBeTruthy();
  });

  it('rejects divergent source metadata without rendering work or metrics', async () => {
    api.get.mockResolvedValueOnce({ data: {
      ...valid(),
      sources_included: ['LEGAL'],
      summary: {
        active_count: 2,
        overdue_count: 1,
        source_counts: { LEGAL: 2 },
      },
    } });
    render(<WilsyHeadquartersDailyBrief tenantId={TENANT} onOpenWork={vi.fn()}/>);
    expect(await screen.findByRole('alert')).toBeTruthy();
    expect(screen.queryByText('Clear dispatch backlog')).toBeNull();
    expect(screen.queryByText('Follow up on renewal')).toBeNull();
  });

  it('rejects foreign tenant read and offers retry without invented metrics', async () => {
    api.get.mockResolvedValueOnce({ data: { ...valid(), tenant_id: 'FOREIGN' } });
    render(<WilsyHeadquartersDailyBrief tenantId={TENANT} onOpenWork={vi.fn()}/>);
    expect(await screen.findByRole('alert')).toBeTruthy();
    expect(screen.queryByText('Clear dispatch backlog')).toBeNull();
    fireEvent.click(screen.getByRole('button', { name: 'Retry source read' }));
    expect(await screen.findByText('Clear dispatch backlog')).toBeTruthy();
    await waitFor(() => expect(api.get).toHaveBeenCalledTimes(2));
  });

  it('never fetches business data when no authenticated tenant is available', async () => {
    render(<WilsyHeadquartersDailyBrief tenantId={null} onOpenWork={vi.fn()}/>);
    expect(await screen.findByRole('alert')).toBeTruthy();
    expect(api.get).not.toHaveBeenCalled();
  });
});

/*
 * ARTIFACT: WilsyHeadquartersDailyBrief.test.jsx
 * VERSION: v1.2.0-SHARED-PROJECTION-CONTRACT
 * AUTHORITY BOUNDARY: Deterministic client test evidence only.
 * TENANT POSTURE: Synthetic exact-scope and foreign-scope checks.
 * FAIL-CLOSED POSTURE: Divergent source metadata cannot render a queue.
 * FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
