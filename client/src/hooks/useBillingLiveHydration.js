/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS – USE BILLING LIVE HYDRATION [V1.0.0-LIVE-DB]                                                                              ║
 * ║ [ABORTABLE | ALL‑SETTLED | SOURCE SNAPSHOT | LIVE_EMPTY AWARE]                                                                     ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 1.0.0-LIVE-DB | PRODUCTION HARDENED | BIBLICAL WORTH BILLIONS                                                              ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/hooks/useBillingLiveHydration.js                                   ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN‑OFF:                                                                                                ║
 * ║ • Wilson Khanyezi (CEO/Lead Architect) – Mandated abortable, error‑safe hydration for BillingHUD with truthful LIVE_EMPTY.          ║
 * ║ • AI Engineering (DeepSeek) – ARCHITECTED: Hook using Promise.allSettled, buildLiveSourceHeartbeat, and normalized adapters.         ║
 * ║ • Kernel EOS (Python) – All requests carry X-Tenant-ID and can be traced; ready for Kernel observability.                          ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 🏆 COMPETITION OBLITERATION:                                                                                                         ║
 * ║ • HubSpot – Provides billing APIs but no built‑in source health snapshot or LIVE_EMPTY fallback.                                    ║
 * ║ • Lemlist – Usage analytics are less granular; no abortable hydration or settled‑promise reporting.                                 ║
 * ║ • Apollo.io – Enrichment APIs lack billing‑specific normalisation and source‑tracking.                                              ║
 * ║ • Wilsy OS – This hook delivers 3 surfaces (summary, analytics, credit) with a sourceSnapshot that BillingHUD uses to compute        ║
 * ║   operational readiness (currently 6/9, soon 9/9).                                                                                  ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 *
 * @fileoverview React hook that hydrates BillingHUD with live data from three BFF endpoints.
 * Uses Promise.allSettled to avoid total failure, normalises each payload via adapters,
 * and builds a sourceSnapshot for the "Operational Readiness" widget.
 */

import { useCallback, useEffect, useRef, useState } from 'react';
import {
  normalizeBillingSummary,
  normalizeBillingAnalytics,
  normalizeCreditScores,
  buildLiveSourceHeartbeat
} from '../utils/billingLiveAdapter';

/**
 * @param {object} options
 * @param {string} options.tenantId - Tenant ID for request headers (default 'MASTER').
 * @param {{ get: Function }} options.client - Axios-like client (e.g., sovereignClient).
 * @param {boolean} [options.auto=true] - Automatically hydrate on mount.
 * @returns {object} { summary, analytics, creditScores, sourceSnapshot, loading, refreshing, error, hydrate, setSummary }
 */
export default function useBillingLiveHydration({ tenantId = 'MASTER', client, auto = true } = {}) {
  const [summary, setSummary] = useState(null);
  const [analytics, setAnalytics] = useState(null);
  const [creditScores, setCreditScores] = useState({});
  const [sourceSnapshot, setSourceSnapshot] = useState({ lastSync: null, sources: {} });
  const [loading, setLoading] = useState(Boolean(auto));
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState(null);
  const abortRef = useRef(null);

  const hydrate = useCallback(
    async (mode = 'cold') => {
      if (!client || typeof client.get !== 'function') {
        setError('Billing client unavailable');
        setLoading(false);
        return null;
      }

      abortRef.current?.abort?.();
      const controller = typeof AbortController !== 'undefined' ? new AbortController() : null;
      abortRef.current = controller;

      setRefreshing(mode !== 'cold');
      setError(null);
      if (mode === 'cold') setLoading(true);

      const signal = controller?.signal;
      const headers = { 'X-Tenant-ID': tenantId };

      try {
        const [summaryResult, analyticsResult, creditResult] = await Promise.allSettled([
          client.get('/billing/summary', { signal, headers }),
          client.get('/billing/analytics', { signal, headers }),
          client.get('/billing/credit-scores', { signal, headers })
        ]);

        let nextSummary = null;
        if (summaryResult.status === 'fulfilled') {
          const raw = summaryResult.value?.data ?? summaryResult.value;
          nextSummary = normalizeBillingSummary(raw);
          setSummary(nextSummary);
        }

        if (analyticsResult.status === 'fulfilled') {
          const raw = analyticsResult.value?.data ?? analyticsResult.value;
          setAnalytics(normalizeBillingAnalytics(raw));
        }

        if (creditResult.status === 'fulfilled') {
          const raw = creditResult.value?.data ?? creditResult.value;
          setCreditScores(normalizeCreditScores(raw).scores);
        }

        setSourceSnapshot({
          lastSync: new Date().toISOString(),
          sources: {
            summary: buildLiveSourceHeartbeat(
              summaryResult.status === 'fulfilled'
                ? { status: 'fulfilled', value: nextSummary }
                : summaryResult,
              'Billing summary'
            ),
            analytics: buildLiveSourceHeartbeat(
              analyticsResult.status === 'fulfilled'
                ? {
                    status: 'fulfilled',
                    value: {
                      source: analyticsResult.value?.data?.source || analyticsResult.value?.source
                    }
                  }
                : analyticsResult,
              'Billing analytics'
            ),
            credit: buildLiveSourceHeartbeat(
              creditResult.status === 'fulfilled'
                ? {
                    status: 'fulfilled',
                    value: {
                      source: creditResult.value?.data?.source || creditResult.value?.source
                    }
                  }
                : creditResult,
              'Credit scores'
            )
          }
        });

        // Only hard-error when summary fails AND no partial data
        if (summaryResult.status === 'rejected' && !nextSummary) {
          const msg =
            summaryResult.reason?.response?.data?.message ||
            summaryResult.reason?.message ||
            'Billing summary unavailable';
          setError(msg);
        }

        return nextSummary;
      } catch (err) {
        if (err?.name !== 'CanceledError' && err?.name !== 'AbortError') {
          setError(err?.response?.data?.message || err?.message || 'Billing hydrate failed');
        }
        return null;
      } finally {
        setLoading(false);
        setRefreshing(false);
      }
    },
    [client, tenantId]
  );

  useEffect(() => {
    if (!auto) return undefined;
    hydrate('cold');
    return () => {
      abortRef.current?.abort?.();
    };
  }, [auto, hydrate, tenantId]);

  return {
    summary,
    analytics,
    creditScores,
    sourceSnapshot,
    loading,
    refreshing,
    error,
    hydrate,
    setSummary
  };
}

/**
 * =============================================================================
 * INSTITUTIONAL CERTIFICATION SEAL — useBillingLiveHydration v1.0.0-LIVE-DB
 * =============================================================================
 */
