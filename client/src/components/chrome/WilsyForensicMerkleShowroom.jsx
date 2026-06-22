/* eslint-disable */
/*
 * WILSY OS - FORENSIC MERKLE SHOWROOM
 * @file client/src/components/chrome/WilsyForensicMerkleShowroom.jsx
 * @version R18Z3-FORENSIC-PROOF-LAB-FORCE-SEAL-HUD-OPEN
 * @description Isolated executive-grade forensic proof showroom centered on the live Sovereign Root witness.
 * @collaboration Connects backend-owned Merkle authority, live audit command, evidence stream, compliance receipts, and authority posture without browser-side Merkle fabrication.
 * @fileNotes
 * - This component is a showroom/harness only.
 * - It must not be wired into Account, CRM, Founder, Executive, Finance, HR, or Security until approved.
 * - Merkle authority stays server-side through client/src/services/wilsyForensicMerkleClient.js.
 * - CSS layout lives in WilsyForensicMerkleShowroom.module.css.
 * - This component must not calculate Merkle roots or fabricate cryptographic receipts in the browser.
 */
import React, { useEffect, useMemo, useState } from 'react';
import {
  Activity,
  AlertTriangle,
  BadgeCheck,
  CheckCircle2,
  ChevronDown,
  DatabaseZap,
  FileCheck2,
  Fingerprint,
  GitBranch,
  Hash,
  LockKeyhole,
  RadioTower,
  ReceiptText,
  RefreshCw,
  ShieldCheck,
  Sparkles,
  TimerReset
} from 'lucide-react';
import {
  buildWilsyMerkleCockpitSnapshot,
  runWilsyMerkleAuditCycle,
  sealWilsyMerkleSafeWindow
} from '../../services/wilsyForensicMerkleClient.js';
import styles from './WilsyForensicMerkleShowroom.module.css';



export const WILSY_FORENSIC_SHOWROOM_BACK_BUTTON_VERSION = 'R18AD2D-REAL-SHOWROOM-BACK-BUTTON';

/**
 * @function resolveWilsyForensicShowroomReturnHrefR18AD2D
 * @description Resolves a safe in-app return target for the forensic showroom back button.
 * @collaboration Keeps the Forensic Proof Lab reachable for founder/root users while preserving dashboard-first navigation.
 */
function resolveWilsyForensicShowroomReturnHrefR18AD2D() {
  if (typeof window === 'undefined') {
    return '/';
  }

  const params = new URLSearchParams(window.location.search);
  const candidate = String(params.get('returnTo') || '/').trim();

  if (!candidate || candidate.startsWith('http://') || candidate.startsWith('https://') || candidate.startsWith('//')) {
    return '/';
  }

  if (candidate.startsWith('/wilsy-lab/forensic-merkle')) {
    return '/';
  }

  return candidate.startsWith('/') ? candidate : '/';
}

/**
 * @function WilsyForensicShowroomBackButtonR18AD2D
 * @description Renders the real showroom back control inside the React route instead of injecting global DOM chrome.
 * @collaboration Gives founder/root operators a deterministic return path without freezing dashboard routes or leaking showroom UI onto tenants.
 */
function WilsyForensicShowroomBackButtonR18AD2D() {
  const backHref = resolveWilsyForensicShowroomReturnHrefR18AD2D();

  return (
    <a
      href={backHref}
      data-wilsy-showroom-back-button="R18AD2D"
      aria-label="Back to Wilsy dashboard"
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '42px',
        padding: '0 18px',
        border: '1px solid rgba(255, 220, 124, 0.55)',
        borderRadius: '999px',
        background: 'linear-gradient(135deg, rgba(255, 234, 160, 0.98), rgba(212, 175, 55, 0.94))',
        color: '#060606',
        fontSize: '11px',
        fontWeight: 900,
        letterSpacing: '0.14em',
        textTransform: 'uppercase',
        textDecoration: 'none',
        boxShadow: '0 18px 50px rgba(0, 0, 0, 0.28)',
        whiteSpace: 'nowrap'
      }}
    >
      <WilsyForensicShowroomBackButtonR18AD2D />
      ← Back to dashboard
    </a>
  );
}

const WILSY_FORENSIC_MERKLE_SHOWROOM_VERSION = 'R18Z3-FORENSIC-PROOF-LAB-FORCE-SEAL-HUD-OPEN';
const WILSY_FORENSIC_PROOF_LAB_STATUS = 'FORENSIC_PROOF_LAB_EXPERIMENTAL';
const WILSY_FORENSIC_ACCOUNT_INTEGRATION_STATUS = 'ACCOUNT_COMMAND_CENTER_CARD_PENDING';

/**
 * @function compactWilsyProofValue
 * @description Compacts long forensic proof values into readable cockpit labels.
 * @collaboration Keeps backend Merkle roots and hashes visible without overwhelming executive proof surfaces.
 */
function compactWilsyProofValue(value, prefix = 'ROOT') {
  const normalized = String(value || 'PENDING').replace(/[^a-z0-9]/gi, '').toUpperCase();

  if (!normalized || normalized === 'PENDING') {
    return `${prefix}-PENDING`;
  }

  return `${prefix}-${normalized.slice(0, 14)}`;
}

/**
 * @function toWilsyExecutiveEvidenceLabel
 * @description Converts backend forensic states into executive-readable proof language.
 * @collaboration Keeps the cockpit truthful while removing raw backend status codes from investor and regulator surfaces.
 */
function toWilsyExecutiveEvidenceLabel(value) {
  const normalized = String(value || 'PENDING').trim();
  const key = normalized.toUpperCase().replace(/[\s-]+/g, '_');

  if (key.includes('FORENSIC_DB_UNAVAILABLE') || key.includes('DB_OFFLINE')) {
    return 'Evidence source offline';
  }

  if (key.includes('SOURCE_SILENT')) {
    return 'No evidence stream yet';
  }

  if (key.includes('LOCAL_APPEND_ONLY_PENDING_WORM')) {
    return 'Append-only seal pending';
  }

  if (key.includes('LOCAL_APPEND_ONLY')) {
    return 'Local append-only anchor';
  }

  if (key.includes('ROOT_VERIFIED')) {
    return 'Root verified';
  }

  if (key.includes('DRIFT') || key.includes('INVALID')) {
    return 'Review required';
  }

  if (key.includes('AWAITING_EVIDENCE') || key.includes('SOURCE_PENDING')) {
    return 'Waiting for evidence stream';
  }

  if (key.includes('RETIRED_NOT_USED')) {
    return 'Retired / not used';
  }

  if (key.includes('NO_WARNING')) {
    return 'No warning returned';
  }

  if (!normalized || key === 'PENDING') {
    return 'Pending';
  }

  return normalized
    .replace(/_/g, ' ')
    .replace(/\b\w/g, match => match.toUpperCase());
}

/**
 * @function normalizeWilsyAnchorList
 * @description Extracts a safe anchor array from possible backend anchor response shapes.
 * @collaboration Allows the showroom to consume existing backend routes without forcing a fragile response contract.
 */
function normalizeWilsyAnchorList(snapshot) {
  const anchorsPayload = snapshot?.anchors;

  if (Array.isArray(anchorsPayload)) {
    return anchorsPayload;
  }

  if (Array.isArray(anchorsPayload?.anchors)) {
    return anchorsPayload.anchors;
  }

  if (Array.isArray(anchorsPayload?.data)) {
    return anchorsPayload.data;
  }

  if (Array.isArray(anchorsPayload?.items)) {
    return anchorsPayload.items;
  }

  return [];
}

/**
 * @function normalizeWilsyReceiptRows
 * @description Extracts safe receipt rows from the R18C5 bridge snapshot contract.
 * @collaboration Lets the showroom display backend-owned receipt hashes and compliance bindings without calculating Merkle proof data in React.
 */
function normalizeWilsyReceiptRows(snapshot) {
  if (Array.isArray(snapshot?.receiptRows)) {
    return snapshot.receiptRows;
  }

  if (Array.isArray(snapshot?.receipts?.receipts)) {
    return snapshot.receipts.receipts;
  }

  if (Array.isArray(snapshot?.chain?.receipts)) {
    return snapshot.chain.receipts;
  }

  return [];
}

/**
 * @function normalizeWilsyReceiptContract
 * @description Extracts the backend receipt contract from current and fallback snapshot shapes.
 * @collaboration Makes receipt counts, clause bindings, receipt Merkle root and anchor posture first-class showroom evidence.
 */
function normalizeWilsyReceiptContract(snapshot) {
  return snapshot?.receiptContract
    || snapshot?.receipts?.receiptContract
    || snapshot?.chain?.receiptContract
    || {};
}

/**
 * @function normalizeWilsyReceiptOverlay
 * @description Extracts the backend receipt overlay from current and fallback snapshot shapes.
 * @collaboration Keeps review posture, jurisdiction anchors and safe-window sample counts aligned with the backend route contract.
 */
function normalizeWilsyReceiptOverlay(snapshot) {
  return snapshot?.receiptOverlay
    || snapshot?.receipts?.receiptOverlay
    || snapshot?.chain?.receiptOverlay
    || {};
}

/**
 * @function formatWilsyFrameworkList
 * @description Builds a compact framework label from receipt compliance rows and overlay anchors.
 * @collaboration Shows POPIA, GDPR, SOC2 and WORM coverage from server receipt data instead of hardcoded pending labels.
 */
function formatWilsyFrameworkList(snapshot) {
  const receiptRows = normalizeWilsyReceiptRows(snapshot);
  const overlay = normalizeWilsyReceiptOverlay(snapshot);
  const frameworks = new Set();

  receiptRows.forEach(receipt => {
    (receipt?.compliance || []).forEach(binding => {
      if (binding?.framework) {
        frameworks.add(String(binding.framework).toUpperCase());
      }
    });
  });

  (overlay?.jurisdictionAnchors || []).forEach(anchor => {
    if (anchor?.framework) {
      frameworks.add(String(anchor.framework).toUpperCase());
    }
  });

  return Array.from(frameworks).length > 0
    ? Array.from(frameworks).join(' · ')
    : 'POPIA · GDPR · SOC2 · WORM';
}

/**
 * @function buildWilsyReceiptSummary
 * @description Builds executive receipt summary labels from the backend receipt contract and overlay.
 * @collaboration Replaces anchor-count placeholders with safe-window receipt counts, sampled receipt rows and clause bindings.
 */
