/**
 * TITLE: WILSY OS Governed Project Work Row
 * VERSION: v1.6.0-READABLE-DUE-WORK-SEMANTICS
 * AUTHORITY: Validated source-backed presentation only; Python EOS owns business state.
 * EPITOME: A single row with selection, verified status, due date, assignee,
 *          provisional status and contextual actions supplied by its caller.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/components/workspaces/ProjectWorkRow.jsx
 * COLLABORATION / OWNERSHIP: ProjectTasksPanel supplies exact-project tasks,
 *          command authorization, idempotency and source readback; row is reusable.
 * CERTIFICATION / UPDATE DATE: 2026-11-19
 * CHANGELOG: v1.6.0-READABLE-DUE-WORK-SEMANTICS shows a
 *          calendar-correct due phrase from verified date-only task fields:
 *          today, tomorrow, overdue days or a concise day/month label;
 *          EOS date evidence is retained verbatim in a title attribute.
 * CHANGELOG: v1.5.0-NAMED-CONTRIBUTOR-AVATAR adds a compact
 *          initials/avatar identity marker only from an EOS-verified display
 *          name, falling back to a neutral person glyph when unavailable.
 *          Opaque principal identifiers remain internal.
 * CHANGELOG: v1.4.0-STRICT-CAPABILITY-BOOLEAN-GATES requires
 *          literal true for each row assignment/keyboard capability;
 *          missing or malformed caller flags can never imply permissions.
 * CHANGELOG: v1.3.0-DENY-BY-DEFAULT-REUSE prevents new
 *          My Work or external callers from receiving write/menu affordances
 *          until they pass explicit source-backed capability flags.
 * CHANGELOG: v1.2.0-EXPLICIT-CALLER-CAPABILITY-GATES hides
 *          assignment and completion shortcuts unless the verified
 *          caller capability projection permits those affordances.
 * CHANGELOG: v1.1.0-TERMINAL-PRIORITY-VISUAL-SEMANTICS mutes
 *          terminal work title without hiding evidence and optionally
 *          signals caller-verified high/critical priority as a small dot.
 * CHANGELOG: v1.0.0-EXTRACTED-REUSABLE-WORK-ROW extracts existing
 *          Project Work presentation with controlled selection, density,
 *          explicit handlers and independently supplied action capabilities.
 * COMPLIANCE: AGENTS.md; POPIA section 19; GDPR Article 32; WCAG 2.2 AA.
 * SECURITY / PRIVACY POSTURE: No HTML injection, bearer tokens or local storage.
 * TENANT BOUNDARY: Caller validates tenant, principal, project and task envelope.
 * AUTHORITY BOUNDARY: No IAM, task authority, status or grant inferred here.
 * FINANCIAL AUTHORITY BOUNDARY: Kennel EOS executes financial authority alone.
 */
import React from 'react';
import { Waypoints, ClipboardList, UserRound } from 'lucide-react';
import ProjectWorkRowActions from './ProjectWorkRowActions.jsx';

const NO_ACTION_CAPABILITIES = Object.freeze({
  canStart: false, canComplete: false, canBlock: false, canCancel: false,
  canAssign: false, canEdit: false, canAttachments: false,
  canActivity: false, canApprovals: false,
});

const statusLabel = status => ({
  TODO: 'To do', IN_PROGRESS: 'In progress', BLOCKED: 'Blocked',
  DONE: 'Done', CANCELLED: 'Cancelled',
}[status] || status);

const duePhrase = (dueDate, todayISO) => {
  if (!dueDate) return 'Not set';
  if (!/^\d{4}-\d{2}-\d{2}$/.test(dueDate)
    || !/^\d{4}-\d{2}-\d{2}$/.test(todayISO || '')) return dueDate;
  const dueTime = Date.parse(dueDate + 'T00:00:00Z');
  const todayTime = Date.parse(todayISO + 'T00:00:00Z');
  if (!Number.isFinite(dueTime) || !Number.isFinite(todayTime)) return dueDate;
  const days = Math.round((dueTime - todayTime) / 86400000);
  if (days === 0) return 'Due today';
  if (days === 1) return 'Due tomorrow';
  if (days < 0) return 'Overdue ' + Math.abs(days) + (days === -1 ? ' day' : ' days');
  const formatter = new Intl.DateTimeFormat('en-ZA', {
    day: 'numeric', month: 'short',
    ...(dueDate.slice(0, 4) === todayISO.slice(0, 4) ? {} : { year: 'numeric' }),
    timeZone: 'UTC',
  });
  return 'Due ' + formatter.format(new Date(dueTime));
};

