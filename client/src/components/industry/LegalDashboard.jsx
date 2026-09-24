/**
 * WILSY OS — ROLE-SCOPED LEGAL OPERATIONS COCKPIT
 * VERSION: v11.1.0-L8-7D16-PERMISSION-AWARE-LEGAL-COMMAND-CENTER
 * AUTHORITY: Presentation of authenticated Python-EOS Legal Operations truth.
 * EPITOME: One role-aware WILSY Legal OS surface for legal-practice operators,
 *          finance, sheriff, deputy and client personas. Law-firm roles receive
 *          a snapshot-backed operating workspace for instructions, process
 *          documents, service attempts, certified executions, returns, exact
 *          finance evidence and governed initial intake; specialist and client
 *          roles retain least-authority views.
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
 * CERTIFICATION / UPDATE DATE: 2026-09-24
 * CHANGELOG: 2026-09-24 v11.1.0-L8-7D16-PERMISSION-AWARE-LEGAL-COMMAND-CENTER makes certified Legal Practice/Finance affordances permission-aware without treating browser permissions as authority: the canonical role remains the maximum presentation envelope and explicit legal_operations permission hints may only narrow intake, ReturnOfService and finance-evidence UI. SHERIFF/DEPUTY server-issued capabilities and LEGAL_CLIENT visibility remain unchanged.
 *            2026-09-24 v11.0.0-L8-7D15-FIRST-CLASS-MATTER-OPERATING-ROOM replaces derived matter grouping with the canonical D15 CaseMatter projection, adds matter-reference/ID/linked-work search, first-class matter selection and an operating-room drilldown across existing instruction/document/attempt/execution/return truth, and routes successful intake to the newly persisted matter only after canonical refresh. No client, custody, billing, AI, payment or settlement truth is synthesized.
 *            2026-09-23 v10.0.0-L8-7D14-PRODUCTION-LEGAL-OPERATIONS-WORKSPACE — Partner/attorney/paralegal/secretary users consume the D11 snapshot
 *            workspace through D13, navigate Command Center, Matters,
 *            Instructions, Documents, Service Operations, Returns and permitted
 *            Finance Evidence, and may register governed initial intake where
 *            their server role already owns instruction:write. Return-authorized
 *            legal-practice users can generate ReturnOfService from exact
 *            server-issued ServiceExecution evidence. LEGAL_FINANCE receives
 *            exact tariff/billing-eligibility/invoice lookup only. Existing
 *            SHERIFF, DEPUTY and LEGAL_CLIENT behavior remains role-bounded.
 *            2026-09-23 v9.0.0-L8-7D9-CLIENT-WORKSPACE-CHROME wraps LEGAL_CLIENT in the certified shared
 *            WilsyOSDashboardChrome without changing Python-EOS authority.
 *            Adds functional Overview, My Matters, and Access & Privacy menu
 *            lanes; visible-matter search; top tenant/operator chrome; live
 *            refresh; open-matters navigation; responsive 64px mobile rail;
 *            and explicit client-scope copy. No unsupported Documents, Billing,
 *            Messages, AI, service, return, payment, or settlement menu is
 *            fabricated. SHERIFF and DEPUTY render paths remain unchanged.
 *            2026-09-23 v8.0.1-L8-7D8-CLIENT-MATTER-COCKPIT-DENIAL-COPY-REPAIR keeps the exact D8 client-denial machine
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
 * SECURITY / PRIVACY POSTURE: Authenticated transport only. Practice workspace
 *                             rows are bounded current P1 projections with opaque
 *                             evidence locators; client navigation remains D7
 *                             sanitized. Browser menus and forms never create
 *                             tenant, role or lifecycle authority. A pseudonymous
 *                             browser field-device reference may be stored locally
 *                             solely for P5M ordering provenance; it is not IAM,
 *                             deputy identity, GPS, biometric or legal truth.
 * TENANT BOUNDARY: Canonical tenant scope comes only from certified server
 *                  projections; deputy identity remains server-bound and client
 *                  matter membership comes only from explicit D5/D7 visibility.
 * AUTHORITY BOUNDARY: Presentation plus initiation of already-authorized
 *                     intake, ReturnOfService and bound-Deputy commands only.
 *                     Menu state, roleView, search, generated opaque IDs and
 *                     display state never grant practice, sheriff, deputy,
 *                     finance or client authority; Python EOS independently
 *                     authorizes and owns all legal truth.
 * FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
 * FAIL-CLOSED DECLARATION: Unknown role, denied/unavailable workspace/client/
 *                          specialist reads, malformed finance evidence, intake/
 *                          return/field-command failure, capability drift or
 *                          failed canonical refresh never falls back across roles,
 *                          invents truth, or displays command success.
 */

import React, { useCallback, useEffect, useMemo, useState } from 'react';
import {
  AlertTriangle,
  Bot,
  CheckCircle2,
  ClipboardList,
  Clock3,
  FileCheck2,
  FilePlus2,
  FileText,
  Inbox,
  Landmark,
  Loader2,
  LockKeyhole,
  LogOut,
  Play,
  RefreshCw,
  Scale,
  Search,
  ShieldCheck,
  Sparkles,
  UserCheck,
} from 'lucide-react';

import {
  LEGAL_OPERATIONS_CLIENT_VERSION,
  generateLegalReturnOfService,
  getDeputyFieldCapabilities,
  getDeputyPersonalActiveWork,
  getLegalClientMatters,
  getLegalFinanceEvidence,
  getLegalPracticeWorkspace,
  getSheriffOperationalQueues,
  recordDeputyFieldOutcome,
  registerLegalIntake,
  transitionDeputyFieldAttempt,
} from '../../services/legalOperationsService.js';
import WilsyOSDashboardChrome from '../os/WilsyOSDashboardChrome.jsx';

const DASHBOARD_VERSION = 'v11.1.0-L8-7D16-PERMISSION-AWARE-LEGAL-COMMAND-CENTER';

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


const EMPTY_PRACTICE_WORKSPACE = Object.freeze({
  schema: '',
  version: '',
  tenantId: '',
  visibility: '',
  summary: Object.freeze({
    matters_total: 0,
    matters_open: 0,
    matters_closed: 0,
    instructions_total: 0,
    instructions_registered: 0,
    instructions_accepted: 0,
    instructions_closed: 0,
    instructions_cancelled: 0,
    documents_total: 0,
    documents_registered: 0,
    documents_received: 0,
    documents_allocated: 0,
    documents_returned: 0,
    attempts_total: 0,
    attempts_allocated: 0,
    attempts_attempted: 0,
    attempts_completed: 0,
    attempts_not_completed: 0,
    attempts_cancelled: 0,
    executions_total: 0,
    executions_completed: 0,
    executions_not_completed: 0,
    returns_total: 0,
  }),
  matters: Object.freeze([]),
  instructions: Object.freeze([]),
  documents: Object.freeze([]),
  attempts: Object.freeze([]),
  executions: Object.freeze([]),
  returns: Object.freeze([]),
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
  LEGAL_PRACTICE: 'LEGAL_PRACTICE',
  LEGAL_FINANCE: 'LEGAL_FINANCE',
  SHERIFF: 'SHERIFF',
  DEPUTY: 'DEPUTY',
  LEGAL_CLIENT: 'LEGAL_CLIENT',
  UNRESOLVED: 'UNRESOLVED',
});

const PRACTICE_ROLE_TOKENS = Object.freeze([
  'LEGAL_PARTNER',
  'TENANT_LEGAL_PARTNER',
  'LEGAL_ATTORNEY',
  'TENANT_LEGAL_ATTORNEY',
  'LEGAL_PARALEGAL',
  'TENANT_LEGAL_PARALEGAL',
  'LEGAL_SECRETARY',
  'TENANT_LEGAL_SECRETARY',
]);

const PRESENTATION_PERMISSIONS = Object.freeze({
  INSTRUCTION_WRITE: 'legal_operations:instruction:write',
  RETURN_WRITE: 'legal_operations:return:write',
  BILLING_READ: 'legal_operations:billing:read',
  INVOICE_READ: 'legal_operations:invoice:read',
});

