/**
 * TITLE: WILSY OS Authorised Work Deadline Calendar
 * VERSION: v1.1.0-CIVIL-DATES-KEYBOARD-AGENDA
 * AUTHORITY: Wilsy OS Core Governance
 * EPITOME: Project source-owned work deadlines with civil-date preservation,
 *          local instant display, keyboard date navigation and actionable agendas.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/components/chrome/WilsyWorkDeadlineCalendar.jsx
 * COLLABORATION / OWNERSHIP: WilsyDailyAttentionCentre validates EOS /my-work;
 *                            MyWorkWorkspace delegates commands to EOS sources.
 * CERTIFICATION / UPDATE DATE: 2026-11-09
 * CHANGELOG: v1.1.0-CIVIL-DATES-KEYBOARD-AGENDA preserves date-only deadlines
 *            without UTC conversion, rejects malformed date values, provides
 *            roving date focus and day/week/month/year keyboard navigation,
 *            and exposes an agenda of source-declared overdue work.
 *            v1.0.0-SOURCE-OWNED-WORK-DEADLINES added month/day navigation,
 *            dated and undated task agendas and source-owned action handoff.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; WCAG keyboard access.
 * SECURITY / PRIVACY POSTURE: In-memory projection; no logging or persistence.
 * TENANT BOUNDARY: Parent supplies only validated current-session EOS work.
 * AUTHORITY BOUNDARY: Calendar selection is presentation. EOS independently
 *                     authorizes every source command. Overdue is source truth.
 * FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively executes funds.
 */
import React, { useId, useLayoutEffect, useMemo, useRef, useState } from 'react';
import { ArrowRight, ChevronLeft, ChevronRight, Clock3 } from 'lucide-react';

const SOURCES = Object.freeze({
  LEGAL: 'Legal', OPERATIONS: 'Operations', INTELLIGENCE: 'Intelligence', CRM: 'CRM',
});
const CIVIL_DATE = /^(\d{4})-(\d{2})-(\d{2})$/;
const INSTANT = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(?::\d{2}(?:\.\d{1,9})?)?(?:Z|[+-]\d{2}:\d{2})$/;

// Noon anchors calendar arithmetic away from DST transitions at midnight.
const civilDate = (year, month, day) => {
  const date = new Date(0);
  date.setFullYear(year, month, day);
  date.setHours(12, 0, 0, 0);
  return date;
};
const parseCivilDate = (value) => {
  const parts = CIVIL_DATE.exec(value);
  if (!parts) return null;
  const [, year, month, day] = parts.map(Number);
  const date = civilDate(year, month - 1, day);
  return date.getFullYear() === year && date.getMonth() === month - 1
    && date.getDate() === day ? date : null;
};
const workDate = (value) => {
  if (value instanceof Date) return Number.isNaN(value.getTime()) ? null : value;
  if (typeof value !== 'string') return null;
  if (CIVIL_DATE.test(value)) return parseCivilDate(value);
  if (!INSTANT.test(value) || !parseCivilDate(value.slice(0, 10))) return null;
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? null : date;
};

/**
 * @description Return the viewer's day for an instant; preserve civil dates.
 * @collaboration Calendar grouping, month cells and calendar certificates.
 * @institutional Dates without times must never acquire an invented UTC instant.
 * @param {Date|string|null} value A Date, offset-qualified ISO instant or YYYY-MM-DD.
 * @returns {string|null} Civil day key, or null for absent/malformed input.
 * No tenant lookup, authority, mutation, idempotency or transaction is owned here.
 */
export function localWorkDay(value) {
  const date = workDate(value);
  if (!date) return null;
  return [String(date.getFullYear()).padStart(4, '0'),
    String(date.getMonth() + 1).padStart(2, '0'),
    String(date.getDate()).padStart(2, '0')].join('-');
}

