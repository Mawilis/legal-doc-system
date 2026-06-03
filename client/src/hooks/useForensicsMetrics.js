/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - FORENSICS METRICS HOOK (SOVEREIGN WRAPPER) [V3.1.0-FORTUNE-500]                                                             ║
 * ║ [INHERITS: CIRCUIT BREAKER | CANONICAL SEALS | ADAPTIVE REFRESH | STALE-WHILE-REVALIDATE]                                              ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 3.1.0-FINAL | PRODUCTION READY | BILLION DOLLAR SPEC                                                                          ║
 * ║ EPITOME: BIBLICAL WORTH BILLIONS | NO CHILD'S PLACE | FORENSIC CHAIN OF CUSTODY                                                        ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/hooks/useForensicsMetrics.js                                          ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                 ║
 * ║ • Wilson Khanyezi (CEO/Lead Architect) - Mandated audit trail streaming, cryptographic strike visibility.                              ║
 * ║ • AI Engineering (Gemini) - RECTIFIED: Enhanced boardroom summary with anomalies, replay attempts, audit status. [2026-05-07]          ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import useSovereignMetrics from './useSovereignMetrics.js';
import api from '../services/api';

/**
 * @hook useForensicsMetrics
 * @description Streams cryptographic audit strikes, forensic seals, and anomaly events.
 * @param {Object} options - Configuration options (see useSovereignMetrics for full list).
 * @returns {Object} { metrics, boardroomSummary, isSyncing, isStale, error, refresh, breakerStatus }
 */
export const useForensicsMetrics = (options = {}) => {
  const apiFn = async ({ tenantId, signal, headers }) => {
    const response = await api.get(`/forensics/metrics/${tenantId}`, {
      signal,
      headers,
    });
    return response.data?.data || response.data;
  };

  return useSovereignMetrics({
    ...options,
    apiFn,
    telemetryType: 'FORENSICS_EVENT',
    prefix: 'FOR',
    boardroomTransform: (data) => ({
      LastStrike: data.lastStrike || 'N/A',
      SealHash: data.sealHash || data.hash || 'Unknown',
      Anomalies: data.anomalies?.length || 0,
      ReplayAttempts: data.replayAttempts || 0,
      AuditStatus: data.auditStatus || 'Pending',
      raw: data,
    }),
  });
};

export default useForensicsMetrics;

/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ BOARDROOM SUMMARY — FORENSICS METRICS WRAPPER                                                                                          ║
 * ║ GUARANTEES:                                                                                                                            ║
 * ║ • Inherits all sovereign guarantees from useSovereignMetrics: canonical seals, circuit breaker, adaptive refresh, SWR, telemetry.     ║
 * ║ • Boardroom Transform exposes audit KPIs (anomalies, replay attempts, audit status) for compliance dashboards.                         ║
 * ║ • Zero duplication: all resilience logic lives in the base hook.                                                                       ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */
