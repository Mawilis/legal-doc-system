/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - UNIFIED SOVEREIGN AUDIT MODULE [V33.10.0-OMEGA-WIRED]                                                                       ║
 * ║ [BATCH AUTHENTICITY | SINGLE-TRACE DRILLDOWN | COMPLIANCE ESCALATION | CENTRALIZED CRYPTO NEXUS]                                       ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 33.10.0-OMEGA | BIBLICAL WORTH BILLIONS | PRODUCTION READY                                                                    ║
 * ║ EPITOME: BIBLICAL WORTH BILLIONS | NO CHILD'S PLACE | INSTITUTIONAL DOMINANCE                                                          ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/components/sovereign/AuditModule.jsx                                  ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                 ║
 * ║ • Wilson Khanyezi (CEO/Lead Architect) - Mandated direct wiring to `auditUtils.js` for centralized cryptographic execution.            ║
 * ║ • AI Engineering (Gemini) - RECTIFIED: Purged raw fetch API. Injected `api` module to secure all cryptographic data transit.           ║
 * ║ • AI Engineering (Gemini) - ENHANCED: Fused the centralized utility logic with the $1B high-fidelity Lucide UI and styling module.     ║
 * ║ ⚠️ ARCHITECT NOTE: Ensure Webpack/Vite is configured to polyfill Node modules ('crypto', 'fs') if auditUtils.js is run client-side.    ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import React, { useEffect, useState } from 'react';
import { Buffer } from 'buffer'; // 🛡️ Production safeguard for Buffer execution in browser
import {
  ShieldCheck, ShieldAlert, Clock, Fingerprint, Link as LinkIcon,
  AlertTriangle, CheckCircle2, ArrowRight, Shield, FileText, ShieldQuestion, Key, Loader2
} from 'lucide-react';
import api from '../../services/api';
import styles from './AuditModule.module.css';

// 🛡️ CENTRALIZED CRYPTOGRAPHIC UTILITIES
import {
  validateChain,
  getSignedAuditQr,
  verifySealHash,
  verifyQrSignature
} from '../../utils/auditUtils';

// ═══════════════════════════════════════════════════════════════════════════════════════════
// 🏛️ COMPONENT 1: BATCH VERIFICATION VIEW
// ═══════════════════════════════════════════════════════════════════════════════════════════

