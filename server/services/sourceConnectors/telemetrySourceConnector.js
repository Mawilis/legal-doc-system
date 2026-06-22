/* eslint-disable */
/**
 * ╔══════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS — TELEMETRY SOURCE CONNECTOR                                      ║
 * ║ VERSION: 1.0.0-PRODUCTION-NO-FAKE-DATA                                     ║
 * ║ FILE: server/services/sourceConnectors/telemetrySourceConnector.js          ║
 * ║ PURPOSE: Verify uptime, incidents and change-control evidence for reliance. ║
 * ╚══════════════════════════════════════════════════════════════════════════════╝
 *
 * @description
 * This connector never fabricates operational verification.
 *
 * It supports:
 * - Local evidence file: WILSY_TELEMETRY_EVIDENCE_FILE
 * - Generic telemetry evidence API: WILSY_TELEMETRY_API_URL
 * - Prometheus query API: WILSY_PROMETHEUS_BASE_URL
 * - Datadog metrics API: WILSY_DATADOG_API_KEY + WILSY_DATADOG_APP_KEY
 * - PagerDuty incidents API: WILSY_PAGERDUTY_API_TOKEN
 * - Sentry issues API: WILSY_SENTRY_AUTH_TOKEN
 * - GitHub change-control evidence: WILSY_GITHUB_TOKEN + WILSY_GITHUB_OWNER + WILSY_GITHUB_REPO
 * - GitLab merge-request evidence: WILSY_GITLAB_TOKEN + WILSY_GITLAB_PROJECT_ID
 *
 * VERIFIED requires:
 * - verified true or status VERIFIED
 * - sourceId / recordId / id
 * - retrievedAt / timestamp / generatedAt
 * - evidence payload
 *
 * Uptime may be verified from live metrics.
 * Incident log may be verified from live incident/issue sources.
 * Change-control may be verified from deployments, pull requests, merge requests, releases or explicit evidence.
 */

import crypto from 'node:crypto';
import { existsSync } from 'node:fs';
import { readFile } from 'node:fs/promises';

const STATUS = Object.freeze({
  VERIFIED: 'VERIFIED',
  PENDING: 'PENDING',
  MISSING: 'MISSING',
  ERROR: 'ERROR',
});

const TELEMETRY_EVIDENCE_TYPES = Object.freeze({
  UPTIME: 'UPTIME',
  INCIDENT_LOG: 'INCIDENT_LOG',
  CHANGE_CONTROL_LOG: 'CHANGE_CONTROL_LOG',
});

const DEFAULT_DATADOG_SITE = 'datadoghq.com';
const DEFAULT_SENTRY_BASE_URL = 'https://sentry.io';
const DEFAULT_GITHUB_BASE_URL = 'https://api.github.com';
const DEFAULT_GITLAB_BASE_URL = 'https://gitlab.com/api/v4';

/**
 * @function nowIso
 * @description Returns current ISO timestamp.
 * @returns {string} ISO timestamp.
 */
function nowIso() {
  return new Date().toISOString();
}

/**
 * @function stableStringify
 * @description Deterministically serializes payloads for forensic hashing.
 * @param {*} value - Value to serialize.
 * @returns {string} Stable JSON.
 */
function stableStringify(value) {
  if (value === null || typeof value !== 'object') return JSON.stringify(value);
  if (Array.isArray(value)) return `[${value.map((item) => stableStringify(item)).join(',')}]`;

  return `{${Object.keys(value)
    .sort()
    .map((key) => `${JSON.stringify(key)}:${stableStringify(value[key])}`)
    .join(',')}}`;
}

/**
 * @function hashEvidence
 * @description Creates a forensic evidence hash.
 * @param {*} payload - Evidence payload.
 * @returns {{algorithm:string, hash:string}} Hash output.
 */
function hashEvidence(payload) {
  const algorithm = crypto.getHashes().includes('sha3-512') ? 'sha3-512' : 'sha512';

  return {
    algorithm,
    hash: crypto.createHash(algorithm).update(stableStringify(payload)).digest('hex'),
  };
}

