/**
 * TITLE: WILSY OS Intelligence Dock and Movable AI Companion
 * VERSION: v4.50.0-EOS-ENCRYPTED-HISTORY-UX
 * AUTHORITY: WILSY OS Core Governance; Python EOS owns all business authority.
 * EPITOME: Keep contextual intelligence alongside the operator's current work,
 * with a movable/minimizable launcher and preserved source-owned AI contracts.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/components/intelligence/WilsyOSIntelligenceDock.jsx
 * COLLABORATION / OWNERSHIP: App authenticated runtime gate, canonical api.js,
 * Legal advisory/deadline adapters and session-only conversation engines.
 * CERTIFICATION / UPDATE DATE: 2026-11-25
 * COMPLIANCE: AGENTS.md; exact-scope fail-closed source evidence.
 * SECURITY / PRIVACY POSTURE: Session-person label never displays account email;
 * no model calls arise from read-only context inspection.
 * TENANT BOUNDARY: Current authenticated tenant and principal only.
 * AUTHORITY BOUNDARY: EOS source/IAM own every permission and work item.
 * FINANCIAL AUTHORITY BOUNDARY: Python EOS retains metering, reconciliation and billing.
 * CHANGELOG: v4.50.0-EOS-ENCRYPTED-HISTORY-UX presents EOS-encrypted saved transcript
 *            state separately from fallback session-only history, supports
 *            explicit authenticated owner deletion with confirmation and
 *            revision validation, and never represents archived model text
 *            as current source-owned EOS work facts.
 * CHANGELOG: v4.49.0-MW-T11-ANSWER-FOCUS places verified EOS task answers at the
 *            focal point of the conversation and moves optional full source
 *            details below the answer. Suppresses duplicated source prompt
 *            and headings after a verified turn; retains independent source
 *            inspection and current access checks without duplicate content.
 * CHANGELOG: v4.48.0-MW-T11-QUIET-CONVERSATIONAL-SOURCE fixes old one-line source replies
 * being formatted as one oversized title; uses calm conversational body
 * text for legacy and structured turns, with a modest task heading and
 * independently labeled facts. Preserves progressive reveal and EOS authority.
 * CHANGELOG: v4.47.0-MW-T11-PROGRESSIVE-VERIFIED-REPLY renders verified task replies as progressive,
 *            structured source transcripts with readable hierarchy, visible
 *            evidence posture, and reduced-motion accessibility. Replayed
 *            history stays instantaneous. No provider or source writes.
 * CHANGELOG: v4.46.0-MW-T11-HISTORY-RECOVERY-UX restores selected current-session turns
 *            to the active conversation panel and visibly distinguishes
 *            session activity from certified EOS durable history.
 * CHANGELOG: v4.45.0-MW-T11-SOURCE-SESSION-HISTORY records independently verified task source
 *            inspections in the existing same-session conversation engine;
 *            labels history as session-only pending a governed EOS durable
 *            route. No model calls, localStorage history or entitlement change.
 * CHANGELOG: v4.44.0-MW-T11-EXPLICIT-TASK-LOOKUP resolves explicit MW-T task inspection through
 * current EOS-authorized complete project-task pages, then independently
 * verified context GET. No provider, billing, IAM or task mutation.
 * CHANGELOG: v4.43.0-MW-T11-TASK-CONTEXT-FIRST opens the existing Dock directly in EOS source
 * context when launched from a selected Projects task. Validates returned
 * task identity and revision against the selected untrusted locator before
 * rendering lifecycle facts; denied/unavailable stays fail-closed. Uses
 * current Python EOS context GET, no paid provider, IAM or new surface.
 * CHANGELOG: v4.34.0-LOCAL-COURTESY-NONMETERED-TURNS supports narrowly allowlisted casual courtesies as explicitly tagged built-in conversation turns, without invoking the OpenAI provider, making quota admissions, or replaying reconciliation-required attempts. Substantive prompts still require verified EOS model execution and usage evidence.
 * CHANGELOG: v4.42.0-BILLING-POS-CERTIFIED-SOURCE-READS registers explicit POS location-authorized commercial count and immutable Billing evidence-by-identity reads. Strictly validates exact source, tenant, principal, counts and financial non-execution claims; does not infer billing balances or POS settlements and never invokes a model for these verified source requests.
 * CHANGELOG: v4.41.0-GOVERNED-MULTIDOMAIN-WORK-SOURCE adds independently authorised multi-domain work intelligence (HR, CRM, Operations, Legal, Intelligence and Projects task queues) using the canonical My Work aggregate and its complete tenant/principal/source-coverage validator. Uses typed read-only plans, no provider calls or omitted-source zeros, keeps business writes and the existing AI replay boundary closed.
 * CHANGELOG: v4.40.0-GOVERNED-COMPOSITE-SOURCE-PLANNING plans multiple safe read-only operations in one Projects source turn from verified conversation context, including 'How many are active and what are details?'. Reuses independently authorised EOS source reads and never sends the combined request to paid inference. Rejects mixed domain, ambiguous and write commands; no IAM or financial changes.
 * CHANGELOG: v4.39.0-VERIFIED-ACTIVE-PROJECT-DETAILS continues a verified Projects status conversation into source-authorised active-project detail, using independent exact-tenant summary, bounded status-filtered list and detail GETs, validating each response; no model request, inferred project data, financial authority, tenant expansion or held-admission changes.
 * CHANGELOG: v4.38.0-SOURCE-GROUNDED-FOLLOWUP-CONTEXT preserves semantic topic continuity only from the previous explicitly verified Projects source reply. A bounded count/status grammar handles natural and imperfect follow-ups (including 'How may are active?') with fresh EOS readback of total/active/planned/on_hold/done/cancelled, not brittle canned answers or paid provider calls. Every read is tenant/principal validated; ungrounded requests retain consented EOS reasoning.
 * CHANGELOG: v4.37.0-SOURCE-VERIFIED-PROJECT-COUNT answers strictly scoped project portfolio count requests from independent exact-tenant/principal EOS Projects summary (GET only), verifying the canonical status-count envelope. No paid reasoning, guessed count, permissions, persistence or reconciliation changes; denial/unavailability remains explicit.
 * CHANGELOG: v4.36.0-LIVE-LOCAL-CLOCK-AND-PROGRESSIVE-TURNS answers strictly bounded current-time requests from the local device clock and reveals newly persisted assistant text progressively with accessible reduced-motion fallbacks. No provider call, EOS admission, IAM expansion, quota bypass, or historical replay.
 * CHANGELOG: v4.35.0-CONTEXTUAL-NONMETERED-COURTESY responds naturally to greetings and tightly scoped day-status acknowledgements after a verified built-in turn (including the previous certified wording) in the same session. No model invocation, quota admission, inferred work, or bypass for substantive prompts.
 * CHANGELOG: v4.33.0-INLINE-CONVERSATIONAL-WORK-ACTIONS converts oversized work-navigation, recovery and contextual follow-ups into accessible inline transcript actions with coherent hierarchy and focus states. The five EOS-authorised CRM tasks remain source-owned; no task mutations, AI charges, changes to admissibility or fabricated records.
 * CHANGELOG: v4.32.0-ONDEMAND-MYWORK-SOURCE-ADMISSION defers the costly cross-source My Work aggregate until a real work-related conversational intent is selected; entering work/overdue initiates a fresh independently admitted read, leaving other Dock surfaces unaffected and avoiding eager concurrent startup load. Scope changes and leaving the view abort/clear local projections; no partial-source/fabricated results.
 * CHANGELOG: v4.31.0-MYWORK-SOURCE-FAILURE-CLASSIFICATION distinguishes exact-tenant My Work IAM refusal, bounded transport timeout, EOS 503 source failure and other transport errors in the chat, without inventing tasks, exposing vendor/request data, extending the client deadline or relaxing backend authority. Kernel health timeout remains an independent optional probe.
 * CHANGELOG: v4.30.1-NATURAL-OVERDUE-WORK-QUERY includes tightly scoped 'Which of my tasks are overdue?' questions in the same read-only EOS work catalog without granting scope or metered access.
 * CHANGELOG: v4.30.0-NATURAL-OUTSTANDING-WORK-INTENT routes bounded natural-language questions about the operator's outstanding/pending/incomplete or overdue work through source-authorized read-only My Work instead of C1B metered reasoning. Questions asking for other people's work, writes or sensitive records remain outside the free local catalog. No release or replay of reconciliation holds.
 * CHANGELOG: v4.29.3-CONTEXT-DEICTIC-INTENT-CERT supports natural local read-only 'inspect this workspace' expression through the same strictly bounded source-intent parser, preserving no-payment/no-write semantics.
 * CHANGELOG: v4.29.2-SOVEREIGN-HEADER-PREFLIGHT places mandatory sovereign boundary declarations in the opening header census; existing authority semantics unchanged.
 * CHANGELOG: v4.29.1-STABLE-COMPOSER-CONTRACT preserves the existing accessible composer placeholder/selector contract while the default conversation, authenticated identity label and no-status-cards interaction change.
 * CHANGELOG: v4.29.0-REAL-CONVERSATION-IDENTITY-RECONCILIATION removes the last permanently rendered quick-action button row, prefers a verified non-email person name (or neutral You) in user turns, and presents provider reconciliation as a distinct pending request in the transcript without claiming completion or retrying metered usage. Retains exact-key replay refusal and authenticated source introspection on natural-language intent.
 * CHANGELOG: v4.28.0-STRICT-READONLY-INTENT-CATALOG registers one strict read-only source-intent catalog for both composer permission gating and execution. Unknown intents never inherit unmetered authority; source views cannot issue a model POST or mutate EOS work; no generated markup or model-supplied action names.
 * CHANGELOG: v4.27.1-CONTEXT-FOCUSED-HEADER removes operational kernel diagnostics as the Dock's hero subtitle while preserving truthful accessible kernel status; the visible header now prioritises current verified workspace and source posture.
 * CHANGELOG: v4.27.0-SOURCE-TURN-CONVERSATION-LEDGER treats explicit local read-only queries as ephemeral user turns followed by verified EOS-source result, not a static header; keeps greeting only on an empty thread, offers contextual follow-ups, and never records a source view as paid model output or persisted assistant history.
 * CHANGELOG: v4.26.1-SAFE-LOCAL-INTENT-COMPOSER keeps the read-only source-intent send affordance independent from metered consent and provider state, while preserving all metered sends' existing reconciliation and usage guards; includes complete bounded My Work rows and explicit intent-selected source expansion.
 * CHANGELOG: v4.26.0-CONTROLLED-CONVERSATIONAL-SOURCE-INTENTS removes default source/status essays from chat and presents one conversational first turn with user-invoked read-only TaskList or SourceInspection. Deterministic exact-intent routing fills only from current EOS-verified sources; no model-generated UI, arbitrary HTML, task mutations or metered POST. Source failures appear within the requested action, not as static opening cards.
 * CHANGELOG: v4.25.1-SESSION-CURRENT-HISTORY-CONTROLS returns to the single conversation on identity/capacity change and new-thread selection, and awaits session-only history clearing and new thread issuance before displaying success; no phantom threads or cross-scope UI state.
 * CHANGELOG: v4.25.0-CONTEXTUAL-ONE-CONVERSATION-WORKFLOW removes generic Suggestions navigation and model-submitting decorative cards, gates Legal Advisory to legal capacity, and adds live exact-tenant My Work focus with read-only details and draft-only contextual question actions. History omits empty placeholder threads. No model calls or inferred task authority.
 * CHANGELOG: v4.24.0-CONVERSATION-FIRST-SOURCE-STREAM moves independently authorised EOS source and My Work projections from fixed stacking panels into the scrollable conversational transcript with progressive disclosure and a fixed composer. Projections remain read-only, not model responses; no new entitlement or IAM truth.
 * CHANGELOG: v4.23.0-VERIFIED-FOUNDER-ACTIVATION-GUARD removes the unsafe subscription-activation fallback on unavailable context, and binds both the displayed action and its command handler to a current source-verified exact-tenant NOT_PROVISIONED state. Source 503 never becomes an entitlement grant or activation offer.
 * CHANGELOG: v4.22.1-READONLY-EXPLICIT-SOURCE-REPROBE bypasses only local synthetic 503 GET backoff for exact read-only My Work and independent kernel health probes, so an explicit Refresh/Recheck reaches EOS rather than repeating a cached synthetic 503; backend IAM/timeout unchanged.
 * CHANGELOG: v4.22.0-EXACT-WORK-SOURCE-DENIAL-RETRY makes read-only Headquarters My Work unavailable/denied states visible and explicitly retriable, without fabricating zero tasks or elevating credentials. Currentness and source permission remain EOS-owned.
 * CHANGELOG: v4.21.0-INDEPENDENT-SOURCE-HEALTH-WORKSPACE-ACTIONS distinguishes a failed optional kernel health probe from independently verified exact-tenant workspace context, offers a real read-only inspect-source action, and replaces generic ready copy with accurate provider/source capability. No model calls, IAM changes or client-origin facts.
 * CHANGELOG: v4.20.0-RECONCILIATION-ATTEMPT-REPLAY-GUARD blocks the exact unresolved reconciliation attempt from manual resubmission while retaining its draft, preserving ordinary uncertain-transport exact-key retry and forbidding fabricated answers or browser quota mutations.
 * CHANGELOG: v4.19.0-RECONCILIATION-CAPACITY-TRANSPARENCY distinguishes confirmed completed usage from held reservations and available quota using EOS source fields, and preserves a reconciliation-required prompt with an explicit do-not-resubmit warning. No reservation state or financial facts are changed in the browser.
 * CHANGELOG: v4.18.0-REASONING-REPLAY-CONFLICT-RECOVERY handles a server-confirmed replay conflict without automatically reissuing an AI request: the original prompt stays editable, and only a separate operator Send generates a new idempotency key. No replay conflict is treated as provider outage.
 * CHANGELOG: v4.17.0-FOUNDER-INSTITUTIONAL-ACTIVATION-ACTION adds
 * one exact-Founder, explicitly clicked Institutional activation command.
 * The Python EOS dual-IAM boundary owns the write; the Dock admits success
 * only after exact-tenant ACTIVE entitlement readback and refreshes context.
 * No automatic login activation, raw Atlas writes, or client-selected tier.
 * v4.16.0-SERVER-GROUNDED-HEADQUARTERS-CONVERSATIONS routes HQ questions
 * through the canonical Python EOS My Work admission flag, sending only a
 * workspace locator and never browser-rendered work facts to a model.
 * v4.15.0-SERVER-PROVIDER-READINESS-PREVIEW displays
 * the safe server-owned provider readiness separately from verified work
 * and entitlement, preventing avoidable model submissions when the Python
 * provider binding is unavailable. v4.14.0-EXPLICIT-AI-COMMERCIAL-READINESS separates EOS-verified work
 * from absent AI commercial capacity, disables only metered model requests
 * when the exact tenant has no AI entitlement and gives bounded guidance.
 * v4.13.1-OPERATOR-READABLE-SOURCE-STATUS replaces raw
 * Kennel machine tokens in the AI header with bounded, truthful human
 * availability language without altering diagnostic or authentication state.
 * v4.13.0-AUTHORIZED-HEADQUARTERS-WORK-FEED projects independently authorized
 * Headquarters My Work priorities as read-only task rows when AI commercial
 * admission is unavailable; tenant/principal and source-owned flags are
 * checked before display. These rows never enter the model from the browser.
 * v4.12.1-QUIET-REMEMBERED-CONSENT keeps previously accepted
 * usage consent collapsed into a discreet, reversible preference instead
 * of presenting the permission prompt again; rejects email values as first
 * names. v4.12.0-PERSONAL-CONVERSATION-AND-SCOPED-CONSENT greets new conversations from the authenticated
 * operator's first name and local time, remembers voluntary consent only
 * for the exact browser/tenant/principal/capacity and disclosure version,
 * and displays failed requests as errors, never fabricated AI turns.
 * v4.11.0-VERIFIED-SELECTED-TASK-FOCUS names the independently verified
 * selected task within the existing conversation context and empty-state
 * explanation, without trusting page-event titles or opening new cards.
 * v4.10.1-INDEPENDENT-AI-CONSENT-DISCLOSURE separates expandable usage
 * information from checkbox label activation, preventing an informational
 * disclosure action from inadvertently consenting to a metered request.
 * v4.10.0-VERIFIED-PROJECT-REASONING-LOCATOR forwards only a server-verified
 * project locator to Python EOS reasoning (never browser project facts), reuses
 * the exact locator on replay, blocks unverified project reasoning and revokes
 * in-flight turns when the observed workspace changes. Consent discloses that
 * EOS may pass verified source excerpts to the authorized model provider.
 * v4.9.1-CONVERSATION-FIRST-CONSENT removes the misleading generic readiness
 * messages, makes the active EOS workspace the conversational starting point,
 * and presents compact consent with an accessible optional disclosure. It
 * preserves metered opt-in and does not claim provider-grounded answers.
 * v4.9.0-VERIFIED-CONTEXT-INSPECTION reads independently admitted
 * workspace context only while open, validates exact scope and source locators,
 * cancels stale reads and exposes source citations and unavailable commercial
 * facts. Collapsible source details retain the mobile composer in view.
 * Inspection does not send source records to a model or issue authority.
 * CHANGELOG: v4.8.2-SESSION-OWNED-REASONING-CANCELLATION cancels obsolete
 * reasoning transport on scope exit and unmount, rejects late work by mount
 * generation, and releases submission state for the newly selected capacity.
 * Cancellation never claims to undo a server admission or quota reservation.
 * CHANGELOG: v4.8.1-EXACT-REPLAY-AI-CONSUMPTION preserves the exact EOS
 * idempotency key and canonical prompt after uncertain AI responses; retries
 * reuse the same admission instead of consuming capacity twice. A confirmed
 * response or changed tenant/session scope clears the replay anchor.
 * CHANGELOG: v4.8.0-ENTITLED-EOS-CONVERSATION sends general conversational
 * turns to the canonical Python EOS metered reasoning boundary only after
 * explicit usage consent. Client history is conversation continuity, not
 * verified workspace evidence. C1C legal authority remains independent.
 * CHANGELOG: v4.7.1-INDEPENDENT-KERNEL-HEALTH starts EOS kernel health independently
 * of optional finance evidence, publishes verified health immediately, and
 * enriches context only after independently verified optional evidence.
 * v4.7.0-MOVABLE-MINIMIZABLE-AI-COMPANION adds a distinct vector AI identity, pointer/keyboard
 * movement, viewport clamping, compact minimization and reset without navigation,
 * source commands, background modal interference or conversation resets.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; accessible controls.
 * SECURITY / PRIVACY POSTURE: Position and size are ephemeral React preferences;
 * no identity, message or layout is written to browser storage by these controls.
 * TENANT BOUNDARY: Existing exact tenant/principal/capacity scope remains owner
 * of all conversation/API state; layout controls never create permission.
 * AUTHORITY BOUNDARY: Companion presentation only; all source requests and
 * late-response guards remain unchanged. No route or workspace switch occurs.
 * FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively.
 */
/**
 * HISTORICAL CHANGELOG
 * Change Log:
 *   2026-11-09 v4.6.1-STALE-OPERATOR-TURN-RENDER-GUARD discards responses, errors,
 *   replies and in-flight UI mutations from a superseded tenant, principal
 *   or business-capacity scope without inventing advisory authority.
 *   2026-11-09 v4.6.0-SESSION-OWNED-OPTIONAL-INTELLIGENCE cancels superseded EOS health probes,
 *   never presents a fabricated LIVE_EMPTY result as verified runtime health,
 *   and revokes transient conversation scope on logout, remount, tenant or
 *   capacity changes. Intelligence availability never gates Headquarters.
 *   2026-10-11 v4.5.0-LEGAL-DEADLINE-INTELLIGENCE-PROJECTION — Added an
 *     explicit-matter, explicit-time Core Legal deadline observation tab backed
 *     by D6B, with no AI, recommendation, reminder, mutation, or finance authority.
 *   2026-09-24 v4.4.1-LEGAL-AUTHORITY-AWARE-ARTIFACT-INTEGRITY — Aligned the sovereign artifact contract with
 *     canonical /kernel health transport, shared-api /ai/operator generic Ask,
 *     C1C legal-role routing, and session-only conversation history.
 *   2026-09-17 v4.4.0-LEGAL-AUTHORITY-AWARE-RUNTIME — Consumed only the
 *     bounded persisted session projection and replaced identity/tenant defaults
 *     with an explicit unresolved posture.
 *   2026-09-17 v4.3.1-C1E-R1D-A1-WILSY-OS-BRAND-CONSOLIDATION — Consolidated
 *     visible product branding to WILSY OS and source-gated secondary tenant identity.
 *   2026-09-17 v4.3.0-C1E-R1C-LEGAL-ADVISORY-PROJECTION — Added explicit
 *     evidence-backed Legal Advisory tab using only certified R1B operations;
 *     no C1E persistence, command affordances, or client-side reinterpretation.
 *   2026-09-13 v4.2.0-M14-P7-BILLING-INTELLIGENCE-EVIDENCE — Added optional
 *     canonical billing-intelligence evidence projection with explicit UTC
 *     snapshot request and explicit operator-context propagation; no client
 *     billing derivation or authorization inference.
 *   2026-08-06 v4.1.1-KENNEL-PHASE4 — Refined History Tab: Integrated New Thread & Sync 
 *     actions using dedicated CSS classes, achieving 10/10 UX parity.
 *   2026-08-06 v4.1.0-KENNEL-PHASE4 — Updated History Tab: Added manual "New Thread" and 
 *     "Sync/Refresh" actions. 
 *   2026-08-04 v4.0.0-KENNEL-PHASE4 — Replaced local buildWilsyOperatorIntelligence
 *     with backend POST /api/ai/operator; removed client engine import.
 *   2026-08-04 v3.1.0-KENNEL-PHASE1-FINAL — Raw fetch removed; api service only.
 *
 */
