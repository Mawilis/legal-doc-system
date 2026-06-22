/* eslint-disable */
import React, { useEffect, useMemo, useState } from 'react';
import WILSY_SOURCE_REPAIR_LOGO_URL from '../../assets/logo/wilsy.jpeg';
import {
  AlignmentType,
  Document,
  HeadingLevel,
  Packer,
  Paragraph,
  Table,
  TableCell,
  TableRow,
  TextRun,
  WidthType
} from 'docx';
import * as artifactCatalogModule from '../../data/wilsyArtifactCatalog';
import { generateArtifactExport } from '../../services/artifacts/artifactExportService';
import {
  enrichSourceRegistryFinding,
  summarizeSourceEvidenceRepairPlan
} from '../../data/sourceEvidenceRequirementsMatrix';
import {
  getSourceRegistryStatus,
  verifySourceRegistry,
  sealBoardroomProof,
  buildInvestorPack,
  summarizeSourceRegistry,
  statusTone
} from '../../services/sourceRegistryService';

const ARTIFACT_API_BASE_URL = (import.meta.env.VITE_API_URL || 'http://localhost:5050').replace(/\/$/, '');
const ARTIFACT_GENERATION_TIMEOUT_MS = 60000;

const ARTIFACT_REQUEST_EVENTS = Object.freeze([
  'wilsy:artifact-request',
  'wilsy:business-artifact-request',
  'wilsy:business-artifacts-open',
  'wilsy:open-business-artifacts',
  'wilsy:open-artifact-studio',
  'business-artifact-request',
  'business-artifacts-open',
  'open-business-artifacts',
  'openBusinessArtifacts',
  'openBusinessArtifactStudio',
  'WILSY_ARTIFACT_REQUEST',
  'WILSY_BUSINESS_ARTIFACT_REQUEST',
  'WILSY_BUSINESS_ARTIFACTS_OPEN',
  'WILSY_OPEN_BUSINESS_ARTIFACTS',
  'WILSY_OPEN_ARTIFACT_STUDIO'
]);

const BUSINESS_ARTIFACT_CATALOG =
  artifactCatalogModule.BUSINESS_ARTIFACT_CATALOG ||
  artifactCatalogModule.WILSY_ARTIFACT_CATALOG ||
  artifactCatalogModule.WILSY_BUSINESS_ARTIFACT_CATALOG ||
  artifactCatalogModule.ARTIFACT_CATALOG ||
  artifactCatalogModule.BUSINESS_ARTIFACTS ||
  artifactCatalogModule.default ||
  [];

const LIFECYCLE_STAGES = Object.freeze(['Draft', 'Review', 'Approve', 'Send', 'Sign', 'Vault']);

const FORMAT_META = Object.freeze({
  PDF: { label: 'PDF', detail: 'Boardroom proof-sealed PDF' },
  DOCX: { label: 'DOCX', detail: 'Editable OpenXML legal review file' },
  JSON: { label: 'JSON', detail: 'System audit payload' },
  EMAIL: { label: 'SEND PACK', detail: 'Email package with PDF attached' },
  XLSX: { label: 'XLSX', detail: 'Finance-ready register export' }
});

/**
 * @function normalizeArtifactType
 * @description Normalizes any artifact identifier into the backend-safe artifact type format.
 * @param {string} value - Raw artifact identifier.
 * @returns {string} Normalized artifact type.
 * @collaboration Aligns dashboard artifact commands with the branded artifact PDF controller.
 */
function normalizeArtifactType(value = 'artifact') {
  return String(value || 'artifact').trim().toLowerCase().replace(/_/g, '-');
}

/**
 * @function safeFileName
 * @description Converts artifact names into safe local download filenames.
 * @param {string} value - Raw filename value.
 * @returns {string} Safe filename segment.
 * @collaboration Keeps BusinessArtifactStudio downloads stable across generated artifact types.
 */
function safeFileName(value = 'artifact') {
  return String(value || 'artifact')
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-|-$/g, '') || 'artifact';
}


/**
 * @function formatArtifactReceipt
 * @description Formats the last generated artifact as a clean executive receipt label.
 * @param {object|null} receipt - Last artifact receipt.
 * @returns {string} Human-readable artifact receipt.
 * @collaboration Prevents raw filenames from degrading the Wilsy OS executive interface.
 */
function formatArtifactReceipt(receipt) {
  if (!receipt) return 'None this session';

  const title = receipt.title || 'Artifact';
  const format = receipt.format || String(receipt.filename || '').split('.').pop()?.toUpperCase() || 'EXPORT';

  return `${title} · ${format}`;
}

/**
 * @function buildSourceRegistryCommandLabel
 * @description Builds the live Source Registry command label from backend evidence state.
 * @param {object} summary - Source Registry summary model.
 * @returns {string} Live command label.
 * @collaboration Replaces prototype status chatter with boardroom-grade evidence posture language.
 */
function buildSourceRegistryCommandLabel(summary = {}) {
  const status = String(summary.status || summary.evidenceStatus || 'NOT_EVALUATED').toUpperCase();
  const actionRequired =
    Number(summary.pending || 0) +
    Number(summary.missing || 0) +
    Number(summary.error || 0) +
    Number(summary.blocked || 0);

  if (!summary.backendLinked) return 'Source Evidence Control Plane · awaiting live registry';
  if (status === 'VERIFIED' && actionRequired === 0) return 'Source Evidence Control Plane · verified';
  if (Number(summary.error || 0) > 0) return 'Source Evidence Control Plane · action required';
  if (Number(summary.missing || 0) > 0) return 'Source Evidence Control Plane · evidence gaps';
  if (Number(summary.pending || 0) > 0) return 'Source Evidence Control Plane · pending verification';

  return `Source Evidence Control Plane · ${status.replace(/_/g, ' ').toLowerCase()}`;
}

/**
 * @function buildSourceRegistryCommandDetail
 * @description Builds the live Source Registry command detail without hardcoded prototype copy.
 * @param {object} summary - Source Registry summary model.
 * @param {number} visibleArtifactTotal - Number of visible artifacts.
 * @returns {string} Live command detail.
 * @collaboration Shows operators the exact evidence posture while keeping VERIFIED reserved for live proof only.
 */
function buildSourceRegistryCommandDetail(summary = {}, visibleArtifactTotal = 0) {
  if (!summary.backendLinked) {
    return `${visibleArtifactTotal} visible artifacts require Source Registry verification before external reliance.`;
  }

  const total = Number(summary.total || visibleArtifactTotal || 0);
  const verified = Number(summary.verified || 0);
  const pending = Number(summary.pending || 0);
  const missing = Number(summary.missing || 0);
  const errors = Number(summary.error || 0);
  const blocked = Number(summary.blocked || 0);
  const repairSignals = pending + missing + errors + blocked;

  if (repairSignals === 0 && verified === total && total > 0) {
    return `${verified}/${total} evidence-backed artifacts verified. Boardroom sealing can proceed.`;
  }

  return `${verified}/${total} verified · ${repairSignals} live repair signals · ${missing} evidence gaps · ${errors} connector errors · ${blocked} blocked.`;
}

/**
 * @function buildSourceRegistryVerificationMessage
 * @description Builds the live post-verification message shown after Source Registry verification.
 * @param {object} summary - Source Registry summary model.
 * @returns {string} Verification result message.
 * @collaboration Converts verification output into an execution command instead of prototype completion text.
 */
function buildSourceRegistryVerificationMessage(summary = {}) {
  const total = Number(summary.total || 0);
  const verified = Number(summary.verified || 0);
  const pending = Number(summary.pending || 0);
  const missing = Number(summary.missing || 0);
  const errors = Number(summary.error || 0);
  const blocked = Number(summary.blocked || 0);
  const repairSignals = pending + missing + errors + blocked;

  if (repairSignals === 0 && total > 0 && verified === total) {
    return `Source Registry verification cleared: ${verified}/${total} artifacts verified. Boardroom proof sealing is ready.`;
  }

  return `Source Registry verification produced ${repairSignals} live repair signals across ${total} artifacts: ${errors} connector errors, ${missing} evidence gaps, ${pending} pending, ${blocked} blocked. Open Evidence Breakdown to execute repairs.`;
}

/**
 * @function sourceStatusForArtifact
 * @description Resolves source truth without inventing placeholder readiness percentages.
 * @param {object} artifact - Artifact template.
 * @returns {{label:string, detail:string, tone:string}} Source status model.
 * @collaboration Prevents fake prototype source-readiness percentages from appearing in Wilsy OS.
 */
function sourceStatusForArtifact(artifact = {}) {
  const hasVerifiedSource =
    artifact.sourceVerified === true ||
    artifact.sourceLinked === true ||
    artifact.sourcePosture === 'VERIFIED' ||
    artifact.sourcePosture === 'SOURCE_VERIFIED' ||
    (Array.isArray(artifact.sourceFields) && artifact.sourceFields.length > 0);

  if (hasVerifiedSource) {
    return {
      label: 'Verified source-linked',
      detail: 'Source evidence connected',
      tone: 'verified'
    };
  }

  return {
    label: 'Source fields required',
    detail: 'No verified source evidence linked',
    tone: 'required'
  };
}

/**
 * @function resolveArtifactApiUrl
 * @description Resolves artifact API calls directly to the backend without duplicate api prefixes.
 * @param {string} apiPath - API path.
 * @returns {string} Absolute backend URL.
 * @collaboration Prevents frontend proxy noise from blocking business artifact generation.
 */
function resolveArtifactApiUrl(apiPath) {
  const base = ARTIFACT_API_BASE_URL.replace(/\/api$/i, '');
  const path = apiPath.startsWith('/') ? apiPath : `/${apiPath}`;
  return `${base}${path}`;
}

/**
 * @function createCanonicalArtifactProof
 * @description Creates the canonical backend artifact proof using SHA-512(type|tenantId|timestamp).
 * @param {string} artifactType - Artifact type sent to the backend.
 * @param {string} tenantId - Tenant identifier.
 * @param {string} timestamp - ISO timestamp.
 * @returns {Promise<string>} SHA-512 digest.
 * @collaboration Aligns browser artifact proof generation with businessArtifactPdfController verification.
 */
async function createCanonicalArtifactProof(artifactType, tenantId, timestamp) {
  const canonical = `${artifactType}|${tenantId}|${timestamp}`;
  const digest = await window.crypto.subtle.digest('SHA-512', new TextEncoder().encode(canonical));

  return Array.from(new Uint8Array(digest))
    .map((byte) => byte.toString(16).padStart(2, '0'))
    .join('');
}

/**
 * @function fetchArtifactWithTimeout
 * @description Fetches an artifact with a hard timeout so generation cannot hang forever.
 * @param {string} url - Absolute URL.
 * @param {RequestInit} options - Fetch options.
 * @returns {Promise<Response>} Fetch response.
 * @collaboration Keeps operator actions recoverable when backend export services fail.
 */
async function fetchArtifactWithTimeout(url, options = {}) {
  const controller = new AbortController();
  const timeoutId = window.setTimeout(() => controller.abort(), ARTIFACT_GENERATION_TIMEOUT_MS);

  try {
    return await fetch(url, { ...options, signal: controller.signal });
  } finally {
    window.clearTimeout(timeoutId);
  }
}

/**
 * @function readArtifactError
 * @description Reads an artifact endpoint failure body safely.
 * @param {Response} response - Failed fetch response.
 * @returns {Promise<string>} Failure text.
 * @collaboration Makes backend rejection reasons visible to the operator.
 */
async function readArtifactError(response) {
  try {
    const text = await response.text();
    return text || `Artifact endpoint failed ${response.status}`;
  } catch {
    return `Artifact endpoint failed ${response.status}`;
  }
}

/**
 * @function downloadBlob
 * @description Downloads a browser blob as a local file.
 * @param {Blob} blob - Blob content.
 * @param {string} filename - Download filename.
 * @returns {void}
 * @collaboration Converts generated artifacts into a real operator download.
 */
function downloadBlob(blob, filename) {
  const url = window.URL.createObjectURL(blob);
  const anchor = document.createElement('a');

  anchor.href = url;
  anchor.download = filename;
  document.body.appendChild(anchor);
  anchor.click();
  anchor.remove();

  window.setTimeout(() => window.URL.revokeObjectURL(url), 1200);
}

/**
 * @function getBrowserToken
 * @description Reads the currently stored browser token from common Wilsy OS storage keys.
 * @returns {string} Bearer token value without the Bearer prefix.
 * @collaboration Keeps artifact generation authenticated without coupling to one auth context implementation.
 */
function getBrowserToken() {
  const token = window.localStorage.getItem('token')
    || window.localStorage.getItem('accessToken')
    || window.localStorage.getItem('wilsy_token')
    || window.sessionStorage.getItem('token')
    || window.sessionStorage.getItem('accessToken')
    || '';

  return token.replace(/^Bearer\s+/i, '');
}

/**
 * @function blobToBase64
 * @description Converts a blob to base64 for email package attachments.
 * @param {Blob} blob - Blob content.
 * @returns {Promise<string>} Base64 content.
 * @collaboration Enables real email packages without pretending mailto can attach files.
 */
function blobToBase64(blob) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();

    reader.onload = () => {
      const value = String(reader.result || '');
      resolve(value.includes(',') ? value.split(',')[1] : value);
    };

    reader.onerror = () => reject(reader.error || new Error('Unable to read blob.'));
    reader.readAsDataURL(blob);
  });
}

/**
 * @function wrapBase64
 * @description Wraps base64 content for MIME email packages.
 * @param {string} value - Base64 value.
 * @returns {string} Wrapped base64.
 * @collaboration Produces email-package attachments compatible with desktop mail clients.
 */
function wrapBase64(value) {
  return String(value || '').match(/.{1,76}/g)?.join('\r\n') || '';
}

/**
 * @function normaliseCatalog
 * @description Normalizes registry artifacts for the lifecycle console.
 * @param {Array<object>} catalog - Raw registry catalog.
 * @returns {Array<object>} Normalized artifacts.
 * @collaboration Turns the full registry into a multi-business-model artifact operating surface.
 */
