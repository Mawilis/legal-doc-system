/* eslint-disable */
import mongoose from 'mongoose';

/**
 * @function coerceWilsyTaskText
 * @description Safely coerces task/reminder values into bounded business text.
 * @param {unknown} value - Raw value.
 * @param {number} limit - Maximum length.
 * @returns {string} Bounded text.
 * @collaboration Wilsy Task Reminder Execution Bridge, tenant-safe input parsing, and operator-ready task drafts.
 */
function coerceWilsyTaskText(value = '', limit = 1400) {
  return String(value || '')
    .replace(/\s+/g, ' ')
    .trim()
    .slice(0, limit);
}

/**
 * @function buildWilsyTaskId
 * @description Builds stable task/reminder draft and event identifiers.
 * @param {string} prefix - Identifier prefix.
 * @returns {string} Stable identifier.
 * @collaboration CRM Task draft links, reminder execution receipts, and operator proof harness.
 */
function buildWilsyTaskId(prefix = 'task') {
  return `${prefix}_${Date.now()}_${Math.random().toString(36).slice(2, 10)}`;
}

/**
 * @function formatWilsyMonthName
 * @description Formats a zero-based month index into a business month name.
 * @param {number} monthIndex - Zero-based month index.
 * @returns {string} Month name.
 * @collaboration Task due-date parsing, business-English answers, and reminder draft proof.
 */
function formatWilsyMonthName(monthIndex = 0) {
  const months = [
    'January',
    'February',
    'March',
    'April',
    'May',
    'June',
    'July',
    'August',
    'September',
    'October',
    'November',
    'December',
  ];

  return months[monthIndex] || 'January';
}

/**
 * @function parseWilsyTaskDate
 * @description Parses natural due dates such as today, tomorrow, next week, 7th, or 7th of July.
 * @param {string} question - Operator request.
 * @param {Date} now - Current date.
 * @returns {{isoDate: string|null, label: string, partial: boolean}} Parsed due date.
 * @collaboration Task/reminder draft preparation, due-date evidence, and approval-ready command payloads.
 */
function parseWilsyTaskDate(question = '', now = new Date()) {
  const text = coerceWilsyTaskText(question, 1800);
  const lower = text.toLowerCase();
  const monthNames = [
    'january',
    'february',
    'march',
    'april',
    'may',
    'june',
    'july',
    'august',
    'september',
    'october',
    'november',
    'december',
  ];
  const monthPattern = monthNames.join('|');
  const isoMatch = text.match(/\b(20\d{2})-(\d{2})-(\d{2})\b/);
  const dayMonth = new RegExp(
    `\\b(?:on\\s+)?(?:the\\s+)?(\\d{1,2})(?:st|nd|rd|th)?\\s+(?:of\\s+)?(${monthPattern})\\b`,
    'i'
  );
  const bareOrdinal = text.match(/\b(?:on\s+)?(?:the\s+)?(\d{1,2})(?:st|nd|rd|th)\b/i);
  const yearMatch = text.match(/\b(20\d{2})\b/);

  if (isoMatch) {
    return {
      isoDate: isoMatch[0],
      label: isoMatch[0],
      partial: false,
    };
  }

  if (lower.includes('today')) {
    return {
      isoDate: now.toISOString().slice(0, 10),
      label: 'today',
      partial: false,
    };
  }

  if (lower.includes('tomorrow')) {
    const value = new Date(now);
    value.setDate(value.getDate() + 1);

    return {
      isoDate: value.toISOString().slice(0, 10),
      label: 'tomorrow',
      partial: false,
    };
  }

  const dayMonthMatch = text.match(dayMonth);

  if (dayMonthMatch) {
    const day = Number(dayMonthMatch[1]);
    const monthIndex = monthNames.indexOf(String(dayMonthMatch[2]).toLowerCase());
    let year = Number(yearMatch?.[1] || now.getFullYear());
    let value = new Date(Date.UTC(year, monthIndex, day));

    if (
      !yearMatch &&
      value < new Date(Date.UTC(now.getFullYear(), now.getMonth(), now.getDate()))
    ) {
      year += 1;
      value = new Date(Date.UTC(year, monthIndex, day));
    }

    return {
      isoDate: value.toISOString().slice(0, 10),
      label: `${day} ${formatWilsyMonthName(monthIndex)} ${year}`,
      partial: false,
    };
  }

  if (bareOrdinal) {
    const day = Number(bareOrdinal[1]);
    let year = now.getFullYear();
    let monthIndex = now.getMonth();
    let value = new Date(Date.UTC(year, monthIndex, day));
    const today = new Date(Date.UTC(now.getFullYear(), now.getMonth(), now.getDate()));

    if (value < today) {
      monthIndex += 1;

      if (monthIndex > 11) {
        monthIndex = 0;
        year += 1;
      }

      value = new Date(Date.UTC(year, monthIndex, day));
    }

    return {
      isoDate: value.toISOString().slice(0, 10),
      label: `${day} ${formatWilsyMonthName(monthIndex)} ${year}`,
      partial: false,
    };
  }

  if (lower.includes('next week')) {
    return {
      isoDate: null,
      label: 'next week',
      partial: true,
    };
  }

  return {
    isoDate: null,
    label: 'Due date not specified',
    partial: true,
  };
}

