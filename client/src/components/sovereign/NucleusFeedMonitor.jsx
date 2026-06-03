/* eslint-disable */
/**
 * WILSY OS - NUCLEUS FEED MONITOR
 * Absolute path: /Users/wilsonkhanyezi/legal-doc-system/client/src/components/sovereign/NucleusFeedMonitor.jsx
 *
 * Collaboration ledger:
 * - Wilson Khanyezi mandated a real operating-system feed, not a decorative panel.
 * - This version consumes live billing, compliance, forensics, telemetry stats and
 *   the event stream already passed from FounderDashboard.
 * - No synthetic operational values are rendered. Silent sources are labelled as
 *   source silent so investors can trust the cockpit.
 */

import React, { useState, useEffect, useCallback, useMemo } from 'react';
import {
  Radio,
  TerminalSquare,
  Activity,
  Cpu,
  RefreshCcw,
  ShieldCheck,
  TrendingUp,
  Database,
  AlertTriangle,
  CheckCircle2,
  Radar,
  ReceiptText,
  Server,
} from 'lucide-react';
import { useTenants } from '../../contexts/tenantContext';
import api from '../../services/api';
import styles from './NucleusFeedMonitor.module.css';

const SOURCE_SILENT = 'SOURCE SILENT';

/**
 * Extracts the canonical payload shape from Wilsy API responses.
 *
 * Collaboration: Keeps component logic free from endpoint-specific response
 * envelopes so future backend changes do not fracture the boardroom feed.
 *
 * @param {object} response - Axios response object.
 * @returns {object|Array|null} Normalised payload.
 */
const extractPayload = (response) => response?.data?.data || response?.data || null;

/**
 * Coerces a value into a finite number.
 *
 * Collaboration: Prevents UI cards from displaying false confidence when the DB
 * returns null, undefined or a non-numeric string.
 *
 * @param {*} value - Candidate numeric value.
 * @returns {number|null} Finite number or null.
 */
const coerceNumber = (value) => {
  const numeric = Number(value);
  return Number.isFinite(numeric) ? numeric : null;
};

/**
 * Reads the first available numeric value from a list of candidate keys.
 *
 * Collaboration: Wilsy services expose metrics through several historical
 * shapes, so this helper lets the monitor remain backwards compatible.
 *
 * @param {object} source - Source object.
 * @param {string[]} keys - Candidate keys.
 * @returns {number|null} First finite numeric value.
 */
const pickNumber = (source, keys = []) => {
  if (!source || typeof source !== 'object') return null;
  for (const key of keys) {
    const value = coerceNumber(source[key]);
    if (value !== null) return value;
  }
  return null;
};

/**
 * Formats a currency amount as South African Rand.
 *
 * Collaboration: The founder tenant is South African, so this keeps financial
 * truth aligned with the current operating jurisdiction.
 *
 * @param {number|null} value - Currency amount.
 * @returns {string} Display value.
 */
const formatZAR = (value) => {
  const numeric = coerceNumber(value);
  if (numeric === null) return SOURCE_SILENT;
  return new Intl.NumberFormat('en-ZA', {
    style: 'currency',
    currency: 'ZAR',
    maximumFractionDigits: 0,
  }).format(numeric);
};

/**
 * Formats a numeric percentage without inventing unavailable values.
 *
 * Collaboration: Silent percentages are more honest than fabricated precision.
 *
 * @param {number|null} value - Percentage value.
 * @returns {string} Display value.
 */
const formatPercent = (value) => {
  const numeric = coerceNumber(value);
  return numeric === null ? SOURCE_SILENT : `${numeric.toFixed(numeric % 1 ? 1 : 0)}%`;
};

/**
 * Formats latency in milliseconds.
 *
 * Collaboration: The OS should show actual latency only when telemetry supplies it.
 *
 * @param {number|null} value - Latency in ms.
 * @returns {string} Display value.
 */
const formatMs = (value) => {
  const numeric = coerceNumber(value);
  return numeric === null ? SOURCE_SILENT : `${numeric.toFixed(numeric % 1 ? 1 : 0)}ms`;
};

/**
 * Returns a tenant identifier suitable for live API calls.
 *
 * Collaboration: Founder surfaces can use MASTER, GLOBAL_ROOT or concrete tenant
 * IDs, so this keeps the monitor explicit and predictable.
 *
 * @param {object|null} activeTenant - Active tenant context.
 * @returns {string} Tenant identifier.
 */
