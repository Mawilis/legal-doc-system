/**
 * SECURITY / PRIVACY POSTURE: No credentials or personal information exposed by this metadata repair.
 * TENANT BOUNDARY: Exact tenant scope, membership and entitlements remain server-governed.
 * AUTHORITY BOUNDARY: No new IAM, admission, session or business execution authority is created.
 * FINANCIAL AUTHORITY BOUNDARY: No financial execution; Kennel EOS remains exclusive.
 * TITLE: WILSY OS Authorised My Work Execution Queue
 * VERSION: v1.9.4-SAFE-MISSING-FIELDS
 * AUTHORITY: Wilsy OS Core Governance
 * EPITOME: Presents the current authenticated unified work projection as a
 *          compact, keyboard-operable queue with source-owned detail actions.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/components/workspaces/MyWorkWorkspace.jsx
 * COLLABORATION / OWNERSHIP: Python EOS /api/my-work owns visibility and
 *                            source services own completion and audit.
 * CERTIFICATION / UPDATE DATE: 2026-11-15
 * CHANGELOG: v1.9.4-SAFE-MISSING-FIELDS displays explicit safe labels when
 *            an optional source status or kind is absent or malformed, rather
 *            than rendering an object or inventing lifecycle data.
 *            v1.9.3-PROJECTION-AS-OF-COUNTS derives due-today from the
 *            exact projection as_of instant so stale snapshots do not cross
 *            a local midnight boundary. v1.9.2-DETAIL-FOCUS-OWNERSHIP moves
 *            keyboard focus into the
 *            detail dialog immediately after it opens, including exact-key
 *            route handoffs. v1.9.1-QUEUE-ROW-ACCESSIBILITY gives each native
 *            row button a
 *            valid list-item parent and restores admitted-source navigation.
 *            v1.9.0-DENSE-EXECUTION-QUEUE replaces expanded work cards with
 *            source-filtered compact rows and an accessible responsive detail
 *            drawer. Existing authenticated projection, exact session scope,
 *            source command endpoints, Legal evidence and cross-view invalidation
 *            remain authoritative. v1.8.0-HR-SOURCE-NAVIGATION exposes only an
 *            EOS-admitted HR workspace navigation handoff; it does not render
 *            personnel data itself or invoke any HR command. v1.7.0-AUTHORIZED-
 *            WORK-CREATION-HANDOFF exposes existing Operations work management.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
 * SECURITY / PRIVACY POSTURE: Only validated current authenticated EOS work is
 *                             rendered; drafts are memory-only and scope-bound.
 * TENANT BOUNDARY: Selection keys only identify records in the current exact-
 *                  tenant and principal projection.
 * AUTHORITY BOUNDARY: Projection metadata never grants access; each source
 *                     independently authorizes its existing completion command.
 * FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively.
 */
import React, { useCallback, useContext, useEffect, useMemo, useRef, useState } from 'react';
import {
  AlertTriangle, CheckCircle2, Circle, Clock3, Loader2, RefreshCw,
  ShieldCheck, X,
} from 'lucide-react';
import { useLocation, useNavigate } from 'react-router-dom';
import api from '../../services/api.js';
import AuthContext from '../../contexts/authContext.jsx';
import { completeLegalWorkItem } from '../../services/legalOperationsService.js';
import { assertUnifiedMyWorkProjection } from '../../services/unifiedMyWorkProjection.js';
import {
  currentUnifiedMyWorkScope,
  invalidateUnifiedMyWork,
} from '../../services/unifiedMyWorkSync.js';

const SOURCE_LABELS = Object.freeze({
  LEGAL: 'Legal',
  OPERATIONS: 'Operations',
  INTELLIGENCE: 'Intelligence',
  CRM: 'CRM',
  HR: 'HR & Hiring',
});
const PRIORITY_ORDER = Object.freeze({ CRITICAL: 0, HIGH: 1, NORMAL: 2, LOW: 3 });
const PRIORITY_STYLE = Object.freeze({
  CRITICAL: 'border-rose-400/50 bg-rose-500/15 text-rose-200',
  HIGH: 'border-orange-400/50 bg-orange-500/15 text-orange-200',
  NORMAL: 'border-sky-400/40 bg-sky-500/10 text-sky-200',
  LOW: 'border-slate-400/40 bg-slate-500/10 text-slate-300',
});

const completionPath = (item) => {
  const id = encodeURIComponent(item.work_item_id);
  if (item.source === 'OPERATIONS' || item.source === 'INTELLIGENCE') {
    return '/tenant-modules/' + item.source.toLowerCase()
      + '/workspace/work-items/' + id + '/complete';
  }
  if (item.source === 'CRM') return '/crm/owner-workspace/work-items/' + id + '/complete';
  return null;
};

