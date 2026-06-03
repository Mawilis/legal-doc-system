/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - DUNNING INTELLIGENCE ENGINE [V56.2.0-PRODUCTION-COLLECTIONS]                                                               ║
 * ║ [EVIDENCE-BACKED COLLECTIONS | CONSENT GATES | DISPUTE SUPPRESSION | QUIET-HOURS | SHA3 DUNNING PROOFS]                              ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 56.2.0-PRODUCTION-COLLECTIONS | PRODUCTION READY | LEGAL-CHAIN COLLECTIONS CONTROL                                           ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/services/DunningIntelligence.js                                      ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                    ║
 * ║ • Wilson Khanyezi (CEO/Lead Architect) - Required algorithmic empathy: accelerate cash without spam, legal shortcuts, or              ║
 * ║   relationship-destroying collection theatre.                                                                                          ║
 * ║ • AI Engineering (Codex) - ARCHITECTED: Converted dunning into a proof engine with source-aware recommendations, consent/quiet-hour    ║
 * ║   gates, dispute/legal-hold suppression, escalation doctrine, endpoint-safe dispatch, and SHA3 receipts.                               ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import { sha3_512 } from 'js-sha3';
import api from './api';
import { broadcastTelemetry } from '../utils/telemetryHelper';

export const DUNNING_INTELLIGENCE_VERSION = 'V56.2.0-PRODUCTION-COLLECTIONS';

const QUIET_HOURS = Object.freeze({ start: 21, end: 8 });
const DUNNING_BACKOFF_MS = 5 * 60 * 1000;

const RECOMMENDATION_ENDPOINTS = Object.freeze([
  tenantId => `/dunning/recommendations/${tenantId}`,
  tenantId => `/collections/dunning/recommendations/${tenantId}`,
  tenantId => `/collections/delinquent-list/${tenantId}`
]);

const RISK_ENDPOINTS = Object.freeze([
  (tenantId, clientId) => `/collections/risk-profile/${tenantId}/${clientId}`,
  (tenantId, clientId) => `/dunning/risk-profile/${tenantId}/${clientId}`
]);

const DISPATCH_ENDPOINTS = Object.freeze([
  () => '/collections/dunning/execute',
  () => '/dunning/intervention/execute',
  () => '/finance/collections/dunning/execute'
]);

export const DUNNING_POSTURE_MATRIX = Object.freeze({
  MONITOR: {
    stage: 'MONITOR',
    channelPriority: ['EMAIL'],
    tone: 'ACCOUNT_MONITORING',
    toneColor: '#00ff88',
    retryIntervalHours: 72,
    nextAction: 'Monitor account and preserve clean payment evidence.',
    legalPosture: 'NO_COLLECTION_ACTION'
  },
  SOFT_REMINDER: {
    stage: 'SOFT_REMINDER',
    channelPriority: ['EMAIL', 'PORTAL'],
    tone: 'COURTEOUS_OPERATIONAL',
    toneColor: '#ffaa33',
    retryIntervalHours: 48,
    nextAction: 'Send polite reminder with invoice copy, statement link, and payment route.',
    legalPosture: 'CUSTOMER_SUCCESS_COLLECTIONS'
  },
  STRUCTURED_DUNNING: {
    stage: 'STRUCTURED_DUNNING',
    channelPriority: ['EMAIL', 'SMS', 'PORTAL'],
    tone: 'PROFESSIONAL_URGENT',
    toneColor: '#D4AF37',
    retryIntervalHours: 24,
    nextAction: 'Send structured dunning notice with settlement link and proof-of-payment request.',
    legalPosture: 'FORMAL_COLLECTIONS_NOTICE'
  },
  FINAL_DEMAND: {
    stage: 'FINAL_DEMAND',
    channelPriority: ['EMAIL', 'PORTAL', 'PHONE'],
    tone: 'FIRM_FINAL_DEMAND',
    toneColor: '#D4AF37',
    retryIntervalHours: 72,
    nextAction: 'Issue final demand, freeze concessions, and require payment or dispute evidence.',
    legalPosture: 'PRE_LEGAL_COLLECTIONS'
  },
  LEGAL_REVIEW: {
    stage: 'LEGAL_REVIEW',
    channelPriority: ['SECURE_PORTAL', 'EMAIL'],
    tone: 'LEGAL_REVIEW_REQUIRED',
    toneColor: '#ff6666',
    retryIntervalHours: 0,
    nextAction: 'Generate sealed statement and route to legal review before any demand notice is dispatched.',
    legalPosture: 'LEGAL_GATE_REQUIRED'
  }
});

