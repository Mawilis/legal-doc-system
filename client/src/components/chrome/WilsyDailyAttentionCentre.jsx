/**
 * TITLE: WILSY OS Authenticated Daily Attention Centre
 * VERSION: v1.1.0-FLOATING-WORK-CALENDAR
 * AUTHORITY: Wilsy OS Core Governance
 * EPITOME: Interactive notification-bell entry to exact-tenant, authorised
 *          EOS My Work triage, with actionable navigation to source-owned
 *          completion. Does not masquerade task counts as unread notifications.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/components/chrome/WilsyDailyAttentionCentre.jsx
 * COLLABORATION / OWNERSHIP: Python EOS /api/my-work owns work visibility;
 *                            App.jsx owns authenticated chrome and navigation.
 * CERTIFICATION / UPDATE DATE: 2026-11-09
 * CHANGELOG: v1.1.0-FLOATING-WORK-CALENDAR adds an accessible movable/dockable work panel,
 *            a real EOS work deadline calendar, and action handoffs to
 *            source-authorised My Work and HR workflows.
 *            v1.0.1-STRICT-PROJECTION-DATE-VALIDATION also rejects
 *            malformed EOS snapshot timestamps before UI date formatting.
 *            v1.0.0-EOS-AUTHORISED-DAILY-ATTENTION implements on-demand work
 *            fetching, scoped validation, due/priority/source triage, search,
 *            keyboard/outside dismissal, safe refresh, detail expansion and
 *            source-owned action navigation.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
 * SECURITY / PRIVACY POSTURE: No browser-persisted queue, fabricated notices,
 *                            unread receipts, or client-derived permissions.
 * TENANT BOUNDARY: Rejects missing/mismatched tenant projections and stale
 *                  in-flight reads on authenticated scope changes.
 * AUTHORITY BOUNDARY: Read-only projection. Only EOS source services may
 *                     complete, approve, assign or acknowledge work.
 * FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns execution.
 */

import React, { useEffect, useMemo, useRef, useState } from 'react';
import {
  AlertTriangle, ArrowRight, Bell, CalendarDays, CheckCircle2,
  ChevronDown, Clock3, Grip, Pin, RefreshCw, Search, X,
} from 'lucide-react';
import api from '../../services/api.js';
import WilsyWorkDeadlineCalendar from './WilsyWorkDeadlineCalendar.jsx';

const SCHEMA = 'WILSY-OS-UNIFIED-MY-WORK/V1';
const SOURCES = Object.freeze({
  LEGAL: 'Legal',
  OPERATIONS: 'Operations',
  INTELLIGENCE: 'Intelligence',
  CRM: 'CRM',
});
const FILTERS = Object.freeze([
  { id: 'ALL', label: 'All work' },
  { id: 'OVERDUE', label: 'Overdue' },
  { id: 'TODAY', label: 'Due today' },
  { id: 'HIGH', label: 'High priority' },
]);
const VALID_PRIORITIES = new Set(['CRITICAL', 'HIGH', 'NORMAL', 'LOW']);

const validCount = (value) => Number.isSafeInteger(value) && value >= 0;

const dueToday = (dateValue) => {
  if (!dateValue) return false;
  const due = new Date(dateValue);
  return !Number.isNaN(due.getTime()) && due.toDateString() === new Date().toDateString();
};

const dueLabel = (value) => {
  if (!value) return 'No due date';
  const due = new Date(value);
  return Number.isNaN(due.getTime())
    ? 'Due date unavailable'
    : due.toLocaleString(undefined, { dateStyle: 'medium', timeStyle: 'short' });
};

/**
 * Validate an EOS-signed-in-session projection, never trusting HTTP success
 * alone as tenant or source authority. This function creates no new rights.
 */