const ROLE_PRESENTATION_PERMISSION_ENVELOPE = Object.freeze({
  LEGAL_PARTNER: Object.freeze([
    PRESENTATION_PERMISSIONS.INSTRUCTION_WRITE,
    PRESENTATION_PERMISSIONS.RETURN_WRITE,
    PRESENTATION_PERMISSIONS.BILLING_READ,
    PRESENTATION_PERMISSIONS.INVOICE_READ,
  ]),
  LEGAL_ATTORNEY: Object.freeze([
    PRESENTATION_PERMISSIONS.INSTRUCTION_WRITE,
    PRESENTATION_PERMISSIONS.RETURN_WRITE,
    PRESENTATION_PERMISSIONS.BILLING_READ,
    PRESENTATION_PERMISSIONS.INVOICE_READ,
  ]),
  LEGAL_PARALEGAL: Object.freeze([
    PRESENTATION_PERMISSIONS.INSTRUCTION_WRITE,
    PRESENTATION_PERMISSIONS.RETURN_WRITE,
    PRESENTATION_PERMISSIONS.INVOICE_READ,
  ]),
  LEGAL_SECRETARY: Object.freeze([
    PRESENTATION_PERMISSIONS.RETURN_WRITE,
    PRESENTATION_PERMISSIONS.INVOICE_READ,
  ]),
  LEGAL_FINANCE: Object.freeze([
    PRESENTATION_PERMISSIONS.BILLING_READ,
    PRESENTATION_PERMISSIONS.INVOICE_READ,
  ]),
});

const PRACTICE_WORKSPACE_VIEWS = Object.freeze({
  COMMAND: 'COMMAND',
  MATTERS: 'MATTERS',
  INSTRUCTIONS: 'INSTRUCTIONS',
  DOCUMENTS: 'DOCUMENTS',
  SERVICE: 'SERVICE',
  RETURNS: 'RETURNS',
  FINANCE: 'FINANCE',
  INTAKE: 'INTAKE',
});

const CLIENT_WORKSPACE_VIEWS = Object.freeze({
  OVERVIEW: 'OVERVIEW',
  MATTERS: 'MATTERS',
  ACCESS: 'ACCESS',
});

function normalizeRoleToken(value) {
  return String(value || '')
    .trim()
    .replace(/[^A-Za-z0-9]+/g, '_')
    .toUpperCase();
}

function canonicalPresentationRole(value) {
  return normalizeRoleToken(value).replace(/^TENANT_/, '');
}

function explicitLegalPermissionHints(user) {
  const values = [
    ...(Array.isArray(user?.permissions) ? user.permissions : []),
    ...(Array.isArray(user?.enabledPermissions) ? user.enabledPermissions : []),
  ];
  return new Set(
    values
      .map((permission) => String(permission || '').trim())
      .filter((permission) => permission.startsWith('legal_operations:')),
  );
}

function presentationAllowsPermission({ roleToken, user, permission }) {
  const role = canonicalPresentationRole(roleToken);
  const roleEnvelope = ROLE_PRESENTATION_PERMISSION_ENVELOPE[role] || [];
  if (!roleEnvelope.includes(permission)) return false;

  const explicitHints = explicitLegalPermissionHints(user);
  if (explicitHints.size === 0) return true;
  return explicitHints.has(permission);
}

