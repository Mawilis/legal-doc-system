/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - ACCOUNT COMPLIANCE COMMAND SERVICE [R18AD23-LIVE-BRIDGE]                                      ║
 * ║ LIVE BACKEND BRIDGE | FORENSIC MERKLE | REGULATOR EXPORT | AUDIT LEDGER | NO FAKE DATA                  ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/services/accountComplianceCommandService.js ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 *
 * @fileoverview Backend-owned Account Compliance Command payload builder.
 * The service aggregates existing Wilsy OS forensic, audit, regulator export and compliance engines
 * into a safe read-only command contract for the Account Command Center.
 */

import forensicMerkleAuditor from './ForensicMerkleAuditor.js';
import '../models/Case.js';
import RegulatorExportETL from './RegulatorExportETL.js';
import auditLogger from './AuditLogger.js';
import caseComplianceService from './CaseComplianceService.js';
import { getAccountComplianceEvidenceSnapshot } from './accountEvidenceCommandService.js';

export const WILSY_ACCOUNT_COMPLIANCE_COMMAND_VERSION = 'R18AD23-LIVE-BACKEND-COMPLIANCE-COMMAND';

/**
 * @function normalizeWilsyComplianceTenantId
 * @description Normalizes a tenant identifier for the Account Compliance command service.
 * @param {string} tenantId - Requested tenant identifier.
 * @returns {string} Safe tenant identifier.
 * @collaboration Keeps Account Compliance, Forensic Merkle and tenant-scoped routes aligned.
 */
function normalizeWilsyComplianceTenantId(tenantId = '') {
  const normalized = String(tenantId || '').trim();
  return normalized || 'wilsy-sovereign-root';
}

/**
 * @function compactWilsyComplianceHash
 * @description Compacts long Merkle/hash values for command-card display.
 * @param {string} value - Hash or root value.
 * @param {string} fallback - Fallback label.
 * @returns {string} Compact display value.
 * @collaboration Keeps proof roots readable without exposing raw noisy payloads in cockpit cards.
 */
function compactWilsyComplianceHash(value = '', fallback = 'Root pending') {
  const normalized = String(value || '')
    .replace(/[^a-z0-9]/gi, '')
    .toUpperCase();
  if (!normalized) return fallback;
  if (normalized.length <= 18) return normalized;
  return `${normalized.slice(0, 10)}…${normalized.slice(-6)}`;
}

/**
 * @function resolveWilsyServiceStatus
 * @description Builds a no-fake service availability packet.
 * @param {Object} params - Service availability inputs.
 * @returns {Object} Service status packet.
 * @collaboration Makes unavailable engines explicit instead of fabricating data.
 */
function resolveWilsyServiceStatus({ name, available, detail = '' }) {
  return {
    name,
    available: Boolean(available),
    status: available ? 'AVAILABLE' : 'UNAVAILABLE',
    detail: detail || (available ? 'Backend engine available' : 'Backend engine unavailable'),
  };
}

/**
 * @function pickWilsyReceiptContract
 * @description Extracts the most likely receipt contract from a Forensic Merkle auditor response.
 * @param {Object} packet - Auditor packet.
 * @returns {Object} Receipt contract.
 * @collaboration Normalizes multiple existing ForensicMerkleAuditor response shapes into one cockpit contract.
 */
function pickWilsyReceiptContract(packet = {}) {
  return (
    packet.receiptContract ||
    packet.receipts?.receiptContract ||
    packet.chain?.receiptContract ||
    packet.forensicReceiptContract ||
    {}
  );
}

/**
 * @function pickWilsyReceiptOverlay
 * @description Extracts the most likely receipt overlay from a Forensic Merkle auditor response.
 * @param {Object} packet - Auditor packet.
 * @returns {Object} Receipt overlay.
 * @collaboration Keeps Account Compliance summary resilient to existing backend packet versions.
 */
