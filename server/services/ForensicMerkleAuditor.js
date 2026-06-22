/* eslint-disable */
import mongoose from 'mongoose';
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - FORENSIC MERKLE AUDITOR [V57.1.0-REVIEW-SAFE-RECEIPTS]                                                                         ║
 * ║ [NIST SHA-3 | HASH-CHAIN REPLAY | MERKLE ROOTS | SEALED RECEIPTS | COMPLIANCE BINDINGS | WORM READY]                               ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 57.1.0-REVIEW-SAFE-RECEIPTS | PRODUCTION READY | INSTITUTIONAL NON-REPUDIATION                                                  ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/services/ForensicMerkleAuditor.js                                      ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                  ║
 * ║ • Wilson Khanyezi (CEO/Lead Architect) - Required continuous cryptographic proof, external immutable anchoring, and production       ║
 * ║   readiness beyond prototype UI features.                                                                                            ║
 * ║ • AI Engineering (Codex) - ARCHITECTED: Replaced retired QLDB assumptions with current WORM-ready anchoring, deterministic replay,   ║
 * ║   and Revenue Ledger compatible status packets.                                                                                      ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import crypto from 'node:crypto';
import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import axios from 'axios';
import ForensicLog from '../models/ForensicLog.js';
import loggerRaw from '../utils/logger.js';
import { broadcastTelemetry } from '../utils/telemetryHelper.js';

const logger = loggerRaw.default || loggerRaw;
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const WILSY_FORENSIC_RECEIPT_CONTRACT_VERSION = 'R18A-SEALED-RECEIPT-CONTRACT';

const WILSY_FORENSIC_COMPLIANCE_BINDINGS = [
  {
    framework: 'POPIA',
    jurisdiction: 'ZA',
    clause: 'Section 19 - Security Safeguards',
    control: 'Accountability, safeguards and lawful processing evidence',
  },
  {
    framework: 'GDPR',
    jurisdiction: 'EU/EEA',
    clause: 'Article 5 and Article 32 - Integrity, confidentiality and security of processing',
    control: 'Integrity, confidentiality, lawful basis and security posture',
  },
  {
    framework: 'SOC2',
    jurisdiction: 'Trust Services',
    clause: 'Security and Processing Integrity Criteria',
    control: 'Change traceability, monitoring, evidence retention and processing integrity',
  },
  {
    framework: 'WORM',
    jurisdiction: 'Append-only evidence',
    clause: 'Write-once evidence retention posture',
    control: 'Append-only receipt manifest and Merkle root witness',
  },
];

/**
 * @function normalizeTenantId
 * @description Normalizes root aliases into the canonical forensic tenant identifier.
 * @collaboration Keeps showroom, API routes, workers and legacy root aliases aligned to the same forensic tenant scope.
 * @param {string} tenantId - Requested tenant identifier.
 * @returns {string} Canonical tenant identifier.
 */
const normalizeTenantId = (tenantId = 'GLOBAL_ROOT') => {
  if (
    ['MASTER', 'GLOBAL_ROOT', 'WILSY_GLOBAL_ROOT', 'WILSY_ROOT', 'wilsy-sovereign-root'].includes(
      String(tenantId)
    )
  ) {
    return 'GLOBAL_ROOT';
  }
  return String(tenantId || 'GLOBAL_ROOT');
};

/**
 * @function buildTenantAliases
 * @description Builds the known root aliases used by legacy and sovereign forensic writers.
 * @collaboration Lets the Merkle auditor replay root evidence across current, legacy and showroom tenant identifiers.
 * @param {string} tenantId - Canonical tenant identifier.
 * @returns {Array<string>} Tenant aliases for DB queries.
 */
const buildTenantAliases = (tenantId) => {
  const canonical = normalizeTenantId(tenantId);
  return [
    ...new Set([
      canonical,
      tenantId,
      'GLOBAL_ROOT',
      'WILSY_ROOT',
      'WILSY_GLOBAL_ROOT',
      'wilsy-sovereign-root',
    ]),
  ];
};

/**
 * @function stableStringify
 * @description Serializes values with deterministic object-key ordering for repeatable cryptographic hashing.
 * @collaboration Provides canonical payload serialization for event seals, receipt hashes, anchor packets and Merkle proof replay.
 * @param {unknown} value - Value to serialize.
 * @returns {string} Canonical JSON string.
 */
const stableStringify = (value) => {
  if (typeof value === 'undefined') return 'null';
  if (value instanceof Date) return JSON.stringify(value.toISOString());
  if (value === null || typeof value !== 'object') return JSON.stringify(value);
  if (Array.isArray(value)) return `[${value.map((item) => stableStringify(item)).join(',')}]`;
  return `{${Object.keys(value)
    .sort()
    .map((key) => `${JSON.stringify(key)}:${stableStringify(value[key])}`)
    .join(',')}}`;
};

/**
 * @function toUpperHash
 * @description Normalizes hashes to uppercase hex for cross-source comparison.
 * @collaboration Keeps stored chain hashes, derived seals, receipt hashes and computed Merkle roots comparable across sources.
 * @param {string|null|undefined} hash - Candidate hash.
 * @returns {string|null} Uppercase hash or null.
 */
const toUpperHash = (hash) => (hash ? String(hash).toUpperCase() : null);

/**
 * @class ForensicMerkleAuditor
 * @description Verifies Wilsy OS forensic ledger integrity by replaying the hash chain, computing Merkle roots,
 * and optionally anchoring verified roots to an external WORM-compatible sink.
 */
