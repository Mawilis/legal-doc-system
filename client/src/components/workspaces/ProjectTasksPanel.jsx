/**
 * TITLE: WILSY OS Project Work Execution Panel
 * VERSION: v1.71.0-TASK-NATIVE-INTELLIGENCE-ACTIONS
 * AUTHORITY: Python EOS Projects task and participant HTTP APIs exclusively.
 * EPITOME: Real task, subtask, milestone and dependency actions with durable
 *          EOS readback, selected project scope and no synthetic task state.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/components/workspaces/ProjectTasksPanel.jsx
 * COLLABORATION / OWNERSHIP: ProjectsWorkspace mounts the authorized owner
 *          detail; api.js supplies session transport; EOS owns task commands.
 * CERTIFICATION / UPDATE DATE: 2026-11-26
 * CHANGELOG: v1.71.0-TASK-NATIVE-INTELLIGENCE-ACTIONS replaces dark duplicate task transcript with a compact source-verified assessment using the same canonical EOS brief and task-owned Activity/Evidence/Approvals navigation; no new workflow or model entitlement. Modal context and keyboard safety remain unchanged.
 * CHANGELOG: v1.70.0-IN-TASK-INTELLIGENCE-VIEW offers a source-authorized WILSY AI task brief inside the current task modal, with a deliberate transition to full Dock conversation and exact task locator. Keeps the external floating Dock hidden while modal is active; source/IAM remain EOS owned.
 * CHANGELOG: v1.69.1-SINGLE-TASK-MODAL-EXIT keeps the
 *          parent's accessible Back to Work action as the sole modal exit
 *          for discussion, aligning with existing Files and Approvals
 *          controls; removes the nested duplicate Close button without
 *          altering focus restoration, permissions or task selection.
 * CHANGELOG: v1.69.0-SINGLE-TASK-SCOPE-READ defers the initial
 *          task-list and optional authority requests beyond discarded
 *          React StrictMode effect setup. Source-driven refresh, exact
 *          tenant validation, IAM and command semantics remain unchanged.
 * CHANGELOG: v1.68.0-STABLE-PROJECT-AUTHORITY-READS stabilizes
 *          semantically identical tenant selector headers so parent rerenders
 *          cannot restart task list and three optional authority GETs.
 *          A changed header still revalidates all sources, without extending
 *          timeouts, caching IAM, or changing EOS admission.
 * CHANGELOG: v1.67.0-CENTERED-TASK-ACTION-WORKSPACE returns Files,
 *          Approvals and Activity to the centered Projects task work surface;
 *          a bounded resizable dialog replaces the pinned right-side panel.
 *          Preserves existing exact-task authority and keyboard focus.
 * CHANGELOG: v1.66.0-GOVERNED-READINESS-ROLLBACK adds a read-only MW-T12 readiness and
 *          rollback inspection using exact-task EOS attachment and business
 *          decision manifests, with release explicitly blocked absent
 *          independent deployment and rollback certification.
 * CHANGELOG: v1.65.0-SOURCE-VERIFIED-EXECUTION-READINESS makes task execution
 *          readiness reflect the current EOS source facts, exposes direct
 *          evidence/approval/activity actions, and does not infer production
 *          certification from task status. The approved Projects UI remains.

 * COMPLIANCE: AGENTS.md; POPIA section 19; GDPR Article 32; WCAG 2.2 AA.
 * SECURITY / PRIVACY POSTURE: Text only, no HTML parsing, AI execution, bearer
 *          extraction, fabricated task metrics or inferred notifications.
 * TENANT BOUNDARY: Exact tenant, principal and project validated on every
 *          response; stale session results are ignored and discarded.
 * AUTHORITY BOUNDARY: UI actions do not grant contributor, employee or owner
 *          rights; EOS checks each mutation and recorded assignment.
 * FINANCIAL AUTHORITY BOUNDARY: Kennel EOS is the sole financial executor.
 * CHANGELOG: v1.64.0-CONTEXTUAL-ACTIVITY-REVIEWER-UX
 *          bounds the task workspace to its content instead of
 *          stretching empty activity to viewport height; avoids duplicate
 *          close actions and passes the separately source-verified
 *          participant authority to approvals for reviewer discovery.
 * CHANGELOG: v1.63.0-WORK-LIST-FIRST-LAYOUT puts the source-
 *          verified work grid immediately after the compact filters
 *          and context strip, moving lifecycle and checklist into one
 *          below-list optional disclosure. The queue stays primary
 *          and the same authorized actions remain available.
 * CHANGELOG: v1.62.1-BOUNDED-CONTEXT-PANE-WIDTH prevents
 *          viewport overflow by resolving inset-constrained width
 *          instead of combining 100%-width with left/right gutters.
 * CHANGELOG: v1.62.0-FOCUSED-IN-PLACE-TASK-WORKSPACE
 *          retains the verified work grid mounted behind a bounded
 *          task-action workspace, rather than destroying and replacing
 *          the queue. Activity, files, approvals and detail share the
 *          selected task context. Escape, keyboard focus and scroll
 *          restoration make focus reversible without a second workflow.
 * CHANGELOG: v1.61.0-GOVERNED-MULTI-ASSIGNMENT provides
 *          explicit multi-selection assignment to one EOS-verified
 *          contributor. Each selected active task receives its own
 *          revision-guarded PATCH and independent exact-scope list
 *          readback before the next command. Ambiguous outcomes halt
 *          without retries; no bulk permission or server endpoint is
 *          invented. A bounded summary reports confirmed/uncertain work.
 * CHANGELOG: v1.60.1-TRIAGE-DATE-ORDER declares the
 *          browser-local comparison date before the memoized verified
 *          task filter evaluates, preventing a render-time TDZ fault.
 * CHANGELOG: v1.60.0-ACTIONABLE-VERIFIED-TRIAGE adds
 *          source-scoped work attention filters for unassigned and
 *          blocked/overdue tasks; selected sets can be populated from
 *          only visible verified records. A selected-work review remains
 *          independently EOS authorized; no aggregate mutation, AI
 *          invented ranking, or unsupported critical-path claim.
 * CHANGELOG: v1.59.0-UNIFIED-EXECUTION-CONTINUITY brings
 *          task files, discussion, approvals and details into one
 *          compact task-local navigation. A session-scoped recent-work
 *          index stores only task ids and visit counts, never task
 *          content or authority; every Resume action first requires an
 *          exact current EOS task readback. Derived work-risk counts
 *          explicitly cover the current verified batch only.
 * CHANGELOG: v1.58.0-DEPENDENCY-ORDERED-REVIEW applies
 *          a bounded topological order to explicitly selected,
 *          source-verified work, presenting known predecessors before
 *          dependent successors in sequential review. It never changes
 *          EOS lifecycle or declares off-page dependencies satisfied.
 * CHANGELOG: v1.57.2-HIERARCHY-SCOPE-AND-FOCUS-GUARD
 *          keeps compact/hierarchy defaults after the authenticated
 *          scope reset and makes optional visual scrolling work across
 *          browser/test implementations without bypassing task focus.
 * CHANGELOG: v1.57.1-SOVEREIGN-HEADER-RESTORE moves the
 *          mandatory authority and financial boundaries ahead of the
 *          historical changelog within the first-100-line integrity guard.
 *          No runtime business or command behavior changes.
 * CHANGELOG: v1.57.0-SOURCE-OWNED-TASK-HIERARCHY defaults
 *          to compact source-owned parent/subtask ordering, with
 *          milestone records visible as distinct root nodes. This does
 *          not invent absent milestone-to-task membership. Removes the
 *          duplicate upper pagination card while retaining the lower
 *          bounded verified-batch pager and manual grouping choices.
 * CHANGELOG: v1.56.0-EXPLAINABLE-DEPENDENCY-BLOCKERS
 *          shows source-verified incomplete predecessors and disables
 *          final completion attestation when a known current-page blocker
 *          remains. Unknown off-page predecessors are never assumed done;
 *          Python EOS independently enforces all dependency gates.
 *          The task inspector also distinguishes downstream tasks in
 *          the exact currently verified project batch.
 * CHANGELOG: v1.55.0-SOURCE-BACKED-SUBTASK-HANDOFF
 *          wires the row's Add subtask menu item into the existing,
 *          authenticated task-create form prefilled with a verified
 *          source parent. Reuses exact-project permission, validation,
 *          idempotency, audit, persisted readback and focused scrolling.
 * CHANGELOG: v1.54.0-FOCUSED-TASK-CONTEXT suppresses
 *          project-level create/refresh while working on one task's files,
 *          discussion or approvals. Replaces duplicate context cards with
 *          one compact in-place task breadcrumb and preserves the existing
 *          authorized task-action panel and return path.
 * CHANGELOG: v1.53.0-IN-GRID-MULTI-SELECTION moves the
 *          multiple-selection command strip inside the exact work grid
 *          beside its Select all checkbox, removes the disconnected
 *          toolbar and keeps per-task actions in each selected work row.
 *          Review is sequential; EOS owns each task command and readback.
 * CHANGELOG: v1.52.0-SELECTION-IN-ROW-ROUTING routes one
 *          selected task to inline work-row controls and reserves the
 *          existing small toolbar for multiple selections only. Existing
 *          delegated EOS handlers, capability gates, task revisions,
 *          authenticated readbacks and review navigation are preserved.
 * CHANGELOG: v1.51.1-SELECTION-JSX-BOUNDARY closes the conditional
 *          selected-work toolbar JSX expression before subsequent queue
 *          controls, restoring valid render structure without changing
 *          EOS permissions, actions, task state, or source readback.
 * CHANGELOG: v1.51.0-ACTIONABLE-SELECTION-REVIEW adds a
 *          source-backed sequence for reviewing selected tasks and a single
 *          task assign/schedule command entry. Batch lifecycle commands
 *          remain prohibited without separately verified EOS authority.
 * CHANGELOG: v1.50.0-COMPACT-DELIVERY-EDITOR
 *          makes the work editor's supporting description collapsible and
 *          uses a restrained neutral accountability surface with clear
 *          contrast; assignment and date remain immediately available.
 * CHANGELOG: v1.49.2-PENDING-CAPABILITY-ACTION-LABEL
 *          keeps pending authority label consistent without implying
 *          assignment-only permission or enabling a command prematurely.
 * CHANGELOG: v1.49.1-OPTIONAL-READ-FAIL-CLOSED
 *          detached auxiliary source readbacks reject fail-closed without
 *          unhandled promise rejection or stale capability reuse.
 * CHANGELOG: v1.49.0-FAST-VERIFIED-SAVE-READBACK
 *          releases completed task command UI after mandatory verified task
 *          list readback, never after unverified mutation success, without
 *          awaiting unrelated contributor/member/capability transport.
 *          Separate contributor admission still waits for fresh proof.
 * CHANGELOG: v1.48.0-ASSIGNEE-FIRST-DELIVERY-COMMANDS
 *          makes contributor selection first, keeps date selection adjacent,
 *          labels the action by exact granted capability and replaces user-
 *          facing backend wording without changing command authorization.
 * CHANGELOG: v1.47.0-ACCOUNTABLE-TASK-EDITOR
 *          prioritizes assignment and due dates in the existing drawer,
 *          puts accountable delivery first in edit form and collapses
 *          secondary classification details. All source permissions,
 *          CAS task revisions and independent readbacks remain intact.
 * CHANGELOG: v1.46.0-NONBLOCKING-OPTIONAL-TASK-SOURCES
 *          admits the already verified task list and exact task drawer
 *          immediately after EOS list validation, while contributor,
 *          capability and member-directory reads settle independently.
 *          All mutations remain disabled until exact-scope capability
 *          readback; no inferred people, grants, task completion or retry.
 * CHANGELOG: v1.45.0-SOURCE-VERIFIED-TASK-FOCUS
 *          opens an exact task passed from Strategy only when it appears in
 *          the independently authorized project work readback. An outage
 *          never fabricates the task or bypasses permissions. This remains
 *          an existing task drawer, not a new editing authority.
 * CHANGELOG: v1.44.0-BOUNDED-WORK-QUEUE-PAGING introduces
 *          ten-row default client paging inside each independently verified
 *          50-record EOS batch, with 10/20/50 page sizes and bidirectional
 *          controls. Search, sort and selection remain exact-batch only.
 * CHANGELOG: v1.43.0-SOURCE-OWNED-DEPENDENT-TASK-HANDOFF replaces
 *          misleading existing-predecessor editing with the canonical
 *          audited task-creation flow preselected with one verified predecessor.
 *          EOS preserves immutable existing graphs, task IAM and CAS.
 * CHANGELOG: v1.42.1-CENTERED-TASK-WORKSPACE replaces the narrow right-anchored
 *          sheet with a centered viewport-bounded responsive task workspace.
 *          No change to EOS commands, authorizations, task data or readback.
 * CHANGELOG: v1.42.0-EXECUTION-FIRST-TASK-DRAWER reorganizes the existing
 *          verified task details around visible execution actions, overdue
 *          dates, source context and dependencies; EOS commands unchanged.
 * CHANGELOG: v1.41.0-SOURCE-AUDITED-WORK-PURPOSE-ACTION mounts
 *          the independently authorized source classification command
 *          directly inside selected task details with fresh EOS audit readback,
 *          no inferred purpose, task mutation or simulated IAM.
 * CHANGELOG: v1.40.0-ATTACHMENT-CONTRIBUTOR-NAVIGATION passes project People navigation into both selected-task attachment views, so owner-view upload prerequisites have a real navigation action instead of an inert advisory.
 * CHANGELOG: v1.39.0-SANITIZED-EOS-TASK-ERROR-CODE-DIAGNOSTICS exposes only strict canonical PROJECT_ uppercase backend error codes alongside HTTP state, without logging source payloads, identity, URLs or unknown exception text. Helps differentiate unavailable task transport from malformed persisted records at the next browser acceptance.
 * CHANGELOG: v1.38.0-PRIMARY-TASK-READ-FIRST-AND-EXPLICIT-HTTP-DIAGNOSTICS verifies the sovereign task list before starting three auxiliary source calls so new member-directory lookups cannot compete with the critical task read. Distinguishes rejected 401/403/404/429/503, transport timeout and malformed read envelopes without logging secrets, losing task drafts, fabricating task rows or retrying commands.
 * CHANGELOG: v1.37.0-INDEPENDENT-TASK-AND-CONTRIBUTOR-READ-FAILURE-BOUNDARIES isolates task, participant and eligible-member reads, preserves only independently verified EOS tasks when a participant directory is denied/unavailable, and gates all contributor/assignee operations until current project participation verifies. Reports which source failed without guessing people, tasks or permissions.
 * CHANGELOG: v1.36.0-TENANT-MEMBER-ASSIGNEE-CHOICES lists exact-tenant currently eligible named member candidates in the assignee selector while keeping only active project contributors directly assignable. Candidate selection opens explicit separate contributor grant; fresh EOS readback must verify new project participation before setting draft assignee. No hidden grants, role inheritance, or synthetic people.
 * CHANGELOG: v1.35.0-ASSIGNEE-DIALOG-VIEWPORT-REPAIR moves governed member selection from above the create form to an immediately visible, viewport-bound dialog with dedicated scrolling and Escape dismissal; preserves active draft and verifies participant grant before assignee refresh. No automatic member or IAM grant.
 * CHANGELOG: v1.34.0-ALWAYS-VISIBLE-WORK-SELECTION-CURRENTNESS keeps exact-page selection status visible while optional work-filter controls are collapsed, without changing selection authority or mutations.
 * CHANGELOG: v1.33.0-INLINE-CONTRIBUTOR-ADMISSION-AND-COLLAPSIBLE-WORK-FILTERS exposes a contextual inline governed contributor-management workflow when no assignees are admitted, refreshes only after source-confirmed participant changes while keeping unsaved task drafts, and collapses the page-only work filters by default. No IAM shortcuts or task mutation semantics altered.
 * CHANGELOG: v1.32.0-SELECTED-TASK-AI-LOCATOR-HANDOFF emits a bounded, EOS-hydrated task id/revision
 *          to the parent while a detail, editor or task discussion is in view;
 *          selection clears on dismissal, remount or source unavailability.
 *          Source content and permission claims never leave this component.
 * CHANGELOG: v1.31.0-POST-CREATE-EVIDENCE-HANDOFF offers a direct governed task
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
import UnifiedTaskReadiness from './UnifiedTaskReadiness.jsx';
import UnifiedTaskHeader from './UnifiedTaskHeader.jsx';
import React, { useCallback, useEffect, useId, useMemo, useRef, useState } from 'react';
import { CalendarDays, CheckCircle2, CirclePause, ClipboardList, LoaderCircle, Plus, RefreshCw, Waypoints } from 'lucide-react';
import api from '../../services/api.js';
import ProjectTaskCommentsPanel from './ProjectTaskCommentsPanel.jsx';
import ProjectWorkRow from './ProjectWorkRow.jsx';
import ProjectNotesPanel from './ProjectNotesPanel.jsx';
import ProjectTaskApprovalsPanel from './ProjectTaskApprovalsPanel.jsx';
import ProjectTaskAttachmentsPanel from './ProjectTaskAttachmentsPanel.jsx';
import ProjectWorkPurposePanel from './ProjectWorkPurposePanel.jsx';
import ProjectParticipantsPanel, { validOptions, optionName } from './ProjectParticipantsPanel.jsx';
import WilsyDockOperatingWork from '../intelligence/WilsyDockOperatingWork.jsx';

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

/**
 * @description Inspect one readiness task's independently scoped evidence and
 * reviewer-decision manifests. This is a non-authorizing projection; neither
 * task completion nor business approvals establish deployment/rollback truth.
 * @authority Python EOS owns every record; production release requires a
 * separately certified release authority not represented by these endpoints.
 * @tenant Exact tenant, actor, project and task match required on every page.
 * @mutation None. Reads are canceled and invalidated on scope/revision change.
 */