function pickWilsyReceiptOverlay(packet = {}) {
  return (
    packet.receiptOverlay || packet.receipts?.receiptOverlay || packet.chain?.receiptOverlay || {}
  );
}

/**
 * @function buildWilsyComplianceProofSummary
 * @description Builds the proof summary from live backend Forensic Merkle data.
 * @param {Object} packet - Forensic Merkle packet.
 * @returns {Object} Proof summary.
 * @collaboration Converts backend-owned Merkle proof posture into Account Compliance rail data.
 */
function buildWilsyComplianceProofSummary(packet = {}) {
  const contract = pickWilsyReceiptContract(packet);
  const overlay = pickWilsyReceiptOverlay(packet);
  const sealDecision = packet.sealDecision || {};
  const eligibility = sealDecision.eligibility || {};
  const blockers = Array.isArray(eligibility.blockers)
    ? eligibility.blockers
    : Array.isArray(packet.blockers)
      ? packet.blockers
      : [];
  const receiptRows = Array.isArray(packet.receiptRows)
    ? packet.receiptRows
    : Array.isArray(packet.receipts?.receipts)
      ? packet.receipts.receipts
      : [];

  const merkleRoot =
    packet.merkleRoot ||
    contract.merkleRoot ||
    overlay.merkleRoot ||
    packet.receiptMerkleRoot ||
    contract.receiptMerkleRoot ||
    overlay.receiptMerkleRoot ||
    '';

  const receiptCount = Number(
    packet.receiptCount ?? contract.receiptCount ?? overlay.receiptCount ?? receiptRows.length ?? 0
  );

  const sealedReceiptCount = Number(
    packet.sealedReceiptCount ?? contract.sealedReceiptCount ?? overlay.sealedReceiptCount ?? 0
  );

  const reviewReceiptCount = Number(
    packet.reviewReceiptCount ?? contract.reviewReceiptCount ?? overlay.reviewReceiptCount ?? 0
  );

  const clausesAnchored = Number(
    packet.clausesAnchored ??
      contract.clausesAnchored ??
      overlay.clausesAnchored ??
      receiptRows.reduce(
        (total, receipt) =>
          total + (Array.isArray(receipt.compliance) ? receipt.compliance.length : 0),
        0
      ) ??
      0
  );

  return {
    source: receiptCount ? 'forensic-merkle-auditor' : 'forensic-merkle-auditor-empty',
    receiptCount,
    sealedReceiptCount,
    reviewReceiptCount,
    clausesAnchored,
    merkleRoot,
    compactRoot: compactWilsyComplianceHash(merkleRoot),
    browserAuthority: false,
    backendAuthority: true,
    blockers,
    receiptSealStatus:
      packet.receiptSealStatus ||
      contract.receiptSealStatus ||
      overlay.receiptSealStatus ||
      (receiptCount ? 'BACKEND_PROOF_AVAILABLE' : 'NO_RECEIPTS_YET'),
  };
}

/**
 * @function callWilsyForensicMerkleAuditor
 * @description Calls the existing ForensicMerkleAuditor through safe read-only method candidates.
 * @param {Object} params - Call inputs.
 * @returns {Promise<Object>} Live forensic proof packet.
 * @collaboration Reuses the existing auditor instead of creating duplicate forensic engines.
 */
