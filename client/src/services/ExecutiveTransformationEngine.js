/* eslint-disable */
/**
 * WILSY OS - EXECUTIVE TRANSFORMATION ENGINE [V1.0.0-UNICORN-PLAYBOOK]
 * [ARR PHASES | AI INSIGHT ROWS | CONNECTOR READINESS | TRUST STACK | COMPETITIVE MOAT PROOFS]
 *
 * VERSION: 1.0.0-UNICORN-PLAYBOOK | PRODUCTION READY | EXECUTIVE OS GROWTH COMMAND ENGINE
 * ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/services/ExecutiveTransformationEngine.js
 *
 * COLLABORATION & SOVEREIGN SIGN-OFF:
 * - Wilson Khanyezi (Founder/CEO) - Supplied the $0 to $1B+ ARR executive roadmap and mandated competition-level OS enhancement.
 * - AI Engineering (Codex) - ARCHITECTED: Converted roadmap research into source-aware executive playbooks, connector gates,
 *   compliance trust rows, natural-language answers and SHA3-sealed transformation packets.
 */

import { sha3_512 } from 'js-sha3';

export const EXECUTIVE_TRANSFORMATION_VERSION = 'V1.0.0-UNICORN-PLAYBOOK';

/**
 * @constant {Array<Object>}
 * @description ARR transformation phases from the executive roadmap.
 * @collaboration Keeps the dashboard aligned to Wilson's product-to-unicorn operating sequence.
 */
export const EXECUTIVE_GROWTH_PHASES = Object.freeze([
  {
    key: 'foundation',
    label: 'PHASE_1_FOUNDATION',
    arrFloor: 0,
    arrCeiling: 500000,
    target: '$0-$500K ARR',
    months: 'Months 1-6',
    mandate: 'Product-market fit, finance source activation, AI insights, beta customer evidence.',
    milestone: '50 paying customers, $25K MRR, NPS above 50.'
  },
  {
    key: 'scale',
    label: 'PHASE_2_SCALE',
    arrFloor: 500000,
    arrCeiling: 5000000,
    target: '$500K-$5M ARR',
    months: 'Months 7-18',
    mandate: 'Enterprise workflows, scenario planning, board portal, investor relations and reseller motion.',
    milestone: '1,000 paying customers, $5M ARR, Series A readiness.'
  },
  {
    key: 'domination',
    label: 'PHASE_3_DOMINATION',
    arrFloor: 5000000,
    arrCeiling: 50000000,
    target: '$5M-$50M ARR',
    months: 'Months 19-36',
    mandate: 'AI co-pilot, ecosystem marketplace, vertical solutions and enterprise suite expansion.',
    milestone: '5,000 paying customers, $50M ARR, market leader posture.'
  },
  {
    key: 'unicorn',
    label: 'PHASE_4_UNICORN',
    arrFloor: 50000000,
    arrCeiling: 1000000000,
    target: '$50M-$1B+ ARR',
    months: 'Months 37-60',
    mandate: 'Unified work graph, autonomous operations, network effects and financial products.',
    milestone: '20,000+ paying customers, $500M+ ARR, IPO or strategic exit readiness.'
  }
]);

/**
 * @constant {Array<Object>}
 * @description Connector playbooks required by the executive roadmap.
 * @collaboration Enterprise buyers expect finance, CRM, communication and SSO rails; Wilsy OS exposes them as gated work.
 */
