/**
 * TITLE: WILSY EOS independent response governance browser certificate
 * VERSION: v1.0.0-SYSTEM-SERVICES-DECISION-TO-CANONICAL-REVOCATION
 * AUTHORITY: Browser certification evidence only.
 * EPITOME: Prove separate requester, approver and executor identities across
 *          authenticated decision, approval and canonical permission revocation.
 * TENANT BOUNDARY: UUID-isolated synthetic tenant and disposable replica set.
 * AUTHORITY BOUNDARY: Existing EOS SYSTEM authorizer and D12 revocation service.
 * FINANCIAL AUTHORITY BOUNDARY: None.
 * FAIL-CLOSED DECLARATION: Any missing permission, workforce relationship,
 *                          correlation, revision or canonical receipt fails.
 */

import fs from 'node:fs';
import { expect, test } from '@playwright/test';

const statePath = process.env.BROWSER_CERT_STATE;
if (!statePath) throw new Error('BROWSER_CERT_STATE_REQUIRED');
const state = JSON.parse(fs.readFileSync(statePath, 'utf8'));
const baseURL = process.env.BROWSER_CERT_BASE_URL || 'http://127.0.0.1:5174';

async function postAs(browser, actorKey, path, body, idempotencyKey) {
  const actor = state.system_actors?.[actorKey];
  if (!actor?.access_token) throw new Error('BROWSER_CERT_SYSTEM_ACTOR_MISSING:' + actorKey);
  const context = await browser.newContext({ baseURL });
  const page = await context.newPage();
  await page.goto('/');
  const result = await page.evaluate(async ({ url, token, payload, key }) => {
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        Authorization: 'Bearer ' + token,
        'Content-Type': 'application/json',
        'Idempotency-Key': key,
      },
      body: JSON.stringify(payload),
    });
    return { status: response.status, body: await response.json() };
  }, {
    url: path,
    token: actor.access_token,
    payload: body,
    key: idempotencyKey,
  });
  await context.close();
  return result;
}

test('certifies independent request, rejection, approval and canonical permission revocation with replay', async ({ browser }) => {
  const rejectedRequestKey = 'browser-response-rejection-request-' + state.database_name;
  const rejectedRequest = await postAs(
    browser,
    'system_requester',
    '/api/system-services/security-response-decisions',
    {
      incident_id: state.system_incident_id,
      action: 'SYSTEM_PERMISSION_REVOCATION',
      target_assignment_id: state.system_target_permission_assignment_id,
      target_permission_id: 'privileged_activation:issue',
    },
    rejectedRequestKey,
  );
  expect(rejectedRequest.status).toBe(201);
  const rejected = await postAs(
    browser,
    'system_approver',
    '/api/system-services/security-response-decisions/' + rejectedRequest.body.decisionId + '/decision',
    {
      approved: false,
      expected_revision: 0,
      decision_evidence_reference: 'browser-cert-independent-rejection:' + state.database_name,
    },
    'browser-response-rejection-' + state.database_name,
  );
  expect(rejected.status).toBe(200);
  expect(rejected.body.status).toBe('REJECTED');
  expect(rejected.body.revision).toBe(1);
  const staleApproval = await postAs(
    browser,
    'system_approver',
    '/api/system-services/security-response-decisions/' + rejectedRequest.body.decisionId + '/decision',
    {
      approved: true,
      expected_revision: 0,
      decision_evidence_reference: 'browser-cert-stale-approval:' + state.database_name,
    },
    'browser-response-stale-approval-' + state.database_name,
  );
  expect(staleApproval.status).toBe(409);

  const requested = await postAs(
    browser,
    'system_requester',
    '/api/system-services/security-response-decisions',
    {
      incident_id: state.system_incident_id,
      action: 'SYSTEM_PERMISSION_REVOCATION',
      target_assignment_id: state.system_target_permission_assignment_id,
      target_permission_id: 'privileged_activation:issue',
    },
    'browser-response-request-' + state.database_name,
  );
  expect(requested.status).toBe(201);
  expect(requested.body.status).toBe('PENDING');
  expect(requested.body.revision).toBe(0);
  expect(requested.body.targetPrincipalId).toBe(state.actors.partner.principal_id);
  const decisionId = requested.body.decisionId;
  const requestReplay = await postAs(
    browser,
    'system_requester',
    '/api/system-services/security-response-decisions',
    {
      incident_id: state.system_incident_id,
      action: 'SYSTEM_PERMISSION_REVOCATION',
      target_assignment_id: state.system_target_permission_assignment_id,
      target_permission_id: 'privileged_activation:issue',
    },
    'browser-response-request-' + state.database_name,
  );
  expect(requestReplay.status).toBe(201);
  expect(requestReplay.body.decisionId).toBe(decisionId);

  const approved = await postAs(
    browser,
    'system_approver',
    '/api/system-services/security-response-decisions/' + decisionId + '/decision',
    {
      approved: true,
      expected_revision: 0,
      decision_evidence_reference: 'browser-cert-independent-approval:' + state.database_name,
    },
    'browser-response-approval-' + state.database_name,
  );
  expect(approved.status).toBe(200);
  expect(approved.body.status).toBe('APPROVED');
  expect(approved.body.revision).toBe(1);
  expect(approved.body.decidedByPrincipalId).toBe(state.system_actors.system_approver.principal_id);
  const approvalReplay = await postAs(
    browser,
    'system_approver',
    '/api/system-services/security-response-decisions/' + decisionId + '/decision',
    {
      approved: true,
      expected_revision: 0,
      decision_evidence_reference: 'browser-cert-independent-approval:' + state.database_name,
    },
    'browser-response-approval-' + state.database_name,
  );
  expect(approvalReplay.status).toBe(200);
  expect(approvalReplay.body).toEqual(approved.body);

  const executionPayload = { expected_revision: 1 };
  const executionKey = 'browser-response-execution-' + state.database_name;
  const executed = await postAs(
    browser,
    'system_executor',
    '/api/system-services/security-response-decisions/' + decisionId + '/execute/permission-revocation',
    executionPayload,
    executionKey,
  );
  expect(executed.status).toBe(200);
  expect(executed.body.status).toBe('REVOKED');
  expect(executed.body.assignmentId).toBe(state.system_target_permission_assignment_id);
  expect(executed.body.permissionId).toBe('privileged_activation:issue');

  const replay = await postAs(
    browser,
    'system_executor',
    '/api/system-services/security-response-decisions/' + decisionId + '/execute/permission-revocation',
    executionPayload,
    executionKey,
  );
  expect(replay.status).toBe(200);
  expect(replay.body).toEqual(executed.body);

  const wrongExecutor = await postAs(
    browser,
    'system_responder',
    '/api/system-services/security-response-decisions/' + decisionId + '/execute/permission-revocation',
    executionPayload,
    'browser-response-wrong-executor-' + state.database_name,
  );
  expect(wrongExecutor.status).toBe(403);
});

// ARTIFACT: system-services-response.browser.spec.js
// AUTHORITY BOUNDARY: authenticated browser plus disposable EOS authority
// END OF WILSY OS SOVEREIGN ARTIFACT
