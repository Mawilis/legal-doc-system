/**
 * WILSY OS — ROLE-SCOPED LEGAL OPERATIONS COCKPIT
 * VERSION: v6.0.1-L8-6C-ROLE-SCOPED-LEGAL-COCKPIT
 * AUTHORITY: Presentation of authenticated Python-EOS Legal Operations truth.
 * EPITOME: Enhances the certified sheriff cockpit with the L8-6C bound-deputy
 *          personal active-work surface. SHERIFF sees only tenant-wide certified
 *          queues; DEPUTY sees only personal ALLOCATED/ATTEMPTED work derived
 *          from the immutable principal-to-Deputy binding. Browser role labels
 *          choose presentation only and never create authority.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/components/industry/LegalDashboard.jsx
 * COLLABORATION / OWNERSHIP: Python EOS IAM owns access authority; P1/P2/L8-0/
 *                            L8-5 own lifecycle/read truth; L8-5C owns sheriff
 *                            queues; L8-6B owns principal-to-Deputy binding;
 *                            L8-6C owns deputy personal work; the client adapter
 *                            owns bounded validation; this component owns
 *                            presentation only.
 * CERTIFICATION / UPDATE DATE: 2026-09-23
 * CHANGELOG: 2026-09-23 v6.0.1-L8-6C-ROLE-SCOPED-LEGAL-COCKPIT clarifies empty-state copy as explicit
 *            non-synthetic-work language; runtime role-scoped queue behavior
 *            is unchanged.
 *            2026-09-23 v6.0.0-L8-6C-ROLE-SCOPED-LEGAL-COCKPIT adds an exact DEPUTY personal-work mode,
 *            preserves the SHERIFF tenant-wide mode, removes the obsolete
 *            "deputy personal queue blocked" roadmap card, prevents unresolved
 *            legal roles from probing either privileged endpoint, and keeps
 *            responsive small-screen stacking without inventing mobile truth.
 *            2026-09-23 v5.0.0-L8-6A-CERTIFIED-SHERIFF-COCKPIT removes all
 *            hard-coded documents, clients, deputies, service attempts,
 *            invoices, revenue, GPS, urgency, addresses, district metrics and
 *            payment states. It renders only office receipt, deputy assignment
 *            and active attempt queues returned by the certified backend.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
 * SECURITY / PRIVACY POSTURE: Authenticated transport only; no secrets are
 *                             rendered or persisted by this component.
 * TENANT BOUNDARY: Canonical tenant scope comes from the server response after
 *                  durable authorization; deputy identity additionally comes
 *                  only from the server-bound L8-6B/L8-6C projection.
 * AUTHORITY BOUNDARY: Read-only presentation. roleView selects presentation
 *                     mode only; Python EOS independently authorizes each read.
 * FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
 * FAIL-CLOSED DECLARATION: Unknown role scope, 401/403/503, malformed payloads,
 *                          tenant drift or deputy drift render bounded states
 *                          with no mock or cross-role fallback.
 */

import React, { useCallback, useEffect, useMemo, useState } from 'react';
import {
  AlertTriangle,
  Bot,
  CheckCircle2,
  ClipboardList,
  Clock3,
  FileCheck2,
  FileText,
  Inbox,
  Loader2,
  LockKeyhole,
  LogOut,
  RefreshCw,
  Scale,
  ShieldCheck,
  Sparkles,
  UserCheck,
} from 'lucide-react';

import {
  LEGAL_OPERATIONS_CLIENT_VERSION,
  getDeputyPersonalActiveWork,
  getSheriffOperationalQueues,
} from '../../services/legalOperationsService.js';

const DASHBOARD_VERSION = 'v6.0.1-L8-6C-ROLE-SCOPED-LEGAL-COCKPIT';

const EMPTY_QUEUES = Object.freeze({
  tenantId: '',
  visibility: '',
  officeReceipt: Object.freeze([]),
  deputyAssignment: Object.freeze([]),
  activeAttempts: Object.freeze([]),
});

const EMPTY_DEPUTY_WORK = Object.freeze({
  tenantId: '',
  visibility: '',
  deputyId: '',
  activeAttempts: Object.freeze([]),
});

