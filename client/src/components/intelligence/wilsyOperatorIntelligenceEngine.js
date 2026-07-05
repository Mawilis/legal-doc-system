/* eslint-disable */

/**
 * @function resolveWilsyCoreIntent
 * @description Resolves the operator intent from prompt text and selected quick-prompt metadata.
 * @param {string} promptText - Prompt text.
 * @param {string} forcedIntent - Optional selected quick-prompt intent.
 * @returns {string} Wilsy operator intent.
 * @collaboration Wilsy AI Core Engine, quick prompts, Ask composer, CRM Setup, Billing, evidence workflows, and gameplay-like task routing.
 */
export function resolveWilsyCoreIntent(promptText = '', forcedIntent = '') {
  const prompt = String(promptText || '').toLowerCase();

  if (forcedIntent) {
    return forcedIntent;
  }

  if (prompt.includes('authority graph') || prompt.includes('authority')) {
    return 'authority_graph';
  }

  if (prompt.includes('release') || prompt.includes('readiness')) {
    return 'release_readiness';
  }

  if (prompt.includes('evidence') || prompt.includes('checklist')) {
    return 'evidence_checklist';
  }

  if (prompt.includes('queue') || prompt.includes('hygiene')) {
    return 'queue_hygiene';
  }

  if (prompt.includes('package') || prompt.includes('workflow')) {
    return 'workflow_packaging';
  }

  if (prompt.includes('document') || prompt.includes('draft')) {
    return 'document_review';
  }

  return 'what_next';
}

/**
 * @function resolveWilsyCoreWorkspace
 * @description Builds a durable workspace profile from the visible dock context and current operator model.
 * @param {Object} context - Current dock context.
 * @param {Object} model - Existing model.
 * @param {string} promptText - Prompt text.
 * @returns {Object} Workspace profile for intelligence generation.
 * @collaboration Wilsy AI Core Engine, Billing, CRM Setup, Meetings, document workflows, and tenant operating posture.
 */
export function resolveWilsyCoreWorkspace(context = {}, model = {}, promptText = '') {
  const prompt = String(promptText || '').toLowerCase();
  const workspaceName = context?.workspace || model?.workspace || model?.domain || 'Wilsy OS';
  const focus = context?.focus || model?.focus || 'current workspace';
  const role = context?.role || model?.role || 'Operator';
  const haystack = `${workspaceName} ${focus} ${role} ${prompt}`.toLowerCase();

  if (
    haystack.includes('billing') ||
    haystack.includes('invoice') ||
    haystack.includes('payment') ||
    haystack.includes('revenue')
  ) {
    return {
      workspace: 'Billing',
      focus: 'Revenue Assurance',
      role: role || 'Finance Operator',
      domain: 'billing',
      playableGoal: 'protect revenue, prove billing changes, and prevent unauthorized billing-state mutation',
      lockedMutation: 'billing-state changes, entitlement updates, credits, refunds, and invoice release',
    };
  }

  if (
    haystack.includes('crm setup') ||
    haystack.includes('authority graph') ||
    haystack.includes('setup') ||
    haystack.includes('release')
  ) {
    return {
      workspace: 'CRM Setup',
      focus: 'Authority Graph',
      role: role || 'Security Admin',
      domain: 'crm_setup',
      playableGoal: 'protect setup authority, approval readiness, release gates, and evidence posture',
      lockedMutation: 'release, approval, packet mutation, and setup-control changes',
    };
  }

  if (haystack.includes('meeting') || haystack.includes('manifest') || haystack.includes('import ledger')) {
    return {
      workspace: 'CRM Meetings',
      focus: 'Meetings Operating Cockpit',
      role: role || 'CRM Operator',
      domain: 'meetings',
      playableGoal: 'protect sync freshness, meeting evidence, import receipts, and capsule integrity',
      lockedMutation: 'record mutation, import acceptance, and evidence promotion',
    };
  }

  if (haystack.includes('document') || haystack.includes('draft')) {
    return {
      workspace: 'Documents',
      focus: 'Document Command Lab',
      role: role || 'Document Operator',
      domain: 'documents',
      playableGoal: 'review draft content, source posture, approval gates, and delivery readiness',
      lockedMutation: 'send, package, recipient delivery, and approval release',
    };
  }

  return {
    workspace: workspaceName,
    focus,
    role,
    domain: 'workspace',
    playableGoal: 'turn the visible screen into safe next actions with evidence',
    lockedMutation: 'any governed mutation until approval and proof are present',
  };
}

