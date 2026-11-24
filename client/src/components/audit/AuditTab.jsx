/**
 * TITLE: WILSY OS Authenticated Billing Audit Workspace
 * VERSION: v36.0.0-EOS-AUTHENTICATED-PERSISTED-AUDIT-READONLY
 * AUTHORITY: Wilsy OS Core Governance
 * EPITOME: Presents tenant-scoped persisted billing audit events and truthful
 *          integrity-control posture through authenticated Python EOS reads.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/components/audit/AuditTab.jsx
 * COLLABORATION / OWNERSHIP: BillingHUD supplies a display tenant candidate;
 *                            TenantContext and Python EOS authorization bind scope.
 * CERTIFICATION / UPDATE DATE: 2026-11-10
 * CHANGELOG:
 *   v36.0.0-EOS-AUTHENTICATED-PERSISTED-AUDIT-READONLY replaces the retired
 *     unauthenticated audit URL and WebSocket with authenticated persisted EOS
 *     reads; integrity controls are visible read-only and never use UI defaults.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
 * SECURITY / PRIVACY POSTURE: No mock audit rows, hardcoded tenant, WebSocket
 *                             stream, or editable integrity control is presented.
 * TENANT BOUNDARY: Requests use only TenantContext's authenticated current tenant;
 *                  mismatched external display props fail closed before transport.
 * AUTHORITY BOUNDARY: Audit visibility is read-only; no integrity-control write
 *                     authority or access-revocation operation is implied.
 * FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution
 *                               and settlement truth.
 */

import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import {
  AlertTriangle,
  CheckCircle,
  CircleDashed,
  FileText,
  Lock,
  Scan,
  Server,
  ShieldCheck,
} from 'lucide-react';
import { useTenants } from '../../contexts/tenantContext';
import sovereignClient from '../../utils/sovereignClient';

const tenantIdentifier = (tenant) => String(
  tenant?.tenant_id || tenant?.tenantId || tenant?.id || tenant?._id || '',
).trim();

const safeText = (value, fallback = 'Not supplied') => (
  typeof value === 'string' && value.trim() ? value.trim() : fallback
);

const shortenReference = (value) => (
  typeof value === 'string' && value.length > 24
    ? `${value.slice(0, 12)}…${value.slice(-8)}`
    : value || 'No proof reference'
);

const normalizeAuditEvent = (row, index) => {
  const metadata = row?.metadata && typeof row.metadata === 'object' ? row.metadata : {};
  const valid = typeof row?.valid === 'boolean'
    ? row.valid
    : typeof metadata.valid === 'boolean'
      ? metadata.valid
      : null;
  const createdAt = row?.created_at || row?.createdAt || row?.timestamp;
  const reference = row?.proof_hash || row?.proofHash || row?.seal_hash || row?.sealHash || '';
  const identity = row?._id || row?.event_id || row?.eventId || reference;

  return {
    id: String(identity || `${row?.event_type || row?.eventType || 'AUDIT_EVENT'}:${createdAt || index}`),
    action: safeText(row?.event_type || row?.eventType || row?.action, 'BILLING_AUDIT_EVENT'),
    timestamp: createdAt ? new Date(createdAt).toLocaleString() : 'Timestamp unavailable',
    entity: safeText(row?.invoice_id || row?.invoiceId || row?.resource_id || row?.resourceId, 'Billing evidence'),
    reference,
    result: valid === true ? 'matched' : valid === false ? 'missing' : 'recorded',
  };
};

const errorMessage = (error, fallback) => (
  error?.response?.data?.detail || error?.response?.data?.message || error?.message || fallback
);

/**
 * @description Renders a current-tenant audit snapshot and read-only controls.
 * @collaboration BillingHUD mounts the tab; TenantContext supplies the
 *                authenticated workspace projection; Python EOS owns audit reads.
 * @institutional Keeps persisted audit truth separate from unbacked WebSocket,
 *                 anomaly, revocation, and integrity-write claims.
 * @param {{externalTenantId?: string|null}} props - Display candidate checked
 *        against the authenticated current workspace; it never sets authority.
 * @returns {JSX.Element} Authenticated persisted audit rows and explicit source states.
 * @throws Never converts missing or mismatched tenant state into an API request.
 */