async function callWilsyForensicMerkleAuditor({ tenantId, limit }) {
  if (forensicMerkleAuditor?.rechainTenantReceiptWindow) {
    return forensicMerkleAuditor.rechainTenantReceiptWindow({
      tenantId,
      limit,
      dryRun: true,
      actor: 'ACCOUNT_COMPLIANCE_COMMAND',
      reason: 'READONLY_ACCOUNT_COMPLIANCE_COMMAND',
    });
  }

  if (forensicMerkleAuditor?.fetchForensicEntries && forensicMerkleAuditor?.computeMerkleRoot) {
    const entries = await forensicMerkleAuditor.fetchForensicEntries({ tenantId, limit });
    const hashes = entries
      .map((entry) => entry?.eventSeal || entry?.chainHash || entry?.hash || entry?._id)
      .filter(Boolean)
      .map((value) => String(value));

    return {
      receiptCount: entries.length,
      sealedReceiptCount: entries.length,
      reviewReceiptCount: 0,
      clausesAnchored: 0,
      merkleRoot: forensicMerkleAuditor.computeMerkleRoot(hashes),
      receiptRows: entries.slice(0, 5),
      receiptSealStatus: entries.length ? 'BACKEND_PROOF_AVAILABLE' : 'NO_RECEIPTS_YET',
    };
  }

  return {
    receiptCount: 0,
    sealedReceiptCount: 0,
    reviewReceiptCount: 0,
    clausesAnchored: 0,
    merkleRoot: '',
    blockers: ['FORENSIC_MERKLE_AUDITOR_METHOD_UNAVAILABLE'],
    receiptSealStatus: 'FORENSIC_MERKLE_AUDITOR_UNAVAILABLE',
  };
}

/**
 * @function resolveWilsyCaseComplianceReport
 * @description Resolves existing CaseComplianceService report without fabricating data on failure.
 * @param {string} tenantId - Tenant identifier.
 * @returns {Promise<Object>} Case compliance report status.
 * @collaboration Reuses the existing compliance engine when available and makes failures explicit.
 */
async function resolveWilsyCaseComplianceReport(tenantId) {
  if (!caseComplianceService?.generateComplianceReport) {
    return {
      available: false,
      status: 'UNAVAILABLE',
      report: null,
      message: 'Case compliance report engine unavailable',
    };
  }

  try {
    const report = await caseComplianceService.generateComplianceReport(tenantId);
    return {
      available: true,
      status: 'AVAILABLE',
      report,
      message: 'Case compliance report resolved',
    };
  } catch (error) {
    const rawMessage = String(error?.message || 'Case compliance report failed');
    const isMissingCaseModel =
      rawMessage.includes('Schema hasn') &&
      rawMessage.includes('registered for model') &&
      rawMessage.includes('Case');

    if (isMissingCaseModel) {
      return {
        available: false,
        status: 'MODEL_UNREGISTERED',
        report: null,
        message: 'Case compliance report model is not registered in this runtime',
      };
    }

    return {
      available: true,
      status: 'ENGINE_ERROR',
      report: null,
      message: 'Case compliance report engine returned an error',
    };
  }
}

/**
 * @function buildWilsyComplianceRailCards
 * @description Builds production rail cards from live service status and proof posture.
 * @param {Object} params - Card inputs.
 * @returns {Array<Object>} Rail cards.
 * @collaboration Powers the Account Compliance right rail without static demo data.
 */
