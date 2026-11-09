/**
 * TITLE: WILSY OS Authorised Work Deadline Calendar
 * VERSION: v1.0.0-SOURCE-OWNED-WORK-DEADLINES
 * AUTHORITY: Wilsy OS Core Governance
 * EPITOME: A genuine navigable month calendar of due dates and an actionable
 *          agenda derived exclusively from EOS-authorised My Work records.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/components/chrome/WilsyWorkDeadlineCalendar.jsx
 * COLLABORATION / OWNERSHIP: WilsyDailyAttentionCentre validates EOS /my-work;
 *                            MyWorkWorkspace owns source-specific commands.
 * CERTIFICATION / UPDATE DATE: 2026-11-09
 * CHANGELOG: v1.0.0-SOURCE-OWNED-WORK-DEADLINES adds month/day navigation,
 *            dated and undated task agendas and source-owned action handoff.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
 * SECURITY / PRIVACY POSTURE: In-memory, read-only and no fabricated events.
 * TENANT BOUNDARY: Consumes only the validated current-session EOS work data.
 * AUTHORITY BOUNDARY: No meeting, shift, leave or task mutation from browser.
 * FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively executes funds.
 */
import React, { useMemo, useState } from 'react';
import { ArrowRight, ChevronLeft, ChevronRight, Clock3 } from 'lucide-react';

const SOURCES = Object.freeze({
  LEGAL: 'Legal', OPERATIONS: 'Operations', INTELLIGENCE: 'Intelligence', CRM: 'CRM',
});

export const localWorkDay = (value) => {
  if (!value) return null;
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return null;
  return [date.getFullYear(), String(date.getMonth() + 1).padStart(2, '0'),
    String(date.getDate()).padStart(2, '0')].join('-');
};

export function monthWorkDays(month) {
  const first = new Date(month.getFullYear(), month.getMonth(), 1);
  const pad = (first.getDay() + 6) % 7;
  const length = new Date(first.getFullYear(), first.getMonth() + 1, 0).getDate();
  return Array.from({ length: Math.ceil((pad + length) / 7) * 7 }, (_, i) => {
    const date = new Date(first.getFullYear(), first.getMonth(), i + 1 - pad);
    return { key: localWorkDay(date), date, currentMonth: date.getMonth() === first.getMonth() };
  });
}

/**
 * @param {Object[]} items Exact-tenant, EOS-validated active work items.
 * @param {Function} onOpenWork Route into the source-governed My Work item.
 * @param {Function} onOpenWorkforce Route to existing authorised HR workspace.
 * @returns {JSX.Element} Navigable month and action-oriented selected-day agenda.
 */
