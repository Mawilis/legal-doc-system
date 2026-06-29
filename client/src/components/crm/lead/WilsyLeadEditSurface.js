/* eslint-disable */

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

import {
  WILSY_LEAD_TITLE_OPTIONS,
  normalizeWilsyLeadTitleValue,
} from '../../../data/wilsyLeadTitleOptions';

import {
  WILSY_LEAD_INDUSTRY_OPTIONS,
  normalizeWilsyLeadIndustryValue,
} from '../../../data/wilsyLeadIndustryOptions';

/**
 * @function normalizeWilsyLeadEditDbGatewayText
 * @description Normalizes Edit gateway text values before DB persistence.
 * @param {unknown} value - Candidate value.
 * @returns {string} Clean string value.
 * @collaboration Lead Edit DB_PERSISTED gateway, backend Lead CRUD route, edit form field collection.
 */
function normalizeWilsyLeadEditDbGatewayText(value) {
  if (value === null || value === undefined) {
    return '';
  }

  return String(value).trim();
}

/**
 * @function readWilsyLeadEditDbGatewayAuthToken
 * @description Reads the current browser auth token for DB_PERSISTED Edit save requests without creating browser-exposed secrets.
 * @returns {string} Bearer token candidate or an empty string.
 * @collaboration Lead Edit DB_PERSISTED gateway, authenticated CRM Lead PATCH route, sovereign browser session.
 */
function readWilsyLeadEditDbGatewayAuthToken() {
  try {
    return localStorage.getItem('token')
      || localStorage.getItem('authToken')
      || localStorage.getItem('wilsyToken')
      || localStorage.getItem('wilsy_token')
      || '';
  } catch {
    return '';
  }
}

/**
 * @function collectWilsyLeadEditDbPersistedPayload
 * @description Collects the current Edit Lead form payload for direct DB_PERSISTED persistence without using the command receipt path.
 * @param {Object} payloadContext - Edit surface payload context.
 * @param {HTMLElement} root - Edit surface root.
 * @returns {Object} Normalized Lead update payload.
 * @collaboration WilsyLeadEditSurface, collectWilsyLeadEditPayload, backend Lead PATCH /api/crm/command/leads/:id.
 */
function collectWilsyLeadEditDbPersistedPayload(payloadContext = {}, root = null) {
  const originalRecord = payloadContext?.record || payloadContext?.lead || payloadContext?.data?.record || payloadContext?.data?.lead || {};
  const payloadCandidates = [];

  if (typeof collectWilsyLeadEditPayload === 'function') {
    const candidateCalls = [
      () => collectWilsyLeadEditPayload(payloadContext),
      () => collectWilsyLeadEditPayload(originalRecord),
      () => collectWilsyLeadEditPayload(originalRecord, root),
      () => collectWilsyLeadEditPayload(payloadContext, root)
    ];

    for (const candidateCall of candidateCalls) {
      try {
        const candidatePayload = candidateCall();

        if (candidatePayload && typeof candidatePayload === 'object' && !Array.isArray(candidatePayload)) {
          payloadCandidates.push(candidatePayload);
        }
      } catch {
        // Continue through guarded fallback collection.
      }
    }
  }

  const domPayload = {};

  if (root && typeof root.querySelectorAll === 'function') {
    const controls = Array.from(root.querySelectorAll('input, select, textarea'));

    for (const control of controls) {
      const rawValue = control.type === 'checkbox' ? control.checked : control.value;
      const value = typeof rawValue === 'boolean' ? rawValue : normalizeWilsyLeadEditDbGatewayText(rawValue);

      if (value === '') {
        continue;
      }

      const directName = normalizeWilsyLeadEditDbGatewayText(
        control.getAttribute('name')
        || control.getAttribute('data-field')
        || control.getAttribute('data-name')
        || control.getAttribute('aria-label')
        || control.getAttribute('placeholder')
        || control.id
        || ''
      ).toLowerCase();

      const nearbyText = normalizeWilsyLeadEditDbGatewayText(
        control.closest('label')?.textContent
        || control.parentElement?.querySelector('label')?.textContent
        || control.parentElement?.previousElementSibling?.textContent
        || control.parentElement?.textContent
        || ''
      ).toLowerCase();

      const signal = [directName, nearbyText].join(' ');

      if (signal.includes('lead name') || signal.includes('name *')) {
        domPayload.name = value;
        domPayload.fullName = value;
        domPayload.leadName = value;
      } else if (signal.includes('company')) {
        domPayload.company = value;
        domPayload.companyName = value;
      } else if (signal.includes('email')) {
        domPayload.email = value;
      } else if (signal.includes('mobile')) {
        domPayload.mobile = value;
      } else if (signal.includes('phone')) {
        domPayload.phone = value;
      } else if (signal.includes('title')) {
        domPayload.title = value;
        domPayload.decisionMakerTitle = value;
      } else if (signal.includes('status')) {
        domPayload.status = value;
        domPayload.leadStatus = value;
      } else if (signal.includes('stage')) {
        domPayload.stage = value;
        domPayload.leadStage = value;
      } else if (signal.includes('source')) {
        domPayload.source = value;
        domPayload.leadSource = value;
      } else if (signal.includes('industry')) {
        domPayload.industry = value;
        domPayload.businessIndustry = value;
      } else if (signal.includes('owner')) {
        domPayload.ownerName = value;
        domPayload.assignedToName = value;
        domPayload.wilsyResolvedOwnerLabel = value;
      } else if (signal.includes('value') || signal.includes('deal')) {
        domPayload.value = value;
        domPayload.dealValue = value;
        domPayload.estimatedDealValue = value;
      }
    }
  }

  const mergedPayload = Object.assign(
    {},
    originalRecord,
    ...payloadCandidates,
    ...payloadCandidates.map(candidate => candidate?.lead || {}).filter(Boolean),
    domPayload
  );

  const recordId = normalizeWilsyLeadEditDbGatewayText(
    payloadContext?.recordId
    || payloadContext?.leadId
    || payloadContext?.id
    || mergedPayload?._id
    || mergedPayload?.id
    || mergedPayload?.leadId
    || mergedPayload?.recordId
    || originalRecord?._id
    || originalRecord?.id
    || originalRecord?.leadId
    || originalRecord?.recordId
    || ''
  );

  if (recordId) {
    mergedPayload.recordId = recordId;
    mergedPayload.leadId = recordId;
  }

  mergedPayload.wilsyPersistenceContract = 'R91K_EDIT_DB_PERSISTED_SAVE_GATEWAY';
  mergedPayload.wilsySaveSurface = 'WilsyLeadEditSurface';

  return mergedPayload;
}

/**
 * @function renderWilsyLeadEditDbPersistedGatewayStatus
 * @description Renders the authoritative Edit save result inside the Edit surface.
 * @param {HTMLElement} root - Edit surface root.
 * @param {string} message - Result message.
 * @param {string} tone - Visual tone.
 * @returns {void}
 * @collaboration Lead Edit save button, DB_PERSISTED route response, operator-facing save evidence.
 */
function renderWilsyLeadEditDbPersistedGatewayStatus(root = null, message = '', tone = 'info') {
  if (!root || typeof document === 'undefined') {
    return;
  }

  let statusNode = root.querySelector('[data-wilsy-edit-db-persisted-save-status="true"]');

  if (!statusNode) {
    statusNode = document.createElement('div');
    statusNode.setAttribute('data-wilsy-edit-db-persisted-save-status', 'true');
    statusNode.style.marginTop = '18px';
    statusNode.style.padding = '16px 18px';
    statusNode.style.borderRadius = '16px';
    statusNode.style.border = '1px solid rgba(0,255,148,0.28)';
    statusNode.style.background = 'rgba(2, 8, 18, 0.88)';
    statusNode.style.color = '#d8e4f4';
    statusNode.style.fontWeight = '800';
    statusNode.style.letterSpacing = '0.02em';
    statusNode.style.boxShadow = 'inset 4px 0 0 rgba(0,255,148,0.72)';
    root.appendChild(statusNode);
  }

  statusNode.style.borderColor = tone === 'error' ? 'rgba(255,75,75,0.42)' : 'rgba(0,255,148,0.28)';
  statusNode.style.boxShadow = tone === 'error' ? 'inset 4px 0 0 rgba(255,75,75,0.78)' : 'inset 4px 0 0 rgba(0,255,148,0.72)';
  statusNode.textContent = message;
}

/**
 * @function attachWilsyLeadEditDbPersistedSaveGateway
 * @description Attaches the DB_PERSISTED save gateway to the active Edit Lead surface without using command receipt persistence.
 * @param {Object} payloadContext - Edit surface payload context.
 * @param {number} attempts - Retry attempts while the Edit surface is rendering.
 * @returns {void}
 * @collaboration WilsyLeadEditSurface, Save button capture, backend Lead PATCH route.
 */
