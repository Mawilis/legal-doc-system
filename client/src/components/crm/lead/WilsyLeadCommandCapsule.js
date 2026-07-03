/* eslint-disable */
import { openWilsyLeadEditSurface } from './WilsyLeadEditSurface';
import { sha3_512 } from 'js-sha3';
import {
  WILSY_LEAD_STATUS_OPTIONS,
  normalizeWilsyLeadStatusValue,
  formatWilsyLeadStatusLabel,
} from '../../../data/wilsyLeadStatusOptions';
import {
  WILSY_DEFAULT_PHONE_COUNTRY,
  getWilsyPhoneCountryOptions,
  normalizeWilsyPhoneForClient,
  formatWilsyPhoneDisplay,
} from '../../../utils/wilsyPhoneGovernance';



/* R91K179E24P58D2 ADAPTIVE_MODULE_AWARE_GOVERNANCE_COPY */

/**
 * @function resolveWilsyR91K179E24P58D2TitleCase
 * @description Converts a module noun into display-safe title case.
 * @param {string} value - Raw module value.
 * @returns {string} Display-safe label.
 * @collaboration WilsyLeadCommandCapsule, shared CRM command governance, Meeting adapter.
 */
function resolveWilsyR91K179E24P58D2TitleCase(value = 'lead') {
  const normalized = String(value || 'lead').replace(/[_-]+/g, ' ').trim().toLowerCase();
  if (!normalized) return 'Lead';

  return normalized
    .split(/\s+/)
    .map(part => part ? `${part.charAt(0).toUpperCase()}${part.slice(1)}` : '')
    .join(' ')
    .trim() || 'Lead';
}

/**
 * @function resolveWilsyR91K179E24P58D2GovernanceCopy
 * @description Resolves protected command governance copy from module context without requiring old hardcoded Lead strings.
 * @param {Object} params - Capsule launch params.
 * @param {Object} record - Source record.
 * @returns {Object} Module-aware copy packet.
 * @collaboration WilsyLeadCommandCapsule, WilsyLeadOperatingRoom, WilsyMeetingOperatingRoom, protected delete governance.
 */
function resolveWilsyR91K179E24P58D2GovernanceCopy(params = {}, record = {}) {
  const operatingCopy = params.operatingCopy && typeof params.operatingCopy === 'object' ? params.operatingCopy : {};
  const providedCopy = params.governanceCopy && typeof params.governanceCopy === 'object' ? params.governanceCopy : {};
  const sourceSignal = String(
    providedCopy.module ||
    params.sourceModule ||
    params.recordModule ||
    params.module ||
    operatingCopy.recordPlural ||
    record.sourceModule ||
    record.source ||
    record.module ||
    ''
  ).toLowerCase();

  const isMeeting = sourceSignal.includes('meeting') ||
    String(record.sourceModule || '').toLowerCase().includes('meeting') ||
    String(record.source || '').toLowerCase().includes('meeting');

  const recordSingular = String(
    providedCopy.recordSingular ||
    params.recordSingular ||
    operatingCopy.recordSingular ||
    (isMeeting ? 'meeting' : 'lead')
  ).toLowerCase();

  const recordPlural = String(
    providedCopy.recordPlural ||
    params.recordPlural ||
    operatingCopy.recordPlural ||
    (isMeeting ? 'meetings' : 'leads')
  ).toLowerCase();

  const recordTitle = resolveWilsyR91K179E24P58D2TitleCase(recordSingular);
  const headers = operatingCopy.tableHeaders || {};

  return {
    module: recordPlural,
    recordSingular,
    recordPlural,
    recordTitle,
    sidebarTitle: providedCopy.sidebarTitle || `Sovereign ${recordTitle} Intelligence`,
    sidebarTitleUpper: String(providedCopy.sidebarTitle || `Sovereign ${recordTitle} Intelligence`).toUpperCase(),
    recordNameLabel: providedCopy.recordNameLabel || headers.name || (isMeeting ? 'Meeting' : 'Lead Name'),
    companyLabel: providedCopy.companyLabel || headers.company || (isMeeting ? 'CRM Link' : 'Company'),
    emailLabel: providedCopy.emailLabel || headers.email || (isMeeting ? 'Participants / Host' : 'Email'),
    phoneLabel: providedCopy.phoneLabel || headers.phone || (isMeeting ? 'Time' : 'Phone'),
    commandSurface: providedCopy.commandSurface || 'R91K179E24P58D2_MODULE_AWARE_DELETE_GOVERNANCE',
  };
}

/**
 * @function applyWilsyR91K179E24P58D2GovernanceCopy
 * @description Applies module-aware visible copy after the shared capsule renders.
 * @param {Document|HTMLElement} root - Root node.
 * @param {Object} copy - Module-aware copy packet.
 * @returns {void}
 * @collaboration WilsyLeadCommandCapsule, Meeting delete verification, Lead delete verification, DOM copy reconciliation.
 */
function applyWilsyR91K179E24P58D2GovernanceCopy(root = document, copy = {}) {
  if (!root || !copy || !copy.sidebarTitle) return;

  const replacements = [
    ['SOVEREIGN LEAD INTELLIGENCE', copy.sidebarTitleUpper],
    ['Sovereign Lead Intelligence', copy.sidebarTitle],
    ['Sovereign Lead', `Sovereign ${copy.recordTitle}`],
    ['Lead Intelligence', `${copy.recordTitle} Intelligence`],
    ['LEAD INTELLIGENCE', `${copy.recordTitle.toUpperCase()} INTELLIGENCE`],
    ['Lead Name', copy.recordNameLabel],
    ['LEAD NAME', String(copy.recordNameLabel || '').toUpperCase()],
    ['Company', copy.companyLabel],
    ['COMPANY', String(copy.companyLabel || '').toUpperCase()],
    ['Email', copy.emailLabel],
    ['EMAIL', String(copy.emailLabel || '').toUpperCase()],
    ['Phone', copy.phoneLabel],
    ['PHONE', String(copy.phoneLabel || '').toUpperCase()],
    ['operating memory of the Lead', `operating memory of the ${copy.recordTitle}`],
    ['operating memory of the lead', `operating memory of the ${copy.recordSingular}`],
    ['the Lead', `the ${copy.recordTitle}`],
  ];

  try {
    const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
    const nodes = [];

    while (walker.nextNode()) nodes.push(walker.currentNode);

    nodes.forEach((node) => {
      let value = node.nodeValue || '';
      replacements.forEach(([from, to]) => {
        value = value.split(from).join(to);
      });

      if (value !== node.nodeValue) {
        node.nodeValue = value;
      }
    });

    const elementRoot = root.querySelectorAll ? root : document;
    elementRoot.querySelectorAll('[aria-label], [title]').forEach((element) => {
      ['aria-label', 'title'].forEach((attribute) => {
        const original = element.getAttribute(attribute);
        if (!original) return;

        let value = original;
        replacements.forEach(([from, to]) => {
          value = value.split(from).join(to);
        });

        if (value !== original) {
          element.setAttribute(attribute, value);
        }
      });
    });
  } catch (error) {
    // Non-fatal. Command governance must not fail because copy reconciliation failed.
  }
}



/* R91K179E24P58H MEETING_DELETE_ROUTE_RECEIPT_RESOLVER */

/**
 * @function resolveWilsyR91K179E24P58HModuleSignal
 * @description Resolves the CRM module signal from command payload and source record evidence.
 * @param {Object} payload - Command payload or launch params.
 * @returns {string} Normalized module signal.
 * @collaboration WilsyLeadCommandCapsule, Meeting adapter, protected delete route authority.
 */
function resolveWilsyR91K179E24P58HModuleSignal(payload = {}) {
  const record = payload.record || payload.meeting || payload.lead || {};
  return String(
    payload.sourceModule ||
    payload.recordModule ||
    payload.module ||
    payload.recordPlural ||
    payload.governanceCopy?.module ||
    payload.operatingCopy?.recordPlural ||
    record.sourceModule ||
    record.source ||
    record.sourceSystem ||
    record.module ||
    record.metadata?.sourceModule ||
    ''
  ).toLowerCase();
}

/**
 * @function isWilsyR91K179E24P58HMeetingCommand
 * @description Determines whether a protected command is operating on the Meetings module.
 * @param {Object} payload - Command payload or launch params.
 * @returns {boolean} True when command belongs to Meetings.
 * @collaboration CRM Meeting delete route authority, Lead shell adapter, protected command receipt bridge.
 */
function isWilsyR91K179E24P58HMeetingCommand(payload = {}) {
  const signal = resolveWilsyR91K179E24P58HModuleSignal(payload);
  const record = payload.record || {};
  return signal.includes('meeting') ||
    String(record.sourceModule || '').toLowerCase().includes('meeting') ||
    String(record.source || '').toLowerCase().includes('meeting') ||
    String(record.sourceSystem || '').toLowerCase().includes('meeting');
}

/**
 * @function resolveWilsyR91K179E24P58HRecordId
 * @description Resolves source-backed CRM record id from command payload and Meeting source record variants.
 * @param {Object} payload - Command payload.
 * @returns {string} Record id.
 * @collaboration Meeting adapter, protected delete command, backend route id integrity.
 */
function resolveWilsyR91K179E24P58HRecordId(payload = {}) {
  const record = payload.record || {};
  const sourceRecord = record.wilsyMeetingSourceRecord || record.sourceRecord || {};
  return String(
    payload.recordId ||
    payload.id ||
    payload.meetingId ||
    record.sourceRecordId ||
    record.meetingId ||
    record.recordId ||
    record._id ||
    record.id ||
    sourceRecord.sourceRecordId ||
    sourceRecord.meetingId ||
    sourceRecord.recordId ||
    sourceRecord._id ||
    sourceRecord.id ||
    ''
  ).trim();
}

/**
 * @function resolveWilsyR91K179E24P58HProtectedDeleteRoute
 * @description Resolves the backend delete route for module-aware protected delete commands.
 * @param {Object} payload - Command payload.
 * @returns {string} Backend command route.
 * @collaboration /api/crm/command/meetings/:id, /api/crm/command/leads/:id, receipt bridge.
 */
function resolveWilsyR91K179E24P58HProtectedDeleteRoute(payload = {}) {
  const recordId = resolveWilsyR91K179E24P58HRecordId(payload);
  const encodedRecordId = encodeURIComponent(recordId || payload.recordId || 'record-id-unavailable');

  if (isWilsyR91K179E24P58HMeetingCommand(payload)) {
    return `/api/crm/command/meetings/${encodedRecordId}`;
  }

  return `/api/crm/command/leads/${encodedRecordId}`;
}

/**
 * @function resolveWilsyR91K179E24P58HReceiptHash
 * @description Resolves receipt hash from known backend response shapes without hiding missing receipt evidence.
 * @param {Object} payload - Backend response payload.
 * @returns {string} Receipt hash or empty string.
 * @collaboration Backend delete receipt, command capsule status rendering, auditMesh normalization.
 */
function resolveWilsyR91K179E24P58HReceiptHash(payload = {}) {
  return String(
    payload.receiptHash ||
    payload.hash ||
    payload.receipt?.receiptHash ||
    payload.receipt?.hash ||
    payload.receipt?.id ||
    payload.auditMesh?.receiptHash ||
    payload.auditMesh?.hash ||
    payload.auditMesh?.rootHash ||
    payload.commandReceipt?.receiptHash ||
    payload.commandReceipt?.hash ||
    payload.data?.receiptHash ||
    payload.data?.receipt?.receiptHash ||
    ''
  ).trim();
}

/**
 * @function buildWilsyLeadApiUrl
 * @description Builds a safe CRM command API URL from Vite runtime base, explicit apiBase, relative route, or absolute route without inventing backend authority.
 * @param {string|Object} first - API base string, route string, or options object.
 * @param {string} second - Optional route string.
 * @returns {string} Safe API URL.
 * @collaboration WilsyLeadCommandCapsule, protected delete governance, Meeting adapter, receipt-safe backend command routing.
 */
function buildWilsyLeadApiUrl(first = '', second = '') {
  const options = first && typeof first === 'object'
    ? first
    : {
        apiBase: first,
        route: second,
      };

  const rawApiBase = String(
    options.apiBase ||
    options.baseUrl ||
    options.baseURL ||
    options.base ||
    ''
  ).trim();

  const rawRoute = String(
    options.route ||
    options.path ||
    options.url ||
    options.endpoint ||
    second ||
    ''
  ).trim();

  const defaultRoute = '/api/crm/command/leads';
  const route = rawRoute || defaultRoute;

  if (/^https?:\/\//i.test(route)) {
    return route;
  }

  const normalizedRoute = route.startsWith('/') ? route : `/${route}`;

  let runtimeBase = '';
  try {
    runtimeBase = String(import.meta?.env?.VITE_API_URL || '').trim();
  } catch (error) {
    runtimeBase = '';
  }

  const base = String(rawApiBase || runtimeBase || '').replace(/\/$/, '');

  if (!base) {
    return normalizedRoute;
  }

  return `${base}${normalizedRoute}`;
}

/**
 * @function buildWilsyLeadNetworkFailurePayload
 * @description Builds a receipt-safe failure payload when protected CRM command probes, profile lookups, or backend command requests fail before backend authority can return a formal receipt.
 * @param {Object|string} context - Failure context, route, command, record, operator, tenant or message.
 * @returns {Object} Receipt-safe network failure payload.
 * @collaboration WilsyLeadCommandCapsule, Meeting lead-shell adapter, protected delete governance, institutional strike payload evidence.
 */
function buildWilsyLeadNetworkFailurePayload(context = {}) {
  const normalizedContext = context && typeof context === 'object' ? context : { message: String(context || '') };
  const error = normalizedContext.error || normalizedContext.networkError || normalizedContext.exception || {};
  const record = normalizedContext.record || normalizedContext.lead || normalizedContext.meeting || normalizedContext.sourceRecord || {};
  const institutionalHeadersSource =
    normalizedContext.institutionalHeaders ||
    normalizedContext.headers ||
    normalizedContext.strikePayload?.institutionalHeaders ||
    {};

  const generatedAt = new Date().toISOString();
  const route = String(
    normalizedContext.route ||
    normalizedContext.sourceRoute ||
    normalizedContext.endpoint ||
    normalizedContext.url ||
    normalizedContext.strikePayload?.route ||
    '/api/crm/command/protected'
  );

  const moduleName = String(
    normalizedContext.module ||
    normalizedContext.moduleName ||
    normalizedContext.recordModule ||
    normalizedContext.strikePayload?.module ||
    record.module ||
    record.sourceModule ||
    record.source ||
    'crm'
  );

  const recordId = String(
    normalizedContext.recordId ||
    normalizedContext.id ||
    normalizedContext.leadId ||
    normalizedContext.meetingId ||
    record._id ||
    record.id ||
    record.recordId ||
    record.leadId ||
    record.meetingId ||
    'record-id-unavailable'
  );

  const tenantId = String(
    normalizedContext.tenantId ||
    institutionalHeadersSource.tenantId ||
    normalizedContext.strikePayload?.tenantId ||
    record.tenantId ||
    record.tenant ||
    'wilsy-sovereign-root'
  );

  const operatorId = String(
    normalizedContext.operatorId ||
    normalizedContext.userId ||
    institutionalHeadersSource.operatorId ||
    institutionalHeadersSource.userId ||
    institutionalHeadersSource.actor ||
    normalizedContext.operator?.id ||
    normalizedContext.operator?.operatorId ||
    'wilsy-local-operator'
  );

  const operatorEmail = String(
    normalizedContext.operatorEmail ||
    institutionalHeadersSource.operatorEmail ||
    normalizedContext.operator?.email ||
    ''
  );

  const commandSurface = String(
    normalizedContext.commandSurface ||
    institutionalHeadersSource.commandSurface ||
    normalizedContext.strikePayload?.commandSurface ||
    'WILSY_PROTECTED_COMMAND_GOVERNANCE'
  );

  const message = String(
    normalizedContext.message ||
    error.message ||
    'Protected command could not complete because network, auth profile, or backend command authority returned an unavailable response.'
  );

  const institutionalHeaders = {
    ...institutionalHeadersSource,
    tenantId,
    operatorId,
    userId: operatorId,
    operatorEmail,
    route,
    commandSurface,
    generatedAt,
    module: moduleName,
    recordId,
    evidenceMode: 'NETWORK_FAILURE_RECEIPT',
  };

  const strikePayload = {
    ...(normalizedContext.strikePayload && typeof normalizedContext.strikePayload === 'object' ? normalizedContext.strikePayload : {}),
    tenantId,
    operatorId,
    userId: operatorId,
    route,
    commandSurface,
    generatedAt,
    module: moduleName,
    recordId,
    institutionalHeaders,
    error: {
      name: String(error.name || 'NetworkFailure'),
      message,
      status: normalizedContext.status || normalizedContext.statusCode || error.status || 'NETWORK_OR_AUTH_FAILURE',
    },
  };

  return {
    ok: false,
    status: 'PROTECTED_COMMAND_NETWORK_FAILURE',
    sourceStatus: 'RECEIPT_SAFE_FAILURE',
    message,
    route,
    tenantId,
    operatorId,
    userId: operatorId,
    operatorEmail,
    commandSurface,
    module: moduleName,
    recordId,
    generatedAt,
    institutionalHeaders,
    strikePayload,
    auditMesh: {
      tenantId,
      operatorId,
      route,
      commandSurface,
      generatedAt,
      recordId,
      module: moduleName,
      posture: 'failure-recorded-not-silent',
    },
    receipt: {
      status: 'NETWORK_FAILURE_RECEIPT',
      generatedAt,
      route,
      tenantId,
      operatorId,
      recordId,
      module: moduleName,
    },
  };
}


