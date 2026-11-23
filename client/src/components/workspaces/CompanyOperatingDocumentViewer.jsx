/**
 * TITLE: WILSY OS Mission and Strategy Document Experience
 * VERSION: v2.21.0-ACTIONABLE-ACCOUNTABILITY-FILTERS
 * AUTHORITY: Python EOS owns content, publication, IAM and durable revision truth.
 * EPITOME: One accessible full-height document drawer for Mission and Strategy,
 *          including honest unpublished state and separately authorized review.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/components/workspaces/CompanyOperatingDocumentViewer.jsx
 * COLLABORATION / OWNERSHIP: Headquarters opens the drawer; AuthContext supplies
 * current scope; companyOperatingDocumentsClient validates source contracts.
 * CERTIFICATION / UPDATE DATE: 2026-11-23
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; keyboard accessibility.
 * SECURITY / PRIVACY POSTURE: Plain React text only; no persisted draft, generated
 * policy, inferred objectives, raw diagnostics or credentials in DOM/logs.
 * TENANT BOUNDARY: Exact current tenant/principal/session and credential revision;
 * scope changes abort reads and suppress late results, drafts and receipts.
 * AUTHORITY BOUNDARY: UI actions never grant permission. Source endpoints
 * reauthorize every command; acknowledgement alone is not verified publication.
 * FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively.
 * CHANGELOG: v2.21.0-ACTIONABLE-ACCOUNTABILITY-FILTERS
 *            turns verified M04 accountability counts into accessible
 *            source-safe work filters; activating any count opens the existing
 *            bounded task/evidence inspector, never mutates an EOS record.
 * CHANGELOG: v2.20.0-ACTIVE-MODES-FOCUSED-PROJECTS
 *            highlights selected Strategy modes; keeps governance context
 *            in an on-demand disclosure; filters tenant project display
 *            locally while retaining exact EOS source and linkage evidence.
 * CHANGELOG: v2.19.0-COMPACT-PUBLISHED-STRATEGY-HEADER
 *            consolidates redundant publication, handoff and mode panels
 *            into one accessible execution-first status/navigation surface.
 *            Retains source-admitted private review and independent link
 *            verification without inventing a relationship or outcome.
 * CHANGELOG: v2.18.1-STRATEGY-MODE-ACTION-ROUTING
 *            routes Current publication to focused document mode, and
 *            Inspect Projects & Delivery back to execution when document is
 *            open; no source commands or authority changes.
 * CHANGELOG: v2.18.0-EXECUTION-FIRST-PUBLICATION-VIEW
 *            defaults currently published Strategy to governed Execution mode;
 *            mounts the full immutable publication only on request, retaining
 *            source provenance, authority, history and current-link validation.
 *            Contents navigation opens document mode before section scrolling;
 *            nonpublished, private-review and Mission workflows are unchanged.
 * CHANGELOG: v2.17.0-FOCUSED-EXECUTION-NAVIGATION
 *            adds bounded searchable/paged M04 source-owned work inspection
 *            and hides repeated legacy task and plan registers until requested.
 *            Search and filters never change EOS truth, completeness, IAM or
 *            task evidence; source verification remains over the full page.
 * CHANGELOG: v2.16.0-ON-DEMAND-DOCUMENT-CONTENTS
 *            defaults the lengthy Contents navigation to collapsed,
 *            expands it on demand via an accessible toolbar toggle, and
 *            gives document/execution the reclaimed width without altering
 *            source reads, publishing, task authority or evidence.
 * CHANGELOG: v2.15.2-M04-CANONICAL-PROJECT-STATUS
 *            compares Strategy execution project status with Python EOS
 *            ProjectStatus.ACTIVE.value ('active'), not IAM's 'ACTIVE'.
 *            Keeps all link revision, task and tenant gates unchanged.
 * CHANGELOG: v2.15.1-M04-EXECUTION-GATE-DIAGNOSTICS
 *            reveals the exact independent M04 gate failing source
 *            verification without relaxing currentness, IAM or evidence.
 * CHANGELOG: v2.15.0-M04-PUBLISHED-EXECUTION-HANDOFF
 *            retires repeated M03 approval gates and publication-stage
 *            controls from already-published Strategy; retains independently
 *            governed private revision review and gives the published view
 *            one actionable handoff to existing Projects execution readback.
 *            No publication, Strategy link, task or IAM writes are added.
 * CHANGELOG: v2.14.1-M04-PUBLISHED-ACTION-GUARD
 *            suppresses completed v1.1.0 preparation after EOS publication,
 *            distinguishes private revision selection from publication truth,
 *            and retains independent project-link and evidence checks.
 * CHANGELOG: v2.14.0-M04-GOVERNANCE-SOURCE-CONSISTENCY
 *            aligns source help text with already-ratified Founder
 *            publication, current Strategy link and separate Projects IAM.
 *            This revision makes no additional authority or task writes.
 * CHANGELOG: v2.13.1-M04-APPROVAL-ID-CONTRACT
 *            honors ProjectApprovalRegistry's canonical par- identifier.
 * CHANGELOG: v2.13.0-M04-SEPARATE-EVIDENCE-SOURCE-READ
 *            verifies DONE task activity together with independently
 *            current project approval and attachment pages, distinguishing
 *            source-audited status, business decisions and scanner clearance
 *            from approved Strategy outcomes. Missing or paged source fails
 *            closed, and no attachment byte/capability is exposed.
 * CHANGELOG: v2.12.1-M04-EVIDENCE-CONTIGUITY checks
 *            contiguous task revision-event chains, preventing an omitted
 *            middle lifecycle transition from being described as complete;
 *            recorded assignee ID does not claim live IAM eligibility.
 * CHANGELOG: v2.12.0-M04-PRIORITIZED-EXECUTION-WORKSPACE
 *            exposes source-owned M04 execution directly after the selected
 *            project heading, above long task lists. No second project,
 *            task workflow or outcome computation is introduced.
 * CHANGELOG: v2.11.1-M04-CANONICAL-DATE-WIRE validates
 *            EOS date-only ISO fields as digits, never literal escapes.
 * CHANGELOG: v2.11.0-M04-GOVERNED-EXECUTION-EVIDENCE
 *            derives a fail-closed operational work graph only after the
 *            current published Pillar 1 link, full exact-project task
 *            source, predecessor/owner/deadline integrity and current
 *            revision are verified. Separate on-demand Projects event
 *            readback exposes durable lifecycle evidence; neither DONE
 *            nor an event is a certified strategic outcome. No new task
 *            registry, approval authority or outcome percentage is created.
 * CHANGELOG: v2.10.0-PUBLISHED-STRATEGY-CONFLICT-RECOVERY
 *            reconciles a refused duplicate Strategy version against
 *            independently verified, immutable EOS published history and
 *            fingerprint before changing views. Unknown status stays
 *            unknown; no command is replayed automatically.
 * CHANGELOG: v2.9.1-FOUNDER-RATIFICATION-PRIMARY-ACTION
 *            makes ratification available directly in the top command rail
 *            for a verified submitted Founder revision and replaces the
 *            irrelevant independent-approval label without new commands.
 * CHANGELOG: v2.9.0-DIRECT-FOUNDER-RATIFICATION-WORKSPACE
 *            transitions submitted Strategy directly into a focused
 *            Founder ratification form, rather than scrolling past six
 *            pillars and Projects. Returns to verified submitted view on
 *            cancel; resets scroll and focuses date picker on entry. EOS
 *            still owns all publication authority, command and readback.
 * CHANGELOG: v2.8.1-FOCUSED-COMMAND-REJECTION focuses
 *            the visible, sanitized rejection immediately after a failed
 *            command, even when the author was scrolled to the Save control.
 * CHANGELOG: v2.8.0-AUDITABLE-COMMAND-REJECTION separates
 *            rejected source writes from failed document reads, preserves
 *            unsaved author input, and displays whitelisted HTTP validation
 *            field paths without leaking rejected content or declaring a
 *            successful write. No IAM/document mutation behavior changes.
 * CHANGELOG: v2.7.1-FOCUSED-AUTHOR-VIEWPORT restores the
 *            modal scroll position and moves focus into the private editor
 *            when prepared, preventing hidden steps after viewing project
 *            details. No backend mutations or permission changes.
 * CHANGELOG: v2.7.0-DIRECT-AUTHOR-WORKSPACE renders the private
 *            draft editor immediately below the active command rail and
 *            replaces the long publication/Projects read-only content while
 *            editing. Closing restores the unchanged live source view. No
 *            Strategy write, authorization or persistence semantics change.
 * CHANGELOG: v2.6.1-FOUNDER-PILLAR-LINK-HANDOFF chooses the
 *            separately source-admitted Founder Strategy link endpoint after
 *            effective publication, preserving exact revisions, IAM Projects
 *            read, idempotency and independent relationship readback.
 * CHANGELOG: v2.6.0-FOUNDER-STRATEGY-COMMAND-STUDIO uses only
 *            EOS-admitted durable Founder command actions for Strategy
 *            creation, submission and explicit effective-date ratification.
 *            Every write requires independent fingerprint readback.
 * CHANGELOG: v2.5.0-M03-PUBLICATION-AUTHORITY-GATES exposes
 *            source-verified current-session author/review actions, distinct
 *            independent publisher verification, effective publication,
 *            and existing Pillar 1 relationship status as governed gates.
 *            No IAM grant or write is attempted by the readiness display.
 * CHANGELOG: v2.4.0-M02-LIVE-EXECUTION-READBACK derives
 *            lifecycle, dependency and past-due calendar counts only from a
 *            complete validated live EOS project snapshot and all 18 unique
 *            plan identities; captures client-observed successful-read time.
 *            Incomplete coverage suppresses metrics, not just a badge.
 * CHANGELOG: v2.3.0-STRATEGY-IMPLEMENTATION-EXECUTION-HANDOFF
 *            shows each plan record's EOS lifecycle state independently of
 *            persistence, and opens its existing project workspace for
 *            source-authorized execution. No completion, IAM, strategy link,
 *            document publication, or project/task creation is inferred.
 * CHANGELOG: v2.2.3-HEADER-INSPECTION-COMPLIANCE
 *            moves existing mandatory governance fields into the inspected
 *            source header boundary; no runtime behavior or IAM change.
 * CHANGELOG: v2.2.2-PROJECT-LIST-RETRY-STATUS-DIAGNOSTICS
 *            distinguishes a timed-out Projects read from a source HTTP 503,
 *            avoids falsely claiming the Strategy link schema is absent, and
 *            preserves fail-closed unverified project-list presentation.
 * CHANGELOG: v2.2.1-CLASSIFICATION-SCOPED-PUBLISH-ACCESSIBILITY
 *            makes independent approval form labeling dynamic by current
 *            source classification; Mission is never mislabeled Strategy.
 * CHANGELOG: v2.2.0-GOVERNED-STRATEGY-PUBLICATION-HANDOFF exposes
 *            source-state-specific draft, submit and distinct publisher
 *            handoffs in the current Strategy drawer, with accessible
 *            follow-through to existing EOS-authorized commands. No automatic
 *            approval, IAM grant, fabricated publication or synthetic progress.
 * CHANGELOG: v2.1.1-PUBLICATION-GATED-STRATEGY-LINK-RECOVERY identifies
 *            EOS's exact unpublished-Strategy 409 separately from IAM and
 *            transport failure, shows an authorized private-review handoff,
 *            and blocks link commands before publication. A Founder-approved
 *            source proposal is never substituted for published EOS truth.
 * CHANGELOG: v2.1.0-SOURCE-GOVERNED-STRATEGY-PROJECT-LINK reads
 *            separately governed Strategy/project link status through EOS,
 *            validates exact tenant/principal/project/pillar, and offers a
 *            deliberate source-authorized idempotent relationship command
 *            only after 18 plan items are verified. A link is not a score
 *            or Strategy publication and never implies financial authority.
 * CHANGELOG: v2.0.1-PARTIAL-PLAN-ADMISSION-RECOVERY shows real
 *            verified/remaining plan counts after a partial EOS admission;
 *            offers an explicit remaining-only retry, and disables creation
 *            after all 18 matching source-owned items are verified.
 * CHANGELOG: v2.0.0-GOVERNED-STRATEGY-PLAN-ADMISSION distinguishes the
 *            roadmap's six proposed milestones and twelve implementation
 *            tasks from EOS-persisted work. Explicit source-authorized plan
 *            admission checks the complete bounded project page, skips exact
 *            existing plan records, uses stable per-item idempotency and
 *            requires independent persisted readback after each create.
 *            No assignees, deadlines, dependencies or progress are inferred.
 * CHANGELOG: v1.9.0-STRATEGY-PROJECT-EXECUTION-UI presents each
 *            independently verified project as a structured accessible row,
 *            styles source-owned task results, and places creation behind a
 *            deliberate expandable workflow; source IAM and counts are unchanged.
 * CHANGELOG: v1.8.2-STRATEGY-RECOVERY-JSX-REPAIR closes the
 *            conditional unavailable-state JSX expression correctly so
 *            OXC, Vitest and production Vite compile the Strategy viewer.
 * CHANGELOG: v1.8.1-TRANSIENT-PROJECTS-READ-RECOVERY retries one safe
 *            source-owned project list GET after transient HTTP 503, retains
 *            fail-closed results, and offers existing Projects workspace
 *            navigation when the Strategy list cannot be verified.
 * CHANGELOG: v1.8.0-EXACT-PROJECT-STRATEGY-READBACK adds read-only, exact-tenant
 *            Projects task/milestone verification from Strategy. Scope, paging
 *            and source status are validated; no objective linkage, progress
 *            percentage, IAM or task mutation is inferred.
 * CHANGELOG: v1.7.2-PROJECTS-DELIVERY-HANDOFF links source-verified Strategy project rows
 *            to the existing authenticated EOS Projects delivery lifecycle.
 *            No strategic linkage, IAM grant, or ownership is inferred.
 * CHANGELOG: v1.7.1-UNAVAILABLE-DRAFT-RETENTION keeps editable project
 *            descriptions and formatted preview visible when EOS Projects
 *            is unavailable, but blocks mutation until a verified fresh read.
 * CHANGELOG: v1.7.0-STRATEGY-RICH-DRAFT-PREVIEW renders a safe semantic
 *            live preview of the entered project description, preserving
 *            editable Markdown source, bounded content and EOS authority.
 *            Also retains bounded machine codes for PROJECT(S) HTTP 503.
 * CHANGELOG: v1.6.2-PROJECT-VALIDATION-DIAGNOSTICS extracts only
 *            bounded project machine codes and recognized field names from
 *            EOS 422 responses; never displays submitted or sensitive values.
 * CHANGELOG: v1.6.1-BOUNDED-ADMISSION-HTTP-STATUS maps known HTTP
 *            outcomes to bounded IAM/transport/readiness classifications
 *            even when the EOS error envelope lacks a simple detail string.
 * CHANGELOG: v1.6.0-FOUNDER-PROJECTS-ACTIVATION-COMMAND presents an explicit\n *            governed Founder activation action only on denied Projects read,\n *            validates source role/entitlement readback and refreshes Projects.\n * CHANGELOG: v1.5.1-PROJECTS-DENIAL-DIAGNOSTICS distinguishes
 *            canonical Projects entitlement denial from project IAM denial
 *            and unavailable infrastructure using bounded EOS codes.
 * CHANGELOG: v1.5.0-SOURCE-BACKED-STRATEGY-EXECUTION adds a tenant/
 *            session-scoped live Projects list and explicit, idempotent project
 *            create plus list/detail readback inside the Strategy document.
 *            Pillar context is descriptive, never a fabricated governed link.
 * CHANGELOG: v1.4.0-APPROVED-SOURCE-READABLE exposes the already
 *            Founder-approved v1.1.0 source text to EOS-authorized readers
 *            while distinguishing EOS pending publication. Source-owned
 *            author and publisher permissions remain unchanged.
 * CHANGELOG: v1.3.0-FOUNDER-APPROVED-CONTENT-ADMISSION maps the two supplied
 *            Founder-approved v1.1.0 PDFs into exact private draft proposals.
 *            The PDF fingerprints identify source files, never EOS publication.
 * CHANGELOG: v1.2.1-SOURCE-AUTHORISED-LIVE-DOCUMENT-STUDIO fixes draft-version validation,
 *            HTML input matching and section word counts so valid proposals
 *            can be submitted to existing EOS author commands.
 * CHANGELOG: v1.2.0-SOURCE-AUTHORISED-LIVE-DOCUMENT-STUDIO brings
 *            publication and separately admitted author/review commands
 *            into one live workspace; supports private section editing,
 *            reorder, removal, preview and persisted EOS draft readback.
 *            Client text is never an official mission or strategy.
 * CHANGELOG: v1.1.0-LIVE-SESSION-SOURCE-STATUS distinguishes local authentication, denied access,
 * unavailable transport/source and invalid responses; presents useful recovery
 * and suppresses commands after an authorization or unverified source failure.
 * CHANGELOG: v1.0.1-FOUNDER-SUPPLIED-LOGO preserves the same selected square navy logo
 * used by authenticated Headquarters; source lifecycle and scope are unchanged.
 * CHANGELOG: v1.0.0-SOURCE-OWNED-COMPANY-DOCUMENT-VIEWER adds contents, publication
 * evidence, history, source-gated draft/submit/publish and verified readback.
 */
import React, { useCallback, useContext, useEffect, useRef, useState } from 'react';
import { ArrowLeft, ArrowUpRight, BookOpen, CheckCircle2, Clock3, FileText, History, Loader2, RefreshCw, ShieldCheck, X } from 'lucide-react';
import { createPortal } from 'react-dom';
import AuthContext from '../../contexts/authContext.jsx';
import api from '../../services/api.js';
import { currentUnifiedMyWorkScope } from '../../services/unifiedMyWorkSync.js';
import { commandCompanyDocument, readCompanyDocumentHistory, readCompanyOperatingDocument } from '../../services/companyOperatingDocumentsClient.js';
import styles from './CompanyOperatingDocumentViewer.module.css';
import { WILSY_PLATFORM_LOGO_SRC } from '../os/wilsyDashboardChromeConfig.js';

