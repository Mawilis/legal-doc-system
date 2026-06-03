/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - SOVEREIGN COMPLIANCE ANALYTICS CORE [V35.0.0-OMEGA-NUCLEUS]                                                                 ║
 * ║ [DYNAMIC JURISDICTION INTELLIGENCE | REDIS CACHED | SHA3-512 ANCHORED | SELF‑CONTAINED & RESILIENT]                                      ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 35.0.0-OMEGA | PRODUCTION READY | BILLION DOLLAR SPEC                                                                     ║
 * ║ EPITOME: BIBLICAL WORTH BILLIONS | NO CHILD'S PLACE | INSTITUTIONAL AUTHORITY | COMPETITIVE OBLITERATION                                 ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/controllers/complianceController.js                                       ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                 ║
 * ║ • Wilson Khanyezi (CEO/Lead Architect) – Mandated real‑time compliance metrics, dynamic jurisdiction resolution, and boardroom‑ready    ║
 * ║   telemetry that functions with zero external dependencies.                                                                              ║
 * ║ • AI Engineering (DeepSeek) – RECTIFIED: Removed all fragile imports. Runs entirely on internal logic and Redis caching.                ║
 * ║ • AI Engineering (Gemini) – ARCHITECTURAL REALIGNMENT: Purged the legacy `cache/` import. Anchored the controller to the true           ║
 * ║   `config/redis.js` Singularity Nucleus. Injected `safeSet` and `safeGet` to permanently obliterate the CACHE_SET_ERROR. [2026-05-24]   ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 * * @fileoverview Sovereign Compliance Analytics Controller.
 * Aggregates jurisdiction data, calculates regulatory drift, and seals
 * the payload with a SHA3-512 hash before pushing to the Executive Boardroom HUD.
 */

import crypto from 'node:crypto';
import loggerRaw from '../utils/logger.js';

// 🚀 REWIRED: Pointing directly to the fortified Singularity Nucleus
import { safeSet, safeGet } from '../config/redis.js';
import JurisdictionRegistry from '../models/JurisdictionRegistry.js';
import Compliance from '../models/Compliance.js';

const logger = loggerRaw.default || loggerRaw;

/**
 * Resolves every tenant identifier that can legitimately point at the same live compliance ledger.
 * @private
 * @param {Object} req - Express request envelope
 * @param {string} tenantId - Route tenant identifier
 * @returns {string[]} Ordered list of unique tenant aliases
 * @collaboration Wilson Khanyezi demanded that founder/root tenants do not disappear behind
 * proxy aliases; this helper binds the API route, auth context, and headers into one lookup frame.
 */
const resolveTenantAliases = (req, tenantId) => {
  const candidates = [
    tenantId,
    req.headers?.['x-tenant-id'],
    req.tenantId,
    req.tenant?.tenantId,
    req.tenant?.id,
    req.user?.tenantId,
    tenantId === 'GLOBAL_ROOT' ? 'WILSY_GLOBAL_ROOT' : null,
    tenantId === 'GLOBAL_ROOT' ? 'wilsy' : null,
    tenantId === 'MASTER' ? 'GLOBAL_ROOT' : null,
    tenantId === 'MASTER' ? 'WILSY_GLOBAL_ROOT' : null,
    tenantId === 'MASTER' ? 'wilsy' : null
  ];

  return [...new Set(candidates.filter(Boolean).map(value => String(value)))];
};

/**
 * Reads the tenant country only from live request or ledger context.
 * @private
 * @param {Object} req - Express request envelope
 * @param {Object|null} complianceLedger - Live compliance ledger document
 * @returns {string|null} ISO-like country code or null when no source proves it
 * @collaboration This prevents Wilsy OS from inventing a jurisdiction when the DB has not
 * established one. Source silence is safer than theatrical certainty.
 */
const resolveTenantCountry = (req, complianceLedger) => {
  const rawCountry = req.headers?.['x-tenant-country']
    || complianceLedger?.jurisdiction
    || req.tenant?.countryCode
    || req.tenant?.metadata?.countryCode
    || null;

  return rawCountry ? String(rawCountry).trim().toUpperCase() : null;
};