export const EXECUTIVE_CONNECTOR_PLAYBOOKS = Object.freeze([
  { key: 'quickbooks_xero', label: 'QuickBooks / Xero', lane: 'Finance', route: '/settings/integrations/finance', sourceKey: 'finance', value: 'SMB finance ingestion' },
  { key: 'sap_netsuite', label: 'SAP / NetSuite', lane: 'Finance', route: '/settings/integrations/erp', sourceKey: 'finance', value: 'Enterprise ERP ledger' },
  { key: 'stripe_paypal', label: 'Stripe / PayPal', lane: 'Revenue', route: '/settings/integrations/payments', sourceKey: 'finance', value: 'Revenue and failed payment stream' },
  { key: 'salesforce_hubspot', label: 'Salesforce / HubSpot', lane: 'Sales', route: '/settings/integrations/crm', sourceKey: 'records', value: 'Pipeline, churn and expansion signal' },
  { key: 'slack_teams', label: 'Slack / Teams', lane: 'Alerts', route: '/settings/integrations/alerts', sourceKey: 'telemetry', value: 'Critical executive alerting' },
  { key: 'google_microsoft_sso', label: 'Google / Microsoft SSO', lane: 'Identity', route: '/settings/security/sso', sourceKey: 'profile', value: 'Enterprise SSO and workspace access' },
  { key: 'docusign_adobe_sign', label: 'DocuSign / Adobe Sign', lane: 'Board', route: '/settings/integrations/signatures', sourceKey: 'records', value: 'Board approvals and resolutions' },
  { key: 'microsoft365_google_docs', label: 'Microsoft 365 / Google Docs', lane: 'Board', route: '/settings/integrations/documents', sourceKey: 'records', value: 'Board pack source materials' }
]);

/**
 * @constant {Array<Object>}
 * @description Enterprise trust workstreams required to sell the executive surface to serious boards.
 * @collaboration Turns SOC2, POPIA/GDPR, RBAC and audit export from vague promises into dashboard-visible work.
 */
export const EXECUTIVE_TRUST_PLAYBOOKS = Object.freeze([
  { key: 'soc2_type_ii', label: 'SOC 2 Type II Evidence', lane: 'Security', sourceKey: 'telemetry', threshold: 78 },
  { key: 'popia_gdpr', label: 'POPIA / GDPR Automation', lane: 'Compliance', sourceKey: 'profile', threshold: 68 },
  { key: 'audit_export', label: 'Audit Trail Export', lane: 'Governance', sourceKey: 'records', threshold: 62 },
  { key: 'rbac_sso', label: 'RBAC / SSO Hardening', lane: 'Identity', sourceKey: 'profile', threshold: 72 },
  { key: 'board_assurance', label: 'Board Assurance Packet', lane: 'Board', sourceKey: 'finance', threshold: 74 }
]);

/**
 * @constant {Array<Object>}
 * @description Competitive battlecards distilled from current market research and the local roadmap.
 * @collaboration Competitor awareness becomes product action: every outside feature maps to a Wilsy OS counter-move.
 */
export const EXECUTIVE_COMPETITIVE_PLAYBOOKS = Object.freeze([
  {
    key: 'generic_bi',
    label: 'Generic BI Dashboards',
    competitorSignal: 'Charts, reports and configurable KPI views.',
    wilsyMove: 'Finance-sourced KPIs, SHA3 command receipts, source registry and daily work orders.',
    sourceKey: 'finance'
  },
  {
    key: 'board_portals',
    label: 'AI Board Portals',
    competitorSignal: 'AI board books, meeting prep, secure board messaging and action tracking.',
    wilsyMove: 'Live finance board packet, investor brief command, repair queues and proofed strategic goals.',
    sourceKey: 'records'
  },
  {
    key: 'connected_reporting',
    label: 'Connected Reporting Platforms',
    competitorSignal: 'Governed data, version control, agentic AI and assurance-ready reporting.',
    wilsyMove: 'Tenant source registry, POPIA/ZAR-first posture, telemetry stream and no-fake-data fallbacks.',
    sourceKey: 'telemetry'
  },
  {
    key: 'enterprise_planning',
    label: 'Enterprise Planning Suites',
    competitorSignal: 'Forecasting, scenario planning, workflow automation and enterprise templates.',
    wilsyMove: 'ARR phase engine, duty-specific work orders, integration ladder and Wilsy AI monetisation.',
    sourceKey: 'profile'
  }
]);

/**
 * @function stableTransformationStringify
 * @description Serializes transformation packets with deterministic key order.
 * @param {unknown} value - Candidate value.
 * @returns {string} Stable JSON string.
 * @collaboration Growth, trust and moat decisions must replay to the same proof hash across exports.
 */
export const stableTransformationStringify = (value) => {
  if (typeof value === 'undefined') return 'null';
  if (value instanceof Date) return JSON.stringify(value.toISOString());
  if (value === null || typeof value !== 'object') return JSON.stringify(value);
  if (Array.isArray(value)) return `[${value.map(item => stableTransformationStringify(item)).join(',')}]`;
  return `{${Object.keys(value).sort().map(key => `${JSON.stringify(key)}:${stableTransformationStringify(value[key])}`).join(',')}}`;
};

