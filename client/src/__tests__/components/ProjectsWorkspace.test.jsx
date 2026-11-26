/**
 * TITLE: WILSY OS Projects workspace interaction certificate
 * VERSION: v2.80.2-NODE-ISOLATED-CSS-CERT
 * CHANGELOG: v2.80.2-NODE-ISOLATED-CSS-CERT keeps UI behavior in Vitest, moves exact stylesheet text assertions to the separately executed Node native certificate so mocked CSS cannot silently become empty.
 * CHANGELOG: v2.80.1-PORTABLE-CSS-SOURCE-CERT reads exact stylesheet through Vite raw assets rather than Node fs/path built-ins, retaining both CSS rule assertions and supporting local Vitest module loading.
 * CHANGELOG: v2.80.0-COMPLETED-WORK-LIFECYCLE-VIEWS-CERT confirms Done tasks disappear from active work, remain in the Completed/All views and open their original source-backed task details; work selection resets on view changes, without mutation.
 * CHANGELOG: v2.48.0-UNOBSTRUCTED-PROJECT-HEADER-CERT verifies the selected project's title remains in its own heading row and the all-projects action lives only in the project navigation strip.
 * AUTHORITY: Client contract evidence only; Python EOS owns Projects authority.
 * EPITOME: Proves exact-scope list/detail/summary validation and the user-facing
 *          create, update, status-transition and archive readback sequence.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/__tests__/components/ProjectsWorkspace.test.jsx
 * COLLABORATION / OWNERSHIP: Vitest mocks the existing authenticated api.js transport; no database is contacted.
 * CERTIFICATION / UPDATE DATE: 2026-11-24.
 * CHANGELOG: v2.79.0-FOCUS-FIRST-TASK-ACTIVITY-EDITOR-CERT
 *          verifies the focused Projects task replaces the source activity
 *          history with an immediately focused comment editor on command.
 *          Closing restores the original EOS timeline and preserves the
 *          draft; verified publication still gates durable readback.
 * CHANGELOG: v2.78.1-SINGLE-MODAL-EXIT-CERT checks
 *          Activity in the focused Projects task workspace has one
 *          visible parent Back to Work action and no redundant nested
 *          Close; all source-backed content and navigation remain.
 * CHANGELOG: v2.78.0-EXPANDABLE-ACTIVITY-READBACK-CERT uses
 *          the accessible ordered source activity timeline for positional
 *          assertions, and explicitly expands the immutable long MW-T12
 *          comment before asserting its exact committed EOS readback.
 *          Short entries and response/command proof remain unchanged.
 * CHANGELOG: v2.77.0-LIST-FIRST-FREE-TIER-LOAD-CERT confirms that the
 *          actionable Projects list is independently source-verified
 *          before optional portfolio summary starts a second transaction.
 *          No permission, timeout, schema or IAM mock relaxation.
 * CHANGELOG: v2.76.0-SHARED-TASK-TAB-READ-CERT verifies switching from work
 *          into project discussion preserves one task GET and the source
 *          snapshot instead of remounting the same task panel and
 *          restarting authorization and database reads.
 * CHANGELOG: v2.75.2-MW-T12-SOURCE-EVIDENCE-CERT treats an EOS-sourced
 *          immutable comment displayed after held readback as the actual
 *          milestone certificate, independently of composer clearing UX.
 * CHANGELOG: v2.75.1-MW-T12-ACTIVITY-READBACK-GATE-CERT waits for the actual
 *          post-command source read rather than assuming a fixed GET
 *          sequence; periodic component reads cannot satisfy the gate.
 * CHANGELOG: v2.75.0-MW-T12-ACTIVITY-READBACK-SIMULATION exercises existing exact-task
 *          comment commands, waits for independent readback and refreshes
 *          history without inventing rollback, Strategy or release truth.
 * COMPLIANCE: AGENTS.md; POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
 * SECURITY / PRIVACY POSTURE: Synthetic exact-scope fixtures only; no tokens,
 *          real identities, private comments or production credentials.
 * TENANT BOUNDARY: Exact tenant and project checks; no root fallback.
 * AUTHORITY BOUNDARY: Mock client assertions only; Python EOS owns IAM,
 *          task commands, decisions, evidence and immutable audit truth.
 * FINANCIAL AUTHORITY BOUNDARY: No financial execution or approval grants.
 * CHANGELOG: v2.74.0-ASYNC-SOURCE-READY-CLIENT-CERT
 *          waits for the optional views to mount after project reads
 *          and for contributor admission to become enabled only after
 *          its independent participant/option sources verify.
 * CHANGELOG: v2.73.0-QUEUES-FIRST-OPTIONAL-VIEWS-CERT opens the deliberately
 *          deferred lifecycle/checklist disclosures before checking
 *          visible evidence. The verified work grid remains first.
 * CHANGELOG: v2.72.0-INDEPENDENT-MULTI-ASSIGNMENT-CERT certifies selected-task
 *          contributor assignment issues distinct revision-guarded EOS
 *          PATCH commands, verifies each persisted source before the
 *          next, and never rewrites work status or uses a bulk endpoint.
 * CHANGELOG: v2.71.4-BATCH-PAGINATION-ROW-CERT verifies
 *          twenty source work records regardless of selection header.
 * CHANGELOG: v2.71.3-DOM-ROW-COUNT-CERT accesses the actual
 *          rendered table element when counting task rows, not the
 *          Testing Library scoped-query collection.
 * CHANGELOG: v2.71.2-SELECTION-HEADER-PAGING-CERT counts
 *          actual source-verified work rows independently of the
 *          contextual selected-work header in the grid.
 * CHANGELOG: v2.71.1-FOCUSED-TASK-AND-PAGING-CERT
 *          tracks the one Back to Work control, requires independently
 *          rendered current-page buttons rather than stale DOM references,
 *          and awaits asynchronous assignment-modal visibility without
 *          weakening exact EOS role/readback assertions.
 * CHANGELOG: v2.71.0-ACTIONABLE-WORK-TITLE-CERT checks the
 *          task's semantic title button instead of a former inert span,
 *          asserts actual selected-row checkbox and in-grid multi-select
 *          state, and keeps exact-source upload denial assertions.
 * CHANGELOG: v2.70.0-DROPZONE-ATTACHMENT-CERT verifies
 *          accessible contributor Browse and owner upload denial
 *          alongside the EOS-verified empty file state.
 * CHANGELOG: v2.69.1-COMPACT-DISCLOSURE-READBACK-CERT
 *          validates native disclosure state and source-owned assignment
 *          readback instead of presentation-only revision label checks.
 * CHANGELOG: v2.69.0-COMPACT-TASK-DETAILS-CERT
 *          verifies title and description remain editable inside explicit
 *          compact disclosure; accountability controls remain immediately
 *          visible and command/readback semantics remain unchanged.
 * CHANGELOG: v2.68.0-NONBLOCKING-VERIFIED-TASK-SAVE-CERT
 *          task save closes after mandatory readback even with stalled
 *          optional source reads; contributor assignment still requires
 *          authorization and verified fresh task data.
 * CHANGELOG: v2.67.0-ACCOUNTABILITY-ASSIGNMENT-READBACK-CERT
 *          proves source-owned contributor assignment through authorized
 *          PATCH, fresh list readback and reopened task owner display.
 * CHANGELOG: v2.66.0-ACCOUNTABILITY-DATE-PERSISTENCE-CERT
 *          asserts due-date changes are CAS-saved and independently
 *          read back on reopening the same authorized task.
 * CHANGELOG: v2.65.0-ACCOUNTABLE-TASK-EDITOR-FIRST-CERT
 *          verifies accountability precedes secondary classification,
 *          due date and contributor controls lead task editing, and
 *          source authority still blocks unauthorized task changes.
 * CHANGELOG: v2.64.1-FOREIGN-SOURCE-USER-ERROR-CERT
 *          preserves the foreign-tenant fail-closed assertions while
 *          verifying the current plain-language unavailable message.
 * CHANGELOG: v2.64.0-NONBLOCKING-TASK-DRAWER-ADMISSION-CERT
 *          proves a verified task opens while optional contributor,
 *          member and capability requests never finish, without enabling
 *          command buttons or weakening task or project verification.
 * CHANGELOG: v2.63.0-EXACT-STRATEGY-TASK-FOCUS-CERT
 *          verifies Strategy-selected task details only after exact-project
 *          and exact-task readback, with no task mutation.
 * CHANGELOG: v2.62.0-BOUNDED-PROJECT-TASK-PAGING-CERT
 *          verifies ten-record default views, forward/back view navigation,
 *          page-size selection and exact-visible selection on one authorized
 *          EOS task batch; updates scope-accurate filter result wording.
 * CHANGELOG: v2.61.0-ATTACHMENT-PEOPLE-PREFLIGHT-CERT asserts failed attachment sources cannot send the user into an unverified People workflow; exact-scope project participants and eligible tenant-member directory are independently preflighted on deliberate action and 403 stays on the task surface.
 * CHANGELOG: v2.60.0-ATTACHMENT-ERROR-SCHEMA-CERT pins explicit invalid task-attachment source envelope diagnostics and bounded safe EOS HTTP error classes while refusing unauthorized uploads.
 * CHANGELOG: v2.59.0-ATTACHMENT-OWNER-AUTHORITY-AND-FAILURE-CERT certifies owner-view attachment 503 source-code diagnosis and a functional route to People for explicit contributor admission. Upload stays unavailable without independently admitted participant IAM; unverified manifests do not fabricate empty files.
 * CHANGELOG: v2.58.0-BOUNDED-ERROR-CODE-PRESENTATION-CERT certifies sanitized source code visibility for HTTP 503 while task list still fails closed; unknown error text is never reflected.
 * CHANGELOG: v2.57.0-PRIMARY-TASK-READ-FIRST-CERT certifies mandatory task GET dispatch completes before optional participant/member queries and exposes actual 503 task source failure instead of fabricating rows. Preserves isolation of independently verified work from failed directories.
 * CHANGELOG: v2.56.0-FAULT-ISOLATED-WORK-READ-CERT certifies that independently verified task records remain available despite rejected contributor-directory reads; task assignment is refused while participant authorization is unverified and source failure is explicit.
 * CHANGELOG: v2.55.0-TENANT-NAMED-ASSIGNEE-ADMISSION-CERT verifies tenant employee names appear in the task Assignee selector as candidate choices and selecting a candidate opens a preselected explicit contributor grant. The task draft is assigned only after independent exact-project readback, not by dropdown choice alone.
 * CHANGELOG: v2.54.0-VIEWPORT-CONTRIBUTOR-SELECTOR-CERT tests immediately visible contributor admission dialog instead of the offscreen inline panel, with the original task editor draft preserved and EOS readback gating assignment.
 * CHANGELOG: v2.53.0-COLLAPSIBLE-FILTERS-AND-ASSIGNEE-ONBOARDING-CERT certifies default-collapsed work filters and source-backed contributor admission from an unassigned task editor, retaining the draft and refreshing assignees only after independent participant readback; no IAM grant or task write.
 * CHANGELOG: v2.52.0-SELECTED-TASK-LOCATOR-LIFECYCLE-CERT verifies an open
 *          EOS-verified task drawer publishes only task id/revision, closing
 *          it clears task focus, and no task title enters browser locators.
 * CHANGELOG: v2.51.0-AI-LOCATOR-PRIVACY-CERT verifies verified-detail locators,
 *          absence of source content in browser events and cleanup on exit.
 * CHANGELOG: v2.50.0-TEMPLATE-FAILURE-RETRY-SOURCE-CERT verifies missing backend routes and
 *          malformed catalogue envelopes are separately diagnosed, source
 *          fallback is prohibited, and an explicit retry recovers 17 options.
 * CHANGELOG: v2.49.0-SEVENTEEN-TEMPLATE-AND-AI-SURFACE-CERT certifies all seventeen industry
 *          options and the opt-in WILSY AI draft-planning surface.
 * CHANGELOG: v2.48.0-HUMAN-OVERVIEW-SOURCE-CERT verifies human-readable project facts without
 *          requiring generated codes or audit revisions in the overview.
 * CHANGELOG: v2.47.0-IMMUTABLE-BASELINE-UI-CERT certifies immutable project baseline fields,
 *          revised target dates, human-only participant presentation and
 *          verified grouped page counts against source-authorized UI.
 * CHANGELOG: v2.46.0-VERIFIED-WORK-GROUPING-CERT certifies grouping of
 *          exact-page tasks by lifecycle with accurate page-only counts,
 *          preserved controls and no unapproved bulk mutation.
 * CHANGELOG: v2.45.0-INLINE-DISCUSSION-AND-NOTES-ENTRY-CERT certifies in-place activity
 *          expands from verified list rows and keeps project-notes access
 *          available without entering the full task drawer.
 * CHANGELOG: v2.44.0-HUMAN-OVERVIEW-AND-IDENTITY-CERT pins readable department names,
 *          capitalized status and suppression of opaque principal IDs in
 *          operating views; verifies source-verified assignment display.
 * CHANGELOG: v2.43.0-COMPACT-DENSITY-STRUCTURAL-CERT checks compact rows hide
 *          expanded detail disclosures and bound action controls to
 *          preserve the 44px density target.
 * CHANGELOG: v2.42.0-CALENDAR-DUE-ROW-PHRASE-CERT pins short date-only
 *          Work Row due phrases including today, tomorrow and overdue;
 *          the original EOS ISO date remains available as metadata.
 * CHANGELOG: v2.41.0-VERIFIED-ASSIGNEE-AVATAR-CERT validates a compact name-derived
 *          assignee identity marker and prohibits displaying backend IDs;
 *          no principal name is invented when missing.
 * CHANGELOG: v2.40.0-ASSIGN-VERSUS-EDIT-CAPABILITY-CERT verifies that a signed
 *          exact-project canAssign response enables the dedicated assignment
 *          picker independently of the canEdit flag.
 * CHANGELOG: v2.39.0-STRICT-ROW-CAPABILITY-BOOLEAN-CERT certifies that missing row
 *          capability flags never expose assignment or lifecycle actions,
 *          even when callbacks are supplied by a reused consumer.
 * CHANGELOG: v2.38.0-ISOLATED-CANCEL-DIALOG-CERT verifies cancel confirmation is a
 *          separately focused modal, not a stacked menu, and requires
 *          explicit confirmation before any EOS transition callback.
 * CHANGELOG: v2.37.0-DENY-BY-DEFAULT-WORK-ACTIONS-CERT certifies omitted capability flags
 *          cannot expose task mutations, while explicit EOS-verified flags
 *          retain primary, menu and mobile action-sheet behaviour.
 * CHANGELOG: v2.36.0-EOS-ACTION-DENIAL-READ-ONLY-CERT proves
 *          that denied task update authority hides row mutations after
 *          refresh without concealing source-verified task records.
 * CHANGELOG: v2.35.0-EOS-CAPABILITY-PROJECTION-CERT supplies only
 *          synthetic exact-project capability records for existing work
 *          journeys; no test fixture grants actual update authority.
 * CHANGELOG: v2.34.1-CONTEXTUAL-MENU-REGRESSION-CERT adapts
 *          existing task edit/activity journeys to desktop menu roles.
 * CHANGELOG: v2.34.0-CAPABILITY-AWARE-MENU-CERT pins desktop menu
 *          keyboard/ARIA and separate Assign/Edit, ensuring explicitly
 *          forbidden action flags hide commands without invoking EOS.
 * CHANGELOG: v2.33.0-WORK-ROW-SELECTION-DENSITY-CERT proves
 *          selected rows toggle independently and page selection is visual
 *          only; work density switches without a server mutation.
 * CHANGELOG: v2.32.0-PENDING-WORK-TRANSITION-CERT verifies immediate
 *          pending feedback without premature task completion, then requires
 *          authoritative readback to clear the pending presentation.
 * CHANGELOG: v2.31.1-SOURCE-REASSIGN-NOOP-CERT proves an assigned
 *          contributor is actionable and an unchanged selection cannot
 *          issue a no-op task revision through EOS.
 * CHANGELOG: v2.31.0-ASSIGNMENT-FOCUS-CERT verifies A opens a compact
 *          current-project assignment picker without unrelated task fields,
 *          while task edits preserve their separate revisioned form.
 * CHANGELOG: v2.30.2-NO-OPAQUE-PROJECT-HEADER-CERT pins the removal
 *          of automatic hexadecimal project codes from the main list and
 *          selected-project header without changing authoritative IDs.
 * CHANGELOG: v2.30.1-COMMITTED-TEMPLATE-COPY-CERT asserts a confirmed
 *          201 activation uses the committed-pending-readback message, not
 *          the distinct ambiguous-save warning.
 * CHANGELOG: v2.30.0-FOCUSED-WORK-KEYBOARD-CERT proves J/K focus,
 *          A opens a bounded edit sheet, and no keyboard shortcut creates
 *          an unauthorized work transition or completion attestation.
 * CHANGELOG: v2.29.1-UNCERTAIN-TEMPLATE-OUTCOME-CERT proves an ambiguous
 *          activation response prompts a source-based list inspection, not
 *          a duplicate POST or a fabricated saved/failed claim.
 * CHANGELOG: v2.29.0-PROJECT-MY-WORK-FILTER-CERT verifies that current
 *          assignee filtering uses only the source-backed current project page,
 *          remains reversible and performs no unauthorized write.
 * CHANGELOG: v2.28.7-MOBILE-ACTION-SHEET-GESTURE-CERT pins a downward
 *          sheet dismissal without executing a mutation or leaving body
 *          scroll locked on a mobile viewport.
 * CHANGELOG: v2.28.6-POSTCOMMAND-REVISION-BROWSER-CERT waits for the
 *          committed revision before reading owner names, reacquires
 *          work rows after filters remount them, and scopes contextual
 *          actions to the current source row.
 * CHANGELOG: v2.28.6-POSTCOMMAND-REVISION-BROWSER-CERT validates source changes
 *          independently of collapsed optional visualizations, scopes
 *          contextual action selection, and preserves correct post-command
 *          disabled states after owner assignment.
 * CHANGELOG: v2.28.6-POSTCOMMAND-REVISION-BROWSER-CERT prevents invisible
 *          template form labels and opaque internal IDs in the verified
 *          industry creation experience at the current test head.
 * CHANGELOG: v2.28.6-POSTCOMMAND-REVISION-BROWSER-CERT certifies Arrow/Home/End
 *          navigation and focus return for the real responsive action
 *          presenter without adding fake lifecycle authority.
 * CHANGELOG: v2.28.6-POSTCOMMAND-REVISION-BROWSER-CERT awaits source-ready row actions after
 *          each command, opens contextual overflow rather than removed
 *          peer buttons, and exercises on-demand checklist/assignment state.
 * CHANGELOG: v2.28.1-KEYBOARD-WORK-DRAWER-CERT verifies
 *          keyboard Enter opens the exact source work drawer and Close
 *          returns focus without mutating persisted EOS task data.
 * CHANGELOG: v2.28.0-RESPONSIVE-WORK-ACTION-CERT asserts
 *          the status-derived primary action, Escape focus restoration,
 *          contextual blocking and explicit destructive cancel confirmation.
 * CHANGELOG: v2.27.3-VALID-TEMPLATE-READBACK-FIXTURE uses a
 *          real two-step work/milestone blueprint in the accepted-command
 *          delayed-list regression, matching strict catalogue validation.
 * CHANGELOG: v2.27.2-CONTEXTUAL-TASK-EDIT-CERT ensures
 *          modal task editing retains EOS revision readback and an
 *          accessible, discoverable save action.
 * CHANGELOG: v2.27.1-NO-FALSE-EMPTY-AFTER-COMMIT-CERT refuses
 *          to render an empty-tenant notice over EOS-confirmed persisted
 *          template materialisation pending list reconciliation.
 * CHANGELOG: v2.27.0-POSTCOMMIT-READBACK-SEPARATION-CERT guards against false
 *          template save failures after EOS committed an authoritative
 *          project but the independent list has not yet returned that item.
 * CHANGELOG: v2.26.1-COLLAPSED-PORTFOLIO-CERT verifies optional portfolio chart disclosure
 *          while the source-backed project table remains primary.
 * CHANGELOG: v2.26.0-PRIMARY-QUEUE-POSTCOMMIT-REGRESSION certifies read-first queue disclosures,
 *          direct Start/Complete controls, contextual secondary task actions,
 *          and separated accepted template activation versus readback failures.
 * CHANGELOG: v2.25.2-EXACT-STATUS-SOURCE-READBACK-CERT verifies
 *          the actual source-backed status control after transition,
 *          without depending on the portfolio toolbar removed from detail.
 * CHANGELOG: v2.25.1-TEMPLATE-RENAMED-DRAFT-CERT certifies
 *          the user-renamed project draft is passed verbatim into the
 *          independently authenticated template activation contract.
 * CHANGELOG: v2.25.0-COMPACT-SELECTED-PROJECT-CERT confirms the
 *          portfolio summary is displayed in list mode, while selected
 *          project views prioritize verified project work; a summary 503
 *          never hides the authorized list or detail on navigation.
 * CHANGELOG: v2.24.0-SEVEN-INDUSTRY-MATERIALIZATION-CLIENT-CERT verifies
 *          seven exact-scope source definitions, a selected business blueprint,
 *          one explicit activation, and independent project list/detail readback.
 * CHANGELOG: v2.23.0-ACTIVITY-FIRST-TEMPLATE-UI-CERT verifies that source activity precedes the
 *          optional editor in DOM, with contextual accessible note actions.
 * CHANGELOG: v2.22.0-CONTEXTUAL-NOTE-READBACK-CERT verifies compact read-first
 *          source notes, optional new-note composer and implicit CAS revision
 *          without exposing opaque audit identifiers in the note board.
 * CHANGELOG: v2.21.0-FOUR-SOURCE-ACTIVITY-CERT proves
 *          independently verified comment, lifecycle, decision and file
 *          events render chronologically, and links remain in exact-task
 *          approval and attachment workflows without new IAM.
 * CHANGELOG: v2.20.0-AUTHORITATIVE-TASK-ACTIVITY-CERT certifies
 *          source-verified task lifecycle events and comment activity appear
 *          newest-first, and the unified Activity & discussion navigation
 *          preserves separately authorized decisions and evidence links.
 * CHANGELOG: v2.19.0-TOP-LEVEL-DISCUSSIONS-CERT certifies
 *          the primary Discussions tab opens an EOS-verified task chooser
 *          without rendering the work dashboard, and selected task comments
 *          remain independently scoped to their canonical project/task.
 * CHANGELOG: v2.18.0-ONE-CLICK-DISCUSSION-CERT verifies
 *          Discuss exposes EOS source-backed comments immediately with the
 *          composer closed, and Write update opens the safe Markdown editor
 *          only on explicit request; retains original draft/readback checks.
 * CHANGELOG: v2.17.0-ON-DEMAND-COMMENT-HISTORY-CERT verifies
 *          comments remain collapsed initially, open on explicit request,
 *          and hide again without losing the independently verified source.
 * CHANGELOG: v2.16.1-ASSIGNMENT-OVERVIEW-CERT updates
 *          owner/department assignment readback assertions for the intentional
 *          source-honest Overview label; verifies the ID is retained in the
 *          title attribute and not exposed as primary display text.
 * CHANGELOG: v2.16.0-OVERVIEW-READABILITY-CERT verifies
 *          overview renders readable source-owned actor names and avoids
 *          publishing unverified department IDs as user-facing labels.
 * CHANGELOG: v2.15.0-PROJECT-SUMMARY-503-ISOLATION-CERT verifies
 *          the independently authorized project page remains operational
 *          when summary returns HTTP 503 before or after its list readback;
 *          foreign-tenant summary rejection remains fail-closed.
 * CHANGELOG: v2.14.0-SAFE-DISCUSSION-MARKDOWN-CERT verifies
 *          literal pasted Markdown renders in live comment preview, escaped
 *          untrusted HTML remains text, and history formats EOS-owned bodies
 *          without changing the stored comment or its authority.
 * CHANGELOG: v2.13.0-FOCUSED-ACTION-NAMED-MEMBER-CERT certifies
 *          focused discussion replacing the long work table and composer
 *          preceding comment history; verifies sourced participant names and
 *          unknown-name fallback without deriving identity from opaque IDs.
 * CHANGELOG: v2.12.1-PARENT-BOUND-CHECKLIST-CERT certifies
 *          Add checklist step selects the EOS-verified active parent before
 *          submitting the existing idempotent task create command.
 * CHANGELOG: v2.12.0-PERSISTED-TODO-CHECKLIST-CERT proves To-do checkboxes
 *          cannot assert Done optimistically, require conscious confirmation,
 *          and reflect the revisioned EOS transition only after fresh source
 *          readback; preserves existing tenant and command scope.
 * CHANGELOG: v2.11.0-LIFECYCLE-AUDIT-VISUAL-CERT proves status
 *          visualization changes only after EOS readback, actionable bar
 *          filters and newest-revision-first audit presentation.
 * CHANGELOG: v2.10.0-OPERATIONAL-WORK-QUEUE-CERT certifies distinct EOS subtask and
 *          milestone commands, active parent selection, and current-page queue
 *          search/filter over exact-scope verified task readbacks.
 * CHANGELOG: v2.9.0-INDEXED-OWNER-PAGINATION-CERT verifies owner-filtered EOS endpoint and source-bound count/pagination, never client-only filtering across 500+ projects.
 * CHANGELOG: v2.27.3-VALID-TEMPLATE-READBACK-FIXTURE certifies owner-only filtering against the authoritative current registry page, with no participant IAM fallback or fake total counts; independently keeps participant navigation for explicitly admitted principals.
 * CHANGELOG: v2.27.3-VALID-TEMPLATE-READBACK-FIXTURE certifies author-selected colour in note command, independently verified EOS readback and sticky-board presentation without project mutation.
 * CHANGELOG: v2.27.3-VALID-TEMPLATE-READBACK-FIXTURE verifies human creator, owner and audit actor display names are backed by the exact source identity, while preserving immutable command and event IDs.
 * CHANGELOG: v2.27.3-VALID-TEMPLATE-READBACK-FIXTURE shows tenant-bound human owner names while submitting immutable principal IDs, and denies fabricated or incomplete name projections without allowing assignment.
 * CHANGELOG: v2.27.3-VALID-TEMPLATE-READBACK-FIXTURE certifies selected-project task-first view, full-width workspace, separate overview, settings, notes and audit navigation without weakening source checks.
 * CHANGELOG: v2.27.3-VALID-TEMPLATE-READBACK-FIXTURE proves a
 *            Daily Attention participant-focused project opens the separately
 *            authorized Assigned Projects UI without owner-list side effects.
 * CHANGELOG: v2.27.3-VALID-TEMPLATE-READBACK-FIXTURE adds in-place task
 *            editing and updated revision readback without changing project
 *            Planned status, task graph or tenant authorization scope.
 * CHANGELOG: v2.27.3-VALID-TEMPLATE-READBACK-FIXTURE certifies task creation, verified
 *            EOS readback, revision-guarded transition and unmodified Planned
 *            project state in the existing authenticated client harness.
 * CHANGELOG: v2.27.3-VALID-TEMPLATE-READBACK-FIXTURE waits for the committed note row
 *            instead of a transient draft textarea with the same source text.
 * CHANGELOG: v2.27.3-VALID-TEMPLATE-READBACK-FIXTURE certifies source-backed project note
 *            creation/readback without modifying Planned status, propagating
 *            current principal/tenant scope or granting participant authority.
 * CHANGELOG: v2.27.3-VALID-TEMPLATE-READBACK-FIXTURE certifies server-side exact-tenant status filtering,
 *            one-page post-filter readback and no client-invented rows.
 * CHANGELOG: v2.27.3-VALID-TEMPLATE-READBACK-FIXTURE tests server-verified page metadata, source
 *            pagination beyond the first page, and denial of phantom next pages.
 * CHANGELOG: v2.27.3-VALID-TEMPLATE-READBACK-FIXTURE proves navigation
 *            beyond 100 same-tenant projects and source-verified status graph
 *            counts while retaining the existing lifecycle assertions.
 *            v1.6.3-RUNNER-PORTABLE-CSS-CERT resolves the source stylesheet
 *            from Vitest's project root rather than transformed import.meta.url;
 *            retains exact semantic label selectors and all assertions.
 *            v1.6.2-ACTUAL-ACCOUNTABILITY-STYLE-HOOK-CERT ensures the rendered
 *            project accountability form is actually targeted by the
 *            contrasting semantic stylesheet; protects against dead selectors.
 *            v1.6.1-EXPLICIT-ASSIGNMENT-SOURCE-STATE-CERT certifies user-visible current
 *            directory counts and fail-closed empty selectors without
 *            inventing principal, department or a completed assignment.
 *            v1.6.0-GOVERNED-ACCOUNTABILITY-CLIENT-CERT covers source-backed owner/department selection,
 *            independently authorized department creation and audited CAS
 *            assignment with fresh list and detail readback.
 * v1.5.0-SOURCE-VERIFIED-AUTO-CODE-CERT verifies
 *            one-click legacy project-code generation, revision guarding,
 *            independent EOS list/detail confirmation, and no duplicate action.
 * CHANGELOG: v1.4.0-NATIVE-CALENDAR-EXECUTION-CERT verifies
 *            visible Start and Target native calendar picker actions
 *            and ISO date-only values without premature EOS mutation.
 * CHANGELOG: v1.3.0-FLUID-PROJECT-DETAIL-PRESENTATION-CERT proves
 *            full-width list, selected detail layout, safe formatted scope
 *            in both collapsed and expanded modes, and sourced null values.
 * CHANGELOG: v1.2.0-STRATEGY-HANDOFF-SCOPE-CERT proves Strategy focus requires an
 *            authenticated exact-tenant list before detail readback and
 *            rejects absent IDs without issuing any project mutations.
 * CHANGELOG: v1.1.1-EXACT-SCOPE-CREATE-UPDATE-ARCHIVE-CERT covers full synthetic lifecycle and rejects stale or foreign envelopes; v1.0.1 covers create replay and denial.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
 * SECURITY / PRIVACY POSTURE: Synthetic test identities only; no credential or production data.
 * TENANT BOUNDARY: Tests assert selected tenant/principal envelopes and stale response isolation; not a live EOS isolation certificate.
 * AUTHORITY BOUNDARY: HTTP is mocked; no IAM or entitlement grant is made or proven.
 * FINANCIAL AUTHORITY BOUNDARY: No financial command is exercised.
 */