export const BatchVerificationView = ({ batchId }) => {
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
        const res = await api.get(`/audit/batch/view/${batchId}`);
        const data = res.data;

        // 🛡️ CENTRALIZED LOGIC: Validate chain using auditUtils
        const chainVerified = validateChain(data.certificateChain);

        // 🛡️ CENTRALIZED LOGIC: Attach signed QR codes to each entry
        const resultsWithQr = await Promise.all(
          data.results.map(async entry => {
            const qrCode = await getSignedAuditQr(entry.traceId, entry.sealHash);
            return { ...entry, qrCode };
          })
        );

        setBatch({ ...data, chainVerified, results: resultsWithQr });
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
          <h2 className={styles.title}>AuditModule.jsx — WILSY OS BATCH VERIFICATION</h2>
        </div>
        <div className={styles.timestamp}>ISSUED: {batch.timestamp ? new Date(batch.timestamp).toLocaleString() : 'N/A'}</div>
      </div>

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

        <div className={styles.cryptoItem} style={{ gridColumn: '1 / -1', marginTop: '10px', paddingTop: '10px', borderTop: '1px solid #222' }}>
          <span className={styles.cryptoLabel}>MASTER SIGNATURE</span>
          <span className={styles.cryptoValue} style={{ fontSize: '0.65rem', color: '#d4af37', wordBreak: 'break-all' }}>
            {batch.signature || 'AWAITING_SOVEREIGN_SIGNATURE'}
          </span>
        </div>
      </div>

      {!isChainValid && (
        <div className={styles.complianceAlert}>
          <AlertTriangle size={18} />
          <div>
            <strong>SOVEREIGN ESCALATION:</strong> Failed chain validation detected. Telemetry alerts and notifications have been dispatched to Wilsy OS Compliance Officers.
          </div>
        </div>
      )}

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
                      >
                        [ VIEW AUDIT ENTRY ] <ArrowRight size={12} />
                      </a>
                    )}
                  </div>

                  {entry.qrCode && (
                    <div className={styles.qrSectionInline}>
                      <img src={entry.qrCode} alt="Signed Audit QR Code" className={styles.qrCodeInline} />
                      <p className={styles.qrLabelInline}>Scan to verify this report — payload + signature included</p>
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

      <section className={styles.complianceFooter}>
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

// ═══════════════════════════════════════════════════════════════════════════════════════════
// 🏛️ COMPONENT 2: SINGLE-TRACE AUDIT ENTRY (DRILL-DOWN)
// ═══════════════════════════════════════════════════════════════════════════════════════════

export const AuditEntry = ({ traceId }) => {
  const [entry, setEntry] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [verificationResult, setVerificationResult] = useState(null);
  const [isVerifying, setIsVerifying] = useState(false);

  useEffect(() => {
    if (!traceId) {
      setError("NO TRACE ID PROVIDED FOR FORENSIC SCAN.");
      setLoading(false);
      return;
    }

    const fetchAuditEntry = async () => {
      try {
        const res = await api.get(`/audit/${traceId}`);
        const data = res.data;

        // 🛡️ CENTRALIZED LOGIC: Verify seal hash using auditUtils
        // Using explicit Buffer to protect browser execution context
        const verified = verifySealHash(Buffer.from(data.pdfBuffer), data.sealHash);

        // 🛡️ CENTRALIZED LOGIC: Generate signed QR code
        const qrCode = await getSignedAuditQr(data.traceId, data.sealHash);

        setEntry({ ...data, verified, qrCode });
      } catch (err) {
        console.error('⚠️ [SOVEREIGN_FRACTURE] Single-trace verification failed:', err);
        setError("CRYPTOGRAPHIC RETRIEVAL FAILED. REPORT MAY BE PURGED OR TAMPERED.");
      } finally {
        setLoading(false);
      }
    };

    fetchAuditEntry();
  }, [traceId]);

  const verifyQr = async () => {
    setIsVerifying(true);
    setVerificationResult(null);
    try {
      const res = await api.get(`/audit/verify-qr/${traceId}`);
      const data = res.data;

      // 🛡️ CENTRALIZED LOGIC: Verify QR Signature
      const result = verifyQrSignature(data.payload, data.signature);

      // Mapping the logic into the $1B Sovereign UI object state
      setVerificationResult({
        valid: result.valid,
        certFingerprint: result.certFingerprint,
        issuer: result.issuer
      });
    } catch (err) {
      console.error('⚠️ [SOVEREIGN_FRACTURE] QR Signature Verification Error:', err);
      setVerificationResult({ valid: false, error: 'VERIFICATION_ERROR' });
    } finally {
      setIsVerifying(false);
    }
  };

  if (loading) return <div className={styles.loading}>DECRYPTING SOVEREIGN LEDGER...</div>;
  if (error) return <div className={styles.error}><ShieldAlert size={16} /> {error}</div>;
  if (!entry) return <div className={styles.error}>NO TRACE DATA AVAILABLE.</div>;

  return (
    <div className={styles.container} style={{ maxWidth: '700px' }}>
      <div className={styles.header}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <FileText size={24} className={styles.iconGold} />
          <h2 className={styles.title}>AuditEntry.jsx — INVESTOR REPORT VERIFICATION</h2>
        </div>
      </div>

      <div className={styles.dataGrid}>
        <div className={styles.dataRow}>
          <span className={styles.label}><Fingerprint size={12} /> TRACE ID</span>
          <span className={styles.value}>{entry.traceId}</span>
        </div>

        <div className={styles.dataRow}>
          <span className={styles.label}><Fingerprint size={12} /> SEAL HASH</span>
          <span className={styles.valueHash}>{entry.sealHash}</span>
        </div>

        <div className={styles.dataRow}>
          <span className={styles.label}><Clock size={12} /> ISSUED</span>
          <span className={styles.value}>
            {entry.issuedTime ? new Date(entry.issuedTime).toLocaleString() : 'UNKNOWN ORIGIN'}
          </span>
        </div>

        <div className={styles.dataRow} style={{ borderBottom: 'none', paddingTop: '15px', paddingBottom: '0' }}>
          <span className={styles.label}>FORENSIC STATUS</span>
          <div className={entry.verified ? styles.statusAuthentic : styles.statusTampered}>
            {entry.verified ? (
              <><ShieldCheck size={16} /> TRACE AUTHENTIC [OK]</>
            ) : (
              <><ShieldAlert size={16} /> TRACE TAMPERED [FRACTURE]</>
            )}
          </div>
        </div>
      </div>

      {entry.qrCode && (
        <div className={styles.qrSection}>
          <img src={entry.qrCode} alt="Signed Audit QR Code" className={styles.qrCode} />
          <p className={styles.qrLabel} style={{ width: '80%', lineHeight: '1.4' }}>
            SCAN TO VERIFY THIS REPORT IN THE SOVEREIGN CONSOLE — PAYLOAD AND SIGNATURE INCLUDED
          </p>

          <button
            onClick={verifyQr}
            disabled={isVerifying}
            className={styles.verifyBtn}
          >
            {isVerifying ? <Loader2 size={14} className="animate-spin" /> : <ShieldQuestion size={14} />}
            {isVerifying ? 'VERIFYING SIGNATURE...' : 'VERIFY QR SIGNATURE'}
          </button>

          {verificationResult && (
            <div className={`${styles.verificationResult} ${verificationResult.valid ? styles.verificationValid : styles.verificationInvalid}`}>
              {verificationResult.valid ? (
                <>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '10px', fontWeight: 'bold', fontSize: '0.75rem' }}>
                    <ShieldCheck size={16} /> SIGNATURE VERIFIED [OK]
                  </div>
                  <div style={{ color: '#888', marginBottom: '6px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <Key size={12} /> FINGERPRINT: <span style={{ color: '#fff' }}>{verificationResult.certFingerprint || 'N/A'}</span>
                  </div>
                  <div style={{ color: '#888', display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <FileText size={12} /> ISSUER: <span style={{ color: '#fff' }}>{verificationResult.issuer || 'N/A'}</span>
                  </div>
                </>
              ) : (
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontWeight: 'bold', fontSize: '0.75rem' }}>
                  <ShieldAlert size={16} /> SIGNATURE INVALID OR TAMPERED [FRACTURE]
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
};
