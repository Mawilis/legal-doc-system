/* eslint-disable */
import React, { useEffect, useMemo, useState, useRef} from 'react';
import { createPortal } from 'react-dom';
import styles from './WilsyCrmSetupControlPlane.module.css';

/**
 * @function buildSetupDomains
 * @description Builds setup operating domains for authority, revenue flow, schema, automation, custody, integration, and board proof.
 * @returns {Array<Object>} Setup domains.
 * @collaboration CRM setup workbench, domain rail, command rail, operating view area, authority rail, and review queue.
 */
function buildSetupDomains() {
  return [
    {
      id: 'authority',
      label: 'Authority',
      title: 'Identity and Access Authority',
      score: 98,
      exposure: 0,
      purpose: 'Control who sees, changes, exports, deletes, approves, and delegates CRM power.',
      controls: [
        {
          id: 'authority-graph',
          name: 'Authority Graph',
          owner: 'Security Admin',
          risk: 'Critical',
          state: 'Sealed',
          engine: 'Sovereign Authority Graph',
          benefit: 'Shows every access path across user, role, field, export, delete, approval, and delegation power.',
          workItems: ['Review role chains', 'Check export rights', 'Verify approval owners', 'Inspect field exposure'],
          surfaces: ['Users', 'Profiles', 'Roles', 'Fields', 'Exports', 'Approvals'],
          signal: 'Board-ready access clarity',
        },
        {
          id: 'field-exposure',
          name: 'Field Exposure Matrix',
          owner: 'Compliance Admin',
          risk: 'Critical',
          state: 'Watched',
          engine: 'Field Exposure Engine',
          benefit: 'Finds sensitive fields visible to the wrong role before customer or financial data is exposed.',
          workItems: ['Scan sensitive fields', 'Review visibility', 'Check edit rights', 'Lock export scope'],
          surfaces: ['Leads', 'Contacts', 'Accounts', 'Fields', 'Exports'],
          signal: 'Sensitive-data control proof',
        },
        {
          id: 'delegation-gate',
          name: 'Delegation Gate',
          owner: 'Tenant Admin',
          risk: 'High',
          state: 'Ready',
          engine: 'Delegation Drift Detector',
          benefit: 'Finds delegated authority chains that create hidden administrator power.',
          workItems: ['Review delegated roles', 'Check admin overlap', 'Confirm owner approval', 'Stage cleanup'],
          surfaces: ['Users', 'Teams', 'Roles', 'Approvals'],
          signal: 'Privilege escalation control',
        },
      ],
    },
    {
      id: 'revenue',
      label: 'Revenue',
      title: 'Revenue Flow Governance',
      score: 96,
      exposure: 1,
      purpose: 'Remove setup friction that slows lead capture, qualification, handoff, and close velocity.',
      controls: [
        {
          id: 'revenue-friction',
          name: 'Revenue Friction Index',
          owner: 'Sales Ops',
          risk: 'High',
          state: 'Watched',
          engine: 'Revenue Flow Sentinel',
          benefit: 'Finds setup decisions that block speed across capture, qualification, conversion, and follow-up.',
          workItems: ['Inspect required fields', 'Review stage gates', 'Check handoff owners', 'Measure conversion blockers'],
          surfaces: ['Leads', 'Meetings', 'Tasks', 'Deals'],
          signal: 'Revenue execution evidence',
        },
        {
          id: 'lead-path',
          name: 'Lead Path Contract',
          owner: 'CRM Architect',
          risk: 'Medium',
          state: 'Ready',
          engine: 'Lead Path Verifier',
          benefit: 'Ensures every lead stage has owner, next action, required data, and proof checkpoint.',
          workItems: ['Verify lead stages', 'Check next actions', 'Review owner rules', 'Confirm stage proof'],
          surfaces: ['Leads', 'Pipeline', 'Tasks'],
          signal: 'Repeatable sales operations',
        },
        {
          id: 'handoff-integrity',
          name: 'Handoff Integrity',
          owner: 'Customer Success',
          risk: 'Medium',
          state: 'Ready',
          engine: 'Handoff Loss Scanner',
          benefit: 'Finds weak ownership between leads, meetings, tasks, accounts, and customer success.',
          workItems: ['Map handoff owners', 'Check missing tasks', 'Review meeting links', 'Confirm account transfer'],
          surfaces: ['Meetings', 'Tasks', 'Accounts'],
          signal: 'Customer continuity proof',
        },
      ],
    },
    {
      id: 'schema',
      label: 'Schema',
      title: 'Modules, Fields, Layouts',
      score: 97,
      exposure: 0,
      purpose: 'Keep modules, fields, and layouts clean so the CRM remains fast and useful.',
      controls: [
        {
          id: 'schema-registry',
          name: 'Schema Registry',
          owner: 'CRM Architect',
          risk: 'High',
          state: 'Sealed',
          engine: 'Schema Entropy Scanner',
          benefit: 'Finds duplicate fields, unused fields, weak labels, layout sprawl, and structure debt.',
          workItems: ['Scan duplicate fields', 'Review unused fields', 'Check required fields', 'Clean layout load'],
          surfaces: ['Modules', 'Fields', 'Layouts'],
          signal: 'Clean operating data model',
        },
        {
          id: 'layout-command',
          name: 'Layout Command Matrix',
          owner: 'Sales Ops',
          risk: 'Medium',
          state: 'Ready',
          engine: 'Layout Load Balancer',
          benefit: 'Keeps every layout focused on role, stage, source, and next action.',
          workItems: ['Review role layouts', 'Check field order', 'Remove clutter', 'Align stage fields'],
          surfaces: ['Layouts', 'Leads', 'Deals'],
          signal: 'Operator speed proof',
        },
        {
          id: 'module-expansion',
          name: 'Module Expansion Gate',
          owner: 'Platform Admin',
          risk: 'Medium',
          state: 'Ready',
          engine: 'Module ROI Gate',
          benefit: 'Prevents custom modules from becoming isolated databases with no owner or proof.',
          workItems: ['Review module need', 'Check owner', 'Confirm record links', 'Approve expansion'],
          surfaces: ['Modules', 'Records', 'Reports'],
          signal: 'Controlled scale posture',
        },
      ],
    },
    {
      id: 'automation',
      label: 'Automation',
      title: 'Workflow and AI Control',
      score: 95,
      exposure: 2,
      purpose: 'Keep automation safe, explainable, collision-free, and tied to work outcomes.',
      controls: [
        {
          id: 'collision-scanner',
          name: 'Automation Collision Scanner',
          owner: 'Automation Admin',
          risk: 'Critical',
          state: 'Watched',
          engine: 'Workflow Collision Engine',
          benefit: 'Finds conflicting rules, duplicate triggers, timing conflicts, and approval loops.',
          workItems: ['Scan triggers', 'Check timing conflicts', 'Review approval loops', 'Confirm rule owner'],
          surfaces: ['Workflows', 'Approvals', 'Tasks'],
          signal: 'Automation risk control',
        },
        {
          id: 'ai-boundary',
          name: 'AI Boundary Policy',
          owner: 'Compliance Admin',
          risk: 'Critical',
          state: 'Sealed',
          engine: 'AI Evidence Boundary',
          benefit: 'Controls what AI may summarize, score, recommend, or block based on trusted CRM evidence.',
          workItems: ['Review AI scope', 'Check evidence inputs', 'Limit sensitive actions', 'Confirm human review'],
          surfaces: ['AI', 'Scores', 'Summaries', 'Approvals'],
          signal: 'Governed AI posture',
        },
        {
          id: 'approval-rails',
          name: 'Approval Rails',
          owner: 'Executive Admin',
          risk: 'High',
          state: 'Ready',
          engine: 'Approval Delay Predictor',
          benefit: 'Finds approval delays before decisions stall leads, deals, or customer follow-up.',
          workItems: ['Review approval owners', 'Check delays', 'Confirm backup approvers', 'Stage escalation'],
          surfaces: ['Approvals', 'Deals', 'Tasks'],
          signal: 'Decision velocity proof',
        },
      ],
    },
    {
      id: 'custody',
      label: 'Custody',
      title: 'Data Custody and Recovery',
      score: 99,
      exposure: 0,
      purpose: 'Control imports, exports, recovery, retention, and deletion from one custody lane.',
      controls: [
        {
          id: 'import-quality',
          name: 'Import Quality Gate',
          owner: 'Data Admin',
          risk: 'High',
          state: 'Ready',
          engine: 'Source Trust Scorer',
          benefit: 'Scores imported data by source, duplicates, missing proof, field quality, and owner gaps.',
          workItems: ['Check source trust', 'Review duplicates', 'Confirm owner', 'Validate required fields'],
          surfaces: ['Imports', 'Leads', 'Contacts'],
          signal: 'Trusted data intake',
        },
        {
          id: 'export-authority',
          name: 'Export Authority Gate',
          owner: 'Compliance Admin',
          risk: 'Critical',
          state: 'Sealed',
          engine: 'Export Blast Radius',
          benefit: 'Shows who can export what, why, when, and how much customer data may leave the CRM.',
          workItems: ['Review export roles', 'Check field scope', 'Confirm approval owner', 'Limit data volume'],
          surfaces: ['Exports', 'Fields', 'Users'],
          signal: 'Data leakage control',
        },
        {
          id: 'recovery-proof',
          name: 'Recovery Proof',
          owner: 'Platform Admin',
          risk: 'Critical',
          state: 'Ready',
          engine: 'Recovery Confidence Index',
          benefit: 'Measures restore readiness, custody chain, retention posture, and recovery confidence.',
          workItems: ['Review recovery policy', 'Check retention', 'Confirm custody owner', 'Stage proof review'],
          surfaces: ['Recovery', 'Backups', 'Records'],
          signal: 'Operational resilience proof',
        },
      ],
    },
    {
      id: 'integration',
      label: 'Integration',
      title: 'API, Connector, and Source Trust',
      score: 94,
      exposure: 3,
      purpose: 'Keep every connector accountable, source-aware, reliable, and restricted to its purpose.',
      controls: [
        {
          id: 'source-trust',
          name: 'Source Trust Registry',
          owner: 'Integration Admin',
          risk: 'High',
          state: 'Watched',
          engine: 'Connector Trust Rank',
          benefit: 'Ranks every source by identity, reliability, freshness, payload quality, and ownership.',
          workItems: ['Rank sources', 'Check freshness', 'Review failed syncs', 'Confirm owner'],
          surfaces: ['Sources', 'Connectors', 'Live Leads'],
          signal: 'Integration governance',
        },
        {
          id: 'access-token',
          name: 'Access Token Posture',
          owner: 'Security Admin',
          risk: 'Critical',
          state: 'Sealed',
          engine: 'Secret Surface Monitor',
          benefit: 'Maps token scope, expiry posture, connector ownership, and isolation boundaries.',
          workItems: ['Review token scope', 'Check expiry', 'Confirm owner', 'Limit permissions'],
          surfaces: ['Connectors', 'Security', 'Sources'],
          signal: 'Secret control posture',
        },
        {
          id: 'connector-sla',
          name: 'Connector SLA Watch',
          owner: 'Platform Admin',
          risk: 'Medium',
          state: 'Ready',
          engine: 'Connector Reliability Index',
          benefit: 'Tracks connector freshness, failures, retry posture, and operating confidence.',
          workItems: ['Check reliability', 'Review retries', 'Confirm freshness', 'Stage repair'],
          surfaces: ['Connectors', 'Sources', 'Sync'],
          signal: 'Reliable growth engine',
        },
      ],
    },
    {
      id: 'board',
      label: 'Board Proof',
      title: 'Investor and Regulator Proof',
      score: 100,
      exposure: 0,
      purpose: 'Turn setup posture into executive, investor, audit, and regulator proof.',
      controls: [
        {
          id: 'proof-compiler',
          name: 'Investor Proof Compiler',
          owner: 'Executive Admin',
          risk: 'Critical',
          state: 'Sealed',
          engine: 'Investor Proof Engine',
          benefit: 'Compiles authority, custody, automation, revenue, and audit posture into one board surface.',
          workItems: ['Compile authority proof', 'Compile custody proof', 'Compile automation proof', 'Review board pack'],
          surfaces: ['Board Pack', 'Audit', 'Evidence'],
          signal: 'Investor diligence pack',
        },
        {
          id: 'policy-drift',
          name: 'Policy Drift Radar',
          owner: 'Compliance Officer',
          risk: 'Critical',
          state: 'Watched',
          engine: 'Policy Drift Radar',
          benefit: 'Finds drift between policy intent, user authority, automation, and data movement.',
          workItems: ['Scan drift', 'Review exceptions', 'Confirm owner', 'Stage correction'],
          surfaces: ['Policies', 'Roles', 'Automation'],
          signal: 'Governance discipline',
        },
        {
          id: 'exception-heatmap',
          name: 'Exception Heatmap',
          owner: 'Audit Admin',
          risk: 'High',
          state: 'Ready',
          engine: 'Exception Heatmap',
          benefit: 'Shows unresolved setup exceptions by domain, owner, risk, and time pressure.',
          workItems: ['Review exceptions', 'Assign owner', 'Set priority', 'Stage review'],
          surfaces: ['Audit', 'Evidence', 'Board Pack'],
          signal: 'Audit-ready operating control',
        },
      ],
    },
  ];
}

/**
 * @function buildEvidencePack
 * @description Builds the evidence labels used by the authority rail.
 * @returns {Array<string>} Evidence labels.
 * @collaboration Evidence rail, authority inspector, review queue, and release gate.
 */
function buildEvidencePack() {
  return [
    'Tenant authority',
    'Operator identity',
    'Control owner',
    'Policy intent',
    'Risk rating',
    'Impact summary',
    'Review outcome',
    'Evidence receipt',
  ];
}