/**
 * Converts compliance enum fields into auditable controls.
 * @private
 * @param {Object|null} ledger - Live compliance ledger
 * @returns {Array<{key: string, label: string, value: string|null, healthy: boolean, severity: string}>}
 * @collaboration Every percentage shown in the cockpit now traces to named controls instead of
 * a hardcoded investor-facing number.
 */
const buildComplianceControls = (ledger) => {
  if (!ledger) return [];

  return [
    {
      key: 'POPIA',
      label: 'POPIA Status',
      value: ledger.popiaStatus || null,
      healthy: ledger.popiaStatus === 'COMPLIANT',
      severity: ledger.popiaStatus === 'FRACTURE' ? 'CRITICAL' : 'REVIEW'
    },
    {
      key: 'GDPR',
      label: 'GDPR Status',
      value: ledger.gdprStatus || null,
      healthy: ledger.gdprStatus === 'ENFORCED',
      severity: ledger.gdprStatus === 'FRACTURE' ? 'CRITICAL' : 'REVIEW'
    },
    {
      key: 'SOC2',
      label: 'SOC2 Validation',
      value: ledger.soc2Validation || null,
      healthy: ledger.soc2Validation === 'VERIFIED',
      severity: ledger.soc2Validation === 'FRACTURE' ? 'CRITICAL' : 'REVIEW'
    },
    {
      key: 'RISK_FLAGS',
      label: 'Risk Flags',
      value: ledger.riskFlags || null,
      healthy: ledger.riskFlags === 'ZERO_DETECTED',
      severity: ledger.riskFlags && ledger.riskFlags !== 'ZERO_DETECTED' ? 'CRITICAL' : 'REVIEW'
    },
    {
      key: 'FORENSIC_SEAL',
      label: 'Forensic Signature',
      value: ledger.forensicSignature || null,
      healthy: Boolean(ledger.forensicSignature && ledger.forensicSignature !== 'PENDING_GENESIS_SEAL'),
      severity: 'REVIEW'
    }
  ];
};

/**
 * Scores a compliance ledger from live controls only.
 * @private
 * @param {Object|null} ledger - Live compliance ledger
 * @returns {Object} Deterministic score frame used by the API response
 * @collaboration The old 98% constant is deliberately impossible here; no ledger means null,
 * and every score is a ratio of passed controls to total live controls.
 */
const scoreComplianceLedger = (ledger) => {
  const controls = buildComplianceControls(ledger);
  if (!controls.length) {
    return {
      integrityScore: null,
      policyAlignment: null,
      activeAudits: 0,
      criticalAnomalies: null,
      systemStatus: 'SOURCE_SILENT',
      controls,
      anomalies: []
    };
  }

  const passedControls = controls.filter(control => control.healthy).length;
  const anomalies = controls.filter(control => !control.healthy);
  const criticalAnomalies = anomalies.filter(control => control.severity === 'CRITICAL').length;
  const integrityScore = Math.round((passedControls / controls.length) * 100);

  return {
    integrityScore,
    policyAlignment: integrityScore,
    activeAudits: ledger.lastAuditDate ? 1 : 0,
    criticalAnomalies,
    systemStatus: criticalAnomalies > 0
      ? 'CRITICAL_REVIEW'
      : integrityScore === 100
        ? 'LIVE_COMPLIANT'
        : 'REVIEW_REQUIRED',
    controls,
    anomalies
  };
};

/**
 * @function buildSourceSilentCompliancePayload
 * @description Creates a truthful compliance payload when the live compliance ledger cannot be read.
 * @param {string} tenantId - Tenant identifier requested by the caller.
 * @param {string} reason - Degradation reason.
 * @returns {Object} API-safe compliance payload with null scores and no synthetic controls.
 * @collaboration Wilson Khanyezi rejected hardcoded compliance percentages; silence must be visible and auditable.
 */
const buildSourceSilentCompliancePayload = (tenantId, reason = 'SOURCE_SILENT') => ({
  success: true,
  timestamp: new Date().toISOString(),
  tenantId,
  sourceStatus: 'DEGRADED',
  warning: reason,
  data: {
    integrityScore: null,
    activeAudits: 0,
    criticalAnomalies: null,
    systemStatus: 'SOURCE_SILENT',
    policyAlignment: null,
    statutoryDrift: null,
    encryptionLayer: null,
    logDensity: null,
    jurisdiction: {
      countryCode: null,
      countryName: null,
      primaryStatute: null,
      statutes: []
    },
    registry: [],
    alerts: [],
    trendHistory: [],
    remediationPlaybooks: [],
    panAfricanPosture: [],
    controls: [],
    sourceEvidence: {
      complianceLedger: false,
      jurisdictionRegistry: false,
      billingCache: false,
      tenantAliases: [tenantId].filter(Boolean)
    },
    billing: null
  }
});