class ForensicMerkleAuditor {
  /**
   * @constructor
   * @param {Object} config - Auditor configuration.
   * @param {string} [config.hashingAlgorithm='sha3-512'] - Node/OpenSSL digest algorithm.
   * @param {number} [config.defaultLimit=5000] - Maximum forensic rows to replay by default.
   * @param {string} [config.externalAnchorUrl] - Optional HTTP endpoint for immutable/WORM anchoring.
   * @param {string} [config.externalAnchorSecret] - Optional HMAC secret for external anchor requests.
   * @param {string} [config.localAnchorPath] - Local append-only fallback anchor path.
   */
  constructor(config = {}) {
    this.hashingAlgorithm =
      config.hashingAlgorithm || process.env.WILSY_MERKLE_HASH_ALGORITHM || 'sha3-512';
    this.defaultLimit = Number(config.defaultLimit || process.env.WILSY_MERKLE_AUDIT_LIMIT || 5000);
    this.externalAnchorUrl = config.externalAnchorUrl || process.env.WILSY_WORM_ANCHOR_URL || '';
    this.externalAnchorSecret =
      config.externalAnchorSecret || process.env.WILSY_WORM_ANCHOR_SECRET || '';
    this.externalAnchorProvider =
      process.env.WILSY_WORM_ANCHOR_PROVIDER ||
      (this.externalAnchorUrl ? 'HTTP_WORM_ANCHOR' : 'LOCAL_APPEND_ONLY');
    this.externalTimeoutMs = Number(process.env.WILSY_WORM_ANCHOR_TIMEOUT_MS || 8000);
    this.localAnchorPath =
      config.localAnchorPath ||
      process.env.WILSY_LOCAL_MERKLE_ANCHOR_PATH ||
      path.resolve(__dirname, '../forensic-reports/merkle-anchors.jsonl');
    this.pollIntervalMs = Number(
      config.pollIntervalMs || process.env.WILSY_MERKLE_AUDITOR_INTERVAL_MS || 120000
    );
    this.timer = null;
    this.isRunning = false;
    this.lastRun = null;
  }

  /**
   * @method hashNode
   * @description Produces a deterministic NIST SHA-3 digest for strings, buffers or structured values.
   * @param {string|Buffer|Object} data - Payload to hash.
   * @returns {string} Uppercase hexadecimal digest.
   */
  hashNode(data) {
    const payload = Buffer.isBuffer(data)
      ? data
      : typeof data === 'string'
        ? data
        : stableStringify(data);
    return crypto.createHash(this.hashingAlgorithm).update(payload).digest('hex').toUpperCase();
  }

  /**
   * @method computeMerkleRoot
   * @description Computes a Merkle root from leaf hashes using duplicate-last balancing for odd layers.
   * @param {Array<string>} hashes - Leaf hashes.
   * @returns {string|null} Merkle root or null when no leaves exist.
   */
  computeMerkleRoot(hashes = []) {
    const leaves = hashes.filter(Boolean).map(toUpperHash);
    if (!leaves.length) return null;
    if (leaves.length === 1) return leaves[0];

    let layer = [...leaves];
    while (layer.length > 1) {
      const next = [];
      for (let index = 0; index < layer.length; index += 2) {
        const left = layer[index];
        const right = layer[index + 1] || left;
        next.push(this.hashNode(`${left}${right}`));
      }
      layer = next;
    }
    return layer[0];
  }

  /**
   * @method extractEventSeal
   * @description Returns a stored event seal or derives a deterministic seal for old rows missing one.
   * @param {Object} entry - ForensicLog row.
   * @returns {{seal:string,derived:boolean}} Event seal with derivation flag.
   */
  extractEventSeal(entry = {}) {
    if (entry.eventSeal) return { seal: toUpperHash(entry.eventSeal), derived: false };
    return {
      seal: this.hashNode({
        tenantId: entry.tenantId,
        traceId: entry.traceId,
        eventType: entry.eventType,
        performedBy: entry.performedBy,
        status: entry.status,
        timestamp: entry.timestamp || entry.createdAt,
        metadata: entry.metadata || {},
      }),
      derived: true,
    };
  }

  /**
   * @method sortForReplay
   * @description Sorts forensic rows into replay order, preferring persisted chain positions and falling back to time.
   * @param {Array<Object>} entries - Raw forensic rows.
   * @returns {Array<Object>} Sorted rows.
   */
  sortForReplay(entries = []) {
    const ordered = [...entries];
    const positionCounts = ordered.reduce((counts, entry) => {
      const position = Number.isFinite(Number(entry.chainPosition))
        ? Number(entry.chainPosition)
        : null;

      if (position !== null) {
        counts[position] = (counts[position] || 0) + 1;
      }

      return counts;
    }, {});
    const duplicatePositionCount = Object.values(positionCounts).filter(
      (count) => count > 1
    ).length;
    const positionCollapseDetected = duplicatePositionCount > 0;

    return ordered.sort((left, right) => {
      const leftTime = new Date(left.timestamp || left.createdAt || 0).getTime();
      const rightTime = new Date(right.timestamp || right.createdAt || 0).getTime();

      if (positionCollapseDetected) {
        if (leftTime !== rightTime) return leftTime - rightTime;
        return String(left._id || left.id || '').localeCompare(String(right._id || right.id || ''));
      }

      const leftPosition = Number.isFinite(Number(left.chainPosition))
        ? Number(left.chainPosition)
        : Number.MAX_SAFE_INTEGER;
      const rightPosition = Number.isFinite(Number(right.chainPosition))
        ? Number(right.chainPosition)
        : Number.MAX_SAFE_INTEGER;

      if (leftPosition !== rightPosition) return leftPosition - rightPosition;
      if (leftTime !== rightTime) return leftTime - rightTime;

      return String(left._id || left.id || '').localeCompare(String(right._id || right.id || ''));
    });
  }

  /**
   * @method fetchForensicEntries
   * @description Loads tenant-scoped forensic rows from MongoDB without fabricating entries when the DB is unavailable.
   * @param {Object} options - Fetch options.
   * @param {string} options.tenantId - Tenant identifier.
   * @param {number} [options.limit] - Maximum entries to replay.
   * @returns {Promise<Array<Object>>} Forensic rows.
   */
  async fetchForensicEntries({ tenantId = 'GLOBAL_ROOT', limit = this.defaultLimit } = {}) {
    if (ForensicLog.db?.readyState !== 1) return [];
    const aliases = buildTenantAliases(tenantId);
    const rows = await ForensicLog.find({ tenantId: { $in: aliases } })
      .sort({ timestamp: 1, createdAt: 1, _id: 1 })
      .limit(Math.min(Number(limit) || this.defaultLimit, 20000))
      .lean();
    return this.sortForReplay(rows);
  }