function normaliseCatalog(catalog = []) {
  return catalog.map((item, index) => {
    const title = item.title || item.name || `Business Artifact ${index + 1}`;
    const type = normalizeArtifactType(item.type || item.id || title);
    const id = item.id || type;
    const formats = Array.from(new Set([...(item.formats || ['PDF', 'DOCX', 'JSON']), 'EMAIL']));

    return {
      ...item,
      id,
      type,
      title,
      category: item.category || 'Enterprise Operations',
      description: item.description || 'Enterprise artifact with review, proof, approval, send and vault controls.',
      formats
    };
  });
}

/**
 * @function readinessForArtifact
 * @description Calculates a deterministic readiness score for an artifact.
 * @param {object} artifact - Artifact template.
 * @returns {number} Readiness score.
 * @collaboration Gives every artifact an operating-system readiness signal instead of flat export buttons.
 */
function readinessForArtifact(artifact) {
  const seed = `${artifact.type}${artifact.category}${artifact.title}`.split('').reduce((sum, char) => sum + char.charCodeAt(0), 0);
  return 62 + (seed % 31);
}

/**
 * @function riskForArtifact
 * @description Classifies artifact risk by business family and document type.
 * @param {object} artifact - Artifact template.
 * @returns {string} Risk level.
 * @collaboration Makes Wilsy OS feel like a governance layer, not a file exporter.
 */
function riskForArtifact(artifact) {
  const text = `${artifact.category} ${artifact.title} ${artifact.type}`.toLowerCase();

  if (/data|privacy|popia|processing|security|employment|shareholder|board|msa|sla/.test(text)) return 'HIGH';
  if (/invoice|receipt|proposal|quote|policy|procurement|supplier/.test(text)) return 'MEDIUM';
  return 'STANDARD';
}

/**
 * @function approvalsForArtifact
 * @description Resolves likely approvals required for an artifact type.
 * @param {object} artifact - Artifact template.
 * @returns {Array<string>} Approval labels.
 * @collaboration Shows CEOs the workflow route before documents leave the OS.
 */
function approvalsForArtifact(artifact) {
  const text = `${artifact.category} ${artifact.title}`.toLowerCase();

  if (/privacy|data|popia|security/.test(text)) return ['Legal', 'Privacy', 'Security'];
  if (/invoice|tax|credit|payment|finance/.test(text)) return ['Finance', 'Director'];
  if (/employment|hr|disciplinary|employee/.test(text)) return ['HR', 'Legal'];
  if (/board|shareholder|governance/.test(text)) return ['Board', 'Director'];
  return ['Owner', 'Legal'];
}

/**
 * @function clausePackForArtifact
 * @description Resolves the clause pack label for artifact storytelling.
 * @param {object} artifact - Artifact template.
 * @returns {string} Clause pack label.
 * @collaboration Positions the studio as a clause-aware lifecycle engine.
 */
function clausePackForArtifact(artifact) {
  const text = `${artifact.title} ${artifact.type}`.toLowerCase();

  if (/non-disclosure|nda/.test(text)) return 'NDA Enterprise v1';
  if (/service|msa|master/.test(text)) return 'Commercial Services v1';
  if (/data|privacy|popia/.test(text)) return 'Privacy & POPIA v1';
  if (/invoice|tax|credit|payment/.test(text)) return 'Finance Controls v1';
  if (/employment|hr/.test(text)) return 'People Operations v1';

  return 'Wilsy Standard v1';
}

/**
 * @function createArtifactPayload
 * @description Creates the common artifact payload sent to exports.
 * @param {object} template - Selected artifact template.
 * @param {string} tenantId - Tenant identifier.
 * @param {object} tenantConfig - Tenant configuration.
 * @returns {object} Artifact payload.
 * @collaboration Keeps all export formats aligned to the same OS context.
 */
function createArtifactPayload(template, tenantId, tenantConfig = {}) {
  return {
    title: template.title,
    type: normalizeArtifactType(template.type || template.id),
    tenantId,
    issuingEntity: tenantConfig?.companyName || tenantConfig?.name || 'Wilsy (Pty) Ltd',
    counterparty: 'Counterparty To Be Completed',
    sourcePosture: 'SOURCE_REPAIR_REQUIRED',
    readiness: readinessForArtifact(template),
    risk: riskForArtifact(template),
    approvals: approvalsForArtifact(template),
    clausePack: clausePackForArtifact(template)
  };
}

/**
 * @function createEnterpriseDocxBlob
 * @description Creates and validates a real Microsoft Word OpenXML DOCX artifact before download.
 * @param {object} template - Selected artifact template.
 * @param {object} payload - Artifact payload.
 * @returns {Promise<Blob>} Valid DOCX blob.
 * @collaboration Ensures Wilsy OS never downloads JSON renamed as DOCX or a corrupt Word package.
 */
async function createEnterpriseDocxBlob(template, payload) {
  const rows = [
    ['Artifact', template.title],
    ['Type', payload.type],
    ['Tenant', payload.tenantId],
    ['Issuing Entity', payload.issuingEntity],
    ['Counterparty', payload.counterparty],
    ['Readiness', payload.readiness ? `${payload.readiness}%` : 'Pending source scoring'],
    ['Risk', payload.risk || 'STANDARD'],
    ['Approvals', Array.isArray(payload.approvals) ? payload.approvals.join(', ') : 'Owner, Legal'],
    ['Clause Pack', payload.clausePack || 'Wilsy Standard v1'],
    ['Signature Route', 'Wilsy Sign / DocuSign-ready handoff'],
    ['Source Posture', payload.sourcePosture || 'SOURCE_REPAIR_REQUIRED']
  ];

  const doc = new Document({
    creator: 'Wilsy OS',
    title: template.title,
    description: template.description,
    sections: [{
      properties: {},
      children: [
        new Paragraph({
          text: 'WILSY OS ARTIFACT LIFECYCLE PACK',
          heading: HeadingLevel.HEADING_1,
          alignment: AlignmentType.CENTER
        }),
        new Paragraph({
          text: template.title,
          heading: HeadingLevel.TITLE,
          alignment: AlignmentType.CENTER
        }),
        new Paragraph({ text: 'Document Control', heading: HeadingLevel.HEADING_2 }),
        new Table({
          width: { size: 100, type: WidthType.PERCENTAGE },
          rows: rows.map(([label, value]) => new TableRow({
            children: [
              new TableCell({
                width: { size: 34, type: WidthType.PERCENTAGE },
                children: [new Paragraph({ children: [new TextRun({ text: label, bold: true })] })]
              }),
              new TableCell({
                width: { size: 66, type: WidthType.PERCENTAGE },
                children: [new Paragraph(String(value || 'To Be Completed'))]
              })
            ]
          }))
        }),
        new Paragraph({ text: 'Lifecycle Route', heading: HeadingLevel.HEADING_2 }),
        new Paragraph('Draft → Review → Approve → Send → Sign → Vault'),
        new Paragraph({ text: 'Signature Route', heading: HeadingLevel.HEADING_2 }),
        new Paragraph('This artifact is prepared for a Wilsy Sign / DocuSign-style signing handoff. Production signing requires provider credentials, recipient routing, signature tags, webhooks, audit events and vault storage.'),
        new Paragraph({ text: 'Enterprise Review Standard', heading: HeadingLevel.HEADING_2 }),
        new Paragraph('This artifact must be reviewed, approved, routed, sent, signed where applicable, vaulted and retained with the Wilsy OS proof trail before external reliance.'),
        new Paragraph({ text: 'Artifact Purpose', heading: HeadingLevel.HEADING_2 }),
        new Paragraph(template.description || 'Enterprise artifact generated by Wilsy OS.')
      ]
    }]
  });

  const blob = typeof Packer.toBlob === 'function'
    ? await Packer.toBlob(doc)
    : new Blob([await Packer.toArrayBuffer(doc)], {
      type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    });

  const signature = Array.from(new Uint8Array(await blob.slice(0, 4).arrayBuffer())).join(',');

  if (signature !== '80,75,3,4') {
    throw new Error('DOCX integrity failed: generated file is not an OpenXML ZIP package.');
  }

  return new Blob([await blob.arrayBuffer()], {
    type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
  });
}



/**
 * @function createJsonBlob
 * @description Creates a system audit JSON export.
 * @param {object} template - Selected artifact template.
 * @param {object} payload - Artifact payload.
 * @returns {Blob} JSON blob.
 * @collaboration Gives each artifact a machine-readable operating record.
 */
function createJsonBlob(template, payload) {
  return new Blob([JSON.stringify({ template, payload, generatedAt: new Date().toISOString() }, null, 2)], {
    type: 'application/json'
  });
}

/**
 * @function createEmailPackageBlob
 * @description Creates an EML email package with the generated PDF attached.
 * @param {object} template - Artifact template.
 * @param {object} payload - Artifact payload.
 * @param {Blob} attachmentBlob - PDF blob.
 * @param {string} attachmentFilename - PDF filename.
 * @returns {Promise<Blob>} EML package blob.
 * @collaboration Makes SEND PACK a real deliverable instead of a mailto shortcut.
 */
async function createEmailPackageBlob(template, payload, attachmentBlob, attachmentFilename) {
  const boundary = `wilsy_${Date.now()}_${Math.random().toString(16).slice(2)}`;
  const base64 = wrapBase64(await blobToBase64(attachmentBlob));

  const message = [
    'Hello,',
    '',
    `Please review the attached Wilsy OS artifact: ${template.title}.`,
    '',
    `Tenant: ${payload.tenantId}`,
    `Source Posture: ${payload.sourcePosture || 'SOURCE_REGISTRY_REQUIRED'}`,
    `Risk: ${payload.risk}`,
    `Approvals: ${payload.approvals.join(', ')}`,
    `Clause Pack: ${payload.clausePack}`,
    '',
    'Lifecycle: Draft → Review → Approve → Send → Sign → Vault',
    '',
    'Regards,',
    'Wilsy OS'
  ].join('\r\n');

  const eml = [
    `Subject: Wilsy OS Artifact: ${template.title}`,
    'To: ',
    'Cc: ',
    'MIME-Version: 1.0',
    `Content-Type: multipart/mixed; boundary="${boundary}"`,
    '',
    `--${boundary}`,
    'Content-Type: text/plain; charset="UTF-8"',
    'Content-Transfer-Encoding: 7bit',
    '',
    message,
    '',
    `--${boundary}`,
    `Content-Type: application/pdf; name="${attachmentFilename}"`,
    'Content-Transfer-Encoding: base64',
    `Content-Disposition: attachment; filename="${attachmentFilename}"`,
    '',
    base64,
    '',
    `--${boundary}--`,
    ''
  ].join('\r\n');

  return new Blob([eml], { type: 'message/rfc822' });
}


const WORKFLOW_FORMATS = [
  { format: 'PDF', label: 'Boardroom PDF' },
  { format: 'DOCX', label: 'Editable DOCX' },
  { format: 'EMAIL', label: 'Send Room' },
  { format: 'JSON', label: 'Audit JSON' }
];

const COCKPIT_GROUP_ORDER = [
  'NDA & Confidentiality',
  'Services & Commercial',
  'SaaS & Subscription',
  'Privacy & Data',
  'Governance & Compliance',
  'Finance & Procurement',
  'People & Operations',
  'Project Delivery',
  'Security & IT',
  'Other Legal Artifacts'
];

/**
 * @function groupArtifactForCockpit
 * @description Places artifacts into executive legal cockpit groups.
 * @param {object} artifact - Artifact template.
 * @returns {string} Cockpit group.
 * @collaboration Converts a noisy template grid into investor-grade legal artifact groupings.
 */
function groupArtifactForCockpit(artifact = {}) {
  const id = `${artifact.id || ''} ${artifact.type || ''} ${artifact.title || ''} ${artifact.category || ''}`.toLowerCase();

  if (id.includes('nda') || id.includes('non-disclosure') || id.includes('confidentiality')) return 'NDA & Confidentiality';
  if (id.includes('master-services') || id.includes('statement-of-work') || id.includes('service agreement') || id.includes('terms-of-service')) return 'Services & Commercial';
  if (id.includes('saas') || id.includes('subscription') || id.includes('service-level')) return 'SaaS & Subscription';
  if (id.includes('privacy') || id.includes('popia') || id.includes('paia') || id.includes('data-processing') || id.includes('cookie')) return 'Privacy & Data';
  if (id.includes('board') || id.includes('governance') || id.includes('resolution') || id.includes('risk-register') || id.includes('compliance') || id.includes('audit')) return 'Governance & Compliance';
  if (id.includes('invoice') || id.includes('quotation') || id.includes('purchase') || id.includes('supplier') || id.includes('vendor') || id.includes('rfp') || id.includes('finance')) return 'Finance & Procurement';
  if (id.includes('employment') || id.includes('hr') || id.includes('employee') || id.includes('contractor') || id.includes('leave') || id.includes('disciplinary')) return 'People & Operations';
  if (id.includes('project') || id.includes('evm') || id.includes('variation') || id.includes('payment-certificate') || id.includes('site-instruction')) return 'Project Delivery';
  if (id.includes('security') || id.includes('access') || id.includes('backup') || id.includes('vulnerability') || id.includes('change-advisory')) return 'Security & IT';

  return 'Other Legal Artifacts';
}

/**
 * @function extractSourceRegistryFindings
 * @description Extracts actionable Source Registry findings from backend verification payloads without assuming one rigid response shape.
 * @param {object|null} payload - Source Registry payload.
 * @returns {Array<object>} Normalized findings.
 * @collaboration Converts backend verification pain into an operator repair plan.
 */
