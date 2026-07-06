/* eslint-disable */
import {
  buildWilsyCapabilityFoundryToolRun,
  stageWilsyCapabilityCandidate,
} from '../server/services/wilsyAI/wilsyAICapabilityFoundryService.js';

/**
 * @function buildFoundryHarnessCase
 * @description Builds a Capability Foundry proof case.
 * @param {string} question - Tenant question.
 * @param {Object} intent - Intent object.
 * @param {Object} tool - Tool object.
 * @returns {Object} Harness case.
 * @collaboration Capability Foundry proof harness, missing tool simulation, and approval-gated registry expansion.
 */
function buildFoundryHarnessCase(question = '', intent = {}, tool = {}) {
  return {
    question,
    intent,
    tool,
    tenantId: 'MASTER',
    operatorId: 'P60K5Q10AR_FOUNDRY_OPERATOR',
    workspaceRoute: '/crm/setup',
    workspaceSurface: 'CRM Calendar Communications Finance Documents Analytics Evidence',
  };
}

/**
 * @function summarizeFoundryCandidate
 * @description Summarizes a Capability Foundry candidate for proof output.
 * @param {Object} candidate - Candidate result.
 * @returns {Object} Summary.
 * @collaboration Proof reporting, candidate review, and CI-friendly assertions.
 */
function summarizeFoundryCandidate(candidate = {}) {
  const toolRun = buildWilsyCapabilityFoundryToolRun(candidate);

  return {
    candidateId: candidate.candidateId,
    capabilityId: candidate.capabilityId,
    businessName: candidate.businessName,
    status: candidate.status,
    approvalRequired: candidate.approvalRequired,
    evidenceRequired: candidate.evidenceRequired,
    quarantinePath: candidate.quarantinePath,
    proofCaseCount: candidate.proofCases?.length || 0,
    promotionGateCount: candidate.promotionGates?.length || 0,
    persistence: candidate.persistence,
    toolRun,
  };
}

/**
 * @function runWilsyCapabilityFoundryProofHarness
 * @description Runs proof cases for Capability Foundry candidate staging.
 * @returns {Promise<Array<Object>>} Candidate summaries.
 * @collaboration Missing capability detection, quarantine artifact generation, and no-auto-publish guarantee.
 */
export async function runWilsyCapabilityFoundryProofHarness() {
  const cases = [
    buildFoundryHarnessCase(
      'Send this board memo to wilsy.wk@gmail.com',
      { intent: 'unsupported_question', domain: 'communications', action: 'unsupported', missingTool: 'email_send' },
      { tool: 'email_send', status: 'TOOL_MISSING', domain: 'communications' }
    ),
    buildFoundryHarnessCase(
      'Generate an invoice for Wilsy AI enterprise tier',
      { intent: 'unsupported_question', domain: 'finance', action: 'unsupported', missingTool: 'invoice_generate' },
      { tool: 'invoice_generate', status: 'TOOL_MISSING', domain: 'finance' }
    ),
    buildFoundryHarnessCase(
      'Connect Google Calendar so I can create event links',
      { intent: 'schedule_meeting', domain: 'calendar', action: 'calendar_execution_bridge' },
      { tool: 'calendar_execution_bridge', status: 'CONNECTOR_UNAVAILABLE', domain: 'calendar' }
    ),
    buildFoundryHarnessCase(
      'Generate a board proposal document',
      { intent: 'unsupported_question', domain: 'documents', action: 'unsupported', missingTool: 'business_document_generate' },
      { tool: 'business_document_generate', status: 'TOOL_MISSING', domain: 'documents' }
    ),
  ];
  const summaries = [];

  for (const item of cases) {
    const candidate = await stageWilsyCapabilityCandidate(item);
    const summary = summarizeFoundryCandidate(candidate);

    summaries.push(summary);
    console.log(JSON.stringify(summary, null, 2));

    if (candidate.status !== 'STAGED_FOR_REVIEW') {
      throw new Error(`Candidate was not staged: ${item.question}`);
    }

    if (candidate.publication?.autoPublish !== false || candidate.publication?.published !== false) {
      throw new Error(`Candidate auto-published unsafely: ${candidate.candidateId}`);
    }

    if (!candidate.proofCases || candidate.proofCases.length < 6) {
      throw new Error(`Candidate lacks proof cases: ${candidate.candidateId}`);
    }

    if (!candidate.quarantinePath) {
      throw new Error(`Candidate lacks quarantine path: ${candidate.candidateId}`);
    }
  }

  return summaries;
}

/**
 * @function executeCli
 * @description Executes the Capability Foundry proof harness from CLI.
 * @returns {Promise<void>} Completion promise.
 * @collaboration Wilsy guard scripts, proof harness execution, and production readiness evidence.
 */
async function executeCli() {
  await runWilsyCapabilityFoundryProofHarness();
}

executeCli().catch((error) => {
  console.error(error);
  process.exit(1);
});
