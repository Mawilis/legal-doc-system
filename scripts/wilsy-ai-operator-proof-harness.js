/* eslint-disable */
import { resolveWilsyAIOperatorModel } from '../server/services/wilsyAI/wilsyAIOperatorModelService.js';
import { executeWilsyCalendarBridge } from '../server/services/wilsyAI/wilsyAICalendarExecutionBridge.js';

/**
 * @function buildProofHarnessRequest
 * @description Builds a request-shaped object for the Wilsy Operator Proof Harness.
 * @param {string} question - Operator question.
 * @param {Object} overrides - Request overrides.
 * @returns {Object} Request object.
 * @collaboration Operator Kernel proof harness, Calendar Execution Bridge, and deterministic smoke cases.
 */
function buildProofHarnessRequest(question = '', overrides = {}) {
  return {
    query: {
      wilsyAiContext: 'ASK',
      operatorQuestion: question,
      tenantId: 'MASTER',
      operatorId: 'P60K5Q10AP_PROOF_OPERATOR',
      workspaceRoute: '/crm/setup',
      workspaceSurface: 'CRM Meetings Tasks Leads Contacts Accounts Deals Pipeline Setup Evidence Sources Calendar Memo Reminder CRM Leads Proof Trail Sort Command Source Authority Evidence Ledger',
      ...(overrides.query || {}),
    },
    headers: {
      'x-tenant-id': 'MASTER',
      'x-operator-id': 'P60K5Q10AP_PROOF_OPERATOR',
      ...(overrides.headers || {}),
    },
    body: {
      ...(overrides.body || {}),
    },
  };
}

/**
 * @function summarizeProofHarnessResult
 * @description Produces compact proof output from an Operator Kernel response.
 * @param {Object} result - Operator Kernel result.
 * @returns {Object} Summary.
 * @collaboration Proof reporting, tool routing evidence, and CI-friendly assertions.
 */
function summarizeProofHarnessResult(result = {}) {
  const firstTool = result.toolRuns?.[0] || {};

  return {
    result: result.result,
    mutation: result.mutation,
    intent: result.operatorModel?.intent,
    action: result.operatorModel?.action,
    domain: result.operatorModel?.domain,
    supported: result.operatorModel?.supported,
    title: result.operatorModel?.title,
    answer: result.operatorModel?.answer,
    tool: firstTool.tool,
    status: firstTool.status,
    label: firstTool.label,
    eventLink: firstTool.eventLink || firstTool.crmCalendarLink || null,
    sourceTrace: result.operatorModel?.sourceTrace,
  };
}

/**
 * @function runWilsyOperatorProofHarness
 * @description Executes first-kernel proof cases for schedule, read, draft, and unsupported behavior.
 * @returns {Promise<Array<Object>>} Proof summaries.
 * @collaboration Calendar Execution Bridge, Operator Kernel, no-fake policy, and production readiness checks.
 */
export async function runWilsyOperatorProofHarness() {
  const questions = [
    'Can you schedule meeting with Wilsy OS Body of Directors on the 6th of July at 10 AM and duration 1 hour. Participants email address is wilsy.wk@gmail.com. We will discuss Wilsy AI prices and tiers.',
    'Schedule meeting for next week',
    'How many meetings do I have this week?',
    'Create a task to follow up with the board tomorrow',
    'Set a reminder to review Wilsy AI pricing tomorrow',
    'Generate a business meeting memo for Wilsy AI prices and tiers',
    'How many leads do we have?',
    'Write me a poem about Mars',
  ];
  const summaries = [];

  for (const question of questions) {
    const result = await resolveWilsyAIOperatorModel(buildProofHarnessRequest(question));
    const summary = summarizeProofHarnessResult(result);

    summaries.push(summary);
    console.log(JSON.stringify(summary, null, 2));

    if (result.result !== 'WILSY_AI_OPERATOR_MODEL_RESOLVED') {
      throw new Error(`Operator Kernel failed for question: ${question}`);
    }

    if (question.toLowerCase().includes('schedule meeting with') && result.operatorModel?.intent !== 'schedule_meeting') {
      throw new Error('Schedule request did not route to schedule_meeting.');
    }

    if (question.toLowerCase().includes('schedule meeting for next week') && result.toolRuns?.[0]?.status !== 'DRAFT_INCOMPLETE') {
      throw new Error('Incomplete schedule request did not request missing details.');
    }

    if (question.toLowerCase().includes('poem') && result.operatorModel?.supported !== false) {
      throw new Error('Unsupported request did not return supported=false.');
    }
  }

  const approvedBridge = await executeWilsyCalendarBridge({
    req: buildProofHarnessRequest(
      'Can you schedule meeting with Wilsy OS Body of Directors on the 6th of July at 10 AM and duration 1 hour. Participants email address is wilsy.wk@gmail.com. We will discuss Wilsy AI prices and tiers.',
      {
        query: {
          executionMode: 'APPROVED_EXECUTE',
          approvalToken: 'P60K5Q10AP_APPROVE_CALENDAR_WRITE',
          calendarConnector: 'crm',
        },
      }
    ),
    question:
      'Can you schedule meeting with Wilsy OS Body of Directors on the 6th of July at 10 AM and duration 1 hour. Participants email address is wilsy.wk@gmail.com. We will discuss Wilsy AI prices and tiers.',
    tenantId: 'MASTER',
    operatorId: 'P60K5Q10AP_PROOF_OPERATOR',
  });

  console.log(JSON.stringify({
    approvedCalendarBridge: {
      status: approvedBridge.status,
      connector: approvedBridge.connector,
      eventLink: approvedBridge.eventLink,
      crmCalendarLink: approvedBridge.crmCalendarLink,
      mutation: approvedBridge.mutation,
    },
  }, null, 2));

  return summaries;
}

/**
 * @function executeCli
 * @description Runs the proof harness from the command line.
 * @returns {Promise<void>} Completion promise.
 * @collaboration Wilsy guard scripts, proof harness execution, and production readiness evidence.
 */
async function executeCli() {
  await runWilsyOperatorProofHarness();
}

executeCli().catch((error) => {
  console.error(error);
  process.exit(1);
});