function resolveRoleMode(value) {
  const token = normalizeRoleToken(value);
  if (PRACTICE_ROLE_TOKENS.includes(token)) return ROLE_MODES.LEGAL_PRACTICE;
  if (
    token === 'LEGAL_FINANCE'
    || token === 'TENANT_LEGAL_FINANCE'
  ) {
    return ROLE_MODES.LEGAL_FINANCE;
  }
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

function LegalClientWorkspace({
  clientMatters,
  error,
  lastUpdated,
  metrics,
  onLogout,
  onRefresh,
  refreshing,
  tenantConfig,
  user,
}) {
  const [activeView, setActiveView] = useState(CLIENT_WORKSPACE_VIEWS.OVERVIEW);
  const [searchQuery, setSearchQuery] = useState('');

  const normalizedQuery = searchQuery.trim().toLowerCase();
  const filteredMatters = useMemo(
    () => (
      normalizedQuery
        ? clientMatters.matters.filter((matter) => (
          matter.caseMatterId.toLowerCase().includes(normalizedQuery)
          || matter.matterReference.toLowerCase().includes(normalizedQuery)
        ))
        : clientMatters.matters
    ),
    [clientMatters.matters, normalizedQuery],
  );

  const chromeMetrics = useMemo(() => ([
    {
      id: 'visible',
      label: 'Visible matters',
      value: metrics.visibleMatters,
      detail: 'ACTIVE visibility only',
    },
    {
      id: 'open',
      label: 'Open matters',
      value: metrics.openMatters,
      detail: 'Current CaseMatter OPEN',
    },
    {
      id: 'closed',
      label: 'Closed matters',
      value: metrics.closedMatters,
      detail: 'Current CaseMatter CLOSED',
    },
  ]), [metrics.closedMatters, metrics.openMatters, metrics.visibleMatters]);

  const navItems = [
    {
      id: CLIENT_WORKSPACE_VIEWS.OVERVIEW,
      label: 'Overview',
      icon: ClipboardList,
    },
    {
      id: CLIENT_WORKSPACE_VIEWS.MATTERS,
      label: 'My Matters',
      icon: FileText,
    },
    {
      id: CLIENT_WORKSPACE_VIEWS.ACCESS,
      label: 'Access & Privacy',
      icon: ShieldCheck,
    },
  ];

  const tenant = {
    ...(tenantConfig || {}),
    tenantId:
      clientMatters.tenantId
      || tenantConfig?.tenantId
      || tenantConfig?.id
      || '',
  };
  const operator = {
    ...(user || {}),
    displayName:
      user?.displayName
      || user?.name
      || user?.email
      || 'Authenticated legal client',
    role: 'LEGAL_CLIENT',
  };

  const leftRail = (
    <nav aria-label="Legal client workspace navigation">
      {navItems.map(({ id, label, icon: Icon }) => (
        <button
          key={id}
          type="button"
          data-active={activeView === id ? 'true' : 'false'}
          aria-current={activeView === id ? 'page' : undefined}
          onClick={() => setActiveView(id)}
          title={label}
        >
          <Icon size={16} />
          <span>{label}</span>
        </button>
      ))}
      {typeof onLogout === 'function' && (
        <button type="button" onClick={onLogout} title="Sign out">
          <LogOut size={16} />
          <span>Sign out</span>
        </button>
      )}
    </nav>
  );

  const errorSurface = error ? (
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
  ) : null;

  let workspaceContent = null;

  if (!error && activeView === CLIENT_WORKSPACE_VIEWS.OVERVIEW) {
    workspaceContent = (
      <div className="space-y-6">
        <section className="rounded-2xl border border-amber-900/30 bg-gradient-to-br from-amber-950/15 via-stone-950 to-stone-950 p-5">
          <div className="flex flex-col justify-between gap-4 lg:flex-row lg:items-end">
            <div>
              <p className="text-[10px] font-black uppercase tracking-[0.2em] text-amber-500">
                Client workspace
              </p>
              <h2 className="mt-2 text-xl font-black text-white">
                Your explicitly visible legal matters
              </h2>
              <p className="mt-2 max-w-3xl text-sm leading-6 text-stone-400">
                This workspace is limited to current matters granted to this authenticated legal client. Internal Legal Operations evidence remains closed.
              </p>
            </div>
            <div className="rounded-xl border border-stone-800 bg-black/35 px-4 py-3 text-right">
              <p className="text-[9px] font-black uppercase tracking-wider text-stone-600">
                Evidence refresh
              </p>
              <p className="mt-1 text-xs font-semibold text-stone-300">
                {lastUpdated ? lastUpdated.toLocaleTimeString() : 'Not available'}
              </p>
            </div>
          </div>
        </section>

        <QueuePanel
          title="Visible matter snapshot"
          subtitle="Current certified client projection"
          icon={FileText}
          rows={filteredMatters.slice(0, 4)}
          emptyMessage={
            normalizedQuery
              ? 'No visible matters match this search.'
              : 'No matters are currently visible to this authenticated legal client.'
          }
          renderRow={(item) => (
            <ClientMatterRow key={item.caseMatterId} item={item} />
          )}
        />
      </div>
    );
  } else if (!error && activeView === CLIENT_WORKSPACE_VIEWS.MATTERS) {
    workspaceContent = (
      <QueuePanel
        title="My matters"
        subtitle="Explicit visibility only · current canonical CaseMatter projection"
        icon={FileText}
        rows={filteredMatters}
        emptyMessage={
          normalizedQuery
            ? 'No visible matters match this search.'
            : 'No matters are currently visible to this authenticated legal client.'
        }
        renderRow={(item) => (
          <ClientMatterRow key={item.caseMatterId} item={item} />
        )}
      />
    );
  } else if (!error && activeView === CLIENT_WORKSPACE_VIEWS.ACCESS) {
    workspaceContent = (
      <div className="grid gap-5 xl:grid-cols-2">
        <section className="rounded-2xl border border-emerald-900/30 bg-emerald-950/10 p-5">
          <div className="flex items-start gap-3">
            <ShieldCheck className="mt-0.5 text-emerald-400" size={19} />
            <div>
              <h2 className="text-sm font-black uppercase tracking-[0.12em] text-white">
                Available in this client projection
              </h2>
              <ul className="mt-4 space-y-3 text-sm text-stone-300">
                <li>Matter identity and client-facing reference</li>
                <li>Opened timestamp</li>
                <li>Current OPEN or CLOSED matter state</li>
                <li>Only matters with current ACTIVE client visibility</li>
              </ul>
            </div>
          </div>
        </section>

        <section className="rounded-2xl border border-sky-900/30 bg-sky-950/10 p-5">
          <div className="flex items-start gap-3">
            <LockKeyhole className="mt-0.5 text-sky-400" size={19} />
            <div>
              <h2 className="text-sm font-black uppercase tracking-[0.12em] text-white">
                Access & privacy boundary
              </h2>
              <p className="mt-3 text-sm leading-6 text-stone-400">
                Internal instructions, documents, deputies, service attempts,
                service or return evidence, invoices, payments, AI outputs and
                settlement truth are deliberately unavailable in this projection.
              </p>
            </div>
          </div>
        </section>
      </div>
    );
  }

  return (
    <WilsyOSDashboardChrome
      dashboardKey="legal-client"
      commandLabel="WILSY Legal OS"
      title="Client Matter Workspace"
      role="LEGAL_CLIENT"
      posture={error ? 'SOURCE_GAPS' : 'LIVE'}
      tenant={tenant}
      operator={operator}
      storyMessages={[
        'Explicit visibility only',
        'Current CaseMatter truth',
        'Python EOS remains sovereign',
      ]}
      search={{
        value: searchQuery,
        placeholder: 'Search visible matters',
        onChange: (event) => {
          setSearchQuery(event.target.value);
          if (event.target.value) setActiveView(CLIENT_WORKSPACE_VIEWS.MATTERS);
        },
        onFocus: () => setActiveView(CLIENT_WORKSPACE_VIEWS.MATTERS),
      }}
      actions={{
        liveSyncLabel: 'Refresh truth',
        onLiveSync: onRefresh,
        isRefreshing: refreshing,
        primaryActionLabel: 'Open matters',
        onPrimaryAction: () => setActiveView(CLIENT_WORKSPACE_VIEWS.MATTERS),
      }}
      metrics={chromeMetrics}
      leftRail={leftRail}
    >
      <div className="space-y-6">
        {errorSurface}
        {workspaceContent}
        <footer className="flex flex-col justify-between gap-3 border-t border-stone-900 py-5 text-[10px] uppercase tracking-[0.15em] text-stone-700 md:flex-row">
          <span>{DASHBOARD_VERSION}</span>
          <span>Presentation only · Python EOS remains sovereign legal truth</span>
        </footer>
      </div>
    </WilsyOSDashboardChrome>
  );
}


function WorkspaceErrorSurface({ error }) {
  if (!error) return null;
  return (
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
            WILSY Legal OS fails closed rather than substituting synthetic legal evidence.
          </p>
        </div>
      </div>
    </section>
  );
}

function PracticeLifecycleRow({ item, kind, action = null }) {
  const definitions = {
    instruction: {
      id: item.instruction_id,
      secondary: `Matter ${item.case_matter_id}`,
      detail: `Document ${item.document_id}`,
      timestamp: item.registered_at,
      state: item.state,
    },
    document: {
      id: item.document_id,
      secondary: item.document_type,
      detail: `Matter ${item.case_matter_id}`,
      timestamp: item.registered_at,
      state: item.state,
    },
    attempt: {
      id: item.attempt_id,
      secondary: `Instruction ${item.instruction_id}`,
      detail: `Deputy ${item.deputy_id}`,
      timestamp: item.allocated_at,
      state: item.state,
    },
    execution: {
      id: item.service_execution_id,
      secondary: `Attempt ${item.attempt_id}`,
      detail: `Document ${item.document_id}`,
      timestamp: item.executed_at,
      state: item.outcome,
    },
    return: {
      id: item.return_id,
      secondary: `Execution ${item.service_execution_id}`,
      detail: `Instruction ${item.instruction_id}`,
      timestamp: item.generated_at,
      state: item.state,
    },
  };
  const view = definitions[kind];
  return (
    <div className="grid gap-4 px-5 py-4 lg:grid-cols-[1.3fr_1fr_1fr_auto] lg:items-center">
      <div className="min-w-0">
        <p className="truncate text-sm font-black text-white">{view.id}</p>
        <p className="mt-1 truncate text-[11px] text-stone-500">{view.secondary}</p>
      </div>
      <div>
        <p className="text-xs font-semibold text-stone-300">{view.detail}</p>
        <p className="mt-1 text-[10px] text-stone-600">{formatTimestamp(view.timestamp)}</p>
      </div>
      <div>
        <p className="text-[9px] font-black uppercase tracking-wider text-stone-600">
          Evidence locator
        </p>
        <p className="mt-1 truncate font-mono text-[10px] text-stone-500" title={item.evidence_identity}>
          {item.evidence_identity}
        </p>
      </div>
      <div className="flex flex-wrap items-center gap-2 lg:justify-end">
        <StatePill state={view.state} />
        {action}
      </div>
    </div>
  );
}

function matterLineage(workspace, caseMatterId) {
  const instructions = workspace.instructions.filter(
    (item) => item.case_matter_id === caseMatterId,
  );
  const documents = workspace.documents.filter(
    (item) => item.case_matter_id === caseMatterId,
  );
  const instructionIds = new Set(instructions.map((item) => item.instruction_id));
  const documentIds = new Set(documents.map((item) => item.document_id));
  const attempts = workspace.attempts.filter(
    (item) => instructionIds.has(item.instruction_id) || documentIds.has(item.document_id),
  );
  const attemptIds = new Set(attempts.map((item) => item.attempt_id));
  const executions = workspace.executions.filter(
    (item) => attemptIds.has(item.attempt_id)
      || instructionIds.has(item.instruction_id)
      || documentIds.has(item.document_id),
  );
  const executionIds = new Set(executions.map((item) => item.service_execution_id));
  const returns = workspace.returns.filter(
    (item) => executionIds.has(item.service_execution_id)
      || attemptIds.has(item.attempt_id)
      || instructionIds.has(item.instruction_id)
      || documentIds.has(item.document_id),
  );
  return { instructions, documents, attempts, executions, returns };
}

function MatterOperationsPanel({
  workspace,
  searchQuery,
  selectedMatterId,
  onSelectMatter,
  overview = false,
}) {
  const canonicalMatters = Array.isArray(workspace.matters) ? workspace.matters : [];
  const normalized = searchQuery.trim().toLowerCase();
  const matters = useMemo(
    () => canonicalMatters.filter((matter) => {
      if (!normalized) return true;
      if (
        matter.case_matter_id.toLowerCase().includes(normalized)
        || matter.matter_reference.toLowerCase().includes(normalized)
      ) {
        return true;
      }
      const lineage = matterLineage(workspace, matter.case_matter_id);
      return Object.values(lineage).some((rows) => (
        rows.some((row) => Object.values(row).some(
          (value) => typeof value === 'string' && value.toLowerCase().includes(normalized),
        ))
      ));
    }),
    [canonicalMatters, normalized, workspace],
  );

  const selectedMatter = canonicalMatters.find(
    (matter) => matter.case_matter_id === selectedMatterId,
  ) || null;
  const selectedLineage = useMemo(
    () => (selectedMatter
      ? matterLineage(workspace, selectedMatter.case_matter_id)
      : null),
    [selectedMatter, workspace],
  );

  const matterRows = overview ? matters.slice(0, 5) : matters;

  return (
    <div className="space-y-6">
      <QueuePanel
        title={overview ? 'Matter register' : 'Matters'}
        subtitle="First-class canonical CaseMatter truth · select a matter to operate its linked current lifecycle"
        icon={Scale}
        rows={matterRows}
        emptyMessage={
          normalized
            ? 'No canonical matter or linked current legal work matches this search.'
            : 'No canonical CaseMatter is currently available for this tenant.'
        }
        renderRow={(matter) => {
          const lineage = matterLineage(workspace, matter.case_matter_id);
          const activeInstructions = lineage.instructions.filter(
            (item) => ['REGISTERED', 'ACCEPTED'].includes(item.state),
          ).length;
          return (
            <div
              key={matter.case_matter_id}
              className="grid gap-4 px-5 py-4 lg:grid-cols-[1.35fr_0.8fr_1fr_auto] lg:items-center"
            >
              <div>
                <p className="text-sm font-black text-white">{matter.matter_reference}</p>
                <p className="mt-1 font-mono text-[10px] text-stone-500">
                  {matter.case_matter_id}
                </p>
                <p className="mt-1 text-[10px] text-stone-600">
                  Opened {formatTimestamp(matter.opened_at)}
                </p>
              </div>
              <div>
                <p className="text-[9px] font-black uppercase tracking-wider text-stone-600">
                  Matter state
                </p>
                <div className="mt-2"><StatePill state={matter.state} /></div>
              </div>
              <div>
                <p className="text-[9px] font-black uppercase tracking-wider text-stone-600">
                  Current linked work
                </p>
                <p className="mt-1 text-xs font-semibold text-stone-300">
                  {lineage.instructions.length} instruction(s) · {lineage.documents.length} document(s)
                </p>
                <p className="mt-1 text-[10px] text-stone-600">
                  {activeInstructions} active instruction(s) · {lineage.attempts.length} attempt(s)
                </p>
              </div>
              <button
                type="button"
                onClick={() => onSelectMatter(matter.case_matter_id)}
                className="inline-flex min-h-[42px] items-center justify-center rounded-lg border border-amber-700/40 bg-amber-500/10 px-4 text-[11px] font-black text-amber-200 transition hover:bg-amber-500/20"
              >
                Open matter
              </button>
            </div>
          );
        }}
      />

      {!overview && selectedMatter && selectedLineage && (
        <section
          aria-label="Matter Operating Room"
          className="overflow-hidden rounded-2xl border border-amber-900/35 bg-stone-950/80"
        >
          <header className="border-b border-stone-800 bg-amber-500/[0.04] px-5 py-5">
            <div className="flex flex-col justify-between gap-4 lg:flex-row lg:items-start">
              <div>
                <div className="flex items-center gap-2 text-amber-400">
                  <Scale size={18} />
                  <span className="text-[9px] font-black uppercase tracking-[0.18em]">
                    Matter Operating Room
                  </span>
                </div>
                <h2 className="mt-2 text-xl font-black text-white">
                  {selectedMatter.matter_reference}
                </h2>
                <p className="mt-1 font-mono text-[10px] text-stone-500">
                  {selectedMatter.case_matter_id}
                </p>
              </div>
              <div className="flex flex-wrap items-center gap-3">
                <StatePill state={selectedMatter.state} />
                <button
                  type="button"
                  onClick={() => onSelectMatter(null)}
                  className="min-h-[40px] rounded-lg border border-stone-800 bg-black/30 px-4 text-[11px] font-black text-stone-300"
                >
                  Close matter view
                </button>
              </div>
            </div>

            <div className="mt-5 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
              <div className="rounded-xl border border-stone-800 bg-black/25 p-4">
                <p className="text-[9px] font-black uppercase tracking-wider text-stone-600">Opened</p>
                <p className="mt-1 text-xs font-semibold text-stone-300">{formatTimestamp(selectedMatter.opened_at)}</p>
              </div>
              <div className="rounded-xl border border-stone-800 bg-black/25 p-4">
                <p className="text-[9px] font-black uppercase tracking-wider text-stone-600">Instructions</p>
                <p className="mt-1 text-lg font-black text-white">{selectedLineage.instructions.length}</p>
              </div>
              <div className="rounded-xl border border-stone-800 bg-black/25 p-4">
                <p className="text-[9px] font-black uppercase tracking-wider text-stone-600">Process documents</p>
                <p className="mt-1 text-lg font-black text-white">{selectedLineage.documents.length}</p>
              </div>
              <div className="rounded-xl border border-stone-800 bg-black/25 p-4">
                <p className="text-[9px] font-black uppercase tracking-wider text-stone-600">Service / returns</p>
                <p className="mt-1 text-xs font-semibold text-stone-300">
                  {selectedLineage.executions.length} execution(s) · {selectedLineage.returns.length} return(s)
                </p>
              </div>
            </div>

            <div className="mt-4 rounded-xl border border-stone-800 bg-black/25 p-4">
              <p className="text-[9px] font-black uppercase tracking-wider text-stone-600">
                Matter evidence locator
              </p>
              <p
                className="mt-1 break-all font-mono text-[10px] text-stone-500"
                title={selectedMatter.evidence_identity}
              >
                {selectedMatter.evidence_identity}
              </p>
            </div>
          </header>

          <div className="space-y-5 p-5">
            <QueuePanel
              title="Instructions"
              subtitle="Current instruction truth linked to this canonical matter"
              icon={Inbox}
              rows={selectedLineage.instructions}
              emptyMessage="No current LegalInstruction is linked to this matter."
              renderRow={(item) => (
                <PracticeLifecycleRow key={item.instruction_id} item={item} kind="instruction" />
              )}
            />
            <QueuePanel
              title="Process documents"
              subtitle="Current ProcessDocument truth linked to this canonical matter"
              icon={FileText}
              rows={selectedLineage.documents}
              emptyMessage="No current ProcessDocument is linked to this matter."
              renderRow={(item) => (
                <PracticeLifecycleRow key={item.document_id} item={item} kind="document" />
              )}
            />
            <div className="grid gap-5 xl:grid-cols-2">
              <QueuePanel
                title="Service attempts"
                subtitle="Attempt truth linked through the matter's instruction/document lineage"
                icon={Clock3}
                rows={selectedLineage.attempts}
                emptyMessage="No current ServiceAttempt is linked to this matter."
                renderRow={(item) => (
                  <PracticeLifecycleRow key={item.attempt_id} item={item} kind="attempt" />
                )}
              />
              <QueuePanel
                title="Returns of Service"
                subtitle="Generated return evidence linked to this matter · not invoice truth"
                icon={FileCheck2}
                rows={selectedLineage.returns}
                emptyMessage="No ReturnOfService is currently linked to this matter."
                renderRow={(item) => (
                  <PracticeLifecycleRow key={item.return_id} item={item} kind="return" />
                )}
              />
            </div>
          </div>
        </section>
      )}
    </div>
  );
}

function LegalFinanceLookup({ roleToken, user }) {
  const canReadBilling = presentationAllowsPermission({
    roleToken,
    user,
    permission: PRESENTATION_PERMISSIONS.BILLING_READ,
  });
  const canReadInvoice = presentationAllowsPermission({
    roleToken,
    user,
    permission: PRESENTATION_PERMISSIONS.INVOICE_READ,
  });
  const allowedKinds = useMemo(() => [
    ...(canReadBilling ? ['TARIFF_ASSESSMENT', 'BILLING_ELIGIBILITY'] : []),
    ...(canReadInvoice ? ['INVOICE'] : []),
  ], [canReadBilling, canReadInvoice]);
  const [kind, setKind] = useState('INVOICE');
  const [identity, setIdentity] = useState('');
  const [result, setResult] = useState(null);
  const [lookupError, setLookupError] = useState('');
  const [pending, setPending] = useState(false);

  useEffect(() => {
    if (allowedKinds.length === 0) {
      if (kind) setKind('');
      return;
    }
    if (!allowedKinds.includes(kind)) setKind(allowedKinds[0]);
  }, [allowedKinds, kind]);

  const submit = async (event) => {
    event.preventDefault();
    setLookupError('');
    setResult(null);
    if (!allowedKinds.includes(kind)) {
      setLookupError('LEGAL_OPERATIONS_FINANCE_PRESENTATION_PERMISSION_DENIED');
      return;
    }
    setPending(true);
    try {
      setResult(await getLegalFinanceEvidence(kind, identity.trim()));
    } catch (caught) {
      setLookupError(commandErrorMessage(caught));
    } finally {
      setPending(false);
    }
  };

  if (allowedKinds.length === 0) {
    return (
      <section className="rounded-2xl border border-stone-800 bg-stone-950/75 p-6">
        <div className="flex items-start gap-3">
          <LockKeyhole className="mt-0.5 text-stone-500" size={20} />
          <div>
            <h2 className="text-sm font-black uppercase tracking-[0.12em] text-white">Finance evidence is read-only for this permission posture</h2>
            <p className="mt-2 text-sm leading-6 text-stone-400">
              Browser permission hints may only narrow presentation. Python EOS remains the authorization authority for legal billing and invoice evidence.
            </p>
          </div>
        </div>
      </section>
    );
  }

  return (
    <section className="overflow-hidden rounded-2xl border border-stone-800 bg-stone-950/75">
      <header className="border-b border-stone-800 px-5 py-4">
        <div className="flex items-center gap-3">
          <div className="rounded-xl border border-amber-800/30 bg-amber-500/10 p-2.5 text-amber-400">
            <Landmark size={18} />
          </div>
          <div>
            <h2 className="text-sm font-black uppercase tracking-[0.12em] text-white">
              Finance evidence
            </h2>
            <p className="mt-1 text-[11px] text-stone-500">
              Exact-ID evidence lookup only · no payment or settlement inference
            </p>
          </div>
        </div>
      </header>

      <div className="p-5">
        <form onSubmit={submit} className="grid gap-4 lg:grid-cols-[0.8fr_1.6fr_auto] lg:items-end">
          <label>
            <span className="text-[10px] font-black uppercase tracking-wider text-stone-500">Evidence type</span>
            <select
              aria-label="Finance evidence type"
              value={kind}
              onChange={(event) => setKind(event.target.value)}
              className="mt-2 min-h-[48px] w-full rounded-xl border border-stone-800 bg-black px-4 text-sm text-white"
            >
              {allowedKinds.includes('TARIFF_ASSESSMENT') && <option value="TARIFF_ASSESSMENT">Tariff assessment</option>}
              {allowedKinds.includes('BILLING_ELIGIBILITY') && <option value="BILLING_ELIGIBILITY">Billing eligibility</option>}
              {canReadInvoice && <option value="INVOICE">Client invoice</option>}
            </select>
          </label>
          <label>
            <span className="text-[10px] font-black uppercase tracking-wider text-stone-500">Exact evidence identity</span>
            <input
              aria-label="Finance evidence identity"
              value={identity}
              onChange={(event) => setIdentity(event.target.value)}
              placeholder="Enter exact assessment, eligibility or invoice id"
              className="mt-2 min-h-[48px] w-full rounded-xl border border-stone-800 bg-black px-4 text-sm text-white outline-none focus:border-amber-700/60"
            />
          </label>
          <button
            type="submit"
            disabled={pending || !identity.trim()}
            className="inline-flex min-h-[48px] items-center justify-center gap-2 rounded-xl border border-amber-700/40 bg-amber-500/15 px-5 text-sm font-black text-amber-200 disabled:opacity-40"
          >
            {pending ? <Loader2 className="animate-spin" size={17} /> : <Search size={17} />}
            Verify evidence
          </button>
        </form>

        {lookupError && (
          <p className="mt-4 rounded-xl border border-red-900/40 bg-red-950/15 p-4 text-xs text-red-300">
            {lookupError}
          </p>
        )}

        {result && (
          <div className="mt-5 rounded-xl border border-emerald-900/30 bg-emerald-950/10 p-5">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div>
                <p className="text-[9px] font-black uppercase tracking-wider text-emerald-500">Canonical finance evidence</p>
                <p className="mt-1 text-sm font-black text-white">{result.entityType}</p>
                <p className="mt-1 font-mono text-[10px] text-stone-500">{result.entityIdentity}</p>
              </div>
              <StatePill state={result.visibility} />
            </div>
            <div className="mt-5 grid gap-3 md:grid-cols-2 xl:grid-cols-3">
              {Object.entries(result.data).map(([key, value]) => (
                <div key={key} className="rounded-lg border border-stone-800 bg-black/30 p-3">
                  <p className="text-[9px] font-black uppercase tracking-wider text-stone-600">{key.replaceAll('_', ' ')}</p>
                  <p className="mt-1 break-words text-xs text-stone-300">
                    {typeof value === 'object' ? JSON.stringify(value) : String(value)}
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </section>
  );
}

function createIntakeDraft() {
  const token = createOpaqueBrowserToken();
  const observedAt = new Date().toISOString();
  return {
    caseMatterId: `matter-${token}`,
    instructionId: `instruction-${token}`,
    documentId: `document-${token}`,
    registrationCustodyEventId: `custody-${token}`,
    matterReference: '',
    documentType: '',
    matterEvidenceReference: '',
    instructionEvidenceReference: '',
    documentRegistrationEvidenceReference: '',
    caseOpenedAt: observedAt,
    instructionRegisteredAt: observedAt,
    documentRegisteredAt: observedAt,
  };
}

function LegalIntakePanel({ onRefresh, onRegistered, roleToken, user }) {
  const canWrite = presentationAllowsPermission({
    roleToken,
    user,
    permission: PRESENTATION_PERMISSIONS.INSTRUCTION_WRITE,
  });
  const [draft, setDraft] = useState(() => createIntakeDraft());
  const [status, setStatus] = useState(null);

  if (!canWrite) {
    return (
      <section className="rounded-2xl border border-stone-800 bg-stone-950/75 p-6">
        <div className="flex items-start gap-3">
          <LockKeyhole className="mt-0.5 text-stone-500" size={20} />
          <div>
            <h2 className="text-sm font-black uppercase tracking-[0.12em] text-white">Instruction intake is read-only for this role</h2>
            <p className="mt-2 text-sm leading-6 text-stone-400">
              The browser does not elevate instruction:write authority. Use a Partner, Attorney or Paralegal identity with current server authorization.
            </p>
          </div>
        </div>
      </section>
    );
  }

  const update = (field, value) => setDraft((current) => ({ ...current, [field]: value }));

  const submit = async (event) => {
    event.preventDefault();
    setStatus({ kind: 'pending', message: 'Registering canonical intake…' });
    try {
      const submittedMatter = {
        caseMatterId: draft.caseMatterId,
        matterReference: draft.matterReference.trim(),
      };
      const result = await registerLegalIntake(draft);
      const refreshed = await onRefresh();
      const refreshedMatters = refreshed?.practiceWorkspace?.matters;
      const matterIsDiscoverable = Array.isArray(refreshedMatters)
        && refreshedMatters.some(
          (matter) => matter.case_matter_id === submittedMatter.caseMatterId,
        );
      if (!matterIsDiscoverable) {
        throw new Error('LEGAL_OPERATIONS_INTAKE_REFRESH_MATTER_NOT_FOUND');
      }
      setStatus({
        kind: 'success',
        message: `${result.disposition}: canonical refresh confirmed ${submittedMatter.matterReference} in the matter workspace.`,
      });
      if (typeof onRegistered === 'function') onRegistered(submittedMatter);
      setDraft(createIntakeDraft());
    } catch (caught) {
      setStatus({ kind: 'error', message: commandErrorMessage(caught) });
    }
  };

  const pending = status?.kind === 'pending';

  return (
    <section className="overflow-hidden rounded-2xl border border-stone-800 bg-stone-950/75">
      <header className="border-b border-stone-800 px-5 py-4">
        <div className="flex items-center gap-3">
          <div className="rounded-xl border border-amber-800/30 bg-amber-500/10 p-2.5 text-amber-400">
            <FilePlus2 size={18} />
          </div>
          <div>
            <h2 className="text-sm font-black uppercase tracking-[0.12em] text-white">New instruction / intake</h2>
            <p className="mt-1 text-[11px] text-stone-500">
              Creates registration facts only · not receipt, allocation, service, invoice or payment truth
            </p>
          </div>
        </div>
      </header>

      <form onSubmit={submit} className="grid gap-5 p-5 xl:grid-cols-2">
        <label>
          <span className="text-[10px] font-black uppercase tracking-wider text-stone-500">Matter reference</span>
          <input
            aria-label="Matter reference"
            required
            value={draft.matterReference}
            onChange={(event) => update('matterReference', event.target.value)}
            placeholder="e.g. CASE-2026-00142"
            className="mt-2 min-h-[48px] w-full rounded-xl border border-stone-800 bg-black px-4 text-sm text-white"
          />
        </label>
        <label>
          <span className="text-[10px] font-black uppercase tracking-wider text-stone-500">Process document type</span>
          <input
            aria-label="Process document type"
            required
            value={draft.documentType}
            onChange={(event) => update('documentType', event.target.value)}
            placeholder="e.g. summons"
            className="mt-2 min-h-[48px] w-full rounded-xl border border-stone-800 bg-black px-4 text-sm text-white"
          />
        </label>
        <label>
          <span className="text-[10px] font-black uppercase tracking-wider text-stone-500">Matter evidence reference</span>
          <input
            aria-label="Matter evidence reference"
            required
            value={draft.matterEvidenceReference}
            onChange={(event) => update('matterEvidenceReference', event.target.value)}
            placeholder="Reference the governed intake evidence"
            className="mt-2 min-h-[48px] w-full rounded-xl border border-stone-800 bg-black px-4 text-sm text-white"
          />
        </label>
        <label>
          <span className="text-[10px] font-black uppercase tracking-wider text-stone-500">Instruction evidence reference</span>
          <input
            aria-label="Instruction evidence reference"
            required
            value={draft.instructionEvidenceReference}
            onChange={(event) => update('instructionEvidenceReference', event.target.value)}
            placeholder="Reference the instruction evidence"
            className="mt-2 min-h-[48px] w-full rounded-xl border border-stone-800 bg-black px-4 text-sm text-white"
          />
        </label>
        <label className="xl:col-span-2">
          <span className="text-[10px] font-black uppercase tracking-wider text-stone-500">Document registration evidence reference</span>
          <input
            aria-label="Document registration evidence reference"
            required
            value={draft.documentRegistrationEvidenceReference}
            onChange={(event) => update('documentRegistrationEvidenceReference', event.target.value)}
            placeholder="Reference the document registration evidence"
            className="mt-2 min-h-[48px] w-full rounded-xl border border-stone-800 bg-black px-4 text-sm text-white"
          />
        </label>

        <div className="xl:col-span-2 rounded-xl border border-stone-800 bg-black/30 p-4">
          <p className="text-[9px] font-black uppercase tracking-wider text-stone-600">Opaque registration identities</p>
          <div className="mt-2 grid gap-2 font-mono text-[10px] text-stone-500 md:grid-cols-2">
            <span>{draft.caseMatterId}</span>
            <span>{draft.instructionId}</span>
            <span>{draft.documentId}</span>
            <span>{draft.registrationCustodyEventId}</span>
          </div>
        </div>

        {status && (
          <div className={`xl:col-span-2 rounded-xl border p-4 text-xs ${
            status.kind === 'error'
              ? 'border-red-900/40 bg-red-950/15 text-red-300'
              : status.kind === 'success'
                ? 'border-emerald-900/40 bg-emerald-950/15 text-emerald-300'
                : 'border-amber-900/40 bg-amber-950/15 text-amber-300'
          }`}>
            {status.message}
          </div>
        )}

        <div className="xl:col-span-2 flex justify-end">
          <button
            type="submit"
            disabled={
              pending
              || !draft.matterReference.trim()
              || !draft.documentType.trim()
              || !draft.matterEvidenceReference.trim()
              || !draft.instructionEvidenceReference.trim()
              || !draft.documentRegistrationEvidenceReference.trim()
            }
            className="inline-flex min-h-[48px] w-full items-center justify-center gap-2 rounded-xl border border-amber-700/40 bg-amber-500/15 px-6 text-sm font-black text-amber-200 disabled:opacity-40 sm:w-auto"
          >
            {pending ? <Loader2 className="animate-spin" size={17} /> : <FilePlus2 size={17} />}
            Register instruction
          </button>
        </div>
      </form>
    </section>
  );
}

function LegalPracticeWorkspace({
  error,
  lastUpdated,
  onLogout,
  onRefresh,
  refreshing,
  roleView,
  tenantConfig,
  user,
  workspace,
}) {
  const roleToken = normalizeRoleToken(roleView);
  const canIntake = presentationAllowsPermission({
    roleToken,
    user,
    permission: PRESENTATION_PERMISSIONS.INSTRUCTION_WRITE,
  });
  const canGenerateReturn = presentationAllowsPermission({
    roleToken,
    user,
    permission: PRESENTATION_PERMISSIONS.RETURN_WRITE,
  });
  const canReadBilling = presentationAllowsPermission({
    roleToken,
    user,
    permission: PRESENTATION_PERMISSIONS.BILLING_READ,
  });
  const canReadInvoice = presentationAllowsPermission({
    roleToken,
    user,
    permission: PRESENTATION_PERMISSIONS.INVOICE_READ,
  });
  const canOpenFinance = canReadBilling || canReadInvoice;
  const [activeView, setActiveView] = useState(PRACTICE_WORKSPACE_VIEWS.COMMAND);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedMatterId, setSelectedMatterId] = useState(null);
  const [returnDrafts, setReturnDrafts] = useState({});
  const [returnStatus, setReturnStatus] = useState({});

  const matches = useCallback((row) => {
    const query = searchQuery.trim().toLowerCase();
    if (!query) return true;
    return Object.values(row).some(
      (value) => typeof value === 'string' && value.toLowerCase().includes(query),
    );
  }, [searchQuery]);

  const matters = (workspace.matters || []).filter(matches);
  const instructions = workspace.instructions.filter(matches);
  const documents = workspace.documents.filter(matches);
  const attempts = workspace.attempts.filter(matches);
  const executions = workspace.executions.filter(matches);
  const returns = workspace.returns.filter(matches);
  const returnedExecutionIds = useMemo(
    () => new Set(workspace.returns.map((item) => item.service_execution_id)),
    [workspace.returns],
  );

  const activeInstructions =
    workspace.summary.instructions_registered + workspace.summary.instructions_accepted;
  const activeAttempts =
    workspace.summary.attempts_allocated + workspace.summary.attempts_attempted;

  const chromeMetrics = [
    {
      id: 'matters',
      label: 'Open matters',
      value: workspace.summary.matters_open ?? matters.filter((item) => item.state === 'OPEN').length,
      detail: `${workspace.summary.matters_total ?? matters.length} canonical matters`,
    },
    {
      id: 'instructions',
      label: 'Active instructions',
      value: activeInstructions,
      detail: `${workspace.summary.instructions_total} total current instructions`,
    },
    {
      id: 'documents',
      label: 'Process documents',
      value: workspace.summary.documents_total,
      detail: `${workspace.summary.documents_received} received · ${workspace.summary.documents_allocated} allocated`,
    },
    {
      id: 'service',
      label: 'Active service work',
      value: activeAttempts,
      detail: `${workspace.summary.executions_total} certified executions`,
    },
  ];

  const navItems = [
    { id: PRACTICE_WORKSPACE_VIEWS.COMMAND, label: 'Command Center', icon: ClipboardList },
    { id: PRACTICE_WORKSPACE_VIEWS.MATTERS, label: 'Matters', icon: Scale },
    { id: PRACTICE_WORKSPACE_VIEWS.INSTRUCTIONS, label: 'Instructions', icon: Inbox },
    { id: PRACTICE_WORKSPACE_VIEWS.DOCUMENTS, label: 'Process Documents', icon: FileText },
    { id: PRACTICE_WORKSPACE_VIEWS.SERVICE, label: 'Service Operations', icon: Clock3 },
    { id: PRACTICE_WORKSPACE_VIEWS.RETURNS, label: 'Returns of Service', icon: FileCheck2 },
    ...(canOpenFinance ? [{ id: PRACTICE_WORKSPACE_VIEWS.FINANCE, label: 'Finance Evidence', icon: Landmark }] : []),
    ...(canIntake ? [{ id: PRACTICE_WORKSPACE_VIEWS.INTAKE, label: 'New Instruction', icon: FilePlus2 }] : []),
  ];

  const openMatter = (caseMatterId) => {
    setSelectedMatterId(caseMatterId);
    setActiveView(PRACTICE_WORKSPACE_VIEWS.MATTERS);
  };

  const handleRegisteredMatter = ({ caseMatterId, matterReference }) => {
    setSearchQuery(matterReference);
    setSelectedMatterId(caseMatterId);
    setActiveView(PRACTICE_WORKSPACE_VIEWS.MATTERS);
  };

  const runReturn = async (execution) => {
    const key = execution.service_execution_id;
    const draft = returnDrafts[key] || {
      executionId: key,
      executionEvidenceIdentity: execution.evidence_identity,
      returnId: `return-${createOpaqueBrowserToken()}`,
      generatedAt: new Date().toISOString(),
    };
    if (!returnDrafts[key]) {
      setReturnDrafts((current) => ({ ...current, [key]: draft }));
    }
    setReturnStatus((current) => ({
      ...current,
      [key]: { kind: 'pending', message: 'Generating governed return…' },
    }));
    try {
      const result = await generateLegalReturnOfService(draft);
      await onRefresh();
      setReturnStatus((current) => ({
        ...current,
        [key]: {
          kind: 'success',
          message: `Return ${result.returnId} generated from certified execution evidence.`,
        },
      }));
    } catch (caught) {
      setReturnStatus((current) => ({
        ...current,
        [key]: { kind: 'error', message: commandErrorMessage(caught) },
      }));
    }
  };

  const returnAction = (execution) => {
    if (!canGenerateReturn) return null;
    if (returnedExecutionIds.has(execution.service_execution_id)) {
      return <span className="text-[10px] font-black uppercase tracking-wider text-emerald-400">Return generated</span>;
    }
    const state = returnStatus[execution.service_execution_id];
    return (
      <div className="flex flex-col items-end gap-1">
        <button
          type="button"
          disabled={state?.kind === 'pending'}
          onClick={() => runReturn(execution)}
          className="inline-flex min-h-[40px] items-center gap-2 rounded-lg border border-emerald-800/40 bg-emerald-500/10 px-3 text-[11px] font-black text-emerald-300 disabled:opacity-40"
        >
          {state?.kind === 'pending' ? <Loader2 className="animate-spin" size={14} /> : <FileCheck2 size={14} />}
          Generate return
        </button>
        {state?.kind === 'error' && <span className="max-w-[240px] text-right text-[9px] text-red-400">{state.message}</span>}
        {state?.kind === 'success' && <span className="max-w-[240px] text-right text-[9px] text-emerald-400">{state.message}</span>}
      </div>
    );
  };

  let content = null;
  if (!error && activeView === PRACTICE_WORKSPACE_VIEWS.COMMAND) {
    content = (
      <div className="space-y-6">
        <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
          <QueueMetric icon={Inbox} label="Active instructions" value={activeInstructions} description="REGISTERED or ACCEPTED instruction truth." />
          <QueueMetric icon={FileText} label="Documents in flow" value={workspace.summary.documents_total} description="Current process-document lifecycle snapshots." />
          <QueueMetric icon={Clock3} label="Active attempts" value={activeAttempts} description="ALLOCATED or ATTEMPTED service work only." />
          <QueueMetric icon={FileCheck2} label="Returns generated" value={workspace.summary.returns_total} description="Generated ReturnOfService evidence; not invoice truth." />
        </section>
        <MatterOperationsPanel
          workspace={workspace}
          searchQuery={searchQuery}
          selectedMatterId={selectedMatterId}
          onSelectMatter={openMatter}
          overview
        />
        <QueuePanel
          title="Service operations"
          subtitle="Current service attempts requiring operational awareness"
          icon={Clock3}
          rows={attempts.slice(0, 6)}
          emptyMessage="No current service attempts match this view."
          renderRow={(item) => <PracticeLifecycleRow key={item.attempt_id} item={item} kind="attempt" />}
        />
      </div>
    );
  } else if (!error && activeView === PRACTICE_WORKSPACE_VIEWS.MATTERS) {
    content = (
      <MatterOperationsPanel
        workspace={workspace}
        searchQuery={searchQuery}
        selectedMatterId={selectedMatterId}
        onSelectMatter={setSelectedMatterId}
      />
    );
  } else if (!error && activeView === PRACTICE_WORKSPACE_VIEWS.INSTRUCTIONS) {
    content = (
      <QueuePanel
        title="Legal instructions"
        subtitle="Current canonical instruction state · registration is not receipt or service"
        icon={Inbox}
        rows={instructions}
        emptyMessage="No current instructions match this view."
        renderRow={(item) => <PracticeLifecycleRow key={item.instruction_id} item={item} kind="instruction" />}
      />
    );
  } else if (!error && activeView === PRACTICE_WORKSPACE_VIEWS.DOCUMENTS) {
    content = (
      <QueuePanel
        title="Process documents"
        subtitle="Current document state · custody and service remain separate evidence"
        icon={FileText}
        rows={documents}
        emptyMessage="No current process documents match this view."
        renderRow={(item) => <PracticeLifecycleRow key={item.document_id} item={item} kind="document" />}
      />
    );
  } else if (!error && activeView === PRACTICE_WORKSPACE_VIEWS.SERVICE) {
    content = (
      <div className="space-y-6">
        <QueuePanel
          title="Service attempts"
          subtitle="ATTEMPT is not SERVICE · current attempt truth"
          icon={Clock3}
          rows={attempts}
          emptyMessage="No current service attempts match this view."
          renderRow={(item) => <PracticeLifecycleRow key={item.attempt_id} item={item} kind="attempt" />}
        />
        <QueuePanel
          title="Certified service executions"
          subtitle="Explicit COMPLETED / NOT_COMPLETED service outcomes"
          icon={CheckCircle2}
          rows={executions}
          emptyMessage="No certified service executions match this view."
          renderRow={(item) => (
            <PracticeLifecycleRow
              key={item.service_execution_id}
              item={item}
              kind="execution"
              action={returnAction(item)}
            />
          )}
        />
      </div>
    );
  } else if (!error && activeView === PRACTICE_WORKSPACE_VIEWS.RETURNS) {
    content = (
      <QueuePanel
        title="Returns of Service"
        subtitle="Canonical generated returns · return is not tax invoice or payment"
        icon={FileCheck2}
        rows={returns}
        emptyMessage="No ReturnOfService evidence matches this view."
        renderRow={(item) => <PracticeLifecycleRow key={item.return_id} item={item} kind="return" />}
      />
    );
  } else if (!error && activeView === PRACTICE_WORKSPACE_VIEWS.FINANCE) {
    content = <LegalFinanceLookup roleToken={roleToken} user={user} />;
  } else if (!error && activeView === PRACTICE_WORKSPACE_VIEWS.INTAKE) {
    content = (
      <LegalIntakePanel
        onRefresh={onRefresh}
        onRegistered={handleRegisteredMatter}
        roleToken={roleToken}
        user={user}
      />
    );
  }

  const leftRail = (
    <nav aria-label="Legal practice workspace navigation">
      {navItems.map(({ id, label, icon: Icon }) => (
        <button
          key={id}
          type="button"
          data-active={activeView === id ? 'true' : 'false'}
          aria-current={activeView === id ? 'page' : undefined}
          onClick={() => setActiveView(id)}
          title={label}
        >
          <Icon size={16} />
          <span>{label}</span>
        </button>
      ))}
      {typeof onLogout === 'function' && (
        <button type="button" onClick={onLogout} title="Sign out">
          <LogOut size={16} />
          <span>Sign out</span>
        </button>
      )}
    </nav>
  );

  const tenant = {
    ...(tenantConfig || {}),
    tenantId: workspace.tenantId || tenantConfig?.tenantId || tenantConfig?.id || '',
  };
  const operator = {
    ...(user || {}),
    displayName: user?.displayName || user?.name || user?.email || 'Authenticated legal operator',
    role: roleToken || 'LEGAL_PRACTICE',
  };

  return (
    <WilsyOSDashboardChrome
      dashboardKey="legal-practice"
      commandLabel="WILSY Legal OS"
      title="Legal Operations Command Center"
      role={roleToken || 'LEGAL_PRACTICE'}
      posture={error ? 'SOURCE_GAPS' : 'LIVE'}
      tenant={tenant}
      operator={operator}
      storyMessages={[
        'Instruction → Document → Attempt → Service → Return',
        'Current canonical lifecycle truth',
        'Kennel EOS remains financial execution authority',
        'Permission hints may narrow presentation; Python EOS remains authorization authority',
      ]}
      search={{
        value: searchQuery,
        placeholder: 'Search matter reference, ID or linked legal work',
        onChange: (event) => {
          const value = event.target.value;
          setSearchQuery(value);
          setSelectedMatterId(null);
          if (value) setActiveView(PRACTICE_WORKSPACE_VIEWS.MATTERS);
        },
        onFocus: () => {
          if (searchQuery) setActiveView(PRACTICE_WORKSPACE_VIEWS.MATTERS);
        },
      }}
      actions={{
        liveSyncLabel: 'Refresh truth',
        onLiveSync: onRefresh,
        isRefreshing: refreshing,
        primaryActionLabel: canIntake ? 'New instruction' : 'Open instructions',
        onPrimaryAction: () => setActiveView(
          canIntake
            ? PRACTICE_WORKSPACE_VIEWS.INTAKE
            : PRACTICE_WORKSPACE_VIEWS.INSTRUCTIONS,
        ),
      }}
      metrics={chromeMetrics}
      leftRail={leftRail}
    >
      <div className="space-y-6">
        <WorkspaceErrorSurface error={error} />
        {content}
        <footer className="flex flex-col justify-between gap-3 border-t border-stone-900 py-5 text-[10px] uppercase tracking-[0.15em] text-stone-700 md:flex-row">
          <span>{DASHBOARD_VERSION}</span>
          <span>Python EOS owns legal truth · Kennel EOS owns financial execution</span>
        </footer>
      </div>
    </WilsyOSDashboardChrome>
  );
}

function LegalFinanceWorkspace({
  onLogout,
  roleView,
  tenantConfig,
  user,
}) {
  const roleToken = normalizeRoleToken(roleView);
  const tenant = {
    ...(tenantConfig || {}),
    tenantId: tenantConfig?.tenantId || tenantConfig?.id || '',
  };
  const operator = {
    ...(user || {}),
    displayName: user?.displayName || user?.name || user?.email || 'Authenticated legal finance operator',
    role: roleToken || 'LEGAL_FINANCE',
  };

  return (
    <WilsyOSDashboardChrome
      dashboardKey="legal-finance"
      commandLabel="WILSY Legal OS"
      title="Legal Finance Evidence"
      role={roleToken || 'LEGAL_FINANCE'}
      posture="LIVE"
      tenant={tenant}
      operator={operator}
      storyMessages={[
        'Tariff assessment ≠ billing eligibility',
        'Invoice ≠ payment execution',
        'Kennel EOS owns settlement',
      ]}
      metrics={[
        { id: 'lookup', label: 'Access mode', value: 'Exact ID', detail: 'No broad legal-workspace access' },
        { id: 'boundary', label: 'Execution authority', value: 'Kennel EOS', detail: 'Read-only finance evidence' },
      ]}
      leftRail={(
        <nav aria-label="Legal finance workspace navigation">
          <button type="button" data-active="true" aria-current="page" title="Finance Evidence">
            <Landmark size={16} />
            <span>Finance Evidence</span>
          </button>
          {typeof onLogout === 'function' && (
            <button type="button" onClick={onLogout} title="Sign out">
              <LogOut size={16} />
              <span>Sign out</span>
            </button>
          )}
        </nav>
      )}
    >
      <div className="space-y-6">
        <LegalFinanceLookup roleToken={roleToken} user={user} />
        <section className="rounded-2xl border border-stone-800 bg-stone-950/75 p-5">
          <div className="flex items-start gap-3">
            <ShieldCheck className="mt-0.5 text-emerald-400" size={20} />
            <div>
              <h2 className="text-sm font-black uppercase tracking-[0.12em] text-white">Finance authority boundary</h2>
              <p className="mt-2 max-w-4xl text-sm leading-6 text-stone-400">
                Legal Finance may verify exact tariff, billing-eligibility and invoice evidence. This surface cannot create service truth, execute payment, move money or mark settlement.
              </p>
            </div>
          </div>
        </section>
      </div>
    </WilsyOSDashboardChrome>
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
  user = null,
}) {
  const roleMode = useMemo(() => resolveRoleMode(roleView), [roleView]);
  const [queues, setQueues] = useState(EMPTY_QUEUES);
  const [deputyWork, setDeputyWork] = useState(EMPTY_DEPUTY_WORK);
  const [clientMatters, setClientMatters] = useState(EMPTY_CLIENT_MATTERS);
  const [practiceWorkspace, setPracticeWorkspace] = useState(
    EMPTY_PRACTICE_WORKSPACE,
  );
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
      setPracticeWorkspace(EMPTY_PRACTICE_WORKSPACE);
      setDeputyCapabilities(EMPTY_DEPUTY_CAPABILITIES);
      setError({
        kind: 'LEGAL_ROLE_SCOPE_REQUIRED',
        message:
          'This Legal OS surface requires a published Legal Practice, Legal Finance, SHERIFF, DEPUTY, or LEGAL_CLIENT presentation scope. No privileged endpoint was queried.',
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
        setPracticeWorkspace(EMPTY_PRACTICE_WORKSPACE);
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
        setPracticeWorkspace(EMPTY_PRACTICE_WORKSPACE);
        setLastUpdated(new Date());
        return { clientMatters: result };
      }

      if (roleMode === ROLE_MODES.LEGAL_PRACTICE) {
        const result = await getLegalPracticeWorkspace();
        setPracticeWorkspace(result);
        setQueues(EMPTY_QUEUES);
        setDeputyWork(EMPTY_DEPUTY_WORK);
        setClientMatters(EMPTY_CLIENT_MATTERS);
        setDeputyCapabilities(EMPTY_DEPUTY_CAPABILITIES);
        setCommandState(null);
        setObservationDrafts({});
        setLastUpdated(new Date());
        return { practiceWorkspace: result };
      }

      if (roleMode === ROLE_MODES.LEGAL_FINANCE) {
        setPracticeWorkspace(EMPTY_PRACTICE_WORKSPACE);
        setQueues(EMPTY_QUEUES);
        setDeputyWork(EMPTY_DEPUTY_WORK);
        setClientMatters(EMPTY_CLIENT_MATTERS);
        setDeputyCapabilities(EMPTY_DEPUTY_CAPABILITIES);
        setCommandState(null);
        setObservationDrafts({});
        setLastUpdated(new Date());
        return { legalFinance: true };
      }

      const result = await getSheriffOperationalQueues();
      setQueues(result);
      setDeputyWork(EMPTY_DEPUTY_WORK);
      setClientMatters(EMPTY_CLIENT_MATTERS);
      setPracticeWorkspace(EMPTY_PRACTICE_WORKSPACE);
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
      } else if (status === 403 && roleMode === ROLE_MODES.LEGAL_PRACTICE) {
        setError({
          kind: 'LEGAL_PRACTICE_WORKSPACE_DENIED',
          message:
            detail || 'The Legal Practice workspace requires current instruction, allocation, attempt and return read authority.',
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
          kind:
            roleMode === ROLE_MODES.LEGAL_PRACTICE
              ? 'LEGAL_PRACTICE_WORKSPACE_READ_FAILED'
              : 'QUEUE_READ_FAILED',
          message:
            caught?.message || 'Certified Legal Operations truth could not be loaded.',
        });
      }

      setQueues(EMPTY_QUEUES);
      setDeputyWork(EMPTY_DEPUTY_WORK);
      setClientMatters(EMPTY_CLIENT_MATTERS);
      setPracticeWorkspace(EMPTY_PRACTICE_WORKSPACE);
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

  const isPracticeMode = roleMode === ROLE_MODES.LEGAL_PRACTICE;
  const isFinanceMode = roleMode === ROLE_MODES.LEGAL_FINANCE;
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

  if (isPracticeMode) {
    return (
      <LegalPracticeWorkspace
        error={error}
        lastUpdated={lastUpdated}
        onLogout={onLogout}
        onRefresh={() => loadOperationalTruth({ refresh: true })}
        refreshing={refreshing}
        roleView={roleView}
        tenantConfig={tenantConfig}
        user={user}
        workspace={practiceWorkspace}
      />
    );
  }

  if (isFinanceMode) {
    return (
      <LegalFinanceWorkspace
        onLogout={onLogout}
        roleView={roleView}
        tenantConfig={tenantConfig}
        user={user}
      />
    );
  }

  if (isClientMode) {
    return (
      <LegalClientWorkspace
        clientMatters={clientMatters}
        error={error}
        lastUpdated={lastUpdated}
        metrics={metrics}
        onLogout={onLogout}
        onRefresh={() => loadOperationalTruth({ refresh: true })}
        refreshing={refreshing}
        tenantConfig={tenantConfig}
        user={user}
      />
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
 * VERSION: v11.1.0-L8-7D16-PERMISSION-AWARE-LEGAL-COMMAND-CENTER
 * AUTHORITY BOUNDARY: governed Legal Practice/Finance/SHERIFF/DEPUTY/LEGAL_CLIENT presentation plus already-authorized intake, ReturnOfService and bound-Deputy command initiation only; canonical role is the maximum browser presentation envelope, explicit legal permission hints may only narrow it, and Python EOS owns authority and legal truth
 * TENANT POSTURE: every data surface remains server-authorized and tenant-scoped; practice workspace is D15 snapshot truth with first-class CaseMatter evidence, client matters are D5/D7 visibility-bound, deputy commands require exact capability parity
 * FAIL-CLOSED POSTURE: unresolved role, explicit legal-permission narrowing, denied/unavailable workspace/client/specialist read, malformed finance/intake/return/field evidence, command failure or failed refresh never invents truth, widens role scope or cross-role fallback
 * FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