/**
 * @function parseWilsyTaskTime
 * @description Parses an optional task/reminder time from the request.
 * @param {string} question - Operator request.
 * @returns {string|null} Time label.
 * @collaboration Task reminder scheduling, due-time evidence, and approval-ready task drafts.
 */
function parseWilsyTaskTime(question = '') {
  const text = coerceWilsyTaskText(question, 1400);
  const match = text.match(/\b(?:at\s+)?([01]?\d|2[0-3])(?::([0-5]\d))?\s*(am|pm)?\b/i);

  if (!match) {
    return null;
  }

  const minute = match[2] || '00';
  const meridiem = match[3] ? ` ${match[3].toUpperCase()}` : '';

  return `${match[1]}:${minute}${meridiem}`;
}

/**
 * @function extractWilsyTaskTitle
 * @description Extracts a business task/reminder title from the request.
 * @param {string} question - Operator request.
 * @returns {string} Task title.
 * @collaboration Task draft details, reminder preparation, and business-English operator answers.
 */
function extractWilsyTaskTitle(question = '') {
  const text = coerceWilsyTaskText(question, 1800);
  const reminderMatch = text.match(/\bas\s+(?:a\s+)?reminder\s+to\s+(.+)$/i);
  const remindMeMatch = text.match(/\bremind\s+me\s+to\s+(.+)$/i);
  const createTaskMatch = text.match(/\bcreate\s+(?:a\s+)?task\s+(?:to\s+)?(.+)$/i);

  if (reminderMatch) {
    return coerceWilsyTaskText(reminderMatch[1], 180);
  }

  if (remindMeMatch) {
    return coerceWilsyTaskText(remindMeMatch[1], 180);
  }

  if (createTaskMatch) {
    let value = createTaskMatch[1];

    value = value
      .replace(/\bon\s+(?:the\s+)?\d{1,2}(?:st|nd|rd|th)?(?:\s+of\s+[a-z]+)?\b/gi, '')
      .replace(/\btoday\b|\btomorrow\b|\bnext week\b|\bthis week\b/gi, '')
      .replace(/\bas\s+(?:a\s+)?reminder\b/gi, '')
      .replace(/^\s*to\s+/i, '')
      .trim();

    return coerceWilsyTaskText(value, 180) || 'Task';
  }

  return 'Task';
}

/**
 * @function buildWilsyTaskReminderDraft
 * @description Builds a validated task/reminder draft from the operator request.
 * @param {Object} params - Draft params.
 * @param {string} params.question - Operator request.
 * @param {string} params.tenantId - Tenant id.
 * @param {string} params.operatorId - Operator id.
 * @param {string} params.kind - Draft kind.
 * @returns {Object} Task/reminder draft.
 * @collaboration CRM Task drafts, reminder execution readiness, and governed approval workflow.
 */
export function buildWilsyTaskReminderDraft({
  question = '',
  tenantId = 'MASTER',
  operatorId = 'WILSY_OPERATOR',
  kind = 'task',
} = {}) {
  const dueDate = parseWilsyTaskDate(question);
  const title = extractWilsyTaskTitle(question);
  const timeLabel = parseWilsyTaskTime(question);
  const draftId = buildWilsyTaskId(kind === 'reminder' ? 'reminder_draft' : 'task_draft');
  const missingFields = [];

  if (!title || title === 'Task') {
    missingFields.push('task title');
  }

  if (!dueDate.isoDate) {
    missingFields.push(dueDate.partial ? 'exact due date' : 'due date');
  }

  return {
    draftId,
    tenantId,
    operatorId,
    kind,
    title,
    dueDateLabel: dueDate.label,
    isoDueDate: dueDate.isoDate,
    timeLabel: timeLabel || 'No specific time',
    priority: 'normal',
    sourceQuestion: coerceWilsyTaskText(question, 1200),
    missingFields,
    readyForApproval: missingFields.length === 0,
    crmTaskDraftLink: `/crm/tasks/drafts/${draftId}`,
    executionStatus:
      missingFields.length === 0
        ? 'Draft ready for approval. No task or reminder has been created yet.'
        : 'Draft incomplete. Missing details must be supplied before approval.',
  };
}