  /**
   * @method replayHashChain
   * @description Replays the forensic chain and detects missing seals, missing chain hashes and hash drift.
   * @param {Array<Object>} entries - Forensic rows in replay order.
   * @returns {Object} Chain replay result.
   */
  replayHashChain(entries = []) {
    let previousExpectedHash = '';
    const leafHashes = [];
    const mismatches = [];
    let derivedSealCount = 0;
    let unchainedCount = 0;

    const replay = entries.map((entry, index) => {
      const { seal, derived } = this.extractEventSeal(entry);
      const expectedChainHash = this.hashNode(`${previousExpectedHash}${seal}`);
      const storedChainHash = toUpperHash(entry.chainHash);

      if (derived) derivedSealCount += 1;
      if (!storedChainHash) unchainedCount += 1;
      if (storedChainHash && storedChainHash !== expectedChainHash) {
        mismatches.push({
          index,
          id: entry._id?.toString?.() || entry.id || null,
          chainPosition: entry.chainPosition ?? index + 1,
          expected: expectedChainHash,
          actual: storedChainHash,
          traceId: entry.traceId || null,
          eventType: entry.eventType || null,
        });
      }

      leafHashes.push(expectedChainHash);
      previousExpectedHash = expectedChainHash;
      return {
        id: entry._id?.toString?.() || entry.id || null,
        traceId: entry.traceId || null,
        eventType: entry.eventType || null,
        chainPosition: entry.chainPosition ?? index + 1,
        storedChainHash,
        expectedChainHash,
        eventSeal: seal,
        timestamp: entry.timestamp || entry.createdAt || null,
      };
    });

    return {
      valid: mismatches.length === 0,
      mismatches,
      derivedSealCount,
      unchainedCount,
      leafHashes,
      replay,
      lastPosition: replay.at(-1)?.chainPosition || null,
      lastHash: replay.at(-1)?.expectedChainHash || null,
    };
  }

  /**
   * @function resolveForensicRechainModelR18AD4C1
   * @description Resolves the Mongoose model that owns fetched forensic entries, even when entries were returned as lean/plain objects.
   * @collaboration Allows controlled backend rechain repair to write through the real database model instead of trusting browser authority.
   * @param {Array<Object>} entries - Forensic entries fetched for replay.
   * @returns {Promise<Object|null>} Mongoose model with bulkWrite support, or null.
   */
  async resolveForensicRechainModelR18AD4C1(entries = []) {
    const constructorModel = entries[0]?.constructor;

    if (constructorModel?.modelName && typeof constructorModel.bulkWrite === 'function') {
      return constructorModel;
    }

    const firstEntry = entries[0] || null;
    const firstId = firstEntry?._id || firstEntry?.id || null;
    const preferredModelNames = [
      'ForensicLog',
      'ForensicAuditLog',
      'ForensicEvent',
      'AuditLog',
      'SovereignAuditLog',
      'AuditEvent',
    ];

    const availableModels = mongoose
      .modelNames()
      .map((modelName) => mongoose.model(modelName))
      .filter((model) => model && typeof model.bulkWrite === 'function');

    for (const modelName of preferredModelNames) {
      if (mongoose.modelNames().includes(modelName)) {
        const model = mongoose.model(modelName);

        if (typeof model.bulkWrite === 'function') {
          if (!firstId) return model;

          try {
            const hit = await model.exists({ _id: firstId });
            if (hit) return model;
          } catch (error) {
            // Continue scanning other models.
          }
        }
      }
    }

    if (firstId) {
      for (const model of availableModels) {
        try {
          const hit = await model.exists({ _id: firstId });
          if (hit) return model;
        } catch (error) {
          // Continue scanning other models.
        }
      }
    }

    return (
      availableModels.find((model) =>
        /forensic|audit/i.test(model.collection?.name || model.modelName || '')
      ) || null
    );
  }

  /**
   * @function buildReceiptRechainRepairPlan
   * @description Builds a controlled repair plan for local forensic rows whose stored chain hashes drift from deterministic replay.
   * @collaboration Classifies chain-position reset drift without mutating evidence until an explicit backend repair command is confirmed.
   * @param {Object} params - Repair plan inputs.
   * @param {Array<Object>} params.entries - Forensic rows fetched in replay order.
   * @param {string} params.actor - Operator requesting the repair.
   * @param {string} params.reason - Repair reason.
   * @returns {Object} Controlled repair plan.
   */
  buildReceiptRechainRepairPlan({
    entries = [],
    actor = 'SYSTEM',
    reason = 'CONTROLLED_RECHAIN_REPAIR',
  } = {}) {
    let previousExpectedHash = '';
    const operations = [];
    const preview = [];
    const blockers = [];

    entries.forEach((entry, index) => {
      const { seal, derived } = this.extractEventSeal(entry);
      const expectedChainHash = this.hashNode(`${previousExpectedHash}${seal}`);
      const storedChainHash = toUpperHash(entry.chainHash);
      const expectedPosition = index + 1;
      const currentPosition = Number(entry.chainPosition || 0);
      const id = entry._id?.toString?.() || entry.id || null;

      if (!id) {
        blockers.push(`MISSING_ROW_ID_${index + 1}`);
      }

      if (derived) {
        blockers.push(`DERIVED_EVENT_SEAL_${index + 1}`);
      }

      preview.push({
        index,
        id,
        traceId: entry.traceId || null,
        eventType: entry.eventType || null,
        currentPosition,
        expectedPosition,
        storedChainHash,
        expectedChainHash,
        requiresUpdate:
          storedChainHash !== expectedChainHash || currentPosition !== expectedPosition,
      });

      if (id) {
        operations.push({
          updateOne: {
            filter: entry._id ? { _id: entry._id } : { id: entry.id },
            update: {
              $set: {
                chainHash: expectedChainHash,
                chainPosition: expectedPosition,
                forensicRechainRepair: {
                  version: 'R18AD4C-CONTROLLED-LOCAL-RECHAIN-AND-RECEIPT-SEAL',
                  actor,
                  reason,
                  repairedAt: new Date().toISOString(),
                  previousChainHash: storedChainHash || null,
                  expectedChainHash,
                  previousChainPosition: currentPosition || null,
                  expectedChainPosition: expectedPosition,
                },
              },
            },
          },
        });
      }

      previousExpectedHash = expectedChainHash;
    });

    const repeatedPositionOne =
      entries.length > 1 && entries.every((entry) => Number(entry.chainPosition || 0) === 1);
    const mismatchedRows = preview.filter((row) => row.requiresUpdate).length;
    const positionCounts = preview.reduce((counts, row) => {
      const position = Number.isFinite(Number(row.currentPosition))
        ? Number(row.currentPosition)
        : null;

      if (position !== null) {
        counts[position] = (counts[position] || 0) + 1;
      }

      return counts;
    }, {});
    const duplicatePositionCount = Object.values(positionCounts).filter(
      (count) => count > 1
    ).length;
    const positionCollapseDetected = duplicatePositionCount > 0;
    const partialRepairDetected =
      preview.some((row) => Number(row.currentPosition) > 1) && positionCollapseDetected;
    const repairable =
      entries.length > 0 &&
      blockers.length === 0 &&
      mismatchedRows > 0 &&
      (repeatedPositionOne || positionCollapseDetected || partialRepairDetected);

    return {
      version: 'R18AD4D-STABLE-REPLAY-ORDER-PARTIAL-RECHAIN',
      repairable,
      repeatedPositionOne,
      positionCollapseDetected,
      partialRepairDetected,
      duplicatePositionCount,
      mismatchedRows,
      operationCount: operations.length,
      blockers,
      preview,
      operations,
    };
  }

