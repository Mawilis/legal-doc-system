/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - BOARD-READY BATCH VERIFICATION VIEW [V33.8.0-OMEGA-QR-SIGNATURE]                                                            ║
 * ║ [ROOT CA VALIDATION | COMPLIANCE ESCALATION | CRYPTOGRAPHIC TIMELINE | INLINE QR PAYLOADS]                                             ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 33.8.0-OMEGA | BIBLICAL WORTH BILLIONS | PRODUCTION READY                                                                     ║
 * ║ EPITOME: BIBLICAL WORTH BILLIONS | NO CHILD'S PLACE | INSTITUTIONAL DOMINANCE                                                          ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/components/sovereign/BatchVerificationView.jsx                        ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                 ║
 * ║ • Wilson Khanyezi (CEO/Lead Architect) - Mandated file name in header, batch signatures, inline QR logic, and compliance blocks.       ║
 * ║ • AI Engineering (Gemini) - RECTIFIED: Purged raw fetch API. Retained authenticated `api` module for sovereign data transit.           ║
 * ║ • AI Engineering (Gemini) - ENHANCED: Injected the signature UI and trace-level dual-assurance QR codes perfectly into the ledger.     ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import React, { useEffect, useState } from 'react';
import { ShieldCheck, ShieldAlert, Clock, Fingerprint, Link as LinkIcon, AlertTriangle, CheckCircle2, ArrowRight, Shield } from 'lucide-react';
import api from '../../services/api';
import styles from './BatchVerificationView.module.css';