/**
 * @function calculatePosture
 * @description Calculates setup posture from scores, exposure, and review queue size.
 * @param {Array<Object>} domains - Setup domains.
 * @param {number} queueSize - Current queue size.
 * @returns {Object} Current setup posture.
 * @collaboration Domain rail, score rail, authority rail, and review queue.
 */
function calculatePosture(domains = [], queueSize = 0) {
  const scoreTotal = domains.reduce((total, domain) => total + Number(domain.score || 0), 0);
  const exposure = domains.reduce((total, domain) => total + Number(domain.exposure || 0), 0);
  const score = domains.length ? Math.round(scoreTotal / domains.length) : 0;

  return {
    score,
    exposure,
    queueSize,
    label: queueSize ? 'Review active' : 'Review required',
  };
}

/**
 * @function createReviewTicket
 * @description Creates a local review ticket for the selected setup control.
 * @param {Object} domain - Active domain.
 * @param {Object} control - Active control.
 * @returns {Object} Review ticket.
 * @collaboration Review queue, command rail, authority rail, and work area.
 */
function createReviewTicket(domain = {}, control = {}) {
  const generatedAt = new Date().toISOString();
  const compactStamp = generatedAt.replace(/[-:.TZ]/g, '');

  return {
    id: `SETUP_REVIEW_${compactStamp}`,
    domain: domain.label,
    domainId: domain.id,
    controlId: control.id,
    title: control.name,
    owner: control.owner,
    risk: control.risk,
    state: control.state,
    engine: control.engine,
    signal: control.signal,
    status: 'Staged review',
    generatedAt,
  };
}

/**
 * @function resolveToneClass
 * @description Resolves CSS tone for risk or state labels.
 * @param {string} value - Risk or state label.
 * @returns {string} CSS class.
 * @collaboration View area badges, right authority rail, queue ledger, and control rows.
 */
function resolveToneClass(value = '') {
  const normalized = String(value || '').toLowerCase();

  if (normalized.includes('critical')) {
    return styles.toneCritical;
  }

  if (normalized.includes('high') || normalized.includes('watched')) {
    return styles.toneHigh;
  }

  if (normalized.includes('sealed') || normalized.includes('ready')) {
    return styles.toneReady;
  }

  return styles.toneNeutral;
}


/* WILSY_P60K3F_DECLARATION_SAFE_LIVE_WIRING */

/**
 * @function resolveWilsySetupReviewStorageValue
 * @description Resolves browser storage values for setup review tenant, operator, and token context.
 * @param {Array<string>} keys - Candidate storage keys.
 * @param {string} fallback - Fallback value.
 * @returns {string} Resolved storage value.
 * @collaboration Setup Control Plane, tenant evidence, operator evidence, and CRM setup backend commands.
 */
function resolveWilsySetupReviewStorageValue(keys = [], fallback = '') {
  if (typeof window === 'undefined') return fallback;

  for (const key of keys) {
    const value = window.localStorage?.getItem(key) || window.sessionStorage?.getItem(key);

    if (value) return value;
  }

  return fallback;
}

/**
 * @function buildWilsySetupReviewLivePayload
 * @description Builds institutionalHeaders and strikePayload evidence for live CRM setup review commands.
 * @param {Object} params - Payload parameters.
 * @returns {Object} Evidence-bearing backend command payload.
 * @collaboration ProductionHardening bridge, setup review backend routes, Packet Console receipts, and tenant audit posture.
 */
function buildWilsySetupReviewLivePayload({ route, ticket = {}, domain = {}, control = {}, lens = 'Authority' } = {}) {
  const generatedAt = new Date().toISOString();
  const tenantId = resolveWilsySetupReviewStorageValue(['tenantId', 'wilsyTenantId', 'x-tenant-id'], 'MASTER');
  const operatorId = resolveWilsySetupReviewStorageValue(
    ['operatorId', 'wilsyOperatorId', 'userId', 'wilsyUserId', 'adminId'],
    'wilsy-sovereign-root'
  );
  const commandSurface = 'CRM_SETUP_OPERATING_CONTROLS';
  const packetId = ticket.packetId || ticket.id || `SETUP_REVIEW_${Date.now()}`;
  const controlId = ticket.controlId || control.id || 'setup-control';

  const institutionalHeaders = {
    tenantId,
    operatorId,
    userId: operatorId,
    route,
    commandSurface,
    generatedAt,
    timestamp: generatedAt,
    source: 'CRM_SETUP_CONTROL_PLANE',
    packetId,
    domainId: ticket.domainId || domain.id || 'setup',
    controlId,
  };

  return {
    tenantId,
    operatorId,
    userId: operatorId,
    route,
    commandSurface,
    generatedAt,
    timestamp: generatedAt,
    packetId,
    id: packetId,
    domainId: ticket.domainId || domain.id || 'setup',
    domainLabel: ticket.domainLabel || domain.title || domain.label || 'Setup',
    controlId,
    controlName: ticket.controlName || ticket.title || control.name || 'Setup Control',
    title: ticket.title || ticket.controlName || control.name || 'Setup Control',
    lens: ticket.lens || lens,
    owner: ticket.owner || control.owner || 'Security Admin',
    risk: ticket.risk || control.risk || 'CRITICAL',
    state: ticket.state || control.state || 'SEALED',
    benefit: ticket.benefit || control.benefit || '',
    signal: ticket.signal || control.signal || '',
    surfaces: Array.isArray(ticket.surfaces) && ticket.surfaces.length ? ticket.surfaces : control.surfaces || [],
    workItems: Array.isArray(ticket.workItems) && ticket.workItems.length ? ticket.workItems : control.workItems || [],
    requiredEvidence: Array.isArray(ticket.requiredEvidence) && ticket.requiredEvidence.length
      ? ticket.requiredEvidence
      : [
          'Tenant authority confirmed',
          'Operator identity attached',
          'Control owner assigned',
          'Risk and impact summary prepared',
          'Approval gate waiting for authorized approver',
          'Release gate waiting for evidence receipt',
        ],
    institutionalHeaders,
    strikePayload: {
      tenantId,
      operatorId,
      userId: operatorId,
      route,
      commandSurface,
      generatedAt,
      timestamp: generatedAt,
      headers: institutionalHeaders,
      institutionalHeaders,
    },
  };
}

/**
 * @function normalizeWilsySetupReviewLivePacket
 * @description Normalizes backend setup review packet responses into the existing setup ticket UI shape.
 * @param {Object} packet - Backend packet.
 * @param {Object} fallback - Fallback ticket.
 * @returns {Object} Normalized ticket.
 * @collaboration Backend packet persistence, review queue, Packet Console, audit receipts, and UI state.
 */
function normalizeWilsySetupReviewLivePacket(packet = {}, fallback = {}) {
  const receipts = Array.isArray(packet.receipts) ? packet.receipts : [];
  const auditTrail = Array.isArray(packet.auditTrail) ? packet.auditTrail : [];

  return {
    ...fallback,
    ...packet,
    id: packet.packetId || packet.id || fallback.packetId || fallback.id,
    packetId: packet.packetId || packet.id || fallback.packetId || fallback.id,
    title: packet.title || packet.controlName || fallback.title || fallback.controlName || 'Setup review packet',
    controlName: packet.controlName || packet.title || fallback.controlName || fallback.title,
    surfaces: Array.isArray(packet.surfaces) && packet.surfaces.length ? packet.surfaces : fallback.surfaces || [],
    workItems: Array.isArray(packet.workItems) && packet.workItems.length ? packet.workItems : fallback.workItems || [],
    requiredEvidence: Array.isArray(packet.requiredEvidence) && packet.requiredEvidence.length
      ? packet.requiredEvidence
      : fallback.requiredEvidence || [],
    receipt: packet.receipt || receipts[receipts.length - 1] || fallback.receipt || null,
    auditEvidence: packet.auditEvidence || auditTrail[auditTrail.length - 1] || fallback.auditEvidence || null,
    receipts,
    auditTrail,
    backendLive: true,
  };
}

/**
 * @function requestWilsySetupReviewLiveCommand
 * @description Sends live CRM setup review commands to the backend with tenant and operator evidence.
 * @param {string} route - Backend route.
 * @param {Object} payload - Command payload.
 * @param {string} method - HTTP method.
 * @returns {Promise<Object>} Backend JSON response.
 * @collaboration Setup Control Plane, CRM command routes, institutional evidence, and Packet Console receipts.
 */
async function requestWilsySetupReviewLiveCommand(route, payload = {}, method = 'POST') {
  const apiBase = String(import.meta?.env?.VITE_API_URL || '').replace(/\/$/, '');
  const token = resolveWilsySetupReviewStorageValue(['token', 'authToken', 'wilsyToken', 'accessToken'], '');
  const headers = {
    'Content-Type': 'application/json',
    'X-Tenant-Id': payload.tenantId || 'MASTER',
  };

  if (token) {
    headers.Authorization = token.startsWith('Bearer ') ? token : `Bearer ${token}`;
  }

  const response = await fetch(`${apiBase}${route}`, {
    method,
    headers,
    body: JSON.stringify(payload),
  });

  const data = await response.json().catch(() => ({}));

  if (!response.ok || data?.ok === false || data?.error) {
    const error = new Error(data?.message || data?.error || `Setup review command failed with ${response.status}`);
    error.payload = data;
    throw error;
  }

  return data;
}


/* WILSY_P60K4C_PACKET_OPERATING_UPGRADE */

/**
 * @function resolveWilsySetupReviewProofReceiptId
 * @description Resolves the business-facing proof receipt id from a backend setup review packet.
 * @param {Object} packet - Setup review packet.
 * @returns {string} Proof receipt id.
 * @collaboration Packet Console, backend receipts, audit trail, and copy controls.
 */
function resolveWilsySetupReviewProofReceiptId(packet = {}) {
  const receipts = Array.isArray(packet.receipts) ? packet.receipts : [];
  const latestReceipt = packet.receipt || receipts[receipts.length - 1] || {};

  return latestReceipt.receiptId || 'Receipt pending';
}

/**
 * @function resolveWilsySetupReviewProofHash
 * @description Resolves the tamper-proof hash from a backend setup review packet.
 * @param {Object} packet - Setup review packet.
 * @returns {string} Tamper-proof hash.
 * @collaboration Packet Console, backend receipts, audit trail, and proof-copy workflow.
 */
function resolveWilsySetupReviewProofHash(packet = {}) {
  const receipts = Array.isArray(packet.receipts) ? packet.receipts : [];
  const latestReceipt = packet.receipt || receipts[receipts.length - 1] || {};

  return latestReceipt.receiptHash || 'Proof hash pending';
}

/**
 * @function resolveWilsySetupReviewAuditBusinessStatus
 * @description Converts backend setup review event names into operator-facing business English.
 * @param {Object} packet - Setup review packet.
 * @returns {string} Business-readable audit status.
 * @collaboration Packet Console, audit evidence, receipt ledger, and CRM setup language.
 */
function resolveWilsySetupReviewAuditBusinessStatus(packet = {}) {
  const auditTrail = Array.isArray(packet.auditTrail) ? packet.auditTrail : [];
  const latestAudit = packet.auditEvidence || auditTrail[auditTrail.length - 1] || {};
  const event = String(latestAudit.event || packet.status || '').toUpperCase();

  if (event.includes('REMOVED')) return 'Stage withdrawn with receipt';
  if (event.includes('CLEARED')) return 'Review queue cleared';
  if (event.includes('OPENED')) return 'Review packet opened';
  if (event.includes('STAGED')) return 'Review packet staged';

  return event ? event.replace(/_/g, ' ').toLowerCase().replace(/(^|\s)\S/g, (letter) => letter.toUpperCase()) : 'Awaiting audit status';
}

/**
 * @function resolveWilsySetupReviewEvidencePurpose
 * @description Explains a backend packet evidence requirement in business language.
 * @param {string} evidence - Evidence requirement.
 * @returns {string} Business purpose.
 * @collaboration Required evidence card, approval gate, release gate, and setup review packet.
 */
function resolveWilsySetupReviewEvidencePurpose(evidence = '') {
  const value = String(evidence).toLowerCase();

  if (value.includes('tenant')) return 'Confirms this review belongs to the active tenant before approval can move forward.';
  if (value.includes('operator')) return 'Shows who staged the review and ties the action to audit evidence.';
  if (value.includes('owner')) return 'Identifies who is accountable for resolving this setup control.';
  if (value.includes('risk')) return 'Explains the business impact before approval or release.';
  if (value.includes('approval')) return 'Keeps approval locked until an authorized approver signs off.';
  if (value.includes('release')) return 'Keeps release locked until receipt-backed evidence exists.';

  return 'Required by the backend packet before this setup change can move forward.';
}

/**
 * @function resolveWilsySetupReviewSurfacePurpose
 * @description Explains why an affected CRM surface is linked to the setup review packet.
 * @param {string} surface - Affected surface.
 * @returns {string} Business purpose.
 * @collaboration Affected surfaces card, setup review packet, authority graph, and CRM operating controls.
 */
function resolveWilsySetupReviewSurfacePurpose(surface = '') {
  const value = String(surface).toLowerCase();

  if (value.includes('user')) return 'User access can be changed by this authority control.';
  if (value.includes('profile')) return 'Profile permissions may inherit or expose this authority.';
  if (value.includes('role')) return 'Role chains must be checked before approval.';
  if (value.includes('field')) return 'Field-level exposure may change who can see sensitive CRM data.';
  if (value.includes('export')) return 'Export rights affect data movement and compliance risk.';
  if (value.includes('approval')) return 'Approval owners and delegated authority must be validated.';

  return 'Included by the backend packet as an impacted CRM surface.';
}


