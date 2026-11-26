/**
 * TITLE: WILSY OS Permissioned Dock Operating Journey
 * VERSION: v1.6.1-IN-APP-WORK-FOCUS
 * AUTHORITY: WILSY OS Core Governance; Python EOS and Projects own source truth.
 * EPITOME: Advance authorized work through verified commands and editable plan evidence.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/components/intelligence/WilsyDockOperatingWork.jsx
 * COLLABORATION / OWNERSHIP: Intelligence Dock, closed catalog, My Work, Projects.
 * CERTIFICATION / UPDATE DATE: 2026-11-26
 * CHANGELOG: v1.6.1-IN-APP-WORK-FOCUS minimizes the Dock on an ordinary internal work navigation so the destination task receives the screen, preserving modifier-key copy/new-tab interactions and all original task authorization checks.
 * CHANGELOG: v1.6.0-IN-APP-WORK-NAVIGATION uses React Router for in-app EOS work links to avoid restarting authentication/tenant bootstrap on every Open; keeps accessible real anchors, modifier-key browser behavior, destination reauthorization and non-router test compatibility.
 * CHANGELOG: v1.5.0-MW-T11-QUIET-TENANT-NEUTRAL-WORK reduces task-title visual weight and uses compact neutral sentence-case source metadata for every tenant; exact EOS source order, priority, overdue date and authorized navigation remain unchanged.
 * CHANGELOG: v1.4.0-MW-T11-SCANNABLE-SOURCE-WORK replaces repeated technical ranking prose with a quiet numeric EOS-order position and readable secondary source/priority/date, preserving full canonical ranking explanation in the row title and exact task selection semantics. No source rank recomputation, action authority or approval inference.
 * CHANGELOG: v1.3.0-MW-T11-SOURCE-RANKED-HANDOFF displays EOS's authorized source identity and returned work order with priority/deadline evidence, then confirms the selected Projects task binding before independent Projects reauthorization on navigation. Neither source ordering nor status is inferred.
 * CHANGELOG: v1.2.0-REHYDRATED-COMMAND-STATE makes pending-command restoration a React state change, preserving fail-closed receipt-only reconciliation across a full browser reload.
 * CHANGELOG: v1.1.0 replaces repeated Open work cards with full-row, source-aware navigation and an explicit complete-queue link.
 * CHANGELOG: v1.0.0 adds briefs, ranked actions, deterministic drafts and read-only reconciliation.
 * COMPLIANCE: AGENTS.md; POPIA section 19; GDPR Article 32; SOC2 CC7.2; keyboard controls.
 * SECURITY / PRIVACY POSTURE: No executable task text, provider calls or transcript browser storage.
 * TENANT BOUNDARY: Exact principal/tenant/capacity generation on every asynchronous result.
 * AUTHORITY BOUNDARY: No optimistic lifecycle truth; uncertain writes cannot be resubmitted.
 * FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively.
 */
import React, { useCallback, useEffect, useLayoutEffect, useRef, useState } from 'react';
import { Link, useInRouterContext } from 'react-router-dom';
import { sha3_512 } from 'js-sha3';
import api from '../../services/api.js';
import { assertUnifiedMyWorkProjection } from '../../services/unifiedMyWorkProjection.js';
import { assertDockEnvelope, draftDockPlan, createDockPlanPdf, dockTaskPath } from './wilsyDockContract.js';
import styles from './WilsyOSIntelligenceDock.module.css';

// Pending command identities survive normal component navigation, but never
// confer authority. Each reconciliation requires current EOS IAM again. Keys
// are unverified continuity metadata; no task text, tokens or transcripts enter browser storage.
const pendingCommands = new Map();
const pendingArtifacts = new Map();
const pendingProviderDrafts = new Map();

// Internal EOS work navigation belongs to the currently mounted SPA Router.
// Keep real href semantics for copied URLs and modifier keys; when the component
// is embedded in an isolated test without Router, retain a normal anchor.
function DockWorkLink({ href, children, onNavigate, ...props }) {
  const inRouter = useInRouterContext();
  const handleClick = event => {
    if (!event.defaultPrevented && event.button === 0
      && !event.metaKey && !event.ctrlKey && !event.shiftKey && !event.altKey) {
      onNavigate?.();
    }
  };
  return inRouter
    ? <Link to={href} onClick={handleClick} {...props}>{children}</Link>
    : <a href={href} onClick={handleClick} {...props}>{children}</a>;
}

