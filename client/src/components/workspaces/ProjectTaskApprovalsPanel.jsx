/**
 * TITLE: WILSY OS Exact-Reviewer Project Business Decisions
 * VERSION: v1.2.1-REVIEWER-REQUEST-SCOPE-GUARD
 * AUTHORITY: Python EOS ProjectApprovalRegistry, participant IAM and audit.
 * EPITOME: Request business review from eligible task contributors, read
 *          source decisions and let only the named reviewer decide once.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/components/workspaces/ProjectTaskApprovalsPanel.jsx
 * COLLABORATION / OWNERSHIP: Owner ProjectTasksPanel or participant AssignedProjects
 *          mounts this shared presentation; EOS alone owns decision truth.
 * CERTIFICATION / UPDATE DATE: 2026-11-18
 * CHANGELOG: v1.2.1-REVIEWER-REQUEST-SCOPE-GUARD avoids
 *          shadowing the scope-ref while validating independently
 *          refreshed contributor responses against the active task.
 * CHANGELOG: v1.2.0-VERIFIED-REVIEWER-DISCOVERY validates
 *          a fresh independently authorized project participant list
 *          before showing eligible distinct reviewers; displays
 *          verified names, never opaque IDs; distinguishes pending,
 *          denied, unavailable and no-independent-reviewer states.
 *          It cannot add roles or approve its own decisions.
 * CHANGELOG: v1.1.0-EXACT-SCAN-CLEARED-REVIEW-PACKET binds explicitly selected, source-verified scan-cleared task attachments to the immutable review packet and independently verified readback; prior rationale-only decisions remain distinct.
 * CHANGELOG: v1.1.0-EXACT-SCAN-CLEARED-REVIEW-PACKET adds independent request,
 *          reviewer decision, revision CAS, source readback and failure states.
 * COMPLIANCE: AGENTS.md; POPIA section 19; GDPR Article 32; WCAG 2.2 AA.
 * SECURITY / PRIVACY POSTURE: Plain text; React escapes all supplied rationale;
 *          in-app review is not a signature, external alert or financial release.
 * TENANT BOUNDARY: Every envelope checked against tenant, project, task and
 *          the authenticated principal; stale session responses ignored.
 * AUTHORITY BOUNDARY: No self approval, IAM creation, task completion, payment
 *          approval or delegation is represented by this client.
 * FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively.
 */
import React, { useCallback, useEffect, useRef, useState } from 'react';
import { Check, ClipboardCheck, RefreshCw, X } from 'lucide-react';
import api from '../../services/api.js';

const APPROVAL = /^par-[a-f0-9]{48}$/;
const ATTACHMENT = /^pat-[a-f0-9]{48}$/;
const SCHEMA = 'wilsy.project.approval.v1';
const LIST = 'WILSY-PROJECT-APPROVAL-LIST/V1';
const RESULT = 'WILSY-PROJECT-APPROVAL-RESULT/V1';

function verified(value, tenantId, projectId, taskId) {
  return Boolean(
    value?.schema === SCHEMA
    && value.tenant_id === tenantId
    && value.project_id === projectId
    && value.task_id === taskId
    && APPROVAL.test(value.approval_id)
    && typeof value.requester_principal_id === 'string'
    && typeof value.reviewer_principal_id === 'string'
    && value.requester_principal_id !== value.reviewer_principal_id
    && typeof value.rationale === 'string' && value.rationale.length > 0
    && ['PENDING', 'APPROVED', 'REJECTED'].includes(value.status)
    && value.revision === (value.status === 'PENDING' ? 1 : 2)
    && (value.status === 'PENDING'
      ? value.decided_at === null && value.decision_rationale === null
      : typeof value.decided_at === 'string'
        && typeof value.decision_rationale === 'string')
    && /^[a-f0-9]{128}$/.test(value.fingerprint || '')
    && (value.evidence_attachment_ids === undefined
      || (Array.isArray(value.evidence_attachment_ids)
        && value.evidence_attachment_ids.length <= 10
        && value.evidence_attachment_ids.every(id => ATTACHMENT.test(id))
        && new Set(value.evidence_attachment_ids).size === value.evidence_attachment_ids.length)),
  );
}