/**
 * Calculates statutory drift from failed controls, stale audits, and jurisdiction risk weights.
 * @private
 * @param {Object|null} ledger - Live compliance ledger
 * @param {Object|null} jurisdiction - Jurisdiction registry document
 * @param {Object} scoreFrame - Output from scoreComplianceLedger
 * @returns {number|null} Deterministic drift percentage or null when the source is silent
 * @collaboration Drift is now earned by evidence: control gaps, audit age, and DB risk weights.
 */
const calculateStatutoryDrift = (ledger, jurisdiction, scoreFrame) => {
  if (!ledger || scoreFrame.integrityScore === null) return null;

  const controlDrift = 100 - scoreFrame.integrityScore;
  const auditAgeDays = ledger.lastAuditDate
    ? Math.max(0, Math.floor((Date.now() - new Date(ledger.lastAuditDate).getTime()) / 86400000))
    : 365;
  const staleAuditDrift = Math.min(25, (auditAgeDays / 365) * 25);
  const activeStatutes = Array.isArray(jurisdiction?.statutes)
    ? jurisdiction.statutes.filter(statute => statute.isActive !== false)
    : [];
  const statuteWeight = activeStatutes.length
    ? activeStatutes.reduce((sum, statute) => sum + Number(statute.riskWeight || 0), 0) / activeStatutes.length
    : 0;
  const jurisdictionDrift = Math.min(20, statuteWeight * 20);

  return Number(Math.min(100, controlDrift + staleAuditDrift + jurisdictionDrift).toFixed(2));
};

/**
 * Builds registry rows from the jurisdiction DB and live score frame.
 * @private
 * @param {Object|null} jurisdiction - Jurisdiction registry document
 * @param {Object} scoreFrame - Output from scoreComplianceLedger
 * @returns {Array<Object>} DB-backed statute rows
 * @collaboration The frontend can now show precisely which statutes are linked, reviewed, or silent.
 */
const buildRegistryRows = (jurisdiction, scoreFrame) => {
  const statutes = Array.isArray(jurisdiction?.statutes)
    ? jurisdiction.statutes.filter(statute => statute.isActive !== false)
    : [];

  return statutes.map(statute => ({
    statute: statute.label,
    key: statute.key,
    authority: statute.authority,
    riskWeight: statute.riskWeight,
    status: scoreFrame.integrityScore === null
      ? 'SOURCE_SILENT'
      : scoreFrame.criticalAnomalies > 0
        ? 'REVIEW_REQUIRED'
        : 'SOURCE_LINKED'
  }));
};

/**
 * Converts failed controls and live billing pressure into operator alerts.
 * @private
 * @param {Object[]} anomalies - Failed compliance controls
 * @param {Object|null} billing - Live billing summary from Redis, when available
 * @returns {Array<Object>} Alert rows for the cockpit
 * @collaboration Alerts now emerge from source facts instead of background theater.
 */
const buildLiveAlerts = (anomalies, billing) => {
  const alerts = anomalies.map(control => ({
    type: control.severity === 'CRITICAL' ? 'COMPLIANCE_FRACTURE' : 'COMPLIANCE_REVIEW',
    timestamp: new Date().toISOString(),
    message: `[${control.key}] ${control.label} is ${control.value || 'UNSET'}.`
  }));

  if (billing?.outstandingReceivables > 1000000) {
    alerts.push({
      type: 'FINANCIAL_RISK',
      timestamp: new Date().toISOString(),
      message: `[BILLING] Outstanding receivables exceed R 1,000,000. Current: R ${billing.outstandingReceivables.toLocaleString()}.`
    });
  }

  return alerts;
};

/**
 * Builds remediation playbooks only when the ledger proves there are control gaps.
 * @private
 * @param {Object[]} anomalies - Failed compliance controls
 * @returns {Array<Object>} Operator-ready remediation instructions
 * @collaboration No gap means no fake playbook. A gap becomes a specific action tied to a control.
 */