/**
 * @function isWilsyTaskExecutionApproved
 * @description Verifies whether a task/reminder execution request has explicit approval.
 * @param {Object} params - Approval params.
 * @param {Object} params.req - Request object.
 * @returns {boolean} Whether execution is approved.
 * @collaboration Human-in-the-loop governance, task write safety, and tenant command approval.
 */
function isWilsyTaskExecutionApproved({ req = {} } = {}) {
  const mode = String(
    req.query?.taskExecutionMode || req.body?.taskExecutionMode || ''
  ).toUpperCase();
  const approval = String(
    req.query?.taskApprovalToken ||
      req.body?.taskApprovalToken ||
      req.headers?.['x-wilsy-task-approval'] ||
      ''
  );

  if (mode !== 'APPROVED_EXECUTE') {
    return false;
  }

  const expected =
    process.env.WILSY_TASK_EXECUTION_APPROVAL_TOKEN || 'P60K5Q10AS_APPROVE_TASK_WRITE';

  return approval === expected;
}

/**
 * @function buildWilsyTaskHeaders
 * @description Builds institutional headers for task/reminder execution evidence.
 * @param {Object} params - Header params.
 * @returns {Object} Institutional headers.
 * @collaboration Task execution bridge, Wilsy evidence receipts, and tenant/operator proof.
 */
function buildWilsyTaskHeaders({
  tenantId = 'MASTER',
  operatorId = 'WILSY_OPERATOR',
  route = '/api/source-registry/health',
  commandSurface = 'WILSY_TASK_REMINDER_EXECUTION_BRIDGE',
} = {}) {
  return {
    tenantId,
    operatorId,
    generatedAt: new Date().toISOString(),
    route,
    commandSurface,
    mutation: true,
    contractVersion: 'P60K5Q10AS_TASK_REMINDER_EXECUTION_BRIDGE',
  };
}

/**
 * @function executeWilsyCrmTaskReminder
 * @description Creates a CRM task/reminder when explicit approval is present and MongoDB is connected.
 * @param {Object} params - Execution params.
 * @param {Object} params.draft - Task/reminder draft.
 * @param {Object} params.institutionalHeaders - Institutional headers.
 * @returns {Promise<Object>} Execution result.
 * @collaboration CRM Tasks, reminder storage, evidence receipts, and tenant task links.
 */
async function executeWilsyCrmTaskReminder({ draft = {}, institutionalHeaders = {} } = {}) {
  const db = mongoose.connection?.db;

  if (!db) {
    return {
      connector: 'CRM Tasks',
      status: 'CONNECTOR_UNAVAILABLE',
      statusLabel: 'CRM Tasks unavailable',
      taskLink: draft.crmTaskDraftLink,
      message:
        'CRM Tasks could not create the item because the database connection is unavailable.',
    };
  }

  const taskId = buildWilsyTaskId(draft.kind === 'reminder' ? 'reminder' : 'task');
  const document = {
    taskId,
    tenantId: draft.tenantId,
    operatorId: draft.operatorId,
    type: draft.kind === 'reminder' ? 'REMINDER' : 'TASK',
    title: draft.title,
    dueDate: draft.isoDueDate,
    dueTime: draft.timeLabel,
    priority: draft.priority,
    status: 'OPEN',
    sourceQuestion: draft.sourceQuestion,
    createdAt: new Date(),
    updatedAt: new Date(),
    institutionalHeaders,
    strikePayload: {
      institutionalHeaders,
      commandType: draft.kind === 'reminder' ? 'CRM_REMINDER_CREATED' : 'CRM_TASK_CREATED',
      mutation: true,
    },
  };

  const result = await db.collection('crm_tasks').insertOne(document);
  const id = result.insertedId?.toString?.() || taskId;

  return {
    connector: 'CRM Tasks',
    status: draft.kind === 'reminder' ? 'REMINDER_CREATED' : 'TASK_CREATED',
    statusLabel: draft.kind === 'reminder' ? 'Reminder created' : 'Task created',
    taskId: id,
    taskLink: `/crm/tasks/${id}`,
    message:
      draft.kind === 'reminder'
        ? 'The reminder has been created in CRM Tasks.'
        : 'The task has been created in CRM Tasks.',
  };
}

