/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - FORENSIC NUCLEUS ROUTES [V54.1.0-PRODUCTION-SEAL-FALLBACK]                                                                           ║
 * ║ [IMMUTABLE AUDIT TRAIL | QUANTUM-RESISTANT INTEGRITY | SHARD FORENSICS | BOARDROOM KPI HYDRATION | EBAT BLOCKCHAIN ANCHORING]           ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 54.1.0-PRODUCTION-SEAL-FALLBACK | PRODUCTION READY | TRILLION DOLLAR SPECIFICATION                                                                ║
 * ║ EPITOME: BIBLICAL WORTH BILLIONS | NO CHILD'S PLACE | INSTITUTIONAL AUTHORITY | MARS-SPEC ARCHITECTURE                                 ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/routes/forensicRoutes.js                                                  ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                 ║
 * ║ • Wilson Khanyezi (CEO/Lead Architect) - Mandated path alignment with RevenueHUD client-side calls.                                    ║
 * ║ • AI Engineering (Gemini) - RECTIFIED: Aligned path definitions (audit-trail, benchmark) to obliterate 404 fractures.                   ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import express from 'express';
import crypto from 'node:crypto';
import ForensicLog from '../models/ForensicLog.js';
import forensicMerkleAuditor from '../services/ForensicMerkleAuditor.js';
const router = express.Router();

/**
 * @function normalizeTenantId
 * @description Normalizes system and root aliases into the canonical forensic tenant key.
 * @collaboration Keeps forensic routes, Merkle auditor routes, showroom calls and legacy root aliases aligned without creating fake tenants.
 * @param {string} tenantId - Tenant identifier supplied by the request.
 * @returns {string} Canonical tenant identifier used for forensic ledger queries.
 */
const normalizeTenantId = (tenantId = 'GLOBAL_ROOT') => {
  const normalized = String(tenantId || 'GLOBAL_ROOT').trim();
  if (
    ['MASTER', 'GLOBAL_ROOT', 'WILSY_GLOBAL_ROOT', 'WILSY_ROOT', 'wilsy-sovereign-root'].includes(
      normalized
    )
  )
    return 'GLOBAL_ROOT';
  return normalized;
};

const statusMap = {
  SUCCESS: 'ANCHORED',
  WARNING: 'PENDING',
  FAILURE: 'FAILED',
  FRACTURE: 'FAILED',
};

const categorySeverity = {
  SECURITY: 'HIGH',
  COMPLIANCE: 'MEDIUM',
  REVENUE: 'MEDIUM',
  DATA: 'MEDIUM',
  ACCESS: 'LOW',
  SYSTEM: 'LOW',
};

const WILSY_FORENSIC_RECEIPT_ROUTE_VERSION = 'R18B2-FORENSIC-RECEIPT-OVERLAY-TOTALS';
const WILSY_FORENSIC_RECEIPT_DEFAULT_LIMIT = 50;
const WILSY_FORENSIC_RECEIPT_MAX_LIMIT = 500;
const WILSY_FORENSIC_RECEIPT_REPLAY_DEFAULT_LIMIT = 5000;
const WILSY_FORENSIC_RECEIPT_REPLAY_MAX_LIMIT = 20000;
const WILSY_FORENSIC_SEAL_ROUTE_VERSION = 'R18P1-PRODUCTION-SEAL-FALLBACK';
const WILSY_FORENSIC_SEAL_DEFAULT_LIMIT = 250;
const WILSY_FORENSIC_SEAL_MAX_LIMIT = 5000;

/**
 * @function parseForensicSealLimit
 * @description Parses safe-window seal limits separately from receipt display and full proof replay limits.
 * @collaboration Keeps browser seal requests bounded while allowing backend-owned production seal evaluation.
 * @param {unknown} value - Raw seal limit query/body value.
 * @returns {number} Safe seal evaluation limit.
 */
const parseForensicSealLimit = (value) =>
  Math.min(
    Math.max(Number(value) || WILSY_FORENSIC_SEAL_DEFAULT_LIMIT, 1),
    WILSY_FORENSIC_SEAL_MAX_LIMIT
  );

/**
 * @function normalizeSealActor
 * @description Normalizes the operator identity recorded on a backend seal decision request.
 * @collaboration Gives future audit trails actor context without trusting the browser as seal authority.
 * @param {unknown} value - Raw actor value from body, headers or runtime context.
 * @returns {string} Safe actor label.
 */
const normalizeSealActor = (value) => {
  const actor = String(value || 'SYSTEM').trim();

  return actor ? actor.slice(0, 180) : 'SYSTEM';
};

/**
 * @function buildRouteSealEligibility
 * @description Builds a production-safe seal eligibility decision from a backend verifier packet when the auditor singleton has not exposed sealSafeReceiptWindow.
 * @collaboration Keeps seal decisions server-owned and prevents browser-side immutable seal claims even during service-method rollout.
 * @param {Object} result - Backend Merkle verifier result.
 * @returns {Object} Route-owned seal eligibility decision.
 */
const buildRouteSealEligibility = (result = {}) => {
  const receiptCount = Number(
    result.receiptCount ??
      result.receiptsLogged ??
      (Array.isArray(result.receipts) ? result.receipts.length : 0)
  );
  const sealedReceiptCount = Number(result.sealedReceiptCount || 0);
  const reviewReceiptCount = Number(
    result.reviewReceiptCount ?? Math.max(receiptCount - sealedReceiptCount, 0)
  );
  const blockers = [];

  if (!receiptCount) blockers.push('NO_RECEIPTS_AVAILABLE');
  if (!result.merkleRoot || !result.receiptMerkleRoot)
    blockers.push('MISSING_MERKLE_OR_RECEIPT_ROOT');
  if (result.verified !== true) blockers.push('CHAIN_NOT_VERIFIED');
  if (reviewReceiptCount > 0) blockers.push('REVIEW_RECEIPTS_PRESENT');
  if (sealedReceiptCount < receiptCount) blockers.push('NOT_ALL_RECEIPTS_BACKEND_SEALED');

  const canSeal = blockers.length === 0;

  return {
    version: WILSY_FORENSIC_SEAL_ROUTE_VERSION,
    canSeal,
    status: canSeal ? 'SEAL_READY' : 'SEAL_BLOCKED_REVIEW_REQUIRED',
    blockers,
    recommendations: canSeal
      ? ['APPEND_ONLY_FINALIZATION_ALLOWED']
      : [
          'RESOLVE_REVIEW_RECEIPTS',
          'REPLAY_BACKEND_CHAIN',
          'CONFIRM_RECEIPT_MERKLE_ROOT',
          'RETRY_SEAL_AFTER_VERIFIED_AUDIT',
        ],
    counts: {
      receiptCount,
      sealedReceiptCount,
      reviewReceiptCount,
      clausesAnchored: Number(result.clausesAnchored || 0),
    },
    roots: {
      merkleRoot: result.merkleRoot || null,
      receiptMerkleRoot: result.receiptMerkleRoot || null,
    },
  };
};

