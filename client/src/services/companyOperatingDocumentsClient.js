/**
 * TITLE: WILSY OS Company Operating Document Client Contract
 * VERSION: v1.2.0-FOUNDER-STRATEGY-RATIFICATION-TRANSPORT
 * AUTHORITY: Python EOS owns content, publication and command authorization.
 * EPITOME: Validate current Mission/Strategy source views and command receipts
 *          without treating a Founder label, draft or acknowledgement as policy.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/services/companyOperatingDocumentsClient.js
 * COLLABORATION / OWNERSHIP: Shared CompanyOperatingDocumentViewer; existing api.js transport.
 * CERTIFICATION / UPDATE DATE: 2026-11-14
 * CHANGELOG: v1.2.0-FOUNDER-STRATEGY-RATIFICATION-TRANSPORT
 *           recognizes strict Strategy-only Founder author/submit/ratify
 *           actions and the exact server-owned self-ratification reference.
 *           All commands still require authenticated EOS readback.
 * CHANGELOG: 2026-11-14 v1.2.0-FOUNDER-STRATEGY-RATIFICATION-TRANSPORT adds a scoped
 *           Founder-session evidence adapter through the existing authenticated
 *           api.js instance; no raw fetch, credential store or admission bypass.
 *           v1.0.0-SCOPED-COMPANY-DOCUMENT-TRANSPORT adds exact scoped no-store
 *           source reads/history and stable-idempotency command adapters.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
 * SECURITY / PRIVACY POSTURE: No storage, logs, HTML execution or policy generation.
 * TENANT BOUNDARY: Every response must match the exact requested tenant/principal.
 * AUTHORITY BOUNDARY: Source endpoints independently authorize every operation;
 *                     mutation success still requires independent source readback.
 * FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively.
 */
import api from './api.js';

const CLASSES = new Set(['MISSION', 'STRATEGY']);
const STATES = new Set(['DRAFT', 'SUBMITTED', 'PUBLISHED']);
const ACTIONS = new Set(['READ_HISTORY', 'REVIEW_DRAFTS', 'CREATE_DRAFT', 'SUBMIT', 'PUBLISH',
  'FOUNDER_CREATE_DRAFT', 'FOUNDER_SUBMIT', 'FOUNDER_RATIFY']);
const FOUNDER_RATIFICATION_REFERENCE = 'WILSY-INSTITUTIONAL-FOUNDER-SELF-RATIFICATION-20261123';
const fingerprint = value => typeof value === 'string' && /^[a-f0-9]{128}$/.test(value);
const validInstant = value => typeof value === 'string' && Number.isFinite(Date.parse(value));
const fail = () => { throw new Error('COMPANY_DOCUMENT_RESPONSE_INVALID'); };

function pathFor(classification) {
  if (!CLASSES.has(classification)) throw new Error('COMPANY_DOCUMENT_CLASSIFICATION_INVALID');
  return '/company-operating-documents/' + classification;
}
function options(scope, { token, signal } = {}) {
  if (!scope?.tenantId || !scope?.principalId || typeof token !== 'string' || !token.trim()) {
    throw new Error('COMPANY_DOCUMENT_AUTHENTICATED_SCOPE_REQUIRED');
  }
  return { headers: { 'X-Tenant-ID': scope.tenantId, Authorization: 'Bearer ' + token },
    forceNetworkRetry: true, ...(signal ? { signal } : {}) };
}
function recordValid(record, classification, tenantId) {
  return Boolean(record && record.schema === 'WILSY-COMPANY-OPERATING-DOCUMENT/V1'
    && record.classification === classification && record.tenant_id === tenantId
    && record.document_id === 'wilsy-company-' + classification.toLowerCase()
    && typeof record.document_version === 'string' && /^\d+\.\d+\.\d+$/.test(record.document_version)
    && Number.isSafeInteger(record.revision) && record.revision > 0 && STATES.has(record.state)
    && typeof record.title === 'string' && record.title.trim() && record.title.length <= 200
    && typeof record.author_principal_id === 'string' && record.author_principal_id
    && validInstant(record.recorded_at) && fingerprint(record.fingerprint)
    && (record.state !== 'PUBLISHED' || (validInstant(record.effective_from)
      && typeof record.approval_reference === 'string' && record.approval_reference.trim()
      && typeof record.approved_by_principal_id === 'string' && record.approved_by_principal_id
      && (record.approved_by_principal_id !== record.author_principal_id
        ? record.approval_reference !== FOUNDER_RATIFICATION_REFERENCE
        : classification === 'STRATEGY'
          && record.approval_reference === FOUNDER_RATIFICATION_REFERENCE))));
}

