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
 * @function buildWilsyPlayableActionRail
 * @description Builds clickable, game-like next actions from the AI reasoning result so the operator can move work immediately.
 * @param {Object} profile - Workspace profile.
 * @param {string} intent - Current AI intent.
 * @param {Array<string>} checklist - Evidence and safety checklist.
 * @returns {Array<Object>} Playable action rail entries.
 * @collaboration Wilsy AI Core Engine, Billing action rail, CRM Setup action rail, evidence proof, approval gates, and no-mutation command planning.
 */
export function buildWilsyPlayableActionRail(profile = {}, intent = 'what_next', checklist = []) {
  const workspace = profile?.workspace || 'Wilsy OS';
  const isBilling = profile?.domain === 'billing';
  const safeChecklist = Array.isArray(checklist) ? checklist : [];

  if (isBilling) {
    return [
      {
        rank: 1,
        id: 'inspect_billing_exceptions',
        intent: 'queue_hygiene',
        title: 'Inspect billing exceptions',
        buttonLabel: 'Inspect exceptions',
        prompt: 'Inspect billing queue hygiene',
        description: safeChecklist[0] || 'Inspect open invoices, unpaid receipts, failed payments, and revenue leakage.',
        mode: 'playable_read_only',
        mutation: false,
        evidenceRequired: true,
        nextState: 'Exception lane',
        lockedReason: 'Billing mutation remains locked until approval and receipt proof are complete.',
      },
      {
        rank: 2,
        id: 'prepare_billing_evidence',
        intent: 'evidence_checklist',
        title: 'Prepare billing evidence',
        buttonLabel: 'Prepare evidence',
        prompt: 'Prepare billing evidence checklist',
        description: safeChecklist[1] || 'Collect tenant, operator, payment, entitlement, receipt, and approval evidence.',
        mode: 'playable_read_only',
        mutation: false,
        evidenceRequired: true,
        nextState: 'Evidence lane',
        lockedReason: 'Evidence is required before payment, entitlement, credit, refund, or invoice release.',
      },
      {
        rank: 3,
        id: 'check_billing_approval_owner',
        intent: 'release_readiness',
        title: 'Check approval owner',
        buttonLabel: 'Check approval',
        prompt: 'Check billing release readiness',
        description: safeChecklist[2] || 'Verify approval owner before billing release, refund, credit, or entitlement change.',
        mode: 'playable_read_only',
        mutation: false,
        evidenceRequired: true,
        nextState: 'Approval lane',
        lockedReason: 'Release remains locked until approval owner and receipt proof are present.',
      },
      {
        rank: 4,
        id: 'package_billing_workflow',
        intent: 'workflow_packaging',
        title: 'Package billing workflow',
        buttonLabel: 'Package workflow',
        prompt: 'Package tenant billing workflow',
        description: 'Package exception detection, evidence, approval, and release gates into a tenant-facing Revenue Assurance workflow.',
        mode: 'playable_read_only',
        mutation: false,
        evidenceRequired: true,
        nextState: 'Workflow package',
        lockedReason: 'Packaging is read-only until operator approves a governed command.',
      },
    ];
  }

  return [
    {
      rank: 1,
      id: 'inspect_authority_path',
      intent: 'authority_graph',
      title: 'Inspect authority path',
      buttonLabel: 'Inspect authority',
      prompt: 'Explain authority graph',
      description: safeChecklist[0] || 'Verify operator role, authority boundary, and command surface.',
      mode: 'playable_read_only',
      mutation: false,
      evidenceRequired: true,
      nextState: `${workspace} authority lane`,
      lockedReason: 'Mutation remains locked until authority and approval proof are complete.',
    },
    {
      rank: 2,
      id: 'prepare_evidence_proof',
      intent: 'evidence_checklist',
      title: 'Prepare evidence proof',
      buttonLabel: 'Prepare evidence',
      prompt: 'Prepare evidence checklist',
      description: safeChecklist[1] || 'Collect staged proof, approval path, release readiness, and command evidence.',
      mode: 'playable_read_only',
      mutation: false,
      evidenceRequired: true,
      nextState: `${workspace} evidence lane`,
      lockedReason: 'Evidence must be complete before any governed command can mutate state.',
    },
    {
      rank: 3,
      id: 'check_release_readiness',
      intent: 'release_readiness',
      title: 'Check release readiness',
      buttonLabel: 'Check release',
      prompt: 'Check release readiness',
      description: safeChecklist[2] || 'Check release permission, packet integrity, approval state, and receipt trail.',
      mode: 'playable_read_only',
      mutation: false,
      evidenceRequired: true,
      nextState: `${workspace} release lane`,
      lockedReason: 'Release remains locked until authority, evidence, and approval are present.',
    },
    {
      rank: 4,
      id: 'package_tenant_workflow',
      intent: 'workflow_packaging',
      title: 'Package tenant workflow',
      buttonLabel: 'Package workflow',
      prompt: 'Package tenant workflow',
      description: 'Package authority checks, evidence, approval, and release readiness into a tenant productivity workflow.',
      mode: 'playable_read_only',
      mutation: false,
      evidenceRequired: true,
      nextState: `${workspace} package`,
      lockedReason: 'Package is read-only until the operator approves a governed command.',
    },
  ];
}