const resolveTenantId = (activeTenant) => (
  activeTenant?.tenantId
  || activeTenant?.id
  || localStorage.getItem('wilsy_tenant_id')
  || localStorage.getItem('tenantId')
  || 'MASTER'
);

/**
 * Converts telemetry event rows into compact, real forensic feed entries.
 *
 * Collaboration: The event stream must never show filler. If the array is empty,
 * the UI says so instead of inventing drama.
 *
 * @param {Array} events - Telemetry events from FounderDashboard.
 * @returns {Array<object>} Normalised event feed.
 */
const normaliseTelemetryEvents = (events = []) => {
  if (!Array.isArray(events)) return [];
  return events.slice(0, 8).map((event, index) => {
    const type = event?.eventType || event?.type || event?.action || event?.name || 'UNCLASSIFIED_EVENT';
    const tenantId = event?.tenantId || event?.tenant || event?.shard || 'UNRESOLVED_TENANT';
    const severity = `${event?.severity || event?.level || event?.status || ''}`.toUpperCase();
    const isAlert = /ERROR|WARN|FAIL|FRACTURE|BREACH|TIMEOUT|429|500|CRITICAL/.test(`${type} ${severity}`.toUpperCase());

    return {
      id: event?._id || event?.id || event?.requestId || `EVT-${index + 1}`,
      type,
      tenantId,
      severity: isAlert ? 'ATTENTION' : 'LIVE',
      timestamp: event?.timestamp || event?.createdAt || event?.time || null,
    };
  });
};

/**
 * Normalises telemetry stats from either array or object responses.
 *
 * Collaboration: Gives the monitor a stable latency and availability contract
 * without hard-coded values.
 *
 * @param {object|Array|null} stats - Telemetry stats payload.
 * @returns {object} Normalised telemetry readings.
 */
const normaliseTelemetryStats = (stats) => {
  const rows = Array.isArray(stats) ? stats : (stats ? [stats] : []);
  const latest = rows[0] || {};
  const latency = pickNumber(latest, ['p95Latency', 'avgLatency', 'latency', 'responseTime', 'ping']);
  const availability = pickNumber(latest, ['availability', 'availabilityScore', 'uptime', 'successRate']);
  const throughput = pickNumber(latest, ['throughput', 'eventsPerMinute', 'tps', 'requestsPerMinute']);

  return {
    rows,
    latency,
    availability,
    throughput,
  };
};

/**
 * Creates a source status object from a settled promise result.
 *
 * Collaboration: The cockpit separates source connectivity from metric value,
 * which makes degraded APIs visible without corrupting live data.
 *
 * @param {PromiseSettledResult} result - Settled API result.
 * @param {string} label - Human label.
 * @returns {object} Source status.
 */
const buildSourceStatus = (result, label) => ({
  label,
  status: result?.status === 'fulfilled' ? 'LIVE' : 'DEGRADED',
  detail: result?.status === 'fulfilled'
    ? 'DB response accepted'
    : (result?.reason?.response?.status ? `HTTP ${result.reason.response.status}` : result?.reason?.message || SOURCE_SILENT),
});

/**
 * Builds live boardroom narratives from source-backed metrics only.
 *
 * Collaboration: The monitor tells the truth. It celebrates live evidence and
 * calls out silence, instead of filling the screen with placeholders.
 *
 * @param {object} params - Narrative inputs.
 * @returns {Array<object>} Narrative packets.
 */
