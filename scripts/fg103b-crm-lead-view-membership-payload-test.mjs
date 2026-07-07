/* eslint-disable */
import crypto from 'node:crypto';

const API_BASE = String(process.env.WILSY_API_BASE || 'http://localhost:3000').replace(/\/$/, '');
const TOKEN = String(process.env.WILSY_AUTH_TOKEN || '').replace(/^Bearer\s+/i, '').trim();
const TENANT_ID = process.env.WILSY_TENANT_ID || 'MASTER';
const OPERATOR_ID = process.env.WILSY_OPERATOR_ID || 'wilsy-operator';
const COMMAND_SURFACE = 'CRM_LEADS_VIEW_MEMBERSHIP_PAYLOAD_TEST';

if (!TOKEN) {
  console.error('STOP: set WILSY_AUTH_TOKEN to a live browser JWT before running this payload test.');
  process.exit(1);
}

/**
 * @function sortForWilsySeal
 * @description Recursively sorts payload keys for backend SHA3 request seal reconstruction.
 * @param {*} value Payload value.
 * @returns {*} Stable value.
 * @collaboration ProductionHardening.middleware, signed payload tests, and Lead View Membership routes.
 */
function sortForWilsySeal(value) {
  if (Array.isArray(value)) return value.map(sortForWilsySeal);
  if (value && typeof value === 'object') {
    return Object.keys(value)
      .sort()
      .reduce((next, key) => {
        next[key] = sortForWilsySeal(value[key]);
        return next;
      }, {});
  }
  return value;
}

/**
 * @function buildEvidencePayload
 * @description Builds Wilsy institutional payload evidence for CRM Lead View Membership tests.
 * @param {string} route API route.
 * @param {string} action Command action.
 * @param {object} body Body fields.
 * @returns {object} Evidence payload.
 * @collaboration Institutional headers, strike payload, audit receipts, and signed membership commands.
 */
function buildEvidencePayload(route, action, body = {}) {
  const generatedAt = new Date().toISOString();
  const requestId = `REQ-FG103B-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;

  const institutionalHeaders = {
    tenantId: TENANT_ID,
    operatorId: OPERATOR_ID,
    operatorUserId: OPERATOR_ID,
    userId: OPERATOR_ID,
    route,
    commandSurface: COMMAND_SURFACE,
    timestamp: generatedAt,
    generatedAt,
    requestId,
  };

  return {
    ...body,
    tenantId: TENANT_ID,
    operatorId: OPERATOR_ID,
    operatorUserId: OPERATOR_ID,
    userId: OPERATOR_ID,
    commandSurface: COMMAND_SURFACE,
    generatedAt,
    requestId,
    institutionalHeaders,
    strikePayload: {
      action,
      tenantId: TENANT_ID,
      operatorId: OPERATOR_ID,
      operatorUserId: OPERATOR_ID,
      userId: OPERATOR_ID,
      route,
      commandSurface: COMMAND_SURFACE,
      timestamp: generatedAt,
      generatedAt,
      requestId,
      institutionalHeaders,
    },
  };
}

/**
 * @function signHeaders
 * @description Builds signed CRM headers for Wilsy request seal verification.
 * @param {object} payload Request payload.
 * @returns {object} Signed headers.
 * @collaboration Production hardening, Authorization bearer token, SHA3 seal, and membership payload tests.
 */
function signHeaders(payload) {
  const traceId = payload.requestId;
  const timestamp = payload.generatedAt;
  const nonce = `NONCE-FG103B-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
  const payloadString = JSON.stringify(sortForWilsySeal(payload));
  const reconstruction = `${traceId}|${timestamp}|${payloadString}|${nonce}`;
  const seal = crypto.createHash('sha3-512').update(reconstruction).digest('hex').toUpperCase();

  return {
    'Content-Type': 'application/json',
    Authorization: `Bearer ${TOKEN}`,
    'X-Tenant-Id': TENANT_ID,
    'X-Operator-Id': OPERATOR_ID,
    'X-Operator-User-Id': OPERATOR_ID,
    'X-User-Id': OPERATOR_ID,
    'X-Command-Surface': COMMAND_SURFACE,
    'X-Request-ID': traceId,
    'X-Trace-ID': traceId,
    'X-Correlation-ID': traceId,
    'X-Forensic-Timestamp': timestamp,
    'X-Timestamp': timestamp,
    'X-Generated-At': timestamp,
    'X-Cryptographic-Nonce': nonce,
    'X-Request-Seal': seal,
  };
}

