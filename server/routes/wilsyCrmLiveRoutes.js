/* eslint-disable */
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import crypto from 'crypto';
import {
  getWilsyCrmLiveAllowedCollections,
  listWilsyCrmLiveCollectionRecords,
} from '../services/wilsyCrmLiveSourceService.js';
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - CRM LIVE ROUTES                                                                                             ║
 * ║ /api/crm/live/source-posture | /api/crm/live/:collection                                                               ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 *
 * @fileoverview Live CRM source routes.
 */

import express from 'express';
import {
  buildSourcePosture,
  getAllowedCollections,
  listCrmCollection,
} from '../services/wilsyCrmLiveSourceService.js';

const router = express.Router();

/* R91K144_SOURCE_SIGNATURE_FABRIC_BACKEND_CONTRACT
   Backend-owned source-to-signature fabric contract for /api/crm/live/source-guide. */

/**
 * @function sanitizeWilsyR91K144Text
 * @description Normalizes backend Source Guide values for the source-signature fabric contract without inventing fake data.
 * @collaboration Used by the CRM live route response middleware to keep Wilsy AI fabric copy backend-owned.
 */
function sanitizeWilsyR91K144Text(...values) {
  for (const value of values) {
    if (value === null || value === undefined) continue;
    const nextValue = String(value).trim();
    if (nextValue.length > 0) return nextValue;
  }

  return 'Unavailable';
}

/**
 * @function normalizeWilsyR91K144Number
 * @description Converts live backend Source Guide values into finite numeric contract fields.
 * @collaboration Keeps sourceSignatureFabric counts and readiness derived from backend telemetry only.
 */
function normalizeWilsyR91K144Number(...values) {
  for (const value of values) {
    const numericValue = Number(value);
    if (Number.isFinite(numericValue)) return numericValue;
  }

  return 0;
}

/**
 * @function readWilsyR91K144Path
 * @description Safely reads nested Source Guide fields for the source-signature fabric contract.
 * @collaboration Prevents route handlers from depending on brittle optional property chains.
 */
function readWilsyR91K144Path(source, pathKey, fallback = null) {
  if (!source || !pathKey) return fallback;

  const parts = String(pathKey).split('.');
  let cursor = source;

  for (const part of parts) {
    if (cursor && Object.prototype.hasOwnProperty.call(cursor, part)) {
      cursor = cursor[part];
    } else {
      return fallback;
    }
  }

  return cursor === undefined || cursor === null || cursor === '' ? fallback : cursor;
}

/**
 * @function buildWilsyR91K144SourceSignatureFabricNodes
 * @description Builds live fabric nodes from the existing Source Guide response body.
 * @collaboration Supplies Source, Evidence, Governance, Revenue and Signature nodes to the frontend fabric.
 */
function buildWilsyR91K144SourceSignatureFabricNodes(payload, contractContext) {
  const sourcePosture = payload?.sourcePosture || {};
  const sourceList = Array.isArray(sourcePosture.sources)
    ? sourcePosture.sources
    : Array.isArray(sourcePosture.sourceHealth)
      ? sourcePosture.sourceHealth
      : [];

  /**
   * @function findSource
   * @description Resolves a live Source Guide source record by semantic label for the source-signature fabric contract.
   * @collaboration Used by R91K144 backend fabric nodes to derive Source, Evidence and Revenue posture from existing telemetry.
   */
  const findSource = (needle) =>
    sourceList.find((source) => {
      const label = [
        source?.label,
        source?.name,
        source?.key,
        source?.collection,
        source?.route,
        source?.endpoint,
        source?.modelName,
        source?.model,
      ]
        .filter(Boolean)
        .join(' ')
        .toLowerCase();

      return label.includes(String(needle).toLowerCase());
    }) || null;

  const emailSource = findSource('email') || findSource('lead');
  const evidenceSource = findSource('evidence') || findSource('anchor');
  const revenueSource = findSource('revenue') || findSource('deal') || findSource('pipeline');

  const sourceRecordCount = normalizeWilsyR91K144Number(
    emailSource?.recordCount,
    emailSource?.count,
    emailSource?.records,
    emailSource?.total
  );

  const evidenceCount = normalizeWilsyR91K144Number(
    evidenceSource?.recordCount,
    evidenceSource?.count,
    evidenceSource?.records,
    evidenceSource?.total,
    payload?.evidenceAnchors,
    payload?.sourceGuideReceipt?.anchors
  );

  return [
    {
      id: 'source',
      label: 'Source',
      status:
        sourceRecordCount > 0 || emailSource?.routeLive || emailSource?.live ? 'LIVE' : 'PENDING',
      value: sanitizeWilsyR91K144Text(
        emailSource?.status,
        emailSource?.sourceStatus,
        sourceRecordCount > 0 ? 'live' : 'pending'
      ),
      detail: `${sourceRecordCount} CRM records`,
      route: sanitizeWilsyR91K144Text(
        emailSource?.route,
        emailSource?.endpoint,
        '/api/crm/live/leads'
      ),
    },
    {
      id: 'evidence',
      label: 'Evidence',
      status: evidenceCount > 0 ? 'ANCHORED' : 'PENDING',
      value: evidenceCount > 0 ? `${evidenceCount} anchors` : 'anchor expansion pending',
      detail: `${evidenceCount} governed anchors`,
      route: sanitizeWilsyR91K144Text(
        evidenceSource?.route,
        evidenceSource?.endpoint,
        'source-guide evidence posture'
      ),
    },
    {
      id: 'governance',
      label: 'Governance',
      status: contractContext.readiness >= 60 ? 'CONTROLLED' : 'EXPAND',
      value: `${contractContext.readiness}%`,
      detail: sanitizeWilsyR91K144Text(contractContext.postureGrade, 'governance posture pending'),
      route: 'source-guide readiness algorithm',
    },
    {
      id: 'revenue',
      label: 'Revenue',
      status: revenueSource?.routeLive || revenueSource?.live ? 'LIVE' : 'STANDBY',
      value: sanitizeWilsyR91K144Text(contractContext.weightedValueLabel, 'R 0'),
      detail: sanitizeWilsyR91K144Text(
        revenueSource?.status,
        revenueSource?.sourceStatus,
        'pipeline standby'
      ),
      route: sanitizeWilsyR91K144Text(
        revenueSource?.route,
        revenueSource?.endpoint,
        'crm command revenue posture'
      ),
    },
    {
      id: 'signature',
      label: 'Signature',
      status: contractContext.rootHash === 'pending' ? 'PENDING' : 'SEALED',
      value: contractContext.rootHash,
      detail: 'Root receipt constrains Wilsy AI command posture',
      route: 'source-guide root receipt',
    },
  ];
}

/**
 * @function buildWilsyR91K144SourceSignatureFabricContract
 * @description Creates the first-class sourceSignatureFabric backend contract for the CRM Source Guide endpoint.
 * @collaboration Bridges backend Source Guide telemetry to the R91K139 frontend fabric without static frontend copy.
 */