const buildNarrativePackets = ({ activeTenant, liveMetrics, eventFeed, telemetryFacts }) => {
  const shardName = activeTenant?.name || activeTenant?.tenantId || liveMetrics.tenantId || 'Wilsy Root';
  const packets = [];

  if (liveMetrics.sources.billing.status === 'LIVE') {
    packets.push({
      title: 'Billing Nucleus',
      icon: ReceiptText,
      severity: 'LIVE',
      body: `${shardName} billing source is online. YTD recognised revenue is ${formatZAR(liveMetrics.ytdRevenue)} and outstanding receivables are ${formatZAR(liveMetrics.outstandingReceivables)}.`,
    });
  } else {
    packets.push({
      title: 'Billing Nucleus',
      icon: ReceiptText,
      severity: 'DEGRADED',
      body: `Billing source is not currently returning live metrics. Reason: ${liveMetrics.sources.billing.detail}. No synthetic revenue is rendered.`,
    });
  }

  if (liveMetrics.integrityScore !== null || liveMetrics.complianceScore !== null) {
    packets.push({
      title: 'Compliance Spine',
      icon: ShieldCheck,
      severity: 'LIVE',
      body: `Compliance and forensic evidence are connected. Integrity is ${formatPercent(liveMetrics.integrityScore)} and compliance score is ${formatPercent(liveMetrics.complianceScore)}.`,
    });
  } else {
    packets.push({
      title: 'Compliance Spine',
      icon: ShieldCheck,
      severity: 'DEGRADED',
      body: 'Compliance and forensic metrics are silent. The cockpit refuses to manufacture a confidence score.',
    });
  }

  if (eventFeed.length) {
    const alertCount = eventFeed.filter((event) => event.severity === 'ATTENTION').length;
    packets.push({
      title: 'Forensic Pulse',
      icon: Radar,
      severity: alertCount ? 'ATTENTION' : 'LIVE',
      body: `${eventFeed.length} live telemetry events are loaded from the founder stream. ${alertCount} event${alertCount === 1 ? '' : 's'} require attention.`,
    });
  } else {
    packets.push({
      title: 'Forensic Pulse',
      icon: Radar,
      severity: 'SOURCE_SILENT',
      body: 'No telemetry events are currently supplied to this monitor. The stream remains empty by design until the DB or API sends evidence.',
    });
  }

  if (telemetryFacts.latency !== null || telemetryFacts.availability !== null) {
    packets.push({
      title: 'Latency Command',
      icon: Activity,
      severity: 'LIVE',
      body: `Telemetry stats report latency at ${formatMs(telemetryFacts.latency)} with availability at ${formatPercent(telemetryFacts.availability)}.`,
    });
  }

  return packets;
};

/**
 * Renders the live Nucleus Feed Monitor.
 *
 * Collaboration: This is the founder cockpit heartbeat. It must be operational,
 * source-backed and explicit about degraded sources.
 *
 * @param {object} props - Component props.
 * @param {Array} props.events - Live telemetry events from FounderDashboard.
 * @param {object|Array|null} props.stats - Live telemetry stats from FounderDashboard.
 * @returns {JSX.Element} Live monitoring panel.
 */