const ROLE_MODES = Object.freeze({
  SHERIFF: 'SHERIFF',
  DEPUTY: 'DEPUTY',
  UNRESOLVED: 'UNRESOLVED',
});

function resolveRoleMode(value) {
  const token = String(value || '')
    .trim()
    .replace(/[^A-Za-z0-9]+/g, '_')
    .toUpperCase();
  if (token.includes('SHERIFF')) return ROLE_MODES.SHERIFF;
  if (token.includes('DEPUTY')) return ROLE_MODES.DEPUTY;
  return ROLE_MODES.UNRESOLVED;
}

const BLOCKED_CAPABILITIES = Object.freeze([
  {
    title: 'Same-day / urgent prioritisation',
    reason: 'No canonical urgency field exists in the certified queue model.',
  },
  {
    title: 'Distance / GPS routing',
    reason: 'No certified geospatial source is connected to this cockpit.',
  },
  {
    title: 'Billing readiness',
    reason: 'Legal operational state is not invoice, payment or settlement truth.',
  },
  {
    title: 'Return-generation queue',
    reason: 'Requires snapshot-consistent cross-entity absence proof before exposure.',
  },
]);

function formatTimestamp(value) {
  if (!value) return '—';
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) return String(value);
  return parsed.toLocaleString();
}

function QueueMetric({ icon: Icon, label, value, description }) {
  return (
    <div className="rounded-2xl border border-amber-900/30 bg-stone-950/70 p-5 shadow-xl shadow-black/20">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-[10px] font-black uppercase tracking-[0.22em] text-stone-500">
            {label}
          </p>
          <p className="mt-2 text-3xl font-black text-white">{value}</p>
        </div>
        <div className="rounded-xl border border-amber-700/30 bg-amber-500/10 p-3 text-amber-400">
          <Icon size={20} />
        </div>
      </div>
      <p className="mt-3 text-xs leading-5 text-stone-500">{description}</p>
    </div>
  );
}

function QueuePanel({ title, subtitle, icon: Icon, rows, renderRow, emptyMessage }) {
  return (
    <section className="overflow-hidden rounded-2xl border border-stone-800 bg-stone-950/75">
      <header className="flex items-center justify-between gap-4 border-b border-stone-800 px-5 py-4">
        <div className="flex items-center gap-3">
          <div className="rounded-xl border border-amber-800/30 bg-amber-500/10 p-2.5 text-amber-400">
            <Icon size={18} />
          </div>
          <div>
            <h2 className="text-sm font-black uppercase tracking-[0.12em] text-white">
              {title}
            </h2>
            <p className="mt-1 text-[11px] text-stone-500">{subtitle}</p>
          </div>
        </div>
        <span className="rounded-full border border-stone-700 bg-black/40 px-3 py-1 text-xs font-black text-stone-300">
          {rows.length}
        </span>
      </header>

      <div className="divide-y divide-stone-900">
        {rows.length === 0 ? (
          <div className="px-5 py-8 text-center">
            <CheckCircle2 className="mx-auto text-emerald-500/70" size={24} />
            <p className="mt-3 text-sm font-bold text-stone-300">{emptyMessage}</p>
            <p className="mt-1 text-xs text-stone-600">
              Empty is a valid certified result. No synthetic work is generated.
            </p>
          </div>
        ) : (
          rows.map((row, index) => renderRow(row, index))
        )}
      </div>
    </section>
  );
}

function StatePill({ state }) {
  return (
    <span className="rounded-full border border-amber-700/30 bg-amber-500/10 px-2.5 py-1 text-[10px] font-black uppercase tracking-wider text-amber-300">
      {state || 'UNKNOWN'}
    </span>
  );
}

function DocumentQueueRow({ item, mode }) {
  const eventTime =
    mode === 'receipt'
      ? item.registered_at
      : item.received_at || item.registered_at;

  return (
    <div className="grid gap-4 px-5 py-4 md:grid-cols-[1.1fr_1fr_0.8fr_auto] md:items-center">
      <div>
        <p className="text-sm font-black text-white">{item.document_id || '—'}</p>
        <p className="mt-1 text-[11px] text-stone-500">
          Matter {item.case_matter_id || '—'}
        </p>
      </div>
      <div>
        <p className="text-xs font-semibold text-stone-300">
          {item.document_type || 'Unspecified canonical document type'}
        </p>
        <p className="mt-1 text-[10px] text-stone-600">{formatTimestamp(eventTime)}</p>
      </div>
      <div className="text-xs text-stone-400">
        {mode === 'receipt' ? 'Awaiting office receipt' : 'Awaiting deputy allocation'}
      </div>
      <StatePill state={item.state} />
    </div>
  );
}

