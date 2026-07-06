/* eslint-disable */

/**
 * @function coerceWilsyRegistryText
 * @description Safely coerces registry values into bounded business text.
 * @param {unknown} value - Raw value.
 * @param {number} limit - Maximum length.
 * @returns {string} Bounded text.
 * @collaboration Wilsy Tool Registry, Capability Foundry, and tenant-safe manifest creation.
 */
function coerceWilsyRegistryText(value = '', limit = 1400) {
  return String(value || '')
    .replace(/\s+/g, ' ')
    .trim()
    .slice(0, limit);
}

/**
 * @function normalizeWilsyCapabilityId
 * @description Normalizes a capability name into a safe capability id.
 * @param {string} value - Capability name.
 * @returns {string} Safe capability id.
 * @collaboration Capability quarantine paths, registry records, and approval-safe publication.
 */
export function normalizeWilsyCapabilityId(value = '') {
  return (
    coerceWilsyRegistryText(value, 180)
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, '_')
      .replace(/^_+|_+$/g, '')
      .slice(0, 80) || 'custom_business_capability'
  );
}

/**
 * @function getWilsyApprovedToolRegistry
 * @description Returns production-approved Wilsy AI tool categories.
 * @returns {Object} Approved tool registry.
 * @collaboration Operator Kernel, Calendar Execution Bridge, CRM source tools, and Capability Foundry gap detection.
 */
export function getWilsyApprovedToolRegistry() {
  return {
    crm_source_reader: {
      businessName: 'CRM Source Reader',
      status: 'APPROVED',
      mutationRisk: 'read',
      approvalRequired: false,
      domains: [
        'meetings',
        'tasks',
        'leads',
        'contacts',
        'accounts',
        'deals',
        'pipeline',
        'setup',
        'evidence',
        'sources',
      ],
    },
    calendar_execution_bridge: {
      businessName: 'Calendar Execution Bridge',
      status: 'APPROVED',
      mutationRisk: 'write',
      approvalRequired: true,
      domains: ['meetings', 'calendar'],
    },
    task_draft: {
      businessName: 'Task Draft',
      status: 'APPROVED_DRAFT_ONLY',
      mutationRisk: 'draft',
      approvalRequired: true,
      domains: ['tasks'],
    },
    reminder_draft: {
      businessName: 'Reminder Draft',
      status: 'APPROVED_DRAFT_ONLY',
      mutationRisk: 'draft',
      approvalRequired: true,
      domains: ['tasks', 'reminders'],
    },
    business_memo_draft: {
      businessName: 'Business Memo Draft',
      status: 'APPROVED_DRAFT_ONLY',
      mutationRisk: 'draft',
      approvalRequired: true,
      domains: ['documents', 'evidence'],
    },
  };
}

/**
 * @function inferWilsyCapabilityBlueprint
 * @description Infers the missing reusable capability from a tenant request.
 * @param {Object} params - Inference parameters.
 * @param {string} params.question - Tenant question.
 * @param {Object} params.intent - Operator intent.
 * @param {Object} params.tool - Failed or missing tool.
 * @returns {Object} Capability blueprint.
 * @collaboration Missing capability detection, self-extending registry, and production no-fake-answer policy.
 */
