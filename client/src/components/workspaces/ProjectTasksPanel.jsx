/**
 * TITLE: WILSY OS Project Work Execution Panel
 * VERSION: v1.5.0-ACCESSIBLE-WORK-CALENDAR
 * AUTHORITY: Python EOS Projects task and participant HTTP APIs exclusively.
 * EPITOME: Real task, subtask, milestone and dependency actions with durable
 *          EOS readback, selected project scope and no synthetic task state.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/components/workspaces/ProjectTasksPanel.jsx
 * COLLABORATION / OWNERSHIP: ProjectsWorkspace mounts the authorized owner
 *          detail; api.js supplies session transport; EOS owns task commands.
 * CERTIFICATION / UPDATE DATE: 2026-11-18
 * CHANGELOG: v1.5.0-ACCESSIBLE-WORK-CALENDAR adds accessible calendar
 *          triggers and local quick dates to create/edit without changing
 *          EOS task authority, schemas, idempotency or source readback.
 * CHANGELOG: v1.4.0-QUARANTINED-TASK-FILE-VIEW opens
 *          task-bound quarantined file evidence; no preview, download,
 *          scanner release or approval authority is created.
 * CHANGELOG: v1.5.0-ACCESSIBLE-WORK-CALENDAR lets the
 *          project owner request named task review through the shared
 *          canonical approval source, separately from discussion/task status.
 * CHANGELOG: v1.5.0-ACCESSIBLE-WORK-CALENDAR opens a selected task's
 *          source-backed immutable comment/mention thread without treating
 *          mentions as deliveries, approvals or task lifecycle commands.
 * CHANGELOG: v1.5.0-ACCESSIBLE-WORK-CALENDAR adds a
 *          single in-place owner task edit and reassignment form, using EOS
 *          current assignee choices, exact revision CAS and fresh readback.
 * CHANGELOG: v1.5.0-ACCESSIBLE-WORK-CALENDAR adds source-backed
 *          task pagination, status distribution, governed creation, milestone,
 *          dependency and assignment selectors and revisioned transitions.
 * COMPLIANCE: AGENTS.md; POPIA section 19; GDPR Article 32; WCAG 2.2 AA.
 * SECURITY / PRIVACY POSTURE: Text only, no HTML parsing, AI execution, bearer
 *          extraction, fabricated task metrics or inferred notifications.
 * TENANT BOUNDARY: Exact tenant, principal and project validated on every
 *          response; stale session results are ignored and discarded.
 * AUTHORITY BOUNDARY: UI actions do not grant contributor, employee or owner
 *          rights; EOS checks each mutation and recorded assignment.
 * FINANCIAL AUTHORITY BOUNDARY: Kennel EOS is the sole financial executor.
 */
import React, { useCallback, useEffect, useId, useRef, useState } from 'react';
import { CalendarDays, CheckCircle2, CirclePause, ClipboardList, LoaderCircle, Plus, RefreshCw, Waypoints } from 'lucide-react';
import api from '../../services/api.js';
import ProjectTaskCommentsPanel from './ProjectTaskCommentsPanel.jsx';
import ProjectTaskApprovalsPanel from './ProjectTaskApprovalsPanel.jsx';
import ProjectTaskAttachmentsPanel from './ProjectTaskAttachmentsPanel.jsx';

const LIST_SCHEMA = 'WILSY-PROJECT-TASK-LIST/V1';
const RESULT_SCHEMA = 'WILSY-PROJECT-TASK-RESULT/V1';
const PARTICIPANT_SCHEMA = 'WILSY-PROJECT-PARTICIPANT-LIST/V1';
const TASK_ID = /^ptk-[0-9a-f]{48}$/;
const STATUSES = ['TODO', 'IN_PROGRESS', 'BLOCKED', 'DONE', 'CANCELLED'];
const TRANSITIONS = {
  TODO: ['IN_PROGRESS', 'BLOCKED', 'CANCELLED'],
  IN_PROGRESS: ['BLOCKED', 'DONE', 'CANCELLED'],
  BLOCKED: ['IN_PROGRESS', 'CANCELLED'],
  DONE: [], CANCELLED: [],
};
const EMPTY = Object.freeze({
  kind: 'TASK', title: '', description: '', due_date: '',
  parent_task_id: '', assignee_principal_id: '', depends_on: [],
});
const label = value => ({
  TODO: 'To do', IN_PROGRESS: 'In progress', BLOCKED: 'Blocked',
  DONE: 'Done', CANCELLED: 'Cancelled',
}[value] || value);