function buildWilsyR91K144SourceSignatureFabricContract(payload = {}) {
  const sourcePosture = payload.sourcePosture || {};
  const routeSurface = payload.routeSurface || {};
  const receipt = payload.sourceGuideReceipt || payload.receipt || {};

  const readiness = Math.max(
    0,
    Math.min(
      100,
      Math.round(
        normalizeWilsyR91K144Number(
          payload.readinessScore,
          sourcePosture.readinessScore,
          payload.governanceScore
        )
      )
    )
  );

  const postureGrade = sanitizeWilsyR91K144Text(
    payload.postureGrade,
    sourcePosture.postureGrade,
    payload.sourcePostureGrade,
    'SOURCE_POSTURE_PENDING'
  );

  const aiMode = sanitizeWilsyR91K144Text(
    payload.aiOperatingMode,
    sourcePosture.aiOperatingMode,
    payload.wilsyAiMode,
    'AI_MODE_PENDING'
  );

  const routeCount = normalizeWilsyR91K144Number(
    routeSurface.crmRelatedRoutes,
    routeSurface.routeSurfaceRoutes,
    payload.routeSurfaceRoutes,
    payload.crmRelatedRoutes
  );

  const sourceList = Array.isArray(sourcePosture.sources)
    ? sourcePosture.sources
    : Array.isArray(sourcePosture.sourceHealth)
      ? sourcePosture.sourceHealth
      : [];

  const totalSources = normalizeWilsyR91K144Number(
    sourcePosture.totalSources,
    sourcePosture.totalRoutes,
    sourcePosture.requiredSources,
    payload.totalSources,
    sourceList.length
  );

  const liveSourceEvidenceCount = sourceList.filter((source) => {
    const sourceText = [
      source?.status,
      source?.sourceStatus,
      source?.routeStatus,
      source?.label,
      source?.name,
    ]
      .filter(Boolean)
      .join(' ')
      .toLowerCase();

    return Boolean(
      source?.routeLive || source?.connected || source?.live || sourceText.includes('live')
    );
  }).length;

  const connectedSources = normalizeWilsyR91K144Number(
    sourcePosture.connectedSources,
    sourcePosture.connectedRoutes,
    sourcePosture.liveSources,
    sourcePosture.readySources,
    sourcePosture.verifiedSources,
    liveSourceEvidenceCount
  );

  const rootHash = sanitizeWilsyR91K144Text(
    receipt.rootHashShort,
    receipt.rootHash,
    payload.rootHashShort,
    payload.rootHash,
    payload.rootHashStatus,
    'pending'
  ).replace(/^root\s+/i, '');

  const weightedValue = normalizeWilsyR91K144Number(
    payload.weightedValue,
    payload.weightedPipeline,
    readWilsyR91K144Path(payload, 'pipeline.weightedValue', 0),
    readWilsyR91K144Path(payload, 'revenue.weightedValue', 0)
  );

  const weightedValueLabel =
    weightedValue > 0 ? `R ${Math.round(weightedValue).toLocaleString('en-ZA')}` : 'R 0';

  const safeTotalSources = totalSources || sourceList.length || 0;
  const safeConnectedSources = Math.min(
    safeTotalSources || connectedSources || liveSourceEvidenceCount,
    Math.max(connectedSources, liveSourceEvidenceCount)
  );

  const contractContext = {
    readiness,
    postureGrade,
    aiMode,
    routeCount,
    connectedSources: safeConnectedSources,
    totalSources: safeTotalSources,
    rootHash,
    weightedValueLabel,
  };

  const sourceRatio = safeTotalSources
    ? `${safeConnectedSources}/${safeTotalSources} CRM sources`
    : `${safeConnectedSources} CRM sources`;

  return {
    contractVersion: 'R91K144_SOURCE_SIGNATURE_FABRIC_BACKEND_CONTRACT',
    source: 'api.crm.live.source-guide',
    live: Boolean(payload.ok),
    generatedAt: new Date().toISOString(),
    kicker: `${sourceRatio} · ${routeCount || 0} route fabric`,
    headline: `${sourceRatio} to root signature`,
    postureLine: `${readiness}% readiness · ${postureGrade} · ${aiMode}`,
    receipt: `Root ${rootHash}`,
    nodes: buildWilsyR91K144SourceSignatureFabricNodes(payload, contractContext),
    ledger: {
      weightedValue: weightedValueLabel,
      governance: `${readiness}%`,
      backendProfile: sanitizeWilsyR91K144Text(
        payload.backendProfile,
        payload.profile,
        payload.sourceStatus,
        'Live constrained'
      ),
      rootReceipt: rootHash,
    },
    verification: {
      endpoint: '/api/crm/live/source-guide',
      constrainedToSourceGuide: true,
      derivedFromBackendPayload: true,
      noFrontendStaticCopyRequired: true,
    },
  };
}

/**
 * @function attachWilsyR91K144SourceSignatureFabric
 * @description Attaches sourceSignatureFabric to the response envelope and nested Source Guide object when present.
 * @collaboration Keeps the frontend contract top-level while preserving existing backend response shape.
 */
function attachWilsyR91K144SourceSignatureFabric(payload, sourceSignatureFabric) {
  if (!payload || typeof payload !== 'object' || Array.isArray(payload)) {
    return payload;
  }

  const enrichedPayload = {
    ...payload,
    sourceSignatureFabric,
  };

  if (payload.data && typeof payload.data === 'object' && !Array.isArray(payload.data)) {
    enrichedPayload.data = {
      ...payload.data,
      sourceSignatureFabric,
    };

    if (
      payload.data.sourceGuide &&
      typeof payload.data.sourceGuide === 'object' &&
      !Array.isArray(payload.data.sourceGuide)
    ) {
      enrichedPayload.data.sourceGuide = {
        ...payload.data.sourceGuide,
        sourceSignatureFabric,
      };
    }
  }

  /* R91K146A_ATTACH_SOURCE_SIGNATURE_FABRIC_TO_GUIDE */
  /* R91K147_ENSURE_GUIDE_LEVEL_SOURCE_SIGNATURE_FABRIC */
  if (payload.guide && typeof payload.guide === 'object' && !Array.isArray(payload.guide)) {
    enrichedPayload.guide = {
      ...payload.guide,
      sourceSignatureFabric,
    };
  }

  /* R91K147A_ENSURE_GUIDE_LEVEL_SOURCE_SIGNATURE_FABRIC */
  if (payload.guide && typeof payload.guide === 'object' && !Array.isArray(payload.guide)) {
    enrichedPayload.guide = {
      ...payload.guide,
      sourceSignatureFabric,
    };
  }

  if (
    payload.sourceGuide &&
    typeof payload.sourceGuide === 'object' &&
    !Array.isArray(payload.sourceGuide)
  ) {
    enrichedPayload.sourceGuide = {
      ...payload.sourceGuide,
      sourceSignatureFabric,
    };
  }

  if (payload.result && typeof payload.result === 'object' && !Array.isArray(payload.result)) {
    enrichedPayload.result = {
      ...payload.result,
      sourceSignatureFabric,
    };
  }

  if (payload.payload && typeof payload.payload === 'object' && !Array.isArray(payload.payload)) {
    enrichedPayload.payload = {
      ...payload.payload,
      sourceSignatureFabric,
    };
  }

  return enrichedPayload;
}