// Projects own task, deadline, evidence and assignment truth. Strategy owns the
// independently read-back Pillar 1 relationship; project title and presence
// never establish linkage, IAM capacity or outcome certification.
const validProjectList = (value, tenantId, principalId) => Boolean(
  value?.schema === 'WILSY-PROJECT-LIST/V1'
  && value.tenant_id === tenantId && value.principal_id === principalId
  && value.limit === 100 && value.offset === 0
  && Array.isArray(value.items) && value.items.every(item =>
    item?.tenant_id === tenantId && typeof item.project_id === 'string'
    && typeof item.name === 'string' && typeof item.status === 'string'
    && Number.isSafeInteger(item.revision) && item.revision >= 1)
  && new Set(value.items.map(item => item.project_id)).size === value.items.length
);
const projectFailure = failure => {
  const status = failure?.response?.status;
  if (!status && (failure?.code === 'ECONNABORTED' || failure?.code === 'ETIMEDOUT')) {
    return 'Project list request timed out before an EOS response. No current project result verified; inspect the exact /api/projects request duration and Python EOS transaction failure code.';
  }
  const detail = failure?.response?.data?.detail;
  // Only EOS's closed machine codes enter the UI; never arbitrary diagnostic
  // strings, database details, credentials or nested exception objects.
  const code = typeof detail === 'string' && /^[A-Z][A-Z0-9_]{1,90}$/.test(detail) ? detail : null;
  if (status === 403 && code === 'PROJECTS_ENTITLEMENT_REQUIRED') {
    return 'PROJECTS_ENTITLEMENT_REQUIRED · WILSY needs a verified ACTIVE Projects product entitlement. Check the canonical tenant entitlement and its current revision; no client bypass is permitted.';
  }
  if (status === 403 && code === 'PROJECT_PLATFORM_OWNER_TENANT_DENIED') {
    return 'PROJECT_PLATFORM_OWNER_TENANT_DENIED · The dedicated platform-owner assignment is valid only in the canonical WILSY company tenant.';
  }
  if (status === 422) {
    const body = failure?.response?.data;
    // A gateway may emit structured errors rather than FastAPI's detail.
    // Surface ONLY approved machine codes and known project form field names.
    const codes = [
      code, body?.error_code, body?.code, body?.detail?.error, body?.detail?.code,
    ];
    const machineCode = codes.find(value => typeof value === 'string'
      && /^PROJECT_[A-Z0-9_]{2,90}$/.test(value));
    const validationRows = Array.isArray(body?.detail) ? body.detail
      : Array.isArray(body?.details) ? body.details : [];
    const fields = [...new Set(validationRows.flatMap(item => {
      const loc = Array.isArray(item?.loc) ? item.loc : [];
      return loc.filter(field => ['name', 'summary', 'code', 'start_date', 'target_date'].includes(field));
    }))].slice(0, 5);
    return 'HTTP 422 · ' + (machineCode || (fields.length ? 'Invalid fields: ' + fields.join(', ')
      : 'EOS rejected the request body or Idempotency-Key.'))
      + ' · No project creation was verified.';
  }
  return status === 401 ? 'HTTP 401 · Project session authentication required.'
    : status === 403 ? 'HTTP 403 · Current EOS IAM or selected company capacity denies project access. Verify ACTIVE project:read and project:create assignments; this is distinct from the Projects entitlement.'
      : status === 409 ? 'HTTP 409 · A conflicting Projects revision or idempotency request was rejected.'
        : status === 503 ? 'HTTP 503 · ' + (
            [
              code, failure?.response?.data?.error_code, failure?.response?.data?.code,
              failure?.response?.data?.detail?.error,
            ].find(value => typeof value === 'string' && /^(PROJECT|PROJECTS)_[A-Z0-9_]{3,90}$/.test(value))
              || 'Project transaction or source unavailable; no current result verified.'
          )
          : 'Projects source unavailable or source readback could not be verified.';
};

// A safe, read-only formatting projection of the user's draft. React escapes all
// text. Markdown characters remain source text until edited by the user.
// No HTML parsing, contentEditable, persistence, or source authority is implied.
const projectInlineNodes = (line, keyPrefix) =>
  line.split(/(\*\*[^*]+\*\*)/g).filter(Boolean).map((piece, i) =>
    piece.startsWith('**') && piece.endsWith('**')
      ? <strong key={keyPrefix + '-strong-' + i}>{piece.slice(2, -2)}</strong>
      : <React.Fragment key={keyPrefix + '-text-' + i}>{piece}</React.Fragment>);

function ProjectDescriptionPreview({ value }) {
  const normalized = value.replace(/\\([*_])/g, '$1').replace(/\r\n?/g, '\n');
  const lines = normalized.split('\n');
  const output = [];
  lines.forEach((sourceLine, index) => {
    const line = sourceLine.trim();
    if (!line) return;
    const key = 'description-' + index;
    const heading = /^#{1,4}\s+(.+)$/.exec(line);
    const ordered = /^(\d+)\.\s+(.+)$/.exec(line);
    const bullet = /^[-•]\s+(.+)$/.exec(line);
    const decoratedHeading = /^\*\*(.+)\*\*$/.exec(line);
    if (heading || decoratedHeading) {
      output.push(<h4 key={key}>{projectInlineNodes((heading?.[1] || decoratedHeading?.[1]), key)}</h4>);
    } else if (ordered) {
      output.push(<p key={key} className={styles.projectListLine}><span>{ordered[1]}.</span>{projectInlineNodes(ordered[2], key)}</p>);
    } else if (bullet) {
      output.push(<p key={key} className={styles.projectListLine}><span aria-hidden="true">•</span>{projectInlineNodes(bullet[1], key)}</p>);
    } else {
      output.push(<p key={key}>{projectInlineNodes(line, key)}</p>);
    }
  });
  return <div className={styles.projectDescriptionPreview} aria-label="Formatted project description preview">
    {output.length ? output : <p>No description entered.</p>}
  </div>;
}

const labelFor = classification => classification === 'MISSION' ? 'Our Mission' : 'Our Strategy';
const displayDate = value => value ? new Date(value).toLocaleString(undefined, { dateStyle: 'medium', timeStyle: 'short' }) : 'Not effective';

// Source-transcribed Founder-approved documents, v1.1.0. These are proposal
// inputs, never EOS publication state or independent publisher authorization.
// Document digests identify the supplied PDF files; they are not EOS revision
// fingerprints. Publication remains pending until EOS confirms it.
const FOUNDER_APPROVED_SOURCE = Object.freeze({
  MISSION: {
    pdf_sha3_512: 'e7d4621d54079730c68d0169c1760c6064e48a37d3b517545fadf06ed98a8db0e25a32f8d45cf8fb9fc1d6a433970a31415df8bf96b3a19bc166687d3ab4d051',
    title: 'WILSY (PTY) LTD — OFFICIAL MISSION',
    document_version: '1.1.0',
    sections: [
      { section_id: 'our-mission', title: 'Our Mission', body: 'To empower businesses of every size and industry to build, operate and grow through one intelligent, secure and unified operating platform.\nWILSY OS exists to eliminate fragmented business systems by bringing people, processes, information, decisions and execution together in a single governed environment.\nWe are committed to making enterprise-grade technology accessible, practical and valuable to businesses—enabling them to manage everyday operations with confidence, accountability, efficiency and intelligence.' },
      { section_id: 'one-intelligent-platform', title: 'One Intelligent Platform', body: 'Unite essential business functions without unnecessary fragmentation.' },
      { section_id: 'business-empowerment', title: 'Business Empowerment', body: 'Equip owners, directors, managers and employees with the tools required to perform meaningful work.' },
      { section_id: 'intelligent-operations', title: 'Intelligent Operations', body: 'Transform reliable business information into actionable insights, accountable decisions and measurable outcomes.' },
      { section_id: 'trust-and-governance', title: 'Trust and Governance', body: 'Protect organizational information through strong security, appropriate authority, transparent records and auditable operations.' },
      { section_id: 'industry-flexibility', title: 'Industry Flexibility', body: 'Support diverse industries through configurable, integrated business capabilities.' },
      { section_id: 'sustainable-growth', title: 'Sustainable Growth', body: 'Help businesses reduce operational friction, improve productivity and create lasting economic value.' },
      { section_id: 'our-promise', title: 'Our Promise', body: 'Build. Operate. Grow.\nWILSY OS — One Intelligent Platform.' },
    ],
  },
  STRATEGY: {
    pdf_sha3_512: '7ab326851ef307a9cd398406fb80e1fadeeec161be3a95d2f3e60c76d252ebe66aa90108f41cf524858a0edbe45b03992a536865d00dd38570dfe9d90b955610',
    title: 'WILSY (PTY) LTD — OFFICIAL CORPORATE STRATEGY',
    document_version: '1.1.0',
    sections: [
      { section_id: 'strategic-vision', title: 'Strategic Vision', body: 'To establish WILSY OS as a trusted, intelligent and comprehensive operating platform through which businesses can manage their organizations, coordinate their workforce, govern their operations and pursue sustainable growth.' },
      { section_id: 'pillar-one', title: 'Strategic Pillar 1 — One Unified Operating System', body: 'Develop a cohesive business operating environment that integrates the essential capabilities of an organization. Our platform will connect Headquarters, Human Resources, Customer Relationships, Finance, Legal Operations, Procurement, Inventory, Point of Sale, Workflow and other business capabilities through shared identity, governance and source-backed information.\nStrategic outcome: Businesses operate through an integrated environment rather than disconnected applications.' },
      { section_id: 'pillar-two', title: 'Strategic Pillar 2 — Effortless Business Adoption', body: 'Make WILSY OS accessible to organizations with different sizes, structures and operating requirements. Support straightforward onboarding, appropriate subscription and entitlement management, workforce administration, industry configuration and progressive adoption of capabilities.\nStrategic outcome: Customers can begin operating efficiently and expand without rebuilding their underlying business systems.' },
      { section_id: 'pillar-three', title: 'Strategic Pillar 3 — Intelligent Business Execution', body: 'Embed practical, governed intelligence into everyday work. Connect business objectives, projects, responsibilities, approvals, deadlines and measurable outcomes. Develop AI-assisted capabilities that help people understand information, identify priorities and make better decisions, while preserving human accountability and established authorization boundaries.\nStrategic outcome: Intelligence contributes to real operational value rather than isolated demonstrations.' },
      { section_id: 'pillar-four', title: 'Strategic Pillar 4 — Institutional Trust and Security', body: 'Build a platform founded on verifiable authority, tenant isolation, data protection, reliable evidence and accountable execution. Preserve clear distinctions between proposals, approvals, authorizations, execution and verified results.\nStrategic outcome: Businesses can rely on WILSY OS for trustworthy operational records and controlled processes.' },
      { section_id: 'pillar-five', title: 'Strategic Pillar 5 — Industry Expansion', body: 'Develop configurable operating capabilities for industries including: Legal and professional services; Healthcare practices, clinics and related providers; Vehicle imports, automotive parts and repair services; Wholesale, retail and general trading; Agriculture and other operationally intensive sectors.\nStrategic outcome: One adaptable operating foundation serves multiple industries without duplicating core business authority.' },
      { section_id: 'pillar-six', title: 'Strategic Pillar 6 — Sustainable Commercial Growth', body: 'Establish a scalable commercial model built around customer value, reliable service, sustainable subscriptions and measurable adoption. Prioritize product quality, customer retention, business continuity and operational effectiveness over superficial feature expansion.\nStrategic outcome: WILSY (Pty) Ltd develops a durable, commercially sustainable software business.' },
      { section_id: 'execution-principles', title: 'Execution Principles', body: 'Our strategy shall be implemented through governed business objectives, accountable ownership, measurable milestones and verified work outcomes.\nApproved strategic objectives may be linked to projects and work items only through authorized WILSY OS business workflows.\nProgress must reflect genuine operational evidence, not invented performance measurements.' },
      { section_id: 'strategic-commitment', title: 'Strategic Commitment', body: 'WILSY (Pty) Ltd will pursue its vision through disciplined engineering, responsible governance, practical innovation and a commitment to helping businesses succeed.\nWILSY OS — One Intelligent Platform. Build. Operate. Grow.' },
    ],
  },
});
const STRATEGY_PILLARS = FOUNDER_APPROVED_SOURCE.STRATEGY.sections.filter(section => section.section_id.startsWith('pillar-'));

// Approved engineering register, not a source project task list. Only EOS can
// persist these as real Work & Milestones; no planned item is counted as done.
const FOUNDATION_PROJECT_NAME = 'WILSY OS — Unified Operating Platform Foundation';
const FOUNDATION_EXECUTION_PLAN = Object.freeze([
  { key: 'MW-M01', kind: 'MILESTONE', title: 'MW-M01 — Operating taxonomy and strategy alignment', description: 'Audited operating, platform build and unclassified audience taxonomy; existing seven tasks remain accessible; Founder default certified.' },
  { key: 'MW-M02', kind: 'MILESTONE', title: 'MW-M02 — Governed work graph and multi-source accountability', description: 'Canonical source-owned work identities and reason edges for authorized work and independent project decisions; real Mongo and IAM evidence.' },
  { key: 'MW-M03', kind: 'MILESTONE', title: 'MW-M03 — Role-aware work execution and approval decisions', description: 'Founder, HQ and tenant-capacity queues and genuine source-owned review decisions; source reauthorization and segregation of duties.' },
  { key: 'MW-M04', kind: 'MILESTONE', title: 'MW-M04 — Ranked Founder operating workspace', description: 'Explainable priorities, deterministic pagination, diverse sources, operating/build split and desktop/mobile certification.' },
  { key: 'MW-M05', kind: 'MILESTONE', title: 'MW-M05 — Audited workflow automation and Intelligence Dock parity', description: 'Source-authorized event rules with replay safeguards, independently authorized Dock suggestions, no inferred financial execution.' },
  { key: 'MW-M06', kind: 'MILESTONE', title: 'MW-M06 — Production readiness and strategy outcome certification', description: 'Exact-head security, role/IAM, real Mongo, performance, accessibility, browser and rollback gates green; approved Strategy evidence readback.' },
  { key: 'MW-T01', kind: 'TASK', title: 'MW-T01 — Inventory canonical My Work sources, capacities and IAM', description: 'MW-M01. Approve source/consumer/command matrix, existing authority and all current work identities; prohibit duplicate work ledgers.' },
  { key: 'MW-T02', kind: 'TASK', title: 'MW-T02 — Define Operating, Platform Build and Unclassified work', description: 'MW-M01. Source-owned classification evidence, no title regex, no hidden unclassified or unauthorized work.' },
  { key: 'MW-T03', kind: 'TASK', title: 'MW-T03 — Implement audited source-owned work classification', description: 'MW-M01. CAS/idempotency, exact tenant and owner authorization; preserve all seven current work records.' },
  { key: 'MW-T04', kind: 'TASK', title: 'MW-T04 — Derive source-authorized work identities and accountability', description: 'MW-M02. Current IAM, source revisions and exact role edges; no graph-owned task or permission grants.' },
  { key: 'MW-T05', kind: 'TASK', title: 'MW-T05 — Integrate independent project approvals in My Work', description: 'MW-M02. Approver-specific pending review, segregation of duties, decision readback and revoked-participation denial.' },
  { key: 'MW-T06', kind: 'TASK', title: 'MW-T06 — Deliver Founder Operating, Platform and Waiting filters', description: 'MW-M03. Verified classification filters, work reasons, unclassified/denied/empty states, accessible presentation.' },
  { key: 'MW-T07', kind: 'TASK', title: 'MW-T07 — Certify role capacity packs and tenant isolation', description: 'MW-M03. Independent Founder/HQ/customer queue tests, seat/entitlement checks and denied cross-tenant cases.' },
  { key: 'MW-T08', kind: 'TASK', title: 'MW-T08 — Implement explainable ranking and source diversity', description: 'MW-M04. Stable EOS scoring/cursors, defensible urgency and 500+ work item regression.' },
  { key: 'MW-T09', kind: 'TASK', title: 'MW-T09 — Wire source-owned task and decision commands', description: 'MW-M04. Create, edit, assign, complete, approve, reject through source IAM, CAS, idempotency and durable readback.' },
  { key: 'MW-T10', kind: 'TASK', title: 'MW-T10 — Build governed event-driven workflow automation', description: 'MW-M05. Event replay, rule conflicts, current IAM, revocation, audits and no unintended external effects.' },
  { key: 'MW-T11', kind: 'TASK', title: 'MW-T11 — Align Intelligence Dock with the authorized work graph', description: 'MW-M05. One source identity/ranking explanation, no invented execution/approval; independently confirmed handoff.' },
  { key: 'MW-T12', kind: 'TASK', title: 'MW-T12 — Certify production readiness and rollback', description: 'MW-M06. Exact-head Python/JS, Mongo replica set, authenticated browser, role matrix, observability and SLO evidence.' },
]);

const founderApprovedProposal = classification => {
  const source = FOUNDER_APPROVED_SOURCE[classification];
  return { title: source.title, document_version: source.document_version,
    sections: source.sections.map(section => ({ ...section })) };
};

const emptyProposal = () => ({ title: '', document_version: '', sections: [{ section_id: 'section-1', title: '', body: '' }] });
// The API has both FastAPI detail envelopes and institutional exception
// envelopes. Only bounded machine codes enter the UI; never server messages,
// credentials, exception stacks, arbitrary diagnostics or confidential bodies.
const sourceError = failure => {
  const status = Number.isInteger(failure?.response?.status) ? failure.response.status : null;
  const body = failure?.response?.data;
  const candidate = body?.detail?.error || body?.detail?.code || body?.error?.code || body?.code
    || (typeof body?.error === 'string' ? body.error : null) || failure?.code || failure?.message;
  const code = typeof candidate === 'string' && /^COMPANY_DOCUMENT_[A-Z_]{1,80}$/.test(candidate)
    ? candidate : status ? 'HTTP_' + status : 'COMPANY_DOCUMENT_CONNECTION_FAILED';
  const evidence = { code, status };
  if (status === 401 || code === 'COMPANY_DOCUMENT_AUTHENTICATED_SCOPE_REQUIRED') return {
    ...evidence, kind: 'AUTHENTICATION_REQUIRED', title: 'Sign-in verification required',
    message: 'The current company session must be verified before this document can be read.',
    next: 'Return to the sign-in screen if your session has expired. Once Headquarters confirms your current session, retry this read.',
  };
  if (status === 403) return {
    ...evidence, kind: 'ACCESS_DENIED', title: 'Access denied',
    message: 'EOS has not authorized this document operation for your current company capacity.',
    next: 'An authorized company administrator must verify document access through the existing IAM process. A Founder title alone does not grant document permission.',
  };
  if (status === 409) return {
    ...evidence, kind: 'CONFLICT', title: 'The document has changed',
    message: 'The source revision no longer matches the requested operation.',
    next: 'Refresh the current publication and review its latest source revision before retrying.',
  };
  if (status === 404 && code === 'COMPANY_DOCUMENT_NOT_FOUND') return {
    ...evidence, kind: 'REVISION_UNAVAILABLE', title: 'Revision unavailable',
    message: 'The requested revision is not available to your current company capacity.',
    next: 'Open the current publication or refresh permitted revision history. This result does not establish that no approved publication exists.',
  };
  if (code === 'COMPANY_DOCUMENT_RESPONSE_INVALID') return {
    ...evidence, kind: 'INVALID_RESPONSE', title: 'Document response could not be verified',
    message: 'The source response did not match the requested company, principal or publication contract.',
    next: 'Retry the source read. If verification still fails, share the status code below with support; no unverified content is displayed.',
  };
  return {
    ...evidence, kind: 'UNAVAILABLE', title: 'Document source unavailable',
    message: status === 404 ? 'The running service did not provide the company-document endpoint.'
      : status ? 'The company-document source could not complete a verified read.'
        : 'The company-document service could not be reached or did not return a response.',
    next: 'Retry the source read. If it remains unavailable, support must check the running EOS route, source connection and current company authorization. Publication status is unknown until a verified read succeeds.',
  };
};