  /**
   * @function rechainTenantReceiptWindow
   * @description Rechains a local forensic receipt window under explicit backend authority and returns the post-repair seal posture.
   * @collaboration Enables dev-safe receipt sealing only after backend replay becomes valid; never grants browser seal authority.
   * @param {Object} params - Rechain command inputs.
   * @param {string} params.tenantId - Tenant identifier.
   * @param {number} params.limit - Receipt replay limit.
   * @param {string} params.actor - Operator requesting repair.
   * @param {string} params.reason - Repair reason.
   * @param {boolean} params.dryRun - Whether to avoid writes.
   * @param {string} params.confirmRepairScope - Explicit repair confirmation token.
   * @returns {Promise<Object>} Backend rechain and receipt seal posture.
   */
  async rechainTenantReceiptWindow({
    tenantId,
    limit,
    actor = 'SYSTEM',
    reason = 'CONTROLLED_RECHAIN_REPAIR',
    dryRun = true,
    confirmRepairScope = '',
  } = {}) {
    const canonicalTenant = normalizeTenantId(tenantId);
    const entries = await this.fetchForensicEntries({ tenantId: canonicalTenant, limit });
    const before = this.replayHashChain(entries);
    const plan = this.buildReceiptRechainRepairPlan({ entries, actor, reason });
    const productionBlocked =
      process.env.NODE_ENV === 'production' &&
      process.env.WILSY_ALLOW_PRODUCTION_RECHAIN !== 'true';
    const confirmed = confirmRepairScope === 'LOCAL_DEV_FORENSIC_RECHAIN';

    if (dryRun || !confirmed || productionBlocked || !plan.repairable) {
      return {
        success: true,
        version: 'R18AD4C-CONTROLLED-LOCAL-RECHAIN-AND-RECEIPT-SEAL',
        tenantId: canonicalTenant,
        dryRun: true,
        applied: false,
        backendAuthority: true,
        browserAuthority: false,
        status: plan.repairable ? 'RECHAIN_REPAIR_READY' : 'RECHAIN_REPAIR_BLOCKED',
        blockers: [
          ...plan.blockers,
          ...(!confirmed ? ['CONFIRM_REPAIR_SCOPE_REQUIRED'] : []),
          ...(productionBlocked ? ['PRODUCTION_RECHAIN_BLOCKED'] : []),
          ...(!plan.repairable ? ['WINDOW_NOT_CLASSIFIED_AS_POSITION_RESET_REPAIR'] : []),
        ],
        before: {
          valid: before.valid,
          driftCount: before.mismatches.length,
          unchainedCount: before.unchainedCount,
          derivedSealCount: before.derivedSealCount,
        },
        plan: {
          repairable: plan.repairable,
          repeatedPositionOne: plan.repeatedPositionOne,
          mismatchedRows: plan.mismatchedRows,
          operationCount: plan.operationCount,
          preview: plan.preview.slice(0, 10),
        },
      };
    }

    const model = await this.resolveForensicRechainModelR18AD4C1(entries);

    if (!model || typeof model.bulkWrite !== 'function') {
      return {
        success: true,
        version: 'R18AD4C-CONTROLLED-LOCAL-RECHAIN-AND-RECEIPT-SEAL',
        tenantId: canonicalTenant,
        dryRun: false,
        applied: false,
        backendAuthority: true,
        browserAuthority: false,
        status: 'RECHAIN_MODEL_UNAVAILABLE',
        resolverVersion: 'R18AD4C1-RECHAIN-MODEL-RESOLVER',
        blockers: ['FORENSIC_MODEL_BULK_WRITE_UNAVAILABLE'],
        before: {
          valid: before.valid,
          driftCount: before.mismatches.length,
          unchainedCount: before.unchainedCount,
          derivedSealCount: before.derivedSealCount,
        },
      };
    }

    const writeResult = await model.bulkWrite(plan.operations, { ordered: true });
    const repairedEntries = await this.fetchForensicEntries({ tenantId: canonicalTenant, limit });
    const after = this.replayHashChain(repairedEntries);
    const merkleRoot = this.computeMerkleRoot(after.leafHashes);
    const anchorMode = this.externalAnchorUrl
      ? 'EXTERNAL_WORM_HTTP'
      : 'LOCAL_APPEND_ONLY_PENDING_WORM';
    const receipts =
      repairedEntries.length && merkleRoot
        ? this.buildSealedReceipts({
            tenantId: canonicalTenant,
            entries: repairedEntries,
            chain: after,
            merkleRoot,
            anchorMode,
            chainValid: after.valid,
          })
        : [];
    const receiptMerkleRoot = this.computeMerkleRoot(
      receipts.map((receipt) => receipt.receiptHash)
    );
    const sealedReceiptCount = receipts.filter((receipt) => receipt.status === 'SEALED').length;
    const reviewReceiptCount = receipts.filter(
      (receipt) => receipt.status === 'REVIEW_REQUIRED'
    ).length;

    const result = {
      success: true,
      version: 'R18AD4C-CONTROLLED-LOCAL-RECHAIN-AND-RECEIPT-SEAL',
      tenantId: canonicalTenant,
      dryRun: false,
      applied: true,
      backendAuthority: true,
      browserAuthority: false,
      status: after.valid ? 'RECHAIN_APPLIED_CHAIN_VERIFIED' : 'RECHAIN_APPLIED_REVIEW_REQUIRED',
      writeResult: {
        matchedCount: writeResult.matchedCount || 0,
        modifiedCount: writeResult.modifiedCount || 0,
        upsertedCount: writeResult.upsertedCount || 0,
      },
      before: {
        valid: before.valid,
        driftCount: before.mismatches.length,
        unchainedCount: before.unchainedCount,
        derivedSealCount: before.derivedSealCount,
      },
      after: {
        valid: after.valid,
        driftCount: after.mismatches.length,
        unchainedCount: after.unchainedCount,
        derivedSealCount: after.derivedSealCount,
      },
      counts: {
        receiptCount: receipts.length,
        sealedReceiptCount,
        reviewReceiptCount,
        clausesAnchored: receipts.reduce((total, receipt) => total + receipt.compliance.length, 0),
      },
      roots: {
        merkleRoot,
        receiptMerkleRoot,
      },
      receiptSealStatus:
        after.valid && sealedReceiptCount === receipts.length
          ? 'RECEIPTS_BACKEND_SEALED'
          : 'RECEIPT_SEAL_BLOCKED_REVIEW_REQUIRED',
      receiptPreview: receipts.slice(0, 5).map((receipt) => ({
        receiptId: receipt.receiptId,
        status: receipt.status,
        receiptHash: receipt.receiptHash,
        recordId: receipt.recordId,
        traceId: receipt.traceId,
        eventType: receipt.eventType,
        chainPosition: receipt.chainPosition,
        sealedAt: receipt.sealedAt,
      })),
    };

    this.lastRun = {
      ...this.lastRun,
      ...result,
      verified: after.valid,
      valid: after.valid,
      status: result.status,
      integrity: after.valid ? 'VERIFIED' : 'DRIFT_DETECTED',
      sourceStatus: 'LIVE_DB',
      receiptCount: receipts.length,
      sealedReceiptCount,
      reviewReceiptCount,
      merkleRoot,
      receiptMerkleRoot,
      receipts,
    };

    return result;
  }

