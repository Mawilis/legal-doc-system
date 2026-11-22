/**
 * TITLE: WILSY OS Governed Project Task Quarantine Attachments Panel
 * VERSION: v1.8.0-QUARANTINE-UPLOAD-RECEIPT-DIAGNOSTICS
 * AUTHORITY: Python EOS task-scoped attachment and participant IAM services.
 * EPITOME: Source-backed task attachments, bounded PDF/image upload and visible
 *          quarantine state, without unsafe preview or download links.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/components/workspaces/ProjectTaskAttachmentsPanel.jsx
 * COLLABORATION / OWNERSHIP: Shared owner and Contributor task workspaces.
 *          API and Python EOS own authentication, bytes, storage and audit.
 * CERTIFICATION / UPDATE DATE: 2026-11-18
 * CHANGELOG: v1.8.0-QUARANTINE-UPLOAD-RECEIPT-DIAGNOSTICS separates rejected multipart commands, unconfigured S3/KMS transport and uncertain provider execution from accepted EOS upload receipts followed by readback mismatch. Maintains the same durable idempotency key and prevents silent replay or claimed completion without exact manifest confirmation.
 * CHANGELOG: v1.7.0-EXPLICIT-FOUNDER-CONTRIBUTOR-IAM-ACTIVATION makes the already-contributing canonical WILSY Founder able to explicitly request narrow contributor attachment IAM activation using an independently governed EOS command, then verifies the role admission response and rechecks original contributor GET. No automatic grant, client permission inference, replay of uploads, or fallback for paying tenants.
 * CHANGELOG: v1.6.0-NO-DUPLICATE-CONTRIBUTOR-ADMISSION recognizes source-verified existing project contributor participation and never routes that member into a duplicate People onboarding path when independent attachment IAM denies. Shows the specific contributor HTTP denial and requires independent IAM/capacity remediation rather than project re-enrollment or silent grants.
 * CHANGELOG: v1.5.0-PEOPLE-NAVIGATION-SOURCE-PREFLIGHT preflights the exact project participant list and eligible tenant-member options before leaving the attachment task for People. A denied/unavailable/synthetic source shows its bounded failure in situ and does not navigate; no IAM inference or upload grant.
 * CHANGELOG: v1.4.0-OWNER-READ-CONTRIBUTOR-WRITE-SEPARATION uses separately authorized owner metadata GET in the owner workspace rather than choosing participant-only GET from a contributor roster. Upload and scan remain on participant-only EOS routes and require independent participant source admission. Both reads validate exact tenant/principal/project/task; no IAM fallback or implicit Founder grant.
 * CHANGELOG: v1.3.0-ACTIONABLE-PROJECT-CONTRIBUTOR-ROUTE supplies a real keyboard-accessible route to project People contributor administration from owner-view attachments, and keeps upload unavailable without independent contributor IAM. Existing authorized upload remains in the contributor mode only.
 * CHANGELOG: v1.2.0-EXPLICIT-SOURCE-AND-UPLOAD-AUTHORITY distinguishes the exact attachment GET failure (HTTP status, bounded project source code or source-schema mismatch) from missing contributor upload authority. Makes the upload entry point and its permission prerequisites visible without attempting unauthorized provider writes or inventing completed scan evidence.
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
import { validParticipants, validOptions } from './ProjectParticipantsPanel.jsx';

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
  participantMode = false, ownerReadMode = false, onClose, onManageContributors = null,
}) {
  const [state, setState] = useState('LOADING');
  const [items, setItems] = useState([]);
  const [offset, setOffset] = useState(0);
  const [hasMore, setHasMore] = useState(false);
  const [file, setFile] = useState(null);
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);
  const [uploadReadState, setUploadReadState] = useState('UNVERIFIED');
  const [peoplePreflight, setPeoplePreflight] = useState('');
  const [checkingPeople, setCheckingPeople] = useState(false);
  const [activatingContributorIAM, setActivatingContributorIAM] = useState(false);
  const [contributorIAMMessage, setContributorIAMMessage] = useState('');
  const scope = [tenantId, principalId, projectId, taskId, participantMode, ownerReadMode].join('\0');
  const current = useRef(scope);
  current.current = scope;
  const generation = useRef(0);
  const uploadOrigin = useRef({ fingerprint: '', key: '' });
  const projectRoot = '/projects/' + encodeURIComponent(projectId);
  const ownerRoot = projectRoot + '/tasks/' + encodeURIComponent(taskId);
  const contributorRoot = projectRoot + '/my-project/tasks/' + encodeURIComponent(taskId);
  const readRoot = ownerReadMode ? ownerRoot
    : (participantMode ? contributorRoot : ownerRoot);
  const uploadReadVerified = participantMode && uploadReadState === 'VERIFIED';
  const headers = tenantHeaders || {};

  const load = useCallback(async (nextOffset = 0) => {
    const request = ++generation.current;
    const active = scope;
    setState('LOADING');
    setUploadReadState('UNVERIFIED');
    setError('');
    try {
      const { data } = await api.get(readRoot + '/attachments?limit=50&offset=' + nextOffset, { headers });
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
      ) {
        const invalid = new Error('PROJECT_ATTACHMENT_SOURCE_INVALID');
        invalid.invalidEnvelope = true;
        throw invalid;
      }
      setItems(data.items);
      setOffset(nextOffset);
      setHasMore(data.has_more);
      setState('READY');
      // A current contributor roster is not an HTTP project:participant:read
      // permission. Verify the participant-only list independently before
      // exposing contributor commands; owner metadata stays independently valid.
      if (participantMode && ownerReadMode) {
        try {
          const { data: contributorData } = await api.get(
            contributorRoot + '/attachments?limit=50&offset=' + nextOffset, { headers },
          );
          if (request !== generation.current || current.current !== active) return true;
          const authorized = contributorData?.schema === 'WILSY-PROJECT-ATTACHMENT-LIST/V1'
            && contributorData.tenant_id === tenantId
            && contributorData.principal_id === principalId
            && contributorData.project_id === projectId && contributorData.task_id === taskId
            && contributorData.limit === 50 && contributorData.offset === nextOffset
            && typeof contributorData.has_more === 'boolean'
            && Array.isArray(contributorData.items) && contributorData.items.length <= 50
            && (!contributorData.has_more || contributorData.items.length > 0)
            && contributorData.next_offset === (contributorData.has_more
              ? nextOffset + contributorData.items.length : null)
            && contributorData.items.every(item => valid(item, tenantId, projectId, taskId))
            && new Set(contributorData.items.map(item => item.attachment_id)).size === contributorData.items.length;
          setUploadReadState(authorized ? 'VERIFIED' : 'INVALID');
        } catch (failure) {
          if (request !== generation.current || current.current !== active) return true;
          setUploadReadState(failure?.response?.status === 403 ? 'DENIED' : 'UNAVAILABLE');
        }
      } else {
        setUploadReadState(participantMode ? 'VERIFIED' : 'UNVERIFIED');
      }
      return true;
    } catch (failure) {
      if (request !== generation.current || current.current !== active) return false;
      setItems([]);
      setHasMore(false);
      const status = failure?.response?.status;
      const rawDetail = failure?.response?.data?.detail;
      const safeDetail = typeof rawDetail === 'string' && /^PROJECT_[A-Z0-9_]{1,80}$/.test(rawDetail)
        ? ' · EOS ' + rawDetail : '';
      setState([401, 403, 404].includes(status) ? 'DENIED' : 'UNAVAILABLE');
      setError(failure?.invalidEnvelope
        ? 'The task attachment manifest response failed exact tenant, principal, task or schema verification.'
        : status === 401 ? 'Sign in to inspect task attachments (HTTP 401).'
          : status === 403 ? 'EOS denied task attachment access (HTTP 403)' + safeDetail + '.'
            : status === 404 ? 'The task attachment endpoint or record was not found (HTTP 404)' + safeDetail + '.'
              : status === 503 ? 'The task attachment source is unavailable (HTTP 503)' + safeDetail + '.'
                : Number.isInteger(status) ? 'Task attachment source failed with HTTP ' + status + safeDetail + '.'
                  : failure?.code === 'ECONNABORTED' ? 'Task attachment source timed out before verification.'
                    : 'EOS could not reach or verify the task attachment manifest. No upload or download is confirmed.');
      return false;
    }
  }, [scope, readRoot, contributorRoot, ownerReadMode, participantMode, tenantId, principalId, projectId, taskId, tenantHeaders]);

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
    if (!uploadReadVerified || busy || state !== 'READY'
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
      const { data } = await api.post(contributorRoot + '/attachments/'
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
        readRoot + '/attachments?limit=50&offset=0', { headers },
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
        readRoot + '/attachments/' + encodeURIComponent(item.attachment_id) + '/download',
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

  const activateContributorIAM = async () => {
    if (activatingContributorIAM || busy || state !== 'READY'
      || !participantMode || uploadReadVerified
      || tenantId !== 'WILSYTENANT-4CD2FZ4O') return;
    const active = scope;
    setActivatingContributorIAM(true);
    setContributorIAMMessage('');
    try {
      const { data } = await api.post(
        projectRoot + '/founder-contributor-iam-admission', null,
        { headers: tenantHeaders || {} },
      );
      if (current.current !== active) return;
      if (data?.schema !== 'WILSY-PROJECT-CONTRIBUTOR-IAM-ADMISSION/V1'
        || data.tenant_id !== tenantId || data.principal_id !== principalId
        || data.project_id !== projectId
        || data.authorization_role !== 'PROJECTS_PARTICIPANT_CONTRIBUTOR'
        || data.authorization_state !== 'ACTIVE'
        || data.authority?.source !== 'PYTHON_EOS_ROLE_ASSIGNMENT') {
        setContributorIAMMessage('EOS returned an invalid contributor IAM admission readback. No upload access has been confirmed.');
        return;
      }
      // A successful role readback is not proof that this session's selected
      // capacity was refreshed. The original contributor GET is the gate.
      const verified = await load(0);
      if (current.current !== active) return;
      if (verified) setContributorIAMMessage(
        'EOS verified the contributor role assignment. Recheck attachment access; if this session remains denied, sign out and authenticate with the authorized contributor capacity.',
      );
    } catch (cause) {
      if (current.current !== active) return;
      const status = cause?.response?.status;
      setContributorIAMMessage(status === 403
        ? 'EOS denied this explicit role admission (HTTP 403). The signed-in operating capacity lacks independent invitation authority. An authorized tenant IAM administrator must issue the contributor role; no access was granted.'
        : status === 409
          ? 'EOS could not verify a governed contributor invitation or admission (HTTP 409). No upload access is confirmed.'
          : status === 503
            ? 'EOS contributor IAM authority is unavailable (HTTP 503). No upload access is confirmed.'
            : 'EOS did not confirm contributor IAM admission. No upload access is confirmed.');
    } finally {
      if (current.current === active) setActivatingContributorIAM(false);
    }
  };

  const navigateToPeople = async () => {
    if (checkingPeople || busy || state !== 'READY' || typeof onManageContributors !== 'function') return;
    const active = scope;
    setCheckingPeople(true);
    setPeoplePreflight('');
    // Never direct the user into another unverified workspace. This is a
    // read-only preflight; it cannot grant participation or contributor IAM.
    const projectRoot = '/projects/' + encodeURIComponent(projectId);
    const sources = [
      { name: 'Project participants', path: projectRoot + '/participants?limit=50&offset=0',
        verify: data => validParticipants(data, { tenantId, principalId, projectId }, 0) },
      { name: 'Eligible tenant member directory', path: projectRoot + '/participant-options?limit=50&offset=0',
        verify: data => validOptions(data, { tenantId, principalId, projectId }, 0) },
    ];
    try {
      const replies = await Promise.allSettled(sources.map(source =>
        api.get(source.path, { headers: tenantHeaders || {}, disableSourceBackoff: true }),
      ));
      if (current.current !== active) return;
      const failures = sources.map((source, index) => {
        const response = replies[index];
        if (response.status === 'fulfilled') {
          try {
            source.verify(response.value?.data);
            return null;
          } catch {
            return source.name + ': response scope or schema not verified.';
          }
        }
        const cause = response.reason;
        const status = cause?.response?.status || cause?.status;
        const detail = cause?.response?.data?.detail;
        const code = typeof detail === 'string' && /^PROJECT_[A-Z0-9_]{1,80}$/.test(detail)
          ? ' · EOS ' + detail : '';
        return source.name + ': '
          + (status === 403 ? 'denied (HTTP 403)' : status === 401 ? 'authentication required (HTTP 401)'
            : status === 503 ? 'unavailable (HTTP 503)' : status === 404 ? 'not found (HTTP 404)'
              : Number.isInteger(status) ? 'HTTP ' + status
                : cause?.code === 'ECONNABORTED' ? 'timed out' : 'transport unavailable')
          + code + '.';
      }).filter(Boolean);
      if (failures.length) {
        setPeoplePreflight(failures.join(' ')
          + ' Project People was not opened because its source was not verified. Participation alone cannot issue contributor IAM.');
        return;
      }
      onManageContributors();
    } finally {
      if (current.current === active) setCheckingPeople(false);
    }
  };

  const formatUploadFailure = (failure, stage) => {
    const status = failure?.response?.status;
    const detail = failure?.response?.data?.detail;
    const code = typeof detail === 'string' && /^PROJECT_[A-Z0-9_]{1,80}$/.test(detail) ? detail : null;
    if (stage === 'READBACK') {
      return 'EOS accepted the attachment command, but its exact persisted file manifest could not be verified. The original upload key is retained. Refresh to reconcile before taking another action; do not submit this file as a new command.';
    }
    if (stage === 'RECEIPT') {
      return 'EOS returned an attachment response that failed exact tenant, task, uploader or content verification. No file is confirmed. The original command key is retained for reconciliation.';
    }
    if (status === 403) return 'EOS denied the attachment upload command (HTTP 403). Contributor read access does not prove contributor write authority or selected operating capacity.';
    if (status === 401) return 'Authentication is required for this attachment upload (HTTP 401). The file has not been confirmed as submitted.';
    if (status === 413) return 'EOS rejected the attachment size (HTTP 413). Select a PDF, PNG or JPEG no larger than 20 MiB.';
    if (status === 422) return 'EOS rejected the multipart file or content (HTTP 422)' + (code ? ' · ' + code : '') + '. No accepted upload is confirmed.';
    if (status === 409) return 'EOS found an attachment command replay or conflict (HTTP 409)' + (code ? ' · ' + code : '') + '. Do not generate a new upload key; reconcile the existing command.';
    if (status === 503 && code === 'PROJECT_ATTACHMENT_STORAGE_NOT_CONFIGURED') return 'EOS quarantine storage is not configured (HTTP 503 · PROJECT_ATTACHMENT_STORAGE_NOT_CONFIGURED). The backend requires a versioned private S3 bucket, approved region and KMS key before real file uploads can be accepted.';
    if (status === 503 && code === 'PROJECT_ATTACHMENT_VERSIONING_REQUIRED') return 'EOS rejected storage because S3 bucket versioning is not enabled (HTTP 503 · PROJECT_ATTACHMENT_VERSIONING_REQUIRED). No verified quarantine receipt was issued.';
    if (status === 503) return 'EOS could not verify the quarantined storage operation (HTTP 503)' + (code ? ' · ' + code : '') + '. Provider execution may be uncertain; the original upload command key is retained. Reconcile the manifest before another attempt.';
    if (Number.isInteger(status)) return 'EOS rejected or could not verify the attachment operation (HTTP ' + status + ')' + (code ? ' · ' + code : '') + '. The original command key is retained.';
    if (failure?.code === 'ECONNABORTED') return 'The upload timed out without a verified EOS receipt. Storage may have accepted bytes; keep the original command key and reconcile before retrying.';
    return 'The attachment upload transport or EOS receipt could not be verified. The original command key is retained; reconcile the task manifest before retrying.';
  };

  const upload = async event => {
    event.preventDefault();
    if (!uploadReadVerified || busy || state !== 'READY' || !file) return;
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
    let stage = 'UPLOAD';
    try {
      const form = new FormData();
      form.append('file', file, file.name);
      const { data } = await api.post(contributorRoot + '/attachments', form, {
        headers: {
          ...headers,
          'Content-Type': 'multipart/form-data',
          'Idempotency-Key': uploadOrigin.current.key,
        },
        timeout: 120000,
      });
      if (current.current !== active) return;
      stage = 'RECEIPT';
      if (
        data?.schema !== 'WILSY-PROJECT-ATTACHMENT-RESULT/V1'
        || data.tenant_id !== tenantId || data.principal_id !== principalId
        || data.project_id !== projectId || data.task_id !== taskId
        || !valid(data.attachment, tenantId, projectId, taskId)
        || data.attachment.uploader_principal_id !== principalId
      ) throw new Error('PROJECT_ATTACHMENT_RESULT_INVALID');
      stage = 'READBACK';
      const listed = await load(0);
      if (!listed || current.current !== active) {
        if (current.current === active) throw new Error('PROJECT_ATTACHMENT_READBACK_UNVERIFIED');
        return;
      }
      // Reconcile independently from a fresh EOS read; never infer completion
      // from a successful storage/command acknowledgement.
      const { data: verification } = await api.get(
        readRoot + '/attachments?limit=50&offset=0', { headers },
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
      setError(formatUploadFailure(failure, stage));
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
    <div aria-label="Attachment upload authority" className="mt-3 rounded-lg border border-slate-200 bg-white p-3">
      <p className="text-sm font-semibold text-slate-900">Add an attachment</p>
      <p className="mt-1 text-xs text-slate-700">
        {uploadReadVerified
          ? 'Contributor attachment read is verified. Select a PDF, PNG or JPEG below; EOS still independently authorizes the contributor upload command.'
          : state !== 'READY'
            ? 'File selection is unavailable until the authenticated attachment source is verified. Refresh after fixing the error below.'
            : participantMode && uploadReadState === 'DENIED'
              ? 'You are already a verified contributor on this project. EOS separately denied the contributor attachment endpoint (HTTP 403). Re-adding yourself in People will not fix the missing or inactive project:participant:read authorization. Upload also requires project:participant:contribute in an authorized contributor operating capacity. No file has been submitted.'
              : participantMode
                ? 'You are already a verified project contributor, but the separate authenticated contributor attachment source is not verified. Check the current operating capacity and project:participant:read authority; project participation alone cannot authorize uploads.'
                : 'Owner access can read attachment manifests but cannot upload. Current project contributor admission and project:participant:contribute are required.'}
      </p>
      {!participantMode && !uploadReadVerified && typeof onManageContributors === 'function' &&
        <button type="button" className="wp-button mt-3"
          disabled={checkingPeople || busy || state !== 'READY'}
          onClick={() => { void navigateToPeople(); }}>
          {checkingPeople ? 'Verifying project People…' : 'Check People access before contributor management'}
        </button>}
      {peoplePreflight && <p role="alert" className="mt-2 text-sm text-rose-800">{peoplePreflight}</p>}
      {!uploadReadVerified && participantMode && tenantId === 'WILSYTENANT-4CD2FZ4O'
        && <button type="button" className="wp-button mt-3"
          disabled={activatingContributorIAM || busy || state !== 'READY'}
          onClick={() => { void activateContributorIAM(); }}>
          {activatingContributorIAM ? 'Verifying contributor IAM…' : 'Activate my contributor attachment access'}
        </button>}
      {contributorIAMMessage && <p role="status" className="mt-2 text-sm text-slate-800">{contributorIAMMessage}</p>}
      {!uploadReadVerified && participantMode && <p role="status" className="mt-2 text-xs font-medium text-slate-800">
        Project participation: verified Contributor. Attachment contributor authority: {uploadReadState === 'DENIED' ? 'denied by EOS (HTTP 403)' : 'not verified'}.
        A tenant IAM administrator must verify the separate contributor role assignment and selected operating capacity. This screen cannot create that grant.
      </p>}
      {!uploadReadVerified && !participantMode && <p className="mt-2 text-xs text-slate-700">
        Project participation and upload IAM are separate. Even an authorized contributor assignment will not grant project:participant:read or project:participant:contribute.
      </p>}
    </div>
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
            {uploadReadVerified && item.scan_clearance_status === 'QUARANTINED' &&
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
      {uploadReadVerified && <form className="mt-3 space-y-2 rounded-lg border border-slate-200 bg-white p-3"
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
// VERSION: v1.8.0-QUARANTINE-UPLOAD-RECEIPT-DIAGNOSTICS
// AUTHORITY BOUNDARY: untrusted file never grants evidence approval or read
// TENANT POSTURE: exact EOS source tenant/principal/project/task response
// FAIL-CLOSED POSTURE: no scan, provider, download or approval invented
// FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
// END OF WILSY OS SOVEREIGN ARTIFACT