// Preserve the exact position supplied by EOS. Show only useful secondary
// facts in the row; the accessible row title preserves the source explanation.
// Never infer a date, overdue state, rank algorithm or executable authority.
const rankedSourceReason = (item, rank) => {
  const source = typeof item.source === 'string' ? item.source : 'Unknown source';
  const displaySource = ({
    PROJECTS: 'Projects', CRM: 'CRM', HR: 'HR', LEGAL: 'Legal',
    OPERATIONS: 'Operations', INTELLIGENCE: 'Intelligence',
  })[source] || source;
  const priority = typeof item.priority === 'string'
    ? item.priority.toLowerCase() : 'unverified';
  const date = typeof item.due_date === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(item.due_date)
    ? item.due_date
    : typeof item.due_at === 'string' && Number.isFinite(Date.parse(item.due_at))
      ? item.due_at.slice(0, 10) : null;
  const status = item.is_overdue === true ? 'Overdue' : null;
  return {
    short: [displaySource, priority, status || (date ? 'Due ' + date : null)]
      .filter(Boolean).join(' · '),
    explanation: 'Position ' + rank + ' in the current EOS-authorized My Work response. '
      + source + ' source, ' + priority + ' priority, '
      + (date ? 'deadline ' + date : 'no deadline supplied')
      + ', overdue ' + (item.is_overdue === true ? 'verified' : 'not indicated') + '. '
      + 'WILSY OS does not independently rank these records.',
  };
};
const continuityKey = (kind, key) => 'wilsy.dock.pending.v1:' + kind + ':' + sha3_512(key);
const rememberPending = (kind, key, attempt) => {
  // This is only an unverified command locator, never transcript or source
  // authority. Keep its opaque key across a refresh without storing draft bytes.
  const metadata = { key: attempt.key, source: attempt.source,
    ...(kind === 'task' ? { target: attempt.target } : { id: attempt.id,
      pdf: { digest: attempt.pdf.digest, filename: attempt.pdf.filename, size: attempt.pdf.size } }) };
  sessionStorage.setItem(continuityKey(kind, key), JSON.stringify(metadata));
};
const forgetPending = (kind, key) => {
  try { sessionStorage.removeItem(continuityKey(kind, key)); }
  catch { /* A retained locator is harmless: EOS must independently reauthorize reconciliation. */ }
};
const restorePending = (kind, key, locator) => {
  const raw = sessionStorage.getItem(continuityKey(kind, key));
  if (!raw) return null;
  if (raw.length > 4096) throw new Error('DOCK_COMMAND_CONTINUITY_INVALID');
  const attempt = JSON.parse(raw);
  if (!attempt || !/^[a-f0-9-]{36}$/.test(attempt.key || '')
    || attempt.source?.project_id !== locator.project_id || attempt.source?.task_id !== locator.task_id
    || attempt.source?.participant_view !== Boolean(locator.participant_view)) throw new Error('DOCK_COMMAND_CONTINUITY_INVALID');
  dockTaskPath(attempt.source); // Same strict source shape used by canonical navigation.
  if (kind === 'task' && !['IN_PROGRESS', 'DONE'].includes(attempt.target)) throw new Error('DOCK_COMMAND_CONTINUITY_INVALID');
  if (kind === 'artifact' && (!/^pat-[a-f0-9]{48}$/.test(attempt.id || '')
    || !/^[a-f0-9]{128}$/.test(attempt.pdf?.digest || '') || !Number.isSafeInteger(attempt.pdf?.size)
    || attempt.pdf.size <= 0 || typeof attempt.pdf.filename !== 'string' || attempt.pdf.filename.length > 255)) {
    throw new Error('DOCK_COMMAND_CONTINUITY_INVALID');
  }
  return attempt;
};

const sourceLocator = source => ({ workspace: 'PROJECTS', project_id: source.project_id,
  task_id: source.task_id, participant_view: source.participant_view });
const taskBase = source => '/projects/' + encodeURIComponent(source.project_id)
  + (source.participant_view ? '/my-project' : '') + '/tasks/' + encodeURIComponent(source.task_id);
const scoped = (data, tenantId, principalId, source) => data?.tenant_id === tenantId
  && data.principal_id === principalId && data.project_id === source.project_id;
const issue = error => error?.response?.status === 403 ? 'Current EOS authority denied this operation.'
  : error?.response?.status === 401 ? 'Your session expired. Sign in and verify again.'
    : error?.response?.status === 409 ? 'The source changed. Refresh the task before acting.'
      : 'EOS could not verify this operation. Retry the source read.';