  /**
   * @function buildComplianceBindings
   * @description Builds jurisdiction-specific compliance bindings for one sealed forensic receipt.
   * @collaboration Ties POPIA, GDPR, SOC2 and WORM posture directly to the receipt hash, leaf hash and Merkle root.
   * @param {Object} params - Binding inputs.
   * @param {string} params.tenantId - Canonical tenant identifier.
   * @param {Object} params.entry - Source forensic row.
   * @param {Object} params.chainItem - Replayed hash-chain item.
   * @param {string} params.merkleRoot - Computed Merkle root.
   * @param {string} params.receiptHash - Receipt hash.
   * @param {boolean} [params.chainValid=true] - Whether the replayed chain is fully valid.
   * @returns {Array<Object>} Compliance binding rows.
   */
  buildComplianceBindings({
    tenantId,
    entry,
    chainItem,
    merkleRoot,
    receiptHash,
    chainValid = true,
  }) {
    return WILSY_FORENSIC_COMPLIANCE_BINDINGS.map((binding) => ({
      ...binding,
      tenantId: normalizeTenantId(tenantId),
      receiptHash,
      leafHash: chainItem?.expectedChainHash || null,
      merkleRoot,
      recordId: entry?._id?.toString?.() || entry?.id || null,
      traceId: entry?.traceId || chainItem?.traceId || null,
      eventType: entry?.eventType || chainItem?.eventType || null,
      chainPosition: chainItem?.chainPosition || entry?.chainPosition || null,
      status:
        merkleRoot && receiptHash && chainValid
          ? 'BOUND'
          : merkleRoot && receiptHash
            ? 'BOUND_REVIEW_REQUIRED'
            : 'PENDING_ROOT',
    }));
  }

  /**
   * @function buildSealedReceipt
   * @description Builds one deterministic SHA3-512 receipt for a replayed forensic log record.
   * @collaboration Makes every verified forensic row addressable as a receipt, compliance binding, leaf hash and root witness.
   * @param {Object} params - Receipt inputs.
   * @param {string} params.tenantId - Canonical tenant identifier.
   * @param {Object} params.entry - Source forensic row.
   * @param {Object} params.chainItem - Replayed hash-chain item.
   * @param {string} params.merkleRoot - Computed Merkle root.
   * @param {string} params.anchorMode - Anchor mode for the receipt.
   * @param {number} params.index - Receipt ordinal.
   * @param {boolean} [params.chainValid=true] - Whether the replayed chain is fully valid.
   * @returns {Object} Sealed or review-required receipt.
   */
  buildSealedReceipt({
    tenantId,
    entry,
    chainItem,
    merkleRoot,
    anchorMode,
    index,
    chainValid = true,
  }) {
    const canonicalTenant = normalizeTenantId(tenantId);
    const recordId =
      entry?._id?.toString?.() || entry?.id || chainItem?.id || `RECORD-${index + 1}`;
    const leafHash = chainItem?.expectedChainHash || null;
    const eventSeal = chainItem?.eventSeal || null;
    const complianceFingerprint = WILSY_FORENSIC_COMPLIANCE_BINDINGS.map((binding) => ({
      framework: binding.framework,
      jurisdiction: binding.jurisdiction,
      clause: binding.clause,
    }));

    const receiptHash = this.hashNode({
      type: 'WILSY_FORENSIC_RECEIPT',
      version: WILSY_FORENSIC_RECEIPT_CONTRACT_VERSION,
      tenantId: canonicalTenant,
      recordId,
      traceId: entry?.traceId || chainItem?.traceId || null,
      eventType: entry?.eventType || chainItem?.eventType || null,
      chainPosition: chainItem?.chainPosition || entry?.chainPosition || index + 1,
      leafHash,
      eventSeal,
      merkleRoot,
      algorithm: this.hashingAlgorithm.toUpperCase(),
      compliance: complianceFingerprint,
    });

    const receiptId = `RCPT-${receiptHash.slice(0, 24)}`;
    const status =
      merkleRoot && leafHash && chainValid
        ? 'SEALED'
        : merkleRoot && leafHash
          ? 'REVIEW_REQUIRED'
          : 'PENDING_ROOT';

    return {
      receiptId,
      receiptHash,
      version: WILSY_FORENSIC_RECEIPT_CONTRACT_VERSION,
      tenantId: canonicalTenant,
      recordId,
      traceId: entry?.traceId || chainItem?.traceId || null,
      eventType: entry?.eventType || chainItem?.eventType || null,
      chainPosition: chainItem?.chainPosition || entry?.chainPosition || index + 1,
      leafHash,
      eventSeal,
      storedChainHash: chainItem?.storedChainHash || null,
      expectedChainHash: chainItem?.expectedChainHash || null,
      merkleRoot,
      algorithm: this.hashingAlgorithm.toUpperCase(),
      anchorMode,
      qldbStatus: 'RETIRED_NOT_USED',
      qldbEndOfSupport: '2025-07-31',
      evidenceTimestamp: entry?.timestamp || entry?.createdAt || chainItem?.timestamp || null,
      sealedAt: new Date().toISOString(),
      status,
      compliance: this.buildComplianceBindings({
        tenantId: canonicalTenant,
        entry,
        chainItem,
        merkleRoot,
        receiptHash,
        chainValid,
      }),
    };
  }