/* WILSY_P60K4H_COLLISION_AWARE_REVEAL_ALGORITHM */

const WILSY_REVEAL_PANEL_PLACEMENT_VIEWPORT_TOP_CENTER = 'VIEWPORT_TOP_CENTER';


/**
 * @function clampWilsyRevealPanelCoordinate
 * @description Clamps a reveal panel coordinate so the intelligence panel stays inside the viewport.
 * @param {number} value - Proposed coordinate.
 * @param {number} min - Minimum coordinate.
 * @param {number} max - Maximum coordinate.
 * @returns {number} Clamped coordinate.
 * @collaboration Wilsy reveal node dock, viewport collision detection, game-like HUD panels, and operator-safe packet controls.
 */
function clampWilsyRevealPanelCoordinate(value, min, max) {
  return Math.min(Math.max(value, min), max);
}

/**
 * @function resolveWilsyRevealPanelGeometry
 * @description Computes top-middle viewport reveal panel geometry for Wilsy OS reveal nodes.
 * @param {HTMLElement} node - Reveal node element.
 * @returns {Object} Reveal geometry.
 * @collaboration Wilsy reveal node dock, viewport-top-center placement parameter, collision-safe overlays, game-like HUD panels, and reusable Wilsy OS card intelligence algorithm.
 */
function resolveWilsyRevealPanelGeometry(node) {
  if (typeof window === 'undefined') {
    return {
      left: 24,
      top: 84,
      placement: WILSY_REVEAL_PANEL_PLACEMENT_VIEWPORT_TOP_CENTER,
      width: 420,
      height: 340,
    };
  }

  const margin = 18;
  const viewportWidth = window.innerWidth || 1440;
  const viewportHeight = window.innerHeight || 900;
  const panelWidth = Math.min(520, Math.max(320, viewportWidth - margin * 2));
  const panelHeight = Math.min(380, Math.max(280, viewportHeight - margin * 2));
  const preferredTop = Math.min(96, Math.max(68, viewportHeight * 0.09));
  const left = clampWilsyRevealPanelCoordinate(
    viewportWidth / 2 - panelWidth / 2,
    margin,
    viewportWidth - panelWidth - margin
  );
  const top = clampWilsyRevealPanelCoordinate(
    preferredTop,
    margin,
    viewportHeight - panelHeight - margin
  );

  return {
    left,
    top,
    placement: WILSY_REVEAL_PANEL_PLACEMENT_VIEWPORT_TOP_CENTER,
    width: panelWidth,
    height: panelHeight,
  };
}


/* WILSY_P60K4J_PORTAL_REVEAL_INTELLIGENCE_LAYER */

/**
 * @function WilsyRevealViewportPanel
 * @description Renders a Wilsy OS reveal-node intelligence panel as a viewport-level top-center overlay instead of a child tooltip.
 * @param {Object} props - Panel props.
 * @param {Object} props.node - Active reveal node.
 * @param {string} props.copyFeedback - Copy status feedback.
 * @param {Function} props.onClose - Close handler.
 * @returns {React.ReactNode|null} Portal-rendered reveal panel.
 * @collaboration Wilsy reveal-node algorithm, viewport top-center placement, compact HUD triggers, copy actions, and mandatory WILSY OS signature.
 */
function WilsyRevealViewportPanel({ node, copyFeedback = '', onClose }) {
  if (!node || typeof document === 'undefined') {
    return null;
  }

  return createPortal(
    <div className={styles.packetRevealViewportLayer} role="presentation">
      <section
        className={styles.packetRevealViewportPanel}
        role="dialog"
        aria-modal="false"
        aria-label={`${node.label} intelligence`}
      >
        <header className={styles.packetRevealViewportHeader}>
          <span>WILSY OS Intelligence</span>
          <strong>{node.label} · {node.status}</strong>

          <button type="button" onClick={onClose} aria-label="Close reveal intelligence panel">
            Close
          </button>
        </header>

        <div className={styles.packetRevealViewportBody}>
          {node.sections.map((section) => (
            <article key={`${node.id}-${section.title}`}>
              <span>{section.title}</span>
              <p>{section.body}</p>
            </article>
          ))}

          {node.previewItems?.length ? (
            <div className={styles.packetRevealPreviewGrid}>
              {node.previewItems.map((item) => (
                <article key={`${node.id}-${item.label}`}>
                  <span>{item.label}</span>
                  <strong>{item.value}</strong>
                </article>
              ))}
            </div>
          ) : null}

          {node.actions?.length ? (
            <div className={styles.packetRevealViewportActions}>
              {node.actions.map((action) => (
                <button key={`${node.id}-${action.label}`} type="button" onClick={action.onClick}>
                  {action.label}
                </button>
              ))}
            </div>
          ) : null}

          {copyFeedback ? <small className={styles.packetRevealViewportFeedback}>{copyFeedback}</small> : null}
        </div>

        <footer className={styles.packetRevealViewportSignature}>
          {node.signature || 'WILSY OS · REVEAL NODE'}
        </footer>
      </section>
    </div>,
    document.body
  );
}


/* WILSY_P60K4T_EVIDENCE_INTELLIGENCE_RAIL */

/**
 * @function resolveWilsySetupReviewEvidenceShortLabel
 * @description Converts a setup evidence requirement into a compact Wilsy OS evidence node label.
 * @param {string} evidence - Evidence requirement text.
 * @returns {string} Compact evidence label.
 * @collaboration Evidence intelligence rail, Wilsy reveal node algorithm, Packet Console, and backend setup packet requirements.
 */
function resolveWilsySetupReviewEvidenceShortLabel(evidence = '') {
  const value = String(evidence).toLowerCase();

  if (value.includes('tenant')) return 'Tenant';
  if (value.includes('operator')) return 'Operator';
  if (value.includes('owner')) return 'Owner';
  if (value.includes('risk')) return 'Risk';
  if (value.includes('approval')) return 'Approval';
  if (value.includes('release')) return 'Release';

  return 'Evidence';
}

/**
 * @function resolveWilsySetupReviewEvidenceGateImpact
 * @description Resolves which gate or operating surface an evidence requirement protects.
 * @param {string} evidence - Evidence requirement text.
 * @returns {string} Gate impact.
 * @collaboration Evidence node intelligence, approval gate, release gate, audit posture, and backend packet requirements.
 */
function resolveWilsySetupReviewEvidenceGateImpact(evidence = '') {
  const value = String(evidence).toLowerCase();

  if (value.includes('tenant')) return 'Tenant authority gate';
  if (value.includes('operator')) return 'Operator accountability gate';
  if (value.includes('owner')) return 'Control ownership gate';
  if (value.includes('risk')) return 'Risk review gate';
  if (value.includes('approval')) return 'Approval gate';
  if (value.includes('release')) return 'Release gate';

  return 'Setup review gate';
}

/**
 * @function resolveWilsySetupReviewEvidenceNextStep
 * @description Resolves a productive next step for a setup evidence node.
 * @param {string} evidence - Evidence requirement text.
 * @returns {string} Next operating step.
 * @collaboration Evidence productivity rail, setup review workflow, proof receipts, and Wilsy OS operator guidance.
 */
function resolveWilsySetupReviewEvidenceNextStep(evidence = '') {
  const value = String(evidence).toLowerCase();

  if (value.includes('tenant')) return 'Confirm the packet tenant matches the active workspace before approval.';
  if (value.includes('operator')) return 'Keep the operator identity attached to the receipt chain.';
  if (value.includes('owner')) return 'Assign or confirm the owner accountable for this control.';
  if (value.includes('risk')) return 'Review the impact summary before moving to approval.';
  if (value.includes('approval')) return 'Attach authorized approver identity before approval actions unlock.';
  if (value.includes('release')) return 'Convert this requirement into receipt-backed release evidence.';

  return 'Inspect the requirement and attach evidence before release.';
}

/**
 * @function createWilsySetupReviewEvidenceRevealNode
 * @description Creates a viewport intelligence panel node for one backend setup evidence requirement.
 * @param {Object} item - Evidence item.
 * @param {Function} copyHandler - Copy handler.
 * @returns {Object} Reveal node payload.
 * @collaboration Wilsy OS reveal-node algorithm, top-center intelligence panel, evidence rail, and backend packet productivity.
 */
function createWilsySetupReviewEvidenceRevealNode(item = {}, copyHandler = () => {}) {
  return {
    id: item.id,
    label: item.shortLabel,
    status: item.status,
    signature: 'WILSY OS · EVIDENCE NODE',
    sections: [
      {
        title: 'Evidence purpose',
        body: item.purpose,
      },
      {
        title: 'Backend productivity',
        body: `This requirement is part of the live setup packet. It protects the ${item.gateImpact} and keeps approval or release from becoming a blind action.`,
      },
      {
        title: 'Next operating step',
        body: item.nextStep,
      },
    ],
    previewItems: [
      {
        label: 'Requirement',
        value: item.fullLabel,
      },
      {
        label: 'Source',
        value: item.source,
      },
      {
        label: 'Gate impact',
        value: item.gateImpact,
      },
    ],
    actions: [
      {
        label: 'Copy requirement',
        onClick: () => copyHandler('Evidence requirement', item.fullLabel),
      },
    ],
  };
}


/* WILSY_P60K4V_SCOPED_LEFT_AUTHORITY_GATE_RAILS */

/**
 * @function createWilsySetupAuthorityRailRevealNode
 * @description Creates a Wilsy OS viewport intelligence node for authority facts and gate controls.
 * @param {Object} item - Authority or gate rail item.
 * @param {Function} copyHandler - Copy handler.
 * @returns {Object} Viewport reveal node payload.
 * @collaboration Packet Console, authority rail, gate rail, backend packet evidence, WILSY OS reveal-node algorithm, and operator productivity.
 */
function createWilsySetupAuthorityRailRevealNode(item = {}, copyHandler = () => {}) {
  return {
    id: item.id,
    label: item.label,
    status: item.status,
    signature: item.signature,
    sections: [
      {
        title: 'Business state',
        body: item.businessState,
      },
      {
        title: 'Why this matters',
        body: item.whyItMatters,
      },
      {
        title: 'Next operating step',
        body: item.nextStep,
      },
    ],
    previewItems: [
      {
        label: 'Source',
        value: item.source,
      },
      {
        label: 'Operating impact',
        value: item.impact,
      },
    ],
    actions: item.copyValue
      ? [
          {
            label: item.copyLabel,
            onClick: () => copyHandler(item.copyLabel, item.copyValue),
          },
        ]
      : [],
  };
}


/* WILSY_P60K4W_SYSTEM_IMPACT_RAIL */

/**
 * @function resolveWilsySetupSurfaceGateImpact
 * @description Resolves the operating impact of a setup surface affected by a backend packet.
 * @param {string} surface - Affected setup surface.
 * @returns {string} Operating impact.
 * @collaboration System impact rail, backend packet surfaces, authority controls, and Wilsy OS reveal-node intelligence.
 */
function resolveWilsySetupSurfaceGateImpact(surface = '') {
  const value = String(surface).toLowerCase();

  if (value.includes('user')) return 'Access control';
  if (value.includes('profile')) return 'Permission inheritance';
  if (value.includes('role')) return 'Role chain review';
  if (value.includes('field')) return 'Sensitive field exposure';
  if (value.includes('export')) return 'Data movement risk';
  if (value.includes('approval')) return 'Approval authority';

  return 'Setup impact';
}

/**
 * @function resolveWilsySetupSurfaceNextStep
 * @description Resolves the next productive action for an affected setup surface.
 * @param {string} surface - Affected setup surface.
 * @returns {string} Next operating step.
 * @collaboration System impact rail, setup productivity, backend packet evidence, and release readiness.
 */
function resolveWilsySetupSurfaceNextStep(surface = '') {
  const value = String(surface).toLowerCase();

  if (value.includes('user')) return 'Confirm which users could gain, lose, or inherit access.';
  if (value.includes('profile')) return 'Review profile permissions before approval.';
  if (value.includes('role')) return 'Check role chains and inherited authority before release.';
  if (value.includes('field')) return 'Validate sensitive CRM field exposure before approval.';
  if (value.includes('export')) return 'Confirm export rights and compliance risk before release.';
  if (value.includes('approval')) return 'Validate approval owners and delegated authority.';

  return 'Inspect this surface before approval or release.';
}

/**
 * @function createWilsySetupSurfaceRevealNode
 * @description Creates a top-center Wilsy OS intelligence node for an affected setup surface.
 * @param {Object} item - Surface rail item.
 * @param {Function} copyHandler - Copy handler.
 * @returns {Object} Viewport reveal node payload.
 * @collaboration System impact rail, Wilsy reveal-node algorithm, backend surfaces, copy workflow, and operator productivity.
 */
function createWilsySetupSurfaceRevealNode(item = {}, copyHandler = () => {}) {
  return {
    id: item.id,
    label: item.label,
    status: item.status,
    signature: 'WILSY OS · SYSTEM IMPACT NODE',
    sections: [
      {
        title: 'Business state',
        body: item.businessState,
      },
      {
        title: 'Why this matters',
        body: item.whyItMatters,
      },
      {
        title: 'Next operating step',
        body: item.nextStep,
      },
    ],
    previewItems: [
      {
        label: 'Source',
        value: item.source,
      },
      {
        label: 'Impact',
        value: item.impact,
      },
    ],
    actions: [
      {
        label: 'Copy system impact',
        onClick: () => copyHandler('System impact', `${item.label}: ${item.impact} — ${item.nextStep}`),
      },
    ],
  };
}


/* WILSY_P60K5C2_SETUP_WORKFLOW_FRONTEND */

