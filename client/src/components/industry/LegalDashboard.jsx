/**
 * WILSY OS — ROLE-SCOPED LEGAL OPERATIONS COCKPIT
 * VERSION: v8.0.1-L8-7D8-CLIENT-MATTER-COCKPIT-DENIAL-COPY-REPAIR
 * AUTHORITY: Presentation of authenticated Python-EOS Legal Operations truth.
 * EPITOME: Preserves certified SHERIFF and governed DEPUTY modes while adding
 *          an exact LEGAL_CLIENT cockpit backed only by the D7 sanitized matter
 *          adapter. Client mode presents explicitly-visible current matters and
 *          derived OPEN/CLOSED counts only; it never probes internal queues,
 *          deputy work, service evidence, billing, AI or financial truth.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/components/industry/LegalDashboard.jsx
 * COLLABORATION / OWNERSHIP: Python EOS IAM owns authority; P1/P2 own lifecycle/
 *                            snapshot truth; L8-5C owns sheriff queues; L8-6B owns
 *                            immutable principal-to-Deputy binding; L8-6C owns
 *                            deputy work; L8-6D owns state-valid capabilities;
 *                            L8-6G owns field-command composition/P5M lineage;
 *                            D5/D6 own sanitized LEGAL_CLIENT projection and
 *                            authenticated snapshot transport; D7 owns browser
 *                            validation. This component owns responsive
 *                            presentation and deputy observation capture only.
 * CERTIFICATION / UPDATE DATE: 2026-09-23
 * CHANGELOG: 2026-09-23 v8.0.1-L8-7D8-CLIENT-MATTER-COCKPIT-DENIAL-COPY-REPAIR keeps the exact D8 client-denial machine
 *            code as the error heading while replacing duplicate opaque body
 *            copy with bounded human-readable guidance. Authorization, endpoint
 *            selection, matter visibility and all SHERIFF/DEPUTY behavior remain unchanged.
 *            2026-09-23 v8.0.0-L8-7D8-CLIENT-MATTER-COCKPIT adds an exact LEGAL_CLIENT role mode that calls
 *            only getLegalClientMatters(), renders visible/open/closed counts and
 *            safe matter cards, handles client-specific denial/unavailability
 *            without cross-role fallback, preserves SHERIFF/DEPUTY behavior, and
 *            keeps responsive one-column mobile stacking. No internal legal,
 *            service, billing, AI or financial truth is inferred or displayed.
 *            2026-09-23 v7.0.0-L8-6I-DEPUTY-FIELD-COMMAND-COCKPIT adds exact deputy capability/work parity checks,
 *            touch-friendly begin/completed/not-completed field controls, explicit
 *            observation reference/time capture, pseudonymous browser field-device
 *            provenance, per-command pending/error/success states, and mandatory
 *            canonical refresh before success. No P5M sequence/fingerprint,
 *            tenant/deputy authority, GPS, AI, billing or financial truth is
 *            created by the component.
 *            2026-09-23 v6.0.1-L8-6C-ROLE-SCOPED-LEGAL-COCKPIT clarifies empty-state copy as explicit
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
 * SECURITY / PRIVACY POSTURE: Authenticated transport only. A pseudonymous
 *                             browser field-device reference may be stored locally
 *                             solely for P5M ordering provenance; it is not IAM,
 *                             deputy identity, GPS, biometric or legal truth.
 * TENANT BOUNDARY: Canonical tenant scope comes only from certified server
 *                  projections; deputy identity remains server-bound and client
 *                  matter membership comes only from explicit D5/D7 visibility.
 * AUTHORITY BOUNDARY: Presentation and deputy observation-command initiation
 *                     only. roleView/display state never grants SHERIFF, DEPUTY
 *                     or LEGAL_CLIENT authority; Python EOS independently
 *                     authorizes and owns all legal truth.
 * FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
 * FAIL-CLOSED DECLARATION: Unknown role, denied/unavailable client/internal
 *                          reads, work/capability drift, malformed observation,
 *                          command failure, or failed canonical refresh never
 *                          falls back, crosses roles, invents matters, or displays
 *                          command success.
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
  Play,
  RefreshCw,
  Scale,
  ShieldCheck,
  Sparkles,
  UserCheck,
} from 'lucide-react';

import {
  LEGAL_OPERATIONS_CLIENT_VERSION,
  getDeputyFieldCapabilities,
  getDeputyPersonalActiveWork,
  getLegalClientMatters,
  getSheriffOperationalQueues,
  recordDeputyFieldOutcome,
  transitionDeputyFieldAttempt,
} from '../../services/legalOperationsService.js';

const DASHBOARD_VERSION = 'v8.0.1-L8-7D8-CLIENT-MATTER-COCKPIT-DENIAL-COPY-REPAIR';

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

const EMPTY_CLIENT_MATTERS = Object.freeze({
  schema: '',
  version: '',
  tenantId: '',
  visibility: '',
  matters: Object.freeze([]),
});


const EMPTY_DEPUTY_CAPABILITIES = Object.freeze({
  tenantId: '',
  visibility: '',
  deputyId: '',
  capabilities: Object.freeze([]),
});

const FIELD_DEVICE_STORAGE_KEY =
  'wilsy.legal-operations.field-device.v1';

const FIELD_COMMAND_KIND = Object.freeze({
  BEGIN: 'TRANSITION_TO_ATTEMPTED',
  COMPLETED: 'RECORD_COMPLETED_OUTCOME',
  NOT_COMPLETED: 'RECORD_NOT_COMPLETED_OUTCOME',
});

const ROLE_MODES = Object.freeze({
  SHERIFF: 'SHERIFF',
  DEPUTY: 'DEPUTY',
  LEGAL_CLIENT: 'LEGAL_CLIENT',
  UNRESOLVED: 'UNRESOLVED',
});

function resolveRoleMode(value) {
  const token = String(value || '')
    .trim()
    .replace(/[^A-Za-z0-9]+/g, '_')
    .toUpperCase();
  if (token.includes('SHERIFF')) return ROLE_MODES.SHERIFF;
  if (token.includes('DEPUTY')) return ROLE_MODES.DEPUTY;
  if (
    token === 'LEGAL_CLIENT'
    || token === 'TENANT_LEGAL_CLIENT'
  ) {
    return ROLE_MODES.LEGAL_CLIENT;
  }
  return ROLE_MODES.UNRESOLVED;
}

function createOpaqueBrowserToken() {
  if (typeof globalThis.crypto?.randomUUID === 'function') {
    return globalThis.crypto.randomUUID();
  }
  if (typeof globalThis.crypto?.getRandomValues === 'function') {
    const bytes = new Uint8Array(16);
    globalThis.crypto.getRandomValues(bytes);
    return Array.from(bytes, (value) => value.toString(16).padStart(2, '0')).join('');
  }
  return `${Date.now().toString(36)}-${Math.random().toString(36).slice(2)}`;
}

function resolveBrowserFieldDeviceId() {
  const create = () => `browser-device:${createOpaqueBrowserToken()}`;
  try {
    const existing = globalThis.localStorage?.getItem(FIELD_DEVICE_STORAGE_KEY);
    if (
      typeof existing === 'string'
      && /^browser-device:[A-Za-z0-9-]+$/.test(existing)
    ) {
      return existing;
    }
    const value = create();
    globalThis.localStorage?.setItem(FIELD_DEVICE_STORAGE_KEY, value);
    return value;
  } catch {
    return create();
  }
}

function createFieldEventId() {
  return `browser-event:${createOpaqueBrowserToken()}`;
}

function localDateTimeValue(date = new Date()) {
  const local = new Date(
    date.getTime() - date.getTimezoneOffset() * 60_000,
  );
  return local.toISOString().slice(0, 16);
}

function canonicalObservedAt(value) {
  const parsed = new Date(value);
  if (!value || Number.isNaN(parsed.getTime())) {
    throw new Error('LEGAL_OPERATIONS_OBSERVATION_TIME_REQUIRED');
  }
  return parsed.toISOString();
}

function assertDeputyWorkCapabilityParity(work, capabilityPacket) {
  if (
    work.tenantId !== capabilityPacket.tenantId
    || work.deputyId !== capabilityPacket.deputyId
  ) {
    throw new Error('LEGAL_OPERATIONS_DEPUTY_CAPABILITY_PARITY_INVALID');
  }

  const byAttempt = new Map();
  for (const capability of capabilityPacket.capabilities) {
    if (byAttempt.has(capability.attemptId)) {
      throw new Error('LEGAL_OPERATIONS_DEPUTY_CAPABILITY_PARITY_INVALID');
    }
    byAttempt.set(capability.attemptId, capability);
  }

  if (byAttempt.size !== work.activeAttempts.length) {
    throw new Error('LEGAL_OPERATIONS_DEPUTY_CAPABILITY_PARITY_INVALID');
  }

  for (const attempt of work.activeAttempts) {
    const capability = byAttempt.get(attempt.attempt_id);
    if (
      !capability
      || capability.tenantId !== attempt.tenant_id
      || capability.deputyId !== attempt.deputy_id
      || capability.instructionId !== attempt.instruction_id
      || capability.documentId !== attempt.document_id
      || capability.currentState !== attempt.state
    ) {
      throw new Error('LEGAL_OPERATIONS_DEPUTY_CAPABILITY_PARITY_INVALID');
    }
  }

  return byAttempt;
}

function commandErrorMessage(caught) {
  return (
    caught?.response?.data?.detail
    || caught?.message
    || 'Governed Legal Operations command failed.'
  );
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

function ClientMatterRow({ item }) {
  return (
    <div className="grid gap-4 px-5 py-4 md:grid-cols-[1.2fr_1fr_0.8fr_auto] md:items-center">
      <div>
        <p className="text-sm font-black text-white">{item.matterReference}</p>
        <p className="mt-1 text-[11px] text-stone-500">
          Matter {item.caseMatterId}
        </p>
      </div>
      <div>
        <p className="text-[10px] font-black uppercase tracking-wider text-stone-600">
          Opened
        </p>
        <p className="mt-1 text-xs font-semibold text-stone-300">
          {formatTimestamp(item.openedAt)}
        </p>
      </div>
      <div className="text-xs leading-5 text-stone-500">
        Explicitly visible to this authenticated legal client.
      </div>
      <StatePill state={item.state} />
    </div>
  );
}

function DeputyAttemptRow({
  item,
  capability,
  draft,
  commandState,
  fieldDeviceId,
  onDraftChange,
  onCommand,
}) {
  const pending =
    commandState?.status === 'pending'
    && commandState?.attemptId === item.attempt_id;
  const commandKinds = capability?.nextCommandKinds || [];
  const canBegin = commandKinds.includes(FIELD_COMMAND_KIND.BEGIN);
  const canComplete = commandKinds.includes(FIELD_COMMAND_KIND.COMPLETED);
  const canNotComplete = commandKinds.includes(FIELD_COMMAND_KIND.NOT_COMPLETED);
  const commandReady =
    Boolean(fieldDeviceId)
    && Boolean(draft?.observationReference?.trim())
    && Boolean(draft?.occurredAt);

  return (
    <div>
      <AttemptQueueRow item={item} />
      <div className="border-t border-stone-900 bg-black/20 px-5 py-5">
        {!capability ? (
          <div className="rounded-xl border border-red-900/40 bg-red-950/15 p-4 text-xs text-red-300">
            Canonical field capability is unavailable for this active attempt. Commands remain closed.
          </div>
        ) : (
          <>
            <div className="grid gap-4 lg:grid-cols-[1.2fr_0.8fr]">
              <label className="block">
                <span className="text-[10px] font-black uppercase tracking-[0.16em] text-stone-500">
                  Observation evidence reference
                </span>
                <input
                  aria-label={`Observation evidence reference for ${item.attempt_id}`}
                  value={draft?.observationReference || ''}
                  onChange={(event) => onDraftChange(
                    item.attempt_id,
                    'observationReference',
                    event.target.value,
                  )}
                  placeholder="Reference the governed field observation"
                  className="mt-2 min-h-[48px] w-full rounded-xl border border-stone-800 bg-stone-950 px-4 py-3 text-sm text-white outline-none transition focus:border-amber-700/60"
                />
                <span className="mt-1 block text-[10px] leading-4 text-stone-600">
                  Reference only. The browser does not create sovereign evidence fingerprints.
                </span>
              </label>

              <label className="block">
                <span className="text-[10px] font-black uppercase tracking-[0.16em] text-stone-500">
                  Observed at
                </span>
                <input
                  aria-label={`Observed at for ${item.attempt_id}`}
                  type="datetime-local"
                  value={draft?.occurredAt || ''}
                  onChange={(event) => onDraftChange(
                    item.attempt_id,
                    'occurredAt',
                    event.target.value,
                  )}
                  className="mt-2 min-h-[48px] w-full rounded-xl border border-stone-800 bg-stone-950 px-4 py-3 text-sm text-white outline-none transition focus:border-amber-700/60"
                />
                <span className="mt-1 block text-[10px] leading-4 text-stone-600">
                  Browser-observed time; Python EOS validates chronology.
                </span>
              </label>
            </div>

            <div className="mt-4 flex flex-col gap-3 sm:flex-row sm:flex-wrap">
              {canBegin && (
                <button
                  type="button"
                  disabled={pending || !commandReady}
                  onClick={() => onCommand(item, FIELD_COMMAND_KIND.BEGIN)}
                  className="inline-flex min-h-[48px] w-full items-center justify-center gap-2 rounded-xl border border-amber-700/40 bg-amber-500/15 px-5 py-3 text-sm font-black text-amber-200 transition hover:bg-amber-500/20 disabled:cursor-not-allowed disabled:opacity-40 sm:w-auto"
                >
                  {pending ? <Loader2 className="animate-spin" size={17} /> : <Play size={17} />}
                  Begin attempt
                </button>
              )}
              {canComplete && (
                <button
                  type="button"
                  disabled={pending || !commandReady}
                  onClick={() => onCommand(item, FIELD_COMMAND_KIND.COMPLETED)}
                  className="inline-flex min-h-[48px] w-full items-center justify-center gap-2 rounded-xl border border-emerald-700/40 bg-emerald-500/15 px-5 py-3 text-sm font-black text-emerald-200 transition hover:bg-emerald-500/20 disabled:cursor-not-allowed disabled:opacity-40 sm:w-auto"
                >
                  {pending ? <Loader2 className="animate-spin" size={17} /> : <CheckCircle2 size={17} />}
                  Record completed outcome
                </button>
              )}
              {canNotComplete && (
                <button
                  type="button"
                  disabled={pending || !commandReady}
                  onClick={() => onCommand(item, FIELD_COMMAND_KIND.NOT_COMPLETED)}
                  className="inline-flex min-h-[48px] w-full items-center justify-center gap-2 rounded-xl border border-stone-700 bg-stone-900 px-5 py-3 text-sm font-black text-stone-200 transition hover:bg-stone-800 disabled:cursor-not-allowed disabled:opacity-40 sm:w-auto"
                >
                  {pending ? <Loader2 className="animate-spin" size={17} /> : <AlertTriangle size={17} />}
                  Record not completed
                </button>
              )}
            </div>

            <div className="mt-3 flex flex-wrap gap-x-4 gap-y-1 text-[10px] uppercase tracking-wider text-stone-600">
              <span>State: {capability.currentState}</span>
              <span>Device provenance: {fieldDeviceId || 'Unavailable'}</span>
              <span>Sequence lineage: server-owned</span>
            </div>

          </>
        )}
      </div>
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
  const [clientMatters, setClientMatters] = useState(EMPTY_CLIENT_MATTERS);
  const [deputyCapabilities, setDeputyCapabilities] = useState(
    EMPTY_DEPUTY_CAPABILITIES,
  );
  const [observationDrafts, setObservationDrafts] = useState({});
  const [commandState, setCommandState] = useState(null);
  const [fieldDeviceId, setFieldDeviceId] = useState('');
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
      setClientMatters(EMPTY_CLIENT_MATTERS);
      setDeputyCapabilities(EMPTY_DEPUTY_CAPABILITIES);
      setError({
        kind: 'LEGAL_ROLE_SCOPE_REQUIRED',
        message:
          'This Legal OS surface requires an explicit SHERIFF, DEPUTY, or LEGAL_CLIENT presentation scope. No privileged endpoint was queried.',
      });
      setLoading(false);
      setRefreshing(false);
      return;
    }

    try {
      if (roleMode === ROLE_MODES.DEPUTY) {
        const [work, capabilityPacket] = await Promise.all([
          getDeputyPersonalActiveWork(),
          getDeputyFieldCapabilities(),
        ]);
        assertDeputyWorkCapabilityParity(work, capabilityPacket);
        setDeputyWork(work);
        setDeputyCapabilities(capabilityPacket);
        setQueues(EMPTY_QUEUES);
        setObservationDrafts((current) => {
          const next = {};
          const observedAt = localDateTimeValue();
          for (const attempt of work.activeAttempts) {
            next[attempt.attempt_id] = current[attempt.attempt_id] || {
              observationReference: '',
              occurredAt: observedAt,
            };
          }
          return next;
        });
        setClientMatters(EMPTY_CLIENT_MATTERS);
        setLastUpdated(new Date());
        return { deputyWork: work, deputyCapabilities: capabilityPacket };
      }

      if (roleMode === ROLE_MODES.LEGAL_CLIENT) {
        const result = await getLegalClientMatters();
        setClientMatters(result);
        setQueues(EMPTY_QUEUES);
        setDeputyWork(EMPTY_DEPUTY_WORK);
        setDeputyCapabilities(EMPTY_DEPUTY_CAPABILITIES);
        setCommandState(null);
        setObservationDrafts({});
        setLastUpdated(new Date());
        return { clientMatters: result };
      }

      const result = await getSheriffOperationalQueues();
      setQueues(result);
      setDeputyWork(EMPTY_DEPUTY_WORK);
      setClientMatters(EMPTY_CLIENT_MATTERS);
      setDeputyCapabilities(EMPTY_DEPUTY_CAPABILITIES);
      setLastUpdated(new Date());
      return { queues: result };
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
      } else if (status === 403 && roleMode === ROLE_MODES.LEGAL_CLIENT) {
        setError({
          kind: 'LEGAL_CLIENT_MATTER_READ_DENIED',
          message:
            detail === 'LEGAL_CLIENT_MATTER_READ_DENIED'
              ? 'Matter visibility is restricted to current authorized LEGAL_CLIENT scope.'
              : detail || 'Matter visibility is restricted to current authorized LEGAL_CLIENT scope.',
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
      setClientMatters(EMPTY_CLIENT_MATTERS);
      setDeputyCapabilities(EMPTY_DEPUTY_CAPABILITIES);
      return null;
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [roleMode]);

  useEffect(() => {
    if (roleMode === ROLE_MODES.DEPUTY && !fieldDeviceId) {
      setFieldDeviceId(resolveBrowserFieldDeviceId());
    }
  }, [fieldDeviceId, roleMode]);

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

  const capabilityByAttempt = useMemo(
    () => new Map(
      deputyCapabilities.capabilities.map((capability) => [
        capability.attemptId,
        capability,
      ]),
    ),
    [deputyCapabilities],
  );

  const updateObservationDraft = useCallback((attemptId, field, value) => {
    setObservationDrafts((current) => ({
      ...current,
      [attemptId]: {
        ...(current[attemptId] || {
          observationReference: '',
          occurredAt: localDateTimeValue(),
        }),
        [field]: value,
      },
    }));
  }, []);

  const runDeputyFieldCommand = useCallback(async (attempt, commandKind) => {
    const capability = capabilityByAttempt.get(attempt.attempt_id);
    if (
      !capability
      || !capability.nextCommandKinds.includes(commandKind)
    ) {
      setCommandState({
        status: 'error',
        attemptId: attempt.attempt_id,
        message: 'Canonical field capability does not permit this command.',
      });
      return;
    }

    const draft = observationDrafts[attempt.attempt_id];
    const observationReference = draft?.observationReference?.trim();
    if (!observationReference) {
      setCommandState({
        status: 'error',
        attemptId: attempt.attempt_id,
        message: 'A governed observation evidence reference is required.',
      });
      return;
    }

    let occurredAt;
    try {
      occurredAt = canonicalObservedAt(draft?.occurredAt);
    } catch (caught) {
      setCommandState({
        status: 'error',
        attemptId: attempt.attempt_id,
        message: commandErrorMessage(caught),
      });
      return;
    }

    if (!fieldDeviceId) {
      setCommandState({
        status: 'error',
        attemptId: attempt.attempt_id,
        message: 'Browser field-device provenance is unavailable.',
      });
      return;
    }

    const command = {
      attemptId: attempt.attempt_id,
      currentEvidenceIdentity: capability.currentEvidenceIdentity,
      deviceId: fieldDeviceId,
      eventId: createFieldEventId(),
      occurredAt,
      observationReference,
    };
    setCommandState({
      status: 'pending',
      attemptId: attempt.attempt_id,
      message: 'Submitting observation to Python EOS and awaiting canonical refresh…',
    });

    try {
      if (commandKind === FIELD_COMMAND_KIND.BEGIN) {
        await transitionDeputyFieldAttempt(command);
      } else {
        await recordDeputyFieldOutcome({
          ...command,
          outcome:
            commandKind === FIELD_COMMAND_KIND.COMPLETED
              ? 'COMPLETED'
              : 'NOT_COMPLETED',
        });
      }

      const refreshed = await loadOperationalTruth({ refresh: true });
      if (!refreshed?.deputyWork || !refreshed?.deputyCapabilities) {
        throw new Error('LEGAL_OPERATIONS_CANONICAL_REFRESH_FAILED');
      }

      const refreshedAttempt = refreshed.deputyWork.activeAttempts.find(
        (value) => value.attempt_id === attempt.attempt_id,
      );
      const refreshedCapability = refreshed.deputyCapabilities.capabilities.find(
        (value) => value.attemptId === attempt.attempt_id,
      );

      if (commandKind === FIELD_COMMAND_KIND.BEGIN) {
        if (
          refreshedAttempt?.state !== 'ATTEMPTED'
          || refreshedCapability?.currentState !== 'ATTEMPTED'
        ) {
          throw new Error('LEGAL_OPERATIONS_CANONICAL_REFRESH_MISMATCH');
        }
      } else if (refreshedAttempt || refreshedCapability) {
        throw new Error('LEGAL_OPERATIONS_CANONICAL_REFRESH_MISMATCH');
      }

      setCommandState({
        status: 'success',
        attemptId: attempt.attempt_id,
        message:
          commandKind === FIELD_COMMAND_KIND.BEGIN
            ? 'Canonical refresh confirms this attempt is now ATTEMPTED.'
            : 'Canonical refresh confirms the terminal attempt left active work.',
      });
    } catch (caught) {
      setCommandState({
        status: 'error',
        attemptId: attempt.attempt_id,
        message: commandErrorMessage(caught),
      });
    }
  }, [
    capabilityByAttempt,
    fieldDeviceId,
    loadOperationalTruth,
    observationDrafts,
  ]);

  const metrics = useMemo(() => {
    if (roleMode === ROLE_MODES.LEGAL_CLIENT) {
      const openMatters = clientMatters.matters.filter(
        (matter) => matter.state === 'OPEN',
      ).length;
      const closedMatters = clientMatters.matters.filter(
        (matter) => matter.state === 'CLOSED',
      ).length;
      return {
        visibleMatters: clientMatters.matters.length,
        openMatters,
        closedMatters,
        officeReceipt: 0,
        deputyAssignment: 0,
        activeAttempts: 0,
        totalCurrentWork: clientMatters.matters.length,
      };
    }
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
  }, [clientMatters, deputyWork, queues, roleMode]);

  const tenantLabel =
    (
      roleMode === ROLE_MODES.DEPUTY
        ? deputyWork.tenantId
        : roleMode === ROLE_MODES.LEGAL_CLIENT
          ? clientMatters.tenantId
          : queues.tenantId
    )
    || tenantConfig?.tenantId
    || tenantConfig?.id
    || 'Awaiting authorized tenant';

  const isDeputyMode = roleMode === ROLE_MODES.DEPUTY;
  const isSheriffMode = roleMode === ROLE_MODES.SHERIFF;
  const isClientMode = roleMode === ROLE_MODES.LEGAL_CLIENT;

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
                    {isDeputyMode
                      ? 'Bound deputy cockpit'
                      : isSheriffMode
                        ? 'Certified sheriff cockpit'
                        : isClientMode
                          ? 'Client matter cockpit'
                          : 'Role scope unresolved'}
                  </span>
                </div>
                <p className="mt-1 text-sm text-stone-400">
                  {isDeputyMode
                    ? 'Binding-scoped field work with server-authorized commands. No tenant-wide queue leakage.'
                    : isSheriffMode
                      ? 'Evidence-backed operational queues. No mock legal truth.'
                      : isClientMode
                        ? 'Explicitly visible current matters only. Internal Legal Operations evidence remains closed.'
                        : 'Privileged Legal Operations surfaces remain closed until role scope resolves.'}
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

        {isClientMode && !error && (
          <>
            <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
              <QueueMetric
                icon={FileText}
                label="Visible matters"
                value={metrics.visibleMatters}
                description="Only matters with a current ACTIVE client visibility relation."
              />
              <QueueMetric
                icon={Clock3}
                label="Open matters"
                value={metrics.openMatters}
                description="Current canonical CaseMatter state is OPEN."
              />
              <QueueMetric
                icon={CheckCircle2}
                label="Closed matters"
                value={metrics.closedMatters}
                description="Current canonical CaseMatter state is CLOSED."
              />
            </section>

            <QueuePanel
              title="My matters"
              subtitle="Explicit visibility only · current canonical CaseMatter projection"
              icon={FileText}
              rows={clientMatters.matters}
              emptyMessage="No matters are currently visible to this authenticated legal client."
              renderRow={(item) => (
                <ClientMatterRow key={item.caseMatterId} item={item} />
              )}
            />

            <section className="rounded-2xl border border-sky-900/30 bg-sky-950/10 p-5">
              <div className="flex items-start gap-3">
                <ShieldCheck className="mt-0.5 text-sky-400" size={19} />
                <div>
                  <h2 className="text-sm font-black uppercase tracking-[0.12em] text-white">
                    Client visibility boundary
                  </h2>
                  <p className="mt-2 max-w-4xl text-xs leading-6 text-stone-400">
                    This view contains matter identity, client-facing reference,
                    opened time and current OPEN/CLOSED state only. Internal
                    instructions, documents, deputies, attempts, service or return
                    evidence, invoices, payments, AI outputs and settlement truth
                    are deliberately not available in this projection.
                  </p>
                </div>
              </div>
            </section>
          </>
        )}

        {isDeputyMode && (
          <>
            {commandState && (
              <section
                role={commandState.status === 'error' ? 'alert' : 'status'}
                className={
                  commandState.status === 'error'
                    ? 'rounded-2xl border border-red-900/40 bg-red-950/15 p-4 text-sm text-red-300'
                    : commandState.status === 'success'
                      ? 'rounded-2xl border border-emerald-900/40 bg-emerald-950/15 p-4 text-sm text-emerald-300'
                      : 'rounded-2xl border border-amber-900/40 bg-amber-950/15 p-4 text-sm text-amber-300'
                }
              >
                <div className="flex items-center gap-3">
                  {commandState.status === 'pending' ? (
                    <Loader2 className="animate-spin" size={18} />
                  ) : commandState.status === 'success' ? (
                    <CheckCircle2 size={18} />
                  ) : (
                    <AlertTriangle size={18} />
                  )}
                  <div>
                    <p className="font-black">
                      {commandState.status === 'pending'
                        ? 'Synchronising governed field evidence'
                        : commandState.status === 'success'
                          ? 'Canonical refresh confirmed'
                          : 'Field command not confirmed'}
                    </p>
                    <p className="mt-1 text-xs opacity-80">{commandState.message}</p>
                  </div>
                </div>
              </section>
            )}

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
              subtitle="Binding-scoped active attempts with exact server-derived field capabilities"
              icon={Clock3}
              rows={deputyWork.activeAttempts}
              emptyMessage="No active service attempts are assigned to this bound deputy."
              renderRow={(item) => (
                <DeputyAttemptRow
                  key={item.attempt_id}
                  item={item}
                  capability={capabilityByAttempt.get(item.attempt_id)}
                  draft={observationDrafts[item.attempt_id]}
                  commandState={commandState}
                  fieldDeviceId={fieldDeviceId}
                  onDraftChange={updateObservationDraft}
                  onCommand={runDeputyFieldCommand}
                />
              )}
            />
          </>
        )}

        {!isClientMode && (
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
        )}

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
 * VERSION: v8.0.1-L8-7D8-CLIENT-MATTER-COCKPIT-DENIAL-COPY-REPAIR
 * AUTHORITY BOUNDARY: governed SHERIFF/DEPUTY/LEGAL_CLIENT presentation plus deputy observation-command initiation only; Python EOS owns authority and legal truth
 * TENANT POSTURE: server-authorized tenant/client/deputy projections are required; client matter membership comes only from D5/D7 and deputy commands require exact capability parity
 * FAIL-CLOSED POSTURE: unresolved role, denied/unavailable client/internal read, capability drift, malformed observation, command failure or failed refresh never invents truth or cross-role fallback
 * FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
