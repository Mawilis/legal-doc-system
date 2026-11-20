/**
 * TITLE: WILSY OS Project Work Execution Panel
 * VERSION: v1.32.0-SELECTED-TASK-AI-LOCATOR-HANDOFF
 * AUTHORITY: Python EOS Projects task and participant HTTP APIs exclusively.
 * EPITOME: Real task, subtask, milestone and dependency actions with durable
 *          EOS readback, selected project scope and no synthetic task state.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/components/workspaces/ProjectTasksPanel.jsx
 * COLLABORATION / OWNERSHIP: ProjectsWorkspace mounts the authorized owner
 *          detail; api.js supplies session transport; EOS owns task commands.
 * CERTIFICATION / UPDATE DATE: 2026-11-19
 * COMPLIANCE: AGENTS.md; POPIA section 19; GDPR Article 32; WCAG 2.2 AA.
 * SECURITY / PRIVACY POSTURE: Text only, no HTML parsing, AI execution, bearer
 *          extraction, fabricated task metrics or inferred notifications.
 * TENANT BOUNDARY: Exact tenant, principal and project validated on every
 *          response; stale session results are ignored and discarded.
 * AUTHORITY BOUNDARY: UI actions do not grant contributor, employee or owner
 *          rights; EOS checks each mutation and recorded assignment.
 * FINANCIAL AUTHORITY BOUNDARY: Kennel EOS is the sole financial executor.
 * CHANGELOG: v1.32.0-SELECTED-TASK-AI-LOCATOR-HANDOFF offers a direct governed task
 *          evidence handoff after confirmed create and fresh EOS list
 *          readback, never before a durable task identifier exists.
 * CHANGELOG: v1.30.0-CONTRIBUTOR-GOVERNED-ATTACHMENT-ENTRY makes upload available to the
 *          EOS-verified current contributor in task attachment actions,
 *          while owner-only users remain read-only. Uploads still use
 *          contributor IAM, independent scan quarantine and EOS readback.
 * CHANGELOG: v1.29.0-GROUPED-PROJECT-WORK-ROWS groups the current
 *          EOS-verified work page by lifecycle, work type or named
 *          contributor without inventing cross-page aggregates or groups.
 * CHANGELOG: v1.28.0-INLINE-ACTIVITY-AND-PROJECT-NOTES brings source-backed task discussion and
 *          project-wide governed notes into Activity list, without task
 *          navigation or inventing linked note counts and authorities.
 * CHANGELOG: v1.27.0-EXACT-ASSIGNMENT-CAPABILITY-GATE validates assignment-only
 *          submissions against canAssign and general revisions against
 *          canEdit, without granting any new EOS update permission.
 * CHANGELOG: v1.26.0-ACCESSIBLE-WORK-ERROR-TOAST presents
 *          a dismissible role-alert error on failed task commands, without
 *          faking rollback or exposing backend error payloads.
 * CHANGELOG: v1.25.1-SEALED-SECONDARY-WORK-CONTROLS hides
 *          checklist mutation shortcuts and disables stale editor submits
 *          unless the independently verified exact-project update permission
 *          remains active.
 * CHANGELOG: v1.25.0-VERIFIED-WORK-ACTION-PERMISSIONS requires
 *          exact-tenant EOS update-authority before showing task writes;
 *          denied or unavailable capabilities preserve read-only tasks.
 * CHANGELOG: v1.24.0-REUSABLE-WORK-ROW-COMPOSITION delegates the
 *          verified row to a reusable stateless component, retaining EOS
 *          source authority and exact-project command handlers in this panel.
 * CHANGELOG: v1.23.0-OPTIMISTIC-PENDING-STATUS immediately projects
 *          a clearly marked provisional status chip, retains verified status
 *          separately and reverts without local business truth on EOS failure.
 *          The grid exposes explicit accessible selection and density.
 * CHANGELOG: v1.22.1-ASSIGN-ACTION-HANDOFF wires explicit work
 *          assignment to the compact exact-project contributor picker.
 * CHANGELOG: v1.22.0-SELECTABLE-DENSITY-WORK-ROWS adds source-scoped
 *          selection, accessible work-row checkboxes, and local density.
 *          Selection does not invent or execute bulk EOS commands.
 * CHANGELOG: v1.21.1-REFRESH-QUEUE-CONTINUITY retains the already
 *          verified task queue and pending-action cue during independent
 *          refresh; fresh EOS readback alone changes work status.
 * CHANGELOG: v1.21.0-PENDING-TRANSITION-PROJECTION shows a bounded
 *          immediate pending transition cue while EOS verifies the command;
 *          only a fresh readback changes task status, and failed commands
 *          remove the cue without inventing lifecycle truth.
 * CHANGELOG: v1.20.1-INLINE-REASSIGN-CONTROL makes the current
 *          contributor an action for active work and prevents no-op
 *          assignment revisions without altering source ownership semantics.
 * CHANGELOG: v1.20.0-CONTRIBUTOR-ASSIGNMENT-SHEET lets Assign/Reassign
 *          open a compact contributor picker instead of the entire editor,
 *          preserving exact-project authorization and revisioned EOS readback.
 * CHANGELOG: v1.19.0-FOCUSED-WORK-KEYBOARD-ACTIONS introduces focused
 *          work-row J/K navigation, A edit/assign and C guarded completion
 *          attestation, never global hotkeys or unverified EOS mutations.
 * CHANGELOG: v1.18.2-CONSTITUTIONAL-HEADER-FIRST places all authority,
 *          privacy and tenant fields ahead of historical changelogs within
 *          the certified 100-line header inspection boundary.
 * CHANGELOG: v1.18.1-HEADER-GOVERNANCE-PLACEMENT keeps mandatory financial
 *          authority metadata within the repository integrity guard's first
 *          100 header lines, preserving all task and filter behaviours.
 * CHANGELOG: v1.18.0-PROJECT-MY-WORK-FILTER introduces an explicit
 *          current-principal task filter over the exact EOS-verified page,
 *          with accurate page scope, no client-assumed assignment authority,
 *          and automatic reset on principal/project scope changes.
 * CHANGELOG: v1.17.1-READABLE-ASSIGNEE-EDITOR shows a verified
 *          contributor name in the edit/assign selector instead of an
 *          opaque principal ID; submitted identity and authority unchanged.
 * CHANGELOG: v1.17.0-SELECTED-WORK-CONTEXT-DRAWER makes
 *          every verified work row directly open a focused, responsive
 *          task detail drawer, with one source truth and governed contextual
 *          actions. Esc restores focus; long content no longer fills rows.
 * CHANGELOG: v1.16.1-MILESTONE-COMPLETION-ATTESTATION routes
 *          both task and milestone primary Complete actions through
 *          the same explicit acceptance attestation and EOS readback.
 * CHANGELOG: v1.16.0-WORK-EDIT-CONTEXT-SHEET opens
 *          task revision/assignment in a contextual, scroll-independent
 *          responsive sheet; sourced contributor names replace opaque IDs
 *          in selection while EOS continues to receive exact principal IDs.
 * CHANGELOG: v1.15.0-DENSE-CONTEXTUAL-WORK-QUEUE shortens row identity,
 *          moves long descriptions behind per-item disclosure, makes
 *          assignment an explicit action and uses only verified participant
 *          display names; opaque IDs remain internal and in audit evidence.
 * CHANGELOG: v1.14.0-SINGLE-ACTION-GOVERNED-WORK-ROWS renders one status-derived primary work
 *          action with responsive keyboard-accessible overflow. Terminal
 *          completion requires a separately visible evidence attestation.
 * CHANGELOG: v1.13.0-PRIMARY-QUEUE-DETAILS-ON-DEMAND removes duplicated status cards,
 *          collapses lifecycle analytics and checklists until explicitly
 *          requested, and puts the actionable project queue first.
 * CHANGELOG: v1.12.0-DENSE-DISCUSSION-CONTEXT keeps selected work context
 *          to one small toolbar and moves the source-backed activity directly
 *          under it; no stacked explanatory cards or decorative section hero.
 * CHANGELOG: v1.11.0-GOVERNED-ACTIVITY-EVIDENCE-LINKS links
 *          activity comments to governed approval/evidence panels without
 *          bypassing their separate source authority; labels project actions
 *          consistently as Activity & discussion.
 * CHANGELOG: v1.10.0-PROJECT-DISCUSSIONS-MODE provides a
 *          dedicated Discussions view using the existing authorized,
 *          paginated EOS project task feed. Users select a verified task or
 *          milestone to read source-backed comments directly, without
 *          mounting charts, checklists or the work editor. Existing work
 *          commands, IAM, source validators and audit boundaries unchanged.
 * CHANGELOG: v1.9.0-FOCUSED-TASK-ACTION-WORKSPACE switches from the
 *          full queue to a focused source-backed task action workspace for
 *          discussion, approvals and attachments, with a clear return control.
 *          One selected verified task loads at a time; no extra source reads,
 *          client-side history aggregation or changed EOS command authority.
 * CHANGELOG: v1.8.1-PARENT-BOUND-TODO-STEPS adds explicit
 *          parent-bound checklist-step creation using the existing EOS subtask
 *          command; no secondary checklist collection or local persistence.
 * CHANGELOG: v1.8.0-EOS-CHECKABLE-DAILY-EXECUTION exposes a checkable
 *          project To-do list backed entirely by existing EOS task/subtask
 *          status transitions, explicit completion confirmation and live
 *          source readback. A checkbox never creates local completion truth;
 *          milestone progress and task evidence remain separate authorities.
 * CHANGELOG: v1.7.0-SOURCE-VERIFIED-LIFECYCLE-CHART replaces the decorative
 *          strip with accessible, filterable status bars and source-backed
 *          completed/open progress metrics. Every chart change follows the
 *          existing EOS command/readback and covers only the verified page.
 * CHANGELOG: v1.6.1-EXPLICIT-TASK-VALIDATION identifies safe task create/revision 422
 *          validation fields using an allowlist, preserving drafts and retry
 *          keys without exposing input values or bypassing EOS authority.
 * CHANGELOG: v1.6.0-OPERATIONAL-WORK-QUEUE exposes three EOS-supported workflows
 *          (task, parent-bound subtask and milestone), validates a selectable
 *          active parent, and adds current-page search, status/type filters,
 *          due-date sorting and actionable overdue cues over verified EOS data.
 *          No new domain kind, permission, or global portfolio count is inferred.
 * CHANGELOG: v1.5.0-ACCESSIBLE-WORK-CALENDAR adds accessible calendar
 *          triggers and local quick dates to create/edit without changing
 *          EOS task authority, schemas, idempotency or source readback.
 * CHANGELOG: v1.4.0-QUARANTINED-TASK-FILE-VIEW opens
 *          task-bound quarantined file evidence; no preview, download,
 *          scanner release or approval authority is created.
 * CHANGELOG: v1.13.0-PRIMARY-QUEUE-DETAILS-ON-DEMAND lets the
 *          project owner request named task review through the shared
 *          canonical approval source, separately from discussion/task status.
 * CHANGELOG: v1.13.0-PRIMARY-QUEUE-DETAILS-ON-DEMAND opens a selected task's
 *          source-backed immutable comment/mention thread without treating
 *          mentions as deliveries, approvals or task lifecycle commands.
 * CHANGELOG: v1.13.0-PRIMARY-QUEUE-DETAILS-ON-DEMAND adds a
 *          single in-place owner task edit and reassignment form, using EOS
 *          current assignee choices, exact revision CAS and fresh readback.
 * CHANGELOG: v1.13.0-PRIMARY-QUEUE-DETAILS-ON-DEMAND adds source-backed
 *          task pagination, status distribution, governed creation, milestone,
 *          dependency and assignment selectors and revisioned transitions.
 */