/**
 * @function enrichWilsyR91K144SourceGuidePayload
 * @description Adds sourceSignatureFabric to Source Guide responses without changing unrelated route payloads.
 * @collaboration Used by router-level middleware mounted only on /source-guide.
 */
/* R91K144C_SOURCE_GUIDE_DEEP_PAYLOAD_RESOLVER */

/**
 * @function scoreWilsyR91K144SourceGuideCandidate
 * @description Scores an object by how strongly it resembles the real CRM Source Guide payload.
 * @collaboration Allows sourceSignatureFabric to be built from live telemetry instead of a shallow response envelope.
 */
function scoreWilsyR91K144SourceGuideCandidate(candidate) {
  if (!candidate || typeof candidate !== 'object' || Array.isArray(candidate)) {
    return 0;
  }

  let score = 0;

  if (Object.prototype.hasOwnProperty.call(candidate, 'readinessScore')) score += 10;
  if (Object.prototype.hasOwnProperty.call(candidate, 'postureGrade')) score += 10;
  if (Object.prototype.hasOwnProperty.call(candidate, 'aiOperatingMode')) score += 10;
  if (Object.prototype.hasOwnProperty.call(candidate, 'routeSurfaceRoutes')) score += 8;
  if (Object.prototype.hasOwnProperty.call(candidate, 'crmRelatedRoutes')) score += 8;
  if (Object.prototype.hasOwnProperty.call(candidate, 'sourcePosture')) score += 8;
  if (Object.prototype.hasOwnProperty.call(candidate, 'routeSurface')) score += 8;
  if (Object.prototype.hasOwnProperty.call(candidate, 'sourceGuideReceipt')) score += 8;
  if (Object.prototype.hasOwnProperty.call(candidate, 'rootHashShort')) score += 8;
  if (Object.prototype.hasOwnProperty.call(candidate, 'rootHash')) score += 8;
  if (Object.prototype.hasOwnProperty.call(candidate, 'rootHashStatus')) score += 8;
  if (Object.prototype.hasOwnProperty.call(candidate, 'directives')) score += 4;
  if (Object.prototype.hasOwnProperty.call(candidate, 'actions')) score += 4;
  if (candidate.ok === true) score += 2;

  return score;
}

/**
 * @function collectWilsyR91K144SourceGuideCandidates
 * @description Recursively collects safe object candidates from common API envelopes.
 * @collaboration Finds the real Source Guide object even when nested under data, payload, result or service envelopes.
 */
function collectWilsyR91K144SourceGuideCandidates(
  source,
  candidates = [],
  depth = 0,
  pathKey = 'root'
) {
  if (!source || typeof source !== 'object' || Array.isArray(source) || depth > 5) {
    return candidates;
  }

  candidates.push({
    path: pathKey,
    value: source,
    score: scoreWilsyR91K144SourceGuideCandidate(source),
  });

  const preferredKeys = [
    'data',
    'sourceGuide',
    'result',
    'payload',
    'guide',
    'liveSourceGuide',
    'crmSourceGuide',
    'crmLiveSourceGuide',
    'sourceGuidePayload',
    'sourceGuideResult',
    'body',
  ];

  for (const key of preferredKeys) {
    if (source[key] && typeof source[key] === 'object' && !Array.isArray(source[key])) {
      collectWilsyR91K144SourceGuideCandidates(
        source[key],
        candidates,
        depth + 1,
        `${pathKey}.${key}`
      );
    }
  }

  if (depth < 2) {
    for (const [key, value] of Object.entries(source)) {
      if (
        value &&
        typeof value === 'object' &&
        !Array.isArray(value) &&
        !preferredKeys.includes(key)
      ) {
        collectWilsyR91K144SourceGuideCandidates(value, candidates, depth + 1, `${pathKey}.${key}`);
      }
    }
  }

  return candidates;
}

/**
 * @function resolveWilsyR91K144SourceGuidePayloadDeep
 * @description Resolves the highest-scoring real Source Guide telemetry object from a response body.
 * @collaboration Prevents backend sourceSignatureFabric from producing 0/pending contracts when telemetry exists deeper in the payload.
 */
function resolveWilsyR91K144SourceGuidePayloadDeep(payload) {
  const candidates = collectWilsyR91K144SourceGuideCandidates(payload).sort(
    (left, right) => right.score - left.score
  );

  const winner = candidates[0];

  if (winner && winner.score > 0) {
    return {
      sourceGuidePayload: winner.value,
      sourceGuidePath: winner.path,
      sourceGuideScore: winner.score,
      candidateSummary: candidates.slice(0, 6).map((candidate) => ({
        path: candidate.path,
        score: candidate.score,
      })),
    };
  }

  return {
    sourceGuidePayload: payload,
    sourceGuidePath: 'root',
    sourceGuideScore: 0,
    candidateSummary: candidates.slice(0, 6).map((candidate) => ({
      path: candidate.path,
      score: candidate.score,
    })),
  };
}

/**
 * @function enrichWilsyR91K144SourceGuidePayload
 * @description Enriches CRM live Source Guide response envelopes with the backend-owned sourceSignatureFabric contract.
 * @collaboration Resolves nested Source Guide telemetry for R91K144/R91K145 fabric consumers without changing the original route shape.
 */
function enrichWilsyR91K144SourceGuidePayload(payload) {
  if (!payload || typeof payload !== 'object' || Array.isArray(payload)) {
    return payload;
  }

  const { sourceGuidePayload, sourceGuidePath, sourceGuideScore, candidateSummary } =
    resolveWilsyR91K144SourceGuidePayloadDeep(payload);

  const sourceSignatureFabric =
    sourceGuidePayload?.sourceSignatureFabric &&
    sourceGuidePayload.sourceSignatureFabric.contractVersion
      ? sourceGuidePayload.sourceSignatureFabric
      : buildWilsyR91K144SourceSignatureFabricContract(sourceGuidePayload);

  const nextSourceSignatureFabric = {
    ...sourceSignatureFabric,
    verification: {
      ...(sourceSignatureFabric.verification || {}),
      endpoint: '/api/crm/live/source-guide',
      constrainedToSourceGuide: true,
      derivedFromBackendPayload: true,
      sourceGuidePayloadPath: sourceGuidePath,
      sourceGuidePayloadScore: sourceGuideScore,
      sourceGuideCandidateSummary: candidateSummary,
    },
  };

  return attachWilsyR91K144SourceSignatureFabric(payload, nextSourceSignatureFabric);
}

/**
 * @function wilsyR91K144SourceSignatureFabricMiddleware
 * @description Enriches /source-guide JSON responses with the backend-owned sourceSignatureFabric object.
 * @collaboration Wraps Express res.json for this route only so existing handlers stay untouched.
 */
function wilsyR91K144SourceSignatureFabricMiddleware(req, res, next) {
  const originalJson = res.json.bind(res);

  res.json = (body) => originalJson(enrichWilsyR91K144SourceGuidePayload(body));

  return next();
}

/* R91K156_READINESS_BREAKDOWN_CONTRACT */