/**
 * Calendar-backed EOS date-only proposal; no persisted state until readback.
 * @authority Dates are draft-only until exact-project EOS command verification.
 * @tenant Local input does not create tenant, identity or financial authority.
 * @failure Keyboard-native date input remains available without showPicker.
 */
function ProjectWorkDateField({ label: fieldLabel, value, onChange }) {
  const id = useId();
  const picker = useRef(null);
  const openCalendar = () => {
    const input = picker.current;
    if (!input) return;
    if (typeof input.showPicker === 'function') {
      try { input.showPicker(); return; } catch { /* Fall back to focus. */ }
    }
    input.focus();
  };
  const quickDate = days => {
    const date = new Date();
    date.setHours(12, 0, 0, 0);
    date.setDate(date.getDate() + days);
    const pad = n => String(n).padStart(2, '0');
    onChange(date.getFullYear() + '-' + pad(date.getMonth() + 1) + '-' + pad(date.getDate()));
  };
  const buttonStyle = 'rounded-md border border-slate-300 bg-white px-2.5 py-1.5 text-xs font-semibold text-slate-800 hover:bg-blue-50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-blue-700';
  return <div className="min-w-0">
    <label htmlFor={id} className="block text-sm font-semibold text-slate-800">{fieldLabel}</label>
    <div className="mt-1 flex min-w-0 items-stretch gap-2">
      <input ref={picker} id={id} type="date" aria-label={fieldLabel} value={value}
        onChange={event => onChange(event.target.value)}
        className="min-w-0 flex-1 rounded-lg border border-slate-300 bg-white p-2.5 text-sm font-normal text-slate-900"/>
      <button type="button" onClick={openCalendar} aria-label={'Open calendar for ' + fieldLabel.toLowerCase()}
        className="inline-flex min-h-11 min-w-11 items-center justify-center rounded-lg border border-blue-300 bg-white text-blue-800 hover:bg-blue-50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-700">
        <CalendarDays size={18} aria-hidden="true"/>
      </button>
    </div>
    <div className="mt-2 flex flex-wrap gap-2" role="group" aria-label={fieldLabel + ' quick dates'}>
      <button type="button" className={buttonStyle} onClick={() => quickDate(0)}>Today</button>
      <button type="button" className={buttonStyle} onClick={() => quickDate(1)}>Tomorrow</button>
      <button type="button" className={buttonStyle} onClick={() => quickDate(7)}>In 7 days</button>
      {value && <button type="button" className={buttonStyle} onClick={() => onChange('')}>Clear date</button>}
    </div>
  </div>;
}

function validTask(task, tenantId, projectId) {
  return Boolean(
    task && task.schema === 'wilsy.project.task.v1'
    && task.tenant_id === tenantId && task.project_id === projectId
    && TASK_ID.test(task.task_id)
    && (task.kind === 'TASK' || task.kind === 'MILESTONE')
    && STATUSES.includes(task.status)
    && typeof task.title === 'string' && task.title.length > 0
    && typeof task.description === 'string'
    && (task.assignee_principal_id === null || typeof task.assignee_principal_id === 'string')
    && (task.parent_task_id === null || TASK_ID.test(task.parent_task_id))
    && (task.due_date === null || /^\d{4}-\d{2}-\d{2}$/.test(task.due_date))
    && Array.isArray(task.depends_on)
    && task.depends_on.length <= 25 && task.depends_on.every(value => TASK_ID.test(value))
    && Number.isSafeInteger(task.revision) && task.revision >= 1
    && /^[a-f0-9]{128}$/.test(task.fingerprint || ''),
  );
}