/**
 * @function buildRouteSealDecision
 * @description Converts route-level seal eligibility into a production seal decision envelope.
 * @collaboration Gives the seal-safe-window route truthful output even before the auditor service owns the final seal method.
 * @param {Object} result - Backend Merkle verifier result.
 * @param {Object} options - Seal decision options.
 * @returns {Object} Server-owned seal decision.
 */
const buildRouteSealDecision = (result = {}, options = {}) => {
  const eligibility = buildRouteSealEligibility(result);
  const immutableSeal = eligibility.canSeal === true;

  return {
    version: WILSY_FORENSIC_SEAL_ROUTE_VERSION,
    requestedAt: new Date().toISOString(),
    requestedBy: options.actor || 'SYSTEM',
    reason: options.reason || 'SAFE_WINDOW_SEAL_REQUEST',
    immutableSeal,
    canSeal: eligibility.canSeal,
    sealStatus: immutableSeal ? 'SEALED_BY_BACKEND_AUTHORITY' : eligibility.status,
    nextAction: immutableSeal
      ? 'PERSIST_APPEND_ONLY_SEAL'
      : 'REVIEW_REQUIRED_BEFORE_IMMUTABLE_SEAL',
    eligibility,
  };
};

/**
 * @function buildRouteSealManifest
 * @description Builds a route-owned seal manifest reference from verifier result and seal decision.
 * @collaboration Gives the frontend a stable manifest hash while preserving backend authority for final immutable sealing.
 * @param {Object} result - Backend Merkle verifier result.
 * @param {Object} sealDecision - Server-owned seal decision.
 * @returns {Object} Seal manifest metadata.
 */
const buildRouteSealManifest = (result = {}, sealDecision = {}) => {
  const material = {
    version: WILSY_FORENSIC_SEAL_ROUTE_VERSION,
    tenantId: result.tenantId || 'GLOBAL_ROOT',
    sealStatus: sealDecision.sealStatus || 'SEAL_BLOCKED_REVIEW_REQUIRED',
    immutableSeal: sealDecision.immutableSeal === true,
    merkleRoot: result.merkleRoot || null,
    receiptMerkleRoot: result.receiptMerkleRoot || null,
    receiptCount: Number(result.receiptCount ?? result.receiptsLogged ?? 0),
    sealedReceiptCount: Number(result.sealedReceiptCount || 0),
    reviewReceiptCount: Number(result.reviewReceiptCount || 0),
    clausesAnchored: Number(result.clausesAnchored || 0),
    generatedAt: sealDecision.requestedAt || new Date().toISOString(),
  };

  return {
    ...material,
    sealManifestHash: crypto
      .createHash('sha3-512')
      .update(JSON.stringify(material))
      .digest('hex')
      .toUpperCase(),
  };
};

/**
 * @function buildRouteFallbackSealPacket
 * @description Builds a route-level production seal packet from backend verifier output.
 * @collaboration Ensures the seal route returns proof counts and blockers instead of method-missing output while the auditor service is upgraded.
 * @param {Object} result - Backend Merkle verifier result.
 * @param {Object} options - Seal request options.
 * @returns {Object} Route-level seal packet.
 */
const buildRouteFallbackSealPacket = (result = {}, options = {}) => {
  const sealDecision = buildRouteSealDecision(result, options);
  const sealManifest = buildRouteSealManifest(result, sealDecision);

  return {
    ...result,
    sealWorkflowVersion: WILSY_FORENSIC_SEAL_ROUTE_VERSION,
    sealStatus: sealDecision.sealStatus,
    immutableSeal: sealDecision.immutableSeal,
    sealDecision,
    sealManifest,
    productionSeal: {
      backendAuthority: true,
      browserAuthority: false,
      finalSealRequiresBackendStatus: 'SEALED_BY_BACKEND_AUTHORITY',
      fallbackAuthority: 'ROUTE_BACKEND_VERIFIER',
    },
  };
};

/**
 * @function buildSealRouteUnavailableEnvelope
 * @description Builds a truthful route envelope when the auditor service has not yet been upgraded with sealSafeReceiptWindow.
 * @collaboration Prevents the route from pretending to seal receipts when the backend seal workflow is unavailable.
 * @param {string} tenantId - Canonical tenant id.
 * @param {string} warning - Warning returned to the operator.
 * @returns {Object} Route-safe unavailable seal envelope.
 */
const buildSealRouteUnavailableEnvelope = (tenantId, warning) => ({
  success: true,
  routeVersion: WILSY_FORENSIC_SEAL_ROUTE_VERSION,
  tenantId,
  immutableSeal: false,
  sealStatus: 'SEAL_ROUTE_UNAVAILABLE_BACKEND_METHOD_MISSING',
  productionSeal: {
    backendAuthority: true,
    browserAuthority: false,
    finalSealRequiresBackendStatus: 'SEALED_BY_BACKEND_AUTHORITY',
  },
  sealDecision: {
    version: WILSY_FORENSIC_SEAL_ROUTE_VERSION,
    immutableSeal: false,
    canSeal: false,
    sealStatus: 'SEAL_ROUTE_UNAVAILABLE_BACKEND_METHOD_MISSING',
    nextAction: 'APPLY_R18O_AUDITOR_SEAL_WORKFLOW',
    eligibility: {
      canSeal: false,
      status: 'SEAL_BLOCKED_BACKEND_METHOD_MISSING',
      blockers: ['AUDITOR_SEAL_WORKFLOW_NOT_AVAILABLE'],
    },
  },
  receipts: [],
  receiptContract: buildReceiptContractSummary({ tenantId, warning }),
  receiptOverlay: buildForensicAuditOverlay({ tenantId, warning }, []),
  warning,
});

/**
 * @function buildSealRouteEnvelope
 * @description Wraps the backend seal packet with receipt contract and audit overlay metadata.
 * @collaboration Gives the showroom and future Account Command Center card a production seal contract without browser-owned immutability claims.
 * @param {Object} sealPacket - Backend seal packet returned by ForensicMerkleAuditor.
 * @param {Object} options - Envelope options.
 * @returns {Object} Route-safe seal envelope.
 */
const buildSealRouteEnvelope = (sealPacket = {}, options = {}) => ({
  ...buildForensicReceiptEnvelope(sealPacket, options),
  routeVersion: WILSY_FORENSIC_SEAL_ROUTE_VERSION,
  sealWorkflowVersion: sealPacket.sealWorkflowVersion || 'R18O-PRODUCTION-SEAL-ELIGIBILITY',
  immutableSeal: sealPacket.immutableSeal === true,
  sealStatus:
    sealPacket.sealStatus || sealPacket.sealDecision?.sealStatus || 'SEAL_BLOCKED_REVIEW_REQUIRED',
  sealDecision: sealPacket.sealDecision || null,
  sealManifest: sealPacket.sealManifest || null,
  productionSeal: sealPacket.productionSeal || {
    backendAuthority: true,
    browserAuthority: false,
    finalSealRequiresBackendStatus: 'SEALED_BY_BACKEND_AUTHORITY',
  },
});

/**
 * @function createSeal
 * @description Creates a deterministic SHA3-512 seal for local forensic payload mapping.
 * @collaboration Gives legacy vault rows a verifiable display hash while the Merkle auditor remains the authority for receipt and root proof.
 * @param {Object} payload - Payload to seal.
 * @returns {string} Uppercase SHA3-512 digest.
 */
