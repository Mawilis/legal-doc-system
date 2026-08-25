// ============================================================================
// WILSY OS – AUDIT TAB UI
// Version: 1.1.0-AUDIT-WEBSOCKET-AI
// Authority: Wilsy OS Core Governance
// Epitome: Forensic audit cockpit with live WebSocket stream, EOS kennel
//          intelligence, blockchain anchoring, and AI reasoning tooltips.
//          Uses the sovereign api service and WebSocket for real‑time updates.
// Kernel Awareness: All backend calls go through api.js; WebSocket connects
//                   to /api/audit/stream for live EOS intelligence.
// Collaboration: Wilson Khanyezi (architect), Wilsy OS Core Team.
// ============================================================================

import React, { useEffect, useState, useRef } from 'react';
import api from '../../services/api';
import styles from './AuditTab.module.css';

const AuditTab = () => {
  const [events, setEvents] = useState([]);
  const [status, setStatus] = useState('');
  const [filter, setFilter] = useState('all');
  const [complianceScore, setComplianceScore] = useState(0);
  const [loading, setLoading] = useState(false);
  const [toast, setToast] = useState(null);
  const wsRef = useRef(null);

  // ─── Toast notifications ─────────────────────────────────────────────
  const showToast = (message, type = 'info') => {
    setToast({ message, type });
    setTimeout(() => setToast(null), 5000);
  };

  // ─── WebSocket live stream ───────────────────────────────────────────
  useEffect(() => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/api/audit/stream`;
    wsRef.current = new WebSocket(wsUrl);

    wsRef.current.onopen = () => {
      console.log('[AuditTab] WebSocket connected');
      showToast('Audit stream live', 'success');
    };

    wsRef.current.onmessage = (msg) => {
      try {
        const payload = JSON.parse(msg.data);
        if (payload.type === 'init') {
          setEvents(payload.events || []);
        } else if (payload.type === 'event') {
          setEvents(prev => [payload.data, ...prev]);
        } else if (payload.type === 'aiDecision') {
          const aiEvent = {
            entityType: 'AI Agent',
            action: 'decision',
            metadata: {
              aiDecision: payload.data.action || 'decision',
              reason: payload.data.reason || '',
              reasoning: payload.data.reasoning || '',
              agent: payload.data.agent || 'EOS Kennel',
            },
            timestamp: new Date().toISOString(),
          };
          setEvents(prev => [aiEvent, ...prev]);
        } else if (payload.type === 'error') {
          showToast(payload.message, 'error');
        }
      } catch (err) {
        console.error('[AuditTab] WebSocket parse error:', err);
      }
    };

    wsRef.current.onerror = (err) => {
      console.error('[AuditTab] WebSocket error:', err);
      showToast('Audit stream disconnected', 'error');
    };

    wsRef.current.onclose = () => {
      console.warn('[AuditTab] WebSocket closed');
      // Attempt reconnect after 5s
      setTimeout(() => {
        if (wsRef.current?.readyState !== WebSocket.OPEN) {
          // Reconnect logic could be implemented here
        }
      }, 5000);
    };

    return () => {
      if (wsRef.current) wsRef.current.close();
    };
  }, []);

  // ─── Fetch events (fallback / manual refresh) ──────────────────────
  const fetchEvents = async () => {
    setLoading(true);
    setStatus('Loading audit events...');
    try {
      const response = await api.get('/audit');
      const data = response.data || [];
      setEvents(Array.isArray(data) ? data : data.events || []);
      setStatus('Audit events loaded');
      showToast('Events refreshed', 'success');
    } catch (err) {
      console.error('[AuditTab] fetch error:', err);
      setStatus(`Error: ${err.message}`);
      showToast(`Error: ${err.message}`, 'error');
    } finally {
      setLoading(false);
    }
  };

  // ─── Compute compliance readiness ───────────────────────────────────
  useEffect(() => {
    const verified = events.filter(e => e.action === 'seal' && e.sealHash).length;
    const total = events.length || 1;
    setComplianceScore(Math.round((verified / total) * 100));
  }, [events]);

  // ─── Chain verification ─────────────────────────────────────────────
  const handleVerifyChain = async (statementId) => {
    setLoading(true);
    setStatus('Verifying chain anchor...');
    try {
      const response = await api.post('/audit/verifyChain', { statementId });
      const result = response.data;
      if (result.valid) {
        showToast(`✅ Chain anchored – TX: ${result.chainTxId?.slice(0, 10)}…`, 'success');
      } else {
        showToast('❌ Unverified – seal not anchored', 'error');
      }
      await fetchEvents();
    } catch (err) {
      console.error('[AuditTab] verifyChain error:', err);
      showToast(`Error: ${err.message}`, 'error');
    } finally {
      setLoading(false);
    }
  };

  // ─── Evidence packet ────────────────────────────────────────────────
  const handleEvidencePacket = async (statementId) => {
    setLoading(true);
    setStatus('Generating evidence packet...');
    try {
      const response = await api.post('/audit/evidencePacket', { statementId });
      const result = response.data;
      showToast(`Packet generated: ${result.filePath}`, 'success');
      if (result.packet) {
        const blob = new Blob([JSON.stringify(result.packet, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `evidence-${statementId}.json`;
        a.click();
        URL.revokeObjectURL(url);
      }
      await fetchEvents();
    } catch (err) {
      console.error('[AuditTab] evidencePacket error:', err);
      showToast(`Error: ${err.message}`, 'error');
    } finally {
      setLoading(false);
    }
  };

  // ─── Filters & helpers ──────────────────────────────────────────────
  const filteredEvents = filter === 'all' ? events : events.filter(e => e.action === filter);

  const getBadge = (event) => {
    if (event.metadata?.chainTxId) return '⛓️ ANCHORED';
    if (event.metadata?.aiDecision) return '🧠 AI';
    if (event.action === 'seal' && event.sealHash) return '🔗 SEALED';
    return '📋';
  };

  const getTooltip = (event) => {
    if (event.metadata?.reasoning) return event.metadata.reasoning;
    if (event.metadata?.reason) return event.metadata.reason;
    if (event.metadata?.aiDecision) return `AI decision: ${event.metadata.aiDecision}`;
    return null;
  };

  // ─── Render ──────────────────────────────────────────────────────────
  return (
    <div className={styles.auditShell}>
      {toast && (
        <div className={`${styles.toast} ${styles[toast.type]}`}>
          {toast.message}
        </div>
      )}

      <div className={styles.header}>
        <h2>🔐 Audit Trail</h2>
        <p className={styles.subtitle}>
          Immutable forensic ledger with live EOS intelligence & blockchain anchoring.
        </p>
      </div>

      <div className={styles.controls}>
        <select
          value={filter}
          onChange={e => setFilter(e.target.value)}
          className={styles.filterSelect}
        >
          <option value="all">All Actions</option>
          <option value="create">Create</option>
          <option value="seal">Seal</option>
          <option value="export">Export</option>
          <option value="verify">Verify</option>
          <option value="verifyChain">Chain Verify</option>
          <option value="evidencePacket">Evidence Packet</option>
          <option value="decision">AI Decision</option>
        </select>
        <button
          onClick={fetchEvents}
          disabled={loading}
          className={styles.refreshButton}
        >
          {loading ? 'Loading…' : 'Refresh'}
        </button>
        <span className={styles.liveBadge}>🔴 LIVE</span>
      </div>

      <div className={styles.dashboard}>
        <div className={styles.metric}>
          <h3>Compliance Readiness</h3>
          <p>{complianceScore}%</p>
          <small>Based on sealed events</small>
        </div>
        <div className={styles.metric}>
          <h3>Blockchain Anchors</h3>
          <p>{events.filter(e => e.metadata?.chainTxId).length}</p>
          <small>Verified on chain</small>
        </div>
        <div className={styles.metric}>
          <h3>AI Decisions Logged</h3>
          <p>{events.filter(e => e.metadata?.aiDecision).length}</p>
          <small>EOS kennel intelligence</small>
        </div>
      </div>

      <div className={styles.tableWrapper}>
        <table className={styles.auditTable}>
          <thead>
            <tr>
              <th>Entity</th>
              <th>Action</th>
              <th>Seal Hash</th>
              <th>Timestamp</th>
              <th>Jurisdiction</th>
              <th>AI / Reasoning</th>
              <th>Chain</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {filteredEvents.length === 0 ? (
              <tr>
                <td colSpan="8" className={styles.empty}>
                  No audit events found.
                </td>
              </tr>
            ) : (
              filteredEvents.slice(0, 100).map(ev => {
                const tooltip = getTooltip(ev);
                return (
                  <tr key={ev._id || ev.id || Math.random()}>
                    <td>{ev.entityType || ev.type || '—'}</td>
                    <td>
                      <span className={styles.badge}>{getBadge(ev)}</span>
                      {ev.action}
                    </td>
                    <td className={styles.hash}>
                      {ev.sealHash ? ev.sealHash.slice(0, 10) + '…' : '—'}
                    </td>
                    <td>{new Date(ev.timestamp || ev.createdAt).toLocaleString()}</td>
                    <td>{ev.metadata?.jurisdiction || ev.jurisdiction || 'N/A'}</td>
                    <td>
                      {ev.metadata?.aiDecision ? (
                        <span className={styles.aiCell}>
                          🧠 {ev.metadata.aiDecision}
                          {tooltip && (
                            <span className={styles.tooltip}>
                              {tooltip}
                            </span>
                          )}
                        </span>
                      ) : (
                        '—'
                      )}
                    </td>
                    <td>
                      {ev.metadata?.chainTxId ? (
                        <span className={styles.anchored}>✅</span>
                      ) : (
                        <span className={styles.unverified}>❌</span>
                      )}
                    </td>
                    <td>
                      {ev.entityType === 'statement' && (
                        <>
                          <button
                            onClick={() => handleVerifyChain(ev.entityId || ev.id)}
                            disabled={loading}
                            className={styles.verifyButton}
                            title="Verify seal against blockchain anchor"
                          >
                            ⛓️
                          </button>
                          <button
                            onClick={() => handleEvidencePacket(ev.entityId || ev.id)}
                            disabled={loading}
                            className={styles.packetButton}
                            title="Generate evidence packet"
                          >
                            📄
                          </button>
                        </>
                      )}
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>

      <div className={styles.status}>{status}</div>
    </div>
  );
};

export default AuditTab;

// ============================================================================
// HEALTH CHECK – Operational UI
// ============================================================================
// Version: 1.1.0-AUDIT-WEBSOCKET-AI
// Test: npm test -- --grep "AuditTab component"
// Kernel Integration: WebSocket + sovereign api service.
// ============================================================================
