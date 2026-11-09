/**
 * TITLE: WILSY OS Authorised Work Calendar Component Certification
 * VERSION: v1.0.0-CALENDAR-DATE-ACTION-CERTIFICATE
 * AUTHORITY: Wilsy OS Core Governance
 * EPITOME: Validates calendar month navigation, sourced work due dates,
 *          undated work and handoff to source-owned completion workflows.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/__tests__/components/WilsyWorkDeadlineCalendar.test.jsx
 * COLLABORATION / OWNERSHIP: WilsyWorkDeadlineCalendar.jsx.
 * CERTIFICATION / UPDATE DATE: 2026-11-09
 * CHANGELOG: v1.0.0-CALENDAR-DATE-ACTION-CERTIFICATE adds actionable calendar
 *            coverage without mocking a nonexistent meeting or shift service.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
 * SECURITY / PRIVACY POSTURE: Synthetic in-memory work items only.
 * TENANT BOUNDARY: Parent supplies EOS-validated current-session items.
 * AUTHORITY BOUNDARY: No client completion, time or assignment mutation.
 * FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively.
 */
import React from 'react';
import { describe, expect, it, vi } from 'vitest';
import { fireEvent, render, screen } from '@testing-library/react';
import WilsyWorkDeadlineCalendar, {
  localWorkDay, monthWorkDays,
} from '../../components/chrome/WilsyWorkDeadlineCalendar.jsx';

const dueToday = new Date();
dueToday.setHours(13, 0, 0, 0);
const dueNextMonth = new Date(dueToday.getFullYear(), dueToday.getMonth() + 1, 13, 12);
const items = [
  {
    source: 'OPERATIONS', source_key: 'OPERATIONS:DAILY-1', work_item_id: 'DAILY-1',
    title: 'Approve supplier delivery', description: 'Verify authorised dispatch evidence',
    priority: 'HIGH', status: 'OPEN', is_overdue: false, due_at: dueToday.toISOString(),
  },
  {
    source: 'LEGAL', source_key: 'LEGAL:NEXT-2', work_item_id: 'NEXT-2',
    title: 'Review next month contract', priority: 'NORMAL',
    status: 'OPEN', is_overdue: false, due_at: dueNextMonth.toISOString(),
  },
  {
    source: 'CRM', source_key: 'CRM:UNDATED-3', work_item_id: 'UNDATED-3',
    title: 'Contact account owner', priority: 'NORMAL',
    status: 'OPEN', is_overdue: false, due_at: null,
  },
];

describe('EOS source-backed deadline calendar', () => {
  it('provides complete Monday-first month cells without losing month boundary dates', () => {
    const month = new Date(2026, 10, 1);
    const cells = monthWorkDays(month);
    expect(cells.length % 7).toBe(0);
    expect(cells.some((day) => day.currentMonth && day.key === '2026-11-01')).toBe(true);
    expect(cells.some((day) => day.currentMonth && day.key === '2026-11-30')).toBe(true);
    expect(localWorkDay(null)).toBeNull();
  });

  it('shows the authorised due-day agenda and delegates completion', () => {
    const onOpenWork = vi.fn();
    render(<WilsyWorkDeadlineCalendar items={items} onOpenWork={onOpenWork}/>);
    expect(screen.getByRole('group', { name: 'Choose work deadline date' })).toBeTruthy();
    expect(screen.getByText('Approve supplier delivery')).toBeTruthy();
    expect(screen.getByText('Verify authorised dispatch evidence')).toBeTruthy();
    fireEvent.click(screen.getByRole('button', { name: 'Review and complete in My Work' }));
    expect(onOpenWork).toHaveBeenCalledWith(items[0]);
  });

  it('moves to the following month and selects an actual deadline', () => {
    render(<WilsyWorkDeadlineCalendar items={items} onOpenWork={vi.fn()}/>);
    fireEvent.click(screen.getByRole('button', { name: 'Next month' }));
    const label = dueNextMonth.toLocaleDateString(undefined, { dateStyle: 'full' });
    fireEvent.click(screen.getByRole('button', { name: label + ': 1 due work items' }));
    expect(screen.getByText('Review next month contract')).toBeTruthy();
  });

  it('provides undated tasks and a useful HR entry when the due-day has no work', () => {
    const onOpenWorkforce = vi.fn();
    render(<WilsyWorkDeadlineCalendar items={items} onOpenWork={vi.fn()} onOpenWorkforce={onOpenWorkforce}/>);
    fireEvent.click(screen.getByRole('button', { name: 'Without due date (1)' }));
    expect(screen.getByText('Contact account owner')).toBeTruthy();
    fireEvent.click(screen.getByRole('button', { name: 'Next month' }));
    fireEvent.click(screen.getByRole('button', { name: 'Without due date (1)' }));
    const noWorkDay = new Date(dueNextMonth.getFullYear(), dueNextMonth.getMonth(), 15);
    fireEvent.click(screen.getByRole('button', {
      name: noWorkDay.toLocaleDateString(undefined, {dateStyle:'full'}) + ': 0 due work items',
    }));
    fireEvent.click(screen.getByRole('button', { name: 'Open HR & workforce duties' }));
    expect(onOpenWorkforce).toHaveBeenCalledTimes(1);
  });

  it('does not fabricate events in a source-verified empty queue', () => {
    render(<WilsyWorkDeadlineCalendar items={[]} onOpenWork={vi.fn()}/>);
    expect(screen.getByText(/No authorised work items have a due date/)).toBeTruthy();
    expect(screen.queryByText('Approve supplier delivery')).toBeNull();
  });
});
/*
 * ARTIFACT: WilsyWorkDeadlineCalendar.test.jsx
 * VERSION: v1.0.0-CALENDAR-DATE-ACTION-CERTIFICATE
 * AUTHORITY BOUNDARY: Deterministic read-only client certification.
 * TENANT POSTURE: Synthetic source-shaped work.
 * FAIL-CLOSED POSTURE: Empty source produces no invented work.
 * FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