/**
 * @function env
 * @description Reads and trims an environment variable.
 * @param {string} name - Environment variable name.
 * @returns {string} Value.
 */
function env(name) {
  return String(process.env[name] || '').trim();
}

/**
 * @function normalizeTenantId
 * @description Normalizes tenant id.
 * @param {string} tenantId - Tenant id.
 * @returns {string} Normalized tenant id.
 */
function normalizeTenantId(tenantId = 'MASTER') {
  return String(tenantId || 'MASTER').trim() || 'MASTER';
}

/**
 * @function evidenceFilePath
 * @description Resolves local telemetry evidence file path.
 * @returns {string} Evidence file path.
 */
function evidenceFilePath() {
  return env('WILSY_TELEMETRY_EVIDENCE_FILE');
}

/**
 * @function genericTelemetryApiUrl
 * @description Resolves generic telemetry evidence API base URL.
 * @returns {string} API base URL.
 */
function genericTelemetryApiUrl() {
  return env('WILSY_TELEMETRY_API_URL').replace(/\/$/, '');
}

/**
 * @function safeJsonParse
 * @description Parses JSON evidence with descriptive errors.
 * @param {string} content - JSON content.
 * @param {string} label - Source label.
 * @returns {*} Parsed JSON.
 */
function safeJsonParse(content, label) {
  try {
    return JSON.parse(content);
  } catch (error) {
    const enriched = new Error(`Invalid telemetry evidence JSON from ${label}: ${error.message}`);
    enriched.cause = error;
    throw enriched;
  }
}

/**
 * @function artifactHints
 * @description Extracts telemetry lookup hints from artifact/context.
 * @param {object} context - Source registry context.
 * @returns {object} Lookup hints.
 */
function artifactHints(context = {}) {
  const artifact = context.artifact || {};

  return {
    tenantId: normalizeTenantId(context.tenantId),
    serviceName:
      artifact.serviceName ||
      artifact.application ||
      artifact.appName ||
      artifact.product ||
      artifact.title ||
      '',
    environment:
      artifact.environment || env('WILSY_ENVIRONMENT') || env('NODE_ENV') || 'production',
    artifactId: artifact.id || artifact.type || artifact.title || '',
    slaId: artifact.slaId || artifact.contractId || artifact.agreementId || '',
    incidentServiceId: artifact.pagerDutyServiceId || artifact.serviceId || '',
    repository: artifact.repository || artifact.repo || '',
    owner: artifact.repositoryOwner || artifact.owner || '',
  };
}

/**
 * @function fetchJson
 * @description Fetches JSON with strict error handling.
 * @param {string|URL} url - URL.
 * @param {object} options - Fetch options.
 * @returns {Promise<object|Array>} JSON response or connector error marker.
 */
async function fetchJson(url, options = {}) {
  const response = await fetch(url, {
    ...options,
    headers: {
      Accept: 'application/json',
      ...(options.headers || {}),
    },
  });

  if (!response.ok) {
    return {
      __connectorStatus: STATUS.ERROR,
      __message: `HTTP ${response.status}: ${await response.text()}`,
    };
  }

  return response.json();
}

/**
 * @function readFileEvidence
 * @description Reads local telemetry evidence file.
 * @returns {Promise<object|null>} Evidence store.
 */
async function readFileEvidence() {
  const filePath = evidenceFilePath();

  if (!filePath) return null;

  if (!existsSync(filePath)) {
    return {
      __connectorStatus: STATUS.MISSING,
      __message: `Configured telemetry evidence file does not exist: ${filePath}`,
    };
  }

  const content = await readFile(filePath, 'utf8');

  return safeJsonParse(content, filePath);
}

/**
 * @function selectTenantEvidence
 * @description Selects tenant-specific telemetry evidence.
 * @param {object} store - Evidence store.
 * @param {string} tenantId - Tenant id.
 * @returns {object|null} Tenant evidence.
 */