/**
 * @description Build complete Monday-first calendar weeks around a month.
 * @collaboration Calendar rendering and deterministic date certificates.
 * @institutional Calendar cells describe dates, never new persisted events.
 * @param {Date} month Any valid Date in the requested local month.
 * @returns {Object[]} Day keys, local noon Dates and current-month indicators.
 * Invalid input returns no cells; no tenant data, transaction or authority changes.
 */
export function monthWorkDays(month) {
  if (!(month instanceof Date) || Number.isNaN(month.getTime())) return [];
  const first = civilDate(month.getFullYear(), month.getMonth(), 1);
  const pad = (first.getDay() + 6) % 7;
  const length = civilDate(first.getFullYear(), first.getMonth() + 1, 0).getDate();
  return Array.from({ length: Math.ceil((pad + length) / 7) * 7 }, (_, index) => {
    const date = civilDate(first.getFullYear(), first.getMonth(), index + 1 - pad);
    return { key: localWorkDay(date), date, currentMonth: date.getMonth() === first.getMonth() };
  });
}

const shiftedMonth = (date, delta) => {
  const first = civilDate(date.getFullYear(), date.getMonth() + delta, 1);
  const last = civilDate(first.getFullYear(), first.getMonth() + 1, 0).getDate();
  return civilDate(first.getFullYear(), first.getMonth(), Math.min(date.getDate(), last));
};
const deadlineTime = (value) => {
  if (!value) return 'No due time';
  if (typeof value === 'string' && CIVIL_DATE.test(value)) return 'Date only · no due time';
  return workDate(value)?.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    || 'Due time unavailable';
};

/**
 * @description Render authorized deadlines and delegate actions to owning sources.
 * @collaboration Daily Attention owns dialog, dismissal, refresh and tenant scope;
 * My Work receives the original selected source record and reauthorizes commands.
 * @institutional A calendar cannot manufacture scheduling, leave or approval truth.
 * @param {Object} props Current-session source projection and navigation callbacks.
 * @param {Object[]} props.items EOS-validated active work; never a notification inbox.
 * @param {Function} props.onOpenWork Navigate to the source-governed work item.
 * @param {Function} [props.onOpenWorkforce] Navigate to the governed HR workspace.
 * @returns {JSX.Element} Navigable calendar and dated, undated or overdue agenda.
 * No persistence, permissions, financial authority or transaction is created.
 */
