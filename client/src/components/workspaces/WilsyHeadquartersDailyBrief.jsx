/**
 * TITLE: WILSY OS Headquarters Daily Execution Brief
 * VERSION: v1.0.2-SHARED-PROJECTION-CONTRACT
 * AUTHORITY: Wilsy OS Core Governance
 * EPITOME: Source-verified daily operating overview for the current authenticated
 *          tenant, with projection coverage derived from EOS source metadata.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/components/workspaces/WilsyHeadquartersDailyBrief.jsx
 * COLLABORATION / OWNERSHIP: EOS /api/my-work owns source admission and item
 *                            visibility; MyWorkWorkspace owns source commands.
 * CERTIFICATION / UPDATE DATE: 2026-11-09
 * CHANGELOG: v1.0.2-SHARED-PROJECTION-CONTRACT delegates tenant, item and source
 *            coverage validation to the canonical shared validator and passes
 *            selected item context through the My Work navigation callback.
 *            v1.0.1-AUTHORISED-SOURCE-COVERAGE derives source filters from
 *            EOS sources_included, checks source counts against projected rows,
 *            distinguishes no included source from a verified empty queue, and
 *            clears filters when the tenant changes.
 *            v1.0.0-SOURCE-VERIFIED-DAILY-BRIEF connects Headquarters to exact-
 *            tenant work counts, urgency, navigation, retry and unavailable state.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
 * SECURITY / PRIVACY POSTURE: Authenticated in-memory projections only; no
 *                            invented company performance or source coverage.
 * TENANT BOUNDARY: Rejects missing/mismatched tenant, malformed source coverage,
 *                  and stale in-flight tenant reads.
 * AUTHORITY BOUNDARY: Read-only projection; source-owned services authorize
 *                     every command.
 * FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively executes funds.
 */

import React, { useEffect, useMemo, useState } from 'react';
import {
  AlertTriangle, ArrowRight, CheckCircle2, Clock3, RefreshCw,
  Search, ShieldCheck, Target,
} from 'lucide-react';
import api from '../../services/api.js';
import {
  assertUnifiedMyWorkProjection,
  unifiedMyWorkSourceLabel,
} from '../../services/unifiedMyWorkProjection.js';

const isToday = (value) => Boolean(value)
  && !Number.isNaN(new Date(value).getTime())
  && new Date(value).toDateString() === new Date().toDateString();

const formatDeadline = (value) => value
  ? new Date(value).toLocaleString(undefined, { dateStyle: 'medium', timeStyle: 'short' })
  : 'No due date';

/**
 * Render the authenticated Headquarters daily work projection without creating
 * work, assigning authority, or executing source commands.
 *
 * @description Displays current EOS work counts, admitted-source coverage,
 *   bounded search/filter controls, and a source-owned My Work handoff.
 * @collaboration WilsyHeadquartersWorkspace supplies the authenticated tenant
 *   and navigation callback; EOS /api/my-work supplies the authorized read.
 * @institutional Exact-tenant projection and source metadata keep a verified
 *   zero distinct from omitted source coverage. Selected item context identifies
 *   a target for focus only; it does not create work or command authority.
 * @param {{tenantId: string|null, onOpenWork: Function}} props Current tenant
 *   and navigation callback supplied by the authenticated workspace.
 * @returns {JSX.Element} Daily work brief with loading, unavailable, or ready state.
 */