  /**
   * @function buildSealedReceipts
   * @description Builds deterministic receipt objects for each replayed forensic row.
   * @collaboration Provides the backend receipt contract consumed by the showroom, compliance overlays and future regulator exports.
   * @param {Object} params - Receipt list inputs.
   * @param {string} params.tenantId - Canonical tenant identifier.
   * @param {Array<Object>} params.entries - Source forensic rows.
   * @param {Object} params.chain - Chain replay result.
   * @param {string} params.merkleRoot - Computed Merkle root.
   * @param {string} params.anchorMode - Anchor mode for receipts.
   * @param {boolean} [params.chainValid=true] - Whether the replayed chain is fully valid.
   * @returns {Array<Object>} Sealed or review-required receipt list.
   */
  buildSealedReceipts({
    tenantId,
    entries = [],
    chain = {},
    merkleRoot,
    anchorMode,
    chainValid = true,
  }) {
    return entries.map((entry, index) =>
      this.buildSealedReceipt({
        tenantId,
        entry,
        chainItem: chain.replay?.[index] || {},
        merkleRoot,
        anchorMode,
        index,
        chainValid,
      })
    );
  }

  /**
   * @method buildAuditPacket
   * @description Builds the immutable anchor packet for an externally verifiable forensic chain state.
   * @param {Object} params - Packet inputs.
   * @param {string} params.tenantId - Tenant identifier.
   * @param {string} params.merkleRoot - Computed Merkle root.
   * @param {Object} params.chain - Chain replay result.
   * @returns {Object} Anchor packet.
   */
  buildAuditPacket({ tenantId, merkleRoot, chain, receipts = [], receiptMerkleRoot = null }) {
    const canonicalTenant = normalizeTenantId(tenantId);
    const generatedAt = new Date().toISOString();
    const sealedReceiptCount = receipts.filter((receipt) => receipt.status === 'SEALED').length;
    const complianceFrameworks = WILSY_FORENSIC_COMPLIANCE_BINDINGS.map(
      (binding) => binding.framework
    );
    return {
      blockId: `WILSY-MERKLE-${canonicalTenant}-${Date.now().toString(36).toUpperCase()}-${String(merkleRoot || 'NO_ROOT').slice(0, 12)}`,
      tenantId: canonicalTenant,
      generatedAt,
      merkleRoot,
      receiptMerkleRoot,
      receiptCount: receipts.length,
      sealedReceiptCount,
      complianceFrameworks,
      receiptContractVersion: WILSY_FORENSIC_RECEIPT_CONTRACT_VERSION,
      chainLength: chain.replay.length,
      lastPosition: chain.lastPosition,
      lastHash: chain.lastHash,
      algorithm: this.hashingAlgorithm.toUpperCase(),
      digestStandard: 'NIST_FIPS_202_SHA3',
      qldbStatus: 'RETIRED_NOT_USED',
      qldbEndOfSupport: '2025-07-31',
      complianceBindings: WILSY_FORENSIC_COMPLIANCE_BINDINGS,
      receiptManifest: receipts.map((receipt) => ({
        receiptId: receipt.receiptId,
        receiptHash: receipt.receiptHash,
        recordId: receipt.recordId,
        traceId: receipt.traceId,
        chainPosition: receipt.chainPosition,
        status: receipt.status,
        complianceFrameworks: receipt.compliance.map((binding) => binding.framework),
      })),
      evidenceRange: {
        firstTraceId: chain.replay[0]?.traceId || null,
        lastTraceId: chain.replay.at(-1)?.traceId || null,
        firstTimestamp: chain.replay[0]?.timestamp || null,
        lastTimestamp: chain.replay.at(-1)?.timestamp || null,
      },
    };
  }

  /**
   * @method signAnchorPacket
   * @description Signs an external anchor packet using HMAC-SHA512 when a secret is configured.
   * @param {Object} packet - Anchor packet.
   * @returns {string|null} HMAC signature or null.
   */
  signAnchorPacket(packet) {
    if (!this.externalAnchorSecret) return null;
    return crypto
      .createHmac('sha512', this.externalAnchorSecret)
      .update(stableStringify(packet))
      .digest('hex')
      .toUpperCase();
  }

  /**
   * @method appendLocalAnchor
   * @description Writes a verified Merkle root to a local append-only queue when no WORM endpoint is configured.
   * @param {Object} packet - Anchor packet.
   * @returns {Promise<Object>} Anchor result.
   */
  async appendLocalAnchor(packet) {
    await fs.mkdir(path.dirname(this.localAnchorPath), { recursive: true });
    const anchor = {
      ...packet,
      anchorId: `LOCAL-${crypto.randomBytes(8).toString('hex').toUpperCase()}`,
      provider: 'LOCAL_APPEND_ONLY_ANCHOR',
      status: 'LOCAL_ANCHOR_RECORDED',
      path: this.localAnchorPath,
      warning:
        'Configure WILSY_WORM_ANCHOR_URL or an S3 Object Lock compatible sink for external WORM retention.',
    };
    await fs.appendFile(this.localAnchorPath, `${JSON.stringify(anchor)}\n`, { mode: 0o600 });
    return anchor;
  }