export default function WilsyWorkDeadlineCalendar({ items, onOpenWork, onOpenWorkforce }) {
  const [month, setMonth] = useState(() => new Date(new Date().getFullYear(), new Date().getMonth(), 1));
  const [selected, setSelected] = useState(() => localWorkDay(new Date()));
  const counts = useMemo(() => {
    const byDay = new Map();
    for (const item of items) {
      const day = localWorkDay(item.due_at);
      if (day) byDay.set(day, (byDay.get(day) || 0) + 1);
    }
    return byDay;
  }, [items]);
  const undated = items.filter((item) => !item.due_at);
  const agenda = selected === null
    ? undated
    : items.filter((item) => localWorkDay(item.due_at) === selected);
  const changeMonth = (delta) => setMonth((previous) =>
    new Date(previous.getFullYear(), previous.getMonth() + delta, 1));
  const jumpToToday = () => {
    const today = new Date();
    setMonth(new Date(today.getFullYear(), today.getMonth(), 1));
    setSelected(localWorkDay(today));
  };
  const dateTitle = selected === null ? 'Work without a due date'
    : new Date(selected + 'T12:00:00').toLocaleDateString(undefined, { dateStyle: 'full' });

  return (
    <div aria-label="EOS work deadline calendar" className="space-y-3">
      <p className="text-xs leading-5 text-slate-400">
        Authorised work deadlines, not a meeting, leave or shift calendar.
        Select a day to review and act on source-owned tasks.
      </p>
      <div className="flex items-center justify-between gap-2">
        <button type="button" aria-label="Previous month" onClick={() => changeMonth(-1)}
          className="rounded-lg border border-white/10 p-2 text-slate-200 hover:bg-white/10">
          <ChevronLeft size={16}/>
        </button>
        <h3 className="font-semibold text-white">
          {month.toLocaleDateString(undefined, { month: 'long', year: 'numeric' })}
        </h3>
        <button type="button" aria-label="Next month" onClick={() => changeMonth(1)}
          className="rounded-lg border border-white/10 p-2 text-slate-200 hover:bg-white/10">
          <ChevronRight size={16}/>
        </button>
      </div>
      <div className="grid grid-cols-7 gap-1 text-center text-[10px] text-slate-400" aria-hidden="true">
        {['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'].map((name) =>
          <span key={name}>{name}</span>)}
      </div>
      <div role="group" aria-label="Choose work deadline date" className="grid grid-cols-7 gap-1">
        {monthWorkDays(month).map(({ key, date, currentMonth }) => {
          const count = counts.get(key) || 0;
          return (
            <button key={key} type="button" aria-pressed={selected === key}
              aria-label={date.toLocaleDateString(undefined, { dateStyle: 'full' }) +
                ': ' + count + ' due work items'}
              onClick={() => {
                setSelected(key);
                if (!currentMonth) setMonth(new Date(date.getFullYear(), date.getMonth(), 1));
              }}
              className={'flex min-h-11 flex-col items-center justify-center rounded-lg border text-xs transition ' +
                (selected === key ? 'border-amber-300 bg-amber-300/15 text-amber-100'
                  : currentMonth ? 'border-white/10 text-slate-200 hover:bg-white/10'
                    : 'border-transparent text-slate-500 hover:bg-white/10')}>
              <span>{date.getDate()}</span>
              {count > 0 && <span className="mt-0.5 text-[10px] font-bold text-amber-300">
                {count} due
              </span>}
            </button>
          );
        })}
      </div>
      <div className="flex flex-wrap gap-2 border-b border-white/10 pb-3">
        <button type="button" onClick={jumpToToday}
          className="rounded-lg border border-white/15 px-3 py-1.5 text-xs text-slate-200 hover:bg-white/10">
          Today
        </button>
        <button type="button" onClick={() => setSelected(null)}
          aria-pressed={selected === null}
          className="rounded-lg border border-white/15 px-3 py-1.5 text-xs text-amber-100 hover:bg-white/10">
          Without due date ({undated.length})
        </button>
      </div>
      <h4 className="text-sm font-semibold text-white">{dateTitle}</h4>
      {agenda.length === 0 ? (
        <div className="rounded-lg border border-white/10 p-4">
          <p className="text-xs leading-5 text-slate-400">
            No authorised work items have a due date on this day.
          </p>
          {onOpenWorkforce && (
            <button type="button" onClick={onOpenWorkforce}
              className="mt-3 inline-flex items-center gap-1.5 text-xs font-semibold text-amber-200 hover:underline">
              Open HR & workforce duties <ArrowRight size={13}/>
            </button>
          )}
        </div>
      ) : agenda.map((item) => (
        <article key={item.source_key}
          className="rounded-xl border border-white/10 bg-white/[0.035] p-3">
          <div className="flex items-center justify-between gap-2 text-[10px] uppercase tracking-wide">
            <span className="font-semibold text-amber-200">{SOURCES[item.source]}</span>
            <span className={item.is_overdue ? 'text-rose-300' : 'text-slate-400'}>
              {item.is_overdue ? 'Overdue' : item.priority + ' priority'}
            </span>
          </div>
          <h5 className="mt-2 text-sm font-semibold text-white">{item.title}</h5>
          {item.description && <p className="mt-1 break-words text-xs text-slate-400">{item.description}</p>}
          <div className="mt-2 flex items-center gap-1 text-xs text-slate-400">
            <Clock3 size={12}/> {item.due_at
              ? new Date(item.due_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
              : 'No due time'}
          </div>
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
 * VERSION: v1.0.0-SOURCE-OWNED-WORK-DEADLINES
 * AUTHORITY BOUNDARY: Read-only dates; source-validated commands elsewhere.
 * TENANT POSTURE: Receives only exact-session validated EOS projection items.
 * FAIL-CLOSED POSTURE: No invented calendar events or synthetic shift truth.
 * FINANCIAL EXECUTION AUTHORITY: Kennel EOS only.
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