/**
 * @function createTransformationProof
 * @description Creates a SHA3-512 proof for executive transformation packets.
 * @param {Object} payload - Payload to seal.
 * @returns {string} Uppercase SHA3-512 proof hash.
 * @collaboration Every roadmap recommendation needs the same forensic discipline as other executive commands.
 */
export const createTransformationProof = (payload = {}) => sha3_512(stableTransformationStringify(payload)).toUpperCase();

/**
 * @function toFiniteNumber
 * @description Converts optional metric values into finite numbers without inventing source data.
 * @param {unknown} value - Candidate numeric value.
 * @param {number} fallback - Explicit fallback number.
 * @returns {number} Finite number.
 * @collaboration Source-silent values remain controllable instead of becoming accidental NaN UI fractures.
 */
const toFiniteNumber = (value, fallback = 0) => {
  const numeric = Number(value);
  return Number.isFinite(numeric) ? numeric : fallback;
};

/**
 * @function formatTransformationMoney
 * @description Formats transformation money values for service-level labels.
 * @param {number|string} value - Money amount.
 * @param {string} currency - Currency label.
 * @returns {string} Compact money label.
 * @collaboration Keeps natural-language answers readable while the UI still owns final money formatting elsewhere.
 */
const formatTransformationMoney = (value = 0, currency = 'ZAR') => {
  const numeric = toFiniteNumber(value, 0);
  return `${String(currency || 'ZAR').toUpperCase()} ${numeric.toLocaleString(undefined, { maximumFractionDigits: 0 })}`;
};

/**
 * @function isSourceLive
 * @description Determines whether a source row should count as live evidence.
 * @param {Object} source - Source row or registry entry.
 * @returns {boolean} True when the source is live.
 * @collaboration Readiness scoring must be source-aware, not optimistic.
 */
const isSourceLive = (source = {}) => Boolean(source?.live);

/**
 * @function resolveSourceByKey
 * @description Resolves a source row by source key with profile-specific support.
 * @param {Object} params - Source lookup inputs.
 * @param {Array<Object>} params.sourceRows - Source registry rows.
 * @param {Object} params.profile - Tenant business profile.
 * @param {string} params.sourceKey - Source key.
 * @returns {Object} Source status row.
 * @collaboration Connector and trust rows need one source truth resolver instead of ad hoc lookups.
 */
const resolveSourceByKey = ({ sourceRows = [], profile = {}, sourceKey = 'records' } = {}) => {
  if (sourceKey === 'profile') {
    return {
      key: 'profile',
      live: profile.sourceStatus !== 'TENANT_PROFILE_INCOMPLETE',
      status: profile.sourceStatus || 'TENANT_PROFILE_INCOMPLETE'
    };
  }
  return sourceRows.find(source => source.key === sourceKey) || {
    key: sourceKey,
    live: false,
    status: 'SOURCE_REQUIRED'
  };
};

/**
 * @function resolveGrowthPhase
 * @description Selects the current ARR growth phase for an executive tenant.
 * @param {number} arr - Annual recurring revenue value.
 * @returns {Object} Growth phase record.
 * @collaboration The dashboard must know whether it is executing foundation, scale, domination or unicorn work.
 */
export const resolveGrowthPhase = (arr = 0) => {
  const numericArr = Math.max(0, toFiniteNumber(arr, 0));
  return EXECUTIVE_GROWTH_PHASES.find(phase => (
    numericArr >= phase.arrFloor && numericArr < phase.arrCeiling
  )) || EXECUTIVE_GROWTH_PHASES[EXECUTIVE_GROWTH_PHASES.length - 1];
};

/**
 * @function calculatePhaseProgress
 * @description Calculates current progress through a growth phase.
 * @param {Object} phase - Growth phase record.
 * @param {number} arr - Annual recurring revenue value.
 * @returns {number} Progress percentage.
 * @collaboration Phase progress gives Wilson a sober operating gauge without fake milestone completion.
 */