function selectTenantEvidence(store = {}, tenantId = 'MASTER') {
  const normalizedTenantId = normalizeTenantId(tenantId);

  if (store.tenantId && normalizeTenantId(store.tenantId) === normalizedTenantId) return store;
  if (store.tenants && store.tenants[normalizedTenantId]) return store.tenants[normalizedTenantId];
  if (store[normalizedTenantId]) return store[normalizedTenantId];

  return store.telemetry || store.Telemetry || null;
}

/**
 * @function normalizeEvidenceRecord
 * @description Strictly normalizes evidence records into Source Registry format.
 * @param {string} evidenceType - Evidence type.
 * @param {object} record - Evidence record.
 * @param {object} context - Source context.
 * @returns {object} Connector result.
 */
function normalizeEvidenceRecord(evidenceType, record, context = {}) {
  if (!record) {
    return {
      status: STATUS.PENDING,
      evidenceType,
      message: `${evidenceType} evidence not found.`,
    };
  }

  if (record.__connectorStatus) {
    return {
      status: record.__connectorStatus,
      evidenceType,
      message: record.__message || record.message || `${evidenceType} source failed.`,
    };
  }

  const evidencePayload =
    record.evidence !== undefined
      ? record.evidence
      : record.data !== undefined
        ? record.data
        : record.record !== undefined
          ? record.record
          : null;

  const sourceId = record.sourceId || record.recordId || record.id || null;
  const retrievedAt = record.retrievedAt || record.timestamp || record.generatedAt || null;
  const verified = record.status === STATUS.VERIFIED || record.verified === true;

  const evidence = {
    evidenceType,
    tenantId: normalizeTenantId(context.tenantId),
    artifact: context.artifact?.id || context.artifact?.type || context.artifact?.title || null,
    sourceId,
    retrievedAt,
    evidence: evidencePayload,
  };

  const seal = hashEvidence(evidence);

  if (
    !verified ||
    !sourceId ||
    !retrievedAt ||
    evidencePayload === null ||
    evidencePayload === undefined
  ) {
    return {
      status: STATUS.PENDING,
      verified: false,
      evidenceType,
      sourceId,
      retrievedAt,
      message: `${evidenceType} evidence is present but incomplete for boardroom reliance.`,
      requirements: {
        verifiedStatus: verified,
        sourceId: Boolean(sourceId),
        retrievedAt: Boolean(retrievedAt),
        evidencePayload: evidencePayload !== null && evidencePayload !== undefined,
      },
      evidence,
      evidenceHash: seal.hash,
      hashAlgorithm: seal.algorithm,
    };
  }

  return {
    status: STATUS.VERIFIED,
    verified: true,
    evidenceType,
    sourceId,
    retrievedAt,
    evidence,
    evidenceHash: seal.hash,
    hashAlgorithm: seal.algorithm,
  };
}

/**
 * @function fetchGenericApiEvidence
 * @description Fetches evidence from a generic Wilsy telemetry evidence API.
 * @param {string} evidenceType - Evidence type.
 * @param {object} context - Source context.
 * @returns {Promise<object|null>} Evidence.
 */
async function fetchGenericApiEvidence(evidenceType, context = {}) {
  const baseUrl = genericTelemetryApiUrl();

  if (!baseUrl) return null;

  const hints = artifactHints(context);
  const url = new URL(`${baseUrl}/telemetry/evidence`);

  url.searchParams.set('tenantId', hints.tenantId);
  url.searchParams.set('type', evidenceType);
  url.searchParams.set('environment', hints.environment);

  if (hints.serviceName) url.searchParams.set('serviceName', hints.serviceName);
  if (hints.slaId) url.searchParams.set('slaId', hints.slaId);
  if (hints.artifactId) url.searchParams.set('artifactId', hints.artifactId);

  const token = env('WILSY_TELEMETRY_API_TOKEN');

  return fetchJson(url, {
    headers: {
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      'X-Wilsy-Trace-Id': context.traceId || `TEL-${Date.now().toString(16).toUpperCase()}`,
    },
  });
}

/**
 * @function evidenceFromLocalOrGenericStore
 * @description Reads telemetry evidence from local file or generic API.
 * @param {string} evidenceType - Evidence type.
 * @param {object} context - Source context.
 * @returns {Promise<object|null>} Normalized evidence or null.
 */