export default function WilsyHeadquartersDailyBrief({ tenantId, onOpenWork }) {
  const [projection, setProjection] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  const [refreshId, setRefreshId] = useState(0);
  const [scope, setScope] = useState(null);
  const [filter, setFilter] = useState('ALL');
  const [query, setQuery] = useState('');
  const [source, setSource] = useState('ALL');

  useEffect(() => {
    setFilter('ALL');
    setQuery('');
    setSource('ALL');
  }, [tenantId]);

  useEffect(() => {
    if (!tenantId) {
      setProjection(null);
      setScope(null);
      setError(true);
      setLoading(false);
      return undefined;
    }
    let active = true;
    setProjection(null);
    setScope(null);
    setLoading(true);
    setError(false);
    api.get('/my-work', { forceNetworkRetry: true })
      .then((response) => {
        const verified = assertUnifiedMyWorkProjection(response?.data, { tenantId });
        if (active) {
          setProjection(verified);
          setScope(tenantId);
          setLoading(false);
        }
      })
      .catch(() => {
        if (active) {
          setProjection(null);
          setScope(null);
          setError(true);
          setLoading(false);
        }
      });
    return () => { active = false; };
  }, [tenantId, refreshId]);

  const data = scope === tenantId ? projection : null;
  const items = data?.items || [];
  const sourceIds = data?.sources_included || [];
  const sourceOptions = sourceIds.map((id) => [id, unifiedMyWorkSourceLabel(id)]);
  const sourceLabels = sourceOptions.map(([, label]) => label);
  const todayCount = items.filter((item) => isToday(item.due_at)).length;
  const urgentCount = items.filter((item) => ['CRITICAL', 'HIGH'].includes(item.priority)).length;

  useEffect(() => {
    if (data && source !== 'ALL' && !data.sources_included.includes(source)) {
      setSource('ALL');
    }
  }, [data, source]);

  const filtered = useMemo(() => {
    const phrase = query.trim().toLocaleLowerCase();
    return items.filter((item) => {
      if (filter === 'OVERDUE' && !item.is_overdue) return false;
      if (filter === 'TODAY' && !isToday(item.due_at)) return false;
      if (filter === 'PRIORITY' && !['HIGH', 'CRITICAL'].includes(item.priority)) return false;
      if (source !== 'ALL' && item.source !== source) return false;
      return !phrase || [
        item.title, item.description, item.status, unifiedMyWorkSourceLabel(item.source),
      ].some((value) => typeof value === 'string' && value.toLocaleLowerCase().includes(phrase));
    });
  }, [items, filter, source, query]);

  return (
    <section
      aria-label="Headquarters daily execution"
      data-wilsy-daily-execution="true"
      className="mt-6 overflow-hidden rounded-2xl border border-white/10 bg-[#101a2a]"
    >
      <header className="flex flex-wrap items-start justify-between gap-3 border-b border-white/10 bg-[#12243d] p-5">
        <div>
          <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.18em] text-amber-300">
            <Target size={15}/> Today in WILSY OS
          </div>
          <h2 className="mt-2 text-xl font-semibold tracking-tight text-white sm:text-2xl">
            Your daily execution brief
          </h2>
          <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-400">
            Work requiring your attention, drawn only from EOS sources
            authorised for your current business capacity.
          </p>
        </div>
        <button type="button" onClick={() => setRefreshId((id) => id + 1)}
          disabled={loading || !tenantId}
          className="inline-flex items-center gap-2 rounded-lg border border-white/15 px-3 py-2 text-xs text-slate-200 hover:bg-white/10 disabled:opacity-40">
          <RefreshCw size={14} className={loading ? 'animate-spin' : ''}/> Refresh
        </button>
      </header>

      {(loading || (!data && !error)) && (
        <div role="status" className="flex items-center gap-3 p-6 text-sm text-amber-200">
          <RefreshCw size={16} className="animate-spin"/> Verifying today's authorised work…
        </div>
      )}

      {!loading && (error || !data) && (
        <div role="alert" className="space-y-3 p-6">
          <div className="flex items-center gap-2 font-semibold text-rose-200">
            <AlertTriangle size={19}/> Daily work cannot be verified
          </div>
          <p className="max-w-2xl text-sm leading-6 text-slate-300">
            EOS could not verify the current tenant's authorised work sources.
            The dashboard will not substitute invented numbers or a stale queue.
          </p>
          {tenantId && <button type="button" onClick={() => setRefreshId((id) => id + 1)}
            className="rounded-lg border border-amber-300/30 px-3 py-2 text-xs text-amber-100 hover:bg-amber-300/10">
            Retry source read
          </button>}
        </div>
      )}

      {!loading && data && (
        <>
          <div className="grid gap-3 p-4 sm:grid-cols-2 xl:grid-cols-4">
            <Metric label="Active work" value={data.summary.active_count} />
            <Metric label="Overdue" value={data.summary.overdue_count} urgent={data.summary.overdue_count > 0}/>
            <Metric label="Due today" value={todayCount}/>
            <Metric label="High-priority" value={urgentCount}/>
          </div>

          <div className="mx-4 flex flex-wrap items-center justify-between gap-3 border-y border-white/10 py-3">
            <div role="group" aria-label="Daily work filters" className="flex flex-wrap gap-2">
              {[
                ['ALL', 'All work'],
                ['OVERDUE', 'Overdue'],
                ['TODAY', 'Due today'],
                ['PRIORITY', 'High priority'],
              ].map(([id, label]) => (
                <button key={id} type="button" aria-pressed={filter === id}
                  onClick={() => setFilter(id)}
                  className={'rounded-full px-3 py-1.5 text-xs font-medium transition ' +
                    (filter === id ? 'bg-amber-300 text-[#081326]' :
                      'border border-white/15 text-slate-300 hover:bg-white/10')}>
                  {label}
                </button>
              ))}
            </div>
            <p className="flex items-center gap-1.5 text-[11px] text-emerald-200">
              <ShieldCheck size={13}/> EOS-authorised source projection
            </p>
          </div>

          <div className="flex flex-wrap gap-2 px-4 py-4 sm:flex-nowrap">
            <label className="flex min-w-0 flex-1 items-center gap-2 rounded-lg border border-white/15 bg-[#0a1423] px-3">
              <Search size={15} className="text-slate-500"/>
              <input type="search" aria-label="Search headquarters work" value={query}
                onChange={(event) => setQuery(event.target.value)}
                placeholder="Search priorities and work items"
                className="h-10 w-full min-w-0 bg-transparent text-sm text-white outline-none placeholder:text-slate-500" />
            </label>
            <select aria-label="Filter headquarters by source" value={source}
              onChange={(event) => setSource(event.target.value)}
              className="h-10 max-w-full rounded-lg border border-white/15 bg-[#0a1423] px-3 text-xs text-slate-200 sm:w-auto">
              <option value="ALL">All included sources</option>
              {sourceOptions.map(([id, label]) =>
                <option key={id} value={id}>{label}</option>)}
            </select>
          </div>

          <div className="space-y-2 px-4 pb-4" aria-live="polite">
            {filtered.length === 0 && (
              <div className="rounded-xl border border-white/10 bg-white/[0.03] px-5 py-8 text-center">
                <CheckCircle2 size={26} className="mx-auto text-emerald-300"/>
                <p className="mt-3 text-sm font-semibold text-white">
                  {items.length === 0
                    ? (sourceIds.length === 0
                      ? 'No work source was included in this session'
                      : 'No active work in the included sources')
                    : 'No work matches these filters'}
                </p>
                <p className="mt-1 text-xs text-slate-400">
                  {items.length === 0
                    ? (sourceIds.length === 0
                      ? 'EOS returned no source projection. This is not evidence that every business queue is empty.'
                      : 'EOS returned no active work from ' + sourceLabels.join(', ') + '.')
                    : 'Adjust the search or filter to see other work.'}
                </p>
              </div>
            )}
            {filtered.slice(0, 6).map((item) => (
              <div key={item.source_key}
                className="flex flex-wrap items-center justify-between gap-3 rounded-xl border border-white/10 bg-white/[0.035] p-4 transition hover:border-amber-300/25">
                <div className="min-w-0 flex-1">
                  <div className="flex flex-wrap items-center gap-2 text-[10px] font-semibold uppercase tracking-wide">
                    <span className="text-amber-200">{unifiedMyWorkSourceLabel(item.source)}</span>
                    {item.is_overdue && <span className="rounded-full bg-rose-400/10 px-2 py-0.5 text-rose-200">Overdue</span>}
                    {['HIGH','CRITICAL'].includes(item.priority) &&
                      <span className="rounded-full bg-amber-300/10 px-2 py-0.5 text-amber-200">{item.priority}</span>}
                  </div>
                  <h3 className="mt-1.5 break-words text-sm font-semibold text-white">{item.title}</h3>
                  <p className="mt-1 flex items-center gap-1.5 text-xs text-slate-400">
                    <Clock3 size={12}/> {formatDeadline(item.due_at)} · {item.status}
                  </p>
                </div>
                <button type="button" onClick={() => onOpenWork(item)}
                  aria-label={'Open authorised work action for ' + item.title}
                  className="inline-flex items-center gap-1.5 rounded-lg border border-amber-300/30 px-3 py-2 text-xs font-medium text-amber-100 hover:bg-amber-300/10">
                  Review action <ArrowRight size={14}/>
                </button>
              </div>
            ))}
            {filtered.length > 6 && <p className="px-2 py-2 text-xs text-slate-400">
              Showing the first six of {filtered.length} matching items. The full queue is available in My Work.
            </p>}
          </div>

          <footer className="flex flex-wrap items-center justify-between gap-3 border-t border-white/10 bg-[#111e32] px-5 py-4">
            <p className="text-[11px] text-slate-400">
              Projection assembled {new Date(data.as_of).toLocaleTimeString([], {hour:'2-digit',minute:'2-digit'})}
              {' · Included: '}{sourceLabels.length ? sourceLabels.join(', ') : 'no source projection'}
            </p>
            <button type="button" onClick={() => onOpenWork(null)}
              className="inline-flex items-center gap-2 rounded-lg bg-amber-300 px-4 py-2.5 text-sm font-semibold text-[#091426] hover:bg-amber-200">
              Work the full queue <ArrowRight size={15}/>
            </button>
          </footer>
        </>
      )}
    </section>
  );
}

/** Presentation-only numerical metric from a verified EOS My Work response. */
function Metric({ label, value, urgent = false }) {
  return (
    <div className="rounded-xl border border-white/10 bg-[#0a1423] px-4 py-3">
      <div className="text-xs text-slate-400">{label}</div>
      <div className={'mt-1 text-2xl font-semibold tabular-nums ' +
        (urgent ? 'text-rose-200' : 'text-white')}>{value}</div>
    </div>
  );
}

/*
 * ARTIFACT: WilsyHeadquartersDailyBrief.jsx
 * VERSION: v1.0.2-SHARED-PROJECTION-CONTRACT
 * AUTHORITY BOUNDARY: Read-only EOS work projection; source commands only.
 * TENANT POSTURE: Current exact tenant; stale and foreign data suppressed.
 * FAIL-CLOSED POSTURE: Shared contract rejects malformed rows and source coverage.
 * FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