/**
 * @function postSigned
 * @description Sends a signed JSON command to the Wilsy API.
 * @param {string} route API route.
 * @param {string} action Action name.
 * @param {object} body Body fields.
 * @param {string} method HTTP method.
 * @returns {Promise<object>} Response payload.
 * @collaboration Payload tests, signed CRM routes, and production hardening.
 */
async function postSigned(route, action, body = {}, method = 'POST') {
  const payload = buildEvidencePayload(route, action, body);
  const response = await fetch(`${API_BASE}${route}`, {
    method,
    headers: signHeaders(payload),
    body: JSON.stringify(payload),
  });

  const json = await response.json().catch(() => ({}));

  return {
    status: response.status,
    ok: response.ok,
    json,
  };
}

/**
 * @function main
 * @description Runs signed include, exclude, clear, and run payload tests for CRM Lead View Membership.
 * @returns {Promise<void>} Test completion.
 * @collaboration Backend membership overrides, signed payload tests, audit receipts, and custom view productivity.
 */
async function main() {
  const query = await postSigned('/api/crm/leads/views/query', 'LIST_LEAD_VIEWS', {}, 'POST');
  const firstView = query.json?.views?.[0] || query.json?.data?.views?.[0] || query.json?.result?.views?.[0];

  if (!query.ok || !firstView?._id && !firstView?.id) {
    console.error(JSON.stringify({ step: 'query', query }, null, 2));
    throw new Error('No saved Lead view available for FG103B payload test.');
  }

  const viewId = String(firstView._id || firstView.id);
  const run = await postSigned(`/api/crm/leads/views/${viewId}/run`, 'RUN_LEAD_VIEW', {}, 'POST');
  const leadId = String(
    process.env.WILSY_TEST_LEAD_ID
      || run.json?.result?.sampleLeadIds?.[0]
      || run.json?.sampleLeadIds?.[0]
      || 'FG103B-SMOKE-LEAD-ID'
  );

  const include = await postSigned(
    `/api/crm/leads/views/${viewId}/overrides/include`,
    'INCLUDE_LEADS_IN_VIEW',
    { leadIds: [leadId], reason: 'FG103B signed payload smoke include' },
    'POST'
  );

  const exclude = await postSigned(
    `/api/crm/leads/views/${viewId}/overrides/exclude`,
    'EXCLUDE_LEADS_FROM_VIEW',
    { leadIds: [leadId], reason: 'FG103B signed payload smoke exclude' },
    'POST'
  );

  const clear = await postSigned(
    `/api/crm/leads/views/${viewId}/overrides/${encodeURIComponent(leadId)}`,
    'CLEAR_LEAD_VIEW_MEMBERSHIP_OVERRIDE',
    { leadId },
    'DELETE'
  );

  const finalRun = await postSigned(`/api/crm/leads/views/${viewId}/run`, 'RUN_LEAD_VIEW', {}, 'POST');

  const report = {
    viewId,
    leadId,
    include: { status: include.status, ok: include.ok, mode: include.json?.mode, auditReceiptId: include.json?.auditReceiptId },
    exclude: { status: exclude.status, ok: exclude.ok, mode: exclude.json?.mode, auditReceiptId: exclude.json?.auditReceiptId },
    clear: { status: clear.status, ok: clear.ok, cleared: clear.json?.cleared, auditReceiptId: clear.json?.auditReceiptId },
    finalRun: { status: finalRun.status, ok: finalRun.ok, membership: finalRun.json?.result?.membership },
  };

  console.log(JSON.stringify(report, null, 2));

  if (!include.ok || !exclude.ok || !clear.ok || !finalRun.ok) {
    process.exit(1);
  }
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