/**
 * @function stableStringify
 * @description Serializes values with deterministic key order for repeatable dunning proof hashes.
 * @param {unknown} value - Value to serialize.
 * @returns {string} Canonical JSON string.
 */
export const stableStringify = (value) => {
  if (typeof value === 'undefined') return 'null';
  if (value instanceof Date) return JSON.stringify(value.toISOString());
  if (value === null || typeof value !== 'object') return JSON.stringify(value);
  if (Array.isArray(value)) return `[${value.map(item => stableStringify(item)).join(',')}]`;
  return `{${Object.keys(value).sort().map(key => `${JSON.stringify(key)}:${stableStringify(value[key])}`).join(',')}}`;
};

/**
 * @function createDunningProofHash
 * @description Creates a SHA3-512 digest over a canonical dunning packet.
 * @param {Object} payload - Payload to seal.
 * @returns {string} Uppercase SHA3-512 digest.
 */
export const createDunningProofHash = (payload) => sha3_512(stableStringify(payload)).toUpperCase();

/**
 * @function normalizeApiPayload
 * @description Normalizes mixed Wilsy API response envelopes.
 * @param {Object} response - Axios response or raw payload.
 * @returns {Object|Array|null} Normalized payload.
 */
const normalizeApiPayload = (response) => response?.data?.data || response?.data || response || null;

/**
 * @function normalizeArray
 * @description Extracts array rows from common API envelope shapes.
 * @param {unknown} value - Candidate payload.
 * @returns {Array<Object>} Normalized rows.
 */
export const normalizeArray = (value) => {
  if (Array.isArray(value)) return value;
  if (Array.isArray(value?.recommendations)) return value.recommendations;
  if (Array.isArray(value?.accounts)) return value.accounts;
  if (Array.isArray(value?.invoices)) return value.invoices;
  if (Array.isArray(value?.items)) return value.items;
  if (Array.isArray(value?.data)) return value.data;
  return [];
};

/**
 * @function normalizeCurrencyAmount
 * @description Converts mixed amount fields into a finite number.
 * @param {Object} row - Source row.
 * @returns {number} Amount.
 */
const normalizeCurrencyAmount = (row = {}) => Number(
  row.amount
  ?? row.outstandingAmount
  ?? row.balance
  ?? row.totalAmount
  ?? row.exposure
  ?? 0
) || 0;

/**
 * @function deriveOverdueDays
 * @description Computes overdue days from explicit fields or a due date.
 * @param {Object} row - Source row.
 * @returns {number} Days overdue.
 */
export const deriveOverdueDays = (row = {}) => {
  const explicit = Number(row.overdueDays ?? row.dueDays ?? row.daysOverdue);
  if (Number.isFinite(explicit) && explicit >= 0) return Math.round(explicit);
  const dueDate = row.dueDate ? new Date(row.dueDate) : null;
  if (!dueDate || Number.isNaN(dueDate.getTime())) return 0;
  return Math.max(0, Math.floor((Date.now() - dueDate.getTime()) / 86400000));
};

/**
 * @function normalizeRiskScore
 * @description Normalizes risk fields into a 0-100 score.
 * @param {Object} row - Source row.
 * @param {number} overdueDays - Days overdue.
 * @returns {number} Risk score.
 */
