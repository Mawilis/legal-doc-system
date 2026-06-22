/* eslint-disable */
import crypto from 'node:crypto';
import fs from 'node:fs/promises';
import path from 'node:path';
import mongoose from 'mongoose';
import CaseModel from '../models/Case.js';
import AccountComplianceEvidenceReceipt from '../models/AccountComplianceEvidenceReceipt.js';

export const ACCOUNT_EVIDENCE_COMMAND_VERSION = 'R18AD30-DEFENSIBLE-EVIDENCE-BACKBONE';

/**
 * @function normalizeEvidenceTenantId
 * @description Normalizes tenant identity for evidence receipts and regulator bundles.
 * @param {string} tenantId - Candidate tenant identifier.
 * @returns {string} Safe tenant identifier.
 * @collaboration Keeps receipt generation scoped to one tenant and prevents cross-tenant evidence display.
 */
export function normalizeEvidenceTenantId(tenantId = 'wilsy-sovereign-root') {
  return String(tenantId || 'wilsy-sovereign-root').trim() || 'wilsy-sovereign-root';
}

/**
 * @function createEvidenceDigest
 * @description Creates a deterministic SHA3-512 digest for receipt payloads.
 * @param {unknown} payload - Payload to hash.
 * @returns {string} Hex digest.
 * @collaboration Produces stable evidence hashes without browser authority or fabricated compliance posture.
 */
export function createEvidenceDigest(payload) {
  return crypto.createHash('sha3-512').update(JSON.stringify(payload)).digest('hex');
}

/**
 * @function computeAccountEvidenceMerkleRoot
 * @description Computes a Merkle root from receipt hashes.
 * @param {string[]} hashes - Receipt hash list.
 * @returns {string} Merkle root or empty string when no hashes exist.
 * @collaboration Gives Account Command Center a real receipt-root signal once backend evidence exists.
 */
export function computeAccountEvidenceMerkleRoot(hashes = []) {
  const cleanHashes = hashes.map((hash) => String(hash || '').trim()).filter(Boolean);

  if (cleanHashes.length === 0) {
    return '';
  }

  let level = [...cleanHashes];

  while (level.length > 1) {
    const nextLevel = [];

    for (let index = 0; index < level.length; index += 2) {
      const left = level[index];
      const right = level[index + 1] || left;
      nextLevel.push(createEvidenceDigest({ left, right }));
    }

    level = nextLevel;
  }

  return level[0];
}

/**
 * @function ensureCaseModelRegistered
 * @description Ensures the Case model is registered in the current Mongoose runtime.
 * @returns {Object} Registration status.
 * @collaboration Stops CaseComplianceService from failing with MODEL_UNREGISTERED while preserving real case data semantics.
 */
export function ensureCaseModelRegistered() {
  const registered = Boolean(mongoose.models.Case || CaseModel);

  return {
    registered,
    modelName: 'Case',
    collection: CaseModel.collection?.name || 'cases',
    source: 'server/models/Case.js',
  };
}

/**
 * @function countTenantCases
 * @description Counts tenant cases without creating any case records.
 * @param {string} tenantId - Tenant identifier.
 * @returns {Promise<number>} Case count.
 * @collaboration Gives evidence receipts live case-model context without fake cases.
 */
export async function countTenantCases(tenantId = 'wilsy-sovereign-root') {
  const safeTenantId = normalizeEvidenceTenantId(tenantId);

  if (mongoose.connection.readyState !== 1) {
    return 0;
  }

  return CaseModel.countDocuments({ tenantId: safeTenantId });
}

/**
 * @function listAccountComplianceEvidenceReceipts
 * @description Lists real tenant-scoped evidence receipts.
 * @param {Object} options - Query options.
 * @param {string} options.tenantId - Tenant identifier.
 * @param {number} options.limit - Maximum receipt count.
 * @returns {Promise<Array>} Receipt rows.
 * @collaboration Feeds Account Command Center from persisted backend evidence, not static UI data.
 */
export async function listAccountComplianceEvidenceReceipts({
  tenantId = 'wilsy-sovereign-root',
  limit = 250,
} = {}) {
  const safeTenantId = normalizeEvidenceTenantId(tenantId);
  const safeLimit = Math.max(1, Math.min(Number(limit || 250), 1000));

  if (mongoose.connection.readyState !== 1) {
    return [];
  }

  return AccountComplianceEvidenceReceipt.find({ tenantId: safeTenantId })
    .sort({ generatedAt: -1 })
    .limit(safeLimit)
    .lean();
}

/**
 * @function buildComplianceBindings
 * @description Builds explicit compliance bindings for an evidence receipt.
 * @param {Object} payload - Receipt payload.
 * @param {string} evidenceHash - Evidence hash.
 * @returns {Array<Object>} Compliance binding rows.
 * @collaboration Maps backend evidence to POPIA, FICA, audit defensibility and regulator-export concerns.
 */