export function assertAttentionProjection(payload, tenantId) {
  if (
    !payload || payload.schema !== SCHEMA || payload.tenant_id !== tenantId
    || typeof payload.as_of !== 'string'
    || Number.isNaN(new Date(payload.as_of).getTime())
    || !Array.isArray(payload.items) || !payload.summary
    || !validCount(payload.summary.active_count)
    || !validCount(payload.summary.overdue_count)
    || payload.summary.active_count !== payload.items.length
    || payload.authority?.commands_owned_by !== 'SOURCE_SERVICES'
    || payload.authority?.permits_completion !== false
  ) {
    throw new Error('ATTENTION_PROJECTION_INVALID');
  }
  const seen = new Set();
  let overdue = 0;
  for (const item of payload.items) {
    if (
      !item || !Object.hasOwn(SOURCES, item.source)
      || typeof item.work_item_id !== 'string' || !item.work_item_id.trim()
      || item.source_key !== item.source + ':' + item.work_item_id
      || seen.has(item.source_key)
      || typeof item.title !== 'string' || !item.title.trim()
      || !VALID_PRIORITIES.has(item.priority)
      || typeof item.is_overdue !== 'boolean'
      || (item.due_at !== null && item.due_at !== undefined
        && (typeof item.due_at !== 'string'
          || Number.isNaN(new Date(item.due_at).getTime())))
      || (Object.hasOwn(item, 'tenant_id') && item.tenant_id !== tenantId)
    ) {
      throw new Error('ATTENTION_ITEM_INVALID');
    }
    seen.add(item.source_key);
    if (item.is_overdue) overdue += 1;
  }
  if (payload.summary.overdue_count !== overdue) {
    throw new Error('ATTENTION_SUMMARY_INVALID');
  }
  return payload;
}

/**
 * @param {Object} props Authenticated chrome-only projection and callbacks.
 * @param {string|undefined} props.tenantId Exact current tenant from auth.
 * @param {boolean} props.systemServicesWorkspace System workspace exclusion.
 * @param {number|null} props.activeCount EOS-derived active work, NOT unread.
 * @param {boolean} props.open Whether the panel is expanded.
 * @param {Function} props.onToggle Toggles the panel.
 * @param {Function} props.onClose Dismisses the panel.
 * @param {Function} props.onOpenWork Navigates to canonical My Work commands.
 * @param {Function} props.onOpenWorkforce Navigates into governed HR workspace.
 */