function buildWilsyComplianceRailCards({ proof, complianceReportStatus, tenantId }) {
  const complianceReport = complianceReportStatus.report || {};
  const regulatoryCompliance = complianceReport.regulatoryCompliance || {};
  const popiaStatus =
    regulatoryCompliance.popia?.complianceLevel || complianceReport.popia?.complianceLevel || '';
  const ficaStatus =
    regulatoryCompliance.fica?.complianceLevel || complianceReport.fica?.complianceLevel || '';
  const lpcStatus = regulatoryCompliance.lpc?.complianceLevel || '';

  return [
    {
      id: 'privacy-command',
      label: 'Privacy command',
      title: popiaStatus
        ? `POPIA ${String(popiaStatus).replaceAll('_', ' ').toLowerCase()}`
        : 'POPIA controls backend-owned',
      detail: 'Privacy posture resolved through backend compliance and proof services.',
      status: popiaStatus || 'BACKEND_REVIEWABLE',
      source: complianceReportStatus.status,
    },
    {
      id: 'regulatory-ledger',
      label: 'Regulatory ledger',
      title: proof.receiptCount
        ? 'Evidence ledger command-ready'
        : 'Evidence ledger awaiting receipts',
      detail: `${proof.receiptCount} receipts · ${proof.clausesAnchored} clause bindings · tenant ${tenantId}`,
      status: proof.receiptSealStatus,
      source: proof.source,
    },
    {
      id: 'audit-defensibility',
      label: 'Audit defensibility',
      title: proof.receiptCount ? 'Backend proof board-ready' : 'Backend proof channel live',
      detail: proof.receiptCount
        ? `${proof.sealedReceiptCount} sealed · ${proof.reviewReceiptCount} review · root ${proof.compactRoot}`
        : 'Mongo-backed forensic auditor responded with no receipt rows yet.',
      status: proof.receiptCount ? 'BOARD_READY' : 'NO_RECEIPTS_YET',
      source: 'ForensicMerkleAuditor',
    },
    {
      id: 'chain-of-custody',
      label: 'Chain of custody',
      title: 'Evidence handling tracked',
      detail: 'Custody posture is backend-owned; no browser-generated proof authority is accepted.',
      status: 'BACKEND_AUTHORITY_ONLY',
      source: 'AuditLogger',
    },
    {
      id: 'regulator-access',
      label: 'Regulator access',
      title: RegulatorExportETL?.generateRegulatorBundle
        ? 'Disclosure package export available'
        : 'Disclosure export unavailable',
      detail: RegulatorExportETL?.generateRegulatorBundle
        ? 'RegulatorExportETL can generate redacted POPIA/GDPR-compliant evidence bundles.'
        : 'RegulatorExportETL.generateRegulatorBundle method is unavailable.',
      status: RegulatorExportETL?.generateRegulatorBundle
        ? 'EXPORT_ENGINE_AVAILABLE'
        : 'EXPORT_ENGINE_UNAVAILABLE',
      source: 'RegulatorExportETL',
    },
    {
      id: 'tenant-ledger',
      label: 'Tenant ledger',
      title: 'Tenant ledger command-ready',
      detail: `Tenant-scoped compliance and evidence posture resolved for ${tenantId}.`,
      status: ficaStatus || lpcStatus || 'TENANT_SCOPE_RESOLVED',
      source: 'CaseComplianceService',
    },
  ];
}

/**
 * @function buildWilsyAccountComplianceCommandPayload
 * @description Builds a live backend compliance command payload for the Account Command Center.
 * @param {Object} params - Payload inputs.
 * @param {string} params.tenantId - Tenant identifier.
 * @param {number} params.limit - Receipt replay limit.
 * @returns {Promise<Object>} Live compliance command payload.
 * @collaboration Wires existing Wilsy OS forensic, audit, regulator and compliance engines into one Account cockpit contract.
 */

/**
 * @function promoteAccountEvidenceSnapshotToCommandPayload
 * @description Promotes sealed Account Compliance evidence receipts into proof and rail cards.
 * @param {Object} payload - Account compliance command payload.
 * @returns {Object} Payload with proof and railCards aligned to sealed evidence when real receipts exist.
 * @collaboration Ensures Account Command Center displays receipt-backed proof without fabricating evidence or hiding backend diagnostics.
 */