export const normalizeRiskScore = (row = {}, overdueDays = 0) => {
  const raw = Number(row.riskScore ?? row.risk ?? row.creditRisk ?? row.churnProbability);
  if (Number.isFinite(raw)) return Math.max(0, Math.min(100, raw <= 1 ? raw * 100 : raw));
  const status = String(row.status || '').toUpperCase();
  const statusBoost = status === 'LEGAL_HOLD' ? 95 : status === 'DISPUTED' ? 80 : status === 'OVERDUE' ? 55 : 20;
  return Math.max(0, Math.min(100, statusBoost + Math.min(35, overdueDays)));
};

/**
 * @function normalizeAccount
 * @description Converts API, invoice, or ledger-risk rows into a dunning account candidate.
 * @param {Object} row - Source row.
 * @param {Object} defaults - Default tenant/source values.
 * @returns {Object} Normalized dunning account.
 */
export const normalizeAccount = (row = {}, defaults = {}) => {
  const overdueDays = deriveOverdueDays(row);
  const riskScore = normalizeRiskScore(row, overdueDays);
  const channelConsent = row.channelConsent || row.consent || {};
  return {
    id: row.id || row.invoiceId || row.reference || `DUN-${defaults.index ?? Date.now()}`,
    invoiceId: row.invoiceId || row.id || row.reference || null,
    tenantId: row.tenantId || defaults.tenantId || 'GLOBAL_ROOT',
    clientId: row.clientId || row.client || row.customerId || row.tenantId || 'UNRESOLVED_CLIENT',
    client: row.client || row.clientName || row.clientId || row.customerName || row.tenantId || 'UNRESOLVED_CLIENT',
    amount: normalizeCurrencyAmount(row),
    currency: String(row.currency || defaults.currency || 'ZAR').toUpperCase(),
    overdueDays,
    riskScore,
    status: String(row.status || defaults.status || 'OPEN').toUpperCase(),
    sourceStatus: row.sourceStatus || defaults.sourceStatus || 'SOURCE_SILENT',
    reason: row.reason || row.recommendation || row.aiRecommendation || 'Dunning candidate derived from ledger evidence.',
    dueDate: row.dueDate || null,
    lastContactAt: row.lastContactAt || row.lastDunningAt || null,
    contactAttemptsLast7Days: Number(row.contactAttemptsLast7Days || row.contactAttempts || 0),
    disputed: Boolean(row.disputed || row.disputeId || String(row.status || '').toUpperCase() === 'DISPUTED'),
    legalHold: Boolean(row.legalHold || String(row.status || '').toUpperCase() === 'LEGAL_HOLD'),
    representedByCounsel: Boolean(row.representedByCounsel || row.legalRepresentative),
    channelConsent: {
      EMAIL: channelConsent.EMAIL ?? channelConsent.email ?? true,
      SMS: channelConsent.SMS ?? channelConsent.sms ?? false,
      WHATSAPP: channelConsent.WHATSAPP ?? channelConsent.whatsapp ?? false,
      PHONE: channelConsent.PHONE ?? channelConsent.phone ?? false,
      PORTAL: true,
      SECURE_PORTAL: true
    },
    timezone: row.timezone || defaults.timezone || 'Africa/Johannesburg',
    metadata: row.metadata || {}
  };
};

/**
 * @class DunningIntelligence
 * @description Builds, gates, seals, and optionally dispatches evidence-backed collections interventions.
 */
class DunningIntelligence {
  /**
   * @constructor
   * @param {Object} config - Engine configuration.
   * @param {Object} [config.apiClient] - Axios-compatible API client.
   */
  constructor(config = {}) {
    this.engineVersion = config.engineVersion || DUNNING_INTELLIGENCE_VERSION;
    this.apiClient = config.apiClient || api;
    this.backoffUntil = 0;
  }

