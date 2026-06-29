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