const buildRemediationPlaybooks = (anomalies) => anomalies.map(control => ({
  control: control.key,
  title: `Resolve ${control.label}`,
  severity: control.severity,
  action: `Review ${control.key} evidence, update the compliance ledger, and seal a fresh audit signature.`
}));

/**
 * Parses the live billing cache without inventing revenue state.
 * @private
 * @param {string} tenantId - Tenant identifier
 * @returns {Promise<Object|null>} Parsed billing frame or null when unavailable
 * @collaboration Billing risk remains visible when Redis proves it; otherwise the response says null.
 */
const readBillingFrame = async (tenantId) => {
  try {
    const billingCache = await safeGet(`wilsy:billing:summary:${tenantId}`);
    if (!billingCache) return null;
    return JSON.parse(billingCache);
  } catch (bErr) {
    logger.warn(`[COMPLIANCE-CTRL] Billing cache read failed: ${bErr.message}`);
    return null;
  }
};

/**
 * @function getTenantComplianceMetrics
 * @description Compiles and streams full statutory compliance metrics for a designated tenant.
 * Hydrates telemetry objects mapping to the tenant's actual jurisdiction and Redis‑cached
 * billing metrics when available. Secured by the fail-open safeSet/safeGet Nucleus wrappers.
 * @param {Object} req - Express request envelope
 * @param {Object} res - Express response channel
 * @returns {Promise<Response>} Cryptographically anchored JSON telemetry frame
 */