import React from 'react';
import { within, act, cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

const api = vi.hoisted(() => ({ get: vi.fn(), post: vi.fn(), patch: vi.fn() }));
vi.mock('../../services/api.js', () => ({ default: api }));

import ProjectsWorkspace from '../../components/workspaces/ProjectsWorkspace.jsx';
import ProjectWorkRowActions from '../../components/workspaces/ProjectWorkRowActions.jsx';
import ProjectWorkRow from '../../components/workspaces/ProjectWorkRow.jsx';
import ProjectTaskAttachmentsPanel from '../../components/workspaces/ProjectTaskAttachmentsPanel.jsx';

const TENANT = 'projects-cert-tenant';
const PRINCIPAL = 'projects-cert-principal';
const PROJECT_ID = `prj-${'a'.repeat(48)}`;
const project = (overrides = {}) => ({
  project_id: PROJECT_ID,
  tenant_id: TENANT,
  name: 'Persisted roadmap',
  code: 'ROADMAP',
  summary: 'Source-confirmed project',
  status: 'planned',
  created_by_principal_id: PRINCIPAL,
  revision: 1,
  created_at: '2026-11-16T12:00:00+00:00',
  updated_at: '2026-11-16T12:00:00+00:00',
  archived_at: null,
  target_date: null,
  ...overrides,
});
const event = (type, revision, tenantId = TENANT, projectId = PROJECT_ID) => ({
  tenant_id: tenantId,
  event_id: `evt-${type}-${revision}`,
  project_id: projectId,
  event_type: type,
  actor_principal_id: PRINCIPAL,
  revision,
  occurred_at: `2026-11-16T12:0${Math.min(revision, 9)}:00+00:00`,
});
const result = (value, events = [event('PROJECT_CREATED', value.revision)]) => ({
  schema: 'WILSY-PROJECT-RESULT/V1',
  tenant_id: value.tenant_id,
  principal_id: PRINCIPAL,
  project: value,
  events,
  actor_profiles: Object.fromEntries(
    [...new Set([value.created_by_principal_id, value.owner_principal_id,
      ...events.map(entry => entry.actor_principal_id)].filter(Boolean))]
      .map(id => [id, {
        first_name: id === PRINCIPAL ? 'Verified' : 'Assigned',
        last_name: id === PRINCIPAL ? 'Creator' : 'Owner',
      }]),
  ),
  authority: { source: 'PYTHON_EOS_PROJECT_REGISTRY', financial_execution: false },
});
const list = (items, tenantId = TENANT, principalId = PRINCIPAL) => ({
  schema: 'WILSY-PROJECT-LIST/V1', tenant_id: tenantId, principal_id: principalId, items,
  limit: 100, offset: 0,
});
const summary = (items, tenantId = TENANT, principalId = PRINCIPAL) => {
  const counts = { total: items.length, active: 0, planned: 0, on_hold: 0, done: 0, cancelled: 0 };
  for (const item of items) if (!item.archived_at) counts[item.status] += 1;
  return { schema: 'WILSY-PROJECT-SUMMARY/V1', tenant_id: tenantId, principal_id: principalId, counts };
};

// Synthetic EOS permission fixture: never a real grant or authenticated claim.
const mockProjectGet = handler => api.get.mockImplementation((path, ...args) => {
  if (typeof path === 'string' && path.endsWith('/task-action-capabilities')) {
    const id = path.split('/')[2];
    return Promise.resolve({ data: {
      schema: 'WILSY-PROJECT-TASK-ACTION-CAPABILITIES/V1',
      tenant_id: TENANT, principal_id: PRINCIPAL, project_id: id,
      can_start: true, can_complete: true, can_block: true,
      can_cancel: true, can_assign: true, can_edit: true,
    } });
  }
  return handler(path, ...args);
});

beforeEach(() => {
  vi.clearAllMocks();
  let keySequence = 0;
  vi.stubGlobal('crypto', { randomUUID: vi.fn(() => `stable-project-key-${++keySequence}`) });
  mockProjectGet(async (path) => {
    if (path === '/projects') return { data: list([]) };
    if (path === '/projects/summary') return { data: summary([]) };
    throw new Error(`Unexpected project GET ${path}`);
  });
});

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

describe('Free-tier Projects read admission order', () => {
  it('does not issue an optional summary transaction while the authorized list is pending', async () => {
    let resolveList;
    const pendingList = new Promise(resolve => { resolveList = resolve; });
    api.get.mockImplementation(path => {
      if (path === '/projects') return pendingList;
      if (path === '/projects/summary') return Promise.resolve({ data: summary([]) });
      throw new Error('Unexpected read: ' + path);
    });
    render(<ProjectsWorkspace tenantId={TENANT} principalId={PRINCIPAL}
      sessionScope="list-first-free-tier-cert"/>);
    await waitFor(() => expect(api.get.mock.calls.filter(([path]) => path === '/projects')).toHaveLength(1));
    expect(api.get.mock.calls.filter(([path]) => path === '/projects/summary')).toHaveLength(0);
    resolveList({ data: list([]) });
    await waitFor(() => expect(api.get.mock.calls.filter(([path]) => path === '/projects/summary')).toHaveLength(1));
    expect(api.get.mock.calls.filter(([path]) => path === '/projects')).toHaveLength(1);
  });
});

describe('Project task attachment source and contributor authority boundary', () => {
  it('reports exact EOS attachment failure without sending owner into unverified People', async () => {
    const taskId = 'ptk-' + 'f'.repeat(48);
    const openPeople = vi.fn();
    api.get.mockRejectedValue({
      response: { status: 503, data: { detail: 'PROJECT_ATTACHMENT_SOURCE_UNAVAILABLE' } },
    });
    render(<ProjectTaskAttachmentsPanel
      tenantId={TENANT} principalId={PRINCIPAL} projectId={PROJECT_ID}
      taskId={taskId} tenantHeaders={{ 'X-Tenant-ID': TENANT }}
      participantMode={false} onManageContributors={openPeople}
      onClose={vi.fn()}/>);
    await waitFor(() => expect(screen.getByRole('alert')).toHaveTextContent(
      /task attachment source is unavailable \(HTTP 503\) · EOS PROJECT_ATTACHMENT_SOURCE_UNAVAILABLE/i,
    ));
    expect(screen.getByRole('heading', { name: 'Files & evidence' })).toBeVisible();
    expect(screen.queryByLabelText('Project attachment file')).not.toBeInTheDocument();
    expect(screen.getByRole('button', {
      name: 'Check contributor access',
    })).toBeDisabled();
    expect(openPeople).not.toHaveBeenCalled();
    expect(api.post).not.toHaveBeenCalled();
    expect(api.get).toHaveBeenCalledWith(
      `/projects/${PROJECT_ID}/tasks/${taskId}/attachments?limit=50&offset=0`,
      expect.objectContaining({ headers: { 'X-Tenant-ID': TENANT } }),
    );
  });

  it('checks eligible-member and participant sources before leaving an authorized task', async () => {
    const taskId = 'ptk-' + 'f'.repeat(48);
    const openPeople = vi.fn();
    api.get.mockImplementation(async path => {
      if (path === `/projects/${PROJECT_ID}/tasks/${taskId}/attachments?limit=50&offset=0`)
        return { data: {
          schema: 'WILSY-PROJECT-ATTACHMENT-LIST/V1',
          tenant_id: TENANT, principal_id: PRINCIPAL, project_id: PROJECT_ID,
          task_id: taskId, items: [], limit: 50, offset: 0, has_more: false, next_offset: null,
        } };
      if (path === `/projects/${PROJECT_ID}/participants?limit=50&offset=0`)
        return { data: {
          schema: 'WILSY-PROJECT-PARTICIPANT-LIST/V1', tenant_id: TENANT,
          principal_id: PRINCIPAL, project_id: PROJECT_ID, items: [],
          limit: 50, offset: 0, has_more: false, next_offset: null,
        } };
      if (path === `/projects/${PROJECT_ID}/participant-options?limit=50&offset=0`) {
        const denied = new Error('Forbidden');
        denied.response = { status: 403, data: { detail: 'PROJECT_PARTICIPANT_DIRECTORY_DENIED' } };
        throw denied;
      }
      throw new Error('Unexpected source ' + path);
    });
    render(<ProjectTaskAttachmentsPanel tenantId={TENANT} principalId={PRINCIPAL}
      projectId={PROJECT_ID} taskId={taskId} tenantHeaders={{ 'X-Tenant-ID': TENANT }}
      participantMode={false} onManageContributors={openPeople} onClose={vi.fn()}/>);
    expect(await screen.findByText(/No files attached yet/)).toBeVisible();
    fireEvent.click(screen.getByRole('button', {
      name: 'Check contributor access',
    }));
    await waitFor(() => expect(screen.getByRole('alert')).toHaveTextContent(
      'Eligible tenant member directory: denied (HTTP 403) · EOS PROJECT_PARTICIPANT_DIRECTORY_DENIED',
    ));
    expect(screen.getByRole('alert')).toHaveTextContent('Project People was not opened');
    expect(openPeople).not.toHaveBeenCalled();
    expect(api.post).not.toHaveBeenCalled();
  });

  it('navigates only after both People sources return verified exact-project contracts', async () => {
    const taskId = 'ptk-' + 'f'.repeat(48);
    const openPeople = vi.fn();
    api.get.mockImplementation(async path => {
      if (path === `/projects/${PROJECT_ID}/tasks/${taskId}/attachments?limit=50&offset=0`)
        return { data: {
          schema: 'WILSY-PROJECT-ATTACHMENT-LIST/V1', tenant_id: TENANT,
          principal_id: PRINCIPAL, project_id: PROJECT_ID,
          task_id: taskId, items: [], limit: 50, offset: 0, has_more: false, next_offset: null,
        } };
      if (path === `/projects/${PROJECT_ID}/participants?limit=50&offset=0`)
        return { data: {
          schema: 'WILSY-PROJECT-PARTICIPANT-LIST/V1', tenant_id: TENANT,
          principal_id: PRINCIPAL, project_id: PROJECT_ID,
          items: [], limit: 50, offset: 0, has_more: false, next_offset: null,
        } };
      if (path === `/projects/${PROJECT_ID}/participant-options?limit=50&offset=0`)
        return { data: {
          schema: 'WILSY-PROJECT-PARTICIPANT-OPTIONS/V1', tenant_id: TENANT,
          principal_id: PRINCIPAL, project_id: PROJECT_ID,
          items: [], limit: 50, offset: 0, has_more: false, next_offset: null,
        } };
      throw new Error('Unexpected source ' + path);
    });
    render(<ProjectTaskAttachmentsPanel tenantId={TENANT} principalId={PRINCIPAL}
      projectId={PROJECT_ID} taskId={taskId} tenantHeaders={{ 'X-Tenant-ID': TENANT }}
      participantMode={false} onManageContributors={openPeople} onClose={vi.fn()}/>);
    expect(await screen.findByText(/No files attached yet/)).toBeVisible();
    fireEvent.click(screen.getByRole('button', {
      name: 'Check contributor access',
    }));
    await waitFor(() => expect(openPeople).toHaveBeenCalledTimes(1));
    expect(api.post).not.toHaveBeenCalled();
  });

  it('shows source-verified quarantine upload only to admitted project contributors', async () => {
    const taskId = 'ptk-' + 'f'.repeat(48);
    api.get.mockResolvedValue({ data: {
      schema: 'WILSY-PROJECT-ATTACHMENT-LIST/V1',
      tenant_id: TENANT, principal_id: PRINCIPAL, project_id: PROJECT_ID,
      task_id: taskId, items: [], limit: 50, offset: 0,
      has_more: false, next_offset: null,
    } });
    render(<ProjectTaskAttachmentsPanel
      tenantId={TENANT} principalId={PRINCIPAL} projectId={PROJECT_ID}
      taskId={taskId} tenantHeaders={{ 'X-Tenant-ID': TENANT }}
      participantMode={true} onClose={vi.fn()}/>);
    expect(await screen.findByRole('button', { name: 'Browse files' })).toBeVisible();
    expect(screen.getByText(/No files attached yet/)).toBeVisible();
    expect(api.post).not.toHaveBeenCalled();
  });
});

describe('ProjectsWorkspace source-backed lifecycle', () => {

  it('renders one primary work action and a keyboard-dismissable contextual action sheet', () => {
    const onTransition = vi.fn();
    const onComplete = vi.fn();
    const onEdit = vi.fn();
    const onAttachments = vi.fn();
    const onApprovals = vi.fn();
    const onActivity = vi.fn();
    const item = { task_id: 'ptk-' + 'c'.repeat(48),
      title: 'Validate deliverable', status: 'TODO' };
    const handlers = { item, busy: false, onTransition, onComplete,
      onAssign: vi.fn(), onEdit, onAttachments, onApprovals, onActivity,
      canStart: true, canComplete: true, canBlock: true, canCancel: true,
      canAssign: true, canEdit: true, canAttachments: true,
      canApprovals: true, canActivity: true };
    const view = render(<ProjectWorkRowActions {...handlers}/>);
    expect(screen.getByRole('button', { name: 'Start: Validate deliverable' })).toBeVisible();
    expect(screen.queryByRole('menuitem', { name: 'Mark blocked' })).not.toBeInTheDocument();
    const trigger = screen.getByRole('button', { name: 'More actions for Validate deliverable' });
    fireEvent.click(trigger);
    const actionDialog = screen.getByRole('menu', { name: 'Actions for Validate deliverable' });
    expect(actionDialog).toBeVisible();
    expect(screen.getByRole('menuitem', { name: 'Mark blocked' })).toHaveFocus();
    fireEvent.keyDown(actionDialog, { key: 'ArrowDown' });
    expect(screen.getByRole('menuitem', { name: 'Assign' })).toHaveFocus();
    fireEvent.keyDown(actionDialog, { key: 'End' });
    expect(screen.getByRole('button', { name: 'Close actions' })).toHaveFocus();
    fireEvent.keyDown(actionDialog, { key: 'Home' });
    expect(screen.getByRole('menuitem', { name: 'Mark blocked' })).toHaveFocus();
    fireEvent.keyDown(window, { key: 'Escape' });
    expect(screen.queryByRole('menu', { name: 'Actions for Validate deliverable' })).not.toBeInTheDocument();
    expect(trigger).toHaveFocus();
    fireEvent.click(trigger);
    fireEvent.click(screen.getByRole('menuitem', { name: 'Mark blocked' }));
    expect(onTransition).toHaveBeenCalledWith(item, 'BLOCKED');
    expect(screen.queryByRole('menu', { name: 'Actions for Validate deliverable' })).not.toBeInTheDocument();
    view.rerender(<ProjectWorkRowActions {...handlers}
      item={{ ...item, status: 'IN_PROGRESS' }}/>);
    fireEvent.click(screen.getByRole('button', { name: 'Complete: Validate deliverable' }));
    expect(onComplete).toHaveBeenCalledWith({ ...item, status: 'IN_PROGRESS' });
    fireEvent.click(trigger);
    fireEvent.click(screen.getByRole('menuitem', { name: 'Cancel work' }));
    expect(screen.queryByRole('menu', { name: 'Actions for Validate deliverable' }))
      .not.toBeInTheDocument();
    const confirmation = screen.getByRole('dialog', {
      name: 'Confirm cancellation for Validate deliverable',
    });
    expect(confirmation).toBeVisible();
    expect(within(confirmation).getByRole('button', { name: 'Keep work' })).toHaveFocus();
    expect(onTransition).toHaveBeenCalledTimes(1);
    fireEvent.click(within(confirmation).getByRole('button', { name: 'Confirm cancellation' }));
    expect(onTransition).toHaveBeenCalledWith({ ...item, status: 'IN_PROGRESS' }, 'CANCELLED');
    expect(onComplete).toHaveBeenCalledTimes(1);
  });



  it('assigns multiple selected tasks only through independently verified EOS commands', async () => {
    const storedProject = project();
    const base = {
      schema: 'wilsy.project.task.v1', tenant_id: TENANT, project_id: PROJECT_ID,
      kind: 'TASK', parent_task_id: null, description: '', status: 'TODO',
      assignee_principal_id: null, due_date: null, depends_on: [],
      created_by_principal_id: PRINCIPAL, updated_by_principal_id: PRINCIPAL,
      created_at: '2026-11-23T08:00:00+00:00',
      updated_at: '2026-11-23T08:00:00+00:00',
      revision: 1, fingerprint: 'a'.repeat(128),
    };
    let tasks = [
      { ...base, task_id: 'ptk-' + 'a'.repeat(48), title: 'First accountable task' },
      { ...base, task_id: 'ptk-' + 'b'.repeat(48), title: 'Second accountable task' },
    ];
    let taskListReads = 0;
    mockProjectGet(async path => {
      if (path === '/projects') return { data: list([storedProject]) };
      if (path === '/projects/summary') return { data: summary([storedProject]) };
      if (path === `/projects/${PROJECT_ID}`) return { data: result(storedProject) };
      if (path === `/projects/${PROJECT_ID}/tasks?limit=50&offset=0`) {
        taskListReads += 1;
        return { data: {
          schema: 'WILSY-PROJECT-TASK-LIST/V1',
          tenant_id: TENANT, principal_id: PRINCIPAL, project_id: PROJECT_ID,
          items: tasks, limit: 50, offset: 0, has_more: false, next_offset: null,
        } };
      }
      if (path === `/projects/${PROJECT_ID}/participants?limit=100&offset=0`) {
        return { data: {
          schema: 'WILSY-PROJECT-PARTICIPANT-LIST/V1',
          tenant_id: TENANT, principal_id: PRINCIPAL, project_id: PROJECT_ID,
          items: [{
            principal_id: PRINCIPAL, tenant_id: TENANT, project_id: PROJECT_ID,
            first_name: 'Verified', last_name: 'Contributor',
            state: 'ACTIVE', role: 'CONTRIBUTOR',
          }],
          limit: 100, offset: 0, has_more: false, next_offset: null,
        } };
      }
      throw new Error('Unexpected source ' + path);
    });
    api.patch.mockImplementation(async (path, body, options) => {
      expect(path).toMatch(new RegExp('^/projects/.+/tasks/ptk-'));
      expect(options.headers['X-Tenant-ID']).toBe(TENANT);
      expect(options.headers['Idempotency-Key']).toBeTruthy();
      const id = path.split('/').at(-1);
      const original = tasks.find(task => task.task_id === id);
      expect(original).toBeDefined();
      expect(body.expected_revision).toBe(original.revision);
      expect(body.assignee_principal_id).toBe(PRINCIPAL);
      expect(body.title).toBe(original.title);
      expect(body.due_date).toBe(original.due_date);
      const updated = { ...original, revision: original.revision + 1,
        fingerprint: 'b'.repeat(128), assignee_principal_id: PRINCIPAL };
      tasks = tasks.map(task => task.task_id === id ? updated : task);
      return { data: {
        schema: 'WILSY-PROJECT-TASK-RESULT/V1',
        tenant_id: TENANT, principal_id: PRINCIPAL,
        project_id: PROJECT_ID, task: updated,
      } };
    });
    render(<ProjectsWorkspace tenantId={TENANT} principalId={PRINCIPAL}
      sessionScope="governed-batch-assign-cert"/>);
    fireEvent.click(await screen.findByRole('button', { name: /View project Persisted roadmap/ }));
    fireEvent.click(await screen.findByRole('checkbox', { name: 'Select First accountable task' }));
    fireEvent.click(screen.getByRole('checkbox', { name: 'Select Second accountable task' }));
    fireEvent.click(await screen.findByRole('button', { name: 'Assign selected…' }));
    const dialog = screen.getByRole('dialog', { name: 'Assign selected project tasks' });
    expect(api.patch).not.toHaveBeenCalled();
    fireEvent.change(within(dialog).getByRole('combobox', {
      name: 'Assign selected tasks to contributor',
    }), { target: { value: PRINCIPAL } });
    fireEvent.click(within(dialog).getByRole('checkbox', {
      name: /I confirm assignment to each selected task/,
    }));
    fireEvent.click(within(dialog).getByRole('button', {
      name: 'Apply individual assignments',
    }));
    await waitFor(() => expect(within(dialog).getByText(/2 of 2 independently verified/)).toBeVisible());
    expect(api.patch).toHaveBeenCalledTimes(2);
    expect(taskListReads).toBeGreaterThanOrEqual(4);
    expect(tasks.map(task => task.assignee_principal_id)).toEqual([PRINCIPAL, PRINCIPAL]);
    expect(tasks.every(task => task.status === 'TODO')).toBe(true);
    expect(api.post).not.toHaveBeenCalled();
  });

  it('uses compact work row structure without expanding secondary content', () => {
    const item = { task_id: 'ptk-' + 'f'.repeat(48),
      title: 'Compact deliverable', kind: 'TASK', status: 'TODO',
      parent_task_id: null, due_date: '2026-11-19', depends_on: [],
      assignee_principal_id: null, description: 'Long source-backed details' };
    const { container } = render(<table><tbody><ProjectWorkRow item={item}
      density="compact" todayISO="2026-11-19" capabilities={{}}
      onOpen={vi.fn()} onToggleSelect={vi.fn()}/></tbody></table>);
    const row = container.querySelector('tr[data-task-id]');
    expect(row).toHaveClass('h-11');
    expect(row.querySelector('details')).toBeNull();
    expect(row.querySelector('.hidden')).not.toBeNull();
    expect(screen.getByRole('button', { name: 'More actions for Compact deliverable' }))
      .toHaveClass('min-h-9');
  });

  it('renders due today, tomorrow and overdue without rewriting the source dates', () => {
    const dates = ['2026-11-19', '2026-11-20', '2026-11-17'];
    render(<table><tbody>{dates.map((dueDate, index) =>
      <ProjectWorkRow key={dueDate} item={{
        task_id: 'ptk-' + String(index + 1).repeat(48),
        title: 'Due phrase ' + (index + 1), kind: 'TASK', status: 'TODO',
        parent_task_id: null, due_date: dueDate, depends_on: [],
        assignee_principal_id: null, description: '',
      }} todayISO="2026-11-19" capabilities={{}}
      onOpen={vi.fn()} onToggleSelect={vi.fn()}/>)}</tbody></table>);
    expect(screen.getByText('Due today')).toHaveAttribute('title', dates[0]);
    expect(screen.getByText('Due tomorrow')).toHaveAttribute('title', dates[1]);
    expect(screen.getByText('Overdue 2 days')).toHaveAttribute('title', dates[2]);
  });

  it('shows a verified contributor identity marker without a backend ID', () => {
    const item = { task_id: 'ptk-' + 'f'.repeat(48),
      title: 'Named delivery', kind: 'TASK', status: 'IN_PROGRESS',
      parent_task_id: null, due_date: null, depends_on: [],
      assignee_principal_id: 'opaque-principal-123', description: '' };
    const { container } = render(<table><tbody><ProjectWorkRow item={item}
      todayISO="2026-11-19" assigneeName={() => 'Verified Contributor'}
      capabilities={{}} onToggleSelect={vi.fn()} onOpen={vi.fn()}
      onComplete={vi.fn()} onAssign={vi.fn()} onEdit={vi.fn()}
      onTransition={vi.fn()} onAttachments={vi.fn()} onApprovals={vi.fn()}
      onActivity={vi.fn()}/></tbody></table>);
    expect(container.querySelector('[data-assignee-avatar]')).toHaveTextContent('VC');
    expect(screen.getByText('Verified Contributor')).toBeVisible();
    expect(screen.queryByText('opaque-principal-123')).not.toBeInTheDocument();
  });

  it('fails closed when a reused Work Row receives an incomplete capability projection', () => {
    const item = { task_id: 'ptk-' + 'e'.repeat(48),
      title: 'Restricted source work', kind: 'TASK', status: 'TODO',
      parent_task_id: null, due_date: null, depends_on: [],
      assignee_principal_id: null, description: '' };
    const onAssign = vi.fn();
    render(<table><tbody><ProjectWorkRow item={item} todayISO="2026-11-19"
      assigneeName={() => 'Verified contributor'} capabilities={{}}
      onAssign={onAssign} onToggleSelect={vi.fn()} onOpen={vi.fn()}
      onComplete={vi.fn()} onEdit={vi.fn()} onTransition={vi.fn()}
      onAttachments={vi.fn()} onActivity={vi.fn()} onApprovals={vi.fn()}/></tbody></table>);
    expect(screen.queryByRole('button', { name: 'Assign: Restricted source work' }))
      .not.toBeInTheDocument();
    expect(screen.queryByRole('button', { name: 'Start: Restricted source work' }))
      .not.toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'More actions for Restricted source work' }))
      .toBeDisabled();
    expect(onAssign).not.toHaveBeenCalled();
  });

  it('denies every action by default for an unadmitted reusable Work Row caller', () => {
    const item = { task_id: 'ptk-' + 'e'.repeat(48),
      title: 'Unadmitted work', status: 'IN_PROGRESS' };
    const onTransition = vi.fn();
    render(<ProjectWorkRowActions item={item} busy={false}
      onTransition={onTransition} onComplete={vi.fn()}
      onEdit={vi.fn()} onAssign={vi.fn()} onActivity={vi.fn()}/>);
    expect(screen.queryByRole('button', { name: 'Complete: Unadmitted work' }))
      .not.toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'More actions for Unadmitted work' }))
      .toBeDisabled();
    expect(onTransition).not.toHaveBeenCalled();
  });

  it('hides actions explicitly disallowed by the caller without changing authority', () => {
    const item = { task_id: 'ptk-' + 'f'.repeat(48),
      title: 'Read-only work', status: 'IN_PROGRESS' };
    const onTransition = vi.fn();
    render(<ProjectWorkRowActions item={item} busy={false}
      onTransition={onTransition} onComplete={vi.fn()} onEdit={vi.fn()}
      onAttachments={vi.fn()} onActivity={vi.fn()} onApprovals={vi.fn()}
      canStart={false} canComplete={false} canBlock={false}
      canCancel={false} canAssign={false} canEdit={false}
      canAttachments={false} canApprovals={false} canActivity={true}/>);
    expect(screen.queryByRole('button', { name: 'Complete: Read-only work' }))
      .not.toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: 'More actions for Read-only work' }));
    const menu = screen.getByRole('menu', { name: 'Actions for Read-only work' });
    expect(within(menu).getByRole('menuitem', { name: 'Activity & discussion' }))
      .toBeVisible();
    expect(within(menu).queryByRole('menuitem', { name: 'Mark blocked' }))
      .not.toBeInTheDocument();
    expect(within(menu).queryByRole('menuitem', { name: 'Cancel work' }))
      .not.toBeInTheDocument();
    expect(within(menu).queryByRole('menuitem', { name: 'Edit' }))
      .not.toBeInTheDocument();
    expect(onTransition).not.toHaveBeenCalled();
  });

  it('dismisses the mobile work actions sheet without mutating work', () => {
    vi.stubGlobal('innerWidth', 390);
    const onTransition = vi.fn();
    const item = { task_id: 'ptk-' + 'd'.repeat(48),
      title: 'Mobile decision', status: 'IN_PROGRESS' };
    render(<ProjectWorkRowActions item={item} busy={false} onTransition={onTransition}
      onComplete={vi.fn()} onEdit={vi.fn()} onAttachments={vi.fn()}
      onApprovals={vi.fn()} onActivity={vi.fn()} canActivity={true}/>);
    const trigger = screen.getByRole('button', { name: 'More actions for Mobile decision' });
    fireEvent.click(trigger);
    const dialog = screen.getByRole('dialog', { name: 'Actions for Mobile decision' });
    expect(dialog).toBeVisible();
    expect(document.body.style.overflow).toBe('hidden');
    const grabber = dialog.querySelector('.touch-pan-y');
    expect(grabber).not.toBeNull();
    fireEvent.touchStart(grabber, { touches: [{ clientY: 80 }] });
    fireEvent.touchEnd(grabber, { changedTouches: [{ clientY: 185 }] });
    expect(screen.queryByRole('dialog', { name: 'Actions for Mobile decision' }))
      .not.toBeInTheDocument();
    expect(trigger).toHaveFocus();
    expect(document.body.style.overflow).not.toBe('hidden');
    expect(onTransition).not.toHaveBeenCalled();
  });

  it('uses exact EOS assignment capability rather than edit capability in the assignment sheet', async () => {
    const source = project();
    let task = { schema: 'wilsy.project.task.v1', tenant_id: TENANT,
      project_id: PROJECT_ID, task_id: 'ptk-' + 'a'.repeat(48),
      kind: 'TASK', parent_task_id: null, title: 'Assign independently',
      description: '', status: 'TODO', assignee_principal_id: null,
      due_date: null, depends_on: [], revision: 1, fingerprint: 'a'.repeat(128),
      created_by_principal_id: PRINCIPAL, updated_by_principal_id: PRINCIPAL,
      created_at: '2026-11-19T09:00:00+00:00',
      updated_at: '2026-11-19T09:00:00+00:00' };
    mockProjectGet(async path => {
      if (path === '/projects') return { data: list([source]) };
      if (path === '/projects/summary') return { data: summary([source]) };
      if (path === `/projects/${PROJECT_ID}`) return { data: result(source) };
      if (path === `/projects/${PROJECT_ID}/tasks?limit=50&offset=0`) return {
        data: { schema: 'WILSY-PROJECT-TASK-LIST/V1', tenant_id: TENANT,
          principal_id: PRINCIPAL, project_id: PROJECT_ID, items: [task],
          limit: 50, offset: 0, has_more: false, next_offset: null },
      };
      if (path === `/projects/${PROJECT_ID}/participants?limit=100&offset=0`) return {
        data: { schema: 'WILSY-PROJECT-PARTICIPANT-LIST/V1', tenant_id: TENANT,
          principal_id: PRINCIPAL, project_id: PROJECT_ID,
          items: [{ principal_id: PRINCIPAL, tenant_id: TENANT,
            project_id: PROJECT_ID, state: 'ACTIVE', role: 'CONTRIBUTOR',
            first_name: 'Verified', last_name: 'Contributor' }],
          limit: 100, offset: 0, has_more: false, next_offset: null },
      };
      throw new Error('Unexpected assignment source ' + path);
    });
    const original = api.get.getMockImplementation();
    api.get.mockImplementation((path, ...args) => path === `/projects/${PROJECT_ID}/task-action-capabilities`
      ? Promise.resolve({ data: {
        schema: 'WILSY-PROJECT-TASK-ACTION-CAPABILITIES/V1',
        tenant_id: TENANT, principal_id: PRINCIPAL, project_id: PROJECT_ID,
        can_start: false, can_complete: false, can_block: false,
        can_cancel: false, can_assign: true, can_edit: false,
      } }) : original(path, ...args));
    render(<ProjectsWorkspace tenantId={TENANT} principalId={PRINCIPAL}
      sessionScope="assign-not-edit-scope-cert"/>);
    fireEvent.click(await screen.findByRole('button', { name: /View project Persisted roadmap/ }));
    fireEvent.click(await screen.findByRole('button', { name: 'Assign: Assign independently' }));
    expect(await screen.findByRole('dialog', { name: 'Assign work' })).toBeVisible();
    fireEvent.change(screen.getByRole('combobox', { name: 'Reassign task' }), {
      target: { value: PRINCIPAL },
    });
    expect(screen.getByRole('button', { name: 'Save assignment' })).toBeEnabled();
    expect(screen.queryByRole('textbox', { name: 'Edit task title' })).not.toBeInTheDocument();
    expect(api.patch).not.toHaveBeenCalled();
    api.patch.mockImplementationOnce(async (path, body) => {
      expect(path).toBe(`/projects/${PROJECT_ID}/tasks/${task.task_id}`);
      expect(body).toEqual({ expected_revision: 1, title: 'Assign independently',
        description: '', due_date: null, assignee_principal_id: PRINCIPAL });
      task = { ...task, assignee_principal_id: PRINCIPAL, revision: 2,
        fingerprint: 'b'.repeat(128) };
      return { data: { schema: 'WILSY-PROJECT-TASK-RESULT/V1', tenant_id: TENANT,
        principal_id: PRINCIPAL, project_id: PROJECT_ID, task } };
    });
    fireEvent.click(screen.getByRole('button', { name: 'Save assignment' }));
    await waitFor(() => expect(api.patch).toHaveBeenCalledTimes(1));
    await waitFor(() => expect(screen.queryByRole('dialog', { name: 'Assign work' })).not.toBeInTheDocument());
    const assignedRow = await screen.findByRole('row', { name: /Assign independently/ });
    assignedRow.focus();
    fireEvent.keyDown(assignedRow, { key: 'Enter' });
    const verifiedDrawer = await screen.findByRole('dialog', { name: 'Work details: Assign independently' });
    await waitFor(() => expect(within(verifiedDrawer).getAllByText('Verified Contributor').length).toBeGreaterThan(0));
  });

  it('filters current-page project work to the exact current assignee without a write', async () => {
    const source = project();
    const base = {
      schema: 'wilsy.project.task.v1', tenant_id: TENANT, project_id: PROJECT_ID,
      kind: 'TASK', parent_task_id: null, description: '', status: 'TODO',
      due_date: null, depends_on: [], revision: 1, fingerprint: 'a'.repeat(128),
      created_by_principal_id: PRINCIPAL, updated_by_principal_id: PRINCIPAL,
      created_at: '2026-11-19T09:00:00+00:00',
      updated_at: '2026-11-19T09:00:00+00:00',
    };
    const mine = { ...base, task_id: 'ptk-' + 'a'.repeat(48),
      title: 'My accountable delivery', assignee_principal_id: PRINCIPAL };
    const someoneElse = { ...base, task_id: 'ptk-' + 'b'.repeat(48),
      title: 'Other contributor delivery', assignee_principal_id: 'other-principal' };
    mockProjectGet(async path => {
      if (path === '/projects') return { data: list([source]) };
      if (path === '/projects/summary') return { data: summary([source]) };
      if (path === `/projects/${PROJECT_ID}`) return { data: result(source) };
      if (path === `/projects/${PROJECT_ID}/tasks?limit=50&offset=0`) return {
        data: { schema: 'WILSY-PROJECT-TASK-LIST/V1', tenant_id: TENANT,
          principal_id: PRINCIPAL, project_id: PROJECT_ID, items: [mine, someoneElse],
          limit: 50, offset: 0, has_more: false, next_offset: null },
      };
      if (path === `/projects/${PROJECT_ID}/participants?limit=100&offset=0`) return {
        data: { schema: 'WILSY-PROJECT-PARTICIPANT-LIST/V1', tenant_id: TENANT,
          principal_id: PRINCIPAL, project_id: PROJECT_ID, items: [],
          limit: 100, offset: 0, has_more: false, next_offset: null },
      };
      throw new Error('Unexpected read in current-assignee certificate ' + path);
    });
    render(<ProjectsWorkspace tenantId={TENANT} principalId={PRINCIPAL}
      sessionScope="project-my-work-page-cert"/>);
    fireEvent.click(await screen.findByRole('button', { name: /View project Persisted roadmap/ }));
    const work = await screen.findByRole('region', { name: 'Verified project tasks' });
    const rows = [...work.querySelectorAll('tbody tr[data-task-id]')];
    expect(rows).toHaveLength(2);
    rows[0].focus();
    fireEvent.keyDown(rows[0], { key: 'j' });
    expect(rows[1]).toHaveFocus();
    fireEvent.keyDown(rows[1], { key: 'k' });
    expect(rows[0]).toHaveFocus();
    fireEvent.keyDown(rows[0], { key: 'c' });
    expect(screen.queryByRole('dialog', { name: 'Confirm verified task completion' }))
      .not.toBeInTheDocument();
    fireEvent.keyDown(rows[0], { key: 'a' });
    expect(await screen.findByRole('dialog', { name: 'Assign work' })).toBeVisible();
    expect(screen.getByRole('combobox', { name: 'Reassign task' })).toBeVisible();
    expect(screen.queryByRole('textbox', { name: 'Edit task title' })).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: 'Cancel edit' }));
    fireEvent.click(screen.getByRole('button', { name: 'Reassign: My accountable delivery' }));
    expect(await screen.findByRole('dialog', { name: 'Assign work' })).toBeVisible();
    expect(screen.getByRole('button', { name: 'Save assignment' })).toBeDisabled();
    fireEvent.click(screen.getByRole('button', { name: 'Cancel edit' }));
    expect(within(work).getByText('My accountable delivery')).toBeVisible();
    expect(within(work).getByText('Other contributor delivery')).toBeVisible();
    fireEvent.click(screen.getByRole('checkbox', { name: 'Select My accountable delivery' }));
    expect(screen.getByRole('checkbox', { name: 'Select My accountable delivery' })).toBeChecked();
    fireEvent.click(screen.getByText(/Work filters, grouping and sorting/));
    fireEvent.change(screen.getByRole('combobox', { name: 'Work row density' }), {
      target: { value: 'compact' },
    });
    expect(work.querySelector('tr[data-task-id]')).toHaveClass('h-11');
    fireEvent.click(screen.getByRole('checkbox', { name: 'Select all visible work' }));
    expect(screen.getByRole('checkbox', { name: 'Select Other contributor delivery' })).toBeChecked();
    expect(screen.getByText(/2 selected · verified current EOS batch/)).toBeVisible();
    fireEvent.click(screen.getByRole('checkbox', { name: 'Select all visible work' }));
    expect(screen.getByRole('checkbox', { name: 'Select My accountable delivery' })).not.toBeChecked();
    fireEvent.change(screen.getByRole('combobox', { name: 'Work row density' }), {
      target: { value: 'comfortable' },
    });
    expect(work.querySelector('tr[data-task-id]')).toHaveClass('h-14');
    fireEvent.click(screen.getByRole('button', { name: 'My work on this page' }));
    expect(within(work).getByText('My accountable delivery')).toBeVisible();
    expect(within(work).queryByText('Other contributor delivery')).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: 'All work on this page' }));
    expect(within(work).getByText('Other contributor delivery')).toBeVisible();
    fireEvent.change(screen.getByRole('combobox', { name: 'Group project work' }), {
      target: { value: 'STATUS' },
    });
    expect(within(work).getByText('To do · 2 on this page')).toBeVisible();
    expect(work.querySelectorAll('tr[data-task-id]')).toHaveLength(2);
    fireEvent.change(screen.getByRole('combobox', { name: 'Group project work' }), {
      target: { value: 'NONE' },
    });
    expect(within(work).queryByText('To do · 2 on this page')).not.toBeInTheDocument();
    const formerTransport = api.get.getMockImplementation();
    api.get.mockImplementation((path, ...args) =>
      typeof path === 'string' && path.endsWith('/task-action-capabilities')
        ? Promise.reject({ response: { status: 403 } }) : formerTransport(path, ...args));
    fireEvent.click(screen.getByRole('button', { name: 'Refresh work' }));
    expect(await screen.findByText(/Project work is read-only/)).toBeVisible();
    expect(within(work).getByText('My accountable delivery')).toBeVisible();
    expect(within(work).queryByRole('button', { name: 'Start: My accountable delivery' }))
      .not.toBeInTheDocument();
    expect(within(work).queryByRole('button', { name: 'Reassign: My accountable delivery' }))
      .not.toBeInTheDocument();
    expect(api.post).not.toHaveBeenCalled();
    expect(api.patch).not.toHaveBeenCalled();
  });

  it('filters authorized owned projects without calling participant IAM or changing records', async () => {
    const owned = project({
      project_id: PROJECT_ID, name: 'Owned platform programme',
      owner_principal_id: PRINCIPAL, status: 'active',
    });
    const another = project({
      project_id: 'prj-' + 'b'.repeat(48), name: 'Another team project',
      owner_principal_id: 'another-principal', code: 'OTHER',
    });
    mockProjectGet(async path => {
      if (path === '/projects') return { data: list([owned, another]) };
      if (path === '/projects?limit=100&offset=0&owned_by_me=true') {
        return { data: list([owned]) };
      }
      if (path === '/projects/summary') return { data: summary([owned, another]) };
      throw new Error('Owner filter requested an unapproved source: ' + path);
    });
    render(<ProjectsWorkspace tenantId={TENANT} principalId={PRINCIPAL}
      sessionScope="explicit-owner-responsibility"/>);
    expect(await screen.findByText('2 shown · 2 verified')).toBeVisible();
    expect(screen.getByText('Owned platform programme')).toBeVisible();
    expect(screen.getByText('Another team project')).toBeVisible();
    fireEvent.click(screen.getByRole('button', { name: 'My owned projects' }));
    expect(await screen.findByText(/1 shown · 1 verified · EOS owner-filtered page/)).toBeVisible();
    expect(screen.getByText('Owned platform programme')).toBeVisible();
    expect(screen.queryByText('Another team project')).not.toBeInTheDocument();
    expect(api.get.mock.calls.some(([path]) =>
      path === '/projects?limit=100&offset=0&owned_by_me=true')).toBe(true);
    expect(api.get.mock.calls.some(([path]) => path.includes('/my-projects'))).toBe(false);
    expect(api.post).not.toHaveBeenCalled();
    expect(api.patch).not.toHaveBeenCalled();
    fireEvent.click(screen.getByRole('button', { name: 'My owned projects' }));
    expect(await screen.findByText('Another team project')).toBeVisible();
  });


  it('opens participant-focused project execution without owner registry reads', async () => {
    mockProjectGet(async path => {
      if (path === '/projects/my-projects?limit=50&offset=0') return { data: {
        schema: 'WILSY-PROJECT-MY-PROJECTS/V1',
        tenant_id: TENANT, principal_id: PRINCIPAL,
        items: [], limit: 50, offset: 0, has_more: false, next_offset: null,
      } };
      throw new Error('Unexpected owner-only project read: ' + path);
    });
    render(<ProjectsWorkspace tenantId={TENANT} principalId={PRINCIPAL}
      sessionScope="participant-attention-focus"
      focusAssignedProjectId={PROJECT_ID}/>);
    expect(await screen.findByRole('heading', { name: 'My assigned projects' })).toBeVisible();
    await waitFor(() => expect(api.get).toHaveBeenCalledWith(
      '/projects/my-projects?limit=50&offset=0',
      expect.any(Object),
    ));
    expect(api.get.mock.calls.some(([path]) => path === '/projects' || path === '/projects/summary')).toBe(false);
  });


  it('navigates 125 source-backed tenant projects without truncating to the first 100', async () => {
    const rows = Array.from({ length: 125 }, (_, index) => project({
      project_id: `prj-${(index + 1).toString(16).padStart(48, '0')}`,
      name: `Tenant project ${index + 1}`,
      code: `TEN-${index + 1}`,
    }));
    mockProjectGet(async (path) => {
      if (path === '/projects') return { data: { ...list(rows.slice(0, 100)), has_more: true, next_offset: 100 } };
      if (path === '/projects?limit=100&offset=100') return {
        data: { ...list(rows.slice(100)), limit: 100, offset: 100, has_more: false, next_offset: null },
      };
      if (path === '/projects/summary') return { data: summary(rows) };
      throw new Error(`Unexpected project GET ${path}`);
    });
    render(<ProjectsWorkspace tenantId={TENANT} principalId={PRINCIPAL}
      sessionScope="tenant-paging-cert" />);
    expect(await screen.findByText('100 shown · 100 verified')).toBeVisible();
    expect(screen.getByText(/Portfolio breakdown ·/)).toBeVisible();
    fireEvent.click(screen.getByText(/Portfolio breakdown ·/));
    expect(screen.getByRole('region', { name: 'Verified project status distribution' })).toBeVisible();
    expect(screen.getByRole('img', { name: 'Planned: 125 of 125 projects' })).toBeVisible();
    fireEvent.click(screen.getByRole('button', { name: 'Next' }));
    expect(await screen.findByText('25 shown · 25 verified')).toBeVisible();
    expect(screen.getByRole('button', { name: 'Previous' })).toBeEnabled();
    expect(screen.getByRole('button', { name: 'Next' })).toBeDisabled();
    expect(screen.getByRole('button', { name: /Tenant project 125/ })).toBeVisible();
    expect(api.get.mock.calls.some(([path]) => path === '/projects?limit=100&offset=100')).toBe(true);
  });

  it('does not invent a next page when exactly 100 projects exist', async () => {
    const rows = Array.from({ length: 100 }, (_, index) => project({
      project_id: `prj-${(index + 1).toString(16).padStart(48, '0')}`,
      name: `Exact-page project ${index + 1}`,
    }));
    mockProjectGet(async (path) => {
      if (path === '/projects') return {
        data: { ...list(rows), has_more: false, next_offset: null },
      };
      if (path === '/projects/summary') return { data: summary(rows) };
      throw new Error(`Unexpected project GET ${path}`);
    });
    render(<ProjectsWorkspace tenantId={TENANT} principalId={PRINCIPAL}
      sessionScope="exact-page-boundary-cert" />);
    expect(await screen.findByText('100 shown · 100 verified')).toBeVisible();
    expect(screen.queryByRole('button', { name: 'Next' })).not.toBeInTheDocument();
    expect(api.get.mock.calls.some(([path]) => path.includes('offset=100'))).toBe(false);
  });

  it('filters project status across the tenant at EOS before paging', async () => {
    const planned = project({ name: 'Unfiltered planned project' });
    const active = project({
      project_id: `prj-${'b'.repeat(48)}`,
      name: 'Verified active project',
      status: 'active',
    });
    mockProjectGet(async (path) => {
      if (path === '/projects') return {
        data: { ...list([planned, active]), has_more: false, next_offset: null },
      };
      if (path === '/projects?limit=100&offset=0&project_status=active') return {
        data: { ...list([active]), has_more: false, next_offset: null },
      };
      if (path === '/projects/summary') return { data: summary([planned, active]) };
      throw new Error(`Unexpected project GET ${path}`);
    });
    render(<ProjectsWorkspace tenantId={TENANT} principalId={PRINCIPAL}
      sessionScope="tenant-status-filter-cert" />);
    expect(await screen.findByText('2 shown · 2 verified')).toBeVisible();
    fireEvent.change(screen.getByRole('combobox', { name: 'Filter by status' }), {
      target: { value: 'active' },
    });
    expect(await screen.findByText('1 shown · 1 verified')).toBeVisible();
    expect(screen.getByRole('button', { name: /Verified active project/ })).toBeVisible();
    expect(screen.queryByRole('button', { name: /Unfiltered planned project/ })).not.toBeInTheDocument();
    expect(api.get.mock.calls.some(([path]) => path === '/projects?limit=100&offset=0&project_status=active')).toBe(true);
  });

  it('creates, transitions and edits source-backed project tasks without activating the project', async () => {
    const persisted = project();
    const taskId = `ptk-${'b'.repeat(48)}`;
    const originalTask = {
      schema: 'wilsy.project.task.v1', tenant_id: TENANT,
      project_id: PROJECT_ID, task_id: taskId, kind: 'TASK',
      parent_task_id: null, title: 'Build milestone execution', description: '',
      status: 'TODO', assignee_principal_id: null, due_date: null,
      depends_on: [], created_by_principal_id: PRINCIPAL,
      updated_by_principal_id: PRINCIPAL,
      created_at: '2026-11-18T06:00:00+00:00',
      updated_at: '2026-11-18T06:00:00+00:00',
      revision: 1, fingerprint: 'a'.repeat(128),
    };
    let work = [];
    let commands = 0;
    mockProjectGet(async path => {
      if (path === '/projects') return { data: list([persisted]) };
      if (path === '/projects/summary') return { data: summary([persisted]) };
      if (path === `/projects/${PROJECT_ID}`) return { data: result(persisted) };
      if (path === `/projects/${PROJECT_ID}/tasks?limit=50&offset=0`) return {
        data: {
          schema: 'WILSY-PROJECT-TASK-LIST/V1', tenant_id: TENANT,
          principal_id: PRINCIPAL, project_id: PROJECT_ID,
          limit: 50, offset: 0, items: work, has_more: false, next_offset: null,
        },
      };
      if (path === `/projects/${PROJECT_ID}/participants?limit=100&offset=0`) return {
        data: {
          schema: 'WILSY-PROJECT-PARTICIPANT-LIST/V1', tenant_id: TENANT,
          principal_id: PRINCIPAL, project_id: PROJECT_ID,
          limit: 100, offset: 0, items: [], has_more: false, next_offset: null,
        },
      };
      throw new Error('Unexpected source GET ' + path);
    });
    api.post.mockImplementation(async (path, body, options) => {
      expect(options.headers['X-Tenant-ID']).toBe(TENANT);
      expect(options.headers['Idempotency-Key']).toBeTruthy();
      commands += 1;
      if (commands === 1) {
        expect(path).toBe(`/projects/${PROJECT_ID}/tasks`);
        expect(body).toEqual({
          kind: 'TASK', title: 'Build milestone execution',
          description: '', due_date: null, assignee_principal_id: null,
          parent_task_id: null, depends_on: [],
        });
        work = [originalTask];
      } else {
        expect(path).toBe(`/projects/${PROJECT_ID}/tasks/${taskId}/transition`);
        expect(body).toEqual({ expected_revision: 1, status: 'IN_PROGRESS' });
        work = [{
          ...originalTask, status: 'IN_PROGRESS', revision: 2,
          fingerprint: 'b'.repeat(128),
        }];
      }
      return { data: {
        schema: 'WILSY-PROJECT-TASK-RESULT/V1',
        tenant_id: TENANT, principal_id: PRINCIPAL,
        project_id: PROJECT_ID, task: work[0],
      } };
    });
    api.patch.mockImplementationOnce(async (path, body, options) => {
      expect(path).toBe(`/projects/${PROJECT_ID}/tasks/${taskId}`);
      expect(options.headers['X-Tenant-ID']).toBe(TENANT);
      expect(options.headers['Idempotency-Key']).toBeTruthy();
      expect(body).toEqual({
        expected_revision: 2, title: 'Updated task handoff',
        description: '', due_date: '2026-12-11', assignee_principal_id: null,
      });
      work = [{
        ...work[0], title: 'Updated task handoff', due_date: '2026-12-11', revision: 3,
        fingerprint: 'c'.repeat(128),
      }];
      // The task update must finish after verified task readback even when
      // ancillary contributor/member/capability requests never respond.
      const previouslyVerifiedGet = api.get.getMockImplementation();
      const stalledSupportingRead = new Promise(() => {});
      api.get.mockImplementation((sourcePath, ...args) => (
        sourcePath === `/projects/${PROJECT_ID}/participants?limit=100&offset=0`
        || sourcePath === `/projects/${PROJECT_ID}/participant-options?limit=50&offset=0`
        || sourcePath === `/projects/${PROJECT_ID}/task-action-capabilities`
          ? stalledSupportingRead : previouslyVerifiedGet(sourcePath, ...args)
      ));
      return { data: {
        schema: 'WILSY-PROJECT-TASK-RESULT/V1',
        tenant_id: TENANT, principal_id: PRINCIPAL,
        project_id: PROJECT_ID, task: work[0],
      } };
    });
    render(<ProjectsWorkspace tenantId={TENANT} principalId={PRINCIPAL}
      sessionScope="task-source-readback-cert" />);
    fireEvent.click(await screen.findByRole('button', { name: /View project Persisted roadmap/ }));
    const panel = await screen.findByRole('region', { name: 'Project work execution' });
    expect(panel).toBeVisible();
    fireEvent.click(await screen.findByRole('button', { name: 'Create task' }));
    fireEvent.change(screen.getByPlaceholderText('Deliverable and action'), {
      target: { value: 'Build milestone execution' },
    });
    fireEvent.click(screen.getByRole('button', { name: 'Save work to EOS' }));
    await waitFor(() => expect(screen.getByText('Build milestone execution', {
      selector: '.wp-project-tasks tbody td button',
    })).toBeVisible());
    const row = screen.getByText('Build milestone execution', {
      selector: '.wp-project-tasks tbody td button',
    }).closest('tr');
    expect(row).toHaveAttribute('data-task-id', taskId);
    row.focus();
    const published = vi.spyOn(window, 'dispatchEvent');
    try {
      fireEvent.keyDown(row, { key: 'Enter' });
      expect(screen.getByRole('dialog', { name: 'Work details: Build milestone execution' }))
        .toBeVisible();
      await waitFor(() => expect(published.mock.calls.some(([event]) =>
        event.type === 'wilsy:ai-context-locator'
        && event.detail?.locator?.task_id === taskId
        && event.detail?.locator?.task_revision === 1
        && event.detail?.locator?.project_id === PROJECT_ID)).toBe(true));
      expect(published.mock.calls.filter(([event]) =>
        event.type === 'wilsy:ai-context-locator'
        && event.detail?.locator?.task_id === taskId)
        .every(([event]) => !JSON.stringify(event.detail).includes('Build milestone execution'))).toBe(true);
      fireEvent.click(screen.getByRole('button', { name: 'Close work details' }));
      await waitFor(() => expect(published.mock.calls.some(([event]) =>
        event.type === 'wilsy:ai-context-locator'
        && event.detail?.locator?.project_id === PROJECT_ID
        && !event.detail.locator.task_id)).toBe(true));
      expect(row).toHaveFocus();
    } finally {
      published.mockRestore();
    }

    fireEvent.click(await screen.findByText('Additional views · lifecycle and checklist'));
    fireEvent.click(screen.getByText(/View lifecycle breakdown · 1 work items on this page/));
    expect(screen.getByText('Work lifecycle · current page')).toBeVisible();
    expect(screen.getByRole('button', { name: /Filter work to To do: 1 of 1 verified on page/ })).toBeVisible();
    const startWork = within(row).getByRole('button', { name: 'Start: Build milestone execution' });
    await waitFor(() => expect(startWork).toBeEnabled());
    fireEvent.click(startWork);
    await waitFor(() => expect(
      screen.getByRole('row', { name: /Build milestone execution/ }),
    ).toHaveTextContent('In progress'));
    const lifecycle = document.querySelector('[aria-label="Verified task lifecycle chart"]');
    if (!lifecycle.open) fireEvent.click(lifecycle.querySelector('summary'));
    expect(screen.getByRole('button', { name: /Filter work to In progress: 1 of 1 verified on page/ })).toBeVisible();
    fireEvent.click(screen.getByRole('button', { name: /Filter work to To do: 0 of 1 verified on page/ }));
    expect(screen.getByText(/No work items on this verified page match/)).toBeVisible();
    fireEvent.click(screen.getByRole('button', { name: /Filter work to To do: 0 of 1 verified on page/ }));
    expect(screen.getByText('Build milestone execution', {
      selector: '.wp-project-tasks tbody td button',
    })).toBeVisible();
    expect(commands).toBe(2);
    const reconciledRow = screen.getByRole('row', { name: /Build milestone execution/ });
    const actionTrigger = within(reconciledRow).getByRole('button', {
      name: 'More actions for Build milestone execution',
    });
    await waitFor(() => expect(actionTrigger).toBeEnabled());
    fireEvent.click(actionTrigger);
    fireEvent.click(within(screen.getByRole('menu', {
       name: 'Actions for Build milestone execution',
     })).getByRole('menuitem', { name: 'Edit' }));
    const additional = screen.getByText('Additional task details · title and description');
    expect(additional.closest('details').open).toBe(false);
    fireEvent.click(additional);
    expect(additional.closest('details').open).toBe(true);
    const taskTitleInput = screen.getByRole('textbox', { name: 'Edit task title' });
    const assigneeInput = screen.getByRole('combobox', { name: 'Reassign task' });
    expect(Boolean(assigneeInput.compareDocumentPosition(taskTitleInput) & Node.DOCUMENT_POSITION_FOLLOWING)).toBe(true);
    fireEvent.change(taskTitleInput, { target: { value: 'Updated task handoff' } });
    fireEvent.change(screen.getByLabelText('Edit task due date'), { target: { value: '2026-12-11' } });
    fireEvent.click(screen.getByRole('button', { name: 'Save task changes' }));
    await waitFor(() => expect(screen.getByText('Updated task handoff', {
      selector: '.wp-project-tasks tbody td button',
    })).toBeVisible());
    expect(api.patch).toHaveBeenCalledTimes(1);
    await waitFor(() => expect(screen.queryByRole('dialog', { name: 'Edit work' })).not.toBeInTheDocument());
    const revisedRow = screen.getByRole('row', { name: /Updated task handoff/ });
    revisedRow.focus();
    fireEvent.keyDown(revisedRow, { key: 'Enter' });
    const reopened = screen.getByRole('dialog', { name: 'Work details: Updated task handoff' });
    expect(within(reopened).getByText('Due 2026-12-11')).toBeVisible();
    expect(persisted.status).toBe('planned');
  });

  it('ticks a persisted To-do checkbox only after confirmed EOS transition and fresh readback', async () => {
    const persisted = project();
    const taskId = 'ptk-' + 'e'.repeat(48);
    const activeTask = {
      schema: 'wilsy.project.task.v1', tenant_id: TENANT, project_id: PROJECT_ID,
      task_id: taskId, kind: 'TASK', parent_task_id: null,
      title: 'Evidence-backed operational acceptance', description: '',
      status: 'IN_PROGRESS', assignee_principal_id: null, due_date: null,
      depends_on: [], created_by_principal_id: PRINCIPAL,
      updated_by_principal_id: PRINCIPAL, revision: 2,
      created_at: '2026-11-18T06:00:00+00:00',
      updated_at: '2026-11-18T06:00:00+00:00', fingerprint: 'a'.repeat(128),
    };
    const completedTask = {
      ...activeTask, status: 'DONE', revision: 3, fingerprint: 'b'.repeat(128),
    };
    let readCount = 0;
    let releaseReadback;
    const pendingReadback = new Promise(resolve => { releaseReadback = resolve; });
    const taskList = item => ({ data: {
      schema: 'WILSY-PROJECT-TASK-LIST/V1', tenant_id: TENANT,
      principal_id: PRINCIPAL, project_id: PROJECT_ID,
      limit: 50, offset: 0, items: [item], has_more: false, next_offset: null,
    } });
    mockProjectGet(async path => {
      if (path === '/projects') return { data: list([persisted]) };
      if (path === '/projects/summary') return { data: summary([persisted]) };
      if (path === `/projects/${PROJECT_ID}`) return { data: result(persisted) };
      if (path === `/projects/${PROJECT_ID}/tasks?limit=50&offset=0`) {
        readCount += 1;
        return readCount === 1 ? taskList(activeTask) : pendingReadback;
      }
      if (path === `/projects/${PROJECT_ID}/participants?limit=100&offset=0`) return { data: {
        schema: 'WILSY-PROJECT-PARTICIPANT-LIST/V1', tenant_id: TENANT,
        principal_id: PRINCIPAL, project_id: PROJECT_ID,
        limit: 100, offset: 0, items: [], has_more: false, next_offset: null,
      } };
      throw new Error('Unexpected project read ' + path);
    });
    api.post.mockImplementationOnce(async (path, body, options) => {
      expect(path).toBe(`/projects/${PROJECT_ID}/tasks/${taskId}/transition`);
      expect(body).toEqual({ expected_revision: 2, status: 'DONE' });
      expect(options.headers['X-Tenant-ID']).toBe(TENANT);
      expect(options.headers['Idempotency-Key']).toBeTruthy();
      return { data: {
        schema: 'WILSY-PROJECT-TASK-RESULT/V1',
        tenant_id: TENANT, principal_id: PRINCIPAL,
        project_id: PROJECT_ID, task: completedTask,
      } };
    });
    render(<ProjectsWorkspace tenantId={TENANT} principalId={PRINCIPAL}
      sessionScope="source-checklist-readback-cert"/>);
    fireEvent.click(await screen.findByRole('button', { name: /View project Persisted roadmap/ }));
    fireEvent.click(await screen.findByText('Additional views · lifecycle and checklist'));
    fireEvent.click(await screen.findByText(/Checklist mode · 0\/1 completed/));
    const checkbox = await screen.findByRole('checkbox', {
      name: 'Mark completed: Evidence-backed operational acceptance',
    });
    expect(checkbox).not.toBeChecked();
    expect(screen.getByText('To-do checklist · current verified page')).toBeVisible();
    fireEvent.click(checkbox);
    expect(screen.getByRole('dialog', { name: 'Confirm verified task completion' })).toBeVisible();
    expect(api.post).not.toHaveBeenCalled();
    const confirm = screen.getByRole('button', { name: 'Confirm Done in EOS' });
    expect(confirm).toBeDisabled();
    fireEvent.click(screen.getByRole('checkbox', {
      name: /I reviewed this task's acceptance and supporting evidence/,
    }));
    expect(confirm).toBeEnabled();
    fireEvent.click(confirm);
    await waitFor(() => expect(api.post).toHaveBeenCalledTimes(1));
    await waitFor(() => expect(readCount).toBe(2));
    expect(checkbox).not.toBeChecked();
    expect(screen.getByText('Updating to Done…')).toBeVisible();
    await act(async () => { releaseReadback(taskList(completedTask)); });
    await waitFor(() => expect(screen.queryByText('Updating to Done…')).not.toBeInTheDocument());
    expect(await screen.findByRole('checkbox', {
      name: 'Mark completed: Evidence-backed operational acceptance',
    })).toBeChecked();
    const checklist = document.querySelector('[aria-label="EOS verified To-do checklist"]');
    if (!checklist.open) fireEvent.click(checklist.querySelector('summary'));
    expect(screen.getByText('1 of 1 completed')).toBeVisible();
    expect(screen.queryByRole('group', { name: 'Confirm verified task completion' }))
      .not.toBeInTheDocument();
  });

  it('opens project Discussions from top navigation and reads the selected milestone without work dashboard', async () => {
    const persisted = project();
    const taskId = 'ptk-' + 'f'.repeat(48);
    const entry = {
      schema: 'wilsy.project.task.v1', tenant_id: TENANT, project_id: PROJECT_ID,
      task_id: taskId, kind: 'TASK', parent_task_id: null,
      title: 'Current project delivery', description: '',
      status: 'TODO', assignee_principal_id: null, due_date: null,
      depends_on: [], created_by_principal_id: PRINCIPAL,
      updated_by_principal_id: PRINCIPAL, revision: 1,
      created_at: '2026-11-18T06:00:00+00:00',
      updated_at: '2026-11-18T06:00:00+00:00', fingerprint: 'a'.repeat(128),
    };
    mockProjectGet(async path => {
      if (path === '/projects') return { data: list([persisted]) };
      if (path === '/projects/summary') return { data: summary([persisted]) };
      if (path === `/projects/${PROJECT_ID}`) return { data: result(persisted) };
      if (path === `/projects/${PROJECT_ID}/tasks?limit=50&offset=0`) return { data: {
        schema: 'WILSY-PROJECT-TASK-LIST/V1', tenant_id: TENANT,
        principal_id: PRINCIPAL, project_id: PROJECT_ID,
        items: [entry], limit: 50, offset: 0, has_more: false, next_offset: null,
      } };
      if (path === `/projects/${PROJECT_ID}/participants?limit=100&offset=0`) return { data: {
        schema: 'WILSY-PROJECT-PARTICIPANT-LIST/V1', tenant_id: TENANT,
        principal_id: PRINCIPAL, project_id: PROJECT_ID,
        items: [], limit: 100, offset: 0, has_more: false, next_offset: null,
      } };
      if (path === `/projects/${PROJECT_ID}/tasks/${taskId}/comments?limit=50&offset=0`) return { data: {
        schema: 'WILSY-PROJECT-COMMENT-LIST/V1', tenant_id: TENANT,
        principal_id: PRINCIPAL, project_id: PROJECT_ID, task_id: taskId,
        items: [{
          schema: 'wilsy.project.comment.v1', tenant_id: TENANT,
          project_id: PROJECT_ID, task_id: taskId, comment_id: 'pcm-' + 'a'.repeat(48),
          author_principal_id: PRINCIPAL, body: '**Recent progress**',
          mentions: [], fingerprint: 'b'.repeat(128),
          created_at: '2026-11-19T09:00:00+00:00',
        }], limit: 50, offset: 0, has_more: false, next_offset: null,
      } };
      if (path === `/projects/${PROJECT_ID}/tasks/${taskId}/events?limit=50&offset=0`) return { data: {
        schema: 'WILSY-PROJECT-TASK-EVENT-LIST/V1', tenant_id: TENANT,
        principal_id: PRINCIPAL, project_id: PROJECT_ID, task_id: taskId,
        items: [{
          schema: 'wilsy.project.task.event.v1', tenant_id: TENANT,
          project_id: PROJECT_ID, task_id: taskId, revision: 1,
          event_type: 'PROJECT_TASK_CREATED', actor_principal_id: PRINCIPAL,
          status_after: 'TODO', occurred_at: '2026-11-18T06:00:00+00:00',
        }], limit: 50, offset: 0, has_more: false, next_offset: null,
      } };
      if (path === `/projects/${PROJECT_ID}/tasks/${taskId}/approvals?limit=50&offset=0`) return { data: {
        schema: 'WILSY-PROJECT-APPROVAL-LIST/V1', tenant_id: TENANT,
        principal_id: PRINCIPAL, project_id: PROJECT_ID, task_id: taskId,
        items: [{
          schema: 'wilsy.project.approval.v1', tenant_id: TENANT,
          project_id: PROJECT_ID, task_id: taskId, approval_id: 'par-' + 'c'.repeat(48),
          requester_principal_id: PRINCIPAL, reviewer_principal_id: 'reviewer-a',
          rationale: 'Approve delivery evidence', status: 'APPROVED',
          requested_at: '2026-11-19T08:00:00+00:00',
          decided_at: '2026-11-19T10:00:00+00:00',
          decision_rationale: 'Reviewed and accepted', revision: 2,
          fingerprint: 'c'.repeat(128),
        }], limit: 50, offset: 0, has_more: false, next_offset: null,
      } };
      if (path === `/projects/${PROJECT_ID}/tasks/${taskId}/attachments?limit=50&offset=0`) return { data: {
        schema: 'WILSY-PROJECT-ATTACHMENT-LIST/V1', tenant_id: TENANT,
        principal_id: PRINCIPAL, project_id: PROJECT_ID, task_id: taskId,
        items: [{
          schema: 'wilsy.project.attachment.v1', tenant_id: TENANT,
          project_id: PROJECT_ID, task_id: taskId, attachment_id: 'pat-' + 'd'.repeat(48),
          filename: 'evidence.pdf', uploader_principal_id: PRINCIPAL,
          media_type: 'application/pdf', size_bytes: 1200,
          content_sha3_512: 'a'.repeat(128), fingerprint: 'd'.repeat(128),
          state: 'QUARANTINED', revision: 1,
          scan_clearance_fingerprint: 'f'.repeat(128),
          created_at: '2026-11-19T11:00:00+00:00',
          scan_clearance_status: 'SCAN_CLEAN_VERIFIED',
        }], limit: 50, offset: 0, has_more: false, next_offset: null,
      } };
      throw new Error('Unexpected project GET ' + path);
    });
    render(<ProjectsWorkspace tenantId={TENANT} principalId={PRINCIPAL}
      sessionScope="top-level-discussions-cert"/>);
    fireEvent.click(await screen.findByRole('button', { name: /View project Persisted roadmap/ }));
    // Work and discussion project the same EOS task source. Switching view
    // must not issue a second costly authentication/database read fanout.
    await screen.findByText('Current project delivery', { selector: '.wp-project-tasks tbody td button' });
    const taskPath = `/projects/${PROJECT_ID}/tasks?limit=50&offset=0`;
    const taskReads = () => api.get.mock.calls.filter(([path]) => path === taskPath).length;
    expect(taskReads()).toBe(1);
    fireEvent.click(within(screen.getByRole('navigation', { name: 'Project workspace views' }))
      .getByRole('button', { name: 'Activity & discussion' }));
    expect(await screen.findByRole('region', { name: 'Project discussions workspace' })).toBeVisible();
    expect(taskReads()).toBe(1);
    expect(screen.queryByRole('region', { name: 'Verified task lifecycle chart' })).not.toBeInTheDocument();
    expect(screen.queryByRole('region', { name: 'EOS verified To-do checklist' })).not.toBeInTheDocument();
    const options = await screen.findByRole('list', { name: 'Verified discussion work items' });
    fireEvent.click(within(options).getByRole('button', { name: /Current project delivery/ }));
    expect(await screen.findByRole('region', { name: 'Activity & discussion' })).toBeVisible();
    expect(screen.getByRole('list', { name: 'Verified discussion work items' })).toBeVisible();
    expect(screen.getByRole('button', { name: 'Project notes' })).toBeVisible();
    expect(screen.queryByRole('dialog', { name: /Work details:/ })).not.toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Write update' })).toHaveAttribute('aria-expanded', 'false');
    expect(document.querySelector('[aria-label="Verified task activity history"]')).toBeVisible();
    expect(await screen.findByText('Work created')).toBeVisible();
    expect(await screen.findByText('Evidence attached')).toBeVisible();
    expect(screen.getByText('Recent progress')).toBeVisible();
    const history = document.querySelector('[aria-label="Verified task activity history"]');
    await waitFor(() => expect(history.querySelectorAll('li')).toHaveLength(5));
    const entries = [...history.querySelectorAll('li')];
    expect(entries.map(item => item.textContent)).toEqual([
      expect.stringContaining('Evidence attached'),
      expect.stringContaining('Decision · approved'),
      expect.stringContaining('Recent progress'),
      expect.stringContaining('Approval requested'),
      expect.stringContaining('Work created'),
    ]);
    expect(screen.getAllByRole('button', { name: 'Open governed decision' })).toHaveLength(2);
    expect(screen.getByRole('button', { name: 'Open governed attachment' })).toBeVisible();
    expect(screen.getByText(/revision 1/)).toBeVisible();
    fireEvent.click(within(options).getByRole('button', { name: /Current project delivery/ }));
    expect(await screen.findByRole('list', { name: 'Verified discussion work items' })).toBeVisible();
  });

  it('opens a focused EOS task discussion with composer before the history and restores the queue', async () => {
    const persisted = project();
    const taskId = 'ptk-' + 'f'.repeat(48);
    const entry = {
      schema: 'wilsy.project.task.v1', tenant_id: TENANT, project_id: PROJECT_ID,
      task_id: taskId, kind: 'TASK', parent_task_id: null,
      title: 'Current project delivery', description: '',
      status: 'TODO', assignee_principal_id: null, due_date: null,
      depends_on: [], created_by_principal_id: PRINCIPAL,
      updated_by_principal_id: PRINCIPAL, revision: 1,
      created_at: '2026-11-18T06:00:00+00:00',
      updated_at: '2026-11-18T06:00:00+00:00', fingerprint: 'a'.repeat(128),
    };
    mockProjectGet(async path => {
      if (path === '/projects') return { data: list([persisted]) };
      if (path === '/projects/summary') return { data: summary([persisted]) };
      if (path === `/projects/${PROJECT_ID}`) return { data: result(persisted) };
      if (path === `/projects/${PROJECT_ID}/tasks?limit=50&offset=0`) return { data: {
        schema: 'WILSY-PROJECT-TASK-LIST/V1', tenant_id: TENANT,
        principal_id: PRINCIPAL, project_id: PROJECT_ID,
        items: [entry], limit: 50, offset: 0, has_more: false, next_offset: null,
      } };
      if (path === `/projects/${PROJECT_ID}/participants?limit=100&offset=0`) return { data: {
        schema: 'WILSY-PROJECT-PARTICIPANT-LIST/V1', tenant_id: TENANT,
        principal_id: PRINCIPAL, project_id: PROJECT_ID,
        items: [], limit: 100, offset: 0, has_more: false, next_offset: null,
      } };
      if (path === `/projects/${PROJECT_ID}/tasks/${taskId}/comments?limit=50&offset=0`) return { data: {
        schema: 'WILSY-PROJECT-COMMENT-LIST/V1', tenant_id: TENANT,
        principal_id: PRINCIPAL, project_id: PROJECT_ID, task_id: taskId,
        items: [], limit: 50, offset: 0, has_more: false, next_offset: null,
      } };
      throw new Error('Unexpected project GET ' + path);
    });
    render(<ProjectsWorkspace tenantId={TENANT} principalId={PRINCIPAL}
      sessionScope="focused-discussion-cert"/>);
    fireEvent.click(await screen.findByRole('button', { name: /View project Persisted roadmap/ }));
    await screen.findByText('Current project delivery', { selector: '.wp-project-tasks tbody td button' });
    fireEvent.click(within(screen.getByRole('row', { name: /Current project delivery/ }))
      .getByRole('button', { name: /More actions for Current project delivery/ }));
    fireEvent.click(within(screen.getByRole('menu', {
       name: 'Actions for Current project delivery',
     })).getByRole('menuitem', { name: 'Activity & discussion' }));
    expect(await screen.findByRole('region', { name: 'Activity & discussion' })).toBeVisible();
    expect(screen.getByRole('button', { name: '← Work' })).toBeVisible();
    expect(screen.queryByRole('button', { name: 'Close task discussion' })).not.toBeInTheDocument();
    expect(screen.queryByRole('region', { name: 'Verified project tasks' })).not.toBeInTheDocument();
    expect(screen.queryByRole('region', { name: 'Verified task lifecycle chart' })).not.toBeInTheDocument();
    const discussion = screen.getByRole('region', { name: 'Activity & discussion' });
    expect(screen.getByRole('button', { name: 'Write update' }))
      .toHaveAttribute('aria-expanded', 'false');
    expect(discussion.querySelector('[aria-label="Verified task activity history"]'))
      .toBeInTheDocument();
    expect(discussion.querySelector('textarea[aria-label="New task comment"]'))
      .not.toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: 'Write update' }));
    expect(screen.getByRole('button', { name: 'Close editor' }))
      .toHaveAttribute('aria-expanded', 'true');
    expect(discussion.querySelector('textarea[aria-label="New task comment"]')).toBeVisible();
    expect(screen.getByRole('textbox', { name: 'New task comment' })).toHaveFocus();
    expect(discussion.querySelector('[aria-label="Verified task activity history"]'))
      .not.toBeInTheDocument();
    const draft = '**Development progress — 19 November 2026**\\n\\n- Source readback verified\\n- Pending mobile acceptance\\n\\n<script>alert(1)</script>'.replaceAll('\\n','\n');
    fireEvent.change(screen.getByRole('textbox', { name: 'New task comment' }), {
      target: { value: draft },
    });
    const preview = screen.getByRole('region', { name: 'Live formatted comment preview' });
    expect(preview.querySelector('strong')).toHaveTextContent('Development progress — 19 November 2026');
    expect(preview.querySelectorAll('li')).toHaveLength(2);
    expect(preview).toHaveTextContent('<script>alert(1)</script>');
    expect(preview.querySelector('script')).not.toBeInTheDocument();
    expect(screen.getByRole('textbox', { name: 'New task comment' })).toHaveValue(draft);
    expect(discussion.querySelector('textarea[aria-label="New task comment"]'))
      .toHaveValue(draft);
    fireEvent.click(screen.getByRole('button', { name: 'Close editor' }));
    expect(discussion.querySelector('textarea')).not.toBeInTheDocument();
    expect(discussion.querySelector('[aria-label="Verified task activity history"]'))
      .toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: 'Write update' }));
    expect(screen.getByRole('textbox', { name: 'New task comment' })).toHaveValue(draft);
    fireEvent.click(screen.getByRole('button', { name: 'Close editor' }));
    fireEvent.click(screen.getByRole('button', { name: '← Work' }));
    expect(screen.getByRole('region', { name: 'Verified project tasks' })).toBeVisible();
  });

  it('simulates MW-T12 milestone recording with EOS comment readback and blocked release', async () => {
    const storedProject = project({ name: 'WILSY OS — Unified Operating Platform Foundation', status: 'active' });
    const taskId = 'ptk-' + 'c'.repeat(48);
    const task = {
      schema: 'wilsy.project.task.v1', tenant_id: TENANT, project_id: PROJECT_ID,
      task_id: taskId, kind: 'TASK', parent_task_id: null,
      title: 'MW-T12 — Certify production readiness and rollback', description: '',
      status: 'IN_PROGRESS', assignee_principal_id: PRINCIPAL, due_date: '2026-11-23',
      depends_on: [], created_by_principal_id: PRINCIPAL, updated_by_principal_id: PRINCIPAL,
      revision: 3, created_at: '2026-11-17T10:13:00+00:00',
      updated_at: '2026-11-24T04:31:00+00:00', fingerprint: 'a'.repeat(128),
    };
    const sha = '840b294865a102ede84f77e3fc83ce4dcaabec19';
    const milestone = [
      '## MW-T12 — Engineering delivery update',
      '**CI:** 23/23 exact-head GitHub workflows passed',
      '**Commit:** ' + sha,
      '**Local build:** successful, with nonblocking warnings',
      '**Rollback and recovery:** NOT CERTIFIED — nonproduction drill pending',
      '**Strategy outcome:** READBACK REQUIRED — no outcome score certified',
      '**Task lifecycle:** IN_PROGRESS — production release remains BLOCKED',
    ].join('\n\n');
    const comment = {
      schema: 'wilsy.project.comment.v1', tenant_id: TENANT, project_id: PROJECT_ID,
      task_id: taskId, comment_id: 'pcm-' + 'd'.repeat(48),
      author_principal_id: PRINCIPAL, body: milestone, mentions: [],
      fingerprint: 'f'.repeat(128), created_at: '2026-11-24T04:35:00+00:00',
    };
    const comments = `/projects/${PROJECT_ID}/tasks/${taskId}/comments`;
    let persisted = false;
    let commentReads = 0;
    let sourceReadbackHeld = false;
    let releaseReadback;
    const heldReadback = new Promise(resolve => { releaseReadback = resolve; });
    mockProjectGet(async (route, config = {}) => {
      if (route === '/projects') return { data: list([storedProject]) };
      if (route === '/projects/summary') return { data: summary([storedProject]) };
      if (route === `/projects/${PROJECT_ID}`) return { data: result(storedProject) };
      if (route === `/projects/${PROJECT_ID}/tasks?limit=50&offset=0`) return { data: {
        schema: 'WILSY-PROJECT-TASK-LIST/V1', tenant_id: TENANT,
        principal_id: PRINCIPAL, project_id: PROJECT_ID, items: [task],
        limit: 50, offset: 0, has_more: false, next_offset: null,
      } };
      if (route === `/projects/${PROJECT_ID}/participants?limit=100&offset=0`) return { data: {
        schema: 'WILSY-PROJECT-PARTICIPANT-LIST/V1', tenant_id: TENANT,
        principal_id: PRINCIPAL, project_id: PROJECT_ID, items: [],
        limit: 100, offset: 0, has_more: false, next_offset: null,
      } };
      if (route === comments + '?limit=50&offset=0') {
        expect(config.headers['X-Tenant-ID']).toBe(TENANT);
        commentReads += 1;
        if (persisted && !sourceReadbackHeld) {
          sourceReadbackHeld = true;
          await heldReadback;
        }
        return { data: {
          schema: 'WILSY-PROJECT-COMMENT-LIST/V1', tenant_id: TENANT,
          principal_id: PRINCIPAL, project_id: PROJECT_ID, task_id: taskId,
          items: persisted ? [comment] : [], limit: 50, offset: 0,
          has_more: false, next_offset: null,
        } };
      }
      throw new Error('Unexpected simulated EOS GET ' + route);
    });
    api.post.mockImplementation(async (route, payload, config) => {
      expect(route).toBe(comments);
      expect(payload).toEqual({ body: milestone, mentions: [] });
      expect(config.headers['X-Tenant-ID']).toBe(TENANT);
      expect(config.headers['Idempotency-Key']).toBeTruthy();
      persisted = true;
      return { data: {
        schema: 'WILSY-PROJECT-COMMENT-RESULT/V1', tenant_id: TENANT,
        principal_id: PRINCIPAL, project_id: PROJECT_ID, task_id: taskId, comment,
      } };
    });
    render(<ProjectsWorkspace tenantId={TENANT} principalId={PRINCIPAL}
      sessionScope="mw-t12-milestone-simulation"/>);
    fireEvent.click(await screen.findByRole('button', {
      name: /View project WILSY OS — Unified Operating Platform Foundation/,
    }));
    fireEvent.click(within(screen.getByRole('navigation', { name: 'Project workspace views' }))
      .getByRole('button', { name: 'Activity & discussion' }));
    const queue = await screen.findByRole('list', { name: 'Verified discussion work items' });
    fireEvent.click(within(queue).getByRole('button', { name: /MW-T12 — Certify production readiness and rollback/ }));
    fireEvent.click(await screen.findByRole('button', { name: 'Write update' }));
    const editor = screen.getByRole('textbox', { name: 'New task comment' });
    fireEvent.change(editor, { target: { value: milestone } });
    fireEvent.click(screen.getByRole('button', { name: 'Publish to EOS' }));
    await waitFor(() => expect(sourceReadbackHeld).toBe(true));
    expect(api.post).toHaveBeenCalledTimes(1);
    expect(editor).toHaveValue(milestone);
    expect(api.patch).not.toHaveBeenCalled();
    await act(async () => { releaseReadback(); });
    const history = document.querySelector('[aria-label="Verified task activity history"]');
    await waitFor(() => expect(within(history).getByRole('button', { name: 'Read full update' })).toBeVisible());
    expect(history).not.toHaveTextContent('23/23 exact-head GitHub workflows passed');
    fireEvent.click(within(history).getByRole('button', { name: 'Read full update' }));
    await waitFor(() => expect(history).toHaveTextContent('23/23 exact-head GitHub workflows passed'));
    expect(history).toHaveTextContent(sha);
    // Durable source content, not local draft clearing, is the certification gate.
    expect(history).toHaveTextContent('NOT CERTIFIED');
    expect(history).toHaveTextContent('READBACK REQUIRED');
    expect(history).toHaveTextContent('production release remains BLOCKED');
    fireEvent.click(screen.getByRole('button', { name: 'Refresh' }));
    await waitFor(() => expect(commentReads).toBeGreaterThanOrEqual(3));
    if (within(history).queryByRole('button', { name: 'Read full update' })) {
      fireEvent.click(within(history).getByRole('button', { name: 'Read full update' }));
    }
    expect(history).toHaveTextContent('23/23 exact-head GitHub workflows passed');
    expect(task.status).toBe('IN_PROGRESS');
    expect(storedProject.status).toBe('active');
    expect(api.post).toHaveBeenCalledTimes(1);
    expect(api.patch).not.toHaveBeenCalled();
  });

  it('prioritizes the task source and classifies real EOS HTTP 503 without auxiliary reads', async () => {
    const persisted = project();
    let rejectTasks;
    let tasksStarted = false;
    const pendingTasks = new Promise((resolve, reject) => {
      rejectTasks = reject;
    });
    mockProjectGet(async path => {
      if (path === '/projects') return { data: list([persisted]) };
      if (path === '/projects/summary') return { data: summary([persisted]) };
      if (path === `/projects/${PROJECT_ID}`) return { data: result(persisted) };
      if (path === `/projects/${PROJECT_ID}/tasks?limit=50&offset=0`) {
        tasksStarted = true;
        return pendingTasks;
      }
      throw new Error('Auxiliary source must not execute before mandatory task read: ' + path);
    });
    render(<ProjectsWorkspace tenantId={TENANT} principalId={PRINCIPAL}
      sessionScope="primary-task-read-first-cert"/>);
    fireEvent.click(await screen.findByRole('button', { name: /View project Persisted roadmap/ }));
    const region = await screen.findByRole('region', { name: 'Project work execution' });
    await waitFor(() => expect(tasksStarted).toBe(true));
    expect(api.get.mock.calls.some(([path]) => String(path).includes('/participants?'))).toBe(false);
    expect(api.get.mock.calls.some(([path]) => String(path).includes('/participant-options?'))).toBe(false);
    rejectTasks({ response: { status: 503, data: { detail: 'PROJECT_TASK_LIST_UNAVAILABLE' } } });
    await waitFor(() => expect(within(region).getByRole('alert'))
      .toHaveTextContent('Project task list is unavailable in EOS (HTTP 503) · EOS PROJECT_TASK_LIST_UNAVAILABLE'));
    expect(within(region).queryByText(/verified work items/)).not.toBeInTheDocument();
    expect(within(region).queryByRole('button', { name: 'Create task' })).not.toBeInTheDocument();
    expect(api.post).not.toHaveBeenCalled();
  });

  it('keeps EOS-verified work visible when project participants fail independently', async () => {
    const persisted = project();
    mockProjectGet(async path => {
      if (path === '/projects') return { data: list([persisted]) };
      if (path === '/projects/summary') return { data: summary([persisted]) };
      if (path === `/projects/${PROJECT_ID}`) return { data: result(persisted) };
      if (path === `/projects/${PROJECT_ID}/tasks?limit=50&offset=0`) return { data: {
        schema: 'WILSY-PROJECT-TASK-LIST/V1',
        tenant_id: TENANT, principal_id: PRINCIPAL, project_id: PROJECT_ID,
        items: [], limit: 50, offset: 0, has_more: false, next_offset: null,
      } };
      if (path === `/projects/${PROJECT_ID}/participants?limit=100&offset=0`)
        throw { response: { status: 503 } };
      if (path === `/projects/${PROJECT_ID}/participant-options?limit=50&offset=0`)
        throw { response: { status: 503 } };
      throw new Error('Unexpected work source: ' + path);
    });
    render(<ProjectsWorkspace tenantId={TENANT} principalId={PRINCIPAL}
      sessionScope="participant-source-failure-isolation"/>);
    fireEvent.click(await screen.findByRole('button', { name: /View project Persisted roadmap/ }));
    const region = await screen.findByRole('region', { name: 'Project work execution' });
    await waitFor(() => expect(within(region).getByRole('alert'))
      .toHaveTextContent('Project contributor list source is unavailable'));
    expect(within(region).getByText(/0 verified work items/)).toBeVisible();
    expect(within(region).queryByText(/Project work could not be verified/)).not.toBeInTheDocument();
    fireEvent.click(within(region).getByRole('button', { name: 'Create task' }));
    const select = within(region).getByRole('combobox', { name: 'Task assignee' });
    expect(select).toBeDisabled();
    expect(within(region).getByRole('button', { name: 'Manage eligible contributors' }))
      .toBeDisabled();
    expect(within(region).queryByRole('dialog', {
      name: 'Manage contributors for task assignment',
    })).not.toBeInTheDocument();
  });

  it('keeps an unsaved task while a verified contributor is admitted inline', async () => {
    const persisted = project();
    const memberId = 'employee-' + 'd'.repeat(24);
    let admitted = false;
    const participant = {
      tenant_id: TENANT, project_id: PROJECT_ID, principal_id: memberId,
      state: 'ACTIVE', role: 'CONTRIBUTOR', revision: 1,
      fingerprint: 'a'.repeat(128), first_name: 'Alex', last_name: 'Mokoena',
    };
    mockProjectGet(async path => {
      if (path === '/projects') return { data: list([persisted]) };
      if (path === '/projects/summary') return { data: summary([persisted]) };
      if (path === `/projects/${PROJECT_ID}`) return { data: result(persisted) };
      if (path === `/projects/${PROJECT_ID}/tasks?limit=50&offset=0`) return { data: {
        schema: 'WILSY-PROJECT-TASK-LIST/V1', tenant_id: TENANT,
        principal_id: PRINCIPAL, project_id: PROJECT_ID, items: [],
        limit: 50, offset: 0, has_more: false, next_offset: null,
      } };
      if (path === `/projects/${PROJECT_ID}/participants?limit=100&offset=0`) return { data: {
        schema: 'WILSY-PROJECT-PARTICIPANT-LIST/V1', tenant_id: TENANT,
        principal_id: PRINCIPAL, project_id: PROJECT_ID,
        items: admitted ? [participant] : [], limit: 100, offset: 0,
        has_more: false, next_offset: null,
      } };
      if (path === `/projects/${PROJECT_ID}/participants?limit=50&offset=0`) return { data: {
        schema: 'WILSY-PROJECT-PARTICIPANT-LIST/V1', tenant_id: TENANT,
        principal_id: PRINCIPAL, project_id: PROJECT_ID,
        items: admitted ? [participant] : [], limit: 50, offset: 0,
        has_more: false, next_offset: null,
      } };
      if (path === `/projects/${PROJECT_ID}/participant-options?limit=50&offset=0`) return { data: {
        schema: 'WILSY-PROJECT-PARTICIPANT-OPTIONS/V1', tenant_id: TENANT,
        principal_id: PRINCIPAL, project_id: PROJECT_ID,
        items: [{ principal_id: memberId, first_name: 'Alex', last_name: 'Mokoena' }],
        limit: 50, offset: 0, has_more: false, next_offset: null,
      } };
      throw new Error('Unexpected project contributor source ' + path);
    });
    api.post.mockImplementation(async (path, body, options) => {
      expect(path).toBe(`/projects/${PROJECT_ID}/participants`);
      expect(body).toEqual({ principal_id: memberId, role: 'CONTRIBUTOR' });
      expect(options.headers['X-Tenant-ID']).toBe(TENANT);
      expect(options.headers['Idempotency-Key']).toBeTruthy();
      admitted = true;
      return { data: {
        schema: 'WILSY-PROJECT-PARTICIPANT-RESULT/V1',
        tenant_id: TENANT, principal_id: PRINCIPAL, project_id: PROJECT_ID,
        participant,
      } };
    });
    render(<ProjectsWorkspace tenantId={TENANT} principalId={PRINCIPAL}
      sessionScope="inline-contributor-admission-cert"/>);
    fireEvent.click(await screen.findByRole('button', { name: /View project Persisted roadmap/ }));
    await screen.findByRole('region', { name: 'Project work execution' });
    expect(screen.getByText(/Work filters, grouping and sorting/)).toBeVisible();
    const filters = screen.getByText(/Work filters, grouping and sorting/).closest('details');
    expect(filters).not.toHaveAttribute('open');
    fireEvent.click(screen.getByRole('button', { name: 'Create task' }));
    fireEvent.change(screen.getByPlaceholderText('Deliverable and action'), {
      target: { value: 'Preserved governance draft' },
    });
    expect(screen.getByText(/No verified current project contributors are eligible/)).toBeVisible();
    const assignee = screen.getByRole('combobox', { name: 'Task assignee' });
    const candidate = within(assignee).getByRole('option', {
      name: 'Alex Mokoena · Authorize contributor',
    });
    expect(candidate).toHaveValue('member:' + memberId);
    fireEvent.change(assignee, { target: { value: 'member:' + memberId } });
    const management = await screen.findByRole('dialog', { name: 'Manage contributors for task assignment' });
    expect(management).toBeVisible();
    expect(within(management).getByRole('button', { name: 'Close' })).toHaveFocus();
    const eligible = await within(management).findByRole('combobox', { name: 'Eligible participant' });
    expect(eligible).toHaveValue(memberId);
    const addContributor = within(management).getByRole('button', { name: /Add participant/ });
    await waitFor(() => expect(addContributor).toBeEnabled());
    fireEvent.click(addContributor);
    await waitFor(() => expect(api.post).toHaveBeenCalledTimes(1));
    await waitFor(() => expect(within(screen.getByRole('combobox', { name: 'Task assignee' }))
      .getByRole('option', { name: 'Alex Mokoena' })).toHaveValue(memberId));
    expect(screen.getByPlaceholderText('Deliverable and action')).toHaveValue('Preserved governance draft');
    fireEvent.change(screen.getByRole('combobox', { name: 'Task assignee' }), {
      target: { value: memberId },
    });
    expect(screen.getByRole('combobox', { name: 'Task assignee' })).toHaveValue(memberId);
    expect(api.post).toHaveBeenCalledTimes(1);
    expect(api.patch).not.toHaveBeenCalled();
  });

  it('labels eligible exact-tenant participants using sourced names, not opaque IDs', async () => {
    const persisted = project();
    const memberId = 'employee-' + 'b'.repeat(24);
    const namelessId = 'employee-' + 'c'.repeat(24);
    mockProjectGet(async path => {
      if (path === '/projects') return { data: list([persisted]) };
      if (path === '/projects/summary') return { data: summary([persisted]) };
      if (path === `/projects/${PROJECT_ID}`) return { data: result(persisted) };
      if (path === `/projects/${PROJECT_ID}/participants?limit=50&offset=0`) return { data: {
        schema: 'WILSY-PROJECT-PARTICIPANT-LIST/V1', tenant_id: TENANT,
        principal_id: PRINCIPAL, project_id: PROJECT_ID,
        items: [], limit: 50, offset: 0, has_more: false, next_offset: null,
      } };
      if (path === `/projects/${PROJECT_ID}/participant-options?limit=50&offset=0`) return { data: {
        schema: 'WILSY-PROJECT-PARTICIPANT-OPTIONS/V1', tenant_id: TENANT,
        principal_id: PRINCIPAL, project_id: PROJECT_ID,
        items: [
          { principal_id: memberId, first_name: 'Alex', last_name: 'Mokoena' },
          { principal_id: namelessId, first_name: null, last_name: null },
        ], limit: 50, offset: 0, has_more: false, next_offset: null,
      } };
      throw new Error('Unexpected GET ' + path);
    });
    render(<ProjectsWorkspace tenantId={TENANT} principalId={PRINCIPAL}
      sessionScope="verified-member-names-cert"/>);
    fireEvent.click(await screen.findByRole('button', { name: /View project Persisted roadmap/ }));
    fireEvent.click(screen.getByRole('button', { name: 'People' }));
    const option = await screen.findByRole('option', { name: 'Alex Mokoena' });
    expect(option).toHaveValue(memberId);
    expect(screen.getByRole('option', { name: 'Verified member — name unavailable' }))
      .toHaveValue(namelessId);
    fireEvent.change(screen.getByRole('combobox', { name: 'Eligible participant' }),
      { target: { value: memberId } });
    expect(screen.queryByText('Source principal: ' + memberId)).not.toBeInTheDocument();
  });

  it('pages an authorized 22-task EOS batch without hiding records or selecting offscreen work', async () => {
    const persisted = project();
    const base = {
      schema: 'wilsy.project.task.v1', tenant_id: TENANT, project_id: PROJECT_ID,
      description: '', status: 'TODO', assignee_principal_id: null, due_date: null,
      depends_on: [], created_by_principal_id: PRINCIPAL, updated_by_principal_id: PRINCIPAL,
      created_at: '2026-11-18T06:00:00+00:00', updated_at: '2026-11-18T06:00:00+00:00',
      revision: 1, fingerprint: 'a'.repeat(128),
      kind: 'TASK', parent_task_id: null,
    };
    const rows = Array.from({ length: 22 }, (_, index) => ({
      ...base, task_id: 'ptk-' + (index + 1).toString(16).padStart(48, '0'),
      title: 'Batch task ' + String(index + 1).padStart(2, '0'),
      status: index === 21 ? 'DONE' : 'TODO',
    }));
    mockProjectGet(async path => {
      if (path === '/projects') return { data: list([persisted]) };
      if (path === '/projects/summary') return { data: summary([persisted]) };
      if (path === `/projects/${PROJECT_ID}`) return { data: result(persisted) };
      if (path === `/projects/${PROJECT_ID}/tasks?limit=50&offset=0`) return { data: {
        schema: 'WILSY-PROJECT-TASK-LIST/V1', tenant_id: TENANT,
        principal_id: PRINCIPAL, project_id: PROJECT_ID, limit: 50, offset: 0,
        items: rows, has_more: false, next_offset: null,
      } };
      if (path === `/projects/${PROJECT_ID}/participants?limit=100&offset=0`) return { data: {
        schema: 'WILSY-PROJECT-PARTICIPANT-LIST/V1', tenant_id: TENANT,
        principal_id: PRINCIPAL, project_id: PROJECT_ID, limit: 100, offset: 0,
        items: [], has_more: false, next_offset: null,
      } };
      throw new Error('Unexpected GET ' + path);
    });
    render(<ProjectsWorkspace tenantId={TENANT} principalId={PRINCIPAL}
      sessionScope="bounded-project-work-paging-cert"/>);
    fireEvent.click(await screen.findByRole('button', { name: /View project Persisted roadmap/ }));
    await waitFor(() => expect(screen.getByRole('button', { name: 'Batch task 01' })).toBeVisible());
    const grid = screen.getByRole('grid', { name: 'Project work grid' });
    const views = screen.getByRole('group', { name: 'Work lifecycle view' });
    expect(within(views).getByRole('button', { name: 'Active work' })).toHaveAttribute('aria-pressed', 'true');
    expect(within(grid).queryByText('Batch task 22')).not.toBeInTheDocument();
    fireEvent.click(within(views).getByRole('button', { name: 'Completed' }));
    expect(within(grid).getByText('Batch task 22')).toBeVisible();
    expect(within(grid).queryByText('Batch task 01')).not.toBeInTheDocument();
    fireEvent.click(within(grid).getByRole('button', { name: 'Batch task 22' }));
    expect(await screen.findByRole('dialog', { name: 'Work details: Batch task 22' })).toBeVisible();
    fireEvent.click(screen.getByRole('button', { name: 'Close work details' }));
    fireEvent.click(within(views).getByRole('button', { name: 'All work' }));
    expect(within(views).getByRole('button', { name: 'All work' })).toHaveAttribute('aria-pressed', 'true');
    expect(within(grid).getAllByRole('row').length).toBe(11);
    expect(within(grid).queryByText('Batch task 11')).not.toBeInTheDocument();
    fireEvent.click(screen.getAllByRole('button', { name: 'Next view' })[0]);
    expect(within(grid).getByText('Batch task 11')).toBeVisible();
    expect(within(grid).queryByText('Batch task 01')).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole('checkbox', { name: 'Select all visible work' }));
    expect(screen.getByText(/10 selected · verified current EOS batch/)).toBeVisible();
    fireEvent.click(screen.getAllByRole('button', { name: 'Next view' })[0]);
    expect(grid.querySelectorAll('tbody tr[data-task-id]')).toHaveLength(2);
    expect(within(grid).getByText('Batch task 22')).toBeVisible();
    fireEvent.change(screen.getAllByRole('combobox', {
      name: 'Project work rows per view',
    })[0], { target: { value: '20' } });
    expect(grid.querySelectorAll('tbody tr[data-task-id]')).toHaveLength(20);
    expect(within(grid).getByText('Batch task 01')).toBeVisible();
    expect(screen.getByText(/10 selected · verified current EOS batch/)).toBeVisible();
    fireEvent.click(within(views).getByRole('button', { name: 'Completed' }));
    expect(screen.queryByText(/10 selected · verified current EOS batch/)).not.toBeInTheDocument();
    expect(api.post).not.toHaveBeenCalled();
  });

  it('operates real task, subtask and milestone commands from the verified work queue', async () => {
    const persisted = project();
    const parentId = 'ptk-' + 'b'.repeat(48);
    const childId = 'ptk-' + 'c'.repeat(48);
    const milestoneId = 'ptk-' + 'd'.repeat(48);
    const base = {
      schema: 'wilsy.project.task.v1', tenant_id: TENANT, project_id: PROJECT_ID,
      description: '', status: 'TODO', assignee_principal_id: null, due_date: null,
      depends_on: [], created_by_principal_id: PRINCIPAL, updated_by_principal_id: PRINCIPAL,
      created_at: '2026-11-18T06:00:00+00:00', updated_at: '2026-11-18T06:00:00+00:00',
      revision: 1, fingerprint: 'a'.repeat(128),
    };
    const parent = { ...base, task_id: parentId, kind: 'TASK',
      parent_task_id: null, title: 'Main delivery' };
    const child = { ...base, task_id: childId, kind: 'TASK',
      parent_task_id: parentId, title: 'Draft deliverable' };
    const milestone = { ...base, task_id: milestoneId, kind: 'MILESTONE',
      parent_task_id: null, title: 'Sign-off checkpoint' };
    let rows = [parent];
    mockProjectGet(async path => {
      if (path === '/projects') return { data: list([persisted]) };
      if (path === '/projects/summary') return { data: summary([persisted]) };
      if (path === `/projects/${PROJECT_ID}`) return { data: result(persisted) };
      if (path === `/projects/${PROJECT_ID}/tasks?limit=50&offset=0`) return { data: {
        schema: 'WILSY-PROJECT-TASK-LIST/V1', tenant_id: TENANT,
        principal_id: PRINCIPAL, project_id: PROJECT_ID, limit: 50, offset: 0,
        items: rows, has_more: false, next_offset: null,
      } };
      if (path === `/projects/${PROJECT_ID}/participants?limit=100&offset=0`) return { data: {
        schema: 'WILSY-PROJECT-PARTICIPANT-LIST/V1', tenant_id: TENANT,
        principal_id: PRINCIPAL, project_id: PROJECT_ID, limit: 100, offset: 0,
        items: [], has_more: false, next_offset: null,
      } };
      throw new Error('Unexpected GET ' + path);
    });
    api.post.mockImplementation(async (path, body, options) => {
      expect(path).toBe(`/projects/${PROJECT_ID}/tasks`);
      expect(options.headers['X-Tenant-ID']).toBe(TENANT);
      expect(options.headers['Idempotency-Key']).toBeTruthy();
      if (body.kind === 'TASK') {
        expect(body).toMatchObject({ title: 'Draft deliverable',
          parent_task_id: parentId, kind: 'TASK' });
        rows = [parent, child];
      } else {
        expect(body).toMatchObject({ title: 'Sign-off checkpoint',
          parent_task_id: null, kind: 'MILESTONE' });
        rows = [parent, child, milestone];
      }
      return { data: { schema: 'WILSY-PROJECT-TASK-RESULT/V1',
        tenant_id: TENANT, principal_id: PRINCIPAL, project_id: PROJECT_ID,
        task: body.kind === 'TASK' ? child : milestone } };
    });
    render(<ProjectsWorkspace tenantId={TENANT} principalId={PRINCIPAL}
      sessionScope="operational-work-queue-cert"/>);
    fireEvent.click(await screen.findByRole('button', { name: /View project Persisted roadmap/ }));
    await screen.findByRole('region', { name: 'Project work execution' });
    expect(await screen.findByText('Main delivery', {
      selector: '.wp-project-tasks tbody td button',
    })).toBeVisible();
    fireEvent.click(await screen.findByText(/Checklist mode ·/));
    fireEvent.click(screen.getByRole('button', { name: 'Add checklist step to Main delivery' }));
    expect(screen.getByRole('combobox', { name: 'Work type' })).toHaveValue('SUBTASK');
    expect(screen.getByRole('combobox', { name: 'Parent task' })).toHaveValue(parentId);
    expect(screen.getByRole('button', { name: 'Save work to EOS' })).toBeDisabled();
    fireEvent.change(screen.getByPlaceholderText('Deliverable and action'), {
      target: { value: 'Draft deliverable' },
    });
    fireEvent.click(screen.getByRole('button', { name: 'Save work to EOS' }));
    await waitFor(() => expect(screen.getByRole('row', { name: /Draft deliverable/ })).toBeVisible());
    fireEvent.click(screen.getByText(/Work filters, grouping and sorting/));
    fireEvent.change(screen.getByRole('combobox', { name: 'Filter work type' }), {
      target: { value: 'SUBTASK' },
    });
    expect(screen.getByText(/1 matching \/ 2 verified in EOS batch 1\./)).toBeVisible();
    expect(screen.queryByText('Main delivery', {
      selector: '.wp-project-tasks tbody td button',
    })).not.toBeInTheDocument();
    fireEvent.change(screen.getByRole('combobox', { name: 'Filter work type' }), {
      target: { value: 'ALL' },
    });
    fireEvent.click(screen.getByRole('button', { name: 'Create task' }));
    fireEvent.change(screen.getByRole('combobox', { name: 'Work type' }), {
      target: { value: 'MILESTONE' },
    });
    fireEvent.change(screen.getByPlaceholderText('Deliverable and action'), {
      target: { value: 'Sign-off checkpoint' },
    });
    fireEvent.click(screen.getByRole('button', { name: 'Save work to EOS' }));
    await waitFor(() => expect(screen.getByText('Sign-off checkpoint', {
      selector: '.wp-project-tasks tbody td button',
    })).toBeVisible());
    expect(api.post).toHaveBeenCalledTimes(2);
    expect(persisted.status).toBe('planned');
  });

  it('keeps automatic hexadecimal IDs out of the operating project list and header', async () => {
    const generated = 'PRJ-' + 'A'.repeat(16);
    const source = project({ name: 'Human-readable delivery', code: generated });
    mockProjectGet(async path => {
      if (path === '/projects') return { data: list([source]) };
      if (path === '/projects/summary') return { data: summary([source]) };
      if (path === `/projects/${PROJECT_ID}`) return { data: result(source) };
      throw new Error('Unexpected source in project identity presentation test: ' + path);
    });
    render(<ProjectsWorkspace tenantId={TENANT} principalId={PRINCIPAL}
      sessionScope="no-opaque-operating-identity-cert"/>);
    expect(await screen.findByRole('button', {
      name: /View project Human-readable delivery/,
    })).toBeVisible();
    expect(screen.getAllByText('Automatically assigned').length).toBeGreaterThan(0);
    expect(screen.queryByText(generated)).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: /View project Human-readable delivery/ }));
    expect(await screen.findByText('Code assigned')).toBeVisible();
    expect(screen.queryByText(generated)).not.toBeInTheDocument();
  });

  it('reports a missing EOS template route and retries the actual authorized source', async () => {
    let verified = false;
    const steps = [
      { id: 'scope', kind: 'TASK', title: 'Authorised scope',
        day: 4, role: 'lead', acceptance: 'Source scope verified', depends_on: [] },
      { id: 'signoff', kind: 'MILESTONE', title: 'Acceptance',
        day: 10, role: 'sponsor', acceptance: 'Source result signed',
        depends_on: ['scope'] },
    ];
    mockProjectGet(async path => {
      if (path === '/projects') return { data: list([]) };
      if (path === '/projects/summary') return { data: summary([]) };
      if (path === '/projects/templates') {
        if (!verified) throw { response: { status: 404 } };
        return { data: {
          schema: 'WILSY-PROJECT-TEMPLATE-CATALOGUE/V1',
          tenant_id: TENANT, principal_id: PRINCIPAL,
          ownership: 'PLATFORM_STARTERS',
          items: Array.from({ length: 17 }, (_, i) => ({
            slug: 'template-' + i, industry: 'Industry ' + i,
            title: 'Verified plan ' + i, revision: 1, steps,
          })),
        } };
      }
      throw new Error('Unexpected source ' + path);
    });
    render(<ProjectsWorkspace tenantId={TENANT} principalId={PRINCIPAL}
      sessionScope="template-route-retry-cert"/>);
    fireEvent.click(await screen.findByRole('button', { name: 'Create project' }));
    fireEvent.click(screen.getByRole('button', { name: 'Browse industry templates' }));
    expect(await screen.findByText('Diagnostic: HTTP_404_PROJECTS_TEMPLATES_ROUTE_MISSING')).toBeVisible();
    expect(screen.queryByRole('listbox', { name: 'Verified industry templates' }))
      .not.toBeInTheDocument();
    verified = true;
    fireEvent.click(screen.getByRole('button', { name: 'Retry templates' }));
    expect(await screen.findByRole('listbox', { name: 'Verified industry templates' })).toBeVisible();
    expect(screen.getAllByRole('option')).toHaveLength(17);
  });

  it('refuses a mismatched EOS template envelope with actionable diagnostics', async () => {
    mockProjectGet(async path => {
      if (path === '/projects') return { data: list([]) };
      if (path === '/projects/summary') return { data: summary([]) };
      if (path === '/projects/templates') return { data: {
        schema: 'WILSY-PROJECT-TEMPLATE-CATALOGUE/V1',
        tenant_id: 'foreign-tenant', principal_id: PRINCIPAL,
        ownership: 'PLATFORM_STARTERS', items: [],
      } };
      throw new Error('Unexpected source ' + path);
    });
    render(<ProjectsWorkspace tenantId={TENANT} principalId={PRINCIPAL}
      sessionScope="template-envelope-rejection-cert"/>);
    fireEvent.click(await screen.findByRole('button', { name: 'Create project' }));
    fireEvent.click(screen.getByRole('button', { name: 'Browse industry templates' }));
    expect(await screen.findByText('Diagnostic: TEMPLATE_CATALOGUE_ENVELOPE_INVALID')).toBeVisible();
    expect(screen.queryByRole('listbox', { name: 'Verified industry templates' }))
      .not.toBeInTheDocument();
  });

  it('materialises one selected verified industry template only after EOS confirms the project', async () => {
    const persisted = project({ name: 'Legal litigation delivery' });
    const steps = [
      { id: 'first', kind: 'TASK', title: 'Open matter', role: 'project_lead',
        day: 5, acceptance: 'Source document accepted', depends_on: [] },
      { id: 'gate', kind: 'MILESTONE', title: 'Matter readiness', role: 'sponsor',
        day: 10, acceptance: 'Acceptance recorded', depends_on: ['first'] },
    ];
    const industries = ['Legal', 'Construction', 'Football', 'Imports',
      'Software', 'Healthcare', 'General business', 'Marketing',
      'Automotive parts', 'Vehicle dealership', 'Workshop', 'Agriculture',
      'Dental healthcare', 'Workforce', 'Finance operations',
      'Customer success', 'International trading'];
    const catalogue = industries.map((industry, index) => ({
      slug: index === 0 ? 'legal-litigation' : 'template-' + index,
      industry, title: industry + ' delivery', revision: 1, steps,
    }));
    let activated = false;
    mockProjectGet(async path => {
      if (path === '/projects') return { data: list(activated ? [persisted] : []) };
      if (path === '/projects/summary') return { data: summary(activated ? [persisted] : []) };
      if (path === '/projects/templates') return { data: {
        schema: 'WILSY-PROJECT-TEMPLATE-CATALOGUE/V1',
        tenant_id: TENANT, principal_id: PRINCIPAL,
        ownership: 'PLATFORM_STARTERS', items: catalogue,
      } };
      if (path === `/projects/${PROJECT_ID}`) return { data: result(persisted) };
      throw new Error('Unexpected template source ' + path);
    });
    api.post.mockImplementation(async (path, body, options) => {
      expect(path).toBe('/projects/templates/legal-litigation/activate');
      expect(body).toEqual({
        name: 'Legal litigation delivery', template_revision: 1,
        start_date: '2026-11-19',
      });
      expect(options.headers['X-Tenant-ID']).toBe(TENANT);
      expect(options.headers['Idempotency-Key']).toBeTruthy();
      activated = true;
      return { data: {
        schema: 'WILSY-PROJECT-TEMPLATE-ACTIVATION/V1',
        tenant_id: TENANT, principal_id: PRINCIPAL,
        template_slug: 'legal-litigation', template_revision: 1,
        project: persisted,
        items: [
          { template_step_id: 'first', kind: 'TASK', task_id: 'ptk-' + 'a'.repeat(48) },
          { template_step_id: 'gate', kind: 'MILESTONE', task_id: 'ptk-' + 'b'.repeat(48) },
        ],
        authority: {
          iam_grants: false, auto_assignments: false, financial_execution: false,
        },
      } };
    });
    render(<ProjectsWorkspace tenantId={TENANT} principalId={PRINCIPAL}
      sessionScope="industry-template-cert" />);
    fireEvent.click(await screen.findByRole('button', { name: 'Create project' }));
    fireEvent.click(screen.getByRole('button', { name: 'Browse industry templates' }));
    const choices = await screen.findByRole('listbox', { name: 'Verified industry templates' });
    expect(within(choices).getAllByRole('option')).toHaveLength(17);
    fireEvent.click(within(choices).getByRole('option', { name: /Legal/ }));
    expect(screen.getByText('Matter readiness')).toBeVisible();
    expect(screen.getByRole('region', { name: 'WILSY AI project planning' })).toBeVisible();
    expect(screen.getByRole('button', { name: 'Customize included work' })).toBeVisible();
    expect(screen.getByRole('button', { name: 'Generate a reviewable AI plan' })).toBeDisabled();
    expect(screen.queryByText(/legacy starter templates/)).not.toBeInTheDocument();
    expect(screen.queryByText(PROJECT_ID)).not.toBeInTheDocument();
    fireEvent.change(screen.getByLabelText('Project name'), {
      target: { value: 'Legal litigation delivery' },
    });
    fireEvent.change(document.querySelector('input[type="date"]'), {
      target: { value: '2026-11-19' },
    });
    fireEvent.click(screen.getByRole('button', { name: 'Create project and work in EOS' }));
    await waitFor(() => expect(api.post).toHaveBeenCalledTimes(1));
    expect(await screen.findByRole('button', { name: 'Back to projects table' })).toBeVisible();
    expect(persisted.status).toBe('planned');
  });

  it('recovers an ambiguous template response in the list without a duplicate write', async () => {
    const persisted = project({ name: 'Recovered legal delivery' });
    const steps = [
      { id: 'scope', kind: 'TASK', title: 'Review scope', role: 'project_lead',
        day: 1, acceptance: 'Scope verified', depends_on: [] },
      { id: 'gate', kind: 'MILESTONE', title: 'Matter gate', role: 'sponsor',
        day: 3, acceptance: 'Approved evidence', depends_on: ['scope'] },
    ];
    const industries = ['Legal', 'Construction', 'Football', 'Imports',
      'Software', 'Healthcare', 'General business'];
    let committed = false;
    mockProjectGet(async path => {
      if (path === '/projects') return { data: list(committed ? [persisted] : []) };
      if (path === '/projects/summary') return { data: summary(committed ? [persisted] : []) };
      if (path === '/projects/templates') return { data: {
        schema: 'WILSY-PROJECT-TEMPLATE-CATALOGUE/V1', tenant_id: TENANT,
        principal_id: PRINCIPAL, ownership: 'PLATFORM_STARTERS',
        items: industries.map((industry, index) => ({
          slug: index === 0 ? 'legal-litigation' : 'template-' + index,
          industry, title: industry + ' delivery', revision: 1, steps,
        })),
      } };
      throw new Error('Unexpected activation recovery read: ' + path);
    });
    api.post.mockImplementationOnce(async (path, body, options) => {
      expect(path).toBe('/projects/templates/legal-litigation/activate');
      expect(options.headers['Idempotency-Key']).toBeTruthy();
      expect(body.start_date).toBe('2026-11-19');
      committed = true;
      throw Object.assign(new Error('Response unavailable after commit'),
        { response: { status: 503 } });
    });
    render(<ProjectsWorkspace tenantId={TENANT} principalId={PRINCIPAL}
      sessionScope="ambiguous-template-outcome-cert"/>);
    fireEvent.click(await screen.findByRole('button', { name: 'Create project' }));
    fireEvent.click(screen.getByRole('button', { name: 'Browse industry templates' }));
    const picker = await screen.findByRole('listbox', { name: 'Verified industry templates' });
    fireEvent.click(within(picker).getByRole('option', { name: /Legal/ }));
    fireEvent.change(screen.getByLabelText('Project name'), {
      target: { value: 'Recovered legal delivery' },
    });
    fireEvent.change(screen.getByLabelText('Start date date'), {
      target: { value: '2026-11-19' },
    });
    fireEvent.click(screen.getByRole('button', { name: 'Create project and work in EOS' }));
    expect(await screen.findByText(/Save outcome not confirmed/)).toBeVisible();
    expect(screen.getByRole('button', { name: 'Refresh matching projects' })).toBeVisible();
    expect(screen.queryByRole('button', { name: 'Create project and work in EOS' }))
      .not.toBeInTheDocument();
    expect(await screen.findByRole('button', { name: /View project Recovered legal delivery/ }))
      .toBeVisible();
    expect(api.post).toHaveBeenCalledTimes(1);
  });

  it('retains committed EOS template activation when immediate list readback is unavailable', async () => {
    const persisted = project({ name: 'Software implementation' });
    const step = { id: 'scope', kind: 'TASK', title: 'Scope release',
      role: 'project_lead', day: 7, acceptance: 'Approved scope',
      depends_on: [] };
    const milestone = { id: 'gate', kind: 'MILESTONE', title: 'Release readiness',
      role: 'project_sponsor', day: 21, acceptance: 'Certified release',
      depends_on: ['scope'] };
    const industries = ['Legal', 'Construction', 'Football', 'Imports',
      'Software', 'Healthcare', 'General business'];
    mockProjectGet(async path => {
      if (path === '/projects' || path.startsWith('/projects?')) return { data: list([]) };
      if (path === '/projects/summary') return { data: summary([]) };
      if (path === '/projects/templates') return { data: {
        schema: 'WILSY-PROJECT-TEMPLATE-CATALOGUE/V1',
        tenant_id: TENANT, principal_id: PRINCIPAL,
        ownership: 'PLATFORM_STARTERS',
        items: industries.map((industry, i) => ({
          slug: industry === 'Software' ? 'software-release' : 'starter-' + i,
          industry, title: industry + ' implementation', revision: 1, steps: [step, milestone],
        })),
      } };
      throw new Error('Unexpected independent read ' + path);
    });
    api.post.mockResolvedValue({ data: {
      schema: 'WILSY-PROJECT-TEMPLATE-ACTIVATION/V1',
      tenant_id: TENANT, principal_id: PRINCIPAL,
      template_slug: 'software-release', template_revision: 1,
      project: persisted,
      items: [
        { template_step_id: 'scope', kind: 'TASK', task_id: 'ptk-' + 'a'.repeat(48) },
        { template_step_id: 'gate', kind: 'MILESTONE', task_id: 'ptk-' + 'b'.repeat(48) },
      ],
      authority: { iam_grants: false, auto_assignments: false,
        financial_execution: false },
    } });
    render(<ProjectsWorkspace tenantId={TENANT} principalId={PRINCIPAL}
      sessionScope="template-accepted-readback-delay-cert"/>);
    fireEvent.click(await screen.findByRole('button', { name: 'Create project' }));
    fireEvent.click(screen.getByRole('button', { name: 'Browse industry templates' }));
    const choices = await screen.findByRole('listbox', { name: 'Verified industry templates' });
    fireEvent.click(within(choices).getByRole('option', { name: /Software/ }));
    expect(screen.queryByRole('listbox', { name: 'Verified industry templates' })).not.toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Change template' })).toBeVisible();
    fireEvent.change(screen.getByLabelText('Start date date'), {
      target: { value: '2026-11-19' },
    });
    fireEvent.click(screen.getByRole('button', { name: 'Create project and work in EOS' }));
    expect(await screen.findByText(/Project and work saved. Current project details are being verified/)).toBeVisible();
    expect(screen.queryByText(/Save outcome not confirmed/)).not.toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Verify project' })).toBeVisible();
    expect(screen.queryByText(/EOS has not verified template activation/)).not.toBeInTheDocument();
    expect(api.post).toHaveBeenCalledTimes(1);
    expect(screen.queryByText('No projects in this tenant')).not.toBeInTheDocument();
    expect(screen.getByText(/A committed project is awaiting refreshed list visibility/))
      .toBeVisible();
  });

  it('creates source-backed notes in selected project detail without changing Planned', async () => {
    const persisted = project();
    const noteId = `pnt-${'a'.repeat(48)}`;
    const approvedNote = {
      tenant_id: TENANT, project_id: PROJECT_ID, note_id: noteId,
      author_principal_id: PRINCIPAL, revision: 1,
      body: 'Project operating context', colour: 'mint', fingerprint: 'f'.repeat(128),
      created_at: '2026-11-18T06:30:00+00:00',
      updated_at: '2026-11-18T06:30:00+00:00',
      archived_at: null,
    };
    let notes = [];
    mockProjectGet(async (path) => {
      if (path === '/projects') return { data: list([persisted]) };
      if (path === '/projects/summary') return { data: summary([persisted]) };
      if (path === `/projects/${PROJECT_ID}`) return { data: result(persisted) };
      if (path === `/projects/${PROJECT_ID}/notes?limit=50&offset=0`) return {
        data: {
          schema: 'WILSY-PROJECT-NOTE-LIST/V1',
          tenant_id: TENANT, principal_id: PRINCIPAL, project_id: PROJECT_ID,
          items: notes, limit: 50, offset: 0, has_more: false, next_offset: null,
        },
      };
      throw new Error(`Unexpected source read ${path}`);
    });
    api.post.mockImplementation(async (path, body, options) => {
      expect(path).toBe(`/projects/${PROJECT_ID}/notes`);
      expect(options.headers['X-Tenant-ID']).toBe(TENANT);
      expect(options.headers['Idempotency-Key']).toBeTruthy();
      expect(body).toEqual({ body: 'Project operating context', colour: 'mint' });
      notes = [approvedNote];
      return { data: {
        schema: 'WILSY-PROJECT-NOTE-RESULT/V1',
        tenant_id: TENANT, principal_id: PRINCIPAL, project_id: PROJECT_ID,
        note: approvedNote, events: [],
      } };
    });
    render(<ProjectsWorkspace tenantId={TENANT} principalId={PRINCIPAL}
      sessionScope="notes-client-certificate" />);
    fireEvent.click(await screen.findByRole('button', { name: /Persisted roadmap/ }));
    fireEvent.click(screen.getByRole('button', { name: 'Notes', exact: true }));
    expect(await screen.findByRole('region', { name: 'Project notes' })).toBeVisible();
    expect(screen.queryByRole('textbox', { name: 'New project note' })).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: 'New note' }));
    const input = screen.getByRole('textbox', { name: 'New project note' });
    fireEvent.change(input, { target: { value: 'Project operating context' } });
    fireEvent.click(screen.getByRole('button', { name: 'Mint sticky-note colour' }));
    expect(screen.getByRole('button', { name: 'Mint sticky-note colour' }))
      .toHaveAttribute('aria-pressed', 'true');
    fireEvent.click(screen.getByRole('button', { name: 'Save note' }));
    await waitFor(() => {
      expect(screen.getByRole('button', { name: 'Edit project note' })).toBeVisible();
    });
    expect(screen.getByText('Project operating context', { selector: '.wp-notes-list p' })).toBeVisible();
    expect(screen.getByRole('list', { name: 'Project sticky notes board' })).toBeVisible();
    expect(screen.getByText('Your note')).toBeVisible();
    expect(within(screen.getByRole('list', { name: 'Project sticky notes board' }))
      .queryByText('Revision 1')).not.toBeInTheDocument();
    expect(screen.queryByRole('textbox', { name: 'New project note' })).not.toBeInTheDocument();
    expect(api.post).toHaveBeenCalledTimes(1);
    expect(api.patch).not.toHaveBeenCalled();
    expect(persisted.status).toBe('planned');
    expect(screen.getByRole('button', { name: 'Edit project note' })).toBeVisible();
  });

  it('opens a Strategy-handoff project only after EOS lists it for the selected scope', async () => {
    const persisted = project({ name: 'WILSY OS — Unified Operating Platform Foundation' });
    mockProjectGet(async (path) => {
      if (path === '/projects') return { data: list([persisted]) };
      if (path === '/projects/summary') return { data: summary([persisted]) };
      if (path === `/projects/${PROJECT_ID}`) return { data: result(persisted) };
      throw new Error('Unexpected source route');
    });
    render(<ProjectsWorkspace tenantId={TENANT} principalId={PRINCIPAL}
      sessionScope="founder-project-handoff" focusProjectId={PROJECT_ID}/>);
    expect(await screen.findByRole('heading', { name: persisted.name })).toBeVisible();
    fireEvent.click(screen.getByRole('button', { name: 'Audit history' }));
    expect(screen.getByRole('heading', { name: 'Audit events' })).toBeVisible();
    expect(api.get.mock.calls.some(([path]) => path === `/projects/${PROJECT_ID}`)).toBe(true);
    expect(api.patch).not.toHaveBeenCalled();
    expect(api.post).not.toHaveBeenCalled();
  });

  it('opens a Strategy-selected task only after its authorized project and work readback', async () => {
    const persisted = project({ name: 'WILSY OS — Unified Operating Platform Foundation' });
    const taskId = 'ptk-' + 'f'.repeat(48);
    const task = { schema: 'wilsy.project.task.v1', tenant_id: TENANT, project_id: PROJECT_ID,
      task_id: taskId, kind: 'TASK', parent_task_id: null, title: 'Certify production readiness and rollback',
      description: '', status: 'TODO', assignee_principal_id: null, due_date: null, depends_on: [],
      revision: 1, fingerprint: 'a'.repeat(128),
      created_by_principal_id: PRINCIPAL, updated_by_principal_id: PRINCIPAL,
      created_at: '2026-11-22T21:44:56+00:00', updated_at: '2026-11-22T21:44:56+00:00',
    };
    // Optional directories and command authorization deliberately never settle.
    // The verified task must open, but edits must remain disabled.
    const unresolvedAuxiliary = new Promise(() => {});
    mockProjectGet(async path => {
      if (path === '/projects') return { data: list([persisted]) };
      if (path === '/projects/summary') return { data: summary([persisted]) };
      if (path === `/projects/${PROJECT_ID}`) return { data: result(persisted) };
      if (path === `/projects/${PROJECT_ID}/tasks?limit=50&offset=0`) return {
        data: { schema: 'WILSY-PROJECT-TASK-LIST/V1', tenant_id: TENANT,
          principal_id: PRINCIPAL, project_id: PROJECT_ID,
          items: [task], limit: 50, offset: 0, has_more: false, next_offset: null },
      };
      if (path === `/projects/${PROJECT_ID}/participants?limit=100&offset=0`) return {
        data: { schema: 'WILSY-PROJECT-PARTICIPANT-LIST/V1', tenant_id: TENANT,
          principal_id: PRINCIPAL, project_id: PROJECT_ID,
          items: [], limit: 100, offset: 0, has_more: false, next_offset: null },
      };
      throw new Error('Unexpected source read ' + path);
    });
    const projectRead = api.get.getMockImplementation();
    api.get.mockImplementation((path, ...args) => (
      path === `/projects/${PROJECT_ID}/participants?limit=100&offset=0`
        || path === `/projects/${PROJECT_ID}/participant-options?limit=50&offset=0`
        || path === `/projects/${PROJECT_ID}/task-action-capabilities`
        ? unresolvedAuxiliary : projectRead(path, ...args)
    ));
    render(<ProjectsWorkspace tenantId={TENANT} principalId={PRINCIPAL}
      sessionScope="exact-task-handoff-cert" focusProjectId={PROJECT_ID} focusTaskId={taskId}/>);
    expect(await screen.findByRole('dialog', {
      name: 'Work details: Certify production readiness and rollback',
    })).toBeVisible();
    expect(screen.getByRole('button', { name: 'Assign & schedule' })).toBeDisabled();
    const readiness = screen.getByRole('region', { name: 'Source-verified task execution readiness' });
    expect(within(readiness).getByText('Assignment required')).toBeVisible();
    expect(within(readiness).getByText('Due date required')).toBeVisible();
    expect(screen.getByText('Work classification and history').closest('details').open).toBe(false);
    expect(api.post).not.toHaveBeenCalled();
    expect(api.patch).not.toHaveBeenCalled();
  });

  it('refuses Strategy-handoff details when the authorized list omits that project', async () => {
    render(<ProjectsWorkspace tenantId={TENANT} principalId={PRINCIPAL}
      sessionScope="absent-project-handoff" focusProjectId={PROJECT_ID}/>);
    expect(await screen.findByText('No projects in this tenant')).toBeVisible();
    expect(api.get.mock.calls.some(([path]) => path === `/projects/${PROJECT_ID}`)).toBe(false);
  });

  it('uses full-width list until selection and renders governed EOS fields and Markdown accessibly', async () => {
    const source = project({
      code: null, owner_principal_id: null, department_id: null, target_date: null,
      summary: 'Strategy reference (descriptive only).\\n**Project objective**\\nDeliver a real platform.\\n**Scope of execution**\\n1. **Unified identity:** Secure access.\\n**Definition of done**\\nConfirmed EOS result. '.repeat(4),
    });
    mockProjectGet(async (path) => {
      if (path === '/projects') return { data: list([source]) };
      if (path === '/projects/summary') return { data: summary([source]) };
      if (path === `/projects/${PROJECT_ID}`) return { data: result(source) };
      throw new Error('Unexpected project route');
    });
    const { container } = render(<ProjectsWorkspace tenantId={TENANT} principalId={PRINCIPAL} sessionScope="layout-cert"/>);
    await screen.findByText('1 shown · 1 verified');
    expect(container.querySelector('.wp-body')).toHaveAttribute('data-layout', 'list');
    fireEvent.click(screen.getByRole('button', { name: /Persisted roadmap/ }));
    expect(await screen.findByRole('heading', { name: 'Persisted roadmap' })).toBeVisible();
    // The secondary list-return action belongs to project view navigation,
    // never beside the source-owned project title.
    const detail = screen.getByRole('region', { name: 'Project detail' });
    const projectHeader = detail.querySelector('.wp-detail-top');
    const views = within(detail).getByRole('navigation', { name: 'Project workspace views' });
    const allProjects = within(views).getByRole('button', { name: 'Back to projects table' });
    expect(allProjects).toHaveTextContent('All projects');
    expect(projectHeader).not.toContainElement(allProjects);
    expect(projectHeader).toContainElement(screen.getByRole('heading', { name: 'Persisted roadmap' }));
    expect(container.querySelector('.wp-body')).toHaveAttribute('data-layout', 'detail');
    fireEvent.click(screen.getByRole('button', { name: 'Overview', exact: true }));
    expect(screen.getAllByText('Automatically assigned').length).toBeGreaterThan(0);
    expect(screen.getAllByText('Not assigned')).toHaveLength(2);
    expect(screen.getByText('Not scheduled')).toBeVisible();
    expect(screen.getByRole('heading', { name: 'Project objective' })).toBeVisible();
    expect(screen.queryByText('**Project objective**')).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: 'Read full project scope' }));
    expect(screen.getByRole('button', { name: 'Collapse project scope' })).toBeVisible();
    expect(screen.getAllByRole('heading', { name: 'Definition of done' }).length).toBeGreaterThan(0);
    fireEvent.click(screen.getByRole('button', { name: 'Manage project' }));
    expect(screen.queryByLabelText('Project code')).not.toBeInTheDocument();
    expect(screen.getByText('Project code · immutable')).toBeVisible();
    fireEvent.click(screen.getByRole('button', { name: 'Back to projects table' }));
    expect(container.querySelector('.wp-body')).toHaveAttribute('data-layout', 'list');
  });

  it('exposes native calendar pickers and preserves exact source-backed date drafts', async () => {
    const current = project({ name: 'Scheduled milestone', target_date: null });
    mockProjectGet(async path => {
      if (path === '/projects') return { data: list([current]) };
      if (path === '/projects/summary') return { data: summary([current]) };
      if (path === `/projects/${PROJECT_ID}`) return { data: result(current) };
      throw new Error('Unexpected EOS read');
    });
    const pickerSpy = vi.fn();
    const originalShowPicker = HTMLInputElement.prototype.showPicker;
    HTMLInputElement.prototype.showPicker = pickerSpy;
    try {
      const { container } = render(<ProjectsWorkspace tenantId={TENANT}
        principalId={PRINCIPAL} sessionScope="date-picker-cert"/>);
      await screen.findByText('1 shown · 1 verified');
      fireEvent.click(screen.getByRole('button', { name: /Scheduled milestone/ }));
      await screen.findByRole('heading', { name: 'Scheduled milestone' });
      expect(container.querySelector('.wp-body')).toHaveAttribute('data-layout', 'detail');
      fireEvent.click(screen.getByRole('button', { name: 'Manage project' }));
      const target = screen.getByLabelText('Target date');
      expect(screen.queryByLabelText('Start date')).not.toBeInTheDocument();
      expect(screen.getByText('Original start date · immutable')).toBeVisible();
      expect(target).toHaveAttribute('type', 'date');
      fireEvent.click(screen.getByRole('button', { name: 'Choose target date' }));
      expect(pickerSpy).toHaveBeenCalledTimes(1);
      fireEvent.change(target, { target: { value: '2026-12-15' } });
      expect(target).toHaveValue('2026-12-15');
      expect(api.patch).not.toHaveBeenCalled();
    } finally {
      if (originalShowPicker) HTMLInputElement.prototype.showPicker = originalShowPicker;
      else delete HTMLInputElement.prototype.showPicker;
    }
  });

  it('selects verified owner and department through EOS and confirms audited assignment readback', async () => {
    const ownerId = 'verified-owner';
    const departmentId = 'dept-' + 'b'.repeat(32);
    let current = project({ owner_principal_id: null, department_id: null });
    mockProjectGet(async (path) => {
      if (path === '/projects') return { data: list([current]) };
      if (path === '/projects/summary') return { data: summary([current]) };
      if (path === `/projects/${PROJECT_ID}`) return { data: result(current) };
      if (path === '/projects/assignment-options') return { data: {
        schema: 'WILSY-PROJECT-ASSIGNMENT-OPTIONS/V1',
        tenant_id: TENANT,
        principals: [{
          principal_id: ownerId, eligibility: 'VERIFIED_CURRENT',
          first_name: 'Verified', last_name: 'Owner',
        }],
        departments: [{ department_id: departmentId, name: 'Platform Engineering', status: 'ACTIVE', revision: 1 }],
      } };
      throw new Error('Unexpected project GET ' + path);
    });
    api.patch.mockImplementation(async (path, body) => {
      expect(path).toBe(`/projects/${PROJECT_ID}/assignment`);
      expect(body).toEqual({
        expected_revision: 1, owner_principal_id: ownerId, department_id: departmentId,
      });
      current = project({
        owner_principal_id: ownerId, department_id: departmentId, revision: 2,
      });
      return { data: result(current, [event('PROJECT_CREATED', 1), event('PROJECT_UPDATED', 2)]) };
    });

    render(<ProjectsWorkspace tenantId={TENANT} principalId={PRINCIPAL} sessionScope="owner-assignment" />);
    fireEvent.click(await screen.findByRole('button', { name: /Persisted roadmap/ }));
    fireEvent.click(screen.getByRole('button', { name: 'Manage project' }));
    const ownerSelector = await screen.findByRole('combobox', { name: 'Eligible project owner' });
    expect(screen.getByRole('option', { name: 'Verified Owner' })).toHaveValue(ownerId);
    expect(screen.queryByRole('option', { name: ownerId })).not.toBeInTheDocument();
    fireEvent.change(ownerSelector, { target: { value: ownerId } });
    fireEvent.change(screen.getByRole('combobox', { name: 'Tenant department' }), {
      target: { value: departmentId },
    });
    fireEvent.click(screen.getByRole('button', { name: 'Save audited assignment' }));
    await waitFor(() => expect(api.patch).toHaveBeenCalledTimes(1));
    // Wait for source readback, not a presentation-only revision label.
    await waitFor(() => expect(api.get.mock.calls.filter(([path]) =>
      path === `/projects/${PROJECT_ID}`).length).toBeGreaterThan(1));
    fireEvent.click(screen.getByRole('button', { name: 'Overview', exact: true }));
    await waitFor(() => {
      expect(screen.getByText('Assigned Owner')).toBeInTheDocument();
      expect(screen.getByText('Verified Creator')).toBeInTheDocument();
      expect(screen.getByText('Platform Engineering')).toBeVisible();
      expect(screen.queryByText(departmentId)).not.toBeInTheDocument();
    });
    expect(current.status).toBe('planned');
    expect(api.get.mock.calls.filter(([path]) => path === `/projects/${PROJECT_ID}`).length).toBeGreaterThan(1);
  });

  it('does not offer assignment when current owner and department directories are empty', async () => {
    mockProjectGet(async (path) => {
      if (path === '/projects') return { data: list([project()]) };
      if (path === '/projects/summary') return { data: summary([project()]) };
      if (path === `/projects/${PROJECT_ID}`) return { data: result(project()) };
      if (path === '/projects/assignment-options') return { data: {
        schema: 'WILSY-PROJECT-ASSIGNMENT-OPTIONS/V1',
        tenant_id: TENANT, principals: [], departments: [],
      } };
      throw new Error('Unexpected project GET ' + path);
    });
    render(<ProjectsWorkspace tenantId={TENANT} principalId={PRINCIPAL} sessionScope="empty-authorities" />);
    fireEvent.click(await screen.findByRole('button', { name: /Persisted roadmap/ }));
    fireEvent.click(screen.getByRole('button', { name: 'Manage project' }));
    await waitFor(() => expect(screen.getByRole('button', { name: 'Save audited assignment' })).toBeDisabled());
    expect(screen.getByText('EOS verified 0 eligible project owners and 0 active tenant departments.')).toBeInTheDocument();
    const accountability = screen.getByRole('region', { name: 'Project accountability' });
    expect(accountability).toHaveClass('wp-accountability');
    expect(screen.getByRole('combobox', { name: 'Eligible project owner' })).toBeDisabled();
    expect(screen.getByRole('combobox', { name: 'Tenant department' })).toBeDisabled();
    expect(screen.getByText(/No eligible project owner has been verified/)).toBeInTheDocument();
    expect(screen.getByText(/No active canonical tenant department is recorded/)).toBeInTheDocument();
    expect(api.patch).not.toHaveBeenCalled();
  });

  it('generates a code for an existing legacy project and verifies EOS list/detail readback', async () => {
    let persisted = project({ code: null });
    const generated = 'PRJ-' + PROJECT_ID.slice(-16).toUpperCase();
    mockProjectGet(async path => {
      if (path === '/projects') return { data: list([persisted]) };
      if (path === '/projects/summary') return { data: summary([persisted]) };
      if (path === `/projects/${PROJECT_ID}`) return { data: result(persisted) };
      throw new Error('Unexpected EOS GET');
    });
    api.patch.mockImplementation(async (path, body) => {
      expect(path).toBe(`/projects/${PROJECT_ID}`);
      expect(body).toEqual({ expected_revision: 1, code: generated });
      persisted = project({ ...persisted, code: generated, revision: 2 });
      return { data: result(persisted) };
    });
    render(<ProjectsWorkspace tenantId={TENANT} principalId={PRINCIPAL}
      sessionScope="code-generation-cert"/>);
    await screen.findByText('1 shown · 1 verified');
    fireEvent.click(screen.getByRole('button', { name: /Persisted roadmap/ }));
    fireEvent.click(screen.getByRole('button', { name: 'Overview', exact: true }));
    expect((await screen.findAllByText('Automatically assigned')).length).toBeGreaterThan(0);
    fireEvent.click(screen.getByRole('button', { name: 'Generate and save code' }));
    await waitFor(() => expect(api.patch).toHaveBeenCalledTimes(1));
    await waitFor(() => expect(screen.queryByRole('button', { name: 'Generate and save code' })).not.toBeInTheDocument());
    expect(api.get.mock.calls.filter(([path]) => path === '/projects').length).toBeGreaterThan(1);
    expect(api.get.mock.calls.filter(([path]) => path === `/projects/${PROJECT_ID}`).length).toBeGreaterThan(1);
    expect(screen.queryByRole('button', { name: 'Generate and save code' })).not.toBeInTheDocument();
  });

  it('creates, reads, updates, changes status, archives and reads back through EOS routes', async () => {
    let current = null;
    let events = [];
    mockProjectGet(async (path) => {
      if (path === '/projects') return { data: list(current && !current.archived_at ? [current] : []) };
      if (path === '/projects/summary') return { data: summary(current && !current.archived_at ? [current] : []) };
      if (path === `/projects/${PROJECT_ID}` && current && !current.archived_at) return { data: result(current, events) };
      throw new Error(`Unexpected project GET ${path}`);
    });
    api.post.mockImplementation(async (path, body) => {
      if (path === '/projects') {
        current = project({ name: body.name, summary: body.summary || '', code: body.code || '' });
        events = [event('PROJECT_CREATED', current.revision)];
        return { data: result(current, events) };
      }
      if (path === `/projects/${PROJECT_ID}/archive`) {
        current = project({ ...current, archived_at: '2026-11-16T12:10:00+00:00', revision: current.revision + 1, updated_at: '2026-11-16T12:10:00+00:00' });
        events = [...events, event('PROJECT_ARCHIVED', current.revision)];
        return { data: result(current, events) };
      }
      throw new Error(`Unexpected project POST ${path}`);
    });
    api.patch.mockImplementation(async (path, body) => {
      if (path !== `/projects/${PROJECT_ID}` || body.expected_revision !== current.revision) {
        throw Object.assign(new Error('revision conflict'), { response: { status: 409 } });
      }
      current = project({ ...current, ...body, revision: current.revision + 1, updated_at: '2026-11-16T12:09:00+00:00' });
      events = [...events, event(body.status ? 'PROJECT_STATUS_TRANSITION' : 'PROJECT_UPDATED', current.revision)];
      return { data: result(current, events) };
    });

    render(<ProjectsWorkspace tenantId={TENANT} principalId={PRINCIPAL} sessionScope="owner-session-1"/>);
    expect(await screen.findByText('No projects in this tenant')).toBeInTheDocument();
    expect(screen.getByText('0 active · 0 total')).toBeInTheDocument();

    fireEvent.click(screen.getByRole('button', { name: 'Create project' }));
    fireEvent.change(screen.getByLabelText('Project name'), { target: { value: 'Persisted roadmap' } });
    fireEvent.change(screen.getByLabelText(/Summary/), { target: { value: 'Source-confirmed project' } });
    fireEvent.click(screen.getByRole('button', { name: 'Save project to EOS' }));
    expect(await screen.findByRole('heading', { name: 'Persisted roadmap' })).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: 'Audit history' }));
    expect(screen.getByText('PROJECT_CREATED')).toBeInTheDocument();
    expect(screen.getByText(/By Verified Creator · revision/)).toBeInTheDocument();
    expect(api.post).toHaveBeenCalledWith('/projects', expect.objectContaining({ name: 'Persisted roadmap' }), expect.objectContaining({
      headers: { 'X-Tenant-ID': TENANT, 'Idempotency-Key': 'stable-project-key-1' },
    }));

    fireEvent.click(screen.getByRole('button', { name: 'Manage project' }));
    fireEvent.change(screen.getByLabelText('Name'), { target: { value: 'Updated roadmap' } });
    fireEvent.click(screen.getByRole('button', { name: 'Save revision' }));
    await waitFor(() => expect(api.patch).toHaveBeenCalledTimes(1));
    await waitFor(() => expect(screen.getByRole('heading', { name: 'Updated roadmap' })).toBeInTheDocument());
    expect(api.patch.mock.calls[0][1].expected_revision).toBe(1);

    fireEvent.change(screen.getByLabelText('Project status'), { target: { value: 'active' } });
    await waitFor(() => expect(api.patch).toHaveBeenCalledTimes(2));
    await waitFor(() => expect(screen.getByLabelText('Project status').value).toBe('active'));
    expect(api.patch.mock.calls[1][1]).toMatchObject({ expected_revision: 2, status: 'active' });
    expect(screen.getByLabelText('Project status')).toHaveValue('active');
    expect(api.get).toHaveBeenCalledWith('/projects/summary', expect.anything());

    fireEvent.click(screen.getByRole('button', { name: 'Archive' }));
    expect(await screen.findByText('No projects in this tenant')).toBeInTheDocument();
    expect(screen.getByText('0 active · 0 total')).toBeInTheDocument();
    expect(api.post).toHaveBeenLastCalledWith(`/projects/${PROJECT_ID}/archive`, { expected_revision: 3 }, expect.objectContaining({
      headers: { 'X-Tenant-ID': TENANT, 'Idempotency-Key': 'stable-project-key-4' },
    }));
    expect(events.map((entry) => entry.event_type)).toEqual([
      'PROJECT_CREATED', 'PROJECT_UPDATED', 'PROJECT_STATUS_TRANSITION', 'PROJECT_ARCHIVED',
    ]);
  });

  it('orders verified project audit events by revision without changing EOS evidence', async () => {
    const current = project({ revision: 4, status: 'active' });
    const evidence = [
      event('PROJECT_CREATED', 1), event('PROJECT_UPDATED', 3),
      event('PROJECT_STATUS_TRANSITION', 4), event('PROJECT_UPDATED', 2),
    ];
    mockProjectGet(async path => {
      if (path === '/projects') return { data: list([current]) };
      if (path === '/projects/summary') return { data: summary([current]) };
      if (path === `/projects/${PROJECT_ID}`) return { data: result(current, evidence) };
      throw new Error('Unexpected project GET ' + path);
    });
    render(<ProjectsWorkspace tenantId={TENANT} principalId={PRINCIPAL}
      sessionScope="audit-visual-newest-first-cert"/>);
    fireEvent.click(await screen.findByRole('button', { name: /View project Persisted roadmap/ }));
    fireEvent.click(screen.getByRole('button', { name: 'Audit history' }));
    const audit = await screen.findByRole('region', { name: 'Project audit timeline' });
    const entries = [...audit.querySelectorAll('[data-audit-revision]')];
    expect(entries.map(element => Number(element.getAttribute('data-audit-revision'))))
      .toEqual([4, 3, 2, 1]);
    expect(entries[0]).toHaveTextContent('PROJECT_STATUS_TRANSITION');
    expect(entries[0]).toHaveTextContent('Latest returned event');
    expect(entries[3]).toHaveTextContent('PROJECT_CREATED');
    expect(evidence.map(item => item.revision)).toEqual([1, 3, 4, 2]);
  });

  it('reuses the same create idempotency key after an uncertain outcome and requires list/detail readback', async () => {
    let listReads = 0;
    let present = false;
    mockProjectGet(async (path) => {
      if (path === '/projects') {
        listReads += 1;
        return { data: list(present && listReads >= 3 ? [project()] : []) };
      }
      if (path === '/projects/summary') return { data: summary(present && listReads >= 3 ? [project()] : []) };
      if (path === `/projects/${PROJECT_ID}` && present) return { data: result(project()) };
      throw new Error(`Unexpected project GET ${path}`);
    });
    api.post
      .mockRejectedValueOnce(new Error('network outcome unknown'))
      .mockImplementationOnce(async () => { present = true; return { data: result(project()) }; });

    render(<ProjectsWorkspace tenantId={TENANT} principalId={PRINCIPAL} sessionScope="session-generation-1"/>);
    await waitFor(() => expect(screen.getByText('No projects in this tenant')).toBeInTheDocument());
    fireEvent.click(screen.getByRole('button', { name: 'Create project' }));
    fireEvent.change(screen.getByLabelText('Project name'), { target: { value: 'Persisted roadmap' } });
    fireEvent.click(screen.getByRole('button', { name: 'Save project to EOS' }));
    await waitFor(() => expect(api.post).toHaveBeenCalledTimes(1));
    await waitFor(() => expect(screen.getByRole('alert')).toHaveTextContent(/could not confirm/i));
    fireEvent.click(screen.getByRole('button', { name: 'Save project to EOS' }));
    await waitFor(() => expect(api.post).toHaveBeenCalledTimes(2));
    expect(api.post.mock.calls[0][2].headers['Idempotency-Key'])
      .toBe(api.post.mock.calls[1][2].headers['Idempotency-Key']);
    expect(await screen.findByRole('heading', { name: 'Persisted roadmap' })).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: 'Audit history' }));
    expect(screen.getByText('PROJECT_CREATED')).toBeInTheDocument();
    expect(screen.getByText(/By Verified Creator · revision/)).toBeInTheDocument();
  });

  it('keeps an independently verified project accessible when summary returns HTTP 503', async () => {
    const persisted = project();
    mockProjectGet(async path => {
      if (path === '/projects') return { data: list([persisted]) };
      if (path === '/projects/summary') throw Object.assign(new Error('temporary summary outage'), {
        response: { status: 503 },
      });
      if (path === `/projects/${PROJECT_ID}`) return { data: result(persisted) };
      throw new Error('Unexpected GET ' + path);
    });
    render(<ProjectsWorkspace tenantId={TENANT} principalId={PRINCIPAL}
      sessionScope="summary-503-isolated-cert"/>);
    const projectRow = await screen.findByRole('button', { name: /View project Persisted roadmap/ });
    expect(screen.getByText('Counts unavailable')).toBeVisible();
    fireEvent.click(projectRow);
    expect(await screen.findByRole('heading', { name: 'Persisted roadmap' })).toBeVisible();
    expect(screen.queryByText(/latest EOS read failed/i)).not.toBeInTheDocument();
  });

  it('does not invalidate a rendered authorized project when a delayed summary returns 503', async () => {
    const persisted = project();
    let rejectSummary;
    const delayed = new Promise((resolve, reject) => { rejectSummary = reject; });
    mockProjectGet(async path => {
      if (path === '/projects') return { data: list([persisted]) };
      if (path === '/projects/summary') return delayed;
      if (path === `/projects/${PROJECT_ID}`) return { data: result(persisted) };
      throw new Error('Unexpected GET ' + path);
    });
    render(<ProjectsWorkspace tenantId={TENANT} principalId={PRINCIPAL}
      sessionScope="summary-late-503-isolated-cert"/>);
    fireEvent.click(await screen.findByRole('button', { name: /View project Persisted roadmap/ }));
    expect(await screen.findByRole('heading', { name: 'Persisted roadmap' })).toBeVisible();
    await act(async () => {
      rejectSummary(Object.assign(new Error('summary unavailable'), { response: { status: 503 } }));
      await Promise.resolve();
    });
    expect(screen.getByRole('heading', { name: 'Persisted roadmap' })).toBeVisible();
    expect(screen.queryByText('Counts unavailable')).not.toBeInTheDocument();
    expect(screen.queryByText(/latest EOS read failed/i)).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: 'Back to projects table' }));
    expect(await screen.findByText('Counts unavailable')).toBeVisible();
    expect(await screen.findByRole('button', { name: /View project Persisted roadmap/ })).toBeVisible();
  });

  it('shows source-honest department and readable audit labels in project overview', async () => {
    const current = project({ department_id: 'dept-' + 'a'.repeat(32) });
    mockProjectGet(async path => {
      if (path === '/projects') return { data: list([current]) };
      if (path === '/projects/summary') return { data: summary([current]) };
      if (path === `/projects/${PROJECT_ID}`) return { data: result(current) };
      throw new Error('Unexpected GET ' + path);
    });
    render(<ProjectsWorkspace tenantId={TENANT} principalId={PRINCIPAL}
      sessionScope="readable-overview-cert"/>);
    fireEvent.click(await screen.findByRole('button', { name: /View project Persisted roadmap/ }));
    fireEvent.click(screen.getByRole('button', { name: 'Overview' }));
    expect(await screen.findByText('Assigned department · name unavailable')).toBeVisible();
    expect(screen.getByText('Audited creator')).toHaveClass('text-slate-800');
    expect(screen.queryByText(current.department_id)).not.toBeInTheDocument();
  });

  it('rejects a foreign tenant summary instead of presenting it as verified empty', async () => {
    mockProjectGet(async (path) => path === '/projects'
      ? { data: list([]) }
      : { data: summary([], 'another-tenant') });
    render(<ProjectsWorkspace tenantId={TENANT} principalId={PRINCIPAL} sessionScope="foreign-response-test"/>);
    expect(await screen.findByRole('alert')).toHaveTextContent(/Projects couldn't load/i);
    expect(screen.queryByText('No projects in this tenant')).not.toBeInTheDocument();
    expect(screen.queryByText('0 active · 0 total')).not.toBeInTheDocument();
  });

  it('renders authorization denial without presenting an empty project state', async () => {
    api.get.mockRejectedValue(Object.assign(new Error('denied'), {
      response: { status: 403, data: { detail: 'UNEXPECTED_SERVER_TEXT' } },
    }));
    render(<ProjectsWorkspace tenantId={TENANT} principalId={PRINCIPAL} sessionScope="denied-session"/>);
    await waitFor(() => expect(screen.getByRole('alert')).toHaveTextContent(/EOS denied Projects access/i));
    expect(screen.queryByText('No projects in this tenant')).not.toBeInTheDocument();
    expect(screen.queryByText(/0 active/)).not.toBeInTheDocument();
  });

  it('keeps late list results from a prior tenant/principal/capacity scope out of the new workspace', async () => {
    let resolvePriorList;
    let listCalls = 0;
    const priorList = new Promise((resolve) => { resolvePriorList = resolve; });
    mockProjectGet(async (path, config = {}) => {
      if (path === '/projects') {
        listCalls += 1;
        if (listCalls === 1) return priorList;
        const nextTenantProject = project({ project_id: `prj-${'b'.repeat(48)}`, tenant_id: 'projects-cert-tenant-b', name: 'Tenant B record' });
        return { data: list([nextTenantProject], 'projects-cert-tenant-b', 'projects-cert-principal-b') };
      }
      const tenant = config.headers?.['X-Tenant-ID'];
      const principal = tenant === 'projects-cert-tenant-b' ? 'projects-cert-principal-b' : PRINCIPAL;
      const items = tenant === 'projects-cert-tenant-b' ? [project({ project_id: `prj-${'b'.repeat(48)}`, tenant_id: tenant, name: 'Tenant B record' })] : [];
      return { data: summary(items, tenant, principal) };
    });
    const { rerender } = render(<ProjectsWorkspace tenantId={TENANT} principalId={PRINCIPAL} sessionScope="capacity-owner"/>);
    await waitFor(() => expect(listCalls).toBe(1));
    rerender(<ProjectsWorkspace tenantId="projects-cert-tenant-b" principalId="projects-cert-principal-b" sessionScope="capacity-manager"/>);
    expect(await screen.findByText('Tenant B record')).toBeInTheDocument();
    await act(async () => { resolvePriorList({ data: list([project({ name: 'Stale tenant A item' })]) }); });
    expect(screen.queryByText('Stale tenant A item')).not.toBeInTheDocument();
  });
  it('publishes bounded AI locators after source verification and clears them on exit', async () => {
    const events = [];
    const capture = event => events.push(event.detail);
    window.addEventListener('wilsy:ai-context-locator', capture);
    const value = project();
    mockProjectGet(async path => {
      if (path === '/projects') return { data: list([value]) };
      if (path === '/projects/summary') return { data: summary([value]) };
      if (path === `/projects/${PROJECT_ID}`) return { data: result(value) };
      throw new Error('Unused child source');
    });
    const mounted = render(<ProjectsWorkspace tenantId={TENANT} principalId={PRINCIPAL} sessionScope="locator-scope"/>);
    try {
      fireEvent.click(await screen.findByRole('button', { name: /View project Persisted roadmap/ }));
      await waitFor(() => expect(events.at(-1)).toEqual({ tenantId: TENANT, principalId: PRINCIPAL,
        locator: { workspace: 'PROJECTS', project_id: PROJECT_ID, project_revision: 1 } }));
      expect(JSON.stringify(events)).not.toContain('Source-confirmed project');
      expect(JSON.stringify(events)).not.toContain('Verified Creator');
      events.length = 0;
      window.dispatchEvent(new CustomEvent('wilsy:ai-context-request'));
      expect(events.at(-1).locator.project_id).toBe(PROJECT_ID);
      mounted.unmount();
      expect(events.at(-1).locator).toEqual({ workspace: 'HEADQUARTERS' });
      const afterExit = events.length;
      window.dispatchEvent(new CustomEvent('wilsy:ai-context-request'));
      expect(events).toHaveLength(afterExit);
      expect(api.post).not.toHaveBeenCalled();
    } finally {
      window.removeEventListener('wilsy:ai-context-locator', capture);
    }
  });
});

/*
 * ARTIFACT: WILSY OS Projects workspace interaction certificate
 * VERSION: v2.80.0-COMPLETED-WORK-LIFECYCLE-VIEWS-CERT
 * AUTHORITY BOUNDARY: Synthetic client transport only; EOS remains authoritative.
 * TENANT POSTURE: Tests validate synthetic exact tenant/principal scope; live isolation is not claimed.
 * FAIL-CLOSED POSTURE: Uncertainty and denial cannot create client-side business truth.
 * FINANCIAL EXECUTION AUTHORITY: None; Kennel EOS exclusively.
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