  /**
   * @method createTraceId
   * @description Creates a dunning trace id for recommendation and dispatch correlation.
   * @param {string} tenantId - Tenant id.
   * @param {string} clientId - Client id.
   * @returns {string} Trace id.
   */
  createTraceId(tenantId = 'GLOBAL_ROOT', clientId = 'CLIENT') {
    const cryptoSource = typeof crypto !== 'undefined' ? crypto : null;
    const entropy = cryptoSource?.randomUUID
      ? cryptoSource.randomUUID().slice(0, 10)
      : `${Date.now().toString(36)}${Math.random().toString(36).slice(2, 8)}`;
    return `DUN-${String(tenantId).toUpperCase()}-${String(clientId).toUpperCase()}-${entropy.toUpperCase()}`;
  }

  /**
   * @method deriveStage
   * @description Converts overdue depth, amount, and risk score into a governed dunning stage.
   * @param {Object} account - Normalized account.
   * @returns {Object} Dunning posture.
   */
  deriveStage(account = {}) {
    if (account.legalHold || account.disputed || account.representedByCounsel) return DUNNING_POSTURE_MATRIX.LEGAL_REVIEW;
    if (account.overdueDays >= 45 || account.riskScore >= 82) return DUNNING_POSTURE_MATRIX.LEGAL_REVIEW;
    if (account.overdueDays >= 28 || account.riskScore >= 68) return DUNNING_POSTURE_MATRIX.FINAL_DEMAND;
    if (account.overdueDays >= 8 || account.riskScore >= 42) return DUNNING_POSTURE_MATRIX.STRUCTURED_DUNNING;
    if (account.overdueDays >= 1 || account.riskScore >= 25) return DUNNING_POSTURE_MATRIX.SOFT_REMINDER;
    return DUNNING_POSTURE_MATRIX.MONITOR;
  }

  /**
   * @method isQuietHours
   * @description Determines whether the local contact time is inside quiet-hour protection.
   * @param {string} timezone - IANA timezone.
   * @param {Date} [date=new Date()] - Date to evaluate.
   * @returns {boolean} True when contact should not be sent.
   */
  isQuietHours(timezone = 'Africa/Johannesburg', date = new Date()) {
    try {
      const hour = Number(new Intl.DateTimeFormat('en-ZA', {
        hour: '2-digit',
        hour12: false,
        timeZone: timezone
      }).format(date));
      return hour >= QUIET_HOURS.start || hour < QUIET_HOURS.end;
    } catch {
      const hour = date.getHours();
      return hour >= QUIET_HOURS.start || hour < QUIET_HOURS.end;
    }
  }

  /**
   * @method chooseChannel
   * @description Selects the first compliant channel from posture priority and consent evidence.
   * @param {Object} account - Normalized account.
   * @param {Object} posture - Dunning posture.
   * @returns {{channel:string,reason:string}} Selected channel.
   */
  chooseChannel(account = {}, posture = DUNNING_POSTURE_MATRIX.MONITOR) {
    const channel = (posture.channelPriority || ['EMAIL']).find(candidate => account.channelConsent?.[candidate]);
    if (channel) return { channel, reason: 'CONSENTED_PRIORITY_CHANNEL' };
    return { channel: 'PORTAL', reason: 'FALLBACK_SECURE_PORTAL_NO_EXTERNAL_CONTACT' };
  }