export default function WilsyWorkDeadlineCalendar({ items, onOpenWork, onOpenWorkforce }) {
  const [month, setMonth] = useState(() => civilDate(new Date().getFullYear(), new Date().getMonth(), 1));
  const [selected, setSelected] = useState(() => localWorkDay(new Date()));
  const [focusedDay, setFocusedDay] = useState(() => localWorkDay(new Date()));
  const dayButtons = useRef(new Map());
  const pendingFocus = useRef(false);
  const helpId = useId();
  const cells = useMemo(() => monthWorkDays(month), [month]);
  const focusKey = cells.some((cell) => cell.key === focusedDay)
    ? focusedDay : cells.find((cell) => cell.currentMonth)?.key;
  const counts = useMemo(() => {
    const byDay = new Map();
    for (const item of items) {
      const day = localWorkDay(item.due_at);
      if (day) byDay.set(day, (byDay.get(day) || 0) + 1);
    }
    return byDay;
  }, [items]);
  const undated = items.filter((item) => item.due_at === null || item.due_at === undefined);
  const overdue = items.filter((item) => item.is_overdue === true);
  const agenda = selected === null ? undated : selected === 'OVERDUE' ? overdue
    : items.filter((item) => localWorkDay(item.due_at) === selected);

  useLayoutEffect(() => {
    if (pendingFocus.current) {
      dayButtons.current.get(focusKey)?.focus();
      pendingFocus.current = false;
    }
  }, [focusKey, month]);

  const chooseDate = (date, focus = false) => {
    const key = localWorkDay(date);
    pendingFocus.current = focus;
    setFocusedDay(key);
    setSelected(key);
    if (date.getMonth() !== month.getMonth() || date.getFullYear() !== month.getFullYear()) {
      setMonth(civilDate(date.getFullYear(), date.getMonth(), 1));
    }
  };
  const changeMonth = (delta) => {
    const current = parseCivilDate(focusKey);
    chooseDate(shiftedMonth(current, delta));
  };
  const handleDateKey = (event, date) => {
    const offsets = { ArrowLeft: -1, ArrowRight: 1, ArrowUp: -7, ArrowDown: 7 };
    let target;
    if (Object.hasOwn(offsets, event.key)) {
      target = civilDate(date.getFullYear(), date.getMonth(), date.getDate() + offsets[event.key]);
    } else if (event.key === 'Home' || event.key === 'End') {
      const weekday = (date.getDay() + 6) % 7;
      target = civilDate(date.getFullYear(), date.getMonth(), date.getDate()
        + (event.key === 'Home' ? -weekday : 6 - weekday));
    } else if (event.key === 'PageUp' || event.key === 'PageDown') {
      target = shiftedMonth(date, (event.key === 'PageUp' ? -1 : 1) * (event.shiftKey ? 12 : 1));
    } else return;
    event.preventDefault();
    chooseDate(target, true);
  };
  const dateTitle = selected === null ? 'Work without a due date'
    : selected === 'OVERDUE' ? 'Overdue work'
      : parseCivilDate(selected).toLocaleDateString(undefined, { dateStyle: 'full' });

  return (
    <div aria-label="EOS work deadline calendar" className="space-y-3">
      <p className="text-xs leading-5 text-slate-400">
        Select a day to review and act on your authorised work deadlines.
      </p>
      <p className="text-[11px] leading-5 text-slate-400">
        Times shown in {Intl.DateTimeFormat().resolvedOptions().timeZone}.
        Dates without a time stay on their recorded day.
      </p>
      <div className="flex items-center justify-between gap-2">
        <button type="button" aria-label="Previous month" onClick={() => changeMonth(-1)}
          className="rounded-lg border border-white/10 p-2 text-slate-200 hover:bg-white/10">
          <ChevronLeft size={16}/>
        </button>
        <h3 aria-live="polite" className="font-semibold text-white">
          {month.toLocaleDateString(undefined, { month: 'long', year: 'numeric' })}
        </h3>
        <button type="button" aria-label="Next month" onClick={() => changeMonth(1)}
          className="rounded-lg border border-white/10 p-2 text-slate-200 hover:bg-white/10">
          <ChevronRight size={16}/>
        </button>
      </div>
      <p id={helpId} className="sr-only">
        Arrow keys move by day or week. Home and End move within the week.
        Page Up and Page Down change month; hold Shift to change year.
      </p>
      <div className="grid grid-cols-7 gap-1 text-center text-[10px] text-slate-400" aria-hidden="true">
        {['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'].map((name) => <span key={name}>{name}</span>)}
      </div>
      <div role="group" aria-label="Choose work deadline date" aria-describedby={helpId}
        className="grid grid-cols-7 gap-1">
        {cells.map(({ key, date, currentMonth }) => {
          const count = counts.get(key) || 0;
          return (
            <button key={key} type="button" aria-pressed={selected === key}
              ref={(node) => { if (node) dayButtons.current.set(key, node); else dayButtons.current.delete(key); }}
              tabIndex={focusKey === key ? 0 : -1}
              aria-current={localWorkDay(new Date()) === key ? 'date' : undefined}
              aria-label={date.toLocaleDateString(undefined, { dateStyle: 'full' })
                + ': ' + count + ' due work items'}
              onFocus={() => setFocusedDay(key)}
              onKeyDown={(event) => handleDateKey(event, date)}
              onClick={() => chooseDate(date)}
              className={'flex min-h-11 flex-col items-center justify-center rounded-lg border text-xs transition '
                + 'focus-visible:outline focus-visible:outline-2 focus-visible:outline-amber-300 '
                + (selected === key ? 'border-amber-300 bg-amber-300/15 text-amber-100'
                  : currentMonth ? 'border-white/10 text-slate-200 hover:bg-white/10'
                    : 'border-transparent text-slate-500 hover:bg-white/10')}>
              <span>{date.getDate()}</span>
              {count > 0 && <span className="mt-0.5 text-[10px] font-bold text-amber-300">{count} due</span>}
            </button>
          );
        })}
      </div>
      <div className="flex flex-wrap gap-2 border-b border-white/10 pb-3">
        <button type="button" onClick={() => chooseDate(new Date())}
          className="rounded-lg border border-white/15 px-3 py-1.5 text-xs text-slate-200 hover:bg-white/10">Today</button>
        <button type="button" onClick={() => setSelected(null)} aria-pressed={selected === null}
          className="rounded-lg border border-white/15 px-3 py-1.5 text-xs text-amber-100 hover:bg-white/10">
          Without due date ({undated.length})
        </button>
        <button type="button" onClick={() => setSelected('OVERDUE')} aria-pressed={selected === 'OVERDUE'}
          className="rounded-lg border border-white/15 px-3 py-1.5 text-xs text-rose-200 hover:bg-white/10">
          Overdue ({overdue.length})
        </button>
      </div>
      <h4 aria-live="polite" className="text-sm font-semibold text-white">{dateTitle}</h4>
      {agenda.length === 0 ? (
        <div className="rounded-lg border border-white/10 p-4">
          <p className="text-xs leading-5 text-slate-400">
            {selected === null ? 'No authorised work items are without a due date.'
              : selected === 'OVERDUE' ? 'No authorised work items are overdue.'
                : 'No authorised work items have a due date on this day.'}
          </p>
          {onOpenWorkforce && (
            <button type="button" onClick={onOpenWorkforce}
              className="mt-3 inline-flex items-center gap-1.5 text-xs font-semibold text-amber-200 hover:underline">
              Open HR & workforce duties <ArrowRight size={13}/>
            </button>
          )}
        </div>
      ) : agenda.map((item) => (
        <article key={item.source_key} className="rounded-xl border border-white/10 bg-white/[0.035] p-3">
          <div className="flex items-center justify-between gap-2 text-[10px] uppercase tracking-wide">
            <span className="font-semibold text-amber-200">{SOURCES[item.source]}</span>
            <span className={item.is_overdue ? 'text-rose-300' : 'text-slate-400'}>
              {item.is_overdue ? 'Overdue' : item.priority + ' priority'}
            </span>
          </div>
          <h5 className="mt-2 text-sm font-semibold text-white">{item.title}</h5>
          {item.description && <p className="mt-1 break-words text-xs text-slate-400">{item.description}</p>}
          <div className="mt-2 flex items-center gap-1 text-xs text-slate-400"><Clock3 size={12}/> {deadlineTime(item.due_at)}</div>
          <button type="button" onClick={() => onOpenWork(item)}
            className="mt-3 inline-flex items-center gap-2 rounded-lg bg-amber-300 px-3 py-2 text-xs font-semibold text-[#081326] hover:bg-amber-200">
            Review and complete in My Work <ArrowRight size={14}/>
          </button>
        </article>
      ))}
    </div>
  );
}
/*
 * ARTIFACT: WilsyWorkDeadlineCalendar.jsx
 * VERSION: v1.1.0-CIVIL-DATES-KEYBOARD-AGENDA
 * AUTHORITY BOUNDARY: Read-only dates; source services authorize commands.
 * TENANT POSTURE: Only exact-session validated EOS projection items are consumed.
 * FAIL-CLOSED POSTURE: Malformed date helpers reject; no invented events or shifts.
 * FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
