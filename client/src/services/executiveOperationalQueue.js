const ACTIONABLE_STATES = new Set([
  'OPEN', 'PENDING', 'OVERDUE', 'BLOCKED', 'IN_PROGRESS',
  'NEEDS_REVIEW', 'AWAITING_APPROVAL', 'REQUIRES_ACTION',
  'ESCALATED', 'NEW', 'SUBMITTED', 'UNDER_REVIEW'
]);
const TERMINAL_STATES = new Set([
  'CLOSED', 'RESOLVED', 'COMPLETED', 'CANCELLED', 'CANCELED',
  'PAID', 'VOID', 'ARCHIVED', 'FULFILLED', 'REJECTED'
]);
const EXCEPTION_STATES = new Set([
  'OVERDUE', 'BLOCKED', 'NEEDS_REVIEW', 'AWAITING_APPROVAL',
  'REQUIRES_ACTION', 'ESCALATED'
]);

const textValue = (value) => (
  typeof value === 'string' || typeof value === 'number'
    ? String(value)
    : ''
);

const stateOf = (record = {}) => String(
  record.status || record.state || record.workflowStatus || ''
).trim().replace(/[ -]+/g, '_').toUpperCase();

const priorityRank = (record = {}) => {
  const priority = String(record.priority || record.severity || '').toUpperCase();
  const state = stateOf(record);
  if (state === 'OVERDUE' || state === 'BLOCKED' || priority === 'CRITICAL') return 0;
  if (EXCEPTION_STATES.has(state) || priority === 'HIGH') return 1;
  if (priority === 'MEDIUM') return 2;
  return 3;
};

/**
 * Creates a work queue only from actionable records returned by live tenant APIs.
 * It deliberately does not turn recommendations, missing sources, or status-less
 * business records into tasks.
 */
export const buildOperationalQueue = (sources = []) => sources.flatMap((source) => {
  if (!source?.live || !Array.isArray(source.records)) return [];
  return source.records.flatMap((record, index) => {
    if (!record || typeof record !== 'object') return [];
    const status = stateOf(record);
    if (!status || TERMINAL_STATES.has(status) || !ACTIONABLE_STATES.has(status)) return [];
    const recordId = textValue(record.id || record._id || record.uuid);
    return [{
      id: recordId ? `${source.key}:${recordId}` : `${source.key}:row-${index}`,
      recordId,
      sourceKey: source.key,
      sourceLabel: source.label || source.key,
      functionKey: source.functionKey,
      sourceStatus: source.status,
      lastSync: source.lastSync || null,
      status,
      priority: String(record.priority || record.severity || 'NORMAL').toUpperCase(),
      title: textValue(record.title || record.subject || record.name || record.description || record.reference) || 'Untitled source record',
      owner: textValue(record.owner?.name || record.assignee?.name || record.owner || record.assignee),
      dueAt: textValue(record.dueAt || record.dueDate || record.deadline),
      record
    }];
  }).filter(Boolean);
}).sort((left, right) => (
  priorityRank(left.record) - priorityRank(right.record)
  || String(left.dueAt || '9999').localeCompare(String(right.dueAt || '9999'))
  || left.title.localeCompare(right.title)
));

export const buildDecisionExceptions = (queue = []) => queue.filter((item) => (
  EXCEPTION_STATES.has(item.status)
  || ['CRITICAL', 'HIGH'].includes(item.priority)
  || item.record?.requiresApproval === true
  || item.record?.isException === true
));

/** Allowlisted scalar fields only; never serialize arbitrary source records into the inspector. */
export const getOperationalRecordFields = (record = {}) => {
  const fields = [
    ['Reference', record.reference || record.referenceNumber || record.id || record._id],
    ['Status', record.status || record.state || record.workflowStatus],
    ['Priority', record.priority || record.severity],
    ['Owner', record.owner?.name || record.assignee?.name || record.owner || record.assignee],
    ['Due', record.dueAt || record.dueDate || record.deadline],
    ['Customer', record.customerName || record.customer?.name],
    ['Project', record.projectName || record.project?.name],
    ['Category', record.category || record.type],
    ['Amount', record.amount],
    ['Currency', record.currency],
    ['Updated', record.updatedAt || record.modifiedAt]
  ];
  return fields
    .map(([label, value]) => [label, textValue(value)])
    .filter(([, value]) => value);
};