function AttemptQueueRow({ item }) {
  return (
    <div className="grid gap-4 px-5 py-4 md:grid-cols-[1.1fr_1fr_1fr_auto] md:items-center">
      <div>
        <p className="text-sm font-black text-white">{item.attempt_id || '—'}</p>
        <p className="mt-1 text-[11px] text-stone-500">
          Instruction {item.instruction_id || '—'}
        </p>
      </div>
      <div>
        <p className="text-xs font-semibold text-stone-300">
          Document {item.document_id || '—'}
        </p>
        <p className="mt-1 text-[10px] text-stone-600">
          {formatTimestamp(item.attempted_at || item.allocated_at)}
        </p>
      </div>
      <div>
        <p className="text-[10px] font-black uppercase tracking-wider text-stone-600">
          Canonical deputy id
        </p>
        <p className="mt-1 text-xs font-semibold text-stone-300">
          {item.deputy_id || '—'}
        </p>
      </div>
      <StatePill state={item.state} />
    </div>
  );
}

function CapabilityBoundary() {
  return (
    <section className="rounded-2xl border border-stone-800 bg-stone-950/75 p-5">
      <div className="flex items-start gap-3">
        <LockKeyhole className="mt-0.5 text-stone-500" size={19} />
        <div>
          <h2 className="text-sm font-black uppercase tracking-[0.12em] text-white">
            Deliberate authority boundaries
          </h2>
          <p className="mt-1 max-w-3xl text-xs leading-5 text-stone-500">
            These capabilities remain visible on the roadmap but cannot display
            synthetic data. Each requires its own canonical authority and certificate.
          </p>
        </div>
      </div>
      <div className="mt-5 grid gap-3 lg:grid-cols-2">
        {BLOCKED_CAPABILITIES.map((capability) => (
          <div
            key={capability.title}
            className="rounded-xl border border-stone-800 bg-black/30 p-4"
          >
            <div className="flex items-center gap-2">
              <AlertTriangle size={14} className="text-amber-500" />
              <p className="text-xs font-black text-stone-300">{capability.title}</p>
            </div>
            <p className="mt-2 text-[11px] leading-5 text-stone-600">
              {capability.reason}
            </p>
          </div>
        ))}
      </div>
    </section>
  );
}