/**
 * @function executeWilsyTaskReminderBridge
 * @description Prepares or executes a task/reminder through the governed CRM Tasks bridge.
 * @param {Object} params - Bridge params.
 * @param {Object} params.req - Request object.
 * @param {string} params.question - Operator request.
 * @param {string} params.tenantId - Tenant id.
 * @param {string} params.operatorId - Operator id.
 * @param {string} params.kind - Draft kind.
 * @returns {Promise<Object>} Task/reminder bridge result.
 * @collaboration Wilsy Operator Kernel, Task Reminder Execution Bridge, evidence receipts, and approval workflow.
 */
export async function executeWilsyTaskReminderBridge({
  req = {},
  question = '',
  tenantId = 'MASTER',
  operatorId = 'WILSY_OPERATOR',
  kind = 'task',
} = {}) {
  const draft = buildWilsyTaskReminderDraft({
    question,
    tenantId,
    operatorId,
    kind,
  });
  const institutionalHeaders = buildWilsyTaskHeaders({
    tenantId,
    operatorId,
  });
  const approvalGranted = isWilsyTaskExecutionApproved({ req });

  if (!draft.readyForApproval) {
    return {
      tool: 'task_reminder_execution_bridge',
      label: kind === 'reminder' ? 'Reminder draft' : 'Task draft',
      domain: 'tasks',
      status: 'DRAFT_INCOMPLETE',
      statusLabel: 'Draft incomplete',
      mutation: false,
      draft,
      crmTaskLink: draft.crmTaskDraftLink,
      taskLink: null,
      missingFields: draft.missingFields,
      connector: 'Approval gate',
      message: `I need ${draft.missingFields.join(', ')} before this ${kind} can be approved.`,
      institutionalHeaders: {
        ...institutionalHeaders,
        mutation: false,
      },
      strikePayload: {
        institutionalHeaders: {
          ...institutionalHeaders,
          mutation: false,
        },
        commandType: 'TASK_REMINDER_DRAFT_INCOMPLETE',
        mutation: false,
      },
    };
  }

  if (!approvalGranted) {
    return {
      tool: 'task_reminder_execution_bridge',
      label: kind === 'reminder' ? 'Reminder draft' : 'Task draft',
      domain: 'tasks',
      status: 'APPROVAL_REQUIRED',
      statusLabel: 'Approval required',
      mutation: false,
      draft,
      crmTaskLink: draft.crmTaskDraftLink,
      taskLink: draft.crmTaskDraftLink,
      missingFields: [],
      connector: 'Approval gate',
      message: `The ${kind} draft is ready. Execution requires operator approval before anything is created.`,
      institutionalHeaders: {
        ...institutionalHeaders,
        mutation: false,
      },
      strikePayload: {
        institutionalHeaders: {
          ...institutionalHeaders,
          mutation: false,
        },
        commandType: 'TASK_REMINDER_DRAFT_READY_FOR_APPROVAL',
        mutation: false,
      },
    };
  }

  const execution = await executeWilsyCrmTaskReminder({
    draft,
    institutionalHeaders,
  });

  return {
    tool: 'task_reminder_execution_bridge',
    label: kind === 'reminder' ? 'Reminder execution bridge' : 'Task execution bridge',
    domain: 'tasks',
    status: execution.status,
    statusLabel: execution.statusLabel,
    mutation: execution.status === 'TASK_CREATED' || execution.status === 'REMINDER_CREATED',
    draft,
    crmTaskLink: execution.taskLink || draft.crmTaskDraftLink,
    taskLink: execution.taskLink,
    missingFields: [],
    connector: execution.connector,
    message: execution.message,
    taskId: execution.taskId,
    institutionalHeaders: {
      ...institutionalHeaders,
      mutation: execution.status === 'TASK_CREATED' || execution.status === 'REMINDER_CREATED',
    },
    strikePayload: {
      institutionalHeaders: {
        ...institutionalHeaders,
        mutation: execution.status === 'TASK_CREATED' || execution.status === 'REMINDER_CREATED',
      },
      commandType: execution.status === 'REMINDER_CREATED' ? 'REMINDER_CREATED' : 'TASK_CREATED',
      mutation: execution.status === 'TASK_CREATED' || execution.status === 'REMINDER_CREATED',
    },
  };
}

export default executeWilsyTaskReminderBridge;