function sameEvidence(left, right) {
  return Array.isArray(left) && Array.isArray(right)
    && left.length === right.length
    && left.every((id, index) => id === right[index]);
}

function verifiedAttachment(item, tenantId, projectId, taskId) {
  return Boolean(
    item?.schema === 'wilsy.project.attachment.v1'
    && item.tenant_id === tenantId && item.project_id === projectId
    && item.task_id === taskId && ATTACHMENT.test(item.attachment_id)
    && typeof item.filename === 'string' && item.filename.length > 0
    && item.filename.length <= 255
    && ['application/pdf', 'image/png', 'image/jpeg'].includes(item.media_type)
    && Number.isSafeInteger(item.size_bytes)
    && item.size_bytes > 0 && item.size_bytes <= 20 * 1024 * 1024
    && /^[a-f0-9]{128}$/.test(item.content_sha3_512 || '')
    && item.state === 'QUARANTINED' && item.revision === 1
    && ['QUARANTINED', 'SCAN_CLEAN_VERIFIED'].includes(item.scan_clearance_status)
    && (item.scan_clearance_status === 'QUARANTINED'
      ? item.scan_clearance_fingerprint === null
      : /^[a-f0-9]{128}$/.test(item.scan_clearance_fingerprint || ''))
    && !Object.hasOwn(item, 'storage_receipt')
    && !Object.hasOwn(item, 'presigned_url')
    && !Object.hasOwn(item, 'download_url'),
  );
}