  /**
   * @method buildComplianceGates
   * @description Builds legal, consent, cadence, and dispute gates for a dunning recommendation.
   * @param {Object} account - Normalized account.
   * @param {Object} posture - Dunning posture.
   * @param {string} channel - Selected channel.
   * @returns {Array<Object>} Gate rows.
   */
  buildComplianceGates(account = {}, posture = DUNNING_POSTURE_MATRIX.MONITOR, channel = 'EMAIL') {
    const externalChannel = !['PORTAL', 'SECURE_PORTAL'].includes(channel);
    return [
      {
        gate: 'DISPUTE_SUPPRESSION',
        status: account.disputed ? 'BLOCK' : 'PASS',
        detail: account.disputed ? 'Invoice is disputed. Route to dispute workflow before collection contact.' : 'No dispute flag present.'
      },
      {
        gate: 'LEGAL_HOLD_SUPPRESSION',
        status: account.legalHold || account.representedByCounsel ? 'BLOCK' : 'PASS',
        detail: account.legalHold || account.representedByCounsel ? 'Legal hold or counsel representation requires legal review.' : 'No legal hold/counsel flag present.'
      },
      {
        gate: 'CHANNEL_CONSENT',
        status: externalChannel && !account.channelConsent?.[channel] ? 'REVIEW' : 'PASS',
        detail: `${channel} selected. ${externalChannel ? 'External contact channel requires consent evidence.' : 'Secure portal contact only.'}`
      },
      {
        gate: 'QUIET_HOURS',
        status: externalChannel && this.isQuietHours(account.timezone) ? 'REVIEW' : 'PASS',
        detail: externalChannel ? `Quiet hours ${QUIET_HOURS.start}:00-${QUIET_HOURS.end}:00 local are protected.` : 'Portal-only action does not interrupt client.'
      },
      {
        gate: 'FREQUENCY_CAP',
        status: account.contactAttemptsLast7Days >= 7 ? 'REVIEW' : 'PASS',
        detail: `${account.contactAttemptsLast7Days}/7 contact attempts recorded in the last 7 days.`
      },
      {
        gate: 'STAGE_LEGALITY',
        status: posture.stage === 'LEGAL_REVIEW' ? 'REVIEW' : 'PASS',
        detail: posture.stage === 'LEGAL_REVIEW' ? 'Legal review required before demand notice dispatch.' : posture.legalPosture
      }
    ];
  }

  /**
   * @method buildRecommendation
   * @description Produces a sealed dunning recommendation from a normalized or raw account row.
   * @param {Object} rawAccount - Source account row.
   * @param {Object} defaults - Default tenant/source values.
   * @returns {Object} Dunning recommendation packet.
   */
  buildRecommendation(rawAccount = {}, defaults = {}) {
    const account = normalizeAccount(rawAccount, defaults);
    const posture = this.deriveStage(account);
    const channelDecision = this.chooseChannel(account, posture);
    const gates = this.buildComplianceGates(account, posture, channelDecision.channel);
    const gateStatus = gates.some(gate => gate.status === 'BLOCK')
      ? 'BLOCKED'
      : (gates.some(gate => gate.status === 'REVIEW') ? 'REVIEW_REQUIRED' : 'READY');
    const traceId = this.createTraceId(account.tenantId, account.clientId);
    const packet = {
      id: account.id,
      traceId,
      engineVersion: this.engineVersion,
      generatedAt: new Date().toISOString(),
      tenantId: account.tenantId,
      clientId: account.clientId,
      client: account.client,
      invoiceId: account.invoiceId,
      amount: account.amount,
      currency: account.currency,
      overdueDays: account.overdueDays,
      riskScore: account.riskScore,
      sourceStatus: account.sourceStatus,
      reason: account.reason,
      stage: posture.stage,
      tone: posture.toneColor,
      toneCode: posture.tone,
      channel: channelDecision.channel,
      channelReason: channelDecision.reason,
      retryIntervalHours: posture.retryIntervalHours,
      nextAction: posture.nextAction,
      legalPosture: posture.legalPosture,
      gateStatus,
      gates,
      complianceWarnings: gates.filter(gate => gate.status !== 'PASS').map(gate => `${gate.gate}: ${gate.detail}`)
    };
    return {
      ...packet,
      proof: {
        algorithm: 'SHA3-512',
        canonicalization: 'STABLE_JSON_KEY_SORT',
        hash: createDunningProofHash(packet),
        canonicalPayload: stableStringify(packet)
      }
    };
  }

  /**
   * @method fetchRiskProfile
   * @description Attempts to fetch a live collections risk profile without fabricating one on failure.
   * @param {string} tenantId - Tenant id.
   * @param {string} clientId - Client id.
   * @returns {Promise<Object|null>} Risk profile or null.
   */
  async fetchRiskProfile(tenantId, clientId) {
    for (const endpointFactory of RISK_ENDPOINTS) {
      try {
        const response = await this.apiClient.get(endpointFactory(tenantId, clientId));
        return normalizeApiPayload(response);
      } catch {
        continue;
      }
    }
    return null;
  }