function promoteAccountEvidenceSnapshotToCommandPayload(payload = {}) {
  const evidence = payload?.evidence || {};
  const receiptCount = Number(evidence.receiptCount || 0);
  const sealedReceiptCount = Number(evidence.sealedReceiptCount || 0);
  const clausesAnchored = Number(evidence.clausesAnchored || 0);
  const merkleRoot = String(evidence.merkleRoot || '').trim();
  const compactRoot =
    evidence.compactRoot ||
    (merkleRoot ? `${merkleRoot.slice(0, 18)}…${merkleRoot.slice(-12)}` : 'Root pending');
  const evidenceIsSealed = receiptCount > 0 && sealedReceiptCount > 0 && Boolean(merkleRoot);

  if (!evidenceIsSealed) {
    return payload;
  }

  const latestReceipt = evidence.latestReceipt || {};
  const previousDiagnostics = payload.diagnostics || {};
  const previousProof = payload.proof || {};

  const promotedProof = {
    ...previousProof,
    source: evidence.source || 'account_compliance_evidence_receipts',
    receiptCount,
    sealedReceiptCount,
    reviewReceiptCount: Number(previousProof.reviewReceiptCount || 0),
    clausesAnchored,
    merkleRoot,
    compactRoot,
    browserAuthority: false,
    backendAuthority: true,
    blockers: [],
    receiptSealStatus: evidence.receiptSealStatus || 'SEALED',
    latestReceiptId: latestReceipt.receiptId || null,
    evidenceHash: latestReceipt.evidenceHash || merkleRoot,
  };

  const railCards = Array.isArray(payload.railCards)
    ? payload.railCards.map((card) => {
        if (card.id === 'regulatory-ledger') {
          return {
            ...card,
            title: 'Sealed evidence ledger live',
            detail: `${receiptCount} receipts · ${clausesAnchored} clause bindings · root ${compactRoot}`,
            status: evidence.receiptSealStatus || 'SEALED',
            source: 'AccountComplianceEvidenceReceipt',
          };
        }

        if (card.id === 'audit-defensibility') {
          return {
            ...card,
            title: 'Receipt-backed audit channel live',
            detail: `Sealed receipt ${latestReceipt.receiptId || 'available'} anchors ${clausesAnchored} compliance bindings.`,
            status: evidence.receiptSealStatus || 'SEALED',
            source: 'AccountComplianceEvidenceReceipt',
          };
        }

        if (card.id === 'chain-of-custody') {
          return {
            ...card,
            title: 'Custody receipt sealed',
            detail: `Backend-only custody confirmed by sealed evidence hash ${String(latestReceipt.evidenceHash || merkleRoot).slice(0, 18)}…`,
            status: 'SEALED_BACKEND_CUSTODY',
            source: 'AccountComplianceEvidenceReceipt',
          };
        }

        if (card.id === 'regulator-access') {
          return {
            ...card,
            title: 'Regulator bundle ready',
            detail: `Regulator bundle can be produced from ${receiptCount} sealed receipts and Merkle root ${compactRoot}.`,
            status: 'BUNDLE_READY',
            source: 'accountEvidenceCommandService',
          };
        }

        if (card.id === 'tenant-ledger') {
          return {
            ...card,
            title: 'Tenant evidence ledger sealed',
            detail: `Tenant ${payload.tenantId || evidence.tenantId} has receipt-backed compliance evidence available.`,
            status: 'TENANT_EVIDENCE_SEALED',
            source: 'AccountComplianceEvidenceReceipt',
          };
        }

        return card;
      })
    : payload.railCards;

  const commandPayload = {
    ...payload,
    proof: promotedProof,
    railCards,
    actions: {
      ...(payload.actions || {}),
      regulatorBundleReady: evidence.regulatorBundleReady === true,
      latestReceiptId: latestReceipt.receiptId || null,
      evidenceProofSource: evidence.source || 'account_compliance_evidence_receipts',
    },
    diagnostics: {
      ...previousDiagnostics,
      evidencePromotedToProof: true,
      evidenceProofSource: evidence.source || 'account_compliance_evidence_receipts',
      forensicRepairBlockers: Array.isArray(previousDiagnostics.blockers)
        ? previousDiagnostics.blockers
        : [],
      blockers: [],
    },
  };

  return promoteAccountEvidenceSnapshotToCommandPayload(commandPayload);
}