async function evidenceFromLocalOrGenericStore(evidenceType, context = {}) {
  const apiEvidence = genericTelemetryApiUrl()
    ? await fetchGenericApiEvidence(evidenceType, context)
    : null;

  if (apiEvidence) {
    const selected = selectTenantEvidence(apiEvidence, context.tenantId);
    const record =
      selected?.[evidenceType] ||
      selected?.[evidenceType.toLowerCase()] ||
      apiEvidence[evidenceType] ||
      apiEvidence;
    return normalizeEvidenceRecord(evidenceType, record, context);
  }

  const fileEvidence = evidenceFilePath() ? await readFileEvidence() : null;

  if (fileEvidence?.__connectorStatus) {
    return {
      status: fileEvidence.__connectorStatus,
      evidenceType,
      message: fileEvidence.__message,
    };
  }

  if (fileEvidence) {
    const selected = selectTenantEvidence(fileEvidence, context.tenantId);
    const record = selected?.[evidenceType] || selected?.[evidenceType.toLowerCase()] || null;
    return normalizeEvidenceRecord(evidenceType, record, context);
  }

  return null;
}

/**
 * @function prometheusQuery
 * @description Executes a Prometheus instant query.
 * @param {string} query - PromQL query.
 * @returns {Promise<object|null>} Prometheus response.
 */