/**
 * @function buildWilsyCoreChecklist
 * @description Builds workspace-specific checks used by the AI response and command plan.
 * @param {Object} profile - Workspace profile.
 * @param {string} intent - Resolved intent.
 * @returns {Array<string>} Operator checklist.
 * @collaboration Wilsy AI Core Engine, evidence contract, governed command plan, and tenant productivity workflows.
 */
export function buildWilsyCoreChecklist(profile = {}, intent = 'what_next') {
  if (profile.domain === 'billing') {
    if (intent === 'authority_graph') {
      return [
        'Confirm who may view billing posture and who may prepare billing evidence.',
        'Separate inspection rights from approval rights for payment, entitlement, refund, and credit changes.',
        'Keep invoice release locked until approval owner and receipt trail are present.',
        'Record tenant identity, operator identity, timestamp, and command surface before any billing mutation.',
      ];
    }

    if (intent === 'release_readiness') {
      return [
        'Match invoice totals to payment status and receipt evidence.',
        'Confirm tenant entitlement and current plan limits.',
        'Verify approval owner for credits, refunds, failed payments, and release.',
        'Hold release if payment, entitlement, approval, or receipt proof is missing.',
      ];
    }

    if (intent === 'evidence_checklist') {
      return [
        'Invoice ID, tenant identity, operator identity, timestamp, and billing command surface.',
        'Payment status, receipt trail, failed-payment reason, and ledger posture.',
        'Plan entitlement, approval owner, credit/refund reason, and release gate.',
        'No mutation until all evidence is attached to the governed command.',
      ];
    }

    return [
      'Inspect open invoices, unpaid receipts, failed payments, and revenue leakage.',
      'Verify tenant plan limits, entitlement changes, refunds, credits, and approval owner.',
      'Collect tenant identity, operator identity, payment status, receipt trail, and timestamp evidence.',
      'Do not change billing state until approval and receipt proof are ready.',
    ];
  }

  if (profile.domain === 'crm_setup') {
    return [
      'Verify operator role, authority boundary, and command surface.',
      'Check staged proof, approval path, release readiness, and packet integrity.',
      'Collect evidence receipts and queue hygiene signals.',
      'Do not mutate setup data until a governed command is approved.',
    ];
  }

  if (profile.domain === 'documents') {
    return [
      'Open the actual draft canvas before showing source or evidence panels.',
      'Verify document source, tenant branding, recipient readiness, connector readiness, and approval gate.',
      'Keep package and send locked until approval and delivery evidence are complete.',
      'Record the review action as a governed evidence event.',
    ];
  }

  return [
    'Read the current workspace context and operator role.',
    'Identify the next safe action and what evidence is missing.',
    'Keep mutation locked until approval and proof are present.',
    'Return a playable next move instead of a static status card.',
  ];
}

/**
 * @function buildWilsyCoreAnswerMap
 * @description Builds useful answers for known operator intents in the active workspace.
 * @param {Object} profile - Workspace profile.
 * @param {string} promptText - Original prompt.
 * @returns {Object} Intent answer map.
 * @collaboration Wilsy AI Core Engine, operator conversation, authority graph, release readiness, evidence checklist, queue hygiene, and workflow packaging.
 */