/**
 * @function scoreWilsyR91K156GateState
 * @description Converts a live CRM readiness score into a production gate state.
 * @collaboration Used by the Source Guide readiness breakdown contract to explain why CRM readiness is not yet 100%.
 */
function scoreWilsyR91K156GateState(score) {
  const numericScore = Number(score || 0);

  if (numericScore >= 100) return 'COMPLETE';
  if (numericScore >= 80) return 'NEAR_READY';
  if (numericScore >= 50) return 'EXPANDING';
  if (numericScore > 0) return 'BLOCKED';

  return 'MISSING';
}

/**
 * @function buildWilsyR91K156ReadinessGate
 * @description Builds a readiness gate from an existing backend health packet without inventing scores.
 * @collaboration Keeps source-guide readiness transparency tied to live source, route, data, connector, and evidence health.
 */
function buildWilsyR91K156ReadinessGate(id, label, health, weight = 0) {
  const score = Number(health?.score || 0);

  return {
    id,
    label,
    weight,
    score,
    status: health?.status || scoreWilsyR91K156GateState(score),
    state: scoreWilsyR91K156GateState(score),
    summary: health?.summary || 'No backend summary emitted.',
    complete: score >= 100,
  };
}

/**
 * @function buildWilsyR91K156MissingSourceGates
 * @description Converts empty live source definitions into explicit readiness blockers.
 * @collaboration Surfaces the exact CRM records that must exist before Wilsy CRM can earn 100% maturity.
 */
function buildWilsyR91K156MissingSourceGates(sourcePosture = {}) {
  const sources = Array.isArray(sourcePosture.sources) ? sourcePosture.sources : [];
  const emptySources = Array.isArray(sourcePosture.emptyLiveSources)
    ? sourcePosture.emptyLiveSources
    : sources.filter((source) => Number(source?.recordCount || 0) === 0);

  return emptySources.map((source) => ({
    id: source.id || source.label || source.route || 'unknown-source',
    label: source.label || source.id || 'Unknown source',
    route: source.route || null,
    modelName: source.modelName || null,
    currentRecords: Number(source.recordCount || 0),
    requiredMinimumRecords: 1,
    severity: source.id === 'deals' || source.id === 'connectors' ? 'CRITICAL' : 'HIGH',
    blocker: `${source.label || source.id || 'Source'} has 0 live production records.`,
    action: `Populate ${source.label || source.id || 'this source'} through live CRM operations or a verified connector.`,
  }));
}

/**
 * @function buildWilsyR91K156PathTo100
 * @description Builds the backend-owned path from the current readiness score to full CRM maturity.
 * @collaboration Gives Wilsy CRM UI and Wilsy AI exact production blockers instead of a naked readiness percentage.
 */
function buildWilsyR91K156PathTo100(guide = {}) {
  const sourcePosture = guide.sourcePosture || {};
  const gates = [
    buildWilsyR91K156ReadinessGate('source-health', 'Source routes', guide.sourceHealth, 20),
    buildWilsyR91K156ReadinessGate(
      'route-surface-health',
      'Route fabric',
      guide.routeSurfaceHealth,
      20
    ),
    buildWilsyR91K156ReadinessGate(
      'data-density-health',
      'Data density',
      guide.dataDensityHealth,
      25
    ),
    buildWilsyR91K156ReadinessGate(
      'connector-health',
      'Connector registry',
      guide.connectorHealth,
      15
    ),
    buildWilsyR91K156ReadinessGate('evidence-health', 'Evidence graph', guide.evidenceHealth, 15),
  ];

  if (guide.addressProviderHealth) {
    gates.push(
      buildWilsyR91K156ReadinessGate(
        'address-provider-health',
        'Address intelligence',
        guide.addressProviderHealth,
        5
      )
    );
  }

  const missingSourceGates = buildWilsyR91K156MissingSourceGates(sourcePosture);
  const hardBlockers = [];

  if (missingSourceGates.length) {
    hardBlockers.push({
      id: 'empty-live-sources',
      severity: 'CRITICAL',
      label: 'Empty live CRM sources',
      summary: `${missingSourceGates.length} live CRM sources are route-live but record-empty.`,
      targets: missingSourceGates.map((gate) => gate.id),
    });
  }

  if (String(guide.aiOperatingMode || '').includes('DATA_DENSITY_EXPANSION')) {
    hardBlockers.push({
      id: 'ai-data-density-expansion',
      severity: 'CRITICAL',
      label: 'AI data density gate',
      summary: 'Wilsy AI remains constrained because live CRM source density is not mature.',
      targets: ['contacts', 'accounts', 'deals', 'tasks', 'meetings', 'evidence', 'connectors'],
    });
  }

  if (String(guide.postureGrade || '').includes('SOURCE_EXPANSION_REQUIRED')) {
    hardBlockers.push({
      id: 'source-expansion-required',
      severity: 'CRITICAL',
      label: 'Source expansion required',
      summary:
        'Backend posture requires source expansion before readiness can be promoted to full maturity.',
      targets: ['data-density-health', 'connector-health', 'evidence-health'],
    });
  }

  const currentScore = Number(guide.readinessScore || 0);
  const remainingTo100 = Math.max(0, 100 - currentScore);
  const completedGates = gates.filter((gate) => gate.complete);

  return {
    contractVersion: 'R91K156_READINESS_BREAKDOWN_CONTRACT',
    currentScore,
    targetScore: 100,
    remainingTo100,
    postureGrade: guide.postureGrade || null,
    aiOperatingMode: guide.aiOperatingMode || null,
    maturityState: remainingTo100 === 0 ? 'FULLY_READY' : 'READINESS_BLOCKED',
    completedGateCount: completedGates.length,
    totalGateCount: gates.length,
    gates,
    missingSourceGates,
    hardBlockers,
    nextBuildSequence: [
      {
        order: 1,
        id: 'populate-live-source-records',
        label: 'Populate empty live CRM sources',
        targets: missingSourceGates.map((gate) => gate.id),
        outcome: 'Raises data density and unlocks AI confidence.',
      },
      {
        order: 2,
        id: 'register-source-connectors',
        label: 'Register real source connectors',
        targets: ['connectors'],
        outcome: 'Moves CRM from local database visibility to cross-system source intelligence.',
      },
      {
        order: 3,
        id: 'expand-evidence-graph',
        label: 'Seal evidence anchors for CRM activity',
        targets: ['evidence', 'audit-log', 'forensic-receipts'],
        outcome: 'Turns CRM movement into regulator and investor proof.',
      },
      {
        order: 4,
        id: 'activate-deal-motion',
        label: 'Create governed deal and revenue movement',
        targets: ['deals', 'accounts', 'contacts', 'tasks', 'meetings'],
        outcome: 'Breaks R0 weighted pipeline and proves commercial motion.',
      },
    ],
    noSyntheticPromotion: true,
    productionRule:
      'Readiness reaches 100 only when backend gates are complete from live records, connectors, evidence, and revenue motion.',
  };
}

/**
 * @function attachWilsyR91K156ReadinessBreakdown
 * @description Attaches readinessBreakdown, missingGates, and pathTo100 to a Source Guide response.
 * @collaboration Makes the CRM source-guide endpoint explain exactly what blocks 100% readiness without changing the score.
 */