  /**
   * @method getDunningRecommendations
   * @description Fetches live dunning recommendations or builds source-aware fallback packets from ledger rows.
   * @param {string} tenantId - Tenant id.
   * @param {Object} context - Fallback context.
   * @param {Array<Object>} [context.invoiceRows=[]] - Invoice rows.
   * @param {Array<Object>} [context.collectionRiskRows=[]] - Collection-risk rows.
   * @param {boolean} [context.preferLedgerFallback=false] - Whether to build from provided ledger rows before optional live probes.
   * @param {boolean} [context.suppressLiveProbe=false] - Whether to suppress optional live recommendation endpoint probes.
   * @returns {Promise<Object>} Recommendation envelope.
   */
  async getDunningRecommendations(tenantId = 'GLOBAL_ROOT', context = {}) {
    const skipLiveProbe = Boolean(context.preferLedgerFallback || context.suppressLiveProbe);

    if (!skipLiveProbe && Date.now() >= this.backoffUntil) {
      for (const endpointFactory of RECOMMENDATION_ENDPOINTS) {
        try {
          const response = await this.apiClient.get(endpointFactory(tenantId));
          const rows = normalizeArray(normalizeApiPayload(response));
          const recommendations = rows.map((row, index) => this.buildRecommendation(row, {
            tenantId,
            index,
            sourceStatus: 'LIVE_DUNNING_SOURCE'
          }));
          return {
            success: true,
            status: recommendations.length ? 'LIVE' : 'LIVE_EMPTY',
            sourceStatus: 'LIVE_DUNNING_SOURCE',
            recommendations,
            lastSync: new Date().toISOString()
          };
        } catch (error) {
          if (error.response?.status === 503 || error.isSourceBackoff || String(error.message || '').toLowerCase().includes('timeout')) {
            this.backoffUntil = Date.now() + DUNNING_BACKOFF_MS;
            break;
          }
        }
      }
      this.backoffUntil = Date.now() + DUNNING_BACKOFF_MS;
    }

    const riskRows = normalizeArray(context.collectionRiskRows).map((row, index) => this.buildRecommendation(row, {
      tenantId,
      index,
      sourceStatus: 'LEDGER_RISK'
    }));
    const invoiceRows = riskRows.length ? [] : normalizeArray(context.invoiceRows)
      .filter(row => ['OVERDUE', 'DISPUTED', 'LEGAL_HOLD', 'PARTIALLY_PAID'].includes(String(row.status || '').toUpperCase()))
      .map((row, index) => this.buildRecommendation(row, {
        tenantId,
        index,
        sourceStatus: 'INVOICE_LEDGER'
      }));

    const recommendations = [...riskRows, ...invoiceRows].slice(0, 12);
    return {
      success: recommendations.length > 0,
      status: recommendations.length ? 'FALLBACK_LEDGER_DERIVED' : 'SOURCE_SILENT',
      sourceStatus: recommendations.length ? 'LEDGER_DERIVED' : 'SOURCE_SILENT',
      recommendations,
      lastSync: new Date().toISOString(),
      warning: recommendations.length
        ? 'Live dunning endpoint is silent. Recommendations were derived from invoice/ledger evidence.'
        : 'No live dunning source or ledger risk rows were available.'
    };
  }

