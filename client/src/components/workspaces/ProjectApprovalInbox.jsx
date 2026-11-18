/**
 * TITLE: WILSY OS My Pending Project Decision Inbox
 * VERSION: v1.1.0-EVIDENCE-VISIBLE-REVIEWER-INBOX
 * AUTHORITY: Python EOS recipient/project participant IAM and approval source.
 * EPITOME: One searchable-by-authority pending review queue with exact-person
 *          decisions and source-confirmed readback, independent of task pages.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/components/workspaces/ProjectApprovalInbox.jsx
 * COLLABORATION / OWNERSHIP: AssignedProjectsWorkspace mounts this reviewer
 *          feed; Python EOS owns project records, decisions, IAM and replay.
 * CERTIFICATION / UPDATE DATE: 2026-11-18
 * CHANGELOG: v1.1.0-EVIDENCE-VISIBLE-REVIEWER-INBOX shows immutable source evidence references and embeds the existing participant-authorized task attachment viewer before a decision, verifying evidence identity on decision acknowledgement.
 * CHANGELOG: v1.1.0-EVIDENCE-VISIBLE-REVIEWER-INBOX adds current designated
 *          participant's PENDING decisions with CAS, no owner-list authority.
 * COMPLIANCE: AGENTS.md; POPIA section 19; GDPR Article 32; WCAG 2.2 AA.
 * SECURITY / PRIVACY POSTURE: Plain text, no client-generated approvals.
 * TENANT BOUNDARY: Every source and result checks exact tenant and principal.
 * AUTHORITY BOUNDARY: No financial authorization, task mutation or IAM grants.
 * FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively.
 */
import React, { useCallback, useEffect, useRef, useState } from 'react';
import { ClipboardCheck, RefreshCw } from 'lucide-react';
import api from '../../services/api.js';
import ProjectTaskAttachmentsPanel from './ProjectTaskAttachmentsPanel.jsx';

const PROJECT = /^prj-[0-9a-f]{48}$/;
const TASK = /^ptk-[0-9a-f]{48}$/;
const APPROVAL = /^par-[0-9a-f]{48}$/;
const ATTACHMENT = /^pat-[0-9a-f]{48}$/;

function matchingEvidence(left, right) {
  return Array.isArray(left) && Array.isArray(right)
    && left.length === right.length
    && left.every((id, index) => id === right[index]);
}

function valid(item, tenantId, principalId) {
  return Boolean(
    item?.schema === 'wilsy.project.approval.v1'
    && item.tenant_id === tenantId
    && item.reviewer_principal_id === principalId
    && PROJECT.test(item.project_id)
    && TASK.test(item.task_id)
    && APPROVAL.test(item.approval_id)
    && typeof item.requester_principal_id === 'string'
    && item.requester_principal_id !== principalId
    && typeof item.rationale === 'string' && item.rationale.trim()
    && item.status === 'PENDING' && item.revision === 1
    && item.decided_at === null && item.decision_rationale === null
    && /^[a-f0-9]{128}$/.test(item.fingerprint || '')
    && (item.evidence_attachment_ids === undefined
      || (Array.isArray(item.evidence_attachment_ids)
        && item.evidence_attachment_ids.length <= 10
        && item.evidence_attachment_ids.every(id => ATTACHMENT.test(id))
        && new Set(item.evidence_attachment_ids).size === item.evidence_attachment_ids.length)),
  );
}