export function buildComplianceBindings(payload = {}, evidenceHash = '') {
  return [
    {
      framework: 'POPIA',
      control: 'privacy-command',
      status: 'BACKEND_EVIDENCE_RECEIPT_CREATED',
      evidenceHash,
      tenantId: payload.tenantId,
    },
    {
      framework: 'FICA',
      control: 'audit-defensibility',
      status: 'BACKEND_EVIDENCE_RECEIPT_CREATED',
      evidenceHash,
      tenantId: payload.tenantId,
    },
    {
      framework: 'AUDIT',
      control: 'chain-of-custody',
      status: 'BACKEND_EVIDENCE_RECEIPT_CREATED',
      evidenceHash,
      tenantId: payload.tenantId,
    },
    {
      framework: 'REGULATOR_EXPORT',
      control: 'regulator-access',
      status: 'BACKEND_EVIDENCE_RECEIPT_CREATED',
      evidenceHash,
      tenantId: payload.tenantId,
    },
  ];
}

/**
 * @function createAccountComplianceEvidenceReceipt
 * @description Creates one explicit backend evidence receipt and recalculates the tenant Merkle root.
 * @param {Object} options - Receipt options.
 * @param {string} options.tenantId - Tenant identifier.
 * @param {string} options.actor - Actor responsible for generation.
 * @param {string} options.reason - Reason for evidence generation.
 * @returns {Promise<Object>} Created receipt summary.
 * @collaboration Converts the Account Command Center from evidence-pending to evidence-backed without fabricating compliance data.
 */
export async function createAccountComplianceEvidenceReceipt({
  tenantId = 'wilsy-sovereign-root',
  actor = 'system',
  reason = 'manual-production-evidence-generation',
} = {}) {
  const safeTenantId = normalizeEvidenceTenantId(tenantId);
  const caseRegistration = ensureCaseModelRegistered();
  const caseCount = await countTenantCases(safeTenantId);
  const existingReceipts = await listAccountComplianceEvidenceReceipts({
    tenantId: safeTenantId,
    limit: 1000,
  });
  const previousMerkleRoot = existingReceipts[0]?.merkleRoot || '';

  const generatedAt = new Date();
  const payload = {
    version: ACCOUNT_EVIDENCE_COMMAND_VERSION,
    tenantId: safeTenantId,
    actor,
    reason,
    generatedAt: generatedAt.toISOString(),
    caseRegistration,
    caseCount,
    controls: [
      'privacy-command',
      'regulatory-ledger',
      'audit-defensibility',
      'chain-of-custody',
      'regulator-access',
      'tenant-ledger',
    ],
    noFakeData: true,
    browserAuthority: false,
    backendAuthority: true,
  };

  const evidenceHash = createEvidenceDigest(payload);
  const receiptId = `ACR_${generatedAt.toISOString().replace(/[-:.TZ]/g, '')}_${evidenceHash.slice(0, 16)}`;
  const allHashes = [...existingReceipts.map((receipt) => receipt.evidenceHash), evidenceHash]
    .filter(Boolean)
    .reverse();
  const merkleRoot = computeAccountEvidenceMerkleRoot(allHashes);
  const complianceBindings = buildComplianceBindings(payload, evidenceHash);

  const receipt = await AccountComplianceEvidenceReceipt.create({
    tenantId: safeTenantId,
    receiptId,
    reason,
    actor,
    source: 'account-compliance-evidence-command',
    status: 'SEALED',
    evidenceHash,
    merkleRoot,
    previousMerkleRoot,
    payload,
    complianceBindings,
    generatedAt,
  });

  return {
    ok: true,
    receiptId: receipt.receiptId,
    tenantId: safeTenantId,
    status: receipt.status,
    evidenceHash: receipt.evidenceHash,
    merkleRoot: receipt.merkleRoot,
    previousMerkleRoot: receipt.previousMerkleRoot,
    complianceBindings: receipt.complianceBindings,
    generatedAt: receipt.generatedAt,
  };
}

/**
 * @function getAccountComplianceEvidenceSnapshot
 * @description Reads current tenant evidence posture for Account Command Center.
 * @param {Object} options - Snapshot options.
 * @param {string} options.tenantId - Tenant identifier.
 * @param {number} options.limit - Maximum receipt count.
 * @returns {Promise<Object>} Evidence snapshot.
 * @collaboration Populates receipt count, Merkle root and regulator-bundle readiness from real persisted receipts.
 */
