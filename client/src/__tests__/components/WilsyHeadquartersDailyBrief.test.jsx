/**
 * TITLE: WILSY OS Headquarters Daily Brief Unit Contract Tests
 * VERSION: v1.0.0-DAILY-BRIEF-CLIENT-CERTIFICATE
 * AUTHORITY: Wilsy OS Core Governance
 * EPITOME: Verifies the source-backed headquarters work briefing, filters,
 *          canonical My Work navigation, and fail-closed tenant behaviour.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/__tests__/components/WilsyHeadquartersDailyBrief.test.jsx
 * COLLABORATION / OWNERSHIP: WilsyHeadquartersDailyBrief.jsx and EOS My Work.
 * CERTIFICATION / UPDATE DATE: 2026-11-09
 * CHANGELOG: v1.0.0-DAILY-BRIEF-CLIENT-CERTIFICATE adds deterministic source
 *            projection, invalid tenant, failed read and interaction coverage.
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
  summary: { active_count: 2, overdue_count: 1, source_counts: { OPERATIONS: 1, CRM: 1 } },
  sources_included: ['OPERATIONS','CRM'],
  authority: { commands_owned_by: 'SOURCE_SERVICES', permits_completion: false },
});

beforeEach(() => {
  vi.clearAllMocks();
  api.get.mockResolvedValue({ data: valid() });
});

describe('Headquarters daily execution', () => {
  it('renders live source counts and authorised actions instead of demo KPIs', async () => {
    const onOpenWork = vi.fn();
    render(<WilsyHeadquartersDailyBrief tenantId={TENANT} onOpenWork={onOpenWork}/>);
    const section = screen.getByRole('region', { name: 'Headquarters daily execution' });
    expect(await within(section).findByText('Clear dispatch backlog')).toBeTruthy();
    expect(within(section).getByText('Follow up on renewal')).toBeTruthy();
    expect(within(section).getByText(/2 authorised sources/)).toBeTruthy();
    expect(api.get).toHaveBeenCalledWith('/my-work', { forceNetworkRetry: true });
    fireEvent.click(within(section).getByRole('button', { name: 'Open authorised work action for Clear dispatch backlog' }));
    expect(onOpenWork).toHaveBeenCalledTimes(1);
  });

  it('filters overdue work and searches within admitted sources', async () => {
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
 * VERSION: v1.0.0-DAILY-BRIEF-CLIENT-CERTIFICATE
 * AUTHORITY BOUNDARY: Client test evidence only.
 * TENANT POSTURE: Synthetic exact-scope and foreign-scope checks.
 * FAIL-CLOSED POSTURE: No fake metrics on errors.
 * FINANCIAL EXECUTION AUTHORITY: Kennel EOS only.
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