/** @description Explicit recipient decisions, never speculative work counts. */
export default function ProjectApprovalInbox({
  tenantId, principalId, tenantHeaders, sessionScope,
}) {
  const [items, setItems] = useState([]);
  const [state, setState] = useState('LOADING');
  const [offset, setOffset] = useState(0);
  const [hasMore, setHasMore] = useState(false);
  const [draft, setDraft] = useState({});
  const [openEvidenceId, setOpenEvidenceId] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const scope = [tenantId, principalId, sessionScope].join('\0');
  const active = useRef(scope);
  active.current = scope;
  const generation = useRef(0);
  const replay = useRef(new Map());
  const headers = tenantHeaders || {};

  const load = useCallback(async (nextOffset = 0) => {
    const request = ++generation.current, current = scope;
    setState('LOADING');
    setError('');
    try {
      const { data } = await api.get('/projects/my-approvals?limit=50&offset=' + nextOffset, { headers });
      if (request !== generation.current || active.current !== current) return false;
      if (
        data?.schema !== 'WILSY-PROJECT-PENDING-APPROVALS/V1'
        || data.tenant_id !== tenantId || data.principal_id !== principalId
        || data.limit !== 50 || data.offset !== nextOffset
        || typeof data.has_more !== 'boolean'
        || !Array.isArray(data.items) || data.items.length > 50
        || (data.has_more && data.items.length === 0)
        || data.next_offset !== (data.has_more ? nextOffset + data.items.length : null)
        || data.items.some(item => !valid(item, tenantId, principalId))
        || new Set(data.items.map(item => item.approval_id)).size !== data.items.length
      ) throw new Error('PROJECT_REVIEWER_INBOX_SOURCE_INVALID');
      setItems(data.items);
      setOffset(nextOffset);
      setHasMore(data.has_more);
      setState('READY');
      return true;
    } catch (failure) {
      if (request !== generation.current || active.current !== current) return false;
      setItems([]);
      setHasMore(false);
      setState([401, 403].includes(failure?.response?.status) ? 'DENIED' : 'UNAVAILABLE');
      setError('EOS could not verify your current project approval inbox.');
      return false;
    }
  }, [scope, tenantId, principalId, tenantHeaders]);

  useEffect(() => {
    generation.current += 1;
    setItems([]);
    setDraft({});
    setOpenEvidenceId(null);
    setOffset(0);
    replay.current.clear();
    void load(0);
    return () => { generation.current += 1; };
  }, [scope, load]);

  const decide = async (item, decision) => {
    if (busy || state !== 'READY' || !valid(item, tenantId, principalId)) return;
    const rationale = (draft[item.approval_id] || '').trim();
    if (!rationale) return;
    const fingerprint = JSON.stringify([
      item.approval_id, item.revision, decision, rationale,
    ]);
    let key = replay.current.get(fingerprint);
    if (!key) {
      if (typeof globalThis.crypto?.randomUUID !== 'function') {
        setError('Cannot establish a durable review command key.');
        return;
      }
      key = globalThis.crypto.randomUUID();
      replay.current.set(fingerprint, key);
    }
    const current = scope;
    setBusy(true);
    setError('');
    try {
      const path = '/projects/' + encodeURIComponent(item.project_id)
        + '/my-project/tasks/' + encodeURIComponent(item.task_id)
        + '/approvals/' + encodeURIComponent(item.approval_id) + '/decision';
      const { data } = await api.post(path, {
        expected_revision: 1, decision, rationale,
      }, { headers: { ...headers, 'Idempotency-Key': key } });
      if (active.current !== current) return;
      if (
        data?.schema !== 'WILSY-PROJECT-APPROVAL-RESULT/V1'
        || data.tenant_id !== tenantId || data.principal_id !== principalId
        || data.project_id !== item.project_id || data.task_id !== item.task_id
        || data.approval?.approval_id !== item.approval_id
        || data.approval.reviewer_principal_id !== principalId
        || data.approval.status !== decision || data.approval.revision !== 2
        || data.approval.decision_rationale !== rationale
        || !/^[a-f0-9]{128}$/.test(data.approval.fingerprint || '')
        || !matchingEvidence(
          data.approval.evidence_attachment_ids || [],
          item.evidence_attachment_ids || [],
        )
      ) throw new Error('PROJECT_REVIEWER_DECISION_RESULT_INVALID');
      const confirmed = await load(0);
      if (!confirmed || active.current !== current) return;
      const { data: refreshed } = await api.get('/projects/my-approvals?limit=50&offset=0', { headers });
      if (active.current !== current) return;
      if (
        refreshed?.schema !== 'WILSY-PROJECT-PENDING-APPROVALS/V1'
        || refreshed.tenant_id !== tenantId || refreshed.principal_id !== principalId
        || !Array.isArray(refreshed.items)
        || refreshed.items.some(row => !valid(row, tenantId, principalId))
        || refreshed.items.some(row => row.approval_id === item.approval_id)
      ) throw new Error('PROJECT_REVIEWER_DECISION_READBACK_PENDING');
      replay.current.delete(fingerprint);
      setOpenEvidenceId(null);
      setDraft(previous => {
        const next = { ...previous };
        delete next[item.approval_id];
        return next;
      });
    } catch (failure) {
      if (active.current !== current) return;
      setError(failure?.response?.status === 409
        ? 'EOS rejected a stale or conflicting decision. Refresh your inbox.'
        : failure?.response?.status === 403
          ? 'EOS denied this decision for your current project participation.'
          : 'Decision has not been verified by an independent EOS read. Refresh.');
    } finally {
      if (active.current === current) setBusy(false);
    }
  };

  return <section aria-label="Pending project approvals"
    className="mt-5 rounded-xl border border-slate-200 bg-white p-4">
    <div className="flex flex-wrap items-center justify-between gap-3">
      <h2 className="flex items-center gap-2 font-semibold text-slate-900">
        <ClipboardCheck size={16}/> My pending project approvals
        {state === 'READY' && <span className="text-sm font-normal text-slate-600">
          ({items.length} on this page)
        </span>}
      </h2>
      <button type="button" className="wp-button" disabled={busy}
        onClick={() => void load(offset)}><RefreshCw size={14}/> Refresh</button>
    </div>
    <p className="mt-2 text-xs text-slate-600">
      EOS shows only decisions assigned to your current project Contributor capacity. A decision never releases funds or completes work.
    </p>
    {state === 'LOADING' && <p role="status" className="mt-3 text-sm text-slate-700">Verifying reviewer authority…</p>}
    {(state === 'DENIED' || state === 'UNAVAILABLE') &&
      <p role="alert" className="mt-3 text-sm text-rose-700">{error}</p>}
    {state === 'READY' && <>
      <ul className="mt-3 divide-y divide-slate-200 rounded-lg border border-slate-200">
        {items.map(item => <li className="space-y-2 p-3 text-sm" key={item.approval_id}>
          <p className="break-words font-semibold text-slate-900">{item.rationale}</p>
          <p className="break-all text-xs text-slate-600">
            Task {item.task_id} · Project {item.project_id}
          </p>
          <p className="break-all text-xs text-slate-600">Requested by {item.requester_principal_id}</p>
          {Array.isArray(item.evidence_attachment_ids) && item.evidence_attachment_ids.length > 0 &&
            <div className="rounded-lg border border-slate-200 bg-slate-50 p-3 text-xs text-slate-700">
              <p className="font-semibold text-slate-900">
                Evidence-backed review · {item.evidence_attachment_ids.length} bound file(s)
              </p>
              <ul aria-label={'Pending approval evidence ' + item.approval_id}
                className="mt-1 space-y-1">
                {item.evidence_attachment_ids.map(id =>
                  <li key={id} className="break-all">{id}</li>)}
              </ul>
              <p className="mt-2">
                Inspect the current task file manifests and authorized scan-cleared downloads
                before deciding. A scan result does not establish document authenticity.
              </p>
              <button type="button" className="wp-button mt-2" disabled={busy}
                onClick={() => setOpenEvidenceId(previous =>
                  previous === item.approval_id ? null : item.approval_id)}>
                {openEvidenceId === item.approval_id ? 'Close task evidence' : 'Inspect task evidence'}
              </button>
              {openEvidenceId === item.approval_id &&
                <ProjectTaskAttachmentsPanel
                  key={scope + item.approval_id}
                  tenantId={tenantId} principalId={principalId}
                  projectId={item.project_id} taskId={item.task_id}
                  tenantHeaders={tenantHeaders} participantMode
                  onClose={() => setOpenEvidenceId(null)}
                />}
            </div>}
          <label className="block text-xs font-semibold text-slate-800">Decision rationale
            <textarea maxLength={3000} rows={2} aria-label={'Review rationale ' + item.approval_id}
              value={draft[item.approval_id] || ''}
              onChange={event => setDraft(previous => ({
                ...previous, [item.approval_id]: event.target.value,
              }))}
              className="mt-1 w-full rounded-lg border border-slate-300 bg-white p-2 text-sm font-normal text-slate-900"/>
          </label>
          <div className="flex flex-wrap gap-2">
            <button type="button" className="wp-button wp-button-primary"
              disabled={busy || !(draft[item.approval_id] || '').trim()}
              onClick={() => void decide(item, 'APPROVED')}>Approve</button>
            <button type="button" className="wp-button"
              disabled={busy || !(draft[item.approval_id] || '').trim()}
              onClick={() => void decide(item, 'REJECTED')}>Reject</button>
          </div>
        </li>)}
        {!items.length && <li className="p-4 text-sm text-slate-600">
          EOS verified no pending reviews assigned to your principal on this page.
        </li>}
      </ul>
      {(offset > 0 || hasMore) && <nav aria-label="Reviewer approval pages" className="mt-3 flex gap-2">
        <button type="button" className="wp-button" disabled={busy || offset === 0}
          onClick={() => void load(Math.max(0, offset - 50))}>Previous</button>
        <button type="button" className="wp-button" disabled={busy || !hasMore}
          onClick={() => void load(offset + 50)}>Next</button>
      </nav>}
      {error && <p role="alert" className="mt-3 text-sm text-rose-700">{error}</p>}
    </>}
  </section>;
}

// ARTIFACT: ProjectApprovalInbox.jsx
// VERSION: v1.1.0-EVIDENCE-VISIBLE-REVIEWER-INBOX
// AUTHORITY BOUNDARY: source-owned review only; no task/financial/IAM action
// TENANT POSTURE: exact tenant/principal on every list and decision readback
// FAIL-CLOSED POSTURE: stale, foreign, malformed, unverifiable decision denied
// FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
// END OF WILSY OS SOVEREIGN ARTIFACT