const safeErrorCode = (error) => {
  const candidate = error?.response?.data?.detail || error?.message || '';
  return typeof candidate === 'string' && /^[A-Z][A-Z0-9_]{1,95}$/.test(candidate)
    ? candidate : 'MY_WORK_REQUEST_FAILED';
};

const formatDue = (value) => {
  if (!value) return 'No deadline';
  const date = new Date(value);
  return Number.isNaN(date.getTime())
    ? 'Deadline unavailable'
    : date.toLocaleString(undefined, { dateStyle: 'medium', timeStyle: 'short' });
};

const formatVerified = (value) => {
  const date = new Date(value);
  return Number.isNaN(date.getTime())
    ? 'Verification time unavailable'
    : date.toLocaleString(undefined, { dateStyle: 'medium', timeStyle: 'short' });
};

const statusLabel = (item) => (
  typeof item.status === 'string' && item.status.trim() ? item.status : 'Status unavailable'
);
const kindLabel = (item) => (
  typeof item.kind === 'string' && item.kind.trim() ? item.kind : 'Type unavailable'
);

const isDueToday = (item, now = new Date()) => {
  if (!item.due_at) return false;
  const due = new Date(item.due_at);
  return !Number.isNaN(due.getTime())
    && due.getFullYear() === now.getFullYear()
    && due.getMonth() === now.getMonth()
    && due.getDate() === now.getDate();
};

const compareItems = (left, right, sortMode) => {
  if (left.is_overdue !== right.is_overdue) return left.is_overdue ? -1 : 1;
  const leftDue = left.due_at ? new Date(left.due_at).getTime() : Number.POSITIVE_INFINITY;
  const rightDue = right.due_at ? new Date(right.due_at).getTime() : Number.POSITIVE_INFINITY;
  const dueOrder = leftDue - rightDue;
  const priorityOrder = (PRIORITY_ORDER[left.priority] ?? 99)
    - (PRIORITY_ORDER[right.priority] ?? 99);
  const ordered = sortMode === 'priority'
    ? (priorityOrder || dueOrder)
    : (dueOrder || priorityOrder);
  if (ordered) return ordered;
  const sourceOrder = String(left.source).localeCompare(String(right.source));
  return sourceOrder || String(left.source_key).localeCompare(String(right.source_key));
};

/**
 * @description Read current authorized work and present source-owned actions.
 * @collaboration Authenticated routes, Headquarters and Daily Attention handoff.
 * @institutional Route and row selection affect presentation only. EOS validates
 *   current tenant/principal/source admission and each source command separately
 *   authorizes durable completion. Client readback cannot create business truth.
 * @param {{focusWorkItem?: string|null}} [props] Exact source key from a verified
 *   parent projection; a fresh EOS projection must still contain the record.
 * @returns {JSX.Element} Authenticated queue with honest read/action states.
 * @security No browser state grants tenant, Legal, financial or completion authority.
 * @tenant Exact current authenticated scope is enforced on every projection read.
 * @mutation Only existing source-owned command endpoints mutate domain records.
 * @transaction Mongo transaction/session ownership remains inside EOS source services.
 */