function ProjectReadinessRollback({ task, tenantId, principalId, projectId, headers, onOpenEvidence, onOpenApprovals }) {
  const [snapshot, setSnapshot] = useState({ state: 'IDLE', attachments: [], approvals: [], issue: '' });
  const generation = useRef(0);
  const controllerRef = useRef(null);
  const key = [tenantId, principalId, projectId, task.task_id, task.revision].join('\u0000');
  const load = useCallback(async () => {
    const request = ++generation.current;
    controllerRef.current?.abort();
    const controller = new AbortController();
    controllerRef.current = controller;
    setSnapshot({ state: 'LOADING', attachments: [], approvals: [], issue: '' });
    const base = '/projects/' + encodeURIComponent(projectId) + '/tasks/' + encodeURIComponent(task.task_id);
    try {
      const results = await Promise.all([
        api.get(base + '/attachments?limit=50&offset=0', { headers, signal: controller.signal }),
        api.get(base + '/approvals?limit=50&offset=0', { headers, signal: controller.signal }),
      ]);
      if (request !== generation.current) return;
      const [evidence, decisions] = results.map(result => result.data);
      const scopedPage = (page, schema) => page?.schema === schema
        && page.tenant_id === tenantId && page.principal_id === principalId
        && page.project_id === projectId && page.task_id === task.task_id
        && page.offset === 0 && page.limit === 50
        && Array.isArray(page.items) && page.items.length <= 50
        && page.has_more === false && page.next_offset === null;
      const validEvidence = item => item?.schema === 'wilsy.project.attachment.v1'
        && item.tenant_id === tenantId && item.project_id === projectId
        && item.task_id === task.task_id && /^pat-[a-f0-9]{48}$/.test(item.attachment_id || '')
        && typeof item.filename === 'string' && item.filename.length > 0 && item.filename.length <= 255
        && ['application/pdf', 'image/png', 'image/jpeg'].includes(item.media_type)
        && Number.isSafeInteger(item.size_bytes) && item.size_bytes > 0 && item.size_bytes <= 20 * 1024 * 1024
        && item.state === 'QUARANTINED' && item.revision === 1
        && /^[a-f0-9]{128}$/.test(item.content_sha3_512 || '')
        && ['QUARANTINED', 'SCAN_CLEAN_VERIFIED'].includes(item.scan_clearance_status)
        && (item.scan_clearance_status === 'QUARANTINED'
          ? item.scan_clearance_fingerprint === null
          : /^[a-f0-9]{128}$/.test(item.scan_clearance_fingerprint || ''))
        && !Object.hasOwn(item, 'download_url') && !Object.hasOwn(item, 'presigned_url')
        && !Object.hasOwn(item, 'storage_receipt');
      const validDecision = item => item?.schema === 'wilsy.project.approval.v1'
        && item.tenant_id === tenantId && item.project_id === projectId
        && item.task_id === task.task_id && /^par-[a-f0-9]{48}$/.test(item.approval_id || '')
        && ['PENDING', 'APPROVED', 'REJECTED'].includes(item.status)
        && item.requester_principal_id !== item.reviewer_principal_id
        && typeof item.requester_principal_id === 'string'
        && typeof item.reviewer_principal_id === 'string'
        && item.revision === (item.status === 'PENDING' ? 1 : 2)
        && typeof item.rationale === 'string' && item.rationale.length > 0
        && (item.status === 'PENDING'
          ? item.decided_at === null && item.decision_rationale === null
          : typeof item.decided_at === 'string' && typeof item.decision_rationale === 'string')
        && (item.evidence_attachment_ids === undefined
          || (Array.isArray(item.evidence_attachment_ids)
            && item.evidence_attachment_ids.length <= 10
            && item.evidence_attachment_ids.every(id => /^pat-[a-f0-9]{48}$/.test(id))
            && new Set(item.evidence_attachment_ids).size === item.evidence_attachment_ids.length))
        && /^[a-f0-9]{128}$/.test(item.fingerprint || '');
      if (!scopedPage(evidence, 'WILSY-PROJECT-ATTACHMENT-LIST/V1')
        || !scopedPage(decisions, 'WILSY-PROJECT-APPROVAL-LIST/V1')
        || !evidence.items.every(validEvidence) || !decisions.items.every(validDecision)
        || new Set(evidence.items.map(item => item.attachment_id)).size !== evidence.items.length
        || new Set(decisions.items.map(item => item.approval_id)).size !== decisions.items.length) {
        throw new Error('SOURCE_MANIFEST_INVALID');
      }
      setSnapshot({ state: 'VERIFIED', attachments: evidence.items, approvals: decisions.items, issue: '' });
    } catch (error) {
      if (request !== generation.current) return;
      if (error?.name === 'CanceledError' || error?.name === 'AbortError') return;
      setSnapshot({ state: 'UNVERIFIED', attachments: [], approvals: [],
        issue: 'At least one independent EOS record could not be verified. Review the source panels and retry.' });
    }
  }, [key]);
  useEffect(() => {
    void load();
    return () => {
      generation.current += 1;
      controllerRef.current?.abort();
    };
  }, [load]);
  const clean = snapshot.attachments.filter(item => item.scan_clearance_status === 'SCAN_CLEAN_VERIFIED').length;
  const pending = snapshot.approvals.filter(item => item.status === 'PENDING').length;
  const rejected = snapshot.approvals.filter(item => item.status === 'REJECTED').length;
  const approved = snapshot.approvals.filter(item => item.status === 'APPROVED').length;
  const row = (name, result, detail) => <li className="grid gap-1 border-b border-slate-200 py-3 last:border-0 sm:grid-cols-[minmax(160px,1fr)_minmax(180px,2fr)]">
    <span className="font-semibold text-slate-950">{name}</span>
    <span className="text-slate-700"><strong className="mr-2 text-slate-900">{result}</strong>{detail}</span>
  </li>;
  return <section aria-label="MW-T12 readiness and rollback" className="mt-4 rounded-xl border border-slate-300 bg-white p-4">
    <div className="flex flex-wrap items-start justify-between gap-3">
      <div>
        <h4 className="text-base font-bold text-slate-950">Readiness &amp; rollback</h4>
        <p className="mt-1 text-sm text-slate-700">Independent EOS task evidence and reviewer decisions. Production release is not authorized here.</p>
      </div>
      <button type="button" disabled={snapshot.state === 'LOADING'} onClick={() => void load()}
        className="min-h-10 rounded-lg border border-slate-300 bg-white px-3 text-sm font-semibold text-slate-900 hover:bg-slate-100 disabled:opacity-50">
        <RefreshCw size={14} className="mr-2 inline"/> Verify sources
      </button>
    </div>
    {snapshot.state === 'LOADING' && <p role="status" className="mt-3 text-sm text-slate-700">Checking independent EOS evidence and decisions…</p>}
    {snapshot.state === 'UNVERIFIED' && <p role="alert" className="mt-3 text-sm font-semibold text-rose-800">{snapshot.issue}</p>}
    <ul className="mt-3 text-sm">
      {row('Authenticated test certification', 'Not certified', 'CI and authenticated production-like test evidence are not certified by these task APIs.')}
      {row('MongoDB and runtime resilience', 'Not certified', 'Primary recovery, latency, TLS and operational SLO evidence require separate certification.')}
      {row('IAM / tenant isolation', 'Not certified', 'Current task access does not prove a complete security-role test matrix.')}
      {row('Rollback drill', 'Not certified', 'No source-verified rollback execution and recovery result is available from these APIs.')}
      {row('Task attachments', snapshot.state === 'VERIFIED' ? clean + ' scan-clean verified' : 'Unverified',
        snapshot.state === 'VERIFIED' ? ' of ' + snapshot.attachments.length + ' attachments; clean scan does not certify test content.' : 'The attachment manifest is not currently verified.' )}
      {row('Independent task reviews', snapshot.state === 'VERIFIED' ? approved + ' approved' : 'Unverified',
        snapshot.state === 'VERIFIED' ? ' · ' + pending + ' pending · ' + rejected + ' rejected. Business decisions are not release approvals.' : 'The approval manifest is not currently verified.')}
      {row('Production release permission', 'BLOCKED', 'No independent deployment certification or authorized release decision is established.')}
    </ul>
    {snapshot.state === 'VERIFIED' && <div className="mt-3 grid gap-3 md:grid-cols-2" aria-label="Verified task evidence and decisions">
      <div className="rounded-lg border border-slate-200 bg-slate-50 p-3">
        <h5 className="text-sm font-bold text-slate-950">Recorded task attachments</h5>
        {snapshot.attachments.length === 0
          ? <p className="mt-2 text-xs text-slate-700">EOS verified no attachments for this task.</p>
          : <ul className="mt-2 space-y-2 text-xs text-slate-800">{snapshot.attachments.map(item =>
            <li key={item.attachment_id} className="break-words border-b border-slate-200 pb-2 last:border-0">
              <strong>{item.filename}</strong>
              <span className="mt-1 block text-slate-600">{item.scan_clearance_status === 'SCAN_CLEAN_VERIFIED'
                ? 'Scan clearance verified · content certification still required'
                : 'Quarantined · scan clearance pending'}</span>
            </li>)}</ul>}
      </div>
      <div className="rounded-lg border border-slate-200 bg-slate-50 p-3">
        <h5 className="text-sm font-bold text-slate-950">Recorded reviewer decisions</h5>
        {snapshot.approvals.length === 0
          ? <p className="mt-2 text-xs text-slate-700">EOS verified no task review requests.</p>
          : <ul className="mt-2 space-y-2 text-xs text-slate-800">{snapshot.approvals.map(item =>
            <li key={item.approval_id} className="border-b border-slate-200 pb-2 last:border-0">
              <strong>{item.status}</strong>
              <span className="mt-1 block text-slate-600">Business task review · not release authority</span>
            </li>)}</ul>}
      </div>
    </div>}
    <div className="mt-3 flex flex-wrap gap-2">
      <button type="button" onClick={onOpenEvidence} className="min-h-11 rounded-lg border border-blue-700 bg-blue-800 px-4 text-sm font-semibold text-white hover:bg-blue-900">Inspect evidence</button>
      <button type="button" onClick={onOpenApprovals} className="min-h-11 rounded-lg border border-slate-300 bg-white px-4 text-sm font-semibold text-slate-900 hover:bg-slate-100">Inspect reviewer decisions</button>
    </div>
    <p className="mt-3 text-xs text-slate-600">This read-only assessment does not change task status, approve deployment, create certification evidence or execute a rollback.</p>
  </section>;
}