export default function LegalDashboard({
  onLogout,
  tenantConfig,
  roleView = 'LEGAL_VIEW',
}) {
  const roleMode = useMemo(() => resolveRoleMode(roleView), [roleView]);
  const [queues, setQueues] = useState(EMPTY_QUEUES);
  const [deputyWork, setDeputyWork] = useState(EMPTY_DEPUTY_WORK);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);

  const loadOperationalTruth = useCallback(async ({ refresh = false } = {}) => {
    if (refresh) setRefreshing(true);
    else setLoading(true);
    setError(null);

    if (roleMode === ROLE_MODES.UNRESOLVED) {
      setQueues(EMPTY_QUEUES);
      setDeputyWork(EMPTY_DEPUTY_WORK);
      setError({
        kind: 'LEGAL_ROLE_SCOPE_REQUIRED',
        message:
          'This Legal OS surface requires an explicit SHERIFF or DEPUTY presentation scope. No privileged queue endpoint was queried.',
      });
      setLoading(false);
      setRefreshing(false);
      return;
    }

    try {
      if (roleMode === ROLE_MODES.DEPUTY) {
        const result = await getDeputyPersonalActiveWork();
        setDeputyWork(result);
        setQueues(EMPTY_QUEUES);
      } else {
        const result = await getSheriffOperationalQueues();
        setQueues(result);
        setDeputyWork(EMPTY_DEPUTY_WORK);
      }
      setLastUpdated(new Date());
    } catch (caught) {
      const status = caught?.response?.status;
      const detail = caught?.response?.data?.detail;

      if (status === 401) {
        setError({
          kind: 'AUTHENTICATION_REQUIRED',
          message: 'Authentication is required to open the Legal Operations cockpit.',
        });
      } else if (status === 403 && roleMode === ROLE_MODES.DEPUTY) {
        setError({
          kind:
            detail === 'DEPUTY_IDENTITY_BINDING_REQUIRED'
              ? 'DEPUTY_IDENTITY_BINDING_REQUIRED'
              : 'DEPUTY_AUTHORITY_REQUIRED',
          message:
            detail === 'DEPUTY_IDENTITY_BINDING_REQUIRED'
              ? 'No immutable principal-to-Deputy identity binding is available for this authenticated deputy.'
              : 'Personal active work is restricted to the canonical DEPUTY authority.',
        });
      } else if (status === 403) {
        setError({
          kind: 'SHERIFF_AUTHORITY_REQUIRED',
          message:
            'The tenant-wide operational queue is restricted to the canonical SHERIFF authority.',
        });
      } else if (status === 503) {
        setError({
          kind: 'EVIDENCE_UNAVAILABLE',
          message:
            detail || 'Certified Legal Operations evidence is temporarily unavailable.',
        });
      } else {
        setError({
          kind: 'QUEUE_READ_FAILED',
          message:
            caught?.message || 'Certified Legal Operations truth could not be loaded.',
        });
      }

      setQueues(EMPTY_QUEUES);
      setDeputyWork(EMPTY_DEPUTY_WORK);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [roleMode]);

  useEffect(() => {
    let active = true;

    const hydrate = async () => {
      if (!active) return;
      await loadOperationalTruth();
    };

    hydrate();
    return () => {
      active = false;
    };
  }, [loadOperationalTruth]);

  const metrics = useMemo(() => {
    if (roleMode === ROLE_MODES.DEPUTY) {
      return {
        officeReceipt: 0,
        deputyAssignment: 0,
        activeAttempts: deputyWork.activeAttempts.length,
        totalCurrentWork: deputyWork.activeAttempts.length,
      };
    }
    const officeReceipt = queues.officeReceipt.length;
    const deputyAssignment = queues.deputyAssignment.length;
    const activeAttempts = queues.activeAttempts.length;
    return {
      officeReceipt,
      deputyAssignment,
      activeAttempts,
      totalCurrentWork: officeReceipt + deputyAssignment + activeAttempts,
    };
  }, [deputyWork, queues, roleMode]);

  const tenantLabel =
    (roleMode === ROLE_MODES.DEPUTY ? deputyWork.tenantId : queues.tenantId)
    || tenantConfig?.tenantId
    || tenantConfig?.id
    || 'Awaiting authorized tenant';

  const isDeputyMode = roleMode === ROLE_MODES.DEPUTY;
  const isSheriffMode = roleMode === ROLE_MODES.SHERIFF;

  if (loading) {
    return (
      <div className="flex min-h-[70vh] items-center justify-center bg-[#080706] text-white">
        <div className="text-center">
          <Loader2 className="mx-auto animate-spin text-amber-400" size={30} />
          <p className="mt-4 text-xs font-black uppercase tracking-[0.22em] text-stone-400">
            Resolving certified Legal Operations truth
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#080706] text-white">
      <div className="border-b border-amber-900/25 bg-gradient-to-r from-black via-stone-950 to-black">
        <div className="mx-auto max-w-[1600px] px-5 py-5 lg:px-8">
          <div className="flex flex-col justify-between gap-5 xl:flex-row xl:items-center">
            <div className="flex items-start gap-4">
              <div className="rounded-2xl border border-amber-700/30 bg-amber-500/10 p-3 text-amber-400">
                <Scale size={27} />
              </div>
              <div>
                <div className="flex flex-wrap items-center gap-2">
                  <h1 className="text-xl font-black tracking-tight text-white lg:text-2xl">
                    WILSY Legal OS
                  </h1>
                  <span className="rounded-full border border-emerald-800/40 bg-emerald-500/10 px-2.5 py-1 text-[9px] font-black uppercase tracking-[0.18em] text-emerald-400">
                    {isDeputyMode ? 'Bound deputy cockpit' : isSheriffMode ? 'Certified sheriff cockpit' : 'Role scope unresolved'}
                  </span>
                </div>
                <p className="mt-1 text-sm text-stone-400">
                  {isDeputyMode
                    ? 'Binding-scoped personal active work. No tenant-wide queue leakage.'
                    : isSheriffMode
                      ? 'Evidence-backed operational queues. No mock legal truth.'
                      : 'Privileged Legal Operations queues remain closed until role scope resolves.'}
                </p>
                <div className="mt-2 flex flex-wrap gap-x-4 gap-y-1 text-[10px] uppercase tracking-wider text-stone-600">
                  <span>Tenant: {tenantLabel}</span>
                  <span>Role view: {roleMode}</span>
                  <span>API: {LEGAL_OPERATIONS_CLIENT_VERSION}</span>
                </div>
              </div>
            </div>

            <div className="flex flex-wrap items-center gap-3">
              <div className="rounded-xl border border-stone-800 bg-black/40 px-3 py-2">
                <p className="text-[9px] font-black uppercase tracking-wider text-stone-600">
                  Evidence refresh
                </p>
                <p className="mt-0.5 text-xs font-semibold text-stone-300">
                  {lastUpdated ? lastUpdated.toLocaleTimeString() : 'Not available'}
                </p>
              </div>
              <button
                type="button"
                onClick={() => loadOperationalTruth({ refresh: true })}
                disabled={refreshing}
                className="inline-flex items-center gap-2 rounded-xl border border-amber-700/35 bg-amber-500/10 px-4 py-3 text-xs font-black text-amber-300 transition hover:bg-amber-500/15 disabled:cursor-not-allowed disabled:opacity-50"
              >
                <RefreshCw size={15} className={refreshing ? 'animate-spin' : ''} />
                Refresh truth
              </button>
              {typeof onLogout === 'function' && (
                <button
                  type="button"
                  onClick={onLogout}
                  className="inline-flex items-center gap-2 rounded-xl border border-stone-800 bg-black/40 px-4 py-3 text-xs font-bold text-stone-400 hover:text-white"
                >
                  <LogOut size={15} />
                  Sign out
                </button>
              )}
            </div>
          </div>
        </div>
      </div>

      <main className="mx-auto max-w-[1600px] space-y-6 px-5 py-6 lg:px-8">
        {error && (
          <section className="rounded-2xl border border-red-900/40 bg-red-950/15 p-5">
            <div className="flex items-start gap-3">
              <ShieldCheck className="mt-0.5 text-red-400" size={20} />
              <div>
                <p className="text-xs font-black uppercase tracking-[0.16em] text-red-300">
                  {error.kind}
                </p>
                <p className="mt-2 max-w-4xl text-sm leading-6 text-stone-300">
                  {error.message}
                </p>
                <p className="mt-2 text-[11px] text-stone-600">
                  WILSY Legal OS does not substitute browser fixtures when canonical evidence is unavailable.
                </p>
              </div>
            </div>
          </section>
        )}

        {isSheriffMode && (
          <>
            <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
              <QueueMetric
                icon={Inbox}
                label="Office receipt"
                value={metrics.officeReceipt}
                description="REGISTERED process documents awaiting certified office receipt."
              />
              <QueueMetric
                icon={UserCheck}
                label="Deputy assignment"
                value={metrics.deputyAssignment}
                description="RECEIVED process documents awaiting canonical deputy allocation."
              />
              <QueueMetric
                icon={Clock3}
                label="Active attempts"
                value={metrics.activeAttempts}
                description="ALLOCATED or ATTEMPTED service attempts requiring operational attention."
              />
              <QueueMetric
                icon={ClipboardList}
                label="Current queue work"
                value={metrics.totalCurrentWork}
                description="Derived presentation count: the sum of the three certified queue families above."
              />
            </section>

            <div className="grid gap-6 2xl:grid-cols-2">
              <QueuePanel
                title="Office receipt"
                subtitle="Canonical REGISTERED ProcessDocument current states"
                icon={FileText}
                rows={queues.officeReceipt}
                emptyMessage="No documents are awaiting office receipt."
                renderRow={(item) => (
                  <DocumentQueueRow
                    key={item.document_id}
                    item={item}
                    mode="receipt"
                  />
                )}
              />
              <QueuePanel
                title="Deputy assignment"
                subtitle="Canonical RECEIVED ProcessDocument current states"
                icon={FileCheck2}
                rows={queues.deputyAssignment}
                emptyMessage="No received documents are awaiting deputy allocation."
                renderRow={(item) => (
                  <DocumentQueueRow
                    key={item.document_id}
                    item={item}
                    mode="assignment"
                  />
                )}
              />
            </div>

            <QueuePanel
              title="Active service attempts"
              subtitle="Canonical ALLOCATED / ATTEMPTED ServiceAttempt current states"
              icon={Clock3}
              rows={queues.activeAttempts}
              emptyMessage="No active service attempts are currently certified."
              renderRow={(item) => (
                <AttemptQueueRow key={item.attempt_id} item={item} />
              )}
            />
          </>
        )}

        {isDeputyMode && (
          <>
            <section className="grid gap-4 md:grid-cols-2">
              <QueueMetric
                icon={UserCheck}
                label="Bound deputy"
                value={deputyWork.deputyId || '—'}
                description="Canonical Deputy identity derived server-side from the immutable principal binding."
              />
              <QueueMetric
                icon={Clock3}
                label="My active attempts"
                value={metrics.activeAttempts}
                description="Only this bound deputy's current ALLOCATED or ATTEMPTED service attempts."
              />
            </section>

            <QueuePanel
              title="My active service work"
              subtitle="Binding-scoped ALLOCATED / ATTEMPTED ServiceAttempt current states"
              icon={Clock3}
              rows={deputyWork.activeAttempts}
              emptyMessage="No active service attempts are assigned to this bound deputy."
              renderRow={(item) => (
                <AttemptQueueRow key={item.attempt_id} item={item} />
              )}
            />
          </>
        )}

        <section className="grid gap-4 xl:grid-cols-[1.2fr_0.8fr]">
          <CapabilityBoundary />

          <div className="rounded-2xl border border-violet-900/30 bg-gradient-to-br from-violet-950/20 via-stone-950 to-stone-950 p-5">
            <div className="flex items-start gap-3">
              <div className="rounded-xl border border-violet-800/30 bg-violet-500/10 p-2.5 text-violet-300">
                <Bot size={19} />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h2 className="text-sm font-black uppercase tracking-[0.12em] text-white">
                    WILSY AI readiness
                  </h2>
                  <Sparkles size={14} className="text-violet-400" />
                </div>
                <p className="mt-2 text-xs leading-6 text-stone-400">
                  WILSY AI will consume certified Legal OS evidence through its own
                  governed tool and reasoning contracts. This cockpit does not let AI
                  create legal facts, queue membership, deputy identity or financial truth.
                </p>
                <div className="mt-4 rounded-xl border border-violet-900/30 bg-black/30 p-4">
                  <p className="text-[10px] font-black uppercase tracking-[0.18em] text-violet-400">
                    Authority equation
                  </p>
                  <p className="mt-2 text-xs leading-6 text-stone-300">
                    Observed fact ≠ derived signal ≠ AI inference ≠ recommendation ≠ authorization ≠ execution.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </section>

        <footer className="flex flex-col justify-between gap-3 border-t border-stone-900 py-5 text-[10px] uppercase tracking-[0.15em] text-stone-700 md:flex-row">
          <span>{DASHBOARD_VERSION}</span>
          <span>Presentation only · Python EOS remains sovereign legal truth</span>
        </footer>
      </main>
    </div>
  );
}

/**
 * ARTIFACT: LegalDashboard.jsx
 * VERSION: v6.0.1-L8-6C-ROLE-SCOPED-LEGAL-COCKPIT
 * AUTHORITY BOUNDARY: role-scoped sheriff/deputy read presentation only; browser role labels never authorize
 * TENANT POSTURE: server-authorized tenant response only; deputy rows additionally match bound deputy_id
 * FAIL-CLOSED POSTURE: unresolved role, denied/unavailable evidence, tenant/deputy drift never falls back or crosses roles
 * FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
