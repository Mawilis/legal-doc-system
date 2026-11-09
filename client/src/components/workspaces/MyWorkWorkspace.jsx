/**
 * TITLE: WILSY OS Authorised My Work Completion Workspace
 * VERSION: v1.4.0-VERIFIED-PROJECTION-FOCUS-HANDOFF
 * AUTHORITY: Wilsy OS Core Governance
 * EPITOME: Executes source-owned evidenced work completion and focuses the
 *          item selected from Daily Attention or Headquarters.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/components/workspaces/MyWorkWorkspace.jsx
 * COLLABORATION / OWNERSHIP: Python EOS /api/my-work owns visibility and
 *                            source services own completion and audit.
 * CERTIFICATION / UPDATE DATE: 2026-11-09
 * CHANGELOG: v1.4.0-VERIFIED-PROJECTION-FOCUS-HANDOFF validates every My Work
 *            read with the shared tenant/principal/source coverage contract
 *            and accepts an exact source-key focus handoff from Headquarters.
 *            v1.3.0-SESSION-GENERATION-CURRENTNESS binds projection, command
 *            freshness, and transient drafts to auth session generation,
 *            membership revision, and selected business-role revision; stale
 *            source reads are cancelled and late results remain suppressed.
 *            v1.2.0-SCOPED-NAVIGATION-SOURCE-REFRESH revalidates work on
 *            same-route navigation and authenticated scope changes, rejects
 *            late source responses, clears prior-scope drafts and focuses only
 *            newly read source work. No source command authority is changed.
 *            v1.1.0-ATTENTION-DEEP-LINK-FOCUS added visual and accessible
 *            focus to selected work without treating route state as authority.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
 * SECURITY / PRIVACY POSTURE: Only current authenticated EOS work is rendered;
 *                             stale reads and work drafts are discarded.
 * TENANT BOUNDARY: Selected keys only match the EOS-authorised item list.
 * AUTHORITY BOUNDARY: Completion commands remain source-owned.
 * FINANCIAL AUTHORITY BOUNDARY: Kennel EOS only.
 */
import React, { useCallback, useContext, useEffect, useMemo, useRef, useState } from 'react';
import { AlertTriangle, CheckCircle2, Circle, Clock3, Loader2, RefreshCw, ShieldCheck } from 'lucide-react';
import { useLocation, useNavigate } from 'react-router-dom';
import api from '../../services/api.js';
import AuthContext from '../../contexts/authContext.jsx';
import { completeLegalWorkItem } from '../../services/legalOperationsService.js';
import { assertUnifiedMyWorkProjection } from '../../services/unifiedMyWorkProjection.js';