export const calculatePhaseProgress = (phase = EXECUTIVE_GROWTH_PHASES[0], arr = 0) => {
  const span = Math.max(1, toFiniteNumber(phase.arrCeiling, 1) - toFiniteNumber(phase.arrFloor, 0));
  const progressed = Math.max(0, toFiniteNumber(arr, 0) - toFiniteNumber(phase.arrFloor, 0));
  return Math.min(100, Math.round((progressed / span) * 100));
};

/**
 * @function buildExecutiveInsightRows
 * @description Builds source-gated AI and analytics insights for the executive dashboard.
 * @param {Object} params - Insight inputs.
 * @returns {Array<Object>} Insight rows with status, action and proof hash.
 * @collaboration Predictive analytics must show readiness and gaps before promising machine intelligence.
 */
export const buildExecutiveInsightRows = ({
  financialKPIs = {},
  sourceSnapshot = {},
  profile = {},
  executiveReadiness = {},
  wilsyAiPlan = []
} = {}) => {
  const currency = financialKPIs.currency || 'ZAR';
  const revenue = toFiniteNumber(financialKPIs.revenue, 0);
  const arr = toFiniteNumber(financialKPIs.arr, revenue * 1.2);
  const margin = financialKPIs.profitMargin === null || financialKPIs.profitMargin === undefined
    ? null
    : toFiniteNumber(financialKPIs.profitMargin, 0);
  const financeLive = Boolean(sourceSnapshot.finance?.live);
  const telemetryLive = Boolean(sourceSnapshot.telemetry?.live);
  const sourceMultiplier = Math.min(0.18, toFiniteNumber(executiveReadiness.score, 0) / 650);
  const forecastValue = Math.round(arr * (1 + sourceMultiplier));
  const activePlan = wilsyAiPlan.find(plan => plan.licenseStatus === 'ACTIVE') || wilsyAiPlan[0] || {};
  const rows = [
    {
      id: 'predictive_arr_forecast',
      lane: 'AI_FORECAST',
      title: 'Predictive ARR Forecast',
      status: financeLive && arr > 0 ? 'READY' : 'FINANCE_SOURCE_REQUIRED',
      signal: financeLive && arr > 0 ? `${formatTransformationMoney(forecastValue, currency)} next-cycle projection` : 'Connect finance source before forecast.',
      confidence: financeLive ? Math.min(96, toFiniteNumber(executiveReadiness.score, 0) + 8) : 24,
      actionLabel: 'Create forecast work order'
    },
    {
      id: 'financial_anomaly_watch',
      lane: 'ANOMALY_DETECTION',
      title: 'Financial Anomaly Watch',
      status: margin === null ? 'MARGIN_SOURCE_REQUIRED' : margin < 12 || revenue < toFiniteNumber(financialKPIs.expenses, 0) ? 'RISK' : 'WATCHING',
      signal: margin === null ? 'Margin source silent.' : `Margin ${margin}% against expense pressure.`,
      confidence: margin === null ? 18 : financeLive ? 88 : 52,
      actionLabel: 'Review anomaly evidence'
    },
    {
      id: 'board_packet_automation',
      lane: 'BOARD_AUTOMATION',
      title: 'Board Packet Automation',
      status: financeLive && telemetryLive ? 'BOARD_READY' : 'SOURCE_GATED',
      signal: financeLive ? `${profile.industryLabel || 'Tenant'} board packet can use live finance posture.` : 'Board packet remains draft until finance answers.',
      confidence: financeLive && telemetryLive ? 91 : 41,
      actionLabel: 'Seal board packet'
    },
    {
      id: 'executive_nlq',
      lane: 'NATURAL_LANGUAGE',
      title: 'Natural-Language Executive Query',
      status: telemetryLive ? 'ONLINE' : 'LOCAL_ONLY',
      signal: 'Ask about revenue, sources, board readiness, integrations, compliance or competition.',
      confidence: telemetryLive ? 84 : 58,
      actionLabel: 'Ask Executive OS'
    },
    {
      id: 'wilsy_ai_monetisation',
      lane: 'WILSY_AI',
      title: 'Wilsy AI Monetisation Ladder',
      status: activePlan.licenseStatus === 'ACTIVE' ? 'ACTIVE' : activePlan.readiness || 'PLAN_REQUIRED',
      signal: activePlan.name ? `${activePlan.name} // ${activePlan.tier || 'TIER_PENDING'}` : 'Tenant automation plan requires source context.',
      confidence: activePlan.name ? 76 : 31,
      actionLabel: 'License top automation'
    }
  ];

  return rows.map(row => ({
    ...row,
    proofHash: createTransformationProof({
      row,
      arr,
      revenue,
      tenantIndustry: profile.industryKey,
      version: EXECUTIVE_TRANSFORMATION_VERSION
    })
  }));
};

