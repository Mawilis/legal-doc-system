import React from 'react';

const CAPABILITIES = Object.freeze({
  overview: 'system_services:queue:read',
  cases: 'system_services:queue:read',
  identity: 'system_services:identity:read',
  recovery: 'system_services:recovery:request',
  incidents: 'system_services:queue:read',
  responder: 'system_services:incident:escalate',
  accessRequests: 'iam:access_request:read',
  assignments: 'iam:role_assignment:read',
  audit: 'system_services:audit:read',
});

const styles = {
  page: { minHeight: '100%', padding: 'clamp(20px, 3vw, 36px)', color: '#e9edf5', background: '#080d18', fontFamily: 'Inter, system-ui, sans-serif' },
  eyebrow: { color: '#8ea5c8', fontSize: 11, letterSpacing: '0.16em', textTransform: 'uppercase' },
  title: { margin: '8px 0', fontSize: 'clamp(25px, 3vw, 36px)', fontWeight: 700, letterSpacing: '-0.035em' },
  muted: { color: '#9aa8bd', lineHeight: 1.55 },
  grid: { display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(230px, 1fr))', gap: 14, marginTop: 24 },
  card: { background: '#111a2a', border: '1px solid #26354b', borderRadius: 14, padding: 18 },
  label: { color: '#9aa8bd', fontSize: 12, letterSpacing: '0.08em', textTransform: 'uppercase' },
  value: { marginTop: 9, fontSize: 27, fontWeight: 700, fontVariantNumeric: 'tabular-nums' },
  section: { marginTop: 28 },
  sectionTitle: { margin: '0 0 12px', fontSize: 17, fontWeight: 650 },
  pill: { display: 'inline-flex', padding: '5px 9px', borderRadius: 999, border: '1px solid #34465f', color: '#b9c7da', fontSize: 11, letterSpacing: '0.04em' },
  row: { display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 12, padding: '13px 0', borderBottom: '1px solid #26354b' },
  empty: { padding: 18, border: '1px dashed #40516a', borderRadius: 12, color: '#a9b6c9', background: '#0d1523' },
};

function hasCapability(workspace, capability) {
  return Array.isArray(workspace?.capabilities) && workspace.capabilities.includes(capability);
}

function sourceValue(value) {
  return value === null || value === undefined ? '—' : String(value);
}

/**
 * Presentation-only System Services console.
 * All workspace, metrics, cases and capability decisions must be supplied by
 * the authenticated EOS workspace-bootstrap projection. This component does
 * not infer authority from role labels or make direct API calls.
 */
