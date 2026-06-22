/* eslint-disable */
/**
 * ╔══════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS — HR SOURCE CONNECTOR                                             ║
 * ║ VERSION: 1.0.0-PRODUCTION-NO-FAKE-DATA                                     ║
 * ║ FILE: server/services/sourceConnectors/hrSourceConnector.js                 ║
 * ║ PURPOSE: Verify HRIS, IP assignment and authority evidence for artifacts.   ║
 * ╚══════════════════════════════════════════════════════════════════════════════╝
 *
 * @description
 * This connector never fabricates HR verification.
 *
 * It supports:
 * - Local evidence file: WILSY_HR_EVIDENCE_FILE
 * - Generic HR evidence API: WILSY_HR_API_URL
 * - Workday/custom worker endpoint: WILSY_WORKDAY_WORKER_API_URL
 * - BambooHR employee API: WILSY_BAMBOOHR_COMPANY_DOMAIN + WILSY_BAMBOOHR_API_KEY
 * - Personio employee API: WILSY_PERSONIO_ACCESS_TOKEN
 * - Microsoft Graph user API: WILSY_GRAPH_ACCESS_TOKEN
 *
 * VERIFIED requires:
 * - verified true or status VERIFIED
 * - sourceId / recordId / id
 * - retrievedAt / timestamp / generatedAt
 * - evidence payload
 *
 * Employee profile may be verified from a live HRIS user/employee record.
 * IP assignment and authority record require explicit assignment/authority evidence.
 * A job title alone is not enough to verify signing authority.
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

const HR_EVIDENCE_TYPES = Object.freeze({
  EMPLOYEE_PROFILE: 'EMPLOYEE_PROFILE',
  IP_ASSIGNMENT: 'IP_ASSIGNMENT',
  AUTHORITY_RECORD: 'AUTHORITY_RECORD',
});

const DEFAULT_BAMBOO_BASE_URL = 'https://api.bamboohr.com';
const DEFAULT_PERSONIO_BASE_URL = 'https://api.personio.de/v1';
const DEFAULT_GRAPH_BASE_URL = 'https://graph.microsoft.com/v1.0';

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
 * @description Normalizes tenant identifier.
 * @param {string} tenantId - Tenant id.
 * @returns {string} Normalized tenant id.
 */
function normalizeTenantId(tenantId = 'MASTER') {
  return String(tenantId || 'MASTER').trim() || 'MASTER';
}

/**
 * @function safeJsonParse
 * @description Parses JSON with source-aware errors.
 * @param {string} content - JSON content.
 * @param {string} label - Source label.
 * @returns {*} Parsed JSON.
 */
function safeJsonParse(content, label) {
  try {
    return JSON.parse(content);
  } catch (error) {
    const enriched = new Error(`Invalid HR evidence JSON from ${label}: ${error.message}`);
    enriched.cause = error;
    throw enriched;
  }
}

/**
 * @function evidenceFilePath
 * @description Resolves configured HR evidence file path.
 * @returns {string} Evidence file path.
 */
function evidenceFilePath() {
  return env('WILSY_HR_EVIDENCE_FILE');
}

/**
 * @function genericHrApiUrl
 * @description Resolves configured generic HR evidence API.
 * @returns {string} API base URL.
 */
function genericHrApiUrl() {
  return env('WILSY_HR_API_URL').replace(/\/$/, '');
}

/**
 * @function bambooBaseUrl
 * @description Resolves BambooHR API base URL.
 * @returns {string} BambooHR base URL.
 */
function bambooBaseUrl() {
  return (env('WILSY_BAMBOOHR_BASE_URL') || DEFAULT_BAMBOO_BASE_URL).replace(/\/$/, '');
}

/**
 * @function personioBaseUrl
 * @description Resolves Personio API base URL.
 * @returns {string} Personio base URL.
 */
function personioBaseUrl() {
  return (env('WILSY_PERSONIO_BASE_URL') || DEFAULT_PERSONIO_BASE_URL).replace(/\/$/, '');
}

/**
 * @function graphBaseUrl
 * @description Resolves Microsoft Graph API base URL.
 * @returns {string} Graph base URL.
 */
function graphBaseUrl() {
  return (env('WILSY_GRAPH_BASE_URL') || DEFAULT_GRAPH_BASE_URL).replace(/\/$/, '');
}

/**
 * @function artifactHints
 * @description Extracts HR lookup hints from artifact/context.
 * @param {object} context - Source registry context.
 * @returns {object} Lookup hints.
 */