const COMMAND_LABELS = Object.freeze({
  CREATE_DRAFT: 'Save private draft', FOUNDER_CREATE_DRAFT: 'Save Founder Strategy draft',
  SUBMIT: 'Submit private revision', FOUNDER_SUBMIT: 'Submit Founder Strategy',
  PUBLISH: 'Publish approved revision', FOUNDER_RATIFY: 'Ratify Founder Strategy',
});
const ALLOWED_VALIDATION_FIELDS = new Set([
  'expected_revision', 'title', 'document_version', 'sections',
  'section_id', 'body', 'effective_from', 'approval_reference',
  'Idempotency-Key',
]);
const commandFailure = (failure, action, acknowledged) => {
  const base = sourceError(failure);
  const status = base.status;
  const detail = failure?.response?.data?.detail;
  const fields = Array.isArray(detail) ? [...new Set(detail.flatMap(entry => {
    if (!Array.isArray(entry?.loc)) return [];
    const allowed = entry.loc.filter(part => typeof part === 'string'
      && ALLOWED_VALIDATION_FIELDS.has(part));
    return allowed.length ? [allowed[allowed.length - 1]] : [];
  }))].slice(0, 5) : [];
  if (!acknowledged && action === 'FOUNDER_CREATE_DRAFT'
    && status === 409 && base.code === 'COMPANY_DOCUMENT_VERSION_ALREADY_PUBLISHED') {
    return {
      ...base, operation: COMMAND_LABELS[action],
      kind: 'PUBLISHED_VERSION_CONFLICT',
      title: 'Strategy version already published in EOS',
      message: 'EOS refused another draft for a version already recorded as published. This is not a rejected content field. Earlier ratification may have succeeded.',
      next: 'Verify the existing published revision and fingerprint. Do not create another draft or repeat ratification while source status is uncertain.',
    };
  }
  return {
    ...base, operation: COMMAND_LABELS[action] || 'Company-document command',
    kind: acknowledged ? 'READBACK_UNVERIFIED' : 'COMMAND_REJECTED',
    title: acknowledged ? 'Command recorded; current readback unverified'
      : status === 422 ? 'EOS rejected the document command (HTTP 422)'
        : 'EOS did not verify the document command',
    message: acknowledged
      ? 'EOS acknowledged the command, but the updated source was not independently verified. Do not retry with a new key before refreshing the source.'
      : status === 422
        ? (fields.length ? 'EOS rejected these request fields: ' + fields.join(', ') + '.'
          : 'EOS rejected the request payload or command contract. The current document remains unverified.')
        : 'This command was not confirmed by EOS. The private editor content is preserved.',
    next: acknowledged ? 'Refresh the source to establish whether the revision exists.'
      : 'Review the rejected fields. Keep the draft open and retry only after resolving the source validation error.',
  };
};

/**
 * @description Open a current company document with contents and source-owned actions.
 * @collaboration Headquarters Mission/Strategy controls and canonical EOS document APIs.
 * @institutional Only source publication state labels official content. Drafts are
 * private to separately authorized users. Commands use stable retry keys and a
 * second source read before any success claim. No transaction or permission is
 * owned by this component; closing discards transient unsaved proposals.
 * @param {{classification:'MISSION'|'STRATEGY',onClose:Function,onOpenWork:Function,onOpenProject?:Function}} props
 * @returns {JSX.Element} Accessible responsive source-backed document drawer.
 */