/**
 * @function buildIntegrationReadiness
 * @description Builds source-aware integration readiness rows from the roadmap connector list.
 * @param {Object} params - Connector inputs.
 * @returns {Array<Object>} Connector readiness rows.
 * @collaboration Integrations are not decorative logos; each connector becomes a source-gated execution path.
 */
export const buildIntegrationReadiness = ({
  activeTenant = {},
  sourceRows = [],
  profile = {}
} = {}) => {
  const tenant = activeTenant && typeof activeTenant === 'object' ? activeTenant : {};
  const enabledIntegrations = new Set([
    ...(tenant.integrations || []),
    ...(tenant.connectors || []),
    ...(tenant.enabledIntegrations || []),
    ...(tenant.enabledConnectors || [])
  ].map(value => String(value).toLowerCase()));

  return EXECUTIVE_CONNECTOR_PLAYBOOKS.map((connector, index) => {
    const source = resolveSourceByKey({ sourceRows, profile, sourceKey: connector.sourceKey });
    const connected = enabledIntegrations.has(connector.key.toLowerCase())
      || enabledIntegrations.has(connector.label.toLowerCase())
      || enabledIntegrations.has(connector.lane.toLowerCase());
    const status = connected
      ? 'CONNECTED'
      : isSourceLive(source)
        ? 'READY_TO_CONNECT'
        : 'SOURCE_REQUIRED';
    const row = {
      ...connector,
      priority: status === 'CONNECTED' ? index + 20 : status === 'READY_TO_CONNECT' ? index + 1 : index + 10,
      status,
      sourceStatus: source.status,
      nextAction: status === 'CONNECTED'
        ? 'Monitor connector evidence.'
        : status === 'READY_TO_CONNECT'
          ? `Open ${connector.route}`
          : `Repair ${connector.sourceKey} source before connector activation.`
    };
    return {
      ...row,
      proofHash: createTransformationProof({
        row,
        tenantId: tenant.tenantId || tenant.id || 'UNRESOLVED_TENANT',
        version: EXECUTIVE_TRANSFORMATION_VERSION
      })
    };
  }).sort((left, right) => left.priority - right.priority);
};

/**
 * @function buildComplianceTrustRows
 * @description Builds enterprise trust stack rows for security, compliance and audit export.
 * @param {Object} params - Trust inputs.
 * @returns {Array<Object>} Trust stack rows.
 * @collaboration Enterprise readiness must expose trust gaps before sales promises are made.
 */
export const buildComplianceTrustRows = ({
  sourceRows = [],
  profile = {},
  accessDecision = {},
  executiveReadiness = {},
  mutationReceipts = []
} = {}) => (
  EXECUTIVE_TRUST_PLAYBOOKS.map((trust, index) => {
    const source = resolveSourceByKey({ sourceRows, profile, sourceKey: trust.sourceKey });
    const readinessScore = toFiniteNumber(executiveReadiness.score, 0);
    const hasReceipts = mutationReceipts.length > 0;
    const status = !accessDecision.allowed
      ? 'ACCESS_DENIED'
      : trust.key === 'audit_export' && hasReceipts
        ? 'EXPORT_READY'
        : trust.key === 'rbac_sso' && accessDecision.allowed
          ? 'RBAC_ACTIVE'
          : isSourceLive(source) && readinessScore >= trust.threshold
            ? 'EVIDENCE_READY'
            : isSourceLive(source)
              ? 'EVIDENCE_BUILDING'
              : 'SOURCE_REQUIRED';
    const row = {
      ...trust,
      priority: status === 'SOURCE_REQUIRED' ? index + 10 : index + 1,
      status,
      sourceStatus: source.status,
      score: Math.min(100, Math.round((isSourceLive(source) ? 45 : 10) + (readinessScore * 0.45) + (hasReceipts ? 10 : 0))),
      nextAction: status === 'SOURCE_REQUIRED'
        ? `Repair ${trust.sourceKey} source.`
        : status === 'EXPORT_READY'
          ? 'Export audit evidence on demand.'
          : `Advance ${trust.label}.`
    };
    return {
      ...row,
      proofHash: createTransformationProof({
        row,
        readinessScore,
        receipts: mutationReceipts.length,
        version: EXECUTIVE_TRANSFORMATION_VERSION
      })
    };
  }).sort((left, right) => left.priority - right.priority)
);

