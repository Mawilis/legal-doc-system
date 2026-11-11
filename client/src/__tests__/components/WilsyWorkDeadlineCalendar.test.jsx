/**
 * TITLE: WILSY OS Authorised Work Calendar Component Certification
 * VERSION: v1.2.0-CIVIL-DATE-DAY-WEEK-CERTIFICATE
 * AUTHORITY: Wilsy OS Core Governance
 * EPITOME: Certify source-owned action handoff, civil dates, local instants,
 *          DST boundaries, keyboard focus, day/week/month views and navigation.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/__tests__/components/WilsyWorkDeadlineCalendar.test.jsx
 * COLLABORATION / OWNERSHIP: WilsyWorkDeadlineCalendar.jsx; client certification CI.
 * CERTIFICATION / UPDATE DATE: 2026-11-10
 * CHANGELOG: v1.2.0-CIVIL-DATE-DAY-WEEK-CERTIFICATE proves single-day and
 *            Monday-first week views use the selected dates and preserve
 *            source-owned agenda handoff, while retaining month-view coverage.
 *            v1.1.0-CIVIL-DATE-KEYBOARD-CERTIFICATE retains all original cases
 *            and adds malformed-date, date-only, timezone/DST, roving focus,
 *            month/year boundary, overdue and live source-readback coverage.
 *            v1.0.0-CALENDAR-DATE-ACTION-CERTIFICATE added actionable calendar
 *            coverage without inventing a meeting or shift service.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
 * SECURITY / PRIVACY POSTURE: Synthetic in-memory work only; no login or secrets.
 * TENANT BOUNDARY: Parent supplies validated current-session work records.
 * AUTHORITY BOUNDARY: Component tests cannot certify IAM or successful MFA.
 * FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively.
 */
import React from 'react';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { fireEvent, render, screen, within } from '@testing-library/react';
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
const datedWeekItems = [
  {
    ...items[0], source_key: 'OPERATIONS:WEEK-9', work_item_id: 'WEEK-9',
    title: 'Prepare Monday dispatch', due_at: '2026-11-09',
  },
  {
    ...items[1], source_key: 'LEGAL:WEEK-10', work_item_id: 'WEEK-10',
    title: 'Review Tuesday contract', due_at: '2026-11-10T12:00:00+02:00',
  },
];

const dateButton = (year, month, day, count = 0) => screen.getByRole('button', {
  name: new Date(year, month - 1, day, 12).toLocaleDateString(undefined, { dateStyle: 'full' })
    + ': ' + count + ' due work items',
});
const freezeToday = () => {
  vi.useFakeTimers();
  vi.setSystemTime(new Date(2026, 10, 9, 12));
};
afterEach(() => vi.useRealTimers());

