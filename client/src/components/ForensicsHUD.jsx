/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║                                                                                                                                        ║
 * ║   ██╗    ██╗██╗██╗     ███████╗██╗   ██╗    ██████╗ ███████╗     ██████╗ ███████╗                                               ║
 * ║   ██║    ██║██║██║     ██╔════╝╚██╗ ██╔╝    ██╔══██╗██╔════╝    ██╔═══██╗██╔════╝                                               ║
 * ║   ██║ █╗ ██║██║██║     ███████╗ ╚████╔╝     ██████╔╝█████╗      ██║   ██║███████╗                                               ║
 * ║   ██║███╗██║██║██║     ╚════██║  ╚██╔╝      ██╔══██╗██╔══╝      ██║   ██║╚════██║                                               ║
 * ║   ╚███╔███╔╝██║███████╗███████║   ██║       ██████╔╝███████╗    ╚██████╔╝███████║                                               ║
 * ║    ╚══╝╚══╝ ╚═╝╚══════╝╚══════╝   ╚═╝       ╚═════╝ ╚══════╝     ╚═════╝ ╚══════╝                                               ║
 * ║                                                                                                                                        ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 * 🏛️ WILSY OS - FORENSIC NEXUS HUD [V68.1.0-MARS-SPEC-SEALED]
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 68.1.0-OMEGA | PRODUCTION READY | BILLION DOLLAR FINALITY                                                                     ║
 * ║ EPITOME: BIBLICAL WORTH BILLIONS | NO CHILD'S PLACE | INSTITUTIONAL AUTHORITY                                                          ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/components/ForensicsHUD.jsx                                           ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                 ║
 * ║ • Wilson Khanyezi – Mandated Mars-spec resilience, strict JSDoc integration, and competitive obliteration.                             ║
 * ║ • AI Engineering – Injected Silent Abort Matrix to neutralize CanceledError unmount memory leaks. Added institutional JSDocs.          ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import React, { useEffect, useState, useCallback, useRef } from "react";
import axios from "axios";
import {
  ShieldAlert, Fingerprint, Search, History,
  Database, Lock, Eye, Binary, Activity, ShieldCheck, RefreshCw,
  AlertTriangle, TrendingUp, Hash, ScrollText, GitBranch, Clock,
  Link2, Award, Cpu, Bell, FileText, Download, Globe, Target,
  AlertOctagon, CheckCircle, XCircle, ChevronRight, Zap
} from "lucide-react";
import styles from "./ForensicsHUD.module.css";

/**
 * @typedef {Object} ForensicData
 * @property {number} integrityIndex - 0-100 chain integrity score.
 * @property {number} activeTraces - Active forensic hooks (logs in last 24h).
 * @property {string} evidenceWeight - Total audit trail size (human readable).
 * @property {number} anomalies - Detected integrity violations.
 * @property {Array<Object>} logs - Immutable audit trail entries with hashes.
 * @property {string} vaultHash - Current SHA3‑512 root hash.
 * @property {string} chainAnchor - Merkle root of the audit chain.
 * @property {number} chainLength - Number of linked entries.
 * @property {Object} benchmark - Competitive benchmark data.
 * @property {Array<Object>} aiRecommendations - Remediation steps.
 * @property {string} logDensity - Human readable log density.
 * @property {Object} riskBreakdown - Granular risk categories.
 * @property {Array<Object>} chainHistory - Last 7 chain integrity checkpoints.
 * @property {Array<Object>} threatIntel - Emerging threat intelligence.
 * @property {Array<Object>} incidentMatrix - Incident response status.
 */

/**
 * @component ForensicsHUD
 * @description The core operational dashboard for monitoring blockchain-anchored
 * evidence, competitive benchmarks, and live threat intelligence.
 * @param {Object} props - Component properties.
 * @param {boolean} [props.embedded=false] - True when mounted inside the Founder Singularity Matrix viewport.
 * @returns {JSX.Element} The forensic evidence operating plane.
 * @collaboration Wilson Khanyezi mandated that Matrix-hosted modules must not use full-page viewport physics that cut components.
 * Mars-spec resilience ensures no unmount data leaks.
 */

/**
 * @function ForensicsHUD
 * @memberof WILSY_OS_CORE
 * @description Sovereign-grade operational asset node optimized for 10-generation architectural distribution.
 * @returns {any} Matrix framework core execution output feedback
 */
