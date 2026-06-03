/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - FORENSIC MERKLE AUDITOR [V56.1.0-PRODUCTION-WORM]                                                                         ║
 * ║ [NIST SHA-3 | HASH-CHAIN REPLAY | MERKLE ROOTS | CONFIGURABLE WORM ANCHORING | QLDB RETIREMENT SAFE]                               ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 56.1.0-PRODUCTION-WORM | PRODUCTION READY | INSTITUTIONAL NON-REPUDIATION                                                  ║
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

/**
 * @function normalizeTenantId
 * @description Normalizes root aliases into the canonical forensic tenant identifier.
 * @param {string} tenantId - Requested tenant identifier.
 * @returns {string} Canonical tenant identifier.
 */
const normalizeTenantId = (tenantId = 'GLOBAL_ROOT') => {
  if (['MASTER', 'GLOBAL_ROOT', 'WILSY_GLOBAL_ROOT', 'WILSY_ROOT', 'wilsy-sovereign-root'].includes(String(tenantId))) {
    return 'GLOBAL_ROOT';
  }
  return String(tenantId || 'GLOBAL_ROOT');
};

/**
 * @function buildTenantAliases
 * @description Builds the known root aliases used by legacy and sovereign forensic writers.
 * @param {string} tenantId - Canonical tenant identifier.
 * @returns {Array<string>} Tenant aliases for DB queries.
 */
const buildTenantAliases = (tenantId) => {
  const canonical = normalizeTenantId(tenantId);
  return [...new Set([canonical, tenantId, 'GLOBAL_ROOT', 'WILSY_ROOT', 'WILSY_GLOBAL_ROOT', 'wilsy-sovereign-root'])];
};

/**
 * @function stableStringify
 * @description Serializes values with deterministic object-key ordering for repeatable cryptographic hashing.
 * @param {unknown} value - Value to serialize.
 * @returns {string} Canonical JSON string.
 */
const stableStringify = (value) => {
  if (typeof value === 'undefined') return 'null';
  if (value instanceof Date) return JSON.stringify(value.toISOString());
  if (value === null || typeof value !== 'object') return JSON.stringify(value);
  if (Array.isArray(value)) return `[${value.map(item => stableStringify(item)).join(',')}]`;
  return `{${Object.keys(value).sort().map(key => `${JSON.stringify(key)}:${stableStringify(value[key])}`).join(',')}}`;
};