  /**
   * @method anchorVerifiedRoot
   * @description Anchors a verified Merkle root to the configured immutable sink or the local append-only queue.
   * @param {Object} packet - Anchor packet.
   * @returns {Promise<Object>} Anchor result.
   */
  async anchorVerifiedRoot(packet) {
    if (!packet?.merkleRoot) {
      return { status: 'NO_ROOT_TO_ANCHOR', provider: 'NONE' };
    }

    if (!this.externalAnchorUrl) {
      return this.appendLocalAnchor(packet);
    }

    const signature = this.signAnchorPacket(packet);
    const response = await axios.post(this.externalAnchorUrl, packet, {
      timeout: this.externalTimeoutMs,
      headers: {
        'Content-Type': 'application/json',
        'X-Wilsy-Merkle-Algorithm': this.hashingAlgorithm.toUpperCase(),
        ...(signature ? { 'X-Wilsy-Merkle-Signature': signature } : {}),
      },
    });

    return {
      status: 'EXTERNAL_ANCHOR_ACCEPTED',
      provider: this.externalAnchorProvider,
      responseStatus: response.status,
      anchorId: response.data?.anchorId || response.data?.id || packet.blockId,
      externalRecord: response.data || null,
    };
  }

  /**
   * @method listLocalAnchors
   * @description Reads recent local anchor records for diagnostics and boardroom proof export.
   * @param {number} limit - Maximum records to return.
   * @returns {Promise<Array<Object>>} Recent anchor rows.
   */
  async listLocalAnchors(limit = 20) {
    try {
      const raw = await fs.readFile(this.localAnchorPath, 'utf8');
      return raw
        .split('\n')
        .filter(Boolean)
        .slice(-Math.min(Number(limit) || 20, 200))
        .map((line) => JSON.parse(line))
        .reverse();
    } catch {
      return [];
    }
  }

  /**
   * @method verifyTenantChain
   * @description Verifies a tenant forensic chain and optionally anchors the computed Merkle root.
   * @param {Object} options - Verification options.
   * @param {string} [options.tenantId='GLOBAL_ROOT'] - Tenant identifier.
   * @param {number} [options.limit] - Maximum rows to replay.
   * @param {boolean} [options.anchor=false] - Whether to anchor valid roots.
   * @returns {Promise<Object>} Verification status packet.
   */
  async verifyTenantChain({
    tenantId = 'GLOBAL_ROOT',
    limit = this.defaultLimit,
    anchor = false,
  } = {}) {
    const canonicalTenant = normalizeTenantId(tenantId);

    if (ForensicLog.db?.readyState !== 1) {
      return {
        success: true,
        verified: false,
        valid: false,
        status: 'SOURCE_SILENT',
        integrity: 'DB_OFFLINE',
        sourceStatus: 'DB_OFFLINE',
        tenantId: canonicalTenant,
        merkleRoot: null,
        chainLength: 0,
        algorithm: this.hashingAlgorithm.toUpperCase(),
        qldbStatus: 'RETIRED_NOT_USED',
        qldbEndOfSupport: '2025-07-31',
        warning: 'FORENSIC_DB_UNAVAILABLE',
        receiptContractVersion: WILSY_FORENSIC_RECEIPT_CONTRACT_VERSION,
        receiptCount: 0,
        sealedReceiptCount: 0,
        receiptsLogged: 0,
        clausesAnchored: 0,
        receiptMerkleRoot: null,
        receipts: [],
        complianceBindings: WILSY_FORENSIC_COMPLIANCE_BINDINGS,
        complianceFrameworks: WILSY_FORENSIC_COMPLIANCE_BINDINGS.map(
          (binding) => binding.framework
        ),
      };
    }

    const entries = await this.fetchForensicEntries({ tenantId: canonicalTenant, limit });
    const chain = this.replayHashChain(entries);
    const merkleRoot = this.computeMerkleRoot(chain.leafHashes);
    const hasEvidence = entries.length > 0;
    const verified = hasEvidence && chain.valid;
    const anchorMode = this.externalAnchorUrl
      ? 'EXTERNAL_WORM_HTTP'
      : 'LOCAL_APPEND_ONLY_PENDING_WORM';
    const receiptDrafts =
      hasEvidence && merkleRoot
        ? this.buildSealedReceipts({
            tenantId: canonicalTenant,
            entries,
            chain,
            merkleRoot,
            anchorMode,
            chainValid: chain.valid,
          })
        : [];
    const receiptMerkleRoot = this.computeMerkleRoot(
      receiptDrafts.map((receipt) => receipt.receiptHash)
    );
    const packet = hasEvidence
      ? this.buildAuditPacket({
          tenantId: canonicalTenant,
          merkleRoot,
          chain,
          receipts: receiptDrafts,
          receiptMerkleRoot,
        })
      : null;
    let externalAnchor = null;

    if (anchor && verified && packet) {
      try {
        externalAnchor = await this.anchorVerifiedRoot(packet);
      } catch (error) {
        externalAnchor = {
          status: 'EXTERNAL_ANCHOR_REJECTED',
          provider: this.externalAnchorProvider,
          error: error.response?.data?.message || error.message,
        };
      }
    }

    const receipts = receiptDrafts.map((receipt) => ({
      ...receipt,
      anchorId: externalAnchor?.anchorId || null,
      anchorStatus:
        externalAnchor?.status ||
        (anchor
          ? verified
            ? 'ANCHOR_PENDING'
            : 'ANCHOR_BLOCKED_REVIEW_REQUIRED'
          : 'ANCHOR_NOT_REQUESTED'),
    }));
    const sealedReceiptCount = receipts.filter((receipt) => receipt.status === 'SEALED').length;
    const reviewReceiptCount = receipts.filter(
      (receipt) => receipt.status === 'REVIEW_REQUIRED'
    ).length;
    const clausesAnchored = receipts.reduce(
      (total, receipt) => total + receipt.compliance.length,
      0
    );
    const complianceFrameworks = WILSY_FORENSIC_COMPLIANCE_BINDINGS.map(
      (binding) => binding.framework
    );

    const result = {
      success: true,
      contractsVerified: entries.length,
      activeSessions: 0,
      receiptsLogged: receipts.length,
      receiptCount: receipts.length,
      sealedReceiptCount,
      reviewReceiptCount,
      clausesAnchored,
      verified,
      valid: verified,
      status: !hasEvidence
        ? 'SOURCE_SILENT'
        : verified
          ? externalAnchor?.status || 'VERIFIED_LOCAL_CHAIN'
          : 'REVIEW_REQUIRED',
      integrity: !hasEvidence ? 'SOURCE_SILENT' : verified ? 'VERIFIED' : 'DRIFT_DETECTED',
      sourceStatus: hasEvidence ? 'LIVE_DB' : 'SOURCE_SILENT',
      tenantId: canonicalTenant,
      merkleRoot,
      chainLength: entries.length,
      lastBlock: chain.lastPosition || 0,
      lastPosition: chain.lastPosition,
      lastHash: chain.lastHash,
      algorithm: this.hashingAlgorithm.toUpperCase(),
      digestStandard: 'NIST_FIPS_202_SHA3',
      anchorMode,
      anchorProvider: this.externalAnchorProvider,
      externalAnchor,
      receipts,
      receiptMerkleRoot,
      receiptContractVersion: WILSY_FORENSIC_RECEIPT_CONTRACT_VERSION,
      complianceBindings: WILSY_FORENSIC_COMPLIANCE_BINDINGS,
      complianceFrameworks,
      qldbStatus: 'RETIRED_NOT_USED',
      qldbEndOfSupport: '2025-07-31',
      driftCount: chain.mismatches.length,
      unchainedCount: chain.unchainedCount,
      derivedSealCount: chain.derivedSealCount,
      mismatches: chain.mismatches.slice(0, 10),
      details: {
        valid: verified,
        sourceStatus: hasEvidence ? 'LIVE_DB' : 'SOURCE_SILENT',
        replayedEntries: entries.length,
        mismatches: chain.mismatches.slice(0, 10),
        unchainedCount: chain.unchainedCount,
        derivedSealCount: chain.derivedSealCount,
        receiptCount: receipts.length,
        sealedReceiptCount,
        reviewReceiptCount,
        receiptMerkleRoot,
        clausesAnchored,
        complianceFrameworks,
      },
      lastEntry: chain.replay.at(-1) || null,
      checkedAt: new Date().toISOString(),
    };

    this.lastRun = result;
    return result;
  }