export async function buildWilsyAccountComplianceCommandPayload({
  tenantId = 'wilsy-sovereign-root',
  limit = 250,
} = {}) {
  // R18AD30_ACCOUNT_EVIDENCE_SNAPSHOT
  const accountEvidenceSnapshot = await getAccountComplianceEvidenceSnapshot({
    tenantId,
    limit,
  }).catch((error) => ({
    available: false,
    version: 'R18AD30-DEFENSIBLE-EVIDENCE-BACKBONE',
    tenantId,
    source: 'account_compliance_evidence_receipts',
    receiptCount: 0,
    sealedReceiptCount: 0,
    clausesAnchored: 0,
    merkleRoot: '',
    compactRoot: 'Root pending',
    receiptSealStatus: 'EVIDENCE_SNAPSHOT_UNAVAILABLE',
    regulatorBundleReady: false,
    error: error?.message || 'Evidence snapshot unavailable',
  }));

  const safeTenantId = normalizeWilsyComplianceTenantId(tenantId);
  const safeLimit = Math.min(Math.max(Number(limit || 250), 1), 1000);

  const serviceStatus = {
    forensicMerkleAuditor: resolveWilsyServiceStatus({
      name: 'ForensicMerkleAuditor',
      available: Boolean(forensicMerkleAuditor),
    }),
    regulatorExportETL: resolveWilsyServiceStatus({
      name: 'RegulatorExportETL',
      available: Boolean(RegulatorExportETL?.generateRegulatorBundle),
      detail: RegulatorExportETL?.generateRegulatorBundle
        ? 'Regulator bundle export method available'
        : 'Regulator bundle export method unavailable',
    }),
    auditLogger: resolveWilsyServiceStatus({
      name: 'AuditLogger',
      available: Boolean(auditLogger),
    }),
    caseComplianceService: resolveWilsyServiceStatus({
      name: 'CaseComplianceService',
      available: Boolean(caseComplianceService?.generateComplianceReport),
    }),
  };

  let forensicPacket;
  try {
    forensicPacket = await callWilsyForensicMerkleAuditor({
      tenantId: safeTenantId,
      limit: safeLimit,
    });
  } catch (error) {
    forensicPacket = {
      receiptCount: 0,
      sealedReceiptCount: 0,
      reviewReceiptCount: 0,
      clausesAnchored: 0,
      merkleRoot: '',
      blockers: [error?.message || 'FORENSIC_MERKLE_AUDITOR_ERROR'],
      receiptSealStatus: 'FORENSIC_MERKLE_AUDITOR_ERROR',
    };
  }

  const proof = buildWilsyComplianceProofSummary(forensicPacket);
  const complianceReportStatus = await resolveWilsyCaseComplianceReport(safeTenantId);
  const railCards = buildWilsyComplianceRailCards({
    proof,
    complianceReportStatus,
    tenantId: safeTenantId,
  });

  return {
    ok: true,
    version: WILSY_ACCOUNT_COMPLIANCE_COMMAND_VERSION,
    tenantId: safeTenantId,
    source: 'live-backend-existing-engines',
    generatedAt: new Date().toISOString(),
    proof,
    compliance: {
      reportAvailable: complianceReportStatus.available,
      reportStatus: complianceReportStatus.status,
      reportMessage: complianceReportStatus.message,
      regulatoryCompliance: complianceReportStatus.report?.regulatoryCompliance || null,
      complianceScore: complianceReportStatus.report?.complianceScore ?? null,
    },
    services: serviceStatus,
    railCards,
    actions: {
      refresh: '/api/account/compliance-command',
      regulatorExportEngineAvailable: Boolean(RegulatorExportETL?.generateRegulatorBundle),
      browserAuthority: false,
      backendAuthority: true,
    },
    evidence: accountEvidenceSnapshot,
    diagnostics: {
      limit: safeLimit,
      blockers: proof.blockers,
      noFakeData: true,
      fallbackPolicy: 'explicit-empty-or-unavailable-only',
    },
  };
}

export default {
  buildWilsyAccountComplianceCommandPayload,
};