export default function MyWorkWorkspace(props = {}) {
  const { focusWorkItem: handoffFocusWorkItem = null } = props;
  const navigate = useNavigate();
  const location = useLocation();
  const auth = useContext(AuthContext);
  const authUser = auth?.user;
  const scopeKey = JSON.stringify([
    auth?.sessionGeneration,
    authUser?.id,
    authUser?.tenantId,
    authUser?.role,
    authUser?.workspaceId,
    authUser?.businessRole,
    authUser?.membershipRevision,
    authUser?.businessRoleRevision,
  ].map((value) => value === null || value === undefined ? '' : String(value)));
  const scopeRef = useRef(scopeKey);
  scopeRef.current = scopeKey;
  const requestRef = useRef(0);
  const requestControllerRef = useRef(null);
  const rowRefs = useRef(new Map());
  const closeButtonRef = useRef(null);
  const queueHeadingRef = useRef(null);
  const previousSelectedRef = useRef(null);
  const pendingRef = useRef(new Set());
  const routeFocus = typeof location.state?.focusWorkItem === 'string'
    ? location.state.focusWorkItem : null;
  const hasParentFocus = Object.prototype.hasOwnProperty.call(props, 'focusWorkItem');
  const focusKey = hasParentFocus
    ? (typeof handoffFocusWorkItem === 'string' ? handoffFocusWorkItem : null)
    : routeFocus;

  const [sourceProjection, setProjection] = useState(null);
  const [projectionScope, setProjectionScope] = useState(null);
  const projection = projectionScope === scopeKey ? sourceProjection : null;
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState('');
  const [errorStatus, setErrorStatus] = useState(null);
  const [selectedKey, setSelectedKey] = useState(null);
  const [sourceFilter, setSourceFilter] = useState('ALL');
  const [search, setSearch] = useState('');
  const [sortMode, setSortMode] = useState('due');
  const [notes, setNotes] = useState({});
  const [legalEvidence, setLegalEvidence] = useState({});
  const [completing, setCompleting] = useState('');
  const [actionError, setActionError] = useState('');
  const [closeGuard, setCloseGuard] = useState(false);

  const load = useCallback(async ({ quiet = false } = {}) => {
    const request = ++requestRef.current;
    requestControllerRef.current?.abort();
    const controller = new AbortController();
    requestControllerRef.current = controller;
    if (quiet) setRefreshing(true);
    else setLoading(true);
    setError('');
    setErrorStatus(null);
    try {
      const response = await api.get('/my-work', {
        forceNetworkRetry: true,
        signal: controller.signal,
      });
      if (request !== requestRef.current || scopeRef.current !== scopeKey) return null;
      const verified = assertUnifiedMyWorkProjection(response?.data, {
        tenantId: authUser?.tenantId,
        principalId: authUser?.id,
      });
      setProjection(verified);
      setProjectionScope(scopeKey);
      return verified;
    } catch (requestError) {
      if (request !== requestRef.current || scopeRef.current !== scopeKey) return null;
      const status = requestError?.response?.status;
      const code = safeErrorCode(requestError);
      const mustClear = status === 401 || status === 403
        || code === 'MY_WORK_SCOPE_MISMATCH';
      if (mustClear || !quiet) {
        setProjection(null);
        setProjectionScope(null);
      }
      setError(code);
      setErrorStatus(status);
      return null;
    } finally {
      if (request === requestRef.current && scopeRef.current === scopeKey) {
        if (requestControllerRef.current === controller) requestControllerRef.current = null;
        setLoading(false);
        setRefreshing(false);
      }
    }
  }, [authUser?.id, authUser?.tenantId, scopeKey]);

  useEffect(() => {
    void load();
    return () => {
      requestRef.current += 1;
      requestControllerRef.current?.abort();
      requestControllerRef.current = null;
    };
  }, [load, location.key, focusKey]);

  useEffect(() => {
    setNotes({});
    setLegalEvidence({});
    setCompleting('');
    setActionError('');
    setSelectedKey(null);
    setCloseGuard(false);
    setSourceFilter('ALL');
    setSearch('');
    pendingRef.current.clear();
  }, [scopeKey]);

  const items = useMemo(() => projection?.items || [], [projection]);
  const selectedItem = items.find((item) => item.source_key === selectedKey) || null;
  const admittedSources = projection?.sources_included || [];
  const dueTodayCount = useMemo(() => {
    if (!projection) return 0;
    const snapshotTime = new Date(projection.as_of);
    return items.filter((item) => isDueToday(item, snapshotTime)).length;
  }, [items, projection]);
  const filteredItems = useMemo(() => {
    const query = search.trim().toLocaleLowerCase();
    return items
      .filter((item) => sourceFilter === 'ALL' || item.source === sourceFilter)
      .filter((item) => !query || [item.title, item.description, item.source,
        SOURCE_LABELS[item.source], item.status].some((value) => (
        typeof value === 'string' && value.toLocaleLowerCase().includes(query)
      )))
      .sort((left, right) => compareItems(left, right, sortMode));
  }, [items, search, sortMode, sourceFilter]);

  useEffect(() => {
    if (!focusKey || !items.some((item) => item.source_key === focusKey)) return;
    rowRefs.current.get(focusKey)?.focus();
    rowRefs.current.get(focusKey)?.scrollIntoView?.({ behavior: 'smooth', block: 'center' });
    setSelectedKey(focusKey);
  }, [items, focusKey]);

  useEffect(() => {
    if (selectedKey) {
      previousSelectedRef.current = selectedKey;
      closeButtonRef.current?.focus();
      return undefined;
    }
    if (previousSelectedRef.current) {
      const prior = previousSelectedRef.current;
      previousSelectedRef.current = null;
      window.requestAnimationFrame(() => {
        const row = rowRefs.current.get(prior);
        if (row?.isConnected) row.focus();
        else queueHeadingRef.current?.focus();
      });
    }
    return undefined;
  }, [selectedKey]);

  useEffect(() => {
    if (selectedKey && !items.some((item) => item.source_key === selectedKey)) {
      setSelectedKey(null);
      setCloseGuard(false);
    }
  }, [items, selectedKey]);

  useEffect(() => {
    if (!selectedKey) return undefined;
    const onKeyDown = (event) => {
      if (event.key === 'Escape') {
        event.preventDefault();
        requestClose();
        return;
      }
      if (event.key !== 'Tab') return;
      const dialog = document.getElementById('my-work-detail-dialog');
      const focusable = dialog?.querySelectorAll(
        'button:not([disabled]), input:not([disabled]), textarea:not([disabled]), [tabindex="0"]',
      );
      if (!focusable?.length) return;
      const first = focusable[0];
      const last = focusable[focusable.length - 1];
      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault();
        last.focus();
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault();
        first.focus();
      }
    };
    document.addEventListener('keydown', onKeyDown);
    return () => document.removeEventListener('keydown', onKeyDown);
  });

  const hasDraft = (item) => Boolean(
    String(notes[item.source_key] || '').trim()
    || String(legalEvidence[item.source_key]?.reference || '').trim()
    || String(legalEvidence[item.source_key]?.fingerprint || '').trim(),
  );

  function requestClose() {
    if (!selectedItem || completing === selectedItem.source_key) return;
    if (hasDraft(selectedItem)) {
      setCloseGuard(true);
      return;
    }
    setActionError('');
    setSelectedKey(null);
  }

  const discardDraftAndClose = () => {
    if (!selectedItem) return;
    setNotes((current) => ({ ...current, [selectedItem.source_key]: '' }));
    setLegalEvidence((current) => ({ ...current, [selectedItem.source_key]: { reference: '', fingerprint: '' } }));
    setActionError('');
    setCloseGuard(false);
    setSelectedKey(null);
  };

  const complete = async (item) => {
    if (pendingRef.current.has(item.source_key)) return;
    const commandScope = scopeKey;
    const path = completionPath(item);
    const note = String(notes[item.source_key] || '').trim();
    const evidence = legalEvidence[item.source_key] || {};
    if (item.source === 'LEGAL') {
      if (!String(evidence.reference || '').trim()
        || !/^[a-f0-9]{128}$/.test(String(evidence.fingerprint || ''))) return;
    } else if (!path || !note) return;

    pendingRef.current.add(item.source_key);
    setCompleting(item.source_key);
    setActionError('');
    try {
      let receipt;
      if (item.source === 'LEGAL') {
        receipt = await completeLegalWorkItem({
          workItemId: item.work_item_id,
          completionEvidenceReference: String(evidence.reference).trim(),
          completionEvidenceFingerprint: String(evidence.fingerprint).trim(),
        });
        if (receipt?.work_item_id !== item.work_item_id) {
          throw new Error('LEGAL_WORK_COMPLETION_RECEIPT_INVALID');
        }
      } else {
        const response = await api.post(path, { completion_note: note });
        receipt = response?.data;
        if (receipt?.work_item_id !== item.work_item_id || receipt?.status !== 'COMPLETED') {
          throw new Error('WORK_ITEM_COMPLETION_RECEIPT_INVALID');
        }
      }
      if (scopeRef.current !== commandScope) return;

      invalidateUnifiedMyWork(currentUnifiedMyWorkScope(auth, authUser?.tenantId));
      const refreshed = await load({ quiet: true });
      if (scopeRef.current !== commandScope) return;
      if (!refreshed) {
        setActionError('WORK_ITEM_COMPLETED_READBACK_UNAVAILABLE');
        return;
      }
      if (refreshed.items.some((candidate) => candidate.source_key === item.source_key)) {
        setActionError('WORK_ITEM_COMPLETION_NOT_REFLECTED');
        return;
      }
      setNotes((current) => ({ ...current, [item.source_key]: '' }));
      setLegalEvidence((current) => ({ ...current, [item.source_key]: { reference: '', fingerprint: '' } }));
      setActionError('');
      setCloseGuard(false);
      setSelectedKey(null);
    } catch (requestError) {
      if (scopeRef.current !== commandScope) return;
      setActionError(safeErrorCode(requestError));
    } finally {
      pendingRef.current.delete(item.source_key);
      if (scopeRef.current === commandScope) setCompleting('');
    }
  };

  if (loading && !projection) {
    return (
      <main className="min-h-screen bg-[#080b10] text-white flex items-center justify-center">
        <div role="status" className="flex items-center gap-3 text-sm text-amber-200">
          <Loader2 className="animate-spin" size={20} /> Verifying your authorized work…
        </div>
      </main>
    );
  }

  if (!projection) {
    const denied = errorStatus === 401 || errorStatus === 403;
    return (
      <main className="min-h-screen bg-[#080b10] text-white px-5 py-10">
        <section className="mx-auto max-w-3xl rounded-2xl border border-red-900/60 bg-[#111720] p-6" role="alert">
          <div className="flex items-center gap-3 text-red-200"><AlertTriangle size={20} />
            {denied ? 'Access to My Work was denied' : 'My Work is unavailable'}
          </div>
          <p className="mt-3 text-sm text-slate-300">
            {denied
              ? 'EOS did not authorize this work projection for the current session.'
              : 'EOS could not verify the authorized source projection. No stale or synthetic queue is displayed.'}
          </p>
          <p className="mt-2 font-mono text-xs text-slate-500">{error || 'MY_WORK_UNAVAILABLE'}</p>
          <button type="button" onClick={() => load()} className="mt-5 rounded-lg border border-amber-500/50 px-4 py-2 text-sm text-amber-100">Retry</button>
        </section>
      </main>
    );
  }

  return (
    <div className="min-h-screen bg-[#080b10] text-slate-100">
      <main
        aria-hidden={selectedItem ? 'true' : undefined}
        className="min-h-screen px-3 py-4 sm:px-6 sm:py-6 lg:px-10"
      >
        <div className="mx-auto max-w-7xl">
          <header className="flex flex-wrap items-center justify-between gap-3 border-b border-white/10 pb-4">
            <div className="min-w-0">
              <div className="flex items-center gap-2 text-[10px] uppercase tracking-[0.2em] text-amber-300">
                <ShieldCheck size={14} /> WILSY OS / Daily execution
              </div>
              <h1 ref={queueHeadingRef} tabIndex={-1} className="mt-1 text-2xl font-semibold tracking-tight outline-none sm:text-3xl">My Work</h1>
              <p className="sr-only">Authorized work across your current business capacity.</p>
            </div>
            <div className="flex items-center gap-2">
              {admittedSources.includes('OPERATIONS') && (
                <button type="button" onClick={() => navigate('/headquarters?section=operations')}
                  className="hidden rounded-lg border border-amber-300/25 px-3 py-2 text-xs text-amber-100 hover:bg-amber-300/5 md:inline-flex">
                  Operations work
                </button>
              )}
              {admittedSources.includes('HR') && (
                <button type="button" onClick={() => navigate('/headquarters?section=hiring')}
                  className="hidden rounded-lg border border-amber-300/25 px-3 py-2 text-xs text-amber-100 hover:bg-amber-300/5 md:inline-flex">
                  Open HR &amp; Hiring
                </button>
              )}
              <div className="hidden text-right text-xs text-slate-400 sm:block">
                <div><span className="text-white">{projection.summary.active_count}</span> open · <span className="text-rose-200">{projection.summary.overdue_count}</span> overdue</div>
                <div className="mt-1">Verified {formatVerified(projection.as_of)}</div>
              </div>
              <button type="button" onClick={() => load({ quiet: true })} disabled={refreshing}
                className="inline-flex min-h-10 items-center gap-2 rounded-lg border border-white/15 bg-white/5 px-3 py-2 text-sm hover:bg-white/10 disabled:opacity-60"
                aria-label={refreshing ? 'Refreshing My Work' : 'Refresh My Work'}>
                <RefreshCw size={15} className={refreshing ? 'animate-spin' : ''} />
                <span className="hidden sm:inline">Refresh</span>
              </button>
            </div>
          </header>

          <div className="flex flex-wrap items-center gap-x-4 gap-y-1 border-b border-white/10 py-2 text-xs sm:hidden">
            <span>{projection.summary.active_count} open</span>
            <span className="text-rose-200">{projection.summary.overdue_count} overdue</span>
            <span className="text-slate-400">Verified {formatVerified(projection.as_of)}</span>
          </div>

          {refreshing && <div role="status" className="border-b border-amber-300/20 bg-amber-300/5 px-3 py-2 text-xs text-amber-100">Refreshing EOS projection; the displayed rows are the last verified snapshot.</div>}
          {error && projection && <div role="alert" className="border-b border-rose-400/20 bg-rose-950/20 px-3 py-2 text-xs text-rose-200">Refresh failed ({error}). Displayed rows remain the prior verified snapshot.</div>}
          {actionError && <div role="alert" className="mt-3 rounded-lg border border-rose-400/25 bg-rose-950/20 px-3 py-2 text-sm text-rose-200">The source action was not confirmed in the current queue: {actionError}</div>}

          <section aria-label="Work queue summary" className="flex flex-wrap gap-2 border-b border-white/10 py-3 text-xs">
            <Summary label="Open" value={projection.summary.active_count} />
            <Summary label="Overdue count" value={projection.summary.overdue_count} tone="rose" />
            <Summary label="Due today" value={dueTodayCount} tone="amber" />
          </section>

          <section className="flex flex-wrap items-center justify-between gap-3 border-b border-white/10 py-3" aria-label="Work source filters">
            <div className="flex flex-wrap gap-2">
              <FilterButton active={sourceFilter === 'ALL'} onClick={() => setSourceFilter('ALL')}>
                All <span className="tabular-nums">{items.length}</span>
              </FilterButton>
              {admittedSources.map((source) => (
                <FilterButton key={source} active={sourceFilter === source} onClick={() => setSourceFilter(source)}>
                  {SOURCE_LABELS[source] || source}
                  <span className="tabular-nums">{projection.summary.source_counts[source]}</span>
                </FilterButton>
              ))}
            </div>
            <span className="text-[11px] text-slate-500">Only independently admitted sources appear here.</span>
          </section>

          <section className="flex flex-col gap-2 py-3 sm:flex-row sm:items-center">
            <label className="sr-only" htmlFor="my-work-search">Search authorized work</label>
            <input id="my-work-search" type="search" value={search} onChange={(event) => setSearch(event.target.value)}
              placeholder="Search title, description or source…"
              className="min-h-10 min-w-0 flex-1 rounded-lg border border-white/15 bg-[#0b1421] px-3 text-sm text-white outline-none placeholder:text-slate-500 focus:border-amber-300/70" />
            <label className="flex items-center gap-2 text-xs text-slate-400">
              Sort
              <select value={sortMode} onChange={(event) => setSortMode(event.target.value)}
                className="min-h-10 rounded-lg border border-white/15 bg-[#0b1421] px-3 text-sm text-slate-100 focus:border-amber-300/70">
                <option value="due">Due soon, then priority</option>
                <option value="priority">Priority, then due</option>
              </select>
            </label>
          </section>

          <section aria-label="Authorized work queue" className="overflow-hidden rounded-xl border border-white/10 bg-[#0c1420]">
            <div className="hidden grid-cols-[minmax(0,1fr)_7rem_9rem_7rem] gap-3 border-b border-white/10 bg-white/[0.025] px-4 py-2 text-[10px] uppercase tracking-[0.14em] text-slate-500 sm:grid">
              <span>Work</span><span>Priority</span><span>Deadline</span><span>Status</span>
            </div>
            {filteredItems.length ? (
              <div role="list" aria-label="Authorized work items" className="divide-y divide-white/[0.07]">
                {filteredItems.map((item) => {
                  const selected = selectedKey === item.source_key;
                  return (
                    <article key={item.source_key} role="listitem"
                      className={`border-l-2 ${selected ? 'border-l-amber-300 bg-amber-300/[0.07] ring-2 ring-inset ring-amber-300/60' : 'border-l-transparent'}`}>
                      <button type="button" aria-pressed={selected}
                        aria-label={`${item.title}, ${SOURCE_LABELS[item.source]}, ${item.priority}, ${statusLabel(item)}${item.is_overdue ? ', overdue' : ''}`}
                        ref={(element) => {
                          if (element) rowRefs.current.set(item.source_key, element);
                          else rowRefs.current.delete(item.source_key);
                        }}
                        onClick={() => { setActionError(''); setCloseGuard(false); setSelectedKey(item.source_key); }}
                        className="grid min-h-[4.25rem] w-full grid-cols-1 items-center gap-2 px-3 py-2 text-left outline-none hover:bg-white/[0.035] focus-visible:ring-2 focus-visible:ring-inset focus-visible:ring-amber-300 sm:grid-cols-[minmax(0,1fr)_7rem_9rem_7rem] sm:gap-3 sm:px-4">
                        <span className="min-w-0">
                          <span className="flex min-w-0 flex-wrap items-center gap-x-2 gap-y-1">
                            <span className="truncate text-sm font-medium text-white">{item.title}</span>
                            {item.is_overdue && <span className="rounded border border-rose-400/30 bg-rose-500/10 px-1.5 py-0.5 text-[9px] font-semibold uppercase tracking-wide text-rose-200">Overdue</span>}
                          </span>
                          <span className="mt-1 flex flex-wrap items-center gap-2 text-[11px] text-slate-400">
                            <span className="rounded border border-amber-300/20 bg-amber-300/[0.06] px-1.5 py-0.5 text-amber-100">{SOURCE_LABELS[item.source] || item.source}</span>
                            <span>{kindLabel(item)}</span>
                          </span>
                        </span>
                        <span className="flex items-center gap-2 text-xs sm:block">
                          <span className="text-slate-500 sm:hidden">Priority</span>
                          <span className={`inline-flex rounded border px-2 py-1 text-[10px] font-semibold uppercase ${PRIORITY_STYLE[item.priority] || PRIORITY_STYLE.NORMAL}`}>{item.priority}</span>
                        </span>
                        <span className="flex items-center gap-1.5 text-xs text-slate-300">
                          <Clock3 size={13} className="shrink-0 text-slate-500" /> {formatDue(item.due_at)}
                        </span>
                        <span className="inline-flex items-center gap-1.5 text-xs text-slate-300">
                          <Circle size={9} className={item.is_overdue ? 'fill-rose-300 text-rose-300' : 'text-slate-500'} /> {statusLabel(item)}
                        </span>
                      </button>
                    </article>
                  );
                })}
              </div>
            ) : items.length === 0 ? (
              <div className="px-4 py-10 text-center" role="status">
                <CheckCircle2 className="mx-auto text-emerald-300" size={25} />
                <h2 className="mt-2 text-sm font-medium text-white">
                  {admittedSources.length ? 'No active work in admitted sources' : 'No source was admitted'}
                </h2>
                <p className="mt-1 text-xs text-slate-400">
                  {admittedSources.length
                    ? 'EOS verified the current admitted queues as empty.'
                    : 'This is not evidence that other business queues are empty.'}
                </p>
              </div>
            ) : (
              <div className="px-4 py-8 text-center text-sm text-slate-400" role="status">
                No work matches the current source filter and search.
                <button type="button" className="ml-2 text-amber-200 underline" onClick={() => { setSearch(''); setSourceFilter('ALL'); }}>Clear filters</button>
              </div>
            )}
          </section>
          <footer className="flex flex-wrap items-center justify-between gap-2 py-3 text-[11px] text-slate-500">
            <span>{filteredItems.length} shown · {items.length} in last verified projection · {admittedSources.length} admitted source{admittedSources.length === 1 ? '' : 's'}</span>
            <span>Commands remain owned by each source service.</span>
          </footer>
        </div>
      </main>

      {selectedItem && (
        <div className="fixed inset-0 z-50 flex justify-end bg-black/55" onMouseDown={(event) => {
          if (event.target === event.currentTarget) requestClose();
        }}>
          <aside id="my-work-detail-dialog" role="dialog" aria-modal="true"
            aria-labelledby="my-work-detail-title" aria-describedby="my-work-detail-description"
            className="flex h-full w-full max-w-full flex-col overflow-y-auto border-l border-white/10 bg-[#101b2b] shadow-2xl outline-none md:max-w-[30rem]">
            <header className="flex items-start justify-between gap-3 border-b border-white/10 px-4 py-4 sm:px-6">
              <div className="min-w-0">
                <p className="text-[10px] uppercase tracking-[0.18em] text-amber-200">{SOURCE_LABELS[selectedItem.source] || selectedItem.source} work</p>
                <h2 id="my-work-detail-title" className="mt-1 break-words text-xl font-semibold text-white">{selectedItem.title}</h2>
              </div>
              <button ref={closeButtonRef} type="button" onClick={requestClose} aria-label="Close work details"
                className="inline-flex h-9 w-9 shrink-0 items-center justify-center rounded-lg border border-white/10 text-slate-300 hover:bg-white/5 focus-visible:outline focus-visible:outline-2 focus-visible:outline-amber-300">
                <X size={18} />
              </button>
            </header>

            <div className="flex-1 space-y-4 p-4 sm:p-6">
              <div className="flex flex-wrap items-center gap-2">
                <span className="rounded border border-amber-300/25 bg-amber-300/[0.07] px-2 py-1 text-xs text-amber-100">{SOURCE_LABELS[selectedItem.source] || selectedItem.source}</span>
                <span className={`rounded border px-2 py-1 text-xs font-semibold ${PRIORITY_STYLE[selectedItem.priority] || PRIORITY_STYLE.NORMAL}`}>{selectedItem.priority}</span>
                <span className="inline-flex items-center gap-1.5 rounded border border-white/10 px-2 py-1 text-xs text-slate-300"><Circle size={9} /> {statusLabel(selectedItem)}</span>
              </div>
              <dl className="grid grid-cols-[6rem_1fr] gap-x-3 gap-y-2 border-y border-white/10 py-3 text-sm">
                <dt className="text-slate-400">Deadline</dt><dd className="text-slate-100">{formatDue(selectedItem.due_at)}</dd>
                <dt className="text-slate-400">Work type</dt><dd className="text-slate-100">{kindLabel(selectedItem)}</dd>
              </dl>
              <section>
                <h3 className="text-sm font-semibold text-white">Description</h3>
                <p id="my-work-detail-description" className="mt-1 whitespace-pre-wrap break-words text-sm leading-6 text-slate-300">
                  {typeof selectedItem.description === 'string' && selectedItem.description.trim()
                    ? selectedItem.description : 'No description was supplied by the source.'}
                </p>
              </section>

              {selectedItem.source === 'LEGAL' ? (
                <section className="space-y-3 border-t border-white/10 pt-4" aria-label="Legal completion evidence">
                  <p className="text-xs text-slate-400">EOS requires source evidence for this Legal completion. My Work cannot create or infer that evidence.</p>
                  <label className="grid gap-1 text-xs text-slate-300">
                    Completion evidence reference
                    <input value={legalEvidence[selectedItem.source_key]?.reference || ''}
                      onChange={(event) => setLegalEvidence((current) => ({
                        ...current,
                        [selectedItem.source_key]: { ...current[selectedItem.source_key], reference: event.target.value },
                      }))}
                      aria-label="Legal completion evidence reference" maxLength={500}
                      className="min-h-10 min-w-0 rounded-lg border border-white/15 bg-black/20 px-3 text-sm text-white outline-none focus:border-amber-300" />
                  </label>
                  <label className="grid gap-1 text-xs text-slate-300">
                    SHA3-512 evidence fingerprint
                    <input value={legalEvidence[selectedItem.source_key]?.fingerprint || ''}
                      onChange={(event) => setLegalEvidence((current) => ({
                        ...current,
                        [selectedItem.source_key]: { ...current[selectedItem.source_key], fingerprint: event.target.value },
                      }))}
                      aria-label="Legal completion evidence fingerprint" maxLength={128} pattern="[a-f0-9]{128}"
                      className="min-h-10 min-w-0 rounded-lg border border-white/15 bg-black/20 px-3 font-mono text-xs text-white outline-none focus:border-amber-300" />
                  </label>
                </section>
              ) : completionPath(selectedItem) ? (
                <label className="grid gap-1 border-t border-white/10 pt-4 text-xs text-slate-300">
                  Completion note <span className="text-slate-500">(required by this source)</span>
                  <textarea value={notes[selectedItem.source_key] || ''}
                    onChange={(event) => setNotes((current) => ({ ...current, [selectedItem.source_key]: event.target.value }))}
                    aria-label="Completion note" maxLength={1000} rows={3}
                    className="min-h-24 resize-y rounded-lg border border-white/15 bg-black/20 px-3 py-2 text-sm text-white outline-none focus:border-amber-300" />
                </label>
              ) : (
                <p className="border-t border-white/10 pt-4 text-xs text-slate-400">This source does not expose a completion action in the current My Work contract.</p>
              )}

              {actionError && <div role="alert" className="rounded-lg border border-rose-400/25 bg-rose-950/20 px-3 py-2 text-sm text-rose-200">EOS did not confirm completion: {actionError}. The work remains in the last verified queue until a fresh projection confirms its state.</div>}
              {closeGuard && (
                <section aria-label="Unsaved completion evidence" className="rounded-lg border border-amber-300/30 bg-amber-300/[0.06] p-3">
                  <p className="text-sm text-amber-100">Discard the unsent completion note or evidence?</p>
                  <div className="mt-3 flex flex-wrap justify-end gap-2">
                    <button type="button" onClick={() => setCloseGuard(false)} className="rounded-lg border border-white/15 px-3 py-2 text-sm">Keep editing</button>
                    <button type="button" onClick={discardDraftAndClose} className="rounded-lg border border-rose-400/40 px-3 py-2 text-sm text-rose-200">Discard and close</button>
                  </div>
                </section>
              )}
            </div>

            {completionPath(selectedItem) || selectedItem.source === 'LEGAL' ? (
              <footer className="border-t border-white/10 p-4 sm:p-6">
                <button type="button" onClick={() => complete(selectedItem)}
                  disabled={completing === selectedItem.source_key || closeGuard
                    || (selectedItem.source === 'LEGAL'
                      ? !String(legalEvidence[selectedItem.source_key]?.reference || '').trim()
                        || !/^[a-f0-9]{128}$/.test(String(legalEvidence[selectedItem.source_key]?.fingerprint || ''))
                      : !String(notes[selectedItem.source_key] || '').trim())}
                  className="inline-flex min-h-11 w-full items-center justify-center gap-2 rounded-lg bg-amber-300 px-4 py-2.5 text-sm font-semibold text-slate-950 hover:bg-amber-200 disabled:cursor-not-allowed disabled:opacity-50">
                  {completing === selectedItem.source_key
                    ? <><Loader2 size={16} className="animate-spin" /> Submitting to EOS…</>
                    : <><CheckCircle2 size={16} /> Complete through {SOURCE_LABELS[selectedItem.source] || selectedItem.source}</>}
                </button>
              </footer>
            ) : null}
          </aside>
        </div>
      )}
    </div>
  );
}

