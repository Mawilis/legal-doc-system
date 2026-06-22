/* eslint-disable */
/**
 * WILSY OS — BACKEND SOURCE EVIDENCE REQUIREMENTS
 * VERSION: 1.0.0-PRODUCTION-REPAIR-PLAN
 *
 * Purpose:
 * - Enriches /api/source-registry/verify responses with connector-level repair intelligence.
 * - Does not mark anything VERIFIED.
 * - Does not fabricate evidence.
 * - Only explains what evidence is required before verification may succeed.
 */

export const SOURCE_EVIDENCE_CONNECTORS = Object.freeze({
  CRM: {
    label: 'CRM / Contract Ledger',
    methods: ['getTenantProfile', 'getContractLedger', 'getCounterpartyAuthority'],
    evidenceNeeded: [
      'Counterparty legal name',
      'Contract or agreement identifier',
      'Authorized signatory evidence',
      'Customer / tenant record',
    ],
    operatorAction:
      'Connect CRM or contract-ledger evidence for counterparty identity, agreement records and authority checks.',
  },
  FINANCE: {
    label: 'Finance Ledger',
    methods: [
      'getRevenueYTD',
      'getAnnualRecurringRevenue',
      'getRunwayMonths',
      'getContractValueLedger',
    ],
    evidenceNeeded: [
      'Invoice / quote / contract value record',
      'Revenue or ledger entry',
      'Payment / receivable context',
      'Finance approval or director control',
    ],
    operatorAction:
      'Connect finance-ledger evidence for commercial value, revenue, invoice, runway or approval checks.',
  },
  HR: {
    label: 'People / HRIS Registry',
    methods: ['getEmployeeProfile', 'getIPAssignment', 'getAuthorityRecord'],
    evidenceNeeded: [
      'Employee or contractor profile',
      'Role / authority record',
      'IP assignment evidence',
      'Employment lifecycle record',
    ],
    operatorAction:
      'Connect HRIS evidence for employee, contractor, authority and IP assignment checks.',
  },
  COMPLIANCE: {
    label: 'Compliance Registry',
    methods: ['getPOPIAStatus', 'getGDPRStatus', 'getSOC2Status', 'getJurisdictionControls'],
    evidenceNeeded: [
      'POPIA / GDPR / SOC2 control record',
      'Jurisdiction control mapping',
      'Policy approval / review evidence',
      'Retention / security safeguard evidence',
    ],
    operatorAction:
      'Connect compliance evidence for POPIA, GDPR, SOC2, policy and jurisdiction control checks.',
  },
  TELEMETRY: {
    label: 'Telemetry / Reliability Evidence',
    methods: ['getUptime', 'getIncidentLog', 'getChangeControlLog'],
    evidenceNeeded: [
      'Uptime / SLA metric',
      'Incident register',
      'Change control record',
      'Reliability or security telemetry',
    ],
    operatorAction:
      'Connect telemetry evidence for uptime, incidents, service levels, reliability and change-control checks.',
  },
});

