/**
 * TITLE: WILSY OS Project Task Source-Owned Work Purpose Panel
 * VERSION: v1.0.0-AUDITED-WORK-PURPOSE-CLASSIFICATION
 * AUTHORITY: Python EOS Projects work-purpose GET/POST owns source and audit.
 * EPITOME: One focused project task classification action with reason and CAS.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/components/workspaces/ProjectWorkPurposePanel.jsx
 * COLLABORATION / OWNERSHIP: ProjectTasksPanel provides already verified task
 * coordinates; EOS independently reauthorizes project:update and task revision.
 * CERTIFICATION / UPDATE DATE: 2026-11-23
 * CHANGELOG: v1.0.0-AUDITED-WORK-PURPOSE-CLASSIFICATION exposes an authorized
 * source purpose field, explicit human rationale and guarded EOS command,
 * preserves command idempotency on ambiguous transport, validates the exact
 * source receipt and independently rereads the committed classification.
 * COMPLIANCE: AGENTS.md; POPIA section 19; GDPR Article 32; WCAG 2.2 AA.
 * SECURITY / PRIVACY POSTURE: No client-authored source evidence, task title
 * heuristic or approval; opaque command key never rendered.
 * TENANT BOUNDARY: Response tenant/principal/project/task/revision exact.
 * AUTHORITY BOUNDARY: Only EOS can admit project:update or persist metadata.
 * FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively.
 */
import React, { useCallback, useEffect, useRef, useState } from 'react';
import api from '../../services/api.js';

const SCHEMA = 'WILSY-PROJECT-WORK-PURPOSE/V1';
const OPTIONS = ['OPERATING', 'PLATFORM_BUILD', 'UNCLASSIFIED'];
const LABELS = {
  OPERATING: 'Operating',
  PLATFORM_BUILD: 'Platform Build',
  UNCLASSIFIED: 'Needs classification',
};

function assertPurpose(value, { tenantId, principalId, projectId, task }) {
  if (!value || value.schema !== SCHEMA
    || value.tenant_id !== tenantId || value.principal_id !== principalId
    || value.project_id !== projectId || value.task_id !== task.task_id
    || value.task_revision !== task.revision
    || !OPTIONS.includes(value.audience)
    || !Number.isSafeInteger(value.purpose_revision) || value.purpose_revision < 0
    || value.critical_gate !== false
    || (value.audience === 'UNCLASSIFIED'
      ? (value.purpose_revision !== 0 || value.evidence_ref !== null
        || value.source_revision !== null)
      : (value.purpose_revision < 1
        || !Number.isSafeInteger(value.source_revision)
        || value.source_revision !== task.revision
        || typeof value.evidence_ref !== 'string' || !value.evidence_ref.startsWith('project-work-purpose:')))) {
    throw new Error('PROJECT_WORK_PURPOSE_READBACK_INVALID');
  }
  return value;
}