/**
 * @function buildWilsyMissionState
 * @description Builds a game-like mission state when the operator clicks a playable action rail button.
 * @param {Object} profile - Workspace profile.
 * @param {string} intent - Resolved intent.
 * @param {string} promptText - Operator prompt text.
 * @param {Array<string>} checklist - Current checklist.
 * @returns {Object|null} Mission state for the selected action.
 * @collaboration Wilsy AI Core Engine, playable action rail, authority inspection, evidence preparation, release readiness, workflow packaging, and safe governed execution.
 */
export function buildWilsyMissionState(profile = {}, intent = 'what_next', promptText = '', checklist = []) {
  const prompt = String(promptText || '').toLowerCase();
  const isBilling = profile?.domain === 'billing';
  const workspace = profile?.workspace || 'Wilsy OS';
  const safeChecklist = Array.isArray(checklist) ? checklist : [];

  const actionKey =
    prompt.includes('inspect') || prompt.includes('authority')
      ? 'inspect'
      : prompt.includes('evidence')
        ? 'evidence'
        : prompt.includes('approval') || prompt.includes('release')
          ? 'approval'
          : prompt.includes('package') || prompt.includes('workflow')
            ? 'package'
            : intent;

  const missionMap = isBilling
    ? {
        inspect: {
          title: 'Mission: Inspect billing exceptions',
          objective: 'Find the billing items that can leak revenue or create unauthorized state change.',
          answer: 'Open the exception lane first: unpaid invoices, failed payments, missing receipts, entitlement mismatches, unresolved credits, refunds, and blocked approvals. Your job is not to mutate billing yet; your job is to identify which item deserves evidence and approval.',
          outcome: 'Mission active: billing exceptions must be inspected before evidence or release.',
          gates: ['Invoice state known', 'Payment status known', 'Receipt trail present', 'Tenant entitlement checked'],
          nextMoves: ['Prepare billing evidence', 'Check approval owner', 'Package billing workflow'],
        },
        evidence: {
          title: 'Mission: Prepare billing evidence',
          objective: 'Build the evidence pack that makes a billing command safe.',
          answer: 'Prepare the evidence pack before any billing change: invoice ID, tenant identity, operator identity, payment status, receipt trail, plan entitlement, approval owner, command surface, and timestamp. This is the proof layer that protects revenue and prevents accidental mutation.',
          outcome: 'Mission active: evidence pack is the next safe billing move.',
          gates: ['Tenant identified', 'Operator identified', 'Invoice/payment proof attached', 'Approval owner known'],
          nextMoves: ['Check approval owner', 'Package billing workflow', 'Inspect billing exceptions'],
        },
        approval: {
          title: 'Mission: Check billing approval owner',
          objective: 'Find who can authorize the billing-state change.',
          answer: 'Approval is the lock. Credits, refunds, entitlement changes, failed-payment overrides, and invoice release must not move until an authorized approval owner is present. If approval is missing, hold release and route the evidence pack to the correct owner.',
          outcome: 'Mission active: approval gate decides whether release can unlock.',
          gates: ['Approval owner present', 'Evidence pack complete', 'Release action identified', 'Mutation still locked'],
          nextMoves: ['Prepare billing evidence', 'Package billing workflow', 'Inspect billing exceptions'],
        },
        package: {
          title: 'Mission: Package billing workflow',
          objective: 'Turn the billing control loop into a tenant-facing productivity workflow.',
          answer: 'Package the workflow as Revenue Assurance: detect exceptions, collect evidence, verify approval, and only then release a billing-state command. This is how Wilsy turns billing operations into a repeatable productivity lane.',
          outcome: 'Mission active: billing workflow package ready for tenant value framing.',
          gates: ['Exception lane defined', 'Evidence pack defined', 'Approval gate defined', 'Release lock defined'],
          nextMoves: ['Inspect billing exceptions', 'Prepare billing evidence', 'Check approval owner'],
        },
      }
    : {
        inspect: {
          title: 'Mission: Inspect authority path',
          objective: 'Find the exact permission path before setup work moves.',
          answer: 'Inspect the authority path first: who can review, who can approve, who can release, and what evidence each step requires. Setup control changes stay locked until that path is proven.',
          outcome: 'Mission active: authority path must be proven before execution.',
          gates: ['Reviewer identified', 'Approver identified', 'Release owner identified', 'Evidence requirement known'],
          nextMoves: ['Prepare evidence proof', 'Check release readiness', 'Package tenant workflow'],
        },
        evidence: {
          title: 'Mission: Prepare setup evidence',
          objective: 'Collect the receipts that make the setup command safe.',
          answer: 'Prepare the proof pack: staged review proof, packet status, approval receipt, release readiness, tenant identity, operator identity, and command-surface evidence. This makes the next setup move auditable.',
          outcome: 'Mission active: setup evidence must be ready before mutation.',
          gates: ['Staged proof present', 'Packet status known', 'Approval receipt attached', 'Command surface recorded'],
          nextMoves: ['Inspect authority path', 'Check release readiness', 'Package tenant workflow'],
        },
        approval: {
          title: 'Mission: Check release readiness',
          objective: 'Decide whether release can unlock or must stay blocked.',
          answer: 'Release readiness requires staged proof, approval state, release permission, packet integrity, and receipt trail. If one is missing, release stays locked and the next move is evidence repair.',
          outcome: 'Mission active: release gate is being checked.',
          gates: ['Staged proof clear', 'Approval complete', 'Release permission present', 'Receipt trail complete'],
          nextMoves: ['Prepare evidence proof', 'Inspect authority path', 'Package tenant workflow'],
        },
        package: {
          title: 'Mission: Package tenant workflow',
          objective: 'Turn the setup control loop into a repeatable tenant workflow.',
          answer: 'Package the workflow as authority, evidence, approval, and release readiness. This gives the tenant a repeatable operating lane instead of isolated setup cards.',
          outcome: 'Mission active: tenant workflow package ready.',
          gates: ['Authority lane defined', 'Evidence lane defined', 'Approval lane defined', 'Release lane defined'],
          nextMoves: ['Inspect authority path', 'Prepare evidence proof', 'Check release readiness'],
        },
      };

  return missionMap[actionKey] || null;
}


