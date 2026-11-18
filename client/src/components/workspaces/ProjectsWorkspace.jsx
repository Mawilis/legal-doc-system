/**
 * TITLE: WILSY OS Authenticated Projects Workspace
 * VERSION: v2.14.0-INDEXED-OWNER-RESPONSIBILITY-PAGES
 * AUTHORITY: Python EOS Projects API and existing authenticated api.js transport.
 * EPITOME: Presents source-backed project list, create, detail, update, status,
 *          archive and immutable event evidence without creating local truth.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/components/workspaces/ProjectsWorkspace.jsx
 * COLLABORATION / OWNERSHIP: Projects domain and registry own business truth;
 *                            EOS owns admission; Headquarters owns navigation.
 * CERTIFICATION / UPDATE DATE: 2026-11-17.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
 * SECURITY / PRIVACY POSTURE: No token or permission claims are read here;
 *                             the existing api.js owns authenticated transport.
 * TENANT BOUNDARY: Tenant selector is an EOS transport hint only; EOS requires
 *                  equality with authenticated session scope and tenant-scopes persistence.
 * AUTHORITY BOUNDARY: UI affordances are requests; EOS reauthorizes each route
 *                     and returns committed project/event state.
 * FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
 * CHANGELOG: v2.14.0-INDEXED-OWNER-RESPONSIBILITY-PAGES uses source-filtered exact-owner pages before pagination, replacing incomplete current-page-only owner selection. Verifies every returned owner identity and preserves participant IAM separation.
 * CHANGELOG: v2.14.0-INDEXED-OWNER-RESPONSIBILITY-PAGES separates currently authorized owner responsibility from independently permitted participant assignments. My owned projects filters verified EOS owner identities on the current page; explicit participant access keeps its existing route and IAM with no founder fallback.
 * CHANGELOG: v2.14.0-INDEXED-OWNER-RESPONSIBILITY-PAGES restores meaningful bounded server validation and conflict details for assignment, prevents recreating a canonical existing department and reloads exact source when uncertainty occurs.
 * CHANGELOG: v2.14.0-INDEXED-OWNER-RESPONSIBILITY-PAGES surfaces exact-tenant EOS verified project creator, owner and audit actor names in Overview and History; immutable opaque IDs remain available as technical identifiers without replacing human labels.
 * CHANGELOG: v2.14.0-INDEXED-OWNER-RESPONSIBILITY-PAGES renders verified first/last names from the canonical exact-tenant EOS owner directory, retaining principal IDs strictly as selection values; missing names show an explicit unlabelled identity instead of guessed user data.
 * CHANGELOG: v2.14.0-INDEXED-OWNER-RESPONSIBILITY-PAGES replaces the clipped fixed-height list/detail split with a full-width, task-first selected project workspace. Separates Work, Overview, People, Notes, Manage and Audit without changing EOS authority or the unselected registry.
 * CHANGELOG: v2.14.0-INDEXED-OWNER-RESPONSIBILITY-PAGES opens
 *            current participant project execution directly from an
 *            EOS-authorized Daily Attention project handoff; owner source
 *            reads are not used as participant admission.
 * CHANGELOG: v2.14.0-INDEXED-OWNER-RESPONSIBILITY-PAGES opens the
 *            separately authorized participant Projects destination, without
 *            claiming owner privileges or weakening owner list admission.
 * CHANGELOG: v2.14.0-INDEXED-OWNER-RESPONSIBILITY-PAGES mounts exact-tenant,
 *            EOS-sourced candidate selection and audited participant
 *            grant/revoke alongside task execution in selected project detail.
 * CHANGELOG: v2.14.0-INDEXED-OWNER-RESPONSIBILITY-PAGES mounts the independently source-backed
 *            task/subtask/milestone table and lifecycle editor inside the
 *            selected exact-tenant project detail without local work truth.
 * CHANGELOG: v2.14.0-INDEXED-OWNER-RESPONSIBILITY-PAGES mounts independently source-backed note
 *            list and author-only edit/archive inside selected project detail;
 *            no project lifecycle state or IAM authority is changed.
 * CHANGELOG: v2.14.0-INDEXED-OWNER-RESPONSIBILITY-PAGES applies status filtering at the exact-tenant
 *            EOS API before paging instead of filtering only the visible page;
 *            status changes reset pagination and preserve all authorization.
 * CHANGELOG: v2.14.0-INDEXED-OWNER-RESPONSIBILITY-PAGES consumes EOS verified has_more/next_offset page
 *            evidence, retaining legacy mock compatibility and denying malformed
 *            new metadata without claiming nonexistent pages.
 *            v2.14.0-INDEXED-OWNER-RESPONSIBILITY-PAGES exposes readable title-case
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
    <span>{label}</span>
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

export default function ProjectsWorkspace({ tenantId = null, principalId = null, sessionScope = '', focusProjectId = null, focusAssignedProjectId = null }) {
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
  const [projectView, setProjectView] = useState('work');
  const [summaryExpanded, setSummaryExpanded] = useState(false);
  const [detail, setDetail] = useState(null);
  const [detailState, setDetailState] = useState('IDLE');
  const [mode, setMode] = useState('LIST');
  const [showAssignedProjects, setShowAssignedProjects] = useState(
    Boolean(focusAssignedProjectId && /^prj-[0-9a-f]{48}$/.test(focusAssignedProjectId)),
  );
  const [draft, setDraft] = useState(EMPTY_DRAFT);
  const [edit, setEdit] = useState(null);
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
    if (projectId !== selectedRef.current) setProjectView('work');
    selectedRef.current = projectId;
    setSelectedId(projectId);
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
    setError('');
    try {
      const [listResponse, summaryResponse] = await Promise.all([
        api.get(
          statusFilterRef.current === 'all' && pageOffsetRef.current === 0 && !ownerOnlyRef.current
            ? '/projects'
            : `/projects?limit=100&offset=${pageOffsetRef.current}${statusFilterRef.current === 'all' ? '' : `&project_status=${statusFilterRef.current}`}${ownerOnlyRef.current ? '&owned_by_me=true' : ''}`,
          { headers: tenantHeaders },
        ),
        api.get('/projects/summary', { headers: tenantHeaders }),
      ]);
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
      const nextSummary = assertProjectSummary(summaryResponse?.data, tenantId, principalId);
      itemsRef.current = nextItems;
      setItems(nextItems);
      setHasNextPage(verifiedNextPage);
      setSummary(nextSummary);
      setSourceState('READY');
      const currentSelection = selectedRef.current;
      if (!preserveSelection || (currentSelection && !nextItems.some((item) => item.project_id === currentSelection))) {
        changeSelection(null);
        setDetail(null);
        setDetailState('IDLE');
      }
      return { items: nextItems, counts: nextSummary };
    } catch (cause) {
      if (sequence !== listSequence.current || activeScope.current !== requestScope) return null;
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
    if (focusAssignedProjectId && /^prj-[0-9a-f]{48}$/.test(focusAssignedProjectId)) {
      setShowAssignedProjects(true);
    } else {
      void refresh({ preserveSelection: false });
    }
    return () => {
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
    await runCommand(async () => {
      const response = await api.patch(`/projects/${encodeURIComponent(selectedId)}`, {
        expected_revision: project.revision,
        name: edit.name,
        code: edit.code || null,
        summary: edit.summary || null,
        start_date: edit.start_date || null,
        target_date: edit.target_date || null,
      }, { headers: { ...tenantHeaders, 'Idempotency-Key': newIdempotencyKey() } });
      const result = assertProjectResult(response?.data, tenantId, principalId, selectedId, project.revision + 1);
      const projection = await refresh();
      if (!projection?.items.some((item) => item.project_id === selectedId && item.revision === result.project.revision)) {
        throw new Error('PROJECT_UPDATE_LIST_READBACK_UNAVAILABLE');
      }
      if (!await openProject(selectedId)) throw new Error('PROJECT_UPDATE_DETAIL_READBACK_UNAVAILABLE');
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

  const personLabel = (principal) => {
    if (!principal) return 'Not assigned';
    const profile = detail?.actor_profiles?.[principal];
    const name = [profile?.first_name, profile?.last_name].filter(Boolean).join(' ');
    return name || 'Name not recorded';
  };
  const statusLabel = (value) => String(value || 'unknown').replaceAll('_', ' ');
  const countLabel = summary
    ? `${summary.active ?? '—'} active · ${summary.total} total`
    : 'Counts unavailable';

  if (showAssignedProjects) {
    return <AssignedProjectsWorkspace
      tenantId={tenantId} principalId={principalId}
      tenantHeaders={tenantHeaders} sessionScope={sessionScope}
      focusProjectId={focusAssignedProjectId}
      onBack={() => { setShowAssignedProjects(false); void refresh({ preserveSelection: false }); }}/>;
  }

  return (
    <section className="wilsy-projects mx-auto w-full max-w-[1500px] px-3 pb-6 sm:px-5" data-projects-workspace data-source-state={sourceState}>
      <header className="wp-toolbar mb-4 flex flex-wrap items-center justify-between gap-3 rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
        <div><p className="wp-eyebrow text-[10px] font-semibold uppercase tracking-[0.18em] text-amber-700">Projects &amp; delivery</p><h1 className="wp-title mt-1 text-2xl font-bold text-slate-900">Projects</h1><p className="wp-subtitle mt-1 text-sm text-slate-600">EOS-authorized project delivery for the selected workspace.</p></div>
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
      </header>

      {sourceState === 'READY' && summary && !selectedId && mode !== 'CREATE' && (
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
      )}
      {sourceState === 'LOADING' && <div role="status" className="mb-3 rounded-lg border border-blue-200 bg-blue-50 p-3 text-sm text-blue-900"><LoaderCircle className="mr-2 inline animate-spin" size={15}/>Loading authorized Projects from EOS…</div>}
      {sourceState === 'DENIED' && <div role="alert" data-project-state="DENIED" className="mb-3 rounded-lg border border-rose-200 bg-rose-50 p-4 text-sm text-rose-900"><ShieldCheck className="mr-2 inline" size={16}/>{error === 'AUTHENTICATION_REQUIRED' ? 'Your session needs reauthentication before Projects can be read.' : error === 'PROJECTS_ENTITLEMENT_REQUIRED' ? 'An active Projects product entitlement is required for this tenant.' : 'EOS denied Projects access for this principal and selected tenant. No project records or counts are shown.'}</div>}
      {sourceState === 'UNAVAILABLE' && <div role="alert" data-project-state="UNAVAILABLE" className="mb-3 flex flex-wrap items-center justify-between gap-3 rounded-lg border border-amber-300 bg-amber-50 p-4 text-sm text-amber-950"><span><CircleAlert className="mr-2 inline" size={16}/>{error === 'AUTHENTICATED_TENANT_REQUIRED' ? 'A verified tenant session is required.' : 'The EOS Projects source is unavailable. No empty result is inferred.'}</span><button type="button" onClick={() => void refresh()} className="rounded-md border border-amber-400 px-3 py-2 font-semibold">Retry</button></div>}
      {sourceState === 'STALE' && <div role="status" className="mb-3 rounded-lg border border-amber-300 bg-amber-50 p-3 text-sm text-amber-950">The latest EOS read failed. Previously verified records remain marked stale. <button type="button" onClick={() => void refresh()} className="font-bold underline">Retry</button></div>}
      {sourceState === 'REFRESHING' && <div role="status" className="mb-3 text-xs text-slate-500">Refreshing from EOS…</div>}

      <div className="wp-body grid min-w-0 grid-cols-1 items-start gap-4"
        data-layout={selectedId && mode !== 'CREATE' ? 'detail' : 'list'}
        style={selectedId && mode !== 'CREATE'
          ? { display: 'block', width: '100%', height: 'auto', overflow: 'visible' }
          : undefined}>
        <section aria-label="Project list" className="wp-panel wp-list-panel min-w-0 overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm"
          style={selectedId && mode !== 'CREATE' ? { display: 'none' } : undefined}>
          {mode === 'CREATE' ? (
            <form onSubmit={submitCreate} className="wp-form space-y-4 p-4 sm:p-5" aria-labelledby="project-create-title">
              <div className="flex items-start justify-between gap-3"><div><h2 id="project-create-title" className="text-lg font-bold text-slate-900">Create project</h2><p className="mt-1 text-sm text-slate-600">EOS validates authority and confirms the persisted project before it appears in the list.</p></div><button type="button" aria-label="Cancel project creation" onClick={() => { setMode('LIST'); setCommandError(''); }} disabled={commandState === 'PENDING'} className="wp-close rounded-md p-2 text-slate-600 hover:bg-slate-100"><X size={18}/></button></div>
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
            {sourceState === 'READY' && items.length === 0 ? <div className="p-8 text-center"><Code2 className="mx-auto text-slate-400" size={28}/><h2 className="mt-3 font-semibold text-slate-900">No projects in this tenant</h2><p className="mt-1 text-sm text-slate-600">EOS returned a verified empty Projects list.</p></div> : sourceState === 'READY' && visibleItems.length === 0 ? <p className="p-6 text-center text-sm text-slate-600">{ownerOnly ? 'No EOS-verified projects are owned by your current principal on this page.' : 'No projects match the current search and status filter.'}</p> : <div className="wp-table-shell" role="region" aria-label="Projects table" tabIndex={0}>
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
                    <span><strong className="wp-row-title">{item.name}</strong><span className="wp-row-meta">{item.project_id}</span></span>
                    <span className="text-sm text-slate-700">{item.code || 'No project code'}</span>
                    <span><span className="wp-status" data-status={item.status}>{statusLabel(item.status)}</span></span>
                    <span className="text-sm text-slate-700">{item.target_date || 'No target date'}</span>
                    <span className="wp-table-action">View details</span>
                  </button>
                </li>)}
              </ul>
            </div>}
            <footer className="wp-footer border-t border-slate-200 px-4 py-2 text-xs text-slate-500">
              <span>{sourceState === 'READY' ? `${visibleItems.length} shown · ${items.length} verified${ownerOnly ? " · EOS owner-filtered page" : ""}` : 'Source state shown above'}</span>
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
          className="wp-panel wp-detail min-w-0 rounded-xl border border-slate-200 bg-white p-4 shadow-sm sm:p-5"
          style={{ width: '100%', height: 'auto', maxHeight: 'none', overflow: 'visible' }}>
          <div className="wp-detail-top mb-3 flex flex-wrap items-start justify-between gap-4">
            <div className="min-w-0">
              <button type="button" onClick={closeDetail}
                className="wp-button mb-3" aria-label="Back to projects table">
                <X size={15}/> Back to all projects
              </button>
              <p className="wp-eyebrow">Projects &amp; delivery / Current project</p>
              <h2 className="wp-detail-title">{detail?.project?.name || 'Loading project…'}</h2>
              {detail?.project && <div className="mt-3 flex flex-wrap items-center gap-3 text-sm text-slate-700">
                <span className="wp-status" data-status={detail.project.status}>
                  {statusLabel(detail.project.status)}
                </span>
                <span className="font-semibold">{detail.project.code || 'Code not recorded'}</span>
                <span>Revision {detail.project.revision}</span>
                <span>Target {detail.project.target_date || 'not scheduled'}</span>
              </div>}
            </div>
            <button type="button" onClick={() => void openProject(selectedId)}
              disabled={detailState === 'LOADING'} className="wp-button">
              <RefreshCw size={15}/> Refresh project
            </button>
          </div>
          <nav className="mb-5 flex flex-wrap gap-2 border-b border-slate-200 pb-3"
            aria-label="Project workspace views">
            {[
              ['work', 'Work & milestones'],
              ['overview', 'Overview'],
              ['people', 'People'],
              ['notes', 'Notes'],
              ['settings', 'Manage project'],
              ['history', 'Audit history'],
            ].map(([value, label]) =>
              <button key={value} type="button"
                aria-current={projectView === value ? 'page' : undefined}
                onClick={() => setProjectView(value)}
                className="wp-button"
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
              {detail.project.code || 'Not recorded'}
              {!detail.project.code && <button type="button"
                className="wp-code-action"
                onClick={() => void assignGeneratedCode()}
                disabled={commandState === 'PENDING' || sourceState !== 'READY'}
              >Generate and save code</button>}
            </dd><dt className="text-slate-500">Status</dt><dd className="capitalize text-slate-900">{statusLabel(detail.project.status)}</dd><dt className="text-slate-500">Revision</dt><dd className="text-slate-900">{detail.project.revision}</dd><dt className="text-slate-500">Owner</dt><dd className="text-slate-900">
              {personLabel(detail.project.owner_principal_id)}
              {detail.project.owner_principal_id && <small className="ml-2 text-xs text-slate-500" title={detail.project.owner_principal_id}>Verified principal</small>}
            </dd><dt className="text-slate-500">Created by</dt><dd className="text-slate-900">
              {personLabel(detail.project.created_by_principal_id)}
              <small className="ml-2 text-xs text-slate-500" title={detail.project.created_by_principal_id}>Audited creator</small>
            </dd><dt className="text-slate-500">Department</dt><dd className="text-slate-900">{detail.project.department_id || 'Not assigned'}</dd><dt className="text-slate-500">Target date</dt><dd className="text-slate-900">{detail.project.target_date || 'Not scheduled'}</dd></dl><p className="wp-record-note">These values come from the current EOS project record. Owner and department are recorded only after EOS verifies independent assignment authority and source-backed eligibility.</p>
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
              principalId={principalId} tenantHeaders={tenantHeaders}/>}
            {projectView === 'notes' && <ProjectNotesPanel key={detail.project.project_id + ':' + sessionScope} projectId={detail.project.project_id}
              tenantId={tenantId} principalId={principalId} tenantHeaders={tenantHeaders}/>}
            {projectView === 'settings' && <div className="max-w-5xl">
            <form onSubmit={submitUpdate} className="wp-form space-y-3 border-t border-slate-200 pt-4"><h3 className="font-semibold text-slate-900">Update project</h3><label className="block text-xs font-semibold text-slate-700">Name<input value={edit?.name || ''} onChange={(event) => setEdit({ ...edit, name: event.target.value })} maxLength={180} className="mt-1 min-h-10 w-full rounded-md border border-slate-300 px-3 text-sm font-normal"/></label><label className="block text-xs font-semibold text-slate-700">Project code <span className="wp-code-optional">(optional override)</span>
                <input aria-label="Project code" maxLength={80} value={edit?.code || ''}
                  placeholder="Automatically assigned by EOS"
                  onChange={event => setEdit({ ...edit, code: event.target.value })}
                  className="mt-1 min-h-10 w-full rounded-md border border-slate-300 px-3 text-sm font-normal"/>
                <small className="wp-code-hint">Optional: keep the generated code, or enter a unique code such as WOS-PLAT-001 (up to 80 characters). EOS validates and audits any change.</small>
              </label><label className="block text-xs font-semibold text-slate-700">Summary<textarea rows={2} value={edit?.summary || ''} onChange={(event) => setEdit({ ...edit, summary: event.target.value })} maxLength={4000} className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2 text-sm font-normal"/></label><div className="wp-form-grid">
                <ProjectDateField label="Start" value={edit?.start_date || ''} disabled={commandState === 'PENDING'}
                  onChange={value => setEdit(current => ({ ...current, start_date: value }))}/>
                <ProjectDateField label="Target" value={edit?.target_date || ''} disabled={commandState === 'PENDING'}
                  onChange={value => setEdit(current => ({ ...current, target_date: value }))}/>
              </div><button type="submit" disabled={commandState === 'PENDING'} className="wp-button min-h-10 w-full rounded-lg border border-blue-700 px-3 text-sm font-semibold text-blue-800 hover:bg-blue-50 disabled:opacity-50">{commandState === 'PENDING' ? 'Saving…' : 'Save revision'}</button></form>
            <div className="wp-actions mt-3 grid grid-cols-1 gap-2 sm:grid-cols-[minmax(0,1fr)_auto]"><label className="sr-only" htmlFor="project-status">Project status</label><select id="project-status" value={detail.project.status} disabled={commandState === 'PENDING'} onChange={(event) => void transitionStatus(event.target.value)} className="min-h-10 rounded-lg border border-slate-300 bg-white px-3 text-sm capitalize">{PROJECT_STATUSES.map((value) => <option key={value} value={value} disabled={value === 'active' && (!detail.project.owner_principal_id || !detail.project.department_id)}>{statusLabel(value)}</option>)}</select><button type="button" disabled={commandState === 'PENDING' || Boolean(detail.project.archived_at)} onClick={() => void archiveProject()} className="wp-button wp-button-danger inline-flex min-h-10 items-center justify-center gap-2 rounded-lg border border-rose-300 px-3 text-sm font-semibold text-rose-800 hover:bg-rose-50 disabled:opacity-50"><Archive size={14}/> Archive</button></div>
            {(!detail.project.owner_principal_id || !detail.project.department_id) && detail.project.status === 'planned' && <p role="status" className="mt-2 text-xs text-amber-900">Activation requires a verified project owner and tenant department. The project remains Planned until EOS confirms both.</p>}
            {commandError && <p role="alert" className="mt-3 rounded-md border border-rose-200 bg-rose-50 p-3 text-sm text-rose-800">{commandError === 'ACCESS_DENIED' ? 'EOS denied this command; project state has not been changed.' : commandError === 'PROJECTS_ENTITLEMENT_REQUIRED' ? 'An active Projects entitlement is required.' : commandError === 'PROJECT_REVISION_OR_REPLAY_CONFLICT' ? 'The project revision changed. Refresh the source before retrying.' : commandError === 'PROJECT_INPUT_INVALID' ? 'EOS rejected the supplied fields. Check the network response detail, including validation paths.' : /^PROJECT_[A-Z0-9_]{1,90}$/.test(commandError) ? 'EOS response: ' + commandError + '. No success has been inferred.' : 'EOS did not confirm the command. The source state is retained; refresh before retrying.'}</p>}
            {commandState === 'CONFIRMED' && <p role="status" className="mt-3 text-sm font-medium text-emerald-800">EOS confirmed the project change and returned persisted state.</p>}
            </div>}
            {projectView === 'history' && <section className="wp-section mt-5 border-t border-slate-200 pt-4"><h3 className="font-semibold text-slate-900">Audit events</h3>{Array.isArray(detail.events) && detail.events.length ? <ol className="mt-2 max-h-56 space-y-2 overflow-y-auto pr-1">{detail.events.map((event) => <li key={event.event_id} className="wp-event rounded-md bg-slate-50 p-2 text-xs"><strong className="text-slate-800">{event.event_type}</strong><div className="mt-1 text-slate-700">By {personLabel(event.actor_principal_id)} · revision {event.revision}</div>
              <div className="text-xs text-slate-500" title={event.actor_principal_id}>Immutable actor ID retained in EOS audit evidence</div><time className="text-slate-500">{event.occurred_at ? new Date(event.occurred_at).toLocaleString() : 'Timestamp unavailable'}</time></li>)}</ol> : <p className="mt-2 text-sm text-slate-600">No audit event was returned by EOS.</p>}</section>}
          </div>}
        </section>}
      </div>
    </section>
  );
}

// ARTIFACT: ProjectsWorkspace.jsx
// VERSION: v2.14.0-INDEXED-OWNER-RESPONSIBILITY-PAGES
// AUTHORITY BOUNDARY: authenticated EOS requests and returned source state only; no local project truth
// TENANT POSTURE: scope changes invalidate late responses and EOS validates the active session tenant
// FAIL-CLOSED POSTURE: denial, missing entitlement, unavailable source, conflict, invalid readback and stale state remain distinct
// FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
// END OF WILSY OS SOVEREIGN ARTIFACT