/**
 * @description Validate one exact source view; an ordinary read cannot contain a draft.
 * @collaboration Shared viewer, read adapter and contract regression tests.
 * @institutional Validation grants no permission and cannot turn proposed content into publication.
 * @param {Object} value Source response.
 * @param {string} classification Requested closed classification.
 * @param {Object} scope Exact authenticated tenant/principal.
 * @param {boolean} review Explicit private-review request.
 * @returns {Object} Same validated source projection.
 * @throws {Error} Stable response-invalid code on any scope/publication inconsistency.
 */
export function assertCompanyDocumentView(value, classification, scope, review = false) {
  if (!value || value.schema !== 'WILSY-COMPANY-OPERATING-DOCUMENT-VIEW/V1'
    || value.classification !== classification || value.tenant_id !== scope.tenantId
    || value.principal_id !== scope.principalId || value.view !== (review ? 'review' : 'published')
    || !validInstant(value.as_of) || !Number.isSafeInteger(value.current_revision) || value.current_revision < 0
    || !Array.isArray(value.available_actions) || value.available_actions.some(action => !ACTIONS.has(action))
    || new Set(value.available_actions).size !== value.available_actions.length
    || value.authority?.publication_owned_by !== 'PYTHON_EOS' || value.authority?.financial_execution !== false
    || value.relationships?.state !== 'NOT_GOVERNED') fail();
  if (value.state === 'NOT_YET_PUBLISHED') {
    if (value.document !== null) fail();
  } else {
    const record = value.document;
    if (!recordValid(record, classification, scope.tenantId) || record.state !== value.state
      || record.revision > value.current_revision || !Array.isArray(record.sections)
      || record.sections.length < 1 || record.sections.length > 24
      || new Set(record.sections.map(section => section?.section_id)).size !== record.sections.length
      || record.sections.some(section => !section || !/^[a-z][a-z0-9-]{0,63}$/.test(section.section_id)
        || typeof section.title !== 'string' || !section.title.trim() || section.title.length > 160
        || typeof section.body !== 'string' || !section.body.trim() || section.body.length > 20000)
      || record.sections.reduce((total, section) => total + section.body.length, 0) > 100000
      || (!review && (record.state !== 'PUBLISHED' || Date.parse(record.effective_from) > Date.parse(value.as_of)))) fail();
  }
  return value;
}

/**
 * @description Read EOS-observed session identity using the existing authenticated API.
 * @collaboration Founder acceptance and current AuthProvider scope; api.js owns
 * bearer transport and delegates expiry recovery to that same session owner.
 * @institutional Session evidence establishes neither capacity authority nor a
 * permission grant. Exact principal/tenant mismatch fails closed before use.
 * No credential, persistence, transaction or financial authority is created.
 * @param {Object} scope Exact expected tenantId and principalId.
 * @param {Object} config Current provider token and optional AbortSignal.
 * @returns {Promise<Object>} Validated EOS session observation, without credentials.
 * @throws {Error} On absent authentication or mismatched/unverifiable evidence.
 */