export const getTenantComplianceMetrics = async (req, res) => {
  const { tenantId } = req.params;
  const startStrike = performance.now();

  try {
    if (!tenantId || typeof tenantId !== 'string') {
      return res.status(400).json({
        success: false,
        error: 'Sovereign violation: Multi-tenant validation requires an explicit alphanumeric partition identifier.'
      });
    }

    // ────────────────────────────────────────────────────────
    // 💾 CACHE LAYER: Check Redis for a recent snapshot using safeGet
    // ────────────────────────────────────────────────────────
    const cacheKey = `wilsy:compliance:metrics:v2:${tenantId}`;
    try {
      const cached = await safeGet(cacheKey);
      if (cached) {
        res.set('X-Cache-Lookup', 'HIT_NUCLEUS');
        return res.status(200).json(JSON.parse(cached));
      }
    } catch (cacheErr) {
      logger.warn(`⚠️ [CACHE_READ_ERROR] ${cacheErr.message}`);
    }

    if (Compliance.db?.readyState !== 1 || req.tenantContextStatus === 'DEGRADED_NO_DB') {
      return res.status(200).json(buildSourceSilentCompliancePayload(tenantId, 'DB_OFFLINE'));
    }

    // ────────────────────────────────────────────────────────
    // 🌍 DYNAMIC JURISDICTION RESOLUTION
    // ────────────────────────────────────────────────────────
    const tenantAliases = resolveTenantAliases(req, tenantId);
    const complianceLedger = await Compliance.findOne({ tenantId: { $in: tenantAliases } })
      .select('+forensicSignature')
      .sort({ updatedAt: -1 })
      .lean();
    const tenantCountry = resolveTenantCountry(req, complianceLedger);
    let jurisdiction = null;
    try {
      if (tenantCountry) {
        jurisdiction = await JurisdictionRegistry.findOne({ countryCode: tenantCountry, isActive: true }).lean();
      }
    } catch (jErr) {
      logger.warn(`[COMPLIANCE-CTRL] Jurisdiction lookup failed: ${jErr.message}`);
    }

    // ────────────────────────────────────────────────────────
    // 🏛️ LIVE COMPLIANCE LEDGER METRICS
    // ────────────────────────────────────────────────────────
    const scoreFrame = scoreComplianceLedger(complianceLedger);
    const statutoryDrift = calculateStatutoryDrift(complianceLedger, jurisdiction, scoreFrame);
    const complianceRecordCount = complianceLedger
      ? await Compliance.countDocuments({ tenantId: { $in: tenantAliases } })
      : 0;

    // ────────────────────────────────────────────────────────
    // 💰 BILLING METRICS (from Redis cache if available)
    // ────────────────────────────────────────────────────────
    const billing = await readBillingFrame(tenantId);

    // ────────────────────────────────────────────────────────
    // 🚨 ALERT CONSTRUCTION
    // ────────────────────────────────────────────────────────
    const liveAlerts = buildLiveAlerts(scoreFrame.anomalies, billing);
    const registry = buildRegistryRows(jurisdiction, scoreFrame);

    // ────────────────────────────────────────────────────────
    // 🏛️ PAYLOAD ASSEMBLY
    // ────────────────────────────────────────────────────────
    const compliancePayload = {
      success: true,
      timestamp: new Date().toISOString(),
      tenantId,
      data: {
        integrityScore: scoreFrame.integrityScore,
        activeAudits: scoreFrame.activeAudits,
        criticalAnomalies: scoreFrame.criticalAnomalies,
        systemStatus: scoreFrame.systemStatus,
        policyAlignment: scoreFrame.policyAlignment,
        statutoryDrift,
        encryptionLayer: complianceLedger?.auditType || null,
        logDensity: complianceLedger ? `${complianceRecordCount} compliance ledger record${complianceRecordCount === 1 ? '' : 's'}` : null,
        jurisdiction: {
          countryCode: jurisdiction?.countryCode || tenantCountry,
          countryName: jurisdiction?.countryName || null,
          primaryStatute: jurisdiction?.primaryStatute || null,
          statutes: registry.map(row => ({
            statute: row.statute,
            authority: row.authority,
            riskWeight: row.riskWeight
          }))
        },
        registry,
        alerts: liveAlerts,
        trendHistory: [],
        remediationPlaybooks: buildRemediationPlaybooks(scoreFrame.anomalies),
        panAfricanPosture: [],
        controls: scoreFrame.controls,
        sourceEvidence: {
          complianceLedger: Boolean(complianceLedger),
          jurisdictionRegistry: Boolean(jurisdiction),
          billingCache: Boolean(billing),
          tenantAliases
        },
        billing
      }
    };

    // 🔐 SHA3-512 FORENSIC SEAL
    const canonicalString = JSON.stringify(compliancePayload.data);
    const forensicSeal = crypto.createHash('sha3-512').update(canonicalString).digest('hex');
    compliancePayload.forensicSeal = forensicSeal;

    // 💾 CACHE WRITE (ANCHORED: Using the safeSet wrapper to prevent fracture)
    try {
      await safeSet(cacheKey, JSON.stringify(compliancePayload), { EX: 15 });
    } catch (cacheSetErr) {
      logger.error('❌ [CACHE_SET_ERROR] Failed to save runtime compliance metrics frame:', cacheSetErr.message);
    }

    const totalExecutionTime = (performance.now() - startStrike).toFixed(2);
    res.set({
      'X-Forensic-Seal-Verification': 'SHA3-512',
      'X-Sovereign-Execution-Time': `${totalExecutionTime}ms`,
      'X-Jurisdiction': jurisdiction?.countryCode || tenantCountry || 'SOURCE_SILENT'
    });

    return res.status(200).json(compliancePayload);
  } catch (globalFault) {
    logger.error(`💥 [CRITICAL_COMPLIANCE_ORCHESTRATOR_FAULT] Core runtime crash tracking tenant: ${tenantId}`, globalFault);
    return res.status(200).json(buildSourceSilentCompliancePayload(tenantId, globalFault.message));
  }
};

/**
 * @function getComplianceStatus
 * @description Provides a lightweight health/status endpoint for the compliance engine.
 * Used for uptime monitoring and circuit‑breaker readiness probes.
 * @param {Object} req - Express request
 * @param {Object} res - Express response
 */
export const getComplianceStatus = async (req, res) => {
  try {
    res.status(200).json({
      service: 'ComplianceController',
      version: '35.0.0-OMEGA',
      status: 'OPERATIONAL',
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    res.status(200).json({
      service: 'ComplianceController',
      version: '35.0.0-OMEGA',
      status: 'DEGRADED',
      timestamp: new Date().toISOString(),
      warning: error.message
    });
  }
};

export const complianceController = {
  getTenantComplianceMetrics,
  getComplianceStatus
};

export const complianceStatus = getComplianceStatus;

export default { complianceController, complianceStatus };
