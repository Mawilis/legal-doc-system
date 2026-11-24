/**
 * TITLE: WILSY OS Authenticated Projects Workspace
 * VERSION: v2.43.0-ONE-NETWORK-MOUNT-PER-SCOPE
 * AUTHORITY: Python EOS Projects API and existing authenticated api.js transport.
 * EPITOME: Presents source-backed project list, create, detail, update, status,
 *          archive and immutable event evidence without creating local truth.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/components/workspaces/ProjectsWorkspace.jsx
 * COLLABORATION / OWNERSHIP: Projects domain and registry own business truth;
 *                            EOS owns admission; Headquarters owns navigation.
 * CERTIFICATION / UPDATE DATE: 2026-11-20.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
 * SECURITY / PRIVACY POSTURE: No token or permission claims are read here;
 *                             the existing api.js owns authenticated transport.
 * TENANT BOUNDARY: Tenant selector is an EOS transport hint only; EOS requires
 *                  equality with authenticated session scope and tenant-scopes persistence.
 * AUTHORITY BOUNDARY: UI affordances are requests; EOS reauthorizes each route
 *                     and returns committed project/event state.
 * FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
 * CHANGELOG: v2.43.0-ONE-NETWORK-MOUNT-PER-SCOPE defers
 *            initial Projects list and summary reads to the post-effect
 *            microtask, preventing the discarded development StrictMode
 *            mount from sending duplicate authenticated MongoDB traffic.
 *            Explicit refresh and source-authorized reads are unchanged.
 * CHANGELOG: v2.42.0-COMPACT-PROJECT-WORKSPACE-CHROME
 *            gives task work priority over project header furniture:
 *            breadcrumb, project title and source status share a compact
 *            wrapped row; project views are one horizontally scrollable
 *            navigation strip. All existing routes and authorities remain.
 * CHANGELOG: v2.41.0-STRATEGY-TASK-FOCUS-PROPAGATION
 *            forwards exact task identity only after authorized project
 *            detail, retaining source-owned task and IAM verification.
 * CHANGELOG: v2.40.0-PLAIN-LANGUAGE-PROJECT-RECOVERY
 *            makes unavailable and stale project states understandable and
 *            actionable without exposing backend codes; preserves user
 *            intent, source-denial boundaries, empty-state truth and retries.
 * CHANGELOG: v2.39.0-EXACT-SELECTED-TASK-INTELLIGENCE-LOCATORS publishes the
 *          EOS-hydrated task id/revision only while that task is actively
 *          viewed inside the current project. Leaving the task removes it.
 *          Python EOS reauthorizes and re-reads task source on each request.
 * CHANGELOG: v2.38.0-EPHEMERAL-AI-CONTEXT-LOCATORS publishes only bounded
 *          current project locators to the contextual Dock. EOS independently
 *          resolves source visibility; browser events contain no names, task
 *          content, entitlement or permission facts and are never persisted.
 * CHANGELOG: v2.37.0-TEMPLATE-FAILURE-DIAGNOSTICS-RETRY exposes bounded, privacy-safe
 *          template catalogue HTTP or schema failures and a real retry.
 *          A mismatched backend cannot be mistaken for an empty template
 *          library. No unchecked or locally invented template is rendered.
 * CHANGELOG: v2.36.0-SEVENTEEN-TEMPLATE-CATALOGUE-COMPAT repairs the seven-template client
 *          validation ceiling, accepts the verified new 17-industry
 *          catalogue and labels the legacy seven-template EOS source as
 *          incomplete rather than inventing the missing templates.
 * CHANGELOG: v2.35.0-BILLABLE-AI-EXPLICIT-ADMISSION-CONSENT requires explicit
 *          user acknowledgement before invoking a potentially billable
 *          WILSY AI reasoning operation; the existing server-owned
 *          entitlement, consumption admission and model binding remain
 *          authoritative and failures never activate a project.
 * CHANGELOG: v2.34.0-AUDITED-DEADLINE-RATIONALE-VIEW displays the source-owned
 *          deadline-change rationale in the immutable audit timeline and
 *          removes opaque actor IDs from browser hover titles.
 * CHANGELOG: v2.33.0-OVERVIEW-JSX-STRUCTURE-REPAIR closes conditional
 *          creator/owner badge expressions after removing internal title IDs;
 *          restores valid JSX without re-exposing backend identities.
 * CHANGELOG: v2.32.0-GOVERNED-WILSY-AI-TEMPLATE-DRAFT uses the existing
 *          tenant-authorized WILSY AI reasoning endpoint to propose strictly
 *          validated edits to a reviewed template. Model output is staged
 *          only as a local draft, with no implicit project or IAM command.
 * CHANGELOG: v2.31.0-CUSTOMIZABLE-GOVERNED-TEMPLATE-STEPS allows review and
 *          per-project edits to source template titles, due offsets and
 *          acceptance criteria before one atomic EOS activation command;
 *          step identity, DAG and assigned authority remain unchanged.
 * CHANGELOG: v2.30.0-IMMUTABLE-BASELINE-AUDITED-TARGET makes code/start read-only
 *          after creation and asks for a persisted, audited reason when
 *          changing a previously committed project target date.
 * CHANGELOG: v2.29.0-HUMAN-OVERVIEW-VERIFIED-DEPARTMENT capitalizes lifecycle status,
 *          resolves assigned department names from exact-tenant EOS source,
 *          hides generated opaque project codes and audit-only revision from
 *          the operating overview without inferring ownership or assignments.
 * CHANGELOG: v2.28.0-UNCERTAIN-TEMPLATE-SAVE-RECOVERY sends ambiguous
 *          activation outcomes to the authorized project list with a name
 *          filter, without issuing a duplicate write or claiming commit truth.
 * CHANGELOG: v2.27.1-TEMPLATE-SELECTED-WORK-VISIBILITY restores immediately
 *          visible, EOS-sourced selected-template work while retaining the
 *          dismissed industry catalogue and human-readable project identity.
 * CHANGELOG: v2.27.0-TEMPLATE-OPERATING-FOCUS makes template preview opt-in
 *          after selection and hides opaque generated codes in operating views.
 * CHANGELOG: v2.26.1-TEMPLATE-UNCERTAIN-COMMIT-RECOVERY distinguishes unverified
 *          activation outcomes from confirmed rejections, offers an
 *          authorized project-list recovery path, and never invites
 *          duplicate creation after ambiguous transport/readback.
 * CHANGELOG: v2.26.1-TEMPLATE-UNCERTAIN-COMMIT-RECOVERY reduces
 *          the persistent list toolbar to an operating title, current
 *          counts and action controls. Removes nonfunctional hero copy.
 * CHANGELOG: v2.25.1-PENDING-COMMIT-NONEMPTY-TRUTH corrects
 *          date-only template activation admission to exactly ten characters
 *          and numeric YYYY-MM-DD groups; Python EOS still strictly parses
 *          and authorizes actual due-date semantics.
 * CHANGELOG: v2.22.0-COMPACT-PROJECT-OPERATING-HEADER removes the
 *          redundant portfolio toolbar while working within a selected
 *          project, compresses its metadata/breadcrumb presentation and
 *          preserves full tenant navigation on the project list.
 * CHANGELOG: v2.21.0-ATOMIC-INDUSTRY-TEMPLATE-CREATION introduces a compact,
 *          EOS-verified seven-industry blueprint selector and explicit
 *          version-checked activation with single-command project/task readback.
 *          The UI never invents template or task results, nor grants staff,
 *          IAM, spending or approvals.
 * CHANGELOG: v2.20.0-PROJECT-ACTIVITY-NAVIGATION names the
 *          main source-backed project activity experience consistently,
 *          keeping project-wide Notes separate from task comment activity.
 * CHANGELOG: v2.19.0-TOP-LEVEL-PROJECT-DISCUSSIONS promotes
 *          project work discussions to the primary navigation alongside
 *          Overview, People and Notes. Reuses the exact-scope task/comment
 *          component, and does not aggregate or invent project-wide comments.
 * CHANGELOG: v2.18.0-READABLE-PROJECT-OVERVIEW improves source-backed
 *          overview readability, suppresses raw department IDs from primary
 *          prose when no verified name is provided, preserves identifier in
 *          the title for inspection, and makes owner/creator evidence legible.
 * CHANGELOG: v2.17.0-INDEPENDENT-SUMMARY-FAILURE-ISOLATION isolates transient
 *          project summary failures from independently verified list and
 *          detail navigation; explicit auth/entitlement denials still fail
 *          closed. Late summary results cannot restore denied visibility.
 * CHANGELOG: v2.16.0-REVISION-FIRST-AUDIT-TIMELINE presents validated EOS project
 *          audit events newest revision first, with deterministic timestamp
 *          and event-ID tie breakers, visual event-type timeline and full
 *          actor/revision/time evidence; does not reorder audit persistence.
 * CHANGELOG: v2.15.0-INDEPENDENT-PROJECT-LIST-READ publishes the independently verified
 * project page without waiting for the separate portfolio summary request;
 * summary failures remain explicit, including fail-closed scope/authority
 * denial. This preserves EOS list/readback semantics and does not cache data.
 * CHANGELOG: v2.14.0-INDEXED-OWNER-RESPONSIBILITY-PAGES uses source-filtered exact-owner pages before pagination, replacing incomplete current-page-only owner selection. Verifies every returned owner identity and preserves participant IAM separation.
 * CHANGELOG: v2.25.1-PENDING-COMMIT-NONEMPTY-TRUTH never shows a
 *          misleading verified-empty notice while a committed template
 *          project still awaits independent list/detail reconciliation.
 * CHANGELOG: v2.25.0-COLLAPSED-PORTFOLIO-ANALYTICS keeps the
 *          actual project list as the default operating surface and moves
 *          portfolio distribution behind explicit user disclosure.
 * CHANGELOG: v2.24.0-TEMPLATE-FOCUS-CONTRAST-HYGIENE hides the catalogue after choice, puts the
 *          actual template task preview and activation controls first,
 *          corrects inherited pale-gold field labels and suppresses raw
 *          backend project identifiers from the everyday project list.
 * CHANGELOG: v2.23.0-TEMPLATE-POSTCOMMIT-RECONCILIATION separates currently authorized owner responsibility from independently permitted participant assignments. My owned projects filters verified EOS owner identities on the current page; explicit participant access keeps its existing route and IAM with no founder fallback.
 * CHANGELOG: v2.25.1-PENDING-COMMIT-NONEMPTY-TRUTH restores meaningful bounded server validation and conflict details for assignment, prevents recreating a canonical existing department and reloads exact source when uncertainty occurs.
 * CHANGELOG: v2.25.1-PENDING-COMMIT-NONEMPTY-TRUTH surfaces exact-tenant EOS verified project creator, owner and audit actor names in Overview and History; immutable opaque IDs remain available as technical identifiers without replacing human labels.
 * CHANGELOG: v2.25.1-PENDING-COMMIT-NONEMPTY-TRUTH renders verified first/last names from the canonical exact-tenant EOS owner directory, retaining principal IDs strictly as selection values; missing names show an explicit unlabelled identity instead of guessed user data.
 * CHANGELOG: v2.25.1-PENDING-COMMIT-NONEMPTY-TRUTH replaces the clipped fixed-height list/detail split with a full-width, task-first selected project workspace. Separates Work, Overview, People, Notes, Manage and Audit without changing EOS authority or the unselected registry.
 * CHANGELOG: v2.25.1-PENDING-COMMIT-NONEMPTY-TRUTH opens
 *            current participant project execution directly from an
 *            EOS-authorized Daily Attention project handoff; owner source
 *            reads are not used as participant admission.
 * CHANGELOG: v2.25.1-PENDING-COMMIT-NONEMPTY-TRUTH opens the
 *            separately authorized participant Projects destination, without
 *            claiming owner privileges or weakening owner list admission.
 * CHANGELOG: v2.25.1-PENDING-COMMIT-NONEMPTY-TRUTH separates successful EOS template activation from
 *          independent list/detail reconciliation. An accepted project is
 *          never represented as a failed save merely because readback is
 *          slow or unavailable; no second write is initiated automatically.
 * CHANGELOG: v2.22.1-CANONICAL-TEMPLATE-DATE-ADMISSION mounts exact-tenant,
 *            EOS-sourced candidate selection and audited participant
 *            grant/revoke alongside task execution in selected project detail.
 * CHANGELOG: v2.25.1-PENDING-COMMIT-NONEMPTY-TRUTH mounts the independently source-backed
 *            task/subtask/milestone table and lifecycle editor inside the
 *            selected exact-tenant project detail without local work truth.
 * CHANGELOG: v2.25.1-PENDING-COMMIT-NONEMPTY-TRUTH mounts independently source-backed note
 *            list and author-only edit/archive inside selected project detail;
 *            no project lifecycle state or IAM authority is changed.
 * CHANGELOG: v2.25.1-PENDING-COMMIT-NONEMPTY-TRUTH applies status filtering at the exact-tenant
 *            EOS API before paging instead of filtering only the visible page;
 *            status changes reset pagination and preserve all authorization.
 * CHANGELOG: v2.25.1-PENDING-COMMIT-NONEMPTY-TRUTH consumes EOS verified has_more/next_offset page
 *            evidence, retaining legacy mock compatibility and denying malformed
 *            new metadata without claiming nonexistent pages.
 *            v2.25.1-PENDING-COMMIT-NONEMPTY-TRUTH exposes readable title-case
 *            status counts to assistive technology without changing EOS truth.
 *            v2.1.0-SOURCE-VERIFIED-PORTFOLIO-PAGES adds explicit
 *            server page navigation and real EOS summary-based portfolio
 *            distribution without simulating metrics or mutating records.
 *            v2.0.2-SOURCE-BACKED-TABLE-NULL-COPY distinguishes missing
 *            table target-date copy from the existing detail readback.
 *            v2.0.1-SOURCE-BACKED-TABLE-CODE-COPY distinguishes the list's
 *            empty code from the source-backed detail value without changing
 *            EOS commands or record truth.
 *            v2.0.0-SOURCE-BACKED-PROJECT-TABLE replaces card-like project rows
 *            with a responsive table sourced exclusively from existing EOS list
 *            fields, retaining search, status filtering, selection and commands.
 *            v1.9.6-ACCOUNTABILITY-SEMANTIC-STYLE-HOOK connects the actual accountability
 *            panel with scoped semantic label styling, preventing the global
 *            gold/uppercase form-label rules from leaking into this workflow.
 *            v1.9.5-OPTIONAL-CODE-HELPER-COPY reduces generated-code guidance to
 *            a brief optional sentence and retains exact-tenant uniqueness;
 *            project status, identity and assignment sources are unchanged.
 *            v1.9.4-VERIFIED-ASSIGNMENT-DIRECTORY-STATES distinguishes verified zero candidates
 *            from an unavailable source and makes assignment prerequisites
 *            explicit instead of implying a populated selection directory.
 *            v1.9.3-DETAIL-ONLY-ACTIVATION-GATE scopes activation option disabling
 *            exclusively to selected project detail; list status filters stay
 *            independent and safe before any project is selected.
 *            v1.9.2-PREACTIVATION-ACCOUNTABILITY-AFFORDANCE prevents the ACTIVE
 *            choice until EOS has saved owner and department, with a clear
 *            explanation; server independently rechecks both current sources.
 *            v1.9.1-ACCOUNTABILITY-IDEMPOTENCY-REUSE retains the exact command key through
 *            uncertain department and assignment retries until verified EOS
 *            readback; role/tenant and project state remain server-owned.
 *            v1.9.0-SOURCE-GOVERNED-ACCOUNTABILITY adds exact-tenant, EOS-verified
 *            owner and department selectors, separately authorized department
 *            provisioning and audited project assignment with fresh readback.
 *            v1.8.0-EOS-PROJECT-CODE-READBACK removes mandatory
 *            manual code entry from new-project creation, documents EOS
 *            generation and permits verified one-click code assignment
 *            for legacy null-code projects via revision-guarded PATCH.
 * CHANGELOG: v1.7.0-ALIGNED-CALENDAR-PROJECT-EXECUTION makes both
 *            project panels a coordinated execution surface and provides
 *            explicit native date picker actions in create and edit flows.
 *            ISO date drafts and EOS revision authority remain unchanged.
 * CHANGELOG: v1.6.0-EXPANDED-DETAIL-SEMANTIC-SCOPE expands the verified
 *            list before selection, provides a detail-led split after selection,
 *            formats escaped and same-line Markdown safely in collapsed and
 *            expanded modes, and exposes the EOS-supported project code edit.
 * CHANGELOG: v1.5.0-ACCESSIBLE-FLUID-PROJECT-DELIVERY replaces
 *            low-contrast project presentation with scoped responsive
 *            list/detail layout and accessible source-backed controls;
 *            formats long project scope as safe text without modifying
 *            EOS persistence, IAM, entitlement or command behavior.
 * CHANGELOG: v1.4.0-SCOPED-STRATEGY-PROJECT-FOCUS admits a Strategy handoff only after the
 *            project ID appears in a fresh exact-tenant EOS list, then loads
 *            source-authorized project detail and immutable audit events.
 *            The handoff is navigation, never an inferred governed link.
 * CHANGELOG: v1.3.0-EXACT-SCOPE-LIFECYCLE-READBACK validates principal/tenant envelopes for list, summary, detail and command results; requires fresh list/detail readback after lifecycle commands and verifies archived items leave the active list.
 *            v1.2.0-PROJECTS-CREATE-REPLAY-KEY-RETENTION preserves an unchanged
 *            create command's idempotency key through uncertain retries and
 *            resets it when the draft or authenticated scope changes. v1.1.0
 *            rejects late tenant/session reads and prioritizes HTTP status.
 */
