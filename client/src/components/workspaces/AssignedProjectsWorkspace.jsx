/**
 * TITLE: WILSY OS Participant Projects and Daily Execution Workspace
 * VERSION: v1.2.0-NAMED-REVIEWER-DECISION-WORKSPACE
 * AUTHORITY: Python EOS participant-scoped Projects and notifications API.
 * EPITOME: Discover explicitly assigned projects, inspect work, act only on
 *          own delegated tasks, collaborate and acknowledge inbox signals.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/components/workspaces/AssignedProjectsWorkspace.jsx
 * COLLABORATION / OWNERSHIP: ProjectsWorkspace supplies navigation and exact
 *          authenticated session; EOS owns all source, task, IAM and receipts.
 * CERTIFICATION / UPDATE DATE: 2026-11-18
 * CHANGELOG: v1.2.0-NAMED-REVIEWER-DECISION-WORKSPACE exposes
 *          source-backed task approvals to current participants, allowing
 *          decisions only by the explicitly designated contributor reviewer.
 * CHANGELOG: v1.2.0-NAMED-REVIEWER-DECISION-WORKSPACE rejects
 *            impossible empty forward pages to prevent unverified project
 *            pagination evidence from controlling focused navigation.
 * CHANGELOG: v1.2.0-NAMED-REVIEWER-DECISION-WORKSPACE opens a
 *          specifically authorized project from Daily Attention even when
 *          it lies beyond the first page of participant project discovery.
 * CHANGELOG: v1.2.0-NAMED-REVIEWER-DECISION-WORKSPACE adds full-width
 *          participant project listing, selected task execution, conversations
 *          and recipient-only notification acknowledgement with verified EOS reads.
 * COMPLIANCE: AGENTS.md; POPIA section 19; GDPR Article 32; WCAG 2.2 AA.
 * SECURITY / PRIVACY POSTURE: No locally invented work, notifications,
 *          approval authority, participant privileges or completion state.
 * TENANT BOUNDARY: Every list/detail/command envelope verifies exact tenant,
 *          authenticated principal, project and corresponding task ID.
 * AUTHORITY BOUNDARY: UI buttons cannot grant IAM, participation or
 *          employment; EOS separately reauthorizes every participant command.
 * FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively.
 */
import React, { useCallback, useEffect, useRef, useState } from 'react';
import {
  ArrowLeft, Bell, Check, CheckCircle2, ClipboardList,
  LoaderCircle, MessageSquare, RefreshCw, ShieldCheck,
} from 'lucide-react';
import api from '../../services/api.js';
import ProjectTaskCommentsPanel from './ProjectTaskCommentsPanel.jsx';
import ProjectTaskApprovalsPanel from './ProjectTaskApprovalsPanel.jsx';

const PROJECT_ID = /^prj-[0-9a-f]{48}$/;
const TASK_ID = /^ptk-[0-9a-f]{48}$/;
const NOTIFICATION_ID = /^pnf-[0-9a-f]{48}$/;
const STATES = ['TODO', 'IN_PROGRESS', 'BLOCKED', 'DONE', 'CANCELLED'];
const TRANSITIONS = {
  TODO: ['IN_PROGRESS', 'BLOCKED', 'CANCELLED'],
  IN_PROGRESS: ['BLOCKED', 'DONE', 'CANCELLED'],
  BLOCKED: ['IN_PROGRESS', 'CANCELLED'],
  DONE: [], CANCELLED: [],
};
const caption = key => ({
  TODO: 'To do', IN_PROGRESS: 'In progress',
  BLOCKED: 'Blocked', DONE: 'Done', CANCELLED: 'Cancelled',
}[key] || key);

