/* eslint-disable */
import { resolveWilsyAIOperatorModel } from '../server/services/wilsyAI/wilsyAIOperatorModelService.js';

/**
 * @function buildCRMLeadsHarnessOverrides
 * @description Builds per-question CRM Leads viewpoint context for Operator Kernel proof cases.
 * @param {string} question - Operator proof question.
 * @returns {Object} Request overrides with CRM Leads context.
 * @collaboration Wilsy AI proof harness, CRM Leads Proof Trail, Sort Command, Source Authority, and Compliance Gap routing.
 */
function buildCRMLeadsHarnessOverrides(question = '') {
  const text = String(question || '').toLowerCase();

  if (!text.includes('crm leads') && !text.includes('leads')) {
    return {};
  }

  const baseContext = {
    visibleLeadCount: 12,
    sourceRouteCount: 4,
    sourceRouteLiveCount: 3,
    complianceVerified: 8,
    compliancePending: 3,
    complianceFailed: 1,
    activeSortField: 'lastActivity',
    activeSortDirection: 'desc',
    rootHash: 'p60k5q10fg45-root',
  };

  if (text.includes('sort command')) {
    return {
      query: {
        workspaceRoute: '/crm/leads',
        workspaceSurface: 'CRM Leads Sort Command Source Authority Evidence Ledger Compliance Gap',
      },
      body: {
        crmLeadsContext: {
          ...baseContext,
          activeTopTab: 'sort',
        },
      },
    };
  }

  if (text.includes('source authority')) {
    return {
      query: {
        workspaceRoute: '/crm/leads',
        workspaceSurface: 'CRM Leads Source Authority Evidence Ledger Compliance Gap',
      },
      body: {
        crmLeadsContext: {
          ...baseContext,
          activeTopTab: 'sources',
          sourceRouteLiveCount: 2,
        },
      },
    };
  }

  if (text.includes('compliance gap')) {
    return {
      query: {
        workspaceRoute: '/crm/leads',
        workspaceSurface: 'CRM Leads Compliance Gap Evidence Ledger Source Authority',
      },
      body: {
        crmLeadsContext: {
          ...baseContext,
          activeTopTab: 'records',
          complianceVerified: 7,
          compliancePending: 4,
          complianceFailed: 1,
        },
      },
    };
  }

  if (text.includes('proof trail')) {
    return {
      query: {
        workspaceRoute: '/crm/leads',
        workspaceSurface: 'CRM Leads Proof Trail Evidence Ledger Source Authority Compliance Gap',
      },
      body: {
        crmLeadsContext: {
          ...baseContext,
          activeTopTab: 'proof',
        },
      },
    };
  }

  return {
    query: {
      workspaceRoute: '/crm/leads',
      workspaceSurface: 'CRM Leads Records Proof Trail Sort Command Source Authority Evidence Ledger Compliance Gap',
    },
    body: {
      crmLeadsContext: {
        ...baseContext,
        activeTopTab: 'records',
      },
    },
  };
}

/**
 * @function mergeHarnessOverrides
 * @description Merges query, header, and body overrides without erasing CRM Leads context.
 * @param {Object} base - Base request object.
 * @param {Object} overrides - Request overrides.
 * @returns {Object} Merged request object.
 * @collaboration Wilsy AI proof harness, tenant-safe request construction, and deterministic operator tests.
 */
function mergeHarnessOverrides(base = {}, overrides = {}) {
  return {
    ...base,
    query: {
      ...(base.query || {}),
      ...(overrides.query || {}),
    },
    headers: {
      ...(base.headers || {}),
      ...(overrides.headers || {}),
    },
    body: {
      ...(base.body || {}),
      ...(overrides.body || {}),
    },
  };
}

/**
 * @function buildProofHarnessRequest
 * @description Builds a request-shaped object for the Wilsy Operator Proof Harness.
 * @param {string} question - Operator question.
 * @param {Object} overrides - Request overrides.
 * @returns {Object} Request object.
 * @collaboration Operator Kernel proof harness, CRM Leads viewpoint intelligence, and deterministic smoke cases.
 */
function buildProofHarnessRequest(question = '', overrides = {}) {
  const baseRequest = {
    query: {
      wilsyAiContext: 'ASK',
      operatorQuestion: question,
      tenantId: 'MASTER',
      operatorId: 'P60K5Q10AP_PROOF_OPERATOR',
      workspaceRoute: '/crm/setup',
      workspaceSurface: 'CRM Meetings Tasks Leads Contacts Accounts Deals Pipeline Setup Evidence Sources Calendar Memo Reminder',
    },
    headers: {
      'x-tenant-id': 'MASTER',
      'x-operator-id': 'P60K5Q10AP_PROOF_OPERATOR',
    },
    body: {},
  };

  return mergeHarnessOverrides(baseRequest, overrides);
}