function attachWilsyLeadEditDbPersistedSaveGateway(payloadContext = {}, attempts = 0) {
  if (typeof document === 'undefined') {
    return;
  }

  const candidateRoots = Array.from(document.querySelectorAll('main, section, article, div'))
    .filter((node) => {
      const text = String(node.textContent || '');
      return text.includes('Edit Lead') && text.includes('Lead Information');
    })
    .sort((left, right) => String(left.textContent || '').length - String(right.textContent || '').length);

  const root = candidateRoots[0];

  if (!root) {
    if (attempts < 30) {
      window.setTimeout(() => attachWilsyLeadEditDbPersistedSaveGateway(payloadContext, attempts + 1), 80);
    }

    return;
  }

  if (root.getAttribute('data-wilsy-edit-db-persisted-save-gateway') === 'true') {
    return;
  }

  root.setAttribute('data-wilsy-edit-db-persisted-save-gateway', 'true');

  root.addEventListener('click', async (event) => {
    const button = event.target?.closest?.('button');

    if (!button) {
      return;
    }

    const buttonText = normalizeWilsyLeadEditDbGatewayText(button.textContent || '');

    if (!/^save$/i.test(buttonText) && !/^save changes$/i.test(buttonText) && !/^update lead$/i.test(buttonText)) {
      return;
    }

    event.preventDefault();
    event.stopPropagation();
    event.stopImmediatePropagation?.();

    button.disabled = true;

    const previousButtonText = button.textContent;
    button.textContent = 'Saving...';

    try {
      const updatePayload = collectWilsyLeadEditDbPersistedPayload(payloadContext, root);
      const recordId = normalizeWilsyLeadEditDbGatewayText(updatePayload.recordId || updatePayload.leadId || updatePayload._id || updatePayload.id || '');

      if (!recordId) {
        throw new Error('CRM_LEAD_ID_REQUIRED: Edit save cannot persist without a Lead record id.');
      }

      const viteApiBase = normalizeWilsyLeadEditDbGatewayText(import.meta.env?.VITE_API_URL || '');
      const apiBase = viteApiBase.replace(/\/$/, '');
      const endpoint = `${apiBase}/api/crm/command/leads/${encodeURIComponent(recordId)}`;

      const tenantId = normalizeWilsyLeadEditDbGatewayText(
        updatePayload.tenantId
        || updatePayload.tenant
        || payloadContext?.tenantId
        || payloadContext?.tenant
        || 'MASTER'
      );

      const tokenCandidate = readWilsyLeadEditDbGatewayAuthToken();

      const headers = {
        'Content-Type': 'application/json',
        'X-Tenant-Id': tenantId
      };

      if (tokenCandidate) {
        headers.Authorization = tokenCandidate.startsWith('Bearer ') ? tokenCandidate : `Bearer ${tokenCandidate}`;
      }

      const body = {
        ...updatePayload,
        lead: {
          ...updatePayload,
          _id: recordId,
          id: recordId
        },
        recordId,
        leadId: recordId,
        tenantId,
        tenant: tenantId,
        wilsyPersistenceContract: 'R91K_EDIT_DB_PERSISTED_SAVE_GATEWAY'
      };

      const response = await fetch(endpoint, {
        method: 'PATCH',
        headers,
        body: JSON.stringify(body)
      });

      let responseBody = {};

      try {
        responseBody = await response.json();
      } catch {
        responseBody = {};
      }

      const statusText = normalizeWilsyLeadEditDbGatewayText(
        responseBody.status
        || responseBody.result
        || responseBody.persistenceStatus
        || ''
      ).toUpperCase();

      const rejectedCommandReceipt = statusText.includes('COMMAND_RECORDED')
        || statusText.includes('ACTION_RECORDED')
        || statusText.includes('CRM_LEAD_ACTION_RECEIPT')
        || normalizeWilsyLeadEditDbGatewayText(responseBody.receiptHash || '').toUpperCase() === 'NO_RECEIPT_HASH';

      if (!response.ok) {
        throw new Error(responseBody.message || responseBody.error || `DB save failed with HTTP ${response.status}`);
      }

      if (rejectedCommandReceipt) {
        throw new Error(`Rejected command receipt response from Edit save: ${statusText || 'UNKNOWN_STATUS'}`);
      }

      const persistedStatus = statusText.includes('DB_PERSISTED') ? statusText : 'DB_PERSISTED';
      const receiptHash = normalizeWilsyLeadEditDbGatewayText(
        responseBody.receiptHash
        || responseBody.auditReceiptHash
        || responseBody.receipt?.hash
        || responseBody.audit?.receiptHash
        || 'DB_PERSISTED_ROUTE'
      );

      const normalizedResponse = {
        ...responseBody,
        ok: true,
        status: persistedStatus,
        result: persistedStatus,
        persistenceStatus: persistedStatus,
        receiptHash,
        lead: responseBody.lead || responseBody.record || body.lead,
        record: responseBody.record || responseBody.lead || body.lead
      };

      try {
        if (typeof completeWilsyLeadEditAfterPersistence === 'function') {
          completeWilsyLeadEditAfterPersistence(normalizedResponse, body, root);
        }
      } catch {
        // DB route already succeeded. Keep operator evidence visible.
      }

      renderWilsyLeadEditDbPersistedGatewayStatus(
        root,
        `Result: ${persistedStatus} · Receipt: ${receiptHash} · Why: Lead DB record updated. · Next: Review Proof Trail after save.`,
        'success'
      );

      window.dispatchEvent(new CustomEvent('wilsy:crm-lead-updated', {
        detail: {
          status: persistedStatus,
          recordId,
          leadId: recordId,
          tenantId,
          lead: normalizedResponse.lead,
          response: normalizedResponse
        }
      }));
    } catch (error) {
      renderWilsyLeadEditDbPersistedGatewayStatus(
        root,
        `Result: DB_SAVE_FAILED · Why: ${error?.message || 'Unknown save error'}`,
        'error'
      );
    } finally {
      button.disabled = false;
      button.textContent = previousButtonText || 'Save';
    }
  }, true);
}

/**
 * @function installWilsyLeadEditDbPersistedSaveGateway
 * @description Installs the Edit Save DB gateway that persists through the backend Lead update route.
 * @param {Object} payloadContext - Edit surface payload context.
 * @returns {void}
 * @collaboration WilsyLeadEditSurface, backend PATCH /api/crm/command/leads/:id, DB_PERSISTED save contract.
 */
function installWilsyLeadEditDbPersistedSaveGateway(payloadContext = {}) {
  attachWilsyLeadEditDbPersistedSaveGateway(payloadContext, 0);
}

/**
 * @function createWilsyLeadEditNode
 * @description Creates a DOM node for the dedicated Lead Edit surface.
 * @collaboration Keeps Lead Edit independent from the legacy command capsule shell.
 */
function createWilsyLeadEditNode(tagName = 'div', className = '', text = '') {
  const node = document.createElement(tagName);

  if (className) node.className = className;
  if (text) node.textContent = text;

  return node;
}

/**
 * @function normalizeWilsyLeadEditText
 * @description Normalizes source values for safe edit rendering.
 * @collaboration Prevents source-silent proof values from polluting editable fields.
 */
function normalizeWilsyLeadEditText(value = '') {
  return String(value || '').replace(/\s+/g, ' ').trim();
}

/**
 * @function isWilsyLeadEditSourceSilent
 * @description Detects empty or source-silent field values.
 * @collaboration Keeps Proof Trail evidence separate from actionable edit controls.
 */
function isWilsyLeadEditSourceSilent(value = '') {
  const normalizedValue = normalizeWilsyLeadEditText(value).toUpperCase();

  return !normalizedValue || normalizedValue === '—' || normalizedValue === '-' || normalizedValue === 'SOURCE SILENT';
}

/**
 * @function cleanWilsyLeadEditValue
 * @description Cleans source-silent values for form controls.
 * @collaboration Keeps form controls production-ready and user-readable.
 */
function cleanWilsyLeadEditValue(value = '', fallback = '') {
  return isWilsyLeadEditSourceSilent(value) ? fallback : String(value || '');
}

/**
 * @function readWilsyLeadEditPath
 * @description Reads a dotted path from a backend Lead record.
 * @collaboration Supports normalized and raw Lead source shapes.
 */
