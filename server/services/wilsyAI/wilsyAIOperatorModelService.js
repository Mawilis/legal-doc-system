/* eslint-disable */
import mongoose from 'mongoose';
import { resolveWilsyAISovereignContext } from './wilsyAISovereignContextService.js';
import { executeWilsyCalendarBridge } from './wilsyAICalendarExecutionBridge.js';
import {
  buildWilsyCapabilityFoundryToolRun,
  stageWilsyCapabilityCandidate,
} from './wilsyAICapabilityFoundryService.js';

import { executeWilsyTaskReminderBridge } from './wilsyAITaskReminderExecutionBridge.js';
import { executeWilsyBusinessDocumentDraftBridge } from './wilsyAIBusinessDocumentDraftBridge.js';
import { resolveWilsyAICRMLeadsViewpointModel } from './wilsyAICRMLeadsViewpointIntelligenceService.js';
/**
 * @function coerceWilsyOperatorText
 * @description Safely coerces operator input into bounded business text.
 * @param {unknown} value - Raw value.
 * @param {number} limit - Max length.
 * @returns {string} Bounded text.
 * @collaboration Wilsy Operator Kernel, tenant-safe request handling, and browser input boundaries.
 */
function coerceWilsyOperatorText(value = '', limit = 1400) {
  return String(value || '')
    .replace(/\s+/g, ' ')
    .trim()
    .slice(0, limit);
}

/**
 * @function formatWilsyBusinessLabel
 * @description Converts backend identifiers into business-English labels.
 * @param {string} value - Raw label.
 * @returns {string} Business label.
 * @collaboration Operator Kernel source trace, tenant-facing answers, and no-backend-language responses.
 */