export function buildWilsyCoreAnswerMap(profile = {}, promptText = '') {
  if (profile.domain === 'billing') {
    return {
      what_next: {
        title: 'Next move in Billing',
        answer:
          'Start with revenue assurance. Check open invoices, failed payments, plan limits, missing receipts, credits, refunds, and entitlement mismatches. Then choose the next governed move: collect evidence, escalate approval, or package a billing workflow. Do not change billing state until approval and receipt proof are ready.',
        outcome: 'Billing next move prepared: inspect exceptions, prove evidence, then escalate only if needed.',
      },
      release_readiness: {
        title: 'Billing release readiness',
        answer:
          'Billing is release-ready only when invoice totals, payment status, tenant entitlement, approval authority, and receipt evidence all match. If one of those is missing, hold release and prepare an evidence checklist instead.',
        outcome: 'Billing release converted into a governed readiness checklist.',
      },
      authority_graph: {
        title: 'Billing authority graph',
        answer:
          'In Billing, the authority graph shows who may view billing posture, prepare evidence, approve changes, and release billing-state updates. Finance Operator may inspect revenue assurance and prepare proof. Payment changes, entitlement changes, credits, refunds, and invoice release stay locked until an authorized approval path is present.',
        outcome: 'Billing authority translated into safe next actions.',
      },
      evidence_checklist: {
        title: 'Billing evidence checklist',
        answer:
          'Collect invoice ID, tenant identity, operator identity, payment status, plan entitlement, failed-payment reason, receipt trail, approval owner, command surface, and timestamp before any billing command is prepared.',
        outcome: 'Billing evidence checklist ready for governed review.',
      },
      queue_hygiene: {
        title: 'Billing queue hygiene',
        answer:
          'Inspect billing items for stale unpaid invoices, repeated payment failures, missing receipts, entitlement mismatches, unresolved refunds or credits, and blocked approvals. Clear proof gaps before adding new billing work.',
        outcome: 'Billing blockers identified before new work enters the lane.',
      },
      workflow_packaging: {
        title: 'Package billing workflow',
        answer:
          'Package this as a Billing Revenue Assurance workflow: detect exceptions, collect evidence, verify authority, prepare approval, and only then release a billing-state command. This becomes a tenant-facing productivity tier because it reduces revenue leakage and approval risk.',
        outcome: 'Billing workflow package prepared.',
      },
    };
  }

  if (profile.domain === 'crm_setup') {
    return {
      what_next: {
        title: 'Next move in CRM Setup',
        answer:
          'Start with authority and evidence. Confirm the operator has the right control path, then check staged proof, approval state, release readiness, and queue hygiene before moving work forward.',
        outcome: 'Setup next move prepared: authority, evidence, approval, release readiness.',
      },
      release_readiness: {
        title: 'Release readiness check',
        answer:
          'Before release, verify staged review proof, approval state, release permission, packet integrity, and receipt trail. Do not use a release command until all five checks are clear.',
        outcome: 'Release decision converted into a governed checklist.',
      },
      authority_graph: {
        title: 'Authority graph interpretation',
        answer:
          'The authority graph shows who can review, who can approve, who can release, and what evidence each step requires. Use it as the permission map before any setup control changes state.',
        outcome: 'Every action mapped to authority before execution.',
      },
      evidence_checklist: {
        title: 'Evidence checklist',
        answer:
          'Collect staged review proof, packet status, approval receipt, release readiness, operator identity, tenant identity, and command-surface evidence before any governed command.',
        outcome: 'Evidence checklist ready for operator review.',
      },
      queue_hygiene: {
        title: 'Queue hygiene review',
        answer:
          'Inspect setup reviews for stale status, missing receipts, repeated pending states, orphaned approvals, and release blockers. Prioritize items with proof gaps first.',
        outcome: 'Queue blockers identified before new setup work enters the lane.',
      },
      workflow_packaging: {
        title: 'Tenant value packaging',
        answer:
          'Package this as governance guidance: authority checks, release readiness, evidence checklist, and queue hygiene. That is billable productivity because it reduces approval risk and saves operator time.',
        outcome: 'Tenant governance workflow package prepared.',
      },
    };
  }

  return {
    what_next: {
      title: `Next move in ${profile.workspace || 'Wilsy OS'}`,
      answer:
        'Read the visible workspace, identify the next safe action, list missing evidence, and keep mutation locked until approval and proof are present. The first useful move is to inspect the current task, verify authority, then prepare an evidence-backed command plan.',
      outcome: 'Workspace next move prepared.',
    },
  };
}