export default function CompanyOperatingDocumentViewer({ classification, onClose, onOpenWork, onOpenProject, onOpenProjects }) {
  const auth = useContext(AuthContext) || {};
  const baseScope = currentUnifiedMyWorkScope(auth, auth.user?.tenantId);
  const credential = useRef({ token: auth.token, revision: 0 });
  if (credential.current.token !== auth.token) credential.current = { token: auth.token, revision: credential.current.revision + 1 };
  const sessionKey = baseScope ? baseScope + ':' + credential.current.revision : null;
  const epoch = useRef(sessionKey);
  epoch.current = sessionKey;
  const scope = { tenantId: auth.user?.tenantId, principalId: auth.user?.id };
  const [source, setSource] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [tab, setTab] = useState('document');
  const [contentsOpen, setContentsOpen] = useState(false);
  const [strategyMode, setStrategyMode] = useState('EXECUTION');
  const [projectSearch, setProjectSearch] = useState('');
  const [pendingDocumentSection, setPendingDocumentSection] = useState(null);
  const [executionSearch, setExecutionSearch] = useState('');
  const [executionFilter, setExecutionFilter] = useState('ALL');
  const [executionPage, setExecutionPage] = useState(0);
  const [executionInspectorOpen, setExecutionInspectorOpen] = useState(false);
  const [history, setHistory] = useState(null);
  const [query, setQuery] = useState({ review: false, revision: null });
  const queryRef = useRef(query);
  const [editorOpen, setEditorOpen] = useState(false);
  const [ratificationOpen, setRatificationOpen] = useState(false);
  const [previewOpen, setPreviewOpen] = useState(false);
  const [proposal, setProposal] = useState(emptyProposal);
  const [approvalReference, setApprovalReference] = useState('');
  const [effectiveFrom, setEffectiveFrom] = useState('');
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState('');
  const [commandIssue, setCommandIssue] = useState(null);
  const [projectState, setProjectState] = useState('IDLE');
  const [projectItems, setProjectItems] = useState([]);
  const [delivery, setDelivery] = useState({ state: 'IDLE', projectId: null, page: null, error: '' });
  const deliveryReadRef = useRef({ sequence: 0, controller: null });
  const executionEvidenceReadRef = useRef({ sequence: 0, controller: null });
  const [executionEvidence, setExecutionEvidence] = useState({
    state: 'IDLE', taskId: null, items: [], error: '',
  });
  const [projectError, setProjectError] = useState('');
  const [projectPillar, setProjectPillar] = useState('pillar-one');
  const [projectName, setProjectName] = useState('');
  const [projectDescription, setProjectDescription] = useState('');
  const [projectEditSource, setProjectEditSource] = useState(false);
  const [projectBusy, setProjectBusy] = useState(false);
  const [projectSuccess, setProjectSuccess] = useState('');
  const [admissionBusy, setAdmissionBusy] = useState(false);
  const [admissionStatus, setAdmissionStatus] = useState('');
  const projectReadRef = useRef({ sequence: 0, controller: null });
  const projectMutation = useRef(null);
  const planMutation = useRef(null);
  const [planState, setPlanState] = useState({ state: 'IDLE', created: 0, skipped: 0, message: '' });
  const [strategyLink, setStrategyLink] = useState({ state: 'IDLE', items: [], message: '' });
  const strategyLinkReadRef = useRef({ sequence: 0, controller: null });
  const strategyLinkWriteRef = useRef(null);
  const projectReplay = useRef({ intent: '', key: null });
  const readId = useRef(0);
  const readController = useRef(null);
  const commandLock = useRef(null);
  const retryKeys = useRef(new Map());
  const containerRef = useRef(null);
  const scrollRef = useRef(null);
  const editorRef = useRef(null);
  const ratificationDateRef = useRef(null);
  const commandIssueRef = useRef(null);
  const closeRef = useRef(null);
  const data = source?.scope === sessionKey && source?.classification === classification ? source.data : null;
  const currentHistory = history?.scope === sessionKey && history?.classification === classification ? history.data : null;
  const document = data?.document;
  const actions = !error && !loading ? data?.available_actions || [] : [];
  const active = key => epoch.current === key && key !== null;

  /** Fetch an authorized first page only. No project-to-pillar relationship is inferred. */
  const loadProjects = useCallback(async () => {
    const request = ++projectReadRef.current.sequence;
    projectReadRef.current.controller?.abort();
    const controller = new AbortController();
    projectReadRef.current.controller = controller;
    const key = sessionKey;
    setProjectState('LOADING'); setProjectError(''); setProjectItems([]);
    if (!key || !scope.tenantId || !scope.principalId || classification !== 'STRATEGY') {
      setProjectState('DENIED'); return null;
    }
    try {
      // A transient EOS 503 may recover while the document remains mounted.
      // Retry only this side-effect-free owner-authorized GET, once. Do not
      // retry denials, invalid response shapes, or mutation commands.
      let reply;
      for (let attempt = 0; attempt < 2; attempt += 1) {
        try {
          reply = await api.get('/projects', { headers: {
            'X-Tenant-ID': scope.tenantId, Authorization: 'Bearer ' + auth.token,
          }, params: { limit: 100, offset: 0 }, signal: controller.signal });
          break;
        } catch (failure) {
          if (attempt !== 0 || failure?.response?.status !== 503
            || controller.signal.aborted || !active(key)
            || request !== projectReadRef.current.sequence) throw failure;
          await new Promise(resolve => setTimeout(resolve, 1200));
          if (controller.signal.aborted || !active(key)
            || request !== projectReadRef.current.sequence) return null;
        }
      }
      if (!active(key) || request !== projectReadRef.current.sequence) return null;
      if (!validProjectList(reply.data, scope.tenantId, scope.principalId)) throw new Error('PROJECT_LIST_SCOPE_OR_SHAPE_INVALID');
      setProjectItems(reply.data.items); setProjectState('READY');
      return reply.data.items;
    } catch (failure) {
      if (!active(key) || request !== projectReadRef.current.sequence) return null;
      if (failure?.name === 'CanceledError' || failure?.name === 'AbortError') return null;
      setProjectState(failure?.response?.status === 401 || failure?.response?.status === 403 ? 'DENIED' : 'UNAVAILABLE');
      setProjectError(projectFailure(failure)); return null;
    }
  }, [classification, sessionKey, auth.token, scope.tenantId, scope.principalId]);

  /**
   * Source-owned Projects task readback for Strategy planning; never a durable
   * strategy-objective relationship, task command, or completion assertion.
   */
  const loadDelivery = async (projectId, offset = 0) => {
    const request = ++deliveryReadRef.current.sequence;
    deliveryReadRef.current.controller?.abort();
    const controller = new AbortController();
    deliveryReadRef.current.controller = controller;
    const key = sessionKey;
    executionEvidenceReadRef.current.sequence += 1;
    executionEvidenceReadRef.current.controller?.abort();
    setExecutionEvidence({ state: 'IDLE', taskId: null, items: [], error: '' });
    setDelivery({ state: 'LOADING', projectId, page: null, error: '' });
    if (!key || classification !== 'STRATEGY' || projectState !== 'READY'
      || !/^prj-[a-f0-9]{48}$/.test(projectId) || !Number.isSafeInteger(offset) || offset < 0
      || !projectItems.some(item => item.project_id === projectId)) {
      setDelivery({ state: 'DENIED', projectId: null, page: null, error: '' });
      return;
    }
    try {
      const { data: page } = await api.get('/projects/' + encodeURIComponent(projectId) + '/tasks', {
        params: { limit: 50, offset },
        headers: { 'X-Tenant-ID': scope.tenantId, Authorization: 'Bearer ' + auth.token },
        signal: controller.signal,
      });
      if (!active(key) || request !== deliveryReadRef.current.sequence) return;
      const validItems = Array.isArray(page?.items) && page.items.length <= 50
        && new Set(page.items.map(item => item.task_id)).size === page.items.length
        && page.items.every(item => item?.tenant_id === scope.tenantId
          && item.project_id === projectId && /^ptk-[a-f0-9]{48}$/.test(item.task_id)
          && ['TASK', 'MILESTONE'].includes(item.kind)
          && ['TODO', 'IN_PROGRESS', 'BLOCKED', 'DONE', 'CANCELLED'].includes(item.status)
          && typeof item.title === 'string' && item.title.trim());
      if (page?.schema !== 'WILSY-PROJECT-TASK-LIST/V1'
        || page.tenant_id !== scope.tenantId || page.principal_id !== scope.principalId
        || page.project_id !== projectId || page.offset !== offset || page.limit !== 50
        || typeof page.has_more !== 'boolean' || !validItems
        || (page.has_more
          ? !Number.isSafeInteger(page.next_offset)
            || page.next_offset !== offset + page.items.length || page.items.length === 0
          : page.next_offset !== null)) throw new Error('STRATEGY_PROJECT_TASK_READBACK_INVALID');
      setDelivery({ state: 'READY', projectId, page, verifiedAt: new Date().toISOString(), error: '' });
      if (projectItems.some(item => item.project_id === projectId && item.name === FOUNDATION_PROJECT_NAME)) void loadStrategyLinks();
    } catch (failure) {
      if (!active(key) || request !== deliveryReadRef.current.sequence) return;
      if (failure?.name === 'CanceledError' || failure?.name === 'AbortError') return;
      setDelivery({ state: failure?.response?.status === 401 || failure?.response?.status === 403
        ? 'DENIED' : 'UNAVAILABLE', projectId, page: null,
      error: 'EOS could not verify the project task page. No Strategy progress was inferred.' });
    }
  };

  useEffect(() => {
    projectReadRef.current.sequence += 1;
    projectReadRef.current.controller?.abort();
    deliveryReadRef.current.sequence += 1;
    deliveryReadRef.current.controller?.abort();
    executionEvidenceReadRef.current.sequence += 1;
    executionEvidenceReadRef.current.controller?.abort();
    setExecutionEvidence({ state: 'IDLE', taskId: null, items: [], error: '' });
    setDelivery({ state: 'IDLE', projectId: null, page: null, error: '' });
    projectMutation.current = null;
    planMutation.current = null;
    setPlanState({ state: 'IDLE', created: 0, skipped: 0, message: '' });
    strategyLinkReadRef.current.sequence += 1;
    strategyLinkReadRef.current.controller?.abort();
    strategyLinkWriteRef.current = null;
    setStrategyLink({ state: 'IDLE', items: [], message: '' });
    projectReplay.current = { intent: '', key: null };
    setProjectItems([]); setProjectState('IDLE'); setProjectError('');
    setProjectBusy(false); setProjectSuccess(''); setAdmissionBusy(false); setAdmissionStatus(''); setProjectName(''); setProjectDescription(''); setProjectEditSource(false);
    setProjectPillar('pillar-one');
    if (classification === 'STRATEGY' && sessionKey) void loadProjects();
    return () => { projectReadRef.current.sequence += 1; projectReadRef.current.controller?.abort(); deliveryReadRef.current.sequence += 1; deliveryReadRef.current.controller?.abort(); strategyLinkReadRef.current.sequence += 1; strategyLinkReadRef.current.controller?.abort(); strategyLinkWriteRef.current = null; projectMutation.current = null; };
  }, [classification, sessionKey, loadProjects]);

  /**
   * Create only missing reviewed plan records, through one audited EOS command
   * per record and independent current task readback. No blind bulk insert:
   * noncanonical source, extra pages, uncertain POST or stale session halts.
   */
  /**
   * Independent EOS strategy/project source read, never an inferred linkage
   * from navigation or matching project title.
   */
  const loadStrategyLinks = async () => {
    const key = sessionKey;
    const request = ++strategyLinkReadRef.current.sequence;
    strategyLinkReadRef.current.controller?.abort();
    const controller = new AbortController();
    strategyLinkReadRef.current.controller = controller;
    setStrategyLink({ state: 'LOADING', items: [], message: '' });
    if (!key || classification !== 'STRATEGY' || !scope.tenantId || !scope.principalId) {
      setStrategyLink({ state: 'DENIED', items: [], message: 'Current Strategy scope is unverified.' });
      return;
    }
    try {
      const { data: result } = await api.get('/company-operating-documents/STRATEGY/project-links', {
        headers: { 'X-Tenant-ID': scope.tenantId, Authorization: 'Bearer ' + auth.token },
        signal: controller.signal,
      });
      if (!active(key) || request !== strategyLinkReadRef.current.sequence) return;
      if (result?.schema !== 'WILSY-STRATEGY-PROJECT-LINK-LIST/V1'
        || result.tenant_id !== scope.tenantId || result.principal_id !== scope.principalId
        || result.classification !== 'STRATEGY' || result.source_verified !== true
        || result.strategy_progress !== null || !Number.isSafeInteger(result.strategy_revision)
        || !Array.isArray(result.items) || result.items.length > 100
        || result.items.some(item => !/^prj-[a-f0-9]{48}$/.test(item?.project_id)
          || !/^pillar-(one|two|three|four|five|six)$/.test(item?.pillar_id)
          || !['VERIFIED_CURRENT', 'SOURCE_CHANGED'].includes(item?.state))) {
        throw new Error('STRATEGY_LINK_SOURCE_RESPONSE_INVALID');
      }
      setStrategyLink({ state: 'READY', items: result.items, message: '' });
    } catch (failure) {
      if (!active(key) || request !== strategyLinkReadRef.current.sequence) return;
      if (failure?.name === 'CanceledError' || failure?.name === 'AbortError') return;
      const reason = failure?.response?.data?.detail?.error;
      if (failure?.response?.status === 409
        && reason === 'STRATEGY_LINK_PUBLISHED_SOURCE_REQUIRED') {
        setStrategyLink({ state: 'PUBLICATION_REQUIRED', items: [],
          message: 'No currently effective EOS-published Strategy exists. Approved source content and project records are not publication evidence. An admitted Founder may submit and self-ratify Strategy; other principals require separately authorized author and independent publisher capacity before Pillar 1 linking.' });
        return;
      }
      setStrategyLink({ state: 'UNAVAILABLE', items: [],
        message: failure?.response?.status === 403
          ? 'EOS did not admit current Strategy and Projects read permissions.'
          : 'EOS could not verify the current Strategy project relationships. No link or progress is inferred.' });
    }
  };

  /**
   * Explicitly authorize and persist one linked publication/project snapshot;
   * readback, not a successful POST alone, proves a current relationship.
   */
  const linkFoundationStrategy = async () => {
    const key = sessionKey;
    const project = projectItems.find(item => item.project_id === delivery.projectId
      && item.name === FOUNDATION_PROJECT_NAME);
    const published = classification === 'STRATEGY' && data?.state === 'PUBLISHED'
      && query.review === false && Number.isSafeInteger(document?.revision)
      && document?.sections?.some(section => section.section_id === 'pillar-one');
    if (!key || !project || !published || delivery.state !== 'READY'
      || foundationPlanRemaining !== 0 || delivery.page.has_more
      || strategyLink.state !== 'READY' || strategyLinkWriteRef.current
      || strategyLink.items.some(item => item.project_id === project.project_id
        && item.pillar_id === 'pillar-one')) return;
    const attempt = Symbol('strategy-project-link');
    strategyLinkWriteRef.current = attempt;
    setStrategyLink(prev => ({ ...prev, state: 'LINKING',
      message: 'EOS is independently authorizing the Strategy and Projects sources…' }));
    const headers = {
      'X-Tenant-ID': scope.tenantId, Authorization: 'Bearer ' + auth.token,
      'Idempotency-Key': 'strategy-pillar-one-foundation-v1-' + project.project_id,
    };
    try {
      const linkEndpoint = actions.includes('FOUNDER_LINK_PROJECT')
        ? '/company-operating-documents/STRATEGY/founder-project-links'
        : '/company-operating-documents/STRATEGY/project-links';
      const { data: receipt } = await api.post(linkEndpoint, {
        pillar_id: 'pillar-one', project_id: project.project_id,
        expected_strategy_revision: document.revision,
        expected_project_revision: project.revision,
      }, { headers });
      if (!active(key) || strategyLinkWriteRef.current !== attempt) return;
      if (receipt?.schema !== 'WILSY-STRATEGY-PROJECT-LINK-RESULT/V1'
        || receipt.tenant_id !== scope.tenantId || receipt.principal_id !== scope.principalId
        || receipt.project_id !== project.project_id || receipt.pillar_id !== 'pillar-one'
        || receipt.strategy_revision !== document.revision
        || receipt.project_revision !== project.revision
        || receipt.relationship_state !== 'RECORDED_NOT_OUTCOME_CERTIFIED'
        || receipt.strategy_progress !== null) {
        throw new Error('STRATEGY_LINK_COMMAND_RECEIPT_UNVERIFIED');
      }
      await loadStrategyLinks();
    } catch (failure) {
      if (active(key) && strategyLinkWriteRef.current === attempt) {
        setStrategyLink({ state: 'UNAVAILABLE', items: [],
          message: failure?.response?.status === 403
            ? 'EOS denied current Strategy author/Founder or Projects source authorization.'
            : failure?.response?.status === 409
              ? 'The published Strategy or project revision changed. Refresh both sources.'
              : 'Link command or its readback could not be verified; refresh before any retry.' });
      }
    } finally {
      if (strategyLinkWriteRef.current === attempt) strategyLinkWriteRef.current = null;
    }
  };

  // M02 is a read-only projection, never Strategy outcome certification.
  // Only the full exact-project response can attest the plan's full graph;
  // a paged or missing predecessor snapshot cannot produce zero blockers.
  const foundationExecution = (() => {
    const page = delivery.page;
    if (delivery.state !== 'READY' || !page || page.offset !== 0
      || page.has_more || !delivery.verifiedAt
      || !projectItems.some(project => project.project_id === delivery.projectId
        && project.name === FOUNDATION_PROJECT_NAME)) return null;
    const byId = new Map(page.items.map(item => [item.task_id, item]));
    const plan = [];
    for (const entry of FOUNDATION_EXECUTION_PLAN) {
      const matches = page.items.filter(item => item.title === entry.title
        && item.kind === entry.kind);
      if (matches.length !== 1) return null;
      plan.push(matches[0]);
    }
    const counts = { TODO: 0, IN_PROGRESS: 0, BLOCKED: 0, DONE: 0, CANCELLED: 0 };
    let waiting = 0;
    let unfinishedPredecessors = 0;
    let pastDue = 0;
    // This is a client-calendar comparison at the instant of successful
    // readback, not an EOS-computed overdue flag or Strategy deadline.
    const asOfDay = delivery.verifiedAt.slice(0, 10);
    for (const task of plan) {
      if (!Object.hasOwn(counts, task.status) || !Array.isArray(task.depends_on)
        || task.depends_on.length > 25
        || new Set(task.depends_on).size !== task.depends_on.length) return null;
      counts[task.status] += 1;
      const predecessors = task.depends_on.map(id => byId.get(id));
      if (predecessors.some(item => !item)) return null;
      const remaining = predecessors.filter(item => item.status !== 'DONE').length;
      if (remaining) { waiting += 1; unfinishedPredecessors += remaining; }
      if (!['DONE', 'CANCELLED'].includes(task.status) && task.due_date != null) {
        if (typeof task.due_date !== 'string'
          || !/^\d{4}-\d{2}-\d{2}$/.test(task.due_date)
          || Number.isNaN(Date.parse(task.due_date + 'T00:00:00Z'))) return null;
        if (task.due_date < asOfDay) pastDue += 1;
      }
    }
    return { counts, waiting, unfinishedPredecessors, pastDue,
      total: plan.length, verifiedAt: delivery.verifiedAt };
  })();

  // This diagnostic is not execution authority and cannot turn stale data into truth.
  const m04GateMessage = (() => {
    if (data?.state !== 'PUBLISHED') return 'Official Strategy publication was not verified.';
    if (query.review) return 'Return to Current publication for execution verification.';
    if (delivery.state !== 'READY' || !delivery.page) return 'Foundation project tasks were not verified.';
    if (delivery.page.offset !== 0 || delivery.page.has_more) return 'The project work snapshot is incomplete.';
    if (!foundationExecution) return 'The work source lacks the complete Foundation plan or valid predecessor graph.';
    if (strategyLink.state === 'IDLE' || strategyLink.state === 'LOADING') return 'The independent Pillar 1 relationship read is still pending.';
    if (strategyLink.state !== 'READY') return strategyLink.message || 'The independent Pillar 1 relationship source is not verified.';
    const project = projectItems.find(item => item.project_id === delivery.projectId
      && item.name === FOUNDATION_PROJECT_NAME);
    if (!project) return 'Foundation project identity is not verified.';
    const links = strategyLink.items.filter(item => item.project_id === project.project_id
      && item.pillar_id === 'pillar-one');
    if (links.length === 0) return 'EOS returned no Pillar 1 link for this project; project presence is not linkage.';
    if (links.length !== 1) return 'Pillar 1 relationship evidence is ambiguous.';
    if (links[0].state === 'SOURCE_CHANGED') return 'EOS reports SOURCE_CHANGED: the established Pillar 1 link does not match the current Strategy or project revision.';
    if (links[0].state !== 'VERIFIED_CURRENT') return 'EOS has not certified the Pillar 1 relationship as current.';
    if (links[0].source_project_revision !== project.revision
      || links[0].source_strategy_revision !== document?.revision)
      return 'Current Strategy or project revision differs from the relationship source revision.';
    if (project.status !== 'active') return 'The Foundation project is not active.';
    return 'One or more task ownership, deadline, status, fingerprint or dependency records did not pass validation.';
  })();

  // M04 is an exact-source execution *read* with independent Pillar 1 link
  // currentness. Operational work counts and event evidence must NEVER
  // become a strategic outcome percentage or an invented completion decision.
  const m04Execution = (() => {
    if (classification !== 'STRATEGY' || data?.state !== 'PUBLISHED'
      || query.review || !foundationExecution || strategyLink.state !== 'READY'
      || delivery.page.has_more || delivery.page.offset !== 0) return null;
    const project = projectItems.find(item =>
      item.project_id === delivery.projectId && item.name === FOUNDATION_PROJECT_NAME);
    const links = strategyLink.items.filter(item => item.project_id === delivery.projectId
      && item.pillar_id === 'pillar-one');
    if (!project || links.length !== 1 || links[0].state !== 'VERIFIED_CURRENT'
      || links[0].source_project_revision !== project.revision
      || links[0].source_strategy_revision !== document?.revision
      || project.status !== 'active' || !Array.isArray(delivery.page.items)) return null;
    const tasks = delivery.page.items;
    const byId = new Map(tasks.map(task => [task.task_id, task]));
    if (tasks.length !== byId.size) return null;
    let assigned = 0; let unassigned = 0; let waiting = 0;
    let missingDueDate = 0; let unfinishedWithDue = 0;
    const states = { TODO: 0, IN_PROGRESS: 0, BLOCKED: 0, DONE: 0, CANCELLED: 0 };
    const asOfDay = delivery.verifiedAt.slice(0, 10);
    const rows = [];
    for (const task of tasks) {
      if (task.tenant_id !== scope.tenantId || task.project_id !== project.project_id
        || !Object.hasOwn(states, task.status)
        || !Number.isSafeInteger(task.revision) || task.revision < 1
        || typeof task.fingerprint !== 'string' || !/^[a-f0-9]{128}$/.test(task.fingerprint)
        || !['TASK', 'MILESTONE'].includes(task.kind)
        || (task.assignee_principal_id !== null && (typeof task.assignee_principal_id !== 'string'
          || !task.assignee_principal_id.trim()))
        || !Array.isArray(task.depends_on) || task.depends_on.length > 25
        || new Set(task.depends_on).size !== task.depends_on.length
        || task.depends_on.some(id => !byId.has(id) || id === task.task_id)
        || (task.due_date !== null && (typeof task.due_date !== 'string'
          || !/^\d{4}-\d{2}-\d{2}$/.test(task.due_date)
          || Number.isNaN(Date.parse(task.due_date + 'T00:00:00Z'))))) return null;
      states[task.status] += 1;
      if (task.assignee_principal_id === null) unassigned += 1;
      else assigned += 1;
      const remaining = task.depends_on.filter(id => byId.get(id).status !== 'DONE').length;
      if (remaining > 0) waiting += 1;
      if (task.due_date === null) missingDueDate += 1;
      else if (!['DONE', 'CANCELLED'].includes(task.status) && task.due_date < asOfDay)
        unfinishedWithDue += 1;
      rows.push({ task, remaining });
    }
    return { project, rows, states, assigned, unassigned, waiting, missingDueDate,
      pastDueCalendar: unfinishedWithDue, observedAt: delivery.verifiedAt,
      certifiedOutcome: null };
  })();

  // This view is a bounded client presentation of an already-complete verified
  // task snapshot; filters do not affect the underlying M04 verification gate.
  const executionMatches = m04Execution ? m04Execution.rows.filter(({ task, remaining }) => {
    const search = executionSearch.trim().toLocaleLowerCase();
    if (search && !task.title.toLocaleLowerCase().includes(search)) return false;
    if (executionFilter === 'ASSIGNED') return task.assignee_principal_id !== null;
    if (executionFilter === 'UNASSIGNED') return task.assignee_principal_id === null;
    if (executionFilter === 'WAITING') return remaining > 0;
    if (executionFilter === 'UNDATED') return task.due_date === null;
    if (executionFilter === 'DUE') return task.due_date !== null
      && !['DONE', 'CANCELLED'].includes(task.status)
      && task.due_date < m04Execution.observedAt.slice(0, 10);
    if (executionFilter === 'DONE') return task.status === 'DONE';
    return true;
  }) : [];
  const focusExecutionWork = filter => {
    setExecutionSearch('');
    setExecutionFilter(filter);
    setExecutionPage(0);
    setExecutionInspectorOpen(true);
  };
  const executionPageSize = 6;
  const executionPageCount = Math.max(1, Math.ceil(executionMatches.length / executionPageSize));
  const safeExecutionPage = Math.min(executionPage, executionPageCount - 1);
  const visibleExecutionRows = executionMatches.slice(
    safeExecutionPage * executionPageSize, (safeExecutionPage + 1) * executionPageSize);

  /** Read immutable lifecycle evidence through the existing Projects owner IAM.
   * No Strategy permission is used to grant task activity, and no write occurs.
   */
  const verifyExecutionEvidence = async taskId => {
    const key = sessionKey;
    if (!key || !m04Execution || !m04Execution.rows.some(row => row.task.task_id === taskId)
      || !/^ptk-[a-f0-9]{48}$/.test(taskId)) return;
    const sequence = ++executionEvidenceReadRef.current.sequence;
    executionEvidenceReadRef.current.controller?.abort();
    const controller = new AbortController();
    executionEvidenceReadRef.current.controller = controller;
    setExecutionEvidence({ state: 'LOADING', taskId, items: [], error: '' });
    try {
      const task = m04Execution.rows.find(row => row.task.task_id === taskId).task;
      const baseUrl = '/projects/' + encodeURIComponent(m04Execution.project.project_id)
        + '/tasks/' + encodeURIComponent(taskId);
      const requestOptions = {
        params: { limit: 100, offset: 0 },
        headers: { 'X-Tenant-ID': scope.tenantId,
          Authorization: 'Bearer ' + auth.token },
        signal: controller.signal,
      };
      // DONE is a task lifecycle state, not independently approved work
      // evidence. Read separate source registries without automatic approval.
      const [eventReply, otherReplies] = await Promise.all([
        api.get(baseUrl + '/events', requestOptions),
        task.status === 'DONE'
          ? Promise.all([
            api.get(baseUrl + '/approvals', requestOptions),
            api.get(baseUrl + '/attachments', requestOptions),
          ]) : Promise.resolve(null),
      ]);
      if (!active(key) || sequence !== executionEvidenceReadRef.current.sequence) return;
      const page = eventReply.data;
      const valid = page?.schema === 'WILSY-PROJECT-TASK-EVENT-LIST/V1'
        && page.tenant_id === scope.tenantId && page.principal_id === scope.principalId
        && page.project_id === m04Execution.project.project_id && page.task_id === taskId
        && page.limit === 100 && page.offset === 0 && Array.isArray(page.items)
        && page.items.length <= 100 && typeof page.has_more === 'boolean'
        && (page.has_more ? page.next_offset === page.items.length : page.next_offset === null)
        && page.items.every((event, index) => event.tenant_id === scope.tenantId
          && event.project_id === page.project_id && event.task_id === taskId
          && event.schema === 'wilsy.project.task.event.v1'
          && Number.isSafeInteger(event.revision) && event.revision >= 1
          && event.revision === task.revision - index
          && ['PROJECT_TASK_CREATED', 'PROJECT_TASK_REVISED', 'PROJECT_TASK_TRANSITIONED']
            .includes(event.event_type)
          && ['TODO', 'IN_PROGRESS', 'BLOCKED', 'DONE', 'CANCELLED']
            .includes(event.status_after)
          && typeof event.occurred_at === 'string');
      if (!valid || page.has_more || page.items.length !== task.revision
        || !page.items.length || page.items[0].revision !== task.revision
        || page.items[0].status_after !== task.status
        || page.items[page.items.length - 1].revision !== 1) {
        throw new Error('M04_LIFECYCLE_EVIDENCE_UNVERIFIED');
      }
      const verifyPage = (payload, schema, predicate) => payload?.schema === schema
        && payload.tenant_id === scope.tenantId && payload.principal_id === scope.principalId
        && payload.project_id === m04Execution.project.project_id && payload.task_id === taskId
        && payload.offset === 0 && payload.limit === 100 && payload.has_more === false
        && payload.next_offset === null && Array.isArray(payload.items)
        && payload.items.length <= 100 && payload.items.every(predicate);
      let decisions = null;
      let attachments = null;
      if (otherReplies) {
        const [approvalReply, attachmentReply] = otherReplies;
        const approvalPage = approvalReply.data;
        const attachmentPage = attachmentReply.data;
        if (!verifyPage(approvalPage, 'WILSY-PROJECT-APPROVAL-LIST/V1', item =>
          item?.tenant_id === scope.tenantId
          && item.project_id === m04Execution.project.project_id && item.task_id === taskId
          && /^par-[a-f0-9]{48}$/.test(item.approval_id || '')
          && ['PENDING', 'APPROVED', 'REJECTED'].includes(item.status))
          || new Set(approvalPage.items.map(item => item.approval_id)).size !== approvalPage.items.length
          || !verifyPage(attachmentPage, 'WILSY-PROJECT-ATTACHMENT-LIST/V1', item =>
            item?.tenant_id === scope.tenantId
            && item.project_id === m04Execution.project.project_id && item.task_id === taskId
            && /^pat-[a-f0-9]{48}$/.test(item.attachment_id || '')
            && ['QUARANTINED', 'SCAN_CLEAN_VERIFIED'].includes(item.scan_clearance_status))
          || new Set(attachmentPage.items.map(item => item.attachment_id)).size !== attachmentPage.items.length) {
          throw new Error('M04_TASK_EVIDENCE_SOURCE_UNVERIFIED');
        }
        decisions = { total: approvalPage.items.length,
          approved: approvalPage.items.filter(item => item.status === 'APPROVED').length };
        attachments = { total: attachmentPage.items.length,
          cleared: attachmentPage.items.filter(item =>
            item.scan_clearance_status === 'SCAN_CLEAN_VERIFIED').length };
      }
      setExecutionEvidence({ state: 'READY', taskId, items: page.items,
        decisions, attachments, error: '' });
    } catch (failure) {
      if (!active(key) || sequence !== executionEvidenceReadRef.current.sequence
        || failure?.name === 'CanceledError' || failure?.name === 'AbortError') return;
      setExecutionEvidence({ state: failure?.response?.status === 403 ? 'DENIED' : 'UNAVAILABLE',
        taskId, items: [], error: 'Projects could not independently verify the complete current task event chain. No completion evidence certified.' });
    }
  };

  const verifiedFoundationPlanCount = delivery.state === 'READY' && delivery.page
    ? FOUNDATION_EXECUTION_PLAN.filter(entry => delivery.page.items.some(item =>
      item.title === entry.title && item.kind === entry.kind)).length
    : 0;
  const foundationPlanRemaining = FOUNDATION_EXECUTION_PLAN.length - verifiedFoundationPlanCount;

  const admitFoundationPlan = async () => {
    const projectId = delivery.projectId;
    const project = projectItems.find(item => item.project_id === projectId);
    const key = sessionKey;
    if (!key || classification !== 'STRATEGY' || projectState !== 'READY'
      || delivery.state !== 'READY' || !project || project.name !== FOUNDATION_PROJECT_NAME
      || foundationPlanRemaining === 0 || delivery.page.has_more
      || planMutation.current || typeof globalThis.crypto?.randomUUID !== 'function') return;
    const nonce = Symbol('strategy-plan');
    planMutation.current = nonce;
    setPlanState({ state: 'RUNNING', created: 0, skipped: 0, message: 'Rechecking existing EOS tasks before any creation…' });
    const headers = { 'X-Tenant-ID': scope.tenantId, Authorization: 'Bearer ' + auth.token };
    let created = 0;
    let skipped = 0;
    try {
      const getPage = async () => {
        const { data: page } = await api.get('/projects/' + encodeURIComponent(projectId) + '/tasks', {
          params: { limit: 100, offset: 0 }, headers,
        });
        if (!active(key) || planMutation.current !== nonce) throw new Error('PLAN_SCOPE_CHANGED');
        if (page?.schema !== 'WILSY-PROJECT-TASK-LIST/V1'
          || page.tenant_id !== scope.tenantId || page.principal_id !== scope.principalId
          || page.project_id !== projectId || page.limit !== 100 || page.offset !== 0
          || page.has_more !== false || page.next_offset !== null
          || !Array.isArray(page.items) || page.items.length > 100
          || new Set(page.items.map(item => item.task_id)).size !== page.items.length
          || page.items.some(item => item?.tenant_id !== scope.tenantId
            || item.project_id !== projectId
            || !/^ptk-[a-f0-9]{48}$/.test(item.task_id)
            || !['TASK', 'MILESTONE'].includes(item.kind)
            || typeof item.title !== 'string')) {
          throw new Error('PLAN_PROJECT_TASK_PAGE_UNVERIFIED');
        }
        return page.items;
      };
      let current = await getPage();
      for (const entry of FOUNDATION_EXECUTION_PLAN) {
        if (!active(key) || planMutation.current !== nonce) throw new Error('PLAN_SCOPE_CHANGED');
        // Exact project-title identity is deterministic; never match by
        // keyword, auto-edit existing tasks, or assume earlier plans are done.
        const matches = current.filter(item => item.title === entry.title);
        if (matches.length > 1 || (matches.length === 1 && matches[0].kind !== entry.kind))
          throw new Error('PLAN_DUPLICATE_OR_KIND_CONFLICT');
        if (matches.length === 1) {
          skipped += 1;
          setPlanState({ state: 'RUNNING', created, skipped, message: entry.key + ' already source-verified.' });
          continue;
        }
        const body = {
          kind: entry.kind, title: entry.title, description: entry.description,
          assignee_principal_id: null, due_date: null, parent_task_id: null, depends_on: [],
        };
        // Scoped stable key supports safe server replay when a response was
        // lost; do not use random keys that could double-create on retry.
        const commandKey = 'strategy-foundation-v1-' + projectId + '-' + entry.key;
        const { data: receipt } = await api.post('/projects/' + encodeURIComponent(projectId) + '/tasks',
          body, { headers: { ...headers, 'Idempotency-Key': commandKey } });
        if (!active(key) || planMutation.current !== nonce) throw new Error('PLAN_SCOPE_CHANGED');
        if (receipt?.schema !== 'WILSY-PROJECT-TASK-RESULT/V1'
          || receipt.tenant_id !== scope.tenantId || receipt.principal_id !== scope.principalId
          || receipt.project_id !== projectId || receipt.task?.tenant_id !== scope.tenantId
          || receipt.task?.project_id !== projectId || receipt.task?.kind !== entry.kind
          || receipt.task?.title !== entry.title
          || !/^ptk-[a-f0-9]{48}$/.test(receipt.task?.task_id || '')) {
          throw new Error('PLAN_CREATE_RECEIPT_INVALID');
        }
        current = await getPage();
        if (!current.some(item => item.task_id === receipt.task.task_id
          && item.title === entry.title && item.kind === entry.kind)) {
          throw new Error('PLAN_CREATE_READBACK_UNVERIFIED');
        }
        created += 1;
        setPlanState({ state: 'RUNNING', created, skipped, message: entry.key + ' source-verified.' });
      }
      setPlanState({ state: 'COMPLETE', created, skipped,
        message: created + ' created and independently verified; ' + skipped + ' previously present.' });
      await loadDelivery(projectId, 0);
    } catch (failure) {
      if (active(key) && planMutation.current === nonce) {
        const status = failure?.response?.status;
        const bounded = status === 401 || status === 403 ? 'EOS denied task creation or readback.'
          : status === 409 ? 'EOS reported a task conflict.'
            : status === 503 ? 'EOS task source is unavailable.'
              : 'One plan item could not be independently verified.';
        setPlanState({ state: 'FAILED', created, skipped,
          message: bounded + ' ' + created + ' created, ' + skipped
            + ' already verified. Refresh the project before retrying; existing tasks are retained.' });
        await loadDelivery(projectId, 0);
      }
    } finally {
      if (planMutation.current === nonce) planMutation.current = null;
    }
  };

  /** Explicitly request the existing administrator-governed Founder admission. */
  const activateFounderProjects = async () => {
    const key = sessionKey;
    if (!key || admissionBusy || projectState !== 'DENIED') return;
    setAdmissionBusy(true); setAdmissionStatus('');
    try {
      const response = await api.post('/projects/founder-projects-admission', {}, {
        headers: { 'X-Tenant-ID': scope.tenantId, Authorization: 'Bearer ' + auth.token },
      });
      if (!active(key)) return;
      const result = response?.data;
      if (result?.schema !== 'WILSY-FOUNDER-PROJECTS-ADMISSION/V1'
          || result.tenant_id !== scope.tenantId || result.principal_id !== scope.principalId
          || result.project_role !== 'ACTIVE' || result.projects_entitlement !== 'ACTIVE') {
        throw new Error('PROJECTS_ADMISSION_READBACK_INVALID');
      }
      setAdmissionStatus('Source-confirmed: Founder Projects role and entitlement ACTIVE. Loading Projects…');
      await loadProjects();
    } catch (failure) {
      if (!active(key)) return;
      const code = failure?.response?.data?.detail;
      const status = failure?.response?.status;
      const boundedCode = typeof code === 'string' && /^[A-Z][A-Z0-9_]{1,90}$/.test(code) ? code : null;
      const category = status === 401 ? 'HTTP 401 · Founder session requires authentication.'
        : status === 403 ? 'HTTP 403 · Current Founder invitation or entitlement-issuance IAM denied.'
          : status === 404 || status === 405 ? 'HTTP ' + status + ' · Updated activation route is not running on this EOS instance.'
            : status === 409 ? 'HTTP 409 · Existing role, invitation, or entitlement state conflicts with admission.'
              : status === 503 ? 'HTTP 503 · EOS authority, entitlement composition, or database readiness unavailable.'
                : status ? 'HTTP ' + status + ' · Founder Projects admission not verified.'
                  : 'No verified HTTP response · EOS connection or request failed.';
      setAdmissionStatus((boundedCode ? boundedCode + ' · ' : '') + category);
    } finally {
      if (active(key)) setAdmissionBusy(false);
    }
  };

  /** Create only a canonical EOS project, then verify list and detail readback. */
  const createStrategyProject = async event => {
    event.preventDefault();
    const key = sessionKey;
    const pillar = STRATEGY_PILLARS.find(item => item.section_id === projectPillar);
    const name = projectName.trim();
    if (!key || !pillar || !name || name.length > 180 || projectBusy
      || projectState !== 'READY' || projectMutation.current) return;
    const summary = [
      'Strategy reference (descriptive only, not a governed relationship): ' + pillar.title + '.',
      'Founder-approved Strategy source version: 1.1.0.',
      projectDescription.trim(),
    ].filter(Boolean).join('\n');
    if (summary.length > 4000 || typeof globalThis.crypto?.randomUUID !== 'function') {
      setProjectError('The project description is too long or a secure command key is unavailable.'); return;
    }
    const body = { name, code: null, summary, start_date: null, target_date: null };
    const intent = JSON.stringify([key, body]);
    if (projectReplay.current.intent !== intent) projectReplay.current = { intent, key: globalThis.crypto.randomUUID() };
    const nonce = Symbol('project'); projectMutation.current = nonce;
    setProjectBusy(true); setProjectError(''); setProjectSuccess('');
    try {
      const config = { headers: { 'X-Tenant-ID': scope.tenantId,
        Authorization: 'Bearer ' + auth.token, 'Idempotency-Key': projectReplay.current.key } };
      const created = (await api.post('/projects', body, config)).data;
      if (!active(key) || projectMutation.current !== nonce) return;
      const item = created?.project;
      if (created?.schema !== 'WILSY-PROJECT-RESULT/V1' || created.tenant_id !== scope.tenantId
        || created.principal_id !== scope.principalId || created.authority?.source !== 'PYTHON_EOS_PROJECT_REGISTRY'
        || item?.tenant_id !== scope.tenantId || !item.project_id || item.name !== name
        || !Number.isSafeInteger(item.revision)) throw new Error('PROJECT_CREATE_READBACK_INVALID');
      const items = await loadProjects();
      if (!active(key) || projectMutation.current !== nonce) return;
      if (!items?.some(current => current.project_id === item.project_id && current.revision === item.revision)) {
        throw new Error('PROJECT_LIST_READBACK_UNVERIFIED');
      }
      const details = (await api.get('/projects/' + encodeURIComponent(item.project_id), {
        headers: { 'X-Tenant-ID': scope.tenantId, Authorization: 'Bearer ' + auth.token },
      })).data;
      if (!active(key) || projectMutation.current !== nonce) return;
      if (details?.schema !== 'WILSY-PROJECT-RESULT/V1' || details.tenant_id !== scope.tenantId
        || details.principal_id !== scope.principalId || details.project?.project_id !== item.project_id
        || details.project?.revision !== item.revision || details.project?.summary !== summary) {
        throw new Error('PROJECT_DETAIL_READBACK_UNVERIFIED');
      }
      projectReplay.current = { intent: '', key: null };
      setProjectName(''); setProjectDescription('');
      setProjectSuccess('EOS confirmed project creation and durable list/detail readback. Open project delivery to update its lifecycle and review audit events; strategic linkage and ownership are not yet governed.');
    } catch (failure) {
      if (active(key) && projectMutation.current === nonce) setProjectError(projectFailure(failure));
    } finally {
      if (active(key) && projectMutation.current === nonce) { projectMutation.current = null; setProjectBusy(false); }
    }
  };

  const load = useCallback(async (nextQuery = queryRef.current) => {
    const request = ++readId.current;
    const key = sessionKey;
    readController.current?.abort();
    const controller = new AbortController(); readController.current = controller;
    setLoading(true); setError(null); setSource(null); setHistory(null); setMessage('');
    if (!key) { setLoading(false); setError(sourceError({ code: 'COMPANY_DOCUMENT_AUTHENTICATED_SCOPE_REQUIRED' })); return; }
    try {
      const result = await readCompanyOperatingDocument(classification, scope, { token: auth.token, signal: controller.signal, ...nextQuery });
      if (!active(key) || request !== readId.current) return;
      setSource({ scope: key, classification, data: result });
    } catch (failure) {
      if (active(key) && request === readId.current && failure?.name !== 'AbortError' && failure?.name !== 'CanceledError') setError(sourceError(failure));
    } finally { if (active(key) && request === readId.current) setLoading(false); }
  }, [classification, sessionKey, auth.token]);

  useEffect(() => {
    epoch.current = sessionKey;
    const fresh = { review: false, revision: null };
    queryRef.current = fresh; setQuery(fresh); setHistory(null); setTab('document');
    setEditorOpen(false); setRatificationOpen(false); setPreviewOpen(false); setProposal(emptyProposal()); setApprovalReference(''); setEffectiveFrom('');
    setMessage(''); setCommandIssue(null); setBusy(false); retryKeys.current.clear(); commandLock.current = null;
    void load(fresh);
    return () => { readId.current += 1; readController.current?.abort(); epoch.current = null; };
  }, [load]);

  useEffect(() => {
    const trigger = window.document.activeElement;
    const formerOverflow = window.document.body.style.overflow;
    window.document.body.style.overflow = 'hidden'; closeRef.current?.focus();
    return () => { window.document.body.style.overflow = formerOverflow; trigger?.focus?.(); };
  }, []);

  useEffect(() => {
    if (!commandIssue) return;
    // A rejected Save may occur after scrolling through every Strategy section.
    // Bring the bounded EOS operation evidence into view without clearing work.
    if (scrollRef.current) scrollRef.current.scrollTop = 0;
    commandIssueRef.current?.focus({ preventScroll: true });
  }, [commandIssue]);

  useEffect(() => {
    if (!editorOpen) return;
    // The author workspace replaces the long source view. Always bring its
    // first control into the visible dialog viewport, including after a
    // return from a previously scrolled document or project readback.
    if (scrollRef.current) scrollRef.current.scrollTop = 0;
    editorRef.current?.focus({ preventScroll: true });
  }, [editorOpen]);

  useEffect(() => {
    if (!ratificationOpen) return;
    // A publication decision is a new operating context, not a scroll target
    // at the bottom of six strategic pillars and the Projects workspace.
    if (scrollRef.current) scrollRef.current.scrollTop = 0;
    ratificationDateRef.current?.focus({ preventScroll: true });
  }, [ratificationOpen]);

  const changeQuery = next => {
    queryRef.current = next; setQuery(next); setTab('document'); setEditorOpen(false); setRatificationOpen(false); setPreviewOpen(false); setHistory(null); setCommandIssue(null);
    void load(next);
  };
  const openHistory = async () => {
    if (!sessionKey || busy) return;
    const key = sessionKey; const request = ++readId.current;
    readController.current?.abort(); const controller = new AbortController(); readController.current = controller;
    setTab('history'); setLoading(true); setError(null); setHistory(null);
    try {
      const result = await readCompanyDocumentHistory(classification, scope, { token: auth.token, signal: controller.signal, review: query.review });
      if (active(key) && request === readId.current) setHistory({ scope: key, classification, data: result });
    } catch (failure) { if (active(key) && request === readId.current && failure?.name !== 'CanceledError' && failure?.name !== 'AbortError') setError(sourceError(failure)); }
    finally { if (active(key) && request === readId.current) setLoading(false); }
  };
  const perform = async (action, payload) => {
    if (!sessionKey || commandLock.current || !data || !actions.includes(action)) return;
    const key = sessionKey; const commandToken = Symbol(action); commandLock.current = commandToken;
    const intent = JSON.stringify([classification, action, payload]);
    if (!retryKeys.current.has(intent)) {
      if (typeof globalThis.crypto?.randomUUID !== 'function') { commandLock.current = null; setError(sourceError(null)); return; }
      retryKeys.current.set(intent, globalThis.crypto.randomUUID());
    }
    setBusy(true); setMessage(''); setCommandIssue(null); setError(null);
    let acknowledged = false;
    try {
      const receipt = await commandCompanyDocument(classification, scope, action, payload, retryKeys.current.get(intent), { token: auth.token });
      acknowledged = true;
      if (!active(key) || commandLock.current !== commandToken) return;
      const next = { review: true, revision: null };
      readController.current?.abort(); const controller = new AbortController(); readController.current = controller;
      const readback = await readCompanyOperatingDocument(classification, scope, { token: auth.token, signal: controller.signal, ...next });
      if (readback.document?.revision !== receipt.revision || readback.document?.fingerprint !== receipt.fingerprint) throw new Error('COMPANY_DOCUMENT_READBACK_UNVERIFIED');
      if (!active(key) || commandLock.current !== commandToken) return;
      readId.current += 1; queryRef.current = next; setQuery(next); setSource({ scope: key, classification, data: readback });
      setEditorOpen(false); setRatificationOpen(false); setPreviewOpen(false); setHistory(null); setTab('document'); retryKeys.current.delete(intent);
      setCommandIssue(null);
      setMessage('EOS confirmed the command and its durable document readback.');
    } catch (failure) {
      if (!active(key) || commandLock.current !== commandToken) return;
      const issue = commandFailure(failure, action, acknowledged);
      if (issue.kind === 'PUBLISHED_VERSION_CONFLICT') {
        // Reconcile the immutable published-version conflict, never repeat a
        // failed or timed-out command or assume a previous ratification succeeded.
        try {
          const history = await readCompanyDocumentHistory(classification, scope, {
            token: auth.token, review: true,
          });
          const published = history.items.find(item =>
            item.state === 'PUBLISHED' && item.document_version === payload.document_version);
          if (!published) throw new Error('COMPANY_DOCUMENT_PUBLICATION_READBACK_UNVERIFIED');
          const next = { review: true, revision: published.revision };
          const verified = await readCompanyOperatingDocument(classification, scope, {
            token: auth.token, ...next,
          });
          if (verified.document?.revision !== published.revision
            || verified.document.fingerprint !== published.fingerprint
            || verified.document.state !== 'PUBLISHED'
            || verified.document.document_version !== payload.document_version) {
            throw new Error('COMPANY_DOCUMENT_PUBLICATION_READBACK_UNVERIFIED');
          }
          if (!active(key) || commandLock.current !== commandToken) return;
          readId.current += 1; readController.current?.abort();
          queryRef.current = next; setQuery(next); setSource({ scope: key, classification, data: verified });
          setEditorOpen(false); setRatificationOpen(false); setPreviewOpen(false);
          setHistory(null); setTab('document'); retryKeys.current.delete(intent);
          setCommandIssue(null);
          setMessage('EOS independently verified existing published Strategy version '
            + published.document_version + ', revision ' + published.revision
            + '. This draft command created no new revision. Effectiveness must be verified separately.');
          return;
        } catch {
          if (!active(key) || commandLock.current !== commandToken) return;
          setCommandIssue(issue);
          return;
        }
      }
      setCommandIssue(issue);
    } finally { if (active(key) && commandLock.current === commandToken) { commandLock.current = null; setBusy(false); } }
  };
  const trapKeyboard = event => {
    if (event.key === 'Escape') { event.stopPropagation(); onClose(); }
    if (event.key !== 'Tab') return;
    const nodes = [...containerRef.current.querySelectorAll('button:not([disabled]),input:not([disabled]),textarea:not([disabled]),select:not([disabled]),a[href]')]
      .filter(node => node.getClientRects().length > 0);
    const first = nodes[0]; const last = nodes[nodes.length - 1];
    if (event.shiftKey && window.document.activeElement === first) { event.preventDefault(); last?.focus(); }
    else if (!event.shiftKey && window.document.activeElement === last) { event.preventDefault(); first?.focus(); }
  };
  const publish = event => {
    event.preventDefault();
    const effective = new Date(effectiveFrom);
    if (!Number.isFinite(effective.getTime())) {
      setError({ kind: 'INVALID_DATE', code: 'COMPANY_DOCUMENT_EFFECTIVE_DATE_INVALID', status: null, title: 'A valid effective date is required', message: 'Choose when the independently approved document should become effective.', next: 'Refresh the source and enter a valid effective date before submitting approval.' });
      return;
    }
    if (classification === 'STRATEGY' && actions.includes('FOUNDER_RATIFY')) {
      void perform('FOUNDER_RATIFY', {
        expected_revision: data?.current_revision ?? 0, effective_from: effective.toISOString(),
      });
    } else {
      void perform('PUBLISH', { expected_revision: data?.current_revision ?? 0,
        approval_reference: approvalReference, effective_from: effective.toISOString() });
    }
  };
  const expected = data?.current_revision ?? 0;
  const founderDraftPermitted = classification === 'STRATEGY' && actions.includes('FOUNDER_CREATE_DRAFT');
  const draftPermitted = actions.includes('CREATE_DRAFT') || founderDraftPermitted;
  // A grant may allow new revisions, not repetition of completed v1.1.0.
  const approvedSourceAlreadyPublished = classification === 'STRATEGY'
    && data?.state === 'PUBLISHED';
  const executionFirst = approvedSourceAlreadyPublished && !query.review && query.revision === null;
  const showPublicationBody = !executionFirst || strategyMode === 'DOCUMENT';
  const showExecutionSurface = !executionFirst || strategyMode === 'EXECUTION';
  // Filtering is view-only; EOS project authority and linked source snapshots
  // are validated against unfiltered projectItems, never rendered search rows.
  const visibleStrategyProjects = projectItems.filter(item => item.name.toLocaleLowerCase()
    .includes(projectSearch.trim().toLocaleLowerCase()));
  // Document Contents cannot navigate to a section until the publication has
  // mounted. This does not issue another source read or mutate publication.
  useEffect(() => {
    if (showPublicationBody && pendingDocumentSection) {
      containerRef.current?.querySelector('[data-document-section="' + pendingDocumentSection + '"]')
        ?.scrollIntoView({ behavior: 'smooth', block: 'start' });
      setPendingDocumentSection(null);
    }
  }, [showPublicationBody, pendingDocumentSection]);
  const strategyPublicationEffective = classification === 'STRATEGY'
    && !query.review && data?.state === 'PUBLISHED'
    && document?.state === 'PUBLISHED'
    && Number.isSafeInteger(document.revision)
    && typeof document.effective_from === 'string'
    && Date.parse(document.effective_from) <= Date.parse(data.as_of);
  const strategyPillarOneSource = strategyPublicationEffective
    && document.sections?.some(section => section.section_id === 'pillar-one');
  const strategyCurrentLink = strategyLink.state === 'READY'
    && strategyLink.items.some(item => item.pillar_id === 'pillar-one'
      && item.project_id === delivery.projectId && item.state === 'VERIFIED_CURRENT');

  const reviewPermitted = actions.includes('REVIEW_DRAFTS');
  const submittedDraft = document?.state === 'SUBMITTED';
  const authorDraft = document?.state === 'DRAFT';
  const updateSection = (index, update) => setProposal(previous => ({
    ...previous,
    sections: previous.sections.map((section, i) => i === index ? { ...section, ...update } : section),
  }));
  const moveSection = (index, direction) => setProposal(previous => {
    const target = index + direction;
    if (target < 0 || target >= previous.sections.length) return previous;
    const sections = [...previous.sections];
    [sections[index], sections[target]] = [sections[target], sections[index]];
    return { ...previous, sections };
  });
  const removeSection = index => setProposal(previous => previous.sections.length <= 1 ? previous : ({
    ...previous, sections: previous.sections.filter((section, i) => i !== index),
  }));
  const addSection = () => setProposal(previous => {
    if (previous.sections.length >= 24) return previous;
    const existing = new Set(previous.sections.map(section => section.section_id));
    let number = 1;
    while (existing.has('section-' + number)) number += 1;
    return { ...previous, sections: [
      ...previous.sections, { section_id: 'section-' + number, title: '', body: '' },
    ] };
  });
  const proposalCharacters = proposal.sections.reduce((sum, section) => sum + section.body.length, 0);
  const proposalValid = Boolean(proposal.title.trim()
    && /^\d+\.\d+\.\d+$/.test(proposal.document_version)
    && proposal.sections.every(section => section.title.trim() && section.body.trim())
    && proposalCharacters <= 100000);

  return createPortal(<div className={styles.backdrop} onMouseDown={event => { if (event.target === event.currentTarget) onClose(); }}>
    <section ref={containerRef} className={styles.viewer} role="dialog" aria-modal="true" aria-labelledby="company-document-title" data-company-document={classification} onKeyDown={trapKeyboard}>
      <header className={styles.header}><img src={WILSY_PLATFORM_LOGO_SRC} alt="WILSY OS logo"/><div><span>WILSY · COMPANY OPERATING DOCUMENTS</span><h1 id="company-document-title">{labelFor(classification)}</h1></div><button ref={closeRef} type="button" onClick={onClose} aria-label="Close company document"><X size={20}/></button></header>
      <div className={styles.toolbar}><button type="button" onClick={() => { if (classification === 'STRATEGY') setStrategyMode('DOCUMENT'); changeQuery({ review: false, revision: null }); }} disabled={busy}><ArrowLeft size={14}/> Current publication</button><button type="button" onClick={() => changeQuery(queryRef.current)} disabled={loading || busy}><RefreshCw size={14} className={loading ? styles.spin : ''}/> Refresh source</button><button type="button" onClick={openHistory} disabled={busy || !sessionKey || !data || loading || Boolean(error)}><History size={14}/> Revision history</button><button type="button" onClick={onOpenWork}><ArrowUpRight size={14}/> My Work</button><button type="button" aria-controls="wilsy-document-contents" aria-expanded={contentsOpen} onClick={() => setContentsOpen(open => !open)}><BookOpen size={14}/>{contentsOpen ? 'Hide contents' : 'Show contents'}</button></div>
      <div className={styles.body} style={contentsOpen ? undefined : { gridTemplateColumns: 'minmax(0,1fr)' }}>
        {contentsOpen && <aside id="wilsy-document-contents" className={styles.contents} aria-label="Document contents"><p>CONTENTS</p>{data && !error && !loading && tab === 'document' && !editorOpen && !ratificationOpen ? (document?.sections || FOUNDER_APPROVED_SOURCE[classification].sections).map(section => <button type="button" key={section.section_id} onClick={() => {
          if (executionFirst && !showPublicationBody) {
            setPendingDocumentSection(section.section_id);
            setStrategyMode('DOCUMENT');
          } else {
            containerRef.current?.querySelector('[data-document-section="' + section.section_id + '"]')
              ?.scrollIntoView({ behavior: 'smooth', block: 'start' });
          }
        }}>{section.title}</button>) : <span>Publication overview</span>}<div className={styles.sourceBoundary}><ShieldCheck size={18}/><strong>Source-owned publication</strong><p>Preparation and submission are distinct from independent approval.</p></div></aside>}
        <div ref={scrollRef} className={styles.scroll}>
          {message && <p className={styles.success} role="status"><CheckCircle2 size={16}/>{message}</p>}
          {commandIssue && <section ref={commandIssueRef} tabIndex={-1} className={styles.notice} role="alert"
            aria-label="Company document command failure" data-document-state={commandIssue.kind}>
            <ShieldCheck size={22} aria-hidden="true"/>
            <h2>{commandIssue.title}</h2>
            <p><strong>Operation:</strong> {commandIssue.operation}</p>
            <p>{commandIssue.message}</p>
            <p><strong>HTTP status:</strong> {commandIssue.status ?? 'No verified response'}</p>
            <p><strong>EOS reference:</strong> {commandIssue.code}</p>
            <p>{commandIssue.next}</p>
            <button type="button" onClick={() => setCommandIssue(null)}>Continue editing</button>
            {commandIssue.kind === 'READBACK_UNVERIFIED' && <button type="button"
              onClick={() => changeQuery({ review: true, revision: null })}>Verify recorded revision</button>}
          </section>}
          {error && <section className={styles.notice} role="alert" data-document-state={error.kind}>
            <ShieldCheck size={28} aria-hidden="true"/><h2>{error.title}</h2><p>{error.message}</p>
            <dl className={styles.sourceStatus} aria-label="Document source status">
              <div><dt>Requested document</dt><dd>{labelFor(classification)}</dd></div>
              <div><dt>Publication source</dt><dd>/api/company-operating-documents/{classification}</dd></div>
              <div><dt>Operation status</dt><dd>{error.status ? 'HTTP ' + error.status : error.kind === 'AUTHENTICATION_REQUIRED' ? 'Not sent · current session required' : 'No verified response'}</dd></div>
              <div><dt>Reference</dt><dd>{error.code}</dd></div>
            </dl>
            <h3>Next step</h3><p>{error.next}</p>
            <button type="button" onClick={() => changeQuery({ review: false, revision: null })} disabled={busy}>Retry source read</button>
            <p className={styles.boundaryNote}>Company document access and publication are governed independently. The source-verified canonical Founder may ratify Strategy; other principals require separately authorized publication.</p>
          </section>}
          {loading ? <div className={styles.loading} role="status"><Loader2 className={styles.spin} size={24}/> Loading the authorized document source…</div>
            : error ? null : tab === 'history' ? <section className={styles.paper}><h2>Revision history</h2><p>Only revisions permitted for your current company capacity appear here.</p>{currentHistory?.items.length ? currentHistory.items.map(item => <button className={styles.revisionRow} key={item.revision} type="button" onClick={() => changeQuery({ review: query.review, revision: item.revision })}><FileText size={18}/><span><strong>Version {item.document_version} · revision {item.revision}</strong><small>{item.state} · {displayDate(item.recorded_at)}</small></span><ArrowUpRight size={15}/></button>) : !error && <p>No permitted revisions are available.</p>}</section>
              : data && <>
                {!executionFirst && <nav className={styles.commandDeck} aria-label="Company document actions">
                  <div className={styles.commandStatus}>
                    <strong>{ratificationOpen ? 'Founder ratification · private decision'
                      : editorOpen ? 'Private draft workspace'
                      : query.review ? 'Private source review'
                      : document?.state === 'PUBLISHED' ? 'Official publication'
                        : authorDraft ? 'Draft under review'
                          : submittedDraft ? (actions.includes('FOUNDER_RATIFY') ? 'Founder ratification available' : 'Awaiting independent approval')
                            : 'Founder-approved source · EOS publication pending'}</strong>
                    <span>{ratificationOpen ? 'Submitted Strategy · publication not yet effective'
                      : editorOpen ? 'Unpublished · editing in your current session'
                      : query.review ? 'Private authorised source view'
                        : 'Public source view · verified by EOS'}</span>
                  </div>
                  <div className={styles.commandButtons}>
                    {ratificationOpen && <button type="button" disabled={busy}
                      onClick={() => setRatificationOpen(false)}>
                      <ArrowLeft size={16}/> Back to submitted Strategy
                    </button>}
                    {!ratificationOpen && draftPermitted && !editorOpen && !approvedSourceAlreadyPublished && <button type="button" disabled={busy}
                      onClick={() => { setProposal(founderApprovedProposal(classification)); setPreviewOpen(false); setEditorOpen(true); }}>
                      <FileText size={16}/> Prepare approved v1.1.0
                    </button>}
                    {!ratificationOpen && reviewPermitted && !query.review && <button type="button" disabled={busy}
                      onClick={() => changeQuery({ review: true, revision: null })}>
                      <BookOpen size={16}/> Review private source
                    </button>}
                    {!ratificationOpen && query.review && <button type="button" disabled={busy}
                      onClick={() => changeQuery({ review: false, revision: null })}>
                      <ArrowLeft size={16}/> Published view
                    </button>}
                    {!ratificationOpen && (actions.includes('SUBMIT') || actions.includes('FOUNDER_SUBMIT')) && <button type="button" disabled={busy}
                      onClick={() => void perform(actions.includes('FOUNDER_SUBMIT') ? 'FOUNDER_SUBMIT' : 'SUBMIT', { expected_revision: expected })}>
                      <ArrowUpRight size={16}/> {actions.includes('FOUNDER_SUBMIT') ? 'Submit Founder Strategy' : 'Submit for approval'}
                    </button>}
                    {!ratificationOpen && classification === 'STRATEGY' && query.review
                      && document?.state === 'SUBMITTED' && actions.includes('FOUNDER_RATIFY')
                      && <button type="button" disabled={busy}
                        onClick={() => setRatificationOpen(true)}>
                        <ShieldCheck size={16}/> Open Founder ratification
                      </button>}
                  </div>
                  {!draftPermitted && !reviewPermitted && !actions.includes('SUBMIT')
                    && !actions.includes('PUBLISH') && !actions.includes('FOUNDER_RATIFY') && <p className={styles.permissionNotice}>
                      Your current EOS permission allows reading this Founder-approved source, not creating a revision or publishing it.
                      Draft and approval actions require separately verified company-document authority.
                    </p>}
                </nav>}
                {editorOpen && draftPermitted && <form ref={editorRef} tabIndex={-1} className={styles.form}
                  aria-label="Company private draft editor"
                  onSubmit={event => { event.preventDefault(); if (proposalValid) void perform(founderDraftPermitted ? 'FOUNDER_CREATE_DRAFT' : 'CREATE_DRAFT', { ...proposal, expected_revision: expected }); }}>
                  <div className={styles.editorHeading}>
                    <div><span className={styles.eyebrow}>AUTHOR WORKSPACE · PRIVATE</span>
                      <h2>Prepare {classification === 'MISSION' ? 'Our Mission' : 'Our Strategy'}</h2>
                      <p>Review the Founder-approved v1.1.0 wording from the supplied PDF. Save only through authorized Python EOS; content approval does not imply EOS publication.</p>
                    </div>
                    <button type="button" disabled={busy} onClick={() => setPreviewOpen(value => !value)}
                      aria-pressed={previewOpen}>{previewOpen ? 'Edit document' : 'Preview draft'}</button>
                  </div>
                  {previewOpen ? <div className={styles.preview} role="region" aria-label="Unpublished draft preview">
                    <span className={styles.eyebrow}>UNPUBLISHED PREVIEW · NOT COMPANY POLICY</span>
                    <h3>{proposal.title || 'Untitled private proposal'}</h3>
                    <p>Version {proposal.document_version || 'not set'}</p>
                    {proposal.sections.map(section => <section key={section.section_id}>
                      <h4>{section.title || 'Untitled section'}</h4>
                      <p>{section.body || 'No content yet'}</p>
                    </section>)}
                  </div> : <>
                    <div className={styles.editorMeta}>
                      <label>Document title<input required maxLength={200} value={proposal.title}
                        onChange={event => setProposal(value => ({ ...value, title: event.target.value }))}/></label>
                      <label>Document version<input required pattern="[0-9]+\.[0-9]+\.[0-9]+"
                        value={proposal.document_version}
                        onChange={event => setProposal(value => ({ ...value, document_version: event.target.value }))}/></label>
                    </div>
                    <div className={styles.sectionList}>
                      {proposal.sections.map((section, index) => <fieldset key={section.section_id}>
                        <legend>Section {index + 1}</legend>
                        <div className={styles.sectionControls}>
                          <span>{section.body.trim().split(/\s+/).filter(Boolean).length} words</span>
                          <button type="button" disabled={busy || index === 0}
                            aria-label={`Move section ${index + 1} up`}
                            onClick={() => moveSection(index, -1)}>Move up</button>
                          <button type="button" disabled={busy || index === proposal.sections.length - 1}
                            aria-label={`Move section ${index + 1} down`}
                            onClick={() => moveSection(index, 1)}>Move down</button>
                          <button type="button" disabled={busy || proposal.sections.length === 1}
                            aria-label={`Remove section ${index + 1}`}
                            onClick={() => removeSection(index)}>Remove</button>
                        </div>
                        <label>Section title<input required maxLength={160} value={section.title}
                          onChange={event => updateSection(index, { title: event.target.value })}/></label>
                        <label>Proposed content<textarea required maxLength={20000} rows={5} value={section.body}
                          onChange={event => updateSection(index, { body: event.target.value })}/></label>
                      </fieldset>)}
                    </div>
                  </>}
                  <div className={styles.editorFooter}>
                    <span>{proposal.sections.length} sections · {proposalCharacters.toLocaleString()} / 100,000 characters · Founder PDF SHA3-512: {FOUNDER_APPROVED_SOURCE[classification].pdf_sha3_512.slice(0, 16)}…</span>
                    <div className={styles.actions}>
                      <button type="button" disabled={busy || proposal.sections.length >= 24 || previewOpen}
                        onClick={addSection}>Add section</button>
                      <button type="submit" disabled={busy || !proposalValid}>
                        {busy ? 'Verifying EOS…' : 'Save private draft to EOS'}
                      </button>
                      <button type="button" disabled={busy}
                        onClick={() => { setEditorOpen(false); setPreviewOpen(false); }}>Close editor</button>
                    </div>
                  </div>
                </form>}
                {ratificationOpen && classification === 'STRATEGY' && query.review
                  && document?.state === 'SUBMITTED' && actions.includes('FOUNDER_RATIFY') && <form
                  className={styles.form} aria-label="Founder Strategy self-ratification"
                  onSubmit={publish}>
                  <div className={styles.editorHeading}>
                    <div><span className={styles.eyebrow}>FOUNDER DECISION · PRIVATE</span>
                      <h2>Ratify and publish your Strategy</h2>
                      <p>EOS will reverify your durable Founder designation, current membership and
                        author authority within the publication transaction. Your decision is recorded
                        as Founder self-ratification, not independent approval.</p>
                    </div>
                  </div>
                  <p>Submitted revision {data.current_revision} · {document.title}</p>
                  <label>Effective date and time<input ref={ratificationDateRef} required
                    type="datetime-local" value={effectiveFrom}
                    onChange={event => setEffectiveFrom(event.target.value)}/></label>
                  <div className={styles.editorFooter}>
                    <button type="submit" disabled={busy || !effectiveFrom}>
                      {busy ? 'Verifying EOS ratification…' : 'Ratify and publish Strategy'}
                    </button>
                    <button type="button" disabled={busy}
                      onClick={() => setRatificationOpen(false)}>Back to submitted Strategy</button>
                  </div>
                </form>}
                {!editorOpen && !ratificationOpen && <>
                {classification === 'STRATEGY' && !approvedSourceAlreadyPublished && <section aria-label="M03 Strategy governance gates"
                  className="mb-4 rounded-xl border border-slate-500/60 bg-slate-950/30 p-4 text-slate-100">
                  <h3 className="text-base font-semibold text-white">M03 · Publication and Pillar 1 governance</h3>
                  <p className="mt-2 text-sm text-slate-200">
                    Permissions are source-verified for this session and selected capacity only.
                    A durable, source-verified Founder designation plus current exact-tenant owner/IAM evidence
                    can admit Strategy self-ratification. All other personnel require distinct author and publisher
                    authority; project ownership alone grants neither.
                  </p>
                  <dl className="mt-3 grid gap-3 sm:grid-cols-2">
                    <div className="rounded-lg border border-slate-600/60 p-3">
                      <dt className="text-xs font-semibold text-slate-300">Strategy author and private-review authority</dt>
                      <dd className="mt-1 text-sm text-white">{approvedSourceAlreadyPublished
                         ? 'Published Strategy exists; prior v1.1.0 preparation is complete. New revisions need separate source authorization.'
                         : founderDraftPermitted
                         ? 'Verified Founder can prepare Strategy through durable source authority'
                        : draftPermitted ? 'Draft creation admitted by current EOS action set'
                        : actions.includes('SUBMIT')
                          ? 'Source-authorized draft submission admitted'
                          : reviewPermitted
                            ? 'Private revision review admitted; draft creation not currently offered'
                            : 'Current source offers read-only actions; author admission not established'}</dd>
                    </div>
                    <div className="rounded-lg border border-slate-600/60 p-3">
                      <dt className="text-xs font-semibold text-slate-300">Independent publisher authority</dt>
                      <dd className="mt-1 text-sm text-white">{actions.includes('FOUNDER_RATIFY')
                        ? 'Current Founder may self-ratify this submitted Strategy with audited EOS evidence'
                        : actions.includes('PUBLISH')
                        ? 'EOS admits publication for this submitted revision under the current independent principal'
                        : 'No publication action admitted in this source view; independent publisher must be verified through EOS'}</dd>
                    </div>
                    <div className="rounded-lg border border-slate-600/60 p-3">
                      <dt className="text-xs font-semibold text-slate-300">Effective Strategy publication</dt>
                      <dd className="mt-1 text-sm text-white">{strategyPublicationEffective
                         ? 'Published and effective · revision ' + document.revision
                         : query.review && approvedSourceAlreadyPublished
                           ? 'Official publication exists; see Current publication for effective date and revision'
                        : document?.state === 'SUBMITTED' ? 'Submitted · independent approval required'
                          : document?.state === 'DRAFT' ? 'Private draft · submission required'
                            : 'Not verified as published and effective'}</dd>
                    </div>
                    <div className="rounded-lg border border-slate-600/60 p-3">
                      <dt className="text-xs font-semibold text-slate-300">Pillar 1 and Foundation relationship</dt>
                      <dd className="mt-1 text-sm text-white">{strategyCurrentLink
                        ? 'EOS link verified current · strategic outcomes not certified'
                        : strategyLink.state === 'PUBLICATION_REQUIRED'
                          ? 'Not linkable · effective EOS Strategy publication required'
                          : strategyLink.state === 'READY'
                            ? strategyPillarOneSource
                              ? 'Publication verified; no current Pillar 1 link read back'
                              : 'No current Pillar 1 relationship verified'
                            : 'Current link readback not verified'}</dd>
                    </div>
                  </dl>
                  <p className="mt-3 text-xs text-slate-300">
                    Sequence: authorized draft → submission → independent publisher approval
                    (or source-verified Founder Strategy ratification) → effective published revision
                    → authorized project link → independent EOS link readback.
                    Execution metrics from M02 are not certified strategic outcomes.
                  </p>
                </section>}
                {classification === 'STRATEGY' && !approvedSourceAlreadyPublished && <section className={styles.commandDeck}
                   aria-label="Governed Strategy publication lifecycle">
                  <div className={styles.commandStatus}>
                    <strong>Strategy publication · source-owned execution</strong>
                    <span>{!document ? (query.review && approvedSourceAlreadyPublished
                        ? 'Official publication exists · no private revision selected'
                        : query.review ? 'No private revision selected' : 'Official publication not yet established')
                      : document.state === 'DRAFT' ? 'Stage 1 of 3 · Author draft'
                         : document.state === 'SUBMITTED' ? (actions.includes('FOUNDER_RATIFY')
                          ? 'Stage 2 of 3 · Founder ratification available' : 'Stage 2 of 3 · Await independent publisher')
                          : Date.parse(document.effective_from) > Date.parse(data.as_of)
                            ? 'Stage 3 of 3 · Published, awaiting effective date'
                            : 'Stage 3 of 3 · Published and effective'}</span>
                  </div>
                  <div className={styles.commandButtons}>
                    {!query.review && reviewPermitted && <button type="button" disabled={busy}
                      onClick={() => changeQuery({ review: true, revision: null })}>
                      Review authorized publication state
                    </button>}
                    {query.review && !document && draftPermitted && !approvedSourceAlreadyPublished && !editorOpen
                      && <button type="button" disabled={busy}
                        onClick={() => { setProposal(founderApprovedProposal('STRATEGY')); setPreviewOpen(false); setEditorOpen(true); }}>
                        Prepare Strategy draft
                      </button>}
                    {query.review && document?.state === 'DRAFT' && (actions.includes('SUBMIT') || actions.includes('FOUNDER_SUBMIT'))
                      && <button type="button" disabled={busy}
                        onClick={() => void perform(actions.includes('FOUNDER_SUBMIT') ? 'FOUNDER_SUBMIT' : 'SUBMIT', { expected_revision: expected })}>
                        {actions.includes('FOUNDER_SUBMIT') ? 'Submit Founder Strategy' : 'Submit Strategy for independent approval'}
                      </button>}
                    {query.review && document?.state === 'SUBMITTED' && actions.includes('PUBLISH')
                      && <button type="button" disabled={busy}
                        onClick={() => containerRef.current.querySelector('[aria-label="Independent Strategy publication approval"]')
                          ?.scrollIntoView({ behavior: 'smooth', block: 'center' })}>
                        Open independent approval form
                      </button>}
                  </div>
                  {query.review && document?.state === 'DRAFT' && !actions.includes('SUBMIT') && !actions.includes('FOUNDER_SUBMIT')
                    && <p className={styles.permissionNotice}>Only the draft's source-authorized author can submit this revision.</p>}
                  {query.review && document?.state === 'SUBMITTED' && !actions.includes('PUBLISH') && !actions.includes('FOUNDER_RATIFY')
                    && <p className={styles.permissionNotice}>Independent publication is required unless EOS verifies the canonical Founder's durable Strategy self-ratification authority for this submission.</p>}
                  {!query.review && !document && !reviewPermitted
                    && <p className={styles.permissionNotice}>Your current capacity can read the approved source but cannot inspect private revision states or create a publication. Current Strategy author/publisher authority must be established separately in tenant IAM.</p>}
                  {document?.state === 'PUBLISHED' && Date.parse(document.effective_from) <= Date.parse(data.as_of)
                    && <p className={styles.permissionNotice}>The official Strategy is published and effective. The Pillar 1 / Foundation relationship and source-owned execution require independent verification in Projects &amp; Delivery; publication does not certify outcomes.</p>}
                </section>}
                {classification === 'STRATEGY' && approvedSourceAlreadyPublished && !query.review && !executionFirst && <section
                  aria-label="Published Strategy execution handoff" className={styles.commandDeck}>
                  <div className={styles.commandStatus}>
                    <strong>Published Strategy · execution</strong>
                    <span>Publication is complete. Pillar 1 delivery requires current EOS project and relationship evidence.</span>
                  </div>
                  <div className={styles.commandButtons}>
                    <button type="button" onClick={() => {
                      if (executionFirst && strategyMode === 'DOCUMENT') setStrategyMode('EXECUTION');
                      else containerRef.current?.querySelector('[aria-label="Company operating execution"]')
                        ?.scrollIntoView({ behavior: 'smooth', block: 'start' });
                    }}>
                      <ArrowUpRight size={16}/> Inspect Projects &amp; Delivery
                    </button>
                  </div>
                  <p className={styles.permissionNotice}>{strategyCurrentLink
                    ? 'Pillar 1 / Foundation project link verified current; strategic outcomes remain uncertified.'
                    : 'Pillar 1 / Foundation relationship not yet verified in this view. Inspect the existing project and independently verify its current source link.'}</p>
                </section>}
                {executionFirst && <nav aria-label="Strategy workspace mode" className="mb-4 flex flex-wrap items-center gap-2 rounded-xl border border-slate-500/60 bg-slate-950/30 p-3">
                  <button type="button" aria-pressed={strategyMode === 'EXECUTION'}
                    className={strategyMode === 'EXECUTION'
                      ? 'min-h-10 rounded-lg border border-sky-300 bg-sky-700 px-4 py-2 text-sm font-semibold text-white shadow-sm ring-2 ring-sky-300/60'
                      : 'min-h-10 rounded-lg border border-slate-500 px-4 py-2 text-sm text-slate-200 hover:border-sky-400 hover:bg-slate-800'}
                    onClick={() => setStrategyMode('EXECUTION')}>Execution workspace</button>
                  <button type="button" aria-pressed={strategyMode === 'DOCUMENT'}
                    className={strategyMode === 'DOCUMENT'
                      ? 'min-h-10 rounded-lg border border-sky-300 bg-sky-700 px-4 py-2 text-sm font-semibold text-white shadow-sm ring-2 ring-sky-300/60'
                      : 'min-h-10 rounded-lg border border-slate-500 px-4 py-2 text-sm text-slate-200 hover:border-sky-400 hover:bg-slate-800'}
                    onClick={() => setStrategyMode('DOCUMENT')}>View full document</button>
                  {reviewPermitted && <button type="button" disabled={busy}
                    className="min-h-10 rounded-lg border border-slate-500 px-3 py-2 text-sm"
                    onClick={() => changeQuery({ review: true, revision: null })}>Review private source</button>}
                  <span className="text-xs text-slate-300">Published Strategy · revision {document?.revision}
                    {' · '}Effective {displayDate(document?.effective_from)}
                    {' · '}{strategyCurrentLink ? 'Pillar 1 link verified' : 'Pillar 1 link awaits independent readback'}
                  </span>
                </nav>}
                {showPublicationBody && <>
                <div className={styles.publication}><span className={styles.state} data-state={data.state}>{data.state === 'NOT_YET_PUBLISHED' ? 'NOT YET PUBLISHED' : data.state}</span>{query.review && <span>Authorized private review</span>}{document?.state === 'PUBLISHED' && Date.parse(document.effective_from) > Date.parse(data.as_of) && <span>Scheduled · not yet effective</span>}{query.revision && <span>Historical revision {query.revision}</span>}</div>
                {!document ? <article className={styles.paper} data-document-state="FOUNDER_APPROVED_EOS_PENDING">
                  <div className={styles.documentIdentity}>
                    <span>{classification} · FOUNDER-APPROVED SOURCE · VERSION {FOUNDER_APPROVED_SOURCE[classification].document_version}</span>
                    <h2>{FOUNDER_APPROVED_SOURCE[classification].title}</h2>
                    <p>WILSY (Pty) Ltd · Founder content approved · EOS publication pending</p>
                    <p className={styles.boundaryNote}>This is the existing Founder-approved corporate document, not an EOS-published revision. Its wording comes from the supplied source PDF. EOS publication remains pending; authorized Founder ratification or independent publication is required. No operational execution metrics are inferred.</p>
                  </div>
                  {FOUNDER_APPROVED_SOURCE[classification].sections.map(section => <section className={styles.documentSection} data-document-section={section.section_id} key={section.section_id}><h3>{section.title}</h3><p style={{ whiteSpace: 'pre-line' }}>{section.body}</p></section>)}
                  <footer className={styles.fingerprint}><span>Founder-approved PDF source · SHA3-512 (not an EOS revision fingerprint)</span><code>{FOUNDER_APPROVED_SOURCE[classification].pdf_sha3_512}</code></footer>
                </article> : <article className={styles.paper}><div className={styles.documentIdentity}><span>{classification} · SOURCE VERSION {document.document_version}</span><h2>{document.title}</h2><dl><div><dt>Prepared by</dt><dd>{document.author_principal_id}</dd></div><div><dt>Effective date</dt><dd>{displayDate(document.effective_from)}</dd></div>{document.approved_by_principal_id && <div><dt>Approved / published by</dt><dd>{document.approved_by_principal_id}</dd></div>}{document.approval_reference && <div><dt>Approval reference</dt><dd>{document.approval_reference}</dd></div>}</dl></div>{document.sections.map(section => <section className={styles.documentSection} data-document-section={section.section_id} key={section.section_id}><h3>{section.title}</h3><p>{section.body}</p></section>)}<footer className={styles.fingerprint}><span>Source evidence · SHA3-512</span><code>{document.fingerprint}</code></footer></article>}
                </>}
                {showExecutionSurface && <section className={styles.execution} aria-label="Company operating execution">
                  <h2>Business execution</h2>
                  {classification === 'STRATEGY' ? <details className="mb-4 rounded-lg border border-slate-600/60 bg-slate-900/40 px-4 py-3">
                    <summary className="cursor-pointer text-sm font-medium text-slate-200">How Strategy links to projects</summary>
                    <p className="mt-3 text-sm leading-relaxed text-slate-300">Pillar-to-project relationships require an effective EOS-published Strategy and explicit source-owned linking. Current Founder self-ratification or independent publisher approval must be verified by EOS. Neither project ownership nor strategic completion percentages are inferred. Tenant projects are not automatically linked to strategic pillars.</p>
                  </details> : <p>Pillar-to-project relationships require an effective EOS-published Strategy and explicit source-owned linking. Current Founder self-ratification or independent publisher approval must be verified by EOS. Neither project ownership nor strategic completion percentages are inferred.</p>}
                  {classification === 'STRATEGY' && <div className={styles.form} aria-label="Live EOS Projects execution">
                    <div className={styles.editorHeading}><div>
                      <span className={styles.eyebrow}>LIVE · PYTHON EOS PROJECTS</span>
                      <h3>Projects &amp; delivery</h3>
                      <p>Current tenant projects · verified through Python EOS</p>
                    </div><button type="button" disabled={projectBusy || projectState === 'LOADING'} onClick={() => void loadProjects()}>
                      <RefreshCw size={15}/> Refresh projects</button></div>
                    {projectState === 'LOADING' && <p role="status">Loading authorized projects…</p>}
                    {projectState === 'READY' && projectItems.length > 0 && <label className="mb-3 flex flex-col gap-1 text-sm text-slate-200">Find a project
                      <input type="search" value={projectSearch} onChange={event => setProjectSearch(event.target.value)}
                        placeholder="Search projects by name…" className="min-h-11 w-full rounded-lg border border-slate-500 bg-slate-950 px-3 text-sm text-white placeholder:text-slate-400"/>
                    </label>}
                    {projectState === 'READY' && <div className={styles.projectListSummary} role="status">
                      <span>{projectItems.length === 0 ? 'No projects returned by EOS on this page.' : projectSearch.trim() ? visibleStrategyProjects.length + ' matching · ' + projectItems.length + ' source-verified projects' : projectItems.length + ' verified projects on this page'}</span>
                      <span className={styles.sourceVerified}>Source verified · EOS</span>
                    </div>}
                    {projectState === 'READY' && projectItems.length > 0 && visibleStrategyProjects.length === 0 && <p role="status" className="text-sm text-slate-300">No verified projects match this search. The source project list is unchanged.</p>}
                    {projectState === 'READY' && visibleStrategyProjects.length > 0 && <ul className={styles.strategyProjectList} aria-label="EOS project list">
                      {visibleStrategyProjects.map(item => <li className={styles.strategyProjectRow} key={item.project_id}>
                        <div className={styles.strategyProjectIdentity}>
                          <strong>{item.name}</strong>
                          <div className={styles.strategyProjectMeta}>
                            <span className={styles.projectStatus} data-status={item.status}>{item.status}</span>
                            <span>Revision {item.revision}</span>
                          </div>
                        </div>
                        <div className={styles.strategyProjectActions}>
                          <button type="button" disabled={delivery.state === 'LOADING'}
                            aria-label={'Verify execution for ' + item.name}
                            aria-pressed={delivery.state === 'READY' && delivery.projectId === item.project_id}
                            onClick={() => void loadDelivery(item.project_id)}>
                            <RefreshCw size={15}/> Verify execution
                          </button>
                          {typeof onOpenProject === 'function' && <button type="button"
                            aria-label={'Open project delivery for ' + item.name}
                            onClick={() => onOpenProject(item.project_id)}>
                            Open project <ArrowUpRight size={15}/>
                          </button>}
                        </div>
                      </li>)}
                    </ul>}
                    {delivery.state === 'LOADING' && <p role="status">Verifying project tasks…</p>}
                    {(delivery.state === 'DENIED' || delivery.state === 'UNAVAILABLE') && <p role="alert">{delivery.error || 'Current project task read denied by EOS.'}</p>}
                    {delivery.state === 'READY' && delivery.page && <section className={styles.strategyDelivery} aria-label="Verified project execution">
                      <div className={styles.strategyDeliveryHeader}>
                        <div>
                          <span className={styles.eyebrow}>EOS · VERIFIED SOURCE RECORDS</span>
                          <h3>Source-verified project execution</h3>
                          <p>{projectItems.find(item => item.project_id === delivery.projectId)?.name} · {delivery.page.items.length} items on this verified page</p>
                        </div>
                        <button type="button" onClick={() => void loadDelivery(delivery.projectId, delivery.page.offset)}>
                          <RefreshCw size={15}/> Refresh execution
                        </button>
                      </div>
                      <p className={styles.strategyDeliveryNote}>Lifecycle records only. No strategic pillar linkage or Strategy completion percentage is inferred.</p>
                      <section aria-label="M04 governed Strategy execution"
                        className="mt-4 rounded-xl border border-slate-500/60 bg-slate-950/40 p-4 text-slate-100">
                        <div className="flex flex-wrap items-start justify-between gap-3">
                          <div><h4 className="text-base font-semibold text-white">M04 · Governed Strategy execution</h4>
                            <p className="mt-1 text-sm text-slate-200">Source-owned accountability, due dates,
                              dependencies and immutable task lifecycle evidence. No outcomes are inferred from task counts.</p>
                          </div>
                          {m04Execution && <button type="button" onClick={() => void loadDelivery(delivery.projectId, 0)}
                            className="rounded-lg border border-slate-500 px-3 py-2 text-sm">
                            <RefreshCw size={14} aria-hidden="true"/> Verify current work
                          </button>}
                        </div>
                        {m04Execution ? <>
                          <p className="mt-3 text-sm" role="status">Pillar 1 relationship verified against
                            Strategy revision {document.revision} and Foundation project revision {m04Execution.project.revision}.
                            {' '}Complete authorized task snapshot: {m04Execution.rows.length} work records.</p>
                          <dl className="mt-3 grid grid-cols-2 gap-3 md:grid-cols-3">
                            {[
                              ['Assigned in task source', m04Execution.assigned, 'ASSIGNED'],
                              ['Unassigned work', m04Execution.unassigned, 'UNASSIGNED'],
                              ['Waiting on predecessors', m04Execution.waiting, 'WAITING'],
                              ['Without due dates', m04Execution.missingDueDate, 'UNDATED'],
                              ['Past calendar due date', m04Execution.pastDueCalendar, 'DUE'],
                              ['Done · task lifecycle only', m04Execution.states.DONE, 'DONE'],
                            ].map(([label, value, filter]) => <div key={label}
                              className="rounded-lg border border-slate-600/70 p-1">
                              <dt><button type="button" aria-label={'Inspect ' + label.toLowerCase()}
                                onClick={() => focusExecutionWork(filter)}
                                className="w-full rounded-lg px-2 py-2 text-left text-slate-100 hover:bg-sky-950 focus-visible:outline focus-visible:outline-2 focus-visible:outline-sky-300">
                                <span className="block text-xs text-slate-300">{label}</span>
                                <span className="mt-1 block text-xl font-semibold">{value}</span>
                                <span className="block text-xs text-sky-300">Inspect work</span>
                              </button></dt>
                            </div>)}
                          </dl>
                          <p className="mt-3 text-sm font-semibold">Certified strategic outcome:
                            {' '}Not established — no authorized outcome evidence or outcome score exists in this source.
                          </p>
                          <p className="mt-1 text-xs text-slate-300">Snapshot observed: {m04Execution.observedAt}.
                            Due-date comparisons use a UTC calendar date, not a server-certified overdue decision.
                            Task DONE and audit history are not strategic outcome certification.</p>
                          <details open={executionInspectorOpen} className="mt-4 rounded-lg border border-slate-600/70 p-3">
                            <summary className="cursor-pointer font-semibold" onClick={event => {
                              event.preventDefault();
                              setExecutionInspectorOpen(open => !open);
                            }}>Inspect accountable work and lifecycle evidence · {m04Execution.rows.length} records</summary>
                            <div className="mt-3 flex flex-wrap items-end gap-3" aria-label="M04 work navigator">
                              <label className="flex min-w-48 flex-1 flex-col gap-1 text-xs text-slate-200">Find work by title
                                <input type="search" value={executionSearch} placeholder="Search verified tasks…"
                                  onChange={event => { setExecutionSearch(event.target.value); setExecutionPage(0); }}
                                  className="min-h-10 rounded-lg border border-slate-500 bg-slate-900 px-3 text-sm text-white" />
                              </label>
                              <label className="flex flex-col gap-1 text-xs text-slate-200">Show work
                                <select value={executionFilter}
                                  onChange={event => { setExecutionFilter(event.target.value); setExecutionPage(0); }}
                                  className="min-h-10 rounded-lg border border-slate-500 bg-slate-900 px-3 text-sm text-white">
                                  <option value="ALL">All verified work</option>
                                  <option value="ASSIGNED">Assigned work</option>
                                  <option value="UNASSIGNED">Unassigned</option>
                                  <option value="WAITING">Waiting on dependencies</option>
                                  <option value="UNDATED">Without due dates</option>
                                  <option value="DUE">Past due date</option>
                                  <option value="DONE">Done in task source</option>
                                </select>
                              </label>
                              <span className="text-xs text-slate-300" role="status">
                                {executionMatches.length} matching · page {safeExecutionPage + 1} of {executionPageCount}
                              </span>
                            </div>
                            {executionMatches.length === 0 && <p className="mt-3 text-sm text-slate-300">No verified work matches this view. The source work snapshot is unchanged.</p>}
                            <ul className="mt-3 divide-y divide-slate-700/70">
                              {visibleExecutionRows.map(({ task, remaining }) => <li key={task.task_id}
                                className="py-3">
                                <div className="flex flex-wrap items-center justify-between gap-2">
                                  <div><strong className="text-sm">{task.title}</strong>
                                    <p className="mt-1 text-xs text-slate-300">
                                      {task.kind} · {task.status.replaceAll('_', ' ')} · revision {task.revision}
                                      {' · '}{task.assignee_principal_id ? 'Assignment recorded in EOS' : 'Unassigned'}
                                      {' · '}{task.due_date ? 'Due ' + task.due_date : 'No due date'}
                                      {' · '}{remaining ? remaining + ' incomplete predecessor(s)' : 'Dependencies clear'}
                                    </p>
                                  </div>
                                  <button type="button" className="rounded-lg border border-slate-500 px-3 py-2 text-sm"
                                    onClick={() => void verifyExecutionEvidence(task.task_id)}>
                                    Inspect lifecycle evidence
                                  </button>
                                </div>
                                {executionEvidence.taskId === task.task_id && <div className="mt-2 text-sm"
                                  role={executionEvidence.state === 'UNAVAILABLE' || executionEvidence.state === 'DENIED' ? 'alert' : 'status'}>
                                  {executionEvidence.state === 'LOADING' && 'Reading source-owned task events…'}
                                  {executionEvidence.state === 'READY' && <>
                                    <p>Verified immutable EOS lifecycle events: {executionEvidence.items.length}.
                                      Most recent: {executionEvidence.items[0].event_type.replaceAll('_', ' ')}
                                      {' · '}{executionEvidence.items[0].status_after}
                                      {' · '}{executionEvidence.items[0].occurred_at}.
                                    </p>
                                    {task.status === 'DONE' && executionEvidence.decisions
                                      && executionEvidence.attachments && <p className="mt-1">
                                        Business decisions: {executionEvidence.decisions.approved} approved
                                        {' / '}{executionEvidence.decisions.total} recorded.
                                        {' '}Attachments: {executionEvidence.attachments.cleared} scanner-cleared
                                        {' / '}{executionEvidence.attachments.total} recorded.
                                      </p>}
                                    <p className="text-xs text-slate-300">Task lifecycle, independent business
                                      decisions and attachment scanner-clearance are different EOS authorities.
                                      None independently certifies strategic outcome attainment or payment.</p>
                                  </>}
                                  {['UNAVAILABLE', 'DENIED'].includes(executionEvidence.state)
                                    && executionEvidence.error}
                                </div>}
                              </li>)}
                            </ul>
                            {executionMatches.length > executionPageSize && <div className="mt-3 flex flex-wrap items-center justify-end gap-2">
                              <button type="button" disabled={safeExecutionPage === 0}
                                onClick={() => setExecutionPage(page => Math.max(0, page - 1))}
                                className="rounded-lg border border-slate-500 px-3 py-2 text-sm">Previous work</button>
                              <button type="button" disabled={safeExecutionPage >= executionPageCount - 1}
                                onClick={() => setExecutionPage(page => Math.min(executionPageCount - 1, page + 1))}
                                className="rounded-lg border border-slate-500 px-3 py-2 text-sm">Next work</button>
                            </div>}
                          </details>
                          {typeof onOpenProject === 'function' && <button type="button"
                            className="mt-3 rounded-lg border border-slate-500 px-3 py-2 text-sm"
                            onClick={() => onOpenProject(m04Execution.project.project_id)}>
                            Open source-owned task commands <ArrowUpRight size={14} aria-hidden="true"/>
                          </button>}
                        </> : <p role="status" className="mt-3 text-sm">
                          M04 execution unavailable until the currently effective published Strategy,
                          exact current Pillar 1 link, unchanged Foundation project revision, complete task
                          snapshot and dependencies are all independently verified. No work or outcome score inferred.{' '}Reason: {m04GateMessage}
                         </p>}
                      </section>


                      {delivery.page.items.length === 0 ? <p role="status">EOS verified no tasks on this page.</p>
                        : <details className="mt-4 rounded-lg border border-slate-600/60 p-3">
                          <summary className="cursor-pointer font-semibold">Source task register · {delivery.page.items.length} records (additional detail)</summary>
                          <ul className={styles.strategyTaskList}>{delivery.page.items.map(item =>
                          <li key={item.task_id}>
                            <div><strong>{item.title}</strong><span>{item.kind === 'MILESTONE' ? 'Milestone' : 'Task'}{item.due_date ? ' · Due ' + item.due_date : ''}</span></div>
                            <span className={styles.projectStatus} data-status={item.status}>{item.status.replaceAll('_', ' ')}</span>
                          </li>)}</ul></details>}
                      {(delivery.page.offset > 0 || delivery.page.has_more) && <div className={styles.strategyPagination}>
                        {delivery.page.offset > 0 && <button type="button" onClick={() => void loadDelivery(delivery.projectId, Math.max(0, delivery.page.offset - 50))}>Previous page</button>}
                        <span>Page {Math.floor(delivery.page.offset / 50) + 1}</span>
                        {delivery.page.has_more && <button type="button" onClick={() => void loadDelivery(delivery.projectId, delivery.page.next_offset)}>Next page</button>}
                      </div>}
                    </section>}
                    {delivery.state === 'READY' && projectItems.some(item => item.project_id === delivery.projectId
                      && item.name === FOUNDATION_PROJECT_NAME) && <section className={styles.strategyPlan}
                        aria-label="Planned My Work overhaul programme">
                      <div className={styles.strategyPlanHeader}>
                        <div>
                          <span className={styles.eyebrow}>EOS-SOURCE VERIFIED · IMPLEMENTATION REGISTER</span>
                          <h3>My Work implementation programme</h3>
                          <p role="status">{verifiedFoundationPlanCount} of 18 planned records persisted in EOS.
                            {' '}{foundationPlanRemaining} still awaiting creation. This is not Strategy completion evidence.</p>
                        </div>
                        <button type="button" onClick={() => void admitFoundationPlan()}
                          disabled={planState.state === 'RUNNING' || delivery.page.has_more || foundationPlanRemaining === 0}>
                          {planState.state === 'RUNNING' ? 'Saving verified work…'
                            : foundationPlanRemaining === 0 ? 'All 18 verified in EOS'
                              : verifiedFoundationPlanCount > 0
                                ? 'Create remaining ' + foundationPlanRemaining + ' in EOS'
                                : 'Create missing in EOS'}
                        </button>
                      </div>
                      {delivery.page.has_more && <p role="alert">Verify the full project task list before admitting the plan.</p>}
                      {typeof onOpenProject === 'function' && <button type="button"
                        className="mt-3 min-h-10 rounded-lg border border-amber-300/60 bg-slate-900 px-4 text-sm font-semibold text-amber-100 hover:bg-slate-800 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-amber-300"
                        onClick={() => onOpenProject(delivery.projectId)}>
                        Open existing project execution <ArrowUpRight size={15} aria-hidden="true"/>
                      </button>}
                      <p className="mt-3 text-xs text-slate-300">
                        Each record below shows current EOS lifecycle state. Persisted means the work exists, not that it is Done, approved, linked to a strategic pillar or published.
                      </p>
                      {foundationExecution ? <section aria-label="M02 live execution readback"
                        className="mt-4 rounded-xl border border-slate-500/50 bg-slate-950/40 p-4 text-slate-100">
                        <div className="flex flex-wrap items-center justify-between gap-2">
                          <h4 className="text-base font-semibold text-white">Live implementation execution · M02</h4>
                          <span className="text-xs text-slate-200">Successful Projects read observed: {foundationExecution.verifiedAt.replace('T', ' ').slice(0, 19)} UTC</span>
                        </div>
                        <p className="mt-2 text-sm text-slate-200">All {foundationExecution.total} programme records uniquely matched in the complete, authorized EOS project snapshot. These are task lifecycle counts, not strategic outcome certification.</p>
                        <dl className="mt-3 grid grid-cols-2 gap-3 sm:grid-cols-3 xl:grid-cols-5">
                          {[
                            ['To do', foundationExecution.counts.TODO],
                            ['In progress', foundationExecution.counts.IN_PROGRESS],
                            ['Done', foundationExecution.counts.DONE],
                            ['Blocked', foundationExecution.counts.BLOCKED],
                            ['Cancelled', foundationExecution.counts.CANCELLED],
                          ].map(([label, count]) => <div key={label} className="rounded-lg border border-slate-600/70 bg-slate-900 p-3">
                            <dt className="text-xs font-medium text-slate-300">{label}</dt>
                            <dd className="mt-1 text-xl font-bold text-white">{count}</dd>
                          </div>)}
                        </dl>
                        <div className="mt-3 grid gap-3 sm:grid-cols-2">
                          <p className="rounded-lg border border-slate-600/70 p-3 text-sm text-slate-100">
                            <strong>{foundationExecution.waiting}</strong> programme records waiting on <strong>{foundationExecution.unfinishedPredecessors}</strong> unfinished predecessor relationships
                          </p>
                          <p className="rounded-lg border border-slate-600/70 p-3 text-sm text-slate-100">
                            <strong>{foundationExecution.pastDue}</strong> unfinished records with calendar due dates before the observed UTC read date
                          </p>
                        </div>
                        <p className="mt-2 text-xs text-slate-300">Refresh execution to verify current EOS state. The timestamp is client-observed after a successful read, not a server transaction timestamp. No pillar link, publication, approval or completion is inferred.</p>
                      </section> : <p role="status" className="mt-3 rounded-lg border border-slate-500/60 p-3 text-sm text-slate-200">
                        M02 execution summary unavailable: full, unique 18-record programme coverage and predecessor readback have not both been verified. No counts are inferred.
                      </p>}

                      <details className="mt-4 rounded-lg border border-slate-600/60 p-3">
                        <summary className="cursor-pointer font-semibold">Browse all 18 planned milestones and tasks</summary>
                      <div className={styles.strategyPlanGroups}>
                        {['MILESTONE', 'TASK'].map(kind => <div key={kind}>
                          <h4>{kind === 'MILESTONE' ? 'Milestones · 6' : 'Implementation tasks · 12'}</h4>
                          <ul>{FOUNDATION_EXECUTION_PLAN.filter(entry => entry.kind === kind).map(entry => {
                            const matches = delivery.page.items.filter(item => item.title === entry.title);
                            const verified = matches.length === 1 && matches[0].kind === entry.kind;
                            return <li key={entry.key}>
                              <span>
                                {entry.title}
                                {verified && <small className="mt-1 block font-medium text-slate-300">
                                  Current EOS status: {matches[0].status.replaceAll('_', ' ')}
                                </small>}
                              </span>
                              <span className={verified ? styles.planPersisted : styles.planProposed}>
                                {verified ? 'Persisted in EOS' : 'Planned'}
                              </span>
                            </li>;
                          })}</ul>
                        </div>)}
                      </div>
                      </details>
                      {planState.state !== 'IDLE' && <p role="status" aria-live="polite">
                        {planState.message} {planState.state === 'RUNNING' ? planState.created + ' created so far.' : ''}
                      </p>}
                      <div className={styles.strategyLinkPanel} aria-label="Governed Strategy project relationship">
                        <div>
                          <h4>Strategic Pillar 1 · Project relationship</h4>
                          {strategyLink.state === 'LOADING' && <p role="status">Verifying current Strategy project link…</p>}
                          {strategyLink.state === 'UNAVAILABLE' && <p role="alert">{strategyLink.message}</p>}
                          {strategyLink.state === 'PUBLICATION_REQUIRED' && <p role="status">{strategyLink.message}</p>}
                          {strategyLink.state === 'PUBLICATION_REQUIRED' && reviewPermitted && !query.review
                            && <button type="button" onClick={() => changeQuery({ review: true, revision: null })}>
                              Review private Strategy publication workflow
                            </button>}
                          {strategyLink.state === 'LINKING' && <p role="status">{strategyLink.message}</p>}
                          {strategyLink.state === 'READY' && (() => {
                            const item = strategyLink.items.find(row => row.pillar_id === 'pillar-one'
                              && row.project_id === delivery.projectId);
                            return item ? <p role="status">{item.state === 'VERIFIED_CURRENT'
                              ? 'Linked in EOS · current Strategy and project snapshots verified. No outcome score certified.'
                              : 'Linked record found; Strategy publication or project source changed. Reverification required.'}</p>
                              : <p role="status">No governed relationship recorded for this project and pillar.</p>;
                          })()}
                        </div>
                        {strategyLink.state === 'READY'
                          && !strategyLink.items.some(item => item.project_id === delivery.projectId
                            && item.pillar_id === 'pillar-one')
                          && <button type="button" onClick={() => void linkFoundationStrategy()}
                            disabled={foundationPlanRemaining !== 0 || data?.state !== 'PUBLISHED'
                              || query.review || !document?.sections?.some(s => s.section_id === 'pillar-one')}>
                            Link verified Foundation project to Pillar 1
                          </button>}
                        <p>This binds approved source identities only. Strategic outcome attainment, independent publication,
                          task completion and financial authorization remain separate EOS authorities.</p>
                      </div>
                      <p className={styles.strategyDeliveryNote}>Creation requires current EOS project:update authority. No assignee,
                        deadline, task completion, approval, financial authorization or strategy linkage is inferred.</p>
                    </section>}
                    {projectState !== 'READY' && projectState !== 'LOADING' && <p role="status">
                      {projectError || 'Projects source has not been verified for this session.'}</p>}
                    {projectState === 'UNAVAILABLE' && typeof onOpenProjects === 'function' && <button
                      type="button" onClick={onOpenProjects}>Open existing Projects workspace</button>}
                    {projectState === 'UNAVAILABLE' && <p role="status">
                      Your existing project has not been changed. A transient read was retried once.
                      Check the Python EOS Projects transaction failure code if the source remains unavailable.
                    </p>}
                    {projectState === 'DENIED' && <button type="button"
                      disabled={admissionBusy} onClick={() => void activateFounderProjects()}>
                      <ShieldCheck size={15}/> {admissionBusy ? 'Verifying Founder authority…' : 'Activate Founder Projects through EOS'}
                    </button>}
                    {admissionStatus && <p role="status">{admissionStatus}</p>}
                    {projectError && projectState === 'READY' && <p role="alert">{projectError}</p>}
                    {projectSuccess && <p role="status">{projectSuccess}</p>}
                    {(projectState === 'READY' || projectState === 'UNAVAILABLE') && <details className={styles.strategyCreateDisclosure}>
                      <summary><span><strong>Create another project</strong><small>Separate governed EOS project · does not link to a strategic pillar</small></span></summary>
                      <form className={styles.strategyCreateForm} onSubmit={createStrategyProject} aria-label="Create governed EOS project">
                      <h3>Create a project in EOS</h3>
                      <p>Choose the strategic context for its description. This does not establish a formal strategy relationship or appoint an owner.</p>
                      {projectState === 'UNAVAILABLE' && <p role="status">Your draft remains available to inspect and edit. Project creation is disabled until a fresh EOS Projects read succeeds. Use Refresh projects to reverify source availability.</p>}
                      <label>Strategic pillar context<select value={projectPillar} disabled={projectBusy}
                        onChange={event => { setProjectPillar(event.target.value); setProjectSuccess(''); }}>
                        {STRATEGY_PILLARS.map(pillar => <option key={pillar.section_id} value={pillar.section_id}>{pillar.title}</option>)}
                      </select></label>
                      <label>Project name<input required maxLength={180} value={projectName} disabled={projectBusy}
                        onChange={event => { setProjectName(event.target.value); setProjectSuccess(''); }}/></label>
                      <div className={styles.projectDescriptionHeader}>
                        <strong>Project description</strong>
                        <button type="button" onClick={() => setProjectEditSource(value => !value)} disabled={projectBusy}>
                          {projectEditSource ? 'View formatted description' : 'Edit description'}
                        </button>
                      </div>
                      <p className={styles.projectDescriptionHint}>Formatted live preview of your draft. Headings, lists and emphasis are displayed as readable text; EOS stores the exact submitted description as source.</p>
                      {!projectEditSource && <ProjectDescriptionPreview value={projectDescription}/>}
                      {projectEditSource && <label>Editable description source
                        <textarea maxLength={3700} rows={12} value={projectDescription} disabled={projectBusy}
                          onChange={event => { setProjectDescription(event.target.value); setProjectSuccess(''); }}/>
                      </label>}
                      <div className={styles.projectDescriptionHeader}>
                        <span>{projectDescription.length.toLocaleString()} / 3,700 characters</span>
                        {!projectDescription.trim() && !projectEditSource && <button type="button" onClick={() => setProjectEditSource(true)}>Enter project description</button>}
                      </div>
                      <button type="submit" disabled={projectBusy || projectState !== 'READY' || !projectName.trim()}>
                        {projectBusy ? 'Verifying EOS readback…' : 'Create project in EOS'}
                      </button>
                      </form>
                    </details>}
                  </div>}
                  <button type="button" onClick={onOpenWork}>Open current My Work <ArrowUpRight size={14}/></button>
                </section>}
                {actions.includes('PUBLISH') && <form className={styles.form} aria-label={`Independent ${classification === 'MISSION' ? 'Mission' : 'Strategy'} publication approval`} onSubmit={publish}><h2>Independent approval and publication</h2><p>Your current source permission and a different author are verified again by EOS.</p><label>Approval reference<input required maxLength={500} value={approvalReference} onChange={event => setApprovalReference(event.target.value)}/></label><label>Effective date and time<input required type="datetime-local" value={effectiveFrom} onChange={event => setEffectiveFrom(event.target.value)}/></label><button type="submit" disabled={busy}>{busy ? 'Verifying…' : 'Approve and publish'}</button></form>}
                </>}
              </>}
        </div>
      </div>
      <footer className={styles.footer}><span><Clock3 size={13}/> {loading ? 'Verifying current company document source' : error ? error.kind === 'AUTHENTICATION_REQUIRED' ? 'Company session verification required' : error.kind === 'ACCESS_DENIED' ? 'Document access denied by EOS' : 'Document source not verified' : data ? 'Source verified ' + displayDate(data.as_of) : 'No verified source read'}</span><button type="button" onClick={onClose}>Close document</button></footer>
    </section>
  </div>, window.document.body);
}

// ARTIFACT: CompanyOperatingDocumentViewer.jsx
// VERSION: v2.21.0-ACTIONABLE-ACCOUNTABILITY-FILTERS
// AUTHORITY BOUNDARY: Source-backed content and command presentation only.
// TENANT POSTURE: Exact session/credential scope; transient state discarded on change.
// FAIL-CLOSED POSTURE: No official content or success without source/readback proof.
// FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
// END OF WILSY OS SOVEREIGN ARTIFACT