/**
 * @function buildWilsyExecutionCanvas
 * @description Builds a state-aware execution cockpit with telemetry, command tokens, route judge, evidence anchors, and non-obvious next moves.
 * @param {Object} profile - Workspace profile.
 * @param {string} intent - Current resolved intent.
 * @param {string} promptText - Operator prompt text.
 * @param {Array<string>} checklist - Current checklist.
 * @param {Object|null} missionState - Current mission state.
 * @returns {Object} Execution canvas stream payload.
 * @collaboration Wilsy AI Core Engine, live canvas stream, source route judge, evidence anchors, authority boundary, command tokens, and sovereign execution cockpit.
 */
export function buildWilsyExecutionCanvas(profile = {}, intent = 'what_next', promptText = '', checklist = [], missionState = null) {
  const isBilling = profile?.domain === 'billing';
  const workspace = profile?.workspace || 'Wilsy OS';
  const focus = profile?.focus || 'Workspace';
  const safeChecklist = Array.isArray(checklist) ? checklist : [];
  const lowerPrompt = String(promptText || '').toLowerCase();

  const routeBase = isBilling ? 'wilsy://billing' : 'wilsy://crm-setup';
  const cockpitMoves = isBilling
    ? [
        {
          label: 'Trace exception lane',
          intent: 'queue_hygiene',
          token: `${routeBase}/exceptions/trace`,
          telemetry: 'Locate unpaid invoices, failed payments, credits, refunds, and missing receipts.',
        },
        {
          label: 'Bind evidence anchors',
          intent: 'evidence_checklist',
          token: `${routeBase}/evidence/bind`,
          telemetry: 'Attach invoice, tenant, operator, payment, entitlement, approval, and receipt proof.',
        },
        {
          label: 'Judge release route',
          intent: 'release_readiness',
          token: `${routeBase}/release/judge`,
          telemetry: 'Compare release request against payment state, approval owner, and receipt trail.',
        },
        {
          label: 'Split approval owner',
          intent: 'release_readiness',
          token: `${routeBase}/approval/split-owner`,
          telemetry: 'Separate inspection, approval, and release identity so mutation cannot jump gates.',
        },
        {
          label: 'Forecast leakage risk',
          intent: 'queue_hygiene',
          token: `${routeBase}/risk/leakage-forecast`,
          telemetry: 'Rank exceptions by revenue leakage, stale receipts, and entitlement mismatch.',
        },
        {
          label: 'Package revenue workflow',
          intent: 'workflow_packaging',
          token: `${routeBase}/workflow/package-revenue-assurance`,
          telemetry: 'Turn the lane into a tenant-facing Revenue Assurance workflow.',
        },
      ]
    : [
        {
          label: 'Trace authority route',
          intent: 'authority_graph',
          token: `${routeBase}/authority/trace-route`,
          telemetry: 'Resolve reviewer, approver, release owner, and evidence boundary before setup changes state.',
        },
        {
          label: 'Bind evidence anchors',
          intent: 'evidence_checklist',
          token: `${routeBase}/evidence/bind-anchors`,
          telemetry: 'Attach staged proof, packet state, approval receipt, operator identity, tenant identity, and command surface.',
        },
        {
          label: 'Judge release route',
          intent: 'release_readiness',
          token: `${routeBase}/release/judge-route`,
          telemetry: 'Check staged proof, approval state, release permission, packet integrity, and receipt trail.',
        },
        {
          label: 'Inspect queue drift',
          intent: 'queue_hygiene',
          token: `${routeBase}/queue/inspect-drift`,
          telemetry: 'Find stale reviews, orphan approvals, repeated pending states, and missing receipts.',
        },
        {
          label: 'Split control boundary',
          intent: 'authority_graph',
          token: `${routeBase}/authority/split-boundary`,
          telemetry: 'Separate review power, approval power, release power, and mutation power.',
        },
        {
          label: 'Package tenant workflow',
          intent: 'workflow_packaging',
          token: `${routeBase}/workflow/package-governance-lane`,
          telemetry: 'Convert authority, evidence, approval, and release readiness into a repeatable tenant lane.',
        },
        {
          label: 'Prepare repair route',
          intent: 'evidence_checklist',
          token: `${routeBase}/repair/prepare-route`,
          telemetry: 'Create the repair path for any missing receipt, role, permission, or packet proof.',
        },
      ];

  const prioritizedMoves = cockpitMoves
    .map((move, index) => ({
      ...move,
      rank: index + 1,
      mode: 'read_only_execution_stream',
      mutation: false,
      evidenceRequired: true,
    }))
    .sort((left, right) => {
      const leftScore = lowerPrompt.includes(left.intent.replace('_', ' ')) || lowerPrompt.includes(left.label.toLowerCase()) ? -1 : left.rank;
      const rightScore = lowerPrompt.includes(right.intent.replace('_', ' ')) || lowerPrompt.includes(right.label.toLowerCase()) ? -1 : right.rank;
      return leftScore - rightScore;
    });

  return {
    label: 'Live Canvas Stream',
    summary: missionState?.objective || `State-aware execution cockpit for ${workspace}.`,
    moves: prioritizedMoves.map((move) => move.label),
    tokens: prioritizedMoves,
    telemetry: [
      {
        label: 'Authority Boundary',
        value: isBilling
          ? 'Billing mutation locked until approval owner and receipt trail are proven.'
          : 'Setup mutation locked until reviewer, approver, release owner, and evidence path are proven.',
      },
      {
        label: 'Evidence Anchor',
        value: safeChecklist[0] || 'Proof is required before any governed command can execute.',
      },
      {
        label: 'Execution Mode',
        value: 'Read-only stream. Wilsy prepares the route; human approval executes mutation.',
      },
      {
        label: 'Workspace Lens',
        value: `${workspace} · ${focus}`,
      },
    ],
    sourceRouteJudge: {
      status: 'READ_ONLY_ALLOWED',
      route: isBilling ? 'billing_governance_lane' : 'crm_setup_governance_lane',
      decision: 'Prepare work only. Mutation requires governed approval.',
      reason: profile?.lockedMutation || 'Mutation remains locked until approval and evidence are present.',
    },
    evidenceAnchors: safeChecklist.slice(0, 6),
  };
}