/* eslint-disable */

import React, { useCallback, useContext, useEffect, useLayoutEffect, useMemo, useRef, useState } from 'react';
import { v4 as uuidv4 } from 'uuid';
import {
  ArrowUpRight,
  ArrowLeft,
  FileSearch,
  ListFilter,
  RefreshCw,
  FileCheck2,
  History,
  MessageSquareText,
  Minimize2,
  PanelRightOpen,
  SendHorizontal,
  ShieldCheck,
  Sparkles,
  GripVertical,
  Minus,
  RotateCcw,
  X,
} from 'lucide-react';
import api from '../../services/api.js'; // Sovereign HTTP client – forensic seals, tenant headers, auto refresh
import { assertUnifiedMyWorkProjection, unifiedMyWorkSourceLabel } from '../../services/unifiedMyWorkProjection.js';
import {
  executeWilsyAILegalServices,
  generateWilsyAILegalNextActions,
  readWilsyAILegalNextAction,
} from '../../services/wilsyAIAdvisoryApi.js';
import { getLegalMatterDeadlineIntelligence } from '../../services/legalMatterDeadlineService.js';
import {
  clearWilsyAIConversationThreads,
  resetWilsyAIConversationSession,
  createWilsyAIConversationThread,
  loadWilsyAIConversationThreads,
  persistWilsyAIConversationTurn,
  deleteWilsyAIConversationThread,
  wilsyAIConversationHistoryPosture,
} from './wilsyAIConversationHistoryEngine.js';
import styles from './WilsyOSIntelligenceDock.module.css';

/**
 * @function classifyWilsyAISourceIntent
 * @description Strict, developer-owned controlled UI catalog. Returns only
 * WORK, OVERDUE, SOURCE or null. No model decides a component, no raw HTML,
 * and no source-inspection choice grants backend permissions or mutates work.
 * Exact-tenant GETs remain independently re-authorised by Python EOS.
 */
function classifyWilsyAISourceIntent(value) {
  const text = String(value || '').trim();
  if (text.length === 0 || text.length > 160) return null;
  if (/^(?:show|list|review|open|view|inspect)\s+(?:(?:my|the|current)\s+)?(?:overdue\s+)?(?:tasks?|work|work\s+queue)(?:\s+(?:items?|queue))?[?.!]?$/i.test(text)) {
    return /\boverdue\b/i.test(text) ? 'OVERDUE' : 'WORK';
  }
  // Narrow natural questions about the signed-in operator's own work.
  // No scope expansion, third-party query or work mutation is ever inferred.
  if (/^(?:what\s+(?:are|is)|which|show\s+me|tell\s+me\s+about)\s+(?:(?:all|the)\s+)?(?:my|mine)\s+(?:(?:currently|still)\s+)?(?:(?:outstanding|open|pending|unfinished|incomplete|overdue)\s+)?(?:work|tasks?|work\s+items?|to-?dos?)(?:\s+(?:items?|remaining|outstanding|pending|overdue|today|right\s+now))?[?.!]?$/i.test(text)) {
    return /\boverdue\b/i.test(text) ? 'OVERDUE' : 'WORK';
  }
  if (/^which\s+of\s+my\s+(?:tasks?|work\s+items?)\s+(?:are|is)\s+(?:outstanding|open|pending|overdue|unfinished)[?.!]?$/i.test(text)) {
    return /\boverdue\b/i.test(text) ? 'OVERDUE' : 'WORK';
  }
  if (/^(?:what\s+(?:work|tasks?)|which\s+(?:work|tasks?))\s+do\s+i\s+(?:have|need\s+to\s+do)(?:\s+(?:outstanding|pending|overdue|today|right\s+now))?[?.!]?$/i.test(text)) {
    return /\boverdue\b/i.test(text) ? 'OVERDUE' : 'WORK';
  }
  if (/^(?:show|inspect|review|open|view)\s+(?:(?:my|the|current|this)\s+)?(?:workspace|project|context|source)(?:\s+(?:details?|context))?[?.!]?$/i.test(text)) {
    return 'SOURCE';
  }
  return null;
}

/**
 * @description Narrow explicit project-task inspection intent, without model inference.
 */
function parseWilsyTaskInspection(value) {
  const match = /^(?:inspect|show|review|open|view)\s+(MW-T\d{1,3})[?.!]?$/i
    .exec(String(value || '').trim());
  return match ? match[1].toUpperCase() : null;
}

/**
 * @description Resolve a unique task from current, complete tenant/principal/
 * project-bound EOS pages. The task locator is subsequently reauthorized by
 * the independent /wilsy-ai/reasoning/context endpoint.
 */
async function resolveWilsyTaskInspection(code, projectId, tenantId, principalId) {
  if (!/^prj-[a-f0-9]{48}$/.test(projectId || '') || !tenantId || !principalId) {
    throw new Error('TASK_SCOPE_REQUIRED');
  }
  const matches = [];
  const seen = new Set();
  let offset = 0;
  for (let page = 0; page < 20; page += 1) {
    const { data } = await api.get(
      '/projects/' + encodeURIComponent(projectId) + '/tasks?limit=50&offset=' + offset,
      { headers: { 'X-Tenant-ID': tenantId }, timeout: 15000 },
    );
    if (data?.schema !== 'WILSY-PROJECT-TASK-LIST/V1'
      || data.tenant_id !== tenantId || data.principal_id !== principalId
      || data.project_id !== projectId || data.limit !== 50 || data.offset !== offset
      || typeof data.has_more !== 'boolean' || !Array.isArray(data.items)
      || data.items.length > 50 || (data.has_more && !data.items.length)
      || data.next_offset !== (data.has_more ? offset + data.items.length : null)) {
      throw new Error('TASK_PAGE_NOT_VERIFIED');
    }
    for (const task of data.items) {
      if (task?.schema !== 'wilsy.project.task.v1'
        || task.tenant_id !== tenantId || task.project_id !== projectId
        || !/^ptk-[a-f0-9]{48}$/.test(task.task_id || '')
        || seen.has(task.task_id) || typeof task.title !== 'string'
        || !Number.isSafeInteger(task.revision) || task.revision < 1
        || !/^[a-f0-9]{128}$/.test(task.fingerprint || '')) {
        throw new Error('TASK_RECORD_NOT_VERIFIED');
      }
      seen.add(task.task_id);
      if (task.title.startsWith(code + ' — ') || task.title.startsWith(code + ' - ')) {
        matches.push(task);
      }
    }
    if (!data.has_more) {
      if (matches.length !== 1) throw new Error('TASK_NOT_UNIQUELY_VERIFIED');
      return { task_id: matches[0].task_id, task_revision: matches[0].revision };
    }
    offset = data.next_offset;
  }
  throw new Error('TASK_PAGINATION_INCOMPLETE');
}

/**
 * @function resolveWilsyLocalCourtesy
 * @description Narrow non-generative conversational etiquette for greetings
 * and acknowledgements. No personal/project/business facts are inferred.
 * Replies are labelled built-in, not model answers, and do not cross EOS IAM,
 * financial or provider boundaries.
 */