export default function ProjectWorkPurposePanel({
  task, projectId, tenantId, principalId, tenantHeaders, canClassify,
}) {
  const [read, setRead] = useState(null);
  const [state, setState] = useState('LOADING');
  const [purpose, setPurpose] = useState('PLATFORM_BUILD');
  const [reason, setReason] = useState('');
  const [message, setMessage] = useState('');
  const operation = useRef(null);
  const epoch = useRef(0);
  const path = '/projects/' + encodeURIComponent(projectId)
    + '/tasks/' + encodeURIComponent(task.task_id) + '/work-purpose';
  const scope = { task, projectId, tenantId, principalId };

  const refresh = useCallback(async (signal) => {
    const { data } = await api.get(path, { headers: tenantHeaders, signal });
    return assertPurpose(data, scope);
  }, [path, tenantHeaders, tenantId, principalId, projectId, task]);

  useEffect(() => {
    const controller = new AbortController();
    const id = ++epoch.current;
    setState('LOADING');
    setRead(null);
    setMessage('');
    void refresh(controller.signal).then(result => {
      if (epoch.current !== id) return;
      setRead(result);
      setPurpose(result.audience === 'UNCLASSIFIED' ? 'PLATFORM_BUILD' : result.audience);
      setState('READY');
    }).catch(error => {
      if (epoch.current !== id || controller.signal.aborted) return;
      setState(error?.response?.status === 401 || error?.response?.status === 403
        ? 'DENIED' : 'UNAVAILABLE');
      setMessage('EOS could not verify the current work classification. No change is authorized.');
    });
    return () => { controller.abort(); epoch.current += 1; };
  }, [refresh]);

  const save = async event => {
    event.preventDefault();
    if (!canClassify || state !== 'READY' || !read || !OPTIONS.slice(0, 2).includes(purpose)
      || reason.trim().length < 10 || reason.trim().length > 1000) return;
    const body = {
      audience: purpose, reason: reason.trim(),
      expected_task_revision: task.revision,
      expected_purpose_revision: read.purpose_revision,
    };
    const fingerprint = JSON.stringify([path, body, tenantId, principalId]);
    if (!operation.current || operation.current.fingerprint !== fingerprint) {
      if (typeof globalThis.crypto?.randomUUID !== 'function') {
        setMessage('Secure command key unavailable. No change submitted.');
        return;
      }
      operation.current = { fingerprint, key: globalThis.crypto.randomUUID() };
    }
    const key = operation.current.key;
    const id = ++epoch.current;
    setState('SAVING');
    setMessage('');
    try {
      const receipt = await api.post(path, body, {
        headers: { ...tenantHeaders, 'Idempotency-Key': key },
      });
      const saved = assertPurpose(receipt.data, scope);
      if (saved.audience !== purpose || saved.purpose_revision !== read.purpose_revision + 1) {
        throw new Error('PROJECT_WORK_PURPOSE_COMMAND_READBACK_INVALID');
      }
      const verified = await refresh();
      if (epoch.current !== id) return;
      if (verified.audience !== saved.audience
          || verified.evidence_ref !== saved.evidence_ref
          || verified.purpose_revision !== saved.purpose_revision) {
        throw new Error('PROJECT_WORK_PURPOSE_INDEPENDENT_READBACK_INVALID');
      }
      setRead(verified);
      setState('READY');
      setReason('');
      setMessage('Source classification verified and audit persisted in EOS.');
      operation.current = null;
    } catch (error) {
      if (epoch.current !== id) return;
      setState('UNAVAILABLE');
      setMessage(error?.response?.status === 403
        ? 'Current project:update authority denied by EOS. No classification verified.'
        : error?.response?.status === 409
          ? 'Task or purpose revision changed. Refresh source before trying again.'
          : 'Command or independent readback could not be verified. Inspect current EOS state before retrying; no duplicate submission was made.');
    }
  };

  return <section className="mt-5 border-t border-slate-200 pt-4"
    aria-label="Source-owned work classification">
    <div className="flex flex-wrap items-center justify-between gap-2">
      <h4 className="text-sm font-bold text-slate-950">Work purpose</h4>
      <button type="button" className="text-xs font-semibold text-blue-800 underline"
        disabled={state === 'LOADING' || state === 'SAVING'}
        onClick={() => {
          const id = ++epoch.current;
          setState('LOADING'); setMessage('');
          void refresh().then(value => {
            if (epoch.current !== id) return;
            setRead(value); setPurpose(value.audience === 'UNCLASSIFIED' ? 'PLATFORM_BUILD' : value.audience);
            setState('READY');
          }).catch(() => { if (epoch.current === id) { setState('UNAVAILABLE'); setMessage('EOS classification source unavailable.'); } });
        }}>Refresh source</button>
    </div>
    {state === 'LOADING' && <p role="status" className="mt-2 text-sm text-slate-600">Verifying classification…</p>}
    {state === 'SAVING' && <p role="status" className="mt-2 text-sm text-slate-600">Verifying source and audit…</p>}
    {state === 'READY' && read && <>
      <p className="mt-2 text-sm text-slate-800">
        {LABELS[read.audience]}{read.audience !== 'UNCLASSIFIED' && ' · Audited source'}
      </p>
      {canClassify && <form className="mt-3 space-y-3" onSubmit={save}>
        <label className="block text-sm font-semibold text-slate-900" htmlFor="task-work-purpose">
          Classification
        </label>
        <select id="task-work-purpose" aria-label="Classify project work purpose"
          value={purpose} onChange={e => setPurpose(e.target.value)}
          className="w-full rounded-lg border border-slate-400 bg-white px-3 py-2 text-slate-950">
          <option value="OPERATING">Operating</option>
          <option value="PLATFORM_BUILD">Platform Build</option>
        </select>
        <label className="block text-sm font-semibold text-slate-900" htmlFor="task-work-purpose-reason">
          Classification rationale
        </label>
        <textarea id="task-work-purpose-reason" aria-label="Work classification rationale"
          rows={3} maxLength={1000} value={reason}
          onChange={e => setReason(e.target.value)}
          placeholder="Describe why this task belongs in the selected work purpose."
          className="w-full rounded-lg border border-slate-400 bg-white px-3 py-2 text-slate-950"/>
        <button type="submit" className="wp-button"
          disabled={reason.trim().length < 10 || reason.trim().length > 1000}>
          Save audited classification
        </button>
      </form>}
      {!canClassify && <p className="mt-2 text-sm text-slate-600">
        Current project:update authority is required to classify this task.
      </p>}
    </>}
    {message && <p role={state === 'READY' ? 'status' : 'alert'}
      className="mt-2 text-sm text-slate-700">{message}</p>}
  </section>;
}

export { assertPurpose };

// ARTIFACT: ProjectWorkPurposePanel.jsx
// VERSION: v1.0.0-AUDITED-WORK-PURPOSE-CLASSIFICATION
// AUTHORITY BOUNDARY: Explicit command only; source validates IAM and revision.
// TENANT POSTURE: Exact source and actor response verification.
// FAIL-CLOSED POSTURE: Unverified receipt or independent readback never succeeds.
// FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
// END OF WILSY OS SOVEREIGN ARTIFACT