const RULES = Object.freeze([
  {
    key: 'NDA_CONFIDENTIALITY',
    label: 'NDA & Confidentiality',
    pattern: /nda|non-disclosure|confidentiality|mutual non-disclosure/i,
    connectors: ['CRM', 'COMPLIANCE'],
  },
  {
    key: 'SERVICES_COMMERCIAL',
    label: 'Services & Commercial',
    pattern: /master services|statement of work|sow|service agreement|terms of service|commercial/i,
    connectors: ['CRM', 'FINANCE', 'COMPLIANCE'],
  },
  {
    key: 'SAAS_SUBSCRIPTION',
    label: 'SaaS & Subscription',
    pattern: /saas|subscription|service level|sla|uptime|availability/i,
    connectors: ['CRM', 'FINANCE', 'TELEMETRY', 'COMPLIANCE'],
  },
  {
    key: 'PRIVACY_DATA',
    label: 'Privacy & Data',
    pattern: /privacy|popia|gdpr|paia|data processing|cookie|data/i,
    connectors: ['COMPLIANCE', 'CRM'],
  },
  {
    key: 'GOVERNANCE_COMPLIANCE',
    label: 'Governance & Compliance',
    pattern: /board|governance|resolution|risk|audit|compliance|policy/i,
    connectors: ['COMPLIANCE'],
  },
  {
    key: 'FINANCE_PROCUREMENT',
    label: 'Finance & Procurement',
    pattern:
      /invoice|tax|credit note|quote|quotation|purchase|supplier|vendor|rfp|payment|finance/i,
    connectors: ['FINANCE', 'COMPLIANCE'],
  },
  {
    key: 'PEOPLE_OPERATIONS',
    label: 'People & Operations',
    pattern:
      /employment|employee|offer letter|contractor|hr|handbook|onboarding|offboarding|disciplinary|leave/i,
    connectors: ['HR', 'COMPLIANCE'],
  },
  {
    key: 'PROJECT_DELIVERY',
    label: 'Project Delivery',
    pattern:
      /project|evm|milestone|variation|payment certificate|site instruction|statement of work/i,
    connectors: ['FINANCE', 'TELEMETRY', 'COMPLIANCE'],
  },
  {
    key: 'SECURITY_IT',
    label: 'Security & IT',
    pattern: /security|access|backup|vulnerability|change advisory|incident|change control/i,
    connectors: ['TELEMETRY', 'COMPLIANCE'],
  },
]);

function unique(values = []) {
  return Array.from(new Set(values.filter(Boolean)));
}

function normalizeStatus(value = '') {
  const status = String(value || '').toUpperCase();

  if (['VERIFIED', 'READY_FOR_ANCHOR'].includes(status)) return status;
  if (['ERROR', 'MISSING', 'BLOCKED', 'PENDING', 'NOT_EVALUATED'].includes(status)) return status;

  return 'MISSING';
}

export function classifySourceEvidenceArtifact(artifact = {}) {
  const text =
    `${artifact.title || ''} ${artifact.type || ''} ${artifact.category || ''} ${artifact.id || ''}`.toLowerCase();

  return (
    RULES.find((rule) => rule.pattern.test(text)) || {
      key: 'OTHER',
      label: 'Other Legal Artifacts',
      connectors: ['COMPLIANCE'],
    }
  );
}

export function resolveSourceEvidenceRequirements(artifact = {}) {
  const rule = classifySourceEvidenceArtifact(artifact);
  const connectors = rule.connectors
    .map((key) => ({
      key,
      ...SOURCE_EVIDENCE_CONNECTORS[key],
    }))
    .filter((connector) => connector.label);

  return {
    family: rule.label,
    familyKey: rule.key,
    requiredConnectors: connectors.map((connector) => connector.key),
    connectorLabels: connectors.map((connector) => connector.label),
    requiredMethods: unique(connectors.flatMap((connector) => connector.methods || [])),
    evidenceNeeded: unique(connectors.flatMap((connector) => connector.evidenceNeeded || [])),
    operatorAction: connectors.map((connector) => connector.operatorAction).join(' '),
    primaryConnector: connectors[0]?.label || 'Compliance Registry',
  };
}

export function enrichSourceEvidenceFinding(finding = {}) {
  const status = normalizeStatus(
    finding.status || finding.evidenceStatus || finding.sourceStatus || finding.result
  );
  const requirements = resolveSourceEvidenceRequirements(finding);

  return {
    id:
      finding.id ||
      finding.artifactId ||
      finding.type ||
      finding.sourceId ||
      finding.title ||
      'SOURCE_REQUIREMENT',
    title:
      finding.title ||
      finding.artifactTitle ||
      finding.name ||
      finding.label ||
      finding.type ||
      'Source requirement',
    type: finding.type || finding.artifactType || finding.id || '',
    category: finding.category || requirements.family,
    status,
    connector:
      finding.connector && finding.connector !== 'Source Registry'
        ? finding.connector
        : requirements.primaryConnector,
    sourceFamily: requirements.family,
    requiredConnectors: requirements.connectorLabels,
    requiredMethods: requirements.requiredMethods,
    evidenceNeeded: requirements.evidenceNeeded,
    operatorAction: requirements.operatorAction,
    method:
      finding.method ||
      finding.requiredMethod ||
      finding.check ||
      requirements.requiredMethods.slice(0, 3).join(' · '),
    message:
      finding.message ||
      finding.reason ||
      finding.error ||
      finding.detail ||
      'Live evidence required before VERIFIED status.',
    severity: status === 'ERROR' || status === 'BLOCKED' ? 'HIGH' : 'MEDIUM',
    fakeVerified: false,
  };
}