/**
 * @description Render only validated inert catalog components; unknown types fail safely.
 * @collaboration Dock catalog and artifact workflow; actions are bound by the host.
 * @institutional Model or historical text cannot introduce an executable component.
 * @returns Accessible source text; no mutation, permission or financial execution.
 */
export function DockInertComponent({ component, source }) {
  switch (component?.type) {
    case 'Checklist': return <ul>{component.items.map((item, index) => <li key={index}><label><input type="checkbox"/> {item}</label></li>)}</ul>;
    case 'PlainText': return <p>{component.text}</p>;
    case 'StatusBanner': return <p role="status">{component.text}</p>;
    case 'ApprovalCard': return <p>{component.text} <a href={dockTaskPath(source)}>Review in task approvals</a></p>;
    case 'ArtifactFrame': return <article><h4>{component.title}</h4><p>{component.state.toLowerCase()}</p><pre>{component.content}</pre></article>;
    default: return <p role="alert">This component is unavailable.</p>;
  }
}

/**
 * @description Operate exact authorized task context or a bounded ranked My Work feed.
 * @collaboration Parent Dock owns transcript and navigation scope; EOS owns every read/write.
 * @institutional Receipt evidence precedes independent current-state readback and UI success.
 * All command identities are stable through uncertainty. Session changes invalidate
 * presentation and cancel reads; they never attempt to undo or replay a possible write.
 * @returns Accessible TaskBrief, ActionList and one replaceable ArtifactFrame.
 */