function attachWilsyR91K156ReadinessBreakdown(payload = {}) {
  const guide = payload.guide || payload.sourceGuide || payload.data?.guide || payload;

  if (!guide || typeof guide !== 'object' || Array.isArray(guide)) {
    return payload;
  }

  const readinessBreakdown = buildWilsyR91K156PathTo100(guide);
  const enrichedGuide = {
    ...guide,
    readinessBreakdown,
    missingGates: readinessBreakdown.missingSourceGates,
    pathTo100: readinessBreakdown.nextBuildSequence,
  };

  return {
    ...payload,
    guide: enrichedGuide,
    readinessBreakdown,
    missingGates: readinessBreakdown.missingSourceGates,
    pathTo100: readinessBreakdown.nextBuildSequence,
  };
}

/**
 * @function wilsyR91K156ReadinessBreakdownMiddleware
 * @description Wraps /source-guide JSON responses so every response explains the path from current readiness to 100%.
 * @collaboration Mounted before R91K144 sourceSignatureFabric middleware so final responses include both readiness and fabric contracts.
 */
function wilsyR91K156ReadinessBreakdownMiddleware(req, res, next) {
  const originalJson = res.json.bind(res);

  res.json = (payload) => originalJson(attachWilsyR91K156ReadinessBreakdown(payload));

  return next();
}

router.use(
  '/source-guide',
  wilsyR91K156ReadinessBreakdownMiddleware
); /* R91K156_ATTACH_READINESS_BREAKDOWN */
router.use('/source-guide', wilsyR91K144SourceSignatureFabricMiddleware);

/**
 * @function asyncHandler
 * @description Wraps async route handlers for Express.
 * @param {Function} handler - Async route handler.
 * @returns {Function} Express middleware.
 * @collaboration Keeps live CRM routes concise and safe.
 */
function asyncHandler(handler) {
  return (req, res, next) => {
    Promise.resolve(handler(req, res, next)).catch(next);
  };
}

/**
 * @function sendSourcePosture
 * @description Sends live CRM source posture.
 * @param {Object} req - Express request.
 * @param {Object} res - Express response.
 * @returns {Promise<void>} Route result.
 * @collaboration Feeds Root Hash and source route counter in the CRM header.
 */
async function sendSourcePosture(req, res) {
  const posture = await buildSourcePosture(req);
  res.json(posture);
}

/**
 * @function sendCrmCollection
 * @description Sends one live CRM collection.
 * @param {Object} req - Express request.
 * @param {Object} res - Express response.
 * @param {Function} next - Express next handler.
 * @returns {Promise<void>} Route result.
 * @collaboration Serves source-honest CRM records without fake data.
 */
async function sendCrmCollection(req, res, next) {
  const collection = String(req.params.collection || '').trim();
  const allowedCollections = getAllowedCollections();

  if (!allowedCollections.includes(collection)) {
    return next();
  }

  const payload = await listCrmCollection(req, collection);
  return res.json(payload);
}

/**
 * @function sendLiveRouteIndex
 * @description Sends live CRM route index.
 * @param {Object} req - Express request.
 * @param {Object} res - Express response.
 * @returns {void} Route result.
 * @collaboration Exposes route availability for smoke tests and diagnostics.
 */
function sendLiveRouteIndex(req, res) {
  res.json({
    ok: true,
    routes: [
      '/api/crm/live/source-posture',
      ...getAllowedCollections().map((collection) => `/api/crm/live/${collection}`),
    ],
  });
}

router.get('/', sendLiveRouteIndex);

const WILSY_R91K110_ROUTE_SURFACE_CACHE = {
  generatedAt: 0,
  payload: null,
};

/**
 * @function normalizeWilsyR91K110RouteMethod
 * @description Normalizes Express route method tokens for CRM route-surface telemetry.
 * @param {string} method - Candidate route method.
 * @returns {string} Uppercase route method.
 * @collaboration CRM source posture, investor telemetry, production route-surface truth.
 */
function normalizeWilsyR91K110RouteMethod(method = '') {
  return (
    String(method || '')
      .trim()
      .toUpperCase() || 'UNKNOWN'
  );
}

/**
 * @function resolveWilsyR91K110ServerRoot
 * @description Resolves the server root from this route module without relying on process cwd.
 * @returns {string} Absolute server root.
 * @collaboration CRM live route, route-surface registry, production deployment portability.
 */
function resolveWilsyR91K110ServerRoot() {
  const currentFile = fileURLToPath(import.meta.url);
  return path.resolve(path.dirname(currentFile), '..');
}

/**
 * @function shouldSkipWilsyR91K110RouteScanPath
 * @description Excludes non-production folders from CRM route-surface route declaration scanning.
 * @param {string} candidatePath - Absolute candidate path.
 * @returns {boolean} True when the file should be skipped.
 * @collaboration CRM route-surface truth, production-only telemetry, guard-safe filesystem scanning.
 */
function shouldSkipWilsyR91K110RouteScanPath(candidatePath = '') {
  const normalized = String(candidatePath || '').replaceAll(path.sep, '/');

  return [
    '/node_modules/',
    '/coverage/',
    '/dist/',
    '/build/',
    '/.git/',
    '/tests/',
    '/test/',
    '/__tests__/',
    '/fixtures/',
    '/mocks/',
  ].some((segment) => normalized.includes(segment));
}

/**
 * @function collectWilsyR91K110ServerRouteFiles
 * @description Recursively collects production server JavaScript files that can contain route declarations.
 * @param {string} root - Absolute server root.
 * @returns {Array<string>} Candidate route source files.
 * @collaboration CRM route-surface truth, source registry posture, investor-grade route telemetry.
 */
function collectWilsyR91K110ServerRouteFiles(root = resolveWilsyR91K110ServerRoot()) {
  const files = [];

  /**
   * @function walk
   * @description Recursively walks the server route tree while honoring production scan exclusions.
   * @param {string} directory - Directory currently being scanned.
   * @returns {void}
   * @collaboration Dynamic CRM route-surface algorithm, production route inventory, guard-safe filesystem traversal.
   */
  function walk(directory) {
    if (!fs.existsSync(directory) || shouldSkipWilsyR91K110RouteScanPath(directory)) {
      return;
    }

    const entries = fs.readdirSync(directory, { withFileTypes: true });

    entries.forEach((entry) => {
      const absolutePath = path.join(directory, entry.name);

      if (shouldSkipWilsyR91K110RouteScanPath(absolutePath)) {
        return;
      }

      if (entry.isDirectory()) {
        walk(absolutePath);
        return;
      }

      if (entry.isFile() && /\.(js|mjs|cjs)$/i.test(entry.name)) {
        files.push(absolutePath);
      }
    });
  }

  walk(root);
  return files;
}

/**
 * @function collectWilsyR91K110RouteDeclarations
 * @description Extracts Express route declarations from production server files.
 * @param {Array<string>} files - Candidate files.
 * @param {string} root - Absolute server root.
 * @returns {Array<Object>} Route declaration records.
 * @collaboration CRM route-surface truth, source posture, command and live route evidence.
 */
