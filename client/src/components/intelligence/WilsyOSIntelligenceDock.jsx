/* eslint-disable */
import React, { useEffect, useMemo, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { buildWilsyOperatorIntelligence } from './wilsyOperatorIntelligenceEngine.js';
import styles from './WilsyOSIntelligenceDock.module.css';

const WILSY_INTELLIGENCE_ROOT_ID = 'wilsy-os-intelligence-dock-root';
const WILSY_INTELLIGENCE_STORAGE_KEY = 'wilsy-os-intelligence-dock-state-v2-large-productivity';
/* WILSY_P60K5Q10AG_AI_OPERATOR_MODEL_SURFACE_JSX_MARKER */
/* WILSY_P60K5Q10AH_AI_DOCK_SIZE_CONTRACT_JSX_MARKER */
const WILSY_AI_CONTEXT_ROUTE = '/api/source-registry/health?wilsyAiContext=RESOLVE';

/**
 * @function humanizeWilsyAIBackendToken
 * @description Converts internal Wilsy AI contract tokens into operator-facing language for the Intelligence Dock.
 * @param {string} value - Raw service token or status.
 * @returns {string} Human-readable label.
 * @collaboration Keeps backend contracts intact while preventing backend language from leaking into the production UI.
 */
function humanizeWilsyAIBackendToken(value = '') {
  const token = String(value || '').trim();

  const dictionary = {
    WILSY_AI_SOVEREIGN_CONTEXT_RESOLVED: 'Workspace intelligence ready',
    DETERMINISTIC_GOVERNANCE_REASONER: 'Live CRM setup guidance',
    EVIDENCE_COMPLETE: 'Checks complete',
    GOVERNANCE_AI_TIER: 'Governance guidance available',
    GOVERNANCE_AI_TIER_AVAILABLE_FOR_PACKAGING: 'Ready for workflow packaging',
    CORE_INTELLIGENCE: 'Core guidance active',
    SOURCE_REGISTRY_HEALTH_GET_CONTEXT_BRIDGE: 'Live workspace context',
  };

  if (dictionary[token]) {
    return dictionary[token];
  }

  return token
    .replace(/^WILSY_AI_/, '')
    .replace(/_/g, ' ')
    .toLowerCase()
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

/**
 * @function buildWilsyAIProductivityCopy
 * @description Shapes raw Wilsy AI context into a useful operator assistant surface without changing the backend contract.
 * @param {Object} payload - Raw Wilsy AI context payload.
 * @returns {Object} UI-safe payload with human-readable fields.
 * @collaboration Wilsy AI context resolver, CRM Setup live workspace, evidence posture, and frontend productivity shell.
 */
function buildWilsyAIProductivityCopy(payload = {}) {
  if (!payload || typeof payload !== 'object') {
    return payload;
  }

  const nextBestActions = Array.isArray(payload.nextBestActions)
    ? payload.nextBestActions.map((action) => ({
        ...action,
        title:
          action.rank === 1
            ? 'Review setup authority'
            : action.rank === 2
              ? 'Prepare release checklist'
              : action.title || 'Inspect setup queue',
        description:
          action.rank === 1
            ? 'Check role power, staged review proof, approval state, and release readiness before moving the setup forward.'
            : action.rank === 2
              ? 'Draft the evidence checklist needed before any release command is used.'
              : action.description || 'Check stale setup work and missing receipts before continuing.',
        billingTierSignal: humanizeWilsyAIBackendToken(action.billingTierSignal),
        evidenceStatus: humanizeWilsyAIBackendToken(action.evidenceStatus),
      }))
    : [];

  return {
    ...payload,
    result: humanizeWilsyAIBackendToken(payload.result),
    bridge: humanizeWilsyAIBackendToken(payload.bridge),
    workspace: {
      ...(payload.workspace || {}),
      focus: payload.workspace?.focus || 'Authority graph',
      operatingRole: payload.workspace?.operatingRole || 'Security Admin',
      monetizationSignal: humanizeWilsyAIBackendToken(payload.workspace?.monetizationSignal),
    },
    modelRoute: {
      ...(payload.modelRoute || {}),
      selectedRoute: humanizeWilsyAIBackendToken(payload.modelRoute?.selectedRoute),
      limitation: 'Read-only guidance. Nothing changes unless you approve a governed command.',
    },
    evidencePosture: {
      ...(payload.evidencePosture || {}),
      status: humanizeWilsyAIBackendToken(payload.evidencePosture?.status),
    },
    billingEntitlement: {
      ...(payload.billingEntitlement || {}),
      tier: humanizeWilsyAIBackendToken(payload.billingEntitlement?.tier),
      requiredTierSignal: humanizeWilsyAIBackendToken(payload.billingEntitlement?.requiredTierSignal),
      upgradeSignal: humanizeWilsyAIBackendToken(payload.billingEntitlement?.upgradeSignal),
    },
    nextBestActions,
    uiCopy: {
      statusTitle: 'Workspace status',
      statusSummary: 'Live CRM setup guidance is ready for this workspace.',
      lensTitle: 'Operating lens',
      nextMoveTitle: 'Recommended next step',
      coverageTitle: 'AI coverage',
    },
  };
}


/**
 * @function parseWilsyOperatorJsonResponse
 * @description Parses Wilsy Operator Kernel responses without throwing raw browser JSON errors into the UI.
 * @param {Response} response - Fetch response.
 * @returns {Promise<Object>} Parsed JSON payload.
 * @collaboration Ask Wilsy frontend loop, production JSON safety, and no-fake-answer error handling.
 */
async function parseWilsyOperatorJsonResponse(response) {
  const rawText = await response.text();

  if (!rawText || !rawText.trim()) {
    throw new Error('Wilsy Operator Kernel returned an empty response. No fake answer was generated.');
  }

  try {
    return JSON.parse(rawText);
  } catch (error) {
    throw new Error(`Wilsy Operator Kernel returned non-JSON output: ${rawText.slice(0, 180)}`);
  }
}

/**
 * @function extractWilsyPreparedWorkLink
 * @description Extracts a review or execution link from Operator Kernel model output.
 * @param {Object} model - Operator model response.
 * @returns {string} Prepared work link.
 * @collaboration Task Reminder Execution Bridge, Calendar Execution Bridge, approval review links, and productivity UI.
 */
function extractWilsyPreparedWorkLink(model = {}) {
  const tool = Array.isArray(model?.toolRuns) ? model.toolRuns[0] || {} : {};
  const answer = String(model?.answer || '');
  const commandPlan = Array.isArray(model?.commandPlan) ? model.commandPlan : [];
  const planText = commandPlan.join('\n');
  const linkPattern = /(\/crm\/(?:tasks|calendar|documents)\/(?:drafts|events)\/[A-Za-z0-9._-]+)/;
  const answerMatch = answer.match(linkPattern);
  const planMatch = planText.match(linkPattern);

  return (
    tool.crmTaskLink ||
    tool.taskLink ||
    tool.crmCalendarLink ||
    tool.eventLink ||
    tool.crmDocumentLink ||
    tool.documentLink ||
    answerMatch?.[1] ||
    planMatch?.[1] ||
    ''
  );
}

/**
 * @function buildWilsyPreparedOperatorItem
 * @description Builds a structured prepared-work card only for real prepared drafts, events, tasks, reminders, or calendar items.
 * @param {Object} model - Operator model response.
 * @returns {Object|null} Prepared work item for rendering.
 * @collaboration Ask Wilsy, task/reminder drafts, meeting drafts, approval gates, and operator productivity controls.
 */
function buildWilsyPreparedOperatorItem(model = {}) {
  const tool = Array.isArray(model?.toolRuns) ? model.toolRuns[0] || {} : {};
  const draft = tool.draft || {};
  const answer = String(model?.answer || '');
  const commandPlan = Array.isArray(model?.commandPlan) ? model.commandPlan : [];
  const planText = commandPlan.join('\n');
  const link = extractWilsyPreparedWorkLink(model);
  const status = String(tool.status || '').toUpperCase();
  const isMissingOrFoundry =
    status === 'TOOL_MISSING' ||
    status === 'NO_SOURCE_FOUND' ||
    status === 'SOURCE_UNAVAILABLE' ||
    tool.tool === 'capability_foundry' ||
    Boolean(model?.capabilityFoundryCandidate?.candidateId);

  if (isMissingOrFoundry && !draft.title && !draft.subject && !link) {
    return null;
  }

  const eligible =
    Boolean(draft.title || draft.subject) ||
    Boolean(link && /\/crm\/(?:tasks|calendar|documents)\/(?:drafts|events)\//.test(link)) ||
    ['APPROVAL_REQUIRED', 'EVENT_CREATED', 'TASK_CREATED', 'REMINDER_CREATED', 'DRAFT_PREPARED'].includes(status);

  if (!eligible) {
    return null;
  }

  const titleFromAnswer = answer.match(/Title:\s*([^.;]+)/i)?.[1];
  const dateFromAnswer = answer.match(/Due date:\s*([^.;]+)/i)?.[1] || answer.match(/Date:\s*([^.;]+)/i)?.[1];
  const timeFromAnswer = answer.match(/Time:\s*([^.;]+)/i)?.[1];
  const priorityFromAnswer = answer.match(/Priority:\s*([^.;]+)/i)?.[1];

  const kind =
    draft.kind ||
    (String(tool.tool || '').includes('document') ? 'document' : '') ||
    (String(tool.tool || '').includes('calendar') ? 'meeting' : '') ||
    (String(model?.action || '').includes('reminder') ? 'reminder' : '') ||
    (String(model?.action || '').includes('task') ? 'task' : '') ||
    'work item';

  const fields = [
    {
      label: 'Document type',
      value: draft.documentType || '',
    },
    {
      label: 'Title',
      value: draft.title || draft.subject || titleFromAnswer || '',
    },
    {
      label: 'Purpose',
      value: draft.purpose || '',
    },
    {
      label: 'Delivery requested',
      value: typeof draft.deliveryRequested === 'boolean' ? (draft.deliveryRequested ? 'Yes' : 'No') : '',
    },
    {
      label: kind === 'meeting' ? 'Date' : 'Due date',
      value: draft.dueDateLabel || draft.dateLabel || dateFromAnswer || '',
    },
    {
      label: 'Time',
      value: draft.timeLabel || timeFromAnswer || '',
    },
    {
      label: 'Priority',
      value: draft.priority || priorityFromAnswer || '',
    },
    {
      label: 'Duration',
      value: draft.durationLabel || '',
    },
    {
      label: 'Participants',
      value: Array.isArray(draft.participants) ? draft.participants.join(', ') : '',
    },
    {
      label: 'Agenda',
      value: draft.agenda || '',
    },
  ].filter((field) => field.value);

  if (fields.length === 0 && !link) {
    return null;
  }

  return {
    kind,
    title: `${kind.charAt(0).toUpperCase()}${kind.slice(1)} prepared`,
    status: tool.statusLabel || 'Approval required',
    link,
    linkLabel: link.includes('/documents/drafts/') ? 'Review Draft' : link.includes('/events/') || (link.includes('/tasks/') && !link.includes('/drafts/')) ? 'Open item' : 'Open review',
    planText: planText || answer,
    documentPreview: tool.documentPreview || draft.documentPreview || null,
    fields,
  };
}

/**
 * @function hasWilsyCapabilityCandidate
 * @description Detects whether the Operator Kernel response contains a Capability Foundry candidate.
 * @param {Object} model - Operator model.
 * @returns {boolean} Whether a Foundry candidate exists.
 * @collaboration Capability Foundry, no-fake-answer policy, and single-answer UI normalization.
 */
function hasWilsyCapabilityCandidate(model = {}) {
  return Boolean(model?.capabilityFoundryCandidate?.candidateId);
}

/**
 * @function buildWilsyFoundryDisplayTitle
 * @description Builds a clean business title for Capability Foundry responses.
 * @param {Object} model - Operator model.
 * @returns {string} Display title.
 * @collaboration Capability Foundry, tenant-facing business English, and answer normalization.
 */
function buildWilsyFoundryDisplayTitle(model = {}) {
  const candidate = model?.capabilityFoundryCandidate;

  if (!candidate?.candidateId) {
    return model?.title || 'Wilsy answer';
  }

  return `${candidate.businessName || 'Capability'} staged for review`;
}

/**
 * @function buildWilsyFoundryDisplayAnswer
 * @description Builds a clean business answer for Capability Foundry responses and suppresses generic tool language.
 * @param {Object} model - Operator model.
 * @returns {string} Display answer.
 * @collaboration Capability Foundry, no-fake-answer policy, and tenant productivity UI.
 */
function buildWilsyFoundryDisplayAnswer(model = {}) {
  const candidate = model?.capabilityFoundryCandidate;

  if (!candidate?.candidateId) {
    return model?.answer || '';
  }

  return `Wilsy cannot complete this request from the approved production registry yet. A reusable capability has been staged for admin review: ${candidate.businessName || 'Capability candidate'}. Candidate: ${candidate.candidateId}.`;
}

/**
 * @function buildWilsyFoundryDisplayOutcome
 * @description Builds a clean business outcome for Capability Foundry responses.
 * @param {Object} model - Operator model.
 * @returns {string} Display outcome.
 * @collaboration Capability Foundry, approval gates, self-extending tool registry, and production honesty.
 */
function buildWilsyFoundryDisplayOutcome(model = {}) {
  const candidate = model?.capabilityFoundryCandidate;

  if (!candidate?.candidateId) {
    return model?.outcome || '';
  }

  return 'Next decision: review the manifest, tool contract, proof cases, source binding, and promotion gates before publishing this capability.';
}

/**
 * @function getWilsyDisplayTitle
 * @description Returns the normalized answer title for regular and Capability Foundry responses.
 * @param {Object} model - Operator model.
 * @returns {string} Display title.
 * @collaboration Ask Wilsy answer surface, Capability Foundry, and production business-English output.
 */
function getWilsyDisplayTitle(model = {}) {

  /* WILSY_P60K5Q10DG_NATURAL_TITLE_GUARD */
  const wilsyMachineGapTitleText = [
    model?.title,
    model?.answer,
    model?.outcome,
    model?.status,
    model?.code,
    model?.errorCode,
    model?.reason,
    ...(Array.isArray(model?.sourceTrace) ? model.sourceTrace.map((trace) => `${trace?.tool || trace?.label || ''} ${trace?.status || ''} ${trace?.message || ''}`) : []),
  ]
    .filter(Boolean)
    .join(' ');

  if (/QUANTUM_LINK|_RESTORING|NO FAKE GUIDANCE|failed tool response|I cannot answer that yet|tool response is visible for repair/i.test(wilsyMachineGapTitleText)) {
    return 'Source connection needs repair';
  }
  return hasWilsyCapabilityCandidate(model) ? buildWilsyFoundryDisplayTitle(model) : model?.title || 'Wilsy answer';
}
/**
 * @function getWilsyModelAnswer
 * @description Returns the visible Wilsy Answer text from the operator model while preserving capability-foundry display behavior.
 * @param {object} model - Operator model.
 * @returns {string} Sanitized Wilsy Answer text.
 * @collaboration Wilsy Answer, capability foundry, document review panel, and split AI dock runtime.
 */
function getWilsyModelAnswer(model = {}) {
  return sanitizeWilsyVisibleOperatorText(hasWilsyCapabilityCandidate(model) ? buildWilsyFoundryDisplayAnswer(model) : model?.answer || '');
}

/**
 * @function getWilsyModelOutcome
 * @description Returns the visible Wilsy outcome text from the operator model while preserving capability-foundry display behavior.
 * @param {object} model - Operator model.
 * @returns {string} Sanitized Wilsy outcome text.
 * @collaboration Wilsy Answer, capability foundry, document review panel, and split AI dock runtime.
 */
function getWilsyModelOutcome(model = {}) {
  return sanitizeWilsyVisibleOperatorText(hasWilsyCapabilityCandidate(model) ? buildWilsyFoundryDisplayOutcome(model) : model?.outcome || '');
}

/**
 * @function getWilsyDisplayAnswer
 * @description Provides a stable visible answer helper for Wilsy Answer rendering without breaking older dock render paths.
 * @param {object} model - Operator model or display model.
 * @returns {string} Sanitized visible answer.
 * @collaboration Wilsy Answer, operator model display, document review panel, and split AI dock runtime.
 */
function getWilsyDisplayAnswer(model = {}) {

  /* WILSY_P60K5Q10DG_NATURAL_ANSWER_GUARD */
  const wilsyMachineGapAnswerText = [
    model?.title,
    model?.answer,
    model?.outcome,
    model?.status,
    model?.code,
    model?.errorCode,
    model?.reason,
    ...(Array.isArray(model?.sourceTrace) ? model.sourceTrace.map((trace) => `${trace?.tool || trace?.label || ''} ${trace?.status || ''} ${trace?.message || ''}`) : []),
  ]
    .filter(Boolean)
    .join(' ');

  if (/QUANTUM_LINK|_RESTORING|NO FAKE GUIDANCE|failed tool response|I cannot answer that yet|tool response is visible for repair/i.test(wilsyMachineGapAnswerText)) {
    const sourceLabel = Array.isArray(model?.sourceTrace) && (model.sourceTrace[0]?.tool || model.sourceTrace[0]?.label)
      ? (model.sourceTrace[0]?.tool || model.sourceTrace[0]?.label)
      : 'operator source';

    return `I checked the ${sourceLabel}, but the command link is still restoring. I will not guess or invent guidance. Next move: restore the source connection, then rerun the request.`;
  }
  if (typeof getWilsyModelAnswer === 'function') {
    return getWilsyModelAnswer(model);
  }

  if (typeof sanitizeWilsyVisibleOperatorText === 'function') {
    return sanitizeWilsyVisibleOperatorText(model?.answer || '');
  }

  return String(model?.answer || '').trim();
}

/**
 * @function getWilsyDisplayOutcome
 * @description Provides a stable visible outcome helper so the Wilsy AI dock cannot crash when rendering outcome text.
 * @param {object} model - Operator model or display model.
 * @returns {string} Sanitized visible outcome.
 * @collaboration Wilsy Answer, operator model display, document review panel, and split AI dock runtime.
 */
function getWilsyDisplayOutcome(model = {}) {

  /* WILSY_P60K5Q10DG_NATURAL_OUTCOME_GUARD */
  const wilsyMachineGapOutcomeText = [
    model?.title,
    model?.answer,
    model?.outcome,
    model?.status,
    model?.code,
    model?.errorCode,
    model?.reason,
    ...(Array.isArray(model?.sourceTrace) ? model.sourceTrace.map((trace) => `${trace?.tool || trace?.label || ''} ${trace?.status || ''} ${trace?.message || ''}`) : []),
  ]
    .filter(Boolean)
    .join(' ');

  if (/QUANTUM_LINK|_RESTORING|NO FAKE GUIDANCE|failed tool response|I cannot answer that yet|tool response is visible for repair/i.test(wilsyMachineGapOutcomeText)) {
    const sourceLabel = Array.isArray(model?.sourceTrace) && (model.sourceTrace[0]?.tool || model.sourceTrace[0]?.label)
      ? (model.sourceTrace[0]?.tool || model.sourceTrace[0]?.label)
      : 'operator source';

    return `Checked: ${sourceLabel} · Needs source repair · Next: restore command link`;
  }
  if (typeof getWilsyModelOutcome === 'function') {
    return getWilsyModelOutcome(model);
  }

  if (typeof sanitizeWilsyVisibleOperatorText === 'function') {
    return sanitizeWilsyVisibleOperatorText(model?.outcome || model?.answer || '');
  }

  return String(model?.outcome || model?.answer || '').trim();
}

/**
 * @function sanitizeWilsyVisibleOperatorText
 * @description Removes raw internal CRM routes from visible Wilsy Answer text while preserving governed review actions in Prepared Work.
 * @param {string} value - Visible answer value.
 * @returns {string} Business-readable visible text without internal route leakage.
 * @collaboration Wilsy Answer, Prepared Work, tenant document review, approval plan, and no-reset AI workspace.
 */
function sanitizeWilsyVisibleOperatorText(value = '') {
  return String(value || '')
    .replace(/Review link:\s*\/crm\/(?:documents|tasks|calendar)\/(?:drafts|events)\/[A-Za-z0-9._-]+\.?/gi, 'Use Review Draft to inspect the governed draft.')
    .replace(/\/crm\/(?:documents|tasks|calendar)\/(?:drafts|events)\/[A-Za-z0-9._-]+/gi, 'the governed review action')
    .replace(/\bQUANTUM_LINK_RESTORING\b/gi, 'the command link is still restoring')
    /* WILSY_P60K5Q10DG_MACHINE_TEXT_SANITIZER */
    .replace(/\b[A-Z]{2,}_[A-Z0-9_]{2,}\b/g, '')
    .replace(/NO FAKE GUIDANCE WAS GENERATED\.?/gi, 'I will not guess or invent guidance.')
    .replace(/THE FAILED TOOL RESPONSE IS VISIBLE FOR REPAIR\.?/gi, 'The source issue is visible for repair.')
    .replace(/\s+/g, ' ')
    .trim();
}

/**
 * @function normalizeWilsyFoundryModelForDisplay
 * @description Normalizes Capability Foundry responses before React state render so stale generic wording cannot leak into the UI.
 * @param {Object} model - Operator model response.
 * @returns {Object} Normalized model.
 * @collaboration Capability Foundry, no-fake-answer policy, and single-answer production UI.
 */
function normalizeWilsyFoundryModelForDisplay(model = {}) {
  const candidate = model?.capabilityFoundryCandidate;

  if (!candidate?.candidateId) {
    return model;
  }

  const businessName = candidate.businessName || 'Business capability';
  const candidateId = candidate.candidateId;

  return {
    ...model,
    title: `${businessName} staged for review`,
    answer: `Wilsy has staged ${businessName} as a reusable capability for admin review. This capability is not live for tenant users yet.`,
    outcome: 'Next decision: review the manifest, tool contract, proof cases, source binding, and promotion gates before publishing this capability.',
  };
}

/**
 * @function buildWilsyCapabilityReviewItem
 * @description Builds one review surface for Capability Foundry candidates.
 * @param {Object} model - Operator model response.
 * @returns {Object|null} Capability review item.
 * @collaboration Capability Foundry, self-extending tool registry, approval gates, and no-fake-answer workflow.
 */
function buildWilsyCapabilityReviewItem(model = {}) {
  const candidate = model?.capabilityFoundryCandidate;

  if (!candidate?.candidateId) {
    return null;
  }

  return {
    candidateId: candidate.candidateId,
    capabilityId: candidate.capabilityId,
    businessName: candidate.businessName || 'Capability candidate',
    status: candidate.status || 'STAGED_FOR_REVIEW',
    quarantinePath: candidate.quarantinePath || '',
    approvalRequired: candidate.approvalRequired !== false,
    nextDecision: 'Review manifest, tool contract, proof cases, source binding, and promotion gates before publishing.',
    planText: [
      `Capability: ${candidate.businessName || 'Capability candidate'}`,
      `Candidate: ${candidate.candidateId}`,
      `Status: ${candidate.status || 'STAGED_FOR_REVIEW'}`,
      `Quarantine: ${candidate.quarantinePath || 'not available'}`,
      'Publication: not live. Human/admin approval required before promotion.',
    ].join('\n'),
  };
}

/**
 * @function buildWilsyOperatorAskUrl
 * @description Builds the backend Wilsy Operator Model GET URL using the proven source-registry health bridge.
 * @param {string} prompt - Operator question.
 * @param {Object} snapshot - Current workspace snapshot.
 * @param {Object} context - Current merged context.
 * @returns {string} Backend ask URL.
 * @collaboration Q10Z source-registry GET bridge, Wilsy Operator Model backend, and browser-safe no-mutation ask loop.
 */
function buildWilsyOperatorAskUrl(prompt = '', snapshot = {}, context = {}) {
  const url = new URL(WILSY_AI_CONTEXT_ROUTE, window.location.origin);

  url.searchParams.set('wilsyAiContext', 'ASK');
  url.searchParams.set('operatorQuestion', String(prompt || '').trim());
  url.searchParams.set('tenantId', window.localStorage?.getItem('wilsy-tenant-id') || 'MASTER');
  url.searchParams.set('operatorId', window.localStorage?.getItem('wilsy-operator-id') || 'WILSY_OPERATOR');
  url.searchParams.set('workspaceRoute', snapshot.path || window.location.pathname || '/crm/setup');
  url.searchParams.set(
    'workspaceSurface',
    String(snapshot.text || context.focus || 'CRM Operating Controls Authority Graph Evidence Approval Release').slice(0, 1400)
  );

  return url.pathname + url.search;
}

/**
 * @function resolveWilsyOperatorIntent
 * @description Resolves the operator's question or quick prompt into a productive Wilsy AI intent.
 * @param {string} prompt - Operator-entered prompt.
 * @param {string} activePrompt - Current selected quick prompt id.
 * @returns {string} Operator intent id.
 * @collaboration Wilsy AI dock prompt loop, CRM Setup workspace context, and governed command preparation.
 */
function resolveWilsyOperatorIntent(prompt = '', activePrompt = 'what_next') {
  const text = String(prompt || '').toLowerCase();
  const isLeadPrompt = /\blead\b|\bleads\b|prospect|prospects/i.test(text);
  const isTaskPrompt = /\btask\b|\btasks\b|todo|to-do|follow up|follow-up/i.test(text);

  if (isLeadPrompt) {
    return 'crm_leads_summary';
  }

  if (isTaskPrompt) {
    return text.includes('next week') ? 'crm_tasks_due_next_week' : 'crm_tasks_due_this_week';
  }

  if (text.includes('release') || text.includes('ready') || text.includes('approval')) {
    return 'release_readiness';
  }

  if (text.includes('authority') || text.includes('role') || text.includes('permission')) {
    return 'authority_graph';
  }

  if (text.includes('evidence') || text.includes('checklist') || text.includes('proof')) {
    return 'evidence_checklist';
  }

  if (text.includes('queue') || text.includes('stale') || text.includes('missing')) {
    return 'queue_hygiene';
  }

  if (text.includes('package') || text.includes('bill') || text.includes('tenant') || text.includes('tier')) {
    return 'workflow_packaging';
  }

  return activePrompt || 'what_next';
}

/**
 * @function buildWilsyOperatorModelSurface
 * @description Builds the user-facing Wilsy Operator Model answer, action board, and governed command plan from live workspace context.
 * @param {Object} params - Operator model input bundle.
 * @param {Object} params.context - Merged workspace context.
 * @param {Object} params.backendContext - Live backend context.
 * @param {Array} params.cards - Legacy card data used only as fallback evidence.
 * @param {string} params.operatorPrompt - Current operator prompt.
 * @param {string} params.activePrompt - Current quick prompt id.
 * @returns {Object} Operator model surface.
 * @collaboration Q10Z live AI context, CRM Setup authority graph, evidence posture, release controls, and human approval boundary.
 */
function buildWilsyOperatorModelSurface({
  context = {},
  backendContext = {},
  cards = [],
  operatorPrompt = '',
  activePrompt = 'what_next',
} = {}) {
  const intent = resolveWilsyOperatorIntent(operatorPrompt, activePrompt);
  const workspaceName = context.workspace || backendContext?.workspace?.label || 'Current workspace';
  const role = context.role || backendContext?.workspace?.operatingRole || 'Operator';
  const focus = context.focus || backendContext?.workspace?.focus || 'Workspace control';
  const actions = Array.isArray(backendContext?.nextBestActions) && backendContext.nextBestActions.length > 0
    ? backendContext.nextBestActions
    : cards.map((card, index) => ({
        rank: index + 1,
        title: card.title,
        description: card.body,
        mode: 'read_only',
        mutation: false,
      }));

  const actionDefaults = [
    {
      rank: 1,
      title: 'Review setup authority',
      description: 'Check who can approve, release, withdraw, and verify this setup packet.',
      mode: 'read_only',
      mutation: false,
    },
    {
      rank: 2,
      title: 'Prepare release checklist',
      description: 'Build the checklist needed before any release command can be used.',
      mode: 'draft_only',
      mutation: false,
    },
    {
      rank: 3,
      title: 'Inspect queue hygiene',
      description: 'Find stale setup work, missing receipts, and unresolved approval blockers.',
      mode: 'read_only',
      mutation: false,
    },
  ];

  const productiveActions = actions.length > 0 ? actions.slice(0, 4) : actionDefaults;

  const answerMap = {
    what_next: {
      title: 'Here is the next useful move',
      answer: `For ${workspaceName}, start with authority and evidence. Confirm ${role} has the right control path, then check staged review proof, approval state, and release readiness before moving work forward.`,
      outcome: 'Move setup work forward without guessing.',
    },
    release_readiness: {
      title: 'Release readiness check',
      answer: 'Before release, verify staged review proof, approval state, release permission, packet integrity, and receipt trail. Do not use a release command until all five checks are clear.',
      outcome: 'Prevent premature release and protect audit posture.',
    },
    authority_graph: {
      title: 'Authority graph interpretation',
      answer: `The active lens is ${focus}. Use it to match each action to the authority available in this workspace: who can review, who can approve, who can release, and what proof each step needs.`,
      outcome: 'Match every action to authority before execution.',
    },
    evidence_checklist: {
      title: 'Evidence checklist',
      answer: 'Collect staged review proof, packet status, approval receipt, release readiness, operator identity, tenant identity, and command-surface evidence before any governed command.',
      outcome: 'Create an approval-ready evidence pack.',
    },
    queue_hygiene: {
      title: 'Queue hygiene review',
      answer: 'Inspect setup reviews for stale status, missing receipts, repeated pending states, orphaned approvals, and release blockers. Prioritize items with proof gaps first.',
      outcome: 'Clear blockers before new setup work enters the queue.',
    },
    workflow_packaging: {
      title: 'Tenant value packaging',
      answer: 'Package this as governance guidance: authority checks, release readiness, evidence checklist, and queue hygiene. That is billable productivity because it reduces approval risk and saves operator time.',
      outcome: 'Turn live guidance into a tenant-facing workflow tier.',
    },
  };

  const selected = answerMap[intent] || answerMap.what_next;

  const checklist = [
    'Confirm tenant and operator identity are visible.',
    'Check staged review proof and current approval state.',
    'Verify release readiness before any release command.',
    'Capture evidence gaps before moving to the next packet.',
    'Prepare a governed command only after the operator approves.',
  ];

  const quickPrompts = [
    { id: 'what_next', label: 'What should I do next?' },
    { id: 'release_readiness', label: 'Check release readiness' },
    { id: 'authority_graph', label: 'Explain authority graph' },
    { id: 'evidence_checklist', label: 'Prepare evidence checklist' },
    { id: 'queue_hygiene', label: 'Inspect queue hygiene' },
    { id: 'workflow_packaging', label: 'Package tenant workflow' },
  ];

  return {
    intent,
    title: selected.title,
    answer: selected.answer,
    outcome: selected.outcome,
    quickPrompts,
    actions: productiveActions,
    checklist,
    commandPlan: [
      `Workspace: ${workspaceName}`,
      `Operator role: ${role}`,
      `Intent: ${selected.title}`,
      `Outcome: ${selected.outcome}`,
      ...checklist.map((item) => `Check: ${item}`),
      'Mutation: none until approved through a governed Wilsy command.',
    ],
  };
}

/**
 * @function readWilsyVisibleText
 * @description Reads a bounded sample of visible workspace text so Wilsy Intelligence can infer the operator's current context.
 * @returns {string} Bounded visible document text.
 * @collaboration Wilsy OS global workspaces, CRM Setup Control Plane, Billing workspace, command rails, and adaptive intelligence runtime.
 */
function readWilsyVisibleText() {
  if (typeof document === 'undefined' || !document.body) {
    return '';
  }

  return String(document.body.innerText || '')
    .replace(/\s+/g, ' ')
    .trim()
    .slice(0, 9000);
}

/**
 * @function readWilsyStorageValue
 * @description Reads non-secret local storage values that identify tenant or operator posture.
 * @param {Array<string>} keys - Candidate local storage keys.
 * @param {string} fallback - Fallback value.
 * @returns {string} Resolved non-secret value.
 * @collaboration Browser runtime, tenant context shell, operator context, and Wilsy AI evidence headers.
 */
function readWilsyStorageValue(keys = [], fallback = '') {
  if (typeof localStorage === 'undefined') {
    return fallback;
  }

  for (const key of keys) {
    const value = localStorage.getItem(key);
    if (value) {
      return value;
    }
  }

  return fallback;
}

/**
 * @function resolveWilsyWorkspaceIntent
 * @description Classifies the active Wilsy OS workspace from URL, title, and visible screen text.
 * @param {string} path - Current browser path.
 * @param {string} text - Bounded visible workspace text.
 * @returns {Object} Workspace context used by the global intelligence dock.
 * @collaboration Wilsy OS routing, CRM workspaces, billing roadmap, setup controls, evidence workflows, and productivity intelligence.
 */
function resolveWilsyWorkspaceIntent(path = '', text = '') {
  const haystack = `${path} ${text}`.toLowerCase();

  if (haystack.includes('billing') || haystack.includes('invoice') || haystack.includes('revenue ledger')) {
    return {
      workspace: 'Billing',
      focus: 'Revenue assurance',
      role: 'Finance Operator',
      state: 'Billing posture detected',
      purpose: 'Track invoices, receipts, payment state, revenue leakage, tenant entitlements, and future Wilsy AI monetization tiers.',
      nextAction: 'Check open invoices, failed payments, plan limits, and evidence receipts before changing billing state.',
      tierSignal: 'Future value-added AI tier candidate',
    };
  }

  if (haystack.includes('crm operating controls') || haystack.includes('authority graph') || haystack.includes('setup map')) {
    return {
      workspace: 'CRM Setup',
      focus: 'Authority Graph',
      role: 'Security Admin',
      state: 'Setup authority posture detected',
      purpose: 'Watch role power, authority surfaces, evidence posture, approval state, release readiness, and queue hygiene.',
      nextAction: 'Use evidence, approval, release, and queue clear only through governed command paths with receipt proof.',
      tierSignal: 'Included in CRM governance intelligence',
    };
  }

  if (haystack.includes('meeting') || haystack.includes('instant manifest') || haystack.includes('import ledger')) {
    return {
      workspace: 'CRM Meetings',
      focus: 'Meetings Operating Cockpit',
      role: 'CRM Operator',
      state: 'Meeting workflow posture detected',
      purpose: 'Track Sync Data Engine, Instant Manifest, Import Ledger, Evidence Vault, and Universal Filter Stream.',
      nextAction: 'Validate meeting evidence, sync freshness, and import receipts before acting on records.',
      tierSignal: 'Operational intelligence module',
    };
  }

  if (haystack.includes('dashboard') || haystack.includes('founder') || haystack.includes('executive')) {
    return {
      workspace: 'Executive OS',
      focus: 'Operating dashboard',
      role: 'Founder / Executive',
      state: 'Executive command posture detected',
      purpose: 'Surface operating risk, revenue signal, compliance posture, and command priorities across the current boardroom surface.',
      nextAction: 'Inspect active risk cards, revenue signals, and command receipts before escalating.',
      tierSignal: 'Executive intelligence layer',
    };
  }

  return {
    workspace: 'Wilsy OS',
    focus: 'Current workspace',
    role: 'Operator',
    state: 'Workspace context active',
    purpose: 'Read the current route and visible work surface, then turn the screen into context-aware actions and evidence posture.',
    nextAction: 'Continue working; Wilsy AI will adapt as the visible workspace changes.',
    tierSignal: 'Core intelligence layer',
  };
}

/**
 * @function buildWilsyIntelligenceCards
 * @description Builds adaptive cards for the current workspace so the dock gives useful, contextual operator guidance.
 * @param {Object} context - Workspace context.
 * @returns {Array<Object>} Adaptive intelligence cards.
 * @collaboration Wilsy OS Intelligence, CRM setup controls, billing tiers roadmap, governance receipts, and operator productivity loops.
 */
function buildWilsyIntelligenceCards(context = {}) {
  return [
    {
      label: 'WORKSPACE STATUS',
      title: context.state,
      body: context.purpose,
    },
    {
      label: 'OPERATING LENS',
      title: context.role,
      body: `Focus: ${context.focus}. Match actions to the authority and evidence available in this workspace.`,
    },
    {
      label: 'RECOMMENDED NEXT STEP',
      title: 'Operator guidance',
      body: context.nextAction,
    },
    {
      label: 'AI COVERAGE',
      title: context.tierSignal,
      body: context.billingDetail || 'This global intelligence surface is built to support future Wilsy OS billing tiers without changing workspace workflows.',
    },
  ];
}

/**
 * @function loadWilsyDockState
 * @description Loads the persisted Wilsy Intelligence dock view state from local storage.
 * @returns {Object} Persisted dock state.
 * @collaboration Wilsy OS global dock runtime, operator preferences, all workspaces, and persistent productivity controls.
 */
function loadWilsyDockState() {
  if (typeof localStorage === 'undefined') {
    return { collapsed: false, focusMode: false };
  }

  try {
    return {
      collapsed: false,
      focusMode: false,
      ...JSON.parse(localStorage.getItem(WILSY_INTELLIGENCE_STORAGE_KEY) || '{}'),
    };
  } catch {
    return { collapsed: false, focusMode: false };
  }
}

/**
 * @function saveWilsyDockState
 * @description Persists the Wilsy Intelligence dock state without touching workspace data.
 * @param {Object} state - Dock UI state.
 * @returns {void}
 * @collaboration Wilsy OS global dock runtime, browser storage, and operator display preference continuity.
 */
function saveWilsyDockState(state = {}) {
  if (typeof localStorage === 'undefined') {
    return;
  }

  localStorage.setItem(WILSY_INTELLIGENCE_STORAGE_KEY, JSON.stringify(state));
}

/**
 * @function buildWilsyAIInstitutionalHeaders
 * @description Builds institutional headers for the read-only Wilsy AI context resolver request.
 * @param {Object} snapshot - Workspace snapshot.
 * @returns {Object} Institutional headers.
 * @collaboration Global intelligence dock, backend AI context resolver, tenant scope, and strike payload evidence contract.
 */
function buildWilsyAIInstitutionalHeaders(snapshot = {}) {
  const generatedAt = new Date().toISOString();
  const tenantId = readWilsyStorageValue(['wilsyTenantId', 'tenantId', 'activeTenantId'], 'MASTER');
  const operatorId = readWilsyStorageValue(['wilsyOperatorId', 'operatorId', 'userId'], 'BROWSER_OPERATOR');

  return {
    tenantId,
    operatorId,
    generatedAt,
    route: WILSY_AI_CONTEXT_ROUTE,
    commandSurface: 'WILSY_OS_INTELLIGENCE_DOCK',
    workspaceRoute: snapshot.path || '',
    contractVersion: 'P60K5Q10_FRONTEND_CONTEXT_REQUEST',
    mutation: false,
  };
}

/**
 * @function buildWilsyAIContextRequest
 * @description Builds the full evidence-bearing payload sent to the read-only Wilsy AI context resolver.
 * @param {Object} snapshot - Workspace snapshot.
 * @returns {Object} Request payload.
 * @collaboration Workspace sensor, institutional headers, strike payload, backend context resolver, and no-mutation AI contract.
 */
function buildWilsyAIContextRequest(snapshot = {}) {
  const institutionalHeaders = buildWilsyAIInstitutionalHeaders(snapshot);

  return {
    tenantId: institutionalHeaders.tenantId,
    operatorId: institutionalHeaders.operatorId,
    workspaceRoute: snapshot.path || '',
    workspaceSurface: snapshot.text || '',
    operatorIntent: snapshot.intent || '',
    generatedAt: institutionalHeaders.generatedAt,
    institutionalHeaders,
    strikePayload: {
      institutionalHeaders: { ...institutionalHeaders },
      commandSurface: 'WILSY_OS_INTELLIGENCE_DOCK',
      commandType: 'READ_ONLY_AI_CONTEXT_RESOLUTION',
      mutation: false,
    },
  };
}

/**
 * @function mergeWilsyBackendContext
 * @description Merges backend sovereign context with local fallback context for resilient dock rendering.
 * @param {Object} localContext - Local context.
 * @param {Object|null} backendContext - Backend context response.
 * @returns {Object} Renderable context.
 * @collaboration Backend Wilsy AI context resolver, local workspace inference, evidence posture, billing entitlement, and dock cards.
 */
function mergeWilsyBackendContext(localContext = {}, backendContext = null) {
  if (!backendContext?.workspace) {
    return localContext;
  }

  const topAction = backendContext.nextBestActions?.[0];
  return {
    workspace: backendContext.workspace.label || localContext.workspace,
    focus: backendContext.workspace.focus || localContext.focus,
    role: backendContext.workspace.operatingRole || localContext.role,
    state: backendContext.result || localContext.state,
    purpose: backendContext.modelRoute?.selectedRoute
      ? `Guidance source: ${backendContext.modelRoute.selectedRoute}. Checks: ${backendContext.evidencePosture?.status || 'UNKNOWN'}.`
      : localContext.purpose,
    nextAction: topAction ? `${topAction.title}: ${topAction.description}` : localContext.nextAction,
    tierSignal: backendContext.billingEntitlement?.requiredTierSignal || localContext.tierSignal,
    billingDetail: backendContext.billingEntitlement?.upgradeSignal || localContext.billingDetail,
    backendContext,
  };
}

/**
 * @function useWilsyWorkspaceContext
 * @description Observes route and DOM changes so Wilsy Intelligence dynamically adapts to the user's active workspace.
 * @returns {Object} Adaptive workspace snapshot and local context.
 * @collaboration MutationObserver, browser routing, Wilsy OS workspaces, CRM, billing, meetings, and executive command surfaces.
 */
function useWilsyWorkspaceContext() {
  const [snapshot, setSnapshot] = useState(() => ({
    path: typeof window === 'undefined' ? '' : window.location.pathname,
    text: readWilsyVisibleText(),
    intent: '',
  }));

  useEffect(() => {
    if (typeof window === 'undefined') {
      return undefined;
    }

    let frame = 0;

    /**
     * @function refreshWilsyWorkspaceSnapshot
     * @description Refreshes the current route and visible-text context for Wilsy OS Intelligence.
     * @returns {void}
     * @collaboration Global Wilsy dock, workspace DOM, browser route changes, and adaptive operator guidance.
     */
    function refreshWilsyWorkspaceSnapshot() {
      cancelAnimationFrame(frame);
      frame = requestAnimationFrame(() => {
        setSnapshot({
          path: window.location.pathname,
          text: readWilsyVisibleText(),
          intent: '',
        });
      });
    }

    const observer = new MutationObserver(refreshWilsyWorkspaceSnapshot);
    observer.observe(document.body, { childList: true, subtree: true, characterData: true });

    window.addEventListener('popstate', refreshWilsyWorkspaceSnapshot);
    window.addEventListener('hashchange', refreshWilsyWorkspaceSnapshot);
    window.addEventListener('wilsy:workspace-context-changed', refreshWilsyWorkspaceSnapshot);

    const interval = window.setInterval(refreshWilsyWorkspaceSnapshot, 3500);

    return () => {
      cancelAnimationFrame(frame);
      observer.disconnect();
      window.removeEventListener('popstate', refreshWilsyWorkspaceSnapshot);
      window.removeEventListener('hashchange', refreshWilsyWorkspaceSnapshot);
      window.removeEventListener('wilsy:workspace-context-changed', refreshWilsyWorkspaceSnapshot);
      window.clearInterval(interval);
    };
  }, []);

  return useMemo(
    () => ({
      snapshot,
      localContext: resolveWilsyWorkspaceIntent(snapshot.path, snapshot.text),
    }),
    [snapshot]
  );
}

/**
 * @function useWilsySovereignBrainContext
 * @description Calls the read-only backend Wilsy AI context resolver and falls back to local context if unavailable.
 * @param {Object} snapshot - Workspace snapshot.
 * @param {Object} localContext - Local context.
 * @returns {Object} Backend-aware render context.
 * @collaboration Wilsy AI sovereign context route, global dock, workspace sensor, evidence contract, and resilient frontend fallback.
 */
function useWilsySovereignBrainContext(snapshot = {}, localContext = {}) {
  const [backendContext, setBackendContext] = useState(null);
  const [status, setStatus] = useState('LOCAL_CONTEXT');

  useEffect(() => {
    if (typeof window === 'undefined') {
      return undefined;
    }

    const controller = new AbortController();

    /**
     * @function fetchWilsySovereignContext
     * @description Fetches the backend read-only Wilsy AI sovereign context contract.
     * @returns {Promise<void>} Updates backend context state.
     * @collaboration Browser fetch, Express AI route, institutional headers, strike payload, and global intelligence dock.
     */
    async function fetchWilsySovereignContext() {
      try {
        const payload = buildWilsyAIContextRequest(snapshot);
        const response = await fetch(WILSY_AI_CONTEXT_ROUTE, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            'X-Tenant-Id': payload.tenantId,
            'X-Operator-Id': payload.operatorId,
            'X-Wilsy-Command-Surface': 'WILSY_OS_INTELLIGENCE_DOCK',
          },          signal: controller.signal,
        });

        if (!response.ok) {
          throw new Error(`Wilsy AI context resolver returned ${response.status}`);
        }

        const rawWilsyAIData = await response.json();
        const data = buildWilsyAIProductivityCopy(rawWilsyAIData);
        setBackendContext(data);
        setStatus('SOVEREIGN_CONTEXT');
      } catch (error) {
        if (error?.name !== 'AbortError') {
          setStatus('LOCAL_FALLBACK');
          setBackendContext(null);
        }
      }
    }

    fetchWilsySovereignContext();

    return () => {
      controller.abort();
    };
  }, [snapshot.path, snapshot.text]);

  return {
    status,
    context: mergeWilsyBackendContext(localContext, backendContext),
    backendContext,
  };
}

/**
 * @function WilsyOSIntelligenceDock
 * @description Renders the global Wilsy OS adaptive intelligence dock visible across workspaces.
 * @returns {JSX.Element} Global Wilsy Intelligence sidecar.
 * @collaboration All Wilsy OS workspaces, CRM Setup, Billing roadmap, Staged Reviews, command rails, and future monetized intelligence tiers.
 */
export function WilsyOSIntelligenceDock() {

  /* WILSY_P60K5Q10BN_DOCUMENT_REVIEW_STATE_SCOPE */
  const [activeDocumentReview, setActiveDocumentReview] = useState(null);
  const activeDocumentReviewFields = Array.isArray(activeDocumentReview?.fields)
    ? activeDocumentReview.fields.reduce((accumulator, field) => {
        accumulator[String(field.label || '').toLowerCase()] = field.value;
        return accumulator;
      }, {})
    : {};
  const activeDocumentReviewPreview = activeDocumentReview?.documentPreview || (activeDocumentReview
    ? {
        previewVersion: 'P60K5Q10CY_ACTIVE_REVIEW_FALLBACK_LAB',
        brand: {
          tenantName: activeDocumentReview?.tenantName || 'Wilsy OS Tenant',
          seal: 'Wilsy OS',
        },
        document: {
          title: activeDocumentReviewFields.title || activeDocumentReview?.title || 'Document draft',
          documentType: activeDocumentReviewFields['document type'] || activeDocumentReview?.documentType || 'Business document',
          status: activeDocumentReview?.status || 'Draft prepared',
          purpose: activeDocumentReviewFields.purpose || activeDocumentReview?.purpose || 'Prepared for governed review.',
          sections: [
            {
              title: 'Source and tenant branding',
              body: 'Wilsy stages this draft inside the AI lab so the operator can verify the tenant source, brand posture, and document purpose before any execution command.',
            },
            {
              title: 'Approval workflow',
              body: 'Send remains locked until recipient details, delivery connector binding, and approval are complete.',
            },
            {
              title: 'Execution readiness',
              body: 'Package and send stay locked until the operator completes approval and evidence requirements.',
            },
          ],
        },
      }
    : null);

  const { snapshot, localContext } = useWilsyWorkspaceContext();
  const { status, context, backendContext } = useWilsySovereignBrainContext(snapshot, localContext);
  const cards = useMemo(() => buildWilsyIntelligenceCards(context), [context]);
  const [dockState, setDockState] = useState(loadWilsyDockState);
















  /* WILSY_P60K5Q10CA_SPLIT_DOCK_EVENT_BRIDGE */
  useEffect(() => {
    if (typeof window === 'undefined') {
      return undefined;
    }

    /**
     * @function handleWilsyAISplitRuntimeOpenRequest
     * @description Opens the Wilsy OS Intelligence dock from the isolated compact launcher root while preserving dock size and document review state.
     * @returns {void} Opens the dock from the split runtime launcher event.
     * @collaboration WilsyOSIntelligenceLauncher, WilsyOSIntelligenceDockRuntime, WilsyOSIntelligenceDock, and tenant productivity shell.
     */
    function handleWilsyAISplitRuntimeOpenRequest() {
      setDockState((previousDockState) => {
        if (
          previousDockState &&
          typeof previousDockState === 'object' &&
          !Array.isArray(previousDockState)
        ) {
          return {
            ...previousDockState,
            isOpen: true,
            open: true,
            visible: true,
            expanded: true,
            
            collapsed: false,minimized: false,
            compact: false,
          };
        }

        if (typeof previousDockState === 'string') {
          return 'open';
        }

        return true;
      });
    }

    window.addEventListener('wilsy-os-intelligence-open-request', handleWilsyAISplitRuntimeOpenRequest);

    return () => {
      window.removeEventListener('wilsy-os-intelligence-open-request', handleWilsyAISplitRuntimeOpenRequest);
    };
  }, []);

  const [operatorPrompt, setOperatorPrompt] = useState('');
  const [operatorBackendBusy, setOperatorBackendBusy] = useState(false);
  const [operatorBackendError, setOperatorBackendError] = useState('');
  const [operatorBackendModel, setOperatorBackendModel] = useState(null);
  const [activePrompt, setActivePrompt] = useState('what_next');
  const [planCopied, setPlanCopied] = useState(false);
  const operatorModel = useMemo(
    () =>
      buildWilsyOperatorModelSurface({
        context,
        backendContext,
        cards,
        operatorPrompt,
        activePrompt,
      }),
    [context, backendContext, cards, operatorPrompt, activePrompt]
  );
  const liveOperatorModel = operatorBackendModel || operatorModel;
  const wilsyHasSubmittedOperatorResult = Boolean(operatorBackendBusy || operatorBackendModel);

  /**
   * @function updateDockState
   * @description Updates and persists the global Wilsy AI dock state.
   * @param {Object} nextState - Partial state update.
   * @returns {void}
   * @collaboration Wilsy AI sidecar controls, workspace visibility, and operator display preferences.
   */
  function updateDockState(nextState = {}) {
    setDockState((current) => {
      const merged = { ...current, ...nextState };
      saveWilsyDockState(merged);
      return merged;
    });
  }

  /**
   * @function handleWilsyAskSubmit
   * @description Sends the operator prompt to the backend Wilsy Operator Model and renders the live tool-backed answer.
   * @param {Event} event - Form submit event.
   * @returns {Promise<void>} Resolves after backend model answer is applied.
   * @collaboration Wilsy Operator Model backend, source-registry GET bridge, CRM source tools, and no-mutation governance boundary.
   */
  async function handleWilsyAskSubmit(event) {
    event.preventDefault();

    const question = operatorPrompt.trim();

    if (!question) {
      return;
    }

    setActivePrompt(resolveWilsyOperatorIntent(question, activePrompt));
    setOperatorBackendBusy(true);
    setOperatorBackendError('');

    try {
      const response = await fetch(buildWilsyOperatorAskUrl(question, snapshot, context), {
        method: 'GET',
        headers: {
          Accept: 'application/json',
          'X-Tenant-Id': window.localStorage?.getItem('wilsy-tenant-id') || 'MASTER',
          'X-Operator-Id': window.localStorage?.getItem('wilsy-operator-id') || 'WILSY_OPERATOR',
          'X-Wilsy-Command-Surface': 'WILSY_OS_OPERATOR_MODEL',
        },
      });

      const payload = await parseWilsyOperatorJsonResponse(response);

      if (!response.ok || payload?.error) {
        throw new Error(payload?.error?.message || payload?.message || 'Wilsy Operator Model could not answer yet.');
      }

      if (payload?.operatorModel) {
        setOperatorBackendModel(normalizeWilsyFoundryModelForDisplay(payload.operatorModel));
      } else {
        throw new Error('Wilsy Operator Model returned no operatorModel payload.');
      }
    } catch (error) {
      const message = error?.message || 'Wilsy Operator Kernel could not answer yet.';
      setOperatorBackendModel(normalizeWilsyFoundryModelForDisplay({
        intent: 'operator_kernel_error',
        domain: null,
        supported: false,
        title: 'Workspace source needs attention',
        answer: message,
        outcome: 'Checked: workspace source · Needs attention · Next: reconnect source',
        progress: 'Kernel error',
        quickPrompts: liveOperatorModel?.quickPrompts || [],
        actions: [
          {
            rank: 1,
            title: 'Repair failed tool response',
            description: message,
            mode: 'read_only',
            mutation: false,
          },
        ],
        checklist: [
          'Verify the endpoint returned JSON.',
          'Confirm the tool exists in the Operator Kernel registry.',
          'Confirm the source is bound for the tenant.',
        ],
        commandPlan: [
          `Question: ${operatorPrompt}`,
          `Error: ${message}`,
          'Mutation: none. No fake command prepared.',
        ],
        sourceTrace: [
          {
            tool: 'workspace_source',
            domain: null,
            status: 'FAILED',
            count: null,
            collectionsChecked: [],
            message,
          },
        ],
      }));
      setOperatorBackendError('');
    } finally {
      setOperatorBackendBusy(false);
    }
  }

  /**
   * @function handleWilsyQuickPrompt
   * @description Runs a workspace quick prompt through the Wilsy Operator Model.
   * @param {Object} prompt - Quick prompt descriptor.
   * @returns {void}
   * @collaboration Operator quick prompts, CRM Setup authority guidance, evidence checklist, and release readiness workflow.
   */
  function handleWilsyQuickPrompt(prompt = {}) {
    const promptLabel = String(prompt.label || prompt.title || prompt.prompt || prompt.description || '').trim();
    const nextPromptId = prompt.intent || prompt.id || resolveWilsyOperatorIntent(promptLabel, activePrompt) || 'what_next';

    if (!promptLabel) {
      return;
    }

    const intelligenceModel = buildWilsyOperatorIntelligence({
      promptText: promptLabel,
      context,
      baseModel: operatorModel,
      liveModel: liveOperatorModel,
      forcedIntent: nextPromptId,
      resolveIntent: resolveWilsyOperatorIntent,
    });

    setActivePrompt(nextPromptId);
    setOperatorPrompt(promptLabel);
    setOperatorBackendModel(normalizeWilsyFoundryModelForDisplay(intelligenceModel));
    setOperatorBackendBusy(false);
    setOperatorBackendError('');
    setPlanCopied(false);
  }

  /**
   * @function handleCopyWilsyCommandPlan
   * @description Copies the current governed command preparation plan for operator review.
   * @returns {Promise<void>} Resolves after clipboard copy attempt.
   * @collaboration Wilsy AI operator model, no-mutation command preparation, and human approval handoff.
   */
  async function handleCopyWilsyCommandPlan() {
    const plan = (liveOperatorModel.commandPlan || []).join('\n');

    try {
      if (navigator?.clipboard?.writeText) {
        await navigator.clipboard.writeText(plan);
      }

      setPlanCopied(true);
      window.setTimeout(() => setPlanCopied(false), 1600);
    } catch (error) {
      setPlanCopied(false);
    }
  }

  const dockClassName = [
    styles.dock,
    dockState.collapsed ? styles.collapsed : '',
    dockState.focusMode ? styles.focusMode : '',
  ]
    .filter(Boolean)
    .join(' ');

  return (
    <aside className={dockClassName} aria-label="Wilsy OS adaptive intelligence dock">
      <section className={styles.shell}>
        <header className={styles.header}>
          <div>
            <p>WILSY OS OPERATOR MODEL · LIVE WORKSPACE</p>
            <h3>{context.workspace} · Productivity Copilot</h3>
          </div>
          <div className={styles.actions}>
            <button
              type="button"
              onClick={() => updateDockState({ focusMode: !dockState.focusMode })}
              aria-pressed={dockState.focusMode}
            >
              {dockState.focusMode ? 'Full size' : 'Compact'}
            </button>
            <button type="button" onClick={handleCopyWilsyCommandPlan}>
              {planCopied ? 'Copied' : 'Copy plan'}
            </button>
            <button type="button" onClick={() => updateDockState({ collapsed: true })}>
              Close
            </button>
          </div>
        </header>

        <div className={styles.contextStrip}>
          <span>{context.focus}</span>
          <strong>{context.role}</strong>
        </div>

        <div className={styles.body}>
          <section className={styles.operatorWorkbench}>
            <form className={styles.askBar} onSubmit={handleWilsyAskSubmit}>
              <input
                type="text"
                value={operatorPrompt}
                onChange={(event) => setOperatorPrompt(event.target.value)}
                placeholder={`Ask Wilsy about ${context.workspace || 'this workspace'}...`}
                aria-label="Ask Wilsy"
              />
              <button type="submit">{operatorBackendBusy ? 'Checking' : 'Ask'}</button>
            </form>

                        {/* WILSY_P60K5Q10BR_ANSWER_FIRST_LAYOUT */}
<div className={`${styles.answerWorkspace} ${!wilsyHasSubmittedOperatorResult || activeDocumentReview ? styles.operatingStateHidden : ''}`}>
              <span>WILSY ANSWER</span>
              <strong>{operatorBackendBusy ? 'Checking live Wilsy sources' : getWilsyDisplayTitle(liveOperatorModel)}</strong>
              <p>{operatorBackendBusy ? 'I am checking connected CRM sources and evidence before answering.' : getWilsyDisplayAnswer(liveOperatorModel)}</p>
              <small>{getWilsyDisplayOutcome(liveOperatorModel)}</small>
              {liveOperatorModel.missionState ? (
                <div className={styles.missionStatePanel} data-wilsy-mission-state="active">
                  <div className={styles.missionStateHeader}>
                    <span>ACTIVE MISSION</span>
                    <strong>{liveOperatorModel.missionState.objective}</strong>
                  </div>
                  <div className={styles.missionStateGrid}>
                    {(liveOperatorModel.missionGates || liveOperatorModel.missionState.gates || []).slice(0, 4).map((gate, index) => (
                      <span key={`${gate}-${index}`}>{gate}</span>
                    ))}
                  </div>
                </div>
              ) : null}
              {operatorBackendBusy ? <em className={styles.operatorProgress}>Live source search in progress...</em> : null}
              {operatorBackendError ? <em className={styles.operatorError}>{operatorBackendError}</em> : null}
              {/* WILSY_P60K5Q10AY_FOUNDRY_SINGLE_CARD */}
              {(() => {
                const capabilityItem = buildWilsyCapabilityReviewItem(liveOperatorModel);

                return capabilityItem ? (
                  <div className={styles.capabilityReviewCard}>
                    <div className={styles.capabilityReviewHeader}>
                      <span>CAPABILITY FOUNDRY</span>
                      <strong>REVIEW REQUIRED</strong>
                    </div>

                    <div className={styles.capabilityReviewGrid}>
                      <span>
                        <small>Capability</small>
                        <strong>{capabilityItem.businessName}</strong>
                      </span>
                      <span>
                        <small>Candidate</small>
                        <strong>{capabilityItem.candidateId}</strong>
                      </span>
                      <span>
                        <small>Status</small>
                        <strong>{String(capabilityItem.status || '').replaceAll('_', ' ')}</strong>
                      </span>
                      <span>
                        <small>Approval</small>
                        <strong>{capabilityItem.approvalRequired ? 'Required before publishing' : 'Not required'}</strong>
                      </span>
                    </div>

                    {/* WILSY_P60K5Q10AZ_FOUNDRY_DECISION_STRIP */}
                    <div className={styles.capabilityReviewDecision}>
                      <small>Next decision</small>
                      <strong>{capabilityItem.nextDecision}</strong>
                    </div>

                    <div className={styles.capabilityReviewActions}>
                      <button
                        type="button"
                        onClick={() => {
                          if (typeof navigator !== 'undefined' && navigator.clipboard) {
                            navigator.clipboard.writeText(capabilityItem.planText);
                          }
                        }}
                      >
                        Copy foundry plan
                      </button>
                    </div>
                  </div>
                ) : null;
              })()}



              {Array.isArray(liveOperatorModel.sourceTrace) && liveOperatorModel.sourceTrace.length > 0 ? (
                <div className={styles.sourceTrace}>
                  {liveOperatorModel.sourceTrace.map((trace) => (
                    <span key={`${trace.tool}-${trace.domain || 'none'}-${trace.status}`}>
                      Checked: {trace.label || 'Operator source'} · {trace.statusLabel || 'Completed'}
                    </span>
                  ))}
                </div>
              ) : null}
            </div>

            {/* WILSY_P60K5Q10AU_PREPARED_WORK_RENDER */}
            {(() => {
              const preparedItem = buildWilsyPreparedOperatorItem(liveOperatorModel);

              return preparedItem ? (
                <div className={`${styles.preparedWorkCard} ${!wilsyHasSubmittedOperatorResult || activeDocumentReview ? styles.operatingStateHidden : ''}`}>
                  <div className={styles.preparedWorkHeader}>
                    <span>PREPARED WORK</span>
                    <strong>{preparedItem.status}</strong>
                  </div>

                  <div className={styles.preparedWorkGrid}>
                    {preparedItem.fields.map((field) => (
                      <span key={`${field.label}-${field.value}`}>
                        <small>{field.label}</small>
                        <strong>{field.value}</strong>
                      </span>
                    ))}
                  </div>

                  <div className={styles.preparedWorkActions}>
                    {preparedItem.link ? (
                      <button
                        type="button"
                        data-wilsy-document-review-action="open-lab"
                        onClick={(event) => {
                          event.preventDefault();
                          event.stopPropagation();

                          const preparedFieldMap = Array.isArray(preparedItem.fields)
                            ? preparedItem.fields.reduce((accumulator, field) => {
                                accumulator[String(field.label || '').toLowerCase()] = field.value;
                                return accumulator;
                              }, {})
                            : {};

                          const reviewLabItem = {
                            ...preparedItem,
                            documentPreview:
                              preparedItem.documentPreview ||
                              liveOperatorModel?.documentPreview ||
                              {
                                previewVersion: 'P60K5Q10DA_EXACT_REVIEW_DRAFT_LAB',
                                brand: {
                                  tenantName: liveOperatorModel?.tenantName || 'Wilsy OS Tenant',
                                  seal: 'Wilsy OS',
                                },
                                document: {
                                  title: preparedFieldMap.title || preparedItem.title || 'Document draft',
                                  documentType:
                                    preparedFieldMap['document type'] ||
                                    preparedItem.documentType ||
                                    'Business document',
                                  status: preparedItem.status || 'Draft prepared',
                                  purpose:
                                    preparedFieldMap.purpose ||
                                    preparedItem.purpose ||
                                    'Prepared for governed review.',
                                  sections: [
                                    {
                                      sectionId: 'source-and-branding',
                                      heading: 'Source and tenant branding',
                                      body: 'Wilsy keeps this review inside the AI lab so the operator can verify tenant source, brand posture, and document purpose before execution.',
                                    },
                                    {
                                      sectionId: 'approval-workflow',
                                      heading: 'Approval workflow',
                                      body: 'Send for approval is the next governed action. Mutation remains locked until approval is complete.',
                                    },
                                    {
                                      sectionId: 'delivery-readiness',
                                      heading: 'Delivery readiness',
                                      body: 'Recipient details, delivery connector binding, and approval must be complete before package or send can unlock.',
                                    },
                                  ],
                                },
                              },
                            planText:
                              preparedItem.planText ||
                              (Array.isArray(liveOperatorModel?.commandPlan) ? liveOperatorModel.commandPlan.join('\\n') : '') ||
                              'Review draft\\nConfirm tenant branding\\nSend for approval\\nApprove governed command\\nPackage receipt',
                            labState: {
                              reviewOpen: true,
                              mutation: false,
                              sendLocked: true,
                              sourceChecked: true,
                              approvalStatus: 'Approval required',
                              deliveryStatus: 'Recipient and connector required',
                            },
                          };

                          setActiveDocumentReview(reviewLabItem);

                          if (typeof window !== 'undefined' && typeof document !== 'undefined') {
                            window.requestAnimationFrame(() => {
                              document
                                .querySelector('[data-wilsy-document-lab="active"]')
                                ?.scrollIntoView({ behavior: 'smooth', block: 'start' });
                            });

                            window.setTimeout(() => {
                              document
                                .querySelector('[data-wilsy-document-lab="active"]')
                                ?.scrollIntoView({ behavior: 'smooth', block: 'start' });
                            }, 160);
                          }
                        }}
                      >
                        {preparedItem.linkLabel || 'Review Draft'}
                      </button>
                    ) : null}
                    <button
                      type="button"
                      onClick={() => {
                        if (typeof navigator !== 'undefined' && navigator.clipboard) {
                          navigator.clipboard.writeText(preparedItem.planText);
                        }
                      }}
                    >
                      Copy approval plan
                    </button>
                  </div>
                </div>
              ) : null;
            })()}

            {/* WILSY_P60K5Q10BE_DOCUMENT_PREVIEW_PANEL */}
            {activeDocumentReview ? (
<section className={styles.documentPreviewPanel} data-wilsy-document-lab="active" aria-label="Tenant-branded document review">
                <div className={styles.documentPreviewHeader}>
                  <span>TENANT DOCUMENT REVIEW</span>
                  <strong>{activeDocumentReviewPreview?.document?.title || activeDocumentReview.fields?.[0]?.value || 'Document draft'}</strong>
                  <button type="button" onClick={() => setActiveDocumentReview(null)}>
                    Close review
                  </button>
                </div>

                  {/* WILSY_P60K5Q10DD_TASK_FIRST_CONTROL_DECK */}
                  <div className={styles.documentTaskControlDeck} aria-label="Document task control deck">
                    <div className={styles.documentTaskNextAction}>
                      <span>NEXT TASK</span>
                      <strong>Complete approval readiness</strong>
                      <small>Recipient, connector, and authorized approval must unlock before package or send.</small>
                    </div>

                    <div className={styles.documentTaskGateMatrix} aria-label="Document execution gates">
                      <span data-gate-state="checked">Source checked</span>
                      <span data-gate-state="blocked">Recipient missing</span>
                      <span data-gate-state="blocked">Connector missing</span>
                      <span data-gate-state="blocked">Approval required</span>
                    </div>

                    <div className={styles.documentTaskActions}>
                      <button type="button" disabled title="Recipient and connector are required first.">
                        Send for approval
                      </button>
                      <button type="button" disabled title="Approval readiness is required before packaging.">
                        Package
                      </button>
                      <button
                        type="button"
                        onClick={() => {
                          if (typeof navigator !== 'undefined' && navigator.clipboard) {
                            navigator.clipboard.writeText(activeDocumentReview.planText || '');
                          }
                        }}
                      >
                        Copy plan
                      </button>
                    </div>
                  </div>


                
                  {/* WILSY_P60K5Q10DE_ACTUAL_DOCUMENT_CANVAS */}
                  {(() => {
                    const documentModel = activeDocumentReviewPreview?.document || {};
                    const documentTitle =
                      documentModel.title ||
                      activeDocumentReview?.fields?.find((field) => field.label === 'Title')?.value ||
                      activeDocumentReview?.title ||
                      'Document draft';
                    const documentType =
                      documentModel.documentType ||
                      activeDocumentReview?.fields?.find((field) => field.label === 'Document type')?.value ||
                      activeDocumentReview?.documentType ||
                      'Business document';
                    const documentPurpose =
                      documentModel.purpose ||
                      activeDocumentReview?.fields?.find((field) => field.label === 'Purpose')?.value ||
                      activeDocumentReview?.purpose ||
                      'Prepared for governed review.';
                    const sourceSections = Array.isArray(documentModel.sections) ? documentModel.sections : [];
                    const presentationSectionPattern = /source and tenant branding|approval workflow|delivery readiness|execution readiness/i;
                    const hasActualDraftBody = sourceSections.some(
                      (section) =>
                        !presentationSectionPattern.test(String(section.heading || section.title || section.sectionId || '')),
                    );
                    const draftBodySections = hasActualDraftBody
                      ? sourceSections
                      : [
                          {
                            sectionId: 'opening-brief',
                            heading: '1. Operating brief',
                            body: `${documentTitle} is prepared for review under Wilsy OS governance. The purpose of this draft is: ${documentPurpose}`,
                          },
                          {
                            sectionId: 'scope-of-document',
                            heading: '2. Scope',
                            body: `This ${documentType} records the proposed business intent, review requirements, approval posture, and delivery controls required before execution.`,
                          },
                          {
                            sectionId: 'review-obligations',
                            heading: '3. Review obligations',
                            body: 'The operator must verify the content, tenant branding, source posture, recipient readiness, delivery connector, and approval path before any send command can unlock.',
                          },
                          {
                            sectionId: 'execution-control',
                            heading: '4. Execution control',
                            body: 'No delivery mutation has been taken. Packaging and sending remain locked until recipient details, connector binding, and authorized approval are complete.',
                          },
                        ];

                    return (
                      <section className={styles.documentActualCanvas} aria-label="Actual document draft canvas">
                        <div className={styles.documentCanvasGameHud} aria-label="Draft progress">
                          <span data-stage-state="complete">Draft visible</span>
                          <span data-stage-state="active">Review now</span>
                          <span data-stage-state="locked">Approval locked</span>
                          <span data-stage-state="locked">Send locked</span>
                        </div>

                        <article className={styles.documentPageSurface}>
                          <header className={styles.documentPageMasthead}>
                            <span>{activeDocumentReviewPreview?.brand?.tenantName || 'Wilsy OS Tenant'}</span>
                            <strong>{documentTitle}</strong>
                            <small>{documentType} · {documentModel.status || activeDocumentReview?.status || 'Draft prepared'}</small>
                          </header>

                          <section className={styles.documentPagePurpose}>
                            <span>Purpose</span>
                            <p>{documentPurpose}</p>
                          </section>

                          <div className={styles.documentDraftBody}>
                            {draftBodySections.map((section, sectionIndex) => (
                              <section
                                key={section.sectionId || section.heading || section.title || `draft-section-${sectionIndex}`}
                                className={styles.documentDraftClause}
                              >
                                <span>{String(section.sectionId || `clause-${sectionIndex + 1}`).replace(/[-_]/g, ' ')}</span>
                                <strong>{section.heading || section.title || `Section ${sectionIndex + 1}`}</strong>
                                <p>{section.body || section.content || 'Draft content pending review.'}</p>
                              </section>
                            ))}
                          </div>

                          <footer className={styles.documentPageSignatureRail}>
                            <div>
                              <span>Prepared by</span>
                              <strong>Wilsy OS AI</strong>
                            </div>
                            <div>
                              <span>Mutation</span>
                              <strong>Locked</strong>
                            </div>
                            <div>
                              <span>Next move</span>
                              <strong>Review content</strong>
                            </div>
                          </footer>
                        </article>
                      </section>
                    );
                  })()}

{/* WILSY_P60K5Q10DD_EVIDENCE_DETAILS */}
                  <details className={styles.documentTaskEvidenceDetails}>
                    <summary>Evidence, source, and delivery constraints</summary>
                    <div className={styles.documentPreviewBrand}>
                  <span>{activeDocumentReviewPreview?.brand?.tenantName || 'Wilsy OS Tenant'}</span>
                  <strong>{activeDocumentReviewPreview?.document?.status || 'Draft ready for review'}</strong>
                </div>

                <div className={styles.documentPreviewSections}>
                  {(activeDocumentReviewPreview?.document?.sections || []).map((section) => (
                    <article key={section.sectionId}>
                      <h4>{section.heading}</h4>
                      <p>{section.body}</p>
                    </article>
                  ))}
                </div>
                  </details>

<div className={styles.documentPreviewFooter}>
                    <span>LOCKED: recipient missing · connector missing · approval required</span>
                  </div>
              </section>
            ) : null}

            {!activeDocumentReview && (liveOperatorModel.playableActions || liveOperatorModel.actions || []).length > 0 ? (
              <div className={styles.playableActionDeck} data-wilsy-visible-playable-action-rail="true">
                <div className={styles.playableActionHeader}>
                  <span>PLAYABLE ACTION RAIL</span>
                  <strong>Choose the next safe move</strong>
                </div>
                <div className={styles.playableActionGrid}>
                  {(liveOperatorModel.playableActions || liveOperatorModel.actions || []).slice(0, 4).map((action, index) => (
                    <button
                      key={action.id || action.title || index}
                      type="button"
                      className={styles.playableActionButton}
                      onClick={() =>
                        handleWilsyQuickPrompt({
                          id: action.intent || resolveWilsyOperatorIntent(action.prompt || action.title, activePrompt),
                          intent: action.intent || resolveWilsyOperatorIntent(action.prompt || action.title, activePrompt),
                          label: action.buttonLabel || action.title,
                          prompt: action.prompt || action.title,
                          description: action.description,
                        })
                      }
                    >
                      <span>{action.buttonLabel || action.title}</span>
                      <small>{action.nextState || action.lockedReason || action.description || 'Read-only governed move'}</small>
                    </button>
                  ))}
                </div>
              </div>
            ) : null}

            <div className={`${styles.promptGrid} ${activeDocumentReview ? styles.operatingStateHidden : ''} `} aria-label="Wilsy quick prompts">
              {liveOperatorModel.quickPrompts.map((prompt) => (
                <button
                  key={prompt.id}
                  type="button"
                  className={activePrompt === prompt.id ? styles.activePrompt : ''}
                  onClick={() => handleWilsyQuickPrompt(prompt)}
                >
                  {prompt.label}
                </button>
              ))}
            </div>
          </section>

          <section className={`${styles.actionBoard} ${activeDocumentReview ? styles.operatingStateHidden : ''} `}>
            <div className={styles.sectionHeader}>
              <span>PLAYABLE ACTION RAIL</span>
              <strong>Play the next safe move</strong>
            </div>
            <div className={styles.actionList}>
              {liveOperatorModel.actions.map((action) => (
                <button
                  key={`${action.rank}-${action.title}`}
                  type="button"
                  onClick={() =>
                    handleWilsyQuickPrompt({
                      id: action.rank === 1 ? 'authority_graph' : action.rank === 2 ? 'evidence_checklist' : 'queue_hygiene',
                      label: action.buttonLabel || action.title,
                        prompt: action.prompt || action.title,
                        intent: action.intent,
                    })
                  }
                >
                  <span>{String(action.mode || 'read_only').replace(/_/g, ' ')}</span>
                  <strong>{action.title}</strong>
                  <p>{action.description}</p>
                </button>
              ))}
            </div>
          </section>

          <section className={`${styles.commandPrep} ${activeDocumentReview ? styles.operatingStateHidden : ''} `}>
            <div className={styles.sectionHeader}>
              <span>GOVERNED COMMAND PREP</span>
              <strong>Ready for operator review</strong>
            </div>
            <ol>
              {liveOperatorModel.checklist.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ol>
            <p>No workspace data changes here. Wilsy prepares the work; execution still requires an approved command.</p>
          </section>

          <details className={styles.modelDetails}>
            <summary>Model coverage</summary>
            <div>
              <span>Workspace: {context.workspace}</span>
              <span>Role: {context.role}</span>
              <span>Focus: {context.focus}</span>
              <span>Status: {status === 'SOVEREIGN_CONTEXT' ? 'Live context connected' : 'Local context only'}</span>
            </div>
          </details>
        </div>
      </section>

      
    </aside>
  );
}

/**
 * @function mountWilsyOSIntelligenceDock
 * @description Mounts the global Wilsy OS Intelligence dock once at app runtime.
 * @returns {HTMLElement|null} Dock host element when mounted.
 * @collaboration React root runtime, all Wilsy OS workspaces, global intelligence sidecar, and future billing-tier intelligence services.
 */
export function mountWilsyOSIntelligenceDock() {
  if (typeof document === 'undefined') {
    return null;
  }

  let host = document.getElementById(WILSY_INTELLIGENCE_ROOT_ID);

  if (!host) {
    host = document.createElement('div');
    host.id = WILSY_INTELLIGENCE_ROOT_ID;
    document.body.appendChild(host);
  }

  if (host.dataset.wilsyMounted === 'true') {
    return host;
  }

  const root = createRoot(host);
  root.render(<WilsyOSIntelligenceDock />);
  host.dataset.wilsyMounted = 'true';
  window.__WILSY_OS_INTELLIGENCE_DOCK_ROOT__ = root;

  return host;
}

export default WilsyOSIntelligenceDock;