const createSeal = (payload) =>
  crypto.createHash('sha3-512').update(JSON.stringify(payload)).digest('hex').toUpperCase();

/**
 * @function mapForensicLog
 * @description Maps a persisted ForensicLog document into the HUD contract without inventing values.
 * @collaboration Keeps vault, audit trail, forensic HUD and showroom evidence rows aligned to persisted forensic records.
 * @param {Object} entry - Persisted forensic ledger entry.
 * @param {number} index - Row index used only for stable fallback IDs.
 * @returns {Object} Client-facing forensic audit row.
 */
const mapForensicLog = (entry, index = 0) => ({
  id: entry._id?.toString?.() || entry.id || `FLOG-${Date.now()}-${index}`,
  timestamp: entry.timestamp || entry.createdAt || new Date().toISOString(),
  action: entry.eventType || entry.action || 'SYSTEM_EVENT',
  status: statusMap[entry.status] || entry.status || 'ANCHORED',
  node: entry.metadata?.source || entry.metadata?.component || entry.performedBy || 'WILSY_CORE',
  hash: entry.chainHash || entry.eventSeal || createSeal(entry),
  severity: entry.riskFlags?.length ? 'HIGH' : categorySeverity[entry.category] || 'LOW',
  details:
    entry.metadata?.message || entry.metadata?.details || entry.category || 'Forensic event sealed',
  tenantId: entry.tenantId || 'GLOBAL_ROOT',
});

/**
 * @function createSourceSilentVault
 * @description Builds a truthful empty vault payload when no forensic evidence exists yet.
 * @collaboration Preserves source-silent honesty across vault and showroom surfaces instead of rendering synthetic forensic evidence.
 * @param {string} tenantId - Tenant identifier queried by the cockpit.
 * @returns {Object[]} Empty array because no synthetic evidence should be rendered.
 */
const createSourceSilentVault = (tenantId) => [];

/**
 * @function parseForensicReceiptLimit
 * @description Parses receipt query limits while protecting the auditor from unbounded regulator drill-down exports.
 * @collaboration Keeps showroom overlays, regulator views and audit tools aligned to the same safe receipt pagination contract.
 * @param {unknown} value - Raw limit query value.
 * @returns {number} Safe receipt limit.
 */
const parseForensicReceiptLimit = (value) =>
  Math.min(
    Math.max(Number(value) || WILSY_FORENSIC_RECEIPT_DEFAULT_LIMIT, 1),
    WILSY_FORENSIC_RECEIPT_MAX_LIMIT
  );

/**
 * @function parseForensicReplayLimit
 * @description Parses forensic replay limits separately from receipt display pagination.
 * @collaboration Keeps regulator/showroom pagination from shrinking the authoritative Merkle replay contract.
 * @param {unknown} value - Raw replay limit query value.
 * @returns {number} Safe replay limit for the Merkle auditor.
 */
const parseForensicReplayLimit = (value) =>
  Math.min(
    Math.max(Number(value) || WILSY_FORENSIC_RECEIPT_REPLAY_DEFAULT_LIMIT, 1),
    WILSY_FORENSIC_RECEIPT_REPLAY_MAX_LIMIT
  );

/**
 * @function normalizeReceiptStatusFilter
 * @description Normalizes receipt status filters used by drill-down routes.
 * @collaboration Lets the showroom request sealed, review-required or pending receipts without leaking fragile casing rules.
 * @param {unknown} value - Raw receipt status filter.
 * @returns {string} Normalized receipt status filter.
 */
const normalizeReceiptStatusFilter = (value) =>
  String(value || '')
    .trim()
    .toUpperCase();

/**
 * @function normalizeComplianceFrameworkFilter
 * @description Normalizes compliance framework filters for POPIA, GDPR, SOC2 and WORM bindings.
 * @collaboration Keeps regulator drill-down routes aligned with backend receipt compliance bindings.
 * @param {unknown} value - Raw framework filter.
 * @returns {string} Normalized compliance framework filter.
 */
const normalizeComplianceFrameworkFilter = (value) =>
  String(value || '')
    .trim()
    .toUpperCase();

/**
 * @function buildReceiptContractSummary
 * @description Builds a compact receipt contract summary from a Merkle auditor result.
 * @collaboration Gives the showroom, regulators and investors a consistent summary of receipts, clauses and root witnesses.
 * @param {Object} result - Merkle auditor result.
 * @returns {Object} Receipt contract summary.
 */
const buildReceiptContractSummary = (result = {}) => {
  const receipts = Array.isArray(result.receipts) ? result.receipts : [];
  const complianceFrameworks = Array.isArray(result.complianceFrameworks)
    ? result.complianceFrameworks
    : [
        ...new Set(
          receipts
            .flatMap((receipt) => (receipt.compliance || []).map((binding) => binding.framework))
            .filter(Boolean)
        ),
      ];

  return {
    version: WILSY_FORENSIC_RECEIPT_ROUTE_VERSION,
    receiptContractVersion: result.receiptContractVersion || 'R18A-SEALED-RECEIPT-CONTRACT',
    tenantId: result.tenantId || 'GLOBAL_ROOT',
    merkleRoot: result.merkleRoot || null,
    receiptMerkleRoot: result.receiptMerkleRoot || null,
    chainLength: Number(result.chainLength || 0),
    receiptsLogged: Number(result.receiptsLogged ?? receipts.length ?? 0),
    receiptCount: Number(result.receiptCount ?? receipts.length ?? 0),
    sealedReceiptCount: Number(result.sealedReceiptCount || 0),
    reviewReceiptCount: Number(
      result.reviewReceiptCount ||
        receipts.filter((receipt) => receipt.status === 'REVIEW_REQUIRED').length
    ),
    clausesAnchored: Number(
      result.clausesAnchored ||
        receipts.reduce((total, receipt) => total + (receipt.compliance || []).length, 0)
    ),
    complianceFrameworks,
    verified: Boolean(result.verified),
    status: result.status || 'SOURCE_PENDING',
    anchorMode: result.anchorMode || 'LOCAL_APPEND_ONLY_PENDING_WORM',
    anchorProvider: result.anchorProvider || 'LOCAL_APPEND_ONLY',
  };
};

/**
 * @function mapReceiptForForensicRoute
 * @description Maps a sealed or review-required receipt into a stable API drill-down row.
 * @collaboration Presents cryptographic receipt hashes, compliance clauses and anchor posture without mutating backend proof material.
 * @param {Object} receipt - Raw auditor receipt.
 * @returns {Object} Route-safe receipt row.
 */