function collectWilsyR91K110RouteDeclarations(files = [], root = resolveWilsyR91K110ServerRoot()) {
  const routePattern =
    /\b(?<object>router|app)\.(?<method>get|post|put|patch|delete|use|all)\s*\(\s*(?<quote>['"`])(?<route>[^'"`]+)\k<quote>/g;
  const declarations = [];

  files.forEach((filePath) => {
    const source = fs.readFileSync(filePath, 'utf8');
    let match = routePattern.exec(source);

    while (match) {
      const method = normalizeWilsyR91K110RouteMethod(match.groups?.method);
      const routePath = String(match.groups?.route || '').trim();
      const relativeFile = path.relative(root, filePath).replaceAll(path.sep, '/');
      const line = source.slice(0, match.index).split('\n').length;
      const lowerFile = relativeFile.toLowerCase();
      const lowerRoute = routePath.toLowerCase();
      const crmRelated = lowerFile.includes('crm') || lowerRoute.includes('/crm');

      declarations.push({
        file: relativeFile,
        line,
        object: match.groups?.object || 'router',
        method,
        route: routePath,
        crmRelated,
        group: lowerFile.includes('crmcommandroutes')
          ? 'command'
          : lowerFile.includes('wilsycrmliveroutes')
            ? 'live'
            : lowerFile.includes('wilsycrmintelligenceroutes')
              ? 'intelligence'
              : lowerFile.includes('crmroutes')
                ? 'crud'
                : lowerRoute.includes('/crm')
                  ? 'mounted'
                  : 'other',
      });

      match = routePattern.exec(source);
    }
  });

  return declarations;
}

/**
 * @function buildWilsyR91K110DynamicCrmRouteSurface
 * @description Builds dynamic CRM route-surface telemetry from production server route declarations.
 * @returns {Object} Dynamic CRM route-surface payload.
 * @collaboration CRM header telemetry, source posture, production route registry evidence.
 */
function buildWilsyR91K110DynamicCrmRouteSurface() {
  const now = Date.now();
  const ttlMs = Number(process.env.WILSY_ROUTE_SURFACE_CACHE_TTL_MS || 30000);

  if (
    WILSY_R91K110_ROUTE_SURFACE_CACHE.payload &&
    now - WILSY_R91K110_ROUTE_SURFACE_CACHE.generatedAt < ttlMs
  ) {
    return {
      ...WILSY_R91K110_ROUTE_SURFACE_CACHE.payload,
      cacheStatus: 'HIT',
    };
  }

  const serverRoot = resolveWilsyR91K110ServerRoot();
  const files = collectWilsyR91K110ServerRouteFiles(serverRoot);
  const declarations = collectWilsyR91K110RouteDeclarations(files, serverRoot);
  const crmRoutes = declarations.filter((route) => route.crmRelated);
  const groupCounts = crmRoutes.reduce((summary, route) => {
    summary[route.group] = (summary[route.group] || 0) + 1;
    return summary;
  }, {});

  const payload = {
    algorithmVersion: 'R91K110_DYNAMIC_CRM_ROUTE_SURFACE_ALGORITHM',
    generatedAt: new Date().toISOString(),
    cacheTtlMs: ttlMs,
    scannedFiles: files.length,
    totalRouteDeclarations: declarations.length,
    crmRelatedRoutes: crmRoutes.length,
    groupCounts,
    routeFiles: Array.from(new Set(crmRoutes.map((route) => route.file))).sort(),
    sampleRoutes: crmRoutes.slice(0, 36),
  };

  WILSY_R91K110_ROUTE_SURFACE_CACHE.generatedAt = now;
  WILSY_R91K110_ROUTE_SURFACE_CACHE.payload = payload;

  return {
    ...payload,
    cacheStatus: 'MISS',
  };
}

/**
 * @function handleWilsyR91K110CrmRouteSurface
 * @description Returns dynamic CRM route-surface telemetry without hardcoded route counts.
 * @param {Object} req - Express request.
 * @param {Object} res - Express response.
 * @returns {Promise<void>} JSON response.
 * @collaboration CRM source posture, investor telemetry, production route-surface truth.
 */
async function handleWilsyR91K110CrmRouteSurface(req, res) {
  const tenantId =
    String(req.tenantId || req.headers?.['x-tenant-id'] || 'MASTER').trim() || 'MASTER';
  const routeSurface = buildWilsyR91K110DynamicCrmRouteSurface();

  res.json({
    ok: true,
    tenantId,
    routeSurface,
  });
}

router.get('/source-posture', asyncHandler(sendSourcePosture));

const WILSY_R91K113_SOURCE_POSTURE_GUIDE_ALGORITHM = 'R91K113_SOURCE_POSTURE_GUIDE_ALGORITHM';

/**
 * @function clampWilsyR91K113Score
 * @description Clamps a source guide score into a production-safe percentage range.
 * @param {number} value - Candidate score.
 * @returns {number} Clamped score.
 * @collaboration Source posture guide, Wilsy AI directives, readiness telemetry.
 */
function clampWilsyR91K113Score(value = 0) {
  return Math.max(0, Math.min(100, Math.round(Number(value || 0))));
}

/**
 * @function resolveWilsyR91K113PostureGrade
 * @description Resolves an executive posture grade from the dynamic source guide score.
 * @param {number} score - Source guide readiness score.
 * @returns {string} Posture grade.
 * @collaboration CRM readiness guide, Wilsy AI operating mode, investor telemetry.
 */
function resolveWilsyR91K113PostureGrade(score = 0) {
  const normalized = clampWilsyR91K113Score(score);

  if (normalized >= 90) return 'BOARDROOM_READY';
  if (normalized >= 78) return 'PRODUCTION_STABLE';
  if (normalized >= 62) return 'SOURCE_EXPANSION_REQUIRED';
  if (normalized >= 44) return 'DATA_DENSITY_RISK';

  return 'SOURCE_RECOVERY_REQUIRED';
}

/**
 * @function resolveWilsyR91K113AiOperatingMode
 * @description Resolves how Wilsy AI should behave from source truth and data density.
 * @param {Object} metrics - Dynamic guide metrics.
 * @returns {string} Wilsy AI operating mode.
 * @collaboration Wilsy AI safety, source honesty, operator next-best-action guidance.
 */
function resolveWilsyR91K113AiOperatingMode(metrics = {}) {
  if (Number(metrics.sourceGaps || 0) > 0) return 'SOURCE_GAP_TRIAGE';
  if (Number(metrics.emptyLiveSources || 0) > 0) return 'DATA_DENSITY_EXPANSION';
  if (Number(metrics.connectorRecords || 0) === 0) return 'CONNECTOR_ONBOARDING';
  if (
    Number(metrics.crmRelatedRoutes || 0) >= 100 &&
    Number(metrics.liveSources || 0) === Number(metrics.totalSources || 0)
  ) {
    return 'COMMAND_ACCELERATION';
  }

  return 'OPERATING_GUIDE';
}

/**
 * @function buildWilsyR91K113HealthPacket
 * @description Builds one normalized health packet for the source guide.
 * @param {string} id - Health packet id.
 * @param {string} label - Human label.
 * @param {number} score - Health score.
 * @param {string} status - Health status.
 * @param {string} summary - Health summary.
 * @returns {Object} Health packet.
 * @collaboration Source posture guide, Wilsy AI directives, operating evidence.
 */
function buildWilsyR91K113HealthPacket(id, label, score, status, summary) {
  return {
    id,
    label,
    score: clampWilsyR91K113Score(score),
    status,
    summary,
  };
}

/**
 * @function buildWilsyR91K113SourceGuideHash
 * @description Builds a deterministic guide receipt hash without exposing secrets.
 * @param {Object} guide - Source guide payload.
 * @returns {string} Receipt hash.
 * @collaboration Source posture guide, forensic receipts, Wilsy AI audit chain.
 */
function buildWilsyR91K113SourceGuideHash(guide = {}) {
  try {
    return crypto.createHash('sha3-512').update(JSON.stringify(guide)).digest('hex');
  } catch (error) {
    return crypto.createHash('sha512').update(JSON.stringify(guide)).digest('hex');
  }
}

/**
 * @function buildWilsyR91K113SourceGuideDirectives
 * @description Builds Wilsy AI directives from dynamic source posture and route-surface telemetry.
 * @param {Object} metrics - Dynamic guide metrics.
 * @param {Array<Object>} emptyLiveSources - Live sources without records.
 * @returns {Array<Object>} AI directives.
 * @collaboration Wilsy AI guide, operator actions, no-placeholder source intelligence.
 */
function buildWilsyR91K113SourceGuideDirectives(metrics = {}, emptyLiveSources = []) {
  const directives = [];

  if (Number(metrics.crmRelatedRoutes || 0) > 0) {
    directives.push({
      id: 'ROUTE_SURFACE_AVAILABLE',
      priority: 'HIGH',
      instruction: `Use ${metrics.crmRelatedRoutes} CRM routes as the command surface boundary before recommending new CRM features.`,
    });
  }

  if (emptyLiveSources.length) {
    directives.push({
      id: 'EMPTY_LIVE_SOURCE_EXPANSION',
      priority: 'CRITICAL',
      instruction: `Prioritize data onboarding for ${emptyLiveSources.map((source) => source.label).join(', ')} before claiming full CRM operational maturity.`,
    });
  }

  if (Number(metrics.connectorRecords || 0) === 0) {
    directives.push({
      id: 'CONNECTOR_REGISTRY_REQUIRED',
      priority: 'HIGH',
      instruction:
        'Guide the operator to connect real CRM, mail, calendar, billing, support, and evidence sources before advanced automation.',
    });
  }

  if (Number(metrics.evidenceRecords || 0) > 0) {
    directives.push({
      id: 'EVIDENCE_AVAILABLE',
      priority: 'MEDIUM',
      instruction:
        'Use existing evidence anchors when explaining source posture and audit readiness.',
    });
  }

  if (metrics.addressProviderConfigured) {
    directives.push({
      id: 'ADDRESS_INTELLIGENCE_READY',
      priority: 'MEDIUM',
      instruction:
        'Use address intelligence as a verified enrichment capability for lead capture and data quality guidance.',
    });
  }

  return directives;
}

/**
 * @function buildWilsyR91K113SourceGuideActions
 * @description Builds operator next-best-actions from live source posture and route surface.
 * @param {Object} metrics - Dynamic guide metrics.
 * @param {Array<Object>} emptyLiveSources - Live sources without records.
 * @returns {Array<Object>} Recommended actions.
 * @collaboration CRM command center, operator workflow, Wilsy AI next-best-action layer.
 */
function buildWilsyR91K113SourceGuideActions(metrics = {}, emptyLiveSources = []) {
  const actions = [];

  if (emptyLiveSources.length) {
    actions.push({
      id: 'ONBOARD_EMPTY_LIVE_SOURCES',
      label: 'Populate live CRM sources',
      impact: 'Raises data density and AI confidence.',
      targets: emptyLiveSources.map((source) => source.id),
    });
  }

  if (Number(metrics.connectorRecords || 0) === 0) {
    actions.push({
      id: 'CONNECT_SOURCE_SYSTEMS',
      label: 'Register real source connectors',
      impact: 'Turns Wilsy AI from local cockpit guidance into cross-system operator intelligence.',
      targets: ['connectors'],
    });
  }

  if (Number(metrics.crmRelatedRoutes || 0) >= 100) {
    actions.push({
      id: 'GENERATE_ROUTE_SURFACE_DOSSIER',
      label: 'Promote CRM route-surface dossier',
      impact: 'Creates investor/regulator proof from the dynamic CRM route map.',
      targets: ['route-surface', 'evidence'],
    });
  }

  if (Number(metrics.evidenceRecords || 0) === 0) {
    actions.push({
      id: 'SEAL_EVIDENCE_ANCHORS',
      label: 'Create source evidence anchors',
      impact: 'Improves audit posture and readiness confidence.',
      targets: ['evidence'],
    });
  }

  return actions;
}

/**
 * @function buildWilsyR91K113SourcePostureGuide
 * @description Builds the dynamic Source Posture Guide used by Wilsy AI and operators.
 * @param {string} tenantId - Active tenant id.
 * @returns {Promise<Object>} Source posture guide.
 * @collaboration Wilsy AI, source posture, route-surface telemetry, operator next-best-actions.
 */
async function buildWilsyR91K113SourcePostureGuide(tenantId = 'MASTER') {
  const sourceIds = getWilsyCrmLiveAllowedCollections();
  const sourceResults = await Promise.all(
    sourceIds.map(async (sourceId) => {
      try {
        return await listWilsyCrmLiveCollectionRecords(sourceId, tenantId, 5);
      } catch (error) {
        return {
          collection: sourceId,
          label: sourceId,
          records: [],
          dataSource: 'source-guide-unavailable',
          modelName: null,
          routeLive: false,
          sourceGuideError: error?.message || 'SOURCE_GUIDE_SOURCE_QUERY_FAILED',
        };
      }
    })
  );
  const routeSurface = buildWilsyR91K110DynamicCrmRouteSurface();
  const sources = sourceResults.map((result) => ({
    id: result.collection,
    label: result.label,
    route: `/api/crm/live/${result.collection}`,
    routeLive: Boolean(result.routeLive),
    dataSource: result.dataSource,
    modelName: result.modelName,
    recordCount: Array.isArray(result.records) ? result.records.length : 0,
    status: result.routeLive ? 'live' : 'source_required',
  }));
  const totalSources = sources.length;
  const liveSources = sources.filter((source) => source.routeLive).length;
  const sourcesWithRecords = sources.filter((source) => Number(source.recordCount || 0) > 0).length;
  const emptyLiveSources = sources.filter(
    (source) => source.routeLive && Number(source.recordCount || 0) === 0
  );
  const evidenceSource = sources.find((source) => source.id === 'evidence') || {};
  const connectorSource = sources.find((source) => source.id === 'connectors') || {};
  const sourceGaps = sources.filter((source) => !source.routeLive);
  const crmRelatedRoutes = Number(routeSurface.crmRelatedRoutes || 0);
  const totalRouteDeclarations = Number(routeSurface.totalRouteDeclarations || 0);
  const routeGroupCounts = routeSurface.groupCounts || {};
  const addressProviderName = String(process.env.WILSY_ADDRESS_PROVIDER || '').trim();
  const addressProviderConfigured = Boolean(
    addressProviderName ||
    process.env.MAPBOX_ACCESS_TOKEN ||
    process.env.GOOGLE_PLACES_API_KEY ||
    process.env.GOOGLE_MAPS_API_KEY ||
    process.env.LOQATE_API_KEY ||
    process.env.HERE_API_KEY ||
    process.env.WILSY_NOMINATIM_USER_AGENT
  );
  const metrics = {
    totalSources,
    liveSources,
    sourcesWithRecords,
    emptyLiveSources: emptyLiveSources.length,
    sourceGaps: sourceGaps.length,
    evidenceRecords: Number(evidenceSource.recordCount || 0),
    connectorRecords: Number(connectorSource.recordCount || 0),
    crmRelatedRoutes,
    totalRouteDeclarations,
    addressProviderConfigured,
  };
  const sourceHealthScore = totalSources ? (liveSources / totalSources) * 100 : 0;
  const dataDensityScore = totalSources ? (sourcesWithRecords / totalSources) * 100 : 0;
  const routeSurfaceScore =
    crmRelatedRoutes > 0 && routeGroupCounts.command && routeGroupCounts.live
      ? 100
      : crmRelatedRoutes > 0
        ? 72
        : 0;
  const evidenceScore = metrics.evidenceRecords > 0 ? 100 : 38;
  const connectorScore = metrics.connectorRecords > 0 ? 100 : 35;
  const addressScore = addressProviderConfigured ? 92 : 30;
  const readinessScore = clampWilsyR91K113Score(
    sourceHealthScore * 0.26 +
      routeSurfaceScore * 0.2 +
      dataDensityScore * 0.24 +
      evidenceScore * 0.12 +
      connectorScore * 0.1 +
      addressScore * 0.08
  );
  const guide = {
    algorithmVersion: WILSY_R91K113_SOURCE_POSTURE_GUIDE_ALGORITHM,
    generatedAt: new Date().toISOString(),
    tenantId,
    postureGrade: resolveWilsyR91K113PostureGrade(readinessScore),
    readinessScore,
    aiOperatingMode: resolveWilsyR91K113AiOperatingMode(metrics),
    sourceHealth: buildWilsyR91K113HealthPacket(
      'source-health',
      'Source health',
      sourceHealthScore,
      sourceGaps.length ? 'SOURCE_GAPS_PRESENT' : 'SOURCES_CONNECTED',
      `${liveSources}/${totalSources} live CRM sources.`
    ),
    routeSurfaceHealth: buildWilsyR91K113HealthPacket(
      'route-surface-health',
      'Route surface health',
      routeSurfaceScore,
      crmRelatedRoutes ? 'ROUTE_SURFACE_DYNAMIC' : 'ROUTE_SURFACE_REQUIRED',
      `${crmRelatedRoutes} dynamic CRM routes across ${Object.keys(routeGroupCounts).length} route groups.`
    ),
    dataDensityHealth: buildWilsyR91K113HealthPacket(
      'data-density-health',
      'Data density health',
      dataDensityScore,
      emptyLiveSources.length ? 'LIVE_SOURCES_EMPTY' : 'DATA_DENSITY_READY',
      `${sourcesWithRecords}/${totalSources} live sources currently contain records.`
    ),
    evidenceHealth: buildWilsyR91K113HealthPacket(
      'evidence-health',
      'Evidence health',
      evidenceScore,
      metrics.evidenceRecords > 0 ? 'EVIDENCE_AVAILABLE' : 'EVIDENCE_REQUIRED',
      `${metrics.evidenceRecords} evidence records available in the live source set.`
    ),
    connectorHealth: buildWilsyR91K113HealthPacket(
      'connector-health',
      'Connector health',
      connectorScore,
      metrics.connectorRecords > 0 ? 'CONNECTORS_REGISTERED' : 'CONNECTORS_REQUIRED',
      `${metrics.connectorRecords} source connector records available.`
    ),
    addressProviderHealth: buildWilsyR91K113HealthPacket(
      'address-provider-health',
      'Address intelligence health',
      addressScore,
      addressProviderConfigured ? 'ADDRESS_PROVIDER_CONFIGURED' : 'ADDRESS_PROVIDER_REQUIRED',
      addressProviderConfigured
        ? 'Address intelligence provider configuration detected.'
        : 'Address intelligence provider configuration required.'
    ),
    sourcePosture: {
      connectedRoutes: liveSources,
      totalRoutes: totalSources,
      sourceGaps,
      sources,
      emptyLiveSources,
    },
    routeSurface: {
      algorithmVersion: routeSurface.algorithmVersion,
      crmRelatedRoutes,
      totalRouteDeclarations,
      scannedFiles: routeSurface.scannedFiles,
      groupCounts: routeGroupCounts,
      routeFiles: routeSurface.routeFiles || [],
      cacheStatus: routeSurface.cacheStatus,
    },
    nextBestActions: buildWilsyR91K113SourceGuideActions(metrics, emptyLiveSources),
    wilsyAiDirectives: buildWilsyR91K113SourceGuideDirectives(metrics, emptyLiveSources),
  };
  const rootHash = buildWilsyR91K113SourceGuideHash(guide);

  return {
    ...guide,
    rootHash,
    rootHashShort: rootHash.slice(0, 12),
  };
}

/**
 * @function resolveWilsyR91K113GuideTenantId
 * @description Resolves the Source Posture Guide tenant id without relying on route-level private imports.
 * @param {Object} req - Express request.
 * @returns {string} Tenant id.
 * @collaboration Source posture guide, tenant-safe live telemetry, institutional finality protection.
 */
function resolveWilsyR91K113GuideTenantId(req = {}) {
  return (
    String(
      req.tenantId ||
        req.headers?.['x-tenant-id'] ||
        req.headers?.['x-wilsy-tenant-id'] ||
        req.query?.tenantId ||
        'MASTER'
    ).trim() || 'MASTER'
  );
}

/**
 * @function handleWilsyR91K113SourcePostureGuide
 * @description Returns the dynamic Source Posture Guide for Wilsy AI and operator guidance.
 * @param {Object} req - Express request.
 * @param {Object} res - Express response.
 * @param {Function} next - Express next callback.
 * @returns {Promise<void>} JSON response.
 * @collaboration Source posture guide, Wilsy AI, production readiness telemetry.
 */
async function handleWilsyR91K113SourcePostureGuide(req, res, next) {
  try {
    const tenantId = resolveWilsyR91K113GuideTenantId(req);
    const guide = await buildWilsyR91K113SourcePostureGuide(tenantId);

    res.json({
      ok: true,
      tenantId,
      guide,
    });
  } catch (error) {
    next(error);
  }
}

router.get('/source-guide', handleWilsyR91K113SourcePostureGuide);
router.get('/route-surface', handleWilsyR91K110CrmRouteSurface);
router.get('/:collection', asyncHandler(sendCrmCollection));

export default router;
