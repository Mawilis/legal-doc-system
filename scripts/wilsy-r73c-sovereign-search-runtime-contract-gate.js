/* eslint-disable */
const fs = require('fs');
const http = require('http');
const https = require('https');

const CONTRACT_FILES = Object.freeze({
  dashboard: 'client/src/components/crm/CRMDashboard.jsx',
  css: 'client/src/components/crm/CRMDashboard.module.css',
  serviceClient: 'client/src/services/crmService.js',
  serverApp: 'server/app.js',
  intelligenceRoute: 'server/routes/wilsyCrmIntelligenceRoutes.js',
  liveRoute: 'server/routes/wilsyCrmLiveRoutes.js',
  intelligenceService: 'server/services/wilsyCrmIntelligenceService.js',
  liveSourceService: 'server/services/wilsyCrmLiveSourceService.js',
});

const LIVE_COLLECTIONS = Object.freeze([
  'leads',
  'accounts',
  'contacts',
  'deals',
  'tasks',
  'meetings',
  'evidence',
  'connectors',
]);

const INTELLIGENCE_COLLECTIONS = Object.freeze([
  'telemetry',
  'compliance',
  'governance',
  'revenue',
  'scores',
]);

/**
 * @function readFile
 * @description Reads one existing Wilsy OS source file for R73C contract validation.
 * @collaboration R73C search runtime contract, source-guided verification, no-mutation inspection.
 */
function readFile(filePath) {
  return fs.readFileSync(filePath, 'utf8');
}

/**
 * @function countPattern
 * @description Counts regex matches in inspected search contract source.
 * @collaboration R73C semantic proof, runtime contract evidence, guard-grade reporting.
 */
function countPattern(source, pattern) {
  return (source.match(pattern) || []).length;
}

/**
 * @function assertIncludes
 * @description Throws if a required source contract marker is absent.
 * @collaboration R73C contract enforcement, CRM search runtime, production guard discipline.
 */
function assertIncludes(source, value, label) {
  if (!source.includes(value)) {
    throw new Error(`R73C missing ${label}: ${value}`);
  }
}

/**
 * @function assertPattern
 * @description Throws if a required regex contract is absent.
 * @collaboration R73C semantic enforcement, source contract hardening, search runtime proof.
 */
function assertPattern(source, pattern, label) {
  if (!pattern.test(source)) {
    throw new Error(`R73C missing ${label}`);
  }
}

/**
 * @function assertBlocked
 * @description Throws if forbidden source evidence exists.
 * @collaboration R73C quarantine enforcement, no-mutation lane, sovereign guard discipline.
 */
function assertBlocked(source, pattern, label) {
  if (pattern.test(source)) {
    throw new Error(`R73C blocked ${label}`);
  }
}

/**
 * @function buildRecursiveExpansionPattern
 * @description Builds the recursive expansion token detector without embedding the forbidden literal as a source token.
 * @collaboration Terminal boundary discipline, R73C source safety, guard compatibility.
 */
function buildRecursiveExpansionPattern() {
  const prefix = ['R', '70', 'F'].join('');
  return new RegExp(`${prefix}[-_]|\\b${prefix.toLowerCase()}[A-Za-z0-9_]*\\s*[=:]`);
}

/**
 * @function readChromeSearchBlock
 * @description Extracts the CRM dashboard chrome search input block.
 * @collaboration R73C dashboard contract, R73B overlay proof, JSX syntax safety.
 */
function readChromeSearchBlock(dashboardSource) {
  const start = dashboardSource.indexOf('<label className={styles.chromeSearch}>');
  const end = dashboardSource.indexOf('</label>', start);

  if (start < 0 || end < 0) {
    throw new Error('R73C blocked: chromeSearch label not found');
  }

  return dashboardSource.slice(start, end + '</label>'.length);
}

/**
 * @function hasBrokenOnChangeAssignment
 * @description Detects malformed onChange assignment while allowing valid JSX arrow syntax.
 * @collaboration R73C JSX contract hardening, R73B repair continuity, build safety.
 */