import React, { useCallback, useEffect, useId, useMemo, useRef, useState } from 'react';
import { CalendarDays, CheckCircle2, CirclePause, ClipboardList, LoaderCircle, Plus, RefreshCw, Waypoints } from 'lucide-react';
import api from '../../services/api.js';
import ProjectTaskCommentsPanel from './ProjectTaskCommentsPanel.jsx';
import ProjectWorkRow from './ProjectWorkRow.jsx';
import ProjectNotesPanel from './ProjectNotesPanel.jsx';
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
  projectId, tenantId, principalId, tenantHeaders, discussionOnly = false,
  onFocusedTaskChange = null,
}) {
  const [items, setItems] = useState([]);
  const [participants, setParticipants] = useState([]);
  const [participantHasMore, setParticipantHasMore] = useState(false);
  const [actionCapabilities, setActionCapabilities] = useState(null);
  const [state, setState] = useState('LOADING');
  const [offset, setOffset] = useState(0);
  const [hasMore, setHasMore] = useState(false);
  const [draft, setDraft] = useState({ ...EMPTY });
  const [creating, setCreating] = useState(false);
  const [workType, setWorkType] = useState('TASK');
  const [workQuery, setWorkQuery] = useState('');
  const [workMineOnly, setWorkMineOnly] = useState(false);
  const [selectedWorkIds, setSelectedWorkIds] = useState([]);
  const [workDensity, setWorkDensity] = useState('comfortable');
  const [workStatus, setWorkStatus] = useState('ALL');
  const [workKind, setWorkKind] = useState('ALL');
  const [workGroup, setWorkGroup] = useState('NONE');
  const [workOrder, setWorkOrder] = useState('DUE_ASC');
  const [completionCandidate, setCompletionCandidate] = useState(null);
  const [completionAttested, setCompletionAttested] = useState(false);
  const [drawerTaskId, setDrawerTaskId] = useState(null);
  const drawerReturnFocus = useRef(null);
  const drawerRef = useRef(null);
  const [editor, setEditor] = useState(null);
  const [assignmentOnly, setAssignmentOnly] = useState(false);
  const [discussionTaskId, setDiscussionTaskId] = useState(null);
  const [inlineDiscussionTaskId, setInlineDiscussionTaskId] = useState(null);
  const [showProjectNotesInline, setShowProjectNotesInline] = useState(false);
  const [approvalTaskId, setApprovalTaskId] = useState(null);
  const [attachmentTaskId, setAttachmentTaskId] = useState(null);
  const [openEvidenceAfterCreate, setOpenEvidenceAfterCreate] = useState(true);
  const [busy, setBusy] = useState(false);
  const [pendingTransition, setPendingTransition] = useState(null);
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
      const [tasks, people, actionResult] = await Promise.all([
        api.get(root + '/tasks?limit=50&offset=' + nextOffset, { headers }),
        api.get(root + '/participants?limit=100&offset=0', { headers }),
        api.get(root + '/task-action-capabilities', { headers })
          .then(result => result?.data).catch(() => null),
      ]);
      if (request !== generation.current || currentScope.current !== active) return false;
      const verified = validList(tasks.data, tenantId, principalId, projectId, nextOffset);
      const eligible = validParticipants(people.data, tenantId, principalId, projectId);
      const capabilityNames = ['can_start', 'can_complete', 'can_block',
        'can_cancel', 'can_assign', 'can_edit'];
      const admitted = actionResult?.schema === 'WILSY-PROJECT-TASK-ACTION-CAPABILITIES/V1'
        && actionResult.tenant_id === tenantId
        && actionResult.principal_id === principalId
        && actionResult.project_id === projectId
        && capabilityNames.every(key => typeof actionResult[key] === 'boolean');
      setActionCapabilities({
        canStart: admitted && actionResult.can_start,
        canComplete: admitted && actionResult.can_complete,
        canBlock: admitted && actionResult.can_block,
        canCancel: admitted && actionResult.can_cancel,
        canAssign: admitted && actionResult.can_assign,
        canEdit: admitted && actionResult.can_edit,
        canAttachments: true, canActivity: true, canApprovals: true,
      });
      setItems(verified.items);
      setSelectedWorkIds(previous => previous.filter(id => nextOffset === offset && verified.items.some(item => item.task_id === id)));
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
      setActionCapabilities(null);
      setHasMore(false);
      setSelectedWorkIds([]);
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
    setActionCapabilities(null);
    setOffset(0);
    setHasMore(false);
    setCreating(false);
    setWorkType('TASK');
    setWorkQuery('');
    setWorkMineOnly(false);
    setSelectedWorkIds([]);
    setWorkDensity('comfortable');
    setWorkStatus('ALL');
    setWorkKind('ALL');
    setWorkGroup('NONE');
    setWorkOrder('DUE_ASC');
    setCompletionCandidate(null);
    setCompletionAttested(false);
    setEditor(null);
    setAssignmentOnly(false);
    setDrawerTaskId(null);
    setDiscussionTaskId(null);
    setInlineDiscussionTaskId(null);
    setShowProjectNotesInline(false);
    setApprovalTaskId(null);
    setAttachmentTaskId(null);
    setOpenEvidenceAfterCreate(true);
    setDraft({ ...EMPTY });
    setPendingTransition(null);
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

  const execute = async (fingerprint, action, expectedTaskId = null, showEvidenceAfterCreate = false) => {
    if (busy || state !== 'READY' || !actionCapabilities) return;
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
      if (showEvidenceAfterCreate && selfIsContributor) {
        setDiscussionTaskId(null);
        setApprovalTaskId(null);
        setAttachmentTaskId(data.task.task_id);
      }
    } catch (cause) {
      if (currentScope.current !== active) return;
      const status = cause?.response?.status;
      const safeFields = new Set([
        'kind', 'title', 'description', 'due_date', 'assignee_principal_id',
        'parent_task_id', 'depends_on', 'expected_revision', 'status',
      ]);
      const problems = Array.isArray(cause?.response?.data?.detail)
        ? cause.response.data.detail : [];
      const invalidFields = [...new Set(problems.flatMap(problem => {
        const loc = problem?.loc;
        if (!Array.isArray(loc)) return [];
        return loc.filter(field => typeof field === 'string' && safeFields.has(field));
      }))];
      setError(status === 403 ? 'EOS denied this task command.'
        : status === 404 ? 'The work item is not visible within this project.'
          : status === 409 ? 'Project work has changed or a dependency is incomplete. Refresh before retrying.'
            : status === 422 ? 'EOS rejected the work-item input'
              + (invalidFields.length ? ': ' + invalidFields.join(', ') : '.')
              + ' Review the indicated fields; your draft is preserved.'
              : 'EOS has not verified this task command. Reconcile source state before retrying.');
    } finally {
      if (currentScope.current === active) {
        setBusy(false);
        setPendingTransition(null);
      }
    }
  };

  const create = event => {
    event.preventDefault();
    const title = draft.title.trim();
    if (!title || !actionCapabilities?.canEdit || title.length > 180
      || (participantHasMore && draft.assignee_principal_id)) return;
    const isSubtask = workType === 'SUBTASK';
    const activeParent = items.some(item => item.task_id === draft.parent_task_id
      && item.kind === 'TASK' && !['DONE', 'CANCELLED'].includes(item.status));
    if (isSubtask && !activeParent) {
      setError('Choose an active, EOS-verified parent task from the current page.');
      return;
    }
    const body = {
      kind: workType === 'MILESTONE' ? 'MILESTONE' : 'TASK',
      title, description: draft.description.trim(),
      due_date: draft.due_date || null,
      assignee_principal_id: draft.assignee_principal_id || null,
      parent_task_id: isSubtask ? draft.parent_task_id : null,
      depends_on: draft.depends_on,
    };
    void execute(JSON.stringify(['create', body]), key =>
      api.post(root + '/tasks', body, {
        headers: { ...headers, 'Idempotency-Key': key },
      }), null, openEvidenceAfterCreate,
    );
  };

  const revise = event => {
    event.preventDefault();
    if (!editor || !editor.title.trim()
      || !(assignmentOnly ? actionCapabilities?.canAssign : actionCapabilities?.canEdit)) return;
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
    const permitted = status === 'IN_PROGRESS' ? actionCapabilities?.canStart
      : status === 'DONE' ? actionCapabilities?.canComplete
        : status === 'BLOCKED' ? actionCapabilities?.canBlock
          : status === 'CANCELLED' ? actionCapabilities?.canCancel : false;
    if (busy || state !== 'READY' || !permitted) return;
    setPendingTransition({ taskId: item.task_id, status });
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
  // All operators below work only on the EOS-verified current page; nothing
  // implies a global cross-page count, sort, search or hidden project record.
  const workRows = useMemo(() => {
    const term = workQuery.trim().toLocaleLowerCase();
    const result = items.filter(item => {
      const kind = item.kind === 'MILESTONE' ? 'MILESTONE'
        : item.parent_task_id ? 'SUBTASK' : 'TASK';
      return (!workMineOnly || item.assignee_principal_id === principalId)
        && (workStatus === 'ALL' || item.status === workStatus)
        && (workKind === 'ALL' || kind === workKind)
        && (!term || [item.title, item.description, item.task_id]
          .some(value => String(value || '').toLocaleLowerCase().includes(term)));
    });
    result.sort((a, b) => {
      const dueOrder = (a.due_date === null) - (b.due_date === null)
        || (a.due_date || '').localeCompare(b.due_date || '');
      const titleOrder = a.title.localeCompare(b.title);
      return (workOrder === 'DUE_DESC' ? -((a.due_date === null) - (b.due_date === null))
        || -((a.due_date || '').localeCompare(b.due_date || ''))
        : workOrder === 'TITLE_ASC' ? titleOrder : dueOrder)
        || a.task_id.localeCompare(b.task_id);
    });
    return result;
  }, [items, workQuery, workMineOnly, principalId, workStatus, workKind, workOrder]);
  const currentDay = new Date();
  const todayISO = currentDay.getFullYear() + '-' + String(currentDay.getMonth() + 1).padStart(2, '0')
    + '-' + String(currentDay.getDate()).padStart(2, '0');
  const overdueOnPage = items.filter(item => item.due_date && item.due_date < todayISO
    && !['DONE', 'CANCELLED'].includes(item.status)).length;
  const selfIsContributor = participants.some(person =>
    person.principal_id === principalId && person.role === 'CONTRIBUTOR'
    && person.status !== 'REVOKED' && person.state !== 'REVOKED');
  const availableParents = items.filter(item => item.kind === 'TASK'
    && !['DONE', 'CANCELLED'].includes(item.status));
  const todoRows = items.filter(item => item.kind === 'TASK'
    && item.status !== 'CANCELLED');
  const doneTodos = todoRows.filter(item => item.status === 'DONE').length;
  const contributorName = id => {
    if (!id) return null;
    const entry = participants.find(person => person.principal_id === id);
    if (!entry) return 'Assigned contributor · name unavailable';
    const names = [entry.first_name, entry.last_name].filter(
      value => typeof value === 'string' && value.trim().length > 0
        && value.length <= 100);
    return names.length ? names.join(' ') : 'Assigned contributor · name unavailable';
  };
  const groupedWorkRows = useMemo(() => {
    if (workGroup === 'NONE') return [{ key: 'all', title: null, rows: workRows }];
    const grouped = new Map();
    workRows.forEach(item => {
      const key = workGroup === 'STATUS' ? item.status
        : workGroup === 'TYPE' ? (item.kind === 'MILESTONE' ? 'MILESTONE'
          : item.parent_task_id ? 'SUBTASK' : 'TASK')
          : item.assignee_principal_id || 'UNASSIGNED';
      const title = workGroup === 'STATUS' ? label(item.status)
        : workGroup === 'TYPE' ? (key === 'MILESTONE' ? 'Milestones'
          : key === 'SUBTASK' ? 'Subtasks' : 'Tasks')
          : key === 'UNASSIGNED' ? 'Not assigned' : contributorName(key);
      if (!grouped.has(key)) grouped.set(key, { key, title, rows: [] });
      grouped.get(key).rows.push(item);
    });
    return [...grouped.values()].sort((a, b) => a.title.localeCompare(b.title));
  }, [workRows, workGroup, participants]);

  const openTaskEditor = (selected, assignOnly = false) => {
    if (!(assignOnly ? actionCapabilities?.canAssign : actionCapabilities?.canEdit)) return;
    setCreating(false);
    setAssignmentOnly(assignOnly);
    setEditor({
      task_id: selected.task_id, revision: selected.revision,
      title: selected.title, description: selected.description,
      due_date: selected.due_date || '',
      assignee_principal_id: selected.assignee_principal_id || '',
    });
  };
  const completingItem = items.find(item => item.task_id === completionCandidate
    && item.status === 'IN_PROGRESS');
  useEffect(() => {
    // Completion confirmation closes only when a fresh EOS page reports DONE,
    // or when the selected record disappears from the authorized source page.
    if (!completionCandidate || state !== 'READY') return;
    const current = items.find(item => item.task_id === completionCandidate);
    if (!current || current.status === 'DONE' || current.status === 'CANCELLED') {
      setCompletionCandidate(null);
      setCompletionAttested(false);
    }
  }, [completionCandidate, items, state]);

  const drawerTask = items.find(item => item.task_id === drawerTaskId);
  const closeDrawer = () => {
    setDrawerTaskId(null);
    drawerReturnFocus.current?.focus?.();
  };
  useEffect(() => {
    if (!drawerTaskId) return undefined;
    const keyDown = event => {
      if (event.key === 'Escape') {
        event.preventDefault();
        setDrawerTaskId(null);
        drawerReturnFocus.current?.focus?.();
      }
    };
    window.addEventListener('keydown', keyDown);
    drawerRef.current?.querySelector('button')?.focus();
    return () => window.removeEventListener('keydown', keyDown);
  }, [drawerTaskId]);
  const focusedAction = discussionTaskId ? { id: discussionTaskId, type: 'discussion' }
    : approvalTaskId ? { id: approvalTaskId, type: 'approvals' }
      : attachmentTaskId ? { id: attachmentTaskId, type: 'attachments' } : null;
  const selectedActionTask = focusedAction && items.find(item => item.task_id === focusedAction.id);
  const contextTask = (state === 'READY' || state === 'REFRESHING')
    ? drawerTask || selectedActionTask || (editor
      ? items.find(item => item.task_id === editor.task_id) : null)
    : null;
  const contextTaskId = contextTask?.task_id || null;
  const contextTaskRevision = contextTask?.revision || null;
  useEffect(() => {
    // Only EOS-hydrated selected task coordinates leave this component.
    // They are untrusted navigation hints: Python EOS independently
    // authorizes and rereads project/task revisions for every AI request.
    if (typeof onFocusedTaskChange !== 'function') return undefined;
    onFocusedTaskChange(contextTaskId && Number.isSafeInteger(contextTaskRevision)
      ? { task_id: contextTaskId, task_revision: contextTaskRevision }
      : null);
    return () => onFocusedTaskChange(null);
  }, [onFocusedTaskChange, contextTaskId, contextTaskRevision]);
  const closeFocusedAction = () => {
    setDiscussionTaskId(null);
    setApprovalTaskId(null);
    setAttachmentTaskId(null);
  };

  if (discussionOnly) {
    return <section className="wp-project-tasks border-t border-slate-200 pt-2"
      aria-label="Project discussions workspace">
      {focusedAction && selectedActionTask ? <>
        <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-200 pb-2">
          <h3 className="min-w-0 break-words text-sm font-semibold text-slate-950">
            {selectedActionTask.title}
          </h3>
          <button type="button" className="text-xs font-semibold text-blue-800 underline underline-offset-2"
            onClick={closeFocusedAction}>All discussions</button>
        </div>
        {focusedAction.type === 'discussion' && <ProjectTaskCommentsPanel
          key={[scope, focusedAction.id].join(':')}
          tenantId={tenantId} projectId={projectId} principalId={principalId}
          taskId={focusedAction.id} participants={participants} tenantHeaders={tenantHeaders}
          onClose={closeFocusedAction}
          onViewApprovals={() => { setDiscussionTaskId(null); setApprovalTaskId(focusedAction.id); }}
          onViewAttachments={() => { setDiscussionTaskId(null); setAttachmentTaskId(focusedAction.id); }}/>}
        {focusedAction.type === 'approvals' && <ProjectTaskApprovalsPanel
          key={[scope, focusedAction.id].join(':')}
          tenantId={tenantId} projectId={projectId} principalId={principalId}
          taskId={focusedAction.id} participants={participants} tenantHeaders={tenantHeaders}
          onClose={() => { setApprovalTaskId(null); setDiscussionTaskId(focusedAction.id); }}/>}
        {focusedAction.type === 'attachments' && <ProjectTaskAttachmentsPanel
          key={[scope, focusedAction.id].join(':')}
          tenantId={tenantId} projectId={projectId} principalId={principalId}
          taskId={focusedAction.id} participantMode={selfIsContributor} tenantHeaders={tenantHeaders}
          onClose={() => { setAttachmentTaskId(null); setDiscussionTaskId(focusedAction.id); }}/>}
        {focusedAction.type !== 'discussion' &&
          <button type="button" className="wp-button mt-2" onClick={() => {
            setApprovalTaskId(null); setAttachmentTaskId(null);
            setDiscussionTaskId(focusedAction.id);
          }}>Back to activity</button>}
      </> : <>
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <h3 className="text-lg font-bold text-slate-950">Activity &amp; discussion</h3>
            <p className="mt-1 text-sm text-slate-600">Discuss source-verified work directly in this list, or write governed project-wide notes without opening a task.</p>
          </div>
          <div className="flex flex-wrap gap-2">
            <button type="button" className="wp-button"
              aria-expanded={showProjectNotesInline}
              onClick={() => setShowProjectNotesInline(value => !value)}>
              {showProjectNotesInline ? 'Hide project notes' : 'Project notes'}
            </button>
            <button type="button" className="wp-button" onClick={() => void load(offset)}
              disabled={state === 'LOADING'}>Refresh discussions</button>
          </div>
        </div>
        {(state === 'LOADING' || state === 'REFRESHING') &&
          <p role="status" className="mt-3 text-sm text-slate-600">Verifying project discussion sources…</p>}
        {(state === 'UNAVAILABLE' || state === 'DENIED') &&
          <p role="alert" className="mt-3 text-sm text-rose-700">{error}</p>}
        {state === 'READY' && <>
          {showProjectNotesInline && <div className="mt-3 rounded-lg border border-slate-200 bg-white p-3"
            aria-label="Inline project notes board">
            <ProjectNotesPanel key={'inline-notes:' + scope} tenantId={tenantId}
              principalId={principalId} projectId={projectId} tenantHeaders={tenantHeaders}/>
          </div>}
          <ul aria-label="Verified discussion work items"
            className="mt-4 divide-y divide-slate-200 overflow-hidden rounded-xl border border-slate-200 bg-white">
            {items.map(item => <li key={item.task_id}>
              <button type="button" aria-expanded={inlineDiscussionTaskId === item.task_id}
                className="flex w-full items-center justify-between gap-4 p-4 text-left hover:bg-blue-50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-blue-700"
                onClick={() => setInlineDiscussionTaskId(current => current === item.task_id ? null : item.task_id)}>
                <span className="min-w-0">
                  <span className="block break-words text-sm font-semibold text-slate-950">{item.title}</span>
                  <span className="mt-1 block text-xs text-slate-600">{item.kind === 'MILESTONE' ? 'Milestone' : item.parent_task_id ? 'Subtask' : 'Task'} · {label(item.status)}</span>
                </span>
                <span className="shrink-0 text-xs font-semibold text-blue-800">
                  {inlineDiscussionTaskId === item.task_id ? 'Close discussion' : 'Discuss / view activity'}
                </span>
              </button>
              {inlineDiscussionTaskId === item.task_id && <div className="border-t border-slate-200 bg-slate-50 p-4"
                aria-label={'Inline activity for ' + item.title}>
                <ProjectTaskCommentsPanel key={'inline:' + scope + ':' + item.task_id}
                  tenantId={tenantId} projectId={projectId} principalId={principalId}
                  taskId={item.task_id} participants={participants} tenantHeaders={tenantHeaders}
                  onClose={() => setInlineDiscussionTaskId(null)}
                  onViewApprovals={() => { setInlineDiscussionTaskId(null); setApprovalTaskId(item.task_id); }}
                  onViewAttachments={() => { setInlineDiscussionTaskId(null); setAttachmentTaskId(item.task_id); }}/>
              </div>}
            </li>)}
            {items.length === 0 && <li className="p-4 text-sm text-slate-600">
              EOS verified no work items on this page.
            </li>}
          </ul>
          {(offset > 0 || hasMore) && <nav aria-label="Discussion work item pages"
            className="mt-3 flex flex-wrap items-center justify-between gap-2">
            <button type="button" className="wp-button" disabled={offset === 0}
              onClick={() => void load(Math.max(0, offset - 50))}>Previous work items</button>
            <span className="text-sm text-slate-600">Page {Math.floor(offset / 50) + 1}</span>
            <button type="button" className="wp-button" disabled={!hasMore}
              onClick={() => void load(offset + 50)}>Next work items</button>
          </nav>}
        </>}
      </>}
    </section>;
  }

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
        {state === 'READY' && actionCapabilities?.canEdit && <button type="button" className="wp-button wp-button-primary"
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
    {(state === 'READY' || state === 'REFRESHING') && (focusedAction && selectedActionTask ? <div className="mt-4" aria-label="Focused project task action">
      <div className="mb-3 flex flex-wrap items-center justify-between gap-3 rounded-xl border border-slate-200 bg-white p-4">
        <div className="min-w-0">
          <p className="text-xs font-semibold uppercase tracking-wide text-slate-600">{focusedAction.type} · selected EOS work item</p>
          <h4 className="mt-1 break-words text-base font-bold text-slate-900">{selectedActionTask.title}</h4>
          <p className="mt-1 text-xs text-slate-600">{label(selectedActionTask.status)} · revision {selectedActionTask.revision}</p>
        </div>
        <button type="button" className="wp-button" onClick={closeFocusedAction}>Back to work queue</button>
      </div>
      {focusedAction.type === 'discussion' && <ProjectTaskCommentsPanel key={[scope, focusedAction.id].join(':')}
        tenantId={tenantId} projectId={projectId} principalId={principalId}
        taskId={focusedAction.id} participants={participants} tenantHeaders={tenantHeaders}
        onClose={closeFocusedAction}
        onViewApprovals={() => { setDiscussionTaskId(null); setApprovalTaskId(focusedAction.id); }}
        onViewAttachments={() => { setDiscussionTaskId(null); setAttachmentTaskId(focusedAction.id); }}/>}
      {focusedAction.type === 'approvals' && <ProjectTaskApprovalsPanel key={[scope, focusedAction.id].join(':')}
        tenantId={tenantId} projectId={projectId} principalId={principalId}
        taskId={focusedAction.id} participants={participants} tenantHeaders={tenantHeaders}
        onClose={closeFocusedAction}/>}
      {focusedAction.type === 'attachments' && <ProjectTaskAttachmentsPanel key={[scope, focusedAction.id].join(':')}
        tenantId={tenantId} projectId={projectId} principalId={principalId}
        taskId={focusedAction.id} participantMode={selfIsContributor} tenantHeaders={tenantHeaders}
        onClose={closeFocusedAction}/>}
    </div> : <>
      {!actionCapabilities?.canEdit && <p role="status" className="mt-2 text-xs font-semibold text-amber-900">
        Project work is read-only. EOS has not confirmed current task-update authority.
      </p>}
      <p className="mt-2 text-xs text-slate-600" aria-label="Verified current task page status">
        {items.length} verified work items · {counts.find(item => item.status === 'IN_PROGRESS')?.count || 0} in progress
        {overdueOnPage > 0 ? ' · ' + overdueOnPage + ' overdue' : ''}
      </p>
      <details className="mt-2 border-b border-slate-200 pb-2" aria-label="Verified task lifecycle chart">
        <summary className="cursor-pointer py-2 text-xs font-semibold text-slate-700">View lifecycle breakdown · {chartTotal} work items on this page</summary>
        <section className="rounded-lg bg-slate-50 p-3">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <h4 className="text-sm font-bold text-slate-900">Work lifecycle · current page</h4>
            <p className="mt-1 text-xs text-slate-600">Every bar uses EOS-verified tasks, not portfolio estimates. Select a bar to filter the work table.</p>
          </div>
          <div className="text-right" aria-label="Verified task completion on current page">
            <span className="block text-2xl font-bold tabular-nums text-slate-900">{chartTotal ? Math.round(100 * counts.find(item => item.status === 'DONE').count / chartTotal) : 0}%</span>
            <span className="text-xs text-slate-600">Done on this page · {counts.find(item => item.status === 'DONE').count} / {chartTotal}</span>
          </div>
        </div>
        <div className="mt-4 space-y-2">
          {counts.map(({ status, count }) => {
            const percent = chartTotal ? Math.round(100 * count / chartTotal) : 0;
            const color = ({
              TODO: '#64748b', IN_PROGRESS: '#2563eb', BLOCKED: '#c2410c',
              DONE: '#15803d', CANCELLED: '#475569',
            })[status];
            return <button key={status} type="button"
              aria-label={'Filter work to ' + label(status) + ': ' + count + ' of ' + chartTotal + ' verified on page'}
              aria-pressed={workStatus === status} onClick={() => setWorkStatus(current => current === status ? 'ALL' : status)}
              className={'grid w-full grid-cols-[minmax(75px,130px)_minmax(0,1fr)_50px] items-center gap-3 rounded-lg px-2 py-2 text-left hover:bg-blue-50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-blue-700 ' +
                (workStatus === status ? 'bg-blue-50 ring-1 ring-blue-300' : '')}>
              <span className="text-xs font-semibold text-slate-800">{label(status)}</span>
              <span className="block h-3 overflow-hidden rounded-full bg-slate-100" role="img"
                aria-label={label(status) + ': ' + percent + ' percent of the verified page'}>
                <span className="block h-full rounded-full transition-[width] duration-200"
                  data-lifecycle-status={status} style={{ width: percent + '%', backgroundColor: color }}/>
              </span>
              <span className="text-right text-xs font-semibold tabular-nums text-slate-800">{count} · {percent}%</span>
            </button>;
          })}
        </div>
        <p role="status" className="mt-3 border-t border-slate-200 pt-3 text-xs text-slate-600">
          {overdueOnPage > 0 ? overdueOnPage + ' overdue on this page.' : 'No overdue items on this page.'}
          {' '}Lifecycle actions update this chart only after a fresh verified EOS list read.
        </p>
      </section>
      </details>
      <details className="mt-2 border-b border-slate-200 pb-2" aria-label="EOS verified To-do checklist">
        <summary className="cursor-pointer py-2 text-xs font-semibold text-slate-700">
          Checklist mode · {doneTodos}/{todoRows.length} completed
        </summary>
        <section className="rounded-lg bg-slate-50 p-3">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <h4 className="text-sm font-bold text-slate-900">To-do checklist · current verified page</h4>
            <p className="mt-1 text-xs text-slate-600">Each checkbox is an actual EOS task or subtask, not a browser-only checklist item. Work must be In progress before it can be completed.</p>
          </div>
          <span role="status" className="text-sm font-semibold tabular-nums text-slate-800">{doneTodos} of {todoRows.length} completed</span>
        </div>
        <div role="progressbar" aria-label="Verified To-do completion on this page"
          aria-valuemin={0} aria-valuemax={todoRows.length || 1}
          aria-valuenow={doneTodos}
          aria-valuetext={doneTodos + ' of ' + todoRows.length + ' verified tasks completed'}
          className="mt-3 h-2 overflow-hidden rounded-full bg-slate-100">
          <div className="h-full rounded-full bg-emerald-700"
            style={{ width: (todoRows.length ? 100 * doneTodos / todoRows.length : 0) + '%' }}/>
        </div>
        {todoRows.length === 0
          ? <p className="mt-3 text-xs text-slate-600">No verified tasks or subtasks on this page. Create a task to begin a persisted checklist.</p>
          : <ul className="mt-3 divide-y divide-slate-200" aria-label="Persisted project task checklist">
            {todoRows.map(item => {
              const complete = item.status === 'DONE';
              const canComplete = item.status === 'IN_PROGRESS';
              return <li key={item.task_id} className="flex flex-wrap items-center gap-3 py-3">
                <label className="flex min-w-[200px] flex-1 items-start gap-3 text-sm text-slate-900">
                  <input type="checkbox" className="mt-1 size-4 accent-emerald-700"
                    aria-label={'Mark completed: ' + item.title}
                    checked={complete} disabled={busy || !canComplete || !actionCapabilities?.canComplete}
                    onChange={() => {
                      if (!canComplete || !actionCapabilities?.canComplete) return;
                      setCompletionCandidate(item.task_id);
                      setCompletionAttested(false);
                    }}/>
                  <span className={complete ? 'text-slate-600 line-through' : ''}>
                    <span className="block font-semibold">{item.title}</span>
                    <span className="mt-0.5 block text-xs text-slate-600">{item.parent_task_id ? 'Subtask' : 'Task'} · {label(item.status)}{item.due_date ? ' · due ' + item.due_date : ''}</span>
                  </span>
                </label>
                {item.status === 'TODO' && actionCapabilities?.canStart && <button type="button" className="wp-button !min-h-9 !px-3 !text-xs"
                  disabled={busy} onClick={() => transition(item, 'IN_PROGRESS')}>Start work</button>}
                {item.status === 'BLOCKED' && actionCapabilities?.canStart && <button type="button" className="wp-button !min-h-9 !px-3 !text-xs"
                  disabled={busy} onClick={() => transition(item, 'IN_PROGRESS')}>Resume work</button>}
                {canComplete && actionCapabilities?.canComplete && <span className="text-xs text-slate-600">Tick to verify completion</span>}
                {complete && <span className="text-xs font-semibold text-emerald-800">EOS confirmed Done</span>}
                {item.status !== 'DONE' && actionCapabilities?.canEdit && <button type="button"
                  className="wp-button !min-h-9 !px-3 !text-xs" disabled={busy}
                  aria-label={'Add checklist step to ' + item.title}
                  onClick={() => {
                    setCreating(true);
                    setEditor(null);
                    setWorkType('SUBTASK');
                    setDraft({ ...EMPTY, kind: 'TASK', parent_task_id: item.task_id });
                  }}>Add checklist step</button>}
                <button type="button" className="wp-button !min-h-9 !px-3 !text-xs" disabled={busy}
                  onClick={() => setDiscussionTaskId(item.task_id)}>Activity &amp; discussion</button>
              </li>;
            })}
          </ul>}
        {hasMore && <p className="mt-3 text-xs font-semibold text-amber-900">More EOS task pages exist. The completion fraction above covers this page only.</p>}
      </section>
      </details>
      <div className="mt-4 flex flex-wrap items-end gap-3 rounded-lg border border-slate-200 bg-white p-3" aria-label="Project work queue controls">
        <label className="flex min-w-[145px] flex-col gap-1 text-xs font-semibold text-slate-800">
          Group work
          <select aria-label="Group project work" value={workGroup}
            onChange={event => setWorkGroup(event.target.value)}
            className="rounded-md border border-slate-300 bg-white px-2 py-2 text-sm text-slate-900">
            <option value="NONE">No grouping</option>
            <option value="STATUS">By status</option>
            <option value="TYPE">By work type</option>
            <option value="ASSIGNEE">By contributor</option>
          </select>
        </label>
        <label className="flex min-w-[145px] flex-col gap-1 text-xs font-semibold text-slate-800">
          Work row density
          <select aria-label="Work row density" value={workDensity}
            onChange={event => setWorkDensity(event.target.value)}
            className="rounded-md border border-slate-300 bg-white px-2 py-2 text-sm text-slate-900">
            <option value="comfortable">Comfortable</option>
            <option value="compact">Compact</option>
          </select>
        </label>
        {selectedWorkIds.length > 0 && <span role="status" className="text-xs font-semibold text-blue-800">
          {selectedWorkIds.length} work item{selectedWorkIds.length === 1 ? '' : 's'} selected on this verified page
          · Actions remain individual until EOS authorizes bulk commands
        </span>}
        <button type="button" className="wp-button min-h-10" aria-pressed={workMineOnly}
          onClick={() => setWorkMineOnly(previous => !previous)}>
          {workMineOnly ? 'All work on this page' : 'My work on this page'}
        </button>
        <label className="min-w-[180px] flex-[2] text-xs font-semibold text-slate-800">Search this verified page
          <input type="search" value={workQuery} onChange={event => setWorkQuery(event.target.value)}
            placeholder="Title, details or work ID"
            className="mt-1 w-full rounded-lg border border-slate-300 bg-white p-2.5 text-sm font-normal text-slate-900"/>
        </label>
        <label className="min-w-[125px] flex-1 text-xs font-semibold text-slate-800">Status
          <select aria-label="Filter work status" value={workStatus} onChange={event => setWorkStatus(event.target.value)}
            className="mt-1 w-full rounded-lg border border-slate-300 bg-white p-2.5 text-sm font-normal text-slate-900">
            <option value="ALL">All statuses</option>
            {STATUSES.map(status => <option key={status} value={status}>{label(status)}</option>)}
          </select>
        </label>
        <label className="min-w-[125px] flex-1 text-xs font-semibold text-slate-800">Work type
          <select aria-label="Filter work type" value={workKind} onChange={event => setWorkKind(event.target.value)}
            className="mt-1 w-full rounded-lg border border-slate-300 bg-white p-2.5 text-sm font-normal text-slate-900">
            <option value="ALL">All types</option>
            <option value="TASK">Tasks</option>
            <option value="SUBTASK">Subtasks</option>
            <option value="MILESTONE">Milestones</option>
          </select>
        </label>
        <label className="min-w-[145px] flex-1 text-xs font-semibold text-slate-800">Sort page
          <select aria-label="Sort work page" value={workOrder} onChange={event => setWorkOrder(event.target.value)}
            className="mt-1 w-full rounded-lg border border-slate-300 bg-white p-2.5 text-sm font-normal text-slate-900">
            <option value="DUE_ASC">Due soonest</option>
            <option value="DUE_DESC">Due latest</option>
            <option value="TITLE_ASC">Title A–Z</option>
          </select>
        </label>
        <span role="status" className="w-full text-xs text-slate-600">{workRows.length} shown / {items.length} verified on page {Math.floor(offset / 50) + 1}. Search and sorting apply only to this page.</span>
      </div>
      {creating && <form onSubmit={create} className="mt-4 space-y-3 rounded-xl border border-blue-200 bg-blue-50/50 p-3">
        <h4 className="text-sm font-bold text-slate-900">Create EOS work item</h4>
        {workType === 'SUBTASK' && draft.parent_task_id && <p role="status" className="text-xs font-semibold text-blue-900">
          Adding an EOS subtask under {availableParents.find(item => item.task_id === draft.parent_task_id)?.title || 'selected source task'}.
        </p>}
        <p className="text-xs text-slate-600">{workType === 'MILESTONE'
          ? 'Milestone — a delivery checkpoint with a target date and accountable owner.'
          : workType === 'SUBTASK'
            ? 'Subtask — work linked to an active parent task; choose that parent below.'
            : 'Task — top-level accountable work, its due date and dependencies.'}</p>
        <div className="grid gap-3 sm:grid-cols-2">
          <label className="block text-sm font-semibold text-slate-800">Work type
            <select className="mt-1 w-full rounded-lg border border-slate-300 bg-white p-2.5 text-sm font-normal text-slate-900"
              value={workType} onChange={event => {
                setWorkType(event.target.value);
                setDraft(value => ({ ...value,
                  kind: event.target.value === 'MILESTONE' ? 'MILESTONE' : 'TASK',
                  parent_task_id: '',
                }));
              }}>
              <option value="TASK">Task</option>
              <option value="SUBTASK">Subtask — requires parent</option>
              <option value="MILESTONE">Milestone</option>
            </select>
          </label>
          <ProjectWorkDateField label={workType === 'MILESTONE' ? 'Milestone target date' : 'Task due date'} value={draft.due_date}
            onChange={date => setDraft(previous => ({ ...previous, due_date: date }))}/>
        </div>
        <label className="block text-sm font-semibold text-slate-800">{workType === 'MILESTONE' ? 'Milestone title' : workType === 'SUBTASK' ? 'Subtask title' : 'Task title'}
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
                {contributorName(person.principal_id)}
              </option>)}
            </select>
          </label>
          <label className="block text-sm font-semibold text-slate-800">Parent task {workType === 'SUBTASK' ? '(required)' : '(not applicable)'}
            <select aria-label="Parent task" required={workType === 'SUBTASK'} disabled={workType !== 'SUBTASK'}
              value={workType === 'SUBTASK' ? draft.parent_task_id : ''}
              onChange={event => setDraft(value => ({ ...value, parent_task_id: event.target.value }))}
              className="mt-1 w-full rounded-lg border border-slate-300 bg-white p-2.5 text-sm font-normal text-slate-900">
              <option value="">Top-level work</option>
              {availableParents.map(item =>
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
        {workType === 'SUBTASK' && availableParents.length === 0 && <p role="status" className="text-xs text-amber-800">No eligible parent task is verified on this page. Create a top-level task or navigate to a page with an eligible parent.</p>}
        {selfIsContributor ? <label className="flex items-start gap-2 text-xs text-slate-800">
          <input type="checkbox" className="mt-0.5 size-4"
            checked={openEvidenceAfterCreate}
            onChange={event => setOpenEvidenceAfterCreate(event.target.checked)}/>
          Open the task evidence uploader after EOS verifies the new task.
        </label> : <p className="text-xs text-slate-700">
          Only a currently authorized project contributor may upload task evidence.
        </p>}
        <p className="text-xs text-slate-700">PDF or image evidence is uploaded only after task creation.
          EOS quarantines files pending independent scan clearance.</p>
        {participantHasMore && <p className="text-xs text-amber-800">Only the first verified participant page is selectable. Further assignments require a complete directory read.</p>}
        <button type="submit" disabled={busy || !actionCapabilities?.canEdit || !draft.title.trim()
          || (workType === 'SUBTASK' && !availableParents.some(item => item.task_id === draft.parent_task_id))}
          className="wp-button wp-button-primary">
          <Plus size={14}/> Save work to EOS
        </button>
      </form>}
      {editor && <div className="fixed inset-0 z-[90] flex items-end justify-center bg-slate-950/45 md:items-center md:p-5"
        onClick={event => { if (event.target === event.currentTarget && !busy) setEditor(null); }}>
        <div role="dialog" aria-modal="true" aria-label={assignmentOnly ? 'Assign work' : 'Edit work'}
          className="max-h-[95vh] w-full overflow-y-auto rounded-t-xl bg-white p-4 shadow-2xl md:max-w-2xl md:rounded-xl">
        <form onSubmit={revise} className="space-y-3" aria-label="Edit project task">
        <div className="flex items-center justify-between gap-2">
          <h4 className="text-sm font-bold text-slate-900">{assignmentOnly ? 'Assign contributor' : 'Edit work'} · {editor.title}</h4>
          <button type="button" disabled={busy} className="wp-button"
            onClick={() => setEditor(null)}>Cancel edit</button>
        </div>
        {!assignmentOnly && <><label className="block text-sm font-semibold text-slate-800">Work title
          <input aria-label="Edit task title" required maxLength={180} value={editor.title}
            onChange={event => setEditor(value => ({ ...value, title: event.target.value }))}
            className="mt-1 w-full rounded-lg border border-slate-300 bg-white p-2.5 text-sm font-normal text-slate-900"/>
        </label>
        <label className="block text-sm font-semibold text-slate-800">Description
          <textarea aria-label="Edit task description" rows={3} maxLength={5000} value={editor.description}
            onChange={event => setEditor(value => ({ ...value, description: event.target.value }))}
            className="mt-1 w-full rounded-lg border border-slate-300 bg-white p-2.5 text-sm font-normal text-slate-900"/>
        </label>
        </>}
        <div className={assignmentOnly ? 'grid gap-3' : 'grid gap-3 sm:grid-cols-2'}>
          {!assignmentOnly && <ProjectWorkDateField label="Edit task due date" value={editor.due_date}
            onChange={date => setEditor(previous => ({ ...previous, due_date: date }))}/>}
          <label className="block text-sm font-semibold text-slate-800">Assigned contributor
            <select aria-label="Reassign task" value={editor.assignee_principal_id}
              onChange={event => setEditor(value => ({ ...value, assignee_principal_id: event.target.value }))}
              className="mt-1 w-full rounded-lg border border-slate-300 bg-white p-2.5 text-sm font-normal text-slate-900">
              <option value="">Unassigned</option>
              {participants.map(person => <option key={person.principal_id} value={person.principal_id}>
                {contributorName(person.principal_id)}
              </option>)}
              {editor.assignee_principal_id && !participants.some(person =>
                person.principal_id === editor.assignee_principal_id) &&
                <option value={editor.assignee_principal_id} disabled>
                  Current assignee not on verified page — choose a current contributor
                </option>}
            </select>
          </label>
        </div>
        {!assignmentOnly && <p className="text-xs text-slate-600">Parent, predecessors and milestone type remain immutable. Reassignment requires a current exact-project Contributor.</p>}
        <button type="submit" className="wp-button wp-button-primary"
          disabled={busy || !(assignmentOnly ? actionCapabilities?.canAssign : actionCapabilities?.canEdit)
            || !editor.title.trim() || Boolean(
            editor.assignee_principal_id && !participants.some(person =>
              person.principal_id === editor.assignee_principal_id))
            || (assignmentOnly && (editor.assignee_principal_id || null)
              === (items.find(item => item.task_id === editor.task_id)?.assignee_principal_id || null))}>
          {assignmentOnly ? 'Save assignment' : 'Save changes to EOS'}
        </button>
        </form>
        </div>
      </div>}
      <div className="mt-4 overflow-x-auto rounded-xl border border-slate-200" role="region" aria-label="Verified project tasks" tabIndex={0}>
        <table role="grid" aria-label="Project work grid" data-density={workDensity}
          className="w-full min-w-[580px] border-collapse text-left text-sm">
          <thead className="bg-slate-100 text-xs font-bold text-slate-700">
            <tr><th scope="col" className="w-10 p-2">
              <input type="checkbox" aria-label="Select all visible work"
                checked={workRows.length > 0 && workRows.every(item => selectedWorkIds.includes(item.task_id))}
                disabled={workRows.length === 0}
                onChange={event => setSelectedWorkIds(previous => event.target.checked
                  ? [...new Set([...previous, ...workRows.map(item => item.task_id)])]
                  : previous.filter(id => !workRows.some(item => item.task_id === id)))}/>
            </th><th scope="col" className="p-3">Work item</th><th scope="col" className="p-3">Status</th>
              <th scope="col" className="p-3">Assignee</th><th scope="col" className="p-3">Due</th>
              <th scope="col" className="p-3">Next action</th></tr>
          </thead>
          <tbody className="divide-y divide-slate-200">
            {groupedWorkRows.map(group => <React.Fragment key={group.key}>
              {group.title && <tr className="bg-slate-100">
                <th colSpan={6} scope="rowgroup" className="px-3 py-2 text-left text-xs font-bold text-slate-800">
                  {group.title} · {group.rows.length} on this page
                </th>
              </tr>}
              {group.rows.map(item => <ProjectWorkRow key={item.task_id}
              item={item} selected={selectedWorkIds.includes(item.task_id)}
              density={workDensity} busy={busy}
              pendingStatus={pendingTransition?.taskId === item.task_id ? pendingTransition.status : null}
              todayISO={todayISO} assigneeName={contributorName}
              onToggleSelect={(id, checked) => setSelectedWorkIds(previous => checked
                ? [...previous, id] : previous.filter(value => value !== id))}
              onOpen={(selected, element) => {
                drawerReturnFocus.current = element;
                setDrawerTaskId(selected.task_id);
              }}
              onAssign={selected => openTaskEditor(selected, true)}
              onEdit={openTaskEditor} onTransition={transition}
              onComplete={selected => {
                setCompletionCandidate(selected.task_id);
                setCompletionAttested(false);
              }}
              onAttachments={selected => setAttachmentTaskId(selected.task_id)}
              onApprovals={selected => setApprovalTaskId(selected.task_id)}
              onActivity={selected => setDiscussionTaskId(selected.task_id)}
              capabilities={actionCapabilities || { canStart: false, canComplete: false,
                canBlock: false, canCancel: false, canEdit: false, canAssign: false }}/>)}
            </React.Fragment>)}
            {workRows.length === 0 && <tr><td colSpan={6} className="p-6 text-center text-sm text-slate-600">
              {items.length === 0 ? 'EOS verified no tasks on this page. Create work to begin execution.'
                : 'No work items on this verified page match the selected search and filters.'}
            </td></tr>}
          </tbody>
        </table>
      </div>



        {completingItem && <div role="dialog" aria-modal="true" aria-label="Confirm verified task completion"
          className="fixed inset-x-4 top-1/4 z-[110] mx-auto max-w-xl rounded-xl border border-blue-300 bg-white p-5 shadow-2xl">
          <h5 className="text-sm font-bold text-slate-900">Confirm completion · {completingItem.title}</h5>
          <p className="mt-2 text-xs text-slate-700">This is a terminal EOS lifecycle command. Verify acceptance and supporting evidence first; a checkbox alone does not certify evidence, an approval or a milestone.</p>
          <label className="mt-3 flex items-start gap-2 text-sm text-slate-900">
            <input type="checkbox" className="mt-1 size-4" checked={completionAttested}
              onChange={event => setCompletionAttested(event.target.checked)}/>
            <span>I reviewed this task's acceptance and supporting evidence.</span>
          </label>
          <div className="mt-3 flex flex-wrap gap-2">
            <button type="button" className="wp-button wp-button-primary" disabled={busy || !actionCapabilities?.canComplete || !completionAttested}
              onClick={() => transition(completingItem, 'DONE')}>Confirm Done in EOS</button>
            <button type="button" className="wp-button" disabled={busy} onClick={() => {
              setCompletionCandidate(null);
              setCompletionAttested(false);
            }}>Cancel</button>
            <button type="button" className="wp-button" disabled={busy}
              onClick={() => setAttachmentTaskId(completingItem.task_id)}>Review attachments</button>
          </div>
        </div>}
      {drawerTask && <div className="fixed inset-0 z-[85] bg-slate-950/35"
        onClick={event => { if (event.target === event.currentTarget) closeDrawer(); }}>
        <aside role="dialog" aria-modal="true"
          aria-label={'Work details: ' + drawerTask.title} ref={drawerRef}
          className="absolute inset-y-0 right-0 flex w-full max-w-xl flex-col overflow-auto border-l border-slate-200 bg-white p-5 shadow-2xl md:p-6">
          <div className="mb-4 flex items-center justify-between gap-3 border-b border-slate-200 pb-3">
            <p className="text-xs font-semibold text-slate-600">
              {drawerTask.kind === 'MILESTONE' ? 'Milestone'
                : drawerTask.parent_task_id ? 'Subtask' : 'Task'}
            </p>
            <button type="button" onClick={closeDrawer}
              className="wp-button" aria-label="Close work details">Close</button>
          </div>
          <h3 className="text-xl font-bold text-slate-950">{drawerTask.title}</h3>
          <div className="mt-3 flex flex-wrap items-center gap-3 text-sm text-slate-800">
            <span className="rounded-md bg-slate-100 px-2 py-1 font-semibold">{label(drawerTask.status)}</span>
            <span>{drawerTask.due_date ? 'Due ' + drawerTask.due_date : 'No due date'}</span>
            {drawerTask.assignee_principal_id
              ? <span>{contributorName(drawerTask.assignee_principal_id)}</span>
              : <span>Not assigned</span>}
          </div>
          <section className="mt-6 border-t border-slate-200 pt-4">
            <h4 className="text-sm font-bold text-slate-900">Description</h4>
            <p className="mt-2 whitespace-pre-wrap break-words text-sm leading-relaxed text-slate-800">
              {drawerTask.description || 'No description recorded'}
            </p>
          </section>
          <section className="mt-5 border-t border-slate-200 pt-4">
            <h4 className="text-sm font-bold text-slate-900">Dependencies</h4>
            {drawerTask.depends_on.length === 0
              ? <p className="mt-2 text-sm text-slate-600">No predecessors</p>
              : <ul className="mt-2 space-y-2">
                {drawerTask.depends_on.map(id => {
                  const predecessor = items.find(value => value.task_id === id);
                  return <li key={id} className="text-sm text-slate-800">
                    {predecessor ? predecessor.title + ' · ' + label(predecessor.status)
                      : 'Predecessor outside the current verified page'}
                  </li>;
                })}
              </ul>}
          </section>
          <div className="mt-auto flex flex-wrap gap-2 border-t border-slate-200 pt-4">
            {!['DONE', 'CANCELLED'].includes(drawerTask.status) &&
              <button type="button" className="wp-button" onClick={() => {
                const item = drawerTask; closeDrawer(); openTaskEditor(item);
              }}>Edit / assign</button>}
            <button type="button" className="wp-button" onClick={() => {
              const item = drawerTask; closeDrawer(); setDiscussionTaskId(item.task_id);
            }}>Activity &amp; discussion</button>
            <button type="button" className="wp-button" onClick={() => {
              const item = drawerTask; closeDrawer(); setAttachmentTaskId(item.task_id);
            }}>Attachments</button>
            <button type="button" className="wp-button" onClick={() => {
              const item = drawerTask; closeDrawer(); setApprovalTaskId(item.task_id);
            }}>Approvals</button>
          </div>
        </aside>
      </div>}
      {(hasMore || offset > 0) && <nav className="mt-3 flex items-center justify-between gap-2" aria-label="Task pages">
        <button type="button" className="wp-button" disabled={busy || offset === 0}
          onClick={() => void load(Math.max(0, offset - 50))}>Previous work</button>
        <span className="text-xs text-slate-600">Page {Math.floor(offset / 50) + 1}</span>
        <button type="button" className="wp-button" disabled={busy || !hasMore}
          onClick={() => void load(offset + 50)}>Next work</button>
      </nav>}
    </>)}
    {state === 'READY' && error && <div role="alert"
      className="fixed bottom-4 left-4 right-4 z-[120] flex max-w-md items-start justify-between gap-3 rounded-xl border border-rose-300 bg-white p-4 text-sm text-rose-900 shadow-xl sm:left-auto sm:right-6">
      <span className="min-w-0 flex-1">{error}</span>
      <button type="button" className="shrink-0 rounded-md border border-rose-300 px-2 py-1 font-semibold text-rose-900 focus-visible:outline focus-visible:outline-2 focus-visible:outline-blue-700"
        onClick={() => setError('')}>Dismiss error</button>
    </div>}
  </section>;
}

// ARTIFACT: ProjectTasksPanel.jsx
// VERSION: v1.32.0-SELECTED-TASK-AI-LOCATOR-HANDOFF
// AUTHORITY BOUNDARY: EOS-verified owner task commands; no local state authority
// TENANT POSTURE: exact session tenant/principal/project readback, no fallback
// FAIL-CLOSED POSTURE: invalid data, denied commands and uncertain source stay visible
// FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
// END OF WILSY OS SOVEREIGN ARTIFACT