/**
 * @function buildCompetitiveMoatRows
 * @description Builds competitive battlecard rows from source posture and roadmap differentiation.
 * @param {Object} params - Moat inputs.
 * @returns {Array<Object>} Competitive moat rows.
 * @collaboration Wilson asked to beat competition; this converts market claims into visible operating counters.
 */
export const buildCompetitiveMoatRows = ({ sourceRows = [], profile = {}, executiveReadiness = {} } = {}) => (
  EXECUTIVE_COMPETITIVE_PLAYBOOKS.map((battlecard, index) => {
    const source = resolveSourceByKey({ sourceRows, profile, sourceKey: battlecard.sourceKey });
    const status = isSourceLive(source)
      ? toFiniteNumber(executiveReadiness.score, 0) >= 76
        ? 'MOAT_LIVE'
        : 'MOAT_BUILDING'
      : 'SOURCE_GATED';
    const row = {
      ...battlecard,
      priority: status === 'SOURCE_GATED' ? index + 10 : index + 1,
      status,
      sourceStatus: source.status,
      nextAction: status === 'SOURCE_GATED'
        ? `Repair ${battlecard.sourceKey} source to strengthen this moat.`
        : `Package ${battlecard.label} counter for sales and board proof.`
    };
    return {
      ...row,
      proofHash: createTransformationProof({
        row,
        industryKey: profile.industryKey,
        version: EXECUTIVE_TRANSFORMATION_VERSION
      })
    };
  }).sort((left, right) => left.priority - right.priority)
);

/**
 * @function buildPriorityActions
 * @description Resolves the highest-value next actions from sources, integrations and trust rows.
 * @param {Object} params - Priority inputs.
 * @returns {Array<Object>} Prioritized executive actions.
 * @collaboration The roadmap becomes daily execution only when the dashboard names the next command.
 */
export const buildPriorityActions = ({
  sourceRows = [],
  insightRows = [],
  integrationRows = [],
  trustRows = [],
  moatRows = []
} = {}) => {
  const sourceGaps = sourceRows
    .filter(source => !source.live)
    .map(source => ({
      id: `repair_${source.key}`,
      lane: 'SOURCE_REPAIR',
      title: `Repair ${String(source.key || 'source').toUpperCase()} source`,
      status: 'SOURCE_REQUIRED',
      route: '/settings/data-sources'
    }));
  const insightGaps = insightRows
    .filter(row => String(row.status || '').includes('SOURCE') || ['RISK', 'SOURCE_GATED'].includes(row.status))
    .slice(0, 2)
    .map(row => ({
      id: `insight_${row.id}`,
      lane: row.lane,
      title: row.actionLabel,
      status: row.status,
      route: '/executive'
    }));
  const connectorMoves = integrationRows
    .filter(row => row.status !== 'CONNECTED')
    .slice(0, 2)
    .map(row => ({
      id: `integration_${row.key}`,
      lane: row.lane,
      title: `Connect ${row.label}`,
      status: row.status,
      route: row.route
    }));
  const trustMoves = trustRows
    .filter(row => !['EVIDENCE_READY', 'EXPORT_READY', 'RBAC_ACTIVE'].includes(row.status))
    .slice(0, 1)
    .map(row => ({
      id: `trust_${row.key}`,
      lane: row.lane,
      title: row.nextAction,
      status: row.status,
      route: '/compliance'
    }));
  const moatMoves = moatRows
    .filter(row => row.status !== 'MOAT_LIVE')
    .slice(0, 1)
    .map(row => ({
      id: `moat_${row.key}`,
      lane: 'COMPETITION',
      title: row.nextAction,
      status: row.status,
      route: '/executive'
    }));

  return [
    ...sourceGaps,
    ...insightGaps,
    ...connectorMoves,
    ...trustMoves,
    ...moatMoves
  ].slice(0, 7).map((action, index) => ({
    ...action,
    priority: index + 1,
    proofHash: createTransformationProof({
      action,
      version: EXECUTIVE_TRANSFORMATION_VERSION
    })
  }));
};