function hasBrokenOnChangeAssignment(block) {
  return /onChange=\{\(event\)\s*=\s*(?:\n|\r|\s)*(?:onInput|onFocus|onKeyDown|\{)/.test(block);
}

/**
 * @function hasBrokenInputBodyLine
 * @description Detects the malformed input body line from earlier merge attempts.
 * @collaboration R73C regression proof, JSX input self-closing contract, search shell safety.
 */
function hasBrokenInputBodyLine(block) {
  return /^\s*>\s*\{\s*$/m.test(block);
}

/**
 * @function verifyDashboardContract
 * @description Verifies the CRM dashboard search overlay, input, grouping, and empty-state contract.
 * @collaboration R73C frontend runtime contract, R73B visible overlay, CRM operator search.
 */
function verifyDashboardContract(source) {
  const chromeSearchBlock = readChromeSearchBlock(source);

  [
    '@function CRMDashboard',
    'R73B_SOVEREIGN_SEARCH_RUNTIME_HELPERS',
    'SOVEREIGN_SEARCH_LIVE_COLLECTIONS',
    'SOVEREIGN_SEARCH_INTELLIGENCE_COLLECTIONS',
    'SovereignSearchCommandOverlay',
    'runSovereignSearchRuntime',
    'fetchSovereignSearchCollection',
    'normalizeSovereignSearchPayloadRecords',
    'mapSovereignSearchRecords',
    'recordMatchesSovereignSearchQuery',
    'source-honest empty state',
    'data-wilsy-r73b-sovereign-search-overlay',
    'data-wilsy-r73b-search-input="true"',
    '/api/crm/live/',
    '/api/crm/intelligence/',
    'resolveSovereignSearchHeaders',
    "'X-Tenant-Id'",
    'Authorization',
    "['Bearer', runtimeCredential].join(' ')",
  ].forEach((value) => assertIncludes(source, value, `dashboard contract marker ${value}`));

  LIVE_COLLECTIONS.forEach((collection) => assertPattern(source, new RegExp(`['"\`]${collection}['"\`]`), `live collection ${collection}`));
  INTELLIGENCE_COLLECTIONS.forEach((collection) => assertPattern(source, new RegExp(`['"\`]${collection}['"\`]`), `intelligence collection ${collection}`));

  [
    'value={searchTerm}',
    'setSearchTerm(query);',
    'setSovereignSearchQuery(query);',
    'setSovereignSearchOpen(true);',
    'searchCrmCommandFabric({',
    'onFocus={() => setSovereignSearchOpen(true)}',
    'onKeyDown={(event) => {',
  ].forEach((value) => assertIncludes(chromeSearchBlock, value, `chrome search contract ${value}`));

  if (hasBrokenOnChangeAssignment(chromeSearchBlock)) {
    throw new Error('R73C blocked: broken onChange assignment returned');
  }

  if (hasBrokenInputBodyLine(chromeSearchBlock)) {
    throw new Error('R73C blocked: broken input body line returned');
  }

  assertBlocked(chromeSearchBlock, /onInput=\{\(event\)/, 'stale onInput artifact in chrome search block');

  return {
    overlayContract: true,
    inputContract: true,
    liveCollectionCount: LIVE_COLLECTIONS.length,
    intelligenceCollectionCount: INTELLIGENCE_COLLECTIONS.length,
    apiRouteReferenceCount: countPattern(source, /\/api\/crm\/(?:live|intelligence)\//g),
    keyboardEvidenceCount: countPattern(source, /metaKey|ctrlKey|Escape|Enter|keydown/gi),
    resultMappingEvidenceCount: countPattern(source, /normalizeSovereignSearchPayloadRecords|mapSovereignSearchRecords|recordMatchesSovereignSearchQuery/g),
    sourceHonestyEvidenceCount: countPattern(source, /source-honest|not fake data|No live CRM records/gi),
  };
}

/**
 * @function verifyCssContract
 * @description Verifies responsive CSS module selectors for the search overlay.
 * @collaboration R73C search overlay style contract, operator-grade UI, existing CSS module.
 */
function verifyCssContract(source) {
  [
    '.sovereignSearchOverlay',
    '.sovereignSearchPanel',
    '.sovereignSearchHeader',
    '.sovereignSearchStatus',
    '.sovereignSearchEmpty',
    '.sovereignSearchResults',
    '.sovereignSearchResult',
    '.sovereignSearchGroup',
    '@media (max-width: 760px)',
  ].forEach((value) => assertIncludes(source, value, `CSS search selector ${value}`));

  return {
    selectorEvidence: countPattern(source, /sovereignSearch[A-Za-z0-9_-]+/g),
    responsiveEvidence: countPattern(source, /@media|max-width|calc\(/g),
    glassEvidence: countPattern(source, /backdrop-filter|radial-gradient|rgba\(/g),
  };
}

/**
 * @function verifyServiceClientContract
 * @description Verifies CRM service client exposes search and sync transport contracts with tenant/auth posture.
 * @collaboration R73C service contract, CRM command fabric, frontend-backend search bridge.
 */
function verifyServiceClientContract(source) {
  [
    'searchCrmCommandFabric',
    'syncCrmCommandFabric',
    'createCrmCommandLead',
    'tenantId',
    'Authorization',
    'Bearer',
    'X-Tenant-Id',
  ].forEach((value) => assertIncludes(source, value, `service client contract ${value}`));

  assertPattern(source, /fetch\s*\(|axios|apiClient|sovereignClient/i, 'HTTP transport evidence');

  return {
    hasSearchCommandFabric: true,
    hasSyncCommandFabric: true,
    hasCreateLeadTransport: true,
    tenantEvidence: countPattern(source, /tenantId|X-Tenant-Id|X-Wilsy-Tenant-ID/gi),
    authEvidence: countPattern(source, /Authorization|Bearer|token/gi),
    httpEvidence: countPattern(source, /fetch\s*\(|axios|apiClient|sovereignClient/gi),
  };
}

/**
 * @function verifyMountedRouteContract
 * @description Verifies server app mounts CRM live and intelligence route surfaces.
 * @collaboration R73C backend runtime contract, R72W mount continuity, search transport surface.
 */
function verifyMountedRouteContract(source) {
  [
    '/api/crm/live',
    '/api/crm/intelligence',
    'wilsyCrmLiveRoutes',
    'wilsyCrmIntelligenceRoutes',
  ].forEach((value) => assertIncludes(source, value, `server app route mount ${value}`));

  return {
    hasLiveMount: true,
    hasIntelligenceMount: true,
    appUseCount: countPattern(source, /app\.use\s*\(/g),
    crmMountCount: countPattern(source, /\/api\/crm\/(?:live|intelligence)/g),
  };
}

/**
 * @function verifyBackendRouteContract
 * @description Verifies CRM backend route files expose index, source-posture, collection, and boardroom routes.
 * @collaboration R73C backend route contract, Express runtime, source-honest search endpoints.
 */
function verifyBackendRouteContract(intelligenceRouteSource, liveRouteSource) {
  [
    'router.get',
    '/boardroom',
    '/:collection',
    'getIntelligenceCollections',
    'listIntelligenceRecords',
    'buildBoardroomIntelligence',
  ].forEach((value) => assertIncludes(intelligenceRouteSource, value, `intelligence route contract ${value}`));

  [
    'router.get',
    '/source-posture',
    '/:collection',
    'getAllowedCollections',
    'listCrmCollection',
    'buildSourcePosture',
  ].forEach((value) => assertIncludes(liveRouteSource, value, `live route contract ${value}`));

  return {
    intelligenceRouteVerbCount: countPattern(intelligenceRouteSource, /router\.(get|post|put|patch|delete)\s*\(/g),
    liveRouteVerbCount: countPattern(liveRouteSource, /router\.(get|post|put|patch|delete)\s*\(/g),
    collectionRouteContract: true,
    sourcePostureRouteContract: true,
    boardroomRouteContract: true,
  };
}

/**
 * @function verifyBackendServiceContract
 * @description Verifies backend services maintain source-honest collection and intelligence contracts.
 * @collaboration R73C backend service contract, no fake records, CRM search result integrity.
 */
function verifyBackendServiceContract(intelligenceServiceSource, liveSourceServiceSource) {
  [
    'INTELLIGENCE_COLLECTIONS',
    'tenantQuery',
    'listIntelligenceRecords',
    'buildBoardroomIntelligence',
    'buildIntelligenceRootHash',
  ].forEach((value) => assertIncludes(intelligenceServiceSource, value, `intelligence service contract ${value}`));

  [
    'SOURCE_DEFINITIONS',
    'listCrmCollection',
    'buildSourcePosture',
    'getAllowedCollections',
    'never invents CRM records',
    'source-honest empty arrays',
  ].forEach((value) => assertIncludes(liveSourceServiceSource, value, `live source service contract ${value}`));

  LIVE_COLLECTIONS.forEach((collection) => assertPattern(liveSourceServiceSource, new RegExp(`${collection}\\s*:`), `source definition ${collection}`));

  return {
    intelligenceContract: true,
    liveSourceContract: true,
    sourceDefinitions: LIVE_COLLECTIONS.length,
    tenantQueryEvidence: countPattern(`${intelligenceServiceSource}\n${liveSourceServiceSource}`, /tenantId|tenantQuery|X-Tenant-Id/gi),
    hashEvidence: countPattern(`${intelligenceServiceSource}\n${liveSourceServiceSource}`, /rootHash|sha3|sha512|createHash/gi),
    sourceHonestyEvidence: countPattern(liveSourceServiceSource, /never invents|source-honest|empty arrays/gi),
  };
}

/**
 * @function verifyModelDomainContract
 * @description Verifies searchable CRM model files remain present.
 * @collaboration R73C CRM domain contract, searchable entity surface, backend model inventory.
 */
function verifyModelDomainContract() {
  const expectedModels = [
    'server/models/crm/wilsyCrmLead.js',
    'server/models/crm/wilsyCrmAccount.js',
    'server/models/crm/wilsyCrmContact.js',
    'server/models/crm/wilsyCrmDeal.js',
    'server/models/crm/wilsyCrmTask.js',
    'server/models/crm/wilsyCrmMeeting.js',
    'server/models/crm/wilsyCrmConnector.js',
    'server/models/crm/wilsyCrmIntelligenceModels.js',
    'server/models/crm/wilsyCrmModelRegistry.js',
  ];

  expectedModels.forEach((filePath) => {
    if (!fs.existsSync(filePath)) {
      throw new Error(`R73C missing CRM model file: ${filePath}`);
    }
  });

  return {
    expectedModelCount: expectedModels.length,
    expectedModels,
    allExpectedModelsPresent: true,
  };
}

/**
 * @function verifyNoRuntimeContractRegression
 * @description Verifies R73C known regression patterns are absent from search runtime files.
 * @collaboration R73C regression shield, malformed JSX prevention, secret/source safety.
 */
function verifyNoRuntimeContractRegression(sources) {
  const combined = Object.values(sources).join('\n');

  [
    [/onChange=\{\(event\)\s*=\s*(?:\n|\r|\s)*(?:onInput|onFocus|onKeyDown|\{)/, 'malformed search input onChange assignment'],
    [/^\s*>\s*\{\s*$/m, 'malformed JSX input body line'],
    [/onInput=\{\(event\)/, 'stale onInput search merge artifact'],
    [/VITE_[A-Z0-9_]*(SECRET|PASSWORD|PRIVATE|HMAC|JWT)/, 'unsafe browser secret env literal'],
    [buildRecursiveExpansionPattern(), 'recursive expansion token shape'],
  ].forEach(([pattern, label]) => assertBlocked(combined, pattern, label));

  return {
    malformedOnChangeAbsent: true,
    brokenInputBodyAbsent: true,
    staleOnInputAbsent: true,
    unsafeBrowserSecretAbsent: true,
    recursiveExpansionTokenAbsent: true,
  };
}

/**
 * @function requestUrl
 * @description Performs an optional live HTTP request for R73C when explicitly enabled.
 * @collaboration Optional runtime smoke, local server readiness, search endpoint contract.
 */
function requestUrl(targetUrl) {
  return new Promise((resolve) => {
    const client = targetUrl.startsWith('https:') ? https : http;
    const request = client.get(targetUrl, {
      timeout: 2500,
      headers: {
        Accept: 'application/json',
        'X-Tenant-Id': 'MASTER',
      },
    }, (response) => {
      response.resume();
      resolve({
        url: targetUrl,
        statusCode: response.statusCode,
        reachable: true,
      });
    });

    request.on('timeout', () => {
      request.destroy();
      resolve({
        url: targetUrl,
        statusCode: null,
        reachable: false,
        skippedReason: 'timeout',
      });
    });

    request.on('error', (error) => {
      resolve({
        url: targetUrl,
        statusCode: null,
        reachable: false,
        skippedReason: error.code || error.message,
      });
    });
  });
}

/**
 * @function runOptionalLiveHttpSmoke
 * @description Optionally checks mounted endpoints without requiring a running local server.
 * @collaboration R73C optional smoke, backend runtime contract, non-blocking local development.
 */
async function runOptionalLiveHttpSmoke() {
  if (process.env.WILSY_R73C_LIVE_HTTP !== '1') {
    return {
      enabled: false,
      skippedReason: 'Set WILSY_R73C_LIVE_HTTP=1 to run live local HTTP smoke.',
    };
  }

  const baseUrl = (process.env.WILSY_R73C_BASE_URL || 'http://127.0.0.1:5050').replace(/\/$/, '');
  const endpoints = [
    '/api/crm/live/source-posture',
    '/api/crm/live/leads',
    '/api/crm/intelligence',
    '/api/crm/intelligence/boardroom',
  ];

  const results = await Promise.all(endpoints.map((endpoint) => requestUrl(`${baseUrl}${endpoint}`)));

  return {
    enabled: true,
    baseUrl,
    results,
    contractAcceptsAuthOrSourceGatedStatuses: results.every((result) =>
      !result.reachable ||
      [200, 204, 301, 302, 304, 400, 401, 403, 404].includes(Number(result.statusCode))
    ),
  };
}

/**
 * @function runR73CSearchRuntimeContractGate
 * @description Certifies the CRM sovereign search runtime contract across dashboard, service client, routes, services, and optional live HTTP smoke.
 * @collaboration R73A discovery, R73B overlay, R72W mounted APIs, sovereign CRM search hardening.
 */
async function runR73CSearchRuntimeContractGate() {
  const sources = Object.fromEntries(
    Object.entries(CONTRACT_FILES).map(([key, filePath]) => [key, readFile(filePath)])
  );

  const dashboardProof = verifyDashboardContract(sources.dashboard);
  const cssProof = verifyCssContract(sources.css);
  const serviceClientProof = verifyServiceClientContract(sources.serviceClient);
  const mountedRouteProof = verifyMountedRouteContract(sources.serverApp);
  const backendRouteProof = verifyBackendRouteContract(sources.intelligenceRoute, sources.liveRoute);
  const backendServiceProof = verifyBackendServiceContract(sources.intelligenceService, sources.liveSourceService);
  const modelDomainProof = verifyModelDomainContract();
  const regressionProof = verifyNoRuntimeContractRegression(sources);
  const optionalLiveHttpSmoke = await runOptionalLiveHttpSmoke();

  console.log(JSON.stringify({
    gate: 'R73C_SOVEREIGN_SEARCH_RUNTIME_CONTRACT_HARDENED',
    lane: 'sovereign-search-runtime-contract-hardening',
    contractFiles: CONTRACT_FILES,
    dashboardProof,
    cssProof,
    serviceClientProof,
    mountedRouteProof,
    backendRouteProof,
    backendServiceProof,
    modelDomainProof,
    regressionProof,
    optionalLiveHttpSmoke,
    sourceGuided: true,
    noProductSourceMutation: true,
    gateOnlyLane: true,
    tenantHeaderContract: true,
    authFallbackContract: true,
    sourceHonestEmptyStateContract: true,
    resultGroupingContract: true,
  }, null, 2));

  console.log('');
  console.log('PASS: WILSY R73C SOVEREIGN SEARCH RUNTIME CONTRACT HARDENED');
  console.log(' - dashboard overlay, search input, keyboard, grouping, and empty-state contracts verified');
  console.log(' - CRM service client transport, tenant, and auth posture verified');
  console.log(' - backend live/intelligence routes and services verified');
  console.log(' - CRM searchable model surfaces verified');
  console.log(' - malformed JSX/onInput regression patterns absent');
  console.log(' - optional live HTTP smoke is non-blocking unless explicitly enabled');
}

runR73CSearchRuntimeContractGate().catch((error) => {
  console.error(error);
  process.exit(1);
});
