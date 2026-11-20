/**
 * TITLE: WILSY OS Governed Project Task Quarantine Attachments Panel
 * VERSION: v1.1.0-GOVERNED-SCAN-AND-CLEAN-DOWNLOAD
 * AUTHORITY: Python EOS task-scoped attachment and participant IAM services.
 * EPITOME: Source-backed task attachments, bounded PDF/image upload and visible
 *          quarantine state, without unsafe preview or download links.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/components/workspaces/ProjectTaskAttachmentsPanel.jsx
 * COLLABORATION / OWNERSHIP: Shared owner and Contributor task workspaces.
 *          API and Python EOS own authentication, bytes, storage and audit.
 * CERTIFICATION / UPDATE DATE: 2026-11-18
 * CHANGELOG: v1.1.0-GOVERNED-SCAN-AND-CLEAN-DOWNLOAD shows
 *          source-owned GuardDuty clearance, recipient-triggered scan
 *          reconciliation and authenticated clean-only byte download.
 * CHANGELOG:  v1.1.0-GOVERNED-SCAN-AND-CLEAN-DOWNLOAD requires exact
 *          source readback after a contributor's quarantined file receipt,
 *          refusing inferred safe/approved attachment states or direct URLs.
 * COMPLIANCE: AGENTS.md; POPIA section 19; GDPR Article 32; WCAG 2.2 AA.
 * SECURITY / PRIVACY POSTURE: Client restricts type/size; EOS revalidates.
 *          No HTML parsing, blob display, S3 URL, preview or file download.
 * TENANT BOUNDARY: Exact tenant/principal/project/task on every source response.
 * AUTHORITY BOUNDARY: Browser cannot release quarantine, approve evidence,
 *          assign permissions, approve payment or override uploader identity.
 * FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively.
 */
import React, { useCallback, useEffect, useRef, useState } from 'react';
import { FileLock2, RefreshCw, UploadCloud, X } from 'lucide-react';
import api from '../../services/api.js';

const LIMIT = 20 * 1024 * 1024;
const SCHEMA = 'wilsy.project.attachment.v1';
const ATTACHMENT = /^pat-[0-9a-f]{48}$/;
const SAFE = new Set(['application/pdf', 'image/png', 'image/jpeg']);

function valid(record, tenantId, projectId, taskId) {
  return Boolean(
    record?.schema === SCHEMA
    && record.tenant_id === tenantId
    && record.project_id === projectId
    && record.task_id === taskId
    && ATTACHMENT.test(record.attachment_id)
    && typeof record.filename === 'string' && record.filename.length > 0
    && SAFE.has(record.media_type)
    && Number.isSafeInteger(record.size_bytes)
    && record.size_bytes > 0 && record.size_bytes <= LIMIT
    && /^[a-f0-9]{128}$/.test(record.content_sha3_512 || '')
    && record.state === 'QUARANTINED' && record.revision === 1
    && ['QUARANTINED', 'SCAN_CLEAN_VERIFIED'].includes(record.scan_clearance_status)
    && (record.scan_clearance_status === 'QUARANTINED'
      ? record.scan_clearance_fingerprint === null
      : /^[a-f0-9]{128}$/.test(record.scan_clearance_fingerprint || ''))
    && !Object.hasOwn(record, 'storage_receipt')
    && !Object.hasOwn(record, 'download_url')
    && !Object.hasOwn(record, 'presigned_url'),
  );
}