function checkAssignedProject(row, tenantId, principalId) {
  const project = row?.project;
  const participation = row?.participation;
  return Boolean(
    project && project.tenant_id === tenantId
    && PROJECT_ID.test(project.project_id)
    && typeof project.name === 'string'
    && participation && participation.tenant_id === tenantId
    && participation.project_id === project.project_id
    && participation.principal_id === principalId
    && participation.state === 'ACTIVE'
    && ['VIEWER', 'CONTRIBUTOR'].includes(participation.role)
    && Number.isSafeInteger(participation.revision)
    && /^[a-f0-9]{128}$/.test(participation.fingerprint || ''),
  );
}
function checkTask(task, tenantId, projectId) {
  return Boolean(
    task?.schema === 'wilsy.project.task.v1'
    && task.tenant_id === tenantId && task.project_id === projectId
    && TASK_ID.test(task.task_id) && STATES.includes(task.status)
    && typeof task.title === 'string'
    && typeof task.description === 'string'
    && Array.isArray(task.depends_on)
    && Number.isSafeInteger(task.revision)
    && /^[a-f0-9]{128}$/.test(task.fingerprint || ''),
  );
}
function checkNotice(item, tenantId, projectId, principalId) {
  return Boolean(
    item?.schema === 'wilsy.project.notification.v1'
    && item.tenant_id === tenantId && item.project_id === projectId
    && item.recipient_principal_id === principalId
    && NOTIFICATION_ID.test(item.notification_id)
    && TASK_ID.test(item.task_id)
    && ['number'].includes(typeof item.revision)
    && (item.revision === 1 || item.revision === 2)
    && (item.read_at === null || typeof item.read_at === 'string')
    && /^[a-f0-9]{128}$/.test(item.fingerprint || ''),
  );
}