async function prometheusQuery(query) {
  const baseUrl = env('WILSY_PROMETHEUS_BASE_URL').replace(/\/$/, '');
  const token = env('WILSY_PROMETHEUS_BEARER_TOKEN');

  if (!baseUrl || !query) return null;

  const url = new URL(`${baseUrl}/api/v1/query`);
  url.searchParams.set('query', query);

  return fetchJson(url, {
    headers: {
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
  });
}

/**
 * @function parsePrometheusScalar
 * @description Parses the first scalar/vector value from a Prometheus response.
 * @param {object} response - Prometheus response.
 * @returns {number|null} Numeric value.
 */
function parsePrometheusScalar(response = {}) {
  if (response.__connectorStatus) return null;

  const result = response.data?.result || [];

  if (!Array.isArray(result) || !result.length) return null;

  const value = result[0]?.value?.[1] || result[0]?.values?.at?.(-1)?.[1];
  const parsed = Number(value);

  return Number.isFinite(parsed) ? parsed : null;
}

/**
 * @function prometheusUptimeEvidence
 * @description Builds uptime evidence from a configured Prometheus query.
 * @param {object} context - Source context.
 * @returns {Promise<object|null>} Uptime evidence.
 */
async function prometheusUptimeEvidence(context = {}) {
  const hints = artifactHints(context);
  const query =
    env('WILSY_PROMETHEUS_UPTIME_QUERY') ||
    (hints.serviceName
      ? `avg_over_time(up{job="${hints.serviceName}"}[30d]) * 100`
      : 'avg_over_time(up[30d]) * 100');

  const response = await prometheusQuery(query);

  if (!response) return null;

  if (response.__connectorStatus || response.status === 'error') {
    return {
      status: STATUS.ERROR,
      message: response.__message || response.error || 'Prometheus query failed.',
    };
  }

  const uptimePercent = parsePrometheusScalar(response);

  if (uptimePercent === null) {
    return {
      status: STATUS.PENDING,
      message: 'Prometheus responded, but uptime query returned no numeric result.',
    };
  }

  const evidence = {
    provider: 'Prometheus',
    query,
    uptimePercent,
    environment: hints.environment,
    serviceName: hints.serviceName || null,
    rawStatus: response.status,
  };

  const seal = hashEvidence(evidence);

  return {
    status: STATUS.VERIFIED,
    verified: true,
    sourceId: `prometheus:uptime:${hints.serviceName || 'global'}`,
    retrievedAt: nowIso(),
    evidence,
    evidenceHash: seal.hash,
    hashAlgorithm: seal.algorithm,
  };
}

/**
 * @function datadogQuery
 * @description Executes a Datadog metrics query.
 * @param {string} query - Datadog query.
 * @param {number} from - Unix seconds.
 * @param {number} to - Unix seconds.
 * @returns {Promise<object|null>} Datadog response.
 */
async function datadogQuery(query, from, to) {
  const apiKey = env('WILSY_DATADOG_API_KEY') || env('DATADOG_API_KEY');
  const appKey = env('WILSY_DATADOG_APP_KEY') || env('DATADOG_APP_KEY');
  const site = env('WILSY_DATADOG_SITE') || DEFAULT_DATADOG_SITE;

  if (!apiKey || !appKey || !query) return null;

  const url = new URL(`https://api.${site}/api/v1/query`);
  url.searchParams.set('from', String(from));
  url.searchParams.set('to', String(to));
  url.searchParams.set('query', query);

  return fetchJson(url, {
    headers: {
      'DD-API-KEY': apiKey,
      'DD-APPLICATION-KEY': appKey,
    },
  });
}

/**
 * @function datadogUptimeEvidence
 * @description Builds uptime evidence from a configured Datadog query.
 * @param {object} context - Source context.
 * @returns {Promise<object|null>} Uptime evidence.
 */
async function datadogUptimeEvidence(context = {}) {
  const hints = artifactHints(context);
  const query = env('WILSY_DATADOG_UPTIME_QUERY');

  if (!query) return null;

  const to = Math.floor(Date.now() / 1000);
  const from = to - 30 * 24 * 60 * 60;
  const response = await datadogQuery(query, from, to);

  if (!response) return null;

  if (response.__connectorStatus) {
    return {
      status: response.__connectorStatus,
      message: response.__message,
    };
  }

  const series = response.series || [];
  const points = series.flatMap((item) => item.pointlist || item.points || []);
  const values = points.map((point) => Number(point[1])).filter((value) => Number.isFinite(value));

  if (!values.length) {
    return {
      status: STATUS.PENDING,
      message: 'Datadog responded, but uptime query returned no numeric datapoints.',
    };
  }

  const average = values.reduce((sum, value) => sum + value, 0) / values.length;
  const evidence = {
    provider: 'Datadog',
    query,
    average,
    from,
    to,
    datapoints: values.length,
    environment: hints.environment,
    serviceName: hints.serviceName || null,
  };

  const seal = hashEvidence(evidence);

  return {
    status: STATUS.VERIFIED,
    verified: true,
    sourceId: `datadog:uptime:${hints.serviceName || 'global'}:${to}`,
    retrievedAt: nowIso(),
    evidence,
    evidenceHash: seal.hash,
    hashAlgorithm: seal.algorithm,
  };
}

/**
 * @function pagerDutyIncidents
 * @description Fetches PagerDuty incidents.
 * @param {object} context - Source context.
 * @returns {Promise<object|null>} PagerDuty incident payload.
 */
async function pagerDutyIncidents(context = {}) {
  const token = env('WILSY_PAGERDUTY_API_TOKEN') || env('PAGERDUTY_API_TOKEN');

  if (!token) return null;

  const hints = artifactHints(context);
  const url = new URL('https://api.pagerduty.com/incidents');

  url.searchParams.set('limit', env('WILSY_PAGERDUTY_LIMIT') || '100');
  url.searchParams.set('statuses[]', 'triggered');
  url.searchParams.append('statuses[]', 'acknowledged');
  url.searchParams.append('statuses[]', 'resolved');

  const since =
    env('WILSY_INCIDENTS_SINCE') || new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString();
  const until = env('WILSY_INCIDENTS_UNTIL') || nowIso();

  url.searchParams.set('since', since);
  url.searchParams.set('until', until);

  const serviceIds = (env('WILSY_PAGERDUTY_SERVICE_IDS') || hints.incidentServiceId)
    .split(',')
    .map((item) => item.trim())
    .filter(Boolean);

  serviceIds.forEach((serviceId) => url.searchParams.append('service_ids[]', serviceId));

  return fetchJson(url, {
    headers: {
      Authorization: `Token token=${token}`,
      Accept: 'application/vnd.pagerduty+json;version=2',
    },
  });
}

/**
 * @function pagerDutyIncidentEvidence
 * @description Builds incident-log evidence from PagerDuty.
 * @param {object} context - Source context.
 * @returns {Promise<object|null>} Incident evidence.
 */
async function pagerDutyIncidentEvidence(context = {}) {
  const response = await pagerDutyIncidents(context);

  if (!response) return null;

  if (response.__connectorStatus) {
    return {
      status: response.__connectorStatus,
      message: response.__message,
    };
  }

  const incidents = response.incidents || [];

  const evidence = {
    provider: 'PagerDuty',
    incidentCount: incidents.length,
    incidents,
    retrievedWindow: {
      since: env('WILSY_INCIDENTS_SINCE') || null,
      until: env('WILSY_INCIDENTS_UNTIL') || null,
    },
  };

  const seal = hashEvidence(evidence);

  return {
    status: STATUS.VERIFIED,
    verified: true,
    sourceId: `pagerduty:incidents:${incidents.length}:${Date.now()}`,
    retrievedAt: nowIso(),
    evidence,
    evidenceHash: seal.hash,
    hashAlgorithm: seal.algorithm,
  };
}

/**
 * @function sentryIssues
 * @description Fetches Sentry organization issues.
 * @param {object} context - Source context.
 * @returns {Promise<object|null>} Sentry issues.
 */
async function sentryIssues(context = {}) {
  const token = env('WILSY_SENTRY_AUTH_TOKEN') || env('SENTRY_AUTH_TOKEN');
  const org = env('WILSY_SENTRY_ORG') || env('SENTRY_ORG');
  const baseUrl = (env('WILSY_SENTRY_BASE_URL') || DEFAULT_SENTRY_BASE_URL).replace(/\/$/, '');

  if (!token || !org) return null;

  const project = env('WILSY_SENTRY_PROJECT') || env('SENTRY_PROJECT');
  const url = project
    ? new URL(
        `${baseUrl}/api/0/projects/${encodeURIComponent(org)}/${encodeURIComponent(project)}/issues/`
      )
    : new URL(`${baseUrl}/api/0/organizations/${encodeURIComponent(org)}/issues/`);

  url.searchParams.set('query', env('WILSY_SENTRY_QUERY') || 'is:unresolved');
  url.searchParams.set('limit', env('WILSY_SENTRY_LIMIT') || '100');

  return fetchJson(url, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
}

/**
 * @function sentryIncidentEvidence
 * @description Builds issue/incident evidence from Sentry.
 * @param {object} context - Source context.
 * @returns {Promise<object|null>} Sentry evidence.
 */
async function sentryIncidentEvidence(context = {}) {
  const response = await sentryIssues(context);

  if (!response) return null;

  if (response.__connectorStatus) {
    return {
      status: response.__connectorStatus,
      message: response.__message,
    };
  }

  const issues = Array.isArray(response) ? response : response.results || response.issues || [];

  const evidence = {
    provider: 'Sentry',
    query: env('WILSY_SENTRY_QUERY') || 'is:unresolved',
    issueCount: issues.length,
    issues: issues.slice(0, 100),
  };

  const seal = hashEvidence(evidence);

  return {
    status: STATUS.VERIFIED,
    verified: true,
    sourceId: `sentry:issues:${issues.length}:${Date.now()}`,
    retrievedAt: nowIso(),
    evidence,
    evidenceHash: seal.hash,
    hashAlgorithm: seal.algorithm,
  };
}

/**
 * @function githubFetch
 * @description Fetches from GitHub REST API.
 * @param {string} path - API path.
 * @param {object} query - Query params.
 * @returns {Promise<object|Array|null>} API response.
 */
async function githubFetch(path, query = {}) {
  const token = env('WILSY_GITHUB_TOKEN') || env('GITHUB_TOKEN');

  if (!token) return null;

  const baseUrl = (env('WILSY_GITHUB_BASE_URL') || DEFAULT_GITHUB_BASE_URL).replace(/\/$/, '');
  const url = new URL(`${baseUrl}${path}`);

  Object.entries(query).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      url.searchParams.set(key, String(value));
    }
  });

  return fetchJson(url, {
    headers: {
      Authorization: `Bearer ${token}`,
      'X-GitHub-Api-Version': '2022-11-28',
      'User-Agent': 'Wilsy-OS-Source-Registry',
    },
  });
}