  /**
   * @method executeAuditCycle
   * @description Runs a Merkle audit cycle and broadcasts telemetry for verified blocks or drift.
   * @param {Object} options - Audit options.
   * @param {string} [options.tenantId='GLOBAL_ROOT'] - Tenant identifier.
   * @param {boolean} [options.anchor=true] - Whether to anchor valid roots.
   * @param {number} [options.limit] - Maximum rows to replay.
   * @returns {Promise<Object>} Verification status packet.
   */
  async executeAuditCycle({
    tenantId = 'GLOBAL_ROOT',
    anchor = true,
    limit = this.defaultLimit,
  } = {}) {
    const result = await this.verifyTenantChain({ tenantId, anchor, limit });

    if (result.sourceStatus === 'LIVE_DB') {
      await broadcastTelemetry(
        result.tenantId,
        'FORENSIC_MERKLE_AUDIT',
        result.verified ? 'BLOCK_VERIFIED' : 'CRITICAL_DRIFT_DETECTED',
        'ForensicMerkleAuditor',
        {
          merkleRoot: result.merkleRoot,
          chainLength: result.chainLength,
          driftCount: result.driftCount,
          anchorMode: result.anchorMode,
          qldbStatus: result.qldbStatus,
          receiptsLogged: result.receiptsLogged,
          sealedReceiptCount: result.sealedReceiptCount,
          reviewReceiptCount: result.reviewReceiptCount,
          receiptMerkleRoot: result.receiptMerkleRoot,
          clausesAnchored: result.clausesAnchored,
          complianceFrameworks: result.complianceFrameworks,
        }
      ).catch(() => {});
    }

    return result;
  }

  /**
   * @method getStatus
   * @description Returns the most recent auditor posture without forcing a DB replay.
   * @returns {Object} Auditor status.
   */
  getStatus() {
    return {
      success: true,
      running: this.isRunning,
      pollIntervalMs: this.pollIntervalMs,
      algorithm: this.hashingAlgorithm.toUpperCase(),
      anchorMode: this.externalAnchorUrl ? 'EXTERNAL_WORM_HTTP' : 'LOCAL_APPEND_ONLY_PENDING_WORM',
      anchorProvider: this.externalAnchorProvider,
      qldbStatus: 'RETIRED_NOT_USED',
      qldbEndOfSupport: '2025-07-31',
      localAnchorPath: this.localAnchorPath,
      receiptContractVersion: WILSY_FORENSIC_RECEIPT_CONTRACT_VERSION,
      complianceFrameworks: WILSY_FORENSIC_COMPLIANCE_BINDINGS.map((binding) => binding.framework),
      lastRun: this.lastRun,
    };
  }

  /**
   * @method start
   * @description Starts the continuous Merkle auditor worker.
   * @param {Object} options - Worker options.
   * @param {string} [options.tenantId='GLOBAL_ROOT'] - Tenant identifier.
   * @returns {void}
   */
  start({ tenantId = 'GLOBAL_ROOT' } = {}) {
    if (this.isRunning) return;
    this.isRunning = true;
    this.executeAuditCycle({ tenantId, anchor: true }).catch((error) => {
      logger.warn(`[MERKLE_AUDITOR] Initial cycle failed: ${error.message}`);
    });
    this.timer = setInterval(() => {
      this.executeAuditCycle({ tenantId, anchor: true }).catch((error) => {
        logger.warn(`[MERKLE_AUDITOR] Scheduled cycle failed: ${error.message}`);
      });
    }, this.pollIntervalMs);
  }

  /**
   * @method stop
   * @description Stops the continuous Merkle auditor worker.
   * @returns {void}
   */
  stop() {
    this.isRunning = false;
    if (this.timer) {
      clearInterval(this.timer);
      this.timer = null;
    }
  }
}

const forensicMerkleAuditor = new ForensicMerkleAuditor();

export { ForensicMerkleAuditor };
export default forensicMerkleAuditor;