export default function WilsyDockOperatingWork({ tenantId, principalId, scope, locator,
  refresh = 0, providerReady = false, usageConsent = false, onVerified, onRecord, onSelectWork, onNavigateWork }) {
  const identity = JSON.stringify([scope, locator.project_id || '', locator.task_id || '', Boolean(locator.participant_view)]);
  const [view, setView] = useState({ identity, state: 'LOADING' });
  const [notice, setNotice] = useState('');
  const [artifact, setArtifact] = useState(null);
  const [busy, setBusy] = useState(false);
  const [continuityBlocked, setContinuityBlocked] = useState(false);
  const [pendingCommand, setPendingCommand] = useState(null);
  const [retry, setRetry] = useState(0);
  const current = useRef(identity);
  const generation = useRef(0);
  const lock = useRef(null);
  const accepted = useRef(null);
  const callbacks = useRef({ onVerified, onRecord, onSelectWork, onNavigateWork });
  callbacks.current = { onVerified, onRecord, onSelectWork, onNavigateWork };
  const hasTask = locator.workspace === 'PROJECTS' && Boolean(locator.task_id);
  const pendingKey = JSON.stringify([scope, locator.project_id, locator.task_id]);
  const isCurrent = token => current.current === identity && generation.current === token;
  useLayoutEffect(() => {
    current.current = identity; generation.current += 1;
    try {
      const taskAttempt = restorePending('task', pendingKey, locator);
      if (taskAttempt) pendingCommands.set(pendingKey, taskAttempt);
      else pendingCommands.delete(pendingKey);
      // Storage restoration must notify React; a module Map alone cannot
      // reliably expose the reconciliation action after a full page reload.
      setPendingCommand(taskAttempt);
      const artifactAttempt = restorePending('artifact', pendingKey, locator);
      if (artifactAttempt && !pendingArtifacts.has(pendingKey)) {
        pendingArtifacts.set(pendingKey, { ...artifactAttempt, artifact: { type: 'ArtifactFrame', id: 'task-plan',
          source: artifactAttempt.source, title: 'Pending plan attachment', content: '',
          provenance: 'DETERMINISTIC_DRAFT', state: 'UNVERIFIED' } });
      }
      const previousAttempt = pendingArtifacts.get(pendingKey);
      setArtifact(previousAttempt?.artifact || null); accepted.current = previousAttempt || null;
      setContinuityBlocked(false);
      setNotice(previousAttempt ? 'Attachment outcome unverified. Reconcile the existing PDF.' : '');
    } catch {
      setContinuityBlocked(true); setPendingCommand(null); setArtifact(null); accepted.current = null;
      setNotice('Command continuity metadata is unavailable. Verify this task in Projects before another Dock write.');
    }
    lock.current = null; setBusy(false);
    return () => { generation.current += 1; };
  }, [identity]);

  const readTask = useCallback(async (signal, exactRevision = false) => {
    const params = { ...locator };
    if (!exactRevision) { delete params.task_revision; delete params.project_revision; }
    const response = await api.get('/wilsy-ai/dock/context', {
      params, headers: { 'X-Tenant-ID': tenantId }, signal, timeout: 15000, forceNetworkRetry: true,
    });
    return assertDockEnvelope(response?.data, { tenantId, principalId, locator: params });
  }, [identity, tenantId, principalId, locator.task_revision, locator.project_revision]);

  useEffect(() => {
    const controller = new AbortController();
    const token = generation.current;
    let live = true;
    setView({ identity, state: 'LOADING' });
    const load = async () => {
      try {
        const data = hasTask ? await readTask(controller.signal, !retry && !refresh)
          : assertUnifiedMyWorkProjection((await api.get('/my-work', {
            headers: { 'X-Tenant-ID': tenantId }, signal: controller.signal,
            timeout: 15000, forceNetworkRetry: true,
          }))?.data, { tenantId, principalId });
        if (!live || !isCurrent(token) || controller.signal.aborted) return;
        setView({ identity, state: 'READY', data });
      } catch (error) {
        if (live && isCurrent(token) && !controller.signal.aborted) {
          setView({ identity, state: 'UNAVAILABLE', message: issue(error) });
        }
      }
    };
    void load();
    return () => { live = false; controller.abort(); };
  }, [identity, refresh, retry, readTask, tenantId, principalId, hasTask]);

  const ready = view.identity === identity && view.state === 'READY';
  const envelope = ready && hasTask ? view.data : null;
  const brief = envelope?.components.find(item => item.type === 'TaskBrief');
  const actions = envelope?.components.find(item => item.type === 'ActionList')?.actions || [];
  const pending = pendingCommand;
  // Only a currently admitted EOS Dock source can confirm the selected work
  // identity. The link itself remains an untrusted navigation hint and the
  // Projects workspace independently checks IAM and durable task source.
  const handoffConfirmed = Boolean(ready && hasTask && envelope
    && envelope.source.project_id === locator.project_id
    && envelope.source.task_id === locator.task_id
    && (locator.task_revision === undefined || envelope.source.revision === locator.task_revision));
  const record = async (content, token) => {
    if (!isCurrent(token)) return;
    try {
      await callbacks.current.onRecord?.(content, sourceLocator(envelope.source));
    } catch {
      if (isCurrent(token)) setNotice(previous => previous + ' Conversation save is unverified.');
    }
  };
  const verifyCommand = async (command, token) => {
    if (!isCurrent(token)) throw new Error('DOCK_SESSION_CHANGED');
    const receipt = await api.get(taskBase(command.source) + '/transition-receipt', {
      params: { expected_revision: command.source.revision, target_status: command.target },
      headers: { 'X-Tenant-ID': tenantId, 'Idempotency-Key': command.key },
      timeout: 15000, forceNetworkRetry: true,
    });
    const result = receipt?.data;
    if (result?.schema !== 'WILSY-PROJECT-TASK-RESULT/V1' || !scoped(result, tenantId, principalId, command.source)
      || result.task?.task_id !== command.source.task_id || result.task.tenant_id !== tenantId
      || result.task.project_id !== command.source.project_id || result.task.status !== command.target
      || result.task.revision !== command.source.revision + 1
      || !/^[a-f0-9]{128}$/.test(result.task.fingerprint || '')) throw new Error('DOCK_RECEIPT_UNVERIFIED');
    if (!isCurrent(token)) throw new Error('DOCK_SESSION_CHANGED');
    const fresh = await readTask();
    if (fresh.source.revision < result.task.revision
      || (fresh.source.revision === result.task.revision && fresh.source.fingerprint !== result.task.fingerprint)) {
      throw new Error('DOCK_READBACK_UNVERIFIED');
    }
    return fresh;
  };

  const transition = async (action, reconcile = false) => {
    if (lock.current || continuityBlocked || (!reconcile && pendingCommands.has(pendingKey))) return;
    const command = reconcile ? pendingCommands.get(pendingKey) : {
      key: globalThis.crypto.randomUUID(), source: { ...action.source }, target: action.execution.target_status,
    };
    if (!command) return;
    if (!reconcile && !window.confirm(`${action.outcome} in EOS? Current task rules and permissions will be checked.`)) return;
    const token = generation.current;
    const operationLock = {}; lock.current = operationLock; setBusy(true);
    setNotice(reconcile ? 'Reconciling existing command evidence…' : 'Verifying current task authority…');
    let posted = reconcile;
    let commandAccepted = reconcile;
    try {
      if (!reconcile) {
        const fresh = await readTask();
        if (!isCurrent(token)) return;
        const admitted = fresh.components.find(item => item.type === 'ActionList')?.actions
          .find(item => item.id === action.id && item.verified_revision === command.source.revision);
        if (!admitted || fresh.source.fingerprint !== command.source.fingerprint) {
          setView({ identity, state: 'READY', data: fresh });
          setNotice('Task or authority changed. Review the refreshed actions.'); return;
        }
        rememberPending('task', pendingKey, command);
        pendingCommands.set(pendingKey, command);
        setPendingCommand(command);
        posted = true;
        await api.post(taskBase(command.source) + '/transition', {
          expected_revision: command.source.revision, status: command.target,
        }, { headers: { 'X-Tenant-ID': tenantId, 'Idempotency-Key': command.key }, timeout: 15000 });
        commandAccepted = true;
      }
      if (!isCurrent(token)) return;
      const fresh = await verifyCommand(command, token);
      pendingCommands.delete(pendingKey); forgetPending('task', pendingKey);
      if (!isCurrent(token)) return;
      setPendingCommand(null);
      setView({ identity, state: 'READY', data: fresh });
      setNotice('EOS verified the command receipt and independently read the current task.');
      callbacks.current.onVerified?.(fresh.source);
      await record(`EOS verified task command: ${command.target}. Current revision ${fresh.source.revision}.`, token);
    } catch (error) {
      if (!commandAccepted && !reconcile && [400, 401, 403, 404, 409, 422].includes(error?.response?.status)) {
        pendingCommands.delete(pendingKey); forgetPending('task', pendingKey);
        if (isCurrent(token)) setPendingCommand(null);
        if (isCurrent(token)) { setNotice(issue(error)); setRetry(value => value + 1); }
      } else if (isCurrent(token)) {
        setNotice(posted ? 'Command outcome unverified. Reconcile existing command; do not submit another.' : issue(error));
      }
    } finally {
      if (lock.current === operationLock) { lock.current = null; if (isCurrent(token)) setBusy(false); }
    }
  };

  const draft = async (useProvider = providerReady && usageConsent) => {
    if (lock.current || pendingArtifacts.has(pendingKey) || (useProvider && pendingProviderDrafts.has(pendingKey))) return;
    const token = generation.current;
    const operationLock = {}; lock.current = operationLock; setBusy(true);
    try {
      const fresh = await readTask();
      if (!isCurrent(token)) return;
      setView({ identity, state: 'READY', data: fresh });
      let frame = draftDockPlan(fresh);
      if (useProvider) {
        // Only the existing EOS reasoning boundary may admit actual inference.
        // Browser source prose and model-proposed tools are never trusted inputs.
        const attempt = { key: globalThis.crypto.randomUUID(),
          prompt: 'Draft a concise alignment plan and checklist for the independently authorized selected task. Separate source facts from proposals. Do not execute actions or claim attachment, approval or completion.' };
        pendingProviderDrafts.set(pendingKey, attempt);
        setNotice('Generating through the governed EOS provider…');
        const response = await api.post('/wilsy-ai/reasoning', { prompt: attempt.prompt }, {
          params: sourceLocator(fresh.source), headers: { 'X-Tenant-ID': tenantId, 'Idempotency-Key': attempt.key }, timeout: 30000,
        });
        const result = response?.data;
        if (result?.outcome !== 'SUCCESS' || typeof result.response_text !== 'string' || !result.response_text.trim()
          || result.response_text.length > 12000 || typeof result.usage_observation_id !== 'string'
          || !result.usage_observation_id || typeof result.invocation_id !== 'string' || !result.invocation_id) {
          throw new Error('DOCK_PROVIDER_RESULT_UNVERIFIED');
        }
        pendingProviderDrafts.delete(pendingKey);
        if (!isCurrent(token)) return;
        frame = { ...frame, provenance: 'GOVERNED_PROVIDER', content: result.response_text };
      }
      setArtifact(frame); accepted.current = null;
      setNotice(useProvider ? 'EOS returned an admitted model draft. Human review required.'
        : 'Deterministic draft created from current EOS context. No model invoked.');
      await record(`Prepared a ${useProvider ? 'governed model' : 'deterministic'} alignment-plan draft for ${fresh.components[0].title}. Not attached.`, token);
    } catch (error) {
      if (useProvider && [400, 401, 403, 404, 409, 422].includes(error?.response?.status)) pendingProviderDrafts.delete(pendingKey);
      if (isCurrent(token)) setNotice(pendingProviderDrafts.has(pendingKey)
        ? 'Model outcome unverified. No second inference will be submitted. A deterministic draft remains available.' : issue(error));
    }
    finally { if (lock.current === operationLock) { lock.current = null; if (isCurrent(token)) setBusy(false); } }
  };

  const verifyAttachment = async attempt => {
    const base = '/projects/' + encodeURIComponent(attempt.source.project_id)
      + (attempt.source.participant_view ? '/my-project' : '') + '/tasks/' + encodeURIComponent(attempt.source.task_id);
    let offset = 0;
    for (let page = 0; page < 20; page += 1) {
      const response = await api.get(base + '/attachments', { params: { limit: 50, offset },
        headers: { 'X-Tenant-ID': tenantId }, timeout: 15000, forceNetworkRetry: true });
      const data = response?.data;
      if (data?.schema !== 'WILSY-PROJECT-ATTACHMENT-LIST/V1' || !scoped(data, tenantId, principalId, attempt.source)
        || data.task_id !== attempt.source.task_id || !Array.isArray(data.items) || data.items.length > 50
        || data.offset !== offset || data.limit !== 50 || typeof data.has_more !== 'boolean') throw new Error('DOCK_ATTACHMENT_READ_INVALID');
      const found = data.items.find(item => item.attachment_id === attempt.id);
      if (found) {
        if (found.schema !== 'wilsy.project.attachment.v1' || found.tenant_id !== tenantId
          || found.project_id !== attempt.source.project_id || found.task_id !== attempt.source.task_id
          || found.uploader_principal_id !== principalId || found.filename !== attempt.pdf.filename
          || found.content_sha3_512 !== attempt.pdf.digest || found.size_bytes !== attempt.pdf.size
          || found.media_type !== 'application/pdf' || found.state !== 'QUARANTINED' || found.revision !== 1
          || Object.hasOwn(found, 'storage_receipt')) throw new Error('DOCK_ATTACHMENT_MANIFEST_INVALID');
        return found;
      }
      if (!data.has_more || data.next_offset !== offset + data.items.length || !data.items.length) break;
      offset = data.next_offset;
    }
    throw new Error('DOCK_ATTACHMENT_NOT_YET_VERIFIED');
  };

  const attach = async reconcile => {
    if (lock.current || continuityBlocked || !artifact || (!reconcile && accepted.current)) return;
    const token = generation.current;
    let attachmentAccepted = reconcile;
    const operationLock = {}; lock.current = operationLock; setBusy(true);
    try {
      if (!reconcile) {
        const fresh = await readTask();
        if (!isCurrent(token)) return;
        const liveBrief = fresh.components.find(item => item.type === 'TaskBrief');
        if (!liveBrief?.can_attach || fresh.source.fingerprint !== artifact.source.fingerprint) {
          setView({ identity, state: 'READY', data: fresh });
          setNotice('Task revision or attachment authority changed. Review a fresh draft.'); return;
        }
        const pdf = await createDockPlanPdf(artifact);
        if (!isCurrent(token)) return;
        const key = globalThis.crypto.randomUUID();
        const id = 'pat-' + sha3_512([tenantId, artifact.source.project_id, artifact.source.task_id, principalId, key].join('\0')).slice(0, 48);
        accepted.current = { key, id, pdf, source: { ...artifact.source }, artifact: { ...artifact, state: 'UNVERIFIED' } };
        rememberPending('artifact', pendingKey, accepted.current);
        pendingArtifacts.set(pendingKey, accepted.current);
        setArtifact(value => ({ ...value, state: 'ATTACHING' }));
        const body = new FormData(); body.append('file', pdf.blob, pdf.filename);
        await api.post('/projects/' + encodeURIComponent(artifact.source.project_id)
          + '/my-project/tasks/' + encodeURIComponent(artifact.source.task_id) + '/attachments', body,
        { headers: { 'X-Tenant-ID': tenantId, 'Idempotency-Key': key }, timeout: 15000 });
        attachmentAccepted = true;
      }
      const attempt = accepted.current;
      if (!attempt) return;
      if (!isCurrent(token)) return;
      const manifest = await verifyAttachment(attempt);
      if (!isCurrent(token)) return;
      pendingArtifacts.delete(pendingKey); forgetPending('artifact', pendingKey);
      setArtifact(value => ({ ...value, state: 'ATTACHED' }));
      setNotice('EOS independently verified the attached PDF. It remains quarantined pending scan clearance.');
      await record(`Attached alignment-plan PDF verified by EOS: ${manifest.filename}. Quarantined; no scan clearance claimed.`, token);
    } catch (error) {
      if (isCurrent(token)) {
        const rejected = !attachmentAccepted && !reconcile && [400, 401, 403, 404, 409, 413, 422].includes(error?.response?.status);
        if (rejected) { accepted.current = null; pendingArtifacts.delete(pendingKey); forgetPending('artifact', pendingKey); }
        setArtifact(value => value ? { ...value, state: rejected ? 'EDITING' : 'UNVERIFIED' } : value);
        setNotice(error?.message === 'WILSY_DOCK_PDF_FONT_UNSUPPORTED'
          ? 'The current PDF font cannot preserve some draft characters. Edit the draft or use the full task document workflow. No upload was attempted.'
          : !accepted.current ? issue(error)
            : rejected ? issue(error) : 'Attachment outcome unverified. Reconcile the existing PDF; no duplicate upload.');
      }
    } finally { if (lock.current === operationLock) { lock.current = null; if (isCurrent(token)) setBusy(false); } }
  };

  return <section className={styles.operatingWork} aria-label={hasTask ? 'Task operating brief' : 'Needs your attention'}>
    {view.identity !== identity || view.state === 'LOADING' ? <p role="status">Checking authorized work…</p>
      : !ready ? <div><p role="status">{view.message || 'Authorized work is unavailable.'}</p>
        <button type="button" onClick={() => setRetry(value => value + 1)}>Retry authorized work</button></div>
        : !hasTask ? <><h4>Needs your attention</h4>
          {view.data.items.length ? <ol className={styles.attentionRows}>{view.data.items.slice(0, 6).map((item, index) =>
            <li key={item.source_key}>
              {(() => {
                const reason = rankedSourceReason(item, index + 1);
                const label = <>
                  <span aria-hidden="true" style={{
                    alignSelf: 'flex-start', paddingTop: 3, flex: '0 0 20px',
                    color: '#8399af', fontSize: 10, fontWeight: 400,
                    fontVariantNumeric: 'tabular-nums',
                  }}>{String(index + 1).padStart(2, '0')}</span>
                  <span className={styles.attentionItemText} style={{ flex: '1 1 auto' }}>
                    <strong style={{ fontSize: 12.5, lineHeight: 1.45, color: '#e5edf7',
                      fontWeight: 540, letterSpacing: 'normal',
                      textTransform: 'none', overflowWrap: 'anywhere' }}>{item.title}</strong>
                    <small style={{ marginTop: 2, color: '#9bafc4',
                      fontSize: 10.5, fontWeight: 400, lineHeight: 1.45,
                      textTransform: 'none', letterSpacing: 'normal' }}>{reason.short}</small>
                  </span>
                  <span className={styles.attentionActionCue} aria-hidden="true" style={{
                    flex: '0 0 auto', fontSize: 11, fontWeight: 450,
                    color: '#a6bed6',
                  }}>{item.source === 'PROJECTS' ? 'Inspect' : 'Open'} <span aria-hidden="true">›</span></span>
                </>;
                const common = { className: styles.attentionItemAction,
                  title: reason.explanation, 'aria-label': item.title + '. ' + reason.explanation,
                  style: { gap: 10, alignItems: 'center', minHeight: 54,
                    padding: '8px 4px', border: 0, background: 'transparent',
                    width: '100%', textAlign: 'left' } };
                return item.source === 'PROJECTS'
                  ? <button type="button" {...common}
                    onClick={() => callbacks.current.onSelectWork?.({
                      workspace: 'PROJECTS', project_id: item.project_id,
                      task_id: item.work_item_id, participant_view: true,
                    })}>{label}</button>
                   : <DockWorkLink {...common} onNavigate={() => callbacks.current.onNavigateWork?.()} href={'/headquarters?section=my-work&work='
                    + encodeURIComponent(item.source_key)}>{label}</DockWorkLink>;
              })()}
            </li>)}</ol>
            : <p>{view.data.sources_included.length ? 'No active work in the verified sources.' : 'No work sources were admitted for this session.'}</p>}
          <div className={styles.attentionFooterActions}>
            <button type="button" onClick={() => setRetry(value => value + 1)}>Refresh work</button>
            <DockWorkLink href="/headquarters?section=my-work" onNavigate={() => callbacks.current.onNavigateWork?.()}>View all in My Work</DockWorkLink>
          </div></>
          : brief && <>
            {handoffConfirmed && <p role="status" aria-label="EOS-confirmed work handoff">
              Projects source verified · revision {envelope.source.revision} · fingerprint checked.
              The Projects workspace independently reauthorizes this record on arrival.
            </p>}
            {!artifact ? <><p className={styles.taskPurpose}>{brief.purpose || 'Review the full task to confirm its intended outcome.'}</p>
              <p>{brief.established}{brief.deadline ? ` Due ${brief.deadline}.` : ''}</p>
              {!!brief.dependencies.length && <p>{brief.dependencies.length} recorded dependencies. Review current source evidence before completion.</p>}
              {!!brief.blockers.length && <ul>{brief.blockers.map(item => <li key={item}>{item}</li>)}</ul>}
              <p className={styles.nextAction}>EOS action order: {actions.map(action => action.outcome).join(' · ')}. Each operation rechecks current source authority.</p>
              <div className={styles.operatingActions} aria-label="Suggested task actions">
                {actions.map(action => action.kind === 'OPEN_TASK' || action.kind === 'REVIEW_EVIDENCE'
                  ? <DockWorkLink key={action.id} onNavigate={() => callbacks.current.onNavigateWork?.()} href={dockTaskPath(action.source, action.kind === 'REVIEW_EVIDENCE')}>{action.outcome}</DockWorkLink>
                  : <button key={action.id} type="button" data-primary={action.priority === 0 ? 'true' : undefined}
                    disabled={busy || (action.execution.operation === 'PROJECT_TASK_TRANSITION' && (continuityBlocked || Boolean(pending)))}
                    onClick={() => action.kind === 'DRAFT_PLAN' ? void draft() : void transition(action)}>{action.kind === 'DRAFT_PLAN' && providerReady && usageConsent ? 'Generate alignment plan' : action.outcome}</button>)}
              </div></> : <div aria-label="Alignment plan artifact" className={styles.artifactFrame}>
              <h4>{artifact.title}</h4><p>{artifact.provenance === 'GOVERNED_PROVIDER' ? 'EOS-admitted model draft' : 'Deterministic draft'} · Task revision {artifact.source.revision} · {artifact.state.toLowerCase()}</p>
              <label htmlFor="dock-plan-content">Edit plan</label>
              <textarea id="dock-plan-content" value={artifact.content} maxLength={12000}
                readOnly={busy || Boolean(accepted.current)} rows={12}
                onChange={event => setArtifact(value => ({ ...value, content: event.target.value, state: 'EDITING' }))}/>
              <div className={styles.operatingActions}>
                {artifact.state !== 'ATTACHED' && <button type="button" data-primary="true"
                  disabled={busy || continuityBlocked || !artifact.content.trim() || !brief.can_attach || Boolean(accepted.current)}
                  onClick={() => void attach(false)}>Accept and attach PDF</button>}
                {artifact.state === 'UNVERIFIED' && accepted.current && <button type="button" disabled={busy}
                  onClick={() => void attach(true)}>Reconcile attachment</button>}
                <button type="button" disabled={busy || (Boolean(accepted.current) && artifact.state !== 'ATTACHED')}
                  onClick={() => { setArtifact(null); accepted.current = null; setNotice(''); }}>{artifact.state === 'ATTACHED' ? 'Back to task' : 'Discard draft'}</button>
              </div>
              {!brief.can_attach && <p>Attachment requires current Projects contributor authority. The draft is not attached.</p>}
            </div>}
          </>}
    {envelope?.components.filter(item => !['TaskBrief', 'ActionList'].includes(item.type)).map(component =>
      <DockInertComponent key={component.id} component={component} source={envelope.source}/>)}
    {pendingProviderDrafts.has(pendingKey) && <button type="button" disabled={busy} onClick={() => void draft(false)}>Draft without AI</button>}
    {pending && <button type="button" disabled={busy} onClick={() => void transition(null, true)}>Reconcile task command</button>}
    {notice && <p role="status" className={styles.operatingNotice}>{notice}</p>}
  </section>;
}

// ARTIFACT: WilsyDockOperatingWork.jsx
// VERSION: v1.6.1-IN-APP-WORK-FOCUS
// AUTHORITY BOUNDARY: presentation and exact-command transport; Python EOS owns truth
// TENANT POSTURE: exact principal, tenant, capacity and request generation
// FAIL-CLOSED POSTURE: uncertain outcomes require read-only reconciliation
// FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
// END OF WILSY OS SOVEREIGN ARTIFACT