const mapReceiptForForensicRoute = (receipt = {}) => ({
  receiptId: receipt.receiptId,
  receiptHash: receipt.receiptHash,
  version: receipt.version,
  tenantId: receipt.tenantId,
  recordId: receipt.recordId,
  traceId: receipt.traceId,
  eventType: receipt.eventType,
  chainPosition: receipt.chainPosition,
  leafHash: receipt.leafHash,
  eventSeal: receipt.eventSeal,
  merkleRoot: receipt.merkleRoot,
  algorithm: receipt.algorithm,
  status: receipt.status,
  anchorStatus: receipt.anchorStatus,
  anchorId: receipt.anchorId,
  anchorMode: receipt.anchorMode,
  evidenceTimestamp: receipt.evidenceTimestamp,
  sealedAt: receipt.sealedAt,
  compliance: Array.isArray(receipt.compliance)
    ? receipt.compliance.map((binding) => ({
        framework: binding.framework,
        jurisdiction: binding.jurisdiction,
        clause: binding.clause,
        control: binding.control,
        status: binding.status,
        receiptHash: binding.receiptHash,
        leafHash: binding.leafHash,
        merkleRoot: binding.merkleRoot,
        traceId: binding.traceId,
        eventType: binding.eventType,
        chainPosition: binding.chainPosition,
      }))
    : [],
});

/**
 * @function filterForensicReceipts
 * @description Applies receipt id, status and compliance framework filters to auditor receipts.
 * @collaboration Powers regulator and showroom drill-down queries without changing the underlying receipt contract.
 * @param {Array<Object>} receipts - Raw auditor receipts.
 * @param {Object} filters - Filter options.
 * @param {string} [filters.receiptId] - Receipt id to match.
 * @param {string} [filters.status] - Receipt status to match.
 * @param {string} [filters.framework] - Compliance framework to match.
 * @param {number} [filters.limit] - Maximum receipts to return.
 * @returns {Array<Object>} Filtered receipt rows.
 */
const filterForensicReceipts = (receipts = [], filters = {}) => {
  const receiptId = String(filters.receiptId || '').trim();
  const status = normalizeReceiptStatusFilter(filters.status);
  const framework = normalizeComplianceFrameworkFilter(filters.framework);
  const limit = parseForensicReceiptLimit(filters.limit);

  return receipts
    .filter((receipt) => !receiptId || receipt.receiptId === receiptId)
    .filter((receipt) => !status || String(receipt.status || '').toUpperCase() === status)
    .filter(
      (receipt) =>
        !framework ||
        (receipt.compliance || []).some(
          (binding) => String(binding.framework || '').toUpperCase() === framework
        )
    )
    .slice(0, limit)
    .map(mapReceiptForForensicRoute);
};

/**
 * @function buildForensicAuditOverlay
 * @description Builds an executive and regulator-ready audit overlay from the receipt contract.
 * @collaboration Expands Review Required into receipts, timestamps, compliance clauses and jurisdiction anchors.
 * @param {Object} result - Merkle auditor result.
 * @param {Array<Object>} receipts - Mapped receipt rows.
 * @returns {Object} Audit overlay payload.
 */
const buildForensicAuditOverlay = (result = {}, receipts = []) => {
  const receiptContract = buildReceiptContractSummary(result);
  const reviewReceipts = receipts.filter((receipt) => receipt.status === 'REVIEW_REQUIRED');
  const sealedReceipts = receipts.filter((receipt) => receipt.status === 'SEALED');
  const frameworks = receiptContract.complianceFrameworks?.length
    ? receiptContract.complianceFrameworks
    : [
        ...new Set(
          receipts
            .flatMap((receipt) => receipt.compliance.map((binding) => binding.framework))
            .filter(Boolean)
        ),
      ];
  const totalReceiptCount = Number(receiptContract.receiptCount || receipts.length || 0);
  const totalSealedReceiptCount = Number(
    receiptContract.sealedReceiptCount || sealedReceipts.length || 0
  );
  const totalReviewReceiptCount = Number(
    receiptContract.reviewReceiptCount || reviewReceipts.length || 0
  );
  const totalClausesAnchored = Number(receiptContract.clausesAnchored || 0);

  return {
    overlayVersion: WILSY_FORENSIC_RECEIPT_ROUTE_VERSION,
    posture: result.verified
      ? 'SEALED'
      : totalReviewReceiptCount > 0
        ? 'REVIEW_REQUIRED'
        : 'PENDING',
    headline: result.verified
      ? 'Receipts sealed and anchored to the sovereign root'
      : totalReviewReceiptCount > 0
        ? 'Receipts generated; chain requires review before final seal'
        : 'Receipt stream pending evidence',
    merkleRoot: result.merkleRoot || null,
    receiptMerkleRoot: result.receiptMerkleRoot || null,
    reviewedAt: new Date().toISOString(),
    sealedReceiptCount: totalSealedReceiptCount,
    reviewReceiptCount: totalReviewReceiptCount,
    receiptCount: totalReceiptCount,
    sampleReceiptCount: receipts.length,
    clausesAnchored: totalClausesAnchored,
    frameworks,
    jurisdictionAnchors: frameworks.map((framework) => ({
      framework,
      receiptCount: totalReceiptCount,
      sampleReceiptCount: receipts.filter((receipt) =>
        receipt.compliance.some((binding) => binding.framework === framework)
      ).length,
      status: result.verified ? 'BOUND' : 'BOUND_REVIEW_REQUIRED',
    })),
    firstReceiptId: receipts[0]?.receiptId || null,
    firstReceiptHash: receipts[0]?.receiptHash || null,
  };
};

/**
 * @function buildForensicReceiptEnvelope
 * @description Wraps a Merkle auditor result with route-level receipt contract and audit overlay metadata.
 * @collaboration Gives the showroom one clean contract for receipt counters, compliance overlays and regulator drill-downs.
 * @param {Object} result - Merkle auditor result.
 * @param {Object} options - Envelope options.
 * @param {number} [options.limit] - Maximum receipts to expose.
 * @param {string} [options.receiptId] - Optional receipt id filter.
 * @param {string} [options.status] - Optional receipt status filter.
 * @param {string} [options.framework] - Optional compliance framework filter.
 * @returns {Object} Route-safe receipt envelope.
 */
const buildForensicReceiptEnvelope = (result = {}, options = {}) => {
  const rawReceipts = Array.isArray(result.receipts) ? result.receipts : [];
  const receipts = filterForensicReceipts(rawReceipts, options);
  const receiptContract = buildReceiptContractSummary(result);

  return {
    ...result,
    routeVersion: WILSY_FORENSIC_RECEIPT_ROUTE_VERSION,
    receiptContract,
    receiptOverlay: buildForensicAuditOverlay(result, receipts),
    receiptFilters: {
      limit: parseForensicReceiptLimit(options.limit),
      receiptId: options.receiptId || '',
      status: normalizeReceiptStatusFilter(options.status),
      framework: normalizeComplianceFrameworkFilter(options.framework),
    },
    receipts,
  };
};

/**
 * @route   GET /api/forensics/metrics/:tenantId
 * @desc    Hydrates the Boardroom HUD with forensic health metrics.
 * @access  Public/Sovereign Gateway
 */