function validList(data, tenantId, principalId, projectId, offset) {
  if (
    data?.schema !== LIST_SCHEMA || data.tenant_id !== tenantId
    || data.principal_id !== principalId || data.project_id !== projectId
    || data.limit !== 50 || data.offset !== offset
    || typeof data.has_more !== 'boolean' || !Array.isArray(data.items)
    || data.items.length > 50
    || data.items.some(item => !validTask(item, tenantId, projectId))
    || new Set(data.items.map(item => item.task_id)).size !== data.items.length
    || data.next_offset !== (data.has_more ? offset + data.items.length : null)
    || (data.has_more && data.items.length === 0)
  ) throw new Error('PROJECT_TASK_SOURCE_INVALID');
  return data;
}

function validParticipants(data, tenantId, principalId, projectId) {
  if (
    data?.schema !== PARTICIPANT_SCHEMA
    || data.tenant_id !== tenantId || data.principal_id !== principalId
    || data.project_id !== projectId || data.limit !== 100 || data.offset !== 0
    || !Array.isArray(data.items) || data.items.length > 100
    || typeof data.has_more !== 'boolean'
    || data.next_offset !== (data.has_more ? data.items.length : null)
    || data.items.some(item => (
      item.tenant_id !== tenantId || item.project_id !== projectId
      || item.state !== 'ACTIVE'
      || !['VIEWER', 'CONTRIBUTOR'].includes(item.role)
      || typeof item.principal_id !== 'string'
    ))
  ) throw new Error('PROJECT_PARTICIPANTS_SOURCE_INVALID');
  return data;
}