function resolveWilsyLocalCourtesy(value, previousTurns = []) {
  const text = String(value || '').trim();
  if (!text || text.length > 120) return null;
  if (/^(?:hi|hello|hey|hey\s+wilsy|hello\s+wilsy|hi\s+wilsy|good\s+(?:morning|afternoon|evening))[!.?\s]*$/i.test(text)) {
    return 'Hello! I’m here and ready to help. What would you like to work on?';
  }
  if (/^(?:(?:hey|hello|hi)[,\s]+)?how\s+(?:(?:are|r)\s+you|(?:is|was)\s+(?:you|your)\s+day|(?:has|have)\s+(?:you|your)\s+day\s+been)[?.!\s]*$/i.test(text)) {
    return 'I’m doing well, thanks for asking. How is your day going?';
  }
  // Day-status replies are nonmetered only when directly answering the
  // canonical built-in question in the same authenticated session thread.
  // No previous provider answer or unrelated user text authorizes this path.
  const previous = Array.isArray(previousTurns) ? previousTurns.at(-1) : null;
  if (previous?.role === 'assistant'
    && previous?.meta?.source === 'WILSY_LOCAL_COURTESY'
    && (previous?.content === 'I’m doing well, thanks for asking. How is your day going?'
      || previous?.content === 'I’m here and ready to help. How is your day going?')) {
    if (/^(?:(?:i(?:'|’)m|i am)\s+)?(?:going\s+)?(?:well|good|great|fine|okay|ok|not bad)(?:,?\s+thanks)?[.!\s]*$/i.test(text)) {
      return 'Glad to hear it! What would you like to work on?';
    }
    if (/^(?:not\s+(?:so\s+)?(?:good|great|well)|(?:having\s+)?a\s+(?:rough|hard)\s+day)[.!\s]*$/i.test(text)) {
      return 'Sorry to hear your day has been difficult. Would you like to tell me what’s going on, or focus on a task?';
    }
  }
  if (/^(?:thanks|thank\s+you|thank\s+you\s+wilsy|much\s+appreciated)[!.\s]*$/i.test(text)) {
    return 'You’re welcome. What would you like to do next?';
  }
  return null;
}

/**
 * @function classifyWilsyProjectPortfolioCountIntent
 * @description Strictly admit a tenant-wide read-only project count question.
 * The actual number comes only from EOS Projects summary with current IAM,
 * never from browser-held project lists, inference, or an untrusted snapshot.
 */
function classifyWilsyProjectPortfolioCountIntent(value, previousTurns = []) {
  const text = String(value || '').trim().toLowerCase()
    .replace(/[?!.;,]+/g, ' ').replace(/\s+/g, ' ').trim();
  if (!text || text.length > 160) return null;

  // The only implicit subject allowed is the immediately previous certified
  // EOS Projects read in this session. The browser does NOT inherit business
  // authority, counts, identity or tenant from a chat transcript.
  const previous = Array.isArray(previousTurns) ? previousTurns.at(-1) : null;
  const verifiedProjectTopic = previous?.role === 'assistant'
    && previous?.meta?.source === 'WILSY_EOS_PROJECT_SUMMARY'
    && previous?.meta?.phase === 'SOURCE_VERIFIED_READ_ONLY'
    && previous?.meta?.domain === 'PROJECTS';
  const explicitProjectTopic = /\bprojects?\b/.test(text);
  if (!explicitProjectTopic && !verifiedProjectTopic) return null;

  // Mixed subjects, requests for records other than the tenant portfolio, and
  // any command or mutation must not inherit the free source-count capability.
  if (/\b(?:employees?|people|users?|clients?|deals?|invoices?|payments?|tasks?|meetings?|staff|revenue|budgets?|delete|edit|change|create|assign|transfer|archive)\b/.test(text)) {
    return null;
  }
  const interrogative = /^(?:how (?:many|may)|number of|count|what(?:'s| is) (?:the |my |our )?(?:total |number of )?|tell me (?:the |my |our )?(?:number of |total )?)/.test(text);
  if (!interrogative) return null;

  const stateWords = [
    ['active', /\bactive\b/],
    ['planned', /\b(?:planned|planning)\b/],
    ['on_hold', /\b(?:on hold|paused)\b/],
    ['done', /\b(?:done|completed|finished)\b/],
    ['cancelled', /\b(?:cancelled|canceled)\b/],
  ];
  const selectedStates = stateWords.filter(([, pattern]) => pattern.test(text));
  if (selectedStates.length > 1) return null;

  if (explicitProjectTopic) {
    // A compact grammatical boundary: do not interpret explanatory, historical,
    // ownership, third-party, conditional or mutation questions as a count.
    if (/\b(?:why|when|who|which|before|after|last|next|tomorrow|yesterday|by|per|each|should|could|would)\b/.test(text)) return null;
    if (!/\b(?:how many|how may|number of|count|total|are there|do i have)\b/.test(text)) return null;
    if (/\b(?:other|another|their|someone|anyone)\b/.test(text)) return null;
    return { status: selectedStates[0]?.[0] || 'total' };
  }

  // A pronoun-only follow-up is admissible ONLY as a short quantity/status
  // question immediately after a verified Projects reply, not an open-ended
  // question about unidentified records.
  if (!selectedStates.length || text.split(' ').length > 8) return null;
  if (!/^(?:how (?:many|may) (?:of (?:them|these|those) )?are |how (?:many|may) (?:of (?:them|these|those) )?|number of |count |what(?:'s| is) (?:the |my |our )?(?:number of )?)/.test(text)) return null;
  const stripped = text.replace(/^(?:how (?:many|may) (?:of (?:them|these|those) )?(?:are )?|number of |count |what(?:'s| is) (?:the |my |our )?(?:number of )?)/, '').trim();
  if (!/^(?:active|planned|planning|on hold|paused|done|completed|finished|cancelled|canceled)(?: (?:ones|projects|are there))?$/.test(stripped)) return null;
  return { status: selectedStates[0][0] };
}

/**
 * @function classifyWilsyActiveProjectDetailIntent
 * @description Read-only detail intent for one current active tenant project.
 * The caller must explicitly mention active Projects, or immediately follow
 * a provenance-marked, source-verified Projects answer in this same thread.
 * No user text or previous assistant turn supplies project authority.
 */
function classifyWilsyActiveProjectDetailIntent(value, previousTurns = []) {
  const text = String(value || '').trim().toLowerCase()
    .replace(/[?!.;,]+/g, ' ').replace(/\s+/g, ' ').trim();
  if (!text || text.length > 180) return false;
  const previous = Array.isArray(previousTurns) ? previousTurns.at(-1) : null;
  const hasProjectTopic = /\bprojects?\b/.test(text)
    || (previous?.role === 'assistant'
      && previous?.meta?.source === 'WILSY_EOS_PROJECT_SUMMARY'
      && previous?.meta?.phase === 'SOURCE_VERIFIED_READ_ONLY'
      && previous?.meta?.domain === 'PROJECTS');
  if (!hasProjectTopic || !/\bactive\b/.test(text)) return false;
  if (/\b(?:employees?|tasks?|invoices?|meetings?|people|clients?|financial|delete|archive|update|change|edit|assign|create|approve|payments?)\b/.test(text)) return false;
  return /^(?:what (?:are|is) (?:the )?details? (?:of|about|for) (?:the |my |our )?active projects?|(?:tell me about|show|give me|describe) (?:the |my |our )?(?:details? (?:of|for) )?active projects?|(?:show|give me) (?:the )?details? (?:of|for) (?:the |my |our )?active projects?)$/.test(text);
}

/**
 * @function planWilsyGovernedReadOnlyQuestion
 * @description Composes a bounded multi-step source-read plan from verified
 * conversation context. This is NOT general LLM parsing or model-generated
 * tool calling: only registered read operations can execute, and each EOS
 * endpoint independently reauthorises the selected tenant and principal.
 *
 * Composition is intentionally separate from source execution, so future
 * read-only business capabilities can register their own schemas, validators,
 * and provenance contracts without creating hundreds of canned replies.
 */
function planWilsyGovernedReadOnlyQuestion(value, previousTurns = []) {
  const text = String(value || '').trim().toLowerCase()
    .replace(/[?!.;,]+/g, ' ').replace(/\s+/g, ' ').trim();
  if (!text || text.length > 220) return null;

  const previous = Array.isArray(previousTurns) ? previousTurns.at(-1) : null;
  const previousVerifiedProjects = previous?.role === 'assistant'
    && ['WILSY_EOS_PROJECT_SUMMARY', 'WILSY_EOS_PROJECT_DETAIL'].includes(previous?.meta?.source)
    && previous?.meta?.phase === 'SOURCE_VERIFIED_READ_ONLY'
    && previous?.meta?.domain === 'PROJECTS';
  if (!previousVerifiedProjects && !/\bprojects?\b/.test(text)) return null;
  // This capability is strictly a read-only, tenant-wide Projects query.
  if (/\b(?:employees?|tasks?|clients?|staff|meetings?|invoices?|payments?|revenue|budgets?|people|delete|change|edit|create|archive|assign|approve|transfer|update|after|before|yesterday|tomorrow)\b/.test(text)) return null;

  const clauses = text.split(/\s+(?:and|&)\s+/);
  if (clauses.length !== 2) return null;

  const count = classifyWilsyProjectPortfolioCountIntent(clauses[0], previousTurns);
  if (count?.status !== 'active') return null;

  // The requested details refer only to the active Projects established by
  // clause one; no entity ID, personal identity or authority is inferred.
  const detailsClause = clauses[1];
  if (!/^(?:(?:what (?:are|is) (?:the )?)|(?:(?:show|give|tell) me (?:the )?))details?(?: (?:of|about|for) (?:the |my |our )?(?:active )?projects?)?$/.test(detailsClause)) {
    return null;
  }
  return Object.freeze({
    domain: 'PROJECTS',
    operations: Object.freeze(['VERIFY_STATUS_COUNTS', 'READ_ACTIVE_LIST', 'READ_PROJECT_DETAIL_IF_UNIQUE']),
    status: 'active',
    includeCount: true,
    includeDetails: true,
  });
}

/**
 * @constant WILSY_READ_ONLY_SOURCE_CAPABILITIES
 * @description Developer-owned, minimum-authority source registry. A tool
 * selects a canonical EOS read, never a browser-trusted business fact or
 * write action; an authenticated endpoint independently enforces every grant.
 */
const WILSY_READ_ONLY_SOURCE_CAPABILITIES = Object.freeze({
  PROJECTS: Object.freeze({ endpoint: '/projects/summary', schema: 'WILSY-PROJECT-SUMMARY/V1' }),
  MY_WORK: Object.freeze({ endpoint: '/my-work', schema: 'WILSY-OS-UNIFIED-MY-WORK/V1' }),
  BILLING_EVIDENCE: Object.freeze({
    endpoint: '/billing/intelligence/verified-evidence/',
    schema: 'WILSY-BILLING-VERIFIED-EVIDENCE-READ/V1',
    source: 'PYTHON_EOS_BILLING_INTELLIGENCE_REGISTRY',
  }),
  POS_LOCATIONS: Object.freeze({ endpoint: '/pos/locations' }),
  POS_COMMERCIAL: Object.freeze({
    endpoint: '/pos/locations/',
    schema: 'WILSY-POS-COMMERCIAL-SUMMARY/V1',
    source: 'PYTHON_EOS_POS_SALE_REGISTRY',
  }),
});

/**
 * @function planWilsyWorkSourceQuestion
 * @description Parse a bounded read-only business-work count into an explicit
 * source selector. This does not imply that the source is entitled: the
 * independently admitted /my-work projection must list it as included.
 * The registered source vocabulary is HR, CRM, OPERATIONS, LEGAL,
 * INTELLIGENCE and PROJECTS; source owner IAM is never granted here.
 */
function planWilsyWorkSourceQuestion(value) {
  const text = String(value || '').trim().toLowerCase()
    .replace(/[?!.;,]+/g, ' ').replace(/\s+/g, ' ').trim();
  if (!text || text.length > 180
    || /\b(?:delete|edit|change|update|create|assign|approve|transfer|complete|payments?|invoices?|users?|other|their|everyone|all employees)\b/.test(text)) return null;
  if (!/^(?:how many|number of|count|what(?:'s| is) (?:the |my |our )?(?:number of |total )?)/.test(text)) return null;
  if (!/\b(?:tasks?|work|work items?|to dos?)\b/.test(text)) return null;
  if (/\b(?:tomorrow|yesterday|last week|next week|by|before|after)\b/.test(text)) return null;

  const selectors = [
    ['HR', /\b(?:hr|hiring|human resources)\b/],
    ['CRM', /\b(?:crm|customer relationship)\b/],
    ['OPERATIONS', /\b(?:operations|operational)\b/],
    ['LEGAL', /\blegal\b/],
    ['INTELLIGENCE', /\bintelligence\b/],
    ['PROJECTS', /\b(?:project|projects)\b/],
  ].filter(([, pattern]) => pattern.test(text));
  if (selectors.length > 3) return null; // bounded multi-domain tool selection
  const overdue = /\b(?:overdue|late)\b/.test(text);
  const activeQualifier = /\b(?:outstanding|open|pending|active|incomplete|unfinished)\b/.test(text);
  if (overdue && activeQualifier) return null;
  // Do not treat a project *portfolio* lifecycle count as a My Work task count.
  if (selectors[0]?.[0] === 'PROJECTS' && !/\b(?:tasks?|work items?|work)\b/.test(text)) return null;
  // Reject any lexical remainder outside the bounded count grammar, including
  // "finished", "belong to someone", financial qualifiers, or arbitrary text.
  const remainder = text
    .replace(/\b(?:human resources|customer relationship|work items?|to dos?)\b/g, ' ')
    .replace(/\b(?:hr|hiring|crm|operations|operational|legal|intelligence|project|projects|tasks?|work|overdue|late|outstanding|open|pending|active|incomplete|unfinished|and)\b/g, ' ')
    .replace(/\s+/g, ' ').trim();
  if (!/^(?:(?:how many|number of|count)(?: do i have| are there| are)?|what(?:'s| is) (?:the |my |our )?(?:number of |total )?(?:do i have|are there)?)$/.test(remainder)) return null;
  return Object.freeze({
    domain: 'MY_WORK',
    capability: WILSY_READ_ONLY_SOURCE_CAPABILITIES.MY_WORK,
    sources: Object.freeze(selectors.map(([source]) => source)),
    overdue,
  });
}

/**
 * @function formatWilsyGovernedMyWorkCount
 * @description Format only an independently validated and admitted EOS result.
 * Absent source is not a verified zero and cannot be exposed as one.
 */
function formatWilsyGovernedMyWorkCount(payload, plan) {
  const included = payload.sources_included;
  const sources = plan.sources;
  if (sources.some(source => !included.includes(source))) {
    return 'I cannot verify a complete work count for the requested departments. One or more sources are not included in your current authorised EOS My Work projection.';
  }
  const count = plan.overdue
    ? sources.length
      ? payload.items.filter(item => sources.includes(item.source) && item.is_overdue === true).length
      : payload.summary.overdue_count
    : sources.length
      ? sources.reduce((total, source) => total + payload.summary.source_counts[source], 0)
      : payload.summary.active_count;
  const names = sources.length
    ? sources.map(source => unifiedMyWorkSourceLabel(source)).join(' and ')
    : 'all admitted work sources';
  const status = plan.overdue ? 'overdue' : 'active';
  return 'EOS verifies ' + count + ' ' + status
    + ' work ' + (count === 1 ? 'item' : 'items')
    + ' for you in ' + names
    + ' under the current tenant and authorised source coverage.';
}

/**
 * @function planWilsyFinancialSourceRead
 * @description Finance source routing is read-only and intentionally narrow.
 * Billing requires an immutable evidence ID (not an unverified live balance).
 * POS requires current sale:read and an independently admitted location.
 */
function planWilsyFinancialSourceRead(value) {
  const text = String(value || '').trim();
  if (!text || text.length > 260) return null;
  const billing = /^(?:show|read|inspect|summarize)\s+(?:my\s+|our\s+|the\s+)?billing\s+(?:intelligence\s+)?evidence\s+([0-9a-f]{128})[?.!\s]*$/i.exec(text);
  if (billing) {
    return Object.freeze({ domain: 'BILLING', evidenceId: billing[1].toLowerCase() });
  }
  if (/^(?:how many|count|what(?:'s| is) (?:the |my |our )?(?:number of )?)\s*(?:pos\s+|point of sale\s+)(?:commercial\s+)?sales\s+(?:do i have|are there|have i recorded)?[?.!\s]*$/i.test(text)
    || /^(?:how many|count)\s+(?:completed\s+)?pos\s+sales(?:\s+do i have)?[?.!\s]*$/i.test(text)) {
    return Object.freeze({ domain: 'POS' });
  }
  return null;
}

function verifyWilsyPOSLocations(payload, tenantId, principalId) {
  if (payload?.tenant_id !== tenantId || payload?.principal_id !== principalId
    || !Array.isArray(payload.locations) || payload.locations.length > 100
    || payload.locations.some(row => !row
      || typeof row.location_id !== 'string' || !row.location_id.trim()
      || row.status !== 'ACTIVE'
      || !Number.isSafeInteger(row.revision) || row.revision < 0)
    || new Set(payload.locations.map(row => row.location_id)).size !== payload.locations.length) {
    throw new Error('WILSY_POS_LOCATION_READ_UNVERIFIED');
  }
  return payload.locations;
}

function verifyWilsyPOSCommercialSummary(payload, tenantId, principalId, locationId) {
  const names = ['DRAFT', 'OPEN', 'COMPLETED_COMMERCIAL', 'VOIDED'];
  const counts = payload?.counts;
  if (payload?.schema !== WILSY_READ_ONLY_SOURCE_CAPABILITIES.POS_COMMERCIAL.schema
    || payload?.tenant_id !== tenantId || payload?.principal_id !== principalId
    || payload?.location_id !== locationId
    || payload?.authority?.source !== WILSY_READ_ONLY_SOURCE_CAPABILITIES.POS_COMMERCIAL.source
    || payload?.authority?.read_only !== true
    || payload?.authority?.model_invoked !== false
    || payload?.authority?.financial_execution !== false
    || payload?.authority?.settlement_not_asserted !== true
    || !counts || !Number.isSafeInteger(counts.total) || counts.total < 0
    || !names.every(key => Number.isSafeInteger(counts[key]) && counts[key] >= 0)
    || names.reduce((total, key) => total + counts[key], 0) !== counts.total) {
    throw new Error('WILSY_POS_COMMERCIAL_SUMMARY_UNVERIFIED');
  }
  return counts;
}

function verifyWilsyBillingEvidenceRead(payload, tenantId, principalId, evidenceId) {
  const evidence = payload?.evidence;
  if (payload?.schema !== WILSY_READ_ONLY_SOURCE_CAPABILITIES.BILLING_EVIDENCE.schema
    || payload?.tenant_id !== tenantId || payload?.principal_id !== principalId
    || payload?.authority?.source !== WILSY_READ_ONLY_SOURCE_CAPABILITIES.BILLING_EVIDENCE.source
    || payload?.authority?.read_only !== true
    || payload?.authority?.model_invoked !== false
    || payload?.authority?.financial_execution !== false
    || payload?.authority?.settlement_not_asserted !== true
    || !evidence || evidence.tenant_id !== tenantId
    || evidence.evidence_identity !== evidenceId
    || !Number.isSafeInteger(evidence.receivable_count) || evidence.receivable_count < 0
    || !Number.isSafeInteger(evidence.receivable_outstanding_amount_minor)
    || evidence.receivable_outstanding_amount_minor < 0
    || !Number.isSafeInteger(evidence.aging_evidence_count) || evidence.aging_evidence_count < 0
    || !Number.isSafeInteger(evidence.dunning_evidence_count) || evidence.dunning_evidence_count < 0
    || typeof evidence.as_of !== 'string'
    || !Number.isFinite(Date.parse(evidence.as_of))) {
    throw new Error('WILSY_BILLING_EVIDENCE_READ_UNVERIFIED');
  }
  return evidence;
}

/**
 * @function verifyWilsyActiveProjectList
 * @description Verify every field used to select a project for further
 * independent EOS authorisation. Never synthesize a project from counts.
 */
function verifyWilsyActiveProjectList(payload, tenantId, principalId, expectedCount) {
  const items = payload?.items;
  if (payload?.schema !== 'WILSY-PROJECT-LIST/V1'
    || payload?.tenant_id !== tenantId || payload?.principal_id !== principalId
    || payload?.limit !== 100 || payload?.offset !== 0
    || payload?.has_more !== false || payload?.next_offset != null
    || !Array.isArray(items) || items.length !== expectedCount
    || items.some(item => !item || item.tenant_id !== tenantId
      || !/^prj-[0-9a-f]{48}$/.test(item.project_id || '')
      || typeof item.name !== 'string' || !item.name.trim()
      || item.status !== 'active' || item.archived_at != null
      || !Number.isSafeInteger(item.revision) || item.revision < 1)
    || new Set(items.map(item => item.project_id)).size !== items.length) {
    throw new Error('WILSY_ACTIVE_PROJECT_LIST_UNVERIFIED');
  }
  return items;
}

/**
 * @function verifyWilsyActiveProjectDetail
 * @description Verify a separately authorised exact-project detail result
 * before deriving display facts. Historical event records must remain
 * complete and scoped; no command, inferred ownership or IAM grant occurs.
 */
function verifyWilsyActiveProjectDetail(payload, tenantId, principalId, projectId) {
  const project = payload?.project;
  if (payload?.schema !== 'WILSY-PROJECT-RESULT/V1'
    || payload?.tenant_id !== tenantId || payload?.principal_id !== principalId
    || payload?.authority?.source !== 'PYTHON_EOS_PROJECT_REGISTRY'
    || payload?.authority?.financial_execution !== false
    || !project || project.tenant_id !== tenantId || project.project_id !== projectId
    || project.status !== 'active' || project.archived_at != null
    || typeof project.name !== 'string' || !project.name.trim()
    || !Number.isSafeInteger(project.revision) || project.revision < 1
    || !Array.isArray(payload.events)
    || payload.events.some(event => !event || event.tenant_id !== tenantId
      || event.project_id !== projectId || typeof event.event_id !== 'string'
      || typeof event.actor_principal_id !== 'string'
      || !Number.isSafeInteger(event.revision)
      || typeof event.occurred_at !== 'string'
      || Number.isNaN(Date.parse(event.occurred_at)))) {
    throw new Error('WILSY_ACTIVE_PROJECT_DETAIL_UNVERIFIED');
  }
  return project;
}

/**
 * @function formatWilsyActiveProjectDetails
 * @description Render only current source-verified project fields. Optional
 * facts omitted by EOS are reported as unassigned/not recorded, never guessed.
 */
function formatWilsyActiveProjectDetails(project) {
  const optionalDate = value => typeof value === 'string'
    && /^\d{4}-\d{2}-\d{2}$/.test(value) ? value : 'Not recorded';
  const summary = typeof project.summary === 'string' && project.summary.trim()
    ? project.summary.trim().slice(0, 1600) : 'No summary recorded';
  return [
    'Here are the verified details of your active project:',
    'Name: ' + project.name.trim(),
    'Status: Active',
    'Summary: ' + summary,
    'Start date: ' + optionalDate(project.start_date),
    'Target date: ' + optionalDate(project.target_date),
  ].join('\n');
}

/**
 * @function verifyWilsyProjectPortfolioSummary
 * @description Accept only a complete current EOS project-count envelope
 * matching both the selected tenant and authenticated principal. A missing
 * status, inconsistent total, or cross-scope response fails closed.
 */
function verifyWilsyProjectPortfolioSummary(payload, tenantId, principalId) {
  const counts = payload?.counts;
  const statuses = ['active', 'planned', 'on_hold', 'done', 'cancelled'];
  if (payload?.schema !== 'WILSY-PROJECT-SUMMARY/V1'
    || payload?.tenant_id !== tenantId
    || payload?.principal_id !== principalId
    || !counts || !Number.isSafeInteger(counts.total) || counts.total < 0
    || !statuses.every((key) => Number.isSafeInteger(counts[key]) && counts[key] >= 0)
    || statuses.reduce((total, key) => total + counts[key], 0) !== counts.total) {
    throw new Error('WILSY_PROJECT_SUMMARY_UNVERIFIED');
  }
  return counts;
}

/**
 * @function resolveWilsyLocalClock
 * @description Answer only current-device-time questions from the browser
 * clock, without inventing EOS source truth or requesting model inference.
 * Other time, schedule, deadline and business questions still require EOS.
 */
function resolveWilsyLocalClock(value, now = new Date()) {
  const text = String(value || '').trim();
  if (!/^(?:what(?:'s| is) the time|what time is it|tell me the (?:current )?time|current time|time now)[?.!\s]*$/i.test(text)) {
    return null;
  }
  if (!(now instanceof Date) || !Number.isFinite(now.getTime())) return null;
  const time = new Intl.DateTimeFormat(undefined, {
    hour: 'numeric', minute: '2-digit', timeZoneName: 'short',
  }).format(now);
  return 'According to your device clock, it’s ' + time + '.';
}

/**
 * @function WilsyProgressiveAssistantText
 * @description Animate only the newest committed response, not provider
 * execution, accounting or previous conversation history. The full text is
 * immediately available to screen readers; reduced motion is instantaneous.
 * Intervals are cancelled on remount, thread switch, and Dock close.
 */
function WilsyProgressiveAssistantText({ content, animate, onComplete, format = 'PLAIN' }) {
  const fullText = String(content || '');
  const [visibleCount, setVisibleCount] = useState(animate ? 0 : fullText.length);
  const onCompleteRef = useRef(onComplete);
  useEffect(() => { onCompleteRef.current = onComplete; }, [onComplete]);

  useEffect(() => {
    const reducedMotion = typeof window === 'undefined'
      || typeof window.matchMedia !== 'function'
      || window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (!animate || reducedMotion || !fullText.length) {
      setVisibleCount(fullText.length);
      if (animate) onCompleteRef.current?.();
      return undefined;
    }
    let shown = 0;
    setVisibleCount(0);
    // 90 paced increments, no fake network stream and no per-letter sluggishness.
    const step = Math.max(1, Math.ceil(fullText.length / 90));
    const timer = window.setInterval(() => {
      shown = Math.min(fullText.length, shown + step);
      setVisibleCount(shown);
      if (shown === fullText.length) {
        window.clearInterval(timer);
        onCompleteRef.current?.();
      }
    }, 19);
    return () => window.clearInterval(timer);
  }, [animate, fullText]);

  const visibleText = fullText.slice(0, visibleCount);
  const formatted = format === 'VERIFIED_TASK' && fullText.includes('\n')
    ? <div className={styles.verifiedReply}>
      {visibleText.split('\n').map((line, index) => {
        if (!line) return null;
        if (index === 0) {
          return <p key={index} className={styles.verifiedReplyTitle}>{line}</p>;
        }
        if (index >= 1 && index <= 3) {
          const split = line.indexOf(': ');
          return <p key={index} className={styles.verifiedReplyFact}>
            <span>{split >= 0 ? line.slice(0, split) : line}</span>
            {split >= 0 && <strong>{line.slice(split + 2)}</strong>}
          </p>;
        }
        return <p key={index} className={styles.verifiedReplyNote}>{line}</p>;
      })}
    </div> : <span className={format === 'VERIFIED_TASK' ? styles.verifiedReplyLegacy : undefined}>{visibleText}</span>;
  return (
    <>
      <span aria-hidden={animate ? 'true' : undefined}>
        {formatted}
        {animate && visibleCount < fullText.length && (
          <span aria-hidden="true" className={styles.replyCursor}>▍</span>
        )}
      </span>
      {animate && <span className={styles.srOnly}>{fullText}</span>}
    </>
  );
}

/**
 * @function classifyWilsyMyWorkReadFailure
 * @description Small allowlist for client-visible source diagnostics.
 * No raw response bodies, tokens, tenant identifiers or stack traces are
 * surfaced. EOS exclusively owns work source admission and transport health.
 */
function classifyWilsyMyWorkReadFailure(error) {
  const status = error?.response?.status;
  if (status === 401 || status === 403) return 'DENIED';
  if (status === 409) return 'STALE';
  if (status === 503) return 'EOS_UNAVAILABLE';
  const errorCode = String(error?.code || '').toUpperCase();
  if (errorCode === 'ECONNABORTED' || errorCode === 'ETIMEDOUT'
    || (typeof error?.message === 'string'
      && /^timeout of [0-9]+ms exceeded$/.test(error.message))) return 'TIMEOUT';
  return 'UNAVAILABLE';
}

/**
 * @function humanizeWilsyAIBackendToken
 * @description Maps kennel/backend tokens to operator-facing copy.
 * @collaboration Designed to make machine tokens human-readable for UI.
 */
function humanizeWilsyAIBackendToken(value = '') {
  const token = String(value || '').trim();
  const dictionary = {
    WILSY_AI_SOVEREIGN_CONTEXT_RESOLVED: 'Workspace intelligence ready',
    DETERMINISTIC_GOVERNANCE_REASONER: 'Live CRM setup guidance',
    EVIDENCE_COMPLETE: 'Checks complete',
    GOVERNANCE_AI_TIER: 'Governance guidance available',
    GOVERNANCE_AI_TIER_AVAILABLE_FOR_PACKAGING: 'Ready for workflow packaging',
    CORE_INTELLIGENCE: 'Core guidance active',
    SOURCE_REGISTRY_HEALTH_GET_CONTEXT_BRIDGE: 'Live workspace context',
    OPERATIONAL: 'Kennel operational',
  };
  if (dictionary[token]) return dictionary[token];
  if (!token) return '';
  return token
    .replace(/^WILSY_AI_/, '')
    .replace(/_/g, ' ')
    .toLowerCase()
    .replace(/\b\w/g, (l) => l.toUpperCase());
}

/**
 * @function buildWilsyAIProductivityCopy
 * @description Normalises kennel / registry payloads for dock UI.
 * @institutional Preserves a truthful LIVE_EMPTY posture when the source registry is silent.
 */
function buildWilsyAIProductivityCopy(payload = {}) {
  if (!payload || typeof payload !== 'object') {
    return {
      result: 'LIVE_EMPTY',
      workspace: { operatingRole: 'UNRESOLVED', focus: 'UNRESOLVED' },
    };
  }
  const nextBestActions = Array.isArray(payload.nextBestActions)
    ? payload.nextBestActions.map((action) => ({
        ...action,
        title:
          action.rank === 1
            ? 'Review setup authority'
            : action.rank === 2
              ? 'Prepare release checklist'
              : action.title || 'Inspect setup queue',
        description:
          action.rank === 1
            ? 'Check role power, staged review proof, approval state, and release readiness before moving the setup forward.'
            : action.rank === 2
              ? 'Draft the evidence checklist needed before any release command is used.'
              : action.description || 'Check stale setup work and missing receipts before continuing.',
        billingTierSignal: humanizeWilsyAIBackendToken(action.billingTierSignal),
        evidenceStatus: humanizeWilsyAIBackendToken(action.evidenceStatus),
      }))
    : [];

  return {
    ...payload,
    result: humanizeWilsyAIBackendToken(payload.result || payload.status) || 'LIVE_EMPTY',
    bridge: humanizeWilsyAIBackendToken(payload.bridge),
    workspace: {
      ...(payload.workspace || {}),
      focus: payload.workspace?.focus || 'UNRESOLVED',
      operatingRole: payload.workspace?.operatingRole || 'UNRESOLVED',
      monetizationSignal: humanizeWilsyAIBackendToken(payload.workspace?.monetizationSignal),
    },
    modelRoute: {
      ...(payload.modelRoute || {}),
      selectedRoute: humanizeWilsyAIBackendToken(payload.modelRoute?.selectedRoute),
    },
    evidencePosture: {
      ...(payload.evidencePosture || {}),
      status: humanizeWilsyAIBackendToken(payload.evidencePosture?.status),
    },
    billingEntitlement: {
      ...(payload.billingEntitlement || {}),
      tier: humanizeWilsyAIBackendToken(payload.billingEntitlement?.tier),
      requiredTierSignal: humanizeWilsyAIBackendToken(payload.billingEntitlement?.requiredTierSignal),
      upgradeSignal: humanizeWilsyAIBackendToken(payload.billingEntitlement?.upgradeSignal),
    },
    nextBestActions,
    kennel: payload.kennel || payload.system || null,
    uiCopy: {
      statusTitle: 'Workspace status',
      statusSummary: 'Live setup guidance is ready for this workspace.',
      lensTitle: 'Operating lens',
      nextMoveTitle: 'Recommended next step',
      coverageTitle: 'AI coverage',
    },
  };
}

/**
 * @function formatLegalAdvisoryError
 * @description Maps bounded C1C/C1E transport failures to truthful operator copy.
 * @institutional Prevents failed, stale, or unauthorized requests from becoming
 * fabricated recommendations while retaining server-owned conflict classes.
 */
function formatLegalAdvisoryError(error) {
  const status = error?.response?.status ?? error?.status;
  const detail = error?.response?.data?.detail ?? error?.response?.data?.error;
  const code = String(detail || error?.code || '').toUpperCase();
  if (!status && !code) return 'Legal advisory source unavailable; no advisory was generated.';
  if (status === 403 || code === 'C1E_LEGAL_ACCESS_DENIED') {
    return 'Current legal advisory authority denied for this workspace.';
  }
  if (status === 404 || code === 'C1E_RESOURCE_NOT_FOUND') {
    return 'Requested legal advisory source or advisory is unavailable.';
  }
  if (status === 409 && code === 'C1E_TOOL_ASSISTED_REQUIRED') {
    return 'Evidence-backed advisory not generated: tool-assisted orchestration is required.';
  }
  if (status === 409 && code === 'C1E_SOURCE_SNAPSHOT_STALE') {
    return 'Source snapshot is stale; no advisory was created from stale evidence.';
  }
  if (status === 409) return 'Advisory conflict; no fabricated result was returned.';
  if (status === 422) return 'Legal advisory request contract rejected.';
  if (status === 503 && code === 'C1E_ADVISORY_RECONCILIATION_REQUIRED') {
    return 'Advisory state requires reconciliation; success cannot be claimed.';
  }
  if (status === 503) return 'Legal advisory service unavailable; no advisory was generated.';
  return 'Legal advisory source unavailable; no advisory was generated.';
}

/**
 * @function formatAdvisoryValue
 * @description Performs presentation-only formatting without deriving C1E meaning.
 */
function formatAdvisoryValue(value) {
  if (value === null || value === undefined || value === '') return 'Not supplied';
  if (typeof value === 'object') return JSON.stringify(value);
  return String(value);
}

/**
 * @function formatConfidenceScore
 * @description Displays the server-provided confidence score without recomputation.
 */
function formatConfidenceScore(value) {
  if (typeof value !== 'number') return formatAdvisoryValue(value);
  return `${(value <= 1 ? value * 100 : value).toFixed(1)}%`;
}

/**
 * @function resolveAuthoritativeTenantBrand
 * @description Resolves an optional organization label only from explicit active
 * tenant-context authority; email, role, and MASTER fallbacks are excluded.
 * @param {unknown} tenant - Browser-provided active tenant context.
 * @returns {string} Proven organization/legal name or an empty string.
 * @institutional Keeps WILSY OS as the product brand while preventing invented tenant identity.
 */
function resolveAuthoritativeTenantBrand(tenant) {
  if (!tenant || typeof tenant !== 'object') return '';
  const authority = String(
    tenant.source || tenant.authority_source || tenant.context_source || tenant.authority || ''
  ).toUpperCase();
  if (authority !== 'ACTIVE_TENANT_CONTEXT') return '';
  return String(
    tenant.legalName ||
    tenant.companyName ||
    tenant.organization?.legalName ||
    tenant.organization?.legal_name ||
    tenant.name ||
    ''
  ).trim();
}

const normalizeDockRole = (role) => String(role || '').trim().toUpperCase();

const isLegalDockRole = (role) => {
  const token = normalizeDockRole(role);
  return (
    token.startsWith('LEGAL_')
    || token.startsWith('TENANT_LEGAL_')
    || token === 'SHERIFF'
    || token === 'DEPUTY'
    || token === 'TENANT_SHERIFF'
    || token === 'TENANT_DEPUTY'
  );
};

const canProbeBillingIntelligence = (role) => (
  ['LEGAL_FINANCE', 'TENANT_LEGAL_FINANCE'].includes(normalizeDockRole(role))
);


/**
 * @function WilsyOSIntelligenceDock
 * @description Renders session-scoped conversation over the existing EOS authorities.
 * @collaboration Authenticated runtime, api.js and transient conversation engine.
 * @institutional Browser scope partitions presentation; EOS independently admits every command.
 * @returns {React.ReactElement} Accessible, movable conversation companion.
 * No IAM, workforce, commercial or financial authority is created.
 */
const AI_CONSENT_VERSION = 'WILSY-AI-USAGE-DISCLOSURE/V1';

/** Use authenticated display identity and local presentation time only. */
function operatorGreeting(user, hour = new Date().getHours()) {
  const raw = [user?.firstName, user?.first_name, user?.displayName, user?.name]
    .find(value => typeof value === 'string' && value.trim() && !value.includes('@'));
  const first = raw?.trim().split(/\s+/u)[0]?.replace(/[^\p{L}\p{M}'-]/gu, '').slice(0, 48);
  const period = hour < 12 ? 'morning' : hour < 17 ? 'afternoon' : 'evening';
  return `Good ${period}${first ? `, ${first}` : ''}.`;
}

/** Browser preference only: never an entitlement or authorized usage admission. */
function consentKeyFor(user, tenant, scope) {
  if (typeof user?.id !== 'string' || !user.id.trim()
    || typeof tenant !== 'string' || !tenant.trim()) return null;
  return 'wilsy.ai.usage-consent:' + JSON.stringify([
    AI_CONSENT_VERSION, tenant, user.id, scope,
  ]);
}

export function WilsyOSIntelligenceDock({
  authUser = null,
  activeTenant = null,
}) {
  const [isOpen, setIsOpen] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);
  const [launcherMinimized, setLauncherMinimized] = useState(false);
  const [dockPosition, setDockPosition] = useState(null);
  const [dragging, setDragging] = useState(false);
  const [positionNotice, setPositionNotice] = useState('');
  const dockContainerRef = useRef(null);
  const dragRef = useRef(null);
  const companionPanelRef = useRef(null);
  const launcherButtonRef = useRef(null);
  const wasOpenRef = useRef(false);
  useEffect(() => {
    if (isOpen) companionPanelRef.current?.focus({ preventScroll: true });
    else if (wasOpenRef.current) launcherButtonRef.current?.focus({ preventScroll: true });
    wasOpenRef.current = isOpen;
  }, [isOpen]);

  // Geometry is a transient preference, never business or identity state.
  const clampDockPosition = useCallback((x, y) => {
    const bounds = dockContainerRef.current?.getBoundingClientRect();
    const width = bounds?.width || 44; const height = bounds?.height || 44;
    const top = Math.min(84, Math.max(12, window.innerHeight - height - 12));
    return { x: Math.max(12, Math.min(x, window.innerWidth - width - 12)),
      y: Math.max(top, Math.min(y, window.innerHeight - height - 12)) };
  }, []);
  useLayoutEffect(() => {
    const keepVisible = () => setDockPosition(current => current
      ? clampDockPosition(current.x, current.y) : current);
    keepVisible(); window.addEventListener('resize', keepVisible);
    return () => window.removeEventListener('resize', keepVisible);
  }, [isOpen, isExpanded, launcherMinimized, clampDockPosition]);
  const beginDockMove = event => {
    if (event.button !== 0) return;
    event.preventDefault(); event.stopPropagation();
    const bounds = dockContainerRef.current.getBoundingClientRect();
    dragRef.current = { id: event.pointerId, x: event.clientX, y: event.clientY,
      left: bounds.left, top: bounds.top };
    event.currentTarget.setPointerCapture?.(event.pointerId); setDragging(true);
  };
  const moveDock = event => {
    const start = dragRef.current;
    if (!start || start.id !== event.pointerId) return;
    event.preventDefault(); event.stopPropagation();
    setDockPosition(clampDockPosition(start.left + event.clientX - start.x,
      start.top + event.clientY - start.y));
  };
  const endDockMove = event => {
    if (!dragRef.current || dragRef.current.id !== event.pointerId) return;
    dragRef.current = null; setDragging(false);
    if (event.currentTarget.hasPointerCapture?.(event.pointerId)) event.currentTarget.releasePointerCapture?.(event.pointerId);
    setPositionNotice('AI companion moved. Your workspace is unchanged.');
  };
  const moveDockWithKeyboard = event => {
    if (event.key === 'Home') { event.preventDefault(); setDockPosition(null); setPositionNotice('AI companion position reset.'); return; }
    const deltas = { ArrowLeft: [-1, 0], ArrowRight: [1, 0], ArrowUp: [0, -1], ArrowDown: [0, 1] };
    if (!deltas[event.key]) return;
    event.preventDefault(); event.stopPropagation();
    const bounds = dockContainerRef.current.getBoundingClientRect();
    const step = event.shiftKey ? 48 : 16; const [x, y] = deltas[event.key];
    setDockPosition(clampDockPosition(bounds.left + x * step, bounds.top + y * step));
    setPositionNotice('AI companion moved. Use Home to reset.');
  };
  const moveHandle = <button type="button" className={styles.moveHandle}
    title="Drag to move · arrow keys to adjust · Home to reset" aria-label="Move WILSY OS AI"
    onPointerDown={beginDockMove} onPointerMove={moveDock} onPointerUp={endDockMove}
    onPointerCancel={endDockMove} onKeyDown={moveDockWithKeyboard}><GripVertical size={16}/></button>;
  const [activeTab, setActiveTab] = useState('chat');
  const [prompt, setPrompt] = useState('');
  const [reasoningUsageConsent, setReasoningUsageConsent] = useState(false);
  const [workLocator, setWorkLocator] = useState({ workspace: 'HEADQUARTERS' });
  const [verifiedWorkspaceContext, setVerifiedWorkspaceContext] = useState(null);
  const workspaceDetailsRef = useRef(null);
  const [headquartersWork, setHeadquartersWork] = useState(null);
  const [focusedWorkIndex, setFocusedWorkIndex] = useState(null);
  const [conversationView, setConversationView] = useState('WELCOME');
  const [localSourceQuery, setLocalSourceQuery] = useState('');
  const [contextRefresh, setContextRefresh] = useState(0);
  const [founderActivationState, setFounderActivationState] = useState('IDLE');
  const [founderActivationMessage, setFounderActivationMessage] = useState('');
  const founderActivationKeyRef = useRef(null);
  const founderActivationInFlightRef = useRef(false);
  const workLocatorKey = JSON.stringify(workLocator);
  const reasoningReplayRef = useRef({ scope: '', text: '', prompt: '', key: '' });
  const reasoningAbortRef = useRef(null);
  const workLocatorKeyRef = useRef(workLocatorKey);
  const conversationGenerationRef = useRef(0);
  const sendLockRef = useRef(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [conversationThreads, setConversationThreads] = useState([]);
  const [historyOperationError, setHistoryOperationError] = useState('');
  const recordedSourceReadRef = useRef('');
  const [activeThreadId, setActiveThreadId] = useState(null);
  const [animatedAssistantKey, setAnimatedAssistantKey] = useState(null);
  const [dockContext, setDockContext] = useState(null);
  const [kennelPosture, setKennelPosture] = useState('STANDBY');
  const [errorMessage, setErrorMessage] = useState('');
  const [legalPrompt, setLegalPrompt] = useState('');
  const [legalSubmitting, setLegalSubmitting] = useState(false);
  const [legalRefreshing, setLegalRefreshing] = useState(false);
  const [legalError, setLegalError] = useState('');
  const [legalServiceResponse, setLegalServiceResponse] = useState(null);
  const [legalAdvisory, setLegalAdvisory] = useState(null);
  const [deadlineMatterId, setDeadlineMatterId] = useState('');
  const [deadlineIntelligence, setDeadlineIntelligence] = useState(null);
  const [deadlineLoading, setDeadlineLoading] = useState(false);
  const [deadlineError, setDeadlineError] = useState('');
  const messagesEndRef = useRef(null);
  const messagesScrollRef = useRef(null);
  const latestVerifiedReplyRef = useRef(null);
  const healthAbortRef = useRef(null);
  const healthGenerationRef = useRef(0);
  const dockScope = [
    authUser?.id, authUser?.tenantId,
    activeTenant?.tenantId || activeTenant?._id, authUser?.workspaceId,
    authUser?.businessRole || authUser?.role,
    authUser?.membershipRevision, authUser?.businessRoleRevision,
  ].map((part) => String(part ?? '')).join(':');
  const dockScopeRef = useRef(dockScope);
  const consentKey = consentKeyFor(authUser,
    activeTenant?.tenantId || activeTenant?._id || authUser?.tenantId, dockScope);
  const consentKeyRef = useRef(consentKey);
  consentKeyRef.current = consentKey;
  const updateUsageConsent = useCallback(accepted => {
    const key = consentKeyRef.current;
    if (key) {
      try {
        if (accepted) window.localStorage.setItem(key, 'accepted');
        else window.localStorage.removeItem(key);
      } catch {
        // Browser storage is optional. EOS reauthorizes every reasoning call.
      }
    }
    setReasoningUsageConsent(accepted);
  }, []);

  // This module-level session history belongs to the current authenticated
  // capacity only. Changing identity, tenant or capacity revokes old turns and
  // aborts obsolete health probes before they can repaint the next workspace.
  useLayoutEffect(() => {
    conversationGenerationRef.current += 1;
    dockScopeRef.current = dockScope;
    reasoningAbortRef.current?.abort();
    reasoningAbortRef.current = null;
    sendLockRef.current = false;
    setIsSubmitting(false);
    setPrompt('');
    setErrorMessage('');
    setActiveTab('chat');
    setWorkLocator({ workspace: 'HEADQUARTERS' });
    setVerifiedWorkspaceContext(null);
    setHeadquartersWork(null);
    setFocusedWorkIndex(null);
    setConversationView('WELCOME');
    setLocalSourceQuery('');
    setFounderActivationState('IDLE');
    setFounderActivationMessage('');
    founderActivationKeyRef.current = null;
    founderActivationInFlightRef.current = false;
    resetWilsyAIConversationSession();
    setConversationThreads([]);
    setHistoryOperationError('');
    setActiveThreadId(null);
    let rememberedConsent = false;
    if (consentKey) {
      try {
        rememberedConsent = window.localStorage.getItem(consentKey) === 'accepted';
      } catch {
        rememberedConsent = false;
      }
    }
    setReasoningUsageConsent(rememberedConsent);
    reasoningReplayRef.current = { scope: '', text: '', prompt: '', key: '' };
    setDockContext(null);
    setKennelPosture('STANDBY');
    return () => {
      conversationGenerationRef.current += 1;
      reasoningAbortRef.current?.abort();
      healthAbortRef.current?.abort();
      healthGenerationRef.current += 1;
      resetWilsyAIConversationSession();
    };
  }, [dockScope, consentKey]);

  useLayoutEffect(() => {
    if (workLocatorKeyRef.current === workLocatorKey) return;
    workLocatorKeyRef.current = workLocatorKey;
    conversationGenerationRef.current += 1;
    reasoningAbortRef.current?.abort();
    reasoningAbortRef.current = null;
    sendLockRef.current = false;
    reasoningReplayRef.current = { scope: '', text: '', prompt: '', key: '' };
    setIsSubmitting(false);
    setErrorMessage('');
  }, [workLocatorKey]);

  // Navigation events are untrusted locators. No profile, permission, seat,
  // project title or other source fact is accepted from browser events.
  useEffect(() => {
    const receive = event => {
      const detail = event.detail;
      const exactTenant = activeTenant?.tenantId || activeTenant?._id || authUser?.tenantId;
      if (!authUser?.id || detail?.tenantId !== exactTenant || detail?.principalId !== authUser.id) return;
      const candidate = detail.locator;
      const allowed = ['workspace', 'project_id', 'project_revision', 'task_id', 'task_revision', 'participant_view'];
      if (!candidate || typeof candidate !== 'object' || Array.isArray(candidate)
        || Object.keys(candidate).some(key => !allowed.includes(key))
        || !['HEADQUARTERS', 'PROJECTS'].includes(candidate.workspace)
        || (candidate.project_id && (!/^prj-[0-9a-f]{48}$/.test(candidate.project_id)
          || candidate.workspace !== 'PROJECTS'))
        || (candidate.project_revision !== undefined && (!candidate.project_id
          || !Number.isSafeInteger(candidate.project_revision) || candidate.project_revision < 1))
        || (candidate.task_id && (!candidate.project_id || !/^ptk-[0-9a-f]{48}$/.test(candidate.task_id)))
        || (candidate.task_revision !== undefined && (!candidate.task_id
          || !Number.isSafeInteger(candidate.task_revision) || candidate.task_revision < 1))
        || (candidate.participant_view !== undefined && typeof candidate.participant_view !== 'boolean')) return;
      setWorkLocator(previous => JSON.stringify(previous) === JSON.stringify(candidate) ? previous : { ...candidate });
    };
    window.addEventListener('wilsy:ai-context-locator', receive);
    window.dispatchEvent(new CustomEvent('wilsy:ai-context-request'));
    return () => window.removeEventListener('wilsy:ai-context-locator', receive);
  }, [dockScope]);

  useEffect(() => {
    const exactTenant = activeTenant?.tenantId || activeTenant?._id || authUser?.tenantId;
    if (!isOpen || !authUser?.id || !exactTenant || isLegalDockRole(authUser?.role)) {
      setVerifiedWorkspaceContext(null);
      return undefined;
    }
    const controller = new AbortController();
    let current = true;
    const base = { scope: dockScope, locatorKey: workLocatorKey };
    setVerifiedWorkspaceContext({ ...base, state: 'LOADING' });
    api.get('/wilsy-ai/reasoning/context', {
      params: workLocator, headers: { 'X-Tenant-ID': exactTenant },
      signal: controller.signal, timeout: 15000, forceNetworkRetry: true,
    }).then(response => {
      if (!current || controller.signal.aborted || dockScopeRef.current !== dockScope) return;
      const data = response?.data;
      if (data?.schema !== 'WILSY-AI-VERIFIED-CONTEXT/V1'
        || data.tenant_id !== exactTenant || data.principal_id !== authUser.id
        || data.authority?.source !== 'PYTHON_EOS' || data.authority?.read_only !== true
        || data.authority?.model_invoked !== false || data.authority?.financial_execution !== false
        || !/^[0-9a-f]{128}$/.test(data.context_fingerprint || '')
        || !Number.isFinite(Date.parse(data.observed_at))
        || data.locator?.workspace !== workLocator.workspace
        || (data.locator?.project_id || null) !== (workLocator.project_id || null)
        || (data.locator?.task_id || null) !== (workLocator.task_id || null)
        || (workLocator.task_id && (
          data.work?.selected_task?.task_id !== workLocator.task_id
          || (workLocator.task_revision
            && data.work.selected_task.revision !== workLocator.task_revision)
        ))
        || (workLocator.project_id && data.work?.project?.project_id !== workLocator.project_id)
        || (workLocator.project_revision && data.work?.project?.revision !== workLocator.project_revision)
        || !Number.isSafeInteger(data.allowance?.available_request_units)
        || data.allowance.available_request_units < 0) throw new Error('WILSY_AI_CONTEXT_RESPONSE_INVALID');
      setVerifiedWorkspaceContext({ ...base, state: 'READY', data });
    }).catch(error => {
      if (!current || controller.signal.aborted || dockScopeRef.current !== dockScope) return;
      const status = error?.response?.status;
      setVerifiedWorkspaceContext({ ...base,
        state: status === 401 || status === 403 ? 'DENIED' : status === 409 ? 'STALE' : 'UNAVAILABLE' });
    });
    return () => { current = false; controller.abort(); };
  }, [isOpen, dockScope, workLocatorKey, contextRefresh]);

  const workInspectionRequested = conversationView === 'WORK' || conversationView === 'OVERDUE';

  // Read-only EOS My Work is independently authorized from AI commercial
  // entitlement. It is a UI projection only; never forwarded to a model as
  // client-provided fact or used to authorize workflow commands.
  useEffect(() => {
    const exactTenant = activeTenant?.tenantId || activeTenant?._id || authUser?.tenantId;
    if (!isOpen || !authUser?.id || !exactTenant
      || workLocator.workspace !== 'HEADQUARTERS' || !workInspectionRequested) {
      setHeadquartersWork(null);
      return undefined;
    }
    const controller = new AbortController();
    let live = true;
    const scope = dockScope;
    setHeadquartersWork({ scope, state: 'LOADING' });
    api.get('/my-work', {
      headers: { 'X-Tenant-ID': exactTenant },
      signal: controller.signal,
      timeout: 15000,
      forceNetworkRetry: true,
    }).then(response => {
      if (!live || controller.signal.aborted || dockScopeRef.current !== scope) return;
      const data = response?.data;
      if (!data || data.tenant_id !== exactTenant || data.principal_id !== authUser.id
        || !Array.isArray(data.items)
        || !data.summary || !Number.isSafeInteger(data.summary.active_count)
        || !Number.isSafeInteger(data.summary.overdue_count)
        || data.authority?.commands_owned_by !== 'SOURCE_SERVICES'
        || data.authority?.permits_completion !== false
        || data.authority?.permits_approval !== false) {
        setHeadquartersWork({ scope, state: 'UNAVAILABLE' });
        return;
      }
      const items = data.items.slice(0, 25).map(item => ({
        title: typeof item.title === 'string' ? item.title.slice(0, 180) : '',
        source: typeof item.source === 'string' ? item.source.slice(0, 32) : '',
        overdue: item.is_overdue === true,
      })).filter(item => item.title && item.source);
      setHeadquartersWork({ scope, state: 'READY', items,
        activeCount: data.summary.active_count,
        overdueCount: data.summary.overdue_count });
    }).catch(error => {
      if (live && !controller.signal.aborted && dockScopeRef.current === scope) {
        const state = classifyWilsyMyWorkReadFailure(error);
        setHeadquartersWork({ scope, state });
        if (import.meta.env.DEV) {
          console.info('[IntelligenceDock] My Work source check', {
            outcome: state,
            http_status: Number.isInteger(error?.response?.status)
              ? error.response.status : 'NO_HTTP_RESPONSE',
          });
        }
      }
    });
    return () => { live = false; controller.abort(); };
  }, [isOpen, dockScope, workLocatorKey, contextRefresh, workInspectionRequested]);

  useEffect(() => {
    setFocusedWorkIndex(null);
  }, [dockScope, workLocatorKey, contextRefresh]);

  const aiProviderUnavailable = verifiedWorkspaceContext?.scope === dockScope
    && verifiedWorkspaceContext?.locatorKey === workLocatorKey
    && verifiedWorkspaceContext?.state === 'READY'
    && verifiedWorkspaceContext.data?.authority?.provider_binding === 'UNAVAILABLE';
  const aiEntitlementNotProvisioned = verifiedWorkspaceContext?.scope === dockScope
    && verifiedWorkspaceContext?.locatorKey === workLocatorKey
    && verifiedWorkspaceContext?.state === 'READY'
    && verifiedWorkspaceContext.data?.allowance?.state === 'NOT_PROVISIONED';
  const visibleWorkspaceContext = verifiedWorkspaceContext?.scope === dockScope
    && verifiedWorkspaceContext?.locatorKey === workLocatorKey ? verifiedWorkspaceContext : null;
  const currentTenantForAI = activeTenant?.tenantId || activeTenant?._id || authUser?.tenantId;
  const founderActivationEligible = Boolean(
    authUser?.id
    && currentTenantForAI === 'WILSYTENANT-4CD2FZ4O'
    && !isLegalDockRole(authUser?.role)
    && founderActivationState !== 'ACTIVE'
    && aiEntitlementNotProvisioned
    && visibleWorkspaceContext?.data?.tenant_id === currentTenantForAI
    && visibleWorkspaceContext?.data?.principal_id === authUser.id
    && visibleWorkspaceContext?.data?.authority?.source === 'PYTHON_EOS'
  );
  const activateFounderInstitutional = useCallback(async () => {
    const tenant = activeTenant?.tenantId || activeTenant?._id || authUser?.tenantId;
    if (founderActivationInFlightRef.current
      || !founderActivationEligible
      || !authUser?.id || tenant !== 'WILSYTENANT-4CD2FZ4O'
      || isLegalDockRole(authUser?.role)
      || verifiedWorkspaceContext?.scope !== dockScope
      || verifiedWorkspaceContext?.locatorKey !== workLocatorKey
      || verifiedWorkspaceContext?.state !== 'READY'
      || verifiedWorkspaceContext?.data?.tenant_id !== tenant
      || verifiedWorkspaceContext?.data?.principal_id !== authUser.id
      || verifiedWorkspaceContext?.data?.allowance?.state !== 'NOT_PROVISIONED') return;
    founderActivationInFlightRef.current = true;
    const scope = dockScope;
    const key = founderActivationKeyRef.current
      || `founder-institutional-${uuidv4()}`;
    founderActivationKeyRef.current = key;
    setFounderActivationState('SUBMITTING');
    setFounderActivationMessage('Verifying Institutional AI commercial authority…');
    try {
      const response = await api.post(
        '/subscriptions/founder-ai-institutional/activate', {},
        { headers: { 'X-Tenant-ID': tenant, 'X-Idempotency-Key': key },
          timeout: 30000 },
      );
      if (dockScopeRef.current !== scope) return;
      const result = response?.data?.data || response?.data;
      if (result?.tenant_id !== tenant
        || result?.subscription_id !== 'WILSYSUB-93455E4E'
        || result?.feature_id !== 'ai.wilsy.institutional'
        || result?.entitlement_state !== 'ACTIVE'
        || result?.source_verified !== true
        || result?.zero_rated_subscription !== true) {
        throw new Error('FOUNDER_AI_ACTIVATION_READBACK_INVALID');
      }
      setFounderActivationState('ACTIVE');
      setFounderActivationMessage(
        'Institutional AI entitlement is active. Verifying provider and workspace context…',
      );
      setContextRefresh(value => value + 1);
    } catch (error) {
      if (dockScopeRef.current !== scope) return;
      const status = error?.response?.status;
      setFounderActivationState('ERROR');
      setFounderActivationMessage(status === 401 || status === 403
        ? 'EOS requires current Founder plan and subscription management authority.'
        : status === 409
          ? 'Commercial records changed. Refresh the source before retrying.'
          : 'EOS could not verify ACTIVE Institutional AI. No activation is being claimed.');
    } finally {
      founderActivationInFlightRef.current = false;
    }
  }, [authUser?.id, authUser?.role, authUser?.tenantId,
    activeTenant?.tenantId, activeTenant?._id, dockScope, workLocatorKey,
    founderActivationEligible, verifiedWorkspaceContext]);

  /**
   * @function hydrateDockContext
   * @description Loads kennel posture via sovereign api – never window.fetch.
   * @collaboration Invoked on mount and during manual refresh.
   */
  const hydrateDockContext = useCallback(async () => {
    healthAbortRef.current?.abort();
    const controller = new AbortController();
    healthAbortRef.current = controller;
    const generation = ++healthGenerationRef.current;
    const isCurrent = () => (
      !controller.signal.aborted
      && healthGenerationRef.current === generation
      && dockScopeRef.current === dockScope
    );
    // Optional finance evidence must never serialize or delay kernel health.
    // Its own EOS IAM remains authoritative; a failure yields no finance facts.
    const billingEvidenceRead = canProbeBillingIntelligence(authUser?.role)
      ? api.get('/billing/intelligence/evidence', {
        params: { as_of: new Date().toISOString() },
        timeout: 8000,
        signal: controller.signal,
      }).then((response) => (
        response?.status === 200
        && response?.data
        && typeof response.data === 'object'
          ? response.data : null
      )).catch(() => null)
      : Promise.resolve(null);

    try {
      // Optional EOS health reads never authorize or block Headquarters.
      const kernelRes = await api.get('/kernel', {
        timeout: 8000,
        signal: controller.signal,
        forceNetworkRetry: true,
      });
      if (!isCurrent()) return;
      const kernel = kernelRes?.data || {};
      const live = String(kernel.status || '').toUpperCase() === 'OPERATIONAL';
      setKennelPosture(live ? 'OPERATIONAL' : 'DEGRADED');

      const normalizedDockContext = buildWilsyAIProductivityCopy({
        result: live ? 'WILSY_AI_SOVEREIGN_CONTEXT_RESOLVED' : 'SOURCE_DEGRADED',
        kennel: kernel,
        bridge: kernel.bridge,
        workspace: {
          operatingRole: authUser?.role || 'UNRESOLVED',
          tenantId: activeTenant?.tenantId || activeTenant?._id || authUser?.tenantId || '',
        },
      });
      if (!isCurrent()) return;
      setDockContext(normalizedDockContext);
      // Publish the independent verified kernel result before optional finance
      // completion; late responses may enrich only the same live auth scope.
      const billingIntelligenceEvidence = await billingEvidenceRead;
      if (!isCurrent()) return;
      if (billingIntelligenceEvidence) {
        setDockContext({
          ...normalizedDockContext,
          billingIntelligenceEvidence,
        });
      }
    } catch (err) {
      if (!isCurrent()) return;
      // Absence of verified EOS health is not successful advisory context.
      setDockContext(null);
      setKennelPosture('SOURCE_SILENT');
      if (import.meta.env.DEV) {
        console.info('[IntelligenceDock] Optional kernel health probe not verified; independent workspace status is unchanged.', {
          outcome: err?.code === 'ECONNABORTED' ? 'TIMEOUT' : 'SOURCE_UNAVAILABLE',
          http_status: Number.isInteger(err?.response?.status)
            ? err.response.status : 'NO_HTTP_RESPONSE',
        });
      }
    }
  }, [dockScope, authUser?.role, activeTenant?.tenantId, activeTenant?._id]);

  /**
   * @function handleNewThread
   * @description Creates a new conversation thread without clearing existing history.
   * @institutional Allows operators to compartmentalize conversations by topic.
   */
  const handleNewThread = useCallback(async () => {
    const scopeAtStart = dockScopeRef.current;
    try {
      const fresh = await createWilsyAIConversationThread({
        title: 'New Sovereign Session',
        workspace: 'WILSY OS',
      });
      if (scopeAtStart !== dockScopeRef.current) return;
      setConversationThreads((prev) => [fresh, ...prev.filter((item) => item.id !== fresh.id)]);
      setActiveThreadId(fresh.id);
      setActiveTab('chat');
    } catch (err) {
      if (scopeAtStart === dockScopeRef.current) {
        setErrorMessage(err?.message || 'Failed to create a new thread.');
      }
    }
  }, []);

  /**
   * @function handleRefresh
   * @description Manually refreshes the conversation list and Kennel context.
   * @institutional Prevents stale data from persisting after external updates.
   */
  const handleRefresh = useCallback(async () => {
    const scopeAtStart = dockScopeRef.current;
    setErrorMessage('');
    try {
      const refreshed = await loadWilsyAIConversationThreads();
      if (scopeAtStart !== dockScopeRef.current) return;
      setConversationThreads(refreshed);
      if (!refreshed.find(t => t.id === activeThreadId)) {
        setActiveThreadId(refreshed[0]?.id || null);
      }
      await hydrateDockContext(); // Also refresh kennel context
    } catch (err) {
      if (scopeAtStart === dockScopeRef.current) {
        setErrorMessage('Failed to refresh threads.');
      }
    }
  }, [activeThreadId, hydrateDockContext]);

  useEffect(() => {
    let active = true;
    const hydrate = async () => {
      try {
        let threads = await loadWilsyAIConversationThreads();
        if (!threads.length) {
          const fresh = await createWilsyAIConversationThread({
            title: 'New Sovereign Session',
            workspace: 'WILSY OS',
          });
          threads = [fresh];
        }
        if (active) {
          setConversationThreads(threads);
          setActiveThreadId(threads[0]?.id || null);
        }
      } catch {
        if (active) {
          setConversationThreads([]);
          setActiveThreadId(null);
        }
      }
      if (active) await hydrateDockContext();
    };
    void hydrate();
    return () => {
      active = false;
      healthAbortRef.current?.abort();
      healthGenerationRef.current += 1;
    };
  }, [hydrateDockContext]);

  const activeThread = useMemo(() => {
    return (
      conversationThreads.find((t) => t.id === activeThreadId) ||
      conversationThreads[0] || { id: null, messages: [] }
    );
  }, [conversationThreads, activeThreadId]);

  // Source inspection is a conversation turn, not a competing status panel.
  // This is a presentation choice only; EOS supplies every actual task fact.
  const hasVerifiedSourceReply = conversationView === 'SOURCE'
    && (activeThread?.messages || []).some(message =>
      message.role === 'assistant' && message.meta?.source === 'PYTHON_EOS'
      && message.meta?.phase === 'SOURCE_VERIFIED_READ_ONLY');

  useEffect(() => {
    if (activeTab !== 'chat' || !isOpen) return;
    const target = hasVerifiedSourceReply ? latestVerifiedReplyRef.current : messagesEndRef.current;
    const scroller = messagesScrollRef.current;
    if (!target || !scroller) return;
    const distance = target.getBoundingClientRect().top
      - scroller.getBoundingClientRect().top;
    const prefersReducedMotion = typeof window.matchMedia === 'function'
      && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    // Scroll only the Dock's transcript. Never move the underlying Projects page.
    scroller.scrollTo?.({
      top: Math.max(0, scroller.scrollTop + distance - 18),
      behavior: prefersReducedMotion ? 'auto' : 'smooth',
    });
  }, [conversationThreads, activeThreadId, activeTab, isOpen, isSubmitting, hasVerifiedSourceReply]);

  // A verified source read is an inspectable same-session turn, not a
  // model-generated answer or a durable EOS conversation record. Record it
  // only after exact task identity/revision and source scope were verified.
  useEffect(() => {
    const code = parseWilsyTaskInspection(localSourceQuery);
    const evidence = visibleWorkspaceContext?.data;
    const task = evidence?.work?.selected_task;
    if (!isOpen || conversationView !== 'SOURCE' || !code
      || visibleWorkspaceContext?.state !== 'READY'
      || evidence?.locator?.workspace !== 'PROJECTS'
      || evidence?.locator?.project_id !== workLocator.project_id
      || evidence?.locator?.task_id !== workLocator.task_id
      || !task || task.task_id !== workLocator.task_id
      || (workLocator.task_revision && task.revision !== workLocator.task_revision)
      || typeof task.title !== 'string'
      || !(task.title.startsWith(code + ' — ') || task.title.startsWith(code + ' - '))) {
      return undefined;
    }
    const key = [dockScope, workLocatorKey, evidence.context_fingerprint, code].join(':');
    if (recordedSourceReadRef.current === key) return undefined;
    recordedSourceReadRef.current = key;
    let current = true;
    const saveSessionInspection = async () => {
      try {
        const thread = await createWilsyAIConversationThread({
          workspace: 'Projects', title: 'EOS source · ' + code, promptText: localSourceQuery,
        });
        const afterRequest = await persistWilsyAIConversationTurn({
          threadId: thread.id,
          message: { role: 'user', content: localSourceQuery },
        });
        const verifiedStatus = typeof task.status === 'string'
          ? task.status.replaceAll('_', ' ').toLowerCase() : 'not provided';
        const reply = 'EOS source verified: ' + task.title
          + '\nLifecycle: ' + verifiedStatus
          + '\nRevision: ' + task.revision
          + '\nDeadline: ' + (task.due_date || 'not supplied by EOS')
          + '\nPython EOS · Read-only inspection. No model invoked or task changed.';
        const recorded = await persistWilsyAIConversationTurn({
          threadId: afterRequest.id,
          message: { role: 'assistant', content: reply,
            meta: { source: 'PYTHON_EOS', phase: 'SOURCE_VERIFIED_READ_ONLY' } },
        });
        if (!current || dockScopeRef.current !== dockScope
          || workLocatorKeyRef.current !== workLocatorKey) return;
        setConversationThreads(previous => [
          recorded, ...previous.filter(item => item.id !== recorded.id),
        ]);
        setActiveThreadId(recorded.id);
        setAnimatedAssistantKey(recorded.id + ':' + recorded.messages?.at(-1)?.timestamp);
      } catch {
        if (current && dockScopeRef.current === dockScope) {
          recordedSourceReadRef.current = '';
        }
      }
    };
    void saveSessionInspection();
    return () => { current = false; };
  }, [isOpen, conversationView, localSourceQuery, visibleWorkspaceContext,
    workLocatorKey, dockScope]);

  /**
   * @function handleSendMessage
   * @description Legal roles keep C1C; ordinary turns use consented EOS metered reasoning, not the legacy operator BFF.
   */
  const handleSendMessage = useCallback(
    async (rawText) => {
      const text = String(rawText || prompt).trim();
      if (!text || isSubmitting || sendLockRef.current) return;
      // Controlled local intent catalog: these are read-only EOS source views,
      // NOT model answers. No POST, admission, consent or billing for inspection.
      const localCourtesyReply = isLegalDockRole(authUser?.role)
        ? null : resolveWilsyLocalCourtesy(text, activeThread?.messages);
      const localClockReply = isLegalDockRole(authUser?.role)
        ? null : resolveWilsyLocalClock(text);
      const localNonmeteredReply = localCourtesyReply || localClockReply;
      const governedReadPlan = isLegalDockRole(authUser?.role)
        ? null : planWilsyGovernedReadOnlyQuestion(text, activeThread?.messages);
      const projectCountIntent = governedReadPlan
        ? null : isLegalDockRole(authUser?.role)
          ? null : classifyWilsyProjectPortfolioCountIntent(text, activeThread?.messages);
      const activeProjectDetailIntent = Boolean(governedReadPlan)
        || (!isLegalDockRole(authUser?.role)
          && classifyWilsyActiveProjectDetailIntent(text, activeThread?.messages));
      const workSourcePlan = isLegalDockRole(authUser?.role)
        ? null : planWilsyWorkSourceQuestion(text);
      const financialSourcePlan = isLegalDockRole(authUser?.role)
        ? null : planWilsyFinancialSourceRead(text);
      const allowedSourceView = isLegalDockRole(authUser?.role)
        ? null : classifyWilsyAISourceIntent(text);
      const taskCode = isLegalDockRole(authUser?.role) ? null : parseWilsyTaskInspection(text);
      if (taskCode) {
        const tenant = activeTenant?.tenantId || activeTenant?._id || authUser?.tenantId;
        const principal = authUser?.id;
        const project = workLocator.workspace === 'PROJECTS' ? workLocator.project_id : null;
        if (!project || visibleWorkspaceContext?.state !== 'READY'
          || visibleWorkspaceContext.data.work?.project?.project_id !== project) {
          setErrorMessage('Open the verified project before inspecting a task. EOS has not verified this project.');
          return;
        }
        const originalScope = dockScopeRef.current;
        const originalLocator = workLocatorKeyRef.current;
        sendLockRef.current = true;
        setIsSubmitting(true);
        setErrorMessage('');
        try {
          const target = await resolveWilsyTaskInspection(taskCode, project, tenant, principal);
          if (dockScopeRef.current !== originalScope
            || workLocatorKeyRef.current !== originalLocator) return;
          setWorkLocator(previous => ({ ...previous, ...target }));
          setConversationView('SOURCE');
          setLocalSourceQuery(text);
          setPrompt('');
        } catch (cause) {
          if (dockScopeRef.current !== originalScope
            || workLocatorKeyRef.current !== originalLocator) return;
          setErrorMessage([401, 403].includes(cause?.response?.status)
            ? 'EOS denied this project task request.'
            : 'EOS could not independently verify one task for that reference.');
        } finally {
          if (dockScopeRef.current === originalScope
            && workLocatorKeyRef.current === originalLocator) {
            setIsSubmitting(false);
            sendLockRef.current = false;
          }
        }
        return;
      }
      if (allowedSourceView) {
        setConversationView(allowedSourceView);
        setLocalSourceQuery(text);
        setFocusedWorkIndex(null);
        setPrompt('');
        setErrorMessage('');
        return;
      }
      // A server-confirmed reconciliation hold is not an uncertain network
      // retry. Preserve the draft but refuse further sends of this exact
      // attempt, including the Enter key and dynamic suggestion route.
      if (!localNonmeteredReply && !projectCountIntent && !activeProjectDetailIntent && !workSourcePlan && !financialSourcePlan
        && reasoningReplayRef.current.blocked === true
        && reasoningReplayRef.current.scope === dockScopeRef.current
        && reasoningReplayRef.current.text === text
        && reasoningReplayRef.current.locatorKey === workLocatorKeyRef.current) {
        setErrorMessage('This request is awaiting EOS execution and usage reconciliation. No verified answer exists. Resubmitting the same request is blocked.');
        return;
      }
      if (!localNonmeteredReply && !projectCountIntent && !activeProjectDetailIntent && !workSourcePlan && !financialSourcePlan && !isLegalDockRole(authUser?.role) && aiEntitlementNotProvisioned) {
        setErrorMessage('Your workspace is verified, but AI reasoning is not yet activated for this tenant.');
        return;
      }
      if (!localNonmeteredReply && !projectCountIntent && !activeProjectDetailIntent && !workSourcePlan && !financialSourcePlan && !isLegalDockRole(authUser?.role) && aiProviderUnavailable) {
        setErrorMessage('Workspace information is available, but the EOS AI provider is not configured.');
        return;
      }
      if (!localNonmeteredReply && !projectCountIntent && !activeProjectDetailIntent && !workSourcePlan && !financialSourcePlan && !isLegalDockRole(authUser?.role) && !reasoningUsageConsent) {
        setErrorMessage('Confirm the WILSY AI usage terms before requesting reasoning.');
        return;
      }
      const currentProject = workLocator.project_id
        && visibleWorkspaceContext?.state === 'READY'
        && visibleWorkspaceContext.data.work?.project?.project_id === workLocator.project_id
        ? { ...workLocator } : null;
      if (!localNonmeteredReply && !projectCountIntent && !activeProjectDetailIntent && !workSourcePlan && !financialSourcePlan && !isLegalDockRole(authUser?.role) && workLocator.project_id && !currentProject) {
        setErrorMessage('EOS must verify the current project before AI can answer about it. Refresh context.');
        return;
      }
      const reasoningLocator = currentProject
        || (workLocator.workspace === 'HEADQUARTERS'
          ? { workspace: 'HEADQUARTERS', include_work_context: true } : null);
      const locatorKeyAtStart = workLocatorKey;
      const scopeAtStart = dockScopeRef.current;
      const generationAtStart = conversationGenerationRef.current;
      const controller = new AbortController();
      reasoningAbortRef.current = controller;
      sendLockRef.current = true;
      const requestIsCurrent = () => !controller.signal.aborted
        && conversationGenerationRef.current === generationAtStart
        && dockScopeRef.current === scopeAtStart
        && workLocatorKeyRef.current === locatorKeyAtStart;

      setIsSubmitting(true);
      setErrorMessage('');
      setPrompt('');

      const userTurn = {
        role: 'user',
        content: text,
        timestamp: new Date().toISOString(),
      };

      let threadId = activeThreadId;
      try {
        if (!threadId) {
          const fresh = await createWilsyAIConversationThread({
            title: text.slice(0, 48) || 'New Sovereign Session',
            promptText: text,
            workspace: 'WILSY OS',
          });
          if (!requestIsCurrent()) return;
          threadId = fresh.id;
          setActiveThreadId(threadId);
          setConversationThreads((prev) => [fresh, ...prev.filter((t) => t.id !== fresh.id)]);
        }
        const afterUser = await persistWilsyAIConversationTurn({
          threadId,
          message: userTurn,
        });
        if (!requestIsCurrent()) return;
        setConversationThreads((prev) => [
          afterUser,
          ...prev.filter((item) => item.id !== afterUser.id),
        ]);
      } catch (err) {
        if (requestIsCurrent()) {
          setErrorMessage(err?.message || 'Failed to record operator turn.');
          setIsSubmitting(false);
          sendLockRef.current = false;
          reasoningAbortRef.current = null;
        }
        return;
      }

      try {
        let result;
        if (localNonmeteredReply) {
          // Clearly separate device time and courtesy from paid inference.
          result = {
            reply: localNonmeteredReply,
            source: localClockReply ? 'WILSY_LOCAL_DEVICE_TIME' : 'WILSY_LOCAL_COURTESY',
            phase: 'NON_GENERATIVE_BUILT_IN',
            domain: 'GENERAL',
            tenantId: activeTenant?.tenantId || activeTenant?._id || authUser?.tenantId || '',
          };
        } else if (financialSourcePlan) {
          const exactTenant = activeTenant?.tenantId || activeTenant?._id || authUser?.tenantId;
          const exactPrincipal = authUser?.id;
          if (typeof exactTenant !== 'string' || !exactTenant.trim()
            || typeof exactPrincipal !== 'string' || !exactPrincipal.trim()) {
            throw new Error('WILSY_FINANCIAL_SOURCE_SCOPE_UNVERIFIED');
          }
          const options = {
            headers: { 'X-Tenant-ID': exactTenant },
            signal: controller.signal, timeout: 15000,
          };
          if (financialSourcePlan.domain === 'BILLING') {
            const response = await api.get(
              WILSY_READ_ONLY_SOURCE_CAPABILITIES.BILLING_EVIDENCE.endpoint + financialSourcePlan.evidenceId,
              options,
            );
            if (!requestIsCurrent()) return;
            const source = verifyWilsyBillingEvidenceRead(
              response?.data, exactTenant, exactPrincipal, financialSourcePlan.evidenceId,
            );
            result = {
              reply: 'The immutable EOS Billing evidence as of ' + source.as_of
                + ' verifies ' + source.receivable_count + ' commercial receivables, '
                + source.aging_evidence_count + ' aging records and '
                + source.dunning_evidence_count + ' dunning records. '
                + 'The evidence does not establish a live account balance or verified payment settlement.',
              source: 'WILSY_EOS_BILLING_EVIDENCE',
              phase: 'SOURCE_VERIFIED_READ_ONLY', domain: 'BILLING', tenantId: exactTenant,
            };
          } else {
            const locationResponse = await api.get(WILSY_READ_ONLY_SOURCE_CAPABILITIES.POS_LOCATIONS.endpoint, options);
            if (!requestIsCurrent()) return;
            const locations = verifyWilsyPOSLocations(
              locationResponse?.data, exactTenant, exactPrincipal,
            );
            let reply;
            if (!locations.length) {
              reply = 'No current POS location assignments are verified for this account. I cannot establish a sale count.';
            } else if (locations.length !== 1) {
              reply = 'You have ' + locations.length
                + ' assigned POS locations. Select a location in POS to inspect its commercial sale count; I will not combine unverified or unauthorized branches.';
            } else {
              const locationId = locations[0].location_id;
              const response = await api.get(
                WILSY_READ_ONLY_SOURCE_CAPABILITIES.POS_COMMERCIAL.endpoint
                + encodeURIComponent(locationId) + '/commercial-summary',
                options,
              );
              if (!requestIsCurrent()) return;
              const counts = verifyWilsyPOSCommercialSummary(
                response?.data, exactTenant, exactPrincipal, locationId,
              );
              reply = 'At your authorised POS location ' + locationId + ', EOS verifies '
                + counts.total + ' commercial sales: '
                + counts.COMPLETED_COMMERCIAL + ' completed commercially, '
                + counts.OPEN + ' open, ' + counts.DRAFT + ' draft and '
                + counts.VOIDED + ' voided. This does not prove payment settlement.';
            }
            result = {
              reply, source: 'WILSY_EOS_POS_COMMERCIAL',
              phase: 'SOURCE_VERIFIED_READ_ONLY', domain: 'POS', tenantId: exactTenant,
            };
          }
        } else if (workSourcePlan) {
          const exactTenant = activeTenant?.tenantId || activeTenant?._id || authUser?.tenantId;
          const exactPrincipal = authUser?.id;
          if (typeof exactTenant !== 'string' || !exactTenant.trim()
            || typeof exactPrincipal !== 'string' || !exactPrincipal.trim()) {
            throw new Error('WILSY_WORK_SOURCE_SCOPE_UNVERIFIED');
          }
          // The same canonical source-coverage validator used by Headquarters
          // and Daily Attention checks tenant, principal, item provenance,
          // source admission, every source count, and command authority.
          const response = await api.get(workSourcePlan.capability.endpoint, {
            headers: { 'X-Tenant-ID': exactTenant },
            timeout: 15000,
            signal: controller.signal,
            forceNetworkRetry: true,
          });
          if (!requestIsCurrent()) return;
          const evidence = assertUnifiedMyWorkProjection(response?.data, {
            tenantId: exactTenant,
            principalId: exactPrincipal,
          });
          result = {
            reply: formatWilsyGovernedMyWorkCount(evidence, workSourcePlan),
            source: 'WILSY_EOS_MULTI_SOURCE_WORK',
            phase: 'SOURCE_VERIFIED_READ_ONLY',
            domain: 'MY_WORK',
            tenantId: exactTenant,
          };
        } else if (projectCountIntent) {
          const exactTenant = activeTenant?.tenantId || activeTenant?._id || authUser?.tenantId;
          const exactPrincipal = authUser?.id;
          if (typeof exactTenant !== 'string' || !exactTenant.trim()
            || typeof exactPrincipal !== 'string' || !exactPrincipal.trim()) {
            throw new Error('WILSY_PROJECT_SUMMARY_IDENTITY_UNVERIFIED');
          }
          // This route independently checks Projects entitlement and current
          // tenant-authorized reader capacity. Never reuse stale UI totals.
          const response = await api.get('/projects/summary', {
            headers: { 'X-Tenant-ID': exactTenant },
            timeout: 15000,
            signal: controller.signal,
          });
          if (!requestIsCurrent()) return;
          const counts = verifyWilsyProjectPortfolioSummary(
            response?.data, exactTenant, exactPrincipal,
          );
          result = {
            reply: projectCountIntent.status === 'total'
              ? (counts.total === 1
                ? 'You have 1 project in this tenant, according to the current EOS Projects registry.'
                : 'You have ' + counts.total + ' projects in this tenant, according to the current EOS Projects registry.')
              : counts[projectCountIntent.status] + ' of your ' + counts.total
                + ' projects are ' + ({
                  active: 'active', planned: 'planned', on_hold: 'on hold',
                  done: 'completed', cancelled: 'cancelled',
                })[projectCountIntent.status]
                + ', according to the current EOS Projects registry.',
            source: 'WILSY_EOS_PROJECT_SUMMARY',
            phase: 'SOURCE_VERIFIED_READ_ONLY',
            domain: 'PROJECTS',
            tenantId: exactTenant,
          };
        } else if (activeProjectDetailIntent) {
          const exactTenant = activeTenant?.tenantId || activeTenant?._id || authUser?.tenantId;
          const exactPrincipal = authUser?.id;
          if (typeof exactTenant !== 'string' || !exactTenant.trim()
            || typeof exactPrincipal !== 'string' || !exactPrincipal.trim()) {
            throw new Error('WILSY_ACTIVE_PROJECT_SCOPE_UNVERIFIED');
          }
          const requestOptions = {
            headers: { 'X-Tenant-ID': exactTenant },
            timeout: 15000,
            signal: controller.signal,
          };
          // A fresh summary and status-filtered list are separate authorised
          // source reads. Count 1 must resolve to exactly one real active row.
          const summaryResponse = await api.get('/projects/summary', requestOptions);
          if (!requestIsCurrent()) return;
          const counts = verifyWilsyProjectPortfolioSummary(
            summaryResponse?.data, exactTenant, exactPrincipal,
          );
          const statusPrefix = governedReadPlan
            ? counts.active + ' of your ' + counts.total
              + ' projects are active, according to the current EOS Projects registry.\n\n'
            : '';
          let responseText;
          if (counts.active === 0) {
            responseText = 'The current EOS Projects registry verifies no active projects in this tenant.';
          } else if (counts.active > 100) {
            throw new Error('WILSY_ACTIVE_PROJECT_LIST_PAGE_REQUIRED');
          } else {
            const listed = await api.get('/projects?project_status=active&limit=100&offset=0', requestOptions);
            if (!requestIsCurrent()) return;
            const projects = verifyWilsyActiveProjectList(
              listed?.data, exactTenant, exactPrincipal, counts.active,
            );
            if (projects.length !== 1) {
              responseText = 'The registry verifies ' + projects.length
                + ' active projects. Specify which project you want to inspect; '
                + 'I will not choose one on your behalf.';
            } else {
              const projectId = projects[0].project_id;
              const detail = await api.get('/projects/' + encodeURIComponent(projectId), requestOptions);
              if (!requestIsCurrent()) return;
              const project = verifyWilsyActiveProjectDetail(
                detail?.data, exactTenant, exactPrincipal, projectId,
              );
              // Reject a concurrent mutation between independent source reads.
              if (project.revision !== projects[0].revision) {
                throw new Error('WILSY_ACTIVE_PROJECT_CHANGED_DURING_READ');
              }
              responseText = formatWilsyActiveProjectDetails(project);
            }
          }
          result = {
            reply: statusPrefix + responseText,
            source: 'WILSY_EOS_PROJECT_DETAIL',
            phase: 'SOURCE_VERIFIED_READ_ONLY',
            domain: 'PROJECTS',
            tenantId: exactTenant,
          };
        } else if (isLegalDockRole(authUser?.role)) {
          const response = await executeWilsyAILegalServices(text, uuidv4());
          const legal = response?.data || {};
          result = {
            reply:
              legal.response_text
              || 'The legal-services authority returned no response text.',
            source: 'WILSY_AI_LEGAL_SERVICES',
            phase: 'C1C',
            intent: legal.outcome || 'LEGAL_SERVICES',
            domain: 'LEGAL',
            tenantId: activeTenant?.tenantId || activeTenant?._id || authUser?.tenantId || '',
          };
        } else {
          const exactTenant = activeTenant?.tenantId || activeTenant?._id || authUser?.tenantId;
          if (typeof exactTenant !== 'string' || !exactTenant.trim()) {
            throw new Error('WILSY_AI_TENANT_SCOPE_REQUIRED');
          }
          // Session conversation only: page location and browser role labels
          // are never promoted to verified EOS business evidence.
          const previous = (activeThread?.messages || [])
            .filter(item => ['user', 'assistant'].includes(item?.role)
              && typeof item?.content === 'string')
            .slice(-6)
            .map(item => (item.role === 'user' ? 'Operator' : 'WILSY AI')
              + ': ' + item.content.slice(0, 900))
            .join('\n');
          const reasoningPrompt = [
            'Current user question:', text,
            ...(previous ? ['Previous conversation (not EOS source evidence):', previous] : []),
            'Do not claim verified access to tenant projects, employee records, '
              + 'financial balances or legal matters without an authorized EOS '
              + 'tool result. Inferences are not authorizations or execution.',
          ].join('\n\n').slice(0, 12000);
          const pending = reasoningReplayRef.current;
          const replay = pending.scope === scopeAtStart && pending.text === text
            && pending.locatorKey === locatorKeyAtStart && pending.key && pending.prompt
            ? pending
            : { scope: scopeAtStart, text, prompt: reasoningPrompt, key: uuidv4(),
              locatorKey: locatorKeyAtStart, params: reasoningLocator };
          reasoningReplayRef.current = replay;
          const response = await api.post('/wilsy-ai/reasoning', {
            prompt: replay.prompt,
          }, {
            headers: { 'X-Tenant-ID': exactTenant, 'Idempotency-Key': replay.key },
            ...(replay.params ? { params: replay.params } : {}),
            timeout: 30000,
            signal: controller.signal,
          });
          const data = response?.data;
          if (typeof data?.response_text !== 'string' || !data.response_text.trim()
            || typeof data?.usage_observation_id !== 'string') {
            throw new Error('WILSY_AI_REASONING_RESULT_UNVERIFIED');
          }
          if (!requestIsCurrent()) return;
          reasoningReplayRef.current = { scope: '', text: '', prompt: '', key: '' };
          result = {
            reply: data.response_text,
            source: 'PYTHON_EOS_WILSY_AI_REASONING',
            phase: 'ADMITTED_REASONING',
            domain: 'GENERAL',
            tenantId: exactTenant,
          };
        }

        if (!requestIsCurrent()) return;

        const content =
          result?.reply ||
          result?.content ||
          result?.message ||
          result?.answer ||
          result?.result ||
            'Operator source returned no intelligence; no recommendation was generated.';

        const assistantTurn = {
          role: 'assistant',
          content: String(content),
          timestamp: new Date().toISOString(),
          meta: {
            source: result?.source || 'OPERATOR_ENGINE_BACKEND',
            phase: result?.phase || 'KENNEL_PHASE_4',
            kennelPosture,
            intent: result?.intent,
            domain: result?.domain,
            tenantId: result?.tenantId || activeTenant?.tenantId || authUser?.tenantId || '',
          },
        };

        const afterAssistant = await persistWilsyAIConversationTurn({
          threadId,
          message: assistantTurn,
        });
        if (!requestIsCurrent()) return;
        setConversationThreads((prev) => [
          afterAssistant,
          ...prev.filter((item) => item.id !== afterAssistant.id),
        ]);
        setAnimatedAssistantKey(threadId + ':' + assistantTurn.timestamp);
      } catch (err) {
        if (!requestIsCurrent()) return;
        const status = err?.response?.status;
        const detail = err?.response?.data?.detail;
        if (!isLegalDockRole(authUser?.role)
          && status === 409 && detail === 'C1B_REASONING_REPLAY_CONFLICT') {
          // The server has confirmed this attempt cannot be replayed.
          // Keep its draft but block same-question re-admission; a new
          // question requires a deliberate different operator input.
          reasoningReplayRef.current = { ...reasoningReplayRef.current, blocked: true };
        }
        if (!isLegalDockRole(authUser?.role)
          && status === 503 && detail === 'C1B_REASONING_RECONCILIATION_REQUIRED') {
          reasoningReplayRef.current = { ...reasoningReplayRef.current, blocked: true };
        }
        const safeMessage = financialSourcePlan
          ? (status === 401 ? 'Sign in to inspect authorised financial source evidence.'
            : status === 403 ? 'This account is not authorised to inspect the requested Billing or POS source.'
              : 'EOS could not verify the requested Billing or POS evidence. No financial fact was guessed and no AI request was sent.')
          : workSourcePlan
          ? (status === 401 ? 'Sign in to inspect your authorised work sources.'
            : status === 403 ? 'Your current session does not have permission for the requested work sources.'
              : 'EOS could not verify a complete current work-source projection. No count was guessed, and no AI request was sent.')
          : activeProjectDetailIntent
          ? (status === 401 ? 'Sign in to inspect current Projects.'
            : status === 403 ? 'The current account is not authorised to inspect these Projects.'
              : 'EOS could not verify current active-project details. No project facts were guessed and no AI request was sent.')
          : projectCountIntent
          ? (status === 401
            ? 'Sign in to inspect your Projects registry.'
            : status === 403
              ? 'The current account is not authorized to view this tenant’s Projects summary.'
              : 'I cannot verify your Projects count from EOS right now. No project total was guessed, and no AI request was sent.')
          : status === 401
          ? 'Authentication is required to use WILSY AI.'
          : status === 403 ? 'WILSY AI permission or subscription entitlement is not verified.'
          : status === 409 && detail === 'C1B_REASONING_REPLAY_CONFLICT'
            ? 'This AI request conflicts with a previously recorded attempt. No answer was generated. Review the question and press Send to create a separate request.'
          : status === 503 && detail === 'C1B_REASONING_RECONCILIATION_REQUIRED'
            ? 'I could not verify an AI answer. EOS must reconcile provider execution and usage evidence before this specific request can be retried. Your draft is preserved; no billable result is confirmed.'
          : status === 429 ? 'WILSY AI usage capacity is exhausted for the current period.'
          : status === 503 ? 'The EOS AI provider or entitlement source is temporarily unavailable.'
          : 'WILSY AI could not verify this answer. Your question remains in the composer.';
        setErrorMessage(safeMessage);
        if (!isLegalDockRole(authUser?.role)) setPrompt(text);
        // A failure is not an AI answer; retain draft and show one error only.
      } finally {
        if (requestIsCurrent()) {
          sendLockRef.current = false;
          reasoningAbortRef.current = null;
          setIsSubmitting(false);
        }
      }
    },
    [
      prompt,
      isSubmitting,
      reasoningUsageConsent,
      aiEntitlementNotProvisioned,
      aiProviderUnavailable,
      workLocatorKey,
      workLocator,
      visibleWorkspaceContext,
      authUser?.role,
      dockScope,
      activeThreadId,
      activeThread?.messages,
      dockContext,
      activeTenant,
      kennelPosture,
    ]
  );

  /**
   * @function handleGenerateLegalAdvisory
   * @description Explicitly composes C1C tool-assisted evidence with C1E advisory projection.
   * @institutional C1C/C1E remain server authorities; the Dock owns only a fresh
   * transport replay key and transient presentation state.
   */
  const handleGenerateLegalAdvisory = useCallback(async () => {
    const exactPrompt = legalPrompt.trim();
    if (!exactPrompt || legalSubmitting) return;

    setLegalSubmitting(true);
    setLegalError('');
    setLegalServiceResponse(null);
    setLegalAdvisory(null);
    try {
      const c1cResponse = await executeWilsyAILegalServices(exactPrompt, uuidv4());
      const c1cPayload = c1cResponse?.data || {};
      setLegalServiceResponse({
        orchestration_id: c1cPayload.orchestration_id,
        outcome: c1cPayload.outcome,
        response_text: c1cPayload.response_text,
        sources: c1cPayload.sources,
      });
      if (c1cPayload.outcome !== 'TOOL_ASSISTED') return;
      if (typeof c1cPayload.orchestration_id !== 'string' || !c1cPayload.orchestration_id) {
        setLegalError('Tool-assisted orchestration did not return an advisory identity.');
        return;
      }
      const c1eResponse = await generateWilsyAILegalNextActions(c1cPayload.orchestration_id);
      const advisory = c1eResponse?.data;
      if (!advisory || typeof advisory !== 'object') {
        setLegalError('Evidence-backed advisory was unavailable; no fabricated result was returned.');
        return;
      }
      setLegalAdvisory(advisory);
    } catch (error) {
      setLegalError(formatLegalAdvisoryError(error));
      setLegalAdvisory(null);
    } finally {
      setLegalSubmitting(false);
    }
  }, [legalPrompt, legalSubmitting]);

  /**
   * @function handleRefreshLegalAdvisory
   * @description Reads the current server-owned advisory status exactly once.
   */
  const handleRefreshLegalAdvisory = useCallback(async () => {
    const advisoryId = legalAdvisory?.advisory_id;
    if (!advisoryId || legalRefreshing) return;
    setLegalRefreshing(true);
    setLegalError('');
    try {
      const response = await readWilsyAILegalNextAction(advisoryId);
      setLegalAdvisory(response?.data || null);
    } catch (error) {
      setLegalError(formatLegalAdvisoryError(error));
    } finally {
      setLegalRefreshing(false);
    }
  }, [legalAdvisory?.advisory_id, legalRefreshing]);

  /**
   * @function handleViewSuccessor
   * @description Reads a server-owned successor advisory without generating a new one.
   * @param {string} successorId - Persisted successor identity from the stale advisory.
   */
  const handleViewSuccessor = useCallback(async (successorId) => {
    if (!successorId || legalRefreshing) return;
    setLegalRefreshing(true);
    setLegalError('');
    try {
      const response = await readWilsyAILegalNextAction(successorId);
      setLegalAdvisory(response?.data || null);
    } catch (error) {
      setLegalError(formatLegalAdvisoryError(error));
    } finally {
      setLegalRefreshing(false);
    }
  }, [legalRefreshing]);

  /**
   * @function clearLegalAdvisoryView
   * @description Clears transient C1E presentation state without touching history or storage.
   */
  const clearLegalAdvisoryView = useCallback(() => {
    setLegalPrompt('');
    setLegalError('');
    setLegalServiceResponse(null);
    setLegalAdvisory(null);
  }, []);

  /**
   * @function handleObserveDeadlines
   * @description Reads a certified D6 Core Legal observation for one explicit matter.
   * @institutional The browser supplies only a locator and observation instant;
   * server IAM and D6 own scope and temporal posture. No advice is generated.
   */
  const handleObserveDeadlines = useCallback(async () => {
    const exactMatterId = deadlineMatterId.trim();
    if (!exactMatterId || deadlineLoading) return;
    setDeadlineLoading(true);
    setDeadlineError('');
    setDeadlineIntelligence(null);
    try {
      const projection = await getLegalMatterDeadlineIntelligence(
        exactMatterId,
        new Date().toISOString(),
      );
      setDeadlineIntelligence(projection);
    } catch (error) {
      const status = error?.response?.status ?? error?.status;
      if (status === 403) {
        setDeadlineError('Current tenant authority does not permit deadline intelligence access.');
      } else if (status === 404) {
        setDeadlineError('No authorized deadline source is available for this matter.');
      } else if (status === 422) {
        setDeadlineError('Matter or observation input was rejected.');
      } else {
        setDeadlineError('Deadline observation is unavailable; no posture was inferred.');
      }
    } finally {
      setDeadlineLoading(false);
    }
  }, [deadlineMatterId, deadlineLoading]);

  const welcomeGreeting = operatorGreeting(authUser);
  const visibleHeadquartersWork = headquartersWork?.scope === dockScope
    && workLocator.workspace === 'HEADQUARTERS' ? headquartersWork : null;
  // Focus is a view over the current, independently rechecked EOS projection.
  // Never retain or forward browser-selected task facts as command authority.
  const focusedWork = visibleHeadquartersWork?.state === 'READY'
    && Number.isInteger(focusedWorkIndex)
    ? visibleHeadquartersWork.items[focusedWorkIndex] || null : null;
  const sourceWorkspaceLabel = visibleWorkspaceContext?.state === 'READY'
    ? (visibleWorkspaceContext.data.locator?.workspace === 'PROJECTS'
      ? 'Project workspace' : 'Headquarters workspace') : null;
  const readOnlySourceIntent = Boolean(classifyWilsyAISourceIntent(prompt) || parseWilsyTaskInspection(prompt));
  const localCourtesyIntent = Boolean(resolveWilsyLocalCourtesy(prompt, activeThread?.messages)
    || resolveWilsyLocalClock(prompt)
    || (!isLegalDockRole(authUser?.role)
      && (planWilsyGovernedReadOnlyQuestion(prompt, activeThread?.messages)
        || classifyWilsyProjectPortfolioCountIntent(prompt, activeThread?.messages)
        || classifyWilsyActiveProjectDetailIntent(prompt, activeThread?.messages)
        || planWilsyWorkSourceQuestion(prompt)
        || planWilsyFinancialSourceRead(prompt))));
  const operatorNameCandidate = [
    [authUser?.firstName || authUser?.first_name, authUser?.lastName || authUser?.last_name]
      .filter(value => typeof value === 'string' && value.trim()).join(' '),
    authUser?.displayName, authUser?.name,
  ].find(value => typeof value === 'string' && value.trim() && !value.includes('@'));
  const operatorLabel = operatorNameCandidate?.trim().slice(0, 96) || 'You';
  const legalStatus = String(legalAdvisory?.status || '').toUpperCase();
  const authoritativeTenantBrand = resolveAuthoritativeTenantBrand(activeTenant);

  return (
    <div ref={dockContainerRef} className={styles.intelligenceDockContainer}
      data-wilsy-intelligence-dock="active" data-kennel={kennelPosture}
      data-ai-layout={isOpen ? 'OPEN' : launcherMinimized ? 'MINIMIZED' : 'LAUNCHER'}
      data-dragging={dragging ? 'true' : undefined}
      style={dockPosition ? { left: dockPosition.x, top: dockPosition.y, right: 'auto', bottom: 'auto' } : undefined}>
      <span className={styles.srOnly} role="status">{positionNotice}</span>
      {!isOpen && (
        <div className={`${styles.launcherTray} ${launcherMinimized ? styles.launcherMinimized : ''}`}>
          {moveHandle}
          <button ref={launcherButtonRef} type="button" className={styles.dockLauncherButton}
            onClick={() => {
              if (workLocator.workspace === 'PROJECTS' && workLocator.project_id && workLocator.task_id) {
                // Untrusted locator is not displayed as task truth. Only the
                // independently authorized EOS context response may do that.
                setActiveTab('chat');
                setConversationView('SOURCE');
                setLocalSourceQuery('Inspect authorized task context');
              }
              setIsOpen(true);
            }} title="Open Wilsy OS Intelligence Dock"
            aria-label="Open Wilsy OS Intelligence Dock" aria-expanded="false">
            <img src="/brand/wilsy-ai-emblem.svg" className={styles.aiEmblem} alt="" aria-hidden="true"/>
            {!launcherMinimized && <span>WILSY OS<small>AI COMPANION</small></span>}
          </button>
          <button type="button" className={styles.launcherSizeControl}
            title={launcherMinimized ? 'Restore AI launcher' : 'Minimize AI launcher'}
            onClick={() => { setLauncherMinimized(value => !value); setPositionNotice('AI launcher size changed.'); }}>
            {launcherMinimized ? <PanelRightOpen size={14}/> : <Minus size={14}/>}
          </button>
        </div>
      )}

      {isOpen && (
        <section className={`${styles.dockWindow} ${isExpanded ? styles.dockExpanded : ''}`} ref={companionPanelRef} tabIndex={-1} role="region" aria-label="WILSY OS AI companion"
          onKeyDown={event => { if (event.key === 'Escape') { event.stopPropagation(); setIsOpen(false); setLauncherMinimized(true); } }}>
          <div className={styles.dockHeader}>
            {moveHandle}
            <div className={styles.dockHeaderTitle}>
              <img src="/brand/wilsy-ai-emblem.svg" className={styles.headerEmblem} alt="Wilsy AI neural core"/>
              <div>
                <span>WILSY OS Intelligence Dock</span>
                <small className={styles.kennelBadge} data-posture={kennelPosture}
                  aria-label={`EOS source status: ${visibleWorkspaceContext?.state === 'READY' ? 'workspace verified' : 'workspace not yet verified'}; kernel health ${kennelPosture === 'OPERATIONAL' ? 'available' : 'not verified'}`}>
                  {visibleWorkspaceContext?.state === 'READY'
                    ? 'Workspace verified'
                    : kennelPosture === 'OPERATIONAL'
                      ? 'EOS connected'
                      : kennelPosture === 'CLIENT_OFFLINE'
                        ? 'Connection unavailable'
                        : 'Source verification pending'}
                </small>
                {authoritativeTenantBrand && (
                  <small className={styles.workspaceBrand} data-brand-source="ACTIVE_TENANT_CONTEXT">
                    {authoritativeTenantBrand}
                  </small>
                )}
              </div>
            </div>
            <div className={styles.dockHeaderActions}>
              <button type="button" className={styles.headerIconButton} title="Reset AI position"
                onClick={() => { setDockPosition(null); setPositionNotice('AI companion position reset.'); }}><RotateCcw size={15}/></button>
              <button type="button" className={styles.headerIconButton} title="Minimize dock"
                onClick={() => { setIsOpen(false); setLauncherMinimized(true); }}><Minus size={16}/></button>
              <button
                type="button"
                className={styles.headerIconButton}
                onClick={() => setIsExpanded(!isExpanded)}
                title={isExpanded ? 'Restore dock size' : 'Expand dock'}
              >
                {isExpanded ? <Minimize2 size={16} /> : <PanelRightOpen size={16} />}
              </button>
              <button
                type="button"
                className={styles.headerIconButton}
                onClick={() => { setIsOpen(false); setLauncherMinimized(false); }}
                title="Close dock"
              >
                <X size={16} />
              </button>
            </div>
          </div>

          <div className={styles.dockNavBar} role="navigation" aria-label="Intelligence Dock navigation">
            <button type="button"
              className={`${styles.navTabButton} ${activeTab === 'chat' ? styles.activeTab : ''}`}
              onClick={() => setActiveTab('chat')}>
              <MessageSquareText size={15}/><span>Conversation</span>
            </button>
            <button type="button"
              className={`${styles.navTabButton} ${activeTab === 'history' ? styles.activeTab : ''}`}
              onClick={() => setActiveTab('history')}>
              <History size={15}/><span>Recent conversations</span>
            </button>
            {isLegalDockRole(authUser?.role) && (
              <button type="button"
                className={`${styles.navTabButton} ${activeTab === 'legalAdvisory' ? styles.activeTab : ''}`}
                onClick={() => setActiveTab('legalAdvisory')}>
                <FileCheck2 size={15}/><span>Legal tools</span>
              </button>
            )}
            {isLegalDockRole(authUser?.role) && (
              <button type="button"
                className={`${styles.navTabButton} ${activeTab === 'deadlineIntelligence' ? styles.activeTab : ''}`}
                onClick={() => setActiveTab('deadlineIntelligence')}>
                <FileCheck2 size={15}/><span>Deadlines</span>
              </button>
            )}
          </div>

          <div className={styles.dockBody}>
            {activeTab === 'chat' && (
              <div className={styles.chatTabContent}>
                <div ref={messagesScrollRef} className={`${styles.messagesContainer} ${hasVerifiedSourceReply ? styles.verifiedAnswerFocus : ''}`} style={{ minHeight: 0 }}>
                  {conversationView === 'WELCOME'
                    && (!activeThread?.messages || activeThread.messages.length === 0) && (
                    <div className={styles.emptyChatWelcome}>
                      <h4>{welcomeGreeting}</h4>
                      <p style={{ color: '#d1dfef', maxWidth: '68ch', lineHeight: 1.7 }}>
                        {visibleWorkspaceContext?.state === 'READY'
                          ? (visibleWorkspaceContext.data.work?.selected_task?.title
                            ? `You're viewing “${visibleWorkspaceContext.data.work.selected_task.title}”. What would you like to do with this verified task context?`
                            : visibleWorkspaceContext.data.work?.project?.name
                              ? `You're viewing “${visibleWorkspaceContext.data.work.project.name}”. What would you like to inspect?`
                              : 'Ask about your work, overdue tasks or this workspace. EOS will determine what you are authorised to see.')
                          : 'Ask me about the work or workspace you are viewing. I can inspect authorised EOS sources without using AI credits.'}
                      </p>
                    </div>
                  )}
                  {conversationView !== 'WELCOME' && localSourceQuery && !hasVerifiedSourceReply && (
                    <div className={`${styles.chatMessageBubble} ${styles.userBubble}`}
                      aria-label="Your source request" style={{ margin: '4px 0 14px' }}>
                      <div className={styles.bubbleBody}>{localSourceQuery}</div>
                    </div>
                  )}
                  {conversationView !== 'WELCOME' && !hasVerifiedSourceReply && !isLegalDockRole(authUser?.role) && (
                    <div className={styles.conversationSectionHeading}>
                      <strong style={{ color: '#eaf3ff', fontSize: 15 }}>
                        {conversationView === 'SOURCE' ? 'EOS workspace evidence' :
                          conversationView === 'OVERDUE' ? 'EOS overdue work' : 'EOS authorised work'}
                      </strong>
                      <button type="button" className={styles.conversationInlineAction}
                        onClick={() => { setConversationView('WELCOME'); setLocalSourceQuery(''); setFocusedWorkIndex(null); }}>
                        <ArrowLeft size={15} aria-hidden="true" />
                        <span>Back to conversation</span>
                      </button>
                    </div>
                  )}
                  {/* EOS observations are read-only, scoped, and not assistant messages. */}
                {conversationView === 'SOURCE' && authUser?.id && !isLegalDockRole(authUser?.role) && <section
                  className={hasVerifiedSourceReply ? styles.secondarySourceEvidence : undefined}
                  aria-label="Verified workspace context" aria-live="polite"
                  style={{ padding: '10px 0', background: 'transparent', color: '#e5edf6',
                    borderTop: '1px solid rgba(148,163,184,.25)',
                    fontSize: 13, lineHeight: 1.65, overflowWrap: 'anywhere' }}>
                  {visibleWorkspaceContext?.state === 'READY' ? <details ref={workspaceDetailsRef} open={!activeThread?.messages?.some(message =>
                    message?.meta?.source === 'PYTHON_EOS' && message?.meta?.phase === 'SOURCE_VERIFIED_READ_ONLY')}>
                    <summary aria-label="Inspect verified workspace context"
                      style={{ cursor: 'pointer', minHeight: hasVerifiedSourceReply ? 32 : 44 }}>
                      {hasVerifiedSourceReply
                        ? <span className={styles.sourceDisclosureLabel}>View source details</span>
                        : <strong>{visibleWorkspaceContext.data.work?.project?.name || 'Verified workspace source'}</strong>}
                      {!hasVerifiedSourceReply && visibleWorkspaceContext.data.work?.selected_task?.title
                        ? <span style={{ display: 'block', overflowWrap: 'anywhere', fontWeight: 400 }}>
                          {'Viewing task: '}{visibleWorkspaceContext.data.work.selected_task.title}
                        </span> : null}
                      {!hasVerifiedSourceReply && ' · '}{!hasVerifiedSourceReply && (aiEntitlementNotProvisioned ? 'AI reasoning not activated'
                        : aiProviderUnavailable ? 'AI provider unavailable'
                          : `${visibleWorkspaceContext.data.allowance.available_request_units} available · ${Number.isSafeInteger(visibleWorkspaceContext.data.allowance.daily_consumed_request_units) ? visibleWorkspaceContext.data.allowance.daily_consumed_request_units : 'unverified'} completed · ${Number.isSafeInteger(visibleWorkspaceContext.data.allowance.held_request_units) ? visibleWorkspaceContext.data.allowance.held_request_units : 'unverified'} held`)}
                    </summary>
                    {workLocator.task_id && visibleWorkspaceContext.data.work?.selected_task
                      && visibleWorkspaceContext.data.work.selected_task.task_id === workLocator.task_id
                      && <p aria-label="EOS-verified selected task lifecycle"
                        style={{ margin: '4px 0', color: '#e8f1ff' }}>
                        {'Current task · '}
                        {['TODO', 'IN_PROGRESS', 'DONE', 'BLOCKED', 'CANCELLED'].includes(
                          visibleWorkspaceContext.data.work.selected_task.status)
                          ? visibleWorkspaceContext.data.work.selected_task.status.replaceAll('_', ' ').toLowerCase()
                          : 'lifecycle not supplied by EOS'}
                        {' · Revision '}
                        {Number.isSafeInteger(visibleWorkspaceContext.data.work.selected_task.revision)
                          ? visibleWorkspaceContext.data.work.selected_task.revision : 'unverified'}
                        {' · Deadline '}
                        {/^\d{4}-\d{2}-\d{2}$/.test(
                          visibleWorkspaceContext.data.work.selected_task.due_date || '')
                          ? visibleWorkspaceContext.data.work.selected_task.due_date : 'not verified'}
                      </p>}
                    <p style={{ margin: '4px 0' }}>
                      {visibleWorkspaceContext.data.work?.current_person_name || 'Person name unavailable'}
                      {' · '}{aiEntitlementNotProvisioned ? 'AI activation required'
                        : `${visibleWorkspaceContext.data.allowance.available_request_units} requests available`}
                      {' · Seats and pricing: '}{visibleWorkspaceContext.data.allowance.seat_allocation?.state === 'UNAVAILABLE'
                        ? 'unavailable' : 'require independent admission'}
                    </p>
                    <p style={{ margin: '4px 0' }}>Workforce and qualifications: unavailable without independent source authority.</p>
                    <p style={{ margin: '4px 0', color: '#cbd5e1' }}>EOS usage evidence: {Number.isSafeInteger(visibleWorkspaceContext.data.allowance.daily_consumed_request_units) ? visibleWorkspaceContext.data.allowance.daily_consumed_request_units : 'unverified'} completed requests; {Number.isSafeInteger(visibleWorkspaceContext.data.allowance.held_request_units) ? visibleWorkspaceContext.data.allowance.held_request_units : 'unverified'} units held, including any unresolved reconciliation. Held capacity is not proof of a completed or billable model response.</p>
                    {(visibleWorkspaceContext.data.work?.sources || []).filter(source => source.kind === 'PROJECT'
                      && source.project_id === workLocator.project_id).map(source => <button type="button"
                      key={source.project_id} className={styles.historyActionButton}
                      style={{ minHeight: 44, color: '#f8fafc', padding: '6px 10px' }}
                      onClick={() => window.dispatchEvent(new CustomEvent('wilsy:ai-inspect-source', {
                        detail: { tenantId: visibleWorkspaceContext.data.tenant_id,
                          principalId: visibleWorkspaceContext.data.principal_id,
                          project_id: source.project_id },
                      }))}>Inspect source: {source.label}</button>)}
                    <p style={{ margin: '4px 0', color: '#cbd5e1' }}>
                      {aiEntitlementNotProvisioned
                        ? 'Your work is independently verified. Model requests remain disabled until the subscription-backed AI entitlement is activated.'
                        : 'Verified project sources can support reasoning only after independent EOS authorization and usage admission.'}
                    </p>
                  </details> : <span>{visibleWorkspaceContext?.state === 'LOADING' ? 'Verifying workspace context…'
                    : visibleWorkspaceContext?.state === 'DENIED' ? 'Workspace context access denied by EOS.'
                      : visibleWorkspaceContext?.state === 'STALE' ? 'Workspace context changed. Refresh the project source.'
                        : 'Verified workspace context unavailable.'}</span>}
                  {founderActivationEligible && <div style={{
                    padding: '8px 0', display: 'flex', flexWrap: 'wrap',
                    alignItems: 'center', gap: 8,
                  }}>
                    <button type="button" className={styles.historyActionButton}
                      aria-label="Activate Founder Institutional AI"
                      disabled={founderActivationState === 'SUBMITTING'}
                      style={{ minHeight: 44, color: '#f8fafc',
                        border: '1px solid #64748b', padding: '6px 10px' }}
                      onClick={activateFounderInstitutional}>
                      {founderActivationState === 'SUBMITTING'
                        ? 'Verifying Institutional AI…' : 'Activate Institutional AI'}
                    </button>
                    <span style={{ color: '#cbd5e1', fontWeight: 400 }}>
                      Exact Founder subscription · EOS authorizes and audits the change
                    </span>
                  </div>}
                  {founderActivationMessage && <p aria-live="polite"
                    style={{ margin: '5px 0', color: '#e2e8f0' }}>
                    {founderActivationMessage}
                  </p>}
                  <button type="button" className={styles.conversationInlineAction}
                    disabled={visibleWorkspaceContext?.state === 'LOADING'}
                    onClick={() => setContextRefresh(value => value + 1)}>
                    <RefreshCw size={15} aria-hidden="true" />
                    <span>Refresh context</span>
                  </button>
                </section>}
                {(conversationView === 'WORK' || conversationView === 'OVERDUE')
                  && visibleHeadquartersWork?.state === 'READY'
                  && visibleHeadquartersWork.activeCount > 0
                  && <section aria-label="Current authorized work"
                    style={{ padding: '12px 0', background: 'transparent',
                      borderTop: '1px solid rgba(148,163,184,.20)',
                      color: '#d7e4f4', fontSize: 13, lineHeight: 1.65 }}>
                    <strong style={{ fontWeight: 550 }}>
                      Your work · {visibleHeadquartersWork.activeCount} active
                      {' · '}{visibleHeadquartersWork.overdueCount} overdue
                    </strong>
                    <ol style={{ margin: '6px 0 0', paddingLeft: 20 }}>
                      {visibleHeadquartersWork.items.map((item, index) =>
                        conversationView === 'OVERDUE' && !item.overdue ? null :
                        <li key={index} style={{ marginBottom: 4, overflowWrap: 'anywhere' }}>
                          <button type="button"
                            aria-label={`Review verified work: ${item.title}`}
                            aria-pressed={focusedWorkIndex === index}
                            className={styles.conversationWorkLink}
                            onClick={() => setFocusedWorkIndex(index)}>
                            {item.title}
                          </button>
                          <span style={{ color: '#abbfd4' }}>
                            · {item.source}{item.overdue ? ' · Overdue' : ''}
                          </span>
                        </li>)}
                    </ol>
                  </section>}
                {(conversationView === 'WORK' || conversationView === 'OVERDUE')
                  && visibleHeadquartersWork?.state === 'READY'
                  && (visibleHeadquartersWork.activeCount === 0
                    || (conversationView === 'OVERDUE' && visibleHeadquartersWork.overdueCount === 0))
                  && <p role="status" style={{ color: '#d1deed', lineHeight: 1.65 }}>
                    {conversationView === 'OVERDUE'
                      ? 'EOS reports no overdue work in this authorised snapshot.'
                      : 'EOS reports no active work in this authorised snapshot.'}
                  </p>}
                {(conversationView === 'WORK' || conversationView === 'OVERDUE')
                  && visibleHeadquartersWork?.state === 'LOADING'
                  && <p role="status">Checking your authorised work source…</p>}
                {(conversationView === 'WORK' || conversationView === 'OVERDUE')
                  && workLocator.workspace === 'HEADQUARTERS'
                  && ['DENIED', 'STALE', 'EOS_UNAVAILABLE', 'TIMEOUT', 'UNAVAILABLE']
                    .includes(visibleHeadquartersWork?.state)
                  && <section aria-label="Headquarters work source status" role="status"
                    style={{ padding: '12px 0', background: 'transparent',
                      color: '#e2e8f0', borderTop: '1px solid rgba(148,163,184,.25)',
                      display: 'flex', justifyContent: 'space-between',
                      alignItems: 'center', gap: 12, flexWrap: 'wrap',
                      fontSize: 13, lineHeight: 1.65 }}>
                    <span>{visibleHeadquartersWork.state === 'DENIED'
                      ? 'EOS has not authorised My Work for this operating capacity. No tasks are inferred.'
                      : visibleHeadquartersWork.state === 'STALE'
                        ? 'My Work source state changed. An independently authorised refresh is required.'
                        : visibleHeadquartersWork.state === 'EOS_UNAVAILABLE'
                          ? 'EOS My Work returned a source-unavailable response (HTTP 503). No task results were verified.'
                          : visibleHeadquartersWork.state === 'TIMEOUT'
                            ? 'EOS My Work timed out before its response was verified. No tasks were inferred.'
                            : 'Current work could not be verified from EOS. This is not a confirmed empty work queue.'}
                    </span>
                    <button type="button" className={styles.conversationInlineAction}
                      onClick={() => setContextRefresh(value => value + 1)}>
                      <RefreshCw size={15} aria-hidden="true" />
                      <span>Recheck work source</span>
                    </button>
                  </section>}
                    {(conversationView === 'WORK' || conversationView === 'OVERDUE') && focusedWork && (
                    <section aria-label="Selected verified work" role="region"
                      style={{ padding: '12px 0', maxWidth: '70ch',
                        borderTop: '1px solid rgba(148,163,184,.25)',
                        color: '#e5edf6', fontSize: 14, lineHeight: 1.65 }}>
                      <p style={{ margin: '0 0 6px', color: '#a9d7e8' }}>
                        Source-backed work inspection · {focusedWork.source}
                      </p>
                      <strong>{focusedWork.title}</strong>
                      <p style={{ margin: '5px 0 10px' }}>
                        {focusedWork.overdue
                          ? 'EOS marks this item overdue.'
                          : 'EOS has not marked this item overdue.'}
                        {' '}This is a read-only work summary; no task mutation is authorised from the Dock.
                      </p>
                      <button type="button" className={styles.conversationInlineAction}
                        onClick={() => {
                          setPrompt(`What should I review next for "${focusedWork.title}" in ${focusedWork.source}?`);
                          setErrorMessage('');
                        }}>
                        Prepare a question about this work
                      </button>
                      <button type="button" className={styles.conversationInlineAction}
                        onClick={() => setFocusedWorkIndex(null)}>Clear focus</button>
                    </section>
                  )}
                {conversationView !== 'WELCOME' && !hasVerifiedSourceReply && !isLegalDockRole(authUser?.role) && (
                  <nav aria-label="Source follow-up actions"
                    className={styles.conversationFollowUps}>
                    {conversationView !== 'WORK' && workLocator.workspace === 'HEADQUARTERS' && (
                      <button type="button" className={styles.conversationInlineAction}
                        onClick={() => { setConversationView('WORK'); setLocalSourceQuery('Review my work'); setFocusedWorkIndex(null); }}>
                        <ListFilter size={15} aria-hidden="true" />
                        <span>Show my work</span>
                      </button>
                    )}
                    {conversationView !== 'OVERDUE' && visibleHeadquartersWork?.state === 'READY'
                      && visibleHeadquartersWork.overdueCount > 0 && (
                      <button type="button" className={styles.conversationInlineAction}
                        onClick={() => { setConversationView('OVERDUE'); setLocalSourceQuery('Show overdue tasks'); setFocusedWorkIndex(null); }}>
                        <ListFilter size={15} aria-hidden="true" />
                        <span>Only overdue</span>
                      </button>
                    )}
                    {conversationView !== 'SOURCE' && visibleWorkspaceContext?.state === 'READY' && (
                      <button type="button" className={styles.conversationInlineAction}
                        onClick={() => { setConversationView('SOURCE'); setLocalSourceQuery('Inspect this workspace'); setFocusedWorkIndex(null); }}>
                        <FileSearch size={15} aria-hidden="true" />
                        <span>Source evidence</span>
                      </button>
                    )}
                  </nav>
                )}
                {(activeThread?.messages || []).map((msg, idx) => (
                    <div
                      key={`${msg.timestamp || idx}-${idx}`}
                      ref={msg.role === 'assistant' && msg.meta?.source === 'PYTHON_EOS'
                        && msg.meta?.phase === 'SOURCE_VERIFIED_READ_ONLY'
                        ? latestVerifiedReplyRef : undefined}
                      className={`${styles.chatMessageBubble} ${
                        msg.role === 'user' ? styles.userBubble : styles.assistantBubble
                      }`}
                    >
                      <div className={styles.bubbleHeader}>
                        <span>{msg.role === 'user' ? operatorLabel
                          : msg.meta?.source === 'WILSY_LOCAL_COURTESY'
                            ? 'WILSY OS · Built-in reply'
                            : msg.meta?.source === 'WILSY_LOCAL_DEVICE_TIME'
                              ? 'WILSY OS · Device time'
                              : ['WILSY_EOS_PROJECT_SUMMARY', 'WILSY_EOS_PROJECT_DETAIL'].includes(msg.meta?.source)
                                ? 'WILSY OS · Verified Projects'
                                : msg.meta?.source === 'WILSY_EOS_MULTI_SOURCE_WORK'
                                  ? 'WILSY OS · Verified Work'
                                  : msg.meta?.source === 'WILSY_EOS_BILLING_EVIDENCE'
                                    ? 'WILSY OS · Verified Billing'
                                    : msg.meta?.source === 'WILSY_EOS_POS_COMMERCIAL'
                                      ? 'WILSY OS · Verified POS' : 'WILSY OS'}</span>
                        <span>
                          {msg.timestamp
                            ? new Date(msg.timestamp).toLocaleTimeString([], {
                                hour: '2-digit',
                                minute: '2-digit',
                              })
                            : ''}
                        </span>
                      </div>
                      <div className={styles.bubbleBody}>
                        {msg.role === 'assistant' ? (
                          <WilsyProgressiveAssistantText
                            content={msg.content}
                            format={msg.meta?.phase === 'SOURCE_VERIFIED_READ_ONLY'
                              && msg.meta?.source === 'PYTHON_EOS' ? 'VERIFIED_TASK' : 'PLAIN'}
                            animate={Boolean(activeTab === 'chat' && isOpen && activeThread?.id
                              && animatedAssistantKey === activeThread.id + ':' + msg.timestamp)}
                            onComplete={() => setAnimatedAssistantKey((previousKey) => (
                              previousKey === activeThread?.id + ':' + msg.timestamp ? null : previousKey
                            ))}
                          />
                        ) : msg.content}
                      </div>
                    </div>
                  ))}
                  {isSubmitting && (
                    <div className={styles.chatMessageBubble + ' ' + styles.assistantBubble}>
                      <div className={styles.bubbleBody}>Consulting operator intelligence…</div>
                    </div>
                  )}
                  {errorMessage && (
                    <div className={styles.assistantBubble} role="status"
                      aria-label="WILSY OS request status"
                      style={{ padding: '10px 0', maxWidth: '70ch' }}>
                      <div className={styles.bubbleHeader}>WILSY OS · Request status</div>
                      <p style={{ margin: 0, color: '#f4d9cd', lineHeight: 1.65,
                        overflowWrap: 'anywhere' }}>{errorMessage}</p>
                    </div>
                  )}
                  <div ref={messagesEndRef} />
                </div>

                {!isLegalDockRole(authUser?.role) && <div style={{
                  padding: '8px 14px', color: '#e7edf9', fontSize: 12,
                  lineHeight: 1.45, flexShrink: 0,
                }}>
                  {!reasoningUsageConsent ? <label style={{ display: 'flex', gap: 9,
                    alignItems: 'center', textTransform: 'none', letterSpacing: 0,
                    fontWeight: 400, color: '#e7edf9' }}>
                    <input type="checkbox" checked={false}
                      onChange={event => updateUsageConsent(event.target.checked)}
                      aria-label="Confirm WILSY AI usage admission"
                      style={{ width: 18, height: 18, flexShrink: 0, accentColor: '#72b8ff' }}/>
                    <span style={{ textTransform: 'none', letterSpacing: 0, fontWeight: 400,
                      color: '#e7edf9' }}>Allow AI usage for this conversation</span>
                  </label> : null}
                  <details style={{ marginTop: 3, paddingLeft: reasoningUsageConsent ? 0 : 27,
                    color: '#cbd5e1', fontWeight: 400, textTransform: 'none',
                    letterSpacing: 0 }}>
                    <summary style={{ cursor: 'pointer', minHeight: 28, fontSize: 12,
                      textTransform: 'none', letterSpacing: 0, color: '#cbd5e1' }}>
                      {reasoningUsageConsent ? 'AI usage preferences' : 'Usage and permissions'}
                    </summary>
                    <p style={{ margin: '4px 0' }}>Each request may consume metered AI usage.
                      EOS checks your permissions, subscription entitlement and capacity.
                      For a verified project, EOS may send bounded project and task
                      excerpts to its configured AI provider to answer. Consent does not
                      authorize project changes, staffing decisions or payments.</p>
                    {reasoningUsageConsent && <button type="button"
                      onClick={() => updateUsageConsent(false)}
                      aria-label="Revoke AI usage consent"
                      style={{ minHeight: 36, color: '#e7edf9', textDecoration: 'underline',
                        textTransform: 'none', fontSize: 12 }}>
                      Revoke AI usage consent
                    </button>}
                  </details>
                </div>}
                <div className={styles.chatInputArea} style={{ flexShrink: 0 }}>
                  <textarea
                    className={styles.promptInput}
                    value={prompt}
                    onChange={(e) => setPrompt(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault();
                        handleSendMessage();
                      }
                    }}
                    placeholder="Ask Wilsy OS…"
                    rows={2}
                    disabled={isSubmitting}
                  />
                  <button
                    type="button"
                    className={styles.sendButton}
                    onClick={() => handleSendMessage()}
                    disabled={isSubmitting || !prompt.trim()
                      || (!isLegalDockRole(authUser?.role)
                        && !readOnlySourceIntent && !localCourtesyIntent
                        && (!reasoningUsageConsent || aiEntitlementNotProvisioned || aiProviderUnavailable
                          || (reasoningReplayRef.current.blocked === true
                            && reasoningReplayRef.current.scope === dockScopeRef.current
                            && reasoningReplayRef.current.text === prompt.trim()
                            && reasoningReplayRef.current.locatorKey === workLocatorKeyRef.current)))}
                    aria-label="Send"
                  >
                    <SendHorizontal size={18} />
                  </button>
                </div>
              </div>
            )}

            {activeTab === 'legalAdvisory' && isLegalDockRole(authUser?.role) && (
              <div className={styles.legalAdvisoryTab}>
                <div className={styles.legalAdvisoryHeader}>
                  <div>
                    <span className={styles.legalAdvisoryEyebrow}>Legal Advisory</span>
                    <h4>Evidence-backed Legal Advisory</h4>
                  </div>
                  <ShieldCheck size={22} aria-hidden="true" />
                </div>
                <p className={styles.legalAdvisoryNotice}>
                  Evidence-backed advisory · No execution authority
                </p>
                <div className={styles.legalAdvisoryPrompt}>
                  <label htmlFor="legal-advisory-prompt">Legal-service question</label>
                  <textarea
                    id="legal-advisory-prompt"
                    aria-label="Legal advisory prompt"
                    value={legalPrompt}
                    onChange={(event) => setLegalPrompt(event.target.value)}
                    placeholder="Describe the legal-service question…"
                    rows={4}
                    disabled={legalSubmitting}
                  />
                  <button
                    type="button"
                    className={styles.legalAdvisoryGenerate}
                    onClick={handleGenerateLegalAdvisory}
                    disabled={legalSubmitting || !legalPrompt.trim()}
                  >
                    <FileCheck2 size={16} />
                    {legalSubmitting ? 'Generating evidence-backed next action…' : 'Generate evidence-backed next action'}
                  </button>
                </div>

                {legalError && (
                  <div className={styles.legalAdvisoryError} role="alert" aria-live="assertive">
                    {legalError}
                  </div>
                )}

                {legalServiceResponse && (
                  <section className={styles.legalServiceResponse} aria-live="polite">
                    <h5>Legal service response</h5>
                    <p>{formatAdvisoryValue(legalServiceResponse.response_text)}</p>
                    <div className={styles.legalAdvisoryGrid}>
                      <div className={styles.legalAdvisoryField}>
                        <small>Orchestration ID</small>
                        <strong>{formatAdvisoryValue(legalServiceResponse.orchestration_id)}</strong>
                      </div>
                      <div className={styles.legalAdvisoryField}>
                        <small>Outcome</small>
                        <strong>{formatAdvisoryValue(legalServiceResponse.outcome)}</strong>
                      </div>
                    </div>
                    {Array.isArray(legalServiceResponse.sources) && legalServiceResponse.sources.length > 0 && (
                      <ul className={styles.legalAdvisorySourceList}>
                        {legalServiceResponse.sources.map((source, index) => (
                          <li key={`${formatAdvisoryValue(source)}-${index}`}>{formatAdvisoryValue(source)}</li>
                        ))}
                      </ul>
                    )}
                    {legalServiceResponse.outcome !== 'TOOL_ASSISTED' && (
                      <strong className={styles.legalAdvisoryNotGenerated}>
                        Evidence-backed advisory not generated
                      </strong>
                    )}
                  </section>
                )}

                {legalAdvisory && (
                  <section className={styles.legalAdvisoryCard} aria-label="Evidence-backed advisory">
                    <div className={styles.legalAdvisoryCardHeader}>
                      <div>
                        <span className={styles.legalAdvisoryEyebrow}>Evidence-backed advisory</span>
                        <h5>{formatAdvisoryValue(legalAdvisory.title)}</h5>
                      </div>
                      <span
                        className={`${styles.legalAdvisoryStatus} ${
                          legalStatus === 'STALE'
                            ? styles.legalAdvisoryStatusStale
                            : styles.legalAdvisoryStatusCurrent
                        }`}
                      >
                        {formatAdvisoryValue(legalAdvisory.status)}
                      </span>
                    </div>
                    <p className={styles.legalAdvisoryNoAuthority}>
                      Evidence-backed advisory · No execution authority
                    </p>
                    <div className={styles.legalAdvisoryGrid}>
                      <div className={styles.legalAdvisoryField}><small>Advisory ID</small><strong>{formatAdvisoryValue(legalAdvisory.advisory_id)}</strong></div>
                      <div className={styles.legalAdvisoryField}><small>Scope reference</small><strong>{formatAdvisoryValue(legalAdvisory.scope_ref)}</strong></div>
                      <div className={styles.legalAdvisoryField}><small>Rationale</small><strong>{formatAdvisoryValue(legalAdvisory.rationale)}</strong></div>
                      <div className={styles.legalAdvisoryField}><small>Confidence score</small><strong>{formatConfidenceScore(legalAdvisory.confidence_score)}</strong></div>
                      <div className={styles.legalAdvisoryField}><small>Confidence basis</small><strong>{formatAdvisoryValue(legalAdvisory.confidence_basis)}</strong></div>
                      <div className={styles.legalAdvisoryField}><small>Risk level</small><strong>{formatAdvisoryValue(legalAdvisory.risk_level)}</strong></div>
                      <div className={styles.legalAdvisoryField}><small>Generated at</small><strong>{formatAdvisoryValue(legalAdvisory.generated_at)}</strong></div>
                      <div className={styles.legalAdvisoryField}><small>Superseded by advisory ID</small><strong>{formatAdvisoryValue(legalAdvisory.superseded_by_advisory_id)}</strong></div>
                    </div>
                    <div className={styles.legalAdvisoryActions}>
                      <button type="button" className={styles.legalAdvisoryRefresh} onClick={handleRefreshLegalAdvisory} disabled={legalRefreshing}>
                        {legalRefreshing ? 'Refreshing status…' : 'Refresh status'}
                      </button>
                      {legalAdvisory.superseded_by_advisory_id && (
                        <button type="button" className={styles.legalAdvisoryRefresh} onClick={() => handleViewSuccessor(legalAdvisory.superseded_by_advisory_id)} disabled={legalRefreshing}>
                          <ArrowUpRight size={15} /> View successor
                        </button>
                      )}
                      <button type="button" className={styles.legalAdvisoryClear} onClick={clearLegalAdvisoryView}>
                        Clear local view
                      </button>
                    </div>
                  </section>
                )}
              </div>
            )}

            {activeTab === 'deadlineIntelligence' && isLegalDockRole(authUser?.role) && (
              <div className={styles.legalAdvisoryTab}>
                <div className={styles.legalAdvisoryHeader}>
                  <div>
                    <span className={styles.legalAdvisoryEyebrow}>Core Legal observation</span>
                    <h4>Matter deadline posture</h4>
                  </div>
                  <ShieldCheck size={22} aria-hidden="true" />
                </div>
                <p className={styles.legalAdvisoryNotice}>
                  Observed canonical deadline posture · Not legal advice or a recommendation
                </p>
                <div className={styles.legalAdvisoryPrompt}>
                  <label htmlFor="deadline-intelligence-matter">Matter identifier</label>
                  <input
                    id="deadline-intelligence-matter"
                    aria-label="Matter identifier for deadline observation"
                    value={deadlineMatterId}
                    onChange={(event) => setDeadlineMatterId(event.target.value)}
                    placeholder="Enter the exact matter identifier"
                    disabled={deadlineLoading}
                  />
                  <button
                    type="button"
                    className={styles.legalAdvisoryGenerate}
                    onClick={handleObserveDeadlines}
                    disabled={deadlineLoading || !deadlineMatterId.trim()}
                  >
                    <FileCheck2 size={16} />
                    {deadlineLoading ? 'Observing canonical deadlines…' : 'Observe deadline posture'}
                  </button>
                </div>
                {deadlineError && (
                  <div className={styles.legalAdvisoryError} role="alert" aria-live="assertive">
                    {deadlineError}
                  </div>
                )}
                {deadlineIntelligence && (
                  <section className={styles.legalAdvisoryCard} aria-label="Matter deadline observation">
                    <div className={styles.legalAdvisoryCardHeader}>
                      <div>
                        <span className={styles.legalAdvisoryEyebrow}>Observed at</span>
                        <h5>{formatAdvisoryValue(deadlineIntelligence.observedAt)}</h5>
                      </div>
                      <span className={styles.legalAdvisoryStatus}>READ ONLY</span>
                    </div>
                    <p className={styles.legalAdvisoryNoAuthority}>
                      No legal-period calculation · No court-rule inference · No reminder or execution authority
                    </p>
                    <div className={styles.legalAdvisoryGrid}>
                      <div className={styles.legalAdvisoryField}><small>Upcoming</small><strong>{deadlineIntelligence.upcomingCount}</strong></div>
                      <div className={styles.legalAdvisoryField}><small>Due</small><strong>{deadlineIntelligence.dueCount}</strong></div>
                      <div className={styles.legalAdvisoryField}><small>Overdue</small><strong>{deadlineIntelligence.overdueCount}</strong></div>
                      <div className={styles.legalAdvisoryField}><small>Inactive</small><strong>{deadlineIntelligence.inactiveCount}</strong></div>
                    </div>
                    {deadlineIntelligence.items.length === 0 ? (
                      <p>No canonical deadline facts were returned for this authorized matter.</p>
                    ) : (
                      <ul className={styles.legalAdvisorySourceList}>
                        {deadlineIntelligence.items.map((item) => (
                          <li key={item.deadlineId}>
                            <strong>{item.temporalPosture}</strong>
                            {' · '}{item.deadlineKind}{' · due '}{item.dueAt}
                            {' · '}{item.jurisdictionReference}
                          </li>
                        ))}
                      </ul>
                    )}
                  </section>
                )}
              </div>
            )}

            {activeTab === 'history' && (
              <div className={styles.historyTabContent}>
                <div className={styles.historyHeaderRow}>
                  <div><h4>Conversations</h4><p style={{ color: '#aebed2', fontSize: 12, marginTop: 4 }}>
                    {wilsyAIConversationHistoryPosture() === 'READY'
                      ? 'Encrypted history is stored by Python EOS for 30 days. Saved transcripts are not live source verification.'
                      : 'EOS saved history is unavailable. Current conversations are session-only and may disappear on refresh.'}
                  </p></div>
                  <div className={styles.historyHeaderActions}>
                    <button type="button" className={styles.historyActionButton} onClick={handleNewThread}>+ New</button>
                    <button type="button" className={styles.historyActionButton} onClick={handleRefresh}>Refresh history</button>
                    <button
                      type="button"
                      className={styles.clearHistoryButton}
                      onClick={async () => {
                        const scope = dockScopeRef.current;
                        try {
                          await clearWilsyAIConversationThreads();
                          const fresh = await createWilsyAIConversationThread({
                            title: 'New Sovereign Session', workspace: 'WILSY OS',
                          });
                          if (scope !== dockScopeRef.current) return;
                          setConversationThreads([fresh]);
                          setActiveThreadId(fresh.id);
                          setActiveTab('chat');
                        } catch {
                          if (scope === dockScopeRef.current) {
                            setErrorMessage('Session history could not be reset. No completed reset is being claimed.');
                          }
                        }
                      }}
                    >
                      Clear session
                    </button>
                  </div>
                </div>
                <div className={styles.threadsList}>
                  {conversationThreads.filter(thread => (thread.messages?.length || 0) > 0).length === 0
                    && <p style={{ color: '#cbd5e1', lineHeight: 1.6 }}>
                      No conversation messages are available in this view. Refresh history to verify the current EOS archive.
                    </p>}
                  {historyOperationError && <p role="alert" style={{ color: '#ffccba', fontSize: 12 }}>
                    {historyOperationError}
                  </p>}
                  {conversationThreads.filter(thread => (thread.messages?.length || 0) > 0).map((thread) => (
                    <div key={thread.id} style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                      <button type="button"
                        className={`${styles.threadCard} ${
                          thread.id === activeThreadId ? styles.activeThreadCard : ''
                        }`}
                        style={{ flex: 1, minWidth: 0 }}
                        onClick={() => { setAnimatedAssistantKey(null); setActiveThreadId(thread.id); setConversationView('WELCOME'); setActiveTab('chat'); }}
                      >
                        <MessageSquareText size={16} />
                        <div>
                          <h5>{thread.title || 'Conversation'}</h5>
                          <span>{thread.messages?.length || 0} messages · {
                            thread.storagePosture === 'EOS_ENCRYPTED_HISTORY'
                              ? 'Saved in EOS' : 'Session only'
                          }</span>
                        </div>
                      </button>
                      <button type="button" className={styles.historyActionButton}
                        aria-label={`Delete conversation ${thread.title || 'Conversation'}`}
                        style={{ minHeight: 40, padding: '6px 10px' }}
                        onClick={async () => {
                          if (!window.confirm('Delete this conversation from WILSY OS history? This cannot be undone.')) return;
                          const scope = dockScopeRef.current;
                          setHistoryOperationError('');
                          try {
                            const remaining = await deleteWilsyAIConversationThread(thread.id);
                            if (scope !== dockScopeRef.current) return;
                            setConversationThreads(remaining);
                            if (activeThreadId === thread.id) {
                              setActiveThreadId(remaining[0]?.id || null);
                            }
                          } catch {
                            if (scope === dockScopeRef.current) {
                              setHistoryOperationError('EOS could not verify deletion. The conversation was not removed.');
                            }
                          }
                        }}>Delete</button>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </section>
      )}
    </div>
  );
}

export default WilsyOSIntelligenceDock;

/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * INSTITUTIONAL ARTIFACT SEAL — Intelligence Dock v4.17.0-FOUNDER-INSTITUTIONAL-ACTIVATION-ACTION
 * ═══════════════════════════════════════════════════════════════════════════════
 * General Ask uses Python EOS /wilsy-ai/reasoning with explicit consent and admission;
 * legal roles retain separately certified C1C legal-services transport.
 * Phase 4.1 complete: "New Thread" & manual "Refresh/Sync" UX added.
 * Phase 4.1.1 complete: CSS classes for action buttons formally integrated.
 * M14-P7 complete: optional billing-intelligence evidence remains a separate
 * server-returned canonical projection and is explicitly named in operator context.
 * The dock now uses the sovereign Kennel for all intelligence generation.
 * C1E-R1C complete: legal advisories remain server-owned, read-only projections;
 * no legal command, execution, financial authority, or browser persistence exists.
 * D6B complete: Core Legal deadline posture is an independent read-only D6
 * projection and does not require or enlarge WILSY AI entitlement or authority.
 * Durable history is stored only by Python EOS when authenticated, keyed and available; fallback remains session-only.
 * ═══════════════════════════════════════════════════════════════════════════════
 * ARTIFACT: WilsyOSIntelligenceDock.jsx
 * VERSION: v4.50.0-EOS-ENCRYPTED-HISTORY-UX
 * AUTHORITY BOUNDARY: client projection only; Python EOS owns C1C/C1E truth
 * TENANT POSTURE: authenticated api.js context; C1E state is React memory only
 * FAIL-CLOSED POSTURE: transport errors render bounded status and never fabricate
 * FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