export default function WilsyDailyAttentionCentre({
  tenantId,
  systemServicesWorkspace = false,
  activeCount = null,
  open,
  onToggle,
  onClose,
  onOpenWork,
  onOpenWorkforce,
}) {
  const rootRef = useRef(null);
  const panelRef = useRef(null);
  const dragRef = useRef(null);
  const [projection, setProjection] = useState(null);
  const [status, setStatus] = useState('IDLE');
  const [refreshId, setRefreshId] = useState(0);
  const [filter, setFilter] = useState('ALL');
  const [source, setSource] = useState('ALL');
  const [query, setQuery] = useState('');
  const [expanded, setExpanded] = useState(null);
  const [view, setView] = useState('WORK');
  const [floating, setFloating] = useState(null);

  useEffect(() => {
    setProjection(null);
    setStatus('IDLE');
    setFilter('ALL');
    setSource('ALL');
    setQuery('');
    setExpanded(null);
    setView('WORK');
    setFloating(null);
  }, [tenantId, systemServicesWorkspace]);

  useEffect(() => {
    if (!open) return undefined;
    if (!tenantId || systemServicesWorkspace) {
      setProjection(null);
      setStatus('UNAVAILABLE');
      return undefined;
    }
    let active = true;
    setProjection(null);
    setStatus('LOADING');
    api.get('/my-work', { forceNetworkRetry: true })
      .then((response) => {
        const verified = assertAttentionProjection(response?.data, tenantId);
        if (active) {
          setProjection(verified);
          setStatus('READY');
        }
      })
      .catch(() => {
        if (active) {
          setProjection(null);
          setStatus('UNAVAILABLE');
        }
      });
    return () => { active = false; };
  }, [open, tenantId, systemServicesWorkspace, refreshId]);

  useEffect(() => {
    if (!open) return undefined;
    const handleKey = (event) => {
      if (event.key === 'Escape') onClose();
    };
    const handlePointer = (event) => {
      if (rootRef.current && !rootRef.current.contains(event.target)) onClose();
    };
    document.addEventListener('keydown', handleKey);
    document.addEventListener('pointerdown', handlePointer);
    return () => {
      document.removeEventListener('keydown', handleKey);
      document.removeEventListener('pointerdown', handlePointer);
    };
  }, [open, onClose]);

  const items = projection?.items || [];
  const verifiedCount = status === 'READY' ? projection.summary.active_count : activeCount;
  const badgeCount = validCount(verifiedCount) && verifiedCount > 0 ? verifiedCount : null;
  const dueTodayCount = items.filter((item) => dueToday(item.due_at)).length;
  const highCount = items.filter((item) => ['CRITICAL', 'HIGH'].includes(item.priority)).length;

  const filteredItems = useMemo(() => {
    const phrase = query.trim().toLocaleLowerCase();
    return items.filter((item) => {
      if (filter === 'OVERDUE' && !item.is_overdue) return false;
      if (filter === 'TODAY' && !dueToday(item.due_at)) return false;
      if (filter === 'HIGH' && !['CRITICAL', 'HIGH'].includes(item.priority)) return false;
      if (source !== 'ALL' && item.source !== source) return false;
      if (!phrase) return true;
      return [
        item.title, item.description, item.status, item.priority,
        SOURCES[item.source], item.work_item_id,
      ].some((value) => typeof value === 'string'
        && value.toLocaleLowerCase().includes(phrase));
    });
  }, [items, filter, source, query]);


  // Floating position is a transient layout preference, not business state.
  const panelBounds = () => {
    const rect = panelRef.current?.getBoundingClientRect();
    return {
      x: rect?.left || 16, y: rect?.top || 72,
      width: rect?.width || Math.min(460, window.innerWidth - 32),
      height: rect?.height || Math.min(780, window.innerHeight - 80),
    };
  };
  const clamp = (x, y, w, h) => ({
    x: Math.max(8, Math.min(x, Math.max(8, window.innerWidth - w - 8))),
    y: Math.max(8, Math.min(y, Math.max(8, window.innerHeight - h - 8))),
  });
  const floatAtPanel = () => {
    const box = panelBounds();
    const pos = clamp(box.x, box.y, box.width, box.height);
    setFloating(pos);
    return pos;
  };
  const handlePointerDown = (event) => {
    if (event.pointerType === 'mouse' && event.button !== 0) return;
    const rect = panelBounds();
    dragRef.current = {
      id: event.pointerId, origin: floating || floatAtPanel(),
      x: event.clientX, y: event.clientY, w: rect.width, h: rect.height,
    };
    event.currentTarget.setPointerCapture?.(event.pointerId);
  };
  const handlePointerMove = (event) => {
    const drag = dragRef.current;
    if (!drag || drag.id !== event.pointerId) return;
    setFloating(clamp(drag.origin.x + event.clientX - drag.x,
      drag.origin.y + event.clientY - drag.y, drag.w, drag.h));
  };
  const handlePointerEnd = (event) => {
    if (dragRef.current?.id !== event.pointerId) return;
    dragRef.current = null;
    if (event.currentTarget.hasPointerCapture?.(event.pointerId)) {
      event.currentTarget.releasePointerCapture(event.pointerId);
    }
  };
  const handleDragKey = (event) => {
    const directions = { ArrowLeft: [-1, 0], ArrowRight: [1, 0],
      ArrowUp: [0, -1], ArrowDown: [0, 1] };
    const d = directions[event.key];
    if (!d) return;
    event.preventDefault();
    const bounds = panelBounds();
    const current = floating || floatAtPanel();
    const amount = event.shiftKey ? 40 : 16;
    setFloating(clamp(current.x + d[0] * amount,
      current.y + d[1] * amount, bounds.width, bounds.height));
  };
  useEffect(() => {
    if (!open || !floating) return undefined;
    const onResize = () => {
      const box = panelBounds();
      setFloating((before) => before && clamp(before.x, before.y, box.width, box.height));
    };
    window.addEventListener('resize', onResize);
    return () => window.removeEventListener('resize', onResize);
  }, [open, Boolean(floating)]);

  return (
    <div className="relative" ref={rootRef} data-wilsy-attention-centre="true">
      <button
        type="button"
        aria-label={badgeCount === null
          ? 'Open daily attention'
          : 'Open daily attention: ' + badgeCount + ' active work items'}
        aria-haspopup="dialog"
        aria-expanded={Boolean(open)}
        onClick={onToggle}
        className="relative grid h-10 w-10 place-items-center rounded-full text-slate-300 transition hover:bg-white/10 focus-visible:outline focus-visible:outline-2 focus-visible:outline-amber-300"
      >
        <Bell size={19} />
        {badgeCount !== null && (
          <span
            aria-label={badgeCount + ' active work items, not unread notifications'}
            className="absolute -right-1 -top-1 grid min-h-5 min-w-5 place-items-center rounded-full bg-amber-400 px-1 text-[10px] font-bold tabular-nums text-[#081326]"
          >
            {badgeCount > 99 ? '99+' : badgeCount}
          </span>
        )}
      </button>

      {open && (
        <section
          ref={panelRef}
          role="dialog"
          aria-label="Daily attention centre"
          data-floating={floating ? 'true' : 'false'}
          style={floating ? { position: 'fixed', left: floating.x, top: floating.y, right: 'auto' } : undefined}
          className={(floating ? 'fixed z-[90]' : 'absolute right-0 top-12 z-50') + ' flex w-[min(460px,calc(100vw-2rem))] max-h-[min(780px,calc(100vh-5rem))] flex-col overflow-hidden rounded-2xl border border-white/15 bg-[#101d32] text-slate-100 shadow-2xl shadow-black/60'}
        >
          <div className="flex shrink-0 items-start justify-between gap-3 border-b border-white/10 bg-[#14243d] px-5 py-4">
            <div>
              <div className="flex items-center gap-2">
                <Bell size={17} className="text-amber-300" />
                <h2 className="text-base font-semibold text-white">Daily attention</h2>
              </div>
              <p className="mt-1 text-xs leading-5 text-slate-400">
                Your authorised EOS work across business functions.
              </p>
            </div>
            <div className="flex items-center gap-1">
              <button type="button" aria-label="Move daily attention panel with pointer or arrow keys"
                title="Drag to move; arrow keys to reposition"
                onPointerDown={handlePointerDown} onPointerMove={handlePointerMove}
                onPointerUp={handlePointerEnd} onPointerCancel={handlePointerEnd}
                onKeyDown={handleDragKey} style={{ touchAction: 'none' }}
                className="cursor-grab rounded-lg p-2 text-slate-300 hover:bg-white/10 active:cursor-grabbing focus-visible:outline focus-visible:outline-2 focus-visible:outline-amber-300">
                <Grip size={18}/>
              </button>
              <button type="button" aria-label={floating ? 'Dock daily attention panel' : 'Float daily attention panel'}
                onClick={() => { dragRef.current = null; floating ? setFloating(null) : floatAtPanel(); }}
                className="rounded-lg p-2 text-slate-300 hover:bg-white/10">
                <Pin size={17} className={floating ? 'text-amber-300' : ''}/>
              </button>
              <button type="button" aria-label="Close daily attention" onClick={onClose}
                className="rounded-lg p-2 text-slate-300 hover:bg-white/10"><X size={17}/></button>
            </div>
          </div>

          {status === 'LOADING' && (
            <div role="status" className="flex items-center gap-2 px-5 py-8 text-sm text-amber-200">
              <RefreshCw size={16} className="animate-spin"/> Checking current work…
            </div>
          )}

          {status === 'UNAVAILABLE' && (
            <div role="alert" className="space-y-3 px-5 py-6">
              <div className="flex items-center gap-2 font-medium text-rose-200">
                <AlertTriangle size={17}/> Work source unavailable
              </div>
              <p className="text-sm leading-6 text-slate-300">
                Current tenant authorisation or an EOS work source could not be verified.
                No cached or invented work is shown.
              </p>
              {!systemServicesWorkspace && tenantId && (
                <button type="button" onClick={() => setRefreshId((id) => id + 1)}
                  className="rounded-lg border border-white/20 px-3 py-2 text-xs hover:bg-white/10">
                  Retry authorised read
                </button>
              )}
            </div>
          )}

          {status === 'READY' && (
            <>
              <div className="shrink-0 border-b border-white/10 px-4 pb-3 pt-4">
                <div role="tablist" aria-label="Daily attention views" className="mb-3 flex items-center gap-2">
                  <button type="button" role="tab" aria-selected={view === 'WORK'}
                    onClick={() => setView('WORK')}
                    className={'rounded-lg px-3 py-2 text-xs font-semibold ' +
                      (view === 'WORK' ? 'bg-amber-300 text-[#081326]' : 'text-slate-300 hover:bg-white/10')}>
                    Work list
                  </button>
                  <button type="button" role="tab" aria-selected={view === 'CALENDAR'}
                    onClick={() => setView('CALENDAR')}
                    className={'inline-flex items-center gap-1.5 rounded-lg px-3 py-2 text-xs font-semibold ' +
                      (view === 'CALENDAR' ? 'bg-amber-300 text-[#081326]' : 'text-slate-300 hover:bg-white/10')}>
                    <CalendarDays size={14}/> Calendar
                  </button>
                </div>
                <div className="grid grid-cols-3 gap-2">
                  <Stat label="Active" value={items.length} />
                  <Stat label="Overdue" value={projection.summary.overdue_count} urgent={projection.summary.overdue_count > 0}/>
                  <Stat label="Due today" value={dueTodayCount}/>
                </div>
                <div className="mt-3 flex flex-wrap items-center justify-between gap-2">
                  <p className="text-[11px] text-slate-400">{highCount} high-priority items</p>
                  <button type="button" onClick={() => setRefreshId((id) => id + 1)}
                    className="flex items-center gap-1.5 rounded-lg px-2 py-1 text-xs text-amber-200 hover:bg-white/10">
                    <RefreshCw size={13}/> Refresh
                  </button>
                </div>
                {view === 'WORK' && (<>
                <div role="group" aria-label="Filter daily attention" className="mt-3 flex flex-wrap gap-1.5">
                  {FILTERS.map(({ id, label }) => (
                    <button key={id} type="button" aria-pressed={filter === id}
                      onClick={() => setFilter(id)}
                      className={'rounded-full border px-2.5 py-1.5 text-[11px] font-medium transition ' +
                        (filter === id
                          ? 'border-amber-300/40 bg-amber-300/15 text-amber-100'
                          : 'border-white/10 text-slate-300 hover:bg-white/10')}
                    >{label}</button>
                  ))}
                </div>
                <div className="mt-3 flex gap-2">
                  <label className="flex min-w-0 flex-1 items-center gap-2 rounded-lg border border-white/15 bg-[#0b1729] px-2.5">
                    <Search size={15} className="shrink-0 text-slate-500"/>
                    <input type="search" aria-label="Search authorised work" value={query}
                      onChange={(event) => setQuery(event.target.value)}
                      placeholder="Search your work"
                      className="h-9 w-full min-w-0 bg-transparent text-xs text-white outline-none placeholder:text-slate-500"/>
                  </label>
                  <label className="relative flex items-center rounded-lg border border-white/15 bg-[#0b1729]">
                    <span className="sr-only">Work source</span>
                    <select aria-label="Filter work by source" value={source}
                      onChange={(event) => setSource(event.target.value)}
                      className="h-9 max-w-[120px] appearance-none bg-transparent pl-2.5 pr-6 text-xs text-white outline-none">
                      <option className="bg-[#101d32]" value="ALL">All sources</option>
                      {Object.entries(SOURCES).map(([id, label]) => (
                        <option className="bg-[#101d32]" key={id} value={id}>{label}</option>
                      ))}
                    </select>
                    <ChevronDown size={12} className="pointer-events-none absolute right-2 text-slate-400"/>
                  </label>
                </div>
                </>)}
              </div>

              <div className="min-h-0 flex-1 overflow-y-auto px-3 py-2" aria-live="polite">
                {view === 'CALENDAR' ? (
                  <WilsyWorkDeadlineCalendar items={items}
                    onOpenWork={onOpenWork} onOpenWorkforce={onOpenWorkforce}/>
                ) : filteredItems.length === 0 ? (
                  <div className="py-9 text-center">
                    <CheckCircle2 size={26} className="mx-auto text-emerald-300"/>
                    <p className="mt-3 text-sm font-medium text-white">
                      {items.length === 0 ? 'No active work in authorised sources' : 'No work matches these filters'}
                    </p>
                    <p className="mt-1 text-xs text-slate-400">
                      {items.length === 0
                        ? 'Your authorised work sources returned an empty active queue.'
                        : 'Try another filter or search term.'}
                    </p>
                    {items.length === 0 && onOpenWorkforce && (
                      <button type="button" onClick={onOpenWorkforce}
                        className="mt-4 inline-flex items-center gap-1.5 rounded-lg border border-amber-300/40 px-3 py-2 text-xs font-semibold text-amber-100 hover:bg-white/10">
                        Open HR & workforce duties <ArrowRight size={13}/>
                      </button>
                    )}
                  </div>
                ) : filteredItems.map((item) => (
                  <article key={item.source_key} className="mb-2 rounded-xl border border-white/10 bg-white/[0.035] p-3">
                    <div className="flex items-center justify-between gap-2 text-[10px] uppercase tracking-[0.08em]">
                      <span className="font-semibold text-amber-200">{SOURCES[item.source]}</span>
                      <span className={item.is_overdue ? 'font-semibold text-rose-300' : 'text-slate-400'}>
                        {item.is_overdue ? 'Overdue' : item.priority + ' priority'}
                      </span>
                    </div>
                    <button type="button" aria-expanded={expanded === item.source_key}
                      onClick={() => setExpanded((previous) => previous === item.source_key ? null : item.source_key)}
                      className="mt-2 flex w-full items-start justify-between gap-2 text-left text-sm font-medium text-white hover:text-amber-100">
                      <span className="min-w-0 break-words">{item.title}</span>
                      <ChevronDown size={15} className={'mt-0.5 shrink-0 transition ' +
                        (expanded === item.source_key ? 'rotate-180' : '')}/>
                    </button>
                    <div className="mt-2 flex flex-wrap items-center gap-3 text-[11px] text-slate-400">
                      <span className="inline-flex items-center gap-1"><Clock3 size={12}/>{dueLabel(item.due_at)}</span>
                      <span>{item.status}</span>
                    </div>
                    {expanded === item.source_key && (
                      <div className="mt-3 border-t border-white/10 pt-3">
                        {item.description && (
                          <p className="mb-3 whitespace-pre-wrap break-words text-xs leading-5 text-slate-300">
                            {item.description}
                          </p>
                        )}
                        <p className="text-[11px] leading-5 text-slate-400">
                          Work actions are verified and recorded by the owning EOS service.
                        </p>
                        <button type="button" onClick={() => onOpenWork(item)}
                          className="mt-3 inline-flex items-center gap-2 rounded-lg bg-amber-300 px-3 py-2 text-xs font-semibold text-[#081326] hover:bg-amber-200">
                          Open in My Work <ArrowRight size={14}/>
                        </button>
                      </div>
                    )}
                  </article>
                ))}
              </div>

              <div className="shrink-0 border-t border-white/10 bg-[#14243d] px-4 py-3">
                <div className="mb-2 flex items-center justify-between gap-2 text-[10px] text-slate-400">
                  <span>{filteredItems.length} of {items.length} authorised items</span>
                  <button type="button" aria-label="Open work deadline calendar"
                    onClick={() => setView('CALENDAR')}
                    className="inline-flex items-center gap-1 rounded-lg px-2 py-1 text-amber-200 hover:bg-white/10">
                    <CalendarDays size={14}/>
                    <span>Calendar · {new Date(projection.as_of).toLocaleTimeString([], {
                      hour: '2-digit', minute: '2-digit',
                    })}</span>
                  </button>
                </div>
                <div className="flex gap-2">
                  {onOpenWorkforce && (
                    <button type="button" onClick={onOpenWorkforce}
                      className="min-w-0 flex-1 rounded-lg border border-amber-300/40 px-3 py-2.5 text-xs font-semibold text-amber-100 hover:bg-white/10">
                      HR & workforce
                    </button>
                  )}
                  <button type="button" onClick={() => onOpenWork(null)}
                    className="flex min-w-0 flex-[2] items-center justify-center gap-2 rounded-lg bg-amber-300 px-3 py-2.5 text-xs font-semibold text-[#091426] hover:bg-amber-200">
                    Open My Work <ArrowRight size={14}/>
                  </button>
                </div>
              </div>
            </>
          )}
        </section>
      )}
    </div>
  );
}

/** Read-only summary tile for EOS-authorised active work. */
function Stat({ label, value, urgent = false }) {
  return (
    <div className="rounded-lg border border-white/10 bg-white/[0.04] px-3 py-2">
      <p className="text-[10px] text-slate-400">{label}</p>
      <p className={'mt-1 text-lg font-semibold tabular-nums ' +
        (urgent ? 'text-rose-200' : 'text-white')}>{value}</p>
    </div>
  );
}

/*
 * ARTIFACT: WilsyDailyAttentionCentre.jsx
 * VERSION: v1.1.0-FLOATING-WORK-CALENDAR
 * AUTHORITY BOUNDARY: Authenticated read-only EOS work triage.
 * TENANT POSTURE: Exact tenant, fail-closed, no browser persistence.
 * FAIL-CLOSED POSTURE: Invalid, denied or unavailable sources show no fabricated items.
 * FINANCIAL EXECUTION AUTHORITY: Kennel EOS only.
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