function buildWilsyReceiptSummary(snapshot) {
  const receiptRows = normalizeWilsyReceiptRows(snapshot);
  const contract = normalizeWilsyReceiptContract(snapshot);
  const overlay = normalizeWilsyReceiptOverlay(snapshot);
  const receiptCount = Number(contract.receiptCount ?? overlay.receiptCount ?? receiptRows.length ?? 0);
  const sampleReceiptCount = Number(overlay.sampleReceiptCount ?? receiptRows.length ?? 0);
  const reviewReceiptCount = Number(contract.reviewReceiptCount ?? overlay.reviewReceiptCount ?? 0);
  const sealedReceiptCount = Number(contract.sealedReceiptCount ?? overlay.sealedReceiptCount ?? 0);
  const clausesAnchored = Number(contract.clausesAnchored ?? overlay.clausesAnchored ?? 0);
  const posture = String(overlay.posture || contract.status || receiptRows[0]?.status || 'REVIEW_REQUIRED').toUpperCase();
  const frameworkList = formatWilsyFrameworkList(snapshot);

  return {
    receiptCount,
    sampleReceiptCount,
    reviewReceiptCount,
    sealedReceiptCount,
    clausesAnchored,
    posture,
    frameworkList,
    receiptMerkleRoot: contract.receiptMerkleRoot || overlay.receiptMerkleRoot || '',
    merkleRoot: contract.merkleRoot || overlay.merkleRoot || '',
    mode: snapshot?.mode || 'SAFE_SNAPSHOT_RECEIPT_CONTRACT',
    meta: `${sampleReceiptCount || receiptRows.length} sample ${posture.toLowerCase().replace(/_/g, ' ')} receipts · ${receiptCount} safe-window receipts · ${clausesAnchored} clause bindings · ${frameworkList}`
  };
}

/**
 * @function buildWilsySelectedReceipt
 * @description Selects the active receipt row for drilldown commands.
 * @collaboration Gives the command layer a stable receipt focus without mutating backend-owned receipt evidence.
 */
function buildWilsySelectedReceipt(receiptRows, selectedReceiptIndex = 0) {
  if (!Array.isArray(receiptRows) || receiptRows.length === 0) {
    return null;
  }

  const safeIndex = Math.min(Math.max(Number(selectedReceiptIndex) || 0, 0), receiptRows.length - 1);

  return receiptRows[safeIndex] || receiptRows[0] || null;
}

/**
 * @function buildWilsyReviewExplanation
 * @description Explains why the current proof posture is review-required rather than sealed.
 * @collaboration Makes review posture operator-readable without pretending that the browser can certify immutable seal status.
 */
function buildWilsyReviewExplanation({ posture, selectedReceipt, snapshot } = {}) {
  const receiptSummary = buildWilsyReceiptSummary(snapshot);
  const receiptStatus = String(selectedReceipt?.status || receiptSummary.posture || posture?.operationalState || 'REVIEW_REQUIRED')
    .toUpperCase();

  if (receiptStatus.includes('SEALED')) {
    return 'Receipt is sealed by backend contract. Browser display is read-only.';
  }

  if (receiptStatus.includes('REVIEW')) {
    return 'Review required because backend evidence is bound but not finalized as immutable seal. Run audit can request backend anchoring; final seal status remains server-owned.';
  }

  if (receiptStatus.includes('PENDING')) {
    return 'Receipt is pending because the backend has not returned a final receipt root or immutable anchor for this proof window.';
  }

  return `Current receipt posture: ${toWilsyExecutiveEvidenceLabel(receiptStatus)}. Backend remains the source of forensic truth.`;
}

/**
 * @function buildWilsyRegulatorPack
 * @description Builds a copy/export friendly regulator evidence pack from receipt contract, overlay and selected receipt data.
 * @collaboration Creates investor and regulator proof material without adding browser-side Merkle computation.
 */
function buildWilsyRegulatorPack({
  snapshot,
  posture,
  selectedReceipt,
  fullProofSnapshot
} = {}) {
  const receiptSummary = buildWilsyReceiptSummary(snapshot);
  const receiptRows = normalizeWilsyReceiptRows(snapshot);

  return {
    product: 'WILSY OS Forensic Merkle Showroom',
    version: WILSY_FORENSIC_MERKLE_SHOWROOM_VERSION,
    tenantId: posture?.tenantId || snapshot?.tenantId || 'wilsy-sovereign-root',
    generatedAt: new Date().toISOString(),
    mode: receiptSummary.mode,
    posture: receiptSummary.posture,
    frameworkList: receiptSummary.frameworkList,
    safeWindow: {
      receiptCount: receiptSummary.receiptCount,
      sampleReceiptCount: receiptSummary.sampleReceiptCount,
      reviewReceiptCount: receiptSummary.reviewReceiptCount,
      sealedReceiptCount: receiptSummary.sealedReceiptCount,
      clausesAnchored: receiptSummary.clausesAnchored
    },
    roots: {
      merkleRoot: posture?.merkleRoot || receiptSummary.merkleRoot || '',
      receiptMerkleRoot: posture?.receiptMerkleRoot || receiptSummary.receiptMerkleRoot || ''
    },
    anchor: {
      provider: posture?.anchorProvider || '',
      mode: posture?.anchorMode || '',
      qldbStatus: posture?.qldbStatus || 'RETIRED_NOT_USED',
      qldbEndOfSupport: posture?.qldbEndOfSupport || ''
    },
    selectedReceipt: selectedReceipt ? {
      receiptId: selectedReceipt.receiptId || '',
      recordId: selectedReceipt.recordId || '',
      eventType: selectedReceipt.eventType || '',
      traceId: selectedReceipt.traceId || '',
      status: selectedReceipt.status || '',
      receiptHash: selectedReceipt.receiptHash || '',
      leafHash: selectedReceipt.leafHash || '',
      eventSeal: selectedReceipt.eventSeal || '',
      compliance: selectedReceipt.compliance || []
    } : null,
    sampledReceipts: receiptRows.map(receipt => ({
      receiptId: receipt.receiptId || '',
      recordId: receipt.recordId || '',
      eventType: receipt.eventType || '',
      traceId: receipt.traceId || '',
      status: receipt.status || '',
      receiptHash: receipt.receiptHash || '',
      frameworks: (receipt.compliance || []).map(binding => binding.framework).filter(Boolean)
    })),
    fullProof: fullProofSnapshot ? {
      mode: fullProofSnapshot.mode,
      receiptCount: fullProofSnapshot.receiptContract?.receiptCount,
      clausesAnchored: fullProofSnapshot.receiptContract?.clausesAnchored,
      posture: fullProofSnapshot.receiptOverlay?.posture || fullProofSnapshot.receiptContract?.status
    } : null,
    note: 'Browser generated display pack only. Backend forensic routes remain authority for Merkle roots, receipt hashes, compliance bindings and immutable seal state.'
  };
}

/**
 * @function serializeWilsyRegulatorPack
 * @description Serializes the regulator evidence pack with stable indentation for copy/export actions.
 * @collaboration Keeps exported evidence readable for investor rooms, auditors and legal review.
 */
function serializeWilsyRegulatorPack(pack) {
  return JSON.stringify(pack || {}, null, 2);
}

/**
 * @function copyWilsyTextToClipboard
 * @description Copies command-layer text using Clipboard API with a textarea fallback.
 * @collaboration Makes regulator-pack copy resilient across Chrome focus states and local development security settings.
 */
async function copyWilsyTextToClipboard(textValue) {
  const serialized = String(textValue || '');

  if (navigator.clipboard?.writeText && document.hasFocus()) {
    await navigator.clipboard.writeText(serialized);
    return true;
  }

  const textarea = document.createElement('textarea');
  textarea.value = serialized;
  textarea.setAttribute('readonly', 'true');
  textarea.style.position = 'fixed';
  textarea.style.left = '-9999px';
  document.body.appendChild(textarea);
  textarea.select();
  const copied = document.execCommand('copy');
  document.body.removeChild(textarea);

  return copied;
}

/**
 * @function downloadWilsyEvidenceBundle
 * @description Downloads a regulator evidence bundle as a JSON artifact.
 * @collaboration Gives the showroom an audit-room export without adding backend file storage or frontend proof fabrication.
 */