function readWilsyLeadEditPath(record = {}, path = '') {
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
 * @function readWilsyLeadEditFirstValue
 * @description Reads the first usable value from ordered Lead field paths.
 * @collaboration Preserves backend field truth while supporting multiple CRM source shapes.
 */
function readWilsyLeadEditFirstValue(record = {}, paths = [], fallback = '') {
  for (const path of paths) {
    const value = readWilsyLeadEditPath(record, path);

    if (Array.isArray(value) && value.length) {
      return value.join(', ');
    }

    if (value && typeof value === 'object') {
      const objectValue = value.fullName || value.name || value.email || value.id || value._id || value.e164 || value.rawInput;

      if (!isWilsyLeadEditSourceSilent(objectValue)) {
        return String(objectValue);
      }
    }

    if (value !== undefined && value !== null && !isWilsyLeadEditSourceSilent(value)) {
      return String(value);
    }
  }

  return fallback;
}

/**
 * @function resolveWilsyLeadEditRecordId
 * @description Resolves the backend Lead record id for PATCH persistence.
 * @collaboration Keeps Save bound to the selected backend Lead row.
 */
function resolveWilsyLeadEditRecordId(record = {}, recordId = '') {
  return cleanWilsyLeadEditValue(
    recordId || readWilsyLeadEditFirstValue(record, ['id', '_id', 'recordId', 'sourceRecordId', 'raw._id', 'raw.id']),
    ''
  );
}

/**
 * @function resolveWilsyLeadEditTenantId
 * @description Resolves tenant id for the governed Lead edit request.
 * @collaboration Preserves multi-tenant authority headers.
 */
function resolveWilsyLeadEditTenantId(record = {}, tenantId = '') {
  return cleanWilsyLeadEditValue(
    tenantId || readWilsyLeadEditFirstValue(record, ['tenantId', 'tenant', 'raw.tenantId'], 'MASTER'),
    'MASTER'
  );
}

/**
 * @function resolveWilsyLeadEditOwnerDisplayValue
 * @description Resolves a human-readable owner value from backend Lead assignment fields.
 * @collaboration Prevents raw Owner ID exposure and surfaces actual CRM ownership evidence.
 */
function resolveWilsyLeadEditOwnerDisplayValue(record = {}) {
  const enrichedOwner =
    record.wilsyResolvedOwnerLabel ||
    record.ownerName ||
    record.assignedToName ||
    record.createdByName ||
    record.updatedByName ||
    record.raw?.ownerName ||
    record.raw?.assignedToName ||
    record.raw?.createdByName ||
    '';

  if (enrichedOwner) {
    return cleanWilsyLeadEditValue(enrichedOwner, 'Unassigned');
  }

  const owner =
    record.owner ||
    record.assignedTo ||
    record.createdBy ||
    record.raw?.owner ||
    record.raw?.assignedTo ||
    record.raw?.createdBy;

  if (owner) {
    if (typeof owner === 'string') {
      return cleanWilsyLeadEditValue(owner, 'Unassigned');
    }

    return cleanWilsyLeadEditValue(
      owner.name ||
      owner.fullName ||
      owner.displayName ||
      owner.email ||
      owner.username ||
      owner.id ||
      owner._id ||
      'Unassigned',
      'Unassigned'
    );
  }

  const operatorContext = resolveWilsyLeadEditOperatorContext();

  return cleanWilsyLeadEditValue(operatorContext.displayName || operatorContext.email || operatorContext.role, 'Unassigned');
}

/**
 * @function resolveWilsyLeadEditOwnerIdValue
 * @description Resolves persisted owner id from backend Lead assignment fields.
 * @collaboration Preserves owner identity metadata without asking operators to type raw ids.
 */
function resolveWilsyLeadEditOwnerIdValue(record = {}) {
  const enrichedOwnerId = cleanWilsyLeadEditValue(record.wilsyResolvedOwnerId, '');

  if (enrichedOwnerId) {
    return enrichedOwnerId;
  }

  const backendOwnerId = cleanWilsyLeadEditValue(
    readWilsyLeadEditFirstValue(record, [
      'ownerId',
      'owner.id',
      'owner._id',
      'assignedToId',
      'assignedTo.id',
      'assignedTo._id',
      'createdById',
      'createdBy.id',
      'createdBy._id',
      'raw.ownerId',
      'raw.assignedToId',
      'raw.createdById',
    ]),
    ''
  );

  if (backendOwnerId) {
    return backendOwnerId;
  }

  return cleanWilsyLeadEditValue(resolveWilsyLeadEditOperatorContext().id, '');
}

/**
 * @function formatWilsyLeadEditCountryLabel
 * @description Formats phone country selector labels.
 * @collaboration Uses local phone metadata for international CRM phone entry.
 */
function formatWilsyLeadEditCountryLabel(option = {}) {
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
 * @function buildWilsyLeadEditFields
 * @description Builds the production Lead Information edit registry.
 * @collaboration Mirrors CRM create density while using backend-backed selected Lead values.
 */
function buildWilsyLeadEditFields(record = {}) {
  const statusValue = normalizeWilsyLeadStatusValue(
    readWilsyLeadEditFirstValue(record, ['status', 'stage', 'raw.status', 'raw.stage'], 'PROSPECTING')
  );

  return [
    { key: 'name', label: 'Lead name', type: 'text', required: true, value: readWilsyLeadEditFirstValue(record, ['name', 'leadName', 'fullName', 'raw.fullName', 'raw.name', 'raw.firstName']), placeholder: 'Enter Lead name' },
    { key: 'company', label: 'Company', type: 'text', required: true, value: readWilsyLeadEditFirstValue(record, ['company', 'companyName', 'accountName', 'raw.companyName', 'raw.company']), placeholder: 'Enter company' },
    { key: 'email', label: 'Email', type: 'email', required: true, value: readWilsyLeadEditFirstValue(record, ['email', 'primaryEmail', 'leadEmail', 'raw.email']), placeholder: 'name@company.com' },
    { key: 'phone', label: 'Phone', type: 'phone', value: readWilsyLeadEditFirstValue(record, ['phoneMeta.e164', 'phone', 'raw.phone']), placeholder: 'Phone number' },
    { key: 'mobile', label: 'Mobile', type: 'phone', value: readWilsyLeadEditFirstValue(record, ['mobileMeta.e164', 'mobile', 'mobileNumber', 'raw.mobile']), placeholder: 'Mobile number' },
    { key: 'title', label: 'Title', type: 'title', value: readWilsyLeadEditFirstValue(record, ['title', 'jobTitle', 'raw.title', 'raw.jobTitle']), placeholder: 'Choose or type decision maker title' },
    { key: 'status', label: 'Status', type: 'status', value: statusValue, placeholder: 'Select status' },
    { key: 'stage', label: 'Stage', type: 'text', value: formatWilsyLeadStatusLabel(statusValue), placeholder: 'Pipeline stage' },
    { key: 'ownerName', label: 'Owner', type: 'owner', value: resolveWilsyLeadEditOwnerDisplayValue(record), ownerId: resolveWilsyLeadEditOwnerIdValue(record), placeholder: 'Owner from backend assignment' },
    { key: 'sourceChannel', label: 'Lead source', type: 'select', value: readWilsyLeadEditFirstValue(record, ['sourceChannel', 'source', 'leadSource', 'raw.sourceChannel'], 'manual'), options: [
      { value: 'manual', label: 'Manual' },
      { value: 'website', label: 'Website' },
      { value: 'email', label: 'Email' },
      { value: 'referral', label: 'Referral' },
      { value: 'campaign', label: 'Campaign' },
      { value: 'import', label: 'Import' },
      { value: 'api', label: 'API' },
    ] },
    { key: 'priority', label: 'Priority', type: 'select', value: readWilsyLeadEditFirstValue(record, ['priority', 'raw.priority'], 'NORMAL').toUpperCase(), options: [
      { value: 'LOW', label: 'Low' },
      { value: 'NORMAL', label: 'Normal' },
      { value: 'HIGH', label: 'High' },
      { value: 'URGENT', label: 'Urgent' },
    ] },
    { key: 'value', label: 'Estimated Deal Value (ZAR)', type: 'number', value: readWilsyLeadEditFirstValue(record, ['value', 'amount', 'dealValue', 'raw.value'], '0'), placeholder: '0' },
    { key: 'score', label: 'Score', type: 'number', value: readWilsyLeadEditFirstValue(record, ['score', 'leadScore', 'raw.score'], '0'), placeholder: '0' },
    { key: 'industry', label: 'Industry', type: 'industry', value: readWilsyLeadEditFirstValue(record, ['industry', 'raw.industry']), placeholder: 'Choose industry' },
    { key: 'dueDate', label: 'Due date', type: 'date', value: readWilsyLeadEditFirstValue(record, ['dueDate', 'nextFollowUpAt', 'raw.dueDate']).slice(0, 10), placeholder: 'Due date' },
    { key: 'notes', label: 'Notes', type: 'textarea', value: readWilsyLeadEditFirstValue(record, ['notes', 'description', 'raw.notes']), placeholder: 'Operator notes' },
  ];
}

/**
 * @function resolveWilsyLeadEditFieldHelperText
 * @description Provides operator-facing helper text for ambiguous CRM Lead fields.
 * @collaboration Clarifies field intent for governed Lead editing, proof trail review, and CRM pipeline consistency.
 */
/**
 * @function resolveWilsyLeadEditFieldHelperText
 * @description Provides operator-facing helper text for ambiguous CRM Lead fields.
 * @collaboration Clarifies field intent for governed Lead editing, proof trail review, due-date governance, and CRM pipeline consistency.
 */
function resolveWilsyLeadEditFieldHelperText(field = {}) {
  const key = String(field.key || field.name || field.id || '').toLowerCase();
  const label = String(field.label || '').toLowerCase();

  if (key === 'value' || key === 'dealvalue' || key === 'opportunityvalue' || label.includes('deal value')) {
    return 'Enter expected revenue if this Lead converts. WILSY stores the clean number and shows the formatted money value.';
  }

  if (key === 'duedate' || key === 'due_date' || label.includes('due date')) {
    return 'Follow-up deadline for this Lead. This saves the deadline; in-app/email reminders require the notification worker to be wired next.';
  }

  if (key === 'score' || label === 'score') {
    return 'Lead quality score used for prioritisation. Higher score means stronger conversion potential.';
  }

  return '';
}

/**
 * @function renderWilsyLeadEditSelectControl
 * @description Renders a controlled select field.
 * @collaboration Keeps CRM values governed and less tedious to enter.
 */
function renderWilsyLeadEditSelectControl(field = {}) {
  const select = createWilsyLeadEditNode('select', 'wilsyLeadEditControl');
  select.dataset.wilsyLeadEditKey = field.key;
  select.setAttribute('aria-label', field.label);

  const options = field.type === 'status'
    ? WILSY_LEAD_STATUS_OPTIONS.map((option) => ({ value: option.value, label: option.label }))
    : field.options || [];

  options.forEach((option) => {
    const optionNode = createWilsyLeadEditNode('option', '', option.label);
    optionNode.value = option.value;

    if (String(option.value).toUpperCase() === String(field.value || '').toUpperCase()) {
      optionNode.selected = true;
    }

    select.appendChild(optionNode);
  });

  return select;
}

/**
 * @function renderWilsyLeadEditTitleControl
 * @description Renders a preloaded title chooser with custom text support.
 * @collaboration Reduces repetitive role typing while preserving real-world custom titles.
 */
function renderWilsyLeadEditTitleControl(field = {}) {
  const deck = createWilsyLeadEditNode('div', 'wilsyLeadEditTitleDeck');
  const input = createWilsyLeadEditNode('input', 'wilsyLeadEditControl');
  const datalist = createWilsyLeadEditNode('datalist', '');

  datalist.id = 'wilsy-lead-edit-title-options';
  input.dataset.wilsyLeadEditKey = field.key;
  input.type = 'text';
  input.setAttribute('list', datalist.id);
  input.value = normalizeWilsyLeadTitleValue(cleanWilsyLeadEditValue(field.value, ''));
  input.placeholder = field.placeholder || 'Choose or type decision maker title';
  input.setAttribute('aria-label', field.label);

  WILSY_LEAD_TITLE_OPTIONS.forEach((title) => {
    const option = createWilsyLeadEditNode('option', '');
    option.value = title;
    datalist.appendChild(option);
  });

  deck.append(input, datalist);


  return deck;
}

/**
 * @function renderWilsyLeadEditOwnerControl
 * @description Renders backend-resolved owner display with hidden owner id.
 * @collaboration Pulls assignment evidence from backend Lead data instead of forcing raw Owner ID input.
 */
function renderWilsyLeadEditOwnerControl(field = {}) {
  const deck = createWilsyLeadEditNode('div', 'wilsyLeadEditOwnerDeck');
  const select = createWilsyLeadEditNode('select', 'wilsyLeadEditControl');
  const hidden = createWilsyLeadEditNode('input', '');
  const operatorContext = resolveWilsyLeadEditOperatorContext();
  const fallbackOwner = operatorContext.displayName || operatorContext.name || operatorContext.email || operatorContext.role || 'Current operator';
  const rawOwner = cleanWilsyLeadEditValue(field.value, '');
  const currentOwner = rawOwner && rawOwner !== 'Unassigned' && !rawOwner.includes('@') ? rawOwner : fallbackOwner;
  const currentOwnerId = cleanWilsyLeadEditValue(field.ownerId, operatorContext.id || '');

  select.dataset.wilsyLeadEditKey = 'ownerName';
  select.setAttribute('aria-label', field.label);

  [
    { label: currentOwner, value: currentOwner },
    { label: fallbackOwner, value: fallbackOwner },
    { label: 'Unassigned', value: 'Unassigned' },
  ]
    .filter((option, index, options) => option.value && options.findIndex((item) => item.value === option.value) === index)
    .forEach((option) => {
      const optionNode = createWilsyLeadEditNode('option', '', option.label);
      optionNode.value = option.value;

      if (option.value === currentOwner) {
        optionNode.selected = true;
      }

      select.appendChild(optionNode);
    });

  hidden.dataset.wilsyLeadEditKey = 'ownerId';
  hidden.type = 'hidden';
  hidden.value = currentOwnerId;

  deck.append(select, hidden);

  return deck;
}

/**
 * @function renderWilsyLeadEditIndustryControl
 * @description Renders a real visible industry dropdown.
 * @collaboration Makes industry selection production-ready and faster than raw typing.
 */
function renderWilsyLeadEditIndustryControl(field = {}) {
  const currentValue = cleanWilsyLeadEditValue(field.value, '');
  const normalizedCurrent = currentValue && currentValue !== 'Choose industry' ? currentValue : '';
  const wrapper = createWilsyLeadEditNode('div', 'wilsyLeadEditIndustryGovernance');

  if (normalizedCurrent) {
    const locked = createWilsyLeadEditNode('div', 'wilsyLeadEditLockedField', normalizedCurrent);
    const lockNote = createWilsyLeadEditNode(
      'p',
      'wilsyLeadEditFieldHelper',
      'Industry is locked after first save because a company normally does not change industry. Use a governed reclassification workflow if this is wrong.'
    );
    const hidden = createWilsyLeadEditNode('input', '');

    hidden.type = 'hidden';
    hidden.dataset.wilsyLeadEditKey = field.key || 'industry';
    hidden.value = normalizedCurrent;

    wrapper.append(locked, lockNote, hidden);

    return wrapper;
  }

  const select = createWilsyLeadEditNode('select', 'wilsyLeadEditControl');
  select.dataset.wilsyLeadEditKey = field.key || 'industry';
  select.setAttribute('aria-label', field.label || 'Industry');

  const placeholder = createWilsyLeadEditNode('option', '', 'Choose industry');
  placeholder.value = '';
  select.appendChild(placeholder);

  WILSY_LEAD_INDUSTRY_OPTIONS.forEach((option) => {
    const optionNode = createWilsyLeadEditNode('option', '', option.label || option);
    optionNode.value = option.value || option.label || option;

    if (optionNode.value === normalizedCurrent) {
      optionNode.selected = true;
    }

    select.appendChild(optionNode);
  });

  wrapper.appendChild(select);

  return wrapper;
}

/**
 * @function renderWilsyLeadEditPhoneControl
 * @description Renders a country-aware phone editor from local metadata.
 * @collaboration Keeps phone entry international without third-party live API dependency.
 */
function renderWilsyLeadEditPhoneControl(field = {}) {
  const deck = createWilsyLeadEditNode('div', 'wilsyLeadEditPhoneDeck');
  const phoneMeta = normalizeWilsyPhoneForClient(field.value, WILSY_DEFAULT_PHONE_COUNTRY);
  const countrySelect = createWilsyLeadEditNode('select', 'wilsyLeadEditControl wilsyLeadEditCountry');
  const phoneInput = createWilsyLeadEditNode('input', 'wilsyLeadEditControl');

  countrySelect.dataset.wilsyLeadEditKey = `${field.key}CountryIso2`;
  countrySelect.setAttribute('aria-label', `${field.label} country`);

  phoneInput.dataset.wilsyLeadEditKey = field.key;
  phoneInput.type = 'tel';
  phoneInput.value = cleanWilsyLeadEditValue(formatWilsyPhoneDisplay(phoneMeta), '');
  phoneInput.placeholder = field.placeholder || 'Phone number';
  phoneInput.setAttribute('aria-label', field.label);

  getWilsyPhoneCountryOptions().forEach((option) => {
    const optionNode = createWilsyLeadEditNode('option', '', formatWilsyLeadEditCountryLabel(option));
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
 * @function renderWilsyLeadEditInputControl
 * @description Renders a text, number, date, email, or textarea control.
 * @collaboration Keeps ordinary editable fields consistent with the dedicated Lead Edit surface.
 */
function renderWilsyLeadEditInputControl(field = {}) {
  const input = createWilsyLeadEditNode(field.type === 'textarea' ? 'textarea' : 'input', 'wilsyLeadEditControl');
  input.dataset.wilsyLeadEditKey = field.key;

  if (field.type !== 'textarea') {
    input.type = field.type || 'text';
  }

  input.value = cleanWilsyLeadEditValue(field.value, '');
  input.placeholder = field.placeholder || field.label || '';
  input.setAttribute('aria-label', field.label);

  if (field.required) {
    input.required = true;
  }

  return input;
}

/**
 * @function renderWilsyLeadEditField
 * @description Renders a single Lead Edit field from the registry.
 * @collaboration Builds the production Lead Information grid from backend-backed values.
 */
function renderWilsyLeadEditField(field = {}) {
  const helperText = resolveWilsyLeadEditFieldHelperText(field);
  const helperNode = helperText ? createWilsyLeadEditNode('p', 'wilsyLeadEditFieldHelper', helperText) : null;

  const wrapper = createWilsyLeadEditNode('label', 'wilsyLeadEditField');
  const title = createWilsyLeadEditNode('span', '', `${field.label}${field.required ? ' *' : ''}`);
  let control;

  if (field.type === 'status' || field.type === 'select') {
    control = renderWilsyLeadEditSelectControl(field);
  } else if (field.type === 'title') {
    control = renderWilsyLeadEditTitleControl(field);
  } else if (field.type === 'owner') {
    control = renderWilsyLeadEditOwnerControl(field);
  } else if (field.type === 'industry') {
    control = renderWilsyLeadEditIndustryControl(field);
  } else if (field.type === 'phone') {
    control = renderWilsyLeadEditPhoneControl(field);
  } else {
    control = renderWilsyLeadEditInputControl(field);
  }

  wrapper.append(title, control);

  if (helperNode) {
    wrapper.appendChild(helperNode);
  }

  // R91K.45_FIELD_HELPER_APPEND
  return wrapper;
}

/**
 * @function collectWilsyLeadEditPayload
 * @description Collects the Lead Edit form into a backend PATCH payload.
 * @collaboration Sends normalized status, phone metadata, owner id, and governed edit fields to the CRM route.
 */
function collectWilsyLeadEditPayload(overlay) {
  const lead = {};
  const controls = Array.from(overlay.querySelectorAll('[data-wilsy-lead-edit-key]'));

  controls.forEach((node) => {
    const key = String(node.dataset.wilsyLeadEditKey || '').trim();

    if (!key) {
      return;
    }

    if (node.type === 'checkbox') {
      lead[key] = Boolean(node.checked);
      return;
    }

    lead[key] = cleanWilsyLeadEditValue(node.value, '');
  });

  /**
   * @function readFirst
   * @description Reads the first populated value from the collected Lead payload.
   * @collaboration Lead Edit payload collection, alias normalization, backend persistence contract.
   */
  function readFirst(...keys) {
    for (const key of keys) {
      const value = cleanWilsyLeadEditValue(lead[key], '');

      if (value) {
        return value;
      }
    }

    return '';
  }

  /**
   * @function readInputByIntent
   * @description Finds a rendered input by label, placeholder, aria label, or nearby field text.
   * @collaboration Supports custom controls like phone, money, and date controls that may use hidden canonical payload nodes.
   */
  function readInputByIntent(...intents) {
    const normalizedIntents = intents.map((intent) => String(intent || '').toLowerCase());

    const node = Array.from(overlay.querySelectorAll('input, textarea, select')).find((candidate) => {
      const haystack = [
        candidate.dataset?.wilsyLeadEditKey,
        candidate.name,
        candidate.id,
        candidate.placeholder,
        candidate.getAttribute('aria-label'),
        candidate.closest?.('label')?.textContent,
        candidate.closest?.('.wilsyLeadEditField')?.textContent,
      ]
        .map((value) => String(value || '').toLowerCase())
        .join(' ');

      return normalizedIntents.some((intent) => haystack.includes(intent));
    });

    return cleanWilsyLeadEditValue(node?.value, '');
  }

  /**
   * @function parseMoneyValue
   * @description Converts money-looking input into a clean numeric amount.
   * @collaboration Estimated Deal Value editor, backend numeric persistence, CRM revenue pipeline.
   */
  function parseMoneyValue(value = '') {
    const amount = Number.parseFloat(
      String(value || '')
        .replace(/[^\d.,-]/g, '')
        .replace(/,/g, '')
        .trim()
    );

    if (!Number.isFinite(amount)) {
      return 0;
    }

    return Math.max(0, Math.round(amount * 100) / 100);
  }

  /**
   * @function normalizeDialCode
   * @description Extracts an international dial code from country text or phone metadata.
   * @collaboration Phone persistence, mobile E.164 normalization, CRM contact data quality.
   */
  function normalizeDialCode(value = '') {
    const match = String(value || '').match(/\+\d{1,4}/);

    return match ? match[0] : '';
  }

  /**
   * @function normalizeMobileDigits
   * @description Normalizes a mobile value to phone-safe characters before E.164 assembly.
   * @collaboration Mobile persistence, phone alias contract, CRM contact row rendering.
   */
  function normalizeMobileDigits(value = '') {
    return String(value || '').replace(/[^\d+]/g, '').trim();
  }

  const operatorContext = resolveWilsyLeadEditOperatorContext();

  const ownerName =
    readFirst('ownerName', 'ownerDisplayName', 'ownerLabel', 'assignedToName', 'ownerDisplay', 'wilsyResolvedOwnerLabel') ||
    operatorContext.displayName ||
    operatorContext.name ||
    operatorContext.email ||
    '';

  const ownerId =
    readFirst('ownerId', 'assignedToId', 'wilsyResolvedOwnerId') ||
    operatorContext.id ||
    '';

  const statusValue =
    readFirst('status', 'leadStatus', 'stage', 'leadStage', 'pipelineStage') ||
    'New';

  const rawMobile =
    readFirst('mobileNumber', 'mobile', 'cellphone', 'cellphoneNumber', 'phoneNumber', 'phone') ||
    readInputByIntent('mobile number', 'mobile', 'cellphone', 'phone number', 'phone');

  const rawPhone =
    readFirst('phoneNumber', 'phone', 'mobileNumber', 'mobile', 'cellphone', 'cellphoneNumber') ||
    rawMobile;

  const countryText =
    readFirst('mobileCountry', 'phoneCountry', 'country', 'mobileCountryCode', 'phoneCountryCode') ||
    readInputByIntent('south africa', 'country');

  const dialCode =
    readFirst('mobileDialCode', 'phoneDialCode', 'dialCode', 'countryDialCode') ||
    normalizeDialCode(countryText) ||
    '+27';

  const mobileDigits = normalizeMobileDigits(rawMobile);
  const localMobile = mobileDigits.replace(/^\+/, '');
  const mobileE164 = mobileDigits.startsWith('+')
    ? mobileDigits
    : `${dialCode}${localMobile.replace(/^0/, '')}`;

  const dealValue = parseMoneyValue(
    readFirst('value', 'dealValue', 'estimatedDealValue', 'opportunityValue') ||
    readInputByIntent('estimated deal value', 'deal value', 'pipeline value', 'value')
  );

  const industry =
    readFirst('industry', 'businessIndustry', 'companyIndustry', 'sector') ||
    readInputByIntent('industry');

  const dueDate = readFirst('dueDate', 'due_date', 'followUpDate', 'follow_up_date') || readInputByIntent('due date');

  Object.assign(lead, {
    ownerName,
    ownerDisplayName: ownerName,
    ownerLabel: ownerName,
    displayOwner: ownerName,
    assignedToName: ownerName,
    assigneeName: ownerName,
    ownerId,
    assignedToId: ownerId,

    status: statusValue,
    leadStatus: statusValue,
    stage: statusValue,
    leadStage: statusValue,
    pipelineStage: statusValue,

    mobile: rawMobile,
    mobileNumber: rawMobile,
    cellphone: rawMobile,
    cellphoneNumber: rawMobile,
    phone: rawPhone || rawMobile,
    phoneNumber: rawPhone || rawMobile,
    contactNumber: rawPhone || rawMobile,
    mobileE164,
    phoneE164: mobileE164,
    mobileCountry: countryText || 'South Africa',
    phoneCountry: countryText || 'South Africa',
    mobileDialCode: dialCode,
    phoneDialCode: dialCode,
    phoneMeta: {
      country: countryText || 'South Africa',
      dialCode,
      localNumber: rawMobile,
      e164: mobileE164,
    },
    mobileMeta: {
      country: countryText || 'South Africa',
      dialCode,
      localNumber: rawMobile,
      e164: mobileE164,
    },

    value: dealValue,
    dealValue,
    estimatedDealValue: dealValue,
    opportunityValue: dealValue,
    valueCurrency: 'ZAR',

    industry,
    businessIndustry: industry,
    companyIndustry: industry,
    sector: industry,

    dueDate,
    followUpDate: dueDate,
    nextFollowUpDate: dueDate,

    wilsyPersistenceContract: 'R91K.51_VALUE_INDUSTRY_OWNER_CONTRACT',
  });

  return lead;
}

/**
 * @function readWilsyLeadEditStoredValue
 * @description Reads operator context from browser storage without throwing.
 * @collaboration Lets the frontend pass existing role context while backend remains authoritative.
 */
function readWilsyLeadEditStoredValue(key = '') {
  if (typeof window === 'undefined') {
    return '';
  }

  return window.localStorage?.getItem(key) || window.sessionStorage?.getItem(key) || '';
}

/**
 * @function safeWilsyLeadEditJsonParse
 * @description Safely parses browser-stored auth JSON.
 * @collaboration Extracts role context from existing auth payloads without crashing the edit surface.
 */
function safeWilsyLeadEditJsonParse(value = '') {
  try {
    return JSON.parse(value);
  } catch (error) {
    return null;
  }
}

/**
 * @function walkWilsyLeadEditObjectForKey
 * @description Finds a value in a nested object by candidate keys.
 * @collaboration Supports multiple WILSY OS account/auth payload shapes.
 */
function walkWilsyLeadEditObjectForKey(value = null, keys = []) {
  if (!value || typeof value !== 'object') {
    return '';
  }

  for (const key of keys) {
    if (value[key]) {
      return String(value[key]);
    }
  }

  for (const child of Object.values(value)) {
    const found = walkWilsyLeadEditObjectForKey(child, keys);

    if (found) {
      return found;
    }
  }

  return '';
}

/**
 * @function decodeWilsyLeadEditJwtPayload
 * @description Decodes a JWT payload without validating secrets or exposing credentials.
 * @collaboration Lets the Lead Edit surface discover operator role/name/email from existing auth tokens for UI ownership and backend role headers.
 */
function decodeWilsyLeadEditJwtPayload(token = '') {
  try {
    const cleanToken = String(token || '').replace(/^Bearer\s+/i, '').trim();
    const payload = cleanToken.split('.')[1];

    if (!payload) {
      return {};
    }

    const normalized = payload.replace(/-/g, '+').replace(/_/g, '/');
    const padded = normalized.padEnd(normalized.length + ((4 - (normalized.length % 4)) % 4), '=');
    const decoded = atob(padded);

    return JSON.parse(decoded);
  } catch (error) {
    return {};
  }
}

/**
 * @function formatWilsyLeadEditDisplayName
 * @description Formats raw identity fragments into a readable operator display name.
 * @collaboration Supports Owner display, operator fallback, and governed Lead mutation attribution.
 */
function formatWilsyLeadEditDisplayName(value = '') {
  return String(value || '')
    .replace(/[_-]+/g, ' ')
    .replace(/\s+/g, ' ')
    .trim()
    .split(' ')
    .filter(Boolean)
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1).toLowerCase())
    .join(' ');
}

/**
 * @function deriveWilsyLeadEditNameFromEmail
 * @description Derives a human-readable name when auth only exposes an email address.
 * @collaboration Prevents Owner from displaying raw email when name and surname are recoverable from account identity evidence.
 */
function deriveWilsyLeadEditNameFromEmail(email = '') {
  const localPart = String(email || '').split('@')[0].split('+')[0].trim();

  if (!localPart) {
    return '';
  }

  const separatedParts = localPart
    .replace(/\d+/g, '')
    .split(/[._\-\s]+/)
    .filter(Boolean);

  if (separatedParts.length >= 2) {
    return formatWilsyLeadEditDisplayName(separatedParts.join(' '));
  }

  const normalized = localPart.replace(/[^a-zA-Z]/g, '').toLowerCase();
  const knownFirstNames = [
    'wilson',
    'john',
    'jane',
    'michael',
    'david',
    'sarah',
    'thabo',
    'sipho',
    'nomsa',
    'lerato',
    'abo',
    'nandi',
    'peter',
    'paul',
    'mark',
    'mary',
    'anna',
  ];

  const firstName = knownFirstNames.find((candidate) => normalized.startsWith(candidate) && normalized.length > candidate.length + 2);

  if (firstName) {
    return `${formatWilsyLeadEditDisplayName(firstName)} ${formatWilsyLeadEditDisplayName(normalized.slice(firstName.length))}`;
  }

  return formatWilsyLeadEditDisplayName(normalized);
}

/**
 * @function resolveWilsyLeadEditProfileName
 * @description Resolves first name and surname from storage, JWT payload, and nested auth profile objects.
 * @collaboration Makes the Owner control use person identity before falling back to email.
 */
function resolveWilsyLeadEditProfileName(authObjects = [], tokenPayload = {}, email = '') {
  const firstName =
    readWilsyLeadEditStoredValue('firstName') ||
    readWilsyLeadEditStoredValue('givenName') ||
    readWilsyLeadEditStoredValue('given_name') ||
    tokenPayload.firstName ||
    tokenPayload.givenName ||
    tokenPayload.given_name ||
    authObjects.map((entry) => walkWilsyLeadEditObjectForKey(entry, ['firstName', 'givenName', 'given_name'])).find(Boolean) ||
    '';

  const lastName =
    readWilsyLeadEditStoredValue('lastName') ||
    readWilsyLeadEditStoredValue('surname') ||
    readWilsyLeadEditStoredValue('familyName') ||
    readWilsyLeadEditStoredValue('family_name') ||
    tokenPayload.lastName ||
    tokenPayload.surname ||
    tokenPayload.familyName ||
    tokenPayload.family_name ||
    authObjects.map((entry) => walkWilsyLeadEditObjectForKey(entry, ['lastName', 'surname', 'familyName', 'family_name'])).find(Boolean) ||
    '';

  const joinedName = formatWilsyLeadEditDisplayName([firstName, lastName].filter(Boolean).join(' '));

  if (joinedName) {
    return joinedName;
  }

  const directName =
    readWilsyLeadEditStoredValue('name') ||
    readWilsyLeadEditStoredValue('fullName') ||
    readWilsyLeadEditStoredValue('displayName') ||
    tokenPayload.name ||
    tokenPayload.fullName ||
    tokenPayload.displayName ||
    authObjects.map((entry) => walkWilsyLeadEditObjectForKey(entry, ['name', 'fullName', 'displayName'])).find(Boolean) ||
    '';

  if (directName && !String(directName).includes('@')) {
    return formatWilsyLeadEditDisplayName(directName);
  }

  return deriveWilsyLeadEditNameFromEmail(email);
}

/**
 * @function resolveWilsyLeadEditOperatorContext
 * @description Resolves role, email, and operator id from passed props and existing browser auth context.
 * @collaboration Provides the backend authority resolver with real operator evidence instead of UNKNOWN.
 */
function resolveWilsyLeadEditOperatorContext(operatorRole = '') {
  const objectKeys = [
    'currentUser',
    'user',
    'wilsyUser',
    'sovereignUser',
    'authUser',
    'tenantUser',
    'operator',
    'profile',
    'account',
    'wilsyAccount',
    'wilsyAuth',
  ];

  const authObjects = objectKeys
    .map((key) => safeWilsyLeadEditJsonParse(readWilsyLeadEditStoredValue(key)))
    .filter(Boolean);

  const tokenPayload = decodeWilsyLeadEditJwtPayload(resolveWilsyLeadEditToken());

  const role =
    operatorRole ||
    readWilsyLeadEditStoredValue('role') ||
    readWilsyLeadEditStoredValue('operatorRole') ||
    readWilsyLeadEditStoredValue('tenantRole') ||
    readWilsyLeadEditStoredValue('wilsyRole') ||
    readWilsyLeadEditStoredValue('sovereignRole') ||
    tokenPayload.role ||
    tokenPayload.tenantRole ||
    tokenPayload.operatorRole ||
    tokenPayload.userRole ||
    authObjects.map((entry) => walkWilsyLeadEditObjectForKey(entry, ['role', 'operatorRole', 'tenantRole', 'userRole', 'accessRole'])).find(Boolean) ||
    '';

  const email =
    readWilsyLeadEditStoredValue('email') ||
    readWilsyLeadEditStoredValue('operatorEmail') ||
    readWilsyLeadEditStoredValue('userEmail') ||
    tokenPayload.email ||
    tokenPayload.operatorEmail ||
    tokenPayload.userEmail ||
    authObjects.map((entry) => walkWilsyLeadEditObjectForKey(entry, ['email', 'operatorEmail', 'userEmail'])).find(Boolean) ||
    '';

  const id =
    readWilsyLeadEditStoredValue('userId') ||
    readWilsyLeadEditStoredValue('operatorId') ||
    readWilsyLeadEditStoredValue('accountId') ||
    tokenPayload.sub ||
    tokenPayload.id ||
    tokenPayload.userId ||
    tokenPayload.operatorId ||
    authObjects.map((entry) => walkWilsyLeadEditObjectForKey(entry, ['id', '_id', 'userId', 'operatorId', 'accountId'])).find(Boolean) ||
    '';

  const name = resolveWilsyLeadEditProfileName(authObjects, tokenPayload, email);

  return {
    role,
    email,
    id,
    name,
    displayName: name || email || role || 'Current operator',
    source: 'R91K.43_OPERATOR_CONTEXT_NAME_SURNAME',
  };
}

/**
 * @function resolveWilsyLeadEditToken
 * @description Resolves the active browser token used by the CRM edit route.
 * @collaboration Preserves authenticated PATCH posture without hardcoding credentials.
 */
function resolveWilsyLeadEditToken() {
  return (
    readWilsyLeadEditStoredValue('token') ||
    readWilsyLeadEditStoredValue('authToken') ||
    readWilsyLeadEditStoredValue('accessToken') ||
    readWilsyLeadEditStoredValue('wilsyToken') ||
    readWilsyLeadEditStoredValue('sovereignToken') ||
    ''
  );
}

/**
 * @function buildWilsyLeadEditHeaders
 * @description Builds authenticated headers for the Lead Edit PATCH request.
 * @collaboration Sends tenant, token, and operator role context while backend authority remains sovereign.
 */
function buildWilsyLeadEditHeaders(tenantId = '', operatorContext = {}) {
  const token = resolveWilsyLeadEditToken();
  const headers = {
    'Content-Type': 'application/json',
    'X-Tenant-Id': tenantId || 'MASTER',
    'X-Wilsy-Command-Surface': 'R91K.31_CANONICAL_LEAD_EDIT_SURFACE',
  };

  if (token) {
    headers.Authorization = ['Bearer', String(token).replace(/^Bearer\s+/i, '').trim()].join(' ');
  }

  if (operatorContext.role) {
    headers['X-Wilsy-Operator-Role'] = operatorContext.role;
    headers['X-Operator-Role'] = operatorContext.role;
  }

  if (operatorContext.email) {
    headers['X-Wilsy-Operator-Email'] = operatorContext.email;
  }

  if (operatorContext.id) {
    headers['X-Wilsy-Operator-Id'] = operatorContext.id;
  }

  return headers;
}

/**
 * @function formatWilsyLeadEditStatusLabel
 * @description Converts backend command statuses into operator-readable status labels while preserving raw status evidence.
 * @collaboration Improves CRM edit feedback without weakening receipt or audit semantics.
 */
function formatWilsyLeadEditStatusLabel(status = '') {
  const normalized = String(status || '').trim().toUpperCase();

  if (normalized === 'DB_PERSISTED') {
    return 'Saved to database';
  }

  if (normalized === 'COMMAND_API_UNREACHABLE') {
    return 'Backend command API unreachable';
  }

  if (normalized === 'CRUD_FORBIDDEN') {
    return 'Save blocked by authority policy';
  }

  return normalized || 'Command result';
}

/**
 * @function renderWilsyLeadEditStatus
 * @description Renders save status, backend reason, receipt, or transport failure.
 * @collaboration Keeps Proof Trail separate while surfacing command outcomes.
 */
function renderWilsyLeadEditStatus(statusNode, payload = {}) {
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
 * @function buildWilsyLeadEditEndpoint
 * @description Builds the Lead edit API endpoint from optional API base and record id.
 * @collaboration Supports Vite proxy and configured API hosts.
 */
function buildWilsyLeadEditEndpointCandidates(apiBase = '', recordId = '') {
  const encodedRecordId = encodeURIComponent(recordId);
  const configuredBase = String(apiBase || '').replace(/\/+$/, '');
  const envBase = String(window?.__WILSY_API_BASE__ || '').replace(/\/+$/, '');
  const candidates = [];

  if (configuredBase) {
    candidates.push(`${configuredBase}/api/crm/command/leads/${encodedRecordId}`);
  }

  if (envBase && envBase !== configuredBase) {
    candidates.push(`${envBase}/api/crm/command/leads/${encodedRecordId}`);
  }

  candidates.push(`/api/crm/command/leads/${encodedRecordId}`);
  candidates.push(`http://localhost:5050/api/crm/command/leads/${encodedRecordId}`);
  candidates.push(`http://127.0.0.1:5050/api/crm/command/leads/${encodedRecordId}`);

  return [...new Set(candidates)];
}

/**
 * @function normalizeWilsyR91K49LeadListValue
 * @description Normalizes values before applying post-save Lead list synchronization.
 * @collaboration Keeps persisted Lead values readable in the list after DB_PERSISTED without waiting for a stale reload.
 */
function normalizeWilsyR91K49LeadListValue(value = '', fallback = '') {
  const normalized = String(value ?? '').replace(/\s+/g, ' ').trim();

  return normalized || fallback;
}

/**
 * @function resolveWilsyR91K50OwnerName
 * @description Resolves a dynamic Lead owner display name from edit payload, backend response, original record, and operator context.
 * @collaboration Aligns Lead Edit, DB persistence, post-save list sync, owner assignment display, and audit receipt evidence.
 */
function resolveWilsyR91K50OwnerName(...sources) {
  /**
   * @function readPath
   * @description Reads a nested Lead value path from source payloads or records.
   * @collaboration Lead Edit alias normalization, owner resolver support, saved-record persistence mapping.
   */
  const readPath = (source = {}, path = '') => {
    const parts = String(path || '').split('.');
    let cursor = source;

    for (const part of parts) {
      cursor = cursor?.[part];
    }

    return cursor;
  };

  const ownerPaths = [
    'ownerName',
    'ownerDisplayName',
    'ownerLabel',
    'displayOwner',
    'assignedToName',
    'assigneeName',
    'responsibleOwner',
    'wilsyResolvedOwnerLabel',
    'owner.name',
    'owner.fullName',
    'owner.displayName',
    'owner.email',
    'assignedTo.name',
    'assignedTo.fullName',
    'assignedTo.displayName',
    'assignedTo.email',
    'assignee.name',
    'assignee.fullName',
    'assignee.displayName',
    'assignee.email',
    'raw.ownerName',
    'raw.ownerDisplayName',
    'raw.assignedToName',
    'raw.owner.name',
    'raw.assignedTo.name',
  ];

  for (const source of sources) {
    for (const path of ownerPaths) {
      const value = normalizeWilsyR91K49LeadListValue(readPath(source, path), '');

      if (value && value !== '—' && value.toLowerCase() !== 'unassigned') {
        return value;
      }
    }
  }

  const operatorContext = typeof resolveWilsyLeadEditOperatorContext === 'function'
    ? resolveWilsyLeadEditOperatorContext()
    : {};

  return normalizeWilsyR91K49LeadListValue(
    operatorContext.displayName ||
      operatorContext.name ||
      operatorContext.email ||
      '',
    ''
  );
}

/**
 * @function resolveWilsyR91K49LeadListPatch
 * @description Builds a canonical post-save Lead row patch from the saved edit payload and backend response.
 * @collaboration Aligns Owner, Status, Stage, Mobile, and value aliases between Edit, backend persistence, and Lead list display.
 */
function resolveWilsyR91K49LeadListPatch({ recordId = '', lead = {}, payload = {}, record = {} } = {}) {
  const responseLead = payload.lead || payload.record || payload.data?.lead || payload.data?.record || payload.data || {};
  const merged = {
    ...record,
    ...lead,
    ...responseLead,
  };

  const ownerName = resolveWilsyR91K50OwnerName(lead, responseLead, merged, record);

  const status = normalizeWilsyR91K49LeadListValue(
    merged.status ||
      merged.leadStatus ||
      merged.stage ||
      merged.leadStage ||
      merged.pipelineStage ||
      '',
    'New'
  );

  const mobile = normalizeWilsyR91K49LeadListValue(
    merged.mobileNumber ||
      merged.mobile ||
      merged.cellphone ||
      merged.cellphoneNumber ||
      merged.phoneNumber ||
      merged.phone ||
      merged.mobileMeta?.localNumber ||
      merged.phoneMeta?.localNumber ||
      ''
  );

  return {
    recordId,
    id: recordId || merged.id || merged._id || merged.leadId || '',
    ownerName,
    ownerDisplayName: ownerName,
    ownerLabel: ownerName,
    displayOwner: ownerName,
    assignedToName: ownerName,
    assigneeName: ownerName,
    status,
    leadStatus: status,
    stage: status,
    leadStage: status,
    pipelineStage: status,
    mobile,
    mobileNumber: mobile,
    cellphone: mobile,
    cellphoneNumber: mobile,
    phoneNumber: mobile || merged.phoneNumber || merged.phone || '',
    phone: mobile || merged.phone || merged.phoneNumber || '',
    source: 'R91K.50_OWNER_CONTRACT_DYNAMIC',
  };
}

/**
 * @function applyWilsyR91K49LeadListDomPatch
 * @description Applies an immediate visual patch to the selected Lead list row after a confirmed save.
 * @collaboration Prevents stale Owner and Status cells from misleading the operator while the canonical list refresh is requested.
 */
function applyWilsyR91K49LeadListDomPatch(detail = {}) {
  window.dispatchEvent(new CustomEvent('wilsy:lead-list-optimistic-patch', {
    detail: {
      ...detail,
      source: 'R91K.51_DOM_PATCH_DISABLED_MODEL_REFRESH_REQUIRED',
    },
  }));
}

/**
 * @function ensureWilsyR91K49LeadEditLayoutStyle
 * @description Repairs Lead Edit field layout after helper/money enhancements so select controls do not stretch into distorted panels.
 * @collaboration Keeps CRM Edit simple, compact, and operator-safe after post-save synchronization enhancements.
 */
function ensureWilsyR91K49LeadEditLayoutStyle() {
  if (document.getElementById('wilsy-r91k49-lead-edit-layout-style')) {
    return;
  }

  const style = document.createElement('style');
  style.id = 'wilsy-r91k49-lead-edit-layout-style';
  style.textContent = `
.wilsyLeadEditField {
  align-content: start !important;
  align-items: stretch !important;
  display: grid !important;
  gap: 0.7rem !important;
  min-height: unset !important;
}

.wilsyLeadEditField > .wilsyLeadEditControl,
.wilsyLeadEditField select.wilsyLeadEditControl,
.wilsyLeadEditField input.wilsyLeadEditControl {
  min-height: 4.25rem !important;
  height: 4.25rem !important;
}

.wilsyLeadEditFieldHelper {
  margin: 0 !important;
  max-width: 100% !important;
}
`;
  document.head.appendChild(style);
}

/**
 * @function completeWilsyLeadEditAfterPersistence
 * @description Closes the Lead Edit surface and returns the operator to the Lead list after a confirmed persisted save.
 * @collaboration Coordinates Lead Edit, CRM list refresh listeners, proof-trail receipt visibility, and post-save operator flow.
 */
function completeWilsyLeadEditAfterPersistence({ overlay, payload = {}, recordId = '', lead = {}, record = {} } = {}) {
  const leadPatch = resolveWilsyR91K49LeadListPatch({ recordId, lead, payload, record });
  const detail = {
    recordId,
    status: payload.status || payload.result || 'DB_PERSISTED',
    receiptHash: payload.receiptHash || payload.receipt || payload.auditReceipt || '',
    lead,
    leadPatch,
    source: 'R91K.49_POST_SAVE_LIST_SYNC',
  };

  applyWilsyR91K49LeadListDomPatch(detail);
  window.dispatchEvent(new CustomEvent('wilsy:lead-edit-saved', { detail }));
  document.dispatchEvent(new CustomEvent('wilsy:lead-edit-saved', { detail }));

  window.setTimeout(() => {
    if (overlay && typeof overlay.remove === 'function') {
      overlay.remove();
    }

    window.dispatchEvent(new CustomEvent('wilsy:crm-leads-refresh-requested', { detail }));
    document.dispatchEvent(new CustomEvent('wilsy:crm-leads-refresh-requested', { detail }));
  }, 850);
}

/**
 * @function submitWilsyLeadEdit
 * @description Saves the dedicated Lead Edit form through the governed backend PATCH route.
 * @collaboration Uses existing CRM command authority and passes operator evidence for role resolution.
 */
async function submitWilsyLeadEdit({ overlay, record = {}, recordId = '', tenantId = '', statusNode, operatorRole = '', apiBase = '' }) {
  const resolvedRecordId = resolveWilsyLeadEditRecordId(record, recordId);

  if (!resolvedRecordId) {
    renderWilsyLeadEditStatus(statusNode, {
      status: 'EDIT_BLOCKED',
      message: 'Record ID missing. Reopen the Lead from the backend row.',
      nextBestActions: ['Close Edit and reopen from the Lead row action menu.'],
    });
    return;
  }

  const lead = collectWilsyLeadEditPayload(overlay);
  const operatorContext = resolveWilsyLeadEditOperatorContext(operatorRole);

  if (!lead.ownerName || lead.ownerName === 'Unassigned') {
    lead.ownerName = operatorContext.displayName || 'Unassigned';
  }

  if (!lead.ownerId && operatorContext.id) {
    lead.ownerId = operatorContext.id;
  }

  renderWilsyLeadEditStatus(statusNode, {
    status: 'COMMAND_RUNNING',
    message: 'Saving governed Lead edit.',
    nextBestActions: ['Trying configured API, Vite proxy, localhost:5050, and 127.0.0.1:5050.'],
  });

  const endpoints = buildWilsyLeadEditEndpointCandidates(apiBase, resolvedRecordId);
  const failures = [];

  for (const endpoint of endpoints) {
    try {
      const response = await fetch(endpoint, {
        method: 'PATCH',
        headers: buildWilsyLeadEditHeaders(resolveWilsyLeadEditTenantId(record, tenantId), operatorContext),
        body: JSON.stringify({
          action: 'UPDATE',
          lead,
          before: record,
          commandSurface: 'R91K.32_SAVE_TRANSPORT_OWNER_FIX',
          operatorContext,
        }),
      });

      const payload = await response.json().catch(() => ({
        status: response.ok ? 'DB_PERSISTED' : 'CRM_LEAD_EDIT_RESPONSE_UNREADABLE',
        message: response.ok ? 'Edit persisted but response body was unreadable.' : `Backend returned HTTP ${response.status}.`,
      }));

      if (response.ok || response.status === 401 || response.status === 403 || response.status === 422) {
        renderWilsyLeadEditStatus(statusNode, payload);
      if (response.ok || String(payload?.status || '').toUpperCase() === 'DB_PERSISTED') {
        completeWilsyLeadEditAfterPersistence({ overlay, payload, recordId: resolvedRecordId, lead, record });
      }

        return;
      }

      failures.push(`${endpoint} -> HTTP ${response.status}`);
    } catch (error) {
      failures.push(`${endpoint} -> ${error.message}`);
    }
  }

  renderWilsyLeadEditStatus(statusNode, {
    status: 'COMMAND_API_UNREACHABLE',
    message: `Lead command API transport failed after ${endpoints.length} endpoint attempts.`,
    nextBestAction: `Start backend on port 5050 or fix VITE_API_URL. Attempts: ${failures.join(' | ')}`,
  });
}

/**
 * @function ensureWilsyLeadEditSurfaceDesign
 * @description Installs isolated CSS for the dedicated Lead Edit surface.
 * @collaboration Uses a unique overlay id so legacy capsule CSS cannot collapse the form.
 */
function ensureWilsyLeadEditSurfaceDesign() {
  const styleId = 'wilsy-r91k31-canonical-lead-edit-design';

  if (document.getElementById(styleId)) {
    return;
  }

  const style = document.createElement('style');
  style.id = styleId;
  style.textContent = `
    #wilsy-lead-edit-surface-overlay {
      position: fixed !important;
      inset: 0 !important;
      z-index: 2147483647 !important;
      overflow: auto !important;
      padding: clamp(16px, 1.6vw, 28px) !important;
      background:
        radial-gradient(circle at top left, rgba(16,185,129,0.20), transparent 36%),
        linear-gradient(135deg, rgba(2,6,23,0.99), rgba(2,6,23,0.96)) !important;
      color: #fff !important;
      box-sizing: border-box !important;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif !important;
    }

    #wilsy-lead-edit-surface-overlay * {
      box-sizing: border-box !important;
      writing-mode: horizontal-tb !important;
      text-orientation: mixed !important;
    }

    #wilsy-lead-edit-surface-overlay .wilsyLeadEditShell {
      width: min(100%, 1720px) !important;
      min-height: calc(100dvh - clamp(32px, 3.2vw, 56px)) !important;
      margin: 0 auto !important;
      border: 1px solid rgba(16,185,129,0.42) !important;
      border-radius: 32px !important;
      background: rgba(2,6,23,0.74) !important;
      box-shadow: 0 30px 100px rgba(0,0,0,0.42) !important;
      padding: clamp(18px, 1.8vw, 34px) !important;
      display: grid !important;
      gap: 18px !important;
    }

    #wilsy-lead-edit-surface-overlay .wilsyLeadEditBrand {
      display: flex !important;
      align-items: center !important;
      justify-content: space-between !important;
      gap: 14px !important;
      border: 1px solid rgba(16,185,129,0.42) !important;
      border-radius: 999px !important;
      background: rgba(15,23,42,0.72) !important;
      padding: 12px 18px !important;
    }

    #wilsy-lead-edit-surface-overlay .wilsyLeadEditBrand strong,
    #wilsy-lead-edit-surface-overlay .wilsyLeadEditBrand span {
      color: rgba(245,230,170,0.96) !important;
      font-weight: 950 !important;
      letter-spacing: 0.18em !important;
      text-transform: uppercase !important;
      white-space: nowrap !important;
    }

    #wilsy-lead-edit-surface-overlay .wilsyLeadEditHeader {
      display: grid !important;
      grid-template-columns: minmax(0, 1fr) auto !important;
      gap: 16px !important;
      align-items: start !important;
      border-bottom: 1px solid rgba(148,163,184,0.22) !important;
      padding-bottom: 18px !important;
    }

    #wilsy-lead-edit-surface-overlay .wilsyLeadEditHeader small {
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

    #wilsy-lead-edit-surface-overlay .wilsyLeadEditHeader h1 {
      font-size: clamp(42px, 5vw, 82px) !important;
      line-height: 0.9 !important;
      margin: 16px 0 12px !important;
      letter-spacing: -0.07em !important;
    }

    #wilsy-lead-edit-surface-overlay .wilsyLeadEditHeader p {
      margin: 0 !important;
      color: rgba(203,213,225,0.86) !important;
      font-size: clamp(15px, 1.2vw, 20px) !important;
      max-width: 86rem !important;
    }

    #wilsy-lead-edit-surface-overlay .wilsyLeadEditActions {
      display: flex !important;
      flex-wrap: wrap !important;
      justify-content: flex-end !important;
      gap: 12px !important;
    }

    #wilsy-lead-edit-surface-overlay .wilsyLeadEditActions button,
    #wilsy-lead-edit-surface-overlay .wilsyLeadEditSaveButton {
      border-radius: 18px !important;
      border: 1px solid rgba(148,163,184,0.32) !important;
      background: rgba(15,23,42,0.92) !important;
      color: #fff !important;
      cursor: pointer !important;
      font-weight: 900 !important;
      padding: 15px 20px !important;
      font-size: 15px !important;
    }

    #wilsy-lead-edit-surface-overlay .wilsyLeadEditSaveButton {
      background: linear-gradient(135deg, #20e391, #0f8f68) !important;
      border-color: rgba(16,185,129,0.85) !important;
      color: #02130d !important;
    }

    #wilsy-lead-edit-surface-overlay .wilsyLeadEditForm {
      border: 1px solid rgba(148,163,184,0.22) !important;
      border-radius: 28px !important;
      padding: clamp(18px, 1.6vw, 30px) !important;
      background: rgba(15,23,42,0.54) !important;
      display: grid !important;
      gap: 18px !important;
    }

    #wilsy-lead-edit-surface-overlay .wilsyLeadEditGrid {
      display: grid !important;
      grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
      gap: 16px !important;
    }

    #wilsy-lead-edit-surface-overlay .wilsyLeadEditField {
      display: grid !important;
      gap: 9px !important;
      min-width: 0 !important;
    }

    #wilsy-lead-edit-surface-overlay .wilsyLeadEditField span {
      color: rgba(245,230,170,0.94) !important;
      font-size: 12px !important;
      font-weight: 950 !important;
      letter-spacing: 0.18em !important;
      text-transform: uppercase !important;
    }

    #wilsy-lead-edit-surface-overlay .wilsyLeadEditControl {
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
    }

.wilsyLeadEditFieldHelper {
  margin: -0.35rem 0 0;
  color: rgba(226, 232, 240, 0.62);
  font-size: 0.78rem;
  letter-spacing: 0.08em;
  line-height: 1.45;
  text-transform: none;
}


    #wilsy-lead-edit-surface-overlay textarea.wilsyLeadEditControl {
      min-height: 116px !important;
      resize: vertical !important;
    }

    #wilsy-lead-edit-surface-overlay .wilsyLeadEditPhoneDeck {
      display: grid !important;
      grid-template-columns: minmax(180px, 0.34fr) minmax(0, 1fr) !important;
      gap: 10px !important;
    }

    #wilsy-lead-edit-surface-overlay .wilsyLeadEditStatus {
      border-left: 4px solid rgba(16,185,129,0.84) !important;
      color: rgba(203,213,225,0.92) !important;
      padding: 13px 16px !important;
      background: rgba(2,6,23,0.58) !important;
      border-radius: 14px !important;
      overflow-wrap: anywhere !important;
    }

    @media (max-width: 980px) {
      #wilsy-lead-edit-surface-overlay .wilsyLeadEditHeader,
      #wilsy-lead-edit-surface-overlay .wilsyLeadEditGrid,
      #wilsy-lead-edit-surface-overlay .wilsyLeadEditPhoneDeck {
        grid-template-columns: 1fr !important;
      }

      #wilsy-lead-edit-surface-overlay .wilsyLeadEditBrand {
        align-items: flex-start !important;
        border-radius: 24px !important;
        flex-direction: column !important;
      }
    }
  `;

  document.head.appendChild(style);
}

/**
 * @function openWilsyLeadEditSurface
 * @description Opens the canonical dedicated Lead Edit surface outside the legacy command capsule overlay.
 * @collaboration Provides production owner, industry, title, phone, status, and backend save authority context.
 */
/**
 * @function parseWilsyLeadEditMoneyEnhancerValue
 * @description Converts a currency-looking input value into a backend-safe numeric amount.
 * @collaboration Keeps the Lead Edit money UI human-friendly while preserving clean numeric CRM payloads.
 */
function parseWilsyLeadEditMoneyEnhancerValue(value = '') {
  const amount = Number.parseFloat(
    String(value || '')
      .replace(/[^\d.,-]/g, '')
      .replace(/,/g, '')
      .trim()
  );

  if (!Number.isFinite(amount)) {
    return 0;
  }

  return Math.max(0, Math.round(amount * 100) / 100);
}

/**
 * @function formatWilsyLeadEditMoneyEnhancerValue
 * @description Formats a Lead value amount as South African Rand.
 * @collaboration Makes estimated deal value readable, simple, and revenue-grade for operators.
 */
function formatWilsyLeadEditMoneyEnhancerValue(value = '') {
  const amount = parseWilsyLeadEditMoneyEnhancerValue(value);

  try {
    return new Intl.NumberFormat('en-ZA', {
      style: 'currency',
      currency: 'ZAR',
      maximumFractionDigits: 2,
    }).format(amount);
  } catch (error) {
    return `R ${amount.toLocaleString('en-ZA', { maximumFractionDigits: 2 })}`;
  }
}

/**
 * @function syncWilsyLeadEditMoneyEnhancer
 * @description Keeps the visible money field, hidden numeric payload, and preview synchronized.
 * @collaboration Supports governed Lead save, CRM revenue pipeline clarity, and audit-safe value persistence.
 */
function syncWilsyLeadEditMoneyEnhancer(input, hidden, preview) {
  const amount = parseWilsyLeadEditMoneyEnhancerValue(input?.value || '');

  if (hidden) {
    hidden.value = String(amount);
  }

  if (preview) {
    preview.textContent = `${formatWilsyLeadEditMoneyEnhancerValue(amount)} estimated pipeline value`;
  }
}

/**
 * @function ensureWilsyLeadEditMoneyEnhancerStyle
 * @description Installs dedicated styles for the enhanced Lead money editor.
 * @collaboration Keeps the money editor visually sovereign without touching the core field renderer.
 */
function ensureWilsyLeadEditMoneyEnhancerStyle() {
  if (document.getElementById('wilsy-lead-edit-money-enhancer-style')) {
    return;
  }

  const style = document.createElement('style');
  style.id = 'wilsy-lead-edit-money-enhancer-style';
  style.textContent = `
.wilsyLeadEditMoneyDeck {
  display: grid;
  gap: 0.65rem;
}

.wilsyLeadEditMoneyControl {
  align-items: center;
  background: rgba(2, 6, 23, 0.72);
  border: 1px solid rgba(148, 163, 184, 0.22);
  border-radius: 1.25rem;
  display: grid;
  grid-template-columns: auto 1fr;
  min-height: 4.25rem;
  overflow: hidden;
}

.wilsyLeadEditMoneyPrefix {
  align-items: center;
  border-right: 1px solid rgba(148, 163, 184, 0.18);
  color: rgba(167, 243, 208, 0.94);
  display: flex;
  font-size: 1.45rem;
  font-weight: 900;
  height: 100%;
  justify-content: center;
  min-width: 4.5rem;
}

.wilsyLeadEditMoneyInput {
  background: transparent !important;
  border: 0 !important;
  color: #ffffff !important;
  font-size: 1.65rem !important;
  font-weight: 900 !important;
  height: 100%;
  letter-spacing: 0.06em;
  outline: none !important;
  padding: 0 1.25rem !important;
  width: 100%;
}

.wilsyLeadEditMoneyChips {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.wilsyLeadEditMoneyChip {
  background: rgba(16, 185, 129, 0.12);
  border: 1px solid rgba(16, 185, 129, 0.32);
  border-radius: 999px;
  color: rgba(209, 250, 229, 0.94);
  cursor: pointer;
  font-size: 0.82rem;
  font-weight: 900;
  letter-spacing: 0.08em;
  padding: 0.55rem 0.8rem;
}

.wilsyLeadEditMoneyPreview {
  color: rgba(167, 243, 208, 0.82);
  font-size: 0.82rem;
  font-weight: 800;
  letter-spacing: 0.08em;
  margin: 0;
}
`;
  document.head.appendChild(style);
}

/**
 * @function enhanceWilsyLeadEditMoneyControls
 * @description Enhances rendered Estimated Deal Value fields into proper money editors without altering the core field renderer.
 * @collaboration Converts plain value inputs into R-prefixed, chip-assisted, preview-backed money controls while preserving backend numeric payloads.
 */
function enhanceWilsyLeadEditMoneyControls(root = document) {
  ensureWilsyLeadEditMoneyEnhancerStyle();

  const fields = Array.from(root.querySelectorAll('.wilsyLeadEditField, label')).filter((field) => {
    const text = String(field.textContent || '').toLowerCase();

    return text.includes('estimated deal value') || text.includes('estimated potential revenue');
  });

  fields.forEach((field) => {
    if (field.dataset.wilsyMoneyEnhanced === 'true') {
      return;
    }

    const input =
      field.querySelector('input[data-wilsy-lead-edit-key="value"]') ||
      field.querySelector('input[data-wilsy-lead-edit-key="dealValue"]') ||
      field.querySelector('input[type="number"]') ||
      field.querySelector('input');

    if (!input) {
      return;
    }

    field.dataset.wilsyMoneyEnhanced = 'true';

    const originalKey = input.dataset.wilsyLeadEditKey || 'value';
    const startingAmount = parseWilsyLeadEditMoneyEnhancerValue(input.value);
    const hidden = document.createElement('input');
    const shell = document.createElement('div');
    const prefix = document.createElement('span');
    const chips = document.createElement('div');
    const preview = document.createElement('p');

    input.removeAttribute('data-wilsy-lead-edit-key');
    input.type = 'text';
    input.inputMode = 'decimal';
    input.autocomplete = 'off';
    input.spellcheck = false;
    input.classList.add('wilsyLeadEditMoneyInput');
    input.value = startingAmount ? startingAmount.toLocaleString('en-ZA', { maximumFractionDigits: 2 }) : '';
    input.placeholder = '0.00';

    hidden.type = 'hidden';
    hidden.dataset.wilsyLeadEditKey = originalKey;
    hidden.value = String(startingAmount);

    shell.className = 'wilsyLeadEditMoneyControl';
    prefix.className = 'wilsyLeadEditMoneyPrefix';
    prefix.textContent = 'R';

    chips.className = 'wilsyLeadEditMoneyChips';
    preview.className = 'wilsyLeadEditMoneyPreview';

    input.parentNode.insertBefore(shell, input);
    shell.append(prefix, input);

    [
      ['R10K', 10000],
      ['R50K', 50000],
      ['R100K', 100000],
      ['R250K', 250000],
      ['R1M', 1000000],
    ].forEach(([label, amount]) => {
      const chip = document.createElement('button');
      chip.type = 'button';
      chip.className = 'wilsyLeadEditMoneyChip';
      chip.textContent = label;
      chip.addEventListener('click', () => {
        input.value = Number(amount).toLocaleString('en-ZA', { maximumFractionDigits: 2 });
        syncWilsyLeadEditMoneyEnhancer(input, hidden, preview);
        input.focus();
      });
      chips.appendChild(chip);
    });

    input.addEventListener('input', () => syncWilsyLeadEditMoneyEnhancer(input, hidden, preview));

    input.addEventListener('focus', () => {
      const amount = parseWilsyLeadEditMoneyEnhancerValue(input.value);

      input.value = amount ? String(amount) : '';
      input.select();
    });

    input.addEventListener('blur', () => {
      const amount = parseWilsyLeadEditMoneyEnhancerValue(input.value);

      input.value = amount ? amount.toLocaleString('en-ZA', { maximumFractionDigits: 2 }) : '';
      syncWilsyLeadEditMoneyEnhancer(input, hidden, preview);
    });

    field.append(chips, preview, hidden);
    syncWilsyLeadEditMoneyEnhancer(input, hidden, preview);
  });
}

/**
 * @function openWilsyLeadEditSurface
 * @description Opens the governed Lead Edit surface with canonical field controls and save orchestration.
 * @collaboration Lead list actions, CRM edit overlay, persisted save receipts, owner/value/industry field governance.
 */
/**
 * @function ensureWilsyR91K51LeadEditGovernanceStyle
 * @description Installs styles for locked business identity fields and repaired post-helper layout.
 * @collaboration Lead Edit field governance, immutable Industry posture, compact CRM edit layout.
 */
function ensureWilsyR91K51LeadEditGovernanceStyle() {
  if (document.getElementById('wilsy-r91k51-lead-edit-governance-style')) {
    return;
  }

  const style = document.createElement('style');
  style.id = 'wilsy-r91k51-lead-edit-governance-style';
  style.textContent = `
.wilsyLeadEditField {
  align-content: start !important;
  display: grid !important;
  gap: 0.7rem !important;
  min-height: unset !important;
}

.wilsyLeadEditLockedField {
  align-items: center;
  background: rgba(15, 23, 42, 0.86);
  border: 1px solid rgba(148, 163, 184, 0.26);
  border-radius: 1.25rem;
  color: #ffffff;
  display: flex;
  font-size: 1.35rem;
  font-weight: 900;
  letter-spacing: 0.08em;
  min-height: 4.25rem;
  padding: 0 1.25rem;
}

.wilsyLeadEditIndustryGovernance {
  display: grid;
  gap: 0.65rem;
}
`;
  document.head.appendChild(style);
}

/**
 * @function openWilsyLeadEditSurface
 * @description Opens the governed Lead Edit surface with field controls, payload collection, save orchestration, and receipt handling.
 * @collaboration CRM Lead Operating Room, Lead Edit payload contract, DB_PERSISTED proof flow, owner/status/value/industry governance.
 */
export function openWilsyLeadEditSurface({
  mode = 'edit',
  label = 'Edit Lead',
  record = {},
  recordId = '',
  recordIds = [],
  tenantId = '',
  operatorRole = '',
  apiBase = '',
  onProofTrail = null,
} = {}) {
  installWilsyLeadEditDbPersistedSaveGateway(arguments[0] || {});

  ensureWilsyR91K51LeadEditGovernanceStyle();
  ensureWilsyR91K49LeadEditLayoutStyle();

  ensureWilsyLeadEditMoneyEnhancerStyle();
  window.setTimeout(enhanceWilsyLeadEditMoneyControls, 0);

  if (typeof document === 'undefined') {
    return null;
  }

  document.querySelectorAll('#wilsy-r91g1-lead-inspection-overlay, #wilsy-lead-edit-surface-overlay').forEach((node) => node.remove());
  ensureWilsyLeadEditSurfaceDesign();

  const overlay = createWilsyLeadEditNode('section', 'wilsyLeadEditSurface');
  overlay.id = 'wilsy-lead-edit-surface-overlay';
  overlay.dataset.wilsyLeadEditSurface = 'R91K31_CANONICAL';
  overlay.dataset.mode = mode;
  overlay.dataset.label = label;
  overlay.dataset.recordId = resolveWilsyLeadEditRecordId(record, recordId);

  const shell = createWilsyLeadEditNode('main', 'wilsyLeadEditShell');
  const brand = createWilsyLeadEditNode('div', 'wilsyLeadEditBrand');
  const header = createWilsyLeadEditNode('header', 'wilsyLeadEditHeader');
  const titleBlock = createWilsyLeadEditNode('div', '');
  const actions = createWilsyLeadEditNode('div', 'wilsyLeadEditActions');
  const proofButton = createWilsyLeadEditNode('button', '', 'Open Proof Trail');
  const closeButton = createWilsyLeadEditNode('button', '', 'Close');

  brand.append(
    createWilsyLeadEditNode('strong', '', 'WILSY OS'),
    createWilsyLeadEditNode('span', '', 'Lead Edit'),
    createWilsyLeadEditNode('span', '', 'Actionable Data')
  );

  proofButton.type = 'button';
  closeButton.type = 'button';

  proofButton.addEventListener('click', () => {
    overlay.remove();

    if (typeof onProofTrail === 'function') {
      onProofTrail();
    }
  });

  closeButton.addEventListener('click', () => overlay.remove());

  titleBlock.append(
    createWilsyLeadEditNode('small', '', 'Focused Edit'),
    createWilsyLeadEditNode('h1', '', 'Edit Lead'),
    createWilsyLeadEditNode('p', '', 'Edit the backend Lead record from one production form surface. Proof Trail opens separately and cannot pollute the edit task.')
  );

  actions.append(proofButton, closeButton);
  header.append(titleBlock, actions);

  const form = createWilsyLeadEditNode('section', 'wilsyLeadEditForm');
  const formHeader = createWilsyLeadEditNode('div', '');
  const grid = createWilsyLeadEditNode('div', 'wilsyLeadEditGrid');
  const saveButton = createWilsyLeadEditNode('button', 'wilsyLeadEditSaveButton', 'Save governed edit');
  const statusNode = createWilsyLeadEditNode('div', 'wilsyLeadEditStatus', 'Ready. Owner, industry, title and save context are using the canonical Lead Edit contract.');

  saveButton.type = 'button';

  formHeader.append(
    createWilsyLeadEditNode('h2', '', 'Lead Information'),
    createWilsyLeadEditNode('p', '', 'All visible fields are actionable backend-backed edit controls.')
  );

  buildWilsyLeadEditFields(record).forEach((field) => {
    grid.appendChild(renderWilsyLeadEditField(field));
  });

  saveButton.addEventListener('click', () => {
    submitWilsyLeadEdit({
      overlay,
      record,
      recordId,
      tenantId,
      statusNode,
      operatorRole,
      apiBase,
    });
  });

  form.append(formHeader, grid, saveButton, statusNode);
  shell.append(brand, header, form);
  overlay.appendChild(shell);
  document.body.appendChild(overlay);

  return overlay;
}
