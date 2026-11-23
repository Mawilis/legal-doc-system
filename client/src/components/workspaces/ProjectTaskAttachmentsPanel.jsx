/**
 * TITLE: WILSY OS Governed Project Task Quarantine Attachments Panel
 * VERSION: v1.11.2-AUTHORITY-UNAVAILABLE-DIAGNOSTICS
 * AUTHORITY: Python EOS task-scoped attachment and participant IAM services.
 * EPITOME: Source-backed task attachments, bounded PDF/image upload and visible
 *          quarantine state, without unsafe preview or download links.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/components/workspaces/ProjectTaskAttachmentsPanel.jsx
 * COLLABORATION / OWNERSHIP: Shared owner and Contributor task workspaces.
 *          API and Python EOS own authentication, bytes, storage and audit.
 * CERTIFICATION / UPDATE DATE: 2026-11-23
 * CHANGELOG: v1.11.2-AUTHORITY-UNAVAILABLE-DIAGNOSTICS
 *          keeps the contributor preflight visible but disabled when
 *          source read fails, instead of hiding all guidance; the
 *          server still independently requires exact task IAM.
 * CHANGELOG: v1.11.1-SINGLE-FOCUSED-EXIT lets the invoking
 *          task workspace own the single Back control, while standalone
 *          attachment consumers retain an explicit close action.
 * CHANGELOG: v1.11.0-ACCESSIBLE-AUTOUPLOAD-DROPZONE replaces
 *          the visible native file chooser and redundant selection step
 *          with keyboard-browse and scoped file drag/drop. User selection
 *          starts one existing EOS multipart command; authenticated source
 *          readback alone confirms attachment presence. Live transfer
 *          percentage never claims scan clearance, and uncertain commands
 *          retain their original idempotency identity.
 * CHANGELOG: v1.10.0-UPLOAD-FIRST-ATTACHMENT-WORKSPACE prioritizes
 *          the existing guarded file picker, visible chosen-file feedback,
 *          and EOS-verified prior attachment list. It condenses repeated
 *          authority warnings into a disclosure, keeps rejected-access
 *          remediation available, and preserves readback/idempotency rules.
 * CHANGELOG: v1.9.0-UPLOAD-READBACK-SELECTED-FILE-CURRENTNESS validates the accepted upload by one independent full exact-tenant/task paginated manifest GET without unmounting the selected file input. On uncertain readback, the original File and idempotency key remain available for explicit reconciliation; no silent duplicate upload.
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
  showClose = true,
}) {
  const [state, setState] = useState('LOADING');
  const [items, setItems] = useState([]);
  const [offset, setOffset] = useState(0);
  const [hasMore, setHasMore] = useState(false);
  const [file, setFile] = useState(null);
  const [dragActive, setDragActive] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(null);
  const [uploadPhase, setUploadPhase] = useState('IDLE');
  const fileInputRef = useRef(null);
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

  const upload = async selectedFile => {
    if (!uploadReadVerified || busy || state !== 'READY' || !selectedFile) return;
    setFile(selectedFile);
    if (!SAFE.has(selectedFile.type) || selectedFile.size <= 0 || selectedFile.size > LIMIT) {
      setError(selectedFile.size > LIMIT
        ? 'Each file must be 20 MiB or smaller.' : 'Only non-empty PDF, PNG and JPEG files are supported.');
      setUploadPhase('INVALID');
      return;
    }
    const fingerprint = JSON.stringify([
      selectedFile.name, selectedFile.size, selectedFile.lastModified, selectedFile.type,
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
    setUploadProgress(0);
    setUploadPhase('UPLOADING');
    let stage = 'UPLOAD';
    try {
      const form = new FormData();
      form.append('file', selectedFile, selectedFile.name);
      const { data } = await api.post(contributorRoot + '/attachments', form, {
        headers: {
          ...headers,
          // The browser/Axios must generate the multipart boundary from FormData.
          // Never force an incomplete Content-Type over the current API defaults.
          'Idempotency-Key': uploadOrigin.current.key,
        },
        timeout: 120000,
        onUploadProgress: progress => {
          if (current.current !== active || !progress.total || progress.total <= 0) return;
          setUploadProgress(Math.min(99, Math.floor(100 * progress.loaded / progress.total)));
        },
      });
      if (current.current !== active) return;
      setUploadPhase('VERIFYING');
      stage = 'RECEIPT';
      if (
        data?.schema !== 'WILSY-PROJECT-ATTACHMENT-RESULT/V1'
        || data.tenant_id !== tenantId || data.principal_id !== principalId
        || data.project_id !== projectId || data.task_id !== taskId
        || !valid(data.attachment, tenantId, projectId, taskId)
        || data.attachment.uploader_principal_id !== principalId
      ) throw new Error('PROJECT_ATTACHMENT_RESULT_INVALID');
      stage = 'READBACK';
      // One independently authenticated, exact-scope manifest readback.
      // Do not call load(): it flips READY->LOADING and unmounts the selected
      // file input before readback, losing the visible selection on failure.
      const { data: verification } = await api.get(
        readRoot + '/attachments?limit=50&offset=0', { headers },
      );
      if (current.current !== active) return;
      if (
        verification?.schema !== 'WILSY-PROJECT-ATTACHMENT-LIST/V1'
        || verification.tenant_id !== tenantId || verification.principal_id !== principalId
        || verification.project_id !== projectId || verification.task_id !== taskId
        || verification.limit !== 50 || verification.offset !== 0
        || !Array.isArray(verification.items) || verification.items.length > 50
        || typeof verification.has_more !== 'boolean'
        || (verification.has_more && verification.items.length === 0)
        || verification.next_offset !== (verification.has_more
          ? verification.items.length : null)
        || verification.items.some(item => !valid(item, tenantId, projectId, taskId))
        || new Set(verification.items.map(item => item.attachment_id)).size !== verification.items.length
        || !verification.items.some(item =>
          item.attachment_id === data.attachment.attachment_id
          && item.content_sha3_512 === data.attachment.content_sha3_512
          && item.uploader_principal_id === principalId
        )
      ) throw new Error('PROJECT_ATTACHMENT_READBACK_UNVERIFIED');
      setItems(verification.items);
      setOffset(0);
      setHasMore(verification.has_more);
      setFile(null);
      setUploadProgress(100);
      setUploadPhase('CONFIRMED');
      uploadOrigin.current = { fingerprint: '', key: '' };
    } catch (failure) {
      if (current.current !== active) return;
      setError(formatUploadFailure(failure, stage));
      setUploadPhase('UNVERIFIED');
    } finally {
      if (current.current === active) setBusy(false);
    }
  };

  return <section aria-label="Task attachments"
    className="mt-3 space-y-4 rounded-xl border border-slate-200 bg-white p-4 sm:p-5">
    <header className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-200 pb-3">
      <div className="min-w-0">
        <h4 className="flex items-center gap-2 text-base font-semibold text-slate-950">
          <FileLock2 size={18}/> Files &amp; evidence
        </h4>
        <p className="mt-1 text-xs text-slate-600">
          Files belong to the selected task. EOS verifies access and upload clearance independently.
        </p>
      </div>
      <div className="flex items-center gap-2">
        <button type="button" className="wp-button !min-h-9 !px-3 !text-xs" disabled={busy}
          onClick={() => void load(offset)}><RefreshCw size={14}/> Refresh files</button>
        {showClose && <button type="button" className="wp-button !min-h-9 !px-3 !text-xs" disabled={busy}
          onClick={onClose} aria-label="Close task attachments"><X size={14}/> Close</button>}
      </div>
    </header>
    {state === 'LOADING' && <p role="status" className="text-sm text-slate-700">
      Verifying task files with EOS…
    </p>}
    {(state === 'DENIED' || state === 'UNAVAILABLE') &&
      <p role="alert" className="rounded-md border border-rose-200 bg-rose-50 p-3 text-sm text-rose-900">{error}</p>}
    {state === 'READY' && uploadReadVerified && <section
      aria-label="Add a task file" className="rounded-lg border border-slate-200 bg-white">
      <div className="px-3 pt-3 sm:px-4">
        <h5 className="text-sm font-bold text-slate-950">Add evidence</h5>
        <p className="mt-1 text-xs text-slate-600">
          PDF, PNG or JPEG · maximum 20 MiB per file · private until verified
        </p>
      </div>
      <input ref={fileInputRef} type="file" tabIndex={-1}
        aria-label="Project attachment file" className="sr-only"
        disabled={busy}
        accept=".pdf,.png,.jpg,.jpeg,application/pdf,image/png,image/jpeg"
        onChange={event => {
          const chosen = event.currentTarget.files?.[0];
          event.currentTarget.value = '';
          if (chosen) void upload(chosen);
        }}/>
      <div className={'m-3 rounded-lg border-2 border-dashed transition-colors sm:m-4 '
        + (dragActive ? 'border-blue-500 bg-blue-50' : 'border-slate-300 bg-slate-50')}
        onDragEnter={event => {
          if (!event.dataTransfer?.types?.includes('Files')) return;
          event.preventDefault();
          setDragActive(true);
        }}
        onDragOver={event => {
          if (!event.dataTransfer?.types?.includes('Files')) return;
          event.preventDefault();
          event.dataTransfer.dropEffect = busy ? 'none' : 'copy';
          setDragActive(true);
        }}
        onDragLeave={event => {
          if (!event.currentTarget.contains(event.relatedTarget)) setDragActive(false);
        }}
        onDrop={event => {
          if (!event.dataTransfer?.files?.length) return;
          event.preventDefault();
          setDragActive(false);
          if (busy) return;
          if (event.dataTransfer.files.length !== 1) {
            setError('Select one file at a time. Each upload requires its own verified EOS receipt.');
            return;
          }
          void upload(event.dataTransfer.files[0]);
        }}>
        <div className="flex flex-col items-center gap-2 px-4 py-5 text-center">
          <UploadCloud size={22} className="text-slate-600" aria-hidden="true"/>
          <p className="text-sm font-semibold text-slate-900">
            {dragActive ? 'Release to attach this file' : 'Drop a file here'}
          </p>
          <button type="button" disabled={busy}
            className="inline-flex min-h-10 items-center rounded-md bg-slate-900 px-4 text-sm font-semibold text-white hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-700"
            onClick={() => fileInputRef.current?.click()}>
            Browse files
          </button>
          <p className="text-xs text-slate-600">Selecting or dropping a file starts the upload.</p>
        </div>
      </div>
      {uploadPhase === 'UPLOADING' && <div className="px-4 pb-4" role="status">
        <div className="flex items-center justify-between gap-2 text-xs text-slate-700">
          <span className="min-w-0 truncate">{file?.name || 'Uploading file…'}</span>
          <span>{uploadProgress === null ? 'Uploading…' : uploadProgress + '%'}</span>
        </div>
        <div role="progressbar" aria-label="File transfer progress"
          aria-valuemin={0} aria-valuemax={100}
          aria-valuenow={uploadProgress === null ? undefined : uploadProgress}
          className="mt-2 h-1.5 overflow-hidden rounded-full bg-slate-200">
          <div className="h-full bg-blue-700 transition-[width]"
            style={{ width: (uploadProgress || 0) + '%' }}/>
        </div>
      </div>}
      {uploadPhase === 'VERIFYING' && <p role="status" className="px-4 pb-4 text-sm text-slate-700">
        Transfer finished. Checking the exact task file record with EOS…
      </p>}
      {uploadPhase === 'CONFIRMED' && <p role="status" className="px-4 pb-4 text-sm text-emerald-800">
        File recorded in the task list. Security clearance is still checked separately.
      </p>}
      {uploadPhase === 'UNVERIFIED' && file && <p role="status"
        className="px-4 pb-4 text-xs text-rose-800">
        Upload is not verified. Refresh the file list to reconcile before attempting the same command again.
      </p>}
    </section>}
    {state !== 'LOADING' && !uploadReadVerified && <section aria-label="Attachment upload authority"
      className="rounded-lg border border-slate-200 bg-slate-50 p-3">
      <h5 className="text-sm font-semibold text-slate-900">Upload not available</h5>
      <p className="mt-1 text-sm text-slate-700">
        {participantMode
          ? 'Contributor attachment access has not been independently verified for this session.'
          : 'The current capacity can inspect verified files but cannot upload as a contributor.'}
      </p>
      {!participantMode && typeof onManageContributors === 'function' &&
        <button type="button" className="wp-button mt-3 !min-h-9 !text-xs"
          disabled={checkingPeople || busy || state !== 'READY'}
          onClick={() => { void navigateToPeople(); }}>
          {checkingPeople ? 'Verifying People access…' : 'Check contributor access'}
        </button>}
      {peoplePreflight && <p role="alert" className="mt-2 text-xs text-rose-800">{peoplePreflight}</p>}
      {participantMode && tenantId === 'WILSYTENANT-4CD2FZ4O' &&
        <button type="button" className="wp-button mt-3 !min-h-9 !text-xs"
          disabled={activatingContributorIAM || busy || state !== 'READY'}
          onClick={() => { void activateContributorIAM(); }}>
          {activatingContributorIAM ? 'Verifying contributor IAM…' : 'Activate my contributor attachment access'}
        </button>}
      {contributorIAMMessage && <p role="status" className="mt-2 text-xs text-slate-800">{contributorIAMMessage}</p>}
      <details className="mt-3 text-xs text-slate-700">
        <summary className="cursor-pointer font-semibold text-slate-800">
          Why is upload unavailable?
        </summary>
        <p className="mt-2 leading-relaxed">
          Project participation and attachment IAM are separate. The contributor endpoint requires
          project:participant:read and project:participant:contribute in an authorized operating
          capacity. Current verification: {uploadReadState === 'DENIED' ? 'denied (HTTP 403)' : uploadReadState.toLowerCase()}.
          A tenant IAM administrator must verify the separate role assignment and capacity;
          this screen never grants access automatically.
        </p>
      </details>
    </section>}
    {state === 'READY' && <section aria-label="Previously attached files">
      <div className="flex flex-wrap items-baseline justify-between gap-2">
        <h5 className="text-sm font-bold text-slate-950">Attached files</h5>
        <span className="text-xs font-medium text-slate-600">
          {items.length} verified on this page{hasMore ? ' · more available' : ''}
        </span>
      </div>
      {items.length === 0
        ? <div className="mt-2 rounded-lg border border-dashed border-slate-300 bg-slate-50 px-4 py-6 text-center">
          <FileLock2 size={21} className="mx-auto text-slate-400"/>
          <p className="mt-2 text-sm font-semibold text-slate-800">No files attached yet</p>
          <p className="mt-1 text-xs text-slate-600">EOS verified no attachment manifests on this page.</p>
        </div>
        : <ul className="mt-2 divide-y divide-slate-200 overflow-hidden rounded-lg border border-slate-200 bg-white">
          {items.map(item => <li key={item.attachment_id}
            className="flex flex-wrap items-center justify-between gap-3 px-3 py-3 text-sm">
            <div className="min-w-0 flex-1">
              <p className="break-words font-semibold text-slate-900">{item.filename}</p>
              <p className="mt-1 text-xs text-slate-600">
                {item.scan_clearance_status === 'SCAN_CLEAN_VERIFIED'
                  ? 'Scan verified clean' : 'Quarantined · clearance pending'}
                {' · '}{item.media_type} · {(item.size_bytes / 1048576).toFixed(2)} MiB
              </p>
              <details className="mt-1 text-xs text-slate-600">
                <summary className="cursor-pointer font-medium text-slate-700">File integrity</summary>
                <p className="mt-1 break-all">SHA3-512 {item.content_sha3_512}</p>
              </details>
            </div>
            <div className="flex shrink-0 flex-wrap gap-2">
              {uploadReadVerified && item.scan_clearance_status === 'QUARANTINED' &&
                <button type="button" disabled={busy} className="wp-button !min-h-9 !text-xs"
                  onClick={() => void verifyScan(item)}>Check scan</button>}
              {item.scan_clearance_status === 'SCAN_CLEAN_VERIFIED' &&
                <button type="button" disabled={busy} className="wp-button !min-h-9 !text-xs"
                  onClick={() => void download(item)}>Download</button>}
            </div>
          </li>)}
        </ul>}
      {(offset > 0 || hasMore) && <nav aria-label="Task attachment pages"
        className="mt-3 flex items-center gap-2">
        <button type="button" className="wp-button !min-h-9 !text-xs"
          disabled={busy || offset === 0}
          onClick={() => void load(Math.max(0, offset - 50))}>Previous</button>
        <button type="button" className="wp-button !min-h-9 !text-xs"
          disabled={busy || !hasMore}
          onClick={() => void load(offset + 50)}>Next</button>
      </nav>}
    </section>}
    {state === 'READY' && error && <p role="alert"
      className="rounded-lg border border-rose-200 bg-rose-50 p-3 text-sm text-rose-900">{error}</p>}
    <details className="border-t border-slate-200 pt-3 text-xs text-slate-700">
      <summary className="cursor-pointer font-semibold text-slate-700">
        File security &amp; evidence rules
      </summary>
      <p className="mt-2 leading-relaxed">
        Uploaded files remain private and quarantined until independent GuardDuty verification.
        Only EOS-cleared files may be downloaded or linked as review evidence.
        Malware clearance does not establish document authenticity, legal validity or electronic signature.
      </p>
    </details>
  </section>;
}

// ARTIFACT: ProjectTaskAttachmentsPanel.jsx
// VERSION: v1.11.2-AUTHORITY-UNAVAILABLE-DIAGNOSTICS
// AUTHORITY BOUNDARY: untrusted file never grants evidence approval or read
// TENANT POSTURE: exact EOS source tenant/principal/project/task response
// FAIL-CLOSED POSTURE: no scan, provider, download or approval invented
// FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
// END OF WILSY OS SOVEREIGN ARTIFACT