/**
 * @function summarizeProofHarnessResult
 * @description Produces compact proof output from an Operator Kernel response.
 * @param {Object} result - Operator Kernel result.
 * @returns {Object} Summary.
 * @collaboration Proof reporting, CRM Leads viewpoint context, tool routing evidence, and CI-friendly assertions.
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
    responseSurface: result.operatorModel?.responseSurface,
    inlineCommandLinks: result.operatorModel?.inlineCommandLinks,
    crmLeadsViewpoint: result.operatorModel?.crmLeadsViewpoint,
    tool: firstTool.tool,
    status: firstTool.status,
    label: firstTool.label,
    eventLink: firstTool.eventLink || firstTool.crmCalendarLink || null,
    sourceTrace: result.operatorModel?.sourceTrace,
  };
}

/**
 * @function assertCRMLeadsProofResult
 * @description Validates CRM Leads proof routing, response surface, and inline command links.
 * @param {string} question - Proof question.
 * @param {Object} result - Operator Kernel result.
 * @returns {void}
 * @collaboration CRM Leads Proof Trail, Sort Command, Source Authority, Compliance Gap, and Wilsy AI response contract.
 */
function assertCRMLeadsProofResult(question = '', result = {}) {
  const text = String(question || '').toLowerCase();

  if (!text.includes('crm leads')) {
    return;
  }

  if (text.includes('proof trail') && result.operatorModel?.intent !== 'crm_leads_proof_trail_summary') {
    throw new Error('CRM Leads Proof Trail did not route to crm_leads_proof_trail_summary.');
  }

  if (text.includes('sort command') && result.operatorModel?.intent !== 'crm_leads_sort_strategy') {
    throw new Error('CRM Leads Sort Command did not route to crm_leads_sort_strategy.');
  }

  if (text.includes('source authority') && result.operatorModel?.intent !== 'crm_leads_source_risk_analysis') {
    throw new Error('CRM Leads Source Authority did not route to crm_leads_source_risk_analysis.');
  }

  if (text.includes('compliance gap') && result.operatorModel?.intent !== 'crm_leads_compliance_gap_next_action') {
    throw new Error('CRM Leads Compliance Gap did not route to crm_leads_compliance_gap_next_action.');
  }

  if (result.operatorModel?.responseSurface !== 'continuous_typographic') {
    throw new Error('CRM Leads AI response did not use the continuous typographic surface.');
  }

  if (!Array.isArray(result.operatorModel?.inlineCommandLinks)) {
    throw new Error('CRM Leads AI response did not include inline command links.');
  }
}

/**
 * @function assertOperatorHarnessResult
 * @description Validates generic Operator Kernel proof result safety.
 * @param {string} question - Proof question.
 * @param {Object} result - Operator Kernel result.
 * @returns {void}
 * @collaboration Operator Kernel smoke coverage, no-fake answer policy, and CRM Leads AI routing.
 */
function assertOperatorHarnessResult(question = '', result = {}) {
  if (result.result !== 'WILSY_AI_OPERATOR_MODEL_RESOLVED') {
    throw new Error(`Operator Kernel failed for question: ${question}`);
  }

  assertCRMLeadsProofResult(question, result);
}

/**
 * @function runWilsyOperatorProofHarness
 * @description Executes Operator Kernel proof cases for scheduling, reading, tasking, drafting, and CRM Leads viewpoint intelligence.
 * @returns {Promise<Array<Object>>} Proof summaries.
 * @collaboration Calendar Execution Bridge, Operator Kernel, CRM Leads viewpoint intelligence, no-fake policy, and production readiness checks.
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
    'In CRM Leads Proof Trail, summarize source risk and compliance gaps.',
    'In CRM Leads Sort Command, recommend the best lead ordering strategy.',
    'In CRM Leads Source Authority, what evidence route should I repair first.',
    'In CRM Leads Compliance Gap, tell me what to fix next.',
    'Write me a poem about Mars',
  ];
  const summaries = [];

  for (const question of questions) {
    const result = await resolveWilsyAIOperatorModel(
      buildProofHarnessRequest(question, buildCRMLeadsHarnessOverrides(question))
    );
    const summary = summarizeProofHarnessResult(result);

    summaries.push(summary);
    console.log(JSON.stringify(summary, null, 2));

    assertOperatorHarnessResult(question, result);
  }

  return summaries;
}

if (import.meta.url === `file://${process.argv[1]}`) {
  runWilsyOperatorProofHarness()
    .then((summaries) => {
      console.log(JSON.stringify({ result: 'WILSY_OPERATOR_PROOF_HARNESS_PASSED', count: summaries.length }, null, 2));
    })
    .catch((error) => {
      console.error(error);
      process.exitCode = 1;
    });
}