/** @description Display one exact-project task/participant workflow, never local truth. */
export default function ProjectTasksPanel({
  projectId, tenantId, principalId, tenantHeaders,
}) {
  const [items, setItems] = useState([]);
  const [participants, setParticipants] = useState([]);
  const [participantHasMore, setParticipantHasMore] = useState(false);
  const [state, setState] = useState('LOADING');
  const [offset, setOffset] = useState(0);
  const [hasMore, setHasMore] = useState(false);
  const [draft, setDraft] = useState({ ...EMPTY });
  const [creating, setCreating] = useState(false);
  const [editor, setEditor] = useState(null);
  const [discussionTaskId, setDiscussionTaskId] = useState(null);
  const [approvalTaskId, setApprovalTaskId] = useState(null);
  const [attachmentTaskId, setAttachmentTaskId] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const generation = useRef(0);
  const command = useRef({ fingerprint: '', key: '' });
  const scope = [tenantId, principalId, projectId].join('\0');
  const currentScope = useRef(scope);
  currentScope.current = scope;
  const root = '/projects/' + encodeURIComponent(projectId);
  const headers = tenantHeaders || {};

  const load = useCallback(async (nextOffset = 0) => {
    const request = ++generation.current;
    const active = scope;
    setState(previous => previous === 'READY' ? 'REFRESHING' : 'LOADING');
    setError('');
    try {
      const [tasks, people] = await Promise.all([
        api.get(root + '/tasks?limit=50&offset=' + nextOffset, { headers }),
        api.get(root + '/participants?limit=100&offset=0', { headers }),
      ]);
      if (request !== generation.current || currentScope.current !== active) return false;
      const verified = validList(tasks.data, tenantId, principalId, projectId, nextOffset);
      const eligible = validParticipants(people.data, tenantId, principalId, projectId);
      setItems(verified.items);
      setHasMore(verified.has_more);
      setOffset(nextOffset);
      setParticipants(eligible.items.filter(item => item.role === 'CONTRIBUTOR'));
      setParticipantHasMore(eligible.has_more);
      setState('READY');
      return true;
    } catch (cause) {
      if (request !== generation.current || currentScope.current !== active) return false;
      setItems([]);
      setParticipants([]);
      setParticipantHasMore(false);
      setHasMore(false);
      const status = cause?.response?.status;
      setError(status === 401 ? 'Authentication required for project work.'
        : status === 403 ? 'EOS denied project work access.'
          : 'Project work could not be verified from EOS. Retry the source read.');
      setState(status === 401 || status === 403 ? 'DENIED' : 'UNAVAILABLE');
      return false;
    }
  }, [scope, root, tenantId, principalId, projectId, tenantHeaders]);

  useEffect(() => {
    generation.current += 1;
    setItems([]);
    setParticipants([]);
    setOffset(0);
    setHasMore(false);
    setCreating(false);
    setEditor(null);
    setDiscussionTaskId(null);
    setApprovalTaskId(null);
    setAttachmentTaskId(null);
    setDraft({ ...EMPTY });
    setError('');
    command.current = { fingerprint: '', key: '' };
    void load(0);
    return () => { generation.current += 1; };
  }, [scope, load]);

  const retainKey = fingerprint => {
    if (command.current.fingerprint !== fingerprint || !command.current.key) {
      if (typeof globalThis.crypto?.randomUUID !== 'function') {
        throw new Error('PROJECT_TASK_IDEMPOTENCY_UNAVAILABLE');
      }
      command.current = { fingerprint, key: globalThis.crypto.randomUUID() };
    }
    return command.current.key;
  };

  const execute = async (fingerprint, action, expectedTaskId = null) => {
    if (busy || state !== 'READY') return;
    const active = scope;
    setBusy(true);
    setError('');
    try {
      const idempotencyKey = retainKey(fingerprint);
      const { data } = await action(idempotencyKey);
      if (currentScope.current !== active) return;
      if (
        data?.schema !== RESULT_SCHEMA
        || data.tenant_id !== tenantId || data.principal_id !== principalId
        || data.project_id !== projectId
        || !validTask(data.task, tenantId, projectId)
        || (expectedTaskId !== null && data.task.task_id !== expectedTaskId)
      ) throw new Error('PROJECT_TASK_RESULT_INVALID');
      // Never announce a command's success before a fresh EOS list confirms it.
      const fresh = await load(0);
      if (!fresh || currentScope.current !== active) return;
      command.current = { fingerprint: '', key: '' };
      setDraft({ ...EMPTY });
      setCreating(false);
      setEditor(null);
    } catch (cause) {
      if (currentScope.current !== active) return;
      const status = cause?.response?.status;
      setError(status === 403 ? 'EOS denied this task command.'
        : status === 404 ? 'The work item is not visible within this project.'
          : status === 409 ? 'Project work has changed or a dependency is incomplete. Refresh before retrying.'
            : 'EOS has not verified this task command. Reconcile source state before retrying.');
    } finally {
      if (currentScope.current === active) setBusy(false);
    }
  };

  const create = event => {
    event.preventDefault();
    const title = draft.title.trim();
    if (!title || title.length > 180 || participantHasMore && draft.assignee_principal_id) return;
    const body = {
      kind: draft.kind, title, description: draft.description.trim(),
      due_date: draft.due_date || null,
      assignee_principal_id: draft.assignee_principal_id || null,
      parent_task_id: draft.kind === 'MILESTONE' ? null : draft.parent_task_id || null,
      depends_on: draft.depends_on,
    };
    void execute(JSON.stringify(['create', body]), key =>
      api.post(root + '/tasks', body, {
        headers: { ...headers, 'Idempotency-Key': key },
      }),
    );
  };

  const revise = event => {
    event.preventDefault();
    if (!editor || !editor.title.trim()) return;
    const body = {
      expected_revision: editor.revision,
      title: editor.title.trim(),
      description: editor.description.trim(),
      due_date: editor.due_date || null,
      assignee_principal_id: editor.assignee_principal_id || null,
    };
    void execute(JSON.stringify(['revise', editor.task_id, body]), key =>
      api.patch(root + '/tasks/' + encodeURIComponent(editor.task_id), body, {
        headers: { ...headers, 'Idempotency-Key': key },
      }), editor.task_id,
    );
  };

  const transition = (item, status) => {
    const body = { expected_revision: item.revision, status };
    void execute(JSON.stringify(['transition', item.task_id, body]), key =>
      api.post(root + '/tasks/' + encodeURIComponent(item.task_id) + '/transition',
        body, { headers: { ...headers, 'Idempotency-Key': key } }),
      item.task_id,
    );
  };

  const counts = STATUSES.map(status => ({
    status, count: items.filter(item => item.status === status).length,
  }));
  const chartTotal = items.length;

  return <section className="wp-project-tasks mt-5 border-t border-slate-200 pt-4" aria-label="Project work execution">
    <div className="flex flex-wrap items-center justify-between gap-3">
      <div>
        <h3 className="text-base font-semibold text-slate-900">Project work</h3>
        <p className="mt-1 text-xs text-slate-600">Tasks, milestones, subtask dependencies and accountable assignments from EOS.</p>
      </div>
      <div className="flex flex-wrap gap-2">
        <button type="button" className="wp-button" disabled={busy} onClick={() => void load(offset)}>
          <RefreshCw size={14}/> Refresh work
        </button>
        {state === 'READY' && <button type="button" className="wp-button wp-button-primary"
          disabled={busy} onClick={() => setCreating(value => !value)}>
          <Plus size={14}/> {creating ? 'Close editor' : 'Create task'}
        </button>}
      </div>
    </div>
    {(state === 'LOADING' || state === 'REFRESHING') &&
      <p role="status" className="mt-3 flex items-center gap-2 text-sm text-slate-600">
        <LoaderCircle size={15} className="animate-spin"/> Verifying project tasks…
      </p>}
    {(state === 'DENIED' || state === 'UNAVAILABLE') &&
      <p role="alert" className="mt-3 text-sm text-rose-700">{error}</p>}
    {state === 'READY' && <>
      <div className="mt-4 grid grid-cols-2 gap-2 sm:grid-cols-5" aria-label="Verified current task page status">
        {counts.map(({ status, count }) =>
          <div key={status} className="rounded-lg border border-slate-200 bg-slate-50 p-2.5">
            <div className="text-xs text-slate-600">{label(status)}</div>
            <strong className="mt-1 block text-lg tabular-nums text-slate-900">{count}</strong>
          </div>)}
      </div>
      <div role="img" aria-label={'Current task page: ' + counts.map(({ status, count }) =>
        label(status) + ' ' + count).join(', ')}
        className="mt-2 flex h-2 w-full overflow-hidden rounded-full bg-slate-100">
        {counts.filter(({ count }) => count).map(({ status, count }) =>
          <span key={status} title={label(status) + ': ' + count}
            data-status={status} style={{
              width: (chartTotal ? 100 * count / chartTotal : 0) + '%',
              background: ({
                TODO: '#94a3b8', IN_PROGRESS: '#2563eb', BLOCKED: '#c2410c',
                DONE: '#15803d', CANCELLED: '#64748b',
              })[status],
            }}/>)}
      </div>
      <p className="mt-1 text-xs text-slate-500">Distribution covers this verified task page, not every project task.</p>
      {creating && <form onSubmit={create} className="mt-4 space-y-3 rounded-xl border border-blue-200 bg-blue-50/50 p-3">
        <h4 className="text-sm font-bold text-slate-900">Create EOS work item</h4>
        <p className="text-xs text-slate-600">{draft.kind === 'MILESTONE'
          ? 'Milestone — define a delivery checkpoint and choose its target date.'
          : 'Task — define accountable work, its due date and dependencies.'}</p>
        <div className="grid gap-3 sm:grid-cols-2">
          <label className="block text-sm font-semibold text-slate-800">Work type
            <select className="mt-1 w-full rounded-lg border border-slate-300 bg-white p-2.5 text-sm font-normal text-slate-900"
              value={draft.kind} onChange={event => setDraft(value => ({
                ...value, kind: event.target.value,
                parent_task_id: event.target.value === 'MILESTONE' ? '' : value.parent_task_id,
              }))}>
              <option value="TASK">Task or subtask</option>
              <option value="MILESTONE">Milestone</option>
            </select>
          </label>
          <ProjectWorkDateField label="Task due date" value={draft.due_date}
            onChange={date => setDraft(previous => ({ ...previous, due_date: date }))}/>
        </div>
        <label className="block text-sm font-semibold text-slate-800">Task title
          <input required maxLength={180} value={draft.title} onChange={event => setDraft(value => ({
            ...value, title: event.target.value,
          }))} placeholder="Deliverable and action" className="mt-1 w-full rounded-lg border border-slate-300 bg-white p-2.5 text-sm font-normal text-slate-900"/>
        </label>
        <label className="block text-sm font-semibold text-slate-800">Description
          <textarea rows={3} maxLength={5000} value={draft.description}
            onChange={event => setDraft(value => ({ ...value, description: event.target.value }))}
            className="mt-1 w-full rounded-lg border border-slate-300 bg-white p-2.5 text-sm font-normal text-slate-900"/>
        </label>
        <div className="grid gap-3 sm:grid-cols-2">
          <label className="block text-sm font-semibold text-slate-800">Assign to
            <select aria-label="Task assignee" value={draft.assignee_principal_id}
              onChange={event => setDraft(value => ({ ...value, assignee_principal_id: event.target.value }))}
              className="mt-1 w-full rounded-lg border border-slate-300 bg-white p-2.5 text-sm font-normal text-slate-900">
              <option value="">Unassigned</option>
              {participants.map(person => <option key={person.principal_id} value={person.principal_id}>
                {person.principal_id}
              </option>)}
            </select>
          </label>
          <label className="block text-sm font-semibold text-slate-800">Parent task
            <select aria-label="Parent task" disabled={draft.kind === 'MILESTONE'}
              value={draft.kind === 'MILESTONE' ? '' : draft.parent_task_id}
              onChange={event => setDraft(value => ({ ...value, parent_task_id: event.target.value }))}
              className="mt-1 w-full rounded-lg border border-slate-300 bg-white p-2.5 text-sm font-normal text-slate-900">
              <option value="">Top-level work</option>
              {items.filter(item => item.kind === 'TASK'
                && !['DONE', 'CANCELLED'].includes(item.status)).map(item =>
                <option key={item.task_id} value={item.task_id}>{item.title}</option>)}
            </select>
          </label>
        </div>
        <fieldset className="rounded-lg border border-slate-200 p-3">
          <legend className="px-1 text-sm font-semibold text-slate-800">Depends on (verified current page)</legend>
          <p className="mb-2 text-xs text-slate-600">Choose predecessor tasks that must reach Done before this item can be completed.</p>
          {items.length === 0 && <p className="text-xs text-slate-600">No available predecessors on this page.</p>}
          <div className="grid max-h-36 gap-2 overflow-auto sm:grid-cols-2">
            {items.filter(item => item.status !== 'CANCELLED').map(item =>
              <label key={item.task_id} className="flex items-center gap-2 text-xs text-slate-800">
                <input type="checkbox" checked={draft.depends_on.includes(item.task_id)}
                  disabled={!draft.depends_on.includes(item.task_id) && draft.depends_on.length >= 25}
                  onChange={event => setDraft(value => ({
                    ...value, depends_on: event.target.checked
                      ? [...value.depends_on, item.task_id]
                      : value.depends_on.filter(id => id !== item.task_id),
                  }))}/>
                <span className="break-words">{item.title}</span>
              </label>)}
          </div>
        </fieldset>
        {participantHasMore && <p className="text-xs text-amber-800">Only the first verified participant page is selectable. Further assignments require a complete directory read.</p>}
        <button type="submit" disabled={busy || !draft.title.trim()}
          className="wp-button wp-button-primary">
          <Plus size={14}/> Save work to EOS
        </button>
      </form>}
      {editor && <form onSubmit={revise} className="mt-4 space-y-3 rounded-xl border border-blue-200 bg-blue-50/50 p-3"
        aria-label="Edit project task">
        <div className="flex items-center justify-between gap-2">
          <h4 className="text-sm font-bold text-slate-900">Edit source task · revision {editor.revision}</h4>
          <button type="button" disabled={busy} className="wp-button"
            onClick={() => setEditor(null)}>Cancel edit</button>
        </div>
        <label className="block text-sm font-semibold text-slate-800">Work title
          <input aria-label="Edit task title" required maxLength={180} value={editor.title}
            onChange={event => setEditor(value => ({ ...value, title: event.target.value }))}
            className="mt-1 w-full rounded-lg border border-slate-300 bg-white p-2.5 text-sm font-normal text-slate-900"/>
        </label>
        <label className="block text-sm font-semibold text-slate-800">Description
          <textarea aria-label="Edit task description" rows={3} maxLength={5000} value={editor.description}
            onChange={event => setEditor(value => ({ ...value, description: event.target.value }))}
            className="mt-1 w-full rounded-lg border border-slate-300 bg-white p-2.5 text-sm font-normal text-slate-900"/>
        </label>
        <div className="grid gap-3 sm:grid-cols-2">
          <ProjectWorkDateField label="Edit task due date" value={editor.due_date}
            onChange={date => setEditor(previous => ({ ...previous, due_date: date }))}/>
          <label className="block text-sm font-semibold text-slate-800">Assigned contributor
            <select aria-label="Reassign task" value={editor.assignee_principal_id}
              onChange={event => setEditor(value => ({ ...value, assignee_principal_id: event.target.value }))}
              className="mt-1 w-full rounded-lg border border-slate-300 bg-white p-2.5 text-sm font-normal text-slate-900">
              <option value="">Unassigned</option>
              {participants.map(person => <option key={person.principal_id} value={person.principal_id}>
                {person.principal_id}
              </option>)}
              {editor.assignee_principal_id && !participants.some(person =>
                person.principal_id === editor.assignee_principal_id) &&
                <option value={editor.assignee_principal_id} disabled>
                  Current assignee not on verified page — choose a current contributor
                </option>}
            </select>
          </label>
        </div>
        <p className="text-xs text-slate-600">Parent, predecessors and milestone type remain immutable. Reassignment requires a current exact-project Contributor.</p>
        <button type="submit" className="wp-button wp-button-primary"
          disabled={busy || !editor.title.trim() || Boolean(
            editor.assignee_principal_id && !participants.some(person =>
              person.principal_id === editor.assignee_principal_id))}>
          Save audited task revision
        </button>
      </form>}
      <div className="mt-4 overflow-x-auto rounded-xl border border-slate-200" role="region" aria-label="Verified project tasks" tabIndex={0}>
        <table className="w-full min-w-[580px] border-collapse text-left text-sm">
          <thead className="bg-slate-100 text-xs font-bold text-slate-700">
            <tr><th scope="col" className="p-3">Work item</th><th scope="col" className="p-3">Status</th>
              <th scope="col" className="p-3">Assignee</th><th scope="col" className="p-3">Due</th>
              <th scope="col" className="p-3">Lifecycle action</th></tr>
          </thead>
          <tbody className="divide-y divide-slate-200">
            {items.map(item => <tr key={item.task_id} data-task-id={item.task_id} className="bg-white align-top">
              <td className="p-3"><div className="flex items-center gap-2 font-semibold text-slate-900">
                {item.kind === 'MILESTONE' ? <Waypoints size={15}/> : <ClipboardList size={15}/>}
                <span className="break-words">{item.title}</span></div>
                <p className="mt-1 whitespace-pre-wrap break-words text-xs text-slate-600">{item.description}</p>
                <div className="mt-1 text-xs text-slate-500">
                  {item.kind === 'MILESTONE' ? 'Milestone' : item.parent_task_id ? 'Subtask' : 'Task'}
                  {item.depends_on.length > 0 ? ' · ' + item.depends_on.length + ' dependencies' : ''}
                  {' · revision ' + item.revision}
                </div></td>
              <td className="p-3 text-slate-800">{label(item.status)}</td>
              <td className="break-all p-3 text-xs text-slate-700">{item.assignee_principal_id || 'Unassigned'}</td>
              <td className="p-3 text-xs text-slate-700">{item.due_date || 'Not set'}</td>
              <td className="p-3">
                <div className="flex flex-wrap gap-1.5">
                  {TRANSITIONS[item.status].map(next =>
                    <button type="button" key={next} disabled={busy}
                      onClick={() => transition(item, next)}
                      className="wp-button !min-h-8 !px-2 !py-1 !text-xs">
                      {next === 'DONE' ? <CheckCircle2 size={13}/> : next === 'BLOCKED' ? <CirclePause size={13}/> : null}
                      {label(next)}
                    </button>)}
                  {TRANSITIONS[item.status].length > 0 &&
                    <button type="button" className="wp-button !min-h-8 !px-2 !py-1 !text-xs"
                      disabled={busy} onClick={() => {
                        setCreating(false);
                        setEditor({
                          task_id: item.task_id, revision: item.revision,
                          title: item.title, description: item.description,
                          due_date: item.due_date || '',
                          assignee_principal_id: item.assignee_principal_id || '',
                        });
                      }}>Edit work</button>}
                  <button type="button" disabled={busy}
                    onClick={() => setAttachmentTaskId(current => current === item.task_id ? null : item.task_id)}
                    className="wp-button !min-h-8 !px-2 !py-1 !text-xs">
                    Attachments
                  </button>
                  <button type="button" disabled={busy}
                    onClick={() => setApprovalTaskId(current => current === item.task_id ? null : item.task_id)}
                    className="wp-button !min-h-8 !px-2 !py-1 !text-xs">
                    Approvals
                  </button>
                  <button type="button" disabled={busy}
                    onClick={() => setDiscussionTaskId(current => current === item.task_id ? null : item.task_id)}
                    className="wp-button !min-h-8 !px-2 !py-1 !text-xs">
                    Discuss
                  </button>
                  {TRANSITIONS[item.status].length === 0 && <span className="text-xs text-slate-500">Terminal state</span>}
                </div>
              </td></tr>)}
            {items.length === 0 && <tr><td colSpan={5} className="p-6 text-center text-sm text-slate-600">
              EOS verified no tasks on this page. Create work to begin execution.
            </td></tr>}
          </tbody>
        </table>
      </div>
      {attachmentTaskId && items.some(item => item.task_id === attachmentTaskId) &&
        <ProjectTaskAttachmentsPanel key={[scope, attachmentTaskId].join(':')}
          tenantId={tenantId} projectId={projectId} principalId={principalId}
          taskId={attachmentTaskId} tenantHeaders={tenantHeaders}
          onClose={() => setAttachmentTaskId(null)}/>}
      {approvalTaskId && items.some(item => item.task_id === approvalTaskId) &&
        <ProjectTaskApprovalsPanel key={[scope, approvalTaskId].join(':')}
          tenantId={tenantId} projectId={projectId} principalId={principalId}
          taskId={approvalTaskId} participants={participants}
          tenantHeaders={tenantHeaders}
          onClose={() => setApprovalTaskId(null)}/>}
      {discussionTaskId && items.some(item => item.task_id === discussionTaskId) &&
        <ProjectTaskCommentsPanel key={[scope, discussionTaskId].join(':')}
          tenantId={tenantId} projectId={projectId} principalId={principalId}
          taskId={discussionTaskId} participants={participants}
          tenantHeaders={tenantHeaders}
          onClose={() => setDiscussionTaskId(null)}/>}
      {(hasMore || offset > 0) && <nav className="mt-3 flex items-center justify-between gap-2" aria-label="Task pages">
        <button type="button" className="wp-button" disabled={busy || offset === 0}
          onClick={() => void load(Math.max(0, offset - 50))}>Previous work</button>
        <span className="text-xs text-slate-600">Page {Math.floor(offset / 50) + 1}</span>
        <button type="button" className="wp-button" disabled={busy || !hasMore}
          onClick={() => void load(offset + 50)}>Next work</button>
      </nav>}
    </>}
    {state === 'READY' && error && <p role="alert" className="mt-3 text-sm text-rose-700">{error}</p>}
  </section>;
}

// ARTIFACT: ProjectTasksPanel.jsx
// VERSION: v1.5.0-ACCESSIBLE-WORK-CALENDAR
// AUTHORITY BOUNDARY: EOS-verified owner task commands; no local state authority
// TENANT POSTURE: exact session tenant/principal/project readback, no fallback
// FAIL-CLOSED POSTURE: invalid data, denied commands and uncertain source stay visible
// FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
// END OF WILSY OS SOVEREIGN ARTIFACT