function extractPayloadFindings(payload = {}, requestBody = {}) {
  const data = payload?.data || payload || {};
  const candidates = [
    data.artifacts,
    data.results,
    data.findings,
    data.verificationResults,
    data.sourceResults,
    data.requirements,
    data.items,
    data.evidence,
    data.errors,
    data.missing,
    requestBody.artifacts,
    requestBody.catalog,
    requestBody.artifact ? [requestBody.artifact] : null,
  ];

  const rows = [];

  function push(item = {}, fallbackStatus = '') {
    if (!item || typeof item !== 'object') return;

    const status = normalizeStatus(
      item.status ||
        item.evidenceStatus ||
        item.sourceStatus ||
        item.result ||
        fallbackStatus ||
        'MISSING'
    );

    if (status === 'VERIFIED' || status === 'READY_FOR_ANCHOR') return;

    rows.push(enrichSourceEvidenceFinding({ ...item, status }));
  }

  candidates.forEach((candidate) => {
    if (Array.isArray(candidate)) {
      candidate.forEach((item) => push(item));
    } else if (candidate && typeof candidate === 'object') {
      Object.entries(candidate).forEach(([key, value]) => {
        if (Array.isArray(value)) {
          value.forEach((item) => push({ id: key, ...item }));
        } else if (value && typeof value === 'object') {
          push({ id: key, ...value });
        } else {
          push({ id: key, title: key, message: String(value) });
        }
      });
    }
  });

  const deduped = [];
  const seen = new Set();

  rows.forEach((row) => {
    const key = `${row.id}|${row.title}|${row.connector}|${row.status}`;
    if (seen.has(key)) return;
    seen.add(key);
    deduped.push(row);
  });

  return deduped;
}

export function buildSourceEvidenceRepairPlan(payload = {}, requestBody = {}) {
  const findings = extractPayloadFindings(payload, requestBody);
  const byConnector = {};
  const byStatus = {};
  const byFamily = {};

  findings.forEach((finding) => {
    byConnector[finding.connector] = (byConnector[finding.connector] || 0) + 1;
    byStatus[finding.status] = (byStatus[finding.status] || 0) + 1;
    byFamily[finding.sourceFamily] = (byFamily[finding.sourceFamily] || 0) + 1;
  });

  return {
    status: findings.length ? 'ACTION_REQUIRED' : 'CLEAR',
    total: findings.length,
    byConnector,
    byStatus,
    byFamily,
    findings,
    generatedAt: new Date().toISOString(),
    truthPolicy: 'NO_FAKE_VERIFIED',
  };
}

export function attachSourceEvidenceRepairPlan(payload = {}, requestBody = {}) {
  const repairPlan = buildSourceEvidenceRepairPlan(payload, requestBody);
  const nextPayload = {
    ...(payload || {}),
    data: {
      ...((payload || {}).data || {}),
      repairPlan,
      sourceEvidenceRepairPlan: repairPlan,
    },
  };

  return nextPayload;
}

export default Object.freeze({
  SOURCE_EVIDENCE_CONNECTORS,
  classifySourceEvidenceArtifact,
  resolveSourceEvidenceRequirements,
  enrichSourceEvidenceFinding,
  buildSourceEvidenceRepairPlan,
  attachSourceEvidenceRepairPlan,
});