function formatWilsyBusinessLabel(value = '') {
  return coerceWilsyOperatorText(value, 200)
    .replace(/^crm_/, '')
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

/**
 * @function buildWilsyDateWindow
 * @description Resolves common date-window language for read-only CRM source tools.
 * @param {string} question - Operator question.
 * @param {Date} now - Current date.
 * @returns {{start: Date, end: Date, label: string, scope: string}} Date window.
 * @collaboration Meetings, Tasks, Pipeline, Evidence, and CRM Operator source tools.
 */
function buildWilsyDateWindow(question = '', now = new Date()) {
  const text = coerceWilsyOperatorText(question, 1000).toLowerCase();
  const base = new Date(now);
  const startOfDay = new Date(base);

  startOfDay.setHours(0, 0, 0, 0);

  if (text.includes('today')) {
    const end = new Date(startOfDay);
    end.setDate(end.getDate() + 1);

    return { start: startOfDay, end, label: startOfDay.toISOString().slice(0, 10), scope: 'today' };
  }

  if (text.includes('tomorrow')) {
    const start = new Date(startOfDay);
    start.setDate(start.getDate() + 1);
    const end = new Date(start);
    end.setDate(end.getDate() + 1);

    return { start, end, label: start.toISOString().slice(0, 10), scope: 'tomorrow' };
  }

  if (text.includes('next week')) {
    const day = base.getDay();
    const daysUntilNextMonday = (8 - day) % 7 || 7;
    const start = new Date(startOfDay);
    start.setDate(start.getDate() + daysUntilNextMonday);
    const end = new Date(start);
    end.setDate(end.getDate() + 7);

    return {
      start,
      end,
      label: `${start.toISOString().slice(0, 10)} to ${end.toISOString().slice(0, 10)}`,
      scope: 'next week',
    };
  }

  const day = base.getDay();
  const mondayOffset = day === 0 ? -6 : 1 - day;
  const start = new Date(startOfDay);
  start.setDate(start.getDate() + mondayOffset);
  const end = new Date(start);
  end.setDate(end.getDate() + 7);

  return {
    start,
    end,
    label: `${start.toISOString().slice(0, 10)} to ${end.toISOString().slice(0, 10)}`,
    scope: 'this week',
  };
}

/**
 * @function buildTenantFilterCandidates
 * @description Builds tenant filter candidates for multi-tenant source queries.
 * @param {string} tenantId - Tenant id.
 * @returns {Array<Object>} Mongo filter candidates.
 * @collaboration Tenant isolation, CRM source adapters, and no-mutation tool execution.
 */
function buildTenantFilterCandidates(tenantId = 'MASTER') {
  return [
    { tenantId },
    { tenant: tenantId },
    { 'tenant.id': tenantId },
    { 'metadata.tenantId': tenantId },
    { 'institutionalHeaders.tenantId': tenantId },
    {},
  ];
}

/**
 * @function getWilsyCrmToolRegistry
 * @description Returns the first production CRM Operator Kernel read-tool registry.
 * @returns {Object} CRM tool registry.
 * @collaboration Meetings, Tasks, Leads, Contacts, Accounts, Deals, Pipeline, Setup, Evidence, Sources, and CRM source routing.
 */
function getWilsyCrmToolRegistry() {
  return {
    meetings: {
      label: 'meetings',
      collections: [
        'meetings',
        'crmmeetings',
        'crm_meetings',
        'meetingrecords',
        'meeting_records',
        'calendar_events',
        'crm_calendar_events',
        'events',
        'crm_tasks',
      ],
      collectionPattern: /meeting|calendar|event|appointment/i,
      titleFields: ['title', 'subject', 'name'],
      dateFields: [
        'dueAt',
        'dueDate',
        'meetingDate',
        'scheduledAt',
        'startAt',
        'startsAt',
        'startTime',
        'startDateTime',
        'date',
        'eventDate',
        'nextDueAt',
      ],
      defaultWindow: true,
    },
    tasks: {
      label: 'tasks',
      collections: ['tasks', 'crm_tasks', 'crmtasks', 'taskrecords', 'task_records'],
      collectionPattern: /task|todo|follow/i,
      titleFields: ['title', 'subject', 'name'],
      dateFields: ['dueAt', 'dueDate', 'scheduledAt', 'startAt', 'date', 'nextDueAt'],
      defaultWindow: true,
    },
    leads: {
      label: 'leads',
      collections: ['leads', 'crmleads', 'crm_leads', 'leadrecords', 'lead_records'],
      collectionPattern: /lead|prospect/i,
      titleFields: ['name', 'title', 'company', 'email'],
      dateFields: ['createdAt', 'updatedAt', 'nextDueAt', 'followUpAt', 'dueAt'],
      defaultWindow: false,
    },
    contacts: {
      label: 'contacts',
      collections: ['contacts', 'crmcontacts', 'crm_contacts', 'contactrecords', 'contact_records'],
      collectionPattern: /contact/i,
      titleFields: ['name', 'fullName', 'email', 'company'],
      dateFields: ['createdAt', 'updatedAt', 'lastContactedAt'],
      defaultWindow: false,
    },
    accounts: {
      label: 'accounts',
      collections: [
        'accounts',
        'crmaccounts',
        'crm_accounts',
        'accountrecords',
        'account_records',
        'companies',
        'organizations',
      ],
      collectionPattern: /account|company|organization/i,
      titleFields: ['name', 'company', 'legalName'],
      dateFields: ['createdAt', 'updatedAt'],
      defaultWindow: false,
    },
    deals: {
      label: 'deals',
      collections: [
        'deals',
        'crmdeals',
        'crm_deals',
        'opportunities',
        'crm_opportunities',
        'pipelines',
      ],
      collectionPattern: /deal|opportunit|pipeline/i,
      titleFields: ['name', 'title', 'dealName', 'company'],
      dateFields: ['closeDate', 'expectedCloseAt', 'createdAt', 'updatedAt'],
      valueFields: ['amount', 'value', 'expectedValue', 'dealValue', 'weightedValue'],
      defaultWindow: false,
    },
    pipeline: {
      label: 'pipeline records',
      collections: [
        'deals',
        'crmdeals',
        'crm_deals',
        'opportunities',
        'crm_opportunities',
        'pipelines',
        'pipeline_stages',
      ],
      collectionPattern: /deal|opportunit|pipeline|stage/i,
      titleFields: ['name', 'title', 'stage', 'dealName'],
      dateFields: ['closeDate', 'expectedCloseAt', 'createdAt', 'updatedAt'],
      valueFields: ['amount', 'value', 'expectedValue', 'dealValue', 'weightedValue'],
      defaultWindow: false,
    },
    setup: {
      label: 'setup controls',
      collections: [
        'crm_setup_controls',
        'crm_setup_packets',
        'crm_setup_reviews',
        'setup_reviews',
        'setup_packets',
        'setup_controls',
      ],
      collectionPattern: /setup|control|review|packet/i,
      titleFields: ['name', 'title', 'controlName', 'packetId'],
      dateFields: ['createdAt', 'updatedAt', 'reviewedAt', 'stagedAt'],
      defaultWindow: false,
    },
    evidence: {
      label: 'evidence receipts',
      collections: [
        'crm_evidence',
        'evidence_receipts',
        'audit_receipts',
        'auditevents',
        'forensiclogs',
        'forensic_logs',
        'crm_governance_events',
      ],
      collectionPattern: /evidence|receipt|audit|forensic|governance/i,
      titleFields: ['name', 'title', 'event', 'action', 'receiptId'],
      dateFields: ['createdAt', 'updatedAt', 'generatedAt', 'timestamp'],
      defaultWindow: false,
    },
    sources: {
      label: 'source routes',
      collections: [
        'crm_source_routes',
        'source_routes',
        'sources',
        'connectors',
        'crm_connectors',
        'integrations',
      ],
      collectionPattern: /source|connector|integration|route/i,
      titleFields: ['name', 'title', 'sourceName', 'route'],
      dateFields: ['createdAt', 'updatedAt', 'lastSyncedAt'],
      defaultWindow: false,
    },
  };
}

/**
 * @function inferWilsyOperatorIntent
 * @description Infers action-first intent before domain routing.
 * @param {string} question - Operator request.
 * @returns {{intent: string, domain: string|null, action: string, supported: boolean, missingTool: string|null}} Intent.
 * @collaboration Action router, Calendar Execution Bridge, CRM read tools, and no-fake unsupported handling.
 */
function inferWilsyOperatorIntent(question = '') {
  const text = coerceWilsyOperatorText(question, 1800).toLowerCase();

  if (
    /\b(schedule|book|arrange|set up)\b/.test(text) &&
    /\b(meeting|call|appointment)\b/.test(text)
  ) {
    return {
      intent: 'schedule_meeting',
      domain: 'meetings',
      action: 'calendar_execution_bridge',
      supported: true,
      missingTool: null,
    };
  }

  if (/\b(remind me|reminder|set reminder)\b/.test(text)) {
    return {
      intent: 'reminder_draft',
      domain: 'tasks',
      action: 'draft_reminder',
      supported: true,
      missingTool: null,
    };
  }

  if (/\b(create|add|assign|set)\b/.test(text) && /\b(task|todo|to-do)\b/.test(text)) {
    return {
      intent: 'task_draft',
      domain: 'tasks',
      action: 'draft_task',
      supported: true,
      missingTool: null,
    };
  }

  if (
    /\b(send|email|mail|deliver|share|forward|generate|draft|create|prepare)\b/.test(text) &&
    /\b(contract|form|proposal|agreement|letter|document)\b/.test(text)
  ) {
    return {
      intent: 'business_document_draft',
      domain: 'documents',
      action: 'business_document_draft',
      supported: true,
      missingTool: null,
    };
  }

  if (
    /\b(memo|minutes|agenda|brief|business meeting memo|meeting memo)\b/.test(text) &&
    /\b(generate|draft|create|write|prepare|make)\b/.test(text)
  ) {
    return {
      intent: 'business_memo_draft',
      domain: 'evidence',
      action: 'draft_memo',
      supported: true,
      missingTool: null,
    };
  }

  const domainRules = [
    ['meetings', /\bmeeting\b|\bmeetings\b|calendar|appointment|event\b|events\b/],
    ['tasks', /\btask\b|\btasks\b|todo|to-do|follow up|follow-up|due work/],
    ['leads', /\blead\b|\bleads\b|prospect|prospects/],
    ['contacts', /\bcontact\b|\bcontacts\b|people|person/],
    ['accounts', /\baccount\b|\baccounts\b|company|companies|organization|organizations/],
    ['deals', /\bdeal\b|\bdeals\b|opportunity|opportunities/],
    ['pipeline', /pipeline|stage|forecast|weighted|revenue/],
    ['setup', /setup|authority|release readiness|approval|control|packet|review/],
    ['evidence', /evidence|receipt|proof|audit|forensic/],
    ['sources', /source|sources|connector|connectors|sync|integration|route/],
  ];

  for (const [domain, pattern] of domainRules) {
    if (pattern.test(text)) {
      return {
        intent: `crm_${domain}_read`,
        domain,
        action: 'read_source',
        supported: true,
        missingTool: null,
      };
    }
  }

  return {
    intent: 'unsupported_question',
    domain: null,
    action: 'unsupported',
    supported: false,
    missingTool: 'registered business tool',
  };
}

/**
 * @function listWilsyDomainCollections
 * @description Lists available MongoDB collections for a CRM source domain.
 * @param {string} domain - Tool domain.
 * @returns {Promise<Array<string>>} Available collections.
 * @collaboration MongoDB source discovery, CRM Operator Kernel, and tenant-safe read execution.
 */
async function listWilsyDomainCollections(domain = 'meetings') {
  const db = mongoose.connection?.db;

  if (!db) {
    return [];
  }

  const registry = getWilsyCrmToolRegistry();
  const config = registry[domain] || registry.meetings;
  const collectionNames = await db
    .listCollections({}, { nameOnly: true })
    .toArray()
    .then((collections) => collections.map((collection) => collection.name))
    .catch(() => []);
  const dynamic = collectionNames.filter((name) => config.collectionPattern.test(name));

  return [...new Set([...config.collections, ...dynamic])].filter((name) =>
    collectionNames.includes(name)
  );
}

/**
 * @function buildWilsyDateFilters
 * @description Builds date filters for a source domain.
 * @param {string} domain - Tool domain.
 * @param {Object} window - Date window.
 * @returns {Array<Object>} Mongo filters.
 * @collaboration Meetings, Tasks, date-window questions, and CRM source tooling.
 */
function buildWilsyDateFilters(domain = 'meetings', window = buildWilsyDateWindow('this week')) {
  const registry = getWilsyCrmToolRegistry();
  const config = registry[domain] || registry.meetings;

  return config.dateFields.map((field) => ({
    [field]: {
      $gte: window.start,
      $lt: window.end,
    },
  }));
}

/**
 * @function shouldApplyWilsyDateWindow
 * @description Determines whether a query should use a date window.
 * @param {string} domain - Tool domain.
 * @param {string} question - Operator question.
 * @returns {boolean} Whether date filtering is needed.
 * @collaboration Meetings, Tasks, natural date questions, and CRM source tools.
 */
function shouldApplyWilsyDateWindow(domain = 'meetings', question = '') {
  const registry = getWilsyCrmToolRegistry();
  const config = registry[domain] || registry.meetings;
  const text = coerceWilsyOperatorText(question, 1200).toLowerCase();

  if (config.defaultWindow) {
    return true;
  }

  return /today|tomorrow|this week|next week|this month|due|scheduled|follow/i.test(text);
}

/**
 * @function buildWilsyProjection
 * @description Builds source sample projection.
 * @param {string} domain - Tool domain.
 * @returns {Object} Mongo projection.
 * @collaboration CRM source samples, business answers, and source traceability.
 */
function buildWilsyProjection(domain = 'meetings') {
  const registry = getWilsyCrmToolRegistry();
  const config = registry[domain] || registry.meetings;
  const projection = {
    _id: 1,
    status: 1,
    stage: 1,
    tenantId: 1,
    createdAt: 1,
    updatedAt: 1,
  };

  [
    ...(config.titleFields || []),
    ...(config.dateFields || []),
    ...(config.valueFields || []),
  ].forEach((field) => {
    projection[field] = 1;
  });

  return projection;
}

/**
 * @function extractWilsySourceTitle
 * @description Extracts a business title from a source record.
 * @param {Object} row - Source row.
 * @param {string} domain - Tool domain.
 * @returns {string} Title.
 * @collaboration Source samples, operator answers, and tenant-readable evidence.
 */
function extractWilsySourceTitle(row = {}, domain = 'meetings') {
  const registry = getWilsyCrmToolRegistry();
  const config = registry[domain] || registry.meetings;

  for (const field of config.titleFields || []) {
    if (row[field]) {
      return coerceWilsyOperatorText(row[field], 120);
    }
  }

  return `Untitled ${config.label}`;
}

/**
 * @function extractWilsySourceDate
 * @description Extracts a relevant date from a source record.
 * @param {Object} row - Source row.
 * @param {string} domain - Tool domain.
 * @returns {unknown} Date value.
 * @collaboration Due-window answers, CRM samples, and evidence receipts.
 */
function extractWilsySourceDate(row = {}, domain = 'meetings') {
  const registry = getWilsyCrmToolRegistry();
  const config = registry[domain] || registry.meetings;

  for (const field of config.dateFields || []) {
    if (row[field]) {
      return row[field];
    }
  }

  return null;
}

/**
 * @function extractWilsySourceValue
 * @description Extracts a numeric source value from deal/pipeline records.
 * @param {Object} row - Source row.
 * @param {string} domain - Tool domain.
 * @returns {number} Numeric value.
 * @collaboration Deals, Pipeline, revenue posture, and CRM Operator Kernel answers.
 */
function extractWilsySourceValue(row = {}, domain = 'deals') {
  const registry = getWilsyCrmToolRegistry();
  const config = registry[domain] || registry.deals;

  for (const field of config.valueFields || []) {
    const value = Number(row[field]);

    if (Number.isFinite(value)) {
      return value;
    }
  }

  return 0;
}

/**
 * @function runWilsyCrmReadTool
 * @description Executes a read-only CRM source tool.
 * @param {Object} params - Tool params.
 * @param {string} params.domain - Tool domain.
 * @param {string} params.tenantId - Tenant id.
 * @param {string} params.question - Operator question.
 * @returns {Promise<Object>} Tool result.
 * @collaboration CRM Operator Kernel, MongoDB source tools, tenant-safe reads, and evidence traces.
 */
async function runWilsyCrmReadTool({
  domain = 'meetings',
  tenantId = 'MASTER',
  question = '',
} = {}) {
  const registry = getWilsyCrmToolRegistry();
  const config = registry[domain];
  const db = mongoose.connection?.db;
  const window = buildWilsyDateWindow(question);
  const applyDateWindow = shouldApplyWilsyDateWindow(domain, question);

  if (!config) {
    return {
      tool: 'registered_business_tool',
      label: 'Registered business tool',
      status: 'TOOL_MISSING',
      statusLabel: 'Tool missing',
      domain,
      count: null,
      collectionsChecked: [],
      sample: [],
      message: `I cannot answer that yet because the ${formatWilsyBusinessLabel(domain)} tool is not registered.`,
    };
  }

  if (!db) {
    return {
      tool: 'crm_source_reader',
      label: `${formatWilsyBusinessLabel(config.label)} source`,
      status: 'SOURCE_UNAVAILABLE',
      statusLabel: 'Source unavailable',
      domain,
      count: null,
      collectionsChecked: [],
      sample: [],
      message: `The ${config.label} source cannot be checked because the database is not connected.`,
    };
  }

  const collections = await listWilsyDomainCollections(domain);
  const tenantFilters = buildTenantFilterCandidates(tenantId);
  const dateFilters = buildWilsyDateFilters(domain, window);
  const collectionsChecked = [];
  const sample = [];
  let total = 0;
  let totalValue = 0;

  for (const collectionName of collections) {
    const collection = db.collection(collectionName);
    collectionsChecked.push(collectionName);

    for (const tenantFilter of tenantFilters) {
      const query = { ...tenantFilter };

      if (applyDateWindow) {
        query.$or = dateFilters;
      }

      const count = await collection.countDocuments(query).catch(() => 0);

      if (count > 0 || Object.keys(tenantFilter).length === 0) {
        const rows = await collection
          .find(query)
          .project(buildWilsyProjection(domain))
          .limit(8)
          .toArray()
          .catch(() => []);

        total += count;
        totalValue += rows.reduce((sum, row) => sum + extractWilsySourceValue(row, domain), 0);
        sample.push(
          ...rows.map((row) => ({
            collection: collectionName,
            title: extractWilsySourceTitle(row, domain),
            status: row.status || row.stage || 'recorded',
            dueAt: extractWilsySourceDate(row, domain),
            value: extractWilsySourceValue(row, domain),
          }))
        );

        break;
      }
    }
  }

  return {
    tool: 'crm_source_reader',
    label: `${formatWilsyBusinessLabel(config.label)} source`,
    status: collections.length > 0 ? 'SOURCE_CHECKED' : 'NO_SOURCE_FOUND',
    statusLabel: collections.length > 0 ? 'Source checked' : 'Source not connected',
    domain,
    count: total,
    totalValue,
    window,
    dateWindowApplied: applyDateWindow,
    collectionsChecked,
    sample: sample.slice(0, 8),
    message:
      collections.length > 0
        ? `Checked ${collections.length} connected ${config.label} source${collections.length === 1 ? '' : 's'}.`
        : `No connected ${config.label} source was found.`,
  };
}

/**
 * @function runWilsyDraftTool
 * @description Executes no-mutation draft tools for reminders, tasks, and memos with detail-rich task/reminder bridge output.
 * @param {Object} params - Tool params.
 * @param {Object} params.intent - Intent.
 * @param {string} params.question - Operator question.
 * @param {Object} params.req - Request object.
 * @param {string} params.tenantId - Tenant id.
 * @param {string} params.operatorId - Operator id.
 * @returns {Promise<Object>} Draft tool result.
 * @collaboration Reminder drafts, task drafts, memo drafts, Task Reminder Execution Bridge, and governed command preparation.
 */
async function runWilsyDraftTool({
  intent = {},
  question = '',
  req = {},
  tenantId = 'MASTER',
  operatorId = 'WILSY_OPERATOR',
} = {}) {
  if (intent.action === 'draft_reminder') {
    return executeWilsyTaskReminderBridge({
      req,
      question,
      tenantId,
      operatorId,
      kind: 'reminder',
    });
  }

  if (intent.action === 'draft_task') {
    return executeWilsyTaskReminderBridge({
      req,
      question,
      tenantId,
      operatorId,
      kind: 'task',
    });
  }

  if (intent.action === 'business_document_draft') {
    return executeWilsyBusinessDocumentDraftBridge({
      req,
      question,
      tenantId,
      operatorId,
    });
  }

  if (intent.action === 'draft_memo') {
    return {
      tool: 'business_memo_draft',
      label: 'Business memo draft',
      status: 'DRAFT_PREPARED',
      statusLabel: 'Draft prepared',
      domain: 'evidence',
      count: null,
      collectionsChecked: ['Memo generator readiness'],
      sample: [],
      draft: {
        title: 'Business Meeting Memo',
        purpose: coerceWilsyOperatorText(question, 260),
        sections: [
          'Purpose',
          'Discussion points',
          'Decisions required',
          'Risks and evidence gaps',
          'Next actions',
        ],
      },
      message: 'Business memo structure prepared for operator review.',
    };
  }

  return {
    tool: 'registered_business_tool',
    label: 'Registered business tool',
    status: 'TOOL_MISSING',
    statusLabel: 'Tool missing',
    domain: intent.domain,
    count: null,
    collectionsChecked: [],
    sample: [],
    message: `I cannot complete this request because ${formatWilsyBusinessLabel(intent.action)} is not registered.`,
  };
}

/**
 * @function buildUnsupportedWilsyResponse
 * @description Builds an honest unsupported response without fake guidance.
 * @param {Object} params - Response params.
 * @param {string} params.question - Question.
 * @param {string} params.missingTool - Missing tool.
 * @returns {Object} Answer.
 * @collaboration Unsupported tool policy, production honesty, and tenant trust.
 */
function buildUnsupportedWilsyResponse({
  question = '',
  missingTool = 'registered business tool',
} = {}) {
  return {
    title: 'I cannot complete that yet',
    answer: `I cannot complete that yet because Wilsy does not have this production tool registered: ${formatWilsyBusinessLabel(missingTool)}.`,
    outcome: 'No fake answer was generated. Register the tool, bind the source, and ask again.',
    commandPlan: [
      `Question: ${question || 'Unsupported question'}`,
      `Missing tool: ${missingTool}`,
      'Outcome: Tool registration required before answering.',
      'Mutation: none.',
    ],
  };
}

/**
 * @function buildWilsyAnswerFromTool
 * @description Builds a business-English answer from a tool result.
 * @param {Object} params - Answer params.
 * @param {string} params.question - Question.
 * @param {Object} params.intent - Intent.
 * @param {Object} params.tool - Tool result.
 * @returns {Object} Answer.
 * @collaboration Calendar bridge, CRM source tools, business-English responses, and no-fake policy.
 */
function buildWilsyAnswerFromTool({ question = '', intent = {}, tool = {} } = {}) {
  if (tool.tool === 'business_document_draft_bridge') {
    const draft = tool.draft || {};
    const documentType = draft.documentType || 'Business document';
    const source = tool.documentSource || draft.documentSource || {};
    const sourceFound = Boolean(source.sourceFound && source.approved);
    const sourceName = source.sourceName || source.sourceReference || `${documentType} source`;
    const tenantBrand =
      source.tenantBrand?.name || draft.tenantBrand?.name || draft.tenantId || 'tenant brand';

    if (!sourceFound) {
      return {
        title: `${documentType} source not connected`,
        answer: `I checked the tenant document library and could not find an approved ${documentType} source. I did not generate an unbranded, unapproved, or fake document.`,
        outcome:
          'Connect or approve the tenant document template, then ask Wilsy to generate the document again.',
        commandPlan: [
          `Tool checked: ${source.toolChecked || 'Tenant Document Library'}`,
          `Document type: ${documentType}`,
          `Source status: ${source.status || 'SOURCE_MISSING'}`,
          `Approved source: ${source.approved ? 'Yes' : 'No'}`,
          `Approved source: ${source.approved ? 'Yes' : 'No'}`,
          `Tenant brand: ${tenantBrand}`,
          'Completion blocked: approved document source is required.',
          'Mutation: none. No document was sent.',
        ],
      };
    }

    return {
      title: `${documentType} draft ready for review`,
      answer: `I checked the tenant document library and found ${sourceName}. I prepared a ${tenantBrand} branded ${documentType} draft for review. Use Review Draft above to inspect it. No sending action has been taken.`,
      outcome: draft.deliveryRequested
        ? 'Review the draft, confirm the recipient and delivery connector, then approve the governed send command.'
        : 'Review the draft, confirm the content, then approve the governed next step.',
      commandPlan: [
        `Tool checked: ${source.toolChecked || 'Tenant Document Library'}`,
        `Source system: ${source.sourceSystem || 'TENANT_DOCUMENT_LIBRARY'}`,
        `Source reference: ${source.sourceReference || source.sourcePath || 'TENANT_DOCUMENT_SOURCE'}`,
        `Tenant brand: ${tenantBrand}`,
        `Document type: ${draft.documentType || 'Business Document'}`,
        `Title: ${draft.title || draft.documentType || 'Business Document'}`,
        `Purpose: ${draft.purpose || 'Review required'}`,
        `Sections: ${(draft.sections || []).join(', ')}`,
        `Delivery requested: ${draft.deliveryRequested ? 'Yes' : 'No'}`,
        `Missing delivery details: ${(draft.missingFields || []).join(', ') || 'none'}`,
        `Review link: ${tool.crmDocumentLink || draft.crmDocumentDraftLink}`,
        'Review mode: tenant-branded in-dock document preview.',
        'Mutation: none. No document was sent.',
      ],
    };
  }

  if (tool.tool === 'task_reminder_execution_bridge') {
    const draft = tool.draft || {};
    const itemLabel = draft.kind === 'reminder' ? 'reminder' : 'task';

    if (tool.status === 'DRAFT_INCOMPLETE') {
      return {
        title: `${itemLabel.charAt(0).toUpperCase()}${itemLabel.slice(1)} details needed`,
        answer: `I can prepare this ${itemLabel}, but I need the following details first: ${tool.missingFields.join(', ')}.`,
        outcome: 'Provide the missing details and I will prepare it for approval.',
        commandPlan: [
          `Question: ${question}`,
          `Missing details: ${tool.missingFields.join(', ')}`,
          `Draft link: ${tool.crmTaskLink}`,
          'Mutation: none.',
        ],
      };
    }

    if (tool.status === 'APPROVAL_REQUIRED') {
      return {
        title: `${itemLabel.charAt(0).toUpperCase()}${itemLabel.slice(1)} ready for approval`,
        answer: `I prepared the ${itemLabel} draft. Title: ${draft.title}. Due date: ${draft.dueDateLabel}. Time: ${draft.timeLabel}. Priority: ${draft.priority}. Use Open Review in Prepared Work to inspect it.`,
        outcome: 'Approval is required before Wilsy creates the task or reminder.',
        commandPlan: [
          `Title: ${draft.title}`,
          `Due date: ${draft.dueDateLabel}`,
          `Time: ${draft.timeLabel}`,
          `Priority: ${draft.priority}`,
          `Review link: ${tool.crmTaskLink}`,
          'Mutation: none until approved.',
        ],
      };
    }

    if (tool.status === 'TASK_CREATED' || tool.status === 'REMINDER_CREATED') {
      return {
        title: tool.status === 'REMINDER_CREATED' ? 'Reminder created' : 'Task created',
        answer: `The ${itemLabel} has been created. Title: ${draft.title}. Link: ${tool.taskLink || tool.crmTaskLink}.`,
        outcome: 'Task/reminder created and evidence receipt prepared.',
        commandPlan: [
          `Title: ${draft.title}`,
          `Due date: ${draft.dueDateLabel}`,
          `Link: ${tool.taskLink || tool.crmTaskLink}`,
          `Connector: ${tool.connector}`,
          'Mutation: task/reminder created with approval.',
        ],
      };
    }

    return {
      title: 'Task connector unavailable',
      answer: tool.message,
      outcome: 'Connect CRM Tasks before executing this item.',
      commandPlan: [`Question: ${question}`, `Status: ${tool.status}`, 'Mutation: none.'],
    };
  }

  if (tool.tool === 'calendar_execution_bridge') {
    if (tool.status === 'DRAFT_INCOMPLETE') {
      return {
        title: 'Meeting details needed',
        answer: `I can prepare this meeting, but I need the following details first: ${tool.missingFields.join(', ')}.`,
        outcome: 'Provide the missing details and I will prepare the meeting for approval.',
        commandPlan: [
          `Question: ${question}`,
          `Missing details: ${tool.missingFields.join(', ')}`,
          `Draft link: ${tool.crmCalendarLink}`,
          'Mutation: none.',
        ],
      };
    }

    if (tool.status === 'APPROVAL_REQUIRED') {
      return {
        title: 'Meeting ready for approval',
        answer: `I prepared the meeting draft. Subject: ${tool.draft.subject}. Date: ${tool.draft.dateLabel}. Time: ${tool.draft.timeLabel}. Duration: ${tool.draft.durationLabel}. Participants: ${tool.draft.participants.join(', ')}. Agenda: ${tool.draft.agenda}. Review link: ${tool.crmCalendarLink}.`,
        outcome: 'Approval is required before Wilsy creates the calendar event.',
        commandPlan: [
          `Subject: ${tool.draft.subject}`,
          `Date: ${tool.draft.dateLabel}`,
          `Time: ${tool.draft.timeLabel}`,
          `Duration: ${tool.draft.durationLabel}`,
          `Participants: ${tool.draft.participants.join(', ')}`,
          `Agenda: ${tool.draft.agenda}`,
          `Review link: ${tool.crmCalendarLink}`,
          'Mutation: none until approved.',
        ],
      };
    }

    if (tool.status === 'EVENT_CREATED') {
      return {
        title: 'Meeting scheduled',
        answer: `The meeting has been scheduled. Subject: ${tool.draft.subject}. Calendar link: ${tool.eventLink || tool.crmCalendarLink}.`,
        outcome: 'Calendar event created and evidence receipt prepared.',
        commandPlan: [
          `Subject: ${tool.draft.subject}`,
          `Calendar link: ${tool.eventLink || tool.crmCalendarLink}`,
          `Connector: ${tool.connector}`,
          'Mutation: calendar event created with approval.',
        ],
      };
    }

    return {
      title: 'Calendar connector unavailable',
      answer: tool.message,
      outcome:
        'Connect CRM Calendar, Google Calendar, or Microsoft Graph Calendar before executing this event.',
      commandPlan: [`Question: ${question}`, `Status: ${tool.status}`, 'Mutation: none.'],
    };
  }

  if (tool.status === 'DRAFT_PREPARED') {
    return {
      title: `${tool.label} prepared`,
      answer: tool.message,
      outcome:
        'Ready for operator review. Execution requires approval through a governed Wilsy command.',
      commandPlan: [
        `Question: ${question}`,
        `Tool: ${tool.label}`,
        `Draft: ${JSON.stringify(tool.draft || {})}`,
        'Mutation: none.',
      ],
    };
  }

  const registry = getWilsyCrmToolRegistry();
  const config = registry[intent.domain] || { label: intent.domain || 'records' };
  const datePhrase = tool.dateWindowApplied
    ? ` for ${tool.window?.scope} (${tool.window?.label})`
    : '';

  if (tool.status === 'SOURCE_CHECKED') {
    return {
      title: `${formatWilsyBusinessLabel(config.label)} answer`,
      answer: `I checked ${tool.collectionsChecked.length} connected ${config.label} source${tool.collectionsChecked.length === 1 ? '' : 's'}. There ${tool.count === 1 ? 'is' : 'are'} ${tool.count} ${config.label}${datePhrase}.`,
      outcome:
        tool.count > 0
          ? `Review the ${config.label} source result, confirm ownership, and prepare the next governed follow-up.`
          : `No ${config.label} matched this question in connected sources.`,
      commandPlan: [
        `Question: ${question}`,
        `Tool: ${tool.label}`,
        `Sources checked: ${tool.collectionsChecked.join(', ') || 'none'}`,
        `Count: ${tool.count}`,
        'Mutation: none.',
      ],
    };
  }

  if (tool.status === 'NO_SOURCE_FOUND' || tool.status === 'SOURCE_UNAVAILABLE') {
    return {
      title: `${formatWilsyBusinessLabel(config.label)} source unavailable`,
      answer: `I cannot answer from production data yet because no connected ${config.label} source was available.`,
      outcome: `Bind the ${config.label} source to Wilsy AI before tenant users rely on this answer.`,
      commandPlan: [
        `Question: ${question}`,
        `Tool: ${tool.label}`,
        `Status: ${tool.status}`,
        'Mutation: none.',
      ],
    };
  }

  return buildUnsupportedWilsyResponse({
    question,
    missingTool: tool.tool || `${intent.domain}_tool`,
  });
}

/**
 * @function buildWilsyQuickPrompts
 * @description Builds production quick prompts from registered tools.
 * @returns {Array<Object>} Quick prompts.
 * @collaboration Operator Model UI, CRM tool registry, and tenant workflow discovery.
 */
function buildWilsyQuickPrompts() {
  return [
    { id: 'schedule_meeting', label: 'Schedule meeting' },
    { id: 'meetings_this_week', label: 'Meetings this week' },
    { id: 'tasks_this_week', label: 'Tasks this week' },
    { id: 'lead_count', label: 'Lead count' },
    { id: 'contact_count', label: 'Contact count' },
    { id: 'account_count', label: 'Account count' },
    { id: 'deal_summary', label: 'Deal summary' },
    { id: 'pipeline_summary', label: 'Pipeline summary' },
    { id: 'setup_status', label: 'Setup status' },
    { id: 'evidence_status', label: 'Evidence status' },
    { id: 'source_status', label: 'Source status' },
    { id: 'contract_form', label: 'Draft contract form' },
    { id: 'draft_memo', label: 'Draft business memo' },
  ];
}

/**
 * @function buildWilsyActions
 * @description Builds no-mutation operator action suggestions.
 * @param {Object} params - Action params.
 * @param {Object} params.intent - Intent.
 * @param {Object} params.tool - Tool result.
 * @param {Object} params.answer - Answer.
 * @returns {Array<Object>} Actions.
 * @collaboration Governed command preparation, source results, and approval workflow.
 */
function buildWilsyActions({ intent = {}, tool = {}, answer = {} } = {}) {
  return [
    {
      rank: 1,
      title: tool.status === 'APPROVAL_REQUIRED' ? 'Review meeting draft' : 'Review result',
      description: answer.outcome || 'Review the result before taking action.',
      mode: 'read_only',
      mutation: false,
    },
    {
      rank: 2,
      title:
        tool.status === 'APPROVAL_REQUIRED'
          ? 'Approve calendar execution'
          : 'Prepare governed follow-up',
      description: 'Execution requires a governed Wilsy command and operator approval.',
      mode: 'approval_required',
      mutation: false,
    },
    {
      rank: 3,
      title: 'Inspect evidence gaps',
      description: `Confirm source and evidence coverage for ${formatWilsyBusinessLabel(intent.domain || tool.domain || 'this request')}.`,
      mode: 'read_only',
      mutation: false,
    },
  ];
}

/**
 * @function buildWilsySourceTrace
 * @description Builds business-English source trace objects.
 * @param {Array<Object>} toolRuns - Tool results.
 * @returns {Array<Object>} Source trace objects.
 * @collaboration Tool transparency, tenant trust, and source checked UI.
 */
function buildWilsySourceTrace(toolRuns = []) {
  return toolRuns.map((tool) => ({
    tool: tool.tool,
    label: tool.label || formatWilsyBusinessLabel(tool.tool || 'source'),
    domain: tool.domain,
    status: tool.status,
    statusLabel: tool.statusLabel || formatWilsyBusinessLabel(tool.status || 'completed'),
    count: tool.count,
    collectionsChecked: tool.collectionsChecked || [],
    message: tool.message,
  }));
}

/**
 * @function extractWilsyFG81LeadCreateValue
 * @description Extracts a bounded Lead field value from an operator question using conservative patterns.
 * @param {string} text - Operator question text.
 * @param {RegExp[]} patterns - Candidate extraction patterns.
 * @returns {string} Extracted value.
 * @collaboration Wilsy AI Create Lead draft preparation, no-mutation safeguards, and operator review.
 */
function extractWilsyFG81LeadCreateValue(text = '', patterns = []) {
  for (const pattern of patterns) {
    const match = text.match(pattern);
    if (match?.[1]) {
      return coerceWilsyOperatorText(match[1])
        .replace(/[.,;]+$/g, '')
        .trim();
    }
  }

  return '';
}

/**
 * @function buildWilsyFG81LeadCreateDraftFromQuestion
 * @description Builds a governed CRM Lead create draft from chat text without mutating the backend.
 * @param {string} operatorQuestion - Operator question.
 * @returns {Object|null} Draft packet or null when the question is not a Create Lead request.
 * @collaboration Wilsy AI Operator Kernel, CRM Create Lead, Edit Lead parity fields, and governed approval.
 */
function buildWilsyFG81LeadCreateDraftFromQuestion(operatorQuestion = '') {
  /* P60K5Q10FG81_GOVERNED_CREATE_LEAD_DRAFT */
  const text = coerceWilsyOperatorText(operatorQuestion);
  const lower = text.toLowerCase();

  if (
    !(
      /\b(create|add|capture|prepare|draft|register)\b/.test(lower) &&
      /\b(lead|prospect)\b/.test(lower)
    )
  ) {
    return null;
  }

  const email = extractWilsyFG81LeadCreateValue(text, [
    /\bemail(?:\s+address)?\s*(?:is|=|:)?\s*([A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,})/i,
    /\b([A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,})\b/i,
  ]);

  const phone = extractWilsyFG81LeadCreateValue(text, [
    /\b(?:phone|mobile|cell)\s*(?:number)?\s*(?:is|=|:)?\s*(\+?[0-9][0-9\s().-]{6,})/i,
    /\b(\+?[0-9][0-9\s().-]{8,})\b/i,
  ]);

  const company = extractWilsyFG81LeadCreateValue(text, [
    /\bcompany\s*(?:is|=|:)?\s*([^.,;]+?)(?:\s+with\s+email|\s+email|\s+phone|\s+mobile|\s+stage|\s+status|\s+priority|\s+value|\s+score|\s+industry|\s+due|\s+source|$)/i,
    /\b(?:at|for)\s+([^.,;]+?)(?:\s+with\s+email|\s+email|\s+phone|\s+mobile|\s+stage|\s+status|\s+priority|\s+value|\s+score|\s+industry|\s+due|\s+source|$)/i,
  ]);

  const name = extractWilsyFG81LeadCreateValue(text, [
    /\blead\s+(?:named|called)\s+([^.,;]+?)(?:\s+at\s+|\s+for\s+|\s+company|\s+email|\s+phone|\s+mobile|\s+stage|\s+status|\s+priority|\s+value|\s+score|\s+industry|\s+due|\s+source|$)/i,
    /\b(?:create|add|capture|prepare|draft|register)\s+(?:a\s+)?(?:new\s+)?(?:lead|prospect)\s+(?:for|named|called)?\s*([^.,;]+?)(?:\s+at\s+|\s+company|\s+email|\s+phone|\s+mobile|\s+stage|\s+status|\s+priority|\s+value|\s+score|\s+industry|\s+due|\s+source|$)/i,
  ]);

  const estimatedDealValue = extractWilsyFG81LeadCreateValue(text, [
    /\b(?:estimated\s+deal\s+value|deal\s+value|value|pipeline\s+value)\s*(?:is|=|:)?\s*(?:R|ZAR)?\s*([0-9][0-9\s,._]*)/i,
  ]).replace(/[^0-9.]/g, '');

  const priority = extractWilsyFG81LeadCreateValue(text, [
    /\bpriority\s*(?:is|=|:)?\s*(urgent|high|medium|low)\b/i,
  ]);
  const stage = extractWilsyFG81LeadCreateValue(text, [
    /\bstage\s*(?:is|=|:)?\s*([^.,;]+?)(?:\s+status|\s+priority|\s+value|\s+score|\s+industry|\s+due|$)/i,
  ]);
  const status = extractWilsyFG81LeadCreateValue(text, [
    /\bstatus\s*(?:is|=|:)?\s*([^.,;]+?)(?:\s+stage|\s+priority|\s+value|\s+score|\s+industry|\s+due|$)/i,
  ]);
  const industry = extractWilsyFG81LeadCreateValue(text, [
    /\bindustry\s*(?:is|=|:)?\s*([^.,;]+?)(?:\s+with\s+|\s+email|\s+phone|\s+priority|\s+value|\s+score|\s+due|$)/i,
  ]);
  const score = extractWilsyFG81LeadCreateValue(text, [/\bscore\s*(?:is|=|:)?\s*([0-9]{1,3})\b/i]);
  const dueDate = extractWilsyFG81LeadCreateValue(text, [
    /\b(?:due|follow\s*up|follow-up)\s*(?:date)?\s*(?:is|=|:)?\s*([0-9]{4}[-/][0-9]{2}[-/][0-9]{2})/i,
  ]).replace(/\//g, '-');
  const website = extractWilsyFG81LeadCreateValue(text, [
    /\b(?:website|site)\s*(?:is|=|:)?\s*(https?:\/\/[^\s,;]+|[A-Z0-9.-]+\.[A-Z]{2,})/i,
  ]);

  const source = lower.includes('referral')
    ? 'Referral'
    : lower.includes('partner')
      ? 'Partner'
      : lower.includes('outbound')
        ? 'Outbound'
        : lower.includes('event')
          ? 'Event'
          : 'Wilsy AI';

  const draft = {
    module: 'Lead',
    name,
    company,
    email,
    phone,
    mobile: phone,
    countryCode: 'ZA',
    mobileCountryCode: 'ZA',
    source,
    status: status || 'NEW',
    stage: stage || 'NURTURE',
    priority: priority ? priority[0].toUpperCase() + priority.slice(1).toLowerCase() : 'Medium',
    estimatedDealValue,
    dealValue: estimatedDealValue,
    industry,
    score,
    dueDate,
    website,
    notes: text,
    description: text,
  };

  Object.keys(draft).forEach((key) => {
    if (draft[key] === '') delete draft[key];
  });

  const missingFields = [];
  if (!draft.name) missingFields.push('lead name');
  if (!draft.company) missingFields.push('company');
  if (!draft.email) missingFields.push('email');

  return {
    status: missingFields.length ? 'DRAFT_INCOMPLETE' : 'APPROVAL_REQUIRED',
    tool: 'crm_lead_create_draft',
    label: 'Create Lead draft',
    mutation: 'NO_BACKEND_MUTATION_REQUIRES_OPERATOR_SAVE',
    missingFields,
    leadCreateDraft: draft,
    createLeadDraft: draft,
    message: missingFields.length
      ? `I can prepare the Lead, but I need: ${missingFields.join(', ')}.`
      : `I prepared a governed Create Lead draft for ${draft.name} at ${draft.company}. Review the Create Lead surface and press Save.`,
  };
}

/**
 * @function buildWilsyFG81LeadCreateOperatorResponse
 * @description Builds the Operator Kernel response for governed Create Lead draft requests.
 * @param {Object} params - Response construction parameters.
 * @returns {Object|null} Operator response or null.
 * @collaboration Wilsy AI chat-to-Create Lead, no-blind-write posture, and frontend draft hydration.
 */
function buildWilsyFG81LeadCreateOperatorResponse({
  operatorQuestion = '',
  tenantId = 'MASTER',
  operatorId = 'WILSY_OPERATOR',
  workspaceRoute = '/crm/leads',
  context = {},
} = {}) {
  const tool = buildWilsyFG81LeadCreateDraftFromQuestion(operatorQuestion);
  if (!tool) return null;

  const draft = tool.leadCreateDraft || {};
  const ready = tool.status === 'APPROVAL_REQUIRED';

  const operatorModel = {
    intent: 'create_lead',
    action: 'prepare_create_lead_draft',
    domain: 'leads',
    supported: true,
    title: ready ? 'Create Lead draft ready' : 'Create Lead draft needs fields',
    answer: tool.message,
    outcome: ready
      ? 'Draft hydrated into the Create Lead workflow for operator review.'
      : 'Provide the missing fields and Wilsy AI will complete the governed draft.',
    responseSurface: 'continuous_typographic',
    leadCreateDraft: draft,
    createLeadDraft: draft,
    inlineCommandLinks: [
      {
        id: 'open_create_lead_draft',
        label: ready ? 'Open Create Lead draft' : 'Complete Lead draft',
        command: 'open_create_lead_draft',
        action: 'prepare_create_lead_draft',
        payload: {
          module: 'Lead',
          draft,
          missingFields: tool.missingFields,
          requiresOperatorApproval: true,
        },
      },
    ],
    sourceTrace: [
      'Wilsy AI prepared a Create Lead draft from chat text.',
      'No backend mutation was executed.',
      'Operator must review fields and press Save.',
    ],
  };

  return {
    result: 'WILSY_AI_OPERATOR_MODEL_RESOLVED',
    mutation: 'NO_BACKEND_MUTATION_REQUIRES_OPERATOR_SAVE',
    tenant: { tenantId, operatorId },
    workspace: context.workspace || { route: workspaceRoute },
    evidencePosture: context.evidencePosture || null,
    operatorModel,
    toolRuns: [tool],
    inlineCommandLinks: operatorModel.inlineCommandLinks,
    actionSuggestions: [
      {
        id: 'review_create_lead_draft',
        title: 'Review Create Lead draft',
        description: 'Open the Create Lead surface, verify every field, then Save.',
        command: 'open_create_lead_draft',
      },
    ],
  };
}

/**
 * @function coerceWilsyFG83BText
 * @description Coerces values for the global Create Lead intent resolver.
 * @param {*} value - Any input value.
 * @returns {string} Trimmed text.
 * @collaboration Wilsy AI global dock, CRM Setup copilot, Leads Create surface, and governed draft creation.
 */
function coerceWilsyFG83BText(value = '') {
  return String(value || '').trim();
}

/**
 * @function extractWilsyFG83BLeadValue
 * @description Extracts bounded Lead field values from natural language create-lead prompts.
 * @param {string} text - Operator prompt.
 * @param {RegExp[]} patterns - Extraction patterns.
 * @returns {string} Extracted field value.
 * @collaboration Wilsy AI lead-create prompt parser, Create Lead parity fields, and operator-reviewed save flow.
 */
function extractWilsyFG83BLeadValue(text = '', patterns = []) {
  for (const pattern of patterns) {
    const match = text.match(pattern);
    if (match?.[1]) {
      return coerceWilsyFG83BText(match[1])
        .replace(/[.;]+$/g, '')
        .trim();
    }
  }

  return '';
}

/**
 * @function resolveWilsyFG83BOperatorQuestion
 * @description Finds the operator question across route, body, strike payload, and direct model request shapes.
 * @param {Object} req - Operator model request.
 * @returns {string} Operator question.
 * @collaboration Global Wilsy AI, CRM Setup copilot, Leads local AI, and backend Operator Kernel.
 */
function resolveWilsyFG83BOperatorQuestion(req = {}) {
  return coerceWilsyFG83BText(
    req?.query?.operatorQuestion ||
      req?.query?.question ||
      req?.query?.prompt ||
      req?.body?.operatorQuestion ||
      req?.body?.question ||
      req?.body?.prompt ||
      req?.body?.strikePayload?.operatorQuestion ||
      req?.body?.strikePayload?.question ||
      req?.operatorQuestion ||
      req?.question ||
      req?.prompt ||
      ''
  );
}

/**
 * @function buildWilsyFG83BCreateLeadDraft
 * @description Builds a governed Lead create draft from a create-lead prompt without mutating the backend.
 * @param {string} operatorQuestion - Operator question.
 * @returns {Object|null} Draft packet or null.
 * @collaboration Wilsy AI chat-to-Lead, Create Lead field parity, no-blind-write policy, and operator approval.
 */
function buildWilsyFG83BCreateLeadDraft(operatorQuestion = '') {
  /* P60K5Q10FG83B_CREATE_LEAD_PRIORITY_DRAFT */
  const text = coerceWilsyFG83BText(operatorQuestion);
  const lower = text.toLowerCase();

  if (
    !/\b(create|add|capture|prepare|draft|register)\b/.test(lower) ||
    !/\b(lead|prospect)\b/.test(lower)
  ) {
    return null;
  }

  const name = extractWilsyFG83BLeadValue(text, [
    /\blead\s+(?:named|called)\s+([^.;]+?)(?:\s+at\s+|\s+company|\s+email|\s+phone|\s+mobile|\s+title|\s+priority|\s+value|\s+industry|\s+stage|\s+status|\s+owner|\s+source|\s+website|\s+employees|\s+due|\s+notes|$)/i,
    /\b(?:create|add|capture|prepare|draft|register)\s+(?:a\s+)?(?:new\s+)?(?:lead|prospect)\s+(?:named|called|for)?\s*([^.;]+?)(?:\s+at\s+|\s+company|\s+email|\s+phone|\s+mobile|\s+title|\s+priority|\s+value|\s+industry|\s+stage|\s+status|\s+owner|\s+source|\s+website|\s+employees|\s+due|\s+notes|$)/i,
  ]);

  const company = extractWilsyFG83BLeadValue(text, [
    /\bcompany\s*(?:is|=|:)?\s*([^.;]+?)(?:\s+with\s+email|\s+email|\s+phone|\s+mobile|\s+title|\s+priority|\s+value|\s+industry|\s+stage|\s+status|\s+owner|\s+source|\s+website|\s+employees|\s+due|\s+notes|$)/i,
    /\bat\s+([^.;]+?)(?:\s+with\s+email|\s+email|\s+phone|\s+mobile|\s+title|\s+priority|\s+value|\s+industry|\s+stage|\s+status|\s+owner|\s+source|\s+website|\s+employees|\s+due|\s+notes|$)/i,
  ]);

  const email = extractWilsyFG83BLeadValue(text, [
    /\bemail(?:\s+address)?\s*(?:is|=|:)?\s*([A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,})/i,
    /\b([A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,})\b/i,
  ]);

  const phone = extractWilsyFG83BLeadValue(text, [
    /\bphone\s*(?:number)?\s*(?:is|=|:)?\s*(\+?[0-9][0-9\s().-]{6,})/i,
  ]);

  const mobile = extractWilsyFG83BLeadValue(text, [
    /\bmobile\s*(?:number)?\s*(?:is|=|:)?\s*(\+?[0-9][0-9\s().-]{6,})/i,
  ]);

  const estimatedDealValue = extractWilsyFG83BLeadValue(text, [
    /\b(?:estimated\s+deal\s+value|deal\s+value|pipeline\s+value|value)\s*(?:is|=|:)?\s*(?:R|ZAR)?\s*([0-9][0-9\s,._]*)/i,
  ]).replace(/[^0-9.]/g, '');

  const priority = extractWilsyFG83BLeadValue(text, [
    /\bpriority\s*(?:is|=|:)?\s*(urgent|high|medium|low)\b/i,
  ]);

  const source =
    extractWilsyFG83BLeadValue(text, [
      /\bsource\s*(?:is|=|:)?\s*([^.;]+?)(?:\s+website|\s+employees|\s+due|\s+notes|$)/i,
    ]) ||
    (lower.includes('referral')
      ? 'Referral'
      : lower.includes('partner')
        ? 'Partner'
        : lower.includes('outbound')
          ? 'Outbound'
          : 'Wilsy AI');

  const draft = {
    module: 'Lead',
    name,
    company,
    email,
    phone,
    mobile: mobile || phone,
    countryCode: 'ZA',
    mobileCountryCode: 'ZA',
    title: extractWilsyFG83BLeadValue(text, [
      /\btitle\s*(?:is|=|:)?\s*([^.;]+?)(?:\s+priority|\s+value|\s+industry|\s+stage|\s+status|\s+owner|\s+source|\s+website|\s+employees|\s+due|\s+notes|$)/i,
    ]),
    priority: priority ? priority[0].toUpperCase() + priority.slice(1).toLowerCase() : 'Medium',
    estimatedDealValue,
    dealValue: estimatedDealValue,
    industry: extractWilsyFG83BLeadValue(text, [
      /\bindustry\s*(?:is|=|:)?\s*([^.;]+?)(?:\s+stage|\s+status|\s+owner|\s+source|\s+website|\s+employees|\s+due|\s+notes|$)/i,
    ]),
    stage:
      extractWilsyFG83BLeadValue(text, [
        /\bstage\s*(?:is|=|:)?\s*([^.;]+?)(?:\s+status|\s+owner|\s+source|\s+website|\s+employees|\s+due|\s+notes|$)/i,
      ]) || 'NURTURE',
    status:
      extractWilsyFG83BLeadValue(text, [
        /\bstatus\s*(?:is|=|:)?\s*([^.;]+?)(?:\s+owner|\s+source|\s+website|\s+employees|\s+due|\s+notes|$)/i,
      ]) || 'NEW',
    owner: extractWilsyFG83BLeadValue(text, [
      /\bowner\s*(?:is|=|:)?\s*([^.;]+?)(?:\s+source|\s+website|\s+employees|\s+due|\s+notes|$)/i,
    ]),
    source,
    website: extractWilsyFG83BLeadValue(text, [
      /\b(?:website|site)\s*(?:is|=|:)?\s*(https?:\/\/[^\s,;]+|[A-Z0-9.-]+\.[A-Z]{2,})/i,
    ]),
    employees: extractWilsyFG83BLeadValue(text, [
      /\bemployees\s*(?:is|=|:)?\s*([0-9][0-9\s,._]*)/i,
    ]).replace(/[^0-9.]/g, ''),
    dueDate: extractWilsyFG83BLeadValue(text, [
      /\b(?:due|follow\s*up|follow-up)\s*(?:date)?\s*(?:is|=|:)?\s*([0-9]{4}[-/][0-9]{2}[-/][0-9]{2})/i,
    ]).replace(/\//g, '-'),
    notes: extractWilsyFG83BLeadValue(text, [/\bnotes\s*(?:are|is|=|:)?\s*(.+)$/i]) || text,
    description: extractWilsyFG83BLeadValue(text, [/\bnotes\s*(?:are|is|=|:)?\s*(.+)$/i]) || text,
  };

  Object.keys(draft).forEach((key) => {
    if (draft[key] === '') delete draft[key];
  });

  const missingFields = [];
  if (!draft.name) missingFields.push('lead name');
  if (!draft.company) missingFields.push('company');
  if (!draft.email) missingFields.push('email');

  return {
    status: missingFields.length ? 'DRAFT_INCOMPLETE' : 'APPROVAL_REQUIRED',
    tool: 'crm_lead_create_draft',
    label: 'Create Lead draft',
    mutation: 'NO_BACKEND_MUTATION_REQUIRES_OPERATOR_SAVE',
    missingFields,
    leadCreateDraft: draft,
    createLeadDraft: draft,
    message: missingFields.length
      ? `I can prepare the Lead, but I need: ${missingFields.join(', ')}.`
      : `I prepared a governed Create Lead draft for ${draft.name} at ${draft.company}. Review the Create Lead surface and press Save.`,
  };
}

/**
 * @function buildWilsyFG83BCreateLeadOperatorResponse
 * @description Builds the high-priority Operator Kernel response for create-lead chat commands.
 * @param {Object} req - Operator model request.
 * @returns {Object|null} Operator response or null.
 * @collaboration Floating Wilsy AI, CRM Setup copilot, Leads Create surface, and governed operator approval.
 */
function buildWilsyFG83BCreateLeadOperatorResponse(req = {}) {
  const operatorQuestion = resolveWilsyFG83BOperatorQuestion(req);
  const tool = buildWilsyFG83BCreateLeadDraft(operatorQuestion);

  if (!tool) return null;

  const tenantId =
    req?.query?.tenantId || req?.body?.tenantId || req?.headers?.['x-tenant-id'] || 'MASTER';
  const operatorId =
    req?.query?.operatorId ||
    req?.body?.operatorId ||
    req?.headers?.['x-operator-id'] ||
    'WILSY_OPERATOR';
  const workspaceRoute = req?.query?.workspaceRoute || req?.body?.workspaceRoute || '/crm/leads';
  const draft = tool.leadCreateDraft || {};
  const ready = tool.status === 'APPROVAL_REQUIRED';

  return {
    result: 'WILSY_AI_OPERATOR_MODEL_RESOLVED',
    mutation: 'NO_BACKEND_MUTATION_REQUIRES_OPERATOR_SAVE',
    tenant: { tenantId, operatorId },
    workspace: { route: workspaceRoute, targetRoute: '/crm/leads', targetMode: 'create' },
    operatorModel: {
      intent: 'create_lead',
      action: 'prepare_create_lead_draft',
      domain: 'leads',
      supported: true,
      title: ready ? 'Create Lead draft ready' : 'Create Lead draft needs fields',
      answer: tool.message,
      outcome: ready
        ? 'Draft is ready for the Create Lead workspace. Review every field and press Save.'
        : 'The draft is incomplete. Provide the missing fields to complete the governed Lead draft.',
      responseSurface: 'continuous_typographic',
      leadCreateDraft: draft,
      createLeadDraft: draft,
      inlineCommandLinks: [
        {
          id: 'open_create_lead_draft',
          label: ready ? 'Open Create Lead draft' : 'Complete Lead draft',
          command: 'open_create_lead_draft',
          action: 'prepare_create_lead_draft',
          payload: {
            module: 'Lead',
            draft,
            missingFields: tool.missingFields,
            requiresOperatorApproval: true,
          },
        },
      ],
      sourceTrace: [
        'Wilsy AI prepared a Create Lead draft from chat text.',
        'No backend create mutation was executed.',
        'Operator must review the Create Lead form and press Save.',
      ],
    },
    toolRuns: [tool],
    inlineCommandLinks: [
      {
        id: 'open_create_lead_draft',
        label: ready ? 'Open Create Lead draft' : 'Complete Lead draft',
        command: 'open_create_lead_draft',
        action: 'prepare_create_lead_draft',
        payload: {
          module: 'Lead',
          draft,
          missingFields: tool.missingFields,
          requiresOperatorApproval: true,
        },
      },
    ],
  };
}

/**
 * @function resolveWilsyAIOperatorModel
 * @description Resolves tenant CRM and business productivity requests through the production Operator Kernel.
 * @param {Object} req - Express request.
 * @returns {Promise<Object>} Operator model response.
 * @collaboration Q10Z source-registry bridge, Calendar Execution Bridge, CRM source tools, and proof harness.
 */
export async function resolveWilsyAIOperatorModel(req = {}) {
  const wilsyFG83BCreateLeadPriorityResponse = buildWilsyFG83BCreateLeadOperatorResponse(req);
  if (wilsyFG83BCreateLeadPriorityResponse) {
    /* P60K5Q10FG83B_CREATE_LEAD_PRIORITY_BEFORE_GENERIC_CONTEXT */
    return wilsyFG83BCreateLeadPriorityResponse;
  }

  const operatorQuestion =
    req?.query?.operatorQuestion ||
    req?.body?.operatorQuestion ||
    req?.body?.question ||
    req?.query?.question ||
    '';

  /* P60K5Q10FG107H_OPERATOR_QUESTION_RESOLVER_RESCUE */

  /* WILSY_P60K5Q10FG43_CRM_LEADS_VIEWPOINT_AI */
  const wilsyFG82CreateLeadPriorityResponse = buildWilsyFG81LeadCreateOperatorResponse({
    operatorQuestion:
      req.query?.operatorQuestion || req.query?.question || req.body?.operatorQuestion || '',
    tenantId: req.query?.tenantId || req.headers?.['x-tenant-id'] || req.body?.tenantId || 'MASTER',
    operatorId:
      req.query?.operatorId ||
      req.headers?.['x-operator-id'] ||
      req.body?.operatorId ||
      'WILSY_OPERATOR',
    workspaceRoute: req.query?.workspaceRoute || req.body?.workspaceRoute || '/crm/leads',
    context: {},
  });

  if (wilsyFG82CreateLeadPriorityResponse) {
    /* P60K5Q10FG82_CREATE_LEAD_PRIORITY_BEFORE_VIEWPOINT */
    return wilsyFG82CreateLeadPriorityResponse;
  }

  const wilsyCRMLeadsViewpointModel = resolveWilsyAICRMLeadsViewpointModel(req);

  if (wilsyCRMLeadsViewpointModel) {
    return wilsyCRMLeadsViewpointModel;
  }

  const generatedAt = new Date().toISOString();
  const tenantId = coerceWilsyOperatorText(
    req.query?.tenantId || req.headers?.['x-tenant-id'] || req.body?.tenantId || 'MASTER',
    120
  );
  const operatorId = coerceWilsyOperatorText(
    req.query?.operatorId ||
      req.headers?.['x-operator-id'] ||
      req.body?.operatorId ||
      'WILSY_OPERATOR',
    160
  );
  const question = coerceWilsyOperatorText(
    req.query?.operatorQuestion || req.query?.question || req.body?.operatorQuestion || '',
    1800
  );
  const workspaceRoute = coerceWilsyOperatorText(
    req.query?.workspaceRoute || req.body?.workspaceRoute || '/crm/setup',
    240
  );
  const workspaceSurface = coerceWilsyOperatorText(
    req.query?.workspaceSurface ||
      req.body?.workspaceSurface ||
      'CRM Meetings Tasks Leads Contacts Accounts Deals Pipeline Setup Evidence Sources Calendar Memo Reminder',
    2600
  );

  const context = await resolveWilsyAISovereignContext({
    ...req,
    headers: {
      ...(req.headers || {}),
      'x-tenant-id': tenantId,
      'x-operator-id': operatorId,
    },
    body: {
      tenantId,
      operatorId,
      workspaceRoute,
      workspaceSurface,
      institutionalHeaders: {
        tenantId,
        operatorId,
        generatedAt,
        route: '/api/source-registry/health',
        commandSurface: 'WILSY_OS_OPERATOR_KERNEL',
        mutation: false,
      },
      strikePayload: {
        institutionalHeaders: {
          tenantId,
          operatorId,
          generatedAt,
          route: '/api/source-registry/health',
          commandSurface: 'WILSY_OS_OPERATOR_KERNEL',
          mutation: false,
        },
        commandType: 'READ_ONLY_OPERATOR_KERNEL_CONTEXT',
        mutation: false,
      },
    },
  });

  const intent = inferWilsyOperatorIntent(question);
  const toolRuns = [];
  let tool;
  let answer;
  let capabilityFoundryCandidate = null;

  if (!intent.supported) {
    answer = buildUnsupportedWilsyResponse({
      question,
      missingTool: intent.missingTool,
    });
    tool = {
      tool: intent.missingTool,
      label: 'Registered business tool',
      domain: null,
      status: 'TOOL_MISSING',
      statusLabel: 'Tool missing',
      count: null,
      collectionsChecked: [],
      sample: [],
      message: answer.answer,
    };
  } else if (intent.action === 'calendar_execution_bridge') {
    tool = await executeWilsyCalendarBridge({
      req,
      question,
      tenantId,
      operatorId,
    });
    answer = buildWilsyAnswerFromTool({
      question,
      intent,
      tool,
    });
  } else if (intent.action === 'read_source') {
    tool = await runWilsyCrmReadTool({
      domain: intent.domain,
      tenantId,
      question,
    });
    answer = buildWilsyAnswerFromTool({
      question,
      intent,
      tool,
    });
  } else {
    tool = await runWilsyDraftTool({
      intent,
      question,
      req,
      tenantId,
      operatorId,
    });
    answer = buildWilsyAnswerFromTool({
      question,
      intent,
      tool,
    });
  }

  toolRuns.push(tool);

  if (
    tool &&
    [
      'TOOL_MISSING',
      'NO_SOURCE_FOUND',
      'SOURCE_UNAVAILABLE',
      'CONNECTOR_UNAVAILABLE',
      'CONNECTOR_FAILED',
    ].includes(String(tool.status || '').toUpperCase())
  ) {
    capabilityFoundryCandidate = await stageWilsyCapabilityCandidate({
      question,
      intent,
      tool,
      tenantId,
      operatorId,
      workspaceRoute,
      workspaceSurface,
    });

    toolRuns.push(buildWilsyCapabilityFoundryToolRun(capabilityFoundryCandidate));

    const businessName = capabilityFoundryCandidate.businessName || 'Business capability';
    const candidateId = capabilityFoundryCandidate.candidateId || 'candidate pending';
    const quarantinePath =
      capabilityFoundryCandidate.quarantinePath || 'Capability Foundry quarantine';

    answer = {
      title: `${businessName} staged for review`,
      answer: `Wilsy has staged ${businessName} as a reusable capability for admin review. This capability is not live for tenant users yet.`,
      outcome:
        'Next decision: review the manifest, tool contract, proof cases, source binding, and promotion gates before publishing this capability.',
      commandPlan: [
        `Capability: ${businessName}`,
        `Candidate: ${candidateId}`,
        `Quarantine path: ${quarantinePath}`,
        `Status: ${capabilityFoundryCandidate.status || 'STAGED_FOR_REVIEW'}`,
        'Publication: not live. Human/admin approval required before registry promotion.',
        'Mutation: none.',
      ],
    };
  }

  const sourceTrace = buildWilsySourceTrace(toolRuns);
  const checklist = [
    'Verify the tool and source checked.',
    'Confirm tenant and operator identity before acting.',
    'Review evidence gaps before preparing a command.',
    'Execute only through an approved governed Wilsy command.',
  ];

  const wilsyFG81CreateLeadResponse = buildWilsyFG81LeadCreateOperatorResponse({
    operatorQuestion,
    tenantId,
    operatorId,
    workspaceRoute,
    context,
  });

  if (wilsyFG81CreateLeadResponse) {
    /* P60K5Q10FG81_CREATE_LEAD_EARLY_OPERATOR_RESPONSE */
    return wilsyFG81CreateLeadResponse;
  }

  const operatorModel = {
    intent: intent.intent,
    domain: intent.domain,
    action: intent.action,
    supported: intent.supported,
    question,
    title: answer.title,
    answer: answer.answer,
    outcome: answer.outcome,
    progress: intent.supported ? 'Tool completed' : 'Tool missing',
    quickPrompts: buildWilsyQuickPrompts(),
    actions: buildWilsyActions({
      intent,
      tool,
      answer,
    }),
    checklist,
    commandPlan: answer.commandPlan || [`Question: ${question}`, 'Mutation: none.'],
    toolRuns,
    sourceTrace,
    capabilityFoundryCandidate,
  };

  return {
    result: 'WILSY_AI_OPERATOR_MODEL_RESOLVED',
    contractVersion: 'P60K5Q10AP_CALENDAR_EXECUTION_BRIDGE_OPERATOR_KERNEL',
    mutation: tool.mutation === true,
    generatedAt,
    tenant: { tenantId, operatorId },
    workspace: context.workspace,
    evidencePosture: context.evidencePosture,
    institutionalHeaders: {
      tenantId,
      operatorId,
      generatedAt,
      route: '/api/source-registry/health',
      commandSurface: 'WILSY_OS_OPERATOR_KERNEL',
      workspaceId: context.workspace?.id,
      mutation: tool.mutation === true,
    },
    strikePayload: {
      institutionalHeaders: {
        tenantId,
        operatorId,
        generatedAt,
        route: '/api/source-registry/health',
        commandSurface: 'WILSY_OS_OPERATOR_KERNEL',
        workspaceId: context.workspace?.id,
        mutation: tool.mutation === true,
      },
      commandType:
        tool.mutation === true
          ? 'OPERATOR_KERNEL_MUTATION_COMPLETED'
          : 'READ_ONLY_OPERATOR_KERNEL_RESPONSE',
      mutation: tool.mutation === true,
    },
    operatorModel,
    toolRuns,
    bridge: 'SOURCE_REGISTRY_HEALTH_GET_OPERATOR_KERNEL',
  };
}

export default resolveWilsyAIOperatorModel;