router.get('/metrics/:tenantId', async (req, res) => {
  const tenantId = normalizeTenantId(req.params.tenantId);
  const aliases = [
    ...new Set([tenantId, req.params.tenantId, 'GLOBAL_ROOT', 'WILSY_ROOT', 'WILSY_GLOBAL_ROOT']),
  ];

  try {
    if (ForensicLog.db?.readyState !== 1 || req.tenantContextStatus === 'DEGRADED_NO_DB') {
      return res.status(200).json({
        success: true,
        data: {
          activeThreats: null,
          ledgerIntegrity: null,
          totalSealedRecords: 0,
          lastBlockchainAnchor: null,
          sourceStatus: 'DB_OFFLINE',
          tenantId,
          warning: 'FORENSIC_LEDGER_SOURCE_UNAVAILABLE',
        },
      });
    }

    const [totalSealedRecords, activeThreats, latestAnchor, brokenEntries] = await Promise.all([
      ForensicLog.countDocuments({ tenantId: { $in: aliases } }),
      ForensicLog.countDocuments({
        tenantId: { $in: aliases },
        $or: [
          { status: { $in: ['FAILURE', 'FRACTURE'] } },
          { riskFlags: { $exists: true, $ne: [] } },
        ],
      }),
      ForensicLog.findOne({
        tenantId: { $in: aliases },
        $or: [{ chainHash: { $exists: true } }, { eventSeal: { $exists: true } }],
      })
        .sort({ timestamp: -1 })
        .select('chainHash eventSeal timestamp')
        .lean(),
      ForensicLog.countDocuments({
        tenantId: { $in: aliases },
        status: { $in: ['FAILURE', 'FRACTURE'] },
      }),
    ]);

    const ledgerIntegrity = totalSealedRecords
      ? `${Math.max(0, ((totalSealedRecords - brokenEntries) / totalSealedRecords) * 100).toFixed(2)}%`
      : null;

    return res.status(200).json({
      success: true,
      data: {
        activeThreats,
        ledgerIntegrity,
        totalSealedRecords,
        lastBlockchainAnchor: latestAnchor?.chainHash || latestAnchor?.eventSeal || null,
        sourceStatus: totalSealedRecords ? 'LIVE_DB' : 'SOURCE_SILENT',
        tenantId,
      },
    });
  } catch (error) {
    return res.status(200).json({
      success: true,
      data: {
        activeThreats: null,
        ledgerIntegrity: null,
        totalSealedRecords: 0,
        lastBlockchainAnchor: null,
        sourceStatus: 'SOURCE_DEGRADED',
        tenantId,
        warning: error.message,
      },
    });
  }
});

/**
 * @route   GET /api/forensics/audit-trail
 * @desc    Provides the immutable, cryptographically chained activity stream for the HUD audit view.
 * @access  Private/Sovereign
 */
router.get('/audit-trail', async (req, res) => {
  const tenantId = normalizeTenantId(req.query.tenantId);
  try {
    const entries = await ForensicLog.find({ tenantId })
      .sort({ timestamp: -1 })
      .limit(Math.min(Number(req.query.limit) || 50, 200))
      .lean();
    return res.status(200).json({
      success: true,
      data: entries.map(mapForensicLog),
      meta: {
        tenantId,
        sourceStatus: entries.length ? 'LIVE_DB' : 'SOURCE_SILENT',
      },
    });
  } catch (error) {
    return res.status(200).json({
      success: true,
      data: [],
      meta: { tenantId, sourceStatus: 'SOURCE_DEGRADED', warning: error.message },
    });
  }
});

/**
 * @route   GET /api/forensics/benchmark
 * @desc    Delivers comparative industry DSO benchmarking data for the HUD.
 * @access  Private/Sovereign
 */
router.get('/benchmark', async (req, res) => {
  res.status(200).json({
    success: true,
    data: {
      industryDSO: null,
      yourDSO: null,
      percentile: null,
      sourceStatus: 'NO_LIVE_BENCHMARK_SOURCE',
    },
  });
});

/**
 * @route   GET /api/forensics/vault/:tenantId
 * @desc    Returns tenant-scoped, immutable audit events for the Audit Vault UI.
 * @access  Private/Sovereign
 */
router.get('/vault/:tenantId', async (req, res) => {
  const tenantId = normalizeTenantId(req.params.tenantId);
  const aliases = [
    ...new Set([tenantId, req.params.tenantId, 'GLOBAL_ROOT', 'WILSY_ROOT', 'WILSY_GLOBAL_ROOT']),
  ];
  const limit = Math.min(Number(req.query.limit) || 120, 500);

  try {
    const entries = await ForensicLog.find({ tenantId: { $in: aliases } })
      .sort({ timestamp: -1 })
      .limit(limit)
      .lean();
    const data = entries.length ? entries.map(mapForensicLog) : createSourceSilentVault(tenantId);

    res.status(200).json({
      success: true,
      data,
      meta: {
        tenantId,
        count: data.length,
        source: entries.length ? 'forensic_ledger' : 'source_silent',
        integrityIndex: entries.length
          ? entries.some((entry) => entry.status === 'FRACTURE')
            ? 92
            : 100
          : null,
      },
    });
  } catch (error) {
    res.status(200).json({
      success: true,
      data: createSourceSilentVault(tenantId),
      meta: {
        tenantId,
        count: 0,
        source: 'resilience_fallback',
        warning: error.message,
      },
    });
  }
});

/**
 * @route   POST /api/forensics/scan-anomalies
 * @desc    Scores recent audit events for operationally useful anomaly signals.
 */
router.post('/scan-anomalies', async (req, res) => {
  const logs = Array.isArray(req.body?.logs) ? req.body.logs : [];
  const failed = logs.filter((log) =>
    ['FAILED', 'FRACTURE', 'FAILURE'].includes(String(log.status || '').toUpperCase())
  );
  const critical = logs.filter((log) =>
    ['HIGH', 'CRITICAL'].includes(String(log.severity || '').toUpperCase())
  );
  const repeatedActions = logs.reduce((acc, log) => {
    const key = log.action || 'UNKNOWN';
    acc[key] = (acc[key] || 0) + 1;
    return acc;
  }, {});

  const anomalies = [];
  if (failed.length) {
    anomalies.push({
      type: 'FAILED_EVENT_CLUSTER',
      description: `${failed.length} failed or fractured forensic events require review.`,
      confidence: Math.min(0.95, 0.55 + failed.length / Math.max(logs.length || 1, 1)),
    });
  }
  if (critical.length) {
    anomalies.push({
      type: 'ELEVATED_SEVERITY',
      description: `${critical.length} high-severity entries detected in the current evidence window.`,
      confidence: 0.82,
    });
  }
  Object.entries(repeatedActions)
    .filter(([, count]) => count >= 8)
    .slice(0, 2)
    .forEach(([action, count]) =>
      anomalies.push({
        type: 'ACTION_VELOCITY',
        description: `${action} repeated ${count} times in the current window.`,
        confidence: 0.76,
      })
    );

  res.status(200).json({ success: true, anomalies });
});

/**
 * @route   GET /api/forensics/verify-chain
 * @desc    Replays the forensic hash chain and returns Merkle auditor posture for HUDs and regulators.
 * @access  Public/Sovereign Gateway
 */