/** @description Display one exact-project task/participant workflow, never local truth. */
export default function ProjectTasksPanel({
  projectId, tenantId, principalId, tenantHeaders, discussionOnly = false,
  onFocusedTaskChange = null, onOpenProjectPeople = null, focusTaskId = null,
  onReturnToAttention = null,
}) {
  const [items, setItems] = useState([]);
  const handledExternalTaskFocus = useRef(null);
  const [participants, setParticipants] = useState([]);
  const [participantHasMore, setParticipantHasMore] = useState(false);
  const [tenantMemberCandidates, setTenantMemberCandidates] = useState([]);
  const [projectContributorStatus, setProjectContributorStatus] = useState('VERIFYING');
  const [projectContributorError, setProjectContributorError] = useState('');
  const [memberDirectoryStatus, setMemberDirectoryStatus] = useState('VERIFYING');
  const [pendingMemberChoice, setPendingMemberChoice] = useState('');
  const [actionCapabilities, setActionCapabilities] = useState(null);
  const [state, setState] = useState('LOADING');
  const [offset, setOffset] = useState(0);
  const [hasMore, setHasMore] = useState(false);
  const [draft, setDraft] = useState({ ...EMPTY });
  const [creating, setCreating] = useState(false);
  const [workType, setWorkType] = useState('TASK');
  const [workQuery, setWorkQuery] = useState('');
  const [workMineOnly, setWorkMineOnly] = useState(false);
  const [workAttention, setWorkAttention] = useState('ALL');
  const [selectedWorkIds, setSelectedWorkIds] = useState([]);
  const [bulkAssignment, setBulkAssignment] = useState(null);
  const [bulkProgress, setBulkProgress] = useState(null);
  const bulkLock = useRef(false);
  const [workDensity, setWorkDensity] = useState('compact');
  const [workStatus, setWorkStatus] = useState('ALL');
  const [workKind, setWorkKind] = useState('ALL');
  const [workGroup, setWorkGroup] = useState('HIERARCHY');
  const [workOrder, setWorkOrder] = useState('DUE_ASC');
  const [workViewSize, setWorkViewSize] = useState(10);
  const [workViewPage, setWorkViewPage] = useState(0);
  const [showContributorManagement, setShowContributorManagement] = useState(false);
  const [completionCandidate, setCompletionCandidate] = useState(null);
  const [completionAttested, setCompletionAttested] = useState(false);
  const [drawerTaskId, setDrawerTaskId] = useState(null);
  const [taskIntelligenceOpen, setTaskIntelligenceOpen] = useState(false);
  const [dependencyOriginId, setDependencyOriginId] = useState(null);
  const createFormRef = useRef(null);
  useEffect(() => {
    if (!creating || (!dependencyOriginId && workType !== 'SUBTASK')) return;
    const form = createFormRef.current;
    if (!form) return;
    form.scrollIntoView?.({ block: 'start', behavior: 'smooth' });
    form.querySelector('input[required]')?.focus({ preventScroll: true });
  }, [creating, dependencyOriginId, workType]);
  const drawerReturnFocus = useRef(null);
  const drawerRef = useRef(null);
  const focusedPanelRef = useRef(null);
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
  // The owner workspace may supply a fresh, equivalent headers object during
  // state changes. Keep the transport selector stable by value so the task
  // loader's effect is not restarted; changed headers still revalidate EOS.
  const headersRef = useRef(null);
  const incomingHeaders = tenantHeaders && typeof tenantHeaders === 'object'
    ? tenantHeaders : {};
  const previousHeaders = headersRef.current;
  const incomingKeys = Object.keys(incomingHeaders);
  if (!previousHeaders || incomingKeys.length !== Object.keys(previousHeaders).length
      || incomingKeys.some(key => previousHeaders[key] !== incomingHeaders[key])) {
    headersRef.current = { ...incomingHeaders };
  }
  const headers = headersRef.current;
  const historyStorageKey = 'wilsy:project-work:recent:' + encodeURIComponent(scope);
  const readRecent = () => {
    try {
      const raw = window.sessionStorage.getItem(historyStorageKey);
      const parsed = raw ? JSON.parse(raw) : null;
      if (!parsed || !Array.isArray(parsed.ids) || typeof parsed.counts !== 'object'
        || parsed.counts === null) return { scope, ids: [], counts: {} };
      const ids = parsed.ids.filter(id => typeof id === 'string' && id.length <= 96)
        .slice(0, 12);
      const counts = Object.fromEntries(ids.map(id => [
        id, Number.isSafeInteger(parsed.counts[id]) && parsed.counts[id] > 0
          ? Math.min(999, parsed.counts[id]) : 1,
      ]));
      return { scope, ids, counts };
    } catch {
      return { scope, ids: [], counts: {} };
    }
  };
  const [recentWork, setRecentWork] = useState(() => readRecent());
  const recordWorkVisit = task => {
    if (!task || !items.some(item => item.task_id === task.task_id)) return;
    const current = recentWork.scope === scope ? recentWork : { scope, ids: [], counts: {} };
    const ids = [task.task_id, ...current.ids.filter(id => id !== task.task_id)].slice(0, 12);
    const counts = { ...current.counts, [task.task_id]:
      Math.min(999, (current.counts[task.task_id] || 0) + 1) };
    const next = { scope, ids, counts };
    setRecentWork(next);
    try {
      window.sessionStorage.setItem(historyStorageKey, JSON.stringify({ ids, counts }));
    } catch {
      // Storage denial affects only the personal navigation shortcut.
    }
  };

  const load = useCallback(async (nextOffset = 0, newlyAdmittedId = null) => {
    const request = ++generation.current;
    const active = scope;
    setState(previous => previous === 'READY' ? 'REFRESHING' : 'LOADING');
    setError('');
    try {
      // Task source is mandatory for work-list truth. Personnel reads are
      // independent capabilities: a failed contributor source must not
      // suppress a valid task list, fabricate assignees or authorize writes.
      // Primary-source admission precedes optional directory reads; never
      // contend with the work-list transaction merely to populate assignees.
      let taskResponse;
      try {
        taskResponse = await api.get(root + '/tasks?limit=50&offset=' + nextOffset, { headers });
      } catch (cause) {
        const sourceFailure = cause instanceof Error ? cause : new Error('PROJECT_TASK_READ_UNAVAILABLE');
        if (sourceFailure !== cause && cause?.response) sourceFailure.response = cause.response;
        sourceFailure.sourceName = 'Project task list';
        throw sourceFailure;
      }
      if (request !== generation.current || currentScope.current !== active) return false;
      let verified;
      try {
        verified = validList(taskResponse?.data, tenantId, principalId, projectId, nextOffset);
      } catch {
        const invalid = new Error('PROJECT_TASK_SOURCE_INVALID');
        invalid.sourceName = 'Project task list';
        invalid.invalidEnvelope = true;
        throw invalid;
      }
      // Do not make a source-verified task (including Strategy-selected work)
      // wait for three independently authorized, optional directory/command
      // reads. These can each take a full transport timeout on a degraded
      // system; the verified task itself must remain visible and read-only.
      setItems(verified.items);
      setSelectedWorkIds(previous => previous.filter(id => nextOffset === offset && verified.items.some(item => item.task_id === id)));
      setHasMore(verified.has_more);
      setOffset(nextOffset);
      setParticipants([]);
      setParticipantHasMore(false);
      setProjectContributorStatus('VERIFYING');
      setProjectContributorError('');
      setTenantMemberCandidates([]);
      setMemberDirectoryStatus('VERIFYING');
      setActionCapabilities(null);
      setState('READY');
      const settleSupportingAuthorities = async () => {
        const [participantResult, actionResult, optionResult] = await Promise.allSettled([
        api.get(root + '/participants?limit=100&offset=0', { headers }),
        api.get(root + '/task-action-capabilities', { headers }),
        api.get(root + '/participant-options?limit=50&offset=0', { headers }),
      ]);
      if (request !== generation.current || currentScope.current !== active) return false;
      let eligible = null;
      let participantIssue = '';
      if (participantResult.status === 'fulfilled') {
        try {
          eligible = validParticipants(participantResult.value.data, tenantId, principalId, projectId);
        } catch {
          participantIssue = 'Project contributor list returned invalid scope or schema.';
        }
      } else {
        const status = participantResult.reason?.response?.status;
        participantIssue = status === 401 ? 'Project contributor list requires authentication.'
          : status === 403 ? 'Project contributor list was denied by EOS.'
            : status === 404 ? 'Project contributor list endpoint was not found in EOS.'
              : status === 503 ? 'Project contributor list source is unavailable.'
                : 'Project contributor list could not be reached or verified.';
      }
      setProjectContributorStatus(eligible ? 'VERIFIED' : 'UNAVAILABLE');
      setProjectContributorError(participantIssue);
      let members = null;
      if (optionResult.status === 'fulfilled') {
        try {
          members = validOptions(
            optionResult.value.data, { tenantId, principalId, projectId }, 0,
          );
        } catch {
          members = null;
        }
      }
      setTenantMemberCandidates(members?.items || []);
      setMemberDirectoryStatus(members ? 'VERIFIED' : 'UNAVAILABLE');
      const currentContributors = eligible?.items.filter(item => item.role === 'CONTRIBUTOR') || [];
      if (newlyAdmittedId && eligible
        && currentContributors.some(item => item.principal_id === newlyAdmittedId)) {
        setDraft(previous => previous.assignee_principal_id
          ? previous : { ...previous, assignee_principal_id: newlyAdmittedId });
      }
      const action = actionResult.status === 'fulfilled' ? actionResult.value?.data : null;
      const capabilityNames = ['can_start', 'can_complete', 'can_block',
        'can_cancel', 'can_assign', 'can_edit'];
      const admitted = action?.schema === 'WILSY-PROJECT-TASK-ACTION-CAPABILITIES/V1'
        && action.tenant_id === tenantId
        && action.principal_id === principalId
        && action.project_id === projectId
        && capabilityNames.every(key => typeof action[key] === 'boolean');
      setActionCapabilities({
        canStart: admitted && action.can_start,
        canComplete: admitted && action.can_complete,
        canBlock: admitted && action.can_block,
        canCancel: admitted && action.can_cancel,
        canAssign: admitted && action.can_assign,
        canEdit: admitted && action.can_edit,
        canAttachments: true, canActivity: true, canApprovals: true,
      });
      setParticipants(currentContributors);
      setParticipantHasMore(eligible?.has_more || false);
        return !newlyAdmittedId
          || currentContributors.some(item => item.principal_id === newlyAdmittedId);
      };
      // An exact-project task CAS command is confirmed by the mandatory fresh
      // task snapshot, not by optional contributor, directory or permission
      // reads. Only contributor admission waits for separate participant proof.
      if (newlyAdmittedId) return await settleSupportingAuthorities();
      void settleSupportingAuthorities().catch(() => {
        // An unexpected failure in an optional read must not cause an
        // unhandled rejection or expose previously verified capabilities.
        if (request !== generation.current || currentScope.current !== active) return;
        setParticipants([]);
        setParticipantHasMore(false);
        setProjectContributorStatus('UNAVAILABLE');
        setProjectContributorError('Project contributor information could not be verified.');
        setTenantMemberCandidates([]);
        setMemberDirectoryStatus('UNAVAILABLE');
        setActionCapabilities(null);
      });
      return true;
    } catch (cause) {
      if (request !== generation.current || currentScope.current !== active) return false;
      setItems([]);
      setParticipants([]);
      setProjectContributorStatus('UNAVAILABLE');
      setProjectContributorError('Project contributor list was not independently verified.');
      setTenantMemberCandidates([]);
      setMemberDirectoryStatus('UNAVAILABLE');
      setParticipantHasMore(false);
      setActionCapabilities(null);
      setHasMore(false);
      setSelectedWorkIds([]);
      const status = cause?.response?.status;
      const source = cause?.sourceName || 'Project work';
      const rawCode = cause?.response?.data?.detail;
      const safeSourceCode = typeof rawCode === 'string'
        && /^PROJECT_[A-Z0-9_]{1,80}$/.test(rawCode)
        ? ' · EOS ' + rawCode : '';
      setError(cause?.invalidEnvelope ? source + ' returned an invalid tenant, principal, project or pagination contract.'
        : status === 401 ? source + ' requires authentication (HTTP 401).'
          : status === 403 ? source + ' access was denied by EOS (HTTP 403).'
            : status === 404 ? source + ' endpoint is unavailable in this EOS runtime (HTTP 404).'
              : status === 429 ? source + ' admission is rate-limited by EOS (HTTP 429).'
                : status === 503 ? source + ' is unavailable in EOS (HTTP 503)' + safeSourceCode + '.'
                  : Number.isInteger(status) ? source + ' failed with EOS HTTP ' + status + '.'
                    : cause?.code === 'ECONNABORTED' ? source + ' timed out before verification.'
                      : source + ' could not reach or verify EOS. No task list is confirmed.');
      setState(status === 401 || status === 403 ? 'DENIED' : 'UNAVAILABLE');
      return false;
    }
  }, [scope, root, tenantId, principalId, projectId, headers]);

  useEffect(() => {
    generation.current += 1;
    setItems([]);
    setParticipants([]);
    setProjectContributorStatus('VERIFYING');
    setProjectContributorError('');
    setTenantMemberCandidates([]);
    setMemberDirectoryStatus('VERIFYING');
    setPendingMemberChoice('');
    setActionCapabilities(null);
    setOffset(0);
    setHasMore(false);
    setCreating(false);
    setWorkType('TASK');
    setWorkQuery('');
    setWorkMineOnly(false);
    setWorkAttention('ALL');
    setSelectedWorkIds([]);
    setBulkAssignment(null);
    setBulkProgress(null);
    bulkLock.current = false;
    setRecentWork(readRecent());
    setWorkDensity('compact');
    setWorkStatus('ALL');
    setWorkKind('ALL');
    setWorkGroup('HIERARCHY');
    setWorkOrder('DUE_ASC');
    setShowContributorManagement(false);
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
    let active = true;
    // One admitted EOS fanout per mounted scope: StrictMode immediately
    // cleans up its first development effect before this microtask runs.
    queueMicrotask(() => { if (active) void load(0); });
    return () => { active = false; generation.current += 1; };
  }, [scope, load]);

  useEffect(() => {
    // A verified Strategy locator may select existing work only after the
    // exact-project, exact-tenant and principal work page passes validation.
    if (discussionOnly || state !== 'READY' || !TASK_ID.test(focusTaskId || '')) return;
    const token = scope + ':' + focusTaskId;
    if (handledExternalTaskFocus.current === token) return;
    const verified = items.find(item => item.task_id === focusTaskId);
    if (!verified) return; // Never invent a task outside this current page.
    handledExternalTaskFocus.current = token;
    setWorkQuery('');
    setWorkStatus('ALL');
    setWorkKind('ALL');
    setWorkGroup('NONE');
    setWorkViewPage(0);
    setDrawerTaskId(verified.task_id);
  }, [discussionOnly, state, focusTaskId, items, scope]);

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
      setDependencyOriginId(null);
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

  const currentDay = new Date();
  const todayISO = currentDay.getFullYear() + '-' + String(currentDay.getMonth() + 1).padStart(2, '0')
    + '-' + String(currentDay.getDate()).padStart(2, '0');
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
        && (workAttention === 'ALL'
          || (workAttention === 'UNASSIGNED' && !item.assignee_principal_id
            && !['DONE', 'CANCELLED'].includes(item.status))
          || (workAttention === 'RISK' && !['DONE', 'CANCELLED'].includes(item.status)
            && (item.status === 'BLOCKED' || Boolean(item.due_date && item.due_date < todayISO))))
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
  }, [items, workQuery, workMineOnly, workAttention, principalId, workStatus, workKind, workOrder]);
  // Presentation-only paging. Never fabricate EOS totals or silently search
  // records outside the currently authenticated, verified 50-item batch.
  const workViewCount = Math.max(1, Math.ceil(workRows.length / workViewSize));
  const workViewIndex = Math.min(workViewPage, workViewCount - 1);
  const workViewStart = workViewIndex * workViewSize;
  const visibleWorkRows = workRows.slice(workViewStart, workViewStart + workViewSize);
  useEffect(() => { setWorkViewPage(0); }, [
    offset, workQuery, workMineOnly, workAttention, workStatus, workKind, workOrder, workViewSize,
  ]);
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
    if (workGroup === 'HIERARCHY') {
      // Parent references are canonical EOS task ids. A missing parent is
      // outside this verified page, never a fabricated milestone link.
      const byId = new Map(visibleWorkRows.map(item => [item.task_id, item]));
      const children = new Map();
      visibleWorkRows.forEach(item => {
        if (!item.parent_task_id || !byId.has(item.parent_task_id)) return;
        if (!children.has(item.parent_task_id)) children.set(item.parent_task_id, []);
        children.get(item.parent_task_id).push(item);
      });
      const ordered = [];
      const seen = new Set();
      const append = item => {
        if (seen.has(item.task_id)) return;
        seen.add(item.task_id);
        ordered.push(item);
        (children.get(item.task_id) || []).forEach(append);
      };
      visibleWorkRows.forEach(item => {
        if (!item.parent_task_id || !byId.has(item.parent_task_id)) append(item);
      });
      visibleWorkRows.forEach(append);
      return [{ key: 'hierarchy', title: null, rows: ordered }];
    }
    if (workGroup === 'NONE') return [{ key: 'all', title: null, rows: visibleWorkRows }];
    const grouped = new Map();
    visibleWorkRows.forEach(item => {
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
  }, [visibleWorkRows, workGroup, participants]);

  const workPager = <nav aria-label="Verified project work view pages"
    className="mt-3 flex flex-wrap items-center justify-between gap-3 rounded-xl border border-slate-200 bg-slate-50 px-3 py-3">
    <div className="flex flex-wrap items-center gap-2">
      <label className="flex items-center gap-2 text-xs font-semibold text-slate-800">
        Rows per view
        <select aria-label="Project work rows per view" value={workViewSize}
          onChange={event => setWorkViewSize(Number(event.target.value))}
          className="min-h-10 rounded-lg border border-slate-300 bg-white px-2 text-sm text-slate-900">
          <option value={10}>10</option>
          <option value={20}>20</option>
          <option value={50}>50</option>
        </select>
      </label>
      <span role="status" className="text-xs text-slate-700">
        {workRows.length === 0 ? 'No matching work in this EOS batch'
          : (workViewStart + 1) + '–' + (workViewStart + visibleWorkRows.length)
            + ' of ' + workRows.length + ' matching in verified batch'}
        {' · '}View {workViewIndex + 1} of {workViewCount}
      </span>
    </div>
    <div className="flex items-center gap-2">
      <button type="button" className="wp-button min-h-10"
        disabled={busy || state !== 'READY' || workViewIndex === 0}
        onClick={() => setWorkViewPage(page => Math.max(0, page - 1))}>
        Previous view
      </button>
      <button type="button" className="wp-button min-h-10"
        disabled={busy || state !== 'READY' || workViewIndex >= workViewCount - 1}
        onClick={() => setWorkViewPage(page => Math.min(workViewCount - 1, page + 1))}>
        Next view
      </button>
    </div>
  </nav>;

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
  const knownCompletionBlockers = completingItem
    ? items.filter(item => completingItem.depends_on.includes(item.task_id)
      && item.status !== 'DONE') : [];
  const offPageCompletionDependencies = completingItem
    ? completingItem.depends_on.filter(id => !items.some(item => item.task_id === id)).length : 0;
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

  const selectedReviewTasks = useMemo(() => {
    const selected = selectedWorkIds.map(id => items.find(item => item.task_id === id))
      .filter(Boolean);
    const byId = new Map(selected.map(item => [item.task_id, item]));
    const degree = new Map(selected.map(item => [item.task_id, 0]));
    const outgoing = new Map(selected.map(item => [item.task_id, []]));
    selected.forEach(item => item.depends_on.forEach(predecessorId => {
      if (!byId.has(predecessorId)) return;
      degree.set(item.task_id, degree.get(item.task_id) + 1);
      outgoing.get(predecessorId).push(item.task_id);
    }));
    const ready = selected.filter(item => degree.get(item.task_id) === 0);
    const order = [];
    for (let index = 0; index < ready.length; index += 1) {
      const item = ready[index];
      order.push(item);
      outgoing.get(item.task_id).forEach(nextId => {
        degree.set(nextId, degree.get(nextId) - 1);
        if (degree.get(nextId) === 0) ready.push(byId.get(nextId));
      });
    }
    // Source domain prevents cycles on immutable creation. If a malformed
    // projection reaches this UI, selection retains its explicit order;
    // EOS remains the only status-transition and dependency authority.
    return order.length === selected.length ? order : selected;
  }, [selectedWorkIds, items]);
  const visibleRecentWork = recentWork.scope === scope
    ? recentWork.ids.map(id => items.find(item => item.task_id === id)).filter(Boolean) : [];
  const frequentWork = visibleRecentWork.filter(item => recentWork.counts[item.task_id] >= 2)
    .sort((a, b) => recentWork.counts[b.task_id] - recentWork.counts[a.task_id]).slice(0, 2);
  const atRiskWork = items.filter(item => !['DONE', 'CANCELLED'].includes(item.status)
    && (item.status === 'BLOCKED' || Boolean(item.due_date && item.due_date < todayISO)));
  const withoutOwnerWork = items.filter(item => !['DONE', 'CANCELLED'].includes(item.status)
    && !item.assignee_principal_id);
  const selectedReviewIndex = selectedReviewTasks.findIndex(item => item.task_id === drawerTaskId);
  const activeSelectedWork = selectedReviewTasks.filter(item =>
    !['DONE', 'CANCELLED'].includes(item.status));
  const confirmBulkAssignment = async () => {
    if (!bulkAssignment || bulkLock.current || busy || state !== 'READY'
      || !actionCapabilities?.canAssign || !bulkAssignment.confirmed
      || !participants.some(person => person.principal_id === bulkAssignment.assignee_principal_id)
      || bulkAssignment.taskIds.length < 2
      || bulkAssignment.taskIds.length > 50) return;
    const targets = bulkAssignment.taskIds.map(id => items.find(item => item.task_id === id));
    if (targets.some(item => !item || ['DONE', 'CANCELLED'].includes(item.status))) {
      setBulkProgress({ done: 0, total: targets.length,
        error: 'Selection changed. Refresh and select currently eligible work again.' });
      return;
    }
    const active = scope;
    const assignee = bulkAssignment.assignee_principal_id;
    bulkLock.current = true;
    setBusy(true);
    setBulkProgress({ done: 0, total: targets.length, error: null });
    let confirmed = 0;
    let issue = null;
    try {
      for (const task of targets) {
        if (currentScope.current !== active) return;
        if (task.assignee_principal_id === assignee) {
          confirmed += 1;
          setBulkProgress({ done: confirmed, total: targets.length, error: null });
          continue;
        }
        const key = globalThis.crypto?.randomUUID?.();
        if (!key) throw new Error('EOS_COMMAND_IDEMPOTENCY_UNAVAILABLE');
        const body = {
          expected_revision: task.revision,
          title: task.title,
          description: task.description,
          due_date: task.due_date || null,
          assignee_principal_id: assignee,
        };
        const response = await api.patch(
          root + '/tasks/' + encodeURIComponent(task.task_id), body,
          { headers: { ...headers, 'Idempotency-Key': key } },
        );
        if (currentScope.current !== active) return;
        const result = response?.data;
        if (result?.schema !== RESULT_SCHEMA
          || result.tenant_id !== tenantId || result.principal_id !== principalId
          || result.project_id !== projectId
          || !validTask(result.task, tenantId, projectId)
          || result.task.task_id !== task.task_id) {
          throw new Error('EOS_TASK_ASSIGNMENT_RECEIPT_INVALID');
        }
        const list = await api.get(root + '/tasks?limit=50&offset=0', { headers });
        if (currentScope.current !== active) return;
        const checked = validList(list?.data, tenantId, principalId, projectId, 0);
        const actual = checked.items.find(item => item.task_id === task.task_id);
        if (!actual || actual.revision <= task.revision
          || actual.assignee_principal_id !== assignee) {
          throw new Error('EOS_TASK_ASSIGNMENT_READBACK_UNVERIFIED');
        }
        confirmed += 1;
        setBulkProgress({ done: confirmed, total: targets.length, error: null });
      }
    } catch {
      issue = 'Assignment stopped after ' + confirmed + ' verified task(s). '
        + 'A later command or its readback could not be verified. '
        + 'Refresh and reconcile the project before any new attempt.';
      setBulkProgress({ done: confirmed, total: targets.length, error: issue });
    } finally {
      if (currentScope.current === active) {
        const refreshed = await load(0);
        if (!refreshed && !issue) {
          setBulkProgress({ done: confirmed, total: targets.length,
            error: 'Per-task receipts were verified, but the final work list is unavailable. Refresh to reconcile.' });
        }
        setBusy(false);
        bulkLock.current = false;
      }
    }
  };
  const drawerTask = items.find(item => item.task_id === drawerTaskId);
  const closeDrawer = () => {
    setTaskIntelligenceOpen(false);
    setDrawerTaskId(null);
    drawerReturnFocus.current?.focus?.();
  };
  const openTaskIntelligenceConversation = () => {
    if (!drawerTask || state !== 'READY'
      || !TASK_ID.test(drawerTask.task_id)
      || !Number.isSafeInteger(drawerTask.revision)
      || drawerTask.revision < 1 || !principalId || !tenantId) return;
    const locator = {
      workspace: 'PROJECTS', project_id: projectId,
      task_id: drawerTask.task_id, task_revision: drawerTask.revision,
      participant_view: Boolean(selfIsContributor),
    };
    closeDrawer();
    // Only task coordinates leave the modal. These browser events confer no
    // membership, context truth, entitlement or model execution authority.
    window.dispatchEvent(new CustomEvent('wilsy:ai-context-locator', {
      detail: { tenantId, principalId, locator },
    }));
    window.dispatchEvent(new CustomEvent('wilsy:ai-request-open', {
      detail: { tenantId, principalId },
    }));
  };
  useEffect(() => {
    if (!drawerTaskId) return undefined;
    const keyDown = event => {
      if (event.key === 'Escape') {
        event.preventDefault();
        setTaskIntelligenceOpen(false);
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
  useEffect(() => {
    if (discussionOnly || !focusedAction || !selectedActionTask) return undefined;
    const panel = focusedPanelRef.current;
    const previousFocus = document.activeElement;
    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
    panel?.querySelector('button')?.focus();
    const onKeyDown = event => {
      if (event.key === 'Escape') {
        event.preventDefault();
        closeFocusedAction();
      } else if (event.key === 'Tab' && panel) {
        const focusable = [...panel.querySelectorAll('button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), a[href]')]
          .filter(element => element.getClientRects().length > 0);
        if (!focusable.length) return;
        const first = focusable[0];
        const last = focusable[focusable.length - 1];
        if (event.shiftKey && document.activeElement === first) {
          event.preventDefault();
          last.focus();
        } else if (!event.shiftKey && document.activeElement === last) {
          event.preventDefault();
          first.focus();
        }
      }
    };
    document.addEventListener('keydown', onKeyDown);
    return () => {
      document.removeEventListener('keydown', onKeyDown);
      document.body.style.overflow = previousOverflow;
      if (previousFocus?.isConnected) previousFocus.focus?.();
    };
  }, [discussionOnly, focusedAction?.id, focusedAction?.type]);

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
          onClose={closeFocusedAction} showClose={false}
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
          taskId={focusedAction.id} participantMode={selfIsContributor} ownerReadMode tenantHeaders={tenantHeaders}
          onManageContributors={onOpenProjectPeople}
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
      {!(focusedAction && selectedActionTask) && <div className="flex flex-wrap gap-2">
        <button type="button" className="wp-button" disabled={busy} onClick={() => void load(offset)}>
          <RefreshCw size={14}/> Refresh work
        </button>
        {state === 'READY' && actionCapabilities?.canEdit && <button type="button" className="wp-button wp-button-primary"
          disabled={busy} onClick={() => {
            setDependencyOriginId(null);
            setCreating(value => !value);
          }}>
          <Plus size={14}/> {creating ? 'Close editor' : 'Create task'}
        </button>}
      </div>}
    </div>
    {(state === 'LOADING' || state === 'REFRESHING') &&
      <p role="status" className="mt-3 flex items-center gap-2 text-sm text-slate-600">
        <LoaderCircle size={15} className="animate-spin"/> Verifying project tasks…
      </p>}
    {(state === 'DENIED' || state === 'UNAVAILABLE') &&
      <p role="alert" className="mt-3 text-sm text-rose-700">{error}</p>}
    {(state === 'READY' || state === 'REFRESHING')
      && projectContributorStatus === 'UNAVAILABLE' &&
      <p role="alert" className="mt-3 rounded-lg border border-amber-300 bg-amber-50 p-3 text-sm text-amber-950">
        {projectContributorError || 'Project contributor authority is not verified.'}
        {' '}Existing verified task rows remain visible, but contributor assignment and member admission are unavailable until this EOS source is verified.
      </p>}
    {(state === 'READY' || state === 'REFRESHING') && <>
      {focusedAction && selectedActionTask && <>
        <div aria-hidden="true" className="fixed inset-0 z-[88] bg-slate-950/45"
          onClick={closeFocusedAction}/>
        <div ref={focusedPanelRef} role="dialog" aria-modal="true"
          aria-label={'Task workspace: ' + selectedActionTask.title}
          className="fixed left-1/2 top-1/2 z-[89] flex h-[min(760px,calc(100dvh-3rem))] min-h-[280px] w-[min(980px,calc(100vw-2rem))] max-w-[calc(100vw-2rem)] -translate-x-1/2 -translate-y-1/2 resize flex-col overflow-auto overscroll-contain rounded-xl border border-slate-200 bg-white p-4 shadow-2xl sm:p-5">
      <div className="mb-2 flex flex-wrap items-center gap-3 border-b border-slate-200 pb-3">
        <button type="button" className="wp-button !min-h-9 !px-3 !text-xs"
          onClick={closeFocusedAction}>← Work</button>
        <div className="min-w-0 flex-1">
          <h4 className="truncate text-sm font-bold text-slate-950"
            title={selectedActionTask.title}>{selectedActionTask.title}</h4>
          <p className="text-xs text-slate-600">{label(selectedActionTask.status)} · {focusedAction.type === 'attachments' ? 'Files & evidence' : focusedAction.type === 'approvals' ? 'Approvals' : 'Discussion'}</p>
        </div>
      </div>
      <nav aria-label="Selected task workspace" className="mb-3 flex flex-wrap gap-1 border-b border-slate-200 pb-2">
        {[['discussion', 'Activity'], ['attachments', 'Files'], ['approvals', 'Approvals'], ['details', 'Details']]
          .map(([type, title]) => <button key={type} type="button"
            aria-current={focusedAction.type === type ? 'page' : undefined}
            className={'min-h-9 rounded-md px-3 text-xs font-semibold focus-visible:outline focus-visible:outline-2 focus-visible:outline-blue-700 '
              + (focusedAction.type === type ? 'bg-slate-900 text-white'
                : 'text-slate-700 hover:bg-slate-100')}
            onClick={() => {
              if (type === 'details') {
                const task = selectedActionTask;
                closeFocusedAction();
                setDrawerTaskId(task.task_id);
                return;
              }
              setDiscussionTaskId(type === 'discussion' ? focusedAction.id : null);
              setAttachmentTaskId(type === 'attachments' ? focusedAction.id : null);
              setApprovalTaskId(type === 'approvals' ? focusedAction.id : null);
            }}>{title}</button>)}
      </nav>
      {focusedAction.type === 'discussion' && <ProjectTaskCommentsPanel key={[scope, focusedAction.id].join(':')}
        tenantId={tenantId} projectId={projectId} principalId={principalId}
        taskId={focusedAction.id} participants={participants} tenantHeaders={tenantHeaders}
        onClose={closeFocusedAction} showClose={false}
        onViewApprovals={() => { setDiscussionTaskId(null); setApprovalTaskId(focusedAction.id); }}
        onViewAttachments={() => { setDiscussionTaskId(null); setAttachmentTaskId(focusedAction.id); }}/>}
      {focusedAction.type === 'approvals' && <ProjectTaskApprovalsPanel key={[scope, focusedAction.id].join(':')}
        tenantId={tenantId} projectId={projectId} principalId={principalId}
        taskId={focusedAction.id} participants={participants} tenantHeaders={tenantHeaders}
        participantAuthorityState={projectContributorStatus} participantHasMore={participantHasMore}
        showClose={false} onManageContributors={() => {
          closeFocusedAction();
          onOpenProjectPeople?.();
        }} onClose={closeFocusedAction}/>}
      {focusedAction.type === 'attachments' && <ProjectTaskAttachmentsPanel key={[scope, focusedAction.id].join(':')}
        tenantId={tenantId} projectId={projectId} principalId={principalId}
        taskId={focusedAction.id} participantMode={selfIsContributor} ownerReadMode tenantHeaders={tenantHeaders}
          onManageContributors={onOpenProjectPeople}
        showClose={false} onClose={closeFocusedAction}/>}
        </div>
      </>}
      <div aria-hidden={Boolean(focusedAction && selectedActionTask)}>
      {!actionCapabilities?.canEdit && <p role="status" className="mt-2 text-xs font-semibold text-amber-900">
        Project work is read-only. EOS has not confirmed current task-update authority.
      </p>}
      <p className="mt-2 text-xs text-slate-600" aria-label="Verified current task page status">
        {items.length} verified work items · {counts.find(item => item.status === 'IN_PROGRESS')?.count || 0} in progress
        {overdueOnPage > 0 ? ' · ' + overdueOnPage + ' overdue' : ''}
      </p>
      {state === 'READY' && <div aria-label="Work continuity and execution signals"
        className="mt-2 flex flex-wrap items-center gap-x-3 gap-y-2 border-b border-slate-200 pb-3 text-xs">
        <span className="font-semibold text-slate-700">This EOS batch</span>
        <button type="button" aria-pressed={workAttention === 'UNASSIGNED'}
          className={'min-h-9 rounded-md border px-3 font-semibold '
            + (workAttention === 'UNASSIGNED'
              ? 'border-slate-800 bg-slate-900 text-white'
              : 'border-slate-300 bg-white text-slate-800 hover:bg-slate-100')}
          onClick={() => setWorkAttention(value => value === 'UNASSIGNED' ? 'ALL' : 'UNASSIGNED')}>
          {withoutOwnerWork.length} unassigned
        </button>
        <button type="button" aria-pressed={workAttention === 'RISK'}
          className={'min-h-9 rounded-md border px-3 font-semibold '
            + (workAttention === 'RISK'
              ? 'border-slate-800 bg-slate-900 text-white'
              : 'border-slate-300 bg-white text-slate-800 hover:bg-slate-100')}
          onClick={() => setWorkAttention(value => value === 'RISK' ? 'ALL' : 'RISK')}>
          {atRiskWork.length} blocked or overdue
        </button>
        {visibleRecentWork.length > 0 && <button type="button"
          className="min-h-9 rounded-md border border-slate-300 bg-white px-3 font-semibold text-slate-800 hover:bg-slate-100"
          onClick={event => {
            drawerReturnFocus.current = event.currentTarget;
            recordWorkVisit(visibleRecentWork[0]);
            setDrawerTaskId(visibleRecentWork[0].task_id);
          }}>Resume: {visibleRecentWork[0].title}</button>}
        {frequentWork.length > 0 && <span className="text-slate-600">
          Often opened this session: {frequentWork.map(item => item.title).join(' · ')}
        </span>}
      </div>}
      <details className="mt-4 rounded-lg border border-slate-200 bg-white" aria-label="Project work queue controls">
        <summary className="cursor-pointer px-4 py-3 text-sm font-semibold text-slate-900 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-700">
          Work filters, grouping and sorting · {workRows.length} match on this verified EOS batch
        </summary>
        <div className="flex flex-wrap items-end gap-3 border-t border-slate-200 p-3">
        <label className="flex min-w-[145px] flex-col gap-1 text-xs font-semibold text-slate-800">
          Group work
          <select aria-label="Group project work" value={workGroup}
            onChange={event => setWorkGroup(event.target.value)}
            className="rounded-md border border-slate-300 bg-white px-2 py-2 text-sm text-slate-900">
            <option value="HIERARCHY">Task hierarchy</option>
            <option value="NONE">Flat list</option>
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
        <span role="status" className="w-full text-xs text-slate-600">{workRows.length} matching / {items.length} verified in EOS batch {Math.floor(offset / 50) + 1}. Search and sorting apply only to this batch.</span>
        </div>
      </details>
      {creating && <form ref={createFormRef} onSubmit={create} className="mt-4 space-y-3 rounded-xl border border-blue-200 bg-blue-50/50 p-3">
        <h4 className="text-sm font-bold text-slate-900">Create EOS work item</h4>
        {dependencyOriginId && <p role="status" className="rounded-md border border-blue-200 bg-white p-3 text-sm text-slate-900">
          New dependent task: <strong>{items.find(item => item.task_id === dependencyOriginId)?.title || 'Verified predecessor'}</strong> must reach Done before the new task can be completed. This creates a new EOS task; it does not modify existing predecessors.
        </p>}
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
            <select aria-label="Task assignee" disabled={projectContributorStatus !== 'VERIFIED'} value={draft.assignee_principal_id}
              onChange={event => {
                const selected = event.target.value;
                if (selected.startsWith('member:')) {
                  const candidateId = selected.slice(7);
                  if (!tenantMemberCandidates.some(member => member.principal_id === candidateId)) return;
                  setPendingMemberChoice(candidateId);
                  setShowContributorManagement(true);
                  return;
                }
                setDraft(value => ({ ...value, assignee_principal_id: selected }));
              }}
              className="mt-1 w-full rounded-lg border border-slate-300 bg-white p-2.5 text-sm font-normal text-slate-900">
              <option value="">Unassigned</option>
              {participants.map(person => <option key={person.principal_id} value={person.principal_id}>
                {contributorName(person.principal_id)}
              </option>)}
              {tenantMemberCandidates.some(member => !participants.some(
                person => person.principal_id === member.principal_id,
              )) && <optgroup label="Eligible tenant members — authorize contributor first">
                {tenantMemberCandidates.filter(member => !participants.some(
                  person => person.principal_id === member.principal_id,
                )).map(member => <option key={member.principal_id} value={'member:' + member.principal_id}>
                  {optionName(member) || 'Verified member — name unavailable'} · Authorize contributor
                </option>)}
              </optgroup>}
            </select>
            {memberDirectoryStatus === 'UNAVAILABLE' && <span role="status" className="mt-2 block text-xs font-normal text-amber-900">
              The tenant member directory is not currently verified. Existing active project contributors remain selectable; refresh when EOS restores the directory.
            </span>}
            {participants.length === 0 && !participantHasMore && <span role="status" className="mt-2 block text-xs font-normal text-slate-700">
              No verified current project contributors are eligible for task assignment yet. Create this task unassigned, or select an eligible tenant member using the nearby contributor-management action.
            </span>}
            {participantHasMore && <span role="status" className="mt-2 block text-xs font-normal text-slate-700">
              More than 100 participants exist. Assignment remains restricted to the verified current participant page.
            </span>}
            <button type="button" disabled={projectContributorStatus !== 'VERIFIED'} className="wp-button mt-2 !min-h-9 !text-xs"
              aria-expanded={showContributorManagement}
              onClick={() => { setPendingMemberChoice(''); setShowContributorManagement(value => !value); }}>
              {showContributorManagement ? 'Close contributor management' : 'Manage eligible contributors'}
            </button>
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
      {showContributorManagement && <div
        className="fixed inset-0 z-[95] flex items-center justify-center bg-slate-950/55 p-3 sm:p-6"
        onMouseDown={event => {
          if (event.target === event.currentTarget) setShowContributorManagement(false);
        }}>
        <div role="dialog" aria-modal="true" aria-label="Manage contributors for task assignment"
          onKeyDown={event => {
            if (event.key === 'Escape') {
              event.stopPropagation();
              setShowContributorManagement(false);
            }
          }}
          className="flex max-h-[90dvh] w-full max-w-3xl flex-col overflow-hidden rounded-xl border border-slate-300 bg-white shadow-2xl">
          <div className="flex shrink-0 items-start justify-between gap-3 border-b border-slate-200 px-4 py-3">
            <div>
              <h4 className="text-base font-bold text-slate-950">Select an eligible tenant member</h4>
              <p className="mt-1 text-xs text-slate-700">Project participation must be verified before a person can be assigned a task. Your unsaved task remains intact.</p>
            </div>
            <button type="button" autoFocus className="wp-button shrink-0"
              onClick={() => setShowContributorManagement(false)}>Close</button>
          </div>
          <div className="min-h-0 flex-1 overflow-y-auto px-4 pb-4">
            <ProjectParticipantsPanel projectId={projectId} tenantId={tenantId}
              principalId={principalId} tenantHeaders={tenantHeaders}
              initialSelectedPrincipal={pendingMemberChoice}
              onParticipantsChanged={admittedId => {
                void load(offset, admittedId).then(verified => {
                  if (verified) {
                    setShowContributorManagement(false);
                    setPendingMemberChoice('');
                  }
                });
              }}/>
          </div>
        </div>
      </div>}
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
        <div className="rounded-lg border border-slate-200 bg-slate-50 px-3 py-2.5">
          <p className="text-sm font-bold text-slate-950">Delivery accountability</p>
          <p className="mt-1 text-xs text-slate-700">Choose a responsible contributor{assignmentOnly ? '.' : ' and the completion date.'} Changes are saved only after verification.</p>
        </div>
        <div className={assignmentOnly ? 'grid gap-3' : 'grid gap-3 sm:grid-cols-2'}>
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
          {!assignmentOnly && <ProjectWorkDateField label="Edit task due date" value={editor.due_date}
            onChange={date => setEditor(previous => ({ ...previous, due_date: date }))}/>}
        </div>
        {!assignmentOnly && <details className="rounded-lg border border-slate-200 px-3 py-2.5">
          <summary className="cursor-pointer text-sm font-semibold text-slate-900">Additional task details · title and description</summary>
          <div className="mt-3 space-y-3">
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
          </div>
        </details>}
        {!assignmentOnly && <p className="text-xs text-slate-600">The project verifies eligible contributors. Parent and predecessor relationships remain unchanged.</p>}
        <button type="submit" className="wp-button wp-button-primary"
          disabled={busy || !(assignmentOnly ? actionCapabilities?.canAssign : actionCapabilities?.canEdit)
            || !editor.title.trim() || Boolean(
            editor.assignee_principal_id && !participants.some(person =>
              person.principal_id === editor.assignee_principal_id))
            || (assignmentOnly && (editor.assignee_principal_id || null)
              === (items.find(item => item.task_id === editor.task_id)?.assignee_principal_id || null))}>
          {assignmentOnly ? 'Save assignment' : 'Save task changes'}
        </button>
        </form>
        </div>
      </div>}
      <div className="mt-3 overflow-x-auto rounded-xl border border-slate-200" role="region" aria-label="Verified project tasks" tabIndex={0}>
        <table role="grid" aria-label="Project work grid" data-density={workDensity}
          className="w-full min-w-[580px] border-collapse text-left text-sm">
          <thead className="bg-slate-100 text-xs font-bold text-slate-700">
            {selectedReviewTasks.length > 1 && <tr className="bg-slate-50">
              <th colSpan={6} scope="colgroup" className="px-3 py-2">
                <div aria-label="Selected work actions" className="flex flex-wrap items-center gap-2">
                  <span role="status" className="mr-auto text-xs font-semibold text-slate-900">
                    {selectedReviewTasks.length} selected · verified current EOS batch
                  </span>
                  <button type="button" className="wp-button !min-h-9 !px-3 !text-xs"
                    onClick={event => {
                      drawerReturnFocus.current = event.currentTarget;
                      setDrawerTaskId(selectedReviewTasks[0].task_id);
                    }}>Review in sequence</button>
                  {activeSelectedWork.length >= 2 && <button type="button"
                    className="wp-button !min-h-9 !px-3 !text-xs"
                    disabled={busy || !actionCapabilities?.canAssign || participants.length === 0}
                    onClick={() => {
                      setBulkProgress(null);
                      setBulkAssignment({ taskIds: activeSelectedWork.map(item => item.task_id),
                        assignee_principal_id: '', confirmed: false });
                    }}>Assign selected…</button>}
                  <button type="button" className="wp-button !min-h-9 !px-3 !text-xs"
                    onClick={() => {
                      const firstUnassigned = selectedReviewTasks.find(item => !item.assignee_principal_id
                        && !['DONE', 'CANCELLED'].includes(item.status));
                      if (firstUnassigned && actionCapabilities?.canAssign) {
                        openTaskEditor(firstUnassigned, true);
                      }
                    }}
                    disabled={!actionCapabilities?.canAssign || !selectedReviewTasks.some(item =>
                      !item.assignee_principal_id && !['DONE', 'CANCELLED'].includes(item.status))}>
                    Assign next unassigned
                  </button>
                  <button type="button" className="wp-button !min-h-9 !px-3 !text-xs"
                    onClick={() => setSelectedWorkIds([])}>Clear selection</button>
                </div>
              </th>
            </tr>}
            <tr><th scope="col" className="w-10 p-2">
              <input type="checkbox" aria-label="Select all visible work"
                checked={visibleWorkRows.length > 0 && visibleWorkRows.every(item => selectedWorkIds.includes(item.task_id))}
                disabled={visibleWorkRows.length === 0}
                onChange={event => setSelectedWorkIds(previous => event.target.checked
                  ? [...new Set([...previous, ...visibleWorkRows.map(item => item.task_id)])]
                  : previous.filter(id => !visibleWorkRows.some(item => item.task_id === id)))}/>
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
              selectedCount={selectedReviewTasks.length}
              depth={workGroup === 'HIERARCHY' && item.parent_task_id
                && visibleWorkRows.some(parent => parent.task_id === item.parent_task_id) ? 1 : 0}
              density={workDensity} busy={busy}
              pendingStatus={pendingTransition?.taskId === item.task_id ? pendingTransition.status : null}
              todayISO={todayISO} assigneeName={contributorName}
              onToggleSelect={(id, checked) => setSelectedWorkIds(previous => checked
                ? [...previous, id] : previous.filter(value => value !== id))}
              onOpen={(selected, element) => {
                drawerReturnFocus.current = element;
                recordWorkVisit(selected);
                setDrawerTaskId(selected.task_id);
              }}
              onCreateSubtask={selected => {
                if (busy || state !== 'READY' || actionCapabilities?.canEdit !== true
                  || selected.kind !== 'TASK' || selected.parent_task_id
                  || ['DONE', 'CANCELLED'].includes(selected.status)) return;
                setCreating(true);
                setEditor(null);
                setDependencyOriginId(null);
                setWorkType('SUBTASK');
                setDraft({ ...EMPTY, kind: 'TASK', parent_task_id: selected.task_id });
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
            {visibleWorkRows.length === 0 && <tr><td colSpan={6} className="p-6 text-center text-sm text-slate-600">
              {items.length === 0 ? 'EOS verified no tasks on this page. Create work to begin execution.'
                : 'No work items on this verified page match the selected search and filters.'}
            </td></tr>}
          </tbody>
        </table>
      </div>
      {workPager}
      <details className="mt-3 border-t border-slate-200 pt-2" aria-label="Additional project work views">
        <summary className="cursor-pointer py-2 text-xs font-semibold text-slate-700">
          Additional views · lifecycle and checklist
        </summary>
        <div className="mt-2 space-y-1">
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
        </div>
      </details>

        {bulkAssignment && <div className="fixed inset-0 z-[115] flex items-center justify-center bg-slate-950/55 p-3"
          onMouseDown={event => {
            if (event.target === event.currentTarget && !busy) setBulkAssignment(null);
          }}>
          <section role="dialog" aria-modal="true" aria-label="Assign selected project tasks"
            className="w-full max-w-lg rounded-xl border border-slate-200 bg-white p-5 shadow-2xl">
            <div className="flex items-start justify-between gap-3">
              <div>
                <h4 className="text-base font-bold text-slate-950">Assign selected tasks</h4>
                <p className="mt-1 text-sm text-slate-700">
                  {bulkAssignment.taskIds.length} active tasks from this verified EOS batch
                </p>
              </div>
              <button type="button" className="wp-button !min-h-9 !text-xs"
                disabled={busy} onClick={() => setBulkAssignment(null)}>Close</button>
            </div>
            <p className="mt-3 text-xs leading-relaxed text-slate-700">
              Each task is updated individually with its current revision, independently
              authorized by EOS, and checked against a fresh persisted task list.
              Processing stops at the first unverified outcome.
            </p>
            <label className="mt-4 block text-sm font-semibold text-slate-900">
              Assign to eligible contributor
              <select aria-label="Assign selected tasks to contributor"
                className="mt-2 w-full rounded-lg border border-slate-300 bg-white p-2.5 text-sm"
                disabled={busy || Boolean(bulkProgress?.error)}
                value={bulkAssignment.assignee_principal_id}
                onChange={event => setBulkAssignment(previous => ({
                  ...previous, assignee_principal_id: event.target.value, confirmed: false,
                }))}>
                <option value="">Choose contributor</option>
                {participants.map(person => <option key={person.principal_id}
                  value={person.principal_id}>{contributorName(person.principal_id)}</option>)}
              </select>
            </label>
            <label className="mt-4 flex items-start gap-2 text-sm text-slate-800">
              <input type="checkbox" className="mt-1" checked={bulkAssignment.confirmed}
                disabled={busy || Boolean(bulkProgress)}
                onChange={event => setBulkAssignment(previous => ({
                  ...previous, confirmed: event.target.checked,
                }))}/>
              I confirm assignment to each selected task; this is not one atomic bulk transaction.
            </label>
            {bulkProgress && <p role="status" className={'mt-3 text-sm '
              + (bulkProgress.error ? 'text-rose-800' : 'text-slate-800')}>
              {bulkProgress.done} of {bulkProgress.total} independently verified.
              {bulkProgress.error ? ' ' + bulkProgress.error : ''}
            </p>}
            <div className="mt-4 flex flex-wrap justify-end gap-2">
              <button type="button" className="wp-button !min-h-10"
                disabled={busy} onClick={() => setBulkAssignment(null)}>Back to work</button>
              <button type="button" className="wp-button wp-button-primary !min-h-10"
                disabled={busy || Boolean(bulkProgress) || !bulkAssignment.confirmed
                  || !bulkAssignment.assignee_principal_id}
                onClick={() => void confirmBulkAssignment()}>Apply individual assignments</button>
            </div>
          </section>
        </div>}
        {completingItem && <div role="dialog" aria-modal="true" aria-label="Confirm verified task completion"
          className="fixed inset-x-4 top-1/4 z-[110] mx-auto max-w-xl rounded-xl border border-blue-300 bg-white p-5 shadow-2xl">
          <h5 className="text-sm font-bold text-slate-900">Confirm completion · {completingItem.title}</h5>
          <p className="mt-2 text-xs text-slate-700">This is a terminal EOS lifecycle command. Verify acceptance and supporting evidence first; a checkbox alone does not certify evidence, an approval or a milestone.</p>
          {knownCompletionBlockers.length > 0 && <div role="alert"
            className="mt-3 rounded-md border border-amber-300 bg-amber-50 p-3 text-sm text-amber-950">
            Completion is blocked by {knownCompletionBlockers.length} unfinished predecessor
            {knownCompletionBlockers.length === 1 ? '' : 's'}:
            <ul className="mt-1 list-inside list-disc">
              {knownCompletionBlockers.map(item => <li key={item.task_id}>
                {item.title} · {label(item.status)}
              </li>)}
            </ul>
            Refresh work after these predecessors reach Done.
          </div>}
          {offPageCompletionDependencies > 0 && <p className="mt-3 text-xs text-slate-700">
            {offPageCompletionDependencies} predecessor record(s) are outside this verified page.
            EOS independently checks their live status before completion.
          </p>}
          <label className="mt-3 flex items-start gap-2 text-sm text-slate-900">
            <input type="checkbox" className="mt-1 size-4" checked={completionAttested}
              onChange={event => setCompletionAttested(event.target.checked)}/>
            <span>I reviewed this task's acceptance and supporting evidence.</span>
          </label>
          <div className="mt-3 flex flex-wrap gap-2">
            <button type="button" className="wp-button wp-button-primary" disabled={busy || !actionCapabilities?.canComplete || !completionAttested
                || knownCompletionBlockers.length > 0}
              onClick={() => transition(completingItem, 'DONE')}>Confirm Done in EOS</button>
            <button type="button" className="wp-button" disabled={busy} onClick={() => {
              setCompletionCandidate(null);
              setCompletionAttested(false);
            }}>Cancel</button>
            <button type="button" className="wp-button" disabled={busy}
              onClick={() => setAttachmentTaskId(completingItem.task_id)}>Review attachments</button>
          </div>
        </div>}
      {drawerTask && <div className="fixed inset-0 z-[85] flex items-center justify-center bg-slate-950/55 p-3 sm:p-6"
        onClick={event => { if (event.target === event.currentTarget) closeDrawer(); }}>
        <aside role="dialog" aria-modal="true"
          aria-label={'Work details: ' + drawerTask.title} ref={drawerRef}
          className="relative flex max-h-[calc(100dvh-1.5rem)] w-full max-w-4xl flex-col overflow-hidden rounded-xl border border-slate-200 bg-white shadow-2xl sm:max-h-[calc(100dvh-3rem)]">
          <UnifiedTaskHeader
            kind={drawerTask.kind === 'MILESTONE' ? 'Milestone' : drawerTask.parent_task_id ? 'Subtask' : 'Task'}
            source="Project" title={drawerTask.title} status={label(drawerTask.status)}
            due={drawerTask.due_date ? (drawerTask.due_date < todayISO && !['DONE', 'CANCELLED'].includes(drawerTask.status)
              ? 'Overdue · ' : 'Due ') + drawerTask.due_date : 'No due date'}
            owner={drawerTask.assignee_principal_id ? contributorName(drawerTask.assignee_principal_id) : 'Not assigned'}
            onClose={typeof onReturnToAttention === 'function' && focusTaskId === drawerTask.task_id
              ? onReturnToAttention : closeDrawer}
            closeLabel={typeof onReturnToAttention === 'function' && focusTaskId === drawerTask.task_id
              ? 'Back to Daily attention' : 'Close work details'}
            primaryControl={<button type="button" onClick={() => setTaskIntelligenceOpen(value => !value)}
          aria-pressed={taskIntelligenceOpen}
          className="inline-flex min-h-11 items-center rounded-lg border border-slate-300 bg-white px-3 text-sm font-semibold text-blue-800 hover:bg-blue-50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-blue-700">
          {taskIntelligenceOpen ? 'Task details' : 'WILSY AI'}
        </button>}
            reviewNavigation={selectedReviewTasks.length > 1 && selectedReviewIndex !== -1 && <nav
              aria-label="Selected work review navigation" className="mt-3 flex flex-wrap items-center gap-2">
              <span className="mr-auto text-xs font-semibold text-slate-700">
                Reviewing {selectedReviewIndex + 1} of {selectedReviewTasks.length} selected tasks
              </span>
              <button type="button" className="wp-button min-h-9"
                disabled={selectedReviewIndex === 0}
                onClick={() => setDrawerTaskId(selectedReviewTasks[selectedReviewIndex - 1].task_id)}>
                Previous task
              </button>
              <button type="button" className="wp-button min-h-9"
                disabled={selectedReviewIndex === selectedReviewTasks.length - 1}
                onClick={() => setDrawerTaskId(selectedReviewTasks[selectedReviewIndex + 1].task_id)}>
                Next task
              </button>
            </nav>}
            actions={<>
              {!['DONE', 'CANCELLED'].includes(drawerTask.status) &&
                <button type="button" disabled={!actionCapabilities?.canEdit && !actionCapabilities?.canAssign}
                  className="min-h-11 rounded-lg border border-blue-700 bg-blue-800 px-2 text-sm font-semibold text-white hover:bg-blue-900 disabled:cursor-not-allowed disabled:opacity-50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-700"
                  onClick={() => { const item = drawerTask; closeDrawer(); openTaskEditor(item, !actionCapabilities?.canEdit); }}>
                  {!actionCapabilities || actionCapabilities.canEdit ? 'Assign & schedule' : 'Assign contributor'}
                </button>}
              <button type="button" className="min-h-9 rounded-md border border-slate-300 bg-white px-3 text-xs font-semibold text-slate-900 hover:bg-slate-100 focus-visible:outline focus-visible:outline-2 focus-visible:outline-blue-700"
                onClick={() => { const item = drawerTask; closeDrawer(); setDiscussionTaskId(item.task_id); }}>
                Activity
              </button>
              <button type="button" className="min-h-9 rounded-md border border-slate-300 bg-white px-3 text-xs font-semibold text-slate-900 hover:bg-slate-100 focus-visible:outline focus-visible:outline-2 focus-visible:outline-blue-700"
                onClick={() => { const item = drawerTask; closeDrawer(); setAttachmentTaskId(item.task_id); }}>
                Attachments
              </button>
              <button type="button" className="min-h-9 rounded-md border border-slate-300 bg-white px-3 text-xs font-semibold text-slate-900 hover:bg-slate-100 focus-visible:outline focus-visible:outline-2 focus-visible:outline-blue-700"
                onClick={() => { const item = drawerTask; closeDrawer(); setApprovalTaskId(item.task_id); }}>
                Approvals
              </button>
            </>}
          />
          <div className="min-h-0 flex-1 overflow-y-auto px-5 pb-8 sm:px-7">
            {taskIntelligenceOpen ? <section aria-label="WILSY AI task intelligence"
              className="mt-4 rounded-lg border border-slate-200 bg-white px-4 py-4 sm:px-5">
              <header className="mb-4 flex flex-wrap items-center justify-between gap-3">
                <div className="space-y-1">
                  <h4 className="text-sm font-semibold text-slate-900">WILSY AI · Task intelligence</h4>
                  <p className="text-xs text-slate-500">Current authorized source · No model required</p>
                </div>
                <button type="button" className="min-h-10 rounded-md border border-slate-300 bg-white px-3 text-xs font-medium text-blue-800 hover:bg-slate-50"
                  onClick={openTaskIntelligenceConversation}>Continue in conversation</button>
              </header>
              <WilsyDockOperatingWork
                tenantId={tenantId} principalId={principalId} scope={scope}
                locator={{ workspace: 'PROJECTS', project_id: projectId,
                  task_id: drawerTask.task_id, task_revision: drawerTask.revision,
                  participant_view: Boolean(selfIsContributor) }}
                providerReady={false} usageConsent={false} readOnly embedded
                onReviewActivity={() => { const id = drawerTask.task_id; closeDrawer(); setDiscussionTaskId(id); }}
                onReviewEvidence={() => { const id = drawerTask.task_id; closeDrawer(); setAttachmentTaskId(id); }}
                onReviewApprovals={() => { const id = drawerTask.task_id; closeDrawer(); setApprovalTaskId(id); }}
                onVerified={() => { void load(offset); }} onRecord={() => {}} />
            </section> : <>
            {!['DONE', 'CANCELLED'].includes(drawerTask.status) &&
              <UnifiedTaskReadiness revision={drawerTask.revision}
                description="Current EOS task facts. Evidence, approvals and production release remain independently governed."
                facts={[
                  { label: 'Accountable contributor', value: drawerTask.assignee_principal_id
                    ? contributorName(drawerTask.assignee_principal_id) : 'Assignment required' },
                  { label: 'Delivery deadline', value: drawerTask.due_date
                    ? drawerTask.due_date < todayISO ? 'Overdue · ' + drawerTask.due_date : drawerTask.due_date
                    : 'Due date required' },
                  { label: 'Source lifecycle', value: label(drawerTask.status) },
                  { label: 'Predecessor gate · current verified page',
                    value: drawerTask.depends_on.some(id => !items.some(item => item.task_id === id))
                      ? 'Some predecessors outside verified page'
                      : drawerTask.depends_on.filter(id => items.some(item =>
                        item.task_id === id && item.status !== 'DONE')).length > 0
                        ? 'Waiting on ' + drawerTask.depends_on.filter(id => items.some(item =>
                          item.task_id === id && item.status !== 'DONE')).length + ' predecessor(s)'
                        : 'No unfinished predecessors visible on this page' },
                ]}
                actions={<>
                {(actionCapabilities?.canEdit || actionCapabilities?.canAssign) && <button type="button"
                  className="min-h-11 rounded-lg border border-blue-700 bg-blue-800 px-4 py-2 text-sm font-bold text-white hover:bg-blue-900 focus-visible:outline focus-visible:outline-2 focus-visible:outline-blue-700"
                  onClick={() => { const item = drawerTask; closeDrawer(); openTaskEditor(item, !actionCapabilities?.canEdit); }}>
                  {drawerTask.assignee_principal_id && drawerTask.due_date
                    ? 'Revise assignment or deadline'
                    : 'Assign contributor and schedule'}
                </button>}
                <button type="button" className="min-h-11 rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-semibold text-slate-900 hover:bg-slate-100 focus-visible:outline focus-visible:outline-2 focus-visible:outline-blue-700"
                  onClick={() => { const item = drawerTask; closeDrawer(); setAttachmentTaskId(item.task_id); }}>
                  Review supporting evidence
                </button>
                <button type="button" className="min-h-11 rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-semibold text-slate-900 hover:bg-slate-100 focus-visible:outline focus-visible:outline-2 focus-visible:outline-blue-700"
                  onClick={() => { const item = drawerTask; closeDrawer(); setApprovalTaskId(item.task_id); }}>
                  Review approvals
                </button>
                <button type="button" className="min-h-11 rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-semibold text-slate-900 hover:bg-slate-100 focus-visible:outline focus-visible:outline-2 focus-visible:outline-blue-700"
                  onClick={() => { const item = drawerTask; closeDrawer(); setDiscussionTaskId(item.task_id); }}>
                  Record activity
                </button>
              </>}
                footnote="Task status does not certify deployment readiness, rollback capability, evidence clearance or strategic outcome attainment. Review independently authorized source records before completion."
              />}
            {drawerTask.kind === 'TASK'
              && /(?:^|—\\s*)certify production readiness and rollback$/i.test(drawerTask.title.trim())
              && <ProjectReadinessRollback
                key={[scope, drawerTask.task_id, drawerTask.revision].join(':')}
                task={drawerTask} tenantId={tenantId} principalId={principalId}
                projectId={projectId} headers={headers}
                onOpenEvidence={() => { const item = drawerTask; closeDrawer(); setAttachmentTaskId(item.task_id); }}
                onOpenApprovals={() => { const item = drawerTask; closeDrawer(); setApprovalTaskId(item.task_id); }}/>}
            <section className="pt-5" aria-label="Task description">
              <h4 className="text-sm font-bold text-slate-950">Description</h4>
              <p className="mt-2 whitespace-pre-wrap break-words text-sm leading-relaxed text-slate-800">
                {drawerTask.description || 'No description recorded'}
              </p>
            </section>
            <details className="mt-5 rounded-xl border border-slate-200 bg-slate-50 px-4 py-3">
              <summary className="cursor-pointer text-sm font-bold text-slate-900">Work classification and history</summary>
              <p className="mt-2 text-xs text-slate-700">Review the saved category or propose an authorized change. This is separate from assignment and deadlines.</p>
              <ProjectWorkPurposePanel
                key={[scope, drawerTask.task_id, drawerTask.revision].join(':')}
                task={drawerTask} projectId={projectId}
                tenantId={tenantId} principalId={principalId}
                tenantHeaders={tenantHeaders} canClassify={Boolean(actionCapabilities?.canEdit)}/>
            </details>
            <section className="mt-5 border-t border-slate-200 pt-4">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <h4 className="text-sm font-bold text-slate-950">Dependencies</h4>
                {actionCapabilities?.canEdit && drawerTask.status !== 'CANCELLED' &&
                  <button type="button" disabled={busy || state !== 'READY'}
                    className="min-h-10 rounded-lg border border-slate-300 bg-white px-3 text-xs font-semibold text-blue-800 hover:bg-blue-50 disabled:opacity-50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-blue-700"
                    onClick={() => {
                      if (creating) {
                        setError('Finish or close the existing task draft before creating a dependent task.');
                        closeDrawer();
                        return;
                      }
                      const predecessor = drawerTask;
                      setWorkType('TASK');
                      setDraft({ ...EMPTY, kind: 'TASK', depends_on: [predecessor.task_id] });
                      setDependencyOriginId(predecessor.task_id);
                      setEditor(null);
                      closeDrawer();
                      setCreating(true);
                    }}>
                    Create dependent task
                  </button>}
              </div>
              <p className="mt-2 text-xs text-slate-600">Existing predecessors are immutable in EOS. Create a dependent task to add a new source-verified relationship without rewriting the current graph.</p>
              <h5 className="mt-4 text-xs font-semibold uppercase tracking-wide text-slate-600">Blocked by</h5>
              {drawerTask.depends_on.length === 0
                ? <p className="mt-2 text-sm text-slate-700">No predecessors</p>
                : <ul className="mt-2 space-y-2">
                  {drawerTask.depends_on.map(id => {
                    const predecessor = items.find(value => value.task_id === id);
                    return <li key={id} className="rounded-lg bg-slate-50 p-3 text-sm text-slate-800">
                      {predecessor ? predecessor.title + ' · ' + label(predecessor.status)
                        : 'Predecessor outside the current verified page'}
                    </li>;
                  })}
                </ul>}
              <h5 className="mt-4 text-xs font-semibold uppercase tracking-wide text-slate-600">
                Blocks · current verified EOS batch
              </h5>
              {items.filter(item => item.depends_on.includes(drawerTask.task_id)).length === 0
                ? <p className="mt-2 text-sm text-slate-700">
                  No successors are visible on this verified page. Other pages are not inferred.
                </p>
                : <ul className="mt-2 space-y-2">
                  {items.filter(item => item.depends_on.includes(drawerTask.task_id))
                    .map(item => <li key={item.task_id} className="rounded-md bg-slate-50 p-2 text-sm text-slate-800">
                      {item.title} · {label(item.status)}
                    </li>)}
                </ul>}
            </section>
            </>}
          </div>
        </aside>
      </div>}
      {(hasMore || offset > 0) && <nav className="mt-3 flex flex-wrap items-center justify-between gap-2 rounded-xl border border-slate-200 p-3" aria-label="EOS task batches">
        <button type="button" className="wp-button" disabled={busy || offset === 0}
          onClick={() => void load(Math.max(0, offset - 50))}>Previous EOS batch</button>
        <span className="text-xs text-slate-600">Verified EOS batch {Math.floor(offset / 50) + 1} · up to 50 source records per batch</span>
        <button type="button" className="wp-button" disabled={busy || !hasMore}
          onClick={() => void load(offset + 50)}>Next EOS batch</button>
      </nav>}
      </div>
    </>}
    {state === 'READY' && error && <div role="alert"
      className="fixed bottom-4 left-4 right-4 z-[120] flex max-w-md items-start justify-between gap-3 rounded-xl border border-rose-300 bg-white p-4 text-sm text-rose-900 shadow-xl sm:left-auto sm:right-6">
      <span className="min-w-0 flex-1">{error}</span>
      <button type="button" className="shrink-0 rounded-md border border-rose-300 px-2 py-1 font-semibold text-rose-900 focus-visible:outline focus-visible:outline-2 focus-visible:outline-blue-700"
        onClick={() => setError('')}>Dismiss error</button>
    </div>}
  </section>;
}

// ARTIFACT: ProjectTasksPanel.jsx
// VERSION: v1.71.0-TASK-NATIVE-INTELLIGENCE-ACTIONS
// AUTHORITY BOUNDARY: EOS-verified owner task commands; no local state authority
// TENANT POSTURE: exact session tenant/principal/project readback, no fallback
// FAIL-CLOSED POSTURE: invalid data, denied commands and uncertain source stay visible
// FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
// END OF WILSY OS SOVEREIGN ARTIFACT