export function inferWilsyCapabilityBlueprint({ question = '', intent = {}, tool = {} } = {}) {
  const text = coerceWilsyRegistryText(question, 1600).toLowerCase();
  const toolStatus = String(tool.status || '').toUpperCase();

  if (/email|send mail|mail/i.test(text)) {
    return {
      capabilityId: 'email_send',
      businessName: 'Send Email',
      domain: 'communications',
      action: 'send_email',
      mutationRisk: 'write',
      approvalRequired: true,
      connectors: ['SMTP', 'Google Gmail', 'Microsoft Graph Mail'],
      intentExamples: ['send an email', 'email the client', 'send this memo to the board'],
      requiredInputs: ['recipients', 'subject', 'body', 'tenantId', 'operatorId'],
    };
  }

  if (/invoice|quote|quotation|bill/i.test(text)) {
    return {
      capabilityId: 'invoice_or_quote_generate',
      businessName: 'Generate Invoice or Quote',
      domain: 'finance',
      action: 'generate_commercial_document',
      mutationRisk: 'write',
      approvalRequired: true,
      connectors: ['Revenue Ledger', 'Billing Engine', 'Document Generator'],
      intentExamples: ['create an invoice', 'generate a quote', 'prepare billing document'],
      requiredInputs: ['customer', 'lineItems', 'amounts', 'taxProfile', 'approval'],
    };
  }

  if (/contract|proposal|agreement|letter|document/i.test(text)) {
    return {
      capabilityId: 'business_document_generate',
      businessName: 'Generate Business Document',
      domain: 'documents',
      action: 'generate_document',
      mutationRisk: 'draft',
      approvalRequired: true,
      connectors: ['Document Generator', 'Evidence Vault', 'Template Registry'],
      intentExamples: ['generate a proposal', 'draft an agreement', 'create a business letter'],
      requiredInputs: ['documentType', 'parties', 'purpose', 'content', 'approval'],
    };
  }

  if (/whatsapp|sms|text message|message client/i.test(text)) {
    return {
      capabilityId: 'tenant_message_send',
      businessName: 'Send Tenant Message',
      domain: 'communications',
      action: 'send_message',
      mutationRisk: 'write',
      approvalRequired: true,
      connectors: ['SMS Gateway', 'WhatsApp Business', 'Notification Service'],
      intentExamples: ['send SMS', 'message the client', 'send WhatsApp update'],
      requiredInputs: ['recipient', 'message', 'channel', 'approval'],
    };
  }

  if (
    /calendar|meeting|appointment|schedule|book/i.test(text) &&
    ['CONNECTOR_UNAVAILABLE', 'CONNECTOR_FAILED'].includes(toolStatus)
  ) {
    return {
      capabilityId: 'calendar_connector_bind',
      businessName: 'Bind Calendar Connector',
      domain: 'calendar',
      action: 'bind_calendar_connector',
      mutationRisk: 'configuration',
      approvalRequired: true,
      connectors: ['CRM Calendar', 'Google Calendar', 'Microsoft Graph Calendar'],
      intentExamples: [
        'connect Google Calendar',
        'connect Microsoft Calendar',
        'create event link',
      ],
      requiredInputs: ['provider', 'tenantOAuth', 'calendarId', 'approval'],
    };
  }

  if (/dashboard|report|analytics|forecast|trend|insight/i.test(text)) {
    return {
      capabilityId: 'analytics_report_generate',
      businessName: 'Generate Analytics Report',
      domain: 'analytics',
      action: 'generate_report',
      mutationRisk: 'read',
      approvalRequired: false,
      connectors: ['CRM Analytics', 'Revenue Ledger', 'Evidence Vault'],
      intentExamples: ['generate a sales report', 'show pipeline forecast', 'summarize trends'],
      requiredInputs: ['metric', 'dateRange', 'tenantScope'],
    };
  }

  return {
    capabilityId: normalizeWilsyCapabilityId(
      intent.missingTool || tool.tool || 'custom_business_capability'
    ),
    businessName: 'Custom Business Capability',
    domain: intent.domain || tool.domain || 'general',
    action: intent.action || 'custom_tool_required',
    mutationRisk: 'unknown',
    approvalRequired: true,
    connectors: ['Capability Foundry'],
    intentExamples: [coerceWilsyRegistryText(question, 180)],
    requiredInputs: ['businessGoal', 'tenantScope', 'operatorApproval', 'evidencePolicy'],
  };
}

/**
 * @function buildWilsyCapabilityManifest
 * @description Builds a governed capability manifest for a missing tool.
 * @param {Object} params - Manifest parameters.
 * @param {Object} params.blueprint - Capability blueprint.
 * @param {string} params.question - Tenant question.
 * @param {string} params.tenantId - Tenant id.
 * @param {string} params.operatorId - Operator id.
 * @returns {Object} Capability manifest.
 * @collaboration Capability Foundry, tool contracts, approval gates, and self-extending registry.
 */
export function buildWilsyCapabilityManifest({
  blueprint = {},
  question = '',
  tenantId = 'MASTER',
  operatorId = 'WILSY_OPERATOR',
} = {}) {
  const capabilityId = normalizeWilsyCapabilityId(blueprint.capabilityId || blueprint.businessName);

  return {
    contractVersion: 'P60K5Q10AR_CAPABILITY_MANIFEST',
    capabilityId,
    businessName: blueprint.businessName || 'Custom Business Capability',
    domain: blueprint.domain || 'general',
    action: blueprint.action || 'custom_tool_required',
    status: 'STAGED_FOR_REVIEW',
    mutationRisk: blueprint.mutationRisk || 'unknown',
    approvalRequired: blueprint.approvalRequired !== false,
    evidenceRequired: true,
    generatedAt: new Date().toISOString(),
    requestedBy: {
      tenantId,
      operatorId,
    },
    sourceQuestion: coerceWilsyRegistryText(question, 1200),
    intentExamples: blueprint.intentExamples || [],
    requiredInputs: blueprint.requiredInputs || [],
    connectors: blueprint.connectors || [],
    publicationPolicy: {
      autoPublish: false,
      humanApprovalRequired: true,
      tenantIsolationRequired: true,
      noMutationWithoutApproval: true,
      rollbackRequired: true,
    },
  };
}