function extractSourceRegistryFindings(payload) {
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
    data.missing
  ];

  const rows = [];

  /**
   * @function pushRow
   * @description Normalizes one backend Source Registry finding into a cockpit repair-card row.
   * @param {object} item - Raw finding candidate from a verification payload.
   * @param {string} fallbackStatus - Status used when the finding does not expose one.
   * @returns {void}
   * @collaboration Converts backend evidence failures into operator-visible repair intelligence without fabricating VERIFIED status.
   */
  function pushRow(item = {}, fallbackStatus = '') {
    const status = String(
      item.status ||
      item.evidenceStatus ||
      item.sourceStatus ||
      item.result ||
      fallbackStatus ||
      'UNKNOWN'
    ).toUpperCase();

    if (!['MISSING', 'ERROR', 'BLOCKED', 'PENDING', 'NOT_EVALUATED', 'UNKNOWN'].includes(status)) return;

    rows.push(enrichSourceRegistryFinding({
      id: item.id || item.artifactId || item.type || item.connector || item.sourceId || `SRC-${rows.length + 1}`,
      title: item.title || item.artifactTitle || item.name || item.label || item.type || item.connector || 'Source requirement',
      connector: item.connector || item.requiredConnector || item.source || item.system || item.module || 'Source Registry',
      status,
      message:
        item.message ||
        item.reason ||
        item.error ||
        item.detail ||
        item.evidenceStatus ||
        'Live evidence required before VERIFIED status.',
      method: item.method || item.requiredMethod || item.check || item.field || ''
    }));
  }

  candidates.forEach((candidate) => {
    if (Array.isArray(candidate)) {
      candidate.forEach((item) => pushRow(item));
    } else if (candidate && typeof candidate === 'object') {
      Object.entries(candidate).forEach(([key, value]) => {
        if (Array.isArray(value)) {
          value.forEach((item) => pushRow({ id: key, ...item }));
        } else if (value && typeof value === 'object') {
          pushRow({ id: key, ...value });
        } else {
          pushRow({ id: key, title: key, message: String(value) });
        }
      });
    }
  });

  return rows.slice(0, 18);
}

/**
 * @function BusinessArtifactStudio
 * @description Renders the Wilsy OS artifact lifecycle console with category intelligence, readiness, approvals and export actions.
 * @param {object} props - Component props.
 * @returns {JSX.Element|null} Lifecycle console.
 * @collaboration Connects ExecutiveDashboard artifact actions to a production-grade Wilsy OS documentation engine.
 */