function Summary({ label, value, tone = 'default' }) {
  const styles = tone === 'rose' ? 'text-rose-200' : tone === 'amber' ? 'text-amber-100' : 'text-slate-100';
  return <div className="rounded-md border border-white/10 bg-white/[0.025] px-3 py-1.5 text-xs"><span className="text-slate-400">{label}</span><span className={`ml-2 font-semibold tabular-nums ${styles}`}>{value}</span></div>;
}

function FilterButton({ active, onClick, children }) {
  return (
    <button type="button" aria-pressed={active} onClick={onClick}
      className={`inline-flex min-h-8 items-center gap-2 rounded-full border px-3 py-1.5 text-xs focus-visible:outline focus-visible:outline-2 focus-visible:outline-amber-300 ${active
        ? 'border-amber-300/60 bg-amber-300/10 text-amber-100'
        : 'border-white/15 text-slate-300 hover:bg-white/5'}`}>
      {children}
    </button>
  );
}

/*
 * ARTIFACT: MyWorkWorkspace.jsx
 * VERSION: v1.9.4-SAFE-MISSING-FIELDS
 * AUTHORITY BOUNDARY: Read-only validated projection plus source-owned commands.
 * TENANT POSTURE: Current exact authenticated tenant and principal only.
 * FAIL-CLOSED POSTURE: Invalid/denied projections clear queue; failed refreshes are marked stale.
 * FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