const SOURCE_LABELS = Object.freeze({
  LEGAL: 'Legal',
  OPERATIONS: 'Operations',
  INTELLIGENCE: 'Intelligence',
  CRM: 'CRM',
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

const formatDue = (value) => {
  if (!value) return 'No due date';
  const date = new Date(value);
  return Number.isNaN(date.getTime())
    ? 'Due date unavailable'
    : date.toLocaleString(undefined, { dateStyle: 'medium', timeStyle: 'short' });
};

/**
 * @description Read current assigned work and hand completion to its owning EOS service.
 * @collaboration Authenticated routes, Headquarters and Daily Attention calendar handoff.
 * @institutional Route or parent handoff state selects focus only. The shared
 * projection contract verifies schema, row identity, source coverage and exact
 * scope. Tenant, principal, capacity and permissions remain EOS-owned; source
 * services own transactions, completion evidence and durable command replay.
 * @param {{focusWorkItem?: string|null}} [props] Optional exact source key from
 *   the Headquarters read-only brief; a match is still required in EOS results.
 * @returns {JSX.Element} Current source queue, loading or bounded unavailable state.
 * No client state establishes legal, financial, MFA or notification authority.
 */
export default function MyWorkWorkspace({ focusWorkItem: handoffFocusWorkItem = null } = {}) {
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
  const focusRef = useRef(null);
  const routeFocus = typeof location.state?.focusWorkItem === 'string'
    ? location.state.focusWorkItem : null;
  const focusKey = typeof handoffFocusWorkItem === 'string'
    ? handoffFocusWorkItem
    : routeFocus;
  const [sourceProjection, setProjection] = useState(null);
  const [projectionScope, setProjectionScope] = useState(null);
  const projection = projectionScope === scopeKey ? sourceProjection : null;
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState('');
  const [notes, setNotes] = useState({});
  const [legalEvidence, setLegalEvidence] = useState({});
  const [completing, setCompleting] = useState('');
  const [actionError, setActionError] = useState('');

  const load = useCallback(async ({ quiet = false } = {}) => {
    const request = ++requestRef.current;
    requestControllerRef.current?.abort();
    const controller = new AbortController();
    requestControllerRef.current = controller;
    if (quiet) setRefreshing(true);
    else setLoading(true);
    setError('');
    try {
      const response = await api.get('/my-work', {
        forceNetworkRetry: true,
        signal: controller.signal,
      });
      if (request !== requestRef.current || scopeRef.current !== scopeKey) return;
      const verified = assertUnifiedMyWorkProjection(response?.data, {
        tenantId: authUser?.tenantId,
        principalId: authUser?.id,
      });
      setProjection(verified);
      setProjectionScope(scopeKey);
    } catch (requestError) {
      if (request !== requestRef.current || scopeRef.current !== scopeKey) return;
      setProjection(null);
      setProjectionScope(null);
      setError(requestError?.response?.data?.detail || requestError?.message || 'MY_WORK_UNAVAILABLE');
    } finally {
      if (request === requestRef.current && scopeRef.current === scopeKey) {
        if (requestControllerRef.current === controller) requestControllerRef.current = null;
        setLoading(false);
        setRefreshing(false);
      }
    }
  }, [scopeKey]);

  useEffect(() => {
    // Same-path attention handoffs re-read EOS before focusing current work.
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
  }, [scopeKey]);

  const items = useMemo(() => projection?.items || [], [projection]);
  useEffect(() => {
    if (!focusKey || !items.some((item) => item.source_key === focusKey)) return;
    focusRef.current?.focus();
    focusRef.current?.scrollIntoView?.({ behavior: 'smooth', block: 'center' });
  }, [items, focusKey]);

  const complete = async (item) => {
    const commandScope = scopeKey;
    const path = completionPath(item);
    const note = String(notes[item.source_key] || '').trim();
    const evidence = legalEvidence[item.source_key] || {};
    if (item.source === 'LEGAL') {
      if (!String(evidence.reference || '').trim() || !/^[a-f0-9]{128}$/.test(String(evidence.fingerprint || ''))) return;
    } else if (!path || !note) return;
    setCompleting(item.source_key);
    setActionError('');
    try {
      if (item.source === 'LEGAL') {
        await completeLegalWorkItem({ workItemId: item.work_item_id, completionEvidenceReference: String(evidence.reference).trim(), completionEvidenceFingerprint: String(evidence.fingerprint).trim() });
        if (scopeRef.current !== commandScope) return;
        setLegalEvidence((current) => ({ ...current, [item.source_key]: { reference: '', fingerprint: '' } }));
      } else {
        await api.post(path, { completion_note: note });
        if (scopeRef.current !== commandScope) return;
        setNotes((current) => ({ ...current, [item.source_key]: '' }));
      }
      await load({ quiet: true });
    } catch (requestError) {
      if (scopeRef.current !== commandScope) return;
      setActionError(requestError?.response?.data?.detail || 'WORK_ITEM_COMPLETION_UNAVAILABLE');
    } finally {
      if (scopeRef.current === commandScope) setCompleting('');
    }
  };

  if (loading) {
    return (
      <main className="min-h-screen bg-[#080b10] text-white flex items-center justify-center">
        <div role="status" className="flex items-center gap-3 text-sm text-amber-200">
          <Loader2 className="animate-spin" size={20} /> Loading your authorized work…
        </div>
      </main>
    );
  }

  if (error || !projection) {
    return (
      <main className="min-h-screen bg-[#080b10] text-white px-5 py-10">
        <section className="mx-auto max-w-3xl rounded-2xl border border-red-900/60 bg-[#111720] p-6" role="alert">
          <div className="flex items-center gap-3 text-red-200"><AlertTriangle size={20} /> My Work is unavailable</div>
          <p className="mt-3 text-sm text-slate-300">The workspace could not verify every authorized source required for this request. No stale or synthetic queue is being displayed.</p>
          <p className="mt-2 font-mono text-xs text-slate-500">{error || 'MY_WORK_UNAVAILABLE'}</p>
          <button onClick={() => load()} className="mt-5 rounded-lg border border-amber-500/50 px-4 py-2 text-sm text-amber-100">Retry</button>
        </section>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-[#080b10] px-4 py-6 text-slate-100 sm:px-6 lg:px-10">
      <div className="mx-auto max-w-7xl">
        <header className="flex flex-wrap items-start justify-between gap-4 border-b border-white/10 pb-6">
          <div>
            <button onClick={() => navigate('/')} className="mb-4 text-xs uppercase tracking-[0.2em] text-slate-400 hover:text-white">← Workspace home</button>
            <div className="flex items-center gap-2 text-xs uppercase tracking-[0.24em] text-amber-300"><ShieldCheck size={15} /> WILSY OS / Daily execution</div>
            <h1 className="mt-2 text-3xl font-semibold tracking-tight sm:text-4xl">My Work</h1>
            <p className="mt-2 max-w-2xl text-sm text-slate-400">One operational queue, assembled only from work your current authenticated business capacity is authorized to see.</p>
          </div>
          <button onClick={() => load({ quiet: true })} disabled={refreshing} className="inline-flex items-center gap-2 rounded-xl border border-white/15 bg-white/5 px-4 py-2.5 text-sm hover:bg-white/10 disabled:opacity-50">
            <RefreshCw size={15} className={refreshing ? 'animate-spin' : ''} /> Refresh
          </button>
        </header>

        <section className="grid grid-cols-2 gap-3 py-6 sm:grid-cols-4">
          <Metric label="Active work" value={projection.summary.active_count} />
          <Metric label="Overdue" value={projection.summary.overdue_count} />
          <Metric label="Sources admitted" value={projection.sources_included.length} />
          <Metric label="Last refreshed" value={new Date(projection.as_of).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })} />
        </section>

        {actionError && <div role="alert" className="mb-4 rounded-xl border border-red-900/60 bg-red-950/30 px-4 py-3 text-sm text-red-200">{actionError}</div>}

        {items.length === 0 ? (
          <section className="rounded-2xl border border-white/10 bg-[#111720] px-6 py-14 text-center">
            <CheckCircle2 className="mx-auto text-emerald-300" size={32} />
            <h2 className="mt-4 text-lg font-medium">
              {projection.sources_included.length === 0
                ? 'No work source was included in this session'
                : 'You’re clear'}
            </h2>
            <p className="mt-2 text-sm text-slate-400">
              {projection.sources_included.length === 0
                ? 'EOS returned no source projection. This is not evidence that every business queue is empty.'
                : 'There is no active work in the sources currently authorized for this session.'}
            </p>
          </section>
        ) : (
          <section aria-label="Authorized work queue" className="space-y-3">
            {items.map((item) => {
              const path = completionPath(item);
              return (
                <article key={item.source_key}
                  ref={item.source_key === focusKey ? focusRef : undefined}
                  tabIndex={-1}
                  className={'rounded-2xl border bg-[#111720] p-4 sm:p-5 outline-none ' +
                    (item.source_key === focusKey
                      ? 'border-amber-300/70 ring-2 ring-amber-300/40'
                      : 'border-white/10')}>
                  <div className="flex flex-wrap items-start justify-between gap-3">
                    <div className="min-w-0 flex-1">
                      <div className="flex flex-wrap items-center gap-2">
                        <span className="rounded-md border border-amber-400/25 bg-amber-400/10 px-2 py-1 text-[10px] font-semibold uppercase tracking-wider text-amber-200">{SOURCE_LABELS[item.source] || item.source}</span>
                        <span className="text-[11px] uppercase tracking-wider text-slate-500">{item.kind || 'TASK'}</span>
                        {item.is_overdue && <span className="rounded-md bg-red-500/15 px-2 py-1 text-[10px] font-semibold uppercase text-red-200">Overdue</span>}
                      </div>
                      <h2 className="mt-3 break-words text-base font-semibold text-white sm:text-lg">{item.title}</h2>
                      {item.description && <p className="mt-1 break-words whitespace-pre-wrap text-sm text-slate-400">{item.description}</p>}
                    </div>
                    <div className="text-right">
                      <div className="text-xs uppercase tracking-wider text-slate-500">Priority</div>
                      <div className="mt-1 text-sm font-semibold text-slate-200">{item.priority}</div>
                    </div>
                  </div>
                  <div className="mt-4 flex flex-wrap items-center gap-x-5 gap-y-2 border-t border-white/10 pt-3 text-xs text-slate-400">
                    <span className="inline-flex items-center gap-1.5"><Clock3 size={13} /> {formatDue(item.due_at)}</span>
                    <span className="inline-flex items-center gap-1.5"><Circle size={10} /> {item.status}</span>
                    {item.visibility_provenance?.length > 0 && <span>Visibility: {item.visibility_provenance.join(' / ')}</span>}
                  </div>
                  {item.source === 'LEGAL' ? (
                    <div className="mt-4 grid gap-2 sm:grid-cols-2" data-legal-completion-evidence="required">
                      <label className="grid gap-1 text-xs text-slate-400">
                        Completion evidence reference
                        <input
                          aria-label={'Legal completion evidence reference for ' + item.title}
                          value={legalEvidence[item.source_key]?.reference || ''}
                          onChange={(event) => setLegalEvidence((current) => ({
                            ...current,
                            [item.source_key]: { ...current[item.source_key], reference: event.target.value },
                          }))}
                          placeholder="Exact source evidence reference"
                          maxLength={500}
                          className="min-w-0 rounded-lg border border-white/10 bg-black/25 px-3 py-2 text-sm text-white outline-none focus:border-amber-400/60"
                        />
                      </label>
                      <label className="grid gap-1 text-xs text-slate-400">
                        SHA3-512 evidence fingerprint (128 lowercase hex)
                        <input
                          aria-label={'Legal completion evidence fingerprint for ' + item.title}
                          value={legalEvidence[item.source_key]?.fingerprint || ''}
                          onChange={(event) => setLegalEvidence((current) => ({
                            ...current,
                            [item.source_key]: { ...current[item.source_key], fingerprint: event.target.value },
                          }))}
                          placeholder="Fingerprint from the evidence source"
                          maxLength={128}
                          pattern="[a-f0-9]{128}"
                          className="min-w-0 rounded-lg border border-white/10 bg-black/25 px-3 py-2 font-mono text-xs text-white outline-none focus:border-amber-400/60"
                        />
                      </label>
                      <p className="sm:col-span-2 text-xs text-slate-500">
                        The canonical Legal command verifies and records this evidence. My Work does not generate, infer or substitute it.
                      </p>
                      <button
                        onClick={() => complete(item)}
                        disabled={
                          !String(legalEvidence[item.source_key]?.reference || '').trim()
                          || !/^[a-f0-9]{128}$/.test(String(legalEvidence[item.source_key]?.fingerprint || ''))
                          || completing === item.source_key
                        }
                        className="sm:col-span-2 inline-flex items-center justify-center gap-2 rounded-lg bg-amber-400 px-4 py-2 text-sm font-semibold text-slate-950 hover:bg-amber-300 disabled:cursor-not-allowed disabled:opacity-40"
                      >
                        {completing === item.source_key ? <Loader2 size={15} className="animate-spin" /> : <CheckCircle2 size={15} />}
                        Submit evidenced Legal completion
                      </button>
                    </div>
                  ) : path ? (
                    <div className="mt-4 flex flex-col gap-2 sm:flex-row">
                      <input
                        aria-label={'Completion note for ' + item.title}
                        value={notes[item.source_key] || ''}
                        onChange={(event) => setNotes((current) => ({ ...current, [item.source_key]: event.target.value }))}
                        placeholder="Record what was completed…"
                        maxLength={1000}
                        className="min-w-0 flex-1 rounded-lg border border-white/10 bg-black/25 px-3 py-2 text-sm text-white outline-none focus:border-amber-400/60"
                      />
                      <button
                        onClick={() => complete(item)}
                        disabled={!String(notes[item.source_key] || '').trim() || completing === item.source_key}
                        className="inline-flex items-center justify-center gap-2 rounded-lg bg-amber-400 px-4 py-2 text-sm font-semibold text-slate-950 hover:bg-amber-300 disabled:cursor-not-allowed disabled:opacity-40"
                      >
                        {completing === item.source_key ? <Loader2 size={15} className="animate-spin" /> : <CheckCircle2 size={15} />}
                        Complete
                      </button>
                    </div>
                  ) : (
                    <div className="mt-4 rounded-lg border border-white/10 bg-black/20 px-3 py-2 text-xs text-slate-400">
                      No generic completion command is available for this source.
                    </div>
                  )}
                </article>
              );
            })}
          </section>
        )}

        <footer className="mt-8 flex flex-wrap items-center justify-between gap-3 border-t border-white/10 pt-4 text-[11px] text-slate-500">
          <span>
            Included: {projection.sources_included.length
              ? projection.sources_included.map((source) => SOURCE_LABELS[source]).join(', ')
              : 'no source projection'}
          </span>
          <span>Commands remain owned by each source service.</span>
        </footer>
      </div>
    </main>
  );
}

function Metric({ label, value }) {
  return (
    <div className="rounded-xl border border-white/10 bg-[#111720] p-4">
      <div className="text-[10px] uppercase tracking-[0.18em] text-slate-500">{label}</div>
      <div className="mt-2 text-2xl font-semibold tabular-nums text-white">{value}</div>
    </div>
  );
}

/*
 * ARTIFACT: MyWorkWorkspace.jsx
 * VERSION: v1.4.0-VERIFIED-PROJECTION-FOCUS-HANDOFF
 * AUTHORITY BOUNDARY: EOS source-owned work completion only.
 * TENANT POSTURE: Current principal, membership and business-role scope only.
 * FAIL-CLOSED POSTURE: Shared contract rejects invalid work and coverage.
 * FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