export default function SystemServicesDashboard({ workspace = null, incidents = [], assignments = [], assignmentDetail = null, actionState = '', onOpenAssignment, onDecideAssignment }) {
  const ready = workspace?.status === 'READY'
    && workspace?.authority === 'EOS_SYSTEM_SERVICES'
    && typeof workspace?.principalId === 'string'
    && workspace.principalId.length > 0;

  if (!ready) {
    return (
      <main style={styles.page} aria-labelledby="system-services-title">
        <div style={styles.eyebrow}>WILSY OS · PLATFORM OPERATIONS</div>
        <h1 id="system-services-title" style={styles.title}>System Services</h1>
        <p style={styles.muted}>Account support, recovery operations and identity governance.</p>
        <div role="status" style={{ ...styles.empty, marginTop: 24 }}>
          <strong>EOS workspace projection unavailable.</strong>
          <p style={{ margin: '8px 0 0' }}>This console remains closed until EOS verifies current System Services authority. No account data, case counts or administrative actions are exposed.</p>
        </div>
      </main>
    );
  }

  const summary = workspace.summary && typeof workspace.summary === 'object' ? workspace.summary : {};
  const sections = [
    ['Support queue', CAPABILITIES.cases, 'cases'],
    ['Account security', CAPABILITIES.identity, 'identity'],
    ['Recovery operations', CAPABILITIES.recovery, 'recovery'],
    ['Access requests', CAPABILITIES.accessRequests, 'accessRequests'],
    ['Role assignments', CAPABILITIES.assignments, 'assignments'],
    ['Audit evidence', CAPABILITIES.audit, 'audit'],
  ];

  return (
    <main style={styles.page} aria-labelledby="system-services-title">
      <div style={styles.eyebrow}>WILSY OS · PLATFORM OPERATIONS</div>
      <h1 id="system-services-title" style={styles.title}>System Services</h1>
      <p style={styles.muted}>EOS-governed account support, security recovery and identity access management.</p>
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, marginTop: 14 }}>
        <span style={styles.pill}>EOS authority verified</span>
        <span style={styles.pill}>Principal {workspace.principalId}</span>
        <span style={styles.pill}>Scope {sourceValue(workspace.scope || 'SYSTEM')}</span>
      </div>

      {hasCapability(workspace, CAPABILITIES.overview) && (
        <section style={styles.grid} aria-label="System Services overview">
          {[
            ['Open cases', summary.openCases],
            ['Security escalations', summary.securityEscalations],
            ['Recovery pending', summary.recoveryPending],
            ['Access reviews pending', summary.accessReviewsPending],
          ].map(([label, value]) => (
            <article key={label} style={styles.card}>
              <div style={styles.label}>{label}</div>
              <div style={styles.value}>{sourceValue(value)}</div>
            </article>
          ))}
        </section>
      )}

      <section style={styles.section} aria-labelledby="services-sections-title">
        <h2 id="services-sections-title" style={styles.sectionTitle}>Authorized work areas</h2>
        <div style={styles.card}>
          {sections.filter(([, capability]) => hasCapability(workspace, capability)).map(([label, , key]) => (
            <div key={key} style={styles.row}>
              <span>{label}</span>
              <span style={styles.pill}>EOS capability present</span>
            </div>
          ))}
          {sections.every(([, capability]) => !hasCapability(workspace, capability)) && (
            <div style={styles.empty}>No System Services work areas are currently authorized for this principal.</div>
          )}
        </div>
      </section>

      {hasCapability(workspace, CAPABILITIES.cases) && (
        <section style={styles.section} aria-labelledby="cases-title">
          <h2 id="cases-title" style={styles.sectionTitle}>Support cases</h2>
          {Array.isArray(workspace.cases) && workspace.cases.length > 0 ? (
            <div style={styles.card}>
              {workspace.cases.map((item) => (
                <div key={item.caseId} style={styles.row}>
                  <span>
                    <strong>{sourceValue(item.reference)}</strong>
                    <span style={{ display: 'block', ...styles.muted }}>{sourceValue(item.category)}</span>
                  </span>
                  <span style={styles.pill}>{sourceValue(item.status)}</span>
                </div>
              ))}
            </div>
          ) : (
            <div style={styles.empty}>No case records were supplied by EOS. An empty response is not treated as an operational metric.</div>
          )}
        </section>
      )}


      {hasCapability(workspace, CAPABILITIES.cases) && (
        <section style={styles.section} aria-labelledby="incidents-title">
          <h2 id="incidents-title" style={styles.sectionTitle}>Security incident queue</h2>
          {incidents.length > 0 ? (
            <div style={styles.card}>
              {incidents.map((incident) => (
                <div key={incident.incidentId} style={styles.row}>
                  <span>
                    <strong>{sourceValue(incident.category)}</strong>
                    <span style={{ display: 'block', ...styles.muted }}>
                      {sourceValue(incident.incidentId)} · observed {sourceValue(incident.observedAt)}
                    </span>
                  </span>
                  <span style={styles.pill}>{sourceValue(incident.status)}</span>
                </div>
              ))}
            </div>
          ) : (
            <div style={styles.empty}>No security incidents were returned by the authenticated EOS queue.</div>
          )}
        </section>
      )}

      {hasCapability(workspace, 'system_services:incident:escalate') && (
        <section style={styles.section} aria-labelledby="responder-inbox-title">
          <h2 id="responder-inbox-title" style={styles.sectionTitle}>My responder assignments</h2>
          {assignments.length > 0 ? (
            <div style={styles.card}>
              {assignments.map((assignment) => (
                <div key={assignment.assignmentId} style={styles.row}>
                  <span>
                    <strong>{sourceValue(assignment.incidentId)}</strong>
                    <span style={{ display: 'block', ...styles.muted }}>
                      {sourceValue(assignment.assignmentId)} · revision {sourceValue(assignment.revision)}
                    </span>
                  </span>
                  <span style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
                    <span style={styles.pill}>{sourceValue(assignment.status)}</span>
                    <button type="button" onClick={() => onOpenAssignment?.(assignment.assignmentId)}>
                      View incident
                    </button>
                    {assignment.status === 'PENDING_ACCEPTANCE' && (
                      <>
                        <button type="button" onClick={() => onDecideAssignment?.(assignment.assignmentId, 'accept')}>
                          Accept
                        </button>
                        <button type="button" onClick={() => onDecideAssignment?.(assignment.assignmentId, 'decline')}>
                          Decline
                        </button>
                      </>
                    )}
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <div style={styles.empty}>No responder assignments are currently addressed to this principal.</div>
          )}
          {assignmentDetail && (
            <div style={{ ...styles.card, marginTop: 12 }} aria-label="Selected responder incident detail">
              <h3 style={{ marginTop: 0 }}>Incident detail</h3>
              <p style={styles.muted}>Assignment {sourceValue(assignmentDetail.assignment?.assignmentId)}</p>
              <p>Category: {sourceValue(assignmentDetail.incident?.category)}</p>
              <p>Status: {sourceValue(assignmentDetail.incident?.status)}</p>
              <p>Observed: {sourceValue(assignmentDetail.incident?.observedAt)}</p>
            </div>
          )}
          {actionState && <p role="status" style={styles.muted}>{actionState}</p>}
        </section>
      )}

      <p style={{ ...styles.muted, marginTop: 28, fontSize: 12 }}>
        Read and command APIs remain authoritative. This screen never grants roles, resets credentials, unlocks accounts or changes sessions by itself.
      </p>
    </main>
  );
}

export { CAPABILITIES as SYSTEM_SERVICES_CAPABILITIES, hasCapability as hasSystemServicesCapability };