const NucleusFeedMonitor = ({ events = [], stats = null }) => {
  const { activeTenant } = useTenants();
  const [activeNarrativeIndex, setActiveNarrativeIndex] = useState(0);
  const [lastSyncTimestamp, setLastSyncTimestamp] = useState(null);
  const [isFetching, setIsFetching] = useState(false);
  const [liveMetrics, setLiveMetrics] = useState({
    tenantId: 'MASTER',
    ytdRevenue: null,
    outstandingReceivables: null,
    integrityScore: null,
    complianceScore: null,
    statutoryDrift: null,
    sources: {
      billing: { label: 'Billing', status: SOURCE_SILENT, detail: SOURCE_SILENT },
      compliance: { label: 'Compliance', status: SOURCE_SILENT, detail: SOURCE_SILENT },
      forensics: { label: 'Forensics', status: SOURCE_SILENT, detail: SOURCE_SILENT },
      telemetry: { label: 'Telemetry', status: SOURCE_SILENT, detail: SOURCE_SILENT },
    },
  });

  const tenantId = resolveTenantId(activeTenant);
  const eventFeed = useMemo(() => normaliseTelemetryEvents(events), [events]);
  const propTelemetryFacts = useMemo(() => normaliseTelemetryStats(stats), [stats]);
  const telemetryFacts = useMemo(() => ({
    ...propTelemetryFacts,
    latency: propTelemetryFacts.latency ?? liveMetrics.telemetryFacts?.latency ?? null,
    availability: propTelemetryFacts.availability ?? liveMetrics.telemetryFacts?.availability ?? null,
    throughput: propTelemetryFacts.throughput ?? liveMetrics.telemetryFacts?.throughput ?? null,
  }), [propTelemetryFacts, liveMetrics.telemetryFacts]);

  /**
   * Fetches source-backed nucleus metrics from live Wilsy APIs.
   *
   * Collaboration: Pulls multiple sources in parallel and marks partial failure
   * instead of crashing the founder command centre.
   *
   * @returns {Promise<void>} Resolves after source hydration.
   */
  const fetchLiveMetrics = useCallback(async () => {
    setIsFetching(true);

    const resolvedTenantId = resolveTenantId(activeTenant);
    const token = localStorage.getItem('wilsy_auth_token');
    const requestConfig = token ? { headers: { Authorization: `Bearer ${token}` } } : {};

    const [
      billingResult,
      complianceResult,
      forensicsResult,
      telemetryResult,
    ] = await Promise.allSettled([
      api.get('/billing/institutional/summary', { ...requestConfig, params: { tenantId: resolvedTenantId } }),
      api.get(`/compliance/metrics/${resolvedTenantId}`, requestConfig),
      api.get(`/forensics/metrics/${resolvedTenantId}`, requestConfig),
      api.get(`/telemetry/${resolvedTenantId}/stats`, requestConfig),
    ]);

    const billing = billingResult.status === 'fulfilled' ? extractPayload(billingResult.value) : null;
    const compliance = complianceResult.status === 'fulfilled' ? extractPayload(complianceResult.value) : null;
    const forensics = forensicsResult.status === 'fulfilled' ? extractPayload(forensicsResult.value) : null;
    const telemetry = telemetryResult.status === 'fulfilled' ? extractPayload(telemetryResult.value) : null;
    const telemetryPayloadFacts = normaliseTelemetryStats(telemetry);

    setLiveMetrics({
      tenantId: resolvedTenantId,
      ytdRevenue: pickNumber(billing?.metrics, ['ytdRevenue', 'totalRevenue', 'arr'])
        ?? pickNumber(billing, ['ytdRevenue', 'totalRevenue', 'arr', 'annualRecurringRevenue']),
      outstandingReceivables: pickNumber(billing?.metrics, ['outstandingReceivables', 'pendingPayments', 'outstanding'])
        ?? pickNumber(billing, ['outstandingReceivables', 'pendingPayments', 'outstanding']),
      integrityScore: pickNumber(forensics, ['integrityIndex', 'chainIntegrity', 'integrity', 'score'])
        ?? pickNumber(forensics?.metrics, ['integrityIndex', 'chainIntegrity', 'integrity', 'score']),
      complianceScore: pickNumber(compliance, ['score', 'ratio', 'adherence', 'complianceScore'])
        ?? pickNumber(compliance?.metrics, ['score', 'ratio', 'adherence', 'complianceScore']),
      statutoryDrift: pickNumber(compliance, ['statutoryDrift', 'driftIndex', 'drift'])
        ?? pickNumber(compliance?.metrics, ['statutoryDrift', 'driftIndex', 'drift']),
      telemetryFacts: telemetryPayloadFacts,
      sources: {
        billing: buildSourceStatus(billingResult, 'Billing'),
        compliance: buildSourceStatus(complianceResult, 'Compliance'),
        forensics: buildSourceStatus(forensicsResult, 'Forensics'),
        telemetry: buildSourceStatus(telemetryResult, 'Telemetry'),
      },
    });
    setLastSyncTimestamp(new Date().toISOString());
    setIsFetching(false);
  }, [activeTenant]);

  const narrativePackets = useMemo(() => buildNarrativePackets({
    activeTenant,
    liveMetrics,
    eventFeed,
    telemetryFacts,
  }), [activeTenant, liveMetrics, eventFeed, telemetryFacts]);

  const activeNarrative = narrativePackets[activeNarrativeIndex] || narrativePackets[0];
  const ActiveNarrativeIcon = activeNarrative?.icon || Activity;

  const sourceRows = useMemo(() => Object.values(liveMetrics.sources), [liveMetrics.sources]);

  useEffect(() => {
    fetchLiveMetrics();
    const metricsInterval = setInterval(fetchLiveMetrics, 45000);
    return () => clearInterval(metricsInterval);
  }, [fetchLiveMetrics]);

  useEffect(() => {
    const narrativeInterval = setInterval(() => {
      setActiveNarrativeIndex((previous) => (previous + 1) % Math.max(narrativePackets.length, 1));
    }, 12000);
    return () => clearInterval(narrativeInterval);
  }, [narrativePackets.length]);

  useEffect(() => {
    setActiveNarrativeIndex(0);
  }, [tenantId]);

  return (
    <section className={styles.nucleusMonitor} aria-label="Nucleus feed monitor">
      <header className={styles.headerBar}>
        <div className={styles.headerTitle}>
          <TerminalSquare size={16} aria-hidden="true" />
          <div>
            <span>SYSTEM CORE</span>
            <strong>Nucleus Feed Monitor</strong>
          </div>
        </div>
        <div className={styles.headerState}>
          <span className={isFetching ? styles.syncing : styles.online}>
            {isFetching ? 'SYNCING SOURCES' : 'LIVE EVIDENCE MODE'}
          </span>
          <button
            type="button"
            className={styles.refreshButton}
            onClick={fetchLiveMetrics}
            disabled={isFetching}
            title="Refresh live nucleus sources"
          >
            <RefreshCcw size={13} className={isFetching ? styles.spin : ''} aria-hidden="true" />
            Refresh
          </button>
        </div>
      </header>

      <div className={styles.identityGrid}>
        <article className={styles.identityCard}>
          <Radio size={15} aria-hidden="true" />
          <span>Feed Identity</span>
          <strong>NUCLEUS_FEED_V47</strong>
          <small>Commonwealth English | zero synthetic telemetry</small>
        </article>
        <article className={styles.identityCard}>
          <Cpu size={15} aria-hidden="true" />
          <span>Shard Cluster</span>
          <strong>{tenantId}</strong>
          <small>{activeTenant?.name || 'Wilsy OS Root'} | source-backed</small>
        </article>
        <article className={styles.identityCard}>
          <Database size={15} aria-hidden="true" />
          <span>Last Hydration</span>
          <strong>{lastSyncTimestamp ? new Date(lastSyncTimestamp).toLocaleTimeString('en-GB') : SOURCE_SILENT}</strong>
          <small>DB/API response timestamp</small>
        </article>
      </div>

      <div className={styles.metricStrip} aria-label="Live nucleus metrics">
        <article className={styles.metricCard}>
          <ShieldCheck size={16} aria-hidden="true" />
          <span>Integrity</span>
          <strong>{formatPercent(liveMetrics.integrityScore)}</strong>
        </article>
        <article className={styles.metricCard}>
          <Activity size={16} aria-hidden="true" />
          <span>Latency</span>
          <strong>{formatMs(telemetryFacts.latency)}</strong>
        </article>
        <article className={styles.metricCard}>
          <TrendingUp size={16} aria-hidden="true" />
          <span>YTD Revenue</span>
          <strong>{formatZAR(liveMetrics.ytdRevenue)}</strong>
        </article>
        <article className={styles.metricCard}>
          <Server size={16} aria-hidden="true" />
          <span>Events</span>
          <strong>{eventFeed.length}</strong>
        </article>
      </div>

      <div className={styles.commandGrid}>
        <article className={styles.narrativePanel}>
          <div className={styles.panelKicker}>
            <ActiveNarrativeIcon size={15} aria-hidden="true" />
            <span>{activeNarrative?.title || 'Nucleus Narrative'}</span>
            <b className={styles[`${(activeNarrative?.severity || 'LIVE').toLowerCase()}Pill`] || styles.livePill}>
              {activeNarrative?.severity || 'LIVE'}
            </b>
          </div>
          <p>{activeNarrative?.body || 'Awaiting live nucleus evidence.'}</p>
          <div className={styles.narrativeCounter}>
            {activeNarrativeIndex + 1}/{narrativePackets.length}
          </div>
        </article>

        <article className={styles.sourceMatrix}>
          <div className={styles.panelKicker}>
            <CheckCircle2 size={15} aria-hidden="true" />
            <span>Source Integrity Matrix</span>
          </div>
          <div className={styles.sourceRows}>
            {sourceRows.map((source) => (
              <div key={source.label} className={styles.sourceRow}>
                <span>{source.label}</span>
                <strong className={source.status === 'LIVE' ? styles.goodText : styles.warnText}>{source.status}</strong>
                <small>{source.detail}</small>
              </div>
            ))}
          </div>
        </article>
      </div>

      <article className={styles.eventTape}>
        <div className={styles.panelKicker}>
          <Radar size={15} aria-hidden="true" />
          <span>Live Forensic Event Tape</span>
        </div>
        {eventFeed.length ? (
          <div className={styles.eventRows}>
            {eventFeed.map((event) => (
              <div key={event.id} className={styles.eventRow}>
                <span>{event.type}</span>
                <strong className={event.severity === 'ATTENTION' ? styles.warnText : styles.goodText}>
                  {event.severity}
                </strong>
                <small>{event.tenantId} | {event.timestamp ? new Date(event.timestamp).toLocaleTimeString('en-GB') : SOURCE_SILENT}</small>
              </div>
            ))}
          </div>
        ) : (
          <div className={styles.silentState}>
            <AlertTriangle size={18} aria-hidden="true" />
            <span>No live telemetry events supplied. Placeholder stream disabled.</span>
          </div>
        )}
      </article>
    </section>
  );
};

export default NucleusFeedMonitor;