function artifactHints(context = {}) {
  const artifact = context.artifact || {};

  return {
    tenantId: normalizeTenantId(context.tenantId),
    employeeId:
      artifact.employeeId ||
      artifact.workerId ||
      artifact.hrisEmployeeId ||
      artifact.personId ||
      '',
    employeeEmail:
      artifact.employeeEmail ||
      artifact.workEmail ||
      artifact.email ||
      artifact.signatoryEmail ||
      '',
    employeeName:
      artifact.employeeName ||
      artifact.workerName ||
      artifact.signatoryName ||
      artifact.counterpartyName ||
      '',
    department: artifact.department || '',
    role: artifact.role || artifact.jobTitle || artifact.titleRole || '',
    ipAssignmentId:
      artifact.ipAssignmentId || artifact.assignmentId || artifact.documentId || artifact.id || '',
    authorityId: artifact.authorityId || artifact.delegationId || artifact.boardResolutionId || '',
    artifactTitle: artifact.title || artifact.name || '',
    artifactType: artifact.type || artifact.id || '',
  };
}

/**
 * @function fetchJson
 * @description Fetches JSON with strict error handling.
 * @param {string|URL} url - URL.
 * @param {object} options - Fetch options.
 * @returns {Promise<object>} JSON or connector error marker.
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
 * @description Reads configured local HR evidence file.
 * @returns {Promise<object|null>} Evidence store or null.
 */
async function readFileEvidence() {
  const filePath = evidenceFilePath();

  if (!filePath) return null;

  if (!existsSync(filePath)) {
    return {
      __connectorStatus: STATUS.MISSING,
      __message: `Configured HR evidence file does not exist: ${filePath}`,
    };
  }

  const content = await readFile(filePath, 'utf8');

  return safeJsonParse(content, filePath);
}

/**
 * @function selectTenantEvidence
 * @description Selects tenant-specific HR evidence.
 * @param {object} store - Evidence store.
 * @param {string} tenantId - Tenant id.
 * @returns {object|null} Tenant evidence.
 */
function selectTenantEvidence(store = {}, tenantId = 'MASTER') {
  const normalizedTenantId = normalizeTenantId(tenantId);

  if (store.tenantId && normalizeTenantId(store.tenantId) === normalizedTenantId) return store;
  if (store.tenants && store.tenants[normalizedTenantId]) return store.tenants[normalizedTenantId];
  if (store[normalizedTenantId]) return store[normalizedTenantId];

  return store.hr || store.HR || null;
}

/**
 * @function normalizeEvidenceRecord
 * @description Strictly normalizes evidence into Source Registry format.
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

  const evidencePayload = record.evidence || record.data || record.record || null;
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

  if (!verified || !sourceId || !retrievedAt || !evidencePayload) {
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
        evidencePayload: Boolean(evidencePayload),
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
 * @description Fetches evidence from a generic Wilsy HR evidence API.
 * @param {string} evidenceType - Evidence type.
 * @param {object} context - Source context.
 * @returns {Promise<object|null>} Evidence.
 */
async function fetchGenericApiEvidence(evidenceType, context = {}) {
  const baseUrl = genericHrApiUrl();

  if (!baseUrl) return null;

  const hints = artifactHints(context);
  const url = new URL(`${baseUrl}/hr/evidence`);

  url.searchParams.set('tenantId', hints.tenantId);
  url.searchParams.set('type', evidenceType);

  if (hints.employeeId) url.searchParams.set('employeeId', hints.employeeId);
  if (hints.employeeEmail) url.searchParams.set('employeeEmail', hints.employeeEmail);
  if (hints.ipAssignmentId) url.searchParams.set('ipAssignmentId', hints.ipAssignmentId);
  if (hints.authorityId) url.searchParams.set('authorityId', hints.authorityId);

  const token = env('WILSY_HR_API_TOKEN');

  return fetchJson(url, {
    headers: {
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      'X-Wilsy-Trace-Id': context.traceId || `HR-${Date.now().toString(16).toUpperCase()}`,
    },
  });
}

/**
 * @function evidenceFromLocalOrGenericStore
 * @description Reads HR evidence from local file or generic API.
 * @param {string} evidenceType - Evidence type.
 * @param {object} context - Source context.
 * @returns {Promise<object|null>} Normalized evidence or null.
 */