/** @description Render quarantined source evidence and an exact-scope upload. */
export default function ProjectTaskAttachmentsPanel({
  tenantId, principalId, projectId, taskId, tenantHeaders,
  participantMode = false, onClose,
}) {
  const [state, setState] = useState('LOADING');
  const [items, setItems] = useState([]);
  const [offset, setOffset] = useState(0);
  const [hasMore, setHasMore] = useState(false);
  const [file, setFile] = useState(null);
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);
  const scope = [tenantId, principalId, projectId, taskId, participantMode].join('\0');
  const current = useRef(scope);
  current.current = scope;
  const generation = useRef(0);
  const uploadOrigin = useRef({ fingerprint: '', key: '' });
  const root = '/projects/' + encodeURIComponent(projectId)
    + (participantMode ? '/my-project/tasks/' : '/tasks/')
    + encodeURIComponent(taskId);
  const headers = tenantHeaders || {};

  const load = useCallback(async (nextOffset = 0) => {
    const request = ++generation.current;
    const active = scope;
    setState('LOADING');
    setError('');
    try {
      const { data } = await api.get(root + '/attachments?limit=50&offset=' + nextOffset, { headers });
      if (request !== generation.current || current.current !== active) return false;
      if (
        data?.schema !== 'WILSY-PROJECT-ATTACHMENT-LIST/V1'
        || data.tenant_id !== tenantId || data.principal_id !== principalId
        || data.project_id !== projectId || data.task_id !== taskId
        || data.limit !== 50 || data.offset !== nextOffset
        || typeof data.has_more !== 'boolean'
        || !Array.isArray(data.items) || data.items.length > 50
        || (data.has_more && !data.items.length)
        || data.next_offset !== (data.has_more ? nextOffset + data.items.length : null)
        || data.items.some(item => !valid(item, tenantId, projectId, taskId))
        || new Set(data.items.map(item => item.attachment_id)).size !== data.items.length
      ) throw new Error('PROJECT_ATTACHMENT_SOURCE_INVALID');
      setItems(data.items);
      setOffset(nextOffset);
      setHasMore(data.has_more);
      setState('READY');
      return true;
    } catch (failure) {
      if (request !== generation.current || current.current !== active) return false;
      setItems([]);
      setHasMore(false);
      setState([401, 403, 404].includes(failure?.response?.status) ? 'DENIED' : 'UNAVAILABLE');
      setError('EOS could not verify the task attachment source. Refresh or check authorization.');
      return false;
    }
  }, [scope, root, tenantId, principalId, projectId, taskId, tenantHeaders]);

  useEffect(() => {
    generation.current += 1;
    setFile(null);
    setItems([]);
    setOffset(0);
    uploadOrigin.current = { fingerprint: '', key: '' };
    void load(0);
    return () => { generation.current += 1; };
  }, [scope, load]);

  const verifyScan = async item => {
    if (!participantMode || busy || state !== 'READY'
      || item.scan_clearance_status !== 'QUARANTINED'
      || !valid(item, tenantId, projectId, taskId)) return;
    const active = scope;
    if (typeof globalThis.crypto?.randomUUID !== 'function') {
      setError('Cannot establish an idempotent scan observation key.');
      return;
    }
    const key = globalThis.crypto.randomUUID();
    setBusy(true);
    setError('');
    try {
      const { data } = await api.post(root + '/attachments/'
        + encodeURIComponent(item.attachment_id) + '/verify-scan',
      null, { headers: { ...headers, 'Idempotency-Key': key } });
      if (current.current !== active) return;
      if (
        data?.schema !== 'WILSY-PROJECT-ATTACHMENT-SCAN-RESULT/V1'
        || data.tenant_id !== tenantId || data.principal_id !== principalId
        || data.project_id !== projectId || data.task_id !== taskId
        || data.attachment_id !== item.attachment_id
        || data.scan_status !== 'NO_THREATS_FOUND'
        || !/^[a-f0-9]{128}$/.test(data.clearance_fingerprint || '')
      ) throw new Error('PROJECT_ATTACHMENT_SCAN_RESULT_INVALID');
      const confirmed = await load(0);
      if (!confirmed || current.current !== active) return;
      const { data: verify } = await api.get(
        root + '/attachments?limit=50&offset=0', { headers },
      );
      if (
        current.current !== active
        || verify?.schema !== 'WILSY-PROJECT-ATTACHMENT-LIST/V1'
        || verify.tenant_id !== tenantId || verify.principal_id !== principalId
        || verify.project_id !== projectId || verify.task_id !== taskId
        || !Array.isArray(verify.items)
        || !verify.items.some(value =>
          valid(value, tenantId, projectId, taskId)
          && value.attachment_id === item.attachment_id
          && value.scan_clearance_status === 'SCAN_CLEAN_VERIFIED'
          && value.scan_clearance_fingerprint === data.clearance_fingerprint
        )
      ) throw new Error('PROJECT_ATTACHMENT_SCAN_READBACK_UNVERIFIED');
    } catch (failure) {
      if (current.current !== active) return;
      setError('Scan clearance is not verified. EOS requires a completed clean scan and approved S3 security policy.');
    } finally {
      if (current.current === active) setBusy(false);
    }
  };

  const download = async item => {
    if (busy || state !== 'READY'
      || item.scan_clearance_status !== 'SCAN_CLEAN_VERIFIED'
      || !valid(item, tenantId, projectId, taskId)) return;
    const active = scope;
    setBusy(true);
    setError('');
    try {
      const { data, headers: resultHeaders } = await api.get(
        root + '/attachments/' + encodeURIComponent(item.attachment_id) + '/download',
        { headers, responseType: 'blob', timeout: 120000 },
      );
      if (current.current !== active) return;
      if (
        !(data instanceof Blob) || data.size !== item.size_bytes
        || !(resultHeaders?.['content-type'] || '').startsWith(item.media_type)
      ) throw new Error('PROJECT_ATTACHMENT_DOWNLOAD_SOURCE_INVALID');
      const objectUrl = URL.createObjectURL(data);
      try {
        const anchor = document.createElement('a');
        anchor.href = objectUrl;
        anchor.download = item.filename;
        anchor.rel = 'noopener';
        document.body.appendChild(anchor);
        anchor.click();
        anchor.remove();
      } finally {
        URL.revokeObjectURL(objectUrl);
      }
    } catch (failure) {
      if (current.current !== active) return;
      setError('EOS did not verify an authorized clean attachment download.');
    } finally {
      if (current.current === active) setBusy(false);
    }
  };

  const upload = async event => {
    event.preventDefault();
    if (!participantMode || busy || state !== 'READY' || !file) return;
    if (!SAFE.has(file.type) || file.size <= 0 || file.size > LIMIT) {
      setError('Choose a PDF, PNG or JPEG up to 20 MiB.');
      return;
    }
    const fingerprint = JSON.stringify([
      file.name, file.size, file.lastModified, file.type,
    ]);
    if (uploadOrigin.current.fingerprint !== fingerprint) {
      if (typeof globalThis.crypto?.randomUUID !== 'function') {
        setError('Cannot establish a durable upload command key in this browser.');
        return;
      }
      uploadOrigin.current = {
        fingerprint, key: globalThis.crypto.randomUUID(),
      };
    }
    const active = scope;
    setBusy(true);
    setError('');
    try {
      const form = new FormData();
      form.append('file', file, file.name);
      const { data } = await api.post(root + '/attachments', form, {
        headers: {
          ...headers,
          'Content-Type': 'multipart/form-data',
          'Idempotency-Key': uploadOrigin.current.key,
        },
        timeout: 120000,
      });
      if (current.current !== active) return;
      if (
        data?.schema !== 'WILSY-PROJECT-ATTACHMENT-RESULT/V1'
        || data.tenant_id !== tenantId || data.principal_id !== principalId
        || data.project_id !== projectId || data.task_id !== taskId
        || !valid(data.attachment, tenantId, projectId, taskId)
        || data.attachment.uploader_principal_id !== principalId
      ) throw new Error('PROJECT_ATTACHMENT_RESULT_INVALID');
      const listed = await load(0);
      if (!listed || current.current !== active) return;
      // Reconcile independently from a fresh EOS read; never infer completion
      // from a successful storage/command acknowledgement.
      const { data: verification } = await api.get(
        root + '/attachments?limit=50&offset=0', { headers },
      );
      if (
        current.current !== active || verification?.schema !== 'WILSY-PROJECT-ATTACHMENT-LIST/V1'
        || verification.tenant_id !== tenantId || verification.principal_id !== principalId
        || verification.project_id !== projectId || verification.task_id !== taskId
        || !Array.isArray(verification.items)
        || !verification.items.some(item =>
          valid(item, tenantId, projectId, taskId)
          && item.attachment_id === data.attachment.attachment_id
          && item.content_sha3_512 === data.attachment.content_sha3_512
        )
      ) throw new Error('PROJECT_ATTACHMENT_READBACK_UNVERIFIED');
      setFile(null);
      uploadOrigin.current = { fingerprint: '', key: '' };
    } catch (failure) {
      if (current.current !== active) return;
      setError(failure?.response?.status === 409
        ? 'EOS detected a changed or replayed attachment. Reconcile before retrying.'
        : failure?.response?.status === 403
          ? 'EOS denied upload under your current project participation.'
          : 'Upload or independent EOS readback was not verified. Refresh before retrying.');
    } finally {
      if (current.current === active) setBusy(false);
    }
  };

  return <section aria-label="Task attachments"
    className="mt-4 rounded-xl border border-slate-200 bg-slate-50 p-3">
    <header className="flex items-center justify-between gap-2">
      <h4 className="flex items-center gap-2 font-semibold text-slate-900">
        <FileLock2 size={16}/> Task attachments
      </h4>
      <div className="flex gap-2">
        <button type="button" className="wp-button" disabled={busy}
          onClick={() => void load(offset)}><RefreshCw size={14}/> Refresh</button>
        <button type="button" className="wp-button" disabled={busy}
          onClick={onClose} aria-label="Close task attachments"><X size={14}/></button>
      </div>
    </header>
    <p className="mt-2 text-xs text-amber-900">
      Newly uploaded files remain quarantined until independent GuardDuty verification.
      Only files whose EOS clearance is recorded may be downloaded or linked as review evidence.
      Scan clearance does not prove document authenticity, legal validity or electronic signature.
    </p>
    {state === 'LOADING' && <p role="status" className="mt-3 text-sm text-slate-700">
      Verifying file manifests with EOS…
    </p>}
    {(state === 'DENIED' || state === 'UNAVAILABLE') &&
      <p role="alert" className="mt-3 text-sm text-rose-700">{error}</p>}
    {state === 'READY' && <>
      <ul className="mt-3 divide-y divide-slate-200 rounded-lg border border-slate-200 bg-white">
        {items.map(item => <li key={item.attachment_id} className="p-3 text-sm">
          <p className="break-words font-semibold text-slate-900">{item.filename}</p>
          <p className="mt-1 text-xs text-slate-600">
            {item.scan_clearance_status === 'SCAN_CLEAN_VERIFIED'
              ? 'GuardDuty scan verified clean · not an electronic signature'
              : 'Quarantined · malware scan clearance unavailable'}
            {' · '}{item.media_type} · {item.size_bytes.toLocaleString()} bytes
          </p>
          <div className="mt-2 flex flex-wrap gap-2">
            {participantMode && item.scan_clearance_status === 'QUARANTINED' &&
              <button type="button" disabled={busy} className="wp-button"
                onClick={() => void verifyScan(item)}>Check malware scan result</button>}
            {item.scan_clearance_status === 'SCAN_CLEAN_VERIFIED' &&
              <button type="button" disabled={busy} className="wp-button"
                onClick={() => void download(item)}>Download verified file</button>}
          </div>
          <p className="mt-1 break-all text-xs text-slate-600">
            SHA3-512 {item.content_sha3_512}
          </p>
        </li>)}
        {!items.length && <li className="p-4 text-sm text-slate-600">
          EOS verified no file manifests on this task page.
        </li>}
      </ul>
      {(offset > 0 || hasMore) && <nav aria-label="Task attachment pages" className="mt-3 flex gap-2">
        <button type="button" className="wp-button" disabled={busy || offset === 0}
          onClick={() => void load(Math.max(0, offset - 50))}>Previous</button>
        <button type="button" className="wp-button" disabled={busy || !hasMore}
          onClick={() => void load(offset + 50)}>Next</button>
      </nav>}
      {participantMode && <form className="mt-3 space-y-2 rounded-lg border border-slate-200 bg-white p-3"
        onSubmit={upload}>
        <label className="block text-sm font-semibold text-slate-800">Submit a file to quarantine
          <input type="file" aria-label="Project attachment file"
            accept=".pdf,.png,.jpg,.jpeg,application/pdf,image/png,image/jpeg"
            onChange={event => setFile(event.target.files?.[0] || null)}
            className="mt-2 block w-full text-sm text-slate-800"/>
        </label>
        <p className="text-xs text-slate-600">PDF, PNG or JPEG · maximum 20 MiB. No preview or public download.</p>
        <button type="submit" className="wp-button wp-button-primary"
          disabled={busy || !file || !SAFE.has(file.type) || file.size <= 0 || file.size > LIMIT}>
          <UploadCloud size={15}/> Submit to EOS quarantine
        </button>
      </form>}
      {error && <p role="alert" className="mt-3 text-sm text-rose-700">{error}</p>}
    </>}
  </section>;
}

// ARTIFACT: ProjectTaskAttachmentsPanel.jsx
// VERSION: v1.1.0-GOVERNED-SCAN-AND-CLEAN-DOWNLOAD
// AUTHORITY BOUNDARY: untrusted file never grants evidence approval or read
// TENANT POSTURE: exact EOS source tenant/principal/project/task response
// FAIL-CLOSED POSTURE: no scan, provider, download or approval invented
// FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
// END OF WILSY OS SOVEREIGN ARTIFACT