export const AuditTab = ({ externalTenantId = null }) => {
  const { activeTenant, bootstrapReady, authorityMismatch } = useTenants();
  const authenticatedTenantId = tenantIdentifier(activeTenant);
  const suppliedTenantId = typeof externalTenantId === 'string' ? externalTenantId.trim() : '';
  const tenantMismatch = Boolean(
    suppliedTenantId && authenticatedTenantId && suppliedTenantId !== authenticatedTenantId,
  );
  const tenantId = tenantMismatch ? '' : authenticatedTenantId;

  const [events, setEvents] = useState([]);
  const [integrity, setIntegrity] = useState(null);
  const [activeFilter, setActiveFilter] = useState('all');
  const [requestState, setRequestState] = useState('INITIALIZING');
  const [auditError, setAuditError] = useState('');
  const [integrityError, setIntegrityError] = useState('');
  const [lastLoadedAt, setLastLoadedAt] = useState(null);
  const requestSequence = useRef(0);

  const loadPersistedSnapshot = useCallback(async () => {
    if (!bootstrapReady || authorityMismatch || tenantMismatch || !tenantId) {
      setRequestState(tenantMismatch || authorityMismatch
        ? 'AUTHENTICATED_TENANT_CONTEXT_MISMATCH'
        : 'AUTHENTICATED_TENANT_UNAVAILABLE');
      setEvents([]);
      setIntegrity(null);
      return;
    }

    const sequence = requestSequence.current + 1;
    requestSequence.current = sequence;
    const controller = new AbortController();
    setRequestState('LOADING_PERSISTED_EOS_SNAPSHOT');
    setAuditError('');
    setIntegrityError('');

    const requestOptions = {
      headers: { 'X-Tenant-ID': tenantId },
      signal: controller.signal,
    };

    const [eventsResult, integrityResult] = await Promise.allSettled([
      sovereignClient.get('/billing/audit/events', {
        ...requestOptions,
        params: { limit: 100 },
      }),
      sovereignClient.get('/billing/audit/integrity', requestOptions),
    ]);

    if (requestSequence.current !== sequence) return;

    if (eventsResult.status === 'fulfilled') {
      const payload = eventsResult.value?.data;
      setEvents(Array.isArray(payload) ? payload.map(normalizeAuditEvent) : []);
      setRequestState('PERSISTED_EOS_SNAPSHOT');
      setLastLoadedAt(new Date());
    } else {
      setEvents([]);
      setRequestState('PERSISTED_EOS_UNAVAILABLE');
      if (eventsResult.reason?.name !== 'AbortError') {
        setAuditError(errorMessage(eventsResult.reason, 'Authenticated billing audit is unavailable.'));
      }
    }

    if (integrityResult.status === 'fulfilled') {
      const payload = integrityResult.value?.data;
      setIntegrity(payload && typeof payload === 'object' ? payload : null);
    } else {
      setIntegrity(null);
      if (integrityResult.reason?.name !== 'AbortError') {
        setIntegrityError(errorMessage(integrityResult.reason, 'Read-only integrity posture is unavailable.'));
      }
    }
  }, [activeTenant, authorityMismatch, bootstrapReady, tenantId, tenantMismatch]);

  useEffect(() => {
    void loadPersistedSnapshot();
    if (!tenantId || tenantMismatch || authorityMismatch) return undefined;
    const intervalId = window.setInterval(() => {
      void loadPersistedSnapshot();
    }, 30000);
    return () => {
      window.clearInterval(intervalId);
      requestSequence.current += 1;
    };
  }, [authorityMismatch, loadPersistedSnapshot, tenantId, tenantMismatch]);

  const filteredEvents = useMemo(() => {
    if (activeFilter === 'all') return events;
    return events.filter((event) => event.result === activeFilter);
  }, [activeFilter, events]);

  const controls = [
    ['auto_renew', 'Auto renew'],
    ['encrypted_backup', 'Encrypted backup'],
    ['neural_sync', 'Neural sync'],
  ];

  const displayedError = tenantMismatch
    ? 'The supplied display tenant does not match the authenticated workspace.'
    : authorityMismatch
      ? 'Python EOS reports an authenticated workspace authority mismatch.'
      : auditError;

  return (
    <main className="flex h-full w-full bg-slate-950 text-slate-200 p-6 overflow-auto font-sans" aria-labelledby="audit-heading">
      <div className="w-full max-w-7xl mx-auto space-y-6">
        <header className="flex flex-col sm:flex-row justify-between items-start sm:items-center border-b border-slate-800 pb-4 gap-4">
          <div>
            <div className="flex items-center gap-3">
              <h1 id="audit-heading" className="text-2xl font-semibold text-slate-100 tracking-tight flex items-center gap-2">
                <ShieldCheck className="text-cyan-400" size={24} /> Billing audit trail
              </h1>
              <span
                className="rounded-full border border-slate-700 bg-slate-800/60 px-2 py-1 text-[10px] text-cyan-300"
                data-testid="audit-source-state"
              >
                {requestState}
              </span>
            </div>
            <p className="text-sm text-slate-400 mt-1 flex items-center gap-2">
              <Server className="w-4 h-4" />
              {tenantId ? `Authenticated tenant ${tenantId}` : 'Authenticated tenant unavailable'}
            </p>
          </div>
          <div className="flex gap-3">
            <button
              type="button"
              onClick={() => void loadPersistedSnapshot()}
              className="flex items-center gap-2 bg-slate-800 hover:bg-slate-700 border border-slate-700 px-4 py-2 rounded-lg text-xs font-medium text-slate-300"
              disabled={!tenantId || tenantMismatch || authorityMismatch}
            >
              <Scan size={16} /> Refresh snapshot
            </button>
            <button
              type="button"
              onClick={() => window.print()}
              className="flex items-center gap-2 bg-amber-600/20 hover:bg-amber-600/30 border border-amber-500/30 px-4 py-2 rounded-lg text-xs font-medium text-amber-300"
            >
              <FileText size={16} /> Print snapshot
            </button>
          </div>
        </header>

        {displayedError && (
          <div role="alert" className="flex items-start gap-3 rounded-lg border border-amber-700/50 bg-amber-950/20 p-4 text-sm text-amber-200" data-testid="audit-error">
            <AlertTriangle size={18} aria-hidden="true" />
            <span>{displayedError}</span>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          <section className="lg:col-span-3 bg-slate-900/60 border border-slate-800/60 rounded-xl overflow-hidden" aria-label="Persisted billing audit events">
            <div className="p-4 border-b border-slate-800 flex justify-between items-center bg-slate-900/80">
              <div className="flex gap-1 rounded-lg bg-slate-800 p-1" role="group" aria-label="Audit event filter">
                {[
                  ['all', 'All'],
                  ['matched', 'Matched'],
                  ['missing', 'Not matched'],
                ].map(([filter, label]) => (
                  <button
                    key={filter}
                    type="button"
                    aria-pressed={activeFilter === filter}
                    onClick={() => setActiveFilter(filter)}
                    className={`px-3 py-1 text-[10px] uppercase tracking-wider font-bold rounded-md ${activeFilter === filter ? 'bg-cyan-500/20 text-cyan-300' : 'text-slate-500 hover:text-slate-300'}`}
                  >
                    {label}
                  </button>
                ))}
              </div>
              <span className="text-[10px] text-slate-500 font-mono">SOURCE: PYTHON EOS PERSISTED EVENTS</span>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead className="bg-slate-900/40 text-slate-400 text-[11px] uppercase tracking-wider">
                  <tr>
                    <th className="p-4 font-medium">Event</th>
                    <th className="p-4 font-medium">Timestamp</th>
                    <th className="p-4 font-medium">Source record</th>
                    <th className="p-4 font-medium">Persisted proof reference</th>
                    <th className="p-4 font-medium text-right">Observation</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/80">
                  {filteredEvents.length === 0 ? (
                    <tr>
                      <td colSpan="5" className="p-8 text-center text-sm text-slate-500">
                        {displayedError || 'No persisted billing audit events are available for this tenant.'}
                      </td>
                    </tr>
                  ) : filteredEvents.map((event) => (
                    <tr key={event.id} className="hover:bg-slate-800/50">
                      <td className="p-4 whitespace-nowrap">
                        <span className="text-slate-200 font-medium">{event.action}</span>
                      </td>
                      <td className="p-4 whitespace-nowrap text-slate-400 font-mono text-xs">{event.timestamp}</td>
                      <td className="p-4 whitespace-nowrap text-slate-300 text-xs">{event.entity}</td>
                      <td className="p-4 whitespace-nowrap font-mono text-xs text-slate-500">
                        <span className="inline-flex items-center gap-2"><Lock size={12} />{shortenReference(event.reference)}</span>
                      </td>
                      <td className="p-4 whitespace-nowrap text-right">
                        <span className="inline-flex items-center gap-1.5 rounded-full border border-slate-700 px-2 py-1 text-[10px] uppercase">
                          {event.result === 'matched' ? <CheckCircle size={12} className="text-emerald-400" /> : <CircleDashed size={12} className="text-slate-400" />}
                          {event.result === 'matched' ? 'Reference matched' : event.result === 'missing' ? 'Reference missing' : 'Recorded'}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <footer className="p-4 border-t border-slate-800 text-[10px] text-slate-500 flex justify-between font-mono">
              <span>{filteredEvents.length} of {events.length} persisted events{tenantId ? ` · tenant ${tenantId}` : ''}</span>
              <span>{lastLoadedAt ? `Last refreshed ${lastLoadedAt.toLocaleTimeString()}` : 'Refresh time unavailable'} · 30 second polling</span>
            </footer>
          </section>

          <aside className="space-y-6" aria-label="Read-only audit posture">
            <section className="bg-slate-900/60 border border-slate-800/60 rounded-xl p-5 space-y-3">
              <h2 className="text-sm font-semibold text-slate-300">Anomaly feed</h2>
              <p className="text-xs text-slate-400" data-testid="audit-anomaly-posture">
                No authenticated Python EOS anomaly feed is mounted on this surface. No live anomaly state is inferred.
              </p>
            </section>

            <section className="bg-slate-900/60 border border-slate-800/60 rounded-xl p-5 space-y-4" aria-labelledby="integrity-heading">
              <div>
                <h2 id="integrity-heading" className="text-sm font-semibold text-slate-300">System integrity posture</h2>
                <p className="mt-1 text-xs text-slate-500">Read-only. No governed Python EOS write capability is established.</p>
              </div>
              {integrityError && <p role="status" className="text-xs text-amber-300" data-testid="audit-integrity-error">{integrityError}</p>}
              {controls.map(([key, label]) => {
                const value = integrity?.[key];
                return (
                  <div key={key} className="flex justify-between items-center gap-3 border-b border-slate-800 pb-2 text-xs">
                    <span className="text-slate-400">{label}</span>
                    <span className="text-slate-300" data-testid={`integrity-${key}`}>
                      {typeof value === 'boolean' ? (value ? 'Enabled' : 'Disabled') : 'Unavailable'}
                    </span>
                  </div>
                );
              })}
              <p className="text-[10px] text-slate-500" data-testid="audit-integrity-source">
                Source: {safeText(integrity?.source, integrity ? 'Persisted EOS value' : 'Unavailable')}
              </p>
            </section>

            <p className="text-[10px] text-slate-600">Audit visibility does not authorize tenant suspension, access revocation, payment, execution, or settlement.</p>
          </aside>
        </div>
      </div>
    </main>
  );
};

/**
 * ARTIFACT: WILSY OS Authenticated Billing Audit Workspace
 * VERSION: v36.0.0-EOS-AUTHENTICATED-PERSISTED-AUDIT-READONLY
 * AUTHORITY BOUNDARY: Authenticated tenant audit reads only; no control or revocation writes.
 * TENANT POSTURE: Current TenantContext projection is required; mismatch fails closed.
 * FAIL-CLOSED POSTURE: Missing event/control sources remain unavailable, never mocked.
 * FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