/**
 * @description Stateless Work Row for verified source-backed callers.
 * @param {object} props Data, actions and availability supplied by an authorized caller.
 */
export default function ProjectWorkRow({
  item, selected = false, density = 'comfortable', busy = false,
  priority = null,
  pendingStatus = null, todayISO, assigneeName,
  onToggleSelect, onOpen, onAssign, onEdit, onTransition, onComplete,
  onAttachments, onApprovals, onActivity, capabilities = NO_ACTION_CAPABILITIES,
}) {
  const displayName = item.assignee_principal_id && typeof assigneeName === 'function'
    ? assigneeName(item.assignee_principal_id) : null;
  const hasNamedContributor = typeof displayName === 'string' && displayName.trim().length > 0
    && !displayName.toLowerCase().includes('unavailable');
  const initials = hasNamedContributor
    ? displayName.trim().split(/\s+/).slice(0, 2).map(word => word[0]).join('').toUpperCase()
    : null;
  const identity = <span className="inline-flex min-w-0 items-center gap-2">
    <span data-assignee-avatar aria-hidden="true"
      className="inline-flex size-6 shrink-0 items-center justify-center rounded-full bg-slate-200 text-[10px] font-bold text-slate-800">
      {initials || <UserRound size={14}/>}
    </span>
    <span className="min-w-0 truncate">{displayName || 'Assigned contributor · name unavailable'}</span>
  </span>;
  return <tr key={item.task_id} data-task-id={item.task_id}
              aria-label={'Open work details: ' + item.title}
              tabIndex={0}
              onClick={event => {
                if (event.target.closest('button, a, input, select, textarea, details, summary')) return;
                onOpen(item, event.currentTarget);
              }}
              onKeyDown={event => {
                if (event.target !== event.currentTarget || event.altKey
                  || event.ctrlKey || event.metaKey || event.shiftKey) return;
                const key = event.key.toLowerCase();
                if (key === 'j' || key === 'k') {
                  event.preventDefault();
                  const rows = [...event.currentTarget.parentElement.querySelectorAll('tr[data-task-id]')];
                  const index = rows.indexOf(event.currentTarget);
                  rows[Math.min(rows.length - 1, Math.max(0,
                    index + (key === 'j' ? 1 : -1)))]?.focus();
                } else if (key === 'a' && !busy && capabilities?.canAssign === true
                  && !['DONE', 'CANCELLED'].includes(item.status)) {
                  event.preventDefault();
                  onAssign(item);
                } else if (key === 'c' && !busy && capabilities?.canComplete === true
                  && item.status === 'IN_PROGRESS') {
                  event.preventDefault();
                  onComplete(item);
                } else if (event.key === 'Enter') {
                  event.preventDefault();
                  onOpen(item, event.currentTarget);
                }
              }}
              aria-selected={selected}
              className={'cursor-pointer align-middle hover:bg-blue-50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-blue-700 '
                + (selected ? 'bg-blue-50 ' : 'bg-white ')
                + (density === 'compact' ? 'h-11' : 'h-14')}>
              <td className={density === 'compact' ? 'p-1.5' : 'p-2'}>
                <input type="checkbox" aria-label={'Select ' + item.title}
                  checked={selected}
                  onChange={event => onToggleSelect(item.task_id, event.target.checked)}/>
              </td>
              <td className={density === 'compact' ? 'p-2' : 'p-3'}>
                <div className="flex items-center gap-2 font-semibold text-slate-900">
                  {item.kind === 'MILESTONE' ? <Waypoints size={15}/> : <ClipboardList size={15}/>}
                  {['critical', 'high'].includes(priority) && <span
                    aria-label={priority === 'critical' ? 'Critical priority' : 'High priority'}
                    title={priority === 'critical' ? 'Critical priority' : 'High priority'}
                    className={'inline-block h-2 w-2 shrink-0 rounded-full '
                      + (priority === 'critical' ? 'bg-rose-700' : 'bg-amber-600')}/>}
                  <span className={'block min-w-0 truncate '
                    + (['DONE', 'CANCELLED'].includes(item.status)
                      ? 'text-slate-500 line-through' : '')}
                    title={item.title}>{item.title}</span>
                </div>
                <div className="mt-1 text-xs text-slate-600">
                  {item.kind === 'MILESTONE' ? 'Milestone' : item.parent_task_id ? 'Subtask' : 'Task'}
                  {item.depends_on.length > 0 ? ' · ' + item.depends_on.length + ' dependencies' : ''}
                </div>
                {item.description && <details className="mt-1 text-xs text-slate-700">
                  <summary className="cursor-pointer font-medium text-blue-800">Details</summary>
                  <p className="mt-2 whitespace-pre-wrap break-words">{item.description}</p>
                </details>}
              </td>
              <td className="p-3 text-slate-800">
                <span className={'inline-flex rounded-md px-2 py-1 text-xs font-semibold '
                  + ({ TODO: 'bg-slate-100 text-slate-800', IN_PROGRESS: 'bg-blue-50 text-blue-800',
                    BLOCKED: 'bg-amber-100 text-amber-900', DONE: 'bg-emerald-50 text-emerald-800',
                    CANCELLED: 'bg-slate-100 text-slate-600' })[pendingStatus !== null
                    ? pendingStatus : item.status]}>
                  {statusLabel(pendingStatus !== null ? pendingStatus : item.status)}
                  {pendingStatus !== null ? ' · pending' : ''}
                </span>
                {pendingStatus !== null && <span className="sr-only">
                  Verified status: {statusLabel(item.status)}.
                </span>}
                {pendingStatus !== null &&
                  <span role="status" className="mt-1 block text-xs font-semibold text-blue-800">
                    Updating to {statusLabel(pendingStatus)}…
                  </span>}
              </td>
              <td className="p-3 text-xs text-slate-700">
                {item.assignee_principal_id
                  ? capabilities?.canAssign === true && ['TODO', 'IN_PROGRESS', 'BLOCKED'].includes(item.status)
                    ? <button type="button" disabled={busy}
                      aria-label={'Reassign: ' + item.title}
                      className="text-xs font-semibold text-blue-800 underline underline-offset-2"
                      onClick={() => onAssign(item)}>
                      {identity}
                    </button>
                    : <span title="Verified exact-project contributor">{identity}</span>
                   : capabilities?.canAssign === true && ['TODO', 'IN_PROGRESS', 'BLOCKED'].includes(item.status) ?
                  <button type="button" disabled={busy}
                    className="text-xs font-semibold text-blue-800 underline underline-offset-2"
                    aria-label={'Assign: ' + item.title}
                    onClick={() => onAssign(item)}>Assign</button> : 'Not assigned'}
              </td>
              <td className="p-3 text-xs text-slate-700">
                <span title={item.due_date || undefined}
                  className={item.due_date && item.due_date < todayISO
                    && !['DONE', 'CANCELLED'].includes(item.status)
                    ? 'font-semibold text-rose-700' : ''}>
                  {duePhrase(item.due_date, todayISO)}
                </span>
              </td>
              <td className="p-3">
                <ProjectWorkRowActions item={item} busy={busy} {...(capabilities || NO_ACTION_CAPABILITIES)}
                  onTransition={onTransition}
                  onComplete={onComplete}
                  onEdit={onEdit}
                  onAssign={onAssign}
                  onAttachments={onAttachments}
                  onApprovals={onApprovals}
                  onActivity={onActivity}/>
              </td></tr>;
}

// ARTIFACT: ProjectWorkRow.jsx
// VERSION: v1.6.0-READABLE-DUE-WORK-SEMANTICS
// AUTHORITY BOUNDARY: EOS mutations, permissions and evidence owned by caller
// TENANT POSTURE: no browser-derived tenant or project scope
// FAIL-CLOSED POSTURE: provisional UI never establishes command commit
// FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
// END OF WILSY OS SOVEREIGN ARTIFACT