export async function readFounderSessionEvidence(scope, config = {}) {
  const response = await api.get('/company-operating-documents/founder-session-evidence', options(scope, config));
  const value = response?.data;
  if (!value || value.schema !== 'WILSY-FOUNDER-SESSION-EVIDENCE/V1'
      || value.state !== 'AUTHENTICATED_SESSION_OBSERVED'
      || value.principal_id !== scope.principalId || value.tenant_id !== scope.tenantId
      || !['GLOBAL', 'TENANT', null].includes(value.principal_scope)
      || value.capacity_authority_verified_by_this_endpoint !== false
      || value.grant_issued !== false || value.administrative_grantor_appointed !== false) {
    throw new Error('FOUNDER_SESSION_EVIDENCE_INVALID');
  }
  return value;
}

/** @description Read exact authorized current/historical content. @collaboration Shared viewer. @institutional No settled read grants command authority; caller owns cancellation. */
export async function readCompanyOperatingDocument(classification, scope, config = {}) {
  const response = await api.get(pathFor(classification), {
    ...options(scope, config), params: { review: Boolean(config.review), ...(config.revision ? { revision: config.revision } : {}) },
  });
  return assertCompanyDocumentView(response?.data, classification, scope, Boolean(config.review));
}

/** @description Read permitted revision metadata. @collaboration Shared contents/history view. @institutional A published history cannot expose draft metadata or content. */
export async function readCompanyDocumentHistory(classification, scope, config = {}) {
  const response = await api.get(pathFor(classification) + '/revisions', { ...options(scope, config), params: { review: Boolean(config.review) } });
  const value = response?.data;
  if (!value || value.schema !== 'WILSY-COMPANY-OPERATING-DOCUMENT-HISTORY/V1'
    || value.classification !== classification || value.tenant_id !== scope.tenantId || value.principal_id !== scope.principalId
    || value.view !== (config.review ? 'review' : 'published') || !validInstant(value.as_of) || !Array.isArray(value.items)
    || value.items.some(record => !recordValid(record, classification, scope.tenantId)
      || Object.hasOwn(record, 'sections') || (!config.review && (record.state !== 'PUBLISHED' || Date.parse(record.effective_from) > Date.parse(value.as_of))))) fail();
  return value;
}

/** @description Submit an existing source-owned draft/submit/publish command with a stable retry key. @collaboration Shared viewer and EOS source registry. @institutional Acknowledgement is validated evidence; caller must independently read back before reporting success. */
export async function commandCompanyDocument(classification, scope, action, payload, idempotencyKey, config = {}) {
  const endpoint = { CREATE_DRAFT: '/drafts', SUBMIT: '/submit', PUBLISH: '/publish',
    FOUNDER_CREATE_DRAFT: '/founder-drafts', FOUNDER_SUBMIT: '/founder-submit',
    FOUNDER_RATIFY: '/founder-ratify' }[action];
  if (action.startsWith('FOUNDER_') && classification !== 'STRATEGY')
    throw new Error('COMPANY_DOCUMENT_FOUNDER_STRATEGY_ONLY');
  if (!endpoint || typeof idempotencyKey !== 'string' || !idempotencyKey) throw new Error('COMPANY_DOCUMENT_COMMAND_INVALID');
  const requestOptions = options(scope, config);
  const response = await api.post(pathFor(classification) + endpoint, payload, {
    ...requestOptions, headers: { ...requestOptions.headers, 'Idempotency-Key': idempotencyKey },
  });
  const value = response?.data;
  if (!value || value.schema !== 'WILSY-COMPANY-OPERATING-DOCUMENT-COMMAND-RESULT/V1'
    || value.tenant_id !== scope.tenantId || value.principal_id !== scope.principalId || value.classification !== classification
    || !recordValid(value.document, classification, scope.tenantId)) fail();
  return value.document;
}

// ARTIFACT: companyOperatingDocumentsClient.js
// VERSION: v1.2.0-FOUNDER-STRATEGY-RATIFICATION-TRANSPORT
// AUTHORITY BOUNDARY: Validated transport only; EOS owns approval/publication.
// TENANT POSTURE: Exact requested tenant/principal; no persisted content cache.
// FAIL-CLOSED POSTURE: Draft/publication/scope mismatch never renders as official.
// FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
// END OF WILSY OS SOVEREIGN ARTIFACT