/**
 * @function githubChangeEvidence
 * @description Builds change-control evidence from GitHub deployments and pull requests.
 * @param {object} context - Source context.
 * @returns {Promise<object|null>} Change-control evidence.
 */
async function githubChangeEvidence(context = {}) {
  const hints = artifactHints(context);
  const owner = env('WILSY_GITHUB_OWNER') || hints.owner;
  const repo = env('WILSY_GITHUB_REPO') || hints.repository;

  if (!owner || !repo || !(env('WILSY_GITHUB_TOKEN') || env('GITHUB_TOKEN'))) return null;

  const encodedOwner = encodeURIComponent(owner);
  const encodedRepo = encodeURIComponent(repo);

  const deployments = await githubFetch(`/repos/${encodedOwner}/${encodedRepo}/deployments`, {
    per_page: env('WILSY_GITHUB_DEPLOYMENT_LIMIT') || '30',
    environment: hints.environment || undefined,
  });

  const pulls = await githubFetch(`/repos/${encodedOwner}/${encodedRepo}/pulls`, {
    state: 'all',
    sort: 'updated',
    direction: 'desc',
    per_page: env('WILSY_GITHUB_PULL_LIMIT') || '30',
  });

  if (deployments?.__connectorStatus) return deployments;
  if (pulls?.__connectorStatus) return pulls;

  const evidence = {
    provider: 'GitHub',
    owner,
    repo,
    environment: hints.environment,
    deployments: Array.isArray(deployments) ? deployments : [],
    pullRequests: Array.isArray(pulls) ? pulls : [],
  };

  const seal = hashEvidence(evidence);

  return {
    status: STATUS.VERIFIED,
    verified: true,
    sourceId: `github:${owner}/${repo}:${Date.now()}`,
    retrievedAt: nowIso(),
    evidence,
    evidenceHash: seal.hash,
    hashAlgorithm: seal.algorithm,
  };
}