function BusinessArtifactStudio({ tenantConfig = {}, tenantId: tenantIdProp = '' }) {
  const tenantId = tenantIdProp || tenantConfig?.tenantId || tenantConfig?.id || 'MASTER';
  const catalog = useMemo(() => normaliseCatalog(BUSINESS_ARTIFACT_CATALOG), []);
  const categories = useMemo(() => ['All', ...Array.from(new Set(catalog.map((item) => item.category)))], [catalog]);

  const [isOpen, setIsOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [activeCategory, setActiveCategory] = useState('All');
  const [activeFormatById, setActiveFormatById] = useState({});
  const [isGeneratingId, setIsGeneratingId] = useState('');
  const [statusMessage, setStatusMessage] = useState('');
  const [sourceRegistryPayload, setSourceRegistryPayload] = useState(null);
  const [sourceRegistryVerification, setSourceRegistryVerification] = useState(null);
  const [sourceRegistryLoading, setSourceRegistryLoading] = useState(false);
  const [sourceRegistryAction, setSourceRegistryAction] = useState('');
  const [sourceRepairConnectorFilter, setSourceRepairConnectorFilter] = useState('ALL');
  const [sourceRepairStatusFilter, setSourceRepairStatusFilter] = useState('ALL');
  const [sourceBreakdownOpen, setSourceBreakdownOpen] = useState(true);
  const [sourceRepairExportFormat, setSourceRepairExportFormat] = useState('PDF');
  const [lastArtifact, setLastArtifact] = useState(null);
  const [workflowFormat, setWorkflowFormat] = useState('PDF');
  const [openGroups, setOpenGroups] = useState(() => ({
    'NDA & Confidentiality': true,
    'Services & Commercial': true,
    'SaaS & Subscription': true
  }));

  const filteredCatalog = useMemo(() => {
    const query = searchTerm.trim().toLowerCase();

    return catalog.filter((item) => {
      const categoryMatch = activeCategory === 'All' || item.category === activeCategory;
      const queryMatch = !query || `${item.title} ${item.type} ${item.category} ${item.description}`.toLowerCase().includes(query);
      return categoryMatch && queryMatch;
    });
  }, [catalog, activeCategory, searchTerm]);

  const groupedCatalog = useMemo(() => {
    const groups = new Map();

    filteredCatalog.forEach((artifact) => {
      const group = groupArtifactForCockpit(artifact);

      if (!groups.has(group)) {
        groups.set(group, []);
      }

      groups.get(group).push(artifact);
    });

    return COCKPIT_GROUP_ORDER
      .filter((group) => groups.has(group))
      .map((group) => ({ group, items: groups.get(group) }));
  }, [filteredCatalog]);

  const sourceRegistryFindings = useMemo(
    () => extractSourceRegistryFindings(sourceRegistryVerification || sourceRegistryPayload),
    [sourceRegistryPayload, sourceRegistryVerification]
  );

  const sourceRegistryRepairPlan = useMemo(
    () => summarizeSourceEvidenceRepairPlan(sourceRegistryFindings),
    [sourceRegistryFindings]
  );

  const sourceRepairConnectorOptions = useMemo(
    () => ['ALL', ...Object.keys(sourceRegistryRepairPlan.byConnector || {})],
    [sourceRegistryRepairPlan]
  );

  const sourceRepairStatusOptions = useMemo(
    () => ['ALL', ...Object.keys(sourceRegistryRepairPlan.byStatus || {})],
    [sourceRegistryRepairPlan]
  );

  const visibleSourceRegistryFindings = useMemo(
    () => sourceRegistryFindings.filter((finding) => {
      const connectorMatch = sourceRepairConnectorFilter === 'ALL' || finding.connector === sourceRepairConnectorFilter;
      const statusMatch = sourceRepairStatusFilter === 'ALL' || finding.status === sourceRepairStatusFilter;
      return connectorMatch && statusMatch;
    }),
    [sourceRegistryFindings, sourceRepairConnectorFilter, sourceRepairStatusFilter]
  );

  const sourceRegistry = useMemo(() => {
    const backendSummary = summarizeSourceRegistry(sourceRegistryPayload);

    if (sourceRegistryPayload) {
      const actionRequired =
        Number(backendSummary.pending || 0) +
        Number(backendSummary.missing || 0) +
        Number(backendSummary.error || 0) +
        Number(backendSummary.blocked || 0);

      return {
        ...backendSummary,
        backendLinked: true,
        required: actionRequired,
        total: backendSummary.total || filteredCatalog.length,
        tone: statusTone(backendSummary.status)
      };
    }

    const verified = filteredCatalog.filter((artifact) => sourceStatusForArtifact(artifact).tone === 'verified').length;

    return {
      status: 'NOT_EVALUATED',
      evidenceStatus: 'NOT_EVALUATED',
      verified,
      pending: 0,
      missing: 0,
      error: 0,
      blocked: 0,
      required: filteredCatalog.length - verified,
      total: filteredCatalog.length,
      backendLinked: false,
      tone: verified === filteredCatalog.length && filteredCatalog.length > 0 ? 'verified' : 'required'
    };
  }, [filteredCatalog, sourceRegistryPayload]);

  useEffect(() => {
    /**
     * @function handleArtifactRequest
     * @description Opens the artifact lifecycle console from dashboard custom events.
     * @param {CustomEvent} event - Artifact request event.
     * @returns {void}
     * @collaboration Keeps ExecutiveDashboard launch commands connected without a permanent floating button.
     */
    function handleArtifactRequest(event = {}) {
      const detail = event.detail || {};
      const requestedType = normalizeArtifactType(detail.type || detail.id || '');
      const selected = catalog.find((item) => normalizeArtifactType(item.type) === requestedType || normalizeArtifactType(item.id) === requestedType);

      if (selected) {
        setSearchTerm(selected.title);
        setActiveCategory(selected.category);
      }

      if (detail.openCatalog) {
        setSearchTerm('');
        setActiveCategory('All');
      }

      setIsOpen(true);
    }

    ARTIFACT_REQUEST_EVENTS.forEach((eventName) => window.addEventListener(eventName, handleArtifactRequest));

    window.openBusinessArtifacts = () => setIsOpen(true);
    window.openBusinessArtifactStudio = window.openBusinessArtifacts;

    /**
     * @function handleBusinessArtifactLauncherClick
     * @description Opens the artifact lifecycle console when legacy dashboard artifact buttons are clicked.
     * @param {MouseEvent} event - Browser click event.
     * @returns {void}
     * @collaboration Keeps ExecutiveDashboard command buttons connected after removing the permanent floating launcher.
     */
    function handleBusinessArtifactLauncherClick(event) {
      const targetNode = event.target?.closest?.('button, a, [role="button"], [data-action], [data-artifact], [aria-label]');

      if (!targetNode) return;

      const visibleText = String(targetNode.textContent || '').toLowerCase();
      const ariaLabel = String(targetNode.getAttribute('aria-label') || '').toLowerCase();
      const dataAction = String(targetNode.getAttribute('data-action') || '').toLowerCase();
      const dataArtifact = String(targetNode.getAttribute('data-artifact') || '').toLowerCase();
      const combined = `${visibleText} ${ariaLabel} ${dataAction} ${dataArtifact}`;

      if (
        combined.includes('business artifacts')
        || combined.includes('business artifact')
        || combined.includes('artifact generator')
        || combined.includes('artifact studio')
        || combined.includes('board pack')
        || combined.includes('document vault')
        || combined.includes('nda')
        || combined.includes('invoice')
      ) {
        event.preventDefault();
        setIsOpen(true);
      }
    }

    document.addEventListener('click', handleBusinessArtifactLauncherClick, true);

    return () => {
      ARTIFACT_REQUEST_EVENTS.forEach((eventName) => window.removeEventListener(eventName, handleArtifactRequest));

      document.removeEventListener('click', handleBusinessArtifactLauncherClick, true);

      if (window.openBusinessArtifacts) delete window.openBusinessArtifacts;
      if (window.openBusinessArtifactStudio) delete window.openBusinessArtifactStudio;
    };
  }, [catalog]);

  useEffect(() => {
    if (!isOpen) return;

    let cancelled = false;

    setSourceRegistryLoading(true);
    setSourceRegistryAction('status');

    getSourceRegistryStatus({ tenantId })
      .then((payload) => {
        if (!cancelled) {
          setSourceRegistryPayload(payload);
        }
      })
      .catch((error) => {
        if (!cancelled) {
          setStatusMessage(`Source Registry status unavailable: ${error.message}`);
        }
      })
      .finally(() => {
        if (!cancelled) {
          setSourceRegistryLoading(false);
          setSourceRegistryAction('');
        }
      });

    return () => {
      cancelled = true;
    };
  }, [isOpen, tenantId]);

  /**
   * @function buildSourceRegistryArtifacts
   * @description Builds the artifact evidence payload sent to the backend Source Registry.
   * @returns {Array<object>} Source Registry artifact payload.
   * @collaboration Links every visible cockpit artifact to live connector verification without inventing readiness.
   */
  function buildSourceRegistryArtifacts() {
    return filteredCatalog.map((artifact) => ({
      id: artifact.id,
      type: artifact.type,
      title: artifact.title,
      category: artifact.category,
      description: artifact.description,
      tenantId,
      sourcePosture: artifact.sourcePosture || 'SOURCE_REGISTRY_REQUIRED',
      sourceFields: artifact.sourceFields || [],
      serviceName: artifact.serviceName,
      repository: artifact.repository,
      employeeId: artifact.employeeId,
      contractId: artifact.contractId,
      agreementId: artifact.agreementId,
      invoiceId: artifact.invoiceId,
      customerId: artifact.customerId
    }));
  }

  /**
   * @function handleVerifySources
   * @description Runs live Source Registry verification through the backend.
   * @returns {Promise<void>} Completion promise.
   * @collaboration Replaces placeholder source text with real connector evidence state.
   */
  async function handleVerifySources() {
    setSourceRegistryLoading(true);
    setSourceRegistryAction('verify');
    setStatusMessage('Verifying source registry against live connector evidence...');

    try {
      const payload = await verifySourceRegistry({
        artifacts: buildSourceRegistryArtifacts(),
        tenantId
      });

      setSourceRegistryPayload(payload);
      setSourceRegistryVerification(payload?.data || payload);

      const summary = summarizeSourceRegistry(payload);
      setStatusMessage(buildSourceRegistryVerificationMessage(summary));
      setSourceBreakdownOpen(true);
    } catch (error) {
      setStatusMessage(`Source Registry verification failed: ${error.message}`);
    } finally {
      setSourceRegistryLoading(false);
      setSourceRegistryAction('');
    }
  }

  /**
   * @function handleSealBoardroomProof
   * @description Requests boardroom proof sealing from verified Source Registry evidence.
   * @returns {Promise<void>} Completion promise.
   * @collaboration Prevents boardroom proof claims unless backend verification permits sealing.
   */
  async function handleSealBoardroomProof() {
    setSourceRegistryLoading(true);
    setSourceRegistryAction('seal');
    setStatusMessage('Preparing boardroom proof seal from Source Registry evidence...');

    try {
      let verification = sourceRegistryVerification;

      if (!verification) {
        const verificationPayload = await verifySourceRegistry({
          artifacts: buildSourceRegistryArtifacts(),
          tenantId
        });

        setSourceRegistryPayload(verificationPayload);
        verification = verificationPayload?.data || verificationPayload;
        setSourceRegistryVerification(verification);
      }

      const sealPayload = await sealBoardroomProof({
        verification,
        tenantId
      });

      const sealStatus = sealPayload?.data?.status || 'BLOCKED';
      setStatusMessage(
        sealPayload?.success
          ? `Boardroom proof seal ready: ${sealStatus}.`
          : `Boardroom proof blocked: ${sealStatus}. Live connector evidence must be VERIFIED before external reliance.`
      );
    } catch (error) {
      setStatusMessage(`Boardroom proof seal failed: ${error.message}`);
    } finally {
      setSourceRegistryLoading(false);
      setSourceRegistryAction('');
    }
  }

  /**
   * @function handleExportInvestorPack
   * @description Builds an investor-pack payload from Source Registry evidence.
   * @returns {Promise<void>} Completion promise.
   * @collaboration Keeps investor packs evidence-backed instead of presentation-only.
   */
  async function handleExportInvestorPack() {
    setSourceRegistryLoading(true);
    setSourceRegistryAction('investor-pack');
    setStatusMessage('Building investor pack from Source Registry evidence...');

    try {
      let verification = sourceRegistryVerification;

      if (!verification) {
        const verificationPayload = await verifySourceRegistry({
          artifacts: buildSourceRegistryArtifacts(),
          tenantId
        });

        setSourceRegistryPayload(verificationPayload);
        verification = verificationPayload?.data || verificationPayload;
        setSourceRegistryVerification(verification);
      }

      const investorPackPayload = await buildInvestorPack({
        verification,
        tenantId
      });

      const packStatus = investorPackPayload?.data?.status || 'BLOCKED';
      setStatusMessage(
        investorPackPayload?.success
          ? `Investor pack ready: ${packStatus}.`
          : `Investor pack blocked: ${packStatus}. Verified sources and boardroom seal are required before export.`
      );
    } catch (error) {
      setStatusMessage(`Investor pack export failed: ${error.message}`);
    } finally {
      setSourceRegistryLoading(false);
      setSourceRegistryAction('');
    }
  }



  /**
   * @function escapeRepairPlanHtml
   * @description Escapes repair-plan values before rendering the operator PDF window.
   * @param {*} value - Raw value.
   * @returns {string} Escaped HTML text.
   * @collaboration Prevents connector/evidence text from breaking the repair-plan PDF export.
   */
  function escapeRepairPlanHtml(value = '') {
    return String(value ?? '')
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  /**
   * @function buildSourceRepairPlanPdfHtml
   * @description Builds the printable boardroom-style PDF HTML for the current visible repair plan.
   * @param {object} payload - Repair-plan payload.
   * @returns {string} Printable HTML document.
   * @collaboration Gives operators a human-readable PDF without claiming backend-sealed evidence.
   */
  function buildSourceRepairPlanPdfHtml(payload) {
    const wilsyBrandMark = `
      <div class="wilsy-logo-seal">
        <div class="logo-aura"></div>
        <img class="brand-logo" src="${escapeRepairPlanHtml(WILSY_SOURCE_REPAIR_LOGO_URL)}" alt="Wilsy OS logo" />
        <div class="logo-ring"></div>
      </div>
    `;

    const wilsyWatermark = `
      <img class="brand-watermark" src="${escapeRepairPlanHtml(WILSY_SOURCE_REPAIR_LOGO_URL)}" alt="" />
    `;

const generated = new Date(payload.generatedAt || Date.now()).toLocaleString('en-ZA', {
      dateStyle: 'medium',
      timeStyle: 'short'
    });

    const summary = payload.summary || {};
    const visibleFindings = payload.visibleFindings || [];
    const connectorEntries = Object.entries(payload?.repairPlan?.byConnector || {});
    const statusEntries = Object.entries(payload?.repairPlan?.byStatus || {});
    const totalFindings = Number(payload?.repairPlan?.total || visibleFindings.length || 0);
    const criticalCount = visibleFindings.filter((finding) => String(finding.status || '').toUpperCase() === 'ERROR').length;
    const missingCount = visibleFindings.filter((finding) => String(finding.status || '').toUpperCase() === 'MISSING').length;

    const connectorCounts = connectorEntries
      .map(([connector, count]) => `
        <div class="connector-cell">
          <span>${escapeRepairPlanHtml(connector)}</span>
          <strong>${escapeRepairPlanHtml(count)}</strong>
        </div>
      `)
      .join('');

    const statusCounts = statusEntries
      .map(([status, count]) => `
        <div class="status-cell">
          <span>${escapeRepairPlanHtml(status)}</span>
          <strong>${escapeRepairPlanHtml(count)}</strong>
        </div>
      `)
      .join('');

    const evidenceMethods = Array.from(new Set(
      visibleFindings.flatMap((finding) => {
        if (Array.isArray(finding.requiredMethods)) return finding.requiredMethods;
        return String(finding.method || '')
          .split('·')
          .map((item) => item.trim())
          .filter(Boolean);
      })
    ));

    const evidenceNeeded = Array.from(new Set(
      visibleFindings.flatMap((finding) => Array.isArray(finding.evidenceNeeded) ? finding.evidenceNeeded : [])
    ));

    const methodList = evidenceMethods.slice(0, 18).map((method) => `<li>${escapeRepairPlanHtml(method)}</li>`).join('');
    const evidenceList = evidenceNeeded.slice(0, 18).map((item) => `<li>${escapeRepairPlanHtml(item)}</li>`).join('');

    const findingCards = visibleFindings
      .map((finding, index) => {
        const evidenceText = Array.isArray(finding.evidenceNeeded)
          ? finding.evidenceNeeded.slice(0, 10).join(' · ')
          : (finding.evidenceNeeded || '');

        const actionText = finding.operatorAction
          || (Array.isArray(finding.actions) ? finding.actions.join(' ') : (finding.actions || ''));

        const status = String(finding.status || 'PENDING').toUpperCase();

        return `
          <section class="finding-card">
            <div class="finding-index">${String(index + 1).padStart(2, '0')}</div>

            <div class="finding-body">
              <div class="finding-meta">
                <span class="badge ${escapeRepairPlanHtml(status.toLowerCase())}">${escapeRepairPlanHtml(status)}</span>
                <span class="connector-badge">${escapeRepairPlanHtml(finding.connector || 'SOURCE REGISTRY')}</span>
              </div>

              <h3>${escapeRepairPlanHtml(finding.title || 'Untitled evidence finding')}</h3>

              ${finding.sourceFamily ? `<div class="family">${escapeRepairPlanHtml(finding.sourceFamily)}</div>` : ''}

              ${finding.method ? `<div class="method">${escapeRepairPlanHtml(finding.method)}</div>` : ''}

              <p class="finding-message">${escapeRepairPlanHtml(finding.message || 'Live evidence required before VERIFIED status.')}</p>

              ${evidenceText ? `
                <div class="finding-block">
                  <div class="block-label">Evidence chain required</div>
                  <p>${escapeRepairPlanHtml(evidenceText)}</p>
                </div>
              ` : ''}

              ${actionText ? `
                <div class="finding-block action">
                  <div class="block-label">Operator repair command</div>
                  <p>${escapeRepairPlanHtml(actionText)}</p>
                </div>
              ` : ''}
            </div>
          </section>
        `;
      })
      .join('');

    return `<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <title>WILSY OS - Sovereign Source Registry Command Brief</title>
  <style>
    @page {
      size: A4 portrait;
      margin: 0;
    }

    * {
      box-sizing: border-box;
      -webkit-print-color-adjust: exact;
      print-color-adjust: exact;
    }

    html,
    body {
      margin: 0;
      padding: 0;
      background: #030306;
      color: #f8f1ff;
      font-family: Inter, Avenir Next, Arial, sans-serif;
    }

    body {
      counter-reset: page;
    }

    .page {
      position: relative;
      min-height: 297mm;
      padding: 18mm;
      overflow: hidden;
      background:
        radial-gradient(circle at 15% 8%, rgba(212,175,55,0.22), transparent 24%),
        radial-gradient(circle at 85% 14%, rgba(192,132,252,0.18), transparent 26%),
        linear-gradient(135deg, #050108 0%, #090512 48%, #010102 100%);
      page-break-after: always;
    }

    .page:last-child {
      page-break-after: auto;
    }

    .page::before {
      content: "";
      position: absolute;
      inset: 7mm;
      border: 1px solid rgba(212,175,55,0.28);
      border-radius: 20px;
      pointer-events: none;
    }

    .page::after {
      content: "WILSY OS";
      position: absolute;
      right: 15mm;
      bottom: 12mm;
      color: rgba(212,175,55,0.13);
      font-size: 38px;
      font-weight: 950;
      letter-spacing: 10px;
    }

    .topbar {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      margin-bottom: 18px;
      position: relative;
      z-index: 2;
    }

    .brand {
      display: flex;
      align-items: center;
      gap: 12px;
    }

    .monogram {
      width: 46px;
      height: 46px;
      border-radius: 14px;
      display: grid;
      place-items: center;
      color: #050505;
      font-weight: 950;
      font-size: 24px;
      background: linear-gradient(135deg, #fff2a5, #d4af37 48%, #c084fc 100%);
      box-shadow: 0 16px 36px rgba(212,175,55,0.28);
    }

    
    .logo-orb {
      position: relative;
      width: 54px;
      height: 54px;
      border-radius: 18px;
      display: grid;
      place-items: center;
      overflow: hidden;
      background:
        radial-gradient(circle at 28% 18%, rgba(255,255,255,0.45), transparent 24%),
        linear-gradient(135deg, #fff2a5 0%, #d4af37 42%, #c084fc 100%);
      border: 1px solid rgba(255,244,194,0.42);
      box-shadow:
        0 18px 46px rgba(212,175,55,0.30),
        0 0 0 6px rgba(212,175,55,0.055);
    }

    .brand-logo {
      position: relative;
      z-index: 2;
      width: 100%;
      height: 100%;
      object-fit: cover;
      display: block;
      filter: saturate(1.13) contrast(1.08);
    }

    .logo-glow {
      position: absolute;
      inset: -26%;
      z-index: 3;
      background: linear-gradient(135deg, rgba(255,255,255,0.42), transparent 38%, rgba(192,132,252,0.28));
      mix-blend-mode: screen;
      opacity: 0.30;
      pointer-events: none;
    }

    .brand-watermark {
      position: absolute;
      z-index: 1;
      right: 13mm;
      top: 24mm;
      width: 86mm;
      max-height: 86mm;
      object-fit: contain;
      opacity: 0.050;
      filter: grayscale(1) sepia(1) hue-rotate(340deg) saturate(1.8) contrast(1.1);
      pointer-events: none;
    }

.brand-title {
      display: grid;
      gap: 3px;
    }

    .brand-title strong {
      color: #fff7dc;
      font-size: 13px;
      letter-spacing: 2.6px;
      text-transform: uppercase;
    }

    .brand-title span,
    .classification {
      color: #bda56b;
      font-size: 9.5px;
      letter-spacing: 1.8px;
      text-transform: uppercase;
      font-weight: 900;
    }

    .classification {
      border: 1px solid rgba(212,175,55,0.35);
      border-radius: 999px;
      padding: 8px 12px;
      background: rgba(0,0,0,0.24);
    }

    .hero {
      position: relative;
      z-index: 2;
      margin-top: 20mm;
      max-width: 170mm;
    }

    .eyebrow {
      color: #d4af37;
      font-size: 10px;
      font-weight: 950;
      letter-spacing: 3px;
      text-transform: uppercase;
      margin-bottom: 12px;
    }

    h1 {
      margin: 0;
      font-size: 48px;
      line-height: 0.95;
      letter-spacing: -1.6px;
      color: #fff7fb;
    }

    .hero-subtitle {
      margin-top: 18px;
      max-width: 132mm;
      color: #d9ccec;
      font-size: 15px;
      line-height: 1.55;
    }

    .truth-band {
      display: grid;
      grid-template-columns: 1.1fr 0.9fr 0.9fr;
      gap: 12px;
      margin-top: 26px;
    }

    .truth-card {
      border: 1px solid rgba(212,175,55,0.26);
      border-radius: 18px;
      padding: 14px;
      background: linear-gradient(180deg, rgba(255,255,255,0.055), rgba(255,255,255,0.018));
      min-height: 78px;
    }

    .truth-card span {
      display: block;
      color: #bda56b;
      font-size: 9px;
      font-weight: 950;
      letter-spacing: 1.8px;
      text-transform: uppercase;
      margin-bottom: 8px;
    }

    .truth-card strong {
      display: block;
      color: #fff7dc;
      font-size: 22px;
      font-weight: 950;
      line-height: 1.1;
    }

    .metrics {
      display: grid;
      grid-template-columns: repeat(6, 1fr);
      gap: 10px;
      margin-top: 20px;
    }

    .metric {
      border: 1px solid rgba(212,175,55,0.22);
      border-radius: 16px;
      padding: 12px;
      background: rgba(0,0,0,0.25);
      min-height: 76px;
    }

    .metric .k {
      color: #bda56b;
      font-size: 8.5px;
      text-transform: uppercase;
      letter-spacing: 1.4px;
      font-weight: 950;
      margin-bottom: 8px;
    }

    .metric .v {
      color: #fff8e7;
      font-size: 24px;
      font-weight: 950;
    }

    .brief-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 14px;
      margin-top: 24px;
    }

    .panel {
      border: 1px solid rgba(212,175,55,0.22);
      border-radius: 18px;
      padding: 16px;
      background: rgba(7,4,13,0.82);
    }

    .panel h2 {
      color: #fff7dc;
      margin: 0 0 10px;
      font-size: 15px;
      letter-spacing: 1.5px;
      text-transform: uppercase;
    }

    .panel p,
    .panel li {
      color: #d9ccec;
      font-size: 11.5px;
      line-height: 1.55;
    }

    .panel ul {
      padding-left: 18px;
      margin: 8px 0 0;
    }

    .connector-grid,
    .status-grid {
      display: grid;
      gap: 8px;
    }

    .connector-cell,
    .status-cell {
      display: flex;
      justify-content: space-between;
      gap: 10px;
      align-items: center;
      border: 1px solid rgba(255,255,255,0.10);
      border-radius: 14px;
      padding: 9px 11px;
      background: rgba(255,255,255,0.035);
    }

    .connector-cell span,
    .status-cell span {
      color: #d5c5df;
      font-size: 11px;
      font-weight: 800;
    }

    .connector-cell strong,
    .status-cell strong {
      color: #d4af37;
      font-size: 15px;
      font-weight: 950;
    }

    .section-title {
      position: relative;
      z-index: 2;
      margin: 0 0 16px;
      color: #fff7fb;
      font-size: 29px;
      line-height: 1.1;
      letter-spacing: -0.5px;
    }

    .section-kicker {
      position: relative;
      z-index: 2;
      color: #d4af37;
      font-size: 9.5px;
      font-weight: 950;
      letter-spacing: 2.4px;
      text-transform: uppercase;
      margin-bottom: 8px;
    }

    .findings {
      position: relative;
      z-index: 2;
      display: grid;
      gap: 12px;
    }

    .finding-card {
      display: grid;
      grid-template-columns: 42px 1fr;
      gap: 12px;
      break-inside: avoid;
      border: 1px solid rgba(212,175,55,0.18);
      border-radius: 20px;
      padding: 14px;
      background:
        linear-gradient(180deg, rgba(255,255,255,0.055), rgba(255,255,255,0.018)),
        rgba(5,3,10,0.88);
      box-shadow: inset 0 1px 0 rgba(255,255,255,0.045);
    }

    .finding-index {
      width: 38px;
      height: 38px;
      border-radius: 13px;
      display: grid;
      place-items: center;
      background: linear-gradient(135deg, rgba(212,175,55,0.24), rgba(192,132,252,0.18));
      color: #fff7dc;
      font-weight: 950;
      font-size: 13px;
      border: 1px solid rgba(212,175,55,0.25);
    }

    .finding-meta {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 8px;
      margin-bottom: 8px;
    }

    .badge,
    .connector-badge {
      border-radius: 999px;
      padding: 6px 10px;
      font-size: 9px;
      font-weight: 950;
      letter-spacing: 1.2px;
      text-transform: uppercase;
    }

    .badge.error {
      color: #ffd2d2;
      border: 1px solid rgba(255,89,89,0.46);
      background: rgba(88,7,17,0.66);
    }

    .badge.missing {
      color: #ffe8a0;
      border: 1px solid rgba(212,175,55,0.42);
      background: rgba(64,45,0,0.58);
    }

    .badge.pending,
    .badge.blocked {
      color: #dfd2ff;
      border: 1px solid rgba(192,132,252,0.42);
      background: rgba(48,13,76,0.55);
    }

    .connector-badge {
      color: #d3c6a5;
      border: 1px solid rgba(255,255,255,0.12);
      background: rgba(255,255,255,0.04);
    }

    .finding-card h3 {
      margin: 0 0 6px;
      color: #ffffff;
      font-size: 16px;
      line-height: 1.25;
    }

    .family {
      color: #bda56b;
      font-size: 10px;
      font-weight: 950;
      text-transform: uppercase;
      letter-spacing: 1.5px;
      margin-bottom: 8px;
    }

    .method {
      color: #d99dff;
      font-size: 11px;
      font-weight: 900;
      line-height: 1.45;
      margin-bottom: 8px;
    }

    .finding-message {
      margin: 0 0 10px;
      color: #ded4ef;
      font-size: 11.5px;
      line-height: 1.48;
    }

    .finding-block {
      border-top: 1px solid rgba(255,255,255,0.08);
      padding-top: 9px;
      margin-top: 9px;
    }

    .block-label {
      color: #d4af37;
      font-size: 8.5px;
      font-weight: 950;
      text-transform: uppercase;
      letter-spacing: 1.6px;
      margin-bottom: 5px;
    }

    .finding-block p {
      margin: 0;
      color: #f3ebff;
      font-size: 10.8px;
      line-height: 1.48;
    }

    .footer-note {
      position: absolute;
      left: 18mm;
      right: 18mm;
      bottom: 12mm;
      color: #a790b2;
      font-size: 8.5px;
      letter-spacing: 1.2px;
      text-transform: uppercase;
      z-index: 2;
      display: flex;
      justify-content: space-between;
      gap: 12px;
    }

    @media print {
      body { background: #030306; }
      .page { min-height: 297mm; }
    }

    /* WILSY_TRUE_LOGO_EPITOME_START */
    .wilsy-logo-seal {
      position: relative;
      width: 76px;
      height: 76px;
      border-radius: 24px;
      display: grid;
      place-items: center;
      overflow: hidden;
      isolation: isolate;
      background:
        radial-gradient(circle at 18% 12%, rgba(255,255,255,0.42), transparent 24%),
        linear-gradient(135deg, rgba(255,244,183,0.98) 0%, rgba(212,175,55,0.72) 36%, rgba(192,132,252,0.44) 100%);
      border: 1px solid rgba(255,244,194,0.58);
      box-shadow:
        0 24px 62px rgba(212,175,55,0.33),
        0 0 0 8px rgba(212,175,55,0.065),
        inset 0 1px 0 rgba(255,255,255,0.36);
    }

    .wilsy-logo-seal::after {
      content: "";
      position: absolute;
      inset: 0;
      z-index: 4;
      background:
        linear-gradient(135deg, rgba(255,255,255,0.38), transparent 32%, rgba(192,132,252,0.22) 74%, rgba(212,175,55,0.20)),
        radial-gradient(circle at 70% 72%, rgba(192,132,252,0.26), transparent 28%);
      mix-blend-mode: screen;
      pointer-events: none;
    }

    .logo-aura {
      position: absolute;
      inset: -18px;
      z-index: 0;
      background:
        radial-gradient(circle, rgba(212,175,55,0.35), transparent 62%),
        radial-gradient(circle at 78% 84%, rgba(192,132,252,0.30), transparent 48%);
      filter: blur(12px);
      opacity: 0.88;
    }

    .brand-logo {
      position: relative;
      z-index: 2;
      width: calc(100% - 10px);
      height: calc(100% - 10px);
      object-fit: contain;
      display: block;
      border-radius: 19px;
      background: rgba(3,3,8,0.18);
      filter: saturate(1.16) contrast(1.08) brightness(1.02);
    }

    .logo-ring {
      position: absolute;
      inset: 5px;
      z-index: 3;
      border-radius: 20px;
      border: 1px solid rgba(255,255,255,0.28);
      box-shadow: inset 0 0 18px rgba(0,0,0,0.20);
      pointer-events: none;
    }

    .brand-watermark {
      position: absolute;
      z-index: 1;
      right: 10mm;
      top: 22mm;
      width: 104mm;
      max-height: 104mm;
      object-fit: contain;
      opacity: 0.055;
      filter:
        grayscale(1)
        sepia(1)
        hue-rotate(334deg)
        saturate(2.2)
        contrast(1.18)
        brightness(1.1);
      mix-blend-mode: screen;
      pointer-events: none;
    }

    .brand-title strong {
      color: #fff7dc;
      font-size: 14px;
      letter-spacing: 3px;
      text-transform: uppercase;
    }

    .brand-title span {
      color: #d4af37;
      font-size: 9.5px;
      letter-spacing: 2.05px;
      text-transform: uppercase;
      font-weight: 950;
    }

    .brand {
      position: relative;
    }

    .brand::after {
      content: "CONTROL MARK";
      position: absolute;
      left: 90px;
      top: 47px;
      color: rgba(212,175,55,0.38);
      font-size: 7px;
      font-weight: 950;
      letter-spacing: 2px;
      text-transform: uppercase;
    }
    /* WILSY_TRUE_LOGO_EPITOME_END */


  </style>
</head>
<body>
  <section class="page">
    ${wilsyWatermark}
    <div class="topbar">
      <div class="brand">
        ${wilsyBrandMark}
        <div class="brand-title">
          <strong>WILSY OS</strong>
          <span>Legal Sovereign Standard</span>
        </div>
      </div>
      <div class="classification">Boardroom Repair Command</div>
    </div>

    <div class="hero">
      <div class="eyebrow">Source Registry Evidence Control Plane</div>
      <h1>Sovereign Repair Plan</h1>
      <p class="hero-subtitle">
        The Wilsy OS logo is not decoration here. It is the control mark of the repair command:
        every gap is named, every connector is accountable, and no document earns VERIFIED status
        until live source evidence exists.
      </p>

      <div class="truth-band">
        <div class="truth-card">
          <span>Tenant</span>
          <strong>${escapeRepairPlanHtml(payload.tenantId || 'MASTER')}</strong>
        </div>
        <div class="truth-card">
          <span>Registry status</span>
          <strong>${escapeRepairPlanHtml(payload.status || 'PENDING')}</strong>
        </div>
        <div class="truth-card">
          <span>Truth policy</span>
          <strong>${escapeRepairPlanHtml(payload.truthPolicy || 'NO_FAKE_VERIFIED')}</strong>
        </div>
      </div>

      <div class="metrics">
        <div class="metric"><div class="k">Total</div><div class="v">${escapeRepairPlanHtml(summary.total || 0)}</div></div>
        <div class="metric"><div class="k">Verified</div><div class="v">${escapeRepairPlanHtml(summary.verified || 0)}</div></div>
        <div class="metric"><div class="k">Pending</div><div class="v">${escapeRepairPlanHtml(summary.pending || 0)}</div></div>
        <div class="metric"><div class="k">Missing</div><div class="v">${escapeRepairPlanHtml(summary.missing || 0)}</div></div>
        <div class="metric"><div class="k">Errors</div><div class="v">${escapeRepairPlanHtml(summary.error || 0)}</div></div>
        <div class="metric"><div class="k">Blocked</div><div class="v">${escapeRepairPlanHtml(summary.blocked || 0)}</div></div>
      </div>

      <div class="brief-grid">
        <div class="panel">
          <h2>Investor interpretation</h2>
          <p>
            ${escapeRepairPlanHtml(criticalCount)} critical error findings and ${escapeRepairPlanHtml(missingCount)}
            missing-evidence findings are visible in this filtered export.
            The register is not broken; it is refusing to fake institutional evidence.
          </p>
          <p>
            Next gate: connect live CRM, compliance, finance, telemetry, and people evidence until the Source Registry can produce VERIFIED outcomes.
          </p>
        </div>

        <div class="panel">
          <h2>Status distribution</h2>
          <div class="status-grid">${statusCounts || '<div class="status-cell"><span>No status counts</span><strong>0</strong></div>'}</div>
        </div>

        <div class="panel">
          <h2>Connector exposure</h2>
          <div class="connector-grid">${connectorCounts || '<div class="connector-cell"><span>No connector counts</span><strong>0</strong></div>'}</div>
        </div>

        <div class="panel">
          <h2>Evidence operating map</h2>
          <ul>${evidenceList || '<li>No evidence requirements returned.</li>'}</ul>
        </div>
      </div>
    </div>

    <div class="footer-note">
      <span>Generated ${escapeRepairPlanHtml(generated)}</span>
      <span>Wilsy OS branded operator export - unsealed until Seal Boardroom Proof confirms VERIFIED evidence.</span>
    </div>
  </section>

  <section class="page">
    ${wilsyWatermark}
    <div class="topbar">
      <div class="brand">
        ${wilsyBrandMark}
        <div class="brand-title">
          <strong>WILSY OS</strong>
          <span>Evidence Method Index</span>
        </div>
      </div>
      <div class="classification">${escapeRepairPlanHtml(totalFindings)} Repair Signals</div>
    </div>

    <div class="section-kicker">Connector method obligations</div>
    <h2 class="section-title">Methods that must resolve before institutional reliance</h2>

    <div class="brief-grid">
      <div class="panel">
        <h2>Required methods</h2>
        <ul>${methodList || '<li>No methods returned.</li>'}</ul>
      </div>

      <div class="panel">
        <h2>Board-level rule</h2>
        <p>
          A repair plan is not a boardroom seal. It is an execution map.
          VERIFIED must only appear after the connector returns live evidence with source identity, retrieval time, and audit-safe payload.
        </p>
        <p>
          This preserves the integrity posture Fortune 500 diligence expects: verifiable sources, explicit gaps, and no cosmetic readiness.
        </p>
      </div>
    </div>

    <div class="footer-note">
      <span>WILSY OS Source Registry</span>
      <span>${escapeRepairPlanHtml(payload.truthPolicy || 'NO_FAKE_VERIFIED')}</span>
    </div>
  </section>

  <section class="page">
    ${wilsyWatermark}
    <div class="topbar">
      <div class="brand">
        ${wilsyBrandMark}
        <div class="brand-title">
          <strong>WILSY OS</strong>
          <span>Repair Execution Ledger</span>
        </div>
      </div>
      <div class="classification">Filtered: ${escapeRepairPlanHtml(payload.filters?.connector || 'ALL')} / ${escapeRepairPlanHtml(payload.filters?.status || 'ALL')}</div>
    </div>

    <div class="section-kicker">Visible repair findings</div>
    <h2 class="section-title">Execution queue</h2>

    <div class="findings">${findingCards || '<div class="panel"><h2>No visible findings</h2><p>No repair findings were included in this export.</p></div>'}</div>

    <div class="footer-note">
      <span>Operator PDF export</span>
      <span>Wilsy OS branded operator export. Unsealed until VERIFIED evidence is sealed.</span>
    </div>
  </section>
</body>
</html>`;
  }

  /**
   * @function exportSourceRepairPlanJson
   * @description Exports the Source Registry repair plan as machine-readable JSON.
   * @param {object} payload - Repair-plan payload.
   * @returns {void}
   * @collaboration Preserves the system-executable repair plan for engineering and audit workflows.
   */
  function exportSourceRepairPlanJson(payload) {
    downloadBlob(
      new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' }),
      `wilsy-source-registry-repair-plan-${tenantId}-${Date.now()}.json`
    );
  }

  /**
   * @function exportSourceRepairPlanPdf
   * @description Opens a printable operator PDF version of the Source Registry repair plan.
   * @param {object} payload - Repair-plan payload.
   * @returns {void}
   * @collaboration Adds human boardroom readability without claiming cryptographic backend sealing.
   */
  function exportSourceRepairPlanPdf(payload) {
    const pdfWindow = window.open('', '_blank', 'width=1280,height=900');

    if (!pdfWindow) {
      throw new Error('Pop-up blocked. Allow pop-ups to export PDF.');
    }

    pdfWindow.document.open();
    pdfWindow.document.write(buildSourceRepairPlanPdfHtml(payload));
    pdfWindow.document.title = 'WILSY OS - Sovereign Source Registry Command Brief';
    pdfWindow.document.close();

    let printed = false;

    /**
     * @function printOnce
     * @description Prints the branded Source Registry command brief exactly once after logo assets are ready.
     * @returns {void}
     * @collaboration Prevents duplicate print dialogs while preserving the true Wilsy OS logo in the PDF export.
     */
    const printOnce = () => {
      if (printed) return;
      printed = true;
      pdfWindow.focus();
      pdfWindow.print();
    };

    const images = Array.from(pdfWindow.document.images || []);
    const pendingImages = images.filter((image) => !image.complete);

    if (!pendingImages.length) {
      window.setTimeout(printOnce, 850);
      return;
    }

    let remaining = pendingImages.length;

    pendingImages.forEach((image) => {
      /**
       * @function done
       * @description Tracks each logo image load result before releasing the print command.
       * @returns {void}
       * @collaboration Ensures the Wilsy OS brand mark and watermark are loaded before the PDF dialog opens.
       */
      const done = () => {
        remaining -= 1;

        if (remaining <= 0) {
          window.setTimeout(printOnce, 850);
        }
      };

      image.onload = done;
      image.onerror = done;
    });

    window.setTimeout(printOnce, 2400);
  }


  /**
   * @function exportSourceRepairPlan
   * @description Exports the current Source Registry repair plan as boardroom JSON.
   * @returns {void}
   * @collaboration Makes the Source Registry repair queue executable outside the browser.
   */
  function exportSourceRepairPlan() {
    const payload = {
      title: 'WILSY OS SOURCE REGISTRY REPAIR PLAN',
      tenantId,
      status: sourceRegistry.status,
      summary: {
        total: sourceRegistry.total,
        verified: sourceRegistry.verified,
        pending: sourceRegistry.pending,
        missing: sourceRegistry.missing,
        error: sourceRegistry.error,
        blocked: sourceRegistry.blocked
      },
      filters: {
        connector: sourceRepairConnectorFilter,
        status: sourceRepairStatusFilter
      },
      repairPlan: sourceRegistryRepairPlan,
      visibleFindings: visibleSourceRegistryFindings,
      truthPolicy: 'NO_FAKE_VERIFIED',
      generatedAt: new Date().toISOString()
    };

    try {
      if (sourceRepairExportFormat === 'PDF') {
        exportSourceRepairPlanPdf(payload);
      } else {
        exportSourceRepairPlanJson(payload);
      }

      setStatusMessage(
        `Source Registry repair plan exported as ${sourceRepairExportFormat}: ${visibleSourceRegistryFindings.length} visible findings.`
      );
    } catch (error) {
      setStatusMessage(`Source Registry repair plan export failed: ${error.message}`);
    }
  }

  /**
   * @function setFormat
   * @description Sets an artifact export format.
   * @param {object} artifact - Artifact template.
   * @param {string} format - Export format.
   * @returns {void}
   * @collaboration Moves exports behind lifecycle cards instead of making export buttons the product.
   */
  function setFormat(artifact, format) {
    setActiveFormatById((current) => ({ ...current, [artifact.id]: format }));
  }

  /**
   * @function generatePdf
   * @description Generates a branded backend PDF for an artifact.
   * @param {object} artifact - Artifact template.
   * @param {object} payload - Artifact payload.
   * @returns {Promise<Blob>} PDF blob.
   * @collaboration Preserves the Wilsy OS proof-sealed backend renderer path.
   */
  async function generatePdf(artifact, payload) {
    const artifactType = normalizeArtifactType(artifact.type || artifact.id);
    const timestamp = new Date().toISOString();
    const nonce = window.crypto.randomUUID();
    const requestProof = await createCanonicalArtifactProof(artifactType, tenantId, timestamp);
    const token = getBrowserToken();

    const response = await fetchArtifactWithTimeout(resolveArtifactApiUrl('/api/generate/pdf'), {
      method: 'POST',
      headers: {
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
        'Content-Type': 'application/json',
        'X-Tenant-ID': tenantId,
        'X-Artifact-Type': artifactType,
        'X-Request-Proof': requestProof,
        'X-Artifact-Proof': requestProof,
        'X-Forensic-Timestamp': timestamp,
        'X-Artifact-Timestamp': timestamp,
        'X-Cryptographic-Nonce': nonce
      },
      body: JSON.stringify({
        type: artifactType,
        tenantId,
        timestamp,
        requestProof,
        nonce,
        metadata: { type: artifactType, tenantId, timestamp, requestProof, nonce },
        data: payload
      })
    });

    if (!response.ok) {
      throw new Error(`Artifact endpoint failed ${response.status}: ${await readArtifactError(response)}`);
    }

    return response.blob();
  }

  /**
   * @function generateArtifact
   * @description Generates the selected artifact through the centralized Wilsy OS artifact export service.
   * @param {object} artifact - Artifact template.
   * @returns {Promise<void>} Completion promise.
   * @collaboration Separates production export behavior from UI card rendering.
   */
  async function generateArtifact(artifact) {
    const format = workflowFormat || 'PDF';

    setIsGeneratingId(`${artifact.id}:${format}`);
    setStatusMessage(`Preparing ${artifact.title} as ${format} through Wilsy OS export service...`);

    try {
      const receipt = await generateArtifactExport({
        artifact,
        format,
        tenantId,
        tenantConfig
      });

      setLastArtifact({ ...receipt, artifactId: artifact.id });
      setStatusMessage(`${artifact.title} generated as ${receipt.format}.`);
    } catch (error) {
      setStatusMessage(`Generation failed: ${error.message}`);
    } finally {
      setIsGeneratingId('');
    }
  }
  


  if (!isOpen) {
    return null;
  }

  return (
    <div style={styles.overlay} role="dialog" aria-modal="true" aria-label="Wilsy OS Wilsy OS Legal Artifact Cockpit">
      <style>{`
        @keyframes wilsyReceiptMarquee {
          0% { transform: translateX(0); }
          14% { transform: translateX(0); }
          100% { transform: translateX(-50%); }
        }
      `}</style>
      <section style={styles.panel}>
        <header style={styles.header}>
          <div>
            <div style={styles.eyebrow}>WILSY OS AGREEMENT INTELLIGENCE</div>
            <h2 style={styles.title}>Artifact Lifecycle Console</h2>
            <p style={styles.subtitle}>
              Generate, review, approve, send, sign, vault and audit every business document across the operating system.
            </p>
          </div>

          <button type="button" style={styles.closeButton} onClick={() => setIsOpen(false)}>
            CLOSE
          </button>
        </header>

        <div style={styles.commandBar}>
          <input
            value={searchTerm}
            onChange={(event) => setSearchTerm(event.target.value)}
            placeholder="Search NDA, board pack, compliance, invoice, employee, supplier, privacy..."
            style={styles.search}
          />
        </div>

        <div style={styles.categoryRail}>
          {categories.map((category) => (
            <button
              key={category}
              type="button"
              style={category === activeCategory ? styles.categoryActive : styles.categoryButton}
              onClick={() => setActiveCategory(category)}
            >
              {category}
            </button>
          ))}
        </div>

        <div style={styles.executiveStrip}>
          <div style={styles.executiveMetric}>
            <span style={styles.metricLabel}>Templates</span>
            <strong style={styles.metricValue}>{catalog.length}</strong>
          </div>
          <div style={styles.executiveMetric}>
            <span style={styles.metricLabel}>Lifecycle</span>
            <strong style={styles.metricValue}>6 stages</strong>
          </div>
          <div style={styles.executiveMetric}>
            <span style={styles.metricLabel}>Source Registry</span>
            <strong style={sourceRegistry.required ? styles.metricWarning : styles.metricSuccess}>
              {sourceRegistry.required ? `${sourceRegistry.required} required` : 'Verified'}
            </strong>
          </div>
          <div style={{ ...styles.executiveMetric, ...styles.lastArtifactMetric }}>
            <span style={styles.metricLabel}>Last Artifact</span>
            <div style={styles.receiptTicker} title={formatArtifactReceipt(lastArtifact)}>
              <div style={styles.receiptMarqueeTrack}>
                <span style={styles.receiptMarqueeItem}>{formatArtifactReceipt(lastArtifact)}</span>
                <span style={styles.receiptMarqueeItem} aria-hidden="true">{formatArtifactReceipt(lastArtifact)}</span>
              </div>
            </div>
          </div>
        </div>

        <div style={sourceRegistry.required ? styles.sourceRegistryAlert : styles.sourceRegistryVerified}>
          <strong>{buildSourceRegistryCommandLabel(sourceRegistry)}</strong>
          <span>{buildSourceRegistryCommandDetail(sourceRegistry, filteredCatalog.length)}</span>
        </div>

        {statusMessage ? <div style={styles.message}>{statusMessage}</div> : null}

        {sourceRegistryFindings.length ? (
          <div style={styles.sourceBreakdownPanel}>
            <div style={styles.sourceBreakdownHeader}>
              <div>
                <strong style={styles.sourceBreakdownTitle}>Evidence Breakdown</strong>
                <span style={styles.sourceBreakdownSubtitle}>Live repair queue for connector-backed verification</span>
              </div>
              <div style={styles.sourceBreakdownHeaderActions}>
                <span style={styles.sourceBreakdownCount}>
                  {sourceBreakdownOpen ? `${sourceRegistryFindings.length} repair signals shown` : 'Repair queue hidden'}
                </span>
                <button
                  type="button"
                  style={styles.sourceBreakdownToggleButton}
                  onClick={() => setSourceBreakdownOpen((current) => !current)}
                >
                  {sourceBreakdownOpen ? 'Hide Queue' : 'Show Queue'}
                </button>
              </div>
            </div>

            {!sourceBreakdownOpen ? (
              <div style={styles.sourceBreakdownCollapsedNotice}>
                Evidence Breakdown is hidden. Live repair state is still active and can be restored without re-running verification.
              </div>
            ) : null}

            {Object.keys(sourceRegistryRepairPlan.byConnector || {}).length ? (
              <div style={sourceBreakdownOpen ? styles.sourceRepairSummaryRail : styles.hidden}>
                {Object.entries(sourceRegistryRepairPlan.byConnector).map(([connector, count]) => (
                  <button
                    key={connector}
                    type="button"
                    style={sourceRepairConnectorFilter === connector ? styles.sourceRepairSummaryPillActive : styles.sourceRepairSummaryPill}
                    onClick={() => setSourceRepairConnectorFilter(sourceRepairConnectorFilter === connector ? 'ALL' : connector)}
                  >
                    {connector}: {count}
                  </button>
                ))}
              </div>
            ) : null}

            {sourceRegistryFindings.length ? (
              <div style={sourceBreakdownOpen ? styles.sourceRepairControlRail : styles.hidden}>
                <select
                  value={sourceRepairConnectorFilter}
                  onChange={(event) => setSourceRepairConnectorFilter(event.target.value)}
                  style={styles.sourceRepairSelect}
                  aria-label="Filter repair plan by connector"
                >
                  {sourceRepairConnectorOptions.map((connector) => (
                    <option key={connector} value={connector}>{connector === 'ALL' ? 'All connectors' : connector}</option>
                  ))}
                </select>

                <select
                  value={sourceRepairStatusFilter}
                  onChange={(event) => setSourceRepairStatusFilter(event.target.value)}
                  style={styles.sourceRepairSelect}
                  aria-label="Filter repair plan by status"
                >
                  {sourceRepairStatusOptions.map((status) => (
                    <option key={status} value={status}>{status === 'ALL' ? 'All statuses' : status}</option>
                  ))}
                </select>
                <div style={styles.sourceRepairExportRail}>
                  <div style={styles.sourceRepairFormatToggle}>
                    {['PDF', 'JSON'].map((format) => (
                      <button
                        key={format}
                        type="button"
                        onClick={() => setSourceRepairExportFormat(format)}
                        style={
                          sourceRepairExportFormat === format
                            ? styles.sourceRepairFormatButtonActive
                            : styles.sourceRepairFormatButton
                        }
                      >
                        {format}
                      </button>
                    ))}
                  </div>

                  <button type="button" style={styles.sourceRepairExportButton} onClick={exportSourceRepairPlan}>
                    Export Repair Plan · {sourceRepairExportFormat}
                  </button>
                </div>

                <span style={styles.sourceRepairVisibleCount}>
                  Showing {visibleSourceRegistryFindings.length}/{sourceRegistryFindings.length}
                </span>
              </div>
            ) : null}

            <div style={sourceBreakdownOpen ? styles.sourceBreakdownGrid : styles.hidden}>
              {visibleSourceRegistryFindings.map((finding, index) => (
                <div key={`${finding.id}-${index}`} style={styles.sourceFindingCard}>
                  <div style={styles.sourceFindingTop}>
                    <span style={
                      finding.status === 'ERROR'
                        ? styles.sourceStatusError
                        : finding.status === 'MISSING'
                          ? styles.sourceStatusMissing
                          : styles.sourceStatusPending
                    }>
                      {finding.status}
                    </span>
                    <span style={styles.sourceConnector}>{finding.connector}</span>
                  </div>
                  <strong style={styles.sourceFindingTitle}>{finding.title}</strong>
                  {finding.method ? <span style={styles.sourceFindingMethod}>{finding.method}</span> : null}
                  <p style={styles.sourceFindingMessage}>{String(finding.message)}</p>

                  {finding.evidenceNeeded?.length ? (
                    <div style={styles.sourceEvidenceList}>
                      <span style={styles.sourceEvidenceLabel}>Evidence needed</span>
                      <span style={styles.sourceEvidenceText}>{finding.evidenceNeeded.slice(0, 3).join(' · ')}</span>
                    </div>
                  ) : null}

                  {finding.operatorAction ? (
                    <p style={styles.sourceFindingAction}>{finding.operatorAction}</p>
                  ) : null}
                </div>
              ))}
            </div>
          </div>
        ) : null}

        <div style={styles.cockpitToolbar}>
          <div>
            <span style={styles.metricLabel}>Workflow Mode</span>
            <div style={styles.workflowModeRail}>
              {WORKFLOW_FORMATS.map((item) => (
                <button
                  key={item.format}
                  type="button"
                  style={workflowFormat === item.format ? styles.workflowModeActive : styles.workflowModeButton}
                  onClick={() => setWorkflowFormat(item.format)}
                >
                  {item.label}
                </button>
              ))}
            </div>
          </div>

          <div style={styles.globalControls}>
            <button
              type="button"
              style={styles.globalControlButton}
              disabled={sourceRegistryLoading}
              onClick={handleVerifySources}
            >
              {sourceRegistryAction === 'verify' ? 'VERIFYING SOURCES' : 'Verify Sources'}
            </button>
            <button
              type="button"
              style={styles.globalControlPrimary}
              disabled={sourceRegistryLoading}
              onClick={handleSealBoardroomProof}
            >
              {sourceRegistryAction === 'seal' ? 'SEALING PROOF' : 'Seal Boardroom Proof'}
            </button>
            <button
              type="button"
              style={styles.globalControlButton}
              disabled={sourceRegistryLoading}
              onClick={handleExportInvestorPack}
            >
              {sourceRegistryAction === 'investor-pack' ? 'EXPORTING PACK' : 'Export Investor Pack'}
            </button>
          </div>
        </div>

        <div style={styles.groupStack}>
          {groupedCatalog.map(({ group, items }) => {
            const isGroupOpen = openGroups[group] !== false;

            return (
              <section key={group} style={styles.contractGroup}>
                <button
                  type="button"
                  style={styles.groupHeader}
                  onClick={() => setOpenGroups((current) => ({ ...current, [group]: !isGroupOpen }))}
                >
                  <span style={styles.groupTitle}>{group}</span>
                  <span style={styles.groupMeta}>{items.length} artifacts</span>
                  <span style={styles.groupChevron}>{isGroupOpen ? 'Collapse' : 'Expand'}</span>
                </button>

                {isGroupOpen ? (
                  <div style={styles.contractGrid}>
                    {items.map((artifact) => {
                      const risk = riskForArtifact(artifact);
                      const approvals = approvalsForArtifact(artifact);
                      const activeFormat = workflowFormat || 'PDF';
                      const generating = isGeneratingId === `${artifact.id}:${activeFormat}`;
                      const isCurrentArtifact = generating || lastArtifact?.artifactId === artifact.id;

                      return (
                        <article key={artifact.id} style={isCurrentArtifact ? styles.contractCardActive : styles.contractCard}>
                          <div style={styles.contractTop}>
                            <span style={styles.categoryPill}>{artifact.category}</span>
                            <span style={risk === 'HIGH' ? styles.riskHigh : risk === 'MEDIUM' ? styles.riskMedium : styles.riskStandard}>{risk}</span>
                          </div>

                          <h3 style={styles.contractTitle}>{artifact.title}</h3>
                          <p style={styles.contractDescription}>{artifact.description}</p>

                          <div style={styles.stageProgress} aria-label="Workflow progress">
                            {LIFECYCLE_STAGES.map((stage, index) => (
                              <span
                                key={stage}
                                title={stage}
                                style={index === 0 ? styles.stageSegmentActive : styles.stageSegment}
                              />
                            ))}
                          </div>

                          <div style={styles.contractMeta}>
                            <div>
                              <span style={styles.intelLabel}>Approvals</span>
                              <strong style={styles.intelValue}>{approvals.join(' + ')}</strong>
                            </div>
                            <div>
                              <span style={styles.intelLabel}>Clause Pack</span>
                              <strong style={styles.intelValue}>{clausePackForArtifact(artifact)}</strong>
                            </div>
                          </div>

                          <button
                            type="button"
                            style={isCurrentArtifact ? styles.primaryButtonActive : styles.primaryButton}
                            disabled={Boolean(isGeneratingId)}
                            onClick={() => generateArtifact(artifact)}
                          >
                            {generating ? `GENERATING ${activeFormat}` : `CONTINUE WORKFLOW · ${FORMAT_META[activeFormat]?.label || activeFormat}`}
                          </button>
                        </article>
                      );
                    })}
                  </div>
                ) : null}
              </section>
            );
          })}
        </div>

      </section>
    </div>
  );
}

const buttonBase = {
  display: 'inline-flex',
  alignItems: 'center',
  justifyContent: 'center',
  gap: 10,
  borderRadius: 14,
  borderWidth: 1,
  borderStyle: 'solid',
  cursor: 'pointer',
  fontFamily: 'inherit',
  fontWeight: 900,
  letterSpacing: 1,
  textTransform: 'uppercase',
  whiteSpace: 'nowrap'
};

const styles = {
  overlay: {
    position: 'fixed',
    inset: 0,
    zIndex: 9999,
    background: 'rgba(0,0,0,0.68)',
    backdropFilter: 'blur(10px)',
    padding: '26px 34px',
    overflow: 'auto'
  },
  panel: {
    minHeight: 'calc(100vh - 52px)',
    border: '1px solid var(--wilsy-command-border, rgba(168,85,247,0.42))',
    borderRadius: 28,
    background: 'linear-gradient(145deg, var(--wilsy-command-bg, #05050a) 0%, var(--wilsy-command-panel, #08050f) 52%, #020203 100%)',
    boxShadow: '0 34px 110px rgba(0,0,0,0.72)',
    color: 'var(--wilsy-command-text, #f8f1ff)',
    padding: 28
  },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    gap: 22,
    alignItems: 'flex-start',
    borderBottom: '1px solid rgba(212,175,55,0.24)',
    paddingBottom: 18
  },
  eyebrow: {
    color: 'var(--wilsy-accent, #d4af37)',
    fontWeight: 950,
    letterSpacing: 2.2,
    fontSize: 12
  },
  title: {
    margin: '7px 0 6px',
    fontSize: 36,
    letterSpacing: -0.8
  },
  subtitle: {
    margin: 0,
    maxWidth: 980,
    color: 'var(--wilsy-muted, #cfc7a8)',
    lineHeight: 1.5,
    fontSize: 15
  },
  closeButton: {
    ...buttonBase,
    minHeight: 44,
    padding: '11px 16px',
    background: 'rgba(255,255,255,0.025)',
    color: 'var(--wilsy-text, #f8f1d0)',
    borderColor: 'rgba(212,175,55,0.34)'
  },
  commandBar: {
    marginTop: 18
  },
  search: {
    width: '100%',
    boxSizing: 'border-box',
    minHeight: 56,
    borderRadius: 18,
    border: '1px solid rgba(212,175,55,0.34)',
    background: 'var(--wilsy-input-bg, #091813)',
    color: 'var(--wilsy-text, #f8f1d0)',
    padding: '0 18px',
    fontSize: 16,
    outline: 'none'
  },
  categoryRail: {
    display: 'flex',
    gap: 10,
    overflowX: 'auto',
    padding: '16px 0 4px'
  },
  categoryButton: {
    ...buttonBase,
    minHeight: 36,
    padding: '8px 12px',
    background: 'rgba(255,255,255,0.025)',
    color: 'var(--wilsy-muted, #cfc7a8)',
    borderColor: 'rgba(212,175,55,0.24)',
    fontSize: 11
  },
  categoryActive: {
    ...buttonBase,
    minHeight: 36,
    padding: '8px 12px',
    background: 'linear-gradient(135deg, #fff3a3, var(--wilsy-accent, #d4af37))',
    color: 'var(--wilsy-on-accent, #050505)',
    borderColor: 'var(--wilsy-accent, #d4af37)',
    fontSize: 11
  },
  statusGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(4, minmax(0, 1fr))',
    gap: 12,
    margin: '14px 0'
  },
  statusTile: {
    display: 'grid',
    alignContent: 'center',
    gap: 6,
    minHeight: 66,
    border: '1px solid rgba(212,175,55,0.22)',
    borderRadius: 16,
    padding: 14,
    background: 'rgba(255,255,255,0.025)',
    overflow: 'hidden'
  },
  message: {
    border: '1px solid var(--wilsy-command-border, rgba(168,85,247,0.34))',
    borderRadius: 16,
    padding: 14,
    marginBottom: 14,
    color: 'var(--wilsy-command-text, #f8f1ff)',
    background: 'rgba(20,8,30,0.78)'
  },
  sourceBreakdownPanel: {
    border: '1px solid rgba(212,175,55,0.30)',
    borderRadius: 22,
    padding: 16,
    marginBottom: 18,
    background: 'linear-gradient(135deg, rgba(10,8,14,0.94), rgba(24,10,34,0.84))',
    boxShadow: 'inset 0 1px 0 rgba(255,255,255,0.035), 0 18px 42px rgba(0,0,0,0.28)'
  },
  sourceBreakdownHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    gap: 18,
    alignItems: 'flex-start',
    marginBottom: 14,
    borderBottom: '1px solid rgba(212,175,55,0.18)',
    paddingBottom: 12
  },
  sourceBreakdownTitle: {
    display: 'block',
    color: '#f8f1ff',
    fontSize: 17,
    fontWeight: 950,
    letterSpacing: 1.3,
    textTransform: 'uppercase',
    marginBottom: 5
  },
  sourceBreakdownSubtitle: {
    display: 'block',
    color: '#bdb39a',
    fontSize: 12,
    fontWeight: 800,
    letterSpacing: 0.6
  },
  hidden: {
    display: 'none'
  },
  sourceBreakdownHeaderActions: {
    display: 'inline-flex',
    alignItems: 'center',
    gap: 10,
    flexWrap: 'wrap',
    justifyContent: 'flex-end'
  },
  sourceBreakdownToggleButton: {
    ...buttonBase,
    minHeight: 32,
    padding: '7px 11px',
    borderRadius: 999,
    borderColor: 'rgba(212,175,55,0.34)',
    background: 'rgba(0,0,0,0.28)',
    color: '#f8f1ff',
    fontSize: 10,
    letterSpacing: 1.1
  },
  sourceBreakdownCollapsedNotice: {
    border: '1px solid rgba(212,175,55,0.22)',
    borderRadius: 16,
    padding: 14,
    background: 'rgba(0,0,0,0.24)',
    color: '#bdb39a',
    fontSize: 12.5,
    lineHeight: 1.45,
    fontWeight: 800,
    marginBottom: 12
  },
  sourceBreakdownCount: {
    display: 'inline-flex',
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: 32,
    padding: '7px 11px',
    borderRadius: 999,
    border: '1px solid rgba(212,175,55,0.32)',
    background: 'rgba(0,0,0,0.28)',
    color: '#d4af37',
    fontSize: 11,
    fontWeight: 950,
    letterSpacing: 1,
    textTransform: 'uppercase',
    whiteSpace: 'nowrap'
  },
  sourceBreakdownGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
    gap: 12,
    maxHeight: 520,
    overflowY: 'auto',
    paddingRight: 4
  },
  sourceFindingCard: {
    border: '1px solid rgba(255,255,255,0.12)',
    borderRadius: 18,
    padding: 14,
    background: 'linear-gradient(180deg, rgba(3,5,8,0.92), rgba(13,6,22,0.84))',
    minHeight: 138,
    boxShadow: 'inset 0 1px 0 rgba(255,255,255,0.035)'
  },
  sourceFindingTop: {
    display: 'flex',
    justifyContent: 'space-between',
    gap: 10,
    alignItems: 'center',
    marginBottom: 10
  },
  sourceStatusError: {
    display: 'inline-flex',
    alignItems: 'center',
    minHeight: 24,
    padding: '4px 8px',
    borderRadius: 999,
    border: '1px solid rgba(255,120,120,0.34)',
    background: 'rgba(90,12,20,0.36)',
    color: '#ffb4b4',
    fontSize: 10,
    fontWeight: 950,
    letterSpacing: 1.1
  },
  sourceStatusMissing: {
    display: 'inline-flex',
    alignItems: 'center',
    minHeight: 24,
    padding: '4px 8px',
    borderRadius: 999,
    border: '1px solid rgba(212,175,55,0.38)',
    background: 'rgba(80,55,8,0.30)',
    color: '#d4af37',
    fontSize: 10,
    fontWeight: 950,
    letterSpacing: 1.1
  },
  sourceStatusPending: {
    display: 'inline-flex',
    alignItems: 'center',
    minHeight: 24,
    padding: '4px 8px',
    borderRadius: 999,
    border: '1px solid rgba(192,132,252,0.34)',
    background: 'rgba(49,17,78,0.34)',
    color: '#d8c7ff',
    fontSize: 10,
    fontWeight: 950,
    letterSpacing: 1.1
  },
  sourceConnector: {
    display: 'inline-flex',
    alignItems: 'center',
    minHeight: 24,
    padding: '4px 8px',
    borderRadius: 999,
    border: '1px solid rgba(255,255,255,0.10)',
    background: 'rgba(255,255,255,0.035)',
    color: '#bdb39a',
    fontSize: 10,
    fontWeight: 900,
    letterSpacing: 0.9,
    textTransform: 'uppercase',
    whiteSpace: 'nowrap'
  },
  sourceFindingTitle: {
    display: 'block',
    color: '#f8f1ff',
    fontSize: 15,
    lineHeight: 1.28,
    marginBottom: 7,
    fontWeight: 950
  },
  sourceFindingMethod: {
    display: 'inline-flex',
    width: 'fit-content',
    color: '#c084fc',
    fontSize: 11,
    fontWeight: 900,
    marginBottom: 7,
    letterSpacing: 0.4
  },
  sourceFindingMessage: {
    margin: 0,
    color: '#d8c7ff',
    fontSize: 12.5,
    lineHeight: 1.38
  },
  sourceRepairSummaryRail: {
    display: 'flex',
    flexWrap: 'wrap',
    gap: 8,
    marginBottom: 14
  },
  sourceRepairSummaryPill: {
    display: 'inline-flex',
    alignItems: 'center',
    minHeight: 28,
    padding: '5px 9px',
    borderRadius: 999,
    border: '1px solid rgba(212,175,55,0.22)',
    background: 'rgba(0,0,0,0.22)',
    color: '#d4af37',
    fontSize: 10.5,
    fontWeight: 950,
    letterSpacing: 0.8,
    textTransform: 'uppercase',
    cursor: 'pointer',
    fontFamily: 'inherit'
  },
  sourceRepairSummaryPillActive: {
    display: 'inline-flex',
    alignItems: 'center',
    minHeight: 28,
    padding: '5px 9px',
    borderRadius: 999,
    border: '1px solid rgba(212,175,55,0.56)',
    background: 'linear-gradient(135deg, rgba(212,175,55,0.28), rgba(192,132,252,0.18))',
    color: '#fff3a3',
    fontSize: 10.5,
    fontWeight: 950,
    letterSpacing: 0.8,
    textTransform: 'uppercase',
    cursor: 'pointer',
    fontFamily: 'inherit'
  },
  sourceRepairControlRail: {
    display: 'grid',
    gridTemplateColumns: 'minmax(180px, 0.8fr) minmax(160px, 0.6fr) minmax(320px, 1fr) minmax(110px, 0.35fr)',
    gap: 10,
    alignItems: 'center',
    marginBottom: 14
  },
  sourceRepairSelect: {
    minHeight: 38,
    borderRadius: 12,
    border: '1px solid rgba(212,175,55,0.28)',
    background: 'rgba(0,0,0,0.34)',
    color: '#f8f1ff',
    padding: '0 10px',
    fontFamily: 'inherit',
    fontWeight: 850,
    outline: 'none'
  },
  sourceRepairExportRail: {
    display: 'grid',
    gridTemplateColumns: '90px minmax(180px, 1fr)',
    gap: 10,
    alignItems: 'stretch'
  },
  sourceRepairFormatToggle: {
    display: 'grid',
    gridTemplateColumns: '1fr 1fr',
    gap: 6,
    padding: 4,
    borderRadius: 12,
    border: '1px solid rgba(212,175,55,0.18)',
    background: 'rgba(255,255,255,0.03)'
  },
  sourceRepairFormatButton: {
    minHeight: 30,
    borderRadius: 9,
    border: '1px solid rgba(255,255,255,0.08)',
    background: 'rgba(0,0,0,0.24)',
    color: '#bdb39a',
    fontSize: 10.5,
    fontWeight: 900,
    letterSpacing: 0.8,
    textTransform: 'uppercase',
    cursor: 'pointer',
    fontFamily: 'inherit'
  },
  sourceRepairFormatButtonActive: {
    minHeight: 30,
    borderRadius: 9,
    border: '1px solid rgba(212,175,55,0.32)',
    background: 'linear-gradient(135deg, rgba(212,175,55,0.22), rgba(192,132,252,0.2))',
    color: '#fff7dc',
    fontSize: 10.5,
    fontWeight: 900,
    letterSpacing: 0.8,
    textTransform: 'uppercase',
    cursor: 'pointer',
    fontFamily: 'inherit'
  },
  sourceRepairExportButton: {
    ...buttonBase,
    minHeight: 38,
    padding: '8px 10px',
    background: 'linear-gradient(135deg, #d4af37, #c084fc)',
    color: '#050505',
    borderColor: '#d4af37',
    fontSize: 10.5,
    width: '100%'
  },
  sourceRepairVisibleCount: {
    color: '#bdb39a',
    fontSize: 11,
    fontWeight: 900,
    textTransform: 'uppercase',
    letterSpacing: 0.8,
    justifySelf: 'end'
  },
  sourceEvidenceList: {
    display: 'grid',
    gap: 4,
    marginTop: 10,
    paddingTop: 9,
    borderTop: '1px solid rgba(255,255,255,0.08)'
  },
  sourceEvidenceLabel: {
    color: '#d4af37',
    fontSize: 10,
    fontWeight: 950,
    letterSpacing: 1.1,
    textTransform: 'uppercase'
  },
  sourceEvidenceText: {
    color: '#f8f1ff',
    fontSize: 11.5,
    lineHeight: 1.35,
    fontWeight: 750
  },
  sourceFindingAction: {
    margin: '9px 0 0',
    color: '#bdb39a',
    fontSize: 11.5,
    lineHeight: 1.36
  },
  grid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(360px, 1fr))',
    gap: 16
  },
  card: {
    border: '1px solid var(--wilsy-card-border, rgba(168,85,247,0.28))',
    borderRadius: 22,
    background: 'linear-gradient(180deg, rgba(7,10,14,0.98), rgba(3,5,8,0.99))',
    padding: 18,
    boxShadow: 'inset 0 1px 0 rgba(255,255,255,0.035)',
    minHeight: 360
  },
  cardTop: {
    display: 'flex',
    justifyContent: 'space-between',
    gap: 12,
    alignItems: 'center'
  },
  categoryPill: {
    color: 'var(--wilsy-accent, #d4af37)',
    fontSize: 12,
    fontWeight: 950
  },
  riskHigh: {
    color: '#ffcf96',
    fontSize: 11,
    fontWeight: 950
  },
  riskMedium: {
    color: '#f3dc7c',
    fontSize: 11,
    fontWeight: 950
  },
  riskStandard: {
    color: 'var(--wilsy-success, #9ff5d1)',
    fontSize: 11,
    fontWeight: 950
  },
  cardTitle: {
    margin: '12px 0 8px',
    fontSize: 21,
    lineHeight: 1.2
  },
  cardDescription: {
    margin: 0,
    minHeight: 54,
    color: 'var(--wilsy-muted, #cfc7a8)',
    lineHeight: 1.45,
    fontSize: 14.5
  },
  intelGrid: {
    display: 'grid',
    gridTemplateColumns: '1fr 1fr',
    gap: 12,
    marginBottom: 12
  },
  lifecycle: {
    display: 'flex',
    flexWrap: 'wrap',
    gap: 6,
    marginBottom: 12
  },
  exportRail: {
    display: 'grid',
    gridTemplateColumns: 'repeat(4, minmax(0, 1fr))',
    gap: 8,
    marginBottom: 12
  },
  formatButton: {
    ...buttonBase,
    minHeight: 44,
    padding: '9px 8px',
    background: 'rgba(0,0,0,0.22)',
    color: 'var(--wilsy-command-text, #f8f1ff)',
    borderColor: 'rgba(212,175,55,0.24)',
    fontSize: 11,
    textAlign: 'center',
    overflow: 'hidden',
    opacity: 0.82
  },
  formatActive: {
    ...buttonBase,
    minHeight: 44,
    padding: '9px 8px',
    background: 'linear-gradient(135deg, #fff3a3 0%, #d4af37 45%, #c084fc 100%)',
    color: '#050505',
    borderColor: '#d4af37',
    fontSize: 11,
    textAlign: 'center',
    overflow: 'hidden',
    opacity: 1
  },
  statusLabel: {
    display: 'block',
    color: '#aFA78E',
    fontSize: 11,
    fontWeight: 900,
    letterSpacing: 1.2,
    textTransform: 'uppercase'
  },
  statusValue: {
    display: 'block',
    color: 'var(--wilsy-text, #f8f1d0)',
    fontSize: 16,
    fontWeight: 900,
    lineHeight: 1.25,
    overflow: 'hidden',
    textOverflow: 'ellipsis',
    whiteSpace: 'nowrap'
  },
  intelLabel: {
    display: 'block',
    color: '#aFA78E',
    fontSize: 11,
    fontWeight: 900,
    letterSpacing: 1,
    textTransform: 'uppercase',
    marginBottom: 4
  },
  intelValue: {
    display: 'block',
    color: 'var(--wilsy-text, #f8f1d0)',
    fontSize: 14,
    fontWeight: 900,
    lineHeight: 1.3
  },
  lifecycleStage: {
    display: 'inline-flex',
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: 28,
    padding: '0 9px',
    borderRadius: 999,
    border: '1px solid rgba(212,175,55,0.22)',
    color: '#d8d0b6',
    background: 'rgba(0,0,0,0.16)',
    fontSize: 11,
    fontWeight: 850,
    letterSpacing: 0.3
  },
  formatLabel: {
    display: 'block',
    width: '100%',
    overflow: 'hidden',
    textOverflow: 'ellipsis',
    whiteSpace: 'nowrap',
    lineHeight: 1.1
  },

  executiveStrip: {
    display: 'grid',
    gridTemplateColumns: 'repeat(3, minmax(150px, 0.65fr)) minmax(320px, 1.4fr)',
    gap: 12,
    margin: '18px 0 12px'
  },
  executiveMetric: {
    minHeight: 76,
    border: '1px solid rgba(212,175,55,0.22)',
    borderRadius: 18,
    padding: 14,
    background: 'rgba(3,5,8,0.78)',
    display: 'grid',
    alignContent: 'center',
    gap: 6,
    overflow: 'hidden'
  },
  lastArtifactMetric: {
    borderColor: 'rgba(212,175,55,0.34)'
  },
  metricLabel: {
    color: '#bdb39a',
    fontSize: 11,
    fontWeight: 950,
    letterSpacing: 1.6,
    textTransform: 'uppercase'
  },
  metricValue: {
    color: '#f8f1d0',
    fontSize: 20,
    fontWeight: 950
  },
  metricWarning: {
    color: '#d4af37',
    fontSize: 18,
    fontWeight: 950,
    textTransform: 'uppercase'
  },
  metricSuccess: {
    color: '#67f5c5',
    fontSize: 18,
    fontWeight: 950,
    textTransform: 'uppercase'
  },
  receiptTicker: {
    position: 'relative',
    overflow: 'hidden',
    width: '100%',
    minHeight: 30,
    whiteSpace: 'nowrap',
    maskImage: 'linear-gradient(90deg, transparent, #000 8%, #000 92%, transparent)'
  },
  receiptMarqueeTrack: {
    display: 'inline-flex',
    gap: 56,
    minWidth: '200%',
    animation: 'wilsyReceiptMarquee 18s linear infinite'
  },
  receiptMarqueeItem: {
    display: 'inline-block',
    minWidth: '50%',
    color: '#f8f1ff',
    fontSize: 18,
    fontWeight: 950,
    lineHeight: 1.35,
    whiteSpace: 'nowrap'
  },
  sourceRegistryAlert: {
    display: 'flex',
    justifyContent: 'space-between',
    gap: 18,
    alignItems: 'center',
    border: '1px solid rgba(212,175,55,0.34)',
    borderRadius: 18,
    padding: '14px 16px',
    marginBottom: 14,
    color: '#f8f1ff',
    background: 'linear-gradient(135deg, rgba(35,18,4,0.74), rgba(18,8,30,0.74))'
  },
  sourceRegistryVerified: {
    display: 'flex',
    justifyContent: 'space-between',
    gap: 18,
    alignItems: 'center',
    border: '1px solid rgba(103,245,197,0.34)',
    borderRadius: 18,
    padding: '14px 16px',
    marginBottom: 14,
    color: '#f8f1ff',
    background: 'rgba(8,26,18,0.74)'
  },
  cockpitToolbar: {
    display: 'grid',
    gridTemplateColumns: 'minmax(340px, 0.8fr) minmax(420px, 1.2fr)',
    gap: 14,
    marginBottom: 16,
    alignItems: 'end'
  },
  workflowModeRail: {
    display: 'grid',
    gridTemplateColumns: 'repeat(4, minmax(0, 1fr))',
    gap: 8,
    marginTop: 8
  },
  workflowModeButton: {
    ...buttonBase,
    minHeight: 42,
    padding: '9px 10px',
    background: 'rgba(0,0,0,0.25)',
    color: '#f8f1ff',
    borderColor: 'rgba(212,175,55,0.24)',
    fontSize: 10.5,
    opacity: 0.78
  },
  workflowModeActive: {
    ...buttonBase,
    minHeight: 42,
    padding: '9px 10px',
    background: 'linear-gradient(135deg, #fff3a3 0%, #d4af37 46%, #c084fc 100%)',
    color: '#050505',
    borderColor: '#d4af37',
    fontSize: 10.5
  },
  globalControls: {
    display: 'grid',
    gridTemplateColumns: 'repeat(3, minmax(0, 1fr))',
    gap: 8
  },
  globalControlButton: {
    ...buttonBase,
    minHeight: 42,
    padding: '9px 10px',
    background: 'rgba(0,0,0,0.25)',
    color: '#f8f1ff',
    borderColor: 'rgba(212,175,55,0.24)',
    fontSize: 10.5
  },
  globalControlPrimary: {
    ...buttonBase,
    minHeight: 42,
    padding: '9px 10px',
    background: 'linear-gradient(135deg, #d4af37, #c084fc)',
    color: '#050505',
    borderColor: '#d4af37',
    fontSize: 10.5
  },
  groupStack: {
    display: 'grid',
    gap: 14
  },
  contractGroup: {
    border: '1px solid rgba(212,175,55,0.22)',
    borderRadius: 24,
    background: 'rgba(0,0,0,0.22)',
    overflow: 'hidden'
  },
  groupHeader: {
    ...buttonBase,
    width: '100%',
    minHeight: 58,
    padding: '14px 18px',
    border: 'none',
    borderBottom: '1px solid rgba(212,175,55,0.16)',
    borderRadius: 0,
    background: 'linear-gradient(90deg, rgba(8,10,15,0.98), rgba(21,9,33,0.76))',
    color: '#f8f1ff',
    justifyContent: 'space-between',
    textAlign: 'left'
  },
  groupTitle: {
    fontSize: 16,
    letterSpacing: 1.4
  },
  groupMeta: {
    color: '#d4af37',
    fontSize: 12
  },
  groupChevron: {
    color: '#bdb39a',
    fontSize: 11
  },
  contractGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(330px, 1fr))',
    gap: 12,
    padding: 14
  },
  contractCard: {
    border: '1px solid rgba(212,175,55,0.18)',
    borderRadius: 20,
    padding: 16,
    background: 'linear-gradient(180deg, rgba(7,10,14,0.98), rgba(3,5,8,0.99))',
    minHeight: 254
  },
  contractCardActive: {
    border: '1px solid rgba(212,175,55,0.46)',
    borderRadius: 20,
    padding: 16,
    background: 'linear-gradient(180deg, rgba(11,14,20,0.99), rgba(13,6,22,0.99))',
    minHeight: 254,
    boxShadow: '0 18px 44px rgba(192,132,252,0.14)'
  },
  contractTop: {
    display: 'flex',
    justifyContent: 'space-between',
    gap: 12,
    alignItems: 'center',
    marginBottom: 10
  },
  contractTitle: {
    margin: '0 0 8px',
    fontSize: 21,
    lineHeight: 1.18,
    color: '#f8f1ff'
  },
  contractDescription: {
    margin: 0,
    minHeight: 44,
    color: '#d8c7ff',
    lineHeight: 1.45,
    fontSize: 14
  },
  stageProgress: {
    display: 'grid',
    gridTemplateColumns: 'repeat(6, minmax(0, 1fr))',
    gap: 5,
    margin: '16px 0'
  },
  stageSegment: {
    height: 6,
    borderRadius: 999,
    background: 'rgba(255,255,255,0.13)'
  },
  stageSegmentActive: {
    height: 6,
    borderRadius: 999,
    background: 'linear-gradient(90deg, #d4af37, #c084fc)'
  },
  contractMeta: {
    display: 'grid',
    gridTemplateColumns: '1fr 1fr',
    gap: 12,
    marginBottom: 14
  },
  primaryButton: {
    ...buttonBase,
    width: '100%',
    minHeight: 46,
    padding: '12px 16px',
    background: 'rgba(0,0,0,0.24)',
    color: '#f8f1ff',
    borderColor: 'rgba(212,175,55,0.24)',
    fontSize: 12,
    opacity: 0.84
  },
  primaryButtonActive: {
    ...buttonBase,
    width: '100%',
    minHeight: 48,
    padding: '13px 16px',
    background: 'linear-gradient(135deg, #fff3a3 0%, #d4af37 48%, #c084fc 100%)',
    color: '#050505',
    borderColor: '#d4af37',
    fontSize: 12,
    boxShadow: '0 12px 30px rgba(192,132,252,0.22)'
  },
};

export default BusinessArtifactStudio;