  /**
   * @method executeIntervention
   * @description Dispatches a recommendation only when gates permit external action.
   * @param {Object} params - Dispatch parameters.
   * @param {string} params.tenantId - Tenant id.
   * @param {Object} params.recommendation - Dunning recommendation.
   * @param {boolean} [params.dryRun=false] - Whether to avoid backend dispatch.
   * @returns {Promise<Object>} Dispatch receipt.
   */
  async executeIntervention({ tenantId = 'GLOBAL_ROOT', recommendation = {}, dryRun = false } = {}) {
    const blocked = recommendation.gateStatus === 'BLOCKED' || recommendation.gateStatus === 'REVIEW_REQUIRED';
    const payload = {
      tenantId,
      traceId: recommendation.traceId || this.createTraceId(tenantId, recommendation.clientId),
      clientId: recommendation.clientId,
      invoiceId: recommendation.invoiceId,
      channel: recommendation.channel,
      tone: recommendation.toneCode,
      stage: recommendation.stage,
      amount: recommendation.amount,
      currency: recommendation.currency,
      nextAction: recommendation.nextAction,
      recommendationProofHash: recommendation.proof?.hash,
      engineVersion: this.engineVersion,
      requestedAt: new Date().toISOString()
    };

    if (dryRun || blocked) {
      const receipt = {
        success: true,
        status: dryRun ? 'DRY_RUN' : recommendation.gateStatus,
        dispatchStatus: 'NO_EXTERNAL_DISPATCH',
        payload,
        recommendation,
        message: blocked
          ? 'Dunning intervention held by compliance gates.'
          : 'Dry run completed. No external dunning message sent.'
      };
      return { ...receipt, proof: { algorithm: 'SHA3-512', hash: createDunningProofHash(receipt) } };
    }

    for (const endpointFactory of DISPATCH_ENDPOINTS) {
      try {
        const response = await this.apiClient.post(endpointFactory(), payload);
        const receipt = {
          success: true,
          status: 'DISPATCHED',
          dispatchStatus: 'DISPATCHED',
          payload,
          recommendation,
          response: normalizeApiPayload(response)
        };
        await Promise.resolve(broadcastTelemetry(tenantId, 'DUNNING_ACTION', 'DISPATCHED', 'DunningIntelligence', {
          traceId: payload.traceId,
          clientId: payload.clientId,
          channel: payload.channel,
          stage: payload.stage
        })).catch(() => {});
        return { ...receipt, proof: { algorithm: 'SHA3-512', hash: createDunningProofHash(receipt) } };
      } catch {
        continue;
      }
    }

    const receipt = {
      success: false,
      status: 'DISPATCH_ENDPOINT_SOURCE_SILENT',
      dispatchStatus: 'NO_EXTERNAL_DISPATCH',
      payload,
      recommendation,
      message: 'No dunning execution endpoint accepted the command.'
    };
    await Promise.resolve(broadcastTelemetry(tenantId, 'DUNNING_ACTION', 'SOURCE_SILENT', 'DunningIntelligence', {
      traceId: payload.traceId,
      clientId: payload.clientId,
      channel: payload.channel,
      stage: payload.stage
    })).catch(() => {});
    return { ...receipt, proof: { algorithm: 'SHA3-512', hash: createDunningProofHash(receipt) } };
  }

  /**
   * @method runSovereignDunningCycle
   * @description Builds recommendations and optionally dispatches ready interventions for a tenant.
   * @param {string} tenantId - Tenant id.
   * @param {Object} context - Cycle context.
   * @param {boolean} [context.autoDispatch=false] - Whether to dispatch ready interventions.
   * @returns {Promise<Object>} Cycle result.
   */
  async runSovereignDunningCycle(tenantId = 'GLOBAL_ROOT', context = {}) {
    const envelope = await this.getDunningRecommendations(tenantId, context);
    const receipts = [];
    if (context.autoDispatch) {
      for (const recommendation of envelope.recommendations || []) {
        if (recommendation.gateStatus === 'READY') {
          receipts.push(await this.executeIntervention({ tenantId, recommendation }));
        }
      }
    }
    return {
      success: true,
      tenantId,
      status: receipts.length ? 'DUNNING_DISPATCHED' : envelope.status,
      recommendations: envelope.recommendations,
      receipts,
      generatedAt: new Date().toISOString()
    };
  }
}

const dunningIntelligence = new DunningIntelligence();

export { DunningIntelligence };
export default dunningIntelligence;