/**
 * @function gitlabMergeRequests
 * @description Fetches GitLab merge requests.
 * @returns {Promise<object|Array|null>} GitLab merge requests.
 */
async function gitlabMergeRequests() {
  const token = env('WILSY_GITLAB_TOKEN') || env('GITLAB_TOKEN');
  const projectId = env('WILSY_GITLAB_PROJECT_ID') || env('GITLAB_PROJECT_ID');

  if (!token || !projectId) return null;

  const baseUrl = (env('WILSY_GITLAB_BASE_URL') || DEFAULT_GITLAB_BASE_URL).replace(/\/$/, '');
  const url = new URL(`${baseUrl}/projects/${encodeURIComponent(projectId)}/merge_requests`);

  url.searchParams.set('state', env('WILSY_GITLAB_MR_STATE') || 'all');
  url.searchParams.set('order_by', 'updated_at');
  url.searchParams.set('sort', 'desc');
  url.searchParams.set('per_page', env('WILSY_GITLAB_MR_LIMIT') || '30');

  return fetchJson(url, {
    headers: {
      'PRIVATE-TOKEN': token,
    },
  });
}

/**
 * @function gitlabChangeEvidence
 * @description Builds change-control evidence from GitLab merge requests.
 * @param {object} context - Source context.
 * @returns {Promise<object|null>} Change-control evidence.
 */
async function gitlabChangeEvidence(context = {}) {
  const response = await gitlabMergeRequests();

  if (!response) return null;

  if (response.__connectorStatus) {
    return {
      status: response.__connectorStatus,
      message: response.__message,
    };
  }

  const mergeRequests = Array.isArray(response) ? response : response.merge_requests || [];

  const evidence = {
    provider: 'GitLab',
    projectId: env('WILSY_GITLAB_PROJECT_ID') || env('GITLAB_PROJECT_ID'),
    mergeRequests: mergeRequests.slice(0, 100),
    environment: artifactHints(context).environment,
  };

  const seal = hashEvidence(evidence);

  return {
    status: STATUS.VERIFIED,
    verified: true,
    sourceId: `gitlab:${evidence.projectId}:${Date.now()}`,
    retrievedAt: nowIso(),
    evidence,
    evidenceHash: seal.hash,
    hashAlgorithm: seal.algorithm,
  };
}