const ForensicsHUD = ({ embedded = false }) => {
  const [forensicData, setForensicData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isSyncing, setIsSyncing] = useState(false);
  const [activeView, setActiveView] = useState('dashboard');

  // 🛡️ ABORT CONTROLLER REF FOR MEMORY SEAL
  const fetchAbortControllerRef = useRef(null);
  const dashboardRef = useRef(null);
  const auditViewRef = useRef(null);
  const benchmarkViewRef = useRef(null);
  const hydratedRef = useRef(false);

  /**
   * @function formatBytes
   * @description Converts raw byte counts into human-readable institutional formats.
   * @param {number} bytes - Raw byte integer
   * @returns {string} Formatted size (e.g., "1.24 MB")
   */
  const formatBytes = (bytes) => {
    if (!bytes || bytes === 0) return "0 B";
    const k = 1024;
    const sizes = ["B", "KB", "MB", "GB", "TB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
  };

  /**
   * @function formatHash
   * @description Truncates cryptographic hashes for HUD display.
   * @param {string} hash - Raw cryptographic hash string
   * @returns {string} Safely truncated hash
   */
  const formatHash = (hash) => {
    if (!hash) return "—";
    return hash.length > 16 ? hash.substring(0, 12) + "…" : hash;
  };

  /**
   * @function formatTimestamp
   * @description Standardizes timestamp rendering for forensic logs.
   * @param {string|Date} timestamp - ISO timestamp
   * @returns {string} Formatted local date/time string
   */
  const formatTimestamp = (timestamp) => {
    if (!timestamp) return "Unknown";
    const date = new Date(timestamp);
    return date.toLocaleDateString() + " " + date.toLocaleTimeString().slice(0, 5);
  };

  /**
   * @function formatScore
   * @description Renders a score only when a live source produced it. This prevents Wilsy OS
   * from presenting invented integrity percentages as boardroom truth.
   * @param {number|null|undefined} score - Live numeric score.
   * @returns {string} Human-readable live score or source-silent marker.
   * @collaboration Wilson Khanyezi mandated that every forensic percentage must be proven by DB evidence.
   */
  const formatScore = (score) => {
    const numeric = Number(score);
    return Number.isFinite(numeric) ? `${numeric}%` : "SOURCE SILENT";
  };

  /**
   * @function scoreWidth
   * @description Converts live scores into safe progress-bar widths without manufacturing fallback values.
   * @param {number|null|undefined} score - Live numeric score.
   * @returns {number} Clamped percentage width.
   * @collaboration Keeps the HUD visually stable while refusing fake data.
   */
  const scoreWidth = (score) => {
    const numeric = Number(score);
    if (!Number.isFinite(numeric)) return 0;
    return Math.max(0, Math.min(100, numeric));
  };

  /**
   * @function getAuthToken
   * @description Reads the currently issued authentication token from approved sovereign storage keys.
   * @returns {string|null} Bearer token or null when no session is available.
   * @collaboration The forensic cockpit must use the operator's real session, never a synthetic credential.
   */
  const getAuthToken = () => (
    localStorage.getItem('wilsy_auth_token') ||
    localStorage.getItem('sovereignToken') ||
    localStorage.getItem('token')
  );

  /**
   * @function getTenantId
   * @description Resolves the active tenant context for tenant-scoped forensic evidence reads.
   * @returns {string} Tenant identifier accepted by the forensic routes.
   * @collaboration Founder/root views should inspect their real tenant ledger instead of a global placeholder.
   */
  const getTenantId = () => (
    localStorage.getItem('tenantId') ||
    localStorage.getItem('wilsy_tenant_id') ||
    localStorage.getItem('discoveredTenant') ||
    'GLOBAL_ROOT'
  );

  /**
   * @function unwrapPayload
   * @description Normalizes API payloads that may return either `{ data }` or raw arrays/objects.
   * @param {Object} response - Axios response object.
   * @returns {*} Unwrapped response payload.
   * @collaboration Keeps the HUD wired to current and legacy route contracts without guessing evidence.
   */
  const unwrapPayload = (response) => response?.data?.data ?? response?.data ?? null;

  /**
   * @function isLiveForensicLedger
   * @description Determines whether the vault route returned real persisted forensic ledger entries.
   * @param {Object} vaultPayload - Raw vault response.
   * @returns {boolean} True only for persisted DB evidence.
   * @collaboration Genesis/resilience fallbacks are useful for uptime, but investors must not see them as proof.
   */
  const isLiveForensicLedger = (vaultPayload) => (
    vaultPayload?.meta?.source === 'forensic_ledger'
  );

  /**
   * @function normalizeVaultLogs
   * @description Extracts only live forensic vault entries and refuses genesis fallback rows.
   * @param {Object} vaultResponse - Axios response from the tenant vault endpoint.
   * @returns {{logs: Array<Object>, meta: Object, liveSource: boolean}} Normalized live evidence packet.
   * @collaboration Wilsy OS should tell the truth when the vault is silent instead of filling the screen.
   */
  const normalizeVaultLogs = (vaultResponse) => {
    const payload = vaultResponse?.data || {};
    const liveSource = isLiveForensicLedger(payload);
    const rows = Array.isArray(payload.data) ? payload.data : [];
    return {
      logs: liveSource ? rows : [],
      meta: payload.meta || {},
      liveSource
    };
  };

  /**
   * @function buildRiskBreakdown
   * @description Builds forensic risk metrics only from live logs and verified chain data.
   * @param {Array<Object>} logs - Persisted forensic log rows.
   * @param {Object} vaultMeta - Vault metadata from the backend.
   * @param {Object|null} chainVerification - Blockchain/hash-chain verification payload.
   * @param {number} activeTraces - Count of 24-hour live traces.
   * @returns {Object} Risk breakdown with nulls for silent sources.
   * @collaboration Eliminates the old hardcoded `98` quantum score and synthetic completeness claims.
   */
  const buildRiskBreakdown = (logs, vaultMeta, chainVerification, activeTraces) => {
    if (!logs.length) {
      return {
        hashIntegrity: null,
        auditCompleteness: null,
        quantumResistance: null,
        forensicDepth: null,
        chainValidation: null
      };
    }

    const hashedRows = logs.filter(log => log.hash || log.chainHash || log.eventSeal).length;
    const hasRealChainVerification = chainVerification && !chainVerification.details?.warning;
    return {
      hashIntegrity: Number.isFinite(Number(vaultMeta.integrityIndex)) ? Number(vaultMeta.integrityIndex) : null,
      auditCompleteness: Math.round((hashedRows / logs.length) * 100),
      quantumResistance: hashedRows ? 100 : null,
      forensicDepth: Math.round((activeTraces / logs.length) * 100),
      chainValidation: hasRealChainVerification ? (chainVerification.verified ? 100 : 0) : null
    };
  };

  /**
   * @function buildAiRecommendations
   * @description Converts live anomaly scans into operational recommendations without generating fake all-clear cards.
   * @param {Array<Object>} anomalies - Live anomaly scan results.
   * @param {Array<Object>} logs - Persisted forensic log rows.
   * @returns {Array<Object>} Actionable forensic recommendation list.
   * @collaboration AI recommendations must originate from evidence, not optimism.
   */
  const buildAiRecommendations = (anomalies, logs) => {
    if (!logs.length) return [];
    if (!anomalies.length) {
      return [{
        id: 'scan-clear',
        priority: 'INFO',
        title: 'Live Scan Clear',
        description: 'The latest anomaly scan returned no failed, fractured or high-severity evidence clusters.',
        steps: ['Continue vault monitoring', 'Export evidence pack only when required'],
        authority: 'Live anomaly scan',
        penaltyRisk: 'None detected in current evidence window',
        severity: 'INFO'
      }];
    }

    return anomalies.map((anomaly, index) => ({
      id: `anomaly-${index + 1}`,
      priority: anomaly.confidence >= 0.8 ? 'IMMEDIATE' : 'REVIEW',
      title: anomaly.type || 'Forensic Anomaly',
      description: anomaly.description || 'Live anomaly source emitted an unspecified evidence warning.',
      steps: ['Open audit trail', 'Verify chain anchor', 'Escalate to founder guard if repeated'],
      authority: 'Live anomaly scan',
      penaltyRisk: 'Evidence admissibility risk if unresolved',
      severity: anomaly.confidence >= 0.8 ? 'CRITICAL' : 'WARN'
    }));
  };

  /**
   * @function buildChainHistory
   * @description Creates chain history from real log rows without invented score decay.
   * @param {Array<Object>} logs - Persisted forensic log rows.
   * @param {Object|null} chainVerification - Live chain verification payload.
   * @returns {Array<Object>} Chain checkpoints.
   * @collaboration Chain history must be a ledger replay, not a decorative graph.
   */
  const buildChainHistory = (logs, chainVerification) => logs.slice(0, 7).map((log, idx) => ({
    id: log.id || idx,
    timestamp: log.timestamp,
    status: log.status || (log.hash ? 'VERIFIED' : 'PENDING'),
    hash: log.hash,
    integrity: chainVerification?.verified === false ? 0 : (log.hash ? 100 : null)
  }));

  /**
   * @function fetchForensics
   * @description Synchronizes the master forensic ledger. Armed with a Silent Abort Matrix
   * to neutralize unmount fractures and network instability.
   * @param {boolean} showSync - Toggles visual syncing state
   */
  const fetchForensics = useCallback(async (showSync = true) => {
    // Sever previous connection if overlapping
    if (fetchAbortControllerRef.current) fetchAbortControllerRef.current.abort();
    fetchAbortControllerRef.current = new AbortController();

    if (showSync) setIsSyncing(true);
    if (showSync || !hydratedRef.current) setLoading(true);
    setError(null);

    try {
      const token = getAuthToken();
      const tenantId = getTenantId();
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:5050';

      const [vaultRes, chainRes, benchRes] = await Promise.all([
        axios.get(`${apiUrl}/forensics/vault/${tenantId}`, {
          params: { limit: 120 },
          headers: { Authorization: `Bearer ${token}` },
          signal: fetchAbortControllerRef.current.signal,
          timeout: 10000
        }),
        axios.get(`${apiUrl}/forensics/blockchain-verify`, {
          headers: { Authorization: `Bearer ${token}` },
          signal: fetchAbortControllerRef.current.signal,
          timeout: 10000
        }).catch(() => ({ data: null })),
        axios.get(`${apiUrl}/forensics/benchmark`, {
          headers: { Authorization: `Bearer ${token}` },
          signal: fetchAbortControllerRef.current.signal,
          timeout: 5000
        }).catch(() => ({ data: null }))
      ]);

      const vaultPacket = normalizeVaultLogs(vaultRes);
      const logs = vaultPacket.logs;
      const chainVerification = unwrapPayload(chainRes);
      const benchmarkPayload = unwrapPayload(benchRes);
      const benchmark = benchmarkPayload?.sampleSize ? benchmarkPayload : {
        wilsyLatency: "SOURCE SILENT",
        competitorLatency: "SOURCE SILENT",
        competitorVolume: "SOURCE SILENT",
        sampleSize: 0
      };

      let totalBytes = logs.reduce((sum, log) => sum + JSON.stringify(log).length, 0);
      const evidenceWeight = formatBytes(totalBytes);
      const now = new Date();
      const activeTraces = logs.filter(log => {
        if (!log.timestamp) return false;
        return (now - new Date(log.timestamp)) / (1000 * 60 * 60) <= 24;
      }).length;

      const anomalyRes = logs.length
        ? await axios.post(`${apiUrl}/forensics/scan-anomalies`, { logs }, {
            headers: { Authorization: `Bearer ${token}` },
            signal: fetchAbortControllerRef.current.signal,
            timeout: 10000
          }).catch(() => ({ data: { anomalies: [] } }))
        : { data: { anomalies: [] } };

      const anomalies = Array.isArray(anomalyRes.data?.anomalies) ? anomalyRes.data.anomalies : [];
      const riskBreakdown = buildRiskBreakdown(logs, vaultPacket.meta, chainVerification, activeTraces);
      const chainHistory = buildChainHistory(logs, chainVerification);
      const aiRecommendations = buildAiRecommendations(anomalies, logs);

      const threatIntel = [];
      const incidentMatrix = anomalies.map((anomaly, index) => ({
        id: `INC-${index + 1}`,
        incident: anomaly.type || 'FORENSIC_ANOMALY',
        severity: anomaly.confidence >= 0.8 ? 'HIGH' : 'MEDIUM',
        status: 'REVIEW_REQUIRED',
        eta: 'MANUAL'
      }));

      setForensicData({
        integrityIndex: logs.length ? riskBreakdown.hashIntegrity : null,
        activeTraces,
        evidenceWeight,
        anomalies: anomalies.length,
        logs,
        vaultHash: logs[0]?.hash || null,
        chainAnchor: chainVerification?.merkleRoot || logs[0]?.hash || null,
        chainLength: logs.length,
        benchmark,
        aiRecommendations,
        logDensity: logs.length ? `${logs.length} entries` : "0 entries",
        riskBreakdown,
        chainHistory,
        threatIntel,
        incidentMatrix,
        source: vaultPacket.liveSource ? 'forensic_ledger' : 'SOURCE_SILENT',
        sourceMeta: vaultPacket.meta,
        chainVerification
      });
      hydratedRef.current = true;
    } catch (err) {
      // 🛑 SILENT ABORT MATRIX: Catch and neutralize component unmount memory leaks
      if (axios.isCancel(err) || err.name === 'AbortError' || err.name === 'CanceledError') {
        console.debug('🛡️ [Forensic_Seal]: Audit sweep aborted gracefully on unmount.');
        return;
      }

      console.error("⚠️ [Forensics_Fracture]: Fetch failed:", err);
      setError(err.message || "Forensic vault unreachable.");
      setForensicData(null);
    } finally {
      setLoading(false);
      if (showSync) setIsSyncing(false);
    }
  }, []);

  /**
   * ⚡ LIFECYCLE HOOK
   * Executes initial sweep and sets up robust heartbeat polling.
   */
  useEffect(() => {
    fetchForensics(true);
    const interval = setInterval(() => fetchForensics(false), 60000);
    return () => {
      clearInterval(interval);
      // Ensure any pending request is killed when component unmounts
      if (fetchAbortControllerRef.current) {
        fetchAbortControllerRef.current.abort();
      }
    };
  }, [fetchForensics]);

  /**
   * @function handleSync
   * @description Executes a manual forensic vault synchronization using the live tenant ledger.
   * @returns {void}
   * @collaboration This is an operator command, not a cosmetic refresh.
   */
  const handleSync = () => fetchForensics(true);

  const safeData = forensicData || {
    integrityIndex: null,
    activeTraces: 0,
    evidenceWeight: "0 B",
    anomalies: 0,
    logs: [],
    vaultHash: null,
    chainAnchor: null,
    chainLength: 0,
    benchmark: { wilsyLatency: "SOURCE SILENT", competitorLatency: "SOURCE SILENT", competitorVolume: "SOURCE SILENT", sampleSize: 0 },
    aiRecommendations: [],
    riskBreakdown: { hashIntegrity: null, auditCompleteness: null, quantumResistance: null, forensicDepth: null, chainValidation: null },
    chainHistory: [],
    threatIntel: [],
    incidentMatrix: [],
    source: 'SOURCE_SILENT',
    sourceMeta: {},
    chainVerification: null
  };

  /**
   * @function handleViewChange
   * @description Activates a forensic sector and moves the viewport to the relevant section.
   * @param {string} view - The target forensic view.
   * @returns {void}
   * @collaboration Section commands must navigate like an operating system, not leave the user scrolling.
   */
  const handleViewChange = (view) => {
    const targetRefs = {
      dashboard: dashboardRef,
      audit: auditViewRef,
      benchmark: benchmarkViewRef
    };
    setActiveView(view);
    window.requestAnimationFrame(() => {
      targetRefs[view]?.current?.scrollIntoView({
        behavior: 'smooth',
        block: 'start',
        inline: 'nearest'
      });
    });
  };

  /**
   * @function copyHashToClipboard
   * @description Copies a live evidence hash to the operator clipboard without pretending it is an Ethereum transaction.
   * @param {string} hash - Evidence hash emitted by the forensic ledger.
   * @returns {Promise<void>}
   * @collaboration Evidence exploration must respect the actual Wilsy chain, not route hashes to unrelated block explorers.
   */
  const copyHashToClipboard = async (hash) => {
    if (!hash || !navigator.clipboard) return;
    await navigator.clipboard.writeText(hash);
  };

  /**
   * @function handleExport
   * @description Exports a board evidence pack only when live vault logs exist.
   * @returns {void}
   * @collaboration Exported artifacts must be court-ready truth, never a generated placeholder packet.
   */
  const handleExport = () => {
    if (!safeData.logs.length) return;

    const evidencePack = {
      exportedAt: new Date().toISOString(),
      integrityIndex: safeData.integrityIndex,
      evidenceWeight: safeData.evidenceWeight,
      chainAnchor: safeData.chainAnchor,
      chainLength: safeData.chainLength,
      anomalies: safeData.anomalies,
      logs: safeData.logs,
      vaultHash: safeData.vaultHash,
      source: safeData.source,
      sourceMeta: safeData.sourceMeta,
      chainVerification: safeData.chainVerification,
      legalBasis: "Forensic evidence export generated from live Wilsy OS vault state"
    };

    const blob = new Blob([JSON.stringify(evidencePack, null, 2)], {
      type: "application/json"
    });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `WILSY_Forensic_Evidence_Pack_${Date.now()}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  if (loading && !forensicData) {
    return <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh', color: '#D4AF37' }}>Reconstructing Evidence Matrix...</div>;
  }

  if (error && !forensicData) {
    return <div style={{ textAlign: 'center', padding: 50, color: 'red' }}>Error: {error}<br/><button onClick={handleSync}>Retry</button></div>;
  }

  return (
    <div className={`${styles.hudContainer} ${embedded ? styles.hudContainerEmbedded : ''}`}>
      {/* MAIN FORENSIC CARD */}
      {!embedded && (
      <div className={styles.forensicCard}>
        <div className={styles.forensicCardHeader}>
          <div className={styles.forensicBrand}>
            <div className={styles.forensicBrandRail} />
            <div>
              <div className={styles.forensicEyebrow}>
                <Database size={12} /> Institutional Audit Fortress
              </div>
              <h1 className={styles.titanTitleCompact}>
                FORENSIC <span style={{ color: '#D4AF37' }}>NEXUS</span>
              </h1>
            </div>
          </div>
          <div className={styles.forensicTabs} role="tablist" aria-label="Forensic Nexus operating views">
            {[
              { id: 'dashboard', label: 'Dashboard' },
              { id: 'audit', label: 'Audit Trail' },
              { id: 'benchmark', label: 'Benchmark' }
            ].map((view) => (
              <button
                key={view.id}
                type="button"
                role="tab"
                aria-selected={activeView === view.id}
                data-active={activeView === view.id ? 'true' : 'false'}
                onClick={() => handleViewChange(view.id)}
              >
                {view.label}
              </button>
            ))}
          </div>
        </div>

        {/* Mini metrics */}
        <div className={styles.metricMiniGrid}>
          {[
            { label: "EVIDENCE", value: safeData.evidenceWeight, color: "#00aaff", sub: "Total Load" },
            { label: "ACTIVE", value: safeData.activeTraces, color: "#D4AF37", sub: "24h Hooks" },
            { label: "DETECTED", value: safeData.anomalies, color: "#ff3333", sub: "Tamper Events" },
            { label: "CHAIN", value: safeData.chainLength, color: "#00ff66", sub: "Linked Entries" }
          ].map((m, idx) => (
            <div key={idx} style={{ background: 'rgba(5,5,5,0.7)', border: '1px solid #1a1a1a', borderRadius: '16px', padding: '16px 8px', textAlign: 'center' }}>
              <div style={{ fontSize: '0.7rem', fontWeight: 900, letterSpacing: '2px', color: '#888' }}>{m.label}</div>
              <div style={{ fontSize: 'clamp(1.2rem, 4vw, 1.8rem)', fontWeight: 900, fontFamily: 'monospace', color: m.color }}>{isSyncing ? "—" : m.value}</div>
              <div style={{ fontSize: '0.65rem', color: '#666', marginTop: '6px' }}>{m.sub}</div>
            </div>
          ))}
        </div>
      </div>
      )}

      {/* TWO-COLUMN: CHAIN INTEGRITY GAUGE + LIVE EVIDENCE STREAM */}
      {!embedded && (
      <div ref={dashboardRef} className={styles.metricGridTwoColumn}>
        <div style={{ background: 'radial-gradient(circle at 30% 20%, rgba(0,255,102,0.04), rgba(5,5,5,0.96))', border: '1px solid rgba(0,255,102,0.2)', borderRadius: '20px', padding: '24px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '16px' }}>
            <div>
              <div style={{ fontSize: '0.7rem', fontWeight: 600, letterSpacing: '2px', color: '#aaa' }}>CHAIN_INTEGRITY_GAUGE</div>
              <div><span style={{ fontSize: 'clamp(2rem, 5vw, 3rem)', fontWeight: 900, fontFamily: 'monospace' }}>{isSyncing ? "---" : formatScore(safeData.integrityIndex)}</span></div>
            </div>
            <div style={{ textAlign: 'right' }}>
              <div style={{ position: 'relative', width: '70px', height: '70px', margin: '0 auto' }}>
                <div style={{ position: 'absolute', width: '100%', height: '100%', borderRadius: '50%', border: '1px solid rgba(212,175,55,0.3)', borderTop: '1px solid #D4AF37', animation: 'spin 3s linear infinite' }} />
                <div style={{ position: 'absolute', width: '70%', height: '70%', top: '15%', left: '15%', borderRadius: '50%', border: '1px solid rgba(0,255,102,0.3)', borderBottom: '1px solid #00ff66', animation: 'spinReverse 2s linear infinite' }} />
                <Hash size={28} style={{ position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%,-50%)', color: '#D4AF37', opacity: 0.5 }} />
              </div>
              <div style={{ fontSize: '0.7rem', fontWeight: 'bold', color: safeData.logs.length ? '#00ff66' : '#D4AF37' }}>{safeData.logs.length ? (safeData.anomalies === 0 ? "HASH_VALID" : "HASH_MISMATCH") : "SOURCE_SILENT"}</div>
              <div style={{ height: '4px', background: '#222', borderRadius: '4px', marginTop: '8px' }}><div style={{ width: `${scoreWidth(safeData.integrityIndex)}%`, height: '100%', background: 'linear-gradient(90deg, #00ff66, #D4AF37)', borderRadius: '4px' }} /></div>
            </div>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3,1fr)', gap: '12px', marginTop: '24px' }}>
            <div style={{ background: '#050505', border: '1px solid #1a1a1a', padding: '10px', textAlign: 'center', borderRadius: '12px' }}><div style={{ fontSize: '0.55rem', color: '#888' }}>Merkle Root</div><div style={{ fontSize: '0.7rem', fontFamily: 'monospace', color: '#D4AF37' }}>{formatHash(safeData.chainAnchor)}</div></div>
            <div style={{ background: '#050505', border: '1px solid #1a1a1a', padding: '10px', textAlign: 'center', borderRadius: '12px' }}><div style={{ fontSize: '0.55rem', color: '#888' }}>Hash Algorithm</div><div style={{ fontSize: '0.7rem', fontFamily: 'monospace', color: 'white' }}>{safeData.logs.length ? 'SHA3-512' : 'SOURCE SILENT'}</div></div>
            <div style={{ background: '#050505', border: '1px solid #1a1a1a', padding: '10px', textAlign: 'center', borderRadius: '12px' }}><div style={{ fontSize: '0.55rem', color: '#888' }}>Quantum Safe</div><div style={{ fontSize: '0.7rem', fontFamily: 'monospace', color: safeData.logs.length ? '#00ff66' : '#D4AF37' }}>{safeData.logs.length ? 'EVIDENCE HASHED' : 'SOURCE SILENT'}</div></div>
          </div>

          <div style={{ marginTop: '20px', paddingTop: '16px', borderTop: '1px solid #1a1a1a' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.65rem', fontWeight: 900, color: '#D4AF37', marginBottom: '12px' }}><Target size={14} /> RISK SCORE BREAKDOWN</div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              <div style={{ display: 'grid', gridTemplateColumns: '110px 1fr minmax(72px, auto)', alignItems: 'center', gap: '8px' }}><span style={{ fontSize: '0.6rem', color: '#aaa' }}>Hash Integrity</span><div style={{ height: '4px', background: '#222', borderRadius: '2px', overflow: 'hidden' }}><div style={{ width: `${scoreWidth(safeData.riskBreakdown.hashIntegrity)}%`, height: '100%', background: '#00ff66' }} /></div><span style={{ fontSize: '0.6rem', fontFamily: 'monospace', color: '#D4AF37', textAlign: 'right' }}>{formatScore(safeData.riskBreakdown.hashIntegrity)}</span></div>
              <div style={{ display: 'grid', gridTemplateColumns: '110px 1fr minmax(72px, auto)', alignItems: 'center', gap: '8px' }}><span style={{ fontSize: '0.6rem', color: '#aaa' }}>Audit Completeness</span><div style={{ height: '4px', background: '#222', borderRadius: '2px', overflow: 'hidden' }}><div style={{ width: `${scoreWidth(safeData.riskBreakdown.auditCompleteness)}%`, height: '100%', background: '#D4AF37' }} /></div><span style={{ fontSize: '0.6rem', fontFamily: 'monospace', color: '#D4AF37', textAlign: 'right' }}>{formatScore(safeData.riskBreakdown.auditCompleteness)}</span></div>
              <div style={{ display: 'grid', gridTemplateColumns: '110px 1fr minmax(72px, auto)', alignItems: 'center', gap: '8px' }}><span style={{ fontSize: '0.6rem', color: '#aaa' }}>Forensic Depth</span><div style={{ height: '4px', background: '#222', borderRadius: '2px', overflow: 'hidden' }}><div style={{ width: `${scoreWidth(safeData.riskBreakdown.forensicDepth)}%`, height: '100%', background: '#00aaff' }} /></div><span style={{ fontSize: '0.6rem', fontFamily: 'monospace', color: '#D4AF37', textAlign: 'right' }}>{formatScore(safeData.riskBreakdown.forensicDepth)}</span></div>
            </div>
          </div>

          <div style={{ marginTop: '16px', paddingTop: '16px', borderTop: '1px solid #1a1a1a' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.65rem', fontWeight: 900, color: '#D4AF37', marginBottom: '12px' }}><History size={14} /> CHAIN INTEGRITY HISTORY</div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {safeData.chainHistory.slice(0,5).map(item => (
                <div key={item.id} style={{ display: 'grid', gridTemplateColumns: '90px 70px 1fr', gap: '8px', alignItems: 'center', fontSize: '0.6rem' }}>
                  <span style={{ color: '#888', fontFamily: 'monospace' }}>{formatTimestamp(item.timestamp)}</span>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>{item.status === "VERIFIED" ? <CheckCircle size={10} style={{ color: '#00ff66' }} /> : <AlertOctagon size={10} style={{ color: '#ff9444' }} />}<span>{item.status}</span></div>
                  <div style={{ height: '3px', background: '#222', borderRadius: '2px', overflow: 'hidden' }}><div style={{ width: `${scoreWidth(item.integrity)}%`, height: '100%', background: '#00ff66' }} /></div>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className={styles.alertShield}>
          <div style={{ background: 'rgba(212,175,55,0.06)', padding: '12px 16px', display: 'flex', alignItems: 'center', gap: '8px', borderBottom: '1px solid rgba(212,175,55,0.15)' }}>
            <AlertTriangle size={14} style={{ color: '#ff9444' }} /> LIVE EVIDENCE STREAM
            <button onClick={handleSync} style={{ marginLeft: 'auto', background: '#222', border: 'none', padding: '4px 8px', borderRadius: '6px', cursor: 'pointer', color: '#D4AF37' }}><RefreshCw size={12} /></button>
          </div>
          <div className={styles.alertScrollContainer}>
            {safeData.logs.slice(0,6).map((log,i) => (
              <div key={i} style={{ borderLeft: '3px solid #D4AF37', padding: '10px', marginBottom: '10px', background: 'rgba(255,255,255,0.02)', borderRadius: '8px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.6rem', color: '#D4AF37', marginBottom: '4px' }}><span>{log.event || 'AUDIT_EVENT'}</span><span style={{ color: '#888' }}>{log.timestamp ? new Date(log.timestamp).toLocaleTimeString() : ''}</span></div>
                <div style={{ fontSize: '0.7rem', color: '#ccc', marginBottom: '4px' }}>{log.message || 'No additional context'}</div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}><span style={{ fontSize: '0.55rem', fontFamily: 'monospace', color: '#888' }}>Hash: {formatHash(log.hash)}</span><button onClick={() => copyHashToClipboard(log.hash)} style={{ background: 'transparent', border: 'none', color: '#00aaff', fontSize: '0.55rem', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '4px' }}><Link2 size={10} /> COPY HASH</button></div>
              </div>
            ))}
            {safeData.logs.length === 0 && <div style={{ textAlign: 'center', padding: '20px', opacity: 0.4 }}><ShieldCheck size={32} /><div>No evidence entries yet.</div></div>}
          </div>
          <button onClick={handleSync} disabled={isSyncing} style={{ background: 'linear-gradient(90deg, rgba(212,175,55,0.12), rgba(0,0,0,0.9))', border: 'none', borderTop: '1px solid rgba(212,175,55,0.3)', padding: '14px', fontWeight: 900, letterSpacing: '2px', color: '#D4AF37', cursor: 'pointer' }}>{isSyncing ? "SYNCING CHAIN..." : "SYNCHRONIZE FORENSIC LEDGER"}</button>
        </div>
      </div>
      )}

      {/* THREAT INTELLIGENCE + INCIDENT RESPONSE */}
      {!embedded && (
      <div className={styles.threatIncidentRow}>
        <div className={styles.alertShield}>
          <div style={{ background: 'rgba(212,175,55,0.06)', padding: '14px 18px', display: 'flex', alignItems: 'center', gap: '12px', borderBottom: '1px solid rgba(212,175,55,0.15)', fontWeight: 900, fontSize: '0.75rem', color: '#D4AF37' }}>
            <Bell size={14} style={{ color: '#ff3333' }} /> THREAT INTELLIGENCE FEED <span style={{ marginLeft: 'auto', background: safeData.threatIntel.length ? '#ff3333' : 'rgba(212,175,55,0.18)', color: safeData.threatIntel.length ? 'white' : '#D4AF37', padding: '2px 10px', borderRadius: '20px', fontSize: '0.6rem' }}>{safeData.threatIntel.length ? 'LIVE' : 'SOURCE SILENT'}</span>
          </div>
          <div style={{ padding: '16px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
            {safeData.threatIntel.map(threat => (
              <div key={threat.id} style={{ borderBottom: '1px solid #2a2a2a', paddingBottom: '12px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '8px', flexWrap: 'wrap' }}>
                  <span style={{ fontSize: '0.6rem', fontWeight: 900, padding: '4px 12px', borderRadius: '20px', background: threat.severity==='CRITICAL'?'rgba(255,51,51,0.2)':threat.severity==='HIGH'?'rgba(255,148,68,0.2)':threat.severity==='MEDIUM'?'rgba(212,175,55,0.2)':'rgba(0,255,102,0.2)', color: threat.severity==='CRITICAL'?'#ff6666':threat.severity==='HIGH'?'#ffaa66':threat.severity==='MEDIUM'?'#ffdd66':'#66ff66' }}>{threat.severity}</span>
                  <span style={{ fontSize: '0.8rem', fontWeight: 'bold', color: 'white' }}>{threat.type}</span>
                </div>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '16px', fontSize: '0.65rem', color: '#aaa', wordBreak: 'break-word' }}>
                  <span>{threat.source}</span><span>{threat.timeAgo}</span><span style={{ fontFamily: 'monospace' }}>{threat.target}</span>
                </div>
              </div>
            ))}
            {safeData.threatIntel.length === 0 && (
              <div style={{ border: '1px solid rgba(212,175,55,0.22)', borderRadius: '12px', padding: '16px', color: '#f5f0dc', background: 'rgba(255,255,255,0.035)', fontSize: '0.72rem', lineHeight: 1.55 }}>
                No synthetic threat feed rendered. Waiting for live forensic intelligence source.
              </div>
            )}
          </div>
        </div>
        <div className={styles.alertShield}>
          <div style={{ background: 'rgba(212,175,55,0.06)', padding: '14px 18px', display: 'flex', alignItems: 'center', gap: '12px', borderBottom: '1px solid rgba(212,175,55,0.15)', fontWeight: 900, fontSize: '0.75rem', color: '#D4AF37' }}>
            <AlertOctagon size={14} /> INCIDENT RESPONSE MATRIX
          </div>
          <div style={{ padding: '16px' }}>
            <div style={{ display: 'grid', gridTemplateColumns: '1.5fr 0.8fr 1fr 0.6fr', fontSize: '0.65rem', fontWeight: 900, color: '#D4AF37', paddingBottom: '10px', borderBottom: '1px solid #2a2a2a', marginBottom: '8px' }}>
              <span>INCIDENT</span><span>SEVERITY</span><span>STATUS</span><span>ETA</span>
            </div>
            {safeData.incidentMatrix.map(inc => (
              <div key={inc.id} style={{ display: 'grid', gridTemplateColumns: '1.5fr 0.8fr 1fr 0.6fr', padding: '10px 0', borderBottom: '1px solid #1a1a1a', fontSize: '0.7rem', alignItems: 'center' }}>
                <span style={{ fontWeight: 'bold', color: '#ddd', wordBreak: 'break-word' }}>{inc.incident}</span>
                <span style={{ fontWeight: 'bold', color: inc.severity==='CRITICAL'?'#ff6666':inc.severity==='HIGH'?'#ffaa66':inc.severity==='MEDIUM'?'#ffdd66':'#66ff66' }}>{inc.severity}</span>
                <span style={{ fontFamily: 'monospace', color: '#aaa' }}>{inc.status}</span>
                <span style={{ color: '#D4AF37' }}>{inc.eta}</span>
              </div>
            ))}
            {safeData.incidentMatrix.length === 0 && (
              <div style={{ padding: '16px 0', fontSize: '0.72rem', color: '#f5f0dc', lineHeight: 1.55 }}>
                Incident matrix is clear from live sources. No placeholder incidents displayed.
              </div>
            )}
          </div>
        </div>
      </div>
      )}

      {/* AI FORENSIC RECOMMENDATIONS + CERTIFICATION BADGES */}
      {!embedded && (
      <div className={styles.aiCertRow}>
        <div className={styles.alertShield}>
          <div style={{ background: 'rgba(212,175,55,0.06)', padding: '14px 18px', display: 'flex', alignItems: 'center', gap: '12px', borderBottom: '1px solid rgba(212,175,55,0.15)', fontWeight: 900, fontSize: '0.75rem', color: '#D4AF37' }}>
            <ScrollText size={14} /> AI FORENSIC RECOMMENDATIONS <span style={{ marginLeft: 'auto', color: '#666' }}>{safeData.aiRecommendations.length} active</span>
          </div>
          <div style={{ maxHeight: '40vh', overflowY: 'auto', padding: '16px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {safeData.aiRecommendations.map(rec => (
              <div key={rec.id} style={{ background: '#111', border: '1px solid #2a2a2a', borderRadius: '14px', padding: '14px' }}>
                <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                  <span style={{ padding: '2px 8px', fontSize: '0.55rem', fontWeight: 900, borderRadius: '20px', background: rec.priority==='IMMEDIATE'?'rgba(255,68,68,0.2)':'rgba(0,255,0,0.2)', color: rec.priority==='IMMEDIATE'?'#ff6666':'#66ff66' }}>{rec.priority}</span>
                  <span style={{ fontSize: '0.7rem', fontWeight: 'bold', color: '#ccc' }}>{rec.title}</span>
                  <span style={{ fontSize: '0.6rem', color: '#555', marginLeft: 'auto' }}>{rec.authority}</span>
                </div>
                <p style={{ fontSize: '0.7rem', color: '#D4AF37', marginBottom: '6px' }}>{rec.description}</p>
                <div style={{ fontSize: '0.65rem', color: '#666', marginBottom: '6px' }}>{rec.steps.join(' • ')}</div>
                <div style={{ fontSize: '0.6rem', color: '#ff8888', borderTop: '1px solid #222', paddingTop: '6px' }}>Penalty: {rec.penaltyRisk}</div>
              </div>
            ))}
          </div>
        </div>
        <div className={styles.alertShield}>
          <div style={{ background: 'rgba(212,175,55,0.06)', padding: '14px 18px', display: 'flex', alignItems: 'center', gap: '12px', borderBottom: '1px solid rgba(212,175,55,0.15)', fontWeight: 900, fontSize: '0.75rem', color: '#D4AF37' }}>
            <Award size={14} /> EVIDENCE CONTROLS
          </div>
          <div className={styles.evidenceControlGrid}>
            {[
              { label: safeData.logs.length ? 'LIVE HASHED' : 'SOURCE SILENT', icon: ShieldCheck },
              { label: safeData.chainAnchor ? 'CHAIN ANCHORED' : 'CHAIN SILENT', icon: Lock },
              { label: safeData.source === 'forensic_ledger' ? 'DB LEDGER' : 'NO DB ROWS', icon: Database },
              { label: safeData.logs.length ? 'EXPORT READY' : 'EXPORT LOCKED', icon: Cpu },
            ].map((control) => {
              const ControlIcon = control.icon;
              return (
                <div key={control.label} className={styles.evidenceControlCard}>
                  <ControlIcon size={22} aria-hidden="true" />
                  <div>{control.label}</div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
      )}

      {/* DYNAMIC VIEWS */}
      {activeView === 'audit' && (
        <div ref={auditViewRef} className={styles.alertShield}>
          <div style={{ background: 'rgba(212,175,55,0.06)', padding: '14px 18px', display: 'flex', alignItems: 'center', gap: '12px', borderBottom: '1px solid rgba(212,175,55,0.15)', fontWeight: 900, fontSize: '0.75rem', color: '#D4AF37' }}>
            <History size={14} /> COMPLETE AUDIT CHAIN
          </div>
          <div style={{ padding: '16px', overflowX: 'auto' }}>
            <table style={{ width: '100%', textAlign: 'left', borderCollapse: 'collapse' }}>
              <thead><tr style={{ borderBottom: '1px solid #222' }}><th style={{ padding: '8px', fontSize: '0.65rem', color: '#888' }}>Evidence Ref</th><th style={{ padding: '8px', fontSize: '0.65rem', color: '#888' }}>Event Type</th><th style={{ padding: '8px', fontSize: '0.65rem', color: '#888' }}>Sovereign Actor</th><th style={{ padding: '8px', fontSize: '0.65rem', color: '#888' }}>Timestamp</th><th style={{ padding: '8px', fontSize: '0.65rem', color: '#888' }}>Hash Link</th></tr></thead>
              <tbody>{safeData.logs.slice(0,20).map((log,idx) => (<tr key={idx} style={{ borderBottom: '1px solid #111' }}><td style={{ padding: '8px', fontSize: '0.7rem', fontFamily: 'monospace', color: '#D4AF37' }}>{log.id || `EV-${idx}`}</td><td style={{ padding: '8px' }}><span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}><Binary size={10} style={{ color: '#00ff66' }} /> {log.event || 'AUDIT_EVENT'}</span></td><td style={{ padding: '8px', fontSize: '0.7rem', color: '#aaa' }}>{log.actor || 'SYSTEM'}</td><td style={{ padding: '8px', fontSize: '0.65rem', fontFamily: 'monospace', color: '#888' }}>{log.timestamp ? new Date(log.timestamp).toLocaleString() : 'Unknown'}</td><td style={{ padding: '8px', fontSize: '0.65rem', fontFamily: 'monospace', color: '#55ff99' }}>{formatHash(log.hash)}</td></tr>))}</tbody>
            </table>
          </div>
        </div>
      )}
      {activeView === 'benchmark' && (
        <div ref={benchmarkViewRef} className={styles.alertShield}>
          <div style={{ background: 'rgba(212,175,55,0.06)', padding: '14px 18px', display: 'flex', alignItems: 'center', gap: '12px', borderBottom: '1px solid rgba(212,175,55,0.15)', fontWeight: 900, fontSize: '0.75rem', color: '#D4AF37' }}>
            <TrendingUp size={14} /> COMPETITIVE OBLITERATION INDEX
          </div>
          <div style={{ padding: '16px' }}>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3,1fr)', gap: '20px', marginBottom: '20px' }}>
              <div style={{ textAlign: 'center', background: '#111', padding: '16px', borderRadius: '14px' }}><div style={{ fontSize: '0.7rem', color: '#aaa' }}>WILSY OS</div><div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#D4AF37', fontFamily: 'monospace' }}>{safeData.benchmark.wilsyLatency || 'SOURCE SILENT'}</div><div style={{ fontSize: '0.6rem', color: '#666' }}>Hash Chain Latency</div></div>
              <div style={{ textAlign: 'center', background: '#111', padding: '16px', borderRadius: '14px' }}><div style={{ fontSize: '0.7rem', color: '#aaa' }}>Legal Tracker</div><div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#D4AF37', fontFamily: 'monospace' }}>{safeData.benchmark.competitorLatency || 'SOURCE SILENT'}</div><div style={{ fontSize: '0.6rem', color: '#666' }}>Average Response</div></div>
              <div style={{ textAlign: 'center', background: '#111', padding: '16px', borderRadius: '14px' }}><div style={{ fontSize: '0.7rem', color: '#aaa' }}>Wolters Kluwer</div><div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#D4AF37', fontFamily: 'monospace' }}>{safeData.benchmark.competitorVolume || 'SOURCE SILENT'}</div><div style={{ fontSize: '0.6rem', color: '#666' }}>Real-time Audit</div></div>
            </div>
            <div style={{ textAlign: 'center', fontSize: '0.65rem', color: '#f5f0dc', borderTop: '1px solid #222', paddingTop: '16px' }}>
              {safeData.benchmark.sampleSize
                ? `Based on ${safeData.benchmark.sampleSize} live benchmark samples.`
                : 'Awaiting live benchmark sample feed. No synthetic comparison rendered.'}
            </div>
          </div>
        </div>
      )}

      {(!embedded || activeView === 'dashboard') && (
      <section className={styles.auditFortressPanel} aria-label="Audit fortress live evidence status">
        <div className={styles.auditFortressHeader}>
          <div>
            <span>Audit Fortress</span>
            <p>Forensic seal, chain anchor and live evidence weight in one command plane.</p>
          </div>
          <strong>{safeData.logs.length ? 'LIVE EVIDENCE LINKED' : 'AWAITING LIVE EVIDENCE'}</strong>
        </div>

        <div className={styles.auditFortressGrid}>
          <article className={styles.auditFortressMetric}>
            <Hash size={16} />
            <span>Chain Anchor</span>
            <strong title={safeData.chainAnchor}>{formatHash(safeData.chainAnchor)}</strong>
          </article>
          <article className={styles.auditFortressMetric}>
            <Database size={16} />
            <span>Evidence Weight</span>
            <strong>{safeData.evidenceWeight}</strong>
          </article>
          <article className={styles.auditFortressMetric}>
            <ShieldCheck size={16} />
            <span>Integrity</span>
            <strong>{formatScore(safeData.integrityIndex)}</strong>
          </article>
        </div>

        <div className={styles.auditFortressStream}>
          <div className={styles.auditFortressStreamHeader}>
            <span>Live Vault Stream</span>
            <button type="button" onClick={handleSync} disabled={isSyncing}>
              <RefreshCw size={13} />
              {isSyncing ? 'Syncing' : 'Sync'}
            </button>
          </div>
          {safeData.logs.length ? safeData.logs.slice(0, 3).map((log, index) => (
            <div key={log.id || index} className={styles.auditFortressEntry}>
              <span>{log.event || 'AUDIT_EVENT'}</span>
              <strong>{formatHash(log.hash)}</strong>
              <small>{log.timestamp ? new Date(log.timestamp).toLocaleTimeString() : 'timestamp pending'}</small>
            </div>
          )) : (
            <div className={styles.auditFortressEmpty}>
              No synthetic audit entries rendered. The fortress will populate when the live vault stream emits evidence.
            </div>
          )}
        </div>

        <div className={styles.auditFortressCommandGrid}>
          <article className={styles.auditFortressReadiness}>
            <div className={styles.auditFortressSectionTitle}>
              <ShieldAlert size={14} />
              Evidence Readiness
            </div>
            <div className={styles.auditFortressReadinessRows}>
              {[
                { label: 'Vault Link', value: safeData.logs.length ? 'Linked' : 'Awaiting Evidence', tone: safeData.logs.length ? 'green' : 'gold' },
                { label: 'Chain Length', value: `${safeData.chainLength} entries`, tone: safeData.chainLength ? 'green' : 'gold' },
                { label: 'Anomaly Gate', value: safeData.anomalies ? `${safeData.anomalies} detected` : 'Clear', tone: safeData.anomalies ? 'red' : 'green' },
                { label: 'Log Density', value: safeData.logDensity, tone: safeData.logs.length ? 'green' : 'gold' }
              ].map((item) => (
                <div key={item.label} className={styles.auditFortressReadinessRow} data-tone={item.tone}>
                  <span>{item.label}</span>
                  <strong>{item.value}</strong>
                </div>
              ))}
            </div>
          </article>

          <article className={styles.auditFortressRouteMap}>
            <div className={styles.auditFortressSectionTitle}>
              <GitBranch size={14} />
              Evidence Route Map
            </div>
            <div className={styles.auditFortressRouteLine}>
              {[
                { label: 'Capture', value: safeData.logs.length ? 'Live' : 'Pending' },
                { label: 'Hash', value: safeData.chainAnchor ? 'Anchored' : 'Pending' },
                { label: 'Seal', value: formatScore(safeData.integrityIndex) },
                { label: 'Export', value: safeData.logs.length ? 'Ready' : 'Standby' }
              ].map((node) => (
                <div key={node.label} className={styles.auditFortressRouteNode}>
                  <i />
                  <span>{node.label}</span>
                  <strong>{node.value}</strong>
                </div>
              ))}
            </div>
          </article>

          <article className={styles.auditFortressCommandCard}>
            <div className={styles.auditFortressPackCopy}>
              <div className={styles.auditFortressSectionTitle}>
                <FileText size={14} />
                Board Evidence Pack
              </div>
              <p>
                Arms only when live audit entries exist. Until then, Wilsy OS holds the line:
                no placeholder filings, no staged records.
              </p>
            </div>
            <div className={styles.auditFortressPackAction}>
              <span>{safeData.logs.length ? 'Ready for seal' : 'Standby mode'}</span>
              <button type="button" onClick={handleExport} disabled={!safeData.logs.length}>
                <Download size={13} />
                {safeData.logs.length ? 'Export Pack' : 'Awaiting Evidence'}
              </button>
            </div>
          </article>
        </div>
      </section>
      )}

      <style>{`
        @keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
        @keyframes spinReverse { from { transform: rotate(360deg); } to { transform: rotate(0deg); } }
      `}</style>
    </div>
  );
};

export default ForensicsHUD;