/**
 * @function buildWilsyToolContract
 * @description Builds a tool contract for the capability candidate.
 * @param {Object} manifest - Capability manifest.
 * @returns {Object} Tool contract.
 * @collaboration Tool registry, validation schemas, approval workflow, and evidence receipts.
 */
export function buildWilsyToolContract(manifest = {}) {
  return {
    contractVersion: 'P60K5Q10AR_TOOL_CONTRACT',
    capabilityId: manifest.capabilityId,
    businessName: manifest.businessName,
    inputSchema: {
      type: 'object',
      required: manifest.requiredInputs || [],
      properties: Object.fromEntries(
        (manifest.requiredInputs || []).map((input) => [input, { type: 'string' }])
      ),
    },
    outputSchema: {
      type: 'object',
      required: [
        'result',
        'businessAnswer',
        'sourceTrace',
        'institutionalHeaders',
        'strikePayload',
      ],
      properties: {
        result: { type: 'string' },
        businessAnswer: { type: 'string' },
        sourceTrace: { type: 'array' },
        mutation: { type: 'boolean' },
        evidenceReceipt: { type: 'object' },
      },
    },
    permissions: {
      tenantScoped: true,
      operatorScoped: true,
      approvalRequired: manifest.approvalRequired,
      mutationRisk: manifest.mutationRisk,
    },
    evidenceContract: {
      institutionalHeadersRequired: true,
      strikePayloadRequired: true,
      sourceTraceRequired: true,
      noFakeAnswerRequired: true,
    },
    rollback: {
      required: manifest.mutationRisk !== 'read',
      strategy: 'tool-specific rollback plan required before approval',
    },
  };
}

/**
 * @function buildWilsyCapabilityProofCases
 * @description Builds proof cases required before capability promotion.
 * @param {Object} manifest - Capability manifest.
 * @returns {Array<Object>} Proof cases.
 * @collaboration Proof harness, tenant isolation, no-fake fallback, approval safety, and source tracing.
 */
export function buildWilsyCapabilityProofCases(manifest = {}) {
  return [
    {
      caseId: 'intent-routing',
      requirement: `Route tenant requests to ${manifest.capabilityId}`,
      expected: 'Correct tool selected before domain fallback.',
    },
    {
      caseId: 'required-inputs',
      requirement: 'Detect missing required inputs.',
      expected: 'Missing fields are requested in business English.',
    },
    {
      caseId: 'tenant-isolation',
      requirement: 'Restrict data/tool execution to tenant scope.',
      expected: 'No cross-tenant data access.',
    },
    {
      caseId: 'approval-gate',
      requirement: 'Block write/configuration actions without approval.',
      expected: 'No mutation when approval is absent.',
    },
    {
      caseId: 'source-trace',
      requirement: 'Return source/tool checked.',
      expected: 'Every answer includes sourceTrace.',
    },
    {
      caseId: 'evidence-receipt',
      requirement: 'Return institutionalHeaders and strikePayload.',
      expected: 'Evidence contract is complete.',
    },
    {
      caseId: 'no-fake-answer',
      requirement: 'Do not hallucinate unsupported capability.',
      expected: 'Unsupported path stages candidate and tells truth.',
    },
  ];
}

/**
 * @function buildWilsyPromotionGates
 * @description Builds mandatory promotion gates for a capability candidate.
 * @returns {Array<string>} Promotion gate names.
 * @collaboration Guard discipline, approval workflow, build safety, and production publication.
 */
export function buildWilsyPromotionGates() {
  return [
    'Secret Guard',
    'Documentation Guard',
    'Syntax Check',
    'Client Build',
    'Tool Routing Evaluation',
    'Tenant Isolation Evaluation',
    'Mutation Approval Evaluation',
    'Evidence Receipt Evaluation',
    'Rollback Plan Review',
    'Load Smoke Test',
    'Human/Admin Approval',
  ];
}