/** @description Real participant workflow without any owner-role fallback. */
export default function AssignedProjectsWorkspace({
  tenantId, principalId, tenantHeaders, sessionScope, onBack,
  focusProjectId = null,
}) {
  const [projects, setProjects] = useState([]);
  const [projectOffset, setProjectOffset] = useState(0);
  const [projectHasMore, setProjectHasMore] = useState(false);
  const [listState, setListState] = useState('LOADING');
  const [selection, setSelection] = useState(null);
  const [work, setWork] = useState([]);
  const [notices, setNotices] = useState([]);
  const [participants, setParticipants] = useState([]);
  const [workState, setWorkState] = useState('LOADING');
  const [discussionTaskId, setDiscussionTaskId] = useState(null);
  const [approvalTaskId, setApprovalTaskId] = useState(null);
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);
  const sequence = useRef(0);
  const focusHandled = useRef(null);
  const command = useRef({ fingerprint: '', key: '' });
  const scope = [tenantId, principalId, sessionScope].join('\0');
  const currentScope = useRef(scope);
  currentScope.current = scope;
  const headers = tenantHeaders || {};

  const list = useCallback(async (offset = 0) => {
    const active = scope, request = ++sequence.current;
    setListState('LOADING');
    setError('');
    try {
      const { data } = await api.get('/projects/my-projects?limit=50&offset=' + offset, { headers });
      if (request !== sequence.current || currentScope.current !== active) return;
      if (
        data?.schema !== 'WILSY-PROJECT-MY-PROJECTS/V1'
        || data.tenant_id !== tenantId || data.principal_id !== principalId
        || data.limit !== 50 || data.offset !== offset
        || typeof data.has_more !== 'boolean'
        || !Array.isArray(data.items) || data.items.length > 50
        || data.items.some(row => !checkAssignedProject(row, tenantId, principalId))
        || new Set(data.items.map(row => row.project.project_id)).size !== data.items.length
        || (data.has_more && data.items.length === 0)
        || data.next_offset !== (data.has_more ? offset + data.items.length : null)
      ) throw new Error('ASSIGNED_PROJECT_SOURCE_INVALID');
      setProjects(data.items);
      setProjectOffset(offset);
      setProjectHasMore(data.has_more);
      setListState('READY');
    } catch (cause) {
      if (request !== sequence.current || currentScope.current !== active) return;
      setProjects([]);
      const status = cause?.response?.status;
      setListState(status === 403 || status === 401 ? 'DENIED' : 'UNAVAILABLE');
      setError(status === 403 ? 'EOS denied assigned project access.'
        : status === 401 ? 'Sign in to see assigned projects.'
          : 'Assigned projects could not be verified. Retry source read.');
    }
  }, [scope, tenantId, principalId, tenantHeaders]);

  useEffect(() => {
    sequence.current += 1;
    setProjects([]);
    setSelection(null);
    setWork([]);
    setNotices([]);
    setParticipants([]);
    setError('');
    focusHandled.current = null;
    command.current = { fingerprint: '', key: '' };
    void list(0);
    return () => { sequence.current += 1; };
  }, [scope, list]);

  const openProject = async row => {
    if (!checkAssignedProject(row, tenantId, principalId)) return;
    const active = scope;
    const request = ++sequence.current;
    const id = row.project.project_id;
    setSelection(row);
    setWorkState('LOADING');
    setWork([]);
    setNotices([]);
    setParticipants([]);
    setDiscussionTaskId(null);
    setApprovalTaskId(null);
    setError('');
    try {
      const prefix = '/projects/' + encodeURIComponent(id) + '/my-project';
      const [detail, tasks, inbox, members] = await Promise.all([
        api.get(prefix, { headers }),
        api.get(prefix + '/tasks?limit=50&offset=0', { headers }),
        api.get(prefix + '/notifications?limit=50&offset=0', { headers }),
        api.get(prefix + '/participants?limit=100&offset=0', { headers }),
      ]);
      if (request !== sequence.current || currentScope.current !== active) return;
      const checks = [tasks.data, inbox.data, members.data];
      const [taskData, noticeData, memberData] = checks;
      if (
        detail.data?.schema !== 'WILSY-PROJECT-PARTICIPANT-DETAIL/V1'
        || detail.data.tenant_id !== tenantId || detail.data.principal_id !== principalId
        || detail.data.project_id !== id
        || !checkAssignedProject({
          project: detail.data.project,
          participation: detail.data.participation,
        }, tenantId, principalId)
      ) throw new Error('ASSIGNED_PROJECT_DETAIL_INVALID');
      if (
        taskData?.schema !== 'WILSY-PROJECT-TASK-LIST/V1'
        || taskData.tenant_id !== tenantId || taskData.principal_id !== principalId
        || taskData.project_id !== id || taskData.limit !== 50 || taskData.offset !== 0
        || typeof taskData.has_more !== 'boolean'
        || !Array.isArray(taskData.items) || taskData.items.length > 50
        || taskData.items.some(task => !checkTask(task, tenantId, id))
      ) throw new Error('ASSIGNED_PROJECT_TASKS_INVALID');
      if (
        noticeData?.schema !== 'WILSY-PROJECT-NOTIFICATION-LIST/V1'
        || noticeData.tenant_id !== tenantId || noticeData.principal_id !== principalId
        || noticeData.project_id !== id || noticeData.limit !== 50 || noticeData.offset !== 0
        || typeof noticeData.has_more !== 'boolean'
        || !Array.isArray(noticeData.items) || noticeData.items.length > 50
        || noticeData.items.some(item => !checkNotice(item, tenantId, id, principalId))
      ) throw new Error('ASSIGNED_PROJECT_INBOX_INVALID');
      if (
        memberData?.schema !== 'WILSY-PROJECT-PARTICIPANT-LIST/V1'
        || memberData.tenant_id !== tenantId || memberData.principal_id !== principalId
        || memberData.project_id !== id || memberData.limit !== 100 || memberData.offset !== 0
        || !Array.isArray(memberData.items) || memberData.items.length > 100
        || memberData.items.some(item => (
          item.tenant_id !== tenantId || item.project_id !== id
          || item.state !== 'ACTIVE' || typeof item.principal_id !== 'string'
        ))
      ) throw new Error('ASSIGNED_PROJECT_MEMBERS_INVALID');
      setSelection({
        project: detail.data.project,
        participation: detail.data.participation,
      });
      setWork(taskData.items);
      setNotices(noticeData.items);
      setParticipants(memberData.items);
      setWorkState('READY');
    } catch (cause) {
      if (request !== sequence.current || currentScope.current !== active) return;
      setWork([]);
      setNotices([]);
      setParticipants([]);
      const status = cause?.response?.status;
      setWorkState(status === 401 || status === 403 || status === 404 ? 'DENIED' : 'UNAVAILABLE');
      setError(status === 403 || status === 404
        ? 'This assigned project is no longer authorized. Refresh your assignments.'
        : 'The project execution source could not be verified. Retry.');
    }
  };

  useEffect(() => {
    if (
      listState !== 'READY' || !focusProjectId
      || !PROJECT_ID.test(focusProjectId)
      || focusHandled.current === scope + ':' + focusProjectId
    ) return undefined;
    const active = scope;
    focusHandled.current = scope + ':' + focusProjectId;
    let live = true;
    const known = projects.find(row => row.project.project_id === focusProjectId);
    if (known) {
      void openProject(known);
    } else {
      // The source queue may contain a project beyond the first 50
      // participant assignments. Fetch only this exact participant detail.
      void api.get('/projects/' + encodeURIComponent(focusProjectId) + '/my-project', {
        headers,
      }).then(({ data }) => {
        if (!live || currentScope.current !== active) return;
        if (
          data?.schema !== 'WILSY-PROJECT-PARTICIPANT-DETAIL/V1'
          || data.tenant_id !== tenantId || data.principal_id !== principalId
          || data.project_id !== focusProjectId
          || !checkAssignedProject({
            project: data.project, participation: data.participation,
          }, tenantId, principalId)
        ) throw new Error('ASSIGNED_PROJECT_FOCUS_INVALID');
        void openProject({ project: data.project, participation: data.participation });
      }).catch(() => {
        if (live && currentScope.current === active) {
          setError('EOS could not verify this project focus. Refresh your assignments.');
        }
      });
    }
    return () => { live = false; };
  }, [scope, listState, focusProjectId, projects, tenantId, principalId, tenantHeaders]);

  const submit = async (fingerprint, action, confirm) => {
    if (busy || workState !== 'READY' || !selection) return;
    const active = scope, row = selection;
    if (!command.current.key || command.current.fingerprint !== fingerprint) {
      if (typeof globalThis.crypto?.randomUUID !== 'function') {
        setError('Cannot establish an idempotent command in this browser session.');
        return;
      }
      command.current = { fingerprint, key: globalThis.crypto.randomUUID() };
    }
    setBusy(true);
    setError('');
    try {
      const { data } = await action(command.current.key);
      if (currentScope.current !== active) return;
      if (!confirm(data, row.project.project_id)) {
        throw new Error('ASSIGNED_PROJECT_COMMAND_SOURCE_INVALID');
      }
      await openProject(row);
      if (currentScope.current === active) command.current = { fingerprint: '', key: '' };
    } catch (cause) {
      if (currentScope.current !== active) return;
      setError(cause?.response?.status === 409
        ? 'EOS detected a revision or dependency conflict. Refresh before retrying.'
        : 'EOS could not verify your command. Reconcile source state first.');
    } finally {
      if (currentScope.current === active) setBusy(false);
    }
  };

  const transition = (task, status) => {
    if (!selection || selection.participation.role !== 'CONTRIBUTOR'
      || task.assignee_principal_id !== principalId) return;
    const projectId = selection.project.project_id;
    const payload = { expected_revision: task.revision, status };
    const path = '/projects/' + encodeURIComponent(projectId)
      + '/my-project/tasks/' + encodeURIComponent(task.task_id) + '/transition';
    void submit(JSON.stringify(['transition', projectId, task.task_id, payload]),
      key => api.post(path, payload, { headers: { ...headers, 'Idempotency-Key': key } }),
      (data, verifiedProject) => data?.schema === 'WILSY-PROJECT-TASK-RESULT/V1'
        && data.tenant_id === tenantId && data.principal_id === principalId
        && data.project_id === verifiedProject
        && checkTask(data.task, tenantId, verifiedProject)
        && data.task.task_id === task.task_id,
    );
  };

  const markRead = item => {
    if (!selection || item.read_at !== null || item.revision !== 1) return;
    const projectId = selection.project.project_id;
    const payload = { expected_revision: item.revision };
    const path = '/projects/' + encodeURIComponent(projectId)
      + '/my-project/notifications/' + encodeURIComponent(item.notification_id) + '/read';
    void submit(JSON.stringify(['notification-read', projectId, item.notification_id]),
      key => api.post(path, payload, { headers: { ...headers, 'Idempotency-Key': key } }),
      (data, verifiedProject) => data?.schema === 'WILSY-PROJECT-NOTIFICATION-RESULT/V1'
        && data.tenant_id === tenantId && data.principal_id === principalId
        && data.project_id === verifiedProject
        && checkNotice(data.notification, tenantId, verifiedProject, principalId)
        && data.notification.notification_id === item.notification_id
        && data.notification.revision === 2,
    );
  };

  return <section className="wilsy-projects mx-auto w-full max-w-[1500px] px-3 pb-6 sm:px-5"
    data-assigned-projects data-source-state={listState}>
    <header className="wp-toolbar flex flex-wrap items-center justify-between gap-3 rounded-xl border border-slate-200 bg-white p-4">
      <div>
        <p className="wp-eyebrow">Projects &amp; delivery</p>
        <h1 className="wp-title">My assigned projects</h1>
        <p className="wp-subtitle">Only active projects explicitly assigned to your authenticated principal.</p>
      </div>
      <div className="flex flex-wrap gap-2">
        <button type="button" className="wp-button" onClick={onBack}><ArrowLeft size={15}/> All projects</button>
        <button type="button" className="wp-button" onClick={() => void list(projectOffset)}><RefreshCw size={15}/> Refresh</button>
      </div>
    </header>
    {listState === 'LOADING' && <p role="status" className="rounded-lg bg-white p-4 text-slate-700">Verifying current project participation…</p>}
    {(listState === 'DENIED' || listState === 'UNAVAILABLE') &&
      <p role="alert" className="rounded-lg border border-rose-200 bg-white p-4 text-rose-800">{error}</p>}
    {listState === 'READY' && <div className="wp-body" data-layout={selection ? 'detail' : 'list'}>
      <section aria-label="Assigned project list" className="wp-panel min-w-0 overflow-hidden rounded-xl border border-slate-200 bg-white">
        <ul className="divide-y divide-slate-200">
          {projects.map(row => <li key={row.project.project_id}>
            <button type="button" className="block w-full p-4 text-left hover:bg-blue-50"
              onClick={() => void openProject(row)} aria-current={selection?.project.project_id === row.project.project_id ? 'true' : undefined}>
              <strong className="block break-words text-slate-900">{row.project.name}</strong>
              <span className="mt-1 block text-xs text-slate-600">
                {row.participation.role === 'CONTRIBUTOR' ? 'Contributor' : 'Viewer'}
                {' · '}{row.project.status}
              </span>
            </button>
          </li>)}
          {projects.length === 0 && <li className="p-6 text-sm text-slate-600">
            EOS verified no active assignments for your current principal.
          </li>}
        </ul>
        {(projectOffset > 0 || projectHasMore) &&
          <nav aria-label="Assigned project pages" className="flex gap-2 border-t border-slate-200 p-3">
            <button type="button" className="wp-button" disabled={projectOffset === 0}
              onClick={() => void list(Math.max(0, projectOffset - 50))}>Previous</button>
            <button type="button" className="wp-button" disabled={!projectHasMore}
              onClick={() => void list(projectOffset + 50)}>Next</button>
          </nav>}
      </section>
      {selection && <aside className="wp-panel wp-detail min-w-0 rounded-xl border border-slate-200 bg-white p-4"
        aria-label="Assigned project execution">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <div>
            <h2 className="text-xl font-bold text-slate-900">{selection.project.name}</h2>
            <p className="mt-1 text-sm text-slate-600">
              <ShieldCheck className="mr-1 inline" size={14}/>
              {selection.participation.role} · {selection.project.status} · EOS current participation
            </p>
          </div>
          <button type="button" className="wp-button" disabled={busy}
            onClick={() => void openProject(selection)}><RefreshCw size={14}/> Refresh work</button>
        </div>
        {workState === 'LOADING' && <p role="status" className="mt-3 text-sm text-slate-600">
          <LoaderCircle size={14} className="mr-2 inline animate-spin"/> Verifying project execution…
        </p>}
        {(workState === 'DENIED' || workState === 'UNAVAILABLE') &&
          <p role="alert" className="mt-3 text-sm text-rose-700">{error}</p>}
        {workState === 'READY' && <>
          <section aria-label="Assigned project tasks" className="mt-4">
            <h3 className="mb-2 flex items-center gap-2 font-semibold text-slate-900">
              <ClipboardList size={15}/> Project tasks
            </h3>
            <div className="overflow-x-auto rounded-lg border border-slate-200" role="region" aria-label="Participant task table" tabIndex={0}>
              <table className="w-full min-w-[540px] border-collapse text-left text-sm">
                <thead className="bg-slate-100 text-xs text-slate-700">
                  <tr><th className="p-3">Task</th><th className="p-3">State</th><th className="p-3">Owner</th><th className="p-3">Action</th></tr>
                </thead>
                <tbody className="divide-y divide-slate-200">
                  {work.map(task => <tr key={task.task_id}>
                    <td className="p-3"><strong className="break-words text-slate-900">{task.title}</strong>
                      <p className="mt-1 break-words text-xs text-slate-500">{task.description}</p></td>
                    <td className="p-3 text-slate-700">{caption(task.status)}</td>
                    <td className="break-all p-3 text-xs text-slate-700">
                      {task.assignee_principal_id || 'Unassigned'}</td>
                    <td className="p-3"><div className="flex flex-wrap gap-1.5">
                      {selection.participation.role === 'CONTRIBUTOR'
                        && task.assignee_principal_id === principalId
                        && TRANSITIONS[task.status].map(next => <button type="button"
                          key={next} className="wp-button !min-h-8 !px-2 !py-1 !text-xs"
                          disabled={busy} onClick={() => transition(task, next)}>{caption(next)}</button>)}
                      <button type="button" className="wp-button !min-h-8 !px-2 !py-1 !text-xs"
                        onClick={() => setApprovalTaskId(value => value === task.task_id ? null : task.task_id)}>
                        <ClipboardList size={13}/> Approvals
                      </button>
                      <button type="button" className="wp-button !min-h-8 !px-2 !py-1 !text-xs"
                        onClick={() => setDiscussionTaskId(value => value === task.task_id ? null : task.task_id)}>
                        <MessageSquare size={13}/> Discuss
                      </button>
                    </div></td>
                  </tr>)}
                  {work.length === 0 && <tr><td colSpan={4} className="p-4 text-sm text-slate-600">
                    EOS verified no tasks on the current project page.
                  </td></tr>}
                </tbody>
              </table>
            </div>
          </section>
          {approvalTaskId && work.some(task => task.task_id === approvalTaskId) &&
            <ProjectTaskApprovalsPanel key={scope + approvalTaskId}
              tenantId={tenantId} projectId={selection.project.project_id}
              taskId={approvalTaskId} principalId={principalId}
              tenantHeaders={tenantHeaders} participantMode
              participants={participants}
              onClose={() => setApprovalTaskId(null)}/>}
          {discussionTaskId && work.some(task => task.task_id === discussionTaskId) &&
            <ProjectTaskCommentsPanel key={scope + discussionTaskId}
              tenantId={tenantId} projectId={selection.project.project_id}
              taskId={discussionTaskId} principalId={principalId}
              tenantHeaders={tenantHeaders} participantMode
              participants={participants}
              onClose={() => setDiscussionTaskId(null)}/>}
          <section className="mt-5 border-t border-slate-200 pt-4" aria-label="Project notifications">
            <h3 className="mb-3 flex items-center gap-2 font-semibold text-slate-900">
              <Bell size={15}/> Project notifications
              <span className="text-sm font-normal text-slate-600">
                {notices.filter(item => item.read_at === null).length} unread on this page
              </span>
            </h3>
            <ul className="divide-y divide-slate-200 rounded-lg border border-slate-200">
              {notices.map(item => <li key={item.notification_id}
                className="flex flex-wrap items-center justify-between gap-3 p-3">
                <div>
                  <p className="break-words text-sm font-medium text-slate-900">
                    Mention in a project task
                  </p>
                  <p className="break-all text-xs text-slate-600">
                    From {item.actor_principal_id} · Task {item.task_id}
                  </p>
                  <p className="text-xs text-slate-500">
                    {item.read_at ? 'Read' : 'Unread'} · {item.occurred_at}
                  </p>
                </div>
                {!item.read_at && <button type="button" className="wp-button"
                  disabled={busy} onClick={() => markRead(item)}>
                  <Check size={14}/> Mark read
                </button>}
              </li>)}
              {notices.length === 0 && <li className="p-4 text-sm text-slate-600">
                EOS verified no in-app notifications on this project page.
              </li>}
            </ul>
            <p className="mt-2 text-xs text-slate-600">
              These are durable in-app mention records, not email or push delivery receipts.
            </p>
          </section>
          {error && <p role="alert" className="mt-3 text-sm text-rose-700">{error}</p>}
        </>}
      </aside>}
    </div>}
  </section>;
}

// ARTIFACT: AssignedProjectsWorkspace.jsx
// VERSION: v1.2.0-NAMED-REVIEWER-DECISION-WORKSPACE
// AUTHORITY BOUNDARY: principal's projects/tasks/notifications, no owner IAM
// TENANT POSTURE: all read/write results exact principal, tenant and project
// FAIL-CLOSED POSTURE: missing, foreign, malformed, uncertain or stale deny
// FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
// END OF WILSY OS SOVEREIGN ARTIFACT