/**
 * @function createWilsySetupWorkflowActionRevealNode
 * @description Creates a top-center Wilsy OS intelligence node for a live setup workflow command.
 * @param {Object} action - Workflow action configuration.
 * @param {Object} workflowState - Current backend workflow state.
 * @param {Object} packet - Current staged setup review packet.
 * @returns {Object} Viewport reveal node payload.
 * @collaboration Packet Console workflow rail, backend evidence ledger, approval gate, release gate, receipts, and Wilsy OS reveal-node intelligence.
 */
function createWilsySetupWorkflowActionRevealNode(action = {}, workflowState = {}, packet = {}) {
  const evidenceCount = Number(workflowState.evidenceCount || packet.evidenceLedger?.length || 0);
  const approved = Boolean(workflowState.approved || packet.approvalState?.status === 'APPROVED');
  const released = Boolean(workflowState.released || packet.releaseState?.status === 'RELEASED');

  return {
    id: `workflow-${action.id || action.label || 'command'}`,
    label: action.label || 'Workflow command',
    status: action.status || 'Ready',
    signature: 'WILSY OS · WORKFLOW COMMAND NODE',
    sections: [
      {
        title: 'Command purpose',
        body: action.description || 'Executes a backend-owned setup review workflow command.',
      },
      {
        title: 'Production contract',
        body: action.contract || 'This command must return a receipt, update workflow state, and preserve audit evidence.',
      },
      {
        title: 'Next operating step',
        body: action.nextStep || 'Run the command when gate requirements are satisfied.',
      },
    ],
    previewItems: [
      {
        label: 'Evidence',
        value: `${evidenceCount} attached`,
      },
      {
        label: 'Approval',
        value: approved ? 'Approved' : 'Waiting',
      },
      {
        label: 'Release',
        value: released ? 'Released' : 'Waiting',
      },
    ],
    actions: [],
  };
}

/**
 * @function WilsyCrmSetupControlPlane
 * @description Renders the CRM Setup Control Plane as a production workbench with rails, dropdown command menus, a clear view area, and compact review workflow.
 * @returns {JSX.Element} CRM setup workbench.
 * @collaboration CRMDashboard setup owner, CRM top rail, setup domain rail, operating view area, authority rail, and review queue.
 */