describe('EOS source-backed deadline calendar', () => {
  it('provides complete Monday-first month cells without losing month boundary dates', () => {
    const cells = monthWorkDays(new Date(2026, 10, 1));
    expect(cells.length % 7).toBe(0);
    expect(cells[0].date.getDay()).toBe(1);
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

  it('preserves date-only values without converting them through UTC', () => {
    expect(localWorkDay('2026-11-09')).toBe('2026-11-09');
    expect(localWorkDay('2028-02-29')).toBe('2028-02-29');
    expect(localWorkDay('0099-02-28')).toBe('0099-02-28');
  });

  it.each([
    '2026-02-29', '2026-02-30', '2026-13-01', '2026-00-01', '2026-01-00',
    '2026-11-09T12:00:00', '2026-02-30T12:00:00Z', 'not-a-date',
    '', true, 1730000000000, {}, new Date('invalid'),
  ])('rejects malformed or unqualified deadline %s', (value) => {
    expect(localWorkDay(value)).toBeNull();
  });

  it('projects offset-qualified instants into the actual viewer timezone across DST', () => {
    const zone = Intl.DateTimeFormat().resolvedOptions().timeZone;
    const expectations = {
      'Africa/Johannesburg': ['2026-03-08', '2026-03-08', '2026-11-01'],
      'America/Los_Angeles': ['2026-03-07', '2026-03-08', '2026-10-31'],
      'Europe/London': ['2026-03-08', '2026-03-08', '2026-11-01'],
      UTC: ['2026-03-08', '2026-03-08', '2026-11-01'],
    };
    // The certificate is invoked separately under these real process timezones.
    expect(Object.hasOwn(expectations, zone)).toBe(true);
    expect([
      localWorkDay('2026-03-08T07:30:00Z'),
      localWorkDay('2026-03-08T10:30:00Z'),
      localWorkDay('2026-11-01T06:30:00Z'),
    ]).toEqual(expectations[zone]);
  });

  it('shows a date-only agenda without inventing a midnight due time', () => {
    freezeToday();
    render(<WilsyWorkDeadlineCalendar items={[{...items[0], due_at: '2026-11-09'}]} onOpenWork={vi.fn()}/>);
    expect(dateButton(2026, 11, 9, 1).getAttribute('aria-pressed')).toBe('true');
    expect(screen.getByText('Date only · no due time')).toBeTruthy();
    expect(screen.getByText('Approve supplier delivery')).toBeTruthy();
  });

  it('shows the selected day and advances its agenda by one actual civil date', () => {
    freezeToday();
    render(<WilsyWorkDeadlineCalendar items={datedWeekItems} onOpenWork={vi.fn()}/>);
    fireEvent.click(screen.getByRole('button', { name: 'Day view' }));
    const dayGroup = within(screen.getByRole('group', { name: 'Choose work deadline date' }));
    expect(dayGroup.getAllByRole('button')).toHaveLength(1);
    expect(dateButton(2026, 11, 9, 1).getAttribute('aria-pressed')).toBe('true');
    expect(screen.getByText('Prepare Monday dispatch')).toBeTruthy();
    fireEvent.click(screen.getByRole('button', { name: 'Next day' }));
    expect(dateButton(2026, 11, 10, 1).getAttribute('aria-pressed')).toBe('true');
    expect(screen.getByText('Review Tuesday contract')).toBeTruthy();
    expect(screen.queryByText('Prepare Monday dispatch')).toBeNull();
  });

  it('shows one Monday-first week and advances by seven days without losing counts', () => {
    freezeToday();
    render(<WilsyWorkDeadlineCalendar items={datedWeekItems} onOpenWork={vi.fn()}/>);
    fireEvent.click(screen.getByRole('button', { name: 'Week view' }));
    const dayGroup = within(screen.getByRole('group', { name: 'Choose work deadline date' }));
    expect(dayGroup.getAllByRole('button')).toHaveLength(7);
    expect(dateButton(2026, 11, 9, 1)).toBeTruthy();
    expect(dateButton(2026, 11, 15, 0)).toBeTruthy();
    fireEvent.click(screen.getByRole('button', { name: 'Next week' }));
    expect(dayGroup.getAllByRole('button')).toHaveLength(7);
    expect(dateButton(2026, 11, 16, 0)).toBeTruthy();
    expect(dateButton(2026, 11, 22, 0)).toBeTruthy();
  });

  it('uses one tab stop and moves real focus by day and week', () => {
    freezeToday();
    render(<WilsyWorkDeadlineCalendar items={[]} onOpenWork={vi.fn()}/>);
    const days = within(screen.getByRole('group', {name: 'Choose work deadline date'}));
    expect(days.getAllByRole('button').filter((button) => button.tabIndex === 0)).toHaveLength(1);
    dateButton(2026, 11, 9).focus();
    fireEvent.keyDown(dateButton(2026, 11, 9), {key: 'ArrowRight'});
    expect(document.activeElement).toBe(dateButton(2026, 11, 10));
    expect(dateButton(2026, 11, 10).getAttribute('aria-pressed')).toBe('true');
    fireEvent.keyDown(document.activeElement, {key: 'ArrowDown'});
    expect(document.activeElement).toBe(dateButton(2026, 11, 17));
    fireEvent.keyDown(document.activeElement, {key: 'Home'});
    expect(document.activeElement).toBe(dateButton(2026, 11, 16));
    fireEvent.keyDown(document.activeElement, {key: 'End'});
    expect(document.activeElement).toBe(dateButton(2026, 11, 22));
  });

  it('moves focus across month and year boundaries with keyboard navigation', () => {
    freezeToday();
    render(<WilsyWorkDeadlineCalendar items={[]} onOpenWork={vi.fn()}/>);
    fireEvent.click(dateButton(2026, 11, 30));
    fireEvent.keyDown(dateButton(2026, 11, 30), {key: 'ArrowRight'});
    expect(document.activeElement).toBe(dateButton(2026, 12, 1));
    fireEvent.keyDown(document.activeElement, {key: 'PageDown', shiftKey: true});
    expect(document.activeElement).toBe(dateButton(2027, 12, 1));
    fireEvent.keyDown(document.activeElement, {key: 'PageUp', shiftKey: true});
    expect(document.activeElement).toBe(dateButton(2026, 12, 1));
    fireEvent.click(screen.getByRole('button', {name: 'Today'}));
    expect(dateButton(2026, 11, 9).getAttribute('aria-pressed')).toBe('true');
  });

  it('clamps month navigation to the actual final day and retains keyboard focus', () => {
    freezeToday();
    render(<WilsyWorkDeadlineCalendar items={[]} onOpenWork={vi.fn()}/>);
    fireEvent.click(screen.getByRole('button', {name: 'Previous month'}));
    fireEvent.click(dateButton(2026, 10, 31));
    fireEvent.keyDown(dateButton(2026, 10, 31), {key: 'PageDown'});
    expect(document.activeElement).toBe(dateButton(2026, 11, 30));
    fireEvent.keyDown(document.activeElement, {key: 'PageDown'});
    fireEvent.keyDown(document.activeElement, {key: 'PageDown'});
    fireEvent.keyDown(document.activeElement, {key: 'PageDown'});
    expect(document.activeElement).toBe(dateButton(2027, 2, 28));
  });

  it('derives overdue agenda only from EOS declarations and refreshes after source changes', () => {
    const onOpenWork = vi.fn();
    const overdue = {...items[0], is_overdue: true};
    const props = {items: [overdue, items[1]], onOpenWork};
    const {rerender} = render(<WilsyWorkDeadlineCalendar {...props}/>);
    fireEvent.click(screen.getByRole('button', {name: 'Overdue (1)'}));
    expect(screen.getByText(overdue.title)).toBeTruthy();
    expect(screen.queryByText(items[1].title)).toBeNull();
    fireEvent.click(screen.getByRole('button', {name: 'Review and complete in My Work'}));
    expect(onOpenWork).toHaveBeenCalledWith(overdue);
    rerender(<WilsyWorkDeadlineCalendar {...props} items={[items[1]]}/>);
    expect(screen.queryByText(overdue.title)).toBeNull();
    expect(screen.getByText('No authorised work items are overdue.')).toBeTruthy();
  });

  it('preserves leap-month grids and rejects invalid month input', () => {
    expect(monthWorkDays(new Date(2028, 1, 1)).filter((cell) => cell.currentMonth)).toHaveLength(29);
    expect(monthWorkDays(new Date('invalid'))).toEqual([]);
    expect(monthWorkDays(null)).toEqual([]);
  });
});

/*
 * ARTIFACT: WilsyWorkDeadlineCalendar.test.jsx
 * VERSION: v1.2.0-CIVIL-DATE-DAY-WEEK-CERTIFICATE
 * AUTHORITY BOUNDARY: Deterministic component certification, not runtime IAM.
 * TENANT POSTURE: Synthetic source-shaped work; no tenant persistence.
 * FAIL-CLOSED POSTURE: Invalid dates reject; source removal removes agenda work.
 * FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