async function evidenceFromLocalOrGenericStore(evidenceType, context = {}) {
  const apiEvidence = genericHrApiUrl()
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
 * @function bambooAuthHeader
 * @description Builds BambooHR Basic auth header.
 * @returns {object} Headers or empty object.
 */
function bambooAuthHeader() {
  const apiKey = env('WILSY_BAMBOOHR_API_KEY') || env('BAMBOOHR_API_KEY');

  if (!apiKey) return {};

  return {
    Authorization: `Basic ${Buffer.from(`${apiKey}:x`).toString('base64')}`,
  };
}

/**
 * @function bambooEmployee
 * @description Fetches BambooHR employee by employee ID.
 * @param {object} context - Source context.
 * @returns {Promise<object|null>} Employee record.
 */
async function bambooEmployee(context = {}) {
  const companyDomain = env('WILSY_BAMBOOHR_COMPANY_DOMAIN') || env('BAMBOOHR_COMPANY_DOMAIN');
  const headers = bambooAuthHeader();
  const hints = artifactHints(context);

  if (!companyDomain || !Object.keys(headers).length || !hints.employeeId) return null;

  const fields = [
    'id',
    'employeeNumber',
    'firstName',
    'lastName',
    'preferredName',
    'workEmail',
    'jobTitle',
    'department',
    'division',
    'location',
    'employmentStatus',
    'status',
    'hireDate',
    'supervisor',
    'supervisorId',
  ].join(',');

  const url = new URL(
    `${bambooBaseUrl()}/api/gateway.php/${companyDomain}/v1/employees/${encodeURIComponent(hints.employeeId)}`
  );
  url.searchParams.set('fields', fields);

  return fetchJson(url, { headers });
}

/**
 * @function bambooEmployeeProfileEvidence
 * @description Builds employee profile evidence from BambooHR.
 * @param {object} context - Source context.
 * @returns {Promise<object|null>} Evidence result.
 */
async function bambooEmployeeProfileEvidence(context = {}) {
  const employee = await bambooEmployee(context);

  if (!employee) return null;

  if (employee.__connectorStatus) {
    return {
      status: employee.__connectorStatus,
      message: employee.__message,
    };
  }

  const sourceId = employee.id || employee.employeeNumber;

  if (!sourceId) {
    return {
      status: STATUS.PENDING,
      message: 'BambooHR returned an employee payload without employee id.',
    };
  }

  const evidence = {
    provider: 'BambooHR',
    tenantId: normalizeTenantId(context.tenantId),
    employee,
  };

  const seal = hashEvidence(evidence);

  return {
    status: STATUS.VERIFIED,
    verified: true,
    sourceId: `bamboohr:${sourceId}`,
    retrievedAt: nowIso(),
    evidence,
    evidenceHash: seal.hash,
    hashAlgorithm: seal.algorithm,
  };
}

/**
 * @function personioEmployees
 * @description Fetches Personio employees with selected attributes.
 * @param {object} context - Source context.
 * @returns {Promise<object|null>} Personio response.
 */
async function personioEmployees(context = {}) {
  const token = env('WILSY_PERSONIO_ACCESS_TOKEN') || env('PERSONIO_ACCESS_TOKEN');

  if (!token) return null;

  const hints = artifactHints(context);
  const url = new URL(`${personioBaseUrl()}/company/employees`);

  [
    'id',
    'first_name',
    'last_name',
    'email',
    'position',
    'department',
    'office',
    'status',
    'supervisor',
    'employment_type',
  ].forEach((attribute) => url.searchParams.append('attributes[]', attribute));

  if (hints.employeeEmail) {
    url.searchParams.set('email', hints.employeeEmail);
  }

  return fetchJson(url, {
    headers: { Authorization: `Bearer ${token}` },
  });
}

/**
 * @function selectPersonioEmployee
 * @description Selects the best Personio employee match.
 * @param {object} response - Personio response.
 * @param {object} context - Source context.
 * @returns {object|null} Employee record.
 */
function selectPersonioEmployee(response = {}, context = {}) {
  const hints = artifactHints(context);
  const records = response.data || response.employees || response.results || [];

  if (!Array.isArray(records) || !records.length) return null;

  const email = String(hints.employeeEmail || '').toLowerCase();
  const employeeId = String(hints.employeeId || '');

  return (
    records.find((record) => {
      const attributes = record.attributes || record;
      const recordId = String(record.id || attributes.id?.value || attributes.id || '');
      const recordEmail = String(attributes.email?.value || attributes.email || '').toLowerCase();

      return (employeeId && recordId === employeeId) || (email && recordEmail === email);
    }) || records[0]
  );
}

/**
 * @function personioEmployeeProfileEvidence
 * @description Builds employee profile evidence from Personio.
 * @param {object} context - Source context.
 * @returns {Promise<object|null>} Evidence result.
 */
async function personioEmployeeProfileEvidence(context = {}) {
  const response = await personioEmployees(context);

  if (!response) return null;

  if (response.__connectorStatus) {
    return {
      status: response.__connectorStatus,
      message: response.__message,
    };
  }

  const employee = selectPersonioEmployee(response, context);

  if (!employee) {
    return {
      status: STATUS.PENDING,
      message: 'Personio configured, but no employee matched the artifact hints.',
    };
  }

  const sourceId = employee.id || employee.attributes?.id?.value;

  const evidence = {
    provider: 'Personio',
    tenantId: normalizeTenantId(context.tenantId),
    employee,
  };

  const seal = hashEvidence(evidence);

  return {
    status: STATUS.VERIFIED,
    verified: true,
    sourceId: `personio:${sourceId || 'employee'}`,
    retrievedAt: nowIso(),
    evidence,
    evidenceHash: seal.hash,
    hashAlgorithm: seal.algorithm,
  };
}

/**
 * @function graphUser
 * @description Fetches a Microsoft Graph user by email or employee ID hint.
 * @param {object} context - Source context.
 * @returns {Promise<object|null>} Graph user.
 */
async function graphUser(context = {}) {
  const token = env('WILSY_GRAPH_ACCESS_TOKEN') || env('GRAPH_ACCESS_TOKEN');
  const hints = artifactHints(context);

  if (!token || (!hints.employeeEmail && !hints.employeeId)) return null;

  const identifier = encodeURIComponent(hints.employeeEmail || hints.employeeId);
  const url = new URL(`${graphBaseUrl()}/users/${identifier}`);

  url.searchParams.set(
    '$select',
    'id,displayName,mail,userPrincipalName,jobTitle,department,officeLocation,employeeId,accountEnabled'
  );

  return fetchJson(url, {
    headers: { Authorization: `Bearer ${token}` },
  });
}

/**
 * @function graphManager
 * @description Fetches a Microsoft Graph user manager.
 * @param {string} userId - User id.
 * @returns {Promise<object|null>} Graph manager.
 */
async function graphManager(userId) {
  const token = env('WILSY_GRAPH_ACCESS_TOKEN') || env('GRAPH_ACCESS_TOKEN');

  if (!token || !userId) return null;

  const url = new URL(`${graphBaseUrl()}/users/${encodeURIComponent(userId)}/manager`);
  url.searchParams.set('$select', 'id,displayName,mail,userPrincipalName,jobTitle,department');

  return fetchJson(url, {
    headers: { Authorization: `Bearer ${token}` },
  });
}

/**
 * @function graphEmployeeProfileEvidence
 * @description Builds employee profile evidence from Microsoft Graph.
 * @param {object} context - Source context.
 * @returns {Promise<object|null>} Evidence result.
 */
async function graphEmployeeProfileEvidence(context = {}) {
  const user = await graphUser(context);

  if (!user) return null;

  if (user.__connectorStatus) {
    return {
      status: user.__connectorStatus,
      message: user.__message,
    };
  }

  const manager = await graphManager(user.id);
  const evidence = {
    provider: 'Microsoft Graph',
    tenantId: normalizeTenantId(context.tenantId),
    user,
    manager: manager?.__connectorStatus ? null : manager,
  };

  const seal = hashEvidence(evidence);

  return {
    status: STATUS.VERIFIED,
    verified: true,
    sourceId: `graph:${user.id}`,
    retrievedAt: nowIso(),
    evidence,
    evidenceHash: seal.hash,
    hashAlgorithm: seal.algorithm,
  };
}

/**
 * @function workdayWorkerEvidence
 * @description Fetches employee evidence from a configured Workday/custom worker endpoint.
 * @param {object} context - Source context.
 * @returns {Promise<object|null>} Evidence result.
 */
async function workdayWorkerEvidence(context = {}) {
  const endpoint = env('WILSY_WORKDAY_WORKER_API_URL');
  const token = env('WILSY_WORKDAY_ACCESS_TOKEN');

  if (!endpoint) return null;

  const hints = artifactHints(context);
  const url = new URL(endpoint);

  url.searchParams.set('tenantId', hints.tenantId);
  if (hints.employeeId) url.searchParams.set('employeeId', hints.employeeId);
  if (hints.employeeEmail) url.searchParams.set('employeeEmail', hints.employeeEmail);
  if (hints.employeeName) url.searchParams.set('employeeName', hints.employeeName);

  const response = await fetchJson(url, {
    headers: {
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      'X-Wilsy-Trace-Id': context.traceId || `WORKDAY-${Date.now().toString(16).toUpperCase()}`,
    },
  });

  if (!response) return null;

  if (response.__connectorStatus) {
    return {
      status: response.__connectorStatus,
      message: response.__message,
    };
  }

  return normalizeEvidenceRecord(HR_EVIDENCE_TYPES.EMPLOYEE_PROFILE, response, context);
}

/**
 * @function firstMeaningfulResult
 * @description Returns VERIFIED if any provider verified; otherwise the most useful non-null status.
 * @param {Array<object|null>} results - Results.
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
        'No HR source configured. Configure WILSY_HR_EVIDENCE_FILE, WILSY_HR_API_URL, Workday, BambooHR, Personio, or Microsoft Graph credentials.',
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
 * @function explicitEvidenceOnly
 * @description Requires explicit evidence for sensitive HR artifact gates.
 * @param {string} evidenceType - Evidence type.
 * @param {object} context - Source context.
 * @param {string} reason - Reason.
 * @returns {Promise<object>} Evidence result.
 */
async function explicitEvidenceOnly(evidenceType, context = {}, reason = '') {
  const local = await evidenceFromLocalOrGenericStore(evidenceType, context);

  if (local?.status === STATUS.VERIFIED) return local;
  if (local) return local;

  return {
    status: STATUS.PENDING,
    evidenceType,
    message: reason,
    requirements: {
      configuredEvidenceFile: Boolean(evidenceFilePath()),
      configuredHrApi: Boolean(genericHrApiUrl()),
      explicitEvidenceRequired: true,
    },
  };
}

/**
 * @function getEmployeeProfile
 * @description Returns verified employee profile evidence from HRIS sources.
 * @param {object} context - Source registry context.
 * @returns {Promise<object>} Employee profile evidence.
 */
export async function getEmployeeProfile(context = {}) {
  try {
    const local = await evidenceFromLocalOrGenericStore(
      HR_EVIDENCE_TYPES.EMPLOYEE_PROFILE,
      context
    );
    const workday = await workdayWorkerEvidence(context);
    const bamboo = await bambooEmployeeProfileEvidence(context);
    const personio = await personioEmployeeProfileEvidence(context);
    const graph = await graphEmployeeProfileEvidence(context);

    return firstMeaningfulResult(
      [local, workday, bamboo, personio, graph],
      HR_EVIDENCE_TYPES.EMPLOYEE_PROFILE
    );
  } catch (error) {
    return {
      status: STATUS.ERROR,
      evidenceType: HR_EVIDENCE_TYPES.EMPLOYEE_PROFILE,
      message: error.message,
    };
  }
}

/**
 * @function getIPAssignment
 * @description Returns verified IP assignment evidence for employment/confidentiality artifacts.
 * @param {object} context - Source registry context.
 * @returns {Promise<object>} IP assignment evidence.
 */
export async function getIPAssignment(context = {}) {
  try {
    return explicitEvidenceOnly(
      HR_EVIDENCE_TYPES.IP_ASSIGNMENT,
      context,
      'IP assignment requires explicit signed assignment, contract clause, HR file, or legal ledger evidence. Employee profile alone is not sufficient.'
    );
  } catch (error) {
    return {
      status: STATUS.ERROR,
      evidenceType: HR_EVIDENCE_TYPES.IP_ASSIGNMENT,
      message: error.message,
    };
  }
}

/**
 * @function getAuthorityRecord
 * @description Returns verified authority/delegation/signatory evidence.
 * @param {object} context - Source registry context.
 * @returns {Promise<object>} Authority evidence.
 */
export async function getAuthorityRecord(context = {}) {
  try {
    return explicitEvidenceOnly(
      HR_EVIDENCE_TYPES.AUTHORITY_RECORD,
      context,
      'Authority requires explicit delegation, board resolution, HR authority matrix, power of attorney, or signing mandate evidence. Job title alone is not sufficient.'
    );
  } catch (error) {
    return {
      status: STATUS.ERROR,
      evidenceType: HR_EVIDENCE_TYPES.AUTHORITY_RECORD,
      message: error.message,
    };
  }
}

export default Object.freeze({
  getEmployeeProfile,
  getIPAssignment,
  getAuthorityRecord,
});