export default function WilsyCrmSetupControlPlane() {
  const domains = useMemo(() => buildSetupDomains(), []);
  const evidencePack = useMemo(() => buildEvidencePack(), []);
  const [activeDomainId, setActiveDomainId] = useState('authority');
  const [activeControlId, setActiveControlId] = useState('authority-graph');
  const [lens, setLens] = useState('Authority');
  const [filterText, setFilterText] = useState('');
  const [reviewQueue, setReviewQueue] = useState([]);
  const [reviewResult, setReviewResult] = useState(null);
  const [packetConsoleOpen, setPacketConsoleOpen] = useState(false);
  const [viewAreaConsoleOpen, setViewAreaConsoleOpen] = useState(false);
  const [domainRailOpen, setDomainRailOpen] = useState(true);
  const [authorityRailOpen, setAuthorityRailOpen] = useState(true);
  const [reviewCommandBusy, setReviewCommandBusy] = useState('');
  const [reviewCommandError, setReviewCommandError] = useState(null);
  const [setupWorkflowCommandBusy, setSetupWorkflowCommandBusy] = useState('');
  const [setupWorkflowCommandFeedback, setSetupWorkflowCommandFeedback] = useState('');
  const wilsyRevealHoverDelayMs = 620;
  const wilsyRevealHoverTimerRef = useRef(null);
  const [copyFeedback, setCopyFeedback] = useState('');
  const [activeRevealNode, setActiveRevealNode] = useState(null);

  const activeDomain = domains.find((domain) => domain.id === activeDomainId) || domains[0];
  const activeControl = activeDomain.controls.find((control) => control.id === activeControlId) || activeDomain.controls[0];

  const filteredControls = activeDomain.controls.filter((control) => {
    const query = filterText.trim().toLowerCase();

    if (!query) {
      return true;
    }

    return [
      control.name,
      control.owner,
      control.risk,
      control.state,
      control.engine,
      control.benefit,
      control.signal,
    ].some((value) => String(value || '').toLowerCase().includes(query));
  });

  const posture = useMemo(() => calculatePosture(domains, reviewQueue.length), [domains, reviewQueue.length]);
  const stagedReview = reviewQueue.find((ticket) => ticket.controlId === activeControl.id);
  useEffect(() => {
    let cancelled = false;
    const route = '/api/crm/command/setup/reviews/list';
    const payload = buildWilsySetupReviewLivePayload({
      route,
      ticket: {
        id: 'SETUP_REVIEW_QUEUE_BOOTSTRAP',
        packetId: 'SETUP_REVIEW_QUEUE_BOOTSTRAP',
        controlId: 'setup-review-queue',
        title: 'Setup review queue',
        risk: 'LOW',
        state: 'READY',
      },
      domain: { id: 'setup', title: 'Setup Review Queue' },
      control: { id: 'setup-review-queue', name: 'Setup review queue' },
      lens: 'Queue',
    });

    requestWilsySetupReviewLiveCommand(route, payload)
      .then((data) => {
        if (cancelled) return;

        const packets = Array.isArray(data?.packets)
          ? data.packets.map((packet) => normalizeWilsySetupReviewLivePacket(packet, {}))
          : [];

        setReviewQueue(packets);
      })
      .catch((error) => {
        if (!cancelled) setReviewCommandError(error?.message || 'Setup review queue could not be loaded.');
      });

    return () => {
      cancelled = true;
    };
  }, []);

  /* WILSY_P60K5D_REVEAL_SCROLL_CANCEL */
  useEffect(() => {
    /**
     * @function cancelRevealHover
     * @description Cancels pending reveal-node hover timers while the operator scrolls, wheels, or touch-moves through the CRM setup board.
     * @returns {void}
     * @collaboration Packet Console reveal-node delay, scroll safety, workflow command rail, and production operator UX.
     */
    const cancelRevealHover = () => {
      if (wilsyRevealHoverTimerRef.current) {
        globalThis.clearTimeout(wilsyRevealHoverTimerRef.current);
        wilsyRevealHoverTimerRef.current = null;
      }
    };

    globalThis.addEventListener?.('scroll', cancelRevealHover, true);
    globalThis.addEventListener?.('wheel', cancelRevealHover, true);
    globalThis.addEventListener?.('touchmove', cancelRevealHover, true);

    return () => {
      cancelRevealHover();
      globalThis.removeEventListener?.('scroll', cancelRevealHover, true);
      globalThis.removeEventListener?.('wheel', cancelRevealHover, true);
      globalThis.removeEventListener?.('touchmove', cancelRevealHover, true);
    };
  }, []);

  const activeControlIndex = activeDomain.controls.findIndex((control) => control.id === activeControl.id);
  const isFirstControl = activeControlIndex <= 0;
  const isLastControl = activeControlIndex >= activeDomain.controls.length - 1;
  const resultText = reviewResult ? `${reviewResult.status}: ${reviewResult.title}` : 'No review staged yet.';
  const packetProofReceiptId = stagedReview ? resolveWilsySetupReviewProofReceiptId(stagedReview) : '';
  const packetProofHash = stagedReview ? resolveWilsySetupReviewProofHash(stagedReview) : '';
  const packetAuditBusinessStatus = stagedReview ? resolveWilsySetupReviewAuditBusinessStatus(stagedReview) : '';
  const packetBusinessStatus = stagedReview?.backendLive ? 'Backend packet staged' : 'Current session packet';
  const packetTechnicalReference = stagedReview?.packetId || stagedReview?.id || '';
  const packetBusinessReference = `${stagedReview?.title || stagedReview?.controlName || 'Setup review'} · ${packetAuditBusinessStatus || 'Audit pending'}`;
  const packetProofReceiptPreview = packetProofReceiptId && !packetProofReceiptId.toLowerCase().includes('pending')
    ? `Receipt ending ${packetProofReceiptId.slice(-8)}`
    : packetProofReceiptId;
  const packetProofHashPreview = packetProofHash && !packetProofHash.toLowerCase().includes('pending')
    ? `Hash ending ${packetProofHash.slice(-8)}`
    : packetProofHash;
  const packetProofBusinessLabel = packetProofReceiptId && !packetProofReceiptId.toLowerCase().includes('pending')
    ? 'Receipt issued'
    : 'Receipt pending';
  const packetHashBusinessLabel = packetProofHash && !packetProofHash.toLowerCase().includes('pending')
    ? 'Hash verified'
    : 'Hash pending';

  const packetEvidenceSource = stagedReview?.backendLive ? 'Backend packet' : 'Current session';
  const packetEvidenceItems = (stagedReview?.requiredEvidence?.length
    ? stagedReview.requiredEvidence
    : [
        'Tenant authority confirmed',
        'Operator identity attached',
        'Control owner assigned',
        'Risk and impact summary prepared',
        'Approval gate waiting for authorized approver',
        'Release gate waiting for evidence receipt',
      ]).map((evidence, index) => ({
    id: `evidence-${index}-${resolveWilsySetupReviewEvidenceShortLabel(evidence).toLowerCase()}`,
    shortLabel: resolveWilsySetupReviewEvidenceShortLabel(evidence),
    fullLabel: evidence,
    status: 'Required',
    source: packetEvidenceSource,
    purpose: resolveWilsySetupReviewEvidencePurpose(evidence),
    gateImpact: resolveWilsySetupReviewEvidenceGateImpact(evidence),
    nextStep: resolveWilsySetupReviewEvidenceNextStep(evidence),
  }));
  const packetEvidenceSummary = `${packetEvidenceItems.length} live packet requirements`;
  const packetEvidenceChecklist = packetEvidenceItems
    .map((item, index) => `${index + 1}. ${item.fullLabel} — ${item.gateImpact} — ${item.nextStep}`)
    .join('\n');

  const authorityRailSource = stagedReview?.backendLive ? 'Backend packet' : 'Current session';
  const authorityOwnerLabel = stagedReview?.owner || activeControl?.owner || 'Owner pending';
  const authorityRiskLabel = stagedReview?.risk || activeControl?.risk || 'Risk pending';
  const authorityStateLabel = stagedReview?.state || activeControl?.state || 'State pending';
  const authorityRailItems = [
    {
      id: 'authority-packet',
      label: 'Packet',
      status: stagedReview?.backendLive ? 'Live' : 'Session',
      source: authorityRailSource,
      impact: 'Audit and packet traceability',
      businessState: 'This setup review is staged as an operating packet. The business sees a clean status while the technical reference remains hidden behind copy.',
      whyItMatters: 'Packet evidence prevents setup work from becoming an invisible UI action. It gives operators, support, audit, and leadership a traceable control record.',
      nextStep: 'Keep this packet staged while evidence is prepared. Withdraw the stage if the review should stop while preserving receipt evidence.',
      copyLabel: 'Copy packet reference',
      copyValue: packetTechnicalReference,
      signature: 'WILSY OS · PACKET NODE',
    },
    {
      id: 'authority-owner',
      label: 'Owner',
      status: authorityOwnerLabel,
      source: authorityRailSource,
      impact: 'Control accountability',
      businessState: `${authorityOwnerLabel} is accountable for this authority control while the packet is staged.`,
      whyItMatters: 'Ownership prevents sensitive setup work from floating without accountable responsibility.',
      nextStep: 'Confirm the owner before approval actions unlock.',
      copyLabel: 'Copy owner',
      copyValue: authorityOwnerLabel,
      signature: 'WILSY OS · OWNER NODE',
    },
    {
      id: 'authority-risk',
      label: 'Risk',
      status: authorityRiskLabel,
      source: authorityRailSource,
      impact: 'Approval priority',
      businessState: `This packet carries ${authorityRiskLabel} risk posture.`,
      whyItMatters: 'Risk level determines how carefully authority, field access, export rights, and approval changes must be reviewed.',
      nextStep: 'Review impact before approval or release.',
      copyLabel: 'Copy risk posture',
      copyValue: authorityRiskLabel,
      signature: 'WILSY OS · RISK NODE',
    },
    {
      id: 'authority-state',
      label: 'State',
      status: authorityStateLabel,
      source: authorityRailSource,
      impact: 'Production readiness',
      businessState: `This control is currently ${authorityStateLabel}.`,
      whyItMatters: 'State tells the operator whether the control is open, sealed, staged, or blocked before release.',
      nextStep: 'Keep sealed controls under review until evidence and approval are ready.',
      copyLabel: 'Copy state',
      copyValue: authorityStateLabel,
      signature: 'WILSY OS · STATE NODE',
    },
  ];
  const setupWorkflowEvidenceLedger = Array.isArray(stagedReview?.evidenceLedger)
    ? stagedReview.evidenceLedger
    : [];
  const setupWorkflowApprovalState = stagedReview?.approvalState || {};
  const setupWorkflowReleaseState = stagedReview?.releaseState || {};
  const setupWorkflowState = stagedReview?.workflowState || {};
  const setupWorkflowEvidenceCount = setupWorkflowEvidenceLedger.filter((item) => item?.status !== 'REMOVED').length;
  const setupWorkflowApproved = setupWorkflowApprovalState.status === 'APPROVED' || setupWorkflowState.approved === true;
  const setupWorkflowReleaseReady = setupWorkflowApproved || setupWorkflowReleaseState.status === 'READY' || setupWorkflowState.releaseReady === true;
  const setupWorkflowReleased = setupWorkflowReleaseState.status === 'RELEASED';
  const setupWorkflowLastReceipt = Array.isArray(stagedReview?.receipts) && stagedReview.receipts.length
    ? stagedReview.receipts[stagedReview.receipts.length - 1]
    : null;
  const setupWorkflowGateLabel = setupWorkflowReleased
    ? 'Released'
    : setupWorkflowApproved
      ? 'Release ready'
      : setupWorkflowEvidenceCount > 0
        ? 'Approval ready'
        : 'Evidence required';
  const setupWorkflowTimeline = [
    {
      id: 'evidence-ledger',
      label: 'Evidence',
      value: `${setupWorkflowEvidenceCount} attached`,
      status: setupWorkflowEvidenceCount > 0 ? 'Ready' : 'Waiting',
    },
    {
      id: 'approval-state',
      label: 'Approval',
      value: setupWorkflowApproved ? 'Approved' : setupWorkflowApprovalState.status || 'Locked',
      status: setupWorkflowApproved ? 'Approved' : setupWorkflowEvidenceCount > 0 ? 'Ready' : 'Locked',
    },
    {
      id: 'release-state',
      label: 'Release',
      value: setupWorkflowReleased ? 'Released' : setupWorkflowReleaseState.status || 'Locked',
      status: setupWorkflowReleased ? 'Released' : setupWorkflowReleaseReady ? 'Ready' : 'Locked',
    },
  ];
  const setupWorkflowActions = [
    {
      id: 'attach-evidence',
      label: 'Attach evidence',
      route: '/api/crm/command/setup/reviews/evidence',
      status: setupWorkflowEvidenceCount > 0 ? `${setupWorkflowEvidenceCount} attached` : 'Ready',
      description: 'Attach receipt-backed evidence to this setup packet.',
      contract: 'POST /setup/reviews/evidence updates evidenceLedger, approvalState, workflowState, receipts, and auditTrail.',
      nextStep: 'Attach evidence so approval can become available.',
      disabled: !stagedReview?.packetId || setupWorkflowReleased,
      disabledReason: setupWorkflowReleased ? 'Packet already released' : 'Stage packet first',
    },
    {
      id: 'approve',
      label: 'Approve',
      route: '/api/crm/command/setup/reviews/approve',
      status: setupWorkflowApproved ? 'Approved' : setupWorkflowEvidenceCount > 0 ? 'Ready' : 'Locked',
      description: 'Approve this setup review packet after evidence is attached.',
      contract: 'POST /setup/reviews/approve requires evidence and updates approvalState, releaseState, workflowState, receipts, and auditTrail.',
      nextStep: setupWorkflowEvidenceCount > 0 ? 'Approve the packet so release can become available.' : 'Attach evidence before approval.',
      disabled: !stagedReview?.packetId || setupWorkflowEvidenceCount < 1 || setupWorkflowApproved || setupWorkflowReleased,
      disabledReason: setupWorkflowApproved
        ? 'Already approved'
        : setupWorkflowReleased
          ? 'Packet already released'
          : setupWorkflowEvidenceCount < 1
            ? 'Evidence required'
            : 'Stage packet first',
    },
    {
      id: 'release',
      label: 'Release',
      route: '/api/crm/command/setup/reviews/release',
      status: setupWorkflowReleased ? 'Released' : setupWorkflowReleaseReady ? 'Ready' : 'Locked',
      description: 'Release this approved setup review packet.',
      contract: 'POST /setup/reviews/release requires approval and evidence, then updates releaseState, workflowState, receipts, and auditTrail.',
      nextStep: setupWorkflowReleaseReady ? 'Release the packet with approval and evidence receipts.' : 'Approve before release.',
      disabled: !stagedReview?.packetId || !setupWorkflowReleaseReady || setupWorkflowReleased,
      disabledReason: setupWorkflowReleased
        ? 'Already released'
        : !setupWorkflowReleaseReady
          ? 'Approval required'
          : 'Stage packet first',
    },
  ];
  const setupWorkflowReceiptLabel = setupWorkflowLastReceipt?.receiptId || 'No workflow receipt yet';

  /* WILSY_P60K5C2_DYNAMIC_GATE_RAIL */
  const gateRailItems = [
    {
      id: 'approval-gate',
      label: setupWorkflowApproved ? 'Approval complete' : setupWorkflowEvidenceCount > 0 ? 'Approval ready' : 'Approval locked',
      status: setupWorkflowApprovalState.status || (setupWorkflowEvidenceCount > 0 ? 'READY' : 'LOCKED'),
      source: 'Backend workflow',
      impact: 'Approval gate',
      businessState: setupWorkflowApproved
        ? `Approved by ${setupWorkflowApprovalState.approver || 'authorized operator'}.`
        : setupWorkflowEvidenceCount > 0
          ? 'Evidence exists. Approval command is available.'
          : 'Approval remains locked until receipt-backed evidence exists.',
      whyItMatters: 'Approval cannot be simulated. It must be stored as backend receipt evidence before release.',
      nextStep: setupWorkflowApproved ? 'Release gate can now be executed.' : 'Attach evidence, then approve.',
    },
    {
      id: 'release-gate',
      label: setupWorkflowReleased ? 'Release complete' : setupWorkflowReleaseReady ? 'Release ready' : 'Release locked',
      status: setupWorkflowReleaseState.status || (setupWorkflowReleaseReady ? 'READY' : 'LOCKED'),
      source: 'Backend workflow',
      impact: 'Release gate',
      businessState: setupWorkflowReleased
        ? `Released with receipt ${setupWorkflowReleaseState.receiptId || setupWorkflowReceiptLabel}.`
        : setupWorkflowReleaseReady
          ? 'Approval is complete. Release command is available.'
          : 'Release remains locked until approval and evidence are complete.',
      whyItMatters: 'Release closes the setup packet and records the final receipt-backed audit event.',
      nextStep: setupWorkflowReleased ? 'Packet is released. Preserve receipts and audit trail.' : 'Approve the packet, then release.',
    },
  ];
  const authorityRailChecklist = authorityRailItems
    .map((item, index) => `${index + 1}. ${item.label}: ${item.status} — ${item.impact}`)
    .join('\n');
  const gateRailChecklist = gateRailItems
    .map((item, index) => `${index + 1}. ${item.label}: ${item.status} — ${item.nextStep}`)
    .join('\n');

  const surfaceRailSource = stagedReview?.backendLive ? 'Backend packet' : 'Current setup control';
  const surfaceRailItems = (stagedReview?.surfaces?.length ? stagedReview.surfaces : (activeControl?.surfaces || []))
    .filter(Boolean)
    .map((surface, index) => ({
      id: `surface-${index}-${String(surface).toLowerCase().replace(/[^a-z0-9]+/g, '-')}`,
      label: surface,
      status: stagedReview?.backendLive ? 'Live' : 'Mapped',
      source: surfaceRailSource,
      impact: resolveWilsySetupSurfaceGateImpact(surface),
      businessState: `${surface} is affected by this authority packet.`,
      whyItMatters: resolveWilsySetupReviewSurfacePurpose(surface),
      nextStep: resolveWilsySetupSurfaceNextStep(surface),
    }));
  const surfaceRailSummary = `${surfaceRailItems.length} affected systems`;
  const surfaceRailMap = surfaceRailItems
    .map((item, index) => `${index + 1}. ${item.label}: ${item.impact} — ${item.nextStep}`)
    .join('\n');

  const packetRevealNodes = [
    {
      id: 'packet',
      label: 'Packet',
      status: 'Staged',
      className: styles.packetRevealNodeLive,
      signature: 'WILSY OS · LIVE PACKET NODE',
      sections: [
        {
          title: 'Business state',
          body: 'The Authority Graph review has been staged and saved through the CRM setup backend. This is now a governed packet, not a local preview.',
        },
        {
          title: 'Why this matters',
          body: 'Authority Graph controls can affect user access, role inheritance, profile exposure, field visibility, export rights, approval chains, and delegation power.',
        },
        {
          title: 'Next operating step',
          body: 'Keep the packet staged while evidence and approver identity are prepared. The packet can be removed if the review should not continue.',
        },
      ],
      previewItems: [
        {
          label: 'Business reference',
          value: packetBusinessReference,
        },
      ],
      actions: [
        {
          label: 'Copy technical reference',
          onClick: () => handleCopyPacketProof('Technical packet reference', packetTechnicalReference),
        },
      ],
    },
    {
      id: 'proof',
      label: 'Proof',
      status: 'Issued',
      className: styles.packetRevealNodeProof,
      signature: 'WILSY OS · PROOF NODE',
      sections: [
        {
          title: 'Business state',
          body: 'The backend has issued proof for this setup review packet. The operator does not need to read technical identifiers unless evidence is being copied.',
        },
        {
          title: 'How to use it',
          body: 'Use the receipt for audit, board review, support escalation, or internal verification. Use the hash when you need tamper-proof proof that the receipt has not been casually rewritten.',
        },
      ],
      previewItems: [
        {
          label: 'Receipt preview',
          value: packetProofReceiptPreview,
        },
        {
          label: 'Hash preview',
          value: packetProofHashPreview,
        },
      ],
      actions: [
        {
          label: 'Copy receipt',
          onClick: () => handleCopyPacketProof('Proof receipt', packetProofReceiptId),
        },
        {
          label: 'Copy hash',
          onClick: () => handleCopyPacketProof('Tamper-proof hash', packetProofHash),
        },
      ],
    },
    {
      id: 'approval',
      label: 'Approval',
      status: 'Locked',
      className: styles.packetRevealNodeLocked,
      signature: 'WILSY OS · APPROVAL NODE',
      sections: [
        {
          title: 'Business state',
          body: 'Approval is intentionally locked. The system is preventing this authority control from moving forward without accountable approval.',
        },
        {
          title: 'Why this matters',
          body: 'This protects the business from silent changes to users, roles, profiles, fields, exports, approvals, and delegated authority.',
        },
        {
          title: 'Next operating step',
          body: 'Attach approver identity, approval scope, and evidence before approval actions become available.',
        },
      ],
    },
    {
      id: 'release',
      label: 'Release',
      status: 'Locked',
      className: styles.packetRevealNodeLocked,
      signature: 'WILSY OS · RELEASE NODE',
      sections: [
        {
          title: 'Business state',
          body: 'Release is blocked until receipt-backed evidence exists. This protects production from unproven setup changes.',
        },
        {
          title: 'Why this matters',
          body: 'Release controls turn review evidence into operational safety. Nothing should reach production unless the packet has proof, ownership, and release evidence.',
        },
        {
          title: 'Next operating step',
          body: 'Convert required evidence into verified records, then enable release review.',
        },
      ],
    },
  ];


  /**
   * @function handleDomainChange
   * @description Changes the selected setup domain and resets the active control to the first control in that domain.
   * @param {string} domainId - Selected domain id.
   * @returns {void}
   * @collaboration Domain rail, command rail, view area, and authority rail.
   */
  function handleDomainChange(domainId) {
    const nextDomain = domains.find((domain) => domain.id === domainId) || domains[0];

    setActiveDomainId(nextDomain.id);
    setActiveControlId(nextDomain.controls[0]?.id || '');
  }

  /**
   * @function handleStageReview
   * @description Stages or refreshes the active setup control in the local review queue.
   * @returns {void}
   * @collaboration Review queue, right authority rail, view area command rail, and action result rail.
   */
  async function handleStageReview() {
    const localTicket = createReviewTicket(activeDomain, activeControl);
    const route = '/api/crm/command/setup/reviews';
    const payload = buildWilsySetupReviewLivePayload({
      route,
      ticket: localTicket,
      domain: activeDomain,
      control: activeControl,
      lens,
    });

    setReviewCommandBusy('stage');
    setReviewCommandError(null);

    try {
      const data = await requestWilsySetupReviewLiveCommand(route, payload);
      const backendTicket = normalizeWilsySetupReviewLivePacket(data.packet, {
        ...localTicket,
        receipt: data.receipt || null,
        auditEvidence: data.auditEvidence || null,
      });

      setReviewQueue((current) => [
        backendTicket,
        ...current.filter((item) => item.controlId !== backendTicket.controlId && item.packetId !== backendTicket.packetId),
      ]);
      setPacketConsoleOpen(false);
      setReviewResult({
        ...backendTicket,
        status: data.result || 'Backend packet staged',
        generatedAt: data.receipt?.generatedAt || data.auditEvidence?.generatedAt || new Date().toISOString(),
      });
    } catch (error) {
      const message = error?.message || 'Setup review stage failed.';
      setReviewCommandError(message);
      setReviewResult({
        ...localTicket,
        status: 'Backend stage failed',
        generatedAt: new Date().toISOString(),
        error: message,
      });
    } finally {
      setReviewCommandBusy('');
    }
  }

  /**
   * @function handleRemoveReview
   * @description Removes a staged review item from the local queue.
   * @param {string} controlId - Control id to remove.
   * @returns {void}
   * @collaboration Review ledger, authority rail, command rail, and queue state.
   */
  async function handleRemoveReview(packetOrControlId = '') {
    const candidate = typeof packetOrControlId === 'object'
      ? packetOrControlId
      : reviewQueue.find((item) => item.packetId === packetOrControlId || item.id === packetOrControlId || item.controlId === packetOrControlId) || stagedReview;
    const packetId = candidate?.packetId || candidate?.id;

    if (!packetId) {
      setReviewCommandError('No backend packet id available for withdrawal.');
      return;
    }

    const route = `/api/crm/command/setup/reviews/${encodeURIComponent(packetId)}`;
    const payload = buildWilsySetupReviewLivePayload({
      route,
      ticket: candidate,
      domain: activeDomain,
      control: activeControl,
      lens,
    });

    setReviewCommandBusy('remove');
    setReviewCommandError(null);

    try {
      const data = await requestWilsySetupReviewLiveCommand(route, payload, 'DELETE');
      const removedTicket = normalizeWilsySetupReviewLivePacket(data.packet, candidate);

      setReviewQueue((current) => current.filter((item) => item.packetId !== packetId && item.id !== packetId));
      setPacketConsoleOpen(false);
      setReviewResult({
        ...removedTicket,
        status: data.result || 'Stage withdrawn with receipt',
        generatedAt: data.receipt?.generatedAt || data.auditEvidence?.generatedAt || new Date().toISOString(),
        receipt: data.receipt || removedTicket.receipt || null,
        auditEvidence: data.auditEvidence || removedTicket.auditEvidence || null,
      });
    } catch (error) {
      const message = error?.message || 'Setup review withdrawal failed.';
      setReviewCommandError(message);
      setReviewResult({
        ...(candidate || {}),
        status: 'Stage withdrawal failed',
        generatedAt: new Date().toISOString(),
        error: message,
      });
    } finally {
      setReviewCommandBusy('');
    }
  }

  /**
   * @function handleClearQueue
   * @description Clears the local staged review queue.
   * @returns {void}
   * @collaboration Review queue, result rail, and setup workbench reset state.
   */
  async function handleClearQueue() {
    const route = '/api/crm/command/setup/reviews/clear';
    const payload = buildWilsySetupReviewLivePayload({
      route,
      ticket: {
        id: `SETUP_REVIEW_CLEAR_${Date.now()}`,
        packetId: `SETUP_REVIEW_CLEAR_${Date.now()}`,
        controlId: activeControl.id,
        title: 'Clear setup review queue',
        owner: activeControl.owner,
        risk: activeControl.risk,
        state: activeControl.state,
      },
      domain: activeDomain,
      control: activeControl,
      lens,
    });

    setReviewCommandBusy('clear');
    setReviewCommandError(null);

    try {
      const data = await requestWilsySetupReviewLiveCommand(route, payload);
      setReviewQueue([]);
      setPacketConsoleOpen(false);
      setReviewResult({
        id: payload.packetId,
        packetId: payload.packetId,
        title: 'Setup review queue cleared',
        status: data.result || 'Backend queue cleared',
        generatedAt: data.receipt?.generatedAt || data.auditEvidence?.generatedAt || new Date().toISOString(),
        receipt: data.receipt || null,
        auditEvidence: data.auditEvidence || null,
        backendLive: true,
      });
    } catch (error) {
      const message = error?.message || 'Setup review queue clear failed.';
      setReviewCommandError(message);
      setReviewResult({
        title: 'Setup review queue',
        status: 'Backend clear failed',
        generatedAt: new Date().toISOString(),
        error: message,
      });
    } finally {
      setReviewCommandBusy('');
    }
  }

  /**
   * @function handlePreviousControl
   * @description Selects the previous control in the active domain and stops at the first control.
   * @returns {void}
   * @collaboration Control dropdown, control boundary algorithm, operating view area, authority rail, and OS navigation contract.
   */
  function handlePreviousControl() {
    if (isFirstControl) {
      return;
    }

    const previousControl = activeDomain.controls[activeControlIndex - 1] || activeControl;

    setActiveControlId(previousControl.id);
    setReviewResult({
      ...createReviewTicket(activeDomain, previousControl),
      status: 'Previous control selected',
    });
  }

  /**
   * @function handleNextControl
   * @description Selects the next control in the active domain and stops at the final control.
   * @returns {void}
   * @collaboration Control dropdown, control boundary algorithm, operating view area, authority rail, and OS navigation contract.
   */
  function handleNextControl() {
    if (isLastControl) {
      return;
    }

    const nextControl = activeDomain.controls[activeControlIndex + 1] || activeControl;

    setActiveControlId(nextControl.id);
    setReviewResult({
      ...createReviewTicket(activeDomain, nextControl),
      status: 'Next control selected',
    });
  }

  /**
   * @function handleOpenTicket
   * @description Opens a staged review ticket from the authority rail queue.
   * @param {Object} ticket - Review ticket.
   * @returns {void}
   * @collaboration Review queue, domain rail, control dropdown, view area, and authority rail.
   */
  async function handleOpenTicket(ticket = {}) {
    const packetId = ticket.packetId || ticket.id;

    if (!packetId) {
      setReviewCommandError('No backend packet id available to open.');
      return;
    }

    const route = '/api/crm/command/setup/reviews/open';
    const payload = buildWilsySetupReviewLivePayload({
      route,
      ticket: { ...ticket, packetId },
      domain: activeDomain,
      control: activeControl,
      lens,
    });

    setReviewCommandBusy('open');
    setReviewCommandError(null);

    try {
      const data = await requestWilsySetupReviewLiveCommand(route, payload);
      const backendTicket = normalizeWilsySetupReviewLivePacket(data.packet, ticket);

      if (backendTicket.domainId) setActiveDomainId(backendTicket.domainId);
      if (backendTicket.controlId) setActiveControlId(backendTicket.controlId);

      setReviewQueue((current) => [
        backendTicket,
        ...current.filter((item) => item.packetId !== backendTicket.packetId && item.controlId !== backendTicket.controlId),
      ]);
      setPacketConsoleOpen(true);
      setReviewResult({
        ...backendTicket,
        status: data.result || 'Backend packet opened',
        generatedAt: data.generatedAt || new Date().toISOString(),
      });
    } catch (error) {
      const message = error?.message || 'Setup review packet open failed.';
      setReviewCommandError(message);
      setReviewResult({
        ...ticket,
        status: 'Backend open failed',
        generatedAt: new Date().toISOString(),
        error: message,
      });
    } finally {
      setReviewCommandBusy('');
    }
  }


  /**
   * @function handleWilsySetupWorkflowCommand
   * @description Executes a backend-owned setup workflow command and refreshes the live Packet Console board through reviewResult and reviewQueue.
   * @param {Object} action - Workflow action configuration.
   * @returns {Promise<void>} Resolves after command feedback is updated.
   * @collaboration CRM setup workflow rail, backend evidence route, approval route, release route, review result state, review queue, receipts, and audit trail.
   */
  async function handleWilsySetupWorkflowCommand(action = {}) {
    handleWilsyPacketRevealNodeCancel();
    if (!action?.route) {
      setSetupWorkflowCommandFeedback('Workflow command route is unavailable.');
      return;
    }

    if (!stagedReview?.packetId) {
      setSetupWorkflowCommandFeedback('Stage a backend packet before running workflow actions.');
      return;
    }

    if (action.disabled) {
      setSetupWorkflowCommandFeedback(action.disabledReason || 'Workflow command is currently locked.');
      return;
    }

    setSetupWorkflowCommandBusy(action.id);
    setSetupWorkflowCommandFeedback(`${action.label} running through backend command authority...`);
    setReviewCommandError(null);

    try {
      const payload = buildWilsySetupReviewLivePayload({
        route: action.route,
        ticket: stagedReview || {},
        domain: activeDomain,
        control: activeControl || {},
        lens: stagedReview?.lens || lens || 'Authority',
      });
      const workflowPayload = {
        ...payload,
        packetId: stagedReview?.packetId || stagedReview?.id,
        controlId: stagedReview?.controlId || activeControl?.id || activeControl?.controlId,
      };

      if (action.id === 'attach-evidence') {
        const firstOpenRequirement = (stagedReview?.requiredEvidence || []).find((item) =>
          !setupWorkflowEvidenceLedger.some((record) => record?.requirement === item)
        ) || 'Risk and impact summary prepared';

        Object.assign(workflowPayload, {
          requirement: firstOpenRequirement,
          label: `${firstOpenRequirement} evidence`,
          type: 'OPERATOR_ATTESTATION',
          notes: 'Evidence attached from Wilsy OS Packet Console workflow rail.',
        });
      }

      if (action.id === 'approve') {
        Object.assign(workflowPayload, {
          approver: stagedReview?.operatorId || payload.operatorId || 'Current operator',
          approvalScope: `${stagedReview?.controlName || activeControl?.name || 'SETUP_REVIEW_PACKET'}_APPROVAL`,
        });
      }

      if (action.id === 'release') {
        Object.assign(workflowPayload, {
          releaseScope: `${stagedReview?.controlName || activeControl?.name || 'SETUP_REVIEW_PACKET'}_RELEASE`,
        });
      }

      const data = await requestWilsySetupReviewLiveCommand(action.route, workflowPayload);
      const backendTicket = normalizeWilsySetupReviewLivePacket(data.packet, {
        ...stagedReview,
        receipt: data.receipt || null,
        auditEvidence: data.auditEvidence || null,
      });

      setReviewQueue((current) => [
        backendTicket,
        ...current.filter((item) =>
          item.controlId !== backendTicket.controlId &&
          item.packetId !== backendTicket.packetId &&
          item.id !== backendTicket.id
        ),
      ].slice(0, 25));
      setReviewResult({
        ...backendTicket,
        status: data.result || action.label,
        generatedAt: data.receipt?.generatedAt || data.auditEvidence?.generatedAt || new Date().toISOString(),
        receipt: data.receipt || backendTicket.receipt || null,
        auditEvidence: data.auditEvidence || backendTicket.auditEvidence || null,
      });

      const receipts = Array.isArray(backendTicket?.receipts) ? backendTicket.receipts : [];
      const fallbackReceipt = receipts.length ? receipts[receipts.length - 1]?.receiptId : '';
      const receiptId = data?.receipt?.receiptId || fallbackReceipt || 'receipt returned';

      setSetupWorkflowCommandFeedback(`${action.label} complete · ${receiptId}`);
      handleWilsyPacketRevealNodeOpen(
        createWilsySetupWorkflowActionRevealNode(
          {
            ...action,
            status: data?.result || action.status,
            nextStep: `Backend returned ${data?.result || 'workflow result'} with receipt ${receiptId}.`,
          },
          backendTicket?.workflowState || setupWorkflowState,
          backendTicket || stagedReview
        )
      );
    } catch (error) {
      const message = error?.message || `${action.label} failed.`;
      setSetupWorkflowCommandFeedback(message);
      setReviewCommandError(message);
    } finally {
      setSetupWorkflowCommandBusy('');
    }
  }

  /**
   * @function handleCopyPacketProof
   * @description Copies a setup review proof value without browser prompts or disruptive modal flows.
   * @param {string} label - Copied value label.
   * @param {string} value - Copied value.
   * @returns {Promise<void>} Copy completion.
   * @collaboration Packet Console proof receipt, proof hash, browser clipboard, and audit evidence workflow.
   */
  async function handleCopyPacketProof(label, value = '') {
    const copyValue = String(value || '').trim();

    if (!copyValue || copyValue.toLowerCase().includes('pending')) {
      setCopyFeedback(`${label} is not ready yet.`);
      return;
    }

    try {
      if (typeof navigator !== 'undefined' && navigator.clipboard?.writeText) {
        await navigator.clipboard.writeText(copyValue);
      } else if (typeof document !== 'undefined') {
        const textArea = document.createElement('textarea');
        textArea.value = copyValue;
        textArea.setAttribute('readonly', 'true');
        textArea.style.position = 'fixed';
        textArea.style.opacity = '0';
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
      }

      setCopyFeedback(`${label} copied`);
      globalThis.setTimeout(() => setCopyFeedback(''), 1800);
    } catch {
      setCopyFeedback(`${label} could not be copied`);
    }
  }


  /**
   * @function handleWilsyPacketRevealNodeOpen
   * @description Opens the viewport-level Wilsy OS intelligence reveal panel through an intentional click, focus, or delayed hover.
   * @param {Object} node - Reveal-node payload.
   * @returns {void}
   * @collaboration Packet Console reveal dock, collision-aware reveal algorithm, WILSY OS micro-HUD, and operator intelligence panels.
   */
  function handleWilsyPacketRevealNodeOpen(node) {
    if (!node) return;

    setActiveRevealNode(node);
  }

  /**
   * @function handleWilsyPacketRevealNodeCancel
   * @description Cancels pending Wilsy OS reveal-node hover opening so scrolling does not trigger random intelligence panels.
   * @returns {void}
   * @collaboration Packet Console reveal-node algorithm, scroll safety, workflow command rail, and production operator UX.
   */
  function handleWilsyPacketRevealNodeCancel() {
    if (wilsyRevealHoverTimerRef.current) {
      globalThis.clearTimeout(wilsyRevealHoverTimerRef.current);
      wilsyRevealHoverTimerRef.current = null;
    }
  }

  /**
   * @function handleWilsyPacketRevealNodeSchedule
   * @description Schedules Wilsy OS reveal-node opening with a deliberate hover delay while click and focus remain intentional.
   * @param {Object} node - Reveal-node payload.
   * @param {Object} event - Pointer event.
   * @returns {void}
   * @collaboration Packet Console hover intelligence, release workflow click safety, delayed reveal UX, and Wilsy OS command board.
   */
  function handleWilsyPacketRevealNodeSchedule(node, event = {}) {
    const pointerType = event?.pointerType || 'mouse';

    if (pointerType !== 'mouse' && pointerType !== 'pen') {
      return;
    }

    handleWilsyPacketRevealNodeCancel();

    wilsyRevealHoverTimerRef.current = globalThis.setTimeout(() => {
      wilsyRevealHoverTimerRef.current = null;
      handleWilsyPacketRevealNodeOpen(node);
    }, wilsyRevealHoverDelayMs);
  }

  /**
   * @function handleWilsyPacketRevealNodeClose
   * @description Closes the viewport-level Wilsy OS intelligence reveal panel and cancels any pending hover-open timer.
   * @returns {void}
   * @collaboration Reveal node dock, top-center intelligence panel, operator workflow, and compact game-like HUD controls.
   */
  function handleWilsyPacketRevealNodeClose() {
    handleWilsyPacketRevealNodeCancel();
    setActiveRevealNode(null);
  }



  return (
    <section
      className={`${styles.setupSurface} ${!domainRailOpen ? styles.domainRailCollapsed : ''} ${!authorityRailOpen ? styles.authorityRailCollapsed : ''}`}
      aria-label="CRM setup operating surface"
    >
      <aside className={styles.domainRail} aria-label="Setup domain rail">
        <header className={styles.railChrome}>
          <div className={styles.railTitle}>
            <span>Domains</span>
            <strong>{domainRailOpen ? 'Setup map' : 'Map'}</strong>
          </div>

          <button
            type="button"
            className={`${styles.railFocusButton} ${!domainRailOpen ? styles.railFocusButtonCollapsed : ''}`}
            onClick={() => setDomainRailOpen((current) => !current)}
            aria-expanded={domainRailOpen}
            aria-label={domainRailOpen ? 'Collapse domain rail' : 'Open domain rail'}
            title={domainRailOpen ? 'Collapse domain rail' : 'Open domain rail'}
          >
            <span className={styles.railIconGlyph} aria-hidden="true">
              <span />
              <span />
            </span>
          </button>
        </header>

        <label className={styles.searchBox}>
          <span>Search</span>
          <input
            value={filterText}
            onChange={(event) => setFilterText(event.target.value)}
            placeholder="Find controls..."
          />
        </label>

        <div className={styles.domainList}>
          {domains.map((domain) => (
            <button
              type="button"
              key={domain.id}
              className={domain.id === activeDomain.id ? styles.domainActive : styles.domainButton}
              onClick={() => handleDomainChange(domain.id)}
            >
              <span>{domain.label}</span>
              <strong>{domain.score}</strong>
              <small>{domain.exposure} exposure · {domain.controls.length} controls</small>
            </button>
          ))}
        </div>
      </aside>

      <main className={styles.workbench} aria-label="Setup view area">
        <header className={styles.commandRail}>
          <button
            type="button"
            className={`${styles.commandTitle} ${styles.viewAreaContextTrigger} ${viewAreaConsoleOpen ? styles.viewAreaContextTriggerActive : ''}`}
            onClick={() => setViewAreaConsoleOpen((current) => !current)}
            aria-expanded={viewAreaConsoleOpen}
            aria-label={viewAreaConsoleOpen ? 'Close View Area console' : 'Open View Area console'}
            title={viewAreaConsoleOpen ? 'Close View Area console' : 'Open View Area console'}
          >
            <span className={styles.viewAreaContextGlyph} aria-hidden="true">
              <span />
              <span />
            </span>
            <span>View Area</span>
            <strong>{activeDomain.title}</strong>
          </button>

          <label>
            <span>Domain</span>
            <select value={activeDomain.id} onChange={(event) => handleDomainChange(event.target.value)}>
              {domains.map((domain) => (
                <option key={domain.id} value={domain.id}>{domain.label}</option>
              ))}
            </select>
          </label>

          <label>
            <span>Control</span>
            <select value={activeControl.id} onChange={(event) => setActiveControlId(event.target.value)}>
              {activeDomain.controls.map((control) => (
                <option key={control.id} value={control.id}>{control.name}</option>
              ))}
            </select>
          </label>

          <label>
            <span>Lens</span>
            <select value={lens} onChange={(event) => setLens(event.target.value)}>
              <option>Authority</option>
              <option>Risk</option>
              <option>Evidence</option>
              <option>Operations</option>
            </select>
          </label>

          <div className={styles.commandButtons} aria-label="Setup control commands">
            <button
              type="button"
              className={styles.stageCommandButton}
              onClick={handleStageReview}
              disabled={Boolean(stagedReview)}
              aria-disabled={Boolean(stagedReview)}
              title={stagedReview ? 'This control is already staged' : 'Stage this control for authority review'}
            >
              {stagedReview ? 'Staged' : 'Stage review'}
            </button>

            <div className={styles.controlNavCluster} aria-label="Control navigation">
              <button
                type="button"
                className={styles.navCommandButton}
                onClick={handlePreviousControl}
                disabled={isFirstControl}
                aria-disabled={isFirstControl}
                title={isFirstControl ? 'First control reached' : 'Previous control'}
              >
                Back
              </button>

              <button
                type="button"
                className={styles.navCommandButton}
                onClick={handleNextControl}
                disabled={isLastControl}
                aria-disabled={isLastControl}
                title={isLastControl ? 'Last control reached' : 'Next control'}
              >
                Next
              </button>
            </div>
          </div>
        </header>

        <section className={`${styles.viewArea} ${packetConsoleOpen && stagedReview ? styles.packetConsoleFocusMode : ''}`}>
          {viewAreaConsoleOpen ? (
          <section className={styles.viewAreaControlConsole} aria-label="View Area control console">
            <header>
              <div>
                <span>View Area Console</span>
                <strong>{activeDomain.title || activeDomain.name || activeDomain.label || activeDomain.id}</strong>
              </div>

              <button type="button" onClick={() => setViewAreaConsoleOpen(false)}>
                Close
              </button>
            </header>

            <div className={styles.viewAreaConsoleGrid}>
              <article>
                <span>Current control</span>
                <strong>{activeControl.name}</strong>
                <small>{activeControl.owner}</small>
              </article>

              <article>
                <span>Lens</span>
                <strong>{lens}</strong>
                <small>{activeControl.signal}</small>
              </article>

              <article>
                <span>Review state</span>
                <strong>{stagedReview ? 'Packet staged' : 'Ready'}</strong>
                <small>{stagedReview ? stagedReview.title : 'No packet staged'}</small>
              </article>

              <article>
                <span>Navigation</span>
                <strong>{isFirstControl ? 'First control' : isLastControl ? 'Last control' : 'Middle control'}</strong>
                <small>{isLastControl ? 'Next locked' : 'Next available'}</small>
              </article>
            </div>

            <div className={styles.viewAreaConsoleActions}>
              <button
                type="button"
                onClick={stagedReview ? () => handleOpenTicket(stagedReview) : handleStageReview}
              >
                {stagedReview ? 'Open packet' : 'Stage review'}
              </button>

              <button
                type="button"
                onClick={handlePreviousControl}
                disabled={isFirstControl}
                aria-disabled={isFirstControl}
              >
                Back
              </button>

              <button
                type="button"
                onClick={handleNextControl}
                disabled={isLastControl}
                aria-disabled={isLastControl}
              >
                Next
              </button>
            </div>
          </section>
        ) : null}

        <section className={styles.taskFocusBar} aria-label="Current setup task">
            <div className={styles.taskFocusIdentity}>
              <span>{lens} task</span>
              <strong>{activeControl.name}</strong>
            </div>

            <div className={styles.taskFocusMeta} aria-label="Task operating state">
              <article>
                <span>Owner</span>
                <strong>{activeControl.owner}</strong>
              </article>

              <article>
                <span>Risk</span>
                <strong className={resolveToneClass(activeControl.risk)}>{activeControl.risk}</strong>
              </article>

              <article>
                <span>State</span>
                <strong className={resolveToneClass(activeControl.state)}>{activeControl.state}</strong>
              </article>
            </div>

            <details className={styles.taskPurposeMenu}>
              <summary>Purpose</summary>
              <p>{activeControl.benefit}</p>
            </details>
          </section>

          <div
            className={`${styles.viewGrid} ${packetConsoleOpen && stagedReview ? styles.packetFullMode : stagedReview ? styles.reviewFocusMode : ''}`}
          >
            {packetConsoleOpen && stagedReview ? (
              <section className={styles.packetViewSurface} aria-label="Full packet console">
                <header className={styles.packetViewHeader}>
                  <div>
                    <span>Packet Console</span>
                    <strong>{stagedReview.title}</strong>
                    <p>{activeControl.benefit}</p>
                  </div>

                  <div className={styles.packetViewHeaderActions}>
                    <button type="button" onClick={() => setPacketConsoleOpen(false)}>
                      Back to review
                    </button>

                    <button
                      type="button"
                      onClick={handleNextControl}
                      disabled={isLastControl}
                      aria-disabled={isLastControl}
                    >
                      {isLastControl ? 'Last control reached' : 'Review next control'}
                    </button>

                    <button
                      type="button"
                      className={styles.packetViewDanger}
                      onClick={() => handleRemoveReview(stagedReview)}
                    >
                      Withdraw stage
                    </button>
                  </div>
                </header>

                <section className={styles.packetOutcomeStrip} aria-label="Live packet reveal dock and compact proof rail">
                  <div className={styles.packetRevealDock}>
                    <span className={styles.packetRevealDockLabel}>
                      <span className={styles.packetRevealPulse} />
                      WILSY OS
                    </span>

                    <div className={styles.packetRevealRail} role="list" aria-label="Compact packet state nodes">
                      {packetRevealNodes.map((node) => (
                        <button
                          key={node.id}
                          type="button"
                          className={`${styles.packetRevealNode} ${node.className || ''}`}
                          onPointerEnter={(event) => handleWilsyPacketRevealNodeSchedule(node, event)}
                          onPointerLeave={handleWilsyPacketRevealNodeCancel}
                          onFocus={() => handleWilsyPacketRevealNodeOpen(node)}
                          onClick={() => handleWilsyPacketRevealNodeOpen(node)}
                        >
                          <span className={styles.packetRevealLabel}>{node.label}</span>
                          <strong>{node.status}</strong>
                        </button>
                      ))}
                    </div>

                    <WilsyRevealViewportPanel
                      node={activeRevealNode}
                      copyFeedback={copyFeedback}
                      onClose={handleWilsyPacketRevealNodeClose}
                    />
                  </div>

                  <div className={styles.packetProofMicroRail} aria-label="Compact backend proof rail">
                    <article
                      className={styles.packetProofMicroCell}
                      tabIndex={0}
                      onPointerEnter={(event) => handleWilsyPacketRevealNodeSchedule(packetRevealNodes.find((node) => node.id === 'proof'), event)}
                      onPointerLeave={handleWilsyPacketRevealNodeCancel}
                      onFocus={() => handleWilsyPacketRevealNodeOpen(packetRevealNodes.find((node) => node.id === 'proof'))}
                    >
                      <span>Proof</span>
                      <strong>{packetProofBusinessLabel}</strong>
                      <small>Backend evidence ready</small>

                      <button
                        type="button"
                        onClick={() => handleCopyPacketProof('Proof receipt', packetProofReceiptId)}
                      >
                        Copy
                      </button>
                    </article>

                    <article
                      className={styles.packetProofMicroCell}
                      tabIndex={0}
                      onPointerEnter={(event) => handleWilsyPacketRevealNodeSchedule(packetRevealNodes.find((node) => node.id === 'proof'), event)}
                      onPointerLeave={handleWilsyPacketRevealNodeCancel}
                      onFocus={() => handleWilsyPacketRevealNodeOpen(packetRevealNodes.find((node) => node.id === 'proof'))}
                    >
                      <span>Hash</span>
                      <strong>{packetHashBusinessLabel}</strong>
                      <small>Technical proof hidden</small>

                      <button
                        type="button"
                        onClick={() => handleCopyPacketProof('Tamper-proof hash', packetProofHash)}
                      >
                        Copy
                      </button>
                    </article>

                    <article
                      className={styles.packetProofMicroCell}
                      tabIndex={0}
                      onPointerEnter={(event) => handleWilsyPacketRevealNodeSchedule(packetRevealNodes.find((node) => node.id === 'proof'), event)}
                      onPointerLeave={handleWilsyPacketRevealNodeCancel}
                      onFocus={() => handleWilsyPacketRevealNodeOpen(packetRevealNodes.find((node) => node.id === 'proof'))}
                    >
                      <span>Audit</span>
                      <strong>{packetAuditBusinessStatus}</strong>
                      <small>Latest backend event</small>
                    </article>
                  </div>
                </section>

                <section className={styles.packetViewGrid} aria-label="Wilsy OS packet operating board">
                <div className={`${styles.packetBoardLane} ${styles.packetBoardLaneLeft}`} aria-label="Authority and gate operating lane">
<article className={`${styles.packetViewCard} ${styles.authorityRailMissionCard}`}>
                    <header className={styles.authorityRailHeader}>
                      <div>
                        <span>WILSY OS · Authority packet</span>
                        <strong>4 live authority facts</strong>
                        <small>Packet, owner, risk, and state are live packet controls. Technical references stay hidden behind copy.</small>
                      </div>

                      <button
                        type="button"
                        onClick={() => handleCopyPacketProof('Authority packet facts', authorityRailChecklist)}
                      >
                        Copy packet
                      </button>
                    </header>

                    <div className={styles.authorityRailCapsuleGrid} aria-label="Authority packet live fact nodes">
                      {authorityRailItems.map((item) => (
                        <button
                          key={item.id}
                          type="button"
                          className={styles.authorityRailCapsuleNode}
                          onPointerEnter={(event) => handleWilsyPacketRevealNodeSchedule(createWilsySetupAuthorityRailRevealNode(item, handleCopyPacketProof), event)}
                          onPointerLeave={handleWilsyPacketRevealNodeCancel}
                          onFocus={() => handleWilsyPacketRevealNodeOpen(createWilsySetupAuthorityRailRevealNode(item, handleCopyPacketProof))}
                          onClick={() => handleWilsyPacketRevealNodeOpen(createWilsySetupAuthorityRailRevealNode(item, handleCopyPacketProof))}
                        >
                          <span>{item.label}</span>
                          <strong>{item.status}</strong>
                          <small>{item.impact}</small>
                        </button>
                      ))}
                    </div>
                  </article>
<article className={`${styles.packetViewCard} ${styles.gateRailMissionCard}`}>
                    <header className={styles.gateRailHeader}>
                      <div>
                        <span>WILSY OS · Gate control</span>
                        <strong>2 locked release gates</strong>
                        <small>Approval and release remain locked until accountable evidence is ready.</small>
                      </div>

                      <button
                        type="button"
                        onClick={() => handleCopyPacketProof('Gate control plan', gateRailChecklist)}
                      >
                        Copy gate plan
                      </button>
                    </header>

                    <div className={styles.gateRailCapsuleGrid} aria-label="Locked gate control nodes">
                      {gateRailItems.map((item) => (
                        <button
                          key={item.id}
                          type="button"
                          className={styles.gateRailCapsuleNode}
                          onPointerEnter={(event) => handleWilsyPacketRevealNodeSchedule(createWilsySetupAuthorityRailRevealNode(item, handleCopyPacketProof), event)}
                          onPointerLeave={handleWilsyPacketRevealNodeCancel}
                          onFocus={() => handleWilsyPacketRevealNodeOpen(createWilsySetupAuthorityRailRevealNode(item, handleCopyPacketProof))}
                          onClick={() => handleWilsyPacketRevealNodeOpen(createWilsySetupAuthorityRailRevealNode(item, handleCopyPacketProof))}
                        >
                          <span>{item.label}</span>
                          <strong>{item.status}</strong>
                          <small>{item.impact}</small>
                        </button>
                      ))}
                    </div>
                  </article>

                  <article className={`${styles.packetViewCard} ${styles.setupWorkflowMissionCard}`} aria-label="Setup workflow command rail">
                    <header className={styles.setupWorkflowHeader}>
                      <div>
                        <span>WILSY OS · Workflow expansion rail</span>
                        <strong>{setupWorkflowGateLabel}</strong>
                        <small>Backend-owned commands: evidence, approval, and release. Every action returns receipt and audit evidence.</small>
                      </div>

                      <button
                        type="button"
                        onClick={() => handleCopyPacketProof('Workflow receipt', setupWorkflowReceiptLabel)}
                      >
                        Copy workflow receipt
                      </button>
                    </header>

                    <div className={styles.setupWorkflowStatusGrid} aria-label="Setup workflow state">
                      {setupWorkflowTimeline.map((item) => (
                        <div key={item.id} className={styles.setupWorkflowStatusNode}>
                          <span>{item.label}</span>
                          <strong>{item.value}</strong>
                          <small>{item.status}</small>
                        </div>
                      ))}
                    </div>

                    <div className={styles.setupWorkflowActionRail} aria-label="Setup workflow actions">
                      {setupWorkflowActions.map((action) => (
                        <button
                          key={action.id}
                          type="button"
                          className={`${styles.setupWorkflowActionNode} ${action.disabled ? styles.setupWorkflowActionNodeDisabled : ''}`}
                          disabled={Boolean(action.disabled || setupWorkflowCommandBusy)}
                          onPointerEnter={(event) => handleWilsyPacketRevealNodeSchedule(createWilsySetupWorkflowActionRevealNode(action, setupWorkflowState, stagedReview), event)}
                          onPointerLeave={handleWilsyPacketRevealNodeCancel}
                          onFocus={() => handleWilsyPacketRevealNodeOpen(createWilsySetupWorkflowActionRevealNode(action, setupWorkflowState, stagedReview))}
                          onClick={() => handleWilsySetupWorkflowCommand(action)}
                        >
                          <span>{action.label}</span>
                          <strong>{setupWorkflowCommandBusy === action.id ? 'Running' : action.status}</strong>
                          <small>{action.disabled ? action.disabledReason : 'Backend command'}</small>
                        </button>
                      ))}
                    </div>

                    {setupWorkflowCommandFeedback ? (
                      <p className={styles.setupWorkflowFeedback}>{setupWorkflowCommandFeedback}</p>
                    ) : null}
                  </article>
                </div>

                <div className={`${styles.packetBoardLane} ${styles.packetBoardLaneRight}`} aria-label="Evidence and system impact operating lane">
<article className={`${styles.packetViewCard} ${styles.packetEvidenceMissionCard}`}>
                    <header className={styles.packetEvidenceCommandHeader}>
                      <div>
                        <span>WILSY OS · Evidence rail</span>
                        <strong>{packetEvidenceSummary}</strong>
                        <small>Hover or focus a node to inspect purpose, gate impact, and the next productive action.</small>
                      </div>

                      <button
                        type="button"
                        onClick={() => handleCopyPacketProof('Evidence checklist', packetEvidenceChecklist)}
                      >
                        Copy checklist
                      </button>
                    </header>

                    <div className={styles.packetEvidenceCapsuleRail} aria-label="Backend evidence requirement nodes">
                      {packetEvidenceItems.map((item) => (
                        <button
                          key={item.id}
                          type="button"
                          className={styles.packetEvidenceCapsuleNode}
                          onPointerEnter={(event) => handleWilsyPacketRevealNodeSchedule(createWilsySetupReviewEvidenceRevealNode(item, handleCopyPacketProof), event)}
                          onPointerLeave={handleWilsyPacketRevealNodeCancel}
                          onFocus={() => handleWilsyPacketRevealNodeOpen(createWilsySetupReviewEvidenceRevealNode(item, handleCopyPacketProof))}
                          onClick={() => handleWilsyPacketRevealNodeOpen(createWilsySetupReviewEvidenceRevealNode(item, handleCopyPacketProof))}
                        >
                          <span>{item.shortLabel}</span>
                          <strong>{item.status}</strong>
                          <small>{item.gateImpact}</small>
                        </button>
                      ))}
                    </div>
                  </article>
<article className={`${styles.packetViewCard} ${styles.surfaceImpactMissionCard}`}>
                    <header className={styles.surfaceImpactHeader}>
                      <div>
                        <span>WILSY OS · System impact rail</span>
                        <strong>{surfaceRailSummary}</strong>
                        <small>Each affected system is a live packet surface. Inspect the node to see risk, purpose, and the next productive action.</small>
                      </div>

                      <button
                        type="button"
                        onClick={() => handleCopyPacketProof('System impact map', surfaceRailMap)}
                      >
                        Copy impact map
                      </button>
                    </header>

                    <div className={styles.surfaceImpactCapsuleRail} aria-label="Affected system impact nodes">
                      {surfaceRailItems.map((item) => (
                        <button
                          key={item.id}
                          type="button"
                          className={styles.surfaceImpactCapsuleNode}
                          onPointerEnter={(event) => handleWilsyPacketRevealNodeSchedule(createWilsySetupSurfaceRevealNode(item, handleCopyPacketProof), event)}
                          onPointerLeave={handleWilsyPacketRevealNodeCancel}
                          onFocus={() => handleWilsyPacketRevealNodeOpen(createWilsySetupSurfaceRevealNode(item, handleCopyPacketProof))}
                          onClick={() => handleWilsyPacketRevealNodeOpen(createWilsySetupSurfaceRevealNode(item, handleCopyPacketProof))}
                        >
                          <span>{item.label}</span>
                          <strong>{item.status}</strong>
                          <small>{item.impact}</small>
                        </button>
                      ))}
                    </div>
                  </article>
                </div>
              </section>
              </section>
            ) : stagedReview ? (
              <section className={styles.reviewFocusWorkspace} aria-label="Staged review focus workspace">
                <article className={styles.reviewFocusPrimary}>
                  <span>Active packet</span>
                  <strong>{stagedReview.title}</strong>
                  <p>{activeControl.benefit}</p>

                  <div className={styles.reviewFocusFacts}>
                    <article>
                      <span>Owner</span>
                      <strong>{stagedReview.owner}</strong>
                    </article>

                    <article>
                      <span>Risk</span>
                      <strong className={resolveToneClass(stagedReview.risk)}>{stagedReview.risk}</strong>
                    </article>

                    <article>
                      <span>State</span>
                      <strong className={resolveToneClass(activeControl.state)}>{activeControl.state}</strong>
                    </article>
                  </div>
                </article>

                <article className={styles.reviewFocusPath}>
                  <span>Completion path</span>

                  <ol>
                    <li className={styles.reviewPathDone}>
                      <strong>Packet staged</strong>
                      <small>Review packet prepared for authority review.</small>
                    </li>

                    <li className={styles.reviewPathLocked}>
                      <strong>Approval waiting</strong>
                      <small>Requires authorized approver before release.</small>
                    </li>

                    <li className={styles.reviewPathLocked}>
                      <strong>Release waiting</strong>
                      <small>Requires evidence receipt after approval.</small>
                    </li>
                  </ol>
                </article>

                <article className={styles.reviewFocusFeedback}>
                  <span>Action feedback</span>
                  <strong>{reviewResult ? reviewResult.status : 'Packet staged'}</strong>
                  <small>{reviewResult ? reviewResult.generatedAt : stagedReview.generatedAt}</small>
                  {reviewCommandError ? <small>{reviewCommandError}</small> : null}

                  <div className={styles.packetActionStack}>
                    <button type="button" onClick={() => handleOpenTicket(stagedReview)}>
                      Open packet
                    </button>

                    <button
                      type="button"
                      onClick={handleNextControl}
                      disabled={isLastControl}
                      aria-disabled={isLastControl}
                    >
                      {isLastControl ? 'Last control reached' : 'Review next control'}
                    </button>

                    <button
                      type="button"
                      className={styles.reviewFocusDanger}
                      onClick={() => handleRemoveReview(stagedReview)}
                    >
                      Withdraw stage
                    </button>
                  </div>
                </article>
              </section>
            ) : (
              <>
                <article className={styles.viewPanel}>
                  <span>Work queue</span>
                  <div className={styles.workStepList}>
                    {activeControl.workItems.map((item, index) => (
                      <button type="button" key={item}>
                        <span>{String(index + 1).padStart(2, '0')}</span>
                        <strong>{item}</strong>
                        <small>{activeControl.owner}</small>
                      </button>
                    ))}
                  </div>
                </article>

                <article className={styles.viewPanel}>
                  <span>Affected surfaces</span>
                  <div className={styles.surfaceImpactList}>
                    {activeControl.surfaces.map((surface) => (
                      <article key={surface}>
                        <span>{surface}</span>
                        <strong>Governed surface</strong>
                        <small>{activeControl.state}</small>
                      </article>
                    ))}
                  </div>
                </article>

                <article className={styles.viewPanel}>
                  <span>Control posture</span>
                  <div className={styles.decisionSignalGrid}>
                    <article>
                      <span>Risk</span>
                      <strong className={resolveToneClass(activeControl.risk)}>{activeControl.risk}</strong>
                    </article>

                    <article>
                      <span>State</span>
                      <strong className={resolveToneClass(activeControl.state)}>{activeControl.state}</strong>
                    </article>

                    <article>
                      <span>Owner</span>
                      <strong>{activeControl.owner}</strong>
                    </article>

                    <article>
                      <span>Purpose</span>
                      <strong>{activeControl.signal}</strong>
                    </article>
                  </div>
                </article>
              </>
            )}
          </div>
        </section>
      </main>

      <aside className={styles.authorityRail} aria-label="Authority rail">
        <header className={styles.authorityRailChrome}>
          <div>
            <span>Authority</span>
            <strong>{authorityRailOpen ? 'Inspector' : 'Rail'}</strong>
          </div>

          <button
            type="button"
            className={`${styles.railFocusButton} ${!authorityRailOpen ? styles.railFocusButtonCollapsed : ''}`}
            onClick={() => setAuthorityRailOpen((current) => !current)}
            aria-expanded={authorityRailOpen}
            aria-label={authorityRailOpen ? 'Collapse authority rail' : 'Open authority rail'}
            title={authorityRailOpen ? 'Collapse authority rail' : 'Open authority rail'}
          >
            <span className={styles.railIconGlyph} aria-hidden="true">
              <span />
              <span />
            </span>
          </button>
        </header>

        <section className={styles.scoreRail}>
          <article>
            <span>Trust</span>
            <strong>{posture.score}</strong>
          </article>
          <article>
            <span>Exposure</span>
            <strong>{posture.exposure}</strong>
          </article>
          <article>
            <span>Queue</span>
            <strong>{posture.queueSize}</strong>
          </article>
        </section>

        <section className={styles.inspector}>
          <span>Inspector</span>
          <strong>{activeControl.name}</strong>
          <p>{activeDomain.purpose}</p>

          <div className={styles.inspectorFacts}>
            <article>
              <span>Owner</span>
              <strong>{activeControl.owner}</strong>
            </article>
            <article>
              <span>Engine</span>
              <strong>{activeControl.engine}</strong>
            </article>
            <article>
              <span>Investor signal</span>
              <strong>{activeControl.signal}</strong>
            </article>
          </div>
        </section>

        <section className={styles.evidenceRail}>
          <span>Evidence pack</span>
          <div>
            {evidencePack.map((item) => (
              <strong key={item}>{item}</strong>
            ))}
          </div>
        </section>

        <section className={styles.queueRail}>
          <header>
            <span>Staged reviews</span>
            <button type="button" onClick={handleClearQueue}>Clear</button>
          </header>

          {reviewQueue.length ? (
            <div>
              {reviewQueue.map((ticket) => (
                <article key={ticket.id}>
                  <button type="button" onClick={() => handleOpenTicket(ticket)}>
                    <span>{ticket.domain}</span>
                    <strong>{ticket.title}</strong>
                    <small>{ticket.owner} · {ticket.risk}</small>
                  </button>

                  <button type="button" onClick={() => handleRemoveReview(ticket.controlId)}>Remove</button>
                </article>
              ))}
            </div>
          ) : (
            <p>No staged reviews.</p>
          )}
        </section>
      </aside>
    </section>
  );
}