/**
 * @function buildWilsyNativeExecutionThread
 * @description Builds a native execution thread with command tokens, route judging, telemetry, and deeper governed actions.
 * @param {Object} profile - Workspace profile.
 * @param {string} intent - Resolved intent.
 * @param {string} promptText - Operator prompt text.
 * @param {Array<string>} checklist - Current checklist.
 * @param {Object|null} missionState - Optional mission state.
 * @param {Array<Object>} playableActions - Existing playable action candidates.
 * @returns {Object} Native execution thread payload.
 * @collaboration Wilsy AI core engine, native execution canvas, sovereign route judge, evidence anchors, command tokens, and operator cockpit.
 */
export function buildWilsyNativeExecutionThread(profile = {}, intent = 'what_next', promptText = '', checklist = [], missionState = null, playableActions = []) {
  const isBilling = profile?.domain === 'billing';
  const workspace = profile?.workspace || 'Wilsy OS';
  const focus = profile?.focus || 'Workspace';
  const route = isBilling ? 'billing-governance-lane' : 'crm-setup-governance-lane';
  const routeBase = isBilling ? 'wilsy://billing' : 'wilsy://crm-setup';
  const safeChecklist = Array.isArray(checklist) ? checklist : [];

  const tokens = isBilling
    ? [
        ['Trace exception lane', 'queue_hygiene', `${routeBase}/exceptions/trace`, 'Locate unpaid invoices, failed payments, credits, refunds, entitlement mismatch, and missing receipts.'],
        ['Bind evidence anchors', 'evidence_checklist', `${routeBase}/evidence/bind`, 'Attach invoice, tenant, operator, payment, entitlement, approval, and receipt proof.'],
        ['Judge release route', 'release_readiness', `${routeBase}/release/judge`, 'Compare release request against payment state, approval owner, and receipt trail.'],
        ['Split approval owner', 'release_readiness', `${routeBase}/approval/split-owner`, 'Separate inspection, approval, and release identity so mutation cannot jump gates.'],
        ['Forecast leakage risk', 'queue_hygiene', `${routeBase}/risk/leakage-forecast`, 'Rank exceptions by revenue leakage, stale receipts, and entitlement mismatch.'],
        ['Package revenue workflow', 'workflow_packaging', `${routeBase}/workflow/package-revenue-assurance`, 'Turn the lane into a tenant-facing Revenue Assurance workflow.'],
      ]
    : [
        ['Trace authority route', 'authority_graph', `${routeBase}/authority/trace-route`, 'Resolve reviewer, approver, release owner, and evidence boundary before setup changes state.'],
        ['Bind evidence anchors', 'evidence_checklist', `${routeBase}/evidence/bind-anchors`, 'Attach staged proof, packet state, approval receipt, operator identity, tenant identity, and command surface.'],
        ['Judge release route', 'release_readiness', `${routeBase}/release/judge-route`, 'Check staged proof, approval state, release permission, packet integrity, and receipt trail.'],
        ['Inspect queue drift', 'queue_hygiene', `${routeBase}/queue/inspect-drift`, 'Find stale reviews, orphan approvals, repeated pending states, and missing receipts.'],
        ['Split control boundary', 'authority_graph', `${routeBase}/authority/split-boundary`, 'Separate review power, approval power, release power, and mutation power.'],
        ['Prepare repair route', 'evidence_checklist', `${routeBase}/repair/prepare-route`, 'Create the repair path for any missing receipt, role, permission, or packet proof.'],
        ['Package tenant workflow', 'workflow_packaging', `${routeBase}/workflow/package-governance-lane`, 'Convert authority, evidence, approval, and release readiness into a repeatable tenant lane.'],
      ];

  const nativeTokens = tokens.map(([label, tokenIntent, token, telemetry], index) => ({
    rank: index + 1,
    id: token.replace('wilsy://', '').replaceAll('/', '-'),
    label,
    title: label,
    buttonLabel: label,
    intent: tokenIntent,
    prompt: label,
    token,
    telemetry,
    description: telemetry,
    mode: 'read_only_execution_stream',
    mutation: false,
    evidenceRequired: true,
  }));

  return {
    label: 'Native Execution Thread',
    summary: missionState?.objective || `State-aware execution cockpit for ${workspace}.`,
    stream: nativeTokens,
    tokens: nativeTokens,
    telemetry: [
      {
        label: 'Authority Boundary',
        value: isBilling
          ? 'Billing mutation locked until approval owner and receipt trail are proven.'
          : 'Setup mutation locked until reviewer, approver, release owner, and evidence path are proven.',
      },
      {
        label: 'Evidence Anchor',
        value: safeChecklist[0] || 'Proof is required before any governed command can execute.',
      },
      {
        label: 'Execution Mode',
        value: 'Read-only stream. Wilsy prepares the route; human approval executes mutation.',
      },
      {
        label: 'Workspace Lens',
        value: `${workspace} · ${focus}`,
      },
    ],
    sourceRouteJudge: {
      status: 'READ_ONLY_ALLOWED',
      route,
      decision: 'Prepare work only. Mutation requires governed approval.',
      reason: profile?.lockedMutation || 'Mutation remains locked until approval and evidence are present.',
    },
    evidenceAnchors: safeChecklist.slice(0, 6),
    inheritedActions: Array.isArray(playableActions) ? playableActions.slice(0, 4) : [],
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

  const playableActions = buildWilsyPlayableActionRail(profile, intent, checklist);
  const missionState = buildWilsyMissionState(profile, intent, promptValue, checklist);
  const executionCanvas =
    typeof buildWilsyExecutionCanvas === 'function'
      ? buildWilsyExecutionCanvas(profile, intent, promptValue, checklist, missionState)
      : null;
  const sovereignExecutionThread = buildWilsyNativeExecutionThread(
    profile,
    intent,
    promptValue,
    checklist,
    missionState,
    playableActions,
  );
  const selectedTitle = missionState?.title || selected.title;
  const selectedAnswer = missionState?.answer || selected.answer;
  const selectedOutcome = missionState?.outcome || selected.outcome;

  return {
    intent,
    domain: profile.workspace,
    supported: true,
    title: selectedTitle,
    answer: selectedAnswer,
    outcome: selectedOutcome,
    progress: 'Wilsy AI Core Engine',
    quickPrompts,
    actions: playableActions,
    executionCanvas: sovereignExecutionThread,
    executionThread: sovereignExecutionThread?.stream || [],
    commandTokens: sovereignExecutionThread?.tokens || [],
    telemetryPacks: sovereignExecutionThread?.telemetry || [],
    sourceRouteJudge: sovereignExecutionThread?.sourceRouteJudge || null,
    evidenceAnchors: sovereignExecutionThread?.evidenceAnchors || [],
    playableActions,
    missionState,
    actionSummary: playableActions.map((action) => action.title),
    checklist,
    missionGates: missionState?.gates || checklist,
    missionNextMoves: sovereignExecutionThread?.stream?.map((row) => row.label) || executionCanvas?.moves || missionState?.nextMoves || [],
    executionCanvas,
    commandTokens: executionCanvas?.tokens || [],
    telemetryPacks: executionCanvas?.telemetry || [],
    sourceRouteJudge: executionCanvas?.sourceRouteJudge || null,
    evidenceAnchors: executionCanvas?.evidenceAnchors || [],
    commandPlan: [
      `Workspace: ${profile.workspace}`,
      `Focus: ${profile.focus}`,
      `Operator role: ${profile.role}`,
      `Prompt: ${promptValue}`,
      `Intent: ${selectedTitle}`,
      `Outcome: ${selectedOutcome}`,
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