/**
 * @function shouldRouteWilsyLeadCommandCapsuleToEditSurface
 * @description Detects Lead Edit intent before the legacy command capsule shell is allowed to render.
 * @param {Object} payload - Lead command capsule payload.
 * @returns {boolean} Whether the payload must be routed to the real Lead Edit surface.
 * @collaboration R91K.24E command capsule gateway, Lead Operating Room callers, WilsyLeadEditSurface production form.
 */
function shouldRouteWilsyLeadCommandCapsuleToEditSurface(payload = {}) {
  const candidateValues = [
    payload?.mode,
    payload?.action,
    payload?.intent,
    payload?.type,
    payload?.command,
    payload?.operation,
    payload?.label,
    payload?.title,
    payload?.surface,
    payload?.panel,
    payload?.dataset?.leadAction,
    payload?.dataset?.action,
    payload?.dataset?.mode
  ]
    .map(value => String(value || '').trim().toLowerCase())
    .filter(Boolean);

  return candidateValues.some(value => (
    value === 'edit'
    || value === 'edit lead'
    || value === 'lead edit'
    || value === 'lead edit actionable data'
    || value.includes('edit lead')
    || value.includes('lead edit')
  ));
}

/**
 * @function buildWilsyLeadEditSurfacePayloadFromCapsule
 * @description Normalizes command capsule payloads into the real Lead Edit surface contract.
 * @param {Object} payload - Lead command capsule payload.
 * @returns {Object} Lead Edit surface payload.
 * @collaboration R91K.24E command capsule gateway, DB_PERSISTED Lead edit form, record identity resolver.
 */
function buildWilsyLeadEditSurfacePayloadFromCapsule(payload = {}) {
  const record = payload?.record
    || payload?.lead
    || payload?.data?.record
    || payload?.data?.lead
    || payload?.payload?.record
    || payload?.payload?.lead
    || {};

  const recordId = payload?.recordId
    || payload?.leadId
    || payload?.id
    || record?._id
    || record?.id
    || record?.leadId
    || record?.recordId
    || '';

  const recordIds = Array.isArray(payload?.recordIds)
    ? payload.recordIds.filter(Boolean)
    : [recordId].filter(Boolean);

  const tenantId = payload?.tenantId || payload?.tenant || payload?.tenantContext?.tenantId || '';

  return {
    ...payload,
    mode: 'edit',
    label: payload?.label || 'Edit Lead',
    record,
    lead: record,
    recordId,
    leadId: recordId,
    recordIds,
    tenantId,
    tenant: tenantId
  };
}

/**
 * @function sortWilsyLeadCommandKeys
 * @description Recursively sorts command payload keys for ProductionHardening seal parity.
 * @param {unknown} value - Raw value.
 * @returns {unknown} Sorted value.
 * @collaboration WILSY OS sealed Lead command capsule.
 */
function sortWilsyLeadCommandKeys(value) {
  if (Array.isArray(value)) return value.map(item => sortWilsyLeadCommandKeys(item));
  if (!value || typeof value !== 'object') return value;

  return Object.keys(value).sort().reduce((accumulator, key) => {
    accumulator[key] = sortWilsyLeadCommandKeys(value[key]);
    return accumulator;
  }, {});
}

/**
 * @function stringifyWilsyLeadCommandPayload
 * @description Builds the deterministic payload string used by the server integrity wall.
 * @param {Object} body - Request body.
 * @returns {string} Deterministic JSON.
 * @collaboration WILSY OS sealed Lead command capsule.
 */
function stringifyWilsyLeadCommandPayload(body = {}) {
  return JSON.stringify(sortWilsyLeadCommandKeys(body || {}));
}

/**
 * @function createWilsyLeadCommandNonce
 * @description Creates a non-secret command nonce.
 * @returns {string} Nonce.
 * @collaboration WILSY OS sealed Lead command capsule.
 */
function createWilsyLeadCommandNonce() {
  if (typeof window !== 'undefined' && window.crypto?.getRandomValues) {
    const bytes = new Uint8Array(16);
    window.crypto.getRandomValues(bytes);
    return Array.from(bytes).map(byte => byte.toString(16).padStart(2, '0')).join('');
  }

  return `nonce-${Date.now()}-${Math.random().toString(36).slice(2)}`;
}

/**
 * @function resolveWilsyLeadCommandRole
 * @description Resolves the local operator role used for display and backend role headers.
 * @returns {string} Role.
 * @collaboration Backend remains the final authority.
 */