/**
 * @function buildWilsyOperatorIntelligence
 * @description Produces an immediate Wilsy AI operator model response using workspace reasoning before backend tools are needed.
 * @param {Object} input - Intelligence input.
 * @param {string} input.promptText - Prompt text.
 * @param {Object} input.context - Current dock context.
 * @param {Object} input.baseModel - Local model.
 * @param {Object} input.liveModel - Current live model.
 * @param {string} input.forcedIntent - Optional quick-prompt intent.
 * @param {Function} input.resolveIntent - Existing dock intent resolver.
 * @returns {Object|null} Operator model response.
 * @collaboration Wilsy OS AI Core Engine, Billing, CRM Setup, documents, evidence, authority, command plan, and governed execution.
 */
export function buildWilsyOperatorIntelligence({
  promptText = '',
  context = {},
  baseModel = {},
  liveModel = {},
  forcedIntent = '',
  resolveIntent = null,
} = {}) {
  const promptValue = String(promptText || '').trim();

  if (!promptValue) {
    return null;
  }

  const profile = resolveWilsyCoreWorkspace(context, baseModel, promptValue);
  const intent = resolveWilsyCoreIntent(
    promptValue,
    forcedIntent || (typeof resolveIntent === 'function' ? resolveIntent(promptValue, baseModel?.intent || 'what_next') : ''),
  );
  const answerMap = buildWilsyCoreAnswerMap(profile, promptValue);
  const selected = answerMap[intent] || answerMap.what_next;
  const checklist = buildWilsyCoreChecklist(profile, intent);
  const quickPrompts =
    Array.isArray(liveModel?.quickPrompts) && liveModel.quickPrompts.length > 0
      ? liveModel.quickPrompts
      : Array.isArray(baseModel?.quickPrompts) && baseModel.quickPrompts.length > 0
        ? baseModel.quickPrompts
        : [
            { id: 'what_next', label: 'What should I do next?' },
            { id: 'release_readiness', label: 'Check release readiness' },
            { id: 'authority_graph', label: 'Explain authority graph' },
            { id: 'evidence_checklist', label: 'Prepare evidence checklist' },
            { id: 'queue_hygiene', label: 'Inspect queue hygiene' },
            { id: 'workflow_packaging', label: 'Package tenant workflow' },
          ];

  return {
    intent,
    domain: profile.workspace,
    supported: true,
    title: selected.title,
    answer: selected.answer,
    outcome: selected.outcome,
    progress: 'Wilsy AI Core Engine',
    quickPrompts,
    actions: [
      {
        rank: 1,
        title: profile.domain === 'billing' ? 'Inspect billing exceptions' : 'Inspect authority path',
        description: checklist[0],
        mode: 'read_only',
        mutation: false,
      },
      {
        rank: 2,
        title: profile.domain === 'billing' ? 'Prepare billing evidence' : 'Prepare evidence proof',
        description: checklist[1],
        mode: 'read_only',
        mutation: false,
      },
      {
        rank: 3,
        title: profile.domain === 'billing' ? 'Check approval owner' : 'Check release readiness',
        description: checklist[2],
        mode: 'read_only',
        mutation: false,
      },
    ],
    checklist,
    commandPlan: [
      `Workspace: ${profile.workspace}`,
      `Focus: ${profile.focus}`,
      `Operator role: ${profile.role}`,
      `Prompt: ${promptValue}`,
      `Intent: ${selected.title}`,
      `Outcome: ${selected.outcome}`,
      `Locked mutation: ${profile.lockedMutation}`,
      ...checklist.map((item) => `Check: ${item}`),
      'Mutation: none until the operator approves a governed Wilsy command.',
    ],
    sourceTrace: [
      {
        label: `${profile.workspace} AI reasoning`,
        tool: 'wilsy_ai_core_engine',
        domain: profile.domain,
        status: 'COMPLETED',
        statusLabel: 'Completed',
        count: checklist.length,
        collectionsChecked: checklist,
        message: 'Answered from workspace context, Wilsy authority rules, and governed execution policy.',
      },
    ],
  };
}
