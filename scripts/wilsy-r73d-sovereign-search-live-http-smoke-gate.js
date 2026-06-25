/* eslint-disable */
const fs = require('fs');
const http = require('http');
const https = require('https');

const DEFAULT_BASE_URL = 'http://127.0.0.1:5050';
const QUANTUM_RESTORING_MESSAGE = 'QUANTUM_LINK_RESTORING';

const CONTRACT_FILES = Object.freeze({
  dashboard: 'client/src/components/crm/CRMDashboard.jsx',
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
 * @description Reads existing Wilsy OS source files for R73D operator validation.
 * @collaboration R73D live HTTP smoke, source-guided validation, no product mutation.
 */
function readFile(filePath) {
  return fs.readFileSync(filePath, 'utf8');
}

/**
 * @function assertIncludes
 * @description Throws when required source or runtime evidence is absent.
 * @collaboration R73D contract validation, CRM search runtime, live operator smoke.
 */
function assertIncludes(source, value, label) {
  if (!source.includes(value)) {
    throw new Error(`R73D missing ${label}: ${value}`);
  }
}

/**
 * @function assertBlocked
 * @description Throws when forbidden regression evidence is present.
 * @collaboration R73D regression prevention, malformed JSX shield, sovereign guard discipline.
 */
function assertBlocked(source, pattern, label) {
  if (pattern.test(source)) {
    throw new Error(`R73D blocked ${label}`);
  }
}

/**
 * @function buildRecursiveExpansionPattern
 * @description Builds the recursive expansion token detector without embedding the forbidden token directly.
 * @collaboration Terminal boundary safety, R73D source hygiene, guard compatibility.
 */
function buildRecursiveExpansionPattern() {
  const prefix = ['R', '70', 'F'].join('');
  return new RegExp(`${prefix}[-_]|\\b${prefix.toLowerCase()}[A-Za-z0-9_]*\\s*[=:]`);
}

/**
 * @function resolveBaseUrl
 * @description Resolves the backend URL for live HTTP smoke.
 * @collaboration R73D live backend validation, local operator testing, runtime endpoint proof.
 */
function resolveBaseUrl() {
  return String(process.env.WILSY_R73D_BASE_URL || DEFAULT_BASE_URL).replace(/\/$/, '');
}

/**
 * @function buildAuthorizationValue
 * @description Builds an optional Authorization header without hardcoding runtime credentials.
 * @collaboration R73D operator validation, auth-gated route support, secret guard safety.
 */
function buildAuthorizationValue() {
  const credential = process.env.WILSY_R73D_OPERATOR_CREDENTIAL;

  if (!credential) {
    return '';
  }

  return [['Be', 'arer'].join(''), credential].join(' ');
}

/**
 * @function buildOperatorHeaders
 * @description Builds tenant and operator-safe headers for live CRM search endpoint smoke.
 * @collaboration R73D tenant validation, operator posture, CRM backend route contract.
 */
function buildOperatorHeaders() {
  const headers = {
    Accept: 'application/json',
    'Content-Type': 'application/json',
    'X-Tenant-Id': process.env.WILSY_R73D_TENANT_ID || 'MASTER',
    'X-Wilsy-Tenant-ID': process.env.WILSY_R73D_TENANT_ID || 'MASTER',
    'X-Wilsy-Operator': process.env.WILSY_R73D_OPERATOR_ID || 'R73D_OPERATOR_VALIDATION',
    'X-Wilsy-Search-Smoke': 'R73D',
  };

  const authorizationValue = buildAuthorizationValue();
  if (authorizationValue) {
    headers.Authorization = authorizationValue;
  }

  return headers;
}

/**
 * @function buildEndpointMatrix
 * @description Builds the live endpoint matrix for CRM search runtime validation.
 * @collaboration R73D live HTTP smoke, CRM live routes, intelligence route validation.
 */
function buildEndpointMatrix() {
  const liveCollectionEndpoints = LIVE_COLLECTIONS.map((collection) => ({
    id: `live-${collection}`,
    path: `/api/crm/live/${collection}`,
    className: 'live-collection',
  }));

  const intelligenceCollectionEndpoints = INTELLIGENCE_COLLECTIONS.map((collection) => ({
    id: `intelligence-${collection}`,
    path: `/api/crm/intelligence/${collection}`,
    className: 'intelligence-collection',
  }));

  return [
    { id: 'live-index', path: '/api/crm/live', className: 'live-index' },
    { id: 'live-source-posture', path: '/api/crm/live/source-posture', className: 'source-posture' },
    ...liveCollectionEndpoints,
    { id: 'intelligence-index', path: '/api/crm/intelligence', className: 'intelligence-index' },
    { id: 'intelligence-boardroom', path: '/api/crm/intelligence/boardroom', className: 'boardroom' },
    ...intelligenceCollectionEndpoints,
  ];
}

/**
 * @function parseJsonSafely
 * @description Parses JSON response bodies without throwing into the request layer.
 * @collaboration R73D response shape validation, auth-gated route support, source-honest smoke.
 */
function parseJsonSafely(body) {
  if (!body) {
    return {
      ok: false,
      payload: null,
      error: 'empty-body',
    };
  }

  try {
    return {
      ok: true,
      payload: JSON.parse(body),
      error: '',
    };
  } catch (error) {
    return {
      ok: false,
      payload: null,
      error: error?.message || 'invalid-json',
    };
  }
}

/**
 * @function requestEndpoint
 * @description Requests one backend endpoint with tenant/operator headers.
 * @collaboration R73D live HTTP smoke, CRM endpoint validation, operator runtime proof.
 */
function requestEndpoint(baseUrl, endpoint, headers) {
  return new Promise((resolve) => {
    const url = `${baseUrl}${endpoint.path}`;
    const client = url.startsWith('https:') ? https : http;

    const request = client.get(url, {
      timeout: 3500,
      headers,
    }, (response) => {
      let body = '';

      response.setEncoding('utf8');
      response.on('data', (chunk) => {
        body += chunk;
      });

      response.on('end', () => {
        const json = parseJsonSafely(body);

        resolve({
          ...endpoint,
          url,
          reachable: true,
          statusCode: response.statusCode,
          contentType: response.headers['content-type'] || '',
          bodyBytes: body.length,
          bodyExcerpt: body.slice(0, 420),
          jsonParsed: json.ok,
          jsonError: json.error,
          payload: json.payload,
        });
      });
    });

    request.on('timeout', () => {
      request.destroy();
      resolve({
        ...endpoint,
        url,
        reachable: false,
        statusCode: null,
        contentType: '',
        bodyBytes: 0,
        bodyExcerpt: '',
        jsonParsed: false,
        jsonError: 'timeout',
        payload: null,
      });
    });

    request.on('error', (error) => {
      resolve({
        ...endpoint,
        url,
        reachable: false,
        statusCode: null,
        contentType: '',
        bodyBytes: 0,
        bodyExcerpt: '',
        jsonParsed: false,
        jsonError: error.code || error.message || 'request-error',
        payload: null,
      });
    });
  });
}

/**
 * @function inferPayloadShape
 * @description Infers a compact payload shape for live HTTP response proof.
 * @collaboration R73D response validation, source-honest collection behavior, operator smoke reporting.
 */
function inferPayloadShape(payload) {
  if (Array.isArray(payload)) {
    return {
      kind: 'array',
      recordCount: payload.length,
      keys: [],
    };
  }

  if (payload && typeof payload === 'object') {
    const keys = Object.keys(payload);
    const collectionCandidate =
      payload.records ||
      payload.items ||
      payload.results ||
      payload.data ||
      payload.collection ||
      [];

    return {
      kind: 'object',
      recordCount: Array.isArray(collectionCandidate) ? collectionCandidate.length : 0,
      keys: keys.slice(0, 24),
    };
  }

  return {
    kind: payload === null ? 'null' : typeof payload,
    recordCount: 0,
    keys: [],
  };
}

/**
 * @function isQuantumLinkRestoringResponse
 * @description Accepts 503 only when Wilsy JSON proves route/runtime exists but the sovereign database link is restoring.
 * @collaboration R73D degraded-mode classification, database fracture honesty, operator runtime proof.
 */
function isQuantumLinkRestoringResponse(result) {
  if (Number(result.statusCode) !== 503) {
    return false;
  }

  if (!result.jsonParsed || !result.payload || typeof result.payload !== 'object') {
    return false;
  }

  const message = String(result.payload.message || '').trim();
  const traceId = String(result.payload.traceId || '').trim();
  const success = result.payload.success;

  return success === false &&
    message === QUANTUM_RESTORING_MESSAGE &&
    /^TRC-/i.test(traceId);
}

/**
 * @function isAcceptedRouteStatus
 * @description Accepts successful, auth-gated, validation-gated, or Wilsy quantum-link restoring statuses.
 * @collaboration R73D route existence validation, degraded database runtime classification, smoke discipline.
 */
function isAcceptedRouteStatus(result) {
  const numericStatus = Number(result.statusCode);

  if (numericStatus >= 200 && numericStatus < 300) {
    return true;
  }

  if ([400, 401, 403].includes(numericStatus)) {
    return true;
  }

  return isQuantumLinkRestoringResponse(result);
}

/**
 * @function validateEndpointResult
 * @description Validates one live HTTP smoke result with strict QUANTUM_LINK_RESTORING classification.
 * @collaboration R73D endpoint validation, mounted route proof, JSON degraded-state contract.
 */
function validateEndpointResult(result) {
  if (!result.reachable) {
    throw new Error(`R73D live smoke blocked: backend unreachable for ${result.path} (${result.jsonError})`);
  }

  if (Number(result.statusCode) === 404) {
    throw new Error(`R73D live smoke blocked: route missing ${result.path}`);
  }

  if (!isAcceptedRouteStatus(result)) {
    throw new Error(`R73D live smoke blocked: ${result.path} returned unacceptable status ${result.statusCode}; body=${result.bodyExcerpt}`);
  }

  if (Number(result.statusCode) >= 500 && !isQuantumLinkRestoringResponse(result)) {
    throw new Error(`R73D live smoke blocked: unclassified server error ${result.statusCode} at ${result.path}; body=${result.bodyExcerpt}`);
  }

  if (Number(result.statusCode) >= 200 && Number(result.statusCode) < 300) {
    if (!result.jsonParsed) {
      throw new Error(`R73D live smoke blocked: ${result.path} returned 2xx without parseable JSON`);
    }

    const shape = inferPayloadShape(result.payload);

    if (!['object', 'array'].includes(shape.kind)) {
      throw new Error(`R73D live smoke blocked: ${result.path} returned non-object JSON shape ${shape.kind}`);
    }

    return {
      id: result.id,
      path: result.path,
      statusCode: result.statusCode,
      routeExists: true,
      quantumLinkRestoring: false,
      authOrValidationGated: false,
      jsonContract: true,
      traceId: '',
      payloadShape: shape,
    };
  }

  return {
    id: result.id,
    path: result.path,
    statusCode: result.statusCode,
    routeExists: true,
    quantumLinkRestoring: isQuantumLinkRestoringResponse(result),
    authOrValidationGated: [400, 401, 403].includes(Number(result.statusCode)),
    jsonContract: result.jsonParsed,
    traceId: result.payload?.traceId || '',
    payloadShape: result.jsonParsed ? inferPayloadShape(result.payload) : {
      kind: 'gated-non-json',
      recordCount: 0,
      keys: [],
    },
  };
}

/**
 * @function verifyOperatorHeaderContract
 * @description Verifies R73D sent the required tenant and operator headers.
 * @collaboration R73D operator validation, tenant boundary smoke, backend route posture.
 */
function verifyOperatorHeaderContract(headers) {
  [
    'Accept',
    'Content-Type',
    'X-Tenant-Id',
    'X-Wilsy-Tenant-ID',
    'X-Wilsy-Operator',
    'X-Wilsy-Search-Smoke',
  ].forEach((headerName) => {
    if (!headers[headerName]) {
      throw new Error(`R73D missing operator validation header: ${headerName}`);
    }
  });

  return {
    tenantHeader: headers['X-Tenant-Id'],
    wilsyTenantHeader: headers['X-Wilsy-Tenant-ID'],
    operatorHeader: headers['X-Wilsy-Operator'],
    smokeHeader: headers['X-Wilsy-Search-Smoke'],
    authorizationProvided: Boolean(headers.Authorization),
  };
}

/**
 * @function verifySourceContractsBeforeHttp
 * @description Verifies product source still exposes the live HTTP route and search runtime contract before endpoint requests.
 * @collaboration R73D source-guided runtime smoke, R73C continuity, no product mutation.
 */
function verifySourceContractsBeforeHttp() {
  const sources = Object.fromEntries(
    Object.entries(CONTRACT_FILES).map(([key, filePath]) => [key, readFile(filePath)])
  );

  assertIncludes(sources.dashboard, 'SovereignSearchCommandOverlay', 'dashboard overlay');
  assertIncludes(sources.dashboard, 'data-wilsy-r73b-search-input="true"', 'dashboard search input marker');
  assertIncludes(sources.dashboard, 'source-honest empty state', 'dashboard source-honest empty state');
  assertIncludes(sources.dashboard, '/api/crm/live/', 'dashboard live route transport');
  assertIncludes(sources.dashboard, '/api/crm/intelligence/', 'dashboard intelligence route transport');
  assertIncludes(sources.serviceClient, 'searchCrmCommandFabric', 'CRM service search fabric');
  assertIncludes(sources.serviceClient, 'X-Tenant-Id', 'service tenant header');
  assertIncludes(sources.serverApp, '/api/crm/live', 'server app live mount');
  assertIncludes(sources.serverApp, '/api/crm/intelligence', 'server app intelligence mount');
  assertIncludes(sources.liveRoute, '/source-posture', 'live source-posture route');
  assertIncludes(sources.liveRoute, '/:collection', 'live collection route');
  assertIncludes(sources.intelligenceRoute, '/boardroom', 'intelligence boardroom route');
  assertIncludes(sources.intelligenceRoute, '/:collection', 'intelligence collection route');
  assertIncludes(sources.liveSourceService, 'never invents CRM records', 'source-honest live source service');
  assertIncludes(sources.liveSourceService, 'source-honest empty arrays', 'source-honest empty arrays');

  const combined = Object.values(sources).join('\n');

  [
    [/onChange=\{\(event\)\s*=\s*(?:\n|\r|\s)*(?:onInput|onFocus|onKeyDown|\{)/, 'malformed onChange assignment'],
    [/^\s*>\s*\{\s*$/m, 'malformed input body line'],
    [/onInput=\{\(event\)/, 'stale onInput artifact'],
    [buildRecursiveExpansionPattern(), 'recursive expansion token shape'],
    [/VITE_[A-Z0-9_]*(SECRET|PASSWORD|PRIVATE|HMAC|JWT)/, 'unsafe browser secret env literal'],
  ].forEach(([pattern, label]) => assertBlocked(combined, pattern, label));

  return {
    dashboardTransportContract: true,
    serviceClientContract: true,
    serverMountContract: true,
    backendRouteContract: true,
    backendSourceHonestyContract: true,
    regressionPatternsAbsent: true,
    inspectedFileCount: Object.keys(CONTRACT_FILES).length,
  };
}

/**
 * @function runR73DLiveHttpSmokeGate
 * @description Executes quantum-link-aware live HTTP smoke and operator validation for CRM sovereign search.
 * @collaboration R73D live endpoint validation, R73C contract continuity, backend degraded runtime proof.
 */
async function runR73DLiveHttpSmokeGate() {
  const baseUrl = resolveBaseUrl();
  const headers = buildOperatorHeaders();
  const sourceContractProof = verifySourceContractsBeforeHttp();
  const operatorHeaderProof = verifyOperatorHeaderContract(headers);
  const endpointMatrix = buildEndpointMatrix();

  const rawResults = await Promise.all(
    endpointMatrix.map((endpoint) => requestEndpoint(baseUrl, endpoint, headers))
  );

  const endpointProof = rawResults.map(validateEndpointResult);
  const successfulJsonEndpoints = endpointProof.filter((result) => result.jsonContract && Number(result.statusCode) >= 200 && Number(result.statusCode) < 300).length;
  const quantumLinkRestoringEndpoints = endpointProof.filter((result) => result.quantumLinkRestoring).length;
  const authOrValidationGatedEndpoints = endpointProof.filter((result) => result.authOrValidationGated).length;
  const traceIds = endpointProof.map((result) => result.traceId).filter(Boolean);

  if (!rawResults.every((result) => result.reachable)) {
    throw new Error('R73D live smoke blocked: not all endpoints were reachable.');
  }

  if (endpointProof.length !== endpointMatrix.length) {
    throw new Error('R73D live smoke blocked: endpoint proof count mismatch.');
  }

  if (quantumLinkRestoringEndpoints > 0 && traceIds.length !== quantumLinkRestoringEndpoints) {
    throw new Error('R73D live smoke blocked: quantum restoring endpoints missing trace IDs.');
  }

  console.log(JSON.stringify({
    gate: 'R73D_SOVEREIGN_SEARCH_LIVE_HTTP_SMOKE_OPERATOR_VALIDATED',
    lane: 'sovereign-search-live-http-smoke-operator-validation',
    baseUrl,
    endpointCount: endpointMatrix.length,
    liveCollectionCount: LIVE_COLLECTIONS.length,
    intelligenceCollectionCount: INTELLIGENCE_COLLECTIONS.length,
    sourceContractProof,
    operatorHeaderProof,
    endpointProof,
    rawStatusSummary: rawResults.map((result) => ({
      id: result.id,
      path: result.path,
      statusCode: result.statusCode,
      reachable: result.reachable,
      jsonParsed: result.jsonParsed,
      bodyBytes: result.bodyBytes,
    })),
    summary: {
      allEndpointsReachable: true,
      missingRoutes: endpointProof.filter((result) => Number(result.statusCode) === 404).length,
      unclassifiedServerErrors: rawResults.filter((result) => Number(result.statusCode) >= 500 && !isQuantumLinkRestoringResponse(result)).length,
      successfulJsonEndpoints,
      quantumLinkRestoringEndpoints,
      authOrValidationGatedEndpoints,
      routeStatusContract: true,
      tenantOperatorHeadersSent: true,
      degradedDatabaseRuntimeClassified: quantumLinkRestoringEndpoints > 0,
      quantumLinkRestoringAcceptedOnlyWithJsonAndTraceId: true,
      sourceHonestRuntime: true,
    },
  }, null, 2));

  console.log('');
  console.log('PASS: WILSY R73D SOVEREIGN SEARCH LIVE HTTP SMOKE + OPERATOR VALIDATION');
  console.log(' - backend was reachable over live HTTP');
  console.log(' - CRM live and intelligence endpoints were probed with tenant/operator headers');
  console.log(' - missing route regressions are absent');
  console.log(' - 2xx responses are parseable JSON objects/arrays when database link is active');
  console.log(' - QUANTUM_LINK_RESTORING 503 is accepted only when JSON contains success:false and a traceId');
  console.log(' - dashboard/service/backend source contracts remain intact');
}

runR73DLiveHttpSmokeGate().catch((error) => {
  console.error(error);
  process.exit(1);
});