/**
 * @function buildExecutiveTransformationPlaybook
 * @description Builds the full executive transformation playbook consumed by the dashboard.
 * @param {Object} params - Playbook inputs.
 * @returns {Object} Transformation playbook.
 * @collaboration This is the roadmap-to-product bridge: ARR phase, AI, integrations, trust and competition in one proofed packet.
 */
export const buildExecutiveTransformationPlaybook = ({
  activeTenant = {},
  financialKPIs = {},
  sourceSnapshot = {},
  sourceRows = [],
  profile = {},
  executiveReadiness = {},
  wilsyAiPlan = [],
  accessDecision = {},
  mutationReceipts = []
} = {}) => {
  const currency = financialKPIs.currency || 'ZAR';
  const revenue = toFiniteNumber(financialKPIs.revenue, 0);
  const arr = toFiniteNumber(financialKPIs.arr, revenue * 1.2);
  const phase = resolveGrowthPhase(arr);
  const phaseProgress = calculatePhaseProgress(phase, arr);
  const insightRows = buildExecutiveInsightRows({
    financialKPIs,
    sourceSnapshot,
    profile,
    executiveReadiness,
    wilsyAiPlan
  });
  const integrationRows = buildIntegrationReadiness({
    activeTenant,
    sourceRows,
    profile
  });
  const trustRows = buildComplianceTrustRows({
    sourceRows,
    profile,
    accessDecision,
    executiveReadiness,
    mutationReceipts
  });
  const moatRows = buildCompetitiveMoatRows({
    sourceRows,
    profile,
    executiveReadiness
  });
  const priorityActions = buildPriorityActions({
    sourceRows,
    insightRows,
    integrationRows,
    trustRows,
    moatRows
  });
  const packet = {
    tenantId: activeTenant?.tenantId || activeTenant?.id || 'UNRESOLVED_TENANT',
    arr,
    currency,
    revenue,
    phaseKey: phase.key,
    phaseProgress,
    readinessScore: executiveReadiness.score || 0,
    liveSources: executiveReadiness.liveSources || 0,
    totalSources: executiveReadiness.totalSources || sourceRows.length,
    priorityActionIds: priorityActions.map(action => action.id),
    version: EXECUTIVE_TRANSFORMATION_VERSION
  };

  return {
    ...packet,
    arrDisplay: formatTransformationMoney(arr, currency),
    revenueDisplay: formatTransformationMoney(revenue, currency),
    phase,
    insightRows,
    integrationRows,
    trustRows,
    moatRows,
    priorityActions,
    proofHash: createTransformationProof(packet)
  };
};

/**
 * @function answerExecutiveNaturalLanguageQuery
 * @description Answers a constrained executive natural-language question from local source-aware playbook data.
 * @param {Object} params - Query inputs.
 * @returns {Object|null} Answer receipt or null when no question is present.
 * @collaboration Executives get useful local answers without pretending a remote LLM or source provided data it did not.
 */