export async function getAccountComplianceEvidenceSnapshot({
  tenantId = 'wilsy-sovereign-root',
  limit = 250,
} = {}) {
  const safeTenantId = normalizeEvidenceTenantId(tenantId);
  const caseRegistration = ensureCaseModelRegistered();
  const receipts = await listAccountComplianceEvidenceReceipts({ tenantId: safeTenantId, limit });
  const latestReceipt = receipts[0] || null;
  const hashes = receipts
    .map((receipt) => receipt.evidenceHash)
    .filter(Boolean)
    .reverse();
  const computedRoot = computeAccountEvidenceMerkleRoot(hashes);
  const merkleRoot = latestReceipt?.merkleRoot || computedRoot || '';
  const receiptCount = receipts.length;

  return {
    available: true,
    version: ACCOUNT_EVIDENCE_COMMAND_VERSION,
    tenantId: safeTenantId,
    source: 'account_compliance_evidence_receipts',
    caseRegistration,
    receiptCount,
    sealedReceiptCount: receipts.filter((receipt) => receipt.status === 'SEALED').length,
    clausesAnchored: receipts.reduce(
      (total, receipt) => total + Number(receipt.complianceBindings?.length || 0),
      0
    ),
    merkleRoot,
    compactRoot: merkleRoot
      ? `${merkleRoot.slice(0, 18)}…${merkleRoot.slice(-12)}`
      : 'Root pending',
    receiptSealStatus: receiptCount > 0 ? 'SEALED' : 'NO_RECEIPTS_YET',
    regulatorBundleReady: receiptCount > 0,
    latestReceipt: latestReceipt
      ? {
          receiptId: latestReceipt.receiptId,
          evidenceHash: latestReceipt.evidenceHash,
          merkleRoot: latestReceipt.merkleRoot,
          generatedAt: latestReceipt.generatedAt,
          status: latestReceipt.status,
        }
      : null,
  };
}

/**
 * @function generateAccountRegulatorBundle
 * @description Writes a tenant-scoped regulator bundle from real account compliance evidence receipts.
 * @param {Object} options - Bundle options.
 * @param {string} options.tenantId - Tenant identifier.
 * @param {string} options.outputDir - Output directory.
 * @returns {Promise<Object>} Bundle metadata and file path.
 * @collaboration Produces a regulator-reviewable artifact without including fabricated compliance records.
 */
export async function generateAccountRegulatorBundle({
  tenantId = 'wilsy-sovereign-root',
  outputDir = path.resolve(process.cwd(), 'server/exports/regulator-bundles'),
} = {}) {
  const safeTenantId = normalizeEvidenceTenantId(tenantId);
  const snapshot = await getAccountComplianceEvidenceSnapshot({
    tenantId: safeTenantId,
    limit: 1000,
  });
  const receipts = await listAccountComplianceEvidenceReceipts({
    tenantId: safeTenantId,
    limit: 1000,
  });
  const generatedAt = new Date().toISOString();

  await fs.mkdir(outputDir, { recursive: true });

  const bundle = {
    ok: true,
    version: ACCOUNT_EVIDENCE_COMMAND_VERSION,
    type: 'WILSY_ACCOUNT_COMPLIANCE_REGULATOR_BUNDLE',
    tenantId: safeTenantId,
    generatedAt,
    noFakeData: true,
    browserAuthority: false,
    backendAuthority: true,
    evidenceComplete: snapshot.receiptCount > 0,
    proof: {
      receiptCount: snapshot.receiptCount,
      sealedReceiptCount: snapshot.sealedReceiptCount,
      clausesAnchored: snapshot.clausesAnchored,
      merkleRoot: snapshot.merkleRoot,
      compactRoot: snapshot.compactRoot,
      receiptSealStatus: snapshot.receiptSealStatus,
    },
    receipts: receipts.map((receipt) => ({
      receiptId: receipt.receiptId,
      status: receipt.status,
      source: receipt.source,
      evidenceHash: receipt.evidenceHash,
      merkleRoot: receipt.merkleRoot,
      previousMerkleRoot: receipt.previousMerkleRoot,
      complianceBindings: receipt.complianceBindings,
      generatedAt: receipt.generatedAt,
    })),
  };

  const bundleHash = createEvidenceDigest(bundle);
  const filename = `WILSY_REGULATOR_BUNDLE_${safeTenantId}_${generatedAt.replace(/[-:.TZ]/g, '')}_${bundleHash.slice(0, 12)}.json`;
  const filepath = path.join(outputDir, filename);

  await fs.writeFile(filepath, `${JSON.stringify({ ...bundle, bundleHash }, null, 2)}\n`, 'utf8');

  return {
    ok: true,
    tenantId: safeTenantId,
    filepath,
    bundleHash,
    receiptCount: snapshot.receiptCount,
    merkleRoot: snapshot.merkleRoot,
    evidenceComplete: snapshot.receiptCount > 0,
  };
}