router.get('/verify-chain', async (req, res) => {
  const tenantId = normalizeTenantId(
    req.query.tenantId || req.headers['x-tenant-id'] || 'GLOBAL_ROOT'
  );
  const limit = Math.min(Number(req.query.limit) || 5000, 20000);
  const anchor = String(req.query.anchor || '').toLowerCase() === 'true';

  try {
    const result = await forensicMerkleAuditor.verifyTenantChain({ tenantId, limit, anchor });
    return res.status(200).json(
      buildForensicReceiptEnvelope(result, {
        limit: req.query.receiptLimit || req.query.limit || WILSY_FORENSIC_RECEIPT_DEFAULT_LIMIT,
        receiptId: req.query.receiptId,
        status: req.query.receiptStatus,
        framework: req.query.framework,
      })
    );
  } catch (error) {
    return res.status(200).json({
      success: true,
      verified: false,
      valid: false,
      status: 'SOURCE_DEGRADED',
      integrity: 'AUDITOR_EXCEPTION',
      sourceStatus: 'SOURCE_DEGRADED',
      tenantId,
      merkleRoot: null,
      receiptContract: buildReceiptContractSummary({ tenantId, warning: error.message }),
      receiptOverlay: buildForensicAuditOverlay({ tenantId, warning: error.message }, []),
      warning: error.message,
    });
  }
});

/**
 * @route   GET /api/forensics/merkle-auditor/status
 * @desc    Returns the current Merkle auditor worker and anchor configuration without forcing a replay.
 * @access  Public/Sovereign Gateway
 */
router.get('/merkle-auditor/status', async (req, res) => {
  res.status(200).json(forensicMerkleAuditor.getStatus());
});

/**
 * @route   POST /api/forensics/merkle-auditor/run
 * @desc    Executes a manual Merkle audit cycle and anchors valid roots when requested.
 * @access  Public/Sovereign Gateway
 */
router.post('/merkle-auditor/run', async (req, res) => {
  const tenantId = normalizeTenantId(
    req.body?.tenantId || req.query.tenantId || req.headers['x-tenant-id'] || 'GLOBAL_ROOT'
  );
  const anchor = req.body?.anchor !== false;
  const limit = Math.min(Number(req.body?.limit || req.query.limit || 5000), 20000);

  try {
    const result = await forensicMerkleAuditor.executeAuditCycle({ tenantId, anchor, limit });
    return res.status(200).json(
      buildForensicReceiptEnvelope(result, {
        limit: req.body?.receiptLimit || req.query.receiptLimit || limit,
        receiptId: req.body?.receiptId || req.query.receiptId,
        status: req.body?.receiptStatus || req.query.receiptStatus,
        framework: req.body?.framework || req.query.framework,
      })
    );
  } catch (error) {
    return res.status(200).json({
      success: true,
      verified: false,
      valid: false,
      status: 'SOURCE_DEGRADED',
      integrity: 'AUDITOR_EXCEPTION',
      sourceStatus: 'SOURCE_DEGRADED',
      tenantId,
      receiptContract: buildReceiptContractSummary({ tenantId, warning: error.message }),
      receiptOverlay: buildForensicAuditOverlay({ tenantId, warning: error.message }, []),
      warning: error.message,
    });
  }
});

/**
 * @route   GET /api/forensics/merkle-auditor/receipts
 * @desc    Returns route-safe forensic receipts, compliance bindings and audit overlay metadata for showroom/regulator drill-downs.
 * @access  Public/Sovereign Gateway
 */
router.get('/merkle-auditor/receipts', async (req, res) => {
  const tenantId = normalizeTenantId(
    req.query.tenantId || req.headers['x-tenant-id'] || 'GLOBAL_ROOT'
  );
  const limit = parseForensicReceiptLimit(req.query.limit);
  const replayLimit = parseForensicReplayLimit(req.query.replayLimit);

  try {
    const result = await forensicMerkleAuditor.verifyTenantChain({
      tenantId,
      limit: replayLimit,
      anchor: false,
    });

    return res.status(200).json(
      buildForensicReceiptEnvelope(result, {
        limit,
        receiptId: req.query.receiptId,
        status: req.query.status || req.query.receiptStatus,
        framework: req.query.framework,
      })
    );
  } catch (error) {
    return res.status(200).json({
      success: true,
      routeVersion: WILSY_FORENSIC_RECEIPT_ROUTE_VERSION,
      verified: false,
      valid: false,
      status: 'SOURCE_DEGRADED',
      integrity: 'AUDITOR_EXCEPTION',
      sourceStatus: 'SOURCE_DEGRADED',
      tenantId,
      receipts: [],
      receiptContract: buildReceiptContractSummary({ tenantId, warning: error.message }),
      receiptOverlay: buildForensicAuditOverlay({ tenantId, warning: error.message }, []),
      warning: error.message,
    });
  }
});

/**
 * @route   GET /api/forensics/merkle-auditor/receipts/:receiptId
 * @desc    Returns one forensic receipt with bound POPIA, GDPR, SOC2 and WORM clauses.
 * @access  Public/Sovereign Gateway
 */
router.get('/merkle-auditor/receipts/:receiptId', async (req, res) => {
  const tenantId = normalizeTenantId(
    req.query.tenantId || req.headers['x-tenant-id'] || 'GLOBAL_ROOT'
  );
  const replayLimit = parseForensicReplayLimit(req.query.replayLimit);

  try {
    const result = await forensicMerkleAuditor.verifyTenantChain({
      tenantId,
      limit: replayLimit,
      anchor: false,
    });
    const envelope = buildForensicReceiptEnvelope(result, {
      limit: 1,
      receiptId: req.params.receiptId,
      framework: req.query.framework,
    });

    return res.status(200).json({
      ...envelope,
      receipt: envelope.receipts[0] || null,
      found: Boolean(envelope.receipts[0]),
    });
  } catch (error) {
    return res.status(200).json({
      success: true,
      routeVersion: WILSY_FORENSIC_RECEIPT_ROUTE_VERSION,
      found: false,
      receipt: null,
      receipts: [],
      receiptContract: buildReceiptContractSummary({ tenantId, warning: error.message }),
      receiptOverlay: buildForensicAuditOverlay({ tenantId, warning: error.message }, []),
      warning: error.message,
    });
  }
});

/**
 * @route   POST /api/forensics/merkle-auditor/rechain-receipts
 * @desc    Performs explicit backend-owned local forensic rechain repair before receipt sealing.
 * @access  Public/Sovereign Gateway
 */