export const answerExecutiveNaturalLanguageQuery = ({
  question = '',
  financialKPIs = {},
  sourceRows = [],
  executiveReadiness = {},
  transformationPlaybook = {}
} = {}) => {
  const cleanQuestion = String(question || '').trim();
  if (!cleanQuestion) return null;
  const normalized = cleanQuestion.toLowerCase();
  const currency = financialKPIs.currency || transformationPlaybook.currency || 'ZAR';
  const arr = toFiniteNumber(financialKPIs.arr, transformationPlaybook.arr || 0);
  const revenue = toFiniteNumber(financialKPIs.revenue, transformationPlaybook.revenue || 0);
  let intent = 'next_action';
  let answer = transformationPlaybook.priorityActions?.[0]?.title || 'Rebase sources and accept the highest-priority executive work order.';
  let evidenceRows = transformationPlaybook.priorityActions?.slice(0, 3).map(action => action.title) || [];

  if (/(arr|revenue|forecast|growth|mrr)/.test(normalized)) {
    intent = 'revenue_forecast';
    const forecast = transformationPlaybook.insightRows?.find(row => row.id === 'predictive_arr_forecast');
    answer = `${transformationPlaybook.phase?.label || 'PHASE_PENDING'}: ARR ${formatTransformationMoney(arr, currency)} and revenue ${formatTransformationMoney(revenue, currency)}. ${forecast?.signal || 'Forecast requires live finance.'}`;
    evidenceRows = [transformationPlaybook.phase?.target, forecast?.status, forecast?.proofHash?.slice(0, 18)].filter(Boolean);
  } else if (/(source|truth|data|live|silent)/.test(normalized)) {
    intent = 'source_posture';
    answer = `${executiveReadiness.liveSources || 0}/${executiveReadiness.totalSources || sourceRows.length} executive sources are live.`;
    evidenceRows = sourceRows.map(source => `${source.key}:${source.status}`);
  } else if (/(board|packet|report|director|minute|meeting)/.test(normalized)) {
    intent = 'board_readiness';
    const board = transformationPlaybook.insightRows?.find(row => row.id === 'board_packet_automation');
    answer = `${board?.status || 'BOARD_SOURCE_PENDING'}: ${board?.signal || 'Board automation requires finance and telemetry source posture.'}`;
    evidenceRows = [board?.proofHash?.slice(0, 18), transformationPlaybook.proofHash?.slice(0, 18)].filter(Boolean);
  } else if (/(compliance|audit|soc|popia|gdpr|trust|rbac|sso)/.test(normalized)) {
    intent = 'trust_stack';
    const topTrust = transformationPlaybook.trustRows?.[0];
    answer = `${topTrust?.label || 'Trust stack'} is ${topTrust?.status || 'SOURCE_REQUIRED'} with score ${topTrust?.score || 0}.`;
    evidenceRows = transformationPlaybook.trustRows?.slice(0, 4).map(row => `${row.label}:${row.status}`) || [];
  } else if (/(integration|quickbooks|xero|sap|netsuite|salesforce|hubspot|slack|teams|sso)/.test(normalized)) {
    intent = 'integration_path';
    const connector = transformationPlaybook.integrationRows?.find(row => row.status !== 'CONNECTED') || transformationPlaybook.integrationRows?.[0];
    answer = connector ? `${connector.label} is ${connector.status}. ${connector.nextAction}` : 'Connector playbook requires tenant context.';
    evidenceRows = transformationPlaybook.integrationRows?.slice(0, 4).map(row => `${row.label}:${row.status}`) || [];
  } else if (/(competition|competitor|moat|diligent|workiva|power bi|tableau|beat)/.test(normalized)) {
    intent = 'competitive_moat';
    const moat = transformationPlaybook.moatRows?.[0];
    answer = `${moat?.label || 'Competitive moat'}: ${moat?.wilsyMove || 'Wilsy OS differentiates through proofed executive operations.'}`;
    evidenceRows = transformationPlaybook.moatRows?.slice(0, 4).map(row => `${row.label}:${row.status}`) || [];
  }

  const packet = {
    question: cleanQuestion,
    intent,
    answer,
    evidenceRows,
    arr,
    readinessScore: executiveReadiness.score || 0,
    playbookProof: transformationPlaybook.proofHash || null,
    generatedAt: new Date().toISOString(),
    version: EXECUTIVE_TRANSFORMATION_VERSION
  };

  return {
    ...packet,
    proofHash: createTransformationProof(packet)
  };
};

export default {
  EXECUTIVE_TRANSFORMATION_VERSION,
  EXECUTIVE_GROWTH_PHASES,
  EXECUTIVE_CONNECTOR_PLAYBOOKS,
  EXECUTIVE_TRUST_PLAYBOOKS,
  EXECUTIVE_COMPETITIVE_PLAYBOOKS,
  stableTransformationStringify,
  createTransformationProof,
  resolveGrowthPhase,
  calculatePhaseProgress,
  buildExecutiveInsightRows,
  buildIntegrationReadiness,
  buildComplianceTrustRows,
  buildCompetitiveMoatRows,
  buildPriorityActions,
  buildExecutiveTransformationPlaybook,
  answerExecutiveNaturalLanguageQuery
};