const BatchVerificationView = ({ batchId }) => {
  const [batch, setBatch] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!batchId) {
      setError("NO BATCH ID PROVIDED.");
      setLoading(false);
      return;
    }

    const fetchBatchData = async () => {
      try {
        // 🛡️ Executing the batch cryptographic strike via secure interceptor
        const res = await api.get(`/audit/batch/view/${batchId}`);
        setBatch(res.data);
      } catch (err) {
        console.error('⚠️ [SOVEREIGN_FRACTURE] Batch verification failed:', err);
        setError("CRYPTOGRAPHIC RETRIEVAL FAILED. BATCH MAY BE PURGED OR TAMPERED.");
      } finally {
        setLoading(false);
      }
    };

    fetchBatchData();
  }, [batchId]);

  if (loading) return <div className={styles.loading}>HYDRATING SOVEREIGN BATCH...</div>;
  if (error) return <div className={styles.error}><ShieldAlert size={16} /> {error}</div>;
  if (!batch) return <div className={styles.error}>NO SOVEREIGN DATA AVAILABLE.</div>;

  const isChainValid = batch.chainVerified;

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <Fingerprint size={24} className={styles.iconGold} />
          {/* 🛡️ RECTIFIED: Explicit File Name Identifier as Mandated */}
          <h2 className={styles.title}>BatchVerificationView.jsx — WILSY OS BATCH VERIFICATION</h2>
        </div>
        <div className={styles.timestamp}>ISSUED: {batch.timestamp ? new Date(batch.timestamp).toLocaleString() : 'N/A'}</div>
      </div>

      {/* 🛡️ BOARD-READY CRYPTOGRAPHIC BLOCK */}
      <div className={styles.cryptoBlock}>
        <div className={styles.cryptoItem}>
          <span className={styles.cryptoLabel}>BATCH ID</span>
          <span className={styles.cryptoValue}>{batch.batchId}</span>
        </div>
        <div className={styles.cryptoItem}>
          <span className={styles.cryptoLabel}>ROOT CA CHAIN STATUS</span>
          <div className={isChainValid ? styles.statusAuthentic : styles.statusTampered}>
            {isChainValid ? (
              <><LinkIcon size={14} /> CHAIN VERIFIED [OK]</>
            ) : (
              <><ShieldAlert size={14} /> CHAIN INVALID [FRACTURE]</>
            )}
          </div>
        </div>

        {/* 🛡️ MASTER BATCH SIGNATURE */}
        <div className={styles.cryptoItem} style={{ gridColumn: '1 / -1', marginTop: '10px', paddingTop: '10px', borderTop: '1px solid #222' }}>
          <span className={styles.cryptoLabel}>MASTER SIGNATURE</span>
          <span className={styles.cryptoValue} style={{ fontSize: '0.65rem', color: '#D4AF37', wordBreak: 'break-all' }}>
            {batch.signature || 'AWAITING_SOVEREIGN_SIGNATURE'}
          </span>
        </div>
      </div>

      {/* 🚨 COMPLIANCE ESCALATION BANNER */}
      {!isChainValid && (
        <div className={styles.complianceAlert}>
          <AlertTriangle size={18} />
          <div>
            <strong>SOVEREIGN ESCALATION:</strong> Failed chain validation detected. Telemetry alerts and notifications have been dispatched to Wilsy OS Compliance Officers.
          </div>
        </div>
      )}

      {/* 🛡️ TIMELINE ITERATION WITH SINGLE-TRACE DRILLDOWN & QR PAYLOADS */}
      <section className={styles.section}>
        <h3 className={styles.sectionTitle}>AUTHENTICITY TIMELINE</h3>
        <div className={styles.timeline}>
          {batch.results && batch.results.length > 0 ? (
            batch.results.map((entry, idx) => {
              const targetAuditUrl = entry.auditUrl || `/audit/${entry.traceId}`;

              return (
                <div key={entry.traceId || idx} className={styles.timelineItem}>
                  <div className={styles.timelineMeta}>
                    <span className={styles.timelineDate}>
                      <Clock size={12} /> {entry.timestamp ? new Date(entry.timestamp).toLocaleString() : 'PENDING'}
                    </span>
                    <span className={styles.timelineTrace}>TRACE: {entry.traceId || 'N/A'}</span>
                  </div>

                  <div className={styles.timelineSeal}>
                    <Fingerprint size={12} /> SEAL: {entry.sealHash || 'AWAITING_SEAL'}
                  </div>

                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '12px' }}>
                    <div className={entry.verified ? styles.statusAuthentic : styles.statusTampered}>
                      {entry.verified ? (
                        <><CheckCircle2 size={14} /> TRACE AUTHENTIC ✅</>
                      ) : (
                        <><ShieldAlert size={14} /> TRACE TAMPERED ❌</>
                      )}
                    </div>

                    {entry.traceId && (
                      <a
                        href={targetAuditUrl}
                        target="_blank"
                        rel="noopener noreferrer"
                        className={styles.drilldownLink}
                        style={{
                          display: 'flex', alignItems: 'center', gap: '6px',
                          color: '#D4AF37', fontSize: '0.6rem', fontWeight: 800,
                          textDecoration: 'none', border: '1px solid #D4AF37',
                          padding: '4px 8px', borderRadius: '4px', letterSpacing: '1px',
                          transition: 'all 0.2s', background: 'rgba(212, 175, 55, 0.05)'
                        }}
                        onMouseEnter={(e) => { e.currentTarget.style.background = '#D4AF37'; e.currentTarget.style.color = '#000'; }}
                        onMouseLeave={(e) => { e.currentTarget.style.background = 'rgba(212, 175, 55, 0.05)'; e.currentTarget.style.color = '#D4AF37'; }}
                      >
                        [ VIEW AUDIT ENTRY ] <ArrowRight size={12} />
                      </a>
                    )}
                  </div>

                  {/* 🛡️ INLINE SIGNED QR CODE FOR EACH TRACE */}
                  {entry.qrCode && (
                    <div style={{ marginTop: '15px', paddingTop: '15px', borderTop: '1px dashed #222', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                      <img
                        src={entry.qrCode}
                        alt="Signed Audit QR Code"
                        style={{ width: '100px', height: '100px', border: '2px solid #D4AF37', borderRadius: '6px', boxShadow: '0 0 10px rgba(212, 175, 55, 0.1)' }}
                      />
                      <p style={{ fontSize: '0.55rem', color: '#D4AF37', marginTop: '10px', textAlign: 'center', textTransform: 'uppercase', letterSpacing: '1px', fontWeight: 'bold' }}>
                        Scan to verify this report — payload + signature included
                      </p>
                    </div>
                  )}
                </div>
              );
            })
          ) : (
            <div className={styles.noData}>NO TRACES IN BATCH</div>
          )}
        </div>
      </section>

      {/* 🛡️ CERTIFICATE CHAIN DUMP */}
      <section className={styles.section}>
        <h3 className={styles.sectionTitle}>CERTIFICATE CHAIN</h3>
        <div className={styles.certContainer}>
          {batch.certificateChain && batch.certificateChain.length > 0 ? (
            batch.certificateChain.map((cert, idx) => (
              <pre key={idx} className={styles.certBlock}>{cert}</pre>
            ))
          ) : (
            <div className={styles.noData}>CHAIN DATA UNAVAILABLE</div>
          )}
        </div>
      </section>

      {/* 🛡️ COMPLIANCE NOTIFICATIONS FOOTER */}
      <section className={styles.section} style={{ marginTop: '30px', padding: '15px', background: '#080808', border: '1px solid #1f1f1f', borderRadius: '6px' }}>
        <h3 className={styles.sectionTitle} style={{ borderBottom: 'none', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Shield size={14} /> COMPLIANCE NOTIFICATIONS
        </h3>
        <p style={{ fontSize: '0.65rem', color: '#888', margin: 0, letterSpacing: '0.5px' }}>
          Any failed chain validations are automatically escalated as sovereign alerts to Wilsy OS compliance officers.
        </p>
      </section>

    </div>
  );
};

export default BatchVerificationView;