/** @description Render one auditable exact-task decision workflow. */
export default function ProjectTaskApprovalsPanel({
  tenantId, projectId, principalId, taskId, participants = [],
  tenantHeaders, participantMode = false, onClose, showClose = true, onManageContributors = null,
}) {
  const [state, setState] = useState('LOADING');
  const [items, setItems] = useState([]);
  const [offset, setOffset] = useState(0);
  const [hasMore, setHasMore] = useState(false);
  const [reviewer, setReviewer] = useState('');
  const [rationale, setRationale] = useState('');
  const [evidenceState, setEvidenceState] = useState('CLOSED');
  const [evidenceItems, setEvidenceItems] = useState([]);
  const [selectedEvidence, setSelectedEvidence] = useState([]);
  const [evidenceOffset, setEvidenceOffset] = useState(0);
  const [evidenceMore, setEvidenceMore] = useState(false);
  const [responses, setResponses] = useState({});
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);
  const [reviewerSource, setReviewerSource] = useState('VERIFYING');
  const [verifiedReviewers, setVerifiedReviewers] = useState([]);
  const [reviewerSourceError, setReviewerSourceError] = useState('');
  const scope = [tenantId, projectId, principalId, taskId, participantMode].join('\0');
  const active = useRef(scope);
  active.current = scope;
  const generation = useRef(0);
  const evidenceGeneration = useRef(0);
  const commands = useRef(new Map());
  const headers = tenantHeaders || {};
  const route = '/projects/' + encodeURIComponent(projectId)
    + (participantMode ? '/my-project/tasks/' : '/tasks/')
    + encodeURIComponent(taskId) + '/approvals';
  const evidenceRoute = '/projects/' + encodeURIComponent(projectId)
    + '/tasks/' + encodeURIComponent(taskId) + '/attachments';

  const loadEvidence = async (requestedOffset = 0) => {
    if (participantMode || busy) return;
    const request = ++evidenceGeneration.current;
    const requestScope = scope;
    setEvidenceState('LOADING');
    setSelectedEvidence([]);
    try {
      const { data } = await api.get(
        evidenceRoute + '?limit=50&offset=' + requestedOffset, { headers },
      );
      if (active.current !== requestScope || request !== evidenceGeneration.current) return;
      if (
        data?.schema !== 'WILSY-PROJECT-ATTACHMENT-LIST/V1'
        || data.tenant_id !== tenantId || data.principal_id !== principalId
        || data.project_id !== projectId || data.task_id !== taskId
        || data.limit !== 50 || data.offset !== requestedOffset
        || typeof data.has_more !== 'boolean'
        || !Array.isArray(data.items) || data.items.length > 50
        || (data.has_more && data.items.length === 0)
        || data.next_offset !== (data.has_more ? requestedOffset + data.items.length : null)
        || data.items.some(item => !verifiedAttachment(item, tenantId, projectId, taskId))
        || new Set(data.items.map(item => item.attachment_id)).size !== data.items.length
      ) throw new Error('PROJECT_APPROVAL_EVIDENCE_SOURCE_INVALID');
      setEvidenceItems(data.items);
      setEvidenceOffset(requestedOffset);
      setEvidenceMore(data.has_more);
      setEvidenceState('READY');
    } catch {
      if (active.current !== requestScope || request !== evidenceGeneration.current) return;
      setEvidenceState('UNAVAILABLE');
      setEvidenceItems([]);
      setEvidenceMore(false);
    }
  };

  const load = useCallback(async (requestedOffset = 0) => {
    const request = ++generation.current;
    const requestScope = scope;
    setState('LOADING');
    setError('');
    try {
      const { data } = await api.get(route + '?limit=50&offset=' + requestedOffset, { headers });
      if (request !== generation.current || active.current !== requestScope) return false;
      if (
        data?.schema !== LIST || data.tenant_id !== tenantId
        || data.principal_id !== principalId || data.project_id !== projectId
        || data.task_id !== taskId || data.offset !== requestedOffset
        || data.limit !== 50 || !Array.isArray(data.items)
        || data.items.length > 50 || typeof data.has_more !== 'boolean'
        || (data.has_more && data.items.length === 0)
        || data.next_offset !== (data.has_more ? requestedOffset + data.items.length : null)
        || data.items.some(item => !verified(item, tenantId, projectId, taskId))
        || new Set(data.items.map(item => item.approval_id)).size !== data.items.length
      ) throw new Error('PROJECT_APPROVAL_SOURCE_INVALID');
      setItems(data.items);
      setOffset(requestedOffset);
      setHasMore(data.has_more);
      setState('READY');
      return true;
    } catch (failure) {
      if (request !== generation.current || active.current !== requestScope) return false;
      setItems([]);
      setState([401, 403, 404].includes(failure?.response?.status) ? 'DENIED' : 'UNAVAILABLE');
      setError('EOS could not verify current approval records for this task. Refresh or check access.');
      return false;
    }
  }, [scope, route, tenantId, principalId, projectId, taskId, tenantHeaders]);

  useEffect(() => {
    generation.current += 1;
    setItems([]);
    setResponses({});
    setReviewer('');
    setRationale('');
    setEvidenceState('CLOSED');
    setEvidenceItems([]);
    setSelectedEvidence([]);
    setEvidenceOffset(0);
    setEvidenceMore(false);
    evidenceGeneration.current += 1;
    commands.current.clear();
    void load(0);
    return () => { generation.current += 1; evidenceGeneration.current += 1; };
  }, [scope, load]);

  const send = async (fingerprint, path, payload, approvalId = null) => {
    if (busy || state !== 'READY') return;
    const originalScope = scope;
    let key = commands.current.get(fingerprint);
    if (!key) {
      if (typeof globalThis.crypto?.randomUUID !== 'function') {
        setError('A secure idempotency key is unavailable in this browser.');
        return;
      }
      key = globalThis.crypto.randomUUID();
      commands.current.set(fingerprint, key);
    }
    setBusy(true);
    setError('');
    try {
      const { data } = await api.post(path, payload, {
        headers: { ...headers, 'Idempotency-Key': key },
      });
      if (active.current !== originalScope) return;
      if (
        data?.schema !== RESULT || data.tenant_id !== tenantId
        || data.principal_id !== principalId || data.project_id !== projectId
        || data.task_id !== taskId
        || !verified(data.approval, tenantId, projectId, taskId)
        || (approvalId && data.approval.approval_id !== approvalId)
        || (!approvalId && !sameEvidence(
          data.approval.evidence_attachment_ids || [],
          payload.evidence_attachment_ids || [],
        ))
      ) throw new Error('PROJECT_APPROVAL_RESULT_INVALID');
      const confirmed = await load(0);
      if (!confirmed || active.current !== originalScope) return;
      // Readback is mandatory: confirm the source status/revision, not merely an ACK.
      // A recently created row can be on a later page in an unusually large task;
      // in that case retain the command key and require manual reconciliation.
      const next = await api.get(
        route + '?limit=50&offset=0', { headers },
      );
      if (active.current !== originalScope) return;
      if (
        next?.data?.schema !== LIST || next.data.tenant_id !== tenantId
        || next.data.principal_id !== principalId || next.data.project_id !== projectId
        || next.data.task_id !== taskId || !Array.isArray(next.data.items)
        || !next.data.items.some(item =>
          verified(item, tenantId, projectId, taskId)
          && item.approval_id === data.approval.approval_id
          && item.revision >= data.approval.revision
          && sameEvidence(item.evidence_attachment_ids || [],
            data.approval.evidence_attachment_ids || [])
        )
      ) throw new Error('PROJECT_APPROVAL_READBACK_PENDING');
      commands.current.delete(fingerprint);
      if (!approvalId) {
        setReviewer(''); setRationale(''); setSelectedEvidence([]);
        setEvidenceItems([]); setEvidenceState('CLOSED');
      }
      setResponses({});
    } catch (failure) {
      if (active.current !== originalScope) return;
      setError(failure?.response?.status === 409
        ? 'EOS rejected a stale review, changed reviewer, or divergent command. Refresh.'
        : failure?.response?.status === 403
          ? 'EOS denied this review for the current authenticated principal.'
          : 'The review was not independently confirmed by EOS. Refresh before retrying.');
    } finally {
      if (active.current === originalScope) setBusy(false);
    }
  };

  const requestReview = event => {
    event.preventDefault();
    if (!reviewer || !rationale.trim() || reviewer === principalId) return;
    const available = new Set(evidenceItems.filter(item =>
      item.scan_clearance_status === 'SCAN_CLEAN_VERIFIED').map(item => item.attachment_id));
    if (selectedEvidence.length && (evidenceState !== 'READY'
      || selectedEvidence.length > 10
      || selectedEvidence.some(id => !available.has(id)))) {
      setError('Selected task evidence must be currently source-verified and scan-cleared.');
      return;
    }
    const payload = { reviewer_principal_id: reviewer, rationale: rationale.trim() };
    if (selectedEvidence.length) payload.evidence_attachment_ids = [...selectedEvidence];
    void send(JSON.stringify(['REQUEST', projectId, taskId, payload]), route, payload);
  };

  const decide = (item, choice) => {
    if (participantMode !== true || item.reviewer_principal_id !== principalId
      || item.status !== 'PENDING') return;
    const explanation = (responses[item.approval_id] || '').trim();
    if (!explanation) return;
    const payload = { expected_revision: item.revision, decision: choice, rationale: explanation };
    void send(JSON.stringify(['DECIDE', item.approval_id, payload]),
      route + '/' + encodeURIComponent(item.approval_id) + '/decision',
      payload, item.approval_id);
  };

  // The parent source may still be verifying when this task panel mounts.
  // Independent project participant GET makes the reviewer selector accurate
  // without assuming that a tenant member is a project contributor.
  const refreshReviewers = useCallback(async () => {
    const requestScope = scope;
    setReviewerSource('VERIFYING');
    setReviewerSourceError('');
    try {
      const response = await api.get(
        '/projects/' + encodeURIComponent(projectId) + '/participants?limit=100&offset=0',
        { headers },
      );
      if (active.current !== requestScope) return;
      const data = response?.data;
      if (data?.schema !== 'WILSY-PROJECT-PARTICIPANT-LIST/V1'
        || data.tenant_id !== tenantId || data.principal_id !== principalId
        || data.project_id !== projectId || data.limit !== 100 || data.offset !== 0
        || !Array.isArray(data.items) || data.items.length > 100
        || typeof data.has_more !== 'boolean'
        || data.next_offset !== (data.has_more ? data.items.length : null)
        || data.items.some(person => person?.tenant_id !== tenantId
          || person.project_id !== projectId || person.state !== 'ACTIVE'
          || !['VIEWER', 'CONTRIBUTOR'].includes(person.role)
          || typeof person.principal_id !== 'string'
          || !person.principal_id)
      ) throw new Error('PROJECT_REVIEWER_SOURCE_INVALID');
      setVerifiedReviewers(data.items.filter(person =>
        person.role === 'CONTRIBUTOR' && person.principal_id !== principalId));
      setReviewerSource(data.has_more ? 'PARTIAL' : 'READY');
    } catch (cause) {
      if (active.current !== requestScope) return;
      setVerifiedReviewers([]);
      const status = cause?.response?.status;
      setReviewerSource(status === 403 || status === 401 ? 'DENIED' : 'UNAVAILABLE');
      setReviewerSourceError(status === 403 ? 'EOS denied the project contributor directory (HTTP 403).'
        : status === 401 ? 'Authenticate to inspect eligible project contributors (HTTP 401).'
          : status === 503 ? 'The EOS project contributor source is unavailable (HTTP 503).'
            : status === 404 ? 'Project contributor source is not available in this EOS runtime (HTTP 404).'
              : 'EOS could not verify the project contributor directory.');
    }
  }, [scope, projectId, tenantId, principalId, tenantHeaders]);
  useEffect(() => {
    setVerifiedReviewers([]);
    setReviewerSource('VERIFYING');
    setReviewer('');
    void refreshReviewers();
  }, [scope, refreshReviewers]);
  const options = verifiedReviewers;
  const reviewerName = person => {
    const name = [person.first_name, person.last_name].filter(value =>
      typeof value === 'string' && value.trim()).join(' ').trim();
    return name || 'Verified contributor · name unavailable';
  };

  return <section aria-label="Task approvals" className="mt-4 rounded-xl border border-slate-200 bg-slate-50 p-3">
    <header className="flex items-center justify-between gap-3">
      <h4 className="flex items-center gap-2 font-semibold text-slate-900">
        <ClipboardCheck size={16}/> Task decisions &amp; approvals
      </h4>
      <div className="flex gap-2">
        <button type="button" className="wp-button" disabled={busy}
          onClick={() => void load(offset)}><RefreshCw size={14}/> Refresh</button>
        {showClose && <button type="button" className="wp-button" disabled={busy}
          onClick={onClose} aria-label="Close task approvals"><X size={14}/></button>}
      </div>
    </header>
    <p className="mt-2 text-xs text-slate-600">A project decision is business review evidence. It does not complete a task, approve spending, release money or prove a digital signature.</p>
    {state === 'LOADING' && <p role="status" className="mt-3 text-sm text-slate-700">Verifying decisions with EOS…</p>}
    {(state === 'DENIED' || state === 'UNAVAILABLE') &&
      <p role="alert" className="mt-3 text-sm text-rose-700">{error}</p>}
    {state === 'READY' && <>
      <ul className="mt-3 divide-y divide-slate-200 rounded-lg border border-slate-200 bg-white">
        {items.map(item => <li key={item.approval_id} className="space-y-2 p-3 text-sm">
          <div className="flex flex-wrap justify-between gap-2">
            <strong className="text-slate-900">{item.status === 'PENDING' ? 'Pending review'
              : item.status === 'APPROVED' ? 'Approved' : 'Rejected'}</strong>
            <span className="text-xs text-slate-600">Revision {item.revision}</span>
          </div>
          <p className="break-words text-slate-800">{item.rationale}</p>
          <p className="break-all text-xs text-slate-600">
            Requested by {item.requester_principal_id} · Reviewer {item.reviewer_principal_id}
          </p>
          {Array.isArray(item.evidence_attachment_ids) && item.evidence_attachment_ids.length > 0 &&
            <div className="rounded-lg border border-slate-200 bg-slate-50 p-2 text-xs text-slate-700">
              <strong className="text-slate-900">Bound task evidence · {item.evidence_attachment_ids.length} file(s)</strong>
              <ul aria-label={'Approval evidence ' + item.approval_id} className="mt-1 space-y-1">
                {item.evidence_attachment_ids.map(id =>
                  <li key={id} className="break-all">{id}</li>)}
              </ul>
              <p>Inspect original files separately through authorized Task attachments. No download grant or signature is inferred.</p>
            </div>}
          {item.decision_rationale && <p className="break-words text-slate-700">
            Decision rationale: {item.decision_rationale}</p>}
          {participantMode && item.status === 'PENDING' && item.reviewer_principal_id === principalId &&
            <div className="space-y-2 rounded-lg border border-blue-200 bg-blue-50/30 p-3">
              <label className="block text-xs font-semibold text-slate-800">Decision rationale
                <textarea aria-label={'Decision rationale ' + item.approval_id}
                  rows={2} maxLength={3000} value={responses[item.approval_id] || ''}
                  onChange={event => setResponses(previous => ({
                    ...previous, [item.approval_id]: event.target.value,
                  }))} className="mt-1 w-full rounded-lg border border-slate-300 bg-white p-2 text-sm font-normal text-slate-900"/>
              </label>
              <div className="flex gap-2">
                <button type="button" className="wp-button wp-button-primary"
                  disabled={busy || !(responses[item.approval_id] || '').trim()}
                  onClick={() => decide(item, 'APPROVED')}><Check size={14}/> Approve review</button>
                <button type="button" className="wp-button"
                  disabled={busy || !(responses[item.approval_id] || '').trim()}
                  onClick={() => decide(item, 'REJECTED')}>Reject review</button>
              </div>
            </div>}
        </li>)}
        {!items.length && <li className="p-4 text-sm text-slate-600">EOS verified no approvals on this task page.</li>}
      </ul>
      {(offset > 0 || hasMore) && <nav aria-label="Approval pages" className="mt-2 flex gap-3">
        <button type="button" className="wp-button" disabled={busy || offset === 0}
          onClick={() => void load(Math.max(0, offset - 50))}>Previous</button>
        <button type="button" className="wp-button" disabled={busy || !hasMore}
          onClick={() => void load(offset + 50)}>Next</button>
      </nav>}
      {!participantMode && <form onSubmit={requestReview} className="mt-4 space-y-3 rounded-lg border border-slate-200 bg-white p-3">
        <h5 className="font-semibold text-slate-900">Request independent review</h5>
        <label className="block text-sm font-semibold text-slate-800">Named project contributor
          <select aria-label="Review contributor" required value={reviewer}
            disabled={busy || reviewerSource === 'VERIFYING' || reviewerSource === 'DENIED'
              || reviewerSource === 'UNAVAILABLE' || !options.length}
            onChange={event => setReviewer(event.target.value)}
            className="mt-1 w-full rounded-lg border border-slate-300 bg-white p-2 text-sm font-normal text-slate-900">
            <option value="">Select a verified contributor</option>
            {options.map(person => <option key={person.principal_id} value={person.principal_id}>
              {reviewerName(person)}
            </option>)}
          </select>
        </label>
        <label className="block text-sm font-semibold text-slate-800">Review request rationale
          <textarea aria-label="Review request rationale" required rows={3} maxLength={3000}
            value={rationale} onChange={event => setRationale(event.target.value)}
            className="mt-1 w-full rounded-lg border border-slate-300 bg-white p-2 text-sm font-normal text-slate-900"/>
        </label>
        <fieldset className="rounded-lg border border-slate-200 bg-slate-50 p-3">
          <legend className="text-sm font-semibold text-slate-900">Task evidence</legend>
          <p className="text-xs text-slate-700">
            Optional: bind up to ten independently scan-cleared task attachments to this review.
            Without selected files, this remains a rationale-only business decision.
          </p>
          <button type="button" className="wp-button mt-2" disabled={busy}
            onClick={() => void loadEvidence(0)}>Choose verified task evidence</button>
          {evidenceState === 'LOADING' && <p role="status" className="mt-2 text-xs text-slate-700">
            Verifying source-backed task attachments…
          </p>}
          {evidenceState === 'UNAVAILABLE' && <p role="alert" className="mt-2 text-xs text-rose-700">
            EOS attachment evidence unavailable. No file can be linked without verification.
          </p>}
          {evidenceState === 'READY' && <>
            <div className="mt-2 space-y-2">
              {evidenceItems.filter(item => item.scan_clearance_status === 'SCAN_CLEAN_VERIFIED')
                .map(item => <label key={item.attachment_id}
                  className="flex items-start gap-2 break-words text-sm text-slate-900">
                  <input type="checkbox" className="mt-1"
                    checked={selectedEvidence.includes(item.attachment_id)}
                    disabled={busy || (selectedEvidence.length >= 10
                      && !selectedEvidence.includes(item.attachment_id))}
                    onChange={event => setSelectedEvidence(previous =>
                      event.target.checked ? [...previous, item.attachment_id]
                        : previous.filter(id => id !== item.attachment_id))}
                  />
                  <span>{item.filename} · SHA3-512 {item.content_sha3_512}</span>
                </label>)}
            </div>
            {!evidenceItems.some(item => item.scan_clearance_status === 'SCAN_CLEAN_VERIFIED') &&
              <p className="mt-2 text-xs text-slate-700">No scan-cleared attachments on this page.</p>}
            {(evidenceOffset > 0 || evidenceMore) &&
              <nav aria-label="Review evidence pages" className="mt-2 flex gap-2">
                <button type="button" className="wp-button"
                  disabled={busy || evidenceOffset === 0}
                  onClick={() => void loadEvidence(Math.max(0, evidenceOffset - 50))}>Previous files</button>
                <button type="button" className="wp-button"
                  disabled={busy || !evidenceMore}
                  onClick={() => void loadEvidence(evidenceOffset + 50)}>Next files</button>
              </nav>}
          </>}
        </fieldset>
        <button type="submit" className="wp-button wp-button-primary"
          disabled={busy || !reviewer || !rationale.trim() || !options.some(person => person.principal_id === reviewer)}>
          Request EOS review
        </button>
        <div role="status" className="flex flex-wrap items-center gap-2 text-xs text-slate-700">
          {reviewerSource === 'VERIFYING' ? 'Verifying independently eligible contributors with EOS…'
            : reviewerSourceError ? reviewerSourceError
              : options.length === 0 ? 'No independent project contributor is verified. The signed-in requester cannot approve their own review.'
                : options.length + ' independent contributor(s) verified for review.'}
          {reviewerSource === 'PARTIAL' && ' More contributor pages exist; only this page is eligible.'}
          <button type="button" className="wp-button !min-h-9 !px-3 !text-xs"
            disabled={busy || reviewerSource === 'VERIFYING'}
            onClick={() => void refreshReviewers()}>Refresh contributors</button>
          {options.length === 0 && typeof onManageContributors === 'function' && <button
            type="button" className="wp-button !min-h-9 !px-3 !text-xs" onClick={onManageContributors}>
            Manage project people
          </button>}
        </div>
      </form>}
      {error && <p role="alert" className="mt-3 text-sm text-rose-700">{error}</p>}
    </>}
  </section>;
}

// ARTIFACT: ProjectTaskApprovalsPanel.jsx
// VERSION: v1.2.1-REVIEWER-REQUEST-SCOPE-GUARD
// AUTHORITY BOUNDARY: source business review UI, no IAM/financial/task authority
// TENANT POSTURE: exact tenant, task, project, participant and session scope
// FAIL-CLOSED POSTURE: source mismatch or unverified command readback denies
// FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
// END OF WILSY OS SOVEREIGN ARTIFACT