import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import {
  Archive, CalendarDays, CircleAlert, Code2, LoaderCircle, Plus,
  RefreshCw, Search, ShieldCheck, X,
} from 'lucide-react';
import api from '../../services/api.js';
import ProjectNotesPanel from './ProjectNotesPanel.jsx';
import ProjectTasksPanel from './ProjectTasksPanel.jsx';
import ProjectParticipantsPanel from './ProjectParticipantsPanel.jsx';
import AssignedProjectsWorkspace from './AssignedProjectsWorkspace.jsx';
import './ProjectsWorkspace.css';

/**
 * @description Render a source-backed project description as safe, readable
 * structured text. Never parse HTML, infer strategy links, or mutate EOS text.
 * @authority Python EOS remains the sole source; this is display only.
 */
function ProjectSummary({ value, expanded, onToggle }) {
  const source = String(value || '');
  // Legacy pasted descriptions sometimes escaped markdown delimiters and
  // placed headings and numbered items on the same physical line.
  const normalized = source.replace(/\\([*_])/g, '$1')
    .replace(/\\n/g, '\n')
    .replace(/\s+(?=\*\*(?:Strategic Pillar \d|Project objective|Scope of execution|Initial delivery sequence|Definition of done|Governance)\b)/gi, '\n')
    .replace(/\s+(?=\d+\.\s+\*\*)/g, '\n')
    .replace(/\s+(?=-\s+Milestone \d+)/g, '\n');
  const inline = (text) => text.split(/(\*\*[^*]+\*\*)/g).filter(Boolean).map((piece, index) =>
    piece.startsWith('**') && piece.endsWith('**')
      ? <strong key={index}>{piece.slice(2, -2)}</strong>
      : <React.Fragment key={index}>{piece}</React.Fragment>);
  const content = normalized.split(/\r?\n/).flatMap((raw, index) => {
    const line = raw.trim();
    if (!line) return [];
    const heading = /^(?:#{1,4}\s+)?\*\*((?:Strategic Pillar \d|Project objective|Scope of execution|Initial delivery sequence|Definition of done|Governance)[^*]*)\*\*(.*)$/i.exec(line);
    if (heading) return [
      <h4 key={index + '-heading'}>{heading[1]}</h4>,
      ...(heading[2].trim() ? [<p key={index + '-body'}>{inline(heading[2].trim())}</p>] : []),
    ];
    const markdownHeading = /^#{1,4}\s+(.+)$/.exec(line);
    if (markdownHeading) return [<h4 key={index}>{inline(markdownHeading[1])}</h4>];
    const numbered = /^(\d+)\.\s+(.+)$/.exec(line);
    const bullet = /^[-•]\s+(.+)$/.exec(line);
    if (numbered || bullet) return [<p className="wp-list-line" key={index}>
      <span>{numbered ? numbered[1] + '.' : '•'}</span>
      <span>{inline(numbered ? numbered[2] : bullet[1])}</span>
    </p>];
    return [<p key={index}>{inline(line)}</p>];
  });
  const long = source.length > 550;
  return <section className="wp-section" aria-label="Project scope">
    <h3 className="wp-section-title">Project scope</h3>
    <div className="wp-summary">{expanded || !long ? content : content.slice(0, 5)}</div>
    {long && <button type="button" className="wp-summary-toggle" aria-expanded={expanded}
      onClick={onToggle}>{expanded ? 'Collapse project scope' : 'Read full project scope'}</button>}
  </section>;
}

/**
 * @description Native, accessible calendar selection for EOS date-only fields.
 * @authority The chosen YYYY-MM-DD value remains a draft until EOS validates
 * and persists the revision. No date is generated or silently defaulted.
 */
function ProjectDateField({ label, value, onChange, disabled = false }) {
  const pickerRef = useRef(null);
  const openCalendar = () => {
    const field = pickerRef.current;
    if (!field || disabled) return;
    if (typeof field.showPicker === 'function') {
      try {
        field.showPicker();
        return;
      } catch {
        // Browser support varies; focusing retains the native date control.
      }
    }
    field.focus();
  };
  return <label className="wp-date-field">
    <span style={{ color: '#172b4d', fontWeight: 650 }}>{label}</span>
    <span className="wp-date-wrap">
      <input ref={pickerRef} type="date" value={value || ''} disabled={disabled}
        onChange={event => onChange(event.target.value)}
        aria-label={label + ' date'} />
      <button type="button" className="wp-calendar-trigger"
        aria-label={'Choose ' + label.toLowerCase() + ' date'}
        disabled={disabled} onClick={openCalendar}>
        <CalendarDays size={17} aria-hidden="true"/>
      </button>
    </span>
  </label>;
}

/**
 * @description Derive the same user-facing code as Python EOS for an existing
 * legacy project whose code was never assigned.
 * @authority Client derivation is a proposal; only a revision-guarded EOS
 * patch and independent list/detail readback establish saved code truth.
 */
function suggestedProjectCode(projectId) {
  return typeof projectId === 'string' && /^prj-[0-9a-f]{48}$/.test(projectId)
    ? 'PRJ-' + projectId.slice(-16).toUpperCase()
    : null;
}

const PROJECT_STATUSES = ['planned', 'active', 'on_hold', 'done', 'cancelled'];
const EMPTY_DRAFT = { name: '', code: '', summary: '', start_date: '', target_date: '' };

/**
 * @description Resolve a stable, non-secret client presentation code.
 * @collaboration ProjectsWorkspace uses this for source-state feedback.
 * @institutional HTTP status takes precedence so an arbitrary response detail
 * cannot convert a denial or conflict into an unavailable-source state.
 * @param {unknown} cause Axios or local response validation failure.
 * @returns {string} Stable code safe for a user-facing state branch.
 */
function classifyFailure(cause) {
  const status = cause?.response?.status;
  if (status === 401) return 'AUTHENTICATION_REQUIRED';
  if (status === 403) {
    const detail = cause?.response?.data?.detail;
    const detailCode = typeof detail === 'string' ? detail : detail?.error;
    return detailCode === 'PROJECTS_ENTITLEMENT_REQUIRED'
      ? 'PROJECTS_ENTITLEMENT_REQUIRED'
      : 'ACCESS_DENIED';
  }
  const detail = cause?.response?.data?.detail;
  if ((status === 409 || status === 422) && typeof detail === 'string'
    && /^[A-Z0-9_]{1,100}$/.test(detail)) return detail;
  if ((status === 409 || status === 422) && detail && typeof detail.error === 'string'
    && /^[A-Z0-9_]{1,100}$/.test(detail.error)) return detail.error;
  if (status === 409) return 'PROJECT_REVISION_OR_REPLAY_CONFLICT';
  if (status === 422) return 'PROJECT_INPUT_INVALID';
  if (typeof detail === 'string' && /^[A-Z0-9_]{1,100}$/.test(detail)) return detail;
  if (detail && typeof detail.error === 'string' && /^[A-Z0-9_]{1,100}$/.test(detail.error)) return detail.error;
  return 'PROJECT_SOURCE_UNAVAILABLE';
}

/**
 * @description Validate a source-owned EOS project response before rendering.
 * @collaboration ProjectsWorkspace consumes the Projects router's committed result.
 * @institutional Reject foreign tenant/principal evidence and incomplete audit records.
 * @param {unknown} payload EOS result envelope.
 * @param {string} tenantId Current selected authenticated tenant.
 * @param {string} principalId Current authenticated principal.
 * @param {string} [projectId] Expected project identity for detail/command results.
 * @param {number} [minimumRevision] Minimum revision expected after an update.
 * @returns {Object} Validated project result envelope.
 * @throws {Error} Rejects any scope, identity, revision or audit mismatch.
 */
function assertProjectResult(payload, tenantId, principalId, projectId, minimumRevision) {
  const project = payload?.project;
  const events = payload?.events;
  if (
    payload?.schema !== 'WILSY-PROJECT-RESULT/V1'
    || payload?.tenant_id !== tenantId || payload?.principal_id !== principalId
    || payload?.authority?.source !== 'PYTHON_EOS_PROJECT_REGISTRY'
    || payload?.authority?.financial_execution !== false
    || !project || project.tenant_id !== tenantId
    || typeof project.project_id !== 'string' || !project.project_id
    || (projectId && project.project_id !== projectId)
    || !PROJECT_STATUSES.includes(project.status)
    || !Number.isSafeInteger(project.revision) || project.revision < (minimumRevision || 1)
    || !Array.isArray(events)
    || events.some((event) => !event || event.tenant_id !== tenantId
      || event.project_id !== project.project_id || typeof event.event_id !== 'string'
      || typeof event.event_type !== 'string' || typeof event.actor_principal_id !== 'string'
      || !Number.isSafeInteger(event.revision) || typeof event.occurred_at !== 'string'
      || Number.isNaN(Date.parse(event.occurred_at)))
    || (payload.actor_profiles !== undefined && (
      !payload.actor_profiles || Array.isArray(payload.actor_profiles)
      || typeof payload.actor_profiles !== 'object'
      || Object.entries(payload.actor_profiles).some(([id, profile]) =>
        ![project.created_by_principal_id, project.owner_principal_id,
          ...events.map(event => event.actor_principal_id)].includes(id)
        || !profile || typeof profile !== 'object'
        || !Object.hasOwn(profile, 'first_name') || !Object.hasOwn(profile, 'last_name')
        || ![profile.first_name, profile.last_name].every(name =>
          name === null || (typeof name === 'string'
            && name.length > 0 && name.length <= 100 && name === name.trim())))
    ))
  ) throw new Error('PROJECT_RESULT_SCOPE_OR_SHAPE_INVALID');
  return payload;
}

/**
 * @description Validate tenant/principal-bound project list readback.
 * @collaboration ProjectsWorkspace and Python EOS Projects list route.
 * @institutional Prevent unverified zeroes, duplicate rows and foreign rows.
 * @param {unknown} payload EOS list envelope.
 * @param {string} tenantId Exact selected tenant.
 * @param {string} principalId Exact authenticated principal.
 * @returns {Array<Object>} Validated active project records.
 * @throws {Error} Invalid list contract fails closed.
 */
function assertProjectList(payload, tenantId, principalId) {
  const items = payload?.items;
  const seen = new Set();
  if (payload?.schema !== 'WILSY-PROJECT-LIST/V1'
    || payload?.tenant_id !== tenantId || payload?.principal_id !== principalId
    || !Array.isArray(items)) throw new Error('PROJECT_LIST_SCOPE_OR_SHAPE_INVALID');
  for (const item of items) {
    if (!item || item.tenant_id !== tenantId || typeof item.project_id !== 'string'
      || !item.project_id || seen.has(item.project_id) || typeof item.name !== 'string'
      || !item.name.trim() || !PROJECT_STATUSES.includes(item.status)
      || !Number.isSafeInteger(item.revision) || item.revision < 1 || item.archived_at != null) {
      throw new Error('PROJECT_LIST_SCOPE_OR_SHAPE_INVALID');
    }
    seen.add(item.project_id);
  }
  return items;
}

/**
 * @description Validate the exact EOS status summary used by the Headquarters KPI.
 * @collaboration ProjectsWorkspace and WilsyHeadquartersWorkspace consume /projects/summary.
 * @institutional Status counts must reconcile to total before the UI displays them.
 * @param {unknown} payload EOS Projects summary envelope.
 * @param {string} tenantId Exact selected tenant.
 * @param {string} principalId Exact authenticated principal.
 * @returns {Object} Validated source counts.
 * @throws {Error} Missing or inconsistent source evidence fails closed.
 */
function assertProjectSummary(payload, tenantId, principalId) {
  const counts = payload?.counts;
  const statuses = ['active', 'planned', 'on_hold', 'done', 'cancelled'];
  if (
    payload?.schema !== 'WILSY-PROJECT-SUMMARY/V1'
    || payload?.tenant_id !== tenantId || payload?.principal_id !== principalId
    || !counts || !Number.isSafeInteger(counts.total) || counts.total < 0
    || !statuses.every((key) => Number.isSafeInteger(counts[key]) && counts[key] >= 0)
    || statuses.reduce((total, key) => total + counts[key], 0) !== counts.total
  ) throw new Error('PROJECT_SUMMARY_SCOPE_OR_SHAPE_INVALID');
  return counts;
}

/**
 * @description Render the tenant's authenticated EOS Projects lifecycle.
 * @collaboration WilsyHeadquartersWorkspace selects this view; api.js supplies
 * the canonical authenticated HTTP transport; Python EOS owns every result.
 * @institutional The component renders only server-returned state and sends
 * revision-guarded, idempotent commands to existing EOS routes.
 * @param {{tenantId?: string|null, sessionScope?: string, focusProjectId?: string|null}} props Exact selected
 * tenant and session generation supplied by the authenticated workspace owner.
 * @returns {JSX.Element} A source-backed Projects workspace.
 */

function ProjectAccountabilityPanel({ project, tenantId, principalId, tenantHeaders, runCommand, refresh, openProject }) {
  const [options, setOptions] = useState(null);
  const [state, setState] = useState('LOADING');
  const [owner, setOwner] = useState(project.owner_principal_id || '');
  const [department, setDepartment] = useState(project.department_id || '');
  const [newDepartmentName, setNewDepartmentName] = useState('');
  const [localError, setLocalError] = useState('');
  const departmentReplay = useRef({ fingerprint: '', key: null });
  const assignmentReplay = useRef({ fingerprint: '', key: null });

  const loadOptions = useCallback(async () => {
    const { data } = await api.get('/projects/assignment-options', { headers: tenantHeaders });
    if (data?.schema !== 'WILSY-PROJECT-ASSIGNMENT-OPTIONS/V1'
      || data?.tenant_id !== tenantId
      || !Array.isArray(data.principals) || !Array.isArray(data.departments)
      || data.principals.some(value => value.eligibility !== 'VERIFIED_CURRENT'
        || typeof value.principal_id !== 'string'
        || !Object.hasOwn(value, 'first_name') || !Object.hasOwn(value, 'last_name')
        || ![value.first_name, value.last_name].every(name =>
          name === null || (typeof name === 'string' && name.length > 0
            && name.length <= 100 && name === name.trim())))
      || data.departments.some(value => value.status !== 'ACTIVE' || typeof value.department_id !== 'string' || typeof value.name !== 'string')) {
      throw new Error('PROJECT_ASSIGNMENT_SOURCE_INVALID');
    }
    return data;
  }, [tenantId, tenantHeaders]);

  useEffect(() => {
    let live = true;
    setState('LOADING');
    setOptions(null);
    setOwner(project.owner_principal_id || '');
    setDepartment(project.department_id || '');
    loadOptions().then(data => {
      if (!live) return;
      setOptions(data);
      setState('READY');
    }).catch(() => {
      if (live) setState('UNAVAILABLE');
    });
    return () => { live = false; };
  }, [loadOptions, project.project_id, project.revision]);

  const newKey = () => {
    if (typeof globalThis.crypto?.randomUUID !== 'function') throw new Error('IDEMPOTENCY_KEY_GENERATOR_UNAVAILABLE');
    return globalThis.crypto.randomUUID();
  };

  const retainedCommandKey = (reference, fingerprint) => {
    if (reference.current.fingerprint !== fingerprint || !reference.current.key) {
      reference.current = { fingerprint, key: newKey() };
    }
    return reference.current.key;
  };

  const createDepartment = async (event) => {
    event.preventDefault();
    const name = newDepartmentName.trim();
    if (name.length < 2) return;
    const existing = options?.departments.find(value =>
      value.name.trim().toLocaleLowerCase() === name.toLocaleLowerCase());
    if (existing) {
      setDepartment(existing.department_id);
      setLocalError('This department already exists. It has been selected; save the audited assignment to use it.');
      return;
    }
    setLocalError('');
    const confirmed = await runCommand(async () => {
      const { data } = await api.post('/projects/departments', { name }, {
        headers: { ...tenantHeaders,
          'Idempotency-Key': retainedCommandKey(departmentReplay, JSON.stringify([tenantId, name])) },
      });
      if (data?.tenant_id !== tenantId || data?.department?.name !== name
        || data.department.status !== 'ACTIVE') throw new Error('PROJECT_DEPARTMENT_READBACK_INVALID');
      const verified = await loadOptions();
      if (!verified.departments.some(value => value.department_id === data.department.department_id)) {
        throw new Error('PROJECT_DEPARTMENT_DIRECTORY_READBACK_UNAVAILABLE');
      }
      setOptions(verified);
      setDepartment(data.department.department_id);
      setNewDepartmentName('');
      departmentReplay.current = { fingerprint: '', key: null };
    });
    if (!confirmed) {
      try {
        const verified = await loadOptions();
        setOptions(verified);
        const matching = verified.departments.find(value =>
          value.name.toLocaleLowerCase() === name.toLocaleLowerCase());
        if (matching) {
          setDepartment(matching.department_id);
          setLocalError('A canonical department with this name is already available. Select it and save the assignment.');
          return;
        }
      } catch { /* Retain the original safe server error. */ }
      setLocalError('EOS did not authorize or verify department creation. No duplicate department was created by this response.');
    }
  };

  const saveAssignment = async (event) => {
    event.preventDefault();
    if (!options?.principals.some(value => value.principal_id === owner)
      || !options?.departments.some(value => value.department_id === department)) return;
    setLocalError('');
    const confirmed = await runCommand(async () => {
      let data;
      try {
        ({ data } = await api.patch(
          `/projects/${encodeURIComponent(project.project_id)}/assignment`,
          { expected_revision: project.revision, owner_principal_id: owner, department_id: department },
          { headers: { ...tenantHeaders,
            'Idempotency-Key': retainedCommandKey(assignmentReplay,
              JSON.stringify([tenantId, project.project_id, project.revision, owner, department])) } },
        ));
      } catch (cause) {
        if (cause?.response?.status === 422) {
          const detail = cause.response.data?.detail;
          const fieldPaths = Array.isArray(detail)
            ? detail.slice(0, 3).map(item => {
              const parts = Array.isArray(item?.loc) ? item.loc.filter(value =>
                typeof value === 'string' && /^[a-z_]{1,40}$/.test(value)) : [];
              return parts.slice(-2).join('.');
            }).filter(Boolean)
            : [];
          setLocalError(fieldPaths.length
            ? 'EOS rejected the assignment fields: ' + fieldPaths.join(', ')
              + '. No assignment was saved.'
            : 'EOS rejected the assignment payload (422). Review the safe response detail and refresh the project.');
        } else if (cause?.response?.status === 403) {
          setLocalError('EOS denied project-update authorization (403). Project creation is a separate permission.');
        }
        throw cause;
      }
      const next = assertProjectResult(data, tenantId, principalId, project.project_id, project.revision + 1).project;
      if (next.owner_principal_id !== owner || next.department_id !== department
        || next.status !== project.status) throw new Error('PROJECT_ASSIGNMENT_READBACK_INVALID');
      const list = await refresh();
      if (!list?.items.some(item => item.project_id === project.project_id && item.revision === next.revision)) {
        throw new Error('PROJECT_ASSIGNMENT_LIST_READBACK_UNAVAILABLE');
      }
      if (!await openProject(project.project_id)) throw new Error('PROJECT_ASSIGNMENT_DETAIL_READBACK_UNAVAILABLE');
      assignmentReplay.current = { fingerprint: '', key: null };
    });
    if (!confirmed) {
      setLocalError(previous => previous || 'Assignment was not confirmed. Inspect the EOS error above; refresh before retrying.');
    }
  };

  return <section aria-label="Project accountability" className="wp-accountability mb-5 border-t border-slate-200 pt-4">
    <h3 className="font-semibold text-slate-900">Owner and department governance</h3>
    <p className="mt-1 text-xs text-slate-600">Only current verified EOS identities and tenant departments are selectable. Project creation does not automatically assign ownership or grant additional IAM authority.</p>
    {state === 'LOADING' && <p role="status" className="mt-2 text-sm text-slate-600">Verifying authorized assignment sources…</p>}
    {state === 'UNAVAILABLE' && <p role="alert" className="mt-2 text-sm text-rose-700">Assignment sources unavailable. <button type="button" onClick={() => {
      setState('LOADING');
      loadOptions().then(data => { setOptions(data); setState('READY'); }).catch(() => setState('UNAVAILABLE'));
    }} className="underline">Retry</button></p>}
    {state === 'READY' && <>
      <p role="status" aria-live="polite" className="mt-3 text-sm font-semibold text-slate-800" data-assignment-directory-status>
        EOS verified {options.principals.length} eligible project {options.principals.length === 1 ? 'owner' : 'owners'} and {options.departments.length} active tenant {options.departments.length === 1 ? 'department' : 'departments'}.
      </p>
      {options.principals.length === 0 && <p role="status" className="mt-2 text-sm text-amber-900">
        No eligible project owner has been verified in the current tenant. A current principal, active tenant membership and eligible tenant-owner capacity are required; the form cannot create those authorities.
      </p>}
      {options.departments.length === 0 && <p role="status" className="mt-2 text-sm text-amber-900">
        No active canonical tenant department is recorded. Use the separately authorized department-creation command below before assigning this project.
      </p>}
      <form onSubmit={saveAssignment} className="mt-3 grid gap-3">
        <label className="block text-xs font-semibold text-slate-700">Eligible project owner
          <select aria-label="Eligible project owner" value={owner} disabled={options.principals.length === 0} onChange={event => setOwner(event.target.value)}
            className="mt-1 min-h-11 w-full rounded-lg border border-slate-300 bg-white px-3 text-sm font-normal">
            <option value="">Select a verified principal</option>
            {options.principals.map(value => {
              const name = [value.first_name, value.last_name].filter(Boolean).join(' ');
              const duplicate = name && options.principals.some(other =>
                other.principal_id !== value.principal_id
                && [other.first_name, other.last_name].filter(Boolean).join(' ') === name);
              return <option key={value.principal_id} value={value.principal_id}>
                {name || 'Verified principal (name not recorded)'}
                {(duplicate || !name) ? ' · ' + value.principal_id.slice(-6) : ''}
              </option>;
            })}
          </select>
        </label>
        <label className="block text-xs font-semibold text-slate-700">Tenant department
          <select aria-label="Tenant department" value={department} disabled={options.departments.length === 0} onChange={event => setDepartment(event.target.value)}
            className="mt-1 min-h-11 w-full rounded-lg border border-slate-300 bg-white px-3 text-sm font-normal">
            <option value="">Select a verified department</option>
            {options.departments.map(value => <option key={value.department_id} value={value.department_id}>{value.name}</option>)}
          </select>
        </label>
        <button type="submit" disabled={!owner || !department || !options.principals.some(value => value.principal_id === owner) || !options.departments.some(value => value.department_id === department)}
          className="min-h-11 rounded-lg bg-blue-900 px-4 text-sm font-semibold text-white disabled:opacity-50">Save audited assignment</button>
      </form>
      <form onSubmit={createDepartment} className="mt-4 grid gap-2 border-t border-slate-200 pt-3">
        <label className="block text-xs font-semibold text-slate-700">Create governed tenant department
          <input aria-label="Department name" value={newDepartmentName} onChange={event => setNewDepartmentName(event.target.value)}
            minLength={2} maxLength={100} required placeholder="e.g. Platform Engineering"
            className="mt-1 min-h-11 w-full rounded-lg border border-slate-300 px-3 text-sm font-normal"/>
        </label>
        <button type="submit" disabled={newDepartmentName.trim().length < 2}
          className="min-h-11 rounded-lg border border-blue-700 px-4 text-sm font-semibold text-blue-800 disabled:opacity-50">Create authorized department</button>
        <p className="text-xs text-slate-500">Creating a tenant department is an organizational administration action. EOS requires both tenant-profile-write and project-create authority; creating a project alone does not grant profile-write access.</p>
      </form>
    </>}
    {localError && <p role="alert" className="mt-2 text-sm text-rose-700">{localError}</p>}
  </section>;
}

/**
 * @description Renders exact-scope Projects and publishes ephemeral navigation locators.
 * @collaboration Canonical EOS Projects routes, work panels and contextual Dock.
 * @institutional Source readback owns truth; locator events confer no access or command authority.
 * @param {Object} props Authenticated scope and optional project navigation hints.
 * @returns {React.ReactElement} Governed project registry and work surface.
 */
export default function ProjectsWorkspace({ tenantId = null, principalId = null, sessionScope = '', focusProjectId = null, focusTaskId = null, focusAssignedProjectId = null }) {
  const [items, setItems] = useState([]);
  const [summary, setSummary] = useState(null);
  const [sourceState, setSourceState] = useState('LOADING');
  const [error, setError] = useState('');
  const [query, setQuery] = useState('');
  const [ownerOnly, setOwnerOnly] = useState(false);
  const ownerOnlyRef = useRef(false);
  const [statusFilter, setStatusFilter] = useState('all');
  const statusFilterRef = useRef('all');
  const [pageOffset, setPageOffset] = useState(0);
  const [hasNextPage, setHasNextPage] = useState(false);
  const pageOffsetRef = useRef(0);
  const [selectedId, setSelectedId] = useState(null);
  const [focusedTask, setFocusedTask] = useState(null);
  const [projectView, setProjectView] = useState('work');
  const [summaryExpanded, setSummaryExpanded] = useState(false);
  const [detail, setDetail] = useState(null);
  const [overviewDepartment, setOverviewDepartment] = useState({ id: null, name: null, status: 'IDLE' });
  const [detailState, setDetailState] = useState('IDLE');
  const [mode, setMode] = useState('LIST');
  const [templates, setTemplates] = useState([]);
  const [templateState, setTemplateState] = useState('IDLE');
  const [templateError, setTemplateError] = useState('');
  const [templateFailureCode, setTemplateFailureCode] = useState('');
  const [templateRetry, setTemplateRetry] = useState(0);
  const [selectedTemplateSlug, setSelectedTemplateSlug] = useState('');
  const [templatePickerOpen, setTemplatePickerOpen] = useState(true);
  const [templateName, setTemplateName] = useState('');
  const [templateEditing, setTemplateEditing] = useState(false);
  const [templateOverrides, setTemplateOverrides] = useState({});
  const [aiProjectBrief, setAiProjectBrief] = useState('');
  const [aiUsageAcknowledged, setAiUsageAcknowledged] = useState(false);
  const [aiProjectState, setAiProjectState] = useState('IDLE');
  const [aiProjectError, setAiProjectError] = useState('');
  const aiDraftReplay = useRef({ fingerprint: '', key: null });
  const [templateStart, setTemplateStart] = useState('');
  const [templateReconciliation, setTemplateReconciliation] = useState(null);
  const templateSequence = useRef(0);
  const [showAssignedProjects, setShowAssignedProjects] = useState(
    Boolean(focusAssignedProjectId && /^prj-[0-9a-f]{48}$/.test(focusAssignedProjectId)),
  );
  const [draft, setDraft] = useState(EMPTY_DRAFT);
  const [edit, setEdit] = useState(null);
  const [targetChangeReason, setTargetChangeReason] = useState('');
  const [commandState, setCommandState] = useState('IDLE');
  const [commandError, setCommandError] = useState('');
  const listSequence = useRef(0);
  const detailSequence = useRef(0);
  const commandPending = useRef(false);
  const createReplay = useRef({ fingerprint: '', key: null });
  const activeScope = useRef('');
  const selectedRef = useRef(null);
  const focusHandled = useRef(null);
  const itemsRef = useRef([]);
  const scopeKey = `${tenantId || ''}\u0000${principalId || ''}\u0000${sessionScope || ''}`;
  activeScope.current = scopeKey;

  const tenantHeaders = useMemo(
    () => tenantId ? { 'X-Tenant-ID': tenantId } : undefined,
    [tenantId],
  );

  const changeSelection = useCallback((projectId) => {
    if (projectId !== selectedRef.current) {
      setProjectView('work');
      setFocusedTask(null);
    }
    selectedRef.current = projectId;
    setSelectedId(projectId);
  }, []);
  const handleFocusedTaskChange = useCallback(next => {
    const current = next && /^ptk-[0-9a-f]{48}$/.test(next.task_id || '')
      && Number.isSafeInteger(next.task_revision) && next.task_revision >= 1
      ? { task_id: next.task_id, task_revision: next.task_revision } : null;
    setFocusedTask(previous => previous?.task_id === current?.task_id
      && previous?.task_revision === current?.task_revision ? previous : current);
  }, []);

  const refresh = useCallback(async ({ preserveSelection = true } = {}) => {
    const sequence = ++listSequence.current;
    const requestScope = scopeKey;
    if (!tenantId || !principalId) {
      itemsRef.current = [];
      setItems([]);
      setSummary(null);
      setDetail(null);
      changeSelection(null);
      setSourceState('DENIED');
      setError('AUTHENTICATED_TENANT_AND_PRINCIPAL_REQUIRED');
      return null;
    }
    setSourceState((current) => current === 'READY' || current === 'STALE' ? 'REFRESHING' : 'LOADING');
    setSummary(null);
    setError('');
    let listFailed = false;
    try {
      // Portfolio aggregation is independent of the authorized project page.
      // A healthy /projects response must not wait on a slower /summary.
      // Both results retain their own exact session scope checks.
      let summaryAuthorityDenied = false;
      void api.get('/projects/summary', { headers: tenantHeaders }).then(response => {
        if (listFailed || sequence !== listSequence.current || activeScope.current !== requestScope
          || summaryAuthorityDenied) return;
        setSummary(assertProjectSummary(response?.data, tenantId, principalId));
      }).catch(cause => {
        if (listFailed || sequence !== listSequence.current || activeScope.current !== requestScope) return;
        const code = classifyFailure(cause);
        setSummary(null);
        // Invalid cross-scope or malformed envelopes are security failures, not
        // an ordinary unavailable counter. Do not retain project visibility.
        if (cause?.message === 'PROJECT_SUMMARY_SCOPE_OR_SHAPE_INVALID') {
          summaryAuthorityDenied = true;
          itemsRef.current = [];
          setItems([]);
          setDetail(null);
          changeSelection(null);
          setError('PROJECT_SOURCE_UNAVAILABLE');
          setSourceState('UNAVAILABLE');
          return;
        }
        // A transient summary outage is not proof that the independently
        // verified authorized project page has failed.
        if (code === 'ACCESS_DENIED' || code === 'AUTHENTICATION_REQUIRED'
          || code === 'PROJECTS_ENTITLEMENT_REQUIRED') {
          summaryAuthorityDenied = true;
          itemsRef.current = [];
          setItems([]);
          setDetail(null);
          changeSelection(null);
          setError(code);
          setSourceState('DENIED');
        }
      });
      const listResponse = await api.get(
        statusFilterRef.current === 'all' && pageOffsetRef.current === 0 && !ownerOnlyRef.current
          ? '/projects'
          : `/projects?limit=100&offset=${pageOffsetRef.current}${statusFilterRef.current === 'all' ? '' : `&project_status=${statusFilterRef.current}`}${ownerOnlyRef.current ? '&owned_by_me=true' : ''}`,
        { headers: tenantHeaders },
      );
      if (summaryAuthorityDenied) return null;
      if (sequence !== listSequence.current || activeScope.current !== requestScope) return null;
      const nextItems = assertProjectList(listResponse?.data, tenantId, principalId);
      if (ownerOnlyRef.current && nextItems.some(item => item.owner_principal_id !== principalId)) {
        throw new Error('PROJECT_OWNER_PAGE_SOURCE_INVALID');
      }
      const pageEvidence = listResponse?.data;
      const hasPageEvidence = Object.prototype.hasOwnProperty.call(pageEvidence, 'has_more');
      if (hasPageEvidence && (
        typeof pageEvidence.has_more !== 'boolean'
        || pageEvidence.offset !== pageOffsetRef.current
        || pageEvidence.limit !== 100
        || (pageEvidence.has_more
          ? pageEvidence.next_offset !== pageOffsetRef.current + nextItems.length
          : pageEvidence.next_offset != null)
      )) throw new Error('PROJECT_PAGE_EVIDENCE_INVALID');
      const verifiedNextPage = hasPageEvidence ? pageEvidence.has_more : nextItems.length === 100;
      itemsRef.current = nextItems;
      setItems(nextItems);
      setHasNextPage(verifiedNextPage);
      if (!summaryAuthorityDenied) setSourceState('READY');
      const currentSelection = selectedRef.current;
      if (!preserveSelection || (currentSelection && !nextItems.some((item) => item.project_id === currentSelection))) {
        changeSelection(null);
        setDetail(null);
        setDetailState('IDLE');
      }
      return { items: nextItems };
    } catch (cause) {
      listFailed = true;
      if (sequence !== listSequence.current || activeScope.current !== requestScope) return null;
      setSummary(null);
      const code = classifyFailure(cause);
      setError(code);
      if (code === 'ACCESS_DENIED' || code === 'AUTHENTICATION_REQUIRED' || code === 'PROJECTS_ENTITLEMENT_REQUIRED') {
        itemsRef.current = [];
        setItems([]);
        setSummary(null);
        setDetail(null);
        changeSelection(null);
        setSourceState('DENIED');
      } else if (itemsRef.current.length > 0) {
        setSourceState('STALE');
      } else {
        setSourceState('UNAVAILABLE');
      }
      return null;
    }
  }, [tenantId, principalId, tenantHeaders, scopeKey, changeSelection]);

  useEffect(() => {
    listSequence.current += 1;
    detailSequence.current += 1;
    itemsRef.current = [];
    selectedRef.current = null;
    focusHandled.current = null;
    setItems([]);
    setSummary(null);
    setSelectedId(null);
    setDetail(null);
    setDetailState('IDLE');
    setSourceState('LOADING');
    setError('');
    setMode('LIST');
    templateSequence.current += 1;
    setTemplates([]);
    setTemplateState('IDLE');
    setTemplateError('');
    setSelectedTemplateSlug('');
    setTemplatePickerOpen(true);
    setTemplateName('');
    setTemplateEditing(false);
    setTemplateOverrides({});
    setAiProjectBrief('');
    setAiUsageAcknowledged(false);
    setAiProjectState('IDLE');
    setAiProjectError('');
    aiDraftReplay.current = { fingerprint: '', key: null };
    setTemplateStart('');
    setTemplateReconciliation(null);
    setDraft(EMPTY_DRAFT);
    createReplay.current = { fingerprint: '', key: null };
    setQuery('');
    setOwnerOnly(false);
    ownerOnlyRef.current = false;
    setStatusFilter('all');
    statusFilterRef.current = 'all';
    pageOffsetRef.current = 0;
    setPageOffset(0);
    setHasNextPage(false);
    let active = true;
    if (focusAssignedProjectId && /^prj-[0-9a-f]{48}$/.test(focusAssignedProjectId)) {
      setShowAssignedProjects(true);
    } else {
      // React development StrictMode replays effects in the same turn;
      // discarded setup must not launch a second EOS list/summary fanout.
      queueMicrotask(() => {
        if (active) void refresh({ preserveSelection: false });
      });
    }
    return () => {
      active = false;
      listSequence.current += 1;
      detailSequence.current += 1;
    };
  }, [scopeKey, refresh, focusAssignedProjectId]);

  const visibleItems = useMemo(() => {
    const normalized = query.trim().toLocaleLowerCase();
    return items.filter((item) => (
      (statusFilter === 'all' || item.status === statusFilter)
      && (!ownerOnly || item.owner_principal_id === principalId)
      && (!normalized || [item.name, item.code, item.summary, item.status]
        .some((value) => String(value || '').toLocaleLowerCase().includes(normalized)))
    ));
  }, [items, query, statusFilter, ownerOnly, principalId]);

  const openProject = useCallback(async (projectId) => {
    const sequence = ++detailSequence.current;
    const requestScope = scopeKey;
    changeSelection(projectId);
    setDetail(null);
    setSummaryExpanded(false);
    setDetailState('LOADING');
    setCommandError('');
    try {
      const response = await api.get(`/projects/${encodeURIComponent(projectId)}`, { headers: tenantHeaders });
      if (sequence !== detailSequence.current || activeScope.current !== requestScope || selectedRef.current !== projectId) return false;
      const payload = assertProjectResult(response?.data, tenantId, principalId, projectId);
      const project = payload.project;
      setDetail(payload);
      setEdit({ name: project.name, code: project.code || '', summary: project.summary || '', start_date: project.start_date || '', target_date: project.target_date || '' });
      setDetailState('READY');
      return true;
    } catch (cause) {
      if (sequence !== detailSequence.current || activeScope.current !== requestScope) return false;
      setDetailState('ERROR');
      setCommandError(classifyFailure(cause));
      return false;
    }
  }, [scopeKey, tenantId, principalId, tenantHeaders, changeSelection]);

  // These events carry locators only. They do not transfer the Projects IAM
  // decision to the Dock or authorize any model egress or business command.
  useEffect(() => {
    if (!tenantId || !principalId) return undefined;
    const publish = () => window.dispatchEvent(new CustomEvent('wilsy:ai-context-locator', {
      detail: { tenantId, principalId, locator: {
        workspace: 'PROJECTS',
        ...(selectedId && detailState === 'READY' && detail?.project?.project_id === selectedId
          ? { project_id: selectedId, project_revision: detail.project.revision,
            ...(projectView === 'work' || projectView === 'discussions'
              ? focusedTask || {} : {}) } : {}),
      } },
    }));
    const inspect = event => {
      const reference = event.detail;
      if (reference?.tenantId !== tenantId || reference?.principalId !== principalId
        || reference.project_id !== selectedId || !/^prj-[0-9a-f]{48}$/.test(reference.project_id || '')) return;
      setProjectView('overview');
      void openProject(reference.project_id);
    };
    window.addEventListener('wilsy:ai-context-request', publish);
    window.addEventListener('wilsy:ai-inspect-source', inspect);
    publish();
    return () => {
      window.removeEventListener('wilsy:ai-context-request', publish);
      window.removeEventListener('wilsy:ai-inspect-source', inspect);
      window.dispatchEvent(new CustomEvent('wilsy:ai-context-locator', {
        detail: { tenantId, principalId, locator: { workspace: 'HEADQUARTERS' } },
      }));
    };
  }, [tenantId, principalId, sessionScope, selectedId, detailState, projectView,
    focusedTask?.task_id, focusedTask?.task_revision,
    detail?.project?.project_id, detail?.project?.revision, openProject]);

  // A Strategy-to-Projects handoff is navigation only. Require an exact
  // authorized first-page list before opening one EOS detail/audit read.
  // Suppress repeated focus after manual selection or a later list refresh.
  useEffect(() => {
    if (!focusProjectId || !/^prj-[0-9a-f]{48}$/.test(focusProjectId)
      || sourceState !== 'READY' || !items.some(item => item.project_id === focusProjectId)
      || focusHandled.current === scopeKey + ':' + focusProjectId) return;
    focusHandled.current = scopeKey + ':' + focusProjectId;
    void openProject(focusProjectId);
  }, [focusProjectId, sourceState, items, scopeKey, openProject]);

  const newIdempotencyKey = () => {
    if (!globalThis.crypto || typeof globalThis.crypto.randomUUID !== 'function') {
      throw new Error('IDEMPOTENCY_KEY_GENERATOR_UNAVAILABLE');
    }
    return globalThis.crypto.randomUUID();
  };

  const createIdempotencyKey = (body) => {
    const fingerprint = JSON.stringify(body);
    if (createReplay.current.fingerprint !== fingerprint || !createReplay.current.key) {
      createReplay.current = { fingerprint, key: newIdempotencyKey() };
    }
    return createReplay.current.key;
  };

  const runCommand = async (command) => {
    if (commandPending.current) return false;
    commandPending.current = true;
    setCommandState('PENDING');
    setCommandError('');
    try {
      await command();
      setCommandState('CONFIRMED');
      return true;
    } catch (cause) {
      const code = classifyFailure(cause);
      setCommandState('FAILED');
      setCommandError(code);
      if (cause?.response?.status === 409 || ![401, 403, 422].includes(cause?.response?.status)) {
        await refresh();
        if (selectedRef.current) await openProject(selectedRef.current);
      }
      return false;
    } finally {
      commandPending.current = false;
    }
  };

  useEffect(() => {
    if (mode !== 'TEMPLATE') return;
    const serial = ++templateSequence.current;
    const current = scopeKey;
    setTemplateState('LOADING');
    setTemplateError('');
    setTemplateFailureCode('');
    void (async () => {
      try {
        const { data } = await api.get('/projects/templates', { headers: tenantHeaders });
        if (serial !== templateSequence.current || activeScope.current !== current) return;
        if (!data || typeof data !== 'object'
          || data.schema !== 'WILSY-PROJECT-TEMPLATE-CATALOGUE/V1'
          || data.tenant_id !== tenantId || data.principal_id !== principalId
          || data.ownership !== 'PLATFORM_STARTERS' || !Array.isArray(data.items)) {
          throw new Error('TEMPLATE_CATALOGUE_ENVELOPE_INVALID');
        }
        if (![7, 17].includes(data.items.length)) {
          throw new Error('TEMPLATE_CATALOGUE_COUNT_' + String(data.items.length).slice(0, 5));
        }
        if (
          new Set(data.items.map(item => item.slug)).size !== data.items.length
          || data.items.some(item => typeof item.slug !== 'string'
            || !/^[a-z][a-z0-9-]{2,63}$/.test(item.slug)
            || typeof item.industry !== 'string' || !item.industry
            || typeof item.title !== 'string' || !item.title
            || !Number.isSafeInteger(item.revision) || item.revision < 1
            || !Array.isArray(item.steps) || item.steps.length < 2 || item.steps.length > 25
            || item.steps.some(step => !['TASK','MILESTONE'].includes(step.kind)
              || typeof step.title !== 'string' || !step.title
              || !Number.isSafeInteger(step.day) || step.day < 0
              || typeof step.role !== 'string' || !step.role
              || typeof step.acceptance !== 'string' || !step.acceptance
              || !Array.isArray(step.depends_on)))) {
          throw new Error('PROJECT_TEMPLATE_SOURCE_INVALID');
        }
        setTemplates(data.items);
        setTemplateFailureCode('');
        setTemplateState('READY');
      } catch (cause) {
        if (serial !== templateSequence.current || activeScope.current !== current) return;
        const status = cause?.response?.status;
        const code = status === 401 ? 'HTTP_401_SESSION_REQUIRED'
          : status === 403 ? 'HTTP_403_CATALOGUE_ACCESS_DENIED'
            : status === 404 ? 'HTTP_404_PROJECTS_TEMPLATES_ROUTE_MISSING'
              : status === 408 || cause?.code === 'ECONNABORTED'
                ? 'TEMPLATE_REQUEST_TIMED_OUT'
                : status === 503 ? 'HTTP_503_EOS_DEPENDENCY_UNAVAILABLE'
                  : Number.isInteger(status) ? 'HTTP_' + status
                    : typeof cause?.message === 'string'
                      && /^TEMPLATE_CATALOGUE_[A-Z0-9_]{1,80}$/.test(cause.message)
                      ? cause.message : 'TEMPLATE_TRANSPORT_UNAVAILABLE';
        setTemplateFailureCode(code);
        setTemplateState(status === 403 || status === 401 ? 'DENIED' : 'UNAVAILABLE');
        setTemplateError(code === 'HTTP_401_SESSION_REQUIRED'
          ? 'Your authenticated EOS session needs renewal before templates can be verified.'
          : code === 'HTTP_403_CATALOGUE_ACCESS_DENIED'
            ? 'EOS denied template catalogue access for this selected tenant and principal.'
            : code === 'HTTP_404_PROJECTS_TEMPLATES_ROUTE_MISSING'
              ? 'The running Python EOS does not expose the Projects template route. Check the backend checkout.'
              : code.startsWith('TEMPLATE_CATALOGUE_')
                ? 'The running EOS returned a template catalogue that failed WILSY source verification.'
                : 'The authorized template catalogue could not be loaded from Python EOS.');
      }
    })();
    return () => { templateSequence.current += 1; };
  }, [mode, scopeKey, tenantId, principalId, tenantHeaders, templateRetry]);

  const selectedTemplate = templates.find(item => item.slug === selectedTemplateSlug);

  const reconcileTemplateActivation = async (persisted) => {
    // POST already committed the template. A transient list/detail failure is
    // strictly readback-unavailable, never a failed activation or a retry cue.
    const projection = await refresh({ preserveSelection: false });
    const row = projection?.items.find(item => item.project_id === persisted.project_id
      && item.tenant_id === tenantId && item.revision >= persisted.revision);
    if (!row) {
      setTemplateReconciliation(previous => previous?.project_id === persisted.project_id
        ? { ...previous, state: 'READBACK_PENDING' } : previous);
      return;
    }
    const opened = await openProject(persisted.project_id);
    setTemplateReconciliation(previous => previous?.project_id === persisted.project_id
      ? { ...previous, state: opened ? 'VERIFIED' : 'READBACK_PENDING' } : previous);
  };

  const askWilsyAiForTemplateDraft = async () => {
    if (aiProjectState === 'PENDING' || templateState !== 'READY'
      || !selectedTemplate || aiProjectBrief.trim().length < 20 || !aiUsageAcknowledged) {
      setAiProjectError('Describe the business goal and expected delivery in at least 20 characters.');
      return;
    }
    const brief = aiProjectBrief.trim();
    const current = scopeKey;
    const activeSlug = selectedTemplate.slug;
    const fingerprint = JSON.stringify([activeSlug, selectedTemplate.revision, brief]);
    if (aiDraftReplay.current.fingerprint !== fingerprint || !aiDraftReplay.current.key) {
      aiDraftReplay.current = { fingerprint, key: newIdempotencyKey() };
    }
    const schema = selectedTemplate.steps.map(step => ({
      id: step.id, kind: step.kind, role: step.role, day: step.day,
      title: step.title, acceptance: step.acceptance, depends_on: step.depends_on,
    }));
    const prompt = [
      'You are WILSY AI project planning support. Produce one strictly valid JSON object only.',
      'JSON shape: {"project_name":"string","steps":[{"id":"string","title":"string","day":integer,"acceptance":"string"}]}.',
      'Use exactly one entry per existing step ID. Never add, delete or rename IDs.',
      'Keep predecessor scheduling valid. Days are nonnegative and <=3650.',
      'Titles must be 1-180 chars and acceptance text 1-1000 chars.',
      'Do not assign people, issue IAM, change project roles or authorize spending.',
      'Existing approved platform blueprint:', JSON.stringify(schema),
      'User reviewed planning brief:', brief,
    ].join('\n');
    setAiProjectState('PENDING');
    setAiProjectError('');
    try {
      const { data } = await api.post('/wilsy-ai/reasoning', { prompt }, {
        headers: { ...tenantHeaders, 'Idempotency-Key': aiDraftReplay.current.key },
      });
      if (activeScope.current !== current || selectedTemplateSlug !== activeSlug) return;
      if (typeof data?.response_text !== 'string' || data.response_text.length > 16000) {
        throw new Error('WILSY_AI_PROJECT_PROPOSAL_INVALID');
      }
      const proposal = JSON.parse(data.response_text.trim());
      if (!proposal || Array.isArray(proposal) || typeof proposal !== 'object'
        || !Array.isArray(proposal.steps)
        || proposal.steps.length !== selectedTemplate.steps.length
        || (proposal.project_name !== undefined && (typeof proposal.project_name !== 'string'
          || !proposal.project_name.trim() || proposal.project_name.length > 180))) {
        throw new Error('WILSY_AI_PROJECT_PROPOSAL_INVALID');
      }
      const drafts = {};
      const days = {};
      for (const suggestion of proposal.steps) {
        const original = selectedTemplate.steps.find(step => step.id === suggestion?.id);
        if (!original || Object.hasOwn(drafts, original.id)
          || typeof suggestion.title !== 'string' || suggestion.title.trim().length < 1
          || suggestion.title.length > 180 || typeof suggestion.acceptance !== 'string'
          || suggestion.acceptance.trim().length < 1 || suggestion.acceptance.length > 1000
          || !Number.isInteger(suggestion.day) || suggestion.day < 0 || suggestion.day > 3650
          || original.depends_on.some(id => days[id] === undefined || days[id] > suggestion.day)) {
          throw new Error('WILSY_AI_PROJECT_PROPOSAL_INVALID');
        }
        drafts[original.id] = { title: suggestion.title.trim(),
          acceptance: suggestion.acceptance.trim(), day: suggestion.day };
        days[original.id] = suggestion.day;
      }
      if (Object.keys(drafts).length !== selectedTemplate.steps.length) {
        throw new Error('WILSY_AI_PROJECT_PROPOSAL_INVALID');
      }
      setTemplateOverrides(drafts);
      if (proposal.project_name) setTemplateName(proposal.project_name.trim());
      setTemplateEditing(true);
      createReplay.current = { fingerprint: '', key: null };
      setAiProjectState('READY');
    } catch {
      if (activeScope.current === current) {
        setAiProjectState('UNAVAILABLE');
        setAiProjectError('WILSY AI could not provide a verified editable plan. Existing template remains available.');
      }
    }
  };

  const activateTemplate = async (event) => {
    event.preventDefault();
    if (templateState !== 'READY' || !selectedTemplate || !templateName.trim()
      || !/^[0-9]{4}-[0-9]{2}-[0-9]{2}$/.test(templateStart)) {
      setTemplateError('Choose a verified template, enter a project name and select a start date.');
      return;
    }
    const step_overrides = selectedTemplate.steps.flatMap(step => {
      const override = templateOverrides[step.id];
      if (!override) return [];
      const changed = { id: step.id };
      if (override.title !== step.title) changed.title = String(override.title).trim();
      if (override.day !== step.day) changed.day = Number(override.day);
      if (override.acceptance !== step.acceptance) changed.acceptance = String(override.acceptance).trim();
      return Object.keys(changed).length > 1 ? [changed] : [];
    });
    if (step_overrides.some(step => ('title' in step && !step.title)
        || ('acceptance' in step && !step.acceptance)
        || ('day' in step && (!Number.isInteger(step.day) || step.day < 0 || step.day > 3650)))) {
      setTemplateError('Check work titles, acceptance evidence and days before saving.');
      return;
    }
    const body = {
      name: templateName.trim(),
      template_revision: selectedTemplate.revision,
      start_date: templateStart,
      ...(step_overrides.length ? { step_overrides } : {}),
    };
    let persisted = null;
    let activationCause = null;
    const accepted = await runCommand(async () => {
      try {
      const response = await api.post(
        '/projects/templates/' + encodeURIComponent(selectedTemplate.slug) + '/activate',
        body, { headers: {
          ...tenantHeaders, 'Idempotency-Key': createIdempotencyKey([
            'template', selectedTemplate.slug, body,
          ]),
        }},
      );
      const data = response?.data;
      if (data?.schema !== 'WILSY-PROJECT-TEMPLATE-ACTIVATION/V1'
        || data.tenant_id !== tenantId || data.principal_id !== principalId
        || data.template_slug !== selectedTemplate.slug
        || data.template_revision !== selectedTemplate.revision
        || data.authority?.iam_grants !== false
        || data.authority?.auto_assignments !== false
        || data.authority?.financial_execution !== false
        || !Array.isArray(data.items) || data.items.length !== selectedTemplate.steps.length
        || !data.project?.project_id
        || data.items.some(item => !item || typeof item.task_id !== 'string'
          || !/^ptk-[a-f0-9]{48}$/.test(item.task_id))) {
        throw new Error('PROJECT_TEMPLATE_ACTIVATION_SOURCE_INVALID');
      }
      // Reuse the authoritative project shape validator, but do not fabricate
      // audit events: the activation response supplies an independently
      // verified project snapshot, and project detail owns event readback.
      persisted = assertProjectResult({
        schema: 'WILSY-PROJECT-RESULT/V1',
        tenant_id: tenantId, principal_id: principalId, project: data.project,
        events: [], authority: {
          source: 'PYTHON_EOS_PROJECT_REGISTRY', financial_execution: false,
        },
      }, tenantId, principalId).project;
      } catch (cause) {
        activationCause = cause;
        throw cause;
      }
    });
    if (!accepted || !persisted) {
      const status = activationCause?.response?.status;
      if (activationCause && (!status || status >= 500)) {
        // A lost/invalid reply may follow a durable commit. Search current
        // authorized rows; never retry a mutation or claim a name match proves
        // this command's outcome.
        setTemplateReconciliation({ project_id: null, name: body.name,
          code: null, state: 'UNCONFIRMED' });
        setQuery(body.name);
        setMode('LIST');
        setCommandError('');
      }
      return;
    }
    setTemplateReconciliation({
      project_id: persisted.project_id,
      name: persisted.name,
      code: persisted.code,
      state: 'READBACK_PENDING',
    });
    setMode('LIST');
    setTemplateError('');
    createReplay.current = { fingerprint: '', key: null };
    // Do not throw from the independent readback. An EOS-committed project must
    // never be displayed as "saving failed" because the browser lost its read.
    await reconcileTemplateActivation(persisted);
  };

  const submitCreate = async (event) => {
    event.preventDefault();
    if (!draft.name.trim()) {
      setCommandError('PROJECT_NAME_REQUIRED');
      return;
    }
    const body = {
      name: draft.name.trim(),
      code: draft.code.trim() || null,
      summary: draft.summary.trim() || null,
      start_date: draft.start_date || null,
      target_date: draft.target_date || null,
    };
    const succeeded = await runCommand(async () => {
      const response = await api.post('/projects', body, {
        headers: { ...tenantHeaders, 'Idempotency-Key': createIdempotencyKey(body) },
      });
      const created = assertProjectResult(response?.data, tenantId, principalId).project;
      const projection = await refresh({ preserveSelection: false });
      if (!projection?.items.some((item) => item.project_id === created.project_id
        && item.tenant_id === tenantId && item.revision === created.revision)) {
        throw new Error('PROJECT_CREATE_NOT_IN_AUTHORIZED_PROJECTION');
      }
      if (!await openProject(created.project_id)) throw new Error('PROJECT_CREATE_DETAIL_READBACK_UNAVAILABLE');
      createReplay.current = { fingerprint: '', key: null };
      setDraft(EMPTY_DRAFT);
      setMode('LIST');
    });
    if (!succeeded) setMode('CREATE');
  };

  const submitUpdate = async (event) => {
    event.preventDefault();
    if (!detail?.project || !edit || !selectedId) return;
    const project = detail.project;
    const targetChanged = (edit.target_date || null) !== (project.target_date || null);
    const reason = targetChangeReason.trim();
    if (targetChanged && project.target_date && reason.length < 12) {
      setCommandError('PROJECT_TARGET_CHANGE_REASON_REQUIRED');
      return;
    }
    await runCommand(async () => {
      const response = await api.patch(`/projects/${encodeURIComponent(selectedId)}`, {
        expected_revision: project.revision,
        name: edit.name,
        summary: edit.summary || null,
        target_date: edit.target_date || null,
        ...(targetChanged && project.target_date ? { target_change_reason: reason } : {}),
      }, { headers: { ...tenantHeaders, 'Idempotency-Key': newIdempotencyKey() } });
      const result = assertProjectResult(response?.data, tenantId, principalId, selectedId, project.revision + 1);
      const projection = await refresh();
      if (!projection?.items.some((item) => item.project_id === selectedId && item.revision === result.project.revision)) {
        throw new Error('PROJECT_UPDATE_LIST_READBACK_UNAVAILABLE');
      }
      if (!await openProject(selectedId)) throw new Error('PROJECT_UPDATE_DETAIL_READBACK_UNAVAILABLE');
      setTargetChangeReason('');
    });
  };

  const assignGeneratedCode = async () => {
    if (!detail?.project || !selectedId || detail.project.code || sourceState !== 'READY') return;
    const current = detail.project;
    const generated = suggestedProjectCode(current.project_id);
    if (!generated) {
      setCommandError('PROJECT_CODE_SOURCE_INVALID');
      return;
    }
    await runCommand(async () => {
      const response = await api.patch(`/projects/${encodeURIComponent(selectedId)}`, {
        expected_revision: current.revision,
        code: generated,
      }, { headers: { ...tenantHeaders, 'Idempotency-Key': newIdempotencyKey() } });
      const result = assertProjectResult(
        response?.data, tenantId, principalId, selectedId, current.revision + 1,
      );
      if (result.project.code !== generated) throw new Error('PROJECT_CODE_COMMAND_READBACK_INVALID');
      const projection = await refresh();
      if (!projection?.items.some(item => item.project_id === selectedId
        && item.revision === result.project.revision && item.code === generated)) {
        throw new Error('PROJECT_CODE_LIST_READBACK_UNAVAILABLE');
      }
      if (!await openProject(selectedId)) throw new Error('PROJECT_CODE_DETAIL_READBACK_UNAVAILABLE');
    });
  };

  const transitionStatus = async (nextStatus) => {
    if (!detail?.project || !selectedId || !PROJECT_STATUSES.includes(nextStatus) || nextStatus === detail.project.status) return;
    const current = detail.project;
    await runCommand(async () => {
      const response = await api.patch(`/projects/${encodeURIComponent(selectedId)}`, {
        expected_revision: current.revision,
        status: nextStatus,
      }, { headers: { ...tenantHeaders, 'Idempotency-Key': newIdempotencyKey() } });
      const result = assertProjectResult(response?.data, tenantId, principalId, selectedId, current.revision + 1);
      if (result.project.status !== nextStatus) throw new Error('PROJECT_STATUS_READBACK_INVALID');
      const projection = await refresh();
      if (!projection?.items.some((item) => item.project_id === selectedId
        && item.status === nextStatus && item.revision === result.project.revision)) {
        throw new Error('PROJECT_STATUS_LIST_READBACK_UNAVAILABLE');
      }
      if (!await openProject(selectedId)) throw new Error('PROJECT_STATUS_DETAIL_READBACK_UNAVAILABLE');
    });
  };

  const archiveProject = async () => {
    if (!detail?.project || !selectedId) return;
    const current = detail.project;
    await runCommand(async () => {
      const response = await api.post(`/projects/${encodeURIComponent(selectedId)}/archive`, {
        expected_revision: current.revision,
      }, { headers: { ...tenantHeaders, 'Idempotency-Key': newIdempotencyKey() } });
      const result = assertProjectResult(response?.data, tenantId, principalId, selectedId, current.revision + 1);
      if (result.project.archived_at == null) throw new Error('PROJECT_ARCHIVE_READBACK_INVALID');
      const projection = await refresh({ preserveSelection: true });
      if (!projection || projection.items.some((item) => item.project_id === selectedId)) {
        throw new Error('PROJECT_ARCHIVE_LIST_READBACK_UNAVAILABLE');
      }
      changeSelection(null);
      setDetail(null);
      setDetailState('IDLE');
    });
  };

  const closeDetail = () => {
    detailSequence.current += 1;
    changeSelection(null);
    setDetail(null);
    setDetailState('IDLE');
    setCommandError('');
  };

  const changeStatusFilter = (value) => {
    if (sourceState !== 'READY' || !['all', ...PROJECT_STATUSES].includes(value)) return;
    statusFilterRef.current = value;
    setStatusFilter(value);
    pageOffsetRef.current = 0;
    setPageOffset(0);
    setHasNextPage(false);
    changeSelection(null);
    setDetail(null);
    setDetailState('IDLE');
    setQuery('');
    void refresh({ preserveSelection: false });
  };

  const changePage = (nextOffset) => {
    if (sourceState !== 'READY' || commandState === 'PENDING'
      || nextOffset < 0 || (nextOffset > pageOffsetRef.current && !hasNextPage)) return;
    pageOffsetRef.current = nextOffset;
    setPageOffset(nextOffset);
    detailSequence.current += 1;
    changeSelection(null);
    setDetail(null);
    setDetailState('IDLE');
    setQuery('');
    void refresh({ preserveSelection: false });
  };

  useEffect(() => {
    const project = detail?.project;
    if (projectView !== 'overview' || detailState !== 'READY'
      || !project?.department_id || !tenantId || !principalId) {
      setOverviewDepartment({ id: null, name: null, status: 'IDLE' });
      return undefined;
    }
    const departmentId = project.department_id;
    let alive = true;
    setOverviewDepartment({ id: departmentId, name: null, status: 'VERIFYING' });
    api.get('/projects/assignment-options', { headers: tenantHeaders }).then(({ data }) => {
      if (!alive) return;
      const valid = data?.schema === 'WILSY-PROJECT-ASSIGNMENT-OPTIONS/V1'
        && data.tenant_id === tenantId && Array.isArray(data.departments)
        && data.departments.every(item => typeof item.department_id === 'string'
          && typeof item.name === 'string' && item.status === 'ACTIVE');
      const match = valid && data.departments.find(item => item.department_id === departmentId);
      setOverviewDepartment({ id: departmentId,
        name: match?.name || null, status: match ? 'READY' : 'UNAVAILABLE' });
    }).catch(() => {
      if (alive) setOverviewDepartment({ id: departmentId, name: null, status: 'UNAVAILABLE' });
    });
    return () => { alive = false; };
  }, [detail?.project?.department_id, detail?.project?.project_id, detail?.project?.revision,
    detailState, projectView, tenantId, principalId, tenantHeaders]);

  const personLabel = (principal) => {
    if (!principal) return 'Not assigned';
    const profile = detail?.actor_profiles?.[principal];
    const name = [profile?.first_name, profile?.last_name].filter(Boolean).join(' ');
    return name || 'Name not recorded';
  };
  const statusLabel = (value) => {
    const readable = String(value || 'unknown').replaceAll('_', ' ');
    return readable.charAt(0).toUpperCase() + readable.slice(1);
  };
  const countLabel = summary
    ? `${ownerOnly ? 'Tenant · ' : ''}${summary.active ?? '—'} active · ${summary.total} total`
    : sourceState === 'LOADING' || sourceState === 'REFRESHING' ? 'Counts loading…' : 'Counts unavailable';

  if (showAssignedProjects) {
    return <AssignedProjectsWorkspace
      tenantId={tenantId} principalId={principalId}
      tenantHeaders={tenantHeaders} sessionScope={sessionScope}
      focusProjectId={focusAssignedProjectId}
      onBack={() => { setShowAssignedProjects(false); void refresh({ preserveSelection: false }); }}/>;
  }

  return (
    <section className="wilsy-projects mx-auto w-full max-w-[1500px] px-3 pb-6 sm:px-5" data-projects-workspace data-source-state={sourceState}>
      {!(selectedId && mode !== 'CREATE') && <header className="wp-toolbar mb-2 flex flex-wrap items-center justify-between gap-3 border-b border-slate-200 bg-white px-2 py-2">
        <h1 className="text-lg font-bold text-slate-950">Projects</h1>
        <div className="flex flex-wrap items-center gap-2"><div aria-live="polite" className="wp-kpi rounded-lg border border-slate-200 px-3 py-2 text-sm text-slate-700">{countLabel}</div><button type="button" onClick={() => {
          const next = !ownerOnlyRef.current;
          ownerOnlyRef.current = next;
          setOwnerOnly(next);
          setPageOffset(0);
          pageOffsetRef.current = 0;
          setHasNextPage(false);
          setMode('LIST');
          setQuery('');
          changeSelection(null);
          setDetail(null);
          setDetailState('IDLE');
          void refresh({ preserveSelection: false });
        }} className="wp-button" aria-pressed={ownerOnly}
          aria-label="My owned projects"><ShieldCheck size={15}/>
          {ownerOnly ? 'All projects' : 'My owned projects'}</button>
          <button type="button" onClick={() => setShowAssignedProjects(true)}
            className="wp-button" aria-label="Participant assignments"
            title="Requires a separate, active project participant grant">
            Participant assignments</button><button type="button" onClick={() => void refresh()} disabled={sourceState === 'LOADING' || sourceState === 'REFRESHING'} className="wp-button inline-flex min-h-10 items-center gap-2 rounded-lg border border-slate-300 px-3 text-sm font-semibold text-slate-700 hover:bg-slate-50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-blue-600 disabled:opacity-60"><RefreshCw size={15}/> Refresh</button><button type="button" onClick={() => { setMode('CREATE'); setCommandError(''); }} disabled={sourceState === 'DENIED' || sourceState === 'UNAVAILABLE' || sourceState === 'LOADING'} className="wp-button wp-button-primary inline-flex min-h-10 items-center gap-2 rounded-lg bg-amber-400 px-4 text-sm font-bold text-slate-950 hover:bg-amber-300 focus-visible:outline focus-visible:outline-2 focus-visible:outline-blue-600 disabled:cursor-not-allowed disabled:opacity-50"><Plus size={16}/> Create project</button></div>
      </header>}

      {sourceState === 'READY' && summary && !ownerOnly && !selectedId && mode === 'LIST' && (
        <details className="mb-3 border-b border-slate-200 pb-2" aria-label="Portfolio breakdown">
          <summary className="cursor-pointer py-2 text-xs font-semibold text-slate-700">
            Portfolio breakdown · {summary.total} projects
          </summary>
          <section className="wp-portfolio-chart" aria-label="Verified project status distribution">
          <div className="wp-chart-heading">
            <strong>Portfolio distribution</strong>
            <span>EOS verified · {summary.total} projects · Read-only status counts</span>
          </div>
          <div className="wp-chart-bars">
            {PROJECT_STATUSES.map((status) => (
              <div key={status} className="wp-chart-item" data-status={status}>
                <span className="wp-chart-value">{summary[status]}</span>
                <div className="wp-chart-track" role="img"
                  aria-label={`${statusLabel(status).replace(/^./, character => character.toUpperCase())}: ${summary[status]} of ${summary.total} projects`}>
                  <div className="wp-chart-fill" style={{ height: `${summary.total ? (100 * summary[status] / summary.total) : 0}%` }}/>
                </div>
                <span className="wp-chart-caption">{statusLabel(status)}</span>
              </div>
            ))}
          </div>
          </section>
        </details>
      )}
      {templateReconciliation && <div role="status"
        className="mb-3 flex flex-wrap items-center justify-between gap-2 border-b border-blue-200 px-2 py-2 text-sm text-slate-800">
        <span>{templateReconciliation.state === 'VERIFIED'
          ? 'Project and work verified in EOS: '
          : templateReconciliation.state === 'UNCONFIRMED'
            ? 'Save outcome not confirmed. Check this project in the list before trying again: '
            : 'Project and work saved. Current project details are being verified: '}
          <strong>{templateReconciliation.name}</strong></span>
        {templateReconciliation.state === 'UNCONFIRMED' ?
          <button type="button" className="wp-button" onClick={() => void refresh({ preserveSelection: false })}>
            Refresh matching projects
          </button> : templateReconciliation.state !== 'VERIFIED' &&
          <button type="button" className="wp-button" onClick={() => void (async () => {
            const response = await refresh({ preserveSelection: false });
            const row = response?.items.find(item => item.project_id === templateReconciliation.project_id);
            if (row) {
              const opened = await openProject(row.project_id);
              if (opened) setTemplateReconciliation(previous =>
                previous?.project_id === row.project_id ? { ...previous, state: 'VERIFIED' } : previous);
            }
          })()}>Verify project</button>}
      </div>}
      {sourceState === 'LOADING' && <div role="status" className="mb-3 rounded-lg border border-blue-200 bg-blue-50 p-3 text-sm text-blue-900"><LoaderCircle className="mr-2 inline animate-spin" size={15}/>Loading authorized Projects from EOS…</div>}
      {sourceState === 'DENIED' && <div role="alert" data-project-state="DENIED" className="mb-3 rounded-lg border border-rose-200 bg-rose-50 p-4 text-sm text-rose-900"><ShieldCheck className="mr-2 inline" size={16}/>{error === 'AUTHENTICATION_REQUIRED' ? 'Your session needs reauthentication before Projects can be read.' : error === 'PROJECTS_ENTITLEMENT_REQUIRED' ? 'An active Projects product entitlement is required for this tenant.' : 'EOS denied Projects access for this principal and selected tenant. No project records or counts are shown.'}</div>}
      {sourceState === 'UNAVAILABLE' && <div role="alert" data-project-state="UNAVAILABLE" className="mb-3 flex flex-wrap items-center justify-between gap-4 rounded-lg border border-amber-300 bg-amber-50 p-4 text-sm text-amber-950">
        <div className="flex min-w-0 items-start gap-3"><CircleAlert className="mt-0.5 shrink-0" size={21}/>
          <div><h2 className="font-bold">Projects couldn't load</h2>
            <p className="mt-1 text-sm">{error === 'AUTHENTICATED_TENANT_REQUIRED'
              ? 'Sign in to your organisation again to continue.'
              : 'WILSY OS is having trouble connecting to your projects. Your task has not been changed. Try again after the connection is restored.'}</p>
          </div>
        </div>
        <button type="button" onClick={() => void refresh()} className="min-h-11 shrink-0 rounded-lg border border-amber-500 bg-white px-4 py-2 font-bold text-amber-950 hover:bg-amber-100">Try again</button>
      </div>}
      {sourceState === 'STALE' && <div role="status" className="mb-3 rounded-lg border border-amber-300 bg-amber-50 p-3 text-sm text-amber-950">We couldn't refresh your projects. The items shown may be out of date. No task was changed. <button type="button" onClick={() => void refresh()} className="font-bold underline">Try again</button></div>}
      {sourceState === 'REFRESHING' && <div role="status" className="mb-3 text-xs text-slate-500">Refreshing from EOS…</div>}

      <div className="wp-body grid min-w-0 grid-cols-1 items-start gap-4"
        data-layout={selectedId && mode !== 'CREATE' ? 'detail' : 'list'}
        style={selectedId && mode !== 'CREATE'
          ? { display: 'block', width: '100%', height: 'auto', overflow: 'visible' }
          : undefined}>
        <section aria-label="Project list" className="wp-panel wp-list-panel min-w-0 overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm"
          style={selectedId && mode !== 'CREATE' ? { display: 'none' } : undefined}>
          {mode === 'TEMPLATE' ? <div className="p-4 sm:p-5" aria-label="Industry project templates">
            <div className="mb-4 flex flex-wrap items-center justify-between gap-2">
              <div><h2 className="text-lg font-bold text-slate-950">Start from a template</h2>
                <p className="text-xs text-slate-600">Choose an industry to create a real project with scheduled work</p></div>
              <button type="button" className="wp-button" onClick={() => setMode('CREATE')}
                disabled={commandState === 'PENDING'}>Back to blank project</button>
            </div>
            {templateState === 'LOADING' && <p role="status" className="text-sm text-slate-600">Verifying available templates…</p>}
            {templateState !== 'READY' && templateState !== 'LOADING' &&
              <div role="alert" className="flex flex-wrap items-center justify-between gap-3 rounded-lg border border-rose-200 bg-rose-50 p-3 text-sm text-rose-950">
                <div>
                  <p className="font-semibold">{templateError}</p>
                  <p className="mt-1 font-mono text-xs">Diagnostic: {templateFailureCode || 'TEMPLATE_SOURCE_UNAVAILABLE'}</p>
                  <p className="mt-1 text-xs">Source: GET /api/projects/templates. No template is selectable until EOS verifies this source.</p>
                </div>
                <button type="button" className="wp-button" disabled={!tenantId || !principalId}
                  onClick={() => setTemplateRetry(count => count + 1)}>Retry templates</button>
              </div>}
            {templateState === 'READY' && <>
              {templates.length < 17 && <p role="alert" className="mb-3 rounded-lg border border-amber-400 bg-amber-50 p-3 text-sm font-semibold text-amber-950">
                This EOS runtime returned {templates.length} legacy starter templates;
                the certified catalogue contains 17. Restart Python EOS from the
                same certified source as this frontend before validating templates.
              </p>}
              {selectedTemplate && !templatePickerOpen &&
                <div className="mb-3 flex flex-wrap items-center justify-between gap-2 border-b border-slate-200 pb-3">
                  <span className="text-sm font-semibold text-slate-900">
                    {selectedTemplate.industry} · {selectedTemplate.title}
                  </span>
                  <button type="button" className="wp-button"
                    onClick={() => setTemplatePickerOpen(true)}>Change template</button>
                </div>}
              <div className={templatePickerOpen ? 'grid gap-4 lg:grid-cols-[minmax(230px,0.9fr)_minmax(0,1.7fr)]' : 'block'}>
                {templatePickerOpen && <div role="listbox" aria-label="Verified industry templates" className="divide-y divide-slate-200 rounded-lg border border-slate-200">
                  {templates.map(item => <button key={item.slug} role="option"
                    aria-selected={selectedTemplateSlug === item.slug}
                    type="button" className="block w-full px-3 py-3 text-left hover:bg-blue-50 focus-visible:outline focus-visible:outline-blue-700"
                    style={selectedTemplateSlug === item.slug ? { background: '#e8f2ff' } : undefined}
                    onClick={() => { setSelectedTemplateSlug(item.slug);
                      setTemplateName(item.title); setTemplatePickerOpen(false); setTemplateError('');
                      setTemplateEditing(false); setTemplateOverrides({});
                      setAiProjectBrief(''); setAiUsageAcknowledged(false); setAiProjectState('IDLE'); setAiProjectError('');
                      aiDraftReplay.current = { fingerprint: '', key: null }; createReplay.current = { fingerprint: '', key: null }; }}>
                    <span className="block text-sm font-semibold text-slate-950">{item.industry}</span>
                    <span className="block text-xs text-slate-700">{item.title}</span>
                  </button>)}
                </div>}
                <div>
                  {!selectedTemplate && <p className="text-sm text-slate-600">Select an industry to inspect its milestones, dependencies, roles and acceptance evidence.</p>}
                  {selectedTemplate && <>
                    {templatePickerOpen && <h3 className="text-base font-bold text-slate-950">{selectedTemplate.title}</h3>}
                    <p className="mt-1 text-xs text-slate-600">Template revision {selectedTemplate.revision} · {selectedTemplate.steps.length} source-defined work items</p>
                    <section className="mt-3 rounded-lg border border-slate-200 bg-slate-50 p-3"
                      aria-label="WILSY AI project planning">
                      <h4 className="text-sm font-bold text-slate-950">Plan with WILSY AI</h4>
                      <p className="mt-1 text-xs text-slate-700">
                        Optional governed AI assistance. Your description is sent only when you request a draft.
                        Review every proposed work item before authorizing EOS activation.
                      </p>
                      <label className="mt-2 block text-xs font-semibold text-slate-800">
                        Describe the project objective, deliverables and risks
                        <textarea aria-label="WILSY AI project brief" rows={3} maxLength={3000}
                          value={aiProjectBrief} onChange={event => {
                            setAiProjectBrief(event.target.value);
                            setAiProjectState('IDLE'); setAiProjectError('');
                            aiDraftReplay.current = { fingerprint: '', key: null };
                          }} className="mt-1 w-full rounded-lg border border-slate-300 bg-white p-2 text-sm font-normal text-slate-950"/>
                      </label>
                      <label className="mt-3 flex items-start gap-2 text-xs text-slate-800">
                        <input type="checkbox" className="mt-0.5 size-4" checked={aiUsageAcknowledged}
                          onChange={event => setAiUsageAcknowledged(event.target.checked)}/>
                        <span>I choose to request WILSY AI reasoning using my tenant's subscribed
                          AI service and available usage allowance. This request may consume
                          paid AI capacity; EOS will reject it without valid entitlement and admission.
                          No project is created by this request.</span>
                      </label>
                      <button type="button" className="wp-button mt-2"
                        disabled={aiProjectState === 'PENDING' || aiProjectBrief.trim().length < 20 || !aiUsageAcknowledged}
                        onClick={() => void askWilsyAiForTemplateDraft()}>
                        {aiProjectState === 'PENDING' ? 'WILSY AI drafting…' : 'Generate a reviewable AI plan'}
                      </button>
                      {aiProjectError && <p role="alert" className="mt-2 text-xs text-rose-800">{aiProjectError}</p>}
                      {aiProjectState === 'READY' && <p role="status" className="mt-2 text-xs font-semibold text-emerald-800">
                        AI proposal staged for review. Nothing has been saved or assigned.
                      </p>}
                    </section>
                    <div className="mt-3 flex flex-wrap items-center justify-between gap-2">
                      <p className="text-xs text-slate-700">Edit your project draft; platform starter, roles and dependencies stay unchanged.</p>
                      <button type="button" className="wp-button" aria-pressed={templateEditing}
                        onClick={() => setTemplateEditing(value => !value)}>
                        {templateEditing ? 'Review work plan' : 'Customize included work'}
                      </button>
                    </div>
                    <div className="mt-3 overflow-x-auto" aria-label="Selected template work items">
                      <table className="w-full text-left text-xs">
                        <thead className="border-b border-slate-200 text-slate-700"><tr><th className="p-2">Deliverable</th><th className="p-2">Role</th><th className="p-2">Due</th><th className="p-2">Depends on</th></tr></thead>
                        <tbody>{selectedTemplate.steps.map(step => <tr className="border-b border-slate-100" key={step.id}>
                          <td className="p-2">
                            {templateEditing ? <div className="grid gap-2">
                              <label className="block text-xs font-semibold">Work title
                                <input aria-label={'Work title for ' + step.id} maxLength={180}
                                  value={templateOverrides[step.id]?.title ?? step.title}
                                  onChange={event => { const title = event.target.value;
                                    setTemplateOverrides(previous => ({
                                      ...previous, [step.id]: { title, day: previous[step.id]?.day ?? step.day,
                                        acceptance: previous[step.id]?.acceptance ?? step.acceptance },
                                    })); createReplay.current = { fingerprint: '', key: null }; }}
                                  className="mt-1 w-full rounded-md border border-slate-300 bg-white p-2 text-sm text-slate-950"/>
                              </label>
                              <label className="block text-xs font-semibold">Acceptance evidence
                                <textarea aria-label={'Acceptance evidence for ' + step.id} rows={2} maxLength={1000}
                                  value={templateOverrides[step.id]?.acceptance ?? step.acceptance}
                                  onChange={event => { const acceptance = event.target.value;
                                    setTemplateOverrides(previous => ({
                                      ...previous, [step.id]: { acceptance, title: previous[step.id]?.title ?? step.title,
                                        day: previous[step.id]?.day ?? step.day },
                                    })); createReplay.current = { fingerprint: '', key: null }; }}
                                  className="mt-1 w-full rounded-md border border-slate-300 bg-white p-2 text-sm text-slate-950"/>
                              </label>
                            </div> : <><strong className="block text-slate-900">{templateOverrides[step.id]?.title ?? step.title}</strong>
                              <span className="text-slate-600">{step.kind} · {templateOverrides[step.id]?.acceptance ?? step.acceptance}</span></>}
                          </td>
                          <td className="p-2 text-slate-700">{step.role.replaceAll('_', ' ')}</td>
                          <td className="p-2 text-slate-700">
                            {templateEditing ? <label className="block text-xs font-semibold">Days from start
                              <input type="number" min={0} max={3650} step={1}
                                aria-label={'Day offset for ' + step.id}
                                value={templateOverrides[step.id]?.day ?? step.day}
                                onChange={event => { const day = event.target.value === '' ? '' : Number(event.target.value);
                                  setTemplateOverrides(previous => ({
                                    ...previous, [step.id]: { day, title: previous[step.id]?.title ?? step.title,
                                      acceptance: previous[step.id]?.acceptance ?? step.acceptance },
                                  })); createReplay.current = { fingerprint: '', key: null }; }}
                                className="mt-1 w-20 rounded-md border border-slate-300 bg-white p-2 text-sm text-slate-950"/>
                            </label> : 'Day +' + (templateOverrides[step.id]?.day ?? step.day)}
                          </td>
                          <td className="p-2 text-slate-700">{step.depends_on.join(', ') || 'None'}</td>
                        </tr>)}</tbody>
                      </table>
                    </div>
                    <form onSubmit={activateTemplate} className="mt-4 space-y-3 border-t border-slate-200 pt-4">
                      <label className="block text-sm font-semibold" style={{ color: '#172b4d' }}>Project name
                        <input required maxLength={180} style={{ color: '#172b4d', backgroundColor: '#fff', letterSpacing: 'normal', fontWeight: 400 }} className="mt-1 block w-full rounded-lg border border-slate-300 px-3 py-2"
                          value={templateName} onChange={event => { createReplay.current = { fingerprint: '', key: null }; setTemplateName(event.target.value); }}/>
                      </label>
                      <ProjectDateField label="Start date" value={templateStart} disabled={commandState === 'PENDING'}
                        onChange={value => { createReplay.current = { fingerprint: '', key: null }; setTemplateStart(value); }}/>
                      {templateError && <p role="alert" className="text-sm text-rose-700">{templateError}</p>}
                      {commandError && <div role="alert" className="space-y-2 border-l-2 border-amber-600 pl-3 text-sm text-slate-800">
                        <p>The activation outcome is not verified. A request can commit in EOS even if its response fails or a subsequent read times out. Check the authorized Projects list before issuing another create command.</p>
                        <button type="button" className="wp-button" onClick={() => {
                          setQuery(templateName.trim());
                          setMode('LIST');
                          void refresh({ preserveSelection: false });
                        }}>Check Projects list</button>
                      </div>}
                      <button type="submit" disabled={commandState === 'PENDING'}
                        className="wp-button wp-button-primary">
                        {commandState === 'PENDING' ? 'Activating in EOS…' : 'Create project and work in EOS'}
                      </button>
                      <p className="text-xs text-slate-600">Creates a PLANNED project with unassigned work; no employment, IAM, project ownership or spending authority is granted.</p>
                    </form>
                  </>}
                </div>
              </div>
            </>}
          </div> : mode === 'CREATE' ? (
            <form onSubmit={submitCreate} className="wp-form space-y-4 p-4 sm:p-5" aria-labelledby="project-create-title">
              <div className="flex items-start justify-between gap-3"><div><h2 id="project-create-title" className="text-lg font-bold text-slate-900">Create project</h2><p className="mt-1 text-sm text-slate-600">EOS validates authority and confirms the persisted project before it appears in the list.</p></div><button type="button" aria-label="Cancel project creation" onClick={() => { setMode('LIST'); setCommandError(''); }} disabled={commandState === 'PENDING'} className="wp-close rounded-md p-2 text-slate-600 hover:bg-slate-100"><X size={18}/></button></div>
              <button type="button" className="wp-button" onClick={() => setMode('TEMPLATE')}>
                Browse industry templates
              </button>
              <label className="block text-sm font-semibold text-slate-800">Project name<input required maxLength={180} value={draft.name} onChange={(event) => (createReplay.current = { fingerprint: '', key: null }, setDraft({ ...draft, name: event.target.value }))} aria-invalid={commandError === 'PROJECT_NAME_REQUIRED' || commandError === 'PROJECT_INPUT_INVALID'} className="mt-1 block min-h-11 w-full rounded-lg border border-slate-300 px-3 font-normal focus:border-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-100"/>{commandError === 'PROJECT_NAME_REQUIRED' && <span className="mt-1 block text-xs font-normal text-rose-700">Enter a project name.</span>}{commandError === 'PROJECT_INPUT_INVALID' && <span className="mt-1 block text-xs font-normal text-rose-700">Check the project name and date fields. Your draft is preserved.</span>}</label>
              <p className="wp-code-hint" role="note">Project code: assigned automatically by Python EOS when the project is created. No manual code is required.</p>
              <label className="block text-sm font-semibold text-slate-800">Summary <span className="font-normal text-slate-500">(optional)</span><textarea maxLength={4000} rows={3} value={draft.summary} onChange={(event) => (createReplay.current = { fingerprint: '', key: null }, setDraft({ ...draft, summary: event.target.value }))} className="mt-1 block w-full rounded-lg border border-slate-300 px-3 py-2 font-normal focus:border-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-100"/></label>
              <div className="wp-form-grid">
                <ProjectDateField label="Start" value={draft.start_date} disabled={commandState === 'PENDING'}
                  onChange={value => { createReplay.current = { fingerprint: '', key: null }; setDraft(current => ({ ...current, start_date: value })); }}/>
                <ProjectDateField label="Target" value={draft.target_date} disabled={commandState === 'PENDING'}
                  onChange={value => { createReplay.current = { fingerprint: '', key: null }; setDraft(current => ({ ...current, target_date: value })); }}/>
              </div>
              {commandError && !['PROJECT_NAME_REQUIRED', 'PROJECT_INPUT_INVALID'].includes(commandError) && <p role="alert" className="rounded-md border border-rose-200 bg-rose-50 p-3 text-sm text-rose-800">{commandError === 'ACCESS_DENIED' ? 'EOS denied this project command. Your draft remains available.' : commandError === 'PROJECTS_ENTITLEMENT_REQUIRED' ? 'This tenant has no active Projects entitlement. Your draft remains available.' : commandError === 'PROJECT_REVISION_OR_REPLAY_CONFLICT' ? 'The source reported a conflict. Refresh before retrying.' : 'EOS could not confirm this command. Your draft remains available; retry after checking the source.'}</p>}
              <div className="flex flex-wrap justify-end gap-2 border-t border-slate-200 pt-3"><button type="button" onClick={() => { setMode('LIST'); setCommandError(''); }} disabled={commandState === 'PENDING'} className="min-h-10 rounded-lg border border-slate-300 px-4 text-sm font-semibold text-slate-700 disabled:opacity-50">Cancel</button><button type="submit" disabled={commandState === 'PENDING'} className="wp-button wp-button-primary min-h-10 rounded-lg bg-amber-400 px-4 text-sm font-bold text-slate-950 disabled:opacity-60">{commandState === 'PENDING' ? 'Saving…' : 'Save project to EOS'}</button></div>
            </form>
          ) : <>
            <div className="wp-list-controls flex flex-wrap items-center gap-2 border-b border-slate-200 p-3"><label className="wp-search relative min-w-[180px] flex-1"><Search size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500"/><span className="sr-only">Search projects</span><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search projects" className="min-h-10 w-full rounded-lg border border-slate-300 pl-9 pr-3 text-sm"/></label><label className="sr-only" htmlFor="project-status-filter">Filter by status</label><select id="project-status-filter" value={statusFilter} onChange={(event) => changeStatusFilter(event.target.value)} className="wp-filter min-h-10 rounded-lg border border-slate-300 bg-white px-3 text-sm"><option value="all">All statuses</option>{PROJECT_STATUSES.map((value) => <option key={value} value={value}>{statusLabel(value)}</option>)}</select></div>
            {sourceState === 'READY' && items.length === 0
              && templateReconciliation?.state !== 'READBACK_PENDING'
              ? <div className="p-8 text-center"><Code2 className="mx-auto text-slate-400" size={28}/><h2 className="mt-3 font-semibold text-slate-900">No projects in this tenant</h2><p className="mt-1 text-sm text-slate-600">EOS returned a verified empty Projects list.</p></div> : sourceState === 'READY' && visibleItems.length === 0
              && templateReconciliation?.state !== 'READBACK_PENDING'
              ? <p className="p-6 text-center text-sm text-slate-600">{ownerOnly ? 'No EOS-verified projects are owned by your current principal on this page.' : 'No projects match the current search and status filter.'}</p> : templateReconciliation?.state === 'READBACK_PENDING' && visibleItems.length === 0
              ? <p role="status" className="p-4 text-sm text-slate-700">
                  A committed project is awaiting refreshed list visibility. No empty result is inferred.
                </p> : <div className="wp-table-shell" role="region" aria-label="Projects table" tabIndex={0}>
              <div className="wp-table-head" aria-hidden="true">
                <span>Project</span><span>Project code</span><span>Status</span><span>Target date</span><span>Action</span>
              </div>
              <ul className="divide-y divide-slate-200" aria-label="Projects returned by EOS">
                {visibleItems.map((item) => <li key={item.project_id}>
                  <button type="button" aria-current={selectedId === item.project_id ? 'true' : undefined}
                    data-selected={selectedId === item.project_id}
                    onClick={() => void openProject(item.project_id)}
                    className="wp-table-row focus-visible:outline focus-visible:outline-2 focus-visible:outline-inset focus-visible:outline-blue-600"
                    aria-label={`View project ${item.name}, ${statusLabel(item.status)}`}>
                    <span><strong className="wp-row-title">{item.name}</strong></span>
                    <span className="text-sm text-slate-700">{item.code && !/^PRJ-[0-9A-F]{16}$/.test(item.code) ? item.code : 'Automatically assigned'}</span>
                    <span><span className="wp-status" data-status={item.status}>{statusLabel(item.status)}</span></span>
                    <span className="text-sm text-slate-700">{item.target_date || 'No target date'}</span>
                    <span className="wp-table-action">View details</span>
                  </button>
                </li>)}
              </ul>
            </div>}
            <footer className="wp-footer border-t border-slate-200 px-4 py-2 text-xs text-slate-500">
              <span>{sourceState === 'READY' ? `${visibleItems.length} shown · ${items.length} verified${ownerOnly ? " · EOS owner-filtered page" : ""}` : 'Projects could not be loaded'}</span>
              {sourceState === 'READY' && (pageOffset > 0 || hasNextPage) && (
                <nav className="wp-pagination" aria-label="Project pages">
                  <span>Page {Math.floor(pageOffset / 100) + 1} · Search applies to this page</span>
                  <button type="button" className="wp-button" disabled={pageOffset === 0}
                    onClick={() => changePage(Math.max(0, pageOffset - 100))}>Previous</button>
                  <button type="button" className="wp-button" disabled={!hasNextPage}
                    onClick={() => changePage(pageOffset + 100)}>Next</button>
                </nav>
              )}
            </footer>
          </>}
        </section>

        {selectedId && mode !== 'CREATE' && <section aria-label="Project detail" aria-busy={detailState === 'LOADING'}
          className="wp-panel wp-detail min-w-0 rounded-xl border border-slate-200 bg-white p-3 shadow-sm sm:p-4"
          style={{ width: '100%', height: 'auto', maxHeight: 'none', overflow: 'visible' }}>
          <div className="wp-detail-top mb-1 flex flex-wrap items-center justify-between gap-2">
            <div className="flex min-w-0 flex-1 flex-wrap items-center gap-x-3 gap-y-1">
              <button type="button" onClick={closeDetail}
                className="wp-button !min-h-9 !px-3 !text-xs" aria-label="Back to projects table">
                <X size={15}/> Back to all projects
              </button>
              <p className="sr-only">Projects &amp; delivery / Current project</p>
              <h2 className="wp-detail-title !text-xl !leading-tight">{detail?.project?.name || 'Loading project…'}</h2>
              {detail?.project && <div className="flex flex-wrap items-center gap-2 text-xs text-slate-700">
                <span className="wp-status" data-status={detail.project.status}>
                  {statusLabel(detail.project.status)}
                </span>
                <span className="font-semibold">{detail.project.code && !/^PRJ-[0-9A-F]{16}$/.test(detail.project.code) ? detail.project.code : 'Code assigned'}</span>
                <span className="sr-only">Revision {detail.project.revision}</span>
                <span>Target {detail.project.target_date || 'not scheduled'}</span>
              </div>}
            </div>
            <button type="button" onClick={() => void openProject(selectedId)}
              disabled={detailState === 'LOADING'} className="wp-button !min-h-9 !px-3 !text-xs">
              <RefreshCw size={15}/> Refresh project
            </button>
          </div>
          <nav className="mb-1 flex min-w-0 gap-1 overflow-x-auto border-b border-slate-200 pb-1"
            aria-label="Project workspace views">
            {[
              ['work', 'Work & milestones'],
              ['discussions', 'Activity & discussion'],
              ['overview', 'Overview'],
              ['people', 'People'],
              ['notes', 'Notes'],
              ['settings', 'Manage project'],
              ['history', 'Audit history'],
            ].map(([value, label]) =>
              <button key={value} type="button"
                aria-current={projectView === value ? 'page' : undefined}
                onClick={() => setProjectView(value)}
                className="wp-button !min-h-9 !shrink-0 !px-3 !text-xs"
                style={projectView === value
                  ? { background: '#e8f2ff', borderColor: '#2b67ad', color: '#163f76' }
                  : undefined}>
                {label}
              </button>)}
          </nav>
          {detailState === 'LOADING' && <p role="status" className="text-sm text-slate-600">Loading project and audit events…</p>}
          {detailState === 'ERROR' && <p role="alert" className="text-sm text-rose-700">{commandError === 'ACCESS_DENIED' ? 'EOS denied this project detail read.' : 'Project detail is unavailable. Retry the read.'}<button type="button" onClick={() => void openProject(selectedId)} className="ml-2 font-semibold underline">Retry</button></p>}
          {detailState === 'READY' && detail && <div className="wp-detail-inner">
            {projectView === 'overview' && <div className="max-w-5xl">
            <h3 className="mb-3 text-lg font-bold text-slate-900">Project overview</h3>
            <dl className="wp-facts mb-4 grid grid-cols-[110px_minmax(0,1fr)] gap-x-3 gap-y-2 border-b border-slate-200 pb-4 text-sm"><dt className="text-slate-500">Code</dt><dd className="break-words text-slate-900">
              {detail.project.code && !/^PRJ-[0-9A-F]{16}$/.test(detail.project.code)
                ? detail.project.code : 'Automatically assigned'}
              {!detail.project.code && <button type="button"
                className="wp-code-action"
                onClick={() => void assignGeneratedCode()}
                disabled={commandState === 'PENDING' || sourceState !== 'READY'}
              >Generate and save code</button>}
            </dd><dt className="text-slate-500">Status</dt><dd className="capitalize text-slate-900">{statusLabel(detail.project.status)}</dd><dt className="text-slate-500">Owner</dt><dd className="text-slate-900">
              {personLabel(detail.project.owner_principal_id)}
              {detail.project.owner_principal_id && <small className="ml-2 inline-block rounded-md border border-slate-300 bg-slate-100 px-2 py-0.5 text-xs font-semibold text-slate-800">Verified owner</small>}
            </dd><dt className="text-slate-500">Created by</dt><dd className="text-slate-900">
              {personLabel(detail.project.created_by_principal_id)}
              <small className="ml-2 inline-block rounded-md border border-slate-300 bg-slate-100 px-2 py-0.5 text-xs font-semibold text-slate-800">Audited creator</small>
            </dd><dt className="text-slate-600">Department</dt><dd className="text-slate-900">{detail.project.department_id
              ? overviewDepartment.id === detail.project.department_id && overviewDepartment.status === 'READY'
                ? overviewDepartment.name
                : overviewDepartment.status === 'VERIFYING' ? 'Verifying assigned department…'
                  : 'Assigned department · name unavailable'
              : 'Not assigned'}</dd><dt className="text-slate-500">Target date</dt><dd className="text-slate-900">{detail.project.target_date || 'Not scheduled'}</dd></dl><p className="wp-record-note">These values come from the current EOS project record. Owner and department are recorded only after EOS verifies independent assignment authority and source-backed eligibility.</p>
            </div>}
            {projectView === 'settings' && <div className="max-w-5xl">
            <h3 className="mb-3 text-lg font-bold text-slate-900">Project governance &amp; configuration</h3>
            <ProjectAccountabilityPanel key={detail.project.project_id} project={detail.project} tenantId={tenantId}
              principalId={principalId} tenantHeaders={tenantHeaders} runCommand={runCommand}
              refresh={refresh} openProject={openProject}/>
            </div>}
            {projectView === 'overview' && detail.project.summary && <ProjectSummary value={detail.project.summary} expanded={summaryExpanded} onToggle={() => setSummaryExpanded((value) => !value)}/>}
            {projectView === 'people' && <ProjectParticipantsPanel key={'participants:' + detail.project.project_id + ':' + sessionScope}
              projectId={detail.project.project_id} tenantId={tenantId}
              principalId={principalId} tenantHeaders={tenantHeaders}/>}
            {projectView === 'work' && <ProjectTasksPanel key={'work:' + detail.project.project_id + ':' + sessionScope}
              projectId={detail.project.project_id} tenantId={tenantId}
              principalId={principalId} tenantHeaders={tenantHeaders}
              focusTaskId={focusProjectId === detail.project.project_id ? focusTaskId : null}
              onFocusedTaskChange={handleFocusedTaskChange}
              onOpenProjectPeople={() => setProjectView('people')}/>}
            {projectView === 'discussions' && <ProjectTasksPanel
              key={'discussions:' + detail.project.project_id + ':' + sessionScope}
              projectId={detail.project.project_id} tenantId={tenantId}
              principalId={principalId} tenantHeaders={tenantHeaders} discussionOnly
              onFocusedTaskChange={handleFocusedTaskChange}
              onOpenProjectPeople={() => setProjectView('people')}/>}
            {projectView === 'notes' && <ProjectNotesPanel key={detail.project.project_id + ':' + sessionScope} projectId={detail.project.project_id}
              tenantId={tenantId} principalId={principalId} tenantHeaders={tenantHeaders}/>}
            {projectView === 'settings' && <div className="max-w-5xl">
            <form onSubmit={submitUpdate} className="wp-form space-y-3 border-t border-slate-200 pt-4"><h3 className="font-semibold text-slate-900">Update project</h3><label className="block text-xs font-semibold text-slate-700">Name<input value={edit?.name || ''} onChange={(event) => setEdit({ ...edit, name: event.target.value })} maxLength={180} className="mt-1 min-h-10 w-full rounded-md border border-slate-300 px-3 text-sm font-normal"/></label><div className="text-sm text-slate-700">
                <span className="block text-xs font-semibold">Project code · immutable</span>
                <span>{detail.project.code && !/^PRJ-[0-9A-F]{16}$/.test(detail.project.code)
                  ? detail.project.code : 'Automatically assigned'}</span>
              </div><label className="block text-xs font-semibold text-slate-700">Summary<textarea rows={2} value={edit?.summary || ''} onChange={(event) => setEdit({ ...edit, summary: event.target.value })} maxLength={4000} className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2 text-sm font-normal"/></label><div className="wp-form-grid">
                <div className="text-sm text-slate-700">
                  <span className="block text-xs font-semibold">Original start date · immutable</span>
                  <span>{detail.project.start_date || 'Not recorded'}</span>
                </div>
                <ProjectDateField label="Target" value={edit?.target_date || ''} disabled={commandState === 'PENDING'}
                  onChange={value => setEdit(current => ({ ...current, target_date: value }))}/>
              </div>
              {(edit?.target_date || null) !== (detail.project.target_date || null)
                && detail.project.target_date && <label className="block text-sm font-semibold text-slate-800">
                  Reason for changing the original target date
                  <textarea required minLength={12} maxLength={1000} rows={3}
                    aria-label="Target date change reason" value={targetChangeReason}
                    onChange={event => setTargetChangeReason(event.target.value)}
                    placeholder="Record delays, risks and planned recovery actions."
                    className="mt-1 w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm font-normal text-slate-950"/>
                  <small className="mt-1 block font-normal text-slate-600">
                    This rationale is bound to the immutable EOS project revision and audit.
                  </small>
                </label>}
              <button type="submit" disabled={commandState === 'PENDING'} className="wp-button min-h-10 w-full rounded-lg border border-blue-700 px-3 text-sm font-semibold text-blue-800 hover:bg-blue-50 disabled:opacity-50">{commandState === 'PENDING' ? 'Saving…' : 'Save revision'}</button></form>
            <div className="wp-actions mt-3 grid grid-cols-1 gap-2 sm:grid-cols-[minmax(0,1fr)_auto]"><label className="sr-only" htmlFor="project-status">Project status</label><select id="project-status" value={detail.project.status} disabled={commandState === 'PENDING'} onChange={(event) => void transitionStatus(event.target.value)} className="min-h-10 rounded-lg border border-slate-300 bg-white px-3 text-sm capitalize">{PROJECT_STATUSES.map((value) => <option key={value} value={value} disabled={value === 'active' && (!detail.project.owner_principal_id || !detail.project.department_id)}>{statusLabel(value)}</option>)}</select><button type="button" disabled={commandState === 'PENDING' || Boolean(detail.project.archived_at)} onClick={() => void archiveProject()} className="wp-button wp-button-danger inline-flex min-h-10 items-center justify-center gap-2 rounded-lg border border-rose-300 px-3 text-sm font-semibold text-rose-800 hover:bg-rose-50 disabled:opacity-50"><Archive size={14}/> Archive</button></div>
            {(!detail.project.owner_principal_id || !detail.project.department_id) && detail.project.status === 'planned' && <p role="status" className="mt-2 text-xs text-amber-900">Activation requires a verified project owner and tenant department. The project remains Planned until EOS confirms both.</p>}
            {commandError && <p role="alert" className="mt-3 rounded-md border border-rose-200 bg-rose-50 p-3 text-sm text-rose-800">{commandError === 'ACCESS_DENIED' ? 'EOS denied this command; project state has not been changed.' : commandError === 'PROJECTS_ENTITLEMENT_REQUIRED' ? 'An active Projects entitlement is required.' : commandError === 'PROJECT_REVISION_OR_REPLAY_CONFLICT' ? 'The project revision changed. Refresh the source before retrying.' : commandError === 'PROJECT_TARGET_CHANGE_REASON_REQUIRED' ? 'Explain the target date change in at least 12 characters before saving.' : commandError === 'PROJECT_INPUT_INVALID' ? 'EOS rejected the supplied fields. Check the network response detail, including validation paths.' : /^PROJECT_[A-Z0-9_]{1,90}$/.test(commandError) ? 'EOS response: ' + commandError + '. No success has been inferred.' : 'EOS did not confirm the command. The source state is retained; refresh before retrying.'}</p>}
            {commandState === 'CONFIRMED' && <p role="status" className="mt-3 text-sm font-medium text-emerald-800">EOS confirmed the project change and returned persisted state.</p>}
            </div>}
            {projectView === 'history' && <section className="wp-section mt-5 border-t border-slate-200 pt-4" aria-label="Project audit timeline">
              <div className="flex flex-wrap items-end justify-between gap-3">
                <div>
                  <h3 className="text-lg font-semibold text-slate-900">Audit events</h3>
                  <p className="mt-1 text-sm text-slate-600">EOS-verified project revisions, newest first. This view does not edit immutable audit evidence.</p>
                </div>
                <span className="rounded-lg border border-blue-200 bg-blue-50 px-3 py-2 text-xs font-semibold text-blue-950">
                  {detail.events.length} verified events · Latest revision {detail.events.length ? Math.max(...detail.events.map(event => event.revision)) : '—'}
                </span>
              </div>
              {detail.events.length ? <ol className="mt-5 space-y-0" aria-label="Newest first project audit events">
                {[...detail.events].sort((a, b) => b.revision - a.revision
                  || Date.parse(b.occurred_at) - Date.parse(a.occurred_at)
                  || a.event_id.localeCompare(b.event_id)).map((event, index) => {
                  const statusChange = event.event_type === 'PROJECT_STATUS_TRANSITION';
                  const created = event.event_type === 'PROJECT_CREATED';
                  const archived = event.event_type === 'PROJECT_ARCHIVED';
                  const tone = archived ? 'border-rose-500 bg-rose-50 text-rose-950'
                    : statusChange ? 'border-blue-500 bg-blue-50 text-blue-950'
                      : created ? 'border-emerald-500 bg-emerald-50 text-emerald-950'
                        : 'border-amber-500 bg-amber-50 text-amber-950';
                  return <li key={event.event_id} className="relative flex gap-4 pb-4">
                    <div className="relative flex w-7 shrink-0 justify-center">
                      {index < detail.events.length - 1 && <span aria-hidden="true" className="absolute bottom-[-1rem] top-7 w-px bg-slate-300"/>}
                      <span aria-hidden="true" className={'relative z-10 mt-4 size-3 rounded-full border-2 ' + (archived ? 'border-rose-600 bg-rose-100'
                        : statusChange ? 'border-blue-700 bg-blue-100'
                          : created ? 'border-emerald-700 bg-emerald-100'
                            : 'border-amber-700 bg-amber-100')}/>
                    </div>
                    <div className={'wp-event min-w-0 flex-1 rounded-xl border-l-4 p-4 shadow-sm ' + tone}
                      data-audit-revision={event.revision}>
                      <div className="flex flex-wrap items-start justify-between gap-2">
                        <div className="min-w-0">
                          <strong className="block break-words text-sm">{event.event_type}</strong>
                          <span className="mt-1 block text-xs opacity-80">{event.event_type.replaceAll('_', ' ').toLowerCase()}</span>
                          <span className="mt-1 block text-xs font-semibold">Revision {event.revision}{index === 0 ? ' · Latest returned event' : ''}</span>
                        </div>
                        <time className="text-xs font-medium" dateTime={event.occurred_at}>{new Date(event.occurred_at).toLocaleString()}</time>
                      </div>
                      <div className="mt-3 border-t border-current/15 pt-2 text-sm">By {personLabel(event.actor_principal_id)} · revision {event.revision}</div>
                      {typeof event.target_change_reason === 'string'
                        && event.target_change_reason.trim() && <div className="mt-2 rounded-lg border border-current/20 bg-white/70 p-3 text-sm">
                          <strong className="block text-slate-900">Reason for revised target date</strong>
                          <p className="mt-1 whitespace-pre-wrap break-words text-slate-800">{event.target_change_reason}</p>
                        </div>}
                      <div className="mt-1 text-xs opacity-80">Immutable actor evidence retained securely by EOS</div>
                    </div>
                  </li>;
                })}
              </ol> : <p className="mt-4 text-sm text-slate-600">No audit event was returned by EOS.</p>}
            </section>}
          </div>}
        </section>}
      </div>
    </section>
  );
}

// ARTIFACT: ProjectsWorkspace.jsx
// VERSION: v2.43.0-ONE-NETWORK-MOUNT-PER-SCOPE
// AUTHORITY BOUNDARY: authenticated EOS requests and returned source state only; no local project truth
// TENANT POSTURE: scope changes invalidate late responses and EOS validates the active session tenant
// FAIL-CLOSED POSTURE: denial, missing entitlement, unavailable source, conflict, invalid readback and stale state remain distinct
// FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
// END OF WILSY OS SOVEREIGN ARTIFACT