function downloadWilsyEvidenceBundle(pack) {
  const payload = serializeWilsyRegulatorPack(pack);
  const blob = new Blob([payload], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const tenant = String(pack?.tenantId || 'wilsy').replace(/[^a-z0-9-]+/gi, '-').toLowerCase();
  const anchor = document.createElement('a');

  anchor.href = url;
  anchor.download = `${tenant}-forensic-regulator-pack-${Date.now()}.json`;
  polishWilsyForensicShowroomBackButtonR18AD2F(anchor);
  document.body.appendChild(anchor);
  anchor.click();
  document.body.removeChild(anchor);
  URL.revokeObjectURL(url);
}

/**
 * @function normalizeWilsyChainStatus
 * @description Builds a readable forensic posture model from R18C5 safe snapshot receipt contracts, overlays and anchor history.
 * @collaboration Converts backend receipt-contract states into honest cockpit language without faking Merkle roots or forcing full-chain browser replay.
 */
function normalizeWilsyChainStatus(snapshot) {
  const chain = snapshot?.chain || {};
  const run = snapshot?.run || {};
  const status = snapshot?.status || {};
  const anchorsPayload = snapshot?.anchors || {};
  const telemetry = snapshot?.telemetry || {};
  const anchors = normalizeWilsyAnchorList(snapshot);
  const receiptRows = normalizeWilsyReceiptRows(snapshot);
  const receiptContract = normalizeWilsyReceiptContract(snapshot);
  const receiptOverlay = normalizeWilsyReceiptOverlay(snapshot);
  const receiptSummary = buildWilsyReceiptSummary(snapshot);

  const merkleRoot = receiptContract.merkleRoot
    || receiptOverlay.merkleRoot
    || chain.merkleRoot
    || chain.rootHash
    || chain.result?.merkleRoot
    || run.merkleRoot
    || status.merkleRoot
    || anchors[0]?.merkleRoot
    || anchors[0]?.rootHash
    || null;

  const receiptMerkleRoot = receiptSummary.receiptMerkleRoot
    || chain.receiptMerkleRoot
    || run.receiptMerkleRoot
    || status.receiptMerkleRoot
    || null;

  const auditorStatus = receiptSummary.posture
    || chain.status
    || run.status
    || anchorsPayload.sourceStatus
    || status.status
    || 'SOURCE_PENDING';

  const sourceStatus = receiptOverlay.sourceStatus
    || chain.sourceStatus
    || run.sourceStatus
    || chain.integrity
    || run.integrity
    || auditorStatus
    || 'SOURCE_PENDING';

  const integrity = chain.integrity
    || run.integrity
    || (sourceStatus === 'DB_OFFLINE' ? 'DB_OFFLINE' : 'SOURCE_PENDING');

  const warning = chain.warning || run.warning || snapshot?.errors?.[0] || '';
  const algorithm = receiptContract.algorithm || chain.algorithm || run.algorithm || status.algorithm || 'SHA3-512';
  const anchorMode = receiptContract.anchorMode || status.anchorMode || run.anchorMode || chain.anchorMode || 'LOCAL_APPEND_ONLY_PENDING_WORM';
  const anchorProvider = receiptContract.anchorProvider || status.anchorProvider || run.anchorProvider || chain.anchorProvider || 'LOCAL_APPEND_ONLY';
  const qldbStatus = receiptContract.qldbStatus || chain.qldbStatus || run.qldbStatus || status.qldbStatus || 'RETIRED_NOT_USED';
  const qldbEndOfSupport = receiptContract.qldbEndOfSupport || chain.qldbEndOfSupport || run.qldbEndOfSupport || status.qldbEndOfSupport || '2025-07-31';
  const chainLength = Number(receiptSummary.receiptCount || chain.chainLength || chain.leafCount || chain.totalLeaves || chain.recordsVerified || chain.result?.leafCount || run.chainLength || 0);
  const driftCount = Number(chain.driftCount ?? chain.invalidCount ?? chain.result?.driftCount ?? run.driftCount ?? 0);
  const contractsVerified = Number(receiptSummary.receiptCount || status.contractsVerified || chain.contractsVerified || chain.recordsVerified || telemetry.contractsVerified || chainLength || 0);
  const activeSessions = Number(status.activeSessions ?? chain.activeSessions ?? run.activeSessions ?? telemetry.activeSessions ?? 0);
  const receiptsLogged = Number(receiptSummary.receiptCount || status.receiptsLogged || chain.receiptsLogged || run.receiptsLogged || telemetry.receiptsLogged || receiptRows.length || anchors.length || 0);
  const clausesAnchored = Number(receiptSummary.clausesAnchored || status.clausesAnchored || chain.clausesAnchored || run.clausesAnchored || telemetry.clausesAnchored || 0);
  const verified = Boolean(merkleRoot || receiptMerkleRoot);
  const reviewRequired = receiptSummary.posture.includes('REVIEW')
    || receiptRows.some(receipt => String(receipt?.status || '').toUpperCase().includes('REVIEW'))
    || driftCount > 0;

  const operationalState = reviewRequired
    ? 'REVIEW_REQUIRED'
    : merkleRoot || receiptMerkleRoot
      ? 'ROOT_VERIFIED'
      : integrity === 'DB_OFFLINE' || sourceStatus === 'DB_OFFLINE'
        ? 'FORENSIC_DB_OFFLINE'
        : auditorStatus === 'SOURCE_SILENT'
          ? 'SOURCE_SILENT'
          : 'AWAITING_EVIDENCE';

  const proofHealth = operationalState === 'REVIEW_REQUIRED'
    ? 'Review required · receipt contract bound by backend proof window'
    : operationalState === 'ROOT_VERIFIED'
      ? 'Sovereign root verified by Wilsy OS'
      : operationalState === 'FORENSIC_DB_OFFLINE'
        ? 'Evidence source is offline; audit service is reachable'
        : operationalState === 'SOURCE_SILENT'
          ? 'Audit service is live; no evidence stream returned yet'
          : 'Waiting for evidence stream';

  const rootState = reviewRequired
    ? 'review'
    : verified
      ? 'verified'
      : 'pending';

  const workerStatus = status.running === true
    ? 'Running'
    : status.running === false
      ? 'Idle'
      : (status.workerStatus || status.mode || receiptSummary.mode || 'Linked');

  return {
    tenantId: chain.tenantId || run.tenantId || snapshot?.tenantId || 'GLOBAL_ROOT',
    verified,
    merkleRoot,
    receiptMerkleRoot,
    receiptSummary,
    rootMode: receiptSummary.mode,
    frameworkList: receiptSummary.frameworkList,
    merkleLabel: merkleRoot ? compactWilsyProofValue(merkleRoot, 'ROOT') : 'Awaiting server root',
    rootDisplay: merkleRoot ? compactWilsyProofValue(merkleRoot, 'ROOT') : toWilsyExecutiveEvidenceLabel(operationalState),
    rootState,
    chainLength,
    leafCount: chainLength,
    contractsVerified,
    activeSessions,
    receiptsLogged,
    sampleReceiptCount: receiptSummary.sampleReceiptCount,
    reviewReceiptCount: receiptSummary.reviewReceiptCount,
    sealedReceiptCount: receiptSummary.sealedReceiptCount,
    clausesAnchored,
    driftCount,
    anchorCount: anchors.length,
    workerStatus,
    auditorStatus,
    sourceStatus,
    integrity,
    warning,
    algorithm,
    anchorMode,
    anchorProvider,
    qldbStatus,
    qldbEndOfSupport,
    localAnchorPath: status.localAnchorPath || '',
    operationalState,
    proofHealth
  };
}


/**
 * @function formatWilsyTelemetryTime
 * @description Formats backend refresh timestamps for compact cockpit telemetry labels.
 * @collaboration Lets operators see live refresh cadence without treating browser time as proof authority.
 */
function formatWilsyTelemetryTime(value) {
  if (!value) {
    return 'Awaiting refresh';
  }

  const parsed = new Date(value);

  if (Number.isNaN(parsed.getTime())) {
    return 'Refresh pending';
  }

  return parsed.toLocaleTimeString([], {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  });
}

/**
 * @function buildWilsyEvidenceItems
 * @description Builds the executive left-rail evidence stream from receipt rows, anchors, compliance posture and live audit state.
 * @collaboration Makes sampled backend receipts visible in the proof stream instead of falling back to anchor-only evidence.
 */
function buildWilsyEvidenceItems({ anchors, posture, lastRefreshAt, snapshot }) {
  const receiptRows = normalizeWilsyReceiptRows(snapshot);
  const receiptItems = receiptRows.slice(0, 7).map((receipt, index) => ({
    id: receipt?.receiptId || receipt?.recordId || `receipt-${index}`,
    label: buildWilsyReceiptCommandIdentity(receipt, index).title,
    title: receipt?.status ? toWilsyExecutiveEvidenceLabel(receipt.status) : 'Receipt witness',
    meta: buildWilsyReceiptCommandIdentity(receipt, index).meta,
    active: index === 0,
    icon: <ReceiptText size={15} />
  }));

  if (receiptItems.length > 0) {
    return receiptItems;
  }

  const anchorItems = anchors.slice(0, 7).map((anchor, index) => ({
    id: anchor?.blockId || anchor?.id || anchor?.anchorId || `anchor-${index}`,
    label: `Anchor ${index + 1}`,
    title: anchor?.blockId || anchor?.anchorId || `Anchor ${index + 1}`,
    meta: compactWilsyProofValue(anchor?.merkleRoot || anchor?.rootHash || anchor?.hash || anchor?.digest, 'HASH'),
    active: index === 0,
    icon: <ReceiptText size={15} />
  }));

  const fallbackItems = [
    {
      id: 'root',
      label: 'Root witness',
      title: posture.merkleRoot ? 'Sovereign root verified' : 'Awaiting root witness',
      meta: posture.merkleRoot ? compactWilsyProofValue(posture.merkleRoot, 'ROOT') : posture.proofHealth,
      active: true,
      icon: <Hash size={15} />
    },
    {
      id: 'audit',
      label: 'Audit service',
      title: toWilsyExecutiveEvidenceLabel(posture.auditorStatus),
      meta: `${posture.contractsVerified || posture.chainLength} records · ${posture.algorithm}`,
      active: false,
      icon: <RadioTower size={15} />
    },
    {
      id: 'anchor',
      label: 'Proof anchor',
      title: toWilsyExecutiveEvidenceLabel(posture.anchorProvider),
      meta: toWilsyExecutiveEvidenceLabel(posture.anchorMode),
      active: false,
      icon: <LockKeyhole size={15} />
    },
    {
      id: 'refresh',
      label: 'Live refresh',
      title: formatWilsyTelemetryTime(lastRefreshAt),
      meta: 'Telemetry pulse from forensic bridge',
      active: false,
      icon: <TimerReset size={15} />
    }
  ];

  return anchorItems.length > 0 ? anchorItems : fallbackItems;
}


/**
 * @function buildWilsyComplianceCards
 * @description Builds right-rail compliance and authority cards from the backend receipt contract.
 * @collaboration Ties POPIA, GDPR, SOC2 and WORM posture to receiptOverlay and receiptRows instead of anchor-count placeholders.
 */
function buildWilsyComplianceCards(posture, anchors, snapshot) {
  const receiptSummary = buildWilsyReceiptSummary(snapshot);

  return [
    {
      id: 'authority',
      label: 'Certificate Authority',
      title: posture.receiptMerkleRoot || posture.merkleRoot ? 'Root authority live' : 'Authority waiting',
      meta: posture.receiptMerkleRoot
        ? compactWilsyProofValue(posture.receiptMerkleRoot, 'RECEIPT-ROOT')
        : posture.merkleRoot
          ? compactWilsyProofValue(posture.merkleRoot, 'ROOT')
          : posture.proofHealth,
      icon: <BadgeCheck size={28} />
    },
    {
      id: 'policy',
      label: 'Policy Engine',
      title: 'Compliance receipts',
      meta: receiptSummary.meta,
      icon: <FileCheck2 size={28} />
    },
    {
      id: 'anchor',
      label: 'Append-only Anchor',
      title: toWilsyExecutiveEvidenceLabel(posture.anchorProvider),
      meta: `${toWilsyExecutiveEvidenceLabel(posture.anchorMode)} · ${receiptSummary.mode}`,
      icon: <LockKeyhole size={28} />
    }
  ];
}


/**
 * @function buildWilsyTechnicalRows
 * @description Builds a compact technical detail drawer for operators from receipt contract and proof posture.
 * @collaboration Moves backend detail out of the first-view executive surface while preserving forensic transparency.
 */
function buildWilsyTechnicalRows(posture, snapshot) {
  const receiptSummary = buildWilsyReceiptSummary(snapshot);

  return [
    ['Tenant scope', posture.tenantId],
    ['Snapshot mode', receiptSummary.mode],
    ['Evidence status', posture.receiptMerkleRoot || posture.merkleRoot ? toWilsyExecutiveEvidenceLabel(posture.operationalState) : toWilsyExecutiveEvidenceLabel(posture.operationalState)],
    ['Receipt posture', toWilsyExecutiveEvidenceLabel(receiptSummary.posture)],
    ['Sample receipts', `${receiptSummary.sampleReceiptCount} displayed`],
    ['Safe-window receipts', `${receiptSummary.receiptCount} receipt contracts`],
    ['Clause bindings', `${receiptSummary.clausesAnchored} compliance clauses`],
    ['Frameworks', receiptSummary.frameworkList],
    ['Audit service', toWilsyExecutiveEvidenceLabel(posture.auditorStatus)],
    ['Data source', toWilsyExecutiveEvidenceLabel(posture.sourceStatus)],
    ['Integrity posture', posture.driftCount > 0 || receiptSummary.posture.includes('REVIEW') ? 'Review required' : 'No drift detected'],
    ['Hash method', posture.algorithm],
    ['Anchor provider', toWilsyExecutiveEvidenceLabel(posture.anchorProvider)],
    ['Anchor mode', toWilsyExecutiveEvidenceLabel(posture.anchorMode)],
    ['Receipt Merkle root', posture.receiptMerkleRoot || 'Awaiting receipt root'],
    ['Sovereign root', posture.merkleRoot || 'Awaiting server root'],
    ['Operator note', posture.warning ? toWilsyExecutiveEvidenceLabel(posture.warning) : 'No warning returned']
  ];
}


/**
 * @function WilsyEvidenceStreamItem
 * @description Renders a single evidence-stream row in the left proof rail.
 * @collaboration Keeps evidence legible while the center of the cockpit focuses on the Sovereign Root.
 */
function WilsyEvidenceStreamItem({ item }) {

  /**
   * @function handleRequestWilsyBackendSeal
   * @description Requests a backend-owned production seal decision for the current safe receipt window.
   * @collaboration Keeps immutable seal authority on the server and only displays backend blockers in the browser command layer.
   */
  const handleRequestWilsyBackendSeal = async () => {
    setFullProofRunning(true);
    setCommandNotice('Requesting backend seal decision · browser authority disabled');

    try {
      const sealPacket = await sealWilsyMerkleSafeWindow({
        tenantId: 'wilsy-sovereign-root',
        limit: 250,
        receiptLimit: 3,
        actor: 'wilsy-founder-console',
        reason: 'SAFE_WINDOW_SEAL_REQUEST'
      });
      const sealStatus = sealPacket?.sealStatus || 'SEAL_DECISION_RETURNED';
      const blockers = Array.isArray(sealPacket?.sealDecision?.eligibility?.blockers)
        ? sealPacket.sealDecision.eligibility.blockers
        : [];
      const authority = sealPacket?.productionSeal?.browserAuthority === false
        ? 'backend authority'
        : 'authority review';

      setFullProofSnapshot(sealPacket);
      setSealDecisionSnapshot(sealPacket);
      setSealDecisionHudOpen(true);

      if (typeof window !== 'undefined') {
        window.__wilsySealHudOpenRequested = true;
      }
      window.__wilsyLastSealDecision = sealPacket;
      setCommandNotice(formatWilsySealDecisionCommandNotice({
        sealStatus,
        blockers,
        authority
      }));
    } catch (error) {
      setCommandNotice(`Backend seal decision failed · ${error?.message || 'forensic route unavailable'}`);
    } finally {
      setFullProofRunning(false);
    }
  };

  return (
    <article className={`${styles.evidenceItem} ${item.active ? styles.evidenceItemActive : ''}`}>
      <span className={styles.evidenceItemIcon}>{item.icon}</span>
      <span className={styles.evidenceItemCopy}>
        <small className={styles.evidenceItemLabel}>{item.label}</small>
        <strong className={styles.evidenceItemTitle}>{item.title}</strong>
        <span className={styles.evidenceItemMeta}>{item.meta}</span>
      </span>
    </article>
  );
}

/**
 * @function WilsyComplianceAuthorityCard
 * @description Renders a right-rail authority card for compliance posture.
 * @collaboration Lets executives understand proof authority without reading backend response objects.
 */
function WilsyComplianceAuthorityCard({ card }) {
  return (
    <article className={styles.complianceAuthorityCard}>
      <span className={styles.complianceAuthorityIcon}>{card.icon}</span>
      <span className={styles.complianceAuthorityCopy}>
        <small className={styles.complianceAuthorityLabel}>{card.label}</small>
        <strong className={styles.complianceAuthorityTitle}>{card.title}</strong>
        <span className={styles.complianceAuthorityMeta}>{card.meta}</span>
      </span>
    </article>
  );
}

/**
 * @function WilsyTechnicalDetailRow
 * @description Renders one operator detail row in the technical drawer.
 * @collaboration Preserves backend transparency without letting operational terms dominate the executive first view.
 */
function WilsyTechnicalDetailRow({ row }) {
  return (
    <span className={styles.technicalRow}>
      <small>{row[0]}</small>
      <strong>{row[1]}</strong>
    </span>
  );
}

/**
 * @function WilsySovereignRootHero
 * @description Renders the central Sovereign Root hero and live audit action.
 * @collaboration Makes the Merkle root the visual focal point of the showroom instead of a crowded status grid.
 */
function WilsySovereignRootHero({
  posture,
  auditReceipt,
  runningAudit,
  onRunAudit
}) {
  const rootStateClass = posture.rootState === 'verified'
    ? styles.rootHaloVerified
    : posture.rootState === 'review'
      ? styles.rootHaloReview
      : styles.rootHaloPending;


  return (
    <section className={styles.rootHero} data-wilsy-forensic-root-visualizer="R18D-RECEIPT-CONTRACT-HERO">
      <div className={styles.rootHeroHeader}>
        <span className={styles.rootHeroEyebrow}>Sovereign Root</span>
        <h2 className={styles.rootHeroTitle}>
          {posture.merkleRoot ? 'Root verified' : 'Awaiting server root'}
        </h2>
        <p className={styles.rootHeroCopy}>{posture.proofHealth}</p>
      </div>

      <div className={`${styles.rootHalo} ${rootStateClass}`} aria-label="Sovereign Merkle root visualizer">
        <span className={styles.rootOrbitTop}>
          <Hash size={24} />
        </span>
        <span className={styles.rootOrbitLine} />
        <article className={styles.rootCore}>
          <small>Merkle root</small>
          <code>{posture.merkleRoot || 'Awaiting server root'}</code>
        </article>
      </div>

      <div className={styles.rootHeroMetrics}>
        <span>
          <small>Verified records</small>
          <strong>{posture.contractsVerified || posture.chainLength}</strong>
        </span>
        <span>
          <small>Receipts logged</small>
          <strong>{posture.receiptsLogged || posture.anchorCount}</strong>
        </span>
        <span>
          <small>Hash method</small>
          <strong>{posture.algorithm}</strong>
        </span>
      </div>

      <div className={styles.rootHeroAction}>
        <span className={styles.rootHeroReceipt}>
          <ReceiptText size={14} />
          {auditReceipt || posture.proofHealth}
        </span>
        <button
          type="button"
          className={styles.runButton}
          data-wilsy-forensic-run-audit="true"
          disabled={runningAudit}
          onClick={onRunAudit}
        >
          <RefreshCw size={15} />
          {runningAudit ? 'Running audit' : 'Run audit'}
        </button>
      </div>
    </section>
  );
}

/**
 * @function buildWilsyReceiptCommandIdentity
 * @description Converts sampled receipt rows into operator-grade command lane labels.
 * @collaboration Replaces generic Receipt 1/2/3 labels with truthful forensic proof lanes without claiming browser-side sealing.
 */
function buildWilsyReceiptCommandIdentity(receipt, index = 0) {
  const status = String(receipt?.status || 'REVIEW_REQUIRED').toUpperCase();
  const frameworks = (receipt?.compliance || [])
    .map(binding => binding?.framework)
    .filter(Boolean)
    .map(framework => String(framework).toUpperCase())
    .join(' · ');
  const hash = compactWilsyProofValue(receipt?.receiptHash || receipt?.leafHash || receipt?.eventSeal, 'HASH');

  const commandLanes = [
    {
      title: 'Root witness',
      meta: `${hash} · Backend root evidence`
    },
    {
      title: 'Clause bound',
      meta: `${frameworks || 'POPIA · GDPR · SOC2 · WORM'} · Compliance binding`
    },
    {
      title: status.includes('REVIEW') ? 'Seal decision' : 'Seal witness',
      meta: `${toWilsyExecutiveEvidenceLabel(status)} · Append-only posture`
    }
  ];

  return commandLanes[index] || {
    title: `Evidence lane ${index + 1}`,
    meta: `${hash} · ${toWilsyExecutiveEvidenceLabel(status)}`
  };
}


/**
 * @function normalizeWilsySealBlockers
 * @description Normalizes backend seal blockers into stable panel rows.
 * @collaboration Makes backend-owned seal refusal readable to investors, operators and engineers without changing proof authority.
 */
function normalizeWilsySealBlockers(sealPacket = {}) {
  const blockers = Array.isArray(sealPacket?.sealDecision?.eligibility?.blockers)
    ? sealPacket.sealDecision.eligibility.blockers
    : [];

  return blockers.length ? blockers : ['NO_BACKEND_SEAL_DECISION_SELECTED'];
}

/**
 * @function normalizeWilsySealRecommendations
 * @description Normalizes backend seal recommendations into operator next-action rows.
 * @collaboration Keeps the UI focused on backend remediation actions instead of implying the browser can force a seal.
 */
function normalizeWilsySealRecommendations(sealPacket = {}) {
  const recommendations = Array.isArray(sealPacket?.sealDecision?.eligibility?.recommendations)
    ? sealPacket.sealDecision.eligibility.recommendations
    : [];

  return recommendations.length
    ? recommendations
    : ['REQUEST_BACKEND_SEAL_DECISION'];
}

/**
 * @function buildWilsySealDecisionSummary
 * @description Builds a persistent seal decision summary from the latest backend seal packet.
 * @collaboration Converts route-owned seal output into a regulator-readable panel while preserving backend-only seal authority.
 */
function buildWilsySealDecisionSummary(sealPacket = {}) {
  const receiptContract = sealPacket?.receiptContract || {};
  const productionSeal = sealPacket?.productionSeal || {};
  const sealDecision = sealPacket?.sealDecision || {};
  const eligibility = sealDecision?.eligibility || {};

  return {
    routeVersion: sealPacket?.routeVersion || 'SEAL_ROUTE_PENDING',
    sealWorkflowVersion: sealPacket?.sealWorkflowVersion || 'SEAL_WORKFLOW_PENDING',
    sealStatus: sealPacket?.sealStatus || sealDecision?.sealStatus || 'NO_BACKEND_SEAL_DECISION',
    immutableSeal: sealPacket?.immutableSeal === true || sealDecision?.immutableSeal === true,
    canSeal: sealDecision?.canSeal === true || eligibility?.canSeal === true,
    backendAuthority: productionSeal?.backendAuthority === true,
    browserAuthority: productionSeal?.browserAuthority === true,
    fallbackAuthority: productionSeal?.fallbackAuthority || 'AUDITOR_SERVICE_OR_ROUTE_VERIFIER',
    receiptCount: Number(receiptContract?.receiptCount || eligibility?.counts?.receiptCount || 0),
    reviewReceiptCount: Number(receiptContract?.reviewReceiptCount || eligibility?.counts?.reviewReceiptCount || 0),
    sealedReceiptCount: Number(receiptContract?.sealedReceiptCount || eligibility?.counts?.sealedReceiptCount || 0),
    clausesAnchored: Number(receiptContract?.clausesAnchored || eligibility?.counts?.clausesAnchored || 0),
    blockers: normalizeWilsySealBlockers(sealPacket),
    recommendations: normalizeWilsySealRecommendations(sealPacket)
  };
}


/**
 * @function formatWilsySealBlockerLabel
 * @description Converts backend seal blocker constants into readable operator labels.
 * @collaboration Keeps backend truth intact while preventing raw machine constants from degrading the command layer experience.
 */
function formatWilsySealBlockerLabel(blocker = '') {
  const blockerLabels = {
    CHAIN_NOT_VERIFIED: 'chain not verified',
    REVIEW_RECEIPTS_PRESENT: 'review receipts present',
    NOT_ALL_RECEIPTS_BACKEND_SEALED: 'receipts not backend sealed',
    NO_RECEIPTS_AVAILABLE: 'no receipts available',
    MISSING_MERKLE_OR_RECEIPT_ROOT: 'missing proof root'
  };

  return blockerLabels[blocker] || String(blocker || 'review required')
    .toLowerCase()
    .replaceAll('_', ' ');
}

/**
 * @function formatWilsySealDecisionCommandNotice
 * @description Formats a backend seal decision into production-grade command-layer copy.
 * @collaboration Shows the operator a clear seal outcome while the persistent panel keeps the full backend blocker evidence.
 */
function formatWilsySealDecisionCommandNotice({
  sealStatus = 'SEAL_DECISION_RETURNED',
  blockers = [],
  authority = 'authority review'
} = {}) {
  const normalizedBlockers = Array.isArray(blockers) ? blockers : [];
  const sealLabel = String(sealStatus).includes('BLOCKED')
    ? 'Backend seal blocked'
    : String(sealStatus).includes('SEALED')
      ? 'Backend seal confirmed'
      : 'Backend seal decision returned';
  const authorityLabel = String(authority).includes('backend')
    ? 'Backend authority confirmed · Browser authority disabled'
    : 'Authority review pending';
  const blockerSummary = normalizedBlockers.length
    ? normalizedBlockers.map(formatWilsySealBlockerLabel).join(' · ')
    : 'no blockers returned';

  return normalizedBlockers.length
    ? `${sealLabel} · ${normalizedBlockers.length} blockers · ${blockerSummary} · ${authorityLabel}`
    : `${sealLabel} · ${authorityLabel}`;
}


/**
 * @function formatWilsySealPanelStatusLabel
 * @description Converts backend seal status constants into boardroom-readable seal decision copy.
 * @collaboration Preserves backend seal truth while making the forensic HUD understandable to operators, investors and engineers.
 */
function formatWilsySealPanelStatusLabel(status = '') {
  const statusLabels = {
    SEAL_BLOCKED_REVIEW_REQUIRED: 'Seal blocked for review',
    SEAL_BLOCKED_MISSING_ROOT: 'Seal blocked · proof root missing',
    SEAL_BLOCKED_NO_RECEIPTS: 'Seal blocked · no receipts available',
    SEAL_READY: 'Seal ready for backend finalization',
    SEALED_BY_BACKEND_AUTHORITY: 'Sealed by backend authority',
    NO_BACKEND_SEAL_DECISION: 'No backend seal decision'
  };

  return statusLabels[status] || String(status || 'Seal decision pending')
    .toLowerCase()
    .replaceAll('_', ' ');
}

/**
 * @function formatWilsySealPanelBlockerLabel
 * @description Converts backend blocker constants into readable seal blocker labels.
 * @collaboration Keeps raw blocker semantics intact while removing machine-code language from the production panel.
 */
function formatWilsySealPanelBlockerLabel(blocker = '') {
  const blockerLabels = {
    CHAIN_NOT_VERIFIED: 'chain not verified',
    REVIEW_RECEIPTS_PRESENT: 'review receipts present',
    NOT_ALL_RECEIPTS_BACKEND_SEALED: 'receipts not backend sealed',
    NO_RECEIPTS_AVAILABLE: 'no receipts available',
    MISSING_MERKLE_OR_RECEIPT_ROOT: 'missing Merkle or receipt root',
    NO_BACKEND_SEAL_DECISION_SELECTED: 'backend seal decision pending'
  };

  return blockerLabels[blocker] || String(blocker || 'review required')
    .toLowerCase()
    .replaceAll('_', ' ');
}

/**
 * @function formatWilsySealPanelRecommendationLabel
 * @description Converts backend recommendation constants into readable next-action labels.
 * @collaboration Makes remediation actions clear without changing backend proof or seal authority.
 */
function formatWilsySealPanelRecommendationLabel(recommendation = '') {
  const recommendationLabels = {
    RESOLVE_REVIEW_RECEIPTS: 'resolve review receipts',
    REPLAY_BACKEND_CHAIN: 'replay backend chain',
    CONFIRM_RECEIPT_MERKLE_ROOT: 'confirm receipt Merkle root',
    RETRY_SEAL_AFTER_VERIFIED_AUDIT: 'retry after verified audit',
    APPEND_ONLY_FINALIZATION_ALLOWED: 'append-only finalization allowed',
    REQUEST_BACKEND_SEAL_DECISION: 'request backend seal decision'
  };

  return recommendationLabels[recommendation] || String(recommendation || 'review required')
    .toLowerCase()
    .replaceAll('_', ' ');
}

/**
 * @function formatWilsySealPanelAuthorityLabel
 * @description Converts backend authority source constants into readable authority labels.
 * @collaboration Clarifies whether the seal decision came from the route verifier or final auditor service.
 */
function formatWilsySealPanelAuthorityLabel(authority = '') {
  const authorityLabels = {
    ROUTE_BACKEND_VERIFIER: 'Route backend verifier',
    AUDITOR_SERVICE_OR_ROUTE_VERIFIER: 'Auditor service or route verifier'
  };

  return authorityLabels[authority] || String(authority || 'backend verifier')
    .toLowerCase()
    .replaceAll('_', ' ');
}

/**
 * @function WilsySealDecisionPanel
 * @description Renders the latest backend seal decision as a persistent forensic artifact.
 * @collaboration Keeps seal state visible after command execution and proves that immutable sealing is backend-owned, not browser-owned.
 */
function WilsySealDecisionPanel({ sealPacket, onDismiss = () => {} }) {
  const decision = buildWilsySealDecisionSummary(sealPacket);
  const blockerText = decision.blockers.map(formatWilsySealPanelBlockerLabel).join(' · ');
  const recommendationText = decision.recommendations.map(formatWilsySealPanelRecommendationLabel).join(' · ');
  const sealStatusLabel = formatWilsySealPanelStatusLabel(decision.sealStatus);
  const authorityLabel = formatWilsySealPanelAuthorityLabel(decision.fallbackAuthority);

  return (
    <section
      data-wilsy-seal-decision-panel="R18T-PERSISTENT-SEAL-DECISION"
      style={{
        display: 'grid',
        gridTemplateColumns: 'minmax(260px, 1fr) minmax(260px, 1.4fr) minmax(220px, 1fr)',
        gap: '12px',
        margin: '12px 0',
        padding: '14px',
        border: '1px solid rgba(255, 213, 116, 0.26)',
        borderRadius: '22px',
        background: 'linear-gradient(135deg, rgba(255, 213, 116, 0.08), rgba(255, 92, 123, 0.08), rgba(0, 0, 0, 0.22))',
        boxShadow: '0 22px 70px rgba(0, 0, 0, 0.34)'
      }}
    >
      <button
        type="button"
        data-wilsy-seal-decision-dismiss="R18Z2"
        aria-label="Dismiss backend seal decision"
        onClick={onDismiss}
        style={{
          position: 'absolute',
          top: '10px',
          right: '12px',
          zIndex: 4,
          width: '30px',
          height: '30px',
          borderRadius: '999px',
          border: '1px solid rgba(255, 218, 132, 0.30)',
          background: 'rgba(0, 0, 0, 0.42)',
          color: '#ffe59b',
          cursor: 'pointer',
          fontWeight: 900,
          lineHeight: 1
        }}
      >
        ×
      </button>
      <div
        style={{
          padding: '14px',
          border: '1px solid rgba(255, 255, 255, 0.11)',
          borderRadius: '18px',
          background: 'rgba(0, 0, 0, 0.22)'
        }}
      >
        <span
          style={{
            display: 'block',
            fontSize: '10px',
            letterSpacing: '0.22em',
            textTransform: 'uppercase',
            color: 'rgba(255, 242, 201, 0.62)',
            marginBottom: '7px'
          }}
        >
          Seal Decision
        </span>
        <strong
          style={{
            display: 'block',
            color: decision.immutableSeal ? '#20f5a4' : '#ffdd8a',
            fontSize: '16px',
            lineHeight: 1.2,
            textTransform: 'uppercase'
          }}
        >
          {sealStatusLabel}
        </strong>
        <small
          style={{
            display: 'block',
            marginTop: '8px',
            color: 'rgba(255, 255, 255, 0.62)',
            lineHeight: 1.45
          }}
        >
          {decision.routeVersion} · {decision.sealWorkflowVersion}
        </small>
      </div>

      <div
        style={{
          padding: '14px',
          border: '1px solid rgba(255, 92, 123, 0.22)',
          borderRadius: '18px',
          background: 'rgba(80, 22, 33, 0.18)'
        }}
      >
        <span
          style={{
            display: 'block',
            fontSize: '10px',
            letterSpacing: '0.22em',
            textTransform: 'uppercase',
            color: 'rgba(255, 242, 201, 0.62)',
            marginBottom: '7px'
          }}
        >
          Backend Blockers
        </span>
        <strong
          style={{
            display: 'block',
            color: '#fff4d6',
            fontSize: '14px',
            lineHeight: 1.45
          }}
        >
          {blockerText}
        </strong>
        <small
          style={{
            display: 'block',
            marginTop: '8px',
            color: 'rgba(255, 255, 255, 0.62)',
            lineHeight: 1.45
          }}
        >
          Next action · {recommendationText}
        </small>
      </div>

      <div
        style={{
          padding: '14px',
          border: '1px solid rgba(32, 245, 164, 0.20)',
          borderRadius: '18px',
          background: 'rgba(12, 46, 33, 0.16)'
        }}
      >
        <span
          style={{
            display: 'block',
            fontSize: '10px',
            letterSpacing: '0.22em',
            textTransform: 'uppercase',
            color: 'rgba(255, 242, 201, 0.62)',
            marginBottom: '7px'
          }}
        >
          Authority Boundary
        </span>
        <strong
          style={{
            display: 'block',
            color: '#20f5a4',
            fontSize: '14px',
            lineHeight: 1.45
          }}
        >
          Backend authority: {decision.backendAuthority ? 'TRUE' : 'PENDING'}
        </strong>
        <small
          style={{
            display: 'block',
            marginTop: '8px',
            color: 'rgba(255, 255, 255, 0.62)',
            lineHeight: 1.45
          }}
        >
          Browser authority: {decision.browserAuthority ? 'TRUE' : 'FALSE'} · {authorityLabel}
        </small>
        <small
          style={{
            display: 'block',
            marginTop: '8px',
            color: 'rgba(255, 255, 255, 0.62)',
            lineHeight: 1.45
          }}
        >
          Receipts {decision.receiptCount} · Review {decision.reviewReceiptCount} · Sealed {decision.sealedReceiptCount} · Clauses {decision.clausesAnchored}
        </small>
      </div>
    </section>
  );
}

/**
 * @function WilsyForensicCommandStrip
 * @description Renders receipt drilldown, regulator pack, export, review explanation, full proof and seal-window commands.
 * @collaboration Turns the proof deck into an operator-grade forensic command surface while backend services remain the cryptographic authority.
 */
function WilsyForensicCommandStrip({
  receiptRows,
  selectedReceipt,
  selectedReceiptIndex,
  commandNotice,
  fullProofRunning,
  onSelectReceipt,
  onCopyRegulatorPack,
  onExportEvidenceBundle,
  onExplainReview,
  onRunFullProof,
  onSealReceipts
}) {
  const selectedFrameworks = selectedReceipt?.compliance?.map(binding => binding.framework).filter(Boolean).join(' · ') || 'POPIA · GDPR · SOC2 · WORM';

  return (
    <section className={styles.commandLayer || styles.technicalDrawer} data-wilsy-forensic-command-layer="R18H-COMMAND-LAYER">
      <div className={styles.commandHeader || styles.railHeader}>
        <span>
          <small>Forensic command layer</small>
          <strong>Regulator-grade receipt operations</strong>
        </span>
        <em>{commandNotice}</em>
      </div>

      <div className={styles.commandGrid || styles.technicalGrid}>
        <button type="button" className={styles.commandButton || styles.topAction} onClick={onExplainReview}>
          <AlertTriangle size={15} />
          Explain review
        </button>
        <button type="button" className={styles.commandButton || styles.topAction} onClick={onCopyRegulatorPack}>
          <FileCheck2 size={15} />
          Copy regulator pack
        </button>
        <button type="button" className={styles.commandButton || styles.topAction} onClick={onExportEvidenceBundle}>
          <DatabaseZap size={15} />
          Export evidence bundle
        </button>
        <button type="button" className={styles.commandButton || styles.topAction} disabled={fullProofRunning} onClick={onRunFullProof}>
          <GitBranch size={15} />
          {fullProofRunning ? 'Running full proof' : 'Run full proof'}
        </button>
        <button type="button" className={styles.commandButton || styles.topAction} onClick={onSealReceipts}>
          <LockKeyhole size={15} />
          Request backend seal
        </button>
      </div>

      <article className={styles.receiptDrilldown || styles.technicalDrawer} data-wilsy-forensic-receipt-drilldown="R18H-RECEIPT-DRILLDOWN">
        <div className={styles.receiptSelector || styles.evidenceList}>
          {receiptRows.map((receipt, index) => (
            <button
              key={receipt?.receiptId || receipt?.recordId || `receipt-selector-${index}`}
              type="button"
              className={`${styles.receiptSelectorButton || styles.evidenceItem} ${index === selectedReceiptIndex ? (styles.receiptSelectorButtonActive || styles.evidenceItemActive) : ''}`}
              onClick={() => {
                onSelectReceipt(index);
                if (index === 2 && typeof onSealSafeWindow === 'function') {
                  onSealSafeWindow();
                }
              }}
              title={buildWilsyReceiptCommandIdentity(receipt, index).meta}
              aria-label={buildWilsyReceiptCommandIdentity(receipt, index).meta}
            >
              <ReceiptText size={14} />
              {buildWilsyReceiptCommandIdentity(receipt, index).title}
            </button>
          ))}
        </div>

        <div className={styles.receiptDrilldownGrid || styles.technicalGrid}>
          <span>
            <small>Status</small>
            <strong>{toWilsyExecutiveEvidenceLabel(selectedReceipt?.status || 'REVIEW_REQUIRED')}</strong>
          </span>
          <span>
            <small>Receipt hash</small>
            <strong>{compactWilsyProofValue(selectedReceipt?.receiptHash, 'HASH')}</strong>
          </span>
          <span>
            <small>Record</small>
            <strong>{selectedReceipt?.recordId || 'Record pending'}</strong>
          </span>
          <span>
            <small>Trace</small>
            <strong>{selectedReceipt?.traceId || 'Trace pending'}</strong>
          </span>
          <span>
            <small>Event type</small>
            <strong>{selectedReceipt?.eventType || 'Forensic event'}</strong>
          </span>
          <span>
            <small>Frameworks</small>
            <strong>{selectedFrameworks}</strong>
          </span>
        </div>
      </article>
    </section>
  );
}

/**
 * @function WilsyTechnicalDrawer
 * @description Renders optional technical details below the executive proof deck.
 * @collaboration Keeps operator-grade diagnostics accessible without degrading the executive view.
 */
function WilsyTechnicalDrawer({ rows }) {
  return (
    <details className={styles.technicalDrawer}>
      <summary>
        <span>
          <ChevronDown size={15} />
          Operator detail
        </span>
        <small>Audit posture, anchor mode, source state, storage notes</small>
      </summary>
      <div className={styles.technicalGrid}>
        {rows.map(row => (
          <WilsyTechnicalDetailRow key={row[0]} row={row} />
        ))}
      </div>
    </details>
  );
}

/**
 * @function WilsyForensicMerkleShowroom
 * @description Renders an isolated backend-bound forensic Merkle showroom with a three-zone Sovereign Root layout.
 * @collaboration Proves the Merkle cockpit UX before any adoption inside Account Command Center, CRM, Executive, Founder, Finance, HR, or Security dashboards.
 */
export default function WilsyForensicMerkleShowroom({
  tenantId = 'wilsy-sovereign-root',
  limit = 3
}) {
  const [snapshot, setSnapshot] = useState(null);
  const [loading, setLoading] = useState(true);
  const [runningAudit, setRunningAudit] = useState(false);
  const [lastAction, setLastAction] = useState('Snapshot pending');
  const [lastRefreshAt, setLastRefreshAt] = useState(null);
  const [auditReceipt, setAuditReceipt] = useState('');
  const [selectedReceiptIndex, setSelectedReceiptIndex] = useState(0);
  const [commandNotice, setCommandNotice] = useState('Forensic Proof Lab / Experimental · Account Command Center card pending');
  const [fullProofRunning, setFullProofRunning] = useState(false);
  const [fullProofSnapshot, setFullProofSnapshot] = useState(null);

    const [sealDecisionSnapshot, setSealDecisionSnapshot] = useState(null);

    const [sealDecisionHudOpen, setSealDecisionHudOpen] = useState(false);
const posture = useMemo(() => normalizeWilsyChainStatus(snapshot), [snapshot]);
  const anchors = useMemo(() => normalizeWilsyAnchorList(snapshot), [snapshot]);
  const evidenceItems = useMemo(() => buildWilsyEvidenceItems({
    anchors,
    posture,
    lastRefreshAt,
    snapshot
  }), [anchors, posture, lastRefreshAt, snapshot]);
  const complianceCards = useMemo(() => buildWilsyComplianceCards(posture, anchors, snapshot), [posture, anchors, snapshot]);
  const technicalRows = useMemo(() => buildWilsyTechnicalRows(posture, snapshot), [posture, snapshot]);
  const receiptRows = useMemo(() => normalizeWilsyReceiptRows(snapshot), [snapshot]);
  const selectedReceipt = useMemo(() => buildWilsySelectedReceipt(receiptRows, selectedReceiptIndex), [receiptRows, selectedReceiptIndex]);
  const reviewExplanation = useMemo(() => buildWilsyReviewExplanation({ posture, selectedReceipt, snapshot }), [posture, selectedReceipt, snapshot]);
  const regulatorPack = useMemo(() => buildWilsyRegulatorPack({
    snapshot,
    posture,
    selectedReceipt,
    fullProofSnapshot
  }), [snapshot, posture, selectedReceipt, fullProofSnapshot]);


  useEffect(() => {
    if (selectedReceiptIndex > 0 && selectedReceiptIndex >= receiptRows.length) {
      setSelectedReceiptIndex(0);
    }
  }, [receiptRows.length, selectedReceiptIndex]);

  const topState = posture.merkleRoot
    ? 'Root verified'
    : posture.driftCount > 0
      ? 'Review required'
      : 'Waiting for root';

  useEffect(() => {
    window.scrollTo({ top: 0, left: 0, behavior: 'auto' });
  }, []);

  useEffect(() => {
    const controller = new AbortController();

    /**
     * @function loadWilsyForensicSnapshot
     * @description Loads the backend-bound forensic Merkle cockpit snapshot for the active tenant.
     * @collaboration Connects the isolated showroom to wilsyForensicMerkleClient while keeping Merkle authority server-side.
     */
    const loadWilsyForensicSnapshot = async () => {
      setLoading(true);

      try {
        const nextSnapshot = await buildWilsyMerkleCockpitSnapshot({
          tenantId,
          limit,
          replayLimit: 250,
          signal: controller.signal
        });
        const nextPosture = normalizeWilsyChainStatus(nextSnapshot);

        setSnapshot(nextSnapshot);
        setLastRefreshAt(new Date().toISOString());
        setAuditReceipt(nextPosture.merkleRoot
          ? `Sovereign root witness ${compactWilsyProofValue(nextPosture.merkleRoot, 'ROOT')}`
          : nextPosture.proofHealth);
        setLastAction('Live proof snapshot loaded');
      } catch (error) {
        setSnapshot({
          tenantId,
          errors: [error.message || 'Forensic snapshot failed']
        });
        setLastRefreshAt(new Date().toISOString());
        setAuditReceipt('Server receipt unavailable');
        setLastAction('Snapshot failed');
      } finally {
        setLoading(false);
      }
    };

    loadWilsyForensicSnapshot();

    return () => controller.abort();
  }, [tenantId, limit]);

  useEffect(() => {
    const controller = new AbortController();
    const telemetryRefresh = window.setInterval(async () => {
      if (runningAudit) {
        return;
      }

      try {
        const nextSnapshot = await buildWilsyMerkleCockpitSnapshot({
          tenantId,
          limit,
          replayLimit: 250,
          signal: controller.signal
        });
        const nextPosture = normalizeWilsyChainStatus(nextSnapshot);

        setSnapshot(nextSnapshot);
        setLastRefreshAt(new Date().toISOString());
        setAuditReceipt(nextPosture.merkleRoot
          ? `Live sovereign witness ${compactWilsyProofValue(nextPosture.merkleRoot, 'ROOT')}`
          : nextPosture.proofHealth);
        setLastAction('Live proof telemetry refreshed');
      } catch (error) {
        setLastRefreshAt(new Date().toISOString());
        setAuditReceipt('Live telemetry refresh failed');
        setSnapshot(previous => ({
          ...(previous || {}),
          tenantId,
          errors: [error.message || 'Live telemetry refresh failed']
        }));
      }
    }, 60000);

    return () => {
      controller.abort();
      window.clearInterval(telemetryRefresh);
    };
  }, [tenantId, limit, runningAudit]);

  /**
   * @function handleRunWilsyForensicAudit
   * @description Runs a backend Merkle audit cycle and refreshes the isolated cockpit snapshot.
   * @collaboration Keeps the run-audit command bound to backend authority instead of browser-owned proof logic.
   */
  const handleRunWilsyForensicAudit = async () => {
    setRunningAudit(true);

    try {
      await runWilsyMerkleAuditCycle({
        tenantId,
        anchor: true,
        limit,
        replayLimit: 250
      });

      const nextSnapshot = await buildWilsyMerkleCockpitSnapshot({
        tenantId,
        limit
      });
      const nextPosture = normalizeWilsyChainStatus(nextSnapshot);

      setSnapshot(nextSnapshot);
      setLastRefreshAt(new Date().toISOString());
      setAuditReceipt(nextPosture.merkleRoot
        ? `Audit returned ${compactWilsyProofValue(nextPosture.merkleRoot, 'ROOT')}`
        : `Audit completed · ${nextPosture.proofHealth}`);
      setLastAction(nextPosture.merkleRoot
        ? 'Audit completed with sovereign root'
        : 'Audit completed; server root awaiting evidence');
    } catch (error) {
      setSnapshot(previous => ({
        ...(previous || {}),
        tenantId,
        errors: [
          ...((previous && previous.errors) || []),
          error.message || 'Manual audit failed'
        ]
      }));
      setLastRefreshAt(new Date().toISOString());
      setAuditReceipt('Audit failed before server root returned');
      setLastAction('Audit failed');
    } finally {
      setRunningAudit(false);
    }
  };

  /**
   * @function handleSelectWilsyReceipt
   * @description Selects a sampled receipt for drilldown review.
   * @collaboration Lets operators inspect receipt-level evidence without mutating backend forensic state.
   */
  const handleSelectWilsyReceipt = (index) => {
    setSelectedReceiptIndex(index);
    const laneTitles = ['Root witness', 'Clause bound', 'Seal decision'];
    setCommandNotice(`${laneTitles[index] || 'Evidence lane'} lane selected · backend proof drilldown ready`);
  };

  /**
   * @function handleCopyWilsyRegulatorPack
   * @description Copies the current regulator evidence pack to the clipboard.
   * @collaboration Gives legal, investor and compliance reviewers a portable JSON proof summary from backend-owned evidence.
   */
  const handleCopyWilsyRegulatorPack = async () => {
    try {
      await copyWilsyTextToClipboard(serializeWilsyRegulatorPack(regulatorPack));
      setCommandNotice('Regulator pack copied');
    } catch (error) {
      setCommandNotice(error.message || 'Regulator pack copy failed');
    }
  };

  /**
   * @function handleExportWilsyEvidenceBundle
   * @description Downloads the current regulator pack as a local JSON evidence bundle.
   * @collaboration Turns receipt-contract posture into a portable artifact without browser-side proof fabrication.
   */
  const handleExportWilsyEvidenceBundle = () => {
    downloadWilsyEvidenceBundle(regulatorPack);
    setCommandNotice('Evidence bundle exported');
  };

  /**
   * @function handleExplainWilsyReview
   * @description Displays the current review-required explanation in the command layer.
   * @collaboration Makes backend review posture clear while avoiding false claims that the browser sealed the receipt.
   */
  const handleExplainWilsyReview = () => {
    setCommandNotice(reviewExplanation);
  };

  /**
   * @function handleRunWilsyFullProof
   * @description Runs a deliberate full proof replay request on demand.
   * @collaboration Keeps expensive replayLimit=5000 work behind an explicit operator command instead of live dashboard polling.
   */
  const handleRunWilsyFullProof = async () => {
    setFullProofRunning(true);
    setCommandNotice('Full proof replay requested');

    try {
      const nextFullProof = await buildWilsyMerkleCockpitSnapshot({
        tenantId,
        limit,
        replayLimit: 5000
      });

      setFullProofSnapshot(nextFullProof);
      setCommandNotice(`Full proof returned ${nextFullProof.receiptContract?.receiptCount || 0} receipts and ${nextFullProof.receiptContract?.clausesAnchored || 0} clause bindings`);
    } catch (error) {
      setCommandNotice(error.message || 'Full proof replay failed');
    } finally {
      setFullProofRunning(false);
    }
  };

  /**
   * @function handleSealWilsySafeWindow
   * @description Requests backend audit anchoring for the safe proof window and refreshes the receipt contract.
   * @collaboration Advances append-only sealing workflow through backend authority without claiming browser-owned immutability.
   */
  const handleSealWilsySafeWindow = async () => {
    setCommandNotice('Safe-window seal request submitted');
    await handleRunWilsyForensicAudit();
  };


  /**
   * @function handleRequestWilsyBackendSealScoped
   * @description Requests a backend-owned seal decision and persists it into the visible seal decision panel.
   * @collaboration Keeps browser authority disabled while surfacing backend blockers from the production seal endpoint.
   */
  const handleRequestWilsyBackendSealScoped = async () => {
    setFullProofRunning(true);
    setCommandNotice('Requesting backend seal decision · browser authority disabled');

    try {
      const sealPacket = await sealWilsyMerkleSafeWindow({
        tenantId: 'wilsy-sovereign-root',
        limit: 250,
        receiptLimit: 3,
        actor: 'wilsy-founder-console',
        reason: 'SAFE_WINDOW_SEAL_REQUEST'
      });
      const sealStatus = sealPacket?.sealStatus || 'SEAL_DECISION_RETURNED';
      const blockers = Array.isArray(sealPacket?.sealDecision?.eligibility?.blockers)
        ? sealPacket.sealDecision.eligibility.blockers
        : [];
      const authority = sealPacket?.productionSeal?.browserAuthority === false
        ? 'backend authority'
        : 'authority review';

      setFullProofSnapshot(sealPacket);
      setSealDecisionSnapshot(sealPacket);
      setSealDecisionHudOpen(true);
      setSealDecisionSnapshot(sealPacket);

      if (typeof window !== 'undefined') {
        window.__wilsyLastSealDecision = sealPacket;
      }

      setCommandNotice(formatWilsySealDecisionCommandNotice({
        sealStatus,
        blockers,
        authority
      }));
    } catch (error) {
      setCommandNotice(`Backend seal decision failed · ${error?.message || 'forensic route unavailable'}`);
    } finally {
      setFullProofRunning(false);
    }
  };

  /**
   * @function handleWilsyForensicRootClick
   * @description Routes seal-related command clicks to the backend seal decision handler.
   * @collaboration Makes Seal Decision and Request Backend Seal operational even when nested visual controls change layout.
   */
  const handleWilsyForensicRootClick = (event) => {
    const commandTarget = event?.target?.closest?.('button, [role="button"], [data-wilsy-receipt-lane], [data-wilsy-command-action]');
    const commandText = String(commandTarget?.innerText || commandTarget?.textContent || '').toUpperCase();

    if (commandText.includes('REQUEST BACKEND SEAL') || commandText.includes('SEAL DECISION')) {
      handleRequestWilsyBackendSealScoped();
    }
  };

  return (
    <section
      className={styles.root}
      data-wilsy-forensic-merkle-showroom="true"
      data-wilsy-forensic-merkle-version={WILSY_FORENSIC_MERKLE_SHOWROOM_VERSION}
      onClick={handleWilsyForensicRootClick}
      data-wilsy-forensic-lab-status={WILSY_FORENSIC_PROOF_LAB_STATUS}
      data-wilsy-account-integration-status={WILSY_FORENSIC_ACCOUNT_INTEGRATION_STATUS}
    >
      <div className={styles.shell} data-wilsy-forensic-layout-shell="R18D-RECEIPT-CONTRACT-DECK-SHELL">
        <header className={styles.topBar} data-wilsy-forensic-command-bar="R18D-RECEIPT-CONTRACT-TOPBAR">
          <span className={styles.topBrand}>
            <strong>WILSY OS Forensic Merkle Showroom</strong>
            <small>Forensic Proof Lab / Experimental · Safe snapshot receipt contract · SHA3-512 · POPIA · GDPR · SOC2 · WORM</small>
          </span>

          <span className={styles.topStatus}>
            <ShieldCheck size={15} />
            {topState}
          </span>

          <button
            type="button"
            className={styles.topAction}
            data-wilsy-forensic-run-audit="true"
            disabled={runningAudit}
            onClick={handleRunWilsyForensicAudit}
          >
            <RefreshCw size={15} />
            {runningAudit ? 'Running' : 'Run audit'}
          </button>
        </header>

        <main className={styles.showroomDeck} data-wilsy-forensic-main-grid="R18D-RECEIPT-CONTRACT-DECK-MAIN">
          <aside className={styles.evidenceRail} data-wilsy-forensic-evidence-rail="R18D-RECEIPT-EVIDENCE-STREAM">
            <div className={styles.railHeader}>
              <h2>Evidence Stream</h2>
              <small>{loading ? 'Loading proof stream' : `${posture.contractsVerified || posture.chainLength} records verified`}</small>
            </div>

            <div className={styles.evidenceList}>
              {evidenceItems.map(item => (
                <WilsyEvidenceStreamItem key={item.id} item={item} />
              ))}
            </div>

            {snapshot?.errors?.length > 0 && (
              <div className={styles.inlineWarning}>
                <AlertTriangle size={14} />
                {snapshot.errors.map(error => toWilsyExecutiveEvidenceLabel(error)).join(' · ')}
              </div>
            )}
          </aside>

          <WilsySovereignRootHero
            posture={posture}
            auditReceipt={auditReceipt || lastAction}
            runningAudit={runningAudit}
            onRunAudit={handleRunWilsyForensicAudit}
          />

          <aside className={styles.complianceRail} data-wilsy-forensic-authority-rail="R18D-COMPLIANCE-RECEIPT-AUTHORITY-RAIL">
            <div className={styles.railHeader}>
              <h2>Compliance Receipts</h2>
              <small>{formatWilsyTelemetryTime(lastRefreshAt)}</small>
            </div>

            <div className={styles.complianceStack}>
              {complianceCards.map(card => (
                <WilsyComplianceAuthorityCard key={card.id} card={card} />
              ))}
            </div>
          </aside>
        </main>


        <WilsyForensicCommandStrip
          receiptRows={receiptRows}
          selectedReceipt={selectedReceipt}
          selectedReceiptIndex={selectedReceiptIndex}
          commandNotice={commandNotice}
          fullProofRunning={fullProofRunning}
          onSelectReceipt={handleSelectWilsyReceipt}
          onCopyRegulatorPack={handleCopyWilsyRegulatorPack}
          onExportEvidenceBundle={handleExportWilsyEvidenceBundle}
          onExplainReview={handleExplainWilsyReview}
          onRunFullProof={handleRunWilsyFullProof}
          onSealReceipts={handleSealWilsySafeWindow}
        
            onSealSafeWindow={handleRequestWilsyBackendSealScoped}/>
          {(sealDecisionHudOpen && (sealDecisionSnapshot || fullProofSnapshot?.sealDecision)) ? (
            <div
              data-wilsy-seal-decision-panel-mounted="R18U"
              data-wilsy-seal-panel-state="BACKEND_DECISION_VISIBLE"
              style={{
                gridColumn: '1 / -1',
                margin: '12px 0 0',
                position: 'relative',
                zIndex: 3
              }}
            >
              <WilsySealDecisionPanel sealPacket={sealDecisionSnapshot || fullProofSnapshot} onDismiss={() => setSealDecisionHudOpen(false)} />
            </div>
          ) : null}

        <WilsyTechnicalDrawer rows={technicalRows} />

        <footer className={styles.boundaryFooter}>
          <span>
            <Activity size={14} />
            Forensic Proof Lab / Experimental
          </span>
          <span>
            <Sparkles size={14} />
            Account card pending
          </span>
          <span>
            <ShieldCheck size={14} />
            No frontend Merkle duplication
          </span>
        </footer>
      </div>
    </section>
  );
}

export {
  WILSY_FORENSIC_MERKLE_SHOWROOM_VERSION,
  WILSY_FORENSIC_ACCOUNT_INTEGRATION_STATUS,
  WILSY_FORENSIC_PROOF_LAB_STATUS,
  buildWilsyRegulatorPack,
  buildWilsyReviewExplanation,
  buildWilsySelectedReceipt,
  copyWilsyTextToClipboard,
  downloadWilsyEvidenceBundle,
  serializeWilsyRegulatorPack,
  WilsyForensicCommandStrip,
  buildWilsyComplianceCards,
  buildWilsyEvidenceItems,
  buildWilsyReceiptCommandIdentity,
  buildWilsyReceiptSummary,
  formatWilsyFrameworkList,
  buildWilsyTechnicalRows,
  compactWilsyProofValue,
  formatWilsyTelemetryTime,
  normalizeWilsyReceiptContract,
  normalizeWilsyReceiptOverlay,
  normalizeWilsyReceiptRows,
  normalizeWilsyAnchorList,
  normalizeWilsyChainStatus,
  toWilsyExecutiveEvidenceLabel
};


export const WILSY_FORENSIC_SHOWROOM_BACK_BUTTON_RUNTIME_VERSION = 'R18AD2K-OPEN-CLICK-RETURNS-TO-DASHBOARD';

/**
 * @function resolveWilsyForensicShowroomBackHrefR18AD2E
 * @description Resolves the safe dashboard return URL for the forensic proof lab back button.
 * @collaboration Keeps Wilsy OS dashboard-first while allowing founder/root users to enter and leave the proof lab deliberately.
 */
function resolveWilsyForensicShowroomBackHrefR18AD2E() {
  if (typeof window === 'undefined') {
    return '/';
  }

  const params = new URLSearchParams(window.location.search);
  const candidate = String(params.get('returnTo') || '/').trim();

  if (!candidate || candidate.startsWith('http://') || candidate.startsWith('https://') || candidate.startsWith('//')) {
    return '/';
  }

  if (candidate.startsWith('/wilsy-lab/forensic-merkle')) {
    return '/';
  }

  return candidate.startsWith('/') ? candidate : '/';
}

/**
 * @function installWilsyForensicShowroomBackButtonR18AD2E
 * @description Installs a route-scoped back button only when the browser is on the forensic proof lab route.
 * @collaboration Avoids global DOM observers, avoids dashboard hijacking, and provides deterministic return to the Wilsy OS dashboard.
 */

/**
 * @function polishWilsyForensicShowroomBackButtonR18AD2F
 * @description Converts the showroom return control into a compact orb with explicit open/close behavior.
 * @collaboration Preserves the existing route-only return runtime while removing the permanent billboard from the proof lab.
 */
function polishWilsyForensicShowroomBackButtonR18AD2F(anchor) {
  if (!anchor) {
    return;
  }

  anchor.setAttribute('data-wilsy-showroom-back-button-runtime', WILSY_FORENSIC_SHOWROOM_BACK_BUTTON_RUNTIME_VERSION);
  anchor.setAttribute('data-wilsy-return-open', anchor.getAttribute('data-wilsy-return-open') || 'false');

  const orbitBase = {
    position: 'fixed',
    left: '26px',
    bottom: '26px',
    top: 'auto',
    zIndex: '2147483000',
    display: 'inline-flex',
    alignItems: 'center',
    justifyContent: 'flex-start',
    border: '1px solid rgba(255, 220, 124, 0.46)',
    borderRadius: '999px',
    background: 'radial-gradient(circle at 35% 25%, rgba(255,241,175,0.30), transparent 36%), linear-gradient(135deg, rgba(5,7,12,0.98), rgba(20,18,12,0.94))',
    color: '#fff1af',
    fontFamily: 'Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
    fontWeight: '900',
    textDecoration: 'none',
    boxShadow: '0 24px 72px rgba(0,0,0,0.50), inset 0 1px 0 rgba(255,255,255,0.10)',
    backdropFilter: 'blur(18px)',
    webkitBackdropFilter: 'blur(18px)',
    cursor: 'pointer',
    overflow: 'hidden',
    transition: 'width 180ms ease, min-width 180ms ease, padding 180ms ease, transform 180ms ease, box-shadow 180ms ease'
  };

  const collapsed = {
    ...orbitBase,
    width: '56px',
    minWidth: '56px',
    maxWidth: '56px',
    height: '56px',
    minHeight: '56px',
    padding: '0',
    gap: '0'
  };

  const open = {
    ...orbitBase,
    width: 'min(430px, calc(100vw - 56px))',
    minWidth: '360px',
    maxWidth: 'calc(100vw - 56px)',
    height: '64px',
    minHeight: '64px',
    padding: '8px 18px 8px 10px',
    gap: '12px'
  };

  const renderClosed = () => {
    Object.assign(anchor.style, collapsed);
    anchor.innerHTML = '<span style="display:grid;place-items:center;width:56px;height:56px;font-size:28px;line-height:1;transform:translateY(-1px);">←</span>';
    anchor.setAttribute('aria-label', 'Open return to command center control');
    anchor.setAttribute('aria-expanded', 'false');
    anchor.setAttribute('data-wilsy-return-open', 'false');
  };

  const renderOpen = () => {
    Object.assign(anchor.style, open);
    anchor.innerHTML = [
      '<span style="display:grid;place-items:center;width:40px;height:40px;border-radius:999px;background:rgba(255,234,160,0.13);border:1px solid rgba(255,220,124,0.34);font-size:22px;line-height:1;">←</span>',
      '<span style="display:grid;gap:4px;line-height:1;">',
      '<strong style="font-size:11px;letter-spacing:0.16em;text-transform:uppercase;color:#fff1af;">Return to Command Center</strong>',
      '<small style="font-size:9px;letter-spacing:0.14em;text-transform:uppercase;color:rgba(255,255,255,0.58);">Click again to exit · Esc closes · Browser authority false</small>',
      '</span>'
    ].join('');
    anchor.setAttribute('aria-label', 'Return to Wilsy dashboard');
    anchor.setAttribute('aria-expanded', 'true');
    anchor.setAttribute('data-wilsy-return-open', 'true');
  };

  if (!anchor.dataset.wilsyReturnControlBound) {
    anchor.dataset.wilsyReturnControlBound = 'true';

    anchor.addEventListener('click', event => {
      const isOpen = anchor.getAttribute('data-wilsy-return-open') === 'true';

      event.preventDefault();
      event.stopImmediatePropagation();

      if (isOpen) {
        window.location.assign(anchor.getAttribute('href') || '/');
        return;
      }

      renderOpen();
    }, true);

    window.addEventListener('keydown', event => {
      if (event.key === 'Escape' && anchor.getAttribute('data-wilsy-return-open') === 'true') {
        renderClosed();
      }
    });
  }

  if (anchor.getAttribute('data-wilsy-return-open') === 'true') {
    renderOpen();
  } else {
    renderClosed();
  }
}

function installWilsyForensicShowroomBackButtonR18AD2E() {
  if (typeof window === 'undefined' || typeof document === 'undefined') {
    return;
  }

  const selector = '[data-wilsy-showroom-back-button="R18AD2D"]';
  const isShowroomRoute = window.location.pathname.startsWith('/wilsy-lab/forensic-merkle');

  if (!isShowroomRoute) {
    document.querySelectorAll(selector).forEach(node => node.remove());
    return;
  }

  const existingButton = document.querySelector(selector);

  if (existingButton) {
    polishWilsyForensicShowroomBackButtonR18AD2F(existingButton);
    return;
  }

  const backHref = resolveWilsyForensicShowroomBackHrefR18AD2E();
  const anchor = document.createElement('a');

  anchor.href = backHref;
  anchor.textContent = '← Back to dashboard';
  anchor.setAttribute('data-wilsy-showroom-back-button', 'R18AD2D');
  anchor.setAttribute('data-wilsy-showroom-back-button-runtime', WILSY_FORENSIC_SHOWROOM_BACK_BUTTON_RUNTIME_VERSION);
  anchor.setAttribute('aria-label', 'Back to Wilsy dashboard');
  anchor.addEventListener('click', event => {
    event.preventDefault();
    window.location.assign(backHref);
  });

  anchor.style.position = 'fixed';
  anchor.style.left = '24px';
  anchor.style.top = '104px';
  anchor.style.zIndex = '2147483000';
  anchor.style.display = 'inline-flex';
  anchor.style.alignItems = 'center';
  anchor.style.justifyContent = 'center';
  anchor.style.minHeight = '42px';
  anchor.style.padding = '0 18px';
  anchor.style.border = '1px solid rgba(255, 220, 124, 0.58)';
  anchor.style.borderRadius = '999px';
  anchor.style.background = 'linear-gradient(135deg, rgba(255, 234, 160, 0.98), rgba(212, 175, 55, 0.94))';
  anchor.style.color = '#050505';
  anchor.style.fontSize = '11px';
  anchor.style.fontWeight = '900';
  anchor.style.letterSpacing = '0.14em';
  anchor.style.textTransform = 'uppercase';
  anchor.style.textDecoration = 'none';
  anchor.style.boxShadow = '0 18px 50px rgba(0, 0, 0, 0.32)';
  anchor.style.whiteSpace = 'nowrap';
  anchor.style.cursor = 'pointer';

  document.body.appendChild(anchor);
}

if (typeof window !== 'undefined') {
  window.requestAnimationFrame(installWilsyForensicShowroomBackButtonR18AD2E);
  window.setTimeout(installWilsyForensicShowroomBackButtonR18AD2E, 250);
}