/**
 * @function firstMeaningfulResult
 * @description Returns VERIFIED if any provider verified; otherwise the most useful non-null status.
 * @param {Array<object|null>} results - Candidate results.
 * @param {string} evidenceType - Evidence type.
 * @returns {object} Rolled result.
 */
function firstMeaningfulResult(results = [], evidenceType) {
  const usable = results.filter(Boolean);

  if (!usable.length) {
    return {
      status: STATUS.MISSING,
      evidenceType,
      message:
        'No telemetry source configured. Configure WILSY_TELEMETRY_EVIDENCE_FILE, WILSY_TELEMETRY_API_URL, Prometheus, Datadog, PagerDuty, Sentry, GitHub, or GitLab credentials.',
    };
  }

  const verified = usable.find((item) => item.status === STATUS.VERIFIED);
  if (verified) return verified;

  const error = usable.find((item) => item.status === STATUS.ERROR);
  if (error) return error;

  const missing = usable.find((item) => item.status === STATUS.MISSING);
  if (missing) return missing;

  return usable[0];
}

/**
 * @function getUptime
 * @description Returns verified uptime/SLO evidence from telemetry sources.
 * @param {object} context - Source registry context.
 * @returns {Promise<object>} Uptime evidence.
 */
export async function getUptime(context = {}) {
  try {
    const local = await evidenceFromLocalOrGenericStore(TELEMETRY_EVIDENCE_TYPES.UPTIME, context);
    const prometheus = await prometheusUptimeEvidence(context);
    const datadog = await datadogUptimeEvidence(context);

    return firstMeaningfulResult([local, prometheus, datadog], TELEMETRY_EVIDENCE_TYPES.UPTIME);
  } catch (error) {
    return {
      status: STATUS.ERROR,
      evidenceType: TELEMETRY_EVIDENCE_TYPES.UPTIME,
      message: error.message,
    };
  }
}

/**
 * @function getIncidentLog
 * @description Returns verified incident log evidence from incident/observability systems.
 * @param {object} context - Source registry context.
 * @returns {Promise<object>} Incident evidence.
 */
export async function getIncidentLog(context = {}) {
  try {
    const local = await evidenceFromLocalOrGenericStore(
      TELEMETRY_EVIDENCE_TYPES.INCIDENT_LOG,
      context
    );
    const pagerDuty = await pagerDutyIncidentEvidence(context);
    const sentry = await sentryIncidentEvidence(context);

    return firstMeaningfulResult([local, pagerDuty, sentry], TELEMETRY_EVIDENCE_TYPES.INCIDENT_LOG);
  } catch (error) {
    return {
      status: STATUS.ERROR,
      evidenceType: TELEMETRY_EVIDENCE_TYPES.INCIDENT_LOG,
      message: error.message,
    };
  }
}

/**
 * @function getChangeControlLog
 * @description Returns verified deployment/change-control evidence.
 * @param {object} context - Source registry context.
 * @returns {Promise<object>} Change-control evidence.
 */
export async function getChangeControlLog(context = {}) {
  try {
    const local = await evidenceFromLocalOrGenericStore(
      TELEMETRY_EVIDENCE_TYPES.CHANGE_CONTROL_LOG,
      context
    );
    const github = await githubChangeEvidence(context);
    const gitlab = await gitlabChangeEvidence(context);

    return firstMeaningfulResult(
      [local, github, gitlab],
      TELEMETRY_EVIDENCE_TYPES.CHANGE_CONTROL_LOG
    );
  } catch (error) {
    return {
      status: STATUS.ERROR,
      evidenceType: TELEMETRY_EVIDENCE_TYPES.CHANGE_CONTROL_LOG,
      message: error.message,
    };
  }
}

export default Object.freeze({
  getUptime,
  getIncidentLog,
  getChangeControlLog,
});