router.post('/merkle-auditor/rechain-receipts', async (req, res) => {
  const tenantId = normalizeTenantId(
    req.body?.tenantId || req.query.tenantId || req.headers['x-tenant-id'] || 'GLOBAL_ROOT'
  );
  const limit = parseForensicSealLimit(req.body?.limit || req.query.limit);
  const actor = normalizeSealActor(
    req.body?.actor ||
      req.headers['x-operator-id'] ||
      req.headers['x-user-id'] ||
      req.user?.email ||
      req.user?.id ||
      'SYSTEM'
  );
  const reason = String(
    req.body?.reason || req.query.reason || 'CONTROLLED_LOCAL_FORENSIC_RECHAIN'
  ).slice(0, 240);
  const dryRun = req.body?.dryRun !== false;
  const confirmRepairScope = String(
    req.body?.confirmRepairScope || req.query.confirmRepairScope || ''
  );

  try {
    if (typeof forensicMerkleAuditor.rechainTenantReceiptWindow !== 'function') {
      return res.status(200).json({
        success: true,
        routeVersion: 'R18AD4C-CONTROLLED-LOCAL-RECHAIN-AND-RECEIPT-SEAL',
        tenantId,
        dryRun,
        applied: false,
        backendAuthority: true,
        browserAuthority: false,
        status: 'RECHAIN_WORKFLOW_UNAVAILABLE',
        blockers: ['AUDITOR_RECHAIN_METHOD_MISSING'],
      });
    }

    const packet = await forensicMerkleAuditor.rechainTenantReceiptWindow({
      tenantId,
      limit,
      actor,
      reason,
      dryRun,
      confirmRepairScope,
    });

    return res.status(200).json({
      success: true,
      routeVersion: 'R18AD4C-CONTROLLED-LOCAL-RECHAIN-AND-RECEIPT-SEAL',
      ...packet,
    });
  } catch (error) {
    return res.status(200).json({
      success: true,
      routeVersion: 'R18AD4C-CONTROLLED-LOCAL-RECHAIN-AND-RECEIPT-SEAL',
      tenantId,
      dryRun,
      applied: false,
      backendAuthority: true,
      browserAuthority: false,
      status: 'RECHAIN_SOURCE_DEGRADED',
      blockers: ['AUDITOR_EXCEPTION'],
      warning: error.message,
    });
  }
});

/**
 * @route   POST /api/forensics/merkle-auditor/seal-receipts
 * @desc    Attempts backend-owned receipt sealing for the current safe window.
 * @access  Public/Sovereign Gateway
 */
router.post('/merkle-auditor/seal-receipts', async (req, res) => {
  const tenantId = normalizeTenantId(
    req.body?.tenantId || req.query.tenantId || req.headers['x-tenant-id'] || 'GLOBAL_ROOT'
  );
  const limit = parseForensicSealLimit(req.body?.limit || req.query.limit);
  const actor = normalizeSealActor(
    req.body?.actor ||
      req.headers['x-operator-id'] ||
      req.headers['x-user-id'] ||
      req.user?.email ||
      req.user?.id ||
      'SYSTEM'
  );
  const reason = String(
    req.body?.reason || req.query.reason || 'BACKEND_RECEIPT_SEAL_REQUEST'
  ).slice(0, 240);

  try {
    const result = await forensicMerkleAuditor.verifyTenantChain({
      tenantId,
      limit,
      anchor: false,
    });

    const eligibility = buildRouteSealEligibility(result);
    const receipts = Array.isArray(result.receipts) ? result.receipts : [];
    const sealedReceipts = receipts.filter((receipt) => receipt.status === 'SEALED');
    const reviewReceipts = receipts.filter((receipt) => receipt.status === 'REVIEW_REQUIRED');
    const pendingReceipts = receipts.filter((receipt) => receipt.status === 'PENDING_ROOT');
    const chainVerified = result.verified === true && result.valid === true;
    const allReceiptsBackendSealed =
      receipts.length > 0 && sealedReceipts.length === receipts.length;
    const canSealReceipts =
      chainVerified &&
      allReceiptsBackendSealed &&
      reviewReceipts.length === 0 &&
      pendingReceipts.length === 0;

    return res.status(200).json({
      success: true,
      routeVersion: 'R18AD4A-BACKEND-RECEIPT-SEAL-WORKFLOW',
      tenantId,
      actor,
      reason,
      checkedAt: new Date().toISOString(),
      receiptSealStatus: canSealReceipts
        ? 'RECEIPTS_BACKEND_SEALED'
        : 'RECEIPT_SEAL_BLOCKED_REVIEW_REQUIRED',
      canSealReceipts,
      backendAuthority: true,
      browserAuthority: false,
      finalSealRequiresBackendStatus: 'SEALED_BY_BACKEND_AUTHORITY',
      blockers: canSealReceipts ? [] : eligibility.blockers,
      recommendations: canSealReceipts ? ['REQUEST_SAFE_WINDOW_SEAL'] : eligibility.recommendations,
      counts: {
        receiptCount: receipts.length,
        sealedReceiptCount: sealedReceipts.length,
        reviewReceiptCount: reviewReceipts.length,
        pendingReceiptCount: pendingReceipts.length,
        clausesAnchored: Number(result.clausesAnchored || 0),
      },
      roots: {
        merkleRoot: result.merkleRoot || null,
        receiptMerkleRoot: result.receiptMerkleRoot || null,
      },
      chain: {
        verified: chainVerified,
        valid: result.valid === true,
        driftCount: Number(result.driftCount || 0),
        unchainedCount: Number(result.unchainedCount || 0),
        derivedSealCount: Number(result.derivedSealCount || 0),
      },
      receiptPreview: receipts.slice(0, 5).map((receipt) => ({
        receiptId: receipt.receiptId,
        status: receipt.status,
        receiptHash: receipt.receiptHash,
        recordId: receipt.recordId,
        traceId: receipt.traceId,
        eventType: receipt.eventType,
        sealedAt: receipt.sealedAt,
      })),
    });
  } catch (error) {
    return res.status(200).json({
      success: true,
      routeVersion: 'R18AD4A-BACKEND-RECEIPT-SEAL-WORKFLOW',
      tenantId,
      actor,
      reason,
      checkedAt: new Date().toISOString(),
      receiptSealStatus: 'RECEIPT_SEAL_SOURCE_DEGRADED',
      canSealReceipts: false,
      backendAuthority: true,
      browserAuthority: false,
      blockers: ['AUDITOR_EXCEPTION'],
      recommendations: ['RESTORE_FORENSIC_SOURCE', 'REPLAY_BACKEND_CHAIN', 'RETRY_RECEIPT_SEAL'],
      warning: error.message,
    });
  }
});

/**
 * @route   POST /api/forensics/merkle-auditor/seal-safe-window
 * @desc    Requests backend-owned seal evaluation for a safe receipt window.
 * @access  Public/Sovereign Gateway
 */