function resolveWilsyLeadCommandRole() {
  if (typeof window === 'undefined') return 'SALES_REP';

  const directKeys = ['wilsyRole', 'wilsy:role', 'role', 'userRole', 'operatorRole'];
  for (const key of directKeys) {
    const value = window.localStorage?.getItem(key) || window.sessionStorage?.getItem(key);
    if (value) return String(value).replace(/["']/g, '').trim().toUpperCase();
  }

  const jsonKeys = ['user', 'wilsy:user', 'wilsy:operator', 'operator', 'profile'];
  for (const key of jsonKeys) {
    const value = window.localStorage?.getItem(key) || window.sessionStorage?.getItem(key);
    if (!value) continue;

    try {
      const parsed = JSON.parse(value);
      const role = parsed?.role || parsed?.userRole || parsed?.operatorRole || parsed?.accessRole;
      if (role) return String(role).trim().toUpperCase();
    } catch {
      // Ignore malformed identity storage.
    }
  }

  if (['localhost', '127.0.0.1'].includes(window.location.hostname)) return 'FOUNDER';
  return 'SALES_REP';
}

/**
 * @function resolveWilsyLeadCommandOperator
 * @description Resolves the local operator id for ownership display and headers.
 * @returns {Object} Operator packet.
 * @collaboration Backend remains the final authority.
 */
function resolveWilsyLeadCommandOperator() {
  if (typeof window === 'undefined') {
    return { role: 'SALES_REP', operatorId: 'SYSTEM', operatorEmail: '', operatorName: 'SYSTEM' };
  }

  const role = resolveWilsyLeadCommandRole();
  const keys = ['user', 'wilsy:user', 'wilsy:operator', 'operator', 'profile'];

  for (const key of keys) {
    const value = window.localStorage?.getItem(key) || window.sessionStorage?.getItem(key);
    if (!value) continue;

    try {
      const parsed = JSON.parse(value);
      return {
        role,
        operatorId: String(parsed.id || parsed._id || parsed.userId || parsed.operatorId || 'SYSTEM'),
        operatorEmail: String(parsed.email || parsed.operatorEmail || ''),
        operatorName: String(parsed.name || parsed.fullName || parsed.displayName || 'SYSTEM')
      };
    } catch {
      // Continue to fallback.
    }
  }

  return { role, operatorId: 'SYSTEM', operatorEmail: '', operatorName: 'SYSTEM' };
}

/**
 * @function buildWilsyLeadCommandHeaders
 * @description Builds tenant, auth, role and integrity headers for Lead commands.
 * @param {Object} params - Header params.
 * @returns {Object} Headers.
 * @collaboration WILSY OS sealed Lead command capsule.
 */
function buildWilsyLeadCommandHeaders({ tenantId = 'wilsy-sovereign-root', bodyPayload = {} } = {}) {
  const traceId = `CRM-R91K-${Date.now()}-${Math.random().toString(36).slice(2)}`;
  const timestamp = new Date().toISOString();
  const nonce = createWilsyLeadCommandNonce();
  const payloadStr = stringifyWilsyLeadCommandPayload(bodyPayload);
  const requestSeal = sha3_512(`${traceId}|${timestamp}|${payloadStr}|${nonce}`).toUpperCase();
  const operator = resolveWilsyLeadCommandOperator();

  const headers = {
    'Content-Type': 'application/json',
    Accept: 'application/json',
    'X-Tenant-Id': tenantId,
    'X-Wilsy-Tenant-ID': tenantId,
    'X-Wilsy-Role': operator.role,
    'X-Wilsy-Operator': operator.operatorId,
    'X-Wilsy-Operator-Email': operator.operatorEmail,
    'X-Wilsy-Operator-Name': operator.operatorName,
    'X-Trace-ID': traceId,
    'X-Forensic-Timestamp': timestamp,
    'X-Cryptographic-Nonce': nonce,
    'X-Request-Seal': requestSeal,
    'X-Request-Proof': requestSeal,
    'X-Binary-Strike': 'TRUE'
  };

  if (typeof window !== 'undefined') {
    const token = window.localStorage?.getItem('token')
      || window.localStorage?.getItem('authToken')
      || window.localStorage?.getItem('wilsyToken');

    if (token) headers.Authorization = `Bearer ${token}`;
  }

  return headers;
}

/**
 * @function resolveWilsyLeadValue
 * @description Resolves a Lead field from flexible backend payloads.
 * @param {Object} record - Lead record.
 * @param {string} field - Field name.
 * @returns {string} Field value.
 * @collaboration Source-backed Lead display.
 */
function resolveWilsyLeadValue(record = {}, field = '') {
  const displayName = record.name
    || record.leadName
    || record.fullName
    || record.contactName
    || [record.firstName, record.surname || record.lastName].filter(Boolean).join(' ')
    || record.email
    || record.primaryEmail;

  const displayPhone = record.phone
    || record.cellPhone
    || record.cellphone
    || record.mobile
    || record.mobilePhone
    || record.mobileNumber
    || record.primaryPhone
    || record.workPhone
    || record.telephone;

  const owner = record.owner
    || record.ownerName
    || record.assignedTo
    || record.assignee
    || record.createdByName
    || record.updatedByName
    || record.operatorName
    || record.createdBy
    || record.updatedBy
    || record.user;

  const values = {
    name: displayName,
    company: record.company || record.companyName || record.accountName || record.organization,
    email: record.email || record.primaryEmail || record.leadEmail || record.contactEmail,
    phone: displayPhone,
    owner: typeof owner === 'object' && owner ? (owner.name || owner.fullName || owner.email || owner.id) : owner,
    status: record.stage || record.pipelineStage || record.status || record.leadStatus || record.rating || 'Unstaged',
    source: record.source || record.sourceSystem || record.sourceChannel || record.connector || record.origin || record.campaign,
    compliance: record.complianceStatus || record.compliance?.status || record.ficaStatus || record.kycStatus || 'PENDING',
    provenance: record.provenanceHash || record.receiptHash || record._id || record.id || record.recordId
  };

  return String(values[field] || '—');
}

/**
 * @function resolveWilsyLeadProofValue
 * @description Normalizes proof values and marks missing data explicitly.
 * @param {unknown} value - Raw value.
 * @returns {string} Proof value.
 * @collaboration Proof Trail must not leave users guessing.
 */
function resolveWilsyLeadProofValue(value) {
  if (value === null || value === undefined || value === '') return 'SOURCE SILENT';
  if (Array.isArray(value)) return value.length ? JSON.stringify(value) : '[]';
  if (typeof value === 'object') {
    try {
      return JSON.stringify(value);
    } catch {
      return '[Unserializable source object]';
    }
  }
  return String(value);
}

/**
 * @function flattenWilsyLeadProofRows
 * @description Flattens all available Lead source fields into dot-path proof rows.
 * @param {Object} record - Lead record.
 * @param {string} prefix - Dot path prefix.
 * @returns {Array<Object>} Proof rows.
 * @collaboration Complete source-backed Proof Trail.
 */
function flattenWilsyLeadProofRows(record = {}, prefix = '') {
  if (!record || typeof record !== 'object') return [];

  return Object.entries(record).flatMap(([key, value]) => {
    const path = prefix ? `${prefix}.${key}` : key;

    if (Array.isArray(value)) return [{ label: path, value: resolveWilsyLeadProofValue(value) }];
    if (value && typeof value === 'object') return flattenWilsyLeadProofRows(value, path);

    return [{ label: path, value: resolveWilsyLeadProofValue(value) }];
  });
}

/**
 * @function resolveWilsyLeadOwnershipPosture
 * @description Explains whether the operator appears to own the selected Lead from source fields.
 * @param {Object} record - Lead record.
 * @returns {Object} Ownership posture.
 * @collaboration Tenant users need reasons before edit denial.
 */
function resolveWilsyLeadOwnershipPosture(record = {}) {
  const operator = resolveWilsyLeadCommandOperator();
  const operatorKeys = [operator.operatorId, operator.operatorEmail].filter(Boolean).map(value => String(value).toLowerCase());
  const ownerFields = [
    record.createdBy,
    record.createdById,
    record.createdByEmail,
    record.owner,
    record.ownerId,
    record.ownerEmail,
    record.assignedTo,
    record.assignedToId,
    record.assignedToEmail,
    record.operatorId,
    record.userId
  ].filter(Boolean).map(value => String(value).toLowerCase());

  const ownsRecord = operatorKeys.some(key => ownerFields.includes(key));
  const institutionalAuthority = isWilsyLeadInstitutionalAuthority(operator.role);

  if (institutionalAuthority) {
    return {
      ownsRecord: true,
      operator,
      ownerEvidence: ownerFields.length ? ownerFields.join(' · ') : 'SOURCE SILENT',
      reason: 'Institutional authority active. Ownership evidence remains visible as evidence but does not block Founder/Admin command authority.'
    };
  }

  return {
    ownsRecord,
    operator,
    ownerEvidence: ownerFields.length ? ownerFields.join(' · ') : 'SOURCE SILENT',
    reason: ownsRecord
      ? 'Current operator identity matches ownership evidence.'
      : 'Current operator identity does not match created-by or owner evidence in the source record.'
  };
}

/**
 * @function createWilsyLeadNode
 * @description Creates a DOM node with optional class and text.
 * @param {string} tagName - Tag name.
 * @param {string} className - Class name.
 * @param {string} text - Text content.
 * @returns {HTMLElement} DOM node.
 * @collaboration Safe DOM rendering.
 */
function createWilsyLeadNode(tagName = 'div', className = '', text = '') {
  const node = document.createElement(tagName);
  if (className) node.className = className;
  if (text !== '') node.textContent = String(text);
  return node;
}

/**
 * @function appendWilsyLeadCard
 * @description Appends one card to a command capsule section.
 * @param {HTMLElement} parent - Parent.
 * @param {string} label - Label.
 * @param {string} value - Value.
 * @param {string} tone - Tone.
 * @returns {HTMLElement} Card.
 * @collaboration Lead command capsule rendering.
 */
function appendWilsyLeadCard(parent, label, value, tone = 'neutral') {
  const card = createWilsyLeadNode('article', `wlcc-card wlcc-${tone}`);
  card.append(createWilsyLeadNode('small', '', label));
  card.append(createWilsyLeadNode('strong', '', resolveWilsyLeadProofValue(value)));
  parent.append(card);
  return card;
}

/**
 * @function ensureWilsyLeadCommandStyles
 * @description Mounts command capsule styles once.
 * @returns {void}
 * @collaboration Competition-grade Lead command capsule.
 */
function ensureWilsyLeadCommandStyles() {
  if (document.getElementById('wilsy-lead-command-capsule-styles')) return;

  const style = document.createElement('style');
  style.id = 'wilsy-lead-command-capsule-styles';
  style.textContent = `
    #wilsy-r91g1-lead-inspection-overlay {
      position: fixed;
      inset: 0;
      z-index: 2147483647;
      display: grid;
      grid-template-columns: minmax(310px, .36fr) minmax(760px, .64fr);
      background:
        radial-gradient(circle at 16% 18%, rgba(127, 90, 240, .32), transparent 34%),
        radial-gradient(circle at 75% 14%, rgba(0, 255, 148, .18), transparent 32%),
        linear-gradient(135deg, rgba(2, 6, 23, .78), rgba(5, 9, 22, .96));
      color: #f8fafc;
      backdrop-filter: blur(20px) saturate(1.16);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }

    #wilsy-r91g1-lead-inspection-overlay .wlcc-orbit {
      border-right: 1px solid rgba(125, 245, 165, .32);
      background:
        radial-gradient(circle at 50% 36%, rgba(125, 245, 165, .16), transparent 34%),
        linear-gradient(180deg, rgba(9, 14, 30, .58), rgba(4, 8, 18, .96));
      padding: 42px;
      display: grid;
      align-content: end;
      gap: 22px;
    }

    #wilsy-r91g1-lead-inspection-overlay .wlcc-orbit strong {
      color: rgba(232, 220, 167, .82);
      font-size: .78rem;
      font-weight: 950;
      letter-spacing: .26em;
      line-height: 1.8;
    }

    #wilsy-r91g1-lead-inspection-overlay .wlcc-orbit span {
      color: rgba(203, 213, 225, .52);
      font-size: .70rem;
      font-weight: 900;
      letter-spacing: .17em;
      line-height: 1.75;
      text-transform: uppercase;
    }

    #wilsy-r91g1-lead-inspection-overlay .wlcc-drawer {
      height: 100vh;
      overflow: auto;
      padding: 34px;
      background:
        radial-gradient(circle at 22% 0%, rgba(125, 245, 165, .10), transparent 34%),
        linear-gradient(160deg, rgba(8, 13, 30, .99), rgba(4, 8, 18, .995));
      box-shadow: -42px 0 130px rgba(0, 0, 0, .62);
    }

    #wilsy-r91g1-lead-inspection-overlay .wlcc-top {
      display: flex;
      justify-content: space-between;
      gap: 24px;
      padding-bottom: 22px;
      border-bottom: 1px solid rgba(148, 163, 184, .20);
      margin-bottom: 22px;
    }

    #wilsy-r91g1-lead-inspection-overlay .wlcc-pill {
      display: inline-flex;
      border: 1px solid rgba(125, 245, 165, .32);
      border-radius: 999px;
      padding: 9px 13px;
      background: rgba(6, 78, 59, .22);
      color: #d1fae5;
      font-size: .70rem;
      font-weight: 950;
      letter-spacing: .18em;
      text-transform: uppercase;
    }

    #wilsy-r91g1-lead-inspection-overlay h2 {
      margin: 12px 0 8px;
      color: #fff;
      font-size: clamp(2.4rem, 4vw, 4.8rem);
      line-height: .9;
      letter-spacing: -.07em;
    }

    #wilsy-r91g1-lead-inspection-overlay p {
      color: rgba(226, 232, 240, .78);
      font-size: 1rem;
      line-height: 1.62;
    }

    #wilsy-r91g1-lead-inspection-overlay button {
      cursor: pointer;
    }

    #wilsy-r91g1-lead-inspection-overlay .wlcc-close,
    #wilsy-r91g1-lead-inspection-overlay .wlcc-primary,
    #wilsy-r91g1-lead-inspection-overlay .wlcc-secondary,
    #wilsy-r91g1-lead-inspection-overlay .wlcc-danger {
      border-radius: 999px;
      padding: 12px 18px;
      font-weight: 950;
      color: #f8fafc;
    }

    #wilsy-r91g1-lead-inspection-overlay .wlcc-close {
      border: 1px solid rgba(125, 245, 165, .42);
      background: rgba(15, 23, 42, .92);
      min-width: 90px;
      height: 50px;
    }

    #wilsy-r91g1-lead-inspection-overlay .wlcc-primary {
      border: 1px solid rgba(125, 245, 165, .48);
      background: linear-gradient(135deg, rgba(16, 185, 129, .94), rgba(6, 78, 59, .88));
    }

    #wilsy-r91g1-lead-inspection-overlay .wlcc-secondary {
      border: 1px solid rgba(148, 163, 184, .34);
      background: rgba(15, 23, 42, .82);
    }

    #wilsy-r91g1-lead-inspection-overlay .wlcc-danger {
      border: 1px solid rgba(248, 113, 113, .5);
      background: linear-gradient(135deg, rgba(127, 29, 29, .86), rgba(69, 10, 10, .88));
    }

    #wilsy-r91g1-lead-inspection-overlay .wlcc-grid,
    #wilsy-r91g1-lead-inspection-overlay .wlcc-proof,
    #wilsy-r91g1-lead-inspection-overlay .wlcc-actions {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 12px;
      margin-top: 16px;
    }

    #wilsy-r91g1-lead-inspection-overlay .wlcc-proof {
      grid-template-columns: repeat(2, minmax(0, 1fr));
      max-height: 46vh;
      overflow: auto;
      padding-right: 6px;
    }

    #wilsy-r91g1-lead-inspection-overlay .wlcc-card,
    #wilsy-r91g1-lead-inspection-overlay .wlcc-panel {
      min-width: 0;
      border: 1px solid rgba(148, 163, 184, .22);
      border-radius: 22px;
      padding: 16px;
      background: rgba(3, 7, 18, .58);
    }

    #wilsy-r91g1-lead-inspection-overlay .wlcc-warning { border-color: rgba(251, 191, 36, .50); }
    #wilsy-r91g1-lead-inspection-overlay .wlcc-sealed { border-color: rgba(125, 245, 165, .44); }
    #wilsy-r91g1-lead-inspection-overlay .wlcc-dangerTone { border-color: rgba(248, 113, 113, .52); }

    #wilsy-r91g1-lead-inspection-overlay small {
      display: block;
      margin-bottom: 8px;
      color: #e8dca7;
      font-size: .68rem;
      font-weight: 950;
      letter-spacing: .16em;
      text-transform: uppercase;
    }

    #wilsy-r91g1-lead-inspection-overlay strong {
      display: block;
      overflow-wrap: anywhere;
      color: #f8fafc;
      font-size: 1rem;
      line-height: 1.45;
    }

    #wilsy-r91g1-lead-inspection-overlay .wlcc-panel {
      margin-top: 18px;
      background:
        linear-gradient(135deg, rgba(16, 185, 129, .09), rgba(127, 90, 240, .08)),
        rgba(15, 23, 42, .76);
    }

    #wilsy-r91g1-lead-inspection-overlay .wlcc-panel h3 {
      margin: 0 0 10px;
      color: #fff;
      font-size: 1.28rem;
    }

    #wilsy-r91g1-lead-inspection-overlay .wlcc-form {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 12px;
      margin: 16px 0;
    }

    #wilsy-r91g1-lead-inspection-overlay .wlcc-form label {
      display: grid;
      gap: 8px;
      color: #e8dca7;
      font-size: .74rem;
      font-weight: 950;
      letter-spacing: .12em;
      text-transform: uppercase;
    }

    #wilsy-r91g1-lead-inspection-overlay .wlcc-form input {
      width: 100%;
      border: 1px solid rgba(148, 163, 184, .30);
      border-radius: 16px;
      padding: 12px 13px;
      background: rgba(3, 7, 18, .72);
      color: #f8fafc;
      font-size: .96rem;
      text-transform: none;
      letter-spacing: 0;
    }

    #wilsy-r91g1-lead-inspection-overlay .wlcc-status {
      margin-top: 12px;
      color: rgba(226, 232, 240, .80);
    }

    @media (max-width: 1020px) {
      #wilsy-r91g1-lead-inspection-overlay { grid-template-columns: 1fr; }
      #wilsy-r91g1-lead-inspection-overlay .wlcc-orbit { display: none; }
      #wilsy-r91g1-lead-inspection-overlay .wlcc-grid,
      #wilsy-r91g1-lead-inspection-overlay .wlcc-proof,
      #wilsy-r91g1-lead-inspection-overlay .wlcc-actions,
      #wilsy-r91g1-lead-inspection-overlay .wlcc-form {
        grid-template-columns: 1fr;
      }
    }
  `;

  document.head.appendChild(style);
}

/**
 * @function requestWilsyLeadActionReceipt
 * @description Records non-mutating Lead action receipts.
 * @param {Object} params - Receipt params.
 * @returns {Promise<Object>} Receipt payload.
 * @collaboration View, Proof, Edit, Delete-intent and Change-owner-intent receipts.
 */
async function requestWilsyLeadActionReceipt({ apiBase = '', tenantId = 'wilsy-sovereign-root', recordId = '', action = 'VIEW_OPENED', mode = 'view', metadata = {} } = {}) {
  const bodyPayload = { tenantId, action, mode, metadata };
  const commandRoute = metadata?.route || metadata?.commandRoute || `/api/crm/command/leads/${encodeURIComponent(recordId)}/action-receipt`;
  const endpoint = buildWilsyLeadApiUrl({
    apiBase,
    route: commandRoute,
  }); /* R91K179E24P58H3_ACTION_RECEIPT_FETCH_REBUILT */

  const response = await fetch(endpoint, {
    method: 'POST',
    headers: buildWilsyLeadCommandHeaders({ tenantId, bodyPayload }),
    credentials: 'include',
    body: JSON.stringify(bodyPayload)
  });

  const payload = await response.json().catch(() => ({}));
  if (!response.ok || payload.ok === false) {
    const error = new Error(payload.message || payload.status || payload.code || `Receipt failed: ${response.status}`);
    error.payload = payload;
    error.status = response.status;
    throw error;
  }

  return payload;
}

/**
 * @function executeWilsyLeadMutation
 * @description Executes a sealed Lead mutation command.
 * @param {Object} params - Mutation params.
 * @returns {Promise<Object>} Mutation response.
 * @collaboration Backend authority returns reasons, next best actions and receipts.
 */
async function executeWilsyLeadMutation({ apiBase = '', tenantId = 'wilsy-sovereign-root', recordId = '', method = 'PATCH', lead = {}, action = '', route = '' } = {}) {
  const normalizedMethod = String(method || 'PATCH').toUpperCase();
  const bodyPayload = normalizedMethod === 'DELETE' ? {} : { tenantId, lead, action };
  const commandRoute = route || lead?.route || lead?.commandRoute || `/api/crm/command/leads/${encodeURIComponent(recordId)}`;
  const endpoint = buildWilsyLeadApiUrl({
    apiBase,
    route: commandRoute,
  }); /* R91K179E24P58H4_MUTATION_FETCH_REBUILT */

  const response = await fetch(endpoint, {
    method: normalizedMethod,
    headers: buildWilsyLeadCommandHeaders({ tenantId, bodyPayload }),
    credentials: 'include',
    body: normalizedMethod === 'DELETE' ? undefined : JSON.stringify(bodyPayload),
  });

  const payload = await response.json().catch(() => ({}));
  if (!response.ok || payload.ok === false) {
    const error = new Error(payload.message || payload.status || payload.code || `Command failed: ${response.status}`);
    error.payload = payload;
    error.status = response.status;
    throw error;
  }

  return payload;
}

/**
 * @function buildWilsyLeadEditPayload
 * @description Builds an edit payload from the capsule form.
 * @param {HTMLFormElement} form - Form node.
 * @param {Object} record - Existing record.
 * @returns {Object} Lead payload.
 * @collaboration Governed edit command.
 */
function buildWilsyLeadEditPayload(form, record = {}) {
  return {
    fullName: form.querySelector('[name="fullName"]')?.value || '',
    companyName: form.querySelector('[name="companyName"]')?.value || '',
    email: form.querySelector('[name="email"]')?.value || '',
    phone: form.querySelector('[name="phone"]')?.value || '',
    stage: form.querySelector('[name="stage"]')?.value || 'Prospecting',
    metadata: {
      ...(record.metadata || {}),
      r91kEditedAt: new Date().toISOString(),
      wilsyCommand: 'GOVERNED_EDIT_SAVE'
    }
  };
}


/* R91K179E24P58K BUSINESS_DELETE_RESULT_COPY */

/**
 * @function resolveWilsyR91K179E24P58KReceiptHash
 * @description Resolves a receipt hash from backend command responses for business-facing delete confirmation.
 * @param {Object} payload - Backend command payload.
 * @returns {string} Receipt hash or fallback.
 * @collaboration Delete governance menu, backend receipt bridge, audit proof trail.
 */
function resolveWilsyR91K179E24P58KReceiptHash(payload = {}) {
  return String(
    payload.receiptHash ||
    payload.receipt?.receiptHash ||
    payload.receipt?.hash ||
    payload.auditMesh?.receiptHash ||
    payload.commandReceipt?.receiptHash ||
    payload.data?.receiptHash ||
    ''
  ).trim();
}

/**
 * @function isWilsyR91K179E24P58KDeleteSuccess
 * @description Determines whether a command payload represents a successful protected delete.
 * @param {Object} payload - Backend command payload.
 * @returns {boolean} True when delete succeeded.
 * @collaboration CRM command result renderer, Meeting delete receipt bridge, Lead delete governance.
 */
function isWilsyR91K179E24P58KDeleteSuccess(payload = {}) {
  const status = String(payload.status || payload.result || payload.code || '').toUpperCase();
  const message = String(payload.message || payload.why || '').toLowerCase();

  return Boolean(
    payload.ok !== false &&
    (
      status.includes('DB_DELETED') ||
      status.includes('DELETED') ||
      message.includes('deleted through crm command authority') ||
      message.includes('meeting deleted') ||
      message.includes('lead deleted')
    )
  );
}

/**
 * @function resolveWilsyR91K179E24P58KBusinessDeleteCopy
 * @description Converts protected delete results into clear business English while retaining evidence posture.
 * @param {Object} payload - Backend command payload.
 * @returns {Object} Business copy.
 * @collaboration Delete verification menu, executive operator experience, receipt-safe audit posture.
 */
function resolveWilsyR91K179E24P58KBusinessDeleteCopy(payload = {}) {
  const moduleSignal = String(
    payload.module ||
    payload.recordModule ||
    payload.sourceModule ||
    payload.receipt?.module ||
    payload.auditMesh?.module ||
    ''
  ).toLowerCase();

  const recordLabel = moduleSignal.includes('meeting') ? 'meeting' : 'record';
  const receiptHash = resolveWilsyR91K179E24P58KReceiptHash(payload);

  return {
    title: 'The ' + recordLabel + ' was deleted successfully.',
    summary: 'Wilsy OS completed the protected delete and recorded the action against the audit trail.',
    evidence: receiptHash ? 'Receipt sealed: ' + receiptHash : 'Receipt evidence is pending review.',
    next: 'You can return to the records workspace or open the proof trail for the full governance record.',
    resultLabel: 'Completed',
    recordLabel,
    receiptHash,
  };
}

/**
 * @function renderWilsyR91K179E24P58KBusinessDeleteResult
 * @description Renders a compact business-English protected delete result.
 * @param {HTMLElement} statusNode - Status container.
 * @param {Object} payload - Backend command payload.
 * @returns {boolean} True when rendered.
 * @collaboration Protected delete verification menu, receipt-safe result renderer, boardroom-grade UX.
 */
function renderWilsyR91K179E24P58KBusinessDeleteResult(statusNode, payload = {}) {
  if (!statusNode || !isWilsyR91K179E24P58KDeleteSuccess(payload)) {
    return false;
  }

  const copy = resolveWilsyR91K179E24P58KBusinessDeleteCopy(payload);

  statusNode.classList.add('wlcc-business-delete-result');
  statusNode.innerHTML = '';

  const card = createWilsyLeadNode('div', 'wlcc-business-delete-card');
  const badge = createWilsyLeadNode('span', 'wlcc-business-delete-badge', copy.resultLabel);
  const title = createWilsyLeadNode('strong', 'wlcc-business-delete-title', copy.title);
  const summary = createWilsyLeadNode('p', 'wlcc-business-delete-summary', copy.summary);

  const evidence = createWilsyLeadNode('div', 'wlcc-business-delete-evidence');
  evidence.append(createWilsyLeadNode('span', '', 'Audit receipt'));
  evidence.append(createWilsyLeadNode('code', '', copy.receiptHash || 'Receipt pending'));

  const next = createWilsyLeadNode('p', 'wlcc-business-delete-next', copy.next);

  card.append(badge, title, summary, evidence, next);
  statusNode.append(card);

  return true;
}

/**
 * @function ensureWilsyR91K179E24P58KCompactDeleteVerificationStyles
 * @description Installs compact protected delete verification styles without changing backend command authority.
 * @returns {void}
 * @collaboration Delete governance drawer, Meeting verification UX, Lead command capsule.
 */
function ensureWilsyR91K179E24P58KCompactDeleteVerificationStyles() {
  if (document.getElementById('wilsy-r91k179e24p58k-delete-verification-styles')) {
    return;
  }

  const style = document.createElement('style');
  style.id = 'wilsy-r91k179e24p58k-delete-verification-styles';
  style.textContent = [
    '#wilsy-r91g1-lead-inspection-overlay .wlcc-business-delete-result { display: block; min-height: auto; }',
    '#wilsy-r91g1-lead-inspection-overlay .wlcc-business-delete-card { display: grid; gap: 0.7rem; padding: 1rem; border: 1px solid rgba(34,197,94,0.28); border-radius: 18px; background: linear-gradient(135deg, rgba(34,197,94,0.14), rgba(15,23,42,0.84)); box-shadow: 0 18px 48px rgba(0,0,0,0.24); }',
    '#wilsy-r91g1-lead-inspection-overlay .wlcc-business-delete-badge { width: fit-content; padding: 0.24rem 0.62rem; border-radius: 999px; border: 1px solid rgba(34,197,94,0.38); color: #bbf7d0; background: rgba(34,197,94,0.14); font-size: 0.7rem; letter-spacing: 0.08em; text-transform: uppercase; font-weight: 800; }',
    '#wilsy-r91g1-lead-inspection-overlay .wlcc-business-delete-title { color: #f8fafc; font-size: 1rem; line-height: 1.3; }',
    '#wilsy-r91g1-lead-inspection-overlay .wlcc-business-delete-summary, #wilsy-r91g1-lead-inspection-overlay .wlcc-business-delete-next { margin: 0; color: rgba(226,232,240,0.82); line-height: 1.5; font-size: 0.86rem; }',
    '#wilsy-r91g1-lead-inspection-overlay .wlcc-business-delete-evidence { display: grid; gap: 0.35rem; padding: 0.72rem; border-radius: 14px; border: 1px solid rgba(148,163,184,0.22); background: rgba(15,23,42,0.62); overflow: hidden; }',
    '#wilsy-r91g1-lead-inspection-overlay .wlcc-business-delete-evidence span { color: rgba(148,163,184,0.88); font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.08em; font-weight: 800; }',
    '#wilsy-r91g1-lead-inspection-overlay .wlcc-business-delete-evidence code { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; color: #e2e8f0; font-size: 0.78rem; }',
    '#wilsy-r91g1-lead-inspection-overlay .wlcc-proof, #wilsy-r91g1-lead-inspection-overlay .wlcc-status { max-height: 42vh; overflow: auto; }',
    '#wilsy-r91g1-lead-inspection-overlay .wlcc-proof pre, #wilsy-r91g1-lead-inspection-overlay .wlcc-panel pre { max-height: 180px; overflow: auto; border-radius: 14px; }',
    '#wilsy-r91g1-lead-inspection-overlay .wlcc-actions { position: sticky; bottom: 0; z-index: 8; padding-top: 0.75rem; background: linear-gradient(180deg, rgba(15,23,42,0), rgba(15,23,42,0.96) 32%); backdrop-filter: blur(12px); }'
  ].join('\n');

  document.head.appendChild(style);
}

/**
 * @function renderWilsyLeadReasonBox
 * @description Renders business-safe command status, including pre-delete verification and post-delete success receipts.
 * @param {HTMLElement} node - Status node.
 * @param {Object} payload - Backend payload.
 * @returns {void}
 * @collaboration Delete governance menu, backend receipt bridge, business-English operator confirmation.
 */
function renderWilsyLeadReasonBox(node, payload = {}) {
  if (!node) {
    return;
  }

  const overlay = document.getElementById('wilsy-r91g1-lead-inspection-overlay');
  const drawer = overlay?.querySelector?.('.wlcc-drawer') || node.closest?.('.wlcc-drawer') || null;

  /**
   * @function collapseProofTrail
   * @description Collapses long audit/proof panels by default for daily users while preserving on-demand evidence access.
   * @returns {void}
   * @collaboration Delete verification menu, tenant daily UX, audit evidence disclosure.
   */
  const collapseProofTrail = () => {
    const proofPanels = Array.from(drawer?.querySelectorAll?.('.wlcc-proof, .wlcc-panel') || []);
    proofPanels.forEach((panel) => {
      const heading = String(panel.querySelector?.('h3')?.textContent || panel.textContent || '').toLowerCase();
      const isProofTrail = heading.includes('complete proof trail') || heading.includes('proof trail') || heading.includes('audit');
      if (!isProofTrail) return;

      panel.classList.add('wlcc-proof-collapsed-daily');

      if (!panel.dataset.wilsyP58mCollapsed) {
        panel.dataset.wilsyP58mCollapsed = 'true';

        const toggle = createWilsyLeadNode('button', 'wlcc-secondary wlcc-proof-toggle', 'Show audit evidence');
        toggle.type = 'button';
        toggle.addEventListener('click', () => {
          const expanded = panel.classList.toggle('wlcc-proof-expanded-daily');
          toggle.textContent = expanded ? 'Hide audit evidence' : 'Show audit evidence';
        });

        panel.insertBefore(toggle, panel.firstChild);
      }
    });
  };

  /**
   * @function scheduleSuccessClose
   * @description Keeps the successful delete confirmation visible briefly before closing the capsule automatically.
   * @returns {void}
   * @collaboration Business delete confirmation, meeting receipt UX, command capsule lifecycle.
   */
  const scheduleSuccessClose = () => {
    if (!overlay || overlay.dataset.wilsyP58mAutoCloseScheduled === 'true') {
      return;
    }

    overlay.dataset.wilsyP58mAutoCloseScheduled = 'true';

    const closeNotice = createWilsyLeadNode('p', 'wlcc-business-delete-next', 'This confirmation will close automatically in a few seconds.');
    node.querySelector?.('.wlcc-business-delete-card')?.append(closeNotice);

    window.setTimeout(() => {
      const closeButton = overlay.querySelector('button[aria-label="Close"], .wlcc-close, button');
      if (closeButton && typeof closeButton.click === 'function') {
        closeButton.click();
        return;
      }

      overlay.remove();
    }, 4200);
  };

  const status = String(payload.sourceStatus || payload.status || payload.result || 'COMMAND_RESULT').toUpperCase();
  const message = String(payload.message || payload.why || '').trim();
  const receipt = payload.proofTrail?.auditReceiptHashShort ||
    payload.auditMesh?.receiptHashShort ||
    payload.auditMesh?.receiptHash ||
    payload.receipt?.receiptHash ||
    payload.receiptHash ||
    '';

  const isDeleteSuccess = payload.ok !== false && (
    status.includes('DB_DELETED') ||
    status.includes('DELETED') ||
    message.toLowerCase().includes('deleted through crm command authority') ||
    message.toLowerCase().includes('meeting deleted') ||
    message.toLowerCase().includes('lead deleted')
  );

  const isPreDeleteVerification = !receipt && (
    status === 'COMMAND_RESULT' ||
    status === 'READY' ||
    status === 'PENDING' ||
    message.toLowerCase().includes('command completed') ||
    !message
  );

  node.classList.add('wlcc-business-verification-status');
  node.innerHTML = '';

  if (isDeleteSuccess) {
    const card = createWilsyLeadNode('div', 'wlcc-business-delete-card');
    card.append(createWilsyLeadNode('span', 'wlcc-business-delete-badge', 'Completed'));
    card.append(createWilsyLeadNode('strong', 'wlcc-business-delete-title', 'The meeting was deleted successfully.'));
    card.append(createWilsyLeadNode('p', 'wlcc-business-delete-summary', 'Wilsy OS completed the protected delete and recorded the action against the audit trail.'));

    const evidence = createWilsyLeadNode('div', 'wlcc-business-delete-evidence');
    evidence.append(createWilsyLeadNode('span', '', 'Audit receipt'));
    evidence.append(createWilsyLeadNode('code', '', receipt || 'Receipt recorded'));
    card.append(evidence);

    card.append(createWilsyLeadNode('p', 'wlcc-business-delete-next', 'You can return to the records workspace or open the proof trail for the full governance record.'));
    node.append(card);

    collapseProofTrail();
    scheduleSuccessClose();
    return;
  }

  if (isPreDeleteVerification) {
    const card = createWilsyLeadNode('div', 'wlcc-business-delete-card wlcc-business-delete-card-pending');
    card.append(createWilsyLeadNode('span', 'wlcc-business-delete-badge', 'Verification required'));
    card.append(createWilsyLeadNode('strong', 'wlcc-business-delete-title', 'Ready for protected deletion.'));
    card.append(createWilsyLeadNode('p', 'wlcc-business-delete-summary', 'Wilsy OS will ask backend authority to delete this meeting. The action will only complete when the server confirms the decision and returns a receipt.'));

    const evidence = createWilsyLeadNode('div', 'wlcc-business-delete-evidence');
    evidence.append(createWilsyLeadNode('span', '', 'Receipt status'));
    evidence.append(createWilsyLeadNode('code', '', 'Receipt will be created after execution'));
    card.append(evidence);

    card.append(createWilsyLeadNode('p', 'wlcc-business-delete-next', 'Review the selected meeting, then choose Execute protected delete to continue.'));
    node.append(card);

    collapseProofTrail();
    return;
  }

  const reasons = Array.isArray(payload.reasons)
    ? payload.reasons
    : [message || payload.status || 'Command completed.'];

  const nextBestActions = Array.isArray(payload.nextBestActions)
    ? payload.nextBestActions
    : ['Open the proof trail for source fields, ownership evidence, compliance posture, receipt posture, and audit posture.'];

  const safeReceipt = receipt || 'Receipt pending';
  node.textContent = `Result: ${payload.sourceStatus || payload.status || 'COMMAND_RESULT'} · Receipt: ${safeReceipt} · Why: ${reasons.join(' ')} · Next: ${nextBestActions.join(' ')}`;

  collapseProofTrail();
} /* R91K179E24P58M_COLLAPSE_PROOF_AND_AUTOCLOSE_RENDERER */

/**
 * @function openWilsyLeadCommandCapsule
 * @description Opens the WILSY OS Lead command capsule for View, Proof, Edit, Delete, Change Owner and Mass Update.
 * @param {Object} params - Capsule params.
 * @returns {void}
 * @collaboration Epitome Lead CRUD command surface.
 */

/**
 * @function ensureR91K9LeadCommandViewportDesign
 * @description Installs hard viewport and premium layout overrides so the Lead command capsule never renders blank or bottom-pinned.
 * @returns {void} Mounts the R91K.9 viewport stylesheet.
 * @collaboration Restores visible View, Proof Trail, Edit, Delete, Change Owner, and Mass Update command surfaces.
 */
function ensureR91K9LeadCommandViewportDesign() {
  if (typeof document === 'undefined') return;
  if (document.getElementById('wilsy-lead-command-capsule-r91k9-viewport')) return;

  const style = document.createElement('style');
  style.id = 'wilsy-lead-command-capsule-r91k9-viewport';
  style.textContent = `
    #wilsy-r91g1-lead-inspection-overlay {
      position: fixed !important;
      inset: 0 !important;
      z-index: 2147483647 !important;
      display: block !important;
      min-height: 100vh !important;
      overflow: hidden !important;
      background:
        radial-gradient(circle at 12% 8%, rgba(0, 255, 148, .16), transparent 30%),
        radial-gradient(circle at 78% 14%, rgba(124, 58, 237, .22), transparent 34%),
        linear-gradient(135deg, rgba(2, 6, 23, .94), rgba(3, 7, 18, .985)) !important;
      color: #f8fafc !important;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif !important;
    }

    #wilsy-r91g1-lead-inspection-overlay .wlcc-orbit {
      position: fixed !important;
      top: 22px !important;
      left: 22px !important;
      bottom: 22px !important;
      width: min(340px, 28vw) !important;
      padding: 26px !important;
      display: grid !important;
      align-content: start !important;
      gap: 18px !important;
      border: 1px solid rgba(125, 245, 165, .26) !important;
      border-radius: 30px !important;
      background:
        linear-gradient(180deg, rgba(15, 23, 42, .72), rgba(2, 6, 23, .88)),
        radial-gradient(circle at 0 0, rgba(0, 255, 148, .12), transparent 40%) !important;
      box-shadow: 0 30px 90px rgba(0, 0, 0, .46), inset 0 1px 0 rgba(255, 255, 255, .06) !important;
    }

    #wilsy-r91g1-lead-inspection-overlay .wlcc-orbit::before {
      content: "WILSY OS";
      display: inline-flex;
      width: max-content;
      max-width: 100%;
      border: 1px solid rgba(232, 220, 167, .38);
      border-radius: 999px;
      padding: 9px 12px;
      color: rgba(232, 220, 167, .92);
      background: rgba(232, 220, 167, .08);
      font-size: .70rem;
      font-weight: 950;
      letter-spacing: .2em;
    }

    #wilsy-r91g1-lead-inspection-overlay .wlcc-orbit strong {
      margin-top: auto !important;
      color: #e8dca7 !important;
      font-size: .88rem !important;
      font-weight: 950 !important;
      letter-spacing: .22em !important;
      line-height: 1.8 !important;
      text-transform: uppercase !important;
    }

    #wilsy-r91g1-lead-inspection-overlay .wlcc-orbit span {
      color: rgba(226, 232, 240, .58) !important;
      font-size: .72rem !important;
      font-weight: 900 !important;
      letter-spacing: .17em !important;
      line-height: 1.85 !important;
      text-transform: uppercase !important;
    }

    #wilsy-r91g1-lead-inspection-overlay .wlcc-drawer {
      position: fixed !important;
      top: 22px !important;
      right: 22px !important;
      bottom: 22px !important;
      left: calc(min(340px, 28vw) + 44px) !important;
      width: auto !important;
      height: auto !important;
      max-height: calc(100vh - 44px) !important;
      overflow: auto !important;
      padding: 28px !important;
      border: 1px solid rgba(148, 163, 184, .22) !important;
      border-radius: 34px !important;
      background:
        linear-gradient(145deg, rgba(8, 13, 30, .98), rgba(2, 6, 23, .995)),
        radial-gradient(circle at 18% 0%, rgba(0, 255, 148, .12), transparent 30%),
        radial-gradient(circle at 86% 6%, rgba(124, 58, 237, .16), transparent 36%) !important;
      box-shadow: 0 34px 120px rgba(0, 0, 0, .58), inset 0 1px 0 rgba(255, 255, 255, .06) !important;
      scroll-behavior: smooth !important;
    }

    #wilsy-r91g1-lead-inspection-overlay .wlcc-top {
      position: sticky !important;
      top: -28px !important;
      z-index: 5 !important;
      display: grid !important;
      grid-template-columns: minmax(0, 1fr) auto !important;
      align-items: start !important;
      gap: 20px !important;
      padding: 0 0 20px !important;
      margin: 0 0 18px !important;
      border-bottom: 1px solid rgba(148, 163, 184, .18) !important;
      background: linear-gradient(180deg, rgba(8, 13, 30, .99), rgba(8, 13, 30, .86)) !important;
      backdrop-filter: blur(18px) !important;
    }

    #wilsy-r91g1-lead-inspection-overlay .wlcc-pill {
      display: inline-flex !important;
      width: max-content !important;
      max-width: 100% !important;
      margin: 0 0 10px !important;
      border: 1px solid rgba(0, 255, 148, .38) !important;
      border-radius: 999px !important;
      padding: 10px 14px !important;
      background: linear-gradient(135deg, rgba(6, 78, 59, .54), rgba(15, 23, 42, .82)) !important;
      color: #d1fae5 !important;
      font-size: .70rem !important;
      font-weight: 950 !important;
      letter-spacing: .18em !important;
      text-transform: uppercase !important;
    }

    #wilsy-r91g1-lead-inspection-overlay h2 {
      margin: 0 0 10px !important;
      color: #fff !important;
      font-size: clamp(2.7rem, 5.2vw, 5.8rem) !important;
      line-height: .86 !important;
      letter-spacing: -.08em !important;
      text-wrap: balance !important;
    }

    #wilsy-r91g1-lead-inspection-overlay p {
      max-width: 980px !important;
      color: rgba(226, 232, 240, .76) !important;
      font-size: 1.02rem !important;
      line-height: 1.65 !important;
    }

    #wilsy-r91g1-lead-inspection-overlay .wlcc-close {
      position: sticky !important;
      top: 0 !important;
      min-width: 92px !important;
      border: 1px solid rgba(125, 245, 165, .46) !important;
      border-radius: 999px !important;
      padding: 13px 18px !important;
      background: rgba(15, 23, 42, .92) !important;
      color: #f8fafc !important;
      font-weight: 950 !important;
      box-shadow: 0 18px 40px rgba(0, 0, 0, .30) !important;
    }

    #wilsy-r91g1-lead-inspection-overlay .wlcc-grid {
      display: grid !important;
      grid-template-columns: repeat(3, minmax(0, 1fr)) !important;
      gap: 14px !important;
      margin: 18px 0 0 !important;
    }

    #wilsy-r91g1-lead-inspection-overlay .wlcc-card,
    #wilsy-r91g1-lead-inspection-overlay .wlcc-panel {
      min-width: 0 !important;
      border: 1px solid rgba(148, 163, 184, .22) !important;
      border-radius: 24px !important;
      padding: 17px !important;
      background:
        linear-gradient(145deg, rgba(15, 23, 42, .74), rgba(2, 6, 23, .64)),
        radial-gradient(circle at 0 0, rgba(0, 255, 148, .07), transparent 38%) !important;
      box-shadow: inset 0 1px 0 rgba(255, 255, 255, .05), 0 18px 55px rgba(0, 0, 0, .22) !important;
    }

    #wilsy-r91g1-lead-inspection-overlay .wlcc-panel {
      margin-top: 16px !important;
    }

    #wilsy-r91g1-lead-inspection-overlay .wlcc-panel h3 {
      margin: 0 0 8px !important;
      color: #fff !important;
      font-size: 1.35rem !important;
      letter-spacing: -.02em !important;
    }

    #wilsy-r91g1-lead-inspection-overlay small {
      display: block !important;
      margin-bottom: 8px !important;
      color: #e8dca7 !important;
      font-size: .68rem !important;
      font-weight: 950 !important;
      letter-spacing: .16em !important;
      text-transform: uppercase !important;
    }

    #wilsy-r91g1-lead-inspection-overlay strong {
      display: block !important;
      overflow-wrap: anywhere !important;
      color: #f8fafc !important;
      font-size: 1.04rem !important;
      line-height: 1.45 !important;
    }

    #wilsy-r91g1-lead-inspection-overlay .wlcc-actions {
      display: flex !important;
      flex-wrap: wrap !important;
      gap: 10px !important;
      margin-top: 16px !important;
    }

    #wilsy-r91g1-lead-inspection-overlay .wlcc-primary,
    #wilsy-r91g1-lead-inspection-overlay .wlcc-secondary,
    #wilsy-r91g1-lead-inspection-overlay .wlcc-danger {
      border-radius: 999px !important;
      padding: 13px 17px !important;
      color: #f8fafc !important;
      font-weight: 950 !important;
      box-shadow: 0 18px 44px rgba(0, 0, 0, .24) !important;
    }

    #wilsy-r91g1-lead-inspection-overlay .wlcc-primary {
      border: 1px solid rgba(0, 255, 148, .48) !important;
      background: linear-gradient(135deg, rgba(16, 185, 129, .95), rgba(6, 95, 70, .90)) !important;
    }

    #wilsy-r91g1-lead-inspection-overlay .wlcc-secondary {
      border: 1px solid rgba(148, 163, 184, .32) !important;
      background: rgba(15, 23, 42, .86) !important;
    }

    #wilsy-r91g1-lead-inspection-overlay .wlcc-danger {
      border: 1px solid rgba(248, 113, 113, .55) !important;
      background: linear-gradient(135deg, rgba(127, 29, 29, .92), rgba(69, 10, 10, .92)) !important;
    }

    #wilsy-r91g1-lead-inspection-overlay .wlcc-form {
      display: grid !important;
      grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
      gap: 14px !important;
      margin: 18px 0 !important;
    }

    #wilsy-r91g1-lead-inspection-overlay .wlcc-form label {
      display: grid !important;
      gap: 8px !important;
      color: #e8dca7 !important;
      font-size: .72rem !important;
      font-weight: 950 !important;
      letter-spacing: .12em !important;
      text-transform: uppercase !important;
    }

    #wilsy-r91g1-lead-inspection-overlay .wlcc-form input {
      width: 100% !important;
      border: 1px solid rgba(148, 163, 184, .30) !important;
      border-radius: 17px !important;
      padding: 13px 14px !important;
      background: rgba(2, 6, 23, .78) !important;
      color: #f8fafc !important;
      font-size: 1rem !important;
      text-transform: none !important;
      letter-spacing: 0 !important;
      outline: none !important;
    }

    #wilsy-r91g1-lead-inspection-overlay .wlcc-form input:focus {
      border-color: rgba(0, 255, 148, .56) !important;
      box-shadow: 0 0 0 3px rgba(0, 255, 148, .12) !important;
    }

    #wilsy-r91g1-lead-inspection-overlay .wlcc-proof {
      display: grid !important;
      grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
      gap: 12px !important;
      max-height: none !important;
      overflow: visible !important;
      padding: 0 !important;
      margin-top: 16px !important;
    }

    #wilsy-r91g1-lead-inspection-overlay .wlcc-status {
      margin-top: 13px !important;
      border-left: 3px solid rgba(0, 255, 148, .50) !important;
      padding-left: 12px !important;
      color: rgba(226, 232, 240, .86) !important;
    }

    @media (max-width: 1100px) {
      #wilsy-r91g1-lead-inspection-overlay .wlcc-orbit {
        display: none !important;
      }

      #wilsy-r91g1-lead-inspection-overlay .wlcc-drawer {
        left: 14px !important;
        right: 14px !important;
        top: 14px !important;
        bottom: 14px !important;
        max-height: calc(100vh - 28px) !important;
      }

      #wilsy-r91g1-lead-inspection-overlay .wlcc-grid,
      #wilsy-r91g1-lead-inspection-overlay .wlcc-proof,
      #wilsy-r91g1-lead-inspection-overlay .wlcc-form {
        grid-template-columns: 1fr !important;
      }
    }
  `;

  document.head.appendChild(style);
}

/**
 * @function openWilsyLeadCommandCapsule
 * @description Opens the WILSY OS Lead command capsule with visible View, Proof Trail, Edit, Delete, Change Owner, and Mass Update command surfaces.
 * @param {Object} params - Capsule launch parameters including mode, label, record, recordId, recordIds, tenantId, and apiBase.
 * @returns {void} Mounts the sovereign Lead command capsule overlay.
 * @collaboration Owns the role-aware Lead command experience while backend R91K authority remains the final source of CRUD truth.
 */

/**
 * @function isWilsyLeadInstitutionalAuthority
 * @description Determines whether a role has institutional Lead authority rather than tenant-user ownership-limited authority.
 * @param {string} role - Operator role.
 * @returns {boolean} True when role is Founder, Master, Super Admin, or Admin.
 * @collaboration Aligns the capsule narrative with backend R91K CRUD authority.
 */
function isWilsyLeadInstitutionalAuthority(role = '') {
  return new Set(['FOUNDER', 'MASTER', 'SUPER_ADMIN', 'ADMIN']).has(String(role || '').trim().toUpperCase());
}

/**
 * @function buildWilsyLeadAuthorityNarrative
 * @description Builds the visible CRM lead authority narrative from institutional role authority, creator evidence, ownership evidence, compliance posture, and receipt posture.
 * @collaboration Keeps Founder and Super Admin authority separate from tenant ownership restrictions while preserving proof, reason, receipt, and next-best action.
 */
function buildWilsyLeadAuthorityNarrative({ ownership = {}, compliance = "PENDING" } = {}) {
  const role = String(
    ownership.role ||
      ownership.operatorRole ||
      ownership.userRole ||
      ownership.profileRole ||
      ownership.currentRole ||
      "TENANT_USER"
  )
    .trim()
    .toUpperCase()
    .replace(/\s+/g, "_");

  const institutionalAuthority =
    typeof isWilsyLeadInstitutionalAuthority === "function"
      ? isWilsyLeadInstitutionalAuthority(role)
      : ["FOUNDER", "MASTER", "SUPER_ADMIN", "ADMIN"].includes(role);

  const creatorVerified = Boolean(
    ownership.creatorVerified ||
      ownership.createdByCurrentOperator ||
      ownership.createdByMatchesOperator ||
      ownership.creatorMatchesOperator ||
      ownership.ownerMatchesOperator ||
      ownership.assignedToCurrentOperator ||
      ownership.operatorOwnsLead ||
      ownership.isCreator ||
      ownership.isOwner
  );

  const sourceSilence = Boolean(
    ownership.sourceSilence ||
      ownership.sourceFieldsSilent ||
      ownership.creatorSourceSilence ||
      ownership.ownerSourceSilence
  );

  const normalizedCompliance = String(compliance || ownership.compliance || "PENDING")
    .trim()
    .toUpperCase();

  if (institutionalAuthority) {
    const authorityEvidence = creatorVerified
      ? "Creator or ownership evidence matches this operator."
      : sourceSilence
        ? "Creator and ownership source fields are silent, so institutional authority carries the command while source silence remains recorded."
        : "Institutional command authority is active. Creator, owner, and assignment evidence remain available in the Proof Trail.";

    return {
      allowed: true,
      status: "INSTITUTIONAL_AUTHORITY_ACTIVE",
      summary: `Operator role: ${role}. Institutional authority is active. ${authorityEvidence} Compliance posture: ${normalizedCompliance}. Delete and owner transfer remain recorded, reasoned, and backend-authorized.`,
      reasons: [
        "Founder/Admin authority is institutionally governed.",
        creatorVerified ? "Creator or ownership evidence matched." : "Lead ownership evidence remains part of the Proof Trail.",
        `Compliance posture: ${normalizedCompliance}.`,
      ],
      nextBestActions: [
        "Open Proof Trail for source fields, source silence, ownership evidence, compliance posture, receipt posture, and audit posture.",
        "Record access receipt before destructive or owner-transfer action.",
      ],
    };
  }

  if (creatorVerified) {
    return {
      allowed: true,
      status: "CREATOR_OR_OWNER_AUTHORITY_VERIFIED",
      summary: `Operator role: ${role}. Creator or ownership authority is verified for this operator. Compliance posture: ${normalizedCompliance}. Command must still produce proof, receipt, and next-best action.`,
      reasons: [
        "Creator or owner evidence matched the current operator.",
        `Compliance posture: ${normalizedCompliance}.`,
      ],
      nextBestActions: [
        "Proceed with governed edit.",
        "Open Proof Trail before delete or owner-transfer action.",
      ],
    };
  }

  if (sourceSilence) {
    return {
      allowed: false,
      status: "SOURCE_SILENCE_REQUIRES_REVIEW",
      summary: `Operator role: ${role}. Creator and ownership source fields are silent. Tenant mutation authority requires recorded proof, receipt, and Founder/Admin review before destructive action.`,
      reasons: [
        "Creator and ownership source fields are silent.",
        "Tenant mutation authority needs verifiable source evidence.",
      ],
      nextBestActions: [
        "Open Proof Trail.",
        "Request Founder/Admin review.",
        "Record access receipt.",
      ],
    };
  }

  return {
    allowed: false,
    status: "TENANT_AUTHORITY_REQUIRES_REVIEW",
    summary: `Operator role: ${role}. Tenant mutation authority requires creator, owner, assignee, or Founder/Admin proof before action.`,
    reasons: [
      "Tenant operator is not verified as creator, owner, or assignee.",
      `Compliance posture: ${normalizedCompliance}.`,
    ],
    nextBestActions: [
      "Open Proof Trail.",
      "Request owner reassignment.",
      "Escalate to Founder/Admin.",
    ],
  };
}

/**
 * @function openWilsyLeadCommandCapsule
 * @description Opens the WILSY OS Lead command capsule with visible View, Proof Trail, Edit, Delete, Change Owner, and Mass Update command surfaces.
 * @param {Object} params - Capsule launch parameters including mode, label, record, recordId, recordIds, tenantId, and apiBase.
 * @returns {void} Mounts the sovereign Lead command capsule overlay.
 * @collaboration Owns the role-aware Lead command experience while backend R91K authority remains the final source of CRUD truth.
 */
/**
 * @function ensureR91K11LeadRailAndAuthorityDesign
 * @description Restores the R91K.11 capsule design installer required before the CRM lead command capsule opens.
 * @collaboration Called by openWilsyLeadCommandCapsule so View, Proof Trail, Edit, Delete, Mass Update, and Change Owner render without runtime failure.
 */
function ensureR91K11LeadRailAndAuthorityDesign() {
  if (typeof document === "undefined") {
    return;
  }

  const styleId = "wilsy-r91k11-lead-rail-authority-design";

  if (document.getElementById(styleId)) {
    return;
  }

  const style = document.createElement("style");
  style.id = styleId;
  style.textContent = [
    "#wilsy-r91g1-lead-inspection-overlay {",
    "  position: fixed !important;",
    "  inset: 0 !important;",
    "  z-index: 2147482000 !important;",
    "  width: 100vw !important;",
    "  height: 100vh !important;",
    "  overflow: auto !important;",
    "  pointer-events: auto !important;",
    "  isolation: isolate !important;",
    "}",
    "#wilsy-r91g1-lead-inspection-overlay > aside {",
    "  box-sizing: border-box !important;",
    "  max-height: calc(100vh - 48px) !important;",
    "  min-height: 0 !important;",
    "  overflow: auto !important;",
    "}",
    "#wilsy-r91g1-lead-inspection-overlay > aside > * {",
    "  box-sizing: border-box !important;",
    "  max-width: 100% !important;",
    "  min-width: 0 !important;",
    "}",
    "#wilsy-r91g1-lead-inspection-overlay [data-r91k12c-command-review-surface='visible'] {",
    "  display: block !important;",
    "  opacity: 1 !important;",
    "  visibility: visible !important;",
    "}",
  ].join("\n");

  document.head.appendChild(style);
}

/**
 * R91K.20A SAFE AUTHORITY DISPLAY REPAIR
 */

/**
 * @function normalizeR91K20ADisplayRole
 * @description Normalizes Wilsy OS authority evidence into the CRM command role vocabulary.
 * @collaboration Prevents the Lead Command verdict from displaying TENANT_USER when institutional proof exists.
 */
function normalizeR91K20ADisplayRole(value = "") {
  const role = String(value || "").trim().toUpperCase();

  if (["FOUNDER", "MASTER", "SUPER_ADMIN", "ADMIN", "TENANT_USER"].includes(role)) {
    return role;
  }

  if (role === "SUPERADMIN" || role === "SUPER ADMIN" || role === "ROOT" || role === "OWNER") {
    return "SUPER_ADMIN";
  }

  return "";
}

/**
 * @function findR91K20ARoleInObject
 * @description Searches nested record, profile, and token payloads for institutional authority evidence.
 * @collaboration Uses existing browser and record evidence without changing backend authorization.
 */
function findR91K20ARoleInObject(value, depth = 0) {
  if (!value || depth > 5) {
    return "";
  }

  if (typeof value === "string") {
    return normalizeR91K20ADisplayRole(value);
  }

  if (Array.isArray(value)) {
    for (const entry of value) {
      const found = findR91K20ARoleInObject(entry, depth + 1);

      if (found) {
        return found;
      }
    }

    return "";
  }

  if (typeof value === "object") {
    const roleKeys = [
      "role",
      "operatorRole",
      "userRole",
      "profileRole",
      "authorityRole",
      "wilsyRole",
      "accessRole",
      "accountRole",
      "permissionRole"
    ];

    for (const key of roleKeys) {
      const found = findR91K20ARoleInObject(value[key], depth + 1);

      if (found) {
        return found;
      }
    }

    for (const entry of Object.values(value)) {
      const found = findR91K20ARoleInObject(entry, depth + 1);

      if (found) {
        return found;
      }
    }
  }

  return "";
}

/**
 * @function parseR91K20AJson
 * @description Parses stored browser identity JSON safely.
 * @collaboration Supports role truth from existing session state without new API calls.
 */
function parseR91K20AJson(value = "") {
  try {
    return JSON.parse(value);
  } catch (error) {
    return null;
  }
}

/**
 * @function decodeR91K20AJwtPayload
 * @description Decodes a browser JWT payload when role evidence lives inside an auth token.
 * @collaboration Helps the View verdict reflect signed-in operator authority.
 */
function decodeR91K20AJwtPayload(value = "") {
  try {
    const parts = String(value || "").split(".");

    if (parts.length < 2 || typeof atob !== "function") {
      return null;
    }

    const normalizedPayload = parts[1].replace(/-/g, "+").replace(/_/g, "/");
    const paddedPayload = normalizedPayload.padEnd(Math.ceil(normalizedPayload.length / 4) * 4, "=");

    return JSON.parse(atob(paddedPayload));
  } catch (error) {
    return null;
  }
}

/**
 * @function collectR91K20ABrowserRoles
 * @description Collects institutional role evidence from local and session storage.
 * @collaboration Uses existing Wilsy OS identity state to repair display truth after capsule render.
 */
function collectR91K20ABrowserRoles() {
  if (typeof window === "undefined") {
    return [];
  }

  const roles = [];
  const stores = [window.localStorage, window.sessionStorage].filter(Boolean);

  stores.forEach((store) => {
    for (let index = 0; index < store.length; index += 1) {
      const key = store.key(index);
      const value = key ? store.getItem(key) : "";

      if (!key || !value) {
        continue;
      }

      const directRole = normalizeR91K20ADisplayRole(value);

      if (directRole) {
        roles.push(directRole);
      }

      const parsedRole = findR91K20ARoleInObject(parseR91K20AJson(value));

      if (parsedRole) {
        roles.push(parsedRole);
      }

      const decodedRole = findR91K20ARoleInObject(decodeR91K20AJwtPayload(value));

      if (decodedRole) {
        roles.push(decodedRole);
      }
    }
  });

  return roles;
}

/**
 * @function resolveR91K20AAuthorityRole
 * @description Resolves authority role from explicit context, record evidence, root tenant posture, and browser session state.
 * @collaboration Fixes the visible Lead Command verdict without altering backend authorization rules.
 */
function resolveR91K20AAuthorityRole({ record = {}, tenantId = "", ownership = {} } = {}) {
  const contextRole = findR91K20ARoleInObject({ record, ownership });

  if (contextRole && contextRole !== "TENANT_USER") {
    return contextRole;
  }

  const resolvedTenantId = String(
    tenantId ||
      record.tenantId ||
      record.raw?.tenantId ||
      record.metadata?.tenantId ||
      ownership.tenantId ||
      ownership.operatorTenantId ||
      ownership.recordTenantId ||
      ""
  ).trim().toLowerCase();

  if (["wilsy-sovereign-root", "root", "master"].includes(resolvedTenantId)) {
    return "SUPER_ADMIN";
  }

  const browserRoles = collectR91K20ABrowserRoles();
  const institutionalBrowserRole = browserRoles.find((role) => ["FOUNDER", "MASTER", "SUPER_ADMIN", "ADMIN"].includes(role));

  if (institutionalBrowserRole) {
    return institutionalBrowserRole;
  }

  return contextRole || "TENANT_USER";
}

/**
 * @function isR91K20AInstitutionalRole
 * @description Checks if a role holds institutional Lead Command authority.
 * @collaboration Keeps Founder, Master, Super Admin, and Admin authority language truthful.
 */
function isR91K20AInstitutionalRole(role = "") {
  return ["FOUNDER", "MASTER", "SUPER_ADMIN", "ADMIN"].includes(normalizeR91K20ADisplayRole(role));
}

/**
 * @function repairR91K20AAuthorityNarrative
 * @description Rewrites the visible authority verdict after capsule render when institutional proof exists.
 * @collaboration Repairs TENANT_USER display drift while preserving proof, reason, receipt, and backend governance.
 */
function repairR91K20AAuthorityNarrative(overlay, context = {}) {
  if (!overlay || typeof document === "undefined") {
    return;
  }

  const role = resolveR91K20AAuthorityRole(context);

  if (!isR91K20AInstitutionalRole(role)) {
    return;
  }

  const institutionalText = `Operator role: ${role}. Institutional authority is active. Ownership, creator, assignee, source gaps, and compliance posture remain visible as proof, but they do not block Founder/Admin command authority. Delete and owner transfer remain backend-governed and receipt-aware.`;

  Array.from(overlay.querySelectorAll("p, span, div")).forEach((node) => {
    const text = node.textContent || "";

    if (!/Operator role:\s*TENANT_USER/i.test(text)) {
      return;
    }

    if (!/Tenant mutation authority requires/i.test(text)) {
      return;
    }

    node.textContent = institutionalText;
  });

  overlay.dataset.r91k20aAuthorityRole = role;
}

/**
 * @function openWilsyLeadCommandCapsule
 * @description Opens the backend-backed CRM lead command capsule for View, Proof Trail, Edit, Delete, Mass Update, Change Owner, and receipt actions.
 * @collaboration Called by WilsyLeadOperatingRoom row and selected-row actions while preserving proof, reason, receipt, and next-best action discipline.
 */
/**
 * R91K.24A FRONTEND EDIT CONSTRUCTOR REBUILD
 */

/**
 * @function createR91K24Node
 * @description Creates a scoped DOM node for the production Lead Edit workspace.
 * @collaboration Replaces after-render mutation with direct edit construction inside WilsyLeadCommandCapsule.
 */
function createR91K24Node(tagName = 'div', className = '', text = '') {
  const node = document.createElement(tagName);

  if (className) node.className = className;
  if (text) node.textContent = text;

  return node;
}

/**
 * @function normalizeR91K24Text
 * @description Normalizes Lead field values for UI decisions.
 * @collaboration Prevents source silence and raw proof values from leaking into editable inputs.
 */
function normalizeR91K24Text(value = '') {
  return String(value || '').replace(/\s+/g, ' ').trim();
}

/**
 * @function isR91K24SourceSilent
 * @description Detects blank, dash, and source-silent values.
 * @collaboration Keeps Proof Trail evidence out of the operator edit form.
 */
function isR91K24SourceSilent(value = '') {
  const normalizedValue = normalizeR91K24Text(value).toUpperCase();

  return !normalizedValue || normalizedValue === '—' || normalizedValue === '-' || normalizedValue === 'SOURCE SILENT';
}

/**
 * @function readR91K24Path
 * @description Reads a dotted backend field path from a Lead record.
 * @collaboration Lets the edit constructor use backend data without exposing raw proof structures.
 */
function readR91K24Path(record = {}, path = '') {
  const parts = String(path || '').split('.');
  let current = record;

  for (const part of parts) {
    if (!current || typeof current !== 'object' || !(part in current)) {
      return undefined;
    }

    current = current[part];
  }

  return current;
}

/**
 * @function readR91K24FirstValue
 * @description Reads the first usable backend-backed Lead value from ordered field paths.
 * @collaboration Supports live rows, raw rows, imported rows, and normalized CRM Lead records.
 */
function readR91K24FirstValue(record = {}, paths = [], fallback = '') {
  for (const path of paths) {
    const value = readR91K24Path(record, path);

    if (Array.isArray(value) && value.length) {
      return value.join(', ');
    }

    if (value && typeof value === 'object') {
      const objectValue = value.fullName || value.name || value.email || value.id || value._id || value.e164 || value.rawInput;

      if (!isR91K24SourceSilent(objectValue)) {
        return String(objectValue);
      }
    }

    if (value !== undefined && value !== null && !isR91K24SourceSilent(value)) {
      return String(value);
    }
  }

  return fallback;
}

/**
 * @function cleanR91K24EditValue
 * @description Converts backend source silence into empty editable values.
 * @collaboration Leaves source silence available only through Proof Trail.
 */
function cleanR91K24EditValue(value = '', fallback = '') {
  return isR91K24SourceSilent(value) ? fallback : String(value || '');
}

/**
 * @function resolveR91K24LeadRecordId
 * @description Resolves the Lead record identifier used by the governed PATCH route.
 * @collaboration Keeps Edit Save aligned with the selected backend Lead row.
 */
function resolveR91K24LeadRecordId(record = {}, recordId = '') {
  return cleanR91K24EditValue(
    recordId ||
    readR91K24FirstValue(record, ['id', '_id', 'recordId', 'sourceRecordId', 'raw._id', 'raw.id']),
    ''
  );
}

/**
 * @function resolveR91K24LeadTenantId
 * @description Resolves tenant id for the Lead edit PATCH header.
 * @collaboration Preserves tenant routing for backend authority decisions.
 */
function resolveR91K24LeadTenantId(record = {}, tenantId = '') {
  return cleanR91K24EditValue(
    tenantId || readR91K24FirstValue(record, ['tenantId', 'raw.tenantId'], 'MASTER'),
    'MASTER'
  );
}

/**
 * @function formatR91K24CountryLabel
 * @description Formats libphonenumber country metadata into a readable country selector label.
 * @collaboration Gives Edit an international dialing selector without hardcoded country data.
 */
function formatR91K24CountryLabel(option = {}) {
  try {
    if (typeof Intl !== 'undefined' && Intl.DisplayNames) {
      const displayNames = new Intl.DisplayNames(['en'], { type: 'region' });
      return `${displayNames.of(option.iso2) || option.iso2} ${option.callingCode}`;
    }
  } catch (error) {
    return `${option.iso2} ${option.callingCode}`;
  }

  return `${option.iso2} ${option.callingCode}`;
}

/**
 * @function buildR91K24LeadEditFields
 * @description Builds the complete production Lead edit field registry.
 * @collaboration Mirrors Create Lead density while using selected backend Lead data.
 */
function buildR91K24LeadEditFields(record = {}) {
  const statusValue = normalizeWilsyLeadStatusValue(
    readR91K24FirstValue(record, ['status', 'stage', 'raw.status', 'raw.stage'], 'PROSPECTING')
  );

  return [
    { key: 'name', label: 'Lead name', type: 'text', required: true, value: readR91K24FirstValue(record, ['name', 'leadName', 'fullName', 'raw.fullName', 'raw.name', 'raw.firstName']), placeholder: 'Enter Lead name' },
    { key: 'company', label: 'Company', type: 'text', required: true, value: readR91K24FirstValue(record, ['company', 'companyName', 'accountName', 'raw.companyName', 'raw.company']), placeholder: 'Enter company' },
    { key: 'email', label: 'Email', type: 'email', required: true, value: readR91K24FirstValue(record, ['email', 'primaryEmail', 'leadEmail', 'raw.email']), placeholder: 'name@company.com' },
    { key: 'phone', label: 'Phone', type: 'phone', value: readR91K24FirstValue(record, ['phoneMeta.e164', 'phone', 'raw.phone']), placeholder: 'Phone number' },
    { key: 'mobile', label: 'Mobile', type: 'phone', value: readR91K24FirstValue(record, ['mobileMeta.e164', 'mobile', 'mobileNumber', 'raw.mobile']), placeholder: 'Mobile number' },
    { key: 'title', label: 'Title', type: 'text', value: readR91K24FirstValue(record, ['title', 'jobTitle', 'raw.title', 'raw.jobTitle']), placeholder: 'Decision maker title' },
    { key: 'status', label: 'Status', type: 'status', value: statusValue, placeholder: 'Select status' },
    { key: 'stage', label: 'Stage', type: 'text', value: formatWilsyLeadStatusLabel(statusValue), placeholder: 'Pipeline stage' },
    { key: 'ownerId', label: 'Owner ID', type: 'text', value: readR91K24FirstValue(record, ['ownerId', 'owner.id', 'assignedToId', 'raw.ownerId']), placeholder: 'Owner or assignee id' },
    { key: 'sourceChannel', label: 'Lead source', type: 'select', value: readR91K24FirstValue(record, ['sourceChannel', 'source', 'leadSource', 'raw.sourceChannel'], 'manual'), options: [
      { value: 'manual', label: 'Manual' },
      { value: 'website', label: 'Website' },
      { value: 'email', label: 'Email' },
      { value: 'referral', label: 'Referral' },
      { value: 'campaign', label: 'Campaign' },
      { value: 'import', label: 'Import' },
      { value: 'api', label: 'API' },
    ] },
    { key: 'priority', label: 'Priority', type: 'select', value: readR91K24FirstValue(record, ['priority', 'raw.priority'], 'NORMAL').toUpperCase(), options: [
      { value: 'LOW', label: 'Low' },
      { value: 'NORMAL', label: 'Normal' },
      { value: 'HIGH', label: 'High' },
      { value: 'URGENT', label: 'Urgent' },
    ] },
    { key: 'consentBasis', label: 'Consent basis', type: 'select', value: readR91K24FirstValue(record, ['consentBasis', 'raw.consentBasis'], ''), options: [
      { value: '', label: 'Select consent basis' },
      { value: 'CONSENT', label: 'Consent' },
      { value: 'LEGITIMATE_INTEREST', label: 'Legitimate interest' },
      { value: 'CONTRACT', label: 'Contract' },
      { value: 'LEGAL_OBLIGATION', label: 'Legal obligation' },
    ] },
    { key: 'value', label: 'Value', type: 'number', value: readR91K24FirstValue(record, ['value', 'amount', 'dealValue', 'raw.value'], '0'), placeholder: '0' },
    { key: 'score', label: 'Score', type: 'number', value: readR91K24FirstValue(record, ['score', 'leadScore', 'raw.score'], '0'), placeholder: '0' },
    { key: 'industry', label: 'Industry', type: 'text', value: readR91K24FirstValue(record, ['industry', 'raw.industry']), placeholder: 'Industry' },
    { key: 'dueDate', label: 'Due date', type: 'date', value: readR91K24FirstValue(record, ['dueDate', 'nextFollowUpAt', 'raw.dueDate']).slice(0, 10), placeholder: 'Due date' },
    { key: 'notes', label: 'Notes', type: 'textarea', value: readR91K24FirstValue(record, ['notes', 'description', 'raw.notes']), placeholder: 'Operator notes' },
  ];
}

/**
 * @function renderR91K24SelectControl
 * @description Renders a governed select control for repeated Lead values.
 * @collaboration Prevents manual typing for status, source, priority, and consent basis.
 */
function renderR91K24SelectControl(field = {}) {
  const select = createR91K24Node('select', 'r91k24EditControl');
  select.dataset.r91k24EditKey = field.key;
  select.setAttribute('aria-label', field.label);

  const options = field.type === 'status'
    ? WILSY_LEAD_STATUS_OPTIONS.map((option) => ({ value: option.value, label: option.label }))
    : field.options || [];

  options.forEach((option) => {
    const optionNode = createR91K24Node('option', '', option.label);
    optionNode.value = option.value;

    if (String(option.value).toUpperCase() === String(field.value || '').toUpperCase()) {
      optionNode.selected = true;
    }

    select.appendChild(optionNode);
  });

  return select;
}

/**
 * @function renderR91K24PhoneControl
 * @description Renders a country-aware phone editor using local libphonenumber metadata.
 * @collaboration Supplies country code selection and normalized client phone metadata for Save.
 */
function renderR91K24PhoneControl(field = {}) {
  const deck = createR91K24Node('div', 'r91k24PhoneDeck');
  const phoneMeta = normalizeWilsyPhoneForClient(field.value, WILSY_DEFAULT_PHONE_COUNTRY);
  const countrySelect = createR91K24Node('select', 'r91k24EditControl r91k24CountryControl');
  const phoneInput = createR91K24Node('input', 'r91k24EditControl');

  countrySelect.dataset.r91k24EditKey = `${field.key}CountryIso2`;
  countrySelect.setAttribute('aria-label', `${field.label} country`);
  phoneInput.dataset.r91k24EditKey = field.key;
  phoneInput.type = 'tel';
  phoneInput.value = cleanR91K24EditValue(formatWilsyPhoneDisplay(phoneMeta), '');
  phoneInput.placeholder = field.placeholder || 'Phone number';
  phoneInput.setAttribute('aria-label', field.label);

  getWilsyPhoneCountryOptions().forEach((option) => {
    const optionNode = createR91K24Node('option', '', formatR91K24CountryLabel(option));
    optionNode.value = option.iso2;

    if (option.iso2 === phoneMeta.countryIso2) {
      optionNode.selected = true;
    }

    countrySelect.appendChild(optionNode);
  });

  deck.append(countrySelect, phoneInput);

  return deck;
}

/**
 * @function renderR91K24InputControl
 * @description Renders a standard Lead edit input or textarea.
 * @collaboration Keeps the rebuilt Edit form actionable instead of proof-heavy.
 */
function renderR91K24InputControl(field = {}) {
  const input = createR91K24Node(field.type === 'textarea' ? 'textarea' : 'input', 'r91k24EditControl');
  input.dataset.r91k24EditKey = field.key;

  if (field.type !== 'textarea') {
    input.type = field.type || 'text';
  }

  input.value = cleanR91K24EditValue(field.value, '');
  input.placeholder = field.placeholder || field.label || '';
  input.setAttribute('aria-label', field.label);

  if (field.required) {
    input.required = true;
  }

  return input;
}

/**
 * @function renderR91K24EditField
 * @description Renders one Lead edit field from the production registry.
 * @collaboration Replaces the limited old r91jEditField construction for Edit mode.
 */
function renderR91K24EditField(field = {}) {
  const wrapper = createR91K24Node('label', 'r91k24EditField');
  const title = createR91K24Node('span', '', `${field.label}${field.required ? ' *' : ''}`);
  let control;

  if (field.type === 'status' || field.type === 'select') {
    control = renderR91K24SelectControl(field);
  } else if (field.type === 'phone') {
    control = renderR91K24PhoneControl(field);
  } else {
    control = renderR91K24InputControl(field);
  }

  wrapper.append(title, control);

  return wrapper;
}

/**
 * @function collectR91K24EditPayload
 * @description Collects rebuilt Edit controls into a backend PATCH Lead payload.
 * @collaboration Sends real form values, governed status, and phone metadata through the existing route.
 */
function collectR91K24EditPayload(overlay) {
  const payload = {};
  const phoneCountryMap = {};

  overlay.querySelectorAll('[data-r91k24-edit-key]').forEach((field) => {
    const key = field.dataset.r91k24EditKey;
    const value = String(field.value || '').trim();

    if (key.endsWith('CountryIso2')) {
      phoneCountryMap[key.replace('CountryIso2', '')] = value || WILSY_DEFAULT_PHONE_COUNTRY;
      return;
    }

    payload[key] = value;
  });

  ['phone', 'mobile'].forEach((key) => {
    const phoneMeta = normalizeWilsyPhoneForClient(payload[key] || '', phoneCountryMap[key] || WILSY_DEFAULT_PHONE_COUNTRY);

    payload[key] = phoneMeta.e164 || phoneMeta.rawInput || '';
    payload[`${key}Meta`] = phoneMeta;
  });

  payload.status = normalizeWilsyLeadStatusValue(payload.status || payload.stage || 'PROSPECTING');
  payload.stage = payload.stage || formatWilsyLeadStatusLabel(payload.status);
  payload.fullName = payload.name;
  payload.leadName = payload.name;
  payload.companyName = payload.company;
  payload.updatedBySurface = 'R91K.24A_FRONTEND_EDIT_CONSTRUCTOR';

  return payload;
}

/**
 * @function buildR91K24PatchHeaders
 * @description Builds headers for the existing backend Lead PATCH route.
 * @collaboration Preserves tenant and token posture for backend authority decisions.
 */
function buildR91K24PatchHeaders(tenantId = '') {
  const token =
    window.localStorage?.getItem('token') ||
    window.localStorage?.getItem('authToken') ||
    window.sessionStorage?.getItem('token') ||
    window.sessionStorage?.getItem('authToken') ||
    '';

  const headers = {
    'Content-Type': 'application/json',
    'X-Tenant-Id': tenantId || 'MASTER',
  };

  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  return headers;
}

/**
 * @function renderR91K24SaveStatus
 * @description Renders save result, reason, receipt, or transport failure.
 * @collaboration Keeps WILSY OS command surfaces proof-backed without dumping Proof Trail inside Edit.
 */
function renderR91K24SaveStatus(statusNode, payload = {}) {
  const receipt =
    payload.auditMesh?.receiptHashShort ||
    payload.auditMesh?.receiptHash ||
    payload.receiptHash ||
    payload.receipt ||
    'NO_RECEIPT_HASH';

  const reason =
    payload.reason ||
    payload.message ||
    payload.reasons?.[0] ||
    payload.status ||
    'Backend response received.';

  const nextAction =
    payload.nextBestAction ||
    payload.nextBestActions?.[0] ||
    'Review Proof Trail after save.';

  statusNode.textContent = `Result: ${payload.status || 'COMMAND_RECORDED'} · Receipt: ${receipt} · Why: ${reason} · Next: ${nextAction}`;
}

/**
 * @function submitR91K24LeadEdit
 * @description Saves the rebuilt Lead Edit form through the existing governed PATCH route.
 * @collaboration Keeps frontend construction correct before backend phoneMeta persistence is expanded.
 */
async function submitR91K24LeadEdit({ overlay, record = {}, recordId = '', tenantId = '', statusNode }) {
  const resolvedRecordId = resolveR91K24LeadRecordId(record, recordId);

  if (!resolvedRecordId) {
    renderR91K24SaveStatus(statusNode, {
      status: 'EDIT_BLOCKED',
      message: 'Record ID missing. Reopen the Lead from the backend row.',
      nextBestActions: ['Close Edit and reopen from the Lead row action menu.'],
    });
    return;
  }

  const lead = collectR91K24EditPayload(overlay);

  renderR91K24SaveStatus(statusNode, {
    status: 'COMMAND_RUNNING',
    message: 'Saving governed Lead edit.',
    nextBestActions: ['Wait for backend receipt.'],
  });

  try {
    const response = await fetch(`/api/crm/command/leads/${encodeURIComponent(resolvedRecordId)}`, {
      method: 'PATCH',
      headers: buildR91K24PatchHeaders(resolveR91K24LeadTenantId(record, tenantId)),
      body: JSON.stringify({
        action: 'UPDATE',
        lead,
        before: record,
        commandSurface: 'R91K.24A_FRONTEND_EDIT_CONSTRUCTOR',
      }),
    });

    const payload = await response.json().catch(() => ({
      status: response.ok ? 'DB_PERSISTED' : 'CRM_LEAD_EDIT_RESPONSE_UNREADABLE',
      message: response.ok ? 'Edit persisted but response body was unreadable.' : 'Backend returned an unreadable error.',
    }));

    renderR91K24SaveStatus(statusNode, payload);
  } catch (error) {
    renderR91K24SaveStatus(statusNode, {
      status: 'COMMAND_API_UNREACHABLE',
      message: `Lead command API transport failed: ${error.message}`,
      nextBestActions: ['Confirm backend is running.', 'Confirm Vite proxy /api is active.', 'Confirm token and tenant headers.'],
    });
  }
}

/**
 * @function ensureR91K24EditDesign
 * @description Installs scoped CSS for the rebuilt Lead Edit workspace.
 * @collaboration Gives Edit the Create Lead style form density without touching dashboard CSS.
 */
function ensureR91K24EditDesign() {
  const styleId = 'wilsy-r91k24a-edit-constructor-design';

  if (document.getElementById(styleId)) {
    return;
  }

  const style = document.createElement('style');
  style.id = styleId;
  style.textContent = `
    #wilsy-r91g1-lead-inspection-overlay.r91k24EditOverlay {
      position: fixed !important;
      inset: 0 !important;
      z-index: 2147483646 !important;
      display: grid !important;
      grid-template-columns: clamp(72px, 7vw, 118px) minmax(0, 1fr) !important;
      gap: clamp(12px, 1.4vw, 22px) !important;
      padding: clamp(12px, 1.35vw, 22px) !important;
      background: radial-gradient(circle at top left, rgba(16,185,129,0.20), rgba(2,6,23,0.98) 44%, rgba(2,6,23,1)) !important;
      color: #fff !important;
      overflow: hidden !important;
      box-sizing: border-box !important;
    }

    #wilsy-r91g1-lead-inspection-overlay .r91k24EditRail {
      border: 1px solid rgba(16,185,129,0.44) !important;
      border-radius: 28px !important;
      background: rgba(2,6,23,0.76) !important;
      padding: 16px 10px !important;
      display: grid !important;
      grid-template-rows: auto 1fr auto !important;
      overflow: hidden !important;
    }

    #wilsy-r91g1-lead-inspection-overlay .r91k24EditRail strong,
    #wilsy-r91g1-lead-inspection-overlay .r91k24EditRail span {
      writing-mode: vertical-rl !important;
      justify-self: center !important;
      color: rgba(245,230,170,0.94) !important;
      text-transform: uppercase !important;
      letter-spacing: 0.18em !important;
      font-weight: 950 !important;
    }

    #wilsy-r91g1-lead-inspection-overlay .r91k24EditWorkspace {
      min-width: 0 !important;
      min-height: 0 !important;
      overflow: auto !important;
      border: 1px solid rgba(148,163,184,0.26) !important;
      border-radius: 30px !important;
      background: rgba(2,6,23,0.76) !important;
      padding: clamp(18px, 1.8vw, 34px) !important;
      box-sizing: border-box !important;
    }

    #wilsy-r91g1-lead-inspection-overlay .r91k24EditHeader {
      display: grid !important;
      grid-template-columns: minmax(0, 1fr) auto !important;
      gap: 16px !important;
      align-items: start !important;
      border-bottom: 1px solid rgba(148,163,184,0.22) !important;
      padding-bottom: 18px !important;
      margin-bottom: 20px !important;
    }

    #wilsy-r91g1-lead-inspection-overlay .r91k24EditHeader small {
      display: inline-flex !important;
      border: 1px solid rgba(16,185,129,0.72) !important;
      border-radius: 999px !important;
      padding: 10px 16px !important;
      color: rgba(245,230,170,0.96) !important;
      background: rgba(6,78,59,0.45) !important;
      font-weight: 950 !important;
      letter-spacing: 0.16em !important;
      text-transform: uppercase !important;
    }

    #wilsy-r91g1-lead-inspection-overlay .r91k24EditHeader h1 {
      font-size: clamp(42px, 5.4vw, 86px) !important;
      line-height: 0.9 !important;
      margin: 16px 0 12px !important;
      letter-spacing: -0.07em !important;
    }

    #wilsy-r91g1-lead-inspection-overlay .r91k24EditHeader p {
      color: rgba(203,213,225,0.86) !important;
      font-size: clamp(15px, 1.2vw, 20px) !important;
      margin: 0 !important;
      max-width: 82rem !important;
    }

    #wilsy-r91g1-lead-inspection-overlay .r91k24EditActions {
      display: flex !important;
      flex-wrap: wrap !important;
      gap: 12px !important;
      justify-content: flex-end !important;
    }

    #wilsy-r91g1-lead-inspection-overlay .r91k24EditActions button,
    #wilsy-r91g1-lead-inspection-overlay .r91k24SaveButton {
      border-radius: 18px !important;
      border: 1px solid rgba(148,163,184,0.32) !important;
      background: rgba(15,23,42,0.92) !important;
      color: #fff !important;
      cursor: pointer !important;
      font-weight: 900 !important;
      padding: 15px 20px !important;
      font-size: 15px !important;
    }

    #wilsy-r91g1-lead-inspection-overlay .r91k24SaveButton {
      background: linear-gradient(135deg, #20e391, #0f8f68) !important;
      border-color: rgba(16,185,129,0.85) !important;
      color: #02130d !important;
    }

    #wilsy-r91g1-lead-inspection-overlay .r91k24EditForm {
      border: 1px solid rgba(148,163,184,0.22) !important;
      border-radius: 28px !important;
      padding: clamp(18px, 1.6vw, 30px) !important;
      background: rgba(15,23,42,0.54) !important;
      display: grid !important;
      gap: 18px !important;
    }

    #wilsy-r91g1-lead-inspection-overlay .r91k24EditGrid {
      display: grid !important;
      grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
      gap: 16px !important;
    }

    #wilsy-r91g1-lead-inspection-overlay .r91k24EditField {
      display: grid !important;
      gap: 9px !important;
      min-width: 0 !important;
    }

    #wilsy-r91g1-lead-inspection-overlay .r91k24EditField span {
      color: rgba(245,230,170,0.94) !important;
      font-size: 12px !important;
      font-weight: 950 !important;
      letter-spacing: 0.18em !important;
      text-transform: uppercase !important;
    }

    #wilsy-r91g1-lead-inspection-overlay .r91k24EditControl {
      width: 100% !important;
      min-height: 58px !important;
      border: 1px solid rgba(148,163,184,0.28) !important;
      border-radius: 18px !important;
      background: rgba(2,6,23,0.88) !important;
      color: #fff !important;
      font-size: clamp(16px, 1.15vw, 21px) !important;
      font-weight: 850 !important;
      padding: 14px 16px !important;
      outline: none !important;
      box-sizing: border-box !important;
    }

    #wilsy-r91g1-lead-inspection-overlay textarea.r91k24EditControl {
      min-height: 116px !important;
      resize: vertical !important;
    }

    #wilsy-r91g1-lead-inspection-overlay .r91k24PhoneDeck {
      display: grid !important;
      grid-template-columns: minmax(180px, 0.34fr) minmax(0, 1fr) !important;
      gap: 10px !important;
    }

    #wilsy-r91g1-lead-inspection-overlay .r91k24SaveStatus {
      border-left: 4px solid rgba(16,185,129,0.84) !important;
      color: rgba(203,213,225,0.92) !important;
      padding: 13px 16px !important;
      background: rgba(2,6,23,0.58) !important;
      border-radius: 14px !important;
      overflow-wrap: anywhere !important;
    }

    @media (max-width: 980px) {
      #wilsy-r91g1-lead-inspection-overlay.r91k24EditOverlay {
        grid-template-columns: 1fr !important;
      }

      #wilsy-r91g1-lead-inspection-overlay .r91k24EditRail {
        display: none !important;
      }

      #wilsy-r91g1-lead-inspection-overlay .r91k24EditHeader,
      #wilsy-r91g1-lead-inspection-overlay .r91k24EditGrid,
      #wilsy-r91g1-lead-inspection-overlay .r91k24PhoneDeck {
        grid-template-columns: 1fr !important;
      }
    }
  `;
  document.head.appendChild(style);
}

/**
 * @function openR91K24LeadEditWorkspace
 * @description Opens the rebuilt Lead Edit workspace without rendering Proof Trail content inside Edit.
 * @collaboration Delegates Proof Trail to its own command action while keeping Edit focused on actionable form fields.
 */
function openR91K24LeadEditWorkspace({ mode = 'edit', label = 'Edit Lead', record = {}, recordId = '', recordIds = [], tenantId = '' } = {}) {
  if (typeof document === 'undefined') {
    return null;
  }

  const existingOverlay = document.getElementById('wilsy-r91g1-lead-inspection-overlay');

  if (existingOverlay) {
    existingOverlay.remove();
  }

  ensureR91K24EditDesign();

  const overlay = createR91K24Node('section', 'r91k24EditOverlay');
  overlay.id = 'wilsy-r91g1-lead-inspection-overlay';
  overlay.dataset.r91k24EditConstructor = 'true';
  overlay.dataset.mode = mode;
  overlay.dataset.recordId = resolveR91K24LeadRecordId(record, recordId);

  const rail = createR91K24Node('aside', 'r91k24EditRail');
  rail.append(
    createR91K24Node('strong', '', 'WILSY OS'),
    createR91K24Node('span', '', 'Lead Edit'),
    createR91K24Node('span', '', 'Actionable Data')
  );

  const workspace = createR91K24Node('main', 'r91k24EditWorkspace');
  const header = createR91K24Node('header', 'r91k24EditHeader');
  const titleBlock = createR91K24Node('div', '');
  const actions = createR91K24Node('div', 'r91k24EditActions');
  const proofButton = createR91K24Node('button', '', 'Open Proof Trail');
  const closeButton = createR91K24Node('button', '', 'Close');

  proofButton.type = 'button';
  closeButton.type = 'button';

  proofButton.addEventListener('click', () => {
    overlay.remove();
    openWilsyLeadCommandCapsule({
      mode: 'proof',
      label: 'Proof Trail',
      record,
      recordId,
      recordIds,
      tenantId,
    });
  });

  closeButton.addEventListener('click', () => overlay.remove());

  titleBlock.append(
    createR91K24Node('small', '', 'Focused Edit'),
    createR91K24Node('h1', '', 'Edit Lead'),
    createR91K24Node('p', '', 'Edit the backend Lead record from one production form surface. Proof Trail is available on demand and is not rendered inside the edit task.')
  );

  actions.append(proofButton, closeButton);
  header.append(titleBlock, actions);

  const form = createR91K24Node('section', 'r91k24EditForm');
  const formHeader = createR91K24Node('div', '');
  const grid = createR91K24Node('div', 'r91k24EditGrid');
  const saveButton = createR91K24Node('button', 'r91k24SaveButton', 'Save governed edit');
  const statusNode = createR91K24Node('div', 'r91k24SaveStatus', 'Ready. Edit values are actionable. Proof evidence is separated into Proof Trail.');

  saveButton.type = 'button';

  formHeader.append(
    createR91K24Node('h2', '', 'Lead Information'),
    createR91K24Node('p', '', 'All visible fields are editable controls backed by the selected Lead record.')
  );

  buildR91K24LeadEditFields(record).forEach((field) => {
    grid.appendChild(renderR91K24EditField(field));
  });

  saveButton.addEventListener('click', () => {
    submitR91K24LeadEdit({
      overlay,
      record,
      recordId,
      tenantId,
      statusNode,
    });
  });

  form.append(formHeader, grid, saveButton, statusNode);
  workspace.append(header, form);
  overlay.append(rail, workspace);
  document.body.appendChild(overlay);

  return overlay;
}

/**
 * @function openWilsyLeadCommandCapsule
 * @description Opens the CRM Lead command capsule and delegates Edit mode to the R91K.24A focused edit constructor while keeping View, Proof Trail, Delete, Mass Update, and Change Owner governed.
 * @collaboration Receives Lead row actions from WilsyLeadOperatingRoom and preserves backend-backed receipt, reason, and Proof Trail separation.
 */
export function openWilsyLeadCommandCapsule({
  mode = 'view',
  label = 'View',
  record = {},
  recordId = '',
  recordIds = [],
  tenantId = 'wilsy-sovereign-root',
  apiBase = '',
  module = '',
  moduleName = '',
  recordModule = '',
  sourceModule = '',
  recordSingular = '',
  recordPlural = '',
  operatingCopy = {},
  governanceCopy = {},
} = {}) {
  const wilsyR91K179E24P58D2LaunchParams = {
    mode,
    label,
    record,
    recordId,
    recordIds,
    tenantId,
    apiBase,
    module,
    moduleName,
    recordModule,
    sourceModule,
    recordSingular,
    recordPlural,
    operatingCopy,
    governanceCopy,
  };
  const wilsyR91K179E24P58D2GovernanceCopy = resolveWilsyR91K179E24P58D2GovernanceCopy(wilsyR91K179E24P58D2LaunchParams, record || {});

  const wilsyR91K24ECommandPayload = {
    mode,
    label,
    record,
    recordId,
    recordIds,
    tenantId,
    apiBase,
    module,
    moduleName,
    recordModule,
    sourceModule,
    recordSingular,
    recordPlural,
    operatingCopy,
    governanceCopy,
    governanceCopyResolved: wilsyR91K179E24P58D2GovernanceCopy,
    route: resolveWilsyR91K179E24P58HProtectedDeleteRoute({
      mode,
      label,
      record,
      recordId,
      recordIds,
      module,
      moduleName,
      recordModule,
      sourceModule,
      recordSingular,
      recordPlural,
      operatingCopy,
      governanceCopy,
    }),
    method: 'DELETE', /* R91K179E24P58H_ROUTE_ON_COMMAND_PAYLOAD */
    commandSurface: governanceCopy?.commandSurface || 'R91K179E24P58E2_RESTORED_COMMAND_PAYLOAD',
  }; /* R91K179E24P58E2_RESTORED_COMMAND_PAYLOAD */

  try {
    window.setTimeout(() => applyWilsyR91K179E24P58D2GovernanceCopy(document, wilsyR91K179E24P58D2GovernanceCopy), 0);
    window.setTimeout(() => applyWilsyR91K179E24P58D2GovernanceCopy(document, wilsyR91K179E24P58D2GovernanceCopy), 60);
    window.setTimeout(() => applyWilsyR91K179E24P58D2GovernanceCopy(document, wilsyR91K179E24P58D2GovernanceCopy), 180);
    window.setTimeout(() => applyWilsyR91K179E24P58D2GovernanceCopy(document, wilsyR91K179E24P58D2GovernanceCopy), 360);
  } catch (error) {
    // Non-fatal. Capsule opening and backend authority are more important than copy reconciliation.
  } /* P58D2_APPLY_MODULE_GOVERNANCE_COPY_TIMERS */
  if (shouldRouteWilsyLeadCommandCapsuleToEditSurface(wilsyR91K24ECommandPayload)) {
    return openWilsyLeadEditSurface(
      buildWilsyLeadEditSurfacePayloadFromCapsule(wilsyR91K24ECommandPayload)
    );
  }

  const r91k24CommandIntent = `${mode || ''} ${label || ''}`.toLowerCase();

  if (
    r91k24CommandIntent.includes('edit') ||
    r91k24CommandIntent.includes('editable') ||
    r91k24CommandIntent.includes('governed edit') ||
    r91k24CommandIntent.includes('lead editable data')
  ) {
    return openR91K24LeadEditWorkspace({ mode, label, record, recordId, recordIds, tenantId });
  }


  if (typeof document === 'undefined') return;

  ensureWilsyLeadCommandStyles();
  if (!document.getElementById('wilsy-r91k179e24p58m-collapsed-proof-styles')) {
    const wilsyR91K179E24P58MStyle = document.createElement('style');
    wilsyR91K179E24P58MStyle.id = 'wilsy-r91k179e24p58m-collapsed-proof-styles';
    wilsyR91K179E24P58MStyle.textContent = [
      '#wilsy-r91g1-lead-inspection-overlay .wlcc-proof-collapsed-daily { max-height: 74px; overflow: hidden; opacity: .82; transition: max-height .22s ease, opacity .22s ease; }',
      '#wilsy-r91g1-lead-inspection-overlay .wlcc-proof-collapsed-daily.wlcc-proof-expanded-daily { max-height: 52vh; overflow: auto; opacity: 1; }',
      '#wilsy-r91g1-lead-inspection-overlay .wlcc-proof-toggle { margin: 0 0 .75rem 0; width: fit-content; }',
      '#wilsy-r91g1-lead-inspection-overlay .wlcc-proof-collapsed-daily:not(.wlcc-proof-expanded-daily) > *:not(.wlcc-proof-toggle):not(h3):not(p) { display: none !important; }',
      '#wilsy-r91g1-lead-inspection-overlay .wlcc-proof-collapsed-daily:not(.wlcc-proof-expanded-daily) p { display: none !important; }'
    ].join('\n');
    document.head.appendChild(wilsyR91K179E24P58MStyle);
  } /* R91K179E24P58M_COLLAPSED_PROOF_STYLES */
  if (!document.getElementById('wilsy-r91k179e24p58l-business-delete-status-styles')) {
    const wilsyR91K179E24P58LStyle = document.createElement('style');
    wilsyR91K179E24P58LStyle.id = 'wilsy-r91k179e24p58l-business-delete-status-styles';
    wilsyR91K179E24P58LStyle.textContent = [
      '#wilsy-r91g1-lead-inspection-overlay .wlcc-business-delete-card { display: grid; gap: .7rem; padding: 1rem; border: 1px solid rgba(34,197,94,.28); border-radius: 18px; background: linear-gradient(135deg, rgba(34,197,94,.12), rgba(15,23,42,.84)); }',
      '#wilsy-r91g1-lead-inspection-overlay .wlcc-business-delete-card-pending { border-color: rgba(232,220,167,.28); background: linear-gradient(135deg, rgba(232,220,167,.10), rgba(15,23,42,.84)); }',
      '#wilsy-r91g1-lead-inspection-overlay .wlcc-business-delete-badge { width: fit-content; padding: .25rem .65rem; border-radius: 999px; border: 1px solid rgba(34,197,94,.34); color: #bbf7d0; background: rgba(34,197,94,.12); font-size: .7rem; letter-spacing: .08em; text-transform: uppercase; font-weight: 900; }',
      '#wilsy-r91g1-lead-inspection-overlay .wlcc-business-delete-title { color: #f8fafc; font-size: 1rem; line-height: 1.35; }',
      '#wilsy-r91g1-lead-inspection-overlay .wlcc-business-delete-summary, #wilsy-r91g1-lead-inspection-overlay .wlcc-business-delete-next { margin: 0; color: rgba(226,232,240,.82); line-height: 1.5; font-size: .88rem; }',
      '#wilsy-r91g1-lead-inspection-overlay .wlcc-business-delete-evidence { display: grid; gap: .35rem; padding: .7rem; border-radius: 14px; border: 1px solid rgba(148,163,184,.22); background: rgba(15,23,42,.62); overflow: hidden; }',
      '#wilsy-r91g1-lead-inspection-overlay .wlcc-business-delete-evidence span { color: rgba(148,163,184,.88); font-size: .72rem; text-transform: uppercase; letter-spacing: .08em; font-weight: 900; }',
      '#wilsy-r91g1-lead-inspection-overlay .wlcc-business-delete-evidence code { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; color: #e2e8f0; font-size: .78rem; }',
      '#wilsy-r91g1-lead-inspection-overlay .wlcc-proof, #wilsy-r91g1-lead-inspection-overlay .wlcc-status { max-height: 42vh; overflow: auto; }'
    ].join('\n');
    document.head.appendChild(wilsyR91K179E24P58LStyle);
  } /* R91K179E24P58L_BUSINESS_DELETE_STATUS_STYLES */
  ensureWilsyR91K179E24P58KCompactDeleteVerificationStyles(); /* R91K179E24P58K_COMPACT_DELETE_STYLES_INSTALLED */
  ensureR91K9LeadCommandViewportDesign();
  ensureR91K11LeadRailAndAuthorityDesign();

  const existing = document.getElementById('wilsy-r91g1-lead-inspection-overlay');
  if (existing) existing.remove();

  const operator = resolveWilsyLeadCommandOperator();
  const ownership = resolveWilsyLeadOwnershipPosture(record);
  const compliance = resolveWilsyLeadValue(record, 'compliance').toUpperCase();
  const authorityNarrative = buildWilsyLeadAuthorityNarrative({ ownership, compliance });
  const titleMap = {
    view: 'Lead Command View',
    proof: 'Complete Proof Trail',
    edit: 'Governed Edit',
    delete: 'Delete Governance',
    changeOwner: 'Ownership Governance',
    massUpdate: 'Mass Update Governance'
  };
  const title = titleMap[mode] || 'Lead Command View';

  const overlay = createWilsyLeadNode('section');
  overlay.id = 'wilsy-r91g1-lead-inspection-overlay';
  overlay.setAttribute('role', 'dialog');
  overlay.setAttribute('aria-modal', 'true');

  const orbit = createWilsyLeadNode('aside', 'wlcc-orbit');
  orbit.append(createWilsyLeadNode('strong', '', 'SOVEREIGN LEAD INTELLIGENCE'));
  orbit.append(createWilsyLeadNode('span', '', 'Sealed request • role decision • audit receipt • proof trail • next best action'));

  const drawer = createWilsyLeadNode('aside', 'wlcc-drawer');
  const top = createWilsyLeadNode('header', 'wlcc-top');
  const titleWrap = createWilsyLeadNode('div');
  titleWrap.append(createWilsyLeadNode('span', 'wlcc-pill', 'Governed Revenue Command Capsule'));
  titleWrap.append(createWilsyLeadNode('h2', '', title));
  titleWrap.append(createWilsyLeadNode('p', '', 'Every action is role-aware, tenant-aware, reason-aware and receipt-aware. WILSY OS does not hide denial, silence or missing evidence.'));
  const close = createWilsyLeadNode('button', 'wlcc-close', 'Close');
  close.type = 'button';
  close.addEventListener('click', () => overlay.remove());
  top.append(titleWrap, close);
  drawer.append(top);

  const overview = createWilsyLeadNode('section', 'wlcc-grid');
  appendWilsyLeadCard(overview, 'Lead name', resolveWilsyLeadValue(record, 'name'));
  appendWilsyLeadCard(overview, 'Company', resolveWilsyLeadValue(record, 'company'));
  appendWilsyLeadCard(overview, 'Email', resolveWilsyLeadValue(record, 'email'));
  appendWilsyLeadCard(overview, 'Phone', resolveWilsyLeadValue(record, 'phone'));
  appendWilsyLeadCard(overview, 'Owner', resolveWilsyLeadValue(record, 'owner'));
  appendWilsyLeadCard(overview, 'Status', resolveWilsyLeadValue(record, 'status'));
  drawer.append(overview);

  const verdict = createWilsyLeadNode('section', 'wlcc-panel');
  verdict.append(createWilsyLeadNode('h3', '', 'Why this action is allowed or blocked'));
  verdict.append(createWilsyLeadNode('p', '', authorityNarrative.summary));
  const status = createWilsyLeadNode('p', 'wlcc-status', 'Recording access receipt...');
  verdict.append(status);

  const actions = createWilsyLeadNode('div', 'wlcc-actions');
  const receiptButton = createWilsyLeadNode('button', 'wlcc-secondary', 'Record access receipt');
  receiptButton.type = 'button';
  receiptButton.addEventListener('click', async event => {
    event.preventDefault();
    receiptButton.disabled = true;
    status.textContent = 'Recording action receipt...';

    try {
      const payload = await requestWilsyLeadActionReceipt({
        apiBase,
        tenantId,
        recordId,
        action: `${String(mode).toUpperCase()}_OPENED`,
        mode,
        metadata: { label, selectedRecords: recordIds.length || 1 }
      });
      renderWilsyLeadReasonBox(status, payload);
    } catch (error) {
      renderWilsyLeadReasonBox(status, error.payload || buildWilsyLeadNetworkFailurePayload(error, { apiBase, recordId, commandPath: 'action-receipt' }));
    } finally {
      receiptButton.disabled = false;
    }
  });
  actions.append(receiptButton);

  const complianceButton = createWilsyLeadNode('button', 'wlcc-primary', 'Execute compliance review action');
  complianceButton.type = 'button';
  complianceButton.addEventListener('click', async event => {
    event.preventDefault();
    complianceButton.disabled = true;
    status.textContent = 'Executing compliance review command...';

    try {
      const payload = await executeWilsyLeadMutation({
        apiBase,
        tenantId,
        recordId,
        method: 'PATCH',
        action: 'COMPLIANCE_REVIEW_REQUESTED',
        lead: {
          stage: resolveWilsyLeadValue(record, 'status'),
          metadata: {
            ...(record.metadata || {}),
            wilsyNextBestAction: 'COMPLIANCE_REVIEW_REQUESTED',
            reason: 'Compliance was pending and required an executable review path.',
            executedAt: new Date().toISOString()
          }
        }
      });
      renderWilsyLeadReasonBox(status, payload);
    } catch (error) {
      renderWilsyLeadReasonBox(status, error.payload || buildWilsyLeadNetworkFailurePayload(error, { apiBase, recordId, commandPath: 'compliance-review' }));
    } finally {
      complianceButton.disabled = false;
    }
  });
  actions.append(complianceButton);

  if (mode === 'delete') {
    const deleteButton = createWilsyLeadNode('button', 'wlcc-danger', 'Execute protected delete');
    deleteButton.type = 'button';
    deleteButton.addEventListener('click', async event => {
      event.preventDefault();
      deleteButton.disabled = true;
      status.textContent = 'Executing protected delete. Backend authority will decide.';

      try {
        const payload = await executeWilsyLeadMutation({
          apiBase,
          tenantId,
          recordId,
          method: 'DELETE',
          route: wilsyR91K24ECommandPayload?.route,
        }); /* R91K179E24P58J_DELETE_ROUTE_PASSED */
        renderWilsyLeadReasonBox(status, payload);
      } catch (error) {
        renderWilsyLeadReasonBox(status, error.payload || buildWilsyLeadNetworkFailurePayload(error, { apiBase, recordId, commandPath: 'protected-delete' }));
      } finally {
        deleteButton.disabled = false;
      }
    });
    actions.append(deleteButton);
  }

  verdict.append(actions);
  drawer.append(verdict);

  if (mode === 'edit' || mode === 'massUpdate' || mode === 'changeOwner') {
    const editPanel = createWilsyLeadNode('section', 'wlcc-panel');
    editPanel.append(createWilsyLeadNode('h3', '', mode === 'changeOwner' ? 'Ownership Governance' : 'Governed Edit Command'));
    editPanel.append(createWilsyLeadNode('p', '', mode === 'changeOwner'
      ? 'Ownership transfer is admin-governed. A tenant user receives a recorded denial with reasons and next-best action.'
      : 'Edit fields are live. Save executes a sealed PATCH. Backend authority explains approval or denial.'
    ));

    const form = createWilsyLeadNode('form', 'wlcc-form');
    [
      ['fullName', 'Lead name', resolveWilsyLeadValue(record, 'name')],
      ['companyName', 'Company', resolveWilsyLeadValue(record, 'company')],
      ['email', 'Email', resolveWilsyLeadValue(record, 'email')],
      ['phone', 'Phone', resolveWilsyLeadValue(record, 'phone')],
      ['stage', 'Status', resolveWilsyLeadValue(record, 'status')]
    ].forEach(([name, fieldLabel, value]) => {
      const field = createWilsyLeadNode('label');
      field.append(createWilsyLeadNode('span', '', fieldLabel));
      const input = document.createElement('input');
      input.name = name;
      input.value = String(value || '').replace(/^—$/, '');
      input.placeholder = 'Source silent';
      field.append(input);
      form.append(field);
    });

    const save = createWilsyLeadNode('button', 'wlcc-primary', mode === 'changeOwner' ? 'Request owner change' : 'Save governed edit');
    save.type = 'button';
    save.addEventListener('click', async event => {
      event.preventDefault();
      save.disabled = true;
      status.textContent = 'Recording edit attempt and executing sealed command...';

      try {
        await requestWilsyLeadActionReceipt({
          apiBase,
          tenantId,
          recordId,
          action: mode === 'changeOwner' ? 'CHANGE_OWNER_ATTEMPTED' : 'EDIT_SAVE_ATTEMPTED',
          mode,
          metadata: { source: 'WILSY_LEAD_COMMAND_CAPSULE' }
        });

        const payload = await executeWilsyLeadMutation({
          apiBase,
          tenantId,
          recordId,
          method: 'PATCH',
          action: mode === 'changeOwner' ? 'CHANGE_OWNER' : 'UPDATE',
          lead: mode === 'changeOwner'
            ? { owner: form.querySelector('[name="fullName"]')?.value || '', metadata: { reason: 'Owner change requested from capsule.' } }
            : buildWilsyLeadEditPayload(form, record)
        });

        renderWilsyLeadReasonBox(status, payload);
      } catch (error) {
        renderWilsyLeadReasonBox(status, error.payload || buildWilsyLeadNetworkFailurePayload(error, { apiBase, recordId, commandPath: mode === 'changeOwner' ? 'change-owner' : 'governed-edit' }));
      } finally {
        save.disabled = false;
      }
    });

    editPanel.append(form, save);
    drawer.append(editPanel);
  }

  const proofPanel = createWilsyLeadNode('section', 'wlcc-panel');
  proofPanel.append(createWilsyLeadNode('h3', '', 'Complete Proof Trail'));
  proofPanel.append(createWilsyLeadNode('p', '', 'This lists source fields, source silence, ownership evidence, audit trail entries, and live receipt outcomes. Proof is not decoration; it is the operating memory of the Lead.'));
  const proofGrid = createWilsyLeadNode('div', 'wlcc-proof');

  const proofRows = [
    { label: 'Record ID', value: recordId },
    { label: 'Tenant ID', value: tenantId },
    { label: 'Operator role', value: operator.role },
    { label: 'Operator ID', value: operator.operatorId },
    { label: 'Operator email', value: operator.operatorEmail },
    { label: 'Ownership posture', value: ownership.reason },
    { label: 'Ownership evidence', value: ownership.ownerEvidence },
    { label: 'Compliance status', value: compliance },
    { label: 'Source system', value: resolveWilsyLeadValue(record, 'source') },
    { label: 'Provenance hash', value: resolveWilsyLeadValue(record, 'provenance') },
    ...flattenWilsyLeadProofRows(record)
  ];

  const seen = new Set();
  proofRows.forEach(item => {
    const labelText = String(item.label || 'Source field');
    const key = labelText.toLowerCase();
    if (seen.has(key)) return;
    seen.add(key);
    appendWilsyLeadCard(proofGrid, labelText, item.value, resolveWilsyLeadProofValue(item.value).includes('SOURCE SILENT') ? 'warning' : 'neutral');
  });

  proofPanel.append(proofGrid);
  drawer.append(proofPanel);

  overlay.append(orbit, drawer);
  overlay.addEventListener('click', event => {
    if (event.target === overlay) overlay.remove();
  });

  document.body.appendChild(overlay);
  repairR91K20AAuthorityNarrative(overlay, { record, tenantId, ownership: typeof ownership !== "undefined" ? ownership : {} });

  window.requestAnimationFrame(() => {
    drawer.scrollTop = 0;
    overlay.scrollTop = 0;
    drawer.classList.add('wlcc-r91k9-ready');
  });

  receiptButton.click();
}

/**
 * R91K.12C BACKEND RECEIPT REVIEW VISIBILITY BRIDGE
 */

/**
 * @function ensureR91K12CBackendReceiptReviewDesign
 * @description Adds visible receipt and proof styling for backend-backed lead command results after review, receipt, delete, owner transfer, and mass-update actions.
 * @collaboration Supports the CRM lead command capsule without replacing server-side authority or audit receipt logic.
 */
function ensureR91K12CBackendReceiptReviewDesign() {
  if (typeof document === "undefined") {
    return;
  }

  const styleId = "wilsy-r91k12c-backend-receipt-review-design";

  if (document.getElementById(styleId)) {
    return;
  }

  const style = document.createElement("style");
  style.id = styleId;
  style.textContent = [
    "[data-r91k12c-command-review-surface='visible'] {",
    "  border: 1px solid rgba(16, 185, 129, 0.52) !important;",
    "  border-left: 6px solid rgba(16, 185, 129, 0.96) !important;",
    "  border-radius: 18px !important;",
    "  box-shadow: 0 18px 60px rgba(16, 185, 129, 0.18) !important;",
    "  display: block !important;",
    "  margin: 18px 0 !important;",
    "  padding: 18px 20px !important;",
    "  white-space: normal !important;",
    "}",
    "[data-r91k12c-command-review-surface='visible']::before {",
    "  content: 'BACKEND RECEIPT SURFACE';",
    "  display: block;",
    "  font-size: 11px;",
    "  font-weight: 900;",
    "  letter-spacing: 0.18em;",
    "  margin-bottom: 10px;",
    "  opacity: 0.72;",
    "}",
  ].join("\n");

  document.head.appendChild(style);
}

/**
 * @function installR91K12CBackendReceiptReviewBridge
 * @description Scrolls backend command results into view when operators click receipt, compliance review, proof, delete, owner-transfer, or mass-update controls.
 * @collaboration Gives the Lead Operating Room a visible backend-backed result surface while preserving the existing command handlers.
 */
function installR91K12CBackendReceiptReviewBridge() {
  if (typeof document === "undefined" || typeof window === "undefined" || typeof Element === "undefined") {
    return;
  }

  if (document.documentElement.dataset.wilsyR91K12CReceiptBridge === "installed") {
    return;
  }

  document.documentElement.dataset.wilsyR91K12CReceiptBridge = "installed";

  document.addEventListener(
    "click",
    (event) => {
      const target = event.target instanceof Element ? event.target : null;
      const button = target ? target.closest("button") : null;
      const label = button && button.textContent ? button.textContent.replace(/\s+/g, " ").trim() : "";

      if (!/Record access receipt|Execute compliance review action|Delete Lead|Delete Selected|Change Owner|Mass Update|Proof Trail/i.test(label)) {
        return;
      }

      window.setTimeout(() => {
        const capsule =
          button.closest("[data-r91k-lead-command-capsule], [data-wilsy-lead-command-capsule], [class*='LeadCommand'], [class*='leadCommand']") ||
          document.body;

        const nodes = Array.from(capsule.querySelectorAll("p, div, section, article"));
        const receiptNode = nodes.find((node) => {
          const text = node.textContent ? node.textContent.replace(/\s+/g, " ").trim() : "";

          return /Result:\s*|Receipt:\s*|COMMAND_FAILED|DB_PERSISTED|NO_RECEIPT_HASH|Proof Trail|audit posture|source fields|source silence/i.test(text) &&
            /Why:\s*|Next:\s*|Proof|Audit|Source|Receipt/i.test(text);
        });

        if (!receiptNode) {
          return;
        }

        receiptNode.setAttribute("data-r91k12c-command-review-surface", "visible");
        receiptNode.scrollIntoView({
          block: "center",
          behavior: "smooth",
        });
      }, 650);
    },
    true
  );
}

if (typeof window !== "undefined") {
  window.requestAnimationFrame(() => {
    ensureR91K12CBackendReceiptReviewDesign();
    installR91K12CBackendReceiptReviewBridge();
  });
}