/**
 * @function toUpperHash
 * @description Normalizes hashes to uppercase hex for cross-source comparison.
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
    this.hashingAlgorithm = config.hashingAlgorithm || process.env.WILSY_MERKLE_HASH_ALGORITHM || 'sha3-512';
    this.defaultLimit = Number(config.defaultLimit || process.env.WILSY_MERKLE_AUDIT_LIMIT || 5000);
    this.externalAnchorUrl = config.externalAnchorUrl || process.env.WILSY_WORM_ANCHOR_URL || '';
    this.externalAnchorSecret = config.externalAnchorSecret || process.env.WILSY_WORM_ANCHOR_SECRET || '';
    this.externalAnchorProvider = process.env.WILSY_WORM_ANCHOR_PROVIDER || (this.externalAnchorUrl ? 'HTTP_WORM_ANCHOR' : 'LOCAL_APPEND_ONLY');
    this.externalTimeoutMs = Number(process.env.WILSY_WORM_ANCHOR_TIMEOUT_MS || 8000);
    this.localAnchorPath = config.localAnchorPath
      || process.env.WILSY_LOCAL_MERKLE_ANCHOR_PATH
      || path.resolve(__dirname, '../forensic-reports/merkle-anchors.jsonl');
    this.pollIntervalMs = Number(config.pollIntervalMs || process.env.WILSY_MERKLE_AUDITOR_INTERVAL_MS || 120000);
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
      : (typeof data === 'string' ? data : stableStringify(data));
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
        metadata: entry.metadata || {}
      }),
      derived: true
    };
  }

  /**
   * @method sortForReplay
   * @description Sorts forensic rows into replay order, preferring persisted chain positions and falling back to time.
   * @param {Array<Object>} entries - Raw forensic rows.
   * @returns {Array<Object>} Sorted rows.
   */
  sortForReplay(entries = []) {
    return [...entries].sort((left, right) => {
      const leftPosition = Number.isFinite(Number(left.chainPosition)) ? Number(left.chainPosition) : Number.MAX_SAFE_INTEGER;
      const rightPosition = Number.isFinite(Number(right.chainPosition)) ? Number(right.chainPosition) : Number.MAX_SAFE_INTEGER;
      if (leftPosition !== rightPosition) return leftPosition - rightPosition;
      return new Date(left.timestamp || left.createdAt || 0).getTime() - new Date(right.timestamp || right.createdAt || 0).getTime();
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
      .sort({ chainPosition: 1, timestamp: 1, createdAt: 1 })
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
          eventType: entry.eventType || null
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
        timestamp: entry.timestamp || entry.createdAt || null
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
      lastHash: replay.at(-1)?.expectedChainHash || null
    };
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
  buildAuditPacket({ tenantId, merkleRoot, chain }) {
    const canonicalTenant = normalizeTenantId(tenantId);
    const generatedAt = new Date().toISOString();
    return {
      blockId: `WILSY-MERKLE-${canonicalTenant}-${Date.now().toString(36).toUpperCase()}-${String(merkleRoot || 'NO_ROOT').slice(0, 12)}`,
      tenantId: canonicalTenant,
      generatedAt,
      merkleRoot,
      chainLength: chain.replay.length,
      lastPosition: chain.lastPosition,
      lastHash: chain.lastHash,
      algorithm: this.hashingAlgorithm.toUpperCase(),
      digestStandard: 'NIST_FIPS_202_SHA3',
      qldbStatus: 'RETIRED_NOT_USED',
      qldbEndOfSupport: '2025-07-31',
      evidenceRange: {
        firstTraceId: chain.replay[0]?.traceId || null,
        lastTraceId: chain.replay.at(-1)?.traceId || null,
        firstTimestamp: chain.replay[0]?.timestamp || null,
        lastTimestamp: chain.replay.at(-1)?.timestamp || null
      }
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
      warning: 'Configure WILSY_WORM_ANCHOR_URL or an S3 Object Lock compatible sink for external WORM retention.'
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
        ...(signature ? { 'X-Wilsy-Merkle-Signature': signature } : {})
      }
    });

    return {
      status: 'EXTERNAL_ANCHOR_ACCEPTED',
      provider: this.externalAnchorProvider,
      responseStatus: response.status,
      anchorId: response.data?.anchorId || response.data?.id || packet.blockId,
      externalRecord: response.data || null
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
        .map(line => JSON.parse(line))
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
  async verifyTenantChain({ tenantId = 'GLOBAL_ROOT', limit = this.defaultLimit, anchor = false } = {}) {
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
        warning: 'FORENSIC_DB_UNAVAILABLE'
      };
    }

    const entries = await this.fetchForensicEntries({ tenantId: canonicalTenant, limit });
    const chain = this.replayHashChain(entries);
    const merkleRoot = this.computeMerkleRoot(chain.leafHashes);
    const hasEvidence = entries.length > 0;
    const verified = hasEvidence && chain.valid;
    const packet = hasEvidence ? this.buildAuditPacket({ tenantId: canonicalTenant, merkleRoot, chain }) : null;
    let externalAnchor = null;

    if (anchor && verified && packet) {
      try {
        externalAnchor = await this.anchorVerifiedRoot(packet);
      } catch (error) {
        externalAnchor = {
          status: 'EXTERNAL_ANCHOR_REJECTED',
          provider: this.externalAnchorProvider,
          error: error.response?.data?.message || error.message
        };
      }
    }

    const result = {
      success: true,
      verified,
      valid: verified,
      status: !hasEvidence
        ? 'SOURCE_SILENT'
        : (verified ? (externalAnchor?.status || 'VERIFIED_LOCAL_CHAIN') : 'REVIEW_REQUIRED'),
      integrity: !hasEvidence ? 'SOURCE_SILENT' : (verified ? 'VERIFIED' : 'DRIFT_DETECTED'),
      sourceStatus: hasEvidence ? 'LIVE_DB' : 'SOURCE_SILENT',
      tenantId: canonicalTenant,
      merkleRoot,
      chainLength: entries.length,
      lastBlock: chain.lastPosition || 0,
      lastPosition: chain.lastPosition,
      lastHash: chain.lastHash,
      algorithm: this.hashingAlgorithm.toUpperCase(),
      digestStandard: 'NIST_FIPS_202_SHA3',
      anchorMode: this.externalAnchorUrl ? 'EXTERNAL_WORM_HTTP' : 'LOCAL_APPEND_ONLY_PENDING_WORM',
      anchorProvider: this.externalAnchorProvider,
      externalAnchor,
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
        derivedSealCount: chain.derivedSealCount
      },
      lastEntry: chain.replay.at(-1) || null,
      checkedAt: new Date().toISOString()
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
   * @returns {Promise<Object>} Verification status packet.
   */
  async executeAuditCycle({ tenantId = 'GLOBAL_ROOT', anchor = true } = {}) {
    const result = await this.verifyTenantChain({ tenantId, anchor });

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
          qldbStatus: result.qldbStatus
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
      lastRun: this.lastRun
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
    this.executeAuditCycle({ tenantId, anchor: true }).catch(error => {
      logger.warn(`[MERKLE_AUDITOR] Initial cycle failed: ${error.message}`);
    });
    this.timer = setInterval(() => {
      this.executeAuditCycle({ tenantId, anchor: true }).catch(error => {
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