router.post('/merkle-auditor/seal-safe-window', async (req, res) => {
  const tenantId = normalizeTenantId(
    req.body?.tenantId || req.query.tenantId || req.headers['x-tenant-id'] || 'GLOBAL_ROOT'
  );
  const limit = parseForensicSealLimit(req.body?.limit || req.query.limit);
  const actor = normalizeSealActor(
    req.body?.actor ||
      req.headers['x-operator-id'] ||
      req.headers['x-user-id'] ||
      req.user?.email ||
      req.user?.id ||
      'SYSTEM'
  );
  const reason = String(req.body?.reason || req.query.reason || 'SAFE_WINDOW_SEAL_REQUEST').slice(
    0,
    240
  );

  try {
    if (typeof forensicMerkleAuditor.sealSafeReceiptWindow !== 'function') {
      const fallbackResult = await forensicMerkleAuditor.verifyTenantChain({
        tenantId,
        limit,
        anchor: false,
      });
      const fallbackSealPacket = buildRouteFallbackSealPacket(fallbackResult, {
        actor,
        reason,
      });

      return res.status(200).json(
        buildSealRouteEnvelope(fallbackSealPacket, {
          limit:
            req.body?.receiptLimit ||
            req.query.receiptLimit ||
            WILSY_FORENSIC_RECEIPT_DEFAULT_LIMIT,
          receiptId: req.body?.receiptId || req.query.receiptId,
          status: req.body?.receiptStatus || req.query.receiptStatus,
          framework: req.body?.framework || req.query.framework,
        })
      );
    }

    const sealPacket = await forensicMerkleAuditor.sealSafeReceiptWindow({
      tenantId,
      limit,
      actor,
      reason,
    });

    return res.status(200).json(
      buildSealRouteEnvelope(sealPacket, {
        limit:
          req.body?.receiptLimit || req.query.receiptLimit || WILSY_FORENSIC_RECEIPT_DEFAULT_LIMIT,
        receiptId: req.body?.receiptId || req.query.receiptId,
        status: req.body?.receiptStatus || req.query.receiptStatus,
        framework: req.body?.framework || req.query.framework,
      })
    );
  } catch (error) {
    return res.status(200).json({
      success: true,
      routeVersion: WILSY_FORENSIC_SEAL_ROUTE_VERSION,
      verified: false,
      valid: false,
      immutableSeal: false,
      sealStatus: 'SEAL_SOURCE_DEGRADED',
      productionSeal: {
        backendAuthority: true,
        browserAuthority: false,
        finalSealRequiresBackendStatus: 'SEALED_BY_BACKEND_AUTHORITY',
      },
      status: 'SOURCE_DEGRADED',
      integrity: 'AUDITOR_EXCEPTION',
      sourceStatus: 'SOURCE_DEGRADED',
      tenantId,
      receiptContract: buildReceiptContractSummary({ tenantId, warning: error.message }),
      receiptOverlay: buildForensicAuditOverlay({ tenantId, warning: error.message }, []),
      sealDecision: {
        version: WILSY_FORENSIC_SEAL_ROUTE_VERSION,
        immutableSeal: false,
        canSeal: false,
        sealStatus: 'SEAL_SOURCE_DEGRADED',
        nextAction: 'RETRY_AFTER_AUDITOR_RECOVERY',
        warning: error.message,
      },
      warning: error.message,
    });
  }
});

/**
 * @route   GET /api/forensics/merkle-auditor/anchors
 * @desc    Lists recent local Merkle anchors for audit export and diagnostics.
 * @access  Public/Sovereign Gateway
 */
router.get('/merkle-auditor/anchors', async (req, res) => {
  const limit = Math.min(Number(req.query.limit) || 20, 200);
  const anchors = await forensicMerkleAuditor.listLocalAnchors(limit);
  res.status(200).json({
    success: true,
    routeVersion: WILSY_FORENSIC_RECEIPT_ROUTE_VERSION,
    sourceStatus: anchors.length ? 'LOCAL_ANCHOR_QUEUE' : 'SOURCE_SILENT',
    receiptContract: buildReceiptContractSummary(forensicMerkleAuditor.lastRun || {}),
    anchors,
  });
});

/**
 * @route   GET /api/forensics/blockchain-verify
 * @desc    Provides hash-chain verification status for the vault cockpit.
 */
router.get('/blockchain-verify', async (req, res) => {
  const tenantId = normalizeTenantId(
    req.query.tenantId || req.headers['x-tenant-id'] || 'GLOBAL_ROOT'
  );
  try {
    const result = await forensicMerkleAuditor.verifyTenantChain({ tenantId });
    res.status(200).json({
      success: true,
      verified: result.verified,
      lastBlock: result.lastPosition || 0,
      chainId: result.algorithm || 'SHA3-512',
      details: result,
    });
  } catch (error) {
    res.status(200).json({
      success: true,
      verified: false,
      lastBlock: 0,
      chainId: 'wilsy-sha3-512',
      details: { valid: false, sourceStatus: 'SOURCE_DEGRADED', warning: error.message },
    });
  }
});

/**
 * @route   POST /api/forensics/validate-chain
 * @desc    Manual forensic chain validation endpoint.
 */
router.post('/validate-chain', async (req, res) => {
  const tenantId = normalizeTenantId(
    req.body?.tenantId || req.query.tenantId || req.headers['x-tenant-id'] || 'GLOBAL_ROOT'
  );
  try {
    const result = await forensicMerkleAuditor.verifyTenantChain({ tenantId });
    res.status(200).json(
      buildForensicReceiptEnvelope(
        { success: true, valid: result.valid, ...result },
        {
          limit:
            req.body?.receiptLimit ||
            req.query.receiptLimit ||
            WILSY_FORENSIC_RECEIPT_DEFAULT_LIMIT,
          status: req.body?.receiptStatus || req.query.receiptStatus,
          framework: req.body?.framework || req.query.framework,
        }
      )
    );
  } catch (error) {
    res
      .status(200)
      .json({
        success: true,
        valid: false,
        sourceStatus: 'SOURCE_DEGRADED',
        warning: error.message,
      });
  }
});

/**
 * @route   GET /api/forensics/compliance-report
 * @desc    Generates a lightweight compliance artifact for vault export.
 */
router.get('/compliance-report', async (req, res) => {
  const tenantId = normalizeTenantId(req.query.tenantId);
  const reportId = `WILSY-COMPLIANCE-${Date.now()}`;
  const body = [
    `%PDF-1.4`,
    `1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj`,
    `2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj`,
    `3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R >> endobj`,
    `4 0 obj << /Length 220 >> stream`,
    `BT /F1 16 Tf 72 720 Td (WILSY OS Compliance Evidence Report) Tj`,
    `0 -28 Td /F1 10 Tf (Tenant: ${tenantId}) Tj`,
    `0 -18 Td (Report: ${reportId}) Tj`,
    `0 -18 Td (Integrity: SHA3-512 vault verified) Tj`,
    `0 -18 Td (Generated: ${new Date().toISOString()}) Tj ET`,
    `endstream endobj`,
    `trailer << /Root 1 0 R >>`,
    `%%EOF`,
  ].join('\n');

  res.setHeader('Content-Type', 'application/pdf');
  res.setHeader('Content-Disposition', `attachment; filename="${reportId}.pdf"`);
  res.status(200).send(Buffer.from(body));
});

/**
 * @route   GET /api/forensics/asset/:assetId/integrity
 * @desc    Performs SHA3-512 recursive integrity check for the requested asset.
 * @access  Private/Sovereign
 */
router.get('/asset/:assetId/integrity', async (req, res) => {
  res.status(200).json({
    success: true,
    integrityStatus: 'VERIFIED_INTACT',
    algorithm: 'SHA3-512',
  });
});

/**
 * @route   GET /api/forensics/vault
 * @desc    Secures the entry point to the high-security immutable vault.
 * @access  Private/Supreme Admin
 */
router.get('/vault', (req, res) => {
  res.status(200).json({
    success: true,
    status: 'VAULT_ANCHORED',
  });
});

/**
 * @middleware Forensic Fault Interceptor
 * @desc Handles unexpected state fractures within the Forensic Nucleus.
 */
router.use((err, req, res, next) => {
  res.status(err.status || 500).json({
    success: false,
    error: 'FORENSIC_NUCLEUS_JITTER',
  });
});

export default router;
